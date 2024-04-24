import argparse
import json
import os
import ast
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.stats import trim_mean


def get_absolute_path(relative_path):
    """
    Converts a relative file path to an absolute path, based on the script's location.
    """
    # Determine the directory of this script:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Debug: Attempting to join script_dir: '{script_dir}' with relative_path: '{relative_path}'")  # Debug print statement
    # Build an absolute path by combining the script's directory with the relative path:
    return os.path.join(script_dir, relative_path)

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


def load_config(filename):
    """
    Loads configuration for a specific filename from a JSON configuration file.
    """
    # Using the get_absolute_path function to find the config file:
    config_file_path = get_absolute_path('../config/preproccessing_config.json')
    with open(config_file_path) as config_file:
        config = json.load(config_file)
    return config.get("data_configurations", {}).get(filename, {})


def load_dataset(df_path):
    """
    Load and return the dataset from the specified path.
    """
    try:
        df = pd.read_csv(df_path)
        return df
    except FileNotFoundError:
        print(f"The file {df_path} was not found.")
        exit(1)


def create_flight_id(df):
    """
    Creates a unique FlightID for each flight based on several columns and removes unnecessary columns.
    """
    id_columns = ['airline_code', 'departure_airport_code', 'destination_airport_code',
                  'First_flight', 'last_flight_code', 'arrival_date', 'departure_date',
                  'departure_time', 'selling_airline', 'arrival_time', 'first_flight_code']
    df['Flight_ID'] = df[id_columns].astype(str).agg('-'.join, axis=1)
    df.drop(['departure_time', 'selling_airline', 'arrival_time'], axis=1, inplace=True)
    return df

def convert_date_columns(df):
    """
    Processes 'arrival_date' and 'departure_date' columns in the DataFrame.
    1. Converts string representations of lists into actual lists using ast.literal_eval.
    2. Cleans the data within these lists using the clean_fifth_element function.
    3. Converts the lists into datetime objects using the convert_list_to_datetime function.
    """
    for col in ['arrival_date', 'departure_date']:
        # Convert string representations to lists
        df[col] = df[col].apply(ast.literal_eval)

        # Clean the lists
        df[col] = clean_fifth_element(df[col])

        # Convert lists to datetime objects
        df[col] = df[col].apply(convert_list_to_datetime)
    
    return df

def load_initial_configuration(filename):
    """
    Loads the initial configuration for the script based on the provided filename.
    This includes loading conversion rates and query dates from the configuration.
    """
    config = load_config(filename)
    conversion_rate_file_path = config.get("conversion_rate_file")
    query_date = config.get("query_date")

    # Resolve the absolute path of the conversion rate file and load it
    conversion_rate_file_absolute_path = get_absolute_path(conversion_rate_file_path)
    with open(conversion_rate_file_absolute_path) as f:
        conversion_rates = json.load(f)
    
    return conversion_rates, query_date

def remove_duplicates_and_erroneous_rows(df):
    """
    Removes duplicates based on a composite key and drops rows with missing or erroneous data.
    - Duplicates are identified based on a composite of 'Flight_ID', 'Detected_Country', 'Detected_Language',
      'Detected_Country' again for emphasis, and 'ticket_price'.
    - Erroneous rows are defined as those missing critical information or having a 'ticket_price' below a threshold.
    """
    # Create a composite key for identifying duplicates
    df["Duplicate_checker"] = (df['Flight_ID'] + df['Detected_Country'] + df["Detected_Language"] +
                               df["Detected_Country"] + df["ticket_price"].astype(str))
    
    # Remove duplicates based on the composite key
    df = df.drop_duplicates(subset='Duplicate_checker', keep='first')
    
    # Drop the temporary duplicate checker column
    df = df.drop(['Duplicate_checker'], axis=1)
    
    # Drop rows missing critical information and with 'ticket_price' below 10
    df.dropna(subset=['Detected_Currency', 'ticket_price', 'Detected_Country'], inplace=True)
    df = df[df['ticket_price'] >= 10]
    
    return df

def convert_to_usd(row, price_col_name, currency_col_name, conversion_rates):
    price = row[price_col_name]
    currency = row[currency_col_name]
    conversion_rate = conversion_rates.get(currency)

    if conversion_rate is None:
        raise ValueError(f"Conversion rate for currency '{currency}' is not available.")
    
    return price * conversion_rate



def convert_prices_to_usd(df, price_column, currency_column, conversion_rates):
    """
    Converts ticket prices from various currencies to USD, using the provided conversion rates.
    """
    df['Price_in_USD'] = df.apply(lambda row: convert_to_usd(row, price_column, currency_column, conversion_rates), axis=1)
    return df


def calculate_commute_time(df, arrival_date_col, departure_date_col):
    """
    Calculates the commute time in minutes.
    """
    df['commute_time'] = (df[arrival_date_col] - df[departure_date_col]).dt.total_seconds() / 60
    return df

def set_query_date_and_calculate_days_until_departure(df, departure_date_col, query_date):
    """
    Sets the query date for the dataset based on a given value and calculates the days until departure.
    """
    # Convert query_date string to datetime object
    df['query_date'] = pd.to_datetime(query_date)
    df['days_until_departure'] = (df[departure_date_col] - df['query_date']).dt.days
    return df


def filter_by_country_variance(df, flight_id_col='Flight_ID', country_col='Detected_Country', min_countries=8):
    """
    Filters the DataFrame to include only those entries where the associated Flight_ID
    has queries from at least `min_countries` different countries.

    Parameters:
    - df: DataFrame to filter.
    - flight_id_col: Name of the column in df that contains Flight_IDs.
    - country_col: Name of the column in df that contains country names.
    - min_countries: Minimum number of unique countries required to keep the Flight_ID in the dataset.

    Returns:
    - DataFrame filtered based on the specified country variance criterion.
    """
    # Count the number of different countries available per Flight_ID
    country_count_per_flight = df.groupby(flight_id_col)[country_col].nunique().reset_index(name='FlightID_in_Countries_Count')

    # Merge this count back into the original DataFrame
    df = df.merge(country_count_per_flight, on=flight_id_col)

    # Filter based on the minimum number of countries criterion
    filtered_df = df[df['FlightID_in_Countries_Count'] >= min_countries]

    return filtered_df


def extract_dates(df):
    df["departure_date_day"] = df["departure_date"].dt.strftime('%d-%m-%Y')
    df["arrival_date_day"] = df["arrival_date"].dt.strftime('%d-%m-%Y')
    return df

def create_journey_id(df):
    df["Journey_route"] = df["departure_airport_code"] + "-" + df["destination_airport_code"]
    df["Journey_ID"] = df["Journey_route"] + ": " + df["departure_date_day"] + " " + df["arrival_date_day"]
    return df

def calculate_FlightID_price_stats(df):
    price_stats = df.groupby('Flight_ID')['Price_in_USD'].agg(['max', 'min'])
    price_stats['max_price_diff_FlightID'] = price_stats['max'] - price_stats['min']
    price_stats.columns = ['max_price_FlightID', 'min_price_FlightID', 'max_price_diff_FlightID']
    price_stats['max_rel_price_diff_FlightID'] = (price_stats['max_price_diff_FlightID'] / price_stats['min_price_FlightID']) * 100
    df = pd.merge(df, price_stats, on='Flight_ID', how='left')
    df["abs_diff_to_min_price_FlightID"] = df["Price_in_USD"] - df["min_price_FlightID"]
    df["rel_diff_to_min_price_FlightID"] = ((df["Price_in_USD"] / df["min_price_FlightID"] ) -1) * 100
    df['rel_price_score_FlightID'] = df['rel_diff_to_min_price_FlightID'] / df['max_rel_price_diff_FlightID']
    return df

def calculate_JourneyID_price_stats(df):    
    price_stats_journey = df.groupby('Journey_ID')['Price_in_USD'].agg(['max', 'min'])
    price_stats_journey['max_abs_diff_JourneyID'] = price_stats_journey['max'] - price_stats_journey['min']
    price_stats_journey.columns = ['max_price_JourneyID', 'min_price_JourneyID', 'max_abs_diff_JourneyID']
    price_stats_journey['max_rel_diff_Journey'] = (price_stats_journey['max_abs_diff_JourneyID'] / price_stats_journey['min_price_JourneyID']) * 100
    df = pd.merge(df,price_stats_journey, on=['Journey_ID'], how='left')
    df["abs_diff_to_min_price_JourneyID"] = df["Price_in_USD"] - df["min_price_JourneyID"]
    df["rel_diff_to_min_price_JourneyID"] = ((df["Price_in_USD"] /df["min_price_JourneyID"] ) -1) * 100
    df['rel_price_score_JourneyID'] = df['rel_diff_to_min_price_JourneyID'] / df['max_rel_diff_Journey']
    return df


def calculate_price_stats_for_JourneyID_same_country(df):
    """
    Calculate price statistics for identical journey IDs within the same query country.

    Parameters:
    - df: DataFrame containing the dataset.

    Returns:
    - DataFrame with additional columns for price statistics.
    """
    price_stats_journey_same_country = df.groupby(['Journey_ID', 'Detected_Country'])['Price_in_USD'].agg(['max', 'min'])
    price_stats_journey_same_country['max_abs_diff_perIDGroup_Journey_same_country'] = price_stats_journey_same_country['max'] - price_stats_journey_same_country['min']
    price_stats_journey_same_country.columns = ['max_journey_same_country', 'min_journey_same_country', 'max_abs_diff_perIDGroup_Journey_same_country']
    price_stats_journey_same_country['max_rel_diff_perIDGroup_Journey_same_country'] = (price_stats_journey_same_country['max_abs_diff_perIDGroup_Journey_same_country'] / price_stats_journey_same_country['min_journey_same_country']) * 100

    df = pd.merge(df, price_stats_journey_same_country, on=['Journey_ID','Detected_Country'], how='left')
    df["price_diff_loc_to_glob_Journey_min"] = df["min_journey_same_country"] - df["min_price_JourneyID"]
    df["rel_price_diff_loc_to_glob_Journey_min"] = (df["price_diff_loc_to_glob_Journey_min"] / df["min_price_JourneyID"]) * 100
    
    return df



def identify_cheapest_location_JourneyID(df):
    cheapest_mask = df['Price_in_USD'] == df['min_price_JourneyID']
    cheapest_journeys = df[cheapest_mask]
    cheapest_locations = cheapest_journeys.groupby('Journey_ID')['Detected_Country'].min().reset_index(name='Cheapest_Location_Journey')
    return df.merge(cheapest_locations, on='Journey_ID', how='left')

def identify_cheapest_location_FlightID(df):
    # Identifying flights with max_rel_price_diff_FlightID < 1.5 and setting their cheapest locations to None
    df['Cheapest_Location_Flight'] = 'No Significant Difference Found'  # Initialize all to None
    flights_with_high_diff = df[df['max_rel_price_diff_FlightID'] >= 1.5]['Flight_ID'].unique()
    
    # Filter the DataFrame for flights with max_rel_price_diff_FlightID >= 1.5 before proceeding with the original logic
    filtered_df = df[df['Flight_ID'].isin(flights_with_high_diff)]
    cheapest_mask = filtered_df['Price_in_USD'] == filtered_df['min_price_FlightID']
    cheapest_flights = filtered_df[cheapest_mask]
    cheapest_locations = cheapest_flights.groupby('Flight_ID')['Detected_Country'].min().reset_index(name='Cheapest_Location_Flight_temp')

    # Merge the original df with the cheapest locations using a temporary column to avoid overwriting the None values
    updated_df = df.merge(cheapest_locations, on='Flight_ID', how='left')
    
    # Now, update the 'Cheapest_Location_Flight' column only where 'Cheapest_Location_Flight_temp' is not null
    updated_df.loc[updated_df['Cheapest_Location_Flight_temp'].notnull(), 'Cheapest_Location_Flight'] = updated_df['Cheapest_Location_Flight_temp']
    updated_df.drop(columns=['Cheapest_Location_Flight_temp'], inplace=True)  # Cleanup the temporary column

    return updated_df




def calculate_average_savings_Journey_route(df):
    average_savings = df.groupby(['Journey_route', 'Detected_Country'])['rel_diff_to_min_price_FlightID'].mean().reset_index(name='average_savings_for_Journey_route_in_Detected_Country')
    return df.merge(average_savings, on=['Journey_route', 'Detected_Country'], how='left')

def determine_mode_cheapest_location(df):
    cheapest_location_counts = df.groupby(['Journey_route', 'Detected_Country', 'Cheapest_Location_Flight']).size().reset_index(name='count_cheapest_location')
    cheapest_location_counts = cheapest_location_counts.sample(frac=1).reset_index(drop=True)
    sorted_counts = cheapest_location_counts.sort_values(['Journey_route', 'Detected_Country', 'count_cheapest_location'], ascending=[True, True, False])
    top_cheapest_location = sorted_counts.groupby(['Journey_route', 'Detected_Country']).first().reset_index()
    top_cheapest_location["Mode_Cheapest_Location_Journey"] = top_cheapest_location["Cheapest_Location_Flight"]
    return df.merge(top_cheapest_location[['Journey_route', 'Detected_Country', 'Mode_Cheapest_Location_Journey']], on=['Journey_route', 'Detected_Country'], how='left')

def determine_mode_cheapest_location_JourneyID(df):
    cheapest_location_counts = df.groupby(['Journey_ID', 'Detected_Country', 'Cheapest_Location_Flight']).size().reset_index(name='count_cheapest_location')
    cheapest_location_counts = cheapest_location_counts.sample(frac=1).reset_index(drop=True)
    sorted_counts = cheapest_location_counts.sort_values(['Journey_ID', 'Detected_Country', 'count_cheapest_location'], ascending=[True, True, False])
    top_cheapest_location = sorted_counts.groupby(['Journey_ID', 'Detected_Country']).first().reset_index()
    top_cheapest_location["Mode_Cheapest_Location_JourneyID"] = top_cheapest_location["Cheapest_Location_Flight"]
    return df.merge(top_cheapest_location[['Journey_ID', 'Detected_Country', 'Mode_Cheapest_Location_JourneyID']], on=['Journey_ID', 'Detected_Country'], how='left')



def calculate_savings_metrics(df):
    # Mean Savings for JourneyID
    mean_savings_journeyID = df.groupby(['Journey_ID', 'Detected_Country'])['rel_diff_to_min_price_FlightID'].mean().reset_index(name='mean_savings_for_JourneyID_in_Detected_Country')
    df = df.merge(mean_savings_journeyID, on=['Journey_ID', 'Detected_Country'], how='left')

    # Trimmed Mean Savings for JourneyID
    trimmed_savings_journeyID = df.groupby(['Journey_ID', 'Detected_Country'])['rel_diff_to_min_price_FlightID'].apply(lambda x: trim_mean(x, proportiontocut=0.1)).reset_index(name='trimmed_mean_savings_for_JourneyID_in_Detected_Country')
    df = df.merge(trimmed_savings_journeyID, on=['Journey_ID', 'Detected_Country'], how='left')

    # Log of Mean Savings for JourneyID
    df['log_mean_savings_for_JourneyID_in_Detected_Country'] = np.log(df['mean_savings_for_JourneyID_in_Detected_Country'] + 1)

    # Mean Savings for JourneyRoute
    mean_savings_journey_route = df.groupby(['Journey_route', 'Detected_Country'])['rel_diff_to_min_price_FlightID'].mean().reset_index(name='mean_savings_for_Journey_route_in_Detected_Country')
    df = df.merge(mean_savings_journey_route, on=['Journey_route', 'Detected_Country'], how='left')

    # Trimmed Mean Savings for JourneyRoute
    trimmed_savings_journey_route = df.groupby(['Journey_route', 'Detected_Country'])['rel_diff_to_min_price_FlightID'].apply(lambda x: trim_mean(x, proportiontocut=0.1)).reset_index(name='trimmed_mean_savings_for_Journey_route_in_Detected_Country')
    df = df.merge(trimmed_savings_journey_route, on=['Journey_route', 'Detected_Country'], how='left')

    # Log of Trimmed Mean Savings for JourneyRoute
    df['log_mean_savings_for_Journey_route_in_Detected_Country'] = np.log(df['trimmed_mean_savings_for_Journey_route_in_Detected_Country'] + 1)

    # Median Savings for JourneyRoute
    median_savings_journey_route = df.groupby(['Journey_route', 'Detected_Country'])['rel_diff_to_min_price_FlightID'].median().reset_index(name='median_savings_for_Journey_route_country')
    df = df.merge(median_savings_journey_route, on=['Journey_route', 'Detected_Country'], how='left')

    # Median Savings for JourneyRoute
    median_savings_JourneyID = df.groupby(['Journey_ID', 'Detected_Country'])['rel_diff_to_min_price_FlightID'].median().reset_index(name='median_savings_for_JourneyID_country')
    df = df.merge(median_savings_JourneyID, on=['Journey_ID', 'Detected_Country'], how='left')

    # Normalized Mean Savings
    df['normalized_mean_savings'] = df[['mean_savings_for_JourneyID_in_Detected_Country', 'median_savings_for_Journey_route_country']].mean(axis=1)
    
    return df



def main():
    parser = argparse.ArgumentParser(description='Preprocess dataset with configuration.')
    parser.add_argument('filename', help='The name of the file to be loaded')
    args = parser.parse_args()

    conversion_rates, query_date = load_initial_configuration(args.filename)

    # Proceed with data loading, cleaning, feature engineering, and exporting...
    #get path to data
    df_path = get_absolute_path(f'../data/3.raw_query_results/{args.filename}')
    df = load_dataset(df_path)

    # Feature Engineering 
    df = create_flight_id(df)
    df = convert_date_columns(df)
    df = remove_duplicates_and_erroneous_rows(df)
    df = convert_prices_to_usd(df, 'ticket_price', 'Detected_Currency', conversion_rates)
    df = calculate_commute_time(df, 'arrival_date', 'departure_date')
    df = set_query_date_and_calculate_days_until_departure(df, 'departure_date', query_date)
    df = filter_by_country_variance(df,min_countries=7)
    df = extract_dates(df)
    df = create_journey_id(df)
    df = calculate_FlightID_price_stats(df)
    df = calculate_JourneyID_price_stats(df)
    df = identify_cheapest_location_FlightID(df)
    df = identify_cheapest_location_JourneyID(df)
    df = calculate_price_stats_for_JourneyID_same_country(df)
    df = calculate_average_savings_Journey_route(df)
    df = determine_mode_cheapest_location(df)
    df = determine_mode_cheapest_location_JourneyID(df)
    df = calculate_savings_metrics(df)


    # Export data
    Output_path = get_absolute_path(f'../data/4.processed_data/Processed_{args.filename}')
    df.to_csv(Output_path, index=False)

if __name__ == "__main__":
    main()
