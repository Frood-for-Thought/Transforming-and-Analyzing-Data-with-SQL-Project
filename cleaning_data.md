## What issues will you address by cleaning the data?

- Divide the unit price by 1000000
- Check if the visitstarttime timestamp and date columns have mismatching dates.
- Changing where statement to, (WHERE DATE(TO_TIMESTAMP(visitstarttime)) <> date AND DATE(TO_TIMESTAMP(visitstarttime)) > date;), gave the same results, so it is most likely that the date column has not matched with the date in viststarttime's time zone. Therefore, the dates column is changed to have the dates in visitstarttime.

- The date in all_sessions also has the same error as analytics.
- After fixing the dates in the analytics table,
- An interim table is created to store all the visitid values and their dates.
- The CTE takes the visitid's and dates from both the all_sessions and analytics tables.
- Insert the values from the CTE into the interim table so that keys from both the tables are preserved.
- The dates from the all_sessions table can be removed now that they are preserved in visitid_values table.
- The date and time are also preserved in a new table "all_sessions_date_time".
- The date and time in all_sessions could be due to an error between time zones. However, even with adding the time to date in the all_sessions column, it still does not match up well with visitstarttime in analytics.
- The query for the all_sessions_date_time table joined with analytics may shows that date and time could have been recorded in one timezone while the timestamp in the analytics table is recorded in distinct time zones.

- The units_sold value needs to be an integer and the column has negative values.
- Remove negative values in units sold.
- Check if negative values are gone in units_sold.

- The pageviews need to be converted to an int.

- The transactionrevenue column is redundant and all the information in totaltransactionrevenue.
- The data is preserved in totaltransactionrevenue after removing the transactionrevenue column.
- Remove the brackets and 'not available in demo ...' from the city column in all_sessions.
- totaltransactionrevenue is divided by 1000000.
- no values of totaltransactionrevenue is less than 0.
- transactions is either 1 or NULL so it is converted from float to integer.
- Alter time in all_sessions to a time interval.
- Alter timeonsite in all_sessions to a time interval.
- sessionqualitydim have whole numbers so they are converted to int.
- all_sessions, type column looks like a boolean but the character titles may still retain some important information.  The VARCHAR was limited to 10 characters.
- productrefundamount is only null but may still be important later if refunds are given.
- divide productprice by 1000000.
- There was an error with the time and timeonsite, but the values are still preseverd on the all_sessions_time table.
- A query is created to match up the all_sessions_time.time, all_sessions_time.timeonsite, 
- all_sessions_date_time.date, analytics.visitstarttime USING(visitid).
- productrevenue is divided by 1000000.
- All revenue contains valid decimal or integer values.

- Removed the (not set) category from v2productcategory
- Removed missing title from v2productcategory.
- Removed slashes from v2productcategory.
- Removed single option only and (not set) from productvarient and lower characters to 10.
- Character length was decreased to 10 in currencycode.
- itemquantity was changed to int and values were left NULL.
- transactionid character length was decreased to 20.
- A value longer than 100 characters was removed from pagetitle.
- pagetitle was set to 100 characters.
- seachkeyword as altered to VARCHAR(20) from real.
- ecommerceaction_option was set to 20 characters in lenght.

- Remove leading spaces in products.name using trim.
- I am unsure of the scoring in the sentiment score, if the negative values are necessary.  The score was converted to a scale betwen 0 and 100. The column was then converted to an integer value.
- All the numeric values are in valid numeric format.
- All the rows are preserved testing each numeric range.

- Remove leading spaces in sales_report.name using trim.
- sentimentscore in sales_report was altered the same method used in the products table.
- Removed (not set) from column country in table all_sessions.
- Restockingleadtime in the sales_report table was converted to a days interval.
- Divided revenue by 1000000.

- Corrected city names and their locations, set city to country.
- London, US may mean London, Ohio.
- Paris, United States may mean Paris, TX.
- There is a Toronto and Vancouver in the United States.
- Set 'New York' to 'United States'.
- There is an Amsterdam in the United States.
- Hong Kong was set to China.
- Los Angeles was set to United States.
- Mexico City was set to Mexico.
- Mountain View was set to United States.
- San Francisco was set to United States.
- Singapore was set to Singapore.
- Yokohama was set to Japan.

- Duplicate rows are removed from analytics.
- Find the distinct visits where the units sold is NULL.  With this the unit price can be changed to NULL in order to remove duplicate visitid rows.  If the units_sold is not NULL, then the rows are retained in order to preserve a transaction record and possibly revenue values that are not NULL.
- Spaces are removed in product_sku.

## Queries:

-Divide the unit price by 1000000:
```
UPDATE analytics
SET unit_price = unit_price/1000000
```

- Check if the visitstarttime timestamp and date columns have mismatching dates:
```
SELECT COUNT(*)
from analytics
WHERE DATE(TO_TIMESTAMP(visitstarttime)) <> date
-- Changing where statement to, (WHERE DATE(TO_TIMESTAMP(visitstarttime)) <> date AND DATE(TO_TIMESTAMP(visitstarttime)) > date;),
-- gave the same results, so it is most likely that the date column has not matched with the date in viststarttime's time zone.
-- Therefore, the dates column is changed to have the dates in visitstarttime:
ALTER TABLE analytics
ALTER COLUMN date TYPE date
USING CAST(visitstarttime AS DATE);
```

- The date in all_sessions also has the same error as analytics:
```
SELECT (an.date - allse.date) as time_difference, *
FROM analytics AS an
FULL OUTER JOIN all_sessions AS allse
USING(visitid)
WHERE an.date <> allse.date
AND (an.date - allse.date) > 1;
```

- A new table "all_sessions_date_time" was created to preserve all_sessions, with the columns: fullvisitorid, visitid, date, time.
- The query shows that the there is either a fullvisitorid or visitid which the date or time can match up to because it comes back empty:
```
SELECT *
FROM all_sessions
WHERE fullvisitorid IS NULL
AND visitid IS NULL;
```

- The date and time in all_sessions could be due to an error between time zones. However even with adding the time to date in the all_sessions column, it still does not match up well with visitstarttime in analytics. The query may show that date and time could have been recorded in one timezone while the timestamp in the analytics table is recorded in distinct time zones:
```
SELECT asdt.date, MAKE_INTERVAL(secs => asdt.time) AS time, an.visitstarttime, 
	(MAKE_INTERVAL(secs => asdt.time) + asdt.date)::DATE AS all_sessions_new_date
FROM all_sessions_date_time AS asdt
JOIN analytics AS an
USING(visitid)
WHERE an.visitstarttime::date <> asdt.date
AND asdt.time <> 0;

-- After fixing the dates in the analytics table,
-- An interim table is created to store all the visitid values and their dates.
CREATE TABLE visitid_values (
	visitid bigint,
	visitid_date date
	);
-- The CTE takes the visitid's and dates from both the all_sessions and analytics tables.
WITH visitid_date_table AS (
	SELECT DISTINCT visitid, an.date as an_date, allse.date as allse_date,
		CASE
			WHEN an.date IS NOT NULL
				THEN an.date
			WHEN an.date IS NULL AND allse.date IS NOT NULL
				THEN allse.date
			ELSE NULL
		END AS date
	FROM analytics AS an
	FULL OUTER JOIN all_sessions AS allse
	USING(visitid)
	)
-- Insert the values from the CTE into the interim table so that keys from both the tables are preserved.
INSERT INTO visitid_values (visitid, visitid_date)
SELECT visitid_date_table.visitid, visitid_date_table.date
FROM visitid_date_table;
-- The dates from the all_sessions table can be removed now that they are preserved in visitid_values table.
ALTER TABLE all_sessions DROP COLUMN date;
```

- The units_sold value needs to be an integer and the column has negative values:
```
ALTER TABLE analytics ALTER units_sold TYPE int;
SELECT DISTINCT units_sold
FROM analytics
ORDER BY units_sold asc;
-- Need to remove negative values in units sold during data cleansing.
UPDATE analytics
SET units_sold = NULL
WHERE units_sold < 0;
-- Check if negative values are gone.
SELECT units_sold
FROM analytics
WHERE units_sold < 0;
```

- The pageviews need to be converted to an int:
```
SELECT DISTINCT pageviews
FROM analytics;
ALTER TABLE analytics ALTER pageviews TYPE int;
```

- The transactionrevenue column is redundant and all the information in totaltransactionrevenue. The data is preserved in totaltransactionrevenue after removing the transactionrevenue column:
```
SELECT *
FROM all_sessions
WHERE totaltransactionrevenue IS NOT NULL
AND transactionrevenue <> totaltransactionrevenue;
ALTER TABLE all_sessions DROP COLUMN transactionrevenue;
```

- Remove the brackets and 'not available in demo ...' from the city column in all_sessions:
```
UPDATE all_sessions
SET city = NULL
WHERE city ~ '[()]'
OR city LIKE 'not available %';
```

- totaltransactionrevenue is divided by 1000000:
```
UPDATE all_sessions
SET totaltransactionrevenue = totaltransactionrevenue/1000000;
-- no values of totaltransactionrevenue is less than 0.
SELECT COUNT(totaltransactionrevenue)
FROM all_sessions
WHERE totaltransactionrevenue IS NOT NULL
AND totaltransactionrevenue < 0;
-- totaltransactionrevenue contains valid decimal or integer values.
SELECT totaltransactionrevenue
FROM all_sessions
WHERE totaltransactionrevenue IS NOT NULL
AND totaltransactionrevenue BETWEEN 1 AND 99999;
```

- transactions is either 1 or NULL so it is converted from float to integer:
```
SELECT DISTINCT transactions
FROM all_sessions;
ALTER TABLE all_sessions
ALTER COLUMN transactions TYPE integer;
```

- Alter time in all_sessions to a time interval:
```
ALTER TABLE all_sessions
ALTER COLUMN time TYPE interval
USING MAKE_INTERVAL(secs => time);
```

- Alter timeonsite in all_sessions to a time interval:
```
ALTER TABLE all_sessions
ALTER COLUMN timeonsite TYPE interval
USING MAKE_INTERVAL(secs => timeonsite);
```

- sessionqualitydim have whole numbers so they are converted to int:
```
SELECT DISTINCT sessionqualitydim
FROM all_sessions;
ALTER TABLE all_sessions ALTER sessionqualitydim TYPE int;
```

- divide productprice by 1000000:
```
UPDATE all_sessions
SET productprice = productprice/1000000;
```

- There was an error with the time and timeonsite, but the values are still preseverd on the all_sessions_time table. The following query matches up the all_sessions_time.time, all_sessions_time.timeonsite, all_sessions_date_time.date, analytics.visitstarttime, USING(visitid):
```
SELECT visitid, ast.time::time, ast.timeonsite::time, asdt.date, an.visitstarttime
from all_sessions_time AS ast
JOIN all_sessions_date_time AS asdt
	USING(visitid)
JOIN analytics AS an
	USING(visitid);
```
	
- productrevenue is divided by 1000000:
```
UPDATE all_sessions
SET productrevenue = productrevenue/1000000;
```

- all revenue contains valid decimal or integer values.
- Remove the (not set) category from v2productcategory:
```
UPDATE all_sessions
SET v2productcategory = NULL
WHERE v2productcategory ~ '[()]';
-- remove missing title from v2productcategory
UPDATE all_sessions
SET v2productcategory = NULL
WHERE LOWER(v2productcategory) LIKE '%title%';
-- remove slashes from v2productcategory
UPDATE all_sessions
SET v2productcategory = TRANSLATE(v2productcategory, '/', ' ')
WHERE v2productcategory ~ '[/]';
```

- Remove single option only and (not set) from productvarient and lower characters to 10:
```
SELECT DISTINCT productvariant
FROM all_sessions
WHERE LOWER(productvariant) LIKE 'single%'
OR productvariant ~ '[()]';
-- remove options
UPDATE all_sessions
SET productvariant = NULL
WHERE LOWER(productvariant) LIKE 'single%'
OR productvariant ~ '[()]';
```

- character length was decreased to 10 in currencycode.
- item quantity was changed to int and values were left NULL.
- transactionid character length was decreased to 20.
- A value longer than 100 characters was removed from pagetitle:
```
UPDATE all_sessions
SET pagetitle = NULL
WHERE LENGTH(pagetitle) > 100;
```
- seachkeyword altered to VARCHAR(20) from real:
```
ALTER TABLE all_sessions ALTER searchkeyword TYPE VARCHAR(20);
```
- ecommerceaction_option was set to 20 characters in lenght.
- Remove leading spaces in products.name using trim:
```
UPDATE products
SET name = TRIM(name);
-- I am unsure of the scoring in the sentiment score, if the negative values are
-- necessary.  The score was converted to a scale betwen 0 and 100.
-- The column was then converted to an integer value.
SELECT DISTINCT (ROUND(sentimentscore*100)+100)/2
FROM products;
```

- After review table is updated:
```
UPDATE products
SET sentimentscore = (ROUND(sentimentscore*100)+100)/2;
ALTER TABLE products ALTER sentimentscore TYPE int;
-- All the numeric values are in valid numeric format.
-- All the rows are preserved testing each numeric range.
SELECT *
FROM products
WHERE orderedquantity BETWEEN 0 AND 999999
AND stocklevel BETWEEN 0 AND 99999
AND restockingleadtime BETWEEN 0 and 9999
AND sentimentmagnitude BETWEEN 0 AND 100
OR sentimentmagnitude IS NULL;
SELECT sentimentscore
FROM products
WHERE sentimentscore BETWEEN 0 AND 100
OR sentimentscore IS NULL;
```

-- Remove leading spaces in sales_report.name using trim.
UPDATE sales_report
SET name = TRIM(name);
-- sentimentscore in sales_report was altered the same method used in the products table.
UPDATE sales_report
SET sentimentscore = (ROUND(sentimentscore*100)+100)/2;
ALTER TABLE sales_report ALTER sentimentscore TYPE int;

-- Remove (not set) from column country in table all_sessions.
UPDATE all_sessions
SET country = NULL
WHERE LOWER(country) LIKE '%(not set)%';

-- restockingleadtime in the sales_report table was converted to a days interval.
ALTER TABLE sales_report
ALTER COLUMN restockingleadtime TYPE interval
USING MAKE_INTERVAL(Days => restockingleadtime);

-- divide revenue by 1000000.
UPDATE analytics
SET revenue = revenue/1000000;

-- Corrected city names and their locations, set city to country.
-- London, US may mean London, Ohio.
-- Paris, United States may mean Paris, TX.
-- There is a Toronto and Vancouver in the United States.
-- Set 'New York' to 'United States'.
-- There is an Amsterdam in the United States.



-- Find cities which have more than one distinct country.  In some cases this could be true.
SELECT city, COUNT(DISTINCT country)
FROM all_sessions
GROUP BY city
HAVING COUNT(DISTINCT country) > 1
AND city IS NOT NULL;
-- Corrected city names and their locations, set city to country.
-- This query is used to list which countries the city appeared in to cross reference if there is one.
SELECT DISTINCT country, city
FROM all_sessions
WHERE city LIKE 'city_name';
-- The query is used to update the city with their country if there should only be a single one.
UPDATE all_sessions
SET country = 'country_name'
WHERE city LIKE 'city_name';

-- Fix fullvisitorid's and fill in NULL information if there are missing cities or there are two countries per single id.
WITH visitor_city_country AS (
	SELECT DISTINCT fullvisitorid, country, city
	FROM all_sessions
	)
SELECT fullvisitorid, COUNT(*)
FROM visitor_city_country
GROUP BY fullvisitorid
HAVING count(*) > 1;

UPDATE all_sessions
SET city = _
WHERE fullvisitorid = _;

-- searchkeyword has no information and was removed.

-- Duplicate rows are removed from analytics.
-- Find the distinct visits where the units sold is NULL.  With this the unit price can be changed to NULL in order
-- to remove duplicate visitid rows.  If the units_sold is not NULL, then the rows are retained in order to preserve
-- a transaction record and possibly revenue values that are not NULL.
-- Query to make a new table new_analytics, which removes duplicate rows in the analytics table.
WITH new_analytics1 AS (
	SELECT DISTINCT 
	visitnumber, visitid, visitstarttime, date, fullvisitorid, channelgrouping, socialengagementtype,
	units_sold, pageviews, timeonsite, bounces, revenue, 
		CASE
			WHEN units_sold IS NULL
				THEN NULL::int
			ELSE unit_price
		END AS unit_price
	FROM analytics
	ORDER BY visitid
	),
new_analytics2 AS (
	SELECT
		ROW_NUMBER() OVER (ORDER BY visitid ASC) AS visit_session, *
	FROM new_analytics1
	)
INSERT INTO new_analytics
SELECT *
FROM new_analytics2;
-- The values from visitid_values are put into new_analytics so now the table can be removed.
WITH new_dates AS (
	SELECT *
	FROM new_analytics na
	FULL OUTER JOIN visitid_values vv
		USING(visitid)
	WHERE na.date IS NULL
	)
UPDATE new_analytics AS na
SET date = nd.visitid_date
FROM new_dates AS nd
WHERE na.visitid = nd.visitid
AND na.fullvisitorid = nd.fullvisitorid;

-- Update pageview in analytics.
UPDATE new_analytics
SET pageviews = alls.pageviews
FROM all_sessions AS alls
WHERE new_analytics.pageviews IS NULL;

-- Spaces are removed in product_sku.
