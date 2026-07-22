<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם אוטומטית מאנגלית ולא נבדק על ידי אדם. הוא עשוי להכיל שגיאות, וייתכן שחלק מהשלבים, הפקודות, ההורדות או זמינות המוצר יהיו שונים בשפה או באזור שלך. אם משהו נראה שגוי, יש להתייחס אל ה-playbook המקורי באנגלית כמקור האמין.
<!-- auto-translated-disclaimer:end -->

# הפעלת OpenClaw עם Lemonade Server כשרת עורפי (Backend)

## סקירה כללית

[**OpenClaw**](https://openclaw.ai/) הוא סוכן AI אוטונומי שיכול לכתוב ולהריץ קוד, לנהל קבצים ולבצע משימות מורכבות מרובות שלבים מטעמכם. בניגוד לעוזר צ'אט שרק עונה על שאלות, OpenClaw מבצע פעולות ממשיות על המערכת שלכם, כלומר הוא זקוק לשרת עורפי AI מהיר ומסוגל שיוכל לעמוד בקצב של לולאת סוכן תובענית.

[**Lemonade Server**](https://lemonade-server.ai/) הוא בדיוק השרת העורפי הזה. מדובר בשרת הסקה מקומי בקוד פתוח שמריץ מודלי GenAI ישירות על החומרה שלכם וחושף אותם דרך תקן ה-API של OpenAI המקובל בתעשייה.

יחד, השניים יוצרים מחסנית סוכן AI מקומית לחלוטין: Lemonade מטפל בהסקת המודל, ו-OpenClaw מספק את לולאת הסוכן שהופכת את פלטי המודל לפעולות ממשיות.

> **לפני שתמשיכו:** OpenClaw הוא סוכן AI אוטונומי מאוד. מתן גישה לכל סוכן AI למערכת שלכם עלול לגרום לתוצאות בלתי צפויות או בלתי מכוונות. המשיכו רק אם אתם מבינים את הסיכונים ונוח לכם עם תוכנה אוטונומית הפועלת מטעמכם.

---

## מה תלמדו

בסיום מדריך זה תוכלו:

- ללמוד על **Lemonade Server**
- **להתקין את OpenClaw** ו**להצביע עליו לעבר Lemonade Server** כשרת העורפי של ה-AI שלו.
- **להפעיל את שער (gateway) OpenClaw** ולוודא שהסוכן שלכם מוכן לעבודה.
- **לחבר ערוץ תקשורת** (Discord או Telegram) כדי שתוכלו לשוחח עם הסוכן שלכם מכל מכשיר.

---

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מקדימות

<!-- @os:linux -->
- מחשב שמריץ **Ubuntu 24.04+** או הפצת לינוקס מבוססת Debian תואמת עם `apt-get`
- לפחות **12GB זיכרון RAM** (מומלץ 64GB+ עבור מודלים גדולים יותר)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (אופציונלי, לצורך הפעלת OpenClaw בסביבת sandbox)

- **כ-10–30GB שטח דיסק פנוי** לקבצי משקלי המודל
<!-- @os:end -->
<!-- @os:windows -->
- מחשב שמריץ **Windows 10/11**
- לפחות **12GB זיכרון RAM** (מומלץ 64GB+ עבור מודלים גדולים יותר)
- **כ-10–30GB שטח דיסק פנוי** לקבצי משקלי המודל
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (אופציונלי, לצורך הפעלת OpenClaw בסביבת sandbox)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## משיכת (Pull) וטעינת המודל המומלץ

המודל המומלץ למדריך זה הוא **Qwen3.6-35B-A3B-GGUF** מבית Unsloth, מודל MoE חזק עם חלון הקשר (context) של 263 אלף טוקנים, המתאים היטב לעומסי עבודה של סוכנים. מודל זה משתמש בכימות (quantization) מסוג UD-Q4_K_XL. משכו אותו כעת:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

לאחר מכן טענו אותו עם חלון הקשר גדול ושמרו הגדרה זו להרצות עתידיות:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

למודל אורך הקשר ברירת מחדל של 262,144 טוקנים. אם נתקלים בשגיאות של חוסר זיכרון (OOM), שקלו להקטין את חלון ההקשר. עם זאת, מכיוון ש-Qwen3.6 מנצל הקשר מורחב עבור משימות מורכבות, אנו ממליצים לשמור על אורך הקשר של לפחות 128K טוקנים כדי לשמר את יכולות החשיבה.

> **טיפ: השבתת מצב חשיבה לתגובות סוכן מהירות יותר:** Qwen3.6-35B-A3B פועל במצב חשיבה כברירת מחדל, מה שמוסיף זמן השהיה (latency) לפני כל תגובה. עבור לולאות סוכן, עלות זו מצטברת במהירות. המאגר [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) מספק תצורה מוכנה מראש שמשביתה את מצב החשיבה. כדי להשתמש בה, הורידו את הקובץ וייבאו אותו:
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

אנו מריצים את OpenClaw בתוך WSL (מומלץ) ומחברים אותו ל-Lemonade הרץ באופן טבעי (native) על Windows. כך מתקבלת סביבת מעטפת לינוקס עבור OpenClaw, תוך שמירה על האצת ה-GPU של Lemonade בצד Windows.

### התקנת WSL ו-Ubuntu

פתחו את PowerShell כמנהל (Administrator) והתקינו את גרעין ה-WSL:

```powershell
wsl --install --no-distribution
```

לאחר מכן התקינו את Ubuntu:

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

הפעילו מחדש את WSL:

```powershell
wsl --shutdown
wsl
```

### גישור בין Lemonade ב-Windows לבין WSL

WSL2 פועל ברשת וירטואלית. Lemonade על Windows נקשר לכתובת `127.0.0.1`, שאליה WSL אינו יכול להגיע ישירות. פרוקסי פורט (port proxy) של Windows מעביר תעבורה מכתובת ה-IP של שער ה-WSL אל localhost של Windows.

**מצאו את כתובת ה-IP של שער ה-WSL שלכם** (הריצו בתוך WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**הוסיפו את פרוקסי הפורט** (הריצו ב-PowerShell כמנהל, והחליפו את `<WSL-Gateway-IP>` בכתובת ה-IP של שער ה-WSL שלכם):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**הוסיפו כלל חומת אש (Firewall)** (אותו חלון PowerShell מוגבה):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**אמתו מתוך WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

אם כבר טענתם את מודל Qwen3.6-35B-A3B-GGUF בשלב הקודם, אתם אמורים לראות פלט JSON כמו זה:

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

> כלל ה-`netsh portproxy` שורד הפעלות מחדש, אך כתובת ה-IP של שער ה-WSL עשויה להשתנות לאחר `wsl --shutdown`. אם Lemonade הופך לבלתי נגיש מ-WSL לאחר הפעלה מחדש, קבלו את כתובת השער המעודכנת ועדכנו את הפרוקסי בכתובת החדשה.

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

הדגל `--no-onboard` מדלג על אשף ההתקנה האינטראקטיבי, ותגדירו את שרת המודל העורפי (backend) באופן ידני בשלב הבא, מה שמעניק לכם שליטה מדויקת על המודל והשרת שבהם נעשה שימוש.

פתחו מסוף חדש ואמתו את ההתקנה:

```bash
openclaw --version
```

> **טיפ:** אם מופיע `command not found` לאחר ההתקנה, הוסיפו את תיקיית ה-bin הגלובלית של npm ל-PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> כדי להפוך שינוי זה לקבוע, הוסיפו את השורה שלמעלה לקובץ ה-`~/.bashrc` או ה-`~/.zshrc` שלכם.

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

הריצו את תהליך ה-onboarding הלא-אינטראקטיבי של OpenClaw.
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

פקודה זו כותבת את הגדרות התצורה של OpenClaw אל `~/.openclaw/openclaw.json`.

> **גודל חלון ההקשר של OpenClaw:** דחיסת ההקשר (compaction) של OpenClaw מופעלת כאשר `contextTokens > contextWindow − reserveTokens`. ברירת המחדל של `reserveTokensFloor` היא 20,000 טוקנים, רצפה שגוברת על `reserveTokens` כאשר הערך שלו נמוך יותר, כך שכל הקשר מודל מתחת ל-~37 אלף טוקנים יגרום ללולאת דחיסה אינסופית. הגדירו רזרבה נמוכה והשביתו את הרצפה פעם אחת בתצורה שלכם, וההגדרה תחול על כל מודל, ללא צורך בכיוונון פרטני לכל מודל:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` הוא *רצפה* (הגנת מינימום), ולא הרזרבה עצמה - הגדרת הרצפה בלבד לא תשפיע. `reserveTokensFloor: 0` משביתה את ההגנה כך שהערך הנמוך יותר של `reserveTokens` יתקבל.
>
> **מתי להחיל זאת:** השתמשו בתצורה זו אם חלון ההקשר האפקטיבי של המודל שלכם נמוך מ-~37 אלף, בין אם מדובר במודל קטן (למשל 8 אלף, 16 אלף, 32 אלף) ובין אם הגבלתם אותו במכוון לערך נמוך יותר (למשל טעינת מודל של 128 אלף אך הגדרת ההקשר ל-16 אלף ב-Lemonade). ללא זה, OpenClaw תיכנס ללולאת דחיסה אינסופית עם ההפעלה.
>
> **מודלים עם הקשר גדול בהקשר מלא:** ניתן לדלג על כך לחלוטין. ברירות המחדל עובדות היטב, הדחיסה תופעל הרבה לפני שהחלון יתמלא ולמודל יהיה מספיק מקום ליצור תגובות ארוכות. אם בכל זאת תחילו זאת, שימו לב ש-`reserveTokens: 4096` מגבילה את אורך התגובה לכ-4 אלף טוקנים, מה שעלול לחתוך יצירת קבצים ארוכה או תוכניות מפורטות.
>
> **היכן להוסיף זאת:** מקמו את בלוק ה-`compaction` בתוך `agents.defaults` בקובץ `openclaw.json` שלכם (בדרך כלל בנתיב `~/.openclaw/openclaw.json`):
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
> שאר התצורה שלכם (gateway, channels, models וכו') נותרת ללא שינוי, יש להוסיף רק את המפתח `compaction`.

### (מומלץ) הפעלת ארגז חול (Sandboxing) של Docker

OpenClaw יכולה לנתב את כל פעולות הקבצים והקוד של הסוכן דרך מכולת Docker מבודדת במקום להריץ אותן ישירות על המארח שלכם. פעולה זו מגבילה את רדיוס ההשפעה של כל פעולה לא מכוונת לארגז החול, ומשאירה את מערכת הקבצים והרשת של המארח ללא פגיעה.

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

הריצו זאת כדי להוסיף את המפתח `sandbox` בתוך בלוק ה-`agents.defaults` הקיים בקובץ `~/.openclaw/openclaw.json`:

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

למכולות ארגז החול **אין גישה לרשת** כברירת מחדל. עיינו ב[מסמך ההפניה לארגז חול](https://docs.openclaw.ai/gateway/sandboxing) לקבלת מידע על הרכבות (bind mounts) והתאמות רשת.

> #### פתרון בעיות: הרשאה נדחתה ב-Docker
> 
> אם מתקבלת שגיאת "permission denied" בעת הרצת פקודות Docker:
> 
> **שלב 1: הוסיפו את המשתמש שלכם לקבוצת docker**
> 
> ```bash
> sudo groupadd docker                    # יצירת הקבוצה במידת הצורך
> sudo usermod -aG docker $USER           # הוספת עצמכם לקבוצה
> newgrp docker                           # הפעלת השינוי
> docker run hello-world                  # בדיקה
> ```
> 
> **שלב 2: אם השגיאה נמשכת, החילו את התיקון הקבוע**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> לאחר מכן **אתחלו** את המערכת.
> 
> **תיקון זמני מהיר** (מתאפס לאחר אתחול):
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

[Firecrawl](https://docs.firecrawl.dev/introduction) מספקת שירות זחילת אינטרנט וחילוץ תוכן המתארח באופן עצמאי, שיכול לעקוף אתגרים אלו ולשחרר את מלוא הפוטנציאל של אוטומציית OpenClaw.

בהגדרה זו, OpenClaw פועלת כקבוצה של מכולות Docker המנוהלות באמצעות Podman. כדי לפשט את ניהול מחזור החיים ואת ההפעלה האוטומטית, אנו רושמים את Firecrawl כשירות `systemd` ברמת המשתמש שמתאם את ערמת ה-Podman Compose הבסיסית. פעולה זו מאפשרת ל-OpenClaw להפעיל את ה-gateway, לעצור ולוודא את שירות Firecrawl באמצעות פקודות `systemctl --user` סטנדרטיות במקום לתקשר ישירות עם המכולות.

כדי לשמור על הפשטות, פירקנו את התהליך כולו לארבעה שלבים:

---

### 1. רישום שירות המערכת
נווטו לתיקיית תצורת המשתמש של systemd:
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
בשלב זה, השירות הוגדר אך טרם נרשם ב-`systemd`.
ודאו ששם הקובץ תואם בדיוק למה שיצרתם למעלה, ולאחר מכן הריצו:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
אם ההרצה הצליחה, אמורה להופיע הפלט הבא:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

תיקיית `default.target.wants/` מכילה קישורים סימבוליים לשירותים המוגדרים להפעלה אוטומטית.
### 2. הגדרת Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) מתאים באופן אידיאלי למי שזקוקים לשליטה מלאה בסביבות הסריקה ועיבוד הנתונים שלהם, אך מגיע עם עלות של מאמצי תחזוקה והגדרה נוספים.

התחילו בשכפול המאגר:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
צרו `.env` בתיקיית השורש `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. פריסת OpenClaw עם Podman Compose

לפני שממשיכים הלאה, ודאו שמשכתם את תמונת ה-Docker העדכנית ביותר של OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
לאחר שזה הושלם, הורידו את קובץ ה-Compose של OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) ומקמו אותו בתיקיית השורש `/firecrawl`:

> מוסכמה זו נדרשת כדי ש-`systemd` יאתר ויפעיל את השירות כראוי, כפי שמצוין ב-`WorkingDirectory=${HOME}/firecrawl`.

> תמיד תוכלו להרחיב את המחסנית על ידי הוספת שירותי Firecrawl נוספים לפי הצורך. הרשימה המלאה של השירותים הזמינים נמצאת בקובץ הרשמי [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. הפעלת שירות OpenClaw דרך Firecrawl 

לפני העברת השליטה ל-`systemd`, ודאו שהכל עובד כראוי על ידי הרצת המחסנית באופן ידני:
```bash
podman compose -f openclaw-compose.yaml up -d
```
אם הכל מוגדר כראוי, אמורים לראות את מכולת ה-OpenClaw עולה, ופלט שורת הפקודה שלכם אמור להיראות בדומה לזה:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

לאחר האימות, החזירו את המחסנית למצב כבוי לפני שממשיכים:
```bash
podman compose -f openclaw-compose.yaml down
```
לפני הפעלת השירות, עליכם לוודא שהבעלות וההרשאות הנכונות מוגדרות עבור תיקיית `firecrawl` וקובץ ה-`.env` שלה. 
זהו דבר חיוני על מנת שהשירות יוכל לכתוב את פרטי הכניסה שלכם בעת ההפעלה.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
כעת, לאחר שהכל אומת, הפעילו את השירות דרך `systemd`:
```bash
systemctl --user start firecrawl.service
```
[פעולות ה-OpenClaw](https://docs.openclaw.ai/) נגישות מתוך המכולה האינטראקטיבית, ולוח הבקרה האינטרנטי זמין באותו מארח ופורט בכתובת http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### קבלת ה-`OPENCLAW_GATEWAY_TOKEN` שלכם

לאחר שהשירות עולה ופועל, תבחינו בתיקיית `.openclaw` חדשה שנוצרה בתיקיית הבית שלכם (~/.openclaw). תיקייה זו נעולה כברירת מחדל, לכן תצטרכו לפתוח אותה כדי לאחזר את אסימון השער (gateway token) שלכם.

1. הענקת גישה לתיקייה:
```bash
sudo chmod 777 ~/.openclaw/
```
2. קריאת אסימון השער שלכם:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
אתרו את הערך `OPENCLAW_GATEWAY_TOKEN` בפלט.

3. פתחו את לוח הבקרה של השער בדפדפן שלכם בכתובת http://127.0.0.1:18789. הדביקו את האסימון שלכם כאשר תתבקשו לאמת.

כדי לעצור את השירות, הריצו:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## הפעלת שער ה-OpenClaw (Gateway)

השער הוא תהליך ה-OpenClaw המנהל את לולאת הסוכן ומגיש את לוח הבקרה:

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

כדי לפתוח את לוח הבקרה, הריצו את הפקודה הבאה במסוף שני בעוד השער עדיין פועל:

```bash
openclaw dashboard
```

מכיוון שהשער מתחבר ל-loopback, לוח הבקרה מאמת אוטומטית כאשר הוא נפתח מאותו מחשב, ואין צורך בהזנת אסימון או אישור מכשיר עבור גישה מקומית. אמורים לראות את לוח הבקרה של OpenClaw עם דגם ה-Lemonade שלכם רשום כרכיב הקצה הפעיל (backend).

> אם הפעלתם sandboxing, תוכלו לוודא זאת על ידי בקשה מהסוכן להריץ `run hostname` מלוח הבקרה. אם אתם רואים מזהה מכולה קצר במקום שם המארח של המחשב שלכם, סימן שהסביבה המבודדת (sandbox) פועלת.

**ברכות, בניתם מחסנית סוכן AI מקומית לחלוטין מאפס.**

> **זקוקים לאסימון השער?** הריצו `openclaw dashboard --no-open` כדי להדפיס את כתובת ה-URL של לוח הבקרה עם האסימון משובץ בתוכה (הפקודה גם מנסה להעתיק אותו ללוח (clipboard) שלכם). לחלופין, האסימון נמצא תחת `gateway.auth.token` בקובץ `~/.openclaw/openclaw.json`.
>
> **אישור מכשיר מרוחק:** כאשר אתם פותחים את לוח הבקרה ממחשב שני או טלפון, הדפדפן מציג מזהה בקשה (request ID). בחזרה במחשב המריץ את השער, הריצו:
> ```bash
> openclaw devices approve <requestId>
> ```
> הדבר נדרש רק עבור מכשירים מרוחקים או משניים, גישת loopback מאותו מחשב מאמתת באופן אוטומטי.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## אופציונלי: חיבור ערוץ תקשורת

לאחר שהשער פועל, תוכלו להגיע לסוכן המקומי שלכם מכל מכשיר. בחרו את האפשרות המתאימה להגדרה שלכם. OpenClaw תומך ב-[Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), ובערוצים נוספים, ראו את הרשימה המלאה בכתובת [docs.openclaw.ai](https://docs.openclaw.ai).

---

### אפשרות א': Discord

Discord דורש שרת שבו **יש לכם גישת מנהל**, כדי להוסיף בוט. אם אתם משתפים שרתים אך לא בבעלותכם אף אחד מהם, השתמשו באפשרות ב' (Telegram) במקום זאת.

#### יצירת חשבון ושרת Discord

אם אין לכם חשבון Discord, הירשמו בכתובת [discord.com](https://discord.com). כמו כן, תזדקקו לשרת שבו אתם מנהל; צרו אחד על ידי לחיצה על סמל ה-**+** בסרגל הצד של Discord ובחירת **Create My Own**. שרת פרטי מספיק.

#### יצירת אפליקציית ובוט Discord

1. גשו אל [פורטל המפתחים של Discord](https://discord.com/developers/applications) ולחצו על **New Application**. תנו לה שם (למשל, "openclaw-bot").
2. בסרגל הצד, לחצו על **Bot**. הגדירו שם משתמש עבור הבוט.
3. עדיין בעמוד ה-Bot, גללו אל **Privileged Gateway Intents** והפעילו:
   - **Message Content Intent** (חובה)
   - **Server Members Intent** (מומלץ)
4. גללו חזרה למעלה ולחצו על **Reset Token** כדי ליצור את אסימון הבוט שלכם. העתיקו אותו.

#### הוספת הבוט לשרת שלכם

1. בסרגל הצד, לחצו על **OAuth2/ URL Generator**.
2. תחת **Scopes**, הפעילו את `bot` ו-`applications.commands`.
3. תחת **Bot Permissions**, הפעילו: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. העתיקו את כתובת ה-URL שנוצרה, הדביקו אותה בדפדפן שלכם, בחרו את השרת שלכם, ואשרו. הבוט אמור להופיע כעת ברשימת החברים של השרת שלכם.
#### אספו את המזהים שלכם

הפעילו מצב מפתחים בדיסקורד (**הגדרות משתמש/ מתקדם/ מצב מפתחים**), ולאחר מכן:
- לחצו לחיצה ימנית על אייקון השרת שלכם: **העתקת מזהה שרת**
- לחצו לחיצה ימנית על התמונה שלכם: **העתקת מזהה משתמש**

#### אפשרו הודעות פרטיות מחברי השרת

לחצו לחיצה ימנית על אייקון השרת שלכם/ **הגדרות פרטיות**/ הפעילו את **הודעות ישירות**. פעולה זו מאפשרת לבוט לשלוח לכם הודעה פרטית, מה שנדרש עבור שלב ההתאמה.

#### הגדירו את OpenClaw עבור דיסקורד

שמרו את טוקן הבוט שלכם כמשתנה סביבה, ולאחר מכן צרו קובץ תיקון (patch) יחיד שמפעיל את דיסקורד, מפנה לטוקן, ומוסיף את השרת שלכם לרשימת ההיתרים. החליפו את `<server_id>` ו-`<user_id>` במזהים שנאספו לעיל.

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

> **אל תסתמכו על בקשה מהסוכן להגדיר זאת.** כאשר ה-sandbox מופעל, הסוכן אינו יכול לכתוב אל `~/.openclaw/openclaw.json` מתוך ה-sandbox, השתמשו בפקודות ה-CLI שלמעלה על המכונה המארחת במקום זאת.

הפעילו מחדש את ה-gateway כדי שיטען את הגדרת הערוץ החדשה:

```bash
openclaw gateway run --bind loopback --port 18789
```

אתם אמורים לראות `logged in to discord as <bot-name>` בפלט ה-gateway תוך מספר שניות.

#### התאימו את חשבון הדיסקורד שלכם

שלחו הודעה פרטית לבוט בדיסקורד. הוא ישיב עם קוד התאמה קצר.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

אשרו זאת במחשב שמריץ את OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> קודי התאמה פגי תוקף לאחר שעה.

כעת תוכלו לשוחח עם הסוכן שלכם ישירות מדיסקורד ולהעביר משימות לחומרה המקומית שלכם.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### אפשרות ב': טלגרם

טלגרם פשוט יותר מדיסקורד עבור רוב המשתמשים, הוא אינו דורש שרת ואינו דורש הרשאות ניהול.

#### צרו בוט טלגרם

1. פתחו את טלגרם ושלחו הודעה ל-**@BotFather**.
2. שלחו `/newbot` ועקבו אחר ההנחיות. שמרו את טוקן הבוט שהוא נותן לכם.

#### הגדירו את OpenClaw עבור טלגרם

שמרו את הטוקן כמשתנה סביבה:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

הוסיפו את הגדרת הערוץ ל-`~/.openclaw/openclaw.json` (או תקנו אותה דרך לוח הבקרה):

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

הפעילו מחדש את ה-gateway, ולאחר מכן שלחו לבוט שלכם הודעה כלשהי בטלגרם. אשרו את ההתאמה:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

קודי התאמה פגי תוקף לאחר שעה. כעת תוכלו לשוחח עם הסוכן שלכם דרך הודעה פרטית בטלגרם.

---

## הצעדים הבאים

עכשיו כשהסוכן שלכם יכול לקבל פקודות מהטלפון שלכם ולפעול על המכונה המקומית שלכם, הנה שלושה כיוונים ששווה לחקור:

1. **מסכם שוק המניות**: תזמנו את OpenClaw לשלוף נתונים מממשקי API פיננסיים במרווח קבוע, סכמו את תנועות היום עם המודל המקומי שלכם, ושלחו תקציר לטלפון שלכם כל בוקר דרך הערוץ שבחרתם.

2. **מעקב אחר כיוונון עדין**: הפעילו משימת אימון מרחוק דרך טלגרם או דיסקורד, ואז תנו לסוכן לעקוב אחר לוג האימון ולדווח על ערכי אובדן תקופתיים, ניצול GPU, ושימוש בדיסק בחזרה לטלפון שלכם. אם הריצה נתקעת או ה-VRAM קופץ, תדעו על כך מיד בלי צורך להיות ליד המכונה.

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