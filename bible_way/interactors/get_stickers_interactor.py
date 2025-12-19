from bible_way.storage import UserDB
from bible_way.presenters.get_stickers_response import GetStickersResponse
from rest_framework.response import Response


class GetStickersInteractor:
    def __init__(self, storage: UserDB, response: GetStickersResponse):
        self.storage = storage
        self.response = response

    def get_all_stickers_interactor(self) -> Response:
        try:
            stickers_data = self.storage.get_all_stickers()
            
            return self.response.stickers_retrieved_successfully_response(
                stickers_data=stickers_data
            )
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve stickers: {str(e)}")

