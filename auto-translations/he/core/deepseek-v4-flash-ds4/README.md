<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> מדריך זה משתמש בתגיות מיוחדות ש-GitHub אינו יכול לעבד. יש לבקר בכתובת [amd.com/playbooks](https://amd.com/playbooks) כדי לצפות בתוכן זה כראוי.
<!-- @github-only:end -->

## סקירה כללית

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) הוא הגרסה המתמקדת ביעילות ממשפחת DeepSeek V4 — מודל Mixture of Experts בעל 284 מיליארד פרמטרים עם 13 מיליארד פרמטרים פעילים. לפי [הדוח הטכני של DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), הוא משיג ציון של 79% ב-SWE-bench Verified ו-91.6% ב-LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) הוא מנוע היסק ייעודי שנבנה במיוחד עבור ארכיטקטורת מודל זו. במקום ריצה כללית, ds4 מכוון ישירות למשפחת DeepSeek V4 עם אופטימיזציות ליבה (kernel) ספציפיות לארכיטקטורה עבור תוכנת AMD ROCm™. הוא כיום אחד ממימושי DeepSeek V4 Flash בעלי הביצועים הטובים ביותר על Strix Halo.

מדריך זה מראה כיצד להשתמש ב-`ds4-cockpit`, ממשק משתמש טקסטואלי (terminal UI), כדי להגדיר את ds4, להוריד את משקלי המודל, ולהתחיל להגיש את DeepSeek V4 Flash מקומית על פלטפורמת הפיתוח AMD Ryzen™ AI Halo.

## מה תלמדו

- כיצד להתקין ולהפעיל את ממשק המשתמש הטקסטואלי `ds4-cockpit`
- כיצד ליצור את מכולת (container) ה-toolbox של ds4 עבור ROCm
- הורדת רמת הכימות המומלצת עבור צומת Halo יחיד
- הפעלת שרת ההיסק של ds4 וחשיפת נקודת קצה תואמת OpenAI
- חיבור ממשק Web UI או סוכן קידוד לשרת המקומי

<!-- @setup:memory_config -->

## התקנת דרישות תוכנה מקדימות

> **דרישות מערכת עבור תצורה זו (IQ2_XXS בצומת יחיד עם הקשר של 126k):**
> - מערכת Strix Halo עם **לפחות 128 GB של זיכרון מאוחד**.
> - **VRAM ייעודי ב-BIOS (מאגר מסגרות UMA) מוגדר למינימום**, כך שמאגר הזיכרון המשותף יוכל להיות גדול ככל האפשר.
> - מאגר הזיכרון המשותף של ה-GPU **מוגדר לכל הפחות ל-110 GB**: הריצו `amd-ttm --set 110` (ראו שלב הגדרת הזיכרון לעיל) ואתחלו מחדש. ערכים נמוכים יותר יגרמו לכשל בזיכרון (out-of-memory) בעת טעינת המודל בהקשר של 126k. אם למערכת שלכם יש פחות זיכרון זמין, הפחיתו במקום זאת את ערך ה-**Context** במצב Server Mode.

ds4-cockpit משתמש במכולות toolbox כדי להריץ את מנוע ds4. יש להתקין את `podman`, `distrobox`, ו-`pipx`:

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

## רמות כימות זמינות

מחבר ds4 מספק מספר גרסאות מכומתות (quantized) של DeepSeek V4 Flash בפורמט GGUF. כל המודלים להלן משתמשים בכיול matrix חשיבות (imatrix), אשר שומר על דיוק גבוה יותר עבור החלקים במודל שהם החשובים ביותר למשימות קידוד והיגיון.

| כימות | גודל | תיאור |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | מומלץ עבור צומת יחיד בעל 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | שומר על שכבות 37–42 בדיוק Q4 לצורך דיוק טוב יותר. נכנס ל-128 GB אך משאיר פחות מקום להקשר |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | איכות גבוהה יותר. דורש שני צמתי Halo באמצעות אשכול (clustering) רב-צמתים |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | תוסף אופציונלי לפענוח ספקולטיבי (speculative decoding) לשיפור מהירות הייצור |

מודל **IQ2_XXS imatrix** הוא נקודת התחלה טובה. הוא נכנס בנוחות לצומת יחיד ומשאיר מספיק זיכרון עבור חלון הקשר סביר.

## התקנת ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) הוא ממשק משתמש טקסטואלי קליל שמקל על ההתחלה עם ds4 על Strix Halo. הוא מטפל ביצירת מכולות toolbox, הורדת משקלי מודל, והפעלת שרתים. יש להתקינו באמצעות `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

הפעילו את ה-cockpit:
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

## יצירת ה-Toolbox

בלשונית **Interactive Toolboxes**, בחרו את ה-toolbox העדכני ביותר הזמין (לדוגמה, `ds4-rocm-7.2.4`) ולחצו על **Create/Update**. פעולה זו מושכת את תמונת המכולה ויוצרת את סביבת ה-toolbox.

> **טיפ**: גרסת ה-toolbox תשתנה עם הזמן ככל שיצאו גרסאות ROCm חדשות יותר. בחרו את הגרסה העדכנית ביותר הזמינה ברשימה.

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

## הורדת המודל

עברו ללשונית **Model Manager**. בחרו **IQ2_XXS imatrix (~80.8 GB)** מהתפריט הנפתח ולחצו על **Download**. קובצי המודל יישמרו בברירת מחדל בנתיב `~/ds4` (ניתן לשנות את נתיב האחסון).

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

## הפעלת השרת

עברו ללשונית **Server Mode**. בחרו את המודל שהורדתם ואת ה-toolbox, ולאחר מכן הגדירו את גודל ההקשר (לדוגמה, 126000), המארח (host) והפורט (8000). כשהכול מוכן, לחצו על **Start ds4-server**.

> **מטמון KV בדיסק (KV Disk Cache) (אופציונלי).** הפעלת **KV Disk Cache** מעבירה את מטמון ה-KV לדיסק (ב-**Host Cache Dir**, ברירת מחדל `~/.cache/ds4-kv`) כך שפרומפטים חוזרים של המערכת משוחזרים מ-SSD במקום להיות מחושבים מחדש. זוהי אופטימיזציית ביצועים עבור זרימות עבודה של סוכני קידוד עם פרומפטים ארוכים וחוזרים, והיא **אינה נדרשת** להפעלת השרת.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

השרת יופעל ויאזין בפורט 8000, ויחשוף נקודת קצה API תואמת OpenAI בכתובת `http://localhost:8000/v1`.

**בדיקה מהירה:**
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

## חיבור ממשק Web UI

ניתן לחבר כל ממשק צ'אט התומך בפורמט API של OpenAI. לדוגמה, כדי להשתמש ב-HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

פתחו את `http://localhost:3000` בדפדפן שלכם כדי להתחיל בשיחה.

## חיבור סוכן קידוד

שרת ds4 חושף נקודות קצה תואמות הן ל-OpenAI והן ל-Anthropic, כך שרוב סוכני הקידוד יכולים להתחבר אליו ישירות. לדוגמה, כדי להוסיף אותו לסוכן הקידוד `pi`, יש להוסיף את הבלוק הבא לקובץ `~/.pi/agent/models.json`:

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

> **טיפ**: אם סוכן הקידוד או ה-Web UI שלכם רצים על מכונה שונה מפלטפורמת ה-Halo, יהיה עליכם להעביר (forward) את פורט 8000 דרך SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```
## הצעדים הבאים

- **אשכול מרובה צמתים (Multi-node clustering)**: אם יש לכם שני מכשירי Halo, ds4 תומך בפיזור מודל ה-Q4 (‎~153 GB) על פני שתי המכונות באמצעות מקביליות צנרת (pipeline parallelism). עיינו ב[תיעוד ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) להוראות ההתקנה.
- **פענוח ספקולטיבי (MTP)**: הורידו את משקלי ה-MTP (‎~3.6 GB) והעבירו את `--mtp` לשרת לשם מהירות ייצור מהירה יותר.
- **העברת מטמון KV לדיסק**: עבור זרימות עבודה של סוכן קידוד, הפעילו את `--kv-disk-dir` כך שהנחיות מערכת חוזרות ישוחזרו מה-SSD במקום להיות מחושבות מחדש בכל פעם.

למידע נוסף, עיינו ב[מאגר ds4](https://github.com/antirez/ds4) וב[toolbox של ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).