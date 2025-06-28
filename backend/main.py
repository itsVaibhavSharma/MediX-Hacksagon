# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

from app.utils.database import create_tables
from app.routers import auth, disease, chat, appointments

load_dotenv()

app = FastAPI(
    title="MediX - Medical AI Platform",
    description="AI-powered medical diagnosis and consultation platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(disease.router, prefix="/api/disease", tags=["Disease Detection"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chat"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])

@app.get("/")
async def root():
    return {"message": "MediX API is running! "}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "MediX API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )