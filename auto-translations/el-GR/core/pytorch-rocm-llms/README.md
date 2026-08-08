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


Θέλετε να τρέξετε ισχυρά μοντέλα γλώσσας AI στο δικό σας hardware; Αυτός ο οδηγός σας δείχνει πώς.
Αυτό το tutorial χρησιμοποιεί το PyTorch με τη δύναμη του λογισμικού AMD ROCm™ για να τρέξει μοντέλα που μπορούν να συνοψίζουν έγγραφα, να απαντούν σε ερωτήσεις, να δημιουργούν κείμενο και πολλά άλλα, όλα εκτελούμενα τοπικά.

## Τι Θα Μάθετε

- Εκτέλεση LLM όπως τα gpt-oss-20b και qwen3.5-4B τοπικά χρησιμοποιώντας PyTorch και ROCm
- Δημιουργία ενός εργαλείου σύνοψης εγγράφων χρησιμοποιώντας LLM

## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού
> **Σημείωση**: Αν το VS Code δεν είναι εγκατεστημένο, μπορείτε να το εγκαταστήσετε με το Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενων Λογισμικού

### Δημιουργία Εικονικού Περιβάλλοντος

<!-- @os:linux -->
<!-- @device:halo_box -->
Στο Linux, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv με ήδη εγκατεστημένα ROCm+Pytorch.
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Παραχωρήστε στον χρήστη σας πρόσβαση σε συσκευές GPU** (αποσυνδεθείτε και συνδεθείτε ξανά για να ισχύσει αυτό):

```bash
sudo usermod -aG render,video $LOGNAME
```

Στο Linux, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv.
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
Στα Windows, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv με ήδη εγκατεστημένα ROCm+Pytorch.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Στα Windows, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Συμβουλή**: Οι χρήστες Windows ενδέχεται να χρειαστεί να τροποποιήσουν την Πολιτική Εκτέλεσης PowerShell (π.χ.
> ρυθμίζοντάς την σε RemoteSigned ή Unrestricted) πριν εκτελέσουν ορισμένες εντολές Powershell.

<!-- @os:end -->

### Εγκατάσταση Βασικών Εξαρτήσεων
<!-- @require:driver,pytorch -->

### Εγκατάσταση Πρόσθετων Εξαρτήσεων

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Γρήγορη Εκκίνηση με Παραδείγματα Scripts

Αυτό το playbook περιλαμβάνει έτοιμα προς χρήση scripts. Κάντε κλικ πάνω τους για προεπισκόπηση και λήψη στον ίδιο κατάλογο με το περιβάλλον που δημιουργήσατε.

| Script | Περιγραφή | Χρήση |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Βασική δημιουργία κειμένου με LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Εργαλείο σύνοψης εγγράφων με υποστήριξη Harmony | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

Και τα δύο scripts υποστηρίζουν:
- Επιλογή μοντέλου μέσω της σημαίας `--model`
- Μορφοποίηση προτύπου συνομιλίας για σωστή προτροπή του μοντέλου, ιδιαίτερα χρήσιμη για τη σύνοψη εγγράφων

## Φόρτωση και Εκτέλεση του Πρώτου σας LLM

Το συμπεριλαμβανόμενο script [run_llm.py](assets/run_llm.py) δείχνει πώς να δημιουργήσετε κείμενο με LLM χρησιμοποιώντας PyTorch και AMD ROCm.

> **Σημείωση:** Όταν φορτώνετε ένα μοντέλο, το Hugging Face Transformers ελέγχει πρώτα την τοπική του κρυφή μνήμη (`~/.cache/huggingface/hub` στο Linux, `C:\Users\<user>\.cache\huggingface\hub` στα Windows). Αν το μοντέλο δεν είναι αποθηκευμένο στην κρυφή μνήμη, γίνεται αυτόματη λήψη από το huggingface.co. Η πρώτη εκτέλεση μπορεί να διαρκέσει μερικά λεπτά ανάλογα με το μέγεθος του μοντέλου και την ταχύτητα δικτύου.

Το παρακάτω απόσπασμα δείχνει πώς να χρησιμοποιήσετε το μοντέλο και να προσαρμόσετε τις ερωτήσεις που τίθενται.

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

Δοκιμάστε το ληφθέν script:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Δημιουργία Εργαλείου Σύνοψης Εγγράφων

Τώρα που έχετε δημιουργήσει τοπική έξοδο LLM, μπορείτε να χτίσετε πάνω σε αυτό δημιουργώντας ένα πρακτικό εργαλείο σύνοψης εγγράφων. Σε αυτή την ενότητα, θα χρησιμοποιήσετε το script [summarizer.py](assets/summarizer.py) για να τροφοδοτήσετε ένα αρχείο .txt και να δημιουργήσετε αυτόματα μια συνοπτική περίληψη, όλα εκτελούμενα τοπικά στην GPU σας.

Το script είναι σχεδιασμένο να λειτουργεί άμεσα χωρίς πρόσθετες ρυθμίσεις. Ανοίξτε το script σε έναν επεξεργαστή για να εξερευνήσετε τον κώδικα, να προσαρμόσετε τις προτροπές και να ρυθμίσετε παραμέτρους όπως το μήκος και τη θερμοκρασία.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Παραδείγματα Χρήσης

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## Μάθετε για τις Παραμέτρους Δημιουργίας

| Παράμετρος | Τι Ελέγχει | Τυπικές Τιμές |
|-----------|------------------|----------------|
| `max_new_tokens` | Το μέγιστο μήκος της εξόδου του LLM | Χρησιμοποιήστε 50–500 tokens για περιλήψεις. (1 token είναι περίπου 0,75 αγγλικές λέξεις) |
| `temperature` | Δημιουργικότητα. Χαμηλές τιμές την κάνουν εστιασμένη, ενώ υψηλές τιμές συνοδεύονται από περισσότερη απροβλεψιμότητα | - **0,1–0,3**: Εστιασμένη, ντετερμινιστική (καλή για περιλήψεις) <br> **0,5–0,7**: Ισορροπημένη (γενική χρήση) <br> **0,8–1,0**: Δημιουργική, ποικίλη (καταιγισμός ιδεών) |
| `top_p` | Δειγματοληψία Πυρήνα (Nucleus Sampling) - Χαμηλές τιμές περιορίζουν το μοντέλο σε πιο στενές εξόδους | **0,1-0,5**: Αυστηρή, προβλέψιμη <br> **0,9-0,95**: (τυπική, φυσική, συνομιλιακή) |


## Εφαρμογές στον Πραγματικό Κόσμο

- **Ανάλυση Ερευνητικών Εργασιών**: Εξαγωγή βασικών ευρημάτων από σύνθετες δημοσιεύσεις για γρήγορη ανασκόπηση
- **Συγκέντρωση Ειδήσεων**: Σύνοψη ειδησεογραφικών άρθρων σε σύντομες καθημερινές περιλήψεις ή επισημάνσεις
- **Σημειώσεις Συναντήσεων**: Συμπύκνωση απομαγνητοφωνήσεων σε ενέργειες προς υλοποίηση και συνοπτικές περιλήψεις
- **Επισκόπηση Νομικών Εγγράφων**: Γρήγορη εξαγωγή σχετικών ρητρών ή υποχρεώσεων από μεγάλα νομικά κείμενα
- **Τεκμηρίωση Κώδικα**: Δημιουργία συνοπτικών επισκοπήσεων αποθετηρίων και επεξηγήσεων συναρτήσεων

## Επόμενα Βήματα

- **Fine-tuning**: Προσαρμογή μοντέλων στον συγκεκριμένο τομέα ή ορολογία σας για καλύτερη ακρίβεια (δείτε τα Fine-tuning Playbooks)
- **Συστήματα RAG**: Συνδυασμός LLM με ανάκτηση εγγράφων για απαντήσεις και αναζήτηση με επίγνωση του πλαισίου
- **Εξερεύνηση Μοντέλων**: Πειραματιστείτε με νέα μοντέλα όπως τα Llama 3, Phi-3, ή Qwen για καλύτερα αποτελέσματα
- **Ανάπτυξη σε Παραγωγή**: Χρησιμοποιήστε εργαλεία όπως το vLLM για κλιμακούμενη εξυπηρέτηση LLM σε οργανισμούς

Το σύστημά σας σάς δίνει τη δυνατότητα να τρέξετε εξελιγμένα μοντέλα γλώσσας τοπικά. Πειραματιστείτε με διαφορετικά μοντέλα, προτροπές και παραμέτρους για να ανακαλύψετε τι λειτουργεί καλύτερα για τις εφαρμογές σας.