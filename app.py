from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import sys
import os

app = Flask(__name__)
CORS(app)

sys.path.append(os.path.dirname(__file__))

from model import (
    load_data,
    build_features,
    build_features_baseline,
    fit_ols,
    what_if_added_dc
)

df_electricity = None
beta_b = None
beta_f = None
names_b = None
names_f = None

df_housing = None
cpi_data = {
    2000: 172.2, 2001: 177.1, 2002: 179.9, 2003: 184.0, 2004: 188.9,
    2005: 195.3, 2006: 201.6, 2007: 207.3, 2008: 215.3, 2009: 214.5,
    2010: 218.1, 2011: 224.9, 2012: 229.6, 2013: 233.0, 2014: 236.7,
    2015: 237.0, 2016: 240.0, 2017: 245.1, 2018: 251.1, 2019: 255.7,
    2020: 258.8, 2021: 271.0, 2022: 296.8, 2023: 308.5, 2024: 319.6,
    2025: 320.0
}
ANNUAL_INFLATION_RATE = 0.025

def initialize_models():
    global df_electricity, beta_b, beta_f, names_b, names_f, df_housing

    df_electricity = load_data()
    Xb, y, names_b = build_features_baseline(df_electricity)
    beta_b = fit_ols(Xb, y)

    Xf, _, names_f = build_features(df_electricity)
    beta_f = fit_ols(Xf, y)

    housing_path = 'csv-generation/house/processed_states_hyperscale.csv'
    if os.path.exists(housing_path):
        df_housing = pd.read_csv(housing_path)
    else:
        print(f"Warning: Housing data file not found at {housing_path}")

initialize_models()

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
        return post_df['HomeValue_Pct_Change'].mean() / 100
    normal_rate = get_normal_growth_rate(df, state)
    total_rate = post_df['HomeValue_Pct_Change'].mean() / 100
    return max(total_rate - normal_rate, 0)

def simple_simulate_house_price(state, current_price, years_after=1, base_year=2025):
    df_state = validate_data(df_housing, state)

    df_state = df_state.copy()
    df_state['Date'] = pd.to_datetime(df_state['Date'])
    df_state['Year'] = df_state['Date'].dt.year

    df_state['Avg_Home_Value_Real'] = df_state.apply(
        lambda row: adjust_for_inflation(row['Avg_Home_Value'], row['Year'], 2025, cpi_data), axis=1
    )

    normal_growth = get_normal_growth_rate(df_housing, state)
    hyperscale_effect = get_hyperscale_pct_change(df_housing, state)

    total_growth = normal_growth + hyperscale_effect

    target_year = base_year + years_after
    nominal_price = current_price * (1 + total_growth) ** years_after
    real_price = adjust_for_inflation(nominal_price, target_year, 2025, cpi_data)

    return nominal_price, real_price, normal_growth, hyperscale_effect

def advanced_simulate_house_price(state, current_price, future_year=2026, base_year=2025):
    df_state = validate_data(df_housing, state)

    if len(df_state) < 3:
        return simple_simulate_house_price(state, current_price, years_after=future_year-base_year, base_year=base_year)

    df_state = df_state.copy()
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

    normal_growth = get_normal_growth_rate(df_housing, state)
    if real_price < current_price * (1 + normal_growth) ** (future_year - base_year):
        return simple_simulate_house_price(state, current_price, years_after=future_year-base_year, base_year=base_year)

    hyperscale_effect = get_hyperscale_pct_change(df_housing, state)
    return nominal_price, real_price, normal_growth, hyperscale_effect

def get_state_housing_history(state):
    df_state = validate_data(df_housing, state)
    df_state = df_state.copy()
    df_state['Date'] = pd.to_datetime(df_state['Date'])
    df_state = df_state.sort_values('Date')

    history = []
    for _, row in df_state.iterrows():
        history.append({
            'date': row['Date'].strftime('%Y-%m-%d'),
            'year': int(row['Date'].year),
            'avg_home_value': float(row['Avg_Home_Value']),
            'pct_change': float(row['HomeValue_Pct_Change']) if pd.notna(row['HomeValue_Pct_Change']) else None,
            'is_post_announcement': int(row['Is_Post_Announcement'])
        })

    return history

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'models_loaded': {
            'electricity': df_electricity is not None,
            'housing': df_housing is not None
        }
    })

@app.route('/api/electricity/predict', methods=['POST'])
def predict_electricity():
    try:
        data = request.json
        state_code = data.get('state')
        added_power_mw = data.get('added_power_mw')
        added_annual_mwh = data.get('added_annual_mwh')
        mode = data.get('mode', 'assumption')
        include_in_sales = data.get('include_in_sales', True)

        if not state_code:
            return jsonify({'error': 'state is required'}), 400

        if added_power_mw is None and added_annual_mwh is None:
            return jsonify({'error': 'Either added_power_mw or added_annual_mwh is required'}), 400

        result = what_if_added_dc(
            df_electricity,
            beta_b if mode == "assumption" else beta_f,
            names_b if mode == "assumption" else names_f,
            state_code=state_code,
            added_power_mw=added_power_mw,
            added_annual_mwh=added_annual_mwh,
            mode=mode,
            include_added_load_in_sales=include_in_sales
        )

        observed = float(df_electricity.loc[
            df_electricity.StateCode == state_code.upper(),
            "AvgRetailPrice_cents_per_kWh"
        ].iloc[0])

        result['observed_price_c_per_kWh'] = observed

        return jsonify({
            'success': True,
            'data': result
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/housing/predict', methods=['POST'])
def predict_housing():
    try:
        if df_housing is None:
            return jsonify({'error': 'Housing data not available'}), 503

        data = request.json
        state = data.get('state')
        current_price = data.get('current_price')
        years_after = data.get('years_after', 1)
        future_year = data.get('future_year')
        base_year = data.get('base_year', 2025)
        method = data.get('method', 'simple')

        if not state:
            return jsonify({'error': 'state is required'}), 400
        if current_price is None:
            return jsonify({'error': 'current_price is required'}), 400

        state = state.upper()

        if method == 'advanced' and future_year:
            nominal, real, normal_growth, hyperscale_effect = advanced_simulate_house_price(
                state, current_price, future_year, base_year
            )
            target_year = future_year
        else:
            nominal, real, normal_growth, hyperscale_effect = simple_simulate_house_price(
                state, current_price, years_after, base_year
            )
            target_year = base_year + years_after

        return jsonify({
            'success': True,
            'data': {
                'state': state,
                'current_price': current_price,
                'target_year': target_year,
                'nominal_price': nominal,
                'real_price_2025_dollars': real,
                'nominal_increase_pct': ((nominal - current_price) / current_price * 100),
                'normal_growth_rate': normal_growth * 100,
                'hyperscale_effect_rate': hyperscale_effect * 100,
                'total_growth_rate': (normal_growth + hyperscale_effect) * 100
            }
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/housing/history', methods=['GET'])
def housing_history():
    try:
        if df_housing is None:
            return jsonify({'error': 'Housing data not available'}), 503

        state = request.args.get('state')
        if not state:
            return jsonify({'error': 'state parameter is required'}), 400

        state = state.upper()
        history = get_state_housing_history(state)

        return jsonify({
            'success': True,
            'data': {
                'state': state,
                'history': history
            }
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/states', methods=['GET'])
def get_states():
    try:
        states_electricity = df_electricity['StateCode'].unique().tolist() if df_electricity is not None else []
        states_housing = df_housing['State'].unique().tolist() if df_housing is not None else []

        return jsonify({
            'success': True,
            'data': {
                'electricity_states': sorted(states_electricity),
                'housing_states': sorted(states_housing),
                'all_states': sorted(list(set(states_electricity + states_housing)))
            }
        })
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
