# backend/app/services/ai_models.py
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
import numpy as np
from PIL import Image
import io
import base64
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)

# Model architectures based on training code
class NailDiseaseClassifier(nn.Module):
    def __init__(self, num_classes=6):
        super(NailDiseaseClassifier, self).__init__()
        self.backbone = models.efficientnet_b0(pretrained=False)
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)

class SkinDiseaseClassifier(nn.Module):
    def __init__(self, num_classes=22):
        super(SkinDiseaseClassifier, self).__init__()
        self.backbone = models.resnet50(pretrained=False)
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.4),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)

class OralDiseaseClassifier(nn.Module):
    def __init__(self, num_classes=6):
        super(OralDiseaseClassifier, self).__init__()
        self.backbone = models.resnet50(pretrained=False)
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)

class EyeDiseaseClassifier(nn.Module):
    def __init__(self, num_classes=5):
        super(EyeDiseaseClassifier, self).__init__()
        self.backbone = models.efficientnet_b3(pretrained=False)
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(num_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)

class BoneFractureClassifier(nn.Module):
    def __init__(self, num_classes=2):
        super(BoneFractureClassifier, self).__init__()
        self.backbone = models.resnet50(pretrained=False)
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)

class ChestXRayClassifier(nn.Module):
    def __init__(self, num_classes=14):  # Common chest conditions
        super(ChestXRayClassifier, self).__init__()
        self.backbone = models.mobilenet_v2(pretrained=False)
        self.features = self.backbone.features
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(1280, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes),
            nn.Sigmoid()  # Multi-label classification
        )
    
    def forward(self, x):
        features = self.features(x)
        output = self.classifier(features)
        return output

class MedicalAIService:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models = {}
        self.class_names = {
            'nail': ['Healthy', 'Nail fungus', 'Ingrown nail', 'Nail psoriasis', 'Nail trauma', 'Paronychia'],
            'skin': ['Acne', 'Eczema', 'Melanoma', 'Psoriasis', 'Basal Cell Carcinoma', 'Dermatitis', 
                    'Vitiligo', 'Rosacea', 'Hives', 'Seborrheic Keratosis', 'Warts', 'Herpes',
                    'Impetigo', 'Cellulitis', 'Ringworm', 'Scabies', 'Age Spots', 'Moles',
                    'Chickenpox', 'Shingles', 'Cold Sores', 'Normal'],
            'oral': ['Caries', 'Calculus', 'Gingivitis', 'Tooth Discoloration', 'Ulcers', 'Hypodontia'],
            'eye': ['Cataract', 'Conjunctivitis', 'Eyelid', 'Normal', 'Uveitis'],
            'bone': ['Not Fractured', 'Fractured'],
            'chest': ['Atelectasis', 'Cardiomegaly', 'Effusion', 'Infiltration', 'Mass', 'Nodule', 
                     'Pneumonia', 'Pneumothorax', 'Consolidation', 'Edema', 'Emphysema', 
                     'Fibrosis', 'Pleural_Thickening', 'Hernia']
        }
        
        # Load models
        self._load_models()
    
    def _load_models(self):
        """Load all trained models"""
        model_configs = {
            'nail': {'class': NailDiseaseClassifier, 'num_classes': 6, 'file': 'nail_disease_model.pth'},
            'skin': {'class': SkinDiseaseClassifier, 'num_classes': 22, 'file': 'skin_disease_model.pth'},
            'oral': {'class': OralDiseaseClassifier, 'num_classes': 6, 'file': 'oral_disease_model.pth'},
            'eye': {'class': EyeDiseaseClassifier, 'num_classes': 5, 'file': 'eye_disease_model.pth'},
            'bone': {'class': BoneFractureClassifier, 'num_classes': 2, 'file': 'bone_fracture_model.pth'},
            'chest': {'class': ChestXRayClassifier, 'num_classes': 14, 'file': 'chest_xray_model.pth'}
        }
        
        for model_type, config in model_configs.items():
            try:
                model = config['class'](config['num_classes'])
                model_path = f"models/{config['file']}"
                
                # Try to load the model
                checkpoint = torch.load(model_path, map_location=self.device)
                
                # Handle different checkpoint formats
                if isinstance(checkpoint, dict):
                    if 'model_state_dict' in checkpoint:
                        model.load_state_dict(checkpoint['model_state_dict'])
                    elif 'state_dict' in checkpoint:
                        model.load_state_dict(checkpoint['state_dict'])
                    else:
                        model.load_state_dict(checkpoint)
                else:
                    model.load_state_dict(checkpoint)
                
                model.to(self.device)
                model.eval()
                self.models[model_type] = model
                logger.info(f"Loaded {model_type} model successfully")
                
            except Exception as e:
                logger.error(f"Failed to load {model_type} model: {str(e)}")
                # Continue loading other models even if one fails
    
    def _get_transforms(self, model_type: str):
        """Get appropriate transforms for each model type"""
        if model_type == 'chest':
            # Chest X-rays are grayscale, convert to RGB
            return transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.Lambda(lambda x: x.convert('RGB') if x.mode != 'RGB' else x),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        else:
            return transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
    
    def _preprocess_image(self, image_base64: str, model_type: str) -> torch.Tensor:
        """Preprocess image for model inference"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply transforms
            transform = self._get_transforms(model_type)
            image_tensor = transform(image).unsqueeze(0)  # Add batch dimension
            
            return image_tensor.to(self.device)
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise ValueError(f"Failed to preprocess image: {str(e)}")
    
    def predict(self, image_base64: str, model_type: str) -> List[Dict[str, float]]:
        """Make prediction using specified model"""
        if model_type not in self.models:
            raise ValueError(f"Model type '{model_type}' not available")
        
        model = self.models[model_type]
        image_tensor = self._preprocess_image(image_base64, model_type)
        
        with torch.no_grad():
            outputs = model(image_tensor)
            
            if model_type == 'chest':
                # Multi-label classification - use sigmoid probabilities
                probabilities = torch.sigmoid(outputs).cpu().numpy()[0]
            else:
                # Single-label classification - use softmax probabilities
                probabilities = torch.softmax(outputs, dim=1).cpu().numpy()[0]
            
            # Get class names for this model
            classes = self.class_names[model_type]
            
            # Create results with class names and confidence scores
            results = []
            for i, prob in enumerate(probabilities):
                if model_type == 'chest':
                    # For multi-label, only include predictions above threshold
                    if prob > 0.3:  # Threshold for chest X-ray
                        results.append({
                            'disease': classes[i],
                            'confidence': float(prob)
                        })
                else:
                    results.append({
                        'disease': classes[i],
                        'confidence': float(prob)
                    })
            
            # Sort by confidence and return top 3 for single-label
            if model_type != 'chest':
                results = sorted(results, key=lambda x: x['confidence'], reverse=True)[:3]
            else:
                # For chest X-ray, sort by confidence
                results = sorted(results, key=lambda x: x['confidence'], reverse=True)
            
            return results
    
    def get_available_models(self) -> List[str]:
        """Get list of available model types"""
        return list(self.models.keys())

# Global instance
medical_ai_service = MedicalAIService()