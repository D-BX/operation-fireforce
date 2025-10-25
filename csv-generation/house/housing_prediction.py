import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Load your CSV file
df = pd.read_csv('processed_states_hyperscale.csv')

# Simplified CPI data (replace with actual BLS CPI data if available)
cpi_data = {
    2000: 172.2,
    2001: 177.1,
    2002: 179.9,
    2003: 184.0,
    2004: 188.9,
    2005: 195.3,
    2006: 201.6,
    2007: 207.3,
    2008: 215.3,
    2009: 214.5,
    2010: 218.1,
    2011: 224.9,
    2012: 229.6,
    2013: 233.0,
    2014: 236.7,
    2015: 237.0,
    2016: 240.0,
    2017: 245.1,
    2018: 251.1,
    2019: 255.7,
    2020: 258.8,
    2021: 271.0,
    2022: 296.8,
    2023: 308.5,
    2024: 319.6,
    2025: 320.0  # hypothetical
}

ANNUAL_INFLATION_RATE = 0.025  # 2.5% per year, recent U.S. average

def adjust_for_inflation(value, base_year, target_year, cpi_data=None):
    """
    Adjusts nominal value from base_year to target_year dollars.
    
    Args:
        value (float): Nominal value.
        base_year (int): Year of original value.
        target_year (int): Year to adjust to.
        cpi_data (dict): Optional {year: CPI} dictionary.
    
    Returns:
        float: Inflation-adjusted value.
    """
    if cpi_data and base_year in cpi_data and target_year in cpi_data:
        return value * (cpi_data[target_year] / cpi_data[base_year])
    years_diff = target_year - base_year
    return value * (1 + ANNUAL_INFLATION_RATE) ** years_diff

def validate_data(df, state):
    """Validate dataset for required columns and state data."""
    required_columns = ['State', 'Date', 'Avg_Home_Value', 'HomeValue_Pct_Change', 'Is_Post_Announcement']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    df_state = df[df['State'] == state]
    if df_state.empty:
        raise ValueError(f"No data found for state: {state}")
    return df_state

def get_normal_growth_rate(df, state):
    """Calculate average annual housing price growth rate for non-announcement periods."""
    df_state = df[df['State'] == state]
    non_post_df = df_state[df_state['Is_Post_Announcement'] == 0]
    if non_post_df.empty:
        # Fallback: use all states' non-announcement data
        non_post_df = df[df['Is_Post_Announcement'] == 0]
        if non_post_df.empty:
            return 0.03  # Default 3% annual growth if no data
        print(f"No non-announcement data for {state}. Using average from all states.")
    return non_post_df['HomeValue_Pct_Change'].mean() / 100

def get_hyperscale_pct_change(df, state):
    """Calculate additional percentage change due to hyperscale announcement."""
    df_state = df[df['State'] == state]
    post_df = df_state[df_state['Is_Post_Announcement'] == 1]
    if post_df.empty:
        # Fallback: use other states' post-announcement data
        post_df = df[df['Is_Post_Announcement'] == 1]
        if post_df.empty:
            return 0.20  # Default 20% hyperscale impact
        print(f"No post-announcement data for {state}. Using fallback from other states.")
        return post_df['HomeValue_Pct_Change'].mean() / 100
    # Calculate excess growth over normal
    normal_rate = get_normal_growth_rate(df, state)
    total_rate = post_df['HomeValue_Pct_Change'].mean() / 100
    return max(total_rate - normal_rate, 0)  # Ensure non-negative hyperscale effect

def simple_simulate_house_price(state, current_price, years_after=1, base_year=2025, cpi_data=None):
    """
    Simulates house price with normal growth, hyperscale effect, and inflation adjustment.
    
    Args:
        state (str): Two-letter state code (e.g., 'NY').
        current_price (float): Current home price (in base_year dollars).
        years_after (int): Years after announcement.
        base_year (int): Base year for current_price (default: 2025).
        cpi_data (dict): Optional CPI data.
    
    Returns:
        tuple: (nominal_price, real_price) in target year and 2025 dollars.
    """
    df_state = validate_data(df, state)
    
    # Convert Date to datetime and extract year
    df_state['Date'] = pd.to_datetime(df_state['Date'])
    df_state['Year'] = df_state['Date'].dt.year
    
    # Adjust historical prices to 2025 dollars
    df_state['Avg_Home_Value_Real'] = df_state.apply(
        lambda row: adjust_for_inflation(row['Avg_Home_Value'], row['Year'], 2025, cpi_data), axis=1
    )
    
    # Get normal growth rate and hyperscale effect
    normal_growth = get_normal_growth_rate(df, state)
    hyperscale_effect = get_hyperscale_pct_change(df, state)
    
    # Calculate total annual growth rate post-announcement
    total_growth = normal_growth + hyperscale_effect
    print(f"{state} - Normal growth: {normal_growth*100:.1f}%, Hyperscale effect: {hyperscale_effect*100:.1f}%")
    
    # Simulate nominal price in target year
    target_year = base_year + years_after
    nominal_price = current_price * (1 + total_growth) ** years_after
    # Adjust to real 2025 dollars
    real_price = adjust_for_inflation(nominal_price, target_year, 2025, cpi_data)
    
    return nominal_price, real_price

def advanced_simulate_house_price(state, current_price, future_year=2026, base_year=2025, cpi_data=None):
    """
    Uses linear regression to predict house price, accounting for normal growth and hyperscale effect.
    
    Args:
        state (str): Two-letter state code (e.g., 'NY').
        current_price (float): Current home price (in base_year dollars).
        future_year (int): Year to predict for.
        base_year (int): Base year for current_price (default: 2025).
        cpi_data (dict): Optional CPI data.
    
    Returns:
        tuple: (nominal_price, real_price) in future_year and 2025 dollars.
    """
    df_state = validate_data(df, state)
    
    if len(df_state) < 3:
        print(f"Insufficient data points for {state}. Falling back to simple simulation.")
        return simple_simulate_house_price(state, current_price, years_after=future_year-base_year, base_year=base_year, cpi_data=cpi_data)
    
    # Convert Date to year and adjust for inflation
    df_state['Date'] = pd.to_datetime(df_state['Date'])
    df_state['Year'] = df_state['Date'].dt.year
    df_state['Avg_Home_Value_Real'] = df_state.apply(
        lambda row: adjust_for_inflation(row['Avg_Home_Value'], row['Year'], 2025, cpi_data), axis=1
    )
    
    # Prepare features and target (use real values)
    X = df_state[['Year', 'Is_Post_Announcement']].values
    y = df_state['Avg_Home_Value_Real'].values
    
    # Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict for future year (real value in 2025 dollars)
    future_features = np.array([[future_year, 1]])
    predicted_real_value = model.predict(future_features)[0]
    
    # Adjust to current price
    latest_real_value = df_state['Avg_Home_Value_Real'].iloc[-1]
    adjustment_factor = current_price / latest_real_value if latest_real_value != 0 else 1
    real_price = predicted_real_value * adjustment_factor
    
    # Convert to nominal price in future year
    nominal_price = adjust_for_inflation(real_price, 2025, future_year, cpi_data)
    
    # Fallback if prediction is unrealistic
    normal_growth = get_normal_growth_rate(df, state)
    if real_price < current_price * (1 + normal_growth) ** (future_year - base_year):
        print(f"Regression predicted lower than normal growth for {state}. Using simple simulation.")
        return simple_simulate_house_price(state, current_price, years_after=future_year-base_year, base_year=base_year, cpi_data=cpi_data)
    
    return nominal_price, real_price

# Example usage
try:
    state = 'LA'
    current_price = 200000.0  # Current price in 2025 dollars
    years_after = 5
    future_year = 2030
    base_year = 2025

    # Simple simulation
    nominal_simple, real_simple = simple_simulate_house_price(state, current_price, years_after, base_year, cpi_data)
    print(f"Simple simulation for {state} after {years_after} year(s):")
    print(f"  Nominal price (in {base_year+years_after} dollars): ${nominal_simple:,.2f}")
    print(f"  Real price (in 2025 dollars): ${real_simple:,.2f}")

    # Advanced simulation
    nominal_advanced, real_advanced = advanced_simulate_house_price(state, current_price, future_year, base_year, cpi_data)
    print(f"Advanced simulation for {state} in {future_year}:")
    print(f"  Nominal price (in {future_year} dollars): ${nominal_advanced:,.2f}")
    print(f"  Real price (in 2025 dollars): ${real_advanced:,.2f}")

except ValueError as e:
    print(f"Error: {e}")