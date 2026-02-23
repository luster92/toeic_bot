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
    
    # Create buttons
    keyboard = [
        [
            InlineKeyboardButton("A", callback_data=f"answer_1_A"),
            InlineKeyboardButton("B", callback_data=f"answer_1_B"),
            InlineKeyboardButton("C", callback_data=f"answer_1_C"),
            InlineKeyboardButton("D", callback_data=f"answer_1_D"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send to Telegram
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN_TOEIC")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("❌ Missing TELEGRAM_BOT_TOKEN_TOEIC or TELEGRAM_CHAT_ID")
        return
    
    bot = Bot(token=bot_token)
    
    print(f"📤 Sending to Telegram (Chat ID: {chat_id})...")
    await bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
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
    
    # Create buttons
    keyboard = [
        [
            InlineKeyboardButton("A", callback_data=f"answer_2_A"),
            InlineKeyboardButton("B", callback_data=f"answer_2_B"),
            InlineKeyboardButton("C", callback_data=f"answer_2_C"),
            InlineKeyboardButton("D", callback_data=f"answer_2_D"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send to Telegram
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN_TOEIC")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    bot = Bot(token=bot_token)
    
    print(f"📤 Sending to Telegram (Chat ID: {chat_id})...")
    await bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
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
