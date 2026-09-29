<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

## ภาพรวม

การปรับแต่งอย่างมีประสิทธิภาพ (Efficient fine-tuning) มีความสำคัญอย่างยิ่งต่อการปรับให้โมเดลภาษาขนาดใหญ่ (LLMs) เหมาะสมกับงานปลายทาง LLaMA Factory เป็นแพลตฟอร์มโอเพนซอร์สที่ใช้งานง่าย ซึ่งช่วยให้การฝึกและปรับแต่งโมเดลภาษาขนาดใหญ่และโมเดลมัลติโมดัลเป็นไปอย่างราบรื่น ช่วยให้ผู้ใช้สามารถปรับแต่งโมเดลที่ผ่านการฝึกล่วงหน้าหลายร้อยโมเดลได้ในเครื่องของตนเองโดยเขียนโค้ดน้อยที่สุด

คู่มือนี้จะสอนวิธีการปรับแต่ง LLMs โดยใช้ LLaMA Factory บนฮาร์ดแวร์ AMD ในเครื่องของคุณ

<!-- @device:stx,krk -->
> **หมายเหตุ:** เทคนิคการปรับแต่งในคู่มือนี้ต้องการอย่างน้อย **RAM ระบบ 32 GB** โดยต้องมีอย่างน้อย **16 GB ที่ใช้งานได้กับ GPU** (16 GB นี้เป็นส่วนหนึ่งของ 32 GB ไม่ใช่เพิ่มเติมจาก 32 GB)
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **หมายเหตุ:** เทคนิคการปรับแต่งในคู่มือนี้ต้องการอย่างน้อย **หน่วยความจำ GPU รวม 16 GB** และ **RAM ระบบ 32 GB**
> - บน Windows หน่วยความจำ GPU รวมประกอบด้วย VRAM เฉพาะของการ์ดกราฟิกร่วมกับหน่วยความจำ GPU ที่ใช้ร่วมกัน (ยืมมาจาก RAM ระบบ)
> - ดังนั้น การ์ดที่มี VRAM เฉพาะน้อยกว่า 16 GB ก็ยังสามารถรันคู่มือนี้ได้โดยใช้หน่วยความจำ GPU ที่ใช้ร่วมกันเพื่อชดเชยส่วนต่าง
<!-- @os:end -->

<!-- @os:linux -->
> **หมายเหตุ:** เทคนิคการปรับแต่งในคู่มือนี้ต้องการการ์ดกราฟิกที่มีอย่างน้อย **หน่วยความจำ GPU เฉพาะ 16 GB** และ **RAM ระบบ 32 GB**
> - บน Linux การฝึกจะทำงานทั้งหมดภายใน VRAM เฉพาะของการ์ดกราฟิก
> - ระบบจะไม่ตกกลับไปใช้หน่วยความจำ GPU ที่ใช้ร่วมกัน (RAM ระบบ) เมื่อ VRAM หมด
> - การ์ดที่มี VRAM เฉพาะน้อยกว่า 16 GB จะหน่วยความจำไม่พอในระหว่างการฝึกบน Linux แม้ว่าระบบจะมี RAM เหลือเฟือก็ตาม
<!-- @os:end -->
<!-- @device:end -->

## สิ่งที่คุณจะได้เรียนรู้

- วิธีตั้งค่า LLaMA Factory ร่วมกับซอฟต์แวร์ AMD ROCm™
- วิธีกำหนดค่าพารามิเตอร์การปรับแต่ง LLM (โดยใช้ Qwen/Qwen3-4B-Instruct-2507 เป็นตัวอย่าง)
- วิธีรันการปรับแต่งด้วย LLaMA Factory
- วิธีรัน inference ด้วยโมเดลที่ปรับแต่งแล้ว
- วิธีส่งออกโมเดลที่ปรับแต่งแล้ว

## ระยะเวลาโดยประมาณ

- ระยะเวลา: การรันคู่มือนี้จะใช้เวลาประมาณ 60 นาที (ขึ้นอยู่กับขนาดโมเดล/ชุดข้อมูลของคุณและความเร็วเครือข่าย)
- ดู [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) เพื่อข้อมูลเพิ่มเติม

<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @os:linux -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```bash
python3 --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```powershell
python --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

#### สร้างสภาพแวดล้อมเสมือน (Virtual Environment)

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env --system-site-packages
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
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
python3 -m venv llamafactory-env
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env --system-site-packages
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->
<!-- @os:end -->

### การติดตั้ง Dependencies พื้นฐาน

<!-- @require:pytorch,driver -->

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### การติดตั้ง Dependencies เพิ่มเติม

> **หมายเหตุ**: ตรวจสอบให้แน่ใจว่าเวอร์ชัน Python เป็น 3.11, 3.12 หรือ 3.13

```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### ติดตั้ง LLaMA Factory

LLaMA Factory ขึ้นอยู่กับ PyTorch คุณควรจะติดตั้งมันไว้แล้วตามข้อกำหนดข้างต้น

ดาวน์โหลดซอร์สโค้ดจาก [LLaMA Factory official GitHub repository](https://github.com/hiyouga/LlamaFactory) และติดตั้ง dependencies ของมัน

<!-- @device:halo_box -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install setuptools --break-system-packages
pip install -e . --break-system-packages
pip install -r requirements/metrics.txt --break-system-packages
```
<!-- @test:end --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt 
```
<!-- @test:end --> 
<!-- @device:end -->

ตรวจสอบว่า `llamafactory-cli` สามารถรันได้หรือไม่

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
echo "llamafactory-cli is available"
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```powershell
cd LlamaFactory
if (Get-Command llamafactory-cli -ErrorAction SilentlyContinue) {
    llamafactory-cli version
    Write-Host "llamafactory-cli is available"
} else {
    Write-Host "llamafactory-cli is not available"
}
```
<!-- @test:end --> 
<!-- @os:end -->

ตัวอย่างผลลัพธ์:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

เมื่อติดตั้ง LLaMA Factory สำเร็จแล้ว มาเริ่มรันการปรับแต่งกัน

## การใช้ LLaMA Factory CLI สำหรับการปรับแต่ง

ส่วนนี้จะครอบคลุมวิธีการเตรียมชุดข้อมูลสำหรับการปรับแต่ง การกำหนดค่าพารามิเตอร์ LoRA/QLoRA และการรันการปรับแต่งด้วย LoRA

### การเตรียมชุดข้อมูล

LLaMA Factory รองรับชุดข้อมูลสำหรับการปรับแต่งในรูปแบบ Alpaca และรูปแบบ ShareGPT ชุดข้อมูลที่มีให้ใช้งานทั้งหมดถูกกำหนดไว้ใน [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json) หากคุณใช้ชุดข้อมูลที่กำหนดเอง โปรดตรวจสอบให้แน่ใจว่าได้เพิ่มคำอธิบายชุดข้อมูลใน `dataset_info.json` และระบุชื่อชุดข้อมูลก่อนการฝึก รายละเอียดสามารถดูได้ในเอกสารของพวกเขา [ที่นี่](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html)

ในคู่มือนี้ เราจะใช้ชุดข้อมูล identity และ alpaca_en_demo เป็นตัวอย่าง และกำหนดค่าข้อมูลชุดข้อมูลในขั้นตอนถัดไป
### การกำหนดค่าพารามิเตอร์สำหรับการไฟน์จูน

LLaMA Factory รองรับรูปแบบการไฟน์จูนหลายแบบ

| รูปแบบการไฟน์จูน | ตัวอย่างของ LLaMA Factory |
|-----------|------|
| Full-Parameter    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| การไฟน์จูนแบบ LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| การไฟน์จูนแบบ QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end -->

ไฟล์ตัวอย่างการกำหนดค่าเหล่านี้ได้ระบุพารามิเตอร์ของโมเดล พารามิเตอร์ของวิธีการไฟน์จูน พารามิเตอร์ของชุดข้อมูล พารามิเตอร์การประเมินผล และอื่น ๆ ไว้แล้ว คุณสามารถกำหนดค่าเหล่านี้ได้ตามความต้องการของคุณเอง ในเพลย์บุ๊กนี้ เราจะใช้ [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml)

**คำอธิบายพารามิเตอร์สำคัญ:**
- `model_name_or_path` - ชื่อโมเดลจาก Hugging Face หรือพาธของไฟล์โมเดลในเครื่อง
- `stage` - ขั้นตอนการฝึก ตัวเลือก: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO
- `do_train` - true สำหรับการฝึก, false สำหรับการประเมินผล
- `finetuning_type` - วิธีการไฟน์จูน ตัวเลือก: freeze, lora, full
- `lora_rank` - มิติของเมทริกซ์ลำดับต่ำ (low-rank matrix) ที่ใช้ใน LoRA ค่าทั่วไป: 4, 6, 8, 16 (ค่าน้อย = พารามิเตอร์น้อยลง = ไฟน์จูนเร็วขึ้น; ค่ามาก = ปรับตัวเข้ากับงานได้ดีขึ้นแต่ใช้ทรัพยากรมากขึ้น)
- `lora_target` - โมดูลเป้าหมายสำหรับวิธี LoRA ค่าเริ่มต้น: all
- `dataset` - ชุดข้อมูลที่จะใช้ ใช้ “,” เพื่อคั่นชุดข้อมูลหลายชุด
- `output_dir` - พาธผลลัพธ์ของการไฟน์จูน
- `logging_steps` - ช่วงเวลาการบันทึกล็อก (เป็นสเต็ป)
- `save_steps` - ช่วงเวลาการบันทึกจุดตรวจสอบ (checkpoint) ของโมเดล
- `overwrite_output_dir` - อนุญาตให้เขียนทับไดเรกทอรีผลลัพธ์หรือไม่
- `per_device_train_batch_size` - ขนาดแบตช์ในการฝึกต่ออุปกรณ์
- `gradient_accumulation_steps` - จำนวนสเต็ปการสะสมเกรเดียนต์ (gradient accumulation)
- `learning_rate` - อัตราการเรียนรู้
- `num_train_epochs` - จำนวนรอบการฝึก (epochs)
- `lr_scheduler_type` - ตารางอัตราการเรียนรู้ (learning rate schedule) ตัวเลือก: linear, cosine, polynomial, constant เป็นต้น
- `warmup_ratio` - อัตราส่วนการวอร์มอัพของอัตราการเรียนรู้

<!-- @os:linux -->
เราจะปรับเปลี่ยนค่าเริ่มต้นของ `lora_rank` เพื่อรันการไฟน์จูนบน AMD Ryzen™ & AMD Radeon™ GPU
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
เราจะอัปเดตการกำหนดค่าการไฟน์จูนแบบ LoRA เริ่มต้นเพื่อความเข้ากันได้ที่ดีขึ้นกับ AMD Ryzen™ และ AMD Radeon™ GPU:
- ตั้งค่า `lora_rank` จาก `8` เป็น `6` เพื่อลดการใช้หน่วยความจำระหว่างการไฟน์จูน
- ใช้ `fp16` แทน `bf16` เพื่อความเข้ากันได้ที่กว้างขึ้นกับ AMD GPU และลดการใช้หน่วยความจำ
- ตั้งค่า `dataloader_num_workers` เป็น `0` บน Windows เพื่อหลีกเลี่ยงข้อผิดพลาด `"Can't pickle local object<>"` ที่เกิดจากการโหลดข้อมูลแบบหลายโพรเซส (multiprocessing)

```powershell
$filePath = "examples/train_lora/qwen3_lora_sft.yaml"

# Create a backup before modifying the YAML file
Copy-Item -Path $filePath -Destination "$filePath.bak" -Force

# Read the file and update the training settings
$content = Get-Content -Path $filePath -Raw

$newContent = $content `
  -replace 'lora_rank: 8', 'lora_rank: 6' `
  -replace 'bf16: true', 'fp16: true' `
  -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0'

Set-Content -Path $filePath -Value $newContent
```
<!-- @os:end -->

### รันการไฟน์จูนด้วย LLaMA Factory 

**llamafactory-cli** เป็นเครื่องมือบรรทัดคำสั่ง (CLI) อย่างเป็นทางการสำหรับ LLaMA Factory ที่พัฒนาขึ้นเพื่อลดความซับซ้อนของเวิร์กโฟลว์ LLM แบบครบวงจร (การเตรียมข้อมูล → การไฟน์จูน → การประเมินผล → การนำไปใช้งาน) โดยไม่ต้องเขียนโค้ดที่ซับซ้อน

สำหรับการฝึก/ไฟน์จูน **llamafactory-cli train** คือคำสั่งย่อยหลัก (core subcommand) ของ LLaMA Factory CLI โดยจะสรุปรวมเวิร์กโฟลว์การไฟน์จูน (การประมวลผลข้อมูลล่วงหน้า การปรับไฮเปอร์พารามิเตอร์ การปรับให้เหมาะกับฮาร์ดแวร์) ไว้ในคำสั่ง CLI เดียว โดยรองรับรูปแบบการไฟน์จูนหลายแบบ (LoRA/QLoRA/Full Fine-Tuning) และได้รับการปรับให้เหมาะสมสำหรับ GPU ที่มีทรัพยากรจำกัด (เช่น QLoRA บน VRAM 16GB)

คุณสามารถรันการไฟน์จูนด้วย LLaMA Factory โดยใช้คำสั่งต่อไปนี้ ซึ่งอิงตามไฟล์การกำหนดค่าที่ปรับปรุงแล้วของการไฟน์จูนแบบ Qwen3 LoRA

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

sed -i 's/max_samples: .*/max_samples: 16/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
if grep -q '^max_steps:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^max_steps:.*/max_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf '\nmax_steps: 5\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi
if grep -q '^save_total_limit:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^save_total_limit:.*/save_total_limit: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf 'save_total_limit: 1\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"

Copy-Item -Path "examples/train_lora/qwen3_lora_sft.yaml" -Destination "examples/train_lora/qwen3_lora_sft_ci.yaml"

$filePath = "examples/train_lora/qwen3_lora_sft_ci.yaml"
(Get-Content -Path $filePath) -replace 'lora_rank: 8', 'lora_rank: 6' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'bf16:\s*true', 'fp16: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'dataloader_num_workers:\s*4', 'dataloader_num_workers: 0' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'output_dir: .*', 'output_dir: saves/qwen3_lora_sft_ci' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'overwrite_output_dir: false', 'overwrite_output_dir: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'per_device_train_batch_size: .*', 'per_device_train_batch_size: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'gradient_accumulation_steps: .*', 'gradient_accumulation_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'num_train_epochs: .*', 'num_train_epochs: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'logging_steps: .*', 'logging_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'save_steps: .*', 'save_steps: 5' | Set-Content -Path $filePath

(Get-Content -Path $filePath) -replace 'max_samples: .*', 'max_samples: 16' | Set-Content -Path $filePath
if (Select-String -Path $filePath -Pattern '^max_steps:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^max_steps:.*', 'max_steps: 5' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value ""
    Add-Content -Path $filePath -Value "max_steps: 5"
}
if (Select-String -Path $filePath -Pattern '^save_total_limit:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^save_total_limit:.*', 'save_total_limit: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "save_total_limit: 1"
}

# Single-process dataset preprocessing to avoid Windows multiprocessing errors.
if (Select-String -Path $filePath -Pattern '^preprocessing_num_workers:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^preprocessing_num_workers:.*', 'preprocessing_num_workers: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "preprocessing_num_workers: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

หลังจากรันการไฟน์จูน LLM แล้ว ผลลัพธ์ทั้งหมดที่สร้างขึ้นจะถูกจัดเก็บไว้ใน "output_dir" ซึ่งประกอบด้วยไฟล์จุดตรวจสอบของโมเดล ไฟล์การกำหนดค่า และเมตริกการฝึก

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 

### ทดสอบโมเดลที่ผ่านการไฟน์จูน 

**llamafactory-cli chat** ได้รับการออกแบบมาสำหรับการสนทนา/การอนุมาน (inference) แบบโต้ตอบกับ LLM (ทั้งโมเดลพื้นฐานและโมเดลที่ผ่านการไฟน์จูนด้วย LoRA) LLaMA Factory มีการกำหนดค่าตัวอย่างสำหรับรันการอนุมานของโมเดลที่ผ่านการไฟน์จูนใน [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference) คุณยังสามารถแก้ไขการกำหนดค่าตัวอย่างนี้เพื่อเปลี่ยนแปลงการตั้งค่าต่าง ๆ เช่น แบ็กเอนด์การอนุมาน

ใช้คำสั่งต่อไปนี้เพื่อทดสอบโมเดล Qwen3 ที่ผ่านการไฟน์จูน:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
ตัวอย่างการสนทนาโดยใช้โมเดลที่ผ่านการไฟน์จูนแสดงไว้ด้านล่างนี้:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### ส่งออกโมเดลที่ผ่านการไฟน์จูน

สำหรับกรณีการใช้งานจริง (production) จำเป็นต้องรวมโมเดลที่ผ่านการฝึกล่วงหน้ากับตัวปรับ LoRA (LoRA adapter) เข้าด้วยกันและส่งออกเป็นโมเดลเดียว โมเดลที่รวมกันนี้สามารถใช้เป็นไฟล์โมเดล Hugging Face แบบปกติได้ LLaMA Factory มีการกำหนดค่าตัวอย่างไว้ใน [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora)

ใช้คำสั่งต่อไปนี้เพื่อส่งออกโมเดล Qwen3 ที่ผ่านการไฟน์จูน:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
ผลลัพธ์ของการส่งออกโมเดลที่ผ่านการไฟน์จูนแสดงไว้ด้านล่างนี้

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Fine-Tuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"
pip install pyyaml

$script = @'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
'@

$tempPy = Join-Path $env:TEMP "write_llamafactory_export_config.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
    throw "FAIL: Could not create qwen3_lora_sft_ci.yaml"
}
Remove-Item $tempPy -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "examples/merge_lora/qwen3_lora_sft_ci.yaml")) {throw "FAIL: examples/merge_lora/qwen3_lora_sft_ci.yaml was not created"}

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
if ($LASTEXITCODE -ne 0) {throw "FAIL: llamafactory-cli export failed"}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end -->
## การใช้ LLaMA Factory GUI

`LLaMA-Factory` ยังรองรับการปรับแต่ง LLM แบบ zero-code ผ่านเว็บ UI ในเบราว์เซอร์อีกด้วย

ใช้คำสั่งต่อไปนี้เพื่อเปิดใช้งาน:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` มอบอินเทอร์เฟซที่ช่วยให้การจัดการเวิร์กโฟลว์ machine learning เป็นไปอย่างราบรื่น ครอบคลุมทั้งการฝึกฝน การประเมินผล การทำนาย การแชท และการส่งออกโมเดล ต่อไปนี้คือคำอธิบายสั้น ๆ ของแต่ละแท็บ:

* **Train**: แท็บนี้ช่วยให้คุณเลือกโมเดลและชุดข้อมูล กำหนดค่าพารามิเตอร์การฝึกฝน และเริ่มต้นกระบวนการฝึกฝนได้ การทำความเข้าใจพารามิเตอร์ที่จำเป็นและพารามิเตอร์เสริมเป็นสิ่งสำคัญเพื่อให้การตั้งค่าการฝึกฝนมีประสิทธิภาพสูงสุด
* **Evaluate & Predict**: หลังจากการฝึกฝนเสร็จสิ้น คุณสามารถประเมินประสิทธิภาพของโมเดลและทำการทำนายได้โดยใช้แท็บนี้ ซึ่งจะให้ข้อมูลเชิงลึกเกี่ยวกับความแม่นยำและประสิทธิผลของโมเดลกับข้อมูลใหม่
* **Chat**: เมื่อการฝึกฝนเสร็จสมบูรณ์แล้ว ให้โหลดโมเดลในแท็บ Chat เพื่อโต้ตอบกับโมเดลและดูผลลัพธ์ของงานที่คุณทำ ฟีเจอร์นี้ช่วยให้สามารถสื่อสารกับโมเดลที่ผ่านการฝึกฝนได้แบบเรียลไทม์
* **Export**: แท็บนี้ช่วยอำนวยความสะดวกในการส่งออกโมเดลที่ผ่านการฝึกฝนเพื่อนำไปใช้งานจริงหรือใช้งานต่อไป คุณสามารถบันทึกโมเดลของคุณในรูปแบบต่าง ๆ ที่เหมาะสมกับการใช้งานที่แตกต่างกันได้

สำหรับคำแนะนำโดยละเอียด เราขอแนะนำให้คุณอ้างอิงเอกสารทางการที่ [LlamaFactory GitHub repository](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) และ [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest) นอกจากนี้ [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) ยังให้ข้อมูลเชิงลึกที่มีคุณค่าเกี่ยวกับอินเทอร์เฟซและฟังก์ชันการทำงานต่าง ๆ ของมัน

## ขั้นตอนถัดไป
- ลองใช้โมเดลที่แตกต่างกัน เช่น `gpt-oss` และโมเดลล้ำสมัยอื่น ๆ
- ทดลองใช้แบ็กเอนด์ที่แตกต่างกันกับโมเดลที่ผ่านการปรับแต่งแล้ว
 
สำหรับเอกสารเพิ่มเติม กรุณาเยี่ยมชม: https://llamafactory.readthedocs.io/en/latest/