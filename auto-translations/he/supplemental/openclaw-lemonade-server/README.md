<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# הפעלת OpenClaw עם Lemonade Server כ-backend

## סקירה כללית

[**OpenClaw**](https://openclaw.ai/) הוא סוכן AI אוטונומי שיכול לכתוב ולהריץ קוד, לנהל קבצים ולבצע משימות מורכבות מרובות שלבים בשמכם. בניגוד לעוזר צ'אט שרק עונה על שאלות, OpenClaw מבצע פעולות אמיתיות במערכת שלכם, מה שאומר שהוא זקוק ל-backend מהיר ומסוגל של AI שיכול לעמוד בקצב של לולאת סוכן תובענית.

[**Lemonade Server**](https://lemonade-server.ai/) הוא ה-backend הזה. זהו שרת הסקה (inference) מקומי בקוד פתוח שמריץ מודלי GenAI ישירות על החומרה שלכם וחושף אותם דרך ה-API בתקן התעשייתי של OpenAI.

יחד, הם יוצרים מחסנית סוכן AI מקומית לחלוטין: Lemonade מטפל בהסקת המודל, ו-OpenClaw מספק את לולאת הסוכן שהופכת את פלטי המודל לפעולות אמיתיות.

> **לפני שתמשיכו:** OpenClaw הוא סוכן AI אוטונומי מאוד. מתן גישה לכל סוכן AI למערכת שלכם עלול לגרום לתוצאות בלתי צפויות או בלתי מכוונות. המשיכו רק אם אתם מבינים את הסיכונים ומרגישים בנוח עם תוכנה אוטונומית הפועלת בשמכם.

---

## מה תלמדו

בסוף מדריך זה תוכלו:

- ללמוד על **Lemonade Server**
- **להתקין את OpenClaw** ו**להפנות אותו ל-Lemonade Server** כ-backend של ה-AI שלו.
- **להפעיל את שער ה-gateway של OpenClaw** ולוודא שהסוכן שלכם מוכן לעבודה.
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
- מחשב שמריץ **Ubuntu 24.04+** או הפצת לינוקס תואמת מבוססת Debian עם `apt-get`
- לפחות **12 GB זיכרון RAM** (מומלץ 64GB+ עבור מודלים גדולים יותר)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (אופציונלי, לצורך sandboxing ל-OpenClaw)

- **כ-10–30 GB שטח דיסק פנוי** עבור משקלי המודל
<!-- @os:end -->
<!-- @os:windows -->
- מחשב שמריץ **Windows 10/11**
- לפחות **12 GB זיכרון RAM** (מומלץ 64GB+ עבור מודלים גדולים יותר)
- **כ-10–30 GB שטח דיסק פנוי** עבור משקלי המודל
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (אופציונלי, לצורך sandboxing ל-OpenClaw)
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

המודל המומלץ עבור מדריך זה הוא **Qwen3.6-35B-A3B-GGUF** מבית Unsloth, מודל MoE חזק עם חלון הקשר של 263,000 טוקנים, המתאים היטב לעומסי עבודה של סוכנים. מודל זה משתמש בקוונטיזציה מסוג UD-Q4_K_XL. משכו אותו כעת:

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

למודל יש אורך הקשר ברירת מחדל של 262,144 טוקנים. אם אתם נתקלים בשגיאות של חוסר זיכרון (OOM), שקלו להקטין את חלון ההקשר. עם זאת, מכיוון ש-Qwen3.6 מנצל הקשר מורחב עבור משימות מורכבות, אנו ממליצים לשמור על אורך הקשר של לפחות 128K טוקנים כדי לשמר את יכולות החשיבה.

> **טיפ: השביתו חשיבה לתגובות סוכן מהירות יותר:** Qwen3.6-35B-A3B פועל במצב חשיבה כברירת מחדל, מה שמוסיף השהיה לפני כל תגובה. עבור לולאות סוכן, תקורה זו מצטברת במהירות. המאגר [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) מספק תצורה מוכנה מראש שמשביתה את החשיבה. כדי להשתמש בה, הורידו את הקובץ וייבאו אותו:
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

אנו מריצים את OpenClaw בתוך WSL (מומלץ) ומחברים אותו ל-Lemonade הרץ באופן טבעי על Windows. כך מתקבלת סביבת מעטפת (shell) לינוקס עבור OpenClaw, תוך שמירה על האצת ה-GPU של Lemonade בצד Windows.

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

הריצו זאת בתוך מסוף ה-Ubuntu:

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

### גישור בין Lemonade ב-Windows ל-WSL

WSL2 פועל ברשת וירטואלית. Lemonade ב-Windows נקשר ל-`127.0.0.1`, אשר WSL אינו יכול להגיע אליו ישירות. proxy של פורטים ב-Windows מעביר תעבורה משער ה-gateway של WSL אל localhost של Windows.

**מצאו את כתובת ה-IP של שער ה-WSL** (הריצו בתוך WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**הוסיפו את ה-port proxy** (הריצו ב-PowerShell כמנהל, והחליפו את `<WSL-Gateway-IP>` בכתובת ה-IP של שער ה-WSL שלכם):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**הוסיפו כלל חומת אש (firewall)** (אותו PowerShell מוגבה):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**וודאו מ-WSL**:

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

> כלל ה-`netsh portproxy` שורד הפעלות מחדש, אך כתובת ה-IP של שער ה-WSL עשויה להשתנות לאחר `wsl --shutdown`. אם Lemonade הופך לבלתי נגיש מ-WSL לאחר הפעלה מחדש, קבלו את כתובת ה-gateway המעודכנת ועדכנו את ה-proxy עם כתובת ה-IP החדשה הזו.

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

## התקנה והגדרת OpenClaw

### התקנת OpenClaw
<!-- @os:windows -->
> הריצו את הפקודות בסעיף זה בתוך **מסוף ה-WSL** שלכם.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

הדגל `--no-onboard` מדלג על אשף ההגדרה האינטראקטיבי, ותגדירו את ה-backend של המודל באופן ידני בשלב הבא, מה שמעניק לכם שליטה מדויקת על אילו מודל ושרת בשימוש.

פתחו מסוף חדש וודאו את ההתקנה:

```bash
openclaw --version
```

> **טיפ:** אם אתם רואים `command not found` לאחר ההתקנה, הוסיפו את ספריית ה-bin הגלובלית של npm ל-PATH שלכם:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> כדי להפוך זאת לקבוע, הוסיפו את השורה למעלה לקובץ `~/.bashrc` או `~/.zshrc` שלכם.

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

הריצו את תהליך ההטמעה הלא-אינטראקטיבי של OpenClaw.
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

פקודה זו כותבת את התצורה של OpenClaw אל `~/.openclaw/openclaw.json`.

> **גודל חלון ההקשר (context window) של OpenClaw:** מנגנון הכיווץ (compaction) של OpenClaw מופעל כאשר `contextTokens > contextWindow − reserveTokens`. ערך ברירת המחדל של `reserveTokensFloor` הוא 20,000 טוקנים, סף שדורס את `reserveTokens` כאשר הוא נמוך יותר, כך שכל חלון הקשר של מודל הנמוך מ-~37 אלף יגרום ללולאת כיווץ אינסופית. הגדירו רזרבה נמוכה והשביתו את הסף פעם אחת בתצורה שלכם, וההגדרה תחול על כל מודל, ללא צורך בכוונון פרטני לכל מודל:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` הוא *סף* (הגנת מינימום), ולא הרזרבה עצמה, הגדרת הסף בלבד לא תשפיע על כלום. `reserveTokensFloor: 0` משביתה את ההגנה כך שהערך הנמוך יותר של `reserveTokens` יתקבל.

>
> **מתי להחיל הגדרה זו:** השתמשו בתצורה זו אם חלון ההקשר האפקטיבי של המודל שלכם נמוך מ-~37 אלף, בין אם המודל קטן (למשל 8 אלף, 16 אלף, 32 אלף) ובין אם הגבלתם אותו בכוונה לערך נמוך יותר (למשל טעינת מודל עם חלון של 128 אלף אך הגדרת ההקשר ל-16 אלף ב-Lemonade). ללא הגדרה זו, OpenClaw ייכנס ללולאת כיווץ אינסופית עם ההפעלה.
>
> **מודלים עם חלון הקשר גדול בהקשר מלא:** ניתן לדלג על שלב זה לחלוטין. ברירות המחדל עובדות היטב, מנגנון הכיווץ יופעל הרבה לפני שהחלון מתמלא ולמודל יש מקום רב לייצר תגובות ארוכות. אם בכל זאת תחילו הגדרה זו, שימו לב ש-`reserveTokens: 4096` מגביל את אורך התגובה לכ-4 אלף טוקנים, מה שעלול לקטוע יצירת קבצים ארוכה או תוכניות מפורטות.
>
> **היכן להוסיף הגדרה זו:** הניחו את הבלוק `compaction` בתוך `agents.defaults` בקובץ `openclaw.json` שלכם (בדרך כלל ב-`~/.openclaw/openclaw.json`):
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
> שאר התצורה שלכם (gateway, channels, models וכו') נשארת ללא שינוי, יש להוסיף רק את המפתח `compaction`.

### (מומלץ) הפעלת בידוד עם Docker

OpenClaw יכול לנתב את כל פעולות הקבצים והקוד של הסוכן דרך קונטיינר Docker מבודד במקום להריץ אותן ישירות על המחשב המארח שלכם. פעולה זו מגבילה את מרחב הפגיעה של כל פעולה לא מכוונת לתוך הסביבה המבודדת, ומשאירה את מערכת הקבצים והרשת של המחשב המארח שלכם ללא פגיעה.

בנו את תמונת ה-sandbox פעם אחת (יש להתקין את Docker):

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

הריצו את הפקודה הבאה כדי להוסיף את המפתח `sandbox` בתוך הבלוק `agents.defaults` הקיים ב-`~/.openclaw/openclaw.json`:

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

לקונטיינרים של sandbox אין **גישה לרשת** כברירת מחדל. עיינו במסמך [ההפניה לבידוד](https://docs.openclaw.ai/gateway/sandboxing) לפרטים על חיבורי bind mount ועקיפת הגדרות רשת.

> #### פתרון בעיות: Docker Permission Denied
> 
> אם אתם מקבלים "permission denied" בעת הרצת פקודות Docker:
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
> **שלב 2: אם השגיאה נמשכת, החילו את התיקון הקבוע**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> לאחר מכן **הפעילו מחדש** את המערכת שלכם.
> 
> **פתרון זמני מהיר** (מתאפס לאחר הפעלה מחדש):
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

### הפעלת שער הכניסה (Gateway) של OpenClaw

השער (gateway) הוא תהליך ה-OpenClaw שמנהל את לולאת הסוכן ומגיש את לוח הבקרה:

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

כדי לפתוח את לוח הבקרה, הריצו זאת במסוף שני בזמן שהשער עדיין פועל:

```bash
openclaw dashboard
```

מכיוון שהשער מתחבר ל-loopback, לוח הבקרה מאמת את עצמו אוטומטית כאשר הוא נפתח מאותו מחשב, אין צורך בהזנת אסימון (token) או באישור מכשיר לגישה מקומית. אתם אמורים לראות את לוח הבקרה של OpenClaw עם מודל ה-Lemonade שלכם רשום כשרת הפעיל.

> אם הפעלתם בידוד (sandboxing), תוכלו לוודא זאת על ידי בקשה מהסוכן ל-`run hostname` מלוח הבקרה. אם אתם רואים מזהה קונטיינר קצר במקום שם המארח (hostname) של המחשב שלכם, הבידוד פועל.

**ברכות, בניתם ערימת סוכן בינה מלאכותית מקומית לחלוטין מאפס.**

> **צריכים את אסימון השער (gateway token)?** הריצו `openclaw dashboard --no-open` כדי להדפיס את כתובת ה-URL של לוח הבקרה עם האסימון משובץ בתוכה (הפקודה גם מנסה להעתיק אותו ללוח ההעתקה שלכם). לחלופין, האסימון נמצא ב-`gateway.auth.token` בקובץ `~/.openclaw/openclaw.json`.
>
> **אישור מכשיר מרוחק:** כאשר אתם פותחים את לוח הבקרה ממחשב שני או מטלפון, הדפדפן מציג מזהה בקשה. חזרו למחשב שמריץ את השער, והריצו:
> ```bash
> openclaw devices approve <requestId>
> ```
> פעולה זו נדרשת רק עבור מכשירים מרוחקים או משניים, גישת loopback מאותו מחשב מאמתת את עצמה אוטומטית.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## אופציונלי: חיבור ערוץ תקשורת

לאחר שהשער פועל, תוכלו להגיע לסוכן המקומי שלכם מכל מכשיר. בחרו את האפשרות המתאימה להגדרה שלכם. OpenClaw תומך ב-[Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), ובערוצים נוספים, ראו את הרשימה המלאה ב-[docs.openclaw.ai](https://docs.openclaw.ai).

---

### אפשרות א': Discord

Discord דורש שרת שבו **יש לכם הרשאת מנהל מערכת** כדי להוסיף בוט. אם אתם משתפים שרתים אך אינכם הבעלים של אף אחד מהם, השתמשו באפשרות ב' (Telegram) במקום זאת.
#### יצירת חשבון Discord ושרת

אם אין לכם חשבון Discord, הירשמו בכתובת [discord.com](https://discord.com). כמו כן, עליכם להחזיק בשרת שבו אתם מנהלים (administrator); צרו אחד על ידי לחיצה על סמל ה-**+** בסרגל הצד של Discord ובחירה ב-**Create My Own**. שרת פרטי מתאים בהחלט.

#### יצירת אפליקציית Discord ובוט

1. עברו אל [פורטל המפתחים של Discord](https://discord.com/developers/applications) ולחצו על **New Application**. תנו לו שם (למשל "openclaw-bot").
2. בסרגל הצד, לחצו על **Bot**. הגדירו שם משתמש עבור הבוט.
3. עדיין בעמוד Bot, גללו אל **Privileged Gateway Intents** והפעילו:
   - **Message Content Intent** (חובה)
   - **Server Members Intent** (מומלץ)
4. גללו חזרה למעלה ולחצו על **Reset Token** כדי לייצר את אסימון הבוט שלכם. העתיקו אותו.

#### הוספת הבוט לשרת שלכם

1. בסרגל הצד, לחצו על **OAuth2/ URL Generator**.
2. תחת **Scopes**, הפעילו את `bot` ואת `applications.commands`.
3. תחת **Bot Permissions**, הפעילו: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. העתיקו את כתובת ה-URL שנוצרה, הדביקו אותה בדפדפן, בחרו את השרת שלכם ואשרו. הבוט אמור להופיע כעת ברשימת החברים של השרת שלכם.

#### איסוף המזהים שלכם

הפעילו את Developer Mode ב-Discord (**User Settings/ Advanced/ Developer Mode**), ולאחר מכן:
- לחיצה ימנית על סמל השרת שלכם: **Copy Server ID**
- לחיצה ימנית על האווטאר שלכם: **Copy User ID**

#### אפשור הודעות פרטיות מחברי שרת

לחיצה ימנית על סמל השרת שלכם/ **Privacy Settings**/ הפעילו את **Direct Messages**. זה מאפשר לבוט לשלוח לכם הודעה פרטית, מה שנדרש לשלב הצימוד (pairing).

#### הגדרת OpenClaw עבור Discord

שמרו את אסימון הבוט שלכם כמשתנה סביבה, ולאחר מכן צרו קובץ patch יחיד שמפעיל את Discord, מפנה לאסימון, ומאשר (allowlist) את השרת שלכם. החליפו את `<server_id>` ואת `<user_id>` במזהים שנאספו לעיל.

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

> **אל תסתמכו על בקשה מהסוכן להגדיר זאת.** כאשר sandboxing מופעל, הסוכן אינו יכול לכתוב אל `~/.openclaw/openclaw.json` מתוך ה-sandbox; השתמשו בפקודות ה-CLI שלמעלה על המחשב המארח (host) במקום.

הפעילו מחדש את ה-gateway כדי שיאמץ את תצורת הערוץ החדשה:

```bash
openclaw gateway run --bind loopback --port 18789
```

אתם אמורים לראות `logged in to discord as <bot-name>` בפלט ה-gateway תוך מספר שניות.

#### צימוד חשבון ה-Discord שלכם

שלחו הודעה פרטית לבוט ב-Discord. הוא ישיב עם קוד צימוד קצר.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

אשרו זאת על המכונה שמריצה את OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> קודי צימוד פגים לאחר שעה אחת.

כעת תוכלו לשוחח עם הסוכן שלכם ישירות מ-Discord ולהעביר משימות לחומרה המקומית שלכם.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### אפשרות ב׳: Telegram

Telegram פשוט יותר מ-Discord עבור רוב המשתמשים, הוא אינו דורש שרת ואינו דורש הרשאות מנהל.

#### יצירת בוט Telegram

1. פתחו את Telegram ושלחו הודעה ל-**@BotFather**.
2. שלחו `/newbot` ופעלו לפי ההנחיות. שמרו את אסימון הבוט שהוא נותן לכם.

#### הגדרת OpenClaw עבור Telegram

שמרו את האסימון כמשתנה סביבה:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

הוסיפו את תצורת הערוץ אל `~/.openclaw/openclaw.json` (או בצעו patch דרך לוח הבקרה):

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

הפעילו מחדש את ה-gateway, ולאחר מכן שלחו לבוט שלכם הודעה כלשהי ב-Telegram. אשרו את הצימוד:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

קודי צימוד פגים לאחר שעה אחת. כעת תוכלו לשוחח עם הסוכן שלכם דרך הודעה פרטית ב-Telegram.

---

## הצעדים הבאים

כעת, לאחר שהסוכן שלכם יכול לקבל פקודות מהטלפון שלכם ולפעול על המחשב המקומי שלכם, הנה שלושה כיוונים ששווה לחקור:

1. **מסכם שוק המניות**: תזמנו את OpenClaw כדי להביא נתונים מממשקי API פיננסיים במרווח זמן קבוע, לסכם את תנועות היום עם המודל המקומי שלכם, ולשלוח תקציר לטלפון שלכם כל בוקר דרך הערוץ שבחרתם.

2. **מעקב אחר Fine-tuning**: הפעילו משימת אימון (training job) מרחוק דרך Telegram או Discord, ולאחר מכן בקשו מהסוכן לעקוב אחר יומן האימון (training log) ולדווח על ערכי loss תקופתיים, ניצולת GPU ושימוש בדיסק חזרה לטלפון שלכם. אם הריצה נתקעת או ה-VRAM קופץ, תדעו על כך מיד מבלי הצורך להיות ליד המכונה.

3. **IOT עם VLM מקומי**: כוונו מצלמה לדלת הכניסה שלכם, הריצו מודל ראייה (vision model) על Lemonade, ובקשו מ-OpenClaw לנתח פריימים לפי דרישה או לפי טריגר. שאלו "האם הגיעו חבילות היום?" מהטלפון שלכם וקבלו תשובה ישירה מהחומרה שלכם.