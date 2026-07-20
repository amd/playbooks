<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> يستخدم هذا الدليل التوجيهي علامات خاصة لا يمكن لـ GitHub عرضها. يُرجى زيارة [amd.com/playbooks](https://amd.com/playbooks) لمعاينة هذا المحتوى بشكل صحيح.
<!-- @github-only:end -->

## نظرة عامة

يوضح هذا الدليل التوجيهي كيفية ضبط نموذج لغوي محليًا باستخدام Unsloth على أجهزة AMD.

يستخدم مثالًا قصيرًا للضبط الدقيق الخاضع للإشراف (SFT) مع محولات LoRA على `unsloth/gemma-4-E4B-it`، باستخدام مجموعة فرعية من مجموعة بيانات `mlabonne/FineTome-100k`. الهدف هو تزويدك بسير عمل بسيط من البداية إلى النهاية يغطي الإعداد والتدريب والاستدلال وحفظ النتيجة المضبوطة دقيقًا.

تم تصميم المثال ليكون عمليًا وسهل التعديل، بحيث يمكنك استخدامه كنقطة انطلاق لمجموعات البيانات والنماذج الخاصة بك.

## ما ستتعلمه

- كيفية إعداد بيئة Unsloth
- كيفية ضبط نموذج لغوي كبير باستخدام SFT مع Unsloth
- كيفية حفظ النتيجة المضبوطة دقيقًا في التخزين المحلي

<!-- @device:halo,stx,krk -->
> **ملاحظة:** تتطلب تقنيات الضبط الدقيق في هذا الدليل التوجيهي 24 جيجابايت على الأقل من ذاكرة GPU و32 جيجابايت من ذاكرة النظام (RAM).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **ملاحظة:** تتطلب تقنيات الضبط الدقيق في هذا الدليل التوجيهي 24 جيجابايت على الأقل من ذاكرة GPU و32 جيجابايت من ذاكرة النظام (RAM).
<!-- @os:end -->

<!-- @os:linux -->
> **ملاحظة:** تتطلب تقنيات الضبط الدقيق في هذا الدليل التوجيهي 24 جيجابايت على الأقل من ذاكرة GPU **المخصصة** و32 جيجابايت من ذاكرة النظام (RAM).
<!-- @os:end -->
<!-- @device:end -->

## لماذا Unsloth؟

تُسهّل Unsloth تشغيل عملية الضبط الدقيق للنماذج اللغوية الكبيرة على الأجهزة المحلية من خلال تقليل استخدام الذاكرة وتسريع التدريب مقارنةً بالإعداد القياسي.

في هذا الدليل التوجيهي، نستخدم Unsloth جنبًا إلى جنب مع **SFT القائم على LoRA**. هذا يعني أن النموذج الأساسي يبقى مجمدًا في معظمه، بينما يتم تدريب مجموعة أصغر بكثير من أوزان المحولات. هذا مناسب جدًا للتطوير المحلي لأنه أخف من الضبط الدقيق الكامل وأسرع في التكرار عليه.

تدعم Unsloth أيضًا أساليب تدريب أخرى، بما في ذلك QLoRA وسير عمل التعلم المعزز. يركز هذا الدليل التوجيهي على أبسط مسار أولًا: مثال بسيط للضبط الدقيق باستخدام LoRA يمكن للمستخدمين تشغيله وفهمه وتوسيعه.

## ضبط إعداد الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج
> **ملاحظة**: إذا لم يكن VS Code مثبتًا، يمكنك تثبيته باستخدام Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرنامج

### إنشاء بيئة افتراضية

<!-- @os:linux -->
<!-- @device:halo_box -->
افتح نافذة طرفية وأنشئ بيئة افتراضية (venv) مع تثبيت AMD ROCm™ software وPyTorch مسبقًا:
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
**امنح مستخدمك حق الوصول إلى أجهزة GPU** (يجب تسجيل الخروج ثم تسجيل الدخول مجددًا لتفعيل هذا التغيير):

```bash
sudo usermod -aG render,video $LOGNAME
```

افتح نافذة طرفية وأنشئ بيئة افتراضية (venv):
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
> **ملاحظة:** يُشترط استخدام Python 3.13 على نظام Windows.

<!-- @device:halo_box -->
افتح نافذة PowerShell وأنشئ بيئة افتراضية:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
افتح نافذة PowerShell وأنشئ بيئة افتراضية:
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

> **ملاحظة:** أثناء عملية الاستيراد، قد تقوم Unsloth باستكشاف مسارات تسريع اختيارية خاصة بـ `bitsandbytes`. في بعض إصدارات ROCm، قد تظهر رسالة مثل `bitsandbytes library load error: Configured ROCm binary not found`. يستخدم هذا الدليل التوجيهي الضبط الدقيق القياسي باستخدام LoRA مع `optim="adamw_torch"`، لذا فإننا لا نعتمد على محسّن `bitsandbytes` أو QLoRA رباعي البت. يمكن تجاهل هذه الرسالة بأمان.

<!-- @os:windows -->
> **ملاحظة:** على نظام Windows مع ROCm، ستطبع Unsloth عدة تحذيرات عند بدء التشغيل — راجع [التحذيرات المعروفة](#known-warnings) أدناه. جميعها آمنة ويمكن تجاهلها؛ يعمل التدريب بشكل صحيح.
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

## تنزيل سكربت الضبط الدقيق الخاص بـ Unsloth

بدلًا من تنفيذ كل خطوة يدويًا، يوفر هذا الدليل التوجيهي سكربتًا نظيفًا من البداية إلى النهاية هنا: [test_unsloth.py](assets/test_unsloth.py).

قم بتشغيل الكود التالي لتنفيذ السكربت:

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

سيستعرض بقية هذا الدليل التوجيهي مفاهيميًا كل خطوة رئيسية من خطوات السكربت.

## كيف يعمل

يقوم سكربت test_unsloth.py بتنفيذ الخطوات التالية:
* **تحميل النموذج**: يقوم بتحميل unsloth/gemma-4-E4B-it باستخدام FastModel.
* **تحضير البيانات**: يوحّد مجموعة البيانات (مثل FineTome-100k) ويطبّق قالب محادثة Gemma-4.
* **تطبيق LoRA**: يضيف محولات إلى وحدات اللغة والانتباه وMLP لتدريب فعّال.
* **التدريب**: يستخدم SFTTrainer مع إخفاء الخسارة الخاص بالاستجابة فقط.
* **الاستدلال**: يقوم بتشغيل اختبار توليد سريع للتحقق من الأداء.
* **الحفظ**: يقوم بتصدير محولات LoRA محليًا.

## الإعدادات الرئيسية

يمكنك تعديل الثوابت التالية لتخصيص عملية التشغيل الخاصة بك:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

مثال على رسالة الترحيب الخاصة بـ Unsloth والناتج عند تحميل أوزان النموذج:

![alt text](assets/welcome.png)

## تحضير مجموعة البيانات

نستخدم مجموعة فرعية من:
```text
mlabonne/FineTome-100k
```
يتم تجهيز مجموعة البيانات كالتالي:
* تحويلها إلى تنسيق محادثة
* معالجتها باستخدام قالب محادثة Gemma-4
* تنظيفها لإزالة رموز BOS المكررة

## تدريب النموذج

يقوم السكربت بتشغيل عرض تدريبي قصير، بالمعلمات التالية:
- ما يقارب 50 خطوة
- حجم دفعة صغير
- تجميع التدرجات

أثناء التدريب، ستشاهد سجلات مثل:

![alt text](assets/training.png)


## الحفظ والنشر

### الحفظ المحلي (LoRA)

يقوم السكربت تلقائيًا بحفظ محولات LoRA في OUTPUT_DIR.
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
> **ملاحظة:** لا يدعم vLLM نظام Windows. لنشر نموذجك المضبوط دقيقًا على Windows، استخدم llama.cpp (راجع [تصدير GGUF](#export-gguf-for-llamacpp) أدناه) أو انقل النموذج المدمج إلى جهاز يعمل بنظام Linux يشغّل vLLM.
<!-- @os:end -->

<!-- @os:linux -->
للنشر باستخدام vLLM، ادمج المحولات في نموذج كامل:
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

قم بالتحويل مباشرةً إلى GGUF للاستدلال المحلي:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## التحذيرات المعروفة

يقوم Unsloth بطباعة هذه التحذيرات عند بدء التشغيل على Windows ROCm، وجميعها آمنة ويمكن تجاهلها:

| التحذير | السبب | آمن للتجاهل؟ |
|---|---|---|
| `bitsandbytes library load error` | لا يوجد لـ bitsandbytes إصدار مبني لـ Windows ROCm | نعم — يستخدم هذا الدليل `adamw_torch`، وليس bnb |
| `No ROCm platform found for torch.distributed` | يفتقر ROCm على Windows إلى دعم التدريب الموزع | نعم — لا يتأثر التدريب على وحدة معالجة رسومات واحدة |
| `Unsloth: WARNING! You are using an unsupported platform` | يشير Unsloth إلى الإصدارات غير القائمة على Linux | نعم — يعمل Windows ROCm مع SFT على وحدة معالجة رسومات واحدة |
| `triton is not available` | لا يوجد لـ Triton إصدار مبني لـ Windows | نعم — يعود Unsloth إلى نوى PyTorch كبديل |

سيستمر التدريب بشكل صحيح رغم هذه التحذيرات.
<!-- @os:end -->

## الخطوات التالية
- جرّب [Unsloth Studio](https://unsloth.ai/docs/new/studio)، وهي واجهة مستخدم رسومية سهلة الاستخدام لـ Unsloth
- درّب النموذج على مجموعات البيانات الخاصة بك
- جرّب الضبط الدقيق بمعاملات فائقة مختلفة
- انشر النموذج باستخدام vLLM أو llama.cpp
- جرّب QLoRA للحصول على إعداد يستهلك ذاكرة أقل

## الموارد

فيما يلي بعض الموارد الإضافية لمعرفة المزيد عن Unsloth والضبط الدقيق:

* [وثائق Unsloth](https://docs.unsloth.ai)

* [مستودع Unsloth على GitHub](https://github.com/unslothai/unsloth)

* [دليل Unsloth للضبط الدقيق](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)