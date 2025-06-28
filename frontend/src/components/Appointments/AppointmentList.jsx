
// frontend/src/components/Appointments/AppointmentList.jsx
import React, { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { api } from '../../services/api'
import { 
  Calendar, 
  Clock, 
  Video, 
  User, 
  Phone, 
  MapPin,
  CheckCircle,
  XCircle,
  AlertCircle,
  Plus
} from 'lucide-react'
import toast from 'react-hot-toast'
import { Link } from 'react-router-dom'

const AppointmentList = () => {
  const { user } = useAuth()
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, upcoming, completed, cancelled

  useEffect(() => {
    fetchAppointments()
  }, [])

  const fetchAppointments = async () => {
    try {
      const response = await api.get('/appointments/my-appointments')
      setAppointments(response.data.appointments || [])
    } catch (error) {
      console.error('Error fetching appointments:', error)
      toast.error('Failed to load appointments')
    } finally {
      setLoading(false)
    }
  }

  const updateAppointmentStatus = async (appointmentId, newStatus, notes = '') => {
    try {
      await api.put(`/appointments/appointments/${appointmentId}/status`, {
        status: newStatus,
        notes: notes
      })
      
      toast.success(`Appointment ${newStatus} successfully`)
      fetchAppointments() // Refresh the list
    } catch (error) {
      console.error('Error updating appointment:', error)
      toast.error('Failed to update appointment status')
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'scheduled':
        return <Clock className="h-4 w-4" />
      case 'completed':
        return <CheckCircle className="h-4 w-4" />
      case 'cancelled':
        return <XCircle className="h-4 w-4" />
      default:
        return <AlertCircle className="h-4 w-4" />
    }
  }

  const filteredAppointments = appointments.filter(appointment => {
    if (filter === 'all') return true
    if (filter === 'upcoming') {
      return appointment.status === 'scheduled' && new Date(appointment.appointment_date) > new Date()
    }
    return appointment.status === filter
  })

  const sortedAppointments = filteredAppointments.sort((a, b) => 
    new Date(b.appointment_date) - new Date(a.appointment_date)
  )

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {user?.user_type === 'patient' ? 'My Appointments' : 'Patient Appointments'}
          </h1>
          <p className="mt-2 text-gray-600">
            {user?.user_type === 'patient' 
              ? 'Manage your scheduled consultations'
              : 'View and manage patient appointments'
            }
          </p>
        </div>
        
        {user?.user_type === 'patient' && (
          <Link
            to="/book-appointment"
            className="mt-4 sm:mt-0 inline-flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700"
          >
            <Plus className="h-5 w-5" />
            <span>Book Appointment</span>
          </Link>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'all', label: 'All' },
              { key: 'upcoming', label: 'Upcoming' },
              { key: 'completed', label: 'Completed' },
              { key: 'cancelled', label: 'Cancelled' }
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setFilter(key)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  filter === key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Appointments List */}
      {sortedAppointments.length > 0 ? (
        <div className="space-y-4">
          {sortedAppointments.map((appointment) => (
            <div key={appointment.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="bg-blue-100 p-2 rounded-full">
                        <User className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">
                          {user?.user_type === 'patient' 
                            ? `Dr. ${appointment.doctor_name || 'Unknown'}`
                            : appointment.patient_name || 'Unknown Patient'
                          }
                        </h3>
                        {user?.user_type === 'patient' && appointment.doctor_specialty && (
                          <p className="text-sm text-gray-600">{appointment.doctor_specialty}</p>
                        )}
                        {user?.user_type === 'doctor' && appointment.patient_age && (
                          <p className="text-sm text-gray-600">Age: {appointment.patient_age}</p>
                        )}
                      </div>
                    </div>
                    
                    <div className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(appointment.status)}`}>
                      {getStatusIcon(appointment.status)}
                      <span className="capitalize">{appointment.status}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Calendar className="h-4 w-4" />
                      <span>{new Date(appointment.appointment_date).toLocaleDateString()}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Clock className="h-4 w-4" />
                      <span>{new Date(appointment.appointment_date).toLocaleTimeString()}</span>
                    </div>

                    {appointment.disease_type && (
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <AlertCircle className="h-4 w-4" />
                        <span>Concern: {appointment.disease_type}</span>
                      </div>
                    )}
                  </div>

                  {appointment.symptoms && (
                    <div className="mb-4">
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Symptoms: </span>
                        {appointment.symptoms}
                      </p>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-2 lg:ml-6">
                  {appointment.meet_link && appointment.status === 'scheduled' && (
                    <a
                      href={appointment.meet_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700"
                    >
                      <Video className="h-4 w-4" />
                      <span>Join Call</span>
                    </a>
                  )}

                  {appointment.status === 'scheduled' && (
                    <div className="flex space-x-2">
                      {user?.user_type === 'doctor' && (
                        <button
                          onClick={() => updateAppointmentStatus(appointment.id, 'completed')}
                          className="inline-flex items-center justify-center space-x-1 bg-blue-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
                        >
                          <CheckCircle className="h-4 w-4" />
                          <span>Complete</span>
                        </button>
                      )}
                      
                      <button
                        onClick={() => updateAppointmentStatus(appointment.id, 'cancelled')}
                        className="inline-flex items-center justify-center space-x-1 border border-red-300 text-red-600 px-3 py-2 rounded-lg text-sm font-medium hover:bg-red-50"
                      >
                        <XCircle className="h-4 w-4" />
                        <span>Cancel</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Calendar className="mx-auto h-16 w-16 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">
            No appointments found
          </h3>
          <p className="mt-2 text-gray-500">
            {filter === 'all' 
              ? user?.user_type === 'patient' 
                ? "You haven't booked any appointments yet."
                : "No patients have booked appointments with you yet."
              : `No ${filter} appointments found.`
            }
          </p>
          {user?.user_type === 'patient' && filter === 'all' && (
            <div className="mt-6">
              <Link
                to="/book-appointment"
                className="inline-flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700"
              >
                <Plus className="h-5 w-5" />
                <span>Book Your First Appointment</span>
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AppointmentList;