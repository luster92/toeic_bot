"""Generate TOEIC-style grammar questions."""
from typing import Dict, Any
import google.generativeai as genai
import json

from config import config


class GrammarGenerator:
    """Generate TOEIC Part 5-6 grammar and vocabulary questions."""
    
    def __init__(self):
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_grammar_question(self, difficulty: str = "intermediate", 
                                  grammar_point: str = None) -> Dict[str, Any]:
        """Generate a TOEIC Part 5 style grammar question.
        
        Args:
            difficulty: Question difficulty (beginner, intermediate, advanced)
            grammar_point: Optional specific grammar point to focus on
            
        Returns:
            Dictionary with question, options, answer, and explanation
        """
        difficulty_prompts = {
            "beginner": "basic grammar concepts (simple tenses, articles, prepositions)",
            "intermediate": "intermediate grammar (conditionals, perfect tenses, modals, relative clauses)",
            "advanced": "advanced grammar (subjunctive, complex conditionals, nuanced usage)"
        }
        
        grammar_focus = f"\nFocus on: {grammar_point}" if grammar_point else ""
        
        prompt = f"""Generate a TOEIC Part 5 style grammar question.

Difficulty level: {difficulty} - {difficulty_prompts.get(difficulty, difficulty_prompts['intermediate'])}{grammar_focus}

Create a sentence with ONE blank, testing grammar or vocabulary in a business/workplace context.

Common grammar topics for TOEIC 800:
- Verb tenses (especially perfect tenses)
- Conditionals
- Passive voice
- Modals (would, should, must, etc.)
- Relative clauses
- Prepositions
- Conjunctions
- Word forms (noun/verb/adjective/adverb)

Requirements:
- Sentence should be realistic business English
- One answer must be clearly correct, others should be plausible distractors
- Test understanding of grammar rules, not just vocabulary

Return ONLY valid JSON in this exact format:
{{
  "question_text": "The company _____ a new product line next quarter.",
  "option_a": "launch",
  "option_b": "launching",
  "option_c": "will launch",
  "option_d": "launched",
  "correct_answer": "C",
  "explanation": "Future tense is needed for 'next quarter'. 'Will launch' is correct.",
  "grammar_point": "Future tense"
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
        result['question_type'] = 'grammar'
        result['difficulty'] = difficulty
        
        return result
    
    def generate_vocabulary_question(self, difficulty: str = "intermediate") -> Dict[str, Any]:
        """Generate a TOEIC vocabulary-in-context question.
        
        Args:
            difficulty: Question difficulty
            
        Returns:
            Dictionary with question, options, answer, and explanation
        """
        difficulty_prompts = {
            "beginner": "common business vocabulary",
            "intermediate": "intermediate business and professional vocabulary",
            "advanced": "advanced vocabulary, collocations, and idiomatic expressions"
        }
        
        prompt = f"""Generate a TOEIC Part 5 style vocabulary question.

Difficulty level: {difficulty} - {difficulty_prompts.get(difficulty, difficulty_prompts['intermediate'])}

Create a sentence with ONE blank, testing vocabulary in a business/workplace context.

Common TOEIC 800 vocabulary areas:
- Business operations (negotiate, implement, coordinate)
- Finance/accounting (budget, revenue, expenses)
- Human resources (recruit, promote, resign)
- Marketing/sales (campaign, promote, generate leads)
- Office/administration (schedule, postpone, confirm)

Requirements:
- Sentence should show clear context for the vocabulary
- One answer must be clearly correct, others should be plausible similar words
- Test true understanding of word meaning and usage

Return ONLY valid JSON in this exact format:
{{
  "question_text": "The manager decided to _____ the meeting due to a scheduling conflict.",
  "option_a": "postpone",
  "option_b": "cancel",
  "option_c": "attend",
  "option_d": "organize",
  "correct_answer": "A",
  "explanation": "'Postpone' means to reschedule for later, which fits the context of a scheduling conflict.",
  "vocabulary_word": "postpone"
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
        result['question_type'] = 'vocabulary'
        result['difficulty'] = difficulty
        
        return result
    
    def generate_question(self, difficulty: str = "intermediate",
                         focus: str = None) -> Dict[str, Any]:
        """Generate either a grammar or vocabulary question.
        
        Args:
            difficulty: Question difficulty
            focus: 'grammar', 'vocabulary', or None for random
            
        Returns:
            Question dictionary
        """
        import random
        
        if focus is None:
            focus = random.choice(['grammar', 'vocabulary'])
        
        if focus == 'grammar':
            return self.generate_grammar_question(difficulty)
        else:
            return self.generate_vocabulary_question(difficulty)
