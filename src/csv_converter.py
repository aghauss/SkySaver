from bs4 import BeautifulSoup
import pandas as pd
import os
import glob


def clean_key_0(data):
    # Attempt to extract values using the initial indices
    airline_code = data[1].replace('"', '').replace(',', '').strip()
    departure_airport_code = data[2].replace('"', '').replace(',', '').strip()
    destination_airport_code = data[3].replace('"', '').replace(',', '').strip()
    
    # Check if the length of departure_airport_code is not equal to three
    if len(departure_airport_code) != 3:
        # If not, use alternative indices for the extraction
        airline_code = data[18].replace('"', '').replace(',', '').strip()
        departure_airport_code = data[19].replace('"', '').replace(',', '').strip()
        destination_airport_code = data[20].replace('"', '').replace(',', '').strip()
    
    return {
        "airline_code": airline_code,
        "departure_airport_code": departure_airport_code,
        "destination_airport_code": destination_airport_code,
    }

# Function to clean Key 1
def clean_key_1(data):
    # Function to find indices of four-digit integers, representing years
    def find_year_indices(data):
        year_indices = []
        for i, item in enumerate(data):
            try:
                # Check if the item is a four-digit year
                if len(item) == 4 and item.isdigit():
                    year = int(item)
                    if 2024 <= year <= 2025:  # Assuming years of interest are 2024 or 2025
                        year_indices.append(i)
            except ValueError:
                # Item is not an integer or does not meet the year condition
                continue
        return year_indices

    year_indices = find_year_indices(data)
    
    # Ensure there are at least two four-digit years to form departure and arrival dates
    if len(year_indices) < 2:
        return [], []  # Not enough data to form dates

    # Calculate the difference in indices to determine the length of the date lists
    length = year_indices[1] - year_indices[0]

    # Extract departure_date and arrival_date
    departure_date = data[year_indices[0]:year_indices[0]+length]
    arrival_date = data[year_indices[1]:year_indices[1]+length]

    # Assuming second item is always the airline name and the last item is always the ticket price
    selling_airline = data[1].replace('"', '').strip()
    ticket_price = data[-1]

    return {
        "selling_airline": selling_airline,
        "ticket_price": ticket_price,
        "departure_date": departure_date,
        "arrival_date": arrival_date
    }



def clean_key_2(data):
    return {
        "First_flight": data[3].replace('"', '').replace(',', '').strip() + "-" + data[6].replace('"', '').replace(',', '').strip()
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

def c2lean_key_3(data):
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
    # Extracting, cleaning, and merging the first and second entries
    last_flight_code = data[0].replace('"', '').strip() + data[1].replace('"', '').strip()
    return {
        "last_flight_code": last_flight_code
    }



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
    journey_info2 = c2lean_key_3(raw_data[3])
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


json_directory_path = 'data/output/raw_output/json_collections/responses'
html_directory_path = 'data/output/raw_output/html_collections/html_pages'

json_files = glob.glob(os.path.join(json_directory_path, '*.json'))

# Clean Dictionaries
    
column_list = ['airline_code','departure_airport_code','destination_airport_code',"departure_date","arrival_date",
                'ticket_price','First_flight','first_flight_code','last_flight_code','selling_airline', "departure_time","arrival_time",]


meta_column_names = ["Detected_Language", "Assigned_Country", "Assigned_Currency"]

df_combined = pd.DataFrame(columns=column_list + meta_column_names)


for json_file_path in json_files:
    df_json = pd.DataFrame(columns = column_list)
    # Derive the base name without the extension to match the HTML file
    base_name = os.path.splitext(os.path.basename(json_file_path))[0]
    
    # Construct the HTML file path based on the JSON file base name but in the HTML directory
    html_file_path = os.path.join(html_directory_path, base_name + '.html')


    # Check if the corresponding HTML file exists
    if os.path.exists(html_file_path):
        # Load and process the JSON file
        with open(json_file_path, 'r') as json_file:
            short_json_string = json_file.read()

            #Unescaping
            unsecaped_json = bytes(short_json_string, "utf-8").decode("unicode_escape")

            #Splitting
            splitted_json_long = unsecaped_json.split("[\\\"")

            # Deleting first and last entry (for now might be necessary to do more)
            splitted_json = splitted_json_long[1:-1]

            # Create Dictionary per Split

            Journeys = []  # This will hold all the parsed journey dictionaries
            journeys_list = splitted_json  # Your list of journeys to parse

            for journey in journeys_list:
                parsed_journey = parse_nested_string_v2(journey)
                Journeys.append(parsed_journey) 

            for journey in Journeys:
                final_dict = add_key_four_if_missing(journey)    

            for journey in Journeys:
                temp_df = process_flight_data(journey)
                df_json = pd.concat([df_json,temp_df])

            

        for journey in Journeys:
                temp_df = process_flight_data(journey)
                df_json = pd.concat([df_json,temp_df])

        # Add the conditional check here
        if len(df_json) > 0:
            # Load and process the HTML file
            with open(html_file_path, 'r') as html_file:
                soup = BeautifulSoup(html_file, 'html.parser')
                # Find elements by class name
                elements = soup.find_all('span', class_='twocKe')

                if len(elements) == len(meta_column_names):
                    # Extract the text from each element and create a dictionary with it
                    new_row = {meta_column_names[i]: elements[i].text for i in range(len(meta_column_names))}
                    # Convert the dictionary to a DataFrame
                    new_row_df = pd.DataFrame([new_row])
                    # Repeat the metadata row for each journey in 'df_json'
                    df2_repeated = pd.concat([new_row_df]*len(df_json), ignore_index=True).reset_index(drop=True)
                else:
                    print("The number of elements does not match the number of columns.")
                    # Handle the error appropriately, perhaps by skipping this file
                    continue

                # Combine the data from JSON and HTML processing
                # Ensure both DataFrames have the same index before concatenating
                df_json.reset_index(drop=True, inplace=True)
                result_df = pd.concat([df_json, df2_repeated], axis=1)

            # Append the combined data to the 'df_combined' DataFrame
            df_combined = pd.concat([df_combined, result_df], ignore_index=True)
        else:
            print(f"No data to concatenate for {json_file_path}")


# Convert 'ticket_price' to numeric, coercing errors to NaN
df_combined['ticket_price'] = pd.to_numeric(df_combined['ticket_price'], errors='coerce')

# Now filter the DataFrame
df_filtered = df_combined[df_combined['ticket_price'] > 2]

# Define the output directory
output_directory = 'output/'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)


# Save the combined DataFrame to a CSV file in the output directory
output_file_path = os.path.join(output_directory, "Query4_results_datefix.csv")
df_filtered.to_csv(output_file_path, index=False)



