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

LM Studio คือตัวห่อหุ้ม (wrapper) แบบ GUI ที่ทรงพลังสำหรับ [llama.cpp](https://github.com/ggml-org/llama.cpp) และยังมี [OpenAI compliant endpoint](https://lmstudio.ai/docs/developer/openai-compat) สำหรับการให้บริการโมเดลแบบโลคัลอีกด้วย LM Studio มอบอินเทอร์เฟซที่เรียบง่ายแต่ทรงพลังสำหรับดาวน์โหลดและนำโมเดลไปใช้งานได้อย่างง่ายดาย LM Studio รองรับทั้ง Vulkan และแบ็กเอนด์ซอฟต์แวร์ AMD ROCm™ (เรียกว่า runtimes) สำหรับผู้ใช้ AMD


## สิ่งที่คุณจะได้เรียนรู้
- วิธีตั้งค่าและใช้งาน LM Studio เพื่อใช้ประโยชน์จากฮาร์ดแวร์ในเครื่องของคุณ
- ทดสอบและจัดการ LLM ในสภาพแวดล้อมออฟไลน์อย่างสมบูรณ์
- ให้บริการโมเดลผ่าน OpenAI Compatible API เพื่อขับเคลื่อนเวิร์กโฟลว์และแอปพลิเคชันแบบกำหนดเอง


## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @os:linux -->
> **หมายเหตุ**: คุณสามารถติดตั้ง VS Code ผ่าน AMD Ryzen™ AI Developer Center ได้ สำหรับ LM Studio ให้ทำตามคำแนะนำการติดตั้งด้านล่าง
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code หรือ LM Studio คุณสามารถติดตั้งได้จาก AMD Ryzen™ AI Developer Center 
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

## การแชทกับ LLM
เรียนรู้วิธีเริ่มแชทกับ LLM ระดับ ChatGPT ได้อย่างสมบูรณ์บนเครื่องของคุณเอง  

1. เปิด LMStudio 
2. กด `Ctrl + L` เพื่อเปิด Model Loader เลือก `Manually choose model load parameters` แล้วคลิกที่ `${model_name}`
3. ตรวจสอบให้แน่ใจว่าได้เลือก "show advanced settings" แล้ว  
4. เปลี่ยน `Context Length` ตามต้องการ ค่า Context Length ที่สูงขึ้นหมายถึงการใช้หน่วยความจำของโมเดลมากขึ้น แต่ก็ใช้หน่วยความจำระบบมากขึ้นเช่นกัน ค่าที่แนะนำสำหรับคู่มือนี้คือ 4096
5. ตรวจสอบให้แน่ใจว่า `GPU Offload` ถูกตั้งค่าไว้ที่ค่าสูงสุด และ `Flash Attention` เปิดอยู่ (Cache Quantizations สามารถปิดไว้ได้)
6. เลือก `Remember settings` แล้วคลิกที่ `Load Model`
7. หากไม่ได้อยู่ในหน้าต่างแชท ให้กด `Ctrl + 1` หรือคลิกที่ปุ่ม 👾 ที่มุมบนซ้ายของหน้าจอ
8. ส่งข้อความและเริ่มโต้ตอบกับโมเดลได้เลย!

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
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y }
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
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y; }
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

> **เคล็ดลับ**: Context length คือหน่วยความจำของโมเดล Flash attention ช่วยเพิ่มความเร็วในการประมวลผลพร้อมทั้งลดการใช้หน่วยความจำ GPU Offload จะย้ายภาระการประมวลผลไปยังการ์ดจอเพื่อให้ได้การตอบสนองที่รวดเร็วขึ้น

## ให้บริการ LLM ผ่านเอนด์พอยต์ที่รองรับ OpenAI

LM Studio ยังมีเอนด์พอยต์ที่รองรับมาตรฐาน OpenAI ในรูปแบบของ LM Studio Server ซึ่งได้แสดงให้เห็นแล้วในเวิร์กโฟลว์การเขียนโค้ดแบบเอเจนต์ด้วย Cline [ที่นี่](../playbooks/vscode-qwen3-coder) อีกกรณีการใช้งานทั่วไปคือการเชื่อมต่อ LM Studio Server กับเว็บแอปพลิเคชันใด ๆ (React, Node.js, Python) โดยการส่งคำขอ HTTP มาตรฐานไปยังเอนด์พอยต์การอนุมาน (inference)

หากต้องการตั้งค่า LM Studio Server ให้ทำตามคำแนะนำต่อไปนี้:

1. ทางด้านซ้ายมือ คลิกที่แท็บ `Developer` (ไอคอนบรรทัดคำสั่ง) หรือกด `Ctrl + 2` จากนั้นคลิกที่ `Server Settings`  
2. (ทางเลือกเสริม): หากคุณต้องการให้บริการโมเดลผ่าน LAN ของคุณ ให้เลือก `Serve on Local Network` หากคุณต้องการใช้งานกับเว็บไซต์หรือการเรียกใช้อย่างละเอียดภายใน VS Code ให้เลือก `Enable CORS` 
3. ที่มุมบนซ้าย ตรวจสอบให้แน่ใจว่าเซิร์ฟเวอร์กำลังทำงานอยู่โดยคลิกที่ปุ่มสลับ (toggle) ด้านหน้า `Status`
4. ขณะนี้เอนด์พอยต์ที่รองรับมาตรฐาน OpenAI จะทำงานอยู่ โดยที่อยู่มักจะอยู่ที่ http://127.0.0.1:1234  
5. หากยังไม่มีการโหลดโมเดล คุณสามารถโหลดได้โดยคลิกที่ `Load Model` แล้วทำตามขั้นตอนที่กล่าวไว้ก่อนหน้านี้ 

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


ขณะนี้โมเดลนี้จะสามารถเข้าถึงได้ผ่านเอนด์พอยต์ LM Studio Server และจะรองรับเอนด์พอยต์ของ OpenAI ซึ่งได้แก่:

| Endpoint | Method | Docs |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### ตัวอย่าง: การ Ping Endpoint ของคุณ
เมื่อสร้าง OpenAI Compatible endpoint เสร็จแล้ว มาดูวิธีการรวมสิ่งนี้เข้ากับสภาพแวดล้อมการพัฒนา Python (เช่น VSCode) และใช้ระบบของคุณเป็น local API Provider

1. สร้าง Python virtual environment:

<!-- @os:linux -->
<!-- @device:halo_box -->
    บน Linux ให้เปิด terminal ในไดเรกทอรีที่คุณเลือก แล้วทำตามคำสั่งเพื่อสร้าง venv
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ให้สิทธิ์ผู้ใช้ของคุณเข้าถึงอุปกรณ์ GPU** (ล็อกเอาต์และล็อกอินกลับเข้ามาใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

    บน Linux ให้เปิด terminal ในไดเรกทอรีที่คุณเลือก แล้วทำตามคำสั่งเพื่อสร้าง venv
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
    บน Windows ให้เปิด terminal ในไดเรกทอรีที่คุณเลือก แล้วทำตามคำสั่งเพื่อสร้าง venv
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องปรับเปลี่ยน PowerShell Execution Policy (เช่น
    > ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนที่จะรันคำสั่ง Powershell บางคำสั่ง

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    บน Windows ให้เปิด terminal ในไดเรกทอรีที่คุณเลือก แล้วทำตามคำสั่งเพื่อสร้าง venv
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องปรับเปลี่ยน PowerShell Execution Policy (เช่น
    > ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนที่จะรันคำสั่ง Powershell บางคำสั่ง

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

#### (ทางเลือกเสริม): การสลับระหว่าง Runtimes

1. กด `Ctrl + Shift + R` บนแป้นพิมพ์ของคุณ หรืออีกวิธีหนึ่งคือคลิกที่แท็บ `Discover` (ไอคอนแว่นขยาย) ทางด้านซ้ายมือ แล้วคลิกที่ `Runtime` ในป๊อปอัป
2. จากนั้นคุณจะเห็น `Runtime Selections` ซึ่งสามารถใช้เมนูแบบดรอปดาวน์เพื่อเปลี่ยน runtime ได้


## ขั้นตอนถัดไป

- **การผสานรวมแอปแบบกำหนดเอง**: ผสานรวมสคริปต์หรือแอปพลิเคชัน Python ของคุณเองโดยใช้ local OpenAI-compatible API
- **ส่วนติดต่อขั้นสูง**: เชื่อมต่ออินเทอร์เฟซที่ทรงพลังอย่าง Open WebUI เข้ากับเซิร์ฟเวอร์ของคุณเพื่อจัดการประวัติการแชทและโปรไฟล์ผู้ใช้

สำหรับเอกสารเพิ่มเติม โปรดไปที่: https://lmstudio.ai/docs/developer