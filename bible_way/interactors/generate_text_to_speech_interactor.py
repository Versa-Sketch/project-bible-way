from bible_way.presenters.generate_text_to_speech_response import GenerateTextToSpeechResponse
from bible_way.utils.google_tts import (
    synthesize_text_to_speech,
    create_audio_data_url,
    MAX_BYTES_PER_CHUNK
)
from rest_framework.response import Response
import re


class GenerateTextToSpeechInteractor:
    def __init__(self, response: GenerateTextToSpeechResponse):
        self.response = response

    def generate_text_to_speech_interactor(
        self,
        text: str,
        language: str
    ) -> Response:
        # Validate required fields
        if not text or (isinstance(text, str) and not text.strip()):
            return self.response.validation_error_response("text is required")
        
        if not language or (isinstance(language, str) and not language.strip()):
            return self.response.validation_error_response("language is required")
        
        # Validate language code format (basic validation: should match pattern like "en-US", "es-ES", etc.)
        language = language.strip()
        if not re.match(r'^[a-z]{2}-[A-Z]{2}$', language):
            return self.response.validation_error_response("language must be in format 'xx-XX' (e.g., 'en-US', 'es-ES')")
        
        # Validate text size
        text = text.strip()
        text_bytes = len(text.encode('utf-8'))
        if text_bytes > MAX_BYTES_PER_CHUNK:
            return self.response.validation_error_response(
                f"Text exceeds the maximum allowed size ({MAX_BYTES_PER_CHUNK} bytes). "
                f"Current size: {text_bytes} bytes. Please provide a shorter text."
            )
        
        try:
            # Synthesize speech for the text
            audio_bytes, duration = synthesize_text_to_speech(
                text=text,
                language_code=language
            )
            
            # Create data URL for the audio
            audio_url = create_audio_data_url(audio_bytes, mime_type="audio/mp3")
            
            # Return successful response with audio and duration
            return self.response.audio_generated_successfully_response(
                audio=audio_url,
                total_duration=round(duration, 2)
            )
            
        except Exception as e:
            return self.response.error_response(f"Failed to generate text-to-speech: {str(e)}")

