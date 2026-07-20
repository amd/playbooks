<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> เพลย์บุ๊กนี้ใช้แท็กพิเศษที่ GitHub ไม่สามารถแสดงผลได้ กรุณาไปที่ [amd.com/playbooks](https://amd.com/playbooks) เพื่อดูตัวอย่างเนื้อหานี้อย่างถูกต้อง
<!-- @github-only:end -->

## ภาพรวม

🍋 **Lemonade** คือเซิร์ฟเวอร์ AI ท้องถิ่นแบบโอเพนซอร์สที่ให้คุณรันโมเดลภาษาขนาดใหญ่ (LLM) เครื่องมือสร้างภาพ และโมเดลเสียงได้โดยตรงบนฮาร์ดแวร์ของคุณเอง โดยเปิดให้เข้าถึงโมเดลเหล่านี้ผ่าน **OpenAI API** ซึ่งเป็นมาตรฐานในอุตสาหกรรม ดังนั้นแอปพลิเคชันใดก็ตามที่ใช้งานร่วมกับ OpenAI ได้ก็จะสามารถใช้งานร่วมกับ Lemonade ได้ทันที เมื่อจบเพลย์บุ๊กนี้ คุณจะได้ใช้ Lemonade เพื่อรันโมเดลต่าง ๆ บนเครื่องของคุณเอง

## สิ่งที่คุณจะได้เรียนรู้

เมื่อจบเพลย์บุ๊กนี้ คุณจะสามารถ:

* **ติดตั้ง Lemonade Server** และตรวจสอบว่ากำลังทำงานอยู่
* **ดาวน์โหลดและสนทนากับ LLM** ด้วยคำสั่งเพียงคำสั่งเดียว
* **สำรวจเว็บ UI** และทดลองใช้โหมดต่าง ๆ เช่น การมองเห็น (vision) การแปลงเสียงเป็นข้อความ (speech-to-text) และการสร้างภาพ
* **สลับแบ็กเอนด์ของ GPU** ระหว่าง Vulkan และซอฟต์แวร์ AMD ROCm™
* **สร้างแอป Python** ที่ขับเคลื่อนด้วย LLM ท้องถิ่นโดยใช้ API ที่เข้ากันได้กับ OpenAI
<!-- @device:halo_box,halo,stx,krk -->
* **รันโมเดลบน AMD Neural Processing Unit (NPU)** โดยใช้โหมดการทำงานแบบ Hybrid และ FLM บนฮาร์ดแวร์ AMD Ryzen™ AI
<!-- @device:end -->

## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

ก่อนเริ่มต้น โปรดตรวจสอบให้แน่ใจว่าคุณมี:

- พีซีที่รัน **Windows 11** หรือดิสทริบิวชัน **Linux** ที่รองรับ (Ubuntu 24.04+, Fedora, Debian)
- แนะนำ **RAM 16 GB** สำหรับโมเดลรันไทม์ที่ใช้ในขั้นตอนที่ 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB) แนะนำ **32 GB ขึ้นไป** หากคุณต้องการใช้โมเดลสร้างโค้ดขนาดใหญ่กว่าในขั้นตอนที่ 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB)
- **พื้นที่ว่างในดิสก์ประมาณ 4–30 GB** ขึ้นอยู่กับโมเดลที่คุณดาวน์โหลด โมเดลที่ใหญ่ที่สุดในคู่มือนี้มีขนาดประมาณ 20 GB
- **Python 3.10–3.13** (ใช้ในส่วนแอป Python)
- การเชื่อมต่ออินเทอร์เน็ต (แบบมีสายหรือไร้สาย)
<!-- @device:halo_box,halo,stx,krk -->
- [ทางเลือกเสริม] AMD XDNA 2 NPU (ซีรีส์ Ryzen AI 300/400/Max 300 หรือ Z2 Extreme) พร้อมไดรเวอร์ล่าสุดที่ติดตั้งจาก [คำแนะนำการติดตั้งซอฟต์แวร์ Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) หากคุณต้องการรันโมเดลบน NPU
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

## แนวคิดหลัก — เซิร์ฟเวอร์ AI ท้องถิ่นทำงานอย่างไร

ก่อนที่เราจะรันโมเดล ควรทำความเข้าใจก่อนว่า *ทำไม* จึงมีการตั้งค่าในลักษณะนี้ Lemonade คือ **เซิร์ฟเวอร์โมเดลท้องถิ่น (local model server)** ซึ่งเป็นโพรเซสที่โหลดโมเดล AI เข้าสู่หน่วยความจำและเปิดให้แอปพลิเคชันต่าง ๆ เข้าถึงได้ผ่าน HTTP เช่นเดียวกับบริการ AI บนคลาวด์

### ทำไมต้องเป็นเซิร์ฟเวอร์?

| ประโยชน์ | สิ่งนี้หมายถึงอะไรสำหรับคุณ |
|---------|----------------------|
| **การผสานรวมที่ง่ายขึ้น** | แอปพลิเคชันสื่อสารผ่าน HTTP API เดียว แทนที่จะต้องจัดการกับไลบรารี C++ หรือ Python ที่เฉพาะเจาะจงกับฮาร์ดแวร์ |
| **การใช้โมเดลร่วมกัน** | โมเดลที่โหลดไว้เพียงตัวเดียวสามารถให้บริการหลายแอปพลิเคชันพร้อมกันได้ โดยไม่ต้องมีสำเนาซ้ำซ้อนที่กิน RAM ของคุณ |
| **ความสามารถในการย้ายระหว่างคลาวด์กับท้องถิ่น** | โค้ดที่เขียนสำหรับ API บนคลาวด์ของ OpenAI สามารถทำงานร่วมกับ Lemonade ได้เพียงแค่เปลี่ยน URL เดียว |
| **การแยกส่วนความรับผิดชอบ** | การจัดการโมเดล การสตรีมข้อมูล และการทนต่อความผิดพลาดจะถูกจัดการโดยเซิร์ฟเวอร์ เพื่อให้นักพัฒนาสามารถโฟกัสที่แอปพลิเคชันของตนเองได้ |

### มาตรฐาน OpenAI API

Lemonade นำมาตรฐาน **OpenAI API** มาใช้ ซึ่งเป็นอินเทอร์เฟซเดียวกับที่ใช้ใน ChatGPT, Azure OpenAI และบริการอื่น ๆ อีกหลายสิบบริการ โมเดลการสนทนามีความเรียบง่าย ดังนี้:

| บทบาท | ใครเป็นผู้พูด |
|------|---------------|
| **system** | คำสั่งที่ให้กับโมเดล (บุคลิก ข้อจำกัด เครื่องมือที่ใช้งานได้) |
| **user** | ข้อความจากมนุษย์ (หรือแอปพลิเคชัน) ถึงโมเดล |
| **assistant** | คำตอบที่สร้างขึ้นโดยโมเดล |

ซึ่งหมายความว่าไลบรารีหรือแอปพลิเคชันใดก็ตามที่รองรับ OpenAI สามารถสื่อสารกับ Lemonade ได้ โดยชี้ไปที่ `http://localhost:13305/api/v1` ในขณะที่ Lemonade Server กำลังทำงานอยู่

## กิจกรรมหลัก — การสนทนา AI ท้องถิ่นครั้งแรกของคุณ

มาดาวน์โหลด LLM และเริ่มสนทนากับมันกัน โดยรัน AI ทั้งหมดบนเครื่องของคุณเอง

### ขั้นตอนที่ 1: ดาวน์โหลดและรันโมเดล

Lemonade มาพร้อมกับไลบรารีโมเดลที่คัดสรรไว้แล้ว เริ่มต้นด้วย **Gemma-4-E2B-it** ซึ่งเป็นโมเดลที่มีความสามารถและมีขนาดกะทัดรัด รวมถึงรองรับการมองเห็น (vision) ด้วย เปิดเทอร์มินัลและรัน:

```
lemonade run Gemma-4-E2B-it-GGUF
```

คำสั่งเดียวนี้ทำสามสิ่ง:

1. **ดาวน์โหลด** โมเดล (~3 GB) จาก Hugging Face หากยังไม่เคยดาวน์โหลดมาก่อน (อาจใช้เวลาสักครู่)
2. **เริ่มต้น** โพรเซส Lemonade Server บนพอร์ต 13305
3. **เปิด Lemonade App** เพื่อให้คุณเริ่มสนทนากับโมเดลได้


<!-- @os:windows -->
บน Windows, Lemonade App จะเปิดขึ้นโดยอัตโนมัติและคุณสามารถเริ่มสนทนาได้ทันที หากคุณติดตั้งแพ็กเกจ `minimal.msi` แอปนี้จะไม่รวมอยู่ด้วย หากต้องการเริ่มสนทนา ให้เปิดเว็บเบราว์เซอร์และไปที่ `http://localhost:13305`
<!-- @os:end -->

<!-- @os:linux -->
บน Linux ให้เปิดเบราว์เซอร์และไปที่ `http://localhost:13305` เพื่อเข้าถึงเว็บแอป
<!-- @os:end -->

ลองพิมพ์คำถาม:

```
What are three fun facts about lemons?
```

โมเดลจะตอบกลับโดยตรงในหน้าต่างแชท **ยินดีด้วย! คุณกำลังรันโมเดลภาษาขนาดใหญ่บนเครื่องของคุณเองแล้ว**

![Lemonade App with Logs displayed](../../dependencies/assets/ChatwithLogs.png)

ในแผง Server Logs ของ Lemonade App คุณจะพบข้อมูลการวัดประสิทธิภาพ (telemetry) เกี่ยวกับประสิทธิภาพของโมเดลหลังจากแต่ละการตอบกลับ ตัวอย่างเช่น:

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

- **โต้ตอบ** กับโมเดลที่โหลดไว้ผ่านหน้าต่างแชทที่คุ้นเคย
- **เรียกดูโมเดล** ในแท็บ Model Manager
- **ดาวน์โหลดโมเดลใหม่** ได้ในคลิกเดียว

ลองสลับไปมาระหว่างโหมดการทำงานต่าง ๆ โดยใช้แท็บ **Model Manager** ในเว็บ UI ซึ่งคุณสามารถเรียกดูโมเดลตาม Recipe หรือตาม Category ได้

1. **Vision:** โมเดล `Gemma-4-E2B-it-GGUF` ที่คุณโหลดไว้แล้วรองรับการมองเห็น (vision) ลองวางรูปภาพลงในกล่องแชทและขอให้โมเดลอธิบายรูปภาพนั้น
2. **การสร้างภาพ:** ในหมวด Image ให้ดาวน์โหลดโมเดลสร้างภาพ เช่น `SDXL-Turbo` จาก Model Manager จากนั้นใช้ Lemonade Image Generator เพื่อพิมพ์พรอมต์และสร้างภาพในเครื่องของคุณเอง
3. **เสียง:** ในหมวด Audio ให้ดาวน์โหลดโมเดลเสียง เช่น `Whisper-Tiny` ซึ่งสามารถแปลงเสียงพูดเป็นข้อความได้ ลองป้อนไฟล์เสียงเพื่อถอดความในเครื่องของคุณเอง สำหรับการแปลงข้อความเป็นเสียงพูด ให้ลองใช้โมเดลในหมวด Speech เช่น `kokoro-v1`

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### ขั้นตอนที่ 3: ลองใช้โมเดลกับ Backend ที่ต่างกัน

หากคุณเลื่อนเมาส์ไปวางบนโมเดลใน Lemonade App คุณจะเห็นไอคอนรูปเฟือง เมื่อคลิกที่ไอคอนนี้จะทำให้คุณสามารถเลือกตัวเลือกต่าง ๆ สำหรับโมเดลได้ รวมถึงการเลือก backend ที่ต้องการ

โดยค่าเริ่มต้น Lemonade จะใช้ Vulkan สำหรับการเร่งความเร็วด้วย GPU หากคุณมี AMD discrete GPU ที่รองรับ คุณสามารถเปลี่ยนไปใช้ ROCm ได้

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

หากต้องการจัดการ backend ที่ติดตั้งไว้ ให้คลิกปุ่ม backend ในคอลัมน์ซ้ายสุด

หรืออีกทางหนึ่ง คุณสามารถระบุ backend ได้โดยใช้คำสั่งต่อไปนี้:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

คุณยังสามารถตั้งค่า backend เริ่มต้นได้โดยใช้ตัวแปรสภาพแวดล้อม `LEMONADE_LLAMACPP` โดยมีค่าที่เป็นไปได้คือ `vulkan`, `rocm`, หรือ `cpu`

---

## เจาะลึกยิ่งขึ้น — สร้างแอปพลิเคชัน AI ด้วย Python

พลังที่แท้จริงของเซิร์ฟเวอร์ AI แบบโลคัลคือแอปพลิเคชันใด ๆ ก็สามารถเชื่อมต่อกับมันได้ด้วยโค้ดเพียงไม่กี่บรรทัด เพื่อพิสูจน์เรื่องนี้ เรามาสร้าง **แอปสร้างการ์ดคำศัพท์สำหรับทบทวนบทเรียน (study flashcard generator)** ขนาดเล็กแต่ใช้งานได้จริงกัน โดยคุณกำหนดหัวข้อ แอปจะสร้างการ์ดคำศัพท์ให้ และคุณสามารถทดสอบตัวเองแบบโต้ตอบได้

### ขั้นตอนที่ 4: เริ่มต้นเซิร์ฟเวอร์

ตรวจสอบให้แน่ใจว่าเซิร์ฟเวอร์ Lemonade กำลังทำงานอยู่ โดยปกติแล้วเซิร์ฟเวอร์จะเริ่มทำงานโดยอัตโนมัติในพื้นหลังหลังการติดตั้ง หากต้องการตรวจสอบ ให้รันคำสั่ง:

```
lemonade status
```

คุณควรเห็นข้อความคล้ายกับ: `Server is running on port 13305`

หากเซิร์ฟเวอร์ยังไม่ได้ทำงาน ให้เริ่มต้นโดยการเปิดแอป Lemonade ใช้พอร์ตเริ่มต้น **13305** (คุณสามารถยืนยันหรือเลือกพอร์ตนี้ได้จากไอคอนบนถาดระบบ)

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

### ขั้นตอนที่ 6: สร้างแอปการ์ดคำศัพท์

มาดาวน์โหลดโมเดลอื่นเพื่อสร้างโค้ดกัน: `Qwen3.5-35B-A3B-GGUF` นี่คือโมเดลขนาดใหญ่ (~20 GB) และมีประสิทธิภาพสูง เหมาะที่สุดสำหรับระบบที่มี RAM 32 GB ขึ้นไป หากคุณมี RAM ว่างน้อยกว่านี้ ให้ลองใช้ `Qwen3.5-9B-GGUF` (~6 GB) แทน

คุณสามารถดาวน์โหลดได้จาก UI หรือรันคำสั่งต่อไปนี้:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

ป้อนพรอมต์ต่อไปนี้ลงใน Lemonade Chat UI เพื่อสร้างโค้ดสำหรับแอป Flashcard แบบง่าย ๆ

เราจะใช้ Qwen3.5-35B-A3B-GGUF (โมเดลขนาดใหญ่ที่เขียนโค้ดได้ดีกว่า) เพื่อสร้างแอป Python ของเรา และตัวแอปเองจะเรียกใช้ Gemma-4-E2B-it-GGUF (โมเดลขนาดเล็กที่คุณดาวน์โหลดไว้แล้ว) ในขณะรันไทม์ จากนั้นสามารถคัดลอกโค้ดไปยังไฟล์ที่คุณเลือกเพื่อรันใน Python ได้

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

> **เคล็ดลับ**: เราได้ปฏิบัติตามแนวทางวิศวกรรมมาตรฐานโดยการสร้างพรอมต์อย่างละเอียดถี่ถ้วนและใช้ระบบสองโมเดลเพื่อเพิ่มประสิทธิภาพการใช้ทรัพยากรและความเร็ว

เพื่อความสะดวกของคุณ เราได้จัดเตรียมตัวอย่างผลลัพธ์ไว้ใน [`flashcards.py`](assets/flashcards.py) แล้ว สามารถดาวน์โหลดไปไว้ในไดเรกทอรีของคุณได้ตามสะดวก ไม่ว่ากรณีใด ตอนนี้คุณควรมีไฟล์ Python ที่พร้อมรันได้แล้ว

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

**นี่คือสิ่งที่คุณควรจะเห็น:**

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

ด้วยโค้ดประมาณ 150 บรรทัด คุณได้สร้างเครื่องมือช่วยทบทวนบทเรียนที่ใช้งานได้เต็มรูปแบบซึ่งขับเคลื่อนด้วย LLM แบบโลคัล โดยไม่ต้องจัดการ API key ไม่มีค่าใช้จ่ายในการใช้งาน และไม่มีข้อมูลใด ๆ ออกจากเครื่องของคุณเลย

> **ข้อคิดสำคัญ:** สังเกตว่าบรรทัด `client = OpenAI(base_url=...) ` เป็นสิ่ง*เดียว*ที่เชื่อมโยงแอปนี้เข้ากับ Lemonade แทนที่จะเป็นคลาวด์ของ OpenAI ส่วนที่เหลือของโค้ดเหมือนกันทุกประการกับที่คุณจะเขียนเพื่อใช้กับบริการที่เข้ากันได้กับ OpenAI ใด ๆ หากคุณเคยใช้ไลบรารี OpenAI Python มาก่อน คุณก็รู้วิธีสร้างแอปด้วย Lemonade อยู่แล้ว

### สิ่งที่การสาธิตนี้แสดงให้เห็น

แอปเล็ก ๆ นี้แสดงให้เห็นรูปแบบการผสานรวมที่ใช้จริงหลายรูปแบบ:

| รูปแบบ | จุดที่ปรากฏ |
|---------|-----------------|
| **System prompts** | ข้อความ `"system"` บอกให้ LLM แสดงผลลัพธ์เป็น JSON แบบมีโครงสร้าง |
| **ผลลัพธ์แบบมีโครงสร้าง** | แอปแปลงคำตอบของ LLM เป็น JSON เพื่อสร้างการ์ดคำศัพท์ |
| **คำขอแบบ Stateless** | การเรียก `generate_flashcards()` แต่ละครั้งเป็นอิสระต่อกัน |
| **การจัดการข้อผิดพลาด** | `try/except` จัดการกรณีที่ผลลัพธ์ของ LLM ไม่ใช่ JSON ที่ถูกต้องได้อย่างราบรื่น |

รูปแบบเดียวกันนี้สามารถนำไปประยุกต์ใช้กับแอปพลิเคชันใด ๆ ได้ เช่น แชทบอท ผู้ช่วยเขียนโค้ด เครื่องมือสร้างเนื้อหา และเครื่องมืออัตโนมัติต่าง ๆ

#### ความท้าทายพิเศษ

* หากต้องการความท้าทายเพิ่มเติม ลองปรับปรุงแอปให้อ่านการ์ดคำศัพท์ให้ผู้ใช้ฟังได้ โดยอ้างอิงจากตัวอย่างที่ให้ไว้ [ที่นี่](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)

---

<!-- @device:halo_box,halo,stx,krk -->
## การรันโมเดลบน NPU (ทางเลือกเสริม)

หากคุณมี Ryzen AI 300/400/Max 300 series หรือ Z2 Extreme อุปกรณ์ของคุณจะมี **หน่วยประมวลผลประสาทเทียม (Neural Processing Unit - NPU)** ในตัว ซึ่งเป็นชิปเฉพาะที่ออกแบบมาสำหรับงาน AI โดยเฉพาะ การรันโมเดลบน NPU จะประหยัดพลังงานมากกว่าการใช้ GPU ทำให้เหมาะสำหรับงาน AI ที่ทำงานเบื้องหลัง เซสชันที่ใช้เวลานาน และการใช้งานบนแบตเตอรี่

Lemonade รองรับโหมดการทำงานของ NPU สามแบบ โดยทั้งหมดทำงานอย่างโปร่งใสผ่าน OpenAI API เดียวกัน:

| โหมด | วิธีการทำงาน | Recipe | ตัวอย่างโมเดล |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU ประมวลผลพรอมป์ iGPU สร้างโทเค็น | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU-only** | การอนุมานทั้งหมดทำงานบน NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | ใช้เอนจิน FastFlowLM บน NPU ที่ปรับให้เหมาะกับ AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### ข้อกำหนด

- โปรเซสเซอร์ **AMD Ryzen AI 300/400 series หรือ Z2 series**
- สำหรับโมเดล **FLM**: สามารถติดตั้งรันไทม์ FLM ได้จากภายในแอป Lemonade หรือ Lemonade จะติดตั้งรันไทม์ FLM ให้โดยอัตโนมัติเมื่อรันโมเดล FLM หากต้องการเรียนรู้เพิ่มเติมเกี่ยวกับ FastFlowLM ดูได้ [ที่นี่](https://fastflowlm.com/docs/)


### ขั้นตอนที่ 8: รันโมเดล Hybrid

โมเดล Hybrid จะแบ่งงานระหว่าง NPU และ iGPU เพื่อความสมดุลที่ดีระหว่างความเร็วและประสิทธิภาพการใช้พลังงาน ในแอป Lemonade ให้เลือกโมเดลจากรายการ `Ryzen AI LLM` เช่น `Qwen3-4B-Hybrid` หรือรันโดยใช้คำสั่งต่อไปนี้:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade จะตรวจจับ NPU ของคุณโดยอัตโนมัติและติดตั้งแบ็กเอนด์ **Ryzen AI LLM**

> **สิ่งที่เกิดขึ้นเบื้องหลัง?** เมื่อคุณส่งข้อความ NPU จะประมวลผลพรอมป์ทั้งหมดของคุณแบบขนาน (เรียกว่า "prefill") จากนั้น iGPU จะรับช่วงต่อในการสร้างคำตอบทีละโทเค็น (เรียกว่า "decode") วิธีการแบบ Hybrid นี้ใช้จุดแข็งของแต่ละชิปอย่างเต็มที่

### ขั้นตอนที่ 9: รันโมเดล FLM

โมเดล FastFlowLM (FLM) ได้รับการปรับให้เหมาะสมสำหรับสถาปัตยกรรม NPU ของ AMD XDNA2 โดยเฉพาะ และสามารถทำงานได้รวดเร็วมากเมื่อเทียบกับขนาด ตัวอย่างเช่น เลือก `qwen3.5-4b-FLM` จากรายการ `FastFlowLM NPU` หรือใช้คำสั่งต่อไปนี้:

<!-- @os:windows -->
วิธีเปิดใช้งาน `FastFlowLM` บน Windows:

* เปิดเมนู `Backends Manager`
* หาหมวดหมู่แบ็กเอนด์ `FastFlowLM NPU`
* คลิก Install NPU
* เมื่อการติดตั้งเสร็จสมบูรณ์ โมเดลเริ่มต้นประมาณ 36 โมเดลจะพร้อมใช้งานภายใต้เมนูดรอปดาวน์ FFLM
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
เมื่อเปิดแอป `Lemonade` ครั้งแรก แบ็กเอนด์ `FastFlowNPU` จะไม่ถูกเปิดใช้งานโดยค่าเริ่มต้น
แอปในเครื่องจะเปิดหน้าการติดตั้งเพื่อแนะนำคุณตลอดขั้นตอนการตั้งค่า

วิธีเปิดใช้งาน `FastFlowLM` บน Linux:

* เปิดแอป `Lemonade`
* เยี่ยมชมเอกสาร [official FLM](https://lemonade-server.ai/flm_npu_linux.html) และทำตามขั้นตอนการติดตั้งสำหรับ FLM โดยเลือกดิสโทร Linux ของคุณ
* เปิดใช้งาน backports ตามที่ระบุไว้ในหน้าการติดตั้ง
* ดาวน์โหลดรุ่น `v0.9.x` ล่าสุดจาก [tags page](https://github.com/FastFlowLM/FastFlowLM/tags)'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
สำหรับ AMD Halo Developer Platform โปรดเลือก Debian 13
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
* แนะนำ: ปิดแอป `Lemonade App` แล้วเปิดใหม่อีกครั้งเพื่อให้ตรวจพบการเปลี่ยนแปลง
* แนะนำ: เปิด `Backends Manager` แล้วคลิกติดตั้งแบ็กเอนด์ `FastFlowNPU`
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
หลังจากติดตั้งสำเร็จ คุณควรเห็นว่า `flm:npu` เสร็จสมบูรณ์ใน **Download Manager** ภายใน **Lemonade Desktop App**
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
จากนั้นคุณสามารถเลือกโมเดล FFLM ที่มีอยู่และเริ่มใช้งานแบ็กเอนด์ NPU ได้

สำหรับโมเดลเฉพาะ ให้ดาวน์โหลดโมเดลที่ต้องการจาก [models page](https://fastflowlm.com/docs/models/qwen/) และตรวจสอบความถูกต้องโดยใช้คำสั่ง Shell ที่ระบุไว้ในเอกสาร
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

แอปแฟลชการ์ดจากขั้นตอนที่ 6 ก็ทำงานกับโมเดล NPU ได้เช่นกัน เพียงเปลี่ยนชื่อโมเดล:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## ขั้นตอนถัดไป

ตอนนี้คุณมีเซิร์ฟเวอร์ AI ที่ทำงานบนฮาร์ดแวร์ของคุณเองแล้ว นี่คือสิ่งที่ควรทำต่อไป:

1. **เชื่อมต่อแอปโปรดของคุณ**: Lemonade ทำงานได้ทันทีร่วมกับ [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) และ [อื่นๆ อีกมากมาย](https://lemonade-server.ai/marketplace)

2. **สำรวจโมเดลเพิ่มเติม**: สำรวจ [ไลบรารีโมเดล](https://lemonade-server.ai/docs/server/server_models/) แบบเต็มเพื่อค้นหาโมเดลที่ปรับให้เหมาะกับการเขียนโค้ด การให้เหตุผล การมองเห็นภาพ และอื่นๆ ใช้แอป Lemonade หรือคำสั่ง `lemonade list` เพื่อดูสิ่งที่มีให้ใช้งาน

3. **ปลดล็อกการเร่งความเร็วด้วย ROCm GPU**: หากคุณมี AMD GPU ที่รองรับ ให้เปลี่ยนไปใช้แบ็กเอนด์ ROCm: `lemonade config set llamacpp.backend=rocm` ดู [AMD GPU ที่รองรับ](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)

4. **อ่านข้อกำหนด API แบบเต็ม**: Lemonade รองรับ chat completions, embeddings, การถอดเสียงเป็นข้อความ, การสร้างภาพ, การแปลงข้อความเป็นเสียง และอื่นๆ ดู [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) สำหรับทุกเอนด์พอยต์

5. **ร่วมสนับสนุน**: Lemonade เป็นโอเพนซอร์ส ลองดู [คู่มือการร่วมสนับสนุน](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) และมองหา [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)