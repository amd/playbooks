<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## نظرة عامة


هل تريد تشغيل نماذج لغوية قوية للذكاء الاصطناعي على أجهزتك الخاصة؟ يوضح لك هذا الدليل كيفية القيام بذلك.
يستخدم هذا الدرس التعليمي PyTorch المدعوم بواسطة برمجيات AMD ROCm™ لتشغيل نماذج قادرة على تلخيص المستندات، والإجابة على الأسئلة، وتوليد النصوص، والمزيد، وكل ذلك يعمل محليًا.

## ما ستتعلمه

- تشغيل نماذج اللغة الكبيرة مثل gpt-oss-20b وqwen3.5-4B محليًا باستخدام PyTorch وROCm
- إنشاء أداة تلخيص مستندات باستخدام نماذج اللغة الكبيرة

<!-- @device:halo_box,halo,stx,krk -->
## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرمجيات
> **ملاحظة**: إذا لم يكن VS Code مثبتًا، يمكنك تثبيته عبر Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرمجيات الأساسية

### إنشاء بيئة افتراضية

<!-- @os:linux -->
<!-- @device:halo_box -->
على نظام Linux، افتح طرفية (terminal) في الدليل الذي تختاره واتبع الأوامر لإنشاء venv مع تثبيت ROCm+Pytorch مسبقًا.
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
**امنح مستخدمك صلاحية الوصول إلى أجهزة GPU** (يجب تسجيل الخروج والدخول مجددًا لتفعيل ذلك):

```bash
sudo usermod -aG render,video $LOGNAME
```

على نظام Linux، افتح طرفية (terminal) في الدليل الذي تختاره واتبع الأوامر لإنشاء venv.
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
على نظام Windows، افتح طرفية (terminal) في الدليل الذي تختاره واتبع الأوامر لإنشاء venv مع تثبيت ROCm+Pytorch مسبقًا.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
على نظام Windows، افتح طرفية (terminal) في الدليل الذي تختاره واتبع الأوامر لإنشاء venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **نصيحة**: قد يحتاج مستخدمو Windows إلى تعديل سياسة تنفيذ PowerShell الخاصة بهم (مثل
> ضبطها على RemoteSigned أو Unrestricted) قبل تشغيل بعض أوامر Powershell.

<!-- @os:end -->

### تثبيت التبعيات الأساسية
<!-- @require:driver,pytorch -->

### تثبيت التبعيات الإضافية

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

> **ملاحظة:** إذا فشل تحميل النموذج أو نفدت الذاكرة، جرّب تثبيت حزمة `kernels` لتحميل النموذج مع تكميم (quantization) محسّن.
>
> ```bash
> # استخدم هذا الإصدار المتوافق مع إصدار Transformers
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

## البدء السريع باستخدام النصوص البرمجية النموذجية

يتضمن هذا الدليل نصوصًا برمجية جاهزة للاستخدام. انقر عليها لمعاينتها وتنزيلها إلى نفس الدليل الذي أنشأت فيه البيئة.

| النص البرمجي | الوصف | الاستخدام |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | توليد نص أساسي باستخدام نموذج لغوي كبير | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | ملخِّص مستندات مع دعم Harmony | `python summarizer.py --file document.txt` |

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

كلا النصين البرمجيين يدعمان:
- اختيار النموذج عبر العلامة `--model`
- تنسيق قالب المحادثة (chat template) لضمان توجيه صحيح للنموذج، وهو مفيد بشكل خاص لتلخيص المستندات

## تحميل وتشغيل أول نموذج لغوي كبير خاص بك

يوضح النص البرمجي المرفق [run_llm.py](assets/run_llm.py) كيفية توليد النصوص باستخدام نماذج اللغة الكبيرة عبر PyTorch وAMD ROCm.

> **ملاحظة:** عند تحميل نموذج، يتحقق Hugging Face Transformers أولًا من ذاكرة التخزين المؤقت المحلية (`~/.cache/huggingface/hub` على Linux، و`C:\Users\<user>\.cache\huggingface\hub` على Windows). إذا لم يكن النموذج مخزنًا مؤقتًا، فسيتم تنزيله تلقائيًا من huggingface.co. قد يستغرق التشغيل الأول بضع دقائق حسب حجم النموذج وسرعة الشبكة.

يوضح المقتطف أدناه كيفية استخدام النموذج وتخصيص الأسئلة المطروحة.

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

جرّب النص البرمجي الذي تم تنزيله:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## بناء ملخِّص مستندات

بعد أن قمت بتوليد مخرجات نموذج لغوي كبير محليًا، يمكنك البناء على ذلك من خلال إنشاء ملخِّص مستندات عملي. في هذا القسم، ستستخدم النص البرمجي [summarizer.py](assets/summarizer.py) لتزويده بملف .txt وتوليد ملخص موجز تلقائيًا، وكل ذلك يعمل محليًا على وحدة معالجة الرسومات (GPU) الخاصة بك.

تم تصميم النص البرمجي ليعمل جاهزًا دون تعديل. افتح النص البرمجي في محرر لاستكشاف الكود، وتخصيص المطالبات (prompts)، وضبط المعاملات مثل الطول ودرجة الحرارة (temperature).

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### أمثلة على الاستخدام

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

## تعرّف على معاملات التوليد

| المعامل | ما الذي يتحكم فيه | القيم النموذجية |
|-----------|------------------|----------------|
| `max_new_tokens` | الطول الأقصى لمخرجات النموذج اللغوي الكبير | استخدم 50–500 رمز (token) للملخصات. (الرمز الواحد يعادل حوالي 0.75 كلمة إنجليزية) |
| `temperature` | الإبداع. القيم المنخفضة تجعله مركزًا، بينما القيم المرتفعة تأتي بمزيد من عدم القدرة على التنبؤ | - **0.1–0.3**: مركّز، حتمي (جيد للملخصات) <br> **0.5–0.7**: متوازن (استخدام عام) <br> **0.8–1.0**: إبداعي، متنوع (لجلسات العصف الذهني) |
| `top_p` | أخذ العينات النووي (Nucleus Sampling) - القيم المنخفضة تحد من مخرجات النموذج لتكون أكثر تحديدًا | **0.1-0.5**: صارم، يمكن التنبؤ به <br> **0.9-0.95**: (قياسي، طبيعي، حواري) |


## تطبيقات واقعية

- **تحليل الأوراق البحثية**: استخلاص النتائج الرئيسية من المنشورات المعقدة لمراجعة سريعة
- **تجميع الأخبار**: تلخيص المقالات الإخبارية في ملخصات يومية موجزة أو أبرز النقاط
- **ملاحظات الاجتماعات**: تكثيف النصوص المكتوبة إلى بنود قابلة للتنفيذ وملخصات موجزة
- **مراجعة المستندات القانونية**: استخلاص البنود أو الالتزامات ذات الصلة من النصوص القانونية الطويلة بسرعة
- **توثيق الكود**: توليد نظرات عامة موجزة عن المستودعات وشروحات للدوال
## الخطوات التالية

- **الضبط الدقيق (Fine-tuning)**: كيّف النماذج لتناسب مجالك أو مصطلحاتك الخاصة لتحقيق دقة أفضل (راجع Fine-tuning Playbooks)
- **أنظمة RAG**: اجمع بين نماذج اللغة الكبيرة واسترجاع المستندات للحصول على إجابات وبحث واعيين بالسياق
- **استكشاف النماذج**: جرّب نماذج جديدة مثل Llama 3 وPhi-3 أو Qwen للحصول على نتائج أفضل
- **النشر الإنتاجي**: استخدم أدوات مثل vLLM لتقديم خدمة نماذج اللغة الكبيرة بشكل قابل للتوسّع في المؤسسات

يمنحك نظامك القدرة على تشغيل نماذج لغة متطورة محليًا. جرّب نماذج ومطالبات (prompts) ومعايير مختلفة لاكتشاف ما يناسب تطبيقاتك بشكل أفضل.