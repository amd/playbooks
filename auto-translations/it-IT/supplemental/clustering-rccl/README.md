<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Questo playbook utilizza tag speciali che GitHub non è in grado di visualizzare. Visita [amd.com/playbooks](https://amd.com/playbooks) per visualizzare correttamente questo contenuto.
<!-- @github-only:end -->

# Clustering di due Ryzen™ AI Halo con RCCL

## Panoramica

Il tuo Ryzen™ AI Halo è già in grado di eseguire modelli linguistici di grandi dimensioni in locale. Il clustering porta questa capacità oltre, combinando la memoria GPU di più sistemi tramite una rete locale, dandoti accesso a modelli ancora più grandi con un ragionamento più solido, una migliore generazione di codice e una comprensione multilingue più approfondita, il tutto interamente sul tuo hardware.

Questo playbook ti insegna come effettuare il clustering di due sistemi Ryzen AI Halo utilizzando RCCL (ROCm Communication Collectives Library) con vLLM ed eseguire Qwen3.5-397B, un modello con 397 miliardi di parametri, su entrambe le macchine con accelerazione ROCm.

## Cosa imparerai

- Come estendere l'allocazione di VRAM sui sistemi Ryzen AI Halo
- Come avviare vLLM con supporto ROCm
- Come configurare RCCL per l'inferenza tensor-parallel multi-nodo su due sistemi Ryzen AI Halo
- Come eseguire un modello con 397 miliardi di parametri su due sistemi Ryzen AI Halo collegati in rete

## Prerequisiti

### Hardware

Questo playbook richiede due unità Ryzen AI Halo e uno switch Ethernet, collegati in una topologia a stella con ciascuna unità cablata direttamente allo switch.

| Componente | Quantità | Descrizione |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nodi di calcolo che formano il cluster |
| Switch Ethernet 10Gbps | 1 | Switch centrale per consentire la comunicazione multi-nodo tra i Ryzen AI Halo (almeno 2 porte) |
| Cavo Ethernet | 2 | Collega ciascuna unità Halo allo switch (si consiglia Cat 7 o superiore) |

> **Nota**: sono necessarie due porte dello switch Ethernet per collegare le due unità Ryzen AI Halo. È necessaria una terza porta se accedi al modello da una macchina client separata anziché da una delle unità Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configurazione fisica dell'hardware

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

Conferma che il collegamento sia attivo e funzioni a piena velocità controllando la velocità della tua interfaccia:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: sostituisci `<IFNAME>` con il nome dell'interfaccia di output ottenuto in [1. Determinare le interfacce di rete](#1-determinare-le-interfacce-di-rete)

Dovresti vedere una velocità di `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: se la velocità è inferiore a `10000Mb/s` o il collegamento non si attiva, controlla il collegamento del cavo e verifica che la porta dello switch sia impostata su 10Gbps. Alcuni switch richiedono la disattivazione dell'auto-negoziazione e l'impostazione manuale della velocità del collegamento; fai riferimento alla documentazione del tuo switch.

## Estensione dell'allocazione di VRAM

> **Nota**: completa questo passaggio sia sulla Macchina 1 che sulla Macchina 2.

### Configurazione della memoria per l'esecuzione di modelli di grandi dimensioni

Su Linux, ROCm utilizza un pool di memoria di sistema condiviso, e questo pool è configurato per impostazione predefinita a metà della memoria di sistema.

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

Il tuo Ryzen AI Halo viene fornito con vLLM confezionato all'interno di un'immagine container predefinita, che esegui utilizzando Podman, uno strumento per container gratuito e open source.

### 1. Creare la directory di download del modello

Quando servi il modello Qwen3.5-397B in questo playbook, vLLM scaricherà automaticamente i pesi del modello sul tuo sistema. Per assicurarti che quei pesi siano accessibili dall'interno del container, crea prima una directory dei modelli che il container possa montare:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Avviare il container vLLM

Il comando seguente avvia il container e ti porta in una shell interattiva. Monta la directory dei modelli appena creata e passa il tuo `IFNAME` a `NCCL_SOCKET_IFNAME` e `GLOO_SOCKET_IFNAME`, indicando a RCCL (la libreria utilizzata da vLLM per coordinare le GPU nel cluster) quale interfaccia utilizzare.

Avvia il container con:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Nota**: sostituisci `<IFNAME>` con il nome dell'interfaccia di output ottenuto in [1. Determinare le interfacce di rete](#1-determinare-le-interfacce-di-rete)

## Esecuzione del modello sul cluster

vLLM utilizza Ray per orchestrare il cluster e RCCL per gestire la comunicazione GPU-to-GPU tra i nodi. Una macchina funge da **nodo principale** (head node) (Macchina 1), coordinando l'inferenza. L'altra si unisce come **nodo worker** (Macchina 2), contribuendo con la propria memoria GPU e capacità di calcolo.

> **Nota**: Ray è una dipendenza opzionale per vLLM ed è disponibile solo dall'interno del container Podman preconfigurato.

All'avvio, vLLM suddivide il modello tra entrambi i nodi utilizzando il tensor parallelism. Una volta caricato, l'inferenza procede come se fosse eseguita su un singolo acceleratore.

### Fase 1: avviare il nodo principale Ray (Macchina 1)

Sulla Macchina 1, avvia il nodo principale Ray per inizializzare il cluster:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Individuazione di `<MACHINE_1_IP>`**: sulla Macchina 1, esegui `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.
### Fase 2: Unione al Cluster (Macchina 2)

Sulla Macchina 2, connettersi al nodo principale per formare il cluster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Individuazione di `<MACHINE_2_IP>`**: Sulla Macchina 2, eseguire `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.

### Fase 3: Servire il Modello (Macchina 1)

Sulla Macchina 1, avviare il server vLLM. Questo scaricherà automaticamente il modello e inizierà a servirlo su entrambi i nodi:

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

#### Riferimento dei Parametri

| Flag | Scopo |
|------|-------|
| `--port` | Porta su cui servire l'API HTTP |
| `--host` | Indirizzo IP a cui associare il server (`0.0.0.0` per tutte le interfacce) |
| `--max-model-len` | Lunghezza massima del contesto in token |
| `--gpu-memory-utilization` | Frazione della memoria GPU da allocare (0.0–1.0) |
| `--dtype` | Tipo di dati per i pesi del modello |
| `--tensor-parallel-size` | Numero di GPU su cui suddividere il modello (impostare al numero totale di GPU nel cluster) |
| `--distributed-executor-backend` | Backend per l'esecuzione multi-nodo (`ray` per implementazioni cluster) |
| `--enforce-eager` | Disabilita la compilazione dei CUDA graph per compatibilità |
| `--language-model-only` | Salta il caricamento dei componenti ausiliari del modello (ad es. l'encoder visivo) |
| `--reasoning-parser` | Abilita il parsing strutturato dell'output di ragionamento per il modello |

Per l'utilizzo completo dei parametri, fare riferimento alla [documentazione di vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Accesso al Modello

vLLM espone un'API compatibile con OpenAI, quindi è possibile connettere qualsiasi client o interfaccia compatibile al proprio cluster. Un'opzione molto diffusa è [Open WebUI](https://github.com/open-webui/open-webui), che fornisce un'interfaccia di chat basata su browser.

Per connettere Open WebUI al proprio endpoint vLLM:

1. Aprire **Impostazioni** > **Pannello di Amministrazione** > **Connessioni**
2. Fare clic sul **+** su **Gestisci Connessioni API OpenAI**
3. Impostare il **Tipo di Connessione** su **Esterno**
4. Impostare l'**URL** su `http://<MACHINE_1_IP>:7000/v1`
5. In **Autenticazione**, selezionare **Nessuna** dal menu a discesa
6. Lasciare vuoto il campo **ID Modello** per rilevare automaticamente tutti i modelli dall'endpoint

> **Individuazione di `<MACHINE_1_IP>`**: Sulla Macchina 1, eseguire `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale. Se si accede a Open WebUI dalla Macchina 1 stessa, è possibile utilizzare `http://localhost:7000/v1`.

![Impostazioni di connessione di Open WebUI per l'endpoint vLLM](assets/openwebui-connection.png)

Una volta connessi, selezionare il modello dal menu a discesa dei modelli in Open WebUI e iniziare a chattare. Il modello è ora in esecuzione su entrambi i nodi Ryzen AI Halo:

![Chat con Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Passaggi Successivi

- **Esplorare altri modelli**: Scoprire nuovi modelli su [Hugging Face](https://huggingface.co/models?&sort=trending) che rientrano nella memoria GPU combinata del cluster
- **Scalare a quattro nodi**: Aggiungere altri due sistemi Ryzen AI Halo come worker Ray aggiuntivi per suddividere i modelli su un numero ancora maggiore di GPU. Questo richiede uno switch Ethernet con almeno quattro porte, una per ogni nodo. Seguire [Fase 2: Unione al Cluster](#step-2-join-the-cluster-machine-2) su ciascun worker aggiuntivo e aumentare di conseguenza `--tensor-parallel-size`
- **Provare altre strategie di parallelismo**: vLLM supporta il [parallelismo esperto](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) per i modelli mixture-of-experts e il [parallelismo dati](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) per un throughput maggiore. Sperimentare con `--enable-expert-parallel` e `--data-parallel-size` per trovare la configurazione migliore per il proprio carico di lavoro