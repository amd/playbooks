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


ต้องการรันโมเดลภาษา AI ที่ทรงพลังบนฮาร์ดแวร์ของคุณเองหรือไม่? คู่มือนี้จะแสดงวิธีการให้คุณ
บทช่วยสอนนี้ใช้ PyTorch ที่ขับเคลื่อนด้วยซอฟต์แวร์ AMD ROCm™ เพื่อรันโมเดลที่สามารถสรุปเอกสาร ตอบคำถาม สร้างข้อความ และอื่นๆ ได้ โดยรันภายในเครื่องทั้งหมด

## สิ่งที่คุณจะได้เรียนรู้

- รัน LLM อย่าง gpt-oss-20b และ qwen3.5-4B บนเครื่องโดยใช้ PyTorch และ ROCm
- สร้างเครื่องมือสรุปเอกสารโดยใช้ LLM

<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ด้วย Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

### สร้างสภาพแวดล้อมเสมือน (Virtual Environment)

<!-- @os:linux -->
<!-- @device:halo_box -->
บน Linux ให้เปิดเทอร์มินัลในไดเรกทอรีที่คุณต้องการ แล้วทำตามคำสั่งเพื่อสร้าง venv ที่ติดตั้ง ROCm+Pytorch ไว้เรียบร้อยแล้ว
<!-- @test:id=create-venv timeout=300 -->
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
**ให้สิทธิ์ผู้ใช้ของคุณเข้าถึงอุปกรณ์ GPU** (ต้องออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

บน Linux ให้เปิดเทอร์มินัลในไดเรกทอรีที่คุณต้องการ แล้วทำตามคำสั่งเพื่อสร้าง venv
<!-- @test:id=create-venv timeout=300 -->
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
บน Windows ให้เปิดเทอร์มินัลในไดเรกทอรีที่คุณต้องการ แล้วทำตามคำสั่งเพื่อสร้าง venv ที่ติดตั้ง ROCm+Pytorch ไว้เรียบร้อยแล้ว
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
บน Windows ให้เปิดเทอร์มินัลในไดเรกทอรีที่คุณต้องการ แล้วทำตามคำสั่งเพื่อสร้าง venv
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องปรับเปลี่ยน PowerShell Execution Policy (เช่น
> ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนที่จะรันคำสั่ง Powershell บางคำสั่ง

<!-- @os:end -->

### การติดตั้งการพึ่งพาพื้นฐาน (Basic Dependencies)
<!-- @require:driver,pytorch -->

### การติดตั้งการพึ่งพาเพิ่มเติม (Additional Dependencies)

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
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
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

> **หมายเหตุ:** หากโมเดลไม่สามารถโหลดได้หรือหน่วยความจำไม่เพียงพอ ให้ลองติดตั้งแพ็กเกจ `kernels` เพื่อโหลดโมเดลด้วยการควอนไทซ์ (quantization) ที่ปรับให้เหมาะสมแล้ว
>
> ```bash
> # Use this version which is compatible with the Transformers version
> pip install "kernels==0.14.1" 
> ```
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
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## เริ่มต้นอย่างรวดเร็วด้วยสคริปต์ตัวอย่าง

ชุดคู่มือนี้มีสคริปต์ที่พร้อมใช้งานทันที คลิกเพื่อดูตัวอย่างและดาวน์โหลดไปยังไดเรกทอรีเดียวกันกับสภาพแวดล้อมที่คุณสร้างขึ้น

| สคริปต์ | คำอธิบาย | การใช้งาน |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | การสร้างข้อความ LLM พื้นฐาน | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | เครื่องมือสรุปเอกสารที่รองรับ Harmony | `python summarizer.py --file document.txt` |

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
- การจัดรูปแบบ chat template สำหรับการสร้างพรอมต์โมเดลที่เหมาะสม โดยเฉพาะอย่างยิ่งสำหรับการสรุปเอกสาร

## การโหลดและรัน LLM ตัวแรกของคุณ

สคริปต์ [run_llm.py](assets/run_llm.py) ที่แนบมาแสดงวิธีการสร้างข้อความด้วย LLM โดยใช้ PyTorch และ AMD ROCm

> **หมายเหตุ:** เมื่อคุณโหลดโมเดล Hugging Face Transformers จะตรวจสอบแคชในเครื่องก่อน (`~/.cache/huggingface/hub` บน Linux, `C:\Users\<user>\.cache\huggingface\hub` บน Windows) หากไม่มีโมเดลนั้นอยู่ในแคช ระบบจะดาวน์โหลดโดยอัตโนมัติจาก huggingface.co การรันครั้งแรกอาจใช้เวลาสักครู่ ขึ้นอยู่กับขนาดโมเดลและความเร็วเครือข่าย

ตัวอย่างโค้ดด้านล่างแสดงวิธีการใช้โมเดลและปรับแต่งคำถามที่ถาม

<!-- @test:id=verify-imports timeout=300 hidden=True setup=activate-venv -->
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
    device_map="auto",
    disable_mmap=True
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

เมื่อคุณได้สร้างผลลัพธ์ LLM ในเครื่องแล้ว คุณสามารถต่อยอดด้วยการสร้างเครื่องมือสรุปเอกสารที่ใช้งานได้จริง ในส่วนนี้ คุณจะใช้สคริปต์ [summarizer.py](assets/summarizer.py) เพื่อป้อนไฟล์ .txt และสร้างบทสรุปที่กระชับโดยอัตโนมัติ โดยรันบน GPU ของคุณทั้งหมด

สคริปต์นี้ได้รับการออกแบบให้ใช้งานได้ทันทีโดยไม่ต้องปรับแต่งใดๆ เปิดสคริปต์ในตัวแก้ไขเพื่อสำรวจโค้ด ปรับแต่งพรอมต์ และปรับพารามิเตอร์ เช่น ความยาวและอุณหภูมิ (temperature)

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

| พารามิเตอร์ | สิ่งที่ควบคุม | ค่าโดยทั่วไป |
|-----------|------------------|----------------|
| `max_new_tokens` | ความยาวสูงสุดของผลลัพธ์จาก LLM | ใช้ 50–500 โทเคนสำหรับบทสรุป (1 โทเคนมีค่าประมาณ 0.75 คำภาษาอังกฤษ) |
| `temperature` | ความคิดสร้างสรรค์ ค่าต่ำทำให้เน้นความแม่นยำ ในขณะที่ค่าสูงจะมีความไม่แน่นอนมากขึ้น | - **0.1–0.3**: เน้นความแม่นยำ กำหนดผลลัพธ์ชัดเจน (เหมาะสำหรับบทสรุป) <br> **0.5–0.7**: สมดุล (ใช้งานทั่วไป) <br> **0.8–1.0**: สร้างสรรค์ หลากหลาย (ระดมความคิด) |
| `top_p` | Nucleus Sampling - ค่าต่ำจำกัดโมเดลให้ได้ผลลัพธ์ที่แคบลง | **0.1-0.5**: เข้มงวด คาดเดาได้ <br> **0.9-0.95**: (มาตรฐาน เป็นธรรมชาติ สนทนาได้) |


## การใช้งานในโลกจริง

- **การวิเคราะห์เอกสารวิจัย**: ดึงข้อค้นพบสำคัญจากสิ่งพิมพ์ที่ซับซ้อนเพื่อทบทวนอย่างรวดเร็ว
- **การรวบรวมข่าวสาร**: สรุปบทความข่าวเป็นสรุปประจำวันแบบสั้นหรือไฮไลต์
- **บันทึกการประชุม**: ย่อบทถอดความให้เป็นรายการที่ปฏิบัติได้และบทสรุปที่กระชับ
- **การตรวจสอบเอกสารกฎหมาย**: ดึงข้อกำหนดหรือข้อผูกพันที่เกี่ยวข้องจากเอกสารกฎหมายยาวๆ ได้อย่างรวดเร็ว
- **เอกสารประกอบโค้ด**: สร้างภาพรวมของ repository และคำอธิบายฟังก์ชันที่กระชับ
## ขั้นตอนถัดไป

- **Fine-tuning**: ปรับแต่งโมเดลให้เข้ากับสาขาหรือศัพท์เฉพาะของคุณเพื่อความแม่นยำที่ดียิ่งขึ้น (ดู Fine-tuning Playbooks)
- **ระบบ RAG**: รวม LLM เข้ากับการดึงข้อมูลเอกสารเพื่อให้ได้คำตอบและการค้นหาที่คำนึงถึงบริบท
- **การสำรวจโมเดล**: ทดลองใช้โมเดลใหม่ๆ เช่น Llama 3, Phi-3 หรือ Qwen เพื่อผลลัพธ์ที่ดียิ่งขึ้น
- **การใช้งานจริงในระดับ Production**: ใช้เครื่องมืออย่าง vLLM สำหรับการให้บริการ LLM ที่รองรับการขยายขนาดในองค์กร

ระบบของคุณมอบพลังในการรันโมเดลภาษาที่ซับซ้อนได้ในเครื่องของคุณเอง ลองทดลองใช้โมเดล พรอมต์ และพารามิเตอร์ที่แตกต่างกันเพื่อค้นหาสิ่งที่เหมาะสมที่สุดสำหรับแอปพลิเคชันของคุณ