// src/services/representativesService.js

// ProPublica Congress API - Free tier allows 5000 requests per day
const PROPUBLICA_API_KEY = 'YOUR_API_KEY_HERE'; // You'll need to get this from ProPublica
const PROPUBLICA_BASE_URL = 'https://api.propublica.org/congress/v1';

// Fallback data for states when API is not available
const STATE_REPRESENTATIVES = {
  california: [
    {
      name: "Sen. Dianne Feinstein",
      position: "U.S. Senator",
      district: "California",
      phone: "(202) 224-3841",
      email: "senator@feinstein.senate.gov",
      address: "331 Hart Senate Office Building, Washington, DC 20510",
      party: "Democrat"
    },
    {
      name: "Sen. Alex Padilla",
      position: "U.S. Senator", 
      district: "California",
      phone: "(202) 224-3553",
      email: "contact@padilla.senate.gov",
      address: "112 Hart Senate Office Building, Washington, DC 20510",
      party: "Democrat"
    }
  ],
  texas: [
    {
      name: "Sen. Ted Cruz",
      position: "U.S. Senator",
      district: "Texas", 
      phone: "(202) 224-5922",
      email: "info@cruz.senate.gov",
      address: "127A Russell Senate Office Building, Washington, DC 20510",
      party: "Republican"
    },
    {
      name: "Sen. John Cornyn",
      position: "U.S. Senator",
      district: "Texas",
      phone: "(202) 224-2934", 
      email: "info@cornyn.senate.gov",
      address: "517 Hart Senate Office Building, Washington, DC 20510",
      party: "Republican"
    }
  ],
  florida: [
    {
      name: "Sen. Marco Rubio",
      position: "U.S. Senator",
      district: "Florida",
      phone: "(202) 224-3041",
      email: "info@rubio.senate.gov", 
      address: "284 Russell Senate Office Building, Washington, DC 20510",
      party: "Republican"
    },
    {
      name: "Sen. Rick Scott",
      position: "U.S. Senator",
      district: "Florida",
      phone: "(202) 224-5274",
      email: "info@scott.senate.gov",
      address: "716 Hart Senate Office Building, Washington, DC 20510", 
      party: "Republican"
    }
  ],
  newyork: [
    {
      name: "Sen. Chuck Schumer",
      position: "U.S. Senator",
      district: "New York",
      phone: "(202) 224-6542",
      email: "info@schumer.senate.gov",
      address: "322 Hart Senate Office Building, Washington, DC 20510",
      party: "Democrat"
    },
    {
      name: "Sen. Kirsten Gillibrand",
      position: "U.S. Senator",
      district: "New York",
      phone: "(202) 224-4451",
      email: "info@gillibrand.senate.gov",
      address: "478 Russell Senate Office Building, Washington, DC 20510",
      party: "Democrat"
    }
  ],
  washington: [
    {
      name: "Sen. Patty Murray",
      position: "U.S. Senator",
      district: "Washington",
      phone: "(202) 224-2621",
      email: "senator_murray@murray.senate.gov",
      address: "154 Russell Senate Office Building, Washington, DC 20510",
      party: "Democrat"
    },
    {
      name: "Sen. Maria Cantwell",
      position: "U.S. Senator",
      district: "Washington",
      phone: "(202) 224-3441",
      email: "senator_cantwell@cantwell.senate.gov",
      address: "511 Hart Senate Office Building, Washington, DC 20510",
      party: "Democrat"
    }
  ],
  default: [
    {
      name: "Sen. Jane Smith",
      position: "U.S. Senator",
      district: "Your State",
      phone: "(202) 224-0000",
      email: "senator@smith.senate.gov",
      address: "123 Senate Office Building, Washington, DC 20510",
      party: "Democrat"
    },
    {
      name: "Rep. John Doe",
      position: "U.S. Representative", 
      district: "Your District",
      phone: "(202) 225-0000",
      email: "rep@doe.house.gov",
      address: "456 House Office Building, Washington, DC 20515",
      party: "Republican"
    }
  ]
};

export const getStateRepresentatives = async (stateName) => {
  try {
    // Normalize state name
    const normalizedState = stateName.toLowerCase().replace(/\s+/g, '');
    
    // Check if we have data for this state
    if (STATE_REPRESENTATIVES[normalizedState]) {
      return {
        success: true,
        data: STATE_REPRESENTATIVES[normalizedState]
      };
    }
    
    // If no specific data, return default representatives
    return {
      success: true,
      data: STATE_REPRESENTATIVES.default.map(rep => ({
        ...rep,
        district: rep.district.replace('Your State', stateName),
        district: rep.district.replace('Your District', `${stateName} District`)
      }))
    };
    
  } catch (error) {
    console.error("Error fetching representatives:", error);
    return {
      success: false,
      error: error.message,
      data: STATE_REPRESENTATIVES.default
    };
  }
};

// Function to get ProPublica API data (requires API key)
export const getProPublicaRepresentatives = async (stateName) => {
  if (!PROPUBLICA_API_KEY || PROPUBLICA_API_KEY === 'YOUR_API_KEY_HERE') {
    console.warn('ProPublica API key not configured, using fallback data');
    return getStateRepresentatives(stateName);
  }

  try {
    const response = await fetch(`${PROPUBLICA_BASE_URL}/members/senate/${stateName}/current.json`, {
      headers: {
        'X-API-Key': PROPUBLICA_API_KEY
      }
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    const data = await response.json();
    
    // Transform ProPublica data to our format
    const representatives = data.results.map(member => ({
      name: member.name,
      position: member.title,
      district: member.state,
      phone: member.phone,
      email: member.email,
      address: member.office,
      party: member.party === 'R' ? 'Republican' : 'Democrat'
    }));

    return {
      success: true,
      data: representatives
    };
  } catch (error) {
    console.error("Error calling ProPublica API:", error);
    // Fallback to our static data
    return getStateRepresentatives(stateName);
  }
};
