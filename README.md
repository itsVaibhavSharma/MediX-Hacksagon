# Medix - AI-Powered Medical Diagnosis Platform

Medix is an intelligent healthcare platform that leverages AI and machine learning to provide accessible medical diagnosis and consultation services. Built for the Hacksagon (IIITM + IEEE) hackathon, this platform bridges the gap between patients and medical professionals through cutting-edge technology.

## Overview

Medix offers a comprehensive solution for medical diagnosis combining image-based disease detection with symptom-based consultation. The platform serves both patients seeking preliminary diagnosis and doctors providing professional healthcare services.

## Key Features

### For Patients
- **Image-Based Disease Detection**: Upload medical images for AI-powered diagnosis across multiple domains
- **Symptom-Based Consultation**: Interactive chat with AI for symptom analysis and health guidance
- **Doctor Recommendations**: Find nearby specialists based on detected conditions and location
- **Appointment Scheduling**: Book consultations with integrated Google Meet sessions
- **Personalized Health History**: RAG-based chat system that maintains conversation context

### For Doctors
- **Professional Dashboard**: Manage patient appointments and consultations
- **Appointment Management**: View scheduled meetings and patient information
- **Integrated Video Consultations**: Conduct appointments through Google Meet integration

## Supported Medical Domains

Our platform includes trained models for detecting various medical conditions:

- **Skin Diseases**: Detection and classification of common dermatological conditions
- **Nail Disorders**: Analysis of nail-related health issues
- **Bone Fractures**: X-ray analysis for fracture detection and classification
- **Chest X-Ray Analysis**: Respiratory and chest-related condition detection
- **Oral Diseases**: Dental and oral health condition identification
- **Eye Diseases**: Ophthalmological condition detection and analysis

## Technology Stack

### Frontend
- **React**: Modern UI framework for responsive web application
- **Tailwind CSS**: Utility-first CSS framework for beautiful, responsive design
- **Medium-toned Theme**: Carefully designed UI with focus on accessibility and user experience

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLite**: Lightweight database for efficient data storage
- **PyTorch**: Deep learning framework for AI model deployment

### AI & Machine Learning
- **Custom Trained Models**: Specialized models for each medical domain
- **Gemini API**: Advanced AI integration for symptom analysis and consultation
- **RAG (Retrieval-Augmented Generation)**: Personalized chat experience with memory

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```bash
   python main.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

### Environment Configuration
Create a `.env` file in the root directory with necessary environment variables for API keys and configuration.

## Project Structure

```
medix/
├── frontend/                          # React + Tailwind CSS
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth/
│   │   │   │   ├── Login.jsx
│   │   │   │   └── Signup.jsx
│   │   │   ├── Dashboard/
│   │   │   │   ├── PatientDashboard.jsx
│   │   │   │   └── DoctorDashboard.jsx
│   │   │   ├── Disease/
│   │   │   │   ├── ImageDetection.jsx
│   │   │   │   ├── SymptomChat.jsx
│   │   │   │   └── DiseaseResult.jsx
│   │   │   ├── Appointments/
│   │   │   │   ├── BookAppointment.jsx
│   │   │   │   └── AppointmentList.jsx
│   │   │   ├── Chat/
│   │   │   │   └── AIChat.jsx
│   │   │   └── Layout/
│   │   │       ├── Header.jsx
│   │   │       └── Sidebar.jsx
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── utils/
│   │   │   └── constants.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/                           # FastAPI + Python
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   └── schemas.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── disease.py
│   │   │   ├── chat.py
│   │   │   └── appointments.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ai_models.py
│   │   │   ├── gemini_service.py
│   │   │   └── image_processing.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── database.py
│   │       └── auth.py
│   ├── models/                        # PyTorch model files
│   │   ├── nail_disease_model.pth
│   │   ├── skin_disease_model.pth
│   │   ├── bone_fracture_model.pth
│   │   ├── chest_xray_model.pth
│   │   ├── oral_disease_model.pth
│   │   └── eye_disease_model.pth
│   ├── requirements.txt
│   └── database.db                    # SQLite database
│
├── .env                              # Environment variables
├── .gitignore
└── README.md
```

## How It Works

### Image-Based Diagnosis Workflow
1. **User Registration**: Sign up as patient or doctor with city specification
2. **Domain Selection**: Choose from available medical domains
3. **Image Upload**: Upload medical images with optional symptom description
4. **AI Analysis**: Custom-trained models analyze the uploaded images
5. **Results**: Top 3 predictions with confidence scores
6. **Gemini Integration**: If symptoms provided, Gemini API refines diagnosis
7. **Follow-up Chat**: Continued conversation for clarification and guidance
8. **Doctor Recommendation**: Suggest nearby specialists based on diagnosis and location

### Symptom-Based Consultation
1. **Interactive Chat**: RAG-based conversation with AI
2. **Symptom Analysis**: Personalized health guidance based on described symptoms
3. **Medical History**: System recalls and references past interactions
4. **Professional Referral**: Recommend appropriate medical specialists when needed

## Demo & Resources

- **Demo Video**: [Watch Demo](https://drive.google.com/file/d/10XOconvXmysl5embjsxK1pkwM3haPqCj/view?usp=sharing)
- **Trained Models**: [Download Models](https://drive.google.com/drive/folders/15S3HVPL6o4sPxL34fJa-ggBsWsJstVMu?usp=sharing)

## Development Team

This project is developed by a dedicated team of students:

- **Vaibhav Sharma** - [itsvaibhavsharma007@gmail.com](mailto:itsvaibhavsharma007@gmail.com)
- **Shreya Khantal** - [khantalshreya@gmail.com](mailto:khantalshreya@gmail.com)
- **Prasanna Saxena** - [prasannasaxena4@gmail.com](mailto:prasannasaxena4@gmail.com)
- **Akshara Rathore** - [itsakshararathore@gmail.com](mailto:itsakshararathore@gmail.com)

## License

This project is developed for educational and hackathon purposes. Please ensure appropriate licensing before any commercial use.