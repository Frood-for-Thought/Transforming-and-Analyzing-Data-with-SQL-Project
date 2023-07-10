Question 1:  Using the locations with units_sold and revenue, find the average tax that would be placed one revenue.
Then use the average tax generated per units sold and unit price to approximate the revenue gained when the value is NULL.

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
	SELECT visitid, an.units_sold, an.unit_price,  
		atpu.avg_tax_per_unit_sold_with_price,
		((an.units_sold*an.unit_price)+atpu.avg_tax_per_unit_sold_with_price) AS revenue
	FROM analytics AS an
	JOIN avg_tax_per_unit AS atpu
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

Now 231540 distinct rows have filled in missing revenue values in the analytics table.
These values should only be used for an approximation of the data and not replace missing NULL values
in the revenue column in the analytics table.

Question 2: 

SQL Queries:

Answer:



Question 3: 

SQL Queries:

Answer:



Question 4: 

SQL Queries:

Answer:



Question 5: 

SQL Queries:

Answer:
