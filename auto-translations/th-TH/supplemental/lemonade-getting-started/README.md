<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

🍋 **Lemonade** คือเซิร์ฟเวอร์ AI ท้องถิ่นแบบโอเพนซอร์สที่ให้คุณรันโมเดลภาษาขนาดใหญ่ (LLMs) ตัวสร้างภาพ และโมเดลเสียงโดยตรงบนฮาร์ดแวร์ของคุณเอง โดยเปิดเผยโมเดลผ่าน **OpenAI API** มาตรฐานอุตสาหกรรม ดังนั้นแอปใดก็ตามที่ทำงานกับ OpenAI สามารถทำงานกับ Lemonade ได้ทันที เมื่อสิ้นสุด playbook นี้ คุณจะสามารถใช้ Lemonade เพื่อรันโมเดลในเครื่องของคุณได้

## สิ่งที่คุณจะได้เรียนรู้

เมื่อสิ้นสุด playbook นี้ คุณจะสามารถ:

* **ติดตั้ง Lemonade Server** และตรวจสอบว่ากำลังทำงานอยู่
* **ดาวน์โหลดและสนทนากับ LLM** โดยใช้คำสั่งเดียว
* **สำรวจ web UI** และลองใช้โมดาลิตีต่างๆ เช่น vision, speech-to-text และการสร้างภาพ
* **สลับ GPU backends** ระหว่าง Vulkan และ AMD ROCm™ software
* **สร้างแอป Python** ที่ขับเคลื่อนด้วย LLM ท้องถิ่นโดยใช้ API ที่เข้ากันได้กับ OpenAI
<!-- @device:halo_box,halo,stx,krk -->
* **รันโมเดลบน AMD Neural Processing Unit (NPU)** โดยใช้โหมดการทำงาน Hybrid และ FLM บนฮาร์ดแวร์ AMD Ryzen™ AI
<!-- @device:end -->

## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

ก่อนเริ่มต้น ตรวจสอบให้แน่ใจว่าคุณมี:

- พีซีที่รัน **Windows 11** หรือ **Linux** distribution ที่รองรับ (Ubuntu 24.04+, Fedora, Debian)
- แนะนำให้มี **RAM 16 GB** สำหรับโมเดล runtime ที่ใช้ในขั้นตอนที่ 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB) แนะนำให้มี **32 GB+** หากต้องการใช้โมเดลสร้างโค้ดขนาดใหญ่กว่าในขั้นตอนที่ 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB)
- **พื้นที่ดิสก์ว่าง ~4–30 GB** ขึ้นอยู่กับโมเดลที่คุณดาวน์โหลด โมเดลที่ใหญ่ที่สุดในคู่มือนี้มีขนาดประมาณ 20 GB
- **Python 3.10–3.13** (ใช้ในส่วนแอป Python)
- การเชื่อมต่ออินเทอร์เน็ต (แบบมีสายหรือไร้สาย)
<!-- @device:halo_box,halo,stx,krk -->
- [ไม่บังคับ] AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 series หรือ Z2 Extreme) พร้อมไดรเวอร์ล่าสุดที่ติดตั้งจาก [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) หากต้องการรันโมเดลบน NPU
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
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
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

---

## แนวคิดหลัก — วิธีการทำงานของเซิร์ฟเวอร์ AI ท้องถิ่น

ก่อนที่เราจะรันโมเดล ควรทำความเข้าใจว่า *เหตุใด* สิ่งต่างๆ จึงถูกตั้งค่าในลักษณะนี้ Lemonade คือ **เซิร์ฟเวอร์โมเดลท้องถิ่น** ซึ่งเป็นกระบวนการที่โหลดโมเดล AI เข้าสู่หน่วยความจำและเปิดเผยให้แอปพลิเคชันเข้าถึงผ่าน HTTP เช่นเดียวกับบริการ AI บนคลาวด์

### เหตุใดจึงต้องใช้เซิร์ฟเวอร์?

| ประโยชน์ | ความหมายสำหรับคุณ |
|---------|----------------------|
| **การผสานรวมที่เรียบง่าย** | แอปต่างๆ สื่อสารกับ HTTP API เดียวแทนที่จะต้องจัดการกับไลบรารี C++ หรือ Python เฉพาะฮาร์ดแวร์ |
| **โมเดลที่ใช้ร่วมกัน** | โมเดลที่โหลดเพียงตัวเดียวสามารถให้บริการหลายแอปพร้อมกันได้ โดยไม่มีสำเนาซ้ำที่กินหน่วยความจำของคุณ |
| **ความสามารถในการพกพาจากคลาวด์สู่ท้องถิ่น** | โค้ดที่เขียนสำหรับ cloud API ของ OpenAI ทำงานกับ Lemonade ได้โดยเปลี่ยน URL เพียงรายการเดียว |
| **การแยกความรับผิดชอบ** | การจัดการโมเดล การสตรีม และการทนต่อความผิดพลาดถูกจัดการโดยเซิร์ฟเวอร์ เพื่อให้นักพัฒนาสามารถมุ่งเน้นที่แอปของตนได้ |

### มาตรฐาน OpenAI API

Lemonade ใช้งาน **OpenAI API** ซึ่งเป็นอินเทอร์เฟซเดียวกับที่ใช้โดย ChatGPT, Azure OpenAI และบริการอื่นๆ อีกหลายสิบรายการ โมเดลการสนทนานั้นเรียบง่าย:

| บทบาท | ผู้ที่กำลังพูด |
|------|---------------|
| **system** | คำแนะนำสำหรับโมเดล (บุคลิก ข้อจำกัด เครื่องมือที่มีอยู่) |
| **user** | ข้อความจากมนุษย์ (หรือแอปพลิเคชัน) ถึงโมเดล |
| **assistant** | การตอบสนองที่สร้างโดยโมเดล |

ซึ่งหมายความว่าไลบรารีหรือแอปใดก็ตามที่รองรับ OpenAI สามารถสื่อสารกับ Lemonade ได้โดยชี้ไปที่ `http://localhost:13305/api/v1` ขณะที่ Lemonade Server กำลังทำงาน

## กิจกรรมหลัก — การสนทนา AI ท้องถิ่นครั้งแรกของคุณ

มาดาวน์โหลด LLM และสนทนากับมัน โดยรัน AI ทั้งหมดบนเครื่องของคุณเอง

### ขั้นตอนที่ 1: ดาวน์โหลดและรันโมเดล

Lemonade มาพร้อมกับไลบรารีโมเดลที่คัดสรรแล้ว มาเริ่มต้นด้วย **Gemma-4-E2B-it** ซึ่งเป็นโมเดลที่มีความสามารถและกะทัดรัด พร้อมรองรับ vision เปิด terminal และรัน:

```
lemonade run Gemma-4-E2B-it-GGUF
```

คำสั่งเดียวนี้ทำสามสิ่ง:

1. **ดาวน์โหลด** โมเดล (~3 GB) จาก Hugging Face หากยังไม่ได้ดาวน์โหลด (อาจใช้เวลาสักครู่)
2. **เริ่มต้น** กระบวนการ Lemonade Server บนพอร์ต 13305
3. **เปิด Lemonade App** เพื่อให้คุณเริ่มสนทนากับโมเดลได้


<!-- @os:windows -->
บน Windows Lemonade App จะเปิดขึ้นโดยอัตโนมัติและคุณสามารถเริ่มสนทนาได้ทันที หากคุณติดตั้งแพ็กเกจ `minimal.msi` แอปจะไม่รวมอยู่ด้วย หากต้องการเริ่มสนทนา ให้เปิดเว็บเบราว์เซอร์และไปที่ `http://localhost:13305`
<!-- @os:end -->

<!-- @os:linux -->
บน Linux ให้เปิดเบราว์เซอร์และไปที่ `http://localhost:13305` เพื่อเข้าถึงเว็บแอป
<!-- @os:end -->

ลองพิมพ์คำถาม:

```
What are three fun facts about lemons?
```

โมเดลจะตอบสนองโดยตรงในหน้าต่างแชท **ยินดีด้วย! คุณกำลังรันโมเดลภาษาขนาดใหญ่ในเครื่องของคุณเอง**

![Lemonade App with Logs displayed](../../dependencies/assets/ChatwithLogs.png)

ในบานหน้าต่าง Server Logs ใน Lemonade App คุณสามารถค้นหาข้อมูลการวัดประสิทธิภาพของโมเดลหลังจากแต่ละการตอบสนอง ตัวอย่างเช่น:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```
### ขั้นตอนที่ 2: สำรวจอินเทอร์เฟซเว็บและโหมดต่างๆ

Lemonade มีอินเทอร์เฟซเว็บในตัวที่คุณสามารถ:

- **โต้ตอบ** กับโมเดลที่โหลดไว้ในหน้าต่างแชทที่คุ้นเคย
- **เรียกดูโมเดล** ในแท็บ Model Manager
- **ดาวน์โหลดโมเดลใหม่** ด้วยคลิกเดียว

ลองสลับระหว่างโหมดต่างๆ โดยใช้แท็บ **Model Manager** ใน web UI ซึ่งคุณสามารถเรียกดูโมเดลตาม Recipe หรือตาม Category:

1. **Vision:** โมเดล `Gemma-4-E2B-it-GGUF` ที่คุณโหลดไว้แล้วรองรับ vision ลองวางรูปภาพลงในกล่องแชทแล้วถามให้โมเดลอธิบายภาพนั้น
2. **การสร้างภาพ:** ในหมวด Image ให้ดาวน์โหลดโมเดลสร้างภาพ เช่น `SDXL-Turbo` จาก Model Manager จากนั้นใช้ Lemonade Image Generator พิมพ์ prompt และสร้างภาพในเครื่องของคุณ
3. **Audio:** ในหมวด Audio ให้ดาวน์โหลดโมเดลเสียง เช่น `Whisper-Tiny` ซึ่งสามารถแปลงเสียงพูดเป็นข้อความได้ ให้ไฟล์เสียงเพื่อถอดความในเครื่องของคุณ สำหรับการแปลงข้อความเป็นเสียงพูด ลองใช้โมเดลในหมวด Speech เช่น `kokoro-v1`

![Multi-Modality กับ Lemonade](../../dependencies/assets/multi_modality.png)

### ขั้นตอนที่ 3: ลองใช้โมเดลกับ Backend ที่แตกต่างกัน

หากคุณวางเมาส์เหนือโมเดลใน Lemonade App คุณจะเห็นไอคอนรูปเฟือง การคลิกที่ไอคอนนี้จะให้คุณเลือกตัวเลือกสำหรับโมเดล รวมถึงการเลือก backend ที่ต้องการ

โดยค่าเริ่มต้น Lemonade ใช้ Vulkan สำหรับการเร่งความเร็วด้วย GPU หากคุณมี AMD discrete GPU ที่รองรับ คุณสามารถเปลี่ยนไปใช้ ROCm ได้

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

หากต้องการจัดการ backend ที่ติดตั้งไว้ ให้คลิกปุ่ม backend ในคอลัมน์ซ้ายสุด

หรือคุณสามารถระบุ backend โดยใช้คำสั่งต่อไปนี้:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

คุณยังสามารถตั้งค่า backend เริ่มต้นโดยใช้ environment variable `LEMONADE_LLAMACPP` ด้วยค่า: `vulkan`, `rocm`, หรือ `cpu`

---

## เจาะลึกยิ่งขึ้น — สร้างแอปที่ขับเคลื่อนด้วย AI ด้วย Python

พลังที่แท้จริงของ AI server ในเครื่องคือแอปพลิเคชันใดก็สามารถเชื่อมต่อกับมันได้ด้วยโค้ดเพียงไม่กี่บรรทัด เพื่อพิสูจน์สิ่งนี้ มาสร้าง **ตัวสร้างแฟลชการ์ดสำหรับการเรียน** ขนาดเล็กแต่ใช้งานได้จริง โดยคุณให้หัวข้อ มันจะสร้างแฟลชการ์ด และคุณสามารถทดสอบตัวเองแบบโต้ตอบได้

### ขั้นตอนที่ 4: เริ่มต้น Server

ตรวจสอบว่า Lemonade server กำลังทำงานอยู่ โดยปกติจะเริ่มต้นโดยอัตโนมัติในพื้นหลังหลังจากการติดตั้ง หากต้องการตรวจสอบ ให้รัน:

```
lemonade status
```

คุณควรเห็นข้อความเช่น: `Server is running on port 13305`

หาก server ไม่ทำงาน ให้เริ่มต้นโดยเปิดแอป Lemonade ใช้พอร์ตเริ่มต้น **13305** (คุณสามารถยืนยันหรือเลือกได้จากไอคอนใน tray)

### ขั้นตอนที่ 5: ติดตั้ง OpenAI Python Client

ในเทอร์มินัล สร้าง venv และติดตั้ง OpenAI Python Client โดยใช้คำสั่งต่อไปนี้:
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### ขั้นตอนที่ 6: สร้างแอป Flashcard

มาดาวน์โหลดโมเดลอื่นเพื่อสร้างโค้ด: `Qwen3.5-35B-A3B-GGUF` นี่คือโมเดลขนาดใหญ่ (~20 GB) ที่มีประสิทธิภาพสูง เหมาะสำหรับระบบที่มี RAM 32 GB ขึ้นไป หากคุณมี RAM น้อยกว่านั้น ลองใช้ `Qwen3.5-9B-GGUF` (~6 GB) แทน

คุณสามารถดาวน์โหลดได้จาก UI หรือรันคำสั่งต่อไปนี้:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

ป้อน prompt ต่อไปนี้ลงใน Lemonade Chat UI เพื่อสร้างโค้ดสำหรับแอป Flashcard อย่างง่าย

เราจะใช้ Qwen3.5-35B-A3B-GGUF (โมเดลขนาดใหญ่ที่เก่งในการเขียนโค้ด) เพื่อสร้างแอป Python ของเรา และแอปนั้นจะเรียกใช้ Gemma-4-E2B-it-GGUF (โมเดลขนาดเล็กที่คุณดาวน์โหลดไว้แล้ว) ในขณะรันไทม์ จากนั้นโค้ดสามารถคัดลอกไปยังไฟล์ที่คุณต้องการเพื่อรันใน Python

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **เคล็ดลับ**: เราได้ปฏิบัติตามแนวทางวิศวกรรมมาตรฐานผ่านการสร้าง prompt อย่างละเอียดและการใช้ระบบสองโมเดลเพื่อเพิ่มประสิทธิภาพทรัพยากรและความเร็ว

เพื่อความสะดวกของคุณ เราได้จัดเตรียมตัวอย่างผลลัพธ์ไว้ใน [`flashcards.py`](assets/flashcards.py) คุณสามารถดาวน์โหลดไปยังไดเรกทอรีของคุณได้ ไม่ว่าจะด้วยวิธีใด ตอนนี้คุณควรมีไฟล์ Python ที่พร้อมรัน

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
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

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### ขั้นตอนที่ 7: รันโค้ดที่สร้างขึ้น

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**นี่คือสิ่งที่คุณควรเห็น:**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

ด้วยโค้ดประมาณ 150 บรรทัด คุณได้สร้างเครื่องมือการเรียนที่ใช้งานได้จริงซึ่งขับเคลื่อนด้วย LLM ในเครื่องของคุณ ไม่มี API key ที่ต้องจัดการ ไม่มีค่าใช้จ่ายในการใช้งาน และข้อมูลไม่เคยออกจากเครื่องของคุณเลย

> **ข้อสังเกตสำคัญ:** สังเกตว่าบรรทัด `client = OpenAI(base_url=...) ` เป็น *สิ่งเดียว* ที่ผูกแอปนี้กับ Lemonade แทนที่จะเป็น cloud ของ OpenAI โค้ดส่วนที่เหลือเหมือนกันทุกประการกับที่คุณจะเขียนสำหรับบริการที่เข้ากันได้กับ OpenAI ใดๆ หากคุณเคยใช้ OpenAI Python library มาก่อน คุณก็รู้วิธีสร้างแอปด้วย Lemonade แล้ว

### สิ่งที่แสดงให้เห็น

แอปขนาดเล็กนี้ใช้รูปแบบการผสานรวมในโลกจริงหลายอย่าง:

| รูปแบบ | ปรากฏที่ไหน |
|---------|-----------------|
| **System prompts** | ข้อความ `"system"` บอกให้ LLM ส่งออกเป็น JSON ที่มีโครงสร้าง |
| **Structured output** | แอปแยกวิเคราะห์การตอบสนองของ LLM เป็น JSON เพื่อสร้างแฟลชการ์ด |
| **Stateless requests** | การเรียก `generate_flashcards()` แต่ละครั้งเป็นอิสระจากกัน |
| **Error handling** | `try/except` จัดการกรณีที่ผลลัพธ์ของ LLM ไม่ใช่ JSON ที่ถูกต้องอย่างสง่างาม |

รูปแบบเหล่านี้สามารถขยายไปสู่แอปพลิเคชันใดก็ได้ เช่น chatbot, ผู้ช่วยเขียนโค้ด, ตัวสร้างเนื้อหา, เครื่องมืออัตโนมัติ

#### ความท้าทายเพิ่มเติม

* สำหรับความท้าทายเพิ่มเติม ลองอัปเดตแอปให้อ่านแฟลชการ์ดให้ผู้ใช้ฟัง โดยอ้างอิงตัวอย่างที่ให้ไว้ [ที่นี่](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)

---

<!-- @device:halo_box,halo,stx,krk -->
## การรันโมเดลบน NPU (ไม่บังคับ)

หากคุณมีอุปกรณ์ Ryzen AI 300/400/Max 300 series หรือ Z2 Extreme อุปกรณ์ของคุณมี **Neural Processing Unit (NPU)** ในตัว ซึ่งเป็นชิปเฉพาะที่ออกแบบมาสำหรับงาน AI โดยเฉพาะ การรันโมเดลบน NPU ใช้พลังงานน้อยกว่าการใช้ GPU ทำให้เหมาะสำหรับงาน AI ที่ทำงานอยู่เบื้องหลัง การใช้งานระยะยาว และการใช้งานด้วยแบตเตอรี่

Lemonade รองรับโหมดการทำงาน NPU สามโหมด ซึ่งทั้งหมดทำงานผ่าน OpenAI API เดียวกันอย่างโปร่งใส:

| โหมด | วิธีการทำงาน | Recipe | ตัวอย่างโมเดล |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU ประมวลผล prompt, iGPU สร้าง token | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU-only** | การอนุมานทั้งหมดทำงานบน NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | ใช้ FastFlowLM engine บน NPU ที่ปรับแต่งสำหรับ AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### ข้อกำหนด

- โปรเซสเซอร์ **AMD Ryzen AI 300/400 series หรือ Z2 series**
- สำหรับโมเดล **FLM**: FLM runtime สามารถติดตั้งได้จากภายในแอป Lemonade หรือ Lemonade จะติดตั้ง FLM runtime โดยอัตโนมัติเมื่อรันโมเดล FLM หากต้องการเรียนรู้เพิ่มเติมเกี่ยวกับ FastFlowLM ดูได้ [ที่นี่](https://fastflowlm.com/docs/)


### ขั้นตอนที่ 8: รัน Hybrid Model

Hybrid model แบ่งงานระหว่าง NPU และ iGPU เพื่อความสมดุลที่ดีระหว่างความเร็วและประสิทธิภาพ ในแอป Lemonade ให้เลือกโมเดลจากรายการ `Ryzen AI LLM` เช่น `Qwen3-4B-Hybrid` หรือรันด้วยคำสั่งต่อไปนี้:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade ตรวจจับ NPU ของคุณโดยอัตโนมัติและติดตั้ง backend **Ryzen AI LLM**

> **เกิดอะไรขึ้นเบื้องหลัง?** เมื่อคุณส่งข้อความ NPU จะประมวลผล prompt ทั้งหมดของคุณแบบขนาน (เรียกว่า "prefill") จากนั้น iGPU จะเข้ามารับช่วงต่อเพื่อสร้างการตอบสนองทีละ token (เรียกว่า "decode") วิธี hybrid นี้ใช้ประโยชน์จากจุดแข็งของแต่ละชิป

### ขั้นตอนที่ 9: รัน FLM Model

โมเดล FastFlowLM (FLM) ได้รับการปรับแต่งโดยเฉพาะสำหรับสถาปัตยกรรม AMD XDNA2 NPU และสามารถทำงานได้เร็วมากสำหรับขนาดของมัน ตัวอย่างเช่น เลือก `qwen3.5-4b-FLM` จากรายการ `FastFlowLM NPU` หรือใช้คำสั่งต่อไปนี้:

<!-- @os:windows -->
เพื่อเปิดใช้งาน `FastFlowLM` บน Windows:

* เปิดเมนู `Backends Manager`
* ค้นหาหมวดหมู่ backend `FastFlowLM NPU`
* คลิก Install NPU
* เมื่อการติดตั้งเสร็จสมบูรณ์ โมเดลเริ่มต้นประมาณ 36 รายการจะพร้อมใช้งานในเมนูดรอปดาวน์ FFLM
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
เมื่อเปิดแอป `Lemonade` เป็นครั้งแรก backend `FastFlowNPU` จะไม่ถูกเปิดใช้งานโดยค่าเริ่มต้น
แอปในเครื่องจะเปิดหน้าการติดตั้งเพื่อแนะนำคุณตลอดขั้นตอนการตั้งค่า

เพื่อเปิดใช้งาน `FastFlowLM` บน Linux:

* เปิดแอป `Lemonade`
* เยี่ยมชม [เอกสาร FLM อย่างเป็นทางการ](https://lemonade-server.ai/flm_npu_linux.html) และทำตามขั้นตอนการติดตั้ง FLM โดยเลือก Linux distribution ของคุณ
* เปิดใช้งาน backports ตามที่ระบุในหน้าการติดตั้ง
* ดาวน์โหลด release `v0.9.x` ล่าสุดจาก [หน้า tags](https://github.com/FastFlowLM/FastFlowLM/tags)
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
สำหรับ AMD Halo Developer Platform ให้แน่ใจว่าเลือก Debian 13
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* ติดตั้งแพ็กเกจ `.deb` ที่ดาวน์โหลดมา
* แนะนำ: ปิดแอป `Lemonade` และเปิดใหม่อีกครั้งเพื่อให้ตรวจจับการเปลี่ยนแปลง
* แนะนำ: เปิด `Backends Manager` และคลิก Install `FastFlowNPU` Backend
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
หลังจากติดตั้งสำเร็จ คุณควรเห็นว่า `flm:npu` เสร็จสมบูรณ์ใน **Download Manager** ภายใน **Lemonade Desktop App**
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
จากนั้นคุณสามารถเลือกโมเดล FFLM ที่มีอยู่และเริ่มใช้งาน NPU backend ได้

สำหรับโมเดลเฉพาะ ให้ดาวน์โหลดโมเดลที่ต้องการจาก [หน้าโมเดล](https://fastflowlm.com/docs/models/qwen/) และตรวจสอบโดยใช้คำสั่ง Shell ที่ระบุในเอกสาร
```
flm run qwen3.5-4b-FLM
```
หรือผ่าน 
```
lemonade run qwen3.5-4b-FLM
```

โมเดล FLM รวมถึงสถาปัตยกรรมยอดนิยมบางส่วน (Gemma 3, Qwen 3, Llama 3 และ DeepSeek R1) และมีขนาดตั้งแต่ต่ำกว่า 1 GB ไปจนถึงมากกว่า 13 GB
Lemonade ตรวจจับ NPU ของคุณโดยอัตโนมัติและติดตั้ง backend **FastFlowLM NPU**

<!-- @os:windows -->
> **เคล็ดลับ:** เพื่อประสิทธิภาพ NPU ที่ดีที่สุด ให้เปิดใช้งาน turbo mode:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### การสลับโมเดล

แอปบัตรคำจากขั้นตอนที่ 6 ทำงานกับโมเดล NPU ได้เช่นกัน เพียงเปลี่ยนชื่อโมเดล:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## ขั้นตอนถัดไป

คุณมีเซิร์ฟเวอร์ AI ในเครื่องที่ทำงานบนฮาร์ดแวร์ของคุณเองแล้ว นี่คือสิ่งที่ควรทำต่อไป:

1. **เชื่อมต่อแอปที่คุณชื่นชอบ**: Lemonade ทำงานได้ทันทีกับ [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) และ [อีกมากมาย](https://lemonade-server.ai/marketplace)

2. **เรียกดูโมเดลเพิ่มเติม**: สำรวจ [คลังโมเดล](https://lemonade-server.ai/docs/server/server_models/) ทั้งหมดเพื่อค้นหาโมเดลที่ปรับแต่งสำหรับการเขียนโค้ด การใช้เหตุผล วิสัยทัศน์ และอื่นๆ ใช้แอป Lemonade หรือ `lemonade list` เพื่อดูสิ่งที่มีอยู่

3. **ปลดล็อก ROCm GPU acceleration**: หากคุณมี AMD GPU ที่รองรับ ให้สลับไปใช้ ROCm backend: `lemonade config set llamacpp.backend=rocm` ดู [AMD GPU ที่รองรับ](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)

4. **อ่านข้อกำหนด API ฉบับเต็ม**: Lemonade รองรับ chat completions, embeddings, audio transcription, image generation, text-to-speech และอื่นๆ ดู [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) สำหรับทุก endpoint

5. **มีส่วนร่วม**: Lemonade เป็น open source ดู [คู่มือการมีส่วนร่วม](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) และค้นหา [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)