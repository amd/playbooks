<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## סקירה כללית

מדריך זה מראה כיצד לכוון במדויק (fine-tune) מודל שפה באופן מקומי בעזרת Unsloth על חומרת AMD.

המדריך משתמש בדוגמת Supervised Fine-Tuning (SFT) קצרה עם מתאמי LoRA על `unsloth/gemma-4-E4B-it`, תוך שימוש בתת-קבוצה של מערך הנתונים `mlabonne/FineTome-100k`. המטרה היא להעניק לכם תהליך עבודה פשוט מקצה לקצה הכולל הגדרה, אימון, הסקה (inference) ושמירה של התוצאה המכוונת.

הדוגמה תוכננה להיות מעשית וקלה לשינוי, כך שתוכלו להשתמש בה כנקודת התחלה עבור מערכי הנתונים והמודלים שלכם.

## מה תלמדו

- כיצד להגדיר את סביבת Unsloth
- כיצד לכוון במדויק LLM באמצעות SFT עם Unsloth
- כיצד לשמור את התוצאה המכוונת באחסון מקומי

<!-- @device:halo,stx,krk -->
> **הערה:** טכניקות הכוונון המדויק במדריך זה דורשות לפחות **64 GB של זיכרון מערכת (RAM)**, מתוכם לפחות **24 GB זמינים ל-GPU** (ה-24 GB הם חלק מ-64 GB, ולא בנוסף להם).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **הערה:** טכניקות הכוונון המדויק במדריך זה דורשות לפחות **24 GB של זיכרון GPU כולל** וכן **32 GB של זיכרון מערכת (RAM)**.
> - ב-Windows, זיכרון ה-GPU הכולל משלב את ה-VRAM הייעודי של כרטיס המסך עם זיכרון GPU משותף (הנשאל מזיכרון המערכת).
> - לכן, כרטיסים עם פחות מ-24 GB של VRAM ייעודי עדיין יכולים להריץ מדריך זה באמצעות שימוש בזיכרון GPU משותף כדי להשלים את ההפרש.
<!-- @os:end -->

<!-- @os:linux -->
> **הערה:** טכניקות הכוונון המדויק במדריך זה דורשות כרטיס מסך עם לפחות **24 GB של זיכרון GPU ייעודי** וכן **32 GB של זיכרון מערכת (RAM)**.
> - ב-Linux, האימון פועל כולו בתוך ה-VRAM הייעודי של כרטיס המסך.
> - הוא אינו חוזר לשימוש בזיכרון GPU משותף (זיכרון המערכת) כאשר ה-VRAM אוזל.
> - כרטיסים עם פחות מ-24 GB של VRAM ייעודי ייתקלו בחוסר זיכרון במהלך האימון ב-Linux, גם אם במערכת יש שפע של RAM.
<!-- @os:end -->
<!-- @device:end -->

## מדוע Unsloth?

Unsloth הופכת את הכוונון המדויק של LLM לקל יותר להרצה על חומרה מקומית, על ידי הפחתת צריכת הזיכרון והאצת האימון בהשוואה להגדרה סטנדרטית.

במדריך זה, אנו משתמשים ב-Unsloth יחד עם **SFT מבוסס LoRA**. המשמעות היא שהמודל הבסיסי נשאר קפוא ברובו, בעוד שקבוצה קטנה בהרבה של משקלי מתאם (adapter) מאומנת. זוהי התאמה טובה לפיתוח מקומי מכיוון שהיא קלה יותר מכוונון מדויק מלא ומהירה יותר לביצוע איטרציות.

Unsloth תומכת גם בגישות אימון נוספות, כולל QLoRA ותהליכי עבודה של למידת חיזוק (reinforcement learning). מדריך זה מתמקד תחילה בנתיב הפשוט ביותר: דוגמת כוונון מדויק קטנה בעזרת LoRA שמשתמשים יכולים להריץ, להבין ולהרחיב.

<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה
> **הערה**: אם VS Code אינו מותקן, ניתן להתקינו באמצעות Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות מוקדמות של תוכנה

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### יצירת סביבה וירטואלית

<!-- @os:linux -->
<!-- @device:halo_box -->
פתחו מסוף וצרו venv עם תוכנת AMD ROCm™ ו-PyTorch מותקנים מראש:
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**הענקת גישה למשתמש שלכם להתקני GPU** (יש להתנתק ולהתחבר מחדש כדי שהשינוי ייכנס לתוקף):

```bash
sudo usermod -aG render,video $LOGNAME
```

פתחו מסוף וצרו venv:
<!-- @test:id=create-venv timeout=300 -->
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
> **הערה:** נדרשת גרסת Python 3.13 עבור Windows.

<!-- @device:halo_box -->
פתחו מסוף PowerShell וצרו סביבה וירטואלית:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
פתחו מסוף PowerShell וצרו סביבה וירטואלית:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### התקנת תלויות בסיסיות
<!-- @require:driver -->

> **חשוב:** Unsloth עדיין אינה תומכת בגרסת PyTorch 2.13 המגיעה יחד עם ROCm 10. עבור מדריך זה, התקינו **ROCm 7.14 עם PyTorch 2.12** באמצעות הפקודות שלהלן. אין להשתמש בחבילות ROCm 10 / PyTorch 2.13.

**התקינו את PyTorch עם תמיכת תוכנת AMD ROCm™** בסביבה הווירטואלית שנוצרה:

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1151]==2.12.0+rocm7.14.0" "torchvision[device-gfx1151]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1150]==2.12.0+rocm7.14.0" "torchvision[device-gfx1150]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1152]==2.12.0+rocm7.14.0" "torchvision[device-gfx1152]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.0" "torchvision[device-gfx1100]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1201]==2.12.0+rocm7.14.0" "torchvision[device-gfx1201]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

עבור התקנים אחרים, עיינו ב-[תיעוד ROCm 7.14](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) להוראות מלאות.

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

### תלויות נוספות

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **הערה:** במהלך הייבוא, ייתכן ש-Unsloth תבדוק נתיבי האצה אופציונליים של `bitsandbytes`. בחלק מגרסאות ROCm, ייתכן שתראו הודעה כגון `bitsandbytes library load error: Configured ROCm binary not found`. מדריך זה משתמש בכוונון מדויק סטנדרטי של LoRA עם `optim="adamw_torch"`, ולכן איננו תלויים באופטימייזר `bitsandbytes` או ב-QLoRA ברזולוציית 4-bit. ניתן להתעלם בבטחה מהודעה זו.

<!-- @os:windows -->
> **הערה:** ב-Windows ROCm, Unsloth תדפיס מספר אזהרות בעת ההפעלה — ראו [אזהרות ידועות](#known-warnings) להלן. כולן בטוחות להתעלמות; האימון פועל כראוי.
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

## הורדת סקריפט הכוונון המדויק של Unsloth

במקום להריץ ידנית כל שלב, מדריך זה מספק סקריפט נקי מקצה לקצה כאן: [test_unsloth.py](assets/test_unsloth.py).

הריצו את הקוד הבא כדי להפעיל את הסקריפט:

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

שאר המדריך יעבור באופן עקרוני על כל שלב מרכזי בסקריפט.

## כיצד זה פועל

סקריפט test_unsloth.py מבצע את השלבים הבאים:
* **טעינת מודל**: טוען את unsloth/gemma-4-E4B-it באמצעות FastModel.
* **הכנת נתונים**: מתקנן (standardizes) את מערך הנתונים (למשל, FineTome-100k) ומחיל את תבנית הצ'אט של Gemma-4.
* **החלת LoRA**: מוסיף מתאמים (adapters) למודולי שפה, קשב (attention) ו-MLP לצורך אימון יעיל.
* **אימון**: משתמש ב-SFTTrainer עם מיסוך הפסד (loss masking) המוגבל לתגובות בלבד.
* **הסקה (Inference)**: מריץ בדיקת ייצור מהירה לאימות ביצועים.
* **שמירה**: מייצא את מתאמי LoRA באופן מקומי.
## תצורת מפתח

ניתן לשנות את הקבועים הבאים כדי להתאים אישית את ההרצה:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

דוגמה להודעת הפתיחה של Unsloth ולפלט בעת טעינת משקלי המודל:

![alt text](assets/welcome.png)

## הכנת מערך הנתונים

אנו משתמשים בתת-קבוצה של:
```text
mlabonne/FineTome-100k
```
מערך הנתונים:
* הומר לפורמט צ'אט
* עובד באמצעות תבנית הצ'אט Gemma-4
* נוקה מטוקני BOS כפולים

## אימון המודל

הסקריפט מריץ הדגמת אימון קצרה, עם הפרמטרים הבאים:
- כ-50 צעדים
- גודל אצווה קטן
- צבירת גרדיאנטים

במהלך האימון, תראו יומנים כגון:

![alt text](assets/training.png)


## שמירה ופריסה

### שמירה מקומית (LoRA)

הסקריפט שומר אוטומטית את מתאמי LoRA ל-OUTPUT_DIR.
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

### שמירת מודל ממוזג (עבור vLLM) 

<!-- @os:windows -->
> **הערה:** vLLM אינו תומך ב-Windows. כדי לפרוס את המודל המכוונן שלכם ב-Windows, השתמשו ב-llama.cpp (ראו [ייצוא GGUF](#export-gguf-for-llamacpp) למטה) או העבירו את המודל הממוזג למחשב Linux המריץ vLLM.
<!-- @os:end -->

<!-- @os:linux -->
לפריסה עם vLLM, מזגו את המתאמים למודל מלא:
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

### ייצוא GGUF (עבור llama.cpp)

המירו ישירות ל-GGUF עבור הסקה מקומית:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## אזהרות ידועות

אזהרות אלה מודפסות על ידי Unsloth בעת ההפעלה ב-Windows ROCm וכולן בטוחות להתעלמות:

| אזהרה | סיבה | בטוח להתעלם? |
|---|---|---|
| `bitsandbytes library load error` | ל-bitsandbytes אין בנייה עבור Windows ROCm | כן — ספר ההדרכה הזה משתמש ב-`adamw_torch`, לא ב-bnb |
| `No ROCm platform found for torch.distributed` | ל-ROCm על Windows אין תמיכה באימון מבוזר | כן — אימון עם GPU יחיד אינו מושפע |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth מסמן בניות שאינן Linux | כן — Windows ROCm עובד עבור SFT עם GPU יחיד |
| `triton is not available` | ל-Triton אין בנייה עבור Windows | כן — Unsloth חוזר לליבות PyTorch |

האימון יתקדם כראוי למרות אזהרות אלה.
<!-- @os:end -->

## השלבים הבאים
- נסו את [Unsloth Studio](https://unsloth.ai/docs/new/studio), ממשק משתמש גרפי אינטואיטיבי עבור Unsloth
- אמנו על מערכי הנתונים הספציפיים שלכם
- נסו כוונון עדין עם היפר-פרמטרים שונים
- פרסו עם vLLM או llama.cpp
- נסו QLoRA להגדרה חסכונית יותר בזיכרון

## משאבים

להלן כמה משאבים נוספים כדי ללמוד עוד על Unsloth וכוונון עדין:

* [תיעוד Unsloth](https://docs.unsloth.ai)

* [GitHub של Unsloth](https://github.com/unslothai/unsloth)

* [מדריך כוונון עדין של Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)