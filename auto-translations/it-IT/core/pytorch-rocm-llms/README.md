<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Panoramica


Vuoi eseguire potenti modelli linguistici AI sul tuo hardware? Questa guida ti mostra come fare.
Questo tutorial utilizza PyTorch basato su software AMD ROCm™ per eseguire modelli in grado di riassumere documenti, rispondere a domande, generare testo e molto altro, il tutto in locale.

## Cosa Imparerai

- Eseguire LLM come gpt-oss-20b e qwen3.5-4B in locale utilizzando PyTorch e ROCm
- Creare uno strumento di riassunto documenti utilizzando gli LLM

## Impostazione della Configurazione della Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli Aggiornamenti Software
> **Nota**: Se VS Code non è installato, puoi installarlo con Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei Prerequisiti Software

### Creare un Ambiente Virtuale

<!-- @os:linux -->
<!-- @device:halo_box -->
Su Linux, apri un terminale nella directory a tua scelta e segui i comandi per creare un venv con ROCm+Pytorch già installati.
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
**Concedi al tuo utente l'accesso ai dispositivi GPU** (esci e rientra nell'account affinché la modifica abbia effetto):

```bash
sudo usermod -aG render,video $LOGNAME
```

Su Linux, apri un terminale nella directory a tua scelta e segui i comandi per creare un venv.
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
Su Windows, apri un terminale nella directory a tua scelta e segui i comandi per creare un venv con ROCm+Pytorch già installati.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Su Windows, apri un terminale nella directory a tua scelta e segui i comandi per creare un venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Suggerimento**: Gli utenti Windows potrebbero dover modificare la loro Execution Policy di PowerShell (ad esempio,
> impostandola su RemoteSigned o Unrestricted) prima di eseguire alcuni comandi Powershell.

<!-- @os:end -->

### Installazione delle Dipendenze di Base
<!-- @require:driver,pytorch -->

### Installazione delle Dipendenze Aggiuntive

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

## Avvio Rapido con Script di Esempio

Questo playbook include script pronti all'uso. Fai clic su di essi per visualizzarne l'anteprima e scaricarli nella stessa directory dell'ambiente che hai creato.

| Script | Descrizione | Utilizzo |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Generazione di testo LLM di base | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Riassunto documenti con supporto Harmony | `python summarizer.py --file document.txt` |

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

Entrambi gli script supportano:
- Selezione del modello tramite il flag `--model`
- Formattazione del template di chat per una corretta creazione dei prompt del modello, particolarmente utile per il riassunto di documenti

## Caricamento ed Esecuzione del Tuo Primo LLM

Lo script incluso [run_llm.py](assets/run_llm.py) mostra come generare testo con gli LLM utilizzando PyTorch e AMD ROCm.

> **Nota:** Quando carichi un modello, Hugging Face Transformers controlla prima la sua cache locale (`~/.cache/huggingface/hub` su Linux, `C:\Users\<user>\.cache\huggingface\hub` su Windows). Se il modello non è memorizzato nella cache, viene scaricato automaticamente da huggingface.co. La prima esecuzione potrebbe richiedere alcuni minuti a seconda delle dimensioni del modello e della velocità della rete.

Il seguente frammento mostra come utilizzare il modello e personalizzare le domande poste.

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

Prova lo script scaricato:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Creazione di uno Strumento di Riassunto Documenti

Ora che hai generato un output LLM in locale, puoi sviluppare ulteriormente questo risultato creando uno strumento pratico di riassunto documenti. In questa sezione, utilizzerai lo script [summarizer.py](assets/summarizer.py) per fornire un file .txt e generare automaticamente un riassunto conciso, il tutto eseguito in locale sulla tua GPU.

Lo script è progettato per funzionare immediatamente. Apri lo script in un editor per esplorare il codice, personalizzare i prompt e regolare parametri come la lunghezza e la temperatura.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Esempi di Utilizzo

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

## Informazioni sui Parametri di Generazione

| Parametro | Cosa Controlla | Valori Tipici |
|-----------|------------------|----------------|
| `max_new_tokens` | La lunghezza massima dell'output dell'LLM | Utilizza 50–500 token per i riassunti. (1 token corrisponde a circa 0,75 parole inglesi) |
| `temperature` | Creatività. Valori bassi lo rendono focalizzato, mentre valori alti comportano maggiore imprevedibilità | - **0.1–0.3**: Focalizzato, deterministico (adatto per i riassunti) <br> **0.5–0.7**: Bilanciato (uso generale) <br> **0.8–1.0**: Creativo, vario (brainstorming) |
| `top_p` | Nucleus Sampling - Valori bassi limitano il modello a output più ristretti | **0.1-0.5**: Rigoroso, prevedibile <br> **0.9-0.95**: (standard, naturale, colloquiale) |


## Applicazioni nel Mondo Reale

- **Analisi di Documenti di Ricerca**: Estrai i risultati chiave da pubblicazioni complesse per una revisione rapida
- **Aggregazione di Notizie**: Riassumi articoli di notizie in brevi digest giornalieri o punti salienti
- **Note di Riunioni**: Condensa le trascrizioni in elementi d'azione e riassunti concisi
- **Revisione di Documenti Legali**: Estrai rapidamente clausole o obblighi rilevanti da lunghi testi legali
- **Documentazione del Codice**: Genera panoramiche concise dei repository e spiegazioni delle funzioni

## Prossimi Passi

- **Fine-tuning**: Adatta i modelli al tuo settore specifico o al tuo gergo per una maggiore precisione (vedi i Playbook di Fine-tuning)
- **Sistemi RAG**: Combina gli LLM con il recupero di documenti per risposte e ricerche contestuali
- **Esplorazione dei Modelli**: Sperimenta con nuovi modelli come Llama 3, Phi-3 o Qwen per risultati migliori
- **Distribuzione in Produzione**: Utilizza strumenti come vLLM per la fornitura scalabile di LLM nelle organizzazioni

Il tuo sistema ti offre la possibilità di eseguire sofisticati modelli linguistici in locale. Sperimenta con diversi modelli, prompt e parametri per scoprire cosa funziona meglio per le tue applicazioni.