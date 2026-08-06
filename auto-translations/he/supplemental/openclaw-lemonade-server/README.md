<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

# הרצת OpenClaw עם Lemonade Server כ-backend

## סקירה כללית

[**OpenClaw**](https://openclaw.ai/) הוא סוכן AI אוטונומי שיכול לכתוב ולהריץ קוד, לנהל קבצים ולעבוד על משימות מורכבות רבות-שלבים מטעמכם. בניגוד לעוזר צ'אט שרק עונה על שאלות, OpenClaw מבצע פעולות אמיתיות במערכת שלכם, מה שאומר שהוא זקוק ל-backend AI מהיר ומיומן שיכול לעמוד בקצב של לולאת סוכן תובענית.

[**Lemonade Server**](https://lemonade-server.ai/) הוא ה-backend הזה. זהו שרת הסקה מקומי בקוד פתוח שמריץ מודלי GenAI ישירות על החומרה שלכם וחושף אותם דרך ה-API הסטנדרטי בתעשייה של OpenAI.

יחד, הם יוצרים מחסנית סוכן AI מקומית לחלוטין: Lemonade מטפל בהסקת המודל, ו-OpenClaw מספק את לולאת הסוכן שהופכת את פלטי המודל לפעולות אמיתיות.

> **לפני שתמשיכו:** OpenClaw הוא סוכן AI אוטונומי מאוד. מתן גישה למערכת שלכם לכל סוכן AI עלול להוביל לתוצאות בלתי צפויות או בלתי מכוונות. המשיכו רק אם אתם מבינים את הסיכונים ומרגישים בנוח עם תוכנה אוטונומית הפועלת מטעמכם.

---

## מה תלמדו

בסיום מדריך זה תוכלו:

- ללמוד על **Lemonade Server**
- **להתקין את OpenClaw** ו**להצביע אותו לעבר Lemonade Server** כ-backend ה-AI שלו.
- **להפעיל את שער ה-OpenClaw (gateway)** ולוודא שהסוכן שלכם מוכן לעבודה.
- **לחבר ערוץ תקשורת** (Discord או Telegram) כדי שתוכלו לשוחח עם הסוכן שלכם מכל מכשיר.

---

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

<!-- @os:linux -->
- מחשב המריץ **Ubuntu 24.04+** או הפצת Linux מבוססת Debian תואמת עם `apt-get`
- לפחות **12 GB של RAM** (מומלץ 64 GB+ עבור מודלים גדולים יותר)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (אופציונלי, ל-sandboxing של OpenClaw)
- **~10–30 GB של שטח דיסק פנוי** עבור משקלי המודל
<!-- @os:end -->

<!-- @os:windows -->
- מחשב המריץ **Windows 10/11**
- לפחות **12 GB של RAM** (מומלץ 64 GB+ עבור מודלים גדולים יותר)
- **~10–30 GB של שטח דיסק פנוי** עבור משקלי המודל
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (אופציונלי, ל-sandboxing של OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## משיכה וטעינה של המודל המומלץ

המודל המומלץ עבור מדריך זה הוא **Qwen3.6-35B-A3B-GGUF** מ-Unsloth, מודל MoE חזק עם חלון הקשר של 263 אלף טוקנים, שמתאים היטב לעומסי עבודה של סוכנים. מודל זה משתמש בקוונטיזציה UD-Q4_K_XL. משכו אותו כעת:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

לאחר מכן טענו אותו עם חלון הקשר גדול ושמרו את ההגדרה הזו להרצות עתידיות:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

למודל אורך הקשר ברירת מחדל של 262,144 טוקנים. אם אתם נתקלים בשגיאות של חוסר זיכרון (OOM), שקלו לצמצם את חלון ההקשר. עם זאת, מכיוון ש-Qwen3.6 מנצל הקשר מורחב עבור משימות מורכבות, אנו ממליצים לשמור על אורך הקשר של לפחות 128K טוקנים כדי לשמר את יכולות החשיבה.

> **טיפ: השבתת מצב חשיבה למען תגובות סוכן מהירות יותר:** Qwen3.6-35B-A3B פועל במצב חשיבה כברירת מחדל, מה שמוסיף השהיה לפני כל תגובה. עבור לולאות סוכן, תקורה זו מצטברת במהירות. המאגר [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) מספק תצורה מוכנה מראש שמשביתה את מצב החשיבה. כדי להשתמש בה, הורידו את הקובץ וייבאו אותו:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"

python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
model_id = "${openclaw_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->

## הגדרת WSL

אנו מריצים את OpenClaw בתוך WSL (מומלץ) ומחברים אותו ל-Lemonade הפועל באופן טבעי ב-Windows. כך תקבלו סביבת מעטפת Linux עבור OpenClaw תוך שמירה על האצת ה-GPU של Lemonade בצד Windows.

### התקנת WSL ו-Ubuntu

פתחו את PowerShell כמנהל מערכת והתקינו את גרעין ה-WSL:

```powershell
wsl --install --no-distribution
```

לאחר מכן התקינו Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### הפעלת systemd ב-WSL

הריצו זאת בתוך מסוף Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

צאו מ-WSL והפעילו אותו מחדש:

```powershell
exit
wsl --shutdown
wsl
```

### חיבור Lemonade מ-Windows אל WSL

WSL2 פועל ברשת וירטואלית. Lemonade ב-Windows נקשר ל-`127.0.0.1`, שאליו WSL לא יכול להגיע ישירות. פרוקסי פורט של Windows מעביר תעבורה מכתובת ה-IP של שער ה-WSL אל localhost של Windows.

**מצאו את כתובת ה-IP של שער ה-WSL שלכם** (הריצו בתוך WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**הוסיפו את פרוקסי הפורט** (הריצו ב-PowerShell כמנהל מערכת, החליפו את `<WSL-Gateway-IP>` בכתובת ה-IP של שער ה-WSL שלכם):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> הערה: אם אתם נתקלים בשגיאת `netsh: command not found`, נסו להשתמש בשם הקובץ המפורש במקום זאת - `netsh.exe`

**הוסיפו כלל חומת אש (firewall)** (אותו PowerShell מוגבה הרשאות):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**אמתו מתוך WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

אם כבר טענתם את המודל Qwen3.6-35B-A3B-GGUF בשלב הקודם, אתם אמורים לראות פלט JSON כמו זה:

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

#### שמירה על תקינות הגשר לאחר הפעלה מחדש

הכלל של `netsh portproxy` שורד לאחר הפעלות מחדש, אך כתובת ה-IP של שער ה-WSL עלולה להשתנות לאחר `wsl --shutdown` או הפעלה מחדש. כשזה קורה, ה-proxy עדיין מצביע על ה-IP הישן ו-Lemonade הופך לבלתי נגיש מ-WSL. אם זה קורה, השתמשו באחת מהאפשרויות הבאות.

**אפשרות 1 (מומלצת) — תיקון הגשר באופן אוטומטי.** כדי להימנע מלעשות זאת ידנית בכל פעם, השתמשו במשימה מתוזמנת שבודקת את הגשר בכל הפעלה והתחברות ומשחזרת אותו רק כאשר כתובת ה-IP של השער השתנתה. ראו את [מדריך התיקון האוטומטי לגשר ה-WSL של Lemonade](assets/RepairLemonadeWslBridge.md).


**אפשרות 2 — תיקון הגשר ידנית.** תחילה, קבלו את כתובת ה-IP הנוכחית של שער ה-WSL על ידי הרצת הפקודה הבאה בתוך WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

העתיקו ערך זה; תשתמשו בו במקום `<new-WSL-Gateway-IP>` בהמשך.

לאחר מכן, ב-**PowerShell מוגבה** (הרצה כמנהל), הציגו את הכללים הקיימים, מחקו רק את כלל ה-Lemonade הישן, והוסיפו כלל חדש עם כתובת ה-IP הנוכחית:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

בפלט של `show all`, כלל ה-Lemonade הישן הוא הרשומה שכתובת ה-connect שלה היא `127.0.0.1` בפורט `13305`; כתובת ה-listen שלה היא `<old-WSL-Gateway-IP>` שלכם. מחיקה לפי כתובת זו מסירה רק את הכלל הזה ומשאירה כל כללי port-proxy אחרים במחשב שלכם ללא שינוי.

כלל חומת האש שהוספתם במהלך ההגדרה מקושר לפורט `13305` (ולא לכתובת ה-IP), כך שהוא ממשיך לפעול ולא צריך ליצור אותו מחדש.

> **המלצה:** כדי להימנע מבעיות שער, אנו ממליצים בחום על תצורת מעטפת הבאה:
> - **פקודות Windows** יש להריץ ב-**PowerShell**
> - **פקודות של הפצת WSL** יש להריץ ב-**Command Prompt** (הרצה כ-**מנהל**)

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## התקנה והגדרה של OpenClaw

### התקנת OpenClaw
<!-- @os:windows -->
> הריצו את הפקודות בסעיף זה בתוך **מסוף ה-WSL** שלכם.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

הדגל `--no-onboard` מדלג על אשף ההגדרה האינטראקטיבי, תגדירו את קצה ה-backend של המודל ידנית בשלב הבא, מה שנותן לכם שליטה מדויקת על אילו מודל ושרת בהם משתמשים.

פתחו מסוף חדש ואשרו את ההתקנה:

```bash
openclaw --version
```

> **טיפ:** אם אתם רואים `command not found` לאחר ההתקנה, הוסיפו את תיקיית ה-bin הגלובלית של npm ל-PATH שלכם:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> כדי להפוך זאת לקבוע, הוסיפו את השורה שלמעלה לקובץ `~/.bashrc` או `~/.zshrc` שלכם.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


### הגדרת OpenClaw לשימוש ב-Lemonade

הריצו את תהליך ההגדרה הלא-אינטראקטיבי של OpenClaw.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

פקודה זו כותבת את תצורת ה-OpenClaw אל `~/.openclaw/openclaw.json`.

> **קביעת גודל חלון ההקשר של OpenClaw:** הכיווץ (compaction) של OpenClaw מופעל כאשר `contextTokens > contextWindow − reserveTokens`. ברירת המחדל של `reserveTokensFloor` היא 20,000 טוקנים, רצפה שדורסת את `reserveTokens` כשהיא נמוכה יותר, כך שכל חלון הקשר של מודל שנמוך מ-~37 אלף יגרום ללולאת כיווץ אינסופית. הגדירו רזרבה נמוכה ובטלו את הרצפה פעם אחת בתצורה שלכם וזה יחול על כל מודל, ללא כיוונון פרטני לכל מודל:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` היא *רצפה* (הגנה מינימלית), לא הרזרבה עצמה, הגדרת הרצפה בלבד אינה משפיעה. `reserveTokensFloor: 0` מבטלת את ההגנה כך שה-`reserveTokens` הנמוך יותר מתקבל.

>
> **מתי להחיל זאת:** השתמשו בתצורה זו אם חלון ההקשר האפקטיבי של המודל שלכם נמוך מ-~37 אלף, בין אם משום שהמודל קטן (למשל 8 אלף, 16 אלף, 32 אלף) ובין אם משום שהגבלתם אותו בכוונה לערך נמוך יותר (למשל טעינת מודל של 128 אלף אך הגדרת ההקשר ל-16 אלף ב-Lemonade). בלעדיה, OpenClaw נכנס ללולאת כיווץ אינסופית בעת ההפעלה.
>
> **מודלים עם הקשר גדול בהקשר מלא:** ניתן לדלג על כל זה לחלוטין. ברירות המחדל עובדות היטב, הכיווץ יופעל הרבה לפני שהחלון מתמלא ולמודל יש די מקום ליצור תגובות ארוכות. אם בכל זאת תחילו זאת, שימו לב ש-`reserveTokens: 4096` מגביל את אורך התגובה לכ-4 אלף טוקנים, מה שעלול לקצץ יצירת קבצים ארוכה או תוכניות מפורטות.
>
> **היכן להוסיף זאת:** מקמו את בלוק ה-`compaction` בתוך `agents.defaults` ב-`openclaw.json` שלכם (בדרך כלל ב-`~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> שאר התצורה שלכם (gateway, ערוצים, מודלים וכו') נשארת ללא שינוי, יש להוסיף רק את המפתח `compaction`.
### (מומלץ) הפעלת ארגז חול (Sandboxing) של Docker

OpenClaw יכולה לנתב את כל פעולות הקבצים והקוד של הסוכן דרך מכל Docker מבודד במקום להריץ אותן ישירות על המחשב המארח שלכם. פעולה זו מגבילה את רדיוס ההשפעה של כל פעולה בלתי מכוונת לארגז החול בלבד, כך שמערכת הקבצים והרשת של המארח נשארות ללא פגע.

בנו את תמונת ארגז החול פעם אחת (יש להתקין Docker):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

הריצו את הפקודה הבאה כדי להוסיף את המפתח `sandbox` בתוך בלוק `agents.defaults` הקיים בקובץ `~/.openclaw/openclaw.json`:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

למכולות ארגז החול **אין גישה לרשת** כברירת מחדל. עיינו ב[מסמך ההתייחסות לארגז החול](https://docs.openclaw.ai/gateway/sandboxing) לגבי צירופי תיקיות (bind mounts) ושינויי גישת רשת.

> #### פתרון בעיות: Docker Permission Denied
> 
> אם מתקבלת שגיאת "permission denied" בעת הרצת פקודות Docker:
> 
> **שלב 1: הוספת המשתמש שלכם לקבוצת docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **שלב 2: אם השגיאה נמשכת, יש להחיל את התיקון הקבוע**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> לאחר מכן **הפעילו מחדש** את המערכת שלכם.
> 
> **תיקון זמני מהיר** (מתאפס לאחר הפעלה מחדש):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
## (מומלץ) שילוב OpenClaw עם שירותי Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) מספקת שירות סריקת אינטרנט וחילוץ תוכן בהתקנה עצמית (self-hosted) שיכול לעקוף אתגרים אלו ולשחרר את מלוא הפוטנציאל של האוטומציה של OpenClaw. 

בהגדרה זו, OpenClaw פועלת כערכת מכולות Docker המנוהלת באמצעות Podman. כדי לפשט את ניהול מחזור החיים ואת ההפעלה האוטומטית, אנו רושמים את Firecrawl כשירות `systemd` ברמת המשתמש, אשר מתזמר את ערימת ה-Podman Compose הבסיסית. הדבר מאפשר ל-OpenClaw להפעיל את השער (gateway), לעצור ולוודא את שירות Firecrawl באמצעות פקודות `systemctl --user` סטנדרטיות במקום לתקשר עם המכולות ישירות. 

כדי לשמור על הפשטות, פירקנו את התהליך כולו לארבעה שלבים:

---

### 1. רישום שירות המערכת
נווטו אל תיקיית הגדרות המשתמש של systemd:
```bash
cd ~/.config/systemd/user
```
צרו ופתחו קובץ חדש בשם `firecrawl.service`.
```bash
nano firecrawl.service
```
העתיקו והדביקו את התצורה הבאה:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
בשלב זה, השירות הוגדר אך עדיין לא נרשם ב-`systemd`. 
ודאו ששם הקובץ תואם בדיוק לזה שיצרתם למעלה, ולאחר מכן הריצו:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
אם ההרצה הצליחה, אמורה להופיע הפלט הבא:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 התיקייה `default.target.wants/` מכילה קישורים סימבוליים לשירותים המוגדרים להתחיל אוטומטית.

### 2. הגדרת Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) אידיאלי עבור מי שזקוקים לשליטה מלאה בסביבות הסריקה ועיבוד הנתונים שלהם, אך מגיע עם המחיר של מאמצי תחזוקה והגדרה נוספים.

התחילו בשכפול המאגר:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
צרו קובץ `.env` בתיקיית השורש `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. פריסת OpenClaw עם Podman Compose

לפני שממשיכים, ודאו שמשכתם את תמונת ה-Docker העדכנית ביותר של OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
לאחר שזה בוצע, הורידו את קובץ ה-Compose של OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) והניחו אותו בתיקיית השורש `/firecrawl`:

> מוסכמה זו נדרשת כדי ש-`systemd` יאתר ויפעיל את השירות כראוי, כפי שצוין ב-`WorkingDirectory=${HOME}/firecrawl`.

> תמיד אפשר להרחיב את הערימה על ידי הוספת שירותי Firecrawl נוספים בהתאם לצורך. הרשימה המלאה של השירותים הזמינים ניתן למצוא בקובץ הרשמי [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. הפעלת שירות OpenClaw דרך Firecrawl 

לפני מסירת השליטה ל-`systemd`, ודאו שהכול פועל כראוי על ידי הרצת הערימה ידנית:
```bash
podman compose -f openclaw-compose.yaml up -d
```
אם הכול מוגדר נכון, אמורה להופיע מכולת OpenClaw ופלט שורת הפקודה שלכם אמור להיראות בדומה לזה:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

לאחר האימות, הורידו את הערימה בחזרה לפני שממשיכים:
```bash
podman compose -f openclaw-compose.yaml down
```
לפני הפעלת השירות, עליכם לוודא שהבעלות וההרשאות הנכונות מוגדרות עבור תיקיית `firecrawl` וקובץ ה-`.env` שלה. 
זה חיוני כדי שהשירות יוכל לכתוב את פרטי הגישה שלכם בעת ההפעלה.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
כעת, לאחר שהכול אומת, הפעילו את השירות דרך `systemd`:
```bash
systemctl --user start firecrawl.service
```
[פעולות OpenClaw](https://docs.openclaw.ai/) נגישות מתוך המכולה האינטראקטיבית, ולוח הבקרה (Web Dashboard) זמין באותו מארח ופורט בכתובת http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### קבלת `OPENCLAW_GATEWAY_TOKEN` שלכם

לאחר שהשירות פועל, תבחינו בתיקיית `.openclaw` חדשה שנוצרה בתיקיית הבית שלכם (~/.openclaw). תיקייה זו נעולה כברירת מחדל, לכן תצטרכו לשחרר את הנעילה כדי לאחזר את אסימון השער (gateway token) שלכם.

1. הענקת גישה לתיקייה:
```bash
sudo chmod 777 ~/.openclaw/
```
2. קריאת אסימון השער שלכם:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
אתרו את הערך `OPENCLAW_GATEWAY_TOKEN` בפלט.

3. פתחו את לוח הבקרה של השער בדפדפן שלכם בכתובת http://127.0.0.1:18789. הדביקו את האסימון שלכם כאשר תתבקשו לאמת זהות.

כדי לעצור את השירות, הריצו:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## הפעלת שער ה-OpenClaw (Gateway)

השער הוא תהליך ה-OpenClaw שמנהל את לולאת הסוכן ומגיש את לוח הבקרה:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

כדי לפתוח את לוח הבקרה, הריצו את הפקודה הבאה במסוף שני בזמן שהשער עדיין פועל:

```bash
openclaw dashboard
```

מכיוון שהשער נקשר ל-loopback, לוח הבקרה מבצע אימות אוטומטי כאשר הוא נפתח מאותה מכונה, אין צורך בהזנת אסימון (token) או באישור מכשיר עבור גישה מקומית. אתם אמורים לראות את לוח הבקרה של OpenClaw כאשר מודל ה-Lemonade שלכם מופיע כ-backend הפעיל.

> אם הפעלתם sandboxing, ניתן לוודא זאת על ידי בקשה מהסוכן להריץ `run hostname` מלוח הבקרה. אם אתם רואים מזהה container קצר במקום שם המארח (hostname) של המכונה שלכם, ה-sandbox פועל כראוי.

**ברכות, בניתם ערימת סוכן AI מקומית לחלוטין מהיסוד.**

> **צריכים את אסימון השער (gateway token)?** הריצו `openclaw dashboard --no-open` כדי להדפיס את כתובת ה-URL של לוח הבקרה עם האסימון משובץ בתוכה (הפקודה גם מנסה להעתיק אותו ללוח ההעתקה שלכם). לחלופין, האסימון נמצא ב-`gateway.auth.token` בקובץ `~/.openclaw/openclaw.json`.

**גישה ללוח הבקרה ממכשיר אחר (דרך מנהרת SSH)**

אם ה-OpenClaw פועל על מכונה מרוחקת, ניתן להגיע ללוח הבקרה שלה מהמכונה המקומית שלכם דרך מנהרת SSH. המנהרה מעבירה את פורט השער (`18789`) כך שהדפדפן המקומי שלכם יכול לתקשר עם השער המרוחק דרך `127.0.0.1`.

1. מה**מכונה המקומית** שלכם, התחברו למכונה המרוחקת פעם אחת ואשרו את הודעת ה-fingerprint כדי שהמארח יתווסף לרשימת המארחים המוכרים שלכם:

   ```bash
   ssh user@<host-ip>
   ```

2. עדיין ב**מכונה המקומית** שלכם, פתחו את מנהרת ה-SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **הערה:** לאחר הזנת הסיסמה, המסוף לא מציג פלט ונראה כאילו הוא "תקוע". זה צפוי: הדגל (flag) `-N` מורה ל-SSH לא להריץ שום פקודה מרוחקת, כך שהוא פשוט משאיר את המנהרה פתוחה. השאירו את המסוף הזה פועל.

3. ב**מכונה המקומית** שלכם, פתחו דפדפן ועברו אל `http://127.0.0.1:18789`.

4. ב**מכונה המרוחקת**, הדפיסו את אסימון השער והדביקו אותו בדפדפן כדי להתחבר:

   ```bash
   openclaw dashboard --no-open
   ```

   פקודה זו מדפיסה את כתובת ה-URL של לוח הבקרה עם האסימון משובץ בתוכה; העתיקו את האסימון כדי להתחבר. (האסימון גם מאוחסן ב-`gateway.auth.token` בקובץ `~/.openclaw/openclaw.json`.)

> **אישור מכשיר מרוחק:** כאשר אתם פותחים את לוח הבקרה ממכונה אחרת או מטלפון, הדפדפן עשוי להציג מזהה בקשה. ב**מכונה המרוחקת**, הציגו את הבקשות הממתינות:
> ```bash
> openclaw devices list
> ```
> לאחר מכן אשרו את הבקשה המתאימה:
> ```bash
> openclaw devices approve <requestId>
> ```
> זה נדרש רק עבור מכשירים מרוחקים או משניים; גישת loopback מאותה מכונה מתאמתת אוטומטית. ראו את התיעוד [גישה מרוחקת](https://docs.openclaw.ai/gateway/remote) לפרטים נוספים.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## אופציונלי: חיבור ערוץ תקשורת

לאחר שהשער פועל, ניתן להגיע לסוכן המקומי שלכם מכל מכשיר. בחרו את האפשרות המתאימה להגדרה שלכם. OpenClaw תומך ב-[Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), וערוצים נוספים, ראו את הרשימה המלאה ב-[docs.openclaw.ai](https://docs.openclaw.ai).

---

### אפשרות א': Discord

Discord דורש שרת שבו יש לכם **גישת מנהל (administrator)**כדי להוסיף בוט. אם אתם משתפים שרתים אך אינכם הבעלים של אף אחד מהם, השתמשו באפשרות ב' (Telegram) במקום זאת.

#### יצירת חשבון ושרת Discord

אם אין לכם חשבון Discord, הירשמו ב-[discord.com](https://discord.com). אתם גם צריכים שרת שבו אתם מנהלים, צרו אחד על ידי לחיצה על סמל ה-**+** בסרגל הצד של Discord ובחירת **Create My Own**. שרת פרטי מתאים לכך.

#### יצירת אפליקציה ובוט ב-Discord

1. עברו אל [Discord Developer Portal](https://discord.com/developers/applications) ולחצו על **New Application**. תנו לו שם (למשל "openclaw-bot").
2. בסרגל הצד, לחצו על **Bot**. הגדירו שם משתמש לבוט.
3. עדיין בעמוד ה-Bot, גללו אל **Privileged Gateway Intents** והפעילו:
   - **Message Content Intent** (נדרש)
   - **Server Members Intent** (מומלץ)
4. גללו למעלה שוב ולחצו על **Reset Token** כדי ליצור את אסימון הבוט שלכם. העתיקו אותו.

#### הוספת הבוט לשרת שלכם

1. בסרגל הצד, לחצו על **OAuth2/ URL Generator**.
2. תחת **Scopes**, הפעילו `bot` ו-`applications.commands`.
3. תחת **Bot Permissions**, הפעילו: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. העתיקו את כתובת ה-URL שנוצרה, הדביקו אותה בדפדפן שלכם, בחרו את השרת שלכם, ואשרו. הבוט אמור להופיע כעת ברשימת החברים של השרת שלכם.

#### איסוף המזהים שלכם

הפעילו את מצב המפתחים (Developer Mode) ב-Discord (**User Settings/ Advanced/ Developer Mode**), ואז:
- לחיצה ימנית על סמל השרת שלכם: **Copy Server ID**
- לחיצה ימנית על התמונה האישית שלכם: **Copy User ID**

#### אפשרו הודעות פרטיות (DMs) מחברי השרת

לחיצה ימנית על סמל השרת שלכם/ **Privacy Settings**/ הפעילו את **Direct Messages**. זה מאפשר לבוט לשלוח לכם הודעה פרטית (DM), מה שנדרש עבור שלב ההתאמה (pairing).

#### הגדרת OpenClaw עבור Discord

שמרו את אסימון הבוט שלכם כמשתנה סביבה, ואז צרו קובץ תיקון (patch) יחיד שמפעיל את Discord, מתייחס לאסימון, ומוסיף את השרת שלכם לרשימת ההיתרים (allowlist). החליפו את `<server_id>` ו-`<user_id>` במזהים שנאספו לעיל.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **אל תסתמכו על בקשה מהסוכן להגדיר זאת.** כאשר sandboxing מופעל, הסוכן לא יכול לכתוב אל `~/.openclaw/openclaw.json` מתוך ה-sandbox, השתמשו בפקודות ה-CLI שלעיל על המארח (host) במקום זאת.

הפעילו מחדש את השער כדי שהוא יטען את הגדרות הערוץ החדשות:

```bash
openclaw gateway run --bind loopback --port 18789
```

אתם אמורים לראות `logged in to discord as <bot-name>` בפלט השער תוך מספר שניות.
#### חברו את חשבון ה-Discord שלכם

שלחו הודעה פרטית (DM) לבוט ב-Discord. הוא ישיב עם קוד צימוד קצר.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

אשרו זאת במכונה שמריצה את OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> קודי צימוד פגים לאחר שעה.

כעת תוכלו לשוחח עם הסוכן שלכם ישירות מ-Discord ולהעביר משימות לחומרה המקומית שלכם.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### אפשרות B: Telegram

Telegram פשוט יותר מ-Discord עבור רוב המשתמשים, הוא לא דורש שרת ולא דורש הרשאות ניהול.

#### יצירת בוט ב-Telegram

1. פתחו את Telegram ושלחו הודעה ל-**@BotFather**.
2. שלחו `/newbot` ופעלו לפי ההנחיות. שמרו את אסימון הבוט (bot token) שהוא מספק.

#### הגדרת OpenClaw עבור Telegram

שמרו את האסימון כמשתנה סביבה:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

הוסיפו את תצורת הערוץ אל `~/.openclaw/openclaw.json` (או עדכנו אותה דרך לוח הבקרה):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

הפעילו מחדש את השער (gateway), ולאחר מכן שלחו לבוט שלכם הודעה כלשהי ב-Telegram. אשרו את הצימוד:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

קודי צימוד פגים לאחר שעה. כעת תוכלו לשוחח עם הסוכן שלכם דרך הודעה פרטית ב-Telegram.

---

## הצעדים הבאים

עכשיו שהסוכן שלכם יכול לקבל פקודות מהטלפון שלכם ולפעול על המכונה המקומית שלכם, הנה שלושה כיוונים ששווה לבחון:

1. **מסכם שוק המניות**: תזמנו את OpenClaw לשלוף נתונים מממשקי API פיננסיים במרווחי זמן קבועים, לסכם את תנודות היום עם המודל המקומי שלכם, ולשלוח תקציר לטלפון שלכם כל בוקר דרך הערוץ שבחרתם.

2. **מוניטור כיוונון עדין (fine-tuning)**: הפעילו עבודת אימון מרחוק דרך Telegram או Discord, ותנו לסוכן לעקוב אחר יומן האימון (training log) ולדווח בחזרה לטלפון שלכם על ערכי אובדן (loss) תקופתיים, ניצול GPU ושימוש בדיסק. אם ההרצה נתקעת או שיש קפיצה בשימוש ב-VRAM, תדעו על כך מיד מבלי שתצטרכו להיות ליד המכונה.

3. **IOT עם VLM מקומי**: כוונו מצלמה לדלת הכניסה שלכם, הריצו מודל ראייה על Lemonade, ותנו ל-OpenClaw לנתח פריימים לפי דרישה או לפי טריגר. שאלו "האם הגיעו חבילות היום?" מהטלפון שלכם וקבלו תשובה ישירה מהחומרה שלכם.

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->