// frontend/src/components/Appointments/BookAppointment.jsx
import React, { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { api } from '../../services/api'
import { 
  Search, 
  MapPin, 
  Calendar, 
  Clock, 
  User, 
  Stethoscope,
  Star,
  CheckCircle,
  ArrowLeft
} from 'lucide-react'
import toast from 'react-hot-toast'
import { Link } from 'react-router-dom'

const BookAppointment = () => {
  const { user } = useAuth()
  const [step, setStep] = useState(1) // 1: Search, 2: Select Time, 3: Confirmation
  const [searchData, setSearchData] = useState({
    city: user?.city || '',
    specialty: ''
  })
  const [doctors, setDoctors] = useState([])
  const [specialties, setSpecialties] = useState([])
  const [selectedDoctor, setSelectedDoctor] = useState(null)
  const [appointmentData, setAppointmentData] = useState({
    date: '',
    time: '',
    disease_type: '',
    symptoms: ''
  })
  const [loading, setLoading] = useState(false)
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    fetchSpecialties()
  }, [])

  const fetchSpecialties = async () => {
    try {
      const response = await api.get('/appointments/doctors/specialties')
      setSpecialties(response.data.specialties)
    } catch (error) {
      console.error('Error fetching specialties:', error)
    }
  }

  const searchDoctors = async () => {
    if (!searchData.city.trim()) {
      toast.error('Please enter a city')
      return
    }

    setSearching(true)
    try {
      const response = await api.get('/appointments/doctors/search', {
        params: {
          city: searchData.city,
          specialty: searchData.specialty || undefined
        }
      })
      setDoctors(response.data.doctors)
      
      if (response.data.doctors.length === 0) {
        toast.error('No doctors found in your area. Try a different city or specialty.')
      }
    } catch (error) {
      console.error('Error searching doctors:', error)
      toast.error('Failed to search doctors. Please try again.')
    } finally {
      setSearching(false)
    }
  }

  const selectDoctor = (doctor) => {
    setSelectedDoctor(doctor)
    setStep(2)
  }

  const bookAppointment = async () => {
    if (!appointmentData.date || !appointmentData.time) {
      toast.error('Please select date and time')
      return
    }

    setLoading(true)
    try {
      const appointmentDateTime = new Date(`${appointmentData.date}T${appointmentData.time}:00`)
      
      const response = await api.post('/appointments/book', {
        doctor_id: selectedDoctor.id,
        appointment_date: appointmentDateTime.toISOString(),
        disease_type: appointmentData.disease_type || null,
        symptoms: appointmentData.symptoms || null
      })

      toast.success('Appointment booked successfully!')
      setStep(3)
    } catch (error) {
      console.error('Error booking appointment:', error)
      toast.error(error.response?.data?.detail || 'Failed to book appointment')
    } finally {
      setLoading(false)
    }
  }

  // Generate time slots
  const generateTimeSlots = () => {
    const slots = []
    for (let hour = 9; hour <= 17; hour++) {
      for (let minute = 0; minute < 60; minute += 30) {
        const timeString = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`
        slots.push(timeString)
      }
    }
    return slots
  }

  const timeSlots = generateTimeSlots()

  // Get minimum date (tomorrow)
  const getMinDate = () => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    return tomorrow.toISOString().split('T')[0]
  }

  // Get maximum date (30 days from now)
  const getMaxDate = () => {
    const maxDate = new Date()
    maxDate.setDate(maxDate.getDate() + 30)
    return maxDate.toISOString().split('T')[0]
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <Link to="/dashboard" className="inline-flex items-center text-blue-600 hover:text-blue-500 mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Book Appointment</h1>
        <p className="mt-2 text-gray-600">
          Find and book appointments with qualified doctors in your area
        </p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-center space-x-8">
          <div className={`flex items-center space-x-2 ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
              step >= 1 ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
            }`}>
              1
            </div>
            <span className="font-medium">Find Doctor</span>
          </div>
          
          <div className={`w-16 h-1 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
          
          <div className={`flex items-center space-x-2 ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
              step >= 2 ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
            }`}>
              2
            </div>
            <span className="font-medium">Select Time</span>
          </div>
          
          <div className={`w-16 h-1 ${step >= 3 ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
          
          <div className={`flex items-center space-x-2 ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
              step >= 3 ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
            }`}>
              3
            </div>
            <span className="font-medium">Confirm</span>
          </div>
        </div>
      </div>

      {/* Step 1: Search Doctors */}
      {step === 1 && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Search for Doctors</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">City</label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    value={searchData.city}
                    onChange={(e) => setSearchData({...searchData, city: e.target.value})}
                    className="pl-10 w-full py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter city name"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Specialty (Optional)</label>
                <select
                  value={searchData.specialty}
                  onChange={(e) => setSearchData({...searchData, specialty: e.target.value})}
                  className="w-full py-3 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Specialties</option>
                  {specialties.map((specialty) => (
                    <option key={specialty} value={specialty}>{specialty}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex items-end">
                <button
                  onClick={searchDoctors}
                  disabled={searching}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  <Search className="h-5 w-5" />
                  <span>{searching ? 'Searching...' : 'Search'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Search Results */}
          {doctors.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Available Doctors</h3>
              {doctors.map((doctor) => (
                <div key={doctor.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <div className="bg-blue-100 p-3 rounded-full">
                          <Stethoscope className="h-6 w-6 text-blue-600" />
                        </div>
                        <div>
                          <h4 className="text-lg font-medium text-gray-900">Dr. {doctor.name}</h4>
                          <p className="text-sm text-gray-600">{doctor.specialty}</p>
                          <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                            <span className="flex items-center space-x-1">
                              <MapPin className="h-4 w-4" />
                              <span>{doctor.city}</span>
                            </span>
                            <span>{doctor.experience_years} years experience</span>
                          </div>
                        </div>
                      </div>
                      {doctor.phone && (
                        <p className="mt-2 text-sm text-gray-600">
                          Phone: {doctor.phone}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => selectDoctor(doctor)}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700"
                    >
                      Select Doctor
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Step 2: Select Time */}
      {step === 2 && selectedDoctor && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-medium text-gray-900">Schedule Appointment</h2>
                <p className="text-sm text-gray-600">With Dr. {selectedDoctor.name}</p>
              </div>
              <button
                onClick={() => setStep(1)}
                className="text-blue-600 hover:text-blue-500 text-sm"
              >
                Change Doctor
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Appointment Date
                </label>
                <input
                  type="date"
                  value={appointmentData.date}
                  onChange={(e) => setAppointmentData({...appointmentData, date: e.target.value})}
                  min={getMinDate()}
                  max={getMaxDate()}
                  className="w-full py-3 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Appointment Time
                </label>
                <select
                  value={appointmentData.time}
                  onChange={(e) => setAppointmentData({...appointmentData, time: e.target.value})}
                  className="w-full py-3 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select time</option>
                  {timeSlots.map((time) => (
                    <option key={time} value={time}>{time}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Primary Concern (Optional)
              </label>
              <input
                type="text"
                value={appointmentData.disease_type}
                onChange={(e) => setAppointmentData({...appointmentData, disease_type: e.target.value})}
                className="w-full py-3 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Skin condition, Chest pain, Regular checkup"
              />
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Symptoms Description (Optional)
              </label>
              <textarea
                value={appointmentData.symptoms}
                onChange={(e) => setAppointmentData({...appointmentData, symptoms: e.target.value})}
                className="w-full h-24 py-3 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                placeholder="Describe your symptoms or any additional information..."
              />
            </div>

            <div className="mt-6 flex space-x-4">
              <button
                onClick={() => setStep(1)}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50"
              >
                Back
              </button>
              <button
                onClick={bookAppointment}
                disabled={loading || !appointmentData.date || !appointmentData.time}
                className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Booking...</span>
                  </>
                ) : (
                  <>
                    <Calendar className="h-5 w-5" />
                    <span>Book Appointment</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Confirmation */}
      {step === 3 && (
        <div className="text-center">
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Appointment Booked!</h2>
            <p className="text-gray-600 mb-6">
              Your appointment has been successfully scheduled
            </p>

            <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left">
              <h3 className="font-medium text-gray-900 mb-4">Appointment Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Doctor:</span>
                  <span className="font-medium">Dr. {selectedDoctor?.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Specialty:</span>
                  <span>{selectedDoctor?.specialty}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Date:</span>
                  <span>{new Date(appointmentData.date).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Time:</span>
                  <span>{appointmentData.time}</span>
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/appointments"
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700"
              >
                View Appointments
              </Link>
              <Link
                to="/dashboard"
                className="border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-50"
              >
                Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default BookAppointment;