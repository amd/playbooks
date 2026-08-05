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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> คู่มือนี้ต้องการหน่วยความจำระบบขั้นต่ำ **32GB**
<!-- @device:end -->

## ภาพรวม

Coding agent เป็นเครื่องมือที่ทรงพลังซึ่งช่วยให้นักพัฒนาทำงานร่วมกับ AI agent ที่ขับเคลื่อนด้วย Large Language Models (LLMs) ได้ โดยสามารถฝังเข้าไปในสภาพแวดล้อมการพัฒนา เช่น เทอร์มินัลหรือ VS Code ทำให้สามารถผสานเข้ากับขั้นตอนการทำงานของนักพัฒนาได้อย่างราบรื่น

บทช่วยสอนนี้สาธิตวิธีการใช้ Cline, VS Code และ LM Studio เพื่อรัน coding agent ทั้งหมดบนเครื่องของคุณเอง

## สิ่งที่คุณจะได้เรียนรู้

* วิธีการรัน VS Code ร่วมกับ coding agent Cline เพื่อช่วยในงานวิศวกรรมซอฟต์แวร์
* วิธีการกำหนดค่า Cline ให้สื่อสารกับ LM Studio สำหรับการอนุมาน (inference) แบบโลคัลของ coding agent
* วิธีการใช้ coding agent แบบโลคัลเพื่อแก้ปัญหางานวิศวกรรมซอฟต์แวร์ในโลกจริง

## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ผ่าน Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @require:lmstudio,vscode -->

## เปิดใช้งานและกำหนดค่า LM Studio

เราจะใช้ LM Studio เพื่อให้บริการ LLM ที่ขับเคลื่อน coding agent

- ในแถบค้นหา ค้นหา `LM Studio` และเปิดใช้งานแอปพลิเคชัน คุณจะเห็นหน้าจอต่อไปนี้

![LM Studio Initial Screen](assets/initial-lm-studio.png)

ต่อไป เราต้องโหลด LLM ลงในระบบ เราจะใช้โมเดล `Qwen3-Coder-30B-A3B` ที่มีความยาวบริบท (context length) ขนาดใหญ่ (ใช้แท็บ Model เพื่อติดตั้งหากยังไม่ได้ติดตั้ง)
- คลิกที่แถบค้นหาด้านบนของหน้าต่าง LM Studio หรือกดปุ่ม `CTRL+L` คลิกสวิตช์ `Manually choose model load parameters` จากนั้นคลิกที่โมเดล Qwen3-Coder-30B-A3B
- เปลี่ยนความยาวบริบทจาก `4096` เป็น `32768` และตรวจสอบให้แน่ใจว่า `GPU Offload` อยู่ที่ค่าสูงสุด จากนั้นคลิก `Load Model`

![Selecting Model](assets/model-list-zoomed.png)

เราใช้ความยาวบริบทขนาดใหญ่เพื่อให้ agent สามารถประมวลผลโค้ดเบสขนาดใหญ่และจดจำการเปลี่ยนแปลงที่เกิดขึ้นได้

![Configuring Model](assets/selecting-model-zoomed.png)

ต่อไป เราต้องเปิดใช้งาน LM Studio Server
- คลิกที่แท็บ Developer หรือกด `CTRL+2` ใน LM Studio ทางด้านซ้าย
- ตรวจสอบสวิตช์สถานะและให้แน่ใจว่าตั้งค่าเป็น `Running`

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![Server Status](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## เปิดใช้งานและกำหนดค่า VS Code

เราจะติดตั้งส่วนขยาย Cline ใน VS Code และเชื่อมต่อกับ LM Studio server ที่เราเพิ่งสร้างขึ้น
- ในแถบค้นหา ค้นหา `VS Code` และเปิดใช้งานแอปพลิเคชัน
- คลิกที่ไอคอน `Extensions` ในคอลัมน์ด้านซ้ายของ VS Code และค้นหา `Cline` จากนั้นคลิกปุ่ม `Install`

![Installing Cline Extension](assets/installing-cline-vscode-extension.png)

- ไอคอน Cline ควรปรากฏขึ้นทางด้านซ้าย คลิกที่ไอคอนนั้นเพื่อเปิด Cline จะมีหน้าต่างถามว่า `How will you use Cline?` เนื่องจากเราจะใช้ LLM แบบโลคัลที่รันผ่าน LM Studio ให้เลือก `Bring my own API Key` แล้วกด `Continue`

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Account Creation](assets/cline-how-will-you-use-cline-zoomed.png)

ต่อไป เราต้องกำหนดค่า Cline ให้สื่อสารกับ LM Studio server ที่เราตั้งค่าไว้
- ตั้งค่า API Provider เป็น `LM Studio` และโมเดลเป็น `Qwen3-Coder-30B-A3B-GGUF`

>**เคล็ดลับ**: อาจมีโมเดลใหม่กว่าให้เลือกใช้ พิจารณาดาวน์โหลดและเปลี่ยนไปใช้โมเดล Qwen3.6 หากต้องการ


![Model Configuration](assets/cline-model-configuration-zoomed.png)

## การสร้างโปรเจกต์แรกของคุณ

มาใช้ agent แบบโลคัลของเราสร้างเว็บไซต์กัน! เปิด VSCode ไปยังไดเรกทอรีที่คุณเลือกไว้ ซึ่ง Cline จะสร้างไฟล์ที่นั่น
- ในการทำเช่นนี้ ให้ไปที่ `File -> Open Folder` ที่มุมซ้ายบนของ VS Code และเลือกโฟลเดอร์ เช่น `Documents`

![VS Code Empty Folder](assets/open-cline-test.png)

ตอนนี้เราพร้อมที่จะป้อนคำสั่งให้ coding agent แบบโลคัลแล้ว
- คลิกที่ส่วนขยาย Cline ในคอลัมน์ด้านซ้ายและป้อนพรอมป์ต์เพื่อเริ่มการทำงานของ agent ตัวอย่างเช่น ลองใช้พรอมป์ต์ต่อไปนี้:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

จากนั้น agent จะเริ่มสร้างไฟล์ตามพรอมป์ต์ ในฐานะผู้ใช้ คุณสามารถดูโค้ดที่ถูกสร้างขึ้นใน VS Code ได้ดังภาพด้านล่าง คุณอาจต้องคลิก `Save` ทุกครั้งที่ Cline ต้องการสร้างไฟล์

![Cline Code Generation](assets/cline-code-generation.png)

หลังจากสร้างซอฟต์แวร์เสร็จแล้ว agent ก็เสร็จสิ้นการทำงาน และคุณสามารถรันแอปพลิเคชันได้ ในกรณีนี้ agent เขียนไฟล์สามไฟล์ ได้แก่ `index.html`, `script.js`, และ `styles.css` เพียงแค่ดับเบิลคลิกที่ไฟล์ HTML เราก็สามารถโหลดและโต้ตอบกับเว็บไซต์ที่สร้างขึ้นได้

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->
## ขั้นตอนถัดไป

หลังจากสร้างเว็บไซต์แล้ว คุณสามารถทำงานร่วมกับ Cline ต่อไปเพื่อปรับปรุงเว็บไซต์ให้ดียิ่งขึ้น การปรับปรุงที่เป็นไปได้สองอย่าง ได้แก่

- **เอกสารประกอบ**: การป้อนคำสั่งให้เอเจนต์ด้วย `Add a README` ก็เพียงพอแล้วที่จะทำให้เอเจนต์สร้างไฟล์ `README.md` ที่บันทึกรายละเอียดของเว็บไซต์
- **แอนิเมชัน**: ป้อนคำสั่งให้โมเดลด้วย `Add an animation that visually represents a large language model running on a laptop.` เพื่อสร้างแอนิเมชันลงในเว็บไซต์

เราขอสนับสนุนให้ผู้อ่านลองสร้างแอปพลิเคชันอื่น ๆ โดยใช้การตั้งค่านี้ ด้านล่างนี้คือตัวอย่างสนุก ๆ บางส่วนที่เราได้ลองทำ

- **เกมอาร์เคดย้อนยุค**: ลองใช้คำสั่งอื่น ๆ ดู นอกจากนี้ยังสนุกไม่น้อยหากให้เอเจนต์สร้างเกมสไตล์ย้อนยุคด้วยภาษา Python โดยใช้แพ็กเกจ `PyGame` ด้วยคำสั่งดังต่อไปนี้:

```code
Create a simple pong game using the PyGame python package.
```

- **การวิเคราะห์ข้อมูล**: หนึ่งในด้านที่เอเจนต์เขียนโค้ดมีประโยชน์อย่างมากคือการเขียนสคริปต์และการวิเคราะห์ข้อมูล นี่คือคำสั่งที่แสดงให้เห็นถึงความสามารถของโมเดลท้องถิ่นในการสร้างซอฟต์แวร์วิเคราะห์ข้อมูลสำหรับการแสดงผลราคาหุ้น:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## แหล่งข้อมูลอ้างอิง

ด้านล่างนี้คือแหล่งข้อมูลเพิ่มเติมเพื่อเรียนรู้เกี่ยวกับ Coding Agents, Cline และการรันเวิร์กโหลดบน 

* ข้อมูลเพิ่มเติมเกี่ยวกับความร่วมมือและการผสานรวมระหว่าง AMD กับ LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* บล็อกของ AMD ที่พาไปทำความรู้จักกับการรัน Cline บนการ์ด AMD Ryzen™ AI และ Radeon™ Graphics: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* บล็อกของ Cline เกี่ยวกับการรันเอเจนต์เขียนโค้ดในเครื่องบน AI PC: https://cline.bot/blog/local-models-amd