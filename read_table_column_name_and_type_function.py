import pandas as pd
import numpy as np


def read_csv_or_excel(file_name, suffix):
    if suffix.lower() == 'c':
        dataframe = pd.read_csv(f"{file_name}.csv")
        pd.set_option('display.max_columns', None)  # Show all the columns
        return dataframe.dtypes
    elif suffix.lower() == 'x':
        dataframe = pd.read_excel(f"{file_name}.xlsx")
        pd.set_option('display.max_columns', None)  # Show all the columns
        return dataframe.dtypes
    else:
        print("cannot read file")

file_name = input("input the exact file name to read: ")
suffix = input("Type 'c' for .csv file or 'x' for excel .xlsx: ")
print(read_csv_or_excel(file_name, suffix))