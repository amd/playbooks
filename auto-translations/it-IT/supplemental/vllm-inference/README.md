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

vLLM è un motore di inferenza ad alte prestazioni progettato per modelli linguistici di grandi dimensioni (LLM). Offre un servizio ottimizzato con batching continuo per un throughput elevato e un'API compatibile con OpenAI per un'integrazione applicativa senza interruzioni. Questo rende vLLM ideale per le distribuzioni in produzione in cui velocità ed efficienza delle risorse sono fondamentali.

Questa guida ti insegna come servire LLM utilizzando vLLM containerizzato sulla GPU integrata e interagire con i modelli tramite l'API Python di OpenAI.

## Cosa imparerai

- Come configurare e avviare un server vLLM con supporto AMD ROCm™
- Come interagire con i modelli tramite endpoint API compatibili con OpenAI
- Come inviare prompt al server locale con `vllm-prompt`

## Configurazione della memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli aggiornamenti software

> **Nota**: se VS Code non è installato, puoi installarlo con AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei prerequisiti software

vLLM viene eseguito in un container precompilato con ROCm e le relative dipendenze già configurate. Non è richiesta alcuna installazione aggiuntiva.

Non è previsto alcun passaggio di installazione di vLLM lato host. Avvia vLLM con:

```bash
vllm-launch
```

Il launcher avvia il container, punta alla GPU integrata ed espone un server vLLM locale compatibile con OpenAI. In alternativa, fai clic sull'icona di vLLM nella barra delle applicazioni.

## Avvio rapido

### 1. Verifica che il server vLLM sia in esecuzione

`vllm-launch` potrebbe impiegare un paio di minuti per inizializzare tutto. Una volta avviato, il server è disponibile all'indirizzo `http://localhost:8001`. Mantieni aperto il terminale di avvio poiché il server viene eseguito in primo piano, quindi apri un terminale separato per i passaggi rimanenti. Gli esempi riportati di seguito utilizzano `Qwen/Qwen3-1.7B`; se il tuo launcher è configurato per un modello diverso, sostituisci quell'ID modello nelle richieste.

### 2. Invia un prompt

Utilizza lo script `vllm-prompt` fornito per inviare una richiesta al server locale vLLM compatibile con OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chatta con il modello utilizzando l'API Python di OpenAI

Poiché vLLM espone un'API compatibile con OpenAI, puoi utilizzare il pacchetto Python `openai` per interagire con essa.

Innanzitutto, crea un ambiente virtuale Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->

Installa il pacchetto OpenAI
```bash
pip install openai
```

Crea un client `OpenAI` puntato al server vLLM locale anziché ai server di OpenAI. L'`api_key` è richiesta dal client, ma vLLM non la convalida, quindi qualsiasi stringa funziona:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Quindi, invia una richiesta di completamento chat. Questa utilizza lo stesso formato di messaggio dell'API OpenAI — un elenco di messaggi con ruoli come `"user"` e `"assistant"`. Impostando `stream=True` la risposta arriverà in modo incrementale anziché tutta in una volta:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

Infine, itera sui blocchi trasmessi in streaming e stampa ogni porzione di testo man mano che arriva:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Lo script [chat_with_model.py](assets/chat_with_model.py) incluso contiene l'intero esempio e può essere scaricato.


## Scelta e configurazione di un modello

Per impostazione predefinita, `vllm-launch` serve `Qwen/Qwen3-1.7B` come modello di test sulla porta `8001`. Puoi cambiare il modello, la porta e i parametri di servizio di vLLM senza ricompilare o modificare il container.

### Modelli testati da AMD

I seguenti modelli sono preconfigurati e convalidati da AMD:

| Modello | Note |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Modello predefinito. Leggero e veloce da caricare. |
| `openai/gpt-oss-20b` | Modello più grande per risposte di qualità superiore. |

### Avvio di un modello diverso

Passa l'ID del modello con `--model` (o `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Modifica della porta

Passa una porta superiore a 1024 con `--port` (o `-p`); l'impostazione predefinita è `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Se cambi la porta, imposta `base_url` del tuo client sulla stessa porta (ad esempio `http://localhost:8080/v1`).

### Passaggio di parametri vLLM aggiuntivi

Eventuali argomenti aggiuntivi vengono inoltrati direttamente a vLLM, quindi puoi ottimizzare il comportamento del servizio come la lunghezza del contesto o il tipo di dati. Esistono due modi per fornirli.

**In linea**, dopo le opzioni del launcher:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**In modo persistente**, in un file di configurazione in `~/.local/share/vLLM/vllm-launch.conf`. Questo file non esiste per impostazione predefinita: creane uno e aggiungi i tuoi argomenti come array Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Utilizza `+=` per aggiungere agli argomenti predefiniti anziché sostituirli:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Per visualizzare tutte le opzioni del launcher in qualsiasi momento, esegui:

```bash
vllm-launch --help
```

### Dove vengono archiviati i modelli

`vllm-launch` cerca i modelli in due posizioni:

| Posizione | Percorso |
|----------|------|
| Modelli di sistema | `/var/cache/models` |
| Modelli utente | `~/.local/share/vLLM/models` |

Puoi posizionare un modello scaricato in una delle due directory e avviarlo passando il suo percorso o ID a `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Nota**: l'esecuzione di un modello scaricato personalmente in questo modo dovrebbe funzionare una volta che il modello è stato posizionato in una delle directory sopra indicate, ma questo flusso di lavoro non è ancora stato ufficialmente convalidato da AMD.

## Risoluzione dei problemi

### Connessione rifiutata

Assicurati che il server sia in esecuzione:
```bash
curl http://localhost:8001/health
```

## Riepilogo

In questa guida, hai imparato a:

- Avviare vLLM containerizzato con supporto ROCm sulla GPU integrata
- Avviare un server vLLM con endpoint API compatibili con OpenAI sulla porta 8001
- Inviare prompt con `vllm-prompt`
- Effettuare chiamate API al server vLLM utilizzando richieste sia in streaming che non in streaming
- Risolvere i problemi comuni relativi all'avvio del server, alla memoria e alle connessioni client

Ora disponi di una distribuzione vLLM containerizzata per servire modelli linguistici di grandi dimensioni con prestazioni ottimizzate sulla GPU integrata.

## Prossimi passi

- **Prova modelli diversi** — Utilizza `vllm-launch --model <model>` per sperimentare con LLM diversi e confrontare le prestazioni (vedi [Scelta e configurazione di un modello](#choosing-and-configuring-a-model)).
- **Crea un'applicazione** — Utilizza l'API compatibile con OpenAI per integrare vLLM in un'app Python, un chatbot o un flusso di lavoro automatizzato.
- **Affina e distribuisci** — Affina un modello utilizzando LoRA o QLoRA, quindi distribuiscilo con vLLM per un'inferenza ottimizzata.
## Risorse aggiuntive

- **[Documentazione ufficiale di vLLM](https://docs.vllm.ai/)** — Guide complete e riferimenti API
- **[Repository GitHub di vLLM](https://github.com/vllm-project/vllm)** — Codice sorgente, problemi e discussioni della community