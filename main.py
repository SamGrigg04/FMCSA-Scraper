"""
Author: Samuel Grigg
Last Updated: 12/06/2025

Datasets: https://data.transportation.gov/browse?sortBy=relevance&pageSize=20&category=Trucking+and+Motorcoaches&limitTo=datasets

Notes:


"""
from scrapers import act_pend_insur_all_with_history_scraper, auth_hist_all_with_history_scraper, company_census_scraper, carrier_all_with_history_scraper
from utils.config_utils import load_config, load_secrets
from utils.data_utils import combine_lists_dot, has_value, in_date_range
from utils.spreadsheet_utils import write_to_sheets

def main(progress_queue):
    progress_queue.put((0, "Starting..."))

    # load config data
    config = load_config()
    secrets = load_secrets()

    # for error handling later if needed
    parsed_data = None
    data_needed = None

    if config.get("mode") == "state":
        params = {
            "phy_state": config["state"], 
            "carrier_operation": "A", # Interstate
            "status_code": "A" # Active status
            }
        headers = {"X-App-Token": secrets["app_token"]}
        progress_queue.put((0, "Running scraper 1 of 2..."))
        safer_data = company_census_scraper.run(params, headers, progress_queue)

        params = {}
        progress_queue.put((0, "Running scraper 2 of 2..."))
        date_data = act_pend_insur_all_with_history_scraper.run(params, headers, progress_queue)

        progress_queue.put((0, "Parsing data..."))
        combined_data = combine_lists_dot(safer_data, date_data)
        filtered_data = has_value(combined_data, "effective_date")
        # last one always has to be "parsed_data" to put on the spreadsheet
        parsed_data = has_value(filtered_data, "cargo_carried")

        data_needed = [
            "dot_number", 
            "legal_name", 
            "dba_name", 
            "phone", 
            "email_address", 
            "power_units", 
            "total_drivers", 
            "classdef",
            "cargo_carried",
            "effective_date",
            "name_company"
            ]

    elif config.get("mode") == "cancel":
        params = {
            "carrier_operation": "A",
            "status_code": "A"
        }
        headers = {"X-App-Token": secrets["app_token"]}
        progress_queue.put((0, "Running scraper 1 of 2..."))
        safer_data = company_census_scraper.run(params, headers, progress_queue)

        params = {}
        progress_queue.put((0, "Running scraper 2 of 2..."))
        date_data = act_pend_insur_all_with_history_scraper.run(params, headers, progress_queue)

        progress_queue.put((0, "Parsing data..."))
        combined_data = combine_lists_dot(safer_data, date_data)
        parsed_data = has_value(combined_data, "cancl_effective_date")
        parsed_data = in_date_range(parsed_data, "cancl_effective_date", config["start_date"], config["end_date"])

        data_needed = [
            "dot_number", 
            "legal_name", 
            "dba_name", 
            "phone", 
            "email_address", 
            "power_units", 
            "total_drivers", 
            "classdef", 
            "effective_date",
            "cancl_effective_date",
            "name_company"
            ]
        
    elif config.get("mode") == "renew":
        params = {
            "carrier_operation": "A",
            "status_code": "A"
            }
        headers = {"X-App-Token": secrets["app_token"]}
        progress_queue.put((0, "Running scraper 1 of 3..."))
        safer_data = company_census_scraper.run(params, headers, progress_queue)

        params = {}
        progress_queue.put((0, "Running scraper 2 of 3..."))
        date_data = act_pend_insur_all_with_history_scraper.run(params, headers, progress_queue)

        params = {
            "$where": "original_action_desc in ('GRANTED','REINSTATED') AND (disp_action_desc IS NULL OR disp_action_desc in ('TRANSFERRED','TRANSFER CONSUMMATED'))",
        }
        progress_queue.put((0, "Running scraper 3 of 3..."))
        business_data = auth_hist_all_with_history_scraper.run(params, headers, progress_queue) # Gets how long they've been in business
        
        progress_queue.put((0, "Parsing data..."))
        combined_data_1 = combine_lists_dot(safer_data, date_data)
        combined_data_2 = combine_lists_dot(combined_data_1, business_data)
        parsed_data = has_value(combined_data_2, "effective_date")
        parsed_data = has_value(parsed_data, "original_action_desc")
        parsed_data = in_date_range(parsed_data, "effective_date", config["start_date"], config["end_date"])

        data_needed = [
            "dot_number", 
            "legal_name", 
            "dba_name", 
            "phone", 
            "email_address", 
            "power_units", 
            "total_drivers", 
            "classdef", 
            "effective_date",
            "name_company",
            "original_action_desc",
            "orig_served_date",
            "business_duration"
            ]

    elif config.get("mode") == "newVenture":
        params = {
            "$where": "(docket_number LIKE 'MC%') " # Starts with MC
                    "AND dot_number != '00000000' "
                    "AND min_cov_amount != '00000' " # Insurance required
                    "AND bipd_file = '00000' " # No insurance already on file
                    "AND ((common_stat = 'N' AND common_app_pend = 'Y') " # If __ not active and __ is pending
                    "OR (contract_stat = 'N' AND contract_app_pend = 'Y') "
                    "OR (broker_stat = 'N' AND broker_app_pend = 'Y'))"
        }
        headers = {"X-App-Token": secrets["app_token"]}
        progress_queue.put((0, "Running scraper 1 of 2..."))
        venture_data = carrier_all_with_history_scraper.run(params, headers, progress_queue)

        params = {
            "carrier_operation": "A",
            "docket1_status_code":"A",
            "docket1prefix": "MC"
        }
        progress_queue.put((0, "Running scraper 2 of 2..."))
        safer_data = company_census_scraper.run(params, headers, progress_queue)

        progress_queue.put((0, "Parsing data..."))
        combined_data = combine_lists_dot(venture_data, safer_data) 
        parsed_data = has_value(combined_data, "phone")
        
        data_needed = [
            "dot_number", 
            "legal_name", 
            "dba_name", 
            "phone", 
            "email_address", 
            "min_cov_amount",
            "application_pending"
        ]

    # Writes to sheets if there is data and an option selected in config
    if parsed_data and data_needed:
        progress_queue.put((0, "Writing to sheets..."))
        try:
            write_to_sheets(parsed_data, data_needed, config, secrets, progress_queue)
        except Exception as e:
            progress_queue.put((None, f"Error writing to sheets: {e}"))
    elif not config.get("mode"):
        progress_queue.put((None, "config error: no mode enabled in config.json"))
    else:
       progress_queue.put((None, "no data parsed"))

if __name__ == "__main__":
    main()

