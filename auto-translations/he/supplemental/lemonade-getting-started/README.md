<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## סקירה כללית

🍋 **Lemonade** הוא שרת AI מקומי בקוד פתוח המאפשר לכם להריץ מודלי שפה גדולים (LLMs), מחוללי תמונות ומודלי אודיו ישירות על החומרה שלכם. הוא חושף את המודלים באמצעות **OpenAI API**, תקן הענף המקובל, כך שכל אפליקציה שעובדת עם OpenAI יכולה לעבוד באופן מיידי עם Lemonade. עד סוף המדריך, תשתמשו ב-Lemonade כדי להריץ מודלים באופן מקומי על המחשב שלכם.

## מה תלמדו

עד סוף מדריך זה תוכלו:

* **להתקין את Lemonade Server** ולוודא שהוא פועל.
* **להוריד ולשוחח עם LLM** באמצעות פקודה אחת.
* **לחקור את ממשק הווב** ולנסות מודליות שונות כמו ראייה, המרת דיבור לטקסט, ויצירת תמונות.
* **להחליף בין backends של GPU** בין Vulkan לתוכנת AMD ROCm™.
* **לבנות אפליקציית Python** המופעלת על ידי LLM מקומי באמצעות ה-API התואם ל-OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **להריץ מודלים על יחידת העיבוד העצבית (NPU) של AMD** באמצעות מצבי הרצה Hybrid ו-FLM על חומרת AMD Ryzen™ AI.
<!-- @device:end -->

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

לפני שתתחילו, ודאו שיש לכם:

- מחשב עם **Windows 11** או הפצת **Linux** נתמכת (Ubuntu 24.04+, Fedora, Debian)
- מומלץ **16 GB של זיכרון RAM** עבור מודל הריצה בשלבים 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). מומלץ **32 GB+** אם ברצונכם להשתמש במודל יצירת הקוד הגדול יותר בשלב 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **כ-4–30 GB של שטח פנוי בדיסק**, בהתאם למודלים שתורידו. המודל הגדול ביותר במדריך זה הוא כ-20 GB.
- **Python 3.10–3.13** (בשימוש בחלק אפליקציית ה-Python)
- חיבור לאינטרנט (קווי או אלחוטי)
<!-- @device:halo_box,halo,stx,krk -->
- [אופציונלי] NPU מסוג AMD XDNA 2 (סדרת Ryzen AI 300/400/Max 300 או Z2 Extreme) עם המנהל התקן העדכני ביותר מותקן מתוך [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) אם ברצונכם להריץ מודל על ה-NPU.
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
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```bash
winget upgrade -e --id AMD.LemonadeServer
lemonade --version
```
<!-- @test:end -->

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
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

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

## מושגי יסוד — כיצד פועלים שרתי AI מקומיים

לפני שנריץ מודל, כדאי להבין *מדוע* הדברים מוגדרים בצורה הזו. Lemonade הוא **שרת מודלים מקומי**, תהליך שטוען מודלי AI לזיכרון וחושף אותם לאפליקציות דרך HTTP, בדיוק כפי ששירות AI בענן היה עושה.

### למה שרת?

| יתרון | מה זה אומר עבורכם |
|---------|----------------------|
| **אינטגרציה פשוטה** | אפליקציות מתקשרות עם API אחד של HTTP במקום להתמודד עם ספריות C++ או Python ספציפיות לחומרה. |
| **מודלים משותפים** | מודל טעון יחיד יכול לשרת מספר אפליקציות בו-זמנית, ללא עותקים כפולים שאוכלים את ה-RAM שלכם. |
| **ניידות מענן למקומי** | קוד שנכתב עבור ה-API הענני של OpenAI עובד עם Lemonade על ידי שינוי כתובת URL אחת. |
| **הפרדת אחריות** | ניהול מודלים, סטרימינג וטיפול בתקלות מטופלים על ידי השרת כך שהמפתחים יכולים להתמקד באפליקציה שלהם. |

### תקן ה-OpenAI API

Lemonade מיישם את **OpenAI API**, אותו ממשק המשמש את ChatGPT, Azure OpenAI ועשרות שירותים נוספים. מודל השיחה פשוט:

| תפקיד | מי מדבר |
|------|---------------|
| **system** | הוראות למודל (אישיות, מגבלות, כלים זמינים) |
| **user** | הודעות מהאדם (או מהאפליקציה) אל המודל |
| **assistant** | תגובות שנוצרות על ידי המודל |

משמעות הדבר היא שכל ספרייה או אפליקציה התומכת ב-OpenAI יכולה לתקשר עם Lemonade על ידי הפניה אל `http://localhost:13305/api/v1` בזמן ש-Lemonade Server פועל.

## פעילות עיקרית — שיחת ה-AI המקומית הראשונה שלכם

בואו נוריד LLM ונשוחח איתו, כאשר ה-AI פועל כולו על המחשב שלכם.

### שלב 1: הורדה והרצה של מודל

Lemonade מגיע עם ספריית מודלים אוצרת. נתחיל עם **Gemma-4-E2B-it**, מודל מסוגל וקומפקטי הכולל תמיכה בראייה. פתחו טרמינל והריצו:

```
lemonade run Gemma-4-E2B-it-GGUF
```

פקודה יחידה זו מבצעת שלושה דברים:

1. **מורידה** את המודל (~3 GB) מ-Hugging Face, אם הוא עוד לא הורד. (עשוי לקחת זמן מה)
2. **מפעילה** את תהליך Lemonade Server בפורט 13305.
3. **פותחת את Lemonade App** כך שתוכלו להתחיל לשוחח עם המודל.


<!-- @os:windows -->
ב-Windows, Lemonade App מופעל אוטומטית ותוכלו להתחיל לשוחח מיד. אם התקנתם את חבילת `minimal.msi`, האפליקציה אינה כלולה. כדי להתחיל לשוחח, פתחו את דפדפן האינטרנט שלכם וגשו אל `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
ב-Linux, פתחו את הדפדפן שלכם ונווטו אל `http://localhost:13305` כדי לגשת לאפליקציית הווב.
<!-- @os:end -->

נסו להקליד שאלה:

```
What are three fun facts about lemons?
```

המודל יגיב ישירות בחלון הצ'אט. **מזל טוב! אתם מריצים כעת מודל שפה גדול באופן מקומי.**

![Lemonade App with Logs displayed](../../dependencies/assets/ChatwithLogs.png)

בחלונית Server Logs באפליקציית Lemonade, תוכלו למצוא נתוני טלמטריה על ביצועי המודל לאחר כל תגובה. לדוגמה:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### שלב 2: חקירת ממשק האינטרנט ומודליות שונות

Lemonade כולל ממשק אינטרנט מובנה שבו ניתן:

- **לתקשר** עם המודל הטעון בחלון צ'אט מוכר
- **לעיין במודלים** בכרטיסייה Model Manager
- **להוריד מודלים חדשים** בלחיצה אחת

נסו לעבור בין מודליות שונות באמצעות הכרטיסייה **Model Manager** בממשק האינטרנט, שם ניתן לעיין במודלים לפי מתכון (Recipe) או לפי קטגוריה:

1. **ראייה (Vision):** המודל `Gemma-4-E2B-it-GGUF` שכבר טענתם תומך בראייה. הדביקו תמונה בתיבת הצ'אט ובקשו מהמודל לתאר אותה.
2. **יצירת תמונות:** בקטגוריית Image, הורידו מודל תמונות כגון `SDXL-Turbo` מה-Model Manager, ולאחר מכן השתמשו ב-Lemonade Image Generator כדי להקליד הנחיה וליצור תמונה באופן מקומי.
3. **שמע:** בקטגוריית Audio, הורידו מודל שמע כגון `Whisper-Tiny`, שיכול לבצע המרת דיבור לטקסט. ספקו הקלטת שמע כדי לתמלל אותה באופן מקומי. עבור המרת טקסט לדיבור, נסו את אחד המודלים בקטגוריית Speech, כגון `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### שלב 3: ניסיון של מודל עם מנוע אחורי (Backend) שונה

אם תעבירו את העכבר מעל מודל באפליקציית Lemonade, תראו סמל של גלגל שיניים. לחיצה עליו מאפשרת לבחור אפשרויות עבור המודל, כולל בחירת מנוע האחורי הרצוי.

כברירת מחדל, Lemonade משתמש ב-Vulkan להאצת GPU. אם יש לכם כרטיס GPU דיסקרטי נתמך של AMD, תוכלו לעבור ל-ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

כדי לנהל את מנועי האחורי המותקנים שלכם, לחצו על כפתור ה-backend בעמודה השמאלית ביותר.

לחלופין, ניתן לציין את מנוע האחורי באמצעות הפקודה הבאה:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

ניתן גם להגדיר את מנוע האחורי המוגדר כברירת מחדל באמצעות משתנה הסביבה `LEMONADE_LLAMACPP` עם הערכים: `vulkan`, `rocm`, או `cpu`.

---

## העמקה — בניית אפליקציית AI מבוססת Python

הכוח האמיתי של שרת AI מקומי הוא שכל אפליקציה יכולה להתחבר אליו באמצעות מספר שורות קוד בלבד. כדי להוכיח זאת, בואו נבנה **מחולל כרטיסיות לימוד (flashcards)** קטן אך פונקציונלי, שבו תיתנו לו נושא, הוא ייצור כרטיסיות לימוד, ותוכלו לבחון את עצמכם באופן אינטראקטיבי.

### שלב 4: הפעלת השרת

ודאו ששרת Lemonade פועל. הוא בדרך כלל מופעל אוטומטית ברקע לאחר ההתקנה. כדי לוודא זאת, הריצו:

```
lemonade status
```

אתם אמורים לראות הודעה כמו: `Server is running on port 13305`.

אם השרת אינו פועל, הפעילו אותו על ידי פתיחת אפליקציית Lemonade. השתמשו בפורט ברירת המחדל **13305** (ניתן לאשר או לבחור אותו מסמל המגש).

### שלב 5: התקנת לקוח ה-Python של OpenAI

בטרמינל, צרו venv והתקינו את לקוח ה-Python של OpenAI באמצעות הפקודות הבאות:
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

### שלב 6: בניית אפליקציית הכרטיסיות

בואו נוריד מודל אחר ליצירת קוד: `Qwen3.5-35B-A3B-GGUF`. זהו מודל גדול (כ-20 GB) ובעל ביצועים גבוהים, המתאים ביותר למערכות עם 32 GB+ של RAM. אם יש לכם פחות RAM זמין, נסו במקום זאת את `Qwen3.5-9B-GGUF` (כ-6 GB).

ניתן להוריד אותו מהממשק או להריץ את הפקודה הבאה:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

הזינו את ההנחיה הבאה לתוך ממשק ה-Chat של Lemonade כדי ליצור קוד עבור אפליקציית Flashcard פשוטה.

נשתמש ב-Qwen3.5-35B-A3B-GGUF (מודל גדול יותר, טוב יותר בכתיבת קוד) כדי ליצור את אפליקציית ה-Python שלנו, והאפליקציה עצמה תקרא בזמן ריצה ל-Gemma-4-E2B-it-GGUF (המודל הקטן יותר שכבר הורדתם). לאחר מכן ניתן להעתיק את הקוד לקובץ לבחירתכם כדי להריץ אותו ב-Python.

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

> **טיפ**: פעלנו לפי שיטות הנדסה סטנדרטיות באמצעות יצירת הנחיות יסודית ושימוש במערכת דו-מודלית כדי לייעל משאבים ומהירות.

לנוחיותכם, סיפקנו פלט לדוגמה בקובץ [`flashcards.py`](assets/flashcards.py). אתם מוזמנים להוריד אותו לתיקייה שלכם. כך או כך, אמור להיות ברשותכם כעת קובץ Python שניתן להריץ.

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


### שלב 7: הרצת הקוד שנוצר

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**הנה מה שאתם אמורים לראות:**

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

בכ-150 שורות קוד בניתם כלי לימוד פונקציונלי במלואו המופעל על ידי LLM מקומי. אין מפתח API לנהל, אין עלויות שימוש, ואף נתון לא יוצא מהמחשב שלכם.

> **תובנה מרכזית:** שימו לב שהשורה `client = OpenAI(base_url=...) ` היא הדבר *היחיד* שמקשר את האפליקציה הזו ל-Lemonade במקום לענן של OpenAI. שאר הקוד זהה למה שהייתם כותבים כנגד כל שירות תואם OpenAI. אם השתמשתם אי פעם בספריית ה-Python של OpenAI, אתם כבר יודעים כיצד לבנות אפליקציות עם Lemonade.

### מה זה ממחיש

אפליקציה קטנה זו מדגימה כמה דפוסי אינטגרציה מהעולם האמיתי:

| דפוס | היכן הוא מופיע |
|---------|-----------------|
| **הנחיות מערכת (System prompts)** | ההודעה `"system"` מנחה את ה-LLM לפלוט JSON מובנה |
| **פלט מובנה** | האפליקציה מנתחת את תגובת ה-LLM כ-JSON כדי לבנות כרטיסיות לימוד |
| **בקשות חסרות מצב (Stateless)** | כל קריאה ל-`generate_flashcards()` היא עצמאית |
| **טיפול בשגיאות** | ה-`try/except` מטפל בצורה חלקה במקרים שבהם הפלט של ה-LLM אינו JSON תקין |

דפוסים זהים אלה מתרחבים לכל אפליקציה כגון צ'אטבוטים, עוזרי קוד, מחוללי תוכן, כלי אוטומציה.

#### אתגר בונוס

* לאתגר נוסף, נסו לעדכן את האפליקציה כך שכרטיסיות הלימוד יוקראו למשתמש, בהתבסס על הדוגמה המסופקת [כאן](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## הפעלת מודלים על ה-NPU (אופציונלי)

אם ברשותכם מכשיר עם Ryzen AI 300/400/Max 300 series או Z2 Extreme, המכשיר שלכם כולל **יחידת עיבוד נוירונים (NPU)** מובנית - שבב ייעודי שתוכנן במיוחד עבור עומסי עבודה של AI. הפעלת מודלים על ה-NPU חסכונית יותר באנרגיה בהשוואה לשימוש ב-GPU, מה שהופך אותה לאידיאלית עבור משימות AI ברקע, סשנים ארוכים ושימוש מבוסס סוללה.

Lemonade תומך בשלושה מצבי הרצה על NPU, כולם שקופים מאחורי אותו OpenAI API:

| מצב | איך זה עובד | מתכון | דוגמאות מודלים |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | ה-NPU מעבד את ה-prompt, ה-iGPU מייצר טוקנים | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU בלבד** | כל תהליך ההסקה רץ על ה-NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | משתמש במנוע FastFlowLM על ה-NPU, מותאם ל-AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### דרישות

- מעבד **AMD Ryzen AI 300/400 series או Z2 series**
- עבור מודלי **FLM**: ניתן להתקין את זמן הריצה של FLM מתוך אפליקציית Lemonade, או ש-Lemonade יתקין אוטומטית את זמן הריצה של FLM בעת הרצת מודל FLM. למידע נוסף על FastFlowLM, ראו [כאן](https://fastflowlm.com/docs/).


### שלב 8: הרצת מודל Hybrid

מודלי Hybrid מחלקים את העבודה בין ה-NPU וה-iGPU לאיזון טוב בין מהירות ויעילות. באפליקציית Lemonade, בחרו מודל מרשימת `Ryzen AI LLM`, לדוגמה, `Qwen3-4B-Hybrid`, או הריצו אותו באמצעות הפקודה הבאה:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade מזהה את ה-NPU שלכם באופן אוטומטי ומתקין את מנגנון **Ryzen AI LLM**.

> **מה קורה מאחורי הקלעים?** כאשר אתם שולחים הודעה, ה-NPU מעבד את כל ה-prompt שלכם במקביל (זה נקרא "prefill"). לאחר מכן, ה-iGPU משתלט על התהליך כדי לייצר את התשובה טוקן אחד בכל פעם (זה נקרא "decode"). גישת ה-hybrid הזו ממנפת את החוזקות של כל שבב.

### שלב 9: הרצת מודל FLM

מודלי FastFlowLM (FLM) מותאמים במיוחד לארכיטקטורת ה-NPU מסוג XDNA2 של AMD, ויכולים להיות מהירים מאוד ביחס לגודלם. לדוגמה, בחרו את `qwen3.5-4b-FLM` מרשימת `FastFlowLM NPU` או השתמשו בפקודה הבאה:

<!-- @os:windows -->
כדי להפעיל את `FastFlowLM` ב-Windows:

* פתחו את תפריט `Backends Manager`.
* אתרו את קטגוריית מנגנון `FastFlowLM NPU`.
* לחצו על Install NPU.
* לאחר השלמת ההתקנה, כ-36 מודלי ברירת מחדל יהיו זמינים תחת תפריט הנפתח של FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
כאשר אפליקציית `Lemonade` מופעלת בפעם הראשונה, מנגנון ה-`FastFlowNPU` אינו מופעל כברירת מחדל. 
האפליקציה המקומית תפתח את עמוד ההתקנה כדי להדריך אתכם בתהליך ההגדרה.

כדי להפעיל את `FastFlowLM` ב-Linux:

* פתחו את אפליקציית `Lemonade`.
* בקרו בתיעוד ה-[רשמי של FLM](https://lemonade-server.ai/flm_npu_linux.html) ועקבו אחר שלבי ההתקנה של FLM על ידי בחירת הפצת ה-Linux שלכם.
* הפעילו backports כפי שמצוין בעמוד ההתקנה.
* הורידו את הגרסה העדכנית ביותר `v0.9.x` מ[עמוד התגיות](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
עבור AMD Halo Developer Platform, ודאו שאתם בוחרים ב-Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* התקינו את חבילת `.deb` שהורדתם.
* מומלץ: צאו מאפליקציית `Lemonade App` ופתחו אותה מחדש כדי שהשינויים יזוהו.
* מומלץ: פתחו את `Backends Manager` ולחצו על Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
לאחר התקנה מוצלחת, אתם אמורים לראות ש-`flm:npu` הושלם ב**מנהל ההורדות** בתוך **אפליקציית Lemonade Desktop**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
לאחר מכן תוכלו לבחור בכל אחד מהמודלים הזמינים של FFLM ולהתחיל להשתמש במנגנון ה-NPU.

עבור מודל ספציפי, הורידו את המודל הרצוי מ[עמוד המודלים](https://fastflowlm.com/docs/models/qwen/) ואמתו אותו באמצעות פקודת ה-Shell המסופקת בתיעוד.
```
flm run qwen3.5-4b-FLM
```
או באמצעות 
```
lemonade run qwen3.5-4b-FLM
```

מודלי FLM כוללים כמה מהארכיטקטורות הפופולריות ביותר (Gemma 3, Qwen 3, Llama 3 ו-DeepSeek R1) ונעים בין פחות מ-1GB ליותר מ-13GB.
Lemonade מזהה את ה-NPU שלכם באופן אוטומטי ומתקין את מנגנון **FastFlowLM NPU**.

<!-- @os:windows -->
> **טיפ:** לביצועי NPU מיטביים, הפעילו מצב turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### החלפת מודלים

אפליקציית כרטיסיות הזיכרון משלב 6 עובדת גם עם מודלי NPU, פשוט שנו את שם המודל:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## הצעדים הבאים

יש לכם שרת AI מקומי שרץ על החומרה שלכם, הנה לאן להמשיך מכאן:

1. **חברו את האפליקציות האהובות עליכם**: Lemonade עובד ישר מהקופסה עם [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/), ו[עוד רבים נוספים](https://lemonade-server.ai/marketplace).

2. **עיינו במודלים נוספים**: חקרו את [ספריית המודלים](https://lemonade-server.ai/docs/server/server_models/) המלאה כדי למצוא מודלים המותאמים לקידוד, הסקה, ראייה ועוד. השתמשו באפליקציית Lemonade או ב-`lemonade list` כדי לראות מה זמין.

3. **פתחו האצת GPU עם ROCm**: אם ברשותכם GPU נתמך של AMD, עברו למנגנון ROCm: `lemonade config set llamacpp.backend=rocm`. ראו [רשימת GPU של AMD הנתמכים](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **קראו את מפרט ה-API המלא**: Lemonade תומך בהשלמות צ'אט, embeddings, תמלול אודיו, יצירת תמונות, המרת טקסט לדיבור ועוד. ראו את [מפרט השרת](https://lemonade-server.ai/docs/server/server_spec/) לכל endpoint.

5. **תרמו לפרויקט**: Lemonade הוא קוד פתוח. עיינו ב[מדריך התרומה](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) וחפשו [בעיות מתאימות למתחילים](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->