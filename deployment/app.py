import streamlit as st
import pandas as pd
from datetime import datetime, date
from pycaret.classification import load_model as load_classification_model
from pycaret.regression import load_model as load_regression_model


# Set page width to 1200 pixels
st.set_page_config(layout="wide")

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

departure_options = ["MUC", "BER", "CDG"]
destination_options = ["MUC", "BER", "CDG"]
country_options = ["Germany","UK"]

st.title("SkySaver")
st.markdown("###### Find out how much you could save for your next flight by switching your IP-Location 💩")


destination_airport_mapper = {
    "Munich (MUC)": "MUC",
    "Berlin (BER)": "BER",
    "Frankfurt (FRA)": "FRA",
}

departure_airport_mapper = {
    "Munich (MUC)": "MUC",
    "Berlin (BER)": "BER",
    "Frankfurt (FRA)": "FRA",
}




# Create a container, then create three columns within that container
with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        departure_airport_code = st.selectbox("Departure City",list(destination_airport_mapper.keys()), help="From where do you want to departure?.")
     

    with col2:
        destination_airport_code = st.selectbox("Destination City",list(departure_airport_mapper.keys()) ,help="Enter your destination goal")

    with col3:
        date_range = st.date_input("Select your departure and return dates", [], help="When do you want to travel?")




reverse_country_mapper = {
    "Polska": "Poland",
    "France": "France",
    "No Significant Difference Found" : "No cheaper country found ☹️"
}

# Your existing code
if len(date_range) == 2:
    departure_date, return_date = date_range[0], date_range[1]
    current_date = datetime.now().date()
    if departure_date < current_date or return_date < departure_date:
        st.error("Departure and return dates must be in the future and the return date must be after the departure date.")
    else:
        days_until_departure = (departure_date - current_date).days
        detected_country_model_output = st.selectbox("Your current location", country_options, help="Country detected from your current location or preference.")

        # Map model output to user-friendly format using the reverse mapper dictionary
        detected_country = reverse_country_mapper.get(detected_country_model_output, detected_country_model_output)

        if st.button("Show Savings Potential"):
            with st.spinner('Calculating...'):
                classification_result, regression_result = predict(departure_airport_code, destination_airport_code, days_until_departure, detected_country)

            # Map classification result to user-friendly format using the reverse mapper dictionary
            classification_result_friendly = reverse_country_mapper.get(classification_result[0], classification_result[0])
            st.metric(label="Cheapest Country for your Flight", value=classification_result_friendly)
            if regression_result[0] != 0:  # assuming regression_result = [0] indicates no savings
                formatted_regression_result = f"{regression_result[0]:.1f}%"
                st.metric(label="Saving Potential", value=formatted_regression_result)
            else:
                st.metric(label="Saving Potential", value="0%")