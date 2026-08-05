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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Αυτό το playbook απαιτεί τουλάχιστον **32GB** μνήμης συστήματος.
<!-- @device:end -->

## Επισκόπηση

Οι πράκτορες κωδικοποίησης (coding agents) είναι ισχυρά εργαλεία που ενδυναμώνουν τους προγραμματιστές μέσω της συνεργασίας με πράκτορες AI που υποστηρίζονται από Large Language Models (LLMs). Μπορούν να ενσωματωθούν στο περιβάλλον ανάπτυξης, όπως το τερματικό ή το VS Code, επιτρέποντας απρόσκοπτη ενσωμάτωση στη ροή εργασίας ενός προγραμματιστή.

Αυτό το tutorial δείχνει πώς να χρησιμοποιήσετε τα Cline, VS Code και LM Studio για να εκτελέσετε έναν πράκτορα κωδικοποίησης εξ ολοκλήρου στο τοπικό σας μηχάνημα.

## Τι θα μάθετε

* Πώς να εκτελέσετε το VS Code με τον πράκτορα κωδικοποίησης Cline για να βοηθήσετε σε εργασίες μηχανικής λογισμικού.
* Πώς να διαμορφώσετε το Cline ώστε να επικοινωνεί με το LM Studio για τοπική εξαγωγή συμπερασμάτων (inference) πρακτόρων κωδικοποίησης.
* Πώς να χρησιμοποιήσετε τοπικούς πράκτορες κωδικοποίησης για να επιλύσετε πραγματικά προβλήματα μηχανικής λογισμικού.

## Ρύθμιση Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού
> **Σημείωση**: Εάν το VS Code δεν είναι εγκατεστημένο, μπορείτε να το εγκαταστήσετε με το Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενων Λογισμικού

<!-- @require:lmstudio,vscode -->

## Εκκίνηση και Διαμόρφωση του LM Studio

Θα χρησιμοποιήσουμε το LM Studio για να εξυπηρετήσουμε το LLM που τροφοδοτεί τον πράκτορα κωδικοποίησης.

- Στη γραμμή αναζήτησης, αναζητήστε `LM Studio` και εκκινήστε την εφαρμογή. Θα σας υποδεχτεί η ακόλουθη σελίδα.

![Αρχική Οθόνη LM Studio](assets/initial-lm-studio.png)

Στη συνέχεια, πρέπει να φορτώσουμε το LLM στο σύστημα. Θα χρησιμοποιήσουμε το μοντέλο `Qwen3-Coder-30B-A3B` με μεγάλο μήκος πλαισίου (context length). (Χρησιμοποιήστε την καρτέλα Model για να το εγκαταστήσετε αν δεν το έχετε κάνει ήδη).
- Κάντε κλικ στη γραμμή αναζήτησης στο επάνω μέρος του παραθύρου LM Studio ή πατήστε `CTRL+L`. Κάντε κλικ στον διακόπτη `Manually choose model load parameters` και έπειτα κάντε κλικ στο μοντέλο Qwen3-Coder-30B-A3B.
- Αλλάξτε το μήκος πλαισίου από `4096` σε `32768`, και βεβαιωθείτε ότι το `GPU Offload` βρίσκεται στο μέγιστο. Στη συνέχεια, κάντε κλικ στο `Load Model`

![Επιλογή Μοντέλου](assets/model-list-zoomed.png)

Χρησιμοποιούμε μεγάλο μήκος πλαισίου ώστε ο πράκτορας να μπορεί να επεξεργάζεται μεγάλες βάσεις κώδικα και να θυμάται τις αλλαγές που έχουν γίνει.

![Διαμόρφωση Μοντέλου](assets/selecting-model-zoomed.png)

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

![Κατάσταση Server](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
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
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Εκκίνηση και Διαμόρφωση του VS Code

Θα εγκαταστήσουμε την επέκταση Cline στο VS Code και θα τη συνδέσουμε με τον server LM Studio που μόλις δημιουργήσαμε.
- Στη γραμμή αναζήτησης, αναζητήστε `VS Code` και εκκινήστε την εφαρμογή.
- Κάντε κλικ στο εικονίδιο `Extensions` στην αριστερή στήλη του VS Code και αναζητήστε `Cline`. Στη συνέχεια, κάντε κλικ στο κουμπί `Install`.

![Εγκατάσταση Επέκτασης Cline](assets/installing-cline-vscode-extension.png)

- Ένα εικονίδιο Cline θα πρέπει να εμφανιστεί στα αριστερά. Κάντε κλικ σε αυτό για να ανοίξετε το Cline. Θα εμφανιστεί ένα παράθυρο που ρωτά `How will you use Cline?` Καθώς θα χρησιμοποιήσουμε ένα τοπικό LLM που εκτελείται μέσω του LM Studio, επιλέξτε `Bring my own API Key` και πατήστε `Continue`.

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

Στη συνέχεια, πρέπει να διαμορφώσουμε το Cline ώστε να επικοινωνεί με τον server LM Studio που ρυθμίσαμε.
- Ορίστε τον API Provider σε `LM Studio` και το μοντέλο σε `Qwen3-Coder-30B-A3B-GGUF`.

>**Συμβουλή**: Ενδέχεται να είναι διαθέσιμα νεότερα μοντέλα. Εξετάστε το ενδεχόμενο λήψης και μετάβασης σε μοντέλα Qwen3.6 εάν το επιθυμείτε.


![Διαμόρφωση Μοντέλου](assets/cline-model-configuration-zoomed.png)

## Δημιουργία του πρώτου σας project

Ας χρησιμοποιήσουμε τον τοπικό μας πράκτορα για να δημιουργήσουμε έναν ιστότοπο! Ανοίξτε το VSCode σε έναν φάκελο της επιλογής σας όπου το Cline θα δημιουργήσει τα αρχεία.
- Για να το κάνετε αυτό, πηγαίνετε στο `File -> Open Folder` στο επάνω αριστερό μέρος του VS Code και επιλέξτε έναν φάκελο όπως `Documents`.

![Κενός Φάκελος VS Code](assets/open-cline-test.png)

Τώρα είμαστε έτοιμοι να δώσουμε prompt στον τοπικό πράκτορα κωδικοποίησης.
- Κάντε κλικ στην επέκταση Cline στην αριστερή στήλη και εισάγετε ένα prompt για να ξεκινήσετε τον πράκτορα. Ως παράδειγμα, ας χρησιμοποιήσουμε το ακόλουθο prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Ο πράκτορας θα ξεκινήσει τότε να δημιουργεί αρχεία σύμφωνα με το prompt. Ως χρήστης, μπορείτε να παρακολουθήσετε τον κώδικα να δημιουργείται στο VS Code όπως φαίνεται παρακάτω. Ίσως χρειαστεί να κάνετε κλικ στο `Save` κάθε φορά που το Cline θέλει να δημιουργήσει ένα αρχείο.

![Δημιουργία Κώδικα Cline](assets/cline-code-generation.png)

Αφού δημιουργηθεί το λογισμικό, ο πράκτορας ολοκληρώνει τη διαδικασία και μπορείτε να εκτελέσετε την εφαρμογή. Σε αυτή την περίπτωση, ο πράκτορας έγραψε σε τρία αρχεία: `index.html`, `script.js` και `styles.css`. Κάνοντας απλά διπλό κλικ στο αρχείο HTML μπορούμε να φορτώσουμε και να αλληλεπιδράσουμε με τον ιστότοπο που δημιουργήθηκε.

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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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

Αφού δημιουργήσετε τον ιστότοπο, μπορείτε να συνεχίσετε να συνεργάζεστε με το Cline για να τον βελτιώσετε. Δύο πιθανές βελτιώσεις είναι:

- **Τεκμηρίωση**: Αρκεί να δώσετε στον πράκτορα την προτροπή `Add a README` για να δημιουργήσει ένα αρχείο `README.md` που τεκμηριώνει τον ιστότοπο.
- **Κίνηση (Animation)**: Δώστε στο μοντέλο την προτροπή `Add an animation that visually represents a large language model running on a laptop.` για να δημιουργήσει ένα animation στον ιστότοπο.

Ενθαρρύνουμε τον αναγνώστη να δοκιμάσει να δημιουργήσει και άλλες εφαρμογές χρησιμοποιώντας αυτή τη διαμόρφωση. Παρακάτω παραθέτουμε μερικά διασκεδαστικά παραδείγματα που έχουμε δοκιμάσει:

- **Retro Arcade Παιχνίδια**: Δοκιμάστε μερικές άλλες προτροπές. Μπορεί επίσης να είναι διασκεδαστικό για τον πράκτορα να δημιουργήσει παιχνίδια σε retro στιλ σε Python χρησιμοποιώντας το πακέτο `PyGame` με την ακόλουθη προτροπή:

```code
Create a simple pong game using the PyGame python package.
```

- **Ανάλυση Δεδομένων**: Ένας τομέας στον οποίο οι πράκτορες κωδικοποίησης είναι ιδιαίτερα χρήσιμοι είναι η δημιουργία scripts και η ανάλυση δεδομένων. Αυτή είναι μια προτροπή που αναδεικνύει την ικανότητα του τοπικού μοντέλου να δημιουργεί λογισμικό ανάλυσης δεδομένων για την οπτικοποίηση τιμών μετοχών:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Πόροι

Παρακάτω παρατίθενται ορισμένοι επιπλέον πόροι για να μάθετε περισσότερα σχετικά με τους Coding Agents, το Cline και την εκτέλεση φόρτων εργασίας σε 

* Περισσότερες πληροφορίες σχετικά με τη συνεργασία και την ενσωμάτωση της AMD με το LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog της AMD που παρουσιάζει την εκτέλεση του Cline σε κάρτες AMD Ryzen™ AI και Radeon™ Graphics: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog του Cline σχετικά με την τοπική εκτέλεση coding agents σε AI PC: https://cline.bot/blog/local-models-amd