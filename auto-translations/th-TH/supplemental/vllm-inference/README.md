<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## ภาพรวม

vLLM คือเอนจินอนุมานประสิทธิภาพสูงที่ออกแบบมาสำหรับโมเดลภาษาขนาดใหญ่ (LLMs) โดยมีการให้บริการที่ปรับแต่งแล้วพร้อม continuous batching เพื่อปริมาณงานสูง และ API ที่เข้ากันได้กับ OpenAI สำหรับการผสานรวมแอปพลิเคชันอย่างราบรื่น ทำให้ vLLM เหมาะอย่างยิ่งสำหรับการใช้งานในระดับ production ที่ความเร็วและประสิทธิภาพการใช้ทรัพยากรเป็นสิ่งสำคัญ

Playbook นี้จะสอนวิธีให้บริการ LLMs โดยใช้ vLLM แบบ containerized บน integrated GPU และโต้ตอบกับโมเดลผ่าน OpenAI Python API

## สิ่งที่คุณจะได้เรียนรู้

- วิธีตั้งค่าและเริ่มต้น vLLM server พร้อมการรองรับ AMD ROCm™
- วิธีโต้ตอบกับโมเดลผ่าน API endpoint ที่เข้ากันได้กับ OpenAI
- วิธีส่ง prompt ไปยัง server ในเครื่องด้วย `vllm-prompt`

## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ผ่าน AMD Ryzen™ AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

Playbook นี้ใช้ container image ที่สร้างไว้ล่วงหน้าซึ่งรวม vLLM, การรองรับ ROCm และสคริปต์ช่วยเหลือที่จำเป็นสำหรับการเปิดใช้งาน server ไว้แล้ว คุณไม่จำเป็นต้องติดตั้ง PyTorch, vLLM หรือสคริปต์ playbook ในเครื่องด้วยตนเอง

ไม่มีขั้นตอนการติดตั้ง vLLM ฝั่ง host เริ่มต้น vLLM ด้วย:

```bash
vllm-launch
```

ตัวเปิดใช้งานจะเริ่มต้น container กำหนดเป้าหมายไปที่ integrated GPU และเปิดเผย vLLM server ที่เข้ากันได้กับ OpenAI ในเครื่อง หรือคลิกไอคอน vLLM ในแถบงาน

## เริ่มต้นอย่างรวดเร็ว

### 1. ยืนยันว่า vLLM Server กำลังทำงาน

`vllm-launch` อาจใช้เวลาสองสามนาทีในการเริ่มต้นทุกอย่าง เมื่อเริ่มต้นแล้ว server จะพร้อมใช้งานที่ `http://localhost:8001` เปิด terminal ที่ใช้เปิดใช้งานไว้เพราะ server ทำงานใน foreground จากนั้นเปิด terminal แยกต่างหากสำหรับขั้นตอนที่เหลือ ตัวอย่างด้านล่างใช้ `Qwen/Qwen3-1.7B` หากตัวเปิดใช้งานของคุณกำหนดค่าสำหรับโมเดลอื่น ให้แทนที่ ID โมเดลนั้นในคำขอ

### 2. ส่ง Prompt

ใช้สคริปต์ `vllm-prompt` ที่มีให้เพื่อส่งคำขอไปยัง vLLM server ที่เข้ากันได้กับ OpenAI ในเครื่อง:

```bash
vllm-prompt "Tell me a story"
```

### 3. สนทนากับโมเดลโดยใช้ OpenAI Python API

เนื่องจาก vLLM เปิดเผย API ที่เข้ากันได้กับ OpenAI คุณจึงสามารถใช้แพ็กเกจ Python `openai` เพื่อโต้ตอบกับมันได้

ขั้นแรก สร้าง Python virtual environment:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

ติดตั้งแพ็กเกจ OpenAI
```bash
pip install openai
```

สร้าง client `OpenAI` ที่ชี้ไปยัง vLLM server ในเครื่องแทนที่จะเป็น server ของ OpenAI โดย `api_key` จำเป็นสำหรับ client แต่ vLLM ไม่ตรวจสอบ ดังนั้นสตริงใดก็ได้:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

จากนั้น ส่งคำขอ chat completion โดยใช้รูปแบบข้อความเดียวกับ OpenAI API ซึ่งเป็นรายการข้อความที่มี role เช่น `"user"` และ `"assistant"` การตั้งค่า `stream=True` หมายความว่าการตอบสนองจะมาถึงแบบค่อยเป็นค่อยไปแทนที่จะมาทั้งหมดในครั้งเดียว:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

สุดท้าย วนซ้ำผ่าน chunk ที่ stream มาและพิมพ์แต่ละส่วนของข้อความเมื่อมาถึง:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

สคริปต์ [chat_with_model.py](assets/chat_with_model.py) ที่รวมไว้มีตัวอย่างทั้งหมดและสามารถดาวน์โหลดได้


## การแก้ไขปัญหา

### Connection refused

ตรวจสอบให้แน่ใจว่า server กำลังทำงาน:
```bash
curl http://localhost:8001/health
```

## สรุป

ใน playbook นี้ คุณได้เรียนรู้วิธี:

- เริ่มต้น vLLM แบบ containerized พร้อมการรองรับ ROCm บน integrated GPU
- เริ่มต้น vLLM server พร้อม API endpoint ที่เข้ากันได้กับ OpenAI บนพอร์ต 8001
- ส่ง prompt ด้วย `vllm-prompt`
- เรียก API ไปยัง vLLM server โดยใช้ทั้งคำขอแบบ streaming และ non-streaming
- แก้ไขปัญหาทั่วไปเกี่ยวกับการเริ่มต้น server หน่วยความจำ และการเชื่อมต่อ client

ตอนนี้คุณมีการใช้งาน vLLM แบบ containerized สำหรับให้บริการโมเดลภาษาขนาดใหญ่พร้อมประสิทธิภาพที่ปรับแต่งแล้วบน integrated GPU

## ขั้นตอนถัดไป

- **ลองใช้โมเดลต่างๆ** — สลับโมเดลในการกำหนดค่า `vllm-launch` เพื่อทดลองกับ LLMs ต่างๆ และเปรียบเทียบประสิทธิภาพ
- **สร้างแอปพลิเคชัน** — ใช้ API ที่เข้ากันได้กับ OpenAI เพื่อผสานรวม vLLM เข้ากับแอป Python, chatbot หรือ workflow อัตโนมัติ
- **Fine-tune และให้บริการ** — Fine-tune โมเดลโดยใช้ LoRA หรือ QLoRA จากนั้น deploy ด้วย vLLM เพื่อการอนุมานที่ปรับแต่งแล้ว

## แหล่งข้อมูลเพิ่มเติม

- **[เอกสารอย่างเป็นทางการของ vLLM](https://docs.vllm.ai/)** — คู่มือที่ครอบคลุมและเอกสารอ้างอิง API
- **[vLLM GitHub Repository](https://github.com/vllm-project/vllm)** — ซอร์สโค้ด ปัญหา และการสนทนาของชุมชน