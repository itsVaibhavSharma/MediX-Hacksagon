# backend/app/routers/disease.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
from datetime import datetime

from app.models.database import User, DiseaseResult
from app.models.schemas import DiseaseDetectionRequest, DiseaseDetectionResponse, PredictionResult
from app.utils.database import get_db
from app.utils.auth import get_current_user
from app.services.ai_models import medical_ai_service
from app.services.gemini_service import gemini_service

router = APIRouter()

@router.get("/models")
async def get_available_models():
    """Get list of available AI models"""
    models = medical_ai_service.get_available_models()
    return {
        "available_models": models,
        "model_descriptions": {
            "nail": "Nail disease detection (fungus, trauma, psoriasis, etc.)",
            "skin": "Skin condition analysis (acne, eczema, melanoma, etc.)",
            "oral": "Oral health assessment (caries, gingivitis, ulcers, etc.)",
            "eye": "Eye disease detection (cataract, conjunctivitis, etc.)",
            "bone": "Bone fracture detection in X-ray images",
            "chest": "Chest X-ray analysis for multiple conditions"
        }
    }

@router.post("/detect", response_model=DiseaseDetectionResponse)
async def detect_disease(
    request: DiseaseDetectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detect disease from uploaded image"""
    
    try:
        # Validate model type
        if request.disease_type not in medical_ai_service.get_available_models():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model type '{request.disease_type}' not available"
            )
        
        # Get AI predictions
        predictions = medical_ai_service.predict(request.image_base64, request.disease_type)
        
        if not predictions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get predictions from AI model"
            )
        
        # Convert to response format
        prediction_results = [
            PredictionResult(disease=pred['disease'], confidence=pred['confidence'])
            for pred in predictions
        ]
        
        # Initialize response
        response = DiseaseDetectionResponse(
            predictions=prediction_results,
            final_diagnosis=None,
            gemini_analysis=None,
            recommendations=None
        )
        
        # If symptoms are provided, use Gemini for analysis
        gemini_analysis_result = None
        if request.symptoms and request.symptoms.strip():
            try:
                # Prepare user context
                user_context = {
                    'age': current_user.age,
                    'gender': current_user.gender,
                    'city': current_user.city
                }
                
                # Get Gemini analysis
                gemini_analysis_result = gemini_service.analyze_with_symptoms(
                    predictions, 
                    request.symptoms, 
                    user_context
                )
                
                response.final_diagnosis = gemini_analysis_result.get('likely_diagnosis')
                response.gemini_analysis = gemini_analysis_result.get('follow_up_questions')
                response.recommendations = gemini_analysis_result.get('recommendations')
                
            except Exception as e:
                print(f"Gemini analysis error: {str(e)}")
                # Continue without Gemini analysis if it fails
                response.final_diagnosis = predictions[0]['disease']
                response.recommendations = "Please consult with a healthcare professional for proper evaluation."
        else:
            # No symptoms provided, use top prediction
            response.final_diagnosis = predictions[0]['disease']
            
            # Get basic disease information
            try:
                disease_info = gemini_service.get_disease_information(predictions[0]['disease'], "brief")
                response.recommendations = disease_info
            except Exception as e:
                print(f"Disease info error: {str(e)}")
                response.recommendations = "Please consult with a healthcare professional for more information."
        
        # Save results to database
        try:
            # Generate unique filename for image
            image_filename = f"{current_user.id}_{request.disease_type}_{uuid.uuid4().hex[:8]}.jpg"
            image_path = f"uploads/{image_filename}"
            
            # Create directory if it doesn't exist
            os.makedirs("uploads", exist_ok=True)
            
            # Save image (in production, you might want to save the actual file)
            # For now, we'll just store the path reference
            
            disease_result = DiseaseResult(
                user_id=current_user.id,
                disease_type=request.disease_type,
                image_path=image_path,
                prediction_1=predictions[0]['disease'],
                confidence_1=predictions[0]['confidence'],
                prediction_2=predictions[1]['disease'] if len(predictions) > 1 else None,
                confidence_2=predictions[1]['confidence'] if len(predictions) > 1 else None,
                prediction_3=predictions[2]['disease'] if len(predictions) > 2 else None,
                confidence_3=predictions[2]['confidence'] if len(predictions) > 2 else None,
                final_diagnosis=response.final_diagnosis,
                symptoms_provided=request.symptoms,
                gemini_analysis=str(gemini_analysis_result) if gemini_analysis_result else None
            )
            
            db.add(disease_result)
            db.commit()
            
        except Exception as e:
            print(f"Database save error: {str(e)}")
            # Continue even if database save fails
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Disease detection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )

@router.get("/history")
async def get_detection_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's disease detection history"""
    
    results = db.query(DiseaseResult).filter(
        DiseaseResult.user_id == current_user.id
    ).order_by(DiseaseResult.created_at.desc()).limit(20).all()
    
    history = []
    for result in results:
        history.append({
            "id": result.id,
            "disease_type": result.disease_type,
            "final_diagnosis": result.final_diagnosis,
            "top_prediction": result.prediction_1,
            "confidence": result.confidence_1,
            "symptoms_provided": bool(result.symptoms_provided),
            "created_at": result.created_at
        })
    
    return {"history": history}

@router.get("/result/{result_id}")
async def get_detection_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed results of a specific detection"""
    
    result = db.query(DiseaseResult).filter(
        DiseaseResult.id == result_id,
        DiseaseResult.user_id == current_user.id
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection result not found"
        )
    
    predictions = []
    if result.prediction_1:
        predictions.append({"disease": result.prediction_1, "confidence": result.confidence_1})
    if result.prediction_2:
        predictions.append({"disease": result.prediction_2, "confidence": result.confidence_2})
    if result.prediction_3:
        predictions.append({"disease": result.prediction_3, "confidence": result.confidence_3})
    
    return {
        "id": result.id,
        "disease_type": result.disease_type,
        "predictions": predictions,
        "final_diagnosis": result.final_diagnosis,
        "symptoms_provided": result.symptoms_provided,
        "gemini_analysis": result.gemini_analysis,
        "created_at": result.created_at
    }

@router.post("/emergency-assessment")
async def assess_emergency(
    symptoms: dict,
    current_user: User = Depends(get_current_user)
):
    """Assess if symptoms require emergency attention"""
    
    try:
        symptom_text = symptoms.get("symptoms", "")
        if not symptom_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Symptoms text is required"
            )
        
        assessment = gemini_service.get_emergency_assessment(symptom_text)
        return assessment
        
    except Exception as e:
        print(f"Emergency assessment error: {str(e)}")
        return {
            "urgency_level": "urgent",
            "reasoning": "Unable to assess - please seek medical attention",
            "immediate_actions": "Contact healthcare provider or emergency services",
            "timeline": "Seek medical attention promptly"
        }