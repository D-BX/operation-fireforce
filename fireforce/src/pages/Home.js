// src/pages/Home.js
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

function Home() {
  const navigate = useNavigate();
  const [selectedState, setSelectedState] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedState) {
      navigate(`/report/${selectedState}`);
    }
  };

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

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">
              The Hidden Cost of AI Data Centers
            </h1>
            <p className="hero-subtitle">
              Understanding the environmental and economic impact of artificial intelligence infrastructure on local communities.
            </p>
            <div className="hero-stats">
              <div className="stat-item">
                <div className="stat-number">15.5%</div>
                <div className="stat-label">Average Power Bill Increase</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">8.2%</div>
                <div className="stat-label">Average Water Bill Increase</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">2.3M</div>
                <div className="stat-label">Gallons Water per Day</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Statement */}
      <section className="mission">
        <div className="container">
          <div className="mission-content">
            <h2>Our Mission</h2>
            <p className="mission-text">
              AI data centers consume massive amounts of water and electricity, often in areas already facing resource constraints. 
              We provide transparency and empower communities to understand and respond to these impacts through data-driven insights.
            </p>
            <div className="mission-features">
              <div className="feature-item">
                <h3>Water Impact</h3>
                <p>Understanding how data centers affect local water resources and utility costs</p>
              </div>
              <div className="feature-item">
                <h3>Energy Impact</h3>
                <p>Analyzing electricity consumption and grid strain from AI infrastructure</p>
              </div>
              <div className="feature-item">
                <h3>Land Impact</h3>
                <p>Tracking changes to local landscapes and ecosystems</p>
              </div>
              <div className="feature-item">
                <h3>Take Action</h3>
                <p>Connecting with representatives to advocate for sustainable development</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* State Selector */}
      <section className="state-selector">
        <div className="container">
          <div className="selector-card card">
            <div className="card-header">
              <h2>Choose Your State</h2>
              <p className="card-subtitle">Get personalized impact reports for your area</p>
            </div>
            <form onSubmit={handleSubmit} className="state-form">
              <div className="form-group">
                <label className="form-label">Select Your State</label>
                <select 
                  className="form-select"
                  value={selectedState} 
                  onChange={(e) => setSelectedState(e.target.value)}
                  required
                >
                  <option value="">Choose a state...</option>
                  {states.map(state => (
                    <option key={state.value} value={state.value}>
                      {state.label}
                    </option>
                  ))}
                </select>
              </div>
              <button type="submit" className="btn btn-primary btn-lg">
                View Impact Report
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="quick-actions">
        <div className="container">
          <h2>Get Started</h2>
          <div className="actions-grid grid grid-2">
            <div className="action-card card">
              <h3>Personal Calculator</h3>
              <p>Upload your utility bills and see how AI data centers could impact your specific costs</p>
              <button 
                className="btn btn-secondary"
                onClick={() => navigate('/calculator')}
              >
                Try Calculator
              </button>
            </div>
            <div className="action-card card">
              <h3>Stay Informed</h3>
              <p>Get the latest news and legislation updates about AI data center impacts in your area</p>
              <button 
                className="btn btn-secondary"
                onClick={() => navigate('/report/california')}
              >
                View News
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="cta">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to Make a Difference?</h2>
            <p>Join thousands of concerned citizens working to ensure AI development happens sustainably</p>
            <div className="cta-buttons">
              <button 
                className="btn btn-primary btn-lg"
                onClick={() => navigate('/calculator')}
              >
                Calculate Your Impact
              </button>
              <button 
                className="btn btn-secondary btn-lg"
                onClick={() => navigate('/report/california')}
              >
                Explore State Reports
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
