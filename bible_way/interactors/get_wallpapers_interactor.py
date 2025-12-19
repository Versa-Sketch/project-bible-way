from bible_way.storage import UserDB
from bible_way.presenters.get_wallpapers_response import GetWallpapersResponse
from rest_framework.response import Response


class GetWallpapersInteractor:
    def __init__(self, storage: UserDB, response: GetWallpapersResponse):
        self.storage = storage
        self.response = response

    def get_all_wallpapers_interactor(self) -> Response:
        try:
            wallpapers_data = self.storage.get_all_wallpapers()
            
            return self.response.wallpapers_retrieved_successfully_response(
                wallpapers_data=wallpapers_data
            )
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve wallpapers: {str(e)}")

