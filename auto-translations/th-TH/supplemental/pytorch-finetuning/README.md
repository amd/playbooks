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

บทแนะนำนี้มีตัวอย่างทีละขั้นตอนสำหรับการปรับแต่งโมเดลภาษาขนาดใหญ่ (LLM) ด้วย PyTorch และ ROCm โดยครอบคลุมเทคนิคหลายแบบ ตั้งแต่การปรับแต่งมาตรฐานไปจนถึงกลยุทธ์ Parameter-Efficient Fine-Tuning (PEFT) ที่ประหยัดหน่วยความจำ เพื่อให้คุณสามารถปรับแต่งโมเดลให้เหมาะกับความต้องการของคุณได้อย่างง่ายดาย

**โมเดลที่ใช้**: google/gemma-3-4b-it  *(ดู [เปิดใช้งานการยืนยันตัวตน HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) หากเป็นโมเดลที่ถูกจำกัดสิทธิ์)*  
**ฮาร์ดแวร์**: AMD Radeon™ GPU ที่รองรับ ROCm  
**เฟรมเวิร์ก**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **หมายเหตุ:** 
> - การปรับแต่งแบบเต็มรูปแบบ (Full fine-tuning) ต้องการ **RAM ระบบอย่างน้อย 64 GB** โดยต้องมีอย่างน้อย **32 GB ที่ใช้งานได้กับ GPU** (32 GB นี้เป็นส่วนหนึ่งของ 64 GB ไม่ใช่เพิ่มเติมจากนั้น)
> - คุณยังสามารถลองใช้สถาปัตยกรรมโมเดลอื่นๆ ได้ รวมถึง **GPT-OSS-20B** โดยการแทนที่โมเดลในสคริปต์การฝึกที่ให้มา
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **หมายเหตุ:** การปรับแต่งด้วย LoRA และ QLoRA ต้องการ **RAM ระบบอย่างน้อย 32 GB** โดยต้องมีอย่างน้อย **16 GB ที่ใช้งานได้กับ GPU** (16 GB นี้เป็นส่วนหนึ่งของ 32 GB ไม่ใช่เพิ่มเติมจากนั้น)
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การปรับแต่งด้วย LoRA ต้องการ **RAM ระบบอย่างน้อย 32 GB** โดยต้องมีอย่างน้อย **16 GB ที่ใช้งานได้กับ GPU** (16 GB นี้เป็นส่วนหนึ่งของ 32 GB ไม่ใช่เพิ่มเติมจากนั้น)
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **หมายเหตุ:** การปรับแต่งด้วย LoRA และ QLoRA ต้องการการ์ดกราฟิกที่มี **หน่วยความจำ GPU เฉพาะอย่างน้อย 16 GB** และ **RAM ระบบ 32 GB**
> - บน Linux การฝึกจะทำงานทั้งหมดภายในหน่วยความจำ VRAM เฉพาะของการ์ดกราฟิก
> - ระบบจะไม่สลับไปใช้หน่วยความจำ GPU ที่ใช้ร่วมกัน (RAM ระบบ) เมื่อ VRAM หมด
> - การ์ดที่มี VRAM เฉพาะน้อยกว่า 16 GB จะประสบปัญหาหน่วยความจำไม่พอระหว่างการฝึกบน Linux แม้ว่าระบบจะมี RAM เหลือเฟือก็ตาม
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การปรับแต่งด้วย LoRA ต้องการ **หน่วยความจำ GPU รวมอย่างน้อย 16 GB** และ **RAM ระบบ 32 GB**
> - บน Windows หน่วยความจำ GPU รวมประกอบด้วย VRAM เฉพาะของการ์ดกราฟิกรวมกับหน่วยความจำ GPU ที่ใช้ร่วมกัน (ยืมมาจาก RAM ระบบ)
> - ดังนั้น การ์ดที่มี VRAM เฉพาะน้อยกว่า 16 GB ยังคงสามารถใช้งานคู่มือนี้ได้โดยใช้หน่วยความจำ GPU ที่ใช้ร่วมกันเพื่อชดเชยส่วนต่าง
<!-- @os:end -->
<!-- @device:end -->

## สิ่งที่คุณจะได้เรียนรู้

- วิธีปรับแต่ง LLM โดยใช้ LoRA, QLoRA และการปรับแต่งแบบเต็มรูปแบบด้วย PyTorch และ ROCm
- วิธีบันทึกและปรับใช้โมเดลที่ปรับแต่งแล้วของคุณ
- วิธีตรวจสอบการฝึกและแก้ไขปัญหาทั่วไป

## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ด้วย Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

#### สร้างสภาพแวดล้อมเสมือน (Virtual Environment)

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
**ให้สิทธิ์ผู้ใช้ของคุณเข้าถึงอุปกรณ์ GPU** (ออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

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

#### การติดตั้งไลบรารีพื้นฐานที่จำเป็น
<!-- @require:pytorch -->

#### ไลบรารีเพิ่มเติมที่จำเป็น

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** มีการทดสอบและรองรับเฉพาะแพ็กเกจหลักเท่านั้นในที่นี้ **bitsandbytes ไม่ได้รับการรองรับที่ดีบน Windows** ดังนั้นการติดตั้งบน Windows จึงไม่รวม bitsandbytes เข้ามาด้วย ให้ใช้ LoRA หรือการปรับแต่งแบบเต็มรูปแบบบน Windows (QLoRA ต้องการ bitsandbytes และมีไว้สำหรับ Linux)
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### เปิดใช้งานการยืนยันตัวตน HF (โมเดลที่ถูกจำกัดสิทธิ์หรือแบบกำหนดเอง / ที่ไม่ได้ติดตั้งไว้ล่วงหน้า)

ในตัวอย่างนี้เราใช้ **google/gemma-3-4b-it** ซึ่งเป็นโมเดลที่ **ถูกจำกัดสิทธิ์ (gated)** คุณต้องยอมรับข้อกำหนดของโมเดลบน Hugging Face ก่อน จากนั้นจึงยืนยันตัวตนเพื่อให้สคริปต์การฝึกสามารถดาวน์โหลดโมเดลได้

1. **ยอมรับใบอนุญาต:** เปิด [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) ลงชื่อเข้าใช้ (หรือสร้างบัญชี) และยอมรับใบอนุญาต/ข้อกำหนดบนหน้าโมเดล (เช่น "Agree and access repository")
2. **ติดตั้งและลงชื่อเข้าใช้:** ติดตั้ง Hugging Face CLI จากนั้นรันคำสั่งลงชื่อเข้าใช้แบบมาตรฐาน:

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

**LoRA (Low-Rank Adaptation)** จะคงโมเดลพื้นฐานให้อยู่ในสถานะแช่แข็ง (frozen) และฝึกเฉพาะเมทริกซ์ "อะแดปเตอร์" (adapter) ขนาดเล็กที่ถูกเพิ่มเข้าไปในเลเยอร์บางส่วนเท่านั้น 

- **แนวคิดหลัก**: แทนที่จะอัปเดตเมทริกซ์น้ำหนักขนาดใหญ่ที่มีพารามิเตอร์นับล้าน เราเรียนรู้การอัปเดตแบบอันดับต่ำ (low-rank) แทน (เมทริกซ์ขนาดเล็กสองตัวที่ผลคูณของมันมีพารามิเตอร์น้อยกว่ามาก) ซึ่งช่วยลดพารามิเตอร์ที่ต้องฝึกและ VRAM ได้อย่างมาก ในขณะที่ยังคงคุณภาพส่วนใหญ่ของการปรับแต่งแบบเต็มรูปแบบไว้

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

**QLoRA** ผสมผสาน **การควอนไทซ์แบบ 4-bit** เข้ากับ **LoRA** โมเดลพื้นฐานจะถูกโหลดในรูปแบบ 4-bit (ประหยัดหน่วยความจำได้มาก) และมีเพียงอะแดปเตอร์ LoRA เท่านั้นที่ถูกฝึกในความละเอียดที่สูงกว่า ดังนั้นคุณจะได้ทั้งประสิทธิภาพด้านพารามิเตอร์ของ LoRA บวกกับการใช้ VRAM ที่ต่ำกว่ามาก โดยมีการแลกเปลี่ยนด้านคุณภาพเล็กน้อยเมื่อเทียบกับ LoRA แบบความละเอียดเต็ม โปรดทราบว่าการควอนไทซ์แบบ 4-bit อาจทำให้เกิดความไม่เสถียรทางตัวเลข (loss spikes หรือ NaN) ดังนั้นผู้ใช้มักนิยม **LoRA** หากมี VRAM เพียงพอ

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **หมายเหตุ**: สำหรับโมเดลพื้นฐาน MXFP4 อย่าง `openai/gpt-oss-20b` เราแนะนำให้ใช้ **LoRA** (`train_lora.py`) แทน QLoRA เนื่องจากเส้นทาง 4-bit ของ `bitsandbytes` ในสคริปต์ QLoRA มักจะทำการ dequantize น้ำหนัก MXFP4 ไปเป็น BF16 ทำให้การรันทำงานเหมือนกับ LoRA มาตรฐาน MXFP4 แบบเนทีฟต้องการ `bitsandbytes` ที่สร้างจากซอร์สโค้ดพร้อมกับชุด Transformers/Triton/kernels ที่ตรงกัน ดูรายละเอียดที่ [เอกสาร Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)

---
### 2. เลือกวิธีการของคุณ

| วิธีการ | หน่วยความจำ | ความเร็ว | คุณภาพ | เหมาะสำหรับ |
|--------|--------|-------|---------|----------|
| **QLoRA** (เฉพาะ Linux) | 12-16GB | เร็วที่สุด | 90-95% | การใช้หน่วยความจำต่ำ |
| **LoRA** | 24-32GB | เร็ว | 95-98% | แนวทางที่สมดุล |
| **Full** | 80GB+ | ช้าที่สุด | 100% | คุณภาพสูงสุด |

### 3. เริ่มการฝึก

**ชุดข้อมูลและสิ่งที่โมเดลเรียนรู้**  
สคริปต์เหล่านี้จะแปลงชุดข้อมูลให้เป็นตัวอย่างการสนทนา ตัวอย่างเช่น สคริปต์ QLoRA ใช้ **Abirate/english_quotes**: แต่ละตัวอย่างจะกลายเป็นคู่ user–assistant ดังนี้:

- **User:** "Give me a quote about: &lt;tag&gt;"
- **Assistant:** "&lt;quote&gt; – &lt;author&gt;"

การปรับแต่งจะสอนให้โมเดลตอบสนองต่อพรอมป์ที่ขอคำคมเกี่ยวกับหัวข้อหนึ่ง และส่งคืนในรูปแบบ `<quote text> - <author>` สคริปต์ LoRA และ full fine-tuning ใช้ **databricks/databricks-dolly-15k** (คู่ instruction/response ทั่วไป) ดังนั้นงานที่แท้จริงจะแตกต่างกันไปตามสคริปต์ แต่แนวคิดหลักยังคงเหมือนเดิม - ปรับโมเดลให้เข้ากับชุดข้อมูลและรูปแบบที่คุณเลือก

ด้านล่างนี้คือสรุปวิธีการฝึกที่มีให้ใช้งาน แต่ละวิธีมีลิงก์ไปยังสคริปต์ของตนเองและมีคำอธิบายสั้น ๆ เพื่อช่วยเลือกแนวทางที่เหมาะสม

| Script                           | Method            | Description                                                                                                         | Typical VRAM | Recommended For                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | ฝึก adapter matrices ขนาดเล็กในขณะที่ freeze โมเดลฐาน เร็วกว่า 3–5 เท่า; คุณภาพประมาณ 95–98% ของเต็มรูปแบบ                         | 24–32GB      | ผู้ใช้ขั้นสูง; adapter หลายตัว; VRAM มากกว่า    |
| [`train_qlora.py`](assets/train_qlora.py)  *(เฉพาะ Linux)*             | **QLoRA**       | การควอนไทซ์ 4-bit + LoRA adapters ใช้หน่วยความจำน้อยที่สุด เร็วที่สุด แลกกับคุณภาพที่ลดลงเล็กน้อย ต้องใช้ `bitsandbytes` (เฉพาะ Linux)                            | 12–16GB      | ผู้ใช้ส่วนใหญ่; การทดลองที่รวดเร็ว; VRAM จำกัด      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full Fine-tuning** | อัปเดตพารามิเตอร์ทั้งหมดของโมเดล คุณภาพสูงสุด; ใช้หน่วยความจำและการประมวลผลมากที่สุด                                    | 40GB+        | คุณภาพสูงสุด; งานวิจัย; VRAM ขนาดใหญ่           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **หมายเหตุ:** Full fine-tuning (`train_full_finetuning.py`) อาจต้องการ RAM ระบบมากกว่า 64GB และอาจไม่สามารถทำได้บนอุปกรณ์นี้ ควรพิจารณาใช้ LoRA หรือ QLoRA แทน
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** Full fine-tuning (`train_full_finetuning.py`) อาจต้องการ RAM ระบบมากกว่า 64GB และอาจไม่สามารถทำได้บนอุปกรณ์นี้ ควรพิจารณาใช้ LoRA แทน
<!-- @os:end -->
<!-- @device:end -->

เพียงเลือก `Training method` ที่คุณต้องการ ดาวน์โหลดสคริปต์ที่เกี่ยวข้อง และรันโดยใช้คำสั่งขณะที่ virtual environment ของคุณยังเปิดใช้งานอยู่: 

```python
python3 train_<method_name>.py.
```

## การใช้งานโมเดลที่ผ่านการปรับแต่งของคุณ

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

### หลังจากการฝึก LoRA/QLoRA

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

### รวม LoRA Adapter เข้ากับโมเดลฐาน

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**หมายเหตุ:**  
- ตรวจสอบให้แน่ใจว่าชื่อไดเรกทอรีของโมเดล (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) ตรงกับโฟลเดอร์ผลลัพธ์จริงจากการฝึกของคุณ  
- หากคุณใช้ LoRA แทน QLoRA เพียงแทนที่พาธให้ตรงกัน  
- โมเดล Gemma บางรุ่นต้องการการระบุ `trust_remote_code=True` ใน `from_pretrained` ให้เพิ่มหากคุณเห็นคำเตือนที่เกี่ยวข้อง

สำหรับการตั้งค่าที่กำหนดเองเพิ่มเติม (padding tokens, device เป็นต้น) ให้ดูที่สคริปต์ที่คุณใช้ในการฝึก

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

สคริปต์ทั้งหมดใช้รูปแบบชุดข้อมูลเดียวกัน แทนที่ส่วนการโหลดข้อมูล:

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
* **การจัดรูปแบบไฟล์:** ไฟล์ JSON ควรถูกจัดรูปแบบภายใน Integrated Development Environment (IDE) เพื่อให้แน่ใจว่ามีโครงสร้างและไวยากรณ์ที่ถูกต้อง
* **คีย์ที่จำเป็น:** ไฟล์ JSON ที่กำหนดเองต้องมีคีย์ `instruction` และ `response` คีย์เหล่านี้มีความจำเป็นเพื่อให้วิธีการทำงานได้อย่างถูกต้อง
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

เมื่อใช้ชุดข้อมูลจาก Hugging Face โปรดตรวจสอบให้แน่ใจว่าชุดข้อมูลของคุณมีโครงสร้างที่ถูกต้องเพื่อให้สามารถผสานรวมได้อย่างราบรื่น 

ควรปฏิบัติตามแนวทางต่อไปนี้:
* **คู่ Instruction-Response:** เน้นชุดข้อมูลที่มีคู่ `instruction-response` โครงสร้างนี้มีความจำเป็นต่อการทำงานที่ตั้งใจไว้
* **การปรับเปลี่ยนคีย์ที่กำหนดเอง:** หากชุดข้อมูลของคุณไม่สอดคล้องกับโครงสร้าง `instruction-response` คุณสามารถปรับเปลี่ยนฟังก์ชัน `format_instruction()` ได้ ซึ่งช่วยให้คุณรองรับคีย์เฉพาะตามที่ต้องการ

ตัวอย่างการปรับเปลี่ยน: ในกรณีที่ผลลัพธ์ของชุดข้อมูลจำเป็นต้องปรับเปลี่ยน คุณสามารถแก้ไขส่วนการตอบสนองภายในฟังก์ชัน format_instruction() ให้เหมาะกับความต้องการของคุณ
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

เพื่อให้สคริปต์รองรับรูปแบบไฟล์ CSV คุณต้องตรวจสอบให้แน่ใจว่าไฟล์ CSV มีคอลัมน์ชื่อ `instruction` และ `response` 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### ปรับพารามิเตอร์การฝึก

แก้ไขสคริปต์การฝึกและเปลี่ยนตัวแปรให้ตรงกับเป้าหมายของคุณ: **learning rate** (`LR`), **epochs** (`EPOCHS`), **batch size** (`BATCH_SIZE`), **gradient accumulation** (`GRAD_ACCUM_STEPS`) และสำหรับ LoRA/QLoRA คือ **rank** (`LORA_R`) หากต้องการรันที่เร็วขึ้นให้ใช้ epochs น้อยลงและ learning rate (LR) สูงขึ้น หากต้องการคุณภาพที่ดีขึ้นให้ใช้ epochs มากขึ้นและ LR ต่ำลง ลดขนาด batch size หรือความยาว sequence หากพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ
### เคล็ดลับการเพิ่มประสิทธิภาพหน่วยความจำ

หากคุณพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ:

**1. ลดขนาด Batch:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. ลดความยาวของลำดับ (Sequence Length):**
```python
max_seq_length=256  # Instead of 512
```

**3. ใช้การควอนไทซ์ที่เข้มข้นขึ้น:**
```
Full → LoRA → QLoRA
```

**4. เปิดใช้งาน Gradient Checkpointing (สำหรับการ fine-tuning แบบเต็มรูปแบบเท่านั้น):**
```python
model.gradient_checkpointing_enable()
```

---

## การตรวจสอบและแก้ไขข้อบกพร่อง

### เฝ้าดูหน่วยความจำ GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (ไม่บังคับ) ติดตามการทดลองด้วย Weights & Biases

หากต้องการบันทึกการรันและเมตริกไปยัง [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

ในสคริปต์การฝึก ให้ตั้งค่า `report_to="wandb"` และหากต้องการ ให้ตั้งค่า `run_name="your-experiment-name"` ในการกำหนดค่า trainer หากคุณไม่ต้องการใช้ Wandb ให้ปล่อย `report_to` ไว้ที่ค่าเริ่มต้น หรือตั้งค่าเป็น `"none"`

### ปัญหาที่พบบ่อย

#### หน่วยความจำไม่เพียงพอ (OOM)

**วิธีแก้ไข:** ลดขนาด batch และ/หรือใช้ QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### ค่า Loss ไม่ลดลง

**วิธีแก้ไข:** ปรับ learning rate
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### การฝึกช้า

**วิธีแก้ไข:** เพิ่มขนาด batch หากหน่วยความจำเพียงพอ
```python
BATCH_SIZE = 8
```
## ขั้นตอนถัดไป

หลังจากที่คุณทำการ fine-tuning สำเร็จแล้ว ให้พิจารณาขั้นตอนถัดไปต่อไปนี้เพื่อให้ได้ประโยชน์สูงสุดจากโมเดลของคุณ:

1. **ประเมินผล** อย่างละเอียดบนชุดข้อมูลทดสอบที่แยกไว้ต่างหาก เพื่อวัดความสามารถในการทำงานทั่วไปและหลีกเลี่ยงการ overfitting
2. **ทดลอง** ด้วยการลองค่าไฮเปอร์พารามิเตอร์ต่าง ๆ เพื่อให้ได้ความสมดุลที่ดีขึ้นระหว่างความแม่นยำ ความเร็ว และการใช้หน่วยความจำ
3. **ติดตาม** การทดลองทั้งหมดของคุณ (พร้อมเมตริกที่เกี่ยวข้อง) ด้วย Weights & Biases เพื่อการวิจัยที่สามารถทำซ้ำได้
4. **ลอง** ฝึกด้วยชุดข้อมูลที่กำหนดเองของคุณเอง เพื่อปรับโมเดลให้เหมาะกับกรณีการใช้งานของคุณโดยเฉพาะ
5. **ปรับใช้** โมเดลที่ fine-tune แล้วของคุณเพื่อการอนุมานที่รวดเร็วโดยใช้ backend ที่มีประสิทธิภาพ เช่น vLLM บนฮาร์ดแวร์ที่รองรับ
6. **สำรวจ** เทคนิคขั้นสูง รวมถึงการทำ prompt engineering, mixed precision และความยาวลำดับ (sequence length) ที่ยาวขึ้น
7. **ฝึก** LoRA adapter หลายตัวสำหรับงานหรือโดเมนที่แตกต่างกัน และสลับใช้งานตามความจำเป็น

---