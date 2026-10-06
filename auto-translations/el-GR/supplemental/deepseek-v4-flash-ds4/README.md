<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Μηχανική μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει ελεγχθεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένες οδηγίες, εντολές, στοιχεία λήψης, διαθεσιμότητα προϊόντων ή άλλο περιεχόμενο ενδέχεται να διαφέρουν ανάλογα με τη γλώσσα ή την περιοχή. Σε περίπτωση οποιασδήποτε ασυμφωνίας ή απόκλισης, υπερισχύει η πρωτότυπη αγγλική έκδοση του playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Επισκόπηση

Το [DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) είναι η παραλλαγή της οικογένειας DeepSeek V4 που εστιάζει στην αποδοτικότητα — ένα μοντέλο Mixture of Experts με 284 δισεκατομμύρια παραμέτρους, εκ των οποίων 13 δισεκατομμύρια είναι ενεργές. Σύμφωνα με την [τεχνική αναφορά της DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), σημειώνει 79% στο SWE-bench Verified και 91.6% στο LiveCodeBench.

Το [ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) είναι μια αφιερωμένη μηχανή εξαγωγής συμπερασμάτων (inference engine) που έχει δημιουργηθεί ειδικά για αυτή την αρχιτεκτονική μοντέλου. Αντί να είναι ένα γενικού σκοπού runtime, το ds4 στοχεύει απευθείας στην οικογένεια DeepSeek V4 με βελτιστοποιήσεις πυρήνα (kernel) ειδικές για την αρχιτεκτονική, για το λογισμικό AMD ROCm™. Αυτή τη στιγμή είναι μία από τις πιο αποδοτικές υλοποιήσεις του DeepSeek V4 Flash στο Strix Halo.

Αυτός ο οδηγός δείχνει πώς να χρησιμοποιήσετε το `ai-toolbox-cockpit`, ένα terminal UI, για να ρυθμίσετε το ds4, να κατεβάσετε τα βάρη του μοντέλου και να ξεκινήσετε την εξυπηρέτηση του DeepSeek V4 Flash τοπικά στην πλατφόρμα AMD Ryzen™ AI Halo Developer Platform.

## Τι θα μάθετε

- Πώς να εγκαταστήσετε και να εκκινήσετε το terminal UI `ai-toolbox-cockpit`
- Πώς να δημιουργήσετε το toolbox container ds4 ROCm
- Λήψη της συνιστώμενης κβαντοποίησης (quantization) για έναν μόνο κόμβο Halo
- Εκκίνηση του διακομιστή εξαγωγής συμπερασμάτων ds4 και έκθεση ενός endpoint συμβατού με OpenAI
- Σύνδεση ενός Web UI ή ενός πράκτορα κωδικοποίησης (coding agent) στον τοπικό διακομιστή

## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

## Εγκατάσταση Προαπαιτούμενου Λογισμικού

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:distrobox,ds4-cockpit,ds4-toolbox-image -->

> **Απαιτήσεις συστήματος για αυτή τη διαμόρφωση (ενιαίος κόμβος IQ2_XXS με πλαίσιο 126k):**
> - Ένα σύστημα Strix Halo με **τουλάχιστον 128 GB ενοποιημένης μνήμης**.
> - Το **αποκλειστικό VRAM του BIOS (UMA frame buffer) ρυθμισμένο στο ελάχιστο**, ώστε η κοινόχρηστη δεξαμενή μνήμης να μπορεί να είναι όσο το δυνατόν μεγαλύτερη.
> - Η **κοινόχρηστη δεξαμενή μνήμης του GPU ρυθμισμένη σε τουλάχιστον 110 GB**: εκτελέστε `amd-ttm --set 110` (δείτε το παραπάνω βήμα διαμόρφωσης μνήμης) και κάντε επανεκκίνηση. Χαμηλότερες τιμές μπορεί να αποτύχουν με σφάλμα έλλειψης μνήμης κατά τη φόρτωση του μοντέλου με πλαίσιο 126k. Αν το σύστημά σας διαθέτει λιγότερη διαθέσιμη μνήμη, μειώστε αντ' αυτού την τιμή **Context** στη λειτουργία Server Mode.
>
> **Σημείωση:** Δοκιμάστε να ρυθμίσετε την **κοινόχρηστη δεξαμενή μνήμης του GPU** στα **110 GB** ως σημείο εκκίνησης. Αν αντιμετωπίσετε σφάλματα έλλειψης μνήμης, αυξήστε την κοινόχρηστη δεξαμενή μνήμης ή μειώστε το μέγεθος του πλαισίου.

Το ai-toolbox-cockpit χρησιμοποιεί container toolboxes για να εκτελέσει τη μηχανή ds4. Εγκαταστήστε τα `podman`, `distrobox`, και `pipx`:

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

## Διαθέσιμες Κβαντοποιήσεις

Ο δημιουργός του ds4 παρέχει αρκετές κβαντοποιημένες εκδόσεις του DeepSeek V4 Flash σε μορφή GGUF. Όλα τα παρακάτω μοντέλα χρησιμοποιούν βαθμονόμηση importance matrix (imatrix), η οποία διατηρεί υψηλότερη ακρίβεια για τα μέρη του μοντέλου που έχουν τη μεγαλύτερη σημασία για εργασίες κωδικοποίησης και συλλογιστικής.

| Κβαντοποίηση | Μέγεθος | Περιγραφή |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | Συνιστάται για έναν μόνο κόμβο 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Διατηρεί τα επίπεδα 37–42 σε ακρίβεια Q4 για καλύτερη ακρίβεια. Χωράει σε 128 GB αλλά αφήνει λιγότερο χώρο για πλαίσιο |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Υψηλότερη ποιότητα. Απαιτεί δύο κόμβους Halo μέσω συστάδας πολλαπλών κόμβων (multi-node clustering) |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | Προαιρετική επέκταση για speculative decoding ώστε να βελτιωθεί η ταχύτητα παραγωγής |

Το μοντέλο **IQ2_XXS imatrix** αποτελεί ένα καλό σημείο εκκίνησης. Χωράει άνετα σε έναν μόνο κόμβο και αφήνει αρκετή μνήμη για ένα λογικό μέγεθος παραθύρου πλαισίου.

## Εγκατάσταση του ai-toolbox-cockpit

Το [ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) είναι ένα ελαφρύ terminal UI που διευκολύνει την εγκατάσταση διάφορων backend τεχνητής νοημοσύνης. Θα το χρησιμοποιήσουμε για να διαχειριστούμε τη δημιουργία του container ds4, τη λήψη των βαρών του μοντέλου και την εκκίνηση διακομιστών. Εγκαταστήστε το με `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Εκκινήστε το cockpit:
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

## Βήμα 1: Δημιουργία του Toolbox

Στην καρτέλα **Interactive Toolboxes**, επιλέξτε το πιο πρόσφατο διαθέσιμο/σταθερό toolbox για το ds4 (π.χ. `ds4-rocm-10.0`) και κάντε κλικ στο **Create/Update**. Αυτό κατεβάζει την εικόνα container και δημιουργεί το περιβάλλον toolbox.


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

## Βήμα 2: Λήψη του Μοντέλου

Μεταβείτε στην καρτέλα **Models**. Πρώτα, επιλέξτε το backend (ds4). Στη συνέχεια, επιλέξτε το **IQ2_XXS imatrix (~80.8 GB)** από το αναπτυσσόμενο μενού και κάντε κλικ στο **Download**. Τα αρχεία του μοντέλου θα αποθηκευτούν στο `~/ds4` από προεπιλογή (μπορείτε να αλλάξετε τη διαδρομή αποθήκευσης).

> **Σημείωση:** Το μοντέλο IQ2_XXS έχει μέγεθος περίπου 80 GB, οπότε η λήψη μπορεί να διαρκέσει αρκετά, ανάλογα με τη σύνδεσή σας. Μπορείτε να συνεχίσετε μόλις ολοκληρωθεί.

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

## Βήμα 3: Εκκίνηση του Διακομιστή

Μεταβείτε στην καρτέλα **Server Mode**. Επιλέξτε το μοντέλο που κατεβάσατε και το toolbox, στη συνέχεια διαμορφώστε το μέγεθος πλαισίου, τον host και τη θύρα (port). Όταν είστε έτοιμοι, κάντε κλικ στο **Start ds4-server**.

> **Συμβουλή** Ένα μέγεθος πλαισίου `126000` είναι μια λογική αρχική τιμή που θα πρέπει να χωρέσει σε έναν μόνο κόμβο — μπορείτε να το ορίσετε υψηλότερα αν έχετε περισσότερη διαθέσιμη μνήμη, ή χαμηλότερα αν αντιμετωπίσετε σφάλματα έλλειψης μνήμης. Η θύρα (`8000` σε αυτόν τον οδηγό) είναι αυθαίρετη· επιλέξτε οποιαδήποτε ελεύθερη θύρα.

> **KV Disk Cache (προαιρετικό).** Η ενεργοποίηση του **KV Disk Cache** μεταφέρει την προσωρινή μνήμη KV (KV cache) στον δίσκο (στο **Host Cache Dir**, προεπιλογή `~/.cache/ds4-kv`), ώστε οι επαναλαμβανόμενες προτροπές συστήματος (system prompts) να ανακτώνται από το SSD αντί να υπολογίζονται εκ νέου. Πρόκειται για μια βελτιστοποίηση απόδοσης για ροές εργασίας πρακτόρων κωδικοποίησης (coding agent) με μεγάλες, επαναλαμβανόμενες προτροπές, και **δεν απαιτείται** για την εκτέλεση του διακομιστή.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Ο διακομιστής θα ξεκινήσει και θα ακούει στη θύρα 8000, εκθέτοντας ένα endpoint API συμβατό με OpenAI στο `http://localhost:8000/v1`.

**Γρήγορος έλεγχος:**
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
## Σύνδεση ενός Web UI

Μπορείτε να συνδέσετε οποιαδήποτε διεπαφή συνομιλίας που υποστηρίζει τη μορφή OpenAI API. Για παράδειγμα, για να χρησιμοποιήσετε το HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Ανοίξτε το `http://localhost:3000` στο πρόγραμμα περιήγησής σας για να ξεκινήσετε τη συνομιλία.

> **Σημείωση:** Το `--network=host` τοποθετεί το Web UI στο δίκτυο του host ώστε να μπορεί να προσεγγίσει απευθείας τον διακομιστή ds4 στο `localhost`. Αυτό διατηρεί τον διακομιστή ds4 συνδεδεμένο στο loopback (δεν χρειάζεται να εκτεθεί σε άλλες διεπαφές).

> **Συμβουλή:** Η θύρα του Web UI (`3000` εδώ, ορίζεται μέσω του `PORT`) είναι αυθαίρετη — επιλέξτε οποιαδήποτε ελεύθερη θύρα αν η `3000` χρησιμοποιείται ήδη, και ανοίξτε αυτή τη θύρα στο πρόγραμμα περιήγησής σας. Βεβαιωθείτε ότι η θύρα στο `OPENAI_BASE_URL` ταιριάζει με τη θύρα στην οποία εκτελείται ο διακομιστής ds4.

## Σύνδεση ενός Coding Agent

Ο διακομιστής ds4 εκθέτει endpoints συμβατά τόσο με OpenAI όσο και με Anthropic, οπότε οι περισσότεροι coding agents μπορούν να συνδεθούν απευθείας σε αυτόν. Για παράδειγμα, για να τον προσθέσετε στον coding agent `pi`, προσθέστε το παρακάτω block στο `~/.pi/agent/models.json`:

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

> **Συμβουλή**: Εάν ο coding agent ή το Web UI σας εκτελείται σε διαφορετική μηχανή από την πλατφόρμα Halo, θα χρειαστεί να προωθήσετε τη θύρα του διακομιστή (`8000` εδώ) μέσω SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Επόμενα Βήματα

- **Clustering πολλαπλών κόμβων**: Αν διαθέτετε δύο συσκευές Halo, το ds4 υποστηρίζει τη διανομή του μοντέλου Q4 (~153 GB) και στις δύο μηχανές μέσω pipeline parallelism. Δείτε την [τεκμηρίωση ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) για οδηγίες ρύθμισης.
- **Speculative decoding (MTP)**: Κατεβάστε τα βάρη MTP (~3.6 GB) και περάστε το `--mtp` στον διακομιστή για ταχύτερη ταχύτητα παραγωγής.
- **Αποφόρτωση της προσωρινής μνήμης KV σε δίσκο**: Για ροές εργασίας coding agent, ενεργοποιήστε το `--kv-disk-dir` ώστε οι επαναλαμβανόμενες system prompts να επαναφέρονται από το SSD αντί να υπολογίζονται εκ νέου κάθε φορά.

Για περισσότερες πληροφορίες, δείτε το [αποθετήριο ds4](https://github.com/antirez/ds4) και το [εργαλειοθήκη ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).