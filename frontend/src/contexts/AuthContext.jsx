
// frontend/src/contexts/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../services/api'
import toast from 'react-hot-toast'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('medix_token')
      if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        const response = await api.get('/auth/me')
        setUser(response.data)
      }
    } catch (error) {
      localStorage.removeItem('medix_token')
      delete api.defaults.headers.common['Authorization']
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password })
      const { access_token, user: userData } = response.data
      
      localStorage.setItem('medix_token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      setUser(userData)
      
      toast.success(`Welcome back, ${userData.full_name}!`)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const signup = async (userData) => {
    try {
      const endpoint = userData.user_type === 'patient' ? '/auth/signup/patient' : '/auth/signup/doctor'
      const response = await api.post(endpoint, userData)
      const { access_token, user: newUser } = response.data
      
      localStorage.setItem('medix_token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      setUser(newUser)
      
      toast.success(`Welcome to MediX, ${newUser.full_name}!`)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || 'Signup failed'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const logout = () => {
    localStorage.removeItem('medix_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
    toast.success('Logged out successfully')
  }

  const value = {
    user,
    loading,
    login,
    signup,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}