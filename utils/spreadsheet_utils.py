import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from gspread.utils import rowcol_to_a1
import time


def write_to_sheets(raw_data, data_needed, config, secrets):
    # Validate inputs
    if not raw_data:
        raise ValueError("raw_data is empty; nothing to write to sheets")
    if not data_needed:
        raise ValueError("data_needed is empty; no columns to write")
    if not isinstance(config, dict) or "spreadsheet_id" not in config or "sheet_name" not in config:
        raise ValueError("config must contain 'spreadsheet_id' and 'sheet_name'")
    if not isinstance(secrets, dict) or "service_account_file" not in secrets or "app_token" not in secrets:
        raise ValueError("secrets must contain 'service_account_file' and 'app_token'")
    # Build data frame from raw_data
    cooked_data = []
    for row in raw_data:
        bite_of_data = []
        for key in data_needed:
            bite_of_data.append(row.get(key, ""))
        cooked_data.append(bite_of_data)


    # Reads the csv data and makes sure it is formatted nicely
    df = pd.DataFrame(cooked_data, columns=data_needed).fillna("")
    if df.empty:
        raise ValueError("DataFrame is empty after processing raw_data")

    # Gives Google full permission to edit spreadsheets
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    # Reads the password and gives me credentials
    try:
        creds = Credentials.from_service_account_file(secrets["service_account_file"], scopes=scopes)
        # Creates a client that I can use to interact with Sheets
        client = gspread.authorize(creds)
    except Exception as e:
        raise Exception(f"Failed to authenticate with Google Sheets: {e}")

    # Open spreadsheet and worksheet (at the bottom of the screen)
    try:
        spreadsheet = client.open_by_key(config["spreadsheet_id"])
        worksheet = spreadsheet.worksheet(config["sheet_name"])
    except Exception as e:
        raise Exception(f"Failed to open spreadsheet or worksheet: {e}")

    # Ensure worksheet has enough rows and columns
    required_rows = len(df) + 1
    if worksheet.row_count < required_rows:
        try:
            worksheet.add_rows(required_rows - worksheet.row_count)
        except Exception as e:
            raise Exception(f"Failed to add rows to worksheet: {e}")

    required_cols = len(df.columns)
    if worksheet.col_count < required_cols:
        try:
            worksheet.add_cols(required_cols - worksheet.col_count)
        except Exception as e:
            raise Exception(f"Failed to add columns to worksheet: {e}")

    # Clears all old data (except the headers)
    try:
        worksheet.batch_clear([f"A2:{rowcol_to_a1(worksheet.row_count, required_cols)}"])
    except Exception as e:
        raise Exception(f"Failed to clear old data from worksheet: {e}")

    # Converts to the format expected
    values = df.values.tolist()
    
    # Send values to Google in chunks
    for i in range(0, len(values), 1000):
        chunk = values[i:i+1000]
        start_row = i + 2
        end_row = start_row + len(chunk) - 1
        range_name = f"A{start_row}:{rowcol_to_a1(end_row, required_cols)}"
        
        # Retry logic with exponential backoff
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                worksheet.update(range_name=range_name, values=chunk)
                print(f"writing to sheets... (rows {start_row}-{end_row})")
                break
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"Failed to update range {range_name} after {max_retries} retries: {e}")
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** (retry_count - 1)
                print(f"Update failed: {e}. Retrying in {wait_time}s... (attempt {retry_count}/{max_retries})")
                time.sleep(wait_time)
        
        # Rate-limiting: brief delay between chunks to avoid overwhelming the API
        if i + 1000 < len(values):
            time.sleep(0.5)
    
    print("All done")



