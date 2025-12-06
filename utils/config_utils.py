import json
import os
from utils.data_utils import try_parse_date # To normalize dates

# Reads config.json, normalizes entries, and returns a dict
def load_config(config_path = "config/config.json"):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    full_path = os.path.join(base_dir, config_path)
    # Gets all the variables from config.json and returns them as a dictionary
    with open(full_path, "r") as file:
        config = json.load(file)

    # config.json only lets me do strings as values, so this
    # converts the strings into data types that we acutally want
    for key, value in list(config.items()):
        if isinstance(value, str):
            low = value.strip().lower()
            if low == "true":
                config[key] = True
            elif low == "false":
                config[key] = False

    for date_key in ("start_date", "end_date"):
        if date_key in config:
            parsed = try_parse_date(config[date_key])
            if parsed:
                config[date_key] = parsed

    return config

# Reads secrets.json and returns the contents as a dictionary
def load_secrets(secrets_path = "config/secrets.json"):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    full_path = os.path.join(base_dir, secrets_path)
    # Gets all the variables from config.json and returns them as a dictionary
    with open(full_path, "r") as file:
        return json.load(file)
    
# Writes input into UI into config
def save_config(updated_values):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    full_path = os.path.join(base_dir, "config/config.json")
    with open(full_path, "w") as config_file:
        json.dump(updated_values, config_file, indent=4)
    