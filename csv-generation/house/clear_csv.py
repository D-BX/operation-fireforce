import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Load CSV
df = pd.read_csv("processed_states_hyperscale.csv")

# Only keep rows with no NaNs in target and feature columns
df_clean = df.dropna(subset=['Avg_Home_Value', 'HomeValue_Pct_Change'])

# Features and target
X = df_clean[['State', 'Avg_Home_Value']]
y = df_clean['HomeValue_Pct_Change']

# Build pipeline
ct = ColumnTransformer(
    transformers=[('encoder', OneHotEncoder(handle_unknown='ignore'), ['State'])],
    remainder='passthrough'
)

model_pipeline = Pipeline(steps=[('preprocessor', ct), ('regressor', LinearRegression())])

# Fit model
model_pipeline.fit(X, y)

# Test prediction
state = 'NY'
current_price = 500000
X_test = pd.DataFrame([[state, current_price]], columns=['State', 'Avg_Home_Value'])
future_pct_change = model_pipeline.predict(X_test)
future_price = current_price * (1 + future_pct_change[0]/100)
print(f"Predicted price after hyperscale announcement: {future_price:.2f}")
