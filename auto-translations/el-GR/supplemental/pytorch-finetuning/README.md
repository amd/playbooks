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

Αυτό το σεμινάριο παρέχει παραδείγματα βήμα προς βήμα για τη βελτιστοποίηση (fine-tuning) ενός μεγάλου γλωσσικού μοντέλου (LLM) με PyTorch και ROCm. Καλύπτει πολλές τεχνικές, από τυπική βελτιστοποίηση έως στρατηγικές Parameter-Efficient Fine-Tuning (PEFT) με αποδοτική χρήση μνήμης, ώστε να μπορείτε να προσαρμόσετε εύκολα μοντέλα στις ανάγκες σας.

**Μοντέλο που χρησιμοποιείται**: google/gemma-3-4b-it (σενάριο QLoRA: openai/gpt-oss-20b)  *(δείτε [Ενεργοποίηση HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) αν απαιτείται πρόσβαση)*  
**Υλικό**: Κάρτα γραφικών AMD Radeon™ με υποστήριξη ROCm  
**Πλαίσιο εργασίας**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Σημείωση:** 
> - Η πλήρης βελτιστοποίηση (fine-tuning) απαιτεί τουλάχιστον **64 GB μνήμης συστήματος (RAM)**, από τα οποία τουλάχιστον **32 GB να είναι διαθέσιμα στην GPU** (τα 32 GB αποτελούν μέρος των 64 GB, όχι επιπλέον αυτών).
> - Μπορείτε επίσης να δοκιμάσετε άλλες αρχιτεκτονικές μοντέλων, συμπεριλαμβανομένου του **GPT-OSS-20B**, αντικαθιστώντας το μοντέλο στα παρεχόμενα scripts εκπαίδευσης.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Σημείωση:** Η βελτιστοποίηση LoRA και QLoRA απαιτεί τουλάχιστον **32 GB μνήμης συστήματος (RAM)**, από τα οποία τουλάχιστον **16 GB να είναι διαθέσιμα στην GPU** (τα 16 GB αποτελούν μέρος των 32 GB, όχι επιπλέον αυτών).
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση:** Η βελτιστοποίηση LoRA απαιτεί τουλάχιστον **32 GB μνήμης συστήματος (RAM)**, από τα οποία τουλάχιστον **16 GB να είναι διαθέσιμα στην GPU** (τα 16 GB αποτελούν μέρος των 32 GB, όχι επιπλέον αυτών).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Σημείωση:** Η βελτιστοποίηση LoRA και QLoRA απαιτεί κάρτα γραφικών με τουλάχιστον **16 GB αποκλειστικής μνήμης GPU** και **32 GB μνήμης συστήματος (RAM)**.
> - Σε Linux, η εκπαίδευση εκτελείται εξ ολοκλήρου στην αποκλειστική μνήμη VRAM της κάρτας γραφικών.
> - Δεν γίνεται επαναφορά σε κοινόχρηστη μνήμη GPU (μνήμη συστήματος) όταν εξαντληθεί η VRAM.
> - Κάρτες με λιγότερα από 16 GB αποκλειστικής VRAM θα εξαντλήσουν τη μνήμη κατά την εκπαίδευση σε Linux, ακόμη κι αν το σύστημα διαθέτει άφθονη RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση:** Η βελτιστοποίηση LoRA απαιτεί τουλάχιστον **16 GB συνολικής μνήμης GPU** και **32 GB μνήμης συστήματος (RAM)**.
> - Σε Windows, η συνολική μνήμη GPU συνδυάζει την αποκλειστική VRAM της κάρτας γραφικών με κοινόχρηστη μνήμη GPU (δανεισμένη από τη μνήμη συστήματος).
> - Επομένως, κάρτες με λιγότερα από 16 GB αποκλειστικής VRAM μπορούν και πάλι να εκτελέσουν αυτό το playbook χρησιμοποιώντας κοινόχρηστη μνήμη GPU για να καλύψουν τη διαφορά.
<!-- @os:end -->
<!-- @device:end -->

## Τι Θα Μάθετε

- Πώς να κάνετε fine-tuning ενός LLM χρησιμοποιώντας LoRA, QLoRA και πλήρη βελτιστοποίηση με PyTorch και ROCm
- Πώς να αποθηκεύσετε και να αναπτύξετε (deploy) το βελτιστοποιημένο μοντέλο σας
- Πώς να παρακολουθείτε την εκπαίδευση και να διορθώνετε συνήθη προβλήματα

<!-- @device:halo_box,halo,stx,krk -->
## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού
> **Σημείωση**: Αν το VS Code δεν είναι εγκατεστημένο, μπορείτε να το εγκαταστήσετε μέσω του Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενου Λογισμικού

<!-- @prereq:hf-models-gemma-3-4b-it,hf-datasets-databricks-dolly-15k -->
<!-- @os:linux -->
<!-- @prereq:hf-datasets-english-quotes -->
<!-- @os:end -->

#### Δημιουργία Εικονικού Περιβάλλοντος

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update 
sudo apt install -y python3-venv 
python3 -m venv finetune-venv --system-site-packages 
source finetune-venv/bin/activate 
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Παραχωρήστε στον χρήστη σας πρόσβαση στις συσκευές GPU** (αποσυνδεθείτε και συνδεθείτε ξανά για να εφαρμοστεί αυτό):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv finetune-venv
source finetune-venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Εγκατάσταση Βασικών Εξαρτήσεων
<!-- @require:pytorch -->

#### Επιπλέον Εξαρτήσεις

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Εδώ δοκιμάζονται και υποστηρίζονται μόνο τα βασικά πακέτα. **Το bitsandbytes δεν υποστηρίζεται καλά σε Windows**, γι' αυτό η εγκατάσταση για Windows το παραλείπει· χρησιμοποιήστε LoRA ή πλήρη βελτιστοποίηση σε Windows (το QLoRA απαιτεί bitsandbytes και προορίζεται για Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Ενεργοποίηση HF authentication (μοντέλα με περιορισμένη πρόσβαση ή προσαρμοσμένα / μη προεγκατεστημένα)

Σε αυτό το παράδειγμα χρησιμοποιούμε το **google/gemma-3-4b-it**, το οποίο είναι ένα μοντέλο με **περιορισμένη πρόσβαση (gated)**. Πρέπει να αποδεχτείτε τους όρους του μοντέλου στο Hugging Face και στη συνέχεια να πιστοποιηθείτε ώστε τα scripts εκπαίδευσης να μπορούν να το κατεβάσουν.

1. **Αποδοχή της άδειας χρήσης:** Ανοίξτε το [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), συνδεθείτε (ή δημιουργήστε λογαριασμό) και αποδεχτείτε την άδεια χρήσης/τους όρους στη σελίδα του μοντέλου (π.χ. "Agree and access repository").
2. **Εγκατάσταση και σύνδεση:** Εγκαταστήστε το Hugging Face CLI και στη συνέχεια εκτελέστε την τυπική σύνδεση:

```bash
pip install huggingface_hub
hf auth login
```

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['train_qlora.py', 'train_lora.py', 'train_full_finetuning.py']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in scripts:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
from trl import SFTTrainer

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=verify-package-version timeout=60 hidden=True setup=activate-venv -->
```python
import importlib.metadata as md

pkgs = [
    "torch", "transformers", "trl", "peft", "accelerate",
    "datasets", "safetensors", "fsspec", "bitsandbytes",
    "huggingface_hub", "tokenizers",
]
for p in pkgs:
    try:
        print(f"{p}: {md.version(p)}")
    except md.PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
```
<!-- @test:end -->

<!-- @test:id=quick-train-lora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=quick-train-qlora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_qlora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=quick-train-full-finetuning timeout=1200 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_full_finetuning.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @device:end -->
---

## Κατανόηση των Τεχνικών

### Τι είναι το LoRA;

Το **LoRA (Low-Rank Adaptation)** διατηρεί το βασικό μοντέλο παγωμένο (frozen) και εκπαιδεύει μόνο μικρούς πίνακες "προσαρμογέα" (adapter) που προστίθενται σε ορισμένα επίπεδα. 

- **Η βασική ιδέα**: αντί να ενημερώνουμε έναν τεράστιο πίνακα βαρών με εκατομμύρια παραμέτρους, μαθαίνουμε μια ενημέρωση χαμηλής τάξης (low-rank) (δύο μικρούς πίνακες των οποίων το γινόμενο έχει πολύ λιγότερες παραμέτρους). Αυτό δίνει μεγάλη μείωση στις εκπαιδεύσιμες παραμέτρους και στη VRAM, διατηρώντας παράλληλα το μεγαλύτερο μέρος της ποιότητας της πλήρους βελτιστοποίησης.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Τι είναι το QLoRA;

Το **QLoRA** συνδυάζει **κβαντισμό 4-bit (4-bit quantization)** με το **LoRA**. Το βασικό μοντέλο φορτώνεται σε 4-bit (μεγάλη εξοικονόμηση μνήμης) και μόνο οι προσαρμογείς LoRA εκπαιδεύονται με μεγαλύτερη ακρίβεια. Έτσι αποκτάτε την αποδοτικότητα παραμέτρων του LoRA σε συνδυασμό με πολύ χαμηλότερη χρήση VRAM, με μικρό συμβιβασμό στην ποιότητα σε σχέση με το LoRA πλήρους ακρίβειας. Σημειώστε ότι ο κβαντισμός 4-bit μπορεί να προκαλέσει αριθμητικές αστάθειες (απότομες αυξήσεις στην απώλεια ή NaN), γι' αυτό οι χρήστες συχνά προτιμούν το **LoRA** όταν υπάρχει διαθέσιμη αρκετή VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Σημείωση**: Για βασικά μοντέλα MXFP4 όπως το `openai/gpt-oss-20b`, συνιστούμε τη χρήση του **LoRA** (`train_lora.py`) αντί του QLoRA. Το μονοπάτι 4-bit του `bitsandbytes` στο script QLoRA συνήθως αποκβαντίζει (dequantizes) τα βάρη MXFP4 σε BF16, οπότε η εκτέλεση συμπεριφέρεται όπως το τυπικό LoRA. Το εγγενές MXFP4 απαιτεί το `bitsandbytes` χτισμένο από τον πηγαίο κώδικα, μαζί με αντίστοιχο στοίβαγμα Transformers/Triton/kernels. Δείτε την [τεκμηρίωση Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Επιλέξτε τη Μέθοδό σας

| Μέθοδος | Μνήμη | Ταχύτητα | Ποιότητα | Καλύτερο για |
|--------|--------|-------|---------|----------|
| **QLoRA** (μόνο Linux) | 12-16GB | Ταχύτερη | 90-95% | Χαμηλή Χρήση Μνήμης |
| **LoRA** | 24-32GB | Γρήγορη | 95-98% | Ισορροπημένη προσέγγιση |
| **Full** | 80GB+ | Πιο αργή | 100% | Μέγιστη ποιότητα |

### 3. Εκτελέστε την Εκπαίδευση

**Σύνολο δεδομένων και τι μαθαίνει το μοντέλο**  
Τα scripts μετατρέπουν το σύνολο δεδομένων σε παραδείγματα συνομιλίας. Για παράδειγμα, το script QLoRA χρησιμοποιεί το **Abirate/english_quotes**: κάθε παράδειγμα γίνεται ένα ζεύγος user–assistant όπως:

- **User:** «Δώσε μου ένα απόφθεγμα σχετικά με: &lt;tag&gt;»
- **Assistant:** «&lt;quote&gt; – &lt;author&gt;»

Το fine-tuning διδάσκει το μοντέλο να απαντά σε προτροπές που ζητούν αποφθέγματα σχετικά με ένα θέμα και να τα επιστρέφει στη μορφή `<quote text> - <author>`. Τα scripts LoRA και full fine-tuning χρησιμοποιούν το **databricks/databricks-dolly-15k** (γενικά ζεύγη εντολής/απόκρισης), οπότε η ακριβής εργασία διαφέρει ανάλογα με το script· η ιδέα είναι η ίδια - προσαρμόστε το μοντέλο στο σύνολο δεδομένων και τη μορφή που έχετε επιλέξει.

Παρακάτω παρατίθεται μια σύνοψη των διαθέσιμων μεθόδων εκπαίδευσης. Κάθε μέθοδος συνδέεται με το script της και παρέχει μια σύντομη περιγραφή για την επιλογή της κατάλληλης προσέγγισης.

| Script                           | Μέθοδος            | Περιγραφή                                                                                                         | Τυπικό VRAM | Συνιστάται για                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Εκπαιδεύει μικρούς πίνακες adapter ενώ παγώνει το βασικό μοντέλο. 3–5 φορές ταχύτερο· ~95–98% της πλήρους ποιότητας.                         | 24–32GB      | Προχωρημένοι χρήστες· πολλαπλοί adapters· περισσότερο VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(μόνο Linux)*             | **QLoRA**       | 4-bit κβαντισμός + adapters LoRA. Χαμηλότερη χρήση μνήμης, ταχύτερο, μικρός συμβιβασμός ποιότητας. Απαιτεί `bitsandbytes` (μόνο Linux).                            | 12–16GB      | Οι περισσότεροι χρήστες· γρήγορα πειράματα· περιορισμένο VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Πλήρες Fine-tuning** | Ενημερώνει όλες τις παραμέτρους του μοντέλου. Μέγιστη ποιότητα· υψηλότερη χρήση μνήμης και υπολογιστικής ισχύος.                                    | 40GB+        | Μέγιστη ποιότητα· έρευνα· μεγάλο VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Σημείωση:** Το πλήρες fine-tuning (`train_full_finetuning.py`) ενδέχεται να απαιτεί περισσότερα από 64GB RAM συστήματος και μπορεί να μην είναι εφικτό σε αυτή τη συσκευή. Εξετάστε το ενδεχόμενο χρήσης LoRA ή QLoRA αντ' αυτού.
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση:** Το πλήρες fine-tuning (`train_full_finetuning.py`) ενδέχεται να απαιτεί περισσότερα από 64GB RAM συστήματος και μπορεί να μην είναι εφικτό σε αυτή τη συσκευή. Εξετάστε το ενδεχόμενο χρήσης LoRA αντ' αυτού.
<!-- @os:end -->
<!-- @device:end -->

Απλώς επιλέξτε την προτιμώμενη `Training method`, κατεβάστε το αντίστοιχο script και εκτελέστε το χρησιμοποιώντας την εντολή διατηρώντας το εικονικό σας περιβάλλον ενεργοποιημένο: 

```python
python3 train_<method_name>.py.
```

## Χρήση του Fine-Tuned Μοντέλου σας

### Μετά το Πλήρες Fine-Tuning

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Μετά την Εκπαίδευση LoRA/QLoRA

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gpt-oss-20b-qlora",   # or "output-gemma-3-4b-it-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Συγχώνευση του Adapter LoRA στο Βασικό Μοντέλο

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Σημείωση:**  
- Βεβαιωθείτε ότι το όνομα του καταλόγου μοντέλου (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) ταιριάζει με τον πραγματικό φάκελο εξόδου από την εκπαίδευση.  
- Αν χρησιμοποιήσατε LoRA αντί για QLoRA, απλώς αντικαταστήστε τη διαδρομή ανάλογα.  
- Ορισμένα μοντέλα Gemma απαιτούν τον ορισμό `trust_remote_code=True` στο `from_pretrained`· προσθέστε το αν δείτε σχετική προειδοποίηση.

Για περισσότερες προσαρμοσμένες ρυθμίσεις (padding tokens, συσκευή, κ.λπ.), ανατρέξτε στο script που χρησιμοποιήσατε για την εκπαίδευση.

<!-- @test:id=verify-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-lora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LoRA output looks correct")
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-qlora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-qlora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: QLoRA output looks correct")
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=verify-full-finetuning-output timeout=300 hidden=True setup=activate-venv -->
```python
import glob
import os
import sys

out_dir = "output-gemma-3-4b-it-full"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

# Weights may be saved as a single model.safetensors or, when the model
# exceeds max_shard_size, as model-*.safetensors shards plus an index.
single = os.path.exists(os.path.join(out_dir, "model.safetensors"))
shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not single and not shards:
    print("FAIL: No model safetensors weights found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Οδηγός Προσαρμογής

### Χρήση του Δικού σας Συνόλου Δεδομένων

Όλα τα scripts χρησιμοποιούν την ίδια μορφή συνόλου δεδομένων. Αντικαταστήστε την ενότητα φόρτωσης:

```python
from datasets import load_dataset

# Option 1: Local JSON/JSONL file
dataset = load_dataset('json', data_files='your_data.json')

# Option 2: Hugging Face Hub dataset
dataset = load_dataset('username/dataset-name')

# Option 3: CSV file
dataset = load_dataset('csv', data_files='data.csv')

# Format for chat models
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

dataset = dataset.map(format_instruction)
```

**Μορφή Συνόλου Δεδομένων για Τοπικό Αρχείο JSON/JSONL:**

Όταν χρησιμοποιείτε αυτή τη μέθοδο, βεβαιωθείτε ότι τα αρχεία JSON σας είναι σωστά δομημένα για να αποφύγετε σφάλματα ανάλυσης. 

Πρέπει να τηρούνται οι ακόλουθες κατευθυντήριες γραμμές:
* **Μορφοποίηση Αρχείου:** Τα αρχεία JSON θα πρέπει να μορφοποιούνται εντός ενός Ολοκληρωμένου Περιβάλλοντος Ανάπτυξης (IDE) για να διασφαλιστεί η σωστή δομή και σύνταξη.
* **Απαιτούμενα Κλειδιά:** Το προσαρμοσμένο αρχείο JSON πρέπει να περιέχει τα κλειδιά `instruction` και `response`. Αυτά τα κλειδιά είναι απαραίτητα για τη σωστή λειτουργία της μεθόδου.
```json
[
  {
    "instruction": "Your first instruction here",
    "response": "Expected response here"
  },
  {
    "instruction": "Your second instruction here",
    "response": "Expected response here"
  }
]
```
**Μορφή Συνόλου Δεδομένων για Σύνολο Δεδομένων Hugging Face Hub**

Όταν χρησιμοποιείτε σύνολα δεδομένων από το Hugging Face, βεβαιωθείτε ότι τα σύνολα δεδομένων σας είναι σωστά δομημένα για να διευκολύνετε την απρόσκοπτη ενσωμάτωση. 

Πρέπει να ακολουθούνται οι εξής κατευθυντήριες γραμμές:
* **Ζεύγος Εντολής-Απόκρισης:** Εστιάστε σε σύνολα δεδομένων που περιλαμβάνουν ένα ζεύγος `instruction-response`. Αυτή η δομή είναι απαραίτητη για την επιδιωκόμενη λειτουργικότητα.
* **Προσαρμοσμένη Τροποποίηση Κλειδιού:** Αν το σύνολο δεδομένων σας δεν συμμορφώνεται με τη δομή `instruction-response`, έχετε τη δυνατότητα να τροποποιήσετε τη συνάρτηση `format_instruction()`. Αυτό σας επιτρέπει να προσαρμόσετε συγκεκριμένα κλειδιά όπως χρειάζεται.

Παράδειγμα Προσαρμογής: Σε περιπτώσεις όπου η έξοδος του συνόλου δεδομένων χρειάζεται προσαρμογή, μπορείτε να τροποποιήσετε την ενότητα απόκρισης εντός της συνάρτησης format_instruction() ώστε να ταιριάζει με τις απαιτήσεις σας.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Μορφή Συνόλου Δεδομένων για Αρχείο CSV**

Για να προσαρμόσετε το script ώστε να χρησιμοποιεί μορφή αρχείου CSV, πρέπει να βεβαιωθείτε ότι το αρχείο CSV περιέχει στήλες με όνομα `instruction` και `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Προσαρμογή Παραμέτρων Εκπαίδευσης

Επεξεργαστείτε το script εκπαίδευσης και αλλάξτε τις μεταβλητές ώστε να ταιριάζουν με τους στόχους σας: **ρυθμός μάθησης** (`LR`), **εποχές** (`EPOCHS`), **μέγεθος παρτίδας** (`BATCH_SIZE`), **συσσώρευση κλίσης** (`GRAD_ACCUM_STEPS`), και για LoRA/QLoRA **βαθμίδα** (`LORA_R`). Για ταχύτερες εκτελέσεις χρησιμοποιήστε λιγότερες εποχές και υψηλότερο ρυθμό μάθησης (LR)· για καλύτερη ποιότητα χρησιμοποιήστε περισσότερες εποχές και χαμηλότερο LR. Μειώστε το μέγεθος παρτίδας ή το μήκος ακολουθίας αν αντιμετωπίσετε σφάλματα έλλειψης μνήμης.
### Συμβουλές Βελτιστοποίησης Μνήμης

Αν αντιμετωπίσετε σφάλματα έλλειψης μνήμης:

**1. Μειώστε το Μέγεθος Παρτίδας (Batch Size):**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Μειώστε το Μήκος Ακολουθίας:**
```python
max_seq_length=256  # Instead of 512
```

**3. Χρησιμοποιήστε πιο Επιθετική Κβαντοποίηση:**
```
Full → LoRA → QLoRA
```

**4. Ενεργοποιήστε το Gradient Checkpointing (μόνο για πλήρη fine-tuning):**
```python
model.gradient_checkpointing_enable()
```

---

## Παρακολούθηση & Αποσφαλμάτωση

### Παρακολουθήστε τη Μνήμη του GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Προαιρετικά) Παρακολουθήστε τα Πειράματά σας με το Weights & Biases

Για να καταγράψετε εκτελέσεις και μετρήσεις στο [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

Στο σενάριο εκπαίδευσης, ορίστε `report_to="wandb"` και προαιρετικά `run_name="your-experiment-name"` στη ρύθμιση του trainer. Αν προτιμάτε να μην χρησιμοποιήσετε το Wandb, αφήστε το `report_to` στην προεπιλεγμένη τιμή του ή ορίστε το σε `"none"`.

### Συνήθη Προβλήματα

#### Έλλειψη Μνήμης (OOM)

**Λύση:** Μειώστε το μέγεθος παρτίδας (batch size) ή/και χρησιμοποιήστε QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Η Απώλεια Δεν Μειώνεται

**Λύση:** Προσαρμόστε τον ρυθμό μάθησης (learning rate)
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Αργή Εκπαίδευση

**Λύση:** Αυξήστε το μέγεθος παρτίδας (batch size) αν η μνήμη το επιτρέπει
```python
BATCH_SIZE = 8
```
## Επόμενα Βήματα

Αφού ολοκληρώσετε επιτυχώς το fine-tuning, εξετάστε τα παρακάτω επόμενα βήματα για να αξιοποιήσετε περισσότερο το μοντέλο σας:

1. **Αξιολογήστε** διεξοδικά σε δεδομένα δοκιμής που δεν έχουν χρησιμοποιηθεί, για να μετρήσετε τη γενίκευση και να αποφύγετε το overfitting.
2. **Πειραματιστείτε** δοκιμάζοντας διαφορετικές τιμές υπερπαραμέτρων για καλύτερους συμβιβασμούς ακρίβειας, ταχύτητας και μνήμης.
3. **Παρακολουθήστε** όλα τα πειράματά σας (και τις αντίστοιχες μετρήσεις) με το Weights & Biases για αναπαραγώγιμη έρευνα.
4. **Δοκιμάστε** να εκπαιδεύσετε σε δικά σας προσαρμοσμένα σύνολα δεδομένων για να προσαρμόσετε το μοντέλο ειδικά στην περίπτωση χρήσης σας.
5. **Αναπτύξτε** το fine-tuned μοντέλο σας για γρήγορη εξαγωγή συμπερασμάτων (inference) χρησιμοποιώντας αποδοτικά backends όπως το vLLM σε συμβατό υλικό.
6. **Εξερευνήστε** προηγμένες τεχνικές, όπως prompt engineering, μικτή ακρίβεια (mixed precision) και μεγαλύτερα μήκη ακολουθιών.
7. **Εκπαιδεύστε** πολλαπλούς προσαρμογείς LoRA για διαφορετικές εργασίες ή τομείς και εναλλάξτε τους όπως χρειάζεται.

---