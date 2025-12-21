from bible_way.presenters.generate_text_to_speech_response import GenerateTextToSpeechResponse
from bible_way.utils.google_tts import (
    synthesize_text_to_speech,
    chunk_blocks,
    encode_audio_to_base64
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
            # Chunk blocks into groups that fit within API limits
            chunked_blocks = chunk_blocks(blocks)
            
            if not chunked_blocks:
                return self.response.validation_error_response("No valid blocks to process")
            
            chunks_data = []
            total_duration = 0.0
            
            # Process each chunk
            for chunk_index, chunk in enumerate(chunked_blocks):
                try:
                    # Synthesize speech for this chunk
                    audio_bytes, duration = synthesize_text_to_speech(
                        text=chunk["text"],
                        language_code=language_code
                    )
                    
                    # Encode audio to base64
                    audio_base64 = encode_audio_to_base64(audio_bytes)
                    
                    # Build chunk data
                    chunk_data = {
                        "chunk_index": chunk_index,
                        "block_ids": chunk["block_ids"],
                        "audio_data": audio_base64,
                        "duration": round(duration, 2)
                    }
                    
                    chunks_data.append(chunk_data)
                    total_duration += duration
                    
                except Exception as e:
                    # If one chunk fails, continue with others but log the error
                    return self.response.error_response(
                        f"Failed to generate audio for chunk {chunk_index}: {str(e)}"
                    )
            
            # Return successful response
            return self.response.audio_generated_successfully_response(
                chunks_data=chunks_data,
                total_chunks=len(chunks_data),
                total_duration=round(total_duration, 2),
                audio_format="mp3"
            )
            
        except Exception as e:
            return self.response.error_response(f"Failed to generate text-to-speech: {str(e)}")

