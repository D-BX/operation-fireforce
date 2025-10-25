// src/pages/Calculator.js
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Calculator() {
  const navigate = useNavigate();
  const [inputs, setInputs] = useState({
    state: '',
    currentPowerBill: '',
    currentWaterBill: '',
    householdSize: '',
    currentHomeValue: '',
    uploadMethod: 'manual' // 'manual' or 'upload'
  });
  const [uploadedFiles, setUploadedFiles] = useState({
    powerBill: null,
    waterBill: null
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('input');

  const states = [
    { value: 'california', label: 'California' },
    { value: 'texas', label: 'Texas' },
    { value: 'virginia', label: 'Virginia' },
    { value: 'washington', label: 'Washington' },
    { value: 'oregon', label: 'Oregon' },
    { value: 'nevada', label: 'Nevada' },
    { value: 'arizona', label: 'Arizona' },
    { value: 'utah', label: 'Utah' },
    { value: 'colorado', label: 'Colorado' },
    { value: 'new-mexico', label: 'New Mexico' },
  ];

  const handleFileUpload = (type, file) => {
    setUploadedFiles(prev => ({
      ...prev,
      [type]: file
    }));
  };

  const handleFileProcessing = async () => {
    // Handle file uploads if in upload mode
    if (inputs.uploadMethod === 'upload') {
      const formData = new FormData();

      if (uploadedFiles.powerBill) {
        formData.append('file', uploadedFiles.powerBill);
        formData.append('type', 'power');

        try {
          const response = await fetch('http://127.0.0.1:5002/api/calculator/parse-bill', {
            method: 'POST',
            body: formData
          });

          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              setInputs(prev => ({
                ...prev,
                currentPowerBill: data.data.amount.toString()
              }));
            }
          }
        } catch (error) {
          console.error('Error parsing power bill:', error);
        }
      }

      if (uploadedFiles.waterBill) {
        const waterFormData = new FormData();
        waterFormData.append('file', uploadedFiles.waterBill);
        waterFormData.append('type', 'water');

        try {
          const response = await fetch('http://127.0.0.1:5002/api/calculator/parse-bill', {
            method: 'POST',
            body: waterFormData
          });

          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              setInputs(prev => ({
                ...prev,
                currentWaterBill: data.data.amount.toString()
              }));
            }
          }
        } catch (error) {
          console.error('Error parsing water bill:', error);
        }
      }
    }
  };

  const handleCalculate = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Process uploaded files first if needed
      await handleFileProcessing();

      // Prepare request data
      const requestData = {
        state: inputs.state,
        currentPowerBill: parseFloat(inputs.currentPowerBill) || 0,
        currentWaterBill: parseFloat(inputs.currentWaterBill) || 0,
        householdSize: parseInt(inputs.householdSize) || 1,
        currentHomeValue: inputs.currentHomeValue ? parseFloat(inputs.currentHomeValue) : null
      };

      // Call backend API
      const response = await fetch('http://127.0.0.1:5002/api/calculator/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to calculate impact');
      }

      const result = await response.json();

      if (result.success) {
        const data = result.data;

        // Transform backend response to match frontend expectations
        setResults({
          currentPowerBill: data.bills.current.power,
          currentWaterBill: data.bills.current.water,
          projectedPowerBill: data.bills.projected.power,
          projectedWaterBill: data.bills.projected.water,
          powerIncrease: data.bills.increase.power,
          waterIncrease: data.bills.increase.water,
          totalMonthlyIncrease: data.bills.increase.total_monthly,
          annualIncrease: data.bills.increase.total_annual,
          householdSize: data.household.size,
          perPersonImpact: data.household.per_person_monthly_impact,
          state: inputs.state,
          stateCode: data.state,
          dataCenterImpact: {
            waterUsage: (data.environmental.water_usage_gallons_per_day / 1000000).toFixed(1),
            energyUsage: data.environmental.energy_usage_gwh_per_year.toFixed(1),
            landUse: data.environmental.land_use_acres.toFixed(1),
            carbonFootprint: (data.environmental.carbon_footprint_tons_per_year / 1000).toFixed(1)
          },
          housing: data.housing,
          electricityModel: data.electricity_model,
          summary: data.summary
        });

        setActiveTab('results');
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Error calculating impact:', error);
      alert(`Error: ${error.message}. Please check your inputs and try again.`);
    } finally {
      setLoading(false);
    }
  };

  const resetCalculator = () => {
    setInputs({
      state: '',
      currentPowerBill: '',
      currentWaterBill: '',
      householdSize: '',
      currentHomeValue: '',
      uploadMethod: 'manual'
    });
    setUploadedFiles({ powerBill: null, waterBill: null });
    setResults(null);
    setActiveTab('input');
  };

  return (
    <div className="calculator-page">
      <div className="container">
        <div className="calculator-header pattern-overlay">
          <button className="btn btn-secondary" onClick={() => navigate('/')}>
            ← Back to Home
          </button>
          <h1 className="calculator-title">Personal Impact Calculator</h1>
          <p className="calculator-subtitle">
            Upload your bills or enter manually to see how AI data centers could affect your costs
          </p>
          <div className="decorative-line"></div>
        </div>

        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'input' ? 'active' : ''}`}
            onClick={() => setActiveTab('input')}
          >
            Enter Information
          </button>
          {results && (
            <button 
              className={`tab-button ${activeTab === 'results' ? 'active' : ''}`}
              onClick={() => setActiveTab('results')}
            >
              Your Results
            </button>
          )}
        </div>

        {activeTab === 'input' && (
          <div className="calculator-content">
            <div className="input-methods">
              <div className="method-selector">
                <button 
                  className={`method-btn ${inputs.uploadMethod === 'manual' ? 'active' : ''}`}
                  onClick={() => setInputs({...inputs, uploadMethod: 'manual'})}
                >
                  Enter Manually
                </button>
                <button 
                  className={`method-btn ${inputs.uploadMethod === 'upload' ? 'active' : ''}`}
                  onClick={() => setInputs({...inputs, uploadMethod: 'upload'})}
                >
                  Upload Bills
                </button>
              </div>

              <form onSubmit={handleCalculate} className="calculator-form">
                <div className="form-section">
                  <h3>Location Information</h3>
                  <div className="form-group">
                    <label className="form-label">State</label>
          <select 
                      className="form-select"
            value={inputs.state}
            onChange={(e) => setInputs({...inputs, state: e.target.value})}
            required
          >
                      <option value="">Choose your state...</option>
                      {states.map(state => (
                        <option key={state.value} value={state.value}>
                          {state.label}
                        </option>
                      ))}
          </select>
                  </div>
        </div>

                {inputs.uploadMethod === 'manual' ? (
                  <div className="form-section">
                    <h3>Current Bills</h3>
                    <div className="form-row">
                      <div className="form-group">
                        <label className="form-label">Monthly Power Bill ($)</label>
          <input 
            type="number" 
                          className="form-input"
            value={inputs.currentPowerBill}
            onChange={(e) => setInputs({...inputs, currentPowerBill: e.target.value})}
                          placeholder="150.00"
            required
          />
        </div>
                      <div className="form-group">
                        <label className="form-label">Monthly Water Bill ($)</label>
          <input 
            type="number" 
                          className="form-input"
            value={inputs.currentWaterBill}
            onChange={(e) => setInputs({...inputs, currentWaterBill: e.target.value})}
                          placeholder="80.00"
                          required
                        />
                      </div>
                    </div>
                    <div className="form-group">
                      <label className="form-label">Household Size</label>
                      <input
                        type="number"
                        className="form-input"
                        value={inputs.householdSize}
                        onChange={(e) => setInputs({...inputs, householdSize: e.target.value})}
                        placeholder="4"
                        min="1"
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Current Home Value (Optional)</label>
                      <input
                        type="number"
                        className="form-input"
                        value={inputs.currentHomeValue}
                        onChange={(e) => setInputs({...inputs, currentHomeValue: e.target.value})}
                        placeholder="350000"
                        min="0"
                      />
                      <small className="form-hint">Enter to see housing market impact predictions</small>
                    </div>
                  </div>
                ) : (
                  <div className="form-section">
                    <h3>Upload Your Bills</h3>
                    <div className="upload-section">
                      <div className="upload-group">
                        <label className="upload-label">
                          <div className="upload-content">
                            <h4>Power Bill</h4>
                            <p>Upload your electricity bill (PDF, JPG, PNG)</p>
                            <input 
                              type="file" 
                              accept=".pdf,.jpg,.jpeg,.png"
                              onChange={(e) => handleFileUpload('powerBill', e.target.files[0])}
                              className="file-input"
                            />
                            {uploadedFiles.powerBill && (
                              <div className="file-info">
                                {uploadedFiles.powerBill.name}
                              </div>
                            )}
                          </div>
                        </label>
                      </div>
                      <div className="upload-group">
                        <label className="upload-label">
                          <div className="upload-content">
                            <h4>Water Bill</h4>
                            <p>Upload your water bill (PDF, JPG, PNG)</p>
                            <input 
                              type="file" 
                              accept=".pdf,.jpg,.jpeg,.png"
                              onChange={(e) => handleFileUpload('waterBill', e.target.files[0])}
                              className="file-input"
                            />
                            {uploadedFiles.waterBill && (
                              <div className="file-info">
                                {uploadedFiles.waterBill.name}
                              </div>
                            )}
                          </div>
                        </label>
                      </div>
                    </div>
                    <div className="form-group">
                      <label className="form-label">Household Size</label>
                      <input
                        type="number"
                        className="form-input"
                        value={inputs.householdSize}
                        onChange={(e) => setInputs({...inputs, householdSize: e.target.value})}
                        placeholder="4"
                        min="1"
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Current Home Value (Optional)</label>
                      <input
                        type="number"
                        className="form-input"
                        value={inputs.currentHomeValue}
                        onChange={(e) => setInputs({...inputs, currentHomeValue: e.target.value})}
                        placeholder="350000"
                        min="0"
                      />
                      <small className="form-hint">Enter to see housing market impact predictions</small>
                    </div>
                  </div>
                )}

                <div className="form-actions">
                  <button 
                    type="submit" 
                    className="btn btn-primary btn-lg"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="loading-spinner"></span>
                        Calculating...
                      </>
                    ) : (
                      <>
                        Calculate My Impact
                      </>
                    )}
                  </button>
                </div>
      </form>
            </div>
          </div>
        )}

        {activeTab === 'results' && results && (
          <div className="results-content">
            <div className="results-header pattern-overlay">
              <h2>Your Personalized Impact Report</h2>
              <p>Based on your location and current bills</p>
              <div className="decorative-line"></div>
            </div>

            <div className="results-grid">
              <div className="results-card enhanced-card">
                <h3>Bill Impact Analysis</h3>
                <div className="bill-comparison">
                  <div className="bill-item">
                    <div className="bill-label">Current Monthly Bills</div>
                    <div className="bill-amount">${results.currentPowerBill + results.currentWaterBill}</div>
                  </div>
                  <div className="bill-increase">
                    <div className="increase-label">Monthly Increase</div>
                    <div className="increase-amount">+${results.totalMonthlyIncrease.toFixed(2)}</div>
                  </div>
                </div>
              </div>

              <div className="results-card enhanced-card">
                <h3>Annual Impact</h3>
                <div className="annual-impact">
                  <div className="impact-stat">
                    <div className="stat-value">${results.annualIncrease.toFixed(2)}</div>
                    <div className="stat-label">Additional Cost Per Year</div>
                  </div>
                  <div className="impact-stat">
                    <div className="stat-value">${results.perPersonImpact.toFixed(2)}</div>
                    <div className="stat-label">Cost Per Person Per Month</div>
                  </div>
                </div>
              </div>

              <div className="results-card enhanced-card">
                <h3>Cost Breakdown</h3>
                <div className="breakdown">
                  <div className="breakdown-item">
                    <span className="breakdown-label">Power Bill Increase</span>
                    <span className="breakdown-value">+${results.powerIncrease.toFixed(2)}/month</span>
                  </div>
                  <div className="breakdown-item">
                    <span className="breakdown-label">Water Bill Increase</span>
                    <span className="breakdown-value">+${results.waterIncrease.toFixed(2)}/month</span>
                  </div>
                </div>
              </div>

              <div className="results-card enhanced-card">
                <h3>Environmental Impact</h3>
                <div className="environmental-stats">
                  <div className="env-stat">
                    <div className="env-content">
                      <div className="env-value">{results.dataCenterImpact.waterUsage}M</div>
                      <div className="env-label">Gallons Water/Day</div>
                    </div>
                  </div>
                  <div className="env-stat">
                    <div className="env-content">
                      <div className="env-value">{results.dataCenterImpact.energyUsage}GWh</div>
                      <div className="env-label">Energy/Year</div>
                    </div>
                  </div>
                  <div className="env-stat">
                    <div className="env-content">
                      <div className="env-value">{results.dataCenterImpact.carbonFootprint}K</div>
                      <div className="env-label">Tons CO2/Year</div>
                    </div>
                  </div>
                </div>
              </div>

              {results.housing && (
                <div className="results-card card">
                  <h3>Housing Market Impact (2025-2030 Projection)</h3>
                  <div className="housing-impact">
                    <div className="impact-stat">
                      <div className="stat-value">${results.housing.projected_value_5yr.toLocaleString('en-US', {maximumFractionDigits: 0})}</div>
                      <div className="stat-label">Projected Home Value (2030)</div>
                    </div>
                    <div className="impact-stat">
                      <div className="stat-value">+${results.housing.value_increase.toLocaleString('en-US', {maximumFractionDigits: 0})}</div>
                      <div className="stat-label">Expected Value Increase</div>
                    </div>
                    <div className="impact-stat">
                      <div className="stat-value">{results.housing.total_growth_rate_pct.toFixed(1)}%/yr</div>
                      <div className="stat-label">Total Growth Rate</div>
                    </div>
                    <div className="impact-breakdown">
                      <div className="breakdown-item">
                        <span className="breakdown-label">Normal Growth Rate</span>
                        <span className="breakdown-value">{results.housing.normal_growth_rate_pct.toFixed(1)}%/yr</span>
                      </div>
                      <div className="breakdown-item">
                        <span className="breakdown-label">Data Center Effect</span>
                        <span className="breakdown-value highlighted">+{results.housing.hyperscale_effect_pct.toFixed(1)}%/yr</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {results.electricityModel && (
                <div className="results-card enhanced-card">
                  <h3>Technical Details</h3>
                  <div className="technical-details">
                    <div className="detail-item">
                      <span className="detail-label">Current Electricity Rate</span>
                      <span className="detail-value">{results.electricityModel.observed_price_cents_per_kwh.toFixed(2)} ¢/kWh</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Projected Rate (with data center)</span>
                      <span className="detail-value">{results.electricityModel.new_pred_cents_per_kwh.toFixed(2)} ¢/kWh</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Rate Increase</span>
                      <span className="detail-value highlighted">+{results.electricityModel.delta_cents_per_kwh.toFixed(2)} ¢/kWh</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Impact Severity</span>
                      <div className="impact-severity">
                        <span className={`detail-value badge ${results.summary?.impact_level || 'moderate'}`}>
                          {(results.summary?.impact_level || 'moderate').toUpperCase()}
                        </span>
                        <div className="impact-indicator">
                          <div className="impact-bar">
                            <div className={`impact-fill ${results.summary?.impact_level || 'moderate'}`}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="results-actions">
              <button 
                className="btn btn-primary btn-lg"
                onClick={() => navigate(`/report/${results.state}`)}
              >
                View State Report
              </button>
              <button 
                className="btn btn-secondary btn-lg"
                onClick={resetCalculator}
              >
                Calculate Again
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Calculator;
