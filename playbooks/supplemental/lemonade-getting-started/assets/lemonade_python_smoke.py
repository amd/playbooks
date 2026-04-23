from openai import OpenAI
import json
import time

client = OpenAI(
    base_url="http://127.0.0.1:13305/api/v1",
    api_key="lemonade",
)

last_error = None

print("\n")
print("="*50)
print("       LEMONADE PYTHON FLASHCARD SMOKE TEST")
print("="*50)
print("Attempting to generate 2 flashcards using the Qwen3.5-4B-GGUF model...")

for attempt in range(5):
    text = None
    try:
        resp = client.chat.completions.create(
            model="Qwen3.5-4B-GGUF",
            messages=[
                {
                    "role": "system",
                    "content": 'Return ONLY valid JSON: [{"question":"...","answer":"..."}]',
                },
                {
                    "role": "user",
                    "content": "Create 2 flashcards about the solar system",
                },
            ],
            temperature=0,
            max_tokens=5000,
            stream=False,
        )

        if getattr(resp, "error", None):
            raise RuntimeError(f"API returned error payload: {resp.error}")

        if not getattr(resp, "choices", None):
            raise RuntimeError(f"No choices returned by model. Full response: {resp}")

        content = getattr(resp.choices[0].message, "content", None)
        if content is None:
            raise RuntimeError(f"Model returned null content. Full response: {resp}")

        text = content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        cards = json.loads(text)

        if not isinstance(cards, list):
            raise RuntimeError("Model did not return a JSON list.")

        if len(cards) != 2:
            raise RuntimeError(f"Expected 2 flashcards, got {len(cards)}.")

        for i, card in enumerate(cards, 1):
            if not isinstance(card, dict):
                raise RuntimeError(f"Card {i} is not a JSON object.")
            if "question" not in card or "answer" not in card:
                raise RuntimeError(f"Card {i} is missing 'question' or 'answer'.")
            if not isinstance(card["question"], str) or not isinstance(card["answer"], str):
                raise RuntimeError(f"Card {i} has non-string 'question' or 'answer'.")

        print(f"Attempt {attempt + 1} passed")
        print("Raw response:", repr(text))
        break

    except Exception as e:
        last_error = e
        print(f"Attempt {attempt + 1} failed: {e}")
        if text is not None:
            print("Raw response:", repr(text))
        if attempt < 4:
            time.sleep(3)
        else:
            raise last_error