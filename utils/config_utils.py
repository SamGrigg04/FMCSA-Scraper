import json
import os


def load_config(config_path = "config/config.json"):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    full_path = os.path.join(base_dir, config_path)
    # Gets all the variables from config.json and returns them as a dictionary
    with open(full_path, "r") as file:
        return json.load(file)
    
def load_secrets(secrets_path = "config/secrets.json"):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    full_path = os.path.join(base_dir, secrets_path)
    # Gets all the variables from config.json and returns them as a dictionary
    with open(full_path, "r") as file:
        return json.load(file)
    
def update_config():
    return

def save_config():
    return