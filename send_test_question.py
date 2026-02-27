"""Send a test TOEIC question to Telegram."""
import sys
import os
from pathlib import Path
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import html

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generators.listening import ListeningGenerator
from generators.grammar import GrammarGenerator

load_dotenv(Path(__file__).parent.parent / '.env')


def escape_html(text):
    """Escape HTML special characters."""
    return html.escape(text)


async def send_grammar_question():
    """Generate and send a grammar question."""
    print("📝 Generating grammar question...")
    generator = GrammarGenerator()
    question = generator.generate_grammar_question(difficulty="intermediate")
    
    # Escape all text content
    q_text = escape_html(question['question_text'])
    opt_a = escape_html(question['option_a'])
    opt_b = escape_html(question['option_b'])
    opt_c = escape_html(question['option_c'])
    opt_d = escape_html(question['option_d'])
    grammar_pt = escape_html(question.get('grammar_point', 'N/A'))
    
    # Format message with proper HTML
    message = f"""📚 <b>TOEIC Grammar Question</b>

{q_text}

A) {opt_a}
B) {opt_b}
C) {opt_c}
D) {opt_d}

<i>Difficulty: Intermediate</i>
<i>Grammar Point: {grammar_pt}</i>"""
    
    # Register user in database (for handling callbacks)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN_TOEIC")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    from database import init_db, get_session, DatabaseOperations
    from config import config
    engine = init_db(config.database_url)
    session = get_session(engine)
    db_ops = DatabaseOperations(session)
    
    # Get or create user
    user_obj = db_ops.get_or_create_user(telegram_id=int(chat_id))
    
    # Save question to DB
    question_obj = db_ops.save_question({
        'question_type': 'grammar',
        'difficulty': 'intermediate',
        'question_text': question['question_text'],
        'option_a': question['option_a'],
        'option_b': question['option_b'],
        'option_c': question['option_c'],
        'option_d': question['option_d'],
        'correct_answer': question['correct_answer'],
        'explanation': question['explanation'],
    })

    # Create buttons with REAL question ID
    keyboard = [
        [
            InlineKeyboardButton("A", callback_data=f"answer_{question_obj.id}_A"),
            InlineKeyboardButton("B", callback_data=f"answer_{question_obj.id}_B"),
            InlineKeyboardButton("C", callback_data=f"answer_{question_obj.id}_C"),
            InlineKeyboardButton("D", callback_data=f"answer_{question_obj.id}_D"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    bot = Bot(token=bot_token)
    
    print(f"📤 Sending to Telegram (Chat ID: {chat_id})...")
    await bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    session.close()
    
    print("✅ Question sent successfully!")
    print(f"\n정답: {question['correct_answer']}")
    print(f"해설: {question['explanation']}")


async def send_listening_question():
    """Generate and send a listening question."""
    print("\n🎧 Generating listening question...")
    generator = ListeningGenerator()
    question = generator.generate_conversation_question(difficulty="intermediate")
    
    # Format conversation with HTML escaping
    conversation_parts = []
    for exchange in question.get('conversation', []):
        speaker = escape_html(exchange['speaker'])
        text = escape_html(exchange['text'])
        conversation_parts.append(f"<b>{speaker}:</b> {text}")
    
    conversation_text = "\n\n".join(conversation_parts)
    
    # Escape question text and options
    q_question = escape_html(question['question'])
    opt_a = escape_html(question['option_a'])
    opt_b = escape_html(question['option_b'])
    opt_c = escape_html(question['option_c'])
    opt_d = escape_html(question['option_d'])
    
    # Format message
    message = f"""🎧 <b>TOEIC Listening Question</b>

<b>Conversation:</b>
{conversation_text}

<b>Question:</b> {q_question}

A) {opt_a}
B) {opt_b}
C) {opt_c}
D) {opt_d}

<i>Difficulty: Intermediate</i>"""
    
    # Register user and save question
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN_TOEIC")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    from database import init_db, get_session, DatabaseOperations
    from config import config
    engine = init_db(config.database_url)
    session = get_session(engine)
    db_ops = DatabaseOperations(session)
    
    # Save question to DB
    question_obj = db_ops.save_question({
        'question_type': 'listening',
        'difficulty': 'intermediate',
        'question_text': question['question'],
        'option_a': question['option_a'],
        'option_b': question['option_b'],
        'option_c': question['option_c'],
        'option_d': question['option_d'],
        'correct_answer': question['correct_answer'],
        'explanation': question['explanation'],
    })

    # Create buttons with REAL question ID
    keyboard = [
        [
            InlineKeyboardButton("A", callback_data=f"answer_{question_obj.id}_A"),
            InlineKeyboardButton("B", callback_data=f"answer_{question_obj.id}_B"),
            InlineKeyboardButton("C", callback_data=f"answer_{question_obj.id}_C"),
            InlineKeyboardButton("D", callback_data=f"answer_{question_obj.id}_D"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    bot = Bot(token=bot_token)
    
    print(f"📤 Sending to Telegram (Chat ID: {chat_id})...")
    await bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    session.close()
    
    print("✅ Question sent successfully!")
    print(f"\n정답: {question['correct_answer']}")
    print(f"해설: {question['explanation']}")


async def main():
    """Send both questions."""
    print("🚀 TOEIC Bot - Test Question Sender")
    print("=" * 60)
    
    # Send grammar question
    await send_grammar_question()
    
    # Send listening question
    await send_listening_question()
    
    print("\n" + "=" * 60)
    print("🎉 All questions sent!")


if __name__ == "__main__":
    asyncio.run(main())
