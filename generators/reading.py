"""Generate TOEIC-style reading comprehension questions."""
from typing import Dict, Any
import google.generativeai as genai
import json

from config import config


class ReadingGenerator:
    """Generate TOEIC Part 7 reading comprehension questions."""
    
    def __init__(self):
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_reading_question(self, difficulty: str = "intermediate") -> Dict[str, Any]:
        """Generate a TOEIC Part 7 style reading comprehension question.
        
        Args:
            difficulty: Question difficulty (beginner, intermediate, advanced)
            
        Returns:
            Dictionary with passage, question, options, and answer
        """
        difficulty_prompts = {
            "beginner": "simple, short business emails or messages with straightforward information",
            "intermediate": "realistic business documents (emails, memos, notices) with moderate complexity",
            "advanced": "complex business documents with multiple details and nuanced information"
        }
        
        prompt = f"""Generate a TOEIC Part 7 style reading comprehension question.

Difficulty level: {difficulty} - {difficulty_prompts.get(difficulty, difficulty_prompts['intermediate'])}

Create a short business document (email, memo, notice, or advertisement) followed by ONE comprehension question with 4 multiple choice options.

Common document types:
- Business emails
- Company memos
- Advertisements
- Notices/announcements
- News articles (business-related)

Requirements:
- Passage should be realistic business English (targeting TOEIC 800 level)
- Keep passage concise (3-5 sentences for intermediate level)
- Question should test main idea, specific detail, inference, or purpose
- One answer must be clearly correct, others plausible but wrong
- Include document type (e.g., "Email", "Memo", "Notice")

Return ONLY valid JSON in this exact format:
{{
  "document_type": "Email",
  "passage": "The complete passage text here",
  "question": "What is the purpose of this email?",
  "option_a": "First option",
  "option_b": "Second option",
  "option_c": "Third option",
  "option_d": "Fourth option",
  "correct_answer": "C",
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
        result['question_type'] = 'reading'
        result['difficulty'] = difficulty
        
        return result
