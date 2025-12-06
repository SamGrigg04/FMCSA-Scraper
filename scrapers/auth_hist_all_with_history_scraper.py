"""
Scrapes data from https://data.transportation.gov/Trucking-and-Motorcoaches/AuthHist-All-With-History/9mw4-x3tu/about_data
"""

from utils.network_utils import get_json # Makes requests to the API
from utils.data_utils import dataset_rows, get_latest_date, find_how_long # For formatting data

def run(params, headers, progress_queue, check_count=True):
    url = "https://data.transportation.gov/resource/9mw4-x3tu.json"

    params = params.copy()
    headers = headers.copy()
    data = [] # List of dicts that contains all the info scraped

    # Gets the number of rows so the progress bar can be updated dynamically
    try:
        rows = dataset_rows(url, params, headers) if check_count else None
    except Exception as e:
        progress_queue.put((None, f"Error fetching dataset row count for {url}: {e}"))
        return []

    # If more than 50k rows, pagination is nescessary
    offset = 0
    params["$limit"] = 50000    

    while True:
        params["$offset"] = offset
        try:
            page = get_json(url, params, headers)
        except Exception as e:
            progress_queue.put((None, f"Error fetching data from {url} at offset {offset}: {e}"))
            return []
        if not page:
            break

        # Normalizes DOT number
        for row in page:
            row["dot_number"] = row.get("dot_number", "").zfill(8)

        try:
            data.extend(page)
        except Exception as e:
            progress_queue.put((None, f"Warning: failed to extend data at offset {offset} for {url}: {e}"))
            pass
        offset += len(page)

        progress_queue.put((100 * offset/rows, f'fetched {offset}/{rows} rows...'))

        if rows and offset >= rows:
            break

    if not data:
        progress_queue.put((None, "No data fit your parameters."))
        return []
    
    progress_queue.put((None, "Parsing data..."))
    data = get_latest_date(data, "orig_served_date") # Formats the data to contain only the most recent date and the info that goes along with it
    data = find_how_long(data) # Adds a key to each dict that shows how long a given company has been with their insurance

    return data
