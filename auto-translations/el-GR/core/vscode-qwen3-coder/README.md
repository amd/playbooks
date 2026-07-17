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

Τα coding agents είναι ισχυρά εργαλεία που ενδυναμώνουν τους προγραμματιστές μέσω συνεργασίας με AI agents που υποστηρίζονται από Μεγάλα Γλωσσικά Μοντέλα (LLMs). Μπορούν να ενσωματωθούν στο περιβάλλον ανάπτυξης, όπως το τερματικό ή το VS Code, επιτρέποντας την απρόσκοπτη ενσωμάτωση στη ροή εργασίας ενός προγραμματιστή.

Αυτό το σεμινάριο δείχνει πώς να χρησιμοποιήσετε το Cline, το VS Code και το LM Studio για να εκτελέσετε ένα coding agent εξ ολοκλήρου στον τοπικό σας υπολογιστή.

## Τι Θα Μάθετε

* Πώς να εκτελέσετε το VS Code με το coding agent Cline για βοήθεια σε εργασίες λογισμικής μηχανικής.
* Πώς να ρυθμίσετε το Cline ώστε να επικοινωνεί με το LM Studio για τοπική εκτέλεση coding agents.
* Πώς να χρησιμοποιήσετε τοπικά coding agents για την επίλυση πραγματικών εργασιών λογισμικής μηχανικής.

## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού
> **Σημείωση**: Εάν το VS Code δεν είναι εγκατεστημένο, μπορείτε να το εγκαταστήσετε μέσω του Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενου Λογισμικού

<!-- @require:lmstudio,vscode -->

## Εκκίνηση και Ρύθμιση του LM Studio

Θα χρησιμοποιήσουμε το LM Studio για να εξυπηρετήσουμε το LLM που τροφοδοτεί το coding agent.

- Στη γραμμή αναζήτησης, αναζητήστε `LM Studio` και εκκινήστε την εφαρμογή. Θα σας υποδεχτεί η παρακάτω σελίδα.

![Αρχική Οθόνη LM Studio](assets/initial-lm-studio.png)

Στη συνέχεια, πρέπει να φορτώσουμε το LLM στο σύστημα. Θα χρησιμοποιήσουμε το μοντέλο `Qwen3-Coder-30B-A3B` με μεγάλο μήκος περιβάλλοντος. (Χρησιμοποιήστε την καρτέλα Model για να το εγκαταστήσετε εάν δεν το έχετε κάνει ήδη).
- Κάντε κλικ στη γραμμή αναζήτησης στην κορυφή του παραθύρου LM Studio ή πατήστε `CTRL+L`. Κάντε κλικ στον διακόπτη `Manually choose model load parameters` και στη συνέχεια κάντε κλικ στο μοντέλο Qwen3-Coder-30B-A3B.
- Αλλάξτε το μήκος περιβάλλοντος από `4096` σε `32768` και βεβαιωθείτε ότι το `GPU Offload` είναι στο μέγιστο. Στη συνέχεια, κάντε κλικ στο `Load Model`.

![Επιλογή Μοντέλου](assets/model-list-zoomed.png)

Χρησιμοποιούμε μεγάλο μήκος περιβάλλοντος ώστε ο agent να μπορεί να επεξεργαστεί μεγάλες βάσεις κώδικα και να θυμάται τις αλλαγές που έχουν γίνει.

![Ρύθμιση Μοντέλου](assets/selecting-model-zoomed.png)

Στη συνέχεια, πρέπει να ενεργοποιήσουμε τον LM Studio Server.
- Κάντε κλικ στην καρτέλα Developer ή πατήστε `CTRL+2` στο LM Studio στα αριστερά.
- Ελέγξτε τον διακόπτη κατάστασης και βεβαιωθείτε ότι είναι ρυθμισμένος σε `Running`.

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

![Κατάσταση Διακομιστή](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Εκκίνηση και Ρύθμιση του VS Code

Θα εγκαταστήσουμε την επέκταση Cline στο VS Code και θα τη συνδέσουμε με τον LM Studio server που μόλις δημιουργήσαμε.
- Στη γραμμή αναζήτησης, αναζητήστε `VS Code` και εκκινήστε την εφαρμογή.
- Κάντε κλικ στο εικονίδιο `Extensions` στην αριστερή στήλη του VS Code και αναζητήστε `Cline`. Στη συνέχεια, κάντε κλικ στο κουμπί `Install`.

![Εγκατάσταση Επέκτασης Cline](assets/installing-cline-vscode-extension.png)

- Ένα εικονίδιο Cline θα πρέπει να εμφανίζεται στα αριστερά. Κάντε κλικ σε αυτό για να ανοίξετε το Cline. Θα εμφανιστεί ένα παράθυρο που ρωτά `How will you use Cline?` Καθώς θα χρησιμοποιούμε ένα τοπικό LLM που εκτελείται μέσω LM Studio, επιλέξτε `Bring my own API Key` και πατήστε `Continue`.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Δημιουργία Λογαριασμού](assets/cline-how-will-you-use-cline-zoomed.png)

Στη συνέχεια, πρέπει να ρυθμίσουμε το Cline ώστε να επικοινωνεί με τον LM Studio server που ρυθμίσαμε.
- Ορίστε τον API Provider σε `LM Studio` και το μοντέλο σε `Qwen3-Coder-30B-A3B-GGUF`.

>**Συμβουλή**: Ενδέχεται να είναι διαθέσιμα νεότερα μοντέλα. Εξετάστε το ενδεχόμενο λήψης και εναλλαγής σε μοντέλα Qwen3.6 εάν το επιθυμείτε.


![Ρύθμιση Μοντέλου](assets/cline-model-configuration-zoomed.png)

## Δημιουργία του πρώτου σας έργου

Ας χρησιμοποιήσουμε τον τοπικό agent μας για να δημιουργήσουμε έναν ιστότοπο! Ανοίξτε το VSCode σε έναν κατάλογο της επιλογής σας όπου το Cline θα δημιουργήσει τα αρχεία.
- Για να το κάνετε αυτό, μεταβείτε στο `File -> Open Folder` στην επάνω αριστερή γωνία του VS Code και επιλέξτε έναν φάκελο όπως `Documents`.

![VS Code Κενός Φάκελος](assets/open-cline-test.png)

Τώρα είμαστε έτοιμοι να δώσουμε εντολή στον τοπικό coding agent.
- Κάντε κλικ στην επέκταση Cline στην αριστερή στήλη και εισαγάγετε μια εντολή για να ξεκινήσετε τον agent. Ως παράδειγμα, ας χρησιμοποιήσουμε την παρακάτω εντολή:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Ο agent θα αρχίσει στη συνέχεια να δημιουργεί αρχεία σύμφωνα με την εντολή. Ως χρήστης, μπορείτε να παρακολουθείτε τον κώδικα να δημιουργείται στο VS Code όπως φαίνεται παρακάτω. Ίσως χρειαστεί να κάνετε κλικ στο `Save` κάθε φορά που το Cline θέλει να δημιουργήσει ένα αρχείο.

![Δημιουργία Κώδικα Cline](assets/cline-code-generation.png)

Μετά τη δημιουργία του λογισμικού, ο agent ολοκληρώνεται και μπορείτε να εκτελέσετε την εφαρμογή. Σε αυτή την περίπτωση, ο agent έγραψε σε τρία αρχεία: `index.html`, `script.js` και `styles.css`. Απλώς κάνοντας διπλό κλικ στο αρχείο HTML μπορούμε να φορτώσουμε και να αλληλεπιδράσουμε με τον δημιουργημένο ιστότοπο.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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

## Επόμενα Βήματα

Μετά τη δημιουργία του ιστότοπου, μπορείτε να συνεχίσετε να εργάζεστε με το Cline για τη βελτίωσή του. Δύο πιθανές βελτιώσεις είναι:

- **Τεκμηρίωση**: Η εντολή `Add a README` στον agent είναι το μόνο που χρειάζεται για να δημιουργήσει ο agent ένα αρχείο `README.md` που τεκμηριώνει τον ιστότοπο.
- **Κινούμενα Σχέδια**: Δώστε στο μοντέλο την εντολή `Add an animation that visually represents a large language model running on a laptop.` για να δημιουργήσετε ένα κινούμενο σχέδιο στον ιστότοπο.

Ενθαρρύνουμε τον αναγνώστη να δοκιμάσει να δημιουργήσει άλλες εφαρμογές χρησιμοποιώντας αυτή τη ρύθμιση. Παρακάτω είναι μερικά διασκεδαστικά παραδείγματα που έχουμε δοκιμάσει:

- **Ρετρό Παιχνίδια Arcade**: Δοκιμάστε μερικές άλλες εντολές. Μπορεί επίσης να είναι διασκεδαστικό να δημιουργήσει ο agent παιχνίδια ρετρό στυλ σε Python χρησιμοποιώντας το πακέτο `PyGame` με την παρακάτω εντολή:

```code
Create a simple pong game using the PyGame python package.
```

- **Ανάλυση Δεδομένων**: Ένας τομέας όπου τα coding agents είναι ιδιαίτερα χρήσιμα είναι αυτός της δημιουργίας σεναρίων και ανάλυσης δεδομένων. Αυτή είναι μια εντολή για να επιδείξει την ικανότητα του τοπικού μοντέλου να δημιουργεί λογισμικό ανάλυσης δεδομένων για οπτικοποίηση τιμών μετοχών:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Πόροι

Παρακάτω υπάρχουν μερικοί επιπλέον πόροι για να μάθετε περισσότερα σχετικά με τα Coding Agents, το Cline και την εκτέλεση φορτίων εργασίας σε

* Περισσότερες πληροφορίες σχετικά με τη συνεργασία AMD και LM Studio και την ενσωμάτωσή τους: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Άρθρο AMD Blog που περιγράφει την εκτέλεση του Cline σε AMD Ryzen™ AI και Radeon™ Graphics Cards: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Άρθρο Cline Blog σχετικά με την εκτέλεση coding agents τοπικά σε AI PCs: https://cline.bot/blog/local-models-amd