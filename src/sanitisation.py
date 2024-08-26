import json


# Load the JSON file
def load_country_names(file_path):
    with open(file_path, 'r') as file:
        country_mapping = json.load(file)
    return country_mapping


simplified_names = load_country_names('input/simpler_countries.json')


def get_simplified_name(country_code: str, country_name: str):
    return simplified_names.get(country_code, country_name)
