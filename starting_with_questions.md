# Answer the following questions and provide the SQL queries used to find the answer.

## Question 1: Which cities and countries have the highest level of transaction revenues on the site?

### SQL Queries:

```
-- The CTE creates a column which defaults to the revenue of the analytics table, 
-- or totaltransactionrevenue in all_sessions if the analytics value is NULL.
-- It also gives values when the country column is not NULL.
WITH visit_country_city_revenue AS (
	SELECT 
		visitid, 
		CASE
			WHEN an.revenue IS NULL
				THEN alls.totaltransactionrevenue
			ELSE alls.totaltransactionrevenue
		END AS visitid_revenue,
		alls.country, alls.city
	FROM all_sessions AS alls
	FULL OUTER JOIN analytics AS an
		USING(visitid)
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
```

## Answer:

The country with the highest transaction revenue is the United States with 250813.56.
The city with the highest transaction revenue is San Francisco, United States, with 1564.32, (not counting NULL as a city).

## Question 2: What is the average number of products ordered from visitors in each city and country?

### SQL Queries:

```
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
	AVG(order_quantity) OVER (PARTITION BY country) AS country_order_quantity,
	AVG(order_quantity) OVER (PARTITION BY city) AS city_order_quantity
FROM country_city_order_quantity_with_analytics
-- -- The following finds the country with the highest order quantity.
-- ORDER BY country_order_quantity DESC
-- LIMIT 1;
-- -- The following finds the city with the highest order quantity.
-- WHERE city IS NOT NULL
-- ORDER BY city_order_quantity DESC;
```

### Answer:
Including orders from the sales_by_sku and all_sessions, even analytics in case of NULL values, the country with the highest average order quantity is Vietnam, while the city with the highest order quantity is Dallas.

The country with the highest order quantity is the United States with 5840. The city with the highest order quantity is Dallas with 1148, (not including NULL), followed by Dublin Ireland.

## Question 3: Is there any pattern in the types (product categories) of products ordered from visitors in each city and country?

### SQL Queries:

```
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
			WHEN LOWER(v2productcategory) LIKE '%sale%'
				THEN 'Sale'
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
```

```
-- Update the product_name_cat_list using the v2productname, 
-- this CTE makes sure that every v2productname is assigned a product_category,
-- based on the description of the product.
update_product_name_cat_list AS (
	SELECT v2productname,
		CASE
		
--	This orders the products by sponsored names
-- 		WHEN LOWER(v2productname) LIKE '%waze%'
-- 			THEN 'Waze'
-- 		WHEN LOWER(v2productname) LIKE '%google%'
-- 			THEN 'Google'
-- 		WHEN LOWER(v2productname) LIKE '%nest%'
-- 			THEN 'Nest'
-- 		WHEN LOWER(v2productname) LIKE '%youtube%'
-- 		OR LOWER(v2productname) LIKE '%you tube%'
-- 			THEN 'YouTube'
-- 		WHEN LOWER(v2productname) LIKE '%android%'
-- 			THEN 'Android'
-- 		WHEN LOWER(v2productname) LIKE '%galaxy%'
-- 			THEN 'Galaxy'

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
				THEN 'Apparel'
			WHEN LOWER(v2productname) LIKE '%bottle%'
				THEN 'Bottle'
			WHEN LOWER(v2productname) LIKE '%mug%'
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
			WHEN LOWER(v2productname) LIKE '%gift card%'
				THEN 'Gift Cards'
			ELSE product_category
		END AS product_category
	FROM product_name_cat_list
	),
	
-- -- Now every v2productname has a product_category and all product_categories are grouped together.
-- SELECT *
-- FROM update_product_name_cat_list;
```

```
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
```

```
-- -- This query takes the CTE above to show how many times each category appears for all the countries.
-- SELECT DISTINCT	product_category, COUNT(country)
-- FROM country_cat_num
-- WHERE cat_rank_per_country = 1
-- GROUP BY product_category;
```

```
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
```

### Answer:

The most times a product category was ordered was in the united states and was a YouTube category with it being the most purchased at 653414 times, followed by the Waze category at 451542 times.  The country with the least times a product category was ordered was Slovakia with Android being ordered 1 time.  The most popular category for all the counties was YouTube, appearing on the top of the list for 114 countries, and
Google coming in second at 12 countries.

The most times a product category was ordered in a city was in Mountain View, (not including NULL in the answer), with the category being YouTube, and the number of times it was purchased being 73671.  Waze was second, with 62140, even though it doesn't appear first in any cities. When dealing with sponsored product categories, Youtube showed up the most with it being the most popular category in 132 cities, followed by Google with 16.

Without taking sponsored brand names, the catagory that was most popular was Office supplies.

## Question 4: What is the top-selling product from each city/country? Can we find any pattern worthy of noting in the products sold?

### SQL Queries:

```
-- All_sessions contains more product name details per productsku than products.
SELECT COUNT(DISTINCT productsku), COUNT(DISTINCT v2productname)
FROM all_sessions;
SELECT COUNT(DISTINCT sku), COUNT(DISTINCT name)
FROM products;
```

```
-- Merge all the product names from products and all_sessions
WITH product_sku_names_cat_list AS (
	SELECT 
		CASE
			WHEN alls.productsku IS NULL
				THEN pro.sku
			WHEN pro.sku IS NULL AND alls.productsku IS NULL
				THEN NULL
			ELSE alls.productsku
		END AS productsku,
		CASE
			WHEN alls.productsku IS NOT NULL
				THEN alls.v2productname
			WHEN pro.sku IS NOT NULL
				THEN pro.name
			ELSE alls.v2productname
		END AS v2productname, 
		alls.v2productcategory
	FROM all_sessions AS alls
	FULL OUTER JOIN products AS pro
		ON alls.productsku = pro.sku
	),

-- filter out productnames, either by brand or type of product.
WITH product_name_list AS (
	SELECT v2productname,
	CASE
--	This orders the products by sponsored names
-- 		WHEN LOWER(v2productname) LIKE '%waze%'
-- 			THEN 'Waze'
-- 		WHEN LOWER(v2productname) LIKE '%google%'
-- 			THEN 'Google'
-- 		WHEN LOWER(v2productname) LIKE '%nest%'
-- 			THEN 'Nest'
-- 		WHEN LOWER(v2productname) LIKE '%youtube%'
-- 		OR LOWER(v2productname) LIKE '%you tube%'
-- 			THEN 'YouTube'
-- 		WHEN LOWER(v2productname) LIKE '%android%'
-- 			THEN 'Android'
-- 		WHEN LOWER(v2productname) LIKE '%galaxy%'
-- 			THEN 'Galaxy'
		
		WHEN LOWER(v2productname) LIKE '%bag%'
		OR LOWER(v2productname) LIKE '%pack%'
		OR LOWER(v2productname) LIKE '%backpack%'
		OR LOWER(v2productname) LIKE '%pouch%'
		OR LOWER(v2productname) LIKE '%sack%'
		OR LOWER(v2productname) LIKE '%duffel%'
		OR LOWER(v2productname) LIKE '%tote%'
			THEN 'Bag'
		WHEN LOWER(v2productname) LIKE '%pen%'
			THEN 'Pen'
		WHEN LOWER(v2productname) LIKE '%journal%'
			THEN 'Journal'
		WHEN LOWER(v2productname) LIKE '%umbrella%'
			THEN 'Umbrella'
		WHEN LOWER(v2productname) LIKE '%hood%'
		OR LOWER(v2productname) LIKE '%vest%' 
		OR LOWER(v2productname) LIKE '%hoodie%'
		OR LOWER(v2productname) LIKE '%sleeve%'
		OR LOWER(v2productname) LIKE '%onesie%'
		OR LOWER(v2productname) LIKE '%sweatshirt%'
		OR LOWER(v2productname) LIKE '%pullover%'
			THEN 'Sweater'
		WHEN LOWER(v2productname) LIKE '%shirt%'
		OR LOWER(v2productname) LIKE '%tee%'
		OR LOWER(v2productname) LIKE '%polo%'
		OR LOWER(v2productname) LIKE '%tank%'
		OR LOWER(v2productname) LIKE '%henley%'
			THEN 'Shirt'
		WHEN LOWER(v2productname) LIKE '%jacket%'
			THEN 'Jacket'
		WHEN LOWER(v2productname) LIKE '%hat%'
		OR LOWER(v2productname) LIKE '%cap%'
			THEN 'Hat'
		WHEN LOWER(v2productname) LIKE '%glasses%'
			THEN 'Glasses'
		WHEN LOWER(v2productname) LIKE '%bottle%'
		OR LOWER(v2productname) LIKE '%mug%'
		OR LOWER(v2productname) LIKE '%cold tumbler%'
			THEN 'Bottle or Mug'
		WHEN LOWER(v2productname) LIKE '%flashlight%'
			THEN 'Flashlight'
		WHEN LOWER(v2productname) LIKE '%mouse%'
			THEN 'Mouse'
		WHEN LOWER(v2productname) LIKE '%charger%'
			THEN 'Charger'
		WHEN LOWER(v2productname) LIKE '%phone%'
			THEN 'Phone'
		WHEN LOWER(v2productname) LIKE '%speaker%'
			THEN 'Speaker'
		WHEN LOWER(v2productname) LIKE '%yoga%'
			THEN 'Yoga Supplies'
		WHEN LOWER(v2productname) LIKE '%dog toy%'
		OR LOWER(v2productname) LIKE '%pet%'
		OR LOWER(V2productname) LIKE '%dog%'
			THEN 'Pet Supplies'
		WHEN LOWER(v2productname) LIKE '%sanitizer%'
			THEN 'Sanitizer'
		WHEN LOWER(v2productname) LIKE '%gift card%'
			THEN 'Gift Cards'
		WHEN LOWER(v2productname) LIKE '%earbuds%'
		OR LOWER(v2productname) LIKE '%earbud%'
			THEN 'Headphones'
		WHEN LOWER(v2productname) LIKE '%camera%'
			THEN 'Camera'
		WHEN LOWER(v2productname) LIKE '%alarm%'
			THEN 'Alarm'
		WHEN LOWER(v2productname) LIKE '%decal%'
		OR LOWER(v2productname) LIKE '%sticker%'
			THEN 'Decal'
		WHEN LOWER(v2productname) LIKE '%socks%'
			THEN 'Socks'
		WHEN LOWER(v2productname) LIKE '%bib%'
			THEN 'Baby Accessories'
		WHEN LOWER(v2productname) LIKE '%notebook%'
			THEN 'Notebook'
		WHEN LOWER(v2productname) LIKE '%luggage tag%'
			THEN 'Luggage Tag'
		WHEN LOWER(v2productname) LIKE '%lunch%'
			THEN 'Lunch Box'
		WHEN LOWER(v2productname) LIKE '%cleaning cloth%'
			THEN 'Cleaning Cloth'
		WHEN LOWER(v2productname) LIKE '%power bank%'
			THEN 'Power Bank'
		WHEN LOWER(v2productname) LIKE '%device holder%'
		OR LOWER(v2productname) LIKE '%device stand%'
			THEN 'Device Stand'
		WHEN v2productname LIKE '%Learning Thermostat 3rd Gen-USA - Copper'
			THEN 'Learning Thermostat 3rd Gen-USA - Copper'
		WHEN v2productname LIKE '%Learning Thermostat 3rd Gen-USA - White'
			THEN 'Learning Thermostat 3rd Gen-USA - White'
		WHEN v2productname LIKE '%Learning Thermostat 3rd Gen-USA%'
			THEN 'Learning Thermostat 3rd Gen-USA'
		WHEN LOWER(v2productname) LIKE '%lip balm%'
			THEN 'Lip Balm'
	ELSE v2productname
	END AS products
	FROM all_sessions
	),
-- SELECT DISTINCT *
-- FROM product_name_list;
```

```
-- CTE to count the products sold per country and list them with a ranking
country_pro_num_rank AS(
	SELECT DISTINCT alls.country, pnl.products,
		COUNT(pnl.products) 
			OVER (PARTITION BY alls.country ORDER BY pnl.products) AS product_num_per_country,
		DENSE_RANK() OVER (PARTITION BY alls.country ORDER BY pnl.products DESC) AS pro_rank_per_country
	FROM all_sessions AS alls
	JOIN product_name_list AS pnl
	USING(v2productname)
	WHERE pnl.products IS NOT NULL
	ORDER BY product_num_per_country DESC
	)

SELECT DISTINCT products, COUNT(country)
FROM country_pro_num_rank
WHERE pro_rank_per_country = 1
GROUP BY products;
```

```
-- --  The CTE groups and orders the times a product was ordered with each city.
-- city_product AS (
-- 	SELECT DISTINCT alls.city, pnl.products,
-- 		COUNT(pnl.products) 
-- 			OVER (PARTITION BY alls.city ORDER BY pnl.products) AS product_num_per_city,
-- 		DENSE_RANK() OVER (PARTITION BY alls.country ORDER BY pnl.products DESC) AS pro_rank_per_city
-- 	FROM all_sessions AS alls
-- 	JOIN product_name_list AS pnl
-- 	USING(v2productname)
-- 	WHERE alls.city IS NOT NULL
-- 	)
-- -- SELECT *
-- -- FROM city_product
-- -- ORDER BY product_num_per_city DESC;

-- -- This lists the most popular category in each city.
-- SELECT products, COUNT(city)
-- FROM city_product
-- WHERE pro_rank_per_city = 1
-- GROUP BY products;
```

### Answer:

The most popular product sold overall are 'Yoga Supplies' being ordered 589784 in the United States.  The next popular supplies after that were umbrellas, being sold 588886 times.  

However, sweater products were the most popular in 73 countries while yoga supplies were the second most popular, being 16 countries.
  
When not ordering the products sold by editing and grouping the original names, the most popular item was  YouTube Wool Heather Cap Heather/Black being the most popular in 30 countries.  This is followed with YouTube Youth Short Sleeve Tee Red, and YouTube Twill Cap being the most popular in 17 countries.  When not grouping the names of the orders sold, the most popular item sold per country was YouTube Youth Short Sleeve Tee Red with it being 653414 times sold in the United States.

Sweaters were the most popular in the most cities with 68 cities, while Yoga Supplies came second, being the most popular in 13 cities. Like with countries, Yoga Supplies were the most ordered with 73902 in Mountain View.

## Question 5: Can we summarize the impact of revenue generated from each city/country?

### SQL Queries:

```
-- The CTE creates a column which defaults to the revenue of the analytics table, 
-- or totaltransactionrevenue in all_sessions if the analytics value is NULL.
-- It also gives values when the country column is not NULL.
WITH visit_country_city_revenue AS (
	SELECT 
		visitid, 
		CASE
			WHEN an.revenue IS NULL
				THEN alls.totaltransactionrevenue
			ELSE alls.totaltransactionrevenue
		END AS visitid_revenue,
		alls.country, alls.city
	FROM all_sessions AS alls
	FULL OUTER JOIN analytics AS an
		USING(visitid)
	WHERE alls.country IS NOT NULL
	),

-- CTE to list the country and city, and to give the sum of revenue per country and city.
country_city_rev_sum AS (
	SELECT country, city,
		SUM(visitid_revenue) OVER (PARTITION BY country) AS country_revenue,
		SUM(visitid_revenue) OVER (PARTITION BY country, city) AS city_revenue,
		SUM(visitid_revenue) OVER () AS total_overall_revenue
	FROM visit_country_city_revenue AS vccr
	-- option to filter out null coutries or cities
	WHERE country IS NOT NULL
-- 	AND city IS NOT NULL
	ORDER BY country, city
	)

-- -- Find the percentage of revenue generated per country
-- SELECT DISTINCT country, country_revenue, (country_revenue/total_overall_revenue)*100 as percent_total_revenue
-- FROM country_city_rev_sum
-- WHERE country_revenue IS NOT NULL
-- ORDER BY country_revenue DESC;
```

```
-- This query finds the city with its country with the highest level of transaction revenue on the site,
-- and compares it as a percentage to the overall revenue generated.
SELECT DISTINCT country, city, city_revenue AS revenue, (city_revenue/total_overall_revenue)*100 as percent_total_revenue
FROM country_city_rev_sum
WHERE city_revenue IS NOT NULL
ORDER BY city_revenue DESC;
```

### Answer:

From the records which takes into account countries which are not null, it appears United States has 13098.16 of total revenue generated. This accounts for 92.52% of all the revenue generated per country.  The next is Israel with 4.25%, then Australia with 2.53%.

The city with the most revenue generated is San Francisco, United States, with 1564.32 which is 11.05% of the total revenue, (in this case the total revenue from all the non-NULL countries, which includes unrecorded cities with NULL).  
The next city being Sunnyvale, with 992.23 generated, and it being 7.01% of the revenue generated, followed by Atlanta with 854.44 and 6.04% revenue generated.  
The three lowest were Zurich, Switzerland, with 0.096%, Columbus, United States, with 0.125%, and Houston, United States, with 0.221%.  There was a total of 19 cities recorded which generated revenue.
