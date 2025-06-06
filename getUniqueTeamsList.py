from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pandas as pd
import xlwt
import csv


# Path to your service account credentials file
SERVICE_ACCOUNT_FILE = 'first-project-457714-60fa3e8514a5.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive.file']

START_ROW=3
START_ROW = START_ROW - 1
END_ROW=120
END_ROW = END_ROW - 1

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
    ['','','Ground 1','Ground 1','Ground 1','Ground 1','Ground 1','Ground 1','Ground 2','Ground 2','Ground 2','Ground 2','Ground 2','Ground 2','Ground 2','Ground 2','Ground 2','Ground 2'],
    ['','','6:30:00 AM Slot','6:30:00 AM Slot','10:00:00 AM Slot','10:00:00 AM Slot','1:30:00 PM Slot','1:30:00 PM Slot','6:30:00 AM Slot','6:30:00 AM Slot','10:00:00 AM Slot','10:00:00 AM Slot','1:30:00 PM Slot','1:30:00 PM Slot','4:30:00 PM Slot','4:30:00 PM Slot','8:00:00 PM Slot','8:00:00 PM Slot']
]


# Read the original CSV (skip the first 2 rows)
with open(file_name, 'r', newline='') as infile:
    reader = csv.reader(infile)
    remaining_rows = [row[:18] for idx, row in enumerate(reader) if idx >= START_ROW and idx <= END_ROW]

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
            records.append(cell_value)

# Optional: print all records
print(records)
count_dict = {}
for record in records:
    count_dict[record] = count_dict.get(record, 0) + 1

print(count_dict)

# Write data to sheet
sheet.write(0,0,"TeamName")
sheet.write(0,1, "Matches")
for row, (key, value) in enumerate(count_dict.items(), start=1):
    sheet.write(row, 0, key)
    sheet.write(row, 1, value)

# Save the workbook
workbook.save("uniqueTeamsList.xlsx")


#upload output file
file_metadata = {
    'name': 'uniqueTeamsList.xlsx',  # Name it will have in Google Drive
    # Optional: add this to upload to a specific folder
    'parents': ['1KkPtctPIJTH7VlZ3jKfFvcIaFm41o9Sh']
}
media = MediaFileUpload('uniqueTeamsList.xlsx', mimetype='application/vnd.ms-excel')

# Upload the file
file = drive_service.files().create(
    body=file_metadata,
    media_body=media,
).execute()

print(f"File uploaded successfully. File ID: {file.get('id')}")

