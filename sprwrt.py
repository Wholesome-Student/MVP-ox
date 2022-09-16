import sys
import pickle
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError as googleHttpError

scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']

if len(sys.argv) == 3:
    spreadsheet_id = sys.argv[1]
    sheet_name = sys.argv[2]
else:
    sys.exit(f'invalid arguments. \n Usage: {sys.argv[0]} [Spreadsheet ID]')

creds = None

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'spr/sodium-hue-361405-237068a500a2.json', scopes)
        creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# Config
range_ = sheet_name + '!A1:B5'

# Check values on sheet
try:
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=range_).execute()
    print(result.get('values', []))
except googleHttpError as e:
    print(e)

# Preprocess
values = []
for i in range(10):
    values += [[f'test{i}', i]]

value_input_option = 'RAW'

body = {
    'range': range_,
    'majorDimension': 'ROWS',
    'values': values
}

# Write values to sheet
try:
    result = sheet.values().update(spreadsheetId=spreadsheet_id,
                                   range=range_,
                                   valueInputOption=value_input_option,
                                   body=body).execute()
except googleHttpError as e:
    print(e)

# Check values on sheet
try:
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=range_).execute()
    print(result.get('values', []))
except googleHttpError as e:
    print(e)