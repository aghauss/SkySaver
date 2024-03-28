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




st.title("SkySaver")
st.markdown("###### Find out how much you could save for your next flight by switching your IP-Location")

departure_airport_mapper = {
    'Madrid (MAD)': 'MAD',
    'London (LHR)': 'LHR',
    'Rome (FCO)': 'FCO',
    'Jakarta (CGK)': 'CGK',
    'Sydney (SYD)': 'SYD',
    'Dallas (DFW)': 'DFW',
    'Paris (CDG)': 'CDG',
    'Bogotá (BOG)': 'BOG',
    'New Orleans (MSY)': 'MSY',
    'Athens (ATH)': 'ATH',
    'Cancún (CUN)': 'CUN',
    'Cape Town (CPT)': 'CPT',
    'Oslo (OSL)': 'OSL',
    'Los Angeles (LAX)': 'LAX',
    'Las Vegas (LAS)': 'LAS',
    'Jeddah (JED)': 'JED',
    'Hong Kong (HKG)': 'HKG',
    'Frankfurt (FRA)': 'FRA',
    'Manchester (MAN)': 'MAN',
    'Barcelona (BCN)': 'BCN',
    'Munich (MUC)': 'MUC',
    'Copenhagen (CPH)': 'CPH',
    'Amsterdam (AMS)': 'AMS',
    'Seattle (SEA)': 'SEA',
    'Lima (LIM)': 'LIM',
    'Luxembourg (LUX)': 'LUX',
    'São Paulo (GRU)': 'GRU',
    'Dubai (DXB)': 'DXB',
    'Phoenix (PHX)': 'PHX',
    'Berlin (BER)': 'BER',
    'Santiago (SCL)': 'SCL',
    'Toronto (YYZ)': 'YYZ',
    'Zagreb (ZAG)': 'ZAG',
    'Helsinki (HEL)': 'HEL',
    'Guangzhou (CAN)': 'CAN',
    'Bangkok (BKK)': 'BKK',
    'Vienna (VIE)': 'VIE',
    'Osaka (KIX)': 'KIX',
    'Baltimore (BWI)': 'BWI',
    'New York (JFK)': 'JFK',
    'Dublin (DUB)': 'DUB',
    'Edinburgh (EDI)': 'EDI',
    'Shanghai (PVG)': 'PVG',
    'Mexico City (MEX)': 'MEX',
    'Brussels (BRU)': 'BRU',
    'Philadelphia (PHL)': 'PHL',
    'Tianjin (TSN)': 'TSN',
    'Casablanca (CMN)': 'CMN',
    'Miami (MIA)': 'MIA',
    'Charlotte (CLT)': 'CLT',
    'Honolulu (HNL)': 'HNL'
}

destination_airport_mapper = {
    'Paris (CDG)': 'CDG',
    'Melbourne (MEL)': 'MEL',
    'New York (JFK)': 'JFK',
    'Lisbon (LIS)': 'LIS',
    'Medellín (MDE)': 'MDE',
    'Barcelona (BCN)': 'BCN',
    'Johannesburg (JNB)': 'JNB',
    'Mexico City (MEX)': 'MEX',
    'Lima (LIM)': 'LIM',
    'Madrid (MAD)': 'MAD',
    'Los Angeles (LAX)': 'LAX',
    'Frankfurt (FRA)': 'FRA',
    'Riyadh (RUH)': 'RUH',
    'Newark (EWR)': 'EWR',
    'Kuala Lumpur (KUL)': 'KUL',
    'Las Palmas (LPA)': 'LPA',
    'Cancún (CUN)': 'CUN',
    'Stavanger (SVG)': 'SVG',
    'Munich (MUC)': 'MUC',
    'Palma de Mallorca (PMI)': 'PMI',
    'Berlin (BER)': 'BER',
    'Nice (NCE)': 'NCE',
    'Heraklion (HER)': 'HER',
    'Seattle (SEA)': 'SEA',
    'Vancouver (YVR)': 'YVR',
    'Palermo (PMO)': 'PMO',
    'Oslo (OSL)': 'OSL',
    'London (LHR)': 'LHR',
    'Beijing (PEK)': 'PEK',
    'Málaga (AGP)': 'AGP',
    'Singapore (SIN)': 'SIN',
    'Dallas (DFW)': 'DFW',
    'Delhi (DEL)': 'DEL',
    'San Salvador (SAL)': 'SAL',
    'Kuwait City (KWI)': 'KWI',
    'Washington (IAD)': 'IAD',
    'Tenerife (TFN)': 'TFN',
    'São Paulo (CGH)': 'CGH',
    'New York (LGA)': 'LGA',
    'Catania (CTA)': 'CTA',
    'Brisbane (BNE)': 'BNE',
    'Bergen (BGO)': 'BGO',
    'Saint Petersburg (LED)': 'LED',
    'Seoul (ICN)': 'ICN',
    'Luxembourg (LUX)': 'LUX',
    'Larnaca (LCA)': 'LCA',
    'Zürich (ZRH)': 'ZRH',
    'Chania (CHQ)': 'CHQ',
    'Dublin (DUB)': 'DUB',
    'Baltimore (BWI)': 'BWI',
    'Bangkok (BKK)': 'BKK',
    'Helsinki (HEL)': 'HEL',
    'Tokyo (NRT)': 'NRT',
    'Santiago (SCL)': 'SCL',
    'Lyon (LYS)': 'LYS',
    'Tromsø (TOS)': 'TOS',
    'Honolulu (HNL)': 'HNL',
    'Shanghai (PVG)': 'PVG',
    'Hong Kong (HKG)': 'HKG',
    'Bordeaux (BOD)': 'BOD',
    'Rome (FCO)': 'FCO',
    'Cape Town (CPT)': 'CPT',
    'Taipei (TPE)': 'TPE',
    'Trondheim (TRD)': 'TRD'
}







# Create a container, then create three columns within that container
with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        departure_city_full_name = st.selectbox("Departure City",list(departure_airport_mapper.keys()), help="From where do you want to departure?.")
     

    with col2:
        destination_city_full_name = st.selectbox("Destination City",list(destination_airport_mapper.keys()) ,help="Enter your destination goal")

    with col3:
        date_range = st.date_input("Select your departure and return dates", [], help="When do you want to travel?")


reverse_country_mapper = {
    'Türkiye': 'Turkey',
    'Schweiz': 'Switzerland',
    'Polska': 'Poland',
    'Deutschland': 'Germany',
    'Brasil': 'Brazil',
    'Australia': 'Australia',
    'Indonesia': 'Indonesia',
    'Shqipëri': 'Albania',
    'United Kingdom': 'United Kingdom',
    '日本': 'Japan',
    'Palestine': 'Palestine',
    'বাংলাদেশ': 'Bangladesh',
    'Vereinigte Staaten': 'United States',
    'Spain': 'Spain',
    'Ukraine': 'Ukraine',
    'Azerbaijan': 'Azerbaijan',
    'Russia': 'Russia',
    'France': 'France',
    'Egypt': 'Egypt',
    'South Africa': 'South Africa',
    'Netherlands': 'Netherlands',
    'United States': 'United States',
    'India': 'India',
    'Poland': 'Poland',
    'Morocco': 'Morocco',
    'Denmark': 'Denmark',
    'Belgium': 'Belgium',
    'Czechia': 'Czech Republic',
    'Portugal': 'Portugal',
    'Belarus': 'Belarus',
    'Sweden': 'Sweden',
    'Lithuania': 'Lithuania',
    'Bosnia & Herzegovina': 'Bosnia and Herzegovina',
    'Bulgaria': 'Bulgaria',
    'Lebanon': 'Lebanon',
    'Stany Zjednoczone': 'United States',
    'Kuwait': 'Kuwait',
    'Armenia': 'Armenia',
    'Benin': 'Benin',
    'United Arab Emirates': 'United Arab Emirates',
    'Amerika Serikat': 'United States',
    'Saudi Arabia': 'Saudi Arabia',
    'Algeria': 'Algeria',
    'Romania': 'Romania',
    'Greece': 'Greece',
    'Libya': 'Libya',
    'Oman': 'Oman',
    'Cyprus': 'Cyprus',
    'Pakistan': 'Pakistan',
    'Norway': 'Norway',
    'イラン': 'Iran',
    "No Significant Difference Found" : "No cheaper country found 😭"
}


country_mapper = {
    'Turkey': 'Türkiye',
    'Switzerland': 'Schweiz',
    'Poland': 'Polska',
    'Germany': 'Deutschland',
    'Brazil': 'Brasil',
    'Australia': 'Australia',
    'Indonesia': 'Indonesia',
    'Albania': 'Shqipëri',
    'United Kingdom': 'United Kingdom',
    'Japan': '日本',
    'Palestine': 'Palestine',
    'Bangladesh': 'বাংলাদেশ',
    'United States': 'Vereinigte Staaten',
    'Spain': 'Spain',
    'Ukraine': 'Ukraine',
    'Azerbaijan': 'Azerbaijan',
    'Russia': 'Russia',
    'France': 'France',
    'Egypt': 'Egypt',
    'South Africa': 'South Africa',
    'Netherlands': 'Netherlands',
    'India': 'India',
    'Morocco': 'Morocco',
    'Denmark': 'Denmark',
    'Belgium': 'Belgium',
    'Czech Republic': 'Czechia',
    'Portugal': 'Portugal',
    'Belarus': 'Belarus',
    'Sweden': 'Sweden',
    'Lithuania': 'Lithuania',
    'Bosnia and Herzegovina': 'Bosnia & Herzegovina',
    'Bulgaria': 'Bulgaria',
    'Lebanon': 'Lebanon',
    'United Arab Emirates': 'United Arab Emirates',
    'Kuwait': 'Kuwait',
    'Armenia': 'Armenia',
    'Benin': 'Benin',
    'Saudi Arabia': 'Saudi Arabia',
    'Algeria': 'Algeria',
    'Romania': 'Romania',
    'Greece': 'Greece',
    'Libya': 'Libya',
    'Oman': 'Oman',
    'Cyprus': 'Cyprus',
    'Pakistan': 'Pakistan',
    'Norway': 'Norway',
    'Iran': 'イラン'
}



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
                  




