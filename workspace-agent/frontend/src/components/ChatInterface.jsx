import { useState, useEffect, useRef } from 'react'
import { Send, Loader2, Sparkles, Mail, Calendar, BookOpen } from 'lucide-react'
import '../styles/Chat.css'
import { useChat } from '../context/ChatContext'

const API_BASE = 'http://localhost:8000/api'

function ChatInterface() {
  const {messages, setMessages } = useChat()
  // const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    loadChatHistory()
    loadSuggestions()
  }, [])

  const loadChatHistory = async () => {
    try{
      const res = await fetch(`${API_BASE}/chat/history`)
      const data = await res.json()
      if (data.history && data.history.length > 0) {
        const sorted = data.history.sort((a, b) => 
          new Date(a.timestamp) - new Date(b.timestamp)
        )
        setMessages(sorted)
      } else {
        // Show welcome message
        setMessages([{
          role: 'agent',
          content: "👋 Hi! I'm your workspace assistant. I can help you with:\n\n📧 **Emails** - See unread, important, or search by sender\n📚 **Assignments** - Check what's due soon\n📅 **Schedule** - View today's meetings\n\nWhat would you like to know?",
          timestamp: new Date().toISOString()
        }])
      }
    } catch (err) {
      console.error('Error loading history:', err)
    }
  }

  const loadSuggestions = async () => {
    try {
      const res = await fetch(`${API_BASE}/snapshot/today`)
      const data = await res.json()
      
      const newSuggestions = []
      if (data.emails && data.emails.length > 0) {
        newSuggestions.push({ icon: Mail, text: "Show me my unread emails" })
        newSuggestions.push({ icon: Mail, text: "Any important emails?" })
      }
      if (data.assignments && data.assignments.length > 0) {
        newSuggestions.push({ icon: BookOpen, text: "What's due this week?" })
      }
      if (data.meetings && data.meetings.length > 0) {
        newSuggestions.push({ icon: Calendar, text: "What's my schedule today?" })
      }
      
      if (newSuggestions.length === 0) {
        newSuggestions.push({ icon: Sparkles, text: "What can you help me with?" })
      }
      
      setSuggestions(newSuggestions.slice(0, 3))
    } catch (err) {
      console.error('Error loading suggestions:', err)
    }
  }

  const sendMessage = async (text = null) => {
    const messageText = text || input
    if (!messageText.trim()) return

    const userMessage = { 
      role: 'user', 
      content: messageText,
      timestamp: new Date().toISOString()
    }
    
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: messageText })
      })
      const data = await res.json()
      
      const agentMessage = { 
        role: 'agent', 
        content: data.response || "Sorry, I couldn't process that request.",
        timestamp: new Date().toISOString()
      }
      
      setMessages(prev => [...prev, agentMessage])
      
      // Update suggestions if provided
      if (data.suggestions && data.suggestions.length > 0) {
        setSuggestions(data.suggestions.map(s => ({ icon: Sparkles, text: s })))
      }
    } catch (err) {
      console.error('Error sending message:', err)
      const errorMessage = {
        role: 'agent',
        content: '❌ Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const formatMessage = (content) => {
    // Split by newlines and format
    return content.split('\n').map((line, i) => {
      // Bold text between **
      const formatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      return <div key={i} dangerouslySetInnerHTML={{ __html: formatted }} />
    })
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-header-content">
          <Sparkles size={24} className="chat-icon" />
          <div>
            <h2>💬 Chat with Your Agent</h2>
            <p className="chat-subtitle">Ask me anything about your workspace</p>
          </div>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="empty-chat">
            <Sparkles size={48} className="empty-icon" />
            <h3>Start a conversation</h3>
            <p>Ask me about your emails, assignments, or schedule</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message-wrapper ${msg.role}`}>
            <div className="message-bubble">
              {msg.role === 'agent' && (
                <div className="message-avatar agent-avatar">
                  <Sparkles size={16} />
                </div>
              )}
              <div className="message-content">
                {formatMessage(msg.content)}
              </div>
              {msg.role === 'user' && (
                <div className="message-avatar user-avatar">
                  You
                </div>
              )}
            </div>
            <div className="message-time">
              {new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-wrapper agent">
            <div className="message-bubble">
              <div className="message-avatar agent-avatar">
                <Sparkles size={16} />
              </div>
              <div className="message-content typing-indicator">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && messages.length <= 1 && (
        <div className="suggestions-bar">
          <p className="suggestions-label">Try asking:</p>
          <div className="suggestions-grid">
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => sendMessage(suggestion.text)}
                className="suggestion-chip"
                disabled={loading}
              >
                <suggestion.icon size={14} />
                {suggestion.text}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="chat-input-wrapper">
        <div className="chat-input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && sendMessage()}
            placeholder="Ask me anything about your workspace..."
            disabled={loading}
            className="chat-input"
          />
          <button 
            onClick={() => sendMessage()} 
            disabled={loading || !input.trim()}
            className="send-button"
          >
            {loading ? (
              <Loader2 size={20} className="spinning" />
            ) : (
              <Send size={20} />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface