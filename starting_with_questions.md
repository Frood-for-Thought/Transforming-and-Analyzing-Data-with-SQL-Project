Answer the following questions and provide the SQL queries used to find the answer.

    
**Question 1: Which cities and countries have the highest level of transaction revenues on the site?**


SQL Queries:

-- The CTE creates a column which defaults to the revenue of the analytics table, 
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

-- Come up with a list of order quantities corresponding to their sku.
-- The CTE includes the sales_by_sku table due to QA showing unique values that are
-- not in the products or sales_report table.
WITH sku_order_quan AS (
	SELECT DISTINCT
		CASE
			WHEN sr.total_ordered IS NULL AND pro.orderedquantity IS NULL
				THEN sbs.total_ordered
			WHEN sr.total_ordered IS NULL
				THEN pro.orderedquantity
			ELSE sbs.total_ordered
		END AS order_quantity,
		CASE
			WHEN pro.sku IS NULL AND sr.productsku IS NULL
				THEN sbs.productsku
			WHEN pro.sku IS NULL
				THEN sr.productsku
			ELSE pro.sku
		END AS productsku
	FROM sales_report as sr
	FULL OUTER JOIN products as pro
	ON pro.sku = sr.productsku
	FULL OUTER JOIN sales_by_sku as sbs
	ON pro.sku = sbs.productsku
	ORDER BY order_quantity DESC
	),
-- Join the previous CTE with all_sessions using the productsku.
country_city_order_quan AS (
	SELECT alls.visitid, productsku, soq.order_quantity, alls.country, alls.city
	FROM all_sessions AS alls
	JOIN sku_order_quan AS soq
	USING(productsku)
	),
-- Make a CTE that takes the order quantity from the analytics table and corresponds it with the visitid
-- Now the CTE has a total order_quantity corresponding to the visitid in analytics.
visitid_oq_analytics AS (
	SELECT DISTINCT visitid, 
		SUM(units_sold) OVER (PARTITION BY visitid) AS order_quantity
	FROM analytics
	WHERE units_sold IS NOT NULL
	),
-- A CTE to describe the order quantity per country and city, and when the quantity is zero,
-- the visitid_oq_analytics table is used to fill in the missing values.
country_city_order_quantity_with_analytics AS (
	SELECT country, city,
		CASE
			WHEN ccoq.order_quantity = 0
				THEN voa.order_quantity
			ELSE ccoq.order_quantity
		END AS order_quantity
	FROM country_city_order_quan AS ccoq
	JOIN visitid_oq_analytics AS voa
	USING(visitid)
	)

SELECT country, city,
	SUM(order_quantity) OVER (PARTITION BY country) AS country_order_quantity,
	SUM(order_quantity) OVER (PARTITION BY city) AS city_order_quantity
FROM country_city_order_quantity_with_analytics
-- -- The following finds the country with the highest order quantity.
-- ORDER BY country_order_quantity DESC
-- LIMIT 1;
-- -- The following finds the city with the highest order quantity.
-- WHERE city IS NOT NULL
-- ORDER BY city_order_quantity DESC;

Answer:
The country with the highest order quantity is the United States with 5840.
The city with the highest order quantity is Dallas with 1148, (not including NULL).




**Question 3: Is there any pattern in the types (product categories) of products ordered from visitors in each city and country?**


SQL Queries:

SELECT DISTINCT v2productcategory
FROM all_sessions
WHERE LOWER(v2productcategory) LIKE '%waze%';
-- This CTE first groups up the products into the following categories:
-- Accessories, Apparel, Bags, Bottle, Drinkware, Electronics, Fun, Games, Gift Cards, Kids, 
-- Lifestyle, Limited Supply, Nest, Office, Sale, and Waze.
WITH product_name_cat_list AS (
	SELECT
		v2productname,
		CASE
			WHEN LOWER(v2productcategory) LIKE '%waze%'
				THEN 'Waze'
			WHEN LOWER(v2productcategory) LIKE '%sale%'
				THEN 'Sale'
			WHEN LOWER(v2productcategory) LIKE '%nest%'
				THEN 'Nest'
			WHEN LOWER(v2productcategory) LIKE '%game%'
				THEN 'Games'
			WHEN LOWER(v2productcategory) LIKE '%accessories%'
				THEN 'Accessories'
			WHEN LOWER(v2productcategory) LIKE '%apparel%' 
			OR LOWER(v2productcategory) LIKE '%shirt%'
				THEN 'Apparel'
			WHEN LOWER(v2productcategory) LIKE '%bags%'
				THEN 'Bags'
			WHEN LOWER(v2productcategory) LIKE '%electronics%'
				THEN 'Electronics'
			WHEN LOWER(v2productcategory) LIKE '%office%'
				THEN 'Office'
			WHEN LOWER(v2productcategory) LIKE '%drinkware%'
				THEN 'Drinkware'
			WHEN LOWER(v2productcategory) LIKE '%fun%'
				THEN 'Fun'
			WHEN LOWER(v2productcategory) LIKE '%kid%'
				THEN 'Kids'
			WHEN LOWER(v2productcategory) LIKE '%lifestyle%'
				THEN 'Lifestyle'
			WHEN LOWER(v2productcategory) LIKE '%gift cards%'
				THEN 'Gift Cards'
			WHEN LOWER(v2productcategory) LIKE '%limited supply%'
				THEN 'Limited Supply'
			ELSE v2productcategory
		END AS product_category
	FROM all_sessions
	),
-- -- This query shows there is no v2productname without a product_category.
-- SELECT *
-- FROM product_name_cat_list
-- WHERE v2productname IS NULL;

-- Update the product_name_cat_list using the v2productname, 
-- this CTE makes sure that every v2productname is assigned a product_category,
-- based on the description of the product.
update_product_name_cat_list AS (
	SELECT v2productname,
		CASE
			WHEN LOWER(v2productname) LIKE '%waze%'
				THEN 'Waze'
			WHEN LOWER(v2productname) LIKE '%bag%'
			OR LOWER(v2productname) LIKE '%backpack%'
			OR LOWER(v2productname) LIKE '%pouch%'
			OR LOWER(v2productname) LIKE '%sack%'
			OR LOWER(v2productname) LIKE '%duffel%'
				THEN 'Bags'
			WHEN LOWER(v2productname) LIKE '%sticky pad%'
			OR LOWER(v2productname) LIKE '%note%'
			OR LOWER(v2productname) LIKE '%pen%'
			OR LOWER(v2productname) LIKE '%journal%'
			OR LOWER(v2productname) LIKE '%keyboard dot sticker%'
			OR LOWER(v2productname) LIKE '%screen cleaning%'
				THEN 'Office'
			WHEN LOWER(v2productname) LIKE '%case%'
			OR LOWER(v2productname) LIKE '%decal%'
			OR LOWER(v2productname) LIKE '%sticker%'
			OR LOWER(v2productname) LIKE '%stand%'
			OR LOWER(v2productname) LIKE '%tag%'
			OR LOWER(v2productname) LIKE '%umbrella%'
				THEN 'Accessories'
			WHEN LOWER(v2productname) LIKE '%hood%' 
			OR LOWER(v2productname) LIKE '%vest%' 
			OR LOWER(v2productname) LIKE '%hoodie%'
			OR LOWER(v2productname) LIKE '%sleeve%'
			OR LOWER(v2productname) LIKE '%cap%'
			OR LOWER(v2productname) LIKE '%onesie%'
			OR LOWER(v2productname) LIKE '%hat'
			OR LOWER(v2productname) LIKE '%men%'
			OR LOWER(v2productname) LIKE '%women%'
			OR LOWER(v2productname) LIKE '%glasses%'
			OR LOWER(v2productname) LIKE '%hat%'
				THEN 'Apparel'
			WHEN LOWER(v2productname) LIKE '%bottle%'
				THEN 'Bottle'
			WHEN LOWER(v2productname) LIKE '%mug%'
			OR LOWER(v2productname) LIKE '%tumbler%'
			OR LOWER(v2productname) LIKE '%screen cleaning%'
				THEN 'Drinkware'
			WHEN LOWER(v2productname) LIKE '%baby%'
			OR LOWER(v2productname) LIKE '%bib%'
			OR LOWER(v2productname) LIKE '%toddler%'
				THEN 'Kids'
			WHEN LOWER(v2productname) LIKE '%ball%'
				THEN 'Fun'
			WHEN LOWER(v2productname) LIKE '%android%' 
			OR LOWER(v2productname) LIKE '%flashlight%'
			OR LOWER(v2productname) LIKE '%mouse%'
			OR LOWER(v2productname) LIKE '%flashlight%'
			OR LOWER(v2productname) LIKE '%charger%'
			OR LOWER(v2productname) LIKE '%power%'
			OR LOWER(v2productname) LIKE '%bluetooth%'
			OR LOWER(v2productname) LIKE '%phone%'
			OR LOWER(v2productname) LIKE '%speaker%'
				THEN 'Electronics'
			WHEN LOWER(v2productname) LIKE '%yoga%'
			OR LOWER(v2productname) LIKE '%balm%'
			OR LOWER(v2productname) LIKE '%dog toy%'
			OR LOWER(v2productname) LIKE '%sanitizer%'
			OR LOWER(v2productname) LIKE '%pet%'
				THEN 'Lifestyle'
			WHEN LOWER(v2productname) LIKE '%nest%'
				THEN 'Nest'
			WHEN LOWER(v2productname) LIKE '%gift card%'
				THEN 'Gift Cards'
			ELSE product_category
		END AS product_category
	FROM product_name_cat_list
	),
	
-- -- Now every v2productname has a product_category and all product_categories are grouped together.
-- SELECT *
-- FROM update_product_name_cat_list;

-- -- The CTE groups and orders the times a product category was ordered with each country.
-- -- It also ranks the category of purchase based on the total amount of times the category is selected.
-- country_cat_num AS (
-- 	SELECT DISTINCT alls.country, upncl.product_category,
-- 		COUNT(upncl.product_category) 
-- 			OVER (PARTITION BY alls.country ORDER BY upncl.product_category) AS product_num_per_country,
-- 		DENSE_RANK() OVER (PARTITION BY alls.country ORDER BY upncl.product_category DESC) AS cat_rank_per_country
-- 	FROM all_sessions AS alls
-- 	JOIN update_product_name_cat_list AS upncl
-- 	USING(v2productname)
-- 	ORDER BY country
-- 	)
-- -- This query takes the CTE above to show the number one category for each country.
-- SELECT DISTINCT	country, product_category, product_num_per_country
-- FROM country_cat_num
-- WHERE cat_rank_per_country = 1
-- ORDER BY product_num_per_country;

-- -- This query takes the CTE above to show how many times each category appears for all the countries.
-- SELECT DISTINCT	product_category, COUNT(country)
-- FROM country_cat_num
-- WHERE cat_rank_per_country = 1
-- GROUP BY product_category;


--  The CTE groups and orders the times a product category was ordered with each city.
city_product_cat AS (
	SELECT DISTINCT alls.city, upncl.product_category,
		COUNT(upncl.product_category) 
			OVER (PARTITION BY alls.city ORDER BY upncl.product_category) AS product_num_per_city,
		DENSE_RANK() OVER (PARTITION BY alls.country ORDER BY upncl.product_category DESC) AS cat_rank_per_city
	FROM all_sessions AS alls
	JOIN update_product_name_cat_list AS upncl
	USING(v2productname)
	WHERE alls.city IS NOT NULL
	)
-- This lists the most popular category in each city.
SELECT product_category, COUNT(city)
FROM city_product_cat
WHERE cat_rank_per_city = 1
GROUP BY product_category;

Answer:

The most times a product category was ordered was in the united states and was a Waze category with it being the most purchased at 653414 times, 
followed by the Sale category at 652082 times.  The country with the least times a product category was ordered was Malta with Apparel being 
ordered 5 times.  The most popular category in the first 7 countries was Waze, however, Office appeared 64 times over all the countries,
while Wase only appeared 31 times.

The most times a product category was ordered in a city was in Mountain View, (not including NULL in the answer), with the category being Sale,
and the number of times it was purchased being 73671.  Like in the country table, Office appeared the most, (39 times), while
Waze was second, appearing 29 times.




**Question 4: What is the top-selling product from each city/country? Can we find any pattern worthy of noting in the products sold?**


SQL Queries:



Answer:





**Question 5: Can we summarize the impact of revenue generated from each city/country?**

SQL Queries:



Answer:







