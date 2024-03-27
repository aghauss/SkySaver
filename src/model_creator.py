import argparse
import os
import pandas as pd
from pycaret.regression import setup, create_model, save_model  
import json

def get_absolute_path(relative_path):
    """
    Converts a relative file path to an absolute path, based on the script's location.
    """
    # Determine the directory of this script:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Build an absolute path by combining the script's directory with the relative path:
    return os.path.join(script_dir, relative_path)

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

def setup_arg_parser():
    """Setup CLI argument parser."""
    parser = argparse.ArgumentParser(description='Runs model training based on predefined hyperparameters and outputs the model as pickle file.')
    parser.add_argument('--filename', required=True, help='Name of the training data file')
    parser.add_argument('--hyperparameter', default="../config/et_model_hyperparameters_config.json", required=False, help='Path to the hyperparameter config file')
    parser.add_argument('--model_save_path', default="../models/trained_model", required=False, help='Path where the trained model will be saved')
    return parser.parse_args()

# Parse command-line arguments
args = setup_arg_parser()

# Load training dataset
df_train_path = get_absolute_path(f'../data/6.model_data/{args.filename}')
hyperparameter_path = get_absolute_path(args.hyperparameter)
df_train = pd.read_csv(df_train_path)

# Define Model setup
fixed_features = ['departure_airport_code','destination_airport_code','Detected_Country','days_until_departure']
target_variable = ['normalized_mean_savings']
columns_to_keep = fixed_features + target_variable

# Assuming hyperparameters are loaded from JSON file
with open(hyperparameter_path, 'r') as f:
    hyperparameters = json.load(f)

# Assuming 'df' is your DataFrame and 'columns_to_keep' is the list of columns you want to retain
df_train = df_train.loc[:, columns_to_keep]

# Set up PyCaret
s = setup(data=df_train, target='normalized_mean_savings', fold=20, session_id=123, verbose=False)

# Train model
dt = create_model('et', **hyperparameters)  # Assuming you want to create an Extra Trees model

# Save trained model
model_save_path = get_absolute_path(args.model_save_path)

# Save the trained model
save_model(dt, model_save_path)

print("Model saved successfully at:", model_save_path)
