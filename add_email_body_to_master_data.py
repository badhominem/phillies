import os
import json
import pandas as pd
from datetime import datetime

import locate_newest_emaildata as lne

def compare_raw_and_master():
	fp_master = lne.fp_latest_master_data()
	with open(fp_master, "r") as f:
		master = json.load(f)

	fp_raw = lne.fp_latest_raw_data()
	with open(fp_raw, "r") as f:
		raw = json.load(f)
	
	for element in master:
		if element['email_id'] in raw.keys():
			element['contents']['body'] = raw[element['email_id']]['body']
	
	# persist in master hierarchy
	file_date = datetime.now().date()
	target_dir = f"emails/master/{file_date.year}/{file_date.month}/{file_date.day}"
	os.makedirs(target_dir, exist_ok=True)
				
	target_fpath = f"{target_dir}/{file_date}_sentiment_body.json"

	with open(target_fpath, "w") as wf:
		json.dump(master, wf, indent=2)
	
	return None

if __name__ == "__main__":
	compare_raw_and_master()