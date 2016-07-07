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

def fetchItemSeller(itemurl):
	"""
		Given a product url, extract all information we need for our analysis
		We are assuming that Amazon use a template for all their products
		because the extraction heavily depends on the tokens (fix strings)

		Alert: the page might use different template for different categories of products
	"""
	print(itemurl)

	try:
		page = getPage(itemurl)
		soup = BeautifulSoup(page, 'lxml') # put into soup
		brandbyline = soup.find(id='brandByline_feature_div')
		adiv = brandbyline.find('div', class_="a-section a-spacing-none")
		asection = adiv.find('a', id='brand')
		return asection.text.strip()
	except:
		return None

def main_fetch(urlfile):
	"""
	"""
	if not urlfile.endswith('.txt'):
		print 'Error: require TXT file'
		return;
		
	try:
		filename = urlfile[:-4]
		#if not os.path.exists(path):
		#	os.makedirs(path)

		itemseller={}
		with open(urlfile, 'r') as urlfp:
		
			lines = urlfp.readlines()
			print lines
			for line in lines:
				line = line.strip()
				end = string.find(line, '/ref=')
				itemurl = line#[0:end]
				print "item:", itemurl
				seller = fetchItemSeller(itemurl) # pull the item
				if seller:
					h = hashlib.md5()
					h.update(itemurl)
					#print h.hexdigest(), seller
					itemseller[h.hexdigest()] = seller
		
		with open('./'+ filename + '.json', 'w') as f:
			json.dump(itemseller, f)

	except:
		print "Error: fail to read ", urlfile

def testItem():
	record = {}
	#fetchItem('http://www.amazon.com/Illustrated-Guide-Home-Chemistry-Experiments/dp/0596514921', record)
	#fetchItem('http://www.amazon.com/Path-Way-Knowledg-Containing-Principles-Geometrie-ebook/dp/B004TPZGEC', record) # kindle
	#fetchItem('http://www.amazon.com/FIFA-15-PlayStation-4/dp/B00KPY1GJA/ref=sr_1_1?s=videogames&ie=UTF8&qid=1429065279&sr=1-1&keywords=FIFA', record)
	#fetchItem('http://www.amazon.com/Mathematics-Physicists-Dover-Books-Physics/dp/0486691934/ref=sr_1_4?s=books&ie=UTF8&qid=1432351575&sr=1-4&keywords=mathematics+books+paperback', record)
	#fetchItem('http://www.amazon.com/Mechanics-Dover-Books-Physics-Hartog/dp/0486607542/ref=sr_1_12?s=books&ie=UTF8&qid=1432356061&sr=1-12&keywords=mathematics+books+paperback', record)
	#fetchItem('http://www.amazon.com/Theoretical-Physics-Dover-Books/dp/0486652270/ref=sr_1_8?s=books&ie=UTF8&qid=1432356061&sr=1-8&keywords=mathematics+books+paperback', record)
	#fetchItem('http://www.amazon.com/Geometry-Relativity-Fourth-Dimension-Mathematics/dp/0486234002/ref=sr_1_3?s=books&ie=UTF8&qid=1432356061&sr=1-3&keywords=mathematics+books+paperback', record)
	itemurl='http://www.amazon.com/Electrodynamics-Classical-Theory-Particles-Physics/dp/0486640388'
	fetchItem(itemurl, record)
	h = hashlib.md5()
	h.update(itemurl)
	print h.hexdigest()
	with open(h.hexdigest() + '.json', 'w') as f:
		json.dump(record, f)
	print(record)

if __name__ == "__main__":
	
	if len(sys.argv) < 2:
		print "Usage: python crawl.py [books.json]"
		exit(0)
	
	if not os.path.exists(sys.argv[1]): 
		print "Error: file [" + sys.argv[1] + "] does not exist"
		exit(0)

	main_fetch(sys.argv[1])
	#test()
	
