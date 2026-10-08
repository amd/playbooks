<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Μηχανική μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει ελεγχθεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένες οδηγίες, εντολές, στοιχεία λήψης, διαθεσιμότητα προϊόντων ή άλλο περιεχόμενο ενδέχεται να διαφέρουν ανάλογα με τη γλώσσα ή την περιοχή. Σε περίπτωση οποιασδήποτε ασυμφωνίας ή απόκλισης, υπερισχύει η πρωτότυπη αγγλική έκδοση του playbook.
<!-- auto-translated-disclaimer:end -->

# Εκτέλεση του OpenClaw με το Lemonade Server ως backend

## Επισκόπηση

Το [**OpenClaw**](https://openclaw.ai/) είναι ένας αυτόνομος AI agent που μπορεί να γράφει και να εκτελεί κώδικα, να διαχειρίζεται αρχεία και να διεκπεραιώνει πολύπλοκα, πολυβηματικά tasks για λογαριασμό σας. Σε αντίθεση με έναν chat assistant που απλώς απαντά σε ερωτήσεις, το OpenClaw εκτελεί πραγματικές ενέργειες στο σύστημά σας, κάτι που σημαίνει ότι χρειάζεται ένα γρήγορο, ικανό AI backend που μπορεί να ανταποκριθεί σε έναν απαιτητικό agent loop.

Το [**Lemonade Server**](https://lemonade-server.ai/) είναι αυτό το backend. Πρόκειται για έναν open-source local inference server που εκτελεί μοντέλα GenAI απευθείας στο υλικό σας και τα εκθέτει μέσω του βιομηχανικού προτύπου OpenAI API.

Μαζί, αποτελούν μια πλήρως τοπική AI agent στοίβα (stack): το Lemonade αναλαμβάνει το inference των μοντέλων, ενώ το OpenClaw παρέχει το agent loop που μετατρέπει τα αποτελέσματα του μοντέλου σε πραγματικές ενέργειες.

> **Πριν συνεχίσετε:** Το OpenClaw είναι ένας εξαιρετικά αυτόνομος AI agent. Η παραχώρηση πρόσβασης σε οποιονδήποτε AI agent στο σύστημά σας ενδέχεται να οδηγήσει σε απρόβλεπτα ή ανεπιθύμητα αποτελέσματα. Προχωρήστε μόνο εάν κατανοείτε τους κινδύνους και αισθάνεστε άνετα με αυτόνομο λογισμικό που ενεργεί για λογαριασμό σας.

---

## Τι Θα Μάθετε

Μέχρι το τέλος αυτού του playbook θα μπορείτε να:

- Μάθετε για το **Lemonade Server**
- **Εγκαταστήσετε το OpenClaw** και **να το κατευθύνετε προς το Lemonade Server** ως AI backend του.
- **Εκκινήσετε το OpenClaw gateway** και να επιβεβαιώσετε ότι ο agent σας είναι έτοιμος να δουλέψει.
- **Συνδέσετε ένα κανάλι επικοινωνίας** (Discord ή Telegram) ώστε να μπορείτε να συνομιλείτε με τον agent σας από οποιαδήποτε συσκευή.

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
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Προαιρετικό, για sandboxing του OpenClaw)
- **~10–30 GB ελεύθερου χώρου στο δίσκο** για τα βάρη του μοντέλου
<!-- @os:end -->

<!-- @os:windows -->
- Ένας υπολογιστής με **Windows 10/11**
- Τουλάχιστον **12 GB RAM** (συνιστώνται 64 GB+ για μεγαλύτερα μοντέλα)
- **~10–30 GB ελεύθερου χώρου στο δίσκο** για τα βάρη του μοντέλου
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Προαιρετικό, για sandboxing του OpenClaw)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:nodejs,openclaw,lemonade-models-qwen3-35b-a3b,lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Λήψη και Φόρτωση του Προτεινόμενου Μοντέλου

Το προτεινόμενο μοντέλο για αυτό το playbook είναι το **Qwen3.6-35B-A3B-GGUF** από την Unsloth, ένα ισχυρό MoE μοντέλο με παράθυρο context 263k tokens που ταιριάζει ιδανικά σε φόρτους εργασίας agent. Αυτό το μοντέλο χρησιμοποιεί κβαντισμό UD-Q4_K_XL. Κατεβάστε το τώρα:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Στη συνέχεια φορτώστε το με ένα μεγάλο παράθυρο context και αποθηκεύστε αυτή τη ρύθμιση για μελλοντικές εκτελέσεις:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Το μοντέλο έχει προεπιλεγμένο μήκος context 262.144 tokens. Εάν αντιμετωπίσετε σφάλματα εξάντλησης μνήμης (OOM), εξετάστε το ενδεχόμενο μείωσης του παραθύρου context. Ωστόσο, επειδή το Qwen3.6 αξιοποιεί εκτεταμένο context για πολύπλοκες εργασίες, συνιστούμε τη διατήρηση μήκους context τουλάχιστον 128K tokens ώστε να διατηρηθούν οι ικανότητες σκέψης.

> **Συμβουλή: Απενεργοποιήστε τη σκέψη για ταχύτερες αποκρίσεις agent:** Το Qwen3.6-35B-A3B εκτελείται σε λειτουργία σκέψης από προεπιλογή, κάτι που προσθέτει καθυστέρηση πριν από κάθε απόκριση. Για agent loops αυτή η επιβάρυνση συσσωρεύεται γρήγορα. Το αποθετήριο [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) παρέχει μια έτοιμη διαμόρφωση που απενεργοποιεί τη σκέψη. Για να τη χρησιμοποιήσετε, κατεβάστε το αρχείο και εισαγάγετέ το:
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

Εκτελούμε το OpenClaw μέσα στο WSL (Προτείνεται) και το συνδέουμε με το Lemonade που εκτελείται εγγενώς στα Windows. Αυτό σας δίνει ένα περιβάλλον κελύφους Linux για το OpenClaw, διατηρώντας παράλληλα την επιτάχυνση GPU του Lemonade στην πλευρά των Windows.

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

Εκτελέστε αυτό μέσα στο τερματικό του Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Κλείστε το WSL και επανεκκινήστε το:

```powershell
exit
wsl --shutdown
wsl
```

### Γεφύρωση του Lemonade από τα Windows στο WSL

Το WSL2 εκτελείται σε ένα εικονικό δίκτυο. Το Lemonade στα Windows συνδέεται στο `127.0.0.1`, κάτι που το WSL δεν μπορεί να προσπελάσει απευθείας. Ένα Windows port proxy προωθεί την κίνηση από την IP πύλης (gateway) του WSL προς το localhost των Windows.

**Βρείτε την IP πύλης (gateway) του WSL** (εκτελέστε μέσα στο WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Προσθέστε το port proxy** (εκτελέστε στο PowerShell ως Διαχειριστής, αντικαθιστώντας το `<WSL-Gateway-IP>` με την IP πύλης του WSL σας):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Σημείωση: Εάν αντιμετωπίσετε σφάλμα `netsh: command not found`, δοκιμάστε να χρησιμοποιήσετε το ρητό όνομα εκτελέσιμου αντ' αυτού - `netsh.exe`

**Προσθέστε έναν κανόνα τείχους προστασίας** (στο ίδιο ανυψωμένο PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Επαλήθευση από το WSL**:

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

#### Διατήρηση της λειτουργίας της γέφυρας μετά από επανεκκίνηση

Ο κανόνας `netsh portproxy` επιβιώνει σε επανεκκινήσεις, αλλά η IP πύλης (gateway) του WSL μπορεί να αλλάξει μετά από `wsl --shutdown` ή επανεκκίνηση. Όταν συμβεί αυτό, ο proxy εξακολουθεί να δείχνει στην παλιά IP και το Lemonade γίνεται μη προσβάσιμο από το WSL. Αν συμβεί αυτό, χρησιμοποιήστε μία από τις παρακάτω επιλογές.

**Επιλογή 1 (προτεινόμενη) — Επιδιόρθωση της γέφυρας αυτόματα.** Για να αποφύγετε να το κάνετε αυτό με το χέρι κάθε φορά, χρησιμοποιήστε μια προγραμματισμένη εργασία που ελέγχει τη γέφυρα σε κάθε εκκίνηση και σύνδεση και την ανακατασκευάζει μόνο όταν έχει αλλάξει η IP πύλης. Δείτε τον [οδηγό αυτόματης επιδιόρθωσης της γέφυρας Lemonade WSL](assets/RepairLemonadeWslBridge.md).


**Επιλογή 2 — Επιδιόρθωση της γέφυρας χειροκίνητα.** Πρώτα, λάβετε την τρέχουσα IP πύλης WSL εκτελώντας αυτό μέσα στο WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Αντιγράψτε αυτήν την τιμή· θα τη χρησιμοποιήσετε στη θέση του `<new-WSL-Gateway-IP>` παρακάτω.

Στη συνέχεια, σε ένα **PowerShell με δικαιώματα διαχειριστή** (Εκτέλεση ως διαχειριστής), καταγράψτε τους υπάρχοντες κανόνες, διαγράψτε μόνο τον παλιό κανόνα Lemonade και προσθέστε έναν νέο με την τρέχουσα IP:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

Στην έξοδο της εντολής `show all`, ο παλιός κανόνας Lemonade είναι η καταχώρηση της οποίας η διεύθυνση σύνδεσης είναι `127.0.0.1` στη θύρα `13305`· η διεύθυνση ακρόασής της είναι η δική σας `<old-WSL-Gateway-IP>`. Η διαγραφή βάσει αυτής της διεύθυνσης αφαιρεί μόνο αυτόν τον κανόνα και αφήνει ανέπαφους οποιουσδήποτε άλλους κανόνες port-proxy στο μηχάνημά σας.

Ο κανόνας τείχους προστασίας που προσθέσατε κατά τη ρύθμιση είναι συνδεδεμένος με τη θύρα `13305` (όχι με την IP), οπότε συνεχίζει να λειτουργεί και δεν χρειάζεται να δημιουργηθεί ξανά.

> **Σύσταση:** Για να αποφύγετε προβλήματα πύλης, προτείνουμε ιδιαίτερα την ακόλουθη ρύθμιση κελύφους (shell):
> - Οι **εντολές Windows** θα πρέπει να εκτελούνται σε **PowerShell**
> - Οι **εντολές διανομής WSL** θα πρέπει να εκτελούνται σε **Command Prompt** (εκτέλεση ως **Διαχειριστής**)

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

Η σημαία `--no-onboard` παραλείπει τον διαδραστικό οδηγό ρύθμισης, θα διαμορφώσετε το backend μοντέλου χειροκίνητα στο επόμενο βήμα, κάτι που σας δίνει ακριβή έλεγχο για το ποιο μοντέλο και εξυπηρετητής χρησιμοποιούνται.

Ανοίξτε ένα νέο τερματικό και επιβεβαιώστε την εγκατάσταση:

```bash
openclaw --version
```

> **Συμβουλή:** Αν δείτε `command not found` μετά την εγκατάσταση, προσθέστε τον καθολικό κατάλογο bin του npm στο PATH σας:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Για να το κάνετε αυτό μόνιμο, προσθέστε την παραπάνω γραμμή στο αρχείο `~/.bashrc` ή `~/.zshrc`.

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


### Διαμόρφωση του OpenClaw ώστε να Χρησιμοποιεί το Lemonade

Εκτελέστε τη μη διαδραστική ενσωμάτωση (onboarding) του OpenClaw.
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

> **Μέγεθος παραθύρου περιβάλλοντος (context window) στο OpenClaw:** Η συμπίεση (compaction) του OpenClaw ενεργοποιείται όταν `contextTokens > contextWindow − reserveTokens`. Η προεπιλεγμένη τιμή `reserveTokensFloor` είναι 20.000 tokens, ένα κατώτατο όριο που υπερισχύει της `reserveTokens` όταν αυτή είναι χαμηλότερη, οπότε οποιοδήποτε περιβάλλον μοντέλου κάτω από ~37k θα προκαλέσει έναν ατέρμονα βρόχο συμπίεσης. Ορίστε μια χαμηλή τιμή reserve και απενεργοποιήστε το κατώτατο όριο μία φορά στη ρύθμισή σας και αυτό θα ισχύει για κάθε μοντέλο, χωρίς να χρειάζεται ρύθμιση ανά μοντέλο:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> Το `reserveTokensFloor` είναι ένα *κατώτατο όριο* (ελάχιστη διασφάλιση), όχι το ίδιο το reserve· ο ορισμός μόνο του κατώτατου ορίου δεν έχει κανένα αποτέλεσμα. Το `reserveTokensFloor: 0` απενεργοποιεί τη διασφάλιση ώστε να γίνει αποδεκτή η χαμηλότερη τιμή `reserveTokens`.
>
> **Πότε να το εφαρμόσετε:** Χρησιμοποιήστε αυτή τη ρύθμιση αν το ενεργό παράθυρο περιβάλλοντος του μοντέλου σας είναι κάτω από ~37k, είτε επειδή το μοντέλο είναι μικρό (π.χ. 8k, 16k, 32k) είτε επειδή το έχετε εσκεμμένα περιορίσει σε χαμηλότερη τιμή (π.χ. φορτώνοντας ένα μοντέλο 128k αλλά ορίζοντας το περιβάλλον σε 16k στο Lemonade). Χωρίς αυτό, το OpenClaw εισέρχεται σε έναν ατέρμονα βρόχο συμπίεσης κατά την εκκίνηση.
>
> **Μοντέλα μεγάλου περιβάλλοντος στο πλήρες περιβάλλον:** Μπορείτε να παραλείψετε εντελώς αυτό το βήμα. Οι προεπιλογές λειτουργούν μια χαρά, η συμπίεση θα ενεργοποιηθεί πολύ πριν γεμίσει το παράθυρο και το μοντέλο έχει άφθονο χώρο για να παράγει μεγάλες απαντήσεις. Αν το εφαρμόσετε παρ' όλα αυτά, να γνωρίζετε ότι το `reserveTokens: 4096` περιορίζει το μήκος της απάντησης σε ~4k tokens, κάτι που μπορεί να διακόψει τη δημιουργία μεγάλων αρχείων ή λεπτομερών σχεδίων.
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
> Το υπόλοιπο της ρύθμισής σας (gateway, κανάλια, μοντέλα, κ.λπ.) παραμένει αμετάβλητο, μόνο το κλειδί `compaction` χρειάζεται να προστεθεί.
### (Προτεινόμενο) Ενεργοποίηση Docker Sandboxing

Το OpenClaw μπορεί να δρομολογεί όλες τις λειτουργίες αρχείων και κώδικα του agent μέσω ενός απομονωμένου Docker container αντί να τις εκτελεί απευθείας στον υπολογιστή σας. Αυτό περιορίζει την ακτίνα επίδρασης οποιασδήποτε ακούσιας ενέργειας στο sandbox, αφήνοντας το σύστημα αρχείων και το δίκτυο του υπολογιστή σας ανεπηρέαστα.

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

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
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

Τα sandbox containers δεν έχουν **πρόσβαση στο δίκτυο** από προεπιλογή. Δείτε την [αναφορά sandboxing](https://docs.openclaw.ai/gateway/sandboxing) για bind mounts και παρακάμψεις δικτύου.

> #### Αντιμετώπιση προβλημάτων: Docker Permission Denied
> 
> Αν λάβετε "permission denied" κατά την εκτέλεση εντολών Docker:
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
> **Βήμα 2: Αν το σφάλμα επιμένει, εφαρμόστε τη μόνιμη λύση**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Στη συνέχεια κάντε **επανεκκίνηση** του συστήματός σας.
> 
> **Γρήγορη προσωρινή λύση** (επαναφέρεται μετά από επανεκκίνηση):
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
## (Προτεινόμενο) Ενσωμάτωση του OpenClaw με τις Υπηρεσίες Firecrawl

Το [Firecrawl](https://docs.firecrawl.dev/introduction) παρέχει μια αυτοφιλοξενούμενη υπηρεσία web crawling και εξαγωγής περιεχομένου που μπορεί να παρακάμψει αυτές τις προκλήσεις και να ξεκλειδώσει το πλήρες δυναμικό της αυτοματοποίησης με το OpenClaw.

Σε αυτήν τη διαμόρφωση, το OpenClaw εκτελείται ως ένα σύνολο Docker containers που διαχειρίζεται το Podman. Για να απλοποιήσουμε τη διαχείριση κύκλου ζωής και την αυτόματη εκκίνηση, καταχωρούμε το Firecrawl ως υπηρεσία `systemd` επιπέδου χρήστη που ορχηστρώνει το υποκείμενο στοίβαγμα Podman Compose. Αυτό επιτρέπει στο OpenClaw να ξεκινά το gateway, να σταματά και να επαληθεύει την υπηρεσία Firecrawl χρησιμοποιώντας τυπικές εντολές `systemctl --user` αντί να αλληλεπιδρά απευθείας με τα containers.

Για να κρατήσουμε τα πράγματα απλά, έχουμε χωρίσει όλη τη διαδικασία σε τέσσερα βήματα:

---

### 1. Καταχώρηση της υπηρεσίας συστήματος
Μεταβείτε στον κατάλογο διαμόρφωσης χρήστη του systemd:
```bash
cd ~/.config/systemd/user
```
Δημιουργήστε και ανοίξτε ένα νέο αρχείο με όνομα `firecrawl.service`.
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
Σε αυτό το σημείο, η υπηρεσία έχει οριστεί αλλά δεν έχει ακόμα καταχωρηθεί στο `systemd`.
Βεβαιωθείτε ότι το όνομα αρχείου ταιριάζει ακριβώς με αυτό που δημιουργήσατε παραπάνω, και στη συνέχεια εκτελέστε:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Αν η διαδικασία ολοκληρωθεί επιτυχώς, θα πρέπει να δείτε την ακόλουθη έξοδο:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 Ο κατάλογος `default.target.wants/` περιέχει συμβολικούς συνδέσμους προς υπηρεσίες που έχουν διαμορφωθεί ώστε να ξεκινούν αυτόματα.

### 2. Διαμόρφωση του Firecrawl

Το [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) είναι ιδανικό για όσους χρειάζονται πλήρη έλεγχο των περιβαλλόντων scraping και επεξεργασίας δεδομένων τους, αλλά έρχεται με το αντάλλαγμα επιπλέον προσπαθειών συντήρησης και διαμόρφωσης.

Ξεκινήστε κλωνοποιώντας το αποθετήριο:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Δημιουργήστε ένα αρχείο `.env`, στον κατάλογο `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Ανάπτυξη του OpenClaw με Podman Compose

Πριν προχωρήσετε, βεβαιωθείτε ότι έχετε κατεβάσει την πιο πρόσφατη εικόνα Docker του OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Μόλις ολοκληρωθεί αυτό, κατεβάστε το αρχείο Compose του OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) και τοποθετήστε το στον ριζικό κατάλογο `/firecrawl`:

> Αυτή η σύμβαση είναι απαραίτητη ώστε το `systemd` να εντοπίσει και να ξεκινήσει σωστά την υπηρεσία, όπως ορίζεται στο `WorkingDirectory=${HOME}/firecrawl`.

> Μπορείτε πάντα να επεκτείνετε τη στοίβα προσθέτοντας επιπλέον υπηρεσίες Firecrawl ανάλογα με τις ανάγκες σας. Η πλήρης λίστα των διαθέσιμων υπηρεσιών βρίσκεται στο επίσημο [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Εκκίνηση της υπηρεσίας OpenClaw μέσω Firecrawl

Πριν παραδώσετε τον έλεγχο στο `systemd`, επαληθεύστε ότι όλα λειτουργούν σωστά εκτελώντας τη στοίβα χειροκίνητα:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Αν όλα έχουν διαμορφωθεί σωστά, θα πρέπει να δείτε το container του OpenClaw να ξεκινά και η έξοδος της γραμμής εντολών σας θα πρέπει να μοιάζει με αυτό:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Αφού το επαληθεύσετε, τερματίστε τη στοίβα πριν συνεχίσετε:
```bash
podman compose -f openclaw-compose.yaml down
```
Πριν ξεκινήσετε την υπηρεσία, πρέπει να βεβαιωθείτε ότι έχουν οριστεί η σωστή ιδιοκτησία και τα δικαιώματα για τον κατάλογο `firecrawl` και το αρχείο `.env` του.
Αυτό είναι απαραίτητο ώστε η υπηρεσία να μπορεί να γράψει τα διαπιστευτήριά σας κατά την εκκίνηση.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Τώρα που όλα έχουν επαληθευτεί, ξεκινήστε την υπηρεσία μέσω του `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Οι Ενέργειες του OpenClaw](https://docs.openclaw.ai/) είναι προσβάσιμες μέσα από το διαδραστικό container, και ο Web Dashboard είναι διαθέσιμος στον ίδιο host και port στο http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Απόκτηση του `OPENCLAW_GATEWAY_TOKEN`

Μόλις η υπηρεσία τεθεί σε λειτουργία, θα παρατηρήσετε έναν νέο κατάλογο `.openclaw` που έχει δημιουργηθεί στον φάκελο του χρήστη σας (~/.openclaw). Αυτός ο κατάλογος είναι κλειδωμένος από προεπιλογή, οπότε θα χρειαστεί να τον ξεκλειδώσετε για να ανακτήσετε το token του gateway σας.

1. Παραχωρήστε πρόσβαση στον κατάλογο:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Διαβάστε το token του gateway σας:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Εντοπίστε την τιμή `OPENCLAW_GATEWAY_TOKEN` στην έξοδο.

3. Ανοίξτε τον πίνακα ελέγχου του gateway στο πρόγραμμα περιήγησής σας http://127.0.0.1:18789. Επικολλήστε το token σας όταν σας ζητηθεί να πιστοποιηθείτε.

Για να σταματήσετε την υπηρεσία, εκτελέστε:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Εκκίνηση του OpenClaw Gateway

Το gateway είναι η διεργασία OpenClaw που διαχειρίζεται τον βρόχο του agent και εξυπηρετεί το dashboard:

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

Για να ανοίξετε το dashboard, εκτελέστε το εξής σε ένα δεύτερο τερματικό ενώ το gateway εξακολουθεί να εκτελείται:

```bash
openclaw dashboard
```

Επειδή το gateway συνδέεται στο loopback, το dashboard πιστοποιείται αυτόματα όταν ανοίγει από το ίδιο μηχάνημα, δεν απαιτείται εισαγωγή token ή έγκριση συσκευής για τοπική πρόσβαση. Θα πρέπει να δείτε το dashboard του OpenClaw με το μοντέλο Lemonade σας να εμφανίζεται ως το ενεργό backend.

> Εάν έχετε ενεργοποιήσει το sandboxing, μπορείτε να το επαληθεύσετε ζητώντας από τον agent να εκτελέσει `run hostname` από το dashboard. Εάν δείτε ένα σύντομο container ID αντί για το hostname του μηχανήματός σας, το sandbox λειτουργεί.

**Συγχαρητήρια, έχετε δημιουργήσει ένα πλήρως τοπικό AI agent stack από την αρχή.**

> **Χρειάζεστε το token του gateway;** Εκτελέστε `openclaw dashboard --no-open` για να εκτυπώσετε το URL του dashboard με το token ενσωματωμένο (προσπαθεί επίσης να το αντιγράψει στο πρόχειρό σας). Εναλλακτικά, το token βρίσκεται στο `gateway.auth.token` μέσα στο `~/.openclaw/openclaw.json`.

**Πρόσβαση στο Dashboard από Άλλη Συσκευή (μέσω SSH Tunnel)**

Εάν το OpenClaw εκτελείται σε ένα απομακρυσμένο μηχάνημα, μπορείτε να προσπελάσετε το dashboard του από το τοπικό σας μηχάνημα μέσω ενός SSH tunnel. Το tunnel προωθεί τη θύρα του gateway (`18789`) ώστε ο τοπικός σας browser να μπορεί να επικοινωνεί με το απομακρυσμένο gateway μέσω `127.0.0.1`.

1. Από το **τοπικό σας μηχάνημα**, συνδεθείτε μία φορά στο απομακρυσμένο μηχάνημα και αποδεχτείτε το μήνυμα fingerprint ώστε ο host να προστεθεί στους γνωστούς σας hosts:

   ```bash
   ssh user@<host-ip>
   ```

2. Ακόμα στο **τοπικό σας μηχάνημα**, ανοίξτε το SSH tunnel:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Σημείωση:** Αφού εισαγάγετε τον κωδικό πρόσβασής σας, το τερματικό δεν εμφανίζει καμία έξοδο και φαίνεται να έχει κολλήσει. Αυτό είναι αναμενόμενο: η σημαία `-N` λέει στο SSH να μην εκτελέσει καμία απομακρυσμένη εντολή, οπότε απλώς κρατά το tunnel ανοιχτό. Αφήστε αυτό το τερματικό να εκτελείται.

3. Στο **τοπικό σας μηχάνημα**, ανοίξτε έναν browser και μεταβείτε στο `http://127.0.0.1:18789`.

4. Στο **απομακρυσμένο μηχάνημα**, εκτυπώστε το token του gateway και επικολλήστε το στον browser για να συνδεθείτε:

   ```bash
   openclaw dashboard --no-open
   ```

   Αυτό εκτυπώνει το URL του dashboard με το token ενσωματωμένο· αντιγράψτε το token για να συνδεθείτε. (Το token αποθηκεύεται επίσης στο `gateway.auth.token` μέσα στο `~/.openclaw/openclaw.json`.)

> **Έγκριση απομακρυσμένης συσκευής:** Όταν ανοίγετε το dashboard από άλλο μηχάνημα ή τηλέφωνο, ο browser ενδέχεται να εμφανίσει ένα request ID. Στο **απομακρυσμένο μηχάνημα**, εμφανίστε τα εκκρεμή αιτήματα:
> ```bash
> openclaw devices list
> ```
> Στη συνέχεια εγκρίνετε το αντίστοιχο αίτημα:
> ```bash
> openclaw devices approve <requestId>
> ```
> Αυτό απαιτείται μόνο για απομακρυσμένες ή δευτερεύουσες συσκευές· η πρόσβαση loopback από το ίδιο μηχάνημα πιστοποιείται αυτόματα. Δείτε την τεκμηρίωση [Remote Access](https://docs.openclaw.ai/gateway/remote) για λεπτομέρειες.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Προαιρετικό: Σύνδεση Καναλιού Επικοινωνίας

Μόλις το gateway εκτελείται, μπορείτε να προσπελάσετε τον τοπικό σας agent από οποιαδήποτε συσκευή. Επιλέξτε την επιλογή που ταιριάζει στη ρύθμισή σας. Το OpenClaw υποστηρίζει [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), και άλλα κανάλια, δείτε την πλήρη λίστα στο [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Επιλογή Α: Discord

Το Discord απαιτεί έναν server στον οποίο **έχετε δικαιώματα διαχειριστή** για να προσθέσετε ένα bot. Εάν μοιράζεστε servers αλλά δεν κατέχετε κάποιον, χρησιμοποιήστε την Επιλογή Β (Telegram) αντ' αυτού.

#### Δημιουργία λογαριασμού και server στο Discord

Εάν δεν έχετε λογαριασμό Discord, εγγραφείτε στο [discord.com](https://discord.com). Χρειάζεστε επίσης έναν server στον οποίο είστε διαχειριστής, δημιουργήστε έναν κάνοντας κλικ στο εικονίδιο **+** στην πλαϊνή μπάρα του Discord και επιλέγοντας **Create My Own**. Ένας ιδιωτικός server είναι μια χαρά.

#### Δημιουργία εφαρμογής και bot στο Discord

1. Μεταβείτε στο [Discord Developer Portal](https://discord.com/developers/applications) και κάντε κλικ στο **New Application**. Δώστε του ένα όνομα (π.χ. "openclaw-bot").
2. Στην πλαϊνή μπάρα, κάντε κλικ στο **Bot**. Ορίστε ένα username για το bot.
3. Ακόμα στη σελίδα Bot, μεταβείτε στο **Privileged Gateway Intents** και ενεργοποιήστε:
   - **Message Content Intent** (απαιτείται)
   - **Server Members Intent** (προτείνεται)
4. Επιστρέψτε πάνω και κάντε κλικ στο **Reset Token** για να δημιουργήσετε το bot token σας. Αντιγράψτε το.

#### Προσθήκη του bot στον server σας

1. Στην πλαϊνή μπάρα, κάντε κλικ στο **OAuth2/ URL Generator**.
2. Στο **Scopes**, ενεργοποιήστε `bot` και `applications.commands`.
3. Στο **Bot Permissions**, ενεργοποιήστε: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Αντιγράψτε το URL που δημιουργήθηκε, επικολλήστε το στον browser σας, επιλέξτε τον server σας και επιβεβαιώστε. Το bot θα πρέπει πλέον να εμφανίζεται στη λίστα μελών του server σας.

#### Συλλογή των IDs σας

Ενεργοποιήστε το Developer Mode στο Discord (**User Settings/ Advanced/ Developer Mode**), στη συνέχεια:
- Δεξί κλικ στο εικονίδιο του server σας: **Copy Server ID**
- Δεξί κλικ στο δικό σας avatar: **Copy User ID**

#### Επιτρέψτε DMs από μέλη server

Δεξί κλικ στο εικονίδιο του server σας/ **Privacy Settings**/ ενεργοποιήστε το **Direct Messages**. Αυτό επιτρέπει στο bot να σας στείλει DM, κάτι που απαιτείται για το βήμα pairing.

#### Διαμόρφωση του OpenClaw για Discord

Αποθηκεύστε το token του bot σας ως μεταβλητή περιβάλλοντος, στη συνέχεια δημιουργήστε ένα ενιαίο αρχείο patch που ενεργοποιεί το Discord, αναφέρεται στο token και επιτρέπει τον server σας μέσω allowlist. Αντικαταστήστε το `<server_id>` και το `<user_id>` με τα IDs που συλλέξατε παραπάνω.

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

> **Μη βασίζεστε στο να ζητήσετε από τον agent να το διαμορφώσει αυτό.** Όταν το sandboxing είναι ενεργοποιημένο, ο agent δεν μπορεί να γράψει στο `~/.openclaw/openclaw.json` από μέσα στο sandbox, χρησιμοποιήστε αντ' αυτού τις παραπάνω εντολές CLI στον host.

Επανεκκινήστε το gateway ώστε να λάβει τη νέα διαμόρφωση καναλιού:

```bash
openclaw gateway run --bind loopback --port 18789
```

Θα πρέπει να δείτε `logged in to discord as <bot-name>` στην έξοδο του gateway μέσα σε λίγα δευτερόλεπτα.
#### Αντιστοιχίστε τον λογαριασμό σας στο Discord

Στείλτε προσωπικό μήνυμα στο bot μέσα στο Discord. Θα σας απαντήσει με έναν σύντομο κωδικό αντιστοίχισης.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Εγκρίνετέ τον στο μηχάνημα όπου εκτελείται το OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Οι κωδικοί αντιστοίχισης λήγουν μετά από μία ώρα.

Μπορείτε τώρα να συνομιλήσετε απευθείας με τον agent σας μέσω Discord και να αναθέσετε εργασίες στο τοπικό σας υλικό.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Επιλογή Β: Telegram

Το Telegram είναι απλούστερο από το Discord για τους περισσότερους χρήστες, καθώς δεν απαιτεί διακομιστή ούτε δικαιώματα διαχειριστή.

#### Δημιουργία bot στο Telegram

1. Ανοίξτε το Telegram και στείλτε μήνυμα στο **@BotFather**.
2. Στείλτε `/newbot` και ακολουθήστε τις οδηγίες. Αποθηκεύστε το token του bot που σας δίνει.

#### Διαμόρφωση του OpenClaw για το Telegram

Αποθηκεύστε το token ως μεταβλητή περιβάλλοντος:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Προσθέστε τη διαμόρφωση του καναλιού στο `~/.openclaw/openclaw.json` (ή εφαρμόστε το patch μέσω του dashboard):

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

Επανεκκινήστε το gateway και, στη συνέχεια, στείλτε οποιοδήποτε μήνυμα στο bot σας στο Telegram. Εγκρίνετε την αντιστοίχιση:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Οι κωδικοί αντιστοίχισης λήγουν μετά από μία ώρα. Μπορείτε τώρα να συνομιλήσετε με τον agent σας μέσω προσωπικών μηνυμάτων στο Telegram.

---

## Επόμενα βήματα

Τώρα που ο agent σας μπορεί να λαμβάνει εντολές από το τηλέφωνό σας και να ενεργεί στο τοπικό σας μηχάνημα, ακολουθούν τρεις κατευθύνσεις που αξίζει να διερευνήσετε:

1. **Σύνοψη χρηματιστηριακών δεδομένων**: Προγραμματίστε το OpenClaw να αντλεί δεδομένα από χρηματοοικονομικά API σε σταθερό διάστημα, να συνοψίζει τις κινήσεις της ημέρας με το τοπικό σας μοντέλο και να στέλνει μια καθημερινή περίληψη στο τηλέφωνό σας μέσω του καναλιού της επιλογής σας.

2. **Παρακολούθηση fine-tuning**: Ξεκινήστε μια εργασία εκπαίδευσης εξ αποστάσεως μέσω Telegram ή Discord και, στη συνέχεια, αφήστε τον agent να παρακολουθεί το αρχείο καταγραφής της εκπαίδευσης και να αναφέρει περιοδικά τιμές απώλειας, χρήση GPU και χρήση δίσκου στο τηλέφωνό σας. Εάν η εκτέλεση κολλήσει ή η χρήση VRAM αυξηθεί απότομα, θα το μάθετε αμέσως χωρίς να χρειάζεται να βρίσκεστε στο μηχάνημα.

3. **IOT με τοπικό VLM**: Στρέψτε μια κάμερα προς την μπροστινή σας πόρτα, εκτελέστε ένα μοντέλο όρασης στο Lemonade και αφήστε το OpenClaw να αναλύει καρέ κατ' απαίτηση ή με βάση κάποιο trigger. Ρωτήστε «ήρθαν δέματα σήμερα;» από το τηλέφωνό σας και λάβετε μια σαφή απάντηση από το δικό σας υλικό.

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