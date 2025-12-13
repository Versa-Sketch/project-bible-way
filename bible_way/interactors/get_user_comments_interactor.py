from bible_way.storage import UserDB
from bible_way.presenters.get_user_comments_response import GetUserCommentsResponse
from rest_framework.response import Response


class GetUserCommentsInteractor:
    def __init__(self, storage: UserDB, response: GetUserCommentsResponse):
        self.storage = storage
        self.response = response

    def get_user_comments_interactor(self, user_id: str) -> Response:
        try:
            comments_data = self.storage.get_user_comments(user_id=user_id)
            
            return self.response.user_comments_retrieved_successfully_response(
                comments_data=comments_data
            )
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve user comments: {str(e)}")

