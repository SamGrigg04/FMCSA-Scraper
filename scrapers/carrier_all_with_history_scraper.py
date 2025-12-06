"""
https://data.transportation.gov/Trucking-and-Motorcoaches/Carrier-All-With-History/6eyk-hxee/about_data
"""

from utils.network_utils import get_json
from utils.data_utils import dataset_rows, sort_dot, pending_app

def run(params, headers, progress_queue, check_count = True):
    url = "https://data.transportation.gov/resource/6eyk-hxee.json"

    params = params.copy()
    headers = headers.copy()
    data = []

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
    data = pending_app(data)
    data = sort_dot(data)
    
    return data