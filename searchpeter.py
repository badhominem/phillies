import os.path
import base64
from bs4 import BeautifulSoup 
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId='me', q='from:peter.g.donato@gmail.com subject:Phillies').execute()
    messages = results.get('messages', [])
    
    if not messages:
        print('No messages found with the subject "Phillies"')
    else:
        print('Messages with the subject "Phillies":')
        msg = service.users().messages().get(userId='me', id='18dd39e9d02df186').execute()
        payload = msg['payload']
        headers = payload['headers']
        for d in headers:
           if d['name'] == 'Subject':
              subject = d['value']

        parts = payload.get('parts')[0]
        data = parts['parts'][0]['body']['data']
        data = data.replace("-", "+").replace("_","/")
        
        data_decoded = base64.b64decode(data)
        
        soup = BeautifulSoup(data_decoded, "html.parser")
        
        # Find all blockquote tags and extract them
        blockquotes = soup.find_all('blockquote')
        for blockquote in blockquotes:
            blockquote.extract()

        elements_with_class = soup.find_all(attrs={"class": True})
        for element in elements_with_class:
           element.extract()

        # Print the modified HTML
        print("Email subject: ", subject, " Email Body: ", soup.get_text(strip = False))

        print(parts)
        
            # for message in messages:
            #     print(message['id'])
            #     msg = service.users().messages().get(userId='me', id=message['id']).execute()
            #     payload = msg['payload']
            #     print(payload.keys())
                # if 'parts' in payload:
                #     parts = payload['parts']
                #     body = None
                #     for part in parts:
                #         if part['mimeType'] == 'text/plain':
                #             data = part['body']['data']
                #             body = base64.urlsafe_b64decode(data).decode('utf-8')
                #             break
                #     if body:
                #         print('Message Body:', body)
                # else:
                #     body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                #     print('Message Body:', body)
            # i += 1
  except HttpError as error:
        print('An error occurred:', error)

if __name__ == "__main__":
  main()