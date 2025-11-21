from utils.network_utils import get_json
from datetime import datetime, timedelta


# Makes the phone number pretty
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

# Makes the cargo carried pretty
def format_cargo(row):
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

    cargo_carried = []
    for key in cargo_list:
        # Format the data as a comma-separated list
        if row.get(key, "") == "X":
            row.pop(key, "")
            cargo_carried.append(nice_cargo[key])
    row["cargo_carried"] = ", ".join(cargo_carried)
    return

# Probably just use this one for loading bar purposes
def dataset_rows(url, params, headers):
    params = params.copy()
    params["$select"] = "count(*) as count"
    return int(get_json(url, params, headers)[0]["count"])

# Combines two data sets based on dot number
# TODO: This will need some testing. I don't
# fully understand it yet.
def combine_lists_dot(list1, list2):
    
    # This will be a reference list with all
    # the dot numbers in list1
    merged_dict = {}

    # For each dict in list 1, add the dot_number
    # to the reference list
    for dict1 in list1:
        key = dict1["dot_number"]
        value = dict1.copy()
        merged_dict[key] = value

    # Merge in values from list2
    for dict2 in list2:
        dot = dict2["dot_number"]
        if dot in merged_dict:
            # Merge dictionaries: values in list1 take precedence if keys overlap
            merged_dict[dot] = {**dict2, **merged_dict[dot]}
        # else:
        #     merged_dict[dot] = dict2.copy()

    # Convert back to list
    return list(merged_dict.values())

# When there are multiple effective dates
# for one dot number, it filters the data
# so it just has the most recent one and 
# the corresponding information
def get_latest_date(data, date_type):
    latest = {}

    for entry in data:
        dot = entry["dot_number"]
        date_str = entry.get(date_type, "")

        try:
            date = datetime.strptime(date_str, "%m/%d/%Y")
        except (ValueError, TypeError):
            continue

        if dot not in latest or date > latest[dot]["_parsed_date"]:
            latest[dot] = {**entry, "_parsed_date": date}

    for dot in latest:
        latest[dot].pop("_parsed_date")
    
    return list(latest.values())

def find_how_long(data):
    # take the orig_served_date and find how long between then and today
    # add that value to the dict with the key "business_duration"
    today = datetime.now()
    for row in data:
        date_str = row.get("orig_served_date", "")
        try:
            served_date = datetime.strptime(date_str, "%m/%d/%Y")
            delta = today - served_date
            # store duration in years with one decimal, e.g. "3.5 years"
            row["business_duration"] = round(delta.days / 365, 1)
        except (ValueError, TypeError):
            # if date is invalid or missing
            row["business_duration"] = ""
    
    return data

# Modifies a data set to only contain rows
# if they have the value we are looking for.
def has_value(data, field):
    filtered = []
    for row in data:
        value = row.get(field)
        if value not in ("", None):
            filtered.append(row)
    return filtered

# Modifies the data set to only have dates
# in the specified range
def in_date_range(data, date_field, start_date=None, end_date=None):
    # Default: from today to one month in the future
    if start_date is None:
        start_date = datetime.now()
    if end_date is None:
        end_date = start_date + timedelta(days=30)

    try:
        start_date = datetime.strptime(start_date, "%m/%d/%Y")
        end_date = datetime.strptime(end_date, "%m/%d/%Y")
    except (ValueError, TypeError):
        print("Start End Error")

    # Sort the data (newest first)
    data = sorted(
        data,
        key=lambda x: datetime.strptime(x.get(date_field, "01/01/1900"), "%m/%d/%Y"),
        reverse=False
    )

    filtered = []
    for row in data:
        date_str = row.get(date_field, "")
        try:
            date = datetime.strptime(date_str, "%m/%d/%Y")
        except ValueError:
            continue  # skip rows with invalid or missing dates

        if start_date <= date <= end_date:
            filtered.append(row)

    return filtered

def sort_dot(data):
    return sorted(
        data,
        key=lambda x: int(x.get("dot_number", "")),
        reverse=True
    )
