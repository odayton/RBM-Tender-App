import logging
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_model(data):
    """
    Train a machine learning model using the provided data.

    :param data: DataFrame containing the training data
    :return: Trained model
    """
    logger.info("Starting model training")

    # Example: Linear regression model for demonstration
    X = data.drop('target', axis=1)
    y = data['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)

    logger.info(f"Model training completed with MSE: {mse}")
    return model

def predict(model, new_data):
    """
    Make predictions using the trained model.

    :param model: Trained machine learning model
    :param new_data: DataFrame containing the new data for predictions
    :return: Predictions
    """
    logger.info("Making predictions with the trained model")
    predictions = model.predict(new_data)
    return predictions

def load_data(file_path):
    """
    Load data from a CSV file.

    :param file_path: Path to the CSV file
    :return: DataFrame
    """
    logger.info(f"Loading data from {file_path}")
    data = pd.read_csv(file_path)
    return data
