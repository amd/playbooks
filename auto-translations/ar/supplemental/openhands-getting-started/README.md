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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) هو وكيل برمجي يعمل بالذكاء الاصطناعي
قادر على كتابة الأكواد، وتشغيل الأوامر، وتصفح الويب، وتحرير الملفات في مساحة
عمل حقيقية. فبدلاً من نسخ الاقتراحات من نافذة محادثة، توجّه الوكيل نحو مجلد
مشروع وتدعه يتولى العمل: تنفيذ ميزة، إصلاح خلل، كتابة اختبارات، أو شرح قاعدة
الأكواد.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) هو واجهة المستخدم
الموصى بها عبر المتصفح لتشغيل OpenHands. يقوم أمر واحد هو `agent-canvas`
بتشغيل خادم الوكيل، وواجهة التشغيل الآلي الخلفية، وواجهة الويب الأمامية معًا،
مما يتيح لك إجراء محادثة مع الوكيل من متصفحك.

للحفاظ على كل شيء ضمن نظام AMD الخاص بك، يتحدث الوكيل مع نموذج محلي يقدَّم عبر
Lemonade Server. يكشف Lemonade عن ذلك النموذج من خلال واجهة برمجة تطبيقات
متوافقة مع OpenAI، مما يتيح لـ Agent Canvas تهيئته مثل أي نقطة نهاية أخرى
بأسلوب OpenAI، بينما يبقى النموذج والكود الخاص بك وسياق المحادثة بأكمله على
جهازك.

في هذا الدليل، ستبدأ تشغيل نموذج محلي، وتُطلق Agent Canvas، وتوجّهه نحو ذلك
النموذج، وتنفّذ أول مهمة برمجية لك على مجلد مشروع حقيقي.

## ما الذي ستتعلمه

- كيفية بدء تشغيل Lemonade Server والتأكد من أن النموذج المحلي يستجيب
  لطلبات المحادثة
- كيفية تثبيت وتشغيل Agent Canvas من حزمة npm
- كيفية تهيئة Agent Canvas لاستخدام نموذج Lemonade محلي كنموذج لغوي كبير (LLM)
- كيفية بدء محادثة OpenHands ومشاهدة الوكيل وهو يحرر الملفات ويشغّل
  الأوامر داخل مساحة عمل
- كيفية مراجعة ما قام الوكيل بتغييره وتوجيهه برسائل متابعة

## المفاهيم الأساسية

| المفهوم | ما هو | مكانه في هذا الدليل |
| --- | --- | --- |
| Lemonade Server | منصة تقديم نماذج لغوية كبيرة محلية مصممة لأجهزة AMD، تكشف عن واجهة برمجة تطبيقات متوافقة مع OpenAI. بياناتك لا تغادر جهازك أبدًا. | يشغّل النموذج الذي يشغّل الوكيل. |
| OpenHands | وكيل برمجي يعمل بالذكاء الاصطناعي يقرأ ويحرّر الملفات، ويشغّل أوامر الصدفة، ويتصفح الويب داخل مساحة عمل. | الوكيل الذي تديره من المحادثة. |
| Agent Canvas | واجهة المتصفح والخلفية التي تشغّل محادثات OpenHands وتعرض استدعاءات الأدوات وتغييرات الملفات. | يطلق المجموعة البرمجية ويستضيف محادثتك. |
| مساحة العمل | مجلد المشروع المسموح للوكيل بقراءته وتعديله. | هدف تحريرات الوكيل وأوامره. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> تستفيد سير عمل وكلاء البرمجة من نموذج أكبر ونافذة سياق أوسع. استخدم على
> الأقل 32 جيجابايت من ذاكرة النظام، ويُفضَّل 64 جيجابايت أو أكثر للنماذج
> الأكبر من نوع GGUF.
<!-- @device:end -->

## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرمجيات

<!-- @require:software-update -->
<!-- @device:end -->

## المتطلبات الأساسية


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
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
- Node.js الإصدار 22.12 أو أحدث مع `npm` (تستخدمه واجهة سطر الأوامر
  `agent-canvas`).
- `uv`، مدير حزم Python الذي تستخدمه Agent Canvas لإدارة بيئة خادم الوكيل.
  إذا لم يكن مثبتًا بالفعل على نظامك، فثبّته من [دليل تثبيت uv](https://docs.astral.sh/uv/getting-started/installation/)
  قبل تشغيل Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)،
  مثبّتًا وقيد التشغيل. على Windows، تعمل مجموعة Agent Canvas من صورة Docker
  المنشورة، التي تضم Node.js و`uv` وحزمة `@openhands/agent-canvas`، لذا لا
  تحتاج إلى تثبيت هذه العناصر على الجهاز المضيف.
<!-- @os:end -->

- مجلد مشروع للعمل فيه. يمكن أن يكون أي مستودع git محلي أو دليل أكواد تريد
  أن يعمل الوكيل عليه.

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

> **اختر نموذجًا يناسب عتادك.** يُعَد `Qwen3.6-35B-A3B-GGUF` (~20 جيجابايت)
> نموذج برمجة قويًا، لكنه يحتاج إلى مجمّع ذاكرة كبير. إذا كان جهازك محدود
> الذاكرة أو ذاكرة GPU VRAM، فاختر بدلاً منه نموذج GGUF أصغر من مكتبة نماذج
> Lemonade، واستخدم معرّف ذلك النموذج في جميع أنحاء هذا الدليل.

> **ملاحظة:** أول تشغيل لـ `lemonade run` يقوم بتنزيل النموذج إذا لم يكن
> موجودًا بالفعل، وقد يستغرق ذلك بعض الوقت تبعًا لحجم النموذج وسرعة اتصالك.

يكشف Lemonade عن واجهة برمجة تطبيقات متوافقة مع OpenAI على العنوان:

```text
http://127.0.0.1:13305/api/v1
```

## 2. التحقق من النموذج المحلي

تأكد من قدرة Lemonade على تقديم النموذج المختار:

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
قم بتثبيت حزمة Agent Canvas المنشورة عالميًا:

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

بعد ذلك، ابدأ تشغيل المكدس الكامل من الطرفية:

```bash
agent-canvas
```

بشكل افتراضي، يبدأ تشغيل Agent Canvas على `http://localhost:8000`. افتح هذا الرابط في
متصفحك. المنفذ ليس له أهمية خاصة — إذا كان المنفذ 8000 قيد الاستخدام بالفعل، مرر أي
منفذ متاح باستخدام `--port` (أو `-p`) عند تشغيل Agent Canvas:

```bash
agent-canvas --port 3000
```

ثم افتح `http://localhost:3000` بدلاً من ذلك. يجب أن تظهر الواجهة الخلفية المحلية الافتراضية
على أنها تعمل بشكل سليم في الشاشة الرئيسية.

يقوم أمر `agent-canvas` بتشغيل خادم الوكيل، والواجهة الخلفية للأتمتة، وواجهة الويب
الأمامية معًا. تحتاج فقط إلى هذا الأمر الواحد لتشغيل OpenHands
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
على نظام Windows، قم بتشغيل صورة حاوية Agent Canvas المنشورة باستخدام Docker Desktop.
تحتوي الصورة على خادم الوكيل، والواجهة الخلفية للأتمتة، وواجهة الويب الأمامية، لذا
لا تحتاج إلى تثبيت Node.js أو `uv` أو واجهة سطر الأوامر على الجهاز المضيف.

أولًا، قم بإنشاء مجلدي الإعدادات ومساحة العمل اللذين تقوم الحاوية بتركيبهما:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

اسحب الصورة المنشورة (إنها عامة، لذا لا يلزم تسجيل الدخول):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

ثم ابدأ تشغيل المكدس:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

افتح `http://localhost:8000/canvas` في متصفحك. إذا كان المنفذ 8000 قيد الاستخدام
بالفعل، قم بتعيين منفذ مضيف مختلف، على سبيل المثال `-p 8080:8000`، وافتح
`http://localhost:8080/canvas` بدلاً من ذلك.

> **ملاحظة:** يقوم أول تشغيل بتهيئة خادم الوكيل داخل الحاوية،
> لذا قد يستغرق الأمر دقيقة أو دقيقتين قبل أن تُبلّغ الواجهة الخلفية عن عملها بشكل سليم.

يحافظ تركيب `.openhands` على ملف تعريف LLM والإعدادات الخاصة بك عبر عمليات إعادة
تشغيل الحاوية. يقوم بقية هذا الدليل بتكوين كل شيء من خلال واجهة مستخدم Agent
Canvas في متصفحك.

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

## 4. تكوين نموذج LLM المحلي

عند أول تشغيل، يفتح Agent Canvas تدفق إعداد أولي. ضمن هذا التدفق:

1. أبقِ **OpenHands** محددًا كوكيل وانقر على **Next**.
2. في **Set up your LLM**، اختر **Advanced**.
3. أبقِ **Authentication** مضبوطًا على **API key**.
4. اضبط **Custom Model** على `openai/Qwen3.6-35B-A3B-GGUF`.
5. اضبط **Base URL** على `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > على نظام Windows، يعمل المكدس داخل حاوية، والتي لا يمكنها الوصول إلى المضيف عبر
   > `127.0.0.1`. استخدم `http://host.docker.internal:13305/api/v1` بدلاً من ذلك حتى
   > يتمكن الوكيل المُحوسب (المُشغّل في الحاوية) من الوصول إلى Lemonade الذي يعمل على مضيف Windows.
   <!-- @os:end -->
6. في **API Key**، أدخل أي قيمة نائبة غير فارغة مثل `lemonade-local`.
   لا يتطلب Lemonade مفتاحًا حقيقيًا، لكن عميل OpenHands يحتاج إلى قيمة
   لإرسالها.
7. انقر على **Next**.

ينبغي أن تبدو إعدادات Advanced المكتملة كما يلي. يتم إخفاء حقل مفتاح API
بواسطة الواجهة.

![إعدادات Agent Canvas المتقدمة لنموذج LLM عند أول استخدام، مع نموذج Lemonade ورابط القاعدة المحلي](assets/01-llm-advanced-settings.png)

يحفظ Agent Canvas هذه القيم كملف تعريف LLM. إذا طلب إصدارك منك تسمية
ملف التعريف هذا، استخدم اسمًا بدون مسافات مثل `lemonade-local`. إذا غيّرت
النماذج لاحقًا، افتح **Settings > LLM** وحدّث نفس حقول Advanced. يمكنك
التبديل بين ملفات التعريف المحفوظة من مربع إدخال الدردشة باستخدام الأمر `/model`.

## 5. فتح مساحة عمل

لا يمكن للوكيل قراءة الملفات أو تعديلها إلا داخل مساحة عمل تختارها. قبل
بدء مهمة، وجّه Agent Canvas إلى مجلد مشروعك:

1. من الشاشة الرئيسية، اختر **Open Workspace**.
2. حدد المجلد الذي يحتوي على مشروعك (على سبيل المثال، مستودع git
   تريد أن يعمل عليه الوكيل).
3. ابدأ محادثة جديدة في مساحة العمل تلك.

كل ما يقوم به الوكيل—قراءة الملفات، وتشغيل الأوامر، وتحرير الكود—يكون
محصورًا ضمن مساحة العمل تلك.

![الشاشة الرئيسية لـ Agent Canvas بعد الإعداد الأولي](assets/02-agent-canvas-home.png)

## 6. تشغيل أول مهمة برمجية

مع فتح مساحة العمل واختيار نموذج LLM المحلي، اكتب مهمة محددة في
الدردشة. من الجيد أن تكون المهمة الأولى صغيرة وقابلة للتحقق منها، على سبيل المثال:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

راقب الجدول الزمني للمحادثة. سيقوم OpenHands بما يلي:

- قراءة مساحة العمل لفهم بنيتها.
- إنشاء `hello.py` مع الدالة المطلوبة وكتلة الاختبار.
- تشغيل `python3 hello.py` اختياريًا للتحقق من الناتج.
- الإبلاغ عما قام به وأي ناتج أوامر في الدردشة.

يجب أن ترى الملف الجديد يظهر في مساحة العمل، وينبغي أن تصف رسالة الوكيل
الأخيرة التغيير الذي أجراه. هذه هي لحظة النتيجة: لقد كتب
الوكيل وشغّل كودًا حقيقيًا في مجلد مشروعك.

## 7. مراجعة الوكيل وتوجيهه

بعد أن ينهي الوكيل خطوة ما، راجع عمله قبل قبول الخطوة التالية:

- **تغييرات الملفات**: استخدم متصفح ملفات مساحة العمل أو عرض الفروقات (diff) الخاص
  بالوكيل لمعرفة بالضبط ما تمت إضافته أو تغييره أو حذفه.
- **ناتج الأوامر**: وسّع أي أمر قام الوكيل بتشغيله لرؤية stdout وstderr
  ورمز الخروج.
- **المتابعات**: إذا لم تكن النتيجة ما أردته، رد في نفس
  المحادثة بتصحيح. يحتفظ الوكيل بالسياق السابق ويكرر العمل
  على نفس الملفات.

على سبيل المثال، إذا لم يطبع الاختبار التحية المتوقعة، رد بما يلي:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

سيعيد الوكيل قراءة الملف، وتشغيل الأمر، وتشخيص المشكلة، ويعدّل
الملف مرة أخرى—كل ذلك في نفس المحادثة.
## استكشاف الأخطاء وإصلاحها

<!-- @os:linux -->
- **`agent-canvas` غير موجود في PATH:** أعد التثبيت باستخدام
  `npm install -g @openhands/agent-canvas` وتأكد من أن دليل npm العام الثنائي
  موجود في PATH قبل أن يتمكن `agent-canvas` من التشغيل من طرفية جديدة.
- **فشل `npm install -g` بخطأ في الأذونات:** قم بتهيئة دليل npm عام مملوك للمستخدم،
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
  يستخدم Agent Canvas أداة `uv` لإدارة بيئة Python الخاصة بخادم الوكيل.
<!-- @os:end -->

<!-- @os:windows -->
- **يفشل `docker pull` أو `docker run` في الاتصال:** تأكد من أن Docker Desktop
  قيد التشغيل (أيقونة الحوت الخاصة به موجودة في شريط النظام) وأن المحرك قد
  انتهى من البدء. يجب أن يطبع `docker version` كلاً من قسم Client وقسم Server.
- **يبدأ الحاوية ولكن الواجهة الخلفية لا تصبح سليمة أبدًا:** يقوم التشغيل الأول
  بتهيئة Agent Server داخل الحاوية؛ امنحه دقيقة أو دقيقتين، ثم تحقق من
  `docker logs <container>` بحثًا عن الأخطاء.
- **لا تستطيع الحاوية الوصول إلى Lemonade:** تصل الحاوية إلى المضيف عبر
  `host.docker.internal`. تأكد من أن Lemonade يعمل على مضيف Windows باستخدام
  `lemonade status`، واستخدم `http://host.docker.internal:13305/api/v1` كعنوان
  URL الأساسي عند تهيئة LLM.
<!-- @os:end -->

- **تُحمَّل الواجهة ولكن الواجهة الخلفية تظهر غير سليمة:** انتظر دقيقة أو دقيقتين
  حتى ينتهي خادم الوكيل من البدء، ثم أعد التحميل. إذا ظلت غير سليمة، أعد تشغيل
  المجموعة (stack) وتحقق من السجلات بحثًا عن الأخطاء.
- **تفشل طلبات دردشة Lemonade بخطأ في الاتصال:** تأكد من أن
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` تنجح وأن Lemonade لا يزال
  يخدم النموذج باستخدام `lemonade status`.
- **يُخطئ الوكيل برسالة طول السياق أو حد الرموز:** ابدأ محادثة جديدة حتى لا يحمل
  الوكيل سجلاً ضخمًا للغاية. إذا استمر حدوث ذلك، أعد تشغيل Lemonade بقيمة
  `ctx_size` أكبر من القيمة الافتراضية 65536 (على سبيل المثال `ctx_size=131072`)،
  بحسب توفر الذاكرة.
- **ينتج الوكيل تعديلات منخفضة الجودة أو غير مكتملة:** بدّل إلى نموذج أكبر في
  Lemonade، أو امنح الوكيل مهمة أصغر وأكثر تحديدًا ودعه ينهيها قبل طلب التغيير
  التالي.

## الخطوات التالية

- جرّب مهمة أكبر في نفس مساحة العمل، مثل إضافة ملف اختبار وحدة أو إصلاح خطأ
  معروف، وراجع الفرق (diff) الخاص بالوكيل قبل الاحتفاظ بالتغيير.
- صِل خادم MCP مثل GitHub أو Slack تحت **Customize** حتى يتمكن الوكيل من قراءة
  المشكلات أو نشر التحديثات أثناء عمله.
- احفظ عدة ملفات تعريف لـ LLM (نموذج صغير سريع ونموذج كبير أقوى) وبدّل بينها
  باستخدام `/model` في منتصف المحادثة.
- انتقل إلى [أتمتة OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
  لتحويل حلقات التطوير المتكررة إلى عمليات تشغيل وكيل مجدولة أو مُشغَّلة بالأحداث.

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