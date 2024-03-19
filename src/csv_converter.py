from bs4 import BeautifulSoup
import pandas as pd
import os
import glob


def clean_string(s):
    return s.replace('"', '').replace(',', '').strip()

def clean_key_0(data):
    # Use clean_string in the condition to determine indices
    indices = [1, 2, 3] if len(clean_string(data[2])) == 3 else [18, 19, 20]
    
    airline_code = clean_string(data[indices[0]])
    departure_airport_code = clean_string(data[indices[1]])
    destination_airport_code = clean_string(data[indices[2]])
    
    return {
        "airline_code": airline_code,
        "departure_airport_code": departure_airport_code,
        "destination_airport_code": destination_airport_code,
    }


def clean_key_1(data, year_min=2024, year_max=2025):
    # Directly find year indices with a more flexible range
    year_indices = [i for i, item in enumerate(data) if item.isdigit() and year_min <= int(item) <= year_max]
    
    if len(year_indices) < 2:
        return {}, {}  # Not enough data to form dates
    
    # Assuming the structure around years is consistent for departure and arrival dates
    length = year_indices[1] - year_indices[0]
    departure_date = data[year_indices[0]:year_indices[0]+length]
    arrival_date = data[year_indices[1]:year_indices[1]+length]
    
    # Use the clean_string function for consistency
    selling_airline = clean_string(data[1])
    ticket_price = clean_string(data[-1])

    return {
        "selling_airline": selling_airline,
        "ticket_price": ticket_price,
        "departure_date": departure_date,
        "arrival_date": arrival_date
    }



def clean_key_2(data):
    # Use the clean_string helper function to clean the data
    first_part = clean_string(data[3])
    second_part = clean_string(data[6])
    
    # Format and return the first flight code
    first_flight_code = f"{first_part}-{second_part}"
    return {
        "First_flight": first_flight_code
    }


def preprocess_flight_data(data):
    # Initialize variables
    preprocessed_data = []
    temp_group = []

    for entry in data:
        # Skip entries that start with "null" or are exactly "true"
        if entry.startswith('null') or entry == 'true':
            continue
        # Add the entry to the temporary group
        temp_group.append(entry)
        # Check if the temporary group has 5 elements (a complete flight entry)
        if len(temp_group) == 5:
            # Extend the preprocessed_data list with this complete flight entry
            preprocessed_data.extend(temp_group)
            # Reset the temporary group for the next flight entry
            temp_group = []
    
    # Handle any remaining entries in temp_group if they form a complete flight entry
    if len(temp_group) == 5:
        preprocessed_data.extend(temp_group)
    
    return preprocessed_data

# Function to clean Key 3
def clean_key_3(data):
    alphanumeric_entry = ''
    next_entry = ''
    
    # Iterate over the data list with an index so we can access the next element
    for i, entry in enumerate(data):
        cleaned_entry = entry.replace('"', '').strip()
        
        # Check if the current entry is alphanumeric (contains letters)
        if cleaned_entry.isalnum() and not cleaned_entry.isnumeric():
            alphanumeric_entry = cleaned_entry
            
            # Check if there is a next entry in the list
            if i + 1 < len(data):
                # Clean and assign the next entry
                next_entry = data[i + 1].replace('"', '').strip()
            break
    
    # Combine the first alphanumeric entry with the next entry
    combined_entry = alphanumeric_entry + next_entry
    
    return {
        "first_flight_code": combined_entry
    }


def clean_key_3_secondtime(data):
    # Process each journey in steps of 5, ignoring any trailing elements that don't fit the pattern
    for i in range(0, len(data) - len(data) % 5, 5):
        # Extract times, dates, and combined airline information
        departure_time, arrival_time, departure_date, arrival_date, combined_info = data[i:i+5]
        # Correct the time format
        departure_time = departure_time.replace(',', ':')
        arrival_time = arrival_time.replace(',', ':')
        # Split the combined airline information by commas and remove quotes
        
        # Construct the journey information dictionary
        flight_journey = {
            "departure_time": departure_time,
            "arrival_time": arrival_time,
        }
        
    return flight_journey




def clean_key_4(data):
    if len(data) >= 2:
        # Use the clean_string helper function to clean the entries
        first_part = clean_string(data[0])
        second_part = clean_string(data[1])
        
        last_flight_code = first_part + second_part
        return {"last_flight_code": last_flight_code}
    else:
        # Handle the case where data does not contain enough entries
        return {"last_flight_code": "NaN"}




# Main function to process the raw dictionary and output a pandas Series
def process_flight_data(raw_data):
    # Remove irrelevant keys
    raw_data.pop(-1, None)
    raw_data.pop(-2, None)
    
    # Clean and extract information from each key
    general_info = clean_key_0(raw_data[0])
    selling_airline_info = clean_key_1(raw_data[1])
    flights_info = clean_key_2(raw_data[2])
    clean_key3_data = preprocess_flight_data(raw_data[3])
    journey_info = clean_key_3(clean_key3_data)
    journey_info2 = clean_key_3_secondtime(raw_data[3])
    last_flight = clean_key_4(raw_data[4])
    
    cleaned_data = {**general_info, **selling_airline_info, **flights_info, **journey_info,**last_flight,**journey_info2}

    
    # Convert to pandas Series
    cleaned_df = pd.DataFrame([cleaned_data])
    return cleaned_df


def parse_nested_string_v2(s):
    level_dict = {}
    current_str = ""
    open_brackets = 0

    for char in s:
        if char == '[':
            if open_brackets > 0:  # Only add non-empty strings and when not at the root
                current_str = current_str.strip()
                if current_str:  # Add current object to the level before going deeper
                    if open_brackets not in level_dict:
                        level_dict[open_brackets] = []
                    level_dict[open_brackets].append(current_str)
                    current_str = ""
            open_brackets += 1
        elif char == ']':
            current_str = current_str.strip()
            if current_str:  # Add current object to the level before exiting
                if open_brackets not in level_dict:
                    level_dict[open_brackets] = []
                level_dict[open_brackets].append(current_str)
                current_str = ""
            open_brackets -= 1
        elif char == ',':
            current_str = current_str.strip()
            if current_str:  # Add current object to the level and reset for the next object
                if open_brackets not in level_dict:
                    level_dict[open_brackets] = []
                level_dict[open_brackets].append(current_str)
                current_str = ""
        else:
            current_str += char

    # Handle any remaining string outside of the loop
    current_str = current_str.strip()
    if current_str:
        if open_brackets not in level_dict:
            level_dict[open_brackets] = []
        level_dict[open_brackets].append(current_str)

    return level_dict

def add_key_four_if_missing(parsed_dict):
    # Convert keys to integers for comparison since dictionary keys might be strings
    keys_as_ints = [int(key) for key in parsed_dict.keys()]

    # Check if key 4 exists
    if 4 not in keys_as_ints:
        # Check if key 3 exists and has enough elements
        if 3 in keys_as_ints and len(parsed_dict[3]) >= 5:
            # Take the last 5 elements from the list at key 3
            last_five_elements = parsed_dict[3][-5:]
            # Create key 4 with these elements
            parsed_dict[4] = last_five_elements
        else:
            # If key 3 does not exist or doesn't have enough elements, create key 4 with an empty list or a default value
            parsed_dict[4] = []  # Or any default value you see fit

    return parsed_dict

# Function to process a single JSON file
def process_json_file(json_file_path):
    # Assuming parse_nested_string_v2 and other necessary parsing functions are defined elsewhere
    with open(json_file_path, 'r') as json_file:
        short_json_string = json_file.read()
        unescaped_json = bytes(short_json_string, "utf-8").decode("unicode_escape")
        splitted_json = unescaped_json.split("[\\\"")[1:-1]

    Journeys = []
    for journey in splitted_json:
        parsed_journey = parse_nested_string_v2(journey)
        # Assuming add_key_four_if_missing is defined and corrects the parsed journey as needed
        final_journey = add_key_four_if_missing(parsed_journey)
        Journeys.append(final_journey)

    df_json = pd.DataFrame()
    for journey in Journeys:
        temp_df = process_flight_data(journey)  # Assuming this function is defined and processes each journey
        df_json = pd.concat([df_json, temp_df], ignore_index=True)
    
    return df_json

# Function to process a corresponding HTML file
def process_html_file(html_file_path, df_json_length):
    with open(html_file_path, 'r') as html_file:
        soup = BeautifulSoup(html_file, 'html.parser')
    elements = soup.find_all('span', class_='twocKe')
    
    meta_data = {}
    if len(elements) >= 3:  # Assuming there are 3 metadata fields to extract
        meta_data = {
            "Detected_Language": elements[0].text,
            "Detected_Country": elements[1].text,
            "Detected_Currency": elements[2].text
        }
    else:
        print(f"Metadata missing or incomplete in {html_file_path}.")
    
    # Repeat the metadata for each row in df_json
    df_meta = pd.DataFrame([meta_data] * df_json_length)
    return df_meta

# Function to merge JSON and HTML extracted data
def merge_data_frames(df_json, df_html):
    result_df = pd.concat([df_json.reset_index(drop=True), df_html.reset_index(drop=True)], axis=1)
    return result_df

# Main processing loop
def main():
    json_directory_path = '../data/2.crawler_output/json_collections/responses'
    html_directory_path = '../data/2.crawler_output/html_collections/html_pages'
    
    output_directory = '../data/query_results'
    json_files = glob.glob(os.path.join(json_directory_path, '*.json'))

    df_combined = pd.DataFrame()

    for json_file_path in json_files:
        df_json = process_json_file(json_file_path)
        if df_json.empty:
            print(f"No data to concatenate for {json_file_path}")
            continue  # Skip further processing for this file

        base_name = os.path.splitext(os.path.basename(json_file_path))[0]
        html_file_path = os.path.join(html_directory_path, f'{base_name}.html')

        if os.path.exists(html_file_path):
            df_html = process_html_file(html_file_path, len(df_json))
            result_df = merge_data_frames(df_json, df_html)
            df_combined = pd.concat([df_combined, result_df], ignore_index=True)
        else:
            print(f"Corresponding HTML file not found for {json_file_path}")
    
    # Additional data processing steps
    df_combined['ticket_price'] = pd.to_numeric(df_combined['ticket_price'], errors='coerce')
    df_filtered = df_combined[df_combined['ticket_price'] > 2]

    # Save the combined DataFrame to a CSV file
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file_path = os.path.join(output_directory, "Query6_results.csv")
    df_combined.to_csv(output_file_path, index=False)

if __name__ == "__main__":
    main()