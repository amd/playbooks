<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## نظرة عامة

يقضي المطورون وقتًا طويلًا في حلقات متكررة وصغيرة: مراجعة طلبات السحب (pull requests) الموسومة، والرد على تعليقات GitHub، وفرز المشكلات الجديدة، وتحويل مواضيع Slack إلى ملاحظات اجتماعات يومية أو متابعات للحوادث، وتتبع إشارات الإصدارات أو الأبحاث.
كل حلقة مألوفة، لكنها لا تزال تتطلب حكمًا: جمع السياق الصحيح، وتحديد ما هو مهم، ونشر تحديث واضح حيث يعمل الفريق بالفعل.

تحوّل [أتمتة OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) هذه الحلقات إلى محادثات وكيل مُجدولة أو مُفعّلة بالأحداث: تشغيلات يمكن فيها لوكيل برمجيات الذكاء الاصطناعي قراءة السياق، واستدعاء الأدوات، وإنتاج تحديث.
تتبع قوالب الأتمتة المشتركة في كتالوج إضافات OpenHands هذا النمط لمراجعة طلبات السحب في GitHub، ومراقبة المستودعات، وفرز مشكلات Linear، ومراجعات ما بعد الحوادث، وملخصات الاجتماعات اليومية في Slack، وملخصات الأبحاث: تستيقظ الأتمتة، وتستخدم تكاملات مُهيّأة مثل GitHub أو Slack لجلب السياق، وتُفكّر في ذلك السياق باستخدام نموذج لغوي كبير (LLM)، وتكتب نتيجة.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) هو مستوى التحكم المحلي لبناء واختبار تلك الأتمتة.
في هذا الدليل، يُشغّل خادم وكيل OpenHands (OpenHands Agent Server)، وهو العملية الخلفية التي تُنفّذ محادثات الوكيل، ويربط الوكيل بخدمات خارجية مثل GitHub وSlack.

للحفاظ على سير العمل على نظام AMD الخاص بك، يتحدث الوكيل إلى نموذج محلي يُقدَّم عبر Lemonade Server.
يعرض Lemonade هذا النموذج من خلال واجهة برمجية متوافقة مع OpenAI، بحيث يمكن لـ Agent Canvas تهيئته كنقطة نهاية بعيدة بأسلوب OpenAI، بينما يبقى النموذج والمُطالبة (prompt) وسياق سير العمل محليًا.

في هذا الدليل، ستبني أتمتة واحدة ملموسة: ملخصًا تطويريًا مُجدولًا من GitHub إلى Slack.
يستخدم هذا GitHub لفحص نشاط المستودع الأخير، وSlack لنشر الملخص، واستدعاءات واجهة برمجة Agent Canvas لتهيئة الأتمتة واختبارها، وLemonade لتشغيل النموذج اللغوي الكبير محليًا.

![رسم بياني معماري يوضح GitHub MCP، وأتمتة OpenHands، وLemonade Server، وSlack MCP](assets/00-architecture-overview.png)

## ما الذي ستتعلمه

- كيفية تشغيل Lemonade Server والتحقق من أن النموذج المحلي يستجيب لطلبات الدردشة
- كيفية إطلاق Agent Canvas وتوجيه خادم الوكيل الخاص به نحو نموذج لغوي كبير محلي
- كيفية تثبيت خوادم بروتوكول سياق النموذج (Model Context Protocol - MCP) الخاصة بـ GitHub وSlack من خلال واجهة برمجة تطبيقات خادم الوكيل
- كيفية إنشاء وإطلاق أتمتة OpenHands مُجدولة تنشر ملخصًا تطويريًا على Slack
- كيفية استكشاف أكثر أعطال النموذج المحلي والأتمتة شيوعًا وإصلاحها

## المفاهيم الأساسية

| المفهوم | ما هو | أين يندرج في هذا الدليل |
| --- | --- | --- |
| Lemonade Server | منصة تقديم نماذج لغوية كبيرة محلية مبنية لأجهزة AMD، تعرض واجهة برمجية متوافقة مع OpenAI. بياناتك لا تغادر جهازك أبدًا. | يُشغّل النموذج الذي يُشغّل الوكيل. |
| OpenHands Agent Server | العملية الخلفية التي تُنفّذ محادثات وكيل OpenHands. | يستضيف الوكيل، وملفه التعريفي للنموذج اللغوي الكبير، وخوادم MCP الخاصة به. |
| Agent Canvas | مستوى التحكم المحلي لـ OpenHands الذي يُشغّل خادم الوكيل وواجهة مستخدم لفحص تشغيلات الوكيل. | يُطلق الخواديم الخلفية ويوفّر واجهة برمجة التطبيقات التي تستدعيها. |
| خادم MCP | خادم بروتوكول سياق النموذج الذي يمنح الوكيل أدوات لخدمة خارجية مثل GitHub أو Slack. | يتيح للوكيل قراءة GitHub والكتابة إلى Slack. |
| أتمتة OpenHands | محادثة وكيل مُجدولة أو مُفعّلة بالأحداث تجلب السياق، وتُفكّر فيه، وتكتب نتيجة في مكان ما. | ملخص GitHub-إلى-Slack الذي تبنيه هنا. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> تستفيد أعباء عمل وكيل البرمجة من نموذج أكبر ونافذة سياق أوسع.
> استخدم 32 جيجابايت على الأقل من ذاكرة النظام، ويُفضّل 64 جيجابايت أو أكثر للنماذج الأكبر بصيغة GGUF.
<!-- @device:end -->

## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## المتطلبات الأساسية

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas); host npm is only used by CI to resolve the MCP packages. -->
<!-- @prereq:docker,nodejs,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

تحتاج إلى:

- تثبيت Lemonade Server باتباع [دليل تثبيت Lemonade](https://lemonade-server.ai/docs/guide/install/) القياسي.

<!-- @os:linux -->
- Node.js الإصدار 22.12 أو أحدث مع `npm`، يُستخدمان لتثبيت واجهة سطر أوامر Agent Canvas المنشورة وتشغيل خوادم MCP باستخدام `npx`.
- `uv`، وهو مدير حزم Python الذي يستخدمه Agent Canvas لبناء بيئة خادم الوكيل. إذا لم يكن مُثبّتًا بالفعل، ثبّته من [دليل تثبيت uv](https://docs.astral.sh/uv/getting-started/installation/).
- إصدار منشور حديثًا من حزمة `@openhands/agent-canvas` مع إعدادات وكيل مبنية على المخطط (schema-driven)، و`LLMSummarizingCondenserSettings.max_tokens`، ودعم `custom_tokenizer` للنموذج اللغوي الكبير.
- حزمة `transformers` الخاصة بـ Python متاحة في بيئة خادم الوكيل. وهي مطلوبة لحساب الرموز (tokens) الخاصة بقالب الدردشة عند ضبط `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)، مُثبّت وقيد التشغيل. على Windows، تعمل حزمة Agent Canvas من صورة Docker المنشورة، التي تضم Node.js وuv وtransformers وحزمة `@openhands/agent-canvas`، لذا لا تحتاج إلى تثبيت هذه العناصر على المضيف.
<!-- @os:end -->

- رمز GitHub بصلاحية قراءة للمستودع الذي تريد تلخيصه.
- رمز بوت Slack (`xoxb-...`) بصلاحيات `chat:write` وقراءة القناة.
- معرّف فريق Slack (`T...`).
- معرّف قناة Slack (`C...`) التي سيُنشر فيها الملخص.

قم بدعوة تطبيق Slack إلى القناة المستهدفة قبل اختبار الأتمتة.
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

تُستخدم هاتان المتغيرتان في أوامر التحقق أدناه.
يتم إدخال النموذج والمحلل اللغوي (tokenizer) وإعدادات LLM الأخرى مباشرةً في واجهة Agent Canvas UI في الخطوات اللاحقة، لذا تظهر قيمها الحرفية مباشرةً حيث تحتاج إليها.

تُدخَل القيم التالية في واجهة Agent Canvas UI في الخطوات اللاحقة.
اضبطها هنا حتى تتمكن من نسخها لاحقًا:

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

استخدم قيمة صريحة بصيغة `owner/repo` لـ `GITHUB_REPO_FILTER`.
قد تُرجع أحرف البدل الواسعة الخاصة بالمؤسسات سياق MCP كبيرًا جدًا بالنسبة للنماذج المحلية.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. تشغيل خادم Lemonade

شغّل النموذج من واجهة سطر الأوامر الخاصة بـ Lemonade:

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

> **اختر نموذجًا يناسب عتادك.** يُعد `Qwen3.6-35B-A3B-GGUF` (بحجم ~20 جيجابايت) نموذجًا قويًا لهذا سير العمل لكنه يحتاج إلى مجمّع ذاكرة كبير.
> إذا كان جهازك يمتلك ذاكرة محدودة أو ذاكرة GPU VRAM محدودة، اختر نموذج GGUF أصغر من مكتبة نماذج Lemonade واستخدم معرّف هذا النموذج (والمحلل اللغوي المطابق له) في جميع أنحاء هذا الدليل الإرشادي.

> **ملاحظة:** يقوم أول تشغيل لأمر `lemonade run` بتنزيل النموذج إذا لم يكن موجودًا بالفعل، وقد يستغرق ذلك بعض الوقت حسب حجم النموذج وسرعة اتصالك.

يوفّر Lemonade واجهة برمجة تطبيقات متوافقة مع OpenAI على العنوان:

```text
http://127.0.0.1:13305/api/v1
```

اختياري: إذا لم تكن واجهة Agent Canvas أو أداة تشغيل الأتمتة على نفس الجهاز، انشر نقطة نهاية Lemonade عبر نفق آمن واستخدم عنوان URL الخاص بـ HTTPS كعنوان أساسي لـ LLM:
يتيح [ngrok](https://ngrok.com/) عرض منفذ محلي على الإنترنت عبر عنوان URL آمن بصيغة HTTPS؛ يتطلب ذلك حساب ngrok مجاني، وتستبدل `YOUR_NGROK_DOMAIN.ngrok-free.dev` بنطاقك المحجوز الخاص بك:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. التحقق من النموذج المحلي

تأكد من أن Lemonade يمكنه تقديم النموذج المُختار:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

ثم أرسل طلب محادثة صغير:

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

ثم أرسل طلب محادثة صغير:

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
ثبّت حزمة Agent Canvas المنشورة وشغّل المكدس الكامل:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

إذا فشل تثبيت npm العام بخطأ في الأذونات، راجع إدخال استكشاف أخطاء أذونات npm وإصلاحها أدناه.

افتراضيًا، يبدأ تشغيل Agent Canvas على العنوان `http://localhost:8000`.
افتح هذا العنوان في متصفحك.
المنفذ ليس له خصوصية—إذا كان المنفذ 8000 مستخدَمًا بالفعل، مرّر أي منفذ متاح باستخدام `--port` (أو `-p`).
يجب أن تظهر الخلفية المحلية الافتراضية بحالة سليمة في الشاشة الرئيسية.

> **ملاحظة:** يقوم أول تشغيل ببناء بيئة بايثون الخاصة بخادم الوكيل (Agent Server) المُدارة بواسطة `uv`، لذا قد يستغرق الأمر بضع دقائق قبل أن تُبلغ الخلفية عن حالتها السليمة.

يُشغّل أمر `agent-canvas` خادم الوكيل، وخلفية الأتمتة، والواجهة الأمامية للويب معًا.
تحتاج فقط إلى هذا الأمر الواحد لتشغيل OpenHands محليًا.
يُكوّن باقي هذا الدليل الإرشادي كل شيء من خلال واجهة Agent Canvas UI في متصفحك.
<!-- @os:end -->

<!-- @os:windows -->
على نظام Windows، شغّل صورة حاوية Agent Canvas المنشورة باستخدام Docker Desktop.
تحتوي الصورة على خادم الوكيل، وخلفية الأتمتة، والواجهة الأمامية للويب، لذا لست بحاجة إلى تثبيت Node.js أو `uv` أو واجهة سطر الأوامر على الجهاز المضيف.

أولًا، أنشئ مجلدات الإعدادات ومساحة العمل التي تُركّبها الحاوية:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

اسحب الصورة المنشورة (حوالي 6 جيجابايت؛ وهي عامة، لذا لا حاجة لتسجيل الدخول):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

ثم شغّل المكدس:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

افتح `http://localhost:8000/canvas` في متصفحك.
إذا كان المنفذ 8000 مستخدَمًا بالفعل، قم بتعيين منفذ مضيف مختلف، على سبيل المثال `-p 8080:8000`، وافتح `http://localhost:8080/canvas` بدلًا من ذلك.

> **ملاحظة:** يقوم أول تشغيل ببناء بيئة خادم الوكيل داخل الحاوية، لذا قد يستغرق الأمر بضع دقائق قبل أن تُبلغ الخلفية عن حالتها السليمة.

يحافظ التركيب `.openhands` على استمرارية ملف تعريف LLM وخوادم MCP والأتمتة الخاصة بك عبر عمليات إعادة تشغيل الحاوية.
يُكوّن باقي هذا الدليل الإرشادي كل شيء من خلال واجهة Agent Canvas UI في متصفحك على العنوان `http://localhost:8000/canvas`.
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
## 4. تكوين نموذج LLM المحلي في واجهة المستخدم

عند التشغيل الأول، يفتح Agent Canvas تدفق تهيئة أولي.
في هذا التدفق:

1. أبقِ **OpenHands** محددًا كوكيل وانقر على **Next**.
2. في **Set up your LLM**، اختر **Advanced**.
3. أبقِ **Authentication** مضبوطًا على **API key**.
4. اضبط **Custom Model** إلى `openai/Qwen3.6-35B-A3B-GGUF`.
5. اضبط **Base URL** إلى `http://127.0.0.1:13305/api/v1`.
6. في **API Key**، أدخل أي قيمة نائبة غير فارغة مثل `lemonade-local`. لا يتطلب Lemonade مفتاحًا حقيقيًا، لكن عميل OpenHands يحتاج إلى قيمة لإرسالها.

<!-- @os:windows -->
> **Windows (Docker):** يعمل Agent Server داخل الحاوية، لذا اضبط **Base URL** إلى `http://host.docker.internal:13305/api/v1` بدلًا من `http://127.0.0.1:13305/api/v1`.
> من داخل الحاوية، يشير `127.0.0.1` إلى الحاوية نفسها؛ بينما يصل `host.docker.internal` إلى Lemonade العامل على مضيف Windows، ويوفر Docker Desktop اسم المضيف هذا تلقائيًا.
<!-- @os:end -->

يجب أن تبدو حقول الاتصال كما يلي.
حقل مفتاح API يكون مموهًا من قبل واجهة المستخدم.

![إعدادات LLM المتقدمة عند أول استخدام لـ Agent Canvas مع نموذج Lemonade وعنوان URL الأساسي المحلي](assets/01-llm-advanced-settings.png)

ثم اختر **All** واضبط حقول النموذج المحلي الإضافية:

1. انتقل إلى **Custom Tokenizer** واضبطه إلى `Qwen/Qwen3.6-35B-A3B`.
2. انتقل إلى **LiteLLM Extra Body** واضبطه إلى `{"enable_thinking": true}`.
3. انقر على **Next**.

![علامة تبويب LLM All عند أول استخدام لـ Agent Canvas مع محلل Qwen المخصص](assets/02-llm-all-tokenizer-settings.png)

![علامة تبويب LLM All عند أول استخدام لـ Agent Canvas مع تكوين LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

يجب أن تُظهر إعدادات LLM ما يلي:

| الحقل | القيمة |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

تُعلم البادئة `openai/` مكتبة LiteLLM باستخدام تنسيق طلبات متوافق مع OpenAI مقابل نقطة نهاية Lemonade.
المحلل المخصص هو محلل Hugging Face الأصلي لنموذج GGUF؛ فهو يتيح لـ OpenHands عدّ رموز قالب الدردشة نفسها التي يراها خادم النموذج المحلي.
لا يعرض نموذج LLM الحالي عند أول استخدام إعدادات المُلخِّص (condenser).
إذا كان إصدارك من Agent Canvas يعرض إعدادات المُلخِّص لاحقًا ضمن **Settings > LLM**، استخدم `llm_summarizing` واضبط الحد الأقصى للرموز أقل من نافذة سياق Lemonade، مثل `56000`.

## 5. تثبيت خوادم GitHub وSlack MCP

في واجهة مستخدم Agent Canvas، افتح **Customize** (أو **Settings > MCP**) لإضافة خوادم MCP التي تمنح الوكيل أدوات للتعامل مع GitHub وSlack.
تُرسل قيم الرموز المميزة فقط إلى Agent Server المحلي الخاص بك وتُحفظ كإعدادات مشفرة.

<!-- @os:windows -->
> **Windows (Docker):** تعمل أوامر خادم `npx` MCP أدناه داخل الحاوية، التي تتضمن بالفعل Node.js، لذا لا يتم تثبيت أي شيء إضافي على المضيف.
> نظرًا لأن `.openhands` مُثبَّت (mounted)، تستمر خوادم MCP ورموزها المميزة عبر إعادة تشغيل الحاوية.
<!-- @os:end -->

### خادم GitHub MCP

أضف خادم MCP جديدًا بهذه الإعدادات:

| الحقل | القيمة |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = رمز GitHub الخاص بك |

استخدم رمز GitHub بإذن قراءة للمستودع الذي تريد تلخيصه.

### خادم Slack MCP

أضف خادم MCP ثانيًا بهذه الإعدادات:

| الحقل | القيمة |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = معرف قناة الملخص الخاصة بك |

اضبط `SLACK_CHANNEL_IDS` إلى معرف قناة الملخص (نفس قيمة `SLACK_DIGEST_CHANNEL`) حتى لا يحتاج الوكيل إلى تصفح كل قناة Slack.

بعد إضافة كلا الخادمين، استخدم زر **Test** على كل منهما للتأكد من أنه يتصل ويُعلن عن الأدوات.
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

في واجهة مستخدم Agent Canvas، افتح صفحة **Automations** وأنشئ أتمتة جديدة:

1. اختر **Create automation** وحدد النوع **Prompt preset**.
2. اضبط **Name** إلى `GitHub Development Digest to Slack`.
3. اضبط **Prompt** إلى النص التالي، مع استبدال العناصر النائبة الخاصة بالمستودع والقناة بقيمك الخاصة:

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

4. اضبط **Trigger** إلى **Cron** بالجدولة `0 9 * * 1-5` (9 صباحًا أيام الأسبوع) واضبط **Timezone** إلى منطقتك الزمنية، مثلًا `America/New_York`.
5. اضبط **Timeout** إلى `900` ثانية.
6. احفظ الأتمتة.

تُظهر صفحة تفاصيل الأتمتة الأتمتة الجديدة مع مُشغِّل cron الخاص بها ونقطة دخول prompt preset التي تم إنشاؤها.

![صفحة تفاصيل الأتمتة في Agent Canvas بعد الإنشاء](assets/05-automation-created.png)
## 7. اختبار الأتمتة

من صفحة تفاصيل الأتمتة في واجهة Agent Canvas:

1. انقر على **Run now** (أو **Dispatch**) لتشغيل الأتمتة مرة واحدة فورًا.
2. راقب قائمة التشغيلات في نفس الصفحة. يجب أن ينتقل آخر تشغيل إلى الحالة `COMPLETED`.
3. افتح قناة Slack المستهدفة لديك. يجب أن تحتوي على الملخص الذي تم إنشاؤه.

لست بحاجة لانتظار تفعيل الجدولة عبر cron—فميزة **Run now** تُطلق تشغيلًا عند الطلب بحيث يمكنك التأكد من أن الـ prompt واتصالات MCP والنشر على Slack تعمل جميعها بشكل صحيح قبل الاعتماد على الجدولة.

![اكتمال تشغيل الأتمتة بنجاح في Agent Canvas](assets/06-automation-run-completed.png)

![قناة Slack تعرض ملخص OpenHands الذي تم إنشاؤه](assets/07-slackbot-message.png)

## استكشاف الأخطاء وإصلاحها

<!-- @os:windows -->
- **منفذ Docker رقم 8000 مستخدم بالفعل:** قم بربط منفذ مضيف مختلف، على سبيل المثال `docker run ... -p 8080:8000 ...`، ثم افتح `http://localhost:8080/canvas`.
- **فشل أمر `docker pull` بسبب خطأ في بيانات الاعتماد** (على سبيل المثال، "A specified logon session does not exist"): قم بتشغيل أمر pull من جلسة Windows تفاعلية، أو قم بسحب الصورة مسبقًا. الصورة عامة، لذا لا حاجة لتنفيذ `docker login`.
- **تُحمَّل الواجهة لكن الخلفية غير سليمة:** يقوم أول تشغيل ببناء بيئة Agent Server داخل الحاوية. انتظر دقيقة ثم أعد التحميل، ثم تحقق من `docker logs <container>` لمتابعة التقدم.
- **لا يمكن لـ Agent Canvas الوصول إلى Lemonade من داخل الحاوية:** اضبط **Base URL** للـ LLM على `http://host.docker.internal:13305/api/v1` (وليس `127.0.0.1`)، وتأكد من أن Lemonade يعمل على مضيف Windows.
<!-- @os:end -->

- **Lemonade متوقف:** أعد تشغيله باستخدام أمر `lemonade run "${LEMONADE_MODEL}"` الموضح في الخطوة 1، ثم أعد تشغيل فحص الحالة الصحية.
- **فشل الأمر `npm install -g` بسبب خطأ في الأذونات:** على Linux أو WSL، قم بتهيئة دليل npm عام مملوك للمستخدم، وأضفه إلى ملف بدء تشغيل shell الخاص بك، ثم أعد تثبيت Agent Canvas مرة أخرى:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

إذا كنت تستخدم `zsh`، أضف نفس سطر `export PATH=...` إلى `~/.zshrc` بدلاً من `~/.bashrc`.
- **يرفض Agent Canvas إعدادات LLM بعد ضبط `custom_tokenizer`:** قم بتثبيت `transformers` في بيئة Python الخاصة بـ Agent Server، وأعد تشغيل Agent Canvas إذا لزم الأمر، ثم أعد محاولة حفظ إعدادات LLM. يتطلب OpenHands وجود Transformers لتحميل قالب محادثة الـ tokenizer عند ضبط `custom_tokenizer`.
- **لا يمكن لـ Agent Canvas الوصول إلى Lemonade:** تحقق من `curl -fsS "${LEMONADE_BASE_URL}/health"` وتأكد من أن الـ base URL المُدخل في نموذج LLM عند أول استخدام أو في **Settings > LLM** يطابق نقطة النهاية المحلية قيد التشغيل أو نفق HTTPS.
- **لم يتم حفظ إعدادات LLM:** تأكد من أنك نقرت على **Next** بعد إدخال القيم. أعد فتح **Settings > LLM** للتأكد من أن القيم محفوظة.
- **لا يمكن لـ GitHub MCP رؤية المستودعات الخاصة:** تأكد من أن رمز GitHub يملك صلاحية قراءة على المستودع المستهدف وأن زر **Test** الخاص بـ MCP في **Customize** يُظهر أدوات GitHub.
- **يمكن لـ Slack قراءة القنوات لكن لا يمكنه النشر:** قم بدعوة تطبيق Slack إلى القناة المستهدفة وتأكد من أن البوت يملك صلاحية `chat:write`.
- **تسرد الأتمتة عددًا كبيرًا جدًا من قنوات Slack:** استخدم معرّف قناة Slack واضبط `SLACK_CHANNEL_IDS` في خادم Slack MCP ضمن **Customize**.
- **يفشل تشغيل الأتمتة أو يتجاوز السياق:** تأكد من أن Lemonade تم تشغيله بقيمة `ctx_size=65536`، وتأكد من أن LLM الخاص بـ OpenHands يحتوي على `custom_tokenizer` مضبوطًا، واستخدم مستودعًا محددًا مع تحديد نتائج GitHub بحد أقصى يتراوح بين 3 إلى 5 عناصر. إذا كانت نسخة Agent Canvas لديك تعرض إعدادات condenser، فاضبط الحد الأقصى لرموز condenser أقل من نافذة سياق Lemonade.

## الخطوات التالية

- إضافة ملخص أسبوعي خاص بالإصدارات فقط.
- إضافة أتمتة مُفعَّلة بأحداث GitHub لإرسال تنبيهات أسرع بشأن طلبات السحب أو عمليات الدفع.
- توجيه نفس الملخص إلى Notion أو Linear أو أداة أخرى مدعومة بـ MCP.

## الموارد

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [توثيق Lemonade Server](https://lemonade-server.ai/docs)
- [مستودع إضافات OpenHands](https://github.com/OpenHands/extensions)
- [خوادم بروتوكول سياق النموذج (Model Context Protocol)](https://github.com/modelcontextprotocol/servers)
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