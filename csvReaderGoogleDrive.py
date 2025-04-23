from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pandas as pd
import xlwt
import csv


# Path to your service account credentials file
SERVICE_ACCOUNT_FILE = 'first-project-457714-60fa3e8514a5.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive.file']

START_ROW=112
START_ROW = START_ROW - 1

# Authenticate
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Drive API client
drive_service = build('drive', 'v3', credentials=creds)

# The file ID of your private .xls file
file_id = '1YsToCoZTAWaxa6OXjZ-kgMipM_jg8WVwGywEICD0sTs'
# file_id = '1NS1gc9G7dcPaXXEckE7CeicidmT_O1dak1V9vWYlfQw'


# Get the file metadata to find its name
file_metadata = drive_service.files().get(fileId=file_id).execute()
file_name = file_metadata['name']+'.csv'
print(file_name)

# Download the file
request = drive_service.files().export_media(fileId=file_id,  mimeType='text/csv')
with open(file_name, 'wb') as f:
    downloader = drive_service._http.request(request.uri, "GET")
    f.write(downloader[1])


workbook = xlwt.Workbook()
sheet = workbook.add_sheet("Sheet1")

replacement_rows = [
    ['','','Ground 1','Ground 1','Ground 1','Ground 1','Ground 1','Ground 1','Ground 2','Ground 2','Ground 2','Ground 2','Ground 2','Ground 2','Ground 2','Ground 2','Ground 2','','',''],
    ['','','6:30:00 AM Slot','6:30:00 AM Slot','10:00:00 AM Slot','10:00:00 AM Slot','1:30:00 PM Slot','1:30:00 PM Slot','6:30:00 AM Slot','6:30:00 AM Slot','10:00:00 AM Slot','10:00:00 AM Slot','1:30:00 PM Slot','1:30:00 PM Slot','4:30:00 PM Slot','4:30:00 PM Slot','8:00:00 PM Slot','8:00:00 PM Slot','','']
]


# Read the original CSV (skip the first 2 rows)
with open(file_name, 'r', newline='') as infile:
    reader = csv.reader(infile)
    remaining_rows = [row[:18] for idx, row in enumerate(reader) if idx >= START_ROW]

# Combine hardcoded + remaining
new_data = replacement_rows + remaining_rows

# Write back to the same file (or a new one)
with open(file_name, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerows(new_data)

# Read the .xls file
df = pd.read_csv(file_name, header=[0, 1])

# Initialize a list to store records
records = []
records.append([ "Date", "Day", "Ground", "Slot", "Team"])
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
workbook.save("output_file.xlsx")


#upload output file
file_metadata = {
    'name': 'output_file.xlsx',  # Name it will have in Google Drive
    # Optional: add this to upload to a specific folder
    'parents': ['1KkPtctPIJTH7VlZ3jKfFvcIaFm41o9Sh']
}
media = MediaFileUpload('output_file.xlsx', mimetype='application/vnd.ms-excel')

# Upload the file
file = drive_service.files().create(
    body=file_metadata,
    media_body=media,
).execute()

print(f"File uploaded successfully. File ID: {file.get('id')}")

