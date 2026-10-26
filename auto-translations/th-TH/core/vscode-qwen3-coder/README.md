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
> เพลย์บุ๊กนี้ต้องการหน่วยความจำระบบขั้นต่ำ **32GB**
<!-- @device:end -->

## ภาพรวม

Coding agents เป็นเครื่องมือทรงพลังที่ช่วยเสริมศักยภาพให้กับนักพัฒนา ผ่านการทำงานร่วมกับ AI agents ที่ขับเคลื่อนด้วย Large Language Models (LLMs) โดยสามารถฝังเข้าไปในสภาพแวดล้อมการพัฒนา เช่น เทอร์มินัลหรือ VS Code ทำให้สามารถผสานเข้ากับเวิร์กโฟลว์ของนักพัฒนาได้อย่างราบรื่น

บทช่วยสอนนี้สาธิตวิธีการใช้ Cline, VS Code และ LM Studio เพื่อรัน coding agent บนเครื่องของคุณเองทั้งหมด

## สิ่งที่คุณจะได้เรียนรู้

* วิธีการรัน VS Code ร่วมกับ coding agent ของ Cline เพื่อช่วยในงานด้านวิศวกรรมซอฟต์แวร์
* วิธีการกำหนดค่า Cline ให้สื่อสารกับ LM Studio สำหรับการอนุมาน (inference) แบบโลคัลของ coding agents
* วิธีการใช้ local coding agents เพื่อแก้ปัญหางานด้านวิศวกรรมซอฟต์แวร์ในโลกความเป็นจริง

<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้จาก Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @require:lmstudio,vscode -->

## เปิดใช้งานและกำหนดค่า LM Studio

เราจะใช้ LM Studio เพื่อให้บริการ LLM ที่ขับเคลื่อน coding agent

- ในแถบค้นหา ให้ค้นหา `LM Studio` แล้วเปิดใช้งานแอปพลิเคชัน คุณจะพบกับหน้าจอต่อไปนี้

![หน้าจอเริ่มต้นของ LM Studio](assets/initial-lm-studio.png)

ถัดไป เราต้องโหลด LLM ลงในระบบ เราจะใช้โมเดล `Qwen3-Coder-30B-A3B` ที่มีความยาวบริบท (context length) ขนาดใหญ่ (ใช้แท็บ Model เพื่อติดตั้งหากคุณยังไม่ได้ติดตั้ง)
- คลิกที่แถบค้นหาด้านบนของหน้าต่าง LM Studio หรือกด `CTRL+L` คลิกสวิตช์ `Manually choose model load parameters` จากนั้นคลิกที่โมเดล Qwen3-Coder-30B-A3B
- เปลี่ยนความยาวบริบทจาก `4096` เป็น `32768` และตรวจสอบให้แน่ใจว่า `GPU Offload` อยู่ที่ระดับสูงสุด จากนั้นคลิก `Load Model`

![การเลือกโมเดล](assets/model-list-zoomed.png)

เราใช้ความยาวบริบทขนาดใหญ่เพื่อให้ agent สามารถประมวลผลโค้ดเบสขนาดใหญ่และจดจำการเปลี่ยนแปลงที่เกิดขึ้นได้

![การกำหนดค่าโมเดล](assets/selecting-model-zoomed.png)

ถัดไป เราจำเป็นต้องเปิดใช้งาน LM Studio Server
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

![สถานะเซิร์ฟเวอร์](assets/lm-studio-server-status.png)

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

เราจะติดตั้งส่วนขยาย Cline ใน VS Code และเชื่อมต่อกับเซิร์ฟเวอร์ LM Studio ที่เราเพิ่งสร้างขึ้น
- ในแถบค้นหา ให้ค้นหา `VS Code` แล้วเปิดใช้งานแอปพลิเคชัน
- คลิกที่ไอคอน `Extensions` ทางคอลัมน์ซ้ายของ VS Code แล้วค้นหา `Cline` จากนั้นคลิกปุ่ม `Install`

![การติดตั้งส่วนขยาย Cline](assets/installing-cline-vscode-extension.png)

- จะมีไอคอน Cline ปรากฏขึ้นทางด้านซ้าย คลิกที่ไอคอนนั้นเพื่อเปิด Cline จะมีหน้าต่างถามว่า `How will you use Cline?` เนื่องจากเราจะใช้ local LLM ที่รันผ่าน LM Studio ให้เลือก `Bring my own API Key` แล้วกด `Continue`

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

ถัดไป เราจำเป็นต้องกำหนดค่า Cline ให้สื่อสารกับเซิร์ฟเวอร์ LM Studio ที่เราตั้งค่าไว้
- ตั้งค่า API Provider เป็น `LM Studio` และโมเดลเป็น `Qwen3-Coder-30B-A3B-GGUF`

>**เคล็ดลับ**: อาจมีโมเดลใหม่ๆ ให้ใช้งาน พิจารณาดาวน์โหลดและเปลี่ยนไปใช้โมเดล Qwen3.6 หากต้องการ


![การกำหนดค่าโมเดล](assets/cline-model-configuration-zoomed.png)

## การสร้างโปรเจกต์แรกของคุณ

มาลองใช้ local agent ของเราสร้างเว็บไซต์กันเถอะ! เปิด VSCode ไปยังไดเรกทอรีที่คุณเลือกเพื่อให้ Cline สร้างไฟล์ต่างๆ
- ในการทำเช่นนี้ ให้ไปที่ `File -> Open Folder` ที่มุมซ้ายบนของ VS Code แล้วเลือกโฟลเดอร์ เช่น `Documents`

![โฟลเดอร์ว่างเปล่าใน VS Code](assets/open-cline-test.png)

ตอนนี้เราพร้อมที่จะป้อนพรอมต์ให้กับ local coding agent แล้ว
- คลิกที่ส่วนขยาย Cline ทางคอลัมน์ซ้ายแล้วป้อนพรอมต์เพื่อเริ่มการทำงานของ agent ตัวอย่างเช่น ลองใช้พรอมต์ต่อไปนี้:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

จากนั้น agent จะเริ่มสร้างไฟล์ต่างๆ ตามพรอมต์ ในฐานะผู้ใช้ คุณสามารถดูโค้ดที่ถูกสร้างขึ้นใน VS Code ได้ดังที่แสดงด้านล่าง คุณอาจต้องคลิก `Save` ทุกครั้งที่ Cline ต้องการสร้างไฟล์

![การสร้างโค้ดด้วย Cline](assets/cline-code-generation.png)

หลังจากสร้างซอฟต์แวร์เสร็จแล้ว agent ก็ทำงานเสร็จสมบูรณ์ และคุณสามารถรันแอปพลิเคชันได้ ในกรณีนี้ agent ได้เขียนไฟล์สามไฟล์คือ `index.html`, `script.js` และ `styles.css` เพียงแค่ดับเบิลคลิกที่ไฟล์ HTML เราก็สามารถโหลดและโต้ตอบกับเว็บไซต์ที่สร้างขึ้นได้

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

หลังจากสร้างเว็บไซต์แล้ว คุณสามารถทำงานร่วมกับ Cline ต่อไปเพื่อปรับปรุงเว็บไซต์ให้ดียิ่งขึ้นได้ การปรับปรุงที่เป็นไปได้สองแบบมีดังนี้:

- **เอกสารประกอบ**: เพียงป้อนพรอมต์ให้ agent ด้วย `Add a README` ก็เพียงพอที่จะทำให้ agent สร้างไฟล์ `README.md` ที่บันทึกรายละเอียดเกี่ยวกับเว็บไซต์
- **แอนิเมชัน**: ป้อนพรอมต์ให้โมเดลด้วย `Add an animation that visually represents a large language model running on a laptop.` เพื่อสร้างแอนิเมชันเพิ่มลงในเว็บไซต์

เราขอสนับสนุนให้ผู้อ่านลองสร้างแอปพลิเคชันอื่นๆ โดยใช้การตั้งค่านี้ ด้านล่างนี้คือตัวอย่างสนุกๆ ที่เราได้ลองทำ:

- **เกมอาร์เคดย้อนยุค**: ลองใช้พรอมต์อื่นๆ ดู นอกจากนี้ยังสามารถให้ agent สร้างเกมสไตล์เรโทรด้วยภาษา Python โดยใช้แพ็กเกจ `PyGame` ได้อย่างสนุกสนาน ด้วยพรอมต์ต่อไปนี้:

```code
Create a simple pong game using the PyGame python package.
```

- **การวิเคราะห์ข้อมูล**: หนึ่งในด้านที่ coding agents มีประโยชน์อย่างยิ่งคือการเขียนสคริปต์และการวิเคราะห์ข้อมูล นี่คือพรอมต์ที่ใช้แสดงความสามารถของโมเดลโลคัลในการสร้างซอฟต์แวร์วิเคราะห์ข้อมูลสำหรับการแสดงผลราคาหุ้น:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## แหล่งข้อมูล

ด้านล่างนี้คือแหล่งข้อมูลเพิ่มเติมสำหรับเรียนรู้เกี่ยวกับ Coding Agents, Cline และการรันเวิร์กโหลดบน 

* ข้อมูลเพิ่มเติมเกี่ยวกับความร่วมมือและการผสานรวมระหว่าง AMD กับ LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* บล็อกของ AMD ที่แนะนำวิธีการรัน Cline บนการ์ด AMD Ryzen™ AI และ Radeon™ Graphics: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* บล็อกของ Cline เกี่ยวกับการรัน coding agents บนเครื่อง AI PC แบบโลคัล: https://cline.bot/blog/local-models-amd