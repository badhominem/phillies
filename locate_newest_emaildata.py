import os

def find_latest_data(path, raw):
    # file hierarchy structure
    # raw/year/month/day/yearmonthday_emaildata.json

    # cycle through directories
    # find maximum folder with maximum values
    # enter folder
    # look for maximum value folder
    # repeat until there is no more folder
    # show files inside last folder
    # show contents of path
    if raw == True:
        path = path + 'raw'
    elif raw == False:
        path = path + 'master'
    else:
        path = path
    
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
        return find_latest_data(path_to_max, "no")
    elif folders:
        # if path_to_max is none, current level is not folder
        # we want to inspect for files
        return os.path.join(path, folders[0])
    else: 
        return None


if __name__ == "__main__":
    operating_path = '/home/badhominem/codefiles/experiments/phillies/emails/'
    x = find_latest_data(operating_path, False)
    print(x)
