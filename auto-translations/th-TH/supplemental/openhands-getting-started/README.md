<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## ภาพรวม

[OpenHands](https://github.com/All-Hands-AI/OpenHands) เป็นเอเจนต์ซอฟต์แวร์ AI
ที่สามารถเขียนโค้ด รันคำสั่ง ท่องเว็บ และแก้ไขไฟล์ในพื้นที่ทำงานจริงได้
แทนที่จะคัดลอกคำแนะนำออกมาจากหน้าต่างแชท คุณเพียงชี้เอเจนต์ไปที่โฟลเดอร์โปรเจกต์
แล้วปล่อยให้มันลงมือทำงาน ไม่ว่าจะเป็นการพัฒนาฟีเจอร์ แก้บั๊ก เขียนเทสต์
หรืออธิบายโค้ดเบส

[Agent Canvas](https://github.com/OpenHands/agent-canvas) คือ UI บนเบราว์เซอร์ที่แนะนำสำหรับรัน OpenHands
คำสั่ง `agent-canvas` เพียงคำสั่งเดียวจะเริ่มเซิร์ฟเวอร์เอเจนต์ แบ็กเอนด์ระบบอัตโนมัติ
และเว็บฟรอนต์เอนด์พร้อมกัน ทำให้คุณสามารถสนทนากับเอเจนต์ผ่านเบราว์เซอร์ของคุณได้

เพื่อให้ทุกอย่างอยู่บนระบบ AMD ของคุณ เอเจนต์จะสื่อสารกับโมเดลภายในเครื่อง
ที่ให้บริการโดย Lemonade Server โดย Lemonade จะเปิดให้ใช้งานโมเดลนั้นผ่าน API
ที่เข้ากันได้กับ OpenAI ทำให้ Agent Canvas สามารถกำหนดค่าให้ใช้งานได้เหมือนกับ
เอนด์พอยต์สไตล์ OpenAI ทั่วไป ในขณะที่โมเดล โค้ดของคุณ และบริบทของการสนทนา
ทั้งหมดยังคงอยู่บนเครื่องของคุณ

ในเพลย์บุ๊กนี้ คุณจะเริ่มโมเดลภายในเครื่อง เปิดใช้งาน Agent Canvas
ชี้ให้มันใช้โมเดลนั้น และรันงานเขียนโค้ดชิ้นแรกของคุณกับโฟลเดอร์โปรเจกต์จริง

## สิ่งที่คุณจะได้เรียนรู้

- วิธีเริ่ม Lemonade Server และยืนยันว่าโมเดลภายในเครื่องตอบสนองต่อคำขอแชทได้
- วิธีติดตั้งและเปิดใช้งาน Agent Canvas จากแพ็กเกจ npm
- วิธีกำหนดค่า Agent Canvas ให้ใช้โมเดล Lemonade ภายในเครื่องเป็น LLM
- วิธีเริ่มการสนทนา OpenHands และสังเกตเอเจนต์แก้ไขไฟล์และรันคำสั่งในพื้นที่ทำงาน
- วิธีตรวจสอบสิ่งที่เอเจนต์เปลี่ยนแปลง และควบคุมทิศทางด้วยข้อความติดตามผล

## แนวคิดหลัก

| แนวคิด | คืออะไร | มีบทบาทอย่างไรในเพลย์บุ๊กนี้ |
| --- | --- | --- |
| Lemonade Server | แพลตฟอร์มให้บริการ LLM ภายในเครื่องที่สร้างขึ้นมาสำหรับฮาร์ดแวร์ AMD ซึ่งเปิดให้ใช้งาน API ที่เข้ากันได้กับ OpenAI ข้อมูลของคุณจะไม่มีวันออกจากเครื่องของคุณ | รันโมเดลที่ขับเคลื่อนเอเจนต์ |
| OpenHands | เอเจนต์ซอฟต์แวร์ AI ที่อ่านและแก้ไขไฟล์ รันคำสั่งเชลล์ และท่องเว็บภายในพื้นที่ทำงาน | เอเจนต์ที่คุณควบคุมจากแชท |
| Agent Canvas | UI บนเบราว์เซอร์และแบ็กเอนด์ที่รันการสนทนา OpenHands และแสดงการเรียกใช้เครื่องมือและการเปลี่ยนแปลงไฟล์ | เปิดใช้งานสแต็กทั้งหมดและโฮสต์การสนทนาของคุณ |
| Workspace | โฟลเดอร์โปรเจกต์ที่เอเจนต์ได้รับอนุญาตให้อ่านและแก้ไข | เป้าหมายของการแก้ไขและคำสั่งของเอเจนต์ |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> เวิร์กโฟลว์เอเจนต์เขียนโค้ดจะได้ประโยชน์จากโมเดลและหน้าต่างบริบทที่ใหญ่ขึ้น ใช้
> หน่วยความจำระบบอย่างน้อย 32 GB และควรใช้ 64 GB ขึ้นไปสำหรับโมเดล GGUF ขนาดใหญ่กว่านี้
<!-- @device:end -->

## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## ข้อกำหนดเบื้องต้น


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

คุณต้องมี:

- Lemonade Server ที่ติดตั้งไว้และสามารถให้บริการโมเดลด้านล่างได้

<!-- @os:linux -->
- Node.js 22.12 หรือใหม่กว่า และ `npm` (ใช้โดย CLI `agent-canvas`)
- `uv` ตัวจัดการแพ็กเกจ Python ที่ Agent Canvas ใช้จัดการสภาพแวดล้อมของเซิร์ฟเวอร์เอเจนต์ หากระบบของคุณยังไม่มี
  ให้ติดตั้งจาก
  [คู่มือการติดตั้ง uv](https://docs.astral.sh/uv/getting-started/installation/)
  ก่อนเปิดใช้งาน Agent Canvas
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
  ที่ติดตั้งและกำลังทำงานอยู่ บน Windows สแต็ก Agent Canvas จะรันจาก
  อิมเมจ Docker ที่เผยแพร่ ซึ่งรวม Node.js, `uv` และแพ็กเกจ
  `@openhands/agent-canvas` มาให้แล้ว ดังนั้นคุณไม่จำเป็นต้องติดตั้งสิ่งเหล่านี้บนโฮสต์
<!-- @os:end -->

- โฟลเดอร์โปรเจกต์สำหรับทำงาน ซึ่งอาจเป็นที่เก็บ git ภายในเครื่อง หรือไดเรกทอรีโค้ดใด ๆ
  ที่คุณต้องการให้เอเจนต์ทำงานด้วย

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

## 1. เริ่ม Lemonade Server

เริ่มโมเดลจาก Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **เลือกโมเดลที่เหมาะกับฮาร์ดแวร์ของคุณ** `Qwen3.6-35B-A3B-GGUF` (~20 GB) เป็นโมเดลเขียนโค้ดที่แข็งแกร่ง แต่ต้องการพูลหน่วยความจำขนาดใหญ่ หากอุปกรณ์ของคุณมีหน่วยความจำหรือ GPU VRAM จำกัด ให้เลือกโมเดล GGUF ขนาดเล็กกว่าจากคลังโมเดลของ Lemonade แทน และใช้ ID ของโมเดลนั้นตลอดทั้งเพลย์บุ๊กนี้

> **หมายเหตุ:** การรัน `lemonade run` ครั้งแรกจะดาวน์โหลดโมเดลหากยังไม่มีอยู่ ซึ่งอาจใช้เวลานานขึ้นอยู่กับขนาดโมเดลและการเชื่อมต่อของคุณ

Lemonade เปิดให้ใช้งาน API ที่เข้ากันได้กับ OpenAI ที่:

```text
http://127.0.0.1:13305/api/v1
```

## 2. ตรวจสอบโมเดลภายในเครื่อง

ยืนยันว่า Lemonade สามารถให้บริการโมเดลที่เลือกได้:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

จากนั้นส่งคำขอแชทเล็ก ๆ:

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

หากผลลัพธ์ที่ได้คืออาร์เรย์ `choices` แสดงว่า Lemonade พร้อมสำหรับ Agent Canvas แล้ว

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
## 3. ติดตั้งและเปิดใช้งาน Agent Canvas

<!-- @os:linux -->
ติดตั้งแพ็กเกจ Agent Canvas ที่เผยแพร่ไว้แบบ global:

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

จากนั้นเริ่มการทำงานของสแตกทั้งหมดจากเทอร์มินัล:

```bash
agent-canvas
```

โดยค่าเริ่มต้น Agent Canvas จะเริ่มทำงานที่ `http://localhost:8000` เปิด URL นั้นใน
เบราว์เซอร์ของคุณ พอร์ตนี้ไม่ได้มีความพิเศษแต่อย่างใด — หากพอร์ต 8000 ถูกใช้งานอยู่แล้ว ให้ระบุ
พอร์ตว่างใดก็ได้ด้วย `--port` (หรือ `-p`) เมื่อคุณเปิดใช้งาน Agent Canvas:

```bash
agent-canvas --port 3000
```

จากนั้นเปิด `http://localhost:3000` แทน แบ็กเอนด์ในเครื่องเริ่มต้นควรแสดง
สถานะปกติ (healthy) บนหน้าจอหลัก

คำสั่ง `agent-canvas` จะเริ่มการทำงานของ agent server, automation backend และ
web frontend พร้อมกัน คุณจำเป็นต้องใช้คำสั่งนี้เพียงคำสั่งเดียวเพื่อรัน OpenHands
ในเครื่องของคุณ

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
บน Windows ให้รันอิมเมจคอนเทนเนอร์ Agent Canvas ที่เผยแพร่ไว้ด้วย Docker Desktop
อิมเมจนี้รวม Agent Server, automation backend และ web frontend ไว้ด้วยกัน ดังนั้น
คุณไม่จำเป็นต้องติดตั้ง Node.js, `uv`, หรือ CLI บนโฮสต์

ก่อนอื่น สร้างโฟลเดอร์ config และ workspace ที่คอนเทนเนอร์จะทำการ mount:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

ดึงอิมเมจที่เผยแพร่ไว้ (เป็นสาธารณะ จึงไม่ต้องเข้าสู่ระบบ):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

จากนั้นเริ่มการทำงานของสแตก:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

เปิด `http://localhost:8000/canvas` ในเบราว์เซอร์ของคุณ หากพอร์ต 8000 ถูกใช้งาน
อยู่แล้ว ให้แมปพอร์ตของโฮสต์เป็นพอร์ตอื่น เช่น `-p 8080:8000` แล้วเปิด
`http://localhost:8080/canvas` แทน

> **หมายเหตุ:** การเปิดใช้งานครั้งแรกจะทำการเริ่มต้น Agent Server ภายในคอนเทนเนอร์
> ดังนั้นอาจใช้เวลาสักครู่ก่อนที่แบ็กเอนด์จะรายงานสถานะปกติ

การ mount `.openhands` จะช่วยให้โปรไฟล์ LLM และการตั้งค่าของคุณคงอยู่ข้ามการรีสตาร์ท
คอนเทนเนอร์ ส่วนที่เหลือของคู่มือนี้จะตั้งค่าทุกอย่างผ่านหน้า UI ของ Agent
Canvas ในเบราว์เซอร์ของคุณ

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

## 4. กำหนดค่า LLM ในเครื่อง

เมื่อเปิดใช้งานครั้งแรก Agent Canvas จะเปิดขั้นตอนการเริ่มต้นใช้งาน (onboarding) ในขั้นตอนนั้น:

1. คงค่า **OpenHands** ให้เลือกอยู่เป็น agent แล้วคลิก **Next**
2. ที่หน้า **Set up your LLM** ให้เลือก **Advanced**
3. คงค่า **Authentication** ไว้ที่ **API key**
4. ตั้งค่า **Custom Model** เป็น `openai/Qwen3.6-35B-A3B-GGUF`
5. ตั้งค่า **Base URL** เป็น `http://127.0.0.1:13305/api/v1`
   <!-- @os:windows -->
   > บน Windows สแตกจะทำงานอยู่ในคอนเทนเนอร์ ซึ่งไม่สามารถเข้าถึงโฮสต์ที่
   > `127.0.0.1` ได้ ให้ใช้ `http://host.docker.internal:13305/api/v1` แทน เพื่อให้
   > agent ที่อยู่ในคอนเทนเนอร์สามารถเข้าถึง Lemonade ที่รันอยู่บนโฮสต์ Windows ได้
   <!-- @os:end -->
6. สำหรับ **API Key** ให้ป้อนค่าตัวยึดตำแหน่ง (placeholder) ใดก็ได้ที่ไม่ว่างเปล่า เช่น `lemonade-local`
   Lemonade ไม่ต้องการคีย์จริง แต่ไคลเอนต์ OpenHands ต้องการค่าเพื่อส่งไป
7. คลิก **Next**

การตั้งค่า Advanced ที่เสร็จสมบูรณ์ควรมีลักษณะดังนี้ ช่อง API key จะถูกซ่อน
โดย UI

![การตั้งค่า LLM Advanced สำหรับการใช้งานครั้งแรกของ Agent Canvas พร้อมโมเดล Lemonade และ base URL ในเครื่อง](assets/01-llm-advanced-settings.png)

Agent Canvas จะบันทึกค่าเหล่านี้เป็นโปรไฟล์ LLM หากเวอร์ชันของคุณให้ตั้งชื่อ
โปรไฟล์นั้น ให้ใช้ชื่อที่ไม่มีเว้นวรรค เช่น `lemonade-local` หากคุณเปลี่ยน
โมเดลในภายหลัง ให้เปิด **Settings > LLM** แล้วอัปเดตช่อง Advanced เดียวกัน คุณ
สามารถสลับโปรไฟล์ที่บันทึกไว้ได้จากช่องแชทด้วยคำสั่ง `/model`

## 5. เปิด Workspace

agent สามารถอ่านและแก้ไขไฟล์ได้เฉพาะภายใน workspace ที่คุณเลือกเท่านั้น ก่อน
เริ่มงาน ให้ชี้ Agent Canvas ไปที่โฟลเดอร์โปรเจกต์ของคุณ:

1. จากหน้าจอหลัก ให้เลือก **Open Workspace**
2. เลือกโฟลเดอร์ที่มีโปรเจกต์ของคุณ (เช่น git repository
   ที่คุณต้องการให้ agent ทำงานด้วย)
3. เริ่มการสนทนาใหม่ใน workspace นั้น

ทุกสิ่งที่ agent ทำ—การอ่านไฟล์ การรันคำสั่ง การแก้ไขโค้ด—จะถูกจำกัดขอบเขต
อยู่ภายใน workspace นั้น

![หน้าหลักของ Agent Canvas หลังจากขั้นตอนการเริ่มต้นใช้งาน](assets/02-agent-canvas-home.png)

## 6. รันงานเขียนโค้ดครั้งแรกของคุณ

เมื่อเปิด workspace และเลือก LLM ในเครื่องแล้ว ให้พิมพ์งานที่เป็นรูปธรรมลงใน
แชท งานแรกที่ดีควรมีขนาดเล็กและตรวจสอบได้ ตัวอย่างเช่น:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

สังเกตไทม์ไลน์ของการสนทนา OpenHands จะ:

- อ่าน workspace เพื่อทำความเข้าใจโครงสร้าง
- สร้าง `hello.py` ที่มีฟังก์ชันและบล็อกทดสอบตามที่ร้องขอ
- รัน `python3 hello.py` (ถ้าจำเป็น) เพื่อตรวจสอบผลลัพธ์
- รายงานสิ่งที่ทำและผลลัพธ์ของคำสั่งใดๆ ในแชท

คุณควรเห็นไฟล์ใหม่ปรากฏใน workspace และข้อความสุดท้ายของ agent ควรอธิบาย
การเปลี่ยนแปลงที่ทำ นี่คือช่วงเวลาแห่งผลลัพธ์: agent ได้เขียนและรันโค้ดจริง
ในโฟลเดอร์โปรเจกต์ของคุณ

## 7. ตรวจสอบและกำกับทิศทางการทำงานของ Agent

หลังจากที่ agent ทำขั้นตอนหนึ่งเสร็จแล้ว ให้ตรวจสอบผลงานก่อนที่จะยอมรับขั้นตอน
ถัดไป:

- **การเปลี่ยนแปลงไฟล์**: ใช้ตัวเรียกดูไฟล์ของ workspace หรือมุมมอง diff ของ agent
  เพื่อดูสิ่งที่ถูกเพิ่ม เปลี่ยนแปลง หรือลบไปอย่างชัดเจน
- **ผลลัพธ์ของคำสั่ง**: ขยายดูคำสั่งใดๆ ที่ agent รันเพื่อดู stdout, stderr
  และ exit code
- **การติดตามผล**: หากผลลัพธ์ไม่ตรงกับที่คุณต้องการ ให้ตอบกลับในการสนทนา
  เดียวกันพร้อมการแก้ไข agent จะเก็บบริบทก่อนหน้าไว้และทำงานซ้ำกับไฟล์เดิม

ตัวอย่างเช่น หากการทดสอบไม่ได้พิมพ์คำทักทายตามที่คาดไว้ ให้ตอบกลับว่า:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

agent จะอ่านไฟล์ใหม่ รันคำสั่ง วินิจฉัยปัญหา และแก้ไขไฟล์อีกครั้ง—ทั้งหมดนี้
อยู่ในการสนทนาเดียวกัน
## การแก้ไขปัญหา

<!-- @os:linux -->
- **`agent-canvas` ไม่ได้อยู่ใน PATH:** ให้ติดตั้งใหม่ด้วย
  `npm install -g @openhands/agent-canvas` และตรวจสอบว่าไดเรกทอรีไบนารีระดับ global ของ npm
  อยู่ใน PATH ของคุณก่อนที่จะสามารถเรียกใช้ `agent-canvas` จากเทอร์มินัลใหม่ได้
- **`npm install -g` ล้มเหลวเนื่องจากข้อผิดพลาดด้านสิทธิ์การเข้าถึง:** ให้กำหนดค่าไดเรกทอรี npm
  ระดับ global ที่เป็นของผู้ใช้ แล้วเปิดเทอร์มินัลใหม่และติดตั้ง Agent Canvas อีกครั้ง

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` หายไป:** ให้ติดตั้งจาก
  [คู่มือการติดตั้ง uv](https://docs.astral.sh/uv/getting-started/installation/)
  Agent Canvas ใช้ `uv` เพื่อจัดการสภาพแวดล้อม Python ของเซิร์ฟเวอร์ตัวแทน
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` หรือ `docker run` เชื่อมต่อไม่สำเร็จ:** ตรวจสอบให้แน่ใจว่า Docker Desktop
  กำลังทำงานอยู่ (ไอคอนรูปวาฬจะปรากฏในถาดระบบ) และเอนจินเริ่มทำงานเสร็จสมบูรณ์แล้ว
  คำสั่ง `docker version` ควรแสดงผลทั้งส่วน Client และ Server
- **คอนเทนเนอร์เริ่มทำงานแต่แบ็กเอนด์ไม่พร้อมใช้งานเลย:** การเปิดใช้งานครั้งแรกจะเป็นการเริ่มต้น
  Agent Server ภายในคอนเทนเนอร์ ให้รอสักครู่ (หนึ่งถึงสองนาที) จากนั้นตรวจสอบ
  `docker logs <container>` เพื่อดูข้อผิดพลาด
- **คอนเทนเนอร์ไม่สามารถเชื่อมต่อกับ Lemonade ได้:** คอนเทนเนอร์จะเข้าถึงโฮสต์ผ่าน
  `host.docker.internal` ให้ยืนยันว่า Lemonade กำลังให้บริการอยู่บนโฮสต์ Windows ด้วย
  `lemonade status` และใช้ `http://host.docker.internal:13305/api/v1` เป็น Base URL
  เมื่อกำหนดค่า LLM
<!-- @os:end -->

- **UI โหลดขึ้นมาได้แต่แบ็กเอนด์แสดงสถานะไม่พร้อมใช้งาน:** ให้รอสักครู่ (หนึ่งถึงสองนาที)
  เพื่อให้เซิร์ฟเวอร์ตัวแทนเริ่มทำงานเสร็จสมบูรณ์ แล้วรีเฟรชหน้าจอ หากยังคงไม่พร้อมใช้งาน
  ให้รีสตาร์ทสแตกและตรวจสอบล็อกเพื่อดูข้อผิดพลาด
- **คำขอแชทของ Lemonade ล้มเหลวด้วยข้อผิดพลาดในการเชื่อมต่อ:** ให้ยืนยันว่า
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` สำเร็จ และ Lemonade
  ยังคงให้บริการโมเดลอยู่ด้วย `lemonade status`
- **ตัวแทนแสดงข้อผิดพลาดเกี่ยวกับความยาวบริบทหรือขีดจำกัดโทเคน:** ให้เริ่มการสนทนาใหม่
  เพื่อไม่ให้ตัวแทนต้องแบกรับประวัติที่มีขนาดใหญ่เกินไป หากยังคงเกิดปัญหานี้อยู่
  ให้รีสตาร์ท Lemonade ด้วยค่า `ctx_size` ที่ใหญ่กว่าค่าเริ่มต้นซึ่งอยู่ที่
  65536 (ตัวอย่างเช่น `ctx_size=131072`) หากหน่วยความจำเพียงพอ
- **ตัวแทนสร้างการแก้ไขที่มีคุณภาพต่ำหรือไม่สมบูรณ์:** ให้เปลี่ยนไปใช้โมเดลที่ใหญ่ขึ้นใน
  Lemonade หรือมอบหมายงานที่เล็กลงและเจาะจงมากขึ้นให้ตัวแทน แล้วรอให้ทำงานเสร็จก่อน
  ที่จะขอให้ทำการเปลี่ยนแปลงถัดไป

## ขั้นตอนถัดไป

- ลองทำงานที่ใหญ่ขึ้นในพื้นที่ทำงานเดียวกัน เช่น การเพิ่มไฟล์ทดสอบยูนิตหรือการแก้ไขข้อบกพร่องที่ทราบอยู่แล้ว
  และตรวจสอบความแตกต่าง (diff) ของตัวแทนก่อนที่จะเก็บการเปลี่ยนแปลงไว้
- เชื่อมต่อเซิร์ฟเวอร์ MCP เช่น GitHub หรือ Slack ภายใต้ **Customize**
  เพื่อให้ตัวแทนสามารถอ่านปัญหาต่างๆ (issues) หรือโพสต์การอัปเดตในระหว่างที่ทำงานได้
- บันทึกโปรไฟล์ LLM หลายรายการ (โมเดลขนาดเล็กที่รวดเร็วและโมเดลขนาดใหญ่ที่มีประสิทธิภาพมากกว่า)
  และสลับไปมาระหว่างโปรไฟล์เหล่านั้นด้วย `/model` ในระหว่างการสนทนา
- ก้าวต่อไปยัง [ระบบอัตโนมัติของ OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
  เพื่อเปลี่ยนวงจรการพัฒนาที่เกิดขึ้นซ้ำๆ ให้กลายเป็นการรันตัวแทนแบบตามกำหนดเวลาหรือเมื่อมีเหตุการณ์เกิดขึ้น

## แหล่งข้อมูล

- [เอกสารประกอบของ OpenHands](https://docs.openhands.dev/)
- [ภาพรวมของ Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [การตั้งค่า Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [โปรไฟล์ LLM และการกำหนดค่าโมเดล](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [เอกสารประกอบของ Lemonade Server](https://lemonade-server.ai/docs)

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