"""Main TOEIC Bot application."""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import threading

from config import config
from database import init_db, get_session, DatabaseOperations
from formatters import TelegramFormatter
from scheduler import DailyScheduler

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TOEICBot:
    """TOEIC learning bot for Telegram."""
    
    def __init__(self):
        """Initialize the bot."""
        self.engine = init_db(config.database_url)
        self.formatter = TelegramFormatter()
        logger.info("TOEIC Bot initialized")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        
        # Register user in database
        session = get_session(self.engine)
        db_ops = DatabaseOperations(session)
        db_ops.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        session.close()
        
        # Get today's grammar topic
        weekday = datetime.now().weekday()
        grammar_topics = {
            0: "Tenses", 1: "Conditionals", 2: "Active/Passive Voice",
            3: "Participles", 4: "Infinitives/Gerunds", 5: "Relative Clauses",
            6: "Comparatives/Superlatives"
        }
        today_topic = grammar_topics[weekday]
        
        welcome_msg = f"""👋 <b>Welcome to TOEIC Practice Bot!</b>

🎯 Practice TOEIC questions daily and track your progress!

📅 <b>Today's Grammar Focus:</b> {today_topic}

<b>Available Commands:</b>
/practice - Get instant practice questions (Grammar + Reading)
/stats - View your learning statistics
/settings - Check your settings
/help - Show help information

💡 <b>Tip:</b> Use /practice anytime to get questions on today's grammar topic!

Ready to start? Type /practice now! 🚀"""
        
        await update.message.reply_text(welcome_msg, parse_mode='HTML')
        logger.info(f"User {user.id} started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_msg = self.formatter.format_help_message()
        await update.message.reply_text(help_msg, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command."""
        user = update.effective_user
        
        session = get_session(self.engine)
        db_ops = DatabaseOperations(session)
        stats = db_ops.get_user_stats(user.id)
        session.close()
        
        if not stats:
            await update.message.reply_text("No statistics yet. Start answering questions!")
            return
        
        stats_msg = self.formatter.format_stats(stats)
        await update.message.reply_text(stats_msg, parse_mode='Markdown')
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command."""
        user = update.effective_user
        
        session = get_session(self.engine)
        db_ops = DatabaseOperations(session)
        user_obj = db_ops.get_or_create_user(user.id)
        
        settings_msg = self.formatter.format_settings_message({
            'delivery_time': user_obj.delivery_time,
            'timezone': user_obj.timezone,
            'difficulty_level': user_obj.difficulty_level,
            'target_score': user_obj.target_score,
        })
        
        session.close()
        await update.message.reply_text(settings_msg, parse_mode='Markdown')
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command - enable daily questions."""
        user = update.effective_user
        
        session = get_session(self.engine)
        db_ops = DatabaseOperations(session)
        user_obj = db_ops.get_or_create_user(user.id)
        
        if user_obj.is_active:
            msg = """✅ <b>You're already subscribed!</b>

You'll receive daily TOEIC questions every day at 07:00.

💡 Use /unsubscribe to stop daily delivery (you can still use /practice anytime!)"""
        else:
            # Activate subscription
            db_ops.update_user_preferences(user.id, is_active=True)
            msg = """🎉 <b>Successfully subscribed!</b>

Starting tomorrow at 07:00, you'll receive:
• 1 Grammar question (based on daily topic)
• 1 Reading comprehension question

💡 You can still use /practice anytime for instant questions!
📴 Use /unsubscribe to stop daily delivery"""
        
        session.close()
        await update.message.reply_text(msg, parse_mode='HTML')
        logger.info(f"User {user.id} subscribed to daily questions")
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command - disable daily questions."""
        user = update.effective_user
        
        session = get_session(self.engine)
        db_ops = DatabaseOperations(session)
        user_obj = db_ops.get_or_create_user(user.id)
        
        if not user_obj.is_active:
            msg = """ℹ️ <b>You're already unsubscribed!</b>

You won't receive automatic daily questions.

💡 You can still use /practice anytime for instant questions!
🔔 Use /subscribe to re-enable daily delivery"""
        else:
            # Deactivate subscription
            db_ops.update_user_preferences(user.id, is_active=False)
            msg = """👋 <b>Successfully unsubscribed!</b>

You won't receive automatic daily questions anymore.

💡 You can still use /practice anytime for instant questions!
🔔 Use /subscribe to re-enable daily delivery"""
        
        session.close()
        await update.message.reply_text(msg, parse_mode='HTML')
        logger.info(f"User {user.id} unsubscribed from daily questions")
    
    async def practice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /practice command - send instant practice questions."""
        user = update.effective_user
        
        # Determine today's grammar focus based on day of week
        weekday = datetime.now().weekday()  # 0=Monday, 6=Sunday
        grammar_topics = {
            0: "Tenses (Present, Past, Future, Perfect)",  # Monday
            1: "Conditionals (If clauses, Hypothetical situations)",  # Tuesday
            2: "Active and Passive Voice",  # Wednesday
            3: "Participles (Present/Past participles, Participial phrases)",  # Thursday
            4: "Infinitives and Gerunds",  # Friday
            5: "Relative Clauses (Who, Which, That, Whose)",  # Saturday
            6: "Comparatives and Superlatives"  # Sunday
        }
        
        today_topic = grammar_topics[weekday]
        
        await update.message.reply_text(f"🎯 Generating practice questions... Please wait!\n\n📅 Today's grammar focus: <b>{today_topic}</b>", parse_mode='HTML')
        
        session = get_session(self.engine)
        db_ops = DatabaseOperations(session)
        user_obj = db_ops.get_or_create_user(user.id)
        
        # Import generators
        from generators.grammar import GrammarGenerator
        from generators.listening import ListeningGenerator
        import html
        
        # Generate and send grammar question with specific topic
        try:
            grammar_gen = GrammarGenerator()
            grammar_q = grammar_gen.generate_grammar_question(
                difficulty=user_obj.difficulty_level,
                grammar_point=today_topic
            )
            
            # Save to database
            question_obj = db_ops.save_question({
                'question_type': 'grammar',
                'question_text': grammar_q['question_text'],
                'option_a': grammar_q['option_a'],
                'option_b': grammar_q['option_b'],
                'option_c': grammar_q['option_c'],
                'option_d': grammar_q['option_d'],
                'correct_answer': grammar_q['correct_answer'],
                'explanation': grammar_q['explanation'],
                'difficulty': user_obj.difficulty_level
            })
            
            # Format and send message
            msg = f"""📚 <b>TOEIC Grammar Question</b>

{html.escape(grammar_q['question_text'])}

A) {html.escape(grammar_q['option_a'])}
B) {html.escape(grammar_q['option_b'])}
C) {html.escape(grammar_q['option_c'])}
D) {html.escape(grammar_q['option_d'])}

<i>Difficulty: {user_obj.difficulty_level}</i>"""
            
            # Create buttons
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [
                    InlineKeyboardButton("A", callback_data=f"answer_{question_obj.id}_A"),
                    InlineKeyboardButton("B", callback_data=f"answer_{question_obj.id}_B"),
                    InlineKeyboardButton("C", callback_data=f"answer_{question_obj.id}_C"),
                    InlineKeyboardButton("D", callback_data=f"answer_{question_obj.id}_D"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(msg, parse_mode='HTML', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error generating grammar question: {e}")
            await update.message.reply_text(f"❌ Error generating grammar question: {e}")
        
        # Generate and send reading question
        try:
            from generators.reading import ReadingGenerator
            reading_gen = ReadingGenerator()
            reading_q = reading_gen.generate_reading_question(difficulty=user_obj.difficulty_level)
            
            # Save to database
            question_obj = db_ops.save_question({
                'question_type': 'reading',
                'question_text': reading_q['question'],
                'option_a': reading_q['option_a'],
                'option_b': reading_q['option_b'],
                'option_c': reading_q['option_c'],
                'option_d': reading_q['option_d'],
                'correct_answer': reading_q['correct_answer'],
                'explanation': reading_q['explanation'],
                'difficulty': user_obj.difficulty_level
            })
            
            # Format message with passage
            passage = html.escape(reading_q['passage'])
            doc_type = html.escape(reading_q.get('document_type', 'Document'))
            
            msg = f"""📖 <b>TOEIC Reading Question</b>

<b>{doc_type}:</b>
{passage}

<b>Question:</b> {html.escape(reading_q['question'])}

A) {html.escape(reading_q['option_a'])}
B) {html.escape(reading_q['option_b'])}
C) {html.escape(reading_q['option_c'])}
D) {html.escape(reading_q['option_d'])}

<i>Difficulty: {user_obj.difficulty_level}</i>"""
            
            keyboard = [
                [
                    InlineKeyboardButton("A", callback_data=f"answer_{question_obj.id}_A"),
                    InlineKeyboardButton("B", callback_data=f"answer_{question_obj.id}_B"),
                    InlineKeyboardButton("C", callback_data=f"answer_{question_obj.id}_C"),
                    InlineKeyboardButton("D", callback_data=f"answer_{question_obj.id}_D"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(msg, parse_mode='HTML', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error generating reading question: {e}")
            await update.message.reply_text(f"❌ Error generating reading question: {e}")
        
        session.close()
        logger.info(f"User {user.id} requested practice questions")
    
    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle answer button callbacks."""
        query = update.callback_query
        await query.answer()
        
        # Parse callback data: answer_<question_id>_<answer>
        parts = query.data.split('_')
        if len(parts) != 3 or parts[0] != 'answer':
            return
        
        question_id = int(parts[1])
        user_answer = parts[2]
        user = update.effective_user
        
        # Save response
        session = get_session(self.engine)
        db_ops = DatabaseOperations(session)
        
        user_obj = db_ops.get_or_create_user(user.id)
        response = db_ops.save_response(user_obj.id, question_id, user_answer)
        question = db_ops.get_question_by_id(question_id)
        
        # Format result
        result_msg = self.formatter.format_answer_result(
            response.is_correct,
            question.correct_answer,
            question.explanation
        )
        
        session.close()
        
        # Edit message to show result
        await query.edit_message_text(
            text=query.message.text + f"\n\n{result_msg}",
            parse_mode='HTML'
        )
        
        logger.info(f"User {user.id} answered question {question_id}: {user_answer} (correct: {response.is_correct})")
    
    def run(self):
        """Run the bot."""
        # Create application
        application = Application.builder().token(config.telegram_token).build()
        
        # Register bot commands (for Telegram menu)
        from telegram import BotCommand
        async def post_init(app: Application):
            await app.bot.set_my_commands([
                BotCommand("start", "Start the bot and see welcome message"),
                BotCommand("practice", "Get instant practice questions"),
                BotCommand("subscribe", "Enable daily question delivery (7 AM)"),
                BotCommand("unsubscribe", "Disable daily question delivery"),
                BotCommand("stats", "View your learning statistics"),
                BotCommand("settings", "Check your settings"),
                BotCommand("help", "Show help information"),
            ])
        
        application.post_init = post_init
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("settings", self.settings_command))
        application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        application.add_handler(CommandHandler("practice", self.practice_command))
        application.add_handler(CallbackQueryHandler(self.handle_answer))
        
        logger.info("Bot handlers registered")
        
        # Start scheduler in separate thread
        scheduler = DailyScheduler(application.bot)
        scheduler_thread = threading.Thread(target=scheduler.start, daemon=True)
        scheduler_thread.start()
        logger.info("Scheduler thread started")
        
        # Start bot
        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = TOEICBot()
    bot.run()
