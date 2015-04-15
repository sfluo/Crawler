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
import re

from bs4 import BeautifulSoup

host = 'http://www.amazon.com'

def extractReviews(rvUrl):
	print(rvUrl)	

def fetchItem(itemurl):
	"""
		Given a product url, extract all information we need for our analysis
		We are assuming that Amazon use a template for all their products
		because the extraction heavily depends on the tokens (fix strings)

		Be careful!!! This may vary from products. 
	"""
	req = urllib2.Request(itemurl)  # pull the page
	response = urllib2.urlopen(req);
	page = response.read()

	soup = BeautifulSoup(page) # put into soup

	# Here, we extract all information we need

	# 0. Time Stamp 
	ts = str(datetime.datetime.now())
	print ts,

	# 1. Sales Rank
	# 2. Product Category
	salesrank = soup.find(id='SalesRank')
	rank = salesrank.contents[2].strip().split(' ', 1)[0]
	category = salesrank.contents[2].strip().split(' ', 1)[1]
	print rank, category

	# 3. Release time
	# 5. Price 
	# Note!!! e.g. Kindle eBook (free) does not have a price
	# Different category of products may have different page layout, different tags
	# FIXME: So far, the following is only for Books (confirmed)
	try:
		buyNewSection = soup.find(id='buyNewSection')
		buyNewSoup = BeautifulSoup(str(buyNewSection))
		offerPrice = buyNewSoup.find('span', class_='a-size-medium a-color-price offer-price a-text-normal')
		print offerPrice.contents[0].strip(),
	except:
		print "No Offer Price Found"

	try:
		buyBoxInner = soup.find(id='buyBoxInner')
		buyBoxSoup = BeautifulSoup(str(buyBoxInner))
		listPrice = buyBoxSoup.find('span', class_= 'a-color-secondary a-text-strike')
		print listPrice.contents[0].strip(),
	except:
		print "No List Price Found"

	# 6. Product Name
	try:
		name = soup.find(id='productTitle') # book
		if name == None:
			name = soup.find(id='btAsinTitle') # kindle ebook, Video Game
		print name.contents[0].strip(),
	except:
		print "No Product Name Found"

	# 4. Star Ratings
	# 7. Reviews (Recent 100): review Text, rating and timestamp, Reviewer
	# 8. Reviewer Info: Name, Rating, rating, location
	try:
		review = soup.find(id='seeAllReviewsUrl')
		reviewPage = review.attrs['href']
		extractReviews(reviewPage)
	except:
		print "No Reviews."


	return True

def amazoncrawl(startUrl, keywords):
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
		pageurl = host + startUrl + '&field-keywords=' + string.replace(key.strip(), ' ', '+')
		required_items = keywords[key] 
		
		while required_items > 0 and pageurl != '':

			req = urllib2.Request(pageurl)  # pull the page
			response = urllib2.urlopen(req);
			page = response.read()
			
			soup = BeautifulSoup(page) # put into soup

			# iterate items in this listing page
			for itemInPage in soup.find_all('a', class_=itemlocator_class):
				itemurl = itemInPage.attrs['href']
				# print(itemurl)
				valid = fetchItem(itemurl) # pull the item
				if valid:
					required_items -= 1

			# not enough, we are greedy. Go to next listing page
			nextPage = soup.find('a', class_=nextlocator_class)
			pageurl = host + nextPage.attrs['href']
			#print(pageurl) 

def main():

	with open('test.json') as f:

		categories = json.load(f)
	
		for type in categories:

			print "Crawling [", type, "] ..."
			info = categories[type]

			if info['url'] == '':  # FIXME : let's skip it for now
				print "Fetching url" 
				continue;

			amazoncrawl(info['url'], info['keywords'])
	
def test():
	#fetchItem('http://www.amazon.com/FIFA-15-PlayStation-4/dp/B00KPY1GJA/ref=sr_1_1?s=videogames&ie=UTF8&qid=1429065279&sr=1-1&keywords=FIFA')
	#fetchItem('http://www.amazon.com/Illustrated-Guide-Home-Chemistry-Experiments/dp/0596514921')
	#fetchItem('http://www.amazon.com/Cartoon-Guide-Chemistry/dp/0060936770')
	#fetchItem('http://www.amazon.com/Path-Way-Knowledg-Containing-Principles-Geometrie-ebook/dp/B004TPZGEC') # kindle

if __name__ == "__main__":

	main()
	#test()
	
