<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering di due Ryzen™ AI Halo con RCCL

## Panoramica

Il tuo Ryzen™ AI Halo è già in grado di eseguire modelli linguistici di grandi dimensioni in locale. Il clustering va oltre, combinando la memoria GPU di più sistemi su una rete locale, dandoti accesso a modelli ancora più grandi con ragionamento più potente, migliore generazione di codice e comprensione multilingue più approfondita, il tutto interamente sul tuo hardware.

Questo playbook ti insegna come raggruppare in cluster due sistemi Ryzen AI Halo utilizzando RCCL (ROCm Communication Collectives Library) con vLLM ed eseguire Qwen3.5-397B, un modello da 397 miliardi di parametri, su entrambe le macchine con accelerazione ROCm.

## Cosa Imparerai

- Come estendere l'allocazione VRAM sui sistemi Ryzen AI Halo
- Avviare vLLM con supporto ROCm
- Configurare RCCL per l'inferenza tensor-parallel multi-nodo su due sistemi Ryzen AI Halo
- Eseguire un modello da 397 miliardi di parametri su due sistemi Ryzen AI Halo collegati in rete

## Prerequisiti

### Hardware

Questo playbook richiede due unità Ryzen AI Halo e uno switch Ethernet, collegati in una topologia a stella con ciascuna unità cablata direttamente allo switch.

| Componente | Quantità | Descrizione |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nodi di calcolo che formano il cluster |
| Switch Ethernet 10Gbps | 1 | Switch centrale per consentire la comunicazione multi-nodo tra i Ryzen AI Halo (almeno 2 porte) |
| Cavo Ethernet | 2 | Collega ciascuna unità Halo allo switch (consigliato Cat 7 o superiore) |

> **Nota**: Sono necessarie due porte dello switch Ethernet per collegare le due unità Ryzen AI Halo. Una terza porta è necessaria se si accede al modello da una macchina client separata invece che da una delle unità Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configurazione Fisica dell'Hardware

> **Nota**: Completa questo passaggio sia su Machine 1 che su Machine 2.

Collega ciascuna unità Ryzen AI Halo allo switch Ethernet utilizzando un cavo Cat 7 (o superiore). Questo stabilisce il collegamento a 10Gbps utilizzato per la comunicazione ad alta velocità tra i nodi.

### 1. Determinare le Interfacce di Rete

Su ciascuna macchina, trova il nome della sua interfaccia di rete e annotalo (verrà indicato nel resto delle istruzioni come `IFNAME`). Esegui:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Questo stampa direttamente il nome dell'interfaccia, ad esempio:

```bash
enp191s0
```

### 2. Verificare le Velocità del Collegamento di Rete

Conferma che il collegamento sia attivo e funzionante alla velocità massima verificando la velocità della tua interfaccia:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: Sostituisci `<IFNAME>` con il nome dell'interfaccia ottenuto in [1. Determinare le Interfacce di Rete](#1-determine-network-interfaces)

Dovresti vedere una velocità di `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: Se la velocità è inferiore a `10000Mb/s` o il collegamento non si attiva, controlla la connessione del cavo e verifica che la porta dello switch sia impostata a 10Gbps. Alcuni switch richiedono la disabilitazione della negoziazione automatica e l'impostazione manuale della velocità del collegamento; consulta la documentazione del tuo switch.

## Estensione dell'Allocazione VRAM

> **Nota**: Completa questo passaggio sia su Machine 1 che su Machine 2.

### Configurazione della Memoria per l'Esecuzione di Modelli di Grandi Dimensioni

Su Linux, ROCm utilizza un pool di memoria di sistema condivisa, e questo pool è configurato per impostazione predefinita alla metà della memoria di sistema.

Questa quantità può essere aumentata modificando l'impostazione della pagina TTM (Translation Table Manager) del kernel, seguendo le istruzioni riportate di seguito. AMD consiglia di impostare la VRAM dedicata minima nel BIOS (0,5 GB).

* Installa l'utilità pipx e aggiungi il percorso per le wheel installate da pipx nel percorso di ricerca del sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installa la wheel amd-debug-tools da PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Esegui lo strumento amd-ttm per interrogare le impostazioni correnti della memoria condivisa.
  ```bash
  amd-ttm
  ```

* Riconfigura le impostazioni della memoria condivisa a **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Riavvia il sistema affinché le modifiche abbiano effetto.

## Inizializzazione del Container vLLM

> **Nota**: Completa questo passaggio sia su Machine 1 che su Machine 2.

Il tuo Ryzen AI Halo viene fornito con vLLM incluso in un'immagine container precompilata, che esegui utilizzando Podman, uno strumento container gratuito e open source.

### 1. Creare la Directory di Download del Modello

Quando servi il modello Qwen3.5-397B in questo playbook, vLLM scaricherà automaticamente i pesi del modello sul tuo sistema. Per assicurarti che quei pesi siano accessibili dall'interno del container, crea prima una directory models che il container possa montare:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Avviare il Container vLLM

Il comando seguente avvia il container e ti porta in una shell interattiva. Monta la directory models appena creata e passa il tuo `IFNAME` a `NCCL_SOCKET_IFNAME` e `GLOO_SOCKET_IFNAME`, indicando a RCCL (la libreria che vLLM usa per coordinare le GPU nel cluster) quale interfaccia utilizzare.

Avvia il container con:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Nota**: Sostituisci `<IFNAME>` con il nome dell'interfaccia ottenuto in [1. Determinare le Interfacce di Rete](#1-determine-network-interfaces)

## Esecuzione del Modello sul Cluster

vLLM utilizza Ray per orchestrare il cluster e RCCL per gestire la comunicazione GPU-to-GPU tra i nodi. Una macchina funge da **nodo head** (Machine 1), coordinando l'inferenza. L'altra si unisce come **nodo worker** (Machine 2), contribuendo con la sua memoria GPU e capacità di calcolo.

> **Nota**: Ray è una dipendenza opzionale per vLLM ed è disponibile solo dall'interno del container Podman preconfigurato.

All'avvio, vLLM suddivide il modello su entrambi i nodi utilizzando il parallelismo tensoriale. Una volta caricato, l'inferenza procede come se fosse in esecuzione su un singolo acceleratore.

### Passaggio 1: Avviare il Nodo Head Ray (Machine 1)

Su Machine 1, avvia il nodo head Ray per inizializzare il cluster:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Trovare `<MACHINE_1_IP>`**: Su Machine 1, esegui `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.

### Passaggio 2: Unirsi al Cluster (Machine 2)

Su Machine 2, connettiti al nodo head per formare il cluster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Trovare `<MACHINE_2_IP>`**: Su Machine 2, esegui `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.

### Passaggio 3: Servire il Modello (Machine 1)

Su Machine 1, avvia il server vLLM. Questo scaricherà automaticamente il modello e inizierà a servirlo su entrambi i nodi:

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

#### Riferimento ai Parametri

| Flag | Scopo |
|------|---------|
| `--port` | Porta su cui servire l'API HTTP |
| `--host` | Indirizzo IP a cui associare il server (`0.0.0.0` per tutte le interfacce) |
| `--max-model-len` | Lunghezza massima del contesto in token |
| `--gpu-memory-utilization` | Frazione di memoria GPU da allocare (0.0–1.0) |
| `--dtype` | Tipo di dato per i pesi del modello |
| `--tensor-parallel-size` | Numero di GPU su cui suddividere il modello (impostare al totale delle GPU nel cluster) |
| `--distributed-executor-backend` | Backend per l'esecuzione multi-nodo (`ray` per i deployment in cluster) |
| `--enforce-eager` | Disabilita la compilazione del grafo CUDA per compatibilità |
| `--language-model-only` | Salta il caricamento dei componenti ausiliari del modello (ad es., il codificatore visivo) |
| `--reasoning-parser` | Abilita il parsing strutturato dell'output di ragionamento per il modello |

Per l'utilizzo completo dei parametri, consulta la [documentazione di vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Accesso al Modello

vLLM espone un'API compatibile con OpenAI, quindi puoi connettere qualsiasi client o interfaccia compatibile al tuo cluster. Un'opzione popolare è [Open WebUI](https://github.com/open-webui/open-webui), che fornisce un'interfaccia di chat basata su browser.

Per connettere Open WebUI al tuo endpoint vLLM:

1. Apri **Impostazioni** > **Pannello Admin** > **Connessioni**
2. Clicca su **+** su **Gestisci Connessioni API OpenAI**
3. Imposta il **Tipo di Connessione** su **Esterno**
4. Imposta l'**URL** su `http://<MACHINE_1_IP>:7000/v1`
5. Sotto **Auth**, seleziona **Nessuno** dal menu a tendina
6. Lascia **ID Modello** vuoto per scoprire automaticamente tutti i modelli dall'endpoint

> **Trovare `<MACHINE_1_IP>`**: Su Machine 1, esegui `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale. Se accedi a Open WebUI da Machine 1 stessa, puoi usare `http://localhost:7000/v1`.

![Impostazioni di connessione Open WebUI per l'endpoint vLLM](assets/openwebui-connection.png)

Una volta connesso, seleziona il modello dal menu a tendina dei modelli in Open WebUI e inizia a chattare. Il modello è ora in esecuzione su entrambi i tuoi nodi Ryzen AI Halo:

![Chat con Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Prossimi Passi

- **Esplora altri modelli**: Scopri nuovi modelli su [Hugging Face](https://huggingface.co/models?&sort=trending) che rientrano nella memoria GPU combinata del tuo cluster
- **Scala a quattro nodi**: Aggiungi altri due sistemi Ryzen AI Halo come worker Ray aggiuntivi per suddividere i modelli su ancora più GPU. Questo richiede uno switch Ethernet con almeno quattro porte, una per ciascun nodo. Segui il [Passaggio 2: Unirsi al Cluster](#step-2-join-the-cluster-machine-2) su ciascun worker aggiuntivo e aumenta `--tensor-parallel-size` di conseguenza
- **Prova altre strategie di parallelismo**: vLLM supporta il [parallelismo degli esperti](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) per i modelli mixture-of-experts e il [parallelismo dei dati](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) per una maggiore throughput. Sperimenta con `--enable-expert-parallel` e `--data-parallel-size` per trovare la configurazione migliore per il tuo carico di lavoro