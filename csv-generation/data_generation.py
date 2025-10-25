import pandas as pd
import io
import random
import numpy as np

# --- Data Generation Configuration ---

# Cities known for major data center clusters
hub_cities = {
"VA": "Ashburn",
"OR": "The Dalles",
"IA": "Council Bluffs",
"OH": "New Albany",
"AZ": "Mesa",
"GA": "Atlanta",
"NV": "Reno",
"TX": "San Antonio",
"WA": "Quincy",
"NC": "Forest City",
"OR_2": "Prineville", # Use alias to have multiple hubs in one state
"AZ_2": "Chandler"
}

# A large sample of other US cities to act as the "non-hub" group
non_hub_cities = {
"AL": "Birmingham", "AK": "Anchorage", "AZ_3": "Tucson", "AR": "Little Rock", "CA": "Los Angeles", "CO": "Denver",
"CT": "Bridgeport", "DE": "Wilmington", "FL": "Miami", "GA_2": "Savannah", "HI": "Honolulu", "ID": "Boise",
"IL": "Chicago", "IN": "Indianapolis", "IA_2": "Des Moines", "KS": "Wichita", "KY": "Louisville", "LA": "New Orleans",
"ME": "Portland", "MD": "Baltimore", "MA": "Boston", "MI": "Detroit", "MN": "Minneapolis", "MS": "Jackson",
"MO": "Kansas City", "MT": "Billings", "NE": "Omaha", "NV_2": "Las Vegas", "NH": "Manchester", "NJ": "Newark",
"NM": "Albuquerque", "NY": "New York", "NC_2": "Charlotte", "ND": "Fargo", "OH_2": "Cleveland", "OK": "Oklahoma City",
"OR_3": "Portland", "PA": "Philadelphia", "RI": "Providence", "SC": "Charleston", "SD": "Sioux Falls", "TN": "Nashville",
"TX_2": "Houston", "UT": "Salt Lake City", "VT": "Burlington", "VA_2": "Richmond", "WA_2": "Seattle", "WV": "Charleston",
"WI": "Milwaukee", "WY": "Cheyenne"
}

# Generate 2000 data points
data_records = []
for _ in range(2000):
    # 20% chance of being a data center hub to create an imbalanced, realistic dataset
    is_hub = random.random() < 0.20
    if is_hub:
        state_key, city = random.choice(list(hub_cities.items()))
        state = state_key.split('_')[0]
        # Higher rate change for hubs (mean 4.5%, std dev 0.8%)
        rate_change = max(0.01, np.random.normal(0.045, 0.008))
    else:
        state_key, city = random.choice(list(non_hub_cities.items()))
        state = state_key.split('_')[0]
        # Lower, typical rate change for non-hubs (mean 1.8%, std dev 0.5%)
        rate_change = max(0.005, np.random.normal(0.018, 0.005))
    data_records.append({
        "State": state,
        "City": city,
        "Elec_Rate_Change_Pct": round(rate_change, 5)
    })

# Create a pandas DataFrame
df = pd.DataFrame(data_records)

# Shuffle the dataframe to mix the hubs and non-hubs
df = df.sample(frac=1).reset_index(drop=True)

# --- THIS IS THE FIX ---
# Provide a filename (e.g., 'hackathon_dataset.csv') to save the file to your device.
# The `index=False` part prevents pandas from writing the row numbers as a column.
df.to_csv('hackathon_dataset.csv', index=False)

# --- Display confirmation and data ---
print(f"Generated a dataset with {len(df)} records.\n")
print("✅ Successfully saved the dataset to 'hackathon_dataset.csv'")
print("\n--- First 20 rows of the dataset ---")
print(df.head(20))