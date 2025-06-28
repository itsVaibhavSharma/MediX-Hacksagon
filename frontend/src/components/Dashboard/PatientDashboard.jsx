
// frontend/src/components/Dashboard/PatientDashboard.jsx
import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { api } from '../../services/api'
import { 
  Camera, 
  MessageCircle, 
  Calendar, 
  Clock, 
  TrendingUp, 
  AlertCircle,
  Activity,
  Brain
} from 'lucide-react'

const PatientDashboard = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    totalDetections: 0,
    chatSessions: 0,
    upcomingAppointments: 0
  })
  const [recentResults, setRecentResults] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [historyResponse, appointmentsResponse] = await Promise.all([
        api.get('/disease/history'),
        api.get('/appointments/my-appointments')
      ])

      const history = historyResponse.data.history || []
      const appointments = appointmentsResponse.data.appointments || []

      setStats({
        totalDetections: history.length,
        chatSessions: 0, // You can implement chat session counting
        upcomingAppointments: appointments.filter(apt => 
          apt.status === 'scheduled' && new Date(apt.appointment_date) > new Date()
        ).length
      })

      setRecentResults(history.slice(0, 5))
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const quickActions = [
    {
      title: 'AI Disease Detection',
      description: 'Upload medical images for AI analysis',
      icon: Camera,
      link: '/detect',
      color: 'bg-blue-500 hover:bg-blue-600',
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600'
    },
    {
      title: 'Symptom Chat',
      description: 'Discuss symptoms with AI assistant',
      icon: MessageCircle,
      link: '/chat',
      color: 'bg-green-500 hover:bg-green-600',
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600'
    },
    {
      title: 'Book Appointment',
      description: 'Schedule consultation with doctors',
      icon: Calendar,
      link: '/book-appointment',
      color: 'bg-purple-500 hover:bg-purple-600',
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600'
    }
  ]

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.full_name}
        </h1>
        <p className="mt-2 text-gray-600">
          Your AI-powered health assistant is ready to help you
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <Activity className="h-6 w-6 text-blue-600" />
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Detections</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalDetections}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="bg-green-100 p-3 rounded-lg">
                  <Brain className="h-6 w-6 text-green-600" />
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Chat Sessions</p>
                <p className="text-2xl font-bold text-gray-900">{stats.chatSessions}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="bg-purple-100 p-3 rounded-lg">
                  <Calendar className="h-6 w-6 text-purple-600" />
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Upcoming Appointments</p>
                <p className="text-2xl font-bold text-gray-900">{stats.upcomingAppointments}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action, index) => (
            <Link
              key={index}
              to={action.link}
              className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200 hover:scale-105"
            >
              <div className="flex items-start">
                <div className={`${action.iconBg} p-3 rounded-lg`}>
                  <action.icon className={`h-6 w-6 ${action.iconColor}`} />
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900">{action.title}</h3>
                  <p className="mt-1 text-sm text-gray-500">{action.description}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Results */}
      <div className="bg-white shadow-sm rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900">Recent AI Detections</h2>
            <Link to="/detect" className="text-sm text-blue-600 hover:text-blue-500">
              View all
            </Link>
          </div>
        </div>
        <div className="divide-y divide-gray-200">
          {recentResults.length > 0 ? (
            recentResults.map((result) => (
              <div key={result.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {result.disease_type.charAt(0).toUpperCase() + result.disease_type.slice(1)} Detection
                    </p>
                    <p className="text-sm text-gray-500">
                      Result: {result.final_diagnosis}
                    </p>
                    <p className="text-xs text-gray-400">
                      {new Date(result.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {Math.round(result.confidence * 100)}% confidence
                    </span>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="px-6 py-8 text-center">
              <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No detections yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Start by uploading an image for AI analysis
              </p>
              <div className="mt-6">
                <Link
                  to="/detect"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  Start Detection
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PatientDashboard;