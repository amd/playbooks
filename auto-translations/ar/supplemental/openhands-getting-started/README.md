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
يمكنه كتابة الكود، وتشغيل الأوامر، وتصفح الويب، وتعديل الملفات في مساحة عمل
حقيقية. بدلاً من نسخ الاقتراحات من نافذة محادثة، توجّه الوكيل إلى مجلد مشروع
وتدعه يقوم بالعمل: تنفيذ ميزة، أو إصلاح خطأ، أو كتابة اختبارات، أو شرح قاعدة كود.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) هو واجهة المتصفح
الموصى بها لتشغيل OpenHands. يبدأ أمر واحد وهو `agent-canvas` خادم الوكيل،
والواجهة الخلفية للأتمتة، وواجهة الويب الأمامية معاً، بحيث يمكنك إدارة محادثة
مع الوكيل من متصفحك.

للحفاظ على كل شيء على نظام AMD الخاص بك، يتحدث الوكيل مع نموذج محلي يتم تقديمه
بواسطة Lemonade Server. يعرض Lemonade هذا النموذج عبر واجهة برمجة تطبيقات
متوافقة مع OpenAI، بحيث يمكن لـ Agent Canvas تهيئته مثل أي نقطة نهاية أخرى على
طراز OpenAI، بينما يبقى النموذج والكود الخاص بك وسياق المحادثة جميعها على جهازك.

في هذا الدليل التطبيقي، ستبدأ نموذجاً محلياً، وتُطلق Agent Canvas، وتوجّهه نحو
ذلك النموذج، وتُشغّل أول مهمة برمجية لك على مجلد مشروع حقيقي.

## ما ستتعلمه

- كيفية بدء تشغيل Lemonade Server والتأكد من أن النموذج المحلي يستجيب لطلبات المحادثة
- كيفية تثبيت وتشغيل Agent Canvas من حزمة npm
- كيفية تهيئة Agent Canvas لاستخدام نموذج Lemonade محلي كـ LLM
- كيفية بدء محادثة OpenHands ومشاهدة الوكيل وهو يعدّل الملفات ويشغّل
  الأوامر في مساحة عمل
- كيفية مراجعة ما قام الوكيل بتغييره وتوجيهه برسائل متابعة

## المفاهيم الأساسية

| المفهوم | ما هو | مكانه في هذا الدليل التطبيقي |
| --- | --- | --- |
| Lemonade Server | منصة تقديم LLM محلية مصممة لعتاد AMD، تعرض واجهة برمجة تطبيقات متوافقة مع OpenAI. بياناتك لا تغادر جهازك أبداً. | يشغّل النموذج الذي يُشغّل الوكيل. |
| OpenHands | وكيل برمجيات ذكاء اصطناعي يقرأ ويعدّل الملفات، ويشغّل أوامر shell، ويتصفح الويب داخل مساحة عمل. | الوكيل الذي تديره من المحادثة. |
| Agent Canvas | واجهة المتصفح والخلفية التي تُشغّل محادثات OpenHands وتُظهر استدعاءات الأدوات وتغييرات الملفات. | يُطلق الحزمة ويستضيف محادثتك. |
| مساحة العمل | مجلد المشروع الذي يُسمح للوكيل بقراءته وتعديله. | هدف تعديلات وأوامر الوكيل. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> تستفيد تدفقات عمل الوكيل البرمجي من نموذج أكبر ونافذة سياق أكبر. استخدم
> 32 جيجابايت على الأقل من ذاكرة النظام، ويُفضَّل 64 جيجابايت أو أكثر للنماذج
> الأكبر من نوع GGUF.
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
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so the host needs only Docker and the model.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:docker,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

تحتاج إلى:

- تثبيت Lemonade Server وتمكينه من تقديم النموذج أدناه.

<!-- @os:linux -->
- Node.js الإصدار 22.12 أو أحدث و`npm` (يستخدمهما أداة سطر الأوامر `agent-canvas`).
- `uv`، مدير حزم Python الذي يستخدمه Agent Canvas لإدارة بيئة خادم الوكيل. إذا
  لم يكن نظامك يحتوي عليه بالفعل، فثبّته من
  [دليل تثبيت uv](https://docs.astral.sh/uv/getting-started/installation/)
  قبل تشغيل Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)،
  مثبت وقيد التشغيل. على نظام Windows، تعمل حزمة Agent Canvas من صورة Docker
  المنشورة، التي تحزم Node.js و`uv` وحزمة
  `@openhands/agent-canvas` معاً، لذا لا تحتاج إلى تثبيت هذه العناصر على الجهاز المضيف.
<!-- @os:end -->

- مجلد مشروع تعمل عليه. يمكن أن يكون هذا أي مستودع git محلي أو دليل كود
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

> **اختر نموذجاً يناسب عتادك.** يُعد `Qwen3.6-35B-A3B-GGUF` (بحجم ~20 جيجابايت) نموذج برمجة قوياً لكنه يحتاج إلى مجمع ذاكرة كبير. إذا كان جهازك يحتوي على ذاكرة أو ذاكرة GPU VRAM محدودة، فاختر نموذج GGUF أصغر من مكتبة نماذج Lemonade بدلاً من ذلك واستخدم معرّف هذا النموذج طوال هذا الدليل التطبيقي.

> **ملاحظة:** يقوم أول تشغيل لـ `lemonade run` بتنزيل النموذج إذا لم يكن موجوداً بالفعل، وقد يستغرق ذلك بعض الوقت حسب حجم النموذج وسرعة اتصالك.

يعرض Lemonade واجهة برمجة تطبيقات متوافقة مع OpenAI على العنوان:

```text
http://127.0.0.1:13305/api/v1
```

## 2. التحقق من النموذج المحلي

تأكد من أن Lemonade يمكنه تقديم النموذج المحدد:

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

بعد ذلك، ابدأ تشغيل المكدس الكامل من طرفية:

```bash
agent-canvas
```

بشكل افتراضي، يبدأ Agent Canvas على `http://localhost:8000`. افتح ذلك الرابط في
متصفحك. المنفذ ليس له خصوصية — إذا كان المنفذ 8000 مستخدمًا بالفعل، مرّر أي
منفذ متاح باستخدام `--port` (أو `-p`) عند تشغيل Agent Canvas:

```bash
agent-canvas --port 3000
```

ثم افتح `http://localhost:3000` بدلاً من ذلك. يجب أن تظهر الخلفية المحلية الافتراضية
بحالة سليمة على الشاشة الرئيسية.

يبدّئ الأمر `agent-canvas` خادم الوكيل، وخلفية الأتمتة، وواجهة الويب الأمامية
معًا. تحتاج فقط إلى هذا الأمر الواحد لتشغيل OpenHands
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
على ويندوز، شغّل صورة حاوية Agent Canvas المنشورة باستخدام Docker Desktop.
تحزّم الصورة خادم الوكيل، وخلفية الأتمتة، وواجهة الويب الأمامية، لذا
لست بحاجة إلى تثبيت Node.js أو `uv` أو واجهة سطر الأوامر على المضيف.

أولاً، أنشئ مجلدات الإعداد ومساحة العمل التي ستقوم الحاوية بوصلها (mount):

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

اسحب الصورة المنشورة (وهي عامة، لذا لا حاجة لتسجيل الدخول):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

بعد ذلك، ابدأ تشغيل المكدس:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

افتح `http://localhost:8000/canvas` في متصفحك. إذا كان المنفذ 8000 مستخدمًا
بالفعل، قم بربط منفذ مضيف مختلف، على سبيل المثال `-p 8080:8000`، وافتح
`http://localhost:8080/canvas` بدلاً من ذلك.

> **ملاحظة:** يقوم أول تشغيل بتهيئة خادم الوكيل داخل الحاوية،
> لذا قد يستغرق الأمر دقيقة أو دقيقتين قبل أن تُبلغ الخلفية عن حالتها كسليمة.

يحافظ وصل (mount) `.openhands` على ملف تعريف LLM والإعدادات الخاصة بك عبر إعادة
تشغيل الحاوية. يقوم بقية هذا الدليل بتهيئة كل شيء من خلال واجهة مستخدم
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

## 4. تهيئة LLM المحلي

عند التشغيل الأول، يفتح Agent Canvas سير عمل للتهيئة الأولية. في ذلك السير:

1. أبقِ **OpenHands** محددًا كوكيل وانقر على **Next**.
2. في **Set up your LLM**، اختر **Advanced**.
3. أبقِ **Authentication** مضبوطًا على **API key**.
4. اضبط **Custom Model** على `openai/Qwen3.6-35B-A3B-GGUF`.
5. اضبط **Base URL** على `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > على ويندوز، يعمل المكدس داخل حاوية، والتي لا يمكنها الوصول إلى المضيف عبر
   > `127.0.0.1`. استخدم `http://host.docker.internal:13305/api/v1` بدلاً من ذلك حتى
   > يتمكن الوكيل المحوسب داخل الحاوية من الوصول إلى Lemonade العامل على مضيف ويندوز.
   <!-- @os:end -->
6. في **API Key**، أدخل أي قيمة بديلة غير فارغة مثل `lemonade-local`.
   لا يتطلب Lemonade مفتاحًا حقيقيًا، لكن عميل OpenHands يحتاج إلى قيمة
   لإرسالها.
7. انقر على **Next**.

يجب أن تبدو إعدادات Advanced المكتملة كما يلي. حقل مفتاح API مُخفى بواسطة الواجهة.

![إعدادات LLM Advanced عند أول استخدام لـ Agent Canvas مع نموذج Lemonade وعنوان URL الأساسي المحلي](assets/01-llm-advanced-settings.png)

يحفظ Agent Canvas هذه القيم كملف تعريف LLM. إذا طلب منك إصدارك تسمية
ذلك الملف التعريفي، استخدم اسمًا بلا مسافات مثل `lemonade-local`. إذا غيّرت
النماذج لاحقًا، افتح **Settings > LLM** وحدّث نفس حقول Advanced. يمكنك
التبديل بين ملفات التعريف المحفوظة من مربع إدخال الدردشة باستخدام الأمر `/model`.

## 5. فتح مساحة عمل

لا يمكن للوكيل قراءة وتعديل الملفات إلا داخل مساحة عمل تختارها أنت. قبل
بدء مهمة، وجّه Agent Canvas إلى مجلد مشروعك:

1. من الشاشة الرئيسية، اختر **Open Workspace**.
2. اختر المجلد الذي يحتوي على مشروعك (على سبيل المثال، مستودع git
   تريد أن يعمل الوكيل عليه).
3. ابدأ محادثة جديدة في مساحة العمل تلك.

كل ما يفعله الوكيل - قراءة الملفات، تشغيل الأوامر، تحرير الكود - يكون
محصورًا ضمن نطاق مساحة العمل تلك.

![الشاشة الرئيسية لـ Agent Canvas بعد التهيئة الأولية](assets/02-agent-canvas-home.png)

## 6. تشغيل أول مهمة برمجية لك

مع فتح مساحة العمل واختيار LLM المحلي، اكتب مهمة ملموسة في
الدردشة. المهمة الأولى الجيدة تكون صغيرة وقابلة للتحقق، على سبيل المثال:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

راقب الجدول الزمني للمحادثة. سيقوم OpenHands بما يلي:

- قراءة مساحة العمل لفهم التخطيط.
- إنشاء `hello.py` بالدالة المطلوبة وكتلة الاختبار.
- تشغيل `python3 hello.py` بشكل اختياري للتحقق من المخرجات.
- الإبلاغ عما قام به وأي مخرجات أوامر في الدردشة.

يجب أن ترى الملف الجديد يظهر في مساحة العمل، ويجب أن تصف الرسالة الأخيرة
للوكيل التغيير الذي أجراه. هذه هي اللحظة المحورية: فقد كتب
الوكيل كودًا حقيقيًا وشغّله في مجلد مشروعك.

## 7. مراجعة وتوجيه الوكيل

بعد أن ينهي الوكيل خطوة ما، راجع عمله قبل قبول الخطوة التالية:

- **تغييرات الملفات**: استخدم متصفح ملفات مساحة العمل أو عرض الفروقات (diff)
  الخاص بالوكيل لترى بالضبط ما تمت إضافته أو تغييره أو حذفه.
- **مخرجات الأوامر**: وسّع أي أمر نفّذه الوكيل لرؤية stdout، وstderr،
  ورمز الخروج.
- **المتابعات**: إذا لم تكن النتيجة ما أردته، رد في نفس
  المحادثة بتصحيح. يحتفظ الوكيل بالسياق السابق ويكرر
  العمل على نفس الملفات.

على سبيل المثال، إذا لم تطبع الاختبار التحية المتوقعة، رد بـ:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

سيعيد الوكيل قراءة الملف، وتشغيل الأمر، وتشخيص المشكلة، وتحرير
الملف مرة أخرى - كل ذلك في نفس المحادثة.
## استكشاف الأخطاء وإصلاحها

<!-- @os:linux -->
- **`agent-canvas` غير موجود على PATH:** أعد التثبيت باستخدام
  `npm install -g @openhands/agent-canvas` وتأكد من أن دليل الملفات الثنائية العام لـ npm
  موجود على PATH قبل أن يتمكن `agent-canvas` من العمل من
  طرفية جديدة.
- **يفشل أمر `npm install -g` مع خطأ في الأذونات:** قم بتهيئة دليل npm عام مملوك للمستخدم،
  ثم أعد فتح الطرفية وثبّت Agent Canvas مرة أخرى.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` غير موجود:** قم بتثبيته من
  [دليل تثبيت uv](https://docs.astral.sh/uv/getting-started/installation/).
  يستخدم Agent Canvas أداة `uv` لإدارة بيئة Python الخاصة بخادم الوكيل.
<!-- @os:end -->

<!-- @os:windows -->
- **يفشل أمر `docker pull` أو `docker run` في الاتصال:** تأكد من أن Docker Desktop
  قيد التشغيل (رمز الحوت الخاص به موجود في شريط النظام) وأن المحرك قد
  انتهى من بدء التشغيل. يجب أن يطبع أمر `docker version` قسمي Client وServer
  كليهما.
- **يبدأ الحاوية لكن الواجهة الخلفية لا تصبح سليمة أبدًا:** يقوم أول تشغيل
  بتهيئة خادم الوكيل داخل الحاوية؛ امنحه دقيقة أو
  دقيقتين، ثم تحقق من `docker logs <container>` بحثًا عن أخطاء.
- **لا تستطيع الحاوية الوصول إلى Lemonade:** تصل الحاوية إلى المضيف عبر
  `host.docker.internal`. تأكد من أن Lemonade يعمل على مضيف Windows باستخدام
  `lemonade status`، واستخدم `http://host.docker.internal:13305/api/v1` كعنوان URL الأساسي
  عند تهيئة نموذج اللغة الكبير.
<!-- @os:end -->

- **تُحمَّل الواجهة لكن الواجهة الخلفية تظهر غير سليمة:** انتظر دقيقة أو دقيقتين حتى
  ينتهي خادم الوكيل من البدء، ثم حدّث الصفحة. إذا بقيت غير سليمة، أعد تشغيل
  المجموعة وتحقق من السجلات بحثًا عن أخطاء.
- **تفشل طلبات محادثة Lemonade مع خطأ في الاتصال:** تأكد من أن
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` ينجح وأن
  Lemonade لا يزال يقدّم النموذج باستخدام `lemonade status`.
- **يخطئ الوكيل برسالة طول السياق أو حد الرموز:** ابدأ محادثة
  جديدة حتى لا يحمل الوكيل سجلاً ضخمًا للغاية. إذا استمر الأمر في الحدوث،
  أعد تشغيل Lemonade بقيمة `ctx_size` أكبر من القيمة الافتراضية
  65536 (على سبيل المثال `ctx_size=131072`)، إذا سمحت الذاكرة بذلك.
- **ينتج الوكيل تعديلات منخفضة الجودة أو غير مكتملة:** انتقل إلى
  نموذج أكبر في Lemonade، أو امنح الوكيل مهمة أصغر وأكثر تحديدًا ودعه
  ينهيها قبل طلب التغيير التالي.

## الخطوات التالية

- جرّب مهمة أكبر في نفس مساحة العمل، مثل إضافة ملف اختبار وحدة أو
  إصلاح خطأ معروف، وراجع الفرق الناتج عن الوكيل قبل الاحتفاظ بالتغيير.
- قم بتوصيل خادم MCP مثل GitHub أو Slack ضمن **Customize** حتى
  يتمكن الوكيل من قراءة المشكلات أو نشر التحديثات أثناء عمله.
- احفظ عدة ملفات تعريف لنماذج اللغة الكبيرة (نموذج صغير سريع ونموذج كبير أقوى) و
  انتقل بينها باستخدام `/model` في منتصف المحادثة.
- انتقل إلى [أتمتة OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) لـ
  تحويل حلقات التطوير المتكررة إلى تشغيلات وكيل مجدولة أو مُشغَّلة بالأحداث.

## الموارد

- [توثيق OpenHands](https://docs.openhands.dev/)
- [نظرة عامة على Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [إعداد Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [ملفات تعريف نماذج اللغة الكبيرة وتهيئة النماذج](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
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