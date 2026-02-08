import { createContext, useContext, useState, useEffect } from 'react'

const ChatContext = createContext()

export function ChatProvider({ children }) {
  const [messages, setMessages] = useState([])
  
  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('chat_messages')
    if (saved) {
      try {
        setMessages(JSON.parse(saved))
      } catch (e) {
        console.error('Failed to load chat:', e)
      }
    }
  }, [])
  
  // Save to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chat_messages', JSON.stringify(messages))
    }
  }, [messages])
  
  const addMessage = (message) => {
    setMessages(prev => [...prev, message])
  }
  
  const clearMessages = () => {
    setMessages([])
    localStorage.removeItem('chat_messages')
  }
  
  return (
    <ChatContext.Provider value={{ messages, addMessage, clearMessages, setMessages }}>
      {children}
    </ChatContext.Provider>
  )
}

export const useChat = () => useContext(ChatContext)