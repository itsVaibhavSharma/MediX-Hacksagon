// frontend/src/App.jsx
import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Header from './components/Layout/Header'
import Login from './components/Auth/Login'
import Signup from './components/Auth/Signup'
import PatientDashboard from './components/Dashboard/PatientDashboard'
import DoctorDashboard from './components/Dashboard/DoctorDashboard'
import ImageDetection from './components/Disease/ImageDetection'
import SymptomChat from './components/Disease/SymptomChat'
import BookAppointment from './components/Appointments/BookAppointment'
import AppointmentList from './components/Appointments/AppointmentList'
import HomePage from './components/HomePage'
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  return user ? children : <Navigate to="/login" />
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  return user ? <Navigate to="/dashboard" /> : children
}

function AppContent() {
  const { user } = useAuth()
  
  return (
    <div className="min-h-screen bg-slate-50">
      {user && <Header />}
      <Routes>
        <Route path="/" element={
          <PublicRoute>
            <HomePage />
          </PublicRoute>
        } />
        {/* Public Routes */}
        <Route path="/login" element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        } />
        <Route path="/signup" element={
          <PublicRoute>
            <Signup />
          </PublicRoute>
        } />
        
        {/* Protected Routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            {user?.user_type === 'patient' ? <PatientDashboard /> : <DoctorDashboard />}
          </ProtectedRoute>
        } />
        
        <Route path="/detect" element={
          <ProtectedRoute>
            <ImageDetection />
          </ProtectedRoute>
        } />
        
        <Route path="/chat" element={
          <ProtectedRoute>
            <SymptomChat />
          </ProtectedRoute>
        } />
        
        <Route path="/appointments" element={
          <ProtectedRoute>
            <AppointmentList />
          </ProtectedRoute>
        } />
        
        <Route path="/book-appointment" element={
          <ProtectedRoute>
            <BookAppointment />
          </ProtectedRoute>
        } />
        
        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </Router>
    </AuthProvider>
  )
}

export default App;