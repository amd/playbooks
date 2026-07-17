<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Αυτό το playbook χρησιμοποιεί ειδικές ετικέτες που το GitHub δεν μπορεί να αποδώσει. Επισκεφθείτε το [amd.com/playbooks](https://amd.com/playbooks) για να προβάλετε σωστά αυτό το περιεχόμενο.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Αυτό το playbook απαιτεί ελάχιστα **32GB** μνήμης συστήματος.
<!-- @device:end -->

## Επισκόπηση

Το [Open WebUI](https://docs.openwebui.com) είναι μια αυτο-φιλοξενούμενη, διαδικτυακή διεπαφή που παρέχει μια οικεία εμπειρία chatbot, ενώ λειτουργεί ως frontend για έναν ή περισσότερους διακομιστές μοντέλων AI. Αντί να είστε δεσμευμένοι σε έναν πάροχο, το Open WebUI μπορεί να συνδεθεί με **οποιοδήποτε backend που εκθέτει ένα API συμβατό με OpenAI**, ώστε να μπορείτε να αλλάζετε μοντέλα και δυνατότητες χωρίς να αλλάζετε διεπαφή.

Σε αυτό το playbook, χρησιμοποιούμε το [**Lemonade**](https://lemonade-server.ai) ως backend επειδή εκθέτει ένα **ενοποιημένο endpoint συμβατό με OpenAI** που υποστηρίζει πολλαπλές λειτουργίες:
- **Μεγάλα Γλωσσικά Μοντέλα (LLMs)** για δημιουργία κειμένου
- **Μοντέλα όρασης** για κατανόηση εικόνας
- **Stable Diffusion** για δημιουργία εικόνας
- **Μοντέλα μεταγραφής ήχου** για μετατροπή ομιλίας σε κείμενο

Αυτή η ρύθμιση σάς επιτρέπει να εξερευνήσετε την **πλήρη πολυτροπική ροή εργασίας από άκρο σε άκρο**.

---

## Τι Θα Μάθετε

Στο τέλος, θα μπορείτε να:

- Συνδέσετε το Open WebUI σε ένα τοπικό backend συμβατό με OpenAI (Lemonade)
- Συνομιλείτε με ένα τοπικό LLM από το πρόγραμμα περιήγησής σας
- Ανεβάζετε μια εικόνα και κάνετε ερωτήσεις σε ένα μοντέλο όρασης σχετικά με αυτήν
- Δημιουργείτε εικόνες από προτροπές κειμένου χρησιμοποιώντας μοντέλα Stable Diffusion (SDXL-Turbo / SDXL)
- Κατανοείτε το νοητικό μοντέλο ώστε να μπορείτε να χρησιμοποιείτε άλλα backends (Ollama, vLLM, llama.cpp server, κ.λπ.)

---

## Βασικές Έννοιες (Νοητικό Μοντέλο)

### Τα Τρία Συστατικά

| Τμήμα | Τι κάνει | Παραδείγματα |
|---|---|---|
| Frontend (UI) | Η διαδικτυακή εφαρμογή με την οποία αλληλεπιδράτε | Open WebUI |
| Backend (Διακομιστής Μοντέλων) | Φιλοξενεί μοντέλα και εκθέτει HTTP endpoints | Lemonade, Ollama, vLLM, llama.cpp server, διακομιστές συμβατοί με OpenAI |
| Μοντέλα | Τα πραγματικά μοντέλα LLM / Όρασης / Diffusion / Ήχου | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Γιατί έχει σημασία το «API συμβατό με OpenAI»

Το Open WebUI είναι χτισμένο γύρω από τυπικά endpoints στυλ OpenAI, όπως:
  - Συνομιλία: `/chat/completions`
  - Λίστα μοντέλων: `/models`
  - Δημιουργία εικόνας: `/images/generations`
  - Μεταγραφή ήχου: `/audio/transcriptions`

Το Lemonade εκθέτει αυτά στο `http://localhost:13305/api/v1/...`

Εάν ένα backend υποστηρίζει αυτά τα endpoints, το Open WebUI μπορεί να επικοινωνήσει μαζί του με ελάχιστη ρύθμιση. Γι' αυτό μπορούμε να αλλάζουμε backends χωρίς να αλλάζουμε τη ροή εργασίας μας.

#### Δύο υπηρεσίες, δύο θύρες

Κατά τη διάρκεια αυτού του playbook θα εργαστείτε με δύο ξεχωριστές υπηρεσίες:

| Υπηρεσία | URL | Τι κάνετε εκεί |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Περιήγηση, λήψη και διαχείριση μοντέλων |
| **Open WebUI** | `http://localhost:8080` | Συνομιλία, ανέβασμα εικόνων, δημιουργία εικόνων — η διεπαφή χρήστη |

Το Lemonade εκτελεί τα μοντέλα· το Open WebUI είναι η διεπαφή με την οποία αλληλεπιδράτε. Χρησιμοποιήστε το GUI του Lemonade για να κατεβάσετε πρώτα τα μοντέλα σας, και στη συνέχεια χρησιμοποιήστε τα από το Open WebUI.

---

## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->

## Εφάπαξ Ρύθμιση

Αυτό το playbook χρειάζεται το Lemonade να εκτελείται ως backend και, στο Linux, μια μηχανή container (Podman) για την εκτέλεση του Open WebUI. Ρυθμίστε αυτά πριν εγκαταστήσετε το Open WebUI.

<!-- @os:windows -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:lemonade -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,lemonade -->
<!-- @device:end -->
---
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:lemonade,podman -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,lemonade,podman -->
<!-- @device:end -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
---
<!-- @device:end -->
<!-- @os:end -->

<!-- @test:id=lemonade-cli-verify timeout=30 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end --> 

## Λήψη Μοντέλων στο Lemonade

Πριν εγκαταστήσετε το Open WebUI, βεβαιωθείτε ότι τα μοντέλα που θέλετε να χρησιμοποιήσετε έχουν ληφθεί και είναι έτοιμα στο Lemonade.

1. Ανοίξτε το GUI του Lemonade στο `http://localhost:13305`.
2. Περιηγηθείτε στα διαθέσιμα μοντέλα και κατεβάστε αυτά που θέλετε να χρησιμοποιήσετε (π.χ., ένα LLM για συνομιλία, ένα μοντέλο όρασης ή/και ένα μοντέλο Stable Diffusion για δημιουργία εικόνας).
3. Επιβεβαιώστε ότι το API είναι προσβάσιμο επισκεπτόμενοι το `http://localhost:13305/api/v1/models` στο πρόγραμμα περιήγησής σας — θα πρέπει να βλέπετε τα ληφθέντα μοντέλα σας να εμφανίζονται.

> Τα μοντέλα πρέπει να ληφθούν στο **Lemonade** (`localhost:13305`) πριν μπορέσουν να εμφανιστούν στο **Open WebUI** (`localhost:8080`). Εάν ένα μοντέλο δεν εμφανίζεται στο Open WebUI αργότερα, επιστρέψτε εδώ και ελέγξτε πρώτα το Lemonade.


<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
<!-- @test:id=openwebui-lemonade-multimodal-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$tmpChat = $null
$tmpVision = $null
$tmpImg = $null

try {
  # Wait for /models
  $modelsJson = $null
  for ($i=0; $i -lt 120; $i++) {
    $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
    if ($modelsJson) { break }
    Start-Sleep -Seconds 1
  }
  if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
  Write-Host "OK: Lemonade server is responding"
  
  # Verify required models are present + downloaded
  $parsed = $modelsJson | ConvertFrom-Json
  $required = @(
    "Qwen3-4B-Hybrid",
    "Qwen3.5-4B-GGUF",
    "SDXL-Turbo"
  )
  foreach ($mid in $required) {
    $entry = $parsed.data | Where-Object { $_.id -eq $mid } | Select-Object -First 1
    if (-not $entry) { throw "Model $mid is not present in /api/v1/models. Please download it." }
    if (-not $entry.downloaded) { throw "Model $mid is present but not downloaded. Please download it." }
    Write-Host "OK: $mid is downloaded"
  }

  # Chat completion smoke test (LLM)
  $chatBody = @{
    model = "Qwen3-4B-Hybrid"
    messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
    temperature = 0
    max_tokens = 500
    stream = $false
  } | ConvertTo-Json -Depth 6
  $tmpChat = Join-Path $env:TEMP "chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from chat/completions" }
  $chatParsed = $chatOut | ConvertFrom-Json
  $chatText = $chatParsed.choices[0].message.content
  if ($chatText -notmatch "\bOK\b") { throw "LLM chat test failed. Got: $chatText" }
  Write-Host "OK: LLM chat works"

  # Vision smoke test (OpenAI-style image_url)
  $png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
  $dataUrl = "data:image/png;base64,$png1x1"
  $visionBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "If you can see an image input, reply with exactly: OK" },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 256
  } | ConvertTo-Json -Depth 10
  $tmpVision = Join-Path $env:TEMP "vision-body.json"
  [System.IO.File]::WriteAllText($tmpVision, $visionBody, [System.Text.UTF8Encoding]::new($false))
  $visionOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpVision"
  if (-not $visionOut) { throw "Empty response from vision chat/completions" }
  $visionParsed = $visionOut | ConvertFrom-Json
  if (-not $visionParsed.choices -or $visionParsed.choices.Count -lt 1) { throw "Unexpected vision response (no choices). Raw response: $visionOut" }
  $visionText = $visionParsed.choices[0].message.content
  if ([string]::IsNullOrWhiteSpace($visionText)) { throw "Vision returned empty content. Raw response: $visionOut" }
  if ($visionText -notmatch "\bOK\b") { throw "Vision test failed. Got: $visionText. Raw response: $visionOut" }
  Write-Host "OK: Vision chat works"

  # Image generation smoke test
  $imgBody = @{
    model  = "SDXL-Turbo"
    prompt = "A simple red cube on a white table, studio lighting"
    size   = "256x256"
    steps  = 4
    response_format = "b64_json"
  } | ConvertTo-Json -Depth 6
  $tmpImg = Join-Path $env:TEMP "img-body.json"
  [System.IO.File]::WriteAllText($tmpImg, $imgBody, [System.Text.UTF8Encoding]::new($false))
  $imgOut = curl.exe -sS --fail-with-body --max-time 900 http://127.0.0.1:13305/api/v1/images/generations `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpImg"
  if (-not $imgOut) { throw "Empty response from images/generations" }
  $imgParsed = $imgOut | ConvertFrom-Json
  if (-not $imgParsed.data -or -not $imgParsed.data[0].b64_json) { throw "Image generation did not return data[0].b64_json. Raw response: $imgOut" }
  Write-Host "OK: Image generation works"
}
finally {
  @($tmpChat, $tmpVision, $tmpImg) |
  Where-Object { $_ } |
  ForEach-Object { Remove-Item $_ -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=openwebui-lemonade-multimodal-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$tmpChat = $null
$tmpVision = $null
$tmpImg = $null

try {
  # Wait for /models
  $modelsJson = $null
  for ($i=0; $i -lt 120; $i++) {
    $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
    if ($modelsJson) { break }
    Start-Sleep -Seconds 1
  }
  if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
  Write-Host "OK: Lemonade server is responding"
  
  # Verify required models are present + downloaded
  $parsed = $modelsJson | ConvertFrom-Json
  $required = @(
    "Qwen3.5-4B-GGUF",
    "SDXL-Turbo"
  )
  foreach ($mid in $required) {
    $entry = $parsed.data | Where-Object { $_.id -eq $mid } | Select-Object -First 1
    if (-not $entry) { throw "Model $mid is not present in /api/v1/models. Please download it." }
    if (-not $entry.downloaded) { throw "Model $mid is present but not downloaded. Please download it." }
    Write-Host "OK: $mid is downloaded"
  }

  # Chat completion smoke test (LLM)
  $chatBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
    temperature = 0
    max_tokens = 500
    stream = $false
  } | ConvertTo-Json -Depth 6
  $tmpChat = Join-Path $env:TEMP "chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from chat/completions" }
  $chatParsed = $chatOut | ConvertFrom-Json
  $chatText = $chatParsed.choices[0].message.content
  if ($chatText -notmatch "\bOK\b") { throw "LLM chat test failed. Got: $chatText" }
  Write-Host "OK: LLM chat works"

  # Vision smoke test (OpenAI-style image_url)
  $png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
  $dataUrl = "data:image/png;base64,$png1x1"
  $visionBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "If you can see an image input, reply with exactly: OK" },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 256
  } | ConvertTo-Json -Depth 10
  $tmpVision = Join-Path $env:TEMP "vision-body.json"
  [System.IO.File]::WriteAllText($tmpVision, $visionBody, [System.Text.UTF8Encoding]::new($false))
  $visionOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpVision"
  if (-not $visionOut) { throw "Empty response from vision chat/completions" }
  $visionParsed = $visionOut | ConvertFrom-Json
  if (-not $visionParsed.choices -or $visionParsed.choices.Count -lt 1) { throw "Unexpected vision response (no choices). Raw response: $visionOut" }
  $visionText = $visionParsed.choices[0].message.content
  if ([string]::IsNullOrWhiteSpace($visionText)) { throw "Vision returned empty content. Raw response: $visionOut" }
  if ($visionText -notmatch "\bOK\b") { throw "Vision test failed. Got: $visionText. Raw response: $visionOut" }
  Write-Host "OK: Vision chat works"

  # Image generation smoke test
  $imgBody = @{
    model  = "SDXL-Turbo"
    prompt = "A simple red cube on a white table, studio lighting"
    size   = "256x256"
    steps  = 4
    response_format = "b64_json"
  } | ConvertTo-Json -Depth 6
  $tmpImg = Join-Path $env:TEMP "img-body.json"
  [System.IO.File]::WriteAllText($tmpImg, $imgBody, [System.Text.UTF8Encoding]::new($false))
  $imgOut = curl.exe -sS --fail-with-body --max-time 900 http://127.0.0.1:13305/api/v1/images/generations `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpImg"
  if (-not $imgOut) { throw "Empty response from images/generations" }
  $imgParsed = $imgOut | ConvertFrom-Json
  if (-not $imgParsed.data -or -not $imgParsed.data[0].b64_json) { throw "Image generation did not return data[0].b64_json. Raw response: $imgOut" }
  Write-Host "OK: Image generation works"
}
finally {
  @($tmpChat, $tmpVision, $tmpImg) |
  Where-Object { $_ } |
  ForEach-Object { Remove-Item $_ -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @device:end -->
<!-- @os:end --> 

<!-- @os:linux --> 
<!-- @test:id=openwebui-lemonade-multimodal-smoke-linux timeout=1800 hidden=True -->
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
import base64, json, os, sys, urllib.request

data = json.loads(os.environ["MODELS_JSON"])
required = [
  "Qwen3.5-4B-GGUF",
  "SDXL-Turbo",
]

by_id = {m.get("id"): m for m in data.get("data", [])}
for mid in required:
  m = by_id.get(mid)
  if not m:
    print(f"Model {mid} is not present in /api/v1/models. Please download it.")
    sys.exit(1)
  if not m.get("downloaded", False):
    print(f"Model {mid} is present but not downloaded. Please download it.")
    sys.exit(1)
  print(f"OK: {mid} is downloaded")

def post_json(url, payload, timeout=300):
  req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
      "Content-Type": "application/json",
      "Authorization": "Bearer -",
    },
    method="POST",
  )
  try:
    with urllib.request.urlopen(req, timeout=timeout) as r:
      return json.loads(r.read().decode("utf-8"))
  except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    raise SystemExit(f"POST {url} failed with HTTP {e.code}. Response body:\n{body}")

# LLM chat smoke test
chat = post_json("http://127.0.0.1:13305/api/v1/chat/completions", {
  "model": "Qwen3.5-4B-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500,
  "stream": False,
}, timeout=300)
text = chat["choices"][0]["message"]["content"]
if "OK" not in text:
  raise SystemExit(f"LLM chat test failed. Got: {text}")
print("OK: LLM chat works")

# Vision smoke test (OpenAI image_url format)
png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
data_url = "data:image/png;base64," + png1x1
vision = post_json("http://127.0.0.1:13305/api/v1/chat/completions", {
  "model": "Qwen3.5-4B-GGUF",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "If you can see an image input, reply with exactly: OK"},
      {"type": "image_url", "image_url": {"url": data_url}},
    ],
  }],
  "temperature": 0,
  "max_tokens": 256,
}, timeout=300)
if not vision.get("choices"):
  raise SystemExit(f"Unexpected vision response (no choices). Raw response:\n{json.dumps(vision, indent=2)}")
vtext = vision["choices"][0]["message"].get("content", "")
if not vtext.strip():
  raise SystemExit(f"Vision returned empty content. Raw response:\n{json.dumps(vision, indent=2)}")
if "OK" not in vtext:
  raise SystemExit(f"Vision test failed. Got: {vtext}\nRaw response:\n{json.dumps(vision, indent=2)}")
print("OK: Vision chat works")

# Image generation smoke test
img = post_json("http://127.0.0.1:13305/api/v1/images/generations", {
  "model": "SDXL-Turbo",
  "prompt": "A simple red cube on a white table, studio lighting",
  "size": "256x256",
  "steps": 4,
  "response_format": "b64_json",
}, timeout=900)
b64 = img.get("data", [{}])[0].get("b64_json")
if not b64:
  raise SystemExit("Image generation did not return data[0].b64_json")
print("OK: Image generation works")
PY
```
<!-- @test:end --> 
<!-- @os:end --> 

## Εγκατάσταση του Open WebUI

<!-- @os:windows -->
### 1. Εγκατάσταση Python 3.12

Το Open WebUI απαιτεί **Python 3.12** — δεν εγκαθίσταται σε Python 3.13+. Ο Windows Python Launcher (`py`) σάς επιτρέπει να εγκαταστήσετε την έκδοση 3.12 παράλληλα με οποιαδήποτε υπάρχουσα έκδοση Python χωρίς συγκρούσεις.

```powershell
winget install Python.Python.3.12
```

Κλείστε και ανοίξτε ξανά το τερματικό σας μετά την εγκατάσταση, και στη συνέχεια επαληθεύστε:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Σημείωση:** Το σύστημά σας διαθέτει προεγκατεστημένη την Python 3.13. Η εγκατάσταση της 3.12 δεν την επηρεάζει — η `python` συνεχίζει να χρησιμοποιεί την 3.13, και η `py -3.12` στοχεύει μόνο στην 3.12 όταν τη χρειάζεστε.
<!-- @device:end -->

<!-- @test:id=python-env-check-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$v = (& py -3.12 --version) 2>&1
if ($LASTEXITCODE -ne 0) { throw "Python 3.12 was not found. Install it with: winget install Python.Python.3.12" }
if ($v -notmatch "Python 3\.12\.") { throw "Expected Python 3.12.x but got: $v" }

Write-Host "OK: $v"
```
<!-- @test:end --> 

### 2. Δημιουργία εικονικού περιβάλλοντος και εγκατάσταση του Open WebUI

```powershell
mkdir openwebui
cd openwebui
py -3.12 -m venv openwebui-venv
.\openwebui-venv\Scripts\activate
pip install open-webui beautifulsoup4
```

<!-- @test:id=openwebui-install-venv-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
if (Test-Path $work) { Remove-Item -Recurse -Force $work }
New-Item -ItemType Directory -Force -Path $work | Out-Null

Push-Location $work
try {
  py -3.12 -m venv openwebui-venv
  $py = Join-Path $work "openwebui-venv\Scripts\python.exe"

  & $py -m pip install --upgrade pip
  if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }

  & $py -m pip install open-webui beautifulsoup4
  if ($LASTEXITCODE -ne 0) { throw "pip install open-webui beautifulsoup4 failed" }

  Write-Host "OK: open-webui installed in venv"
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 

<!-- @test:id=openwebui-install-check-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
$venv = Join-Path $work "openwebui-venv"
$py = Join-Path $venv "Scripts\python.exe"

& $py -c "import open_webui; print('OK: import open_webui')"
& $py -c "import bs4; print('OK: bs4 import')"
```
<!-- @test:end --> 

<!-- @test:id=openwebui-cli-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
$venv = Join-Path $work "openwebui-venv"
$ow = Join-Path $venv "Scripts\open-webui.exe"

if (-not (Test-Path $ow)) { throw "open-webui.exe not found at $ow" }

& $ow --help | Out-Null
Write-Host "OK: open-webui CLI is available"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
Θα χρησιμοποιήσουμε τώρα την υπηρεσία Podman για να containerize την εγκατάστασή μας του Open WebUI.

Κατεβάστε το παρακάτω σε έναν κατάλογο της επιλογής σας: [compose.yml](assets/compose.yml)

Σε αυτόν τον κατάλογο, εκτελέστε την ακόλουθη εντολή:

```bash
podman compose up -d
```

Αυτό κατεβάζει την εικόνα του Open WebUI και γράφει σε μόνιμη αποθήκευση.

Εκκινήστε το Open WebUI πληκτρολογώντας `localhost:8080` στη γραμμή διευθύνσεων του προγράμματος περιήγησής σας.

<!-- @test:id=openwebui-podman-prereq-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
export PODMAN_COMPOSE_WARNING_LOGS=false

podman --version
podman compose version
podman info >/dev/null

if [ ! -f compose.yml ]; then
  echo "compose.yml not found in current working directory (playbooks/supplemental/open-webui-chat/assets)"
  exit 1
fi

echo "OK: Podman, Podman Compose, and compose.yml are available"
```
<!-- @test:end -->

<!-- @test:id=openwebui-compose-validate-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import sys
import yaml

path = Path("compose.yml")
if not path.exists():
    raise SystemExit("compose.yml not found")

data = yaml.safe_load(path.read_text())
svc = data.get("services", {}).get("open-webui")
if not svc:
    raise SystemExit("compose.yml does not define services.open-webui")

expected_image = "ghcr.io/open-webui/open-webui:main"
if svc.get("image") != expected_image:
    raise SystemExit(f"Expected image {expected_image}, got {svc.get('image')}")

if svc.get("container_name") != "open-webui":
    raise SystemExit("Expected container_name: open-webui")

if svc.get("network_mode") != "host":
    raise SystemExit("Expected network_mode: host")

volumes = svc.get("volumes", [])
if "open_webui_data:/app/backend/data" not in volumes:
    raise SystemExit("Expected open_webui_data:/app/backend/data volume mount")

if "open_webui_data" not in data.get("volumes", {}):
    raise SystemExit("Expected top-level open_webui_data volume")

print("OK: compose.yml matches the Open WebUI Podman setup")
PY

podman compose -f compose.yml config >/dev/null

echo "OK: podman compose can parse compose.yml"
```
<!-- @test:end -->
<!-- @os:end -->

> **Συμβουλή**: Το Open WebUI παρέχει επίσης άλλες επιλογές εγκατάστασης στο [GitHub](https://github.com/open-webui/open-webui) τους.
## Εκκίνηση του Διακομιστή Open WebUI

<!-- @os:windows -->
- Εκτελέστε την παρακάτω εντολή για να εκκινήσετε τον HTTP διακομιστή Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- Σε ένα πρόγραμμα περιήγησης, μεταβείτε στη διεύθυνση `http://localhost:8080`.
- Το Open WebUI θα σας ζητήσει να δημιουργήσετε έναν τοπικό λογαριασμό διαχειριστή. Μόλις συνδεθείτε, θα δείτε τη διεπαφή συνομιλίας.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Κρατήστε το παράθυρο τερματικού ανοιχτό. Το κλείσιμό του διακόπτει το Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Το container εκτελείται στο παρασκήνιο. Από τον κατάλογο που περιέχει το `compose.yml`, διαχειριστείτε το με `podman compose down` (διακοπή) και `podman compose up -d` (εκκίνηση). Οι λογαριασμοί και οι ρυθμίσεις σας παραμένουν στον τόμο `open_webui_data`.
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openwebui-server-smoke-windows timeout=900 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
$venv = Join-Path $work "openwebui-venv"
$ow = Join-Path $venv "Scripts\open-webui.exe"
if (-not (Test-Path $ow)) { throw "open-webui not found. Run openwebui-install-venv-windows first." }

# Fresh data dir so auth mode/config isn't polluted by previous runs
$dataDir = Join-Path $work "openwebui-data-ci"
if (Test-Path $dataDir) { Remove-Item -Recurse -Force $dataDir }
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

$env:DATA_DIR = $dataDir
$env:WEBUI_AUTH = "False" # Disable auth for CI
$env:ENABLE_PERSISTENT_CONFIG = "False" # Ensure environment-variable config applies for the run and isn't overridden by persistent settings

$logOut = Join-Path $work "openwebui-ci-out.log"
$logErr = Join-Path $work "openwebui-ci-err.log"
$p = Start-Process -FilePath $ow -ArgumentList "serve --port 8080" -NoNewWindow -PassThru -RedirectStandardOutput $logOut -RedirectStandardError $logErr
try {
  $ok = $false
  for ($i=0; $i -lt 90; $i++) {
    $health = curl.exe -s --max-time 2 http://127.0.0.1:8080/health
    if ($health) { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "Open WebUI not ready on http://127.0.0.1:8080" }
  Write-Host "OK: Open WebUI is responding on /health"
}
finally {
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux -->
<!-- @test:id=openwebui-podman-server-smoke-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
export PODMAN_COMPOSE_WARNING_LOGS=false

cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Clean up a stale container from a previous failed run.
podman rm -f open-webui >/dev/null 2>&1 || true

podman compose -f compose.yml up -d

health=""
for i in $(seq 1 180); do
  health="$(curl -fsS --max-time 2 http://127.0.0.1:8080/health || true)"
  if [ -n "$health" ]; then
    break
  fi
  sleep 1
done

if [ -z "$health" ]; then
  echo "Open WebUI did not become ready on http://127.0.0.1:8080/health"
  echo "Container status:"
  podman ps -a || true
  echo "Open WebUI logs:"
  podman logs --tail 200 open-webui || true
  exit 1
fi

echo "OK: Open WebUI container is responding on /health"

# Verify that the Open WebUI container can reach Lemonade through host networking.
podman exec open-webui sh -lc 'python -c "import json, urllib.request; data=json.load(urllib.request.urlopen(\"http://127.0.0.1:13305/api/v1/models\", timeout=10)); assert \"data\" in data; print(\"OK: Open WebUI container can reach Lemonade models endpoint\")"'
```
<!-- @test:end --> 
<!-- @os:end --> 

## Σύνδεση του Open WebUI με το Lemonade

Τώρα που και οι δύο υπηρεσίες εκτελούνται — το Lemonade στο `localhost:13305` και το Open WebUI στο `localhost:8080` — συνδέστε τα ώστε το Open WebUI να μπορεί να χρησιμοποιεί τα μοντέλα του Lemonade.

Στο Open WebUI:

1. Κάντε κλικ στο **εικονίδιο προφίλ χρήστη** στην επάνω δεξιά γωνία και, στη συνέχεια, επιλέξτε **Ρυθμίσεις**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. Στον πίνακα Ρυθμίσεων, κάντε κλικ στις **Ρυθμίσεις Διαχειριστή** κάτω αριστερά.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Στην πλαϊνή μπάρα Ρυθμίσεων Διαχειριστή, κάντε κλικ στις **Συνδέσεις** (ή μεταβείτε απευθείας στη διεύθυνση `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Στο **OpenAI API**, προσθέστε μια νέα σύνδεση:
   - **Βασικό URL:** `http://localhost:13305/api/v1`
   - **Κλειδί API:** `-` (μια μονή παύλα λειτουργεί για τοπική χρήση)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Βεβαιωθείτε ότι στο **"Διαχείριση Συνδέσεων OpenAI API"**, μόνο το `http://localhost:13305/api/v1` είναι ενεργοποιημένο. Απενεργοποιήστε τυχόν άλλες συνδέσεις (π.χ., την προεπιλεγμένη σύνδεση OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Κάντε κλικ στο **Αποθήκευση**.

7. **(Συνιστάται)** Απενεργοποιήστε τις λειτουργίες αυτόματης δημιουργίας για να διατηρήσετε το Open WebUI αποκρινόμενο με τοπικά LLM. Μεταβείτε στις **Ρυθμίσεις Διαχειριστή → Ρυθμίσεις → Διεπαφή** και απενεργοποιήστε:
   - Δημιουργία Τίτλου
   - Δημιουργία Συνέχειας
   - Δημιουργία Ετικετών

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Κάντε κλικ στο **Αποθήκευση** και, στη συνέχεια, επιστρέψτε στη διεύθυνση `http://localhost:8080`.
9. Κάντε κλικ στο αναπτυσσόμενο μενού μοντέλου — θα πρέπει να βλέπετε τα μοντέλα που κατεβάσατε από το Lemonade.

---

## Κύριες Δραστηριότητες

Τώρα είστε έτοιμοι. Ας δούμε τρία ενδιαφέροντα πράγματα που μπορείτε να κάνετε.

---

### Δραστηριότητα 1: Συνομιλία με ένα Τοπικό LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Κάντε κλικ στο αναπτυσσόμενο μενού στην επάνω αριστερή γωνία της διεπαφής. Αυτό θα εμφανίσει τα μοντέλα Lemonade που έχετε εγκαταστήσει. Επιλέξτε ένα για να συνεχίσετε. (παράδειγμα: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Εισαγάγετε ένα μήνυμα στο LLM και κάντε κλικ στην αποστολή (ή πατήστε Enter). Το LLM θα χρειαστεί μερικά δευτερόλεπτα για να φορτωθεί στη μνήμη και στη συνέχεια θα δείτε την απόκριση να εμφανίζεται σταδιακά.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Κάντε κλικ στο αναπτυσσόμενο μενού στην επάνω αριστερή γωνία της διεπαφής. Αυτό θα εμφανίσει τα μοντέλα Lemonade που έχετε εγκαταστήσει. Επιλέξτε ένα για να συνεχίσετε. (παράδειγμα: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Εισαγάγετε ένα μήνυμα στο LLM και κάντε κλικ στην αποστολή (ή πατήστε Enter). Το LLM θα χρειαστεί μερικά δευτερόλεπτα για να φορτωθεί στη μνήμη και στη συνέχεια θα δείτε την απόκριση να εμφανίζεται σταδιακά.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Το μοντέλο θα απαντήσει στη συνομιλία.

4. Αυτή τη στιγμή, ανοίξτε τη `Διαχείριση Εργασιών` στο σύστημά σας. Θα δείτε **υψηλή χρήση GPU ή NPU** ανάλογα με το αν το μοντέλο που επιλέξατε είναι **Hybrid** ή **NPU** αντίστοιχα. Χρησιμοποιώντας τη διαχείριση εργασιών, μπορείτε να επιβεβαιώσετε ότι εκτελείτε το μοντέλο τοπικά.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Κάντε κλικ στο αναπτυσσόμενο μενού στην επάνω αριστερή γωνία της διεπαφής. Αυτό θα εμφανίσει τα μοντέλα Lemonade που έχετε εγκαταστήσει. Επιλέξτε ένα για να συνεχίσετε. (παράδειγμα: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Εισαγάγετε ένα μήνυμα στο LLM και κάντε κλικ στην αποστολή (ή πατήστε Enter). Το LLM θα χρειαστεί μερικά δευτερόλεπτα για να φορτωθεί στη μνήμη και στη συνέχεια θα δείτε την απόκριση να εμφανίζεται σταδιακά.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Το μοντέλο θα απαντήσει στη συνομιλία.
<!-- @os:end -->

Αυτό επαληθεύει ότι το Open WebUI μπορεί να στέλνει αιτήματα στο Lemonade χρησιμοποιώντας το συμβατό με OpenAI τελικό σημείο συνομιλίας.

---

### Δραστηριότητα 2: Ανέβασμα Εικόνας και Υποβολή Ερωτήσεων (Vision)

Αυτό απαιτεί ένα μοντέλο που υποστηρίζει εισαγωγή εικόνας (μοντέλο Vision ή Πολυτροπικό μοντέλο).

1. Κάντε κλικ στο εικονίδιο φίλτρου, επιλέξτε "Κατά Κατηγορία" και, στη συνέχεια, επιλέξτε ένα μοντέλο από την ενότητα **Vision** (π.χ., `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Κάντε κλικ στο κουμπί **`+`** στο πλαίσιο μηνύματος και ανεβάστε μια εικόνα
3. Κάντε μια ερώτηση που απαιτεί πραγματική κατανόηση εικόνας: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Το μοντέλο απαντά με βάση το περιεχόμενο της εικόνας, όχι γενικό κείμενο.

Αυτό αποδεικνύει ότι το Open WebUI μπορεί να στέλνει πολυτροπικά αιτήματα (κείμενο + εικόνα) μέσω του backend (Lemonade) σε ένα μοντέλο vision.

---

<!-- @os:windows -->
### Δραστηριότητα 3: Δημιουργία Εικόνας από Κείμενο (Stable Diffusion)

Τα μοντέλα Stable Diffusion δεν υποστηρίζουν δημιουργία κειμένου, δημιουργούν μόνο εικόνες μέσω του Images API.

#### Βήμα 1: Διαμόρφωση Δημιουργίας Εικόνων στο Open WebUI

1. Στο γραφικό περιβάλλον του Lemonade (`http://localhost:13305`), αναζητήστε `SDXL-Turbo` (γρήγορο) ή `SDXL-Base-1.0` (υψηλότερη ποιότητα) και κατεβάστε το.
2. Μεταβείτε στις **Ρυθμίσεις Διαχειριστή → Εικόνες** (http://localhost:8080/admin/settings/images)
3. Ορίστε:
   - **Δημιουργία Εικόνων:** ΕΝΕΡΓΟ
   - **Μηχανή Δημιουργίας Εικόνων:** Προεπιλογή (OpenAI)
   - **Βασικό URL OpenAI API:** `http://localhost:13305/api/v1`
   - **Κλειδί OpenAI API:** `-`
   - **Μοντέλο:** `SDXL-Turbo` ή `SDXL-Base-1.0`
4. Αν θέλετε να προσθέσετε περισσότερες παραμέτρους, προσθέστε τις στο πεδίο κειμένου ως JSON. Για παράδειγμα: `{ "steps": 4, "cfg_scale": 1 }`. Δείτε τις διαθέσιμες παραμέτρους στη διεύθυνση [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Αποθήκευση
#### Βήμα 2: Ενεργοποίηση Δημιουργίας Εικόνας για το μοντέλο
Αυτό το βήμα διασφαλίζει ότι ενεργοποιείτε τη Δημιουργία Εικόνας ως δυνατότητα για το μοντέλο σας.
1. Μεταβείτε στις **Admin Settings → Models** (http://localhost:8080/admin/settings/models) και επιλέξτε το μοντέλο σας
2. Ενεργοποιήστε το `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Βήμα 3: Δημιουργία εικόνας από την οθόνη συνομιλίας

1. Επιστρέψτε στη συνομιλία στο `http://localhost:8080`.
2. Επιλέξτε ένα **LLM Δημιουργίας Κειμένου** στο αναπτυσσόμενο μενού μοντέλων (παράδειγμα: Qwen, Llama). **Μην επιλέξετε μοντέλο Stable Diffusion** καθώς αυτός είναι ο επιλογέας μοντέλου συνομιλίας.
3. Στην περιοχή μηνύματος, κάντε κλικ στις **Integrations** και ενεργοποιήστε το **Image**.
4. Χρησιμοποιήστε μια προτροπή όπως: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Μια εικόνα δημιουργείται και εμφανίζεται στη συνομιλία.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Αυτό αποδεικνύει ότι το Open WebUI μπορεί να συντονίσει μια ροή εργασίας «δύο μερών»:
  - Το LLM βοηθά στη βελτίωση της προτροπής
  - Η εικόνα δημιουργείται μέσω του endpoint Images του Lemonade χρησιμοποιώντας Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Δραστηριότητα 3: Δημιουργία Εικόνας από Προτροπή Κειμένου (Stable Diffusion)

Τα μοντέλα Stable Diffusion δεν υποστηρίζουν δημιουργία κειμένου, δημιουργούν μόνο εικόνες μέσω του Images API.

#### Βήμα 1: Διαμόρφωση Δημιουργίας Εικόνας στο Open WebUI

1. Στο GUI του Lemonade (`http://localhost:13305`), αναζητήστε `SDXL-Turbo` (γρήγορο) ή `SDXL-Base-1.0` (υψηλότερη ποιότητα) και κατεβάστε το.
2. Μεταβείτε στις **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Ορίστε:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` ή `SDXL-Base-1.0`
4. Αν θέλετε να προσθέσετε περισσότερες παραμέτρους, προσθέστε τις στο πεδίο κειμένου ως JSON. Για παράδειγμα: `{ "steps": 4, "cfg_scale": 1 }`. Δείτε τις διαθέσιμες παραμέτρους στο [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Αποθήκευση


#### Βήμα 2: Ενεργοποίηση Δημιουργίας Εικόνας για το μοντέλο
Αυτό το βήμα διασφαλίζει ότι ενεργοποιείτε τη Δημιουργία Εικόνας ως δυνατότητα για το μοντέλο σας.
1. Μεταβείτε στις **Admin Settings → Models** (http://localhost:8080/admin/settings/models) και επιλέξτε το μοντέλο σας
2. Ενεργοποιήστε το `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Βήμα 3: Δημιουργία εικόνας από την οθόνη συνομιλίας

1. Επιστρέψτε στη συνομιλία στο `http://localhost:8080`.
2. Επιλέξτε ένα **LLM Δημιουργίας Κειμένου** στο αναπτυσσόμενο μενού μοντέλων (παράδειγμα: Qwen, Llama). **Μην επιλέξετε μοντέλο Stable Diffusion** καθώς αυτός είναι ο επιλογέας μοντέλου συνομιλίας.
3. Στην περιοχή μηνύματος, κάντε κλικ στις **Integrations** και ενεργοποιήστε το **Image**.
4. Χρησιμοποιήστε μια προτροπή όπως: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Μια εικόνα δημιουργείται και εμφανίζεται στη συνομιλία.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Αυτό αποδεικνύει ότι το Open WebUI μπορεί να συντονίσει μια ροή εργασίας «δύο μερών»:
  - Το LLM βοηθά στη βελτίωση της προτροπής
  - Η εικόνα δημιουργείται μέσω του endpoint Images του Lemonade χρησιμοποιώντας Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Αντιμετώπιση Προβλημάτων

### «Κανένα μοντέλο δεν εμφανίζεται στο Open WebUI»
- Πρώτα, ελέγξτε το Lemonade: ανοίξτε το `http://localhost:13305/api/v1/models` σε ένα πρόγραμμα περιήγησης και επιβεβαιώστε ότι τα μοντέλα σας εμφανίζονται και έχουν ληφθεί
- Στη συνέχεια, ελέγξτε τη σύνδεση Open WebUI: μεταβείτε στις **Admin Settings → Connections** στο `http://localhost:8080/admin/settings/connections` και επαληθεύστε ότι το Base URL είναι `http://localhost:13305/api/v1`

### Μήνυμα σφάλματος «This model does not support chat completion»
- Επιλέξατε ένα μοντέλο εικόνας (SDXL-Turbo / SDXL-Base-1.0) στο αναπτυσσόμενο μενού μοντέλου συνομιλίας.
- **Επίλυση**: επιλέξτε ένα LLM για συνομιλία και χρησιμοποιήστε την εναλλαγή Image και τις ρυθμίσεις Images για τη δημιουργία.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Σφάλματα/χρονικά όρια δημιουργίας εικόνας
- Ξεκινήστε πρώτα με το `SDXL-Turbo` (γρήγορο, λιγότερα βήματα)
- Μόλις λειτουργήσει, αλλάξτε το μοντέλο εικόνας σε `SDXL-Base-1.0` για ποιότητα

---

## Επόμενα Βήματα

Τώρα διαθέτετε μια λειτουργική **«τοπική στοίβα AI»**, ένα ενιαίο UI που ελέγχει πολλαπλούς τύπους μοντέλων μέσω ενός τυπικού API.

Ακολουθούν τρεις επεκτάσεις που ξεκλειδώνουν εντελώς νέες ροές εργασίας:

### 1. Ομιλία σε Κείμενο με Whisper

Δοκιμάστε να μετατρέψετε ήχο σε κείμενο χρησιμοποιώντας ένα μοντέλο Whisper και στη συνέχεια τροφοδοτήστε το σε ένα LLM για περίληψη, στοιχεία δράσης ή επανεγγραφή. Αυτό είναι το θεμέλιο για σημειώσεις συναντήσεων και βοηθούς που βασίζονται στη φωνή.

### 2. Κωδικοποίηση Python εντός Open WebUI

Χρησιμοποιήστε την ενσωματωμένη εμπειρία εκτέλεσης κώδικα του Open WebUI για να εκτελέσετε αποσπάσματα Python, να επιθεωρήσετε αποτελέσματα και να επαναλαμβάνετε γρηγορότερα—χωρίς να φύγετε από το UI. [Αναφορά](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Απόδοση HTML εντός Open WebUI

Αποδώστε εξόδους HTML απευθείας στη διεπαφή. Αυτό είναι εκπληκτικά ισχυρό για τη δημιουργία γρήγορων πρωτοτύπων, μορφοποιημένων αναφορών και διαδραστικών αποσπασμάτων. [Αναφορά](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Αναφορές

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Τεκμηρίωση Lemonade Server](https://lemonade-server.ai/docs)
- [CLI Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [Οδηγός ενσωμάτωσης Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Προδιαγραφή API Lemonade Server (endpoints)](https://lemonade-server.ai/docs/server/server_spec)
- [Βίντεο παρουσίαση (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Βίντεο παρουσίαση (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)