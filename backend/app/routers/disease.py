# backend/app/routers/disease.py - Updated with better error handling
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
    """Get list of available AI models with detailed information"""
    try:
        available_models = medical_ai_service.get_available_models()
        model_info = medical_ai_service.get_model_info()
        
        return {
            "available_models": available_models,
            "model_descriptions": {
                "nail": "Nail disease detection - Analyzes nail conditions including fungus, trauma, psoriasis (6 conditions)",
                "skin": "Skin disease analysis - Detects various skin conditions using DenseNet architecture (22 conditions)", 
                "oral": "Oral health assessment - Identifies dental and gum diseases (6 conditions)",
                "eye": "Eye disease detection - Diagnoses eye conditions like cataract, conjunctivitis (5 conditions)",
                "bone": "Bone fracture detection - Binary classification for X-ray fracture analysis",
                "chest": "Chest X-ray analysis - Multi-label detection of chest conditions (14 conditions)"
            },
            "model_info": model_info,
            "total_models": len(available_models)
        }
    except Exception as e:
        print(f"Error getting models: {str(e)}")
        return {
            "available_models": [],
            "model_descriptions": {},
            "error": "Models not loaded. Please check model files."
        }

@router.post("/detect", response_model=DiseaseDetectionResponse)
async def detect_disease(
    request: DiseaseDetectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detect disease from uploaded image with improved error handling"""
    
    try:
        # Validate model type
        available_models = medical_ai_service.get_available_models()
        if request.disease_type not in available_models:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model type '{request.disease_type}' not available. Available models: {available_models}"
            )
        
        print(f"Processing {request.disease_type} detection for user {current_user.email}")
        
        # Get AI predictions
        try:
            predictions = medical_ai_service.predict(request.image_base64, request.disease_type)
        except Exception as e:
            print(f"AI prediction error: {str(e)}")
            # Return a fallback response
            predictions = [
                {"disease": f"Unable to analyze {request.disease_type}", "confidence": 0.0}
            ]
        
        if not predictions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get predictions from AI model"
            )
        
        # Convert to response format
        prediction_results = [
            PredictionResult(disease=pred['disease'], confidence=pred['confidence'])
            for pred in predictions[:3]  # Take top 3
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
                
                response.final_diagnosis = gemini_analysis_result.get('likely_diagnosis', predictions[0]['disease'])
                response.gemini_analysis = gemini_analysis_result.get('follow_up_questions', 'Please consult with a healthcare professional.')
                response.recommendations = gemini_analysis_result.get('recommendations', 'Seek medical attention for proper diagnosis.')
                
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
                response.recommendations = "Please consult with a healthcare professional for more information about this condition."
        
        # Save results to database
        try:
            # Generate unique filename for image
            image_filename = f"{current_user.id}_{request.disease_type}_{uuid.uuid4().hex[:8]}.jpg"
            image_path = f"uploads/{image_filename}"
            
            # Create directory if it doesn't exist
            os.makedirs("uploads", exist_ok=True)
            
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
            
            print(f"Saved detection result for {request.disease_type}: {response.final_diagnosis}")
            
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
            detail=f"Error processing {request.disease_type} image: {str(e)}"
        )

@router.get("/test-models")
async def test_all_models():
    """Test all AI models with sample data"""
    try:
        available_models = medical_ai_service.get_available_models()
        results = {}
        
        # Create a simple test image (1x1 white pixel)
        import base64
        from PIL import Image
        import io
        
        # Create test image
        test_img = Image.new('RGB', (224, 224), color='white')
        buffer = io.BytesIO()
        test_img.save(buffer, format='JPEG')
        test_image_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        for model_type in available_models:
            try:
                predictions = medical_ai_service.predict(test_image_b64, model_type)
                results[model_type] = {
                    "status": "✅ Working",
                    "predictions": len(predictions),
                    "top_prediction": predictions[0] if predictions else None,
                    "error": None
                }
            except Exception as e:
                results[model_type] = {
                    "status": "❌ Error", 
                    "predictions": 0,
                    "top_prediction": None,
                    "error": str(e)
                }
        
        return {
            "total_models": len(available_models),
            "working_models": len([r for r in results.values() if r["status"] == "✅ Working"]),
            "results": results
        }
        
    except Exception as e:
        return {
            "error": f"Test failed: {str(e)}",
            "total_models": 0,
            "working_models": 0,
            "results": {}
        }

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

# backend/test_models_updated.py - Enhanced model testing script
"""
Enhanced test script to verify all AI models are loaded correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_models import medical_ai_service
from app.services.gemini_service import gemini_service
import base64
from PIL import Image
import io

def create_test_image():
    """Create a simple test image for model testing"""
    # Create a simple colored image
    img = Image.new('RGB', (224, 224), color='white')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str

def test_models():
    """Test all loaded models"""
    print("🧪 Testing MediX AI Models...")
    print("=" * 60)
    
    # Get available models
    available_models = medical_ai_service.get_available_models()
    model_info = medical_ai_service.get_model_info()
    
    print(f"Available models: {available_models}")
    print(f"Total models loaded: {len(available_models)}")
    
    if not available_models:
        print("❌ No models loaded! Please check:")
        print("1. Model files (.pth) are in backend/models/ directory")
        print("2. Model files have correct names")
        print("3. PyTorch and torchvision are installed")
        print("4. Model architectures match training code")
        return False
    
    # Print detailed model info
    print("\n📊 Model Information:")
    for model_type, info in model_info.items():
        print(f"\n{model_type.upper()} Model:")
        print(f"  ✅ Loaded: {info['loaded']}")
        print(f"  🏗️  Architecture: {info['architecture']}")
        print(f"  📊 Classes: {info['num_classes']}")
        print(f"  💻 Device: {info['device']}")
        print(f"  📝 Conditions: {', '.join(info['classes'][:3])}{'...' if len(info['classes']) > 3 else ''}")
    
    # Create test image
    test_image = create_test_image()
    
    # Test each model
    print("\n🔬 Testing Model Predictions:")
    all_passed = True
    for model_type in available_models:
        print(f"\n🧪 Testing {model_type} model...")
        
        try:
            predictions = medical_ai_service.predict(test_image, model_type)
            
            if predictions:
                print(f"✅ {model_type} model working!")
                print(f"   📊 Predictions: {len(predictions)} classes detected")
                print(f"   🎯 Top prediction: {predictions[0]['disease']} ({predictions[0]['confidence']:.3f})")
                
                # Show all predictions for multi-label models
                if model_type == 'chest' and len(predictions) > 1:
                    print(f"   📋 All predictions: {len(predictions)} conditions detected")
                elif len(predictions) > 1:
                    print(f"   📋 Top 3: {[p['disease'] for p in predictions[:3]]}")
                    
            else:
                print(f"❌ {model_type} model returned no predictions")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {model_type} model failed: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All models are working correctly!")
        print("✅ Ready for disease detection!")
    else:
        print("⚠️  Some models have issues. Check the errors above.")
        print("💡 Make sure model files match the expected names:")
        print("   - nail_disease_model.pth or nail_disease_classifier_best.pth")
        print("   - skin_disease_model.pth or densenet_efficient_skin_disease.pth")
        print("   - oral_disease_model.pth or oral_disease_model_final.pth")
        print("   - eye_disease_model.pth or eye_disease_efficientnet_b3.pth")
        print("   - bone_fracture_model.pth or best_bone_fracture_model.pth")
        print("   - chest_xray_model.pth or chest_xray_pytorch_model.pth")
    
    return all_passed

def test_gemini_service():
    """Test Gemini AI service"""
    print("\n🤖 Testing Gemini AI Service...")
    print("=" * 40)
    
    try:
        # Test basic functionality
        response = gemini_service.get_disease_information("fever", "brief")
        
        if response and len(response) > 10:
            print("✅ Gemini AI service working!")
            print(f"   📝 Sample response length: {len(response)} characters")
            print(f"   📋 Preview: {response[:100]}...")
        else:
            print("❌ Gemini AI service not responding properly")
            return False
            
    except Exception as e:
        print(f"❌ Gemini AI service failed: {str(e)}")
        print("🔑 Check your GEMINI_API_KEY in .env file")
        return False
    
    return True

if __name__ == "__main__":
    print("🏥 MediX AI Models Enhanced Test Suite")
    print("=" * 50)
    
    # Test AI models
    models_ok = test_models()
    
    # Test Gemini service
    gemini_ok = test_gemini_service()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"🤖 AI Models: {'✅ PASS' if models_ok else '❌ FAIL'}")
    print(f"🧠 Gemini AI: {'✅ PASS' if gemini_ok else '❌ FAIL'}")
    
    if models_ok and gemini_ok:
        print("\n🎉 All systems ready! You can start the FastAPI server.")
        print("🚀 Run: python -m uvicorn app.main:app --reload")
    else:
        print("\n⚠️  Please fix the issues above before running the server.")
        if not models_ok:
            print("🔧 Model troubleshooting:")
            print("   1. Check model files exist in backend/models/")
            print("   2. Verify model architectures match training code")
            print("   3. Ensure PyTorch dependencies are installed")
        if not gemini_ok:
            print("🔧 Gemini troubleshooting:")
            print("   1. Check GEMINI_API_KEY in .env file")
            print("   2. Verify internet connection")
            print("   3. Check API quota limits")