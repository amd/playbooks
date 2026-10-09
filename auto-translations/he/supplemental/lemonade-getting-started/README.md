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

🍋 **Lemonade** הוא שרת AI מקומי בקוד פתוח המאפשר להריץ מודלים גדולים של שפה (LLMs), מחוללי תמונות ומודלים קוליים ישירות על החומרה שלך. הוא חושף את המודלים דרך **OpenAI API** התקני בתעשייה, כך שכל אפליקציה שעובדת עם OpenAI יכולה לעבוד באופן מיידי עם Lemonade. בסוף המדריך הזה, תשתמש ב-Lemonade כדי להריץ מודלים מקומית על המחשב שלך.

## מה תלמד

בסוף המדריך הזה תוכל:

* **להתקין את Lemonade Server** ולוודא שהוא פועל.
* **להוריד ולשוחח עם LLM** באמצעות פקודה אחת בלבד.
* **לחקור את ממשק ה-web** ולנסות מודאליות שונות כגון ראייה, המרת דיבור לטקסט ויצירת תמונות.
* **להחליף בין backend-ים של GPU** בין Vulkan לתוכנת AMD ROCm™.
* **לבנות אפליקציית Python** המופעלת על ידי LLM מקומי באמצעות ה-API התואם ל-OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **להריץ מודלים על ה-Neural Processing Unit (NPU) של AMD** באמצעות מצבי הרצה Hybrid ו-FLM על חומרת AMD Ryzen™ AI.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות התוכנה המקדימות

לפני שתתחיל, ודא שיש לך:

- מחשב המריץ **Windows 11** או הפצת **Linux** נתמכת (Ubuntu 24.04+, Fedora, Debian)
- מומלצים **16 GB של RAM** עבור מודל ה-runtime המשמש בשלבים 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). מומלצים **32 GB+** אם ברצונך להשתמש במודל יצירת הקוד הגדול יותר בשלב 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB של שטח פנוי בדיסק**, בהתאם למודלים שתוריד. המודל הגדול ביותר במדריך זה הוא כ-20 GB.
- **Python 3.10–3.13** (בשימוש בחלק האפליקציית Python)
- חיבור לאינטרנט (קווי או אלחוטי)
<!-- @device:halo_box,halo,stx,krk -->
- [אופציונלי] NPU מסוג AMD XDNA 2 (סדרת Ryzen AI 300/400/Max 300 או Z2 Extreme) עם הדרייבר העדכני ביותר מותקן מתוך [הוראות התקנת תוכנת Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) אם ברצונך להריץ מודל על ה-NPU.
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
<!-- @test:id=lemonade-update-linux timeout=300 hidden=True -->
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

## מושגי יסוד — כיצד שרתי AI מקומיים פועלים

לפני שנריץ מודל, כדאי להבין *מדוע* הדברים מוגדרים בצורה זו. Lemonade הוא **שרת מודלים מקומי**, תהליך שטוען מודלים של AI לזיכרון וחושף אותם לאפליקציות דרך HTTP, בדיוק כפי ששירות AI בענן היה עושה.

### למה שרת?

| יתרון | מה זה אומר עבורך |
|---------|----------------------|
| **אינטגרציה פשוטה** | אפליקציות מתקשרות עם API אחד של HTTP במקום להתמודד עם ספריות C++ או Python ספציפיות לחומרה. |
| **מודלים משותפים** | מודל טעון אחד יכול לשרת מספר אפליקציות בו-זמנית, ללא עותקים כפולים שצורכים את ה-RAM שלך. |
| **ניידות מענן למקומי** | קוד שנכתב עבור ה-API הענני של OpenAI עובד עם Lemonade על ידי שינוי כתובת URL אחת. |
| **הפרדת אחריות** | ניהול מודלים, הזרמה (streaming) וסבילות לתקלות מנוהלים על ידי השרת כך שהמפתחים יכולים להתמקד באפליקציה שלהם. |

### תקן ה-OpenAI API

Lemonade מיישם את **OpenAI API**, אותו ממשק המשמש את ChatGPT, Azure OpenAI ועשרות שירותים נוספים. מודל השיחה פשוט:

| תפקיד | מי מדבר |
|------|---------------|
| **system** | הוראות למודל (דמות, אילוצים, כלים זמינים) |
| **user** | הודעות מהאדם (או מהאפליקציה) אל המודל |
| **assistant** | תגובות שנוצרו על ידי המודל |

המשמעות היא שכל ספרייה או אפליקציה שתומכת ב-OpenAI יכולה לתקשר עם Lemonade על ידי הפניה אל `http://localhost:13305/api/v1` בזמן ש-Lemonade Server פועל.

## פעילות עיקרית — צ'אט ה-AI המקומי הראשון שלך

בוא נוריד LLM ונשוחח איתו, כשה-AI פועל כולו על המחשב שלך.

### שלב 1: הורדה והרצה של מודל

Lemonade מגיע עם ספריית מודלים מתוכננת. נתחיל עם **Gemma-4-E2B-it**, מודל יעיל וקומפקטי הכולל תמיכה בראייה. פתח מסוף והרץ:

```
lemonade run Gemma-4-E2B-it-GGUF
```

פקודה בודדת זו עושה שלושה דברים:

1. **מורידה** את המודל (~3 GB) מ-Hugging Face, אם הוא עדיין לא הורד. (עשוי לקחת זמן מה)
2. **מפעילה** את תהליך Lemonade Server על פורט 13305.
3. **פותחת** את Lemonade App כדי שתוכל להתחיל לשוחח עם המודל.


<!-- @os:windows -->
ב-Windows, Lemonade App נפתח אוטומטית ותוכל להתחיל לשוחח מיד. אם התקנת את חבילת `minimal.msi`, האפליקציה אינה כלולה. כדי להתחיל לשוחח, פתח את דפדפן האינטרנט שלך ועבור אל `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
ב-Linux, פתח את הדפדפן שלך ונווט אל `http://localhost:13305` כדי לגשת לאפליקציית ה-web.
<!-- @os:end -->

נסה להקליד שאלה:

```
What are three fun facts about lemons?
```

המודל יגיב ישירות בחלון הצ'אט. **כל הכבוד! אתה מריץ מודל שפה גדול באופן מקומי.**

![Lemonade App עם יומנים מוצגים](../../dependencies/assets/ChatwithLogs.png)

בחלונית Server Logs באפליקציית Lemonade, תוכל למצוא נתוני טלמטריה אודות ביצועי המודל לאחר כל תגובה. לדוגמה:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### שלב 2: גלו את ממשק האינטרנט ואת המודאליות השונות

Lemonade כולל ממשק אינטרנט מובנה שבו תוכלו:

- **לתקשר** עם המודל הטעון בחלון צ'אט מוכר
- **לעיין במודלים** בכרטיסייה Model Manager
- **להוריד מודלים חדשים** בלחיצה אחת

נסו לעבור בין מודאליות שונות באמצעות הכרטיסייה **Model Manager** בממשק האינטרנט, שבה תוכלו לעיין במודלים לפי Recipe או לפי Category:

1. **ראייה (Vision):** המודל `Gemma-4-E2B-it-GGUF` שכבר טענתם תומך בראייה. הדביקו תמונה לתוך תיבת הצ'אט ובקשו מהמודל לתאר אותה.
2. **יצירת תמונות:** בקטגוריית Image, הורידו מודל ליצירת תמונות כגון `SDXL-Turbo` מה-Model Manager, ולאחר מכן השתמשו ב-Lemonade Image Generator כדי להקליד הנחיה וליצור תמונה באופן מקומי.
3. **אודיו:** בקטגוריית Audio, הורידו מודל אודיו כגון `Whisper-Tiny`, שיכול לבצע המרת דיבור לטקסט. ספקו הקלטת אודיו כדי לתמלל אותה באופן מקומי. עבור המרת טקסט לדיבור, נסו אחד מהמודלים בקטגוריית Speech, כגון `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### שלב 3: נסו מודל עם Backend שונה

אם תעבירו את העכבר מעל מודל באפליקציית Lemonade, תראו סמל גלגל שיניים. לחיצה עליו מאפשרת לבחור אפשרויות עבור המודל, כולל בחירת ה-Backend הרצוי.

כברירת מחדל, Lemonade משתמש ב-Vulkan להאצת GPU. אם יש לכם GPU נפרד נתמך של AMD, תוכלו לעבור ל-ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

כדי לנהל את ה-Backends המותקנים שלכם, לחצו על כפתור ה-Backend בעמודה השמאלית ביותר.

לחלופין, תוכלו לציין את ה-Backend באמצעות הפקודה הבאה:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

תוכלו גם להגדיר את ה-Backend המוגדר כברירת מחדל שלכם באמצעות משתנה הסביבה `LEMONADE_LLAMACPP` עם הערכים: `vulkan`, `rocm`, או `cpu`.

---

## צלילה עמוקה יותר — בניית אפליקציית AI עם Python

הכוח האמיתי של שרת AI מקומי הוא שכל אפליקציה יכולה להתחבר אליו באמצעות מספר שורות קוד בלבד. כדי להוכיח זאת, בואו נבנה **מחולל כרטיסיות לימוד (flashcard)** קטן אך פונקציונלי, שבו תיתנו לו נושא, הוא ייצור כרטיסיות לימוד, ותוכלו לבחון את עצמכם באופן אינטראקטיבי.

### שלב 4: הפעלת השרת

ודאו שהשרת של Lemonade פועל. הוא בדרך כלל מופעל אוטומטית ברקע לאחר ההתקנה. כדי לוודא זאת, הריצו:

```
lemonade status
```

אתם אמורים לראות הודעה כמו: `Server is running on port 13305`.

אם השרת אינו פועל, הפעילו אותו על ידי פתיחת אפליקציית Lemonade. השתמשו בפורט ברירת המחדל **13305** (תוכלו לאשר או לבחור זאת מסמל מגש המערכת).

### שלב 5: התקנת OpenAI Python Client

בטרמינל, צרו venv והתקינו את OpenAI Python Client באמצעות הפקודות הבאות:
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

בואו נוריד מודל אחר ליצירת קוד: `Qwen3.5-35B-A3B-GGUF`. זהו מודל גדול (כ-20 GB) ועתיר ביצועים, המתאים ביותר למערכות עם 32GB+ של RAM. אם יש לכם פחות RAM זמין, נסו במקום זאת את `Qwen3.5-9B-GGUF` (כ-6 GB).

תוכלו להוריד אותו מהממשק או להריץ את הפקודה הבאה:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

הזינו את ההנחיה הבאה לתוך ממשק הצ'אט של Lemonade כדי ליצור קוד לאפליקציית כרטיסיות פשוטה.

נשתמש ב-Qwen3.5-35B-A3B-GGUF (מודל גדול יותר שטוב יותר בכתיבת קוד) כדי ליצור את אפליקציית ה-Python שלנו, והאפליקציה עצמה תקרא ל-Gemma-4-E2B-it-GGUF (המודל הקטן יותר שכבר הורדתם) בזמן ריצה. ניתן אז להעתיק את הקוד לקובץ לבחירתכם כדי להריץ אותו ב-Python.

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

> **טיפ**: עקבנו אחר נהלי הנדסה סטנדרטיים באמצעות יצירת הנחיות יסודית ושימוש במערכת דו-מודלית כדי לייעל משאבים ומהירות.

לנוחיותכם, סיפקנו פלט לדוגמה בקובץ [`flashcards.py`](assets/flashcards.py). מוזמנים להוריד אותו לתיקייה שלכם. בכל מקרה, אתם אמורים כעת לקבל קובץ Python שניתן להריץ.

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

בכ-150 שורות קוד בניתם כלי לימוד פונקציונלי לחלוטין המופעל על ידי LLM מקומי. אין מפתח API לנהל, אין עלויות שימוש, ושום נתון לא עוזב את המכשיר שלכם.

> **תובנה מרכזית:** שימו לב שהשורה `client = OpenAI(base_url=...) ` היא הדבר *היחיד* המקשר את האפליקציה הזו ל-Lemonade במקום לענן של OpenAI. שאר הקוד זהה למה שהייתם כותבים מול כל שירות תואם OpenAI. אם אי פעם השתמשתם בספריית OpenAI Python, אתם כבר יודעים כיצד לבנות אפליקציות עם Lemonade.

### מה זה ממחיש

אפליקציה קטנה זו מדגימה כמה דפוסי שילוב מהעולם האמיתי:

| דפוס | היכן הוא מופיע |
|---------|-----------------|
| **הנחיות מערכת (System prompts)** | ההודעה `"system"` מורה ל-LLM להפיק JSON מובנה |
| **פלט מובנה** | האפליקציה מפרשת את תגובת ה-LLM כ-JSON כדי לבנות כרטיסיות |
| **בקשות חסרות מצב (Stateless)** | כל קריאה ל-`generate_flashcards()` היא עצמאית |
| **טיפול בשגיאות** | ה-`try/except` מטפל בחן במקרים שבהם פלט ה-LLM אינו JSON תקין |

דפוסים אלה ניתנים להרחבה לכל אפליקציה כגון צ'אטבוטים, עוזרי קוד, מחוללי תוכן, כלי אוטומציה.

#### אתגר בונוס

* לאתגר נוסף, נסו לעדכן את האפליקציה כך שהכרטיסיות יוקראו למשתמש על ידי התייחסות לדוגמה המסופקת [כאן](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
# הרצת מודלים על ה-NPU (אופציונלי)

אם ברשותכם מכשיר מסדרת Ryzen AI 300/400/Max 300 או Z2 Extreme, המכשיר שלכם כולל שבב ייעודי בשם **יחידת עיבוד נוירונית (NPU)**, שבב מובנה שתוכנן במיוחד עבור עומסי עבודה של AI. הרצת מודלים על ה-NPU חסכונית יותר באנרגיה בהשוואה לשימוש ב-GPU, מה שהופך אותה לאידיאלית למשימות AI ברקע, לסשנים ארוכים ולשימוש המופעל על סוללה.

Lemonade תומך בשלושה מצבי הרצה על ה-NPU, כולם שקופים מאחורי אותו OpenAI API:

| מצב | איך זה עובד | מתכון | מודלים לדוגמה |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | ה-NPU מעבד את ה-prompt, ה-iGPU מייצר את הטוקנים | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU בלבד** | כל תהליך ההסקה פועל על ה-NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | משתמש במנוע FastFlowLM על ה-NPU, מותאם עבור AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### דרישות

- מעבד **AMD Ryzen AI מסדרה 300/400 או Z2**
- עבור מודלים מסוג **FLM**: ניתן להתקין את סביבת ההרצה (runtime) של FLM מתוך אפליקציית Lemonade, או ש-Lemonade יתקין אותה אוטומטית בעת הרצת מודל FLM. למידע נוסף על FastFlowLM, ראו [כאן](https://fastflowlm.com/docs/).


### שלב 8: הרצת מודל Hybrid

מודלים מסוג Hybrid מחלקים את העבודה בין ה-NPU ל-iGPU כדי להשיג איזון טוב בין מהירות ליעילות. באפליקציית Lemonade, בחרו מודל מהרשימה `Ryzen AI LLM`, לדוגמה `Qwen3-4B-Hybrid`, או הריצו אותו באמצעות הפקודה הבאה:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade מזהה את ה-NPU שלכם אוטומטית ומתקין את ה-backend **Ryzen AI LLM**.

> **מה קורה מאחורי הקלעים?** כאשר אתם שולחים הודעה, ה-NPU מעבד את כל ה-prompt שלכם במקביל (זה נקרא "prefill"). לאחר מכן, ה-iGPU משתלט על התהליך כדי לייצר את התגובה טוקן אחר טוקן (זה נקרא "decode"). גישת ה-Hybrid הזו מנצלת את החוזקות של כל שבב.

### שלב 9: הרצת מודל FLM

מודלי FastFlowLM (FLM) מותאמים במיוחד לארכיטקטורת ה-NPU מסוג XDNA2 של AMD, ויכולים להיות מהירים מאוד ביחס לגודלם. לדוגמה, בחרו `qwen3.5-4b-FLM` מהרשימה `FastFlowLM NPU` או השתמשו בפקודה הבאה:

<!-- @os:windows -->
כדי להפעיל את `FastFlowLM` ב-Windows:

* פתחו את התפריט `Backends Manager`.
* אתרו את קטגוריית ה-backend `FastFlowLM NPU`.
* לחצו על Install NPU.
* לאחר השלמת ההתקנה, כ-36 מודלי ברירת מחדל יהיו זמינים תחת תפריט ה-FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
כאשר אפליקציית `Lemonade` מופעלת בפעם הראשונה, ה-backend `FastFlowNPU` אינו מופעל כברירת מחדל.
האפליקציה המקומית תפתח את דף ההתקנה כדי להדריך אתכם בתהליך ההגדרה.

כדי להפעיל את `FastFlowLM` ב-Linux:

* פתחו את אפליקציית `Lemonade`.
* בקרו בתיעוד ה-[official FLM](https://lemonade-server.ai/flm_npu_linux.html) ועקבו אחר שלבי ההתקנה עבור FLM על ידי בחירת הפצת ה-Linux שלכם.
* הפעילו backports כפי שמוסבר בדף ההתקנה.
* הורידו את הגרסה העדכנית ביותר של `v0.9.x` מ[דף התגיות](https://github.com/FastFlowLM/FastFlowLM/tags).

<!-- @device:halo_box -->
>[!Note]
עבור AMD Halo Developer Platform, ודאו שבחרתם ב-Debian 13.
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
* מומלץ: צאו מאפליקציית `Lemonade App` ופתחו אותה מחדש כדי שהשינויים יזוהו.
* מומלץ: פתחו את `Backends Manager` ולחצו על Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
לאחר התקנה מוצלחת, אמורים לראות ש-`flm:npu` הושלם ב-**Download Manager** בתוך **אפליקציית Lemonade Desktop**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
כעת תוכלו לבחור כל אחד מהמודלים הזמינים מסוג FFLM ולהתחיל להשתמש ב-backend של ה-NPU.

עבור מודל ספציפי, הורידו את המודל הרצוי מ[דף המודלים](https://fastflowlm.com/docs/models/qwen/) ואמתו אותו באמצעות פקודת ה-Shell המופיעה בתיעוד.
```
flm run qwen3.5-4b-FLM
```
או באמצעות 
```
lemonade run qwen3.5-4b-FLM
```

מודלי FLM כוללים כמה מהארכיטקטורות הפופולריות ביותר (Gemma 3, Qwen 3, Llama 3, ו-DeepSeek R1) ונעים בטווח שבין פחות מ-1 GB ועד מעל 13 GB.
Lemonade מזהה את ה-NPU שלכם אוטומטית ומתקין את ה-backend **FastFlowLM NPU**.

<!-- @os:windows -->
> **טיפ:** לקבלת הביצועים הטובים ביותר של ה-NPU, הפעילו מצב turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### מעבר בין מודלים

אפליקציית כרטיסיות הלימוד (flashcard) משלב 6 עובדת גם עם מודלי NPU, פשוט שנו את שם המודל:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## הצעדים הבאים

כעת יש לכם שרת AI מקומי הפועל על החומרה שלכם. הנה לאן כדאי להמשיך משם:

1. **חברו את האפליקציות האהובות עליכם**: Lemonade עובד מיד עם [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/), ו[עוד רבים נוספים](https://lemonade-server.ai/marketplace).

2. **עיינו במודלים נוספים**: חקרו את [ספריית המודלים](https://lemonade-server.ai/docs/server/server_models/) המלאה כדי למצוא מודלים המותאמים לכתיבת קוד, הסקה לוגית, ראייה ממוחשבת ועוד. השתמשו באפליקציית Lemonade או בפקודה `lemonade list` כדי לראות מה זמין.

3. **פתחו את האצת ה-GPU של ROCm**: אם ברשותכם GPU נתמך של AMD, עברו ל-backend של ROCm: `lemonade config set llamacpp.backend=rocm`. ראו [GPUs נתמכים של AMD](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **קראו את מפרט ה-API המלא**: Lemonade תומך בהשלמות צ'אט (chat completions), embeddings, תמלול אודיו, יצירת תמונות, המרת טקסט לדיבור (text-to-speech) ועוד. ראו את [מפרט השרת](https://lemonade-server.ai/docs/server/server_spec/) לכל נקודת קצה (endpoint).

5. **תרמו**: Lemonade הוא קוד פתוח. עיינו ב[מדריך התרומה](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) וחפשו [בעיות מתאימות למתחילים](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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