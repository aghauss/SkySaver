import base64
import json
import streamlit as st
import pandas as pd
from datetime import datetime, date
from pycaret.classification import load_model as load_classification_model
from pycaret.regression import load_model as load_regression_model

@st.cache_data
def load_mappers(filename):
    with open(filename, "r") as file:
        mappers = json.load(file)
    return mappers

st.set_page_config(page_title='SkySaver', page_icon='logo_background.png',layout= "wide")

# Caching the model loading using the appropriate Streamlit caching command
@st.cache_resource
def load_cached_classification_model():
    return load_classification_model('../models/classification_model')

@st.cache_resource
def load_cached_regression_model():
    return load_regression_model('../models/regression_model')

classification_model = load_cached_classification_model()
regression_model = load_cached_regression_model()

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as file:
        data = file.read()
    return base64.b64encode(data).decode()

def predict(departure_airport_code, destination_airport_code, days_until_departure, detected_country):
    input_data_regression = pd.DataFrame({
        'departure_airport_code': [departure_airport_code],
        'destination_airport_code': [destination_airport_code],
        'Detected_Country': [detected_country],
        'days_until_departure': [days_until_departure]
    })
    
    input_data_classifier = pd.DataFrame({
        'departure_airport_code': [departure_airport_code],
        'destination_airport_code': [destination_airport_code],
        'Detected_Country': [detected_country],
        'days_until_departure': [days_until_departure]
    })

    print("Classifier Input Data:")
    print(input_data_classifier)
    
    classification_prediction = classification_model.predict(input_data_classifier)
    print("Classifier Output:")
    print(classification_prediction)

    if classification_prediction[0] == "No Significant Difference Found":
        regression_prediction = [0]  # Skipping regression model
        print("Regression Model Skipped")
    else:
        print("Regression Input Data:")
        print(input_data_regression)
        
        regression_prediction = regression_model.predict(input_data_regression)
        
        print("Regression Output:")
        print(regression_prediction)
    
    return classification_prediction, regression_prediction

mappers = load_mappers("mappers.json")
# Access a specific mapper
country_mapper = mappers["country_mapper"]
departure_airport_mapper = mappers["departure_airport_mapper"]
destination_airport_mapper = mappers["destination_airport_mapper"]
reverse_country_mapper = mappers["reverse_country_mapper"]


# Create columns to place elements side-by-side
col1, col2 = st.columns([1, 13]) 

# Display the image in the first column with a set width
col1.image('transparent_logo_hd.png', width=100)

# Display the title in the second column
col2.title('SkySaver')

# Additional Markdown for the subtitle
st.markdown("###### Find out how much you could save for your next flight by switching your IP-Location")


# Create a container, then create three columns within that container
with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        departure_city_full_name = st.selectbox("Departure City",list(departure_airport_mapper.keys()), help="From where do you want to departure?.")
     

    with col2:
        destination_city_full_name = st.selectbox("Destination City",list(destination_airport_mapper.keys()) ,help="Enter your destination goal")

    with col3:
        date_range = st.date_input("Select your departure and return dates", [], help="When do you want to travel?")

# Your existing code
if len(date_range) == 2:
    departure_date, return_date = date_range[0], date_range[1]
    current_date = datetime.now().date()
    if departure_date < current_date or return_date < departure_date:
        st.error("Departure and return dates must be in the future and the return date must be after the departure date.")
    else:
        days_until_departure = (departure_date - current_date).days
        detected_country_model_output = st.selectbox("Your current location", country_mapper, help="Country detected from your current location or preference.")

        # Map model output to user-friendly format using the reverse mapper dictionary
        detected_country = reverse_country_mapper.get(detected_country_model_output, detected_country_model_output)

        if st.button("Show Savings Potential"):
            departure_airport_code = departure_airport_mapper.get(departure_city_full_name, "Unknown")
            destination_airport_code = destination_airport_mapper.get(destination_city_full_name, "Unknown")
            with st.spinner('Calculating...'):
                classification_result, regression_result = predict(departure_airport_code, destination_airport_code,days_until_departure ,detected_country)
                

            classification_result_friendly = reverse_country_mapper.get(classification_result[0], classification_result[0])
            

            # Create two columns
            col1, col2 = st.columns(2)

            # Display "Cheapest Country for your Flight" in the first column
           # Display "Cheapest Country for your Flight" in the first column
            with col1:
                st.markdown(f"<h1 style='text-align: left; font-size: 20px;'>Cheapest Country for your Flight</h1>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: left; font-size: 15px;'>{classification_result_friendly}</h1>", unsafe_allow_html=True)
                

            # Display "Saving Potential" in the second column
            with col2:
                if regression_result[0] != 0:  # assuming regression_result = [0] indicates no savings
                    formatted_regression_result = f"{regression_result[0]:.1f}%"
                    st.markdown(f"<h1 style='text-align: left;font-size: 20px;'>Saving Potential</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align: left; font-size: 15px;'>{formatted_regression_result}</h2>",unsafe_allow_html=True)
                    
                else:
                    st.markdown(f"<h1 style='text-align: left;font-size: 20px;'>Saving Potential</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align: left; font-size: 15px;'>0%</h2>",unsafe_allow_html=True)
                  

