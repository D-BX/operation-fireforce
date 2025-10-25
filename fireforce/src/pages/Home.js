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

  // const states = [
  //   { value: 'california', label: 'California' },
  //   { value: 'texas', label: 'Texas' },
  //   { value: 'virginia', label: 'Virginia' },
  //   { value: 'washington', label: 'Washington' },
  //   { value: 'oregon', label: 'Oregon' },
  //   { value: 'nevada', label: 'Nevada' },
  //   { value: 'arizona', label: 'Arizona' },
  //   { value: 'utah', label: 'Utah' },
  //   { value: 'colorado', label: 'Colorado' },
  //   { value: 'new-mexico', label: 'New Mexico' },
  // ];

  const states = [
      { value: 'virginia', label: 'Virginia' }, // VA
      { value: 'michigan', label: 'Michigan' }, // MI
      { value: 'georgia', label: 'Georgia' }, // GA
      { value: 'texas', label: 'Texas' }, // TX
      { value: 'indiana', label: 'Indiana' }, // IN
      { value: 'minnesota', label: 'Minnesota' }, // MN
      { value: 'california', label: 'California' } // CA
  ];

  return (
    <div className="home-page">
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">
              The True Cost of AI Data Centers
            </h1>
            <p className="hero-subtitle">
              Are you informed of what the construction of local AI data centers might mean for you? 
              AI data centers consume vast amounts of resources, and this can affect the price of goods for local residents.
              Enter your state of residence below to learn what AI data centers mean for your bills and quality of life.
            </p>
            <div className="hero-stats">
              <div className="stat-item">
                <div className="stat-number">15.5%</div>
                <div className="stat-label">Average Power Bill Increase</div>
                <img src="/lights.gif" alt="Lights" width={200} height={150} />
              </div>
              <div className="stat-item">
                <div className="stat-number">8.2%</div>
                <div className="stat-label">Average Water Bill Increase</div>
                <img src="/tapwater.gif" alt="Tap Water" width={200} height={150} />
              </div>
              <div className="stat-item">
                <div className="stat-number">2.3M</div>
                <div className="stat-label">Gallons Water per Day</div>
                <img src="/waterfall.gif" alt="Waterfall" width={300} height={150} />
              </div>
            </div>
          </div>
        </div>
      </section>

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
    </div>
  );
}

export default Home;
