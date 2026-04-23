from openai import OpenAI
import json

client = OpenAI(base_url="http://127.0.0.1:13305/api/v1", api_key="lemonade")

resp = client.chat.completions.create(
    model="Qwen3.5-4B-GGUF",
    messages=[
        {
            "role": "system",
            "content": 'Return ONLY valid JSON: [{"question":"...","answer":"..."}]',
        },
        {"role": "user", "content": "Create 2 flashcards about the solar system"},
    ],
    temperature=0,
    max_tokens=5000,
)

text = resp.choices[0].message.content.strip()
if text.startswith("```"):
    text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

print("Raw response:", repr(text))
cards = json.loads(text)
assert isinstance(cards, list) and len(cards) >= 1
assert "question" in cards[0] and "answer" in cards[0]
print("OK")
