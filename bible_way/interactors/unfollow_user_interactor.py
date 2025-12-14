from bible_way.storage import UserDB
from bible_way.presenters.unfollow_user_response import UnfollowUserResponse
from rest_framework.response import Response


class UnfollowUserInteractor:
    def __init__(self, storage: UserDB, response: UnfollowUserResponse):
        self.storage = storage
        self.response = response

    def unfollow_user_interactor(self, follower_id: str, followed_id: str) -> Response:
        if follower_id == followed_id:
            return self.response.cannot_unfollow_yourself_response()
        
        followed_user = self.storage.get_user_by_user_id(followed_id)
        if not followed_user:
            return self.response.user_not_found_response()
        
        if not self.storage.check_follow_exists(follower_id, followed_id):
            return self.response.not_following_response()
        
        # Find and deactivate conversation before unfollowing
        from project_chat.storage import ChatDB
        chat_db = ChatDB()
        conversation = chat_db.find_conversation_between_users(follower_id, followed_id)
        
        conversation_id = None
        if conversation:
            chat_db.deactivate_conversation(conversation.id)
            conversation_id = str(conversation.id)
        
        self.storage.unfollow_user(follower_id, followed_id)
        
        return self.response.unfollow_success_response(conversation_id=conversation_id)

