from bible_way.storage import UserDB
from bible_way.presenters.admin.get_languages_response import GetLanguagesResponse
from rest_framework.response import Response


class GetLanguagesInteractor:
    def __init__(self, storage: UserDB, response: GetLanguagesResponse):
        self.storage = storage
        self.response = response

    def get_languages_interactor(self) -> Response:
        try:
            languages = self.storage.get_all_languages()
            
            languages_data = []
            for language in languages:
                languages_data.append({
                    "language_id": str(language.language_id),
                    "language_name": language.language_name,
                    "display_name": language.get_language_name_display()
                })
            
            return self.response.languages_retrieved_successfully_response(languages_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve languages: {str(e)}")

