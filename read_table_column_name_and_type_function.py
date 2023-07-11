import pandas as pd
import numpy as np

# This program reads files to identify their column parameters as long as the files are in the same folder.


def read_csv_or_excel(file_name, suffix):
    """
    This function imports the file contents into a DataFrame and then displays column types and data inside.
    :param file_name: title of the file to read
    :param suffix: should be either "c" or "x" to check if .csv or .xlsx
    :return: displays the types of data for each column name: dataframe.dtypes
             displays the first 5 rows to see the type of data: dataframe.head()
    """
    if suffix.lower() == 'c':
        dataframe = pd.read_csv(f"{file_name}.csv", nrows=20)
        pd.set_option('display.max_columns', None)  # Show all the columns
        return dataframe.dtypes, dataframe.head()
    elif suffix.lower() == 'x':
        dataframe = pd.read_excel(f"{file_name}.xlsx")
        pd.set_option('display.max_columns', None)  # Show all the columns
        return dataframe.dtypes, dataframe.head()
    else:
        print("cannot read file")

# Input the file name and extension (suffix) display the results described in the function "read_csv_or_excel"
file_name = input("input the exact file name to read: ")
suffix = input("Type 'c' for .csv file or 'x' for excel .xlsx: ")

# Get a series list with the column names and data types (file_df_dtypes),
# and a sample of the first 5 rows for the table, (file_df_head)
file_df_dtypes, file_df_head = read_csv_or_excel(file_name, suffix)
column_list = list(file_df_dtypes.index)

print(f"\nTable First 5 Rows:\n{file_df_head}")  # Print off a sample of the table's first 5 rows

print(f"\nColumn Names and Their Datatypes:\n{file_df_dtypes}")  # Print off a list of the column names and their datatypes

print("\nColumn Names in Lowercase:")
for i, j in enumerate(column_list):
    print(j.lower())  # Print off a list of all the column names in lowercase.
