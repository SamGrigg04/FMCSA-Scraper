# from ui.interface.py import ___ (lauch tkinter UI)
from scrapers import act_pend_insur_all_with_history_scraper, auth_hist_all_with_history_scraper, company_census_scraper
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
    """
    TODO:
    # Pending Application
    # No Authority Granted
    # No insurance on file

    elif config["new_venture"] == "True":
        params = {
            "classdef": "none",
            "application_status": "pending"
        }
        headers = {"X-App-Token": secrets["app_token"]}
        
        application_scraper.run()

        data_needed = [
            # Application Status (pending)
            # Authority Granted (none)
            # Insurance on File (none)
            # Company Name
            # Email
            # Phone Number
            # Most Recent Authority Granted/Reinstated Date
            # Cargo Carried

            # dot number
        ]
        """

    print("Writing to sheets")
    write_to_sheets(parsed_data, data_needed, config, secrets)

    #TODO: Launch the UI


if __name__ == "__main__":
    main()

