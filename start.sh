#!/bin/bash
# 빠른 시작 스크립트

echo "🎯 TOEIC 봇 설정을 시작합니다..."
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env 파일이 없습니다."
    echo "📝 .env 파일을 생성합니다..."
    cp .env.example .env
    echo ""
    echo "⚠️  중요: .env 파일을 편집하여 다음을 입력하세요:"
    echo "   1. TELEGRAM_BOT_TOKEN (BotFather에서 받은 토큰)"
    echo "   2. OPENAI_API_KEY (OpenAI API 키)"
    echo ""
    echo "💡 편집 방법:"
    echo "   nano .env"
    echo "   또는"
    echo "   open -e .env"
    echo ""
    exit 1
fi

# Check if tokens are set
if grep -q "your_telegram_bot_token_here" .env || grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  .env 파일에 API 키를 입력해주세요!"
    echo ""
    echo "편집 방법:"
    echo "  nano .env"
    echo ""
    exit 1
fi

echo "✅ .env 파일 확인 완료"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 가상 환경 활성화 완료"
else
    echo "⚠️  가상 환경이 없습니다. 먼저 설치하세요:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "🚀 TOEIC 봇을 시작합니다..."
echo "📱 Telegram에서 봇을 검색하고 /start를 입력하세요!"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

# Run the bot
python main.py
