"""
Interactor for getting user inbox (all conversations).
"""

from typing import Dict, Any
from project_chat.storage import ChatDB
from project_chat.presenters.inbox_response import InboxResponse


class GetInboxInteractor:
    """Interactor for getting user inbox."""
    
    def __init__(self, storage: ChatDB, response: InboxResponse):
        self.storage = storage
        self.response = response
    
    def get_inbox_interactor(self, user_id: str) -> Dict[str, Any]:
        """
        Get all conversations for a user (inbox).
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary response with list of conversations
        """
        try:
            conversations = self.storage.get_user_conversations(user_id)
            return self.response.inbox_success_response(conversations)
        except Exception as e:
            import traceback
            print(f"Error in get_inbox_interactor: {e}")
            print(traceback.format_exc())
            return self.response.error_response(f"Failed to retrieve inbox: {str(e)}")

