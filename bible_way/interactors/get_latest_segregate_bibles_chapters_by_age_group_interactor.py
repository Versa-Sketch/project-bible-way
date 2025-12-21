from bible_way.storage import UserDB
from bible_way.presenters.get_latest_segregate_bibles_chapters_by_age_group_response import GetLatestSegregateBiblesChaptersByAgeGroupResponse
from rest_framework.response import Response


class GetLatestSegregateBiblesChaptersByAgeGroupInteractor:
    def __init__(self, storage: UserDB, response: GetLatestSegregateBiblesChaptersByAgeGroupResponse):
        self.storage = storage
        self.response = response

    def get_latest_segregate_bibles_chapters_by_age_group_interactor(self) -> Response:
        try:
            # Get latest chapter books for each age group
            age_groups_data = self.storage.get_latest_chapter_books_by_age_group_in_segregate_bibles()
            
            return self.response.success_response(age_groups_data)
        except Exception as e:
            return self.response.error_response(f"Failed to get latest chapters by age group: {str(e)}")

