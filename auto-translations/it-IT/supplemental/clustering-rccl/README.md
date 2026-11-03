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

# Clustering di due Ryzen™ AI Halo con RCCL

## Panoramica

Il tuo Ryzen™ AI Halo è già in grado di eseguire modelli linguistici di grandi dimensioni in locale. Il clustering porta questa capacità oltre, combinando la memoria GPU di più sistemi tramite una rete locale, dandoti accesso a modelli ancora più grandi, con ragionamento più solido, migliore generazione di codice e comprensione multilingue più approfondita, tutto interamente sul tuo hardware.

Questa guida ti insegna a effettuare il clustering di due sistemi Ryzen AI Halo utilizzando RCCL (ROCm Communication Collectives Library) con vLLM ed eseguire Qwen3.5-397B, un modello con 397 miliardi di parametri, su entrambe le macchine con accelerazione ROCm.

## Cosa imparerai

- Come estendere l'allocazione di VRAM sui sistemi Ryzen AI Halo
- Come avviare vLLM con supporto ROCm
- Come configurare RCCL per l'inferenza tensor-parallel multi-nodo su due sistemi Ryzen AI Halo
- Come eseguire un modello con 397 miliardi di parametri su due sistemi Ryzen AI Halo collegati in rete

## Prerequisiti

### Hardware

Questa guida richiede due unità Ryzen AI Halo e uno switch Ethernet, collegati in una topologia a stella con ciascuna unità cablata direttamente allo switch.

| Componente | Quantità | Descrizione |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nodi di calcolo che formano il cluster |
| Switch Ethernet 10Gbps | 1 | Switch centrale per consentire la comunicazione multi-nodo tra i Ryzen AI Halo (almeno 2 porte) |
| Cavo Ethernet | 2 | Collega ciascuna unità Halo allo switch (consigliato Cat 7 o superiore) |

> **Nota**: sono necessarie due porte dello switch Ethernet per collegare le due unità Ryzen AI Halo. È necessaria una terza porta se accedi al modello da una macchina client separata invece che da una delle unità Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configurazione dell'hardware fisico

> **Nota**: completa questo passaggio sia sulla Macchina 1 che sulla Macchina 2.

Collega ciascuna unità Ryzen AI Halo allo switch Ethernet utilizzando un cavo Cat 7 (o superiore). Questo stabilisce il collegamento a 10Gbps utilizzato per la comunicazione ad alta velocità tra i nodi.

### 1. Determinare le interfacce di rete

Su ciascuna macchina, individua il nome della sua interfaccia di rete e annotalo (verrà indicato nel resto delle istruzioni come `IFNAME`). Esegui:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Questo stampa direttamente il nome dell'interfaccia, ad esempio:

```bash
enp191s0
```

### 2. Verificare la velocità del collegamento di rete

Conferma che il collegamento sia attivo e funzioni alla piena velocità controllando la velocità della tua interfaccia:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: sostituisci `<IFNAME>` con il nome dell'interfaccia in output ottenuto da [1. Determinare le interfacce di rete](#1-determine-network-interfaces)

Dovresti vedere una velocità di `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: se la velocità è inferiore a `10000Mb/s` o il collegamento non si attiva, controlla il collegamento del cavo e conferma che la porta dello switch sia impostata su 10Gbps. Alcuni switch richiedono che l'auto-negoziazione sia disabilitata e la velocità del collegamento impostata manualmente; fai riferimento alla documentazione del tuo switch.

## Estensione dell'allocazione di VRAM

> **Nota**: completa questo passaggio sia sulla Macchina 1 che sulla Macchina 2.

### Configurazione della memoria per l'esecuzione di modelli di grandi dimensioni

Su Linux, ROCm utilizza un pool di memoria di sistema condiviso, e questo pool è configurato per impostazione predefinita alla metà della memoria di sistema.

Questa quantità può essere aumentata modificando l'impostazione delle pagine del Translation Table Manager (TTM) del kernel, seguendo le istruzioni seguenti. AMD consiglia di impostare la VRAM dedicata minima nel BIOS (0,5 GB).

* Installa l'utility pipx e aggiungi il percorso per i wheel installati da pipx nel percorso di ricerca di sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installa il wheel amd-debug-tools da PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Esegui lo strumento amd-ttm per interrogare le impostazioni correnti per la memoria condivisa.
  ```bash
  amd-ttm
  ```

* Riconfigura le impostazioni della memoria condivisa a **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Riavvia il sistema affinché le modifiche abbiano effetto.

## Inizializzazione del container vLLM

> **Nota**: completa questo passaggio sia sulla Macchina 1 che sulla Macchina 2.

Il tuo Ryzen AI Halo viene fornito con vLLM incluso in un'immagine container preconfigurata, che esegui utilizzando Podman, uno strumento per container gratuito e open source.

### 1. Creare la directory di download del modello

Quando eseguirai il modello Qwen3.5-397B in questa guida, vLLM scaricherà automaticamente i pesi del modello sul tuo sistema. Per assicurarti che quei pesi siano accessibili dall'interno del container, crea innanzitutto una directory dei modelli che il container possa montare:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Avviare il container vLLM

Il comando seguente avvia il container e ti porta in una shell interattiva. Monta la directory dei modelli che hai appena creato e passa il tuo `IFNAME` a `NCCL_SOCKET_IFNAME` e `GLOO_SOCKET_IFNAME`, indicando a RCCL (la libreria che vLLM utilizza per coordinare le GPU nel cluster) quale interfaccia utilizzare.

Avvia il container con:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Nota**: sostituisci `<IFNAME>` con il nome dell'interfaccia in output ottenuto da [1. Determinare le interfacce di rete](#1-determine-network-interfaces)

## Esecuzione del modello sul cluster

vLLM utilizza Ray per orchestrare il cluster e RCCL per gestire la comunicazione GPU-to-GPU tra i nodi. Una macchina funge da **nodo principale** (Macchina 1), coordinando l'inferenza. L'altra si unisce come **nodo worker** (Macchina 2), contribuendo con la propria memoria GPU e capacità di calcolo.

> **Nota**: Ray è una dipendenza opzionale per vLLM ed è disponibile solo dall'interno del container Podman preconfigurato.

All'avvio, vLLM suddivide il modello tra entrambi i nodi utilizzando il parallelismo tensoriale. Una volta caricato, l'inferenza procede come se venisse eseguita su un singolo acceleratore.

#### Prevenire errori OOM di Ray

Per impostazione predefinita, Ray monitora la memoria host su ciascun nodo e termina il processo più grande quando l'utilizzo della memoria supera il 95%. Sul tuo Ryzen™ AI Halo, la GPU e l'host condividono un unico pool di memoria, quindi il caricamento di un modello può innescare un `ray.exceptions.OutOfMemoryError` e terminare il processo worker.

Per prevenire questo, esporteremo `RAY_memory_monitor_refresh_ms=0` su ciascuna macchina prima di avviare e unirsi al cluster.
### Passaggio 1: Avvia il nodo head di Ray (Macchina 1)

Sulla Macchina 1, avvia il nodo head di Ray per inizializzare il cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Individuazione di `<MACHINE_1_IP>`**: sulla Macchina 1, esegui `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.

### Passaggio 2: Unisciti al cluster (Macchina 2)

Sulla Macchina 2, connettiti al nodo head per formare il cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Individuazione di `<MACHINE_2_IP>`**: sulla Macchina 2, esegui `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.

### Passaggio 3: Distribuisci il modello (Macchina 1)

Sulla Macchina 1, avvia il server vLLM. Questo scaricherà automaticamente il modello e inizierà a distribuirlo su entrambi i nodi:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Riferimento dei parametri

| Flag | Scopo |
|------|-------|
| `--port` | Porta su cui distribuire l'API HTTP |
| `--host` | Indirizzo IP a cui associare il server (`0.0.0.0` per tutte le interfacce) |
| `--max-model-len` | Lunghezza massima del contesto in token |
| `--gpu-memory-utilization` | Frazione di memoria GPU da allocare (0.0–1.0) |
| `--dtype` | Tipo di dati per i pesi del modello |
| `--tensor-parallel-size` | Numero di GPU su cui suddividere il modello (impostare al numero totale di GPU nel cluster) |
| `--distributed-executor-backend` | Backend per l'esecuzione multi-nodo (`ray` per distribuzioni in cluster) |
| `--enforce-eager` | Disabilita la compilazione dei CUDA graph per compatibilità |
| `--language-model-only` | Salta il caricamento dei componenti ausiliari del modello (ad es. l'encoder visivo) |
| `--reasoning-parser` | Abilita il parsing strutturato dell'output di ragionamento per il modello |

Per l'utilizzo completo dei parametri, consulta la [documentazione di vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Accesso al modello

vLLM espone un'API compatibile con OpenAI, quindi puoi connettere qualsiasi client o interfaccia compatibile al tuo cluster. Un'opzione molto diffusa è [Open WebUI](https://github.com/open-webui/open-webui), che fornisce un'interfaccia di chat basata su browser.

Per connettere Open WebUI al tuo endpoint vLLM:

1. Apri **Settings** > **Admin Panel** > **Connections**
2. Fai clic sul **+** in **Manage OpenAI API Connections**
3. Imposta il **Connection Type** su **External**
4. Imposta l'**URL** su `http://<MACHINE_1_IP>:7000/v1`
5. In **Auth**, seleziona **None** dal menu a discesa
6. Lascia **Model IDs** vuoto per scoprire automaticamente tutti i modelli dall'endpoint

> **Individuazione di `<MACHINE_1_IP>`**: sulla Macchina 1, esegui `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale. Se accedi a Open WebUI dalla Macchina 1 stessa, puoi usare `http://localhost:7000/v1`.

![Impostazioni di connessione di Open WebUI per l'endpoint vLLM](assets/openwebui-connection.png)

Una volta connesso, seleziona il modello dal menu a discesa dei modelli in Open WebUI e inizia a chattare. Il modello ora è in esecuzione su entrambi i tuoi nodi Ryzen AI Halo:

![Chat con Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Prossimi passi

- **Esplora altri modelli**: scopri nuovi modelli su [Hugging Face](https://huggingface.co/models?&sort=trending) che rientrano nella memoria GPU combinata del tuo cluster
- **Scala a quattro nodi**: aggiungi altri due sistemi Ryzen AI Halo come ulteriori worker Ray per suddividere i modelli su ancora più GPU. Questo richiede uno switch Ethernet con almeno quattro porte, una per ciascun nodo. Segui il [Passaggio 2: Unisciti al cluster](#step-2-join-the-cluster-machine-2) su ciascun worker aggiuntivo e aumenta di conseguenza `--tensor-parallel-size`
- **Prova altre strategie di parallelismo**: vLLM supporta il [parallelismo esperto](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) per i modelli mixture-of-experts e il [parallelismo dati](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) per un throughput più elevato. Sperimenta con `--enable-expert-parallel` e `--data-parallel-size` per trovare la configurazione migliore per il tuo carico di lavoro