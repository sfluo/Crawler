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
import cookielib

from bs4 import BeautifulSoup

host = 'http://www.amazon.com'
MaxNumReviews = 15 

FakeCookie='skin=noskin; x-wl-uid=1uHgA6QYtOf9VAskEst2YwASvctHz7iD/DW4sDnNew/GMyywt9FUDbwsRnzE39zseg1uFAnaoIOI=; session-token=ULgTXs9bV43xIhlut2kEZI/Le5ZL2aINFopjKFZtgrdqGxxcX/1GSZkYmvCc0+uktkYcJD657Tk9Dsi11JxPnPodmIOYJjBuc4tAAts0ZpR6lbzomtDBPlLh5LnmGAschVmi/T0BOD1Nr2+6qf/WyvMupgeEHH+ya5b4z+aYSY+5jD3LapfzmrqE3jF3ogvn1E+bbPmdR5rrwJkRej25mYbSkOrYqBNHyZNf9TCOrnCNEgOOU/g/JIjb10OaOkAB; __gads=ID=25a2624337c614a3:T=1428607844:S=ALNI_MZfckri_ZZ1-ydzF7K7bsrJYRUofA; __ar_v4=7CUFP6UIQZARTK57SDZKRU%3A20150409%3A3%7CVKZDA7NCVJAINNGOEQVAY3%3A20150409%3A3%7CIQS3HPYPHFHRHEYBEZAXCQ%3A20150409%3A3; ubid-main=188-5471422-6981114; session-id-time=2082787201l; session-id=184-9289097-6318545; csm-hit=1QC1CAANPA2T95A9NVZ4+s-1QC1CAANPA2T95A9NVZ4|1429326231448'

UserAgent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'

def getPage(url):

	tries = 0

	while tries < 3:

		try:
			req = urllib2.Request(url)  # pull the page

			req.add_header('Cookie', FakeCookie) 
			req.add_header('User-Agent',UserAgent)
			response = urllib2.urlopen(req)
			page = response.read()

			return page

		except:
			tries += 1
			continue;

	return None;
	

def extractReviewer(authorUrl, Author):
	"""
		Extract information from reviewer profile
		Author: ditionary of reviewer info
	"""

	print(authorUrl)
	
	page = getPage(authorUrl)
	if page is None:
		return

	soup = BeautifulSoup(page) # put into soup
	
	# find the profile
	profile = soup.find('div', class_='profile-info')
	if profile is None:
		return
	
	try:
		name = profile.find('span', class_='profile-display-name break-word')
		Author['Name'] = name.string.strip()
	except:
		return # must have a name 

	try:
		nameblock = profile.find('div', class_='a-row a-spacing-micro')
		location = nameblock.find('span', class_='a-size-small a-color-secondary')
		Author['Location'] = location.string.strip()
	except:
		Author['Location'] = '' 

	for child in profile.children:
		try: 
			row = child.find('div', class_='a-row')
			ranking = row.find('span', class_='a-size-large a-text-bold')
			Author['Ranking'] = ranking.string.strip()
			break # once we have, break
		except:
			pass

		# if the ranking is not highlighted, then let's try a combined ranking string
		try:
			ranking = child.span #row.find('span', class_='a-size-small a-color-secondary')
			if re.match(r'Reviewer ranking: #\d+', ranking.string.strip()) is not None :
				Author['Ranking'] = ranking.string.strip() # once we have, break
				break
		except:
			Author['Ranking'] = ''
			
	try:
		helpful = profile.find('div', class_='a-row customer-helpfulness')
		rate = helpful.find('span', class_='a-size-large a-text-bold')
		Author['Helpfulness'] = rate.string
	except:
		Author['Helpfulness'] = ''

def extractReviews(revUrl, maxNum, reviews):
	"""
		revUrl: the URL of all reviews
		maxNum: the maximum number of reviews we want
		reviews: the directionary of reviews (return)
	"""
	
	numOfReviews = 0

	reviews['ReviewUrl'] = revUrl
	reviews['AverageStarRating'] = ''

	reviewList = []
	while revUrl is not None:

		print(revUrl)

		page = getPage(revUrl)
		if page is None:
			break

		soup = BeautifulSoup(page) # put into soup
		
		if reviews['AverageStarRating'] is not '':
			summary = soup.find('div', class_='a-row averageStarRatingNumerical')
			if summary is not None:
				stars = summary.span.string
				reviews['AverageStarRating'] = stars
			else:
				reviews['AverageStarRating'] = ''

		reviewsoup = soup.find(id='cm_cr-review_list')
		#for review in reviewsoup.find_all('div', class_='a-section review'):
		if reviewsoup is None:
			break

		for review in reviewsoup.children:

			# A review should have a ID
			if review.get('id') is None:
				continue;	

			a_review = {}
			valid = False

			# Helpfulness vote
			try:
				vote = review.find('span', class_='a-size-small a-color-secondary review-votes')
				hwords = vote.string.split(' ')	
				hrate = float(hwords[0]) / float(hwords[2])
				a_review['helpfulnesss'] = hrate
			except:
				a_review['Helpfulnesss'] = ''

			# Rating
			try:
				stars = review.find('span', class_='a-icon-alt')
				a_review['StarRating'] = stars.string
			except:
				a_review['StarRating'] = ''

			# Date
			date = review.find('span', class_='a-size-base a-color-secondary review-date')
			if date is not None:
				a_review['Date'] = date.string
			else:
				a_review['Date'] = ''

			# review text
			try:
				reviewdata = review.find('div', class_='a-row review-data')
				text = reviewdata.find('span', class_='a-size-base review-text')
				a_review['Text'] = text.string
				valid = True
			except:
				a_review['Text'] = ''

			profile = {}
			reviewer = review.find('a', class_='a-size-base a-link-normal author')
			if reviewer is not None:
				authorUrl = host + reviewer.get('href')
				profile = {'ProfileUrl' : authorUrl}
				extractReviewer(authorUrl, profile)
			else:
				profile = {'ProfileUrl' : ''}
			a_review['Author'] = profile

			if valid is True:
				reviewList.append(a_review)			

			numOfReviews += 1

		# Okay, we had enough, time to leave
		if numOfReviews > maxNum:
			break

		# otherwise, continue to explore
		try:
			pagebar = soup.find(id='cm_cr-pagination_bar')
			last = pagebar.find('li', class_="a-last")
			nextpage = last.a.get('href')
			revUrl = host + nextpage
		except:	
			revUrl = None # no more pages

	reviews['ReviewList'] = reviewList 
	#print(reviewList)

def fetchItem(itemurl, record):
	"""
		Given a product url, extract all information we need for our analysis
		We are assuming that Amazon use a template for all their products
		because the extraction heavily depends on the tokens (fix strings)

		Be careful!!! This may vary from products. 
	"""
	print(itemurl)

	page = getPage(itemurl)
	if page is None:
		return

	soup = BeautifulSoup(page) # put into soup

	# Here, we extract all information we need

	# 0. Time Stamp 
	ts = str(datetime.datetime.now())
	record['Timestamp'] = ts;

	# 1. Sales Rank
	# 2. Product Category
	salesrank = soup.find(id='SalesRank')
	if salesrank is not None:
		rank = salesrank.contents[2].strip().split(' ', 1)[0]
		category = salesrank.contents[2].strip().split(' ', 1)[1]
		record['Salesrank'] = rank
		record['Category'] = category
	else:
		record['Salesrank'] = ''
		record['Category'] = '' 

	# 3. Release time
	# 5. Price 
	# Note!!! e.g. Kindle eBook (free) does not have a price
	# Different category of products may have different page layout, different tags
	# FIXME: So far, the following is only for Books (confirmed)
	try:
		buyNewSection = soup.find(id='buyNewSection')
		offerPrice = buyNewSection.find('span', class_='a-size-medium a-color-price offer-price a-text-normal')
		record['OfferPrice'] = offerPrice.contents[0].strip()
	except:
		record['OfferPrice'] = ''

	try:
		buyBoxInner = soup.find(id='buyBoxInner')
		listPrice = buyBoxInner.find('span', class_= 'a-color-secondary a-text-strike')
		record['ListPrice'] = listPrice.contents[0].strip()
	except:
		record['ListPrice'] = ''

	# 6. Product Name
	try:
		name = soup.find(id='productTitle') # book
		if name == None:
			name = soup.find(id='btAsinTitle') # kindle ebook, Video Game
		record['Name'] = name.string.strip(),
	except:
		record['Name'] = ''

	# 4. Star Ratings
	# 7. Reviews (Recent 100): review Text, rating and timestamp, Reviewer
	# 8. Reviewer Info: Name, Rating, rating, location
	reviews = { 'MaxNumReviews' : MaxNumReviews }

	try:
		review = soup.find(id='customer-reviews_feature_div')
		allrev = review.find('a', id='seeAllReviewsUrl')
		revurl = allrev.get('href')
		if revurl is not None:
			# may replace 'sortBy=bySubmissionDateDescending' with 'sortBy=helpful'
			extractReviews(str(revurl), MaxNumReviews, reviews)
			record['Reviews'] = reviews
	except:
		revurl =  itemurl.replace('/dp/', '/product-reviews/') + \
			'/ref=cm_cr_dp_see_all_btm?ie=UTF8&showViewpoints=1&sortBy=helpful'
		extractReviews(str(revurl), MaxNumReviews, reviews)
		record['Reviews'] = reviews

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

		collected = 0 # tracking how many we collected already

		while collected < required_items and pageurl != '':

			page = getPage(pageurl)
			if page is None: 
				break;
			
			soup = BeautifulSoup(page) # put into soup

			# iterate items in this listing page
			for itemInPage in soup.find_all('a', class_=itemlocator_class):
				itemurl = itemInPage.attrs['href']
				# print(itemurl)
				
				if itemurl is None:
					continue;

				record = { 'itemurl' : itemurl}
				valid = fetchItem(itemurl, record) # pull the item
				if valid:
					collected += 1

			# not enough, we are greedy. Go to next listing page
			nextPage = soup.find('a', class_=nextlocator_class)
			if nextPage is not None:
				pageurl = host + nextPage.attrs['href']
			else:
				pageurl = None 

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
	
def testReviewer():
	Author = {}
	extractReviewer('http://www.amazon.com/gp/pdp/profile/ALC6LWQXBHIPG?ie=UTF8', Author)
	#extractReviewer('http://www.amazon.com/gp/pdp/profile/A1UXJUYUJ8RA87/ref=cm_cr_pr_pdp?ie=UTF8', Author)
	print(Author)

def testItem():
	record = {}
	fetchItem('http://www.amazon.com/FIFA-15-PlayStation-4/dp/B00KPY1GJA/ref=sr_1_1?s=videogames&ie=UTF8&qid=1429065279&sr=1-1&keywords=FIFA', record)
	print(record)

def test():
	#testReviewer()
	testItem()
	#fetchItem('http://www.amazon.com/FIFA-15-PlayStation-4/dp/B00KPY1GJA/ref=sr_1_1?s=videogames&ie=UTF8&qid=1429065279&sr=1-1&keywords=FIFA', record)
	#fetchItem('http://www.amazon.com/Path-Way-Knowledg-Containing-Principles-Geometrie-ebook/dp/B004TPZGEC', record) # kindle
#	fetchItem('http://www.amazon.com/Illustrated-Guide-Home-Chemistry-Experiments/dp/0596514921', record)
	#fetchItem('http://www.amazon.com/Illustrated-Guide-Home-Chemistry-Experiments/dp/0596514921')
	#fetchItem('http://www.amazon.com/Cartoon-Guide-Chemistry/dp/0060936770')
	#fetchItem('http://www.amazon.com/Path-Way-Knowledg-Containing-Principles-Geometrie-ebook/dp/B004TPZGEC') # kindle

if __name__ == "__main__":

	#main()
	test()
	
