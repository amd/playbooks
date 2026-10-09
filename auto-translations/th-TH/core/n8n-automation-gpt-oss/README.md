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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->
## ภาพรวม
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> คู่มือนี้ต้องการหน่วยความจำระบบ (system memory) อย่างน้อย **32GB**
<!-- @device:end -->
n8n เป็นแพลตฟอร์มสำหรับระบบอัตโนมัติของเวิร์กโฟลว์ที่ช่วยให้คุณเชื่อมต่อแอปและบริการต่าง ๆ โดยใช้โปรแกรมแก้ไขแบบภาพที่อิงตามโหนด (node-based editor)

คู่มือนี้จะสอนวิธีตั้งค่าระบบสรุปข่าวการเงินที่ขับเคลื่อนด้วย AI ซึ่งดึงพาดหัวข่าวธุรกิจล่าสุดจากฟีด RSS ข่าว และใช้ LLM ในเครื่องที่ทำงานบนระบบของคุณเพื่อสร้างบทสรุปที่เน้นมุมมองของนักลงทุน

## สิ่งที่คุณจะได้เรียนรู้

- วิธีติดตั้งและเปิดใช้งาน n8n
- การนำเข้าและกำหนดค่าเวิร์กโฟลว์ที่สร้างไว้ล่วงหน้า
- การเชื่อมต่อกับ Lemonade โดยใช้การผสานการทำงานแบบเนทีฟของ n8n
- การทำความเข้าใจโหนดเวิร์กโฟลว์และการไหลของข้อมูล

## Lemonade คืออะไร?

[Lemonade](https://lemonade-server.ai) เป็นแพลตฟอร์มให้บริการ LLM ในเครื่องที่สร้างขึ้นสำหรับฮาร์ดแวร์ AMD โดยเฉพาะ โดยมี API ที่เข้ากันได้กับ OpenAI ซึ่งทำงานทั้งหมดบนเครื่องของคุณเอง—ข้อมูลของคุณจะไม่ถูกส่งออกจากอุปกรณ์เลย

ในคู่มือนี้ เราใช้ Lemonade เพื่อให้บริการ LLM ในเครื่องที่ n8n เชื่อมต่อเพื่อทำงานที่ขับเคลื่อนด้วย AI

n8n มี **โหนด Lemonade แบบเนทีฟ** (`Lemonade Chat Model`) ที่มอบการผสานการทำงานระดับเฟิร์สคลาส - ไม่จำเป็นต้องกำหนดค่าด้วยตนเอง ทำให้การเชื่อมต่อ LLM ในเครื่องของคุณเข้ากับเวิร์กโฟลว์อัตโนมัติเป็นเรื่องง่าย
<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าหน่วยความจำ
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
<!-- @require:software-update -->
<!-- @device:end -->
## การติดตั้งซอฟต์แวร์ที่จำเป็นเบื้องต้น
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:n8n,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- Linux runs n8n as a Podman container (see compose.yml below), so Node.js and a host n8n install are not required; podman is the only extra prerequisite. -->
<!-- @require:lemonade,podman -->
<!-- @prereq:podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @prereq:lemonade-models-gpt-oss-120b -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:lemonade-models-gpt-oss-20b -->
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

<!-- @os:windows -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->
## การติดตั้ง n8n
<!-- @os:windows -->
ติดตั้ง n8n แบบ global โดยใช้ npm

> **หมายเหตุ**: คุณอาจเห็นคำเตือน (warning) บางอย่างจาก npm ซึ่งถือเป็นเรื่องปกติ

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องแก้ไข PowerShell Execution Policy (เช่น
> ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนรันคำสั่ง Powershell บางคำสั่ง
<!-- @os:end -->


<!-- @os:windows -->
> **ปัญหาเกี่ยวกับ PATH**: หากคำสั่ง `n8n --version` แสดงข้อความว่าไม่พบคำสั่ง (command not found) ให้ตรวจสอบว่าไดเรกทอรี bin ส่วนกลางของ npm ถูกเพิ่มไว้ใน `PATH` ของผู้ใช้แล้ว โดยปกติแล้วเส้นทางการติดตั้งจะอยู่ที่ `C:\Users\<username>\AppData\Roaming\npm`
> ให้เพิ่มเส้นทางนี้ลงใน user path (ไปที่ Edit the system environment variables > Environment Variables > Edit User Path) จากนั้นรีโหลดเทอร์มินัล
<!-- @os:end -->

<!-- @os:linux -->
ตอนนี้เราจะใช้บริการ Podman เพื่อทำคอนเทนเนอร์การติดตั้ง n8n ของเรา

กรุณาดาวน์โหลดไฟล์ต่อไปนี้ไปยังไดเรกทอรีที่คุณเลือก: [compose.yml](assets/compose.yml)

ในไดเรกทอรีนั้น ให้รันคำสั่งต่อไปนี้:
```bash
podman compose up -d
```

วิธีนี้จะติดตั้ง n8n และเขียนลงในพื้นที่จัดเก็บข้อมูลแบบถาวร

เปิดใช้งาน n8n โดยพิมพ์ `localhost:5678` ในแถบที่อยู่ของเบราว์เซอร์ของคุณ
<!-- @os:end -->

<!-- @os:windows -->
## การเปิดใช้งาน n8n

เปิดใช้งาน n8n จากเทอร์มินัล:

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

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

podman rm -f n8n >/dev/null 2>&1 || true
podman compose -f compose.yml up -d

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
  podman ps -a || true
  podman logs n8n 2>&1 | tail -30 || true
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
กด `'o'` หรือเปิดเบราว์เซอร์ไปที่ `http://localhost:5678` เพื่อเข้าถึงโปรแกรมแก้ไข n8n จะเริ่มต้นเว็บเซิร์ฟเวอร์ภายในเครื่อง
<!-- @os:end -->
> **เคล็ดลับ**: เปิดหน้าต่างเทอร์มินัลค้างไว้ในขณะที่ใช้งาน n8n การปิดหน้าต่างอาจทำให้เซิร์ฟเวอร์หยุดทำงาน

## การเปิดใช้งาน Lemonade

Lemonade คือเซิร์ฟเวอร์ภายในเครื่องที่จะรันโมเดลและเชื่อมต่อกับ n8n
<!-- @os:linux -->
คลิกไอคอน Lemonade ในแถบงานเพื่อเปิด Lemonade GUI คุณสามารถเรียกดูโมเดล แบ็กเอนด์ และโหลดโมเดลที่ติดตั้งไว้ล่วงหน้าได้จากที่นี่
<!-- @os:end -->

<!-- @os:windows -->
เปิด Lemonade GUI โดยคลิกที่ไอคอน Lemonade คลิกขวาที่ไอคอนในถาดระบบ (tray icon) เพื่อเปิดแอป จากนั้นคุณสามารถเพิ่มโมเดล แบ็กเอนด์ (backends) และโหลดโมเดลที่ติดตั้งไว้ล่วงหน้าได้
<!-- @os:end -->
**คำแนะนำ**: เมื่อทำงานแล้ว คุณยังสามารถเข้าถึง Lemonade GUI ได้ที่ http://localhost:13305

หรืออีกทางหนึ่ง คุณสามารถเปิดเทอร์มินัลแล้วรัน `lemonade list` เพื่อดูว่ามีโมเดลใดติดตั้งอยู่บ้าง จากนั้นให้รัน:
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

เมื่อคุณเปิด n8n เป็นครั้งแรก ระบบจะแจ้งให้คุณสร้างบัญชีหรือเข้าสู่ระบบ:

1. เปิด `http://localhost:5678` ในเบราว์เซอร์ของคุณ
2. สร้างบัญชีท้องถิ่นใหม่ด้วยอีเมลของคุณ หรือเข้าสู่ระบบหากคุณมีบัญชีอยู่แล้ว
3. เมื่อเข้าสู่ระบบแล้ว คุณจะเห็นแดชบอร์ดของ n8n

> **เคล็ดลับ**: หากถูกล็อกไม่ให้เข้าถึงบัญชีของคุณ ให้ลอง `n8n user-management:reset`

### ขั้นตอนที่ 2: นำเข้าเวิร์กโฟลว์

เราได้จัดเตรียมเวิร์กโฟลว์ที่สร้างไว้ล่วงหน้าให้คุณสามารถนำเข้าได้โดยตรง:

1. ดาวน์โหลดไฟล์เวิร์กโฟลว์ต่อไปนี้: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. คลิก **Start from Scratch** เพื่อเปิดตัวแก้ไขเวิร์กโฟลว์ หรือสามารถคลิกปุ่ม + ที่มุมบนซ้าย แล้วเลือก **Add workflow**
3. คลิกเมนู **...** (จุดสามจุด) ที่แถบด้านบนขวา แล้วเลือก **Import from file**
4. เลือกไฟล์ `financial-news-workflow.json` ที่ดาวน์โหลดมา
5. เวิร์กโฟลว์จะปรากฏบนผืนผ้าใบ (canvas)
### ขั้นตอนที่ 3: ทำความเข้าใจเวิร์กโฟลว์

เวิร์กโฟลว์ที่นำเข้ามานั้นประกอบด้วยโหนดที่เชื่อมต่อกัน 8 โหนด:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| โหนด | วัตถุประสงค์ |
|------|---------|
| **When clicking 'Execute workflow'** | ตัวทริกเกอร์แบบแมนนวลเพื่อเริ่มต้นเวิร์กโฟลว์ |
| **Fetch Financial News Feed** | โหนด RSS Read ที่ดึงพาดหัวข่าวธุรกิจล่าสุดจากฟีด RSS (ค่าเริ่มต้นคือฟีด NYT Business ไม่ต้องใช้ API key) |
| **Aggregate Headlines** | โหนด Aggregate ที่รวบรวมชื่อเรื่องและบทสรุปของพาดหัวข่าวจากทุกรายการในฟีดให้เป็นรายการเดียว |
| **Clean Extracted News Data** | โหนด Set ที่รวมพาดหัวข่าวทั้งหมดไว้ในฟิลด์ข้อความเดียว |
| **AI Financial News Summarizer** | AI Agent ที่ประมวลผลข่าวโดยใช้ system prompt สำหรับนักวิเคราะห์การเงิน |
| **Lemonade Chat Model** | เชื่อมต่อกับเซิร์ฟเวอร์ Lemonade ในเครื่องที่กำลังรัน LLM |
| **Structured Output Parser** | จัดรูปแบบผลลัพธ์จาก AI ให้เป็น JSON ที่มีโครงสร้าง |
| **Convert to File** | แปลงบทสรุปให้เป็นไฟล์ที่สามารถดาวน์โหลดได้ |

> **เคล็ดลับ**: หากต้องการใช้แหล่งข่าวอื่น ให้ดับเบิลคลิกที่โหนด **Fetch Financial News Feed** แล้วแทนที่ URL ด้วยฟีด RSS ของข่าวธุรกิจหรือตลาดการเงินที่คุณต้องการ

### ขั้นตอนที่ 4: กำหนดค่าข้อมูลรับรอง Lemonade

ก่อนรันเวิร์กโฟลว์ คุณจำเป็นต้องเชื่อมต่อกับเซิร์ฟเวอร์ Lemonade ในเครื่องของคุณ:

1. ดับเบิลคลิกที่โหนด **Lemonade Chat Model** ใน n8n
2. ในเมนูแบบดรอปดาวน์ **Credential to connect with** ให้เลือก **Create New Credential**
3. กรอกค่าตามตารางด้านล่างแล้วคลิกบันทึก
4. เลือกโมเดลที่เกี่ยวข้องซึ่งคุณได้โหลดไว้ใน Lemonade Server

  | ฟิลด์ | ค่า |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **หมายเหตุ**: ก่อนทดสอบ ให้รันคำสั่ง `lemonade status` ในเทอร์มินัลเพื่อยืนยันว่าเซิร์ฟเวอร์ Lemonade กำลังทำงานอยู่
<!-- @device:halo_box -->
> เวิร์กโฟลว์นี้ใช้ GPT-OSS-120B ซึ่งติดตั้งไว้ล่วงหน้าใน Lemonade แล้ว คุณสามารถเปลี่ยนไปใช้โมเดลอื่นที่โหลดไว้ได้ในการตั้งค่าโหนด Lemonade Chat Model
<!-- @device:end -->

### ขั้นตอนที่ 5: ทดสอบเวิร์กโฟลว์

1. ตรวจสอบให้แน่ใจว่า Lemonade กำลังทำงานอยู่พร้อมกับโหลดโมเดลไว้แล้ว
2. คลิก **Execute workflow** ที่ตรงกลางด้านล่างของแคนวาส
3. สังเกตการทำงานของแต่ละโหนดจากซ้ายไปขวา—โหนดจะเปลี่ยนเป็นสีเขียวเมื่อทำงานเสร็จสมบูรณ์
4. ดับเบิลคลิกที่โหนด **AI Financial News Summarizer** เพื่อดูบทสรุปที่สร้างขึ้นในแผงด้านล่าง
5. ดับเบิลคลิกที่โหนด **Convert to File** เพื่อดาวน์โหลดไฟล์ข้อความที่เกี่ยวข้องในแผงด้านล่าง

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

เอเจนต์จะรับข้อมูลข่าวที่ผ่านการล้างแล้ว และส่งออกบทสรุปที่มีโครงสร้างพร้อมทัศนคติของตลาด

### การบันทึกเวิร์กโฟลว์ของคุณ

คลิกที่ชื่อเวิร์กโฟลว์ด้านบนแล้วเปลี่ยนชื่อได้ตามต้องการ เวิร์กโฟลว์จะบันทึกอัตโนมัติขณะที่คุณทำงาน

## ขั้นตอนถัดไป

- **กำหนดเวลาระบบอัตโนมัติ**: แทนที่ Manual Trigger ด้วย **Schedule Trigger** เพื่อรันทุกวัน
- **ส่งการแจ้งเตือน**: เพิ่มโหนด **Discord**, **Slack**, หรือ **Email** เพื่อรับบทสรุป
- **ลองใช้โมเดลอื่น**: เปลี่ยนโมเดลในโหนด Lemonade Chat Model เพื่อทดลองใช้ LLM ที่แตกต่างกัน
- **เปลี่ยนแหล่งข่าว**: ชี้โหนด **Fetch Financial News Feed** ไปยังฟีด RSS อื่นเพื่อติดตามหมวดหมู่หรือสำนักพิมพ์อื่น ๆ
- **ลองใช้แบ็กเอนด์อื่น**: n8n ยังรองรับ [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio และแบ็กเอนด์ LLM ในเครื่องอื่น ๆ

### สำรวจเทมเพลตของ n8n

n8n มีเทมเพลตเวิร์กโฟลว์สำเร็จรูปหลายร้อยแบบ เรียกดูไลบรารีเทมเพลตอย่างเป็นทางการได้ที่:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

ค้นหาคำว่า "AI", "LLM" หรือ "automation" เพื่อค้นหาเวิร์กโฟลว์ที่คุณสามารถนำเข้าและปรับแต่งได้

สำหรับข้อมูลเพิ่มเติม โปรดดูที่ [n8n Documentation](https://docs.n8n.io/)

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