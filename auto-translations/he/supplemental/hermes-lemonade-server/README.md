<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

# הפעלת Hermes Agent באופן מקומי עם Lemonade Server

## סקירה כללית

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) הוא סוכן AI משתפר-עצמי שנבנה על ידי Nous Research. יש לו לולאת למידה מובנית, הוא יוצר כישורים מתוך ניסיון, בונה זיכרון מתמשך של מי אתה על פני הפעלות (sessions), ויכול להריץ אוטומציות מתוזמנות מטעמך. בניגוד לעוזר צ'אט פשוט, Hermes מבצע פעולות אמיתיות: הרצת פקודות shell, כתיבת קבצים, גלישה באינטרנט, והאצלת זרימות עבודה מקבילות לתת-סוכנים.

[**Lemonade Server**](https://lemonade-server.ai/) הוא מנוע ההסקה המקומי שמניע אותו. זהו שרת קוד פתוח שמריץ מודלי GenAI ישירות על חומרת AMD שלך וחושף אותם דרך ה-API הסטנדרטי בתעשייה של OpenAI.

יחד הם מהווים מחסנית סוכן AI מקומית לחלוטין: Lemonade מטפל בהסקת המודל על ה-GPU שלך, ו-Hermes מספק את לולאת הסוכן, הזיכרון, הכישורים, ושער ההודעות (messaging gateway).

> **לפני שתמשיך:** Hermes Agent הוא סוכן AI בעל אוטונומיה גבוהה. מתן גישה לכל סוכן AI למערכת שלך עלול לגרום לתוצאות בלתי צפויות או לא מכוונות. המשך רק אם אתה מבין את הסיכונים ומרגיש בנוח עם תוכנה אוטונומית הפועלת מטעמך.

---

## מה תלמד

בסיום מדריך זה תוכל:

- **להתקין את Hermes Agent** ולהפנות אותו אל **Lemonade Server** כמנוע ה-AI שלו.
- **(מומלץ) להפעיל בידוד Docker/Podman** כדי לבודד את פעולות הסוכן מהמארח שלך.
- **להפעיל את שער ה-Hermes** ולוודא שהסוכן שלך מוכן.
- **לחבר ערוץ תקשורת** (Discord או Telegram) כדי שתוכל לשוחח עם הסוכן שלך מכל מכשיר.

---

<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות התוכנה המקדימות

<!-- @os:linux -->
- מחשב המריץ **Ubuntu 24.04+** או הפצת לינוקס מבוססת-Debian תואמת עם `apt-get`
- לפחות **12 GB של RAM** (מומלץ 64 GB+ עבור מודלים גדולים יותר)
- **~10–30 GB של שטח דיסק פנוי** עבור משקלי המודל
- [Podman](https://podman.io/docs/installation) (אופציונלי, לבידוד Hermes Agent)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- מחשב המריץ **Windows 10/11**
- לפחות **12 GB של RAM** (מומלץ 64 GB+ עבור מודלים גדולים יותר)
- **~10–30 GB של שטח דיסק פנוי** עבור משקלי המודל
- Podman (אופציונלי, לבידוד Hermes Agent). התקן בתוך WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman מותקן מראש ב-Halo Box ואין צורך בהגדרה
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## משיכה וטעינה של המודל המומלץ

המודל המומלץ עבור מדריך זה הוא **Qwen3.6-35B-A3B-GGUF** מבית Unsloth, מודל MoE חזק עם חלון הקשר (context window) של 263k טוקנים המתאים היטב לעומסי עבודה של סוכנים. מודל זה משתמש בקוונטיזציית UD-Q4_K_XL. משוך אותו כעת:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

לאחר מכן טען אותו עם חלון הקשר גדול ושמור הגדרה זו להרצות עתידיות:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

למודל יש אורך הקשר ברירת מחדל של 262,144 טוקנים. אם אתה נתקל בשגיאות חוסר זיכרון (OOM), שקול להקטין את חלון ההקשר.

> **טיפ: השבת חשיבה לתגובות סוכן מהירות יותר:** Qwen3.6-35B-A3B פועל במצב חשיבה כברירת מחדל, מה שמוסיף השהיה לפני כל תגובה. עבור לולאות סוכן, תקורה זו מצטברת במהירות. המאגר [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) מספק תצורה מוכנה שמשביתה חשיבה. כדי להשתמש בה, הורד את הקובץ וייבא אותו:
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
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
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
model_id = "${hermes_model}"

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
  "model": "${hermes_model}",
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

אנו מריצים את Hermes Agent בתוך WSL ומחברים אותו ל-Lemonade הרץ באופן טבעי על Windows. זה נותן לך סביבת מעטפת לינוקס עבור Hermes תוך שמירה על האצת ה-GPU של Lemonade בצד Windows.

### התקנת WSL ו-Ubuntu

פתח את PowerShell כמנהל (Administrator) והתקן את גרעין ה-WSL:

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

WSL2 פועל ברשת וירטואלית. Lemonade ב-Windows מתחבר ל-`127.0.0.1`, ש-WSL לא יכול להגיע אליו ישירות. פרוקסי פורטים של Windows מעביר תעבורה מכתובת ה-IP של שער ה-WSL אל localhost של Windows.

**מצא את כתובת ה-IP של שער ה-WSL שלך** (הרץ בתוך WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**הוסף את פרוקסי הפורט** (הרץ ב-PowerShell כמנהל, החלף את `<WSL-Gateway-IP>` בכתובת ה-IP של שער ה-WSL שלך):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**הוסף כלל חומת אש** (אותו PowerShell עם הרשאות מוגברות):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**וודא מ-WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

אם כבר טענת את המודל Qwen3.6-35B-A3B-GGUF בשלב הקודם, אמור להופיע פלט JSON המפרט את המודל הטעון שלך.

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

> כלל ה-`netsh portproxy` שורד הפעלות מחדש, אך כתובת ה-IP של שער ה-WSL עלולה להשתנות לאחר `wsl --shutdown`. אם Lemonade הופך לבלתי נגיש מ-WSL לאחר הפעלה מחדש, קבל את כתובת השער המעודכנת ועדכן את הפרוקסי עם כתובת ה-IP החדשה הזו.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## התקנת Hermes Agent

<!-- @os:windows -->
> הרץ את הפקודות בסעיף זה בתוך **מסוף ה-WSL** שלך, אלא אם צוין אחרת.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

הדגל `--skip-setup` מדלג על אשף ההתקנה האינטראקטיבי כך שתוכל להגדיר את מנוע המודל באופן ידני בשלב הבא.

טען מחדש את המעטפת שלך:

```bash
source ~/.bashrc
```

אשר את ההתקנה:

```bash
hermes --version
```

הרץ אבחון עצמי לבדיקת כל התלויות:

```bash
hermes doctor
```

> **טיפ:** אם אתה רואה `command not found` לאחר ההתקנה, הוסף את Hermes ל-PATH שלך:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> כדי להפוך זאת לקבוע, הוסף את השורה למעלה לקובץ `~/.bashrc` או `~/.zshrc` שלך.

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## הגדרת Hermes לשימוש ב-Lemonade

Hermes שומר את תצורת המודל שלו ב-`~/.hermes/config.yaml`. ניתן להשתמש בבורר האינטראקטיבי `hermes model` או לכתוב את התצורה ישירות.

### אפשרות 1: בורר אינטראקטיבי

<!-- @os:windows -->
> הריצו את הפקודה הבאה בתוך **טרמינל ה-WSL** שלכם.
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

כאשר תתבקשו:

1. בחרו **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** השתמשו בכתובת ה-IP של שער ה-WSL: הריצו `ip route show default | awk '{print $3}' | head -1` בתוך WSL כדי לקבל אותה, ולאחר מכן הזינו `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** בחרו את `Qwen3.6-35B-A3B-GGUF` מהרשימה
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (או כל שם אחר שתעדיפו)

`hermes model` שומר גם את בחירת המודל הפעיל וגם רשומת `custom_providers` בעלת שם, המאחסנת את אורך ההקשר לצד נקודת הקצה. התוצאה בקובץ `~/.hermes/config.yaml` נראית כך:

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### אפשרות 2: כתיבת התצורה ישירות

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

בתוך טרמינל ה-WSL שלכם, קבלו את כתובת ה-IP של מארח Windows וכתבו את התצורה:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## (מומלץ) הפעלת בידוד ארגז חול (Sandboxing) עם Podman

סוכן Hermes יכול לנתב את כל פעולות המעטפת (shell) והקבצים של הסוכן דרך מכולה מבודדת, במקום להריץ אותן ישירות על המארח שלכם. כך צמצם רדיוס הפגיעה של כל פעולה לא מכוונת לארגז החול בלבד, ומערכת הקבצים והרשת של המארח שלכם נשארות ללא פגיעה.

בנו תמונת ארגז חול קלת משקל:

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
היכנסו לטרמינל ה-WSL שלכם:

```powershell
wsl -d Ubuntu-24.04
```

לאחר מכן, בנו תמונת ארגז חול קלת משקל:

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

לאחר מכן הגדירו את Hermes להשתמש ב-Podman כזמן ריצה של המכולות והגדירו את backend הטרמינל:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> ה-`terminal.backend` עדיין `docker`.
> `HERMES_DOCKER_BINARY` הוא זה שמורה ל-Hermes להשתמש ב-Podman כזמן הריצה במקום זאת.

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

כעת Hermes יפעיל מכולת ארגז חול קבועה וינתב את כל קריאות ה-`terminal` וכלי הקבצים דרכה. המכולה חולקת את מחזור החיים של תהליך Hermes, נעשה בה שימוש חוזר בכל קריאות הכלים, והיא נהרסת כאשר Hermes יוצא.

> **אימות שארגז החול פועל:** הפעילו את Hermes (`hermes`) ובקשו ממנו `run hostname` - אתם אמורים לראות מזהה מכולה קצר במקום שם המארח של המחשב שלכם. תוכלו גם לבקש ממנו `rm -rf <path-to-a-dummy-file/folder>`: Hermes יאשר את המחיקה, אך התיקייה עדיין תהיה קיימת במארח שלכם. הפקודה רצה בתוך `$HOME` המבודד של המכולה, לא שלכם.

> **זקוקים לבידוד חזק יותר?** Hermes מספק גם תמונת Docker רשמית (`nousresearch/hermes-agent`) שמריצה את כל תהליך הסוכן בתוך מכולה - כולל השער (gateway), הכלים, והכול. ראו את [תיעוד ה-Docker של Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/docker) לפרטי ההגדרה.

---

<!-- @os:linux -->
## (מומלץ) שילוב Hermes עם שירותי Firecrawl

Hermes יכול לגלוש ולחלץ תוכן מאתרים באמצעות כלי הרשת המובנים שלו. עם זאת, אתרים מודרניים רבים משתמשים במערכות זיהוי בוטים, החוסמות בקשות HTTP פשוטות ומחזירות דפי אתגר במקום התוכן בפועל. כתוצאה מכך, ייתכן ש-Hermes לא יוכל לחלץ מידע מאתרים אלו בצורה אמינה.

כדי להתגבר על מגבלה זו, [Firecrawl](https://docs.firecrawl.dev/introduction) מספק שירות גרימה (crawling) וחילוץ תוכן מאוחסן עצמאית, שיכול לעקוף אתגרים אלו ולשחרר את הפוטנציאל המלא של אוטומציית Hermes.

בהגדרה זו, Firecrawl פועל כקבוצת מכולות Docker המנוהלות באמצעות Podman. כדי לפשט את ניהול מחזור החיים וההפעלה האוטומטית, אנו רושמים את Firecrawl כשירות `systemd` ברמת המשתמש, המתזמר את מחסנית ה-Podman Compose הבסיסית. כך Hermes יכול להתחיל, לעצור ולוודא את שירות Firecrawl באמצעות פקודות `systemctl --user` סטנדרטיות, במקום לתקשר עם המכולות ישירות.

כדי לשמור על הפשטות, פירקנו את כל התהליך לארבעה שלבים:

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
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
בשלב זה, השירות הוגדר אך טרם נרשם ב-`systemd`.
ודאו ששם הקובץ תואם במדויק למה שיצרתם למעלה, ולאחר מכן הריצו:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
אם ההרצה הצליחה, אמורים לראות את הפלט הבא:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` מכיל קישורים סימבוליים לשירותים המוגדרים להתחיל אוטומטית.

### 2. הגדרת Firecrawl עבור השירות שלכם

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) אידיאלי עבור מי שזקוק לשליטה מלאה בסביבות הגרימה ועיבוד הנתונים שלו, אך מגיע עם מחיר של מאמצי תחזוקה והגדרה נוספים.

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
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> הגדירו את `BULL_AUTH_KEY` לסוד חזק, במיוחד בכל פריסה הנגישה מרשתות לא מהימנות.
### 3. פריסת Hermes באמצעות Compose

לפני שממשיכים, ודאו שמשכתם את תמונת ה-Docker העדכנית ביותר של Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
לאחר מכן, הורידו את קובץ ה-Compose של Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) והניחו אותו בתיקיית השורש `/firecrawl`:

> מוסכמה זו נדרשת כדי ש-`systemd` יוכל לאתר ולהפעיל את השירות כראוי, כפי שצוין ב-`WorkingDirectory=${HOME}/firecrawl`.

> תמיד ניתן להרחיב את המחסנית על ידי הוספת שירותי Firecrawl נוספים לפי הצורך. הרשימה המלאה של השירותים הזמינים נמצאת בקובץ הרשמי [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. הפעלת שירות Hermes דרך Firecrawl 

לפני העברת השליטה ל-`systemd`, ודאו שהכול עובד כראוי על ידי הרצת המחסנית באופן ידני:
```bash
podman compose -f hermes-compose.yaml up -d
```
אם הכול מוגדר כראוי, אמור להופיע מכולת Hermes, ופלט שורת הפקודה שלכם אמור להיראות בערך כך:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

לאחר האימות, הורידו את המחסנית לפני שממשיכים:
```bash
podman compose -f hermes-compose.yaml down
```
כעת, לאחר שהכול אומת, הפעילו את השירות דרך `systemd`:
```bash
systemctl --user start firecrawl.service
```
[ה-API של Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) נגיש מתוך המכולה האינטראקטיבית, ולוח הבקרה מבוסס האינטרנט (Web Dashboard) זמין באותו מארח ופורט בכתובת http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

כדי לעצור את השירות, הריצו:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

התחילו הפעלת CLI אינטראקטיבית ישירות: 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**ברכות, בניתם מחסנית סוכן AI מקומית לחלוטין.**

### לוח הבקרה מבוסס האינטרנט (Web Dashboard)

Hermes כולל ממשק משתמש מבוסס דפדפן לניהול הגדרות, מפתחות API, מודלים, הפעלות, זיכרון ומשימות מתוזמנות (cron). פתחו מסוף שני בזמן שהשער (gateway) או ה-CLI פועלים, והפעילו אותו באמצעות:

```bash
hermes dashboard
```

פעולה זו מפעילה שרת מקומי ופותחת את `http://127.0.0.1:9119` בדפדפן שלכם. עיינו ב[תיעוד לוח הבקרה](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) לרשימת המאפיינים המלאה.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## אופציונלי: חיבור ערוץ תקשורת

לאחר שהשער (gateway) פועל, ניתן לגשת לסוכן המקומי שלכם מכל מכשיר. Hermes תומך ב-[Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) ועוד

---

### Discord

Discord דורש שרת שבו **יש לכם הרשאות מנהל** כדי להוסיף בוט. אם אתם משתפים שרתים אך אינכם הבעלים של אף אחד מהם, השתמשו ב-Telegram במקום.

#### יצירת אפליקציה ובוט ב-Discord

1. עברו אל [Discord Developer Portal](https://discord.com/developers/applications) ולחצו על **New Application**. תנו לה שם (למשל, "hermes-bot").
2. בסרגל הצד, לחצו על **Bot**. הגדירו שם משתמש עבור הבוט.
3. בעודכם בעמוד ה-Bot, גללו אל **Privileged Gateway Intents** והפעילו:
   - **Message Content Intent** (נדרש)
   - **Server Members Intent** (מומלץ)
4. גללו חזרה למעלה ולחצו על **Reset Token** כדי ליצור את אסימון (token) הבוט שלכם. העתיקו אותו.

#### הוספת הבוט לשרת שלכם

1. בסרגל הצד, לחצו על **OAuth2 / URL Generator**.
2. תחת **Scopes**, הפעילו את `bot` ואת `applications.commands`.
3. תחת **Bot Permissions**, הפעילו: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. העתיקו את הכתובת (URL) שנוצרה, הדביקו אותה בדפדפן, בחרו את השרת שלכם ואשרו.

#### איסוף המזהים (IDs) שלכם והפעלת הודעות פרטיות

הפעילו את מצב המפתחים (Developer Mode) ב-Discord (**User Settings / Advanced / Developer Mode**), ולאחר מכן:
- לחצו לחיצה ימנית על סמל השרת שלכם: **Copy Server ID**
- לחצו לחיצה ימנית על תמונת הפרופיל שלכם: **Copy User ID**

לחצו לחיצה ימנית על סמל השרת שלכם / **Privacy Settings** / הפעילו את **Direct Messages**. פעולה זו נדרשת לשלב הצימוד (pairing).

#### הגדרת Hermes עבור Discord

הוסיפו את השורות הבאות אל `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

לאחר מכן, הפעילו את השער (gateway):

```bash
hermes gateway
```

הבוט אמור להופיע כמחובר (online) ב-Discord תוך מספר שניות. שלחו לו הודעה, בין אם בהודעה פרטית ובין אם בערוץ שהוא רואה.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### יצירת בוט ב-Telegram

1. פתחו את Telegram ושלחו הודעה ל-**@BotFather**.
2. שלחו `/newbot` ופעלו לפי ההנחיות. שמרו את אסימון (token) הבוט שהוא מספק לכם.

#### הגדרת Hermes עבור Telegram

הוסיפו את השורות הבאות אל `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **לא יודעים מהו מזהה המשתמש (user ID) שלכם ב-Telegram?** שלחו הודעה ל-[@userinfobot](https://t.me/userinfobot) ב-Telegram, הוא ישיב לכם עם המזהה המספרי שלכם.

לאחר מכן, הפעילו את השער (gateway):

```bash
hermes gateway
```

שלחו לבוט שלכם כל הודעה ב-Telegram כדי לבדוק. כעת תוכלו לשוחח עם הסוכן שלכם דרך הודעה פרטית ב-Telegram. עיינו ב[מדריך ההגדרה המלא של Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) עבור מצב webhook ואפשרויות מתקדמות.

---

## הצעדים הבאים

כעת, כאשר הסוכן שלכם יכול לקבל פקודות מהטלפון שלכם ולפעול על המחשב המקומי שלכם, הנה שלושה כיוונים ששווה לחקור:

1. **תקציר מחקר אוטומטי**: תזמנו את Hermes לחפש ברשת נושאים שמעניינים אתכם מדי בוקר, לסכם את הממצאים באמצעות המודל המקומי שלכם, ולשלוח תקציר לטלפון שלכם דרך Telegram או Discord, הכול פועל על החומרה שלכם ללא עלויות ענן.

2. **סקירת קוד לפי דרישה**: הפנו את Hermes למאגר (repository) ב-GitHub, בקשו ממנו לסקור בקשות משיכה (pull requests) פתוחות, ותנו לו לפרסם תגובות או סיכום חזרה לצ'אט שלכם. בעזרת backend של מסוף Docker, כל פעולות ה-git פועלות בתוך הסביבה המבודדת (sandbox), ובכך שומרות על ניקיון המארח שלכם.

3. **עוזר קבצים מקומי**: תנו ל-Hermes גישה לתיקיית עבודה ובקשו ממנו לארגן, לשנות שם, לסכם או להמיר קבצים לפי דרישה מהטלפון שלכם. מכיוון שה-backend של מסוף Docker מגביל את כל פעולות הכתיבה לסביבת העבודה המבודדת (sandbox), פעולות הרסניות בטעות מוכלות ומוגבלות.