<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Επισκόπηση

Αυτό το playbook δείχνει πώς να κάνετε fine-tune ένα γλωσσικό μοντέλο τοπικά με Unsloth σε AMD υλικό.

Χρησιμοποιεί ένα σύντομο παράδειγμα Supervised Fine-Tuning (SFT) με LoRA adapters στο `unsloth/gemma-4-E4B-it`, χρησιμοποιώντας ένα υποσύνολο του dataset `mlabonne/FineTome-100k`. Ο στόχος είναι να σας δώσει ένα απλό end-to-end workflow που καλύπτει τη ρύθμιση, την εκπαίδευση, την εξαγωγή συμπερασμάτων και την αποθήκευση του fine-tuned αποτελέσματος.

Το παράδειγμα είναι σχεδιασμένο να είναι πρακτικό και εύκολο να τροποποιηθεί, ώστε να μπορείτε να το χρησιμοποιήσετε ως σημείο εκκίνησης για τα δικά σας datasets και μοντέλα.

## Τι Θα Μάθετε

- Πώς να ρυθμίσετε το περιβάλλον Unsloth
- Πώς να κάνετε fine-tune ένα LLM χρησιμοποιώντας SFT με Unsloth
- Πώς να αποθηκεύσετε το fine-tuned αποτέλεσμα στον τοπικό χώρο αποθήκευσης

<!-- @device:halo,stx,krk -->
> **Σημείωση:** Οι τεχνικές fine-tuning σε αυτό το playbook απαιτούν τουλάχιστον 24 GB μνήμης GPU και 32 GB μνήμης RAM συστήματος.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Σημείωση:** Οι τεχνικές fine-tuning σε αυτό το playbook απαιτούν τουλάχιστον 24 GB μνήμης GPU και 32 GB μνήμης RAM συστήματος.
<!-- @os:end -->

<!-- @os:linux -->
> **Σημείωση:** Οι τεχνικές fine-tuning σε αυτό το playbook απαιτούν τουλάχιστον 24 GB **αποκλειστικής** μνήμης GPU και 32 GB μνήμης RAM συστήματος.
<!-- @os:end -->
<!-- @device:end -->

## Γιατί Unsloth;

Το Unsloth κάνει το fine-tuning LLM ευκολότερο να εκτελεστεί σε τοπικό υλικό, μειώνοντας τη χρήση μνήμης και επιταχύνοντας την εκπαίδευση σε σύγκριση με μια τυπική ρύθμιση.

Σε αυτό το playbook, χρησιμοποιούμε το Unsloth μαζί με **SFT βασισμένο σε LoRA**. Αυτό σημαίνει ότι το βασικό μοντέλο παραμένει κυρίως παγωμένο, ενώ εκπαιδεύεται ένα πολύ μικρότερο σύνολο βαρών adapter. Αυτό ταιριάζει καλά για τοπική ανάπτυξη επειδή είναι ελαφρύτερο από το πλήρες fine-tuning και πιο γρήγορο για επανάληψη.

Το Unsloth υποστηρίζει επίσης άλλες προσεγγίσεις εκπαίδευσης, συμπεριλαμβανομένων των QLoRA και ροών εργασίας ενισχυτικής μάθησης. Αυτό το playbook εστιάζει πρώτα στην απλούστερη διαδρομή: ένα μικρό παράδειγμα LoRA fine-tuning που οι χρήστες μπορούν να εκτελέσουν, να κατανοήσουν και να επεκτείνουν.

## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού
> **Σημείωση**: Εάν το VS Code δεν είναι εγκατεστημένο, μπορείτε να το εγκαταστήσετε με το Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενων Λογισμικού

### Δημιουργία Εικονικού Περιβάλλοντος

<!-- @os:linux -->
<!-- @device:halo_box -->
Ανοίξτε ένα τερματικό και δημιουργήστε ένα venv με AMD ROCm™ λογισμικό και PyTorch ήδη εγκατεστημένα:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Παραχωρήστε στον χρήστη σας πρόσβαση στις συσκευές GPU** (αποσυνδεθείτε και επανασυνδεθείτε για να τεθεί σε ισχύ):

```bash
sudo usermod -aG render,video $LOGNAME
```

Ανοίξτε ένα τερματικό και δημιουργήστε ένα venv:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση:** Απαιτείται Python 3.13 για Windows.

<!-- @device:halo_box -->
Ανοίξτε ένα τερματικό PowerShell και δημιουργήστε ένα εικονικό περιβάλλον:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Ανοίξτε ένα τερματικό PowerShell και δημιουργήστε ένα εικονικό περιβάλλον:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Εγκατάσταση Βασικών Εξαρτήσεων
<!-- @require:pytorch,driver -->

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### Πρόσθετες Εξαρτήσεις

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Σημείωση:** Κατά την εισαγωγή, το Unsloth ενδέχεται να ελέγξει προαιρετικά μονοπάτια επιτάχυνσης `bitsandbytes`. Σε ορισμένες εκδόσεις ROCm, ενδέχεται να δείτε ένα μήνυμα όπως `bitsandbytes library load error: Configured ROCm binary not found`. Αυτό το playbook χρησιμοποιεί τυπικό LoRA fine-tuning με `optim="adamw_torch"`, επομένως δεν βασιζόμαστε στον βελτιστοποιητή `bitsandbytes` ή στο 4-bit QLoRA. Αυτό το μήνυμα μπορεί να αγνοηθεί με ασφάλεια.

<!-- @os:windows -->
> **Σημείωση:** Στο Windows ROCm, το Unsloth θα εκτυπώσει αρκετές προειδοποιήσεις κατά την εκκίνηση — δείτε [Γνωστές Προειδοποιήσεις](#known-warnings) παρακάτω. Όλες είναι ασφαλές να αγνοηθούν· η εκπαίδευση λειτουργεί σωστά.
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## Λήψη του Script Fine-Tuning του Unsloth

Αντί να εκτελείτε κάθε βήμα χειροκίνητα, αυτό το playbook παρέχει ένα καθαρό, end-to-end script εδώ: [test_unsloth.py](assets/test_unsloth.py).

Εκτελέστε τον παρακάτω κώδικα για να εκτελέσετε το script:

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

Το υπόλοιπο του playbook θα διατρέξει εννοιολογικά κάθε κύριο βήμα του script.

## Πώς Λειτουργεί

Το script test_unsloth.py εκτελεί τα παρακάτω βήματα:
* **Φόρτωση Μοντέλου**: Φορτώνει το unsloth/gemma-4-E4B-it χρησιμοποιώντας FastModel.
* **Προετοιμασία Δεδομένων**: Τυποποιεί το dataset (π.χ., FineTome-100k) και εφαρμόζει το πρότυπο συνομιλίας Gemma-4.
* **Εφαρμογή LoRA**: Προσθέτει adapters σε γλωσσικές, modules προσοχής και MLP για αποδοτική εκπαίδευση.
* **Εκπαίδευση**: Χρησιμοποιεί SFTTrainer με μάσκαρισμα απώλειας μόνο για απαντήσεις.
* **Εξαγωγή Συμπερασμάτων**: Εκτελεί ένα γρήγορο τεστ παραγωγής για επαλήθευση της απόδοσης.
* **Αποθήκευση**: Εξάγει τοπικά τα LoRA adapters.

## Βασική Διαμόρφωση

Μπορείτε να τροποποιήσετε τις παρακάτω σταθερές για να προσαρμόσετε την εκτέλεσή σας:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Παράδειγμα του μηνύματος καλωσορίσματος Unsloth και εξόδου κατά τη φόρτωση των βαρών μοντέλου:

![εναλλακτικό κείμενο](assets/welcome.png)

## Προετοιμασία Dataset

Χρησιμοποιούμε ένα υποσύνολο του:
```text
mlabonne/FineTome-100k
```
Το dataset:
* Μετατρέπεται σε μορφή συνομιλίας
* Επεξεργάζεται χρησιμοποιώντας το πρότυπο συνομιλίας Gemma-4
* Καθαρίζεται για την αφαίρεση διπλότυπων BOS tokens

## Εκπαίδευση του Μοντέλου

Το script εκτελεί μια σύντομη επίδειξη εκπαίδευσης, με τις παρακάτω παραμέτρους:
- ~50 βήματα
- Μικρό μέγεθος batch
- Συσσώρευση κλίσης

Κατά τη διάρκεια της εκπαίδευσης, θα δείτε αρχεία καταγραφής όπως:

![εναλλακτικό κείμενο](assets/training.png)


## Αποθήκευση και Ανάπτυξη

### Τοπική Αποθήκευση (LoRA)

Το script αποθηκεύει αυτόματα τα LoRA adapters στο OUTPUT_DIR.
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### Αποθήκευση συγχωνευμένου μοντέλου (για vLLM)

<!-- @os:windows -->
> **Σημείωση:** Το vLLM δεν υποστηρίζει Windows. Για να αναπτύξετε το fine-tuned μοντέλο σας στα Windows, χρησιμοποιήστε llama.cpp (δείτε [Εξαγωγή GGUF](#export-gguf-for-llamacpp) παρακάτω) ή μεταφέρετε το συγχωνευμένο μοντέλο σε ένα μηχάνημα Linux που εκτελεί vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Για ανάπτυξη με vLLM, συγχωνεύστε τα adapters σε ένα πλήρες μοντέλο:
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### Εξαγωγή GGUF (για llama.cpp)

Μετατρέψτε απευθείας σε GGUF για τοπική εξαγωγή συμπερασμάτων:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Γνωστές Προειδοποιήσεις

Αυτές οι προειδοποιήσεις εκτυπώνονται από το Unsloth κατά την εκκίνηση στο Windows ROCm και είναι όλες ασφαλές να αγνοηθούν:

| Προειδοποίηση | Αιτία | Ασφαλές να αγνοηθεί; |
|---|---|---|
| `bitsandbytes library load error` | Το bitsandbytes δεν έχει έκδοση Windows ROCm | Ναι — αυτό το playbook χρησιμοποιεί `adamw_torch`, όχι bnb |
| `No ROCm platform found for torch.distributed` | Το ROCm-on-Windows δεν διαθέτει κατανεμημένη εκπαίδευση | Ναι — η εκπαίδευση single-GPU δεν επηρεάζεται |
| `Unsloth: WARNING! You are using an unsupported platform` | Το Unsloth επισημαίνει εκδόσεις εκτός Linux | Ναι — το Windows ROCm λειτουργεί για single-GPU SFT |
| `triton is not available` | Το Triton δεν έχει έκδοση Windows | Ναι — το Unsloth επιστρέφει σε PyTorch kernels |

Η εκπαίδευση θα προχωρήσει σωστά παρά αυτές τις προειδοποιήσεις.
<!-- @os:end -->

## Επόμενα Βήματα
- Δοκιμάστε το [Unsloth Studio](https://unsloth.ai/docs/new/studio), ένα διαισθητικό GUI για Unsloth
- Εκπαιδεύστε στα δικά σας συγκεκριμένα datasets
- Δοκιμάστε fine-tuning με διαφορετικές υπερπαραμέτρους
- Αναπτύξτε με vLLM ή llama.cpp
- Δοκιμάστε QLoRA για ρύθμιση με χαμηλότερη μνήμη

## Πόροι

Παρακάτω υπάρχουν μερικοί πρόσθετοι πόροι για να μάθετε περισσότερα σχετικά με το Unsloth και το finetuning:

* [Τεκμηρίωση Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Οδηγός Fine-tuning Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)