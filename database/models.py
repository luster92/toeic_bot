"""Database models for TOEIC Bot."""
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class User(Base):
    """User model for tracking learners."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    target_score = Column(Integer, default=800)
    current_estimated_score = Column(Integer, default=600)
    
    # Preferences
    delivery_time = Column(String(5), default="07:00")
    timezone = Column(String(50), default="Asia/Seoul")
    difficulty_level = Column(String(20), default="intermediate")  # beginner, intermediate, advanced
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    responses = relationship("Response", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, target={self.target_score})>"


class Question(Base):
    """Question model for storing generated questions."""
    
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True)
    question_type = Column(String(20), nullable=False)  # listening, grammar, vocabulary, reading
    difficulty = Column(String(20), nullable=False)  # beginner, intermediate, advanced
    
    # Question content
    question_text = Column(Text, nullable=False)
    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500), nullable=False)
    option_d = Column(String(500), nullable=False)
    correct_answer = Column(String(1), nullable=False)  # A, B, C, or D
    
    # Explanation
    explanation = Column(Text, nullable=True)
    
    # For listening questions
    audio_script = Column(Text, nullable=True)
    audio_file_path = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    used_count = Column(Integer, default=0)
    
    # Relationships
    responses = relationship("Response", back_populates="question")
    
    def __repr__(self):
        return f"<Question(type={self.question_type}, difficulty={self.difficulty})>"


class Response(Base):
    """User response model for tracking answers."""
    
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # Response details
    user_answer = Column(String(1), nullable=False)  # A, B, C, or D
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Integer, nullable=True)
    
    # Metadata
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="responses")
    question = relationship("Question", back_populates="responses")
    
    def __repr__(self):
        return f"<Response(user_id={self.user_id}, correct={self.is_correct})>"


class Progress(Base):
    """Daily progress tracking."""
    
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Daily stats
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    accuracy_percentage = Column(Float, default=0.0)
    
    # By question type
    listening_accuracy = Column(Float, nullable=True)
    grammar_accuracy = Column(Float, nullable=True)
    vocabulary_accuracy = Column(Float, nullable=True)
    reading_accuracy = Column(Float, nullable=True)
    
    # Estimated score (based on performance)
    estimated_toeic_score = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="progress_records")
    
    def __repr__(self):
        return f"<Progress(user_id={self.user_id}, date={self.date}, accuracy={self.accuracy_percentage:.1f}%)>"


# Database initialization
def init_db(database_url: str = "sqlite:///toeic_bot.db"):
    """Initialize the database."""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get a database session."""
    Session = sessionmaker(bind=engine)
    return Session()
