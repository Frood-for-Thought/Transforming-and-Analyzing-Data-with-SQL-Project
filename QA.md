What are your risk areas? Identify and describe them.



QA Process:
Describe your QA process and include the SQL queries used to execute it.

- When importing data, in order for the process to succeed, all columns with characters needed to have appropriate lengths.
	- The pageTitle column in the all_sessions table needed to be extended to 600 characters in order to import the data,
	needed to find area where pageTitle > 500 characters.
- Column titles needed to be converted to lowercase for easier usage and so the queries tool can recognize the titles typed out after SELECT.
	- A list of all each file's column names in lowercase was provided by the "read_table_column_name_and_type_function.py".

- Go through Data Validation for each table.

- In pgAdmin, list the column names, data types, character max length or number precision, if column is nullable, and if it is updateable.
SELECT table_name, column_name, ordinal_position, data_type, 
	CASE 
		WHEN LOWER(data_type) LIKE '%character%'
			THEN character_maximum_length
		ELSE numeric_precision
	END AS char_max_length_or_num_precision,
	is_nullable, is_updatable
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

- First the column data types needed to be matched to the quality of data they held

-- Reformat the date with the option of text
SELECT date, CONCAT(LEFT(date::text, 4),'-',SUBSTRING(date::text, 5, 2),'-',RIGHT(date::text, 2)) AS date_text,
	TO_DATE(date::text, 'YYYYMMDD')
FROM analytics
LIMIT 1;

-- date column reformatted in analytics and all_sessions tables:
ALTER TABLE table_name
ALTER COLUMN date TYPE date
USING TO_DATE(date::text, 'YYYYMMDD');

-- Test if conversion to big_int is allowable for fullvisitorid without losing unique IDs for analytics and all_sessions tables:
WITH column_change AS (
	SELECT 
		COUNT(DISTINCT fullvisitorid) AS col_before_change,
		COUNT(DISTINCT CAST(fullvisitorid/10000000 AS bigint)) AS col_after_change
	FROM all_sessions --(or "analytics")
	)
-- This query comes up with 'Conversion Acceptable'.
SELECT col_before_change, col_after_change,
	CASE
		WHEN col_before_change = col_after_change
			THEN 'Conversion Acceptable'
		ELSE 'Conversion Unacceptable'
	END AS is_conversion_allowed
FROM column_change;
-- Reformat fullvisitorid in tables analytics and all_sessions:
ALTER TABLE talbe_name
ALTER COLUMN fullvisitorid TYPE bigint
USING CAST(fullvisitorid/10000000 AS bigint);

-- Change the visitstarttime column from unix epoch to a timestamp
ALTER TABLE analytics
ALTER COLUMN visitstarttime TYPE timestamp
USING TO_TIMESTAMP(visitstarttime);



--
-- The following query shows there are productsku's in sales_by_skew,
-- however the same product skews are not in the products table.
SELECT *
FROM products pro
RIGHT JOIN sales_by_sku sbs
ON pro.sku = sbs.productsku
WHERE pro.sku is null;
-- The same is true with the sales_report table.
SELECT *
FROM sales_report sr
RIGHT JOIN sales_by_sku sbs
USING(productsku)
WHERE sr.productsku IS NULL;
-- So there are unique values in sales_by_skew which are not in the tables products or sales_report.
-- The table should not be deleted because of this but it should be deleted after preserving those values.
-- This one-to-one table seems redundant and everything could be placed into the sales_report table.
-- Products should get a unique products key and not the sku column, while sales_report should get a sales key.
-- In this case, for now sales_report can have productsku as its primary key which link to all_sessions productsku
-- as a foreign key.