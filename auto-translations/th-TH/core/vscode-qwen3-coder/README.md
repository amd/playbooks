<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

## ภาพรวม

Coding agent เป็นเครื่องมืออันทรงพลังที่ช่วยเสริมศักยภาพให้นักพัฒนาผ่านการทำงานร่วมกับ AI agent ที่ขับเคลื่อนด้วย Large Language Models (LLMs) สามารถฝังตัวอยู่ในสภาพแวดล้อมการพัฒนา เช่น terminal หรือ VS Code ช่วยให้ผสานรวมเข้ากับกระบวนการทำงานของนักพัฒนาได้อย่างราบรื่น

บทช่วยสอนนี้สาธิตวิธีใช้ Cline, VS Code และ LM Studio เพื่อรัน coding agent ทั้งหมดบนเครื่องของคุณเอง

## สิ่งที่คุณจะได้เรียนรู้

* วิธีรัน VS Code พร้อมกับ Cline coding agent เพื่อช่วยในงานวิศวกรรมซอฟต์แวร์
* วิธีกำหนดค่า Cline ให้สื่อสารกับ LM Studio สำหรับการ inference แบบโลคัลของ coding agent
* วิธีใช้ local coding agent เพื่อแก้ปัญหางานวิศวกรรมซอฟต์แวร์จริง

## การตั้งค่าการกำหนดค่าหน่วยความจำ

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

- ในแถบค้นหา ค้นหา `LM Studio` และเปิดแอปพลิเคชัน คุณจะพบกับหน้าต่อไปนี้

![หน้าจอเริ่มต้นของ LM Studio](assets/initial-lm-studio.png)

ถัดไป เราต้องโหลด LLM บนระบบ เราจะใช้โมเดล `Qwen3-Coder-30B-A3B` ที่มีความยาว context ขนาดใหญ่ (ใช้แท็บ Model เพื่อติดตั้งหากยังไม่ได้ดำเนินการ)
- คลิกที่แถบค้นหาด้านบนของหน้าต่าง LM Studio หรือกด `CTRL+L` คลิกสวิตช์ `Manually choose model load parameters` จากนั้นคลิกที่โมเดล Qwen3-Coder-30B-A3B
- เปลี่ยนความยาว context จาก `4096` เป็น `32768` และตรวจสอบให้แน่ใจว่า `GPU Offload` อยู่ที่ค่าสูงสุด จากนั้นคลิก `Load Model`

![การเลือกโมเดล](assets/model-list-zoomed.png)

เราใช้ความยาว context ขนาดใหญ่เพื่อให้ agent สามารถประมวลผล codebase ขนาดใหญ่และจดจำการเปลี่ยนแปลงที่เกิดขึ้นได้

![การกำหนดค่าโมเดล](assets/selecting-model-zoomed.png)

ถัดไป เราต้องเปิดใช้งาน LM Studio Server
- คลิกแท็บ Developer หรือกด `CTRL+2` ใน LM Studio ทางด้านซ้าย
- ตรวจสอบสวิตช์สถานะและตรวจสอบให้แน่ใจว่าตั้งค่าเป็น `Running`

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
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
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
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## เปิดใช้งานและกำหนดค่า VS Code

เราจะติดตั้ง Cline Extension ใน VS Code และเชื่อมต่อกับ LM Studio server ที่เราสร้างขึ้น
- ในแถบค้นหา ค้นหา `VS Code` และเปิดแอปพลิเคชัน
- คลิกที่ไอคอน `Extensions` ในคอลัมน์ด้านซ้ายของ VS Code และค้นหา `Cline` จากนั้นคลิกปุ่ม `Install`

![การติดตั้ง Cline Extension](assets/installing-cline-vscode-extension.png)

- ควรมีไอคอน Cline ปรากฏทางด้านซ้าย คลิกที่ไอคอนนั้นเพื่อเปิด Cline จะมีหน้าต่างถามว่า `How will you use Cline?` เนื่องจากเราจะใช้ LLM แบบโลคัลที่รันผ่าน LM Studio ให้เลือก `Bring my own API Key` และคลิก `Continue`

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

ถัดไป เราต้องกำหนดค่า Cline ให้สื่อสารกับ LM Studio server ที่เราตั้งค่าไว้
- ตั้งค่า API Provider เป็น `LM Studio` และโมเดลเป็น `Qwen3-Coder-30B-A3B-GGUF`

>**เคล็ดลับ**: อาจมีโมเดลใหม่กว่าให้ใช้งาน พิจารณาดาวน์โหลดและเปลี่ยนไปใช้โมเดล Qwen3.6 หากต้องการ


![การกำหนดค่าโมเดล](assets/cline-model-configuration-zoomed.png)

## การสร้างโปรเจกต์แรกของคุณ

มาใช้ local agent ของเราเพื่อสร้างเว็บไซต์กัน! เปิด VSCode ไปยังไดเรกทอรีที่คุณต้องการให้ Cline สร้างไฟล์
- ในการดำเนินการนี้ ไปที่ `File -> Open Folder` ที่มุมบนซ้ายของ VS Code และเลือกโฟลเดอร์ เช่น `Documents`

![VS Code โฟลเดอร์ว่าง](assets/open-cline-test.png)

ตอนนี้เราพร้อมที่จะส่ง prompt ให้กับ local coding agent แล้ว
- คลิกที่ Cline extension ในคอลัมน์ด้านซ้ายและป้อน prompt เพื่อเริ่มต้น agent ตัวอย่างเช่น ลองใช้ prompt ต่อไปนี้:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

จากนั้น agent จะเริ่มสร้างไฟล์ตาม prompt ในฐานะผู้ใช้ คุณสามารถดูโค้ดที่ถูกสร้างขึ้นใน VS Code ดังที่แสดงด้านล่าง คุณอาจต้องคลิก `Save` ทุกครั้งที่ Cline ต้องการสร้างไฟล์

![การสร้างโค้ดด้วย Cline](assets/cline-code-generation.png)

หลังจากสร้างซอฟต์แวร์แล้ว agent จะเสร็จสิ้นและคุณสามารถรันแอปพลิเคชันได้ ในกรณีนี้ agent เขียนไปยังสามไฟล์: `index.html`, `script.js` และ `styles.css` เพียงดับเบิลคลิกที่ไฟล์ HTML เราก็สามารถโหลดและโต้ตอบกับเว็บไซต์ที่สร้างขึ้นได้

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
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
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
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
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

หลังจากสร้างเว็บไซต์แล้ว คุณสามารถทำงานร่วมกับ Cline ต่อไปเพื่อปรับปรุงเว็บไซต์ การปรับปรุงที่เป็นไปได้สองประการ ได้แก่:

- **เอกสารประกอบ**: การส่ง prompt ให้ agent ด้วย `Add a README` ก็เพียงพอสำหรับให้ agent สร้างไฟล์ `README.md` ที่บันทึกข้อมูลเว็บไซต์
- **แอนิเมชัน**: ส่ง prompt ให้โมเดลด้วย `Add an animation that visually represents a large language model running on a laptop.` เพื่อสร้างแอนิเมชันให้กับเว็บไซต์

เราขอแนะนำให้ผู้อ่านลองสร้างแอปพลิเคชันอื่น ๆ โดยใช้การตั้งค่านี้ ด้านล่างนี้คือตัวอย่างที่สนุกที่เราได้ลองทำ:

- **เกมอาร์เคดสไตล์เรโทร**: ลอง prompt อื่น ๆ ดู นอกจากนี้ยังสนุกที่จะให้ agent สร้างเกมสไตล์เรโทรใน Python โดยใช้แพ็กเกจ `PyGame` ด้วย prompt ต่อไปนี้:

```code
Create a simple pong game using the PyGame python package.
```

- **การวิเคราะห์ข้อมูล**: หนึ่งในพื้นที่ที่ coding agent มีประโยชน์อย่างยิ่งคือการเขียนสคริปต์และการวิเคราะห์ข้อมูล นี่คือ prompt เพื่อแสดงความสามารถของโมเดลโลคัลในการสร้างซอฟต์แวร์วิเคราะห์ข้อมูลสำหรับการแสดงภาพราคาหุ้น:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## แหล่งข้อมูล

ด้านล่างนี้คือแหล่งข้อมูลเพิ่มเติมเพื่อเรียนรู้เพิ่มเติมเกี่ยวกับ Coding Agent, Cline และการรัน workload บน

* ข้อมูลเพิ่มเติมเกี่ยวกับความร่วมมือและการผสานรวมระหว่าง AMD กับ LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* บล็อกของ AMD ที่อธิบายการรัน Cline บน AMD Ryzen™ AI และ Radeon™ Graphics Cards: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* บล็อกของ Cline เกี่ยวกับการรัน coding agent แบบโลคัลบน AI PC: https://cline.bot/blog/local-models-amd