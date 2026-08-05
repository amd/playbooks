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

Το Ollama είναι ένα δημοφιλές, ελαφρύ εργαλείο για την τοπική εκτέλεση μεγάλων γλωσσικών μοντέλων. Διαχειρίζεται τη λήψη μοντέλων, την κβαντοποίηση και την εξυπηρέτηση πίσω από μια απλή διεπαφή γραμμής εντολών και εφαρμογή desktop, ώστε να μπορείτε να ξεκινήσετε να συνομιλείτε με ένα LLM μέσα σε λίγα λεπτά.

Αυτό το playbook σας καθοδηγεί στην εγκατάσταση του Ollama, στη λήψη του μοντέλου GPT-OSS 20B και στην πραγματοποίηση μιας συνομιλίας μαζί του, τόσο μέσω του τερματικού όσο και μέσω της εφαρμογής desktop.

## Τι θα μάθετε

- Πώς να εγκαταστήσετε και να εκκινήσετε το Ollama στο σύστημά σας
- Λήψη και εκτέλεση του μοντέλου GPT-OSS 20B τοπικά
- Συνομιλία με μοντέλα χρησιμοποιώντας το CLI
- Ερώτημα σε μοντέλα προγραμματιστικά μέσω του REST API

## Ρύθμιση Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού
> **Σημείωση**: Αν το VS Code δεν είναι εγκατεστημένο, μπορείτε να το εγκαταστήσετε με το Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενων Λογισμικού

<!-- @require:driver -->

### Εγκατάσταση του Ollama

<!-- @os:windows -->

1. Κατεβάστε τον εγκαταστάτη από το [ollama.com/download](https://ollama.com/download).
2. Εκτελέστε τον εγκαταστάτη `.exe` και ακολουθήστε τις οδηγίες.
3. Μόλις εγκατασταθεί, το Ollama εκτελείται ως υπηρεσία παρασκηνίου και είναι προσβάσιμο από το τερματικό, την εφαρμογή desktop και τη γραμμή συστήματος (system tray).

Επαληθεύστε την εγκατάσταση ανοίγοντας ένα τερματικό και εκτελώντας:

```powershell
ollama --version
```

<!-- @test:id=ollama-version-windows timeout=60 hidden=True -->
```powershell
ollama --version
```
<!-- @test:end --> 

Θα πρέπει να δείτε τον αριθμό της εγκατεστημένης έκδοσης να εκτυπώνεται στην κονσόλα.
<!-- @os:end -->

<!-- @os:linux -->

Εκτελέστε το επίσημο σενάριο εγκατάστασης:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Επαληθεύστε την εγκατάσταση:

```bash
ollama --version
```

<!-- @test:id=ollama-version-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end --> 

Θα πρέπει να δείτε τον αριθμό της εγκατεστημένης έκδοσης να εκτυπώνεται στην κονσόλα.
<!-- @os:end -->

## Λήψη του Πρώτου σας Μοντέλου

Το Ollama διαχειρίζεται τα μοντέλα μέσω ενός μητρώου παρόμοιου με τις εικόνες container. Για να κατεβάσετε το GPT-OSS 20B:

```bash
ollama pull gpt-oss:20b
```

Αυτό κατεβάζει τα βάρη του μοντέλου στον τοπικό σας υπολογιστή (περίπου 12 GB). Η λήψη γίνεται μόνο μία φορά και οι επόμενες εκτελέσεις φορτώνουν το μοντέλο από τον δίσκο.

Μπορείτε να επιβεβαιώσετε ότι το μοντέλο είναι διαθέσιμο με:

```bash
ollama list
```

Θα πρέπει να δείτε το `gpt-oss:20b` στην έξοδο μαζί με το μέγεθός του και την ημερομηνία τελευταίας τροποποίησης.

<!-- @os:windows -->
<!-- @test:id=ollama-list-gpt-oss-20b-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
$list = (ollama list | Out-String)
if (-not $list) { throw "ollama list returned no output" }
if ($list -notmatch 'gpt-oss:20b') { throw "Model gpt-oss:20b is not present in ollama list. Please download it before running this test." }
Write-Host "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-list-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"

cleanup() {
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-list-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

list="$(ollama list)"
if [ -z "$list" ]; then
  echo "ollama list returned no output"
  exit 1
fi
echo "$list" | grep -q 'gpt-oss:20b' || {
  echo "Model gpt-oss:20b is not present in ollama list. Please download it before running this test."
  exit 1
}
echo "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

### Ονοματολογία Μοντέλων

Τα ονόματα μοντέλων του Ollama ακολουθούν τη μορφή `name:tag`. Η ετικέτα (tag) συνήθως υποδεικνύει τον αριθμό παραμέτρων ή την παραλλαγή κβαντοποίησης. Ορισμένες χρήσιμες εντολές για τη διαχείριση μοντέλων:

| Εντολή | Περιγραφή |
|---------|-------------|
| `ollama list` | Εμφάνιση όλων των μοντέλων που έχουν ληφθεί |
| `ollama pull <model>` | Λήψη ενός μοντέλου χωρίς εκτέλεσή του |
| `ollama rm <model>` | Αφαίρεση ενός μοντέλου για απελευθέρωση χώρου στον δίσκο |
| `ollama show <model>` | Εμφάνιση μεταδεδομένων και παραμέτρων μοντέλου |

## Συνομιλία από το Τερματικό

Ξεκινήστε μια διαδραστική συνεδρία συνομιλίας απευθείας από τη γραμμή εντολών:

```bash
ollama run gpt-oss:20b
```

Το Ollama φορτώνει το μοντέλο στη μνήμη και σας μεταφέρει σε ένα prompt. Δοκιμάστε να ρωτήσετε κάτι:

```
>>> What is the capital of France and why is it historically significant?
```

Το μοντέλο ρέει (streams) την απάντησή του token προς token απευθείας στο τερματικό. Πληκτρολογήστε `/bye` ή πατήστε `Ctrl+D` για να τερματίσετε τη συνεδρία.

> **Συμβουλή**: Η πρώτη εκτέλεση χρειάζεται λίγα δευτερόλεπτα για να φορτώσει το μοντέλο στη μνήμη. Τα επόμενα prompts μέσα στην ίδια συνεδρία ανταποκρίνονται πολύ πιο γρήγορα, καθώς το μοντέλο παραμένει φορτωμένο.

<!-- @os:windows -->
## Συνομιλία από την Εφαρμογή Desktop

Το Ollama διατίθεται επίσης με μια εφαρμογή desktop που παρέχει μια καθαρή διεπαφή συνομιλίας για την αλληλεπίδραση με τα μοντέλα σας.

Ανοίξτε το **Ollama** από το μενού Έναρξη ή κάντε κλικ στο εικονίδιο του Ollama στη γραμμή συστήματος (system tray) και επιλέξτε **Open Ollama**.

Μόλις ανοίξει η εφαρμογή:

1. Κάντε κλικ στο **New Chat** στην πλαϊνή στήλη.
2. Επιλέξτε **gpt-oss:20b** από το αναπτυσσόμενο μενού μοντέλων στην κάτω-δεξιά γωνία της περιοχής εισαγωγής συνομιλίας.
3. Πληκτρολογήστε ένα μήνυμα και πατήστε Enter για να ξεκινήσετε τη συνομιλία.

<p align="center">
  <img src="assets/ollama_app.png" alt="Ollama desktop app chatting with gpt-oss:20b" width="600"/>
</p>

Η εφαρμογή desktop διατηρεί ένα ιστορικό των συνομιλιών σας στην πλαϊνή στήλη, διευκολύνοντας την επανεξέταση προηγούμενων συνομιλιών.
<!-- @os:end -->

## Χρήση του REST API

Μετά την εγκατάσταση, το Ollama εκτελείται ως υπηρεσία παρασκηνίου και εκθέτει ένα REST API στη διεύθυνση `http://localhost:11434` που μπορείτε να χρησιμοποιήσετε για να ενσωματώσετε μοντέλα στις δικές σας εφαρμογές και σενάρια.

<!-- @os:windows -->
<!-- @test:id=ollama-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$p = $null
$startedHere = $false
$tmpShow = $null
$tmpGenerate = $null
$tmpChat = $null
$venv = "$PWD\ollama-env-ci"
$pythonSmoke = "$PWD\ollama_python_smoke.py" 

function Wait-OllamaApi {
  param( [int]$MaxAttempts = 120 )
  $resp = $null
  for ($i = 0; $i -lt $MaxAttempts; $i++) {
    $resp = curl.exe -s --max-time 2 http://127.0.0.1:11434/api/tags
    if ($LASTEXITCODE -eq 0 -and $resp) { return $resp }
    Start-Sleep -Seconds 1
  }
  return $null
}

try {
  # If Ollama API is not already up, start it.
  $tagsJson = Wait-OllamaApi -MaxAttempts 5
  if (-not $tagsJson) {
    $p = Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow -PassThru
    $startedHere = $true
    $tagsJson = Wait-OllamaApi -MaxAttempts 120
  }
  if (-not $tagsJson) { throw "Ollama API not ready on http://127.0.0.1:11434" }
  Write-Host "OK: Ollama API is responding on http://127.0.0.1:11434"

  # /api/tags must include gpt-oss:20b
  $tags = $tagsJson | ConvertFrom-Json
  $model = $tags.models | Where-Object { $_.name -eq "gpt-oss:20b" } | Select-Object -First 1
  if (-not $model) { throw "Model gpt-oss:20b is not present in /api/tags. Please download it before running this test." }
  Write-Host "OK: gpt-oss:20b is present in /api/tags"

  # /api/show should return model metadata
  $showBody = @{ name = "gpt-oss:20b" } | ConvertTo-Json
  $tmpShow = Join-Path $env:TEMP "ollama-show-body.json"
  [System.IO.File]::WriteAllText($tmpShow, $showBody, [System.Text.UTF8Encoding]::new($false))
  $showOut = curl.exe -sS --fail-with-body --max-time 60 http://127.0.0.1:11434/api/show `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpShow"
  if (-not $showOut) { throw "Empty response from /api/show" }
  $showJson = $showOut | ConvertFrom-Json
  if (-not $showJson.details) { throw "/api/show did not return model details for gpt-oss:20b" }
  Write-Host "OK: /api/show returned model details"

  # CLI inference smoke
  $cliOut = & ollama run gpt-oss:20b "Reply with exactly OK"
  if (-not $cliOut) { throw "ollama run returned empty output" }
  $cliText = ($cliOut | Out-String).Trim()
  if ($cliText -notmatch '(^|\s)OK(\s|$)') { throw "ollama run did not return OK. Output was: $cliText" }
  Write-Host "OK: ollama run inference works"

  # /api/generate smoke
  $generateBody = @{
    model  = "gpt-oss:20b"
    prompt = "Reply with exactly OK"
    stream = $false
  } | ConvertTo-Json
  $tmpGenerate = Join-Path $env:TEMP "ollama-generate-body.json"
  [System.IO.File]::WriteAllText($tmpGenerate, $generateBody, [System.Text.UTF8Encoding]::new($false))
  $generateOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/generate `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpGenerate"
  if (-not $generateOut) { throw "Empty response from /api/generate" }
  $generateJson = $generateOut | ConvertFrom-Json
  if (-not $generateJson.response) { throw "/api/generate did not return a response field" }
  if ($generateJson.response.Trim() -ne "OK") { throw "/api/generate expected exactly OK but got: $($generateJson.response)" }
  Write-Host "OK: /api/generate works"

  # /api/chat smoke
  $chatBody = @{
    model = "gpt-oss:20b"
    messages = @(
      @{
        role = "user"
        content = "Reply with exactly OK"
      }
    )
    stream = $false
  } | ConvertTo-Json -Depth 5
  $tmpChat = Join-Path $env:TEMP "ollama-chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/chat `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from /api/chat" }
  $chatJson = $chatOut | ConvertFrom-Json
  $chatText = $chatJson.message.content
  if (-not $chatText) { throw "/api/chat did not return message.content" }
  if ($chatText.Trim() -ne "OK") { throw "/api/chat expected exactly OK but got: $chatText" }
  Write-Host "OK: /api/chat works"

  # Python requests smoke
  if (Test-Path $venv) { Remove-Item -Recurse -Force $venv }
  python -m venv $venv
  $py = Join-Path $venv "Scripts\python.exe"
  & $py -m pip install --upgrade pip
  & $py -m pip install requests
@'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
'@ | Set-Content -Path $pythonSmoke -Encoding UTF8
  & $py $pythonSmoke
}

finally {
  Remove-Item $tmpShow, $tmpGenerate, $tmpChat, $pythonSmoke -Force -ErrorAction SilentlyContinue
  Remove-Item $venv -Recurse -Force -ErrorAction SilentlyContinue
  if ($startedHere) {
    if ($p -and -not $p.HasExited) {
      Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
  }
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-smoke-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"
venv="./ollama-env-ci"
python_smoke="./ollama_python_smoke.py" 

cleanup() {
  rm -f "$python_smoke"
  rm -rf "$venv"
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

export TAGS_JSON="$tags_json"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["TAGS_JSON"])
models = data.get("models", [])
for item in models:
    if item.get("name") == "gpt-oss:20b":
        print("OK: gpt-oss:20b is present in /api/tags")
        sys.exit(0)
print("Model gpt-oss:20b is not present in /api/tags. Please download it before running this test.")
sys.exit(1)
PY

show_out="$(curl -s --max-time 60 http://127.0.0.1:11434/api/show \
  -H "Content-Type: application/json" \
  -d '{"name":"gpt-oss:20b"}' || true)"
if [ -z "$show_out" ]; then
  echo "Empty response from /api/show"
  exit 1
fi
export SHOW_OUT="$show_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["SHOW_OUT"])
if not data.get("details"):
    print("/api/show did not return model details for gpt-oss:20b")
    sys.exit(1)
print("OK: /api/show returned model details")
PY

cli_out="$(ollama run gpt-oss:20b "Reply with exactly OK" || true)"
if [ -z "$cli_out" ]; then
  echo "ollama run returned empty output"
  exit 1
fi
export CLI_OUT="$cli_out"
python3 - <<'PY'
import os
import sys
text = os.environ["CLI_OUT"].strip()
if "OK" not in text.split():
    print(f"ollama run did not return OK. Output was: {text}")
    sys.exit(1)
print("OK: ollama run inference works")
PY

generate_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","prompt":"Reply with exactly OK","stream":false}' || true)"
if [ -z "$generate_out" ]; then
  echo "Empty response from /api/generate"
  exit 1
fi
export GENERATE_OUT="$generate_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["GENERATE_OUT"])
text = data.get("response", "")
if not text:
    print("/api/generate did not return a response field")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/generate expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/generate works")
PY

chat_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","messages":[{"role":"user","content":"Reply with exactly OK"}],"stream":false}' || true)"
if [ -z "$chat_out" ]; then
  echo "Empty response from /api/chat"
  exit 1
fi
export CHAT_OUT="$chat_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["CHAT_OUT"])
msg = data.get("message", {})
text = msg.get("content", "")
if not text:
    print("/api/chat did not return message.content")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/chat expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/chat works")
PY

rm -rf "$venv"
python3 -m venv "$venv"
py="$venv/bin/python"
"$py" -m pip install --upgrade pip
"$py" -m pip install requests
cat > "$python_smoke" <<'PY'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
PY
"$py" "$python_smoke"
```
<!-- @test:end --> 
<!-- @os:end -->

### Δημιουργία Απάντησης στο Τερματικό

<!-- @os:linux -->
```bash
curl http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

Η απάντηση είναι ένα αντικείμενο JSON που περιέχει την έξοδο του μοντέλου στο πεδίο `response`.


### Παράδειγμα Python
Τώρα που μπορούμε να καλέσουμε το API του Ollama προγραμματιστικά, ας το καλέσουμε από την Python.

#### Δημιουργία Εικονικού Περιβάλλοντος στο Τερματικό

<!-- @os:linux -->
```bash
sudo apt install -y python3-venv
python3 -m venv ollama-env
source ollama-env/bin/activate
pip install requests
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
python -m venv ollama-env
ollama-env\Scripts\activate
pip install requests
```
<!-- @os:end -->
#### Δημιουργία Αρχείου Python
Στον ίδιο κατάλογο, χρησιμοποιήστε το VS Code ή έναν άλλο επεξεργαστή για να δημιουργήσετε ένα αρχείο .py και αντιγράψτε τον παρακάτω κώδικα σε αυτό. Στη συνέχεια, εκτελέστε το αρχείο στο ενεργοποιημένο περιβάλλον σας με `python your_file_name.py`

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Write a haiku about local AI inference.",
        "stream": False,
    },
)

print(response.json()["response"])
```

### Βασικά Endpoints του API

| Endpoint | Μέθοδος | Σκοπός |
|----------|--------|---------|
| `/api/generate` | POST | Δημιουργία κειμένου ενός γύρου (single-turn) |
| `/api/chat` | POST | Πολυγυριστή συνομιλία με ιστορικό μηνυμάτων |
| `/api/tags` | GET | Εμφάνιση διαθέσιμων μοντέλων |
| `/api/show` | POST | Εμφάνιση λεπτομερειών μοντέλου |
| `/api/pull` | POST | Λήψη ενός μοντέλου από το μητρώο |

Για την πλήρη τεκμηρίωση του API, δείτε την [τεκμηρίωση του Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md).
## Επόμενα Βήματα

- **Δοκιμάστε διαφορετικά μοντέλα**: Περιηγηθείτε στη [βιβλιοθήκη μοντέλων Ollama](https://ollama.com/library) για να εξερευνήσετε εκατοντάδες διαθέσιμα μοντέλα, από μικρούς βοηθούς κωδικοποίησης έως μεγάλα μοντέλα συλλογιστικής.
- **Δημιουργήστε προσαρμοσμένα μοντέλα**: Χρησιμοποιήστε ένα [Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) για να ορίσετε προσαρμοσμένα system prompts, temperature και άλλες παραμέτρους για μια εξατομικευμένη εμπειρία.
- **Δημιουργήστε εφαρμογές με το API**: Χρησιμοποιήστε τις βιβλιοθήκες πελάτη [Python](https://github.com/ollama/ollama-python) ή [JavaScript](https://github.com/ollama/ollama-js) για να ενσωματώσετε το Ollama στις εφαρμογές σας.
- **Συνδεθείτε με frontends**: Συνδυάστε το Ollama με εργαλεία όπως το [Open WebUI](https://github.com/open-webui/open-webui) για μια πλούσια σε λειτουργίες διεπαφή συνομιλίας με αναζήτηση, personas και μεταφόρτωση εγγράφων.

Για περισσότερες πληροφορίες, ανατρέξτε στην [τεκμηρίωση του Ollama](https://github.com/ollama/ollama/blob/main/README.md).