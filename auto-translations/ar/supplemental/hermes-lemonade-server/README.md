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

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) هو وكيل ذكاء اصطناعي ذاتي التحسين من بناء Nous Research. يتميز بحلقة تعلّم مدمجة، حيث يبني مهارات من الخبرة، ويكوّن ذاكرة دائمة عنك عبر الجلسات، ويمكنه تشغيل أتمتة مجدولة نيابةً عنك. وعلى خلاف مساعد المحادثة البسيط، ينفّذ Hermes إجراءات فعلية: تشغيل أوامر الصدفة، وكتابة الملفات، وتصفح الويب، وتفويض مهام متوازية إلى وكلاء فرعيين.

[**Lemonade Server**](https://lemonade-server.ai/) هو خلفية الاستدلال المحلية التي تشغّله. وهو خادم مفتوح المصدر يشغّل نماذج الذكاء الاصطناعي التوليدي مباشرةً على عتاد AMD لديك، ويعرضها عبر واجهة OpenAI API القياسية في الصناعة.

معًا، يشكّلان حزمة وكيل ذكاء اصطناعي محلية بالكامل: يتولى Lemonade استدلال النماذج على وحدة معالجة الرسومات (GPU) لديك، بينما يوفّر Hermes حلقة الوكيل والذاكرة والمهارات وبوابة المراسلة.

> **قبل أن تواصل:** Hermes Agent هو وكيل ذكاء اصطناعي ذو استقلالية عالية. قد يؤدي منح أي وكيل ذكاء اصطناعي صلاحية الوصول إلى نظامك إلى نتائج غير متوقعة أو غير مقصودة. تابع فقط إذا كنت تفهم المخاطر ومرتاحًا لفكرة أن يتصرف برنامج مستقل نيابةً عنك.

---

## ماذا ستتعلم

بحلول نهاية هذا الدليل، ستكون قادرًا على:

- **تثبيت Hermes Agent** وتوجيهه نحو **Lemonade Server** كخلفية للذكاء الاصطناعي.
- **(موصى به) تفعيل عزل Docker/Podman** لعزل إجراءات الوكيل عن جهازك المضيف.
- **بدء تشغيل بوابة Hermes** والتأكد من جاهزية وكيلك.
- **ربط قناة اتصال** (Discord أو Telegram) حتى تتمكن من الدردشة مع وكيلك من أي جهاز.

---

<!-- @device:halo_box,halo,stx,krk -->
## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرامج الأساسية

<!-- @os:linux -->
- جهاز كمبيوتر يعمل بنظام **Ubuntu 24.04+** أو توزيعة Linux متوافقة قائمة على Debian مع `apt-get`
- على الأقل **12 جيجابايت من الذاكرة العشوائية (RAM)** (يُوصى بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- **~10–30 جيجابايت من مساحة القرص الحرة** لأوزان النموذج
- [Podman](https://podman.io/docs/installation) (اختياري، لعزل Hermes Agent)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- جهاز كمبيوتر يعمل بنظام **Windows 10/11**
- على الأقل **12 جيجابايت من الذاكرة العشوائية (RAM)** (يُوصى بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
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
<!-- @prereq:hermes,lemonade-models-qwen3-35b-a3b,lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## سحب وتحميل النموذج الموصى به

النموذج الموصى به لهذا الدليل هو **Qwen3.6-35B-A3B-GGUF** من Unsloth، وهو نموذج MoE قوي بنافذة سياق تصل إلى 263 ألف رمز، وهو مناسب جدًا لأعباء عمل الوكلاء. يستخدم هذا النموذج التكميم UD-Q4_K_XL. اسحبه الآن:

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

> **نصيحة: عطّل وضع التفكير للحصول على استجابات أسرع للوكيل:** يعمل Qwen3.6-35B-A3B في وضع التفكير افتراضيًا، مما يضيف زمن انتقال قبل كل استجابة. وفي حلقات الوكيل، يتراكم هذا العبء بسرعة. يوفر مستودع [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) تهيئة جاهزة تعطّل وضع التفكير. لاستخدامها، نزّل الملف واستورده:
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

نشغّل Hermes Agent داخل WSL ونربطه بـ Lemonade الذي يعمل بشكل أصلي على Windows. يمنحك هذا بيئة shell خاصة بـ Linux لـ Hermes مع الإبقاء على تسريع الرسومات (GPU) الخاص بـ Lemonade على جانب Windows.

### تثبيت WSL وUbuntu

افتح PowerShell كمسؤول (Administrator) وثبّت نواة WSL:

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

تعمل WSL2 ضمن شبكة افتراضية. يرتبط Lemonade على Windows بالعنوان `127.0.0.1`، والذي لا تستطيع WSL الوصول إليه مباشرةً. يقوم بروكسي منفذ Windows بإعادة توجيه حركة المرور من عنوان IP الخاص ببوابة WSL إلى المضيف المحلي (localhost) في Windows.

**ابحث عن عنوان IP الخاص ببوابة WSL** (شغّل داخل WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**أضف بروكسي المنفذ** (شغّله في PowerShell كمسؤول، مع استبدال `<WSL-Gateway-IP>` بعنوان IP الخاص ببوابة WSL لديك):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**أضف قاعدة جدار حماية** (في نفس نافذة PowerShell المرتفعة الصلاحيات):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**تحقق من داخل WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

إذا كنت قد حمّلت بالفعل نموذج Qwen3.6-35B-A3B-GGUF في الخطوة السابقة، فيجب أن ترى إخراج JSON يسرد النموذج الذي قمت بتحميله.

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

> تبقى قاعدة `netsh portproxy` فعّالة بعد إعادة التشغيل، لكن عنوان IP الخاص ببوابة WSL قد يتغيّر بعد تنفيذ `wsl --shutdown`. إذا أصبح Lemonade غير قابل للوصول من WSL بعد إعادة التشغيل، فاحصل على عنوان IP الجديد للبوابة وحدّث البروكسي بهذا العنوان الجديد.

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
> نفّذ الأوامر الواردة في هذا القسم داخل **طرفية WSL** ما لم يُذكر خلاف ذلك.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

تتخطى العلامة `--skip-setup` معالج الإعداد التفاعلي حتى تتمكن من تهيئة خلفية النموذج يدويًا في الخطوة التالية.

أعد تحميل الصدفة (shell):

```bash
source ~/.bashrc
```

تأكّد من التثبيت:

```bash
hermes --version
```

شغّل تشخيصًا ذاتيًا للتحقق من جميع الاعتماديات:

```bash
hermes doctor
```

> **نصيحة:** إذا ظهرت لديك رسالة `command not found` بعد التثبيت، أضف Hermes إلى متغير PATH لديك:
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

يخزّن Hermes إعدادات النموذج الخاصة به في `~/.hermes/config.yaml`. يمكنك إما استخدام أداة اختيار `hermes model` التفاعلية أو كتابة الإعداد مباشرةً.

### الخيار 1: أداة الاختيار التفاعلية

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

عند الطلب:

1. اختر **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **عنوان URL الأساسي لواجهة API:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **عنوان URL الأساسي لواجهة API:** استخدم عنوان IP الخاص ببوابة WSL: نفّذ `ip route show default | awk '{print $3}' | head -1` داخل WSL للحصول عليه، ثم أدخل `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **مفتاح API:** `lemonade`
4. **وضع توافق API:** `1` (الكشف التلقائي)
5. **اختر النموذج:** اختر `Qwen3.6-35B-A3B-GGUF` من القائمة
6. **طول السياق بالرموز:** `262144`
7. **الاسم المعروض:** `local-lemonade` (أو أي اسم تفضله)

يحفظ `hermes model` كلًا من اختيار النموذج النشط وإدخال `custom_providers` المُسمّى الذي يخزّن طول السياق جنبًا إلى جنب مع نقطة النهاية. تظهر النتيجة في `~/.hermes/config.yaml` على النحو التالي:

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

### الخيار 2: كتابة الإعداد مباشرةً

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

داخل طرفية WSL الخاصة بك، احصل على عنوان IP لمضيف Windows واكتب الإعداد:

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

## (موصى به) تمكين عزل Podman الآمن (Sandboxing)

يمكن لـ Hermes Agent توجيه جميع عمليات الصدفة والملفات الخاصة بالوكيل عبر حاوية معزولة بدلاً من تشغيلها مباشرةً على جهازك المضيف. هذا يحدّ من نطاق تأثير أي إجراء غير مقصود ليقتصر على البيئة المعزولة، تاركًا نظام الملفات والشبكة الخاصين بجهازك المضيف دون تأثير.

ابنِ صورة بيئة معزولة خفيفة الوزن:

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

بعد ذلك، ابنِ صورة بيئة معزولة خفيفة الوزن:

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

بعد ذلك، قم بتهيئة Hermes لاستخدام Podman كبيئة تشغيل الحاويات، وحدد خلفية الطرفية:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> لا تزال `terminal.backend` قيمتها `docker`.
> `HERMES_DOCKER_BINARY` هو ما يخبر Hermes باستخدام Podman كبيئة التشغيل بدلاً من ذلك.

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

سيقوم Hermes الآن بتشغيل حاوية بيئة معزولة دائمة وتوجيه جميع استدعاءات `terminal` وأدوات الملفات من خلالها. تشارك الحاوية دورة حياة عملية Hermes، ويُعاد استخدامها عبر جميع استدعاءات الأدوات، ويتم إتلافها عند إنهاء Hermes.

> **تحقق من عمل بيئة العزل:** شغّل Hermes (`hermes`) واطلب منه `run hostname` - يجب أن ترى معرّف حاوية قصيرًا بدلاً من اسم مضيف جهازك. يمكنك أيضًا أن تطلب منه `rm -rf <path-to-a-dummy-file/folder>`: سيؤكد Hermes عملية الحذف، لكن المجلد سيبقى موجودًا على جهازك المضيف. تم تنفيذ الأمر داخل `$HOME` المعزول الخاص بالحاوية، وليس داخل جهازك.

> **بحاجة إلى عزل أقوى؟** يوفر Hermes أيضًا صورة Docker رسمية (`nousresearch/hermes-agent`) تُشغّل عملية الوكيل بأكملها داخل حاوية - البوابة والأدوات وكل شيء. راجع [وثائق Hermes Docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker) للاطلاع على تفاصيل الإعداد.

---

<!-- @os:linux -->
## (موصى به) تكامل Hermes مع خدمات Firecrawl

يمكن لـ Hermes تصفّح واستخراج المحتوى من المواقع الإلكترونية باستخدام أدواته المدمجة الخاصة بالويب. ومع ذلك، تستخدم العديد من المواقع الحديثة أنظمة كشف الروبوتات، التي تحظر طلبات HTTP البسيطة وتعيد صفحات تحدٍّ بدلاً من المحتوى الفعلي. نتيجة لذلك، قد لا يتمكن Hermes من استخراج المعلومات من هذه المواقع بشكل موثوق.

للتغلب على هذا القيد، توفر [Firecrawl](https://docs.firecrawl.dev/introduction) خدمة استضافة ذاتية لزحف الويب واستخراج المحتوى يمكنها تجاوز هذه التحديات وإطلاق الإمكانات الكاملة لأتمتة Hermes.

في هذا الإعداد، يعمل Firecrawl كمجموعة من حاويات Docker المُدارة باستخدام Podman. ولتبسيط إدارة دورة الحياة والتشغيل التلقائي، نسجّل Firecrawl كخدمة `systemd` على مستوى المستخدم تنسّق حزمة Podman Compose الأساسية. يتيح هذا لـ Hermes بدء وإيقاف والتحقق من خدمة Firecrawl باستخدام أوامر `systemctl --user` القياسية بدلاً من التفاعل مع الحاويات مباشرةً.

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

يحتوي `default.target.wants/` على روابط رمزية للخدمات المُهيّأة للبدء تلقائيًا.

### 2. تهيئة Firecrawl لخدمتك

يُعد [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) مثاليًا لمن يحتاجون إلى التحكم الكامل في بيئات الزحف ومعالجة البيانات الخاصة بهم، لكنه يأتي مع عبء إضافي من الصيانة وجهود الإعداد.

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
> عيّن `BULL_AUTH_KEY` إلى قيمة سرية قوية، خاصة في أي نشر يمكن الوصول إليه من شبكات غير موثوقة.
### 3. نشر Hermes عبر Compose

قبل المتابعة، تأكد من أنك قد سحبت أحدث صورة Docker لـ Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
بعد الانتهاء من ذلك، قم بتنزيل ملف Hermes Compose [hermes-compose.yaml](assets/hermes-compose.yaml) وضعه في الدليل الجذري `/firecrawl`:

> هذا الاتفاق مطلوب حتى يتمكن `systemd` من تحديد الخدمة وتشغيلها بشكل صحيح كما هو محدد في `WorkingDirectory=${HOME}/firecrawl`.

> يمكنك دائمًا توسيع المجموعة بإضافة خدمات Firecrawl إضافية حسب الحاجة. يمكن العثور على القائمة الكاملة للخدمات المتاحة في ملف [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) الرسمي.

### 4. تشغيل خدمة Hermes عبر Firecrawl 

قبل تسليم التحكم إلى `systemd`، تحقق من أن كل شيء يعمل بشكل صحيح عن طريق تشغيل المجموعة يدويًا:
```bash
podman compose -f hermes-compose.yaml up -d
```
إذا تم تكوين كل شيء بشكل صحيح، يجب أن ترى حاوية Hermes تعمل، ويجب أن يبدو إخراج سطر الأوامر لديك مشابهًا لهذا:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

بعد التحقق، أوقف المجموعة قبل المتابعة:
```bash
podman compose -f hermes-compose.yaml down
```
بعد التحقق من كل شيء، ابدأ الخدمة من خلال `systemd`:
```bash
systemctl --user start firecrawl.service
```
[واجهة Hermes البرمجية API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) متاحة من داخل الحاوية التفاعلية، ولوحة التحكم عبر الويب متاحة على نفس المضيف والمنفذ على http://127.0.0.1:9119.
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

ابدأ جلسة CLI تفاعلية مباشرة: 

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

**تهانينا، لقد قمت ببناء مجموعة وكيل ذكاء اصطناعي محلية بالكامل.**

### لوحة التحكم عبر الويب

يتضمن Hermes واجهة مستخدم تعمل عبر المتصفح لإدارة الإعدادات ومفاتيح API والنماذج والجلسات والذاكرة ومهام cron. افتح نافذة طرفية ثانية أثناء تشغيل البوابة أو CLI وقم بتشغيلها باستخدام:

```bash
hermes dashboard
```

يؤدي هذا إلى تشغيل خادم محلي وفتح `http://127.0.0.1:9119` في متصفحك. راجع [وثائق لوحة التحكم](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) للحصول على المرجع الكامل للميزات.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## اختياري: ربط قناة اتصال

بمجرد تشغيل البوابة، يمكنك الوصول إلى وكيلك المحلي من أي جهاز. يدعم Hermes [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord) و[Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) وغيرها

---

### Discord

يتطلب Discord خادمًا تملك فيه **صلاحيات المسؤول** لإضافة بوت. إذا كنت تشارك خوادم ولكنك لا تملك واحدًا، استخدم Telegram بدلاً من ذلك.

#### إنشاء تطبيق وبوت Discord

1. انتقل إلى [بوابة مطوري Discord](https://discord.com/developers/applications) وانقر على **New Application**. أعطه اسمًا (مثل "hermes-bot").
2. في الشريط الجانبي، انقر على **Bot**. اضبط اسم مستخدم للبوت.
3. لا تزال في صفحة Bot، انتقل إلى **Privileged Gateway Intents** وفعّل:
   - **Message Content Intent** (مطلوب)
   - **Server Members Intent** (موصى به)
4. عد إلى الأعلى وانقر على **Reset Token** لإنشاء رمز البوت الخاص بك. انسخه.

#### إضافة البوت إلى خادمك

1. في الشريط الجانبي، انقر على **OAuth2 / URL Generator**.
2. ضمن **Scopes**، فعّل `bot` و`applications.commands`.
3. ضمن **Bot Permissions**، فعّل: View Channels وSend Messages وRead Message History وEmbed Links وAttach Files.
4. انسخ الرابط الذي تم إنشاؤه، الصقه في متصفحك، اختر خادمك، وأكد العملية.

#### جمع المعرّفات الخاصة بك والسماح بالرسائل المباشرة

فعّل وضع المطور في Discord (**User Settings / Advanced / Developer Mode**)، ثم:
- انقر بزر الفأرة الأيمن على أيقونة خادمك: **Copy Server ID**
- انقر بزر الفأرة الأيمن على صورتك الرمزية: **Copy User ID**

انقر بزر الفأرة الأيمن على أيقونة خادمك / **Privacy Settings** / فعّل خيار **Direct Messages**. هذا مطلوب لخطوة الإقران.

#### تكوين Hermes لـ Discord

أضف ما يلي إلى `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

ثم ابدأ البوابة:

```bash
hermes gateway
```

يجب أن يصبح البوت متصلاً في Discord خلال بضع ثوانٍ. أرسل له رسالة، سواء كانت رسالة مباشرة أو في قناة يمكنه رؤيتها.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### إنشاء بوت Telegram

1. افتح Telegram وأرسل رسالة إلى **@BotFather**.
2. أرسل `/newbot` واتبع التعليمات. احفظ رمز البوت الذي يُعطيك إياه.

#### تكوين Hermes لـ Telegram

أضف ما يلي إلى `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **لا تعرف معرّف مستخدم Telegram الخاص بك؟** أرسل رسالة إلى [@userinfobot](https://t.me/userinfobot) في Telegram، وسيرد عليك برقم معرّفك.

ثم ابدأ البوابة:

```bash
hermes gateway
```

أرسل أي رسالة إلى بوتك في Telegram للاختبار. يمكنك الآن الدردشة مع وكيلك عبر رسائل Telegram المباشرة. راجع [دليل إعداد Telegram الكامل](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) لوضع webhook والخيارات المتقدمة.

---

## الخطوات التالية

الآن بعد أن أصبح بإمكان وكيلك تلقي الأوامر من هاتفك والتصرف على جهازك المحلي، إليك ثلاثة اتجاهات تستحق الاستكشاف:

1. **ملخص بحث آلي**: جدول Hermes للبحث على الويب عن المواضيع التي تهمك كل صباح، وتلخيص النتائج باستخدام نموذجك المحلي، ودفع ملخص إلى هاتفك عبر Telegram أو Discord، كل ذلك يعمل على جهازك الخاص دون أي تكاليف سحابية.

2. **مراجعة الكود عند الطلب**: وجّه Hermes إلى مستودع GitHub، واطلب منه مراجعة طلبات السحب المفتوحة، واجعله ينشر تعليقات أو ملخصًا في محادثتك. مع خلفية الطرفية الخاصة بـ Docker، تعمل جميع عمليات git داخل البيئة المعزولة، مما يحافظ على نظافة جهازك المضيف.

3. **مساعد ملفات محلي**: امنح Hermes صلاحية الوصول إلى دليل عمل واطلب منه تنظيم الملفات أو إعادة تسميتها أو تلخيصها أو تحويلها عند الطلب من هاتفك. ولأن خلفية الطرفية الخاصة بـ Docker تحصر جميع عمليات الكتابة داخل مساحة العمل المعزولة، فإن أي عمليات مدمرة عرضية تظل محصورة.