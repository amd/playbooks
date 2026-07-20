<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> Questo playbook utilizza tag speciali che GitHub non è in grado di visualizzare. Visita [amd.com/playbooks](https://amd.com/playbooks) per visualizzare correttamente questo contenuto.
<!-- @github-only:end -->

# Creazione di un cluster con due Ryzen™ AI Halo tramite RPC

## Panoramica

Il tuo Ryzen™ AI Halo è già in grado di eseguire modelli linguistici di grandi dimensioni in locale. Il clustering porta questa capacità oltre, combinando la memoria GPU di più sistemi tramite una rete locale, dandoti accesso a modelli ancora più grandi con capacità di ragionamento più solide, generazione di codice migliore e una comprensione multilingue più approfondita, il tutto interamente sul tuo hardware.

Questo playbook ti insegna a creare un cluster con due sistemi Ryzen AI Halo utilizzando il motore RPC di llama.cpp ed eseguire GLM 4.7, un modello con 358 miliardi di parametri, su entrambe le macchine con accelerazione AMD ROCm™.

## Cosa imparerai

- Come estendere l'allocazione di VRAM sui sistemi Ryzen AI Halo
- Come installare llama.cpp con supporto ROCm e RPC
- Come configurare un worker RPC e avviare l'inferenza distribuita su due nodi
- Come eseguire un modello con 358 miliardi di parametri su due sistemi Ryzen AI Halo collegati in rete

## Impostazione della configurazione della memoria

> **Nota**: completa questo passaggio sia sulla Macchina 1 che sulla Macchina 2.

<!-- @os:windows -->
Su Windows, per eseguire modelli più grandi che richiedono maggiore memoria, è necessario utilizzare l'allocazione AMD Variable Graphics Memory (VRAM iGPU).

Questo può essere fatto aprendo il pannello di controllo AMD Software: Adrenalin Edition e accedendo a: `Performance > Tuning > AMD Variable Graphics Memory`. Imposta il valore su **96 GB**. Riavvia il sistema affinché le modifiche abbiano effetto.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Su Linux, ROCm utilizza un pool di memoria di sistema condiviso, configurato per impostazione predefinita a metà della memoria di sistema.

Questa quantità può essere aumentata modificando l'impostazione delle pagine del Translation Table Manager (TTM) del kernel, seguendo le istruzioni riportate di seguito. AMD consiglia di impostare la VRAM dedicata minima nel BIOS (0,5 GB).

* Installa l'utility pipx e aggiungi il percorso per i wheel installati da pipx al percorso di ricerca di sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installa il wheel amd-debug-tools da PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Esegui lo strumento amd-ttm per interrogare le impostazioni attuali della memoria condivisa.
  ```bash
  amd-ttm
  ```

* Riconfigura le impostazioni della memoria condivisa a **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Riavvia il sistema affinché le modifiche abbiano effetto.


<!-- @os:end -->
<!-- @device:halo_box -->
## Verifica degli aggiornamenti software

<!-- @require:software-update -->
<!-- @device:end -->
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
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Installa:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) con il carico di lavoro **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Configurazione fisica dell'hardware

> **Nota**: completa questo passaggio sia sulla Macchina 1 che sulla Macchina 2.

Collega ciascuna unità Ryzen AI Halo allo switch Ethernet utilizzando un cavo Cat 7 (o superiore). Questo stabilisce il collegamento a 10Gbps utilizzato per la comunicazione ad alta velocità tra i nodi.
<!-- @os:linux -->
### 1. Determinazione delle interfacce di rete

Su ciascuna macchina, individua il nome della sua interfaccia di rete e prendine nota (verrà indicato di seguito come `IFNAME`). Esegui:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Questo stampa direttamente il nome dell'interfaccia, ad esempio:

```bash
enp191s0
```

### 2. Verifica della velocità del collegamento di rete

Conferma che il collegamento sia attivo e funzioni alla massima velocità controllando la velocità della tua interfaccia:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: sostituisci `<IFNAME>` con il nome dell'interfaccia in output ottenuto in [1. Determinazione delle interfacce di rete](#1-determine-network-interfaces)

Dovresti vedere una velocità di `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: se la velocità è inferiore a `10000Mb/s` o il collegamento non si attiva, verifica il collegamento del cavo e conferma che la porta dello switch sia impostata su 10Gbps. Alcuni switch richiedono la disattivazione dell'auto-negoziazione e l'impostazione manuale della velocità di collegamento; consulta la documentazione del tuo switch.

<!-- @os:end -->

<!-- @os:windows -->
### Verifica della velocità del collegamento di rete

Su ciascuna macchina, controlla la velocità del collegamento delle tue interfacce di rete:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

La tua interfaccia Ethernet dovrebbe essere `Up` e funzionare a `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Nota**: se la velocità è inferiore a `10 Gbps` o il collegamento non si attiva, verifica il collegamento del cavo e conferma che la porta dello switch sia impostata su 10Gbps. Alcuni switch richiedono la disattivazione dell'auto-negoziazione e l'impostazione manuale della velocità di collegamento; consulta la documentazione del tuo switch.

<!-- @os:end -->

## Installazione di llama.cpp

> **Nota**: completa questo passaggio sia sulla Macchina 1 che sulla Macchina 2.

Sono disponibili due opzioni di installazione:

- [Opzione 1: Lemonade SDK (consigliata)](#option-1-lemonade-sdk-recommended) - binari pre-compilati, configurazione più rapida
- [Opzione 2: Build manuale dal sorgente](#option-2-manual-source-build) - build dal sorgente con pieno controllo sui flag di compilazione

### Opzione 1: Lemonade SDK (consigliata)

Lemonade SDK fornisce build notturne di llama.cpp con accelerazione AMD ROCm 7, destinate a GPU come gfx1151 (Strix Halo / Ryzen AI Max+ 395) e altre architetture Radeon recenti.

<!-- @os:windows -->
#### Step 1: Scaricare i Binari Pre-Compilati

Vai alla pagina dell'ultima release e scarica l'archivio corrispondente alla tua piattaforma e al target GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Scarica il file denominato `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (dove `xxxx` è il numero della build).

#### Step 2: Estrarre i Binari

Decomprimi l'archivio scaricato:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Questa directory ora contiene le build abilitate per ROCm di `llama-cli.exe`, `llama-server.exe` e `rpc-server.exe`, precompilate per il tuo sistema Ryzen AI Halo.

#### Step 3: Verificare il Rilevamento della GPU

```bash
.\llama-cli.exe --list-devices
```

Output previsto:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: Scaricare i Binari Pre-Compilati

Vai alla pagina dell'ultima release e scarica l'archivio corrispondente alla tua piattaforma e al target GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Scarica il file denominato `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (dove `xxxx` è il numero della build).

#### Step 2: Estrarre e Preparare i Binari

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Questa directory ora contiene le build abilitate per ROCm di `llama-cli`, `llama-server` e `rpc-server`, precompilate per il tuo sistema Ryzen AI Halo.

#### Step 3: Verificare il Rilevamento della GPU

```bash
./llama-cli --list-devices
```

Output previsto:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Con llama.cpp preparato su ciascun nodo, procedi con [Scaricamento del Modello](#downloading-the-model).

### Opzione 2: Build Manuale da Sorgente

<!-- @os:windows -->
#### Step 1: Compilare llama.cpp

Apri il **x64 Native Tools Command Prompt** (installato con Visual Studio Build Tools) e clona il repository:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Aggiungi HIP al tuo path e compila con supporto ROCm e RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Flag di Build | Scopo |
|-----------|---------|
| `-DGGML_HIP=ON` | Abilita lo stack software ROCm/HIP |
| `-DGGML_RPC=ON` | Abilita RPC per l'inferenza distribuita |
| `-DGPU_TARGETS=gfx1151` | Ha come target la GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Utilizza il sistema di build Ninja |

#### Step 2: Verificare il Rilevamento della GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Output previsto:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Step 3: Aggiungere HIP al Path Utente

Il passaggio di build precedente ha impostato `%HIP_PATH%\bin` solo per la sessione corrente. Per rendere le librerie HIP disponibili in qualsiasi terminale (non solo nel x64 Native Tools Command Prompt), aggiungilo permanentemente al tuo `PATH` utente:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Con llama.cpp preparato su ciascun nodo, procedi con [Scaricamento del Modello](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: Compilare llama.cpp

Clona il repository:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Compila con supporto ROCm e RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Flag di Build | Scopo |
|-----------|---------|
| `-DGGML_HIP=ON` | Abilita lo stack software ROCm |
| `-DGGML_RPC=ON` | Abilita RPC per l'inferenza distribuita |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Abilita rocWMMA per Flash Attention avanzata sulle GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Ha come target la GPU Ryzen AI Halo (Radeon 8060s) |

Per ulteriori opzioni di build, consulta la [documentazione di build di llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Step 2: Verificare il Rilevamento della GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Output previsto:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Con llama.cpp preparato su ciascun nodo, procedi con [Scaricamento del Modello](#downloading-the-model).
<!-- @os:end -->

## Scaricamento del Modello

Questo playbook utilizza [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), un modello con 358 miliardi di parametri nella quantizzazione `Q4_K_XL` di [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Con questa quantizzazione il modello richiede circa 205 GB di spazio di archiviazione e rientra nella memoria GPU combinata di due nodi Ryzen AI Halo.

Scarica i file GGUF utilizzando la CLI di Hugging Face:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **Nota**: Il download del modello deve essere completato sulla Machine 1 (il controller). I nodi worker RPC non necessitano di una copia locale dei file del modello.

## Avvio del Modello sul Cluster

Il motore RPC (Remote Procedure Call) di llama.cpp consente a una singola istanza di llama.cpp di scaricare i livelli del modello su worker remoti tramite la rete. Una macchina funge da **controller** (Machine 1), gestendo la tokenizzazione, la pianificazione e l'orchestrazione. L'altra macchina esegue un leggero **server RPC** (Machine 2) che espone la propria memoria GPU e capacità di calcolo al controller.

Al momento del caricamento, llama.cpp suddivide il modello tra entrambi i nodi. Una volta caricato, l'inferenza procede come se fosse eseguita su un singolo acceleratore. RPC gestisce i trasferimenti dei tensori e la sincronizzazione dietro le quinte.

### Step 1: Avviare il Server RPC (Machine 2)

Sulla Machine 2, avvia il server RPC per esporre le sue risorse GPU al controller:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Flag | Scopo |
|------|---------|
| `-p` | Porta su cui trasmettere il server RPC |
| `-c` | Abilita una cache locale per i tensori di grandi dimensioni, evitando trasferimenti di rete ripetuti durante il caricamento del modello |
| `--host` | Indirizzo IP a cui associare il server RPC (`0.0.0.0` per tutte le interfacce) |

Per ulteriori opzioni, consulta la [documentazione RPC di llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Step 2: Avviare il Modello (Machine 1)

Con il server RPC in esecuzione sulla Machine 2, avvia l'inferenza dalla Machine 1 utilizzando `llama-cli` o `llama-server`.

#### llama-cli

`llama-cli` fornisce un'interfaccia basata su terminale per interagire direttamente con il modello. È ideale per benchmark, debug e sperimentazione a basso livello.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **Trovare `<RPC_WORKER_IP>`**: Sulla Machine 2, esegui `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: Esegui questo comando nel Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Trovare `<RPC_WORKER_IP>`**: Sulla Machine 2, esegui `ipconfig | findstr /C:"IPv4"` nel Terminal (Powershell) per trovare il suo indirizzo IP locale.

<!-- @os:end -->

Una volta avviato, `llama-cli` mostra l'avanzamento del caricamento del modello ed entra in un prompt interattivo dove puoi chattare direttamente con il modello:

![llama-cli in esecuzione con GLM 4.7 su due nodi](assets/llama-cli-example.png)
#### llama-server

`llama-server` espone lo stesso motore di inferenza tramite un processo server persistente con un'interfaccia web integrata e un'API HTTP compatibile con OpenAI. Questa è l'interfaccia preferita per implementazioni a lungo termine, accesso multi-utente e integrazione con strumenti esterni.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **Come trovare `<RPC_WORKER_IP>`**: Sulla Macchina 2, eseguire `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: Eseguire questo comando in Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Come trovare `<RPC_WORKER_IP>`**: Sulla Macchina 2, eseguire `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) per trovare il suo indirizzo IP locale.
<!-- @os:end -->

Una volta avviato, aprire `http://<HOST_IP>:8081` nel browser per accedere all'interfaccia web integrata. Questa fornisce un'interfaccia di chat basata su browser per interagire con il modello:

![interfaccia web di llama-server in esecuzione con GLM 4.7 su due nodi](assets/llama-server-example.png)

<!-- @os:linux -->
> **Come trovare `<HOST_IP>`**: Sulla Macchina 1, eseguire `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Come trovare `<HOST_IP>`**: Sulla Macchina 1, eseguire `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) per trovare il suo indirizzo IP locale.
<!-- @os:end -->

#### Riferimento dei parametri

| Flag | Scopo |
|------|---------|
| `-m` | Percorso del file del modello GGUF (usare il primo shard, `00001-of-00005`) |
| `-c` | Dimensione del contesto in token. Valori più elevati utilizzano più memoria |
| `-fa on` | Abilita rocWMMA Flash Attention per prestazioni migliorate sulle GPU AMD |
| `-ngl 999` | Trasferisce tutti i livelli del modello alla GPU |
| `--no-mmap` | Disabilita la mappatura della memoria, riducendo i tempi di caricamento quando le dimensioni del modello superano la RAM di sistema ma rientrano nella VRAM |
| `--host` | IP a cui associare `llama-server` (solo `llama-server`) |
| `--port` | Porta su cui servire l'API HTTP (solo `llama-server`) |
| `--rpc` | Elenco separato da virgole degli endpoint dei worker RPC (`IP:port`) |

Per l'utilizzo completo dei parametri, consultare la [documentazione di llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) e la [documentazione di llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Prossimi passi

- **Connettere applicazioni di terze parti**: `llama-server` espone un'API compatibile con OpenAI. Puntare qualsiasi applicazione compatibile con OpenAI (come Open WebUI) a `http://<HOST_IP>:8081` con una chiave API segnaposto qualsiasi (ad es., `none`) per connettersi al proprio cluster
- **Esplorare altri modelli**: Sfogliare i GGUF quantizzati su [Hugging Face](https://huggingface.co/models?search=gguf) per trovare modelli che rientrino nella memoria GPU combinata del proprio cluster
- **Scalare a quattro nodi**: Aggiungere altri due sistemi Ryzen AI Halo come worker RPC aggiuntivi per accedere a modelli su scala di 1 trilione di parametri. Passare endpoint aggiuntivi a `--rpc` come elenco separato da virgole (ad es., `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)