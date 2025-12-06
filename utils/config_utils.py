import json
import sys
import shutil
from pathlib import Path
from utils.data_utils import try_parse_date # To normalize dates


def resource_path(relative_path):
    # Return the absolute path to a resource, works for PyInstaller.
    try:
        # PyInstaller stores bundled files in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Running normally
        base_path = Path(__file__).parent.parent  # same as your base_dir
    return base_path / relative_path

# Needed for PyInstaller functionality
def writable_config_path():
    # Returns a path to a writable config.json.
    #     - In development: same as default config.
    #     - In frozen EXE: next to the EXE.
    # Ensures that a copy of the default config exists if none is present.
    
    if getattr(sys, "frozen", False):
        # Folder where EXE resides
        write_path = Path(sys.executable).parent / "config.json"
        default_config = resource_path("config/config.json")
        # Copy default config to writable location if it doesn't exist
        if not write_path.exists():
            write_path.parent.mkdir(exist_ok=True)
            shutil.copy(default_config, write_path)
    else:
        write_path = resource_path("config/config.json")

    return write_path

# Reads config.json, normalizes entries, and returns a dict
def load_config():
    full_path = writable_config_path()
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
    full_path = resource_path(secrets_path)    
    # Gets all the variables from config.json and returns them as a dictionary
    with open(full_path, "r") as file:
        return json.load(file)
    
# Writes input into UI into config
def save_config(updated_values):
    full_path = writable_config_path()
    # Make sure the folder exists before I put this file inside it. If it already exists, that’s fine, just move on.
    full_path.parent.mkdir(exist_ok=True)
    with open(full_path, "w") as config_file:
        json.dump(updated_values, config_file, indent=4)
    