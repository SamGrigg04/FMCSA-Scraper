"""
https://data.transportation.gov/Trucking-and-Motorcoaches/ActPendInsur-All-With-History/qh9u-swkp/about_data
"""

from utils.network_utils import get_json
from utils.data_utils import dataset_rows, get_latest_date
# from ui.interface import progress bar updater


def run(params, headers, config, check_count = True):
    url = "https://data.transportation.gov/resource/qh9u-swkp.json"

    params = params.copy()
    headers = headers.copy()
    data = []

    try:
        rows = dataset_rows(url, params, headers) if check_count else None
    except Exception as e:
        print(f"Error fetching dataset row count for {url}: {e}")
        return []
    print(f'rows: {rows}')


    # If more than 50k rows, pagination is nescessary
    offset = 0
    params["$limit"] = 50000    

    while True:
        params["$offset"] = offset
        try:
            page = get_json(url, params, headers)
        except Exception as e:
            print(f"Error fetching data from {url} at offset {offset}: {e}")
            return []
        if not page:
            break

        for row in page:
            row["dot_number"] = row.get("dot_number", "").zfill(8)

        try:
            data.extend(page)
        except Exception as e:
            print(f"Warning: failed to extend data at offset {offset} for {url}: {e}")
            pass
        offset += len(page)

        print(f'fetched {offset} rows')

        if rows and offset >= rows:
            break

    if not data:
        #TODO: Print a big error message or something
        print("No data fit your parameters.")
        return []
    
    data = get_latest_date(data, "effective_date")

    return data


