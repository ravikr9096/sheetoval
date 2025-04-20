import pandas as pd
import math
import xlwt


# Replace with your actual CSV file path
filename = 'example2.csv'

workbook = xlwt.Workbook()
sheet = workbook.add_sheet("Sheet1")

# Read the CSV file with two headers
df = pd.read_csv(filename, header=[0, 1])

# Initialize a list to store records
records = []
# Loop through each row
for idx, row in df.iterrows():

    # Get the first column's value (assuming it's the first column in df)
    first_col_value = row[df.columns[0]]
    second_col_value = row[df.columns[1]]
    
    # Traverse all columns and collect info
    for col in df.columns:
        h1, h2 = col
        cell_value = row[col]
        if not pd.isna(cell_value) and cell_value != first_col_value and cell_value != second_col_value and not h1.startswith('Unnamed') and not h2.startswith('Unnamed'):
            records.append([ first_col_value, second_col_value, h1, h2, cell_value])

# Optional: print all records
for record in records:
    print(record)

# Write data to sheet
for row_idx, row in enumerate(records):
    for col_idx, value in enumerate(row):
        sheet.write(row_idx, col_idx, value)

# Save the workbook
workbook.save("output_file.xls")
