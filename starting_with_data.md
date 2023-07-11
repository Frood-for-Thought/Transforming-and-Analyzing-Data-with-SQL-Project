Question 1:  Using the locations with units_sold and revenue, find the average tax that would be placed on revenue.
Then use the average tax generated per units sold and unit price to approximate the revenue gained when the value 
in the revenue column is NULL.

SQL Queries: 

-- There are NO locations where revenue is not null and units_sold is null.
-- 
WITH id_rev_tax AS (
	SELECT visitid, revenue, unit_price, 
		units_sold, 
		(revenue - (unit_price*units_sold)) AS tax,
		((revenue - (unit_price*units_sold))/(unit_price*units_sold))*100 AS percent_tax
	FROM analytics
	WHERE units_sold IS NOT NULL AND revenue IS NOT NULL
	AND unit_price*units_sold > 0
	ORDER BY units_sold, unit_price
	),
-- This CTE now calculates the average tax grouped up with units sold and with price.
avg_tax_per_unit AS (
	SELECT DISTINCT
		units_sold, unit_price, 
		AVG(tax) OVER (PARTITION BY units_sold) AS avg_tax_per_units_sold,
		AVG(tax) OVER (PARTITION BY units_sold, unit_price) AS avg_tax_per_unit_sold_with_price
	FROM id_rev_tax
	ORDER BY units_sold, unit_price
	),
-- SELECT *
-- FROM avg_tax_per_unit
-- ORDER BY units_sold, unit_price;

-- This CTE now caluclates an approximation for the revenue gained using the avg_tax_per_unit_sold_with_price.
-- This is now a revenue value to fill in the sections in the analytics table where revenue is NULL.
visitid_missing_revenue AS (
	SELECT DISTINCT visitid, an.units_sold, an.unit_price,  
		atpu.avg_tax_per_unit_sold_with_price,
		((an.units_sold*an.unit_price)+atpu.avg_tax_per_unit_sold_with_price) AS revenue
	FROM analytics AS an
	LEFT JOIN avg_tax_per_unit AS atpu
		USING(units_sold)
	WHERE units_sold IS NOT NULL AND revenue IS NULL
	AND an.unit_price = atpu.unit_price
	ORDER BY an.units_sold, an.unit_price
	)
-- Now the missing revenue values have an approximate revenue value added if they are NULL.
-- The CTE visitid_missing_revenue is joined to fill in the missing revenue values in analytics 
-- using the revenue values calculated in the CTE.
SELECT an.visitid, an.units_sold, an.unit_price, an.revenue,
	CASE
		WHEN an.units_sold IS NULL
			THEN NULL
		WHEN an.revenue IS NULL
			THEN vmr.revenue
		ELSE an.revenue
	END AS missing_revenue
FROM analytics AS an
JOIN visitid_missing_revenue AS vmr
	USING(visitid)
WHERE an.units_sold IS NOT NULL 
AND an.revenue IS NULL 
AND an.unit_price = vmr.unit_price
AND an.units_sold = vmr.units_sold
ORDER BY visitid;

Answer:  

Now 39977 distinct rows have filled in missing revenue values in the analytics table.
These values should only be used for an approximation of the data and not replace missing NULL values
in the revenue column in the analytics table.



Question 2: Answer questions 1 and 5 again from starting_with_questions but this time use the approximate
missing revenue values calculated in starting_with_data question 1.


SQL Queries:

-- There are NO locations where revenue is not null and units_sold is null.
-- Using the locations with units_sold and revenue, find the average tax that would be placed one revenue.
-- Then use the average tax generated per units sold and unit price to approximate the revenue gained when the value is NULL.
WITH id_rev_tax AS (
	SELECT visitid, revenue, unit_price, 
		units_sold, 
		(revenue - (unit_price*units_sold)) AS tax,
		((revenue - (unit_price*units_sold))/(unit_price*units_sold))*100 AS percent_tax
	FROM new_analytics
	WHERE units_sold IS NOT NULL AND revenue IS NOT NULL
	AND unit_price*units_sold > 0
	ORDER BY units_sold, unit_price
	),
avg_tax_per_unit AS (
	SELECT DISTINCT
		units_sold, unit_price, 
		AVG(tax) OVER (PARTITION BY units_sold) AS avg_tax_per_units_sold,
		AVG(tax) OVER (PARTITION BY units_sold, unit_price) AS avg_tax_per_unit_sold_with_price
	FROM id_rev_tax
	ORDER BY units_sold, unit_price
	),
-- SELECT *
-- FROM avg_tax_per_unit
-- ORDER BY units_sold, unit_price;

-- This CTE now finds an approximation for the revenue gained using the avg_tax_per_unit_sold_with_price.
-- This is now a revenue value to fill is the sections in the analytics tabel where it is NULL.
visitid_missing_revenue AS (
	SELECT visitid, an.units_sold, an.unit_price,  
		atpu.avg_tax_per_unit_sold_with_price,
		((an.units_sold*an.unit_price)+atpu.avg_tax_per_unit_sold_with_price) AS revenue
	FROM new_analytics AS an
	JOIN avg_tax_per_unit AS atpu
	USING(units_sold)
	WHERE units_sold IS NOT NULL AND revenue IS NULL
	AND an.unit_price = atpu.unit_price
	ORDER BY an.units_sold, an.unit_price
	),
-- SELECT *
-- FROM visitid_missing_revenue
-- ORDER BY revenue DESC;


-- Now missing revenue values have an approximate value added.
analytics_apprixmate_revenue_values AS (
	SELECT DISTINCT an.visitid, an.fullvisitorid, an.units_sold, an.unit_price, 
		an.revenue,
		CASE
			WHEN an.units_sold IS NULL
				THEN NULL
			WHEN an.revenue IS NULL
				THEN vmr.revenue
			ELSE an.revenue
		END AS missing_revenue
	FROM new_analytics AS an
	LEFT JOIN visitid_missing_revenue AS vmr
		USING(visitid)
	WHERE an.units_sold IS NOT NULL 
	AND an.unit_price = vmr.unit_price
	AND an.units_sold = vmr.units_sold
	),
-- SELECT *
-- FROM analytics_apprixmate_revenue_values;

-- Make a CTE to assign a country and city to fullvisitorid with visitid
fullvisitorid_country AS (
	SELECT DISTINCT fullvisitorid, country, city, visitid, totaltransactionrevenue
	FROM all_sessions
	WHERE country is not null
	),

-- The CTE creates a column which defaults to the revenue of the analytics table, 
-- or totaltransactionrevenue in all_sessions if the analytics revenue values are NULL.
-- It also gives values when the country column is not NULL.
visit_country_city_revenue AS (
	SELECT 
		visitid, 
		CASE
			WHEN aarv.revenue IS NULL
				THEN aarv.missing_revenue
			WHEN aarv.missing_revenue IS NULL
				THEN fvc.totaltransactionrevenue
			ELSE aarv.revenue
		END AS visitid_revenue,
		fvc.country,fvc.city
	FROM fullvisitorid_country AS fvc
	FULL OUTER JOIN analytics_apprixmate_revenue_values AS aarv
		USING(visitid)
	),
-- SELECT DISTINCT *
-- FROM visit_country_city_revenue
-- WHERE country IS NOT NULL
-- AND visitid_revenue IS NOT NULL;
	
-- CTE to list the country and city, and to give the sum of revenue per country and city.
country_city_rev_sum AS (
	SELECT country, city,
		SUM(visitid_revenue) OVER (PARTITION BY country) AS country_revenue,
		SUM(visitid_revenue) OVER (PARTITION BY country, city) AS city_revenue,
		SUM(visitid_revenue) OVER () AS total_overall_revenue
	FROM visit_country_city_revenue AS vccr
	WHERE country IS NOT NULL
	ORDER BY country, city
	)

-- -- Find the percentage of revenue generated per country
-- SELECT DISTINCT country, country_revenue, (country_revenue/total_overall_revenue)*100 as percent_total_revenue
-- FROM country_city_rev_sum
-- WHERE country_revenue IS NOT NULL
-- ORDER BY country_revenue DESC;

-- This query finds the city with its country with the highest level of transaction revenue on the site,
-- and compares it as a percentage to the overall revenue generated.
SELECT DISTINCT country, city, city_revenue AS revenue, (city_revenue/total_overall_revenue)*100 as percent_total_revenue
FROM country_city_rev_sum
WHERE city_revenue IS NOT NULL
AND city IS NOT NULL
ORDER BY city_revenue DESC;


Answer:

Compared to questions 1 and 5 in starting_with_questions, now 99.44% of the revenue is going to countries which are
not listed and given a NULL category.
In question 1 and 5 there were a total of 5 countries recorded which did not contain NULL values, now with
approximating the revenue per transaction in the analytics table, it has increased to 14 countries.
These countries have even less percent of the revenue generated than compared to questions 1 and 5 because now 
there is more revenue going to countries without a category and labelled NULL.
The country with the highest transaction revenue is still the United States but instead of 205475.11 found in 
question 1 in starting_with_questions, the revenue is now 11362.12.  While the approximate tax is not exact in question 1
for starting_with_data, it may give a more accurate summery over how the revenue is distributed between countries.

Compared to question 1 and 5, there is now 32 cities recorded instead of 19.  Of the categories with cities and countries which
are not including missing values, the city with the most revenue generated is Mountain View, with 14.07% of the revenue.  Following
that is Sunnyvale with 13.94% of the revenue.  Unlike question 5 in starting_with_questions, San Francisco is now 4th instead of 
1st with 5.87% of the revenue generated.

It is important to note that even with an approximation to broaden the amount of countries and cities collected, there is still
a lot of missing data.  More records should be gathered to find 99.44% of the revenue going to other countries in order for there
to be a more accurate accounting going on in other cities.

Question 3: 

SQL Queries:



Answer:



Question 4: 

SQL Queries:

Answer:



Question 5: 

SQL Queries:

Answer:
