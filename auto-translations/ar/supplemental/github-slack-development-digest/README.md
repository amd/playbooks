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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## نظرة عامة

يقضي المطورون قدرًا كبيرًا من الوقت في حلقات صغيرة متكررة: مراجعة طلبات السحب (pull requests) المُصنّفة، والرد على تعليقات GitHub، وفرز المشكلات الجديدة، وتحويل مسارات Slack إلى ملاحظات الاجتماعات اليومية أو متابعات الحوادث، وتتبع إشارات الإصدارات أو الأبحاث.
كل حلقة مألوفة، لكنها لا تزال تتطلب حكمًا: جمع السياق المناسب، وتحديد ما هو مهم، ونشر تحديث واضح في المكان الذي يعمل فيه الفريق بالفعل.

تحوّل [أتمتة OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) تلك الحلقات إلى محادثات وكيل مُجدولة أو مُشغَّلة بالأحداث: تشغيلات يمكن فيها لوكيل برمجيات الذكاء الاصطناعي قراءة السياق، واستدعاء الأدوات، وإنتاج تحديث.
تتبع قوالب الأتمتة المشتركة في كتالوج ملحقات OpenHands هذا النمط لمراجعة طلبات سحب GitHub، ومراقبة المستودعات، وفرز مشكلات Linear، ومراجعات الحوادث بعد وقوعها، وملخصات الاجتماعات اليومية عبر Slack، وموجزات الأبحاث: تستيقظ الأتمتة، وتستخدم تكاملات مُهيّأة مثل GitHub أو Slack لجلب السياق، وتُحلّل ذلك السياق باستخدام نموذج لغوي كبير (LLM)، وتكتب نتيجة.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) هو لوحة التحكم المحلية لبناء واختبار تلك الأتمتة.
في هذا الدليل، يُشغّل خادم وكيل OpenHands، وهو العملية الخلفية التي تنفّذ محادثات الوكيل، ويربط الوكيل بالخدمات الخارجية مثل GitHub وSlack.

للحفاظ على سير العمل داخل نظام AMD الخاص بك، يتواصل الوكيل مع نموذج محلي يُقدَّم عبر Lemonade Server.
يُعرّض Lemonade هذا النموذج عبر واجهة برمجة تطبيقات متوافقة مع OpenAI، لذا يمكن لـ Agent Canvas تهيئته كنقطة نهاية بعيدة بأسلوب OpenAI بينما يبقى النموذج والمطالبة وسياق سير العمل محليًا.

في هذا الدليل، ستبني أتمتة ملموسة واحدة: موجز تطوير مُجدول من GitHub إلى Slack.
تستخدم GitHub لفحص نشاط المستودع الأخير، وSlack لنشر الموجز، واستدعاءات واجهة برمجة تطبيقات Agent Canvas لتهيئة الأتمتة واختبارها، وLemonade لتشغيل النموذج اللغوي الكبير محليًا.

![رسم بياني للهندسة يوضح GitHub MCP وأتمتة OpenHands وLemonade Server وSlack MCP](assets/00-architecture-overview.png)

## ما الذي ستتعلمه

- كيفية تشغيل Lemonade Server والتحقق من أن نموذجًا محليًا يستجيب لطلبات المحادثة
- كيفية إطلاق Agent Canvas وتوجيه خادم الوكيل الخاص به إلى نموذج لغوي كبير محلي
- كيفية تثبيت خوادم بروتوكول سياق النموذج (MCP) الخاصة بـ GitHub وSlack عبر واجهة برمجة تطبيقات خادم الوكيل
- كيفية إنشاء وإرسال أتمتة OpenHands مُجدولة تنشر موجز تطوير إلى Slack
- كيفية استكشاف أكثر أعطال النموذج المحلي والأتمتة شيوعًا وإصلاحها

## المفاهيم الأساسية

| المفهوم | ما هو | أين يندرج في هذا الدليل |
| --- | --- | --- |
| Lemonade Server | منصة تقديم نموذج لغوي كبير محلية مبنية لعتاد AMD، تُعرّض واجهة برمجة تطبيقات متوافقة مع OpenAI. بياناتك لا تغادر جهازك أبدًا. | يُشغّل النموذج الذي يُشغّل الوكيل. |
| خادم وكيل OpenHands | العملية الخلفية التي تنفّذ محادثات وكيل OpenHands. | يستضيف الوكيل وملفه الشخصي للنموذج اللغوي الكبير وخوادم MCP الخاصة به. |
| Agent Canvas | لوحة التحكم المحلية لـ OpenHands التي تُشغّل خادم الوكيل وواجهة مستخدم لفحص تشغيلات الوكيل. | يُطلق الخلفيات ويوفّر واجهة برمجة التطبيقات التي تستدعيها. |
| خادم MCP | خادم بروتوكول سياق النموذج يمنح الوكيل أدوات لخدمة خارجية مثل GitHub أو Slack. | يتيح للوكيل قراءة GitHub والكتابة إلى Slack. |
| أتمتة OpenHands | محادثة وكيل مُجدولة أو مُشغَّلة بالأحداث تجلب السياق، وتُحلّله، وتكتب نتيجة في مكان ما. | موجز GitHub إلى Slack الذي تبنيه هنا. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> تستفيد سير عمل الوكيل البرمجي من نموذج أكبر ونافذة سياق أوسع.
> استخدم 32 جيجابايت على الأقل من ذاكرة النظام، ويُفضَّل 64 جيجابايت أو أكثر للنماذج الأكبر بصيغة GGUF.
<!-- @device:end -->

## تهيئة إعدادات الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## المتطلبات الأساسية

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

تحتاج إلى:

- تثبيت Lemonade Server باتباع [دليل تثبيت Lemonade](https://lemonade-server.ai/docs/guide/install/) القياسي.

<!-- @os:linux -->
- Node.js 22.12 أو أحدث مع `npm`، تُستخدم لتثبيت واجهة سطر أوامر Agent Canvas المنشورة وتشغيل خوادم MCP باستخدام `npx`.
- `uv`، مدير حزم Python الذي يستخدمه Agent Canvas لبناء بيئة خادم الوكيل. إذا لم يكن مثبتًا بالفعل، قم بتثبيته من [دليل تثبيت uv](https://docs.astral.sh/uv/getting-started/installation/).
- إصدار حديث منشور من حزمة `@openhands/agent-canvas` يحتوي على إعدادات وكيل مبنية على المخطط، و`LLMSummarizingCondenserSettings.max_tokens`، ودعم `custom_tokenizer` للنموذج اللغوي الكبير.
- توفر حزمة `transformers` الخاصة بـ Python في بيئة خادم الوكيل. وهي مطلوبة لعدّ الرموز وفق قالب المحادثة عند تعيين `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop لنظام Windows](https://docs.docker.com/desktop/setup/install/windows-install/)، مثبّت وقيد التشغيل. على نظام Windows، تعمل حزمة Agent Canvas من صورة Docker المنشورة، التي تجمع Node.js وuv وtransformers وحزمة `@openhands/agent-canvas`، لذا لست بحاجة إلى تثبيت هذه العناصر على المضيف.
<!-- @os:end -->

- رمز GitHub بصلاحية قراءة للمستودع الذي تريد تلخيصه.
- رمز بوت Slack (`xoxb-...`) بصلاحيات `chat:write` وقراءة القناة.
- معرّف فريق Slack (`T...`).
- معرّف قناة Slack (`C...`) حيث يجب نشر الموجز.

ادعُ تطبيق Slack إلى القناة المستهدفة قبل اختبار الأتمتة.
## المتغيرات المستخدمة في هذا الدليل الإرشادي

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

يُستخدم هذان المتغيران في أوامر التحقق أدناه.
يتم إدخال النموذج (model) والمُجزّئ (tokenizer) وإعدادات LLM الأخرى مباشرةً في واجهة Agent Canvas في الخطوات اللاحقة، لذا تُعرض قيمها الحرفية هنا بشكل مضمّن عند الحاجة إليها.

تُدخَل القيم التالية في واجهة Agent Canvas في الخطوات اللاحقة.
عيّنها هنا حتى تتمكن من نسخها لاحقًا:

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

استخدم قيمة صريحة بالصيغة `owner/repo` لمتغير `GITHUB_REPO_FILTER`.
فقد تؤدي بطاقات حرف المؤسسات العامة (organization wildcards) إلى إرجاع سياق MCP كبير جدًا بالنسبة للنماذج المحلية.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. تشغيل خادم Lemonade

شغّل النموذج من واجهة سطر أوامر Lemonade:

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **اختر نموذجًا يناسب عتادك.** يُعد `Qwen3.6-35B-A3B-GGUF` (بحجم ~20 جيجابايت) نموذجًا قويًا لهذا سير العمل، لكنه يتطلب مساحة ذاكرة كبيرة.
> إذا كان جهازك يحتوي على ذاكرة محدودة أو ذاكرة GPU VRAM محدودة، فاختر نموذج GGUF أصغر من مكتبة نماذج Lemonade واستخدم معرّف ذلك النموذج (والمُجزّئ المطابق له) في جميع أنحاء هذا الدليل.

> **ملاحظة:** يقوم أول أمر `lemonade run` بتنزيل النموذج إذا لم يكن موجودًا بالفعل، وقد يستغرق ذلك بعض الوقت حسب حجم النموذج وسرعة اتصالك.

يوفّر Lemonade واجهة برمجة تطبيقات متوافقة مع OpenAI على العنوان:

```text
http://127.0.0.1:13305/api/v1
```

اختياري: إذا لم تكن واجهة Agent Canwas أو مُشغّل الأتمتة على نفس الجهاز، فانشر نقطة نهاية Lemonade عبر نفق آمن واستخدم عنوان HTTPS كعنوان أساس (base URL) لـ LLM.
تتيح أداة [ngrok](https://ngrok.com/) كشف منفذ محلي على الإنترنت عبر عنوان HTTPS آمن؛ وهي تتطلب حساب ngrok مجاني، وتقوم باستبدال `YOUR_NGROK_DOMAIN.ngrok-free.dev` بنطاقك المحجوز الخاص:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. التحقق من النموذج المحلي

تأكد من أن Lemonade قادر على تقديم النموذج المحدد:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

ثم أرسل طلب محادثة صغيرًا:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

ثم أرسل طلب محادثة صغيرًا:

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

إذا أعاد هذا مصفوفة `choices`، فهذا يعني أن Lemonade جاهز لـ Agent Canvas.

<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
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
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 64
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. تشغيل Agent Canvas

<!-- @os:linux -->
ثبّت حزمة Agent Canvas المنشورة وشغّل المجموعة الكاملة:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

إذا فشل تثبيت npm العالمي بخطأ متعلق بالأذونات، راجع إدخال استكشاف أخطاء أذونات npm وإصلاحها أدناه.

بشكل افتراضي، يبدأ Agent Canvas على العنوان `http://localhost:8000`.
افتح ذلك العنوان في متصفحك.
المنفذ غير مميز—إذا كان المنفذ 8000 مستخدمًا بالفعل، مرّر أي منفذ متاح باستخدام `--port` (أو `-p`).
يجب أن تظهر الواجهة الخلفية المحلية الافتراضية بحالة سليمة (healthy) في الشاشة الرئيسية.

> **ملاحظة:** يقوم أول تشغيل ببناء بيئة بايثون الخاصة بخادم الوكيل (Agent Server) والمُدارة بواسطة `uv`، لذا قد يستغرق الأمر بضع دقائق قبل أن تُبلّغ الواجهة الخلفية عن حالتها السليمة.

يقوم أمر `agent-canvas` بتشغيل خادم الوكيل، والواجهة الخلفية للأتمتة، والواجهة الأمامية للويب معًا.
تحتاج فقط إلى هذا الأمر الواحد لتشغيل OpenHands محليًا.
يقوم باقي هذا الدليل الإرشادي بتهيئة كل شيء من خلال واجهة Agent Canvas في متصفحك.
<!-- @os:end -->

<!-- @os:windows -->
على نظام Windows، شغّل صورة حاوية Agent Canvas المنشورة باستخدام Docker Desktop.
تحتوي الصورة على خادم الوكيل، والواجهة الخلفية للأتمتة، والواجهة الأمامية للويب، لذا لا تحتاج إلى تثبيت Node.js أو `uv` أو واجهة سطر الأوامر على الجهاز المضيف.

أولًا، أنشئ مجلدي التهيئة ومساحة العمل اللذين ستقوم الحاوية بتحميلهما (mount):

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

اسحب الصورة المنشورة (بحجم حوالي 6 جيجابايت؛ وهي عامة، لذا لا يلزم تسجيل الدخول):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

ثم شغّل المجموعة:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

افتح `http://localhost:8000/canvas` في متصفحك.
إذا كان المنفذ 8000 مستخدمًا بالفعل، قم بربط منفذ مضيف مختلف، مثل `-p 8080:8000`، وافتح `http://localhost:8080/canvas` بدلًا من ذلك.

> **ملاحظة:** يقوم أول تشغيل ببناء بيئة خادم الوكيل داخل الحاوية، لذا قد يستغرق الأمر بضع دقائق قبل أن تُبلّغ الواجهة الخلفية عن حالتها السليمة.

يحافظ تحميل `.openhands` على استمرارية ملف تعريف LLM الخاص بك، وخوادم MCP، والأتمتة عبر عمليات إعادة تشغيل الحاوية.
يقوم باقي هذا الدليل الإرشادي بتهيئة كل شيء من خلال واجهة Agent Canvas في متصفحك على العنوان `http://localhost:8000/canvas`.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->
## 4. تهيئة نموذج اللغة الكبير المحلي في الواجهة

عند التشغيل الأول، يفتح Agent Canvas تدفق تهيئة أولي (onboarding).
في هذا التدفق:

1. أبقِ **OpenHands** محددًا كوكيل (agent) وانقر على **Next**.
2. في **Set up your LLM**، اختر **Advanced**.
3. أبقِ **Authentication** مضبوطًا على **API key**.
4. اضبط **Custom Model** على `openai/Qwen3.6-35B-A3B-GGUF`.
5. اضبط **Base URL** على `http://127.0.0.1:13305/api/v1`.
6. في حقل **API Key**، أدخل أي قيمة نائبة غير فارغة مثل `lemonade-local`. لا يتطلب Lemonade مفتاحًا حقيقيًا، لكن عميل OpenHands يحتاج إلى قيمة لإرسالها.

<!-- @os:windows -->
> **Windows (Docker):** يعمل Agent Server داخل الحاوية، لذا اضبط **Base URL** على `http://host.docker.internal:13305/api/v1` بدلًا من `http://127.0.0.1:13305/api/v1`.
> من داخل الحاوية، يشير `127.0.0.1` إلى الحاوية نفسها؛ أما `host.docker.internal` فيصل إلى Lemonade العامل على مضيف Windows، ويوفر Docker Desktop اسم المضيف هذا تلقائيًا.
<!-- @os:end -->

يجب أن تبدو حقول الاتصال كما يلي.
يُخفي واجهة المستخدم حقل مفتاح API.

![إعدادات LLM Advanced عند أول استخدام لـ Agent Canvas مع نموذج Lemonade وعنوان URL الأساسي المحلي](assets/01-llm-advanced-settings.png)

بعد ذلك، اختر **All** واضبط حقول النموذج المحلي الإضافية:

1. مرر إلى **Custom Tokenizer** واضبطه على `Qwen/Qwen3.6-35B-A3B`.
2. مرر إلى **LiteLLM Extra Body** واضبطه على `{"enable_thinking": true}`.
3. انقر على **Next**.

![علامة تبويب LLM All عند أول استخدام لـ Agent Canvas مع مُرمِّز Qwen المخصص](assets/02-llm-all-tokenizer-settings.png)

![علامة تبويب LLM All عند أول استخدام لـ Agent Canvas مع تهيئة LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

يجب أن تُظهر إعدادات LLM ما يلي:

| الحقل | القيمة |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

تخبر البادئة `openai/` LiteLLM باستخدام تنسيق طلبات متوافق مع OpenAI عند التعامل مع نقطة نهاية Lemonade.
المُرمِّز المخصص (tokenizer) هو مُرمِّز Hugging Face الأصلي لنموذج GGUF؛ وهو يتيح لـ OpenHands عدّ نفس رموز قالب المحادثة (chat-template tokens) التي يراها خادم النموذج المحلي.
لا يعرض نموذج LLM الحالي عند أول استخدام إعدادات المُكثِّف (condenser).
إذا كانت نسخة Agent Canvas لديك تعرض إعدادات المُكثِّف لاحقًا ضمن **Settings > LLM**، استخدم `llm_summarizing` واضبط الحد الأقصى للرموز بحيث يكون أقل من نافذة سياق Lemonade، مثل `56000`.

## 5. تثبيت خوادم MCP الخاصة بـ GitHub وSlack

في واجهة Agent Canvas، افتح **Customize** (أو **Settings > MCP**) لإضافة خوادم MCP التي تمنح الوكيل أدوات للتعامل مع GitHub وSlack.
تُرسَل قيم الرموز (tokens) فقط إلى Agent Server المحلي لديك، وتُحفظ كإعدادات مشفّرة.

<!-- @os:windows -->
> **Windows (Docker):** تعمل أوامر خادم MCP الخاصة بـ `npx` أدناه داخل الحاوية، التي تتضمن بالفعل Node.js، لذا لا يُثبَّت شيء إضافي على المضيف.
> نظرًا لأن `.openhands` مُحمَّل (mounted)، تستمر خوادم MCP ورموزها عبر عمليات إعادة تشغيل الحاوية.
<!-- @os:end -->

### خادم MCP الخاص بـ GitHub

أضف خادم MCP جديدًا بهذه الإعدادات:

| الحقل | القيمة |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = رمز GitHub الخاص بك |

استخدم رمز GitHub يتمتع بصلاحية قراءة للمستودع الذي تريد تلخيصه.

### خادم MCP الخاص بـ Slack

أضف خادم MCP ثانيًا بهذه الإعدادات:

| الحقل | القيمة |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = معرف قناة الملخص لديك |

اضبط `SLACK_CHANNEL_IDS` على معرف قناة الملخص (نفس قيمة `SLACK_DIGEST_CHANNEL`) حتى لا يحتاج الوكيل إلى تصفح كل قناة في Slack.

بعد إضافة كلا الخادمين، استخدم زر **Test** على كل منهما للتأكد من اتصاله وإعلانه عن الأدوات المتاحة.
يجب أن يسرد خادم GitHub أدوات GitHub، ويجب أن يسرد خادم Slack أدوات Slack.

![صفحة MCP في Agent Canvas مع تثبيت خادمي GitHub وSlack](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. إنشاء أتمتة الملخص

في واجهة Agent Canvas، افتح صفحة **Automations** وأنشئ أتمتة جديدة:

1. اختر **Create automation** وحدد النوع **Prompt preset**.
2. اضبط **Name** على `GitHub Development Digest to Slack`.
3. اضبط **Prompt** على النص التالي، مع استبدال العناصر النائبة للمستودع والقناة بقيمك الخاصة:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. اضبط **Trigger** على **Cron** بالجدول `0 9 * * 1-5` (الساعة 9 صباحًا أيام الأسبوع) واضبط **Timezone** على منطقتك الزمنية، على سبيل المثال `America/New_York`.
5. اضبط **Timeout** على `900` ثانية.
6. احفظ الأتمتة.

تعرض صفحة تفاصيل الأتمتة الأتمتة الجديدة مع مُشغّلها (trigger) من نوع cron ونقطة الدخول (entrypoint) المُولَّدة من نوع prompt preset.

![تفاصيل الأتمتة في Agent Canvas بعد الإنشاء](assets/05-automation-created.png)
## 7. اختبار الأتمتة

من صفحة تفاصيل الأتمتة في واجهة Agent Canvas:

1. انقر على **Run now** (أو **Dispatch**) لتشغيل الأتمتة فورًا مرة واحدة.
2. راقب قائمة التشغيلات في نفس الصفحة. يجب أن ينتقل التشغيل الأخير إلى الحالة `COMPLETED`.
3. افتح قناة Slack المستهدفة. يجب أن تحتوي على الملخص الذي تم إنشاؤه.

لست بحاجة إلى الانتظار حتى يبدأ جدول cron بالعمل—فخيار **Run now** يُشغّل تشغيلًا عند الطلب حتى تتمكن من التأكد من أن الطلب واتصالات MCP والنشر على Slack تعمل جميعها بشكل صحيح قبل الاعتماد على الجدولة.

![اكتمال تشغيل أتمتة Agent Canvas بنجاح](assets/06-automation-run-completed.png)

![قناة Slack تعرض ملخص OpenHands الذي تم إنشاؤه](assets/07-slackbot-message.png)

## استكشاف الأخطاء وإصلاحها

<!-- @os:windows -->
- **منفذ Docker 8000 مستخدم بالفعل:** قم بربط منفذ مضيف مختلف، على سبيل المثال `docker run ... -p 8080:8000 ...`، ثم افتح `http://localhost:8080/canvas`.
- **يفشل `docker pull` بخطأ في بيانات الاعتماد** (على سبيل المثال، "A specified logon session does not exist"): قم بتشغيل أمر السحب من جلسة Windows تفاعلية، أو قم بسحب الصورة مسبقًا. الصورة عامة، لذا لا حاجة إلى `docker login`.
- **تُحمَّل الواجهة ولكن الخلفية غير سليمة:** يقوم التشغيل الأول ببناء بيئة Agent Server داخل الحاوية. انتظر دقيقة وأعد التحميل، ثم تحقق من `docker logs <container>` لمتابعة التقدم.
- **لا يستطيع Agent Canvas الوصول إلى Lemonade من الحاوية:** اضبط **Base URL** الخاص بـ LLM على `http://host.docker.internal:13305/api/v1` (وليس `127.0.0.1`)، وتأكد من أن Lemonade يعمل على مضيف Windows.
<!-- @os:end -->

- **Lemonade متوقف:** أعد تشغيله باستخدام أمر `lemonade run "${LEMONADE_MODEL}"` في الخطوة 1، ثم أعد تشغيل فحص الحالة.
- **يفشل `npm install -g` بخطأ في الأذونات:** على Linux أو WSL، قم بتكوين دليل npm عام مملوك للمستخدم، وأضفه إلى ملف بدء تشغيل الشِل الخاص بك، ثم ثبّت Agent Canvas مرة أخرى:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

إذا كنت تستخدم `zsh`، أضف نفس السطر `export PATH=...` إلى `~/.zshrc` بدلاً من `~/.bashrc`.
- **يرفض Agent Canvas إعدادات LLM بعد ضبط `custom_tokenizer`:** ثبّت `transformers` في بيئة Python الخاصة بـ Agent Server، وأعد تشغيل Agent Canvas إذا لزم الأمر، وحاول حفظ إعدادات LLM مرة أخرى. يتطلب OpenHands وجود Transformers لتحميل قالب محادثة المُجزِّئ (tokenizer) عند ضبط `custom_tokenizer`.
- **لا يستطيع Agent Canvas الوصول إلى Lemonade:** تحقق من `curl -fsS "${LEMONADE_BASE_URL}/health"` وتأكد من أن عنوان URL الأساسي المُدخل في نموذج LLM عند الاستخدام الأول أو في **Settings > LLM** يطابق نقطة النهاية المحلية قيد التشغيل أو نفق HTTPS.
- **لم يتم حفظ إعدادات LLM:** تأكد من أنك نقرت على **Next** بعد إدخال القيم. أعد فتح **Settings > LLM** للتأكد من أن القيم محفوظة.
- **لا يستطيع GitHub MCP رؤية المستودعات الخاصة:** تأكد من أن رمز GitHub يملك صلاحية قراءة المستودع المستهدف، وأن زر **Test** الخاص بـ MCP في **Customize** يعرض أدوات GitHub.
- **يستطيع Slack قراءة القنوات ولكن لا يستطيع النشر:** قم بدعوة تطبيق Slack إلى القناة المستهدفة وتأكد من أن البوت يملك صلاحية `chat:write`.
- **تسرد الأتمتة عددًا كبيرًا جدًا من قنوات Slack:** استخدم معرّف قناة Slack واضبط `SLACK_CHANNEL_IDS` على خادم Slack MCP في **Customize**.
- **يفشل تشغيل الأتمتة أو يتجاوز السياق:** تأكد من أن Lemonade تم تشغيله بـ `ctx_size=65536`، وتأكد من ضبط `custom_tokenizer` في LLM الخاص بـ OpenHands، واستخدم مستودعًا محددًا صراحةً مع تحديد مجموعات نتائج GitHub بحد أقصى يتراوح بين 3 و5 عناصر. إذا كان إصدار Agent Canvas الخاص بك يعرض إعدادات condenser، فاضبط الحد الأقصى لرموز condenser بحيث يكون أقل من نافذة سياق Lemonade.

## الخطوات التالية

- أضف ملخصًا أسبوعيًا يقتصر على الإصدارات.
- أضف أتمتة مُشغَّلة بأحداث GitHub لتنبيهات أسرع عند طلبات السحب أو الدفع.
- وجّه نفس الملخص إلى Notion أو Linear أو أداة أخرى مدعومة بـ MCP.

## الموارد

- [دلائل AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [وثائق Lemonade Server](https://lemonade-server.ai/docs)
- [مستودع ملحقات OpenHands](https://github.com/OpenHands/extensions)
- [خوادم Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [حزمة Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->