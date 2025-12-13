from bible_way.storage import UserDB
from bible_way.presenters.get_promotions_response import GetPromotionsResponse
from rest_framework.response import Response


class GetPromotionsInteractor:
    def __init__(self, storage: UserDB, response: GetPromotionsResponse):
        self.storage = storage
        self.response = response

    def get_all_promotions_interactor(self) -> Response:
        try:
            promotions_data = self.storage.get_all_promotions()
            
            return self.response.promotions_retrieved_successfully_response(
                promotions_data=promotions_data
            )
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve promotions: {str(e)}")

