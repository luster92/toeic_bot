"""Configuration management for TOEIC Bot."""
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class BotConfig(BaseModel):
    """Bot configuration settings."""
    
    # Telegram
    telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN_TOEIC", "")
    
    # Gemini AI
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Scheduling
    daily_delivery_time: str = os.getenv("DAILY_DELIVERY_TIME", "07:00")
    timezone: str = os.getenv("TIMEZONE", "Asia/Seoul")
    
    # Content settings
    listening_questions_per_day: int = int(os.getenv("LISTENING_QUESTIONS_PER_DAY", "3"))
    grammar_questions_per_day: int = int(os.getenv("GRAMMAR_QUESTIONS_PER_DAY", "5"))
    weekend_delivery: bool = os.getenv("WEEKEND_DELIVERY", "false").lower() == "true"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///toeic_bot.db")
    
    # TTS (using gTTS - Google Text-to-Speech)
    tts_language: str = os.getenv("TTS_LANGUAGE", "en")
    tts_speed: float = float(os.getenv("TTS_SPEED", "1.0"))
    
    # Target score
    default_target_score: int = 800
    
    class Config:
        """Pydantic config."""
        validate_assignment = True


# Global config instance
config = BotConfig()
