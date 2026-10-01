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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Επισκόπηση

Το [OpenHands](https://github.com/All-Hands-AI/OpenHands) είναι ένας πράκτορας λογισμικού AI
που μπορεί να γράφει κώδικα, να εκτελεί εντολές, να περιηγείται στο διαδίκτυο και να επεξεργάζεται
αρχεία σε έναν πραγματικό χώρο εργασίας. Αντί να αντιγράφετε προτάσεις από ένα παράθυρο συνομιλίας,
κατευθύνετε τον πράκτορα σε έναν φάκελο έργου και τον αφήνετε να κάνει τη δουλειά: να υλοποιήσει
μια λειτουργία, να διορθώσει ένα σφάλμα, να γράψει δοκιμές ή να εξηγήσει μια βάση κώδικα.

Το [Agent Canvas](https://github.com/OpenHands/agent-canvas) είναι η προτεινόμενη
διεπαφή browser για την εκτέλεση του OpenHands. Μία μόνο εντολή `agent-canvas` ξεκινά
τον διακομιστή πράκτορα, το backend αυτοματισμού και το frontend web μαζί, ώστε να μπορείτε
να οδηγήσετε μια συνομιλία με τον πράκτορα από το πρόγραμμα περιήγησής σας.

Για να διατηρήσετε τα πάντα στο σύστημά σας AMD, ο πράκτορας επικοινωνεί με ένα τοπικό μοντέλο
που εξυπηρετείται από τον Lemonade Server. Το Lemonade εκθέτει αυτό το μοντέλο μέσω ενός
συμβατού με OpenAI API, ώστε το Agent Canvas να μπορεί να το ρυθμίσει όπως κάθε άλλο endpoint
τύπου OpenAI, ενώ το μοντέλο, ο κώδικάς σας και το πλαίσιο της συνομιλίας παραμένουν όλα
στο μηχάνημά σας.

Σε αυτό το playbook, θα ξεκινήσετε ένα τοπικό μοντέλο, θα εκκινήσετε το Agent Canvas, θα το
κατευθύνετε σε αυτό το μοντέλο και θα εκτελέσετε την πρώτη σας εργασία κωδικοποίησης σε έναν
πραγματικό φάκελο έργου.

## Τι θα μάθετε

- Πώς να ξεκινήσετε τον Lemonade Server και να επιβεβαιώσετε ότι ένα τοπικό μοντέλο απαντά σε
  αιτήματα συνομιλίας
- Πώς να εγκαταστήσετε και να εκκινήσετε το Agent Canvas από το πακέτο npm
- Πώς να ρυθμίσετε το Agent Canvas ώστε να χρησιμοποιεί ένα τοπικό μοντέλο Lemonade ως LLM
- Πώς να ξεκινήσετε μια συνομιλία OpenHands και να παρακολουθήσετε τον πράκτορα να επεξεργάζεται
  αρχεία και να εκτελεί εντολές σε έναν χώρο εργασίας
- Πώς να ελέγξετε τι άλλαξε ο πράκτορας και να τον καθοδηγήσετε με επακόλουθα μηνύματα

## Βασικές έννοιες

| Έννοια | Τι είναι | Πού εντάσσεται σε αυτό το playbook |
| --- | --- | --- |
| Lemonade Server | Μια πλατφόρμα εξυπηρέτησης τοπικών LLM κατασκευασμένη για υλικό AMD που εκθέτει ένα συμβατό με OpenAI API. Τα δεδομένα σας δεν φεύγουν ποτέ από το μηχάνημά σας. | Εκτελεί το μοντέλο που τροφοδοτεί τον πράκτορα. |
| OpenHands | Ένας πράκτορας λογισμικού AI που διαβάζει και επεξεργάζεται αρχεία, εκτελεί εντολές shell και περιηγείται στο διαδίκτυο μέσα σε έναν χώρο εργασίας. | Ο πράκτορας που κατευθύνετε από τη συνομιλία. |
| Agent Canvas | Η διεπαφή browser και το backend που εκτελεί συνομιλίες OpenHands και εμφανίζει κλήσεις εργαλείων και αλλαγές αρχείων. | Εκκινεί τη στοίβα και φιλοξενεί τη συνομιλία σας. |
| Χώρος εργασίας | Ο φάκελος έργου που επιτρέπεται στον πράκτορα να διαβάζει και να τροποποιεί. | Ο στόχος των επεξεργασιών και των εντολών του πράκτορα. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Οι ροές εργασίας πράκτορα κωδικοποίησης επωφελούνται από ένα μεγαλύτερο μοντέλο και παράθυρο
> πλαισίου. Χρησιμοποιήστε τουλάχιστον 32 GB μνήμης συστήματος και προτιμήστε 64 GB ή περισσότερα
> για μεγαλύτερα μοντέλα GGUF.
<!-- @device:end -->

## Ρύθμιση διαμόρφωσης μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Έλεγχος για ενημερώσεις λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->

## Προϋποθέσεις


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Χρειάζεστε:

- Τον Lemonade Server εγκατεστημένο και ικανό να εξυπηρετήσει το παρακάτω μοντέλο.

<!-- @os:linux -->
- Node.js 22.12 ή νεότερη έκδοση και `npm` (χρησιμοποιείται από το CLI `agent-canvas`).
- Το `uv`, τον διαχειριστή πακέτων Python που χρησιμοποιεί το Agent Canvas για τη διαχείριση
  του περιβάλλοντος του διακομιστή πράκτορα. Εάν το σύστημά σας δεν το διαθέτει ήδη,
  εγκαταστήστε το από τον [οδηγό εγκατάστασης uv](https://docs.astral.sh/uv/getting-started/installation/)
  πριν εκκινήσετε το Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- Το [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  εγκατεστημένο και σε λειτουργία. Στα Windows, η στοίβα του Agent Canvas εκτελείται από την
  δημοσιευμένη εικόνα Docker, η οποία περιλαμβάνει το Node.js, το `uv` και το πακέτο
  `@openhands/agent-canvas`, οπότε δεν χρειάζεται να τα εγκαταστήσετε στον υπολογιστή σας.
<!-- @os:end -->

- Έναν φάκελο έργου στον οποίο θα εργαστείτε. Μπορεί να είναι οποιοδήποτε τοπικό αποθετήριο
  git ή κατάλογος κώδικα που θέλετε να επεξεργαστεί ο πράκτορας.

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. Εκκίνηση του Lemonade Server

Ξεκινήστε το μοντέλο από το CLI του Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Επιλέξτε ένα μοντέλο που ταιριάζει με το υλικό σας.** Το `Qwen3.6-35B-A3B-GGUF` (~20 GB) είναι ένα ισχυρό μοντέλο κωδικοποίησης αλλά απαιτεί μεγάλη δεξαμενή μνήμης. Εάν η συσκευή σας έχει περιορισμένη μνήμη ή VRAM GPU, επιλέξτε αντ' αυτού ένα μικρότερο μοντέλο GGUF από τη βιβλιοθήκη μοντέλων του Lemonade και χρησιμοποιήστε αυτό το ID μοντέλου σε όλο αυτό το playbook.

> **Σημείωση:** Η πρώτη εκτέλεση `lemonade run` κατεβάζει το μοντέλο εάν δεν υπάρχει ήδη, κάτι που μπορεί να διαρκέσει αρκετή ώρα ανάλογα με το μέγεθος του μοντέλου και τη σύνδεσή σας.

Το Lemonade εκθέτει ένα συμβατό με OpenAI API στη διεύθυνση:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Επαλήθευση του τοπικού μοντέλου

Επιβεβαιώστε ότι το Lemonade μπορεί να εξυπηρετήσει το επιλεγμένο μοντέλο:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Στη συνέχεια, στείλτε ένα μικρό αίτημα συνομιλίας:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Εάν αυτό επιστρέψει έναν πίνακα `choices`, το Lemonade είναι έτοιμο για το Agent Canvas.

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
model_id = "${lemonade_model}"

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
PY

body='{
  "model": "${lemonade_model}",
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
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
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
## 3. Εγκατάσταση και Εκκίνηση του Agent Canvas

<!-- @os:linux -->
Εγκαταστήστε το δημοσιευμένο πακέτο Agent Canvas καθολικά:

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

Έπειτα, ξεκινήστε το πλήρες stack από ένα τερματικό:

```bash
agent-canvas
```

Από προεπιλογή, το Agent Canvas ξεκινά στο `http://localhost:8000`. Ανοίξτε αυτό το URL στο
πρόγραμμα περιήγησής σας. Η θύρα δεν είναι κάτι ιδιαίτερο — αν η 8000 χρησιμοποιείται ήδη, δώστε οποιαδήποτε
ελεύθερη θύρα με το `--port` (ή `-p`) όταν εκκινείτε το Agent Canvas:

```bash
agent-canvas --port 3000
```

Έπειτα ανοίξτε το `http://localhost:3000` αντ' αυτού. Το προεπιλεγμένο τοπικό backend θα πρέπει να εμφανίζεται
ως healthy στην αρχική οθόνη.

Η εντολή `agent-canvas` ξεκινά μαζί τον agent server, το automation backend και
το web frontend. Χρειάζεστε μόνο αυτήν την εντολή για να εκτελέσετε το OpenHands
τοπικά.

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Στα Windows, εκτελέστε τη δημοσιευμένη container image του Agent Canvas με το Docker Desktop.
Η image περιλαμβάνει τον Agent Server, το automation backend και το web frontend, οπότε
δεν χρειάζεται να εγκαταστήσετε Node.js, `uv`, ή το CLI στον host.

Πρώτα, δημιουργήστε τους φακέλους config και workspace που προσαρτά το container:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Κατεβάστε τη δημοσιευμένη image (είναι δημόσια, οπότε δεν απαιτείται login):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Έπειτα ξεκινήστε το stack:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Ανοίξτε το `http://localhost:8000/canvas` στο πρόγραμμα περιήγησής σας. Αν η θύρα 8000 χρησιμοποιείται ήδη,
αντιστοιχίστε μια διαφορετική θύρα host, για παράδειγμα `-p 8080:8000`, και ανοίξτε
το `http://localhost:8080/canvas` αντ' αυτού.

> **Σημείωση:** Η πρώτη εκκίνηση αρχικοποιεί τον Agent Server μέσα στο container,
> οπότε μπορεί να χρειαστεί ένα ή δύο λεπτά μέχρι το backend να αναφέρει ότι είναι healthy.

Η προσάρτηση `.openhands` διατηρεί το προφίλ LLM και τις ρυθμίσεις σας μεταξύ επανεκκινήσεων
του container. Το υπόλοιπο αυτού του οδηγού διαμορφώνει τα πάντα μέσω του UI
του Agent Canvas στο πρόγραμμα περιήγησής σας.

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->

## 4. Διαμόρφωση του Τοπικού LLM

Κατά την πρώτη εκκίνηση, το Agent Canvas ανοίγει μια ροή onboarding. Σε αυτή τη ροή:

1. Κρατήστε επιλεγμένο το **OpenHands** ως agent και κάντε κλικ στο **Next**.
2. Στο **Set up your LLM**, επιλέξτε **Advanced**.
3. Κρατήστε το **Authentication** ρυθμισμένο σε **API key**.
4. Ορίστε το **Custom Model** σε `openai/Qwen3.6-35B-A3B-GGUF`.
5. Ορίστε το **Base URL** σε `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Στα Windows, το stack εκτελείται σε ένα container, το οποίο δεν μπορεί να προσπελάσει τον host στη διεύθυνση
   > `127.0.0.1`. Χρησιμοποιήστε αντ' αυτού το `http://host.docker.internal:13305/api/v1`, ώστε ο
   > containerized agent να μπορεί να προσπελάσει το Lemonade που εκτελείται στον host Windows.
   <!-- @os:end -->
6. Για το **API Key**, εισαγάγετε οποιοδήποτε μη κενό placeholder όπως `lemonade-local`.
   Το Lemonade δεν απαιτεί πραγματικό κλειδί, αλλά ο client OpenHands χρειάζεται μια τιμή
   για να στείλει.
7. Κάντε κλικ στο **Next**.

Οι ολοκληρωμένες ρυθμίσεις Advanced θα πρέπει να μοιάζουν ως εξής. Το πεδίο API key
είναι κρυμμένο από το UI.

![Ρυθμίσεις Advanced LLM κατά την πρώτη χρήση του Agent Canvas με το μοντέλο Lemonade και το τοπικό base URL](assets/01-llm-advanced-settings.png)

Το Agent Canvas αποθηκεύει αυτές τις τιμές ως προφίλ LLM. Αν η έκδοσή σας σας ζητήσει να
ονομάσετε αυτό το προφίλ, χρησιμοποιήστε ένα όνομα χωρίς κενά, όπως `lemonade-local`. Αν αλλάξετε
μοντέλα αργότερα, ανοίξτε το **Settings > LLM** και ενημερώστε τα ίδια πεδία Advanced. Μπορείτε
να αλλάξετε αποθηκευμένα προφίλ από το πεδίο εισαγωγής chat με την εντολή `/model`.

## 5. Άνοιγμα ενός Workspace

Ο agent μπορεί να διαβάσει και να τροποποιήσει αρχεία μόνο μέσα σε ένα workspace που εσείς επιλέγετε. Πριν
ξεκινήσετε μια εργασία, κατευθύνετε το Agent Canvas στον φάκελο του project σας:

1. Από την αρχική οθόνη, επιλέξτε **Open Workspace**.
2. Επιλέξτε τον φάκελο που περιέχει το project σας (για παράδειγμα, ένα αποθετήριο git
   στο οποίο θέλετε να εργαστεί ο agent).
3. Ξεκινήστε μια νέα συνομιλία σε αυτό το workspace.

Οτιδήποτε κάνει ο agent—ανάγνωση αρχείων, εκτέλεση εντολών, επεξεργασία κώδικα—περιορίζεται
σε αυτό το workspace.

![Αρχική οθόνη Agent Canvas μετά το onboarding](assets/02-agent-canvas-home.png)

## 6. Εκτέλεση της Πρώτης σας Εργασίας Προγραμματισμού

Με το workspace ανοιχτό και επιλεγμένο το τοπικό LLM, πληκτρολογήστε μια συγκεκριμένη εργασία στο
chat. Μια καλή πρώτη εργασία είναι μικρή και επαληθεύσιμη, για παράδειγμα:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Παρακολουθήστε το χρονολόγιο της συνομιλίας. Το OpenHands θα:

- Διαβάσει το workspace για να κατανοήσει τη διάταξη.
- Δημιουργήσει το `hello.py` με τη ζητούμενη συνάρτηση και το test block.
- Προαιρετικά εκτελέσει το `python3 hello.py` για να επαληθεύσει το αποτέλεσμα.
- Αναφέρει τι έκανε και οποιοδήποτε αποτέλεσμα εντολής στο chat.

Θα πρέπει να δείτε το νέο αρχείο να εμφανίζεται στο workspace, και το τελικό μήνυμα του agent
θα πρέπει να περιγράφει την αλλαγή που έκανε. Αυτή είναι η στιγμή της ανταμοιβής: ο
agent έγραψε και εκτέλεσε πραγματικό κώδικα στον φάκελο του project σας.

## 7. Επισκόπηση και Καθοδήγηση του Agent

Αφού ο agent ολοκληρώσει ένα βήμα, επισκοπήστε την εργασία του πριν αποδεχτείτε το επόμενο:

- **Αλλαγές αρχείων**: χρησιμοποιήστε το file browser του workspace ή την προβολή diff του agent για
  να δείτε ακριβώς τι προστέθηκε, άλλαξε ή διαγράφηκε.
- **Αποτέλεσμα εντολών**: αναπτύξτε οποιαδήποτε εντολή εκτέλεσε ο agent για να δείτε το stdout, το stderr,
  και τον κωδικό εξόδου.
- **Παρακολούθηση**: αν το αποτέλεσμα δεν είναι αυτό που θέλατε, απαντήστε στην ίδια
  συνομιλία με μια διόρθωση. Ο agent διατηρεί το προηγούμενο πλαίσιο και
  επαναλαμβάνει στα ίδια αρχεία.

Για παράδειγμα, αν το test δεν εμφάνισε τον αναμενόμενο χαιρετισμό, απαντήστε:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Ο agent θα διαβάσει ξανά το αρχείο, θα εκτελέσει την εντολή, θα διαγνώσει το πρόβλημα και θα επεξεργαστεί
ξανά το αρχείο—όλα στην ίδια συνομιλία.
## Αντιμετώπιση προβλημάτων

<!-- @os:linux -->
- **Το `agent-canvas` δεν βρίσκεται στο PATH:** επανεγκαταστήστε με
  `npm install -g @openhands/agent-canvas` και βεβαιωθείτε ότι ο κατάλογος του
  καθολικού δυαδικού αρχείου npm βρίσκεται στο PATH σας πριν το `agent-canvas`
  μπορέσει να εκτελεστεί από νέο τερματικό.
- **Το `npm install -g` αποτυγχάνει με σφάλμα δικαιωμάτων:** διαμορφώστε έναν
  καθολικό κατάλογο npm που ανήκει στον χρήστη, στη συνέχεια ανοίξτε ξανά το
  τερματικό και εγκαταστήστε ξανά το Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **Το `uv` λείπει:** εγκαταστήστε το από
  [τον οδηγό εγκατάστασης uv](https://docs.astral.sh/uv/getting-started/installation/).
  Το Agent Canvas χρησιμοποιεί το `uv` για τη διαχείριση του περιβάλλοντος Python
  του διακομιστή πράκτορα.
<!-- @os:end -->

<!-- @os:windows -->
- **Το `docker pull` ή `docker run` αποτυγχάνει να συνδεθεί:** βεβαιωθείτε ότι
  το Docker Desktop εκτελείται (το εικονίδιο φάλαινας βρίσκεται στη γραμμή
  συστήματος) και ότι η μηχανή έχει ολοκληρώσει την εκκίνηση. Η εντολή
  `docker version` θα πρέπει να εμφανίζει τόσο ενότητα Client όσο και Server.
- **Το container ξεκινά αλλά το backend δεν γίνεται ποτέ υγιές:** η πρώτη
  εκκίνηση αρχικοποιεί τον Agent Server μέσα στο container· δώστε του ένα με
  δύο λεπτά, στη συνέχεια ελέγξτε το `docker logs <container>` για σφάλματα.
- **Το container δεν μπορεί να προσπελάσει το Lemonade:** το container
  προσπελαύνει τον υπολογιστή μέσω `host.docker.internal`. Επιβεβαιώστε ότι το
  Lemonade εξυπηρετεί στον υπολογιστή Windows με `lemonade status`, και
  χρησιμοποιήστε το `http://host.docker.internal:13305/api/v1` ως Base URL
  κατά τη διαμόρφωση του LLM.
<!-- @os:end -->

- **Η διεπαφή χρήστη φορτώνει αλλά το backend εμφανίζεται μη υγιές:**
  περιμένετε ένα με δύο λεπτά για να ολοκληρώσει την εκκίνησή του ο διακομιστής
  πράκτορα, στη συνέχεια ανανεώστε τη σελίδα. Εάν παραμένει μη υγιές,
  επανεκκινήστε τη στοίβα και ελέγξτε τα αρχεία καταγραφής για σφάλματα.
- **Τα αιτήματα συνομιλίας Lemonade αποτυγχάνουν με σφάλμα σύνδεσης:**
  επιβεβαιώστε ότι το `curl -fsS "http://127.0.0.1:13305/api/v1/health"`
  επιτυγχάνει και ότι το Lemonade εξακολουθεί να εξυπηρετεί το μοντέλο με
  `lemonade status`.
- **Ο πράκτορας εμφανίζει σφάλμα σχετικά με το μήκος συμφραζομένων ή το όριο
  διακριτικών (token):** ξεκινήστε μια νέα συνομιλία ώστε ο πράκτορας να μην
  μεταφέρει ένα υπερβολικά μεγάλο ιστορικό. Εάν συνεχίζει να συμβαίνει,
  επανεκκινήστε το Lemonade με μεγαλύτερο `ctx_size` από την προεπιλογή 65536
  (για παράδειγμα `ctx_size=131072`), εφόσον επιτρέπει η μνήμη.
- **Ο πράκτορας παράγει επεξεργασίες χαμηλής ποιότητας ή ελλιπείς:**
  μεταβείτε σε μεγαλύτερο μοντέλο στο Lemonade, ή δώστε στον πράκτορα μια
  μικρότερη, πιο συγκεκριμένη εργασία και αφήστε τον να την ολοκληρώσει πριν
  ζητήσετε την επόμενη αλλαγή.

## Επόμενα Βήματα

- Δοκιμάστε μια μεγαλύτερη εργασία στον ίδιο χώρο εργασίας, όπως την προσθήκη
  ενός αρχείου δοκιμής μονάδας (unit test) ή τη διόρθωση ενός γνωστού σφάλματος,
  και εξετάστε τις διαφορές (diff) του πράκτορα πριν διατηρήσετε την αλλαγή.
- Συνδέστε έναν διακομιστή MCP όπως το GitHub ή το Slack στην ενότητα
  **Customize** ώστε ο πράκτορας να μπορεί να διαβάζει ζητήματα (issues) ή να
  δημοσιεύει ενημερώσεις ενώ εργάζεται.
- Αποθηκεύστε αρκετά προφίλ LLM (ένα γρήγορο μικρό μοντέλο και ένα ισχυρότερο
  μεγάλο μοντέλο) και εναλλάξτε μεταξύ τους με `/model` κατά τη διάρκεια της
  συνομιλίας.
- Προχωρήστε στο [OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview) για να
  μετατρέψετε επαναλαμβανόμενους κύκλους ανάπτυξης σε προγραμματισμένες ή
  βασισμένες σε συμβάντα εκτελέσεις πράκτορα.

## Πόροι

- [Τεκμηρίωση OpenHands](https://docs.openhands.dev/)
- [Επισκόπηση Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Εγκατάσταση Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Προφίλ LLM και διαμόρφωση μοντέλου](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Τεκμηρίωση Lemonade Server](https://lemonade-server.ai/docs)

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->