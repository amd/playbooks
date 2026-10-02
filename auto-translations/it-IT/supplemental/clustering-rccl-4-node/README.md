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

# Clustering di quattro Ryzen™ AI Halo con RCCL

## Panoramica

Il tuo Ryzen™ AI Halo è già in grado di eseguire modelli linguistici di grandi dimensioni in locale. Il clustering spinge questa capacità ancora oltre, combinando la memoria GPU di più sistemi su una rete locale, offrendoti accesso a modelli ancora più grandi con un ragionamento più solido, una migliore generazione di codice e una comprensione multilingue più approfondita, il tutto interamente sul tuo hardware.

Questo playbook ti insegna come creare un cluster di quattro sistemi Ryzen AI Halo usando RCCL (ROCm Communication Collectives Library) con vLLM ed eseguire Qwen3.5-397B, un modello con 397 miliardi di parametri, su tutte e quattro le macchine con accelerazione ROCm.

## Cosa imparerai

- Come estendere l'allocazione della VRAM sui sistemi Ryzen AI Halo
- Avviare vLLM con supporto ROCm
- Configurare RCCL per l'inferenza tensor-parallel multi-nodo su quattro sistemi Ryzen AI Halo
- Eseguire un modello con 397 miliardi di parametri su quattro sistemi Ryzen AI Halo collegati in rete

## Prerequisiti

### Hardware

Questo playbook richiede quattro unità Ryzen AI Halo e uno switch Ethernet, collegati in topologia a stella con ogni unità cablata direttamente allo switch.

| Componente | Quantità | Descrizione |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Nodi di calcolo che compongono il cluster |
| Switch Ethernet a 10Gbps | 1 | Switch centrale per consentire la comunicazione multi-nodo tra i Ryzen AI Halo (almeno 4 porte) |
| Cavo Ethernet | 4 | Collega ogni unità Halo allo switch (consigliato Cat 7 o superiore) |

> **Nota**: sono necessarie quattro porte dello switch Ethernet per collegare le quattro unità Ryzen AI Halo. È richiesta una quinta porta se si accede al modello da una macchina client separata anziché da una delle unità Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configurazione hardware fisica

> **Nota**: completa questo passaggio su tutte e quattro le macchine (Macchina 1 fino alla Macchina 4).

Collega ogni unità Ryzen AI Halo allo switch Ethernet usando un cavo Cat 7 (o superiore). Questo stabilisce il collegamento a 10Gbps utilizzato per la comunicazione ad alta velocità tra i nodi.

### 1. Determinare le interfacce di rete

Su ogni macchina, individua il nome della sua interfaccia di rete e annotalo (nel resto delle istruzioni verrà indicato come `IFNAME`). Esegui:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Questo stampa direttamente il nome dell'interfaccia, ad esempio:

```bash
enp191s0
```

### 2. Verificare le velocità di collegamento di rete

Conferma che il collegamento sia attivo e funzioni alla velocità massima controllando la velocità della tua interfaccia:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: sostituisci `<IFNAME>` con il nome dell'interfaccia di output ottenuto in [1. Determinare le interfacce di rete](#1-determine-network-interfaces)

Dovresti vedere una velocità di `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: se la velocità è inferiore a `10000Mb/s` o il collegamento non si attiva, controlla il collegamento del cavo e verifica che la porta dello switch sia impostata su 10Gbps. Alcuni switch richiedono di disabilitare l'auto-negoziazione e impostare manualmente la velocità del collegamento; consulta la documentazione del tuo switch.

## Estensione dell'allocazione della VRAM

> **Nota**: completa questo passaggio su tutte e quattro le macchine (Macchina 1 fino alla Macchina 4).

### Configurazione della memoria per l'esecuzione di modelli di grandi dimensioni

Su Linux, ROCm utilizza un pool di memoria di sistema condiviso, e questo pool è configurato per impostazione predefinita alla metà della memoria di sistema.

Questa quantità può essere aumentata modificando l'impostazione delle pagine del Translation Table Manager (TTM) del kernel, seguendo le istruzioni seguenti. AMD consiglia di impostare la VRAM dedicata minima nel BIOS (0,5 GB).

* Installa l'utility pipx e aggiungi il percorso per i wheel installati da pipx al percorso di ricerca del sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installa il wheel amd-debug-tools da PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Esegui lo strumento amd-ttm per interrogare le impostazioni attuali per la memoria condivisa.
  ```bash
  amd-ttm
  ```

* Riconfigura le impostazioni della memoria condivisa a **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Riavvia il sistema affinché le modifiche abbiano effetto.

## Inizializzazione del container vLLM

> **Nota**: completa questo passaggio su tutte e quattro le macchine (Macchina 1 fino alla Macchina 4).

Il tuo Ryzen AI Halo viene fornito con vLLM incluso in un'immagine container precompilata, che esegui utilizzando Podman, uno strumento per container gratuito e open source.

### 1. Creare la directory di download del modello

Quando avvii il modello Qwen3.5-397B in questo playbook, vLLM scaricherà automaticamente i pesi del modello sul tuo sistema. Per assicurarti che tali pesi siano accessibili dall'interno del container, crea prima una directory dei modelli che il container possa montare:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Avviare il container vLLM

Il comando seguente avvia il container e ti porta direttamente a una shell interattiva. Monta la directory dei modelli appena creata e passa il tuo `IFNAME` a `NCCL_SOCKET_IFNAME` e `GLOO_SOCKET_IFNAME`, indicando a RCCL (la libreria utilizzata da vLLM per coordinare le GPU in tutto il cluster) quale interfaccia utilizzare.

Avvia il container con:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Nota**: sostituisci `<IFNAME>` con il nome dell'interfaccia di output ottenuto in [1. Determinare le interfacce di rete](#1-determine-network-interfaces)

## Esecuzione del modello sul cluster

vLLM utilizza Ray per orchestrare il cluster e RCCL per gestire la comunicazione GPU-to-GPU tra i nodi. Una macchina funge da nodo head (Macchina 1), coordinando l'inferenza. Le altre tre si uniscono come nodi worker (Macchine 2, 3 e 4), contribuendo con la loro memoria GPU e capacità di calcolo.

> **Nota**: Ray è una dipendenza opzionale per vLLM ed è disponibile solo all'interno del container Podman preconfigurato. 

All'avvio, vLLM suddivide il modello su tutti e quattro i nodi utilizzando il parallelismo tensoriale. Una volta caricato, l'inferenza procede come se venisse eseguita su un singolo acceleratore.

#### Prevenire gli errori OOM di Ray

Per impostazione predefinita, Ray monitora la memoria host su ogni nodo e termina il processo più grande quando l'utilizzo della memoria supera il 95%. Sul tuo Ryzen™ AI Halo, la GPU e l'host condividono un unico pool di memoria, quindi il caricamento di un modello può generare un `ray.exceptions.OutOfMemoryError` e terminare il processo worker.

Per evitarlo, esporteremo `RAY_memory_monitor_refresh_ms=0` su ogni macchina prima di avviare e unirsi al cluster.
### Passo 1: Avviare il nodo head di Ray (Macchina 1)

Sulla Macchina 1, avviare il nodo head di Ray per inizializzare il cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Individuare `<MACHINE_1_IP>`**: sulla Macchina 1, eseguire `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.

### Passo 2: Unirsi al cluster (Macchine 2, 3 e 4)

Su ciascuna delle Macchine 2, 3 e 4, connettersi al nodo head per formare il cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **Individuare `<MACHINE_N_IP>`**: su ciascuna macchina worker, eseguire `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.

### Passo 3: Servire il modello (Macchina 1)

Sulla Macchina 1, avviare il server vLLM. Questo scaricherà automaticamente il modello e inizierà a servirlo su tutti e quattro i nodi:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.8 \
  --dtype float16 \
  --tensor-parallel-size 4 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Riferimento dei parametri

| Flag | Scopo |
|------|---------|
| `--port` | Porta su cui servire l'API HTTP |
| `--host` | Indirizzo IP a cui associare il server (`0.0.0.0` per tutte le interfacce) |
| `--max-model-len` | Lunghezza massima del contesto in token |
| `--gpu-memory-utilization` | Frazione di memoria GPU da allocare (0.0–1.0) |
| `--dtype` | Tipo di dato per i pesi del modello |
| `--tensor-parallel-size` | Numero di GPU su cui suddividere il modello (impostare sul totale delle GPU nel cluster) |
| `--distributed-executor-backend` | Backend per l'esecuzione multi-nodo (`ray` per le distribuzioni in cluster) |
| `--enforce-eager` | Disabilita la compilazione dei CUDA graph per compatibilità |
| `--language-model-only` | Salta il caricamento dei componenti ausiliari del modello (ad es. l'encoder visivo) |
| `--reasoning-parser` | Abilita il parsing strutturato dell'output di ragionamento per il modello |

Per l'utilizzo completo dei parametri, consultare la [documentazione di vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Accedere al modello

vLLM espone un'API compatibile con OpenAI, quindi è possibile connettere qualsiasi client o interfaccia compatibile al proprio cluster. Un'opzione molto diffusa è [Open WebUI](https://github.com/open-webui/open-webui), che offre un'interfaccia di chat basata su browser.

Per connettere Open WebUI al proprio endpoint vLLM:

1. Aprire **Settings** > **Admin Panel** > **Connections**
2. Fare clic sul **+** in **Manage OpenAI API Connections**
3. Impostare **Connection Type** su **External**
4. Impostare **URL** su `http://<MACHINE_1_IP>:7000/v1`
5. In **Auth**, selezionare **None** dal menu a discesa
6. Lasciare **Model IDs** vuoto per rilevare automaticamente tutti i modelli dall'endpoint

> **Individuare `<MACHINE_1_IP>`**: sulla Macchina 1, eseguire `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale. Se si accede a Open WebUI dalla stessa Macchina 1, è possibile usare `http://localhost:7000/v1`.

![Impostazioni di connessione di Open WebUI per l'endpoint vLLM](assets/openwebui-connection.png)

Una volta connessi, selezionare il modello dal menu a discesa dei modelli in Open WebUI e iniziare a chattare. Il modello è ora in esecuzione su tutti e quattro i nodi Ryzen AI Halo:

![Chat con Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Passi successivi

- **Esplorare altri modelli**: scoprire nuovi modelli su [Hugging Face](https://huggingface.co/models?&sort=trending) che rientrino nella memoria GPU complessiva del proprio cluster
- **Scalare oltre quattro nodi**: aggiungere ulteriori sistemi Ryzen AI Halo come worker Ray aggiuntivi per suddividere i modelli su un numero ancora maggiore di GPU. Seguire il [Passo 2: Unirsi al cluster](#step-2-join-the-cluster-machines-2-3-and-4) su ciascun worker aggiuntivo e aumentare di conseguenza `--tensor-parallel-size`
- **Provare altre strategie di parallelismo**: vLLM supporta il [parallelismo degli esperti](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) per i modelli mixture-of-experts e il [parallelismo dei dati](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) per un throughput maggiore. Sperimentare con `--enable-expert-parallel` e `--data-parallel-size` per trovare la configurazione migliore per il proprio carico di lavoro