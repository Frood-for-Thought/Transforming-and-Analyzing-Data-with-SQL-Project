What are your risk areas? Identify and describe them.



QA Process:
Describe your QA process and include the SQL queries used to execute it.

- When importing data, in order for the process to succeed, all columns with characters needed to have appropriate lengths.
	- The pageTitle column in the all_sessions table needed to be extended to 600 characters in order to import the data,
	needed to find area where pageTitle > 500 characters.
- Column titles needed to be converted to lowercase for easier usage and so the queries tool can recognize the titles typed out after SELECT.
