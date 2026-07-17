<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

## סקירה כללית

סוכני קידוד הם כלים עוצמתיים המעצימים מפתחים באמצעות שיתוף פעולה עם סוכני AI המונעים על ידי מודלי שפה גדולים (LLMs). ניתן לשלב אותם בסביבת הפיתוח, כגון הטרמינל או VS Code, ובכך לאפשר אינטגרציה חלקה בתוך זרימת העבודה של המפתח.

מדריך זה מדגים כיצד להשתמש ב-Cline, VS Code ו-LM Studio להפעלת סוכן קידוד לחלוטין על המחשב המקומי שלך.

## מה תלמד

* כיצד להפעיל את VS Code עם סוכן הקידוד Cline לסיוע במשימות הנדסת תוכנה.
* כיצד להגדיר את Cline לתקשורת עם LM Studio לצורך הסקה מקומית של סוכני קידוד.
* כיצד להשתמש בסוכני קידוד מקומיים לפתרון משימות הנדסת תוכנה מהעולם האמיתי.

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה
> **הערה**: אם VS Code אינו מותקן, ניתן להתקין אותו דרך Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

<!-- @require:lmstudio,vscode -->

## הפעלה והגדרת LM Studio

נשתמש ב-LM Studio להגשת ה-LLM המניע את סוכן הקידוד.

- בשורת החיפוש, חפש את `LM Studio` והפעל את האפליקציה. תתקבל בדף הבא.

![מסך ראשוני של LM Studio](assets/initial-lm-studio.png)

לאחר מכן, עלינו לטעון את ה-LLM על המערכת. נשתמש במודל `Qwen3-Coder-30B-A3B` עם אורך הקשר גדול. (השתמש בלשונית Model להתקנתו אם טרם עשית זאת).
- לחץ על שורת החיפוש בחלק העליון של חלון LM Studio או הקש `CTRL+L`. לחץ על המתג `Manually choose model load parameters` ולאחר מכן לחץ על מודל Qwen3-Coder-30B-A3B.
- שנה את אורך ההקשר מ-`4096` ל-`32768`, וודא ש-`GPU Offload` מוגדר למקסימום. לאחר מכן, לחץ על `Load Model`.

![בחירת מודל](assets/model-list-zoomed.png)

אנו משתמשים באורך הקשר גדול כדי שהסוכן יוכל לעבד בסיסי קוד גדולים ולזכור שינויים שבוצעו.

![הגדרת מודל](assets/selecting-model-zoomed.png)

לאחר מכן, עלינו להפעיל את שרת LM Studio.
- לחץ על לשונית Developer או הקש `CTRL+2` ב-LM Studio בצד שמאל.
- בדוק את מתג הסטטוס וודא שהוא מוגדר ל-`Running`.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![סטטוס שרת](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## הפעלה והגדרת VS Code

נתקין את תוסף Cline ב-VS Code ונחבר אותו לשרת LM Studio שיצרנו.
- בשורת החיפוש, חפש את `VS Code` והפעל את האפליקציה.
- לחץ על סמל `Extensions` בעמודה השמאלית של VS Code וחפש את `Cline`. לאחר מכן, לחץ על כפתור `Install`.

![התקנת תוסף Cline](assets/installing-cline-vscode-extension.png)

- סמל Cline אמור להופיע בצד שמאל. לחץ עליו כדי לפתוח את Cline. יופיע חלון עם השאלה `How will you use Cline?` מכיוון שנשתמש ב-LLM מקומי הפועל דרך LM Studio, בחר `Bring my own API Key` ולחץ `Continue`.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![יצירת חשבון](assets/cline-how-will-you-use-cline-zoomed.png)

לאחר מכן, עלינו להגדיר את Cline לתקשורת עם שרת LM Studio שהגדרנו.
- הגדר את ספק ה-API ל-`LM Studio` ואת המודל ל-`Qwen3-Coder-30B-A3B-GGUF`.

>**טיפ**: ייתכן שמודלים חדשים יותר זמינים. שקול להוריד ולעבור למודלי Qwen3.6 אם תרצה.


![הגדרת מודל](assets/cline-model-configuration-zoomed.png)

## יצירת הפרויקט הראשון שלך

בואו נשתמש בסוכן המקומי שלנו ליצירת אתר אינטרנט! פתח את VSCode לתיקייה לבחירתך שבה Cline ייצור את הקבצים.
- לשם כך, עבור אל `File -> Open Folder` בפינה השמאלית העליונה של VS Code ובחר תיקייה כגון `Documents`.

![תיקייה ריקה ב-VS Code](assets/open-cline-test.png)

כעת אנו מוכנים לשלוח פרומפט לסוכן הקידוד המקומי.
- לחץ על תוסף Cline בעמודה השמאלית והזן פרומפט להפעלת הסוכן. כדוגמה, נשתמש בפרומפט הבא:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

הסוכן יתחיל ליצור קבצים בהתאם לפרומפט. כמשתמש, תוכל לצפות בקוד הנוצר ב-VS Code כפי שמוצג להלן. ייתכן שתצטרך ללחוץ על `Save` בכל פעם ש-Cline רוצה ליצור קובץ.

![יצירת קוד על ידי Cline](assets/cline-code-generation.png)

לאחר יצירת התוכנה, הסוכן מסיים ותוכל להפעיל את האפליקציה. במקרה זה, הסוכן כתב לשלושה קבצים: `index.html`, `script.js` ו-`styles.css`. בלחיצה כפולה פשוטה על קובץ ה-HTML נוכל לטעון ולתקשר עם האתר שנוצר.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

## השלבים הבאים

לאחר יצירת האתר, תוכל להמשיך לעבוד עם Cline לשיפורו. שני שיפורים אפשריים הם:

- **תיעוד**: שליחת פרומפט לסוכן עם `Add a README` היא כל מה שנדרש כדי שהסוכן יצור קובץ `README.md` המתעד את האתר.
- **אנימציה**: שלח למודל את הפרומפט `Add an animation that visually represents a large language model running on a laptop.` ליצירת אנימציה לאתר.

אנו מעודדים את הקורא לנסות ליצור אפליקציות אחרות באמצעות הגדרה זו. להלן כמה דוגמאות מהנות שניסינו:

- **משחקי ארקייד רטרו**: נסה פרומפטים אחרים. יכול להיות מהנה לבקש מהסוכן ליצור משחקים בסגנון רטרו ב-Python באמצעות חבילת `PyGame` עם הפרומפט הבא:

```code
Create a simple pong game using the PyGame python package.
```

- **ניתוח נתונים**: תחום אחד שבו סוכני קידוד שימושיים במיוחד הוא תסריטים וניתוח נתונים. זהו פרומפט להדגמת יכולת המודל המקומי ליצור תוכנת ניתוח נתונים לויזואליזציה של מחירי מניות:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## משאבים

להלן כמה משאבים נוספים ללמידה נוספת על סוכני קידוד, Cline והפעלת עומסי עבודה על

* מידע נוסף על שותפות ואינטגרציה של AMD עם LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* בלוג AMD המדריך כיצד להפעיל את Cline על AMD Ryzen™ AI ועל כרטיסי גרפיקה Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* בלוג Cline על הפעלת סוכני קידוד מקומית על מחשבי AI: https://cline.bot/blog/local-models-amd