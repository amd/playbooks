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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) هو وكيل برمجيات ذكاء اصطناعي
قادر على كتابة الشيفرة، وتشغيل الأوامر، وتصفح الويب، وتحرير الملفات في مساحة
عمل حقيقية. بدلاً من نسخ الاقتراحات من نافذة محادثة، تُوجّه الوكيل إلى مجلد
مشروع وتدعه يقوم بالعمل: تنفيذ ميزة، أو إصلاح خطأ، أو كتابة اختبارات، أو شرح
قاعدة شيفرة.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) هي واجهة المتصفح
الموصى بها لتشغيل OpenHands. يقوم أمر واحد هو `agent-canvas` بتشغيل خادم
الوكيل، وخلفية الأتمتة، والواجهة الأمامية للويب معًا، بحيث يمكنك إجراء محادثة
مع الوكيل من متصفحك.

للحفاظ على كل شيء على نظامك من AMD، يتحدث الوكيل إلى نموذج محلي يقدمه
Lemonade Server. يعرض Lemonade هذا النموذج عبر واجهة برمجة تطبيقات متوافقة مع
OpenAI، بحيث يمكن لـ Agent Canvas تهيئته مثل أي نقطة نهاية أخرى على طراز
OpenAI، بينما يبقى النموذج وشيفرتك وسياق المحادثة جميعها على جهازك.

في هذا الدليل، ستبدأ تشغيل نموذج محلي، وتطلق Agent Canvas، وتوجّهه إلى ذلك
النموذج، وتنفّذ أول مهمة برمجية لك على مجلد مشروع حقيقي.

## ما الذي ستتعلمه

- كيفية بدء تشغيل Lemonade Server والتأكد من أن النموذج المحلي يستجيب لطلبات
  المحادثة
- كيفية تثبيت وتشغيل Agent Canvas من حزمة npm
- كيفية تهيئة Agent Canvas لاستخدام نموذج Lemonade محلي كنموذج اللغة الكبير (LLM)
- كيفية بدء محادثة OpenHands ومشاهدة الوكيل وهو يحرر الملفات وينفّذ الأوامر
  في مساحة عمل
- كيفية مراجعة ما قام الوكيل بتغييره وتوجيهه برسائل متابعة

## المفاهيم الأساسية

| المفهوم | ما هو | أين يندرج في هذا الدليل |
| --- | --- | --- |
| Lemonade Server | منصة محلية لخدمة نماذج اللغة الكبيرة مصممة لأجهزة AMD، تعرض واجهة برمجة تطبيقات متوافقة مع OpenAI. بياناتك لا تغادر جهازك أبدًا. | يشغّل النموذج الذي يُشغّل الوكيل. |
| OpenHands | وكيل برمجيات ذكاء اصطناعي يقرأ ويحرر الملفات، وينفّذ أوامر الصدفة، ويتصفح الويب داخل مساحة عمل. | الوكيل الذي تُشغّله من المحادثة. |
| Agent Canvas | واجهة المتصفح والخلفية التي تُشغّل محادثات OpenHands وتعرض استدعاءات الأدوات وتغييرات الملفات. | يُطلق المجموعة ويستضيف محادثتك. |
| مساحة العمل | مجلد المشروع الذي يُسمح للوكيل بقراءته وتعديله. | هدف تعديلات الوكيل وأوامره. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> تستفيد سير عمل الوكيل البرمجي من نموذج أكبر ونافذة سياق أوسع. استخدم على
> الأقل 32 جيجابايت من ذاكرة النظام، ويُفضّل استخدام 64 جيجابايت أو أكثر
> لنماذج GGUF الأكبر حجمًا.
<!-- @device:end -->

## ضبط تهيئة الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## المتطلبات الأساسية


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

تحتاج إلى:

- تثبيت Lemonade Server وقدرته على تقديم النموذج أدناه.

<!-- @os:linux -->
- Node.js الإصدار 22.12 أو أحدث، و`npm` (يُستخدمان بواسطة واجهة سطر الأوامر `agent-canvas`).
- `uv`، مدير حزم Python الذي يستخدمه Agent Canvas لإدارة بيئة خادم الوكيل. إذا
  لم يكن نظامك يحتوي عليه بالفعل، فثبّته من
  [دليل تثبيت uv](https://docs.astral.sh/uv/getting-started/installation/)
  قبل تشغيل Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop لنظام Windows](https://docs.docker.com/desktop/setup/install/windows-install/)،
  مثبّتًا وقيد التشغيل. على Windows، تُشغَّل مجموعة Agent Canvas من صورة
  Docker المنشورة، التي تتضمن Node.js و`uv` وحزمة `@openhands/agent-canvas`،
  لذا لا تحتاج إلى تثبيت هذه العناصر على المضيف.
<!-- @os:end -->

- مجلد مشروع تعمل فيه. يمكن أن يكون هذا أي مستودع git محلي أو دليل شيفرة
  تريد أن يعمل عليه الوكيل.

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

> **اختر نموذجًا يناسب عتادك.** `Qwen3.6-35B-A3B-GGUF` (~20 جيجابايت) هو نموذج برمجي قوي لكنه يحتاج إلى مجمع ذاكرة كبير. إذا كان جهازك يمتلك ذاكرة محدودة أو ذاكرة فيديو محدودة لوحدة معالجة الرسوميات (GPU VRAM)، اختر نموذج GGUF أصغر من مكتبة نماذج Lemonade بدلاً من ذلك، واستخدم معرّف ذلك النموذج في جميع أنحاء هذا الدليل.

> **ملاحظة:** يقوم أول تنفيذ لأمر `lemonade run` بتنزيل النموذج إذا لم يكن موجودًا بالفعل، وقد يستغرق ذلك بعض الوقت حسب حجم النموذج وسرعة اتصالك.

يعرض Lemonade واجهة برمجة تطبيقات متوافقة مع OpenAI عند:

```text
http://127.0.0.1:13305/api/v1
```

## 2. التحقق من النموذج المحلي

تأكد من أن Lemonade يستطيع تقديم النموذج المحدد:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

ثم أرسل طلب محادثة صغير:

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
قم بتثبيت حزمة Agent Canvas المنشورة بشكل عام:

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

بعد ذلك، ابدأ الحزمة الكاملة من الطرفية:

```bash
agent-canvas
```

بشكل افتراضي، يبدأ Agent Canvas على `http://localhost:8000`. افتح هذا الرابط في
متصفحك. المنفذ ليس خاصًا — إذا كان المنفذ 8000 مستخدمًا بالفعل، مرر أي
منفذ متاح باستخدام `--port` (أو `-p`) عند تشغيل Agent Canvas:

```bash
agent-canvas --port 3000
```

ثم افتح `http://localhost:3000` بدلاً من ذلك. يجب أن تظهر الواجهة الخلفية المحلية الافتراضية
بحالة سليمة على الشاشة الرئيسية.

يبدأ الأمر `agent-canvas` خادم الوكيل، والواجهة الخلفية للأتمتة، والواجهة
الأمامية للويب معًا. تحتاج فقط إلى هذا الأمر الواحد لتشغيل OpenHands
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
على Windows، قم بتشغيل صورة حاوية Agent Canvas المنشورة باستخدام Docker Desktop.
تحتوي الصورة على Agent Server، والواجهة الخلفية للأتمتة، والواجهة الأمامية للويب، لذا
لست بحاجة إلى تثبيت Node.js أو `uv` أو واجهة سطر الأوامر على الجهاز المضيف.

أولاً، أنشئ مجلدات الإعدادات ومساحة العمل التي ستقوم الحاوية بتركيبها:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

اسحب الصورة المنشورة (إنها عامة، لذا لا حاجة لتسجيل الدخول):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

ثم ابدأ تشغيل الحزمة:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

افتح `http://localhost:8000/canvas` في متصفحك. إذا كان المنفذ 8000 مستخدمًا بالفعل، قم
بتعيين منفذ مضيف مختلف، على سبيل المثال `-p 8080:8000`، وافتح
`http://localhost:8080/canvas` بدلاً من ذلك.

> **ملاحظة:** يقوم أول تشغيل بتهيئة Agent Server داخل الحاوية،
> لذا قد يستغرق الأمر دقيقة أو دقيقتين قبل أن تُبلّغ الواجهة الخلفية بأنها سليمة.

يحافظ تركيب `.openhands` على ملف تعريف LLM والإعدادات الخاصة بك عبر عمليات إعادة
تشغيل الحاوية. يقوم باقي هذا الدليل بتهيئة كل شيء من خلال واجهة مستخدم
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

عند أول تشغيل، يفتح Agent Canvas سير عمل تأهيلي. في هذا السير:

1. أبقِ **OpenHands** محددًا كوكيل وانقر على **Next**.
2. في **Set up your LLM**، اختر **Advanced**.
3. أبقِ **Authentication** مضبوطة على **API key**.
4. اضبط **Custom Model** على `openai/Qwen3.6-35B-A3B-GGUF`.
5. اضبط **Base URL** على `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > على Windows، تعمل الحزمة داخل حاوية، والتي لا يمكنها الوصول إلى المضيف عبر
   > `127.0.0.1`. استخدم `http://host.docker.internal:13305/api/v1` بدلاً من ذلك حتى يتمكن
   > الوكيل المُحوّى من الوصول إلى Lemonade العامل على مضيف Windows.
   <!-- @os:end -->
6. في حقل **API Key**، أدخل أي قيمة نائبة غير فارغة مثل `lemonade-local`.
   لا يتطلب Lemonade مفتاحًا حقيقيًا، لكن عميل OpenHands يحتاج إلى قيمة
   لإرسالها.
7. انقر على **Next**.

يجب أن تبدو إعدادات Advanced المكتملة كما يلي. حقل مفتاح الـ API
مُخفى بواسطة الواجهة.

![إعدادات Advanced لنموذج اللغة الكبير عند أول استخدام لـ Agent Canvas مع نموذج Lemonade والرابط الأساسي المحلي](assets/01-llm-advanced-settings.png)

يحفظ Agent Canvas هذه القيم كملف تعريف LLM. إذا طلب منك إصدارك
تسمية ملف التعريف هذا، استخدم اسمًا بدون مسافات مثل `lemonade-local`. إذا غيّرت
النماذج لاحقًا، افتح **Settings > LLM** وحدّث نفس حقول Advanced. يمكنك
التبديل بين ملفات التعريف المحفوظة من مربع إدخال الدردشة باستخدام الأمر `/model`.

## 5. فتح مساحة عمل

يمكن للوكيل قراءة الملفات وتعديلها فقط داخل مساحة عمل تختارها. قبل
بدء مهمة، وجّه Agent Canvas إلى مجلد مشروعك:

1. من الشاشة الرئيسية، اختر **Open Workspace**.
2. حدد المجلد الذي يحتوي على مشروعك (على سبيل المثال، مستودع git
   تريد أن يعمل عليه الوكيل).
3. ابدأ محادثة جديدة في مساحة العمل تلك.

كل ما يقوم به الوكيل—قراءة الملفات، وتشغيل الأوامر، وتعديل الشفرة—مقتصر
على مساحة العمل تلك.

![الشاشة الرئيسية لـ Agent Canvas بعد التأهيل](assets/02-agent-canvas-home.png)

## 6. تنفيذ أول مهمة برمجة

مع فتح مساحة العمل وتحديد نموذج اللغة الكبير المحلي، اكتب مهمة محددة في
الدردشة. المهمة الأولى الجيدة صغيرة وقابلة للتحقق، على سبيل المثال:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

راقب الجدول الزمني للمحادثة. سيقوم OpenHands بما يلي:

- قراءة مساحة العمل لفهم تخطيطها.
- إنشاء `hello.py` يحتوي على الدالة المطلوبة وكتلة الاختبار.
- تشغيل `python3 hello.py` اختياريًا للتحقق من الناتج.
- الإبلاغ عما قام به وأي ناتج أوامر في الدردشة.

يجب أن ترى الملف الجديد يظهر في مساحة العمل، ويجب أن تصف رسالة الوكيل
النهائية التغيير الذي أجراه. هذه هي لحظة النتيجة: كتب
الوكيل شفرة حقيقية وشغّلها في مجلد مشروعك.

## 7. مراجعة الوكيل وتوجيهه

بعد أن ينهي الوكيل خطوة ما، راجع عمله قبل قبول الخطوة التالية:

- **تغييرات الملفات**: استخدم متصفح ملفات مساحة العمل أو عرض الفروقات الخاص بالوكيل
  لرؤية ما الذي تمت إضافته أو تغييره أو حذفه بالضبط.
- **ناتج الأوامر**: وسّع أي أمر نفّذه الوكيل لرؤية stdout وstderr،
  ورمز الخروج.
- **المتابعات**: إذا لم تكن النتيجة ما أردته، رد في نفس
  المحادثة بتصحيح. يحتفظ الوكيل بالسياق السابق ويكرر
  العمل على نفس الملفات.

على سبيل المثال، إذا لم يطبع الاختبار التحية المتوقعة، رد:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

سيعيد الوكيل قراءة الملف، وتشغيل الأمر، وتشخيص المشكلة، وتعديل
الملف مرة أخرى—كل ذلك في نفس المحادثة.
## استكشاف الأخطاء وإصلاحها

<!-- @os:linux -->
- **`agent-canvas` غير موجود في PATH:** أعد التثبيت باستخدام
  `npm install -g @openhands/agent-canvas` وتأكد من أن دليل الملفات التنفيذية العام لـ npm
  موجود ضمن PATH قبل أن يصبح بالإمكان تشغيل `agent-canvas` من طرفية جديدة.
- **فشل تنفيذ `npm install -g` بسبب خطأ في الأذونات:** قم بتهيئة دليل npm عام مملوك للمستخدم،
  ثم أعد فتح الطرفية وثبّت Agent Canvas مرة أخرى.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` مفقود:** قم بتثبيته من
  [دليل تثبيت uv](https://docs.astral.sh/uv/getting-started/installation/).
  يستخدم Agent Canvas الأداة `uv` لإدارة بيئة Python الخاصة بخادم الوكيل.
<!-- @os:end -->

<!-- @os:windows -->
- **فشل `docker pull` أو `docker run` في الاتصال:** تأكد من أن Docker Desktop
  قيد التشغيل (أيقونة الحوت الخاصة به موجودة في شريط النظام) وأن المحرك قد
  انتهى من بدء التشغيل. يجب أن يعرض `docker version` قسمي Client وServer معًا.
- **يبدأ الحاوية لكن الواجهة الخلفية لا تصبح سليمة أبدًا:** يقوم التشغيل الأول
  بتهيئة Agent Server داخل الحاوية؛ امنحه دقيقة أو دقيقتين، ثم تحقق من
  `docker logs <container>` بحثًا عن الأخطاء.
- **لا تستطيع الحاوية الوصول إلى Lemonade:** تصل الحاوية إلى المضيف عبر
  `host.docker.internal`. تأكد من أن Lemonade يعمل على مضيف Windows باستخدام
  `lemonade status`، واستخدم `http://host.docker.internal:13305/api/v1` كعنوان
  URL الأساسي عند تهيئة LLM.
<!-- @os:end -->

- **تُحمّل الواجهة لكن الواجهة الخلفية تظهر غير سليمة:** انتظر دقيقة أو دقيقتين
  حتى ينتهي خادم الوكيل من البدء، ثم قم بالتحديث. إذا ظلت غير سليمة، أعد تشغيل
  المجموعة وتحقق من السجلات بحثًا عن الأخطاء.
- **تفشل طلبات دردشة Lemonade بخطأ اتصال:** تأكد من نجاح
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` ومن أن Lemonade لا يزال
  يخدم النموذج عبر `lemonade status`.
- **يُخطئ الوكيل برسالة تتعلق بطول السياق أو حد الرموز:** ابدأ محادثة جديدة
  حتى لا يحمل الوكيل سجلًا ضخمًا. إذا استمرت المشكلة، أعد تشغيل Lemonade
  بقيمة `ctx_size` أكبر من القيمة الافتراضية 65536 (على سبيل المثال
  `ctx_size=131072`)، إذا سمحت الذاكرة بذلك.
- **ينتج الوكيل تعديلات منخفضة الجودة أو غير مكتملة:** انتقل إلى نموذج أكبر في
  Lemonade، أو امنح الوكيل مهمة أصغر وأكثر تحديدًا ودعه ينهيها قبل طلب التغيير
  التالي.

## الخطوات التالية

- جرّب مهمة أكبر في نفس مساحة العمل، مثل إضافة ملف اختبار وحدة أو إصلاح خطأ
  معروف، وراجع الفروقات (diff) الخاصة بالوكيل قبل الإبقاء على التغيير.
- قم بتوصيل خادم MCP مثل GitHub أو Slack ضمن **Customize** حتى يتمكن
  الوكيل من قراءة المشكلات (issues) أو نشر التحديثات أثناء عمله.
- احفظ عدة ملفات تعريف LLM (نموذج صغير وسريع ونموذج كبير وأقوى) وتنقّل
  بينها باستخدام `/model` أثناء المحادثة.
- انتقل إلى [أتمتة OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) لتحويل
  حلقات التطوير المتكررة إلى عمليات تشغيل مجدولة أو مُحفَّزة بالأحداث للوكيل.

## الموارد

- [وثائق OpenHands](https://docs.openhands.dev/)
- [نظرة عامة على Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [إعداد Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [ملفات تعريف LLM وتهيئة النماذج](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [وثائق Lemonade Server](https://lemonade-server.ai/docs)

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