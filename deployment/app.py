import streamlit as st
import pandas as pd
from datetime import datetime
from datetime import date
from pycaret.classification import load_model as load_classification_model
from pycaret.regression import load_model as load_regression_model

# Caching the model loading using the appropriate Streamlit caching command
@st.cache_resource
def load_cached_classification_model():
    return load_classification_model('../models/country_gbc_model_v0.1')

@st.cache_resource
def load_cached_regression_model():
    return load_regression_model('../models/savings_extra_trees_model_v0.1')

classification_model = load_cached_classification_model()
regression_model = load_cached_regression_model()

# Since st.cache_resource or st.cache_data cannot be directly used for caching function outputs like predictions,
# the prediction function remains uncached. Consider optimizing the model or input handling if performance is an issue.
def predict(departure_airport_code, destination_airport_code, days_until_departure, detected_country):
    input_data = pd.DataFrame({
        'departure_airport_code': [departure_airport_code],
        'destination_airport_code': [destination_airport_code],
        'days_until_departure': [days_until_departure],
        'Detected_Country': [detected_country]
    })

    classification_prediction = classification_model.predict(input_data)

    if classification_prediction[0] == "No Differences":
        regression_prediction = [0]  # Skipping regression model
    else:
        regression_prediction = regression_model.predict(input_data)
    
    return classification_prediction, regression_prediction

st.title("SkySaver")
st.subheader("Find out how much you could save for your next flight by switching your IP-Location")

departure_airport_code = st.text_input("Departure Airport Code", help="Enter the 3-letter airport code.")
destination_airport_code = st.text_input("Destination Airport Code", help="Enter the 3-letter airport code.")

# Using a date input for selecting both departure and return dates
date_range = st.date_input("Select your departure and return dates", [], help="Select your departure and return dates.")
if date_range:
    departure_date, return_date = date_range[0], date_range[-1]
else:
    departure_date, return_date = datetime.now().date(), datetime.now().date()  # Default or error values

# Check if the selected dates are in the future and valid
current_date = datetime.now().date()
if departure_date < current_date or return_date < departure_date:
    st.error("Departure and return dates must be in the future and the return date must be after the departure date.")
else:
    days_until_departure = (departure_date - current_date).days
    days_until_return = (return_date - departure_date).days  # Assuming you might use this

# Calculate days until departure
days_until_departure = (departure_date - date.today()).days


detected_country = st.text_input("Detected Country", help="Country detected from your current location or preference.")

if st.button("Show Savings Potential"):
    with st.spinner('Calculating...'):
        classification_result, regression_result = predict(departure_airport_code, destination_airport_code, days_until_departure, detected_country)
    st.success("Calculation complete!")
    st.metric(label="Classification Prediction", value=classification_result[0])
    st.metric(label="Regression Prediction", value=regression_result[0] if regression_result else "N/A")