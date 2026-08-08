<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Übersicht

Dieses Tutorial bietet Schritt-für-Schritt-Beispiele zum Fine-Tuning eines großen Sprachmodells (Large Language Model, LLM) mit PyTorch und ROCm. Es behandelt mehrere Techniken, vom Standard-Fine-Tuning bis hin zu speichereffizienten Parameter-Efficient Fine-Tuning (PEFT)-Strategien, damit Sie Modelle einfach an Ihre Bedürfnisse anpassen können.

**Verwendetes Modell**: google/gemma-3-4b-it *(siehe [HF-Authentifizierung aktivieren](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), falls das Modell zugangsbeschränkt ist)*  
**Hardware**: AMD Radeon™ GPU mit ROCm-Unterstützung  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Hinweis:** 
> - Vollständiges Fine-Tuning erfordert mindestens **64 GB Arbeitsspeicher (RAM)**, wobei mindestens **32 GB davon für die GPU verfügbar sein müssen** (die 32 GB sind Teil der 64 GB, nicht zusätzlich dazu).
> - Sie können auch andere Modellarchitekturen ausprobieren, darunter **GPT-OSS-20B**, indem Sie das Modell in den bereitgestellten Trainingsskripten ersetzen.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Hinweis:** LoRA- und QLoRA-Fine-Tuning erfordern mindestens **32 GB Arbeitsspeicher (RAM)**, wobei mindestens **16 GB davon für die GPU verfügbar sein müssen** (die 16 GB sind Teil der 32 GB, nicht zusätzlich dazu).
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis:** LoRA-Fine-Tuning erfordert mindestens **32 GB Arbeitsspeicher (RAM)**, wobei mindestens **16 GB davon für die GPU verfügbar sein müssen** (die 16 GB sind Teil der 32 GB, nicht zusätzlich dazu).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Hinweis:** LoRA- und QLoRA-Fine-Tuning erfordern eine Grafikkarte mit mindestens **16 GB dediziertem GPU-Speicher** und **32 GB Arbeitsspeicher (RAM)**.
> - Unter Linux läuft das Training vollständig im dedizierten VRAM der Grafikkarte.
> - Es erfolgt kein Rückgriff auf gemeinsam genutzten GPU-Speicher (System-RAM), wenn der VRAM ausgeht.
> - Karten mit weniger als 16 GB dediziertem VRAM laufen während des Trainings unter Linux in einen Speichermangel, selbst wenn das System über ausreichend RAM verfügt.
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis:** LoRA-Fine-Tuning erfordert mindestens **16 GB Gesamt-GPU-Speicher** und **32 GB Arbeitsspeicher (RAM)**.
> - Unter Windows setzt sich der Gesamt-GPU-Speicher aus dem dedizierten VRAM der Grafikkarte und dem gemeinsam genutzten GPU-Speicher (aus dem System-RAM entliehen) zusammen.
> - Daher können Karten mit weniger als 16 GB dediziertem VRAM dieses Playbook dennoch ausführen, indem sie gemeinsam genutzten GPU-Speicher zum Ausgleich der Differenz nutzen.
<!-- @os:end -->
<!-- @device:end -->

## Was Sie lernen werden

- Wie Sie ein LLM mit LoRA, QLoRA und vollständigem Fine-Tuning mithilfe von PyTorch und ROCm fine-tunen
- Wie Sie Ihr fine-getuntes Modell speichern und bereitstellen
- Wie Sie das Training überwachen und häufige Probleme debuggen

## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen
> **Hinweis**: Wenn VS Code nicht installiert ist, können Sie es mit dem Ryzen AI Developer Center installieren.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation der Software-Voraussetzungen

#### Erstellen einer virtuellen Umgebung

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
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
**Gewähren Sie Ihrem Benutzer Zugriff auf GPU-Geräte** (melden Sie sich ab und wieder an, damit dies wirksam wird):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
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
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Installation grundlegender Abhängigkeiten
<!-- @require:pytorch -->

#### Zusätzliche Abhängigkeiten

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Hier werden nur Kernpakete getestet und unterstützt. **bitsandbytes wird unter Windows nicht gut unterstützt**, daher lässt die Windows-Installation dieses Paket aus; verwenden Sie unter Windows LoRA oder vollständiges Fine-Tuning (QLoRA erfordert bitsandbytes und ist für Linux vorgesehen).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF-Authentifizierung aktivieren (zugangsbeschränkte oder benutzerdefinierte / nicht vorinstallierte Modelle)

In diesem Beispiel verwenden wir **google/gemma-3-4b-it**, ein **zugangsbeschränktes** Modell. Sie müssen die Nutzungsbedingungen des Modells auf Hugging Face akzeptieren und sich anschließend authentifizieren, damit die Trainingsskripte es herunterladen können.

1. **Lizenz akzeptieren:** Öffnen Sie [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), melden Sie sich an (oder erstellen Sie ein Konto) und akzeptieren Sie die Lizenz/Nutzungsbedingungen auf der Modellseite (z. B. „Agree and access repository“).
2. **Installieren und anmelden:** Installieren Sie die Hugging Face CLI und führen Sie anschließend den Standard-Login aus:

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

## Die Techniken verstehen

### Was ist LoRA?

**LoRA (Low-Rank Adaptation)** hält das Basismodell eingefroren und trainiert nur kleine „Adapter“-Matrizen, die zu bestimmten Schichten hinzugefügt werden.

- **Die Kernidee**: Anstatt eine riesige Gewichtsmatrix mit Millionen von Parametern zu aktualisieren, lernen wir ein Low-Rank-Update (zwei kleine Matrizen, deren Produkt deutlich weniger Parameter hat). Das führt zu einer erheblichen Reduzierung der trainierbaren Parameter und des VRAM-Bedarfs, während der Großteil der Qualität eines vollständigen Fine-Tunings erhalten bleibt.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Was ist QLoRA?

**QLoRA** kombiniert **4-Bit-Quantisierung** mit **LoRA**. Das Basismodell wird in 4-Bit geladen (große Speicherersparnis), und nur die LoRA-Adapter werden mit höherer Präzision trainiert. So erhalten Sie die Parametereffizienz von LoRA sowie einen deutlich geringeren VRAM-Bedarf, bei einem geringen Qualitätskompromiss im Vergleich zu LoRA mit voller Präzision. Beachten Sie, dass die 4-Bit-Quantisierung numerische Instabilitäten (Loss-Spitzen oder NaNs) verursachen kann, weshalb Benutzer bei ausreichend verfügbarem VRAM oft **LoRA** bevorzugen.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Hinweis**: Für MXFP4-Basismodelle wie `openai/gpt-oss-20b` empfehlen wir die Verwendung von **LoRA** (`train_lora.py`) anstelle von QLoRA. Der 4-Bit-Pfad von `bitsandbytes` im QLoRA-Skript dequantisiert MXFP4-Gewichte typischerweise auf BF16, sodass der Lauf sich wie Standard-LoRA verhält. Natives MXFP4 erfordert eine aus dem Quellcode erstellte `bitsandbytes`-Version sowie einen passenden Transformers/Triton/Kernels-Stack. Siehe die [Transformers-MXFP4-Dokumentation](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Wählen Sie Ihre Methode

| Methode | Speicher | Geschwindigkeit | Qualität | Am besten geeignet für |
|--------|--------|-------|---------|----------|
| **QLoRA** (nur Linux) | 12-16GB | Am schnellsten | 90-95% | Geringen Speicherverbrauch |
| **LoRA** | 24-32GB | Schnell | 95-98% | Ausgewogenen Ansatz |
| **Full** | 80GB+ | Am langsamsten | 100% | Maximale Qualität |

### 3. Training ausführen

**Datensatz und was das Modell lernt**  
Die Skripte wandeln den Datensatz in Chat-Beispiele um. Das QLoRA-Skript verwendet beispielsweise **Abirate/english_quotes**: Jedes Beispiel wird zu einem User-Assistant-Paar wie:

- **User:** „Gib mir ein Zitat über: &lt;tag&gt;“
- **Assistant:** „&lt;quote&gt; – &lt;author&gt;“

Das Fine-Tuning bringt dem Modell bei, auf Prompts zu reagieren, die nach Zitaten zu einem Thema fragen, und diese im Format `<quote text> - <author>` zurückzugeben. Die LoRA- und Full-Fine-Tuning-Skripte verwenden **databricks/databricks-dolly-15k** (allgemeine Instruction/Response-Paare), sodass die genaue Aufgabe je nach Skript variiert; das Prinzip bleibt jedoch gleich – das Modell an Ihren gewählten Datensatz und Ihr Format anzupassen.

Nachfolgend finden Sie eine Übersicht der verfügbaren Trainingsmethoden. Jede Methode verlinkt auf das zugehörige Skript und enthält eine kurze Beschreibung zur Auswahl des passenden Ansatzes.

| Skript                           | Methode            | Beschreibung                                                                                                         | Typischer VRAM | Empfohlen für                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Trainiert kleine Adaptermatrizen, während das Basismodell eingefroren bleibt. 3–5x schneller; ~95–98% der vollen Qualität.                         | 24–32GB      | Fortgeschrittene Benutzer; mehrere Adapter; mehr VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(nur Linux)*             | **QLoRA**       | 4-Bit-Quantisierung + LoRA-Adapter. Geringster Speicherverbrauch, am schnellsten, geringer Qualitätsverlust. Erfordert `bitsandbytes` (nur Linux).                            | 12–16GB      | Die meisten Benutzer; schnelle Experimente; begrenzter VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Vollständiges Fine-Tuning** | Aktualisiert alle Modellparameter. Maximale Qualität; höchster Speicher- und Rechenaufwand.                                    | 40GB+        | Maximale Qualität; Forschung; großer VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Hinweis:** Vollständiges Fine-Tuning (`train_full_finetuning.py`) kann mehr als 64GB Arbeitsspeicher erfordern und ist auf diesem Gerät möglicherweise nicht durchführbar. Erwägen Sie stattdessen die Verwendung von LoRA oder QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis:** Vollständiges Fine-Tuning (`train_full_finetuning.py`) kann mehr als 64GB Arbeitsspeicher erfordern und ist auf diesem Gerät möglicherweise nicht durchführbar. Erwägen Sie stattdessen die Verwendung von LoRA.
<!-- @os:end -->
<!-- @device:end -->

Wählen Sie einfach Ihre bevorzugte `Training method`, laden Sie das entsprechende Skript herunter und führen Sie es mit dem Befehl aus, während Ihre virtuelle Umgebung aktiviert bleibt: 

```python
python3 train_<method_name>.py.
```

## Verwendung Ihres Fine-Tuned Modells

### Nach vollständigem Fine-Tuning

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

### Nach LoRA/QLoRA-Training

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### LoRA-Adapter in Basismodell zusammenführen

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Hinweis:**  
- Stellen Sie sicher, dass der Name des Modellverzeichnisses (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) mit dem tatsächlichen Ausgabeordner Ihres Trainings übereinstimmt.  
- Wenn Sie LoRA anstelle von QLoRA verwendet haben, ersetzen Sie den Pfad entsprechend.  
- Einige Gemma-Modelle erfordern die Angabe von `trust_remote_code=True` in `from_pretrained`; fügen Sie dies hinzu, wenn Sie eine entsprechende Warnung sehen.

Für weitere benutzerdefinierte Einstellungen (Padding-Tokens, Gerät usw.) beachten Sie das Skript, das Sie für das Training verwendet haben.

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
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Anpassungsleitfaden

### Eigenen Datensatz verwenden

Alle Skripte verwenden dasselbe Datensatzformat. Ersetzen Sie den Ladeabschnitt:

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

**Datensatzformat für lokale JSON/JSONL-Datei:**

Bei Verwendung dieser Methode stellen Sie bitte sicher, dass Ihre JSON-Dateien korrekt strukturiert sind, um Parsing-Fehler zu vermeiden. 

Die folgenden Richtlinien müssen eingehalten werden:
* **Dateiformatierung:** JSON-Dateien sollten in einer integrierten Entwicklungsumgebung (IDE) formatiert werden, um die korrekte Struktur und Syntax sicherzustellen.
* **Erforderliche Schlüssel:** Die benutzerdefinierte JSON-Datei muss die Schlüssel `instruction` und `response` enthalten. Diese Schlüssel sind für die korrekte Funktion der Methode unerlässlich.
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
**Datensatzformat für Hugging Face Hub-Datensatz**

Bei der Verwendung von Datensätzen von Hugging Face stellen Sie bitte sicher, dass Ihre Datensätze korrekt strukturiert sind, um eine reibungslose Integration zu ermöglichen. 

Die folgenden Richtlinien sollten befolgt werden:
* **Instruction-Response-Paar:** Konzentrieren Sie sich auf Datensätze, die ein `instruction-response`-Paar enthalten. Diese Struktur ist für die beabsichtigte Funktionalität unerlässlich.
* **Modifikation benutzerdefinierter Schlüssel:** Wenn Ihr Datensatz nicht der `instruction-response`-Struktur entspricht, haben Sie die Möglichkeit, die Funktion `format_instruction()` zu ändern. Dies ermöglicht es Ihnen, spezifische Schlüssel nach Bedarf zu berücksichtigen.

Beispielanpassung: Falls die Ausgabe des Datensatzes angepasst werden muss, können Sie den Antwortabschnitt innerhalb der Funktion format_instruction() ändern, um ihn an Ihre Anforderungen anzupassen.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Datensatzformat für CSV-Datei**

Um das Skript mit einem CSV-Dateiformat zu verwenden, müssen Sie sicherstellen, dass die CSV-Datei Spalten mit den Namen `instruction` und `response` enthält. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Trainingsparameter anpassen

Bearbeiten Sie das Trainingsskript und ändern Sie die Variablen entsprechend Ihren Zielen: **Lernrate** (`LR`), **Epochen** (`EPOCHS`), **Batch-Größe** (`BATCH_SIZE`), **Gradientenakkumulation** (`GRAD_ACCUM_STEPS`) und für LoRA/QLoRA den **Rang** (`LORA_R`). Für schnellere Durchläufe verwenden Sie weniger Epochen und eine höhere Lernrate (LR); für bessere Qualität verwenden Sie mehr Epochen und eine niedrigere LR. Reduzieren Sie die Batch-Größe oder die Sequenzlänge, wenn Speicherfehler (Out-of-Memory) auftreten.
### Tipps zur Speicheroptimierung

Wenn Speicherfehler (Out-of-Memory) auftreten:

**1. Batch-Größe reduzieren:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Sequenzlänge reduzieren:**
```python
max_seq_length=256  # Instead of 512
```

**3. Aggressivere Quantisierung verwenden:**
```
Full → LoRA → QLoRA
```

**4. Gradient Checkpointing aktivieren (nur bei vollständigem Fine-Tuning):**
```python
model.gradient_checkpointing_enable()
```

---

## Überwachung & Fehlerbehebung

### GPU-Speicher beobachten

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Optional) Experimente mit Weights & Biases verfolgen

Um Läufe und Metriken bei [Weights & Biases](https://wandb.ai) zu protokollieren:

```bash
pip install wandb
wandb login
```

Setzen Sie im Trainingsskript `report_to="wandb"` und optional `run_name="your-experiment-name"` in der Trainer-Konfiguration. Wenn Sie Wandb nicht verwenden möchten, belassen Sie `report_to` beim Standardwert oder setzen Sie es auf `"none"`.

### Häufige Probleme

#### Speichermangel (OOM)

**Lösung:** Batch-Größe reduzieren und/oder QLoRA verwenden
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Verlust sinkt nicht

**Lösung:** Lernrate anpassen
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Langsames Training

**Lösung:** Batch-Größe erhöhen, wenn genug Speicher vorhanden ist
```python
BATCH_SIZE = 8
```
## Nächste Schritte

Nachdem Sie das Fine-Tuning erfolgreich abgeschlossen haben, sollten Sie folgende nächste Schritte in Betracht ziehen, um mehr aus Ihrem Modell herauszuholen:

1. **Evaluieren** Sie gründlich anhand von zurückgehaltenen Testdaten, um die Generalisierung zu messen und Overfitting zu vermeiden.
2. **Experimentieren** Sie mit verschiedenen Hyperparameterwerten für bessere Kompromisse zwischen Genauigkeit, Geschwindigkeit und Speicherverbrauch.
3. **Verfolgen** Sie alle Ihre Experimente (und die zugehörigen Metriken) mit Weights & Biases für reproduzierbare Forschung.
4. **Versuchen** Sie das Training mit Ihren eigenen benutzerdefinierten Datensätzen, um das Modell speziell an Ihren Anwendungsfall anzupassen.
5. **Stellen** Sie Ihr fein abgestimmtes Modell für schnelle Inferenz mit effizienten Backends wie vLLM auf kompatibler Hardware bereit.
6. **Erkunden** Sie fortgeschrittene Techniken wie Prompt Engineering, gemischte Präzision und längere Sequenzlängen.
7. **Trainieren** Sie mehrere LoRA-Adapter für verschiedene Aufgaben oder Domänen und tauschen Sie diese bei Bedarf aus.

---