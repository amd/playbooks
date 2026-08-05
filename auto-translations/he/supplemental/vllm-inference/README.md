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

vLLM הוא מנוע היסק בעל ביצועים גבוהים שנועד עבור מודלי שפה גדולים (LLMs). הוא מספק שירות מותאם עם אצווה רציפה (continuous batching) להשגת תפוקה גבוהה, וממשק API תואם OpenAI לשילוב חלק עם יישומים. הדבר הופך את vLLM לכלי מצוין עבור פריסות ייצור שבהן מהירות ויעילות משאבים הם קריטיים.

מדריך זה מלמד כיצד להגיש LLMs באמצעות vLLM המוכל (containerized) על ה-GPU המשולב ולתקשר עם מודלים דרך ה-OpenAI Python API.

## מה תלמדו

- כיצד להגדיר ולהפעיל שרת vLLM עם תמיכת AMD ROCm™
- כיצד לתקשר עם מודלים דרך נקודות קצה API תואמות OpenAI
- כיצד לשלוח בקשות (prompts) לשרת המקומי באמצעות `vllm-prompt`

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

> **הערה**: אם VS Code אינו מותקן, ניתן להתקין אותו באמצעות AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מקדימות

vLLM פועל בתוך קונטיינר מוכן מראש עם ROCm ותלויותיו המותאמות מראש. אין צורך בהתקנה נוספת.

אין שלב התקנת vLLM בצד המארח. יש להפעיל את vLLM באמצעות:

```bash
vllm-launch
```

המשגר מפעיל את הקונטיינר, מכוון אל ה-GPU המשולב, וחושף שרת vLLM מקומי תואם OpenAI. לחלופין, ניתן ללחוץ על סמל vLLM בשורת המשימות.

## התחלה מהירה

### 1. אימות שהשרת של vLLM פועל

ל-`vllm-launch` עשוי לקחת מספר דקות לאתחל את כל הרכיבים. ברגע שהשרת עולה, הוא זמין בכתובת `http://localhost:8001`. יש להשאיר את מסוף ההפעלה פתוח מכיוון שהשרת פועל בחזית (foreground), ולאחר מכן לפתוח מסוף נפרד עבור השלבים הנותרים. הדוגמאות שלהלן משתמשות במודל `Qwen/Qwen3-1.7B`; אם המשגר שלכם מוגדר עבור מודל אחר, יש להחליף את מזהה המודל בבקשות בהתאם.

### 2. שליחת בקשה (Prompt)

יש להשתמש בסקריפט `vllm-prompt` המסופק כדי לשלוח בקשה אל שרת ה-vLLM המקומי התואם OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. שיחה עם המודל באמצעות ה-OpenAI Python API

מכיוון ש-vLLM חושף API תואם OpenAI, ניתן להשתמש בחבילת ה-Python `openai` כדי לתקשר איתו.

תחילה, יש ליצור סביבה וירטואלית של Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

יש להתקין את חבילת OpenAI
```bash
pip install openai
```

יש ליצור לקוח `OpenAI` שמופנה לשרת ה-vLLM המקומי במקום לשרתי OpenAI. מפתח ה-`api_key` נדרש על ידי הלקוח, אך vLLM אינו מאמת אותו, כך שכל מחרוזת תעבוד:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

לאחר מכן, יש לשלוח בקשת השלמת שיחה (chat completion). זו משתמשת באותו פורמט הודעות כמו ה-API של OpenAI — רשימת הודעות עם תפקידים (roles) כגון `"user"` ו-`"assistant"`. הגדרת `stream=True` משמעה שהתגובה תגיע בהדרגה במקום בבת אחת:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

לבסוף, יש לעבור על מקטעי הזרימה (streamed chunks) ולהדפיס כל חלק טקסט ברגע שהוא מגיע:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

הסקריפט המצורף [chat_with_model.py](assets/chat_with_model.py) מכיל את הדוגמה המלאה וניתן להורדה.


## בחירה והגדרת מודל

כברירת מחדל, `vllm-launch` מגיש את `Qwen/Qwen3-1.7B` כמודל בדיקה בפורט `8001`. ניתן לשנות את המודל, הפורט, ופרמטרי ההגשה של vLLM ללא בנייה מחדש או עריכת הקונטיינר.

### מודלים שנבדקו על ידי AMD

המודלים הבאים מוגדרים מראש ומאומתים על ידי AMD:

| מודל | הערות |
|-------|-------|
| `Qwen/Qwen3-1.7B` | מודל ברירת מחדל. קליל ומהיר לטעינה. |
| `openai/gpt-oss-20b` | מודל גדול יותר לתגובות באיכות גבוהה יותר. |

### הפעלת מודל שונה

יש להעביר את מזהה המודל עם `--model` (או `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### שינוי הפורט

יש להעביר פורט מעל 1024 עם `--port` (או `-p`); ברירת המחדל היא `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

אם משנים את הפורט, יש להפנות את `base_url` של הלקוח לאותו פורט (לדוגמה `http://localhost:8080/v1`).

### העברת פרמטרים נוספים ל-vLLM

כל הארגומנטים הנוספים מועברים ישירות אל vLLM, כך שניתן לכוונן התנהגות הגשה כגון אורך ההקשר (context length) או סוג הנתונים (data type). ישנן שתי דרכים לספק אותם.

**באופן מוטבע (Inline)**, לאחר אפשרויות המשגר:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**באופן קבוע**, בקובץ תצורה בנתיב `~/.local/share/vLLM/vllm-launch.conf`. קובץ זה אינו קיים כברירת מחדל — יש ליצור אותו ולהוסיף את הארגומנטים שלכם כמערך Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

יש להשתמש ב-`+=` כדי להוסיף לארגומנטים המוגדרים כברירת מחדל במקום להחליף אותם:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

כדי לראות את כל אפשרויות המשגר בכל עת, יש להריץ:

```bash
vllm-launch --help
```

### היכן מאוחסנים המודלים

`vllm-launch` מחפש מודלים בשני מיקומים:

| מיקום | נתיב |
|----------|------|
| מודלי מערכת | `/var/cache/models` |
| מודלי משתמש | `~/.local/share/vLLM/models` |

ניתן למקם מודל שהורד באחת מהתיקיות ולהפעיל אותו על ידי העברת הנתיב או המזהה שלו אל `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **הערה**: הפעלת מודל שהורד בעצמכם בדרך זו צפויה לעבוד ברגע שהמודל ממוקם באחת מהתיקיות שלעיל, אך זרימת עבודה זו טרם אומתה רשמית על ידי AMD.

## פתרון בעיות

### החיבור נדחה (Connection refused)

יש לוודא שהשרת פועל:
```bash
curl http://localhost:8001/health
```

## סיכום

במדריך זה למדתם כיצד:

- להפעיל vLLM המוכל (containerized) עם תמיכת ROCm על ה-GPU המשולב
- להפעיל שרת vLLM עם נקודות קצה API תואמות OpenAI בפורט 8001
- לשלוח בקשות (prompts) באמצעות `vllm-prompt`
- לבצע קריאות API אל שרת ה-vLLM באמצעות בקשות עם ובלי הזרמה (streaming)
- לפתור בעיות נפוצות בהפעלת השרת, בזיכרון, ובחיבורי לקוח

כעת יש ברשותכם פריסת vLLM מוכלת (containerized) להגשת מודלי שפה גדולים עם ביצועים מותאמים על ה-GPU המשולב.

## הצעדים הבאים

- **נסו מודלים שונים** — יש להשתמש ב-`vllm-launch --model <model>` כדי להתנסות ב-LLMs שונים ולהשוות ביצועים (ראו [בחירה והגדרת מודל](#choosing-and-configuring-a-model)).
- **בנו יישום** — יש להשתמש ב-API התואם OpenAI כדי לשלב את vLLM ביישום Python, צ'אטבוט, או תהליך אוטומציה.
- **כיוונון עדין והגשה** — יש לבצע כיוונון עדין (fine-tune) למודל באמצעות LoRA או QLoRA, ולאחר מכן לפרוס אותו עם vLLM עבור היסק מותאם.
## משאבים נוספים

- **[התיעוד הרשמי של vLLM](https://docs.vllm.ai/)** — מדריכים מקיפים והפניות API
- **[מאגר ה-GitHub של vLLM](https://github.com/vllm-project/vllm)** — קוד מקור, בעיות ודיונים בקהילה