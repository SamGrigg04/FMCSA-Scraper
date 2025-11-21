import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from gspread.utils import rowcol_to_a1


def write_to_sheets(raw_data, data_needed, config, secrets):
    
    cooked_data = []
    for row in raw_data:
        byte_of_data = []
        for key in data_needed:
            byte_of_data.append(row.get(key, ""))
        cooked_data.append(byte_of_data)


    # Reads the csv data and makes sure it is formatted nicely
    df = pd.DataFrame(cooked_data, columns=data_needed).fillna("")

    # Gives Google full permission to edit spreadsheets
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    # Reads the password and gives me credentials
    creds = Credentials.from_service_account_file(secrets["service_account_file"], scopes=scopes)
    # Creates a client that I can use to interact with Sheets
    client = gspread.authorize(creds)

    
    # Opens the spreadsheet and opens the worksheet (at the bottom of the screen)
    spreadsheet = client.open_by_key(config["spreadsheet_id"])
    worksheet = spreadsheet.worksheet(config["sheet_name"])

    # Ensure worksheet has enough rows and columns
    required_rows = len(df) + 1
    if worksheet.row_count < required_rows:
        worksheet.add_rows(required_rows - worksheet.row_count)

    required_cols = len(df.columns)
    if worksheet.col_count < required_cols:
        worksheet.add_cols(required_cols - worksheet.col_count)
    

    # Clears all old data (except the headers)
    worksheet.batch_clear([f"A2:{rowcol_to_a1(worksheet.row_count, worksheet.col_count)}"])

    # Converts to the format expected
    values = df.values.tolist()
    # Sends the values to Google in chunks
    # Instead of worksheet.update(range_name=f"A2:{rowcol_to_a1(num_rows+1, num_cols)}", values=values)
    for i in range(0, len(values), 1000):
        # TODO: Add error handling. I overwhelmed the API once with too many requests
        chunk = values[i:i+1000]
        start_row = i + 2
        end_row = start_row + len(chunk) - 1
        worksheet.update(
            range_name=f"A{start_row}:{rowcol_to_a1(end_row, worksheet.col_count)}",
            values=chunk
        )
        print("writing to sheets...")



