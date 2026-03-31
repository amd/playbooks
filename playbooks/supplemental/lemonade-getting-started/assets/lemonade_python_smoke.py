from openai import OpenAI
import json

client = OpenAI(base_url="http://127.0.0.1:8000/api/v1", api_key="lemonade")

resp = client.chat.completions.create(
    model="Gemma-3-4b-it-GGUF",
    messages=[
        {
            "role": "system",
            "content": 'Return ONLY valid JSON: [{"question":"...","answer":"..."}]',
        },
        {"role": "user", "content": "Create 2 flashcards about the solar system"},
    ],
    temperature=0,
    max_tokens=500,
)

text = resp.choices[0].message.content.strip()
if text.startswith("```"):
    text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

cards = json.loads(text)
assert isinstance(cards, list) and len(cards) >= 1
assert "question" in cards[0] and "answer" in cards[0]
print("OK")
