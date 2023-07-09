What issues will you address by cleaning the data?

- Divide the unit price by 1000000

-- Check if the visitstarttime timestamp and date columns have mismatching dates.
-- Changing where statement to, (WHERE DATE(TO_TIMESTAMP(visitstarttime)) <> date AND DATE(TO_TIMESTAMP(visitstarttime)) > date;),
-- gave the same results, so it is most likely that the date column has not matched with the date in viststarttime's time zone.
-- Therefore, the dates column is changed to have the dates in visitstarttime.

-- The date in all_sessions also has the same error as analytics.
-- After fixing the dates in the analytics table,
-- An interim table is created to store all the visitid values and their dates.
-- The CTE takes the visitid's and dates from both the all_sessions and analytics tables.
-- Insert the values from the CTE into the interim table so that keys from both the tables are preserved.
-- The dates from the all_sessions table can be removed now that they are preserved in visitid_values table.


-- The units_sold value needs to be an integer and the column has negative values.
-- Need to remove negative values in units sold during data cleansing.
-- Check if negative values are gone in units_sold.

-- The pageviews need to be converted to an int.

Queries:
Below, provide the SQL queries you used to clean your data.

-Divide the unit price by 1000000
UPDATE analytics
SET unit_price = unit_price/1000000

-- Check if the visitstarttime timestamp and date columns have mismatching dates.
SELECT COUNT(*)
from analytics
WHERE DATE(TO_TIMESTAMP(visitstarttime)) <> date
-- Changing where statement to, (WHERE DATE(TO_TIMESTAMP(visitstarttime)) <> date AND DATE(TO_TIMESTAMP(visitstarttime)) > date;),
-- gave the same results, so it is most likely that the date column has not matched with the date in viststarttime's time zone.
-- Therefore, the dates column is changed to have the dates in visitstarttime:
ALTER TABLE analytics
ALTER COLUMN date TYPE date
USING CAST(visitstarttime AS DATE);

-- The date in all_sessions also has the same error as analytics.
SELECT (an.date - allse.date) as time_difference, *
FROM analytics AS an
FULL OUTER JOIN all_sessions AS allse
USING(visitid)
WHERE an.date <> allse.date
AND (an.date - allse.date) > 1;

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

-- The units_sold value needs to be an integer and the column has negative values.
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

-- The pageviews need to be converted to an int.
SELECT DISTINCT pageviews
FROM analytics;
ALTER TABLE analytics ALTER pageviews TYPE int;