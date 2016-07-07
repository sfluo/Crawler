#!/usr/bin/env python
"""
	This script is created for crawling Amazon Product Data
	It searches for certain categories with specific keywords
"""

__author__ = "Shoufu Luo"
__copyright__ = "Copyright 2015, All rights reserved."

import urllib2
import datetime
import json
import string
import re, os, sys
import cookielib
import hashlib

from bs4 import BeautifulSoup

host = 'http://www.amazon.com'
MaxNumReviews = 1500

##### it seems in order to get details of product, cookie is required.
#FakeCookie='skin=noskin; x-wl-uid=1uHgA6QYtOf9VAskEst2YwASvctHz7iD/DW4sDnNew/GMyywt9FUDbwsRnzE39zseg1uFAnaoIOI=; session-token=ULgTXs9bV43xIhlut2kEZI/Le5ZL2aINFopjKFZtgrdqGxxcX/1GSZkYmvCc0+uktkYcJD657Tk9Dsi11JxPnPodmIOYJjBuc4tAAts0ZpR6lbzomtDBPlLh5LnmGAschVmi/T0BOD1Nr2+6qf/WyvMupgeEHH+ya5b4z+aYSY+5jD3LapfzmrqE3jF3ogvn1E+bbPmdR5rrwJkRej25mYbSkOrYqBNHyZNf9TCOrnCNEgOOU/g/JIjb10OaOkAB; __gads=ID=25a2624337c614a3:T=1428607844:S=ALNI_MZfckri_ZZ1-ydzF7K7bsrJYRUofA; __ar_v4=7CUFP6UIQZARTK57SDZKRU%3A20150409%3A3%7CVKZDA7NCVJAINNGOEQVAY3%3A20150409%3A3%7CIQS3HPYPHFHRHEYBEZAXCQ%3A20150409%3A3; ubid-main=188-5471422-6981114; session-id-time=2082787201l; session-id=184-9289097-6318545; csm-hit=1QC1CAANPA2T95A9NVZ4+s-1QC1CAANPA2T95A9NVZ4|1429326231448'

#FakeCookie='skin=noskin; x-wl-uid=1uHgA6QYtOf9VAskEst2YwASvctHz7iD/DW4sDnNew/GMyywt9FUDbwsRnzE39zseg1uFAnaoIOI=; session-token=ULgTXs9bV43xIhlut2kEZI/Le5ZL2aINFopjKFZtgrdqGxxcX/1GSZkYmvCc0+uktkYcJD657Tk9Dsi11JxPnPodmIOYJjBuc4tAAts0ZpR6lbzomtDBPlLh5LnmGAschVmi/T0BOD1Nr2+6qf/WyvMupgeEHH+ya5b4z+aYSY+5jD3LapfzmrqE3jF3ogvn1E+bbPmdR5rrwJkRej25mYbSkOrYqBNHyZNf9TCOrnCNEgOOU/g/JIjb10OaOkAB; __gads=ID=25a2624337c614a3:T=1428607844:S=ALNI_MZfckri_ZZ1-ydzF7K7bsrJYRUofA; __ar_v4=7CUFP6UIQZARTK57SDZKRU%3A20150409%3A3%7CVKZDA7NCVJAINNGOEQVAY3%3A20150409%3A3%7CIQS3HPYPHFHRHEYBEZAXCQ%3A20150409%3A3; skin=noskin; ubid-main=188-5471422-6981114; session-id-time=2082787201l; session-id=184-9289097-6318545; csm-hit=0K7BJKCF2ECQJKR3VDP3+s-0K7BJKCF2ECQJKR3VDP3|1432388134040'

# we want to mimic a web browser
#UserAgent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
#UserAgent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko)'

def getPage(url):
	'''
		Get a page with customized http header, cookie and user-agent	
	'''

	tries = 0

	# maximum three failures
	while tries < 3:

		try:
			req = urllib2.Request(url)  # pull the page

			#req.add_header('Cookie', FakeCookie) 
			#req.add_header('User-Agent',UserAgent)
			response = urllib2.urlopen(req)
			page = response.read()

			return page

		except:
			tries += 1
			continue;

	print "Error: Fail to get ", url

	return None;
	
def amazoncrawl(startUrl, keywords, path):
	"""
		This function crawls the item listing page returned by the search 
		it parses the page to extract the each item's URL and calls fetchItem()
		It stops when it has enough items collected or there is no more to collect 

		keywords: a dictionary of keywords and required instances, e.g. 'free physics books': 200
	"""
	
	# Magic strings for crawling on amazon.com
	itemlocator_class = 'a-link-normal s-access-detail-page a-text-normal'
	nextlocator_class = 'pagnNext'

	# iterate all keywords
	for key in keywords:

		# construct the listing page
		newkey = string.replace(key.strip(), ' ', '+')
		pageurl = host + startUrl + '&field-keywords=' + newkey
		required_items = keywords[key] 

		collected = 0 # tracking how many we collected already

		urlfilename = string.replace(path.strip(), ' ', '-') + '_' + newkey + '.txt'
		urlfp = open(urlfilename, 'w')
		while collected < required_items and pageurl != '':

			print(pageurl)
			page = getPage(pageurl)
			if page is None: 
				break;
			
			soup = BeautifulSoup(page) # put into soup

			# iterate items in this listing page
			for itemInPage in soup.find_all('a', class_=itemlocator_class):
				itemurl = itemInPage.attrs['href']
				print(itemurl)
				
				if itemurl is None:
					print "No Item"
					continue;

				###############################
				#####
				##### Save the URL
				urlfp.write(itemurl + "\n")
				continue

				###############################
				#####
				#####  Capture the data when we get the URL
				record = { 'itemurl' : itemurl, 'keyword' : key }
				valid = fetchItem(itemurl, record) # pull the item
				if valid:
					collected += 1
					h = hashlib.md5()
					h.update(itemurl)
					print h.hexdigest()
					with open(path + '/' + h.hexdigest() + '.json', 'w') as f:
						json.dump(record, f)

			# not enough, we are greedy. Go to next listing page
			nextPage = soup.find('a', class_=nextlocator_class)
			if nextPage is not None:
				pageurl = host + nextPage.attrs['href']
			else:
				pageurl = None 
		urlfp.close()

def main(config):

	with open(config) as f:
		try:
			categories = json.load(f)
		except:
			print "Error: invalid JSON file"
			return
			
		for type in categories:

			print "Crawling [", type, "] ..."
			info = categories[type]

			# we could use search to find the url of product list for 
			# each category. For now, let's skip it
			if info['url'] == '': 
				print "TODO: Fetching url" 
				continue;

			if not os.path.exists(type): 
				os.makedirs(type)
			#else:
			#	h = hashlib.md5()
			#	h.update(info['url'])
				# if already exits, then just skip
			#	if os.path.exists(type + '/' + h.hexdigest() + '.json'):
			#		continue;
			amazoncrawl(info['url'], info['keywords'], type)

if __name__ == "__main__":
	
	if len(sys.argv) < 2:
		print "Usage: python crawl.py [books.json]"
		exit(0)
	
	if not os.path.exists(sys.argv[1]): 
		print "Error: file [" + sys.argv[1] + "] does not exist"
		exit(0)

	main(sys.argv[1])
	
