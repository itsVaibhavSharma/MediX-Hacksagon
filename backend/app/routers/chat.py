# backend/app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from typing import List

from app.models.database import User, ChatSession
from app.models.schemas import ChatMessage, ChatResponse
from app.utils.database import get_db
from app.utils.auth import get_current_user
from app.services.gemini_service import gemini_service

router = APIRouter()

@router.post("/start", response_model=ChatResponse)
async def start_chat(
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new medical chat session"""
    
    try:
        # Generate session ID if not provided
        session_id = message.session_id or str(uuid.uuid4())
        
        # Prepare user context
        user_context = {
            'age': current_user.age,
            'gender': current_user.gender,
            'city': current_user.city,
            'user_type': current_user.user_type
        }
        
        # Start chat with Gemini
        response_text = gemini_service.start_medical_chat(
            session_id, 
            message.message, 
            user_context
        )
        
        # Save messages to database
        # Save user message
        user_msg = ChatSession(
            user_id=current_user.id,
            session_id=session_id,
            message_type="user",
            message_content=message.message,
            context_type=message.context_type
        )
        db.add(user_msg)
        
        # Save assistant response
        assistant_msg = ChatSession(
            user_id=current_user.id,
            session_id=session_id,
            message_type="assistant",
            message_content=response_text,
            context_type=message.context_type
        )
        db.add(assistant_msg)
        
        db.commit()
        
        return ChatResponse(response=response_text, session_id=session_id)
        
    except Exception as e:
        print(f"Chat start error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error starting chat session"
        )

@router.post("/continue", response_model=ChatResponse)
async def continue_chat(
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Continue an existing chat session"""
    
    if not message.session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID is required for continuing chat"
        )
    
    try:
        # Get chat history for context
        chat_history = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.session_id == message.session_id
        ).order_by(ChatSession.timestamp.desc()).limit(10).all()
        
        # Convert to list format for Gemini
        history_list = [
            {
                'message_type': msg.message_type,
                'message_content': msg.message_content
            }
            for msg in reversed(chat_history)  # Reverse to get chronological order
        ]
        
        # Continue chat with Gemini
        response_text = gemini_service.continue_medical_chat(
            message.session_id,
            message.message,
            history_list
        )
        
        # Save messages to database
        # Save user message
        user_msg = ChatSession(
            user_id=current_user.id,
            session_id=message.session_id,
            message_type="user",
            message_content=message.message,
            context_type=message.context_type
        )
        db.add(user_msg)
        
        # Save assistant response
        assistant_msg = ChatSession(
            user_id=current_user.id,
            session_id=message.session_id,
            message_type="assistant",
            message_content=response_text,
            context_type=message.context_type
        )
        db.add(assistant_msg)
        
        db.commit()
        
        return ChatResponse(response=response_text, session_id=message.session_id)
        
    except Exception as e:
        print(f"Chat continue error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error continuing chat session"
        )

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a specific session"""
    
    messages = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.session_id == session_id
    ).order_by(ChatSession.timestamp.asc()).all()
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "type": msg.message_type,
                "content": msg.message_content,
                "timestamp": msg.timestamp
            }
            for msg in messages
        ]
    }

@router.get("/sessions")
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for current user"""
    
    # Get unique session IDs with latest message for each
    sessions = db.query(ChatSession.session_id, 
                       ChatSession.message_content,
                       ChatSession.timestamp).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.timestamp.desc()).all()
    
    # Group by session_id and get the latest message for each
    session_dict = {}
    for session_id, content, timestamp in sessions:
        if session_id not in session_dict:
            session_dict[session_id] = {
                "session_id": session_id,
                "last_message": content,
                "last_activity": timestamp
            }
    
    return {"sessions": list(session_dict.values())}
