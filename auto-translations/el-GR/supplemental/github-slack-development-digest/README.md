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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Επισκόπηση

Οι προγραμματιστές αφιερώνουν πολύ χρόνο σε μικρούς επαναλαμβανόμενους βρόχους: την αξιολόγηση σημειωμένων pull requests, την απάντηση σε σχόλια στο GitHub, την ταξινόμηση νέων issues, τη μετατροπή νημάτων στο Slack σε σημειώσεις standup ή παρακολούθηση περιστατικών, και την παρακολούθηση σημάτων έκδοσης ή έρευνας.
Κάθε βρόχος είναι οικείος, αλλά εξακολουθεί να απαιτεί κρίση: τη συλλογή του σωστού πλαισίου, την απόφαση για το τι έχει σημασία και την ανάρτηση μιας σαφούς ενημέρωσης εκεί όπου ήδη εργάζεται η ομάδα.

Οι [αυτοματισμοί OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) μετατρέπουν αυτούς τους βρόχους σε προγραμματισμένες ή ενεργοποιούμενες από συμβάντα συνομιλίες πράκτορα: εκτελέσεις όπου ένας πράκτορας λογισμικού AI μπορεί να διαβάσει το πλαίσιο, να καλέσει εργαλεία και να παράγει μια ενημέρωση.
Τα κοινόχρηστα πρότυπα αυτοματισμού στον κατάλογο επεκτάσεων OpenHands ακολουθούν αυτό το μοτίβο για την αξιολόγηση pull request στο GitHub, την παρακολούθηση αποθετηρίου, την ταξινόμηση issues στο Linear, τις αναδρομικές αναλύσεις περιστατικών, τις συνοψίσεις standup στο Slack και τις αναφορές έρευνας: ένας αυτοματισμός ενεργοποιείται, χρησιμοποιεί διαμορφωμένες ενσωματώσεις όπως το GitHub ή το Slack για να ανακτήσει πλαίσιο, συλλογίζεται πάνω σε αυτό το πλαίσιο με ένα μεγάλο γλωσσικό μοντέλο (LLM) και καταγράφει ένα αποτέλεσμα.

Το [Agent Canvas](https://github.com/OpenHands/agent-canvas) είναι το τοπικό επίπεδο ελέγχου για τη δημιουργία και δοκιμή αυτών των αυτοματισμών.
Σε αυτόν τον οδηγό, εκτελεί έναν OpenHands Agent Server, τη διεργασία backend που εκτελεί τις συνομιλίες του πράκτορα, και συνδέει τον πράκτορα με εξωτερικές υπηρεσίες όπως το GitHub και το Slack.

Για να διατηρηθεί η ροή εργασίας στο σύστημά σας AMD, ο πράκτορας επικοινωνεί με ένα τοπικό μοντέλο που εξυπηρετείται από το Lemonade Server.
Το Lemonade εκθέτει αυτό το μοντέλο μέσω ενός API συμβατού με το OpenAI, ώστε το Agent Canvas να μπορεί να το διαμορφώσει σαν ένα απομακρυσμένο endpoint τύπου OpenAI, ενώ το μοντέλο, η προτροπή (prompt) και το πλαίσιο της ροής εργασίας παραμένουν τοπικά.

Σε αυτόν τον οδηγό, θα δημιουργήσετε έναν συγκεκριμένο αυτοματισμό: ένα προγραμματισμένο ημερήσιο σύνοψη ανάπτυξης από το GitHub προς το Slack.
Χρησιμοποιεί το GitHub για να επιθεωρήσει πρόσφατη δραστηριότητα αποθετηρίου, το Slack για να αναρτήσει τη σύνοψη, κλήσεις στο Agent Canvas API για να διαμορφώσει και να δοκιμάσει τον αυτοματισμό, και το Lemonade για να εκτελέσει το LLM τοπικά.

![Διάγραμμα αρχιτεκτονικής που δείχνει το GitHub MCP, τον αυτοματισμό OpenHands, το Lemonade Server και το Slack MCP](assets/00-architecture-overview.png)

## Τι Θα Μάθετε

- Πώς να ξεκινήσετε το Lemonade Server και να επαληθεύσετε ότι ένα τοπικό μοντέλο απαντά σε αιτήματα συνομιλίας
- Πώς να εκκινήσετε το Agent Canvas και να κατευθύνετε τον Agent Server του σε ένα τοπικό LLM
- Πώς να εγκαταστήσετε διακομιστές GitHub και Slack Model Context Protocol (MCP) μέσω του API του Agent Server
- Πώς να δημιουργήσετε και να αποστείλετε έναν προγραμματισμένο αυτοματισμό OpenHands που αναρτά μια σύνοψη ανάπτυξης στο Slack
- Πώς να αντιμετωπίσετε τα πιο συνηθισμένα σφάλματα τοπικού μοντέλου και αυτοματισμού

## Βασικές Έννοιες

| Έννοια | Τι είναι | Πού ταιριάζει σε αυτόν τον οδηγό |
| --- | --- | --- |
| Lemonade Server | Μια πλατφόρμα εξυπηρέτησης τοπικού LLM σχεδιασμένη για υλικό AMD που εκθέτει ένα API συμβατό με το OpenAI. Τα δεδομένα σας δεν φεύγουν ποτέ από το μηχάνημά σας. | Εκτελεί το μοντέλο που τροφοδοτεί τον πράκτορα. |
| OpenHands Agent Server | Η διεργασία backend που εκτελεί τις συνομιλίες του πράκτορα OpenHands. | Φιλοξενεί τον πράκτορα, το προφίλ LLM του και τους διακομιστές MCP του. |
| Agent Canvas | Το τοπικό επίπεδο ελέγχου για το OpenHands που εκτελεί τον Agent Server και ένα περιβάλλον χρήστη για την επιθεώρηση των εκτελέσεων του πράκτορα. | Εκκινεί τα backends και παρέχει το API που καλείτε. |
| Διακομιστής MCP | Ένας διακομιστής Model Context Protocol που δίνει σε έναν πράκτορα εργαλεία για μια εξωτερική υπηρεσία όπως το GitHub ή το Slack. | Επιτρέπει στον πράκτορα να διαβάζει από το GitHub και να γράφει στο Slack. |
| Αυτοματισμός OpenHands | Μια προγραμματισμένη ή ενεργοποιούμενη από συμβάντα συνομιλία πράκτορα που ανακτά πλαίσιο, συλλογίζεται πάνω σε αυτό και καταγράφει ένα αποτέλεσμα κάπου. | Η σύνοψη από το GitHub προς το Slack που δημιουργείτε εδώ. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Οι ροές εργασίας πράκτορα κωδικοποίησης επωφελούνται από ένα μεγαλύτερο μοντέλο και παράθυρο πλαισίου.
> Χρησιμοποιήστε τουλάχιστον 32 GB μνήμης συστήματος, και προτιμήστε 64 GB ή περισσότερα για μεγαλύτερα μοντέλα GGUF.
<!-- @device:end -->

## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->

## Προαπαιτούμενα

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas); host npm is only used by CI to resolve the MCP packages. -->
<!-- @prereq:docker,nodejs,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

Χρειάζεστε:

- Το Lemonade Server εγκατεστημένο ακολουθώντας τον τυπικό [οδηγό εγκατάστασης Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 ή νεότερο και `npm`, που χρησιμοποιούνται για την εγκατάσταση του δημοσιευμένου Agent Canvas CLI και την εκτέλεση διακομιστών MCP με `npx`.
- `uv`, τον διαχειριστή πακέτων Python που χρησιμοποιεί το Agent Canvas για να δημιουργήσει το περιβάλλον του Agent Server. Αν δεν είναι ήδη εγκατεστημένο, εγκαταστήστε το από τον [οδηγό εγκατάστασης uv](https://docs.astral.sh/uv/getting-started/installation/).
- Ένα πρόσφατο δημοσιευμένο πακέτο `@openhands/agent-canvas` με ρυθμίσεις πράκτορα βασισμένες σε σχήμα, `LLMSummarizingCondenserSettings.max_tokens`, και υποστήριξη `custom_tokenizer` για LLM.
- Το πακέτο Python `transformers` διαθέσιμο στο περιβάλλον του Agent Server. Απαιτείται για την καταμέτρηση tokens προτύπου συνομιλίας (chat-template) όταν έχει οριστεί το `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop για Windows](https://docs.docker.com/desktop/setup/install/windows-install/), εγκατεστημένο και σε λειτουργία. Στα Windows, η στοίβα Agent Canvas εκτελείται από τη δημοσιευμένη εικόνα Docker, η οποία περιλαμβάνει τα Node.js, `uv`, `transformers`, και το πακέτο `@openhands/agent-canvas`, οπότε δεν χρειάζεται να τα εγκαταστήσετε στον κεντρικό υπολογιστή (host).
<!-- @os:end -->

- Ένα token GitHub με δικαίωμα ανάγνωσης στο αποθετήριο που θέλετε να συνοψίσετε.
- Ένα token bot Slack (`xoxb-...`) με δικαιώματα `chat:write` και ανάγνωσης καναλιού.
- Ένα αναγνωριστικό ομάδας Slack (`T...`).
- Ένα αναγνωριστικό καναλιού Slack (`C...`) όπου θα αναρτηθεί η σύνοψη.

Προσκαλέστε την εφαρμογή Slack στο κανάλι προορισμού πριν δοκιμάσετε τον αυτοματισμό.
## Μεταβλητές που Χρησιμοποιούνται σε Αυτό το Playbook

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

Αυτές οι δύο μεταβλητές χρησιμοποιούνται από τις παρακάτω εντολές επαλήθευσης.
Το μοντέλο, ο tokenizer, και οι άλλες ρυθμίσεις LLM εισάγονται απευθείας στο UI του Agent Canvas σε επόμενα βήματα, οπότε οι κυριολεκτικές τιμές τους εμφανίζονται ενσωματωμένες όπου χρειάζεστε.

Οι ακόλουθες τιμές εισάγονται στο UI του Agent Canvas σε επόμενα βήματα.
Ορίστε τις εδώ ώστε να μπορείτε να τις αντιγράψετε:

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

Χρησιμοποιήστε μια ρητή τιμή `owner/repo` για το `GITHUB_REPO_FILTER`.
Ευρεία wildcards οργανισμού μπορεί να επιστρέψουν υπερβολικό MCP context για τα τοπικά μοντέλα.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Εκκίνηση του Lemonade Server

Ξεκινήστε το μοντέλο από το Lemonade CLI:

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **Επιλέξτε ένα μοντέλο που ταιριάζει στο υλικό σας.** Το `Qwen3.6-35B-A3B-GGUF` (~20 GB) είναι ένα ισχυρό μοντέλο για αυτή τη ροή εργασίας αλλά απαιτεί μεγάλο pool μνήμης.
> Αν η συσκευή σας έχει περιορισμένη μνήμη ή GPU VRAM, επιλέξτε ένα μικρότερο GGUF μοντέλο από τη βιβλιοθήκη μοντέλων Lemonade και χρησιμοποιήστε αυτό το model ID (και τον αντίστοιχο tokenizer) σε όλο αυτό το playbook.

> **Σημείωση:** Η πρώτη εκτέλεση `lemonade run` κατεβάζει το μοντέλο αν δεν υπάρχει ήδη, κάτι που μπορεί να πάρει αρκετή ώρα ανάλογα με το μέγεθος του μοντέλου και τη σύνδεσή σας.

Το Lemonade εκθέτει ένα συμβατό με OpenAI API στο:

```text
http://127.0.0.1:13305/api/v1
```

Προαιρετικά: αν το Agent Canvas ή ο automation runner δεν βρίσκονται στο ίδιο μηχάνημα, δημοσιεύστε το endpoint του Lemonade μέσω ενός ασφαλούς tunnel και χρησιμοποιήστε το HTTPS URL ως LLM base URL.
Το [ngrok](https://ngrok.com/) εκθέτει μια τοπική θύρα στο διαδίκτυο μέσω ενός ασφαλούς HTTPS URL· απαιτεί ένα δωρεάν λογαριασμό ngrok, και αντικαθιστάτε το `YOUR_NGROK_DOMAIN.ngrok-free.dev` με το δικό σας κρατημένο domain:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Επαλήθευση του Τοπικού Μοντέλου

Επιβεβαιώστε ότι το Lemonade μπορεί να εξυπηρετήσει το επιλεγμένο μοντέλο:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Στη συνέχεια στείλτε ένα μικρό αίτημα chat:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

Στη συνέχεια στείλτε ένα μικρό αίτημα chat:

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

Αν αυτό επιστρέψει έναν πίνακα `choices`, το Lemonade είναι έτοιμο για το Agent Canvas.

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
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 64
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
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

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. Εκκίνηση του Agent Canvas

<!-- @os:linux -->
Εγκαταστήστε το δημοσιευμένο πακέτο Agent Canvas και ξεκινήστε ολόκληρη τη στοίβα:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Αν η καθολική εγκατάσταση npm αποτύχει με σφάλμα δικαιωμάτων, δείτε την καταχώρηση αντιμετώπισης προβλημάτων δικαιωμάτων npm παρακάτω.

Από προεπιλογή, το Agent Canvas ξεκινά στο `http://localhost:8000`.
Ανοίξτε αυτό το URL στο πρόγραμμα περιήγησής σας.
Η θύρα δεν είναι ειδική—αν η 8000 χρησιμοποιείται ήδη, περάστε οποιαδήποτε ελεύθερη θύρα με `--port` (ή `-p`).
Το προεπιλεγμένο τοπικό backend θα πρέπει να εμφανίζεται ως υγιές στην αρχική οθόνη.

> **Σημείωση:** Η πρώτη εκκίνηση δημιουργεί το Python περιβάλλον του Agent Server διαχειριζόμενο από `uv`, οπότε μπορεί να χρειαστούν μερικά λεπτά πριν το backend αναφέρει ότι είναι υγιές.

Η εντολή `agent-canvas` ξεκινά μαζί τον agent server, το backend αυτοματισμού, και το web frontend.
Χρειάζεστε μόνο αυτή τη μία εντολή για να εκτελέσετε το OpenHands τοπικά.
Το υπόλοιπο αυτού του playbook ρυθμίζει τα πάντα μέσω του UI του Agent Canvas στο πρόγραμμα περιήγησής σας.
<!-- @os:end -->

<!-- @os:windows -->
Σε Windows, εκτελέστε τη δημοσιευμένη εικόνα container του Agent Canvas με το Docker Desktop.
Η εικόνα περιλαμβάνει τον Agent Server, το backend αυτοματισμού, και το web frontend, οπότε δεν χρειάζεται να εγκαταστήσετε Node.js, `uv`, ή το CLI στον host.

Πρώτα, δημιουργήστε τους φακέλους config και workspace που θα προσαρτήσει το container:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Κατεβάστε τη δημοσιευμένη εικόνα (περίπου 6 GB· είναι δημόσια, οπότε δεν απαιτείται σύνδεση):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Στη συνέχεια ξεκινήστε τη στοίβα:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Ανοίξτε το `http://localhost:8000/canvas` στο πρόγραμμα περιήγησής σας.
Αν η θύρα 8000 χρησιμοποιείται ήδη, αντιστοιχίστε μια διαφορετική θύρα host, για παράδειγμα `-p 8080:8000`, και ανοίξτε αντ' αυτού το `http://localhost:8080/canvas`.

> **Σημείωση:** Η πρώτη εκκίνηση δημιουργεί το περιβάλλον του Agent Server μέσα στο container, οπότε μπορεί να χρειαστούν μερικά λεπτά πριν το backend αναφέρει ότι είναι υγιές.

Η προσάρτηση `.openhands` διατηρεί το προφίλ LLM, τους servers MCP, και τους αυτοματισμούς σας μεταξύ επανεκκινήσεων του container.
Το υπόλοιπο αυτού του playbook ρυθμίζει τα πάντα μέσω του UI του Agent Canvas στο πρόγραμμα περιήγησής σας στο `http://localhost:8000/canvas`.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
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
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
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
## 4. Διαμόρφωση του τοπικού LLM στο UI

Με την πρώτη εκκίνηση, το Agent Canvas ανοίγει μια ροή onboarding.
Σε αυτή τη ροή:

1. Διατηρήστε επιλεγμένο το **OpenHands** ως agent και κάντε κλικ στο **Next**.
2. Στο **Set up your LLM**, επιλέξτε **Advanced**.
3. Διατηρήστε το **Authentication** ρυθμισμένο σε **API key**.
4. Ορίστε το **Custom Model** σε `openai/Qwen3.6-35B-A3B-GGUF`.
5. Ορίστε το **Base URL** σε `http://127.0.0.1:13305/api/v1`.
6. Για το **API Key**, εισαγάγετε οποιαδήποτε μη κενή τιμή-δεσμευτική θέσης, όπως `lemonade-local`. Το Lemonade δεν απαιτεί πραγματικό κλειδί, αλλά ο πελάτης OpenHands χρειάζεται μια τιμή για να στείλει.

<!-- @os:windows -->
> **Windows (Docker):** ο Agent Server εκτελείται μέσα στο container, επομένως ορίστε το **Base URL** σε `http://host.docker.internal:13305/api/v1` αντί για `http://127.0.0.1:13305/api/v1`.
> Από μέσα στο container, το `127.0.0.1` είναι το ίδιο το container· το `host.docker.internal` προσεγγίζει το Lemonade που εκτελείται στον Windows host, και το Docker Desktop παρέχει αυτό το hostname αυτόματα.
<!-- @os:end -->

Τα πεδία σύνδεσης θα πρέπει να μοιάζουν ως εξής.
Το πεδίο API key είναι καλυμμένο από το UI.

![Αρχικές ρυθμίσεις LLM Advanced του Agent Canvas με το μοντέλο Lemonade και το τοπικό base URL](assets/01-llm-advanced-settings.png)

Στη συνέχεια επιλέξτε **All** και ορίστε τα επιπλέον πεδία τοπικού μοντέλου:

1. Μεταβείτε στο **Custom Tokenizer** και ορίστε το σε `Qwen/Qwen3.6-35B-A3B`.
2. Μεταβείτε στο **LiteLLM Extra Body** και ορίστε το σε `{"enable_thinking": true}`.
3. Κάντε κλικ στο **Next**.

![Καρτέλα LLM All του Agent Canvas με τον προσαρμοσμένο tokenizer Qwen](assets/02-llm-all-tokenizer-settings.png)

![Καρτέλα LLM All του Agent Canvas με διαμορφωμένο το LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Οι ρυθμίσεις LLM θα πρέπει να εμφανίζουν:

| Πεδίο | Τιμή |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Το πρόθεμα `openai/` ενημερώνει το LiteLLM να χρησιμοποιήσει μορφοποίηση αιτημάτων συμβατή με OpenAI έναντι του endpoint Lemonade.
Ο προσαρμοσμένος tokenizer είναι ο αρχικός tokenizer Hugging Face για το μοντέλο GGUF· επιτρέπει στο OpenHands να μετρά τα ίδια tokens chat-template που βλέπει ο τοπικός διακομιστής μοντέλου.
Η τρέχουσα φόρμα πρώτης χρήσης LLM δεν εμφανίζει ρυθμίσεις condenser.
Εάν η έκδοση του Agent Canvas σας εμφανίσει αργότερα ρυθμίσεις condenser κάτω από το **Settings > LLM**, χρησιμοποιήστε το `llm_summarizing` και ορίστε max tokens κάτω από το παράθυρο context του Lemonade, όπως `56000`.

## 5. Εγκατάσταση MCP Servers για GitHub και Slack

Στο UI του Agent Canvas, ανοίξτε το **Customize** (ή **Settings > MCP**) για να προσθέσετε τους MCP servers που δίνουν στον agent εργαλεία για GitHub και Slack.
Οι τιμές token αποστέλλονται μόνο στον τοπικό σας Agent Server και διατηρούνται ως κρυπτογραφημένες ρυθμίσεις.

<!-- @os:windows -->
> **Windows (Docker):** οι παρακάτω εντολές MCP server `npx` εκτελούνται μέσα στο container, το οποίο ήδη περιλαμβάνει το Node.js, επομένως δεν εγκαθίσταται τίποτα επιπλέον στον host.
> Επειδή το `.openhands` είναι mounted, οι MCP servers και τα tokens τους διατηρούνται μεταξύ επανεκκινήσεων του container.
<!-- @os:end -->

### GitHub MCP server

Προσθέστε έναν νέο MCP server με αυτές τις ρυθμίσεις:

| Πεδίο | Τιμή |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = το GitHub token σας |

Χρησιμοποιήστε ένα GitHub token με δικαιώματα ανάγνωσης στο repository που θέλετε να συνοψιστεί.

### Slack MCP server

Προσθέστε έναν δεύτερο MCP server με αυτές τις ρυθμίσεις:

| Πεδίο | Τιμή |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = το ID του καναλιού digest σας |

Ορίστε το `SLACK_CHANNEL_IDS` στο ID του καναλιού digest (την ίδια τιμή με το `SLACK_DIGEST_CHANNEL`), ώστε ο agent να μη χρειάζεται να σαρώνει κάθε κανάλι Slack.

Αφού προσθέσετε και τους δύο servers, χρησιμοποιήστε το κουμπί **Test** σε κάθε έναν για να επιβεβαιώσετε ότι συνδέεται και διαφημίζει εργαλεία.
Ο server GitHub θα πρέπει να εμφανίζει εργαλεία GitHub, και ο server Slack θα πρέπει να εμφανίζει εργαλεία Slack.

![Σελίδα MCP του Agent Canvas με εγκατεστημένους τους servers GitHub και Slack](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Δημιουργία του Digest Automation

Στο UI του Agent Canvas, ανοίξτε τη σελίδα **Automations** και δημιουργήστε ένα νέο automation:

1. Επιλέξτε **Create automation** και επιλέξτε τον τύπο **Prompt preset**.
2. Ορίστε το **Name** σε `GitHub Development Digest to Slack`.
3. Ορίστε το **Prompt** στο ακόλουθο κείμενο, αντικαθιστώντας τα placeholders repository και channel με τις δικές σας τιμές:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. Ορίστε το **Trigger** σε **Cron** με πρόγραμμα `0 9 * * 1-5` (9 π.μ. τις καθημερινές) και ορίστε το **Timezone** στη δική σας ζώνη ώρας, για παράδειγμα `America/New_York`.
5. Ορίστε το **Timeout** σε `900` δευτερόλεπτα.
6. Αποθηκεύστε το automation.

Η σελίδα λεπτομερειών automation εμφανίζει το νέο automation με το cron trigger του και το παραγόμενο entrypoint prompt-preset.

![Λεπτομέρειες automation του Agent Canvas μετά τη δημιουργία](assets/05-automation-created.png)
## 7. Δοκιμή της Αυτοματοποίησης

Από τη σελίδα λεπτομερειών της αυτοματοποίησης στο Agent Canvas UI:

1. Κάντε κλικ στο **Run now** (ή **Dispatch**) για να εκτελέσετε την αυτοματοποίηση μία φορά άμεσα.
2. Παρακολουθήστε τη λίστα εκτελέσεων στην ίδια σελίδα. Η πιο πρόσφατη εκτέλεση θα πρέπει να μεταβεί στην κατάσταση `COMPLETED`.
3. Ανοίξτε το κανάλι Slack προορισμού σας. Θα πρέπει να περιέχει το δημιουργημένο digest.

Δεν χρειάζεται να περιμένετε την ενεργοποίηση του προγραμματισμού cron—το **Run now** ενεργοποιεί μια εκτέλεση κατ' απαίτηση ώστε να μπορείτε να επιβεβαιώσετε ότι η προτροπή, οι συνδέσεις MCP και η δημοσίευση στο Slack λειτουργούν όλα σωστά πριν βασιστείτε στο πρόγραμμα.

![Η εκτέλεση αυτοματοποίησης στο Agent Canvas ολοκληρώθηκε με επιτυχία](assets/06-automation-run-completed.png)

![Κανάλι Slack που εμφανίζει το δημιουργημένο digest OpenHands](assets/07-slackbot-message.png)

## Αντιμετώπιση προβλημάτων

<!-- @os:windows -->
- **Η θύρα 8000 του Docker χρησιμοποιείται ήδη:** αντιστοιχίστε μια διαφορετική θύρα κεντρικού υπολογιστή, για παράδειγμα `docker run ... -p 8080:8000 ...`, και ανοίξτε το `http://localhost:8080/canvas`.
- **Η εντολή `docker pull` αποτυγχάνει με σφάλμα διαπιστευτηρίων** (για παράδειγμα, "A specified logon session does not exist"): εκτελέστε το pull από μια διαδραστική συνεδρία Windows, ή κάντε προκαταβολικό pull της εικόνας. Η εικόνα είναι δημόσια, οπότε δεν απαιτείται `docker login`.
- **Το UI φορτώνει αλλά το backend δεν είναι υγιές:** η πρώτη εκκίνηση δημιουργεί το περιβάλλον Agent Server μέσα στο container. Περιμένετε ένα λεπτό και ανανεώστε, στη συνέχεια ελέγξτε το `docker logs <container>` για πρόοδο.
- **Το Agent Canvas δεν μπορεί να προσεγγίσει το Lemonade από το container:** ορίστε το **Base URL** του LLM σε `http://host.docker.internal:13305/api/v1` (όχι `127.0.0.1`), και επιβεβαιώστε ότι το Lemonade εκτελείται στον κεντρικό υπολογιστή Windows.
<!-- @os:end -->

- **Το Lemonade είναι εκτός λειτουργίας:** επανεκκινήστε το με την εντολή `lemonade run "${LEMONADE_MODEL}"` στο βήμα 1, στη συνέχεια εκτελέστε ξανά τον έλεγχο υγείας.
- **Η εντολή `npm install -g` αποτυγχάνει με σφάλμα δικαιωμάτων:** σε Linux ή WSL, διαμορφώστε έναν καθολικό κατάλογο npm που ανήκει στον χρήστη, προσθέστε τον στο αρχείο εκκίνησης του shell σας, στη συνέχεια εγκαταστήστε ξανά το Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Αν χρησιμοποιείτε `zsh`, προσθέστε την ίδια γραμμή `export PATH=...` στο `~/.zshrc` αντί για το `~/.bashrc`.
- **Το Agent Canvas απορρίπτει τις ρυθμίσεις LLM μετά τον ορισμό του `custom_tokenizer`:** εγκαταστήστε το `transformers` στο περιβάλλον Python του Agent Server, επανεκκινήστε το Agent Canvas εάν χρειάζεται, και προσπαθήστε ξανά να αποθηκεύσετε τις ρυθμίσεις LLM. Το OpenHands απαιτεί το Transformers για να φορτώσει το πρότυπο συνομιλίας (chat template) του tokenizer όταν έχει οριστεί το `custom_tokenizer`.
- **Το Agent Canvas δεν μπορεί να προσεγγίσει το Lemonade:** επαληθεύστε με `curl -fsS "${LEMONADE_BASE_URL}/health"` και επιβεβαιώστε ότι το base URL που έχει εισαχθεί στη φόρμα LLM πρώτης χρήσης ή στο **Settings > LLM** αντιστοιχεί στο τρέχον τοπικό endpoint ή στο HTTPS tunnel.
- **Οι ρυθμίσεις LLM δεν αποθηκεύτηκαν:** βεβαιωθείτε ότι κάνατε κλικ στο **Next** μετά την εισαγωγή των τιμών. Ανοίξτε ξανά το **Settings > LLM** για να επιβεβαιώσετε ότι οι τιμές διατηρήθηκαν.
- **Το GitHub MCP δεν μπορεί να δει ιδιωτικά αποθετήρια:** επιβεβαιώστε ότι το token του GitHub έχει δικαιώματα ανάγνωσης στο αποθετήριο προορισμού και ότι το κουμπί **Test** του MCP στο **Customize** εμφανίζει τα εργαλεία GitHub.
- **Το Slack μπορεί να διαβάζει κανάλια αλλά δεν μπορεί να δημοσιεύσει:** προσκαλέστε την εφαρμογή Slack στο κανάλι προορισμού και επιβεβαιώστε ότι το bot διαθέτει το δικαίωμα `chat:write`.
- **Η αυτοματοποίηση εμφανίζει πάρα πολλά κανάλια Slack:** χρησιμοποιήστε ένα αναγνωριστικό καναλιού Slack (channel ID) και ορίστε το `SLACK_CHANNEL_IDS` στον διακομιστή Slack MCP στο **Customize**.
- **Η εκτέλεση της αυτοματοποίησης αποτυγχάνει ή υπερβαίνει τα όρια context:** επιβεβαιώστε ότι το Lemonade εκκινήθηκε με `ctx_size=65536`, επιβεβαιώστε ότι το LLM του OpenHands έχει ορισμένο το `custom_tokenizer`, και χρησιμοποιήστε ένα ρητά καθορισμένο αποθετήριο με τα σύνολα αποτελεσμάτων GitHub περιορισμένα σε 3 έως 5 στοιχεία. Αν η έκδοση του Agent Canvas που χρησιμοποιείτε εκθέτει ρυθμίσεις condenser, ορίστε το μέγιστο αριθμό tokens του condenser κάτω από το παράθυρο context του Lemonade.

## Επόμενα Βήματα

- Προσθέστε ένα εβδομαδιαίο digest μόνο για εκδόσεις (release-only).
- Προσθέστε μια αυτοματοποίηση που ενεργοποιείται από συμβάντα GitHub για ταχύτερες ειδοποιήσεις PR ή push.
- Δρομολογήστε το ίδιο digest σε Notion, Linear, ή κάποιο άλλο εργαλείο βασισμένο σε MCP.

## Πόροι

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Τεκμηρίωση Lemonade Server](https://lemonade-server.ai/docs)
- [Αποθετήριο επεκτάσεων OpenHands](https://github.com/OpenHands/extensions)
- [Διακομιστές Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Πακέτο Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->