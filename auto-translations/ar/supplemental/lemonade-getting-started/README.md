<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->
## نظرة عامة

🍋 **Lemonade** هو خادم ذكاء اصطناعي محلي مفتوح المصدر يتيح لك تشغيل نماذج اللغة الكبيرة (LLMs)، ومولدات الصور، ونماذج الصوت مباشرة على جهازك الخاص. يعرض النماذج من خلال **OpenAI API** المعياري في هذا المجال، لذا فإن أي تطبيق يعمل مع OpenAI يمكنه العمل فورًا مع Lemonade. بحلول نهاية هذا الدليل، ستكون قد استخدمت Lemonade لتشغيل النماذج محليًا على جهازك.

## ما ستتعلمه

بحلول نهاية هذا الدليل، ستكون قادرًا على:

* **تثبيت Lemonade Server** والتحقق من أنه يعمل.
* **تنزيل نموذج لغة كبير والدردشة معه** باستخدام أمر واحد.
* **استكشاف واجهة الويب** وتجربة أنماط مختلفة مثل الرؤية، وتحويل الكلام إلى نص، وتوليد الصور.
* **التبديل بين خلفيات GPU** بين Vulkan و AMD ROCm™ software.
* **بناء تطبيق Python** مدعوم بنموذج لغة كبير محلي باستخدام واجهة برمجة التطبيقات المتوافقة مع OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **تشغيل النماذج على وحدة المعالجة العصبية (NPU) من AMD** باستخدام وضعي التنفيذ Hybrid وFLM على أجهزة AMD Ryzen™ AI.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## تعيين تكوين الذاكرة
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## تحقق من تحديثات البرنامج
<!-- @require:software-update -->
<!-- @device:end -->
## تثبيت متطلبات البرامج الأساسية

قبل البدء، تأكد من توفر ما يلي:

- جهاز يعمل بنظام **Windows 11** أو توزيعة **Linux** مدعومة (Ubuntu 24.04+، Fedora، Debian)
- يُوصى بتوفر **16 غيغابايت من ذاكرة الوصول العشوائي (RAM)** للنموذج الذي يعمل بشكل أساسي في الخطوات من 1 إلى 7 (`Gemma-4-E2B-it-GGUF`، حوالي 3 غيغابايت). ويُوصى بتوفر **32 غيغابايت أو أكثر** إذا كنت ترغب في استخدام نموذج توليد الأكواد الأكبر حجمًا في الخطوة 6 (`Qwen3.5-35B-A3B-GGUF`، حوالي 20 غيغابايت).
- **حوالي 4 إلى 30 غيغابايت من المساحة الحرة على القرص**، حسب النماذج التي تقوم بتنزيلها. أكبر نموذج في هذا الدليل يبلغ حجمه حوالي 20 غيغابايت.
- **Python 3.10–3.13** (يُستخدم في قسم تطبيق Python)
- اتصال بالإنترنت (سلكي أو لاسلكي)
<!-- @device:halo_box,halo,stx,krk -->
- [اختياري] وحدة NPU من نوع AMD XDNA 2 (سلسلة Ryzen AI 300/400/Max 300 أو Z2 Extreme) مع أحدث برنامج تشغيل مثبت من [تعليمات تثبيت برنامج Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) إذا كنت تريد تشغيل نموذج على NPU.
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

## المفاهيم الأساسية — كيفية عمل خوادم الذكاء الاصطناعي المحلية

قبل تشغيل نموذج، من المفيد فهم *سبب* إعداد الأمور بهذه الطريقة. Lemonade هو **خادم نماذج محلي**، وهو عملية تُحمّل نماذج الذكاء الاصطناعي في الذاكرة وتعرضها للتطبيقات عبر HTTP، تمامًا كما تفعل خدمة ذكاء اصطناعي سحابية.

### لماذا خادم؟

| الفائدة | ماذا يعني ذلك لك |
|---------|----------------------|
| **تكامل مبسّط** | تتحدث التطبيقات إلى واجهة برمجة تطبيقات HTTP واحدة بدلاً من التعامل مع مكتبات C++ أو Python الخاصة بالأجهزة. |
| **نماذج مشتركة** | يمكن لنموذج واحد محمّل خدمة عدة تطبيقات في وقت واحد، دون وجود نسخ مكررة تستهلك ذاكرة RAM الخاصة بك. |
| **قابلية النقل من السحابة إلى المحلي** | الكود المكتوب لواجهة برمجة تطبيقات OpenAI السحابية يعمل مع Lemonade بتغيير عنوان URL واحد فقط. |
| **فصل الاهتمامات** | يتم التعامل مع إدارة النماذج، والبث، وتحمّل الأخطاء من قِبل الخادم بحيث يمكن للمطورين التركيز على تطبيقهم. |

### معيار واجهة برمجة تطبيقات OpenAI

يُنفّذ Lemonade **واجهة برمجة تطبيقات OpenAI**، وهي نفس الواجهة المستخدمة من قِبل ChatGPT وAzure OpenAI وعشرات الخدمات الأخرى. نموذج المحادثة بسيط:

| الدور | من يتحدث |
|------|---------------|
| **system** | تعليمات للنموذج (الشخصية، القيود، الأدوات المتاحة) |
| **user** | رسائل من الإنسان (أو التطبيق) إلى النموذج |
| **assistant** | الردود التي يولّدها النموذج |

هذا يعني أن أي مكتبة أو تطبيق يدعم OpenAI يمكنه التحدث إلى Lemonade من خلال توجيهه إلى `http://localhost:13305/api/v1` أثناء تشغيل Lemonade Server.

## النشاط الرئيسي — أول محادثة ذكاء اصطناعي محلية لك

لنقم بتنزيل نموذج لغوي كبير وإجراء محادثة معه، مع تشغيل الذكاء الاصطناعي بالكامل على جهازك الخاص.

### الخطوة 1: تنزيل نموذج وتشغيله

يأتي Lemonade مزودًا بمكتبة نماذج منسّقة. لنبدأ بـ **Gemma-4-E2B-it**، وهو نموذج قوي ومدمج يتضمن دعم الرؤية. افتح طرفية (terminal) وقم بتشغيل:

```
lemonade run Gemma-4-E2B-it-GGUF
```

تقوم هذه الأمر الواحد بثلاثة أشياء:

1. **تنزيل** النموذج (~3 GB) من Hugging Face، إذا لم يكن قد تم تنزيله بالفعل. (قد يستغرق بعض الوقت)
2. **تشغيل** عملية Lemonade Server على المنفذ 13305.
3. **فتح Lemonade App** حتى تتمكن من بدء الدردشة مع النموذج.
<!-- @os:windows -->
على نظام Windows، يتم تشغيل تطبيق Lemonade App تلقائيًا ويمكنك البدء في الدردشة على الفور. إذا قمت بتثبيت حزمة `minimal.msi`، فإن التطبيق غير مضمّن. لبدء الدردشة، افتح متصفح الويب الخاص بك وانتقل إلى `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
للوصول إلى تطبيق الويب على نظام Linux، افتح متصفحك وانتقل إلى `http://localhost:13305`.
<!-- @os:end -->
جرّب كتابة سؤال:

```
What are three fun facts about lemons?
```

**تهانينا! أنت الآن تُشغّل نموذج لغة كبير محليًا.**

![Lemonade App with Logs displayed](../../dependencies/assets/ChatwithLogs.png)

في لوحة سجلات الخادم (Server Logs) الموجودة في Lemonade App، يمكنك العثور على بيانات القياس عن بُعد (telemetry) المتعلقة بأداء النموذج بعد كل استجابة. على سبيل المثال:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### الخطوة 2: استكشاف واجهة الويب والأنماط المختلفة

يتضمن Lemonade واجهة ويب مدمجة يمكنك من خلالها:

- **التفاعل** مع النموذج المُحمَّل في نافذة محادثة مألوفة
- **تصفح النماذج** في علامة التبويب Model Manager
- **تنزيل نماذج جديدة** بنقرة واحدة

جرِّب التنقل بين الأنماط المختلفة باستخدام علامة التبويب **Model Manager** في واجهة الويب حيث يمكنك تصفح النماذج حسب Recipe أو حسب Category:

1. **الرؤية:** يدعم نموذج `Gemma-4-E2B-it-GGUF` الذي قمت بتحميله بالفعل ميزة الرؤية. الصق صورة في مربع المحادثة واطلب من النموذج وصفها.
2. **توليد الصور:** في فئة Image، قم بتنزيل نموذج صور مثل `SDXL-Turbo` من Model Manager، ثم استخدم Lemonade Image Generator لكتابة موجّه (prompt) وتوليد صورة محليًا.
3. **الصوت:** في فئة Audio، قم بتنزيل نموذج صوتي مثل `Whisper-Tiny`، والذي يمكنه تحويل الكلام إلى نص. قدِّم تسجيلًا صوتيًا لتفريغه محليًا. أما بالنسبة لتحويل النص إلى كلام، جرِّب أحد النماذج في فئة Speech، مثل `kokoro-v1`.

![التعددية النمطية مع Lemonade](../../dependencies/assets/multi_modality.png)

### الخطوة 3: جرِّب نموذجًا بخلفية (backend) مختلفة

إذا مررت بالماوس فوق نموذج في تطبيق Lemonade، سترى أيقونة ترس (gear). النقر عليها يتيح لك تحديد خيارات النموذج، بما في ذلك اختيار الخلفية المرغوبة.

بشكل افتراضي، يستخدم Lemonade Vulkan لتسريع GPU. إذا كان لديك بطاقة AMD discrete GPU مدعومة، يمكنك التبديل إلى ROCm.

![اختيار خلفية Lemonade](../../dependencies/assets/lemonademodeloptions.png)

لإدارة الخلفيات المثبتة لديك، انقر على زر backend في أقصى العمود الأيسر.

بدلاً من ذلك، يمكنك تحديد الخلفية باستخدام الأمر التالي:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

يمكنك أيضًا تعيين الخلفية الافتراضية باستخدام متغير البيئة `LEMONADE_LLAMACPP` بالقيم: `vulkan`، أو `rocm`، أو `cpu`.

---

## التعمق أكثر — بناء تطبيق مدعوم بالذكاء الاصطناعي باستخدام Python

القوة الحقيقية لخادم الذكاء الاصطناعي المحلي تكمن في أن أي تطبيق يمكنه الاتصال به باستخدام بضعة أسطر من الكود فقط. لإثبات ذلك، لنقم ببناء **مولّد بطاقات دراسية (flashcard)** صغير لكنه وظيفي بالكامل حيث تعطيه موضوعًا، فيقوم بتوليد البطاقات الدراسية، ويمكنك اختبار نفسك بشكل تفاعلي.

### الخطوة 4: تشغيل الخادم

تحقق من أن خادم Lemonade قيد التشغيل. عادةً ما يبدأ تلقائيًا في الخلفية بعد التثبيت. للتحقق، شغِّل:

```
lemonade status
```

يجب أن ترى رسالة مثل: `Server is running on port 13305`.

إذا لم يكن الخادم قيد التشغيل، ابدأه عن طريق فتح تطبيق Lemonade. استخدم المنفذ الافتراضي **13305** (يمكنك التأكد منه أو اختياره من أيقونة الدرج (tray icon)).

### الخطوة 5: تثبيت OpenAI Python Client

في الطرفية (terminal)، أنشئ بيئة venv وقم بتثبيت OpenAI Python Client باستخدام الأوامر التالية:
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

لنقم بتنزيل نموذج مختلف لتوليد الكود: `Qwen3.5-35B-A3B-GGUF`. هذا نموذج كبير (~20 جيجابايت) وعالي الأداء، وهو الأنسب للأنظمة التي تحتوي على 32 جيجابايت أو أكثر من ذاكرة RAM. إذا كانت لديك ذاكرة RAM أقل متاحة، جرِّب `Qwen3.5-9B-GGUF` (~6 جيجابايت) بدلاً من ذلك.

يمكنك تنزيله من واجهة المستخدم أو تشغيل ما يلي:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

أدخل الموجّه (prompt) التالي في واجهة Lemonade Chat لتوليد كود لتطبيق بطاقات دراسية بسيط.

سنستخدم Qwen3.5-35B-A3B-GGUF (نموذج أكبر وأفضل في كتابة الكود) لتوليد تطبيق Python الخاص بنا، وسيقوم التطبيق نفسه باستدعاء Gemma-4-E2B-it-GGUF (النموذج الأصغر الذي قمت بتنزيله بالفعل) أثناء التشغيل. يمكن بعد ذلك نسخ الكود إلى ملف من اختيارك ليتم تشغيله في Python.

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

> **نصيحة**: لقد اتبعنا ممارسات هندسية معيارية من خلال إنشاء موجّهات (prompts) دقيقة واستخدام نظام ذي نموذجين لتحسين استخدام الموارد والسرعة.

لراحتك، قدمنا مثالاً على المخرجات في [`flashcards.py`](assets/flashcards.py). لا تتردد في تنزيله إلى دليلك (directory). في كلتا الحالتين، يجب أن يكون لديك الآن ملف Python جاهز للتشغيل.

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


### الخطوة 7: تشغيل الكود المُولَّد

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

في حوالي 150 سطرًا من الكود، تكون قد بنيت أداة دراسية كاملة الوظائف تعمل بواسطة نموذج LLM محلي. لا يوجد مفتاح API لإدارته، ولا تكاليف استخدام، ولا تغادر أي بيانات جهازك على الإطلاق.

> **رؤية أساسية:** لاحظ أن السطر `client = OpenAI(base_url=...) ` هو الشيء *الوحيد* الذي يربط هذا التطبيق بـ Lemonade بدلاً من سحابة OpenAI. بقية الكود مطابقة تمامًا لما كنت ستكتبه ضد أي خدمة متوافقة مع OpenAI. إذا سبق لك استخدام مكتبة OpenAI Python، فأنت تعرف بالفعل كيفية بناء تطبيقات باستخدام Lemonade.

### ما يوضحه هذا

يستعرض هذا التطبيق الصغير عدة أنماط تكامل واقعية:

| النمط | أين يظهر |
|---------|-----------------|
| **الموجّهات النظامية (System prompts)** | تخبر رسالة `"system"` نموذج LLM بإخراج JSON منظم |
| **المخرجات المنظمة** | يقوم التطبيق بتحليل استجابة نموذج LLM كـ JSON لبناء البطاقات الدراسية |
| **الطلبات عديمة الحالة (Stateless requests)** | كل استدعاء لـ `generate_flashcards()` مستقل |
| **معالجة الأخطاء** | يتعامل `try/except` بسلاسة مع الحالات التي لا تكون فيها مخرجات نموذج LLM بصيغة JSON صالحة |

تتوسع هذه الأنماط نفسها لتشمل أي تطبيق مثل روبوتات المحادثة، ومساعدي الكود، ومولّدات المحتوى، وأدوات الأتمتة.

#### تحدٍّ إضافي

* لتحدٍّ إضافي، جرِّب تحديث التطبيق ليتم قراءة البطاقات الدراسية للمستخدم من خلال الرجوع إلى المثال المتوفر [هنا](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## تشغيل النماذج على وحدة المعالجة العصبية (NPU) (اختياري)

إذا كان لديك جهاز من سلسلة Ryzen AI 300/400/Max 300 أو Z2 Extreme، فإن جهازك مزود بـ **وحدة معالجة عصبية مدمجة (NPU)**، وهي شريحة مخصصة مصممة خصيصًا لأحمال عمل الذكاء الاصطناعي. يُعد تشغيل النماذج على NPU أكثر كفاءة في استهلاك الطاقة مقارنةً باستخدام GPU، مما يجعله مثاليًا لمهام الذكاء الاصطناعي في الخلفية، والجلسات الطويلة، والاستخدام بالبطارية.

يدعم Lemonade ثلاثة أوضاع تشغيل لوحدة NPU، وكلها تعمل بشفافية خلف نفس OpenAI API:

| الوضع | كيف يعمل | الوصفة (Recipe) | نماذج مثال |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | تعالج NPU الطلب (prompt)، ويولّد iGPU الرموز (tokens) | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU-only** | يعمل الاستدلال بالكامل على NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | يستخدم محرك FastFlowLM على NPU، مُحسَّن لـ AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### المتطلبات

- معالج **AMD Ryzen AI 300/400 series أو Z2 series**
- بالنسبة لنماذج **FLM**: يمكن تثبيت وقت تشغيل FLM من داخل تطبيق Lemonade، أو سيقوم Lemonade تلقائيًا بتثبيت وقت تشغيل FLM عند تشغيل نموذج FLM. لمعرفة المزيد عن FastFlowLM، انظر [هنا](https://fastflowlm.com/docs/).


### الخطوة 8: تشغيل نموذج Hybrid

تقسم نماذج Hybrid العمل بين NPU و iGPU لتحقيق توازن جيد بين السرعة والكفاءة. في تطبيق Lemonade، اختر نموذجًا من قائمة `Ryzen AI LLM`، على سبيل المثال، `Qwen3-4B-Hybrid`، أو قم بتشغيله باستخدام الأمر التالي:

```
lemonade run Qwen3-4B-Hybrid
```

يكتشف Lemonade وحدة NPU لديك تلقائيًا ويثبّت خلفية **Ryzen AI LLM**.

> **ما الذي يحدث خلف الكواليس؟** عند إرسال رسالة، تعالج NPU طلبك بالكامل بالتوازي (تُسمى هذه العملية "prefill"). ثم يتولى iGPU توليد الاستجابة رمزًا تلو الآخر (تُسمى هذه العملية "decode"). يستفيد هذا النهج الهجين من نقاط قوة كل شريحة.

### الخطوة 9: تشغيل نموذج FLM

نماذج FastFlowLM (FLM) مُحسَّنة خصيصًا لمعمارية AMD's XDNA2 NPU ويمكن أن تكون سريعة جدًا بالنسبة لحجمها. على سبيل المثال، اختر `qwen3.5-4b-FLM` من قائمة `FastFlowLM NPU` أو استخدم الأمر التالي:

<!-- @os:windows -->
لتفعيل `FastFlowLM` على Windows:

* افتح قائمة `Backends Manager`.
* حدد فئة خلفية `FastFlowLM NPU`.
* انقر على Install NPU.
* بعد اكتمال التثبيت، ستتوفر حوالي 36 نموذجًا افتراضيًا ضمن قائمة FFLM المنسدلة.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
عند تشغيل تطبيق `Lemonade` لأول مرة، لا يتم تفعيل خلفية `FastFlowNPU` افتراضيًا.
سيفتح التطبيق المحلي صفحة التثبيت لإرشادك خلال عملية الإعداد.

لتفعيل `FastFlowLM` على Linux:

* افتح تطبيق `Lemonade`.
* قم بزيارة توثيق [official FLM](https://lemonade-server.ai/flm_npu_linux.html) واتبع خطوات التثبيت لـ FLM عن طريق اختيار توزيعة Linux الخاصة بك.
* فعّل backports كما هو موضح في صفحة التثبيت.
* قم بتنزيل أحدث إصدار `v0.9.x` من [صفحة العلامات (tags page)](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
بالنسبة لـ AMD Halo Developer Platform، تأكد من اختيار Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* قم بتثبيت حزمة `.deb` التي تم تنزيلها.
* موصى به: أغلق `Lemonade App` وافتحه مرة أخرى ليتم اكتشاف التغييرات.
* موصى به: افتح `Backends Manager` وانقر على تثبيت خلفية `FastFlowNPU`.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
بعد نجاح التثبيت، يجب أن تلاحظ أن `flm:npu` قد اكتمل في **Download Manager** داخل **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
يمكنك بعد ذلك اختيار أي من نماذج FFLM المتاحة والبدء باستخدام خلفية NPU.

بالنسبة لنموذج معين، قم بتنزيل النموذج المطلوب من [صفحة النماذج](https://fastflowlm.com/docs/models/qwen/) وتحقق منه باستخدام أمر Shell المذكور في التوثيق.
```
flm run qwen3.5-4b-FLM
```
أو عبر 
```
lemonade run qwen3.5-4b-FLM
```

تشمل نماذج FLM بعضًا من أشهر المعماريات (Gemma 3، Qwen 3، Llama 3، و DeepSeek R1) وتتراوح من أقل من 1 جيجابايت إلى أكثر من 13 جيجابايت.
يكتشف Lemonade وحدة NPU لديك تلقائيًا ويثبّت خلفية **FastFlowLM NPU**.

<!-- @os:windows -->
> **نصيحة:** لأفضل أداء لـ NPU، فعّل وضع turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### تبديل النماذج

يعمل تطبيق البطاقات التعليمية (flashcard) من الخطوة 6 مع نماذج NPU أيضًا، فقط قم بتغيير اسم النموذج:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## الخطوات التالية

لديك الآن خادم ذكاء اصطناعي محلي يعمل على جهازك الخاص، وإليك الخطوات التالية التي يمكنك اتخاذها:

1. **قم بربط تطبيقاتك المفضلة**: يعمل Lemonade مباشرة مع [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)، و[Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)، و[Continue](https://lemonade-server.ai/docs/server/apps/continue/)، و[n8n](https://n8n.io/integrations/lemonade-model/)، و[المزيد](https://lemonade-server.ai/marketplace).

2. **تصفح المزيد من النماذج**: استكشف [مكتبة النماذج](https://lemonade-server.ai/docs/server/server_models/) الكاملة للعثور على نماذج مُحسَّنة للبرمجة، والاستدلال، والرؤية، والمزيد. استخدم تطبيق Lemonade أو `lemonade list` لمعرفة ما هو متاح.

3. **فتح تسريع ROCm GPU**: إذا كان لديك AMD GPU مدعوم، قم بالتبديل إلى خلفية ROCm: `lemonade config set llamacpp.backend=rocm`. راجع [بطاقات AMD المدعومة](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **اقرأ مواصفات API الكاملة**: يدعم Lemonade إكمالات المحادثة، والتضمينات (embeddings)، ونسخ الصوت، وتوليد الصور، وتحويل النص إلى كلام، والمزيد. راجع [مواصفات الخادم (Server Spec)](https://lemonade-server.ai/docs/server/server_spec/) لمعرفة كل نقطة نهاية (endpoint).

5. **ساهم في المشروع**: Lemonade مفتوح المصدر. اطّلع على [دليل المساهمة](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) وابحث عن [المشكلات المناسبة للبدء (Good First Issues)](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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