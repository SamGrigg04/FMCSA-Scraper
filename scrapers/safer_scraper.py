from utils.network_utils import get_json
from utils.data_utils import dataset_rows, format_phone, format_cargo
# from ui.interface import progress bar updater



def run(params, headers, config, check_count = True):
    # This is the API we're hitting
    url = "https://data.transportation.gov/resource/az4n-8mr2.json"
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

        for row in page:
            row["dot_number"] = row.get("dot_number", "").zfill(8)
            format_cargo(row)
            row["phone"] = format_phone(row.get("phone", ""))

        data.extend(page)
        offset += len(page)

        print(f'fetched {offset} rows')

        if rows and offset >= rows:
            break

    if not data:
        print("No data fit your parameters.")
        #TODO: Print a big error message or something
        return []

    return data


