// src/pages/StateReport.js
import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getStateInfo } from '../services/geminiService';

function StateReport() {
  const { state } = useParams();
  const navigate = useNavigate();
  const [newsData, setNewsData] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedGraph, setSelectedGraph] = useState(null);
  const [question, setQuestion] = useState('');
  const [news, setNews] = useState([]);
  const [representatives, setRepresentatives] = useState([]);

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
        landImpact: 12.3,
        carbonFootprint: 8.7,
        dataCenters: 23,
        projectedGrowth: 45.2,
        waterUsage: 2.3,
        energyUsage: 18.7
      });
      
      // Simulated news data
      setNews([
        {
          id: 1,
          title: "New AI Data Center Approved Despite Water Concerns",
          source: "Local News",
          date: "2024-01-15",
          summary: "City council approves new 500MW data center despite community concerns about water usage.",
          url: "#"
        },
        {
          id: 2,
          title: "State Legislature Considers Data Center Water Regulations",
          source: "State Politics",
          date: "2024-01-12",
          summary: "New bill would require data centers to report water usage and implement conservation measures.",
          url: "#"
        },
        {
          id: 3,
          title: "Environmental Groups Sue Over Data Center Impact",
          source: "Environmental News",
          date: "2024-01-10",
          summary: "Lawsuit filed against major tech company for environmental impact of new data center.",
          url: "#"
        }
      ]);

      // Simulated representatives data
      setRepresentatives([
        {
          name: "Sen. Jane Smith",
          position: "State Senator",
          district: "District 15",
          phone: "(555) 123-4567",
          email: "jane.smith@state.gov",
          address: "123 Capitol St, Capital City, ST 12345",
          party: "Democrat"
        },
        {
          name: "Rep. John Doe",
          position: "State Representative",
          district: "District 42",
          phone: "(555) 987-6543",
          email: "john.doe@state.gov",
          address: "456 State Ave, Capital City, ST 12345",
          party: "Republican"
        }
      ]);
      
      setLoading(false);
    }, 1000);
    fetchNews();
  }, [state]);

  const handleGraphClick = (graphType) => {
    setSelectedGraph(graphType);
    setQuestion('');
  };

  const handleQuestionSubmit = (e) => {
    e.preventDefault();
    // Here you would integrate with your AI model to answer questions
    console.log(`Question about ${selectedGraph}: ${question}`);
    setQuestion('');
    setSelectedGraph(null);
  };

  const copyPhoneNumber = (phone) => {
    navigator.clipboard.writeText(phone);
    alert('Phone number copied to clipboard!');
  };

  const openEmail = (email, name) => {
    const subject = `Concern about AI Data Center Impact in ${state}`;
    const body = `Dear ${name},\n\nI am writing to express my concerns about the environmental impact of AI data centers in our state. Based on recent reports, these facilities are significantly increasing our water and electricity costs while consuming massive amounts of resources.\n\nI would like to discuss potential regulations and oversight measures to ensure sustainable development of AI infrastructure.\n\nThank you for your time and consideration.\n\nSincerely,\n[Your Name]`;
    
    const mailtoLink = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.open(mailtoLink);
  };

  if (loading) {
    return <div className="loading">Loading report for {state}...</div>;
  }

  return (
    <div className="state-report">
      <div className="container">
        {/* Header */}
        <div className="report-header">
          <button className="btn btn-secondary" onClick={() => navigate('/')}>
            ← Back to Home
          </button>
          <h1 className="report-title">
            {state.charAt(0).toUpperCase() + state.slice(1)} Impact Report
          </h1>
          <p className="report-subtitle">
            Comprehensive analysis of AI data center impacts on your state
          </p>
        </div>

        <div className="report-layout">
          {/* Main Content */}
          <div className="main-content">
            {/* Key Metrics */}
            <section className="metrics-section">
              <h2>Key Impact Metrics</h2>
              <div className="metrics-grid grid grid-2">
                <div className="metric-card card">
                  <h3>Power Bill Impact</h3>
                  <div className="metric-value">{reportData.powerIncrease}%</div>
                  <p className="metric-description">Average increase in electricity costs</p>
                </div>
                <div className="metric-card card">
                  <h3>Water Bill Impact</h3>
                  <div className="metric-value">{reportData.waterIncrease}%</div>
                  <p className="metric-description">Average increase in water costs</p>
                </div>
                <div className="metric-card card">
                  <h3>Land Impact</h3>
                  <div className="metric-value">{reportData.landImpact}%</div>
                  <p className="metric-description">Land use change from data centers</p>
                </div>
                <div className="metric-card card">
                  <h3>Data Centers</h3>
                  <div className="metric-value">{reportData.dataCenters}</div>
                  <p className="metric-description">Active data centers in state</p>
                </div>
              </div>
            </section>

            {/* Interactive Graphs */}
            <section className="graphs-section">
              <h2>Interactive Data Visualizations</h2>
              <div className="graphs-grid grid grid-2">
                <div 
                  className="graph-card card clickable"
                  onClick={() => handleGraphClick('water-usage')}
                >
                  <h3>Water Usage Trends</h3>
                  <div className="graph-placeholder">
                    <p>Click to explore water usage data</p>
                  </div>
                </div>
                <div 
                  className="graph-card card clickable"
                  onClick={() => handleGraphClick('energy-consumption')}
                >
                  <h3>Energy Consumption</h3>
                  <div className="graph-placeholder">
                    <p>Click to explore energy data</p>
                  </div>
                </div>
                <div 
                  className="graph-card card clickable"
                  onClick={() => handleGraphClick('cost-impact')}
                >
                  <h3>Cost Impact Analysis</h3>
                  <div className="graph-placeholder">
                    <p>Click to explore cost data</p>
                  </div>
                </div>
                <div 
                  className="graph-card card clickable"
                  onClick={() => handleGraphClick('growth-projection')}
                >
                  <h3>Growth Projections</h3>
                  <div className="graph-placeholder">
                    <p>Click to explore growth data</p>
                  </div>
                </div>
              </div>
            </section>

            {/* Action Buttons */}
            <section className="action-section">
              <div className="action-buttons">
                <button 
                  className="btn btn-primary btn-lg"
                  onClick={() => navigate('/calculator')}
                >
                  Calculate Your Personal Impact
                </button>
                <button 
                  className="btn btn-secondary btn-lg"
                  onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                >
                  Contact Representatives
                </button>
              </div>
            </section>
          </div>

          {/* Sidebar */}
          <div className="sidebar">
            {/* News Section */}
            <div className="news-section card">
              <h3 className="sidebar-title">Latest News</h3>
              <div className="news-list">
                {news.map(article => (
                  <div key={article.id} className="news-item">
                    <h4 className="news-title">{article.title}</h4>
                    <div className="news-meta">
                      <span className="news-source">{article.source}</span>
                      <span className="news-date">{article.date}</span>
                    </div>
                    <p className="news-summary">{article.summary}</p>
                    <a href={article.url} className="news-link">Read More</a>
                  </div>
                ))}
              </div>
            </div>

            {/* Representatives Section */}
            <div className="representatives-section card">
              <h3 className="sidebar-title">Your Representatives</h3>
              <div className="representatives-list">
                {representatives.map((rep, index) => (
                  <div key={index} className="rep-card">
                    <div className="rep-header">
                      <h4 className="rep-name">{rep.name}</h4>
                      <span className={`rep-party ${rep.party.toLowerCase()}`}>
                        {rep.party}
                      </span>
                    </div>
                    <p className="rep-position">{rep.position} - {rep.district}</p>
                    <div className="rep-actions">
                      <button 
                        className="btn btn-sm btn-primary"
                        onClick={() => copyPhoneNumber(rep.phone)}
                      >
                        {rep.phone}
                      </button>
                      <button 
                        className="btn btn-sm btn-secondary"
                        onClick={() => openEmail(rep.email, rep.name)}
                      >
                        Email
                      </button>
                    </div>
                    <div className="rep-address">
                      <small>{rep.address}</small>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Graph Question Modal */}
      {selectedGraph && (
        <div className="modal-overlay" onClick={() => setSelectedGraph(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Ask a Question about {selectedGraph.replace('-', ' ')}</h3>
              <button 
                className="modal-close"
                onClick={() => setSelectedGraph(null)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleQuestionSubmit} className="question-form">
              <div className="form-group">
                <label className="form-label">Your Question:</label>
                <textarea
                  className="form-input"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask anything about this data..."
                  rows="4"
                  required
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setSelectedGraph(null)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Ask Question
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default StateReport;
