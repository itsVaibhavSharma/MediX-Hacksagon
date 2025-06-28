// frontend/src/components/Disease/SymptomChat.jsx
import React, { useState, useRef, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { api } from '../../services/api'
import { 
  Send, 
  Bot, 
  User, 
  AlertTriangle, 
  Calendar,
  MessageCircle,
  Loader2,
  RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'

const SymptomChat = () => {
  const { user } = useAuth()
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [emergencyAssessment, setEmergencyAssessment] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    // Start with a welcome message
    setMessages([
      {
        type: 'assistant',
        content: `Hello ${user?.full_name}! I'm your AI medical assistant. I'm here to help you understand your symptoms and provide medical guidance. Please describe what you're experiencing, and I'll do my best to assist you.

Remember: I provide information and guidance, but I'm not a replacement for professional medical care. If you have severe symptoms or concerns, please consult with a healthcare professional.`,
        timestamp: new Date()
      }
    ])
  }, [user])

  const sendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setLoading(true)

    try {
      let response
      if (sessionId) {
        // Continue existing chat
        response = await api.post('/chat/continue', {
          message: inputMessage,
          session_id: sessionId
        })
      } else {
        // Start new chat
        response = await api.post('/chat/start', {
          message: inputMessage
        })
        setSessionId(response.data.session_id)
      }

      const assistantMessage = {
        type: 'assistant',
        content: response.data.response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])

      // Check for emergency symptoms
      if (containsEmergencyKeywords(inputMessage)) {
        await checkEmergencyStatus(inputMessage)
      }

    } catch (error) {
      console.error('Chat error:', error)
      toast.error('Failed to send message. Please try again.')
      
      const errorMessage = {
        type: 'assistant',
        content: 'I apologize, but I\'m having trouble responding right now. Please try again in a moment, or if you have urgent medical concerns, please contact a healthcare professional immediately.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
      setInputMessage('')
    }
  }

  const containsEmergencyKeywords = (message) => {
    const emergencyKeywords = [
      'chest pain', 'difficulty breathing', 'severe pain', 'bleeding heavily',
      'unconscious', 'stroke', 'heart attack', 'suicide', 'overdose', 
      'severe headache', 'high fever', 'can\'t breathe'
    ]
    return emergencyKeywords.some(keyword => 
      message.toLowerCase().includes(keyword)
    )
  }

  const checkEmergencyStatus = async (symptoms) => {
    try {
      const response = await api.post('/disease/emergency-assessment', {
        symptoms: symptoms
      })
      setEmergencyAssessment(response.data)
    } catch (error) {
      console.error('Emergency assessment error:', error)
    }
  }

  const startNewChat = () => {
    setMessages([
      {
        type: 'assistant',
        content: `Hello again! I'm ready to help with any new symptoms or concerns you might have. What can I assist you with today?`,
        timestamp: new Date()
      }
    ])
    setSessionId(null)
    setEmergencyAssessment(null)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Symptom Chat</h1>
            <p className="mt-2 text-gray-600">
              Discuss your symptoms with our AI medical assistant
            </p>
          </div>
          <button
            onClick={startNewChat}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <RefreshCw className="h-4 w-4" />
            <span>New Chat</span>
          </button>
        </div>
      </div>

      {/* Emergency Alert */}
      {emergencyAssessment && emergencyAssessment.urgency_level === 'emergency' && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Emergency Alert</h3>
              <p className="mt-1 text-sm text-red-700">
                {emergencyAssessment.immediate_actions}
              </p>
              <div className="mt-3">
                <a
                  href="tel:911"
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded text-white bg-red-600 hover:bg-red-700"
                >
                  Call Emergency Services
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col h-[600px]">
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-3 max-w-3xl ${
                message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}>
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.type === 'user' 
                    ? 'bg-blue-600' 
                    : 'bg-green-600'
                }`}>
                  {message.type === 'user' ? (
                    <User className="h-4 w-4 text-white" />
                  ) : (
                    <Bot className="h-4 w-4 text-white" />
                  )}
                </div>
                <div className={`px-4 py-3 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                  <div className={`text-xs mt-1 ${
                    message.type === 'user' ? 'text-blue-200' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="flex items-start space-x-3 max-w-3xl">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-600 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div className="px-4 py-3 rounded-lg bg-gray-100">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm text-gray-600">AI is typing...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex space-x-4">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe your symptoms..."
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows="2"
                disabled={loading}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={loading || !inputMessage.trim()}
              className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
          <div className="mt-2 flex justify-between items-center text-xs text-gray-500">
            <span>Press Enter to send, Shift+Enter for new line</span>
            <div className="flex space-x-4">
              <button
                onClick={() => window.open('/detect', '_blank')}
                className="flex items-center space-x-1 text-blue-600 hover:text-blue-700"
              >
                <MessageCircle className="h-3 w-3" />
                <span>Try Image Detection</span>
              </button>
              <button
                onClick={() => window.open('/book-appointment', '_blank')}
                className="flex items-center space-x-1 text-purple-600 hover:text-purple-700"
              >
                <Calendar className="h-3 w-3" />
                <span>Book Appointment</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SymptomChat;