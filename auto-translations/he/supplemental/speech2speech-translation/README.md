<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## סקירה כללית

תוכנת AMD ROCm™ וערימת PyTorch יוצרות מערכת אקולוגית מאוחדת עבור בינה מלאכותית על המכשיר. היא פועלת הן ב-Windows והן ב-Linux עם תמיכה רשמית במגוון רחב של מכשירים, כולל APU‏ Ryzen™ AI וכרטיסי מסך Radeon™.

מדריך זה ילמד אתכם כיצד להריץ תרגום דיבור-לדיבור באיכות גבוהה, בעל השהיה נמוכה ופרטי לחלוטין, לגמרי בקצה הרשת (edge).

## מה תלמדו

- כיצד להגדיר סביבת עבודה לתרגום דיבור-לדיבור
- כיצד לכתוב קוד Python לטעינה ולשימוש במודלים לתרגום דיבור-לדיבור
- כיצד להריץ ולהתנסות בממשק המשתמש Gradio

## מדוע להשתמש בתרגום דיבור-לדיבור בזמן אמת?

- מסיר חיכוך בין תרגום למחסומי שפה
- מעביר טון, רגש וכוונה ללא הפסקות מביכות
- מאפשר שיתוף פעולה גלובלי וקבלת החלטות מהירה יותר

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדקו אם קיימים עדכוני תוכנה
> **הערה**: אם VS Code אינו מותקן, ניתן להתקין אותו באמצעות Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות מוקדמות של התוכנה

### יצירת סביבה וירטואלית

<!-- @os:linux -->
<!-- @device:halo_box -->
ב-Linux, פתחו מסוף (terminal) והריצו את הפקודה הבאה כדי ליצור venv עם ROCm+Pytorch מותקנים מראש:

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
**הענקת גישה למשתמש שלכם להתקני GPU** (התנתקו והתחברו מחדש כדי שהשינוי ייכנס לתוקף):

```bash
sudo usermod -aG render,video $LOGNAME
```

ב-Linux, פתחו מסוף (terminal) והריצו את הפקודה הבאה כדי ליצור venv:

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
ב-Windows, פתחו מסוף בתיקייה לבחירתכם ובצעו את הפקודות הבאות כדי ליצור venv עם ROCm+Pytorch מותקנים מראש:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **טיפ**: ייתכן שמשתמשי Windows יצטרכו לשנות את מדיניות ההרשאות (Execution Policy) של PowerShell (למשל,
> להגדיר אותה כ-RemoteSigned או Unrestricted) לפני הרצת פקודות מסוימות ב-PowerShell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
ב-Windows, פתחו מסוף בתיקייה לבחירתכם ובצעו את הפקודות הבאות כדי ליצור venv:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **טיפ**: ייתכן שמשתמשי Windows יצטרכו לשנות את מדיניות ההרשאות (Execution Policy) של PowerShell (למשל,
> להגדיר אותה כ-RemoteSigned או Unrestricted) לפני הרצת פקודות מסוימות ב-PowerShell.

<!-- @device:end -->
<!-- @os:end -->

### התקנת תלויות בסיסיות

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:pytorch -->

### תלויות נוספות

התקינו את תלויות m4t באמצעות pip:
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


## הגדרת הדגמת תרגום דיבור-לדיבור

#### מידע על seamless-m4t-v2

עיינו ב[כרטיס המודל](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main) ב-Hugging Face למידע נוסף.
זוהי הארכיטקטורה הטכנית של מודלי הדיבור-לדיבור:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>

#### הורדת סקריפטים

מדריך זה כולל סקריפטים מוכנים לשימוש. אנא הורידו את כולם לאותה תיקייה שבה נמצאת הסביבה שיצרתם.

| סקריפט | תיאור | שימוש |
|--------|-------------|-------|
| [infer.py](assets/infer.py) | יצירת טקסט בסיסית באמצעות LLM | `python infer.py` |
| [input1.wav](assets/input1.wav) | קובץ אודיו לדוגמה | לא רלוונטי |
| [lang_list.py](assets/lang_list.py) | קובץ תמיכת שפות | לא רלוונטי |
| [gradio_demo.py](assets/gradio_demo.py) | ממשק משתמש אינטואיטיבי לתרגום דיבור | `python gradio_demo.py --no-share` |


### התחלה עם infer.py

כדי להריץ את הסקריפט, הריצו 
```bash
python infer.py
```
> **הערה**: ייתכן שתראו כמה אזהרות. זה צפוי.
 
  
#### הסבר על הקוד
**קטע 1: ייבוא התלויות הדרושות**

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

**קטע 2: טעינת המודלים מ-HuggingFace**

פונקציה זו מקבלת מזהה מודל ומורידה את המודל אם הוא עדיין לא הורד. לאחר מכן היא מחזירה את המעבד (processor) ואת המודל לשימוש הפונקציה הבאה.
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

**קטע 3: קליטת קובץ קול קלט .wav ועיבודו המקדים**

פונקציה זו טוענת את קובץ הקול ומדגמת אותו מחדש (resample) לקצב היעד.
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

**קטע 4: הרצת ההסקה (inference)**

פונקציה זו מריצה הסקה עם המודל ומחזירה את הפלט שנוצר.
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

**קטע 5: שמירת הקובץ המתורגם**

פונקציה זו שומרת את מערך האודיו לקובץ WAV.
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

### הרצת ממשק המשתמש Gradio:

לאחר שהרצתם דוגמת סקריפט בסיסית, ההוראות הבאות מספקות ממשק משתמש שימושי הבנוי על הקוד שכתבנו והופך את תרגום הדיבור-לדיבור בזמן אמת לקל יותר.

#### הרצת Gradio מקומית

```bash
python ./gradio_demo.py --no-share
```
לאחר מכן, פתחו את דפדפן האינטרנט שלכם בכתובת `http://127.0.0.1:7860` כדי לגשת לממשק המשתמש.


### דוגמת ממשק המשתמש Gradio:

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


## הצעדים הבאים

- שלבו וערבבו בין עשרות שפות לתרגום מהיר.
- שתפו את ההדגמה שלכם עם אחרים: הוסיפו --share כדי ליצור קישור ציבורי שכל אחד יכול לגשת אליו מרחוק, או פרסו באופן קבוע באמצעות Hugging Face Spaces

## משאבים

להלן כמה משאבים נוספים כדי ללמוד עוד על תרגום דיבור-לדיבור:
* המאגר נמצא כאן https://huggingface.co/facebook/seamless-m4t-v2-large
* מחקר אקדמי הקשור ל-"Seamless: Multilingual Expressive and Streaming Speech Translation"
* שיתוף ופריסה של Gradio: [מדריך שיתוף האפליקציה שלכם](https://www.gradio.app/guides/sharing-your-app) ו[פריסה ל-Hugging Face Spaces](https://shafiqulai.github.io/blogs/blog_5.html)