<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## סקירה כללית

🍋 **Lemonade** הוא שרת AI מקומי בקוד פתוח המאפשר לך להריץ מודלים שפה גדולים (LLMs), מחוללי תמונות ומודלי אודיו ישירות על החומרה שלך. הוא חושף את המודלים דרך **OpenAI API** הסטנדרטי בתעשייה, כך שכל אפליקציה שעובדת עם OpenAI יכולה לעבוד מיידית עם Lemonade. בסיום ה-playbook, תשתמש ב-Lemonade להרצת מודלים מקומית על המחשב שלך.

## מה תלמד

בסיום ה-playbook הזה תוכל:

* **להתקין את Lemonade Server** ולאמת שהוא פועל.
* **להוריד ולשוחח עם LLM** באמצעות פקודה אחת.
* **לחקור את ממשק המשתמש הגרפי** ולנסות מודאליות שונות כגון ראייה, המרת דיבור לטקסט ויצירת תמונות.
* **להחליף בין backends של GPU** בין Vulkan ו-AMD ROCm™ software.
* **לבנות אפליקציית Python** המופעלת על ידי LLM מקומי באמצעות ה-API התואם ל-OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **להריץ מודלים על AMD Neural Processing Unit (NPU)** באמצעות מצבי הרצה Hybrid ו-FLM על חומרת AMD Ryzen™ AI.
<!-- @device:end -->

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

לפני שתתחיל, ודא שיש לך:

- מחשב עם **Windows 11** או הפצת **Linux** נתמכת (Ubuntu 24.04+, Fedora, Debian)
- **16 GB של RAM** מומלצים עבור מודל הזמן-ריצה המשמש בשלבים 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** מומלצים אם ברצונך להשתמש במודל יצירת הקוד הגדול יותר בשלב 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB של שטח דיסק פנוי**, בהתאם למודלים שתוריד. המודל הגדול ביותר במדריך זה הוא כ-20 GB.
- **Python 3.10–3.13** (משמש בחלק אפליקציית Python)
- חיבור לאינטרנט (קווי או אלחוטי)
<!-- @device:halo_box,halo,stx,krk -->
- [אופציונלי] AMD XDNA 2 NPU (סדרת Ryzen AI 300/400/Max 300 או Z2 Extreme) עם מנהל ההתקן העדכני ביותר המותקן מ-[הוראות התקנת Ryzen AI Software](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) אם ברצונך להריץ מודל על ה-NPU.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

---

## מושגי יסוד — כיצד עובדים שרתי AI מקומיים

לפני שנריץ מודל, כדאי להבין *מדוע* הדברים מוגדרים בצורה זו. Lemonade הוא **שרת מודלים מקומי**, תהליך שטוען מודלי AI לזיכרון וחושף אותם לאפליקציות דרך HTTP, בדיוק כפי שהיה עושה שירות AI בענן.

### מדוע שרת?

| יתרון | מה זה אומר עבורך |
|---------|----------------------|
| **אינטגרציה פשוטה** | אפליקציות מתקשרות עם API HTTP אחד במקום להתמודד עם ספריות C++ או Python ספציפיות לחומרה. |
| **מודלים משותפים** | מודל טעון אחד יכול לשרת מספר אפליקציות בו-זמנית, ללא עותקים כפולים שאוכלים את ה-RAM שלך. |
| **ניידות מענן למקומי** | קוד שנכתב עבור ה-API הענני של OpenAI עובד עם Lemonade על ידי שינוי URL אחד. |
| **הפרדת אחריות** | ניהול מודלים, סטרימינג וסובלנות לתקלות מטופלים על ידי השרת כך שמפתחים יכולים להתמקד באפליקציה שלהם. |

### תקן OpenAI API

Lemonade מממש את **OpenAI API**, אותו ממשק המשמש את ChatGPT, Azure OpenAI ועשרות שירותים אחרים. מודל השיחה פשוט:

| תפקיד | מי מדבר |
|------|---------------|
| **system** | הוראות למודל (אישיות, מגבלות, כלים זמינים) |
| **user** | הודעות מהאדם (או האפליקציה) למודל |
| **assistant** | תגובות שנוצרו על ידי המודל |

משמעות הדבר היא שכל ספרייה או אפליקציה התומכת ב-OpenAI יכולה לדבר עם Lemonade על ידי הפנייתה אל `http://localhost:13305/api/v1` בזמן שהשרת Lemonade Server פועל.

## פעילות ראשית — שיחת AI מקומית ראשונה שלך

בואו נוריד LLM ונשוחח איתו, כשה-AI פועל לחלוטין על המחשב שלך.

### שלב 1: הורדה והרצת מודל

Lemonade מגיע עם ספריית מודלים מאוצרת. נתחיל עם **Gemma-4-E2B-it**, מודל מסוגל וקומפקטי הכולל תמיכה בראייה. פתח טרמינל והרץ:

```
lemonade run Gemma-4-E2B-it-GGUF
```

פקודה בודדת זו עושה שלושה דברים:

1. **מוריד** את המודל (~3 GB) מ-Hugging Face, אם הוא עדיין לא הורד. (עשוי לקחת זמן מה)
2. **מפעיל** את תהליך Lemonade Server על פורט 13305.
3. **פותח את Lemonade App** כדי שתוכל להתחיל לשוחח עם המודל.


<!-- @os:windows -->
ב-Windows, Lemonade App מופעל אוטומטית ותוכל להתחיל לשוחח מיידית. אם התקנת את חבילת `minimal.msi`, האפליקציה אינה כלולה. כדי להתחיל לשוחח, פתח את דפדפן האינטרנט שלך ועבור אל `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
בלינוקס, פתח את הדפדפן שלך ונווט אל `http://localhost:13305` כדי לגשת לאפליקציית האינטרנט.
<!-- @os:end -->

נסה להקליד שאלה:

```
What are three fun facts about lemons?
```

המודל יגיב ישירות בחלון הצ'אט. **ברכות! אתה מריץ מודל שפה גדול מקומית.**

![Lemonade App עם יומנים מוצגים](../../dependencies/assets/ChatwithLogs.png)

בחלונית יומני השרת ב-Lemonade App, תוכל למצוא נתוני טלמטריה על ביצועי המודל לאחר כל תגובה. לדוגמה:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```
### שלב 2: חקור את ממשק האינטרנט ומודאליות שונות

Lemonade כולל ממשק אינטרנט מובנה שבו תוכל:

- **לתקשר** עם המודל הטעון בחלון צ'אט מוכר
- **לעיין במודלים** בלשונית Model Manager
- **להוריד מודלים חדשים** בלחיצה אחת

נסה לעבור בין מודאליות שונות באמצעות לשונית **Model Manager** בממשק האינטרנט, שם תוכל לעיין במודלים לפי Recipe או לפי Category:

1. **ראייה:** המודל `Gemma-4-E2B-it-GGUF` שכבר טענת תומך בראייה. הדבק תמונה לתיבת הצ'אט ובקש מהמודל לתאר אותה.
2. **יצירת תמונות:** בקטגוריית Image, הורד מודל תמונה כגון `SDXL-Turbo` מה-Model Manager, ולאחר מכן השתמש ב-Lemonade Image Generator כדי להקליד פרומפט וליצור תמונה באופן מקומי.
3. **שמע:** בקטגוריית Audio, הורד מודל שמע כגון `Whisper-Tiny`, שיכול לבצע המרת דיבור לטקסט. ספק הקלטת שמע כדי לתמלל אותה באופן מקומי. להמרת טקסט לדיבור, נסה אחד מהמודלים בקטגוריית Speech, כגון `kokoro-v1`.

![מולטי-מודאליות עם Lemonade](../../dependencies/assets/multi_modality.png)

### שלב 3: נסה מודל עם Backend שונה

אם תרחף מעל מודל באפליקציית Lemonade, תראה סמל גלגל שיניים. לחיצה עליו מאפשרת לך לבחור אפשרויות עבור המודל, כולל בחירת ה-backend הרצוי.

כברירת מחדל, Lemonade משתמש ב-Vulkan לאצת GPU. אם יש לך AMD GPU נפרד נתמך, תוכל לעבור ל-ROCm.

![Lemonade בחירת Backend](../../dependencies/assets/lemonademodeloptions.png)

כדי לנהל את ה-backends המותקנים שלך, לחץ על כפתור ה-backend בעמודה השמאלית ביותר.

לחלופין, תוכל לציין את ה-backend באמצעות הפקודה הבאה:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

תוכל גם להגדיר את ה-backend שלך כברירת מחדל באמצעות משתנה הסביבה `LEMONADE_LLAMACPP` עם הערכים: `vulkan`, `rocm`, או `cpu`.

---

## העמקה — בנה אפליקציית AI מבוססת Python

הכוח האמיתי של שרת AI מקומי הוא שכל אפליקציה יכולה להתחבר אליו באמצעות כמה שורות קוד בלבד. כדי להוכיח זאת, בואו נבנה **מחולל כרטיסיות לימוד** קטן אך פונקציונלי, שבו אתה נותן לו נושא, הוא מייצר כרטיסיות, ותוכל לבחון את עצמך באופן אינטראקטיבי.

### שלב 4: הפעל את השרת

ודא שהשרת של Lemonade פועל. הוא בדרך כלל מתחיל אוטומטית ברקע לאחר ההתקנה. לאימות, הרץ:

```
lemonade status
```

אמור לראות הודעה כגון: `Server is running on port 13305`.

אם השרת אינו פועל, הפעל אותו על ידי פתיחת אפליקציית Lemonade. השתמש ביציאת ברירת המחדל **13305** (תוכל לאשר או לבחור זאת מסמל המגש).

### שלב 5: התקן את לקוח Python של OpenAI

בטרמינל, צור venv והתקן את לקוח Python של OpenAI באמצעות הפקודות הבאות:
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### שלב 6: בנה את אפליקציית הכרטיסיות

בואו נוריד מודל שונה ליצירת קוד: `Qwen3.5-35B-A3B-GGUF`. זהו מודל גדול (~20 GB) ובעל ביצועים גבוהים, המתאים ביותר למערכות עם 32 GB+ של RAM. אם יש לך פחות RAM זמין, נסה את `Qwen3.5-9B-GGUF` (~6 GB) במקום.

תוכל להוריד אותו מממשק המשתמש או להריץ את הפקודה הבאה:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

הזן את הפרומפט הבא לממשק Lemonade Chat UI כדי ליצור קוד לאפליקציית כרטיסיות פשוטה.

נשתמש ב-Qwen3.5-35B-A3B-GGUF (מודל גדול יותר שטוב יותר בכתיבת קוד) כדי ליצור את אפליקציית Python שלנו, והאפליקציה עצמה תקרא ל-Gemma-4-E2B-it-GGUF (המודל הקטן יותר שכבר הורדת) בזמן ריצה. לאחר מכן ניתן להעתיק את הקוד לקובץ לבחירתך להרצה ב-Python.

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **טיפ**: פעלנו לפי שיטות הנדסה סטנדרטיות באמצעות יצירת פרומפטים מקיפה ושימוש במערכת דו-מודלית לאופטימיזציה של משאבים ומהירות.

לנוחיותך, סיפקנו פלט לדוגמה ב-[`flashcards.py`](assets/flashcards.py). אל תהסס להוריד אותו לספרייה שלך. כך או כך, אמור להיות לך כעת קובץ Python שניתן להריץ.

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### שלב 7: הרץ את הקוד שנוצר

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**הנה מה שאמור להופיע:**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

בכ-150 שורות קוד בנית כלי לימוד פונקציונלי לחלוטין המופעל על ידי LLM מקומי. אין מפתח API לנהל, אין עלויות שימוש, ואין נתונים שיוצאים אי פעם מהמחשב שלך.

> **תובנה מרכזית:** שים לב שהשורה `client = OpenAI(base_url=...) ` היא *הדבר היחיד* שקושר את האפליקציה הזו ל-Lemonade במקום לענן של OpenAI. שאר הקוד זהה למה שהיית כותב מול כל שירות תואם OpenAI. אם השתמשת אי פעם בספריית Python של OpenAI, אתה כבר יודע כיצד לבנות אפליקציות עם Lemonade.

### מה זה מדגים

אפליקציה קטנה זו מממשת מספר דפוסי אינטגרציה מהעולם האמיתי:

| דפוס | היכן הוא מופיע |
|---------|-----------------|
| **פרומפטים של מערכת** | הודעת `"system"` מורה ל-LLM לפלוט JSON מובנה |
| **פלט מובנה** | האפליקציה מנתחת את תגובת ה-LLM כ-JSON לבניית כרטיסיות |
| **בקשות ללא מצב** | כל קריאה ל-`generate_flashcards()` היא עצמאית |
| **טיפול בשגיאות** | ה-`try/except` מטפל בחן במקרים שבהם פלט ה-LLM אינו JSON תקין |

אותם דפוסים מתרחבים לכל אפליקציה כגון צ'אטבוטים, עוזרי קוד, מחוללי תוכן, כלי אוטומציה.

#### אתגר בונוס

* לאתגר נוסף, נסה לעדכן את האפליקציה כך שהכרטיסיות יוקראו למשתמש על ידי הפניה לדוגמה המסופקת [כאן](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## הרצת מודלים על ה-NPU (אופציונלי)

אם יש לך סדרת Ryzen AI 300/400/Max 300 או Z2 Extreme, המכשיר שלך כולל **יחידת עיבוד עצבי (NPU)** מובנית — שבב ייעודי שתוכנן במיוחד לעומסי עבודה של בינה מלאכותית. הרצת מודלים על ה-NPU יעילה יותר מבחינת צריכת חשמל בהשוואה לשימוש ב-GPU, מה שהופך אותה לאידיאלית למשימות בינה מלאכותית ברקע, סשנים ממושכים ושימוש על סוללה.

Lemonade תומך בשלושה מצבי הרצה על ה-NPU, כולם שקופים מאחורי אותו OpenAI API:

| מצב | כיצד זה עובד | Recipe | דוגמאות למודלים |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | ה-NPU מעבד את ה-prompt, ה-iGPU מייצר טוקנים | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU בלבד** | כל ה-inference רץ על ה-NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | משתמש במנוע FastFlowLM על ה-NPU, מותאם ל-AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### דרישות

- מעבד **AMD Ryzen AI 300/400 series או Z2 series**
- עבור מודלי **FLM**: ניתן להתקין את סביבת הריצה של FLM מתוך אפליקציית Lemonade, או ש-Lemonade תתקין אוטומטית את סביבת הריצה של FLM בעת הרצת מודל FLM. למידע נוסף על FastFlowLM, ראה [כאן](https://fastflowlm.com/docs/).


### שלב 8: הרצת מודל Hybrid

מודלי Hybrid מחלקים את העבודה בין ה-NPU ל-iGPU לאיזון טוב בין מהירות ויעילות. באפליקציית Lemonade, בחר מודל מרשימת `Ryzen AI LLM`, לדוגמה `Qwen3-4B-Hybrid`, או הרץ אותו באמצעות הפקודה הבאה:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade מזהה את ה-NPU שלך אוטומטית ומתקין את ה-backend של **Ryzen AI LLM**.

> **מה קורה מאחורי הקלעים?** כאשר אתה שולח הודעה, ה-NPU מעבד את כל ה-prompt שלך במקביל (זה נקרא "prefill"). לאחר מכן, ה-iGPU לוקח את השליטה כדי לייצר את התגובה טוקן אחד בכל פעם (זה נקרא "decode"). גישת ה-hybrid הזו מנצלת את החוזקות של כל שבב.

### שלב 9: הרצת מודל FLM

מודלי FastFlowLM (FLM) מותאמים במיוחד לארכיטקטורת ה-XDNA2 NPU של AMD ויכולים להיות מהירים מאוד ביחס לגודלם. לדוגמה, בחר `qwen3.5-4b-FLM` מרשימת `FastFlowLM NPU` או השתמש בפקודה הבאה:

<!-- @os:windows -->
כדי להפעיל את `FastFlowLM` על Windows:

* פתח את תפריט `Backends Manager`.
* אתר את קטגוריית ה-backend של `FastFlowLM NPU`.
* לחץ על Install NPU.
* לאחר השלמת ההתקנה, כ-36 מודלים ברירת מחדל יהיו זמינים תחת תפריט ה-FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
כאשר אפליקציית `Lemonade` מופעלת בפעם הראשונה, ה-backend של `FastFlowNPU` אינו מופעל כברירת מחדל.
האפליקציה המקומית תפתח את דף ההתקנה כדי להדריך אותך בתהליך ההגדרה.

כדי להפעיל את `FastFlowLM` על Linux:

* פתח את אפליקציית `Lemonade`.
* בקר בתיעוד [הרשמי של FLM](https://lemonade-server.ai/flm_npu_linux.html) ופעל לפי שלבי ההתקנה של FLM על ידי בחירת הפצת Linux שלך.
* הפעל backports כפי שמוסבר בדף ההתקנה.
* הורד את גרסת `v0.9.x` האחרונה מ[דף ה-tags](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
עבור AMD Halo Developer Platform, הקפד לבחור Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* התקן את חבילת ה-`.deb` שהורדת.
* מומלץ: צא מ`אפליקציית Lemonade` ופתח אותה שוב כדי שהשינויים יזוהו.
* מומלץ: פתח את `Backends Manager` ולחץ על Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
לאחר התקנה מוצלחת, אמור להופיע ש-`flm:npu` הושלם ב**Download Manager** בתוך **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
לאחר מכן תוכל לבחור כל אחד ממודלי ה-FFLM הזמינים ולהתחיל להשתמש ב-backend של ה-NPU.

עבור מודל ספציפי, הורד את המודל הרצוי מ[דף המודלים](https://fastflowlm.com/docs/models/qwen/) ואמת אותו באמצעות פקודת ה-Shell המסופקת בתיעוד.
```
flm run qwen3.5-4b-FLM
```
או דרך 
```
lemonade run qwen3.5-4b-FLM
```

מודלי FLM כוללים חלק מהארכיטקטורות הפופולריות ביותר (Gemma 3, Qwen 3, Llama 3, ו-DeepSeek R1) ונעים בין פחות מ-1 GB ליותר מ-13 GB.
Lemonade מזהה את ה-NPU שלך אוטומטית ומתקין את ה-backend של **FastFlowLM NPU**.

<!-- @os:windows -->
> **טיפ:** לביצועי NPU מיטביים, הפעל מצב turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### החלפת מודלים

אפליקציית כרטיסיות הלמידה משלב 6 עובדת גם עם מודלי NPU, פשוט שנה את שם המודל:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## השלבים הבאים

יש לך שרת בינה מלאכותית מקומי שרץ על החומרה שלך, הנה לאן להמשיך:

1. **חבר את האפליקציות המועדפות עליך**: Lemonade עובד מהקופסה עם [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/), ו[עוד רבים](https://lemonade-server.ai/marketplace).

2. **עיין במודלים נוספים**: חקור את [ספריית המודלים](https://lemonade-server.ai/docs/server/server_models/) המלאה כדי למצוא מודלים מותאמים לקידוד, הסקה, ראייה ועוד. השתמש באפליקציית Lemonade או ב-`lemonade list` כדי לראות מה זמין.

3. **שחרר האצת GPU של ROCm**: אם יש לך GPU של AMD נתמך, עבור ל-backend של ROCm: `lemonade config set llamacpp.backend=rocm`. ראה [GPU נתמכים של AMD](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **קרא את מפרט ה-API המלא**: Lemonade תומך בהשלמות צ'אט, embeddings, תמלול שמע, יצירת תמונות, המרת טקסט לדיבור ועוד. ראה את [מפרט השרת](https://lemonade-server.ai/docs/server/server_spec/) לכל endpoint.

5. **תרום**: Lemonade הוא קוד פתוח. עיין ב[מדריך התרומה](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) וחפש [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).