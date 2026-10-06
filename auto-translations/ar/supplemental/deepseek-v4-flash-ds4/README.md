<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## نظرة عامة

يُعد [DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) الإصدار الذي يركّز على الكفاءة من عائلة DeepSeek V4 — وهو نموذج خليط خبراء (Mixture of Experts) بحجم 284 مليار معامل مع 13 مليار معامل نشط. وفقًا [للتقرير التقني الخاص بـ DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)، يحقق هذا النموذج 79% على SWE-bench Verified و91.6% على LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) هو محرك استدلال مخصص مبني خصيصًا لهذه البنية النموذجية. فبدلاً من أن يكون وقت تشغيل عام الغرض، يستهدف ds4 عائلة DeepSeek V4 مباشرةً عبر تحسينات نواة (kernel) خاصة بالبنية لبرنامج AMD ROCm™. وهو حاليًا أحد أفضل التطبيقات أداءً لنموذج DeepSeek V4 Flash على Strix Halo.

يوضح هذا البرنامج التعليمي كيفية استخدام `ai-toolbox-cockpit`، وهي واجهة مستخدم طرفية (terminal UI)، لإعداد ds4، وتنزيل أوزان النموذج، وبدء تقديم خدمة DeepSeek V4 Flash محليًا على منصة AMD Ryzen™ AI Halo Developer Platform.

## ما ستتعلمه

- كيفية تثبيت وتشغيل واجهة المستخدم الطرفية `ai-toolbox-cockpit`
- كيفية إنشاء حاوية ds4 ROCm toolbox
- تنزيل التكميم (quantization) الموصى به لعقدة Halo واحدة
- بدء تشغيل خادم استدلال ds4 وكشف نقطة نهاية متوافقة مع OpenAI
- ربط واجهة ويب أو وكيل برمجة (coding agent) بالخادم المحلي

## تعيين إعدادات الذاكرة

<!-- @require:memory-config -->

## تثبيت متطلبات البرامج الأساسية

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:distrobox,ds4-cockpit,ds4-toolbox-image -->

> **متطلبات النظام لهذا الإعداد (عقدة واحدة IQ2_XXS بسياق 126 ألف):**
> - نظام Strix Halo بذاكرة موحدة لا تقل عن **128 جيجابايت**.
> - **ضبط ذاكرة VRAM المخصصة في BIOS (مخزن الإطار UMA) على الحد الأدنى**، بحيث تكون مجموعة الذاكرة المشتركة بأكبر حجم ممكن.
> - ضبط **مجموعة ذاكرة GPU المشتركة على 110 جيجابايت على الأقل**: شغّل الأمر `amd-ttm --set 110` (راجع خطوة تعيين إعدادات الذاكرة أعلاه) ثم أعد التشغيل. قد تؤدي القيم الأقل إلى فشل بسبب نفاد الذاكرة عند تحميل النموذج بسياق 126 ألف. إذا كانت ذاكرة نظامك المتاحة أقل، فقم بخفض قيمة **السياق (Context)** في وضع الخادم بدلًا من ذلك.
>
> **ملاحظة:** جرّب ضبط **مجموعة ذاكرة GPU المشتركة** على **110 جيجابايت** كنقطة بداية. إذا واجهت أخطاء نفاد الذاكرة، فارفع مجموعة الذاكرة المشتركة أو قلّل حجم السياق.

يستخدم ai-toolbox-cockpit صناديق أدوات الحاويات (container toolboxes) لتشغيل محرك ds4. ثبّت `podman` و`distrobox` و`pipx`:

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

## التكميمات المتاحة

يوفر مؤلف ds4 عدة إصدارات مكمَّمة (quantized) من DeepSeek V4 Flash بصيغة GGUF. تستخدم جميع النماذج أدناه معايرة مصفوفة الأهمية (imatrix)، التي تحافظ على دقة أعلى للأجزاء الأكثر أهمية في النموذج لمهام البرمجة والاستدلال.

| التكميم | الحجم | الوصف |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 جيجابايت | موصى به لعقدة واحدة بسعة 128 جيجابايت |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 جيجابايت | يحافظ على الطبقات من 37 إلى 42 بدقة Q4 لتحسين الدقة. يتناسب مع 128 جيجابايت لكنه يترك مساحة أقل للسياق |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 جيجابايت | جودة أعلى. يتطلب عقدتي Halo عبر تجميع متعدد العقد (multi-node clustering) |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 جيجابايت | إضافة اختيارية لفك الترميز التخميني (speculative decoding) لتحسين سرعة التوليد |

يُعد نموذج **IQ2_XXS imatrix** نقطة انطلاق جيدة. فهو يتناسب بشكل مريح مع عقدة واحدة ويترك ذاكرة كافية لنافذة سياق معقولة.

## تثبيت ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) هي واجهة مستخدم طرفية خفيفة لتسهيل تثبيت مختلف أطر عمل الذكاء الاصطناعي الخلفية (backends). سنستخدمها للتعامل مع إنشاء حاوية ds4 الخاصة بنا، وتنزيل أوزان النموذج، وبدء تشغيل الخوادم. ثبّتها باستخدام `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

شغّل الـ cockpit:
```bash
ai-toolbox-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ai-toolbox-cockpit
echo "OK: ai-toolbox-cockpit is installed and on PATH"
```
<!-- @test:end -->

## الخطوة 1: إنشاء صندوق الأدوات (Toolbox)

في علامة التبويب **Interactive Toolboxes**، اختر أحدث صندوق أدوات متاح/مستقر لـ ds4 (مثل `ds4-rocm-10.0`) وانقر على **Create/Update**. يؤدي هذا إلى سحب صورة الحاوية وإنشاء بيئة صندوق الأدوات.


<p align="center">
  <img src="assets/ai-toolbox-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ai-toolbox-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## الخطوة 2: تنزيل النموذج

انتقل إلى علامة التبويب **Models**. أولًا، اختر الخلفية (backend) (ds4). ثم اختر **IQ2_XXS imatrix (~80.8 جيجابايت)** من القائمة المنسدلة وانقر على **Download**. سيتم حفظ ملفات النموذج في `~/ds4` بشكل افتراضي (يمكنك تغيير مسار التخزين).

> **ملاحظة:** حجم نموذج IQ2_XXS نحو 80 جيجابايت، لذا قد يستغرق التنزيل وقتًا حسب سرعة اتصالك. يمكنك المتابعة بمجرد انتهائه.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-models.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ai-toolbox-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ai-toolbox-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ai-toolbox-cockpit first."
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

## الخطوة 3: بدء تشغيل الخادم

انتقل إلى علامة التبويب **Server Mode**. اختر النموذج الذي تم تنزيله وصندوق الأدوات، ثم اضبط حجم السياق والمضيف (host) والمنفذ (port). عند الاستعداد، انقر على **Start ds4-server**.

> **تلميح** يُعد حجم سياق قدره `126000` قيمة ابتدائية معقولة ينبغي أن تتناسب مع عقدة واحدة — يمكنك رفعه إذا كانت لديك ذاكرة إضافية، أو خفضه إذا واجهت أخطاء نفاد الذاكرة. المنفذ (`8000` في هذا الدليل) اختياري؛ اختر أي منفذ متاح.

> **ذاكرة التخزين المؤقت KV على القرص (اختياري).** يؤدي تفعيل **KV Disk Cache** إلى نقل ذاكرة التخزين المؤقت KV إلى القرص (في **Host Cache Dir**، الافتراضي `~/.cache/ds4-kv`) بحيث تتم استعادة موجّهات النظام المتكررة من SSD بدلًا من إعادة حسابها. إنه تحسين أداء لسير عمل وكلاء البرمجة الذين يستخدمون موجّهات طويلة ومتكررة، وهو **غير مطلوب** لتشغيل الخادم.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

سيبدأ الخادم بالتشغيل والاستماع على المنفذ 8000، مُظهِرًا نقطة نهاية API متوافقة مع OpenAI على `http://localhost:8000/v1`.

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
  echo "No .gguf model found under $MODEL_DIR. Download it in ai-toolbox-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# keep-id maps the calling user into the container. Root does not need it, and as root it cannot
# be combined with --ipc=host (crun fails to mount /dev/mqueue), so root keeps the host user namespace.
userns=keep-id
if [ "$(id -u)" -eq 0 ]; then
  userns=host
fi

# Remove any stale instance, then start ds4-server detached (same flags ai-toolbox-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns="$userns" \
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
## توصيل واجهة ويب

يمكنك توصيل أي واجهة محادثة تدعم تنسيق OpenAI API. على سبيل المثال، لاستخدام HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

افتح `http://localhost:3000` في متصفحك لبدء المحادثة.

> **ملاحظة:** يضع `--network=host` واجهة الويب على شبكة المضيف بحيث يمكنها الوصول إلى خادم ds4 عبر `localhost` مباشرة. وهذا يبقي خادم ds4 مرتبطًا بـ loopback (لا داعي لعرضه على واجهات أخرى).

> **تلميح:** منفذ واجهة الويب (`3000` هنا، يُحدَّد عبر `PORT`) هو منفذ اعتباطي — اختر أي منفذ متاح إذا كان `3000` مستخدَمًا بالفعل، وافتح ذلك المنفذ في متصفحك بدلًا منه. تأكد من أن المنفذ الموجود في `OPENAI_BASE_URL` يطابق المنفذ الذي يعمل عليه خادم ds4.

## توصيل وكيل برمجي (Coding Agent)

يوفر خادم ds4 نقاط نهاية متوافقة مع كل من OpenAI وAnthropic، لذا يمكن لمعظم وكلاء البرمجة الاتصال به مباشرة. على سبيل المثال، لإضافته إلى وكيل البرمجة `pi`، أضف الكتلة التالية إلى `~/.pi/agent/models.json`:

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

> **تلميح**: إذا كان وكيل البرمجة أو واجهة الويب لديك يعمل على جهاز مختلف عن منصة Halo، فستحتاج إلى إعادة توجيه منفذ الخادم (`8000` هنا) عبر SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## الخطوات التالية

- **التجميع متعدد العُقد (Multi-node clustering)**: إذا كان لديك جهازا Halo، يدعم ds4 توزيع نموذج Q4 (~153 جيجابايت) عبر الجهازين باستخدام التوازي الأنبوبي (pipeline parallelism). راجع [وثائق ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) للحصول على تعليمات الإعداد.
- **فك التشفير التخميني (MTP)**: قم بتنزيل أوزان MTP (~3.6 جيجابايت) ومرّر `--mtp` إلى الخادم لتحقيق سرعة توليد أسرع.
- **نقل ذاكرة التخزين المؤقت KV إلى القرص**: لسير عمل وكلاء البرمجة، فعّل `--kv-disk-dir` بحيث تتم استعادة موجّهات النظام المتكررة من SSD بدلاً من إعادة حسابها في كل مرة.

لمزيد من المعلومات، راجع [مستودع ds4](https://github.com/antirez/ds4) و[مجموعة أدوات ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).