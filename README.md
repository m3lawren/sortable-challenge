# Sortable Coding Challenge

This is my attempt at [Sortable's coding challenge](http://sortable.com/blog/coding-challenge/).

## Getting Started

- Clone the repo `git clone git://github.com/m3lawren/sortable-challenge.git`
- Run via `python challenge.py`
- Use the `-h` or `--help` flag to see command line options
- ???
- Profit!

## Required Software

This script was tested with Python 2.7.3 on Ubuntu Precise. No third party python libraries are required.

## Algorithm

My goal with the algorithm I implemented is to focus on scaling well with large numbers of listings and a relatively smaller number of products. To accomplish this I made my matching function, `findProducts`, operate on a single listing at a time, finding all products which are a match. The basic flow is as follows:

1. Load and pre-process products.
1. For each listing in the listing file:
    1. Pre-process the listing.
    1. Call `findProducts` to see which products match the current listing.
    1. Add the listing to the list of matches for each matched product.
1. For each product:
    1. Grab the list of matched listings.
    1. Dump to JSON and append to the file.

This method allows us to scale in O(n) with the number of listings, so long as our implementation of `findProducts` is pure (no side effects). 

The first scalability issue which would be encountered is most likely having the dictionary of matched listings for each product grow too large if there are a large number of relevant listings. This could be alleviated by pushing that tracking into a more persistent storage mechanism such as a database instead of keeping it in memory, or just by breaking up the listings into batches and then merging at the end.

### The `findProducts` Algorithm

The `findProducts` algorithm is designed to be fairly accurate while being simple to understand and fast to run. The algorithm is broken up into multiple passes over the list of products, with the first pass being the most stringent and the last pass being most relaxed. The first pass which turns up matching product(s) has its list of matching product(s) returned as the result.

*Note: All text comparison is presumed to be case-insensitive unless otherwise specified.*

1. Match on exact model, manufacturer and family. I define the *exact model* as being the model number with no adjacent alphanumeric characters. So if the model is `D40` then `foo-D40-bar` is an exact match but `D40N` is not because of the trailing `N`. If the listing contains the exact model, manufacturer and family of a product, then this means that it is a match for all of the product data we have and thus is the highest quality.
1. Match on exact model and manufacturer. If the listing contains the exact model and manufacturer but not the family, then it is still most likely a high quality listing and is relevant to our interests.
1. Match on model with trailing non-digit, manufacturer and family. This is the same as exact model above, but it allows a non-numeric character after the model number. For example with `D40`, `D400` would not match but `D40N` would match. This was implemented because some companies append letters to the model to indicate colour, so `D40B` might be black while `D40W` might be white.
1. Match on model with trailing non-digit and manufacturer, same logic as above. 
1. Match on model with any leading/trailing non-digit, manufacturer and family. This is a slightly more relaxed version of the previous steps, with similar logic.
1. Match on model with any leading/trailing non-digit and manufacturer.
1. Match on manufacturer, family, and ` for `. This is done because some accessories are intended to  cover a broad range of camera models, and may be listed as `Cover for Fujifilm Finepix Series`. If we did not find a known model number in the previous steps, then this is probably what happened.

### Product Pre-Processing

As we load our list of products, we do a bit of pre-processing on them in order to make life easier when we are doing our matching. First we perform a bit of voodoo on model numbers and families for a few strange manufacturers:

* Olympus lists their PEN series of cameras with a model of `PEN xxxxx`, so we sanitize this by moving `PEN` to the family and strip it off of the model.
* Panasonic's DMC series does the same, so we strip off the leading `DMC-` and move it to the family.
* Sony's DSLR series is the same as well, so we treat it the same way.

After this is done, we lowercase all strings which we might use. This is done at this point so it does not need to be done repeatedly down the road. Once lower-cased we create variations of the model names which we might see. We create a number of variations to accomodate vendor variations in how product models are displayed. In the vast majority of cases these should not cause false positives.

* Strip spaces
* Strip dashes
* Replace dashes with spaces
* Replace spaces with dashes

Once we have our list of variations, we use them to create three regexes which are used to match the model number in the `findProducts` algorithm:

* Exact match - any of the model variations surrounded by non-alphanumerics
* Match with trailing non-digit - any of the model variations with a leading non-alphanumeric and a trailing non-digit
* Match with leading and trailing non-digit - any of the model variations surrounded by non-digits

We do not worry about manually stripping out duplicate variations, for example `D40` would have all four variations the same. We rely on the regex implementation being smart enough to dedupe these when converting into a DFA.

## Performance

The initial performance with this algorithm took about 1min to process the sample dataset on my Linode 1024. I'm impatient, so I decided to see if I could make some improvements:

1. The first thing I did was merge pairs of steps together. Steps 1&2, 3&4 and 5&6 are actually done at the same time. The code checks the regexes for a match, and then depending on whether or not the family is found it adds the product to either the `matchedFamily` or `matchedNoFamily` list. Then when it is done looping over the products, it will return `matchedFamily` if it is non-empty, then try and return `matchedNoFamily` if it is non-empty. If both are empty it moves to the next step. This was done in c0a3190ea4.
1. The second thing was to switch off case-insensitivity in the regex compilation. Since it was already lower-casing all relevant strings, there was a small improvement to be had at no cost. This was done in 2970d1dbd1.
1. The last change I made was to change the regex grouping to be non-capturing. This meant that the regex implementation didn't have to keep track of which of the model variants were matched and instead could just worry about whether there was a match or not. This was another respectable performance bump, and was done in 8e63ba32c0.

I think the next place where the algorithm could be improved would be switching away from regexes and just using plain string comparison. The only reason I used regexes was for ease of implementation, I think that string comparison could be used instead with better performance.

## License

This code is made available under the [MIT license](http://opensource.org/licenses/MIT).
