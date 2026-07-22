<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> Αυτό το playbook χρησιμοποιεί ειδικές ετικέτες που το GitHub δεν μπορεί να αποδώσει. Επισκεφθείτε το [amd.com/playbooks](https://amd.com/playbooks) για να προεπισκοπήσετε σωστά αυτό το περιεχόμενο.
<!-- @github-only:end -->

## Επισκόπηση

Το [DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) είναι η παραλλαγή της οικογένειας DeepSeek V4 με έμφαση στην απόδοση — ένα μοντέλο Mixture of Experts με 284 δισεκατομμύρια παραμέτρους και 13 δισεκατομμύρια ενεργές παραμέτρους. Σύμφωνα με την [τεχνική αναφορά της DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), σημειώνει 79% στο SWE-bench Verified και 91.6% στο LiveCodeBench.

Το [ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) είναι μια αποκλειστική μηχανή συμπερασμού (inference engine) σχεδιασμένη ειδικά για αυτή την αρχιτεκτονική μοντέλου. Αντί για ένα γενικού σκοπού runtime, το ds4 στοχεύει απευθείας στην οικογένεια DeepSeek V4 με βελτιστοποιήσεις πυρήνα (kernel) ειδικά προσαρμοσμένες στην αρχιτεκτονική, για το λογισμικό AMD ROCm™. Είναι επί του παρόντος μία από τις καλύτερες σε απόδοση υλοποιήσεις του DeepSeek V4 Flash στο Strix Halo.

Αυτό το εκπαιδευτικό οδηγεί στη χρήση του `ds4-cockpit`, ενός τερματικού περιβάλλοντος χρήστη (terminal UI), για τη ρύθμιση του ds4, τη λήψη των βαρών του μοντέλου και την έναρξη τοπικής εξυπηρέτησης (serving) του DeepSeek V4 Flash στην πλατφόρμα AMD Ryzen™ AI Halo Developer Platform.

## Τι θα μάθετε

- Πώς να εγκαταστήσετε και να εκκινήσετε το τερματικό περιβάλλον χρήστη `ds4-cockpit`
- Πώς να δημιουργήσετε το toolbox container ROCm για το ds4
- Πώς να κατεβάσετε τη συνιστώμενη κβάντιση (quantization) για έναν μεμονωμένο κόμβο Halo
- Πώς να ξεκινήσετε τον διακομιστή συμπερασμού (inference server) του ds4 και να εκθέσετε ένα endpoint συμβατό με OpenAI
- Πώς να συνδέσετε ένα Web UI ή έναν πράκτορα κωδικοποίησης (coding agent) στον τοπικό διακομιστή

<!-- @setup:memory_config -->

## Εγκατάσταση Προαπαιτούμενου Λογισμικού

> **Απαιτήσεις συστήματος για αυτή τη διαμόρφωση (μονού κόμβου IQ2_XXS με context 126k):**
> - Ένα σύστημα Strix Halo με **τουλάχιστον 128 GB ενοποιημένης μνήμης**.
> - **Η αποκλειστική VRAM στο BIOS (UMA frame buffer) ορισμένη στο ελάχιστο**, ώστε η κοινόχρηστη δεξαμενή μνήμης να μπορεί να είναι όσο το δυνατόν μεγαλύτερη.
> - Η κοινόχρηστη δεξαμενή μνήμης της GPU **ορισμένη σε τουλάχιστον 110 GB**: εκτελέστε `amd-ttm --set 110` (βλ. το παραπάνω βήμα διαμόρφωσης μνήμης) και επανεκκινήστε. Χαμηλότερες τιμές αποτυγχάνουν με σφάλμα έλλειψης μνήμης κατά τη φόρτωση του μοντέλου σε context 126k. Αν το σύστημά σας διαθέτει λιγότερη διαθέσιμη μνήμη, μειώστε αντ' αυτού την τιμή **Context** στο Server Mode.

Το ds4-cockpit χρησιμοποιεί container toolboxes για την εκτέλεση της μηχανής ds4. Εγκαταστήστε τα `podman`, `distrobox` και `pipx`:

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

## Διαθέσιμες Κβαντίσεις

Ο δημιουργός του ds4 παρέχει αρκετές κβαντισμένες εκδόσεις του DeepSeek V4 Flash σε μορφή GGUF. Όλα τα παρακάτω μοντέλα χρησιμοποιούν βαθμονόμηση πίνακα σπουδαιότητας (importance matrix, imatrix), η οποία διατηρεί υψηλότερη ακρίβεια στα τμήματα του μοντέλου που έχουν τη μεγαλύτερη σημασία για εργασίες κωδικοποίησης και συλλογιστικής.

| Κβάντιση | Μέγεθος | Περιγραφή |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | Συνιστάται για έναν μεμονωμένο κόμβο 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Διατηρεί τα επίπεδα 37–42 σε ακρίβεια Q4 για καλύτερη ακρίβεια. Χωράει σε 128 GB αλλά αφήνει λιγότερο χώρο για context |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Υψηλότερη ποιότητα. Απαιτεί δύο κόμβους Halo μέσω πολυκομβικής συγκρότησης σε σύμπλεγμα (multi-node clustering) |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | Προαιρετική προσθήκη για κερδοσκοπική αποκωδικοποίηση (speculative decoding) που βελτιώνει την ταχύτητα παραγωγής |

Το μοντέλο **IQ2_XXS imatrix** αποτελεί ένα καλό σημείο εκκίνησης. Χωράει άνετα σε έναν μεμονωμένο κόμβο και αφήνει αρκετή μνήμη για ένα λογικό παράθυρο context.

## Εγκατάσταση του ds4-cockpit

Το [ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) είναι ένα ελαφρύ τερματικό περιβάλλον χρήστη που διευκολύνει την εκκίνηση με το ds4 στο Strix Halo. Αναλαμβάνει τη δημιουργία toolbox containers, τη λήψη βαρών μοντέλου και την εκκίνηση διακομιστών. Εγκαταστήστε το με το `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Εκκινήστε το cockpit:
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

## Δημιουργία του Toolbox

Στην καρτέλα **Interactive Toolboxes**, επιλέξτε το πιο πρόσφατο διαθέσιμο toolbox (π.χ. `ds4-rocm-7.2.4`) και κάντε κλικ στο **Create/Update**. Αυτό κατεβάζει το image του container και δημιουργεί το περιβάλλον toolbox.

> **Συμβουλή**: Η έκδοση του toolbox θα αλλάζει με τον καιρό καθώς κυκλοφορούν νεότερες εκδόσεις ROCm. Επιλέξτε την πιο πρόσφατη διαθέσιμη στη λίστα.

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

## Λήψη του Μοντέλου

Μεταβείτε στην καρτέλα **Model Manager**. Επιλέξτε **IQ2_XXS imatrix (~80.8 GB)** από το αναπτυσσόμενο μενού και κάντε κλικ στο **Download**. Τα αρχεία του μοντέλου θα αποθηκευτούν στο `~/ds4` από προεπιλογή (μπορείτε να αλλάξετε τη διαδρομή αποθήκευσης).

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

## Εκκίνηση του Διακομιστή

Μεταβείτε στην καρτέλα **Server Mode**. Επιλέξτε το ληφθέν μοντέλο και το toolbox, και στη συνέχεια διαμορφώστε το μέγεθος context (π.χ. 126000), τον host και τη θύρα (8000). Όταν είστε έτοιμοι, κάντε κλικ στο **Start ds4-server**.

> **KV Disk Cache (προαιρετικό).** Η ενεργοποίηση του **KV Disk Cache** μεταφέρει την κρυφή μνήμη KV στον δίσκο (στο **Host Cache Dir**, προεπιλογή `~/.cache/ds4-kv`), ώστε επαναλαμβανόμενα system prompts να επαναφέρονται από το SSD αντί να υπολογίζονται εκ νέου. Πρόκειται για μια βελτιστοποίηση απόδοσης για ροές εργασίας με coding agents που περιλαμβάνουν μεγάλα, επαναλαμβανόμενα prompts, και **δεν απαιτείται** για την εκτέλεση του διακομιστή.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Ο διακομιστής θα ξεκινήσει και θα ακούει στη θύρα 8000, εκθέτοντας ένα endpoint API συμβατό με OpenAI στο `http://localhost:8000/v1`.

**Γρήγορη δοκιμή:**
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

## Σύνδεση ενός Web UI

Μπορείτε να συνδέσετε οποιοδήποτε περιβάλλον συνομιλίας (chat interface) που υποστηρίζει τη μορφή API της OpenAI. Για παράδειγμα, για να χρησιμοποιήσετε το HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Ανοίξτε το `http://localhost:3000` στο πρόγραμμα περιήγησής σας για να ξεκινήσετε τη συνομιλία.

## Σύνδεση ενός Coding Agent

Ο διακομιστής ds4 εκθέτει endpoints συμβατά τόσο με OpenAI όσο και με Anthropic, οπότε οι περισσότεροι coding agents μπορούν να συνδεθούν απευθείας σε αυτόν. Για παράδειγμα, για να τον προσθέσετε στον coding agent `pi`, προσθέστε το παρακάτω μπλοκ στο `~/.pi/agent/models.json`:

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

> **Συμβουλή**: Αν ο coding agent ή το Web UI σας εκτελείται σε διαφορετικό μηχάνημα από την πλατφόρμα Halo, θα χρειαστεί να προωθήσετε τη θύρα 8000 μέσω SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```
## Επόμενα Βήματα

- **Ομαδοποίηση πολλαπλών κόμβων (Multi-node clustering)**: Αν διαθέτετε δύο συσκευές Halo, το ds4 υποστηρίζει τη διανομή του μοντέλου Q4 (~153 GB) και στα δύο μηχανήματα μέσω παραλληλισμού διοχέτευσης (pipeline parallelism). Δείτε την [τεκμηρίωση του ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) για οδηγίες ρύθμισης.
- **Κερδοσκοπική αποκωδικοποίηση (MTP)**: Κατεβάστε τα βάρη MTP (~3.6 GB) και περάστε το `--mtp` στον server για ταχύτερη ταχύτητα δημιουργίας.
- **Εκφόρτωση κρυφής μνήμης KV σε δίσκο**: Για ροές εργασίας πρακτόρων κωδικοποίησης, ενεργοποιήστε το `--kv-disk-dir` ώστε τα επαναλαμβανόμενα system prompts να αποκαθίστανται από τον SSD αντί να υπολογίζονται εκ νέου κάθε φορά.

Για περισσότερες πληροφορίες, δείτε το [αποθετήριο ds4](https://github.com/antirez/ds4) και το [εργαλείο ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).