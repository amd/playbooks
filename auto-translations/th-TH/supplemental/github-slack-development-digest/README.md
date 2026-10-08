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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## ภาพรวม

นักพัฒนาใช้เวลาจำนวนมากไปกับงานที่เกิดซ้ำเล็กๆ น้อยๆ เช่น การรีวิว pull request ที่ถูกติดป้าย การตอบความคิดเห็นใน GitHub การจัดลำดับความสำคัญของ issue ใหม่ การแปลงเธรด Slack ให้เป็นบันทึก standup หรือการติดตามผลหลังเกิดเหตุขัดข้อง (incident) และการติดตามสัญญาณของการออกเวอร์ชันหรือการวิจัย
แต่ละงานล้วนคุ้นเคยดี แต่ก็ยังต้องอาศัยการตัดสินใจ: รวบรวมบริบทที่ถูกต้อง ตัดสินใจว่าอะไรสำคัญ และโพสต์อัปเดตที่ชัดเจนไปยังที่ที่ทีมทำงานอยู่แล้ว

[OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview) เปลี่ยนงานเหล่านั้นให้เป็นบทสนทนาของเอเจนต์ที่ทำงานตามกำหนดเวลาหรือถูกกระตุ้นโดยเหตุการณ์: การรันที่ตัวแทนซอฟต์แวร์ AI สามารถอ่านบริบท เรียกใช้เครื่องมือ และสร้างอัปเดตได้
เทมเพลตการทำงานอัตโนมัติที่แชร์ร่วมกันในแคตตาล็อกส่วนขยายของ OpenHands ปฏิบัติตามรูปแบบนี้สำหรับการรีวิว pull request ของ GitHub การตรวจสอบ repository การจัดลำดับความสำคัญของ issue ใน Linear การวิเคราะห์ย้อนหลังหลังเกิดเหตุขัดข้อง สรุปข่าว standup ใน Slack และสรุปงานวิจัย: การทำงานอัตโนมัติตื่นขึ้นมา ใช้การเชื่อมต่อที่กำหนดค่าไว้ เช่น GitHub หรือ Slack เพื่อดึงบริบท ใช้เหตุผลกับบริบทนั้นด้วยโมเดลภาษาขนาดใหญ่ (LLM) และเขียนผลลัพธ์กลับไป

[Agent Canvas](https://github.com/OpenHands/agent-canvas) คือ control plane ในเครื่องสำหรับสร้างและทดสอบการทำงานอัตโนมัติเหล่านั้น
ในคู่มือนี้ มันรัน OpenHands Agent Server ซึ่งเป็นกระบวนการแบ็กเอนด์ที่ประมวลผลบทสนทนาของเอเจนต์ และเชื่อมต่อเอเจนต์เข้ากับบริการภายนอก เช่น GitHub และ Slack

เพื่อให้เวิร์กโฟลว์ยังคงอยู่บนระบบ AMD ของคุณ เอเจนต์จะสื่อสารกับโมเดลในเครื่องที่ให้บริการโดย Lemonade Server
Lemonade เปิดเผยโมเดลนั้นผ่าน API ที่เข้ากันได้กับ OpenAI ดังนั้น Agent Canvas จึงสามารถกำหนดค่ามันเหมือนกับ endpoint สไตล์ OpenAI ระยะไกล ในขณะที่โมเดล พรอมต์ และบริบทของเวิร์กโฟลว์ยังคงอยู่ในเครื่อง

ในคู่มือนี้ คุณจะสร้างการทำงานอัตโนมัติที่เป็นรูปธรรมหนึ่งอย่าง: สรุปการพัฒนาแบบ GitHub-ไปยัง-Slack ตามกำหนดเวลา
มันใช้ GitHub เพื่อตรวจสอบกิจกรรม repository ล่าสุด ใช้ Slack เพื่อโพสต์สรุป ใช้การเรียก API ของ Agent Canvas เพื่อกำหนดค่าและทดสอบการทำงานอัตโนมัติ และใช้ Lemonade เพื่อรัน LLM ในเครื่อง

![แผนภาพสถาปัตยกรรมแสดง GitHub MCP, การทำงานอัตโนมัติ OpenHands, Lemonade Server และ Slack MCP](assets/00-architecture-overview.png)

## สิ่งที่คุณจะได้เรียนรู้

- วิธีเริ่มต้น Lemonade Server และยืนยันว่าโมเดลในเครื่องตอบสนองต่อคำขอแชทได้
- วิธีเปิดใช้งาน Agent Canvas และชี้ Agent Server ไปยัง LLM ในเครื่อง
- วิธีติดตั้งเซิร์ฟเวอร์ Model Context Protocol (MCP) ของ GitHub และ Slack ผ่าน API ของ Agent Server
- วิธีสร้างและส่งการทำงานอัตโนมัติ OpenHands ตามกำหนดเวลาที่โพสต์สรุปการพัฒนาไปยัง Slack
- วิธีแก้ไขปัญหาความล้มเหลวที่พบบ่อยที่สุดของโมเดลในเครื่องและการทำงานอัตโนมัติ

## แนวคิดหลัก

| แนวคิด | คืออะไร | เกี่ยวข้องกับคู่มือนี้อย่างไร |
| --- | --- | --- |
| Lemonade Server | แพลตฟอร์มให้บริการ LLM ในเครื่องที่สร้างขึ้นสำหรับฮาร์ดแวร์ AMD ซึ่งเปิดเผย API ที่เข้ากันได้กับ OpenAI ข้อมูลของคุณจะไม่ออกจากเครื่องของคุณเลย | รันโมเดลที่ขับเคลื่อนเอเจนต์ |
| OpenHands Agent Server | กระบวนการแบ็กเอนด์ที่ประมวลผลบทสนทนาของเอเจนต์ OpenHands | โฮสต์เอเจนต์ โปรไฟล์ LLM ของมัน และเซิร์ฟเวอร์ MCP ของมัน |
| Agent Canvas | control plane ในเครื่องสำหรับ OpenHands ที่รัน Agent Server และ UI สำหรับตรวจสอบการรันของเอเจนต์ | เปิดใช้งานแบ็กเอนด์และให้ API ที่คุณเรียกใช้ |
| เซิร์ฟเวอร์ MCP | เซิร์ฟเวอร์ Model Context Protocol ที่ให้เครื่องมือแก่เอเจนต์สำหรับบริการภายนอก เช่น GitHub หรือ Slack | ให้เอเจนต์อ่าน GitHub และเขียนไปยัง Slack ได้ |
| การทำงานอัตโนมัติของ OpenHands | บทสนทนาของเอเจนต์ที่ทำงานตามกำหนดเวลาหรือถูกกระตุ้นโดยเหตุการณ์ ซึ่งดึงบริบท ใช้เหตุผลกับมัน และเขียนผลลัพธ์ไปยังที่ใดที่หนึ่ง | สรุป GitHub-ไปยัง-Slack ที่คุณสร้างขึ้นที่นี่ |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> เวิร์กโฟลว์เอเจนต์สำหรับการเขียนโค้ดได้ประโยชน์จากโมเดลและหน้าต่างบริบทที่ใหญ่กว่า
> ใช้หน่วยความจำระบบอย่างน้อย 32 GB และควรใช้ 64 GB หรือมากกว่าสำหรับโมเดล GGUF ขนาดใหญ่กว่า
<!-- @device:end -->

## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## ข้อกำหนดเบื้องต้น

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

คุณต้องมี:

- Lemonade Server ที่ติดตั้งตาม [คู่มือการติดตั้ง Lemonade](https://lemonade-server.ai/docs/guide/install/) แบบมาตรฐาน

<!-- @os:linux -->
- Node.js 22.12 หรือใหม่กว่า และ `npm` ใช้สำหรับติดตั้ง Agent Canvas CLI ที่เผยแพร่แล้วและรันเซิร์ฟเวอร์ MCP ด้วย `npx`
- `uv` ตัวจัดการแพ็กเกจ Python ที่ Agent Canvas ใช้ในการสร้างสภาพแวดล้อม Agent Server หากยังไม่ได้ติดตั้ง ให้ติดตั้งจาก [คู่มือการติดตั้ง uv](https://docs.astral.sh/uv/getting-started/installation/)
- แพ็กเกจ `@openhands/agent-canvas` เวอร์ชันล่าสุดที่เผยแพร่แล้ว ซึ่งมีการตั้งค่าเอเจนต์ที่ขับเคลื่อนด้วยสคีมา รองรับ `LLMSummarizingCondenserSettings.max_tokens` และการรองรับ `custom_tokenizer` ของ LLM
- แพ็กเกจ `transformers` ของ Python ที่พร้อมใช้งานในสภาพแวดล้อม Agent Server ซึ่งจำเป็นสำหรับการนับโทเค็นแบบ chat-template เมื่อตั้งค่า `custom_tokenizer`
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) ที่ติดตั้งและกำลังทำงานอยู่ บน Windows สแต็ก Agent Canvas จะรันจาก Docker image ที่เผยแพร่แล้ว ซึ่งรวม Node.js, `uv`, `transformers` และแพ็กเกจ `@openhands/agent-canvas` ไว้ด้วยกัน คุณจึงไม่ต้องติดตั้งสิ่งเหล่านั้นบนโฮสต์
<!-- @os:end -->

- โทเค็น GitHub ที่มีสิทธิ์อ่าน repository ที่คุณต้องการสรุป
- โทเค็นบอต Slack (`xoxb-...`) ที่มีสิทธิ์ `chat:write` และสิทธิ์อ่านช่อง
- Slack team ID (`T...`)
- Slack channel ID (`C...`) ที่ต้องการให้โพสต์สรุป

เชิญแอป Slack เข้าสู่ช่องเป้าหมายก่อนทดสอบการทำงานอัตโนมัติ
## ตัวแปรที่ใช้ในเพลย์บุ๊กนี้

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

ตัวแปรทั้งสองนี้ใช้สำหรับคำสั่งตรวจสอบด้านล่าง
ส่วนโมเดล โทเค็นไนเซอร์ และการตั้งค่า LLM อื่น ๆ จะถูกกรอกโดยตรงใน Agent Canvas UI ในขั้นตอนถัดไป ดังนั้นค่าจริงของตัวแปรเหล่านี้จึงแสดงแบบอินไลน์ในจุดที่คุณต้องใช้

ค่าต่อไปนี้จะถูกกรอกลงใน Agent Canvas UI ในขั้นตอนถัดไป
กำหนดค่าไว้ที่นี่เพื่อให้คุณสามารถคัดลอกไปใช้ได้:

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

ใช้ค่า `owner/repo` ที่ชัดเจนสำหรับ `GITHUB_REPO_FILTER`
การใช้ไวลด์การ์ดขององค์กรแบบกว้าง ๆ อาจทำให้ได้ MCP context มากเกินไปสำหรับโมเดลที่รันในเครื่อง

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. เริ่มต้น Lemonade Server

เริ่มต้นโมเดลจาก Lemonade CLI:

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

> **เลือกโมเดลที่เหมาะกับฮาร์ดแวร์ของคุณ** `Qwen3.6-35B-A3B-GGUF` (~20 GB) เป็นโมเดลที่ดีสำหรับเวิร์กโฟลว์นี้ แต่ต้องการพื้นที่หน่วยความจำขนาดใหญ่
> หากอุปกรณ์ของคุณมีหน่วยความจำหรือ GPU VRAM จำกัด ให้เลือกโมเดล GGUF ที่มีขนาดเล็กลงจากคลังโมเดลของ Lemonade และใช้รหัสโมเดลนั้น (พร้อมโทเค็นไนเซอร์ที่ตรงกัน) ตลอดทั้งเพลย์บุ๊กนี้

> **หมายเหตุ:** การรัน `lemonade run` ครั้งแรกจะดาวน์โหลดโมเดลหากยังไม่มีอยู่ในเครื่อง ซึ่งอาจใช้เวลาสักพักขึ้นอยู่กับขนาดโมเดลและความเร็วการเชื่อมต่อของคุณ

Lemonade เปิดให้ใช้งาน API ที่เข้ากันได้กับ OpenAI ที่:

```text
http://127.0.0.1:13305/api/v1
```

ทางเลือกเสริม: หาก Agent Canvas หรือตัวรันระบบอัตโนมัติไม่ได้อยู่บนเครื่องเดียวกัน ให้เผยแพร่เอนด์พอยต์ของ Lemonade ผ่านทันเนลที่ปลอดภัย แล้วใช้ URL แบบ HTTPS เป็น LLM base URL
[ngrok](https://ngrok.com/) เปิดให้พอร์ตในเครื่องเข้าถึงได้จากอินเทอร์เน็ตผ่าน URL แบบ HTTPS ที่ปลอดภัย โดยต้องมีบัญชี ngrok แบบฟรี และคุณต้องแทนที่ `YOUR_NGROK_DOMAIN.ngrok-free.dev` ด้วยโดเมนที่คุณจองไว้เอง:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. ตรวจสอบโมเดลในเครื่อง

ยืนยันว่า Lemonade สามารถให้บริการโมเดลที่เลือกได้:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

จากนั้นส่งคำขอแชทเล็ก ๆ:

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

จากนั้นส่งคำขอแชทเล็ก ๆ:

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

หากได้ผลลัพธ์เป็นอาร์เรย์ `choices` แสดงว่า Lemonade พร้อมใช้งานสำหรับ Agent Canvas แล้ว

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

## 3. เริ่มต้น Agent Canvas

<!-- @os:linux -->
ติดตั้งแพ็กเกจ Agent Canvas ที่เผยแพร่แล้ว และเริ่มต้นสแตกทั้งหมด:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

หากการติดตั้ง npm แบบ global ล้มเหลวเนื่องจากข้อผิดพลาดเรื่องสิทธิ์การเข้าถึง โปรดดูรายการแก้ปัญหาสิทธิ์การเข้าถึง npm ด้านล่าง

โดยค่าเริ่มต้น Agent Canvas จะเริ่มทำงานที่ `http://localhost:8000`
เปิด URL นั้นในเบราว์เซอร์ของคุณ
หมายเลขพอร์ตนี้ไม่ได้มีความพิเศษ—หาก 8000 ถูกใช้งานอยู่แล้ว ให้ระบุพอร์ตว่างใด ๆ ด้วย `--port` (หรือ `-p`)
แบ็กเอนด์ในเครื่องเริ่มต้นควรแสดงสถานะว่าทำงานปกติ (healthy) บนหน้าจอหลัก

> **หมายเหตุ:** การเปิดใช้งานครั้งแรกจะสร้างสภาพแวดล้อม Python ที่จัดการด้วย `uv` ของ Agent Server ดังนั้นอาจใช้เวลาสักครู่ก่อนที่แบ็กเอนด์จะรายงานว่าทำงานปกติ

คำสั่ง `agent-canvas` จะเริ่มต้น agent server, แบ็กเอนด์ระบบอัตโนมัติ และเว็บฟรอนต์เอนด์ไปพร้อมกัน
คุณต้องใช้เพียงคำสั่งเดียวนี้เพื่อรัน OpenHands ในเครื่องของคุณ
ส่วนที่เหลือของเพลย์บุ๊กนี้จะกำหนดค่าทุกอย่างผ่าน Agent Canvas UI ในเบราว์เซอร์ของคุณ
<!-- @os:end -->

<!-- @os:windows -->
บน Windows ให้รันอิมเมจคอนเทนเนอร์ Agent Canvas ที่เผยแพร่แล้วด้วย Docker Desktop
อิมเมจนี้รวม Agent Server, แบ็กเอนด์ระบบอัตโนมัติ และเว็บฟรอนต์เอนด์ไว้ด้วยกัน ดังนั้นคุณไม่จำเป็นต้องติดตั้ง Node.js, `uv`, หรือ CLI บนเครื่องโฮสต์

ก่อนอื่น สร้างโฟลเดอร์ config และ workspace ที่คอนเทนเนอร์จะเมาท์:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

ดึงอิมเมจที่เผยแพร่แล้ว (ขนาดประมาณ 6 GB; เป็นอิมเมจสาธารณะ จึงไม่ต้องล็อกอิน):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

จากนั้นเริ่มต้นสแตก:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

เปิด `http://localhost:8000/canvas` ในเบราว์เซอร์ของคุณ
หากพอร์ต 8000 ถูกใช้งานอยู่แล้ว ให้แมปไปยังพอร์ตโฮสต์อื่น เช่น `-p 8080:8000` แล้วเปิด `http://localhost:8080/canvas` แทน

> **หมายเหตุ:** การเปิดใช้งานครั้งแรกจะสร้างสภาพแวดล้อม Agent Server ภายในคอนเทนเนอร์ ดังนั้นอาจใช้เวลาสักครู่ก่อนที่แบ็กเอนด์จะรายงานว่าทำงานปกติ

การเมาท์ `.openhands` จะเก็บรักษาโปรไฟล์ LLM, MCP servers และระบบอัตโนมัติของคุณไว้แม้จะรีสตาร์ทคอนเทนเนอร์
ส่วนที่เหลือของเพลย์บุ๊กนี้จะกำหนดค่าทุกอย่างผ่าน Agent Canvas UI ในเบราว์เซอร์ของคุณที่ `http://localhost:8000/canvas`
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
## 4. กำหนดค่า LLM แบบโลคัลในหน้า UI

เมื่อเปิดใช้งานครั้งแรก Agent Canvas จะเปิดขั้นตอนการปฐมนิเทศ (onboarding flow)
ในขั้นตอนนั้น:

1. คงให้ **OpenHands** ถูกเลือกไว้เป็นเอเจนต์ และคลิก **Next**
2. ใน **Set up your LLM** ให้เลือก **Advanced**
3. คงค่า **Authentication** ไว้เป็น **API key**
4. ตั้งค่า **Custom Model** เป็น `openai/Qwen3.6-35B-A3B-GGUF`
5. ตั้งค่า **Base URL** เป็น `http://127.0.0.1:13305/api/v1`
6. สำหรับ **API Key** ให้ป้อนค่าตัวยึดตำแหน่ง (placeholder) ที่ไม่ว่างเปล่าใดก็ได้ เช่น `lemonade-local` Lemonade ไม่จำเป็นต้องใช้คีย์จริง แต่ไคลเอนต์ OpenHands จำเป็นต้องมีค่าเพื่อส่งไป

<!-- @os:windows -->
> **Windows (Docker):** Agent Server ทำงานอยู่ภายในคอนเทนเนอร์ ดังนั้นให้ตั้งค่า **Base URL** เป็น `http://host.docker.internal:13305/api/v1` แทน `http://127.0.0.1:13305/api/v1`
> จากภายในคอนเทนเนอร์ `127.0.0.1` คือตัวคอนเทนเนอร์เอง ส่วน `host.docker.internal` เข้าถึง Lemonade ที่ทำงานอยู่บนโฮสต์ Windows และ Docker Desktop จะให้ชื่อโฮสต์นั้นโดยอัตโนมัติ
<!-- @os:end -->

ช่องการเชื่อมต่อควรมีลักษณะดังนี้
ช่อง API key จะถูกปิดบังโดย UI

![การตั้งค่าขั้นสูงของ LLM เมื่อใช้งาน Agent Canvas ครั้งแรก พร้อมโมเดล Lemonade และ base URL แบบโลคัล](assets/01-llm-advanced-settings.png)

จากนั้นเลือก **All** และตั้งค่าช่องเพิ่มเติมสำหรับโมเดลแบบโลคัล:

1. เลื่อนไปที่ **Custom Tokenizer** และตั้งค่าเป็น `Qwen/Qwen3.6-35B-A3B`
2. เลื่อนไปที่ **LiteLLM Extra Body** และตั้งค่าเป็น `{"enable_thinking": true}`
3. คลิก **Next**

![แท็บ All ของ LLM เมื่อใช้งาน Agent Canvas ครั้งแรก พร้อม custom tokenizer ของ Qwen](assets/02-llm-all-tokenizer-settings.png)

![แท็บ All ของ LLM เมื่อใช้งาน Agent Canvas ครั้งแรก พร้อมการกำหนดค่า LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

การตั้งค่า LLM ควรแสดงดังนี้:

| Field | Value |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

คำนำหน้า `openai/` บอกให้ LiteLLM ใช้รูปแบบคำขอที่เข้ากันได้กับ OpenAI กับปลายทาง Lemonade
custom tokenizer คือ tokenizer ดั้งเดิมจาก Hugging Face สำหรับโมเดล GGUF ซึ่งช่วยให้ OpenHands นับโทเคนของ chat-template แบบเดียวกับที่เซิร์ฟเวอร์โมเดลโลคัลเห็น
แบบฟอร์ม LLM สำหรับการใช้งานครั้งแรกในปัจจุบันยังไม่แสดงการตั้งค่า condenser
หาก Agent Canvas build ของคุณเปิดให้ตั้งค่า condenser ในภายหลังภายใต้ **Settings > LLM** ให้ใช้ `llm_summarizing` และตั้งค่า max tokens ให้ต่ำกว่าขนาดหน้าต่างบริบท (context window) ของ Lemonade เช่น `56000`

## 5. ติดตั้งเซิร์ฟเวอร์ GitHub และ Slack MCP

ในหน้า UI ของ Agent Canvas ให้เปิด **Customize** (หรือ **Settings > MCP**) เพื่อเพิ่มเซิร์ฟเวอร์ MCP ที่ให้เครื่องมือแก่เอเจนต์สำหรับ GitHub และ Slack
ค่าโทเคนจะถูกส่งไปยัง Agent Server ในเครื่องของคุณเท่านั้น และจะถูกบันทึกเป็นการตั้งค่าที่เข้ารหัส

<!-- @os:windows -->
> **Windows (Docker):** คำสั่งเซิร์ฟเวอร์ MCP ของ `npx` ด้านล่างนี้ทำงานอยู่ภายในคอนเทนเนอร์ ซึ่งมี Node.js อยู่แล้ว ดังนั้นจึงไม่มีการติดตั้งสิ่งใดเพิ่มเติมบนโฮสต์
> เนื่องจาก `.openhands` ถูกเมาท์ไว้ เซิร์ฟเวอร์ MCP และโทเคนของมันจะยังคงอยู่แม้คอนเทนเนอร์จะรีสตาร์ท
<!-- @os:end -->

### เซิร์ฟเวอร์ GitHub MCP

เพิ่มเซิร์ฟเวอร์ MCP ใหม่โดยใช้การตั้งค่าดังนี้:

| Field | Value |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = โทเคน GitHub ของคุณ |

ใช้โทเคน GitHub ที่มีสิทธิ์อ่าน (read access) สำหรับรีโพซิทอรีที่คุณต้องการสรุป

### เซิร์ฟเวอร์ Slack MCP

เพิ่มเซิร์ฟเวอร์ MCP ตัวที่สองโดยใช้การตั้งค่าดังนี้:

| Field | Value |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ไอดีของช่องสรุปของคุณ |

ตั้งค่า `SLACK_CHANNEL_IDS` เป็นไอดีของช่องสรุป (ค่าเดียวกับ `SLACK_DIGEST_CHANNEL`) เพื่อให้เอเจนต์ไม่ต้องไล่ดูทุกช่อง Slack

หลังจากเพิ่มเซิร์ฟเวอร์ทั้งสองแล้ว ให้ใช้ปุ่ม **Test** บนแต่ละเซิร์ฟเวอร์เพื่อยืนยันว่าสามารถเชื่อมต่อและประกาศเครื่องมือได้
เซิร์ฟเวอร์ GitHub ควรแสดงรายการเครื่องมือของ GitHub และเซิร์ฟเวอร์ Slack ควรแสดงรายการเครื่องมือของ Slack

![หน้า MCP ของ Agent Canvas ที่ติดตั้งเซิร์ฟเวอร์ GitHub และ Slack แล้ว](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. สร้างระบบอัตโนมัติสำหรับสรุปข้อมูล (Digest Automation)

ในหน้า UI ของ Agent Canvas ให้เปิดหน้า **Automations** และสร้างระบบอัตโนมัติใหม่:

1. เลือก **Create automation** และเลือกประเภท **Prompt preset**
2. ตั้งค่า **Name** เป็น `GitHub Development Digest to Slack`
3. ตั้งค่า **Prompt** เป็นข้อความต่อไปนี้ โดยแทนที่ตัวยึดตำแหน่งของรีโพซิทอรีและช่องด้วยค่าของคุณเอง:

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

4. ตั้งค่า **Trigger** เป็น **Cron** โดยใช้กำหนดการ `0 9 * * 1-5` (9 โมงเช้าของวันธรรมดา) และตั้งค่า **Timezone** เป็นเขตเวลาของคุณ เช่น `America/New_York`
5. ตั้งค่า **Timeout** เป็น `900` วินาที
6. บันทึกระบบอัตโนมัติ

หน้ารายละเอียดของระบบอัตโนมัติจะแสดงระบบอัตโนมัติใหม่พร้อมตัวกระตุ้น cron และจุดเริ่มต้นของ prompt-preset ที่สร้างขึ้น

![หน้ารายละเอียดระบบอัตโนมัติของ Agent Canvas หลังจากสร้างแล้ว](assets/05-automation-created.png)
## 7. ทดสอบการทำงานอัตโนมัติ

จากหน้ารายละเอียดของการทำงานอัตโนมัติใน Agent Canvas UI:

1. คลิก **Run now** (หรือ **Dispatch**) เพื่อรันการทำงานอัตโนมัติทันทีหนึ่งครั้ง
2. สังเกตรายการรันในหน้าเดียวกัน การรันล่าสุดควรเปลี่ยนสถานะเป็น `COMPLETED`
3. เปิดช่อง Slack เป้าหมายของคุณ ควรมีข้อมูลสรุปที่สร้างขึ้นปรากฏอยู่

คุณไม่จำเป็นต้องรอให้กำหนดการ cron ทำงาน—**Run now** จะเรียกใช้การรันตามความต้องการ เพื่อให้คุณสามารถยืนยันได้ว่า prompt การเชื่อมต่อ MCP และการโพสต์ไปยัง Slack ทำงานถูกต้องทั้งหมดก่อนที่จะพึ่งพากำหนดการ

![การรันการทำงานอัตโนมัติใน Agent Canvas เสร็จสมบูรณ์](assets/06-automation-run-completed.png)

![ช่อง Slack ที่แสดงข้อมูลสรุป OpenHands ที่สร้างขึ้น](assets/07-slackbot-message.png)

## การแก้ไขปัญหา

<!-- @os:windows -->
- **พอร์ต Docker 8000 ถูกใช้งานอยู่แล้ว:** กำหนดพอร์ตโฮสต์อื่นแทน เช่น `docker run ... -p 8080:8000 ...` แล้วเปิด `http://localhost:8080/canvas`
- **`docker pull` ล้มเหลวด้วยข้อผิดพลาดเกี่ยวกับข้อมูลรับรอง** (ตัวอย่างเช่น "A specified logon session does not exist"): รันคำสั่ง pull จาก Windows session แบบโต้ตอบ หรือทำการ pre-pull อิมเมจไว้ล่วงหน้า อิมเมจนี้เป็นสาธารณะ จึงไม่จำเป็นต้องใช้ `docker login`
- **UI โหลดได้แต่ backend ไม่พร้อมใช้งาน:** การเปิดใช้งานครั้งแรกจะสร้างสภาพแวดล้อม Agent Server ภายในคอนเทนเนอร์ รอสักครู่แล้วรีเฟรช จากนั้นตรวจสอบความคืบหน้าได้ที่ `docker logs <container>`
- **Agent Canvas ไม่สามารถเชื่อมต่อกับ Lemonade จากคอนเทนเนอร์ได้:** ตั้งค่า LLM **Base URL** เป็น `http://host.docker.internal:13305/api/v1` (ไม่ใช่ `127.0.0.1`) และยืนยันว่า Lemonade กำลังทำงานอยู่บนโฮสต์ Windows
<!-- @os:end -->

- **Lemonade หยุดทำงาน:** รีสตาร์ทด้วยคำสั่ง `lemonade run "${LEMONADE_MODEL}"` ในขั้นตอนที่ 1 จากนั้นรันการตรวจสอบสถานะอีกครั้ง
- **`npm install -g` ล้มเหลวด้วยข้อผิดพลาดเกี่ยวกับสิทธิ์การเข้าถึง:** บน Linux หรือ WSL ให้กำหนดค่าไดเรกทอรี npm แบบ global ที่เป็นของผู้ใช้เอง เพิ่มเข้าไปในไฟล์เริ่มต้นของเชลล์ จากนั้นติดตั้ง Agent Canvas อีกครั้ง:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

หากคุณใช้ `zsh` ให้เพิ่มบรรทัด `export PATH=...` เดียวกันลงใน `~/.zshrc` แทนที่จะเป็น `~/.bashrc`
- **Agent Canvas ปฏิเสธการตั้งค่า LLM หลังจากตั้งค่า `custom_tokenizer`:** ติดตั้ง `transformers` ในสภาพแวดล้อม Python ของ Agent Server รีสตาร์ท Agent Canvas หากจำเป็น แล้วลองบันทึกการตั้งค่า LLM อีกครั้ง OpenHands ต้องใช้ Transformers เพื่อโหลด tokenizer chat template เมื่อมีการตั้งค่า `custom_tokenizer`
- **Agent Canvas ไม่สามารถเชื่อมต่อกับ Lemonade ได้:** ตรวจสอบด้วย `curl -fsS "${LEMONADE_BASE_URL}/health"` และยืนยันว่า base URL ที่ป้อนในแบบฟอร์ม LLM ครั้งแรกหรือใน **Settings > LLM** ตรงกับ endpoint ภายในเครื่องหรือ HTTPS tunnel ที่กำลังทำงานอยู่
- **การตั้งค่า LLM ไม่ได้ถูกบันทึก:** ตรวจสอบให้แน่ใจว่าคุณคลิก **Next** หลังจากป้อนค่าต่าง ๆ แล้ว เปิด **Settings > LLM** อีกครั้งเพื่อยืนยันว่าค่าดังกล่าวถูกบันทึกไว้
- **GitHub MCP มองไม่เห็นรีพอสิทอรีส่วนตัว:** ยืนยันว่า GitHub token มีสิทธิ์อ่านรีพอสิทอรีเป้าหมาย และปุ่ม **Test** ของ MCP ใน **Customize** แสดงเครื่องมือของ GitHub
- **Slack อ่านช่องได้แต่โพสต์ไม่ได้:** เชิญแอป Slack เข้าสู่ช่องเป้าหมาย และยืนยันว่าบอทมีสิทธิ์ `chat:write`
- **การทำงานอัตโนมัติแสดงรายการช่อง Slack มากเกินไป:** ใช้รหัสช่อง Slack (channel ID) และตั้งค่า `SLACK_CHANNEL_IDS` บนเซิร์ฟเวอร์ Slack MCP ใน **Customize**
- **การรันการทำงานอัตโนมัติล้มเหลวหรือเกินขอบเขต context:** ยืนยันว่า Lemonade ถูกเริ่มต้นด้วย `ctx_size=65536` ยืนยันว่า LLM ของ OpenHands ได้ตั้งค่า `custom_tokenizer` แล้ว และใช้รีพอสิทอรีที่ระบุชัดเจนโดยจำกัดชุดผลลัพธ์ของ GitHub ไว้ที่ 3 ถึง 5 รายการ หากบิลด์ Agent Canvas ของคุณมีการตั้งค่า condenser ให้ตั้งค่า condenser max tokens ให้ต่ำกว่าหน้าต่าง context ของ Lemonade

## ขั้นตอนถัดไป

- เพิ่มข้อมูลสรุปรายสัปดาห์ที่เน้นเฉพาะการเผยแพร่เวอร์ชัน (release)
- เพิ่มการทำงานอัตโนมัติที่ทริกเกอร์ด้วยเหตุการณ์ของ GitHub เพื่อการแจ้งเตือน PR หรือ push ที่รวดเร็วยิ่งขึ้น
- ส่งข้อมูลสรุปเดียวกันนี้ไปยัง Notion, Linear หรือเครื่องมืออื่นที่รองรับ MCP

## แหล่งข้อมูลอ้างอิง

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [เอกสารประกอบ Lemonade Server](https://lemonade-server.ai/docs)
- [รีพอสิทอรีส่วนขยายของ OpenHands](https://github.com/OpenHands/extensions)
- [เซิร์ฟเวอร์ Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [แพ็กเกจ Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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