# backend/app/models/database.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    user_type = Column(String, nullable=False)  # 'patient' or 'doctor'
    city = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    
    # Doctor specific fields
    specialty = Column(String, nullable=True)  # Only for doctors
    license_number = Column(String, nullable=True)  # Only for doctors
    experience_years = Column(Integer, nullable=True)  # Only for doctors
    
    # Patient specific fields
    age = Column(Integer, nullable=True)  # Only for patients
    gender = Column(String, nullable=True)  # Only for patients
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    appointments_as_patient = relationship("Appointment", foreign_keys="Appointment.patient_id", back_populates="patient")
    appointments_as_doctor = relationship("Appointment", foreign_keys="Appointment.doctor_id", back_populates="doctor")
    chat_sessions = relationship("ChatSession", back_populates="user")
    disease_results = relationship("DiseaseResult", back_populates="user")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    appointment_date = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled
    
    # Disease context
    disease_type = Column(String, nullable=True)
    symptoms = Column(Text, nullable=True)
    
    # Google Meet details
    meet_link = Column(String, nullable=True)
    meeting_id = Column(String, nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="appointments_as_patient")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="appointments_as_doctor")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, nullable=False, index=True)
    
    message_type = Column(String, nullable=False)  # 'user' or 'assistant'
    message_content = Column(Text, nullable=False)
    
    # Context for RAG
    context_type = Column(String, nullable=True)  # 'symptom_analysis', 'disease_followup', etc.
    related_disease = Column(String, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")

class DiseaseResult(Base):
    __tablename__ = "disease_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Disease detection details
    disease_type = Column(String, nullable=False)  # nail, skin, bone, etc.
    image_path = Column(String, nullable=True)  # Path to uploaded image
    
    # Model predictions (top 3)
    prediction_1 = Column(String, nullable=False)
    confidence_1 = Column(Float, nullable=False)
    prediction_2 = Column(String, nullable=True)
    confidence_2 = Column(Float, nullable=True)
    prediction_3 = Column(String, nullable=True)
    confidence_3 = Column(Float, nullable=True)
    
    # Final diagnosis (after Gemini analysis if symptoms provided)
    final_diagnosis = Column(String, nullable=True)
    symptoms_provided = Column(Text, nullable=True)
    gemini_analysis = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="disease_results")
