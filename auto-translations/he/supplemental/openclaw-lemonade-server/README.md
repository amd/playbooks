<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# הפעלת OpenClaw עם Lemonade Server כ-backend

## סקירה כללית

[**OpenClaw**](https://openclaw.ai/) הוא סוכן AI אוטונומי שיכול לכתוב ולהריץ קוד, לנהל קבצים, ולבצע משימות מורכבות רב-שלביות בשמך. בשונה מעוזר צ'אט שרק עונה על שאלות, OpenClaw נוקט פעולות ממשיות במערכת שלך, ולכן הוא זקוק ל-backend מהיר ומסוגל שיוכל לעמוד בקצב של לולאת סוכן תובענית.

[**Lemonade Server**](https://lemonade-server.ai/) הוא אותו backend. זהו שרת הסקה מקומי בקוד פתוח שמריץ מודלי GenAI ישירות על החומרה שלך וחושף אותם דרך ה-API הסטנדרטי של OpenAI.

יחד, הם מהווים מחסנית סוכן AI מקומית לחלוטין: Lemonade מטפל בהסקת המודל, ו-OpenClaw מספק את לולאת הסוכן שהופכת את פלטי המודל לפעולות ממשיות.

> **לפני שתמשיך:** OpenClaw הוא סוכן AI בעל אוטונומיה גבוהה. מתן גישה לכל סוכן AI למערכת שלך עלול לגרום לתוצאות בלתי צפויות או לא מכוונות. המשך רק אם אתה מבין את הסיכונים ומרגיש בנוח עם תוכנה אוטונומית הפועלת בשמך.

---

## מה תלמד

בסוף המדריך הזה תוכל:

- ללמוד על **Lemonade Server**
- **להתקין את OpenClaw** ו**לכוון אותו אל Lemonade Server** כ-backend ה-AI שלו.
- **להפעיל את שער OpenClaw** ולאשר שהסוכן שלך מוכן לעבודה.
- **לחבר ערוץ תקשורת** (Discord או Telegram) כדי שתוכל לשוחח עם הסוכן שלך מכל מכשיר.

---

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

<!-- @os:linux -->
- מחשב עם **Ubuntu 24.04+** או הפצת Linux מבוססת Debian תואמת עם `apt-get`
- לפחות **12 GB של RAM** (מומלץ 64 GB+ למודלים גדולים יותר)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (אופציונלי, לבידוד OpenClaw בסביבת sandbox)

- **~10–30 GB של שטח דיסק פנוי** לקבצי משקל המודל
<!-- @os:end -->
<!-- @os:windows -->
- מחשב עם **Windows 10/11**
- לפחות **12 GB של RAM** (מומלץ 64 GB+ למודלים גדולים יותר)
- **~10–30 GB של שטח דיסק פנוי** לקבצי משקל המודל
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (אופציונלי, לבידוד OpenClaw בסביבת sandbox)
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

המודל המומלץ למדריך זה הוא **Qwen3.6-35B-A3B-GGUF** מ-Unsloth, מודל MoE חזק עם חלון הקשר של 263k טוקנים המתאים היטב לעומסי עבודה של סוכנים. מודל זה משתמש בכימות UD-Q4_K_XL. משוך אותו עכשיו:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

לאחר מכן טען אותו עם חלון הקשר גדול ושמור את ההגדרה להפעלות עתידיות:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

למודל יש אורך הקשר ברירת מחדל של 262,144 טוקנים. אם נתקלת בשגיאות אזילת זיכרון (OOM), שקול להקטין את חלון ההקשר. עם זאת, מכיוון ש-Qwen3.6 מנצל הקשר מורחב למשימות מורכבות, אנו ממליצים לשמור על אורך הקשר של לפחות 128K טוקנים כדי לשמר יכולות חשיבה.

> **טיפ: השבת חשיבה לתגובות סוכן מהירות יותר:** Qwen3.6-35B-A3B פועל במצב חשיבה כברירת מחדל, מה שמוסיף זמן המתנה לפני כל תגובה. בלולאות סוכן, עומס זה מצטבר במהירות. מאגר [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) מספק תצורה מוכנה שמשביתה את החשיבה. כדי להשתמש בה, הורד את הקובץ וייבא אותו:
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

אנו מריצים את OpenClaw בתוך WSL (מומלץ) ומחברים אותו ל-Lemonade הפועל באופן מקורי על Windows. זה מעניק לך סביבת מעטפת Linux עבור OpenClaw תוך שמירה על האצת GPU של Lemonade בצד Windows.

### התקנת WSL ו-Ubuntu

פתח את PowerShell כמנהל מערכת והתקן את ליבת WSL:

```powershell
wsl --install --no-distribution
```

לאחר מכן התקן את Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### הפעלת systemd ב-WSL

הרץ זאת בתוך מסוף Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

הפעל מחדש את WSL:

```powershell
wsl --shutdown
wsl
```

### גישור Lemonade מ-Windows אל WSL

WSL2 פועל ברשת וירטואלית. Lemonade על Windows נקשר ל-`127.0.0.1`, אליו WSL אינו יכול להגיע ישירות. פרוקסי פורט של Windows מעביר תעבורה מכתובת ה-IP של שער WSL אל localhost של Windows.

**מצא את כתובת ה-IP של שער WSL שלך** (הרץ בתוך WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**הוסף את פרוקסי הפורט** (הרץ ב-PowerShell כמנהל מערכת, החלף את `<WSL-Gateway-IP>` בכתובת ה-IP של שער WSL שלך):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**הוסף כלל חומת אש** (אותו PowerShell מורם):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**אמת מ-WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

אם כבר טענת את מודל Qwen3.6-35B-A3B-GGUF בשלב הקודם, אמור לראות פלט JSON כזה:

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

> כלל `netsh portproxy` שורד אתחולים מחדש, אך כתובת ה-IP של שער WSL עשויה להשתנות לאחר `wsl --shutdown`. אם Lemonade הופך לבלתי נגיש מ-WSL לאחר הפעלה מחדש, קבל את כתובת ה-IP המעודכנת של השער ועדכן את הפרוקסי עם כתובת ה-IP החדשה.

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
> הרץ את הפקודות בסעיף זה בתוך **מסוף WSL** שלך.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

הדגל `--no-onboard` מדלג על אשף ההגדרה האינטראקטיבי, תגדיר את ה-backend של המודל ידנית בשלב הבא, מה שמעניק לך שליטה מדויקת על איזה מודל ושרת משמשים.

פתח מסוף חדש ואשר את ההתקנה:

```bash
openclaw --version
```

> **טיפ:** אם אתה רואה `command not found` לאחר ההתקנה, הוסף את ספריית bin הגלובלית של npm ל-PATH שלך:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> כדי להפוך זאת לקבוע, הוסף את השורה לעיל לקובץ `~/.bashrc` או `~/.zshrc` שלך.

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

הרץ את ה-onboarding הלא-אינטראקטיבי של OpenClaw.
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

פקודה זו כותבת את תצורת OpenClaw אל `~/.openclaw/openclaw.json`.

> **גודל חלון ההקשר של OpenClaw:** דחיסת OpenClaw מופעלת כאשר `contextTokens > contextWindow − reserveTokens`. ברירת המחדל של `reserveTokensFloor` היא 20,000 טוקנים, רצפה שעוקפת את `reserveTokens` כאשר נמוכה ממנה, כך שכל הקשר מודל מתחת ל-~37k יפעיל לולאת דחיסה אינסופית. הגדר רזרבה נמוכה והשבת את הרצפה פעם אחת בתצורה שלך וזה יחול על כל מודל, ללא כוונון לכל מודל בנפרד:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` הוא *רצפה* (מגן מינימלי), לא הרזרבה עצמה, הגדרת הרצפה בלבד אינה משפיעה. `reserveTokensFloor: 0` משבית את המגן כך שה-`reserveTokens` הנמוך יותר מתקבל.
>
> **מתי להחיל זאת:** השתמש בתצורה זו אם חלון ההקשר האפקטיבי של המודל שלך נמוך מ-~37k, בין אם מכיוון שהמודל קטן (למשל 8k, 16k, 32k) או מכיוון שהגבלת אותו לערך נמוך יותר במכוון (למשל טעינת מודל 128k אך הגדרת הקשר ל-16k ב-Lemonade). ללא זאת, OpenClaw נכנס ללולאת דחיסה אינסופית בהפעלה.
>
> **מודלים עם הקשר גדול בהקשר מלא:** ניתן לדלג על זה לחלוטין. ברירות המחדל עובדות היטב, הדחיסה תיכנס לפעולה הרבה לפני שהחלון יתמלא והמודל יכול לייצר תגובות ארוכות. אם אתה מחיל זאת, שים לב ש-`reserveTokens: 4096` מגביל את אורך התגובה ל-~4k טוקנים, מה שעלול לקטוע יצירת קבצים ארוכה או תוכניות מפורטות.
>
> **היכן להוסיף זאת:** מקם את בלוק `compaction` בתוך `agents.defaults` ב-`openclaw.json` שלך (בדרך כלל ב-`~/.openclaw/openclaw.json`):
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
> שאר התצורה שלך (שער, ערוצים, מודלים וכו') נשארת ללא שינוי, רק מפתח ה-`compaction` צריך להתווסף.

### (מומלץ) הפעלת בידוד Docker

OpenClaw יכול לנתב את כל פעולות הקבצים והקוד של הסוכן דרך מיכל Docker מבודד במקום להריץ אותן ישירות על המארח שלך. זה מגביל את היקף הנזק של כל פעולה לא מכוונת לסביבת ה-sandbox, ומשאיר את מערכת הקבצים והרשת של המארח שלך ללא פגע.

בנה את תמונת ה-sandbox פעם אחת (Docker חייב להיות מותקן):

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

הרץ זאת כדי להוסיף את מפתח ה-`sandbox` בתוך בלוק `agents.defaults` הקיים ב-`~/.openclaw/openclaw.json`:

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

למיכלי sandbox אין **גישה לרשת** כברירת מחדל. ראה את [מדריך ה-sandboxing](https://docs.openclaw.ai/gateway/sandboxing) לעיגון נתומים ועקיפות רשת.

> #### פתרון בעיות: Docker Permission Denied
> 
> אם אתה מקבל "permission denied" בעת הרצת פקודות Docker:
> 
> **שלב 1: הוסף את המשתמש שלך לקבוצת docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **שלב 2: אם השגיאה נמשכת, החל את התיקון הקבוע**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> לאחר מכן **אתחל** את המערכת שלך.
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

### הפעלת שער OpenClaw

השער הוא תהליך OpenClaw שמנהל את לולאת הסוכן ומשרת את לוח המחוונים:

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

כדי לפתוח את לוח המחוונים, הרץ זאת במסוף שני בזמן שהשער עדיין פועל:

```bash
openclaw dashboard
```

מכיוון שהשער נקשר ל-loopback, לוח המחוונים מאמת אוטומטית כאשר נפתח מאותו מחשב, ללא צורך בהזנת טוקן או אישור מכשיר לגישה מקומית. אמור לראות את לוח המחוונים של OpenClaw עם מודל Lemonade שלך רשום כ-backend הפעיל.

> אם הפעלת sandboxing, תוכל לאמת זאת על ידי בקשה מהסוכן להריץ `run hostname` מלוח המחוונים. אם אתה רואה מזהה מיכל קצר במקום שם המחשב שלך, ה-sandbox פועל.

**ברכות, בנית מחסנית סוכן AI מקומית לחלוטין מאפס.**

> **צריך את טוקן השער?** הרץ `openclaw dashboard --no-open` כדי להדפיס את כתובת ה-URL של לוח המחוונים עם הטוקן מוטמע (הוא גם מנסה להעתיק אותו ללוח שלך). לחלופין, הטוקן נמצא ב-`gateway.auth.token` ב-`~/.openclaw/openclaw.json`.
>
> **אישור מכשיר מרוחק:** כאשר אתה פותח את לוח המחוונים ממחשב שני או טלפון, הדפדפן מציג מזהה בקשה. בחזרה על המחשב שמריץ את השער, הרץ:
> ```bash
> openclaw devices approve <requestId>
> ```
> זה נדרש רק עבור מכשירים מרוחקים או משניים, גישת loopback מאותו מחשב מאמתת אוטומטית.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## אופציונלי: חיבור ערוץ תקשורת

לאחר שהשער פועל, תוכל להגיע לסוכן המקומי שלך מכל מכשיר. בחר את האפשרות המתאימה להגדרה שלך. OpenClaw תומך ב-[Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), וערוצים נוספים, ראה את הרשימה המלאה ב-[docs.openclaw.ai](https://docs.openclaw.ai).

---

### אפשרות א': Discord

Discord דורש שרת שבו **יש לך הרשאות מנהל** להוספת בוט. אם אתה חולק שרתים אך אינך הבעלים של אחד מהם, השתמש באפשרות ב' (Telegram) במקום.

#### יצירת חשבון ושרת Discord

אם אין לך חשבון Discord, הירשם ב-[discord.com](https://discord.com). אתה גם צריך שרת שבו אתה מנהל, צור אחד על ידי לחיצה על סמל **+** בסרגל הצד של Discord ובחירת **Create My Own**. שרת פרטי מתאים.

#### יצירת אפליקציה ובוט Discord

1. עבור אל [פורטל המפתחים של Discord](https://discord.com/developers/applications) ולחץ על **New Application**. תן לו שם (למשל "openclaw-bot").
2. בסרגל הצד, לחץ על **Bot**. הגדר שם משתמש לבוט.
3. עדיין בדף Bot, גלול אל **Privileged Gateway Intents** והפעל:
   - **Message Content Intent** (נדרש)
   - **Server Members Intent** (מומלץ)
4. גלול חזרה למעלה ולחץ על **Reset Token** כדי ליצור את טוקן הבוט שלך. העתק אותו.

#### הוספת הבוט לשרת שלך

1. בסרגל הצד, לחץ על **OAuth2/ URL Generator**.
2. תחת **Scopes**, הפעל `bot` ו-`applications.commands`.
3. תחת **Bot Permissions**, הפעל: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. העתק את ה-URL שנוצר, הדבק אותו בדפדפן שלך, בחר את השרת שלך ואשר. הבוט אמור להופיע כעת ברשימת החברים של השרת שלך.

#### איסוף ה-IDs שלך

הפעל את מצב המפתח ב-Discord (**User Settings/ Advanced/ Developer Mode**), לאחר מכן:
- לחץ לחיצה ימנית על סמל השרת שלך: **Copy Server ID**
- לחץ לחיצה ימנית על הדמות שלך: **Copy User ID**

#### אפשרות הודעות ישירות מחברי שרת

לחץ לחיצה ימנית על סמל השרת שלך/ **Privacy Settings**/ הפעל **Direct Messages**. זה מאפשר לבוט לשלוח לך הודעות ישירות, שנדרשות לשלב ההתאמה.

#### הגדרת OpenClaw עבור Discord

שמור את טוקן הבוט שלך כמשתנה סביבה, לאחר מכן צור קובץ patch יחיד שמפעיל את Discord, מפנה לטוקן, ומוסיף לרשימת ההיתרים את השרת שלך. החלף את `<server_id>` ו-`<user_id>` ב-IDs שנאספו לעיל.

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

> **אל תסתמך על בקשה מהסוכן להגדיר זאת.** כאשר sandboxing מופעל, הסוכן אינו יכול לכתוב אל `~/.openclaw/openclaw.json` מתוך ה-sandbox, השתמש בפקודות CLI לעיל על המארח במקום.

הפעל מחדש את השער כדי שיקלוט את תצורת הערוץ החדשה:

```bash
openclaw gateway run --bind loopback --port 18789
```

אמור לראות `logged in to discord as <bot-name>` בפלט השער תוך מספר שניות.

#### התאמת חשבון Discord שלך

שלח הודעה ישירה לבוט ב-Discord. הוא ישיב עם קוד התאמה קצר.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

אשר זאת על המחשב שמריץ את OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> קודי התאמה פגים לאחר שעה אחת.

כעת תוכל לשוחח עם הסוכן שלך ישירות מ-Discord ולהעביר משימות לחומרה המקומית שלך.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### אפשרות ב': Telegram

Telegram פשוט יותר מ-Discord עבור רוב המשתמשים, הוא אינו דורש שרת ואינו דורש הרשאות מנהל.

#### יצירת בוט Telegram

1. פתח את Telegram ושלח הודעה ל-**@BotFather**.
2. שלח `/newbot` ופעל לפי ההנחיות. שמור את טוקן הבוט שהוא מעניק לך.

#### הגדרת OpenClaw עבור Telegram

שמור את הטוקן כמשתנה סביבה:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

הוסף את תצורת הערוץ אל `~/.openclaw/openclaw.json` (או תקן אותה דרך לוח המחוונים):

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

הפעל מחדש את השער, לאחר מכן שלח לבוט שלך כל הודעה ב-Telegram. אשר את ההתאמה:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

קודי התאמה פגים לאחר שעה אחת. כעת תוכל לשוחח עם הסוכן שלך דרך הודעה ישירה ב-Telegram.

---

## השלבים הבאים

כעת שהסוכן שלך יכול לקבל פקודות מהטלפון שלך ולפעול על המחשב המקומי שלך, הנה שלושה כיוונים שכדאי לחקור:

1. **מסכם שוק המניות**: תזמן את OpenClaw לא