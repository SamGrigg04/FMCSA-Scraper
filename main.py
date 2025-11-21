"""
Author: Samuel Grigg
Last Updated: 11/17/2025

Datasets: https://data.transportation.gov/browse?sortBy=relevance&pageSize=20&category=Trucking+and+Motorcoaches&limitTo=datasets

Notes:


"""


# from ui.interface.py import ___ (lauch tkinter UI)
from scrapers import act_pend_insur_all_with_history_scraper, auth_hist_all_with_history_scraper, company_census_scraper, carrier_all_with_history_scraper
from utils.config_utils import load_config, load_secrets
from utils.data_utils import combine_lists_dot, has_value, in_date_range
from utils.spreasheet_utils import write_to_sheets

def main():
    # load config data
    config = load_config()
    secrets = load_secrets()

    if config["state_spreadsheet"] == "True":
        params = {
            "phy_state": config["state"], 
            "carrier_operation": "A", # Interstate
            "status_code": "A" # Active status
            }
        headers = {"X-App-Token": secrets["app_token"]}
        safer_data = company_census_scraper.run(params, headers, config)
        params = {}
        date_data = act_pend_insur_all_with_history_scraper.run(params, headers, config)
        combined_data = combine_lists_dot(safer_data, date_data)
        filtered_data = has_value(combined_data, "effective_date")
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

    elif config["next_cancel"] == "True":
        params = {
            "carrier_operation": "A",
            "status_code": "A"
        }
        headers = {"X-App-Token": secrets["app_token"]}
        safer_data = company_census_scraper.run(params, headers, config)
        params = {}
        date_data = act_pend_insur_all_with_history_scraper.run(params, headers, config)
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
        
    elif config["renew"] == "True":
        params = {
            "carrier_operation": "A",
            "status_code": "A"
            }
        headers = {"X-App-Token": secrets["app_token"]}
        safer_data = company_census_scraper.run(params, headers, config)
        params = {}
        date_data = act_pend_insur_all_with_history_scraper.run(params, headers, config)
        params = {
            "$where": "original_action_desc in ('GRANTED','REINSTATED') AND (disp_action_desc IS NULL OR disp_action_desc in ('TRANSFERRED','TRANSFER CONSUMMATED'))",
        }
        business_data = auth_hist_all_with_history_scraper.run(params, headers, config) # Gets how long they've been in business
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

    elif config["new_venture"] == "True":
        params = {
            "$where": "(docket_number LIKE 'MC%') " # Starts with MC
                    "AND (common_stat = 'N' OR contract_stat = 'N' OR broker_stat = 'N') " # Not active
                    "AND ((common_stat = 'N' AND common_app_pend = 'Y') " # If __ not active and __ is pending
                    "OR (contract_stat = 'N' AND contract_app_pend = 'Y') "
                    "OR (broker_stat = 'N' AND broker_app_pend = 'Y')) "
                    "AND min_cov_amount > 0 " # Insurance required
                    "AND bipd_file = 0" # No insurance already on file
        }
        headers = {"X-App-Token": secrets["app_token"]}
        venture_data = carrier_all_with_history_scraper.run(params, headers, config)
        params = {}
        safer_data = company_census_scraper(params, headers, config)
        parsed_data = combine_lists_dot(venture_data, safer_data) # last one always has to be parsed data to put on the spreadsheet

        data_needed = [
            "dot_number", 
            "legal_name", 
            "dba_name", 
            "phone", 
            "email_address", 
            "name_company",
            "classdef",
            "application_pending"
        ]

    print("Writing to sheets")
    write_to_sheets(parsed_data, data_needed, config, secrets)

    #TODO: Launch the UI


if __name__ == "__main__":
    main()

