<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## نظرة عامة

يوضح هذا الدليل كيفية ضبط نموذج لغوي محلياً باستخدام Unsloth على أجهزة AMD.

يستخدم مثالاً قصيراً للضبط الدقيق الخاضع للإشراف (SFT) مع محولات LoRA على `unsloth/gemma-4-E4B-it`، باستخدام مجموعة فرعية من مجموعة البيانات `mlabonne/FineTome-100k`. الهدف هو تزويدك بسير عمل بسيط من البداية إلى النهاية يغطي الإعداد والتدريب والاستنتاج وحفظ النتيجة المضبوطة.

تم تصميم المثال ليكون عملياً وسهل التعديل، حتى تتمكن من استخدامه كنقطة انطلاق لمجموعات بياناتك ونماذجك الخاصة.

## ما ستتعلمه

- كيفية إعداد بيئة Unsloth
- كيفية ضبط نموذج لغوي كبير باستخدام SFT مع Unsloth
- كيفية حفظ النتيجة المضبوطة في التخزين المحلي

<!-- @device:halo,stx,krk -->
> **ملاحظة:** تتطلب تقنيات الضبط الدقيق في هذا الدليل ما لا يقل عن 24 جيجابايت من ذاكرة GPU و32 جيجابايت من ذاكرة الوصول العشوائي للنظام.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **ملاحظة:** تتطلب تقنيات الضبط الدقيق في هذا الدليل ما لا يقل عن 24 جيجابايت من ذاكرة GPU و32 جيجابايت من ذاكرة الوصول العشوائي للنظام.
<!-- @os:end -->

<!-- @os:linux -->
> **ملاحظة:** تتطلب تقنيات الضبط الدقيق في هذا الدليل ما لا يقل عن 24 جيجابايت من ذاكرة GPU **المخصصة** و32 جيجابايت من ذاكرة الوصول العشوائي للنظام.
<!-- @os:end -->
<!-- @device:end -->

## لماذا Unsloth؟

يجعل Unsloth الضبط الدقيق لنماذج اللغة الكبيرة أسهل للتشغيل على الأجهزة المحلية من خلال تقليل استخدام الذاكرة وتسريع التدريب مقارنةً بالإعداد القياسي.

في هذا الدليل، نستخدم Unsloth مع **SFT المستند إلى LoRA**. وهذا يعني أن النموذج الأساسي يبقى مجمداً في معظمه، بينما يتم تدريب مجموعة أصغر بكثير من أوزان المحول. يُعدّ هذا مناسباً للتطوير المحلي لأنه أخف من الضبط الدقيق الكامل وأسرع في التكرار.

يدعم Unsloth أيضاً مناهج تدريب أخرى، بما في ذلك QLoRA وسير عمل التعلم المعزز. يركز هذا الدليل على أبسط مسار أولاً: مثال صغير للضبط الدقيق باستخدام LoRA يمكن للمستخدمين تشغيله وفهمه وتوسيعه.

## ضبط تكوين الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج
> **ملاحظة**: إذا لم يكن VS Code مثبتاً، يمكنك تثبيته من خلال Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرامج

### إنشاء بيئة افتراضية

<!-- @os:linux -->
<!-- @device:halo_box -->
افتح طرفية وأنشئ بيئة venv مع تثبيت برنامج AMD ROCm™ و PyTorch مسبقاً:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**امنح مستخدمك حق الوصول إلى أجهزة GPU** (سجّل الخروج وأعد تسجيل الدخول لتفعيل ذلك):

```bash
sudo usermod -aG render,video $LOGNAME
```

افتح طرفية وأنشئ بيئة venv:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة:** يُشترط استخدام Python 3.13 على Windows.

<!-- @device:halo_box -->
افتح طرفية PowerShell وأنشئ بيئة افتراضية:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
افتح طرفية PowerShell وأنشئ بيئة افتراضية:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### تثبيت التبعيات الأساسية
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

### تبعيات إضافية

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **ملاحظة:** أثناء الاستيراد، قد يستكشف Unsloth مسارات تسريع `bitsandbytes` الاختيارية. في بعض إصدارات ROCm، قد تظهر رسالة مثل `bitsandbytes library load error: Configured ROCm binary not found`. يستخدم هذا الدليل الضبط الدقيق القياسي باستخدام LoRA مع `optim="adamw_torch"`، لذا لا نعتمد على محسّن `bitsandbytes` أو QLoRA ذي 4 بت. يمكن تجاهل هذه الرسالة بأمان.

<!-- @os:windows -->
> **ملاحظة:** على Windows ROCm، سيطبع Unsloth عدة تحذيرات عند بدء التشغيل — راجع [التحذيرات المعروفة](#known-warnings) أدناه. يمكن تجاهل جميعها بأمان؛ إذ يعمل التدريب بشكل صحيح.
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## تنزيل سكريبت الضبط الدقيق لـ Unsloth

بدلاً من تنفيذ كل خطوة يدوياً، يوفر هذا الدليل سكريبتاً نظيفاً من البداية إلى النهاية هنا: [test_unsloth.py](assets/test_unsloth.py).

شغّل الكود التالي لتنفيذ السكريبت:

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

سيستعرض باقي الدليل مفاهيمياً كل خطوة رئيسية في السكريبت.

## كيف يعمل

يُنفّذ سكريبت test_unsloth.py الخطوات التالية:
* **تحميل النموذج**: يحمّل unsloth/gemma-4-E4B-it باستخدام FastModel.
* **إعداد البيانات**: يوحّد مجموعة البيانات (مثل FineTome-100k) ويطبّق قالب محادثة Gemma-4.
* **تطبيق LoRA**: يضيف محولات إلى وحدات اللغة والانتباه و MLP للتدريب الفعّال.
* **التدريب**: يستخدم SFTTrainer مع إخفاء الخسارة المقتصرة على الاستجابة.
* **الاستنتاج**: يُجري اختبار توليد سريع للتحقق من الأداء.
* **الحفظ**: يُصدّر محولات LoRA محلياً.

## التكوين الرئيسي

يمكنك تعديل الثوابت التالية لتخصيص تشغيلك:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

مثال على رسالة الترحيب من Unsloth والمخرجات عند تحميل أوزان النموذج:

![نص بديل](assets/welcome.png)

## إعداد مجموعة البيانات

نستخدم مجموعة فرعية من:
```text
mlabonne/FineTome-100k
```
مجموعة البيانات:
* مُحوَّلة إلى تنسيق المحادثة
* مُعالَجة باستخدام قالب محادثة Gemma-4
* مُنقَّحة لإزالة رموز BOS المكررة

## تدريب النموذج

يُشغّل السكريبت عرضاً تجريبياً قصيراً للتدريب بالمعاملات التالية:
- ~50 خطوة
- حجم دُفعة صغير
- تراكم التدرجات

أثناء التدريب، ستظهر لك سجلات مثل:

![نص بديل](assets/training.png)


## الحفظ والنشر

### الحفظ المحلي (LoRA)

يحفظ السكريبت تلقائياً محولات LoRA في OUTPUT_DIR.
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### حفظ النموذج المدمج (لـ vLLM)

<!-- @os:windows -->
> **ملاحظة:** لا يدعم vLLM نظام Windows. لنشر نموذجك المضبوط على Windows، استخدم llama.cpp (راجع [تصدير GGUF](#export-gguf-for-llamacpp) أدناه) أو انقل النموذج المدمج إلى جهاز Linux يعمل عليه vLLM.
<!-- @os:end -->

<!-- @os:linux -->
للنشر مع vLLM، ادمج المحولات في نموذج كامل:
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### تصدير GGUF (لـ llama.cpp)

حوّل مباشرةً إلى GGUF للاستنتاج المحلي:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## التحذيرات المعروفة

تُطبع هذه التحذيرات بواسطة Unsloth عند بدء التشغيل على Windows ROCm وجميعها آمنة للتجاهل:

| التحذير | السبب | آمن للتجاهل؟ |
|---|---|---|
| `bitsandbytes library load error` | لا يوجد إصدار bitsandbytes لـ Windows ROCm | نعم — يستخدم هذا الدليل `adamw_torch` وليس bnb |
| `No ROCm platform found for torch.distributed` | يفتقر ROCm على Windows إلى التدريب الموزع | نعم — التدريب على GPU واحد غير متأثر |
| `Unsloth: WARNING! You are using an unsupported platform` | يُشير Unsloth إلى الإصدارات غير المبنية على Linux | نعم — يعمل Windows ROCm لـ SFT على GPU واحد |
| `triton is not available` | لا يوجد إصدار Triton لـ Windows | نعم — يعود Unsloth إلى نوى PyTorch |

سيستمر التدريب بشكل صحيح على الرغم من هذه التحذيرات.
<!-- @os:end -->

## الخطوات التالية
- جرّب [Unsloth Studio](https://unsloth.ai/docs/new/studio)، واجهة رسومية بديهية لـ Unsloth
- درّب على مجموعات بياناتك الخاصة
- جرّب الضبط الدقيق بمعاملات فائقة مختلفة
- انشر باستخدام vLLM أو llama.cpp
- جرّب QLoRA للحصول على إعداد بذاكرة أقل

## الموارد

فيما يلي بعض الموارد الإضافية لمعرفة المزيد عن Unsloth والضبط الدقيق:

* [توثيق Unsloth](https://docs.unsloth.ai)

* [Unsloth على GitHub](https://github.com/unslothai/unsloth)

* [دليل الضبط الدقيق لـ Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)