#!/usr/bin/python

import json
import getopt
import sys

class Product:
	def __init__(self, productName, mfr, family, model, announcedDate):
		self.productName = productName
		self.mfr = mfr
		self.family = family
		self.model = model
		self.announcedDate = announcedDate

	def __str__(self):
		#Serialize back to json
		tempDict = {'product_name': self.productName, 'manufacturer': self.mfr, 'model': self.model, 'announcedDate': self.announcedDate}
	
		#Family is optional, don't include it at all if it's not present
		if self.family:
			tempDict['family'] = self.family

		return json.dumps(tempDict)

class Listing:
	def __init__(self, title, mfr, currency, price):
		self.title = title
		self.mfr = mfr
		self.currency = currency
		self.price = price

	def __str__(self):
		#Serialize back to json
		return json.dumps({'title': self.title, 'manufacturer': self.mfr, 'currency': self.currency, 'price': self.price})

def loadProducts(fileName):
	result = []
	f = open(fileName, 'r')

	lineNumber = 0

	for line in f:
		lineNumber = lineNumber + 1

		jsonObj = json.loads(line)

		#Validate required fields
		if 'product_name' not in jsonObj:
			raise KeyError('Invalid product on line %d, missing product_name.' % lineNumber)
		if 'manufacturer' not in jsonObj:
			raise KeyError('Invalid product on line %d, missing manufacturer.' % lineNumber)
		if 'model' not in jsonObj:
			raise KeyError('Invalid product on line %d, missing model.' % lineNumber)
		if 'announced-date' not in jsonObj:
			raise KeyError('Invalid product on line %d, missing announced-date.' % lineNumber)

		#Fetch required fields
		productName = jsonObj['product_name']
		mfr = jsonObj['manufacturer']
		model = jsonObj['model']
		announcedDate = jsonObj['announced-date']

		#Fetch optional fields, default to None
		family = jsonObj.get('family', None) 

		result.append(Product(productName, mfr, model, announcedDate, family))

	return result

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hp:l:', ['help','products=', 'listings='])
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	productFile = 'products.txt'
	listingFile = 'listings.txt'

	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
			sys.exit()
		elif o in ('-p', '--products'):
			productFile = str(a)
		elif o in ('-l', '--listings'):
			listingFile = str(a)

	print productFile
	print listingFile

def usage():
	print """challenge.py, an implementation of Sortable's coding challenge
Copyright (C) 2012 Matt Lawrence

 -h, --help              displays this help
 -p, --products=FILE     use a specific product file, defaults to 'products.txt'
 -l, --listings=FILE     use a specific listing file, defaults to 'listings.txt'"""

if __name__ == '__main__':
	main()
