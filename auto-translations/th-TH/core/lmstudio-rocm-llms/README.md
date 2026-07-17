<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

LM Studio เป็น wrapper แบบ GUI ที่ทรงพลังสำหรับ [llama.cpp](https://github.com/ggml-org/llama.cpp) และยังมี [endpoint ที่รองรับ OpenAI](https://lmstudio.ai/docs/developer/openai-compat) สำหรับการให้บริการโมเดลในเครื่อง LM Studio มีอินเทอร์เฟซที่เรียบง่ายแต่ทรงพลังสำหรับการดาวน์โหลดและปรับใช้โมเดลได้อย่างง่ายดาย LM Studio มีทั้ง backend Vulkan และ AMD ROCm™ software (เรียกว่า runtimes) สำหรับผู้ใช้ AMD


## สิ่งที่คุณจะได้เรียนรู้
- วิธีกำหนดค่าและใช้งาน LM Studio เพื่อใช้ประโยชน์จากฮาร์ดแวร์ในเครื่องของคุณ
- ทดสอบและจัดการ LLM ในสภาพแวดล้อมแบบออฟไลน์อย่างสมบูรณ์
- ให้บริการโมเดลผ่าน OpenAI Compatible API เพื่อขับเคลื่อน workflow และแอปพลิเคชันที่กำหนดเอง


## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @os:linux -->
> **หมายเหตุ**: คุณสามารถติดตั้ง VS Code ผ่าน AMD Ryzen™ AI Developer Center สำหรับ LM Studio ให้ทำตามคำแนะนำการติดตั้งด้านล่าง
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: หาก VS Code หรือ LM Studio ยังไม่ได้ติดตั้ง คุณสามารถติดตั้งได้จาก AMD Ryzen™ AI Developer Center
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## การดาวน์โหลดโมเดล

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## การสนทนากับ LLM
เรียนรู้วิธีเริ่มสนทนากับ LLM ระดับ ChatGPT ในเครื่องของคุณอย่างสมบูรณ์

1. เปิด LMStudio
2. กด `Ctrl + L` เพื่อเปิด Model Loader เลือก `Manually choose model load parameters` และคลิกที่ `${model_name}`
3. ตรวจสอบให้แน่ใจว่าได้เลือก "show advanced settings" ไว้แล้ว
4. เปลี่ยน `Context Length` ตามที่ต้องการ ความยาว context ที่มากขึ้นหมายถึงหน่วยความจำโมเดลมากขึ้น แต่ใช้หน่วยความจำระบบมากขึ้นด้วย แนะนำสำหรับ playbook นี้คือ 4096
5. ตรวจสอบให้แน่ใจว่า `GPU Offload` ตั้งค่าเป็นสูงสุดและ `Flash Attention` เปิดอยู่ (Cache Quantizations สามารถปิดไว้ได้)
6. เลือก `Remember settings` และคลิกที่ `Load Model`
7. หากไม่ได้อยู่ในหน้าต่างแชท ให้กด `Ctrl + 1` หรือคลิกที่ปุ่ม 👾 ที่มุมบนซ้ายของหน้าจอ
8. ส่งข้อความและเริ่มโต้ตอบกับโมเดล!

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **เคล็ดลับ**: ความยาว context หมายถึงหน่วยความจำของโมเดล Flash attention ช่วยเพิ่มความเร็วในการประมวลผลพร้อมลดการใช้หน่วยความจำ GPU Offload ย้ายการคำนวณไปยังการ์ดกราฟิกเพื่อการตอบสนองที่เร็วขึ้น

## ให้บริการ LLM ผ่าน endpoint ที่รองรับ OpenAI

LM Studio ยังมี endpoint ที่รองรับ OpenAI ในรูปแบบของ LM Studio Server ซึ่งได้รับการสาธิตแล้วใน workflow การเขียนโค้ดแบบ agentic กับ Cline [ที่นี่](../playbooks/vscode-qwen3-coder) กรณีการใช้งานทั่วไปอีกอย่างคือการเชื่อมต่อ LM Studio Server กับเว็บแอปพลิเคชันใดก็ได้ (React, Node.js, Python) โดยการส่ง HTTP request มาตรฐานไปยัง inference endpoint

ในการตั้งค่า LM Studio Server ให้ทำตามคำแนะนำต่อไปนี้:

1. ที่ด้านซ้ายมือ คลิกที่แท็บ `Developer` (ไอคอน command line) หรือ `Ctrl + 2` จากนั้นคลิกที่ `Server Settings`
2. (ไม่บังคับ): หากต้องการให้บริการโมเดลผ่าน LAN ของคุณ ให้เลือก `Serve on Local Network` หากต้องการใช้กับเว็บไซต์หรือการเรียกใช้งานจำนวนมากภายใน VS Code ให้เลือก `Enable CORS`
3. ที่มุมบนซ้าย ตรวจสอบให้แน่ใจว่าเซิร์ฟเวอร์กำลังทำงานโดยคลิกที่ปุ่มสลับหน้า `Status`
4. ขณะนี้ endpoint ที่รองรับ OpenAI จะทำงานอยู่ โดยทั่วไปที่อยู่จะอยู่ที่ http://127.0.0.1:1234
5. หากยังไม่ได้โหลดโมเดล คุณสามารถโหลดได้โดยคลิก `Load Model` และทำตามขั้นตอนที่กล่าวถึงก่อนหน้านี้

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


โมเดลนี้จะสามารถเข้าถึงได้ผ่าน LM Studio Server endpoint และจะรองรับ OpenAI endpoints รวมถึง:

| Endpoint | Method | เอกสาร |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### ตัวอย่าง: การ Ping Endpoint ของคุณ
หลังจากสร้าง OpenAI Compatible endpoint แล้ว มาดูวิธีการผสานรวมเข้ากับสภาพแวดล้อมนักพัฒนา Python (เช่น VSCode) และใช้ระบบของคุณเป็น local API Provider

1. สร้าง Python virtual environment:

<!-- @os:linux -->
<!-- @device:halo_box -->
    บน Linux ให้เปิด terminal ในไดเรกทอรีที่คุณต้องการและทำตามคำสั่งเพื่อสร้าง venv
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ให้สิทธิ์ผู้ใช้ของคุณในการเข้าถึงอุปกรณ์ GPU** (ออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

    บน Linux ให้เปิด terminal ในไดเรกทอรีที่คุณต้องการและทำตามคำสั่งเพื่อสร้าง venv
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
    บน Windows ให้เปิด terminal ในไดเรกทอรีที่คุณต้องการและทำตามคำสั่งเพื่อสร้าง venv
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องแก้ไข PowerShell Execution Policy (เช่น
    > ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนรันคำสั่ง Powershell บางคำสั่ง

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    บน Windows ให้เปิด terminal ในไดเรกทอรีที่คุณต้องการและทำตามคำสั่งเพื่อสร้าง venv
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องแก้ไข PowerShell Execution Policy (เช่น
    > ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนรันคำสั่ง Powershell บางคำสั่ง

<!-- @device:end -->
<!-- @os:end -->

2. ติดตั้งแพ็กเกจ OpenAI
    ```bash
    pip install openai
    ```

3. รันสคริปต์ต่อไปนี้เพื่อ ping endpoint ที่เราเพิ่งสร้างขึ้น
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local LM Studio server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
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
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
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

#### (ไม่บังคับ): การสลับระหว่าง Runtimes

1. กด `Ctrl + Shift + R` บนแป้นพิมพ์ของคุณ หรือคลิกที่แท็บ `Discover` (แว่นขยาย) ที่ด้านซ้ายมือ จากนั้นคลิกที่ `Runtime` ในป๊อปอัปที่ปรากฏขึ้น
2. คุณจะเห็น `Runtime Selections` ซึ่งสามารถใช้เมนูดรอปดาวน์เพื่อเปลี่ยน runtime ได้


## ขั้นตอนถัดไป

- **การผสานรวมแอปที่กำหนดเอง**: ผสานรวมสคริปต์ Python หรือแอปพลิเคชันของคุณเองโดยใช้ local OpenAI-compatible API
- **Frontend ขั้นสูง**: เชื่อมต่ออินเทอร์เฟซที่ทรงพลังอย่าง Open WebUI กับเซิร์ฟเวอร์ของคุณสำหรับประวัติการแชทและการจัดการ persona

สำหรับเอกสารเพิ่มเติม โปรดเยี่ยมชม: https://lmstudio.ai/docs/developer