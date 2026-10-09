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
# סקירה כללית

🍋 **Lemonade** הוא שרת AI מקומי בקוד פתוח המאפשר להריץ מודלי שפה גדולים (LLMs), מחוללי תמונות ומודלי אודיו ישירות על החומרה שלך. הוא חושף את המודלים באמצעות ה-**OpenAI API** התעשייתי הסטנדרטי, כך שכל אפליקציה שעובדת עם OpenAI יכולה לעבוד באופן מיידי עם Lemonade. בסיום המדריך, תשתמשו ב-Lemonade כדי להריץ מודלים מקומית על המכונה שלכם.

## מה תלמדו

בסיום מדריך זה תוכלו:

* **להתקין את Lemonade Server** ולוודא שהוא פועל.
* **להוריד ולשוחח עם LLM** בעזרת פקודה אחת.
* **לחקור את ממשק המשתמש באינטרנט** ולנסות מודאליות שונות כמו ראייה, המרת דיבור לטקסט, ויצירת תמונות.
* **להחליף בין backends של GPU** בין Vulkan לתוכנת AMD ROCm™.
* **לבנות אפליקציית Python** המופעלת על ידי LLM מקומי באמצעות ה-API התואם ל-OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **הרצת מודלים על יחידת העיבוד הנוירונית (NPU) של AMD** באמצעות מצבי הרצה Hybrid ו-FLM על חומרת AMD Ryzen™ AI.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה
<!-- @require:software-update -->
<!-- @device:end -->
## התקנת תלויות התוכנה

לפני שתתחילו, ודאו שיש לכם:

- מחשב שמריץ **Windows 11** או הפצת **Linux** נתמכת (Ubuntu 24.04+, Fedora, Debian)
- מומלצים **16 GB של זיכרון RAM** עבור מודל הריצה המשמש בשלבים 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). מומלצים **32 GB+** אם ברצונכם להשתמש במודל יצירת הקוד הגדול יותר בשלב 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **כ-4–30 GB של שטח פנוי בדיסק**, תלוי במודלים שתורידו. המודל הגדול ביותר במדריך זה הוא כ-20 GB.
- **Python 3.10–3.13** (בשימוש בחלק האפליקציית Python)
- חיבור אינטרנט (קווי או אלחוטי)
<!-- @device:halo_box,halo,stx,krk -->
- [אופציונלי] NPU מסוג AMD XDNA 2 (סדרת Ryzen AI 300/400/Max 300 או Z2 Extreme) עם מנהל ההתקן העדכני ביותר מותקן מתוך [הוראות התקנת Ryzen AI Software](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) אם ברצונך להריץ מודל על ה-NPU.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade-models-gemma-4-e2b,lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
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

לפני שנריץ מודל, כדאי להבין *מדוע* הדברים מוגדרים כך. Lemonade הוא **שרת מודלים מקומי**, תהליך שטוען מודלי AI לזיכרון וחושף אותם לאפליקציות דרך HTTP, בדיוק כפי ששירות AI בענן היה עושה.

### למה צריך שרת?

| יתרון | מה זה אומר עבורך |
|---------|----------------------|
| **אינטגרציה פשוטה יותר** | אפליקציות מתקשרות עם API אחד מבוסס HTTP במקום להתמודד עם ספריות C++ או Python ספציפיות לחומרה. |
| **מודלים משותפים** | מודל יחיד שנטען יכול לשרת מספר אפליקציות בו-זמנית, ללא עותקים כפולים שצורכים את ה-RAM שלך. |
| **ניידות מענן למקומי** | קוד שנכתב עבור ה-API הענני של OpenAI עובד עם Lemonade פשוט על ידי שינוי כתובת URL אחת. |
| **הפרדת אחריות** | ניהול מודלים, הזרמה (streaming) וסבילות לתקלות מנוהלים על ידי השרת, כך שהמפתחים יכולים להתמקד באפליקציה שלהם. |

### תקן ה-API של OpenAI

Lemonade מממש את **ה-API של OpenAI**, אותו ממשק המשמש את ChatGPT, Azure OpenAI ועשרות שירותים נוספים. מודל השיחה פשוט:

| תפקיד | מי מדבר |
|------|---------------|
| **system** | הוראות למודל (אופי, מגבלות, כלים זמינים) |
| **user** | הודעות מהאדם (או מהאפליקציה) אל המודל |
| **assistant** | תגובות שנוצרות על ידי המודל |

המשמעות היא שכל ספרייה או אפליקציה התומכת ב-OpenAI יכולה לדבר עם Lemonade פשוט על ידי הפניה אל `http://localhost:13305/api/v1` בזמן ש-Lemonade Server פועל.

## פעילות ראשית — שיחת ה-AI המקומית הראשונה שלך

בואו נוריד LLM ונקיים איתו שיחה, תוך הרצת ה-AI כולו על המחשב שלך בלבד.

### שלב 1: הורדה והרצה של מודל

Lemonade מגיע עם ספריית מודלים אוצרת. נתחיל עם **Gemma-4-E2B-it**, מודל קומפקטי ומוכשר הכולל גם תמיכה בראייה (vision). פתחו מסוף (terminal) והריצו:

```
lemonade run Gemma-4-E2B-it-GGUF
```

פקודה בודדת זו עושה שלושה דברים:

1. **מורידה** את המודל (~3 GB) מ-Hugging Face, אם הוא עדיין לא הורד. (עשויה לקחת זמן מה)
2. **מפעילה** את תהליך Lemonade Server ביציאה 13305.
3. **פותחת** את Lemonade App כדי שתוכלו להתחיל לשוחח עם המודל.
<!-- @os:windows -->
בוויندוס, אפליקציית Lemonade App מופעלת אוטומטית וניתן להתחיל לשוחח מיד. אם התקנתם את החבילה `minimal.msi`, האפליקציה אינה כלולה. כדי להתחיל לשוחח, פתחו את דפדפן האינטרנט שלכם ועברו אל `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
ב-Linux, פתחו את הדפדפן שלכם ונווטו אל `http://localhost:13305` כדי לגשת לאפליקציית האינטרנט.
<!-- @os:end -->
「נסה להקליד שאלה:」

```
What are three fun facts about lemons?
```

התגובה של המודל תוצג ישירות בחלון הצ'אט. **ברכותינו! אתם מריצים כעת מודל שפה גדול באופן מקומי.**

![Lemonade App with Logs displayed](../../dependencies/assets/ChatwithLogs.png)

בחלונית Server Logs באפליקציית Lemonade App, ניתן למצוא נתוני טלמטריה על ביצועי המודל לאחר כל תגובה. לדוגמה:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### שלב 2: גלו את ממשק הווב ואת המודליות השונות

Lemonade כוללת ממשק ווב מובנה שבו תוכלו:

- **לתקשר** עם המודל הטעון בחלון צ'אט מוכר
- **לעיין במודלים** בכרטיסייה Model Manager
- **להוריד מודלים חדשים** בלחיצה אחת

נסו לעבור בין מודליות שונות באמצעות הכרטיסייה **Model Manager** בממשק הווב, שבה תוכלו לעיין במודלים לפי Recipe או לפי Category:

1. **ראייה (Vision):** המודל `Gemma-4-E2B-it-GGUF` שכבר טעון אצלכם תומך בראייה. הדביקו תמונה בתיבת הצ'אט ובקשו מהמודל לתאר אותה.
2. **יצירת תמונות:** בקטגוריית Image, הורידו מודל יצירת תמונות כגון `SDXL-Turbo` מה-Model Manager, ולאחר מכן השתמשו ב-Lemonade Image Generator כדי להקליד פרומפט וליצור תמונה באופן מקומי.
3. **אודיו:** בקטגוריית Audio, הורידו מודל אודיו כגון `Whisper-Tiny`, שיכול לבצע המרת דיבור לטקסט. ספקו הקלטת אודיו כדי לתמלל אותה באופן מקומי. עבור המרת טקסט לדיבור, נסו אחד מהמודלים בקטגוריית Speech, כגון `kokoro-v1`.

![מולטי-מודליות עם Lemonade](../../dependencies/assets/multi_modality.png)

### שלב 3: נסו מודל עם backend אחר

אם תעבירו את העכבר מעל מודל באפליקציית Lemonade, תראו סמל גלגל שיניים. לחיצה עליו מאפשרת לכם לבחור אפשרויות עבור המודל, כולל בחירת ה-backend הרצוי לכם.

כברירת מחדל, Lemonade משתמשת ב-Vulkan עבור האצת GPU. אם יש לכם GPU נפרד של AMD נתמך, תוכלו לעבור ל-ROCm.

![בחירת Backend ב-Lemonade](../../dependencies/assets/lemonademodeloptions.png)

כדי לנהל את ה-backends המותקנים שלכם, לחצו על כפתור ה-backend בעמודה השמאלית ביותר.

לחלופין, תוכלו לציין את ה-backend באמצעות הפקודה הבאה:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

תוכלו גם להגדיר את ה-backend המחדלי שלכם באמצעות משתנה הסביבה `LEMONADE_LLAMACPP` עם הערכים: `vulkan`, `rocm`, או `cpu`.

---

## צוללים לעומק — בנו אפליקציית AI עם Python

העוצמה האמיתית של שרת AI מקומי היא שכל אפליקציה יכולה להתחבר אליו באמצעות מספר שורות קוד בלבד. כדי להוכיח זאת, בואו נבנה **מחולל כרטיסיות לימוד (flashcards)** קטן אך פונקציונלי, שבו תיתנו לו נושא, הוא ייצור כרטיסיות, ותוכלו לבחון את עצמכם באופן אינטראקטיבי.

### שלב 4: הפעלת השרת

ודאו ששרת Lemonade פועל. בדרך כלל הוא מופעל אוטומטית ברקע לאחר ההתקנה. כדי לוודא זאת, הריצו:

```
lemonade status
```

אמורה להופיע הודעה כגון: `Server is running on port 13305`.

אם השרת אינו פועל, הפעילו אותו על ידי פתיחת אפליקציית Lemonade. השתמשו בפורט ברירת המחדל **13305** (ניתן לאשר או לבחור זאת מסמל מגש המערכת).

### שלב 5: התקנת לקוח ה-OpenAI Python

בטרמינל, צרו venv והתקינו את לקוח ה-OpenAI Python באמצעות הפקודות הבאות:
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

תוכלו להוריד אותו מה-UI או להריץ את הפקודה הבאה:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

הזינו את הפרומפט הבא לתוך Lemonade Chat UI כדי ליצור קוד עבור אפליקציית Flashcard פשוטה.

נשתמש ב-Qwen3.5-35B-A3B-GGUF (מודל גדול יותר שטוב יותר בכתיבת קוד) כדי ליצור את אפליקציית ה-Python שלנו, והאפליקציה עצמה תקרא בזמן ריצה ל-Gemma-4-E2B-it-GGUF (המודל הקטן יותר שכבר הורדתם). לאחר מכן ניתן להעתיק את הקוד לקובץ לבחירתכם כדי להריץ אותו ב-Python.

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

> **טיפ**: עקבנו אחר נהלי הנדסה סטנדרטיים באמצעות יצירת פרומפטים יסודית ושימוש במערכת דו-מודלית כדי לייעל משאבים ומהירות.

לנוחיותכם, סיפקנו פלט לדוגמה ב-[`flashcards.py`](assets/flashcards.py). מוזמנים להוריד אותו לתיקייה שלכם. כך או כך, כעת אמור להיות ברשותכם קובץ Python שניתן להריץ.

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


### שלב 7: הריצו את הקוד שנוצר

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**כך זה אמור להיראות:**

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

בכ-150 שורות קוד בניתם כלי לימוד מתפקד במלואו המופעל על ידי LLM מקומי. אין מפתח API לנהל, אין עלויות שימוש, ושום נתון לא יוצא מהמחשב שלכם.

> **תובנה מרכזית:** שימו לב ששורת `client = OpenAI(base_url=...) ` היא הדבר *היחיד* המקשר את האפליקציה הזו ל-Lemonade במקום לענן של OpenAI. שאר הקוד זהה לחלוטין לקוד שהייתם כותבים מול כל שירות תואם OpenAI. אם אי פעם השתמשתם בספריית Python של OpenAI, אתם כבר יודעים לבנות אפליקציות עם Lemonade.

### מה זה מדגים

האפליקציה הקטנה הזו מתרגלת מספר דפוסי שילוב מהעולם האמיתי:

| דפוס | היכן הוא מופיע |
|---------|-----------------|
| **פרומפטים של מערכת** | הודעת ה-`"system"` מנחה את ה-LLM לפלוט JSON מובנה |
| **פלט מובנה** | האפליקציה מפרשת את תגובת ה-LLM כ-JSON כדי לבנות כרטיסיות |
| **בקשות חסרות מצב** | כל קריאה ל-`generate_flashcards()` היא עצמאית |
| **טיפול בשגיאות** | ה-`try/except` מטפל בחן במקרים שבהם פלט ה-LLM אינו JSON תקין |

אותם דפוסים בדיוק מתרחבים לכל אפליקציה כגון צ'אטבוטים, עוזרי קוד, מחוללי תוכן, כלי אוטומציה.

#### אתגר בונוס

* לאתגר נוסף, נסו לעדכן את האפליקציה כך שהכרטיסיות יוקראו למשתמש, בהתבסס על הדוגמה המסופקת [כאן](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## הרצת מודלים על ה-NPU (אופציונלי)

אם ברשותכם Ryzen AI 300/400/Max 300 series או Z2 Extreme, במכשיר שלכם מובנה **יחידת עיבוד נוירונית (NPU)**, שבב ייעודי שתוכנן במיוחד לעומסי עבודה של AI. הרצת מודלים על ה-NPU חסכונית יותר באנרגיה מאשר שימוש ב-GPU, מה שהופך אותה לאידיאלית למשימות AI ברקע, להפעלות ארוכות ולשימוש מבוסס סוללה.

Lemonade תומך בשלושה מצבי הרצה של NPU, כולם שקופים מאחורי אותו OpenAI API:

| מצב | איך זה עובד | מתכון | דוגמאות למודלים |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | ה-NPU מעבד את ההנחיה (prompt), ה-iGPU מייצר את הטוקנים | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU-only** | כל תהליך ההסקה (inference) רץ על ה-NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | משתמש במנוע FastFlowLM על ה-NPU, מותאם ל-AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### דרישות

- מעבד **AMD Ryzen AI 300/400 series או Z2 series**
- עבור מודלי **FLM**: ניתן להתקין את זמן הריצה של FLM מתוך אפליקציית Lemonade, או ש-Lemonade יתקין אותו אוטומטית בעת הרצת מודל FLM. למידע נוסף על FastFlowLM, ראו [כאן](https://fastflowlm.com/docs/).


### שלב 8: הרצת מודל Hybrid

מודלי Hybrid מחלקים את העבודה בין ה-NPU וה-iGPU לאיזון טוב בין מהירות ויעילות. באפליקציית Lemonade, בחרו מודל מתוך הרשימה `Ryzen AI LLM`, לדוגמה `Qwen3-4B-Hybrid`, או הריצו אותו באמצעות הפקודה הבאה:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade מזהה את ה-NPU שלכם אוטומטית ומתקין את תשתית ה-**Ryzen AI LLM**.

> **מה קורה מאחורי הקלעים?** כאשר אתם שולחים הודעה, ה-NPU מעבד את כל ההנחיה שלכם במקביל (זה נקרא "prefill"). לאחר מכן, ה-iGPU לוקח את ההובלה כדי לייצר את התשובה טוקן אחר טוקן (זה נקרא "decode"). גישת hybrid זו מנצלת את היתרונות של כל שבב.

### שלב 9: הרצת מודל FLM

מודלי FastFlowLM (FLM) מותאמים במיוחד לארכיטקטורת ה-NPU מסוג XDNA2 של AMD ויכולים להיות מהירים מאוד ביחס לגודלם. לדוגמה, בחרו `qwen3.5-4b-FLM` מתוך הרשימה `FastFlowLM NPU` או השתמשו בפקודה הבאה:

<!-- @os:windows -->
כדי להפעיל את `FastFlowLM` ב-Windows:

* פתחו את התפריט `Backends Manager`.
* אתרו את קטגוריית התשתית `FastFlowLM NPU`.
* לחצו על Install NPU.
* לאחר השלמת ההתקנה, כ-36 מודלים ברירת מחדל יהיו זמינים תחת תפריט ה-FFLM הנפתח.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
כאשר האפליקציה `Lemonade` מופעלת בפעם הראשונה, תשתית ה-`FastFlowNPU` אינה מופעלת כברירת מחדל.
האפליקציה המקומית תפתח את דף ההתקנה כדי להדריך אתכם בתהליך ההגדרה.

כדי להפעיל את `FastFlowLM` ב-Linux:

* פתחו את האפליקציה `Lemonade`.
* בקרו בתיעוד [official FLM](https://lemonade-server.ai/flm_npu_linux.html) ועקבו אחר שלבי ההתקנה עבור FLM על ידי בחירת הפצת ה-Linux שלכם.
* הפעילו backports כפי שמוסבר בדף ההתקנה.
* הורידו את גרסת ה-`v0.9.x` העדכנית ביותר מ-[tags page](https://github.com/FastFlowLM/FastFlowLM/tags).

<!-- @device:halo_box -->
>[!Note]
עבור AMD Halo Developer Platform, ודאו לבחור Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* התקינו את חבילת ה-`.deb` שהורדתם.
* מומלץ: צאו מהאפליקציה `Lemonade App` ופתחו אותה מחדש כדי שהשינויים יזוהו.
* מומלץ: פתחו את `Backends Manager` ולחצו על Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
לאחר התקנה מוצלחת, אמורים לראות ש-`flm:npu` הושלם ב-**Download Manager** בתוך **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
לאחר מכן תוכלו לבחור כל אחד מהמודלים הזמינים של FFLM ולהתחיל להשתמש בתשתית ה-NPU.

עבור מודל ספציפי, הורידו את המודל הרצוי מ-[models page](https://fastflowlm.com/docs/models/qwen/) ואמתו אותו באמצעות פקודת ה-Shell המסופקת בתיעוד.
```
flm run qwen3.5-4b-FLM
```
או באמצעות 
```
lemonade run qwen3.5-4b-FLM
```

מודלי FLM כוללים כמה מהארכיטקטורות הפופולריות ביותר (Gemma 3, Qwen 3, Llama 3, ו-DeepSeek R1) ונעים בין פחות מ-1GB ליותר מ-13GB.
Lemonade מזהה את ה-NPU שלכם אוטומטית ומתקין את תשתית ה-**FastFlowLM NPU**.

<!-- @os:windows -->
> **טיפ:** לביצועי NPU מיטביים, הפעילו מצב turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### החלפת מודלים

אפליקציית כרטיסי הלימוד משלב 6 עובדת גם עם מודלי NPU, פשוט שנו את שם המודל:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## הצעדים הבאים

כעת יש לכם שרת AI מקומי הפועל על החומרה שלכם, הנה לאן להמשיך מכאן:

1. **חברו את האפליקציות האהובות עליכם**: Lemonade עובד ישירות מהקופסה עם [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/), ו[עוד רבים נוספים](https://lemonade-server.ai/marketplace).

2. **עיינו במודלים נוספים**: חקרו את [ספריית המודלים](https://lemonade-server.ai/docs/server/server_models/) המלאה כדי למצוא מודלים המותאמים לקידוד, להיסק (reasoning), לראייה ועוד. השתמשו באפליקציית Lemonade או ב-`lemonade list` כדי לראות מה זמין.

3. **שחררו את האצת ה-GPU של ROCm**: אם ברשותכם GPU נתמך של AMD, עברו לתשתית ROCm: `lemonade config set llamacpp.backend=rocm`. ראו [GPUs נתמכים של AMD](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **קראו את מפרט ה-API המלא**: Lemonade תומך בהשלמות צ'אט, embeddings, תמלול אודיו, יצירת תמונות, המרת טקסט לדיבור ועוד. ראו את [מפרט השרת](https://lemonade-server.ai/docs/server/server_spec/) לכל נקודת קצה.

5. **תרמו**: Lemonade הוא קוד פתוח. עיינו ב[מדריך התרומה](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) וחפשו [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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