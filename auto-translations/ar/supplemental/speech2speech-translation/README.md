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

يُنشئ برنامج AMD ROCm™ وحزمة PyTorch نظامًا بيئيًا موحدًا للذكاء الاصطناعي على الجهاز. يعمل على كل من Windows وLinux مع دعم رسمي لمجموعة واسعة من الأجهزة، بما في ذلك وحدات المعالجة Ryzen™ AI APUs ووحدات معالجة الرسومات Radeon™.

سيعلّمك هذا الدليل التوجيهي كيفية تشغيل ترجمة كلام إلى كلام منخفضة الكمون، ومعبّرة، وخاصة بالكامل على الطرف (edge).

## ما ستتعلمه

- كيفية إعداد بيئة الكلام إلى الكلام
- كيفية كتابة كود Python لتحميل واستخدام نماذج الكلام إلى الكلام
- كيفية تشغيل واختبار واجهة Gradio

## لماذا تستخدم ترجمة الكلام إلى كلام في الوقت الفعلي؟

- تزيل الاحتكاك بين الترجمة وحواجز اللغة
- تنقل النبرة والعاطفة والنية دون توقفات مربكة
- تُمكّن من التعاون العالمي واتخاذ قرارات أسرع

## إعداد تهيئة الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرنامج
> **ملاحظة**: إذا لم يكن VS Code مثبتًا، يمكنك تثبيته باستخدام Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرنامج الأساسية

### إنشاء بيئة افتراضية

<!-- @os:linux -->
<!-- @device:halo_box -->
على Linux، افتح طرفية (terminal) ونفّذ الأمر التالي لإنشاء بيئة افتراضية (venv) مع تثبيت ROCm+Pytorch مسبقًا:

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env --system-site-packages
source s2st-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source s2st-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**امنح مستخدمك صلاحية الوصول إلى أجهزة GPU** (يجب تسجيل الخروج ثم الدخول مرة أخرى ليصبح هذا فعالًا):

```bash
sudo usermod -aG render,video $LOGNAME
```

على Linux، افتح طرفية (terminal) ونفّذ الأمر التالي لإنشاء بيئة افتراضية (venv):

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env
source s2st-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source s2st-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
على Windows، افتح طرفية في الدليل الذي تختاره واتبع الأوامر التالية لإنشاء بيئة افتراضية (venv) مع تثبيت ROCm+Pytorch مسبقًا:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **نصيحة**: قد يحتاج مستخدمو Windows إلى تعديل سياسة تنفيذ PowerShell الخاصة بهم (مثل ضبطها على RemoteSigned أو Unrestricted) قبل تشغيل بعض أوامر PowerShell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
على Windows، افتح طرفية في الدليل الذي تختاره واتبع الأوامر التالية لإنشاء بيئة افتراضية (venv):

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **نصيحة**: قد يحتاج مستخدمو Windows إلى تعديل سياسة تنفيذ PowerShell الخاصة بهم (مثل ضبطها على RemoteSigned أو Unrestricted) قبل تشغيل بعض أوامر PowerShell.

<!-- @device:end -->
<!-- @os:end -->

### تثبيت التبعيات الأساسية

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:pytorch -->

### تبعيات إضافية

قم بتثبيت تبعيات m4t باستخدام pip:
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 tiktoken==0.9.0 accelerate soundfile==0.13.1 sentencepiece protobuf gradio scipy==1.15.3 
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=300 setup=activate-venv hidden=True -->
```python
import importlib
import os
import sys

# Ensure local assets directory is importable
sys.path.insert(0, os.getcwd())

modules = [
    "torch",
    "torchaudio",
    "scipy",
    "soundfile",
    "gradio",
    "transformers",
    "safetensors",
    "sentencepiece",
    "accelerate",
    "tiktoken",
]

for module in modules:
    importlib.import_module(module)
    print(f"PASS: imported {module}")

from transformers import AutoProcessor, SeamlessM4Tv2Model
import lang_list
from lang_list import LANGUAGE_NAME_TO_CODE, ASR_TARGET_LANGUAGE_NAMES, S2ST_TARGET_LANGUAGE_NAMES

assert "English" in LANGUAGE_NAME_TO_CODE, "FAIL: English missing in LANGUAGE_NAME_TO_CODE"
assert len(S2ST_TARGET_LANGUAGE_NAMES) > 0, "FAIL: S2ST_TARGET_LANGUAGE_NAMES is empty"

print("PASS: imported local module lang_list")
print("PASS: key speech2speech imports work")
```
<!-- @test:end -->

<!-- @test:id=verify-scripts timeout=60 hidden=True -->
```python
import ast
import os
import sys

required_files = [
    "infer.py",
    "gradio_demo.py",
    "lang_list.py",
    "input1.wav",
]

missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: All required files exist")

for script in ["infer.py", "gradio_demo.py", "lang_list.py"]:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->


## إعداد عرض الكلام إلى الكلام التوضيحي

#### تعرّف على seamless-m4t-v2

اطّلع على [بطاقة النموذج](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main) على Hugging Face لمزيد من المعلومات.
هذه هي البنية التقنية لنماذج الكلام إلى الكلام:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>

#### تنزيل النصوص البرمجية

يتضمن هذا الدليل التوجيهي نصوصًا برمجية جاهزة للاستخدام. يُرجى تنزيلها جميعًا إلى نفس الدليل الخاص بالبيئة التي أنشأتها.

| النص البرمجي | الوصف | الاستخدام |
|--------|-------------|-------|
| [infer.py](assets/infer.py) | توليد نص أساسي باستخدام LLM | `python infer.py` |
| [input1.wav](assets/input1.wav) | ملف صوتي كمثال | غير متاح |
| [lang_list.py](assets/lang_list.py) | ملف دعم اللغات | غير متاح |
| [gradio_demo.py](assets/gradio_demo.py) | واجهة مستخدم بديهية لترجمة الكلام | `python gradio_demo.py --no-share` |


### البدء مع infer.py

لتنفيذ النص البرمجي، شغّل 
```bash
python infer.py
```
> **ملاحظة**: قد تظهر لك بعض التحذيرات. هذا أمر متوقع.
 
  
#### شرح الكود
**المقتطف 1: استيراد التبعيات اللازمة**

```python 
import os
os.environ["HIP_VISIBLE_DEVICES"] = "0"

import time
import numpy as np
import scipy.io.wavfile
import soundfile as sf
import torch
import torchaudio

from transformers import AutoProcessor, SeamlessM4Tv2Model

# ============ Configuration ============
DEFAULT_TARGET_LANGUAGE = "eng"

INPUT_AUDIO_PATH = "./input1.wav"
OUTPUT_AUDIO_PATH = "./out1.wav"

# Automatically downloads + caches via Hugging Face
MODEL_ID = "facebook/seamless-m4t-v2-large"

TARGET_SAMPLE_RATE = 16_000
```

**المقتطف 2: تحميل النماذج من HuggingFace**

تأخذ هذه الدالة معرّف النموذج وتقوم بتنزيل النموذج إذا لم يكن قد تم تنزيله بالفعل. ثم تُعيد المعالج (processor) والنموذج لاستخدامهما في الدالة التالية.
```python
def load_model(model_id: str, device: torch.device):
    start = time.time()

    print("Loading model (downloads automatically on first run)...")

    processor = AutoProcessor.from_pretrained(model_id)

    dtype = torch.float16 if device.type == "cuda" else torch.float32

    model = SeamlessM4Tv2Model.from_pretrained(model_id, torch_dtype=dtype).to(device)

    elapsed = time.time() - start
    print(f"Model loading duration: {elapsed:.2f} seconds")

    return processor, model
```

**المقتطف 3: إدخال ملف صوتي .wav ومعالجته مسبقًا**

تقوم هذه الدالة بتحميل المقطع الصوتي وإعادة أخذ العينات (resample) بمعدل الهدف.
```python
def preprocess_audio(audio_path: str, target_sr: int = TARGET_SAMPLE_RATE) -> torch.Tensor:

    audio_np, orig_freq = sf.read(audio_path, dtype="float32", always_2d=True)

    # Convert to tensor [channels, samples]
    audio = torch.from_numpy(audio_np.T)

    # Resample if needed
    if orig_freq != target_sr:
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=target_sr)

    # Convert stereo -> mono
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)

    return audio
```

**المقتطف 4: تشغيل الاستدلال**

تقوم هذه الدالة بتشغيل الاستدلال باستخدام النموذج وتُعيد المخرجات المُولّدة.
```python
def run_inference(model, processor, audio: torch.Tensor, device: torch.device, target_lang: str = DEFAULT_TARGET_LANGUAGE):

    start = time.time()

    audio_inputs = processor(
        audio=audio.squeeze(0).cpu().numpy(),
        sampling_rate=TARGET_SAMPLE_RATE,
        return_tensors="pt",
    )

    audio_inputs = {
        k: v.to(device) if isinstance(v, torch.Tensor) else v
        for k, v in audio_inputs.items()
    }

    with torch.inference_mode():
        output = model.generate(**audio_inputs, tgt_lang=target_lang)[0]

    audio_array = output.float().cpu().numpy().squeeze()

    elapsed = time.time() - start
    print(f"Inference duration: {elapsed:.2f} seconds")

    return audio_array, elapsed
```

**المقتطف 5: حفظ الملف المُترجم**

تقوم هذه الدالة بحفظ المصفوفة الصوتية في ملف WAV.
```python
def save_audio(audio_array: np.ndarray, output_path: str, sample_rate: int):
    if np.issubdtype(audio_array.dtype, np.floating):
        max_abs = np.max(np.abs(audio_array)) if audio_array.size else 0.0

        if max_abs > 1.0:
            audio_array = audio_array / max_abs

        audio_array = (audio_array * 32767.0).clip(-32768, 32767).astype(np.int16)

    scipy.io.wavfile.write(output_path, rate=sample_rate, data=audio_array)

    print(f"Output saved to: {output_path}")
```

<!-- @os:windows -->
<!-- @test:id=infer-smoke-windows timeout=1800 setup=activate-venv hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
Remove-Item .\out1.wav -Force -ErrorAction SilentlyContinue

if (-not (Test-Path .\input1.wav)) { throw "FAIL: input1.wav not found in current directory" }

python .\infer.py
if ($LASTEXITCODE -ne 0) { throw "infer.py failed" }

if (-not (Test-Path .\out1.wav)) { throw "FAIL: out1.wav was not created" }
$file = Get-Item .\out1.wav
if ($file.Length -le 0) { throw "FAIL: out1.wav is empty" }

Write-Host "PASS: infer.py created out1.wav successfully"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=infer-smoke-linux timeout=1800 setup=activate-venv hidden=True -->
```bash
set -euo pipefail
rm -f ./out1.wav

if [ ! -f ./input1.wav ]; then
  echo "FAIL: input1.wav not found in current directory"
  exit 1
fi

python ./infer.py

if [ ! -f ./out1.wav ]; then
  echo "FAIL: out1.wav was not created"
  exit 1
fi
if [ ! -s ./out1.wav ]; then
  echo "FAIL: out1.wav is empty"
  exit 1
fi

echo "PASS: infer.py created out1.wav successfully"
```
<!-- @test:end --> 
<!-- @os:end -->

### تشغيل عرض واجهة Gradio التوضيحي:

الآن بعد أن قمت بتشغيل مثال نصي برمجي أساسي، تقدم التعليمات التالية واجهة مستخدم مفيدة تبني على الكود الذي كتبناه وتجعل ترجمة الكلام إلى كلام المباشرة سهلة.

#### تشغيل Gradio محليًا

```bash
python ./gradio_demo.py --no-share
```
ثم افتح متصفح الويب الخاص بك على `http://127.0.0.1:7860` للوصول إلى الواجهة.


### مثال على واجهة Gradio:

<p align="center">
  <img src="assets/gradio.png" alt="gradio UI" width="600"/>
</p>

<!-- @os:windows -->
<!-- @test:id=gradio-ui-smoke-windows timeout=1800 setup=activate-venv hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
import os
import sys
import gradio as gr

# Ensure current directory is importable so lang_list.py can be imported
sys.path.insert(0, os.getcwd())

import gradio_demo

called = {}

def fake_launch(self, *args, **kwargs):
    called["args"] = args
    called["kwargs"] = kwargs
    print(f"PASS: launch called with kwargs={kwargs}")
    return self

orig_launch = gr.Blocks.launch

def fake_runner(input_audio, target_language):
    return None, "OK"

try:
    demo = gradio_demo.build_ui(fake_runner)
    print(f"PASS: build_ui(fake_runner) returned {type(demo).__name__}")

    gr.Blocks.launch = fake_launch
    sys.argv = ["gradio_demo.py", "--no-share"]
    gradio_demo.main()

    kwargs = called.get("kwargs", {})
    assert kwargs.get("server_name") == "127.0.0.1", "FAIL: unexpected server_name"
    assert kwargs.get("server_port") == 7860, "FAIL: unexpected server_port"
    assert kwargs.get("share") is False, "FAIL: expected share=False by default/--no-share"

    print("PASS: gradio_demo main() reached launch() with expected settings")
finally:
    gr.Blocks.launch = orig_launch
'@

$tempPy = Join-Path $env:TEMP "gradio_ui_smoke_ci.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy

if ($LASTEXITCODE -ne 0) {
  Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
  throw "gradio UI smoke test failed"
}

Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=gradio-ui-smoke-linux timeout=1800 setup=activate-venv hidden=True -->
```bash
set -euo pipefail

python - <<'PY'
import os
import sys
import gradio as gr

# Ensure current directory is importable so lang_list.py can be imported
sys.path.insert(0, os.getcwd())

import gradio_demo

called = {}

def fake_launch(self, *args, **kwargs):
    called["args"] = args
    called["kwargs"] = kwargs
    print(f"PASS: launch called with kwargs={kwargs}")
    return self

orig_launch = gr.Blocks.launch

def fake_runner(input_audio, target_language):
    return None, "OK"

try:
    demo = gradio_demo.build_ui(fake_runner)
    print(f"PASS: build_ui(fake_runner) returned {type(demo).__name__}")

    gr.Blocks.launch = fake_launch
    sys.argv = ["gradio_demo.py", "--no-share"]
    gradio_demo.main()

    kwargs = called.get("kwargs", {})
    assert kwargs.get("server_name") == "127.0.0.1", "FAIL: unexpected server_name"
    assert kwargs.get("server_port") == 7860, "FAIL: unexpected server_port"
    assert kwargs.get("share") is False, "FAIL: expected share=False by default/--no-share"

    print("PASS: gradio_demo main() reached launch() with expected settings")
finally:
    gr.Blocks.launch = orig_launch
PY
```
<!-- @test:end --> 
<!-- @os:end -->


## الخطوات التالية

- امزج وطابق بين عشرات اللغات للترجمة السريعة.
- شارك عرضك التوضيحي مع الآخرين: أضف --share لإنشاء رابط عام يمكن لأي شخص الوصول إليه عن بُعد، أو انشره بشكل دائم باستخدام Hugging Face Spaces

## الموارد

فيما يلي بعض الموارد الإضافية لمعرفة المزيد حول ترجمة الكلام إلى كلام:
* المستودع موجود هنا https://huggingface.co/facebook/seamless-m4t-v2-large
* الأبحاث الأكاديمية المتعلقة بـ "Seamless: Multilingual Expressive and Streaming Speech Translation"
* مشاركة Gradio ونشرها: [دليل مشاركة تطبيقك](https://www.gradio.app/guides/sharing-your-app) و[النشر على Hugging Face Spaces](https://shafiqulai.github.io/blogs/blog_5.html)