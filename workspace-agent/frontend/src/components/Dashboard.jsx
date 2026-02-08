import { useState, useEffect } from 'react'
import { RefreshCw, Calendar, Mail, BookOpen, AlertCircle, CheckCircle, Clock, X, ChevronRight } from 'lucide-react'
import '../styles/Dashboard.css'

const API_BASE = 'http://localhost:8000/api'

function Dashboard() {
  const [report, setReport] = useState(null)
  const [snapshot, setSnapshot] = useState(null)
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [selectedModal, setSelectedModal] = useState(null) // 'emails' | 'assignments' | 'meetings' | null

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
      setTimeout(fetchData, 2000)
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

  const openModal = (type) => {
    setSelectedModal(type)
  }

  const closeModal = () => {
    setSelectedModal(null)
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

      {/* Stats Cards - NOW CLICKABLE */}
      {snapshot && (
        <div className="stats-grid">
          <button 
            className="stat-card clickable"
            onClick={() => openModal('emails')}
            disabled={!snapshot.emails || snapshot.emails.length === 0}
          >
            <div className="stat-icon" style={{background: 'var(--primary-50)', color: 'var(--primary-600)'}}>
              <Mail size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{snapshot.emails?.length || 0}</div>
              <div className="stat-label">Unread Emails</div>
            </div>
            {snapshot.emails?.length > 0 && (
              <ChevronRight size={20} className="stat-arrow" />
            )}
          </button>

          <button 
            className="stat-card clickable"
            onClick={() => openModal('assignments')}
            disabled={!snapshot.assignments || snapshot.assignments.length === 0}
          >
            <div className="stat-icon" style={{background: '#FEF3C7', color: '#F59E0B'}}>
              <BookOpen size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{snapshot.assignments?.length || 0}</div>
              <div className="stat-label">Assignments</div>
            </div>
            {snapshot.assignments?.length > 0 && (
              <ChevronRight size={20} className="stat-arrow" />
            )}
          </button>

          <button 
            className="stat-card clickable"
            onClick={() => openModal('meetings')}
            disabled={!snapshot.meetings || snapshot.meetings.length === 0}
          >
            <div className="stat-icon" style={{background: '#DBEAFE', color: '#3B82F6'}}>
              <Calendar size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{snapshot.meetings?.length || 0}</div>
              <div className="stat-label">Meetings Today</div>
            </div>
            {snapshot.meetings?.length > 0 && (
              <ChevronRight size={20} className="stat-arrow" />
            )}
          </button>

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
                {formatReportContent(report.content)}
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

      {/* MODAL FOR DETAILED VIEW */}
      {selectedModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                {selectedModal === 'emails' && <><Mail size={24} /> All Emails</>}
                {selectedModal === 'assignments' && <><BookOpen size={24} /> All Assignments</>}
                {selectedModal === 'meetings' && <><Calendar size={24} /> All Meetings</>}
              </h2>
              <button className="modal-close" onClick={closeModal}>
                <X size={24} />
              </button>
            </div>
            <div className="modal-body">
              {selectedModal === 'emails' && snapshot?.emails && (
                <div className="detail-list">
                  {snapshot.emails.map((email, idx) => (
                    <div key={idx} className="detail-item">
                      <div className="detail-item-header">
                        <h4>{email.subject}</h4>
                        <span className={`urgency-badge ${getUrgencyColor(email.urgency)}`}>
                          {email.urgency}
                        </span>
                      </div>
                      <p className="detail-meta">From: {email.sender}</p>
                      <p className="detail-snippet">{email.snippet}</p>
                      <p className="detail-time">{new Date(email.received).toLocaleString()}</p>
                    </div>
                  ))}
                </div>
              )}
              
              {selectedModal === 'assignments' && snapshot?.assignments && (
                <div className="detail-list">
                  {snapshot.assignments.map((assignment, idx) => (
                    <div key={idx} className="detail-item">
                      <div className="detail-item-header">
                        <h4>{assignment.title}</h4>
                        <span className={`urgency-badge ${getUrgencyColor(assignment.urgency)}`}>
                          Due in {assignment.days_until_due} days
                        </span>
                      </div>
                      <p className="detail-meta">Course: {assignment.course}</p>
                      <p className="detail-meta">Points: {assignment.points}</p>
                      <p className="detail-time">Due: {new Date(assignment.due_date).toLocaleString()}</p>
                    </div>
                  ))}
                </div>
              )}
              
              {selectedModal === 'meetings' && snapshot?.meetings && (
                <div className="detail-list">
                  {snapshot.meetings.map((meeting, idx) => (
                    <div key={idx} className="detail-item">
                      <h4>{meeting.title}</h4>
                      <p className="detail-meta">
                        {new Date(meeting.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </p>
                      <p className="detail-meta">Duration: {meeting.duration_minutes} minutes</p>
                      <p className="detail-meta">Attendees: {meeting.attendees_count}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Helper function to format report content
function formatReportContent(content) {
  const lines = content.split('\n')
  return lines.map((line, i) => {
    // Headers
    if (line.startsWith('## ')) {
      return <h3 key={i} className="report-heading">{line.slice(3)}</h3>
    }
    
    // Bold
    let formatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    
    // Empty lines
    if (!formatted.trim()) {
      return <br key={i} />
    }
    
    return <p key={i} dangerouslySetInnerHTML={{ __html: formatted }} />
  })
}

export default Dashboard