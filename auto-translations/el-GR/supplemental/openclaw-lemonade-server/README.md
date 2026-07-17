<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Εκτέλεση του OpenClaw με τον Lemonade Server ως backend

## Επισκόπηση

Το [**OpenClaw**](https://openclaw.ai/) είναι ένας αυτόνομος πράκτορας τεχνητής νοημοσύνης που μπορεί να γράφει και να εκτελεί κώδικα, να διαχειρίζεται αρχεία και να επεξεργάζεται σύνθετες πολυβηματικές εργασίες για λογαριασμό σας. Σε αντίθεση με έναν βοηθό συνομιλίας που απλώς απαντά σε ερωτήσεις, το OpenClaw εκτελεί πραγματικές ενέργειες στο σύστημά σας, πράγμα που σημαίνει ότι χρειάζεται ένα γρήγορο και ικανό AI backend που να μπορεί να ανταποκριθεί στις απαιτήσεις ενός βρόχου πράκτορα.

Ο [**Lemonade Server**](https://lemonade-server.ai/) είναι αυτό το backend. Πρόκειται για έναν τοπικό διακομιστή συμπερασμού ανοιχτού κώδικα που εκτελεί μοντέλα GenAI απευθείας στο υλικό σας και τα εκθέτει μέσω του βιομηχανικού προτύπου OpenAI API.

Μαζί, σχηματίζουν ένα πλήρως τοπικό stack πράκτορα AI: ο Lemonade χειρίζεται τη συμπερασματολογία μοντέλων, και το OpenClaw παρέχει τον βρόχο πράκτορα που μετατρέπει τις εξόδους του μοντέλου σε πραγματικές ενέργειες.

> **Πριν συνεχίσετε:** Το OpenClaw είναι ένας εξαιρετικά αυτόνομος πράκτορας AI. Η παροχή πρόσβασης οποιουδήποτε πράκτορα AI στο σύστημά σας μπορεί να οδηγήσει σε απρόβλεπτα ή ακούσια αποτελέσματα. Προχωρήστε μόνο εάν κατανοείτε τους κινδύνους και είστε άνετοι με αυτόνομο λογισμικό που ενεργεί για λογαριασμό σας.

---

## Τι θα Μάθετε

Στο τέλος αυτού του playbook θα μπορείτε να:

- Μάθετε για τον **Lemonade Server**
- **Εγκαταστήσετε το OpenClaw** και **να το κατευθύνετε στον Lemonade Server** ως AI backend.
- **Εκκινήσετε το gateway του OpenClaw** και να επιβεβαιώσετε ότι ο πράκτοράς σας είναι έτοιμος να λειτουργήσει.
- **Συνδέσετε ένα κανάλι επικοινωνίας** (Discord ή Telegram) ώστε να μπορείτε να συνομιλείτε με τον πράκτορά σας από οποιαδήποτε συσκευή.

---

## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενων Λογισμικών

<!-- @os:linux -->
- Ένας υπολογιστής με **Ubuntu 24.04+** ή συμβατή διανομή Linux βασισμένη σε Debian με `apt-get`
- Τουλάχιστον **12 GB RAM** (συνιστώνται 64 GB+ για μεγαλύτερα μοντέλα)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Προαιρετικό, για απομόνωση του OpenClaw σε sandbox)

- **~10–30 GB ελεύθερου χώρου στο δίσκο** για τα βάρη του μοντέλου
<!-- @os:end -->
<!-- @os:windows -->
- Ένας υπολογιστής με **Windows 10/11**
- Τουλάχιστον **12 GB RAM** (συνιστώνται 64 GB+ για μεγαλύτερα μοντέλα)
- **~10–30 GB ελεύθερου χώρου στο δίσκο** για τα βάρη του μοντέλου
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Προαιρετικό, για απομόνωση του OpenClaw σε sandbox)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Λήψη και Φόρτωση του Συνιστώμενου Μοντέλου

Το συνιστώμενο μοντέλο για αυτό το playbook είναι το **Qwen3.6-35B-A3B-GGUF** από το Unsloth, ένα ισχυρό μοντέλο MoE με παράθυρο περιβάλλοντος 263k tokens που είναι κατάλληλο για φόρτους εργασίας πράκτορα. Αυτό το μοντέλο χρησιμοποιεί κβαντοποίηση UD-Q4_K_XL. Κατεβάστε το τώρα:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Στη συνέχεια φορτώστε το με μεγάλο παράθυρο περιβάλλοντος και αποθηκεύστε αυτή τη ρύθμιση για μελλοντικές εκτελέσεις:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Το μοντέλο έχει προεπιλεγμένο μήκος περιβάλλοντος 262.144 tokens. Εάν αντιμετωπίσετε σφάλματα εξάντλησης μνήμης (OOM), εξετάστε το ενδεχόμενο μείωσης του παραθύρου περιβάλλοντος. Ωστόσο, επειδή το Qwen3.6 αξιοποιεί το εκτεταμένο περιβάλλον για σύνθετες εργασίες, συνιστούμε να διατηρείτε μήκος περιβάλλοντος τουλάχιστον 128K tokens για να διατηρηθούν οι δυνατότητες σκέψης.

> **Συμβουλή: Απενεργοποιήστε τη σκέψη για ταχύτερες αποκρίσεις πράκτορα:** Το Qwen3.6-35B-A3B εκτελείται σε λειτουργία σκέψης από προεπιλογή, η οποία προσθέτει καθυστέρηση πριν από κάθε απόκριση. Για βρόχους πράκτορα αυτή η επιβάρυνση συσσωρεύεται γρήγορα. Το αποθετήριο [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) παρέχει μια έτοιμη διαμόρφωση που απενεργοποιεί τη σκέψη. Για να τη χρησιμοποιήσετε, κατεβάστε το αρχείο και εισαγάγετέ το:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

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
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
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
model_id = "${openclaw_model}"

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

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
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

## Ρύθμιση του WSL

Εκτελούμε το OpenClaw μέσα στο WSL (Συνιστάται) και το συνδέουμε με τον Lemonade που εκτελείται εγγενώς στα Windows. Αυτό σας παρέχει ένα περιβάλλον Linux shell για το OpenClaw, διατηρώντας παράλληλα την επιτάχυνση GPU του Lemonade στην πλευρά των Windows.

### Εγκατάσταση WSL και Ubuntu

Ανοίξτε το PowerShell ως Διαχειριστής και εγκαταστήστε τον πυρήνα WSL:

```powershell
wsl --install --no-distribution
```

Στη συνέχεια εγκαταστήστε το Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Ενεργοποίηση systemd στο WSL

Εκτελέστε αυτό μέσα στο τερματικό Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Επανεκκινήστε το WSL:

```powershell
wsl --shutdown
wsl
```

### Σύνδεση του Lemonade από τα Windows στο WSL

Το WSL2 εκτελείται σε εικονικό δίκτυο. Ο Lemonade στα Windows δεσμεύεται στο `127.0.0.1`, το οποίο το WSL δεν μπορεί να προσεγγίσει απευθείας. Ένας διακομιστής μεσολάβησης θύρας των Windows προωθεί την κίνηση από τη διεύθυνση IP πύλης WSL στο localhost των Windows.

**Βρείτε τη διεύθυνση IP πύλης WSL** (εκτελέστε μέσα στο WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Προσθέστε τον διακομιστή μεσολάβησης θύρας** (εκτελέστε στο PowerShell ως Διαχειριστής, αντικαθιστώντας το `<WSL-Gateway-IP>` με τη διεύθυνση IP πύλης WSL σας):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Προσθέστε κανόνα τείχους προστασίας** (στο ίδιο PowerShell με αυξημένα δικαιώματα):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Επαλήθευση από το WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Εάν έχετε ήδη φορτώσει το μοντέλο Qwen3.6-35B-A3B-GGUF στο προηγούμενο βήμα, θα πρέπει να δείτε έξοδο JSON ως εξής:

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

> Ο κανόνας `netsh portproxy` επιβιώνει μετά από επανεκκινήσεις, αλλά η διεύθυνση IP πύλης WSL μπορεί να αλλάξει μετά από `wsl --shutdown`. Εάν ο Lemonade καταστεί μη προσβάσιμος από το WSL μετά από επανεκκίνηση, λάβετε την ενημερωμένη διεύθυνση IP πύλης και ενημερώστε τον διακομιστή μεσολάβησης με αυτή τη νέα διεύθυνση IP.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## Εγκατάσταση και Διαμόρφωση του OpenClaw

### Εγκατάσταση του OpenClaw
<!-- @os:windows -->
> Εκτελέστε τις εντολές αυτής της ενότητας μέσα στο **τερματικό WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Η σημαία `--no-onboard` παραλείπει τον διαδραστικό οδηγό εγκατάστασης· θα διαμορφώσετε το backend μοντέλου χειροκίνητα στο επόμενο βήμα, το οποίο σας δίνει ακριβή έλεγχο του ποιου μοντέλου και διακομιστή χρησιμοποιούνται.

Ανοίξτε ένα νέο τερματικό και επιβεβαιώστε την εγκατάσταση:

```bash
openclaw --version
```

> **Συμβουλή:** Εάν δείτε `command not found` μετά την εγκατάσταση, προσθέστε τον καθολικό κατάλογο bin του npm στο PATH σας:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Για να το κάνετε μόνιμο, προσθέστε την παραπάνω γραμμή στο αρχείο `~/.bashrc` ή `~/.zshrc` σας.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->
### Ρύθμιση του OpenClaw για χρήση με Lemonade

Εκτελέστε την μη διαδραστική εισαγωγή του OpenClaw.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

Αυτή η εντολή γράφει τη διαμόρφωση του OpenClaw στο `~/.openclaw/openclaw.json`.

> **Ρύθμιση μεγέθους παραθύρου περιβάλλοντος OpenClaw:** Η συμπίεση του OpenClaw ενεργοποιείται όταν `contextTokens > contextWindow − reserveTokens`. Η προεπιλεγμένη τιμή `reserveTokensFloor` είναι 20.000 tokens, ένα κατώτατο όριο που παρακάμπτει το `reserveTokens` όταν είναι χαμηλότερο, οπότε οποιοδήποτε παράθυρο περιβάλλοντος μοντέλου κάτω από ~37k θα ενεργοποιεί έναν άπειρο βρόχο συμπίεσης. Ορίστε χαμηλό αποθεματικό και απενεργοποιήστε το κατώτατο όριο μία φορά στη διαμόρφωσή σας και εφαρμόζεται σε κάθε μοντέλο, χωρίς ανάγκη ρύθμισης ανά μοντέλο:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> Το `reserveTokensFloor` είναι ένα *κατώτατο όριο* (ελάχιστη προστασία), όχι το ίδιο το αποθεματικό· ο ορισμός μόνο του κατώτατου ορίου δεν έχει αποτέλεσμα. Το `reserveTokensFloor: 0` απενεργοποιεί την προστασία ώστε να γίνεται αποδεκτό το χαμηλότερο `reserveTokens`.
>
> **Πότε να εφαρμόσετε αυτό:** Χρησιμοποιήστε αυτή τη διαμόρφωση εάν το αποτελεσματικό παράθυρο περιβάλλοντος του μοντέλου σας είναι κάτω από ~37k, είτε επειδή το μοντέλο είναι μικρό (π.χ. 8k, 16k, 32k) είτε επειδή το έχετε σκόπιμα περιορίσει σε χαμηλότερη τιμή (π.χ. φόρτωση μοντέλου 128k αλλά ορισμός περιβάλλοντος στα 16k στο Lemonade). Χωρίς αυτό, το OpenClaw εισέρχεται σε άπειρο βρόχο συμπίεσης κατά την εκκίνηση.
>
> **Μοντέλα μεγάλου περιβάλλοντος σε πλήρες περιβάλλον:** Μπορείτε να το παραλείψετε εντελώς. Οι προεπιλογές λειτουργούν καλά, η συμπίεση θα ενεργοποιηθεί πολύ πριν γεμίσει το παράθυρο και το μοντέλο έχει αρκετό χώρο για να δημιουργήσει μεγάλες απαντήσεις. Εάν το εφαρμόσετε, να γνωρίζετε ότι το `reserveTokens: 4096` περιορίζει το μήκος απόκρισης σε ~4k tokens, κάτι που μπορεί να διακόψει τη δημιουργία μεγάλων αρχείων ή λεπτομερών σχεδίων.
>
> **Πού να το προσθέσετε:** Τοποθετήστε το μπλοκ `compaction` μέσα στο `agents.defaults` στο `openclaw.json` σας (συνήθως στο `~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> Το υπόλοιπο της διαμόρφωσής σας (gateway, channels, models κ.λπ.) παραμένει αμετάβλητο, μόνο το κλειδί `compaction` χρειάζεται να προστεθεί.

### (Συνιστάται) Ενεργοποίηση Docker Sandboxing

Το OpenClaw μπορεί να δρομολογεί όλες τις λειτουργίες αρχείων και κώδικα του agent μέσω ενός απομονωμένου Docker container αντί να τις εκτελεί απευθείας στον κεντρικό υπολογιστή σας. Αυτό περιορίζει τον αντίκτυπο οποιασδήποτε ακούσιας ενέργειας στο sandbox, αφήνοντας ανέπαφα το σύστημα αρχείων και το δίκτυο του κεντρικού υπολογιστή σας.

Δημιουργήστε την εικόνα sandbox μία φορά (το Docker πρέπει να είναι εγκατεστημένο):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Εκτελέστε αυτό για να προσθέσετε το κλειδί `sandbox` μέσα στο υπάρχον μπλοκ `agents.defaults` στο `~/.openclaw/openclaw.json`:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

Τα containers sandbox δεν έχουν **πρόσβαση στο δίκτυο** από προεπιλογή. Δείτε την [αναφορά sandboxing](https://docs.openclaw.ai/gateway/sandboxing) για bind mounts και παρακάμψεις δικτύου.

> #### Αντιμετώπιση προβλημάτων: Docker Permission Denied
> 
> Εάν λάβετε "permission denied" κατά την εκτέλεση εντολών Docker:
> 
> **Βήμα 1: Προσθέστε τον χρήστη σας στην ομάδα docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Βήμα 2: Εάν το σφάλμα επιμένει, εφαρμόστε τη μόνιμη διόρθωση**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Στη συνέχεια **επανεκκινήστε** το σύστημά σας.
> 
> **Γρήγορη προσωρινή διόρθωση** (επαναφέρεται μετά την επανεκκίνηση):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

### Εκκίνηση του OpenClaw Gateway

Το gateway είναι η διεργασία OpenClaw που διαχειρίζεται τον βρόχο agent και εξυπηρετεί τον πίνακα ελέγχου:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

Για να ανοίξετε τον πίνακα ελέγχου, εκτελέστε αυτό σε ένα δεύτερο τερματικό ενώ το gateway εξακολουθεί να εκτελείται:

```bash
openclaw dashboard
```

Επειδή το gateway δεσμεύεται στο loopback, ο πίνακας ελέγχου πραγματοποιεί αυτόματη αυθεντικοποίηση όταν ανοίγεται από το ίδιο μηχάνημα, χωρίς να απαιτείται εισαγωγή token ή έγκριση συσκευής για τοπική πρόσβαση. Θα πρέπει να δείτε τον πίνακα ελέγχου OpenClaw με το μοντέλο Lemonade σας να εμφανίζεται ως ενεργό backend.

> Εάν έχετε ενεργοποιήσει το sandboxing, μπορείτε να το επαληθεύσετε ζητώντας από τον agent να `run hostname` από τον πίνακα ελέγχου. Εάν δείτε ένα σύντομο αναγνωριστικό container αντί για το hostname του μηχανήματός σας, το sandbox λειτουργεί.

**Συγχαρητήρια, έχετε δημιουργήσει μια πλήρως τοπική στοίβα AI agent από την αρχή.**

> **Χρειάζεστε το token gateway;** Εκτελέστε `openclaw dashboard --no-open` για να εκτυπώσετε τη διεύθυνση URL του πίνακα ελέγχου με το token ενσωματωμένο (επίσης προσπαθεί να το αντιγράψει στο πρόχειρό σας). Εναλλακτικά, το token βρίσκεται στο `gateway.auth.token` στο `~/.openclaw/openclaw.json`.
>
> **Έγκριση απομακρυσμένης συσκευής:** Όταν ανοίγετε τον πίνακα ελέγχου από ένα δεύτερο μηχάνημα ή τηλέφωνο, το πρόγραμμα περιήγησης εμφανίζει ένα αναγνωριστικό αιτήματος. Στο μηχάνημα που εκτελεί το gateway, εκτελέστε:
> ```bash
> openclaw devices approve <requestId>
> ```
> Αυτό απαιτείται μόνο για απομακρυσμένες ή δευτερεύουσες συσκευές· η πρόσβαση loopback από το ίδιο μηχάνημα πραγματοποιεί αυτόματη αυθεντικοποίηση.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Προαιρετικό: Σύνδεση Καναλιού Επικοινωνίας

Μόλις το gateway εκτελείται, μπορείτε να προσεγγίσετε τον τοπικό agent σας από οποιαδήποτε συσκευή. Επιλέξτε την επιλογή που ταιριάζει στη ρύθμισή σας. Το OpenClaw υποστηρίζει [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) και άλλα κανάλια· δείτε την πλήρη λίστα στο [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Επιλογή Α: Discord

Το Discord απαιτεί έναν διακομιστή όπου **έχετε πρόσβαση διαχειριστή** για να προσθέσετε ένα bot. Εάν μοιράζεστε διακομιστές αλλά δεν είστε ιδιοκτήτης κανενός, χρησιμοποιήστε αντ' αυτού την Επιλογή Β (Telegram).
#### Δημιουργία λογαριασμού και διακομιστή Discord

Εάν δεν έχετε λογαριασμό Discord, εγγραφείτε στο [discord.com](https://discord.com). Χρειάζεστε επίσης έναν διακομιστή όπου είστε διαχειριστής· δημιουργήστε έναν κάνοντας κλικ στο εικονίδιο **+** στην πλαϊνή μπάρα του Discord και επιλέγοντας **Create My Own**. Ένας ιδιωτικός διακομιστής είναι κατάλληλος.

#### Δημιουργία εφαρμογής και bot Discord

1. Μεταβείτε στο [Discord Developer Portal](https://discord.com/developers/applications) και κάντε κλικ στο **New Application**. Δώστε του ένα όνομα (π.χ. "openclaw-bot").
2. Στην πλαϊνή μπάρα, κάντε κλικ στο **Bot**. Ορίστε ένα όνομα χρήστη για το bot.
3. Παραμένοντας στη σελίδα Bot, μετακινηθείτε προς τα κάτω στο **Privileged Gateway Intents** και ενεργοποιήστε:
   - **Message Content Intent** (απαιτείται)
   - **Server Members Intent** (συνιστάται)
4. Μετακινηθείτε πάλι προς τα πάνω και κάντε κλικ στο **Reset Token** για να δημιουργήσετε το token του bot σας. Αντιγράψτε το.

#### Προσθήκη του bot στον διακομιστή σας

1. Στην πλαϊνή μπάρα, κάντε κλικ στο **OAuth2/ URL Generator**.
2. Στην ενότητα **Scopes**, ενεργοποιήστε `bot` και `applications.commands`.
3. Στην ενότητα **Bot Permissions**, ενεργοποιήστε: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Αντιγράψτε τη δημιουργημένη διεύθυνση URL, επικολλήστε την στο πρόγραμμα περιήγησής σας, επιλέξτε τον διακομιστή σας και επιβεβαιώστε. Το bot θα πρέπει τώρα να εμφανίζεται στη λίστα μελών του διακομιστή σας.

#### Συλλογή των αναγνωριστικών σας

Ενεργοποιήστε τη Λειτουργία Προγραμματιστή στο Discord (**User Settings/ Advanced/ Developer Mode**), και στη συνέχεια:
- Κάντε δεξί κλικ στο εικονίδιο του διακομιστή σας: **Copy Server ID**
- Κάντε δεξί κλικ στο δικό σας avatar: **Copy User ID**

#### Να επιτρέπονται τα DM από μέλη του διακομιστή

Κάντε δεξί κλικ στο εικονίδιο του διακομιστή σας/ **Privacy Settings**/ ενεργοποιήστε τα **Direct Messages**. Αυτό επιτρέπει στο bot να σας στέλνει DM, κάτι που απαιτείται για το βήμα σύζευξης.

#### Ρύθμιση παραμέτρων του OpenClaw για Discord

Αποθηκεύστε το token του bot σας ως μεταβλητή περιβάλλοντος, και στη συνέχεια δημιουργήστε ένα μεμονωμένο αρχείο patch που ενεργοποιεί το Discord, αναφέρεται στο token και προσθέτει τον διακομιστή σας στη λίστα επιτρεπόμενων. Αντικαταστήστε τα `<server_id>` και `<user_id>` με τα αναγνωριστικά που συλλέξατε παραπάνω.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **Μην βασίζεστε στο να ζητάτε από τον πράκτορα να το ρυθμίσει αυτό.** Όταν είναι ενεργοποιημένο το sandboxing, ο πράκτορας δεν μπορεί να γράψει στο `~/.openclaw/openclaw.json` από μέσα του sandbox· χρησιμοποιήστε αντ' αυτού τις παραπάνω εντολές CLI στον κεντρικό υπολογιστή.

Επανεκκινήστε το gateway ώστε να ανακτήσει τη νέα ρύθμιση καναλιού:

```bash
openclaw gateway run --bind loopback --port 18789
```

Θα πρέπει να δείτε `logged in to discord as <bot-name>` στην έξοδο του gateway μέσα σε λίγα δευτερόλεπτα.

#### Σύζευξη του λογαριασμού σας στο Discord

Στείλτε DM στο bot στο Discord. Θα απαντήσει με έναν σύντομο κωδικό σύζευξης.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Εγκρίνετέ τον στο μηχάνημα που εκτελεί το OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Οι κωδικοί σύζευξης λήγουν μετά από μία ώρα.

Μπορείτε τώρα να συνομιλείτε με τον πράκτορά σας απευθείας από το Discord και να αναθέτετε εργασίες στο τοπικό σας υλικό.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Επιλογή Β: Telegram

Το Telegram είναι απλούστερο από το Discord για τους περισσότερους χρήστες· δεν απαιτεί διακομιστή ούτε δικαιώματα διαχειριστή.

#### Δημιουργία bot Telegram

1. Ανοίξτε το Telegram και στείλτε μήνυμα στον **@BotFather**.
2. Στείλτε `/newbot` και ακολουθήστε τις οδηγίες. Αποθηκεύστε το token του bot που σας δίνει.

#### Ρύθμιση παραμέτρων του OpenClaw για Telegram

Αποθηκεύστε το token ως μεταβλητή περιβάλλοντος:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Προσθέστε τη ρύθμιση καναλιού στο `~/.openclaw/openclaw.json` (ή εφαρμόστε patch μέσω του dashboard):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

Επανεκκινήστε το gateway, και στη συνέχεια στείλτε οποιοδήποτε μήνυμα στο bot σας στο Telegram. Εγκρίνετε τη σύζευξη:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Οι κωδικοί σύζευξης λήγουν μετά από μία ώρα. Μπορείτε τώρα να συνομιλείτε με τον πράκτορά σας μέσω DM στο Telegram.

---

## Επόμενα Βήματα

Τώρα που ο πράκτοράς σας μπορεί να λαμβάνει εντολές από το τηλέφωνό σας και να ενεργεί στο τοπικό σας μηχάνημα, αξίζει να εξερευνήσετε τρεις κατευθύνσεις:

1. **Συνοπτική παρουσίαση χρηματιστηρίου**: Προγραμματίστε το OpenClaw να ανακτά δεδομένα από χρηματοοικονομικά API σε σταθερό χρονικό διάστημα, να συνοψίζει τις κινήσεις της ημέρας με το τοπικό σας μοντέλο και να αποστέλλει μια περίληψη στο τηλέφωνό σας κάθε πρωί μέσω του επιλεγμένου καναλιού σας.

2. **Παρακολούθηση fine-tuning**: Εκκινήστε μια εργασία εκπαίδευσης εξ αποστάσεως μέσω Telegram ή Discord, και στη συνέχεια αφήστε τον πράκτορα να παρακολουθεί το αρχείο καταγραφής εκπαίδευσης και να αναφέρει περιοδικές τιμές απώλειας, χρήση GPU και χρήση δίσκου πίσω στο τηλέφωνό σας. Εάν η εκτέλεση σταματήσει ή η VRAM αυξηθεί απότομα, θα το μάθετε αμέσως χωρίς να χρειαστεί να βρίσκεστε μπροστά στο μηχάνημα.

3. **IOT με τοπικό VLM**: Στρέψτε μια κάμερα στην μπροστινή πόρτα σας, εκτελέστε ένα μοντέλο όρασης στο Lemonade και αφήστε το OpenClaw να αναλύει καρέ κατ' απαίτηση ή βάσει ενεργοποιητή. Ρωτήστε "έφτασαν σήμερα πακέτα;" από το τηλέφωνό σας και λάβετε μια άμεση απάντηση από το δικό σας υλικό.