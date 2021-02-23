import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from urllib.parse import urljoin, urlparse, unquote

from scrapers.scraper import Scraper

credentials = service_account.Credentials.from_service_account_file('key.json')

scoped_credentials = credentials.with_scopes(
  ['https://www.googleapis.com/auth/spreadsheets']
)

service = build('sheets', 'v4', credentials=scoped_credentials)

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = process.env.SPREADSHEET_ID
SAMPLE_RANGE_NAME = process.env.SPREADSHEET_RANGE

scraper = Scraper()

def sanitizeTwitterUrl(url):
  username = url.replace('https://', '')
  username = username.replace('Https://', '')
  username = username.replace('http://', '')
  username = username.replace('Http://', '')
  username = username.replace('T', 't')
  username = username.replace('www.', '')
  url = f"https://www.{username}"
  new_url = f"{urljoin(url, urlparse(url).path)}"
  last_char = new_url[-1]
  if last_char != '/':
    new_url = f"{new_url}/"
  
  return new_url

def sanitizeLinkedin(url):
  username = url.replace('https://', '')
  username = username.replace('Https://', '')
  username = username.replace('http://', '')
  username = username.replace('Http://', '')
  username = username.replace('L', 'l')
  username = username.replace('www.', '')
  username = username.replace('tr.', '')
  username = username.replace('uk.', '')
  username = username.replace('de.', '')
  username = username.replace('ca.', '')
  username = username.replace('at.', '')
  url = f"https://www.{username}"
  new_url = f"{urljoin(url, urlparse(url).path)}"
  last_char = new_url[-1]
  if last_char != '/':
    new_url = f"{new_url}/"
  
  return new_url

def sanitizeUsername(uname):
  username = uname.replace('@', '')
  return username

def process_values(values):
    for row in range(len(values)):
      row_length = len(values[row])
      print(f"row length {row_length}")
      if row_length >= 15:
        print(f"row {row} has data")
      else:
        username = sanitizeLinkedin(values[row][12])
        linked = scraper.getInfo(username, "Linkedin")
        
        processedData = [
          [
            linked["followers"],
            linked["connections"]
          ]
        ]
        # print(f"{username} data: {processedData}")
        
        batch_update_values_request_body = {
          'value_input_option': 'USER_ENTERED',
          "data": [
              {
                  "range": f"Linkedin!O{row+2}:P",
                  "values": processedData
              }
          ]
        }
        req = service.spreadsheets().values().batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=batch_update_values_request_body)
        res = req.execute()
        print('wrote data to sheet')
        
    scraper.destroy()

def main():
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        process_values(values)
        

if __name__ == '__main__':
    main()