# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.models.database import User
from app.models.schemas import UserCreatePatient, UserCreateDoctor, UserLogin, UserResponse
from app.utils.database import get_db
from app.utils.auth import get_password_hash, verify_password, create_access_token
from app.utils.auth import get_current_user

router = APIRouter()

@router.post("/signup/patient", response_model=dict)
async def signup_patient(user: UserCreatePatient, db: Session = Depends(get_db)):
    """Register a new patient"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new patient
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        user_type="patient",
        city=user.city,
        phone=user.phone,
        age=user.age,
        gender=user.gender
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "message": "Patient registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user)
    }

@router.post("/signup/doctor", response_model=dict)
async def signup_doctor(user: UserCreateDoctor, db: Session = Depends(get_db)):
    """Register a new doctor"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new doctor
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        user_type="doctor",
        city=user.city,
        phone=user.phone,
        specialty=user.specialty,
        license_number=user.license_number,
        experience_years=user.experience_years
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "message": "Doctor registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user)
    }

@router.post("/login", response_model=dict)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    updated_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    
    # Update allowed fields based on user type
    allowed_fields = ["full_name", "phone", "city"]
    
    if current_user.user_type == "patient":
        allowed_fields.extend(["age", "gender"])
    elif current_user.user_type == "doctor":
        allowed_fields.extend(["specialty", "experience_years"])
    
    for field, value in updated_data.items():
        if field in allowed_fields and hasattr(current_user, field):
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)