# TOEIC Bot

A Telegram-based TOEIC learning bot that delivers daily personalized content to help you achieve your target score of 800.

## Features

- 🎧 **Daily Listening Practice**: AI-generated TOEIC-style listening questions with TTS audio
- ✍️ **Grammar & Vocabulary**: Daily grammar and vocabulary exercises
- 📊 **Progress Tracking**: Track your improvement and estimated TOEIC score
- 🎯 **Adaptive Learning**: Content difficulty adjusts to your performance
- 🔥 **Streak Tracking**: Build consistent study habits
- 📱 **Mobile-Friendly**: Perfect for commute-time learning
- 🆓 **Free AI**: Uses Google Gemini API (free tier available)

## Setup

### 1. Install Dependencies

```bash
cd toeic_bot
python -m venv venv
source venv/bin/activate  # On Mac/Linux
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required configuration:
- `TELEGRAM_BOT_TOKEN_TOEIC`: Get from [@BotFather](https://t.me/botfather)
- `GEMINI_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/apikey)

Optional configuration:
- `DAILY_DELIVERY_TIME`: When to send daily lessons (default: 07:00)
- `LISTENING_QUESTIONS_PER_DAY`: Number of listening questions (default: 3)
- `GRAMMAR_QUESTIONS_PER_DAY`: Number of grammar questions (default: 5)
- `WEEKEND_DELIVERY`: Whether to deliver on weekends (default: false)
- `TTS_LANGUAGE`: Language for text-to-speech (default: en)

### 3. Create Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token to your `.env` file as `TELEGRAM_BOT_TOKEN_TOEIC`

### 4. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a new API key
3. Copy it to your `.env` file as `GEMINI_API_KEY`

### 5. Run the Bot

```bash
python main.py
```

Or use the launch script:

```bash
./start.sh
```

## Usage

1. **Start the bot**: Open your bot on Telegram and send `/start`
2. **Daily lessons**: Receive automatic lessons each morning
3. **Listen while commuting**: Play audio questions during your drive
4. **Answer questions**: Tap A/B/C/D buttons to submit answers
5. **Track progress**: Use `/stats` to see your improvement

### Commands

- `/start` - Start using the bot
- `/help` - Show help message
- `/stats` - View your progress and statistics
- `/settings` - View your current settings

## Project Structure

```
toeic_bot/
├── main.py                 # Main bot application
├── config.py              # Configuration management
├── scheduler.py           # Daily content scheduler
├── database/              # Database models and operations
│   ├── models.py
│   └── operations.py
├── generators/            # AI content generators
│   ├── listening.py       # Listening question generator (Gemini)
│   ├── grammar.py         # Grammar question generator (Gemini)
│   └── tts.py            # Text-to-speech generator (gTTS)
├── formatters/           # Telegram message formatters
│   └── telegram.py
└── deploy/               # Deployment scripts
    └── run.sh
```

## Cost Estimation

- **Google Gemini API**: FREE tier (60 requests/minute)
- **gTTS (Google Text-to-Speech)**: FREE unlimited
- **Total**: $0/month! 🎉

## Tips for Success

1. 🎧 **Save audio files** to listen multiple times
2. 📊 **Check stats weekly** to identify weak areas
3. 🔥 **Build a streak** for consistent improvement
4. 📝 **Review explanations** to learn from mistakes
5. 🎯 **Stay focused** on your 800-point goal!

## Requirements

- Python 3.8+
- Telegram account
- Google Gemini API key (free tier available)
- Internet connection

## Migration from OpenAI

This bot now uses Google Gemini instead of OpenAI, making it completely free to run!

- Question generation: Gemini 2.0 Flash
- Text-to-speech: Google TTS (gTTS)

## License

MIT License - Feel free to modify for your own use!

---

Good luck on your TOEIC journey! 화이팅! 🚀
