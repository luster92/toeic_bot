"""Test script for TOEIC Bot question generation."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generators.listening import ListeningGenerator
from generators.grammar import GrammarGenerator
from generators.tts import TTSGenerator
import json


def test_grammar_question():
    """Test grammar question generation."""
    print("=" * 60)
    print("Testing Grammar Question Generation with Gemini API")
    print("=" * 60)
    
    try:
        generator = GrammarGenerator()
        question = generator.generate_grammar_question(difficulty="intermediate")
        
        print("\n✅ Grammar Question Generated Successfully!")
        print(f"\nQuestion: {question['question_text']}")
        print(f"\nA) {question['option_a']}")
        print(f"B) {question['option_b']}")
        print(f"C) {question['option_c']}")
        print(f"D) {question['option_d']}")
        print(f"\nCorrect Answer: {question['correct_answer']}")
        print(f"Explanation: {question['explanation']}")
        print(f"Grammar Point: {question.get('grammar_point', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error generating grammar question: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_listening_question():
    """Test listening question generation."""
    print("\n" + "=" * 60)
    print("Testing Listening Question Generation with Gemini API")
    print("=" * 60)
    
    try:
        generator = ListeningGenerator()
        question = generator.generate_conversation_question(difficulty="intermediate")
        
        print("\n✅ Listening Question Generated Successfully!")
        print(f"\nConversation:")
        for exchange in question.get('conversation', []):
            print(f"  {exchange['speaker']}: {exchange['text']}")
        
        print(f"\nQuestion: {question['question']}")
        print(f"\nA) {question['option_a']}")
        print(f"B) {question['option_b']}")
        print(f"C) {question['option_c']}")
        print(f"D) {question['option_d']}")
        print(f"\nCorrect Answer: {question['correct_answer']}")
        print(f"Explanation: {question['explanation']}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error generating listening question: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tts():
    """Test TTS generation."""
    print("\n" + "=" * 60)
    print("Testing TTS Generation with gTTS")
    print("=" * 60)
    
    try:
        generator = TTSGenerator()
        test_text = "Hello, this is a test of the text-to-speech system for TOEIC listening practice."
        
        audio_file = generator.generate_audio(test_text, "test_audio")
        
        print(f"\n✅ Audio Generated Successfully!")
        print(f"Audio file saved to: {audio_file}")
        
        # Check if file exists
        import os
        if os.path.exists(audio_file):
            file_size = os.path.getsize(audio_file)
            print(f"File size: {file_size} bytes")
            return True
        else:
            print(f"❌ Audio file not found: {audio_file}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error generating TTS: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n🚀 TOEIC Bot - Gemini API Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Grammar Question
    results.append(("Grammar Question", test_grammar_question()))
    
    # Test 2: Listening Question
    results.append(("Listening Question", test_listening_question()))
    
    # Test 3: TTS
    results.append(("TTS Generation", test_tts()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The bot is ready to use!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
