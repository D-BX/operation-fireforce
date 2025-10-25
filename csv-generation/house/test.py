import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Load your CSV file
df = pd.read_csv('processed_states_hyperscale.csv')

def simple_simulate_house_price(state, current_price, years_after=1):
    """
    Simulates house price after a hyperscale announcement using average post-announcement growth.
    
    Args:
        state (str): Two-letter state code (e.g., 'AK').
        current_price (float): Current home price.
        years_after (int): Number of years after announcement to simulate (default: 1).
    
    Returns:
        float: Simulated home price after the announcement.
    """
    # Filter for the given state
    df_state = df[df['State'] == state].copy()
    
    if df_state.empty:
        raise ValueError(f"No data found for state: {state}")
    
    # Convert Date to datetime
    df_state['Date'] = pd.to_datetime(df_state['Date'])
    df_state = df_state.sort_values('Date')
    
    # Filter post-announcement data
    post_df = df_state[df_state['Is_Post_Announcement'] == 1]
    
    if post_df.empty:
        print(f"No post-announcement data for {state}. Using default 20% increase.")
        return current_price * (1 + 0.20) ** years_after  # Default 20% based on typical hyperscale impact
    
    # Calculate average annual percentage change post-announcement
    avg_pct_change = post_df['HomeValue_Pct_Change'].mean() / 100  # Convert to decimal
    
    # Simulate compounded growth
    simulated_price = current_price * (1 + avg_pct_change) ** years_after
    
    return simulated_price

def advanced_simulate_house_price(state, current_price, future_year=2026):
    """
    Uses linear regression to predict house price after announcement.
    
    Features: Year, Is_Post_Announcement.
    Target: Avg_Home_Value.
    Predicts for a future year assuming post-announcement (Is_Post_Announcement=1).
    
    Args:
        state (str): Two-letter state code (e.g., 'AK').
        current_price (float): Current home price.
        future_year (int): Year to predict for (default: 2026).
    
    Returns:
        float: Simulated home price.
    """
    df_state = df[df['State'] == state].copy()
    
    if len(df_state) < 2:
        raise ValueError(f"Insufficient data for state: {state}")
    
    # Prepare features and target
    df_state['Year'] = pd.to_datetime(df_state['Date']).dt.year
    X = df_state[['Year', 'Is_Post_Announcement']].values
    y = df_state['Avg_Home_Value'].values
    
    # Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict for future year post-announcement
    future_features = np.array([[future_year, 1]])  # 1 for post-announcement
    predicted_value = model.predict(future_features)[0]
    
    # Adjust to current price as baseline
    latest_value = df_state['Avg_Home_Value'].iloc[-1]
    adjustment_factor = current_price / latest_value if latest_value != 0 else 1
    simulated_price = predicted_value * adjustment_factor
    
    return max(simulated_price, current_price)  # Ensure no negative prediction

# Example usage
try:
    state = 'VA'  # Replace with desired state
    current_price = 200000.0  # Replace with actual current house price
    years_after = 1  # Number of years after announcement
    future_year = 2026  # Year for advanced prediction

    # Simple simulation
    simple_price = simple_simulate_house_price(state, current_price, years_after)
    print(f"Simple simulation for {state} after {years_after} year(s): ${simple_price:,.2f}")

    # Advanced simulation
    advanced_price = advanced_simulate_house_price(state, current_price, future_year)
    print(f"Advanced simulation for {state} in {future_year}: ${advanced_price:,.2f}")

except ValueError as e:
    print(f"Error: {e}")