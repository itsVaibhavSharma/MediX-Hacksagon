
# backend/app/services/ai_models.py - FIXED VERSION
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
import os

logger = logging.getLogger(__name__)

# Updated model architectures with fixed torchvision warnings
class NailDiseaseClassifier(nn.Module):
    def __init__(self, num_classes=6):
        super(NailDiseaseClassifier, self).__init__()
        # Fix deprecation warning
        self.backbone = models.efficientnet_b0(weights=None)
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
    """Updated to match the new EfficientNet-B3 training architecture"""
    def __init__(self, num_classes=22, pretrained=False):
        super(SkinDiseaseClassifier, self).__init__()
        
        # Use EfficientNet-B3 as backbone (matching your training code)
        self.backbone = models.efficientnet_b3(weights=None if not pretrained else 'DEFAULT')
        
        # Get the number of features from the classifier
        num_features = self.backbone.classifier[1].in_features
        
        # Replace the classifier with the exact same architecture from training
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(num_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
        
        # Initialize the new layers (matching training code)
        for module in self.backbone.classifier:
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.constant_(module.bias, 0)
    
    def forward(self, x):
        return self.backbone(x)



class OralDiseaseClassifier(nn.Module):
    def __init__(self, num_classes=6):
        super(OralDiseaseClassifier, self).__init__()
        self.backbone = models.resnet50(weights=None)
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
        self.backbone = models.efficientnet_b3(weights=None)
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
        self.backbone = models.resnet50(weights=None)
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
    def __init__(self, num_classes=14):
        super(ChestXRayClassifier, self).__init__()
        self.backbone = models.mobilenet_v2(weights=None)
        self.features = self.backbone.features
        self.num_classes = num_classes  # Store for dynamic adjustment
        
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
        
        # Updated class names - handle both 13 and 14 class chest models
        self.class_names = {
            'nail': ['Acral Lentiginous Melanoma', 'Healthy Nail', 'Onychogryphosis', 'blue finger', 'clubbing', 'pitting'],
            'skin': ['Acne', 'Eczema', 'Melanoma', 'Psoriasis', 'Basal Cell Carcinoma', 'Dermatitis', 
                    'Vitiligo', 'Rosacea', 'Hives', 'Seborrheic Keratosis', 'Warts', 'Herpes',
                    'Impetigo', 'Cellulitis', 'Ringworm', 'Scabies', 'Age Spots', 'Moles',
                    'Chickenpox', 'Shingles', 'Cold Sores', 'Normal'],
            'oral': ['Caries', 'Calculus', 'Gingivitis', 'Tooth Discoloration', 'Ulcers', 'Hypodontia'],
            'eye': ['Cataract', 'Conjunctivitis', 'Eyelid', 'Normal', 'Uveitis'],
            'bone': ['Not Fractured', 'Fractured'],
            # Support both 13 and 14 class chest models
            'chest_13': ['Atelectasis', 'Cardiomegaly', 'Effusion', 'Infiltration', 'Mass', 'Nodule', 
                        'Pneumonia', 'Pneumothorax', 'Consolidation', 'Edema', 'Emphysema', 
                        'Fibrosis', 'Pleural_Thickening'],
            'chest_14': ['Atelectasis', 'Cardiomegaly', 'Effusion', 'Infiltration', 'Mass', 'Nodule', 
                        'Pneumonia', 'Pneumothorax', 'Consolidation', 'Edema', 'Emphysema', 
                        'Fibrosis', 'Pleural_Thickening', 'Hernia']
        }
        
        # Load models
        self._load_models()
    
    def _load_chest_model_dynamic(self, model_path):
        """Dynamically load chest model with correct number of classes"""
        try:
            # First, peek at the checkpoint to see how many classes it has
            checkpoint = torch.load(model_path, map_location='cpu')
            
            # Handle different checkpoint formats
            if isinstance(checkpoint, dict):
                if 'model_state_dict' in checkpoint:
                    state_dict = checkpoint['model_state_dict']
                elif 'state_dict' in checkpoint:
                    state_dict = checkpoint['state_dict']
                else:
                    state_dict = checkpoint
            else:
                state_dict = checkpoint
            
            # Check the final layer size to determine number of classes
            final_layer_key = None
            for key in state_dict.keys():
                if 'classifier.6.weight' in key or 'fc.weight' in key:
                    final_layer_key = key
                    break
            
            if final_layer_key:
                num_classes = state_dict[final_layer_key].shape[0]
                print(f"Detected chest model with {num_classes} classes")
            else:
                # Default to 14 if we can't determine
                num_classes = 14
                print(f"Could not determine chest model classes, defaulting to {num_classes}")
            
            # Create model with correct number of classes
            model = ChestXRayClassifier(num_classes=num_classes)
            
            # Load the state dict
            model.load_state_dict(state_dict)
            
            # Update class names for this specific model
            if num_classes == 13:
                self.class_names['chest'] = self.class_names['chest_13']
            else:
                self.class_names['chest'] = self.class_names['chest_14']
            
            return model
            
        except Exception as e:
            print(f"Error in dynamic chest model loading: {str(e)}")
            return None
    
    def _load_models(self):
        """Load all trained models with better error handling"""
        model_configs = {
            'nail': {
                'class': NailDiseaseClassifier, 
                'num_classes': 6, 
                'files': ['nail_disease_model.pth', 'nail_disease_classifier_best.pth'],
                'special_loader': None
            },
            'skin': {
                'class': SkinDiseaseClassifier, 
                'num_classes': 22, 
                'files': ['skin_disease_classifier.pth', 'resnet_efficientnet_skin_disease.pth', 'densenet_efficient_skin_disease.pth'],
                'special_loader': None
            },
            'oral': {
                'class': OralDiseaseClassifier, 
                'num_classes': 6, 
                'files': ['oral_disease_model.pth', 'oral_disease_model_final.pth'],
                'special_loader': None
            },
            'eye': {
                'class': EyeDiseaseClassifier, 
                'num_classes': 5, 
                'files': ['eye_disease_model.pth', 'eye_disease_efficientnet_b3.pth'],
                'special_loader': None
            },
            'bone': {
                'class': BoneFractureClassifier, 
                'num_classes': 2, 
                'files': ['bone_fracture_model.pth', 'best_bone_fracture_model.pth'],
                'special_loader': None
            },
            'chest': {
                'class': ChestXRayClassifier, 
                'num_classes': 14,  # Default, will be adjusted dynamically
                'files': ['chest_xray_model.pth', 'chest_xray_pytorch_model.pth'],
                'special_loader': self._load_chest_model_dynamic
            }
        }
        
        for model_type, config in model_configs.items():
            model_loaded = False
            
            for model_file in config['files']:
                model_path = f"models/{model_file}"
                
                if os.path.exists(model_path):
                    try:
                        # Use special loader if available (for chest model)
                        if config['special_loader']:
                            model = config['special_loader'](model_path)
                            if model is None:
                                continue
                        else:
                            # Standard loading for other models
                            model = config['class'](config['num_classes'])
                            
                            # Try to load the model
                            checkpoint = torch.load(model_path, map_location=self.device)
                            
                            # Handle different checkpoint formats
                            if isinstance(checkpoint, dict):
                                if 'model_state_dict' in checkpoint:
                                    model.load_state_dict(checkpoint['model_state_dict'])
                                elif 'state_dict' in checkpoint:
                                    model.load_state_dict(checkpoint['state_dict'])
                                else:
                                    # Try to load the whole dict as state_dict
                                    model.load_state_dict(checkpoint)
                            else:
                                model.load_state_dict(checkpoint)
                        
                        model.to(self.device)
                        model.eval()
                        self.models[model_type] = model
                        logger.info(f"✅ Loaded {model_type} model from {model_file}")
                        model_loaded = True
                        break
                        
                    except Exception as e:
                        logger.warning(f"Failed to load {model_type} from {model_file}: {str(e)}")
                        continue
            
            if not model_loaded:
                logger.error(f"❌ Could not load {model_type} model from any file: {config['files']}")
                print(f"⚠️  Skipping {model_type} model - no valid model file found")
    
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
            # Handle data URL format
            if 'data:image' in image_base64:
                image_data = base64.b64decode(image_base64.split(',')[1])
            else:
                image_data = base64.b64decode(image_base64)
            
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
            available_models = list(self.models.keys())
            raise ValueError(f"Model type '{model_type}' not available. Available models: {available_models}")
        
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
                # For chest X-ray, sort by confidence and return all above threshold
                results = sorted(results, key=lambda x: x['confidence'], reverse=True)
                if not results:  # If no predictions above threshold, return top 3
                    all_results = []
                    for i, prob in enumerate(probabilities):
                        all_results.append({
                            'disease': classes[i],
                            'confidence': float(prob)
                        })
                    results = sorted(all_results, key=lambda x: x['confidence'], reverse=True)[:3]
            
            return results
    
    def get_available_models(self) -> List[str]:
        """Get list of available model types"""
        return list(self.models.keys())
    
    def get_model_info(self) -> Dict[str, Dict]:
        """Get detailed information about loaded models"""
        info = {}
        for model_type, model in self.models.items():
            info[model_type] = {
                'loaded': True,
                'device': str(self.device),
                'num_classes': len(self.class_names[model_type]),
                'classes': self.class_names[model_type],
                'architecture': model.__class__.__name__
            }
        return info

# Global instance
medical_ai_service = MedicalAIService()