<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# تشغيل OpenClaw باستخدام Lemonade Server كخلفية

## نظرة عامة

[**OpenClaw**](https://openclaw.ai/) هو وكيل ذكاء اصطناعي مستقل قادر على كتابة الأكواد وتشغيلها، وإدارة الملفات، وإنجاز مهام معقدة متعددة الخطوات نيابةً عنك. وعلى عكس مساعد المحادثة الذي يكتفي بالإجابة عن الأسئلة، يقوم OpenClaw باتخاذ إجراءات فعلية على نظامك، مما يعني أنه بحاجة إلى خلفية ذكاء اصطناعي سريعة وقادرة تستطيع مواكبة حلقة عمل الوكيل المتطلبة.

[**Lemonade Server**](https://lemonade-server.ai/) هو تلك الخلفية. إنه خادم استدلال محلي مفتوح المصدر يقوم بتشغيل نماذج GenAI مباشرةً على أجهزتك ويتيحها من خلال واجهة برمجة تطبيقات OpenAI القياسية في الصناعة.

معًا، يشكلان مجموعة وكيل ذكاء اصطناعي محلية بالكامل: يتولى Lemonade استدلال النموذج، بينما يوفر OpenClaw حلقة الوكيل التي تحوّل مخرجات النموذج إلى إجراءات فعلية.

> **قبل أن تتابع:** OpenClaw هو وكيل ذكاء اصطناعي ذو استقلالية عالية. قد يؤدي منح أي وكيل ذكاء اصطناعي صلاحية الوصول إلى نظامك إلى نتائج غير متوقعة أو غير مقصودة. تابع فقط إذا كنت تفهم المخاطر وتشعر بالارتياح تجاه قيام برنامج مستقل بالتصرف نيابةً عنك.

---

## ما ستتعلمه

بنهاية هذا الدليل ستكون قادرًا على:

- التعرف على **Lemonade Server**
- **تثبيت OpenClaw** و**توجيهه نحو Lemonade Server** كخلفية ذكاء اصطناعي له.
- **بدء تشغيل بوابة OpenClaw** والتأكد من جاهزية وكيلك للعمل.
- **ربط قناة تواصل** (Discord أو Telegram) لتتمكن من محادثة وكيلك من أي جهاز.

---

## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرامج الأساسية

<!-- @os:linux -->
- جهاز كمبيوتر يعمل بنظام **Ubuntu 24.04+** أو توزيعة لينكس متوافقة قائمة على Debian مزودة بـ `apt-get`
- ما لا يقل عن **12 غيغابايت من ذاكرة الوصول العشوائي** (يُوصى بـ 64 غيغابايت أو أكثر للنماذج الأكبر)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (اختياري، لعزل OpenClaw داخل بيئة معزولة)

- **~10-30 غيغابايت من مساحة القرص الفارغة** لأوزان النموذج
<!-- @os:end -->
<!-- @os:windows -->
- جهاز كمبيوتر يعمل بنظام **Windows 10/11**
- ما لا يقل عن **12 غيغابايت من ذاكرة الوصول العشوائي** (يُوصى بـ 64 غيغابايت أو أكثر للنماذج الأكبر)
- **~10-30 غيغابايت من مساحة القرص الفارغة** لأوزان النموذج
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (اختياري، لعزل OpenClaw داخل بيئة معزولة)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## سحب النموذج الموصى به وتحميله

النموذج الموصى به لهذا الدليل هو **Qwen3.6-35B-A3B-GGUF** من Unsloth، وهو نموذج MoE قوي بنافذة سياق تبلغ 263 ألف رمز، ويناسب أعباء عمل الوكلاء بشكل جيد. يستخدم هذا النموذج التكميم UD-Q4_K_XL. قم بسحبه الآن:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

ثم قم بتحميله بنافذة سياق كبيرة واحفظ هذا الإعداد للتشغيلات المستقبلية:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

يبلغ طول السياق الافتراضي للنموذج 262,144 رمزًا. إذا واجهت أخطاء نفاد الذاكرة (OOM)، ففكر في تقليل نافذة السياق. ومع ذلك، ونظرًا لأن Qwen3.6 يستفيد من السياق الموسّع للمهام المعقدة، فإننا ننصح بالحفاظ على طول سياق لا يقل عن 128 ألف رمز للحفاظ على قدرات التفكير.

> **نصيحة: تعطيل وضع التفكير للحصول على استجابات أسرع من الوكيل:** يعمل Qwen3.6-35B-A3B في وضع التفكير افتراضيًا، مما يضيف زمن استجابة قبل كل رد. بالنسبة لحلقات الوكيل، يتراكم هذا العبء الإضافي بسرعة. يوفر مستودع [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) تهيئة جاهزة تعطّل وضع التفكير. لاستخدامها، قم بتنزيل الملف واستيراده:
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

## إعداد WSL

نقوم بتشغيل OpenClaw داخل WSL (موصى به) وربطه بـ Lemonade الذي يعمل بشكل أصلي على Windows. يمنحك هذا بيئة صدفة لينكس لتشغيل OpenClaw مع الحفاظ على تسريع GPU الخاص بـ Lemonade على جانب Windows.

### تثبيت WSL و Ubuntu

افتح PowerShell كمسؤول وقم بتثبيت نواة WSL:

```powershell
wsl --install --no-distribution
```

ثم قم بتثبيت Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### تفعيل systemd في WSL

قم بتشغيل هذا داخل طرفية Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

أعد تشغيل WSL:

```powershell
wsl --shutdown
wsl
```

### ربط Lemonade من Windows إلى WSL

يعمل WSL2 في شبكة افتراضية. يرتبط Lemonade على Windows بـ `127.0.0.1`، والذي لا يستطيع WSL الوصول إليه مباشرةً. يقوم وكيل منفذ Windows بإعادة توجيه حركة المرور من عنوان IP الخاص ببوابة WSL إلى المضيف المحلي على Windows.

**ابحث عن عنوان IP الخاص ببوابة WSL** (قم بتشغيل هذا داخل WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**أضف وكيل المنفذ** (قم بتشغيل هذا في PowerShell كمسؤول، مع استبدال `<WSL-Gateway-IP>` بعنوان IP الخاص ببوابة WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**أضف قاعدة جدار حماية** (في نفس نافذة PowerShell المرتفعة الصلاحيات):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**تحقق من ذلك من داخل WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

إذا كنت قد قمت بالفعل بتحميل نموذج Qwen3.6-35B-A3B-GGUF في الخطوة السابقة، فمن المفترض أن تظهر لك مخرجات JSON مثل هذه:

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

> تظل قاعدة `netsh portproxy` سارية بعد إعادة التشغيل، لكن عنوان IP الخاص ببوابة WSL قد يتغير بعد تنفيذ `wsl --shutdown`. إذا أصبح Lemonade غير قابل للوصول من WSL بعد إعادة التشغيل، فاحصل على عنوان IP المحدّث للبوابة وقم بتحديث الوكيل بهذا العنوان الجديد.

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

## تثبيت وتهيئة OpenClaw

### تثبيت OpenClaw
<!-- @os:windows -->
> قم بتشغيل الأوامر الواردة في هذا القسم داخل **طرفية WSL** الخاصة بك.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

تعمل العلامة `--no-onboard` على تخطي معالج الإعداد التفاعلي، حيث ستقوم بتهيئة خلفية النموذج يدويًا في الخطوة التالية، مما يمنحك تحكمًا دقيقًا في النموذج والخادم المستخدمين.

افتح طرفية جديدة وتأكد من التثبيت:

```bash
openclaw --version
```

> **نصيحة:** إذا ظهرت لك رسالة `command not found` بعد التثبيت، فأضف دليل npm العام إلى متغير PATH الخاص بك:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> لجعل هذا الإعداد دائمًا، أضف السطر أعلاه إلى ملف `~/.bashrc` أو `~/.zshrc` الخاص بك.

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
### تهيئة OpenClaw لاستخدام Lemonade

قم بتشغيل عملية الإعداد غير التفاعلية الخاصة بـ OpenClaw.
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

يقوم هذا الأمر بكتابة تهيئة OpenClaw إلى `~/.openclaw/openclaw.json`.

> **ضبط حجم نافذة السياق في OpenClaw:** يتم تفعيل عملية الضغط (compaction) في OpenClaw عندما تكون `contextTokens > contextWindow − reserveTokens`. القيمة الافتراضية لـ `reserveTokensFloor` هي 20,000 رمز، وهي حد أدنى يتجاوز `reserveTokens` عندما تكون أقل منه، لذا فإن أي نافذة سياق للنموذج أقل من حوالي 37 ألف رمز ستؤدي إلى حلقة ضغط لا نهائية. اضبط قيمة احتياطية منخفضة وعطّل الحد الأدنى مرة واحدة في التهيئة الخاصة بك ليُطبَّق ذلك على كل نموذج، دون الحاجة لضبط منفصل لكل نموذج:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` هو *حد أدنى* (ضمانة دنيا)، وليس القيمة الاحتياطية نفسها، وضبط الحد الأدنى فقط لن يكون له أي تأثير. تعطيل `reserveTokensFloor: 0` يُلغي هذه الضمانة بحيث تُقبل القيمة الأدنى لـ `reserveTokens`.
>
> **متى تُطبّق هذا:** استخدم هذه التهيئة إذا كانت نافذة السياق الفعلية لنموذجك أقل من حوالي 37 ألف رمز، سواء كان ذلك لأن النموذج صغير (مثل 8 آلاف، أو 16 ألف، أو 32 ألف)، أو لأنك حددت عمدًا قيمة أقل (مثل تحميل نموذج بسعة 128 ألف رمز مع ضبط السياق على 16 ألف في Lemonade). بدون ذلك، سيدخل OpenClaw في حلقة ضغط لا نهائية عند بدء التشغيل.
>
> **النماذج ذات نافذة السياق الكبيرة عند السعة الكاملة:** يمكنك تجاوز هذا الأمر تمامًا. تعمل الإعدادات الافتراضية بشكل جيد، حيث تبدأ عملية الضغط قبل امتلاء النافذة بوقت كافٍ، ويتوفر للنموذج مساحة كافية لتوليد استجابات طويلة. إذا طبّقت هذا الإعداد رغم ذلك، فاعلم أن `reserveTokens: 4096` يحد طول الاستجابة إلى حوالي 4 آلاف رمز، مما قد يقطع توليد الملفات الطويلة أو الخطط التفصيلية.
>
> **أين تُضيف هذا:** ضع كتلة `compaction` داخل `agents.defaults` في ملف `openclaw.json` الخاص بك (عادةً في `~/.openclaw/openclaw.json`):
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
> بقية التهيئة الخاصة بك (البوابة، القنوات، النماذج، إلخ) تبقى دون تغيير، ولا يلزم إضافة سوى مفتاح `compaction`.

### (موصى به) تفعيل العزل الرملي عبر Docker

يمكن لـ OpenClaw توجيه جميع عمليات الملفات والأكواد الخاصة بالعميل عبر حاوية Docker معزولة بدلًا من تشغيلها مباشرة على جهازك المضيف. يحد هذا من نطاق تأثير أي إجراء غير مقصود ليقتصر على البيئة المعزولة، مع الحفاظ على سلامة نظام الملفات والشبكة في جهازك المضيف.

قم ببناء صورة البيئة المعزولة مرة واحدة (يجب أن يكون Docker مثبتًا):

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

قم بتشغيل هذا الأمر لإضافة المفتاح `sandbox` داخل كتلة `agents.defaults` الموجودة في `~/.openclaw/openclaw.json`:

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

لا تملك حاويات البيئة المعزولة أي **وصول إلى الشبكة** افتراضيًا. راجع [مرجع العزل الرملي](https://docs.openclaw.ai/gateway/sandboxing) للتعرف على تثبيتات الربط (bind mounts) وتجاوزات الشبكة.

> #### استكشاف الأخطاء وإصلاحها: رفض إذن Docker
> 
> إذا واجهت رسالة "permission denied" عند تشغيل أوامر Docker:
> 
> **الخطوة 1: أضف مستخدمك إلى مجموعة docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **الخطوة 2: إذا استمر الخطأ، طبّق الحل الدائم**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> ثم قم **بإعادة تشغيل** نظامك.
> 
> **حل مؤقت سريع** (يُعاد ضبطه بعد إعادة التشغيل):
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

### تشغيل بوابة OpenClaw

البوابة هي عملية OpenClaw التي تدير حلقة العميل وتقدّم لوحة التحكم:

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

لفتح لوحة التحكم، شغّل هذا الأمر في نافذة طرفية ثانية بينما لا تزال البوابة قيد التشغيل:

```bash
openclaw dashboard
```

نظرًا لأن البوابة ترتبط بالمنفذ المحلي (loopback)، فإن لوحة التحكم تُصادق تلقائيًا عند فتحها من نفس الجهاز، ولا حاجة لإدخال رمز أو موافقة الجهاز للوصول المحلي. يجب أن تشاهد لوحة تحكم OpenClaw مع ظهور نموذج Lemonade الخاص بك كخلفية نشطة.

> إذا قمت بتفعيل العزل الرملي، يمكنك التحقق من ذلك بأن تطلب من العميل تنفيذ `run hostname` من لوحة التحكم. إذا شاهدت معرّف حاوية قصيرًا بدلًا من اسم مضيف جهازك، فهذا يعني أن البيئة المعزولة تعمل بنجاح.

**تهانينا، لقد قمت ببناء منظومة وكيل ذكاء اصطناعي محلية بالكامل من الصفر.**

> **بحاجة إلى رمز البوابة؟** شغّل `openclaw dashboard --no-open` لطباعة رابط لوحة التحكم مع تضمين الرمز فيه (كما يحاول نسخه إلى الحافظة تلقائيًا). بدلًا من ذلك، يمكنك إيجاد الرمز في `gateway.auth.token` ضمن `~/.openclaw/openclaw.json`.
>
> **الموافقة على جهاز عن بُعد:** عند فتح لوحة التحكم من جهاز ثانٍ أو هاتف، يعرض المتصفح معرّف طلب. عد إلى الجهاز الذي يشغّل البوابة وشغّل:
> ```bash
> openclaw devices approve <requestId>
> ```
> هذا مطلوب فقط للأجهزة البعيدة أو الثانوية، حيث يتم المصادقة تلقائيًا عند الوصول المحلي من نفس الجهاز.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## اختياري: ربط قناة تواصل

بمجرد تشغيل البوابة، يمكنك الوصول إلى عميلك المحلي من أي جهاز. اختر الخيار الذي يناسب إعدادك. يدعم OpenClaw [Discord](https://docs.openclaw.ai/channels/discord)، و[Telegram](https://docs.openclaw.ai/channels/telegram)، وقنوات أخرى، راجع القائمة الكاملة على [docs.openclaw.ai](https://docs.openclaw.ai).

---

### الخيار أ: Discord

يتطلب Discord وجود خادم **تملك عليه صلاحيات المسؤول (administrator)** لإضافة بوت. إذا كنت تشارك خوادم دون امتلاك أي منها، استخدم الخيار ب (Telegram) بدلًا من ذلك.
#### إنشاء حساب Discord وسيرفر

إذا لم يكن لديك حساب Discord، سجّل في [discord.com](https://discord.com). ستحتاج أيضًا إلى سيرفر تكون فيه مسؤولًا، أنشئ واحدًا بالنقر على أيقونة **+** في الشريط الجانبي لـ Discord واختيار **Create My Own**. سيرفر خاص يفي بالغرض.

#### إنشاء تطبيق وبوت Discord

1. اذهب إلى [Discord Developer Portal](https://discord.com/developers/applications) وانقر **New Application**. أعطه اسمًا (مثل "openclaw-bot").
2. في الشريط الجانبي، انقر **Bot**. عيّن اسم مستخدم للبوت.
3. لا تزال في صفحة Bot، مرر للأسفل إلى **Privileged Gateway Intents** وفعّل:
   - **Message Content Intent** (مطلوب)
   - **Server Members Intent** (موصى به)
4. مرر للأعلى مجددًا وانقر **Reset Token** لتوليد رمز البوت الخاص بك. انسخه.

#### إضافة البوت إلى سيرفرك

1. في الشريط الجانبي، انقر **OAuth2/ URL Generator**.
2. تحت **Scopes**، فعّل `bot` و`applications.commands`.
3. تحت **Bot Permissions**، فعّل: View Channels، Send Messages، Read Message History، Embed Links، Attach Files.
4. انسخ الرابط المُولَّد، الصقه في متصفحك، اختر سيرفرك، وأكّد. يجب أن يظهر البوت الآن في قائمة أعضاء سيرفرك.

#### جمع معرّفاتك (IDs)

فعّل وضع المطور في Discord (**User Settings/ Advanced/ Developer Mode**)، ثم:
- انقر بزر الفأرة الأيمن على أيقونة سيرفرك: **Copy Server ID**
- انقر بزر الفأرة الأيمن على صورتك الرمزية: **Copy User ID**

#### السماح بالرسائل المباشرة من أعضاء السيرفر

انقر بزر الفأرة الأيمن على أيقونة سيرفرك/ **Privacy Settings**/ فعّل خيار **Direct Messages**. هذا يسمح للبوت بمراسلتك مباشرةً، وهو مطلوب لخطوة الاقتران.

#### إعداد OpenClaw لـ Discord

خزّن رمز البوت الخاص بك كمتغير بيئة، ثم أنشئ ملف تصحيح واحد يفعّل Discord، ويشير إلى الرمز، ويضيف سيرفرك إلى القائمة المسموح بها. استبدل `<server_id>` و`<user_id>` بالمعرّفات التي جمعتها أعلاه.

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

> **لا تعتمد على مطالبة الوكيل بإعداد هذا.** عند تفعيل العزل (sandboxing)، لا يمكن للوكيل الكتابة إلى `~/.openclaw/openclaw.json` من داخل بيئة العزل، استخدم أوامر CLI أعلاه على الجهاز المضيف بدلًا من ذلك.

أعد تشغيل البوابة (gateway) لتطبيق إعدادات القناة الجديدة:

```bash
openclaw gateway run --bind loopback --port 18789
```

يجب أن تشاهد `logged in to discord as <bot-name>` في مخرجات البوابة خلال ثوانٍ قليلة.

#### اقتران حساب Discord الخاص بك

راسل البوت مباشرةً في Discord. سيرد عليك برمز اقتران قصير.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

وافق عليه على الجهاز الذي يشغّل OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> تنتهي صلاحية رموز الاقتران بعد ساعة واحدة.

يمكنك الآن الدردشة مع وكيلك مباشرةً من Discord وتفويض المهام إلى جهازك المحلي.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### الخيار ب: Telegram

يُعد Telegram أبسط من Discord لمعظم المستخدمين، فهو لا يتطلب سيرفرًا ولا صلاحيات إدارية.

#### إنشاء بوت Telegram

1. افتح Telegram وراسل **@BotFather**.
2. أرسل `/newbot` واتبع التعليمات. احفظ رمز البوت الذي يعطيك إياه.

#### إعداد OpenClaw لـ Telegram

خزّن الرمز كمتغير بيئة:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

أضف تكوين القناة إلى `~/.openclaw/openclaw.json` (أو صحّحه عبر لوحة التحكم):

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

أعد تشغيل البوابة، ثم أرسل لبوتك أي رسالة في Telegram. وافق على الاقتران:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

تنتهي صلاحية رموز الاقتران بعد ساعة واحدة. يمكنك الآن الدردشة مع وكيلك عبر رسائل Telegram المباشرة.

---

## الخطوات التالية

بعد أن أصبح بإمكان وكيلك تلقي الأوامر من هاتفك والتصرف على جهازك المحلي، إليك ثلاثة اتجاهات تستحق الاستكشاف:

1. **ملخّص سوق الأسهم**: جدول OpenClaw لجلب البيانات من واجهات برمجة التطبيقات المالية على فترات ثابتة، ولخّص تحركات اليوم باستخدام نموذجك المحلي، وأرسل ملخصًا إلى هاتفك كل صباح عبر القناة التي اخترتها.

2. **مراقب الضبط الدقيق (fine-tuning)**: ابدأ مهمة تدريب عن بُعد عبر Telegram أو Discord، ثم اجعل الوكيل يتابع سجل التدريب ويبلغك دوريًا بقيم الخسارة، ونسبة استخدام GPU، ومساحة القرص المتبقية على هاتفك. إذا توقفت العملية أو ارتفع استخدام VRAM بشكل مفاجئ، ستعرف ذلك فورًا دون الحاجة إلى التواجد أمام الجهاز.

3. **إنترنت الأشياء (IOT) مع نموذج رؤية محلي (VLM)**: وجّه كاميرا نحو باب منزلك، وشغّل نموذج رؤية على Lemonade، واجعل OpenClaw يحلل الإطارات عند الطلب أو عند حدوث محفّز معين. اسأل "هل وصلت أي طرود اليوم؟" من هاتفك واحصل على إجابة مباشرة من عتادك الخاص.