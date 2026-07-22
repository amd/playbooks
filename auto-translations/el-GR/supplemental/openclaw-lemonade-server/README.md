<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Αυτόματη μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει επανεξεταστεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένα βήματα, εντολές, λήψεις ή η διαθεσιμότητα προϊόντων μπορεί να διαφέρουν στη γλώσσα ή την περιοχή σας. Εάν κάτι φαίνεται λανθασμένο, θεωρήστε το πρωτότυπο αγγλικό playbook ως την πηγή αλήθειας.
<!-- auto-translated-disclaimer:end -->

# Εκτέλεση του OpenClaw με τον Lemonade Server ως backend

## Επισκόπηση

Το [**OpenClaw**](https://openclaw.ai/) είναι ένας αυτόνομος πράκτορας AI που μπορεί να γράφει και να εκτελεί κώδικα, να διαχειρίζεται αρχεία και να επεξεργάζεται πολύπλοκες, πολυβηματικές εργασίες για λογαριασμό σας. Σε αντίθεση με έναν βοηθό συνομιλίας που απλώς απαντά σε ερωτήσεις, το OpenClaw εκτελεί πραγματικές ενέργειες στο σύστημά σας, κάτι που σημαίνει ότι χρειάζεται ένα γρήγορο, ικανό backend AI που να μπορεί να ανταποκριθεί σε έναν απαιτητικό βρόχο πράκτορα (agent loop).

Ο [**Lemonade Server**](https://lemonade-server.ai/) είναι αυτό το backend. Πρόκειται για έναν ανοιχτού κώδικα τοπικό server συμπερασμού (inference) που εκτελεί μοντέλα GenAI απευθείας στο υλικό σας και τα εκθέτει μέσω του βιομηχανικού προτύπου OpenAI API.

Μαζί, σχηματίζουν μια πλήρως τοπική στοίβα πράκτορα AI: ο Lemonade χειρίζεται το συμπέρασμα μοντέλου, ενώ το OpenClaw παρέχει τον βρόχο πράκτορα που μετατρέπει τις εξόδους του μοντέλου σε πραγματικές ενέργειες.

> **Πριν συνεχίσετε:** Το OpenClaw είναι ένας εξαιρετικά αυτόνομος πράκτορας AI. Η παροχή πρόσβασης σε οποιονδήποτε πράκτορα AI στο σύστημά σας ενδέχεται να οδηγήσει σε απρόβλεπτα ή ανεπιθύμητα αποτελέσματα. Προχωρήστε μόνο εάν κατανοείτε τους κινδύνους και αισθάνεστε άνετα με το να ενεργεί αυτόνομο λογισμικό για λογαριασμό σας.

---

## Τι Θα Μάθετε

Μέχρι το τέλος αυτού του οδηγού θα μπορείτε να:

- Μάθετε για τον **Lemonade Server**
- **Εγκαταστήσετε το OpenClaw** και το **κατευθύνετε προς τον Lemonade Server** ως backend AI του.
- **Ξεκινήσετε το gateway του OpenClaw** και επιβεβαιώσετε ότι ο πράκτοράς σας είναι έτοιμος να εργαστεί.
- **Συνδέσετε ένα κανάλι επικοινωνίας** (Discord ή Telegram) ώστε να μπορείτε να συνομιλείτε με τον πράκτορά σας από οποιαδήποτε συσκευή.

---

## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενων Λογισμικού

<!-- @os:linux -->
- Ένας υπολογιστής που εκτελεί **Ubuntu 24.04+** ή μια συμβατή διανομή Linux με βάση το Debian με `apt-get`
- Τουλάχιστον **12 GB RAM** (συνιστάται 64 GB+ για μεγαλύτερα μοντέλα)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Προαιρετικό, για sandboxing του OpenClaw)

- **~10–30 GB ελεύθερου χώρου στον δίσκο** για τα βάρη μοντέλου
<!-- @os:end -->
<!-- @os:windows -->
- Ένας υπολογιστής που εκτελεί **Windows 10/11**
- Τουλάχιστον **12 GB RAM** (συνιστάται 64 GB+ για μεγαλύτερα μοντέλα)
- **~10–30 GB ελεύθερου χώρου στον δίσκο** για τα βάρη μοντέλου
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Προαιρετικό, για sandboxing του OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Λήψη και Φόρτωση του Προτεινόμενου Μοντέλου

Το προτεινόμενο μοντέλο για αυτόν τον οδηγό είναι το **Qwen3.6-35B-A3B-GGUF** από το Unsloth, ένα ισχυρό μοντέλο MoE με παράθυρο πλαισίου 263k tokens που είναι κατάλληλο για φόρτους εργασίας πρακτόρων. Αυτό το μοντέλο χρησιμοποιεί κβαντισμό UD-Q4_K_XL. Κάντε λήψη τώρα:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Στη συνέχεια, φορτώστε το με ένα μεγάλο παράθυρο πλαισίου και αποθηκεύστε αυτή τη ρύθμιση για μελλοντικές εκτελέσεις:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Το μοντέλο έχει προεπιλεγμένο μήκος πλαισίου 262.144 tokens. Εάν αντιμετωπίσετε σφάλματα εξάντλησης μνήμης (OOM), εξετάστε το ενδεχόμενο μείωσης του παραθύρου πλαισίου. Ωστόσο, επειδή το Qwen3.6 αξιοποιεί το εκτεταμένο πλαίσιο για πολύπλοκες εργασίες, συνιστούμε τη διατήρηση μήκους πλαισίου τουλάχιστον 128K tokens ώστε να διατηρηθούν οι δυνατότητες σκέψης.

> **Συμβουλή: Απενεργοποιήστε τη σκέψη για ταχύτερες αποκρίσεις πράκτορα:** Το Qwen3.6-35B-A3B εκτελείται σε λειτουργία σκέψης από προεπιλογή, κάτι που προσθέτει καθυστέρηση πριν από κάθε απόκριση. Για βρόχους πρακτόρων, αυτή η επιβάρυνση συσσωρεύεται γρήγορα. Το αποθετήριο [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) παρέχει μια έτοιμη διαμόρφωση που απενεργοποιεί τη σκέψη. Για να τη χρησιμοποιήσετε, κάντε λήψη του αρχείου και εισαγάγετέ το:
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

Εκτελούμε το OpenClaw μέσα στο WSL (Προτείνεται) και το συνδέουμε με τον Lemonade που εκτελείται εγγενώς στα Windows. Αυτό σας δίνει ένα περιβάλλον κελύφους Linux για το OpenClaw, διατηρώντας παράλληλα την επιτάχυνση GPU του Lemonade στην πλευρά των Windows.

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

### Γεφύρωση του Lemonade από τα Windows στο WSL

Το WSL2 εκτελείται σε ένα εικονικό δίκτυο. Ο Lemonade στα Windows συνδέεται στο `127.0.0.1`, το οποίο το WSL δεν μπορεί να προσπελάσει απευθείας. Ένα port proxy των Windows προωθεί την κίνηση από τη διεύθυνση IP της πύλης WSL στο localhost των Windows.

**Βρείτε τη διεύθυνση IP της πύλης WSL** (εκτελέστε μέσα στο WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Προσθέστε το port proxy** (εκτελέστε στο PowerShell ως Διαχειριστής, αντικαθιστώντας το `<WSL-Gateway-IP>` με τη διεύθυνση IP της πύλης WSL σας):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Προσθέστε έναν κανόνα τείχους προστασίας** (στο ίδιο ανυψωμένο PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Επαληθεύστε από το WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Εάν έχετε ήδη φορτώσει το μοντέλο Qwen3.6-35B-A3B-GGUF στο προηγούμενο βήμα, θα πρέπει να δείτε έξοδο JSON όπως αυτή:

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

> Ο κανόνας `netsh portproxy` επιβιώνει τις επανεκκινήσεις, αλλά η διεύθυνση IP της πύλης WSL μπορεί να αλλάξει μετά από `wsl --shutdown`. Εάν ο Lemonade γίνει μη προσβάσιμος από το WSL μετά από επανεκκίνηση, λάβετε την ενημερωμένη διεύθυνση IP πύλης και ενημερώστε το proxy με τη νέα διεύθυνση IP.

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

## Εγκατάσταση και Ρύθμιση του OpenClaw

### Εγκατάσταση του OpenClaw
<!-- @os:windows -->
> Εκτελέστε τις εντολές αυτής της ενότητας μέσα στο **τερματικό WSL** σας.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Η σημαία `--no-onboard` παραλείπει τον διαδραστικό οδηγό εγκατάστασης· θα διαμορφώσετε το backend μοντέλου χειροκίνητα στο επόμενο βήμα, κάτι που σας δίνει ακριβή έλεγχο του ποιο μοντέλο και server χρησιμοποιούνται.

Ανοίξτε ένα νέο τερματικό και επιβεβαιώστε την εγκατάσταση:

```bash
openclaw --version
```

> **Συμβουλή:** Εάν δείτε `command not found` μετά την εγκατάσταση, προσθέστε τον κατάλογο global bin του npm στο PATH:
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
### Διαμόρφωση του OpenClaw για Χρήση του Lemonade

Εκτελέστε την μη διαδραστική ενσωμάτωση (onboarding) του OpenClaw.
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

Αυτή η εντολή εγγράφει τη διαμόρφωση του OpenClaw στο `~/.openclaw/openclaw.json`.

> **Μέγεθος παραθύρου περιεχομένου (context window) του OpenClaw:** Η συμπύκνωση (compaction) του OpenClaw ενεργοποιείται όταν `contextTokens > contextWindow − reserveTokens`. Η προεπιλεγμένη τιμή του `reserveTokensFloor` είναι 20.000 tokens, ένα κατώτατο όριο που υπερισχύει του `reserveTokens` όταν αυτό είναι χαμηλότερο, οπότε οποιοδήποτε παράθυρο περιεχομένου μοντέλου κάτω από περίπου 37k θα προκαλέσει έναν ατέρμονο βρόχο συμπύκνωσης. Ορίστε μια χαμηλή τιμή εφεδρείας (reserve) και απενεργοποιήστε το κατώτατο όριο μία φορά στη διαμόρφωσή σας και θα ισχύει για κάθε μοντέλο, χωρίς να χρειάζεται ρύθμιση ανά μοντέλο:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> Το `reserveTokensFloor` είναι ένα *κατώτατο όριο* (ελάχιστη διασφάλιση), όχι το ίδιο το reserve, ο ορισμός μόνο του κατώτατου ορίου δεν έχει καμία επίδραση. Το `reserveTokensFloor: 0` απενεργοποιεί τη διασφάλιση, ώστε να γίνεται αποδεκτό το χαμηλότερο `reserveTokens`.
>
> **Πότε να εφαρμόσετε αυτή τη ρύθμιση:** Χρησιμοποιήστε αυτή τη διαμόρφωση εάν το πραγματικό παράθυρο περιεχομένου του μοντέλου σας είναι κάτω από περίπου 37k, είτε επειδή το μοντέλο είναι μικρό (π.χ. 8k, 16k, 32k) είτε επειδή το έχετε σκόπιμα περιορίσει σε χαμηλότερη τιμή (π.χ. φόρτωση ενός μοντέλου 128k αλλά ρύθμιση του περιεχομένου στα 16k στο Lemonade). Χωρίς αυτή τη ρύθμιση, το OpenClaw εισέρχεται σε ατέρμονο βρόχο συμπύκνωσης κατά την εκκίνηση.
>
> **Μοντέλα μεγάλου παραθύρου περιεχομένου σε πλήρη χωρητικότητα:** Μπορείτε να παραλείψετε εντελώς αυτό το βήμα. Οι προεπιλεγμένες ρυθμίσεις λειτουργούν καλά, η συμπύκνωση θα ενεργοποιηθεί πολύ πριν γεμίσει το παράθυρο και το μοντέλο θα έχει άφθονο χώρο για να δημιουργήσει μεγάλες απαντήσεις. Εάν την εφαρμόσετε παρόλα αυτά, λάβετε υπόψη ότι το `reserveTokens: 4096` περιορίζει το μήκος της απάντησης σε περίπου 4k tokens, κάτι που μπορεί να διακόψει τη δημιουργία μεγάλων αρχείων ή λεπτομερών σχεδίων.
>
> **Πού να το προσθέσετε:** Τοποθετήστε το μπλοκ `compaction` μέσα στο `agents.defaults` στο αρχείο `openclaw.json` (συνήθως στο `~/.openclaw/openclaw.json`):
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
> Το υπόλοιπο της διαμόρφωσής σας (gateway, channels, models, κ.λπ.) παραμένει αμετάβλητο, χρειάζεται να προστεθεί μόνο το κλειδί `compaction`.

### (Συνιστάται) Ενεργοποίηση Sandboxing μέσω Docker

Το OpenClaw μπορεί να δρομολογήσει όλες τις λειτουργίες αρχείων και κώδικα του πράκτορα μέσω ενός απομονωμένου container Docker αντί να τις εκτελεί απευθείας στον υπολογιστή σας. Αυτό περιορίζει την ακτίνα επίδρασης οποιασδήποτε ανεπιθύμητης ενέργειας στο sandbox, αφήνοντας ανέπαφο το σύστημα αρχείων και το δίκτυο του κεντρικού υπολογιστή σας.

Δημιουργήστε την εικόνα (image) του sandbox μία φορά (το Docker πρέπει να είναι εγκατεστημένο):

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

Εκτελέστε το παρακάτω για να προσθέσετε το κλειδί `sandbox` μέσα στο υπάρχον μπλοκ `agents.defaults` στο `~/.openclaw/openclaw.json`:

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

Τα containers του sandbox **δεν έχουν πρόσβαση στο δίκτυο** από προεπιλογή. Δείτε την [τεκμηρίωση αναφοράς sandboxing](https://docs.openclaw.ai/gateway/sandboxing) για τις προσαρτήσεις (bind mounts) και τις παρακάμψεις δικτύου.

> #### Αντιμετώπιση προβλημάτων: Άρνηση Δικαιώματος Docker
> 
> Εάν λάβετε το μήνυμα "permission denied" κατά την εκτέλεση εντολών Docker:
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
> Στη συνέχεια, **επανεκκινήστε** το σύστημά σας.
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

<!-- @os:linux -->
## (Συνιστάται) Ενσωμάτωση του OpenClaw με Υπηρεσίες Firecrawl

Το [Firecrawl](https://docs.firecrawl.dev/introduction) παρέχει μια αυτοφιλοξενούμενη υπηρεσία σάρωσης ιστού και εξαγωγής περιεχομένου που μπορεί να παρακάμψει αυτές τις προκλήσεις και να ξεκλειδώσει το πλήρες δυναμικό της αυτοματοποίησης του OpenClaw.

Σε αυτή τη ρύθμιση, το OpenClaw εκτελείται ως ένα σύνολο containers Docker που διαχειρίζονται μέσω του Podman. Για να απλοποιήσουμε τη διαχείριση του κύκλου ζωής και την αυτόματη εκκίνηση, καταχωρούμε το Firecrawl ως υπηρεσία `systemd` σε επίπεδο χρήστη που ενορχηστρώνει το υποκείμενο στοίβαγμα (stack) Podman Compose. Αυτό επιτρέπει στο OpenClaw να εκκινεί το gateway, να σταματά και να επαληθεύει την υπηρεσία Firecrawl χρησιμοποιώντας τυπικές εντολές `systemctl --user` αντί να αλληλεπιδρά απευθείας με τα containers.

Για να το κρατήσουμε απλό, έχουμε χωρίσει ολόκληρη τη διαδικασία σε τέσσερα βήματα:

---

### 1. Καταχώρηση της υπηρεσίας συστήματος
Μεταβείτε στον κατάλογο διαμόρφωσης χρήστη του systemd:
```bash
cd ~/.config/systemd/user
```
Δημιουργήστε και ανοίξτε ένα νέο αρχείο με το όνομα `firecrawl.service`.
```bash
nano firecrawl.service
```
Αντιγράψτε και επικολλήστε την ακόλουθη διαμόρφωση:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
Σε αυτό το σημείο, η υπηρεσία έχει οριστεί αλλά δεν έχει ακόμη καταχωρηθεί στο `systemd`. 
Βεβαιωθείτε ότι το όνομα αρχείου ταιριάζει ακριβώς με αυτό που δημιουργήσατε παραπάνω και, στη συνέχεια, εκτελέστε:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Εάν είναι επιτυχής, θα πρέπει να δείτε την ακόλουθη έξοδο:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 Ο κατάλογος `default.target.wants/` περιέχει συμβολικούς συνδέσμους προς υπηρεσίες που έχουν διαμορφωθεί να εκκινούν αυτόματα.
### 2. Διαμόρφωση του Firecrawl

Το [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) είναι ιδανικό για όσους χρειάζονται πλήρη έλεγχο των περιβαλλόντων scraping και επεξεργασίας δεδομένων τους, αλλά έρχεται με το κόστος επιπλέον προσπάθειας συντήρησης και διαμόρφωσης.

Ξεκινήστε κλωνοποιώντας το αποθετήριο:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Δημιουργήστε το `.env` στον ριζικό κατάλογο `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Ανάπτυξη του OpenClaw με το Podman Compose

Πριν προχωρήσετε, βεβαιωθείτε ότι έχετε κατεβάσει την πιο πρόσφατη εικόνα Docker του OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Μόλις ολοκληρωθεί αυτό, κατεβάστε το αρχείο Compose του OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) και τοποθετήστε το στον ριζικό κατάλογο `/firecrawl`:

> Αυτή η σύμβαση απαιτείται ώστε το `systemd` να μπορεί να εντοπίσει και να εκκινήσει την υπηρεσία σωστά, όπως ορίζεται στο `WorkingDirectory=${HOME}/firecrawl`.

> Μπορείτε πάντα να επεκτείνετε το stack προσθέτοντας επιπλέον υπηρεσίες Firecrawl όπως χρειάζεται. Η πλήρης λίστα των διαθέσιμων υπηρεσιών βρίσκεται στο επίσημο [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Εκκίνηση της υπηρεσίας OpenClaw μέσω του Firecrawl 

Πριν παραδώσετε τον έλεγχο στο `systemd`, επιβεβαιώστε ότι όλα λειτουργούν σωστά εκτελώντας το stack χειροκίνητα:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Αν όλα έχουν διαμορφωθεί σωστά, θα πρέπει να δείτε το container του OpenClaw να ανεβαίνει και η έξοδος της γραμμής εντολών σας θα πρέπει να μοιάζει με αυτό:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Μόλις επαληθευτεί, τερματίστε το stack πριν προχωρήσετε:
```bash
podman compose -f openclaw-compose.yaml down
```
Πριν ξεκινήσετε την υπηρεσία, πρέπει να βεβαιωθείτε ότι έχουν οριστεί η σωστή ιδιοκτησία και τα σωστά δικαιώματα στον κατάλογο `firecrawl` και στο αρχείο `.env` του. 
Αυτό είναι απαραίτητο ώστε η υπηρεσία να μπορεί να γράψει τα διαπιστευτήριά σας κατά την εκκίνηση.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Τώρα που όλα έχουν επαληθευτεί, ξεκινήστε την υπηρεσία μέσω του `systemd`:
```bash
systemctl --user start firecrawl.service
```
Οι [Ενέργειες του OpenClaw](https://docs.openclaw.ai/) είναι προσβάσιμες μέσα από το διαδραστικό container, και ο Πίνακας Ελέγχου Web είναι διαθέσιμος στον ίδιο host και port στο http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Απόκτηση του δικού σας `OPENCLAW_GATEWAY_TOKEN`

Μόλις η υπηρεσία τεθεί σε λειτουργία, θα παρατηρήσετε έναν νέο κατάλογο `.openclaw` να δημιουργείται στον φάκελο του χρήστη σας (~/.openclaw). Αυτός ο κατάλογος είναι κλειδωμένος από προεπιλογή, οπότε θα χρειαστεί να τον ξεκλειδώσετε για να ανακτήσετε το token πύλης σας.

1. Παραχωρήστε πρόσβαση στον κατάλογο:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Διαβάστε το token πύλης σας:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Εντοπίστε την τιμή `OPENCLAW_GATEWAY_TOKEN` στην έξοδο.

3. Ανοίξτε τον πίνακα ελέγχου πύλης στο πρόγραμμα περιήγησής σας στη διεύθυνση http://127.0.0.1:18789. Επικολλήστε το token σας όταν σας ζητηθεί για ταυτοποίηση.

Για να διακόψετε την υπηρεσία, εκτελέστε:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Εκκίνηση της Πύλης OpenClaw

Η πύλη είναι η διεργασία του OpenClaw που διαχειρίζεται τον βρόχο του agent και εξυπηρετεί τον πίνακα ελέγχου:

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

Για να ανοίξετε τον πίνακα ελέγχου, εκτελέστε αυτό σε ένα δεύτερο τερματικό ενώ η πύλη εξακολουθεί να εκτελείται:

```bash
openclaw dashboard
```

Επειδή η πύλη συνδέεται στο loopback, ο πίνακας ελέγχου αυθεντικοποιείται αυτόματα όταν ανοίγει από τον ίδιο υπολογιστή, δεν χρειάζεται εισαγωγή token ή έγκριση συσκευής για τοπική πρόσβαση. Θα πρέπει να δείτε τον πίνακα ελέγχου του OpenClaw με το μοντέλο Lemonade σας να εμφανίζεται ως το ενεργό backend.

> Αν έχετε ενεργοποιήσει το sandboxing, μπορείτε να το επαληθεύσετε ζητώντας από τον agent να εκτελέσει `run hostname` από τον πίνακα ελέγχου. Αν δείτε ένα σύντομο container ID αντί για το hostname του υπολογιστή σας, το sandbox λειτουργεί.

**Συγχαρητήρια, δημιουργήσατε ένα πλήρως τοπικό AI agent stack από την αρχή.**

> **Χρειάζεστε το token πύλης;** Εκτελέστε `openclaw dashboard --no-open` για να εκτυπώσετε τη διεύθυνση URL του πίνακα ελέγχου με το token ενσωματωμένο (επίσης προσπαθεί να το αντιγράψει στο πρόχειρό σας). Εναλλακτικά, το token βρίσκεται στο `gateway.auth.token` μέσα στο `~/.openclaw/openclaw.json`.
>
> **Έγκριση απομακρυσμένης συσκευής:** Όταν ανοίγετε τον πίνακα ελέγχου από έναν δεύτερο υπολογιστή ή κινητό, το πρόγραμμα περιήγησης εμφανίζει ένα request ID. Πίσω στον υπολογιστή που εκτελεί την πύλη, εκτελέστε:
> ```bash
> openclaw devices approve <requestId>
> ```
> Αυτό χρειάζεται μόνο για απομακρυσμένες ή δευτερεύουσες συσκευές, η πρόσβαση loopback από τον ίδιο υπολογιστή αυθεντικοποιείται αυτόματα.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Προαιρετικό: Σύνδεση Καναλιού Επικοινωνίας

Μόλις η πύλη εκτελείται, μπορείτε να προσεγγίσετε τον τοπικό agent σας από οποιαδήποτε συσκευή. Επιλέξτε την επιλογή που ταιριάζει στη ρύθμισή σας. Το OpenClaw υποστηρίζει [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), και άλλα κανάλια, δείτε την πλήρη λίστα στο [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Επιλογή Α: Discord

Το Discord απαιτεί έναν server όπου **έχετε δικαιώματα διαχειριστή** για να προσθέσετε ένα bot. Αν μοιράζεστε servers αλλά δεν κατέχετε κάποιον, χρησιμοποιήστε την Επιλογή Β (Telegram) αντ' αυτού.

#### Δημιουργία λογαριασμού και server στο Discord

Αν δεν έχετε λογαριασμό Discord, εγγραφείτε στο [discord.com](https://discord.com). Χρειάζεστε επίσης έναν server όπου είστε διαχειριστής, δημιουργήστε έναν κάνοντας κλικ στο εικονίδιο **+** στην πλαϊνή στήλη του Discord και επιλέγοντας **Create My Own**. Ένας ιδιωτικός server είναι αρκετός.

#### Δημιουργία εφαρμογής και bot στο Discord

1. Μεταβείτε στο [Discord Developer Portal](https://discord.com/developers/applications) και κάντε κλικ στο **New Application**. Δώστε του ένα όνομα (π.χ. "openclaw-bot").
2. Στην πλαϊνή στήλη, κάντε κλικ στο **Bot**. Ορίστε ένα username για το bot.
3. Ακόμα στη σελίδα Bot, μεταβείτε στο **Privileged Gateway Intents** και ενεργοποιήστε:
   - **Message Content Intent** (απαραίτητο)
   - **Server Members Intent** (συνιστάται)
4. Επιστρέψτε προς τα πάνω και κάντε κλικ στο **Reset Token** για να δημιουργήσετε το token του bot σας. Αντιγράψτε το.

#### Προσθήκη του bot στον server σας

1. Στην πλαϊνή στήλη, κάντε κλικ στο **OAuth2/ URL Generator**.
2. Κάτω από το **Scopes**, ενεργοποιήστε τα `bot` και `applications.commands`.
3. Κάτω από το **Bot Permissions**, ενεργοποιήστε: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Αντιγράψτε τη διεύθυνση URL που δημιουργήθηκε, επικολλήστε την στο πρόγραμμα περιήγησής σας, επιλέξτε τον server σας και επιβεβαιώστε. Το bot θα πρέπει τώρα να εμφανίζεται στη λίστα μελών του server σας.
#### Συλλέξτε τα IDs σας

Ενεργοποιήστε τη λειτουργία Developer Mode στο Discord (**User Settings/ Advanced/ Developer Mode**), και στη συνέχεια:
- Κάντε δεξί κλικ στο εικονίδιο του server σας: **Copy Server ID**
- Κάντε δεξί κλικ στο δικό σας avatar: **Copy User ID**

#### Επιτρέψτε τα DMs από μέλη του server

Κάντε δεξί κλικ στο εικονίδιο του server σας/ **Privacy Settings**/ ενεργοποιήστε το **Direct Messages**. Αυτό επιτρέπει στο bot να σας στείλει DM, κάτι που απαιτείται για το βήμα της σύζευξης (pairing).

#### Ρυθμίστε το OpenClaw για το Discord

Αποθηκεύστε το token του bot σας ως μεταβλητή περιβάλλοντος, και στη συνέχεια δημιουργήστε ένα ενιαίο αρχείο patch που ενεργοποιεί το Discord, αναφέρεται στο token, και προσθέτει τον server σας στη λίστα επιτρεπόμενων. Αντικαταστήστε τα `<server_id>` και `<user_id>` με τα IDs που συλλέξατε παραπάνω.

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

> **Μη βασίζεστε στο να ζητήσετε από τον πράκτορα να το ρυθμίσει αυτό.** Όταν το sandboxing είναι ενεργοποιημένο, ο πράκτορας δεν μπορεί να γράψει στο `~/.openclaw/openclaw.json` από μέσα στο sandbox, χρησιμοποιήστε αντ' αυτού τις παραπάνω εντολές CLI στον host.

Επανεκκινήστε το gateway ώστε να λάβει υπόψη τη νέα ρύθμιση καναλιού:

```bash
openclaw gateway run --bind loopback --port 18789
```

Θα πρέπει να δείτε το `logged in to discord as <bot-name>` στην έξοδο του gateway μέσα σε λίγα δευτερόλεπτα.

#### Συζεύξτε τον λογαριασμό σας στο Discord

Στείλτε DM στο bot στο Discord. Θα απαντήσει με έναν σύντομο κωδικό σύζευξης.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Εγκρίνετέ το στο μηχάνημα που εκτελεί το OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Οι κωδικοί σύζευξης λήγουν μετά από μία ώρα.

Μπορείτε πλέον να συνομιλείτε με τον πράκτορά σας απευθείας από το Discord και να αναθέτετε εργασίες στο τοπικό σας υλικό.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Επιλογή Β: Telegram

Το Telegram είναι πιο απλό από το Discord για τους περισσότερους χρήστες, δεν απαιτεί server ούτε δικαιώματα διαχειριστή.

#### Δημιουργήστε ένα bot στο Telegram

1. Ανοίξτε το Telegram και στείλτε μήνυμα στο **@BotFather**.
2. Στείλτε `/newbot` και ακολουθήστε τις οδηγίες. Αποθηκεύστε το token του bot που θα σας δοθεί.

#### Ρυθμίστε το OpenClaw για το Telegram

Αποθηκεύστε το token ως μεταβλητή περιβάλλοντος:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Προσθέστε τη ρύθμιση καναλιού στο `~/.openclaw/openclaw.json` (ή εφαρμόστε το patch μέσω του dashboard):

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

Επανεκκινήστε το gateway, στη συνέχεια στείλτε στο bot σας οποιοδήποτε μήνυμα στο Telegram. Εγκρίνετε τη σύζευξη:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Οι κωδικοί σύζευξης λήγουν μετά από μία ώρα. Μπορείτε πλέον να συνομιλείτε με τον πράκτορά σας μέσω DM στο Telegram.

---

## Επόμενα Βήματα

Τώρα που ο πράκτοράς σας μπορεί να λαμβάνει εντολές από το κινητό σας και να ενεργεί στο τοπικό σας μηχάνημα, ακολουθούν τρεις κατευθύνσεις που αξίζει να εξερευνήσετε:

1. **Σύνοψη χρηματιστηριακής αγοράς**: Προγραμματίστε το OpenClaw να αντλεί δεδομένα από χρηματοοικονομικά APIs σε σταθερά διαστήματα, να συνοψίζει τις κινήσεις της ημέρας με το τοπικό σας μοντέλο, και να στέλνει μια σύνοψη στο κινητό σας κάθε πρωί μέσω του καναλιού που έχετε επιλέξει.

2. **Παρακολούθηση fine-tuning**: Ξεκινήστε μια εργασία εκπαίδευσης εξ αποστάσεως μέσω Telegram ή Discord, και στη συνέχεια ζητήστε από τον πράκτορα να παρακολουθεί το log εκπαίδευσης και να αναφέρει περιοδικά τιμές loss, χρήση GPU, και χρήση δίσκου πίσω στο κινητό σας. Αν η εκτέλεση κολλήσει ή η VRAM παρουσιάσει αιχμή, το μαθαίνετε αμέσως χωρίς να χρειάζεται να βρίσκεστε δίπλα στο μηχάνημα.

3. **IOT με τοπικό VLM**: Στρέψτε μια κάμερα προς την εξώπορτά σας, εκτελέστε ένα μοντέλο όρασης στο Lemonade, και αφήστε το OpenClaw να αναλύει καρέ κατ' απαίτηση ή με βάση κάποιο trigger. Ρωτήστε «έφτασαν σήμερα κάποια πακέτα;» από το κινητό σας και πάρτε μια απευθείας απάντηση από το δικό σας υλικό.

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