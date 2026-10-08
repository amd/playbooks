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

🍋 **Lemonade** เป็นเซิร์ฟเวอร์ AI แบบโลคัลที่เป็นโอเพนซอร์ส ซึ่งช่วยให้คุณสามารถรันโมเดลภาษาขนาดใหญ่ (LLM) ตัวสร้างภาพ และโมเดลเสียงได้โดยตรงบนฮาร์ดแวร์ของคุณเอง โดยจะเปิดให้เข้าถึงโมเดลเหล่านี้ผ่าน **OpenAI API** ซึ่งเป็นมาตรฐานของอุตสาหกรรม ดังนั้นแอปใดก็ตามที่ทำงานร่วมกับ OpenAI ได้ก็จะสามารถทำงานร่วมกับ Lemonade ได้ทันที เมื่อจบ playbook นี้ คุณจะได้ใช้ Lemonade ในการรันโมเดลแบบโลคัลบนเครื่องของคุณ

## สิ่งที่คุณจะได้เรียนรู้

เมื่อจบ playbook นี้ คุณจะสามารถ:

* **ติดตั้ง Lemonade Server** และตรวจสอบว่ามันกำลังทำงานอยู่
* **ดาวน์โหลดและแชทกับ LLM** โดยใช้คำสั่งเดียว
* **สำรวจเว็บ UI** และลองใช้โหมดต่างๆ เช่น การมองเห็น (vision), การแปลงเสียงเป็นข้อความ (speech-to-text) และการสร้างภาพ
* **สลับแบ็กเอนด์ GPU** ระหว่าง Vulkan และซอฟต์แวร์ AMD ROCm™
* **สร้างแอป Python** ที่ขับเคลื่อนด้วย LLM แบบโลคัลโดยใช้ API ที่เข้ากันได้กับ OpenAI
<!-- @device:halo_box,halo,stx,krk -->
* **รันโมเดลบน AMD Neural Processing Unit (NPU)** โดยใช้โหมดการทำงานแบบ Hybrid และ FLM บนฮาร์ดแวร์ AMD Ryzen™ AI
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

ก่อนเริ่มต้น โปรดตรวจสอบให้แน่ใจว่าคุณมี:

- พีซีที่รัน **Windows 11** หรือดิสทริบิวชัน **Linux** ที่รองรับ (Ubuntu 24.04+, Fedora, Debian)
- แนะนำให้มี **RAM 16 GB** สำหรับโมเดลรันไทม์ที่ใช้ในขั้นตอนที่ 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB) แนะนำ **32 GB+** หากคุณต้องการใช้โมเดลสร้างโค้ดขนาดใหญ่กว่าในขั้นตอนที่ 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB)
- **พื้นที่ว่างบนดิสก์ประมาณ 4–30 GB** ขึ้นอยู่กับโมเดลที่คุณดาวน์โหลด โมเดลที่ใหญ่ที่สุดในคู่มือนี้มีขนาดประมาณ 20 GB
- **Python 3.10–3.13** (ใช้ในส่วนแอป Python)
- การเชื่อมต่ออินเทอร์เน็ต (แบบมีสายหรือไร้สาย)
<!-- @device:halo_box,halo,stx,krk -->
- [ไม่บังคับ] AMD XDNA 2 NPU (Ryzen AI ซีรีส์ 300/400/Max 300 หรือ Z2 Extreme) ที่ติดตั้งไดรเวอร์เวอร์ชันล่าสุดจาก [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) หากคุณต้องการรันโมเดลบน NPU
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade-models-gemma-4-e2b,lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
```
<!-- @test:end -->

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
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

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

## แนวคิดหลัก — การทำงานของเซิร์ฟเวอร์ AI แบบโลคัล

ก่อนที่เราจะรันโมเดล ควรทำความเข้าใจก่อนว่า *เหตุใด* จึงตั้งค่าในลักษณะนี้ Lemonade คือ **เซิร์ฟเวอร์โมเดลแบบโลคัล** ซึ่งเป็นโปรเซสที่โหลดโมเดล AI เข้าสู่หน่วยความจำและเปิดให้แอปพลิเคชันเข้าถึงได้ผ่าน HTTP เช่นเดียวกับที่บริการ AI บนคลาวด์ทำ

### ทำไมต้องใช้เซิร์ฟเวอร์?

| ประโยชน์ | ความหมายสำหรับคุณ |
|---------|----------------------|
| **การผสานรวมที่ง่ายขึ้น** | แอปจะสื่อสารกับ HTTP API เพียงตัวเดียว แทนที่จะต้องจัดการกับไลบรารี C++ หรือ Python เฉพาะฮาร์ดแวร์ |
| **การแชร์โมเดล** | โมเดลที่โหลดไว้เพียงตัวเดียวสามารถให้บริการหลายแอปพร้อมกันได้ โดยไม่ต้องมีสำเนาซ้ำซ้อนมากินพื้นที่ RAM ของคุณ |
| **ความพกพาได้จากคลาวด์สู่โลคัล** | โค้ดที่เขียนสำหรับ API คลาวด์ของ OpenAI สามารถทำงานกับ Lemonade ได้โดยเปลี่ยน URL เพียงอันเดียว |
| **การแยกส่วนความรับผิดชอบ** | การจัดการโมเดล, การสตรีม และความทนทานต่อข้อผิดพลาดจะถูกจัดการโดยเซิร์ฟเวอร์ เพื่อให้นักพัฒนาสามารถมุ่งเน้นไปที่แอปของตนได้ |

### มาตรฐาน OpenAI API

Lemonade นำไปใช้ **OpenAI API** ซึ่งเป็นอินเทอร์เฟซเดียวกับที่ใช้โดย ChatGPT, Azure OpenAI และบริการอื่นๆ อีกหลายสิบรายการ โมเดลการสนทนามีความเรียบง่าย:

| บทบาท | ใครกำลังพูด |
|------|---------------|
| **system** | คำสั่งสำหรับโมเดล (บุคลิก, ข้อจำกัด, เครื่องมือที่ใช้งานได้) |
| **user** | ข้อความจากมนุษย์ (หรือแอปพลิเคชัน) ถึงโมเดล |
| **assistant** | คำตอบที่สร้างขึ้นโดยโมเดล |

ซึ่งหมายความว่าไลบรารีหรือแอปใดก็ตามที่รองรับ OpenAI สามารถสื่อสารกับ Lemonade ได้โดยชี้ไปที่ `http://localhost:13305/api/v1` ในขณะที่ Lemonade Server กำลังทำงานอยู่

## กิจกรรมหลัก — การแชท AI แบบโลคัลครั้งแรกของคุณ

มาดาวน์โหลด LLM และสนทนากับมันกัน โดยรัน AI ทั้งหมดบนเครื่องของคุณเอง

### ขั้นตอนที่ 1: ดาวน์โหลดและรันโมเดล

Lemonade มาพร้อมกับไลบรารีโมเดลที่คัดสรรไว้แล้ว มาเริ่มกันที่ **Gemma-4-E2B-it** ซึ่งเป็นโมเดลที่มีความสามารถสูงและมีขนาดกะทัดรัด รวมถึงรองรับการมองเห็น (vision) ด้วย เปิดเทอร์มินัลแล้วรันคำสั่งนี้:

```
lemonade run Gemma-4-E2B-it-GGUF
```

คำสั่งนี้ทำสามสิ่งพร้อมกัน:

1. **ดาวน์โหลด** โมเดล (~3 GB) จาก Hugging Face หากยังไม่ได้ดาวน์โหลดไว้ (อาจใช้เวลาสักครู่)
2. **เริ่มต้น** โปรเซส Lemonade Server บนพอร์ต 13305
3. **เปิด Lemonade App** เพื่อให้คุณเริ่มแชทกับโมเดลได้

<!-- @os:windows -->
บน Windows แอป Lemonade จะเปิดขึ้นโดยอัตโนมัติและคุณสามารถเริ่มแชทได้ทันที หากคุณติดตั้งแพ็กเกจ `minimal.msi` แอปจะไม่ถูกรวมมาด้วย หากต้องการเริ่มแชท ให้เปิดเว็บเบราว์เซอร์และไปที่ `http://localhost:13305`
<!-- @os:end -->

<!-- @os:linux -->
บน Linux ให้เปิดเบราว์เซอร์และไปที่ `http://localhost:13305` เพื่อเข้าถึงเว็บแอป
<!-- @os:end -->

ลองพิมพ์คำถาม:

```
What are three fun facts about lemons?
```

โมเดลจะตอบกลับโดยตรงในหน้าต่างแชท **ยินดีด้วย! คุณกำลังรันโมเดลภาษาขนาดใหญ่แบบโลคัลแล้ว**

![Lemonade App with Logs displayed](../../dependencies/assets/ChatwithLogs.png)

ในแผง Server Logs ของ Lemonade App คุณจะพบข้อมูลเทเลเมทรีเกี่ยวกับประสิทธิภาพของโมเดลหลังจากแต่ละคำตอบ ตัวอย่างเช่น:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### ขั้นตอนที่ 2: สำรวจเว็บอินเทอร์เฟซและโหมดการทำงานต่าง ๆ

Lemonade มาพร้อมกับเว็บอินเทอร์เฟซในตัวที่คุณสามารถ:

- **โต้ตอบ** กับโมเดลที่โหลดไว้ในหน้าต่างแชทที่คุ้นเคย
- **เรียกดูโมเดล** ในแท็บ Model Manager
- **ดาวน์โหลดโมเดลใหม่** ได้ในคลิกเดียว

ลองสลับระหว่างโหมดการทำงานต่าง ๆ โดยใช้แท็บ **Model Manager** ในเว็บ UI ซึ่งคุณสามารถเรียกดูโมเดลได้ตาม Recipe หรือตาม Category:

1. **Vision:** โมเดล `Gemma-4-E2B-it-GGUF` ที่คุณโหลดไว้แล้วรองรับการมองเห็น (vision) ลองวางรูปภาพลงในกล่องแชทแล้วขอให้โมเดลอธิบายรูปนั้น
2. **การสร้างภาพ:** ในหมวดหมู่ Image ให้ดาวน์โหลดโมเดลสร้างภาพ เช่น `SDXL-Turbo` จาก Model Manager จากนั้นใช้ Lemonade Image Generator เพื่อพิมพ์พรอมต์และสร้างภาพในเครื่องของคุณเอง
3. **เสียง:** ในหมวดหมู่ Audio ให้ดาวน์โหลดโมเดลเสียง เช่น `Whisper-Tiny` ซึ่งสามารถแปลงเสียงพูดเป็นข้อความได้ ให้บันทึกเสียงเพื่อถอดความในเครื่องของคุณเอง สำหรับการแปลงข้อความเป็นเสียงพูด ให้ลองใช้โมเดลในหมวดหมู่ Speech เช่น `kokoro-v1`

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### ขั้นตอนที่ 3: ลองใช้โมเดลด้วยแบ็กเอนด์ที่แตกต่างกัน

หากคุณวางเมาส์เหนือโมเดลใน Lemonade App คุณจะเห็นไอคอนรูปเฟือง การคลิกไอคอนนี้จะทำให้คุณสามารถเลือกตัวเลือกต่าง ๆ สำหรับโมเดล รวมถึงการเลือกแบ็กเอนด์ที่ต้องการ

โดยค่าเริ่มต้น Lemonade จะใช้ Vulkan สำหรับการเร่งความเร็วด้วย GPU หากคุณมี GPU แบบแยก (discrete GPU) ของ AMD ที่รองรับ คุณสามารถสลับไปใช้ ROCm ได้

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

หากต้องการจัดการแบ็กเอนด์ที่ติดตั้งไว้ ให้คลิกปุ่มแบ็กเอนด์ในคอลัมน์ซ้ายสุด

หรือคุณสามารถระบุแบ็กเอนด์โดยใช้คำสั่งต่อไปนี้:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

คุณยังสามารถตั้งค่าแบ็กเอนด์เริ่มต้นได้โดยใช้ตัวแปรสภาพแวดล้อม `LEMONADE_LLAMACPP` ด้วยค่า: `vulkan`, `rocm`, หรือ `cpu`

---

## เจาะลึกยิ่งขึ้น — สร้างแอป AI ด้วย Python

พลังที่แท้จริงของเซิร์ฟเวอร์ AI ในเครื่องคือ แอปพลิเคชันใด ๆ ก็สามารถเชื่อมต่อกับมันได้ด้วยโค้ดเพียงไม่กี่บรรทัด เพื่อพิสูจน์สิ่งนี้ มาสร้าง**เครื่องมือสร้างแฟลชการ์ดเพื่อการเรียน (study flashcard generator)** ขนาดเล็กแต่ใช้งานได้จริงกัน โดยคุณป้อนหัวข้อเข้าไป มันจะสร้างแฟลชการ์ด และคุณสามารถทดสอบตัวเองได้แบบโต้ตอบ

### ขั้นตอนที่ 4: เริ่มต้นเซิร์ฟเวอร์

ตรวจสอบว่าเซิร์ฟเวอร์ Lemonade กำลังทำงานอยู่หรือไม่ โดยปกติแล้วมันจะเริ่มทำงานโดยอัตโนมัติในพื้นหลังหลังจากการติดตั้ง หากต้องการตรวจสอบ ให้รัน:

```
lemonade status
```

คุณควรเห็นข้อความเช่น: `Server is running on port 13305`

หากเซิร์ฟเวอร์ไม่ได้ทำงาน ให้เริ่มต้นโดยการเปิดแอป Lemonade ใช้พอร์ตเริ่มต้น **13305** (คุณสามารถยืนยันหรือเลือกพอร์ตนี้ได้จากไอคอนในถาดระบบ)

### ขั้นตอนที่ 5: ติดตั้ง OpenAI Python Client

ในเทอร์มินัล ให้สร้าง venv และติดตั้ง OpenAI Python Client โดยใช้คำสั่งต่อไปนี้:
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

### ขั้นตอนที่ 6: สร้างแอปแฟลชการ์ด

มาดาวน์โหลดโมเดลอื่นเพื่อสร้างโค้ดกัน: `Qwen3.5-35B-A3B-GGUF` นี่เป็นโมเดลขนาดใหญ่ (~20 GB) ที่มีประสิทธิภาพสูง เหมาะที่สุดสำหรับระบบที่มี RAM 32 GB ขึ้นไป หากคุณมี RAM น้อยกว่านี้ ให้ลองใช้ `Qwen3.5-9B-GGUF` (~6 GB) แทน

คุณสามารถดาวน์โหลดได้จาก UI หรือรันคำสั่งต่อไปนี้:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

ป้อนพรอมต์ต่อไปนี้ลงใน Lemonade Chat UI เพื่อสร้างโค้ดสำหรับแอปแฟลชการ์ดแบบง่าย

เราจะใช้ Qwen3.5-35B-A3B-GGUF (โมเดลขนาดใหญ่กว่าที่เขียนโค้ดได้ดีกว่า) เพื่อสร้างแอป Python ของเรา และตัวแอปเองจะเรียกใช้ Gemma-4-E2B-it-GGUF (โมเดลขนาดเล็กกว่าที่คุณดาวน์โหลดไว้แล้ว) ในขณะรันไทม์ จากนั้นสามารถคัดลอกโค้ดไปยังไฟล์ที่คุณเลือกเพื่อรันใน Python ได้

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

> **เคล็ดลับ**: เราได้ปฏิบัติตามแนวทางวิศวกรรมมาตรฐานผ่านการสร้างพรอมต์อย่างละเอียด และการใช้ระบบสองโมเดลเพื่อเพิ่มประสิทธิภาพการใช้ทรัพยากรและความเร็ว

เพื่อความสะดวกของคุณ เราได้จัดเตรียมตัวอย่างผลลัพธ์ไว้ใน [`flashcards.py`](assets/flashcards.py) คุณสามารถดาวน์โหลดไปยังไดเรกทอรีของคุณได้ตามสะดวก ไม่ว่าจะเลือกวิธีใด ตอนนี้คุณควรมีไฟล์ Python ที่สามารถรันได้แล้ว

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

ด้วยโค้ดประมาณ 150 บรรทัด คุณได้สร้างเครื่องมือช่วยเรียนที่ใช้งานได้เต็มรูปแบบโดยขับเคลื่อนด้วย LLM ในเครื่อง ไม่มี API key ที่ต้องจัดการ ไม่มีค่าใช้จ่ายในการใช้งาน และไม่มีข้อมูลใดออกจากเครื่องของคุณเลย

> **ข้อมูลเชิงลึกสำคัญ:** สังเกตว่าบรรทัด `client = OpenAI(base_url=...) ` เป็นสิ่งเดียวที่เชื่อมโยงแอปนี้เข้ากับ Lemonade แทนที่จะเป็นคลาวด์ของ OpenAI โค้ดที่เหลือเหมือนกันทุกประการกับที่คุณจะเขียนสำหรับบริการที่เข้ากันได้กับ OpenAI ใด ๆ หากคุณเคยใช้ไลบรารี OpenAI Python มาก่อน คุณก็รู้วิธีสร้างแอปด้วย Lemonade อยู่แล้ว

### สิ่งที่สิ่งนี้แสดงให้เห็น

แอปเล็ก ๆ นี้แสดงให้เห็นรูปแบบการผสานรวมที่ใช้งานจริงหลายรูปแบบ:

| รูปแบบ | ปรากฏที่ใด |
|---------|-----------------|
| **System prompts** | ข้อความ `"system"` บอกให้ LLM ส่งออกเป็น JSON ที่มีโครงสร้าง |
| **ผลลัพธ์ที่มีโครงสร้าง** | แอปแยกวิเคราะห์การตอบกลับของ LLM เป็น JSON เพื่อสร้างแฟลชการ์ด |
| **คำขอแบบไม่มีสถานะ (Stateless)** | การเรียก `generate_flashcards()` แต่ละครั้งเป็นอิสระต่อกัน |
| **การจัดการข้อผิดพลาด** | `try/except` จัดการกรณีที่ผลลัพธ์ของ LLM ไม่ใช่ JSON ที่ถูกต้องได้อย่างราบรื่น |

รูปแบบเดียวกันนี้สามารถนำไปขยายใช้กับแอปพลิเคชันใด ๆ เช่น แชทบอท ผู้ช่วยเขียนโค้ด เครื่องมือสร้างเนื้อหา และเครื่องมืออัตโนมัติ

#### ความท้าทายพิเศษ

* หากต้องการความท้าทายเพิ่มเติม ลองอัปเดตแอปให้สามารถอ่านแฟลชการ์ดให้ผู้ใช้ฟัง โดยอ้างอิงจากตัวอย่างที่ให้ไว้ [ที่นี่](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)

---

<!-- @device:halo_box,halo,stx,krk -->
## การรันโมเดลบน NPU (ทางเลือกเสริม)

หากคุณมีอุปกรณ์ที่ใช้ Ryzen AI 300/400/Max 300 series หรือ Z2 Extreme อุปกรณ์ของคุณจะมี **หน่วยประมวลผลประสาทเทียม (Neural Processing Unit - NPU)** ในตัว ซึ่งเป็นชิปเฉพาะทางที่ออกแบบมาสำหรับงาน AI โดยเฉพาะ การรันโมเดลบน NPU จะประหยัดพลังงานมากกว่าการใช้ GPU ทำให้เหมาะอย่างยิ่งสำหรับงาน AI ที่ทำงานเบื้องหลัง เซสชันที่ใช้เวลานาน และการใช้งานแบบพกพาด้วยแบตเตอรี่

Lemonade รองรับโหมดการประมวลผลบน NPU สามโหมด ซึ่งทั้งหมดทำงานอย่างโปร่งใสภายใต้ OpenAI API เดียวกัน:

| โหมด | วิธีการทำงาน | Recipe | ตัวอย่างโมเดล |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU ประมวลผลพรอมต์ iGPU สร้างโทเคน | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU-only** | การอนุมานทั้งหมดทำงานบน NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | ใช้เอนจิน FastFlowLM บน NPU ซึ่งปรับให้เหมาะกับ AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### ข้อกำหนด

- โปรเซสเซอร์ **AMD Ryzen AI 300/400 series หรือ Z2 series**
- สำหรับโมเดล **FLM**: สามารถติดตั้ง FLM runtime ได้จากภายในแอป Lemonade หรือ Lemonade จะติดตั้ง FLM runtime ให้โดยอัตโนมัติเมื่อรันโมเดล FLM หากต้องการเรียนรู้เพิ่มเติมเกี่ยวกับ FastFlowLM โปรดดู[ที่นี่](https://fastflowlm.com/docs/)


### ขั้นตอนที่ 8: รันโมเดล Hybrid

โมเดล Hybrid จะแบ่งงานระหว่าง NPU และ iGPU เพื่อให้ได้สมดุลที่ดีระหว่างความเร็วและประสิทธิภาพการใช้พลังงาน ในแอป Lemonade ให้เลือกโมเดลจากรายการ `Ryzen AI LLM` ตัวอย่างเช่น `Qwen3-4B-Hybrid` หรือรันด้วยคำสั่งต่อไปนี้:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade จะตรวจจับ NPU ของคุณโดยอัตโนมัติและติดตั้งแบ็กเอนด์ **Ryzen AI LLM**

> **เบื้องหลังการทำงานเป็นอย่างไร?** เมื่อคุณส่งข้อความ NPU จะประมวลผลพรอมต์ทั้งหมดของคุณแบบขนาน (เรียกว่า "prefill") จากนั้น iGPU จะรับช่วงต่อเพื่อสร้างคำตอบทีละโทเคน (เรียกว่า "decode") แนวทางแบบ hybrid นี้ใช้จุดแข็งของแต่ละชิปได้อย่างเต็มที่

### ขั้นตอนที่ 9: รันโมเดล FLM

โมเดล FastFlowLM (FLM) ได้รับการปรับให้เหมาะกับสถาปัตยกรรม NPU XDNA2 ของ AMD โดยเฉพาะ และสามารถทำงานได้รวดเร็วมากเมื่อเทียบกับขนาดของมัน ตัวอย่างเช่น เลือก `qwen3.5-4b-FLM` จากรายการ `FastFlowLM NPU` หรือใช้คำสั่งต่อไปนี้:

<!-- @os:windows -->
วิธีเปิดใช้งาน `FastFlowLM` บน Windows:

* เปิดเมนู `Backends Manager`
* ค้นหาหมวดหมู่แบ็กเอนด์ `FastFlowLM NPU`
* คลิก Install NPU
* เมื่อการติดตั้งเสร็จสมบูรณ์ โมเดลเริ่มต้นประมาณ 36 รายการจะปรากฏในเมนูแบบเลื่อนลง FFLM
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
เมื่อเปิดแอป `Lemonade` เป็นครั้งแรก แบ็กเอนด์ `FastFlowNPU` จะไม่ถูกเปิดใช้งานโดยค่าเริ่มต้น
แอปในเครื่องจะเปิดหน้าการติดตั้งเพื่อนำทางคุณผ่านขั้นตอนการตั้งค่า

วิธีเปิดใช้งาน `FastFlowLM` บน Linux:

* เปิดแอป `Lemonade`
* เข้าชมเอกสาร [official FLM](https://lemonade-server.ai/flm_npu_linux.html) และปฏิบัติตามขั้นตอนการติดตั้งสำหรับ FLM โดยเลือกดิสโทรของ Linux ของคุณ
* เปิดใช้งาน backports ตามที่ระบุไว้ในหน้าการติดตั้ง
* ดาวน์โหลดรีลีสล่าสุด `v0.9.x` จาก [tags page](https://github.com/FastFlowLM/FastFlowLM/tags)
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
สำหรับ AMD Halo Developer Platform โปรดเลือก Debian 13 ให้แน่ใจ
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
* แนะนำ: ปิด `Lemonade App` แล้วเปิดใหม่อีกครั้งเพื่อให้ตรวจพบการเปลี่ยนแปลง
* แนะนำ: เปิด `Backends Manager` แล้วคลิก Install `FastFlowNPU` Backend
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
หลังจากติดตั้งสำเร็จแล้ว คุณควรเห็นว่า `flm:npu` ดำเนินการเสร็จสมบูรณ์ใน **Download Manager** ภายใน **Lemonade Desktop App**
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
จากนั้นคุณสามารถเลือกโมเดล FFLM ที่มีอยู่และเริ่มใช้งานแบ็กเอนด์ NPU ได้

สำหรับโมเดลเฉพาะ ให้ดาวน์โหลดโมเดลที่ต้องการจาก[หน้าโมเดล](https://fastflowlm.com/docs/models/qwen/) และตรวจสอบความถูกต้องโดยใช้คำสั่ง Shell ที่ระบุไว้ในเอกสารประกอบ
```
flm run qwen3.5-4b-FLM
```
หรือผ่าน
```
lemonade run qwen3.5-4b-FLM
```

โมเดล FLM รวมถึงสถาปัตยกรรมที่ได้รับความนิยมมากที่สุดบางส่วน (Gemma 3, Qwen 3, Llama 3 และ DeepSeek R1) และมีขนาดตั้งแต่ต่ำกว่า 1 GB ไปจนถึงมากกว่า 13 GB
Lemonade จะตรวจจับ NPU ของคุณโดยอัตโนมัติและติดตั้งแบ็กเอนด์ **FastFlowLM NPU**

<!-- @os:windows -->
> **เคล็ดลับ:** เพื่อประสิทธิภาพ NPU ที่ดีที่สุด ให้เปิดใช้งานโหมดเทอร์โบ:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### การสลับโมเดล

แอปแฟลชการ์ดจากขั้นตอนที่ 6 ก็ใช้งานได้กับโมเดลบน NPU เช่นกัน เพียงแค่เปลี่ยนชื่อโมเดล:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## ขั้นตอนถัดไป

คุณมีเซิร์ฟเวอร์ AI ในเครื่องที่ทำงานอยู่บนฮาร์ดแวร์ของคุณเองแล้ว ต่อไปนี้คือสิ่งที่ควรทำต่อ:

1. **เชื่อมต่อแอปโปรดของคุณ**: Lemonade ทำงานได้ทันทีกับ [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) และ[อีกมากมาย](https://lemonade-server.ai/marketplace)

2. **ค้นหาโมเดลเพิ่มเติม**: สำรวจ[คลังโมเดล](https://lemonade-server.ai/docs/server/server_models/)ฉบับเต็มเพื่อค้นหาโมเดลที่ปรับให้เหมาะกับการเขียนโค้ด การให้เหตุผล การมองเห็น และอื่นๆ ใช้แอป Lemonade หรือ `lemonade list` เพื่อดูสิ่งที่มีให้ใช้งาน

3. **ปลดล็อกการเร่งความเร็วด้วย GPU ผ่าน ROCm**: หากคุณมี AMD GPU ที่รองรับ ให้สลับไปใช้แบ็กเอนด์ ROCm: `lemonade config set llamacpp.backend=rocm` ดู[AMD GPU ที่รองรับ](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)

4. **อ่านสเปก API ฉบับเต็ม**: Lemonade รองรับ chat completions, embeddings, การถอดความเสียง, การสร้างภาพ, การแปลงข้อความเป็นเสียง และอื่นๆ ดู[สเปกเซิร์ฟเวอร์](https://lemonade-server.ai/docs/server/server_spec/)สำหรับทุกเอ็นด์พอยท์

5. **ร่วมมีส่วนร่วม**: Lemonade เป็นโอเพนซอร์ส ดู[คู่มือการมีส่วนร่วม](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) และมองหา [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

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