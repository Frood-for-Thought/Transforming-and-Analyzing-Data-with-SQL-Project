# Final-Project-Transforming-and-Analyzing-Data-with-SQL

## Project/Goals
(fill in your description and goals here)

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
-- The date in all_sessions also has the same error as analytics.
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

-- A query shows there are unique values in sales_by_skew which are not in the tables products or sales_report.
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

The starting_with_questions were answered after cleaning_data and some QA.

## Results
(fill in what you discovered this data could tell you and how you used the data to answer those questions)

## Challenges 
(discuss challenges you faced in the project)

## Future Goals
(what would you do if you had more time?)
