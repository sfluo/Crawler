#!/usr/bin/env python

import httplib, urllib
import hmac, base64, hashlib
import datetime, time
from collections import OrderedDict

import xml.etree.ElementTree as ET
import re, os, sys
import json

AWSSecretKey="jD0xWPZjM3Osk8hKR+s8VqM+AZcTv1Ks5Xa/7lb1"
AWSAccessKeyId="AKIAJPEO5ZOU336KUTLA"
AWSMarketplaceId='ATVPDKIKX0DER'
MWSAuthToken='amzn.mws.88aae548-3bb8-abe2-0da0-18cf099bca9c'
AWSSellerId='AKMMW71WY8BJO'
AWSHost='mws.amazonservices.com'
UserAgent='Guess-1.0/Research'
AWSMaxProductPerRequest=5
AWSProductReqQuota=20

def getProductData(idList, idType='ASIN'):
	"""
		query product information via aws api
	"""
	PRODUCT_API_VERSION="2011-10-01"
	urlpath='/Products/' + PRODUCT_API_VERSION

	# if idList is empty, return

	methods=['POST', 'mws.amazonservices.com', urlpath]
	fields={ 
		'AWSAccessKeyId': AWSAccessKeyId, 
		'Action' : 'GetMatchingProductForId',
		#'IdList.Id.1' : 'B0002FGEK8',
		#'IdList.Id.2' : 'B0012V6ZVE',
		'IdType' : idType,
		'MWSAuthToken' : MWSAuthToken,
		'MarketplaceId' : AWSMarketplaceId,
		'SellerId' : AWSSellerId, 
		'SignatureMethod' : 'HmacSHA256',
		'SignatureVersion' : 2,
		'Timestamp' : datetime.datetime.utcnow().isoformat() + 'Z', #'2016-07-08T18:18:55.587Z', 
		'Version': PRODUCT_API_VERSION
		#'Signature' : '0RExample0%3D'
	}
	
	for i in range(1, min(10, len(idList)) + 1):
		fields['IdList.Id.' + str(i)] = idList[i-1]

	sorted_values = sorted(fields.items(), key=lambda val: val[0])
	stringToSign= '\n'.join(methods) + '\n' + urllib.urlencode(sorted_values)
	# print stringToSign
	signature = base64.b64encode(hmac.new(AWSSecretKey, msg=stringToSign, digestmod=hashlib.sha256).digest())
	fields['Signature'] = signature
	params = urllib.urlencode(fields)
	# print params

	headers = {"Content-type": "application/x-www-form-urlencoded", "Host": AWSHost, "User-Agent" : UserAgent}
	conn = httplib.HTTPSConnection(AWSHost)
	conn.request("POST", urlpath, params, headers)

	response = conn.getresponse()
	if response.status != 200:
		print response.status, response.reason
		return None
	
	return response.read()


def enumBrands(ids):
	"""
	"""
	prodbrand = {}

	data = getProductData(ids)
	# e.g. 
	# data = "<?xml version=\"1.0\"?><GetMatchingProductForIdResponse xmlns=\"http://mws.amazonservices.com/schema/Products/2011-10-01\"><GetMatchingProductForIdResult Id=\"B0002FGEK8\" IdType=\"ASIN\" status=\"Success\"><Products xmlns=\"http://mws.amazonservices.com/schema/Products/2011-10-01\" xmlns:ns2=\"http://mws.amazonservices.com/schema/Products/2011-10-01/default.xsd\"><Product><Identifiers><MarketplaceASIN><MarketplaceId>ATVPDKIKX0DER</MarketplaceId><ASIN>B0002FGEK8</ASIN></MarketplaceASIN></Identifiers><AttributeSets><ns2:ItemAttributes xml:lang=\"en-US\"><ns2:Binding>Office Product</ns2:Binding><ns2:Brand>SHARP</ns2:Brand><ns2:Color>WHITE</ns2:Color><ns2:Feature>+/- Switch Key - Yes</ns2:Feature><ns2:Feature>Amortization - No</ns2:Feature><ns2:Feature>Backspace Key - Yes</ns2:Feature><ns2:Feature>Base Number Calculations - Yes</ns2:Feature><ns2:Feature>Bond Calculations - No</ns2:Feature><ns2:ItemDimensions><ns2:Height Units=\"inches\">2.00</ns2:Height><ns2:Length Units=\"inches\">9.00</ns2:Length><ns2:Width Units=\"inches\">5.75</ns2:Width></ns2:ItemDimensions><ns2:IsAutographed>false</ns2:IsAutographed><ns2:IsMemorabilia>false</ns2:IsMemorabilia><ns2:Label>Sharp</ns2:Label><ns2:ListPrice><ns2:Amount>13.99</ns2:Amount><ns2:CurrencyCode>USD</ns2:CurrencyCode></ns2:ListPrice><ns2:Manufacturer>Sharp</ns2:Manufacturer><ns2:Model>EL501WBBL</ns2:Model><ns2:NumberOfItems>1</ns2:NumberOfItems><ns2:PackageDimensions><ns2:Height Units=\"inches\">1.10</ns2:Height><ns2:Length Units=\"inches\">7.60</ns2:Length><ns2:Width Units=\"inches\">4.10</ns2:Width><ns2:Weight Units=\"pounds\">0.25</ns2:Weight></ns2:PackageDimensions><ns2:PackageQuantity>1</ns2:PackageQuantity><ns2:PartNumber>EL501WBBL</ns2:PartNumber><ns2:ProductGroup>CE</ns2:ProductGroup><ns2:ProductTypeName>CALCULATOR</ns2:ProductTypeName><ns2:Publisher>Sharp</ns2:Publisher><ns2:SmallImage><ns2:URL>http://ecx.images-amazon.com/images/I/41myk%2BMbE5L._SL75_.jpg</ns2:URL><ns2:Height Units=\"pixels\">75</ns2:Height><ns2:Width Units=\"pixels\">75</ns2:Width></ns2:SmallImage><ns2:Studio>Sharp</ns2:Studio><ns2:Title>Sharp(R) EL-501VB Scientific Calculator</ns2:Title></ns2:ItemAttributes></AttributeSets><Relationships/><SalesRankings><SalesRank><ProductCategoryId>172525</ProductCategoryId><Rank>465</Rank></SalesRank><SalesRank><ProductCategoryId>1069242</ProductCategoryId><Rank>702921</Rank></SalesRank></SalesRankings></Product></Products></GetMatchingProductForIdResult><GetMatchingProductForIdResult Id=\"B0012V6ZVE\" IdType=\"ASIN\" status=\"Success\"><Products xmlns=\"http://mws.amazonservices.com/schema/Products/2011-10-01\" xmlns:ns2=\"http://mws.amazonservices.com/schema/Products/2011-10-01/default.xsd\"><Product><Identifiers><MarketplaceASIN><MarketplaceId>ATVPDKIKX0DER</MarketplaceId><ASIN>B0012V6ZVE</ASIN></MarketplaceASIN></Identifiers><AttributeSets><ns2:ItemAttributes xml:lang=\"en-US\"><ns2:Binding>Office Product</ns2:Binding><ns2:Brand>Tops</ns2:Brand><ns2:Color>Blue;White</ns2:Color><ns2:Department>Forms, Record Keeping &amp; Reference</ns2:Department><ns2:Feature>Includes space for costs in materials and labor</ns2:Feature><ns2:Feature>Back of third part also serves as a costing form to determine job profitability</ns2:Feature><ns2:Feature>3-part carbonless (white, canary, white tag paper sequence)</ns2:Feature><ns2:Feature>Blue ink</ns2:Feature><ns2:Feature>50 sets per pack</ns2:Feature><ns2:ItemDimensions><ns2:Height Units=\"inches\">0.90</ns2:Height><ns2:Length Units=\"inches\">9.20</ns2:Length><ns2:Width Units=\"inches\">5.50</ns2:Width><ns2:Weight Units=\"pounds\">0.20</ns2:Weight></ns2:ItemDimensions><ns2:Label>0</ns2:Label><ns2:ListPrice><ns2:Amount>11.99</ns2:Amount><ns2:CurrencyCode>USD</ns2:CurrencyCode></ns2:ListPrice><ns2:Manufacturer>0</ns2:Manufacturer><ns2:Model>3868</ns2:Model><ns2:NumberOfItems>1</ns2:NumberOfItems><ns2:PackageDimensions><ns2:Height Units=\"inches\">1.00</ns2:Height><ns2:Length Units=\"inches\">9.00</ns2:Length><ns2:Width Units=\"inches\">5.70</ns2:Width><ns2:Weight Units=\"pounds\">1.05</ns2:Weight></ns2:PackageDimensions><ns2:PackageQuantity>1</ns2:PackageQuantity><ns2:PartNumber>3868</ns2:PartNumber><ns2:ProductGroup>Office Product</ns2:ProductGroup><ns2:ProductTypeName>OFFICE_PRODUCTS</ns2:ProductTypeName><ns2:PublicationDate>2014-03-12</ns2:PublicationDate><ns2:Publisher>0</ns2:Publisher><ns2:Size>5 2/3 x 9 inches</ns2:Size><ns2:SmallImage><ns2:URL>http://ecx.images-amazon.com/images/I/51edkCdLtXL._SL75_.jpg</ns2:URL><ns2:Height Units=\"pixels\">75</ns2:Height><ns2:Width Units=\"pixels\">75</ns2:Width></ns2:SmallImage><ns2:Studio>0</ns2:Studio><ns2:Title>TOPS Job Work Order Forms, 3-Part, Carbonless, 5-1/2 x 9-1/8 Inches, 50 Sets per Pack (3868)</ns2:Title></ns2:ItemAttributes></AttributeSets><Relationships><VariationParent><Identifiers><MarketplaceASIN><MarketplaceId>ATVPDKIKX0DER</MarketplaceId><ASIN>B013CJCZEO</ASIN></MarketplaceASIN></Identifiers></VariationParent></Relationships><SalesRankings><SalesRank><ProductCategoryId>office_product_display_on_website</ProductCategoryId><Rank>31342</Rank></SalesRank><SalesRank><ProductCategoryId>1069686</ProductCategoryId><Rank>22</Rank></SalesRank></SalesRankings></Product></Products></GetMatchingProductForIdResult><ResponseMetadata><RequestId>545ae4d4-9e25-4d5e-972b-326387e969fe</RequestId></ResponseMetadata></GetMatchingProductForIdResponse>"
	
	if data is not None:
		root = ET.fromstring(data)
		m=re.match('\{.*\}', root.tag)
		ns=m.group(0) if m else '' # extract namespace

		for productres in root.findall(ns + 'GetMatchingProductForIdResult'):
			brand = []
			'''
				FIXME/TODO: is possible to have several products given one id
			'''
			attrSet = productres.find(ns+'Products/' + ns +'Product/'  + ns + 'AttributeSets')
			if attrSet is None:
				continue
			for child in attrSet:
				# print "child: ", child.tag
				m = re.match('\{.*\}', child.tag)
				attr_ns = m.group(0) if m else ''
				attr = child.find(attr_ns + 'Brand')	
				if attr is not None:
					brand.append(attr.text)

			prodbrand[productres.attrib['Id']]=brand

	return prodbrand

def main_fetch(urlfile):
	"""
		Input: txt file contains all product url
		Output: (url, ASIN, [Brand])
	"""
	if not urlfile.endswith('.txt'):
		print 'Error: require TXT file'
		return;

	brands = []
	tid = 0
	total = 0
	with open(urlfile, 'r') as urlfp:
		moredata = True
		while moredata:
			lines = filter(lambda x: x != '', [ urlfp.readline().strip() for _ in range(AWSMaxProductPerRequest) ])
			if len(lines) < AWSMaxProductPerRequest:
				moredata = False
			asins = [ x[x.rfind('/')+1:] for x in lines]
			print asins
			now = datetime.datetime.utcnow()
			results = enumBrands(asins)
			tid = tid + 1
			total = total + 1
			print('Sent No. {} requests'.format(total))

			if results is None:
				print 'No Data Received (either error or empty data).'
				continue

			for url, asin in zip(lines, asins):
				try:
					h = hashlib.md5()
					h.update(url)
					brands.append([h.hexdigest(), asin, results[asin]])
				except KeyError:
					pass
			if tid >= AWSProductReqQuota: 
				# 18,000 requests per hour
				# 3,600 seconds / 4 = 900 times
				# 900 x 20 requests = 18,000
				time.sleep(4) # wait for 4 second to reset the quota
				tid = 0

		#except Exception as inst:
		#	print(inst)

	if len(brands) > 0: 
		with open(urlfile + '.brand.json', 'w') as f:
			json.dump(brands, f)

if __name__ == '__main__':

	if len(sys.argv) < 2:
		print "Usage: python crawl.py [urlfile.txt]"
		exit(0)
	
	if not os.path.exists(sys.argv[1]): 
		print "Error: file [" + sys.argv[1] + "] does not exist"
		exit(0)

	main_fetch(sys.argv[1])


