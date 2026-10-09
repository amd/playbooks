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

บทแนะนำนี้นำเสนอตัวอย่างทีละขั้นตอนสำหรับการปรับแต่งโมเดลภาษาขนาดใหญ่ (LLM) ด้วย PyTorch และ ROCm โดยครอบคลุมเทคนิคต่าง ๆ ตั้งแต่การปรับแต่งแบบมาตรฐานไปจนถึงกลยุทธ์ Parameter-Efficient Fine-Tuning (PEFT) ที่ประหยัดหน่วยความจำ เพื่อให้คุณสามารถปรับโมเดลให้เหมาะกับความต้องการของคุณได้อย่างง่ายดาย

**โมเดลที่ใช้**: google/gemma-3-4b-it (QLoRA script: openai/gpt-oss-20b)  *(ดู [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) หากถูกจำกัดสิทธิ์)*  
**ฮาร์ดแวร์**: AMD Radeon™ GPU ที่รองรับ ROCm  
**เฟรมเวิร์ก**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **หมายเหตุ:** 
> - การปรับแต่งแบบเต็มรูปแบบ (Full fine-tuning) ต้องการ **RAM ระบบอย่างน้อย 64 GB** โดยอย่างน้อย **32 GB ของจำนวนนี้ต้องพร้อมใช้งานสำหรับ GPU** (32 GB นี้เป็นส่วนหนึ่งของ 64 GB ไม่ใช่เพิ่มเติมจากนั้น)
> - คุณยังสามารถลองใช้สถาปัตยกรรมโมเดลอื่น ๆ รวมถึง **GPT-OSS-20B** โดยการแทนที่โมเดลในสคริปต์การฝึกที่ให้มา
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **หมายเหตุ:** การปรับแต่งแบบ LoRA และ QLoRA ต้องการ **RAM ระบบอย่างน้อย 32 GB** โดยอย่างน้อย **16 GB ของจำนวนนี้ต้องพร้อมใช้งานสำหรับ GPU** (16 GB นี้เป็นส่วนหนึ่งของ 32 GB ไม่ใช่เพิ่มเติมจากนั้น)
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การปรับแต่งแบบ LoRA ต้องการ **RAM ระบบอย่างน้อย 32 GB** โดยอย่างน้อย **16 GB ของจำนวนนี้ต้องพร้อมใช้งานสำหรับ GPU** (16 GB นี้เป็นส่วนหนึ่งของ 32 GB ไม่ใช่เพิ่มเติมจากนั้น)
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **หมายเหตุ:** การปรับแต่งแบบ LoRA และ QLoRA ต้องการการ์ดจอที่มี **หน่วยความจำ GPU เฉพาะ (dedicated) อย่างน้อย 16 GB** และ **RAM ระบบ 32 GB**
> - บน Linux การฝึกจะทำงานทั้งหมดใน VRAM เฉพาะของการ์ดจอ
> - ระบบจะไม่ถอยกลับไปใช้หน่วยความจำ GPU ที่ใช้ร่วมกัน (shared, ยืมจาก RAM ระบบ) เมื่อ VRAM หมด
> - การ์ดที่มี VRAM เฉพาะน้อยกว่า 16 GB จะหน่วยความจำไม่พอระหว่างการฝึกบน Linux แม้ว่าระบบจะมี RAM เหลือเฟือก็ตาม
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การปรับแต่งแบบ LoRA ต้องการ **หน่วยความจำ GPU รวมอย่างน้อย 16 GB** และ **RAM ระบบ 32 GB**
> - บน Windows หน่วยความจำ GPU รวมจะผสมผสาน VRAM เฉพาะของการ์ดจอกับหน่วยความจำ GPU ที่ใช้ร่วมกัน (ยืมจาก RAM ระบบ)
> - ดังนั้นการ์ดที่มี VRAM เฉพาะน้อยกว่า 16 GB ยังสามารถใช้งาน playbook นี้ได้ โดยใช้หน่วยความจำ GPU ที่ใช้ร่วมกันมาชดเชยส่วนต่าง
<!-- @os:end -->
<!-- @device:end -->

## สิ่งที่คุณจะได้เรียนรู้

- วิธีปรับแต่ง LLM โดยใช้ LoRA, QLoRA และการปรับแต่งแบบเต็มรูปแบบด้วย PyTorch และ ROCm
- วิธีบันทึกและปรับใช้โมเดลที่ปรับแต่งแล้วของคุณ
- วิธีตรวจสอบการฝึกและแก้ไขปัญหาที่พบบ่อย

<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ด้วย Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งข้อกำหนดเบื้องต้นของซอฟต์แวร์

#### สร้างสภาพแวดล้อมเสมือน (Virtual Environment)

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
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

<!-- @test:id=create-venv timeout=300 -->
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
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### การติดตั้งแพ็กเกจพื้นฐานที่จำเป็น
<!-- @require:pytorch -->

#### แพ็กเกจเพิ่มเติมที่จำเป็น

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** มีการทดสอบและรองรับเฉพาะแพ็กเกจหลักเท่านั้น **bitsandbytes ไม่ได้รับการรองรับอย่างสมบูรณ์บน Windows** ดังนั้นการติดตั้งบน Windows จะไม่รวม bitsandbytes ให้ใช้ LoRA หรือการปรับแต่งแบบเต็มรูปแบบบน Windows (QLoRA ต้องการ bitsandbytes และออกแบบมาสำหรับ Linux)
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### เปิดใช้งานการยืนยันตัวตน HF (โมเดลที่ถูกจำกัดสิทธิ์หรือโมเดลที่กำหนดเอง / ยังไม่ได้ติดตั้งไว้ล่วงหน้า)

ในตัวอย่างนี้เราใช้ **google/gemma-3-4b-it** ซึ่งเป็นโมเดลแบบ **gated** (ถูกจำกัดสิทธิ์) คุณต้องยอมรับข้อกำหนดของโมเดลบน Hugging Face ก่อน จากนั้นจึงยืนยันตัวตนเพื่อให้สคริปต์การฝึกสามารถดาวน์โหลดได้

1. **ยอมรับใบอนุญาต:** เปิด [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) ลงชื่อเข้าใช้ (หรือสร้างบัญชี) และยอมรับใบอนุญาต/ข้อกำหนดบนหน้าโมเดล (เช่น “Agree and access repository”)
2. **ติดตั้งและลงชื่อเข้าใช้:** ติดตั้ง Hugging Face CLI จากนั้นเรียกใช้คำสั่งลงชื่อเข้าใช้แบบมาตรฐาน:

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

## ทำความเข้าใจเทคนิคต่าง ๆ

### LoRA คืออะไร?

**LoRA (Low-Rank Adaptation)** จะคงโมเดลฐานไว้แบบ frozen และฝึกเฉพาะเมทริกซ์ "adapter" ขนาดเล็กที่ถูกเพิ่มเข้าไปในบางเลเยอร์เท่านั้น 

- **แนวคิดหลัก**: แทนที่จะอัปเดตเมทริกซ์น้ำหนักขนาดใหญ่ที่มีพารามิเตอร์หลายล้านตัว เราเรียนรู้การอัปเดตแบบ low-rank (เมทริกซ์ขนาดเล็กสองตัวที่ผลคูณมีพารามิเตอร์น้อยกว่ามาก) สิ่งนี้ช่วยลดจำนวนพารามิเตอร์ที่ต้องฝึกและ VRAM ได้อย่างมาก ในขณะที่ยังคงคุณภาพของการปรับแต่งแบบเต็มรูปแบบไว้ได้ส่วนใหญ่

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

**QLoRA** ผสมผสาน **การควอนไทซ์แบบ 4 บิต** เข้ากับ **LoRA** โมเดลฐานจะถูกโหลดในรูปแบบ 4 บิต (ประหยัดหน่วยความจำได้มาก) และมีเพียง LoRA adapters เท่านั้นที่ถูกฝึกด้วยความแม่นยำที่สูงกว่า ดังนั้นคุณจะได้ทั้งประสิทธิภาพด้านพารามิเตอร์ของ LoRA บวกกับ VRAM ที่ต่ำกว่ามาก โดยมีการแลกเปลี่ยนด้านคุณภาพเล็กน้อยเมื่อเทียบกับ LoRA แบบความแม่นยำเต็ม โปรดทราบว่าการควอนไทซ์แบบ 4 บิตอาจทำให้เกิดความไม่เสถียรทางตัวเลข (loss พุ่งสูงหรือ NaN) ดังนั้นผู้ใช้อาจเลือกใช้ **LoRA** แทนหากมี VRAM เพียงพอ

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **หมายเหตุ**: สำหรับโมเดลฐานแบบ MXFP4 เช่น `openai/gpt-oss-20b` เราขอแนะนำให้ใช้ **LoRA** (`train_lora.py`) แทน QLoRA เนื่องจากเส้นทาง 4 บิตของ `bitsandbytes` ในสคริปต์ QLoRA มักจะ dequantize น้ำหนัก MXFP4 กลับเป็น BF16 ทำให้การรันทำงานเหมือน LoRA แบบมาตรฐาน MXFP4 แบบเนทีฟต้องการ `bitsandbytes` ที่สร้างจากซอร์สโค้ดพร้อมกับชุด Transformers/Triton/kernels ที่เข้ากันได้ ดูที่ [Transformers MXFP4 docs](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)

---
### 2. เลือกวิธีการของคุณ

| วิธีการ | หน่วยความจำ | ความเร็ว | คุณภาพ | เหมาะสำหรับ |
|--------|--------|-------|---------|----------|
| **QLoRA** (Linux เท่านั้น) | 12-16GB | เร็วที่สุด | 90-95% | การใช้หน่วยความจำต่ำ |
| **LoRA** | 24-32GB | เร็ว | 95-98% | แนวทางที่สมดุล |
| **Full** | 80GB+ | ช้าที่สุด | 100% | คุณภาพสูงสุด |

### 3. รันการฝึก

**ชุดข้อมูลและสิ่งที่โมเดลเรียนรู้**  
สคริปต์จะแปลงชุดข้อมูลให้เป็นตัวอย่างการสนทนา ตัวอย่างเช่น สคริปต์ QLoRA ใช้ **Abirate/english_quotes**: แต่ละตัวอย่างจะกลายเป็นคู่ผู้ใช้-ผู้ช่วยเช่น:

- **ผู้ใช้:** “Give me a quote about: &lt;tag&gt;”
- **ผู้ช่วย:** “&lt;quote&gt; – &lt;author&gt;”

การปรับแต่งนี้สอนให้โมเดลตอบสนองต่อพรอมต์ที่ขอคำคมเกี่ยวกับหัวข้อหนึ่ง ๆ และส่งคืนในรูปแบบ `<quote text> - <author>` สคริปต์ LoRA และการฝึกแบบเต็มรูปแบบใช้ **databricks/databricks-dolly-15k** (คู่คำสั่ง/คำตอบทั่วไป) ดังนั้นงานที่แน่นอนจะแตกต่างกันไปตามแต่ละสคริปต์ แต่แนวคิดเหมือนกัน - ปรับโมเดลให้เข้ากับชุดข้อมูลและรูปแบบที่คุณเลือก

ด้านล่างนี้คือสรุปวิธีการฝึกที่มีอยู่ แต่ละวิธีจะลิงก์ไปยังสคริปต์ของตนเองและมีคำอธิบายสั้น ๆ เพื่อช่วยเลือกแนวทางที่เหมาะสม

| สคริปต์                           | วิธีการ            | คำอธิบาย                                                                                                         | VRAM โดยทั่วไป | แนะนำสำหรับ                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | ฝึกเมทริกซ์อะแดปเตอร์ขนาดเล็กในขณะที่ตรึงโมเดลฐานไว้ เร็วขึ้น 3–5 เท่า; คุณภาพประมาณ 95–98% ของเต็มรูปแบบ                         | 24–32GB      | ผู้ใช้ขั้นสูง; อะแดปเตอร์หลายตัว; มี VRAM มากกว่า    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux เท่านั้น)*             | **QLoRA**       | การควอนไทซ์ 4 บิต + อะแดปเตอร์ LoRA ใช้หน่วยความจำน้อยที่สุด เร็วที่สุด แลกคุณภาพเล็กน้อย ต้องใช้ `bitsandbytes` (Linux เท่านั้น)                            | 12–16GB      | ผู้ใช้ส่วนใหญ่; การทดลองที่รวดเร็ว; VRAM จำกัด      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **การปรับแต่งแบบเต็มรูปแบบ** | อัปเดตพารามิเตอร์ของโมเดลทั้งหมด คุณภาพสูงสุด; ใช้หน่วยความจำและการประมวลผลสูงที่สุด                                    | 40GB+        | คุณภาพสูงสุด; งานวิจัย; มี VRAM มาก           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **หมายเหตุ:** การปรับแต่งแบบเต็มรูปแบบ (`train_full_finetuning.py`) อาจต้องใช้ RAM ของระบบมากกว่า 64GB และอาจไม่สามารถทำได้บนอุปกรณ์นี้ ควรพิจารณาใช้ LoRA หรือ QLoRA แทน
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การปรับแต่งแบบเต็มรูปแบบ (`train_full_finetuning.py`) อาจต้องใช้ RAM ของระบบมากกว่า 64GB และอาจไม่สามารถทำได้บนอุปกรณ์นี้ ควรพิจารณาใช้ LoRA แทน
<!-- @os:end -->
<!-- @device:end -->

เพียงเลือก `Training method` ที่คุณต้องการ ดาวน์โหลดสคริปต์ที่สอดคล้องกัน และรันโดยใช้คำสั่งในขณะที่ยังเปิดใช้งาน virtual environment ของคุณอยู่: 

```python
python3 train_<method_name>.py.
```

## การใช้งานโมเดลที่ปรับแต่งแล้วของคุณ

### หลังจากการปรับแต่งแบบเต็มรูปแบบ

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
    "output-gpt-oss-20b-qlora",   # or "output-gemma-3-4b-it-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### รวมอะแดปเตอร์ LoRA เข้ากับโมเดลฐาน

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**หมายเหตุ:**  
- ตรวจสอบให้แน่ใจว่าชื่อไดเรกทอรีของโมเดล (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) ตรงกับโฟลเดอร์ผลลัพธ์จริงจากการฝึกของคุณ  
- หากคุณใช้ LoRA แทน QLoRA เพียงแทนที่พาธให้ตรงกัน  
- โมเดล Gemma บางรุ่นต้องระบุ `trust_remote_code=True` ใน `from_pretrained` ให้เพิ่มหากคุณเห็นคำเตือนที่เกี่ยวข้อง

สำหรับการตั้งค่าที่กำหนดเองเพิ่มเติม (padding tokens, device เป็นต้น) โปรดดูที่สคริปต์ที่คุณใช้ในการฝึก

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
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

# Weights may be saved as a single model.safetensors or, when the model
# exceeds max_shard_size, as model-*.safetensors shards plus an index.
single = os.path.exists(os.path.join(out_dir, "model.safetensors"))
shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not single and not shards:
    print("FAIL: No model safetensors weights found")
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
* **การจัดรูปแบบไฟล์:** ไฟล์ JSON ควรถูกจัดรูปแบบภายใน Integrated Development Environment (IDE) เพื่อให้มั่นใจว่ามีโครงสร้างและไวยากรณ์ที่ถูกต้อง
* **คีย์ที่จำเป็น:** ไฟล์ JSON ที่กำหนดเองต้องมีคีย์ `instruction` และ `response` คีย์เหล่านี้จำเป็นต่อการทำงานของวิธีการอย่างถูกต้อง
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

เมื่อใช้ชุดข้อมูลจาก Hugging Face โปรดตรวจสอบให้แน่ใจว่าชุดข้อมูลของคุณมีโครงสร้างที่ถูกต้องเพื่อให้สามารถรวมเข้ากันได้อย่างราบรื่น 

ควรปฏิบัติตามแนวทางต่อไปนี้:
* **คู่ instruction-response:** มุ่งเน้นไปที่ชุดข้อมูลที่มีคู่ `instruction-response` โครงสร้างนี้จำเป็นต่อการทำงานตามที่ตั้งใจไว้
* **การปรับเปลี่ยนคีย์ที่กำหนดเอง:** หากชุดข้อมูลของคุณไม่สอดคล้องกับโครงสร้าง `instruction-response` คุณสามารถปรับเปลี่ยนฟังก์ชัน `format_instruction()` ได้ ซึ่งจะช่วยให้คุณรองรับคีย์เฉพาะตามที่ต้องการ

ตัวอย่างการปรับเปลี่ยน: ในกรณีที่ผลลัพธ์ของชุดข้อมูลต้องมีการปรับเปลี่ยน คุณสามารถแก้ไขส่วนคำตอบภายในฟังก์ชัน format_instruction() เพื่อให้เหมาะกับความต้องการของคุณได้
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

### ปรับค่าพารามิเตอร์การฝึก

แก้ไขสคริปต์การฝึกและเปลี่ยนตัวแปรให้ตรงกับเป้าหมายของคุณ: **learning rate** (`LR`), **epochs** (`EPOCHS`), **batch size** (`BATCH_SIZE`), **gradient accumulation** (`GRAD_ACCUM_STEPS`) และสำหรับ LoRA/QLoRA **rank** (`LORA_R`) หากต้องการให้รันเร็วขึ้น ให้ใช้จำนวน epoch น้อยลงและ learning rate (LR) สูงขึ้น; หากต้องการคุณภาพที่ดีขึ้น ให้ใช้จำนวน epoch มากขึ้นและ LR ต่ำลง ลด batch size หรือความยาวของลำดับหากพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ
### เคล็ดลับการเพิ่มประสิทธิภาพหน่วยความจำ

หากพบข้อผิดพลาด out-of-memory:

**1. ลดขนาด Batch:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. ลดความยาวของลำดับ:**
```python
max_seq_length=256  # Instead of 512
```

**3. ใช้การควอนไทซ์ที่เข้มงวดมากขึ้น:**
```
Full → LoRA → QLoRA
```

**4. เปิดใช้งาน Gradient Checkpointing (สำหรับการไฟน์จูนแบบเต็มรูปแบบเท่านั้น):**
```python
model.gradient_checkpointing_enable()
```

---

## การตรวจสอบและดีบัก

### ตรวจสอบหน่วยความจำ GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (ไม่บังคับ) ติดตามการทดลองด้วย Weights & Biases

เพื่อบันทึกการรันและเมตริกไปยัง [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

ในสคริปต์การฝึก ให้ตั้งค่า `report_to="wandb"` และตั้งค่า `run_name="your-experiment-name"` ตามต้องการในค่าคอนฟิกของ trainer หากคุณไม่ต้องการใช้ Wandb ให้ปล่อย `report_to` ไว้ที่ค่าเริ่มต้น หรือตั้งค่าเป็น `"none"`

### ปัญหาที่พบบ่อย

#### Out of Memory (OOM)

**วิธีแก้ไข:** ลดขนาด batch และ/หรือใช้ QLoRA
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

**วิธีแก้ไข:** เพิ่มขนาด batch หากหน่วยความจำเพียงพอ
```python
BATCH_SIZE = 8
```
## ขั้นตอนถัดไป

หลังจากที่คุณไฟน์จูนสำเร็จแล้ว ลองพิจารณาขั้นตอนถัดไปต่อไปนี้เพื่อใช้ประโยชน์จากโมเดลของคุณให้มากขึ้น:

1. **ประเมินผล** อย่างละเอียดบนข้อมูลทดสอบที่แยกไว้ เพื่อวัดความสามารถในการทำงานทั่วไปและหลีกเลี่ยงการ overfitting
2. **ทดลอง** โดยลองใช้ค่าไฮเปอร์พารามิเตอร์ที่แตกต่างกันเพื่อให้ได้ความแม่นยำ ความเร็ว และการแลกเปลี่ยนด้านหน่วยความจำที่ดีขึ้น
3. **ติดตาม** การทดลองทั้งหมดของคุณ (พร้อมเมตริกที่เกี่ยวข้อง) ด้วย Weights & Biases เพื่อการวิจัยที่สามารถทำซ้ำได้
4. **ลอง** ฝึกด้วยชุดข้อมูลที่กำหนดเองของคุณเพื่อปรับโมเดลให้เหมาะกับกรณีการใช้งานของคุณโดยเฉพาะ
5. **นำไปใช้งาน** โมเดลที่ไฟน์จูนแล้วของคุณเพื่อการอนุมานที่รวดเร็วโดยใช้แบ็กเอนด์ที่มีประสิทธิภาพ เช่น vLLM บนฮาร์ดแวร์ที่รองรับ
6. **สำรวจ** เทคนิคขั้นสูง รวมถึง prompt engineering, mixed precision และความยาวของลำดับที่ยาวขึ้น
7. **ฝึก** LoRA adapter หลายตัวสำหรับงานหรือโดเมนที่แตกต่างกัน และสลับใช้งานตามความจำเป็น

---