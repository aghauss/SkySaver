import streamlit as st
import pandas as pd
from datetime import datetime, date
from pycaret.classification import load_model as load_classification_model
from pycaret.regression import load_model as load_regression_model

# Caching the model loading
@st.cache_resource
def load_cached_classification_model():
    return load_classification_model('../models/classification_model')

@st.cache_resource
def load_cached_regression_model():
    return load_regression_model('../models/regression_model')

# Prediction function
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
    regression_prediction = regression_model.predict(input_data_regression) if classification_prediction[0] != "No Significant Difference Found" else [0]

    return classification_prediction, regression_prediction

# Initialize models
classification_model = load_cached_classification_model()
regression_model = load_cached_regression_model()

# Display the logo at the top of the application
st.image("design/skysaver_logo.png", use_column_width=True)

# Implementing a "Start" button to reveal the application fields
if st.button('Start'):
    st.title("SkySaver")
    st.subheader("Find out how much you could save for your next flight by switching your IP-Location")

    # Arranging input fields side by side
    col1, col2, col3 = st.columns(3)
    with col1:
        departure_airport_code = st.text_input("Departure Airport Code", help="Enter the 3-letter airport code.")
    with col2:
        destination_airport_code = st.text_input("Destination Airport Code", help="Enter the 3-letter airport code.")
    with col3:
        detected_country = st.text_input("Detected Country", help="Country detected from your current location or preference.")

    # Date input for departure and return dates
    date_range = st.date_input("Select your departure and return dates", help="Select your departure and return dates.")
    if len(date_range) == 2:
        departure_date, return_date = date_range[0], date_range[-1]
        current_date = datetime.now().date()
        if departure_date < current_date or return_date < departure_date:
            st.error("Departure and return dates must be in the future and the return date must be after the departure date.")
        else:
            days_until_departure = (departure_date - date.today()).days

            if st.button("Show Savings Potential"):
                with st.spinner('Calculating...'):
                    classification_result, regression_result = predict(departure_airport_code, destination_airport_code, days_until_departure, detected_country)
                st.success("Calculation complete!")
                st.metric(label="Cheapest Country for your Flight", value=classification_result[0])
                if regression_result[0] != 0:
                    formatted_regression_result = f"{regression_result[0]:.1f}%"
                    st.metric(label="Saving Potential", value=formatted_regression_result)
                else:
                    st.metric(label="Saving Potential", value="N/A")
