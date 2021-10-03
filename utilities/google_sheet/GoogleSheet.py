from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
from datetime import datetime


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_RANGE_NAME = 'A:B'

#
find = "WP"
replacement = "auto"


class GoogleSheet:

    def __init__(self, sample_spreadsheet_id):
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        self.sample_spreadsheet_id = sample_spreadsheet_id
        self.values = None
        self.values_size = None
        creds = None
        if os.path.exists(os.path.join("static", 'token.pickle')):
            with open(os.path.join("static", 'token.pickle'), 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join("static", 'credentials.json'), SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(os.path.join("static", 'token.pickle'), 'wb') as token:
                pickle.dump(creds, token)
        assert creds is not None
        self.creds = creds
        self.service = build('sheets', 'v4', credentials=creds)
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.sample_spreadsheet_id,
                                    range=SAMPLE_RANGE_NAME).execute()
        self.values = result.get('values', [])
        self.upc = [x[0] for x in self.values if x[0] != 'UPC']
        self.cost = [x[1] for x in self.values if x[1] != 'COST']
        self.values_size = len(self.values)

    def update_sheet_with_values_at_the_end(self, values):
        service = self.service
        # [START sheets_update_values]
        _values = (
            values,
        )
        value_range_body = {
            'majorDimension': 'COLUMNS',
            'values': _values
        }

        body = {
            'values': _values
        }
        SAMPLE_RANGE_NAME = '{}:{}'.format(self.values_size + 1, self.values_size + 1)
        result = service.spreadsheets().values().update(
            spreadsheetId=self.sample_spreadsheet_id, range=SAMPLE_RANGE_NAME,
            valueInputOption="USER_ENTERED", body=body).execute()
        self.values.append(list(values))
        self.values_size = self.values_size + 1
        print('{0} cells updated.'.format(result.get('updatedCells')))