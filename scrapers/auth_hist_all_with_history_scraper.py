from utils.network_utils import get_json
from utils.data_utils import dataset_rows, get_latest_date, find_how_long
# from ui.interface import progress bar updater



def run(params, headers, config, check_count = True):
    url = "https://data.transportation.gov/resource/9mw4-x3tu.json"

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

        for row in data:
            row["dot_number"] = row.get("dot_number", "").zfill(8)

        data.extend(page)
        offset += len(page)

        print(f'fetched {offset} rows')

        if rows and offset >= rows:
            break

    if not data:
        #TODO: Print a big error message or something
        print("No data fit your parameters.")
        return []
    
    print("Parsing Data")
    data = get_latest_date(data, "orig_served_date")
    data = find_how_long(data)

    return data
