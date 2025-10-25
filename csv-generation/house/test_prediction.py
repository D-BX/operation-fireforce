import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Load processed data
df = pd.read_csv("processed_states_hyperscale.csv")

# Prepare features and target
features = ["State", "Avg_Home_Value"]
target = "HomeValue_Pct_Change"

X = df[features]
y = df[target]

# Impute missing numeric values with median
numeric_transformer = SimpleImputer(strategy="median")

# One-hot encode states, ignore unknown categories
categorical_transformer = OneHotEncoder(handle_unknown="ignore")

# Column transformer for preprocessing
ct = ColumnTransformer([
    ("state_enc", categorical_transformer, ["State"]),
    ("num_imputer", numeric_transformer, ["Avg_Home_Value"])
])

# Pipeline: preprocessing + regression
model_pipeline = Pipeline([
    ("preprocess", ct),
    ("regressor", LinearRegression())
])

# Fit model
model_pipeline.fit(X, y)

# Prediction function
def predict_future_price(state: str, current_price: float):
    X_input = pd.DataFrame([[state, current_price]], columns=features)
    pct_change = model_pipeline.predict(X_input)[0]
    future_price = current_price * (1 + pct_change / 100)
    return future_price, pct_change

# Example usage
state = "NY"
current_price = 600000
future_price, pct_change = predict_future_price(state, current_price)
print(f"Predicted % change: {pct_change:.2f}%")
print(f"Predicted future price: ${future_price:,.2f}")
