import os
import pandas as pd

def list_files_and_columns(directory):
    for filename in os.listdir(directory):
        # Check if file is csv or excel
        if filename.endswith('.csv') or filename.endswith('.xlsx'):
            file_path = os.path.join(directory, filename)
            # Load file with pandas
            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                # Extract column names
                columns = ', '.join(df.columns)
                print(f"{filename}: {columns}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

directory_path = r"C:\path\to\download"
list_files_and_columns(directory_path)