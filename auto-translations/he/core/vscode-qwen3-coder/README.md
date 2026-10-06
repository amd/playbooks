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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> מדריך זה דורש לפחות **32GB** של זיכרון מערכת.
<!-- @device:end -->

## סקירה כללית

סוכני קוד הם כלים רבי עוצמה המעצימים מפתחים באמצעות שיתוף פעולה עם סוכני AI המבוססים על מודלי שפה גדולים (LLMs). ניתן להטמיע אותם בסביבת הפיתוח, כגון המסוף או VS Code, מה שמאפשר שילוב חלק בתהליך העבודה של המפתח.

מדריך זה מדגים כיצד להשתמש ב-Cline, VS Code ו-LM Studio כדי להפעיל סוכן קוד באופן מלא על המחשב המקומי שלך.

## מה תלמדו

* כיצד להפעיל את VS Code עם סוכן הקוד Cline כדי לסייע במשימות הנדסת תוכנה.
* כיצד להגדיר את Cline לתקשר עם LM Studio לצורך הסקה מקומית של סוכני קוד.
* כיצד להשתמש בסוכני קוד מקומיים כדי לפתור משימות הנדסת תוכנה מהעולם האמיתי.

<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה
> **הערה**: אם VS Code אינו מותקן, ניתן להתקין אותו באמצעות Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מקדימות

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lmstudio,vscode -->
<!-- @prereq:lmstudio-models-qwen3-coder-30b -->

## הפעלה והגדרת LM Studio

נשתמש ב-LM Studio כדי להגיש את ה-LLM שמפעיל את סוכן הקוד.

- בשורת החיפוש, חפשו `LM Studio` והפעילו את האפליקציה. תתקבלו בפנים על ידי הדף הבא.

![מסך ההתחלה של LM Studio](assets/initial-lm-studio.png)

בשלב הבא, עלינו לטעון את ה-LLM על המערכת. נשתמש במודל `Qwen3-Coder-30B-A3B` עם אורך הקשר גדול. (השתמשו בלשונית Model כדי להתקין אותו אם עדיין לא עשיתם זאת).
- לחצו על שורת החיפוש בחלק העליון של חלון LM Studio או הקישו `CTRL+L`. לחצו על המתג `Manually choose model load parameters` ולאחר מכן לחצו על מודל Qwen3-Coder-30B-A3B.
- שנו את אורך ההקשר מ-`4096` ל-`32768`, וודאו ש-`GPU Offload` נמצא במקסימום. לאחר מכן, לחצו על `Load Model`

![בחירת מודל](assets/model-list-zoomed.png)

אנו משתמשים באורך הקשר גדול כדי שהסוכן יוכל לעבד בסיסי קוד גדולים ולזכור שינויים שבוצעו.

![הגדרת מודל](assets/selecting-model-zoomed.png)

בשלב הבא, עלינו להפעיל את שרת LM Studio.
- לחצו על לשונית Developer או הקישו `CTRL+2` ב-LM Studio בצד שמאל.

- סמנו את מתג הסטטוס וודאו שהוא מוגדר ל-`Running`.

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

![סטטוס השרת](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
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
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## הפעלה והגדרת VS Code

נתקין את התוסף Cline ב-VS Code ונחבר אותו לשרת LM Studio שיצרנו זה עתה.
- בשורת החיפוש, חפשו `VS Code` והפעילו את האפליקציה.
- לחצו על סמל ה-`Extensions` בעמודה השמאלית של VS Code וחפשו `Cline`. לאחר מכן, לחצו על כפתור ה-`Install`.

![התקנת תוסף Cline](assets/installing-cline-vscode-extension.png)

- סמל Cline אמור להופיע בצד שמאל. לחצו עליו כדי לפתוח את Cline. יופיע חלון ששואל `How will you use Cline?` מכיוון שאנו עומדים להשתמש ב-LLM מקומי הפועל דרך LM Studio, בחרו `Bring my own API Key` ולחצו `Continue`.

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

בשלב הבא, עלינו להגדיר את Cline לתקשר עם שרת LM Studio שהקמנו.
- הגדירו את ה-API Provider ל-`LM Studio` ואת המודל ל-`Qwen3-Coder-30B-A3B-GGUF`.

>**טיפ**: ייתכן שיהיו זמינים מודלים חדשים יותר. שקלו להוריד ולעבור למודלי Qwen3.6 אם תרצו.


![הגדרת מודל](assets/cline-model-configuration-zoomed.png)

## יצירת הפרויקט הראשון שלכם

בואו נשתמש בסוכן המקומי שלנו כדי ליצור אתר אינטרנט! פתחו את VSCode בתיקייה לבחירתכם שבה Cline ייצור את הקבצים.
- לשם כך, לכו אל `File -> Open Folder` בחלק השמאלי העליון של VS Code ובחרו תיקייה כגון `Documents`.

![תיקייה ריקה ב-VS Code](assets/open-cline-test.png)

כעת אנו מוכנים להזין פקודה לסוכן הקוד המקומי.
- לחצו על תוסף Cline בעמודה השמאלית והזינו פקודה כדי להפעיל את הסוכן. לדוגמה, נשתמש בפקודה הבאה:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

הסוכן יתחיל ליצור קבצים בהתאם לפקודה. כמשתמשים, תוכלו לצפות בקוד נוצר ב-VS Code כפי שמוצג להלן. ייתכן שתצטרכו ללחוץ על `Save` בכל פעם ש-Cline רוצה ליצור קובץ.

![יצירת קוד על ידי Cline](assets/cline-code-generation.png)

לאחר יצירת התוכנה, הסוכן סיים את עבודתו ותוכלו להפעיל את האפליקציה. במקרה זה, הסוכן כתב לשלושה קבצים: `index.html`, `script.js`, ו-`styles.css`. פשוט על ידי לחיצה כפולה על קובץ ה-HTML נוכל לטעון ולהתעסק עם האתר שנוצר.

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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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

## שלבים הבאים

לאחר יצירת האתר, תוכלו להמשיך לעבוד עם Cline כדי לשפר את האתר. שני שיפורים אפשריים הם:

- **תיעוד**: הזנת הפקודה `Add a README` לסוכן היא כל מה שנדרש כדי שהסוכן ייצור קובץ `README.md` המתעד את האתר.
- **אנימציה**: הזינו למודל את הפקודה `Add an animation that visually represents a large language model running on a laptop.` כדי ליצור אנימציה לאתר.

אנו מעודדים את הקוראים לנסות ליצור אפליקציות נוספות באמצעות ההגדרה הזו. להלן כמה דוגמאות מהנות שניסינו:

- **משחקי ארקייד רטרו**: נסו פקודות נוספות. יכול להיות גם כיף שהסוכן ייצור משחקים בסגנון רטרו בפייתון באמצעות החבילה `PyGame` עם הפקודה הבאה:

```code
Create a simple pong game using the PyGame python package.
```

- **ניתוח נתונים**: תחום אחד שבו סוכני קוד שימושיים במיוחד הוא כתיבת סקריפטים וניתוח נתונים. זוהי פקודה המדגימה את יכולת המודל המקומי ליצור תוכנת ניתוח נתונים להצגת מחירי מניות:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## משאבים

להלן כמה משאבים נוספים ללמידה נוספת על סוכני קידוד (Coding Agents), Cline, והרצת עומסי עבודה על 

* מידע נוסף על שותפות השילוב בין AMD ל-LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* בלוג של AMD המדגים כיצד להריץ את Cline על כרטיסי AMD Ryzen™ AI ו-Radeon™ Graphics: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* בלוג של Cline על הרצת סוכני קידוד באופן מקומי במחשבי AI PC: https://cline.bot/blog/local-models-amd