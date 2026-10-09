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

Το [**OpenClaw**](https://openclaw.ai/) είναι ένας αυτόνομος πράκτορας AI που μπορεί να γράφει και να εκτελεί κώδικα, να διαχειρίζεται αρχεία και να εκτελεί πολύπλοκες εργασίες πολλαπλών βημάτων για λογαριασμό σας. Σε αντίθεση με έναν βοηθό συνομιλίας που απλώς απαντά σε ερωτήσεις, το OpenClaw εκτελεί πραγματικές ενέργειες στο σύστημά σας, κάτι που σημαίνει ότι χρειάζεται ένα γρήγορο, ικανό backend AI που μπορεί να ανταποκριθεί σε έναν απαιτητικό βρόχο πράκτορα.

Το [**Lemonade Server**](https://lemonade-server.ai/) είναι αυτό το backend. Είναι ένας open-source τοπικός server inference που εκτελεί μοντέλα GenAI απευθείας στο υλικό σας και τα εκθέτει μέσω του βιομηχανικού προτύπου OpenAI API.

Μαζί, αποτελούν έναν πλήρως τοπικό στοίβα AI πράκτορα: το Lemonade χειρίζεται το inference μοντέλων, ενώ το OpenClaw παρέχει τον βρόχο πράκτορα που μετατρέπει τις εξόδους μοντέλων σε πραγματικές ενέργειες.

> **Πριν συνεχίσετε:** Το OpenClaw είναι ένας εξαιρετικά αυτόνομος πράκτορας AI. Η παροχή πρόσβασης σε οποιονδήποτε πράκτορα AI στο σύστημά σας μπορεί να οδηγήσει σε απρόβλεπτα ή ανεπιθύμητα αποτελέσματα. Προχωρήστε μόνο εάν κατανοείτε τους κινδύνους και νιώθετε άνετα με αυτόνομο λογισμικό που ενεργεί για λογαριασμό σας.

---

## Τι θα μάθετε

Μέχρι το τέλος αυτού του playbook θα μπορείτε να:

- Μάθετε για το **Lemonade Server**
- **Εγκαταστήσετε το OpenClaw** και **να το κατευθύνετε προς το Lemonade Server** ως backend AI.
- **Ξεκινήσετε το gateway του OpenClaw** και να επιβεβαιώσετε ότι ο πράκτοράς σας είναι έτοιμος να εργαστεί.
- **Συνδέσετε ένα κανάλι επικοινωνίας** (Discord ή Telegram) ώστε να μπορείτε να συνομιλείτε με τον πράκτορά σας από οποιαδήποτε συσκευή.

---

<!-- @device:halo_box,halo,stx,krk -->
## Ρύθμιση Διαμόρφωσης Μνήμης

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
- **~10–30 GB ελεύθερου χώρου στον δίσκο** για τα βάρη των μοντέλων
<!-- @os:end -->

<!-- @os:windows -->
- Ένας υπολογιστής με **Windows 10/11**
- Τουλάχιστον **12 GB RAM** (συνιστώνται 64 GB+ για μεγαλύτερα μοντέλα)
- **~10–30 GB ελεύθερου χώρου στον δίσκο** για τα βάρη των μοντέλων
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Προαιρετικό, για sandboxing του OpenClaw)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @os:linux -->
<!-- @prereq:nodejs -->
<!-- @os:end -->
<!-- On Windows OpenClaw runs in WSL, so its Node.js is covered by the openclaw prereq. -->
<!-- @prereq:docker,openclaw,lemonade-models-qwen3-6-35b-a3b,lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Λήψη και Φόρτωση του Προτεινόμενου Μοντέλου

Το προτεινόμενο μοντέλο για αυτό το playbook είναι το **Qwen3.6-35B-A3B-GGUF** από την Unsloth, ένα ισχυρό μοντέλο MoE με παράθυρο συμφραζομένων 263k tokens που είναι κατάλληλο για φόρτους εργασίας πρακτόρων. Αυτό το μοντέλο χρησιμοποιεί κβαντισμό UD-Q4_K_XL. Κάντε λήψη του τώρα:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Στη συνέχεια, φορτώστε το με ένα μεγάλο παράθυρο συμφραζομένων και αποθηκεύστε αυτή τη ρύθμιση για μελλοντικές εκτελέσεις:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Το μοντέλο έχει ένα προεπιλεγμένο μήκος συμφραζομένων 262.144 tokens. Εάν αντιμετωπίσετε σφάλματα εξάντλησης μνήμης (OOM), εξετάστε το ενδεχόμενο μείωσης του παραθύρου συμφραζομένων. Ωστόσο, επειδή το Qwen3.6 αξιοποιεί εκτεταμένα συμφραζόμενα για σύνθετες εργασίες, συνιστούμε τη διατήρηση ενός μήκους συμφραζομένων τουλάχιστον 128K tokens για τη διατήρηση των δυνατοτήτων σκέψης.

> **Συμβουλή: Απενεργοποιήστε τη σκέψη για ταχύτερες αποκρίσεις πράκτορα:** Το Qwen3.6-35B-A3B εκτελείται σε λειτουργία σκέψης από προεπιλογή, η οποία προσθέτει καθυστέρηση πριν από κάθε απόκριση. Για βρόχους πρακτόρων αυτή η επιβάρυνση συσσωρεύεται γρήγορα. Το αποθετήριο [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) παρέχει μια έτοιμη διαμόρφωση που απενεργοποιεί τη σκέψη. Για να τη χρησιμοποιήσετε, κάντε λήψη του αρχείου και εισαγάγετέ το:
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

Εκτελούμε το OpenClaw μέσα στο WSL (Προτείνεται) και το συνδέουμε με το Lemonade που εκτελείται εγγενώς στα Windows. Αυτό σας παρέχει ένα περιβάλλον κελύφους Linux για το OpenClaw, διατηρώντας παράλληλα την επιτάχυνση GPU του Lemonade στην πλευρά των Windows.

### Εγκατάσταση του WSL και του Ubuntu

Ανοίξτε το PowerShell ως Διαχειριστής και εγκαταστήστε τον πυρήνα WSL:

```powershell
wsl --install --no-distribution
```

Στη συνέχεια, εγκαταστήστε το Ubuntu:

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

Εξέλθετε από το WSL και επανεκκινήστε το:

```powershell
exit
wsl --shutdown
wsl
```

### Γεφύρωση του Lemonade από τα Windows στο WSL

Το WSL2 εκτελείται σε ένα εικονικό δίκτυο. Το Lemonade στα Windows συνδέεται στο `127.0.0.1`, το οποίο το WSL δεν μπορεί να προσπελάσει απευθείας. Ένας port proxy των Windows προωθεί την κίνηση από την IP πύλης του WSL στο localhost των Windows.

**Βρείτε την IP πύλης του WSL** (εκτελέστε μέσα στο WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Προσθέστε τον port proxy** (εκτελέστε στο PowerShell ως Διαχειριστής, αντικαθιστώντας το `<WSL-Gateway-IP>` με την IP πύλης του WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Σημείωση: Εάν αντιμετωπίσετε σφάλμα `netsh: command not found`, δοκιμάστε να χρησιμοποιήσετε το ρητό όνομα εκτελέσιμου αρχείου - `netsh.exe`

**Προσθέστε έναν κανόνα τείχους προστασίας** (στο ίδιο ανυψωμένο PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Επαληθεύστε από το WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Αν έχετε ήδη φορτώσει το μοντέλο Qwen3.6-35B-A3B-GGUF στο προηγούμενο βήμα, θα πρέπει να δείτε έξοδο JSON όπως αυτή:

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

Ο κανόνας `netsh portproxy` επιβιώνει τις επανεκκινήσεις, αλλά η IP του gateway του WSL μπορεί να αλλάξει μετά από `wsl --shutdown` ή επανεκκίνηση. Όταν συμβεί αυτό, ο proxy εξακολουθεί να δείχνει στην παλιά IP και το Lemonade γίνεται μη προσβάσιμο από το WSL. Αν συμβεί αυτό, χρησιμοποιήστε μία από τις παρακάτω επιλογές.

**Επιλογή 1 (συνιστάται) — Αυτόματη επιδιόρθωση της γέφυρας.** Για να αποφύγετε να το κάνετε αυτό χειροκίνητα κάθε φορά, χρησιμοποιήστε μια προγραμματισμένη εργασία που ελέγχει τη γέφυρα σε κάθε εκκίνηση και σύνδεση και την ανακατασκευάζει μόνο όταν η IP του gateway έχει αλλάξει. Δείτε τον [οδηγό αυτόματης επιδιόρθωσης γέφυρας Lemonade WSL](assets/RepairLemonadeWslBridge.md).

**Επιλογή 2 — Χειροκίνητη επιδιόρθωση της γέφυρας.** Πρώτα, αποκτήστε την τρέχουσα IP του gateway του WSL εκτελώντας αυτό μέσα στο WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Αντιγράψτε αυτή την τιμή· θα τη χρησιμοποιήσετε στη θέση του `<new-WSL-Gateway-IP>` παρακάτω.

Στη συνέχεια, σε ένα **elevated PowerShell** (Εκτέλεση ως διαχειριστής), παραθέστε τους υπάρχοντες κανόνες, διαγράψτε μόνο τον παλιό κανόνα Lemonade και προσθέστε έναν νέο με την τρέχουσα IP:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

Στην έξοδο της `show all`, ο παλιός κανόνας Lemonade είναι η καταχώρηση της οποίας η διεύθυνση σύνδεσης είναι `127.0.0.1` στη θύρα `13305`· η διεύθυνση ακρόασής της είναι η δική σας `<old-WSL-Gateway-IP>`. Η διαγραφή με βάση αυτή τη διεύθυνση αφαιρεί μόνο αυτόν τον κανόνα και αφήνει ανέπαφους τυχόν άλλους κανόνες port-proxy στον υπολογιστή σας.

Ο κανόνας τείχους προστασίας που προσθέσατε κατά τη ρύθμιση είναι συνδεδεμένος με τη θύρα `13305` (όχι με την IP), οπότε συνεχίζει να λειτουργεί και δεν χρειάζεται να δημιουργηθεί ξανά.

> **Σύσταση:** Για να αποφύγετε προβλήματα με το gateway, συνιστούμε ιδιαίτερα την παρακάτω διαμόρφωση κελύφους:
> - Οι **εντολές Windows** πρέπει να εκτελούνται σε **PowerShell**
> - Οι **εντολές διανομής WSL** πρέπει να εκτελούνται σε **Command Prompt** (εκτέλεση ως **Διαχειριστής**)

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

Η σημαία `--no-onboard` παρακάμπτει τον διαδραστικό οδηγό ρύθμισης, θα διαμορφώσετε το backend του μοντέλου χειροκίνητα στο επόμενο βήμα, κάτι που σας δίνει ακριβή έλεγχο για το ποιο μοντέλο και εξυπηρετητής χρησιμοποιούνται.

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


### Διαμόρφωση του OpenClaw για Χρήση του Lemonade

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

> **Μέγεθος παραθύρου περιβάλλοντος OpenClaw:** Η συμπίεση του OpenClaw ενεργοποιείται όταν `contextTokens > contextWindow − reserveTokens`. Το προεπιλεγμένο `reserveTokensFloor` είναι 20.000 tokens, ένα κατώτατο όριο που υπερισχύει του `reserveTokens` όταν αυτό είναι χαμηλότερο, οπότε οποιοδήποτε παράθυρο περιβάλλοντος μοντέλου κάτω από ~37k θα ενεργοποιήσει έναν ατέρμονα βρόχο συμπίεσης. Ορίστε ένα χαμηλό reserve και απενεργοποιήστε το κατώτατο όριο μία φορά στη διαμόρφωσή σας και εφαρμόζεται σε κάθε μοντέλο, χωρίς να χρειάζεται ρύθμιση ανά μοντέλο:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> Το `reserveTokensFloor` είναι ένα *κατώτατο όριο* (ελάχιστη διασφάλιση), όχι το ίδιο το reserve· ο ορισμός μόνο του κατώτατου ορίου δεν έχει κανένα αποτέλεσμα. Το `reserveTokensFloor: 0` απενεργοποιεί τη διασφάλιση ώστε να γίνει αποδεκτό το χαμηλότερο `reserveTokens`.
>
> **Πότε να το εφαρμόσετε:** Χρησιμοποιήστε αυτή τη διαμόρφωση αν το ενεργό παράθυρο περιβάλλοντος του μοντέλου σας είναι κάτω από ~37k, είτε επειδή το μοντέλο είναι μικρό (π.χ. 8k, 16k, 32k) είτε επειδή το έχετε εσκεμμένα περιορίσει σε χαμηλότερη τιμή (π.χ. φόρτωση ενός μοντέλου 128k αλλά ορισμός του περιβάλλοντος σε 16k στο Lemonade). Χωρίς αυτό, το OpenClaw εισέρχεται σε ατέρμονα βρόχο συμπίεσης κατά την εκκίνηση.
>
> **Μοντέλα μεγάλου περιβάλλοντος σε πλήρες περιβάλλον:** Μπορείτε να το παραλείψετε εντελώς αυτό. Οι προεπιλογές λειτουργούν μια χαρά, η συμπίεση θα ενεργοποιηθεί αρκετά πριν γεμίσει το παράθυρο και το μοντέλο έχει άφθονο χώρο για να παράγει μεγάλες απαντήσεις. Αν το εφαρμόσετε, λάβετε υπόψη ότι το `reserveTokens: 4096` περιορίζει το μήκος της απάντησης σε ~4k tokens, κάτι που μπορεί να κόψει τη δημιουργία μεγάλων αρχείων ή λεπτομερών σχεδίων.
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
> Το υπόλοιπο της διαμόρφωσής σας (gateway, κανάλια, μοντέλα, κ.λπ.) παραμένει αμετάβλητο, μόνο το κλειδί `compaction` χρειάζεται να προστεθεί.
### (Προτεινόμενο) Ενεργοποίηση Docker Sandboxing

Το OpenClaw μπορεί να δρομολογεί όλες τις λειτουργίες αρχείων και κώδικα του agent μέσω ενός απομονωμένου container Docker αντί να τις εκτελεί απευθείας στον host σας. Αυτό περιορίζει την ακτίνα επίδρασης οποιασδήποτε ακούσιας ενέργειας στο sandbox, αφήνοντας το σύστημα αρχείων και το δίκτυο του host σας ανέπαφα.

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

Εκτελέστε το εξής για να προσθέσετε το κλειδί `sandbox` μέσα στο υπάρχον μπλοκ `agents.defaults` στο `~/.openclaw/openclaw.json`:

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

> #### Αντιμετώπιση προβλημάτων: Άρνηση Δικαιώματος Docker
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
> **Βήμα 2: Εάν το σφάλμα παραμένει, εφαρμόστε τη μόνιμη λύση**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Στη συνέχεια κάντε **επανεκκίνηση** του συστήματός σας.
> 
> **Γρήγορη προσωρινή λύση** (επαναφέρεται μετά την επανεκκίνηση):
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
## (Προτεινόμενο) Ενσωμάτωση OpenClaw με Υπηρεσίες Firecrawl

Το [Firecrawl](https://docs.firecrawl.dev/introduction) παρέχει μια αυτοφιλοξενούμενη (self-hosted) υπηρεσία web crawling και εξαγωγής περιεχομένου που μπορεί να παρακάμψει αυτές τις προκλήσεις και να ξεκλειδώσει το πλήρες δυναμικό της αυτοματοποίησης του OpenClaw.

Σε αυτή τη διαμόρφωση, το OpenClaw εκτελείται ως ένα σύνολο containers Docker που διαχειρίζεται το Podman. Για να απλοποιήσουμε τη διαχείριση κύκλου ζωής και την αυτόματη εκκίνηση, καταχωρούμε το Firecrawl ως υπηρεσία `systemd` επιπέδου χρήστη που οργανώνει το υποκείμενο στοίβαγμα Podman Compose. Αυτό επιτρέπει στο OpenClaw να εκκινεί τον gateway, να σταματά και να επαληθεύει την υπηρεσία Firecrawl χρησιμοποιώντας τυπικές εντολές `systemctl --user` αντί να αλληλεπιδρά απευθείας με τα containers.

Για απλότητα, χωρίσαμε όλη τη διαδικασία σε τέσσερα βήματα:

---

### 1. Καταχώρηση της υπηρεσίας συστήματος
Μεταβείτε στον κατάλογο διαμόρφωσης χρήστη systemd:
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
Σε αυτό το σημείο, η υπηρεσία έχει οριστεί αλλά δεν έχει ακόμη καταχωρηθεί στο `systemd`.
Βεβαιωθείτε ότι το όνομα αρχείου ταιριάζει ακριβώς με αυτό που δημιουργήσατε παραπάνω, και στη συνέχεια εκτελέστε:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Εάν η διαδικασία ήταν επιτυχής, θα πρέπει να δείτε την εξής έξοδο:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 Ο κατάλογος `default.target.wants/` περιέχει συμβολικούς συνδέσμους προς υπηρεσίες που έχουν διαμορφωθεί να εκκινούν αυτόματα.

### 2. Διαμόρφωση του Firecrawl

Το [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) είναι ιδανικό για όσους χρειάζονται πλήρη έλεγχο των περιβαλλόντων scraping και επεξεργασίας δεδομένων τους, αλλά συνοδεύεται από το κόστος επιπλέον προσπάθειας συντήρησης και διαμόρφωσης.

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

Προτού προχωρήσετε, βεβαιωθείτε ότι έχετε κατεβάσει την πιο πρόσφατη εικόνα Docker του OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Μόλις ολοκληρωθεί αυτό, κατεβάστε το αρχείο Compose του OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) και τοποθετήστε το στον κεντρικό κατάλογο `/firecrawl`:

> Αυτή η σύμβαση είναι απαραίτητη ώστε το `systemd` να εντοπίσει και να εκκινήσει σωστά την υπηρεσία, όπως ορίζεται στο `WorkingDirectory=${HOME}/firecrawl`.

> Μπορείτε πάντα να επεκτείνετε τη στοίβα προσθέτοντας επιπλέον υπηρεσίες Firecrawl όπως χρειάζεται. Η πλήρης λίστα των διαθέσιμων υπηρεσιών βρίσκεται στο επίσημο [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Εκκίνηση της υπηρεσίας OpenClaw μέσω Firecrawl

Πριν παραδώσετε τον έλεγχο στο `systemd`, επαληθεύστε ότι όλα λειτουργούν σωστά εκτελώντας τη στοίβα χειροκίνητα:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Εάν όλα έχουν διαμορφωθεί σωστά, θα πρέπει να δείτε το container OpenClaw να ενεργοποιείται και η έξοδος της γραμμής εντολών σας θα πρέπει να μοιάζει με την εξής:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Μόλις το επαληθεύσετε, κατεβάστε ξανά τη στοίβα πριν προχωρήσετε:
```bash
podman compose -f openclaw-compose.yaml down
```
Πριν εκκινήσετε την υπηρεσία, πρέπει να βεβαιωθείτε ότι έχουν οριστεί η σωστή κυριότητα και τα σωστά δικαιώματα στον κατάλογο `firecrawl` και στο αρχείο `.env` του.
Αυτό είναι απαραίτητο για να μπορεί η υπηρεσία να γράψει τα διαπιστευτήριά σας κατά την εκκίνηση.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Τώρα που όλα έχουν επαληθευτεί, εκκινήστε την υπηρεσία μέσω `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Οι Ενέργειες OpenClaw](https://docs.openclaw.ai/) είναι προσβάσιμες από το εσωτερικό του διαδραστικού container, και ο Web Dashboard είναι διαθέσιμος στον ίδιο host και θύρα στη διεύθυνση http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Απόκτηση του `OPENCLAW_GATEWAY_TOKEN`

Μόλις η υπηρεσία τεθεί σε λειτουργία, θα παρατηρήσετε ότι έχει δημιουργηθεί ένας νέος κατάλογος `.openclaw` στον αρχικό σας φάκελο (~/.openclaw). Αυτός ο κατάλογος είναι κλειδωμένος από προεπιλογή, οπότε θα χρειαστεί να τον ξεκλειδώσετε για να ανακτήσετε το token του gateway σας.

1. Παραχωρήστε πρόσβαση στον κατάλογο:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Διαβάστε το token του gateway σας:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Εντοπίστε την τιμή `OPENCLAW_GATEWAY_TOKEN` στην έξοδο.

3. Ανοίξτε τον πίνακα ελέγχου (dashboard) του gateway στο πρόγραμμα περιήγησής σας στη διεύθυνση http://127.0.0.1:18789. Επικολλήστε το token σας όταν σας ζητηθεί για έλεγχο ταυτότητας.

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

Επειδή το gateway συνδέεται στο loopback, το dashboard πραγματοποιεί αυτόματη αυθεντικοποίηση όταν ανοίγει από τον ίδιο υπολογιστή, δεν απαιτείται εισαγωγή token ή έγκριση συσκευής για τοπική πρόσβαση. Θα πρέπει να δείτε το dashboard του OpenClaw με το μοντέλο Lemonade σας να εμφανίζεται ως το ενεργό backend.

> Αν έχετε ενεργοποιήσει το sandboxing, μπορείτε να το επαληθεύσετε ζητώντας από τον agent να εκτελέσει `run hostname` από το dashboard. Αν δείτε ένα σύντομο container ID αντί για το hostname του μηχανήματός σας, το sandbox λειτουργεί.

**Συγχαρητήρια, δημιουργήσατε από την αρχή ένα πλήρως τοπικό stack AI agent.**

> **Χρειάζεστε το token του gateway;** Εκτελέστε `openclaw dashboard --no-open` για να εκτυπωθεί η διεύθυνση URL του dashboard με ενσωματωμένο το token (επίσης επιχειρεί να το αντιγράψει στο πρόχειρό σας). Εναλλακτικά, το token βρίσκεται στο `gateway.auth.token` μέσα στο `~/.openclaw/openclaw.json`.

**Πρόσβαση στο Dashboard από Άλλη Συσκευή (μέσω SSH Tunnel)**

Αν το OpenClaw εκτελείται σε απομακρυσμένο μηχάνημα, μπορείτε να προσπελάσετε το dashboard του από τον τοπικό σας υπολογιστή μέσω ενός SSH tunnel. Το tunnel προωθεί τη θύρα του gateway (`18789`) ώστε ο τοπικός σας browser να μπορεί να επικοινωνεί με το απομακρυσμένο gateway μέσω `127.0.0.1`.

1. Από τον **τοπικό σας υπολογιστή**, συνδεθείτε μία φορά στο απομακρυσμένο μηχάνημα και αποδεχτείτε την προτροπή του fingerprint ώστε ο host να προστεθεί στους γνωστούς hosts σας:

   ```bash
   ssh user@<host-ip>
   ```

2. Ακόμα στον **τοπικό σας υπολογιστή**, ανοίξτε το SSH tunnel:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Σημείωση:** Αφού εισαγάγετε τον κωδικό πρόσβασής σας, το τερματικό δεν εμφανίζει καμία έξοδο και φαίνεται να έχει κολλήσει. Αυτό είναι αναμενόμενο: η σημαία `-N` λέει στο SSH να μην εκτελέσει καμία απομακρυσμένη εντολή, οπότε απλώς διατηρεί το tunnel ανοιχτό. Αφήστε αυτό το τερματικό να εκτελείται.

3. Στον **τοπικό σας υπολογιστή**, ανοίξτε έναν browser και πηγαίνετε στο `http://127.0.0.1:18789`.

4. Στο **απομακρυσμένο μηχάνημα**, εκτυπώστε το token του gateway και επικολλήστε το στον browser για να συνδεθείτε:

   ```bash
   openclaw dashboard --no-open
   ```

   Αυτό εκτυπώνει τη διεύθυνση URL του dashboard με ενσωματωμένο το token· αντιγράψτε το token για να συνδεθείτε. (Το token αποθηκεύεται επίσης στο `gateway.auth.token` μέσα στο `~/.openclaw/openclaw.json`.)

> **Έγκριση απομακρυσμένης συσκευής:** Όταν ανοίγετε το dashboard από άλλο μηχάνημα ή κινητό, ο browser ενδέχεται να εμφανίσει ένα request ID. Στο **απομακρυσμένο μηχάνημα**, καταγράψτε τα εκκρεμή αιτήματα:
> ```bash
> openclaw devices list
> ```
> Στη συνέχεια εγκρίνετε το αντίστοιχο αίτημα:
> ```bash
> openclaw devices approve <requestId>
> ```
> Αυτό απαιτείται μόνο για απομακρυσμένες ή δευτερεύουσες συσκευές, η πρόσβαση loopback από το ίδιο μηχάνημα πραγματοποιεί αυθεντικοποίηση αυτόματα. Δείτε την τεκμηρίωση [Remote Access](https://docs.openclaw.ai/gateway/remote) για λεπτομέρειες.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Προαιρετικό: Σύνδεση Καναλιού Επικοινωνίας

Μόλις το gateway εκτελείται, μπορείτε να προσπελάσετε τον τοπικό σας agent από οποιαδήποτε συσκευή. Επιλέξτε την επιλογή που ταιριάζει στη ρύθμισή σας. Το OpenClaw υποστηρίζει [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), και άλλα κανάλια, δείτε την πλήρη λίστα στο [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Επιλογή Α: Discord

Το Discord απαιτεί έναν server όπου **έχετε δικαιώματα διαχειριστή** για να προσθέσετε ένα bot. Αν μοιράζεστε servers αλλά δεν κατέχετε κάποιον, χρησιμοποιήστε την Επιλογή Β (Telegram) αντ' αυτού.

#### Δημιουργία λογαριασμού και server στο Discord

Αν δεν έχετε λογαριασμό Discord, εγγραφείτε στο [discord.com](https://discord.com). Χρειάζεστε επίσης έναν server όπου είστε διαχειριστής, δημιουργήστε έναν κάνοντας κλικ στο εικονίδιο **+** στην πλαϊνή μπάρα του Discord και επιλέγοντας **Create My Own**. Ένας ιδιωτικός server είναι αρκετός.

#### Δημιουργία εφαρμογής και bot στο Discord

1. Μεταβείτε στο [Discord Developer Portal](https://discord.com/developers/applications) και κάντε κλικ στο **New Application**. Δώστε του ένα όνομα (π.χ. "openclaw-bot").
2. Στην πλαϊνή μπάρα, κάντε κλικ στο **Bot**. Ορίστε ένα όνομα χρήστη για το bot.
3. Ακόμα στη σελίδα Bot, μεταβείτε στο **Privileged Gateway Intents** και ενεργοποιήστε:
   - **Message Content Intent** (απαιτείται)
   - **Server Members Intent** (συνιστάται)
4. Μετακινηθείτε πίσω προς τα πάνω και κάντε κλικ στο **Reset Token** για να δημιουργήσετε το token του bot σας. Αντιγράψτε το.

#### Προσθήκη του bot στον server σας

1. Στην πλαϊνή μπάρα, κάντε κλικ στο **OAuth2/ URL Generator**.
2. Στο **Scopes**, ενεργοποιήστε τα `bot` και `applications.commands`.
3. Στο **Bot Permissions**, ενεργοποιήστε: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Αντιγράψτε τη διεύθυνση URL που δημιουργήθηκε, επικολλήστε την στον browser σας, επιλέξτε τον server σας και επιβεβαιώστε. Το bot θα πρέπει τώρα να εμφανίζεται στη λίστα μελών του server σας.

#### Συλλογή των IDs σας

Ενεργοποιήστε τη λειτουργία Developer Mode στο Discord (**User Settings/ Advanced/ Developer Mode**), στη συνέχεια:
- Κάντε δεξί κλικ στο εικονίδιο του server σας: **Copy Server ID**
- Κάντε δεξί κλικ στο δικό σας avatar: **Copy User ID**

#### Να επιτρέπονται τα DM από μέλη του server

Δεξί κλικ στο εικονίδιο του server σας/ **Privacy Settings**/ ενεργοποιήστε το **Direct Messages**. Αυτό επιτρέπει στο bot να σας στείλει DM, κάτι που απαιτείται για το βήμα pairing.

#### Διαμόρφωση του OpenClaw για το Discord

Αποθηκεύστε το token του bot σας ως μεταβλητή περιβάλλοντος, στη συνέχεια δημιουργήστε ένα ενιαίο αρχείο patch που ενεργοποιεί το Discord, αναφέρεται στο token και προσθέτει τον server σας στη λίστα επιτρεπόμενων. Αντικαταστήστε τα `<server_id>` και `<user_id>` με τα IDs που συλλέξατε παραπάνω.

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

> **Μην βασίζεστε στο να ζητήσετε από τον agent να το ρυθμίσει.** Όταν το sandboxing είναι ενεργοποιημένο, ο agent δεν μπορεί να γράψει στο `~/.openclaw/openclaw.json` από μέσα στο sandbox, χρησιμοποιήστε αντ' αυτού τις παραπάνω εντολές CLI στον host.

Επανεκκινήστε το gateway ώστε να φορτώσει τη νέα διαμόρφωση καναλιού:

```bash
openclaw gateway run --bind loopback --port 18789
```

Θα πρέπει να δείτε `logged in to discord as <bot-name>` στην έξοδο του gateway μέσα σε λίγα δευτερόλεπτα.
#### Αντιστοίχιση του λογαριασμού σας Discord

Στείλτε μήνυμα στο bot στο Discord. Θα απαντήσει με έναν σύντομο κωδικό αντιστοίχισης.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Εγκρίνετέ τον στο μηχάνημα που εκτελεί το OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Οι κωδικοί αντιστοίχισης λήγουν μετά από μία ώρα.

Μπορείτε πλέον να συνομιλείτε με τον agent σας απευθείας από το Discord και να αναθέτετε εργασίες στο τοπικό σας υλικό.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Επιλογή Β: Telegram

Το Telegram είναι πιο απλό από το Discord για τους περισσότερους χρήστες, δεν απαιτεί server ούτε δικαιώματα διαχειριστή.

#### Δημιουργία ενός bot Telegram

1. Ανοίξτε το Telegram και στείλτε μήνυμα στο **@BotFather**.
2. Στείλτε `/newbot` και ακολουθήστε τις οδηγίες. Αποθηκεύστε το token του bot που σας δίνει.

#### Διαμόρφωση του OpenClaw για το Telegram

Αποθηκεύστε το token ως μεταβλητή περιβάλλοντος:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Προσθέστε τη διαμόρφωση καναλιού στο `~/.openclaw/openclaw.json` (ή εφαρμόστε την μέσω του dashboard):

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

Επανεκκινήστε το gateway και στείλτε στο bot σας οποιοδήποτε μήνυμα στο Telegram. Εγκρίνετε την αντιστοίχιση:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Οι κωδικοί αντιστοίχισης λήγουν μετά από μία ώρα. Μπορείτε πλέον να συνομιλείτε με τον agent σας μέσω DM στο Telegram.

---

## Επόμενα Βήματα

Τώρα που ο agent σας μπορεί να λαμβάνει εντολές από το κινητό σας και να ενεργεί στο τοπικό σας μηχάνημα, εδώ είναι τρεις κατευθύνσεις που αξίζει να εξερευνήσετε:

1. **Περίληψη χρηματιστηριακής αγοράς**: Προγραμματίστε το OpenClaw να αντλεί δεδομένα από χρηματοοικονομικά API σε σταθερό διάστημα, να συνοψίζει τις κινήσεις της ημέρας με το τοπικό σας μοντέλο και να στέλνει μια περίληψη στο κινητό σας κάθε πρωί μέσω του καναλιού της επιλογής σας.

2. **Παρακολούθηση fine-tuning**: Ξεκινήστε μια εργασία εκπαίδευσης εξ αποστάσεως μέσω Telegram ή Discord και αφήστε τον agent να παρακολουθεί το log εκπαίδευσης και να αναφέρει περιοδικές τιμές απώλειας, χρήση GPU και χρήση δίσκου πίσω στο κινητό σας. Εάν η εκτέλεση σταματήσει ή η VRAM εκτοξευτεί, το μαθαίνετε αμέσως χωρίς να χρειάζεται να βρίσκεστε στο μηχάνημα.

3. **IOT με τοπικό VLM**: Στρέψτε μια κάμερα στην μπροστινή σας πόρτα, εκτελέστε ένα μοντέλο όρασης στο Lemonade και αφήστε το OpenClaw να αναλύει καρέ κατά παραγγελία ή με ενεργοποιητή. Ρωτήστε "έφτασαν σήμερα δέματα;" από το κινητό σας και λάβετε μια ξεκάθαρη απάντηση από το δικό σας υλικό.

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