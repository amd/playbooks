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

רוצים להריץ מודלים חזקים של בינה מלאכותית לשפה על החומרה שלכם? מדריך זה יראה לכם כיצד.
מדריך זה משתמש ב-PyTorch המופעל על ידי תוכנת AMD ROCm™ כדי להריץ מודלים שיכולים לסכם מסמכים, לענות על שאלות, ליצור טקסט ועוד, הכל באופן מקומי.

## מה תלמדו

- הרצת מודלי LLM כמו gpt-oss-20b ו-qwen3.5-4B באופן מקומי באמצעות PyTorch ו-ROCm
- יצירת כלי לסיכום מסמכים באמצעות מודלי LLM

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה
> **הערה**: אם VS Code אינו מותקן, ניתן להתקין אותו באמצעות Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מקדימות

### יצירת סביבה וירטואלית

<!-- @os:linux -->
<!-- @device:halo_box -->
במערכת Linux, פתחו מסוף בתיקייה לבחירתכם ובצעו את הפקודות ליצירת venv עם ROCm+Pytorch מותקנים מראש.
<!-- @test:id=create-venv timeout=120 -->
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
**הענקת גישה למשתמש שלכם להתקני GPU** (יש להתנתק ולהתחבר מחדש כדי שהשינוי ייכנס לתוקף):

```bash
sudo usermod -aG render,video $LOGNAME
```

במערכת Linux, פתחו מסוף בתיקייה לבחירתכם ובצעו את הפקודות ליצירת venv.
<!-- @test:id=create-venv timeout=120 -->
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
במערכת Windows, פתחו מסוף בתיקייה לבחירתכם ובצעו את הפקודות ליצירת venv עם ROCm+Pytorch מותקנים מראש.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
במערכת Windows, פתחו מסוף בתיקייה לבחירתכם ובצעו את הפקודות ליצירת venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **טיפ**: ייתכן שמשתמשי Windows יצטרכו לשנות את מדיניות ההרצה (Execution Policy) של PowerShell שלהם (למשל,
> להגדיר אותה כ-RemoteSigned או Unrestricted) לפני הרצת חלק מפקודות ה-Powershell.

<!-- @os:end -->

### התקנת תלויות בסיסיות
<!-- @require:driver,pytorch -->

### התקנת תלויות נוספות

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
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
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## התחלה מהירה עם סקריפטים לדוגמה

מדריך זה כולל סקריפטים מוכנים לשימוש. לחצו עליהם כדי לצפות בהם ולהוריד אותם לאותה תיקייה של הסביבה שיצרתם.

| סקריפט | תיאור | שימוש |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | יצירת טקסט בסיסית עם LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | כלי לסיכום מסמכים עם תמיכת Harmony | `python summarizer.py --file document.txt` |

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

שני הסקריפטים תומכים ב:
- בחירת מודל באמצעות דגל `--model`
- עיצוב תבנית שיחה (chat template) עבור הנחיה תקינה של המודל, שימושי במיוחד לסיכום מסמכים

## טעינה והרצה של מודל ה-LLM הראשון שלכם

הסקריפט המצורף [run_llm.py](assets/run_llm.py) מדגים כיצד ליצור טקסט באמצעות מודלי LLM תוך שימוש ב-PyTorch ו-AMD ROCm.

> **הערה:** כאשר אתם טוענים מודל, Hugging Face Transformers בודקת תחילה את המטמון המקומי שלה (`~/.cache/huggingface/hub` במערכת Linux, `C:\Users\<user>\.cache\huggingface\hub` במערכת Windows). אם המודל אינו שמור במטמון, הוא יורד אוטומטית מ-huggingface.co. ההרצה הראשונה עשויה לקחת מספר דקות, בהתאם לגודל המודל ומהירות הרשת.

הקטע שלהלן מדגים כיצד להשתמש במודל ולהתאים אישית את השאלות הנשאלות.

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
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
    device_map="auto"
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

נסו את הסקריפט שהורדתם:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## בניית כלי לסיכום מסמכים

לאחר שיצרתם פלט מקומי ממודל LLM, תוכלו להמשיך משם ולבנות כלי מעשי לסיכום מסמכים. בסעיף זה תשתמשו בסקריפט [summarizer.py](assets/summarizer.py) כדי להזין קובץ txt. ולייצר באופן אוטומטי סיכום תמציתי, הכל תוך הרצה מקומית על ה-GPU שלכם.

הסקריפט מתוכנן לעבוד ישר מהקופסה. פתחו את הסקריפט בעורך כדי לחקור את הקוד, להתאים אישית את ההנחיות (prompts) ולכוונן פרמטרים כמו אורך וטמפרטורה.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### דוגמאות שימוש

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

## הכירו את פרמטרי היצירה

| פרמטר | מה הוא שולט בו | ערכים טיפוסיים |
|-----------|------------------|----------------|
| `max_new_tokens` | האורך המקסימלי של הפלט של ה-LLM | השתמשו ב-50–500 טוקנים עבור סיכומים. (טוקן אחד שווה בערך ל-0.75 מילים באנגלית) |
| `temperature` | יצירתיות. ערכים נמוכים הופכים אותה למרוכזת, בעוד שערכים גבוהים מגיעים עם יותר בלתי-צפיות | - **0.1–0.3**: ממוקד, דטרמיניסטי (טוב לסיכומים) <br> **0.5–0.7**: מאוזן (לשימוש כללי) <br> **0.8–1.0**: יצירתי, מגוון (סיעור מוחות) |
| `top_p` | דגימת גרעין (Nucleus Sampling) - ערכים נמוכים מגבילים את המודל לפלטים צרים יותר | **0.1-0.5**: קפדני, צפוי <br> **0.9-0.95**: (סטנדרטי, טבעי, שיחתי) |


## יישומים בעולם האמיתי

- **ניתוח מאמרי מחקר**: חילוץ ממצאים מרכזיים מפרסומים מורכבים לסקירה מהירה
- **איסוף חדשות**: סיכום כתבות חדשותיות לתמציות או הדגשות יומיות קצרות
- **פרוטוקולי פגישות**: צמצום תמלולים לפריטי פעולה וסיכומים תמציתיים
- **סקירת מסמכים משפטיים**: חילוץ סעיפים או התחייבויות רלוונטיים מטקסטים משפטיים ארוכים במהירות
- **תיעוד קוד**: יצירת סקירות תמציתיות של מאגרי קוד והסברי פונקציות

## השלבים הבאים

- **כוונון עדין (Fine-tuning)**: התאמת מודלים לתחום או לעגה הספציפיים שלכם לדיוק טוב יותר (ראו מדריכי Fine-tuning)
- **מערכות RAG**: שילוב מודלי LLM עם אחזור מסמכים לתשובות וחיפוש מודעי-הקשר
- **חקר מודלים**: התנסות במודלים חדשים כמו Llama 3, Phi-3 או Qwen לתוצאות טובות יותר
- **פריסה בסביבת ייצור**: שימוש בכלים כמו vLLM להגשת LLM בקנה מידה גדול בארגונים

המערכת שלכם מעניקה לכם את היכולת להריץ מודלי שפה מתוחכמים באופן מקומי. התנסו במודלים, הנחיות ופרמטרים שונים כדי לגלות מה עובד הכי טוב עבור היישומים שלכם.