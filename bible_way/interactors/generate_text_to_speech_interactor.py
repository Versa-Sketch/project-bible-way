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
        chapter_id: str,
        book_id: str,
        blocks: list,
        language_code: str
    ) -> Response:
        # Validate required fields
        if not chapter_id or (isinstance(chapter_id, str) and not chapter_id.strip()):
            return self.response.validation_error_response("chapter_id is required")
        
        if not book_id or (isinstance(book_id, str) and not book_id.strip()):
            return self.response.validation_error_response("book_id is required")
        
        if not blocks or not isinstance(blocks, list) or len(blocks) == 0:
            return self.response.validation_error_response("blocks array is required and cannot be empty")
        
        if not language_code or (isinstance(language_code, str) and not language_code.strip()):
            return self.response.validation_error_response("language_code is required")
        
        # Validate language code format (basic validation: should match pattern like "en-US", "es-ES", etc.)
        language_code = language_code.strip()
        if not re.match(r'^[a-z]{2}-[A-Z]{2}$', language_code):
            return self.response.validation_error_response("language_code must be in format 'xx-XX' (e.g., 'en-US', 'es-ES')")
        
        # Validate blocks structure
        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                return self.response.validation_error_response(f"Block at index {i} must be an object")
            
            if "block_id" not in block or not block.get("block_id"):
                return self.response.validation_error_response(f"Block at index {i} must have a 'block_id' field")
            
            if "text" not in block:
                return self.response.validation_error_response(f"Block at index {i} must have a 'text' field")
            
            if not isinstance(block.get("text"), str):
                return self.response.validation_error_response(f"Block at index {i} 'text' field must be a string")
        
        try:
            blocks_data = []
            total_duration = 0.0
            
            # Process each block individually
            for block in blocks:
                block_id = block.get("block_id")
                block_text = block.get("text", "")
                
                # Check if block text exceeds the byte limit
                text_bytes = len(block_text.encode('utf-8'))
                if text_bytes > MAX_BYTES_PER_CHUNK:
                    return self.response.validation_error_response(
                        f"Block '{block_id}' text exceeds the maximum allowed size ({MAX_BYTES_PER_CHUNK} bytes). "
                        f"Current size: {text_bytes} bytes. Please split this block into smaller parts."
                    )
                
                try:
                    # Synthesize speech for this block
                    audio_bytes, duration = synthesize_text_to_speech(
                        text=block_text,
                        language_code=language_code
                    )
                    
                    # Create data URL for the audio
                    audio_url = create_audio_data_url(audio_bytes, mime_type="audio/mp3")
                    
                    # Build block data
                    block_data = {
                        "block_id": block_id,
                        "audio_url": audio_url,
                        "duration": round(duration, 2)
                    }
                    
                    blocks_data.append(block_data)
                    total_duration += duration
                    
                except Exception as e:
                    # If one block fails, return error
                    return self.response.error_response(
                        f"Failed to generate audio for block '{block_id}': {str(e)}"
                    )
            
            # Return successful response
            return self.response.audio_generated_successfully_response(
                blocks_data=blocks_data,
                total_blocks=len(blocks_data),
                total_duration=round(total_duration, 2),
                audio_format="mp3"
            )
            
        except Exception as e:
            return self.response.error_response(f"Failed to generate text-to-speech: {str(e)}")

