import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class Sheet:
    ID = None
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = None

    def __init__(self, id: str):
        self.ID = id
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('sheets', 'v4', credentials=creds)

    def getValues(self, range: str):
        result = self.service.spreadsheets().values().get(spreadsheetId=self.ID, range=range).execute()
        values = result.get('values', [])

        return values

def main():
    sheet = Sheet('1hEngBbbJQkBpfTjC0qbcsZld-edUK8dinQwnQ8_PgSM')
    values = sheet.getValues("Баллы итоговые!A2:B35")
    names = []
    for row in values:
        names.append(row[0])
    print(names)


if __name__ == '__main__':
    main()