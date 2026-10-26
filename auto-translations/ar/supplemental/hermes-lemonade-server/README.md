<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

# تشغيل Hermes Agent محليًا باستخدام Lemonade Server

## نظرة عامة

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) هو وكيل ذكاء اصطناعي ذاتي التحسين من بناء Nous Research. يتميز بحلقة تعلم مدمجة، حيث يبني مهارات من الخبرة، ويبني ذاكرة دائمة حول من تكون عبر الجلسات، ويمكنه تشغيل أتمتة مجدولة نيابة عنك. على عكس مساعد محادثة بسيط، يقوم Hermes باتخاذ إجراءات فعلية: تشغيل أوامر shell، كتابة الملفات، تصفح الويب، وتفويض مسارات عمل متوازية إلى وكلاء فرعيين.

[**Lemonade Server**](https://lemonade-server.ai/) هو خلفية الاستدلال المحلية التي تشغّله. إنه خادم مفتوح المصدر يشغّل نماذج GenAI مباشرة على أجهزة AMD الخاصة بك ويعرضها عبر واجهة برمجة التطبيقات OpenAI API المعيارية في الصناعة.

معًا، يشكّلان مجموعة وكيل ذكاء اصطناعي محلية بالكامل: يتولى Lemonade استدلال النموذج على GPU الخاص بك، بينما يوفر Hermes حلقة الوكيل والذاكرة والمهارات وبوابة المراسلة.

> **قبل أن تتابع:** Hermes Agent هو وكيل ذكاء اصطناعي ذو استقلالية عالية. قد يؤدي منح أي وكيل ذكاء اصطناعي الوصول إلى نظامك إلى نتائج غير متوقعة أو غير مقصودة. تابع فقط إذا كنت تفهم المخاطر وترتاح لفكرة أن يتصرف برنامج مستقل نيابة عنك.

---

## ما ستتعلمه

بنهاية هذا الدليل التفصيلي، ستكون قادرًا على:

- **تثبيت Hermes Agent** وتوجيهه نحو **Lemonade Server** كخلفية ذكاء اصطناعي له.
- **(موصى به) تفعيل عزل Docker/Podman** لعزل إجراءات الوكيل عن جهازك المضيف.
- **بدء تشغيل بوابة Hermes** والتأكد من جاهزية وكيلك.
- **ربط قناة اتصال** (Discord أو Telegram) حتى تتمكن من الدردشة مع وكيلك من أي جهاز.

---

<!-- @device:halo_box,halo,stx,krk -->
## ضبط إعداد الذاكرة

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرامج الأساسية

<!-- @os:linux -->
- جهاز كمبيوتر يعمل بنظام **Ubuntu 24.04+** أو توزيعة Linux متوافقة قائمة على Debian مع `apt-get`
- ما لا يقل عن **12 جيجابايت من الذاكرة العشوائية (RAM)** (يوصى بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- **~10–30 جيجابايت من مساحة القرص الحرة** لأوزان النموذج
- [Podman](https://podman.io/docs/installation) (اختياري، لعزل Hermes Agent)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- جهاز كمبيوتر يعمل بنظام **Windows 10/11**
- ما لا يقل عن **12 جيجابايت من الذاكرة العشوائية (RAM)** (يوصى بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- **~10–30 جيجابايت من مساحة القرص الحرة** لأوزان النموذج
- Podman (اختياري، لعزل Hermes Agent). ثبّته داخل WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman مثبّت مسبقًا على Halo Box ولا حاجة لأي إعداد
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:hermes,lemonade-models-qwen3-6-35b-a3b,podman,lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## سحب وتحميل النموذج الموصى به

النموذج الموصى به لهذا الدليل التفصيلي هو **Qwen3.6-35B-A3B-GGUF** من Unsloth، وهو نموذج MoE قوي بنافذة سياق تبلغ 263 ألف رمز، وهو مناسب جدًا لأعباء عمل الوكلاء. يستخدم هذا النموذج التكميم UD-Q4_K_XL. اسحبه الآن:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

ثم قم بتحميله بنافذة سياق كبيرة واحفظ هذا الإعداد للتشغيلات المستقبلية:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

الطول الافتراضي للسياق في هذا النموذج هو 262,144 رمزًا. إذا واجهت أخطاء نفاد الذاكرة (OOM)، ففكّر في تقليل نافذة السياق.

> **نصيحة: تعطيل وضع التفكير للحصول على استجابات أسرع للوكيل:** يعمل Qwen3.6-35B-A3B في وضع التفكير بشكل افتراضي، مما يضيف تأخيرًا قبل كل استجابة. بالنسبة لحلقات الوكيل، يتراكم هذا العبء بسرعة. يوفر مستودع [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) تهيئة جاهزة تعطّل التفكير. لاستخدامها، نزّل الملف واستورده:
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

## إعداد WSL

نقوم بتشغيل Hermes Agent داخل WSL وربطه بـ Lemonade الذي يعمل بشكل أصلي على Windows. يمنحك هذا بيئة shell لينكس لـ Hermes مع الإبقاء على تسريع GPU الخاص بـ Lemonade على جانب Windows.

### تثبيت WSL وUbuntu

افتح PowerShell كمسؤول وثبّت نواة WSL:

```powershell
wsl --install --no-distribution
```

ثم ثبّت Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### تفعيل systemd في WSL

شغّل هذا داخل طرفية Ubuntu:

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

يعمل WSL2 في شبكة افتراضية. يرتبط Lemonade على Windows بـ `127.0.0.1`، والذي لا يمكن لـ WSL الوصول إليه مباشرة. يقوم وكيل منفذ Windows بإعادة توجيه حركة المرور من عنوان IP بوابة WSL إلى localhost الخاص بـ Windows.

**ابحث عن عنوان IP بوابة WSL الخاص بك** (شغّله داخل WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**أضف وكيل المنفذ** (شغّله في PowerShell كمسؤول، مع استبدال `<WSL-Gateway-IP>` بعنوان IP بوابة WSL الخاص بك):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**أضف قاعدة جدار حماية** (نفس PowerShell المرتفع الصلاحيات):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**تحقّق من WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

إذا كنت قد حمّلت بالفعل نموذج Qwen3.6-35B-A3B-GGUF في الخطوة السابقة، فيجب أن ترى مخرجات JSON تسرد نموذجك المحمّل.

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

> تبقى قاعدة `netsh portproxy` سارية بعد إعادة التشغيل، لكن عنوان IP بوابة WSL قد يتغيّر بعد تنفيذ `wsl --shutdown`. إذا أصبح Lemonade غير قابل للوصول من WSL بعد إعادة التشغيل، احصل على عنوان IP البوابة المحدّث وحدّث الوكيل بهذا العنوان الجديد.

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

## تثبيت Hermes Agent

<!-- @os:windows -->
> شغّل الأوامر في هذا القسم داخل **طرفية WSL** الخاصة بك ما لم يُذكر خلاف ذلك.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

يتخطى العلم `--skip-setup` معالج الإعداد التفاعلي حتى تتمكن من تهيئة خلفية النموذج يدويًا في الخطوة التالية.

أعد تحميل shell الخاص بك:

```bash
source ~/.bashrc
```

تأكد من التثبيت:

```bash
hermes --version
```

شغّل تشخيصًا ذاتيًا للتحقق من جميع الاعتماديات:

```bash
hermes doctor
```

> **نصيحة:** إذا ظهرت رسالة `command not found` بعد التثبيت، أضف Hermes إلى PATH الخاص بك:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> لجعل هذا دائمًا، أضف السطر أعلاه إلى ملف `~/.bashrc` أو `~/.zshrc` الخاص بك.

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
## تهيئة Hermes لاستخدام Lemonade

يُخزّن Hermes إعدادات النموذج الخاصة به في `~/.hermes/config.yaml`. يمكنك إما استخدام أداة اختيار `hermes model` التفاعلية أو كتابة الإعداد مباشرة.

### الخيار 1: الأداة التفاعلية

<!-- @os:windows -->
> نفّذ الأمر التالي داخل **طرفية WSL**.
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

عند المطالبة:

1. اختر **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** استخدم عنوان IP الخاص ببوابة WSL: نفّذ الأمر `ip route show default | awk '{print $3}' | head -1` داخل WSL للحصول عليه، ثم أدخل `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** اختر `Qwen3.6-35B-A3B-GGUF` من القائمة
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (أو أي اسم تفضله)

يحفظ `hermes model` كلًا من اختيار النموذج النشط ومُدخلًا مُسمّى في `custom_providers` يخزّن طول السياق إلى جانب نقطة النهاية. تبدو النتيجة في `~/.hermes/config.yaml` كما يلي:

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

### الخيار 2: كتابة الإعداد مباشرة

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

داخل طرفية WSL الخاصة بك، احصل على عنوان IP لجهاز Windows المضيف واكتب الإعداد:

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

## (موصى به) تفعيل عزل Podman

يمكن لـ Hermes Agent توجيه جميع عمليات الصدفة (shell) والملفات الخاصة بالوكيل عبر حاوية معزولة بدلًا من تنفيذها مباشرة على جهازك المضيف. وهذا يحدّ من نطاق أي إجراء غير مقصود ليقتصر على البيئة المعزولة (sandbox)، تاركًا نظام الملفات والشبكة الخاصين بجهازك المضيف دون أي تأثير.

ابنِ صورة sandbox خفيفة:

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
ادخل إلى طرفية WSL الخاصة بك:

```powershell
wsl -d Ubuntu-24.04
```

ثم، ابنِ صورة sandbox خفيفة:

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

ثم اضبط Hermes لاستخدام Podman كبيئة تشغيل الحاويات وحدّد واجهة الطرفية الخلفية (backend):

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> لا تزال قيمة `terminal.backend` هي `docker`.
> `HERMES_DOCKER_BINARY` هو ما يُخبر Hermes باستخدام Podman كبيئة تشغيل بدلًا من ذلك.

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

سيقوم Hermes الآن بتشغيل حاوية sandbox دائمة وتوجيه جميع استدعاءات `terminal` وأدوات الملفات عبرها. تشارك الحاوية دورة حياة عملية Hermes، ويُعاد استخدامها عبر جميع استدعاءات الأدوات، ويتم تدميرها عند إنهاء Hermes.

> **تحقّق من أن البيئة المعزولة تعمل:** شغّل Hermes (`hermes`) واطلب منه `run hostname` - يجب أن ترى معرّف حاوية قصير بدلًا من اسم مضيف جهازك. يمكنك أيضًا أن تطلب منه `rm -rf <path-to-a-dummy-file/folder>`: سيؤكد Hermes عملية الحذف، لكن المجلد سيظل موجودًا على جهازك المضيف. تم تنفيذ الأمر داخل `$HOME` المعزول الخاص بالحاوية، وليس داخل مجلدك الشخصي.

> **هل تحتاج إلى عزل أقوى؟** يوفر Hermes أيضًا صورة Docker رسمية (`nousresearch/hermes-agent`) تُشغّل عملية الوكيل بأكملها داخل حاوية - البوابة والأدوات وكل شيء. راجع [توثيق Hermes Docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker) للاطلاع على تفاصيل الإعداد.

---

<!-- @os:linux -->
## (موصى به) تكامل Hermes مع خدمات Firecrawl

يمكن لـ Hermes تصفّح واستخراج المحتوى من المواقع الإلكترونية باستخدام أدواته المدمجة للويب. لكن العديد من المواقع الحديثة تستخدم أنظمة لكشف الروبوتات، والتي تحجب طلبات HTTP البسيطة وتعيد صفحات تحدٍّ (challenge pages) بدلًا من المحتوى الفعلي. ونتيجة لذلك، قد يعجز Hermes عن استخراج المعلومات من هذه المواقع بشكل موثوق.

للتغلب على هذا القيد، يوفر [Firecrawl](https://docs.firecrawl.dev/introduction) خدمة ذاتية الاستضافة لزحف الويب واستخراج المحتوى، قادرة على تجاوز هذه التحديات وإطلاق العِنان لكامل إمكانات أتمتة Hermes.

في هذا الإعداد، يعمل Firecrawl كمجموعة من حاويات Docker المُدارة باستخدام Podman. ولتبسيط إدارة دورة الحياة والتشغيل التلقائي، نسجّل Firecrawl كخدمة `systemd` على مستوى المستخدم تُنظّم حزمة Podman Compose الأساسية. وهذا يسمح لـ Hermes ببدء وإيقاف والتحقق من خدمة Firecrawl باستخدام أوامر `systemctl --user` القياسية بدلًا من التفاعل مع الحاويات مباشرة.

للحفاظ على البساطة، قسّمنا العملية بأكملها إلى أربع خطوات:

---

### 1. تسجيل خدمة النظام
انتقل إلى دليل إعداد مستخدم systemd:
```bash
cd ~/.config/systemd/user
```
أنشئ وافتح ملفًا جديدًا باسم `firecrawl.service`.
```bash
nano firecrawl.service
```
انسخ والصق الإعداد التالي:
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
في هذه المرحلة، تم تعريف الخدمة لكن لم يتم تسجيلها بعد مع `systemd`.
تأكد من أن اسم الملف مطابق تمامًا لما أنشأته أعلاه، ثم نفّذ:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
إذا نجحت العملية، يجب أن ترى المخرجات التالية:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

يحتوي `default.target.wants/` على روابط رمزية إلى الخدمات المُعدّة للبدء تلقائيًا.

### 2. تهيئة Firecrawl لخدمتك

يُعد [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) مثاليًا لمن يحتاج إلى تحكم كامل في بيئات الزحف ومعالجة البيانات الخاصة به، لكنه يأتي مع عبء جهد إضافي للصيانة والتهيئة.

ابدأ باستنساخ المستودع:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
أنشئ ملف `.env` في الدليل الجذري `/firecrawl`:
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
> اضبط `BULL_AUTH_KEY` على سر قوي، خاصة في أي نشر يمكن الوصول إليه من شبكات غير موثوقة.
### 3. نشر Hermes عبر Compose

قبل المتابعة، تأكد من أنك قمت بسحب أحدث صورة Docker الخاصة بـ Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
بعد الانتهاء من ذلك، قم بتنزيل ملف Compose الخاص بـ Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) وضعه في المجلد الجذري `/firecrawl`:

> هذه القاعدة مطلوبة حتى يتمكن `systemd` من تحديد موقع الخدمة وتشغيلها بشكل صحيح كما هو محدد في `WorkingDirectory=${HOME}/firecrawl`.

> يمكنك دائمًا توسيع المجموعة بإضافة خدمات Firecrawl إضافية حسب الحاجة. يمكن العثور على القائمة الكاملة للخدمات المتاحة في ملف [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) الرسمي.

### 4. تشغيل خدمة Hermes عبر Firecrawl

قبل تسليم التحكم إلى `systemd`، تحقق من أن كل شيء يعمل بشكل صحيح عن طريق تشغيل المجموعة يدويًا:
```bash
podman compose -f hermes-compose.yaml up -d
```
إذا تم تكوين كل شيء بشكل صحيح، يجب أن ترى حاوية Hermes تعمل، وأن يبدو مخرج سطر الأوامر لديك مشابهًا لهذا:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

بمجرد التحقق من ذلك، أوقف تشغيل المجموعة قبل المتابعة:
```bash
podman compose -f hermes-compose.yaml down
```
بعد أن تم التحقق من كل شيء الآن، ابدأ تشغيل الخدمة عبر `systemd`:
```bash
systemctl --user start firecrawl.service
```
يمكن الوصول إلى [واجهة برمجة تطبيقات Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) من داخل الحاوية التفاعلية، كما تتوفر لوحة التحكم عبر الويب على نفس المضيف والمنفذ على العنوان http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

لإيقاف الخدمة، قم بتشغيل:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

ابدأ جلسة سطر أوامر تفاعلية مباشرة:

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

**تهانينا، لقد أنشأت مجموعة وكيل ذكاء اصطناعي محلية بالكامل.**

### لوحة التحكم عبر الويب

تتضمن Hermes واجهة مستخدم تعمل عبر المتصفح لإدارة التكوين ومفاتيح واجهة برمجة التطبيقات والنماذج والجلسات والذاكرة والمهام المجدولة. افتح طرفية ثانية أثناء تشغيل البوابة أو واجهة سطر الأوامر، وقم بتشغيلها باستخدام:

```bash
hermes dashboard
```

يؤدي هذا إلى تشغيل خادم محلي وفتح `http://127.0.0.1:9119` في متصفحك. راجع [توثيق لوحة التحكم](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) للحصول على مرجع الميزات الكامل.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## اختياري: ربط قناة تواصل

بمجرد تشغيل البوابة، يمكنك الوصول إلى وكيلك المحلي من أي جهاز. تدعم Hermes [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord) و [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) وغيرهما

---

### Discord

يتطلب Discord خادمًا تملك فيه **صلاحيات المسؤول** لإضافة بوت. إذا كنت تشارك خوادم ولكنك لا تملك واحدًا، استخدم Telegram بدلًا من ذلك.

#### إنشاء تطبيق وبوت Discord

1. انتقل إلى [بوابة مطوري Discord](https://discord.com/developers/applications) وانقر على **New Application**. أعطه اسمًا (مثل "hermes-bot").
2. في الشريط الجانبي، انقر على **Bot**. حدد اسم مستخدم للبوت.
3. أثناء وجودك في صفحة Bot، مرر لأسفل إلى **Privileged Gateway Intents** وفعّل:
   - **Message Content Intent** (مطلوب)
   - **Server Members Intent** (موصى به)
4. مرر لأعلى مجددًا وانقر على **Reset Token** لإنشاء رمز البوت الخاص بك. انسخه.

#### إضافة البوت إلى خادمك

1. في الشريط الجانبي، انقر على **OAuth2 / URL Generator**.
2. ضمن **Scopes**، فعّل `bot` و `applications.commands`.
3. ضمن **Bot Permissions**، فعّل: View Channels و Send Messages و Read Message History و Embed Links و Attach Files.
4. انسخ الرابط الذي تم إنشاؤه، والصقه في متصفحك، واختر خادمك، ثم أكّد.

#### جمع المعرّفات الخاصة بك والسماح بالرسائل المباشرة

فعّل وضع المطور في Discord (**User Settings / Advanced / Developer Mode**)، ثم:
- انقر بزر الفأرة الأيمن على أيقونة خادمك: **Copy Server ID**
- انقر بزر الفأرة الأيمن على صورتك الرمزية: **Copy User ID**

انقر بزر الفأرة الأيمن على أيقونة خادمك / **Privacy Settings** / وفعّل **Direct Messages**. هذا مطلوب لخطوة الاقتران.

#### تكوين Hermes لاستخدام Discord

أضف ما يلي إلى `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

ثم ابدأ تشغيل البوابة:

```bash
hermes gateway
```

يجب أن يصبح البوت متصلًا في Discord خلال ثوانٍ قليلة. أرسل له رسالة، سواء كانت رسالة مباشرة أو في قناة يمكنه رؤيتها.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### إنشاء بوت Telegram

1. افتح Telegram وراسل **@BotFather**.
2. أرسل `/newbot` واتبع التعليمات. احفظ رمز البوت الذي يُعطيك إياه.

#### تكوين Hermes لاستخدام Telegram

أضف ما يلي إلى `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **لا تعرف معرّف مستخدم Telegram الخاص بك؟** راسل [@userinfobot](https://t.me/userinfobot) في Telegram، وسيرد عليك بمعرّفك الرقمي.

ثم ابدأ تشغيل البوابة:

```bash
hermes gateway
```

أرسل أي رسالة إلى بوتك في Telegram للاختبار. يمكنك الآن التحدث مع وكيلك عبر رسالة مباشرة في Telegram. راجع [دليل إعداد Telegram الكامل](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) للاطلاع على وضع webhook والخيارات المتقدمة.

---

## الخطوات التالية

الآن بعد أن أصبح بإمكان وكيلك تلقي الأوامر من هاتفك والتصرف على جهازك المحلي، إليك ثلاثة اتجاهات تستحق الاستكشاف:

1. **ملخص أبحاث آلي**: قم بجدولة Hermes للبحث في الويب عن المواضيع التي تهمك كل صباح، وتلخيص النتائج باستخدام نموذجك المحلي، ودفع ملخص إلى هاتفك عبر Telegram أو Discord، كل ذلك يعمل على عتادك الخاص دون أي تكاليف سحابية.

2. **مراجعة الكود عند الطلب**: وجّه Hermes إلى مستودع على GitHub، واطلب منه مراجعة طلبات السحب المفتوحة، واجعله ينشر التعليقات أو ملخصًا في محادثتك. ومع واجهة طرفية Docker الخلفية، تعمل جميع عمليات git داخل البيئة المعزولة، مما يبقي جهازك المضيف نظيفًا.

3. **مساعد ملفات محلي**: امنح Hermes صلاحية الوصول إلى مجلد عمل واطلب منه تنظيم الملفات أو إعادة تسميتها أو تلخيصها أو تحويلها عند الطلب من هاتفك. ونظرًا لأن واجهة طرفية Docker الخلفية تحصر جميع عمليات الكتابة داخل مساحة عمل البيئة المعزولة، فإن أي عمليات تدميرية عرضية تبقى محصورة.