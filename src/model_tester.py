import argparse
import os
import pandas as pd
from pycaret.regression import load_model, predict_model, get_metrics, setup

def get_absolute_path(relative_path):
    """
    Converts a relative file path to an absolute path, based on the script's location.
    """
    # Determine the directory of this script:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Build an absolute path by combining the script's directory with the relative path:
    return os.path.join(script_dir, relative_path)

def setup_arg_parser():
    """Setup CLI argument parser."""
    parser = argparse.ArgumentParser(description='Loads test data, makes predictions using a trained model, and returns the results.')
    parser.add_argument('--testfile', required=True, help='Name of the test data file')
    parser.add_argument('--model_path',default="../models/trained_model" ,required=False, help='Path to the trained model file')
    return parser.parse_args()


# Parse command-line arguments
args = setup_arg_parser()

# Load test dataset
test_data_path = get_absolute_path(f'../data/6.model_data/{args.testfile}')
df_test = pd.read_csv(test_data_path)

# Load trained model
model_path = get_absolute_path(args.model_path)
model = load_model(model_path)

# Set up PyCaret
setup(data=df_test)

# Make predictions
predictions = predict_model(model, data=df_test)

# Get high-level metrics
metrics = get_metrics()

# Print high-level metrics
print(metrics)
