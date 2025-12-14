"""
Interactor for getting conversation details by ID.
"""

from typing import Dict, Any
from project_chat.storage import ChatDB
from project_chat.presenters.conversation_response import ConversationResponse
from project_chat.presenters.chat_error_response import ChatErrorResponse


class GetConversationInteractor:
    """Interactor for getting conversation details."""
    
    def __init__(self, storage: ChatDB, response: ConversationResponse, error_response: ChatErrorResponse):
        self.storage = storage
        self.response = response
        self.error_response = error_response
    
    def get_conversation_interactor(self, conversation_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get conversation details by ID.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user requesting (must be a member)
            
        Returns:
            Dictionary response
        """
        try:
            # Validate conversation exists
            conversation = self.storage.get_conversation_by_id(conversation_id)
            if not conversation:
                return self.error_response.conversation_not_found("")
            
            # Check user is a member
            if not self.storage.check_user_membership(user_id, conversation_id):
                return self.error_response.not_member("")
            
            # Get conversation members
            members = self.storage.get_conversation_members(conversation_id)
            
            # Get all messages
            messages = self.storage.get_conversation_messages(
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            # Format response
            return self.response.conversation_details_response(
                conversation=conversation,
                members=members,
                messages=messages
            )
        except Exception as e:
            import traceback
            print(f"Error in get_conversation_interactor: {e}")
            print(traceback.format_exc())
            return self.error_response.server_error("")

