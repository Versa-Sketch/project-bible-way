from bible_way.storage import UserDB
from bible_way.presenters.get_age_groups_response import GetAgeGroupsResponse
from rest_framework.response import Response


class GetAgeGroupsInteractor:
    def __init__(self, storage: UserDB, response: GetAgeGroupsResponse):
        self.storage = storage
        self.response = response

    def get_age_groups_interactor(self) -> Response:
        try:
            age_groups = self.storage.get_all_age_groups()
            
            age_groups_data = []
            for age_group in age_groups:
                age_groups_data.append({
                    "age_group_id": str(age_group.age_group_id),
                    "age_group_name": age_group.age_group_name,
                    "display_name": age_group.get_age_group_name_display(),
                    "cover_image_url": age_group.cover_image_url,
                    "description": age_group.description,
                    "display_order": age_group.display_order,
                    "created_at": age_group.age_group_created_at.isoformat() if age_group.age_group_created_at else None,
                    "updated_at": age_group.age_group_updated_at.isoformat() if age_group.age_group_updated_at else None
                })
            
            return self.response.age_groups_retrieved_successfully_response(age_groups_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve age groups: {str(e)}")

