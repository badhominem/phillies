import os.path
import base64
from bs4 import BeautifulSoup 
import pandas as pd
import re
import json
import email
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def gmail_credentials():
	""" Get user gmail credentials from Oauth flow.
	currently requires a new credential every 7 days on google console.
	Once the project is no longer in testing environment, the credential
	does not have to be renewed every 7 days.
	philliesdump@gmail.com receives all phillies emails.
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
	return creds

def main():
	creds = gmail_credentials()

	try:
		# Call the Gmail API
		service = build("gmail", "v1", credentials=creds)
		results = service.users().messages().list(userId='me', q='from:peter.g.donato@gmail.com subject:Phillies').execute()
		messages = results.get('messages', [])
		if not messages:
			print('No messages found with the subject "Phillies"')
		else:
			extract = {}
			file_date = datetime.now()

			for message in messages:
				
				body = ""
				# GET request for one message:
				msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()

				data = msg['raw']
				data = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
				
				# Create timestamp
				internalDate = msg['internalDate']
				internalDate = int(internalDate) / 1000
				internalDate = datetime.fromtimestamp(internalDate)

				mime_msg = email.message_from_bytes(data)
				
				messageMainType = mime_msg.get_content_maintype()
				
				if messageMainType == 'multipart':
					for part in mime_msg.walk():
						if part.get_content_type() == 'text/html':
							
							soup = BeautifulSoup(part.get_payload(decode=True).decode('utf-8', 'ignore'), "html.parser")
							
							blockquotes = soup.find_all('blockquote')
							for blockquote in blockquotes:
								blockquote.extract()
							
							body_part = soup.get_text(separator="\n")
							
							if body == "":
								body = body_part
							else:
								body = "\n" + body_part
											
				elif messageMainType == 'text':
					
					soup = BeautifulSoup(mime_msg.get_payload(decode=True).decode('utf-8', 'ignore'), "html.parser")
					
					blockquotes = soup.find_all('blockquote')
					for blockquote in blockquotes:
						blockquote.extract()
					
					body = soup.get_text(separator="\n")

				extract[message['id']] = {						
						"date_created": str(internalDate),
						"date_imported": str(file_date),
						"body": body
					}
			try:
				# persist in date hierarchy
				target_dir = f"emails/raw/{file_date.year}/{file_date.month}/{file_date.day}"
				os.makedirs(target_dir, exist_ok=True)
				
				target_fpath = f"{target_dir}/{file_date.date()}_emaildata.json"

				with open(target_fpath, 'a') as f:
					json.dump(extract, f, indent=2)
			
			except Exception as e:
				print("json.dump location", e)


	except:
		print("error bottom of script")

if __name__ == "__main__":
  main()