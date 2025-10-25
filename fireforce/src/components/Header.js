// src/components/Header.js
import { Link } from 'react-router-dom';

function Header() {
  return (
    <header className="header">
      <nav>
        <Link to="/" className="logo">AI Impact Calculator</Link>
        <div className="nav-links">
          <Link to="/">Home</Link>
          <Link to="/calculator">Calculator</Link>
        </div>
      </nav>
    </header>
  );
}

export default Header;
