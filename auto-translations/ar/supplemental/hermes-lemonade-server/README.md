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

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) هو وكيل ذكاء اصطناعي ذاتي التحسين من تطوير Nous Research. يمتلك حلقة تعلم مدمجة، ويُنشئ مهارات من التجربة، ويبني ذاكرة دائمة عنك عبر الجلسات، ويمكنه تشغيل عمليات أتمتة مجدولة نيابةً عنك. على عكس مساعد الدردشة البسيط، يقوم Hermes بتنفيذ إجراءات فعلية: تشغيل أوامر shell، وكتابة الملفات، وتصفح الويب، وتفويض مهام متوازية إلى وكلاء فرعيين (subagents).

[**Lemonade Server**](https://lemonade-server.ai/) هو محرك الاستدلال المحلي الذي يشغّله. إنه خادم مفتوح المصدر يقوم بتشغيل نماذج GenAI مباشرةً على أجهزة AMD الخاصة بك ويعرضها عبر واجهة برمجة التطبيقات القياسية في الصناعة OpenAI API.

معًا، يشكّلان حزمة وكيل ذكاء اصطناعي محلية بالكامل: يتولى Lemonade عملية استدلال النموذج على GPU الخاص بك، بينما يوفر Hermes حلقة الوكيل، والذاكرة، والمهارات، وبوابة المراسلة.

> **قبل المتابعة:** Hermes Agent هو وكيل ذكاء اصطناعي ذو استقلالية عالية. قد يؤدي منح أي وكيل ذكاء اصطناعي إمكانية الوصول إلى نظامك إلى نتائج غير متوقعة أو غير مقصودة. تابع فقط إذا كنت تفهم المخاطر وتشعر بالارتياح تجاه برنامج مستقل يتصرف نيابةً عنك.

---

## ما الذي ستتعلمه

بنهاية هذا الدليل ستكون قادرًا على:

- **تثبيت Hermes Agent** وتوجيهه نحو **Lemonade Server** كخلفية ذكاء اصطناعي له.
- **(موصى به) تفعيل عزل Docker/Podman** لعزل إجراءات الوكيل عن جهازك المضيف.
- **بدء تشغيل بوابة Hermes** والتأكد من جاهزية وكيلك.
- **ربط قناة اتصال** (Discord أو Telegram) حتى تتمكن من الدردشة مع وكيلك من أي جهاز.

---

<!-- @device:halo_box,halo,stx,krk -->
## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرمجيات

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرمجيات

<!-- @os:linux -->
- جهاز يعمل بنظام **Ubuntu 24.04+** أو توزيعة لينكس متوافقة قائمة على Debian مع `apt-get`
- ما لا يقل عن **12 جيجابايت من ذاكرة الوصول العشوائي (RAM)** (يُوصى بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- **~10-30 جيجابايت من مساحة القرص الخالية** لأوزان النموذج
- [Podman](https://podman.io/docs/installation) (اختياري، لعزل Hermes Agent)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- جهاز يعمل بنظام **Windows 10/11**
- ما لا يقل عن **12 جيجابايت من ذاكرة الوصول العشوائي (RAM)** (يُوصى بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- **~10-30 جيجابايت من مساحة القرص الخالية** لأوزان النموذج
- Podman (اختياري، لعزل Hermes Agent). قم بالتثبيت داخل WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman مثبّت مسبقًا على Halo Box ولا حاجة لأي إعداد
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## سحب النموذج الموصى به وتحميله

النموذج الموصى به لهذا الدليل هو **Qwen3.6-35B-A3B-GGUF** من Unsloth، وهو نموذج MoE قوي بنافذة سياق تبلغ 263 ألف رمز، مناسب تمامًا لأعباء عمل الوكلاء. يستخدم هذا النموذج تكميم UD-Q4_K_XL. قم بسحبه الآن:

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

يبلغ طول السياق الافتراضي للنموذج 262,144 رمزًا. إذا واجهت أخطاء نفاد الذاكرة (OOM)، ففكّر في تقليل نافذة السياق.

> **نصيحة: تعطيل وضع التفكير للحصول على استجابات أسرع للوكيل:** يعمل Qwen3.6-35B-A3B في وضع التفكير افتراضيًا، مما يضيف زمن استجابة قبل كل رد. بالنسبة لحلقات الوكيل، يتراكم هذا العبء بسرعة. يوفر مستودع [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) تكوينًا جاهزًا يعطّل التفكير. لاستخدامه، قم بتنزيل الملف واستيراده:
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

نقوم بتشغيل Hermes Agent داخل WSL وربطه بـ Lemonade الذي يعمل بشكل أصلي على Windows. يمنحك هذا بيئة سطر أوامر Linux لـ Hermes مع الاحتفاظ بتسريع GPU الخاص بـ Lemonade على جانب Windows.

### تثبيت WSL و Ubuntu

افتح PowerShell كمسؤول (Administrator) وقم بتثبيت نواة WSL:

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

يعمل WSL2 ضمن شبكة افتراضية. يرتبط Lemonade على Windows بالعنوان `127.0.0.1`، والذي لا يمكن لـ WSL الوصول إليه مباشرةً. يقوم وكيل منفذ Windows (port proxy) بإعادة توجيه حركة المرور من عنوان IP الخاص ببوابة WSL إلى localhost في Windows.

**اعثر على عنوان IP الخاص ببوابة WSL** (شغّل داخل WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**أضف وكيل المنفذ** (شغّل في PowerShell كمسؤول، مع استبدال `<WSL-Gateway-IP>` بعنوان IP الخاص ببوابة WSL لديك):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**أضف قاعدة جدار حماية** (نفس نافذة PowerShell المرتفعة الصلاحيات):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**تحقّق من داخل WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

إذا كنت قد قمت بالفعل بتحميل نموذج Qwen3.6-35B-A3B-GGUF في الخطوة السابقة، فيجب أن ترى مخرجات JSON تسرد النموذج المحمّل لديك.

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

> تبقى قاعدة `netsh portproxy` سارية بعد إعادة التشغيل، لكن عنوان IP الخاص ببوابة WSL قد يتغير بعد تنفيذ `wsl --shutdown`. إذا أصبح Lemonade غير قابل للوصول من WSL بعد إعادة التشغيل، احصل على عنوان IP المحدّث للبوابة وقم بتحديث الوكيل بهذا العنوان الجديد.

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
> قم بتشغيل الأوامر في هذا القسم داخل **طرفية WSL** ما لم يُذكر خلاف ذلك.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

تُستخدم العلامة `--skip-setup` لتخطي معالج الإعداد التفاعلي حتى تتمكن من تكوين خلفية النموذج يدويًا في الخطوة التالية.

أعد تحميل الطرفية الخاصة بك:

```bash
source ~/.bashrc
```

تأكد من التثبيت:

```bash
hermes --version
```

قم بتشغيل تشخيص ذاتي للتحقق من جميع التبعيات:

```bash
hermes doctor
```

> **نصيحة:** إذا ظهرت لك رسالة `command not found` بعد التثبيت، أضف Hermes إلى PATH الخاص بك:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> لجعل هذا التغيير دائمًا، أضف السطر أعلاه إلى ملف `~/.bashrc` أو `~/.zshrc` الخاص بك.

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

يخزّن Hermes إعدادات النموذج الخاصة به في `~/.hermes/config.yaml`. يمكنك إما استخدام أداة اختيار `hermes model` التفاعلية أو كتابة الإعدادات مباشرةً.

### الخيار 1: أداة الاختيار التفاعلية

<!-- @os:windows -->
> شغّل ما يلي داخل **طرفية WSL** الخاصة بك.
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

عند الطلب:

1. اختر **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **رابط الأساس (API base URL):** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **رابط الأساس (API base URL):** استخدم عنوان IP الخاص ببوابة WSL: شغّل `ip route show default | awk '{print $3}' | head -1` داخل WSL للحصول عليه، ثم أدخل `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **مفتاح API:** `lemonade`
4. **وضع توافق API:** `1` (اكتشاف تلقائي)
5. **اختر النموذج:** اختر `Qwen3.6-35B-A3B-GGUF` من القائمة
6. **طول السياق بالرموز:** `262144`
7. **الاسم المعروض:** `local-lemonade` (أو أي اسم تفضله)

يحفظ `hermes model` كلًا من اختيار النموذج النشط وإدخال `custom_providers` مسمّى يخزّن طول السياق إلى جانب نقطة النهاية. تبدو النتيجة في `~/.hermes/config.yaml` كما يلي:

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

### الخيار 2: كتابة الإعدادات مباشرةً

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

داخل طرفية WSL الخاصة بك، احصل على عنوان IP لمضيف Windows واكتب الإعدادات:

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

يمكن لـ Hermes Agent توجيه جميع عمليات الصدفة والملفات الخاصة بالوكيل عبر حاوية معزولة بدلًا من تشغيلها مباشرةً على مضيفك. وهذا يحد من نطاق تأثير أي إجراء غير مقصود ليقتصر على بيئة العزل، تاركًا نظام ملفات مضيفك وشبكتك بلا تأثير.

قم ببناء صورة عزل خفيفة الوزن:

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

ثم قم ببناء صورة عزل خفيفة الوزن:

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

بعد ذلك قم بتهيئة Hermes لاستخدام Podman كوقت تشغيل الحاويات، وحدد الواجهة الخلفية للطرفية:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> لا تزال قيمة `terminal.backend` هي `docker`.
> `HERMES_DOCKER_BINARY` هو ما يخبر Hermes باستخدام Podman كوقت تشغيل بدلًا من ذلك.

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

سيقوم Hermes الآن بتشغيل حاوية عزل دائمة وتوجيه جميع استدعاءات `terminal` وأدوات الملفات عبرها. تشارك الحاوية دورة حياة عملية Hermes، ويُعاد استخدامها عبر جميع استدعاءات الأدوات، ويتم تدميرها عند إنهاء Hermes.

> **تحقق من عمل بيئة العزل:** شغّل Hermes (`hermes`) واطلب منه `run hostname` — يجب أن ترى معرّف حاوية قصير بدلًا من اسم مضيف جهازك. يمكنك أيضًا أن تطلب منه `rm -rf <path-to-a-dummy-file/folder>`: سيؤكد Hermes الحذف، لكن المجلد سيظل موجودًا على مضيفك. تم تشغيل الأمر داخل مجلد `$HOME` المعزول الخاص بالحاوية، وليس مجلدك.

> **هل تحتاج إلى عزل أقوى؟** يوفر Hermes أيضًا صورة Docker رسمية (`nousresearch/hermes-agent`) تشغّل عملية الوكيل بأكملها داخل حاوية — البوابة والأدوات وكل شيء. راجع [وثائق Hermes Docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker) للحصول على تفاصيل الإعداد.

---

<!-- @os:linux -->
## (موصى به) تكامل Hermes مع خدمات Firecrawl

يمكن لـ Hermes تصفح المواقع واستخراج المحتوى منها باستخدام أدوات الويب المدمجة الخاصة به. ومع ذلك، تستخدم العديد من المواقع الحديثة أنظمة كشف الروبوتات، والتي تحظر طلبات HTTP البسيطة وتعيد صفحات تحدٍّ (challenge pages) بدلًا من المحتوى الفعلي. ونتيجةً لذلك، قد يعجز Hermes عن استخراج المعلومات من هذه المواقع بشكل موثوق.

للتغلب على هذا القيد، توفّر [Firecrawl](https://docs.firecrawl.dev/introduction) خدمة زحف واستخراج محتوى ويب ذاتية الاستضافة يمكنها تجاوز هذه التحديات وإطلاق العنان للإمكانات الكاملة لأتمتة Hermes.

في هذا الإعداد، يعمل Firecrawl كمجموعة من حاويات Docker المُدارة باستخدام Podman. ولتبسيط إدارة دورة الحياة والتشغيل التلقائي، نسجّل Firecrawl كخدمة `systemd` على مستوى المستخدم تنظّم حزمة Podman Compose الأساسية. وهذا يتيح لـ Hermes بدء خدمة Firecrawl وإيقافها والتحقق منها باستخدام أوامر `systemctl --user` القياسية بدلًا من التفاعل مع الحاويات مباشرةً.

للحفاظ على البساطة، قسّمنا العملية بأكملها إلى أربع خطوات:

---

### 1. تسجيل خدمة النظام
انتقل إلى دليل إعدادات systemd الخاص بالمستخدم:
```bash
cd ~/.config/systemd/user
```
أنشئ ملفًا جديدًا وافتحه باسم `firecrawl.service`.
```bash
nano firecrawl.service
```
انسخ والصق الإعدادات التالية:
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
في هذه المرحلة، تم تعريف الخدمة لكن لم يتم تسجيلها بعد لدى `systemd`.
تأكد من أن اسم الملف يطابق تمامًا ما أنشأته أعلاه، ثم شغّل:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
إذا نجحت العملية، فيجب أن ترى المخرجات التالية:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

يحتوي `default.target.wants/` على روابط رمزية للخدمات المهيأة لتبدأ تلقائيًا.

### 2. تهيئة Firecrawl لخدمتك

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) مثالي لمن يحتاج إلى تحكم كامل في بيئات الزحف ومعالجة البيانات الخاصة به، لكنه يأتي مقابل جهد إضافي في الصيانة والإعداد.

ابدأ باستنساخ المستودع:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
أنشئ ملف `.env` في الدليل الجذر `/firecrawl`:
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
> اضبط `BULL_AUTH_KEY` على قيمة سرّية قوية، خاصة في أي عملية نشر يمكن الوصول إليها من شبكات غير موثوقة.
### 3. نشر Hermes عبر Compose

قبل المتابعة، تأكد من أنك قمت بسحب أحدث صورة Docker الخاصة بـ Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
بمجرد الانتهاء من ذلك، قم بتنزيل ملف Compose الخاص بـ Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) وضعه في المجلد الجذري `/firecrawl`:

> هذا الاصطلاح مطلوب حتى يتمكن `systemd` من تحديد الخدمة وبدء تشغيلها بشكل صحيح كما هو محدد في `WorkingDirectory=${HOME}/firecrawl`.

> يمكنك دائمًا توسيع المجموعة عن طريق إضافة خدمات Firecrawl إضافية حسب الحاجة. يمكن العثور على القائمة الكاملة للخدمات المتاحة في ملف [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) الرسمي.

### 4. تشغيل خدمة Hermes عبر Firecrawl 

قبل تسليم التحكم إلى `systemd`، تحقق من أن كل شيء يعمل بشكل صحيح عن طريق تشغيل المجموعة يدويًا:
```bash
podman compose -f hermes-compose.yaml up -d
```
إذا تم كل شيء بشكل صحيح، يجب أن ترى حاوية Hermes تعمل، ويجب أن يبدو ناتج سطر الأوامر لديك مشابهًا لهذا:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

بمجرد التحقق، أوقف تشغيل المجموعة قبل المتابعة:
```bash
podman compose -f hermes-compose.yaml down
```
الآن بعد أن تم التحقق من كل شيء، ابدأ تشغيل الخدمة عبر `systemd`:
```bash
systemctl --user start firecrawl.service
```
يمكن الوصول إلى [واجهة برمجة تطبيقات Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) من داخل الحاوية التفاعلية، وتتوفر لوحة المعلومات على نفس المضيف والمنفذ على http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

لإيقاف الخدمة، قم بتشغيل:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes الأصلي

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

**تهانينا، لقد قمت ببناء حزمة وكيل ذكاء اصطناعي محلية بالكامل.**

### لوحة المعلومات على الويب

يتضمن Hermes واجهة مستخدم قائمة على المتصفح لإدارة الإعدادات ومفاتيح واجهة برمجة التطبيقات والنماذج والجلسات والذاكرة ومهام cron. افتح طرفية ثانية أثناء تشغيل البوابة أو واجهة سطر الأوامر وقم بتشغيلها باستخدام:

```bash
hermes dashboard
```

هذا يبدأ خادمًا محليًا ويفتح `http://127.0.0.1:9119` في متصفحك. راجع [وثائق لوحة المعلومات](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) للحصول على المرجع الكامل للميزات.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## اختياري: ربط قناة تواصل

بمجرد تشغيل البوابة، يمكنك الوصول إلى وكيلك المحلي من أي جهاز. يدعم Hermes [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord)، و[Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)، وغيرها

---

### Discord

يتطلب Discord خادمًا **لديك فيه صلاحيات المسؤول** لإضافة بوت. إذا كنت تشارك خوادم لكن لا تملك واحدًا، استخدم Telegram بدلاً من ذلك.

#### إنشاء تطبيق وبوت Discord

1. انتقل إلى [بوابة مطوري Discord](https://discord.com/developers/applications) وانقر على **New Application**. أعطه اسمًا (مثل "hermes-bot").
2. في الشريط الجانبي، انقر على **Bot**. حدد اسم مستخدم للبوت.
3. لا تزال في صفحة Bot، مرر إلى **Privileged Gateway Intents** وفعّل:
   - **Message Content Intent** (مطلوب)
   - **Server Members Intent** (موصى به)
4. مرر للأعلى مرة أخرى وانقر على **Reset Token** لإنشاء رمز البوت الخاص بك. انسخه.

#### إضافة البوت إلى خادمك

1. في الشريط الجانبي، انقر على **OAuth2 / URL Generator**.
2. ضمن **Scopes**، فعّل `bot` و`applications.commands`.
3. ضمن **Bot Permissions**، فعّل: View Channels، Send Messages، Read Message History، Embed Links، Attach Files.
4. انسخ الرابط الذي تم إنشاؤه، الصقه في متصفحك، اختر خادمك، وأكّد.

#### جمع معرّفاتك والسماح بالرسائل المباشرة

فعّل وضع المطور في Discord (**User Settings / Advanced / Developer Mode**)، ثم:
- انقر بزر الفأرة الأيمن على أيقونة خادمك: **Copy Server ID**
- انقر بزر الفأرة الأيمن على صورتك الرمزية الخاصة: **Copy User ID**

انقر بزر الفأرة الأيمن على أيقونة خادمك / **Privacy Settings** / فعّل **Direct Messages**. هذا مطلوب لخطوة الاقتران.

#### تهيئة Hermes لـ Discord

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

يجب أن يصبح البوت متصلاً في Discord خلال ثوانٍ قليلة. أرسل له رسالة، إما كرسالة مباشرة أو في قناة يمكنه رؤيتها.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### إنشاء بوت Telegram

1. افتح Telegram وأرسل رسالة إلى **@BotFather**.
2. أرسل `/newbot` واتبع التعليمات. احفظ رمز البوت الذي يمنحك إياه.

#### تهيئة Hermes لـ Telegram

أضف ما يلي إلى `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **لا تعرف معرّف مستخدم Telegram الخاص بك؟** أرسل رسالة إلى [@userinfobot](https://t.me/userinfobot) في Telegram، وسيرد عليك بمعرّفك الرقمي.

ثم ابدأ تشغيل البوابة:

```bash
hermes gateway
```

أرسل أي رسالة إلى بوتك في Telegram للاختبار. يمكنك الآن الدردشة مع وكيلك عبر رسالة Telegram المباشرة. راجع [دليل إعداد Telegram الكامل](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) لوضع webhook والخيارات المتقدمة.

---

## الخطوات التالية

الآن بعد أن أصبح وكيلك قادرًا على تلقي الأوامر من هاتفك والتصرف على جهازك المحلي، إليك ثلاثة اتجاهات تستحق الاستكشاف:

1. **ملخص بحث آلي**: قم بجدولة Hermes للبحث في الويب عن المواضيع التي تهمك كل صباح، وتلخيص النتائج باستخدام نموذجك المحلي، وإرسال ملخص إلى هاتفك عبر Telegram أو Discord، كل ذلك يعمل على أجهزتك الخاصة دون أي تكاليف سحابية.

2. **مراجعة الكود عند الطلب**: وجّه Hermes إلى مستودع GitHub، واطلب منه مراجعة طلبات السحب المفتوحة، واجعله ينشر تعليقات أو ملخصًا في محادثتك. مع خلفية طرفية Docker، تعمل جميع عمليات git داخل بيئة العزل (sandbox)، مما يحافظ على نظافة جهازك المضيف.

3. **مساعد ملفات محلي**: امنح Hermes صلاحية الوصول إلى دليل عمل واطلب منه تنظيم أو إعادة تسمية أو تلخيص أو تحويل الملفات عند الطلب من هاتفك. نظرًا لأن خلفية طرفية Docker تحصر جميع عمليات الكتابة ضمن مساحة عمل العزل (sandbox)، يتم احتواء أي عمليات مدمرة عرضية.