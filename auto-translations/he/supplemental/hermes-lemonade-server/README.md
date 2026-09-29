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

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) הוא סוכן AI משתפר-עצמי שנבנה על ידי Nous Research. יש לו לולאת למידה מובנית, הוא יוצר כישורים מתוך ניסיון, בונה זיכרון מתמשך של מי אתם על פני מספר הפעלות, ויכול להריץ אוטומציות מתוזמנות מטעמכם. בשונה מעוזר צ'אט פשוט, Hermes מבצע פעולות אמיתיות: הרצת פקודות shell, כתיבת קבצים, גלישה באינטרנט, והאצלת זרימות עבודה מקבילות לתת-סוכנים.

[**Lemonade Server**](https://lemonade-server.ai/) הוא backend ההסקה המקומי שמפעיל אותו. זהו שרת קוד פתוח שמריץ מודלים של GenAI ישירות על חומרת AMD שלכם וחושף אותם באמצעות ה-API התקני של OpenAI.

יחד הם מהווים מחסנית סוכן AI מקומית לחלוטין: Lemonade מטפל בהסקת המודל על ה-GPU שלכם, ו-Hermes מספק את לולאת הסוכן, הזיכרון, הכישורים, ושער ההודעות.

> **לפני שתמשיכו:** Hermes Agent הוא סוכן AI אוטונומי במידה רבה. מתן גישה למערכת שלכם לכל סוכן AI עלול להוביל לתוצאות בלתי צפויות או בלתי מכוונות. המשיכו רק אם אתם מבינים את הסיכונים ומרגישים בנוח עם תוכנה אוטונומית הפועלת מטעמכם.

---

## מה תלמדו

בסיום מדריך זה תוכלו:

- **להתקין את Hermes Agent** ולהצביע אותו אל **Lemonade Server** כ-backend ה-AI שלו.
- **(מומלץ) להפעיל בידוד Docker/Podman** כדי לבודד את פעולות הסוכן ממארח (host) המחשב שלכם.
- **להפעיל את שער Hermes** ולוודא שהסוכן שלכם מוכן.
- **לחבר ערוץ תקשורת** (Discord או Telegram) כדי שתוכלו לשוחח עם הסוכן שלכם מכל מכשיר.

---

<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מקדימות

<!-- @os:linux -->
- מחשב המריץ **Ubuntu 24.04+** או הפצת Linux מבוססת-Debian תואמת עם `apt-get`
- לפחות **12 GB של RAM** (מומלץ 64 GB+ עבור מודלים גדולים יותר)
- **כ-10–30 GB של שטח דיסק פנוי** עבור משקלי המודל
- [Podman](https://podman.io/docs/installation) (אופציונלי, לבידוד Hermes Agent)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- מחשב המריץ **Windows 10/11**
- לפחות **12 GB של RAM** (מומלץ 64 GB+ עבור מודלים גדולים יותר)
- **כ-10–30 GB של שטח דיסק פנוי** עבור משקלי המודל
- Podman (אופציונלי, לבידוד Hermes Agent). התקינו בתוך WSL:
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

המודל המומלץ עבור מדריך זה הוא **Qwen3.6-35B-A3B-GGUF** מבית Unsloth, מודל MoE חזק עם חלון הקשר של 263k טוקנים המתאים היטב לעומסי עבודה של סוכנים. מודל זה משתמש בקוונטיזציה מסוג UD-Q4_K_XL. משכו אותו כעת:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

לאחר מכן טענו אותו עם חלון הקשר גדול ושמרו הגדרה זו להפעלות עתידיות:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

למודל יש אורך הקשר ברירת מחדל של 262,144 טוקנים. אם אתם נתקלים בשגיאות של חוסר בזיכרון (OOM), שקלו להקטין את חלון ההקשר.

> **טיפ: השביתו חשיבה לתגובות סוכן מהירות יותר:** Qwen3.6-35B-A3B פועל במצב חשיבה כברירת מחדל, מה שמוסיף השהיה לפני כל תגובה. עבור לולאות סוכן, תקורה זו מצטברת במהירות. המאגר [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) מספק תצורה מוכנה מראש שמשביתה את מצב החשיבה. כדי להשתמש בה, הורידו את הקובץ וייבאו אותו:
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

אנו מריצים את Hermes Agent בתוך WSL ומחברים אותו ל-Lemonade הרץ באופן טבעי על Windows. כך תקבלו סביבת מעטפת (shell) Linux עבור Hermes תוך שמירה על האצת ה-GPU של Lemonade בצד Windows.

### התקנת WSL ו-Ubuntu

פתחו את PowerShell כמנהל (Administrator) והתקינו את הליבה (kernel) של WSL:

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

### גישור Lemonade מ-Windows אל WSL

WSL2 פועל ברשת וירטואלית. Lemonade ב-Windows נקשר ל-`127.0.0.1`, שאליו WSL אינו יכול להגיע ישירות. שרת proxy של פורט ב-Windows מעביר תעבורה מכתובת ה-IP של שער ה-WSL אל localhost של Windows.

**מצאו את כתובת ה-IP של שער ה-WSL** (הריצו בתוך WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**הוסיפו את ה-port proxy** (הריצו ב-PowerShell כמנהל, החליפו את `<WSL-Gateway-IP>` בכתובת ה-IP של שער ה-WSL שלכם):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**הוסיפו כלל חומת אש (firewall)** (אותו PowerShell מורם הרשאות):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**אמתו מתוך WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

אם כבר טענתם את המודל Qwen3.6-35B-A3B-GGUF בשלב הקודם, אמורים להופיע פלט JSON המפרט את המודל הטעון שלכם.

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

> כלל ה-`netsh portproxy` שורד לאחר הפעלות מחדש, אך כתובת ה-IP של שער ה-WSL עשויה להשתנות לאחר `wsl --shutdown`. אם Lemonade הופך לבלתי נגיש מתוך WSL לאחר הפעלה מחדש, קבלו את כתובת השער המעודכנת ועדכנו את ה-proxy עם כתובת ה-IP החדשה.

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
> הריצו את הפקודות בסעיף זה בתוך **מסוף ה-WSL** שלכם, אלא אם צוין אחרת.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

הדגל `--skip-setup` מדלג על אשף ההגדרה האינטראקטיבי כדי שתוכלו להגדיר את ה-backend של המודל ידנית בשלב הבא.

טענו מחדש את המעטפת (shell) שלכם:

```bash
source ~/.bashrc
```

אשרו את ההתקנה:

```bash
hermes --version
```

הריצו אבחון עצמי כדי לבדוק את כל התלויות:

```bash
hermes doctor
```

> **טיפ:** אם אתם רואים `command not found` לאחר ההתקנה, הוסיפו את Hermes ל-PATH שלכם:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> כדי להפוך זאת לקבוע, הוסיפו את השורה הנ"ל לקובץ `~/.bashrc` או `~/.zshrc` שלכם.

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

Hermes שומר את הגדרות המודל שלו ב-`~/.hermes/config.yaml`. ניתן להשתמש בבורר האינטראקטיבי `hermes model` או לכתוב את הקובץ ישירות.

### אפשרות 1: בורר אינטראקטיבי

<!-- @os:windows -->
> הרץ את הפקודה הבאה בתוך **מסוף WSL** שלך.
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

כאשר תתבקש:

1. בחר **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** השתמש בכתובת ה-IP של שער ה-WSL: הרץ `ip route show default | awk '{print $3}' | head -1` בתוך WSL כדי לקבל אותה, ולאחר מכן הזן `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** בחר `Qwen3.6-35B-A3B-GGUF` מהרשימה
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (או כל שם אחר שתעדיף)

`hermes model` שומר גם את בחירת המודל הפעיל וגם ערך בשם `custom_providers` המאחסן את אורך ההקשר יחד עם נקודת הקצה. התוצאה בקובץ `~/.hermes/config.yaml` נראית כך:

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

### אפשרות 2: כתיבת הקובץ ישירות

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

בתוך מסוף ה-WSL שלך, קבל את כתובת ה-IP של מארח ה-Windows וכתוב את קובץ ההגדרות:

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

## (מומלץ) הפעלת בידוד באמצעות Podman Sandboxing

Hermes Agent יכול לנתב את כל פעולות המעטפת והקבצים של הסוכן דרך מיכל מבודד במקום להריץ אותן ישירות על המארח שלך. הדבר מגביל את רדיוס הפגיעה של כל פעולה בלתי מכוונת לסביבת ה-sandbox, ומשאיר את מערכת הקבצים והרשת של המארח שלך ללא פגיעה.

בנה תמונת sandbox קלת משקל:

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
היכנס למסוף ה-WSL שלך:

```powershell
wsl -d Ubuntu-24.04
```

לאחר מכן, בנה תמונת sandbox קלת משקל:

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

לאחר מכן, הגדר את Hermes להשתמש ב-Podman כסביבת ריצה למיכלים והגדר את ה-backend של המסוף:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> ה-`terminal.backend` עדיין `docker`.
> `HERMES_DOCKER_BINARY` הוא זה שמורה ל-Hermes להשתמש ב-Podman כסביבת הריצה במקום זאת.

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

כעת Hermes יריץ מיכל sandbox קבוע וינתב את כל קריאות `terminal` וכלי הקבצים דרכו. המיכל חולק את מחזור החיים של תהליך Hermes, נעשה בו שימוש חוזר בכל קריאות הכלים, והוא נהרס כאשר Hermes מסתיים.

> **וודא שה-sandbox עובד:** הפעל את Hermes (`hermes`) ובקש ממנו `run hostname` - אמור להופיע מזהה מיכל קצר במקום שם המחשב שלך. אפשר גם לבקש ממנו `rm -rf <path-to-a-dummy-file/folder>`: Hermes יאשר את המחיקה, אך התיקייה עדיין תהיה קיימת במארח שלך. הפקודה רצה בתוך ה-`$HOME` המבודד של המיכל, לא שלך.

> **צריך בידוד חזק יותר?** Hermes מספק גם תמונת Docker רשמית (`nousresearch/hermes-agent`) שמריצה את כל תהליך הסוכן בתוך מיכל - שער הגישה, הכלים, והכל. עיין ב-[תיעוד ה-Docker של Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/docker) לפרטי ההתקנה.

---

<!-- @os:linux -->
## (מומלץ) שילוב Hermes עם שירותי Firecrawl

Hermes יכול לגלוש ולחלץ תוכן מאתרי אינטרנט באמצעות כלי האינטרנט המובנים שלו. עם זאת, אתרים מודרניים רבים משתמשים במערכות זיהוי בוטים, החוסמות בקשות HTTP פשוטות ומחזירות דפי אתגר במקום התוכן בפועל. כתוצאה מכך, ייתכן ש-Hermes לא יוכל לחלץ מידע באופן אמין מאתרים אלה.

כדי להתגבר על מגבלה זו, [Firecrawl](https://docs.firecrawl.dev/introduction) מספק שירות סריקת אינטרנט וחילוץ תוכן המתארח באופן עצמאי, שיכול לעקוף אתגרים אלה ולפתוח את מלוא הפוטנציאל של אוטומציית Hermes.

בהגדרה זו, Firecrawl פועל כקבוצת מיכלי Docker המנוהלים באמצעות Podman. כדי לפשט את ניהול מחזור החיים וההפעלה האוטומטית, אנו רושמים את Firecrawl כשירות `systemd` ברמת המשתמש, שמתזמר את ערימת ה-Podman Compose הבסיסית. הדבר מאפשר ל-Hermes להפעיל, לעצור ולוודא את שירות Firecrawl באמצעות פקודות `systemctl --user` סטנדרטיות במקום לתקשר ישירות עם המיכלים.

כדי לשמור על הפשטות, פירקנו את התהליך כולו לארבעה שלבים:

---

### 1. רישום שירות המערכת
נווט לתיקיית הגדרות המשתמש של systemd:
```bash
cd ~/.config/systemd/user
```
צור ופתח קובץ חדש בשם `firecrawl.service`.
```bash
nano firecrawl.service
```
העתק והדבק את ההגדרה הבאה:
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
ודא ששם הקובץ תואם בדיוק למה שיצרת למעלה, ולאחר מכן הרץ:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
אם הפעולה הצליחה, אמורה להופיע הפלט הבא:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` מכיל קישורים סימבוליים לשירותים המוגדרים להתחיל אוטומטית.

### 2. הגדרת Firecrawl עבור השירות שלך

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) אידיאלי עבור מי שזקוק לשליטה מלאה בסביבות הסריקה ועיבוד הנתונים שלו, אך מגיע עם המחיר של מאמצי תחזוקה והגדרה נוספים.

התחל בשכפול המאגר:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
צור `.env` בתיקיית השורש `/firecrawl`:
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
> הגדר את `BULL_AUTH_KEY` לסוד חזק, במיוחד בכל פריסה הנגישה מרשתות לא מהימנות.
### 3. פריסת Hermes באמצעות Compose

לפני שממשיכים, ודאו שמשכתם את תמונת ה-Docker העדכנית ביותר של Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
לאחר מכן, הורידו את קובץ ה-Compose של Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) ומקמו אותו בתיקיית השורש `/firecrawl`:

> מוסכמה זו נדרשת כדי ש-`systemd` יאתר ויפעיל את השירות כראוי, כפי שמצוין ב-`WorkingDirectory=${HOME}/firecrawl`.

> ניתן תמיד להרחיב את הסטאק על ידי הוספת שירותי Firecrawl נוספים בהתאם לצורך. את הרשימה המלאה של השירותים הזמינים ניתן למצוא בקובץ הרשמי [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. הפעלת שירות Hermes דרך Firecrawl 

לפני מסירת השליטה ל-`systemd`, ודאו שהכול פועל כראוי על ידי הרצת הסטאק ידנית:
```bash
podman compose -f hermes-compose.yaml up -d
```
אם הכול מוגדר כראוי, אמור להופיע קונטיינר ה-Hermes, ופלט שורת הפקודה שלכם אמור להיראות בדומה לזה:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

לאחר האימות, הורידו את הסטאק לפני שתמשיכו:
```bash
podman compose -f hermes-compose.yaml down
```
כעת, לאחר שהכול אומת, הפעילו את השירות דרך `systemd`:
```bash
systemctl --user start firecrawl.service
```
[ה-API של Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) נגיש מתוך הקונטיינר האינטראקטיבי, ולוח הבקרה הרשתי (Web Dashboard) זמין באותו מארח ופורט בכתובת http://127.0.0.1:9119.
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

התחילו הפעלה אינטראקטיבית של שורת פקודה (CLI) ישירות: 

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

**מזל טוב, בניתם סטאק סוכן בינה מלאכותית מקומי לחלוטין.**

### לוח בקרה רשתי (Web Dashboard)

Hermes כולל ממשק משתמש מבוסס דפדפן לניהול תצורה, מפתחות API, מודלים, הפעלות, זיכרון ומשימות cron. פתחו מסוף שני בזמן שה-gateway או ה-CLI פועלים והפעילו אותו באמצעות:

```bash
hermes dashboard
```

פעולה זו מפעילה שרת מקומי ופותחת את `http://127.0.0.1:9119` בדפדפן שלכם. עיינו ב[תיעוד לוח הבקרה](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) לעיון מלא בכל התכונות.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## אופציונלי: חיבור ערוץ תקשורת

לאחר שה-gateway פועל, תוכלו להגיע לסוכן המקומי שלכם מכל מכשיר. Hermes תומך ב[Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), ב[Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) ובאחרים

---

### Discord

Discord דורש שרת שבו **יש לכם הרשאות מנהל מערכת** כדי להוסיף בוט. אם אתם משתפים שרתים אך אינכם הבעלים של אף אחד מהם, השתמשו ב-Telegram במקום.

#### יצירת אפליקציית Discord ובוט

1. עברו אל [Discord Developer Portal](https://discord.com/developers/applications) ולחצו על **New Application**. תנו לה שם (לדוגמה, "hermes-bot").
2. בסרגל הצד, לחצו על **Bot**. הגדירו שם משתמש לבוט.
3. עדיין בעמוד ה-Bot, גללו אל **Privileged Gateway Intents** והפעילו:
   - **Message Content Intent** (נדרש)
   - **Server Members Intent** (מומלץ)
4. גללו חזרה למעלה ולחצו על **Reset Token** כדי ליצור את אסימון (token) הבוט שלכם. העתיקו אותו.

#### הוספת הבוט לשרת שלכם

1. בסרגל הצד, לחצו על **OAuth2 / URL Generator**.
2. תחת **Scopes**, הפעילו את `bot` ואת `applications.commands`.
3. תחת **Bot Permissions**, הפעילו: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. העתיקו את הכתובת URL שנוצרה, הדביקו אותה בדפדפן, בחרו את השרת שלכם ואשרו.

#### איסוף מזהי ה-ID שלכם והתרת הודעות פרטיות

הפעילו את מצב המפתחים ב-Discord (**User Settings / Advanced / Developer Mode**), ולאחר מכן:
- לחצו קליק ימני על אייקון השרת שלכם: **Copy Server ID**
- לחצו קליק ימני על תמונת הפרופיל שלכם: **Copy User ID**

לחצו קליק ימני על אייקון השרת שלכם / **Privacy Settings** / הפעילו את **Direct Messages**. הדבר נדרש עבור שלב הצימוד (pairing).

#### הגדרת Hermes עבור Discord

הוסיפו את הבא לקובץ `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

לאחר מכן, הפעילו את ה-gateway:

```bash
hermes gateway
```

הבוט אמור להופיע כמקוון ב-Discord תוך מספר שניות. שלחו לו הודעה, בין אם הודעה פרטית (DM) או בערוץ שהוא רואה.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### יצירת בוט Telegram

1. פתחו את Telegram ושלחו הודעה ל-**@BotFather**.
2. שלחו `/newbot` ופעלו לפי ההוראות. שמרו את אסימון (token) הבוט שהוא מספק לכם.

#### הגדרת Hermes עבור Telegram

הוסיפו את הבא לקובץ `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **לא יודעים מהו מזהה המשתמש שלכם ב-Telegram?** שלחו הודעה ל-[@userinfobot](https://t.me/userinfobot) בטלגרם, הוא ישיב לכם עם המזהה המספרי שלכם.

לאחר מכן, הפעילו את ה-gateway:

```bash
hermes gateway
```

שלחו לבוט שלכם הודעה כלשהי ב-Telegram כדי לבדוק. כעת תוכלו לשוחח עם הסוכן שלכם באמצעות הודעה פרטית ב-Telegram. עיינו ב[מדריך ההתקנה המלא של Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) עבור מצב webhook ואפשרויות מתקדמות.

---

## הצעדים הבאים

כעת, לאחר שהסוכן שלכם יכול לקבל פקודות מהטלפון שלכם ולפעול על המחשב המקומי שלכם, הנה שלושה כיוונים ששווה לחקור:

1. **תקציר מחקר אוטומטי**: תזמנו את Hermes לחפש ברשת נושאים שמעניינים אתכם כל בוקר, לסכם את הממצאים באמצעות המודל המקומי שלכם, ולשלוח תקציר לטלפון שלכם דרך Telegram או Discord, הכול פועל על החומרה שלכם ללא עלויות ענן.

2. **סקירת קוד לפי דרישה**: הפנו את Hermes למאגר GitHub, בקשו ממנו לסקור בקשות משיכה (pull requests) פתוחות, ותנו לו לפרסם תגובות או תקציר חזרה לצ'אט שלכם. עם backend מסוף ה-Docker, כל פעולות ה-git פועלות בתוך ה-sandbox, ושומרות על ניקיון המארח שלכם.

3. **עוזר קבצים מקומי**: תנו ל-Hermes גישה לתיקיית עבודה ובקשו ממנו לארגן, לשנות שם, לסכם או להמיר קבצים לפי דרישה מהטלפון שלכם. מכיוון שה-backend של מסוף ה-Docker מגביל את כל פעולות הכתיבה למרחב העבודה של ה-sandbox, פעולות הרסניות בטעות מוכלות ומוגבלות.