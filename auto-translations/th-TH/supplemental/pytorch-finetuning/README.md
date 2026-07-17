<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

บทช่วยสอนนี้ให้ตัวอย่างทีละขั้นตอนสำหรับการ fine-tune โมเดลภาษาขนาดใหญ่ (LLM) ด้วย PyTorch และ ROCm ครอบคลุมเทคนิคหลายอย่าง ตั้งแต่การ fine-tune แบบมาตรฐานไปจนถึงกลยุทธ์ Parameter-Efficient Fine-Tuning (PEFT) ที่ประหยัดหน่วยความจำ เพื่อให้คุณสามารถปรับโมเดลให้เหมาะกับความต้องการของคุณได้อย่างง่ายดาย

**โมเดลที่ใช้**: google/gemma-3-4b-it  *(ดู [เปิดใช้งานการยืนยันตัวตน HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) หากเป็นโมเดลแบบ gated)*  
**ฮาร์ดแวร์**: AMD Radeon™ GPU ที่รองรับ ROCm  
**เฟรมเวิร์ก**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **หมายเหตุ:** คุณสามารถลองใช้สถาปัตยกรรมโมเดลอื่นได้เช่นกัน รวมถึง **GPT-OSS-20B** โดยแทนที่โมเดลในสคริปต์การฝึกที่ให้มา
> การ fine-tune แบบเต็มรูปแบบต้องใช้หน่วยความจำ GPU อย่างน้อย 32 GB และ RAM ของระบบ 64 GB
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **หมายเหตุ:** การ fine-tune ด้วย LoRA และ QLoRA ต้องใช้หน่วยความจำ GPU อย่างน้อย 16 GB และ RAM ของระบบ 32 GB
<!-- @device:end -->

## สิ่งที่คุณจะได้เรียนรู้

- วิธี fine-tune LLM โดยใช้ LoRA, QLoRA และการ fine-tune แบบเต็มรูปแบบด้วย PyTorch และ ROCm
- วิธีบันทึกและนำโมเดลที่ fine-tune แล้วไปใช้งาน
- วิธีตรวจสอบการฝึกและแก้ไขปัญหาที่พบบ่อย

## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ผ่าน Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

#### สร้าง Virtual Environment

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
```bash
sudo apt update 
sudo apt install -y python3-venv 
python3 -m venv finetune-venv --system-site-packages 
source finetune-venv/bin/activate 
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ให้สิทธิ์ผู้ใช้ของคุณในการเข้าถึงอุปกรณ์ GPU** (ออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv finetune-venv
source finetune-venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### การติดตั้ง Dependencies พื้นฐาน
<!-- @require:pytorch -->

#### Dependencies เพิ่มเติม

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** มีเพียงแพ็กเกจหลักเท่านั้นที่ได้รับการทดสอบและรองรับที่นี่ **bitsandbytes ไม่รองรับ Windows เป็นอย่างดี** ดังนั้นการติดตั้งบน Windows จึงละเว้นส่วนนี้ ให้ใช้ LoRA หรือการ fine-tune แบบเต็มรูปแบบบน Windows (QLoRA ต้องใช้ bitsandbytes และมีไว้สำหรับ Linux)
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### เปิดใช้งานการยืนยันตัวตน HF (โมเดลแบบ gated หรือกำหนดเอง / ที่ไม่ได้ติดตั้งไว้ล่วงหน้า)

ในตัวอย่างนี้เราใช้ **google/gemma-3-4b-it** ซึ่งเป็นโมเดลแบบ **gated** คุณต้องยอมรับข้อกำหนดของโมเดลบน Hugging Face และยืนยันตัวตนเพื่อให้สคริปต์การฝึกสามารถดาวน์โหลดได้

1. **ยอมรับใบอนุญาต:** เปิด [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) ลงชื่อเข้าใช้ (หรือสร้างบัญชี) และยอมรับใบอนุญาต/ข้อกำหนดบนหน้าโมเดล (เช่น "Agree and access repository")
2. **ติดตั้งและเข้าสู่ระบบ:** ติดตั้ง Hugging Face CLI จากนั้นรันคำสั่งเข้าสู่ระบบมาตรฐาน:

```bash
pip install huggingface_hub
hf auth login
```

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['train_qlora.py', 'train_lora.py', 'train_full_finetuning.py']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in scripts:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
from trl import SFTTrainer

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=verify-package-version timeout=60 hidden=True setup=activate-venv -->
```python
import importlib.metadata as md

pkgs = [
    "torch", "transformers", "trl", "peft", "accelerate",
    "datasets", "safetensors", "fsspec", "bitsandbytes",
    "huggingface_hub", "tokenizers",
]
for p in pkgs:
    try:
        print(f"{p}: {md.version(p)}")
    except md.PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
```
<!-- @test:end -->

<!-- @test:id=quick-train-lora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=quick-train-qlora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_qlora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=quick-train-full-finetuning timeout=1200 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_full_finetuning.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @device:end -->
---

## ทำความเข้าใจเทคนิคต่างๆ

### LoRA คืออะไร?

**LoRA (Low-Rank Adaptation)** คือการเก็บโมเดลพื้นฐานไว้แบบ frozen และฝึกเฉพาะเมทริกซ์ "adapter" ขนาดเล็กที่เพิ่มเข้าไปในเลเยอร์บางส่วนเท่านั้น

- **แนวคิดหลัก**: แทนที่จะอัปเดตเมทริกซ์น้ำหนักขนาดใหญ่ที่มีพารามิเตอร์หลายล้านตัว เราเรียนรู้การอัปเดตแบบ low-rank (เมทริกซ์ขนาดเล็กสองตัวที่ผลคูณมีพารามิเตอร์น้อยกว่ามาก) ซึ่งช่วยลดพารามิเตอร์ที่ต้องฝึกและ VRAM ได้อย่างมาก ในขณะที่ยังคงคุณภาพใกล้เคียงกับการ fine-tune แบบเต็มรูปแบบ

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### QLoRA คืออะไร?

**QLoRA** รวม **การ quantization แบบ 4-bit** เข้ากับ **LoRA** โมเดลพื้นฐานจะถูกโหลดในรูปแบบ 4-bit (ประหยัดหน่วยความจำได้มาก) และฝึกเฉพาะ LoRA adapters ในความแม่นยำที่สูงกว่า ดังนั้นคุณจะได้รับประสิทธิภาพด้านพารามิเตอร์ของ LoRA บวกกับ VRAM ที่ต่ำกว่ามาก โดยมีการสูญเสียคุณภาพเล็กน้อยเมื่อเทียบกับ LoRA แบบความแม่นยำเต็ม โปรดทราบว่าการ quantization แบบ 4-bit อาจทำให้เกิดความไม่เสถียรทางตัวเลข (loss spikes หรือ NaN) ดังนั้นผู้ใช้มักจะชอบใช้ **LoRA** หากมี VRAM เพียงพอ

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **หมายเหตุ**: สำหรับโมเดลพื้นฐาน MXFP4 เช่น `openai/gpt-oss-20b` เราแนะนำให้ใช้ **LoRA** (`train_lora.py`) แทน QLoRA เส้นทาง `bitsandbytes` 4-bit ของสคริปต์ QLoRA มักจะ dequantize น้ำหนัก MXFP4 เป็น BF16 ดังนั้นการรันจะทำงานเหมือน LoRA มาตรฐาน MXFP4 แบบ native ต้องใช้ `bitsandbytes` ที่ build จาก source พร้อมกับ Transformers/Triton/kernels stack ที่ตรงกัน ดู [เอกสาร Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)

---

### 2. เลือกวิธีการของคุณ

| วิธีการ | หน่วยความจำ | ความเร็ว | คุณภาพ | เหมาะสำหรับ |
|--------|--------|-------|---------|----------|
| **QLoRA** (Linux เท่านั้น) | 12-16GB | เร็วที่สุด | 90-95% | การใช้หน่วยความจำต่ำ |
| **LoRA** | 24-32GB | เร็ว | 95-98% | แนวทางที่สมดุล |
| **Full** | 80GB+ | ช้าที่สุด | 100% | คุณภาพสูงสุด |

### 3. รันการฝึก

**ชุดข้อมูลและสิ่งที่โมเดลเรียนรู้**  
สคริปต์จะแปลงชุดข้อมูลเป็นตัวอย่างการสนทนา ตัวอย่างเช่น สคริปต์ QLoRA ใช้ **Abirate/english_quotes**: แต่ละตัวอย่างจะกลายเป็นคู่ user–assistant เช่น:

- **User:** "Give me a quote about: &lt;tag&gt;"
- **Assistant:** "&lt;quote&gt; – &lt;author&gt;"

การ fine-tune สอนให้โมเดลตอบสนองต่อ prompt ที่ขอคำพูดเกี่ยวกับหัวข้อหนึ่งและส่งคืนในรูปแบบ `<quote text> - <author>` สคริปต์ LoRA และการ fine-tune แบบเต็มรูปแบบใช้ **databricks/databricks-dolly-15k** (คู่คำสั่ง/การตอบสนองทั่วไป) ดังนั้นงานที่แน่นอนจะแตกต่างกันตามสคริปต์ แนวคิดเดียวกันคือ - ปรับโมเดลให้เข้ากับชุดข้อมูลและรูปแบบที่คุณเลือก

ด้านล่างนี้คือสรุปของวิธีการฝึกที่มีอยู่ แต่ละวิธีเชื่อมโยงไปยังสคริปต์และให้คำอธิบายสั้นๆ สำหรับการเลือกแนวทางที่เหมาะสม

| สคริปต์                           | วิธีการ            | คำอธิบาย                                                                                                         | VRAM ทั่วไป | แนะนำสำหรับ                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | ฝึกเมทริกซ์ adapter ขนาดเล็กในขณะที่ freeze โมเดลพื้นฐาน เร็วกว่า 3–5 เท่า; คุณภาพ ~95–98% ของแบบเต็มรูปแบบ                         | 24–32GB      | ผู้ใช้ขั้นสูง; adapters หลายตัว; VRAM มากกว่า    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux เท่านั้น)*             | **QLoRA**       | การ quantization แบบ 4-bit + LoRA adapters ใช้หน่วยความจำน้อยที่สุด เร็วที่สุด มีการสูญเสียคุณภาพเล็กน้อย ต้องใช้ `bitsandbytes` (Linux เท่านั้น)                            | 12–16GB      | ผู้ใช้ส่วนใหญ่; การทดลองรวดเร็ว; VRAM จำกัด      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full Fine-tuning** | อัปเดตพารามิเตอร์โมเดลทั้งหมด คุณภาพสูงสุด; ใช้หน่วยความจำและการคำนวณสูงสุด                                    | 40GB+        | คุณภาพสูงสุด; การวิจัย; VRAM ขนาดใหญ่           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **หมายเหตุ:** การ fine-tune แบบเต็มรูปแบบ (`train_full_finetuning.py`) อาจต้องใช้ RAM ของระบบมากกว่า 64GB และอาจไม่สามารถทำได้บนอุปกรณ์นี้ พิจารณาใช้ LoRA หรือ QLoRA แทน
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การ fine-tune แบบเต็มรูปแบบ (`train_full_finetuning.py`) อาจต้องใช้ RAM ของระบบมากกว่า 64GB และอาจไม่สามารถทำได้บนอุปกรณ์นี้ พิจารณาใช้ LoRA แทน
<!-- @os:end -->
<!-- @device:end -->

เพียงเลือก `Training method` ที่คุณต้องการ ดาวน์โหลดสคริปต์ที่สอดคล้องกัน และรันโดยใช้คำสั่งต่อไปนี้โดยให้ virtual environment ของคุณยังคงเปิดใช้งานอยู่:

```python
python3 train_<method_name>.py.
```

## การใช้งานโมเดลที่ Fine-Tune แล้ว

### หลังจาก Full Fine-Tuning

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### หลังจากการฝึกด้วย LoRA/QLoRA

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### รวม LoRA Adapter เข้ากับโมเดลพื้นฐาน

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**หมายเหตุ:**  
- ตรวจสอบให้แน่ใจว่าชื่อไดเรกทอรีโมเดล (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) ตรงกับโฟลเดอร์ output จริงจากการฝึก  
- หากคุณใช้ LoRA แทน QLoRA เพียงแทนที่ path ตามความเหมาะสม  
- โมเดล Gemma บางรุ่นต้องระบุ `trust_remote_code=True` ใน `from_pretrained` เพิ่มเข้าไปหากคุณเห็นคำเตือนที่เกี่ยวข้อง

สำหรับการตั้งค่าที่กำหนดเองเพิ่มเติม (padding tokens, device ฯลฯ) โปรดดูสคริปต์ที่คุณใช้สำหรับการฝึก

<!-- @test:id=verify-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-lora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LoRA output looks correct")
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-qlora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-qlora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: QLoRA output looks correct")
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=verify-full-finetuning-output timeout=300 hidden=True setup=activate-venv -->
```python
import glob
import os
import sys

out_dir = "output-gemma-3-4b-it-full"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## คู่มือการปรับแต่ง

### ใช้ชุดข้อมูลของคุณเอง

สคริปต์ทั้งหมดใช้รูปแบบชุดข้อมูลเดียวกัน แทนที่ส่วนการโหลด:

```python
from datasets import load_dataset

# Option 1: Local JSON/JSONL file
dataset = load_dataset('json', data_files='your_data.json')

# Option 2: Hugging Face Hub dataset
dataset = load_dataset('username/dataset-name')

# Option 3: CSV file
dataset = load_dataset('csv', data_files='data.csv')

# Format for chat models
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

dataset = dataset.map(format_instruction)
```

**รูปแบบชุดข้อมูลสำหรับไฟล์ JSON/JSONL ในเครื่อง:**

เมื่อใช้วิธีนี้ โปรดตรวจสอบให้แน่ใจว่าไฟล์ JSON ของคุณมีโครงสร้างที่ถูกต้องเพื่อหลีกเลี่ยงข้อผิดพลาดในการแยกวิเคราะห์

ต้องปฏิบัติตามแนวทางต่อไปนี้:
* **การจัดรูปแบบไฟล์:** ควรจัดรูปแบบไฟล์ JSON ภายใน Integrated Development Environment (IDE) เพื่อให้มั่นใจในโครงสร้างและ syntax ที่ถูกต้อง
* **คีย์ที่จำเป็น:** ไฟล์ JSON ที่กำหนดเองต้องมีคีย์ `instruction` และ `response` คีย์เหล่านี้จำเป็นสำหรับการทำงานของวิธีการอย่างถูกต้อง
```json
[
  {
    "instruction": "Your first instruction here",
    "response": "Expected response here"
  },
  {
    "instruction": "Your second instruction here",
    "response": "Expected response here"
  }
]
```
**รูปแบบชุดข้อมูลสำหรับชุดข้อมูลจาก Hugging Face Hub**

เมื่อใช้ชุดข้อมูลจาก Hugging Face โปรดตรวจสอบให้แน่ใจว่าชุดข้อมูลของคุณมีโครงสร้างที่ถูกต้องเพื่อให้การรวมเข้ากันเป็นไปอย่างราบรื่น

ควรปฏิบัติตามแนวทางต่อไปนี้:
* **คู่ Instruction-Response:** มุ่งเน้นที่ชุดข้อมูลที่มีคู่ `instruction-response` โครงสร้างนี้จำเป็นสำหรับฟังก์ชันที่ต้องการ
* **การปรับเปลี่ยนคีย์ที่กำหนดเอง:** หากชุดข้อมูลของคุณไม่เป็นไปตามโครงสร้าง `instruction-response` คุณมีตัวเลือกในการแก้ไขฟังก์ชัน `format_instruction()` ซึ่งช่วยให้คุณรองรับคีย์เฉพาะตามที่ต้องการ

ตัวอย่างการปรับ: ในกรณีที่ output ของชุดข้อมูลต้องการการปรับ คุณสามารถแก้ไขส่วน response ภายในฟังก์ชัน format_instruction() เพื่อให้เหมาะกับความต้องการของคุณ
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**รูปแบบชุดข้อมูลสำหรับไฟล์ CSV**

เพื่อรองรับสคริปต์ที่ใช้รูปแบบไฟล์ CSV คุณต้องตรวจสอบให้แน่ใจว่าไฟล์ CSV มีคอลัมน์ชื่อ `instruction` และ `response` 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### ปรับพารามิเตอร์การฝึก

แก้ไขสคริปต์การฝึกและเปลี่ยนตัวแปรให้ตรงกับเป้าหมายของคุณ: **learning rate** (`LR`), **epochs** (`EPOCHS`), **batch size** (`BATCH_SIZE`), **gradient accumulation** (`GRAD_ACCUM_STEPS`) และสำหรับ LoRA/QLoRA **rank** (`LORA_R`) สำหรับการรันที่เร็วขึ้นให้ใช้ epochs น้อยลงและ learning rate สูงขึ้น (LR) สำหรับคุณภาพที่ดีขึ้นให้ใช้ epochs มากขึ้นและ LR ต่ำลง ลด batch size หรือความยาว sequence หากพบข้อผิดพลาด out-of-memory

### เคล็ดลับการเพิ่มประสิทธิภาพหน่วยความจำ

หากคุณพบข้อผิดพลาด out-of-memory:

**1. ลด Batch Size:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. ลดความยาว Sequence:**
```python
max_seq_length=256  # Instead of 512
```

**3. ใช้การ Quantization ที่เข้มข้นขึ้น:**
```
Full → LoRA → QLoRA
```

**4. เปิดใช้งาน Gradient Checkpointing (สำหรับการ fine-tune แบบเต็มรูปแบบเท่านั้น):**
```python
model.gradient_checkpointing_enable()
```

---

## การตรวจสอบและการแก้ไขปัญหา

### ดูหน่วยความจำ GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (ไม่บังคับ) ติดตามการทดลองด้วย Weights & Biases

เพื่อบันทึกการรันและ metrics ไปยัง [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

ในสคริปต์การฝึก ตั้งค่า `report_to="wandb"` และเลือกตั้งค่า `run_name="your-experiment-name"` ใน trainer config หากคุณไม่ต้องการใช้ Wandb ให้ปล่อย `report_to` ไว้ที่ค่าเริ่มต้นหรือตั้งค่าเป็น `"none"`

### ปัญหาที่พบบ่อย

#### Out of Memory (OOM)

**วิธีแก้ไข:** ลด batch size และ/หรือใช้ QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Loss ไม่ลดลง

**วิธีแก้ไข:** ปรับ learning rate
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### การฝึกช้า

**วิธีแก้ไข:** เพิ่ม batch size หากหน่วยความจำอนุญาต
```python
BATCH_SIZE = 8
```
## ขั้นตอนถัดไป

หลังจากที่คุณทำการ fine-tune สำเร็จแล้ว ให้พิจารณาขั้นตอนถัดไปต่อไปนี้เพื่อให้ได้ประโยชน์มากขึ้นจากโมเดลของคุณ:

1. **ประเมิน** อย่างละเอียดบนข้อมูลทดสอบที่แยกไว้เพื่อวัดการ generalization และหลีกเลี่ยง overfitting
2. **ทดลอง** โดยลองค่า hyperparameter ต่างๆ เพื่อความแม่นยำ ความเร็ว และการแลกเปลี่ยนหน่วยความจำที่ดีขึ้น
3. **ติดตาม** การทดลองทั้งหมดของคุณ (และ metrics ที่สอดคล้องกัน) ด้วย Weights & Biases เพื่อการวิจัยที่ทำซ้ำได้
4. **ลอง** ฝึกบนชุดข้อมูลที่กำหนดเองของคุณเพื่อปรับโมเดลให้เหมาะกับกรณีการใช้งานของคุณโดยเฉพาะ
5. **นำไปใช้งาน** โมเดลที่ fine-tune แล้วของคุณสำหรับการ inference ที่รวดเร็ว