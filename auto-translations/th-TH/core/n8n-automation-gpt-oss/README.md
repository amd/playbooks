<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Playbook นี้ใช้แท็กพิเศษที่ GitHub ไม่สามารถแสดงผลได้ กรุณาเยี่ยมชม [amd.com/playbooks](https://amd.com/playbooks) เพื่อดูตัวอย่างเนื้อหานี้อย่างถูกต้อง
<!-- @github-only:end -->

## ภาพรวม

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Playbook นี้ต้องการหน่วยความจำระบบขั้นต่ำ **32GB**
<!-- @device:end -->

n8n คือแพลตฟอร์มอัตโนมัติสำหรับเวิร์กโฟลว์ที่ช่วยให้คุณเชื่อมต่อแอปและบริการต่างๆ โดยใช้ตัวแก้ไขแบบ visual node-based

Playbook นี้จะสอนวิธีตั้งค่าระบบสรุปข่าวการเงินที่ขับเคลื่อนด้วย AI ซึ่งดึงข้อมูลจากหน้าธุรกิจของ AP News ดึงหัวข้อข่าวสำคัญ และใช้ LLM ในเครื่องที่รันบนระบบของคุณเพื่อสร้างสรุปที่มุ่งเน้นสำหรับนักลงทุน

## สิ่งที่คุณจะได้เรียนรู้

- วิธีติดตั้งและเปิดใช้งาน n8n
- การนำเข้าและกำหนดค่าเวิร์กโฟลว์ที่สร้างไว้ล่วงหน้า
- การเชื่อมต่อกับ Lemonade โดยใช้การผสานรวมแบบ native ของ n8n
- ทำความเข้าใจ node ของเวิร์กโฟลว์และการไหลของข้อมูล

## Lemonade คืออะไร?

[Lemonade](https://lemonade-server.ai) คือแพลตฟอร์มให้บริการ LLM ในเครื่องที่สร้างขึ้นสำหรับฮาร์ดแวร์ AMD โดยมี API ที่เข้ากันได้กับ OpenAI ซึ่งทำงานบนเครื่องของคุณทั้งหมด—ข้อมูลของคุณจะไม่ออกจากอุปกรณ์

ใน Playbook นี้ เราใช้ Lemonade เพื่อให้บริการ LLM ในเครื่องที่ n8n เชื่อมต่อเพื่อทำงานที่ขับเคลื่อนด้วย AI

n8n มี **native Lemonade node** (`Lemonade Chat Model`) ที่ให้การผสานรวมระดับ first-class โดยไม่ต้องกำหนดค่าด้วยตนเอง ทำให้การเชื่อมต่อ LLM ในเครื่องกับเวิร์กโฟลว์อัตโนมัติเป็นเรื่องง่าย

## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


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
  "max_tokens": 32
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

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## การติดตั้ง n8n
<!-- @os:windows -->
ติดตั้ง n8n แบบ global โดยใช้ npm

> **หมายเหตุ**: คุณอาจเห็นคำเตือนจาก npm บางส่วน ซึ่งเป็นเรื่องปกติ

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องแก้ไข PowerShell Execution Policy (เช่น
> ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนรันคำสั่ง Powershell บางคำสั่ง
<!-- @os:end -->


<!-- @os:windows -->
> **ปัญหา PATH**: หาก `n8n --version` แจ้งว่าไม่พบคำสั่ง ให้ตรวจสอบว่า npm global bin directory อยู่ใน `PATH` ของผู้ใช้ เส้นทางการติดตั้งปกติอยู่ที่ `C:\Users\<username>\AppData\Roaming\npm`
> เพิ่มเส้นทางนี้ใน user path (แก้ไขตัวแปรสภาพแวดล้อมของระบบ > Environment Variables > Edit User Path) และโหลด terminal ใหม่

<!-- @os:end -->

<!-- @os:linux -->
ตอนนี้เราจะใช้บริการ Podman เพื่อทำ containerize การติดตั้ง n8n ของเรา

กรุณาดาวน์โหลดไฟล์ต่อไปนี้ไปยังไดเรกทอรีที่คุณเลือก: [compose.yml](assets/compose.yml)

ในไดเรกทอรีนั้น ให้รันคำสั่งต่อไปนี้:
```bash
podman compose up -d
```

ซึ่งจะติดตั้ง n8n และเขียนข้อมูลลงในพื้นที่จัดเก็บแบบถาวร

เปิดใช้งาน n8n โดยพิมพ์ `localhost:5678` ในแถบที่อยู่ของเบราว์เซอร์
<!-- @os:end -->

<!-- @os:windows -->
## การเปิดใช้งาน n8n

เริ่ม n8n จาก terminal:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n เริ่มต้น web server ในเครื่อง กด `'o'` หรือเปิดเบราว์เซอร์ไปที่ `http://localhost:5678` เพื่อเข้าถึงตัวแก้ไข
<!-- @os:end -->


> **เคล็ดลับ**: เปิดหน้าต่าง terminal ไว้ขณะใช้งาน n8n การปิดอาจทำให้ server หยุดทำงาน

## การเปิดใช้งาน Lemonade

Lemonade คือ server ในเครื่องที่จะรันโมเดลและเชื่อมต่อกับ n8n

<!-- @os:linux -->
เปิด Lemonade GUI โดยคลิกไอคอน Lemonade ในแถบงาน คุณสามารถเรียกดูโมเดล, backend และโหลดโมเดลที่ติดตั้งไว้ล่วงหน้าจากที่นี่
<!-- @os:end -->

<!-- @os:windows -->
เปิด Lemonade GUI โดยคลิกไอคอน Lemonade คลิกขวาที่ไอคอนใน tray เพื่อเปิดแอป จากนั้นคุณสามารถเพิ่มโมเดล, backend และโหลดโมเดลที่ติดตั้งไว้ล่วงหน้า
<!-- @os:end -->

>**เคล็ดลับ**: เมื่อรันแล้ว Lemonade GUI ยังสามารถเข้าถึงได้ที่ http://localhost:13305

หรือคุณสามารถเปิด terminal และรัน `lemonade list` เพื่อดูว่าโมเดลใดถูกติดตั้งไว้ จากนั้นรัน:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## การตั้งค่าเวิร์กโฟลว์

### ขั้นตอนที่ 1: สมัครสมาชิกหรือเข้าสู่ระบบ n8n

เมื่อคุณเปิด n8n เป็นครั้งแรก คุณจะได้รับแจ้งให้สร้างบัญชีหรือเข้าสู่ระบบ:

1. เปิด `http://localhost:5678` ในเบราว์เซอร์ของคุณ
2. สร้างบัญชีในเครื่องใหม่ด้วยอีเมลของคุณ หรือเข้าสู่ระบบหากคุณมีบัญชีอยู่แล้ว
3. เมื่อเข้าสู่ระบบแล้ว คุณจะเห็น dashboard ของ n8n

> **เคล็ดลับ**: หากถูกล็อกออกจากบัญชี ให้ลอง `n8n user-management:reset`

### ขั้นตอนที่ 2: นำเข้าเวิร์กโฟลว์

เราได้จัดเตรียมเวิร์กโฟลว์ที่สร้างไว้ล่วงหน้าซึ่งคุณสามารถนำเข้าได้โดยตรง:

1. ดาวน์โหลดไฟล์เวิร์กโฟลว์ต่อไปนี้: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. คลิก **Start from Scratch** เพื่อเปิดตัวแก้ไขเวิร์กโฟลว์ หรือคลิกปุ่ม + ที่มุมบนซ้าย แล้วคลิก **Add workflow**
3. คลิกเมนู **...** (จุดสามจุด) ที่แถบด้านบนขวาและเลือก **Import from file**
4. เลือกไฟล์ `financial-news-workflow.json` ที่ดาวน์โหลดมา
5. เวิร์กโฟลว์จะปรากฏบน canvas


### ขั้นตอนที่ 3: ทำความเข้าใจเวิร์กโฟลว์

เวิร์กโฟลว์ที่นำเข้ามีประกอบด้วย 9 node ที่เชื่อมต่อกัน:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Node | วัตถุประสงค์ |
|------|---------|
| **When clicking 'Execute workflow'** | ทริกเกอร์แบบ manual เพื่อเริ่มเวิร์กโฟลว์ |
| **Fetch Financial News Webpage** | HTTP GET request ไปยัง `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Wait node เพื่อให้แน่ใจว่าเนื้อหาของหน้าโหลดครบถ้วน |
| **Extract News Headlines & Text** | HTML node ที่ดึงหัวข้อข่าว, editor's picks, top stories และข่าวระดับภูมิภาคโดยใช้ CSS selectors |
| **Clean Extracted News Data** | Set node ที่รวมข้อมูลที่ดึงมาทั้งหมดเป็นฟิลด์ข้อความเดียว |
| **AI Financial News Summarizer** | AI Agent ที่ประมวลผลข่าวด้วย system prompt ของนักวิเคราะห์การเงิน |
| **Lemonade Chat Model** | เชื่อมต่อกับ Lemonade server ในเครื่องที่รัน LLM |
| **Structured Output Parser** | จัดรูปแบบผลลัพธ์ AI เป็น JSON ที่มีโครงสร้าง |
| **Convert to File** | แปลงสรุปเป็นไฟล์ที่ดาวน์โหลดได้ |

### ขั้นตอนที่ 4: กำหนดค่า Lemonade Credentials

ก่อนรันเวิร์กโฟลว์ คุณต้องเชื่อมต่อกับ Lemonade server ในเครื่องของคุณ:

1. ดับเบิลคลิก node **Lemonade Chat Model** ใน n8n
2. ในเมนูดรอปดาวน์ **Credential to connect with** เลือก **Create New Credential**
3. ป้อนค่าในตารางด้านล่างและคลิกบันทึก
4. เลือกโมเดลที่เกี่ยวข้องที่คุณโหลดไว้ใน Lemonade Server

  | ฟิลด์ | ค่า |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **หมายเหตุ**: ก่อนทดสอบ ให้รัน `lemonade status` ใน terminal เพื่อยืนยันว่า Lemonade server กำลังทำงานอยู่
<!-- @device:halo_box -->
> เวิร์กโฟลว์นี้ใช้ GPT-OSS-120B และติดตั้งไว้ล่วงหน้าใน Lemonade คุณสามารถเปลี่ยนเป็นโมเดลอื่นที่โหลดไว้ได้ในการตั้งค่า node Lemonade Chat Model
<!-- @device:end -->

### ขั้นตอนที่ 5: ทดสอบเวิร์กโฟลว์

1. ตรวจสอบให้แน่ใจว่า Lemonade กำลังทำงานพร้อมโมเดลที่โหลดไว้
2. คลิก **Execute workflow** ที่กึ่งกลางด้านล่างของ canvas
3. ดูแต่ละ node ทำงานจากซ้ายไปขวา—จะเปลี่ยนเป็นสีเขียวเมื่อเสร็จสมบูรณ์
4. ดับเบิลคลิก node **AI Financial News Summarizer** เพื่อดูสรุปที่สร้างขึ้นในแผงด้านล่าง
5. ดับเบิลคลิก node **Convert to File** เพื่อดาวน์โหลดไฟล์ข้อความที่เกี่ยวข้องในแผงด้านล่าง

## ทำความเข้าใจ AI Agent

AI Financial News Summarizer ใช้ system prompt ที่ออกแบบมาสำหรับการวิเคราะห์ทางการเงิน:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agent รับข้อมูลข่าวที่ผ่านการทำความสะอาดแล้วและส่งออกสรุปที่มีโครงสร้างพร้อมความรู้สึกของตลาด

### การบันทึกเวิร์กโฟลว์ของคุณ

คลิกชื่อเวิร์กโฟลว์ที่ด้านบนและเปลี่ยนชื่อหากต้องการ เวิร์กโฟลว์จะบันทึกอัตโนมัติขณะที่คุณทำงาน

## ขั้นตอนถัดไป

- **กำหนดเวลาอัตโนมัติ**: แทนที่ Manual Trigger ด้วย **Schedule Trigger** เพื่อรันทุกวัน
- **ส่งการแจ้งเตือน**: เพิ่ม node **Discord**, **Slack** หรือ **Email** เพื่อรับสรุป
- **ลองโมเดลต่างๆ**: เปลี่ยนโมเดลใน node Lemonade Chat Model เพื่อทดลองกับ LLM ที่แตกต่างกัน
- **ปรับแต่งการดึงข้อมูล**: แก้ไข CSS selectors ของ node HTML Extract เพื่อกำหนดเป้าหมายส่วนข่าวที่แตกต่างกัน
- **ลอง backend ต่างๆ**: n8n ยังรองรับ [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio และ backend LLM ในเครื่องอื่นๆ

### สำรวจ n8n Templates

n8n มีเทมเพลตเวิร์กโฟลว์ที่สร้างไว้ล่วงหน้าหลายร้อยรายการ เรียกดูไลบรารีเทมเพลตอย่างเป็นทางการได้ที่:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

ค้นหา "AI", "LLM" หรือ "automation" เพื่อค้นหาเวิร์กโฟลว์ที่คุณสามารถนำเข้าและปรับแต่งได้

สำหรับข้อมูลเพิ่มเติม โปรดดูที่ [n8n Documentation](https://docs.n8n.io/)