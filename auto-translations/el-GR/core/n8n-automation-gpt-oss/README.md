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
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Αυτό το playbook απαιτεί τουλάχιστον **32GB** μνήμης συστήματος.
<!-- @device:end -->
Το n8n είναι μια πλατφόρμα αυτοματοποίησης ροών εργασίας που σας επιτρέπει να συνδέετε εφαρμογές και υπηρεσίες χρησιμοποιώντας έναν οπτικό επεξεργαστή βασισμένο σε κόμβους.

Αυτός ο οδηγός σάς διδάσκει πώς να δημιουργήσετε έναν εργαλείο σύνοψης οικονομικών ειδήσεων με τεχνητή νοημοσύνη, το οποίο αντλεί τους πιο πρόσφατους επιχειρηματικούς τίτλους από ένα RSS feed ειδήσεων και χρησιμοποιεί ένα τοπικό LLM που εκτελείται στο σύστημά σας για να δημιουργήσει μια σύνοψη προσανατολισμένη σε επενδυτές.

## Τι Θα Μάθετε

- Πώς να εγκαταστήσετε και να εκκινήσετε το n8n
- Εισαγωγή και διαμόρφωση μιας προκατασκευασμένης ροής εργασίας
- Σύνδεση με το Lemonade χρησιμοποιώντας την εγγενή ενσωμάτωση του n8n
- Κατανόηση των κόμβων ροής εργασίας και της ροής δεδομένων

## Τι Είναι το Lemonade;

Το [Lemonade](https://lemonade-server.ai) είναι μια πλατφόρμα τοπικής εξυπηρέτησης LLM σχεδιασμένη για υλικό AMD. Παρέχει ένα API συμβατό με OpenAI που εκτελείται εξ ολοκλήρου στο μηχάνημά σας—τα δεδομένα σας δεν εγκαταλείπουν ποτέ τη συσκευή σας.

Σε αυτόν τον οδηγό, χρησιμοποιούμε το Lemonade για να εξυπηρετήσουμε ένα τοπικό LLM με το οποίο συνδέεται το n8n για εργασίες με τεχνητή νοημοσύνη.

Το n8n περιλαμβάνει έναν **εγγενή κόμβο Lemonade** (`Lemonade Chat Model`) που παρέχει μια ενσωμάτωση πρώτης κατηγορίας - χωρίς ανάγκη χειροκίνητης διαμόρφωσης. Αυτό καθιστά τη σύνδεση του τοπικού σας LLM με ροές εργασίας αυτοματοποίησης απλή υπόθεση.
<!-- @device:halo_box,halo,stx,krk -->
# Ρύθμιση της Διαμόρφωσης Μνήμης
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού
<!-- @require:software-update -->
<!-- @device:end -->
## Εγκατάσταση Προαπαιτούμενου Λογισμικού
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:n8n,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- Linux runs n8n as a Podman container (see compose.yml below), so Node.js and a host n8n install are not required; podman is the only extra prerequisite. -->
<!-- @require:lemonade,podman -->
<!-- @prereq:podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @prereq:lemonade-models-gpt-oss-120b -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:lemonade-models-gpt-oss-20b -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
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
  "max_tokens": 32
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
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->
## Εγκατάσταση του n8n
<!-- @os:windows -->
Εγκαταστήστε το n8n καθολικά χρησιμοποιώντας το npm.

> **Σημείωση**: Ενδέχεται να δείτε κάποιες προειδοποιήσεις npm. Αυτό είναι αναμενόμενο.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Συμβουλή**: Οι χρήστες Windows ενδέχεται να χρειαστεί να τροποποιήσουν την Πολιτική Εκτέλεσης PowerShell (Execution Policy) (π.χ.
> ρυθμίζοντάς την σε RemoteSigned ή Unrestricted) πριν εκτελέσουν ορισμένες εντολές Powershell.
<!-- @os:end -->


<!-- @os:windows -->
> **Πρόβλημα PATH**: Αν η εντολή `n8n --version` εμφανίζει μήνυμα ότι η εντολή δεν βρέθηκε, βεβαιωθείτε ότι ο καθολικός φάκελος bin του npm βρίσκεται στο `PATH` του χρήστη. Η συνήθης διαδρομή εγκατάστασης είναι η `C:\Users\<username>\AppData\Roaming\npm`.
> Προσθέστε αυτή τη διαδρομή στο path του χρήστη (Edit the system environment variables > Environment Variables > Edit User Path) και επαναφορτώστε το τερματικό.
<!-- @os:end -->

<!-- @os:linux -->
Θα χρησιμοποιήσουμε τώρα την υπηρεσία Podman για να γίνει containerization της εγκατάστασης n8n.

Παρακαλούμε κατεβάστε τα παρακάτω σε έναν κατάλογο της επιλογής σας: [compose.yml](assets/compose.yml)

Σε αυτόν τον κατάλογο, εκτελέστε την εξής εντολή:
```bash
podman compose up -d
```

Αυτό θα πρέπει να εγκαταστήσει το n8n και να γράψει σε μόνιμο αποθηκευτικό χώρο.

Εκκινήστε το n8n πληκτρολογώντας `localhost:5678` στη γραμμή διεύθυνσης του προγράμματος περιήγησής σας.
<!-- @os:end -->

<!-- @os:windows -->
## Εκκίνηση του n8n

Ξεκινήστε το n8n από το τερματικό:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

podman rm -f n8n >/dev/null 2>&1 || true
podman compose -f compose.yml up -d

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  podman ps -a || true
  podman logs n8n 2>&1 | tail -30 || true
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Το n8n ξεκινά έναν τοπικό web server. Πατήστε `'o'` ή ανοίξτε το πρόγραμμα περιήγησής σας στο `http://localhost:5678` για να αποκτήσετε πρόσβαση στον επεξεργαστή.
<!-- @os:end -->
> **Συμβουλή**: Διατηρήστε το παράθυρο τερματικού ανοιχτό κατά τη χρήση του n8n. Αν το κλείσετε, ενδέχεται να διακοπεί ο server.

## Εκκίνηση του Lemonade

Το Lemonade είναι ο τοπικός server που θα εκτελέσει ένα μοντέλο και θα συνδεθεί με το n8n.
<!-- @os:linux -->
Ανοίξτε το GUI του Lemonade κάνοντας κλικ στο εικονίδιο Lemonade στη γραμμή εργασιών. Από εδώ μπορείτε να περιηγηθείτε σε μοντέλα, backends, και να φορτώσετε τα προεγκατεστημένα μοντέλα.
<!-- @os:end -->

<!-- @os:windows -->
Ανοίξτε το Lemonade GUI κάνοντας κλικ στο εικονίδιο Lemonade. Κάντε δεξί κλικ στο εικονίδιο της γραμμής εργασιών για να ανοίξετε την εφαρμογή. Στη συνέχεια, μπορείτε να προσθέσετε μοντέλα, backends και να φορτώσετε τα προεγκατεστημένα μοντέλα.
<!-- @os:end -->
**Συμβουλή**: Μόλις εκτελεστεί, το Lemonade GUI είναι επίσης προσβάσιμο στο http://localhost:13305

Εναλλακτικά, μπορείτε να ανοίξετε ένα τερματικό και να εκτελέσετε `lemonade list` για να δείτε ποια μοντέλα είναι εγκατεστημένα. Στη συνέχεια, εκτελέστε:
<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->
## Ρύθμιση της Ροής Εργασίας

### Βήμα 1: Εγγραφή ή Σύνδεση στο n8n

Όταν ανοίξετε το n8n για πρώτη φορά, θα σας ζητηθεί να δημιουργήσετε έναν λογαριασμό ή να συνδεθείτε:

1. Ανοίξτε το `http://localhost:5678` στο πρόγραμμα περιήγησής σας
2. Δημιουργήστε έναν νέο τοπικό λογαριασμό με το email σας, ή συνδεθείτε αν έχετε ήδη έναν
3. Μόλις συνδεθείτε, θα δείτε τον πίνακα ελέγχου (dashboard) του n8n

> **Συμβουλή**: Αν κλειδωθείτε έξω από τον λογαριασμό σας, δοκιμάστε `n8n user-management:reset`

### Βήμα 2: Εισαγωγή της Ροής Εργασίας

Σας έχουμε παρέχει μια προκατασκευασμένη ροή εργασίας που μπορείτε να εισάγετε απευθείας:

1. Κατεβάστε το ακόλουθο αρχείο ροής εργασίας: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Κάντε κλικ στο **Start from Scratch** για να ανοίξετε τον επεξεργαστή ροών εργασίας. Εναλλακτικά, κάντε κλικ στο κουμπί + πάνω αριστερά, και στη συνέχεια στο **Add workflow**.
3. Κάντε κλικ στο μενού **...** (τρεις τελείες) στην πάνω δεξιά μπάρα και επιλέξτε **Import from file**
4. Επιλέξτε το κατεβασμένο αρχείο `financial-news-workflow.json`
5. Η ροή εργασίας θα εμφανιστεί στον καμβά
### Βήμα 3: Κατανόηση της Ροής Εργασίας

Η εισαγόμενη ροή εργασίας περιέχει 8 συνδεδεμένους κόμβους:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Κόμβος | Σκοπός |
|------|---------|
| **When clicking 'Execute workflow'** | Χειροκίνητη ενεργοποίηση για την έναρξη της ροής εργασίας |
| **Fetch Financial News Feed** | Κόμβος RSS Read που αντλεί τους πιο πρόσφατους επιχειρηματικούς τίτλους από μια ροή RSS (προεπιλογή είναι η ροή NYT Business, χωρίς απαίτηση κλειδιού API) |
| **Aggregate Headlines** | Κόμβος Aggregate που συγκεντρώνει τους τίτλους και τις περιλήψεις από κάθε στοιχείο της ροής σε μία ενιαία λίστα |
| **Clean Extracted News Data** | Κόμβος Set που συνδυάζει όλους τους τίτλους σε ένα ενιαίο πεδίο κειμένου |
| **AI Financial News Summarizer** | AI Agent που επεξεργάζεται τις ειδήσεις με ένα system prompt οικονομικού αναλυτή |
| **Lemonade Chat Model** | Συνδέεται με τον τοπικό σας Lemonade server που εκτελεί το LLM |
| **Structured Output Parser** | Μορφοποιεί την έξοδο του AI ως δομημένο JSON |
| **Convert to File** | Μετατρέπει την περίληψη σε αρχείο που μπορεί να ληφθεί |

> **Συμβουλή**: Για να χρησιμοποιήσετε διαφορετική πηγή ειδήσεων, κάντε διπλό κλικ στον κόμβο **Fetch Financial News Feed** και αντικαταστήστε τη διεύθυνση URL με οποιαδήποτε ροή RSS επιχειρηματικών ή χρηματιστηριακών ειδήσεων προτιμάτε.

### Βήμα 4: Διαμόρφωση Διαπιστευτηρίων Lemonade

Πριν εκτελέσετε τη ροή εργασίας, πρέπει να τη συνδέσετε με τον τοπικό σας Lemonade server:

1. Κάντε διπλό κλικ στον κόμβο **Lemonade Chat Model** στο n8n
2. Στο αναπτυσσόμενο μενού **Credential to connect with** επιλέξτε **Create New Credential**
3. Εισαγάγετε τις τιμές στον παρακάτω πίνακα και κάντε κλικ στο save.
4. Επιλέξτε το σχετικό μοντέλο που έχετε φορτώσει στο Lemonade Server.

  | Πεδίο | Τιμή |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Σημείωση**: Πριν από τη δοκιμή, εκτελέστε `lemonade status` σε ένα τερματικό για να επιβεβαιώσετε ότι ο Lemonade server εκτελείται.
<!-- @device:halo_box -->
> Αυτή η ροή εργασίας χρησιμοποιεί το GPT-OSS-120B και είναι προεγκατεστημένο στο Lemonade. Μπορείτε να το αλλάξετε σε άλλα φορτωμένα μοντέλα στις ρυθμίσεις του κόμβου Lemonade Chat Model.
<!-- @device:end -->

### Βήμα 5: Δοκιμή της Ροής Εργασίας

1. Βεβαιωθείτε ότι το Lemonade εκτελείται με φορτωμένο μοντέλο
2. Κάντε κλικ στο **Execute workflow** στο κάτω κεντρικό τμήμα του καμβά
3. Παρακολουθήστε κάθε κόμβο να εκτελείται από αριστερά προς τα δεξιά—γίνονται πράσινοι όταν ολοκληρωθούν
4. Κάντε διπλό κλικ στον κόμβο **AI Financial News Summarizer** για να δείτε την παραγόμενη περίληψη στο κάτω παράθυρο.
5. Κάντε διπλό κλικ στον κόμβο **Convert to File** για να κατεβάσετε το αντίστοιχο αρχείο κειμένου στο κάτω παράθυρο.

## Κατανόηση του AI Agent

Ο AI Financial News Summarizer χρησιμοποιεί ένα system prompt σχεδιασμένο για οικονομική ανάλυση:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Ο agent λαμβάνει τα καθαρισμένα δεδομένα ειδήσεων και παράγει μια δομημένη περίληψη με το κλίμα της αγοράς.

### Αποθήκευση της Ροής Εργασίας σας

Κάντε κλικ στο όνομα της ροής εργασίας στο επάνω μέρος και μετονομάστε την αν το επιθυμείτε. Οι ροές εργασίας αποθηκεύονται αυτόματα καθώς εργάζεστε.

## Επόμενα Βήματα

- **Προγραμματισμός αυτοματισμού**: Αντικαταστήστε το Manual Trigger με ένα **Schedule Trigger** για καθημερινή εκτέλεση
- **Αποστολή ειδοποιήσεων**: Προσθέστε έναν κόμβο **Discord**, **Slack**, ή **Email** για να λαμβάνετε περιλήψεις
- **Δοκιμάστε διαφορετικά μοντέλα**: Αλλάξτε το μοντέλο στον κόμβο Lemonade Chat Model για να πειραματιστείτε με διαφορετικά LLM
- **Αλλαγή πηγής ειδήσεων**: Κατευθύνετε τον κόμβο **Fetch Financial News Feed** σε μια διαφορετική ροή RSS για να παρακολουθείτε άλλες ενότητες ή εκδόσεις
- **Δοκιμάστε διαφορετικά backend**: Το n8n υποστηρίζει επίσης [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio, και άλλα τοπικά LLM backends

### Εξερευνήστε τα Πρότυπα του n8n

Το n8n διαθέτει εκατοντάδες προκατασκευασμένα πρότυπα ροών εργασίας. Περιηγηθείτε στην επίσημη βιβλιοθήκη προτύπων στο:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Αναζητήστε "AI", "LLM", ή "automation" για να βρείτε ροές εργασίας που μπορείτε να εισαγάγετε και να προσαρμόσετε.

Για περισσότερες πληροφορίες, δείτε την [Τεκμηρίωση του n8n](https://docs.n8n.io/).

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