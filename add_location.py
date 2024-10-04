import pandas as pd
from geopy.geocoders import Nominatim
import time

# Load the original CSV file
file_path = 'Traffic_Volume_Counts_20241004.csv'  # 修改为您的本地文件路径
data = pd.read_csv(file_path)

# Initialize geolocator
geolocator = Nominatim(user_agent="geo_locator")

# Function to get latitude and longitude
def get_lat_lon(place_name):
    # Check if the place name has been processed before
    if place_name in coordinates_dict:
        return coordinates_dict[place_name]
    
    try:
        print(place_name)
        location = geolocator.geocode(f"{place_name}, New York, USA")
        if location:
            coordinates_dict[place_name] = (location.latitude, location.longitude)
            return coordinates_dict[place_name]
    except:
        coordinates_dict[place_name] = (None, None)
    
    return (None, None)

# Initialize a dictionary to store coordinates for each unique place name
coordinates_dict = {}

# Iterate through the dataset and get coordinates for each place name
data['Latitude'] = None
data['Longitude'] = None

# Attempt to get coordinates for each place name
for index, row in data.iterrows():
    lat, lon = get_lat_lon(row['Roadway Name'])
    data.at[index, 'Latitude'] = lat
    data.at[index, 'Longitude'] = lon
    # Print progress and add delay to avoid overwhelming the geolocation API
    if index % 10 == 0:  # Print progress every 10 rows
        print(f"Processed {index} rows.")
    # time.sleep(1)

# Save the updated dataset for future use
data.to_csv('Traffic_Volume_Counts_20241004_with_Coordinates.csv', index=False)
