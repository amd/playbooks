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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) คือเอเจนต์ซอฟต์แวร์ AI
ที่สามารถเขียนโค้ด รันคำสั่ง เรียกดูเว็บ และแก้ไขไฟล์ในพื้นที่ทำงานจริง
แทนที่จะคัดลอกคำแนะนำออกจากหน้าต่างแชท คุณเพียงชี้เอเจนต์ไปยังโฟลเดอร์โปรเจกต์
แล้วปล่อยให้มันทำงาน ไม่ว่าจะเป็นการพัฒนาฟีเจอร์ แก้ไขบั๊ก เขียนเทสต์ หรืออธิบายโค้ดเบส

[Agent Canvas](https://github.com/OpenHands/agent-canvas) คือ UI เบราว์เซอร์ที่แนะนำ
สำหรับการรัน OpenHands คำสั่งเดียวคือ `agent-canvas` จะเริ่มต้นเซิร์ฟเวอร์เอเจนต์
แบ็กเอนด์สำหรับการทำงานอัตโนมัติ และเว็บฟรอนต์เอนด์พร้อมกัน ทำให้คุณสามารถ
สนทนากับเอเจนต์ได้จากเบราว์เซอร์ของคุณ

เพื่อให้ทุกอย่างอยู่บนระบบ AMD ของคุณ เอเจนต์จะสื่อสารกับโมเดลภายในเครื่องที่ให้บริการ
โดย Lemonade Server Lemonade จะเปิดใช้งานโมเดลนั้นผ่าน API ที่รองรับ OpenAI
ดังนั้น Agent Canvas จึงสามารถกำหนดค่าให้ใช้งานได้เหมือนกับ endpoint สไตล์ OpenAI ทั่วไป
ในขณะที่โมเดล โค้ดของคุณ และบริบทการสนทนาทั้งหมดยังคงอยู่บนเครื่องของคุณ

ใน playbook นี้ คุณจะเริ่มต้นโมเดลภายในเครื่อง เปิดใช้งาน Agent Canvas
ชี้ไปยังโมเดลนั้น และรันงานเขียนโค้ดชิ้นแรกของคุณกับโฟลเดอร์โปรเจกต์จริง

## สิ่งที่คุณจะได้เรียนรู้

- วิธีเริ่มต้น Lemonade Server และยืนยันว่าโมเดลภายในเครื่องตอบสนองต่อคำขอแชทได้
- วิธีติดตั้งและเปิดใช้งาน Agent Canvas จากแพ็กเกจ npm
- วิธีกำหนดค่า Agent Canvas ให้ใช้โมเดล Lemonade ภายในเครื่องเป็น LLM
- วิธีเริ่มต้นการสนทนา OpenHands และดูเอเจนต์แก้ไขไฟล์และรันคำสั่งในพื้นที่ทำงาน
- วิธีตรวจสอบสิ่งที่เอเจนต์เปลี่ยนแปลง และควบคุมทิศทางด้วยข้อความติดตามผล

## แนวคิดหลัก

| แนวคิด | คืออะไร | มีบทบาทอย่างไรใน playbook นี้ |
| --- | --- | --- |
| Lemonade Server | แพลตฟอร์มให้บริการ LLM ภายในเครื่องที่สร้างขึ้นสำหรับฮาร์ดแวร์ AMD ซึ่งเปิดใช้งาน API ที่รองรับ OpenAI ข้อมูลของคุณจะไม่ออกจากเครื่องของคุณเลย | รันโมเดลที่ขับเคลื่อนเอเจนต์ |
| OpenHands | เอเจนต์ซอฟต์แวร์ AI ที่อ่านและแก้ไขไฟล์ รันคำสั่งเชลล์ และเรียกดูเว็บภายในพื้นที่ทำงาน | เอเจนต์ที่คุณควบคุมจากแชท |
| Agent Canvas | UI เบราว์เซอร์และแบ็กเอนด์ที่รันการสนทนา OpenHands และแสดงการเรียกใช้เครื่องมือและการเปลี่ยนแปลงไฟล์ | เปิดใช้งานสแต็กและโฮสต์การสนทนาของคุณ |
| พื้นที่ทำงาน (Workspace) | โฟลเดอร์โปรเจกต์ที่เอเจนต์ได้รับอนุญาตให้อ่านและแก้ไข | เป้าหมายของการแก้ไขและคำสั่งของเอเจนต์ |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> เวิร์กโฟลว์เอเจนต์เขียนโค้ดจะได้ประโยชน์จากโมเดลขนาดใหญ่และหน้าต่างบริบทที่กว้างขึ้น
> ควรใช้หน่วยความจำระบบอย่างน้อย 32 GB และควรใช้ 64 GB ขึ้นไปสำหรับโมเดล GGUF ขนาดใหญ่กว่า

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

- ติดตั้ง Lemonade Server และสามารถให้บริการโมเดลด้านล่างได้

<!-- @os:linux -->
- Node.js 22.12 หรือใหม่กว่า และ `npm` (ใช้โดย CLI ของ `agent-canvas`)
- `uv` ตัวจัดการแพ็กเกจ Python ที่ Agent Canvas ใช้จัดการสภาพแวดล้อมของเซิร์ฟเวอร์เอเจนต์
  หากระบบของคุณยังไม่มี ให้ติดตั้งจาก
  [คู่มือการติดตั้ง uv](https://docs.astral.sh/uv/getting-started/installation/)
  ก่อนเปิดใช้งาน Agent Canvas
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop สำหรับ Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
  ติดตั้งและกำลังทำงานอยู่ บน Windows สแต็ก Agent Canvas จะรันจาก
  Docker image ที่เผยแพร่ ซึ่งรวม Node.js, `uv`, และแพ็กเกจ
  `@openhands/agent-canvas` ไว้ด้วยกัน ดังนั้นคุณจึงไม่ต้องติดตั้งสิ่งเหล่านั้นบนโฮสต์
<!-- @os:end -->

- โฟลเดอร์โปรเจกต์สำหรับทำงาน สามารถเป็น git repository ในเครื่องหรือไดเรกทอรีโค้ดใดก็ได้
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

## 1. เริ่มต้น Lemonade Server

เริ่มต้นโมเดลจาก Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **เลือกโมเดลที่เหมาะกับฮาร์ดแวร์ของคุณ** `Qwen3.6-35B-A3B-GGUF` (~20 GB) เป็นโมเดลเขียนโค้ดที่แข็งแกร่ง แต่ต้องการพูลหน่วยความจำขนาดใหญ่ หากอุปกรณ์ของคุณมีหน่วยความจำหรือ GPU VRAM จำกัด ให้เลือกโมเดล GGUF ขนาดเล็กกว่าจากไลบรารีโมเดลของ Lemonade แทน และใช้ model ID นั้นตลอดทั้ง playbook นี้

> **หมายเหตุ:** การรัน `lemonade run` ครั้งแรกจะดาวน์โหลดโมเดลหากยังไม่มีอยู่ ซึ่งอาจใช้เวลาสักครู่ขึ้นอยู่กับขนาดโมเดลและการเชื่อมต่อของคุณ

Lemonade เปิดใช้งาน API ที่รองรับ OpenAI ที่:

```text
http://127.0.0.1:13305/api/v1
```

## 2. ตรวจสอบโมเดลภายในเครื่อง

ยืนยันว่า Lemonade สามารถให้บริการโมเดลที่เลือกได้:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

จากนั้นส่งคำขอแชทเล็กๆ:

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

หากได้รับอาร์เรย์ `choices` กลับมา แสดงว่า Lemonade พร้อมสำหรับ Agent Canvas แล้ว

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
ติดตั้งแพ็กเกจ Agent Canvas ที่เผยแพร่แล้วแบบ global:

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

โดยค่าเริ่มต้น Agent Canvas จะเริ่มทำงานที่ `http://localhost:8000` เปิด URL
นั้นในเบราว์เซอร์ของคุณ พอร์ตนี้ไม่ได้มีความพิเศษแต่อย่างใด — หากพอร์ต 8000
ถูกใช้งานอยู่แล้ว ให้ระบุพอร์ตว่างใดก็ได้ด้วย `--port` (หรือ `-p`)
เมื่อคุณเปิดใช้งาน Agent Canvas:

```bash
agent-canvas --port 3000
```

จากนั้นให้เปิด `http://localhost:3000` แทน แบ็กเอนด์เฉพาะที่ (local backend)
เริ่มต้นควรแสดงสถานะปกติ (healthy) บนหน้าจอหลัก

คำสั่ง `agent-canvas` จะเริ่มทำงานทั้ง agent server, automation backend และ
web frontend พร้อมกัน คุณต้องใช้เพียงคำสั่งเดียวนี้เท่านั้นในการรัน OpenHands
บนเครื่องของคุณเอง

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
บน Windows ให้รันอิมเมจคอนเทนเนอร์ Agent Canvas ที่เผยแพร่แล้วด้วย Docker Desktop
อิมเมจนี้รวม Agent Server, automation backend และ web frontend ไว้ด้วยกัน
คุณจึงไม่จำเป็นต้องติดตั้ง Node.js, `uv`, หรือ CLI บนเครื่องโฮสต์

ก่อนอื่น ให้สร้างโฟลเดอร์ config และ workspace ที่คอนเทนเนอร์จะเมาท์:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

ดึงอิมเมจที่เผยแพร่แล้ว (เป็นสาธารณะ จึงไม่ต้องล็อกอิน):

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

เปิด `http://localhost:8000/canvas` ในเบราว์เซอร์ของคุณ หากพอร์ต 8000
ถูกใช้งานอยู่แล้ว ให้แมปพอร์ตโฮสต์อื่น เช่น `-p 8080:8000` แล้วเปิด
`http://localhost:8080/canvas` แทน

> **หมายเหตุ:** การเปิดใช้งานครั้งแรกจะเป็นการเริ่มต้น Agent Server
> ภายในคอนเทนเนอร์ จึงอาจใช้เวลาสักครู่ก่อนที่แบ็กเอนด์จะรายงานสถานะปกติ

การเมาท์ `.openhands` จะเก็บโปรไฟล์ LLM และการตั้งค่าของคุณไว้ให้คงอยู่แม้จะ
รีสตาร์ทคอนเทนเนอร์ เนื้อหาที่เหลือของแนวทางนี้จะกำหนดค่าทุกอย่างผ่าน UI ของ
Agent Canvas ในเบราว์เซอร์ของคุณ

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

## 4. กำหนดค่า LLM แบบ Local

เมื่อเปิดใช้งานครั้งแรก Agent Canvas จะเปิดขั้นตอนการเริ่มต้นใช้งาน (onboarding)
ในขั้นตอนนั้น:

1. คงค่า **OpenHands** ไว้เป็น agent ที่เลือก แล้วคลิก **Next**
2. ที่หน้า **Set up your LLM** ให้เลือก **Advanced**
3. คงค่า **Authentication** ไว้เป็น **API key**
4. ตั้งค่า **Custom Model** เป็น `openai/Qwen3.6-35B-A3B-GGUF`
5. ตั้งค่า **Base URL** เป็น `http://127.0.0.1:13305/api/v1`
   <!-- @os:windows -->
   > บน Windows สแตกจะรันอยู่ในคอนเทนเนอร์ ซึ่งไม่สามารถเข้าถึงโฮสต์ที่
   > `127.0.0.1` ได้ ให้ใช้ `http://host.docker.internal:13305/api/v1` แทน
   > เพื่อให้ agent ในคอนเทนเนอร์สามารถเข้าถึง Lemonade ที่รันอยู่บนเครื่อง
   > โฮสต์ Windows ได้
   <!-- @os:end -->
6. สำหรับ **API Key** ให้ป้อนค่าตัวยึดตำแหน่ง (placeholder) ที่ไม่ว่างเปล่าใดก็ได้
   เช่น `lemonade-local` Lemonade ไม่ต้องการคีย์จริง แต่ไคลเอนต์ OpenHands
   จำเป็นต้องส่งค่าบางอย่าง
7. คลิก **Next**

การตั้งค่า Advanced ที่เสร็จสมบูรณ์ควรมีลักษณะดังนี้ ช่อง API key จะถูกซ่อนไว้
โดย UI

![การตั้งค่า LLM Advanced ในการใช้งานครั้งแรกของ Agent Canvas พร้อมโมเดล Lemonade และ base URL แบบเฉพาะที่](assets/01-llm-advanced-settings.png)

Agent Canvas จะบันทึกค่าเหล่านี้เป็นโปรไฟล์ LLM หากเวอร์ชันของคุณให้ตั้งชื่อ
โปรไฟล์นั้น ให้ใช้ชื่อที่ไม่มีช่องว่าง เช่น `lemonade-local` หากคุณเปลี่ยน
โมเดลในภายหลัง ให้เปิด **Settings > LLM** แล้วอัปเดตช่อง Advanced เดิม คุณ
สามารถสลับโปรไฟล์ที่บันทึกไว้จากช่องแชทได้ด้วยคำสั่ง `/model`

## 5. เปิด Workspace

agent จะสามารถอ่านและแก้ไขไฟล์ได้เฉพาะภายใน workspace ที่คุณเลือกเท่านั้น
ก่อนเริ่มงาน ให้ชี้ Agent Canvas ไปยังโฟลเดอร์โปรเจกต์ของคุณ:

1. จากหน้าจอหลัก เลือก **Open Workspace**
2. เลือกโฟลเดอร์ที่มีโปรเจกต์ของคุณ (ตัวอย่างเช่น git repository
   ที่คุณต้องการให้ agent ทำงานด้วย)
3. เริ่มการสนทนาใหม่ใน workspace นั้น

ทุกสิ่งที่ agent ทำ—การอ่านไฟล์ การรันคำสั่ง การแก้ไขโค้ด—จะถูกจำกัดขอบเขต
ไว้เฉพาะภายใน workspace นั้น

![หน้าหลักของ Agent Canvas หลังการเริ่มต้นใช้งาน](assets/02-agent-canvas-home.png)

## 6. รันงานเขียนโค้ดครั้งแรกของคุณ

เมื่อเปิด workspace และเลือก LLM แบบ local แล้ว ให้พิมพ์งานที่เจาะจงลงใน
แชท งานแรกที่ดีควรมีขนาดเล็กและสามารถตรวจสอบผลลัพธ์ได้ ตัวอย่างเช่น:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

สังเกตไทม์ไลน์ของการสนทนา OpenHands จะ:

- อ่าน workspace เพื่อทำความเข้าใจโครงสร้าง
- สร้าง `hello.py` ที่มีฟังก์ชันและบล็อกทดสอบตามที่ร้องขอ
- อาจรัน `python3 hello.py` เพื่อยืนยันผลลัพธ์
- รายงานสิ่งที่ทำและผลลัพธ์ของคำสั่งใด ๆ ในแชท

คุณควรเห็นไฟล์ใหม่ปรากฏใน workspace และข้อความสุดท้ายของ agent
ควรอธิบายถึงการเปลี่ยนแปลงที่ทำ นี่คือช่วงเวลาแห่งผลลัพธ์: agent
ได้เขียนและรันโค้ดจริงในโฟลเดอร์โปรเจกต์ของคุณ

## 7. ตรวจสอบและควบคุมทิศทางของ Agent

หลังจาก agent ทำงานแต่ละขั้นตอนเสร็จสิ้น ให้ตรวจสอบผลงานก่อนที่จะยอมรับขั้น
ตอนถัดไป:

- **การเปลี่ยนแปลงไฟล์**: ใช้ file browser ของ workspace หรือมุมมอง diff
  ของ agent เพื่อดูสิ่งที่ถูกเพิ่ม เปลี่ยนแปลง หรือลบออกอย่างชัดเจน
- **ผลลัพธ์ของคำสั่ง**: ขยายดูคำสั่งใด ๆ ที่ agent รัน เพื่อดู stdout,
  stderr และ exit code
- **การติดตามผล**: หากผลลัพธ์ไม่เป็นไปตามที่คุณต้องการ ให้ตอบกลับในการ
  สนทนาเดิมพร้อมคำแก้ไข agent จะเก็บบริบทก่อนหน้าไว้และทำซ้ำกับไฟล์เดิม

ตัวอย่างเช่น หากการทดสอบไม่ได้พิมพ์คำทักทายตามที่คาดไว้ ให้ตอบกลับว่า:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

agent จะอ่านไฟล์ใหม่ รันคำสั่ง วินิจฉัยปัญหา และแก้ไขไฟล์อีกครั้ง—ทั้งหมด
ภายในการสนทนาเดียวกัน
## การแก้ไขปัญหา

<!-- @os:linux -->
- **`agent-canvas` ไม่ได้อยู่ใน PATH:** ให้ติดตั้งใหม่ด้วย
  `npm install -g @openhands/agent-canvas` และตรวจสอบว่าไดเรกทอรี binary
  แบบ global ของ npm อยู่ใน PATH ของคุณก่อนที่จะสามารถเรียกใช้ `agent-canvas`
  จากเทอร์มินัลใหม่ได้
- **`npm install -g` ล้มเหลวเนื่องจากปัญหาสิทธิ์การเข้าถึง:** ให้กำหนดค่าไดเรกทอรี
  global npm ที่ผู้ใช้เป็นเจ้าของ จากนั้นเปิดเทอร์มินัลใหม่และติดตั้ง Agent Canvas อีกครั้ง

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` หายไป:** ให้ติดตั้งจาก
  [คู่มือการติดตั้ง uv](https://docs.astral.sh/uv/getting-started/installation/)
  Agent Canvas ใช้ `uv` เพื่อจัดการสภาพแวดล้อม Python ของ agent server
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` หรือ `docker run` เชื่อมต่อไม่สำเร็จ:** ตรวจสอบให้แน่ใจว่า Docker Desktop
  กำลังทำงานอยู่ (ไอคอนรูปวาฬอยู่ในถาดระบบ) และเอนจินเริ่มทำงานเสร็จเรียบร้อยแล้ว
  `docker version` ควรแสดงทั้งส่วน Client และ Server
- **คอนเทนเนอร์เริ่มทำงานแล้วแต่ backend ไม่พร้อมใช้งาน (healthy):** การเปิดใช้งานครั้งแรก
  จะเริ่มต้น Agent Server ภายในคอนเทนเนอร์ ให้รอสักหนึ่งถึงสองนาที
  แล้วตรวจสอบ `docker logs <container>` เพื่อดูข้อผิดพลาด
- **คอนเทนเนอร์ไม่สามารถเชื่อมต่อกับ Lemonade ได้:** คอนเทนเนอร์เข้าถึงโฮสต์ผ่าน
  `host.docker.internal` ให้ยืนยันว่า Lemonade กำลังให้บริการอยู่บนโฮสต์ Windows
  ด้วย `lemonade status` และใช้ `http://host.docker.internal:13305/api/v1`
  เป็น Base URL เมื่อกำหนดค่า LLM
<!-- @os:end -->

- **UI โหลดขึ้นมาแต่ backend แสดงสถานะไม่พร้อมใช้งาน:** ให้รอสักหนึ่งถึงสองนาที
  เพื่อให้ agent server เริ่มทำงานเสร็จสมบูรณ์ แล้วรีเฟรชอีกครั้ง หากยังคงไม่พร้อมใช้งาน
  ให้รีสตาร์ตสแตกและตรวจสอบล็อกเพื่อดูข้อผิดพลาด
- **คำขอแชทของ Lemonade ล้มเหลวด้วยข้อผิดพลาดในการเชื่อมต่อ:** ให้ยืนยันว่า
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` สำเร็จ และ
  Lemonade ยังคงให้บริการโมเดลอยู่ด้วย `lemonade status`
- **agent แสดงข้อผิดพลาดเกี่ยวกับความยาวบริบทหรือข้อจำกัดของโทเคน:** ให้เริ่มต้น
  การสนทนาใหม่เพื่อไม่ให้ agent แบกรับประวัติที่ใหญ่เกินไป หากยังคงเกิดขึ้นซ้ำ
  ให้รีสตาร์ต Lemonade ด้วยค่า `ctx_size` ที่มากกว่าค่าเริ่มต้น 65536
  (ตัวอย่างเช่น `ctx_size=131072`) หากหน่วยความจำเพียงพอ
- **agent สร้างการแก้ไขที่มีคุณภาพต่ำหรือไม่สมบูรณ์:** ให้เปลี่ยนไปใช้โมเดลที่ใหญ่ขึ้น
  ใน Lemonade หรือมอบหมายงานที่เล็กลงและเจาะจงมากขึ้นให้ agent และปล่อยให้ทำเสร็จ
  ก่อนที่จะขอให้แก้ไขในส่วนถัดไป

## ขั้นตอนถัดไป

- ลองทำงานที่ใหญ่ขึ้นในพื้นที่ทำงานเดียวกัน เช่น การเพิ่มไฟล์ unit test หรือ
  การแก้ไขบั๊กที่รู้จัก และตรวจสอบ diff ของ agent ก่อนที่จะเก็บการเปลี่ยนแปลงนั้นไว้
- เชื่อมต่อ MCP server เช่น GitHub หรือ Slack ภายใต้ **Customize** เพื่อให้
  agent สามารถอ่าน issue หรือโพสต์อัปเดตในขณะที่กำลังทำงานได้
- บันทึกโปรไฟล์ LLM หลายชุด (โมเดลขนาดเล็กที่รวดเร็วและโมเดลขนาดใหญ่ที่ทรงพลังกว่า)
  และสลับไปมาระหว่างโปรไฟล์เหล่านั้นด้วย `/model` ระหว่างการสนทนา
- ไปยังขั้นตอนถัดไปที่ [OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview) เพื่อ
  เปลี่ยนวงจรการพัฒนาที่เกิดขึ้นซ้ำให้กลายเป็นการรัน agent ที่กำหนดเวลาหรือทริกเกอร์ตามเหตุการณ์

## แหล่งข้อมูล

- [เอกสาร OpenHands](https://docs.openhands.dev/)
- [ภาพรวม Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [การตั้งค่า Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [โปรไฟล์ LLM และการกำหนดค่าโมเดล](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [เอกสาร Lemonade Server](https://lemonade-server.ai/docs)

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