<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Questo playbook utilizza tag speciali che GitHub non è in grado di visualizzare correttamente. Visita [amd.com/playbooks](https://amd.com/playbooks) per visualizzare correttamente questo contenuto.
<!-- @github-only:end -->


## Panoramica

vLLM è un motore di inferenza ad alte prestazioni progettato per i large language model (LLM). Offre un servizio ottimizzato con batching continuo per un elevato throughput e un'API compatibile con OpenAI per un'integrazione applicativa fluida. Questo rende vLLM ideale per le implementazioni in produzione in cui velocità ed efficienza delle risorse sono fondamentali.

Questo playbook ti insegna come servire LLM utilizzando vLLM containerizzato sulla GPU integrata e come interagire con i modelli tramite l'API Python di OpenAI.

## Cosa Imparerai

- Come configurare e avviare un server vLLM con supporto AMD ROCm™
- Come interagire con i modelli tramite endpoint API compatibili con OpenAI
- Come inviare prompt al server locale con `vllm-prompt`

## Configurazione della Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli Aggiornamenti Software

> **Nota**: se VS Code non è installato, puoi installarlo tramite AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei Prerequisiti Software

Questo playbook utilizza un'immagine container predefinita che include vLLM, il supporto ROCm e gli script di supporto necessari per avviare il server. Non è necessario installare manualmente PyTorch, vLLM o gli script locali del playbook.

Non è previsto alcun passaggio di installazione di vLLM lato host. Avvia vLLM con:

```bash
vllm-launch
```

Il launcher avvia il container, indirizza la GPU integrata ed espone un server vLLM locale compatibile con OpenAI. In alternativa, fai clic sull'icona di vLLM nella barra delle applicazioni.

## Avvio Rapido

### 1. Verifica che il Server vLLM Sia in Esecuzione

`vllm-launch` potrebbe impiegare un paio di minuti per inizializzare tutto. Una volta avviato, il server è disponibile all'indirizzo `http://localhost:8001`. Tieni aperto il terminale di avvio poiché il server viene eseguito in primo piano, quindi apri un terminale separato per i passaggi rimanenti. Gli esempi seguenti utilizzano `Qwen/Qwen3-1.7B`; se il tuo launcher è configurato per un modello diverso, sostituisci quell'ID modello nelle richieste.

### 2. Invia un Prompt

Utilizza lo script `vllm-prompt` fornito per inviare una richiesta al server vLLM locale compatibile con OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chatta con il modello utilizzando l'API Python di OpenAI

Poiché vLLM espone un'API compatibile con OpenAI, puoi utilizzare il pacchetto Python `openai` per interagire con esso.

Innanzitutto, crea un ambiente virtuale Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Installa il pacchetto OpenAI
```bash
pip install openai
```

Crea un client `OpenAI` puntato al server vLLM locale anziché ai server di OpenAI. L'`api_key` è richiesta dal client ma vLLM non la convalida, quindi qualsiasi stringa funziona:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Successivamente, invia una richiesta di completamento chat. Questo utilizza lo stesso formato di messaggio dell'API OpenAI — un elenco di messaggi con ruoli come `"user"` e `"assistant"`. Impostare `stream=True` significa che la risposta arriverà in modo incrementale anziché tutta in una volta:

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

Infine, itera sui frammenti in streaming e stampa ogni porzione di testo man mano che arriva:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Lo script incluso [chat_with_model.py](assets/chat_with_model.py) contiene l'esempio completo e può essere scaricato.


## Risoluzione dei Problemi

### Connessione rifiutata

Assicurati che il server sia in esecuzione:
```bash
curl http://localhost:8001/health
```

## Riepilogo

In questo playbook, hai imparato a:

- Avviare vLLM containerizzato con supporto ROCm sulla GPU integrata
- Avviare un server vLLM con endpoint API compatibili con OpenAI sulla porta 8001
- Inviare prompt con `vllm-prompt`
- Effettuare chiamate API al server vLLM utilizzando richieste sia in streaming che non in streaming
- Risolvere problemi comuni relativi all'avvio del server, alla memoria e alle connessioni client

Ora disponi di un'implementazione vLLM containerizzata per servire large language model con prestazioni ottimizzate sulla GPU integrata.

## Prossimi Passi

- **Prova modelli diversi** — Sostituisci il modello nella configurazione di `vllm-launch` per sperimentare con LLM diversi e confrontare le prestazioni.
- **Crea un'applicazione** — Utilizza l'API compatibile con OpenAI per integrare vLLM in un'app Python, un chatbot o un flusso di lavoro di automazione.
- **Ottimizza e servi** — Ottimizza un modello utilizzando LoRA o QLoRA, quindi implementalo con vLLM per un'inferenza ottimizzata.

## Risorse Aggiuntive

- **[Documentazione Ufficiale di vLLM](https://docs.vllm.ai/)** — Guide complete e riferimenti API
- **[Repository GitHub di vLLM](https://github.com/vllm-project/vllm)** — Codice sorgente, problemi e discussioni della community