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
  });

  const handleCalculate = (e) => {
    e.preventDefault();
    // Run your personalized calculation here
    console.log('Calculating with inputs:', inputs);
  };

  return (
    <div className="calculator-page">
      <button onClick={() => navigate('/')}>← Back to Home</button>
      
      <h1>Personal Bill Calculator</h1>
      <p>Get a personalized estimate based on your household</p>

      <form onSubmit={handleCalculate}>
        <div className="input-group">
          <label>State:</label>
          <select 
            value={inputs.state}
            onChange={(e) => setInputs({...inputs, state: e.target.value})}
            required
          >
            <option value="">Choose a state...</option>
            <option value="california">California</option>
            <option value="texas">Texas</option>
            {/* Add more states */}
          </select>
        </div>

        <div className="input-group">
          <label>Current Monthly Power Bill ($):</label>
          <input 
            type="number" 
            value={inputs.currentPowerBill}
            onChange={(e) => setInputs({...inputs, currentPowerBill: e.target.value})}
            required
          />
        </div>

        <div className="input-group">
          <label>Current Monthly Water Bill ($):</label>
          <input 
            type="number" 
            value={inputs.currentWaterBill}
            onChange={(e) => setInputs({...inputs, currentWaterBill: e.target.value})}
            required
          />
        </div>

        <div className="input-group">
          <label>Household Size:</label>
          <input 
            type="number" 
            value={inputs.householdSize}
            onChange={(e) => setInputs({...inputs, householdSize: e.target.value})}
            required
          />
        </div>

        <button type="submit">Calculate My Impact</button>
      </form>

      <div className="results">
        {/* Display personalized results here */}
      </div>
    </div>
  );
}

export default Calculator;
