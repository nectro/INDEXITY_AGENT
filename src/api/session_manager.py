"""
Session manager for handling conversation memory across API calls
"""

import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage


class SessionManager:
    """Manages conversation sessions for different users"""
    
    def __init__(self, session_timeout_hours: int = 24):
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout_hours = session_timeout_hours
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """Get existing session or create a new one"""
        if session_id and session_id in self.sessions:
            # Check if session is still valid
            if self._is_session_valid(session_id):
                return session_id
            else:
                # Remove expired session
                self.remove_session(session_id)
        
        # Create new session
        new_session_id = session_id or str(uuid.uuid4())
        self.sessions[new_session_id] = {
            'memory': ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            ),
            'created_at': datetime.now(),
            'last_accessed': datetime.now(),
            'suggested_tasks': []  # Store suggested tasks for meeting analysis
        }
        return new_session_id
    
    def get_session_memory(self, session_id: str) -> Optional[ConversationBufferMemory]:
        """Get conversation memory for a session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session['last_accessed'] = datetime.now()
            return session['memory']
        return None
    
    def get_suggested_tasks(self, session_id: str) -> list:
        """Get suggested tasks for a session"""
        if session_id in self.sessions:
            return self.sessions[session_id].get('suggested_tasks', [])
        return []
    
    def set_suggested_tasks(self, session_id: str, tasks: list):
        """Set suggested tasks for a session"""
        if session_id in self.sessions:
            self.sessions[session_id]['suggested_tasks'] = tasks
    
    def clear_suggested_tasks(self, session_id: str):
        """Clear suggested tasks for a session"""
        if session_id in self.sessions:
            self.sessions[session_id]['suggested_tasks'] = []
    
    def remove_session(self, session_id: str):
        """Remove a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def _is_session_valid(self, session_id: str) -> bool:
        """Check if a session is still valid (not expired)"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        last_accessed = session['last_accessed']
        timeout_threshold = datetime.now() - timedelta(hours=self.session_timeout_hours)
        
        return last_accessed > timeout_threshold
    
    def cleanup_expired_sessions(self):
        """Remove all expired sessions"""
        expired_sessions = []
        for session_id in self.sessions:
            if not self._is_session_valid(session_id):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.remove_session(session_id)
        
        return len(expired_sessions)
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get information about a session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            memory = session['memory']
            return {
                'session_id': session_id,
                'created_at': session['created_at'],
                'last_accessed': session['last_accessed'],
                'message_count': len(memory.chat_memory.messages) if memory.chat_memory else 0,
                'suggested_tasks_count': len(session.get('suggested_tasks', []))
            }
        return None
    
    def get_all_sessions_info(self) -> list:
        """Get information about all active sessions"""
        sessions_info = []
        for session_id in self.sessions:
            info = self.get_session_info(session_id)
            if info:
                sessions_info.append(info)
        return sessions_info


# Global session manager instance
session_manager = SessionManager() 