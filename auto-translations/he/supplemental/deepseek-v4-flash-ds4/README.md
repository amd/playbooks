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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) הוא הוריאנט הממוקד ביעילות ממשפחת DeepSeek V4 — מודל Mixture of Experts בעל 284 מיליארד פרמטרים עם 13 מיליארד פרמטרים פעילים. על פי [הדוח הטכני של DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), הוא משיג ציון של 79% ב-SWE-bench Verified ו-91.6% ב-LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) הוא מנוע הסקה ייעודי שנבנה במיוחד עבור ארכיטקטורת מודל זו. במקום זמן ריצה כללי, ds4 מכוון ישירות למשפחת DeepSeek V4 עם אופטימיזציות ליבה (kernel) ספציפיות לארכיטקטורה עבור תוכנת AMD ROCm™. זהו כיום אחד המימושים בעלי הביצועים הטובים ביותר של DeepSeek V4 Flash על Strix Halo.

מדריך זה מראה כיצד להשתמש ב-`ai-toolbox-cockpit`, ממשק משתמש מסוף, כדי להגדיר את ds4, להוריד משקלי מודל, ולהתחיל להגיש את DeepSeek V4 Flash באופן מקומי על פלטפורמת המפתחים AMD Ryzen™ AI Halo.

## מה תלמדו

- כיצד להתקין ולהפעיל את ממשק המשתמש של המסוף `ai-toolbox-cockpit`
- כיצד ליצור את מכולת ה-toolbox של ROCm עבור ds4
- הורדת הקוונטיזציה המומלצת עבור צומת Halo יחיד
- הפעלת שרת ההסקה של ds4 וחשיפת נקודת קצה תואמת OpenAI
- חיבור ממשק אינטרנט (Web UI) או סוכן קידוד לשרת המקומי

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

## התקנת דרישות תוכנה מקדימות

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:distrobox,ds4-cockpit,ds4-toolbox-image -->

> **דרישות מערכת עבור תצורה זו (צומת יחיד IQ2_XXS בהקשר של 126k):**
> - מערכת Strix Halo עם **לפחות 128 GB זיכרון מאוחד**.
> - **זיכרון VRAM ייעודי ב-BIOS (מאגר מסגרות UMA) מוגדר למינימום**, כך שמאגר הזיכרון המשותף יוכל להיות גדול ככל האפשר.
> - **מאגר הזיכרון המשותף של ה-GPU מוגדר לפחות ל-110 GB**: הריצו `amd-ttm --set 110` (ראו את שלב הגדרת הזיכרון לעיל) ואתחלו מחדש. ערכים נמוכים יותר עלולים להיכשל עם שגיאת חוסר זיכרון כאשר המודל נטען בהקשר של 126k. אם במערכת שלכם זמין פחות זיכרון, הורידו במקום זאת את ערך **Context** במצב שרת (Server Mode).
>
> **הערה:** נסו להגדיר את **מאגר הזיכרון המשותף של ה-GPU** ל-**110 GB** כנקודת התחלה. אם נתקלים בשגיאות חוסר זיכרון, הגדילו את מאגר הזיכרון המשותף או הקטינו את גודל ההקשר.

ai-toolbox-cockpit משתמש במכולות toolbox להרצת מנוע ds4. התקינו את `podman`, `distrobox`, ו-`pipx`:

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

יוצר ds4 מספק מספר גרסאות מקוונטטות של DeepSeek V4 Flash בפורמט GGUF. כל המודלים שלהלן משתמשים בכיול מטריצת חשיבות (imatrix), אשר שומר על דיוק גבוה יותר עבור חלקי המודל החשובים ביותר למשימות קידוד והיגיון.

| קוונטיזציה | גודל | תיאור |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | מומלץ עבור צומת יחיד בן 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | שומר על שכבות 37–42 בדיוק Q4 לדיוק טוב יותר. מתאים ל-128 GB אך משאיר פחות מקום להקשר |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | איכות גבוהה יותר. דורש שני צמתי Halo באמצעות אשכול מרובה-צמתים |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | תוספת אופציונלית לפענוח ספקולטיבי לשיפור מהירות הייצור |

מודל **IQ2_XXS imatrix** הוא נקודת התחלה טובה. הוא מתאים בנוחות לצומת יחיד ומשאיר מספיק זיכרון עבור חלון הקשר סביר.

## התקנת ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) הוא ממשק משתמש מסוף קליל שמקל על התקנת מגוון backend-ים של AI. נשתמש בו כדי לטפל ביצירת מכולת ds4 שלנו, הורדת משקלי מודל, והפעלת שרתים. התקינו אותו עם `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

הפעילו את ה-cockpit:
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

## שלב 1: יצירת ה-Toolbox

בלשונית **Interactive Toolboxes**, בחרו את ה-toolbox העדכני/היציב הזמין ביותר עבור ds4 (למשל, `ds4-rocm-10.0`) ולחצו על **Create/Update**. פעולה זו מושכת את תמונת המכולה ויוצרת את סביבת ה-toolbox.


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

## שלב 2: הורדת המודל

עברו ללשונית **Models**. ראשית, בחרו את ה-backend (ds4). לאחר מכן, בחרו את **IQ2_XXS imatrix (~80.8 GB)** מהתפריט הנפתח ולחצו על **Download**. קבצי המודל יישמרו ב-`~/ds4` כברירת מחדל (ניתן לשנות את נתיב האחסון).

> **הערה:** מודל ה-IQ2_XXS גדול בערך 80 GB, כך שההורדה עלולה לקחת זמן בהתאם לחיבור שלכם. ניתן להמשיך לאחר סיומה.

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

## שלב 3: הפעלת השרת

עברו ללשונית **Server Mode**. בחרו את המודל שהורד ואת ה-toolbox, ולאחר מכן הגדירו את גודל ההקשר, המארח (host) והפורט. כשתהיו מוכנים, לחצו על **Start ds4-server**.

> **טיפ** גודל הקשר של `126000` הוא ערך התחלתי סביר שאמור להתאים לצומת יחיד — ניתן להגדיר אותו גבוה יותר אם יש לכם זיכרון פנוי, או להנמיך אותו אם נתקלים בשגיאות חוסר זיכרון. הפורט (`8000` במדריך זה) הוא שרירותי; בחרו כל פורט פנוי.

> **מטמון דיסק KV (אופציונלי).** הפעלת **KV Disk Cache** מעבירה את מטמון ה-KV לדיסק (ב-**Host Cache Dir**, ברירת מחדל `~/.cache/ds4-kv`) כך שהנחיות מערכת חוזרות (system prompts) משוחזרות מ-SSD במקום להיות מחושבות מחדש. זוהי אופטימיזציית ביצועים עבור זרימות עבודה של סוכני קידוד עם הנחיות ארוכות וחוזרות, והיא **אינה נדרשת** להרצת השרת.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
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
## חיבור ממשק Web UI

ניתן לחבר כל ממשק צ'אט התומך בפורמט OpenAI API. לדוגמה, כדי להשתמש ב-HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

פתחו את `http://localhost:3000` בדפדפן כדי להתחיל לשוחח.

> **הערה:** `--network=host` ממקם את ה-Web UI ברשת של המארח כך שהוא יכול להגיע לשרת ds4 ישירות דרך `localhost`. כך שרת ה-ds4 נשאר מוגבל לממשק loopback (אין צורך לחשוף אותו בממשקים אחרים).

> **טיפ:** הפורט של ה-Web UI (`3000` כאן, מוגדר באמצעות `PORT`) הוא שרירותי — ניתן לבחור כל פורט פנוי אם `3000` כבר בשימוש, ולפתוח את אותו פורט בדפדפן במקום. ודאו שהפורט ב-`OPENAI_BASE_URL` תואם לפורט שבו פועל שרת ה-ds4.

## חיבור סוכן קידוד (Coding Agent)

שרת ds4 חושף נקודות קצה תואמות הן ל-OpenAI והן ל-Anthropic, כך שרוב סוכני הקידוד יכולים להתחבר אליו ישירות. לדוגמה, כדי להוסיף אותו לסוכן הקידוד `pi`, הוסיפו את הבלוק הבא לקובץ `~/.pi/agent/models.json`:

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

> **טיפ**: אם סוכן הקידוד או ה-Web UI שלכם פועלים על מכונה שונה מפלטפורמת Halo, תצטרכו להעביר (forward) את פורט השרת (`8000` כאן) דרך SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## השלבים הבאים

- **אשכול מרובה-צמתים (Multi-node clustering)**: אם יש לכם שני מכשירי Halo, ds4 תומך בחלוקת המודל Q4 (כ-153 ג'יגה-בייט) בין שתי המכונות באמצעות pipeline parallelism. ראו את [תיעוד ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) להוראות התקנה.
- **פענוח ספקולטיבי (MTP)**: הורידו את משקולות ה-MTP (כ-3.6 ג'יגה-בייט) והעבירו `--mtp` לשרת כדי לקבל מהירות יצירה מהירה יותר.
- **העברת מטמון KV לדיסק (KV cache disk offloading)**: עבור זרימות עבודה של סוכני קידוד, הפעילו את `--kv-disk-dir` כך שהנחיות מערכת חוזרות (system prompts) ישוחזרו מה-SSD במקום להיות מחושבות מחדש בכל פעם.

למידע נוסף, ראו את [מאגר ds4](https://github.com/antirez/ds4) ואת [כלי ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).