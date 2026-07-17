## ภาพรวม

การ Fine-tuning ที่มีประสิทธิภาพมีความสำคัญอย่างยิ่งสำหรับการปรับใช้ Large Language Models (LLMs) กับงานปลายทาง LLaMA-Factory คือแพลตฟอร์มโอเพนซอร์สที่ใช้งานง่าย ซึ่งช่วยให้กระบวนการฝึกและ Fine-tuning ของ Large Language Models และ Multimodal Models เป็นไปอย่างราบรื่น โดยอนุญาตให้ผู้ใช้ปรับแต่งโมเดลที่ผ่านการฝึกมาแล้วหลายร้อยโมเดลในเครื่องของตนเองด้วยโค้ดที่น้อยที่สุด

Playbook นี้จะสอนวิธี Fine-tune LLMs โดยใช้ LLaMA-Factory บนฮาร์ดแวร์ AMD ของคุณในเครื่อง

<!-- @device:stx,krk -->
> **หมายเหตุ:** เทคนิค Fine-tuning ใน Playbook นี้ต้องการ RAM ของระบบอย่างน้อย **32 GB** โดยมีอย่างน้อย **16 GB ที่พร้อมใช้งานสำหรับ GPU** (16 GB นั้นเป็นส่วนหนึ่งของ 32 GB ไม่ใช่เพิ่มเติมจากนั้น)
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **หมายเหตุ:** เทคนิค Fine-tuning ใน Playbook นี้ต้องการหน่วยความจำ GPU รวมอย่างน้อย **16 GB** และ RAM ของระบบ **32 GB**
> - บน Windows หน่วยความจำ GPU รวมจะรวม VRAM เฉพาะของการ์ดจอเข้ากับหน่วยความจำ GPU ที่แชร์ (ยืมมาจาก RAM ของระบบ)
> - ดังนั้น การ์ดที่มี VRAM เฉพาะน้อยกว่า 16 GB ยังสามารถรัน Playbook นี้ได้โดยใช้หน่วยความจำ GPU ที่แชร์เพื่อชดเชยส่วนที่ขาด
<!-- @os:end -->

<!-- @os:linux -->
> **หมายเหตุ:** เทคนิค Fine-tuning ใน Playbook นี้ต้องการการ์ดจอที่มีหน่วยความจำ GPU เฉพาะอย่างน้อย **16 GB** และ RAM ของระบบ **32 GB**
> - บน Linux การฝึกจะทำงานทั้งหมดใน VRAM เฉพาะของการ์ดจอ
> - ไม่มีการ Fallback ไปยังหน่วยความจำ GPU ที่แชร์ (RAM ของระบบ) เมื่อ VRAM หมด
> - การ์ดที่มี VRAM เฉพาะน้อยกว่า 16 GB จะหน่วยความจำหมดระหว่างการฝึกบน Linux แม้ว่าระบบจะมี RAM เหลือเพียงพอก็ตาม
<!-- @os:end -->
<!-- @device:end -->

## สิ่งที่คุณจะได้เรียนรู้

- วิธีตั้งค่า LLaMA-Factory ด้วยซอฟต์แวร์ AMD ROCm™
- วิธีกำหนดค่าพารามิเตอร์ Fine-tuning ของ LLM (โดยใช้ Qwen/Qwen3-4B-Instruct-2507 เป็นตัวอย่าง)
- วิธีรัน Fine-tuning ด้วย LLaMA-Factory
- วิธีรัน Inference ด้วยโมเดลที่ผ่านการ Fine-tune แล้ว
- วิธี Export โมเดลที่ผ่านการ Fine-tune แล้ว

## เวลาที่ประมาณการ

- ระยะเวลา: ใช้เวลาประมาณ 60 นาทีในการรัน Playbook นี้ (ขึ้นอยู่กับขนาดโมเดล/ชุดข้อมูลและความเร็วเครือข่ายของคุณ)
- ดูข้อมูลเพิ่มเติมได้ที่ [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory)

## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->

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

#### สร้าง Virtual Environment

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
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
**ให้สิทธิ์ผู้ใช้ของคุณในการเข้าถึงอุปกรณ์ GPU** (ออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
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

LLaMA-Factory ขึ้นอยู่กับ PyTorch คุณควรติดตั้งไว้แล้วตามข้อกำหนดข้างต้น

ดาวน์โหลดซอร์สโค้ดจาก [LLaMA Factory official GitHub repository](https://github.com/hiyouga/LlamaFactory) และติดตั้ง Dependencies ของมัน

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

เมื่อติดตั้ง LLaMA-Factory สำเร็จแล้ว มาเริ่มรัน Fine-tuning กัน

## การใช้ LLaMA Factory CLI สำหรับ Fine Tuning

ส่วนนี้จะครอบคลุมวิธีเตรียมชุดข้อมูล Fine-tuning กำหนดค่าพารามิเตอร์ LoRA/QLoRA และรัน LoRA Fine-tuning

### การเตรียมชุดข้อมูล

LLaMA-Factory รองรับชุดข้อมูล Fine-tuning ในรูปแบบ Alpaca และรูปแบบ ShareGPT ชุดข้อมูลที่มีอยู่ทั้งหมดได้ถูกกำหนดไว้ใน [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json) หากคุณใช้ชุดข้อมูลที่กำหนดเอง โปรดตรวจสอบให้แน่ใจว่าได้เพิ่มคำอธิบายชุดข้อมูลใน `dataset_info.json` และระบุชื่อชุดข้อมูลก่อนการฝึก รายละเอียดสามารถดูได้ในเอกสารของพวกเขา [ที่นี่](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html)

ใน Playbook นี้ เราจะใช้ชุดข้อมูล identity และ alpaca_en_demo เป็นตัวอย่าง และกำหนดค่าข้อมูลชุดข้อมูลในขั้นตอนถัดไป


### การกำหนดค่าพารามิเตอร์ Fine-tuning

LLaMA-Factory รองรับรูปแบบ Fine-tuning หลายแบบ

| รูปแบบ Fine-Tuning | ตัวอย่าง LLaMA-Factory |
|-----------|------|
| Full-Parameter    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| LoRA fine-tuning  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| QLoRA fine-tuning | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

ไฟล์การกำหนดค่าตัวอย่างเหล่านี้ได้ระบุพารามิเตอร์โมเดล พารามิเตอร์วิธี Fine-tuning พารามิเตอร์ชุดข้อมูล พารามิเตอร์การประเมิน และอื่นๆ คุณสามารถกำหนดค่าตามความต้องการของคุณเอง ใน Playbook นี้ เราจะใช้ [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml)

**คำอธิบายพารามิเตอร์หลัก:**
- `model_name_or_path` - ชื่อโมเดลบน Hugging Face หรือเส้นทางไฟล์โมเดลในเครื่อง
- `stage` - ขั้นตอนการฝึก ตัวเลือก: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO
- `do_train` - true สำหรับการฝึก, false สำหรับการประเมิน
- `finetuning_type` - วิธี Fine-tuning ตัวเลือก: freeze, lora, full
- `lora_rank` - มิติของ Low-rank Matrix ที่ใช้ใน LoRA ค่าทั่วไป: 4, 6, 8, 16 (ค่าน้อยกว่า = พารามิเตอร์น้อยกว่า = Fine-tuning เร็วกว่า; ค่ามากกว่า = การปรับตัวกับงานดีกว่าแต่ใช้ทรัพยากรมากกว่า)
- `lora_target` - โมดูลเป้าหมายสำหรับวิธี LoRA ค่าเริ่มต้น: all
- `dataset` - ชุดข้อมูลที่จะใช้ ใช้ "," เพื่อแยกชุดข้อมูลหลายชุด
- `output_dir` - เส้นทาง Output ของ Fine-tuning
- `logging_steps` - ช่วงการบันทึก Log เป็นจำนวน Steps
- `save_steps` - ช่วงการบันทึก Checkpoint ของโมเดล
- `overwrite_output_dir` - อนุญาตให้เขียนทับไดเรกทอรี Output หรือไม่
- `per_device_train_batch_size` - ขนาด Batch การฝึกต่ออุปกรณ์
- `gradient_accumulation_steps` - จำนวน Steps ของการสะสม Gradient
- `learning_rate` - อัตราการเรียนรู้
- `num_train_epochs` - จำนวน Epoch การฝึก
- `lr_scheduler_type` - ตารางอัตราการเรียนรู้ ตัวเลือก: linear, cosine, polynomial, constant เป็นต้น
- `warmup_ratio` - อัตราส่วน Warmup ของอัตราการเรียนรู้

<!-- @os:linux -->
เราจะแก้ไขค่าเริ่มต้นของ `lora_rank` เพื่อรัน Fine-tuning บน AMD Ryzen™ & AMD Radeon™ GPUs
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
เราจะอัปเดตการกำหนดค่า LoRA Fine-tuning เริ่มต้นเพื่อให้เข้ากันได้ดีขึ้นกับ AMD Ryzen™ และ AMD Radeon™ GPUs:
- ตั้งค่า `lora_rank` จาก `8` เป็น `6` เพื่อลดการใช้หน่วยความจำระหว่าง Fine-tuning
- ใช้ `fp16` แทน `bf16` เพื่อความเข้ากันได้กับ AMD GPU ที่กว้างขึ้นและการใช้หน่วยความจำที่ต่ำลง
- ตั้งค่า `dataloader_num_workers` เป็น `0` บน Windows เพื่อหลีกเลี่ยงข้อผิดพลาด `"Can't pickle local object<>"` ที่เกิดจากการโหลดข้อมูลแบบ Multiprocessing

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

### รัน LLaMA Factory Fine-Tuning

**llamafactory-cli** คือเครื่องมือ Command-line Interface (CLI) อย่างเป็นทางการสำหรับ LLaMA-Factory ที่พัฒนาขึ้นเพื่อลดความซับซ้อนของ Workflow LLM แบบ End-to-end (การเตรียมข้อมูล → Fine-tuning → การประเมิน → การ Deploy) โดยไม่ต้องเขียนโค้ดที่ซับซ้อน

สำหรับการฝึก/Fine-tuning **llamafactory-cli train** คือ Subcommand หลักของ LLaMA Factory CLI ซึ่งรวม Workflow Fine-tuning (การประมวลผลข้อมูลล่วงหน้า การปรับ Hyperparameter การปรับแต่งฮาร์ดแวร์) ไว้ในคำสั่ง CLI เดียว รองรับ Paradigm Fine-tuning หลายแบบ (LoRA/QLoRA/Full Fine-Tuning) และได้รับการปรับแต่งสำหรับ GPU ที่มีทรัพยากรจำกัด (เช่น QLoRA บน VRAM 16GB)

คุณสามารถรัน LLaMA-Factory Fine-tuning โดยใช้คำสั่งต่อไปนี้ ซึ่งอ้างอิงจากไฟล์การกำหนดค่าที่แก้ไขแล้วของ Qwen3 LoRA Fine-tuning

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

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

หลังจากรัน LLM Fine-tuning แล้ว ผลลัพธ์ที่สร้างขึ้นทั้งหมดจะถูกเก็บไว้ใน "output_dir" รวมถึงไฟล์ Checkpoint ของโมเดล ไฟล์การกำหนดค่า และ Metrics การฝึก

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

### ทดสอบโมเดลที่ผ่านการ Fine-tune แล้ว

**llamafactory-cli chat** ออกแบบมาสำหรับการแชท/Inference แบบโต้ตอบกับ LLMs (ทั้งโมเดลพื้นฐานและโมเดลที่ผ่านการ LoRA Fine-tune แล้ว) LLaMA-Factory มีการกำหนดค่าตัวอย่างสำหรับรัน Inference ของโมเดลที่ผ่านการ Fine-tune แล้วใน [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference) คุณยังสามารถแก้ไขการกำหนดค่าตัวอย่างนี้เพื่อเปลี่ยนการตั้งค่า เช่น Backend ของ Inference

ใช้คำสั่งต่อไปนี้เพื่อทดสอบโมเดล Qwen3 ที่ผ่านการ Fine-tune แล้ว:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
ตัวอย่างการแชทโดยใช้โมเดลที่ผ่านการ Fine-tune แล้วแสดงไว้ด้านล่าง:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Export โมเดลที่ผ่านการ Fine-tune แล้ว

สำหรับกรณีการใช้งานในระดับ Production โมเดลที่ผ่านการฝึกมาแล้วและ LoRA Adapter จำเป็นต้องถูกรวมและ Export เป็นโมเดลเดียว โมเดลที่รวมแล้วนี้สามารถใช้เป็นไฟล์โมเดล Hugging Face ปกติได้ LLaMA-Factory มีการกำหนดค่าตัวอย่างใน [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora)

ใช้คำสั่งต่อไปนี้เพื่อ Export โมเดล Qwen3 ที่ผ่านการ Fine-tune แล้ว:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
ผลลัพธ์ของการ Export โมเดลที่ผ่านการ Fine-tune แล้วแสดงไว้ด้านล่าง

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

`LLaMA-Factory` ยังรองรับการ Fine-tune LLMs แบบไม่ต้องเขียนโค้ดผ่าน Web UI ในเบราว์เซอร์

ใช้คำสั่งต่อไปนี้เพื่อเปิด:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` มีอินเทอร์เฟซที่เรียบง่ายสำหรับจัดการ Workflow Machine Learning รวมถึงการฝึก การประเมิน การทำนาย การแชท และการ Export โมเดล ต่อไปนี้คือการแนะนำสั้นๆ ของแต่ละแท็บ:

* **Train**: แท็บนี้ช่วยให้คุณเลือกโมเดลและชุดข้อมูล กำหนดค่าพารามิเตอร์การฝึก และเริ่มกระบวนการฝึก การทำความเข้าใจพารามิเตอร์ที่จำเป็นและไม่จำเป็นมีความสำคัญในการปรับแต่งการตั้งค่าการฝึกให้เหมาะสม
* **Evaluate & Predict**: หลังจากการฝึก คุณสามารถประเมินประสิทธิภาพของโมเดลและทำการทำนายโดยใช้แท็บนี้ ซึ่งให้ข้อมูลเชิงลึกเกี่ยวกับความแม่นยำและประสิทธิผลของโมเดลบนข้อมูลใหม่
* **Chat**: เมื่อการฝึกเสร็จสมบูรณ์ โหลดโมเดลในแท็บ Chat เพื่อโต้ตอบกับมันและดูผลลัพธ์ของงานของคุณ ฟีเจอร์นี้เปิดใช้งานการสื่อสารแบบ Real-time กับโมเดลที่ผ่านการฝึกแล้ว
* **Export**: แท็บนี้อำนวยความสะดวกในการ Export โมเดลที่ผ่านการฝึกแล้วสำหรับการ Deploy หรือการใช้งานต่อไป คุณสามารถบันทึกโมเดลของคุณในรูปแบบต่างๆ ที่เหมาะสมสำหรับแอปพลิเคชันที่แตกต่างกัน

สำหรับคำแนะนำโดยละเอียด เราขอแนะนำให้คุณอ้างอิงเอกสารอย่างเป็นทางการใน [LlamaFactory GitHub repository](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) และ [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest) นอกจากนี้ [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) ยังให้ข้อมูลเชิงลึกที่มีคุณค่าเกี่ยวกับอินเทอร์เฟซและฟังก์ชันการทำงานของมัน

## ขั้นตอนถัดไป
- ลองใช้โมเดลต่างๆ เช่น `gpt-oss` และโมเดลที่ทันสมัยอื่นๆ
- ทดลองใช้ Backend ต่างๆ บนโมเดลที่ผ่านการ Fine-tune แล้ว
 
สำหรับเอกสารเพิ่มเติม โปรดเยี่ยมชม: https://llamafactory.readthedocs.io/en/latest/