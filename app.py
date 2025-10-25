from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import sys
import os

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

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

def get_state_housing_predictions(state, base_price=300000, base_year=2025):
    """
    Generate forward-looking housing predictions from 2025-2030
    using the predictive model
    """
    df_state = validate_data(df_housing, state)

    # Get growth rates from the model
    normal_growth = get_normal_growth_rate(df_housing, state)
    hyperscale_effect = get_hyperscale_pct_change(df_housing, state)

    # Generate predictions for years 2025-2030
    predictions = []
    for year in range(2025, 2031):
        years_after = year - base_year

        # Use the predictive model
        nominal, real, _, _ = simple_simulate_house_price(
            state, base_price, years_after=years_after, base_year=base_year
        )

        # Calculate year-over-year percentage change
        if year == base_year:
            pct_change = 0
        else:
            prev_nominal, _, _, _ = simple_simulate_house_price(
                state, base_price, years_after=years_after-1, base_year=base_year
            )
            pct_change = ((nominal - prev_nominal) / prev_nominal) * 100

        # All future years have data center impact
        is_post_announcement = 1

        predictions.append({
            'date': f'{year}-01-01',
            'year': year,
            'avg_home_value': float(nominal),
            'pct_change': float(pct_change),
            'is_post_announcement': is_post_announcement
        })

    return predictions

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
    """
    Get housing predictions for 2025-2030 (forward-looking)
    """
    try:
        if df_housing is None:
            return jsonify({'error': 'Housing data not available'}), 503

        state = request.args.get('state')
        base_price = request.args.get('base_price', 300000, type=float)

        if not state:
            return jsonify({'error': 'state parameter is required'}), 400

        state = state.upper()
        predictions = get_state_housing_predictions(state, base_price=base_price)

        return jsonify({
            'success': True,
            'data': {
                'state': state,
                'history': predictions  # Keep key name for backwards compatibility
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

STATE_NAME_TO_CODE = {
    'california': 'CA',
    'texas': 'TX',
    'virginia': 'VA',
    'washington': 'WA',
    'oregon': 'OR',
    'nevada': 'NV',
    'arizona': 'AZ',
    'utah': 'UT',
    'colorado': 'CO',
    'new-mexico': 'NM',
    'new mexico': 'NM',
    'louisiana': 'LA',
    'illinois': 'IL',
    'iowa': 'IA',
    'north carolina': 'NC',
    'south carolina': 'SC',
    'wisconsin': 'WI'
}

@app.route('/api/calculator/predict', methods=['POST'])
def calculator_predict():
    """
    Comprehensive calculator endpoint that predicts:
    1. Electricity bill impact based on data center presence
    2. Housing price increases due to hyperscale data centers
    3. Environmental impact metrics
    """
    try:
        data = request.json

        # Extract input data
        state_input = data.get('state', '').lower().strip()
        current_power_bill = float(data.get('currentPowerBill', 0))
        current_water_bill = float(data.get('currentWaterBill', 0))
        household_size = int(data.get('householdSize', 1))
        current_home_value = data.get('currentHomeValue')

        # Validate inputs
        if not state_input:
            return jsonify({'error': 'State is required'}), 400
        if current_power_bill <= 0:
            return jsonify({'error': 'Current power bill must be greater than 0'}), 400
        if household_size <= 0:
            return jsonify({'error': 'Household size must be greater than 0'}), 400

        # Convert state name to code
        state_code = STATE_NAME_TO_CODE.get(state_input)
        if not state_code:
            state_code = state_input.upper()

        # Calculate average household electricity consumption from bill
        # Assume average US rate of ~14 cents/kWh as baseline
        baseline_rate_cents = 14.0
        estimated_monthly_kwh = (current_power_bill / baseline_rate_cents) * 100

        # Predict electricity price impact using model
        # Simulate a medium-sized data center impact (500 MW)
        electricity_result = what_if_added_dc(
            df_electricity,
            beta_b,
            names_b,
            state_code=state_code,
            added_power_mw=500,  # Medium data center
            mode="assumption",
            include_added_load_in_sales=True
        )

        # Get current observed price
        try:
            observed_price_cents = float(df_electricity.loc[
                df_electricity.StateCode == state_code,
                "AvgRetailPrice_cents_per_kWh"
            ].iloc[0])
        except:
            observed_price_cents = baseline_rate_cents

        # Calculate new electricity bills
        new_price_cents = electricity_result['new_pred_c_per_kWh']
        price_increase_pct = ((new_price_cents - observed_price_cents) / observed_price_cents) * 100

        new_power_bill = current_power_bill * (1 + price_increase_pct / 100)
        power_bill_increase = new_power_bill - current_power_bill

        # Water bill impact (data centers use significant water for cooling)
        # Estimate 15-25% increase in water costs due to infrastructure strain
        water_increase_pct = 18.0
        new_water_bill = current_water_bill * (1 + water_increase_pct / 100)
        water_bill_increase = new_water_bill - current_water_bill

        total_monthly_increase = power_bill_increase + water_bill_increase
        annual_increase = total_monthly_increase * 12

        # Housing price prediction (if home value provided)
        housing_impact = None
        if current_home_value and df_housing is not None:
            try:
                nominal, real, normal_growth, hyperscale_effect = simple_simulate_house_price(
                    state_code,
                    float(current_home_value),
                    years_after=5,
                    base_year=2025
                )

                housing_impact = {
                    'current_value': current_home_value,
                    'projected_value_5yr': nominal,
                    'value_increase': nominal - current_home_value,
                    'normal_growth_rate_pct': normal_growth * 100,
                    'hyperscale_effect_pct': hyperscale_effect * 100,
                    'total_growth_rate_pct': (normal_growth + hyperscale_effect) * 100,
                    'explanation': f'Housing prices in {state_code} are projected to increase by {((nominal - current_home_value) / current_home_value * 100):.1f}% over 5 years due to data center development.'
                }
            except Exception as e:
                print(f"Housing prediction error: {e}")
                housing_impact = None

        # Environmental impact metrics (for a typical hyperscale data center)
        environmental_impact = {
            'water_usage_gallons_per_day': 2_300_000,  # 2.3M gallons/day typical
            'energy_usage_gwh_per_year': 18.7,  # GWh annually
            'carbon_footprint_tons_per_year': 8_700,  # metric tons CO2
            'land_use_acres': 12.3,
            'explanation': 'These metrics represent the typical impact of a hyperscale data center in your region.'
        }

        # Compile comprehensive response
        response = {
            'success': True,
            'data': {
                'state': state_code,
                'bills': {
                    'current': {
                        'power': current_power_bill,
                        'water': current_water_bill,
                        'total': current_power_bill + current_water_bill
                    },
                    'projected': {
                        'power': new_power_bill,
                        'water': new_water_bill,
                        'total': new_power_bill + new_water_bill
                    },
                    'increase': {
                        'power': power_bill_increase,
                        'power_pct': price_increase_pct,
                        'water': water_bill_increase,
                        'water_pct': water_increase_pct,
                        'total_monthly': total_monthly_increase,
                        'total_annual': annual_increase
                    }
                },
                'household': {
                    'size': household_size,
                    'per_person_monthly_impact': total_monthly_increase / household_size,
                    'estimated_monthly_kwh': estimated_monthly_kwh
                },
                'electricity_model': {
                    'observed_price_cents_per_kwh': observed_price_cents,
                    'baseline_pred_cents_per_kwh': electricity_result['baseline_pred_c_per_kWh'],
                    'new_pred_cents_per_kwh': new_price_cents,
                    'delta_cents_per_kwh': electricity_result['delta_c_per_kWh'],
                    'dc_share': electricity_result['dc_share_new']
                },
                'housing': housing_impact,
                'environmental': environmental_impact,
                'summary': {
                    'total_annual_cost_increase': annual_increase,
                    'five_year_cost_increase': annual_increase * 5,
                    'impact_level': 'high' if annual_increase > 500 else 'moderate' if annual_increase > 200 else 'low'
                }
            }
        }

        return jsonify(response)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Calculator error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/calculator/parse-bill', methods=['POST'])
def parse_bill():
    """
    Placeholder endpoint for bill image parsing.
    In production, this would use OCR (Tesseract, Google Vision API, etc.)
    For now, returns mock data based on file upload.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        bill_type = request.form.get('type', 'power')  # 'power' or 'water'

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # TODO: Implement actual OCR parsing
        # For now, return mock data
        mock_data = {
            'success': True,
            'data': {
                'bill_type': bill_type,
                'amount': 150.00 if bill_type == 'power' else 80.00,
                'usage': '850 kWh' if bill_type == 'power' else '5,000 gallons',
                'billing_period': '2025-01-01 to 2025-01-31',
                'parsed': True,
                'confidence': 0.95,
                'message': 'Bill parsing feature coming soon. Using default values for demo.'
            }
        }

        return jsonify(mock_data)

    except Exception as e:
        return jsonify({'error': f'Error parsing bill: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002, host='127.0.0.1')
