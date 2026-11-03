<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Μηχανική μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει ελεγχθεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένες οδηγίες, εντολές, στοιχεία λήψης, διαθεσιμότητα προϊόντων ή άλλο περιεχόμενο ενδέχεται να διαφέρουν ανάλογα με τη γλώσσα ή την περιοχή. Σε περίπτωση οποιασδήποτε ασυμφωνίας ή απόκλισης, υπερισχύει η πρωτότυπη αγγλική έκδοση του playbook.
<!-- auto-translated-disclaimer:end -->

# Εκτέλεση του Hermes Agent τοπικά με το Lemonade Server

## Επισκόπηση

Το [**Hermes Agent**](https://hermes-agent.nousresearch.com/) είναι ένας αυτοβελτιούμενος πράκτορας AI, δημιουργημένος από τη Nous Research. Διαθέτει έναν ενσωματωμένο βρόχο μάθησης, δημιουργεί δεξιότητες από την εμπειρία, δημιουργεί μια μόνιμη μνήμη σχετικά με το ποιος είστε σε όλες τις συνεδρίες, και μπορεί να εκτελεί προγραμματισμένες αυτοματοποιήσεις εκ μέρους σας. Σε αντίθεση με έναν απλό βοηθό συνομιλίας, το Hermes εκτελεί πραγματικές ενέργειες: εκτελεί εντολές shell, γράφει αρχεία, περιηγείται στο διαδίκτυο και αναθέτει παράλληλες ροές εργασίας σε υποπράκτορες.

Το [**Lemonade Server**](https://lemonade-server.ai/) είναι το τοπικό backend συμπερασμού που το τροφοδοτεί. Είναι ένας ανοιχτού κώδικα διακομιστής που εκτελεί μοντέλα GenAI απευθείας στο υλικό AMD σας και τα εκθέτει μέσω του βιομηχανικού προτύπου OpenAI API.

Μαζί σχηματίζουν μια πλήρως τοπική στοίβα πράκτορα AI: το Lemonade διαχειρίζεται τον συμπερασμό μοντέλων στην GPU σας, ενώ το Hermes παρέχει τον βρόχο πράκτορα, τη μνήμη, τις δεξιότητες και την πύλη ανταλλαγής μηνυμάτων.

> **Πριν συνεχίσετε:** Το Hermes Agent είναι ένας άκρως αυτόνομος πράκτορας AI. Η παροχή πρόσβασης σε οποιονδήποτε πράκτορα AI στο σύστημά σας ενδέχεται να οδηγήσει σε απρόβλεπτα ή ανεπιθύμητα αποτελέσματα. Προχωρήστε μόνο εάν κατανοείτε τους κινδύνους και αισθάνεστε άνετα με το λογισμικό που ενεργεί αυτόνομα εκ μέρους σας.

---

## Τι Θα Μάθετε

Μέχρι το τέλος αυτού του οδηγού θα μπορείτε να:

- **Εγκαταστήσετε το Hermes Agent** και να το κατευθύνετε προς το **Lemonade Server** ως backend AI του.
- **(Συνιστάται) Ενεργοποιήσετε το sandboxing με Docker/Podman** για να απομονώσετε τις ενέργειες του πράκτορα από τον κεντρικό υπολογιστή σας.
- **Ξεκινήσετε την πύλη Hermes** και επιβεβαιώσετε ότι ο πράκτοράς σας είναι έτοιμος.
- **Συνδέσετε ένα κανάλι επικοινωνίας** (Discord ή Telegram) ώστε να μπορείτε να συνομιλείτε με τον πράκτορά σας από οποιαδήποτε συσκευή.

---

<!-- @device:halo_box,halo,stx,krk -->
## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενων Λογισμικού

<!-- @os:linux -->
- Ένας υπολογιστής με **Ubuntu 24.04+** ή μια συμβατή διανομή Linux βασισμένη σε Debian με `apt-get`
- Τουλάχιστον **12 GB RAM** (συνιστώνται 64 GB+ για μεγαλύτερα μοντέλα)
- **~10–30 GB ελεύθερου χώρου στον δίσκο** για τα βάρη του μοντέλου
- [Podman](https://podman.io/docs/installation) (Προαιρετικό, για sandboxing του Hermes Agent)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- Ένας υπολογιστής με **Windows 10/11**
- Τουλάχιστον **12 GB RAM** (συνιστώνται 64 GB+ για μεγαλύτερα μοντέλα)
- **~10–30 GB ελεύθερου χώρου στον δίσκο** για τα βάρη του μοντέλου
- Podman (Προαιρετικό, για sandboxing του Hermes Agent). Εγκαταστήστε το μέσα στο WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Το Podman είναι προεγκατεστημένο στο Halo Box και δεν απαιτείται καμία ρύθμιση
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Λήψη και Φόρτωση του Συνιστώμενου Μοντέλου

Το συνιστώμενο μοντέλο για αυτόν τον οδηγό είναι το **Qwen3.6-35B-A3B-GGUF** από την Unsloth, ένα ισχυρό μοντέλο MoE με παράθυρο περιεχομένου 263k tokens που ταιριάζει καλά σε φόρτους εργασίας πρακτόρων. Αυτό το μοντέλο χρησιμοποιεί κβαντισμό UD-Q4_K_XL. Κάντε λήψη τώρα:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Στη συνέχεια, φορτώστε το με ένα μεγάλο παράθυρο περιεχομένου και αποθηκεύστε αυτήν τη ρύθμιση για μελλοντικές εκτελέσεις:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Το μοντέλο έχει προεπιλεγμένο μήκος περιεχομένου 262.144 tokens. Εάν αντιμετωπίσετε σφάλματα έλλειψης μνήμης (OOM), εξετάστε το ενδεχόμενο μείωσης του παραθύρου περιεχομένου.

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
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
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
model_id = "${hermes_model}"

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
  "model": "${hermes_model}",
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

Εκτελούμε το Hermes Agent μέσα στο WSL και το συνδέουμε με το Lemonade που εκτελείται εγγενώς στα Windows. Αυτό σας παρέχει ένα περιβάλλον κελύφους Linux για το Hermes, διατηρώντας παράλληλα την επιτάχυνση GPU του Lemonade στην πλευρά των Windows.

### Εγκατάσταση WSL και Ubuntu

Ανοίξτε το PowerShell ως Διαχειριστής και εγκαταστήστε τον πυρήνα WSL:

```powershell
wsl --install --no-distribution
```

Στη συνέχεια εγκαταστήστε το Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Ενεργοποίηση του systemd στο WSL

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

Το WSL2 εκτελείται σε ένα εικονικό δίκτυο. Το Lemonade στα Windows συνδέεται στο `127.0.0.1`, το οποίο το WSL δεν μπορεί να προσπελάσει απευθείας. Ένα port proxy των Windows προωθεί την κίνηση από την IP της πύλης WSL στο localhost των Windows.

**Βρείτε την IP της πύλης WSL** (εκτελέστε μέσα στο WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Προσθέστε το port proxy** (εκτελέστε στο PowerShell ως Διαχειριστής, αντικαθιστώντας το `<WSL-Gateway-IP>` με την IP της πύλης WSL σας):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Προσθέστε έναν κανόνα τείχους προστασίας** (στο ίδιο αναβαθμισμένο PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Επαληθεύστε από το WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Εάν έχετε ήδη φορτώσει το μοντέλο Qwen3.6-35B-A3B-GGUF στο προηγούμενο βήμα, θα πρέπει να δείτε έξοδο JSON που παραθέτει το φορτωμένο μοντέλο σας.

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

> Ο κανόνας `netsh portproxy` διατηρείται μετά από επανεκκινήσεις, αλλά η IP της πύλης WSL μπορεί να αλλάξει μετά από `wsl --shutdown`. Εάν το Lemonade γίνει μη προσβάσιμο από το WSL μετά από επανεκκίνηση, λάβετε την ενημερωμένη IP πύλης και ενημερώστε το proxy με αυτήν τη νέα IP.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## Εγκατάσταση του Hermes Agent

<!-- @os:windows -->
> Εκτελέστε τις εντολές αυτής της ενότητας μέσα στο **τερματικό WSL** σας, εκτός εάν αναφέρεται διαφορετικά.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Η σημαία `--skip-setup` παρακάμπτει τον διαδραστικό οδηγό εγκατάστασης, ώστε να μπορείτε να διαμορφώσετε το backend του μοντέλου χειροκίνητα στο επόμενο βήμα.

Επαναφορτώστε το κέλυφός σας:

```bash
source ~/.bashrc
```

Επιβεβαιώστε την εγκατάσταση:

```bash
hermes --version
```

Εκτελέστε ένα αυτοδιαγνωστικό για να ελέγξετε όλες τις εξαρτήσεις:

```bash
hermes doctor
```

> **Συμβουλή:** Εάν δείτε `command not found` μετά την εγκατάσταση, προσθέστε το Hermes στο PATH σας:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Για να το κάνετε αυτό μόνιμο, προσθέστε την παραπάνω γραμμή στο `~/.bashrc` ή `~/.zshrc` σας.

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## Ρύθμιση του Hermes ώστε να χρησιμοποιεί το Lemonade

Το Hermes αποθηκεύει τη ρύθμιση του μοντέλου του στο `~/.hermes/config.yaml`. Μπορείτε είτε να χρησιμοποιήσετε τον διαδραστικό επιλογέα `hermes model` είτε να γράψετε απευθείας τη ρύθμιση.

### Επιλογή 1: Διαδραστικός επιλογέας

<!-- @os:windows -->
> Εκτελέστε το παρακάτω μέσα στο **τερματικό WSL** σας.
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

Όταν σας ζητηθεί:

1. Επιλέξτε **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** χρησιμοποιήστε το IP της πύλης WSL: εκτελέστε `ip route show default | awk '{print $3}' | head -1` μέσα στο WSL για να το λάβετε, στη συνέχεια εισαγάγετε `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Αυτόματος εντοπισμός)
5. **Select model:** επιλέξτε `Qwen3.6-35B-A3B-GGUF` από τη λίστα
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (ή οποιοδήποτε όνομα προτιμάτε)

Το `hermes model` αποθηκεύει τόσο την ενεργή επιλογή μοντέλου όσο και μια ονομαστική καταχώρηση `custom_providers` που αποθηκεύει το μήκος περιεχομένου μαζί με το endpoint. Το αποτέλεσμα στο `~/.hermes/config.yaml` μοιάζει ως εξής:

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### Επιλογή 2: Απευθείας εγγραφή της ρύθμισης

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

Μέσα στο τερματικό WSL σας, λάβετε το IP του κεντρικού υπολογιστή Windows και γράψτε τη ρύθμιση:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## (Προτείνεται) Ενεργοποίηση Sandboxing με Podman

Ο Hermes Agent μπορεί να δρομολογήσει όλες τις λειτουργίες shell και αρχείων του agent μέσω ενός απομονωμένου container αντί να τις εκτελεί απευθείας στον κεντρικό υπολογιστή σας. Αυτό περιορίζει την ακτίνα επίδρασης οποιασδήποτε ακούσιας ενέργειας στο sandbox, αφήνοντας το σύστημα αρχείων και το δίκτυο του κεντρικού υπολογιστή σας ανέπαφα.

Δημιουργήστε μια ελαφριά εικόνα sandbox:

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Εισέλθετε στο τερματικό WSL σας:

```powershell
wsl -d Ubuntu-24.04
```

Στη συνέχεια, δημιουργήστε μια ελαφριά εικόνα sandbox:

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Στη συνέχεια, ρυθμίστε το Hermes ώστε να χρησιμοποιεί το Podman ως χρόνο εκτέλεσης container και ορίστε το backend του τερματικού:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> Το `terminal.backend` παραμένει `docker`.
> Το `HERMES_DOCKER_BINARY` είναι αυτό που ενημερώνει το Hermes να χρησιμοποιεί το Podman ως χρόνο εκτέλεσης αντί για αυτό.

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Το Hermes θα δημιουργήσει τώρα ένα μόνιμο container sandbox και θα δρομολογεί όλες τις κλήσεις `terminal` και εργαλείων αρχείων μέσω αυτού. Το container μοιράζεται τη διάρκεια ζωής της διεργασίας Hermes, επαναχρησιμοποιείται σε όλες τις κλήσεις εργαλείων και καταστρέφεται όταν τερματίζεται το Hermes.

> **Επαληθεύστε ότι το sandbox λειτουργεί:** Ξεκινήστε το Hermes (`hermes`) και ζητήστε του να `run hostname` - θα πρέπει να δείτε ένα σύντομο ID container αντί για το όνομα κεντρικού υπολογιστή του μηχανήματός σας. Μπορείτε επίσης να του ζητήσετε να `rm -rf <path-to-a-dummy-file/folder>`: Το Hermes θα επιβεβαιώσει τη διαγραφή, αλλά ο φάκελος θα παραμείνει στον κεντρικό υπολογιστή σας. Η εντολή εκτελέστηκε μέσα στον απομονωμένο φάκελο `$HOME` του container, όχι στον δικό σας.

> **Χρειάζεστε ισχυρότερη απομόνωση;** Το Hermes παρέχει επίσης μια επίσημη εικόνα Docker (`nousresearch/hermes-agent`) που εκτελεί ολόκληρη τη διεργασία agent μέσα σε ένα container - gateway, εργαλεία, τα πάντα. Δείτε την [τεκμηρίωση Docker του Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/docker) για λεπτομέρειες ρύθμισης.

---

<!-- @os:linux -->
## (Προτείνεται) Ενσωμάτωση του Hermes με τις Υπηρεσίες Firecrawl

Το Hermes μπορεί να περιηγηθεί και να εξαγάγει περιεχόμενο από ιστότοπους χρησιμοποιώντας τα ενσωματωμένα εργαλεία web του. Ωστόσο, πολλοί σύγχρονοι ιστότοποι χρησιμοποιούν συστήματα ανίχνευσης bot, τα οποία μπλοκάρουν απλά αιτήματα HTTP και επιστρέφουν σελίδες πρόκλησης αντί για το πραγματικό περιεχόμενο. Ως αποτέλεσμα, το Hermes ενδέχεται να μην μπορεί να εξαγάγει αξιόπιστα πληροφορίες από αυτούς τους ιστότοπους.

Για να ξεπεραστεί αυτός ο περιορισμός, το [Firecrawl](https://docs.firecrawl.dev/introduction) παρέχει μια αυτο-φιλοξενούμενη υπηρεσία εξερεύνησης ιστού και εξαγωγής περιεχομένου που μπορεί να παρακάμψει αυτές τις προκλήσεις και να ξεκλειδώσει το πλήρες δυναμικό του αυτοματισμού Hermes.

Σε αυτή τη ρύθμιση, το Firecrawl εκτελείται ως ένα σύνολο containers Docker διαχειριζόμενα με το Podman. Για να απλοποιήσουμε τη διαχείριση κύκλου ζωής και την αυτόματη εκκίνηση, καταχωρούμε το Firecrawl ως υπηρεσία `systemd` σε επίπεδο χρήστη που ενορχηστρώνει την υποκείμενη στοίβα Podman Compose. Αυτό επιτρέπει στο Hermes να ξεκινά, να σταματά και να επαληθεύει την υπηρεσία Firecrawl χρησιμοποιώντας τυπικές εντολές `systemctl --user` αντί να αλληλεπιδρά απευθείας με τα containers.

Για να κρατήσουμε τα πράγματα απλά, χωρίσαμε ολόκληρη τη διαδικασία σε τέσσερα βήματα:

---

### 1. Καταχώρηση της υπηρεσίας συστήματος
Πλοηγηθείτε στον κατάλογο ρυθμίσεων χρήστη systemd:
```bash
cd ~/.config/systemd/user
```
Δημιουργήστε και ανοίξτε ένα νέο αρχείο με όνομα `firecrawl.service`.
```bash
nano firecrawl.service
```
Αντιγράψτε και επικολλήστε την παρακάτω ρύθμιση:
```bash
[Unit]
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
Στο σημείο αυτό, η υπηρεσία έχει οριστεί αλλά δεν έχει ακόμα καταχωρηθεί στο `systemd`.
Βεβαιωθείτε ότι το όνομα αρχείου ταιριάζει ακριβώς με αυτό που δημιουργήσατε παραπάνω, στη συνέχεια εκτελέστε:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Εάν είναι επιτυχές, θα πρέπει να δείτε την παρακάτω έξοδο:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

Ο κατάλογος `default.target.wants/` περιέχει συμβολικούς συνδέσμους προς υπηρεσίες που έχουν ρυθμιστεί να εκκινούν αυτόματα.

### 2. Ρύθμιση του Firecrawl για την Υπηρεσία σας

Το [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) είναι ιδανικό για όσους χρειάζονται πλήρη έλεγχο πάνω στα περιβάλλοντα scraping και επεξεργασίας δεδομένων τους, αλλά έχει το αντάλλαγμα πρόσθετης προσπάθειας συντήρησης και ρύθμισης.

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
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> Ορίστε το `BULL_AUTH_KEY` σε ένα ισχυρό μυστικό, ειδικά σε οποιαδήποτε ανάπτυξη προσβάσιμη από μη έμπιστα δίκτυα.
### 3. Ανάπτυξη του Hermes μέσω Compose

Πριν προχωρήσετε, βεβαιωθείτε ότι έχετε κατεβάσει την τελευταία εικόνα Docker του Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Αφού ολοκληρωθεί αυτό, κατεβάστε το αρχείο Compose του Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) και τοποθετήστε το στον ριζικό κατάλογο `/firecrawl`:

> Αυτή η σύμβαση απαιτείται ώστε το `systemd` να μπορεί να εντοπίσει και να ξεκινήσει σωστά την υπηρεσία, όπως ορίζεται στο `WorkingDirectory=${HOME}/firecrawl`.

> Μπορείτε πάντα να επεκτείνετε το stack προσθέτοντας επιπλέον υπηρεσίες Firecrawl όπως χρειάζεται. Η πλήρης λίστα των διαθέσιμων υπηρεσιών βρίσκεται στο επίσημο [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Εκκίνηση της υπηρεσίας Hermes μέσω του Firecrawl 

Πριν παραδώσετε τον έλεγχο στο `systemd`, επιβεβαιώστε ότι όλα λειτουργούν σωστά εκτελώντας το stack χειροκίνητα:
```bash
podman compose -f hermes-compose.yaml up -d
```
Αν όλα έχουν διαμορφωθεί σωστά, θα πρέπει να δείτε τον container του Hermes να ανεβαίνει και η έξοδος της γραμμής εντολών σας θα πρέπει να μοιάζει με αυτή:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Μόλις επαληθεύσετε, τερματίστε ξανά το stack πριν προχωρήσετε:
```bash
podman compose -f hermes-compose.yaml down
```
Τώρα που όλα έχουν επαληθευτεί, ξεκινήστε την υπηρεσία μέσω του `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Το API του Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) είναι προσβάσιμο από μέσα στον διαδραστικό container, και ο Web Dashboard είναι διαθέσιμος στον ίδιο host και port στη διεύθυνση http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Για να σταματήσετε την υπηρεσία, εκτελέστε:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Ξεκινήστε απευθείας μια διαδραστική συνεδρία CLI: 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**Συγχαρητήρια, δημιουργήσατε ένα πλήρως τοπικό AI agent stack.**

### Web Dashboard

Το Hermes περιλαμβάνει ένα UI βασισμένο σε browser για τη διαχείριση διαμόρφωσης, κλειδιών API, μοντέλων, συνεδριών, μνήμης και εργασιών cron. Ανοίξτε ένα δεύτερο τερματικό ενώ το gateway ή το CLI εκτελείται και ξεκινήστε το με:

```bash
hermes dashboard
```

Αυτό ξεκινά έναν τοπικό διακομιστή και ανοίγει το `http://127.0.0.1:9119` στον browser σας. Δείτε την [τεκμηρίωση του dashboard](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) για την πλήρη αναφορά λειτουργιών.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Προαιρετικό: Σύνδεση ενός καναλιού επικοινωνίας

Μόλις το gateway εκτελείται, μπορείτε να προσπελάσετε τον τοπικό σας agent από οποιαδήποτε συσκευή. Το Hermes υποστηρίζει το [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), το [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram), και άλλα

---

### Discord

Το Discord απαιτεί έναν server όπου **έχετε δικαιώματα διαχειριστή** για να προσθέσετε ένα bot. Αν μοιράζεστε servers αλλά δεν κατέχετε κάποιον, χρησιμοποιήστε αντ' αυτού το Telegram.

#### Δημιουργία εφαρμογής και bot Discord

1. Μεταβείτε στο [Discord Developer Portal](https://discord.com/developers/applications) και κάντε κλικ στο **New Application**. Δώστε του ένα όνομα (π.χ. "hermes-bot").
2. Στη πλαϊνή γραμμή, κάντε κλικ στο **Bot**. Ορίστε ένα username για το bot.
3. Ακόμα στη σελίδα Bot, μεταβείτε στο **Privileged Gateway Intents** και ενεργοποιήστε:
   - **Message Content Intent** (απαιτείται)
   - **Server Members Intent** (συνιστάται)
4. Επιστρέψτε επάνω και κάντε κλικ στο **Reset Token** για να δημιουργήσετε το token του bot σας. Αντιγράψτε το.

#### Προσθήκη του bot στον server σας

1. Στη πλαϊνή γραμμή, κάντε κλικ στο **OAuth2 / URL Generator**.
2. Κάτω από το **Scopes**, ενεργοποιήστε τα `bot` και `applications.commands`.
3. Κάτω από το **Bot Permissions**, ενεργοποιήστε: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Αντιγράψτε το URL που δημιουργήθηκε, επικολλήστε το στον browser σας, επιλέξτε τον server σας και επιβεβαιώστε.

#### Συλλογή των IDs σας και ενεργοποίηση DMs

Ενεργοποιήστε τη Λειτουργία Προγραμματιστή στο Discord (**User Settings / Advanced / Developer Mode**), και στη συνέχεια:
- Κάντε δεξί κλικ στο εικονίδιο του server σας: **Copy Server ID**
- Κάντε δεξί κλικ στο δικό σας avatar: **Copy User ID**

Κάντε δεξί κλικ στο εικονίδιο του server σας / **Privacy Settings** / ενεργοποιήστε τα **Direct Messages**. Αυτό απαιτείται για το βήμα ζευγοποίησης.

#### Διαμόρφωση του Hermes για το Discord

Προσθέστε τα παρακάτω στο `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Στη συνέχεια ξεκινήστε το gateway:

```bash
hermes gateway
```

Το bot θα πρέπει να εμφανιστεί online στο Discord μέσα σε λίγα δευτερόλεπτα. Στείλτε του ένα μήνυμα, είτε μέσω DM είτε σε ένα κανάλι που μπορεί να δει.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Δημιουργία ενός bot Telegram

1. Ανοίξτε το Telegram και στείλτε μήνυμα στο **@BotFather**.
2. Στείλτε `/newbot` και ακολουθήστε τις οδηγίες. Αποθηκεύστε το token του bot που θα σας δώσει.

#### Διαμόρφωση του Hermes για το Telegram

Προσθέστε τα παρακάτω στο `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Δεν γνωρίζετε το Telegram user ID σας;** Στείλτε μήνυμα στο [@userinfobot](https://t.me/userinfobot) στο Telegram, θα σας απαντήσει με τον αριθμητικό σας ID.

Στη συνέχεια ξεκινήστε το gateway:

```bash
hermes gateway
```

Στείλτε στο bot σας οποιοδήποτε μήνυμα στο Telegram για δοκιμή. Μπορείτε τώρα να συνομιλείτε με τον agent σας μέσω DM στο Telegram. Δείτε τον [πλήρη οδηγό εγκατάστασης Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) για λειτουργία webhook και προχωρημένες επιλογές.

---

## Επόμενα Βήματα

Τώρα που ο agent σας μπορεί να λαμβάνει εντολές από το κινητό σας και να ενεργεί στο τοπικό σας μηχάνημα, εδώ είναι τρεις κατευθύνσεις που αξίζει να εξερευνήσετε:

1. **Αυτοματοποιημένη περίληψη έρευνας**: Προγραμματίστε το Hermes να αναζητά στο web θέματα που σας ενδιαφέρουν κάθε πρωί, να συνοψίζει τα ευρήματα με το τοπικό σας μοντέλο, και να στέλνει μια περίληψη στο κινητό σας μέσω Telegram ή Discord, όλα εκτελούμενα στο δικό σας hardware χωρίς κόστη cloud.

2. **Ανασκόπηση κώδικα κατόπιν αιτήματος**: Κατευθύνετε το Hermes σε ένα GitHub repository, ζητήστε του να ανασκοπήσει ανοιχτά pull requests, και να δημοσιεύσει σχόλια ή μια περίληψη πίσω στη συνομιλία σας. Με το Docker terminal backend, όλες οι λειτουργίες git εκτελούνται μέσα στο sandbox, διατηρώντας τον host σας καθαρό.

3. **Τοπικός βοηθός αρχείων**: Δώστε στο Hermes πρόσβαση σε έναν κατάλογο εργασίας και ζητήστε του να οργανώνει, μετονομάζει, συνοψίζει ή μετασχηματίζει αρχεία κατόπιν αιτήματος από το κινητό σας. Επειδή το Docker terminal backend περιορίζει όλες τις εγγραφές στο sandbox workspace, τυχαίες καταστροφικές λειτουργίες περιορίζονται.