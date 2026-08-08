<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

## Panoramica

Il fine-tuning efficiente è fondamentale per adattare i modelli linguistici di grandi dimensioni (LLM) a compiti specifici. LLaMA Factory è una piattaforma open-source e di facile utilizzo che semplifica l'addestramento e il fine-tuning di modelli linguistici di grandi dimensioni e modelli multimodali. Consente agli utenti di personalizzare centinaia di modelli pre-addestrati localmente con una codifica minima.

Questa guida ti insegna come effettuare il fine-tuning degli LLM utilizzando LLaMA Factory sul tuo hardware AMD locale.

<!-- @device:stx,krk -->
> **Nota:** Le tecniche di fine-tuning descritte in questa guida richiedono almeno **32 GB di RAM di sistema**, di cui almeno **16 GB disponibili per la GPU** (i 16 GB fanno parte dei 32 GB, non si aggiungono ad essi).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Nota:** Le tecniche di fine-tuning descritte in questa guida richiedono almeno **16 GB di memoria GPU totale** e **32 GB di RAM di sistema**.
> - Su Windows, la memoria GPU totale combina la VRAM dedicata della scheda grafica con la memoria GPU condivisa (presa in prestito dalla RAM di sistema).
> - Pertanto, le schede con meno di 16 GB di VRAM dedicata possono comunque eseguire questa guida utilizzando la memoria GPU condivisa per colmare la differenza.
<!-- @os:end -->

<!-- @os:linux -->
> **Nota:** Le tecniche di fine-tuning descritte in questa guida richiedono una scheda grafica con almeno **16 GB di memoria GPU dedicata** e **32 GB di RAM di sistema**.
> - Su Linux, l'addestramento viene eseguito interamente nella VRAM dedicata della scheda grafica.
> - Non si ricorre alla memoria GPU condivisa (RAM di sistema) quando la VRAM si esaurisce.
> - Le schede con meno di 16 GB di VRAM dedicata esauriranno la memoria durante l'addestramento su Linux, anche se il sistema dispone di abbondante RAM.
<!-- @os:end -->
<!-- @device:end -->

## Cosa Imparerai

- Come configurare LLaMA Factory con il software AMD ROCm™
- Come configurare i parametri di fine-tuning degli LLM (utilizzando Qwen/Qwen3-4B-Instruct-2507 come esempio)
- Come eseguire il fine-tuning con LLaMA Factory
- Come eseguire l'inferenza con il modello sottoposto a fine-tuning
- Come esportare il modello sottoposto a fine-tuning

## Tempo Stimato

- Durata: l'esecuzione di questa guida richiederà circa 60 minuti (a seconda delle dimensioni del modello/dataset e della velocità di rete).
- Consulta il [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) per maggiori informazioni.

## Impostazione della Configurazione della Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli Aggiornamenti Software

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei Prerequisiti Software

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

#### Creare un Ambiente Virtuale

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
**Concedi al tuo utente l'accesso ai dispositivi GPU** (disconnettiti e riconnettiti affinché la modifica abbia effetto):

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

### Installazione delle Dipendenze di Base

<!-- @require:pytorch,driver -->
 
### Installazione delle Dipendenze Aggiuntive

> **Nota**: Assicurati che la versione di Python sia 3.11, 3.12 o 3.13

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

### Installare LLaMA Factory

LLaMA Factory dipende da PyTorch. Dovresti già averlo installato in base ai requisiti sopra indicati.

Scarica il codice sorgente dal [repository ufficiale GitHub di LLaMA Factory](https://github.com/hiyouga/LlamaFactory) e installa le sue dipendenze.

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

Verifica se `llamafactory-cli` è eseguibile.

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

Output di esempio:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Dopo aver installato correttamente LLaMA Factory, procediamo con l'esecuzione del fine-tuning.

## Utilizzo della CLI di LLaMA Factory per il Fine-Tuning

Questa sezione tratterà come preparare i dataset di fine-tuning, configurare i parametri LoRA/QLoRA ed eseguire il fine-tuning LoRA.

### Preparazione del Dataset

LLaMA Factory supporta dataset di fine-tuning nei formati Alpaca e ShareGPT. Tutti i dataset disponibili sono stati definiti nel file [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Se stai utilizzando un dataset personalizzato, assicurati di aggiungere una descrizione del dataset in `dataset_info.json` e di specificare il nome del dataset prima dell'addestramento. I dettagli sono disponibili nella loro documentazione [qui](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

In questa guida, utilizzeremo i dataset identity e alpaca_en_demo come esempio, e configureremo le informazioni del dataset nel passaggio successivo.
### Configurazione dei parametri di fine-tuning

LLaMA Factory supporta diversi schemi di fine-tuning.

| Schemi di fine-tuning | Esempi LLaMA Factory |
|-----------|------|
| Full-Parameter    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Fine-tuning LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Fine-tuning QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

Questi file di configurazione di esempio hanno specificato i parametri del modello, i parametri del metodo di fine-tuning, i parametri del dataset, i parametri di valutazione e altro ancora. Puoi configurarli secondo le tue esigenze. In questo playbook, utilizzeremo [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Spiegazione dei parametri chiave:**
- `model_name_or_path` - Nome del modello Hugging Face o percorso del file del modello locale.
- `stage` - Fase di addestramento. Opzioni: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true per l'addestramento, false per la valutazione
- `finetuning_type` - Metodo di fine-tuning. Opzioni: freeze, lora, full
- `lora_rank` - La dimensionalità della matrice a basso rango utilizzata in LoRA, valori tipici: 4, 6, 8, 16 (valori più piccoli = meno parametri = fine-tuning più veloce; valori più grandi = migliore adattamento al task ma maggior utilizzo di risorse).
- `lora_target` - Moduli target per il metodo LoRA. Predefinito: all.
- `dataset` - Dataset da utilizzare. Usa “,” per separare più dataset
- `output_dir` - Percorso di output del fine-tuning
- `logging_steps` - Intervallo di logging in step
- `save_steps` - Intervallo di salvataggio del checkpoint del modello.
- `overwrite_output_dir` - Se consentire la sovrascrittura della directory di output.
- `per_device_train_batch_size` - Dimensione del batch di addestramento per dispositivo.
- `gradient_accumulation_steps` - Numero di step di accumulo del gradiente.
- `learning_rate` - Learning rate
- `num_train_epochs` - Numero di epoche di addestramento
- `lr_scheduler_type` - Pianificazione del learning rate. Opzioni: linear, cosine, polynomial, constant, ecc.
- `warmup_ratio` - Rapporto di warmup del learning rate

<!-- @os:linux -->
Modificheremo il valore predefinito di `lora_rank` per eseguire il fine-tuning su GPU AMD Ryzen™ e AMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Aggiorneremo la configurazione predefinita di fine-tuning LoRA per una migliore compatibilità con le GPU AMD Ryzen™ e AMD Radeon™:
- Impostare `lora_rank` da `8` a `6` per ridurre l'utilizzo di memoria durante il fine-tuning.
- Utilizzare `fp16` invece di `bf16` per una maggiore compatibilità con le GPU AMD e un minor utilizzo di memoria.
- Impostare `dataloader_num_workers` su `0` su Windows per evitare errori `"Can't pickle local object<>"` causati dal caricamento dei dati in multiprocessing.

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

### Esecuzione del fine-tuning con LLaMA Factory 

**llamafactory-cli** è lo strumento ufficiale a riga di comando (CLI) per LLaMA Factory, sviluppato per semplificare i flussi di lavoro end-to-end degli LLM (preparazione dei dati → fine-tuning → valutazione → distribuzione) senza scrivere codice complesso.

Per l'addestramento/fine-tuning, **llamafactory-cli train** è il sottocomando principale della CLI di LLaMA Factory. Astrae i flussi di lavoro di fine-tuning (preelaborazione dei dati, ottimizzazione degli iperparametri, ottimizzazione hardware) in un unico comando CLI, supportando molteplici paradigmi di fine-tuning (LoRA/QLoRA/Full Fine-Tuning) ed è ottimizzato per GPU con risorse limitate (ad esempio, QLoRA su 16GB di VRAM).

Puoi eseguire il fine-tuning di LLaMA Factory utilizzando il seguente comando, basato sul file di configurazione modificato per il fine-tuning LoRA di Qwen3.

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

Dopo aver eseguito il fine-tuning dell'LLM, tutti gli output generati vengono memorizzati in "output_dir", inclusi i file di checkpoint del modello, i file di configurazione e le metriche di addestramento.

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

### Testare il modello sottoposto a fine-tuning 

**llamafactory-cli chat** è progettato per la chat/inferenza interattiva con gli LLM (sia modelli base che modelli sottoposti a fine-tuning LoRA). LLaMA Factory fornisce la configurazione di esempio per eseguire l'inferenza dei modelli sottoposti a fine-tuning in [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Puoi anche modificare questa configurazione di esempio per cambiare le impostazioni, come il backend di inferenza.

Utilizza il seguente comando per testare il modello Qwen3 sottoposto a fine-tuning:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Di seguito è mostrato un esempio di chat utilizzando il modello sottoposto a fine-tuning:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Esportare il modello sottoposto a fine-tuning

Per i casi d'uso in produzione, il modello pre-addestrato e l'adattatore LoRA devono essere uniti ed esportati in un unico modello. Questo modello unito può essere utilizzato come un normale file di modello Hugging Face. LLaMA Factory fornisce le configurazioni di esempio in [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Utilizza il seguente comando per esportare il modello Qwen3 sottoposto a fine-tuning:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Di seguito è mostrato il risultato dell'esportazione del modello sottoposto a fine-tuning.

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
## Utilizzo della GUI di LLaMA Factory

`LLaMA-Factory` supporta anche il fine-tuning senza codice degli LLM tramite un'interfaccia web nel browser.

Usa il seguente comando per aprirla:

```bash
llamafactory-cli webui
```
La `LlamaFactory Web UI` offre un'interfaccia semplificata per gestire i flussi di lavoro di machine learning, tra cui addestramento, valutazione, previsione, chat ed esportazione dei modelli. Ecco una breve introduzione a ciascuna scheda:

* **Train**: questa scheda consente di selezionare un modello e un dataset, configurare i parametri di addestramento e avviare il processo di addestramento. È essenziale comprendere i parametri obbligatori e facoltativi per ottimizzare la configurazione dell'addestramento.
* **Evaluate & Predict**: dopo l'addestramento, è possibile valutare le prestazioni del modello ed effettuare previsioni utilizzando questa scheda. Fornisce informazioni sull'accuratezza e sull'efficacia del modello su nuovi dati.
* **Chat**: una volta completato l'addestramento, carica il modello nella scheda Chat per interagire con esso e vedere i risultati del tuo lavoro. Questa funzionalità consente la comunicazione in tempo reale con il modello addestrato.
* **Export**: questa scheda facilita l'esportazione dei modelli addestrati per la distribuzione o per un ulteriore utilizzo. È possibile salvare i modelli in vari formati adatti a diverse applicazioni.

Per una guida dettagliata, ti invitiamo a consultare la documentazione ufficiale sul [repository GitHub di LlamaFactory](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) e su [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Inoltre, la [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) fornisce informazioni preziose sull'interfaccia e sulle sue funzionalità.

## Prossimi passi
- Prova modelli diversi come `gpt-oss` e altri modelli all'avanguardia.
- Sperimenta con diversi backend sul modello sottoposto a fine-tuning
 
Per ulteriore documentazione, visita: https://llamafactory.readthedocs.io/en/latest/ 