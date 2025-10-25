import pandas as pd

# Load the merged Zillow + hyperscale data
long_df = pd.read_csv("merged_hyperscale_zillow.csv")

# Convert Date to datetime just in case
long_df["Date"] = pd.to_datetime(long_df["Date"], errors="coerce")

# Drop rows missing home value or percent change
model_df = long_df.dropna(subset=["Avg_Home_Value", "HomeValue_Pct_Change"])

# Optional: Check first few rows
print(model_df.head())

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

# Drop rows with missing home values
model_df = long_df.dropna(subset=["Avg_Home_Value", "HomeValue_Pct_Change"])

X = model_df[["StateName", "is_hub", "Is_Post_Announcement", "Avg_Home_Value"]]
y = model_df["HomeValue_Pct_Change"]

# Preprocessing
preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), ["StateName"])
], remainder="passthrough")

# Model
model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(random_state=42))
])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# Example: predict post-announcement home value % change for Texas
sample = pd.DataFrame([{
    "StateName": "TX",
    "is_hub": 1,
    "Is_Post_Announcement": 1,
    "Avg_Home_Value": 410000
}])

pred = model.predict(sample)
print(f"Predicted % change in home value after hyperscale announcement: {pred[0]:.2f}%")
