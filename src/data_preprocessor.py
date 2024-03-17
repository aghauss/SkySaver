import pandas as pd
import numpy as np
import ast
import argparse
from datetime import datetime


def convert_to_usd(row, price_col_name, currency_col_name):
    price = row[price_col_name]
    currency = row[currency_col_name]
    price = row['ticket_price']
    conversion_rate = conversion_rates.get(currency)

    # Check if conversion_rate is None
    if conversion_rate is None:
        # Handle the error (e.g., return 0, raise an exception, or use a default conversion rate)
        raise ValueError(f"Conversion rate for currency '{currency}' is not available.")
        # Alternatively, you can return 0 or some default value instead of raising an error
        # return 0
    
    return price * conversion_rate


def convert_us_formatted_list_to_datetime(date_list):
    # Convert 'null' or empty strings to 0 and other elements to integers
    date_list = [0 if element in ['null', ''] else int(element) for element in date_list]
    
    try:
        # Assuming date_list is in the format [MM, DD, YYYY, hour (optional), minute (optional)]
        # and you want to handle lists with optional time components
        if len(date_list) == 3:
            # Only date components are present
            return datetime(month=date_list[0], day=date_list[1], year=date_list[2])
        elif len(date_list) == 5:
            # Both date and time components are present
            return datetime(month=date_list[0], day=date_list[1], year=date_list[2], hour=date_list[3], minute=date_list[4])
        elif len(date_list) == 4:
            # Date and either hour or minute is present, assuming hour is given and setting default for minute
            return datetime(month=date_list[0], day=date_list[1], year=date_list[2], hour=date_list[3], minute=0)
        else:
            # Return None for lists of unexpected length to indicate an issue
            return None
    except TypeError as e:
        # Handle cases where the list contents cannot be directly unpacked into datetime
        print(f"Error converting list to datetime: {e}")
        return None
    except ValueError as e:
        # Handle cases where the conversion fails due to incorrect values (e.g., invalid dates like February 30th)
        print(f"Invalid date value in the list: {e}")
        return None



def convert_list_to_datetime(date_list):
    # Convert 'null' strings to 0 and other elements to integers
    date_list = [0 if element == 'null' else int(element) for element in date_list]
    
    try:
        if len(date_list) == 5:
            # If all components are present, unpack the list directly into datetime
            return datetime(*date_list)
        elif len(date_list) == 4:
            # If the minute is missing (or any single component), append 0 for minutes and then convert
            return datetime(*(date_list + [0]))
        else:
            # Return None for lists of unexpected length to indicate an issue
            return None
    except TypeError:
        # Handle cases where the list contents cannot be directly unpacked into datetime
        return None

def clean_fifth_element(lst):
    cleaned_lst = []
    for item in lst:
        if len(item) >= 5:
            fifth_element = item[4]
            if isinstance(fifth_element, int):
                cleaned_lst.append(item[:4] + [fifth_element] + item[5:])
            else:
                try:
                    cleaned_lst.append(item[:4] + [int(fifth_element)] + item[5:])
                except ValueError:
                    # If the fifth element cannot be converted to an integer, replace it with 0
                    cleaned_lst.append(item[:4] + [0] + item[5:])
        else:
            # If the list is too short, consider the fifth element as 0
            cleaned_lst.append(item[:4] + [0])
    return cleaned_lst

conversion_rates = {
    'CHF': 1.14,  # 1 CHF = 1.134556 USD as of Feb 20, 2024, according to X-Rates
    'TRY': 0.032,   # 1 TRY = 0.03230 USD as of Feb 21, 2024, according to Wise
    'PLN': 0.25,  # 1 PLN = 0.250338 USD as of Feb 21, 2024, according to Xe.com
    'GBP': 1.26,      # Example rate, adjust with the actual rate when available
    'JOD': 1.41,      
    'AUD' : 0.66,
    'BRL' : 0.2,
    'IDR' : 0.000064,
    'USD' : 1.0,
    'EUR' : 1.08,
    'ALL' : 0.010,
    'JPY' : 0.0066,
    'BDT' : 0.0091,
}

conversion_rates_new = {
    "CHF": 1.1345485196501948,
    "TRY": 0.032438522553027406,
    "PLN": 0.24811059907834102,
    "GBP": 1.2578704514923194,
    "AUD": 0.6519343706484229,
    "BRL": 0.20107934492353083,
    "IDR": 0.000064,
    'JOD': 1.41,
    "EUR": 1.0768,
    "ALL": 0.011,
    "JPY": 0.006651840869780084,
    "BDT": 0.0091,
    "USD": 1.0
}

# Initialize the parser
parser = argparse.ArgumentParser(description='Load a CSV file that will be preproccessed. The output will be a csv with more features.')
# Add the 'filename' argument
parser.add_argument('filename', help='The name of the file to be loaded from the folder')
# Parse the command line arguments
args = parser.parse_args()

# Construct the file path using the 'filename' argument
file_path = f'../data/3.raw_query_results/{args.filename}.csv'

# Read and Clean Dataset

df = pd.read_csv(file_path)

for i in ['arrival_date','departure_date']:
    df[i] = df[i].apply(ast.literal_eval)

df['arrival_date'] = clean_fifth_element(df['arrival_date'])
df['departure_date'] = clean_fifth_element(df['departure_date'])
for i in ['arrival_date','departure_date']:
    df[i] = df[i].apply(convert_list_to_datetime)

#Create identifier (FlightID) for identical flights**
df['Flight_ID'] = df[['airline_code', 'departure_airport_code', 'destination_airport_code','First_flight','last_flight_code','arrival_date','departure_date', 'departure_time','selling_airline','arrival_time','first_flight_code']].astype(str).agg('-'.join, axis=1)
df = df.drop(['departure_time','selling_airline','arrival_time'], axis = 1)
#Remove duplicates**
df["Duplicate_checker"] = df['Flight_ID'] + df['Detected_Country'] + df["Detected_Language"] + df["Detected_Country"] + str(df["ticket_price"])
df_reduced = df.drop_duplicates(subset='Duplicate_checker', keep='first').copy()
df_reduced = df_reduced.drop(['Duplicate_checker'], axis = 1)
#Remove NaN and erroneous rows**
df_reduced.dropna(subset=['Detected_Currency', 'ticket_price', 'Detected_Country'], inplace=True)
df_reduced = df_reduced[df_reduced['ticket_price'] >= 10]

# Feature engineering
df_reduced['Price_in_USD'] = df_reduced.apply(lambda row: convert_to_usd(row, 'ticket_price', 'Detected_Currency'), axis=1)

#Creating commutime time

df_reduced['commute_time'] = (df_reduced['arrival_date'] - df_reduced['departure_date']).dt.total_seconds() / 60
df_reduced['query_date'] = pd.Timestamp('2024-03-15')
df_reduced['days_until_departure'] = (df_reduced['departure_date'] - df_reduced['query_date']).dt.days

#Eliminating queries with little country variance

# Count the number of different countries available per Flight_ID
country_count_per_flight = df_reduced.groupby('Flight_ID')['Detected_Country'].nunique().reset_index(name='FlightID_in_Countries_Count')

# Merge this count back into the original dataframe
df_reduced = df_reduced.merge(country_count_per_flight, on='Flight_ID')

df_reduced = df_reduced[df_reduced['FlightID_in_Countries_Count'] >= 8]
#Creating Journey_ID: Identifier for identical journeys (same departure and destination airport) on same days

#Extracting departure and arrival days
df_reduced["departure_date_day"] = df_reduced["departure_date"].dt.strftime('%d-%m-%Y')
df_reduced["arrival_date_day"] = df_reduced["arrival_date"].dt.strftime('%d-%m-%Y')

#Creating column for whole Journey
df_reduced["Journey_route"] = df_reduced["departure_airport_code"] + "-" + df_reduced["destination_airport_code"]
df_reduced["Journey_ID"] = df_reduced["Journey_route"] + ": " + df_reduced["departure_date_day"] + " "  + df_reduced["arrival_date_day"]

#Creating Variables that analyse price differences between identical Flights**
# Group by Flight_ID and calculate max, min prices and their absolute difference
price_stats = df_reduced.groupby('Flight_ID')['Price_in_USD'].agg(['max', 'min'])
price_stats['max_price_diff_FlightID'] = price_stats['max'] - price_stats['min']
price_stats.columns = ['max_price_FlightID', 'min_price_FlightID', 'max_price_diff_FlightID']

# Calculate the relative difference as a percentage of the min price
price_stats['max_rel_price_diff_FlightID'] = (price_stats['max_price_diff_FlightID'] / price_stats['min_price_FlightID']) * 100
df_reduced = pd.merge(df_reduced, price_stats, on='Flight_ID', how='left')
df_reduced["abs_diff_to_min_price_FlightID"] = df_reduced["Price_in_USD"] - df_reduced["min_price_FlightID"]
df_reduced["rel_diff_to_min_price_FlightID"] = ((df_reduced["Price_in_USD"] /df_reduced["min_price_FlightID"] ) -1) * 100
df_reduced['rel_price_score_FlightID'] = df_reduced['rel_diff_to_min_price_FlightID'] / df_reduced['max_rel_price_diff_FlightID']


#Creating Variables that analyse price differences between identical Journey**
# Group by Flight_ID and calculate max, min prices and their absolute difference
price_stats_journey = df_reduced.groupby('Journey_ID')['Price_in_USD'].agg(['max', 'min'])
price_stats_journey['max_abs_diff_JourneyID'] = price_stats_journey['max'] - price_stats_journey['min']
price_stats_journey.columns = ['max_price_JourneyID', 'min_price_JourneyID', 'max_abs_diff_JourneyID']
price_stats_journey['max_rel_diff_Journey'] = (price_stats_journey['max_abs_diff_JourneyID'] / price_stats_journey['min_price_JourneyID']) * 100
df_reduced = pd.merge(df_reduced, price_stats_journey, on='Journey_ID', how='left')
df_reduced["abs_diff_to_min_price_JourneyID"] = df_reduced["Price_in_USD"] - df_reduced["min_price_JourneyID"]
df_reduced["rel_diff_to_min_price_JourneyID"] = ((df_reduced["Price_in_USD"] /df_reduced["min_price_JourneyID"] ) -1) * 100
df_reduced['rel_price_score_JourneyID'] = df_reduced['rel_diff_to_min_price_JourneyID'] / df_reduced['max_rel_diff_Journey']

#Creating Variables that analyse price differences between identical Journey within the same query-country**
price_stats_journey_same_country = df_reduced.groupby(['Journey_ID', 'Detected_Country'])['Price_in_USD'].agg(['max', 'min'])
price_stats_journey_same_country['max_abs_diff_perIDGroup_Journey_same_country'] = price_stats_journey_same_country['max'] - price_stats_journey_same_country['min']
price_stats_journey_same_country.columns = ['max_journey_same_country', 'min_journey_same_country', 'max_abs_diff_perIDGroup_Journey_same_country']
price_stats_journey_same_country['max_rel_diff_perIDGroup_Journey_same_country'] = (price_stats_journey_same_country['max_abs_diff_perIDGroup_Journey_same_country'] / price_stats_journey_same_country['min_journey_same_country']) * 100

df_reduced = pd.merge(df_reduced, price_stats_journey_same_country, on=['Journey_ID','Detected_Country'], how='left')
df_reduced["price_diff_loc_to_glob_Journey_min"] = df_reduced["min_journey_same_country"] - df_reduced["min_price_JourneyID"]
df_reduced["rel_price_diff_loc_to_glob_Journey_min"] = (df_reduced["price_diff_loc_to_glob_Journey_min"] / df_reduced["min_price_JourneyID"]) * 100


# Step 1: Filter to get rows where Price_in_USD equals the min for each Journey_ID
cheapest_mask_journey = df_reduced['Price_in_USD'] == df_reduced['min_price_JourneyID']
cheapest_journeys = df_reduced[cheapest_mask_journey]

# Group by Flight_ID and select the first Detected_Country name alphabetically
cheapest_locations_journey = cheapest_journeys.groupby('Journey_ID')['Detected_Country'].min().reset_index()

# Rename the column for clarity
cheapest_locations_journey.rename(columns={'Detected_Country': 'Cheapest_Location_Journey'}, inplace=True)

# Step 2: Merge this information back with the original DataFrame
df_reduced = df_reduced.merge(cheapest_locations_journey, on='Journey_ID', how='left')



#Creating Variables that analyse price differences between identical Flights within the same query-country**
cheapest_mask = df_reduced['Price_in_USD'] == df_reduced['min_price_FlightID']
cheapest_flights = df_reduced[cheapest_mask]
# Group by Flight_ID and select the first Detected_Country name alphabetically
cheapest_locations = cheapest_flights.groupby('Flight_ID')['Detected_Country'].min().reset_index()
# Rename the column for clarity
cheapest_locations.rename(columns={'Detected_Country': 'Cheapest_Location_Flight'}, inplace=True)
# Step 2: Merge this information back with the original DataFrame
df_reduced = df_reduced.merge(cheapest_locations, on='Flight_ID', how='left')


# Calculate the average of rel_diff_to_min_price_FlightID for each Journey_ID and Detected_Country
average_savings_route = df_reduced.groupby(['Journey_route', 'Detected_Country'])['rel_diff_to_min_price_FlightID'].mean().reset_index(name='average_savings_for_Journey_route_in_Detected_Country')
# Merge the average_savings DataFrame back into df_reduced
df_reduced = df_reduced.merge(average_savings_route, on=['Journey_route', 'Detected_Country'], how='left')

cheapest_location_counts = df_reduced.groupby(['Journey_route', 'Detected_Country', 'Cheapest_Location_Flight']).size().reset_index(name='count_cheapest_location')
# Ensure a randomized selection in case of ties by shuffling
cheapest_location_counts = cheapest_location_counts.sample(frac=1).reset_index(drop=True)
cheapest_location_counts_sorted = cheapest_location_counts.sort_values(['Journey_route', 'Detected_Country', 'count_cheapest_location'], ascending=[True, True, False])
top_cheapest_location = cheapest_location_counts_sorted.groupby(['Journey_route', 'Detected_Country']).first().reset_index()
top_cheapest_location["Mode_Cheapest_Location_Journey"] = top_cheapest_location["Cheapest_Location_Flight"]
df_reduced = df_reduced.merge(top_cheapest_location[['Journey_route', 'Detected_Country', 'Mode_Cheapest_Location_Journey']], on=['Journey_route', 'Detected_Country'], how='left')


file_path = f'../data/4.processed_data/{args.filename}_processed.csv'

df_reduced.to_csv(file_path, index=False)