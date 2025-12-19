from bible_way.storage import UserDB
from bible_way.presenters.admin.approve_testimonial_response import AdminApproveTestimonialResponse
from rest_framework.response import Response


class AdminApproveTestimonialInteractor:
    def __init__(self, storage: UserDB, response: AdminApproveTestimonialResponse):
        self.storage = storage
        self.response = response

    def approve_testimonial_interactor(self, testimonial_id: str) -> Response:
        if not testimonial_id:
            return self.response.validation_error_response("Testimonial ID is required")
        
        try:
            self.storage.approve_testimonial(testimonial_id=testimonial_id)
            return self.response.testimonial_approved_successfully_response()
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.testimonial_not_found_response()
            return self.response.error_response(f"Failed to approve testimonial: {error_message}")

