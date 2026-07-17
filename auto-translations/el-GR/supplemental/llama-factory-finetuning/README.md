## Επισκόπηση

Η αποδοτική βελτιστοποίηση (fine-tuning) είναι ζωτικής σημασίας για την προσαρμογή μεγάλων γλωσσικών μοντέλων (LLMs) σε κατάντη εργασίες. Το LLaMA-Factory είναι μια ανοιχτού κώδικα και φιλική προς τον χρήστη πλατφόρμα που απλοποιεί την εκπαίδευση και τη βελτιστοποίηση μεγάλων γλωσσικών μοντέλων και πολυτροπικών μοντέλων. Επιτρέπει στους χρήστες να προσαρμόζουν εκατοντάδες προεκπαιδευμένα μοντέλα τοπικά με ελάχιστη κωδικοποίηση.

Αυτό το playbook σας διδάσκει πώς να βελτιστοποιείτε LLMs χρησιμοποιώντας το LLaMA-Factory στο τοπικό σας υλικό AMD.

<!-- @device:stx,krk -->
> **Σημείωση:** Οι τεχνικές βελτιστοποίησης σε αυτό το playbook απαιτούν τουλάχιστον **32 GB μνήμης RAM συστήματος**, με τουλάχιστον **16 GB από αυτά διαθέσιμα στο GPU** (τα 16 GB αποτελούν μέρος των 32 GB, όχι επιπλέον αυτών).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Σημείωση:** Οι τεχνικές βελτιστοποίησης σε αυτό το playbook απαιτούν τουλάχιστον **16 GB συνολικής μνήμης GPU** και **32 GB μνήμης RAM συστήματος**.
> - Στα Windows, η συνολική μνήμη GPU συνδυάζει την αποκλειστική VRAM της κάρτας γραφικών με την κοινόχρηστη μνήμη GPU (που δανείζεται από τη μνήμη RAM του συστήματος).
> - Επομένως, κάρτες με λιγότερα από 16 GB αποκλειστικής VRAM μπορούν να εκτελέσουν αυτό το playbook χρησιμοποιώντας κοινόχρηστη μνήμη GPU για να καλύψουν τη διαφορά.
<!-- @os:end -->

<!-- @os:linux -->
> **Σημείωση:** Οι τεχνικές βελτιστοποίησης σε αυτό το playbook απαιτούν κάρτα γραφικών με τουλάχιστον **16 GB αποκλειστικής μνήμης GPU** και **32 GB μνήμης RAM συστήματος**.
> - Στο Linux, η εκπαίδευση εκτελείται εξ ολοκλήρου στην αποκλειστική VRAM της κάρτας γραφικών.
> - Δεν επιστρέφει σε κοινόχρηστη μνήμη GPU (μνήμη RAM συστήματος) όταν εξαντληθεί η VRAM.
> - Κάρτες με λιγότερα από 16 GB αποκλειστικής VRAM θα εξαντλήσουν τη μνήμη κατά την εκπαίδευση στο Linux, ακόμα και αν το σύστημα διαθέτει άφθονη μνήμη RAM.
<!-- @os:end -->
<!-- @device:end -->

## Τι θα Μάθετε

- Πώς να ρυθμίσετε το LLaMA-Factory με το λογισμικό AMD ROCm™
- Πώς να διαμορφώσετε τις παραμέτρους βελτιστοποίησης LLM (χρησιμοποιώντας το Qwen/Qwen3-4B-Instruct-2507 ως παράδειγμα)
- Πώς να εκτελέσετε τη βελτιστοποίηση LLaMA-Factory
- Πώς να εκτελέσετε συμπέρασμα (inference) με το βελτιστοποιημένο μοντέλο
- Πώς να εξαγάγετε το βελτιστοποιημένο μοντέλο

## Εκτιμώμενος Χρόνος

- Διάρκεια: Θα χρειαστούν περίπου 60 λεπτά για την εκτέλεση αυτού του playbook (ανάλογα με το μέγεθος του μοντέλου/συνόλου δεδομένων και την ταχύτητα δικτύου).
- Δείτε το [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) για περισσότερες πληροφορίες.

## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενων Λογισμικού

<!-- @os:linux -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```bash
python3 --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```powershell
python --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

#### Δημιουργία Εικονικού Περιβάλλοντος

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env --system-site-packages
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Παραχωρήστε στον χρήστη σας πρόσβαση στις συσκευές GPU** (αποσυνδεθείτε και συνδεθείτε ξανά για να τεθεί σε ισχύ):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env --system-site-packages
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->
<!-- @os:end -->

### Εγκατάσταση Βασικών Εξαρτήσεων

<!-- @require:pytorch,driver -->
 
### Εγκατάσταση Πρόσθετων Εξαρτήσεων

> **Σημείωση**: Βεβαιωθείτε ότι η έκδοση Python είναι 3.11, 3.12 ή 3.13

```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### Εγκατάσταση του LLaMA-Factory

Το LLaMA-Factory εξαρτάται από το PyTorch. Θα πρέπει ήδη να το έχετε εγκαταστήσει σύμφωνα με τις παραπάνω απαιτήσεις.

Κατεβάστε τον πηγαίο κώδικα από το [επίσημο αποθετήριο LLaMA Factory στο GitHub](https://github.com/hiyouga/LlamaFactory) και εγκαταστήστε τις εξαρτήσεις του.

<!-- @device:halo_box -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install setuptools --break-system-packages
pip install -e . --break-system-packages
pip install -r requirements/metrics.txt --break-system-packages
```
<!-- @test:end --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt 
```
<!-- @test:end --> 
<!-- @device:end -->

Επαληθεύστε αν το `llamafactory-cli` είναι εκτελέσιμο.

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
echo "llamafactory-cli is available"
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```powershell
cd LlamaFactory
if (Get-Command llamafactory-cli -ErrorAction SilentlyContinue) {
    llamafactory-cli version
    Write-Host "llamafactory-cli is available"
} else {
    Write-Host "llamafactory-cli is not available"
}
```
<!-- @test:end --> 
<!-- @os:end -->

Παράδειγμα εξόδου:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Έχοντας εγκαταστήσει επιτυχώς το LLaMA-Factory, ας εκτελέσουμε τη βελτιστοποίηση σε αυτό.

## Χρήση του LLaMA Factory CLI για Βελτιστοποίηση

Αυτή η ενότητα θα καλύψει τον τρόπο προετοιμασίας συνόλων δεδομένων βελτιστοποίησης, τη διαμόρφωση παραμέτρων LoRA/QLoRA και την εκτέλεση βελτιστοποίησης LoRA.

### Προετοιμασία Συνόλου Δεδομένων

Το LLaMA-Factory υποστηρίζει σύνολα δεδομένων βελτιστοποίησης σε μορφή Alpaca και μορφή ShareGPT. Όλα τα διαθέσιμα σύνολα δεδομένων έχουν οριστεί στο [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Εάν χρησιμοποιείτε προσαρμοσμένο σύνολο δεδομένων, βεβαιωθείτε ότι έχετε προσθέσει μια περιγραφή συνόλου δεδομένων στο `dataset_info.json` και καθορίστε το όνομα του συνόλου δεδομένων πριν από την εκπαίδευση. Λεπτομέρειες μπορείτε να βρείτε στην τεκμηρίωσή τους [εδώ](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

Σε αυτό το playbook, θα χρησιμοποιήσουμε τα σύνολα δεδομένων identity και alpaca_en_demo ως παράδειγμα, και θα διαμορφώσουμε τις πληροφορίες συνόλου δεδομένων στο επόμενο βήμα.


### Διαμόρφωση παραμέτρων βελτιστοποίησης

Το LLaMA-Factory υποστηρίζει πολλαπλά σχήματα βελτιστοποίησης.

| Σχήματα Βελτιστοποίησης | Παραδείγματα LLaMA-Factory |
|-----------|------|
| Πλήρης Παράμετρος    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Βελτιστοποίηση LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Βελτιστοποίηση QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end -->

Αυτά τα παραδείγματα αρχείων διαμόρφωσης έχουν καθορίσει παραμέτρους μοντέλου, παραμέτρους μεθόδου βελτιστοποίησης, παραμέτρους συνόλου δεδομένων, παραμέτρους αξιολόγησης και άλλα. Μπορείτε να τα διαμορφώσετε σύμφωνα με τις δικές σας ανάγκες. Σε αυτό το playbook, θα χρησιμοποιήσουμε το [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml).

**Επεξήγηση βασικών παραμέτρων:**
- `model_name_or_path` - Όνομα μοντέλου Hugging Face ή τοπική διαδρομή αρχείου μοντέλου.
- `stage` - Στάδιο εκπαίδευσης. Επιλογές: rm (μοντελοποίηση ανταμοιβής), pt (προεκπαίδευση), sft (Εποπτευόμενη Βελτιστοποίηση), PPO, DPO, KTO, ORPO.
- `do_train` - true για εκπαίδευση, false για αξιολόγηση
- `finetuning_type` - Μέθοδος βελτιστοποίησης. Επιλογές: freeze, lora, full
- `lora_rank` - Η διαστατικότητα του πίνακα χαμηλής τάξης που χρησιμοποιείται στο LoRA, τυπικές τιμές: 4, 6, 8, 16 (μικρότερες τιμές = λιγότερες παράμετροι = ταχύτερη βελτιστοποίηση· μεγαλύτερες τιμές = καλύτερη προσαρμογή εργασίας αλλά υψηλότερη χρήση πόρων).
- `lora_target` - Μονάδες-στόχοι για τη μέθοδο LoRA. Προεπιλογή: all.
- `dataset` - Σύνολο/α δεδομένων προς χρήση. Χρησιμοποιήστε "," για διαχωρισμό πολλαπλών συνόλων δεδομένων
- `output_dir` - Διαδρομή εξόδου βελτιστοποίησης
- `logging_steps` - Διάστημα καταγραφής σε βήματα
- `save_steps` - Διάστημα αποθήκευσης σημείου ελέγχου μοντέλου.
- `overwrite_output_dir` - Εάν επιτρέπεται η αντικατάσταση του καταλόγου εξόδου.
- `per_device_train_batch_size` - Μέγεθος δέσμης εκπαίδευσης ανά συσκευή.
- `gradient_accumulation_steps` - Αριθμός βημάτων συσσώρευσης κλίσης.
- `learning_rate` - Ρυθμός μάθησης
- `num_train_epochs` - Αριθμός εποχών εκπαίδευσης
- `lr_scheduler_type` - Χρονοδιάγραμμα ρυθμού μάθησης. Επιλογές: linear, cosine, polynomial, constant, κ.λπ.
- `warmup_ratio` - Αναλογία προθέρμανσης ρυθμού μάθησης

<!-- @os:linux -->
Θα τροποποιήσουμε την προεπιλεγμένη τιμή του `lora_rank` για να εκτελέσουμε βελτιστοποίηση σε AMD Ryzen™ & AMD Radeon™ GPUs.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Θα ενημερώσουμε την προεπιλεγμένη διαμόρφωση βελτιστοποίησης LoRA για καλύτερη συμβατότητα με AMD Ryzen™ και AMD Radeon™ GPUs:
- Ορισμός του `lora_rank` από `8` σε `6` για μείωση της χρήσης μνήμης κατά τη βελτιστοποίηση.
- Χρήση `fp16` αντί για `bf16` για ευρύτερη συμβατότητα AMD GPU και χαμηλότερη χρήση μνήμης.
- Ορισμός του `dataloader_num_workers` σε `0` στα Windows για αποφυγή σφαλμάτων `"Can't pickle local object<>"` που προκαλούνται από φόρτωση δεδομένων πολλαπλής επεξεργασίας.

```powershell
$filePath = "examples/train_lora/qwen3_lora_sft.yaml"

# Create a backup before modifying the YAML file
Copy-Item -Path $filePath -Destination "$filePath.bak" -Force

# Read the file and update the training settings
$content = Get-Content -Path $filePath -Raw

$newContent = $content `
  -replace 'lora_rank: 8', 'lora_rank: 6' `
  -replace 'bf16: true', 'fp16: true' `
  -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0'

Set-Content -Path $filePath -Value $newContent
```
<!-- @os:end -->

### Εκτέλεση Βελτιστοποίησης LLaMA-Factory

Το **llamafactory-cli** είναι το επίσημο εργαλείο διεπαφής γραμμής εντολών (CLI) για το LLaMA-Factory, αναπτυγμένο για την απλοποίηση ολοκληρωμένων ροών εργασίας LLM (προετοιμασία δεδομένων → βελτιστοποίηση → αξιολόγηση → ανάπτυξη) χωρίς τη συγγραφή σύνθετου κώδικα.

Για εκπαίδευση/βελτιστοποίηση, το **llamafactory-cli train** είναι η βασική υποεντολή του LLaMA Factory CLI. Αφαιρεί τις ροές εργασίας βελτιστοποίησης (προεπεξεργασία δεδομένων, συντονισμός υπερπαραμέτρων, βελτιστοποίηση υλικού) σε μία μόνο εντολή CLI, υποστηρίζοντας πολλαπλά παραδείγματα βελτιστοποίησης (LoRA/QLoRA/Πλήρης Βελτιστοποίηση) και είναι βελτιστοποιημένο για GPUs χαμηλών πόρων (π.χ., QLoRA σε 16GB VRAM).

Μπορείτε να εκτελέσετε τη βελτιστοποίηση LLaMA-Factory χρησιμοποιώντας την παρακάτω εντολή, η οποία βασίζεται στο τροποποιημένο αρχείο διαμόρφωσης βελτιστοποίησης Qwen3 LoRA.

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

sed -i 's/max_samples: .*/max_samples: 16/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
if grep -q '^max_steps:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^max_steps:.*/max_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf '\nmax_steps: 5\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi
if grep -q '^save_total_limit:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^save_total_limit:.*/save_total_limit: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf 'save_total_limit: 1\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"

Copy-Item -Path "examples/train_lora/qwen3_lora_sft.yaml" -Destination "examples/train_lora/qwen3_lora_sft_ci.yaml"

$filePath = "examples/train_lora/qwen3_lora_sft_ci.yaml"
(Get-Content -Path $filePath) -replace 'lora_rank: 8', 'lora_rank: 6' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'bf16:\s*true', 'fp16: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'dataloader_num_workers:\s*4', 'dataloader_num_workers: 0' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'output_dir: .*', 'output_dir: saves/qwen3_lora_sft_ci' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'overwrite_output_dir: false', 'overwrite_output_dir: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'per_device_train_batch_size: .*', 'per_device_train_batch_size: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'gradient_accumulation_steps: .*', 'gradient_accumulation_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'num_train_epochs: .*', 'num_train_epochs: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'logging_steps: .*', 'logging_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'save_steps: .*', 'save_steps: 5' | Set-Content -Path $filePath

(Get-Content -Path $filePath) -replace 'max_samples: .*', 'max_samples: 16' | Set-Content -Path $filePath
if (Select-String -Path $filePath -Pattern '^max_steps:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^max_steps:.*', 'max_steps: 5' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value ""
    Add-Content -Path $filePath -Value "max_steps: 5"
}
if (Select-String -Path $filePath -Pattern '^save_total_limit:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^save_total_limit:.*', 'save_total_limit: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "save_total_limit: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

Μετά την εκτέλεση της βελτιστοποίησης LLM, όλες οι παραγόμενες έξοδοι αποθηκεύονται στο "output_dir", συμπεριλαμβανομένων αρχείων σημείου ελέγχου μοντέλου, αρχείων διαμόρφωσης και μετρικών εκπαίδευσης.

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 

### Δοκιμή του βελτιστοποιημένου μοντέλου

Το **llamafactory-cli chat** έχει σχεδιαστεί για διαδραστική συνομιλία/συμπέρασμα με LLMs (τόσο βασικά μοντέλα όσο και μοντέλα βελτιστοποιημένα με LoRA). Το LLaMA-Factory παρέχει το δείγμα διαμόρφωσης για την εκτέλεση συμπεράσματος βελτιστοποιημένων μοντέλων στο [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Μπορείτε επίσης να τροποποιήσετε αυτό το δείγμα διαμόρφωσης για να αλλάξετε τις ρυθμίσεις, όπως το backend συμπεράσματος.

Χρησιμοποιήστε την παρακάτω εντολή για να δοκιμάσετε το βελτιστοποιημένο μοντέλο Qwen3:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Ένα παράδειγμα συνομιλίας με το βελτιστοποιημένο μοντέλο φαίνεται παρακάτω:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Εξαγωγή του βελτιστοποιημένου μοντέλου

Για περιπτώσεις χρήσης σε παραγωγή, το προεκπαιδευμένο μοντέλο και ο προσαρμογέας LoRA πρέπει να συγχωνευθούν και να εξαχθούν σε ένα ενιαίο μοντέλο. Αυτό το συγχωνευμένο μοντέλο μπορεί να χρησιμοποιηθεί ως κανονικό αρχείο μοντέλου Hugging Face. Το LLaMA-Factory παρέχει δείγματα διαμορφώσεων στο [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Χρησιμοποιήστε την παρακάτω εντολή για να εξαγάγετε το βελτιστοποιημένο μοντέλο Qwen3:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Το αποτέλεσμα της εξαγωγής του βελτιστοποιημένου μοντέλου φαίνεται παρακάτω.

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Fine-Tuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"
pip install pyyaml

$script = @'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
'@

$tempPy = Join-Path $env:TEMP "write_llamafactory_export_config.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
    throw "FAIL: Could not create qwen3_lora_sft_ci.yaml"
}
Remove-Item $tempPy -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "examples/merge_lora/qwen3_lora_sft_ci.yaml")) {throw "FAIL: examples/merge_lora/qwen3_lora_sft_ci.yaml was not created"}

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
if ($LASTEXITCODE -ne 0) {throw "FAIL: llamafactory-cli export failed"}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end --> 

## Χρήση του LLaMA Factory GUI

Το `LLaMA-Factory` υποστηρίζει επίσης βελτιστοποίηση LLMs χωρίς κώδικα μέσω ενός web UI στο πρόγραμμα περιήγησης.

Χρησιμοποιήστε την παρακάτω εντολή για να το ανοίξετε:

```bash
llamafactory-cli webui
```
Το `LlamaFactory Web UI` προσφέρει μια απλοποιημένη διεπαφή για τη διαχείριση ροών εργασίας μηχανικής μάθησης, συμπεριλαμβανομένης της εκπαίδευσης, αξιολόγησης, πρόβλεψης, συνομιλίας και εξαγωγής μοντέλων. Ακολουθεί μια σύντομη εισαγωγή σε κάθε καρτέλα:

* **Train**: Αυτή η καρτέλα σάς επιτρέπει να επιλέξετε ένα μοντέλο και σύνολο δεδομένων, να διαμορφώσετε παραμέτρους εκπαίδευσης και να ξεκινήσετε τη διαδικασία εκπαίδευσης. Είναι απαραίτητο να κατανοήσετε τις υποχρεωτικές και προαιρετικές παραμέτρους για τη βελτιστοποίηση της ρύθμισης εκπαίδευσης.
* **Evaluate & Predict**: Μετά την εκπαίδευση, μπορείτε να αξιολογήσετε την απόδοση του μοντέλου και να κάνετε προβλέψεις χρησιμοποιώντας αυτή την καρτέλα. Παρέχει πληροφορίες για την ακρίβεια και την αποτελεσματικότητα του μοντέλου σε νέα δεδομένα.
* **Chat**: Μόλις ολοκληρωθεί η εκπαίδευση, φορτώστε το μοντέλο στην καρτέλα Chat για να αλληλεπιδράσετε μαζί του και να δείτε τα αποτελέσματα της εργασίας σας. Αυτή η λειτουργία επιτρέπει επικοινωνία σε πραγματικό χρόνο με το εκπαιδευμένο μοντέλο.
* **Export**: Αυτή η καρτέλα διευκολύνει την εξαγωγή εκπαιδευμένων μοντέλων για ανάπτυξη ή περαιτέρω χρήση. Μπορείτε να αποθηκεύσετε τα μοντέλα σας σε διάφορες μορφές κατάλληλες για διαφορετικές εφαρμογές.

Για λεπτομερή καθοδήγηση, σας ενθαρρύνουμε να ανατρέξετε στην επίσημη τεκμηρίωση στο [αποθετήριο LlamaFactory GitHub](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) και στο [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Επιπλέον, το [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) παρέχει πολύτιμες πληροφορίες για τη διεπαφή και τις λειτουργίες της.

## Επόμενα Βήματα
- Δοκιμάστε διαφορετικ