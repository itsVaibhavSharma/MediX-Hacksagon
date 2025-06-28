
# backend/app/routers/appointments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.models.database import User, Appointment
from app.models.schemas import AppointmentCreate, AppointmentResponse, DoctorSearch
from app.utils.database import get_db
from app.utils.auth import get_current_user

router = APIRouter()

@router.get("/doctors/search")
async def search_doctors(
    city: str,
    specialty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search for doctors by city and specialty"""
    
    query = db.query(User).filter(
        User.user_type == "doctor",
        User.is_active == True,
        User.city.ilike(f"%{city}%")
    )
    
    if specialty:
        query = query.filter(User.specialty.ilike(f"%{specialty}%"))
    
    doctors = query.limit(20).all()
    
    return {
        "doctors": [
            {
                "id": doc.id,
                "name": doc.full_name,
                "specialty": doc.specialty,
                "city": doc.city,
                "experience_years": doc.experience_years,
                "phone": doc.phone
            }
            for doc in doctors
        ]
    }

@router.get("/doctors/specialties")
async def get_specialties(db: Session = Depends(get_db)):
    """Get list of available medical specialties"""
    
    specialties = db.query(User.specialty).filter(
        User.user_type == "doctor",
        User.is_active == True,
        User.specialty.isnot(None)
    ).distinct().all()
    
    return {
        "specialties": [spec[0] for spec in specialties if spec[0]]
    }

@router.post("/book", response_model=dict)
async def book_appointment(
    appointment: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Book an appointment with a doctor"""
    
    # Verify current user is a patient
    if current_user.user_type != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can book appointments"
        )
    
    # Verify doctor exists and is active
    doctor = db.query(User).filter(
        User.id == appointment.doctor_id,
        User.user_type == "doctor",
        User.is_active == True
    ).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Check if appointment time is in the future
    if appointment.appointment_date <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment must be scheduled for a future date"
        )
    
    # Check for conflicting appointments (basic check)
    existing = db.query(Appointment).filter(
        Appointment.doctor_id == appointment.doctor_id,
        Appointment.appointment_date.between(
            appointment.appointment_date - timedelta(minutes=30),
            appointment.appointment_date + timedelta(minutes=30)
        ),
        Appointment.status == "scheduled"
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor is not available at this time"
        )
    
    # Generate Google Meet link (simplified)
    meeting_id = str(uuid.uuid4())[:8]
    meet_link = f"https://meet.google.com/{meeting_id}"
    
    # Create appointment
    db_appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        disease_type=appointment.disease_type,
        symptoms=appointment.symptoms,
        meet_link=meet_link,
        meeting_id=meeting_id,
        status="scheduled"
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return {
        "message": "Appointment booked successfully",
        "appointment_id": db_appointment.id,
        "meet_link": meet_link,
        "doctor_name": doctor.full_name,
        "appointment_date": appointment.appointment_date
    }

@router.get("/my-appointments")
async def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get appointments for current user (patient or doctor)"""
    
    if current_user.user_type == "patient":
        appointments = db.query(Appointment).filter(
            Appointment.patient_id == current_user.id
        ).order_by(Appointment.appointment_date.desc()).all()
        
        return {
            "appointments": [
                {
                    "id": apt.id,
                    "doctor_name": apt.doctor.full_name if apt.doctor else "Unknown",
                    "doctor_specialty": apt.doctor.specialty if apt.doctor else None,
                    "appointment_date": apt.appointment_date,
                    "status": apt.status,
                    "disease_type": apt.disease_type,
                    "meet_link": apt.meet_link,
                    "symptoms": apt.symptoms
                }
                for apt in appointments
            ]
        }
    
    elif current_user.user_type == "doctor":
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == current_user.id
        ).order_by(Appointment.appointment_date.desc()).all()
        
        return {
            "appointments": [
                {
                    "id": apt.id,
                    "patient_name": apt.patient.full_name if apt.patient else "Unknown",
                    "patient_age": apt.patient.age if apt.patient else None,
                    "appointment_date": apt.appointment_date,
                    "status": apt.status,
                    "disease_type": apt.disease_type,
                    "meet_link": apt.meet_link,
                    "symptoms": apt.symptoms
                }
                for apt in appointments
            ]
        }

@router.put("/appointments/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: int,
    status_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update appointment status"""
    
    new_status = status_data.get("status")
    if new_status not in ["scheduled", "completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )
    
    # Find appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check if user has permission to update
    if current_user.user_type == "patient" and appointment.patient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    if current_user.user_type == "doctor" and appointment.doctor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Update status
    appointment.status = new_status
    if "notes" in status_data:
        appointment.notes = status_data["notes"]
    
    db.commit()
    
    return {"message": "Appointment status updated successfully"}