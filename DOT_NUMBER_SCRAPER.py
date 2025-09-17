"""
Author: Sam Grigg
Last Updated: 09/17/2025
Purpose: Get data from FMCSA and put it in a Google Sheet

Notes:
    To change the sheet the data imports to:
        Update config.json
        Make sure the helper account has editing permission

    If you're using the code and you're not me:
        Update APP_TOKEN (line 102)
        Update SERVICE_ACCOUNT_FILE (line 275)
        Get a different helper account
    To filter with different parameters, add them in params (line 64)
    To include more data on the spreadsheet, update data_needed (line 154)
"""


import requests # Looks at the API data
import csv # Accesses and modifies spreadsheets
from datetime import datetime # Needed to get most current effective date
import json # Makes the variables work with a config file

# Stuff for getting the data on a shared Google Sheet
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from gspread.utils import rowcol_to_a1


# Gets the data from a call and checks to see if it throws an error
def get_json(url, params=None, headers=None):
    # Makes the API call
    response = requests.get(url, params=params, headers=headers)
    # Returns the data if there was no error
    if response.status_code == 200:
        return response.json()
    # Raises an exception if there was an error
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")

def format_phone(number):
    # If the number has a US country code, remove it
    if len(number) == 11 and number.startswith("1"):
        number = number[1:]
    # Format as (123) 456-7890
    if len(number) == 10:
        number = f"({number[:3]}) {number[3:6]}-{number[6:]}"
    # If it is longer than normal and isn't a US number
    # just return non-formatted numbers
    return number

# Reads the config file to update variables
with open("config.json") as f:
    config = json.load(f)

# Configurable variables
STATE = config["state"]
SPREADSHEET_ID = config["spreadsheet_id"]
SHEET_NAME = config["sheet_name"]

# URL for the main API call
url = "https://data.transportation.gov/resource/az4n-8mr2.json"

# Filters the data we need in the API call
params = {
    "$select": "count(*)", # Figuring out if we need multiple requests
    "phy_state": STATE, # Hardcoded to PA
    "carrier_operation": "A", # Hardcoded to Interstate
    "status_code": "A" # Only active status
}

# Get the number of companies so we know if we need to paginate
data = get_json(url, params)
rows = int(data[0]["count"])

# Set up the parameters
all_data = [] # Going to be a huge list with lots of dictionaries
params.pop("$select", None)
params["$limit"] = 50000
params["$offset"] = 0

# Does the API call and adds the data to the big list
data = get_json(url, params)
all_data.extend(data)

# If we need to paginate: (more than 50k rows of data)
if rows > 50000:
    offset = 50000
    # Keeps offsetting until we get to the end of the data
    while rows > 0:
        params["$offset"] = offset
        all_data.extend(get_json(url, params))
        rows -= 50000
        offset += 50000

# URL to get the extra data
csv_url = "https://data.transportation.gov/resource/qh9u-swkp.json"
# Helps get around call limits
# DO NOT SHARE
APP_TOKEN = ""

# Sets the parameters for the API call
headers = {"X-App-Token": APP_TOKEN}
params = {
    "$limit": 50000,
    "$offset": 0
}

dot_lookup = {} # This will map DOTs to their effective date and current current_carrier

while True:
    # Gets at most 50k rows of data
    data = get_json(csv_url, params=params, headers=headers)
    # If there is no more data, end the loop
    if not data:
        break

    # Maps DOTs to their effective date and current carrier and stores them in a dictionary so we can look them up
    for row in data:
        dot = str(int(row["dot_number"]))
        effective_date_string = row.get("effective_date", "").strip()
        current_carrier = row.get("name_company", "").strip()
        
        # Prevents an error if there is no effective date
        try:
            effective_date = datetime.strptime(effective_date_string, "%m/%d/%Y")
        except ValueError:
            effective_date = None

        # If there isn't another effective date for the company in the
        # database already, great. Set it.
        if dot not in dot_lookup:
            dot_lookup[dot] = {
                "effective_date": effective_date_string,
                "parsed_date": effective_date,
                "current_carrier": current_carrier
            }

        # If there is another effective date, figure out which date is
        # more recent and set that one.
        else:
            existing_effective_date = dot_lookup[dot]["parsed_date"]
            if effective_date and (existing_effective_date is None or effective_date > existing_effective_date):
                dot_lookup[dot] = {
                    "effective_date": effective_date_string,
                    "parsed_date": effective_date,
                    "current_carrier": current_carrier
                }
    # Keep the loop going
    params["$offset"] += 50000
    # This way I know something is actually happening
    print("Loading...")

# Data we can get from the first API call (minus cargo)
data_needed = [
    "dot_number", 
    "legal_name", 
    "dba_name", 
    "phone", 
    "email_address", 
    "power_units", 
    "total_drivers", 
    "classdef" 
    ]
# All possible cargo types
cargo_list = [
    "crgo_genfreight",
    "crgo_household",
    "crgo_metalsheet",
    "crgo_motoveh",
    "crgo_drivetow",
    "crgo_logpole",
    "crgo_bldgmat",
    "crgo_mobilehome",
    "crgo_machlrg",
    "crgo_produce",
    "crgo_liqgas",
    "crgo_intermodal",
    "crgo_passengers",
    "crgo_oilfield",
    "crgo_livestock",
    "crgo_grainfeed",
    "crgo_coalcoke",
    "crgo_meat",
    "crgo_garbage"
    ]
# Format the cargo types to be nice text
nice_cargo = {
    "crgo_genfreight": "General Freight",
    "crgo_household": "Household Goods",
    "crgo_metalsheet": "Metal Sheets, Coils, Rolls",
    "crgo_motoveh": "Motor Vehicles",
    "crgo_drivetow": "Driveaway / Towaway",
    "crgo_logpole": "Logs, Poles, Beams, Lumber",
    "crgo_bldgmat": "Building Materials",
    "crgo_mobilehome": "Mobile Homes",
    "crgo_machlrg": "Machinery, Large Objects",
    "crgo_produce": "Fresh Produce",
    "crgo_liqgas": "Liquids/Gases",
    "crgo_intermodal": "Intermodal Containers",
    "crgo_passengers": "Passengers",
    "crgo_oilfield": "Oilfield Equipment",
    "crgo_livestock": "Livestock",
    "crgo_grainfeed": "Grain, Feed, Hay",
    "crgo_coalcoke": "Coal/Coke",
    "crgo_meat": "Meat",
    "crgo_garbage": "Garbage, Refuse, Trash"
}

filtered_rows = [] # This will contain each row in the spreadsheet as a list

# Takes all the data from the API call to format it nicely for our spreadsheet
for row in all_data: # For each company
    filtered_row = [] # This will be one row in the spreadsheet

    # Non-cargo Data
    for key in data_needed:
        # Phone number formatting
        if key == "phone":
            number = str(row.get(key, "")).strip()
            if number: # If the phone number exists
                pretty_number = format_phone(number)
                row[key] = pretty_number


        # Add the data to the row for the spreadsheet
        filtered_row.append(row.get(key, ""))

    # Cargo Data
    cargo_carried = []
    for key in cargo_list:
        # Format the data as a comma-separated list
        if row.get(key, "") == "X":
            cargo_carried.append(nice_cargo[key])
    # Add the list to the row for the spreadsheet
    filtered_row.append(", ".join(cargo_carried))
    
    # Get the DOT so we can look up the extra data
    dot = str(row.get("dot_number", "")).strip()
    extra_data = dot_lookup.get(dot, {})

    # Add the extra data to the row
    filtered_row.append(extra_data.get("effective_date", ""))
    filtered_row.append(extra_data.get("current_carrier", ""))
    
    # Add the row to the spreadsheet
    filtered_rows.append(filtered_row)
    
# Headers for the spreadsheet
spreadsheet_headers = [
    "Dot Number", 
    "Legal Name", 
    "DBA", 
    "Number", 
    "Email", 
    "Power Units", 
    "Driver Count", 
    "Authority Status", 
    "Cargo Carried", 
    "Effective Date", 
    "Current Carrier"
    ]

# Writes the data to the spreadsheet
with open("output.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(spreadsheet_headers)
    writer.writerows(filtered_rows)

# Uploads to sheets
CSV_FILE = "output.csv"
# This is basically the password for the helper account. Don't share it.
SERVICE_ACCOUNT_FILE = ""

# Gives Google full permission to edit spreadsheets
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
# Reads the password and gives me credentials
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
# Creates a client that I can use to interact with Sheets
client = gspread.authorize(creds)

# Reads the csv data and makes sure it is formatted nicely
df = pd.read_csv(CSV_FILE, dtype=str)
df = df.fillna("")

# Opens the spreadsheet and opens the worksheet (at the bottom of the screen)
spreadsheet = client.open_by_key(SPREADSHEET_ID)
worksheet = spreadsheet.worksheet(SHEET_NAME)

# Determines how many rows/columns to update
num_rows = len(df)
num_cols = len(df.columns)

# Clears all old data (except the headers)
worksheet.batch_clear([f"A2:{rowcol_to_a1(num_rows+1, num_cols)}"])

# Converts to the format expected
values = df.values.tolist()
# Sends the values to Google
worksheet.update(range_name=f"A2:{rowcol_to_a1(num_rows+1, num_cols)}", values=values)
