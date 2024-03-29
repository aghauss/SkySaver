
# Skysaver

## Description

Skysaver is an innovative application designed to help users optimize their flight costs by leveraging IP location switching. By querying flight prices across a multitude of countries, Skysaver identifies potential savings opportunities, enabling users to make more informed decisions on flight bookings. At its core, Skysaver utilizes a sophisticated web crawler that runs identical flight queries on Google Flights from various countries, compiling a comprehensive dataset. This dataset undergoes a meticulous preprocessing pipeline to create a final training set for a predictive model, which then guides users on whether switching their IP location could result in cost savings for their flight.

## Features

- Unique IP location-based flight cost optimization.
- Advanced web crawling to gather flight data from Google Flights across a wide range of countries.
- Structured data transformation into CSV format for analysis.
- A comprehensive data preprocessing pipeline to prepare the training dataset.
- Predictive modeling to inform users of potential savings through IP location switching.

## Technologies Used

- Python
- Playwright for Python (for asynchronous web scraping)
- PyCaret (for machine learning model creation and evaluation)
- Pandas (for data manipulation)

## Getting Started

### Prerequisites

- Python 3.8 or newer
- Poetry for dependency management

### Installation

1. Clone the repository to your local machine:
```bash
git clone https://yourrepositoryurl/Skysaver.git
cd Skysaver
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Usage

Follow the steps below to start leveraging Skysaver for your flight queries:

1. Navigate to the `src` directory:
```bash
cd src
```

2. Run the web crawler to collect flight data (Note: This step requires appropriate configurations for IP switching):
```bash
python csv_converter.py --config your_config.json
```

3. Preprocess the collected data to prepare the training dataset:
```bash
python data_preprocessor.py
```

4. Train the predictive model with the preprocessed data:
```bash
python model_creator.py
```

5. Query for flights and receive recommendations on IP location switching for cost savings:
```bash
python flight_query_executor.py --flight-query your_query.json
```

Replace `your_config.json`, `your_query.json`, and other placeholders with actual file names or arguments as per your setup and requirements.

## Contributing

Contributions to Skysaver are welcome! If you have ideas for improvement or want to contribute code, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Acknowledgments

- Thanks to all the contributors and the community for the insights and support in developing Skysaver.
