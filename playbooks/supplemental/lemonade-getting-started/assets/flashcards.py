# Copyright Advanced Micro Devices, Inc.
# 
# SPDX-License-Identifier: MIT

from openai import OpenAI
import json
import random

# Configuration
API_KEY = "lemonade"
BASE_URL = "http://localhost:13305/api/v1"
MODEL = "Gemma-4-E2B-it-GGUF"

# Initialize the OpenAI Client
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

def clean_json_response(raw_response):
    """
    Attempts to extract JSON from a raw string response.
    Handles cases where the LLM wraps JSON in markdown code blocks.
    """
    raw_response = raw_response.strip()
    if raw_response.startswith("```json"):
        raw_response = raw_response[7:]
    elif raw_response.startswith("```"):
        raw_response = raw_response[3:]
    if raw_response.endswith("```"):
        raw_response = raw_response[:-3]
    return raw_response.strip()

def generate_flashcards(topic, count=5):
    """
    Prompts the LLM to generate a JSON array of flashcards.
    """
    print(f"\n✨ Generating {count} flashcards on: {topic}\n")

    system_prompt = """
    You are a helpful study assistant.
    Your task is to generate exactly {count} flashcards about the topic '{topic}'.
    Return ONLY a raw JSON array of objects.
    Each object must have "question" and "answer" keys.
    Do not include markdown formatting (like ```json), do not include explanations,
    and do not include any text outside the JSON array.
    """

    user_prompt = f"Create {count} flashcards on the topic: {topic}"

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt.format(topic=topic, count=count)},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        raw_content = response.choices[0].message.content
        cleaned_content = clean_json_response(raw_content)

        cards = json.loads(cleaned_content)

        # Basic validation that items have keys
        if not all("question" in c and "answer" in c for c in cards):
            raise ValueError("Generated JSON objects missing 'question' or 'answer' keys.")

        return cards

    except json.JSONDecodeError:
        print("\n[ERROR] The model returned invalid JSON. Please try a different topic or check your connection.")
        print(f"Raw response: {raw_content[:100]}...")
        return []
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        return []

def quiz(cards):
    """
    Runs the interactive quiz session.
    """
    if not cards:
        print("No cards available to quiz.")
        return

    score = 0
    shuffled_cards = cards.copy()
    random.shuffle(shuffled_cards)

    for i, card in enumerate(shuffled_cards, 1):
        print(f"--- Card {i}/{len(shuffled_cards)} ---")
        print(f"Q: {card['question']}\n")
        input("Press Enter to reveal the answer...")
        print(f"A: {card['answer']}\n")

        while True:
            try:
                user_response = input("Did you get it right? (y/n): ").strip().lower()
                if user_response in ['y', 'yes']:
                    score += 1
                    print()
                    break
                elif user_response in ['n', 'no']:
                    print()
                    break
                else:
                    print("Please type 'y' or 'n'.")
            except (KeyboardInterrupt, EOFError):
                print("\nQuiz interrupted.")
                return

    print(f"🏆 Score: {score}/{len(shuffled_cards)}")

def main():
    print("🍋 Lemonade Flashcard Generator")
    print("================================")
    print("Powered by a local LLM running on your own hardware.\n")

    while True:
        topic = input('Enter a topic (or "quit" to exit): ').strip()

        if topic.lower() == 'quit':
            print("Happy studying! 👋")
            break

        if not topic:
            print("Topic cannot be empty.")
            continue

        cards = generate_flashcards(topic)

        if not cards:
            print("Failed to generate cards. Returning to main menu.\n")
            continue

        print(f"Generated {len(cards)} cards!\n")
        for i, card in enumerate(cards, 1):
            print(f"  {i}. {card['question']}")
        print()

        try:
            start_quiz = input("Start quiz? (y/n): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nHappy studying! 👋")
            break

        if start_quiz == 'y':
            quiz(cards)
            print()

if __name__ == "__main__":
    main()
