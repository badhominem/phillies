import os
import json
import pandas as pd
import locate_newest_emaildata as lne

# identifies which records in staged emails should be brought into gold source

def main():
	email_body = None
	
	# add current wd var so this becomes transferrable
	operating_path = '/home/badhominem/codefiles/experiments/phillies/emails/'
	
	fp_incremental_raw_data = lne.find_latest_data(operating_path, True)
	try:
		with open(fp_incremental_raw_data, 'r') as f:
			email_body = json.load(f)
	
	except Exception as e:
		print(e)
	
	print("checkpoint 1. Expect new emails.", email_body)

	## added 2024-04-01. Compare staged data to gold data.
	## add to gold data only non-existing emails
		
	## code not working as intended.
	## was calling on wrong function
	try:
		fp_current_data = lne.find_latest_data(operating_path, False)
		with open(fp_current_data, "r") as x:
			current_data = json.load(x)
	
	except Exception as e:
		print("load_emails(), opening finding and opening files in master hierarchy", "\n", e)

	try:
		# find the ids that are not in existing data
		
		email_ids = [d['email_id'] for d in current_data]
		
		new_ids = set(email_body.keys()).difference(set(email_ids))
		
		to_add = new_ids.intersection(set(email_body.keys()))
	
		print("Checkpoint 2. Expect emails that have not been added to master yet.", to_add)

	
		email_dict={}
		for key, value in email_body.items():
			print(key)
			if key in to_add:
				email_dict[key] = value

		print("Checkpoint 3. Expect JSON of emails that have not been added to master yet.", email_dict)
	except Exception as e:
		print("issue with email_ids", e)

	return email_dict
	

if __name__ == "__main__":
	main()