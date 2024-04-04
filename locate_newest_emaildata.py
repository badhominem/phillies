import os

def fp_latest_master_data():
    starting_fp = '/home/badhominem/codefiles/experiments/phillies/emails/master'
    fp_latest_data = find_max_folder(starting_fp)
    return fp_latest_data

def fp_latest_raw_data():
    starting_fp = '/home/badhominem/codefiles/experiments/phillies/emails/raw'
    fp_latest_data = find_max_folder(starting_fp)
    return fp_latest_data

def find_max_folder(path):
    """This function finds the folder with the maximum value 
    inside the emails master and raw file hierarchy.
    emails/raw/year/month/day/file.json
    The function returns the path to the file in the maximum
    folder of the hierarchy.
    The anticipation is that there will be a maximum of one file
    in each day leaf. This is due to the logic in ingest_and_stage_emails.py:
    
    target_fpath = f"{target_dir}/{file_date.date()}_emaildata.json"

			with open(target_fpath, 'a') as f:
				json.dump(extract, f, indent=2)
    
    This logic means that all _emaildata.json files should be checked
    for email id duplicates.
    """

    folders = os.listdir(path)

    max_val = 0
    path_to_max = None

    # cycle through directories to identify the one with max value
    for folder in folders:
        
        new_dir = os.path.join(path,folder)
        
        # check if path is file
        if os.path.isdir(new_dir):
            try:
                folder_val = int(folder)
                
                if folder_val > max_val:
                    max_val = folder_val
                    # update the path with max value
                    path_to_max = new_dir
            except ValueError:
                pass
    
    if path_to_max:
        # if path_to_max is not None, current level is a folder
        return find_max_folder(path_to_max)
    elif folders:
        # if path_to_max is none, current level is not folder
        # we want to inspect for files
        return os.path.join(path, folders[0])
    else: 
        return None
