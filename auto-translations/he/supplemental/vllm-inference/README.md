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

vLLM הוא מנוע הסקה בעל ביצועים גבוהים המיועד למודלי שפה גדולים (LLMs). הוא מספק שירות מותאם עם batching רציף (continuous batching) לתפוקה גבוהה וממשק API תואם OpenAI לשילוב חלק עם אפליקציות. זה הופך את vLLM למתאים מאוד לפריסות ייצור שבהן מהירות ויעילות משאבים הם קריטיים.

מדריך זה ילמד אתכם כיצד לשרת LLMs באמצעות vLLM בקונטיינר על ה-GPU המשולב ולתקשר עם מודלים דרך ה-OpenAI Python API.

## מה תלמדו

- כיצד להגדיר ולהפעיל שרת vLLM עם תמיכת AMD ROCm™
- כיצד לתקשר עם מודלים דרך נקודות קצה של API תואם OpenAI
- כיצד לשלוח פרומפטים לשרת המקומי עם `vllm-prompt`

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

> **הערה**: אם VS Code אינו מותקן, ניתן להתקינו באמצעות AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מקדימות

vLLM פועל בקונטיינר בנוי מראש עם ROCm והתלויות שלו מותאמות מראש. אין צורך בהתקנה נוספת.

אין שלב התקנה של vLLM בצד המארח. הפעילו את vLLM באמצעות:

```bash
vllm-launch
```

ה-launcher מפעיל את הקונטיינר, מכוון ל-GPU המשולב, וחושף שרת vLLM מקומי תואם OpenAI. לחלופין, לחצו על סמל vLLM בשורת המשימות.

## התחלה מהירה

### 1. אימות שהשרת של vLLM פועל

ל-`vllm-launch` ייתכן ויידרשו מספר דקות לאתחל את הכול. לאחר שהשרת מופעל, הוא זמין בכתובת `http://localhost:8001`. השאירו את מסוף ההפעלה פתוח מכיוון שהשרת פועל בחזית (foreground), ואז פתחו מסוף נפרד עבור השלבים הנותרים. הדוגמאות שלהלן משתמשות ב-`Qwen/Qwen3-1.7B`; אם ה-launcher שלכם מוגדר למודל אחר, החליפו את מזהה המודל בבקשות.

### 2. שליחת פרומפט

השתמשו בסקריפט המסופק `vllm-prompt` לשליחת בקשה לשרת ה-vLLM המקומי התואם OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. שיחה עם המודל באמצעות ה-OpenAI Python API

מכיוון ש-vLLM חושף API תואם OpenAI, ניתן להשתמש בחבילת ה-Python `openai` כדי לתקשר איתו.

ראשית, צרו סביבה וירטואלית של Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->

התקינו את חבילת ה-OpenAI
```bash
pip install openai
```

צרו לקוח `OpenAI` שמכוון לשרת ה-vLLM המקומי במקום לשרתי OpenAI. הלקוח דורש `api_key` אך vLLM אינו מאמת אותו, כך שכל מחרוזת תעבוד:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

לאחר מכן, שלחו בקשת chat completion. זו משתמשת באותו פורמט הודעות כמו ה-OpenAI API — רשימת הודעות עם תפקידים כמו `"user"` ו-`"assistant"`. הגדרת `stream=True` משמעותה שהתשובה תגיע בהדרגה ולא כולה בבת אחת:

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

לבסוף, עברו על חלקי התגובה הזורמים (streamed chunks) והדפיסו כל חלק טקסט כשהוא מגיע:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

הסקריפט המצורף [chat_with_model.py](assets/chat_with_model.py) מכיל את הדוגמה המלאה וניתן להורדה.


## בחירה והגדרת מודל

כברירת מחדל, `vllm-launch` משרת את `Qwen/Qwen3-1.7B` כמודל בדיקה בפורט `8001`. ניתן לשנות את המודל, הפורט, ופרמטרי השירות של vLLM מבלי לבנות מחדש או לערוך את הקונטיינר.

### מודלים שנבדקו על ידי AMD

המודלים הבאים מוגדרים מראש ומאומתים על ידי AMD:

| מודל | הערות |
|-------|-------|
| `Qwen/Qwen3-1.7B` | מודל ברירת המחדל. קליל ומהיר לטעינה. |
| `openai/gpt-oss-20b` | מודל גדול יותר עבור תשובות באיכות גבוהה יותר. |

### הפעלת מודל שונה

העבירו את מזהה המודל עם `--model` (או `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### שינוי הפורט

העבירו פורט מעל 1024 עם `--port` (או `-p`); ברירת המחדל היא `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

אם שיניתם את הפורט, כוונו את `base_url` של הלקוח שלכם לאותו פורט (למשל `http://localhost:8080/v1`).

### העברת פרמטרים נוספים ל-vLLM

כל הארגומנטים הנוספים מועברים ישירות אל vLLM, כך שניתן לכוונן התנהגות שירות כמו אורך ההקשר (context length) או סוג הנתונים. ישנן שתי דרכים לספק אותם.

**בשורה (Inline)**, לאחר אפשרויות ה-launcher:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**באופן קבוע (Persistently)**, בקובץ תצורה ב-`~/.local/share/vLLM/vllm-launch.conf`. קובץ זה אינו קיים כברירת מחדל — צרו אותו והוסיפו את הארגומנטים שלכם כמערך Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

השתמשו ב-`+=` כדי להוסיף לארגומנטי ברירת המחדל במקום להחליף אותם:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

כדי לראות את כל אפשרויות ה-launcher בכל עת, הריצו:

```bash
vllm-launch --help
```

### היכן מאוחסנים המודלים

`vllm-launch` מחפש מודלים בשני מיקומים:

| מיקום | נתיב |
|----------|------|
| מודלי מערכת | `/var/cache/models` |
| מודלי משתמש | `~/.local/share/vLLM/models` |

ניתן למקם מודל שהורדתם באחת מהתיקיות ולהפעיל אותו על ידי העברת הנתיב או המזהה שלו ל-`--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **הערה**: הפעלת מודל שהורד באופן עצמאי בדרך זו צפויה לעבוד ברגע שהמודל ממוקם באחת מהתיקיות שלעיל, אך תהליך עבודה זה טרם אומת רשמית על ידי AMD.

## פתרון בעיות

### החיבור נדחה (Connection refused)

ודאו שהשרת פועל:
```bash
curl http://localhost:8001/health
```

## סיכום

במדריך זה, למדתם כיצד:

- להפעיל את vLLM בקונטיינר עם תמיכת ROCm על ה-GPU המשולב
- להפעיל שרת vLLM עם נקודות קצה API תואם OpenAI בפורט 8001
- לשלוח פרומפטים עם `vllm-prompt`
- לבצע קריאות API לשרת vLLM באמצעות בקשות סטרימינג ולא-סטרימינג
- לפתור בעיות נפוצות בהפעלת השרת, בזיכרון, ובחיבורי לקוח

כעת יש לכם פריסת vLLM בקונטיינר לשירות מודלי שפה גדולים עם ביצועים מותאמים על ה-GPU המשולב.

## הצעדים הבאים

- **נסו מודלים שונים** — השתמשו ב-`vllm-launch --model <model>` כדי להתנסות ב-LLMs שונים ולהשוות ביצועים (ראו [בחירה והגדרת מודל](#choosing-and-configuring-a-model)).
- **בנו אפליקציה** — השתמשו ב-API התואם OpenAI כדי לשלב את vLLM באפליקציית Python, בוט צ'אט, או תהליך אוטומציה.
- **כוונון עדין ושירות** — בצעו כוונון עדין (fine-tune) למודל באמצעות LoRA או QLoRA, ואז פרסו אותו עם vLLM להסקה מותאמת.
## משאבים נוספים

- **[התיעוד הרשמי של vLLM](https://docs.vllm.ai/)** — מדריכים מקיפים והפניות API
- **[מאגר ה-GitHub של vLLM](https://github.com/vllm-project/vllm)** — קוד מקור, בעיות ודיונים קהילתיים