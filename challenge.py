#!/usr/bin/python

import json
import getopt
import sys
import re

class Product(object):
    """Representation of a product."""
    def __init__(self, productName, mfr, family, model, announcedDate):
        self.productName = productName
        self.mfr = mfr
        self.family = family
        self.model = model
        self.announcedDate = announcedDate

        self.l_mfr = mfr.lower()
        self.l_model = model.lower()

        self.l_model_nospace = self.l_model.replace(' ', '')
        self.l_model_nodash = self.l_model.replace('-', '')
        self.l_model_dashtospace = self.l_model.replace('-', ' ')
        self.l_model_spacetodash = self.l_model.replace(' ', '-')

        regex = '(\W%s\W|\W%s\W|\W%s\W|\W%s\W|\W%s\W)' % (
            self.l_model, 
            self.l_model_nospace,
            self.l_model_nodash,
            self.l_model_dashtospace,
            self.l_model_spacetodash)

        self.l_regex = re.compile(regex, re.I)
        
        regex = '(\W%s|\W%s|\W%s|\W%s|\W%s)' % (
            self.l_model, 
            self.l_model_nospace,
            self.l_model_nodash,
            self.l_model_dashtospace,
            self.l_model_spacetodash)
        
        self.l_regex_allow_trail = re.compile(regex, re.I)

        regex = '(%s|%s|%s|%s|%s)' % (
            self.l_model, 
            self.l_model_nospace,
            self.l_model_nodash,
            self.l_model_dashtospace,
            self.l_model_spacetodash)

        self.l_regex_allow_lead_and_trail = re.compile(regex, re.I)

        if family:
            self.l_family = family.lower()

    def __str__(self):
        """Gets the json string representation of the product."""
        tempDict = {'product_name' : self.productName, 
                    'manufacturer' : self.mfr, 
                    'model'        : self.model, 
                    'announced-date': self.announcedDate}
    
        #Family is optional, don't include it at all if it's not present
        if self.family:
            tempDict['family'] = self.family

        return json.dumps(tempDict)

class Listing(object):
    """Representation of a product listing."""

    def __init__(self, title, mfr, currency, price):
        self.title = title
        self.mfr = mfr
        self.currency = currency
        self.price = price

        self.l_title = title.lower()
        self.l_mfr = mfr.lower()

        self.l_title_nodash = self.l_title.replace('-', '')

    def __str__(self):
        """Gets the json string representation of the listing."""
        return json.dumps({'title'       : self.title, 
                           'manufacturer': self.mfr, 
                           'currency'    : self.currency, 
                           'price'       : self.price})

    def toDict(self):
        """Gets this as a dict."""
        return {'title'        : self.title,
                'manufacturer' : self.mfr,
                'currency'     : self.currency,
                'price'        : self.price}

def loadProducts(file_name):
    """Loads a list of products from a file. 
    
    Args:
        file_name: the file to load data from, should be a single json encoded 
            product per line.

    Returns:
        A list of Product objects corresponding to the file lines.

    Raises:
        KeyError: One of the products is missing a required field.
    """

    result = []
    with open(file_name, 'r') as f:

        #Used for error messages
        lineNumber = 0

        for line in f:
            lineNumber += 1

            jsonObj = json.loads(line)

            # Validate required fields
            if 'product_name' not in jsonObj:
                raise KeyError('Invalid product on line %d, missing product_name.' % lineNumber)
            if 'manufacturer' not in jsonObj:
                raise KeyError('Invalid product on line %d, missing manufacturer.' % lineNumber)
            if 'model' not in jsonObj:
                raise KeyError('Invalid product on line %d, missing model.' % lineNumber)
            if 'announced-date' not in jsonObj:
                raise KeyError('Invalid product on line %d, missing announced-date.' % lineNumber)

            # Fetch required fields
            productName = jsonObj['product_name']
            mfr = jsonObj['manufacturer']
            model = jsonObj['model']
            announcedDate = jsonObj['announced-date']

            # Fetch optional fields, default to None
            family = jsonObj.get('family', None) 

            # Olympus PEN series seem to have the family in with the model
            if 'olympus' == mfr.lower() and model[:4] == 'PEN ':
                family = 'PEN'
                model = model[4:]

            # Panasonic Lumix DMC series seem to have the same issue
            if 'panasonic' == mfr.lower() and model[:4] == 'DMC-':
                family = 'DMC'
                model = model[4:]

            # Sony alpha series seem to prefix models with 'DSLR-'
            if 'sony' == mfr.lower() and model[:5] == 'DSLR-':
                model = model[5:]

            result.append(Product(productName, mfr, family, model, announcedDate))

    return result

def loadListings(fileName):
    """Loads a list of listings from a file. 
    
    Args:
        file_name: the file to load data from, should be a single json-encoded 
            listing per line.

    Returns:
        A list of Listing objects corresponding to the file lines.

    Raises:
        KeyError: One of the listings is missing a required field.
    """
    
    result = []
    with open(fileName, 'r') as f:

        #Used for error messages
        lineNumber = 0

        for line in f:
            lineNumber += 1

            jsonObj = json.loads(line)

            #Validate required fields
            if 'title' not in jsonObj:
                raise KeyError('Invalid listing on line %d, missing title.' % lineNumber)
            if 'manufacturer' not in jsonObj:
                raise KeyError('Invalid listing on line %d, missing manufacturer.' % lineNumber)
            if 'currency' not in jsonObj:
                raise KeyError('Invalid listing on line %d, missing currency.' % lineNumber)
            if 'price' not in jsonObj:
                raise KeyError('Invalid listing on line %d, missing price.' % lineNumber)

            yield Listing(jsonObj['title'], 
                                  jsonObj['manufacturer'], 
                                  jsonObj['currency'], 
                                  jsonObj['price'])

def findProducts(listing, products):
    matchedProducts = []

    title = ' %s ' % listing.l_title
    title_nodash = ' %s ' % listing.l_title_nodash
   
    # First pass, check for model, mfr, and family
    for product in products:
        mfr = product.l_mfr

        if mfr in title or mfr in listing.l_mfr:
            if product.family and product.l_family in title:
                if product.l_regex.search(title) \
                    or product.l_regex.search(listing.l_title_nodash):

                    matchedProducts.append(product)

    if len(matchedProducts) > 0:
        return matchedProducts

    # Next pass, check for the product's model in the title
    for product in products:
        mfr = product.l_mfr

        if mfr in title or mfr in listing.l_mfr:
            if product.l_regex.search(title) \
                or product.l_regex.search(listing.l_title_nodash):

                matchedProducts.append(product)

    if len(matchedProducts) > 0:
        return matchedProducts
    
    # Next pass, check for model, mfr, and family, allowing trailing alphanum
    # after the model.
    for product in products:
        mfr = product.l_mfr

        if mfr in title or mfr in listing.l_mfr:
            if product.family and product.l_family in title:
                if product.l_regex_allow_trail.search(title) \
                    or product.l_regex_allow_trail.search(listing.l_title_nodash):

                    matchedProducts.append(product)

    if len(matchedProducts) > 0:
        return matchedProducts

    # Next pass, check for the product's model in the title, allowing trailing
    # alphpanum after the model.
    for product in products:
        mfr = product.l_mfr

        if mfr in title or mfr in listing.l_mfr:
            if product.l_regex_allow_trail.search(title) \
                or product.l_regex_allow_trail.search(listing.l_title_nodash):

                matchedProducts.append(product)

    if len(matchedProducts) > 0:
        return matchedProducts
    
    # Next pass, check for model, mfr, and family, allowing anything around
    # the model.
    for product in products:
        mfr = product.l_mfr

        if mfr in title or mfr in listing.l_mfr:
            if product.family and product.l_family in title:
                if product.l_regex_allow_lead_and_trail.search(title) \
                    or product.l_regex_allow_lead_and_trail.search(listing.l_title_nodash):

                    matchedProducts.append(product)

    if len(matchedProducts) > 0:
        return matchedProducts

    # Next pass, check for the product's model in the title, allowing anything
    # around the model.
    for product in products:
        mfr = product.l_mfr

        if mfr in title or mfr in listing.l_mfr:
            if product.l_regex_allow_lead_and_trail.search(title) \
                or product.l_regex_allow_lead_and_trail.search(listing.l_title_nodash):

                matchedProducts.append(product)

    if len(matchedProducts) > 0:
        return matchedProducts
    
    # Next pass, if no models were matched then it may be a family-specific
    # accessory.
    if ' for ' in title:
        for product in products:

            # Skip over products with no family
            if not product.family:
                continue

            mfr = product.l_mfr
            family = product.l_family
            if family in title and mfr in title:
                matchedProducts.append(product)

    return matchedProducts

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

    products = loadProducts(productFile)
    listings = loadListings(listingFile)

    productResults = {}

    for listing in listings:
        matchedProducts = findProducts(listing, products)

        for product in matchedProducts:
            name = product.productName

            if name not in productResults:
                productResults[name] = []

            productResults[name].append(listing.toDict())

    for product, matchedListings in productResults.iteritems():
        print json.dumps({'product_name': product, 'listings': matchedListings})

def usage():
    print """challenge.py, an implementation of Sortable's coding challenge
Copyright (C) 2012 Matt Lawrence

 -h, --help              displays this help
 -p, --products=FILE     use a specific product file, defaults to 'products.txt'
 -l, --listings=FILE     use a specific listing file, defaults to 'listings.txt'"""

if __name__ == '__main__':
    main()
