import json
import csv
import os
from shapely.geometry import shape
from shapely.wkt import dumps
from shapely.geometry.base import BaseGeometry

from sanitisation import get_simplified_name

# File paths
input_geojson = 'input/world-administrative-boundaries.geojson'
output_csv = 'output/country-wkt.csv'

# Ensure the output directory exists
output_dir = os.path.dirname(output_csv)
os.makedirs(output_dir, exist_ok=True)


# Function to simplify geometries
def simplify_geometry(geometry: BaseGeometry, tolerance: float) -> BaseGeometry:
    return geometry.simplify(tolerance, preserve_topology=True)


# Load GeoJSON data
with open(input_geojson, 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# Extract and convert data to a list of tuples (country_name, wkt_representation)
data = []

# Works for most of them
MAGIC_TOLERANCE_VALUE = 0.05
# Some countries produce >50k characters which is more than google sheets allows in a cell
MAGIC_REDUCTION_VALUES = {
    "Russian Federation": 0.9,
    "United States of America": 0.3,
    "Greenland": 0.3,
    "Chile": 0.1,
    "Indonesia": 0.1
}

def simplify_big_countries(country: str) -> float:
    if country in MAGIC_REDUCTION_VALUES:
        return MAGIC_REDUCTION_VALUES[country]
    else:
        return MAGIC_TOLERANCE_VALUE


for feature in geojson_data['features']:
    country_name = feature['properties']['name']
    country_code = feature['properties']['iso3']
    geometry = shape(feature['geometry'])
    tolerance = simplify_big_countries(country_name)
    simplified_geometry = simplify_geometry(geometry, tolerance)
    wkt_representation = dumps(simplified_geometry)

    # Ensure the WKT is within the character limit
    if len(wkt_representation) > 50000:
        print(
            f"Warning: WKT for {country_name} exceeds 50,000 characters after simplification: {len(wkt_representation)}")

    if not country_name == "Canada":
        data.append((get_simplified_name(country_code, country_name), wkt_representation))
    else:
        # Canada is still too big so use another geography I found somewhere
        with open('input/blame-canada.txt', 'r', encoding='utf-8') as file:
            smaller_canada_wkt = file.read()
            data.append(("Canada", smaller_canada_wkt))

# Sort the data by country name alphabetically
data.sort(key=lambda x: x[0])

# Write the sorted data to the CSV file
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write header
    csvwriter.writerow(['country', 'wkt'])

    # Write sorted rows to CSV
    csvwriter.writerows(data)

print(f"WKT data has been successfully written and sorted to {output_csv}")
