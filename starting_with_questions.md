Answer the following questions and provide the SQL queries used to find the answer.

    
**Question 1: Which cities and countries have the highest level of transaction revenues on the site?**


SQL Queries:

-- The CTE creates a column which defaults to the visit revenue of the analytics table, 
-- or totaltransactionrevenue in all_sessions if the analytics value is NULL.
-- It also gives values when the country column is not NULL.
WITH visit_country_city_revenue AS (
	SELECT 
		visitid, 
		CASE
			WHEN an.revenue IS NULL
				THEN alls.totaltransactionrevenue
			ELSE an.revenue
		END AS visitid_revenue,
		alls.country, alls.city
	FROM all_sessions AS alls
	FULL OUTER JOIN analytics AS an
		USING(visitid)
	WHERE alls.country IS NOT NULL
	),
-- CTE to list the country and city, and to give the sum of revenue per country and city.
country_city_rev_sum AS (
	SELECT DISTINCT country, city,
		SUM(visitid_revenue) OVER (PARTITION BY country) AS country_revenue,
		SUM(visitid_revenue) OVER (PARTITION BY country, city) AS city_revenue
	FROM visit_country_city_revenue AS vccr
	WHERE city is not null
	ORDER BY country, city
	)
-- -- This query finds the country with the highest level of transaction revenue on the site.
-- SELECT DISTINCT country, country_revenue AS revenue
-- FROM country_city_rev_sum
-- WHERE country_revenue IS NOT NULL
-- ORDER BY country_revenue DESC
-- LIMIT 1;

-- -- This query finds the city with the country it's in with the highest level of transaction revenue on the site.
-- SELECT DISTINCT country, city, city_revenue AS revenue
-- FROM country_city_rev_sum
-- WHERE city_revenue IS NOT NULL
-- ORDER BY city_revenue DESC
-- LIMIT 1;

Answer:
The country with the highest transaction revenue is the United States with 205475.11.
The city with the highest transaction revenue is Sunnyvale, United States, with 155620.72.



**Question 2: What is the average number of products ordered from visitors in each city and country?**


SQL Queries:



Answer:





**Question 3: Is there any pattern in the types (product categories) of products ordered from visitors in each city and country?**


SQL Queries:



Answer:





**Question 4: What is the top-selling product from each city/country? Can we find any pattern worthy of noting in the products sold?**


SQL Queries:



Answer:





**Question 5: Can we summarize the impact of revenue generated from each city/country?**

SQL Queries:



Answer:







