"""Telegram message formatting utilities."""
from typing import Dict, Any, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class TelegramFormatter:
    """Format content for Telegram display."""
    
    @staticmethod
    def format_listening_question(question_data: Dict[str, Any], question_id: int) -> str:
        """Format a listening question for Telegram.
        
        Args:
            question_data: Question dictionary from ListeningGenerator
            question_id: Database question ID
            
        Returns:
            Formatted message text
        """
        msg = "🎧 **LISTENING QUESTION**\n\n"
        
        # Add conversation context if available
        if 'conversation' in question_data:
            msg += "_Listen to the audio, then answer:_\n\n"
        else:
            msg += "_Listen to the talk/announcement, then answer:_\n\n"
        
        msg += f"**{question_data['question']}**\n\n"
        msg += f"A) {question_data['option_a']}\n"
        msg += f"B) {question_data['option_b']}\n"
        msg += f"C) {question_data['option_c']}\n"
        msg += f"D) {question_data['option_d']}\n"
        
        return msg
    
    @staticmethod
    def format_grammar_question(question_data: Dict[str, Any], question_id: int,
                                question_num: int = 1) -> str:
        """Format a grammar question for Telegram.
        
        Args:
            question_data: Question dictionary from GrammarGenerator
            question_id: Database question ID
            question_num: Question number in sequence
            
        Returns:
            Formatted message text
        """
        q_type = "GRAMMAR" if question_data.get('question_type') == 'grammar' else "VOCABULARY"
        
        msg = f"✍️ **{q_type} QUESTION #{question_num}**\n\n"
        msg += f"{question_data['question_text']}\n\n"
        msg += f"A) {question_data['option_a']}\n"
        msg += f"B) {question_data['option_b']}\n"
        msg += f"C) {question_data['option_c']}\n"
        msg += f"D) {question_data['option_d']}\n"
        
        return msg
    
    @staticmethod
    def create_answer_keyboard(question_id: int) -> InlineKeyboardMarkup:
        """Create inline keyboard for answering questions.
        
        Args:
            question_id: Database question ID
            
        Returns:
            InlineKeyboardMarkup with A/B/C/D buttons
        """
        keyboard = [
            [
                InlineKeyboardButton("A", callback_data=f"answer_{question_id}_A"),
                InlineKeyboardButton("B", callback_data=f"answer_{question_id}_B"),
                InlineKeyboardButton("C", callback_data=f"answer_{question_id}_C"),
                InlineKeyboardButton("D", callback_data=f"answer_{question_id}_D"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def format_answer_result(is_correct: bool, correct_answer: str, 
                            explanation: str) -> str:
        """Format answer result message.
        
        Args:
            is_correct: Whether user answered correctly
            correct_answer: The correct answer letter
            explanation: Explanation text
            
        Returns:
            Formatted result message
        """
        if is_correct:
            msg = "✅ **Correct!**\n\n"
        else:
            msg = f"❌ **Incorrect.** The correct answer is **{correct_answer}**.\n\n"
        
        msg += f"💡 {explanation}"
        
        return msg
    
    @staticmethod
    def format_daily_intro(user_stats: Dict[str, Any]) -> str:
        """Format daily introduction message.
        
        Args:
            user_stats: Dictionary with user statistics
            
        Returns:
            Formatted introduction message
        """
        current_score = user_stats.get('current_score', 600)
        target_score = user_stats.get('target_score', 800)
        progress = user_stats.get('progress_to_goal', 0)
        streak = user_stats.get('streak_days', 0)
        
        # Progress bar
        filled = int(progress / 10)
        bar = "█" * filled + "░" * (10 - filled)
        
        msg = f"🎧 **TOEIC Daily Practice**\n\n"
        msg += f"🎯 Target: {target_score} | Current: {current_score}\n"
        msg += f"Progress: {bar} {progress:.0f}%\n"
        
        if streak > 0:
            msg += f"🔥 {streak} day streak!\n"
        
        msg += f"\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        return msg
    
    @staticmethod
    def format_stats(stats: Dict[str, Any]) -> str:
        """Format user statistics message.
        
        Args:
            stats: User statistics dictionary
            
        Returns:
            Formatted stats message
        """
        msg = "📊 **Your TOEIC Progress**\n\n"
        
        # Overall stats
        msg += f"🎯 **Target Score:** {stats.get('target_score', 800)}\n"
        msg += f"💯 **Current Score:** {stats.get('current_score', 600)}\n"
        msg += f"📈 **Progress:** {stats.get('progress_to_goal', 0):.0f}%\n\n"
        
        # Performance
        total_q = stats.get('total_questions', 0)
        accuracy = stats.get('overall_accuracy', 0)
        msg += f"📝 **Questions Answered:** {total_q}\n"
        msg += f"✅ **Overall Accuracy:** {accuracy:.1f}%\n"
        
        if stats.get('streak_days', 0) > 0:
            msg += f"🔥 **Streak:** {stats['streak_days']} days\n"
        
        # Weak areas
        weak_areas = stats.get('weak_areas', {})
        if weak_areas:
            msg += "\n**📉 Areas to Improve:**\n"
            for area, acc in list(weak_areas.items())[:3]:
                emoji = "🎧" if area == "listening" else "✍️"
                msg += f"{emoji} {area.title()}: {acc:.0f}%\n"
        
        msg += f"\n💡 Keep practicing to reach your goal!"
        
        return msg
    
    @staticmethod
    def format_help_message() -> str:
        """Format help message with available commands."""
        msg = """📚 **TOEIC Bot Commands**

**Daily Practice:**
Your daily lesson arrives automatically each morning with listening and grammar questions.

**Commands:**
/start - Start using the bot
/stats - View your progress and statistics
/settings - Adjust your preferences
/help - Show this help message

**How to Use:**
1. Listen to audio questions (great for your commute!)
2. Tap A/B/C/D to answer questions
3. Review explanations to learn
4. Track your progress toward 800!

**Tips:**
🎧 Save audio files to listen during your commute
📊 Check /stats weekly to see improvement
🔥 Build a daily streak for best results

Good luck! 화이팅! 🚀"""
        
        return msg
    
    @staticmethod
    def format_settings_message(user_prefs: Dict[str, Any]) -> str:
        """Format settings display message.
        
        Args:
            user_prefs: User preferences dictionary
            
        Returns:
            Formatted settings message
        """
        msg = "⚙️ **Your Settings**\n\n"
        msg += f"🕐 **Delivery Time:** {user_prefs.get('delivery_time', '07:00')}\n"
        msg += f"🌏 **Timezone:** {user_prefs.get('timezone', 'Asia/Seoul')}\n"
        msg += f"📊 **Difficulty:** {user_prefs.get('difficulty_level', 'intermediate').title()}\n"
        msg += f"🎯 **Target Score:** {user_prefs.get('target_score', 800)}\n\n"
        msg += "To change settings, contact support or modify .env file."
        
        return msg
