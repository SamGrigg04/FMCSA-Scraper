"""
retry logic?
"""

import requests

def get_json(url, params=None, headers=None):
    # Makes the API call
    response = requests.get(url, params=params, headers=headers)
    # Returns the data if there was no error
    if response.status_code == 200:
        return response.json()
    # Raise s an exception if there was an error
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")