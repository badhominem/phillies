import json
import pandas as pd
import os
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import locate_newest_emaildata as lne

from datetime import datetime

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
	fp_master = lne.fp_latest_master_data()
	
	with open(fp_master, "r") as f:
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
	
	df = df.filter(items=['email_date', 'sentiment', 'phillies_won', 'body'])
	
	df_filtered = df[ (df['sentiment'] != -99) & (df['email_date'] > datetime(2023,12,31)) ]
	
	df_sorted = df_filtered.sort_values('email_date', axis = 0, ascending = True)

	return df_sorted

def transformed_df_to_string(df):
	series = df['sentiment'].astype(str) + ' ' + df['phillies_won'].astype(str)
	combined_text = series.str.cat(sep=' ')

	return combined_text

def main():
	client = load_client()
	df = load_df()
	
	df = df_filter(df)

	# Smooth the 'sentiment' column using a rolling mean with window size 3
	# smoothed_sentiment = df['sentiment'].rolling(window=4, min_periods=1).mean()
	smoothed_sentiment = df['sentiment']
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

	# persist plot in hierarchy
	file_date = df['email_date'].max()
	target_dir = f"moodcharts/{file_date.year}/{file_date.month}/{file_date.day}"
	os.makedirs(target_dir, exist_ok=True)
	target_fpath = f"{target_dir}/{file_date.date()}_pete_mood.png"
	plt.savefig(target_fpath)

	return

if __name__ == "__main__":
	main()