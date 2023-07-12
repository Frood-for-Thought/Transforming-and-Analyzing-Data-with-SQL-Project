# Final-Project-Transforming-and-Analyzing-Data-with-SQL

## Project/Goals
Can any product revenue, name, category patterns be extrapolated from the website data provided?
What are the patters with respect to user, country, and/or city?


## Process
NOTE: Some cleaning_data and QA process notes are taken from the QA.md file and are also listed here in Process with a "-" in the front.

Following Part 1 in the assignment.md file, a new PostgreSQL database called `ecommerce` was created.
A program "read_table_column_name_and_type_function.py" was created to display each table column with their datatype.
When running the program, input exact file_name and type "c" for .csv or "x" for .xlsx and the program will list the file's column names and their datatypes.
Note: make sure the program is in the same location as the table files to read for it to work.

(Parts of notes taken from QA Process or cleaning_data)
- When importing data, in order for the process to succeed, all columns with characters needed to have appropriate lengths.
	- The pageTitle column in the all_sessions table needed to be extended to 600 characters in order to import the data,
	needed to find area where pageTitle > 500 characters.
- Column titles needed to be converted to lowercase for easier usage and so the queries tool can recognize the titles typed out after SELECT.
	- A list of all each file's column names in lowercase was provided by the "read_table_column_name_and_type_function.py", 
	so that the column names and data types could be known before being inserted into the table values in SQL.


-- During QA, in pgAdmin, list the column names, data types, character max length or number precision, 
-- if column is nullable, and if it is updateable.

-- Divide the unit_price by 1000000 in cleaning_data.
-- date column reformatted in analytics and all_sessions tables.  For full detail on what was done real the cleaning_data file.

-- Test if conversion to big_int is allowable for fullvisitorid without losing unique IDs for analytics and all_sessions tables.
-- Reformatted fullvisitorid in tables analytics and all_sessions.

-- Change the visitstarttime column in analytics from unix epoch to a timestamp.
-- Check if the visitstarttime timestamp and date columns have mismatching dates.
-- The date in all_sessions also has the same error as in analytics.
-- After fixing the dates in the analytics table,
-- An interim table is created to store all the visitid values and their dates.
-- The CTE takes the visitid's and dates from both the all_sessions and analytics tables.
-- The values from the CTE are inserted into the interim table so that keys from both the tables are preserved.

-- The units_sold value needs to be an integer and the column has negative values.
-- Need to remove negative values in units sold during data cleansing.
-- Check if negative values are gone in units_sold.

-- The pageviews need to be converted to an int.
-- The transactionrevenue column is redundant in all_sessions and all the information in totaltransactionrevenue.
-- The data is preserved in totaltransactionrevenue after removing the transactionrevenue column.
-- Remove the brackets and 'not available in demo ...' from the city column in all_sessions.
-- totaltransactionrevenue is divided by 1000000.
-- no values of totaltransactionrevenue is less than 0.
-- transactions is either 1 or NULL so it is converted from float to integer.
-- Alter time in all_sessions to a time interval.
-- Alter timeonsite in all_sessions to a time interval.
-- sessionqualitydim have whole numbers so they are converted to int.
-- all_sessions, type column looks like a boolean but the character titles may still retain some 
-- important information.  The VARCHAR was limited to 10 characters.
-- productrefundamount is only null but may still be important later if refunds are given.
-- divide productprice by 1000000.
-- no values of productprice is less than 0.
-- There was an error with the time and timeonsite, but the values are still preseverd on the all_sessions_time table.
-- A query is created in cleaning_data to match up the all_sessions_time.time, all_sessions_time.timeonsite, 
-- all_sessions_date_time.date, analytics.visitstarttime USING(visitid).
-- productrevenue is divided by 1000000.
-- no values of productrevenue is less than 0.
-- all revenue contains valid decimal or integer values.

-- A query shows there are unique values in sales_by_sku which are not in the tables products or sales_report.
-- The table should not be deleted because of this but it should be deleted after preserving those values.
-- This one-to-one table seems redundant and everything could be placed into the sales_report table.
-- Products should get a unique products key and not the sku column, while sales_report should get a sales key.
-- In this case, for now sales_report can have productsku as its primary key which link to all_sessions productsku
-- as a foreign key.
-- the character limit in all the columns with sku was shortened to 20.

-- v2productname can be shortened to 100 characters.
-- Reveiwing the format of v2productname to make sure they are capitalized at the start
-- or start with a number.  The remaining products start with two capitals.
-- A CTE to add up all the products with the right format,
-- adds to the same count of rows in v2productname.
-- Therefore all rows have proper format at the start.
-- Removed the (not set) category from v2productcategory.
-- Removed missing title from v2productcategory.
-- Removed slashes from v2productcategory.
-- Removed single option only and (not set) from productvarient and lower characters to 10.
-- Character length was decreased to 10 in currencycode.
-- itemquantity was changed to int and values were left NULL.
-- transactionid character length was decreased to 20.
-- A value longer than 100 characters was removed from pagetitle.
-- pagetitle was set to 100 characters.
-- seachkeyword as altered to VARCHAR(20) from real.
-- ecommerceaction_option was set to 20 characters in lenght.

-- Remove leading spaces in products.name using trim.
-- I am unsure of the scoring in the sentiment score, if the negative values are
-- necessary.  The score was converted to a scale betwen 0 and 100.
-- The column was then converted to an integer value.
-- All the numeric values are in valid numeric format.
-- All the rows are preserved testing each numeric range.

-- Remove leading spaces in sales_report.name using trim.
-- sentimentscore in sales_report was altered the same method used in the products table.
-- Removed (not set) from column country in table all_sessions.
-- Restockingleadtime in the sales_report table was converted to a days interval.
-- Divided revenue by 1000000.

-- Verified there are no locations with cities without countries in all_sessions table for QA.
-- During cleaning_data, found some cities which have more than one distinct country.  In some cases this could be true.
-- Corrected city names and their locations, set city to country.
-- Fix fullvisitorid's and fill in NULL information if there are missing cities or there are two countries per single id.
-- London, US may mean London, Ohio.
-- Paris, United States may mean Paris, TX.
-- There is a Toronto and Vancouver in the United States.
-- Set 'New York' to 'United States'.
-- There is an Amsterdam in the United States.
-- Hong Kong was set to China.
-- Los Angeles was set to United States.
-- Mexico City was set to Mexico.
-- Mountain View was set to United States.
-- San Francisco was set to United States.
-- Singapore was set to Singapore.
-- Yokohama was set to Japan.

-- Duplicate rows are removed from analytics when transferring to new_analytics.
-- Instead of millions of rows there are now over 200000.
-- Find the distinct visits where the units sold is NULL.  With this the unit price can be changed to NULL in order
-- to remove duplicate visitid rows.  If the units_sold is not NULL, then the rows are retained in order to preserve
-- a transaction record and possibly revenue values that are not NULL.
-- The values from visitid_values are put into new_analytics so now the table can be removed.
-- Now new_analytics has a record of every visitid, but there are still duplicates if 

The starting_with_questions were answered after cleaning_data and some QA.
-- Some of the v2productname and v2productcategory errors and inconsistencies were cleaned during the starting_with_questions.
-- (You Tube -> YouTube, Earbud -> Earbuds, etc.)

-- Combined the information from tables products, sales_by_sku, and sales_report
-- into the table product_information to get rid of redundant information.

-- product_information still has a lot of duplicate rows for product_sku to be a primary key,
-- it still requires a lot of work to filter through all the productnames and productcategory values.
-- Also filtering down the productnames may could cause a loss in information, such as brand names.
-- More time is needed to go through the product_information table before product_sku can be a primary key.
-- However, the tables products, sales_report, and sales_by_sku can now be removed because all the infomation is preserved in product_information.
-- The order details are removed from product_information are now in the table product_order with product_sku being the primary key.

-- There are still duplicate values of visitid in the new_analytics table in order to preserve missing transaction revenue,
-- so that table column cannot become a primary key. Instead a new row, visit_session was made to be the primary key.

-- The main takeaway from Question 2 of starting_with_data, is that there are a lot of countries and cities unaccounted for
-- across the globe, and more data gathering needs to be done to match the fullvisitorid with the country and city.

-- There are five main tables now, all_sessions, new_analytics, product_information, product_order, and fullvisitorid_location.
-- In order to preserve data I still had duplicare product_sku's, fullvisitorid's and visitid's and was not able to get to 3NF.

## Results

Tested and converted to fullvisitorid to bigint without losing unique IDs for analytics and all_sessions tables.
Revenues were divided by 1000000.
Change the visitstarttime column in analytics from unix epoch to a timestamp.
The transactionrevenue column is redundant in all_sessions and all the information is stored in totaltransactionrevenue.
Discreet units were converted to integer while continuous were real.
VARCHAR were shortened to meet the needs of table column with characters and values far above that were reformatted or removed.
Remove leading spaces in product names using trim.
A lot of the product names and categories were cleaned up.
Verified there are no locations with cities without countries in all_sessions table.
Fixed fullvisitorid with country and city, filled in NULL information if there are missing cities or there are two countries per single id.
Found some cities which have more than one distinct country, and corrected this in cases where this wasn't true.
Sentimentscore was converted to a scale betwen 0 and 100.
Duplicate rows are removed from analytics when transferring to new_analytics.
Instead of millions of rows there are now over 200000.

Partial starting_with_questions answers:
Question 1: Which cities and countries have the highest level of transaction revenues on the site?
The country with the highest transaction revenue is the United States with 250813.56.
The city with the highest transaction revenue is San Francisco, United States, with 1564.32,
(not counting NULL as a city).

Question 2: What is the average number of products ordered from visitors in each city and country?
Including orders from the analytics table incase all_sessions is NULL,
the country with the highest average order quantity is Vietnam,
while the city with the highest order quantity is Dallas.

Question 3: Is there any pattern in the types (product categories) of products ordered from visitors in each city and country?
The most popular category for all the counties was YouTube, appearing on the top of the list for 114 countries, and
Google coming in second at 12 countries if going by sponsor brands, the least popular was Android.
Without taking sponsored brand names, the catagory that was most popular was Office supplies.

Question 4: What is the top-selling product from each city/country? Can we find any pattern worthy of noting in the products sold?
The most popular product sold overall are 'Yoga Supplies' in the United States with most ordered in Mountain View.
However, sweater products were the most popular in 73 countries while yoga supplies were the second most popular, being 16 countries.
Sweaters were the most popular in the most cities with 68 cities, while Yoga Supplies came second, being the most popular in 13 cities.

When not ordering the products sold by editing and grouping the original names, the most popular item was 
YouTube Wool Heather Cap Heather/Black being the most popular in 30 countries, and the most popular item
sold per country was YouTube Youth Short Sleeve Tee Red in the United States.

Question 5: Can we summarize the impact of revenue generated from each city/country?
From the records which takes into account countries which are not null, 
it appears United States accounts for 92.52% of all the revenue generated per country.  
The next is Israel with 4.25%, then Australia with 2.53%.

The city with the most revenue generated is San Francisco, United States, with 11.05% of the total revenue, 
(in this case the total revenue from all the non-NULL countries, which includes unrecorded cities with NULL).  
The next city being Sunnyvale, with 7.01% of the revenue generated.  
The lowest was Zurich, Switzerland, with 0.096%.
There was a total of 19 cities recorded which generated revenue.

starting_with_data summary:

A query was made to approximate the revenue gained when the value in the revenue column in the analytics table is NULL.
Compared to questions 1 and 5 in starting_with_questions, now 99.10% of the revenue is going to countries which are
not listed and given a NULL category.  While the approximate tax is not exact in question 1
for starting_with_data, it may give a more accurate summery over how the revenue is distributed between countries.

In question 1 and 5 there were a total of 5 countries recorded which did not contain NULL values, now with
approximating the revenue per transaction in the analytics table, it has increased to 14 countries.
These countries have even less percent of the revenue generated than compared to questions 1 and 5 because now 
there is more revenue going to countries without a category and labelled NULL. 
The country with the highest transaction revenue is still the United States.

Compared to question 1 and 5, there is now 32 cities recorded instead of 19.  Of the categories with cities and countries which
are not including missing values, the city with the most revenue generated is Sunnyvale, and following
that is Mountain View.  Unlike question 5 in starting_with_questions, San Francisco is now 4th instead of 1st.

It is important to note that even with an approximation to broaden the amount of countries and cities collected, there is still
a lot of missing data.  More records should be gathered to find 99.10% of the revenue going to other countries in order for there
to be a more accurate accounting going on in other cities.

There are 14223 distinct fullvisitorid's in the all_sessions table and 120018 distinct in the analytics table.
Between the two tables there are 130345 distinct fullvisitorid's. 
Which means each table contains unique fullvisitorid's so care should be made when creating a primary key.

There are 14556 distinct visitid's in the all_sessions table and 148642 distinct in the analytics table.
Between the two tables there are 159538 distinct visitid's which is less than 163198 added between the two tables.
Like fullvisitorid's, each table contains unique visitid's so care should be made when creating a primary key using visitid.

SELECT count(distinct visitid), count(distinct fullvisitorid)
FROM new_analytics;
-- Shows 159538 and 130345, which means the new_analytics table now contains all the unique fullvisitorid's and visitid's.

The country with the maximum number of pageviews is the United States.
There was no correlation with start time and pageviews, (p-value > 0.05 using regression analysis).
The second highest was China.

Compared to question 2, Mountain View has the most traffic, with 10246 pageviews, however, it looks like Sunnyvale has
generated more revenue with fewer pageviews, being 8207.

What should be noted, is that there were 265 cities with pageviews, however, only 32 cities were recorded to make purchases.
Most pageviews go to cities unaccounted for.

There are still duplicate values of visitid in the new_analytics table in order to preserve missing transaction revenue.
A new row, visit_session was made to be the primary key. Unique visitid's can have multiple values for units_sold, unit_price, and revenue.
More work needs to go into gathering data to determine if there are multiple orders per visit or if a lot of the information is redundant.
From the data gathered, fullvisitorid's are making multiple purchases of the same product during the same visitid or during multiple visits,
based on different order quantities, unit_prices, revenue generated, and multiple visitid's for the same product.

Despite Yoga Supplies generating the most revenue, sweater products were the most popular in 73 countries 
while yoga supplies were the second most popular, being 16 countries. 
It looks like most purchases for yoga supplies are being made in the United States, while other products are being viewed in other countries.  
Since a lot of revenue is unaccounted for in other countries, visitor views could be gauge for what items are popular to purchase.

Including the approximation, there were 463 distinct fullvisitorid's which made a purchase on the site.  
That's 0.35% when compared to 130345 ids in question 3, which further affirms a lot of missing revenue data.
There is also around 120000 fullvisitorid's with no country or city.

## Challenges 
More work needs to go into gathering data to determine if there are multiple orders per visit or if a lot of the information is redundant.

There are five main tables now, all_sessions, new_analytics, product_information, product_order, and fullvisitorid_location.
In order to preserve data I still have duplicare product_sku's, fullvisitorid's and visitid's and was not able to get to 3NF.

## Future Goals

Instead of general productnames, more work needs to go into matching one productname with one sku in order to make a primary key in product_information.

Since an approximate estimate showed 99% of the revenue is going to countries which are not listed more work needs to be done to fill in those values.
The purchase revenue data is a small snapshot of what the total global purchases done are, and as a result can have a false positive with what
item is popular.  

More work needs to go into clarifying how much revenue is generated per visitid and to which country and city that revenue is coming from.
After data is gathered on revenue, country and city, only then can all_sessions have fullvisitorid as its primary key, 
and new_analytics have visitid as its primary key.  

The webpage time, productsku, pagetitle, and pagepathlevel1 also needs to be cleaned before fullvisitorid can become the foreign key of all_sessions
with the table's own primary key.
