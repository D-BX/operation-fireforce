import { useEffect, useState } from 'react';
import { apiService } from '../services/apiService';
import { getStateCode } from '../utils/stateMapping';

function HousingChart({ state, currentPrice = 300000 }) {
  const [housingData, setHousingData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      const stateCode = getStateCode(state);

      const historyResult = await apiService.getHousingHistory(stateCode, currentPrice);
      if (historyResult.success) {
        setHousingData(historyResult.data);
      } else {
        setError(historyResult.error);
      }

      const predictionResult = await apiService.predictHousing({
        state: stateCode,
        currentPrice: currentPrice,
        yearsAfter: 5,
        method: 'simple'
      });

      if (predictionResult.success) {
        setPrediction(predictionResult.data);
      }

      setLoading(false);
    };

    fetchData();
  }, [state, currentPrice]);

  if (loading) {
    return <div className="loading">Loading housing data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  const history = housingData?.history || [];

  if (history.length === 0) {
    return (
      <div className="housing-chart card">
        <h3>Housing Price History - {getStateCode(state)}</h3>
        <p style={{ color: 'var(--text-secondary)', padding: '2rem', textAlign: 'center' }}>
          No housing data available for this state. Please ensure the backend is running and data exists.
        </p>
      </div>
    );
  }

  const maxValue = Math.max(...history.map(h => h.avg_home_value), 0);
  const minValue = Math.min(...history.map(h => h.avg_home_value), 0);
  const range = maxValue - minValue || 1;

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="housing-chart-container">
      <div className="housing-chart card">
        <h3>Housing Price Predictions (2025-2030) - {getStateCode(state)}</h3>

        <div className="chart-wrapper">
          <div className="line-chart-container">
            <svg viewBox="0 0 400 200" className="housing-line-chart">
              <defs>
                <linearGradient id="priceGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="var(--color-red)" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="var(--color-red)" stopOpacity="0.05" />
                </linearGradient>
              </defs>

              {history.length > 0 && (
                <>
                  <polyline
                    fill="url(#priceGradient)"
                    stroke="none"
                    points={history.map((point, index) => {
                      const x = 50 + (index / (history.length - 1)) * 300;
                      const normalizedValue = (point.avg_home_value - minValue) / range;
                      const y = 170 - (normalizedValue * 140);
                      return `${x},${y}`;
                    }).join(' ') + ` 350,170 50,170`}
                  />

                  <polyline
                    fill="none"
                    stroke="var(--color-red)"
                    strokeWidth="3"
                    points={history.map((point, index) => {
                      const x = 50 + (index / (history.length - 1)) * 300;
                      const normalizedValue = (point.avg_home_value - minValue) / range;
                      const y = 170 - (normalizedValue * 140);
                      return `${x},${y}`;
                    }).join(' ')}
                  />

                  {history.map((point, index) => {
                    const x = 50 + (index / (history.length - 1)) * 300;
                    const normalizedValue = (point.avg_home_value - minValue) / range;
                    const y = 170 - (normalizedValue * 140);

                    return (
                      <g key={index}>
                        <circle
                          cx={x}
                          cy={y}
                          r="5"
                          fill="var(--color-red)"
                        />
                        <text
                          x={x}
                          y="190"
                          textAnchor="middle"
                          fontSize="10"
                          fill="var(--color-text-secondary)"
                        >
                          {point.year}
                        </text>
                      </g>
                    );
                  })}
                </>
              )}

              <line x1="50" y1="30" x2="50" y2="170" stroke="var(--color-border)" strokeWidth="1" />
              <line x1="50" y1="170" x2="350" y2="170" stroke="var(--color-border)" strokeWidth="1" />
            </svg>
          </div>

          <div className="chart-legend">
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: 'var(--color-red)' }}></div>
              <span>Projected with Data Center Impact</span>
            </div>
          </div>
        </div>

        {history.length > 0 && (
          <div className="chart-stats">
            <div className="stat-box">
              <div className="stat-label">Starting Price (2025)</div>
              <div className="stat-value">{formatCurrency(currentPrice)}</div>
              <div className="stat-year">{history[0].year}</div>
            </div>
            <div className="stat-box">
              <div className="stat-label">Projected Price (2030)</div>
              <div className="stat-value">
                {prediction ? formatCurrency(prediction.nominal_price) : formatCurrency(maxValue)}
              </div>
              <div className="stat-year">{history[history.length - 1].year}</div>
            </div>
            <div className="stat-box">
              <div className="stat-label">Total Projected Increase</div>
              <div className="stat-value">
                {prediction ?
                  `${prediction.nominal_increase_pct.toFixed(1)}%` :
                  currentPrice > 0 ?
                    `${((maxValue - currentPrice) / currentPrice * 100).toFixed(1)}%` :
                    'N/A'
                }
              </div>
              <div className="stat-year">{history[0].year}-{history[history.length - 1].year}</div>
            </div>
          </div>
        )}
      </div>

      {prediction && (
        <div className="housing-prediction card">
          <h3>5-Year Price Forecast</h3>
          <div className="prediction-grid">
            <div className="prediction-item">
              <div className="prediction-label">Current Price (2025)</div>
              <div className="prediction-value">{formatCurrency(prediction.current_price)}</div>
            </div>
            <div className="prediction-item">
              <div className="prediction-label">Predicted Price ({prediction.target_year})</div>
              <div className="prediction-value highlight">{formatCurrency(prediction.nominal_price)}</div>
            </div>
            <div className="prediction-item">
              <div className="prediction-label">Expected Increase</div>
              <div className="prediction-value increase">
                +{formatCurrency(prediction.nominal_price - prediction.current_price)}
              </div>
              <div className="prediction-percentage">
                ({prediction.nominal_increase_pct.toFixed(1)}%)
              </div>
            </div>
            <div className="prediction-item">
              <div className="prediction-label">Normal Growth Rate</div>
              <div className="prediction-value">{prediction.normal_growth_rate.toFixed(2)}%/yr</div>
            </div>
            <div className="prediction-item">
              <div className="prediction-label">Data Center Impact</div>
              <div className="prediction-value warning">
                +{prediction.hyperscale_effect_rate.toFixed(2)}%/yr
              </div>
            </div>
            <div className="prediction-item">
              <div className="prediction-label">Total Growth Rate</div>
              <div className="prediction-value">{prediction.total_growth_rate.toFixed(2)}%/yr</div>
            </div>
          </div>

          <div className="prediction-visual">
            <div className="bar-comparison">
              <div className="bar-item">
                <div className="bar-label">Current</div>
                <div className="bar-container">
                  <div
                    className="bar current"
                    style={{ width: '100%', height: '40px' }}
                  >
                    {formatCurrency(prediction.current_price)}
                  </div>
                </div>
              </div>
              <div className="bar-item">
                <div className="bar-label">Predicted ({prediction.target_year})</div>
                <div className="bar-container">
                  <div
                    className="bar predicted"
                    style={{
                      width: `${(prediction.nominal_price / prediction.current_price) * 100}%`,
                      height: '40px'
                    }}
                  >
                    {formatCurrency(prediction.nominal_price)}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="prediction-note">
            <p>
              <strong>Projected Impact:</strong> Housing prices in {getStateCode(state)} are projected to grow at{' '}
              <strong>{prediction.total_growth_rate.toFixed(1)}%</strong> per year through 2030 with data center development.
              This combines normal market growth of {prediction.normal_growth_rate.toFixed(1)}% annually plus an additional{' '}
              {prediction.hyperscale_effect_rate.toFixed(1)}% annual increase from AI data center impact,
              resulting in a total {prediction.nominal_increase_pct.toFixed(1)}% increase by {prediction.target_year}.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default HousingChart;
