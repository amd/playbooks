<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม


ต้องการรันโมเดลภาษา AI ที่ทรงพลังบนฮาร์ดแวร์ของคุณเองหรือไม่? คู่มือนี้จะแสดงวิธีการให้คุณทราบ
บทช่วยสอนนี้ใช้ PyTorch ที่ขับเคลื่อนด้วยซอฟต์แวร์ AMD ROCm™ เพื่อรันโมเดลที่สามารถสรุปเอกสาร ตอบคำถาม สร้างข้อความ และอื่นๆ ทั้งหมดทำงานในเครื่องของคุณ

## สิ่งที่คุณจะได้เรียนรู้

- รัน LLM เช่น gpt-oss-20b และ qwen3.5-4B ในเครื่องโดยใช้ PyTorch และ ROCm
- สร้างเครื่องมือสรุปเอกสารโดยใช้ LLM

## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ผ่าน Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

### สร้าง Virtual Environment

<!-- @os:linux -->
<!-- @device:halo_box -->
บน Linux ให้เปิด terminal ในไดเรกทอรีที่คุณต้องการ แล้วทำตามคำสั่งเพื่อสร้าง venv ที่ติดตั้ง ROCm+Pytorch ไว้แล้ว
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ให้สิทธิ์ผู้ใช้ของคุณในการเข้าถึงอุปกรณ์ GPU** (ออกจากระบบแล้วเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

บน Linux ให้เปิด terminal ในไดเรกทอรีที่คุณต้องการ แล้วทำตามคำสั่งเพื่อสร้าง venv
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
บน Windows ให้เปิด terminal ในไดเรกทอรีที่คุณต้องการ แล้วทำตามคำสั่งเพื่อสร้าง venv ที่ติดตั้ง ROCm+Pytorch ไว้แล้ว
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
บน Windows ให้เปิด terminal ในไดเรกทอรีที่คุณต้องการ แล้วทำตามคำสั่งเพื่อสร้าง venv
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องแก้ไข PowerShell Execution Policy (เช่น
> ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนรันคำสั่ง Powershell บางคำสั่ง

<!-- @os:end -->

### การติดตั้ง Dependencies พื้นฐาน
<!-- @require:driver,pytorch -->

### การติดตั้ง Dependencies เพิ่มเติม

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## เริ่มต้นอย่างรวดเร็วด้วยสคริปต์ตัวอย่าง

Playbook นี้มีสคริปต์ที่พร้อมใช้งาน คลิกเพื่อดูตัวอย่างและดาวน์โหลดไปยังไดเรกทอรีเดียวกับ environment ที่คุณสร้างไว้

| สคริปต์ | คำอธิบาย | การใช้งาน |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | การสร้างข้อความด้วย LLM พื้นฐาน | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | เครื่องมือสรุปเอกสารพร้อมรองรับ Harmony | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

สคริปต์ทั้งสองรองรับ:
- การเลือกโมเดลผ่านแฟล็ก `--model`
- การจัดรูปแบบ chat template สำหรับการ prompt โมเดลอย่างถูกต้อง ซึ่งมีประโยชน์อย่างยิ่งสำหรับการสรุปเอกสาร

## การโหลดและรัน LLM ตัวแรกของคุณ

สคริปต์ [run_llm.py](assets/run_llm.py) ที่รวมมาด้วยแสดงวิธีการสร้างข้อความด้วย LLM โดยใช้ PyTorch และ AMD ROCm

> **หมายเหตุ:** เมื่อคุณโหลดโมเดล Hugging Face Transformers จะตรวจสอบ cache ในเครื่องก่อน (`~/.cache/huggingface/hub` บน Linux, `C:\Users\<user>\.cache\huggingface\hub` บน Windows) หากโมเดลยังไม่ได้ถูก cache ไว้ ระบบจะดาวน์โหลดโดยอัตโนมัติจาก huggingface.co การรันครั้งแรกอาจใช้เวลาสักครู่ขึ้นอยู่กับขนาดโมเดลและความเร็วเครือข่าย

ตัวอย่างโค้ดด้านล่างแสดงวิธีใช้โมเดลและปรับแต่งคำถามที่ถาม

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

ลองใช้สคริปต์ที่ดาวน์โหลดมา:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## การสร้างเครื่องมือสรุปเอกสาร

เมื่อคุณสร้างผลลัพธ์จาก LLM ในเครื่องได้แล้ว คุณสามารถต่อยอดโดยสร้างเครื่องมือสรุปเอกสารที่ใช้งานได้จริง ในส่วนนี้ คุณจะใช้สคริปต์ [summarizer.py](assets/summarizer.py) เพื่อป้อนไฟล์ .txt และสร้างสรุปที่กระชับโดยอัตโนมัติ ทั้งหมดทำงานในเครื่องบน GPU ของคุณ

สคริปต์ได้รับการออกแบบให้ใช้งานได้ทันที เปิดสคริปต์ในโปรแกรมแก้ไขเพื่อสำรวจโค้ด ปรับแต่ง prompt และปรับพารามิเตอร์ต่างๆ เช่น ความยาวและ temperature

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### ตัวอย่างการใช้งาน

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## เรียนรู้เกี่ยวกับพารามิเตอร์การสร้างข้อความ

| พารามิเตอร์ | สิ่งที่ควบคุม | ค่าทั่วไป |
|-----------|------------------|----------------|
| `max_new_tokens` | ความยาวสูงสุดของผลลัพธ์จาก LLM | ใช้ 50–500 token สำหรับการสรุป (1 token ประมาณ 0.75 คำภาษาอังกฤษ) |
| `temperature` | ความสร้างสรรค์ ค่าต่ำทำให้มีความเฉพาะเจาะจง ในขณะที่ค่าสูงมาพร้อมกับความไม่แน่นอนมากขึ้น | - **0.1–0.3**: เฉพาะเจาะจง, กำหนดได้ (เหมาะสำหรับการสรุป) <br> **0.5–0.7**: สมดุล (ใช้งานทั่วไป) <br> **0.8–1.0**: สร้างสรรค์, หลากหลาย (ระดมความคิด) |
| `top_p` | Nucleus Sampling - ค่าต่ำจำกัดโมเดลให้ผลลัพธ์แคบลง | **0.1-0.5**: เข้มงวด, คาดเดาได้ <br> **0.9-0.95**: (มาตรฐาน, เป็นธรรมชาติ, เหมือนการสนทนา) |


## การประยุกต์ใช้งานในโลกจริง

- **การวิเคราะห์บทความวิจัย**: ดึงข้อค้นพบสำคัญจากสิ่งพิมพ์ที่ซับซ้อนเพื่อการทบทวนอย่างรวดเร็ว
- **การรวบรวมข่าว**: สรุปบทความข่าวเป็นสรุปประจำวันหรือไฮไลต์ที่กระชับ
- **บันทึกการประชุม**: ย่อบันทึกการถอดความเป็นรายการที่ดำเนินการได้และสรุปที่กระชับ
- **การตรวจสอบเอกสารทางกฎหมาย**: ดึงข้อกำหนดหรือภาระผูกพันที่เกี่ยวข้องจากข้อความทางกฎหมายที่ยาวได้อย่างรวดเร็ว
- **เอกสารโค้ด**: สร้างภาพรวม repository และคำอธิบายฟังก์ชันที่กระชับ

## ขั้นตอนถัดไป

- **การ Fine-tuning**: ปรับโมเดลให้เข้ากับสาขาหรือศัพท์เฉพาะของคุณเพื่อความแม่นยำที่ดีขึ้น (ดู Fine-tuning Playbooks)
- **ระบบ RAG**: รวม LLM กับการดึงข้อมูลเอกสารเพื่อคำตอบและการค้นหาที่รับรู้บริบท
- **การสำรวจโมเดล**: ทดลองกับโมเดลใหม่ๆ เช่น Llama 3, Phi-3 หรือ Qwen เพื่อผลลัพธ์ที่ดีขึ้น
- **การ Deploy ในระดับ Production**: ใช้เครื่องมืออย่าง vLLM สำหรับการให้บริการ LLM ที่ปรับขนาดได้ในองค์กร

ระบบของคุณมอบพลังในการรันโมเดลภาษาที่ซับซ้อนในเครื่อง ทดลองกับโมเดล prompt และพารามิเตอร์ต่างๆ เพื่อค้นหาสิ่งที่เหมาะสมที่สุดสำหรับแอปพลิเคชันของคุณ