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

Coding agents เป็นเครื่องมือที่ทรงพลังซึ่งช่วยเสริมศักยภาพให้นักพัฒนาผ่านการทำงานร่วมกับ AI agents ที่ขับเคลื่อนด้วย Large Language Models (LLMs) โดยสามารถฝังเข้าไปในสภาพแวดล้อมการพัฒนา เช่น เทอร์มินัลหรือ VS Code ทำให้สามารถผสานรวมเข้ากับขั้นตอนการทำงานของนักพัฒนาได้อย่างราบรื่น

บทแนะนำนี้สาธิตวิธีการใช้ Cline, VS Code และ LM Studio เพื่อรัน coding agent ทั้งหมดบนเครื่องของคุณเอง

## สิ่งที่คุณจะได้เรียนรู้

* วิธีรัน VS Code ร่วมกับ coding agent ของ Cline เพื่อช่วยในงานด้านวิศวกรรมซอฟต์แวร์
* วิธีกำหนดค่า Cline ให้สื่อสารกับ LM Studio สำหรับการอนุมาน (inference) coding agents แบบ local
* วิธีใช้ local coding agents เพื่อแก้ปัญหางานวิศวกรรมซอฟต์แวร์ในโลกจริง

<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ผ่าน Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lmstudio,vscode -->
<!-- @prereq:lmstudio-models-qwen3-coder-30b -->

## เปิดและกำหนดค่า LM Studio

เราจะใช้ LM Studio เพื่อให้บริการ LLM ที่ขับเคลื่อน coding agent

- ในแถบค้นหา ค้นหา `LM Studio` แล้วเปิดแอปพลิเคชัน คุณจะพบหน้าจอดังต่อไปนี้

![หน้าจอเริ่มต้นของ LM Studio](assets/initial-lm-studio.png)

ต่อไป เราต้องโหลด LLM ลงในระบบ เราจะใช้โมเดล `Qwen3-Coder-30B-A3B` ที่มีความยาว context ขนาดใหญ่ (ใช้แท็บ Model เพื่อติดตั้งหากยังไม่ได้ติดตั้ง)
- คลิกที่แถบค้นหาด้านบนของหน้าต่าง LM Studio หรือกด `CTRL+L` คลิกสวิตช์ `Manually choose model load parameters` จากนั้นคลิกที่โมเดล Qwen3-Coder-30B-A3B
- เปลี่ยนความยาว context จาก `4096` เป็น `32768` และตรวจสอบให้แน่ใจว่า `GPU Offload` อยู่ที่ค่าสูงสุด จากนั้นคลิก `Load Model`

![การเลือกโมเดล](assets/model-list-zoomed.png)

เราใช้ความยาว context ขนาดใหญ่เพื่อให้ agent สามารถประมวลผล codebase ขนาดใหญ่และจดจำการเปลี่ยนแปลงที่เกิดขึ้นได้

![การกำหนดค่าโมเดล](assets/selecting-model-zoomed.png)

ต่อไป เราต้องเปิดใช้งาน LM Studio Server
- คลิกแท็บ Developer หรือกด `CTRL+2` ใน LM Studio ทางด้านซ้าย
- ตรวจสอบสวิตช์สถานะและตรวจให้แน่ใจว่าตั้งค่าเป็น `Running`

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

![สถานะของเซิร์ฟเวอร์](assets/lm-studio-server-status.png)

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

## เปิดและกำหนดค่า VS Code

เราจะติดตั้งส่วนขยาย Cline ใน VS Code และเชื่อมต่อกับเซิร์ฟเวอร์ LM Studio ที่เราเพิ่งสร้างขึ้น
- ในแถบค้นหา ค้นหา `VS Code` แล้วเปิดแอปพลิเคชัน
- คลิกไอคอน `Extensions` ที่คอลัมน์ด้านซ้ายของ VS Code และค้นหา `Cline` จากนั้นคลิกปุ่ม `Install`

![การติดตั้งส่วนขยาย Cline](assets/installing-cline-vscode-extension.png)

- ควรมีไอคอน Cline ปรากฏอยู่ทางด้านซ้าย คลิกที่ไอคอนนั้นเพื่อเปิด Cline จะมีหน้าต่างถามว่า `How will you use Cline?` เนื่องจากเราจะใช้ local LLM ที่รันผ่าน LM Studio ให้เลือก `Bring my own API Key` แล้วกด `Continue`

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

![การสร้างบัญชี](assets/cline-how-will-you-use-cline-zoomed.png)

ต่อไป เราต้องกำหนดค่า Cline ให้สื่อสารกับเซิร์ฟเวอร์ LM Studio ที่เราตั้งค่าไว้
- ตั้งค่า API Provider เป็น `LM Studio` และโมเดลเป็น `Qwen3-Coder-30B-A3B-GGUF`

>**เคล็ดลับ**: อาจมีโมเดลใหม่กว่านี้ให้ใช้งาน ลองพิจารณาดาวน์โหลดและเปลี่ยนไปใช้โมเดล Qwen3.6 หากต้องการ


![การกำหนดค่าโมเดล](assets/cline-model-configuration-zoomed.png)

## การสร้างโปรเจกต์แรกของคุณ

มาลองใช้ local agent ของเราในการสร้างเว็บไซต์กันเถอะ! เปิด VSCode ไปยังไดเรกทอรีที่คุณเลือกซึ่ง Cline จะสร้างไฟล์ไว้
- ในการทำเช่นนี้ ไปที่ `File -> Open Folder` ที่มุมบนซ้ายของ VS Code และเลือกโฟลเดอร์ เช่น `Documents`

![โฟลเดอร์ว่างใน VS Code](assets/open-cline-test.png)

ตอนนี้เราพร้อมที่จะป้อนคำสั่งให้ local coding agent แล้ว
- คลิกที่ส่วนขยาย Cline ที่คอลัมน์ด้านซ้ายและป้อนพรอมป์ต์เพื่อเริ่ม agent ตัวอย่างเช่น ลองใช้พรอมป์ต์ต่อไปนี้:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

จากนั้น agent จะเริ่มสร้างไฟล์ตามพรอมป์ต์ ในฐานะผู้ใช้ คุณสามารถดูโค้ดถูกสร้างขึ้นใน VS Code ได้ดังที่แสดงด้านล่าง คุณอาจต้องคลิก `Save` ทุกครั้งที่ Cline ต้องการสร้างไฟล์

![การสร้างโค้ดของ Cline](assets/cline-code-generation.png)

หลังจากสร้างซอฟต์แวร์เสร็จแล้ว agent ก็เสร็จสมบูรณ์และคุณสามารถรันแอปพลิเคชันได้ ในกรณีนี้ agent ได้เขียนไฟล์สามไฟล์: `index.html`, `script.js` และ `styles.css` เพียงแค่ดับเบิลคลิกที่ไฟล์ HTML เราก็สามารถโหลดและโต้ตอบกับเว็บไซต์ที่สร้างขึ้นได้

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

หลังจากสร้างเว็บไซต์แล้ว คุณสามารถทำงานกับ Cline ต่อเพื่อปรับปรุงเว็บไซต์ได้ มีการปรับปรุงที่เป็นไปได้สองอย่าง ได้แก่:

- **เอกสารประกอบ**: เพียงป้อนพรอมป์ต์ให้ agent ด้วย `Add a README` ก็เพียงพอให้ agent สร้างไฟล์ `README.md` ที่บันทึกเอกสารเกี่ยวกับเว็บไซต์
- **แอนิเมชัน**: ป้อนพรอมป์ต์ให้โมเดลด้วย `Add an animation that visually represents a large language model running on a laptop.` เพื่อสร้างแอนิเมชันเพิ่มเข้าไปในเว็บไซต์

เราขอสนับสนุนให้ผู้อ่านลองสร้างแอปพลิเคชันอื่นๆ โดยใช้การตั้งค่านี้ ด้านล่างนี้เป็นตัวอย่างสนุกๆ ที่เราได้ลองทำ:

- **เกมอาร์เคดสไตล์เรโทร**: ลองใช้พรอมป์ต์อื่นๆ ดู นอกจากนี้ยังสนุกไม่น้อยที่ให้ agent สร้างเกมสไตล์เรโทรด้วย Python โดยใช้แพ็กเกจ `PyGame` ด้วยพรอมป์ต์ต่อไปนี้:

```code
Create a simple pong game using the PyGame python package.
```

- **การวิเคราะห์ข้อมูล**: หนึ่งในด้านที่ coding agents มีประโยชน์เป็นพิเศษคือการเขียนสคริปต์และการวิเคราะห์ข้อมูล นี่คือพรอมป์ต์ที่แสดงให้เห็นความสามารถของ local model ในการสร้างซอฟต์แวร์วิเคราะห์ข้อมูลสำหรับการแสดงผลราคาหุ้น:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## แหล่งข้อมูล

ด้านล่างนี้คือแหล่งข้อมูลเพิ่มเติมสำหรับเรียนรู้เกี่ยวกับ Coding Agents, Cline และการรันเวิร์กโหลดบน 

* ข้อมูลเพิ่มเติมเกี่ยวกับความร่วมมือและการผสานรวมระหว่าง AMD กับ LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* บล็อกของ AMD ที่อธิบายขั้นตอนการรัน Cline บนการ์ด AMD Ryzen™ AI และ Radeon™ Graphics: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* บล็อกของ Cline เกี่ยวกับการรัน coding agents แบบโลคัลบน AI PC: https://cline.bot/blog/local-models-amd