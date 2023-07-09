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


- In pgAdmin, list the column names, data types, character max length or number precision, if column is nullable, and if it is updateable.

- Divide the unit_price by 1000000

-- date column reformatted in analytics and all_sessions tables.

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

## Results
(fill in what you discovered this data could tell you and how you used the data to answer those questions)

## Challenges 
(discuss challenges you faced in the project)

## Future Goals
(what would you do if you had more time?)
