import argparse
import os
import pandas as pd
from pycaret.regression import setup as setup_regression, create_model as create_model_regression, save_model as save_model_regression, finalize_model as finalize_model_regression
from pycaret.classification import setup as setup_classification, create_model as create_model_classification, save_model as save_model_classification, finalize_model as finalize_model_classification
import json

def get_absolute_path(relative_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)

def load_dataset(df_path):
    try:
        return pd.read_csv(df_path)
    except FileNotFoundError:
        print(f"The file {df_path} was not found.")
        exit(1)

def train_and_save_model(df, target, model_type, hyperparameters, model_save_path):
    if model_type == 'regression':
        setup_regression(data=df, target=target, fold=10, session_id=123, verbose=False)
        model = create_model_regression('et', **hyperparameters['regression'])
        final_model = finalize_model_regression(model)
        save_model_regression(final_model, model_save_path)
    elif model_type == 'classification':
        setup_classification(data=df, target=target, fold=10, session_id=123, verbose=False)
        model = create_model_classification('et', **hyperparameters['classification'])
        final_model = finalize_model_classification(model)
        save_model_classification(model, model_save_path)
    else:
        raise ValueError("Invalid model type specified. Choose 'regression' or 'classification'.")

    print(f"Model saved successfully at: {model_save_path}")

def main():
    parser = argparse.ArgumentParser(description='Trains and saves models.')
    parser.add_argument('--datapath', required=True, help='Path to the training data file')
    parser.add_argument('--hyperparameter', default="../config/models_hyperparameters_config.json", required=False, help='Path to the hyperparameter config file')
    parser.add_argument('--model_save_path', default="../models/", required=False, help='Directory where the trained models will be saved')
    args = parser.parse_args()

    df_train_path = get_absolute_path(f'../data/6.model_data/{args.datapath}')
    df_train = load_dataset(df_train_path)

    hyperparameter_path = get_absolute_path(args.hyperparameter)
    with open(hyperparameter_path, 'r') as f:
        hyperparameters = json.load(f)

    regression_target = 'normalized_mean_savings'
    regression_columns_to_keep = ['departure_airport_code', 'destination_airport_code', 'Detected_Country', 'days_until_departure', regression_target]
    df_regression = df_train.loc[:, regression_columns_to_keep]
    train_and_save_model(df_regression, regression_target, 'regression', hyperparameters, os.path.join(args.model_save_path, "regression_model"))

    classification_target = 'Mode_Cheapest_Location_Journey'
    classification_columns_to_keep = ['departure_airport_code', 'destination_airport_code', 'Detected_Country','days_until_departure', classification_target]
    df_classification = df_train.loc[:, classification_columns_to_keep]
    train_and_save_model(df_classification, classification_target, 'classification', hyperparameters, os.path.join(args.model_save_path, "classification_model"))

if __name__ == "__main__":
    main()
