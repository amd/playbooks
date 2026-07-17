<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> يستخدم هذا الدليل علامات خاصة لا يمكن لـ GitHub عرضها. يرجى زيارة [amd.com/playbooks](https://amd.com/playbooks) لمعاينة هذا المحتوى بشكل صحيح.
<!-- @github-only:end -->

## نظرة عامة

🍋 **Lemonade** هو خادم ذكاء اصطناعي محلي مفتوح المصدر يتيح لك تشغيل نماذج اللغة الكبيرة (LLMs) ومولدات الصور ونماذج الصوت مباشرةً على جهازك الخاص. يعرض النماذج من خلال **OpenAI API** المعياري في الصناعة، بحيث يمكن لأي تطبيق يعمل مع OpenAI أن يعمل فوراً مع Lemonade. بنهاية هذا الدليل، ستكون قادراً على استخدام Lemonade لتشغيل النماذج محلياً على جهازك.

## ما ستتعلمه

بنهاية هذا الدليل ستكون قادراً على:

* **تثبيت Lemonade Server** والتحقق من تشغيله.
* **تنزيل نموذج LLM والتحدث معه** باستخدام أمر واحد.
* **استكشاف واجهة الويب** وتجربة أنماط مختلفة مثل الرؤية والتحويل من كلام إلى نص وتوليد الصور.
* **التبديل بين خلفيات GPU** بين Vulkan وبرنامج AMD ROCm™.
* **بناء تطبيق Python** مدعوم بنموذج LLM محلي باستخدام واجهة برمجة التطبيقات المتوافقة مع OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **تشغيل النماذج على وحدة المعالجة العصبية AMD (NPU)** باستخدام أوضاع تنفيذ Hybrid وFLM على أجهزة AMD Ryzen™ AI.
<!-- @device:end -->

## ضبط تكوين الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرامج

قبل البدء، تأكد من توفر ما يلي:

- جهاز كمبيوتر يعمل بنظام **Windows 11** أو توزيعة **Linux** مدعومة (Ubuntu 24.04+، Fedora، Debian)
- يُوصى بـ **16 جيجابايت من الذاكرة العشوائية (RAM)** للنموذج المستخدم في الخطوات 1–7 (`Gemma-4-E2B-it-GGUF`، ~3 جيجابايت). يُوصى بـ **32 جيجابايت أو أكثر** إذا كنت تريد استخدام نموذج توليد الكود الأكبر في الخطوة 6 (`Qwen3.5-35B-A3B-GGUF`، ~20 جيجابايت).
- **~4–30 جيجابايت من مساحة القرص الحرة**، حسب النماذج التي تقوم بتنزيلها. أكبر نموذج في هذا الدليل يبلغ حجمه حوالي 20 جيجابايت.
- **Python 3.10–3.13** (يُستخدم في قسم تطبيق Python)
- اتصال بالإنترنت (سلكي أو لاسلكي)
<!-- @device:halo_box,halo,stx,krk -->
- [اختياري] NPU من نوع AMD XDNA 2 (سلسلة Ryzen AI 300/400/Max 300 أو Z2 Extreme) مع تثبيت أحدث برنامج تشغيل من [تعليمات تثبيت برنامج Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) إذا كنت تريد تشغيل نموذج على NPU.
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

## المفاهيم الأساسية — كيف تعمل خوادم الذكاء الاصطناعي المحلية

قبل تشغيل نموذج، من المفيد فهم *سبب* إعداد الأمور بهذه الطريقة. Lemonade هو **خادم نماذج محلي**، وهو عملية تحمّل نماذج الذكاء الاصطناعي في الذاكرة وتعرضها للتطبيقات عبر HTTP، تماماً كما تفعل خدمة الذكاء الاصطناعي السحابية.

### لماذا خادم؟

| الفائدة | ما يعنيه ذلك بالنسبة لك |
|---------|----------------------|
| **تكامل مبسّط** | تتحدث التطبيقات إلى واجهة HTTP واحدة بدلاً من التعامل مع مكتبات C++ أو Python خاصة بالأجهزة. |
| **نماذج مشتركة** | يمكن لنموذج واحد محمّل أن يخدم تطبيقات متعددة في آنٍ واحد، دون نسخ مكررة تستهلك ذاكرتك. |
| **قابلية النقل من السحابة إلى المحلي** | الكود المكتوب لواجهة OpenAI السحابية يعمل مع Lemonade بتغيير عنوان URL واحد فقط. |
| **فصل المهام** | تتولى إدارة النماذج والبث والتسامح مع الأخطاء الخادمُ، مما يتيح للمطورين التركيز على تطبيقاتهم. |

### معيار OpenAI API

تُطبّق Lemonade **OpenAI API**، وهي نفس الواجهة التي تستخدمها ChatGPT وAzure OpenAI وعشرات الخدمات الأخرى. نموذج المحادثة بسيط:

| الدور | من يتحدث |
|------|---------------|
| **system** | تعليمات للنموذج (الشخصية، القيود، الأدوات المتاحة) |
| **user** | رسائل من الإنسان (أو التطبيق) إلى النموذج |
| **assistant** | الردود التي يولّدها النموذج |

هذا يعني أن أي مكتبة أو تطبيق يدعم OpenAI يمكنه التحدث إلى Lemonade بتوجيهه إلى `http://localhost:13305/api/v1` أثناء تشغيل Lemonade Server.

## النشاط الرئيسي — أول محادثة ذكاء اصطناعي محلية لك

لنقم بتنزيل نموذج LLM وإجراء محادثة معه، مع تشغيل الذكاء الاصطناعي بالكامل على جهازك الخاص.

### الخطوة 1: تنزيل نموذج وتشغيله

تأتي Lemonade مع مكتبة نماذج منتقاة. لنبدأ بـ **Gemma-4-E2B-it**، وهو نموذج قادر ومدمج يتضمن دعم الرؤية. افتح طرفية ونفّذ:

```
lemonade run Gemma-4-E2B-it-GGUF
```

هذا الأمر الواحد يقوم بثلاثة أشياء:

1. **تنزيل** النموذج (~3 جيجابايت) من Hugging Face، إذا لم يكن محمّلاً مسبقاً. (قد يستغرق بعض الوقت)
2. **تشغيل** عملية Lemonade Server على المنفذ 13305.
3. **فتح Lemonade App** حتى تتمكن من بدء المحادثة مع النموذج.


<!-- @os:windows -->
على Windows، يُشغَّل Lemonade App تلقائياً ويمكنك البدء في المحادثة فوراً. إذا قمت بتثبيت حزمة `minimal.msi`، فإن التطبيق غير مضمّن. لبدء المحادثة، افتح متصفح الويب وانتقل إلى `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
على Linux، افتح متصفحك وانتقل إلى `http://localhost:13305` للوصول إلى تطبيق الويب.
<!-- @os:end -->

جرّب كتابة سؤال:

```
What are three fun facts about lemons?
```

سيرد النموذج مباشرةً في نافذة المحادثة. **تهانينا! أنت تشغّل نموذج لغة كبيراً محلياً.**

![Lemonade App مع عرض السجلات](../../dependencies/assets/ChatwithLogs.png)

في لوحة سجلات الخادم في Lemonade App، يمكنك العثور على بيانات القياس عن أداء النموذج بعد كل رد. على سبيل المثال:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```
### الخطوة 2: استكشاف واجهة الويب والأنماط المختلفة

يتضمن Lemonade واجهة ويب مدمجة حيث يمكنك:

- **التفاعل** مع النموذج المحمّل في نافذة دردشة مألوفة
- **تصفح النماذج** في تبويب Model Manager
- **تنزيل نماذج جديدة** بنقرة واحدة

جرّب التبديل بين الأنماط المختلفة باستخدام تبويب **Model Manager** في واجهة الويب، حيث يمكنك تصفح النماذج حسب الوصفة أو حسب الفئة:

1. **الرؤية:** نموذج `Gemma-4-E2B-it-GGUF` الذي قمت بتحميله بالفعل يدعم الرؤية. الصق صورة في مربع الدردشة واطلب من النموذج وصفها.
2. **توليد الصور:** في فئة الصور، قم بتنزيل نموذج صور مثل `SDXL-Turbo` من Model Manager، ثم استخدم Lemonade Image Generator لكتابة موجّه وتوليد صورة محلياً.
3. **الصوت:** في فئة الصوت، قم بتنزيل نموذج صوتي مثل `Whisper-Tiny`، الذي يمكنه تحويل الكلام إلى نص. قدّم تسجيلاً صوتياً لنسخه محلياً. لتحويل النص إلى كلام، جرّب أحد النماذج في فئة Speech، مثل `kokoro-v1`.

![تعدد الأنماط مع Lemonade](../../dependencies/assets/multi_modality.png)

### الخطوة 3: تجربة نموذج بواجهة خلفية مختلفة

إذا مررت بالمؤشر فوق نموذج في تطبيق Lemonade، ستظهر لك أيقونة الترس. النقر عليها يتيح لك تحديد خيارات النموذج، بما في ذلك اختيار الواجهة الخلفية المطلوبة.

بشكل افتراضي، يستخدم Lemonade Vulkan لتسريع GPU. إذا كان لديك GPU منفصل من AMD مدعوم، يمكنك التبديل إلى ROCm.

![اختيار الواجهة الخلفية في Lemonade](../../dependencies/assets/lemonademodeloptions.png)

لإدارة الواجهات الخلفية المثبتة لديك، انقر على زر الواجهة الخلفية في العمود الأيسر.

بدلاً من ذلك، يمكنك تحديد الواجهة الخلفية باستخدام الأمر التالي:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

يمكنك أيضاً تعيين الواجهة الخلفية الافتراضية باستخدام متغير البيئة `LEMONADE_LLAMACPP` بالقيم: `vulkan` أو `rocm` أو `cpu`.

---

## التعمق أكثر — بناء تطبيق مدعوم بالذكاء الاصطناعي باستخدام Python

القوة الحقيقية لخادم الذكاء الاصطناعي المحلي هي أن أي تطبيق يمكنه الاتصال به باستخدام بضعة أسطر من الكود فقط. لإثبات ذلك، لنبنِ **مولّد بطاقات دراسية** صغيراً لكنه وظيفي، حيث تعطيه موضوعاً فيولّد بطاقات دراسية ويمكنك اختبار نفسك بشكل تفاعلي.

### الخطوة 4: تشغيل الخادم

تحقق من أن خادم Lemonade يعمل. عادةً ما يبدأ تلقائياً في الخلفية بعد التثبيت. للتحقق، شغّل:

```
lemonade status
```

يجب أن ترى رسالة مثل: `Server is running on port 13305`.

إذا لم يكن الخادم يعمل، ابدأ تشغيله بفتح تطبيق Lemonade. استخدم المنفذ الافتراضي **13305** (يمكنك تأكيده أو تحديده من أيقونة علبة النظام).

### الخطوة 5: تثبيت عميل OpenAI Python

في الطرفية، أنشئ بيئة venv وثبّت عميل OpenAI Python باستخدام الأوامر التالية:
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

### الخطوة 6: بناء تطبيق البطاقات الدراسية

لنقم بتنزيل نموذج مختلف لتوليد الكود: `Qwen3.5-35B-A3B-GGUF`. هذا نموذج كبير (~20 جيجابايت) وعالي الأداء، وهو الأنسب للأنظمة التي تحتوي على 32 جيجابايت أو أكثر من الذاكرة العشوائية. إذا كانت الذاكرة المتاحة لديك أقل، جرّب `Qwen3.5-9B-GGUF` (~6 جيجابايت) بدلاً من ذلك.

يمكنك تنزيله من واجهة المستخدم أو تشغيل ما يلي:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

أدخل الموجّه التالي في واجهة Lemonade Chat لتوليد كود لتطبيق بطاقات دراسية بسيط.

سنستخدم Qwen3.5-35B-A3B-GGUF (نموذج أكبر وأفضل في كتابة الكود) لتوليد تطبيق Python الخاص بنا، وسيستدعي التطبيق نفسه Gemma-4-E2B-it-GGUF (النموذج الأصغر الذي قمت بتنزيله بالفعل) أثناء التشغيل. يمكن بعد ذلك نسخ الكود إلى ملف من اختيارك لتشغيله في Python.

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

> **نصيحة**: لقد اتبعنا ممارسات هندسية قياسية من خلال إنشاء موجّهات شاملة واستخدام نظام ثنائي النماذج لتحسين الموارد والسرعة.

لراحتك، قدّمنا مخرجات نموذجية في [`flashcards.py`](assets/flashcards.py). لا تتردد في تنزيله إلى مجلدك. في كلتا الحالتين، يجب أن يكون لديك الآن ملف Python جاهز للتشغيل.

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


### الخطوة 7: تشغيل الكود المولَّد

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**إليك ما يجب أن تراه:**

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

في حوالي 150 سطراً من الكود، قمت ببناء أداة دراسة وظيفية بالكامل مدعومة بنموذج لغوي محلي. لا يوجد مفتاح API لإدارته، ولا تكاليف استخدام، ولا بيانات تغادر جهازك أبداً.

> **رؤية أساسية:** لاحظ أن السطر `client = OpenAI(base_url=...) ` هو *الشيء الوحيد* الذي يربط هذا التطبيق بـ Lemonade بدلاً من سحابة OpenAI. بقية الكود مطابق لما ستكتبه مقابل أي خدمة متوافقة مع OpenAI. إذا سبق لك استخدام مكتبة OpenAI Python، فأنت تعرف بالفعل كيفية بناء تطبيقات مع Lemonade.

### ما يُظهره هذا

يمارس هذا التطبيق الصغير عدة أنماط تكامل واقعية:

| النمط | أين يظهر |
|---------|-----------------|
| **موجّهات النظام** | رسالة `"system"` تخبر النموذج اللغوي بإخراج JSON منظّم |
| **المخرجات المنظّمة** | يحلّل التطبيق استجابة النموذج اللغوي بصيغة JSON لبناء البطاقات الدراسية |
| **الطلبات عديمة الحالة** | كل استدعاء لـ `generate_flashcards()` مستقل |
| **معالجة الأخطاء** | يتعامل `try/except` بشكل سلس مع الحالات التي لا تكون فيها مخرجات النموذج اللغوي JSON صالحاً |

تتوسّع هذه الأنماط نفسها لتناسب أي تطبيق مثل روبوتات الدردشة ومساعدي الكود ومولّدات المحتوى وأدوات الأتمتة.

#### تحدٍّ إضافي

* لتحدٍّ إضافي، جرّب تحديث التطبيق ليقرأ البطاقات الدراسية للمستخدم بالرجوع إلى المثال المقدَّم [هنا](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## تشغيل النماذج على NPU (اختياري)

إذا كان لديك جهاز من سلسلة Ryzen AI 300/400/Max 300 أو Z2 Extreme، فإن جهازك يحتوي على **وحدة المعالجة العصبية (NPU)** المدمجة، وهي شريحة مخصصة صُممت خصيصاً لأعباء عمل الذكاء الاصطناعي. تشغيل النماذج على NPU أكثر كفاءة في استهلاك الطاقة مقارنةً باستخدام GPU، مما يجعله مثالياً لمهام الذكاء الاصطناعي في الخلفية، والجلسات الطويلة، والاستخدام بالبطارية.

يدعم Lemonade ثلاثة أوضاع تنفيذ على NPU، وجميعها شفافة خلف نفس OpenAI API:

| الوضع | آلية العمل | الوصفة | أمثلة على النماذج |
|------|-------------|--------|----------------|
| **هجين (NPU + iGPU)** | يعالج NPU الطلب، ويولّد iGPU الرموز | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU فقط** | تعمل الاستدلال بالكامل على NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | يستخدم محرك FastFlowLM على NPU، محسَّن لـ AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### المتطلبات

- معالج **AMD Ryzen AI 300/400 series أو Z2 series**
- لنماذج **FLM**: يمكن تثبيت وقت تشغيل FLM من داخل تطبيق Lemonade، أو سيقوم Lemonade تلقائياً بتثبيت وقت تشغيل FLM عند تشغيل نموذج FLM. لمعرفة المزيد عن FastFlowLM، انظر [هنا](https://fastflowlm.com/docs/).


### الخطوة 8: تشغيل نموذج هجين

تقسّم النماذج الهجينة العمل بين NPU و iGPU لتحقيق توازن جيد بين السرعة والكفاءة. في تطبيق Lemonade، اختر نموذجاً من قائمة `Ryzen AI LLM`، على سبيل المثال `Qwen3-4B-Hybrid`، أو شغّله باستخدام الأمر التالي:

```
lemonade run Qwen3-4B-Hybrid
```

يكتشف Lemonade NPU الخاص بك تلقائياً ويثبّت الواجهة الخلفية **Ryzen AI LLM**.

> **ما الذي يحدث خلف الكواليس؟** عندما ترسل رسالة، يعالج NPU طلبك بالكامل بشكل متوازٍ (يُسمى هذا "الملء المسبق"). ثم يتولى iGPU توليد الاستجابة رمزاً واحداً في كل مرة (يُسمى هذا "فك الترميز"). يستفيد هذا النهج الهجين من نقاط قوة كل شريحة.

### الخطوة 9: تشغيل نموذج FLM

نماذج FastFlowLM (FLM) محسَّنة خصيصاً لبنية AMD XDNA2 NPU ويمكن أن تكون سريعة جداً بالنسبة لحجمها. على سبيل المثال، اختر `qwen3.5-4b-FLM` من قائمة `FastFlowLM NPU` أو استخدم الأمر التالي:

<!-- @os:windows -->
لتفعيل `FastFlowLM` على Windows:

* افتح قائمة `Backends Manager`.
* حدد فئة الواجهة الخلفية `FastFlowLM NPU`.
* انقر على Install NPU.
* بعد اكتمال التثبيت، ستتوفر ~36 نموذجاً افتراضياً ضمن قائمة FFLM المنسدلة.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
عند تشغيل تطبيق `Lemonade` لأول مرة، لا تكون الواجهة الخلفية `FastFlowNPU` مفعّلة بشكل افتراضي.
سيفتح التطبيق المحلي صفحة التثبيت لإرشادك خلال عملية الإعداد.

لتفعيل `FastFlowLM` على Linux:

* افتح تطبيق `Lemonade`.
* زر توثيق [FLM الرسمي](https://lemonade-server.ai/flm_npu_linux.html) واتبع خطوات تثبيت FLM باختيار توزيعة Linux الخاصة بك.
* فعّل backports كما هو موضح في صفحة التثبيت.
* نزّل أحدث إصدار `v0.9.x` من [صفحة الإصدارات](https://github.com/FastFlowLM/FastFlowLM/tags).
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
لمنصة AMD Halo Developer Platform، تأكد من اختيار Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* ثبّت حزمة `.deb` التي تم تنزيلها.
* موصى به: أغلق `Lemonade App` وافتحه مجدداً حتى يتم اكتشاف التغييرات.
* موصى به: افتح `Backends Manager` وانقر على Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
بعد التثبيت الناجح، يجب أن ترى أن `flm:npu` قد اكتمل في **Download Manager** داخل **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
يمكنك بعد ذلك اختيار أي من نماذج FFLM المتاحة والبدء في استخدام الواجهة الخلفية NPU.

لنموذج محدد، نزّل النموذج المطلوب من [صفحة النماذج](https://fastflowlm.com/docs/models/qwen/) وتحقق منه باستخدام أمر Shell المقدم في التوثيق.
```
flm run qwen3.5-4b-FLM
```
أو عبر 
```
lemonade run qwen3.5-4b-FLM
```

تتضمن نماذج FLM بعضاً من أكثر البنيات شيوعاً (Gemma 3، Qwen 3، Llama 3، وDeepSeek R1) وتتراوح من أقل من 1 غيغابايت إلى أكثر من 13 غيغابايت.
يكتشف Lemonade NPU الخاص بك تلقائياً ويثبّت الواجهة الخلفية **FastFlowLM NPU**.

<!-- @os:windows -->
> **نصيحة:** للحصول على أفضل أداء لـ NPU، فعّل وضع turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### التبديل بين النماذج

تطبيق البطاقات التعليمية من الخطوة 6 يعمل أيضاً مع نماذج NPU، فقط غيّر اسم النموذج:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## الخطوات التالية

لديك الآن خادم ذكاء اصطناعي محلي يعمل على جهازك الخاص، إليك ما يمكنك فعله بعد ذلك:

1. **اربط تطبيقاتك المفضلة**: يعمل Lemonade مباشرةً مع [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)، و[Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)، و[Continue](https://lemonade-server.ai/docs/server/apps/continue/)، و[n8n](https://n8n.io/integrations/lemonade-model/)، و[العديد غيرها](https://lemonade-server.ai/marketplace).

2. **تصفح المزيد من النماذج**: استكشف [مكتبة النماذج](https://lemonade-server.ai/docs/server/server_models/) الكاملة للعثور على نماذج محسَّنة للبرمجة والاستدلال والرؤية والمزيد. استخدم تطبيق Lemonade أو `lemonade list` لمعرفة ما هو متاح.

3. **افتح تسريع ROCm GPU**: إذا كان لديك AMD GPU مدعوم، انتقل إلى الواجهة الخلفية ROCm: `lemonade config set llamacpp.backend=rocm`. انظر [AMD GPUs المدعومة](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **اقرأ مواصفات API الكاملة**: يدعم Lemonade إكمال المحادثات، والتضمينات، ونسخ الصوت، وتوليد الصور، وتحويل النص إلى كلام، والمزيد. انظر [مواصفات الخادم](https://lemonade-server.ai/docs/server/server_spec/) لكل نقطة نهاية.

5. **ساهم في المشروع**: Lemonade مفتوح المصدر. اطلع على [دليل المساهمة](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) وابحث عن [المشكلات المناسبة للمبتدئين](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).