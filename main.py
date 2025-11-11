# from ui.interface.py import ___ (lauch tkinter UI)
from scrapers import safer_scraper, effective_date_scraper, auth_scraper
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
        safer_data = safer_scraper.run(params, headers, config)
        params = {}
        date_data = effective_date_scraper.run(params, headers, config)
        combined_data = combine_lists_dot(safer_data, date_data)
        filtered_data = has_value(combined_data, "effective_date")
        parsed_data = has_value(filtered_data, "cargo_carried")

        print(f"Parsed data length: {len(parsed_data)}")
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
        print("running next cancel")
        params = {
            "carrier_operation": "A",
            "status_code": "A"
        }
        headers = {"X-App-Token": secrets["app_token"]}
        safer_data = safer_scraper.run(params, headers, config)
        params = {}
        date_data = effective_date_scraper.run(params, headers, config)
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
        print("running renew")
        params = {
            "carrier_operation": "A",
            "status_code": "A"
            }
        headers = {"X-App-Token": secrets["app_token"]}
        safer_data = safer_scraper.run(params, headers, config)
        params = {}
        date_data = effective_date_scraper.run(params, headers, config)
        business_data = auth_scraper.run(params, headers, config) # Gets how long they've been in business
        combined_data_1 = combine_lists_dot(safer_data, date_data)
        combined_data_2 = combine_lists_dot(combined_data_1, business_data)
        parsed_data = has_value(combined_data_2, "effective_date")
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
            "name_company",
            "original_action_desc",
            "orig_served_date",
            "business_duration"
            ]
    """
    TODO:
    elif config["new_venture"] == "True":
        params = {
            "classdef": "none",
            "application_status": "pending"
        }
        headers = {"X-App-Token": secrets["app_token"]}
        
        application_scraper.run()

        data_needed = [
            "classdef", # I think that's authority. should be none
            "application_status", 
            "insurance_on_file", # could be blank, but better if not i guess

            "current_carrier", 

            # This info might come from the same scraper since they might not have a dot number yet
            "phone", 
            "legal_name",
            "email",
            "cargo", 

            "reinstated_date or if not latest_granted_date", 
        ]
        """

    print("Writing to sheets")
    write_to_sheets(parsed_data, data_needed, config, secrets)

    #TODO: Launch the UI


if __name__ == "__main__":
    main()

