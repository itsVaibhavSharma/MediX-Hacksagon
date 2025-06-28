
// frontend/src/utils/constants.js
export const API_BASE_URL = 'http://localhost:8000/api'

export const DISEASE_TYPES = {
  NAIL: 'nail',
  SKIN: 'skin', 
  ORAL: 'oral',
  EYE: 'eye',
  BONE: 'bone',
  CHEST: 'chest'
}

export const USER_TYPES = {
  PATIENT: 'patient',
  DOCTOR: 'doctor'
}

export const APPOINTMENT_STATUS = {
  SCHEDULED: 'scheduled',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled'
}

export const MEDICAL_SPECIALTIES = [
  'General Medicine',
  'Cardiology', 
  'Dermatology',
  'Neurology',
  'Orthopedics',
  'Ophthalmology',
  'Dentistry',
  'Psychiatry',
  'Radiology',
  'Emergency Medicine',
  'Pediatrics',
  'Gynecology',
  'ENT',
  'Oncology',
  'Endocrinology'
]

export const EMERGENCY_KEYWORDS = [
  'chest pain',
  'difficulty breathing', 
  'severe pain',
  'bleeding heavily',
  'unconscious',
  'stroke',
  'heart attack',
  'suicide',
  'overdose',
  'severe headache',
  'high fever',
  'can\'t breathe'
]
