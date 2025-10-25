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

  const handleCalculate = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    setTimeout(() => {
      const powerBill = parseFloat(inputs.currentPowerBill) || 0;
      const waterBill = parseFloat(inputs.currentWaterBill) || 0;
      const householdSize = parseInt(inputs.householdSize) || 1;
      
      const stateMultipliers = {
        california: { power: 0.18, water: 0.12 },
        texas: { power: 0.15, water: 0.08 },
        virginia: { power: 0.20, water: 0.15 },
        washington: { power: 0.16, water: 0.10 },
        oregon: { power: 0.14, water: 0.09 },
        nevada: { power: 0.22, water: 0.18 },
        arizona: { power: 0.25, water: 0.20 },
        utah: { power: 0.17, water: 0.11 },
        colorado: { power: 0.19, water: 0.13 },
        'new-mexico': { power: 0.21, water: 0.16 }
      };
      
      const multipliers = stateMultipliers[inputs.state] || { power: 0.15, water: 0.10 };
      
      const powerIncrease = powerBill * multipliers.power;
      const waterIncrease = waterBill * multipliers.water;
      const totalIncrease = powerIncrease + waterIncrease;
      const annualIncrease = totalIncrease * 12;
      
      setResults({
        currentPowerBill: powerBill,
        currentWaterBill: waterBill,
        projectedPowerBill: powerBill + powerIncrease,
        projectedWaterBill: waterBill + waterIncrease,
        powerIncrease: powerIncrease,
        waterIncrease: waterIncrease,
        totalMonthlyIncrease: totalIncrease,
        annualIncrease: annualIncrease,
        householdSize: householdSize,
        perPersonImpact: totalIncrease / householdSize,
        state: inputs.state,
        dataCenterImpact: {
          waterUsage: 2.3,
          energyUsage: 18.7,
          landUse: 12.3,
          carbonFootprint: 8.7
        }
      });
      
      setLoading(false);
      setActiveTab('results');
    }, 2000);
  };

  const resetCalculator = () => {
    setInputs({
      state: '',
      currentPowerBill: '',
      currentWaterBill: '',
      householdSize: '',
      uploadMethod: 'manual'
    });
    setUploadedFiles({ powerBill: null, waterBill: null });
    setResults(null);
    setActiveTab('input');
  };

  return (
    <div className="calculator-page">
      <div className="container">
        <div className="calculator-header">
          <button className="btn btn-secondary" onClick={() => navigate('/')}>
            ← Back to Home
          </button>
          <h1 className="calculator-title">Personal Impact Calculator</h1>
          <p className="calculator-subtitle">
            Upload your bills or enter manually to see how AI data centers could affect your costs
          </p>
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
            <div className="results-header">
              <h2>Your Personalized Impact Report</h2>
              <p>Based on your location and current bills</p>
            </div>

            <div className="results-grid">
              <div className="results-card card">
                <h3>Bill Impact Analysis</h3>
                <div className="bill-comparison">
                  <div className="bill-item">
                    <div className="bill-label">Current Monthly Bills</div>
                    <div className="bill-amount">${results.currentPowerBill + results.currentWaterBill}</div>
                  </div>
                  <div className="bill-item projected">
                    <div className="bill-label">Projected Monthly Bills</div>
                    <div className="bill-amount">${(results.projectedPowerBill + results.projectedWaterBill).toFixed(2)}</div>
                  </div>
                  <div className="bill-increase">
                    <div className="increase-label">Monthly Increase</div>
                    <div className="increase-amount">+${results.totalMonthlyIncrease.toFixed(2)}</div>
                  </div>
                </div>
              </div>

              <div className="results-card card">
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

              <div className="results-card card">
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

              <div className="results-card card">
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
                      <div className="env-value">{results.dataCenterImpact.carbonFootprint}T</div>
                      <div className="env-label">CO2/Year</div>
                    </div>
                  </div>
                </div>
              </div>
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
