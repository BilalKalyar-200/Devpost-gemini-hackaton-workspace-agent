import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import ChatInterface from './components/ChatInterface'
import './App.css'

function App() {
  const [health, setHealth] = useState(null)

  useEffect(() => {
    //check backend health on load->did this just to assure
    fetch('http://localhost:8000/api/health')
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(err => console.error('Backend not running:', err))
  }, [])

  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navbar">
          <h1>🤖 Workspace Agent</h1>
          <div className="nav-links">
            <Link to="/">Dashboard</Link>
            <Link to="/chat">Chat</Link>
          </div>
          {health && (
            <div className="health-status">
              Status: {health.status}
            </div>
          )}
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<ChatInterface />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App