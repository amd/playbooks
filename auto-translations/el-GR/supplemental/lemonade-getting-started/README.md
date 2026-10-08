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

🍋 Το **Lemonade** είναι ένας ανοιχτού κώδικα τοπικός διακομιστής τεχνητής νοημοσύνης που σας επιτρέπει να εκτελείτε μεγάλα γλωσσικά μοντέλα (LLM), γεννήτριες εικόνων και μοντέλα ήχου απευθείας στο δικό σας υλικό. Εκθέτει τα μοντέλα μέσω του βιομηχανικού προτύπου **OpenAI API**, οπότε οποιαδήποτε εφαρμογή λειτουργεί με το OpenAI μπορεί αμέσως να λειτουργήσει με το Lemonade. Μέχρι το τέλος αυτού του οδηγού, θα χρησιμοποιείτε το Lemonade για να εκτελείτε μοντέλα τοπικά στον υπολογιστή σας.

## Τι Θα Μάθετε

Μέχρι το τέλος αυτού του οδηγού θα μπορείτε να:

* **Εγκαταστήσετε το Lemonade Server** και να επαληθεύσετε ότι εκτελείται.
* **Κατεβάσετε και να συνομιλήσετε με ένα LLM** χρησιμοποιώντας μία μόνο εντολή.
* **Εξερευνήσετε το web UI** και να δοκιμάσετε διαφορετικές λειτουργίες όπως όραση, μετατροπή ομιλίας σε κείμενο και δημιουργία εικόνων.
* **Εναλλάξετε backend GPU** μεταξύ Vulkan και λογισμικού AMD ROCm™.
* **Δημιουργήσετε μια εφαρμογή Python** που τροφοδοτείται από ένα τοπικό LLM χρησιμοποιώντας το συμβατό με OpenAI API.
<!-- @device:halo_box,halo,stx,krk -->
* **Εκτέλεση μοντέλων στη Neural Processing Unit (NPU) της AMD** χρησιμοποιώντας τις λειτουργίες εκτέλεσης Hybrid και FLM σε υλικό AMD Ryzen™ AI.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Ρύθμιση της Διαμόρφωσης Μνήμης
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού
<!-- @require:software-update -->
<!-- @device:end -->
## Εγκατάσταση Απαιτούμενου Λογισμικού

Πριν ξεκινήσετε, βεβαιωθείτε ότι διαθέτετε:

- Έναν υπολογιστή με **Windows 11** ή μια υποστηριζόμενη διανομή **Linux** (Ubuntu 24.04+, Fedora, Debian)
- Συνιστώνται **16 GB RAM** για το μοντέλο εκτέλεσης που χρησιμοποιείται στα Βήματα 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). Συνιστώνται **32 GB+** εάν θέλετε να χρησιμοποιήσετε το μεγαλύτερο μοντέλο δημιουργίας κώδικα στο Βήμα 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB ελεύθερου χώρου στον δίσκο**, ανάλογα με τα μοντέλα που κατεβάζετε. Το μεγαλύτερο μοντέλο σε αυτόν τον οδηγό είναι περίπου 20 GB.
- **Python 3.10–3.13** (χρησιμοποιείται στην ενότητα εφαρμογής Python)
- Σύνδεση στο διαδίκτυο (ενσύρματη ή ασύρματη)
<!-- @device:halo_box,halo,stx,krk -->
- [Προαιρετικό] Ένας επεξεργαστής AMD XDNA 2 NPU (σειρά Ryzen AI 300/400/Max 300 ή Z2 Extreme) με τον πιο πρόσφατο οδηγό εγκατεστημένο από τις [Οδηγίες Εγκατάστασης Λογισμικού Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) εάν θέλετε να εκτελέσετε ένα μοντέλο στο NPU.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade-models-gemma-4-e2b,lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
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
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->
---

## Βασικές Έννοιες — Πώς Λειτουργούν οι Τοπικοί Διακομιστές AI

Πριν εκτελέσουμε ένα μοντέλο, αξίζει να κατανοήσουμε *γιατί* τα πράγματα είναι ρυθμισμένα με αυτόν τον τρόπο. Το Lemonade είναι ένας **τοπικός διακομιστής μοντέλων (local model server)**, μια διεργασία που φορτώνει μοντέλα AI στη μνήμη και τα εκθέτει σε εφαρμογές μέσω HTTP, ακριβώς όπως θα έκανε μια υπηρεσία AI στο cloud.

### Γιατί Διακομιστής;

| Όφελος | Τι Σημαίνει για Εσάς |
|---------|----------------------|
| **Απλοποιημένη ενσωμάτωση** | Οι εφαρμογές επικοινωνούν με ένα API HTTP αντί να ασχολούνται με βιβλιοθήκες C++ ή Python ειδικές για το υλικό. |
| **Κοινόχρηστα μοντέλα** | Ένα μόνο φορτωμένο μοντέλο μπορεί να εξυπηρετεί πολλές εφαρμογές ταυτόχρονα, χωρίς διπλά αντίγραφα που καταναλώνουν τη μνήμη RAM σας. |
| **Φορητότητα από το cloud στο τοπικό περιβάλλον** | Κώδικας γραμμένος για το cloud API του OpenAI λειτουργεί με το Lemonade αλλάζοντας μία μόνο διεύθυνση URL. |
| **Διαχωρισμός αρμοδιοτήτων** | Η διαχείριση μοντέλων, η ροή δεδομένων (streaming) και η ανοχή σφαλμάτων διαχειρίζονται από τον διακομιστή, ώστε οι προγραμματιστές να μπορούν να επικεντρωθούν στην εφαρμογή τους. |

### Το Πρότυπο OpenAI API

Το Lemonade υλοποιεί το **OpenAI API**, την ίδια διεπαφή που χρησιμοποιείται από το ChatGPT, το Azure OpenAI και δεκάδες άλλες υπηρεσίες. Το μοντέλο συνομιλίας είναι απλό:

| Ρόλος | Ποιος Μιλάει |
|------|---------------|
| **system** | Οδηγίες προς το μοντέλο (προσωπικότητα, περιορισμοί, διαθέσιμα εργαλεία) |
| **user** | Μηνύματα από τον άνθρωπο (ή την εφαρμογή) προς το μοντέλο |
| **assistant** | Απαντήσεις που δημιουργούνται από το μοντέλο |

Αυτό σημαίνει ότι οποιαδήποτε βιβλιοθήκη ή εφαρμογή υποστηρίζει το OpenAI μπορεί να επικοινωνήσει με το Lemonade, κατευθύνοντάς την προς το `http://localhost:13305/api/v1` ενώ ο Lemonade Server εκτελείται.

## Κύρια Δραστηριότητα — Η Πρώτη σας Τοπική Συνομιλία AI

Ας κατεβάσουμε ένα LLM και ας κάνουμε μια συνομιλία μαζί του, εκτελώντας το AI εξ ολοκλήρου στο δικό σας μηχάνημα.

### Βήμα 1: Λήψη και Εκτέλεση ενός Μοντέλου

Το Lemonade διατίθεται με μια επιμελημένη βιβλιοθήκη μοντέλων. Ας ξεκινήσουμε με το **Gemma-4-E2B-it**, ένα ικανό και συμπαγές μοντέλο που περιλαμβάνει υποστήριξη όρασης. Ανοίξτε ένα τερματικό και εκτελέστε:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Αυτή η μεμονωμένη εντολή κάνει τρία πράγματα:

1. **Κατεβάζει** το μοντέλο (~3 GB) από το Hugging Face, εάν δεν έχει ήδη κατέβει. (Μπορεί να χρειαστεί κάποιος χρόνος)
2. **Εκκινεί** τη διεργασία Lemonade Server στη θύρα 13305.
3. **Ανοίγει** το Lemonade App ώστε να μπορείτε να ξεκινήσετε να συνομιλείτε με το μοντέλο.
<!-- @os:windows -->
Στα Windows, η εφαρμογή Lemonade App εκκινείται αυτόματα και μπορείτε να ξεκινήσετε τη συνομιλία αμέσως. Αν εγκαταστήσατε το πακέτο `minimal.msi`, η εφαρμογή δεν περιλαμβάνεται. Για να ξεκινήσετε τη συνομιλία, ανοίξτε το πρόγραμμα περιήγησής σας και μεταβείτε στη διεύθυνση `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
Στα Linux, ανοίξτε τον περιηγητή σας και μεταβείτε στη διεύθυνση `http://localhost:13305` για να αποκτήσετε πρόσβαση στην εφαρμογή ιστού.
<!-- @os:end -->
Δοκιμάστε να πληκτρολογήσετε μια ερώτηση:

```
What are three fun facts about lemons?
```

Το μοντέλο θα απαντήσει απευθείας στο παράθυρο συνομιλίας. **Συγχαρητήρια! Εκτελείτε ένα μεγάλο γλωσσικό μοντέλο τοπικά.**

![Lemonade App with Logs displayed](../../dependencies/assets/ChatwithLogs.png)

Στο παράθυρο Server Logs της Lemonade App, μπορείτε να βρείτε δεδομένα τηλεμετρίας σχετικά με την απόδοση του μοντέλου μετά από κάθε απάντηση. Για παράδειγμα:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Βήμα 2: Εξερευνήστε τη Διεπαφή Ιστού και τις Διαφορετικές Λειτουργίες

Το Lemonade περιλαμβάνει μια ενσωματωμένη διεπαφή ιστού όπου μπορείτε να:

- **Αλληλεπιδράσετε** με το φορτωμένο μοντέλο σε ένα οικείο παράθυρο συνομιλίας
- **Περιηγηθείτε σε μοντέλα** στην καρτέλα Model Manager
- **Κατεβάσετε νέα μοντέλα** με ένα κλικ

Δοκιμάστε να εναλλάσσετε διαφορετικές λειτουργίες χρησιμοποιώντας την καρτέλα **Model Manager** στη διεπαφή ιστού, όπου μπορείτε να περιηγηθείτε σε μοντέλα ανά Recipe ή ανά Category:

1. **Vision:** Το μοντέλο `Gemma-4-E2B-it-GGUF` που έχετε ήδη φορτωμένο υποστηρίζει vision. Επικολλήστε μια εικόνα στο πλαίσιο συνομιλίας και ζητήστε από το μοντέλο να την περιγράψει.
2. **Δημιουργία εικόνας:** Στην κατηγορία Image, κατεβάστε ένα μοντέλο εικόνας όπως το `SDXL-Turbo` από το Model Manager, και στη συνέχεια χρησιμοποιήστε το Lemonade Image Generator για να πληκτρολογήσετε μια προτροπή και να δημιουργήσετε μια εικόνα τοπικά.
3. **Audio:** Στην κατηγορία Audio, κατεβάστε ένα μοντέλο ήχου όπως το `Whisper-Tiny`, το οποίο μπορεί να κάνει speech-to-text. Παρέχετε μια ηχογράφηση ήχου για να τη μεταγράψετε τοπικά. Για text-to-speech, δοκιμάστε ένα από τα μοντέλα στην κατηγορία Speech, όπως το `kokoro-v1`.

![Πολλαπλή λειτουργικότητα με το Lemonade](../../dependencies/assets/multi_modality.png)

### Βήμα 3: Δοκιμάστε ένα Μοντέλο με Διαφορετικό Backend

Αν μετακινήσετε τον δείκτη του ποντικιού πάνω από ένα μοντέλο στο Lemonade App, θα δείτε ένα εικονίδιο γραναζιού. Κάνοντας κλικ σε αυτό σας επιτρέπει να επιλέξετε επιλογές για το μοντέλο, συμπεριλαμβανομένης της επιλογής του επιθυμητού backend.

Από προεπιλογή, το Lemonade χρησιμοποιεί Vulkan για επιτάχυνση GPU. Αν διαθέτετε μια υποστηριζόμενη διακριτή GPU AMD, μπορείτε να μεταβείτε σε ROCm.

![Επιλογή Backend στο Lemonade](../../dependencies/assets/lemonademodeloptions.png)

Για να διαχειριστείτε τα εγκατεστημένα backend σας, κάντε κλικ στο κουμπί backend στην αριστερότερη στήλη.

Εναλλακτικά, μπορείτε να καθορίσετε το backend χρησιμοποιώντας την παρακάτω εντολή:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Μπορείτε επίσης να ορίσετε το προεπιλεγμένο backend σας χρησιμοποιώντας τη μεταβλητή περιβάλλοντος `LEMONADE_LLAMACPP` με τις τιμές: `vulkan`, `rocm`, ή `cpu`.

---

## Πηγαίνοντας Πιο Βαθιά — Δημιουργήστε μια Εφαρμογή με Τεχνητή Νοημοσύνη σε Python

Η πραγματική δύναμη ενός τοπικού διακομιστή AI είναι ότι οποιαδήποτε εφαρμογή μπορεί να συνδεθεί σε αυτόν χρησιμοποιώντας μόλις λίγες γραμμές κώδικα. Για να το αποδείξουμε, ας δημιουργήσουμε μια μικρή αλλά λειτουργική **γεννήτρια flashcard μελέτης** όπου της δίνετε ένα θέμα, δημιουργεί flashcards, και μπορείτε να κάνετε κουίζ στον εαυτό σας διαδραστικά.

### Βήμα 4: Εκκινήστε τον Διακομιστή

Επαληθεύστε ότι ο διακομιστής Lemonade εκτελείται. Συνήθως ξεκινά αυτόματα στο παρασκήνιο μετά την εγκατάσταση. Για να το επιβεβαιώσετε, εκτελέστε:

```
lemonade status
```

Θα πρέπει να δείτε ένα μήνυμα όπως: `Server is running on port 13305`.

Αν ο διακομιστής δεν εκτελείται, ξεκινήστε τον ανοίγοντας την εφαρμογή Lemonade. Χρησιμοποιήστε την προεπιλεγμένη θύρα **13305** (μπορείτε να την επιβεβαιώσετε ή να την επιλέξετε από το εικονίδιο στο tray).

### Βήμα 5: Εγκαταστήστε τον OpenAI Python Client

Σε ένα τερματικό, δημιουργήστε ένα venv και εγκαταστήστε τον OpenAI Python Client χρησιμοποιώντας τις παρακάτω εντολές:
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### Βήμα 6: Δημιουργήστε την Εφαρμογή Flashcard

Ας κατεβάσουμε ένα διαφορετικό μοντέλο για τη δημιουργία κώδικα: `Qwen3.5-35B-A3B-GGUF`. Αυτό είναι ένα μεγάλο (~20 GB) και αποδοτικό μοντέλο κατάλληλο για συστήματα με 32 GB+ RAM. Αν έχετε λιγότερη διαθέσιμη RAM, δοκιμάστε αντ' αυτού το `Qwen3.5-9B-GGUF` (~6 GB).

Μπορείτε να το κατεβάσετε από το UI ή να εκτελέσετε το παρακάτω:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Εισαγάγετε την παρακάτω προτροπή στο Lemonade Chat UI για να δημιουργήσετε κώδικα για μια απλή εφαρμογή Flashcard.

Θα χρησιμοποιήσουμε το Qwen3.5-35B-A3B-GGUF (ένα μεγαλύτερο μοντέλο καλύτερο στη συγγραφή κώδικα) για να δημιουργήσουμε την εφαρμογή μας Python, και η ίδια η εφαρμογή θα καλεί το Gemma-4-E2B-it-GGUF (το μικρότερο μοντέλο που έχετε ήδη κατεβάσει) κατά τον χρόνο εκτέλεσης. Ο κώδικας μπορεί στη συνέχεια να αντιγραφεί σε ένα αρχείο της επιλογής σας για να εκτελεστεί σε Python.

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **Συμβουλή**: Ακολουθήσαμε τυπικές πρακτικές μηχανικής μέσω διεξοδικής δημιουργίας προτροπών και χρησιμοποιώντας ένα σύστημα δύο μοντέλων για τη βελτιστοποίηση πόρων και ταχύτητας.

Για τη διευκόλυνσή σας, έχουμε παράσχει ένα δείγμα εξόδου στο [`flashcards.py`](assets/flashcards.py). Μη διστάσετε να το κατεβάσετε στον κατάλογό σας. Σε κάθε περίπτωση, θα πρέπει τώρα να έχετε ένα αρχείο Python που μπορεί να εκτελεστεί.

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
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

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### Βήμα 7: Εκτελέστε τον Δημιουργημένο Κώδικα

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Να τι θα πρέπει να δείτε:**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

Σε περίπου 150 γραμμές κώδικα έχετε δημιουργήσει ένα πλήρως λειτουργικό εργαλείο μελέτης που τροφοδοτείται από ένα τοπικό LLM. Δεν υπάρχει κλειδί API προς διαχείριση, κανένα κόστος χρήσης, και κανένα δεδομένο δεν εγκαταλείπει ποτέ τον υπολογιστή σας.

> **Βασική διαπίστωση:** Παρατηρήστε ότι η γραμμή `client = OpenAI(base_url=...) ` είναι το *μόνο* πράγμα που συνδέει αυτή την εφαρμογή με το Lemonade αντί για το cloud του OpenAI. Ο υπόλοιπος κώδικας είναι πανομοιότυπος με αυτόν που θα γράφατε για οποιαδήποτε υπηρεσία συμβατή με OpenAI. Αν έχετε χρησιμοποιήσει ποτέ τη βιβλιοθήκη OpenAI Python, ήδη γνωρίζετε πώς να δημιουργείτε εφαρμογές με το Lemonade.

### Τι Αποδεικνύει Αυτό

Αυτή η μικρή εφαρμογή ασκεί αρκετά πραγματικά μοτίβα ενσωμάτωσης:

| Μοτίβο | Πού Εμφανίζεται |
|---------|-----------------|
| **System prompts** | Το μήνυμα `"system"` λέει στο LLM να παράγει δομημένο JSON |
| **Δομημένη έξοδος** | Η εφαρμογή αναλύει την απάντηση του LLM ως JSON για να δημιουργήσει flashcards |
| **Αιτήματα χωρίς κατάσταση** | Κάθε κλήση `generate_flashcards()` είναι ανεξάρτητη |
| **Διαχείριση σφαλμάτων** | Το `try/except` χειρίζεται με χάρη περιπτώσεις όπου η έξοδος του LLM δεν είναι έγκυρο JSON |

Αυτά τα ίδια μοτίβα κλιμακώνονται σε οποιαδήποτε εφαρμογή όπως chatbots, βοηθούς κώδικα, γεννήτριες περιεχομένου, εργαλεία αυτοματισμού.

#### Πρόκληση Μπόνους

* Για μια επιπλέον πρόκληση, δοκιμάστε να ενημερώσετε την εφαρμογή ώστε τα flashcards να διαβάζονται στον χρήστη, αναφερόμενοι στο παράδειγμα που παρέχεται [εδώ](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Εκτέλεση Μοντέλων στη NPU (Προαιρετικό)

Αν διαθέτετε Ryzen AI 300/400/Max 300 series ή Z2 Extreme, η συσκευή σας διαθέτει ενσωματωμένη **Neural Processing Unit (NPU)**, ένα ειδικό τσιπ σχεδιασμένο αποκλειστικά για φόρτους εργασίας AI. Η εκτέλεση μοντέλων στη NPU είναι πιο αποδοτική ενεργειακά σε σύγκριση με τη χρήση της GPU, γεγονός που την καθιστά ιδανική για εργασίες AI στο παρασκήνιο, μεγαλύτερες συνεδρίες και χρήση με μπαταρία.

Το Lemonade υποστηρίζει τρεις λειτουργίες εκτέλεσης στη NPU, όλες διαφανείς πίσω από το ίδιο OpenAI API:

| Λειτουργία | Πώς Λειτουργεί | Recipe | Παραδείγματα Μοντέλων |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | Η NPU επεξεργάζεται το prompt, η iGPU παράγει tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Μόνο NPU** | Ολόκληρο το inference εκτελείται στη NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Χρησιμοποιεί τη μηχανή FastFlowLM στη NPU, βελτιστοποιημένη για AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Απαιτήσεις

- Επεξεργαστής **AMD Ryzen AI 300/400 series ή Z2 series**
- Για μοντέλα **FLM**: Το runtime FLM μπορεί να εγκατασταθεί μέσα από την εφαρμογή Lemonade ή το Lemonade θα εγκαταστήσει αυτόματα το runtime FLM κατά την εκτέλεση ενός μοντέλου FLM. Για να μάθετε περισσότερα σχετικά με το FastFlowLM, δείτε [εδώ](https://fastflowlm.com/docs/).


### Βήμα 8: Εκτέλεση ενός Hybrid Μοντέλου

Τα hybrid μοντέλα κατανέμουν τον φόρτο εργασίας μεταξύ της NPU και της iGPU για μια καλή ισορροπία μεταξύ ταχύτητας και αποδοτικότητας. Στην εφαρμογή Lemonade, επιλέξτε ένα μοντέλο από τη λίστα `Ryzen AI LLM`, για παράδειγμα, `Qwen3-4B-Hybrid`, ή εκτελέστε το χρησιμοποιώντας την παρακάτω εντολή:

```
lemonade run Qwen3-4B-Hybrid
```

Το Lemonade εντοπίζει αυτόματα τη NPU σας και εγκαθιστά το backend **Ryzen AI LLM**.

> **Τι συμβαίνει στο παρασκήνιο;** Όταν στέλνετε ένα μήνυμα, η NPU επεξεργάζεται ολόκληρο το prompt σας παράλληλα (αυτό ονομάζεται "prefill"). Στη συνέχεια, η iGPU αναλαμβάνει να παράγει την απάντηση ένα token τη φορά (αυτό ονομάζεται "decode"). Αυτή η υβριδική προσέγγιση αξιοποιεί τα δυνατά σημεία κάθε τσιπ.

### Βήμα 9: Εκτέλεση ενός Μοντέλου FLM

Τα μοντέλα FastFlowLM (FLM) είναι ειδικά βελτιστοποιημένα για την αρχιτεκτονική NPU XDNA2 της AMD και μπορούν να είναι πολύ γρήγορα για το μέγεθός τους. Για παράδειγμα, επιλέξτε `qwen3.5-4b-FLM` από τη λίστα `FastFlowLM NPU` ή χρησιμοποιήστε την παρακάτω εντολή:

<!-- @os:windows -->
Για να ενεργοποιήσετε το `FastFlowLM` στα Windows:

* Ανοίξτε το μενού `Backends Manager`.
* Εντοπίστε την κατηγορία backend `FastFlowLM NPU`.
* Κάντε κλικ στο Install NPU.
* Μόλις ολοκληρωθεί η εγκατάσταση, θα είναι διαθέσιμα περίπου 36 προεπιλεγμένα μοντέλα στο αναπτυσσόμενο μενού FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Όταν η εφαρμογή `Lemonade` εκτελείται για πρώτη φορά, το backend `FastFlowNPU` δεν είναι ενεργοποιημένο από προεπιλογή.
Η τοπική εφαρμογή θα ανοίξει τη σελίδα εγκατάστασης για να σας καθοδηγήσει στη ρύθμιση.

Για να ενεργοποιήσετε το `FastFlowLM` στο Linux:

* Ανοίξτε την εφαρμογή `Lemonade`.
* Επισκεφθείτε την [επίσημη τεκμηρίωση FLM](https://lemonade-server.ai/flm_npu_linux.html) και ακολουθήστε τα βήματα εγκατάστασης για το FLM επιλέγοντας τη διανομή Linux σας.
* Ενεργοποιήστε τα backports όπως υποδεικνύεται στη σελίδα εγκατάστασης.
* Κατεβάστε την πιο πρόσφατη έκδοση `v0.9.x` από τη [σελίδα tags](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Για την AMD Halo Developer Platform, φροντίστε να επιλέξετε Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Εγκαταστήστε το ληφθέν πακέτο `.deb`.
* Συνιστάται: Κλείστε την εφαρμογή `Lemonade App` και ανοίξτε την ξανά ώστε να εντοπιστούν οι αλλαγές.
* Συνιστάται: Ανοίξτε το `Backends Manager` και κάντε κλικ στο Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Μετά από μια επιτυχημένη εγκατάσταση, θα πρέπει να δείτε ότι το `flm:npu` ολοκληρώθηκε στον **Download Manager** μέσα στην **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Στη συνέχεια, μπορείτε να επιλέξετε οποιοδήποτε από τα διαθέσιμα μοντέλα FFLM και να ξεκινήσετε να χρησιμοποιείτε το backend NPU.

Για συγκεκριμένο μοντέλο, κατεβάστε το επιθυμητό μοντέλο από τη [σελίδα μοντέλων](https://fastflowlm.com/docs/models/qwen/) και επαληθεύστε το χρησιμοποιώντας την εντολή Shell που παρέχεται στην τεκμηρίωση.
```
flm run qwen3.5-4b-FLM
```
ή μέσω 
```
lemonade run qwen3.5-4b-FLM
```

Τα μοντέλα FLM περιλαμβάνουν ορισμένες από τις πιο δημοφιλείς αρχιτεκτονικές (Gemma 3, Qwen 3, Llama 3, και DeepSeek R1) και κυμαίνονται από κάτω από 1 GB έως πάνω από 13 GB.
Το Lemonade εντοπίζει αυτόματα τη NPU σας και εγκαθιστά το backend **FastFlowLM NPU**.

<!-- @os:windows -->
> **Συμβουλή:** Για καλύτερη απόδοση NPU, ενεργοποιήστε τη λειτουργία turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Εναλλαγή Μοντέλων

Η εφαρμογή flashcard από το Βήμα 6 λειτουργεί και με μοντέλα NPU, απλώς αλλάξτε το όνομα του μοντέλου:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Επόμενα Βήματα

Έχετε έναν τοπικό διακομιστή AI που εκτελείται στο δικό σας υλικό, εδώ είναι το επόμενο βήμα:

1. **Συνδέστε τις αγαπημένες σας εφαρμογές**: Το Lemonade λειτουργεί εξ ορισμού με το [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), το [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), το [Continue](https://lemonade-server.ai/docs/server/apps/continue/), το [n8n](https://n8n.io/integrations/lemonade-model/), και [πολλά ακόμα](https://lemonade-server.ai/marketplace).

2. **Εξερευνήστε περισσότερα μοντέλα**: Εξερευνήστε την πλήρη [βιβλιοθήκη μοντέλων](https://lemonade-server.ai/docs/server/server_models/) για να βρείτε μοντέλα βελτιστοποιημένα για κωδικοποίηση, συλλογιστική, όραση, και πολλά άλλα. Χρησιμοποιήστε την εφαρμογή Lemonade ή το `lemonade list` για να δείτε τι είναι διαθέσιμο.

3. **Ξεκλειδώστε επιτάχυνση ROCm GPU**: Αν διαθέτετε μια υποστηριζόμενη GPU AMD, μεταβείτε στο backend ROCm: `lemonade config set llamacpp.backend=rocm`. Δείτε τις [υποστηριζόμενες GPU AMD](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Διαβάστε την πλήρη προδιαγραφή API**: Το Lemonade υποστηρίζει ολοκληρώσεις συνομιλίας, embeddings, μεταγραφή ήχου, δημιουργία εικόνας, μετατροπή κειμένου σε ομιλία, και πολλά άλλα. Δείτε την [Προδιαγραφή Server](https://lemonade-server.ai/docs/server/server_spec/) για κάθε endpoint.

5. **Συνεισφέρετε**: Το Lemonade είναι ανοιχτού κώδικα. Ρίξτε μια ματιά στον [οδηγό συνεισφοράς](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) και αναζητήστε [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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