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

  return (
    <div className="home-page">
      <section className="hero">
        <h1>AI Data Center Impact Calculator</h1>
        <p>Understand how AI data centers affect your power and water bills</p>
      </section>

      <section className="state-selector">
        <h2>Select Your State</h2>
        <form onSubmit={handleSubmit}>
          <select 
            value={selectedState} 
            onChange={(e) => setSelectedState(e.target.value)}
            required
          >
            <option value="">Choose a state...</option>
            <option value="california">California</option>
            <option value="texas">Texas</option>
            <option value="virginia">Virginia</option>
            {/* Add more states */}
          </select>
          <button type="submit">View Impact Report</button>
        </form>
      </section>

      <section className="quick-links">
        <button onClick={() => navigate('/calculator')}>
          Try the Bill Calculator
        </button>
      </section>
    </div>
  );
}

export default Home;
