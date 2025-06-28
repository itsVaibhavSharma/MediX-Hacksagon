# backend/app/services/gemini_service.py
import google.generativeai as genai
import os
from typing import List, Dict, Optional
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class GeminiMedicalService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.chat_sessions = {}  # Store active chat sessions
        
        # Medical context prompts
        self.base_medical_prompt = """
        You are MediX AI, a professional medical assistant integrated into a healthcare platform. 
        You provide helpful medical information and guidance while emphasizing the importance of professional medical consultation.
        
        Guidelines:
        1. Always provide evidence-based medical information
        2. Encourage users to consult healthcare professionals for diagnosis and treatment
        3. Be empathetic and understanding
        4. Ask relevant follow-up questions to better understand symptoms
        5. Provide helpful lifestyle and wellness advice when appropriate
        6. Never provide specific drug dosages or prescriptions
        7. Always mention when emergency medical attention might be needed
        
        Remember: You are assisting, not replacing, professional medical care.
        """
    
    def analyze_with_symptoms(self, predictions: List[Dict], symptoms: str, user_context: Optional[Dict] = None) -> Dict[str, str]:
        """Analyze AI model predictions along with user symptoms to provide final diagnosis"""
        
        context = f"""
        Based on AI image analysis, here are the top predictions:
        """
        
        for i, pred in enumerate(predictions, 1):
            context += f"\n{i}. {pred['disease']}: {pred['confidence']:.2%} confidence"
        
        context += f"\n\nPatient reported symptoms: {symptoms}"
        
        if user_context:
            context += f"\nPatient context: Age: {user_context.get('age', 'N/A')}, Gender: {user_context.get('gender', 'N/A')}"
        
        prompt = f"""
        {self.base_medical_prompt}
        
        {context}
        
        Please analyze the AI predictions along with the reported symptoms and provide:
        1. The most likely diagnosis from the AI predictions based on symptoms
        2. Additional questions to ask the patient to clarify the diagnosis
        3. General recommendations and next steps
        4. When to seek immediate medical attention
        
        Format your response as JSON with keys: 'likely_diagnosis', 'follow_up_questions', 'recommendations', 'emergency_signs'
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Try to parse as JSON, fallback to structured text
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback parsing
                result = {
                    'likely_diagnosis': predictions[0]['disease'] if predictions else 'Unable to determine',
                    'follow_up_questions': 'Please consult with a healthcare professional for proper evaluation.',
                    'recommendations': response.text,
                    'emergency_signs': 'Seek immediate medical attention if symptoms worsen rapidly.'
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Gemini symptom analysis: {str(e)}")
            return {
                'likely_diagnosis': predictions[0]['disease'] if predictions else 'Analysis unavailable',
                'follow_up_questions': 'Unable to generate follow-up questions at this time.',
                'recommendations': 'Please consult with a healthcare professional.',
                'emergency_signs': 'Seek immediate medical attention if you have severe symptoms.'
            }
    
    def start_medical_chat(self, session_id: str, initial_message: str, user_context: Optional[Dict] = None) -> str:
        """Start a new medical chat session"""
        
        context_info = ""
        if user_context:
            context_info = f"Patient context: Age: {user_context.get('age', 'N/A')}, Gender: {user_context.get('gender', 'N/A')}, City: {user_context.get('city', 'N/A')}"
        
        system_prompt = f"""
        {self.base_medical_prompt}
        
        {context_info}
        
        The patient is starting a medical consultation. Please:
        1. Greet them warmly and professionally
        2. Ask relevant questions about their symptoms
        3. Provide helpful medical guidance
        4. Remember this conversation context for follow-up messages
        """
        
        try:
            # Start new chat session
            chat = self.model.start_chat(history=[])
            
            full_prompt = f"{system_prompt}\n\nPatient message: {initial_message}"
            response = chat.send_message(full_prompt)
            
            # Store chat session
            self.chat_sessions[session_id] = {
                'chat': chat,
                'context': user_context,
                'started_at': datetime.now()
            }
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error starting medical chat: {str(e)}")
            return "I'm sorry, I'm having trouble connecting right now. Please try again or consult with a healthcare professional."
    
    def continue_medical_chat(self, session_id: str, message: str, chat_history: Optional[List[Dict]] = None) -> str:
        """Continue an existing medical chat session"""
        
        try:
            if session_id in self.chat_sessions:
                # Use existing chat session
                chat_session = self.chat_sessions[session_id]
                chat = chat_session['chat']
                
                # Add context about previous conversation
                contextual_message = f"""
                Previous conversation context available.
                Patient's current message: {message}
                
                Please continue the medical consultation, referring to previous discussion points when relevant.
                """
                
                response = chat.send_message(contextual_message)
                return response.text
                
            else:
                # Create new session if not found, using chat history for context
                chat = self.model.start_chat(history=[])
                
                # Build context from chat history
                context = "Previous conversation:\n"
                if chat_history:
                    for msg in chat_history[-5:]:  # Last 5 messages for context
                        role = "Patient" if msg.get('message_type') == 'user' else "MediX AI"
                        context += f"{role}: {msg.get('message_content', '')}\n"
                
                context += f"\nCurrent message: {message}"
                
                full_prompt = f"""
                {self.base_medical_prompt}
                
                {context}
                
                Please continue the medical consultation based on the conversation history above.
                """
                
                response = chat.send_message(full_prompt)
                
                # Store new session
                self.chat_sessions[session_id] = {
                    'chat': chat,
                    'context': None,
                    'started_at': datetime.now()
                }
                
                return response.text
                
        except Exception as e:
            logger.error(f"Error in medical chat continuation: {str(e)}")
            return "I'm experiencing technical difficulties. Please try again or consult with a healthcare professional if you have urgent concerns."
    
    def get_disease_information(self, disease_name: str, detail_level: str = "comprehensive") -> str:
        """Get detailed information about a specific disease"""
        
        prompt = f"""
        {self.base_medical_prompt}
        
        Please provide {detail_level} information about: {disease_name}
        
        Include:
        1. Overview of the condition
        2. Common symptoms
        3. Potential causes
        4. General prevention measures
        5. When to seek medical attention
        6. General treatment approaches (emphasize need for professional consultation)
        
        Keep the language accessible but medically accurate.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error getting disease information: {str(e)}")
            return f"I'm unable to provide detailed information about {disease_name} right now. Please consult with a healthcare professional for accurate medical information."
    
    def get_emergency_assessment(self, symptoms: str) -> Dict[str, any]:
        """Assess if symptoms require emergency attention"""
        
        prompt = f"""
        {self.base_medical_prompt}
        
        Please assess these symptoms for emergency urgency: {symptoms}
        
        Provide assessment as JSON with:
        - 'urgency_level': 'emergency', 'urgent', 'routine', or 'self_care'
        - 'reasoning': explanation of assessment
        - 'immediate_actions': what to do right now
        - 'timeline': when to seek care
        
        Be conservative - when in doubt, recommend seeking medical attention.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError:
                # Conservative fallback
                result = {
                    'urgency_level': 'urgent',
                    'reasoning': 'Unable to properly assess - recommend medical evaluation',
                    'immediate_actions': 'Contact healthcare provider or emergency services if concerned',
                    'timeline': 'Seek medical attention promptly'
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in emergency assessment: {str(e)}")
            return {
                'urgency_level': 'urgent',
                'reasoning': 'Technical error in assessment',
                'immediate_actions': 'Contact healthcare provider or emergency services if you have serious concerns',
                'timeline': 'Seek medical attention if symptoms persist or worsen'
            }
    
    def cleanup_old_sessions(self, hours: int = 24):
        """Clean up old chat sessions to prevent memory issues"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        sessions_to_remove = []
        for session_id, session_data in self.chat_sessions.items():
            if session_data['started_at'] < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.chat_sessions[session_id]
        
        logger.info(f"Cleaned up {len(sessions_to_remove)} old chat sessions")

# Global instance
gemini_service = GeminiMedicalService()