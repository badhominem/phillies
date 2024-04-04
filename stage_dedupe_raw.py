import os
import json
import pandas as pd
import locate_newest_emaildata as lne

# identifies which records in staged emails should be brought into gold source

def main():
	email_body = None
	
	fp_raw = lne.fp_latest_raw_data()
	
	try:
		with open(fp_raw, 'r') as f:
			email_body = json.load(f)
	
	except Exception as e:
		print(e)

	## added 2024-04-01. Compare staged data to gold data.
	## add to gold data only non-existing emails
	
	try:
		fp_master = lne.fp_latest_master_data()
		with open(fp_master, "r") as x:
			current_data = json.load(x)
	
	except Exception as e:
		print("stage_dedupe_raw.py, tried to get file path for most recent master data and then open the file", e)

	try:
		# find the ids that are not in existing data
		email_dict = {}

		email_ids = [d['email_id'] for d in current_data]
		
		new_ids = set(email_body.keys()).difference(set(email_ids))
		
		# if new_ids is empty, return None

		to_add = new_ids.intersection(set(email_body.keys()))

		if to_add == set():
			return email_dict
	
		for key, value in email_body.items():
			
			if key in to_add:
				email_dict[key] = value

	except Exception as e:
		print("stage_dedupe_raw.py, tried to finalise dictionary of email ids to be added to master data", e)

	return email_dict
	

if __name__ == "__main__":
	main()