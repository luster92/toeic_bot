"""Generate TOEIC-style listening questions."""
from typing import Dict, Any, Optional
import google.generativeai as genai
import json

from config import config


class ListeningGenerator:
    """Generate TOEIC Part 3-4 listening questions."""
    
    def __init__(self):
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
    
    def generate_conversation_question(self, difficulty: str = "intermediate") -> Dict[str, Any]:
        """Generate a TOEIC Part 3 style conversation question.
        
        Args:
            difficulty: Question difficulty (beginner, intermediate, advanced)
            
        Returns:
            Dictionary with conversation script, question, options, and answer
        """
        difficulty_prompts = {
            "beginner": "simple, everyday workplace situations with clear context",
            "intermediate": "realistic workplace scenarios with moderate complexity",
            "advanced": "complex business situations with nuanced language and idiomatic expressions"
        }
        
        prompt = f"""Generate a TOEIC Part 3 style listening question.

Difficulty level: {difficulty} - {difficulty_prompts.get(difficulty, difficulty_prompts['intermediate'])}

Create a short conversation (2-3 exchanges) between two people in a workplace or business setting, followed by ONE comprehension question with 4 multiple choice options.

Requirements:
- Conversation should be natural and realistic (targeting TOEIC 800 level)
- Question should test comprehension, inference, or detail recognition
- One answer must be clearly correct, others plausible but wrong
- Suitable for text-to-speech conversion (avoid complex formatting)

Return ONLY valid JSON in this exact format:
{{
  "conversation": [
    {{"speaker": "Person A", "text": "dialogue here"}},
    {{"speaker": "Person B", "text": "dialogue here"}}
  ],
  "question": "What is the man's main concern?",
  "option_a": "First option",
  "option_b": "Second option",
  "option_c": "Third option",
  "option_d": "Fourth option",
  "correct_answer": "A",
  "explanation": "Brief explanation of why this is correct"
}}"""
        
        response = self.model.generate_content(
            f"""You are a TOEIC test question generator. Always return valid JSON.

{prompt}""",
            generation_config=genai.GenerationConfig(
                temperature=0.8,
                response_mime_type="application/json"
            )
        )
        
        result = json.loads(response.text)
        
        # Format conversation as script for TTS
        script_parts = []
        for exchange in result['conversation']:
            script_parts.append(exchange['text'])
        
        result['audio_script'] = " ... ".join(script_parts)
        result['question_type'] = 'listening'
        result['difficulty'] = difficulty
        
        return result
    
    def generate_talk_question(self, difficulty: str = "intermediate") -> Dict[str, Any]:
        """Generate a TOEIC Part 4 style talk/announcement question.
        
        Args:
            difficulty: Question difficulty
            
        Returns:
            Dictionary with talk script, question, options, and answer
        """
        difficulty_prompts = {
            "beginner": "simple announcements with clear, straightforward information",
            "intermediate": "realistic announcements or talks with moderate detail",
            "advanced": "complex talks with multiple details and sophisticated vocabulary"
        }
        
        prompt = f"""Generate a TOEIC Part 4 style listening question.

Difficulty level: {difficulty} - {difficulty_prompts.get(difficulty, difficulty_prompts['intermediate'])}

Create a short talk, announcement, or voice message (3-5 sentences) followed by ONE comprehension question with 4 multiple choice options.

Common topics:
- Telephone messages
- Recorded announcements (airports, stores, offices)
- News/weather broadcasts
- Advertisements
- Tours/presentations

Requirements:
- Talk should be natural and realistic (targeting TOEIC 800 level)
- Question should test main idea, specific detail, or inference
- One answer must be clearly correct, others plausible but wrong
- Suitable for text-to-speech conversion

Return ONLY valid JSON in this exact format:
{{
  "talk_script": "The complete talk/announcement text here",
  "question": "What is the purpose of the message?",
  "option_a": "First option",
  "option_b": "Second option",
  "option_c": "Third option",
  "option_d": "Fourth option",
  "correct_answer": "B",
  "explanation": "Brief explanation of why this is correct"
}}"""
        
        response = self.model.generate_content(
            f"""You are a TOEIC test question generator. Always return valid JSON.

{prompt}""",
            generation_config=genai.GenerationConfig(
                temperature=0.8,
                response_mime_type="application/json"
            )
        )
        
        result = json.loads(response.text)
        result['audio_script'] = result['talk_script']
        result['question_type'] = 'listening'
        result['difficulty'] = difficulty
        
        return result
    
    def generate_question(self, difficulty: str = "intermediate", 
                         question_style: Optional[str] = None) -> Dict[str, Any]:
        """Generate a listening question (randomly choose conversation or talk).
        
        Args:
            difficulty: Question difficulty
            question_style: 'conversation' or 'talk', or None for random
            
        Returns:
            Question dictionary
        """
        import random
        
        if question_style is None:
            question_style = random.choice(['conversation', 'talk'])
        
        if question_style == 'conversation':
            return self.generate_conversation_question(difficulty)
        else:
            return self.generate_talk_question(difficulty)
