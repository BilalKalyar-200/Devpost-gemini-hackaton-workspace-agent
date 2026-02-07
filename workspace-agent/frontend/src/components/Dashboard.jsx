import { useState, useEffect } from 'react'
import { RefreshCw, Calendar, Mail, BookOpen, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import '../styles/Dashboard.css'

const API_BASE = 'http://localhost:8000/api'

function Dashboard() {
  const [report, setReport] = useState(null)
  const [snapshot, setSnapshot] = useState(null)
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [reportRes, snapshotRes] = await Promise.all([
        fetch(`${API_BASE}/eod-report`),
        fetch(`${API_BASE}/snapshot/today`)
      ])
      
      const reportData = await reportRes.json()
      const snapshotData = await snapshotRes.json()
      
      setReport(reportData)
      setSnapshot(snapshotData)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const triggerReport = async () => {
    setGenerating(true)
    try {
      await fetch(`${API_BASE}/eod-report/generate`, { method: 'POST' })
      setTimeout(fetchData, 2000) // Refresh after generation
    } catch (error) {
      console.error('Error generating report:', error)
    } finally {
      setGenerating(false)
    }
  }

  const getUrgencyColor = (urgency) => {
    const colors = {
      critical: 'urgency-critical',
      high: 'urgency-high',
      normal: 'urgency-normal',
      low: 'urgency-low'
    }
    return colors[urgency] || 'urgency-normal'
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1>📊 Workspace Dashboard</h1>
          <p className="subtitle">Your intelligent workspace assistant</p>
        </div>
        <button 
          onClick={triggerReport} 
          disabled={generating}
          className="btn-primary"
        >
          <RefreshCw size={18} className={generating ? 'spinning' : ''} />
          {generating ? 'Generating...' : 'Generate Report'}
        </button>
      </div>

      {/* Stats Cards */}
      {snapshot && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon" style={{background: 'var(--primary-50)', color: 'var(--primary-600)'}}>
              <Mail size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{snapshot.emails?.length || 0}</div>
              <div className="stat-label">Unread Emails</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{background: '#FEF3C7', color: '#F59E0B'}}>
              <BookOpen size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{snapshot.assignments?.length || 0}</div>
              <div className="stat-label">Assignments</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{background: '#DBEAFE', color: '#3B82F6'}}>
              <Calendar size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{snapshot.meetings?.length || 0}</div>
              <div className="stat-label">Meetings Today</div>
            </div>
          </div>

          <div className="stat-card highlight">
            <div className="stat-icon" style={{background: '#FEE2E2', color: '#EF4444'}}>
              <AlertCircle size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{snapshot.urgent_count || 0}</div>
              <div className="stat-label">Urgent Items</div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="content-grid">
        {/* EOD Report */}
        <div className="report-section">
          <div className="section-header">
            <h2>📝 End-of-Day Summary</h2>
            {report?.date && (
              <span className="date-badge">{new Date(report.date).toLocaleDateString()}</span>
            )}
          </div>

          {report?.content ? (
            <>
              {report.urgent_items && report.urgent_items.length > 0 && (
                <div className="urgent-items-card">
                  <h3><AlertCircle size={18} /> Urgent Actions Required</h3>
                  <ul className="urgent-list">
                    {report.urgent_items.map((item, idx) => (
                      <li key={idx} className="urgent-item">
                        <span className="item-type">{item.type}</span>
                        <div>
                          <div className="item-title">{item.title}</div>
                          <div className="item-action">{item.action}</div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="report-content">
                {report.content}
              </div>

              {report.stats && (
                <div className="report-stats">
                  <div className="stat-pill">
                    <Mail size={14} />
                    {report.stats.emails} emails
                  </div>
                  <div className="stat-pill">
                    <BookOpen size={14} />
                    {report.stats.assignments} assignments
                  </div>
                  <div className="stat-pill">
                    <Calendar size={14} />
                    {report.stats.meetings} meetings
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <Clock size={48} />
              <p>No report generated yet</p>
              <button onClick={triggerReport} className="btn-secondary">
                Generate Your First Report
              </button>
            </div>
          )}
        </div>

        {/* Activity Breakdown */}
        <div className="activity-section">
          <h2>📋 Today's Activity</h2>

          {/* Emails */}
          {snapshot?.emails && snapshot.emails.length > 0 && (
            <div className="activity-card">
              <h3><Mail size={18} /> Emails ({snapshot.emails.length})</h3>
              <div className="activity-list">
                {snapshot.emails.slice(0, 5).map((email, idx) => (
                  <div key={idx} className="activity-item">
                    <div className={`urgency-dot ${getUrgencyColor(email.urgency)}`}></div>
                    <div className="activity-details">
                      <div className="activity-title">{email.subject}</div>
                      <div className="activity-meta">{email.sender}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Assignments */}
          {snapshot?.assignments && snapshot.assignments.length > 0 && (
            <div className="activity-card">
              <h3><BookOpen size={18} /> Assignments ({snapshot.assignments.length})</h3>
              <div className="activity-list">
                {snapshot.assignments.map((assignment, idx) => (
                  <div key={idx} className="activity-item">
                    <div className={`urgency-dot ${getUrgencyColor(assignment.urgency)}`}></div>
                    <div className="activity-details">
                      <div className="activity-title">{assignment.title}</div>
                      <div className="activity-meta">
                        {assignment.course} • Due in {assignment.days_until_due} days • {assignment.points} pts
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Meetings */}
          {snapshot?.meetings && snapshot.meetings.length > 0 && (
            <div className="activity-card">
              <h3><Calendar size={18} /> Meetings ({snapshot.meetings.length})</h3>
              <div className="activity-list">
                {snapshot.meetings.map((meeting, idx) => (
                  <div key={idx} className="activity-item">
                    <div className="urgency-dot urgency-normal"></div>
                    <div className="activity-details">
                      <div className="activity-title">{meeting.title}</div>
                      <div className="activity-meta">
                        {new Date(meeting.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} • {meeting.duration_minutes} min
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {(!snapshot?.emails?.length && !snapshot?.assignments?.length && !snapshot?.meetings?.length) && (
            <div className="empty-state-small">
              <CheckCircle size={32} />
              <p>No activity today</p>
              <p className="text-sm text-gray-600">Generate a report to start tracking</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard