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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## نظرة عامة

[OpenHands](https://github.com/All-Hands-AI/OpenHands) هو عامل برمجي مدعوم بالذكاء الاصطناعي
قادر على كتابة الشيفرة البرمجية، وتشغيل الأوامر، وتصفح الويب، وتحرير الملفات في مساحة عمل
حقيقية. بدلاً من نسخ الاقتراحات من نافذة محادثة، توجّه العامل إلى مجلد مشروع
وتتركه ينجز العمل: تنفيذ ميزة، إصلاح خلل، كتابة اختبارات، أو شرح قاعدة شيفرة.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) هو واجهة المتصفح
الموصى بها لتشغيل OpenHands. يقوم أمر واحد وهو `agent-canvas` بتشغيل خادم
العامل، والواجهة الخلفية للأتمتة، والواجهة الأمامية للويب معًا، بحيث يمكنك
إجراء محادثة مع العامل من متصفحك.

للحفاظ على كل شيء على نظام AMD الخاص بك، يتحدث العامل إلى نموذج محلي يُقدَّم
عبر Lemonade Server. يعرض Lemonade هذا النموذج من خلال واجهة برمجة تطبيقات
متوافقة مع OpenAI، لذا يمكن لـ Agent Canvas تهيئته مثل أي نقطة نهاية أخرى
بأسلوب OpenAI بينما يبقى النموذج وشيفرتك وسياق المحادثة كلها على جهازك.

في هذا الدليل التطبيقي، ستبدأ نموذجًا محليًا، وتُطلق Agent Canvas، وتوجّهه
نحو ذلك النموذج، وتُشغّل أول مهمة برمجة لك على مجلد مشروع حقيقي.

## ما ستتعلمه

- كيفية بدء تشغيل Lemonade Server والتأكد من أن نموذجًا محليًا يستجيب لطلبات المحادثة
- كيفية تثبيت وإطلاق Agent Canvas من حزمة npm
- كيفية تهيئة Agent Canvas لاستخدام نموذج Lemonade محلي كنموذج اللغة الكبير (LLM)
- كيفية بدء محادثة OpenHands ومشاهدة العامل يُحرر الملفات ويُشغّل
  الأوامر في مساحة عمل
- كيفية مراجعة ما غيّره العامل وتوجيهه برسائل متابعة

## المفاهيم الأساسية

| المفهوم | ما هو | مكانه في هذا الدليل التطبيقي |
| --- | --- | --- |
| Lemonade Server | منصة محلية لتقديم نماذج اللغة الكبيرة مصممة لأجهزة AMD تعرض واجهة برمجة تطبيقات متوافقة مع OpenAI. بياناتك لا تغادر جهازك أبدًا. | يُشغّل النموذج الذي يُشغّل العامل. |
| OpenHands | عامل برمجي مدعوم بالذكاء الاصطناعي يقرأ الملفات ويحررها، ويشغّل أوامر الصدفة، ويتصفح الويب داخل مساحة عمل. | العامل الذي تُوجّهه من المحادثة. |
| Agent Canvas | واجهة المتصفح والواجهة الخلفية التي تُشغّل محادثات OpenHands وتُظهر استدعاءات الأدوات وتغييرات الملفات. | تُطلق المجموعة الكاملة وتستضيف محادثتك. |
| مساحة العمل | مجلد المشروع الذي يُسمح للعامل بقراءته وتعديله. | هدف تعديلات العامل وأوامره. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> تستفيد سير عمل عامل البرمجة من نموذج أكبر ونافذة سياق أوسع. استخدم
> ذاكرة نظام لا تقل عن 32 غيغابايت، ويُفضّل 64 غيغابايت أو أكثر لنماذج GGUF الأكبر.
<!-- @device:end -->

## ضبط تهيئة الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرمجيات

<!-- @require:software-update -->
<!-- @device:end -->

## المتطلبات الأساسية


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

ستحتاج إلى:

- تثبيت Lemonade Server وقدرته على تقديم النموذج أدناه.

<!-- @os:linux -->
- Node.js الإصدار 22.12 أو أحدث و`npm` (يستخدمهما أداة سطر الأوامر `agent-canvas`).
- `uv`، وهو مدير حزم Python الذي يستخدمه Agent Canvas لإدارة بيئة
  خادم العامل. إذا لم يكن نظامك يحتوي عليه بالفعل، فقم بتثبيته من
  [دليل تثبيت uv](https://docs.astral.sh/uv/getting-started/installation/)
  قبل إطلاق Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)،
  مثبتًا وقيد التشغيل. على Windows، تعمل مجموعة Agent Canvas من
  صورة Docker المنشورة، والتي تحزّم Node.js و`uv` وحزمة
  `@openhands/agent-canvas`، لذا لست بحاجة لتثبيت هذه العناصر على الجهاز المضيف.
<!-- @os:end -->

- مجلد مشروع للعمل فيه. يمكن أن يكون هذا أي مستودع git محلي أو دليل شيفرة
  تريد أن يعمل عليه العامل.

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. بدء تشغيل Lemonade Server

ابدأ تشغيل النموذج من واجهة سطر أوامر Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **اختر نموذجًا يناسب جهازك.** يُعد `Qwen3.6-35B-A3B-GGUF` (~20 غيغابايت) نموذج ترميز قويًا لكنه يحتاج إلى مجموعة ذاكرة كبيرة. إذا كان جهازك يمتلك ذاكرة محدودة أو ذاكرة GPU VRAM محدودة، فاختر بدلاً منه نموذج GGUF أصغر من مكتبة نماذج Lemonade واستخدم معرّف ذلك النموذج طوال هذا الدليل التطبيقي.

> **ملاحظة:** يقوم أمر `lemonade run` الأول بتنزيل النموذج إذا لم يكن موجودًا بالفعل، وهو ما قد يستغرق بعض الوقت حسب حجم النموذج وسرعة اتصالك.

يعرض Lemonade واجهة برمجة تطبيقات متوافقة مع OpenAI على العنوان:

```text
http://127.0.0.1:13305/api/v1
```

## 2. التحقق من النموذج المحلي

تأكد من أن Lemonade قادر على تقديم النموذج المُختار:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

ثم أرسل طلب محادثة صغيرًا:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

إذا أعاد هذا مصفوفة `choices`، فإن Lemonade جاهز لـ Agent Canvas.

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
model_id = "${lemonade_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
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

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->
## 3. تثبيت وتشغيل Agent Canvas

<!-- @os:linux -->
ثبّت حزمة Agent Canvas المنشورة بشكل عام:

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

ثم ابدأ تشغيل المجموعة الكاملة من طرفية:

```bash
agent-canvas
```

بشكل افتراضي، يبدأ Agent Canvas على `http://localhost:8000`. افتح هذا الرابط في
متصفحك. المنفذ ليس مميزًا — إذا كان المنفذ 8000 مستخدمًا بالفعل، مرر أي
منفذ متاح باستخدام `--port` (أو `-p`) عند تشغيل Agent Canvas:

```bash
agent-canvas --port 3000
```

ثم افتح `http://localhost:3000` بدلاً من ذلك. يجب أن تظهر الواجهة الخلفية المحلية الافتراضية
بحالة سليمة على الشاشة الرئيسية.

يبدأ الأمر `agent-canvas` خادم الوكيل، والواجهة الخلفية للأتمتة، وواجهة
الويب الأمامية معًا. تحتاج فقط إلى هذا الأمر الواحد لتشغيل OpenHands
محليًا.

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
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
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
على نظام Windows، شغّل صورة حاوية Agent Canvas المنشورة باستخدام Docker Desktop.
تحتوي الصورة على Agent Server، والواجهة الخلفية للأتمتة، وواجهة الويب الأمامية، لذا
لست بحاجة إلى تثبيت Node.js أو `uv` أو الواجهة النصية على الجهاز المضيف.

أولاً، أنشئ مجلدي التهيئة ومساحة العمل التي ستقوم الحاوية بربطهما (mount):

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

اسحب الصورة المنشورة (وهي عامة، لذا لا حاجة لتسجيل الدخول):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

ثم ابدأ تشغيل المجموعة:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

افتح `http://localhost:8000/canvas` في متصفحك. إذا كان المنفذ 8000 مستخدمًا
بالفعل، اربط منفذ مضيف مختلف، على سبيل المثال `-p 8080:8000`، وافتح
`http://localhost:8080/canvas` بدلاً من ذلك.

> **ملاحظة:** يقوم أول تشغيل بتهيئة Agent Server داخل الحاوية،
> لذا قد يستغرق الأمر دقيقة أو دقيقتين قبل أن تُبلغ الواجهة الخلفية عن حالتها السليمة.

يحافظ الربط `.openhands` على ملف تعريف LLM الخاص بك وإعداداته عبر عمليات إعادة تشغيل
الحاوية. يقوم بقية هذا الدليل بتهيئة كل شيء من خلال واجهة مستخدم
Agent Canvas في متصفحك.

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
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

## 4. تهيئة نموذج اللغة الكبير المحلي

عند التشغيل الأول، يفتح Agent Canvas تدفق إعداد أولي. في هذا التدفق:

1. أبقِ **OpenHands** محددًا كالوكيل وانقر على **Next**.
2. في **Set up your LLM**، اختر **Advanced**.
3. أبقِ **Authentication** مضبوطًا على **API key**.
4. اضبط **Custom Model** على `openai/Qwen3.6-35B-A3B-GGUF`.
5. اضبط **Base URL** على `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > على نظام Windows، تعمل المجموعة داخل حاوية، والتي لا يمكنها الوصول إلى المضيف عبر
   > `127.0.0.1`. استخدم `http://host.docker.internal:13305/api/v1` بدلاً من ذلك حتى يتمكن
   > الوكيل الموجود داخل الحاوية من الوصول إلى Lemonade الذي يعمل على مضيف Windows.
   <!-- @os:end -->
6. في حقل **API Key**، أدخل أي نص بديل غير فارغ مثل `lemonade-local`.
   لا يتطلب Lemonade مفتاحًا حقيقيًا، لكن عميل OpenHands يحتاج إلى قيمة
   لإرسالها.
7. انقر على **Next**.

يجب أن تبدو إعدادات Advanced المكتملة كما يلي. حقل مفتاح API
مخفٍ بواسطة الواجهة.

![إعدادات Agent Canvas المتقدمة لنموذج اللغة الكبير عند أول استخدام مع نموذج Lemonade والرابط الأساسي المحلي](assets/01-llm-advanced-settings.png)

يحفظ Agent Canvas هذه القيم كملف تعريف LLM. إذا طلب إصدارك منك
تسمية ملف التعريف هذا، استخدم اسمًا بدون مسافات مثل `lemonade-local`. إذا غيّرت
النماذج لاحقًا، افتح **Settings > LLM** وحدّث نفس حقول Advanced. يمكنك
التبديل بين ملفات التعريف المحفوظة من مدخل الدردشة باستخدام الأمر `/model`.

## 5. فتح مساحة عمل

يمكن للوكيل قراءة وتعديل الملفات فقط داخل مساحة عمل تختارها. قبل
بدء مهمة، وجّه Agent Canvas إلى مجلد مشروعك:

1. من الشاشة الرئيسية، اختر **Open Workspace**.
2. حدد المجلد الذي يحتوي على مشروعك (على سبيل المثال، مستودع git
   تريد أن يعمل عليه الوكيل).
3. ابدأ محادثة جديدة في مساحة العمل هذه.

كل ما يقوم به الوكيل - قراءة الملفات، وتشغيل الأوامر، وتحرير الكود - يكون
محصورًا في تلك مساحة العمل.

![الشاشة الرئيسية لـ Agent Canvas بعد الإعداد الأولي](assets/02-agent-canvas-home.png)

## 6. تشغيل أول مهمة برمجية

مع فتح مساحة العمل واختيار نموذج اللغة الكبير المحلي، اكتب مهمة محددة في
الدردشة. المهمة الأولى الجيدة تكون صغيرة وقابلة للتحقق، على سبيل المثال:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

راقب الجدول الزمني للمحادثة. سيقوم OpenHands بما يلي:

- قراءة مساحة العمل لفهم التخطيط.
- إنشاء `hello.py` مع الدالة المطلوبة وكتلة الاختبار.
- تشغيل `python3 hello.py` اختياريًا للتحقق من الناتج.
- الإبلاغ عما فعله وأي ناتج للأوامر في الدردشة.

يجب أن ترى الملف الجديد يظهر في مساحة العمل، ويجب أن تصف رسالة الوكيل
النهائية التغيير الذي أجراه. هذه هي لحظة الإنجاز: كتب
الوكيل وشغّل كودًا حقيقيًا في مجلد مشروعك.

## 7. مراجعة الوكيل وتوجيهه

بعد أن ينتهي الوكيل من خطوة ما، راجع عمله قبل قبول الخطوة التالية:

- **تغييرات الملفات**: استخدم متصفح ملفات مساحة العمل أو عرض الفروقات
  (diff) الخاص بالوكيل لرؤية ما تمت إضافته أو تغييره أو حذفه بالضبط.
- **ناتج الأوامر**: وسّع أي أمر شغّله الوكيل لرؤية stdout و stderr
  ورمز الخروج.
- **المتابعات**: إذا لم تكن النتيجة كما تريد، رد في نفس
  المحادثة بتصحيح. يحتفظ الوكيل بالسياق السابق ويكرر
  العمل على نفس الملفات.

على سبيل المثال، إذا لم يطبع الاختبار التحية المتوقعة، رد:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

سيعيد الوكيل قراءة الملف، وتشغيل الأمر، وتشخيص المشكلة، وتعديل
الملف مرة أخرى - كل ذلك ضمن نفس المحادثة.
## استكشاف الأخطاء وإصلاحها

<!-- @os:linux -->
- **`agent-canvas` غير موجود في PATH:** أعد التثبيت باستخدام
  `npm install -g @openhands/agent-canvas` وتأكد من أن دليل الملفات الثنائية العام لـ npm
  موجود ضمن PATH قبل أن يتمكّن `agent-canvas` من التشغيل من طرفية جديدة.
- **يفشل `npm install -g` بخطأ في الأذونات:** قم بتهيئة دليل npm عام مملوك للمستخدم،
  ثم أعد فتح الطرفية وقم بتثبيت Agent Canvas مرة أخرى.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` مفقود:** قم بتثبيته من
  [دليل تثبيت uv](https://docs.astral.sh/uv/getting-started/installation/).
  يستخدم Agent Canvas أداة `uv` لإدارة بيئة Python الخاصة بخادم العميل (agent server).
<!-- @os:end -->

<!-- @os:windows -->
- **يفشل الاتصال عند تنفيذ `docker pull` أو `docker run`:** تأكد من أن Docker Desktop
  قيد التشغيل (أيقونة الحوت الخاصة به موجودة في شريط النظام) وأن المحرك قد
  انتهى من بدء التشغيل. يجب أن يعرض الأمر `docker version` كلا القسمين، Client وServer.
- **يبدأ الحاوية لكن الخلفية (backend) لا تصبح سليمة أبدًا:** يقوم أول تشغيل بتهيئة Agent Server
  داخل الحاوية؛ انتظر دقيقة أو دقيقتين، ثم تحقق من `docker logs <container>` بحثًا عن أخطاء.
- **لا يمكن للحاوية الوصول إلى Lemonade:** تصل الحاوية إلى المضيف عبر
  `host.docker.internal`. تأكد من أن Lemonade يعمل على مضيف Windows باستخدام
  `lemonade status`، واستخدم `http://host.docker.internal:13305/api/v1` كعنوان URL الأساسي
  عند تهيئة LLM.
<!-- @os:end -->

- **تُحمَّل واجهة المستخدم لكن الخلفية تظهر غير سليمة:** انتظر دقيقة أو دقيقتين حتى
  ينتهي خادم العميل من بدء التشغيل، ثم قم بالتحديث. إذا استمرت في الظهور بحالة غير سليمة، أعد تشغيل
  المكدس (stack) وتحقق من السجلات بحثًا عن أخطاء.
- **تفشل طلبات محادثة Lemonade بخطأ في الاتصال:** تأكد من أن
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` ينجح وأن
  Lemonade لا يزال يخدم النموذج باستخدام `lemonade status`.
- **يظهر العميل خطأً متعلقًا بطول السياق أو حد الرموز (tokens):** ابدأ محادثة
  جديدة حتى لا يحمل العميل سجلًا كبيرًا بشكل مفرط. إذا استمر حدوث ذلك، أعد تشغيل
  Lemonade بقيمة `ctx_size` أكبر من الافتراضية 65536 (على سبيل المثال `ctx_size=131072`)، إذا سمحت الذاكرة بذلك.
- **يقدّم العميل تعديلات منخفضة الجودة أو غير مكتملة:** انتقل إلى نموذج أكبر
  في Lemonade، أو أعطِ العميل مهمة أصغر وأكثر تحديدًا ودعه ينهيها قبل طلب
  التغيير التالي.

## الخطوات التالية

- جرّب مهمة أكبر في نفس مساحة العمل، مثل إضافة ملف اختبار وحدة أو
  إصلاح خطأ معروف، وراجع الفرق (diff) الناتج عن العميل قبل قبول التغيير.
- اربط خادم MCP مثل GitHub أو Slack ضمن **Customize** حتى
  يتمكن العميل من قراءة المشكلات (issues) أو نشر التحديثات أثناء عمله.
- احفظ عدة ملفات تعريف LLM (نموذج صغير وسريع ونموذج كبير وأقوى) وقم
  بالتبديل بينها باستخدام `/model` أثناء المحادثة.
- انتقل إلى [أتمتة OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) لتحويل
  حلقات التطوير المتكررة إلى تشغيلات مجدولة أو مُشغَّلة بالأحداث للعميل.

## الموارد

- [توثيق OpenHands](https://docs.openhands.dev/)
- [نظرة عامة على Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [إعداد Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [ملفات تعريف LLM وتهيئة النموذج](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [توثيق Lemonade Server](https://lemonade-server.ai/docs)

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