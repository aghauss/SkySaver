import streamlit as st
import pandas as pd
from datetime import datetime, date
from pycaret.classification import load_model as load_classification_model
from pycaret.regression import load_model as load_regression_model

# Caching the model loading using the appropriate Streamlit caching command
@st.cache_resource
def load_cached_classification_model():
    return load_classification_model('../models/classification_model')

@st.cache_resource
def load_cached_regression_model():
    return load_regression_model('../models/regression_model')

classification_model = load_cached_classification_model()
regression_model = load_cached_regression_model()

# Prediction function remains uncached
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
        'Detected_Country': [detected_country]
    })

    classification_prediction = classification_model.predict(input_data_classifier)

    if classification_prediction[0] == "No Significant Difference Found":
        regression_prediction = [0]  # Skipping regression model
    else:
        regression_prediction = regression_model.predict(input_data_regression)
    
    return classification_prediction, regression_prediction

st.title("SkySaver")
st.subheader("Find out how much you could save for your next flight by switching your IP-Location")

departure_airport_code = st.text_input("Departure Airport Code", help="Enter the 3-letter airport code.")
destination_airport_code = st.text_input("Destination Airport Code", help="Enter the 3-letter airport code.")

# Using a date input for selecting both departure and return dates, ensuring they're chosen
date_range = st.date_input("Select your departure and return dates", [], help="Select your departure and return dates.")

if len(date_range) == 2:
    departure_date, return_date = date_range[0], date_range[-1]
    current_date = datetime.now().date()
    if departure_date < current_date or return_date < departure_date:
        st.error("Departure and return dates must be in the future and the return date must be after the departure date.")
    else:
        # Calculate days until departure
        days_until_departure = (departure_date - date.today()).days
        detected_country = st.text_input("Detected Country", help="Country detected from your current location or preference.")

        if st.button("Show Savings Potential"):
            with st.spinner('Calculating...'):
                classification_result, regression_result = predict(departure_airport_code, destination_airport_code, days_until_departure, detected_country)
            st.success("Calculation complete!")
            st.metric(label="Cheapest Country for your Flight", value=classification_result[0])
            if regression_result:
                formatted_regression_result = f"{regression_result[0]:.1f}%"
                st.metric(label="Saving Potential", value=formatted_regression_result)
            else:
                st.metric(label="Saving Potential", value="N/A")
