<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## סקירה כללית

מדריך זה מראה כיצד לכוונן דק (fine-tune) מודל שפה באופן מקומי עם Unsloth על חומרת AMD.

הוא משתמש בדוגמה קצרה של כוונון דק מפוקח (SFT) עם מתאמי LoRA על `unsloth/gemma-4-E4B-it`, תוך שימוש בתת-קבוצה של מערך הנתונים `mlabonne/FineTome-100k`. המטרה היא לספק לך תהליך עבודה פשוט מקצה לקצה המכסה הגדרה, אימון, הסקה ושמירת התוצאה המכוונת.

הדוגמה מתוכננת להיות מעשית וקלה לשינוי, כך שתוכל להשתמש בה כנקודת התחלה עבור מערכי הנתונים והמודלים שלך.

## מה תלמד

- כיצד להגדיר את סביבת Unsloth
- כיצד לכוונן דק מודל LLM באמצעות SFT עם Unsloth
- כיצד לשמור את התוצאה המכוונת באחסון מקומי

<!-- @device:halo,stx,krk -->
> **הערה:** טכניקות הכוונון הדק במדריך זה דורשות לפחות 24 GB של זיכרון GPU ו-32 GB של זיכרון RAM במערכת.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **הערה:** טכניקות הכוונון הדק במדריך זה דורשות לפחות 24 GB של זיכרון GPU ו-32 GB של זיכרון RAM במערכת.
<!-- @os:end -->

<!-- @os:linux -->
> **הערה:** טכניקות הכוונון הדק במדריך זה דורשות לפחות 24 GB של זיכרון GPU **ייעודי** ו-32 GB של זיכרון RAM במערכת.
<!-- @os:end -->
<!-- @device:end -->

## מדוע Unsloth?

Unsloth מקל על הפעלת כוונון דק של מודלי LLM על חומרה מקומית על ידי הפחתת השימוש בזיכרון והאצת האימון בהשוואה להגדרה רגילה.

במדריך זה, אנו משתמשים ב-Unsloth יחד עם **SFT מבוסס LoRA**. המשמעות היא שהמודל הבסיסי נשאר קפוא ברובו, בעוד שמאומן קבוצה קטנה בהרבה של משקלי מתאם. זהו פתרון מתאים לפיתוח מקומי מכיוון שהוא קל יותר מכוונון דק מלא ומהיר יותר לאיטרציה.

Unsloth תומך גם בגישות אימון אחרות, כולל QLoRA ותהליכי עבודה של למידה מחיזוקים. מדריך זה מתמקד בנתיב הפשוט ביותר תחילה: דוגמה קטנה של כוונון דק עם LoRA שמשתמשים יכולים להריץ, להבין ולהרחיב.

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה
> **הערה**: אם VS Code אינו מותקן, ניתן להתקין אותו עם Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

### יצירת סביבה וירטואלית

<!-- @os:linux -->
<!-- @device:halo_box -->
פתח מסוף וצור venv עם תוכנת AMD ROCm™ ו-PyTorch מותקנים מראש:
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
**הענק למשתמש שלך גישה להתקני GPU** (התנתק והתחבר מחדש כדי שהשינוי ייכנס לתוקף):

```bash
sudo usermod -aG render,video $LOGNAME
```

פתח מסוף וצור venv:
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
> **הערה:** נדרש Python 3.13 עבור Windows.

<!-- @device:halo_box -->
פתח מסוף PowerShell וצור סביבה וירטואלית:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
פתח מסוף PowerShell וצור סביבה וירטואלית:
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

### תלויות נוספות

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

> **הערה:** במהלך הייבוא, Unsloth עשוי לבדוק נתיבי האצה אופציונליים של `bitsandbytes`. בגרסאות ROCm מסוימות, ייתכן שתראה הודעה כגון `bitsandbytes library load error: Configured ROCm binary not found`. מדריך זה משתמש בכוונון דק רגיל עם LoRA עם `optim="adamw_torch"`, ולכן אנו לא מסתמכים על האופטימייזר של `bitsandbytes` או על QLoRA בדגימה של 4-ביט. ניתן להתעלם בבטחה מהודעה זו.

<!-- @os:windows -->
> **הערה:** ב-Windows ROCm, Unsloth ידפיס מספר אזהרות בעת ההפעלה — ראה [אזהרות ידועות](#known-warnings) להלן. כל אלה בטוחות להתעלמות; האימון פועל כראוי.
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

## הורדת סקריפט הכוונון הדק של Unsloth

במקום לבצע כל שלב באופן ידני, מדריך זה מספק סקריפט נקי מקצה לקצה כאן: [test_unsloth.py](assets/test_unsloth.py).

הרץ את הקוד הבא כדי להפעיל את הסקריפט:

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

שאר המדריך יעבור באופן רעיוני על כל שלב מרכזי של הסקריפט.

## כיצד זה עובד

סקריפט test_unsloth.py מבצע את השלבים הבאים:
* **טעינת מודל**: טוען את unsloth/gemma-4-E4B-it באמצעות FastModel.
* **הכנת נתונים**: מתקנן את מערך הנתונים (למשל, FineTome-100k) ומיישם את תבנית הצ'אט של Gemma-4.
* **יישום LoRA**: מוסיף מתאמים למודולי שפה, תשומת לב ו-MLP לאימון יעיל.
* **אימון**: משתמש ב-SFTTrainer עם מיסוך הפסד על תגובות בלבד.
* **הסקה**: מריץ בדיקת יצירה מהירה לאימות הביצועים.
* **שמירה**: מייצא מתאמי LoRA באופן מקומי.

## תצורת מפתח

ניתן לשנות את הקבועים הבאים כדי להתאים אישית את הריצה שלך:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

דוגמה להודעת הברוכים הבאים של Unsloth ופלט בעת טעינת משקלי המודל:

![טקסט חלופי](assets/welcome.png)

## הכנת מערך הנתונים

אנו משתמשים בתת-קבוצה של:
```text
mlabonne/FineTome-100k
```
מערך הנתונים:
* מומר לפורמט צ'אט
* מעובד באמצעות תבנית הצ'אט של Gemma-4
* מנוקה להסרת אסימוני BOS כפולים

## אימון המודל

הסקריפט מריץ הדגמת אימון קצרה, עם הפרמטרים הבאים:
- ~50 צעדים
- גודל אצווה קטן
- צבירת גרדיאנטים

במהלך האימון, תראה יומנים כגון:

![טקסט חלופי](assets/training.png)


## שמירה ופריסה

### שמירה מקומית (LoRA)

הסקריפט שומר אוטומטית מתאמי LoRA ל-OUTPUT_DIR.
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
> **הערה:** vLLM אינו תומך ב-Windows. כדי לפרוס את המודל המכוונן שלך ב-Windows, השתמש ב-llama.cpp (ראה [ייצוא GGUF](#export-gguf-for-llamacpp) להלן) או העבר את המודל הממוזג למכונת Linux המריצה vLLM.
<!-- @os:end -->

<!-- @os:linux -->
לפריסה עם vLLM, מזג את המתאמים למודל מלא:
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

המר ישירות ל-GGUF להסקה מקומית:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## אזהרות ידועות

אזהרות אלה מודפסות על ידי Unsloth בעת ההפעלה ב-Windows ROCm וכולן בטוחות להתעלמות:

| אזהרה | סיבה | בטוח להתעלמות? |
|---|---|---|
| `bitsandbytes library load error` | ל-bitsandbytes אין גרסת בנייה עבור Windows ROCm | כן — מדריך זה משתמש ב-`adamw_torch`, לא ב-bnb |
| `No ROCm platform found for torch.distributed` | ל-ROCm-on-Windows חסר אימון מבוזר | כן — אימון על GPU יחיד אינו מושפע |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth מסמן גרסאות בנייה שאינן Linux | כן — Windows ROCm עובד עבור SFT על GPU יחיד |
| `triton is not available` | ל-Triton אין גרסת בנייה עבור Windows | כן — Unsloth חוזר לגרעיני PyTorch |

האימון יתקדם כראוי למרות אזהרות אלה.
<!-- @os:end -->

## השלבים הבאים
- נסה את [Unsloth Studio](https://unsloth.ai/docs/new/studio), ממשק GUI אינטואיטיבי עבור Unsloth
- אמן על מערכי הנתונים הספציפיים שלך
- נסה כוונון דק עם היפר-פרמטרים שונים
- פרוס עם vLLM או llama.cpp
- נסה QLoRA להגדרה עם זיכרון נמוך יותר

## משאבים

להלן מספר משאבים נוספים ללמידה נוספת על Unsloth וכוונון דק:

* [תיעוד Unsloth](https://docs.unsloth.ai)

* [Unsloth ב-GitHub](https://github.com/unslothai/unsloth)

* [מדריך כוונון דק של Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)