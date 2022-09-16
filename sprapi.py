import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# use creds to create a client to interact with the Google Drive API
scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('spr/sodium-hue-361405-237068a500a2.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("MVP").sheet1

# Extract and print all of the values
"""
list_of_hashes = sheet.get_all_records()
#print(list_of_hashes)
with open("spr/cell.json", "w") as f:
    json.dump(list_of_hashes, f, ensure_ascii=False, indent=4)
"""

sheet.update_cell(1,1,"test1")