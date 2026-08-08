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

## Überblick

Dieses Playbook zeigt, wie man ein Sprachmodell lokal mit Unsloth auf AMD-Hardware feinabstimmt.

Es verwendet ein kurzes Supervised-Fine-Tuning-Beispiel (SFT) mit LoRA-Adaptern für `unsloth/gemma-4-E4B-it`, unter Verwendung einer Teilmenge des `mlabonne/FineTome-100k`-Datensatzes. Ziel ist es, Ihnen einen einfachen End-to-End-Workflow an die Hand zu geben, der Einrichtung, Training, Inferenz und das Speichern des feinabgestimmten Ergebnisses abdeckt.

Das Beispiel ist praxisnah und leicht anpassbar gestaltet, sodass Sie es als Ausgangspunkt für Ihre eigenen Datensätze und Modelle verwenden können.

## Was Sie lernen werden

- Wie Sie die Unsloth-Umgebung einrichten
- Wie Sie ein LLM mit SFT und Unsloth feinabstimmen
- Wie Sie das feinabgestimmte Ergebnis lokal speichern

<!-- @device:halo,stx,krk -->
> **Hinweis:** Die Fine-Tuning-Techniken in diesem Playbook erfordern mindestens **64 GB Systemarbeitsspeicher**, wovon mindestens **24 GB für die GPU verfügbar** sein müssen (die 24 GB sind Teil der 64 GB, nicht zusätzlich dazu).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Hinweis:** Die Fine-Tuning-Techniken in diesem Playbook erfordern mindestens **24 GB Gesamt-GPU-Speicher** und **32 GB Systemarbeitsspeicher**.
> - Unter Windows setzt sich der Gesamt-GPU-Speicher aus dem dedizierten VRAM der Grafikkarte und dem gemeinsam genutzten GPU-Speicher (aus dem Systemarbeitsspeicher entliehen) zusammen.
> - Daher können auch Karten mit weniger als 24 GB dediziertem VRAM dieses Playbook ausführen, indem sie den Unterschied über gemeinsam genutzten GPU-Speicher ausgleichen.
<!-- @os:end -->

<!-- @os:linux -->
> **Hinweis:** Die Fine-Tuning-Techniken in diesem Playbook erfordern eine Grafikkarte mit mindestens **24 GB dediziertem GPU-Speicher** und **32 GB Systemarbeitsspeicher**.
> - Unter Linux läuft das Training vollständig im dedizierten VRAM der Grafikkarte.
> - Es erfolgt kein Rückgriff auf gemeinsam genutzten GPU-Speicher (Systemarbeitsspeicher), wenn der VRAM erschöpft ist.
> - Karten mit weniger als 24 GB dediziertem VRAM werden während des Trainings unter Linux nicht genügend Speicher haben, selbst wenn das System über ausreichend RAM verfügt.
<!-- @os:end -->
<!-- @device:end -->

## Warum Unsloth?

Unsloth erleichtert das Ausführen von LLM-Fine-Tuning auf lokaler Hardware, indem es im Vergleich zu einem Standard-Setup den Speicherverbrauch reduziert und das Training beschleunigt.

In diesem Playbook verwenden wir Unsloth zusammen mit **LoRA-basiertem SFT**. Das bedeutet, dass das Basismodell größtenteils eingefroren bleibt, während ein deutlich kleinerer Satz von Adaptergewichten trainiert wird. Dies eignet sich gut für die lokale Entwicklung, da es leichter als vollständiges Fine-Tuning ist und schnellere Iterationen ermöglicht.

Unsloth unterstützt außerdem weitere Trainingsansätze, einschließlich QLoRA und Reinforcement-Learning-Workflows. Dieses Playbook konzentriert sich zunächst auf den einfachsten Weg: ein kleines LoRA-Fine-Tuning-Beispiel, das Nutzer ausführen, verstehen und erweitern können.

## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Softwareupdates suchen
> **Hinweis**: Falls VS Code nicht installiert ist, können Sie es mit dem Ryzen AI Developer Center installieren.

<!-- @require:software-update -->
<!-- @device:end -->

## Installieren der Softwarevoraussetzungen

### Erstellen einer virtuellen Umgebung

<!-- @os:linux -->
<!-- @device:halo_box -->
Öffnen Sie ein Terminal und erstellen Sie eine venv mit bereits installierter AMD ROCm™-Software und PyTorch:
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
**Gewähren Sie Ihrem Benutzer Zugriff auf GPU-Geräte** (melden Sie sich ab und wieder an, damit dies wirksam wird):

```bash
sudo usermod -aG render,video $LOGNAME
```

Öffnen Sie ein Terminal und erstellen Sie eine venv:
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
> **Hinweis:** Für Windows ist Python 3.13 erforderlich.

<!-- @device:halo_box -->
Öffnen Sie ein PowerShell-Terminal und erstellen Sie eine virtuelle Umgebung:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Öffnen Sie ein PowerShell-Terminal und erstellen Sie eine virtuelle Umgebung:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Installieren grundlegender Abhängigkeiten
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

### Zusätzliche Abhängigkeiten

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Hinweis:** Beim Import kann Unsloth optionale `bitsandbytes`-Beschleunigungspfade prüfen. Bei manchen ROCm-Versionen kann eine Meldung wie `bitsandbytes library load error: Configured ROCm binary not found` erscheinen. Dieses Playbook verwendet standardmäßiges LoRA-Fine-Tuning mit `optim="adamw_torch"`, sodass wir nicht auf den `bitsandbytes`-Optimizer oder 4-Bit-QLoRA angewiesen sind. Diese Meldung kann ohne Bedenken ignoriert werden.

<!-- @os:windows -->
> **Hinweis:** Unter Windows ROCm gibt Unsloth beim Start mehrere Warnungen aus — siehe [Bekannte Warnungen](#known-warnings) unten. Diese können alle gefahrlos ignoriert werden; das Training funktioniert korrekt.
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

## Herunterladen des Unsloth-Fine-Tuning-Skripts

Anstatt jeden Schritt manuell auszuführen, stellt dieses Playbook ein sauberes End-to-End-Skript hier bereit: [test_unsloth.py](assets/test_unsloth.py).

Führen Sie den folgenden Code aus, um das Skript auszuführen:

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

Der Rest des Playbooks geht konzeptionell jeden wichtigen Schritt des Skripts durch. 

## Funktionsweise

Das Skript test_unsloth.py führt die folgenden Schritte aus:
* **Modell laden**: Lädt unsloth/gemma-4-E4B-it mittels FastModel.
* **Daten vorbereiten**: Standardisiert den Datensatz (z. B. FineTome-100k) und wendet die Gemma-4-Chat-Vorlage an.
* **LoRA anwenden**: Fügt Adapter zu Sprach-, Attention- und MLP-Modulen für effizientes Training hinzu.
* **Trainieren**: Verwendet SFTTrainer mit Response-Only-Loss-Maskierung.
* **Inferenz**: Führt einen kurzen Generierungstest durch, um die Leistung zu überprüfen.
* **Speichern**: Exportiert LoRA-Adapter lokal.

## Wichtige Konfiguration

Sie können die folgenden Konstanten anpassen, um Ihren Durchlauf zu individualisieren:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Beispiel für die Unsloth-Willkommensnachricht und Ausgabe beim Laden der Modellgewichte:

![alt text](assets/welcome.png)

## Datensatz vorbereiten

Wir verwenden eine Teilmenge von:
```text
mlabonne/FineTome-100k
```
Der Datensatz wird:
* In das Chatformat umgewandelt
* Mit der Gemma-4-Chat-Vorlage verarbeitet
* Bereinigt, um doppelte BOS-Tokens zu entfernen

## Trainieren des Modells

Das Skript führt eine kurze Trainingsdemo mit den folgenden Parametern aus:
- ~50 Schritte
- Kleine Batchgröße
- Gradientenakkumulation

Während des Trainings sehen Sie Protokolle wie:

![alt text](assets/training.png)


## Speichern und Bereitstellung
### Lokales Speichern (LoRA)

Das Skript speichert LoRA-Adapter automatisch im OUTPUT_DIR.
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

### Zusammengeführtes Modell speichern (für vLLM) 

<!-- @os:windows -->
> **Hinweis:** vLLM unterstützt Windows nicht. Um Ihr feinabgestimmtes Modell unter Windows bereitzustellen, verwenden Sie llama.cpp (siehe [Export GGUF](#export-gguf-for-llamacpp) unten) oder übertragen Sie das zusammengeführte Modell auf einen Linux-Rechner, auf dem vLLM läuft.
<!-- @os:end -->

<!-- @os:linux -->
Für die Bereitstellung mit vLLM führen Sie die Adapter zu einem vollständigen Modell zusammen:
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

### GGUF exportieren (für llama.cpp)

Direkt in GGUF für lokale Inferenz konvertieren:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Bekannte Warnungen

Diese Warnungen werden von Unsloth beim Start unter Windows ROCm ausgegeben und können alle ignoriert werden:

| Warnung | Grund | Kann ignoriert werden? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes hat keinen Windows-ROCm-Build | Ja — dieses Playbook verwendet `adamw_torch`, nicht bnb |
| `No ROCm platform found for torch.distributed` | ROCm unter Windows unterstützt kein verteiltes Training | Ja — Einzel-GPU-Training ist davon nicht betroffen |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth markiert Nicht-Linux-Builds | Ja — Windows ROCm funktioniert für Einzel-GPU-SFT |
| `triton is not available` | Triton hat keinen Windows-Build | Ja — Unsloth greift auf PyTorch-Kernels zurück |

Das Training läuft trotz dieser Warnungen korrekt weiter.
<!-- @os:end -->

## Nächste Schritte
- Probieren Sie [Unsloth Studio](https://unsloth.ai/docs/new/studio) aus, eine intuitive GUI für Unsloth
- Trainieren Sie mit Ihren eigenen spezifischen Datensätzen
- Probieren Sie das Finetuning mit verschiedenen Hyperparametern aus
- Stellen Sie mit vLLM oder llama.cpp bereit
- Probieren Sie QLoRA für ein speichersparenderes Setup aus

## Ressourcen

Im Folgenden finden Sie einige zusätzliche Ressourcen, um mehr über Unsloth und Finetuning zu erfahren:

* [Unsloth-Dokumentation](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth-Finetuning-Leitfaden](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)