from bible_way.storage import UserDB
from bible_way.presenters.get_categories_response import GetCategoriesResponse
from rest_framework.response import Response


class GetCategoriesInteractor:
    def __init__(self, storage: UserDB, response: GetCategoriesResponse):
        self.storage = storage
        self.response = response

    def get_categories_interactor(self) -> Response:
        try:
            categories = self.storage.get_all_categories()
            
            categories_data = []
            for category in categories:
                categories_data.append({
                    "category_id": str(category.category_id),
                    "category_name": category.category_name,
                    "display_name": category.get_category_name_display(),
                    "cover_image_url": category.cover_image_url,
                    "description": category.description,
                    "display_order": category.display_order,
                    "created_at": category.created_at.isoformat() if category.created_at else None,
                    "updated_at": category.updated_at.isoformat() if category.updated_at else None
                })
            
            return self.response.categories_retrieved_successfully_response(categories_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve categories: {str(e)}")

