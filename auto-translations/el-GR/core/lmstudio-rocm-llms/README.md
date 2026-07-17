<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Επισκόπηση

Το LM Studio είναι ένα ισχυρό περιτύλιγμα με γραφικό περιβάλλον για το [llama.cpp](https://github.com/ggml-org/llama.cpp) και παρέχει επίσης ένα [συμβατό endpoint με OpenAI](https://lmstudio.ai/docs/developer/openai-compat) για τοπική εξυπηρέτηση μοντέλων. Το LM Studio προσφέρει ένα απλό αλλά ισχυρό περιβάλλον για εύκολη λήψη και ανάπτυξη μοντέλων. Το LM Studio προσφέρει backends (που ονομάζονται runtimes) τόσο Vulkan όσο και AMD ROCm™ για χρήστες AMD.


## Τι Θα Μάθετε
- Πώς να ρυθμίσετε και να χρησιμοποιήσετε το LM Studio για να αξιοποιήσετε το τοπικό σας υλικό
- Δοκιμή και διαχείριση LLM σε πλήρως εκτός σύνδεσης περιβάλλον
- Εξυπηρέτηση μοντέλων μέσω συμβατού API με OpenAI για την υποστήριξη προσαρμοσμένων ροών εργασίας και εφαρμογών


## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @os:linux -->
> **Σημείωση**: Μπορείτε να εγκαταστήσετε το VS Code μέσω του AMD Ryzen™ AI Developer Center. Για το LM Studio, ακολουθήστε τις παρακάτω οδηγίες εγκατάστασης.
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση**: Εάν το VS Code ή το LM Studio δεν είναι εγκατεστημένο, μπορείτε να τα εγκαταστήσετε από το AMD Ryzen™ AI Developer Center.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενου Λογισμικού

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Λήψη Μοντέλων

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## Συνομιλία με ένα LLM
Μάθετε πώς να ξεκινήσετε να συνομιλείτε με ένα LLM επιπέδου ChatGPT εντελώς τοπικά.

1. Ανοίξτε το LMStudio.
2. Πατήστε `Ctrl + L` για να ανοίξετε το Model Loader, επιλέξτε `Manually choose model load parameters` και κάντε κλικ στο `${model_name}`
3. Βεβαιωθείτε ότι το "show advanced settings" είναι επιλεγμένο.
4. Αλλάξτε το `Context Length` όπως επιθυμείτε. Μεγαλύτερο μήκος περιβάλλοντος σημαίνει περισσότερη μνήμη μοντέλου, αλλά και περισσότερη χρήση μνήμης συστήματος. Η συνιστώμενη τιμή για αυτό το playbook είναι 4096.
5. Βεβαιωθείτε ότι το `GPU Offload` είναι ρυθμισμένο στο μέγιστο και το `Flash Attention` είναι ενεργοποιημένο (οι Cache Quantizations μπορούν να παραμείνουν απενεργοποιημένες)
6. Επιλέξτε `Remember settings` και κάντε κλικ στο `Load Model`.
7. Εάν δεν βρίσκεστε στο παράθυρο συνομιλίας, πατήστε `Ctrl + 1` ή κάντε κλικ στο κουμπί 👾 στην επάνω αριστερή γωνία της οθόνης.
8. Στείλτε ένα μήνυμα και ξεκινήστε να αλληλεπιδράτε με το μοντέλο!

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Συμβουλή**: Το μήκος περιβάλλοντος αναφέρεται στη μνήμη του μοντέλου. Η flash attention βελτιώνει την ταχύτητα επεξεργασίας μειώνοντας παράλληλα τη χρήση μνήμης. Το GPU Offload μεταφέρει τους υπολογισμούς στην κάρτα γραφικών για ταχύτερες αποκρίσεις.

## Εξυπηρέτηση LLM μέσω συμβατού endpoint με OpenAI

Το LM Studio προσφέρει επίσης ένα συμβατό endpoint με OpenAI με τη μορφή του LM Studio Server. Αυτό έχει ήδη παρουσιαστεί σε μια agentic ροή εργασίας κωδικοποίησης με το Cline [εδώ](../playbooks/vscode-qwen3-coder). Μια άλλη συνηθισμένη περίπτωση χρήσης είναι η σύνδεση του LM Studio Server με οποιαδήποτε διαδικτυακή εφαρμογή (React, Node.js, Python) μέσω αποστολής τυπικών αιτημάτων HTTP στο endpoint συμπερασμού.

Για να ρυθμίσετε το LM Studio Server, ακολουθήστε τις παρακάτω οδηγίες:

1. Στην αριστερή πλευρά, κάντε κλικ στην καρτέλα `Developer` (εικονίδιο γραμμής εντολών) ή `Ctrl + 2` και στη συνέχεια κάντε κλικ στο `Server Settings`.
2. (Προαιρετικό): Εάν θέλετε να εξυπηρετείτε το μοντέλο μέσω του τοπικού σας δικτύου, επιλέξτε `Serve on Local Network`. Εάν θέλετε να το χρησιμοποιήσετε με ιστότοπο ή εκτεταμένες κλήσεις εντός του VS Code, επιλέξτε `Enable CORS`.
3. Στην επάνω αριστερή γωνία, βεβαιωθείτε ότι ο διακομιστής εκτελείται κάνοντας κλικ στο κουμπί εναλλαγής μπροστά από το `Status`.
4. Ένα συμβατό endpoint με OpenAI θα εκτελείται τώρα. Η διεύθυνση βρίσκεται συνήθως στο http://127.0.0.1:1234
5. Εάν ένα μοντέλο δεν είναι ήδη φορτωμένο, μπορείτε να το φορτώσετε κάνοντας κλικ στο `Load Model` και ακολουθώντας τα προαναφερθέντα βήματα.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->


Αυτό το μοντέλο θα είναι πλέον προσβάσιμο μέσω του endpoint του LM Studio Server και θα υποστηρίζει τα endpoints OpenAI, συμπεριλαμβανομένων:

| Endpoint | Μέθοδος | Τεκμηρίωση |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### Παράδειγμα: Δοκιμή του Endpoint σας
Έχοντας μόλις δημιουργήσει το συμβατό endpoint με OpenAI, ας δούμε πώς να το ενσωματώσετε σε ένα περιβάλλον ανάπτυξης Python (όπως το VSCode) και να χρησιμοποιήσετε το σύστημά σας ως τοπικό Πάροχο API.

1. Δημιουργήστε ένα εικονικό περιβάλλον Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Στο Linux, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Παραχωρήστε στον χρήστη σας πρόσβαση στις συσκευές GPU** (αποσυνδεθείτε και συνδεθείτε ξανά για να τεθεί σε ισχύ):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Στο Linux, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
    Στα Windows, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Συμβουλή**: Οι χρήστες Windows ενδέχεται να χρειαστεί να τροποποιήσουν την Πολιτική Εκτέλεσης PowerShell (π.χ.
    > ορίζοντάς την σε RemoteSigned ή Unrestricted) πριν εκτελέσουν ορισμένες εντολές Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Στα Windows, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Συμβουλή**: Οι χρήστες Windows ενδέχεται να χρειαστεί να τροποποιήσουν την Πολιτική Εκτέλεσης PowerShell (π.χ.
    > ορίζοντάς την σε RemoteSigned ή Unrestricted) πριν εκτελέσουν ορισμένες εντολές Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. Εγκαταστήστε το πακέτο OpenAI
    ```bash
    pip install openai
    ```

3. Εκτελέστε το παρακάτω script για να δοκιμάσετε το endpoint που μόλις δημιουργήσαμε.
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local LM Studio server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
   "temperature": 0,
   "max_tokens": 500
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
   "temperature": 0,
   "max_tokens": 500
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end --> 
<!-- @os:end -->

#### (Προαιρετικό): Εναλλαγή μεταξύ Runtimes

1. Πατήστε `Ctrl + Shift + R` στο πληκτρολόγιό σας. Εναλλακτικά, κάντε κλικ στην καρτέλα `Discover` (Μεγεθυντικός Φακός) στην αριστερή πλευρά και στη συνέχεια κάντε κλικ στο `Runtime` στο αναδυόμενο παράθυρο.
2. Θα πρέπει τότε να δείτε τις `Runtime Selections`, όπου το αναπτυσσόμενο μενού μπορεί να χρησιμοποιηθεί για την αλλαγή του runtime.


## Επόμενα Βήματα

- **Ενσωμάτωση Προσαρμοσμένης Εφαρμογής**: Ενσωματώστε τα δικά σας scripts Python ή εφαρμογές χρησιμοποιώντας το τοπικό API συμβατό με OpenAI.
- **Προηγμένα Frontends**: Συνδέστε ισχυρά περιβάλλοντα όπως το Open WebUI στον διακομιστή σας για διαχείριση ιστορικού συνομιλιών και προσωπικοτήτων.

Για περισσότερη τεκμηρίωση, επισκεφθείτε: https://lmstudio.ai/docs/developer