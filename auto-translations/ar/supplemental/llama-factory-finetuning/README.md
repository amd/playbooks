## نظرة عامة

يُعدّ الضبط الدقيق الفعّال أمرًا بالغ الأهمية لتكييف نماذج اللغة الكبيرة (LLMs) مع المهام اللاحقة. LLaMA-Factory هي منصة مفتوحة المصدر وسهلة الاستخدام تُبسّط عملية تدريب وضبط نماذج اللغة الكبيرة والنماذج متعددة الوسائط. وتتيح للمستخدمين تخصيص مئات النماذج المدرّبة مسبقًا محليًا بأدنى قدر من البرمجة.

يُعلّمك هذا الدليل كيفية ضبط نماذج LLMs دقيقًا باستخدام LLaMA-Factory على أجهزة AMD المحلية الخاصة بك.

<!-- @device:stx,krk -->
> **ملاحظة:** تتطلب تقنيات الضبط الدقيق في هذا الدليل ما لا يقل عن **32 جيجابايت من ذاكرة الوصول العشوائي للنظام**، مع توفر ما لا يقل عن **16 جيجابايت منها للـ GPU** (الـ 16 جيجابايت هي جزء من الـ 32 جيجابايت، وليست إضافةً إليها).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **ملاحظة:** تتطلب تقنيات الضبط الدقيق في هذا الدليل ما لا يقل عن **16 جيجابايت من إجمالي ذاكرة GPU** و**32 جيجابايت من ذاكرة الوصول العشوائي للنظام**.
> - على نظام Windows، تجمع ذاكرة GPU الإجمالية بين ذاكرة VRAM المخصصة لبطاقة الرسومات وذاكرة GPU المشتركة (المستعارة من ذاكرة الوصول العشوائي للنظام).
> - لذلك، يمكن للبطاقات التي تحتوي على أقل من 16 جيجابايت من VRAM المخصصة تشغيل هذا الدليل باستخدام ذاكرة GPU المشتركة لتعويض الفارق.
<!-- @os:end -->

<!-- @os:linux -->
> **ملاحظة:** تتطلب تقنيات الضبط الدقيق في هذا الدليل بطاقة رسومات تحتوي على ما لا يقل عن **16 جيجابايت من ذاكرة GPU المخصصة** و**32 جيجابايت من ذاكرة الوصول العشوائي للنظام**.
> - على نظام Linux، يعمل التدريب بالكامل في ذاكرة VRAM المخصصة لبطاقة الرسومات.
> - لا يتراجع إلى ذاكرة GPU المشتركة (ذاكرة الوصول العشوائي للنظام) عند نفاد ذاكرة VRAM.
> - ستنفد ذاكرة البطاقات التي تحتوي على أقل من 16 جيجابايت من VRAM المخصصة أثناء التدريب على Linux، حتى لو كان النظام يحتوي على ذاكرة وصول عشوائي وفيرة.
<!-- @os:end -->
<!-- @device:end -->

## ما ستتعلمه

- كيفية إعداد LLaMA-Factory مع برنامج AMD ROCm™
- كيفية تهيئة معاملات الضبط الدقيق لنماذج LLM (باستخدام Qwen/Qwen3-4B-Instruct-2507 كمثال)
- كيفية تشغيل الضبط الدقيق باستخدام LLaMA-Factory
- كيفية تشغيل الاستدلال باستخدام النموذج المضبوط دقيقًا
- كيفية تصدير النموذج المضبوط دقيقًا

## الوقت التقديري

- المدة: سيستغرق تشغيل هذا الدليل حوالي 60 دقيقة (اعتمادًا على حجم النموذج/مجموعة البيانات وسرعة الشبكة).
- اطّلع على [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) للحصول على مزيد من المعلومات.

## ضبط تهيئة الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرامج

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

#### إنشاء بيئة افتراضية

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
**منح مستخدمك حق الوصول إلى أجهزة GPU** (سجّل الخروج وأعد تسجيل الدخول لتفعيل هذا الإعداد):

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

### تثبيت التبعيات الأساسية

<!-- @require:pytorch,driver -->
 
### تثبيت التبعيات الإضافية

> **ملاحظة**: تأكد من أن إصدار Python هو 3.11 أو 3.12 أو 3.13

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

### تثبيت LLaMA-Factory

يعتمد LLaMA-Factory على PyTorch. يجب أن تكون قد ثبّتته بالفعل وفقًا للمتطلبات المذكورة أعلاه.

نزّل الكود المصدري من [مستودع LLaMA Factory الرسمي على GitHub](https://github.com/hiyouga/LlamaFactory)، وثبّت تبعياته.

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

تحقق مما إذا كان `llamafactory-cli` قابلًا للتنفيذ.

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

مثال على المخرجات:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

بعد تثبيت LLaMA-Factory بنجاح، لنشغّل الضبط الدقيق عليه.

## استخدام واجهة سطر أوامر LLaMA-Factory للضبط الدقيق

يغطي هذا القسم كيفية إعداد مجموعات بيانات الضبط الدقيق، وتهيئة معاملات LoRA/QLoRA، وتشغيل الضبط الدقيق باستخدام LoRA.

### إعداد مجموعة البيانات

يدعم LLaMA-Factory مجموعات بيانات الضبط الدقيق بتنسيق Alpaca وتنسيق ShareGPT. جميع مجموعات البيانات المتاحة مُعرَّفة في [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). إذا كنت تستخدم مجموعة بيانات مخصصة، فتأكد من إضافة وصف لمجموعة البيانات في `dataset_info.json` وتحديد اسم مجموعة البيانات قبل التدريب. يمكن الاطلاع على التفاصيل في وثائقهم [هنا](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

في هذا الدليل، سنستخدم مجموعتَي بيانات identity وalpaca_en_demo كمثال، وسنهيّئ معلومات مجموعة البيانات في الخطوة التالية.


### تهيئة معاملات الضبط الدقيق

يدعم LLaMA-Factory مخططات ضبط دقيق متعددة.

| مخططات الضبط الدقيق | أمثلة LLaMA-Factory |
|-----------|------|
| المعاملات الكاملة    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| الضبط الدقيق باستخدام LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| الضبط الدقيق باستخدام QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

تحدد ملفات التهيئة النموذجية هذه معاملات النموذج، ومعاملات طريقة الضبط الدقيق، ومعاملات مجموعة البيانات، ومعاملات التقييم، وغير ذلك. يمكنك تهيئتها وفقًا لاحتياجاتك الخاصة. في هذا الدليل، سنستخدم [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml).

**شرح المعاملات الرئيسية:**
- `model_name_or_path` - اسم نموذج Hugging Face أو مسار ملف النموذج المحلي.
- `stage` - مرحلة التدريب. الخيارات: rm (نمذجة المكافأة)، pt (التدريب المسبق)، sft (الضبط الدقيق الخاضع للإشراف)، PPO، DPO، KTO، ORPO.
- `do_train` - true للتدريب، false للتقييم.
- `finetuning_type` - طريقة الضبط الدقيق. الخيارات: freeze، lora، full.
- `lora_rank` - أبعاد المصفوفة منخفضة الرتبة المستخدمة في LoRA، القيم النموذجية: 4، 6، 8، 16 (القيم الأصغر = معاملات أقل = ضبط دقيق أسرع؛ القيم الأكبر = تكيّف أفضل مع المهمة لكن استخدام موارد أعلى).
- `lora_target` - الوحدات المستهدفة لطريقة LoRA. الافتراضي: all.
- `dataset` - مجموعة (مجموعات) البيانات المراد استخدامها. استخدم "," للفصل بين مجموعات البيانات المتعددة.
- `output_dir` - مسار مخرجات الضبط الدقيق.
- `logging_steps` - فترة التسجيل بالخطوات.
- `save_steps` - فترة حفظ نقطة تفتيش النموذج.
- `overwrite_output_dir` - ما إذا كان يُسمح بالكتابة فوق دليل المخرجات.
- `per_device_train_batch_size` - حجم دفعة التدريب لكل جهاز.
- `gradient_accumulation_steps` - عدد خطوات تراكم التدرج.
- `learning_rate` - معدل التعلم.
- `num_train_epochs` - عدد حقب التدريب.
- `lr_scheduler_type` - جدول معدل التعلم. الخيارات: linear، cosine، polynomial، constant، إلخ.
- `warmup_ratio` - نسبة الإحماء لمعدل التعلم.

<!-- @os:linux -->
سنعدّل القيمة الافتراضية لـ `lora_rank` لتشغيل الضبط الدقيق على وحدات معالجة الرسومات AMD Ryzen™ وAMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
سنحدّث تهيئة الضبط الدقيق الافتراضية باستخدام LoRA لتحسين التوافق مع وحدات معالجة الرسومات AMD Ryzen™ وAMD Radeon™:
- تعيين `lora_rank` من `8` إلى `6` لتقليل استخدام الذاكرة أثناء الضبط الدقيق.
- استخدام `fp16` بدلًا من `bf16` لتحقيق توافق أوسع مع وحدات معالجة الرسومات AMD وتقليل استخدام الذاكرة.
- تعيين `dataloader_num_workers` إلى `0` على نظام Windows لتجنب أخطاء `"Can't pickle local object<>"` الناجمة عن تحميل البيانات متعدد العمليات.

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

### تشغيل الضبط الدقيق باستخدام LLaMA-Factory

**llamafactory-cli** هي أداة واجهة سطر الأوامر (CLI) الرسمية لـ LLaMA-Factory، وقد طُوِّرت لتبسيط سير عمل نماذج LLM الشاملة (إعداد البيانات ← الضبط الدقيق ← التقييم ← النشر) دون كتابة كود معقد.

للتدريب/الضبط الدقيق، يُعدّ **llamafactory-cli train** الأمر الفرعي الأساسي لواجهة سطر أوامر LLaMA-Factory. إذ يُجرّد سير عمل الضبط الدقيق (المعالجة المسبقة للبيانات، وضبط المعاملات الفائقة، وتحسين الأجهزة) في أمر CLI واحد، ويدعم مخططات ضبط دقيق متعددة (LoRA/QLoRA/الضبط الدقيق الكامل) وهو مُحسَّن لوحدات معالجة الرسومات ذات الموارد المحدودة (مثل QLoRA على 16 جيجابايت VRAM).

يمكنك تشغيل الضبط الدقيق باستخدام LLaMA-Factory عبر الأمر التالي، المستند إلى ملف التهيئة المعدَّل للضبط الدقيق باستخدام LoRA لنموذج Qwen3.

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

بعد تشغيل الضبط الدقيق لنموذج LLM، تُخزَّن جميع المخرجات المُولَّدة في "output_dir"، بما في ذلك ملفات نقاط تفتيش النموذج، وملفات التهيئة، ومقاييس التدريب.

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

### اختبار النموذج المضبوط دقيقًا

**llamafactory-cli chat** مصمَّم للمحادثة التفاعلية/الاستدلال مع نماذج LLMs (سواء النماذج الأساسية أو النماذج المضبوطة دقيقًا باستخدام LoRA). يوفر LLaMA-Factory تهيئة نموذجية لتشغيل الاستدلال على النماذج المضبوطة دقيقًا في [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). يمكنك أيضًا تعديل هذه التهيئة النموذجية لتغيير الإعدادات، مثل خلفية الاستدلال.

استخدم الأمر التالي لاختبار النموذج المضبوط دقيقًا Qwen3:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
يُعرض أدناه مثال على محادثة باستخدام النموذج المضبوط دقيقًا:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### تصدير النموذج المضبوط دقيقًا

لحالات الاستخدام الإنتاجية، يجب دمج النموذج المدرَّب مسبقًا ومحوّل LoRA وتصديرهما في نموذج واحد. يمكن استخدام هذا النموذج المدمج كملف نموذج Hugging Face عادي. يوفر LLaMA-Factory تهيئات نموذجية في [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

استخدم الأمر التالي لتصدير النموذج المضبوط دقيقًا Qwen3:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
تُعرض أدناه نتيجة تصدير النموذج المضبوط دقيقًا.

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

## استخدام واجهة المستخدم الرسومية لـ LLaMA-Factory

يدعم `LLaMA-Factory` أيضًا الضبط الدقيق لنماذج LLMs بدون كود عبر واجهة مستخدم ويب في المتصفح.

استخدم الأمر التالي لفتحها:

```bash
llamafactory-cli webui
```
تقدم `LlamaFactory Web UI` واجهة مبسّطة لإدارة سير عمل التعلم الآلي، بما في ذلك التدريب والتقييم والتنبؤ والمحادثة وتصدير النماذج. فيما يلي مقدمة موجزة لكل تبويب:

* **Train (التدريب)**: يتيح لك هذا التبويب تحديد نموذج ومجموعة بيانات، وتهيئة معاملات التدريب، وبدء عملية التدريب. من الضروري فهم المعاملات الإلزامية والاختيارية لتحسين إعداد التدريب.
* **Evaluate & Predict (التقييم والتنبؤ)**: بعد التدريب، يمكنك تقييم أداء النموذج وإجراء تنبؤات باستخدام هذا التبويب. يوفر رؤى حول دقة النموذج وفعاليته على البيانات الجديدة.
* **Chat (المحادثة)**: بمجرد اكتمال التدريب، حمّل النموذج في تبويب المحادثة للتفاعل معه ورؤية نتائج عملك. تتيح هذه الميزة التواصل في الوقت الفعلي مع النموذج المدرَّب.
* **Export (التصدير)**: يُسهّل هذا التبويب تصدير النماذج المدرَّبة للنشر أو الاستخدام الإضافي. يمكنك حفظ نماذجك بتنسيقات مختلفة مناسبة لتطبيقات متعددة.

للحصول على إرشادات تفصيلية، نشجعك على الرجوع إلى الوثائق الرسمية في [مستودع LlamaFactory على GitHub](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) و[وثائق LlamaFactory على ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). بالإضافة إلى ذلك، يوفر [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) رؤى قيّمة حول الواجهة ووظائفها.

## الخطوات التالية
- جرّب نماذج مختلفة مثل `gpt-oss` وغيرها من النماذج الحديثة المتطورة.
- جرّب خلفيات مختلفة على النموذج المضبوط دقيقًا.
 
لمزيد من الوثائق، يُرجى زيارة: https://llamafactory.readthedocs.io/en/latest/