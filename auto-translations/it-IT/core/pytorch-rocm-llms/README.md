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


Vuoi eseguire potenti modelli linguistici IA sul tuo hardware personale? Questa guida ti mostra come fare.
Questo tutorial utilizza PyTorch potenziato dal software AMD ROCm™ per eseguire modelli in grado di riassumere documenti, rispondere a domande, generare testo e molto altro, tutto in locale.

## Cosa imparerai

- Eseguire LLM come gpt-oss-20b e qwen3.5-4B in locale utilizzando PyTorch e ROCm
- Creare uno strumento di riepilogo dei documenti utilizzando gli LLM

<!-- @device:halo_box,halo,stx,krk -->
## Configurazione della memoria

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verifica degli aggiornamenti software
> **Nota**: se VS Code non è installato, puoi installarlo con Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei prerequisiti software

### Creare un ambiente virtuale

<!-- @os:linux -->
<!-- @device:halo_box -->
Su Linux, apri un terminale nella directory di tua scelta e segui i comandi per creare un venv con ROCm+PyTorch già installati.
<!-- @test:id=create-venv timeout=300 -->
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
**Concedi al tuo utente l'accesso ai dispositivi GPU** (esci e rientra nella sessione affinché la modifica abbia effetto):

```bash
sudo usermod -aG render,video $LOGNAME
```

Su Linux, apri un terminale nella directory di tua scelta e segui i comandi per creare un venv.
<!-- @test:id=create-venv timeout=300 -->
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
Su Windows, apri un terminale nella directory di tua scelta e segui i comandi per creare un venv con ROCm+PyTorch già installati.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Su Windows, apri un terminale nella directory di tua scelta e segui i comandi per creare un venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Suggerimento**: gli utenti Windows potrebbero dover modificare la propria Execution Policy di PowerShell (ad esempio
> impostandola su RemoteSigned o Unrestricted) prima di eseguire alcuni comandi PowerShell.

<!-- @os:end -->

### Installazione delle dipendenze di base
<!-- @require:driver,pytorch -->

### Installazione delle dipendenze aggiuntive

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
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
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

> **Nota:** se il modello non riesce a caricarsi o la memoria si esaurisce, prova a installare il pacchetto `kernels` per caricare il modello con quantizzazione ottimizzata.
>
> ```bash
> # Use this version which is compatible with the Transformers version
> pip install "kernels==0.14.1" 
> ```
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
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Avvio rapido con script di esempio

Questo playbook include script pronti all'uso. Fai clic su di essi per visualizzarne l'anteprima e scaricarli nella stessa directory dell'ambiente che hai creato.

| Script | Descrizione | Utilizzo |
|--------|-------------|----------|
| [run_llm.py](assets/run_llm.py) | Generazione di testo LLM di base | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Strumento di riepilogo documenti con supporto Harmony | `python summarizer.py --file document.txt` |

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
- Formattazione del template di chat per una corretta impostazione dei prompt del modello, particolarmente utile per il riepilogo di documenti

## Caricamento ed esecuzione del tuo primo LLM

Lo script incluso [run_llm.py](assets/run_llm.py) mostra come generare testo con gli LLM utilizzando PyTorch e AMD ROCm.

> **Nota:** quando carichi un modello, Hugging Face Transformers controlla prima la sua cache locale (`~/.cache/huggingface/hub` su Linux, `C:\Users\<user>\.cache\huggingface\hub` su Windows). Se il modello non è presente in cache, viene scaricato automaticamente da huggingface.co. La prima esecuzione può richiedere alcuni minuti a seconda della dimensione del modello e della velocità di rete.

Il frammento di codice qui sotto mostra come utilizzare il modello e personalizzare le domande poste.

<!-- @test:id=verify-imports timeout=300 hidden=True setup=activate-venv -->
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
    device_map="auto",
    disable_mmap=True
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


## Creazione di uno strumento di riepilogo dei documenti

Ora che hai generato un output con l'LLM in locale, puoi proseguire creando uno strumento pratico di riepilogo dei documenti. In questa sezione, utilizzerai lo script [summarizer.py](assets/summarizer.py) per inserire un file .txt e generare automaticamente un riepilogo conciso, il tutto eseguito localmente sulla tua GPU.

Lo script è progettato per funzionare subito, senza configurazioni aggiuntive. Apri lo script in un editor per esplorare il codice, personalizzare i prompt e regolare parametri come lunghezza e temperatura.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Esempi di utilizzo

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

## Informazioni sui parametri di generazione

| Parametro | Cosa controlla | Valori tipici |
|-----------|-----------------|----------------|
| `max_new_tokens` | La lunghezza massima dell'output dell'LLM | Usa 50–500 token per i riepiloghi. (1 token corrisponde a circa 0,75 parole in inglese) |
| `temperature` | Creatività. Valori bassi lo rendono più focalizzato, valori alti comportano maggiore imprevedibilità | - **0,1–0,3**: focalizzato, deterministico (adatto ai riepiloghi) <br> **0,5–0,7**: bilanciato (uso generale) <br> **0,8–1,0**: creativo, vario (brainstorming) |
| `top_p` | Nucleus Sampling - Valori bassi limitano il modello a output più ristretti | **0,1-0,5**: rigido, prevedibile <br> **0,9-0,95**: (standard, naturale, colloquiale) |


## Applicazioni nel mondo reale

- **Analisi di articoli di ricerca**: estrarre i risultati chiave da pubblicazioni complesse per una rapida consultazione
- **Aggregazione di notizie**: riassumere articoli di notizie in brevi digest giornalieri o punti salienti
- **Note di riunione**: condensare le trascrizioni in elementi d'azione e riepiloghi concisi
- **Revisione di documenti legali**: estrarre rapidamente clausole o obblighi rilevanti da lunghi testi legali
- **Documentazione del codice**: generare panoramiche concise dei repository e spiegazioni delle funzioni
## Prossimi Passi

- **Fine-tuning**: Adatta i modelli al tuo campo specifico o al tuo gergo per una maggiore precisione (vedi Fine-tuning Playbooks)
- **Sistemi RAG**: Combina gli LLM con il recupero di documenti per risposte e ricerche context-aware
- **Esplorazione dei modelli**: Sperimenta con nuovi modelli come Llama 3, Phi-3 o Qwen per ottenere risultati migliori
- **Distribuzione in produzione**: Usa strumenti come vLLM per il serving scalabile di LLM nelle organizzazioni

Il tuo sistema ti offre la possibilità di eseguire modelli linguistici sofisticati in locale. Sperimenta con modelli, prompt e parametri diversi per scoprire cosa funziona meglio per le tue applicazioni.