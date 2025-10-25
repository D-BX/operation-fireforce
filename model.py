# model.py
# Combined Housing + DC Electricity Price Models
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# -------------------------
# Housing Price Model
# -------------------------

# Load housing CSV once
housing_df = pd.read_csv("processed_states_hyperscale.csv")

# Simplified CPI data
cpi_data = {
    2000: 172.2, 2001: 177.1, 2002: 179.9, 2003: 184.0, 2004: 188.9,
    2005: 195.3, 2006: 201.6, 2007: 207.3, 2008: 215.3, 2009: 214.5,
    2010: 218.1, 2011: 224.9, 2012: 229.6, 2013: 233.0, 2014: 236.7,
    2015: 237.0, 2016: 240.0, 2017: 245.1, 2018: 251.1, 2019: 255.7,
    2020: 258.8, 2021: 271.0, 2022: 296.8, 2023: 308.5, 2024: 319.6,
    2025: 320.0  # hypothetical
}

ANNUAL_INFLATION_RATE = 0.025  # 2.5% per year

def adjust_for_inflation(value, base_year, target_year, cpi_data=None):
    if cpi_data and base_year in cpi_data and target_year in cpi_data:
        return value * (cpi_data[target_year] / cpi_data[base_year])
    years_diff = target_year - base_year
    return value * (1 + ANNUAL_INFLATION_RATE) ** years_diff

def validate_data(df, state):
    required_columns = ['State', 'Date', 'Avg_Home_Value', 'HomeValue_Pct_Change', 'Is_Post_Announcement']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    df_state = df[df['State'] == state]
    if df_state.empty:
        raise ValueError(f"No data found for state: {state}")
    return df_state

def get_normal_growth_rate(df, state):
    df_state = df[df['State'] == state]
    non_post_df = df_state[df_state['Is_Post_Announcement'] == 0]
    if non_post_df.empty:
        non_post_df = df[df['Is_Post_Announcement'] == 0]
        if non_post_df.empty:
            return 0.03
    return non_post_df['HomeValue_Pct_Change'].mean() / 100

def get_hyperscale_pct_change(df, state):
    df_state = df[df['State'] == state]
    post_df = df_state[df_state['Is_Post_Announcement'] == 1]
    if post_df.empty:
        post_df = df[df['Is_Post_Announcement'] == 1]
        if post_df.empty:
            return 0.20
    normal_rate = get_normal_growth_rate(df, state)
    total_rate = post_df['HomeValue_Pct_Change'].mean() / 100
    return max(total_rate - normal_rate, 0)

def simple_simulate_house_price(state, current_price, years_after=1, base_year=2025, cpi_data=cpi_data):
    df_state = validate_data(housing_df, state)
    df_state['Date'] = pd.to_datetime(df_state['Date'])
    df_state['Year'] = df_state['Date'].dt.year
    df_state['Avg_Home_Value_Real'] = df_state.apply(
        lambda row: adjust_for_inflation(row['Avg_Home_Value'], row['Year'], 2025, cpi_data), axis=1
    )
    normal_growth = get_normal_growth_rate(housing_df, state)
    hyperscale_effect = get_hyperscale_pct_change(housing_df, state)
    total_growth = normal_growth + hyperscale_effect
    target_year = base_year + years_after
    nominal_price = current_price * (1 + total_growth) ** years_after
    real_price = adjust_for_inflation(nominal_price, target_year, 2025, cpi_data)
    return nominal_price, real_price

def advanced_simulate_house_price(state, current_price, future_year=2026, base_year=2025, cpi_data=cpi_data):
    df_state = validate_data(housing_df, state)
    if len(df_state) < 3:
        return simple_simulate_house_price(state, current_price, years_after=future_year-base_year, base_year=base_year, cpi_data=cpi_data)
    df_state['Date'] = pd.to_datetime(df_state['Date'])
    df_state['Year'] = df_state['Date'].dt.year
    df_state['Avg_Home_Value_Real'] = df_state.apply(
        lambda row: adjust_for_inflation(row['Avg_Home_Value'], row['Year'], 2025, cpi_data), axis=1
    )
    X = df_state[['Year', 'Is_Post_Announcement']].values
    y = df_state['Avg_Home_Value_Real'].values
    model = LinearRegression()
    model.fit(X, y)
    future_features = np.array([[future_year, 1]])
    predicted_real_value = model.predict(future_features)[0]
    latest_real_value = df_state['Avg_Home_Value_Real'].iloc[-1]
    adjustment_factor = current_price / latest_real_value if latest_real_value != 0 else 1
    real_price = predicted_real_value * adjustment_factor
    nominal_price = adjust_for_inflation(real_price, 2025, future_year, cpi_data)
    normal_growth = get_normal_growth_rate(housing_df, state)
    if real_price < current_price * (1 + normal_growth) ** (future_year - base_year):
        return simple_simulate_house_price(state, current_price, years_after=future_year-base_year, base_year=base_year, cpi_data=cpi_data)
    return nominal_price, real_price

# -------------------------
# Data Center Price Model
# -------------------------

dc_state_csv = "State_energy_metrics.csv"
dc_csv = "datacenter_regression_ready_with_state_context.csv"
dc_df = None

PASS_THROUGH_ELEC = 0.60  # assumption

def load_dc_data():
    global dc_df
    if dc_df is None:
        state = pd.read_csv(dc_state_csv)
        dc = pd.read_csv(dc_csv)
        state["StateCode"] = state["StateCode"].str.upper()
        dc["State"] = dc["State"].str.upper()
        dc_agg = (
            dc.groupby("State")["EstimatedAnnualElectricityMWh"].sum()
            .rename("DC_Annual_Electricity_MWh").reset_index()
            .rename(columns={"State": "StateCode"})
        )
        df = state.merge(dc_agg, on="StateCode", how="left")
        df["DC_Annual_Electricity_MWh"] = df["DC_Annual_Electricity_MWh"].fillna(0.0)
        dc_df = df
    return dc_df

def build_features(df):
    sales_twh = df["TotalRetailSales_MWh"].astype(float) / 1e6
    gen_twh = df["NetGeneration_MWh"].astype(float) / 1e6
    cap_gw = df["NetSummerCapacity_MW"].astype(float) / 1000.0
    with np.errstate(divide='ignore', invalid='ignore'):
        dc_share = (df["DC_Annual_Electricity_MWh"].astype(float) /
                    df["TotalRetailSales_MWh"].replace({0: np.nan}).astype(float))
    dc_share = dc_share.fillna(0.0)
    dc_present = (df["DC_Annual_Electricity_MWh"] > 0).astype(int)
    X = np.column_stack([
        np.ones(len(df)),
        sales_twh.values,
        gen_twh.values,
        cap_gw.values,
        dc_share.values,
        dc_present.values,
    ])
    feature_names = [
        "Intercept",
        "Sales_TWh",
        "Gen_TWh",
        "Capacity_GW",
        "DC_Load_Share",
        "DC_Present",
    ]
    y = df["AvgRetailPrice_cents_per_kWh"].astype(float).values
    return X, y, feature_names

def build_features_baseline(df):
    sales_twh = df["TotalRetailSales_MWh"].astype(float) / 1e6
    gen_twh = df["NetGeneration_MWh"].astype(float) / 1e6
    cap_gw = df["NetSummerCapacity_MW"].astype(float) / 1000.0
    X = np.column_stack([
        np.ones(len(df)),
        sales_twh.values,
        gen_twh.values,
        cap_gw.values,
    ])
    feature_names = ["Intercept", "Sales_TWh", "Gen_TWh", "Capacity_GW"]
    y = df["AvgRetailPrice_cents_per_kWh"].astype(float).values
    return X, y, feature_names

def fit_ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta

def predict(X, beta):
    return X @ beta

def what_if_added_dc(df, beta, feature_names, state_code, added_power_mw=None, added_annual_mwh=None,
                     pue=1.25, include_added_load_in_sales=True, mode="assumption"):
    sc = state_code.upper()
    row = df[df["StateCode"] == sc]
    if row.empty:
        raise ValueError(f"State {state_code} not found")
    row = row.iloc[0].copy()
    if mode == "trained":
        X_base, _, _ = build_features(df.loc[[row.name]])
        base_pred = predict(X_base, beta).item()
    else:
        Xb, _, _ = build_features_baseline(df.loc[[row.name]])
        base_pred = predict(Xb, beta).item()
    if added_annual_mwh is None:
        if added_power_mw is None:
            raise ValueError("Provide either added_power_mw or added_annual_mwh")
        added_annual_mwh = added_power_mw * 8760.0 * pue
    dc_new = float(row["DC_Annual_Electricity_MWh"]) + float(added_annual_mwh)
    sales_new = float(row["TotalRetailSales_MWh"]) + (float(added_annual_mwh) if include_added_load_in_sales else 0.0)
    sales_twh_new = sales_new / 1e6
    gen_twh_new = float(row["NetGeneration_MWh"]) / 1e6
    cap_gw_new = float(row["NetSummerCapacity_MW"]) / 1000.0
    dc_share_new = 0.0 if sales_new == 0 else dc_new / sales_new
    if mode == "trained":
        dc_present_new = 1 if dc_new > 0 else 0
        X_new = np.array([1.0, sales_twh_new, gen_twh_new, cap_gw_new, dc_share_new, dc_present_new])[None, :]
        new_pred = predict(X_new, beta).item()
    else:
        new_pred = base_pred * (1.0 + PASS_THROUGH_ELEC * dc_share_new)
    return {
        "state": sc,
        "baseline_pred_c_per_kWh": base_pred,
        "new_pred_c_per_kWh": new_pred,
        "delta_c_per_kWh": new_pred - base_pred,
        "added_annual_mwh": added_annual_mwh,
        "dc_share_new": dc_share_new,
        "include_added_load_in_sales": include_added_load_in_sales,
    }
