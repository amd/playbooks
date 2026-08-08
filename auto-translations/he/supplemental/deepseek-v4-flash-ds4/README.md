<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## סקירה כללית

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) הוא הגרסה הממוקדת ביעילות של משפחת DeepSeek V4 — מודל Mixture of Experts בעל 284 מיליארד פרמטרים עם 13 מיליארד פרמטרים פעילים. על פי [הדוח הטכני של DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), הוא משיג ציון של 79% ב-SWE-bench Verified ו-91.6% ב-LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) הוא מנוע היסק ייעודי שנבנה במיוחד עבור ארכיטקטורת המודל הזו. במקום זמן ריצה כללי, ds4 מכוון ישירות למשפחת DeepSeek V4 עם אופטימיזציות kernel ספציפיות לארכיטקטורה עבור תוכנת AMD ROCm™. זהו כיום אחד היישומים בעלי הביצועים הטובים ביותר של DeepSeek V4 Flash על Strix Halo.

מדריך זה מראה כיצד להשתמש ב-`ds4-cockpit`, ממשק משתמש טרמינלי, כדי להגדיר את ds4, להוריד את משקלי המודל, ולהתחיל להריץ את DeepSeek V4 Flash באופן מקומי על AMD Ryzen™ AI Halo Developer Platform.

## מה תלמד

- כיצד להתקין ולהפעיל את ממשק המשתמש הטרמינלי `ds4-cockpit`
- כיצד ליצור את מיכל ה-toolbox של ds4 ROCm
- הורדת הקוונטיזציה המומלצת עבור מפרק Halo יחיד
- הפעלת שרת ההיסק של ds4 וחשיפת נקודת קצה תואמת OpenAI
- חיבור ממשק Web UI או סוכן קידוד לשרת המקומי

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

## התקנת דרישות תוכנה מקדימות

> **דרישות מערכת עבור תצורה זו (IQ2_XXS במפרק יחיד עם הקשר של 126k):**
> - מערכת Strix Halo עם **לפחות 128 GB של זיכרון מאוחד**.
> - **VRAM ייעודי ב-BIOS (מאגר מסגרות UMA) מוגדר למינימום**, כך שמאגר הזיכרון המשותף יוכל להיות גדול ככל האפשר.
> - **מאגר הזיכרון המשותף של ה-GPU מוגדר לפחות ל-110 GB**: הרץ `amd-ttm --set 110` (ראה שלב תצורת הזיכרון לעיל) ואתחל מחדש. ערכים נמוכים יותר עלולים להיכשל עקב חוסר זיכרון בעת טעינת המודל בהקשר של 126k. אם למערכת שלך יש פחות זיכרון זמין, הורד במקום זאת את ערך ה-**Context** במצב שרת.
>
> **הערה:** נסה להגדיר את **מאגר הזיכרון המשותף של ה-GPU** ל-**110 GB** כנקודת מוצא. אם אתה נתקל בשגיאות חוסר זיכרון, הגדל את מאגר הזיכרון המשותף או הקטן את גודל ההקשר.

ds4-cockpit משתמש ב-toolboxes של מיכלים כדי להריץ את מנוע ds4. התקן את `podman`, `distrobox`, ו-`pipx`:

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

## קוונטיזציות זמינות

מחבר ds4 מספק מספר גרסאות מקוונטזות של DeepSeek V4 Flash בפורמט GGUF. כל המודלים למטה משתמשים בכיול מטריצת חשיבות (imatrix), השומר על דיוק גבוה יותר עבור החלקים במודל החשובים ביותר למשימות קידוד וחשיבה.

| קוונטיזציה | גודל | תיאור |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | מומלץ עבור מפרק יחיד בעל 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | שומר על שכבות 37–42 בדיוק Q4 לדיוק טוב יותר. מתאים ל-128 GB אך משאיר פחות מקום להקשר |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | איכות גבוהה יותר. דורש שני מפרקי Halo באמצעות אשכול מרובה-מפרקים |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | תוסף אופציונלי לפענוח ספקולטיבי לשיפור מהירות היצירה |

מודל ה-**IQ2_XXS imatrix** הוא נקודת התחלה טובה. הוא מתאים בקלות למפרק יחיד ומשאיר מספיק זיכרון לחלון הקשר סביר.

## התקנת ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) הוא ממשק משתמש טרמינלי קליל שהופך את תהליך ההפעלה של ds4 על Strix Halo לפשוט. הוא מטפל ביצירת מיכלי toolbox, הורדת משקלי מודל, והפעלת שרתים. התקן אותו באמצעות `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

הפעל את ה-cockpit:
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

בכרטיסייה **Interactive Toolboxes**, בחר את ה-toolbox העדכני/יציב הזמין (למשל `ds4-rocm-7.2.4`) ולחץ על **Create/Update**. פעולה זו מושכת את תמונת המיכל ויוצרת את סביבת ה-toolbox.


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

עבור לכרטיסייה **Model Manager**. בחר **IQ2_XXS imatrix (~80.8 GB)** מהתפריט הנפתח ולחץ על **Download**. קבצי המודל יישמרו ב-`~/ds4` כברירת מחדל (ניתן לשנות את נתיב האחסון).

> **הערה:** מודל ה-IQ2_XXS גודלו כ-80 GB, כך שההורדה עשויה להימשך זמן מה בהתאם לחיבור שלך. תוכל להמשיך לאחר סיומה.

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

עבור לכרטיסייה **Server Mode**. בחר את המודל שהורדת ואת ה-toolbox, ולאחר מכן הגדר את גודל ההקשר, המארח, והפורט. כשאתה מוכן, לחץ על **Start ds4-server**.

> **טיפ** גודל הקשר של `126000` הוא ערך התחלתי סביר שאמור להתאים למפרק יחיד — ניתן להגדיר אותו גבוה יותר אם יש לך זיכרון פנוי, או נמוך יותר אם אתה נתקל בשגיאות חוסר זיכרון. הפורט (`8000` במדריך זה) הוא שרירותי; בחר כל פורט פנוי.

> **מטמון דיסק KV (אופציונלי).** הפעלת **KV Disk Cache** מעבירה את מטמון ה-KV לדיסק (ב-**Host Cache Dir**, ברירת המחדל `~/.cache/ds4-kv`) כך שהוראות מערכת חוזרות משוחזרות מ-SSD במקום להיחשב מחדש. זוהי אופטימיזציית ביצועים עבור זרימות עבודה של סוכני קידוד עם הוראות ארוכות וחוזרות, ו**אינה נדרשת** להפעלת השרת.

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

ניתן לחבר כל ממשק צ'אט התומך בפורמט OpenAI API. לדוגמה, כדי להשתמש ב-HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

פתח את `http://localhost:3000` בדפדפן שלך כדי להתחיל לשוחח.
## חיבור סוכן קידוד

שרת ds4 חושף נקודות קצה תואמות גם ל-OpenAI וגם ל-Anthropic, כך שרוב סוכני הקידוד יכולים להתחבר אליו ישירות. לדוגמה, כדי להוסיף אותו לסוכן הקידוד `pi`, הוסיפו את הבלוק הבא ל-`~/.pi/agent/models.json`:

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

> **טיפ**: אם סוכן הקידוד או ה-Web UI שלכם רץ על מכונה שונה מפלטפורמת Halo, תצטרכו להעביר (forward) את פורט 8000 דרך SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## הצעדים הבאים

- **אשכולות (clustering) מרובי-צמתים**: אם יש לכם שני מכשירי Halo, ds4 תומך בפיזור מודל Q4 (‏~153GB) על פני שתי המכונות באמצעות מקביליות צנרת (pipeline parallelism). ראו את [תיעוד ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) להוראות הגדרה.
- **פענוח ספקולטיבי (MTP)**: הורידו את משקלי ה-MTP (‏~3.6GB) והעבירו `--mtp` לשרת לצורך מהירות יצירה מהירה יותר.
- **פריקת מטמון KV לדיסק**: עבור זרימות עבודה של סוכני קידוד, הפעילו את `--kv-disk-dir` כדי שהנחיות מערכת (system prompts) חוזרות יושחזרו מה-SSD במקום להיות מחושבות מחדש בכל פעם.

למידע נוסף, ראו את [מאגר ds4](https://github.com/antirez/ds4) ואת [ארגז הכלים ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).