"""Text-to-speech generation for listening exercises."""
import os
from pathlib import Path
from typing import Optional
from gtts import gTTS

from config import config


class TTSGenerator:
    """Generate audio files from text using Google Text-to-Speech (gTTS)."""
    
    def __init__(self, audio_dir: str = "audio"):
        """Initialize TTS generator.
        
        Args:
            audio_dir: Directory to save audio files
        """
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(exist_ok=True)
        
        self.language = config.tts_language
        self.speed = config.tts_speed
    
    def generate_audio(self, text: str, filename: Optional[str] = None) -> str:
        """Generate audio file from text.
        
        Args:
            text: Text to convert to speech
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to generated audio file
        """
        if filename is None:
            # Generate filename from timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"toeic_{timestamp}"
        
        # Ensure .mp3 extension
        if not filename.endswith(".mp3"):
            filename = f"{filename}.mp3"
        
        filepath = self.audio_dir / filename
        
        # Generate speech using gTTS
        tts = gTTS(
            text=text,
            lang=self.language,
            slow=(self.speed < 1.0)  # gTTS uses 'slow' boolean instead of speed float
        )
        
        # Save to file
        tts.save(str(filepath))
        
        return str(filepath)
    
    def generate_conversation_audio(self, speakers: list[dict], filename: Optional[str] = None) -> str:
        """Generate audio for a multi-speaker conversation.
        
        For more natural conversations, you might want to use different voices
        or add pauses between speakers.
        
        Args:
            speakers: List of dicts with 'speaker' and 'text' keys
            filename: Optional custom filename
            
        Returns:
            Path to generated audio file
        """
        # Combine all speaker text with slight formatting
        full_text = ""
        for item in speakers:
            speaker = item.get('speaker', 'Speaker')
            text = item.get('text', '')
            full_text += f"{text} ... "  # Add pause between speakers
        
        return self.generate_audio(full_text.strip(), filename)
