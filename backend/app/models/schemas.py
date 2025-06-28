
# backend/app/models/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    user_type: str
    city: str
    phone: Optional[str] = None

class UserCreatePatient(UserBase):
    password: str
    age: Optional[int] = None
    gender: Optional[str] = None

class UserCreateDoctor(UserBase):
    password: str
    specialty: str
    license_number: str
    experience_years: int

class UserResponse(UserBase):
    id: int
    specialty: Optional[str] = None
    experience_years: Optional[int] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Disease detection schemas
class DiseaseDetectionRequest(BaseModel):
    disease_type: str
    image_base64: str
    symptoms: Optional[str] = None

class PredictionResult(BaseModel):
    disease: str
    confidence: float

class DiseaseDetectionResponse(BaseModel):
    predictions: List[PredictionResult]
    final_diagnosis: Optional[str] = None
    gemini_analysis: Optional[str] = None
    recommendations: Optional[str] = None

# Chat schemas
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    context_type: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

# Appointment schemas
class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: datetime
    disease_type: Optional[str] = None
    symptoms: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    doctor_name: str
    patient_name: str
    appointment_date: datetime
    status: str
    disease_type: Optional[str] = None
    meet_link: Optional[str] = None
    
    class Config:
        from_attributes = True

class DoctorSearch(BaseModel):
    city: str
    specialty: Optional[str] = None