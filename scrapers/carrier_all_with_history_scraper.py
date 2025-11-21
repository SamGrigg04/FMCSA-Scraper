"""
https://data.transportation.gov/Trucking-and-Motorcoaches/Carrier-All-With-History/6eyk-hxee/about_data
"""

from utils.network_utils import get_json
from utils.data_utils import dataset_rows, sort_dot
# from ui.interface import progress bar updater


def run(params, headers, config, check_count = True):
    url = "https://data.transportation.gov/resource/6eyk-hxee.json"

    params = params.copy()
    headers = headers.copy()
    data = []

    rows = dataset_rows(url, params, headers) if check_count else None
    print(f'rows: {rows}')


    # If more than 50k rows, pagination is nescessary
    offset = 0
    params["$limit"] = 50000    

    while True:
        params["$offset"] = offset
        page = get_json(url, params, headers)
        if not page:
            break

        data.extend(page)
        offset += len(page)

        # what application(s) is pending

        print(f'fetched {offset} rows')

        if rows and offset >= rows:
            break

    if not data:
        #TODO: Print a big error message or something
        print("No data fit your parameters.")
        return []
    
    data = sort_dot(data)
    
    return data