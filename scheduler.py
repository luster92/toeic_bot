"""Daily content scheduler for TOEIC Bot."""
import schedule
import time
from datetime import datetime
from typing import List
import logging

from database import init_db, get_session, DatabaseOperations
from generators import ListeningGenerator, GrammarGenerator, TTSGenerator
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DailyScheduler:
    """Schedule and deliver daily TOEIC content."""
    
    def __init__(self, bot_instance):
        """Initialize scheduler.
        
        Args:
            bot_instance: Telegram bot instance for sending messages
        """
        self.bot = bot_instance
        self.engine = init_db(config.database_url)
        
        # Generators
        self.listening_gen = ListeningGenerator()
        self.grammar_gen = GrammarGenerator()
        self.tts_gen = TTSGenerator()
        
        logger.info("DailyScheduler initialized")
    
    def generate_daily_content(self, user, db_ops: DatabaseOperations) -> dict:
        """Generate daily content for a user.
        
        Args:
            user: User database object
            db_ops: DatabaseOperations instance
            
        Returns:
            Dictionary with generated questions and audio files
        """
        difficulty = user.difficulty_level
        content = {
            'listening_questions': [],
            'grammar_questions': []
        }
        
        # Generate listening questions
        for i in range(config.listening_questions_per_day):
            try:
                # Generate question
                q_data = self.listening_gen.generate_question(difficulty)
                
                # Generate audio
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_filename = f"listening_{user.telegram_id}_{timestamp}_{i}"
                audio_path = self.tts_gen.generate_audio(
                    q_data['audio_script'], 
                    audio_filename
                )
                
                # Save to database
                question = db_ops.save_question({
                    'question_type': 'listening',
                    'difficulty': difficulty,
                    'question_text': q_data['question'],
                    'option_a': q_data['option_a'],
                    'option_b': q_data['option_b'],
                    'option_c': q_data['option_c'],
                    'option_d': q_data['option_d'],
                    'correct_answer': q_data['correct_answer'],
                    'explanation': q_data.get('explanation', ''),
                    'audio_script': q_data['audio_script'],
                    'audio_file_path': audio_path
                })
                
                content['listening_questions'].append(question)
                logger.info(f"Generated listening question {i+1} for user {user.telegram_id}")
                
            except Exception as e:
                logger.error(f"Error generating listening question: {e}")
        
        # Generate grammar/vocabulary questions
        for i in range(config.grammar_questions_per_day):
            try:
                q_data = self.grammar_gen.generate_question(difficulty)
                
                # Save to database
                question = db_ops.save_question({
                    'question_type': q_data['question_type'],
                    'difficulty': difficulty,
                    'question_text': q_data['question_text'],
                    'option_a': q_data['option_a'],
                    'option_b': q_data['option_b'],
                    'option_c': q_data['option_c'],
                    'option_d': q_data['option_d'],
                    'correct_answer': q_data['correct_answer'],
                    'explanation': q_data.get('explanation', ''),
                })
                
                content['grammar_questions'].append(question)
                logger.info(f"Generated grammar question {i+1} for user {user.telegram_id}")
                
            except Exception as e:
                logger.error(f"Error generating grammar question: {e}")
        
        return content
    
    def send_daily_content(self, user, content: dict):
        """Send daily content to a user.
        
        Args:
            user: User database object
            content: Dictionary with questions to send
        """
        from formatters import TelegramFormatter
        formatter = TelegramFormatter()
        
        try:
            # Get user stats for intro
            session = get_session(self.engine)
            db_ops = DatabaseOperations(session)
            stats = db_ops.get_user_stats(user.telegram_id)
            
            # Send intro message
            intro_msg = formatter.format_daily_intro(stats)
            self.bot.send_message(chat_id=user.telegram_id, text=intro_msg, parse_mode='Markdown')
            
            # Send listening questions with audio
            for i, question in enumerate(content['listening_questions'], 1):
                # Send audio
                with open(question.audio_file_path, 'rb') as audio_file:
                    self.bot.send_audio(
                        chat_id=user.telegram_id,
                        audio=audio_file,
                        title=f"Listening Question {i}"
                    )
                
                # Send question with answer buttons
                msg = formatter.format_listening_question({
                    'question': question.question_text,
                    'option_a': question.option_a,
                    'option_b': question.option_b,
                    'option_c': question.option_c,
                    'option_d': question.option_d,
                }, question.id)
                
                keyboard = formatter.create_answer_keyboard(question.id)
                self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=msg,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            
            # Send grammar questions
            self.bot.send_message(
                chat_id=user.telegram_id,
                text="\n━━━━━━━━━━━━━━━━━━━━━\n",
                parse_mode='Markdown'
            )
            
            for i, question in enumerate(content['grammar_questions'], 1):
                msg = formatter.format_grammar_question({
                    'question_type': question.question_type,
                    'question_text': question.question_text,
                    'option_a': question.option_a,
                    'option_b': question.option_b,
                    'option_c': question.option_c,
                    'option_d': question.option_d,
                }, question.id, i)
                
                keyboard = formatter.create_answer_keyboard(question.id)
                self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=msg,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            
            # Closing message
            self.bot.send_message(
                chat_id=user.telegram_id,
                text="━━━━━━━━━━━━━━━━━━━━━\n💡 Answer at your convenience. Good luck! 화이팅!",
                parse_mode='Markdown'
            )
            
            session.close()
            logger.info(f"Daily content sent to user {user.telegram_id}")
            
        except Exception as e:
            logger.error(f"Error sending daily content to user {user.telegram_id}: {e}")
    
    def deliver_to_all_users(self):
        """Generate and deliver content to all active users."""
        # Check if we should deliver today (skip weekends if configured)
        if not config.weekend_delivery:
            if datetime.now().weekday() >= 5:  # Saturday = 5, Sunday = 6
                logger.info("Skipping weekend delivery")
                return
        
        logger.info("Starting daily content delivery")
        
        session = get_session(self.engine)
        db_ops = DatabaseOperations(session)
        
        try:
            users = db_ops.get_all_active_users()
            logger.info(f"Delivering to {len(users)} active users")
            
            for user in users:
                try:
                    # Generate content
                    content = self.generate_daily_content(user, db_ops)
                    
                    # Send to user
                    self.send_daily_content(user, content)
                    
                    # Small delay between users
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error delivering to user {user.telegram_id}: {e}")
                    continue
            
            logger.info("Daily content delivery complete")
            
        finally:
            session.close()
    
    def start(self):
        """Start the scheduler."""
        # Schedule daily delivery
        schedule.every().day.at(config.daily_delivery_time).do(self.deliver_to_all_users)
        
        logger.info(f"Scheduler started. Daily delivery at {config.daily_delivery_time} {config.timezone}")
        
        # Run scheduler loop
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
