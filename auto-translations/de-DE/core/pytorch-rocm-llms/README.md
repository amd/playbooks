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


Möchten Sie leistungsstarke KI-Sprachmodelle auf Ihrer eigenen Hardware ausführen? Dieser Leitfaden zeigt Ihnen, wie es geht.
Dieses Tutorial verwendet PyTorch, angetrieben von AMD ROCm™ Software, um Modelle auszuführen, die Dokumente zusammenfassen, Fragen beantworten, Text generieren und mehr, alles lokal ausgeführt.

## Was Sie lernen werden

- Führen Sie LLMs wie gpt-oss-20b und qwen3.5-4B lokal mit PyTorch und ROCm aus
- Erstellen Sie ein Tool zur Dokumentenzusammenfassung mit LLMs

## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Softwareaktualisierungen suchen
> **Hinweis**: Wenn VS Code nicht installiert ist, können Sie es mit dem Ryzen AI Developer Center installieren.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation der Software-Voraussetzungen

### Erstellen einer virtuellen Umgebung

<!-- @os:linux -->
<!-- @device:halo_box -->
Öffnen Sie unter Linux ein Terminal in einem Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv mit bereits installiertem ROCm+Pytorch zu erstellen.
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
**Gewähren Sie Ihrem Benutzer Zugriff auf GPU-Geräte** (melden Sie sich ab und wieder an, damit dies wirksam wird):

```bash
sudo usermod -aG render,video $LOGNAME
```

Öffnen Sie unter Linux ein Terminal in einem Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen.
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
Öffnen Sie unter Windows ein Terminal in einem Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv mit bereits installiertem ROCm+Pytorch zu erstellen.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Öffnen Sie unter Windows ein Terminal in einem Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tipp**: Windows-Benutzer müssen möglicherweise ihre PowerShell-Ausführungsrichtlinie ändern (z. B.
> auf RemoteSigned oder Unrestricted setzen), bevor sie einige PowerShell-Befehle ausführen können.

<!-- @os:end -->

### Installation grundlegender Abhängigkeiten
<!-- @require:driver,pytorch -->

### Installation zusätzlicher Abhängigkeiten

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

## Schnellstart mit Beispielskripten

Dieses Playbook enthält einsatzbereite Skripte. Klicken Sie darauf, um sie in der Vorschau anzuzeigen und in das gleiche Verzeichnis wie die von Ihnen erstellte Umgebung herunterzuladen.

| Skript | Beschreibung | Verwendung |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Grundlegende LLM-Textgenerierung | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Dokumentenzusammenfasser mit Harmony-Unterstützung | `python summarizer.py --file document.txt` |

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

Beide Skripte unterstützen:
- Modellauswahl über das `--model`-Flag
- Chat-Vorlagenformatierung für korrektes Modell-Prompting, besonders nützlich für die Dokumentenzusammenfassung

## Laden und Ausführen Ihres ersten LLM

Das enthaltene Skript [run_llm.py](assets/run_llm.py) zeigt, wie man mit PyTorch und AMD ROCm Text generiert.

> **Hinweis:** Wenn Sie ein Modell laden, überprüft Hugging Face Transformers zunächst den lokalen Cache (`~/.cache/huggingface/hub` unter Linux, `C:\Users\<user>\.cache\huggingface\hub` unter Windows). Wenn das Modell nicht im Cache ist, wird es automatisch von huggingface.co heruntergeladen. Der erste Durchlauf kann je nach Modellgröße und Netzwerkgeschwindigkeit einige Minuten dauern.

Der folgende Ausschnitt zeigt, wie das Modell verwendet und die gestellten Fragen angepasst werden.

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

Probieren Sie das heruntergeladene Skript aus:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Erstellen eines Dokumentenzusammenfassers

Nachdem Sie nun lokale LLM-Ausgaben generiert haben, können Sie darauf aufbauen und einen praktischen Dokumentenzusammenfasser erstellen. In diesem Abschnitt verwenden Sie das Skript [summarizer.py](assets/summarizer.py), um eine .txt-Datei einzuspeisen und automatisch eine prägnante Zusammenfassung zu generieren, alles lokal auf Ihrer GPU ausgeführt.

Das Skript ist so konzipiert, dass es sofort einsatzbereit ist. Öffnen Sie das Skript in einem Editor, um den Code zu erkunden, Prompts anzupassen und Parameter wie Länge und Temperatur zu optimieren.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Anwendungsbeispiele

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

## Generierungsparameter kennenlernen

| Parameter | Was er steuert | Typische Werte |
|-----------|------------------|----------------|
| `max_new_tokens` | Die maximale Länge der LLM-Ausgabe | Verwenden Sie 50–500 Tokens für Zusammenfassungen. (1 Token entspricht etwa 0,75 englischen Wörtern) |
| `temperature` | Kreativität. Niedrige Werte machen die Ausgabe fokussiert, hohe Werte bringen mehr Unvorhersehbarkeit | - **0,1–0,3**: Fokussiert, deterministisch (gut für Zusammenfassungen) <br> **0,5–0,7**: Ausgewogen (allgemeine Verwendung) <br> **0,8–1,0**: Kreativ, vielfältig (Brainstorming) |
| `top_p` | Nucleus Sampling – Niedrige Werte beschränken das Modell auf engere Ausgaben | **0,1-0,5**: Streng, vorhersehbar <br> **0,9-0,95**: (standardmäßig, natürlich, gesprächig) |


## Praxisanwendungen

- **Analyse wissenschaftlicher Arbeiten**: Extrahieren Sie wichtige Erkenntnisse aus komplexen Publikationen zur schnellen Durchsicht
- **Nachrichtenaggregation**: Fassen Sie Nachrichtenartikel in kurze tägliche Übersichten oder Highlights zusammen
- **Besprechungsnotizen**: Verdichten Sie Transkripte zu umsetzbaren Punkten und prägnanten Zusammenfassungen
- **Prüfung juristischer Dokumente**: Extrahieren Sie relevante Klauseln oder Verpflichtungen schnell aus langen Rechtstexten
- **Code-Dokumentation**: Erstellen Sie prägnante Repository-Übersichten und Funktionserklärungen

## Nächste Schritte

- **Fine-Tuning**: Passen Sie Modelle an Ihr spezifisches Fachgebiet oder Ihren Fachjargon an, um die Genauigkeit zu verbessern (siehe Fine-Tuning-Playbooks)
- **RAG-Systeme**: Kombinieren Sie LLMs mit Dokumentenabruf für kontextbewusste Antworten und Suche
- **Modellerkundung**: Experimentieren Sie mit neuen Modellen wie Llama 3, Phi-3 oder Qwen für bessere Ergebnisse
- **Produktionsbereitstellung**: Verwenden Sie Tools wie vLLM für skalierbare LLM-Bereitstellung in Organisationen

Ihr System gibt Ihnen die Möglichkeit, anspruchsvolle Sprachmodelle lokal auszuführen. Experimentieren Sie mit verschiedenen Modellen, Prompts und Parametern, um herauszufinden, was für Ihre Anwendungen am besten funktioniert.