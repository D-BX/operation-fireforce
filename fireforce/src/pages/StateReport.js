// src/pages/StateReport.js
import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getStateInfo } from '../services/geminiService';

function StateReport() {
  const { state } = useParams(); // Gets the state from URL
  const navigate = useNavigate();
  const [newsData, setNewsData] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch or calculate report data for this state
    // Call your linear regression model here
    // Call Gemini API for news/legislation

    const fetchNews = async () => {
        setLoading(true);
        const result = await getStateInfo(state);
      
        if (result.success) {
            setNewsData(result.data);
            setError(null);
        } else {
            setError(result.error);
        }
        setLoading(false);
    };

    
    // Simulated data loading
    setTimeout(() => {
      setReportData({
        state: state,
        powerIncrease: 15.5,
        waterIncrease: 8.2,
        // ... other data
      });
      setLoading(false);
    }, 1000);
    fetchNews();
  }, [state]);

  if (loading) {
    return <div className="loading">Loading report for {state}...</div>;
  }

  return (
    <div className="state-report">
      <button onClick={() => navigate('/')}>← Back to Home</button>
      
      <h1>{state.toUpperCase()} Impact Report</h1>
      
      <section className="predictions">
        <h2>Predicted Bill Increases</h2>
        <div className="metric">
          <h3>Power Bill Increase</h3>
          <p className="value">{reportData.powerIncrease}%</p>
        </div>
        <div className="metric">
          <h3>Water Bill Increase</h3>
          <p className="value">{reportData.waterIncrease}%</p>
        </div>
      </section>

      <section className="news">
        <h2>Related News & Legislation</h2>
        {/* Gemini API results will go here */}
      </section>

      <button onClick={() => navigate('/calculator')}>
        Calculate Your Personal Impact
      </button>
    </div>
  );
}

export default StateReport;
