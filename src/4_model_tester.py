import argparse
import os
import pandas as pd
from pycaret.regression import load_model as load_regression_model, predict_model as predict_regression_model, setup as setup_regression, get_metrics as get_regression_metrics
from pycaret.classification import load_model as load_classification_model, predict_model as predict_classification_model, setup as setup_classification, get_metrics as get_classification_metrics

def get_absolute_path(relative_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)

def setup_arg_parser():
    parser = argparse.ArgumentParser(description='Loads test data, makes predictions using a trained model, and returns the results.')
    parser.add_argument('--testfile', required=True, help='Name of the test data file')
    parser.add_argument('--model_path', default="../models/trained_model", required=False, help='Path to the trained model file')
    parser.add_argument('--model_type', choices=['regression', 'classification'], required=True, help='Type of the model (regression or classification)')
    return parser.parse_args()

def test_model(df_test, model_path, model_type):
    if model_type == 'regression':
        model = load_regression_model(model_path)
        setup_regression(data=df_test)
        predictions = predict_regression_model(model, data=df_test)
        metrics = get_regression_metrics()
    elif model_type == 'classification':
        model = load_classification_model(model_path)
        setup_classification(data=df_test)
        predictions = predict_classification_model(model, data=df_test)
        metrics = get_classification_metrics()
    else:
        raise ValueError("Invalid model type specified. Choose 'regression' or 'classification'.")

    print(metrics)

def main():
    args = setup_arg_parser()
    test_data_path = get_absolute_path(f'../data/6.model_data/{args.testfile}')
    df_test = pd.read_csv(test_data_path)
    model_path = get_absolute_path(args.model_path)
    test_model(df_test, model_path, args.model_type)

if __name__ == "__main__":
    main()
