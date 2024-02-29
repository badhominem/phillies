import json
import pandas as pd
import os
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


from dotenv import load_dotenv
from openai import OpenAI


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

def load_df():

	# Get data from sentiment analysis
	with open("output.json", "r") as f:
		data = json.load(f)

	# Flatten JSON data to create a data frame
	df_norm = pd.json_normalize(data)

	# Remove 'contents.' from names of columns that have been flattened
	# Both of these methods work
	# df_norm.rename(columns=lambda x: x.replace("contents.", ""), inplace=True)
	df_norm.columns = df_norm.columns.str.replace("contents.", "")

	# change data types to support transformations
	df_norm['sentiment'] = df_norm['sentiment'].astype(int)
	df_norm['email_date'] = pd.to_datetime(df_norm['email_date'])
	
	return df_norm

def df_filter(df):
	
	df['phillies_won'] = df['winner'].map(lambda x: str.lower(x) in ["phillies", "philadelphia phillies"])
	
	df = df.filter(items=['email_date', 'sentiment', 'phillies_won'])
	
	df_filtered = df[ df['sentiment'] != -99 ]
	
	return df_filtered

def transformed_df_to_string(df):
	series = df['sentiment'].astype(str) + ' ' + df['phillies_won'].astype(str)
	combined_text = series.str.cat(sep=' ')

	return combined_text


def prognosis_win(client, df_as_text):
	result = client.chat.completions.create(
		model="gpt-3.5-turbo",
		messages=[
			{
				"role":"system",
				"content": "You are a highly skilled AI with the capability to understand structured text data. Here is a string that contains only digits and booleans. The digits can range from -5 to 5 and represent positivity, where -5 is the least positive and 5 is the most positive. Each digit is associated with the boolean to the right of it. The first digit and first boolean starting from the left of the string represent the most recent recorded values. The rightmost digit and boolean represent the oldest records. Based on this list, please predict the sentiment digit (-5 to 5) in the event that the next boolean is True"
			},
			{
				"role":"user",
				"content": df_as_text
			}
		]
	) 
	return result.choices[0].message.content

def main():
	client = load_client()
	df = load_df()
	
	df = df_filter(df)
	
	# Smooth the 'sentiment' column using a rolling mean with window size 3
	smoothed_sentiment = df['sentiment'].rolling(window=4, min_periods=1).mean()

	# Plot
	plt.figure(figsize=(12, 8))
	plt.ylim([-5, 5])
	plt.axhline(y=0, color='black', linestyle='-', linewidth='2')
	plt.plot(df['email_date'], smoothed_sentiment, marker='o', linestyle='-', color='black', linewidth='2')
	plt.xlabel('DATE', fontsize = 14)
	plt.xticks(fontsize=12)
	plt.ylabel('MOOD', fontsize = 14)
	plt.yticks(fontsize=12)
	plt.tick_params(axis='x', width=2)
	plt.tick_params(axis='y', width=2)
	for spine in plt.gca().spines.values():
		spine.set_linewidth(2)
	plt.title('Post-game mood barometer', fontsize = 16)
	plt.suptitle('"Re: Phillies" - the emotional toll of baseball', fontsize = 18)
	
	plt.savefig("pete\'s_mood.png")

	return

if __name__ == "__main__":
	main()