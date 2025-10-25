import pandas as pd
import numpy as np
import random

# --- This script learns from your real data to generate a larger, realistic dataset ---

# --- 1. LOAD REAL DATA TO LEARN STATISTICAL PROPERTIES ---
try:
    summary_df = pd.read_csv('all_isos_summary_statistics.csv')
    print("✅ Successfully loaded 'all_isos_summary_statistics.csv' to learn from.")
except FileNotFoundError:
    print("❌ ERROR: 'all_isos_summary_statistics.csv' not found.")
    print("Please run 'process_all.py' script first to generate this file.")
    exit()

# --- 2. CONFIGURATION & MAPPING ---
CITY_CONFIG = {
    "Ashburn":      {"iso": "PJM",   "is_hub": 1, "population": 50000},
    "Manassas":     {"iso": "PJM",   "is_hub": 1, "population": 42000},
    "Philadelphia": {"iso": "PJM",   "is_hub": 0, "population": 1600000},
    "Baltimore":    {"iso": "PJM",   "is_hub": 0, "population": 580000},
    "Cleveland":    {"iso": "PJM",   "is_hub": 0, "population": 370000},
    "Richmond":     {"iso": "PJM",   "is_hub": 0, "population": 230000},
    "San Antonio":  {"iso": "ERCOT", "is_hub": 1, "population": 1450000},
    "Dallas":       {"iso": "ERCOT", "is_hub": 1, "population": 1300000},
    "Houston":      {"iso": "ERCOT", "is_hub": 0, "population": 2300000},
    "Austin":       {"iso": "ERCOT", "is_hub": 0, "population": 970000},
    "Santa Clara":  {"iso": "CAISO", "is_hub": 1, "population": 130000},
    "Los Angeles":  {"iso": "CAISO", "is_hub": 1, "population": 3900000},
    "San Diego":    {"iso": "CAISO", "is_hub": 0, "population": 1400000},
    "Sacramento":   {"iso": "CAISO", "is_hub": 0, "population": 525000},
    "Minneapolis":  {"iso": "MISO",  "is_hub": 1, "population": 430000},
    "Des Moines":   {"iso": "MISO",  "is_hub": 1, "population": 215000},
    "Detroit":      {"iso": "MISO",  "is_hub": 0, "population": 640000},
    "Indianapolis": {"iso": "MISO",  "is_hub": 0, "population": 890000},
    "Boston":       {"iso": "ISONE", "is_hub": 1, "population": 675000},
    "Providence":   {"iso": "ISONE", "is_hub": 0, "population": 190000},
    "Hartford":     {"iso": "ISONE", "is_hub": 0, "population": 120000},
}

# --- 3. CALCULATE THE "STATISTICAL SIGNATURES" ---
# (This part remains the same)
hub_status_map = {city: details['is_hub'] for city, details in CITY_CONFIG.items()}
summary_df['City'] = summary_df['location'].apply(lambda x: next((city for city in hub_status_map if city.upper() in x.upper()), None))
summary_df.dropna(subset=['City'], inplace=True)
summary_df['is_hub'] = summary_df['City'].map(hub_status_map)

hub_data = summary_df[summary_df['is_hub'] == 1]
non_hub_data = summary_df[summary_df['is_hub'] == 0]

hub_stats = {'price_mean': 45, 'price_std': 15, 'vol_mean': 50, 'vol_std': 25}
non_hub_stats = {'price_mean': 35, 'price_std': 8, 'vol_mean': 25, 'vol_std': 10}

if not hub_data.empty:
    hub_stats.update({
        'price_mean': hub_data['Avg_Price'].mean(), 'price_std': hub_data['Avg_Price'].std(),
        'vol_mean': hub_data['Price_Std_Dev'].mean(), 'vol_std': hub_data['Price_Std_Dev'].std()
    })
    print("\nLearned Hub Signature:", hub_stats)

if not non_hub_data.empty:
    non_hub_stats.update({
        'price_mean': non_hub_data['Avg_Price'].mean(), 'price_std': non_hub_data['Avg_Price'].std(),
        'vol_mean': non_hub_data['Price_Std_Dev'].mean(), 'vol_std': non_hub_data['Price_Std_Dev'].std()
    })
    print("Learned Non-Hub Signature:", non_hub_stats)

# --- 4. GENERATE 10,000 REALISTIC DATA POINTS ---
print("\nGenerating 10,000 data points with realistic usage and pricing...")
data_records = []
hub_cities_list = [city for city, details in CITY_CONFIG.items() if details['is_hub'] == 1]
non_hub_cities_list = [city for city, details in CITY_CONFIG.items() if details['is_hub'] == 0]

for _ in range(10000):
    is_hub_point = random.random() < 0.3
    city_name = random.choice(hub_cities_list if is_hub_point else non_hub_cities_list)
    config = CITY_CONFIG[city_name]
    population = config['population']
    iso = config['iso']

    # Calculate Current Power Usage
    base_kw_per_person = 1.3
    if iso in ["ERCOT", "CAISO"]:
        climate_factor = np.random.uniform(0.1, 0.4)
    elif iso in ["MISO", "ISONE"]:
        climate_factor = np.random.uniform(0.0, 0.2)
    else: # PJM
        climate_factor = np.random.uniform(0.0, 0.3)
    
    total_kw_per_person = base_kw_per_person + climate_factor
    current_power_usage_mw = (population * total_kw_per_person) / 1000
    
    # Use learned statistics for market data
    stats_to_use = hub_stats if is_hub_point else non_hub_stats
    avg_lmp = max(20, np.random.normal(stats_to_use['price_mean'], stats_to_use['price_std']))
    lmp_volatility = max(5, np.random.normal(stats_to_use['vol_mean'], stats_to_use['vol_std']))
    high_price_days = int(max(0, np.random.normal(avg_lmp / 15, lmp_volatility / 20)))

    # Calculate the final Elec_Rate_Change_Pct
    rate_change = 0.015 + (avg_lmp / 2000) + (lmp_volatility / 1500) + (high_price_days / 500)
    if config['is_hub']:
        rate_change += 0.01 + (lmp_volatility / 800)
    rate_change += np.random.normal(0, 0.003)
    
    data_records.append({
        "City": city_name,
        "ISO": iso,
        "Population": population,
        "Current_Power_Usage_MW": round(current_power_usage_mw, 2),
        "Power_Usage_per_Capita_kW": round(total_kw_per_person, 4), # NEW COLUMN
        "Is_Hub": config['is_hub'],
        "Avg_LMP_USD_per_MWh": round(avg_lmp, 2),
        "LMP_Volatility": round(lmp_volatility, 2),
        "High_Price_Days": high_price_days,
        "Elec_Rate_Change_Pct": round(max(0.005, rate_change), 5)
    })

# --- 5. Create and Save Final Training DataFrame ---
final_df = pd.DataFrame(data_records)
# Reorder columns to place the new column next to the other usage metrics
final_df = final_df[[
    "City", "ISO", "Population", "Current_Power_Usage_MW", "Power_Usage_per_Capita_kW", 
    "Is_Hub", "Avg_LMP_USD_per_MWh", "LMP_Volatility", "High_Price_Days", "Elec_Rate_Change_Pct"
]]
final_df = final_df.sample(frac=1).reset_index(drop=True)
final_df.to_csv('final_training_dataset_10000.csv', index=False)

print("\n✅ Successfully generated 'final_training_dataset_10000.csv' with Power_Usage_per_Capita_kW.")
print("\n--- First 15 rows of the final training dataset ---")
print(final_df.head(15))