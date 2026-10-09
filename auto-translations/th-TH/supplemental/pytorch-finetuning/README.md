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

บทแนะนำนี้มีตัวอย่างทีละขั้นตอนสำหรับการปรับแต่ง (fine-tuning) โมเดลภาษาขนาดใหญ่ (LLM) ด้วย PyTorch และ ROCm โดยครอบคลุมเทคนิคต่าง ๆ ตั้งแต่การปรับแต่งแบบมาตรฐานไปจนถึงกลยุทธ์การปรับแต่งแบบประหยัดหน่วยความจำ (Parameter-Efficient Fine-Tuning หรือ PEFT) เพื่อให้คุณสามารถปรับโมเดลให้เหมาะกับความต้องการของคุณได้อย่างง่ายดาย

**โมเดลที่ใช้**: google/gemma-3-4b-it (สคริปต์ QLoRA: openai/gpt-oss-20b)  *(ดู [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) หากเป็นโมเดลที่ถูกจำกัดสิทธิ์)*  
**ฮาร์ดแวร์**: GPU AMD Radeon™ ที่รองรับ ROCm  
**เฟรมเวิร์ก**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **หมายเหตุ:** 
> - การปรับแต่งแบบเต็มรูปแบบ (full fine-tuning) ต้องการ **RAM ของระบบอย่างน้อย 64 GB** โดยอย่างน้อย **32 GB ของจำนวนนี้ต้องพร้อมใช้งานสำหรับ GPU** (32 GB นี้เป็นส่วนหนึ่งของ 64 GB ไม่ใช่ส่วนเพิ่มเติม)
> - คุณยังสามารถลองใช้สถาปัตยกรรมโมเดลอื่น ๆ รวมถึง **GPT-OSS-20B** ได้โดยการแทนที่โมเดลในสคริปต์การฝึกที่ให้มา
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **หมายเหตุ:** การปรับแต่งแบบ LoRA และ QLoRA ต้องการ **RAM ของระบบอย่างน้อย 32 GB** โดยอย่างน้อย **16 GB ของจำนวนนี้ต้องพร้อมใช้งานสำหรับ GPU** (16 GB นี้เป็นส่วนหนึ่งของ 32 GB ไม่ใช่ส่วนเพิ่มเติม)
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การปรับแต่งแบบ LoRA ต้องการ **RAM ของระบบอย่างน้อย 32 GB** โดยอย่างน้อย **16 GB ของจำนวนนี้ต้องพร้อมใช้งานสำหรับ GPU** (16 GB นี้เป็นส่วนหนึ่งของ 32 GB ไม่ใช่ส่วนเพิ่มเติม)
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **หมายเหตุ:** การปรับแต่งแบบ LoRA และ QLoRA ต้องการการ์ดแสดงผลที่มี **หน่วยความจำ GPU เฉพาะ (dedicated) อย่างน้อย 16 GB** และ **RAM ของระบบ 32 GB**
> - บน Linux การฝึกจะทำงานทั้งหมดภายใน VRAM เฉพาะของการ์ดแสดงผล
> - ระบบจะไม่ย้อนกลับไปใช้หน่วยความจำ GPU ที่ใช้ร่วมกัน (shared) (RAM ของระบบ) เมื่อ VRAM หมด
> - การ์ดที่มี VRAM เฉพาะน้อยกว่า 16 GB จะพบปัญหาหน่วยความจำไม่เพียงพอระหว่างการฝึกบน Linux แม้ว่าระบบจะมี RAM เหลือเฟือก็ตาม
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การปรับแต่งแบบ LoRA ต้องการ **หน่วยความจำ GPU รวมอย่างน้อย 16 GB** และ **RAM ของระบบ 32 GB**
> - บน Windows หน่วยความจำ GPU รวมจะรวม VRAM เฉพาะของการ์ดแสดงผลเข้ากับหน่วยความจำ GPU ที่ใช้ร่วมกัน (ที่ยืมมาจาก RAM ของระบบ)
> - ดังนั้น การ์ดที่มี VRAM เฉพาะน้อยกว่า 16 GB ก็ยังสามารถใช้งานตามคู่มือนี้ได้โดยใช้หน่วยความจำ GPU ที่ใช้ร่วมกันเพื่อชดเชยส่วนต่าง
<!-- @os:end -->
<!-- @device:end -->

## สิ่งที่คุณจะได้เรียนรู้

- วิธีปรับแต่ง LLM โดยใช้ LoRA, QLoRA และการปรับแต่งแบบเต็มรูปแบบด้วย PyTorch และ ROCm
- วิธีบันทึกและปรับใช้งานโมเดลที่ปรับแต่งแล้ว
- วิธีตรวจสอบการฝึกและแก้ไขปัญหาที่พบบ่อย

<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ผ่าน Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @prereq:hf-models-gemma-3-4b-it,hf-datasets-databricks-dolly-15k -->
<!-- @os:linux -->
<!-- @prereq:hf-datasets-english-quotes -->
<!-- @os:end -->

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
**ให้สิทธิ์ผู้ใช้ของคุณในการเข้าถึงอุปกรณ์ GPU** (ต้องออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

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

#### การติดตั้งไลบรารีพื้นฐานที่จำเป็น
<!-- @require:pytorch -->

#### ไลบรารีเพิ่มเติมที่จำเป็น

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** มีการทดสอบและรองรับเฉพาะแพ็กเกจหลักเท่านั้น **bitsandbytes ยังไม่รองรับบน Windows ได้ดีนัก** ดังนั้นการติดตั้งบน Windows จึงไม่รวม bitsandbytes ให้ใช้ LoRA หรือการปรับแต่งแบบเต็มรูปแบบบน Windows แทน (QLoRA ต้องใช้ bitsandbytes และออกแบบมาสำหรับ Linux)
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### เปิดใช้งานการยืนยันตัวตน HF (สำหรับโมเดลที่ถูกจำกัดสิทธิ์หรือโมเดลที่กำหนดเอง / ไม่ได้ติดตั้งไว้ล่วงหน้า)

ในตัวอย่างนี้เราใช้ **google/gemma-3-4b-it** ซึ่งเป็นโมเดลที่ **ถูกจำกัดสิทธิ์ (gated)** คุณต้องยอมรับข้อกำหนดของโมเดลบน Hugging Face ก่อน แล้วจึงยืนยันตัวตนเพื่อให้สคริปต์การฝึกสามารถดาวน์โหลดโมเดลได้

1. **ยอมรับใบอนุญาต:** เปิด [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) เข้าสู่ระบบ (หรือสร้างบัญชี) และยอมรับใบอนุญาต/ข้อกำหนดบนหน้าโมเดล (เช่น “Agree and access repository”)
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

## ทำความเข้าใจเทคนิคต่าง ๆ

### LoRA คืออะไร?

**LoRA (Low-Rank Adaptation)** จะคงโมเดลฐาน (base model) ไว้โดยไม่เปลี่ยนแปลง (frozen) และฝึกเฉพาะเมทริกซ์ "อะแดปเตอร์" ขนาดเล็กที่ถูกเพิ่มเข้าไปในบางเลเยอร์เท่านั้น 

- **แนวคิดหลัก**: แทนที่จะอัปเดตเมทริกซ์น้ำหนักขนาดใหญ่ที่มีพารามิเตอร์หลายล้านตัว เราเรียนรู้การอัปเดตแบบแรงก์ต่ำ (low-rank) (เมทริกซ์ขนาดเล็กสองตัวที่ผลคูณมีพารามิเตอร์น้อยกว่ามาก) วิธีนี้ช่วยลดจำนวนพารามิเตอร์ที่ต้องฝึกและ VRAM ลงได้อย่างมาก ในขณะที่ยังคงรักษาคุณภาพส่วนใหญ่ของการปรับแต่งแบบเต็มรูปแบบไว้ได้

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

**QLoRA** รวม **การควอนไทซ์แบบ 4 บิต (4-bit quantization)** เข้ากับ **LoRA** โมเดลฐานจะถูกโหลดในรูปแบบ 4 บิต (ประหยัดหน่วยความจำได้มาก) และมีเพียงอะแดปเตอร์ LoRA เท่านั้นที่ถูกฝึกด้วยความแม่นยำที่สูงกว่า ดังนั้นคุณจะได้ทั้งประสิทธิภาพด้านพารามิเตอร์ของ LoRA และ VRAM ที่ต่ำลงมาก โดยแลกกับคุณภาพที่ลดลงเล็กน้อยเมื่อเทียบกับ LoRA แบบความแม่นยำเต็ม โปรดทราบว่าการควอนไทซ์แบบ 4 บิตอาจทำให้เกิดความไม่เสถียรทางตัวเลข (loss พุ่งสูงขึ้นหรือค่า NaN) ดังนั้นผู้ใช้จึงมักนิยมใช้ **LoRA** หาก VRAM มีเพียงพอ

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **หมายเหตุ**: สำหรับโมเดลฐานแบบ MXFP4 เช่น `openai/gpt-oss-20b` เราขอแนะนำให้ใช้ **LoRA** (`train_lora.py`) แทน QLoRA เนื่องจากเส้นทางการประมวลผล 4 บิตของ `bitsandbytes` ในสคริปต์ QLoRA มักจะทำการ dequantize น้ำหนัก MXFP4 กลับเป็น BF16 ทำให้การทำงานมีลักษณะเหมือนกับ LoRA มาตรฐาน การใช้ MXFP4 แบบดั้งเดิม (native) ต้องใช้ `bitsandbytes` ที่คอมไพล์จากซอร์สโค้ด พร้อมกับชุด Transformers/Triton/kernels ที่เข้ากันได้ ดูเพิ่มเติมที่ [Transformers MXFP4 docs](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)

---
### 2. เลือกวิธีการของคุณ

| วิธีการ | หน่วยความจำ | ความเร็ว | คุณภาพ | เหมาะสำหรับ |
|--------|--------|-------|---------|----------|
| **QLoRA** (Linux เท่านั้น) | 12-16GB | เร็วที่สุด | 90-95% | การใช้หน่วยความจำต่ำ |
| **LoRA** | 24-32GB | เร็ว | 95-98% | แนวทางที่สมดุล |
| **Full** | 80GB+ | ช้าที่สุด | 100% | คุณภาพสูงสุด |

### 3. เริ่มการฝึกอบรม

**ชุดข้อมูลและสิ่งที่โมเดลเรียนรู้**  
สคริปต์จะแปลงชุดข้อมูลให้เป็นตัวอย่างการสนทนา ตัวอย่างเช่น สคริปต์ QLoRA ใช้ **Abirate/english_quotes**: แต่ละตัวอย่างจะกลายเป็นคู่สนทนาระหว่างผู้ใช้กับผู้ช่วยในลักษณะนี้:

- **ผู้ใช้:** “Give me a quote about: &lt;tag&gt;”
- **ผู้ช่วย:** “&lt;quote&gt; – &lt;author&gt;”

การปรับแต่งโมเดลนี้จะสอนให้โมเดลตอบสนองต่อคำสั่งที่ขอคำคมเกี่ยวกับหัวข้อหนึ่ง ๆ และส่งคืนในรูปแบบ `<quote text> - <author>` สคริปต์ LoRA และการปรับแต่งแบบเต็มรูปแบบใช้ **databricks/databricks-dolly-15k** (คู่คำสั่ง/คำตอบทั่วไป) ดังนั้นงานที่แน่นอนจะแตกต่างกันไปตามสคริปต์ แต่แนวคิดหลักยังคงเหมือนเดิม - ปรับโมเดลให้เข้ากับชุดข้อมูลและรูปแบบที่คุณเลือก

ด้านล่างนี้คือสรุปวิธีการฝึกอบรมที่มีให้ใช้งาน แต่ละวิธีจะเชื่อมโยงไปยังสคริปต์ของตนเองและมีคำอธิบายสั้น ๆ เพื่อช่วยในการเลือกแนวทางที่เหมาะสม

| สคริปต์                           | วิธีการ            | คำอธิบาย                                                                                                         | VRAM โดยทั่วไป | แนะนำสำหรับ                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | ฝึกเมทริกซ์ adapter ขนาดเล็กในขณะที่ล็อกโมเดลฐานไว้ เร็วกว่า 3-5 เท่า; ให้คุณภาพประมาณ 95-98% ของคุณภาพเต็ม                         | 24–32GB      | ผู้ใช้ขั้นสูง; adapter หลายตัว; มี VRAM มากกว่า    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux เท่านั้น)*             | **QLoRA**       | การควอนไทซ์แบบ 4-bit ร่วมกับ adapter LoRA ใช้หน่วยความจำน้อยที่สุด เร็วที่สุด แลกกับคุณภาพที่ลดลงเล็กน้อย ต้องใช้ `bitsandbytes` (Linux เท่านั้น)                            | 12–16GB      | ผู้ใช้ส่วนใหญ่; การทดลองอย่างรวดเร็ว; VRAM จำกัด      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **การปรับแต่งแบบเต็มรูปแบบ** | อัปเดตพารามิเตอร์ของโมเดลทั้งหมด คุณภาพสูงสุด แต่ใช้หน่วยความจำและการประมวลผลมากที่สุด                                    | 40GB+        | คุณภาพสูงสุด; งานวิจัย; มี VRAM มาก           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **หมายเหตุ:** การปรับแต่งแบบเต็มรูปแบบ (`train_full_finetuning.py`) อาจต้องการ RAM ของระบบมากกว่า 64GB และอาจไม่สามารถทำได้บนอุปกรณ์นี้ ลองพิจารณาใช้ LoRA หรือ QLoRA แทน
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การปรับแต่งแบบเต็มรูปแบบ (`train_full_finetuning.py`) อาจต้องการ RAM ของระบบมากกว่า 64GB และอาจไม่สามารถทำได้บนอุปกรณ์นี้ ลองพิจารณาใช้ LoRA แทน
<!-- @os:end -->
<!-- @device:end -->

เพียงเลือก `Training method` ที่คุณต้องการ ดาวน์โหลดสคริปต์ที่เกี่ยวข้อง และรันโดยใช้คำสั่งนี้ พร้อมเปิดใช้งาน virtual environment ของคุณไว้: 

```python
python3 train_<method_name>.py.
```

## การใช้งานโมเดลที่ผ่านการปรับแต่งแล้ว

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

### หลังจากการฝึกด้วย LoRA/QLoRA

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

### การรวม LoRA Adapter เข้ากับโมเดลฐาน

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**หมายเหตุ:**  
- ตรวจสอบให้แน่ใจว่าชื่อไดเรกทอรีของโมเดล (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) ตรงกับโฟลเดอร์ผลลัพธ์จริงจากการฝึกของคุณ  
- หากคุณใช้ LoRA แทน QLoRA เพียงแค่เปลี่ยนเส้นทางให้ตรงกัน  
- โมเดล Gemma บางรุ่นต้องระบุ `trust_remote_code=True` ใน `from_pretrained` ให้เพิ่มเข้าไปหากคุณเห็นคำเตือนที่เกี่ยวข้อง

สำหรับการตั้งค่าที่กำหนดเองเพิ่มเติม (padding tokens, device เป็นต้น) ให้อ้างอิงสคริปต์ที่คุณใช้ในการฝึกอบรม

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

## คู่มือการปรับแต่งเพิ่มเติม

### ใช้ชุดข้อมูลของคุณเอง

สคริปต์ทั้งหมดใช้รูปแบบชุดข้อมูลแบบเดียวกัน แทนที่ส่วนการโหลด:

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

ควรปฏิบัติตามแนวทางต่อไปนี้:
* **การจัดรูปแบบไฟล์:** ไฟล์ JSON ควรได้รับการจัดรูปแบบภายใน Integrated Development Environment (IDE) เพื่อให้มั่นใจว่ามีโครงสร้างและไวยากรณ์ที่ถูกต้อง
* **คีย์ที่จำเป็น:** ไฟล์ JSON ที่กำหนดเองต้องมีคีย์ `instruction` และ `response` คีย์เหล่านี้มีความจำเป็นต่อการทำงานที่ถูกต้องของวิธีการนี้
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
* **คู่คำสั่ง-คำตอบ:** มุ่งเน้นไปที่ชุดข้อมูลที่มีคู่ `instruction-response` โครงสร้างนี้มีความจำเป็นต่อการทำงานตามที่ตั้งใจไว้
* **การปรับเปลี่ยนคีย์แบบกำหนดเอง:** หากชุดข้อมูลของคุณไม่ตรงกับโครงสร้าง `instruction-response` คุณสามารถปรับเปลี่ยนฟังก์ชัน `format_instruction()` เพื่อรองรับคีย์เฉพาะตามที่ต้องการได้

ตัวอย่างการปรับเปลี่ยน: ในกรณีที่ผลลัพธ์ของชุดข้อมูลจำเป็นต้องปรับเปลี่ยน คุณสามารถแก้ไขส่วนคำตอบภายในฟังก์ชัน format_instruction() ให้เหมาะกับความต้องการของคุณได้
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

### ปรับพารามิเตอร์การฝึกอบรม

แก้ไขสคริปต์การฝึกอบรมและเปลี่ยนตัวแปรให้ตรงกับเป้าหมายของคุณ: **อัตราการเรียนรู้** (`LR`), **จำนวนรอบ** (`EPOCHS`), **ขนาดแบตช์** (`BATCH_SIZE`), **การสะสมเกรเดียนต์** (`GRAD_ACCUM_STEPS`) และสำหรับ LoRA/QLoRA คือ **rank** (`LORA_R`) หากต้องการให้การรันเร็วขึ้น ให้ใช้จำนวนรอบที่น้อยลงและอัตราการเรียนรู้ (LR) ที่สูงขึ้น หากต้องการคุณภาพที่ดีขึ้น ให้ใช้จำนวนรอบที่มากขึ้นและ LR ที่ต่ำลง ลดขนาดแบตช์หรือความยาวลำดับหากคุณพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ
### เคล็ดลับการเพิ่มประสิทธิภาพหน่วยความจำ

หากคุณพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ:

**1. ลดขนาดแบตช์ (Batch Size):**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. ลดความยาวของลำดับ (Sequence Length):**
```python
max_seq_length=256  # Instead of 512
```

**3. ใช้การควอนไทซ์ที่เข้มข้นมากขึ้น:**
```
Full → LoRA → QLoRA
```

**4. เปิดใช้งาน Gradient Checkpointing (สำหรับการทำ full fine-tuning เท่านั้น):**
```python
model.gradient_checkpointing_enable()
```

---

## การตรวจสอบและการแก้ไขข้อบกพร่อง

### ตรวจสอบหน่วยความจำของ GPU

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

ในสคริปต์การฝึก ให้ตั้งค่า `report_to="wandb"` และตั้งค่า `run_name="your-experiment-name"` ได้ตามต้องการในคอนฟิกของ trainer หากคุณไม่ต้องการใช้ Wandb ให้ปล่อย `report_to` ไว้ที่ค่าเริ่มต้น หรือกำหนดเป็น `"none"`

### ปัญหาที่พบบ่อย

#### หน่วยความจำไม่เพียงพอ (OOM)

**วิธีแก้ไข:** ลดขนาดแบตช์และ/หรือใช้ QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### ค่า Loss ไม่ลดลง

**วิธีแก้ไข:** ปรับอัตราการเรียนรู้ (Learning Rate)
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### การฝึกช้า

**วิธีแก้ไข:** เพิ่มขนาดแบตช์หากหน่วยความจำเพียงพอ
```python
BATCH_SIZE = 8
```
## ขั้นตอนถัดไป

หลังจากที่คุณได้ทำการ fine-tuning สำเร็จแล้ว ให้พิจารณาขั้นตอนถัดไปต่อไปนี้เพื่อให้ได้ประโยชน์สูงสุดจากโมเดลของคุณ:

1. **ประเมินผล** อย่างละเอียดบนชุดข้อมูลทดสอบที่แยกไว้ต่างหาก เพื่อวัดความสามารถในการทำงานทั่วไปและหลีกเลี่ยงการ overfitting
2. **ทดลอง** ด้วยการลองค่าไฮเปอร์พารามิเตอร์ที่แตกต่างกัน เพื่อให้ได้ความสมดุลที่ดีขึ้นระหว่างความแม่นยำ ความเร็ว และหน่วยความจำ
3. **ติดตาม** การทดลองทั้งหมดของคุณ (พร้อมเมตริกที่เกี่ยวข้อง) ด้วย Weights & Biases เพื่อให้สามารถทำวิจัยซ้ำได้
4. **ลอง** ฝึกด้วยชุดข้อมูลที่กำหนดเองของคุณ เพื่อปรับโมเดลให้เหมาะกับกรณีการใช้งานของคุณโดยเฉพาะ
5. **ปรับใช้ (Deploy)** โมเดลที่ fine-tune แล้วของคุณเพื่อการอนุมาน (inference) ที่รวดเร็ว โดยใช้แบ็กเอนด์ที่มีประสิทธิภาพ เช่น vLLM บนฮาร์ดแวร์ที่รองรับ
6. **สำรวจ** เทคนิคขั้นสูง รวมถึงวิศวกรรมพรอมป์ (prompt engineering), ความแม่นยำแบบผสม (mixed precision) และความยาวลำดับที่มากขึ้น
7. **ฝึก** LoRA adapters หลายตัวสำหรับงานหรือโดเมนที่แตกต่างกัน และสลับใช้งานตามความต้องการ

---