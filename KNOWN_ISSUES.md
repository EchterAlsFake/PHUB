# Known issues

> Here are a reference of all the issues i know/have encountered using this project.
> 
> Feel free to submit more, so hopefully they will be fixed with PHUB 4.0.

-----------

### > Search queries provide different results

**Descripton** - When 2 exact same search queries are posted with pretty much no delay between them, one of them might provide a completly
different result. I don't know why. It seems to be PH fault, or maybe some headers errors.

**Potential fix** - PHUB 4 should be able to use pornhub webmaster program for the search queries, so this should be fixed

-----------

### > 'List index out of range'

**Description** - As the api rely a lot on regexes, i was too lazy to check, each time they were used, if they were successfull. Generally, this
means Pornhub didn't returned excpected data.

**Potential fix** = PHUB 4 will have regex type wrappers which will throw more detailled errors on what went wrong. 

-----------

### > Feed object still does not work

**Description** - The Feed object is a mess. I want it to behave like a query object and not rely on bs4, because this api is meant to be as light as possible.

**Potential fix** - Too lazy, this thing is incredibly boring to code
