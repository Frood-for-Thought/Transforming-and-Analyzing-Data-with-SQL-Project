What are your risk areas? Identify and describe them.

The main goal was to normalize the data to become more structured and less redundant, 
and a lot of this was done during QA and data cleaning.  However,
two tables still have duplicate values, the reason for this are described below or in
Challenges and Future Goals in README.

THE FOLLOWING RISK AREAS ARE LISTED UNDER FUTURE GOALS IN README.
Product_information still has a lot of duplicate rows for product_sku to be a primary key,
it still requires a lot of work to filter through all the productnames and productcategory values.
Also filtering down the productnames may could cause a loss in information, such as brand names.
More time is needed to go through the product_information table before product_sku can be a primary key.
However, the tables products, sales_report, and sales_by_sku can now be removed because all the infomation is preserved in product_information.
The order details are removed from product_information are now in the table product_order with product_sku being the primary key.

The main takeaway from Question 2 of starting_with_data, is that there are a lot of countries and cities unaccounted for
across the globe, and more data gathering needs to be done to match the fullvisitorid with the country and city.

There are still duplicate values of visitid in the new_analytics table in order to preserve missing transaction revenue,
so that table column cannot become a primary key. Instead a new row, visit_session was made to be the primary key.
A new table was created called fullvisitorid_location with fullvisitorid as its primary key.

There are five main tables now, all_sessions, new_analytics, product_information, product_order, and fullvisitorid_location.
In order to preserve data I still have duplicare product_sku's, fullvisitorid's and visitid's and was not able to get to 3NF.
See questions 3 and 4 in starting_with_questions for dealing with productname and category risk areas sorting.

The webpage time, productsku, pagetitle, and pagepathlevel1 also needs to be cleaned before fullvisitorid can become the foreign key of all_sessions
with the table's own primary key.


QA Process:
Describe your QA process and include the SQL queries used to execute it.

- When importing data, in order for the process to succeed, all columns with characters needed to have appropriate lengths.
	- The pageTitle column in the all_sessions table needed to be extended to 600 characters in order to import the data,
	needed to find area where pageTitle > 500 characters.
- Column titles needed to be converted to lowercase for easier usage and so the queries tool can recognize the titles typed out after SELECT.
	- A list of all each file's column names in lowercase was provided by the "read_table_column_name_and_type_function.py".

- Go through Data Validation for each table.

-- In pgAdmin, list the column names, data types, character max length or number precision, if column is nullable, and if it is updateable.
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

-- The date can be reformatted with the option of text.
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
-- The following query shows there are unique values in sales_by_sku which are not in the tables products or sales_report.
-- The table should not be deleted because of this but it should be deleted after preserving those values.
-- This one-to-one table seems redundant and everything could be placed into the sales_report table.
-- Products should get a unique products key and not the sku column, while sales_report should get a sales key.
-- In this case, for now sales_report can have productsku as its primary key which link to all_sessions productsku
-- as a foreign key.
SELECT sbs.productsku, sbs.total_ordered
FROM products as pro
RIGHT JOIN sales_by_sku as sbs
	ON pro.sku = sbs.productsku
LEFT JOIN sales_report as sr
	USING(productsku)
WHERE pro.sku is null AND sr.productsku IS NULL;

-- the character limit in all the sku columns was shortened to 20.

-- v2productname can be shortened to 100 characters.
SELECT COUNT(v2productname)
FROM all_sessions
WHERE LENGTH(v2productname) > 100;

-- Reveiwing the format of v2productname to make sure they are capitalized at the start
-- or start with a number.  The remaining products start with two capitals.
SELECT v2productname, COUNT(v2productname)
FROM all_sessions
GROUP BY v2productname
HAVING v2productname NOT IN (
	SELECT v2productname
	FROM all_sessions
	WHERE LEFT(v2productname, 1) ~ '[1-9]'
	OR v2productname ~ E'^[[:upper:]][^[:upper:]]');
-- The CTE adds up all the products with the right format to 15134,
-- which adds to the same count of rows in v2productname.
-- Therefore all rows have proper format at the start.
WITH count_table AS (
	SELECT COUNT(v2productname) AS number_of_products
	FROM all_sessions
	WHERE LEFT(v2productname, 1) ~ '[1-9]'
	OR v2productname ~ E'^[[:upper:]][^[:upper:]]'
	UNION ALL
	SELECT COUNT(v2productname)
	FROM all_sessions
	WHERE v2productname NOT IN (
		SELECT v2productname
		FROM all_sessions
		WHERE LEFT(v2productname, 1) ~ '[1-9]'
		OR v2productname ~ E'^[[:upper:]][^[:upper:]]')
	)
SELECT SUM(number_of_products)
FROM count_table;

-- The following query shows there are no location with cities without countries in all_sessions.
SELECT visitid, country, city, totaltransactionrevenue
FROM all_sessions
WHERE country IS NULL AND city IS NOT NULL;


-- All_sessions contains more product name details per productsku than products.
SELECT COUNT(DISTINCT productsku), COUNT(DISTINCT v2productname)
FROM all_sessions;
SELECT COUNT(DISTINCT sku), COUNT(DISTINCT name)
FROM products;

-- Combine the information from tables products, sales_by_sku, and sales_report.
-- The CTE combines information from the products table and the product names from all_sessions.
WITH product_sku_names_cat_list AS (
	SELECT
		CASE
			WHEN alls.productsku IS NULL
				THEN pro.sku
			ELSE alls.productsku
		END AS product_sku,
		CASE
			WHEN alls.productsku IS NOT NULL
				THEN alls.v2productname
			WHEN pro.sku IS NOT NULL
				THEN pro.name
			ELSE alls.v2productname
		END AS productname,
	pro.*
	FROM all_sessions AS alls
	FULL OUTER JOIN products AS pro
		ON alls.productsku = pro.sku
	),
-- Combine all the tables to make one product table with all the information including the
-- distinct skus in sales_by_product.
product_information2 AS (
	SELECT DISTINCT
		CASE
			WHEN sr.productsku IS NULL AND psncl.product_sku IS NULL
				THEN sbs.productsku
			WHEN psncl.product_sku IS NULL
				THEN sr.productsku
			ELSE psncl.product_sku
		END AS product_sku,
		psncl.productname, alls.v2productcategory AS productcategory,
		alls.productvariant,
		psncl.orderedquantity, sr.stocklevel,
		sr.restockingleadtime, sr.sentimentscore, sr.sentimentmagnitude,
		sr.ratio, sbs.total_ordered
	FROM product_sku_names_cat_list AS psncl
	FULL OUTER JOIN sales_report AS sr
	ON psncl.product_sku = sr.productsku
	FULL OUTER JOIN sales_by_sku AS sbs
	ON psncl.product_sku = sbs.productsku
	JOIN all_sessions AS alls
	ON psncl.product_sku = alls.productsku
	)
-- Put all the information from products, sales_by_sku, and sales_report 
-- into the table product_information to get rid of redundant information.
-- INSERT INTO product_information
-- SELECT *
-- FROM product_information2;

-- Product_information still has a lot of duplicate rows for product_sku to be a primary key,
-- it still requires a lot of work to filter through all the productnames and productcategory values.
-- Also filtering down the productnames may could cause a loss in information, such as brand names.
-- More time is needed to go through the product_information table before product_sku can be a primary key.

The order details are removed from product_information are now in the table product_order with product_sku being the primary key.
```
WITH product_info AS (
	SELECT product_sku, 
	orderedquantity, 
	stocklevel, 
	restockingleadtime, 
	sentimentscore, 
	sentimentmagnitude, 
	ratio, 
	total_ordered
	FROM product_information
	),
to_be_inserted AS (
	SELECT DISTINCT *
	FROM product_info
	)
INSERT INTO product_order
SELECT *
FROM to_be_inserted;
```

-- A new table was created called fullvisitorid_location with fullvisitorid as its primary key.
WITH visitor_city_country AS (
	SELECT DISTINCT fullvisitorid, country, city
	FROM all_sessions
	)
INSERT INTO fullvisitorid_location
SELECT *
FROM visitor_city_country;
