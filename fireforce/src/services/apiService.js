const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export const apiService = {
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async predictElectricity({ state, addedPowerMW, addedAnnualMWh, mode = 'assumption', includeInSales = true }) {
    try {
      const response = await fetch(`${API_BASE_URL}/electricity/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          state,
          added_power_mw: addedPowerMW,
          added_annual_mwh: addedAnnualMWh,
          mode,
          include_in_sales: includeInSales,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        return { success: false, error: data.error };
      }

      return { success: true, data: data.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async predictHousing({ state, currentPrice, yearsAfter = 1, futureYear, baseYear = 2025, method = 'simple' }) {
    try {
      const response = await fetch(`${API_BASE_URL}/housing/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          state,
          current_price: currentPrice,
          years_after: yearsAfter,
          future_year: futureYear,
          base_year: baseYear,
          method,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        return { success: false, error: data.error };
      }

      return { success: true, data: data.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async getHousingHistory(state) {
    try {
      const response = await fetch(`${API_BASE_URL}/housing/history?state=${encodeURIComponent(state)}`);
      const data = await response.json();

      if (!response.ok) {
        return { success: false, error: data.error };
      }

      return { success: true, data: data.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async getStates() {
    try {
      const response = await fetch(`${API_BASE_URL}/states`);
      const data = await response.json();

      if (!response.ok) {
        return { success: false, error: data.error };
      }

      return { success: true, data: data.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },
};

export default apiService;
