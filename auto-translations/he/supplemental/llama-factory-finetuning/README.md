## סקירה כללית

כוונון עדין יעיל הוא חיוני להתאמת מודלים שפתיים גדולים (LLMs) למשימות במורד הזרם. LLaMA-Factory היא פלטפורמה קוד-פתוח ידידותית למשתמש המייעלת את האימון והכוונון העדין של מודלים שפתיים גדולים ומודלים מולטי-מודאליים. היא מאפשרת למשתמשים להתאים מאות מודלים מאומנים מראש באופן מקומי עם מינימום קוד.

מדריך זה מלמד אתכם כיצד לכוונן LLMs באמצעות LLaMA-Factory על חומרת AMD המקומית שלכם.

<!-- @device:stx,krk -->
> **הערה:** טכניקות הכוונון העדין במדריך זה דורשות לפחות **32 GB של זיכרון RAM במערכת**, כאשר לפחות **16 GB ממנו זמינים ל-GPU** (16 ה-GB הם חלק מ-32 ה-GB, לא בנוסף אליהם).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **הערה:** טכניקות הכוונון העדין במדריך זה דורשות לפחות **16 GB של זיכרון GPU כולל** ו-**32 GB של זיכרון RAM במערכת**.
> - ב-Windows, זיכרון ה-GPU הכולל משלב את ה-VRAM הייעודי של כרטיס המסך עם זיכרון GPU משותף (שאול מ-RAM של המערכת).
> - לכן, כרטיסים עם פחות מ-16 GB של VRAM ייעודי עדיין יכולים להריץ מדריך זה על ידי שימוש בזיכרון GPU משותף כדי לכסות את ההפרש.
<!-- @os:end -->

<!-- @os:linux -->
> **הערה:** טכניקות הכוונון העדין במדריך זה דורשות כרטיס מסך עם לפחות **16 GB של זיכרון GPU ייעודי** ו-**32 GB של זיכרון RAM במערכת**.
> - ב-Linux, האימון מתבצע כולו ב-VRAM הייעודי של כרטיס המסך.
> - הוא אינו חוזר לזיכרון GPU משותף (RAM של המערכת) כאשר ה-VRAM אוזל.
> - כרטיסים עם פחות מ-16 GB של VRAM ייעודי יאזלו מזיכרון במהלך האימון ב-Linux, גם אם למערכת יש הרבה RAM.
<!-- @os:end -->
<!-- @device:end -->

## מה תלמדו

- כיצד להגדיר את LLaMA-Factory עם תוכנת AMD ROCm™
- כיצד להגדיר פרמטרי כוונון עדין של LLM (תוך שימוש ב-Qwen/Qwen3-4B-Instruct-2507 כדוגמה)
- כיצד להריץ כוונון עדין של LLaMA-Factory
- כיצד להריץ הסקה עם המודל המכוונן
- כיצד לייצא את המודל המכוונן

## זמן משוער

- משך: ביצוע מדריך זה ייקח כ-60 דקות (בהתאם לגודל המודל/מערך הנתונים ומהירות הרשת).
- עיינו ב-[LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) לקבלת מידע נוסף.

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

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

#### יצירת סביבה וירטואלית

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
**הענקת גישת המשתמש שלכם להתקני GPU** (התנתקו והתחברו מחדש כדי שזה ייכנס לתוקף):

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

### התקנת תלויות בסיסיות

<!-- @require:pytorch,driver -->
 
### התקנת תלויות נוספות

> **הערה**: ודאו שגרסת Python היא 3.11, 3.12, או 3.13

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

### התקנת LLaMA-Factory

LLaMA-Factory תלויה ב-PyTorch. כבר אמורה להיות לכם גרסה מותקנת בהתאם לדרישות לעיל.

הורידו את קוד המקור מ-[מאגר GitHub הרשמי של LLaMA Factory](https://github.com/hiyouga/LlamaFactory), והתקינו את התלויות שלו.

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

ודאו ש-`llamafactory-cli` ניתן להרצה.

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

פלט לדוגמה:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

לאחר התקנה מוצלחת של LLaMA-Factory, בואו נריץ עליו כוונון עדין.

## שימוש ב-LLaMA Factory CLI לכוונון עדין

סעיף זה יכסה כיצד להכין מערכי נתונים לכוונון עדין, להגדיר פרמטרי LoRA/QLoRA, ולהריץ כוונון עדין של LoRA.

### הכנת מערך נתונים

LLaMA-Factory תומכת במערכי נתונים לכוונון עדין בפורמט Alpaca ובפורמט ShareGPT. כל מערכי הנתונים הזמינים הוגדרו ב-[dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). אם אתם משתמשים במערך נתונים מותאם אישית, אנא ודאו להוסיף תיאור מערך נתונים ב-`dataset_info.json` ולציין את שם מערך הנתונים לפני האימון. פרטים נוספים ניתן למצוא בתיעוד שלהם [כאן](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

במדריך זה, נשתמש במערכי הנתונים identity ו-alpaca_en_demo כדוגמה, ונגדיר את מידע מערך הנתונים בשלב הבא.


### הגדרת פרמטרי כוונון עדין

LLaMA-Factory תומכת במספר תכניות כוונון עדין.

| תכניות כוונון עדין | דוגמאות LLaMA-Factory |
|-----------|------|
| פרמטר מלא    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| כוונון עדין LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| כוונון עדין QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

קבצי תצורה לדוגמה אלה ציינו פרמטרי מודל, פרמטרי שיטת כוונון עדין, פרמטרי מערך נתונים, פרמטרי הערכה ועוד. ניתן להגדיר אותם בהתאם לצרכים שלכם. במדריך זה, נשתמש ב-[qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml).

**הסבר על פרמטרים מרכזיים:**
- `model_name_or_path` - שם מודל Hugging Face או נתיב קובץ מודל מקומי.
- `stage` - שלב האימון. אפשרויות: rm (מידול תגמול), pt (אימון מקדים), sft (כוונון עדין מפוקח), PPO, DPO, KTO, ORPO.
- `do_train` - true לאימון, false להערכה
- `finetuning_type` - שיטת כוונון עדין. אפשרויות: freeze, lora, full
- `lora_rank` - הממד של המטריצה בדרגה נמוכה המשמשת ב-LoRA, ערכים טיפוסיים: 4, 6, 8, 16 (ערכים קטנים יותר = פחות פרמטרים = כוונון עדין מהיר יותר; ערכים גדולים יותר = התאמה טובה יותר למשימה אך שימוש גבוה יותר במשאבים).
- `lora_target` - מודולי יעד לשיטת LoRA. ברירת מחדל: all.
- `dataset` - מערך/י נתונים לשימוש. השתמשו ב-"," להפרדת מספר מערכי נתונים
- `output_dir` - נתיב פלט הכוונון העדין
- `logging_steps` - מרווח רישום ביומן בצעדים
- `save_steps` - מרווח שמירת נקודת ביקורת של המודל.
- `overwrite_output_dir` - האם לאפשר דריסת ספריית הפלט.
- `per_device_train_batch_size` - גודל אצווה לאימון לכל התקן.
- `gradient_accumulation_steps` - מספר צעדי צבירת גרדיאנט.
- `learning_rate` - קצב למידה
- `num_train_epochs` - מספר תקופות אימון
- `lr_scheduler_type` - לוח זמנים לקצב למידה. אפשרויות: linear, cosine, polynomial, constant, וכו'.
- `warmup_ratio` - יחס חימום קצב למידה

<!-- @os:linux -->
נשנה את ערך ברירת המחדל של `lora_rank` כדי להריץ כוונון עדין על AMD Ryzen™ ו-AMD Radeon™ GPUs.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
נעדכן את תצורת כוונון ה-LoRA העדין המוגדרת כברירת מחדל לתאימות טובה יותר עם AMD Ryzen™ ו-AMD Radeon™ GPUs:
- הגדרת `lora_rank` מ-`8` ל-`6` כדי להפחית את השימוש בזיכרון במהלך הכוונון העדין.
- שימוש ב-`fp16` במקום `bf16` לתאימות רחבה יותר עם AMD GPU וצריכת זיכרון נמוכה יותר.
- הגדרת `dataloader_num_workers` ל-`0` ב-Windows כדי למנוע שגיאות `"Can't pickle local object<>"` הנגרמות מטעינת נתונים במולטי-פרוססינג.

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

### הרצת כוונון עדין של LLaMA-Factory

**llamafactory-cli** הוא כלי ממשק שורת הפקודה (CLI) הרשמי של LLaMA-Factory, שפותח כדי לפשט תהליכי עבודה מקצה לקצה של LLM (הכנת נתונים ← כוונון עדין ← הערכה ← פריסה) ללא כתיבת קוד מורכב.

לאימון/כוונון עדין, **llamafactory-cli train** הוא תת-הפקודה המרכזית של LLaMA Factory CLI. הוא מפשט תהליכי עבודה של כוונון עדין (עיבוד מקדים של נתונים, כוונון היפר-פרמטרים, אופטימיזציה של חומרה) לפקודת CLI אחת, תומך במספר פרדיגמות כוונון עדין (LoRA/QLoRA/כוונון עדין מלא) ומותאם ל-GPUs עם משאבים מוגבלים (למשל, QLoRA על 16GB VRAM).

ניתן להריץ כוונון עדין של LLaMA-Factory באמצעות הפקודה הבאה, המבוססת על קובץ התצורה המשונה של כוונון עדין Qwen3 LoRA.

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

לאחר הרצת כוונון עדין של LLM, כל הפלטים שנוצרו מאוחסנים ב-"output_dir", כולל קבצי נקודת ביקורת של המודל, קבצי תצורה ומדדי אימון.

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

### בדיקת המודל המכוונן

**llamafactory-cli chat** מיועד לצ'אט/הסקה אינטראקטיביים עם LLMs (הן מודלים בסיסיים והן מודלים מכווננים עם LoRA). LLaMA-Factory מספקת תצורת דוגמה להרצת הסקה של מודלים מכווננים ב-[examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). ניתן גם לשנות תצורת דוגמה זו כדי לשנות את ההגדרות, כגון ה-backend של ההסקה.

השתמשו בפקודה הבאה כדי לבדוק את המודל המכוונן של Qwen3:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
דוגמה לצ'אט עם המודל המכוונן מוצגת להלן:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### ייצוא המודל המכוונן

לשימוש בסביבת ייצור, המודל המאומן מראש ומתאם ה-LoRA צריכים להתמזג ולהיות מיוצאים למודל יחיד. מודל ממוזג זה ניתן לשימוש כקובץ מודל Hugging Face רגיל. LLaMA-Factory מספקת תצורות דוגמה ב-[examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

השתמשו בפקודה הבאה כדי לייצא את המודל המכוונן של Qwen3:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
תוצאת ייצוא המודל המכוונן מוצגת להלן.

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

## שימוש בממשק המשתמש הגרפי של LLaMA-Factory

`LLaMA-Factory` תומכת גם בכוונון עדין ללא קוד של LLMs דרך ממשק משתמש ווב בדפדפן.

השתמשו בפקודה הבאה כדי לפתוח אותו:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` מציע ממשק יעיל לניהול תהליכי עבודה של למידת מכונה, כולל אימון, הערכה, חיזוי, צ'אט וייצוא מודלים. להלן הקדמה קצרה לכל לשונית:

* **Train**: לשונית זו מאפשרת לכם לבחור מודל ומערך נתונים, להגדיר פרמטרי אימון ולהתחיל את תהליך האימון. חשוב להבין את הפרמטרים החובה והאופציונליים כדי לייעל את הגדרת האימון.
* **Evaluate & Predict**: לאחר האימון, ניתן להעריך את ביצועי המודל ולבצע חיזויים באמצעות לשונית זו. היא מספקת תובנות לגבי דיוק המודל ויעילותו על נתונים חדשים.
* **Chat**: לאחר השלמת האימון, טענו את המודל בלשונית Chat כדי לתקשר איתו ולראות את תוצאות עבודתכם. תכונה זו מאפשרת תקשורת בזמן אמת עם המודל המאומן.
* **Export**: לשונית זו מאפשרת ייצוא מודלים מאומנים לפריסה או לשימוש נוסף. ניתן לשמור את המודלים שלכם בפורמטים שונים המתאימים ליישומים שונים.

להנחיה מפורטת, אנו ממליצים לעיין בתיעוד הרשמי ב-[מאגר GitHub של LlamaFactory](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) וב-[LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). בנוסף, [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) מספק תובנות יקרות ערך לגבי הממשק ופונקציונליותו.

## השלבים הבאים
- נסו מודלים שונים כגון `gpt-oss` ומודלים מתקדמים אחרים.
- התנסו עם backends שונים על המודל המכוונן
 
לתיעוד נוסף, בקרו בכתובת: https://llamafactory.readthedocs.io/en/latest/