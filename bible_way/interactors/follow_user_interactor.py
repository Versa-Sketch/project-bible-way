from bible_way.storage import UserDB
from bible_way.presenters.follow_user_response import FollowUserResponse
from rest_framework.response import Response


class FollowUserInteractor:
    def __init__(self, storage: UserDB, response: FollowUserResponse):
        self.storage = storage
        self.response = response

    def follow_user_interactor(self, follower_id: str, followed_id: str) -> Response:
        if follower_id == followed_id:
            return self.response.cannot_follow_yourself_response()
        
        followed_user = self.storage.get_user_by_user_id(followed_id)
        if not followed_user:
            return self.response.user_not_found_response()
        
        if self.storage.check_follow_exists(follower_id, followed_id):
            return self.response.already_following_response()
        
        self.storage.follow_user(follower_id, followed_id)
        
        # Create or get conversation between follower and followed user
        from project_chat.storage import ChatDB
        chat_db = ChatDB()
        conversation = chat_db.get_or_create_direct_conversation(follower_id, followed_id)
        
        conversation_id = str(conversation.id) if conversation else None
        
        return self.response.follow_success_response(conversation_id=conversation_id)

