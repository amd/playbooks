<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> يستخدم هذا الدليل الإرشادي علامات خاصة لا يمكن لموقع GitHub عرضها. يُرجى زيارة [amd.com/playbooks](https://amd.com/playbooks) لمعاينة هذا المحتوى بشكل صحيح.
<!-- @github-only:end -->

## نظرة عامة

يُعد [DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) النسخة المركّزة على الكفاءة من عائلة DeepSeek V4 — وهو نموذج خليط خبراء (Mixture of Experts) بحجم 284 مليار معلمة، منها 13 مليار معلمة نشطة. وفقًا [للتقرير الفني الخاص بـ DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)، يحقق هذا النموذج نسبة 79% في اختبار SWE-bench Verified و91.6% في اختبار LiveCodeBench.

يُعد [ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) محرك استدلال مخصص مُصمم خصيصًا لهذه البنية النموذجية. فبدلًا من كونه وقت تشغيل عام الغرض، يستهدف ds4 عائلة DeepSeek V4 مباشرة من خلال تحسينات نواة خاصة بالبنية لبرنامج AMD ROCm™. وهو حاليًا أحد أفضل عمليات التنفيذ أداءً لنموذج DeepSeek V4 Flash على منصة Strix Halo.

يوضح هذا البرنامج التعليمي كيفية استخدام `ds4-cockpit`، وهي واجهة مستخدم طرفية، لإعداد ds4، وتنزيل أوزان النموذج، وبدء تشغيل DeepSeek V4 Flash محليًا على منصة AMD Ryzen™ AI Halo Developer Platform.

## ما ستتعلمه

- كيفية تثبيت وتشغيل واجهة المستخدم الطرفية `ds4-cockpit`
- كيفية إنشاء حاوية أدوات ds4 ROCm
- تنزيل مستوى التكميم الموصى به لعقدة Halo واحدة
- بدء تشغيل خادم استدلال ds4 وكشف نقطة نهاية متوافقة مع OpenAI
- ربط واجهة ويب أو وكيل برمجي بالخادم المحلي

<!-- @setup:memory_config -->

## تثبيت متطلبات البرمجيات الأساسية

> **متطلبات النظام لهذا التكوين (عقدة واحدة IQ2_XXS بسياق 126 ألف):**
> - نظام Strix Halo مزوّد بـ **ذاكرة موحدة لا تقل عن 128 جيجابايت**.
> - **يجب ضبط ذاكرة VRAM المخصصة في BIOS (إطار UMA) على الحد الأدنى**، بحيث يكون مجمّع الذاكرة المشتركة بأكبر حجم ممكن.
> - **يجب ضبط مجمّع الذاكرة المشتركة الخاص بوحدة معالجة الرسومات (GPU) على 110 جيجابايت على الأقل**: نفّذ الأمر `amd-ttm --set 110` (راجع خطوة تهيئة الذاكرة أعلاه) ثم أعد تشغيل النظام. القيم الأقل من ذلك تؤدي إلى فشل بسبب نفاد الذاكرة عند تحميل النموذج بسياق 126 ألف. إذا كان نظامك يحتوي على ذاكرة أقل متاحة، فقلّل قيمة **Context** في وضع الخادم بدلًا من ذلك.

يستخدم ds4-cockpit صناديق أدوات الحاويات (container toolboxes) لتشغيل محرك ds4. قم بتثبيت `podman` و`distrobox` و`pipx`:

```bash
sudo apt update
sudo apt install -y podman distrobox pipx
```

<!-- @test:id=ds4-prereqs-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
podman --version
distrobox version 2>/dev/null || distrobox --version
pipx --version
echo "OK: podman, distrobox, and pipx are installed"
```
<!-- @test:end -->

## مستويات التكميم المتاحة

يوفر مؤلف ds4 عدة نسخ مكممة من DeepSeek V4 Flash بتنسيق GGUF. تستخدم جميع النماذج أدناه معايرة مصفوفة الأهمية (imatrix)، التي تحافظ على دقة أعلى في أجزاء النموذج الأكثر أهمية لمهام البرمجة والاستدلال.

| مستوى التكميم | الحجم | الوصف |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 جيجابايت | موصى به لعقدة واحدة بسعة 128 جيجابايت |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 جيجابايت | يحافظ على الطبقات من 37 إلى 42 بدقة Q4 لتحسين الدقة. يتناسب مع 128 جيجابايت لكنه يترك مساحة أقل للسياق |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 جيجابايت | جودة أعلى. يتطلب عقدتي Halo عبر التجميع متعدد العقد |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 جيجابايت | إضافة اختيارية لفك التشفير التخميني لتحسين سرعة التوليد |

يُعد نموذج **IQ2_XXS imatrix** نقطة انطلاق جيدة. فهو يتناسب بسهولة مع عقدة واحدة ويترك مساحة كافية من الذاكرة لنافذة سياق معقولة.

## تثبيت ds4-cockpit

يُعد [ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) واجهة مستخدم طرفية خفيفة لتسهيل إعداد ds4 وتشغيله على Strix Halo. فهو يتولى إنشاء حاويات صناديق الأدوات، وتنزيل أوزان النموذج، وبدء تشغيل الخوادم. قم بتثبيته باستخدام `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

شغّل الـ cockpit:
```bash
ds4-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ds4-cockpit
echo "OK: ds4-cockpit is installed and on PATH"
```
<!-- @test:end -->

## إنشاء صندوق الأدوات

في علامة التبويب **Interactive Toolboxes**، اختر أحدث صندوق أدوات متاح (مثل `ds4-rocm-7.2.4`) وانقر على **Create/Update**. سيؤدي ذلك إلى سحب صورة الحاوية وإنشاء بيئة صندوق الأدوات.

> **تلميح**: ستتغير نسخة صندوق الأدوات بمرور الوقت مع صدور إصدارات ROCm أحدث. اختر أحدث إصدار متاح في القائمة.

<p align="center">
  <img src="assets/ds4-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ds4-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## تنزيل النموذج

انتقل إلى علامة التبويب **Model Manager**. اختر **IQ2_XXS imatrix (~80.8 GB)** من القائمة المنسدلة وانقر على **Download**. سيتم حفظ ملفات النموذج في `~/ds4` افتراضيًا (يمكنك تغيير مسار التخزين).

<p align="center">
  <img src="assets/ds4-cockpit-model-manager.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ds4-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ds4-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ds4-cockpit first."
  exit 1
fi

# Prefer to confirm the recommended IQ2_XXS imatrix quantization is present.
if find "$model_dir" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' | grep -q .; then
  echo "OK: IQ2_XXS imatrix model is downloaded"
else
  echo "OK: a GGUF model is present (recommended IQ2_XXS imatrix file not detected by name)"
fi
```
<!-- @test:end -->

## بدء تشغيل الخادم

انتقل إلى علامة التبويب **Server Mode**. اختر النموذج المُنزَّل وصندوق الأدوات، ثم قم بتهيئة حجم السياق (على سبيل المثال، 126000)، والمضيف، والمنفذ (8000). عند الاستعداد، انقر على **Start ds4-server**.

> **ذاكرة تخزين KV المؤقتة على القرص (اختياري).** يؤدي تفعيل **KV Disk Cache** إلى نقل ذاكرة التخزين المؤقت KV إلى القرص (عند **Host Cache Dir**، والافتراضي هو `~/.cache/ds4-kv`) بحيث يتم استعادة توجيهات النظام المتكررة من القرص الصلب بدلًا من إعادة حسابها. هذا تحسين للأداء مخصص لسير عمل الوكلاء البرمجيين ذوي التوجيهات الطويلة والمتكررة، وهو **غير مطلوب** لتشغيل الخادم.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

سيبدأ الخادم بالعمل والاستماع على المنفذ 8000، مع كشف نقطة نهاية واجهة برمجة تطبيقات متوافقة مع OpenAI على العنوان `http://localhost:8000/v1`.

**اختبار سريع:**
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

<!-- @test:id=ds4-server-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

# This runner is shared with other playbooks, and ds4 at a 126k context consumes almost the entire GPU memory pool.
# So rather than keeping ds4 resident, CI starts the server, verifies a chat completion, then stops it again.
# This frees the memory for the next job.
# ds4 has no separate "unload"; stopping the server process is what releases the ~80 GB model.

CONTAINER="ds4-ci-server"
MODEL_DIR="$HOME/ds4"

# Locate the downloaded model (prefer the recommended IQ2_XXS imatrix file).
model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' 2>/dev/null | head -1)"
if [ -z "$model_file" ]; then
  model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*.gguf' 2>/dev/null | head -1)"
fi
if [ -z "$model_file" ]; then
  echo "No .gguf model found under $MODEL_DIR. Download it in ds4-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Remove any stale instance, then start ds4-server detached (same flags ds4-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns=keep-id \
  -p 127.0.0.1:8000:8000 \
  -v "$MODEL_DIR":/models:ro \
  "$image" \
  ds4-server -m "/models/$model_name" --ctx 126000 --host 0.0.0.0 --port 8000

# Wait for readiness; the ~80 GB model can take a few minutes to load.
up=false
for i in $(seq 1 240); do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8000/v1/models || true)"
  if [ -n "$code" ] && [ "$code" != "000" ]; then
    up=true
    break
  fi
  if ! podman inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null | grep -q true; then
    echo "ds4-server container exited during startup:"
    podman logs "$CONTAINER" 2>&1 | tail -40 || true
    exit 1
  fi
  sleep 2
done

if [ "$up" != "true" ]; then
  echo "ds4 server did not become ready on http://127.0.0.1:8000"
  podman logs "$CONTAINER" 2>&1 | tail -40 || true
  exit 1
fi
echo "OK: ds4 server is responding on :8000"

body='{
  "model": "deepseek-v4-flash",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32,
  "stream": false
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from ds4 /v1/chat/completions"
  exit 1
fi

export DS4_OUT="$out"
python3 - <<'PY'
import json, os, sys

data = json.loads(os.environ["DS4_OUT"])
choices = data.get("choices")
if not choices:
    print("Response has no 'choices':")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

message = choices[0].get("message", {}) or {}
content = message.get("content") or message.get("reasoning_content")
if not content:
    print("Response choice has empty content:")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

print("OK: ds4 chat/completions returned content")
PY

echo "OK: ds4 server test complete; server stopped and GPU memory released"
```
<!-- @test:end -->

## ربط واجهة ويب

يمكنك ربط أي واجهة محادثة تدعم تنسيق واجهة برمجة تطبيقات OpenAI. على سبيل المثال، لاستخدام HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

افتح `http://localhost:3000` في متصفحك لبدء المحادثة.

## ربط وكيل برمجي

يكشف خادم ds4 نقاط نهاية متوافقة مع كل من OpenAI وAnthropic، لذا يمكن لمعظم وكلاء البرمجة الاتصال به مباشرة. على سبيل المثال، لإضافته إلى وكيل البرمجة `pi`، أضف الكتلة التالية إلى `~/.pi/agent/models.json`:

```json
"ds4": {
  "name": "ds4.c local",
  "baseUrl": "http://localhost:8000/v1",
  "api": "openai-completions",
  "apiKey": "dsv4-local",
  "compat": {
    "supportsStore": false,
    "supportsDeveloperRole": false,
    "supportsReasoningEffort": true,
    "supportsUsageInStreaming": true,
    "maxTokensField": "max_tokens",
    "supportsStrictMode": false,
    "thinkingFormat": "deepseek",
    "requiresReasoningContentOnAssistantMessages": true
  },
  "models": [
    {
      "id": "deepseek-v4-flash",
      "name": "DeepSeek V4 Flash (ds4.c local)",
      "reasoning": true,
      "thinkingLevelMap": {
        "off": null,
        "minimal": "low",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "input": ["text"],
      "contextWindow": 131072,
      "maxTokens": 65536,
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
    }
  ]
}
```

> **تلميح**: إذا كان وكيل البرمجة أو واجهة الويب لديك يعمل على جهاز مختلف عن منصة Halo، فستحتاج إلى توجيه المنفذ 8000 عبر SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```
## الخطوات التالية

- **التجميع متعدد العقد (Multi-node clustering)**: إذا كان لديك جهازا Halo، فإن ds4 يدعم توزيع نموذج Q4 (~153 جيجابايت) عبر كلا الجهازين باستخدام التوازي الأنبوبي (pipeline parallelism). راجع [وثائق ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) للحصول على تعليمات الإعداد.
- **فك الترميز التخميني (Speculative decoding) (MTP)**: قم بتنزيل أوزان MTP (~3.6 جيجابايت) ومرر `--mtp` إلى الخادم للحصول على سرعة توليد أسرع.
- **تفريغ ذاكرة التخزين المؤقت KV على القرص**: لسير عمل وكلاء البرمجة، قم بتفعيل `--kv-disk-dir` بحيث تتم استعادة موجهات النظام المتكررة من SSD بدلاً من إعادة حسابها في كل مرة.

لمزيد من المعلومات، راجع [مستودع ds4](https://github.com/antirez/ds4) و[أدوات ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).