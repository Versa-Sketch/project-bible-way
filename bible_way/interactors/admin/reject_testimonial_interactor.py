from bible_way.storage import UserDB
from bible_way.presenters.admin.reject_testimonial_response import AdminRejectTestimonialResponse
from rest_framework.response import Response


class AdminRejectTestimonialInteractor:
    def __init__(self, storage: UserDB, response: AdminRejectTestimonialResponse):
        self.storage = storage
        self.response = response

    def reject_testimonial_interactor(self, testimonial_id: str) -> Response:
        if not testimonial_id:
            return self.response.validation_error_response("Testimonial ID is required")
        
        try:
            self.storage.reject_testimonial(testimonial_id=testimonial_id)
            return self.response.testimonial_rejected_successfully_response()
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.testimonial_not_found_response()
            return self.response.error_response(f"Failed to reject testimonial: {error_message}")

