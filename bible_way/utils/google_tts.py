from google.cloud import texttospeech
import os
import base64
import io
try:
    from mutagen.mp3 import MP3
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

# Path to your Google Cloud service account JSON key file
KEY_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "serviceAccountKey.json")

# Maximum bytes per TTS API request (5000 bytes limit, using 4500 for safety)
MAX_BYTES_PER_CHUNK = 4500


def get_tts_client():
    """Initialize and return a Text-to-Speech client."""
    if os.path.exists(KEY_PATH):
        return texttospeech.TextToSpeechClient.from_service_account_file(KEY_PATH)
    else:
        # Try using default credentials (from environment or metadata service)
        return texttospeech.TextToSpeechClient()


def synthesize_text_to_speech(text: str, language_code: str = "en-US") -> tuple[bytes, float]:
    """
    Synthesize text to speech using Google Cloud TTS API.
    
    Args:
        text: The text to convert to speech
        language_code: Language code (e.g., "en-US", "es-ES", "ja-JP")
    
    Returns:
        tuple: (audio_bytes, duration_seconds)
    """
    client = get_tts_client()
    
    # Set the text input to be synthesized
    input_text = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code and gender
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=input_text,
        voice=voice,
        audio_config=audio_config
    )

    audio_bytes = response.audio_content
    
    # Calculate duration
    duration = calculate_audio_duration(audio_bytes)
    
    return audio_bytes, duration


def calculate_audio_duration(audio_bytes: bytes) -> float:
    """
    Calculate the duration of MP3 audio in seconds.
    
    Args:
        audio_bytes: Binary MP3 audio data
    
    Returns:
        float: Duration in seconds
    """
    if MUTAGEN_AVAILABLE:
        try:
            audio_file = MP3(io.BytesIO(audio_bytes))
            return float(audio_file.info.length)
        except Exception:
            # Fallback to estimation if mutagen fails
            pass
    
    # Fallback: Estimate duration based on average speaking rate
    # Average speaking rate: ~150 words per minute = 2.5 words per second
    # Estimate: ~5 characters per word, so ~12.5 characters per second
    # This is a rough estimate
    estimated_chars = len(audio_bytes) // 100  # Rough character count estimate
    estimated_duration = estimated_chars / 12.5  # seconds
    return round(estimated_duration, 2)


def chunk_blocks(blocks: list, max_bytes: int = MAX_BYTES_PER_CHUNK) -> list[dict]:
    """
    Group blocks into chunks based on byte limit (not character limit).
    
    Args:
        blocks: List of dicts with 'block_id' and 'text' keys
        max_bytes: Maximum bytes per chunk (default: 4500)
    
    Returns:
        list: List of chunk dictionaries with block_ids, text, and byte_count
    """
    chunks = []
    current_chunk = {"block_ids": [], "text": "", "byte_count": 0}
    
    for block in blocks:
        block_text = block.get("text", "")
        block_id = block.get("block_id", "")
        text_bytes = len(block_text.encode('utf-8'))  # Get byte length, not char length
        
        # Check if adding this block would exceed limit
        separator_bytes = 1 if current_chunk["text"] else 0  # Space separator
        total_bytes_with_block = current_chunk["byte_count"] + separator_bytes + text_bytes
        
        if total_bytes_with_block > max_bytes and current_chunk["block_ids"]:
            # Save current chunk and start new one
            chunks.append(current_chunk)
            current_chunk = {
                "block_ids": [block_id],
                "text": block_text,
                "byte_count": text_bytes
            }
        else:
            # Add to current chunk
            separator = " " if current_chunk["text"] else ""
            current_chunk["block_ids"].append(block_id)
            current_chunk["text"] += separator + block_text
            # Recalculate byte_count for the updated text
            current_chunk["byte_count"] = len(current_chunk["text"].encode('utf-8'))
    
    # Add last chunk if it has content
    if current_chunk["block_ids"]:
        chunks.append(current_chunk)
    
    return chunks


def encode_audio_to_base64(audio_bytes: bytes) -> str:
    """
    Encode binary audio data to base64 string.
    
    Args:
        audio_bytes: Binary audio data
    
    Returns:
        str: Base64 encoded string
    """
    return base64.b64encode(audio_bytes).decode('utf-8')


def run_quickstart():
    # Instantiates a client using the service account file
    client = get_tts_client()

    # Set the text input to be synthesized
    input_text = texttospeech.SynthesisInput(text="Hello everyone, welcome to Bible Way App built by Biblia World  where you can read the Bible in your preferred language and get the audio version of the Bible.")

    # Build the voice request, select the language code and gender
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=input_text, 
        voice=voice, 
        audio_config=audio_config
    )

    # The response's audio_content is binary
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')