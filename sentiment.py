from dotenv import load_dotenv
from openai import OpenAI

import os
import json
import pandas as pd
import load_emails
from datetime import datetime
import locate_newest_emaildata as lne

def load_client():
	client = None
	
	try:
		load_dotenv()

		api_key = os.getenv("OPENAI_API_KEY")
		
		if api_key is None:
			raise ValueError("API key not found in environment variables")

		else:
			client = OpenAI()
	
	except Exception as e:
		raise RuntimeError("Failed to load OpenAI client: " + str(e))
	
	return client

def sentiment_analysis(client, text):
	completion = client.chat.completions.create(
		model="gpt-3.5-turbo",
		messages=[
			{
				"role": "system",
				"content": "As an AI with expertise in language and emotion analysis, your task is to analyze the sentiment of the following text. Please consider the overall tone of the discussion, the emotion conveyed by the language used, and the context in which words and phrases are used. On a scale of -5 to 5, indicate how positive the text is, where 5 is the most positive, -5 is the least positive, and 0 is neutral. Respond with one digit."
			},
			{
				"role": "user",
				"content": text
			}
		],
		temperature=0
	)
	return completion.choices[0].message.content

def is_game_summary(client,text):
	completion = client.chat.completions.create(
		model="gpt-3.5-turbo",
		messages=[
			{
				"role": "system",
				"content": "You are a highly skilled AI with the capability to understand unstructured text. You will be given a text. If you think the text is attempting to summarize a major league baseball game played by the Phillies then, if you can find it in the text, respond with the name of the other team that participated in the game. Respond with the shortest version of their team name, and if you cannot find the name or if you think the email is not a summary of a MLB game played by the Phillies, simply respond with 'missing'"
			},
			{
				"role": "user",
				"content": text
			}
		],
		temperature=0
	)
	return completion.choices[0].message.content

def game_winner(client,text,opponent):
	completion = client.chat.completions.create(
		model="gpt-3.5-turbo",
		messages=[
			{
				"role": "system",
				"content": f"You are a highly skilled AI with the capability to understand unstructured text. You will be given a text that you have previously characterized as a summary of a MLB game played by the Phillies. The other team is {opponent}. Based on the text, who won the game? Respond with the shortest possible version of the team name"
			},
			{
				"role": "user",
				"content": text
			}
		],
		temperature=0
	)
	return completion.choices[0].message.content

def phillies_email(client, text, date_created):
	winner = 'missing'
	sentiment = '-99'
	opp = is_game_summary(client,text)
	
	if opp != 'missing':
		winner = game_winner(client, text, opp)
		sentiment = sentiment_analysis(client,text)
	
	return {
			'email_date': date_created,
			'opponent': opp,
			'winner': winner,
			'sentiment': sentiment
			}


def main():
	
	client = load_client()
	
	new_emails= load_emails.main()
	
	fp_gold_emails = lne.find_latest_data('/home/badhominem/codefiles/experiments/phillies/emails/', False)
	with open(fp_gold_emails, "r") as f:
		gold_emails = json.load(f)

	# # needs to update to reflect master data structure
	# # open latest master data
	# with open("output.json", "r") as f:
	# 	gold_emails = json.load(f)


	for id in new_emails:
		text = new_emails[id]['body']
		date = new_emails[id]['date_created']
		
		response = phillies_email(client, text, date)
		

		result =	{
					"email_id" : id,
					"contents": response
					}
		
		gold_emails.append(result)

	# need to change file structure of master folder
	# year/month/day/files.json
		
	file_date = datetime.now().date()
	target_dir = f"emails/master/{file_date.year}/{file_date.month}/{file_date.day}"
	os.makedirs(target_dir, exist_ok=True)
				
	target_fpath = f"{target_dir}/{file_date}_emaildata.json"

	with open(target_fpath, "w") as wf:
		json.dump(gold_emails, wf, indent=2)

if __name__ == "__main__":
  main()