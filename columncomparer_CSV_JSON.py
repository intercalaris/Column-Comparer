import pandas as pd
from datetime import date, datetime, timedelta
import json
import os

# Load column mappings from JSON file
mapping_file_path = r'C:\path\to\file\table_column_mapping.json' 
with open(mapping_file_path, 'r') as file:
    column_mappings = json.load(file)

# Map table names to parts of file names
table_file_namemap = {
    'Table Name 1': 'tablename1',
    'Table Name 2': 'tablename2',
    'Table Name 3': 'tablename3',
    'Table Name 4': 'tablename4'
}

date_logged = False
new_columns_found_today = False
today_dt = date.today()
today = str(today_dt)

yesterday_dt = today_dt - timedelta(days=1)
print(f"today's date is {today_dt} and yesterday's was {yesterday_dt}")

# Access csv/excel files to upload
csv_file_directory = r'C:\path\to\csv\files'
# Get file modification timestamp
modification_time = os.path.getmtime(csv_file_directory)
modification_date = datetime.fromtimestamp(modification_time).date()
# Get yesterday's date
yesterday = today_dt - timedelta(days=1)
files_from_yesterday = []

# List directory and filter files based on modification date
files_in_directory = os.listdir(csv_file_directory)
for file_name in files_in_directory:
    file_path = os.path.join(csv_file_directory, file_name)
    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path)).date()
    if file_mtime == yesterday:
        files_from_yesterday.append(file_name)
print(f"Found {len(files_from_yesterday)} files modified yesterday out of {len(files_in_directory)} files total in the directory.\n")

# Map SQL table names to file names for each file in directory
for file_name in files_from_yesterday:
    file_path = os.path.join(csv_file_directory, file_name)
    matched_table_name = None
    for table_name_key, file_id_value in table_file_namemap.items():
        if file_id_value in file_name:
            matched_table_name = table_name_key
            break

    # Read csv/excel file into pandas df
    if file_name.endswith('.csv'):
        new_csv_df = pd.read_csv(file_path)
    elif file_name.endswith('.xlsx'):
        new_csv_df = pd.read_excel(file_path)
    else:
        continue

    new_columns = []
    table_column_mapping = column_mappings[matched_table_name]
    print(f"Checking if columns from {file_name} ({matched_table_name}) are present in JSON file \n")
    # Check if column exists in mapping
    for csv_column in new_csv_df.columns:
        if csv_column not in table_column_mapping:
            new_columns.append(csv_column)

    # Create log for new columns  
    log_folder_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'Col Compare', 'Col Compare Logs')
    log_file_path = os.path.join(log_folder_path, 'new_columns.txt')
    os.makedirs(log_folder_path, exist_ok=True)

    # If new columns found for table, mark that new column was found today. If date not logged yet, log it and mark as logged.
    # Append list of new columns to log
    if len(new_columns) > 0:
        new_columns_found_today = True
        with open(log_file_path, 'a') as file:
            if date_logged == False:
                file.write(f"\n{today}:\n") 
                date_logged = True
            file.write(f"New columns for {file_name} ({matched_table_name}): {', '.join(new_columns)}\n")
            print(f"Logged new columns for {file_name} ({matched_table_name}): {', '.join(new_columns)}\n")
    else:
        print(f"For {file_name} ({matched_table_name}), no new columns found\n\n")

# If no new columns in any table:
if new_columns_found_today == False:
    print("No files contain new columns\n\n")
    with open(log_file_path, 'r') as file:
        log_lines = file.readlines()
        
    # if previous entry present
    if len(log_lines) >= 2:
        # if last log entry is "No new columns" and date isn't today's, overwrite last entry message and date
        start_date_str = log_lines[-2][:10]
        if ("No new columns" in log_lines[-1]) and (start_date_str != today):
            print("if: previous entry or entry range had no new columns and wasn't initiated today")
            log_lines[-2] = f"{start_date_str} to {today}:\n"   # date line
            log_lines[-1] = "No new columns\n"                  # message line
        elif ("No new columns" in log_lines[-1]) and (start_date_str == today):
            print("elif: previous log had no new columns and was from today")
            log_lines[-2] = f"{today}:\n"
            log_lines[-1] = "No new columns\n"
        else: # If last entry isn't "No new columns", append it  
            print("else: previous log had new columns ")
            log_lines.append(f"\n{today}:\n")
            log_lines.append("No new columns\n")
        with open(log_file_path, 'w') as file:
            file.writelines(log_lines)
    else: # If no previous entry:
        print("first entry in log")
        with open(log_file_path, 'w') as file:
            file.write(f"{today}:\nNo new columns\n")