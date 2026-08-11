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

# Clustering di due Ryzen™ AI Halo con RPC

## Panoramica

Il tuo Ryzen™ AI Halo è già in grado di eseguire large language model in locale. Il clustering porta questo concetto oltre, combinando la memoria GPU di più sistemi tramite una rete locale, offrendoti accesso a modelli ancora più grandi con un ragionamento più solido, una generazione di codice migliore e una comprensione multilingue più approfondita, il tutto interamente sul tuo hardware.

Questo playbook ti insegna a effettuare il clustering di due sistemi Ryzen AI Halo utilizzando il motore RPC di llama.cpp e a eseguire GLM 4.7, un modello con 358 miliardi di parametri, su entrambe le macchine con accelerazione AMD ROCm™.

## Cosa imparerai

- Come estendere l'allocazione della VRAM sui sistemi Ryzen AI Halo
- Installazione di llama.cpp con supporto ROCm e RPC
- Configurazione di un worker RPC e avvio dell'inferenza distribuita su due nodi
- Esecuzione di un modello con 358 miliardi di parametri su due sistemi Ryzen AI Halo collegati in rete

## Impostazione della configurazione della memoria

> **Nota**: completa questo passaggio sia sulla Macchina 1 sia sulla Macchina 2.

<!-- @os:windows -->
Su Windows, per eseguire modelli più grandi che richiedono più memoria, è necessario utilizzare l'allocazione AMD Variable Graphics Memory (iGPU VRAM).

Questo può essere fatto aprendo il pannello di controllo AMD Software: Adrenalin Edition e accedendo a: `Performance > Tuning > AMD Variable Graphics Memory`. Imposta il valore su **96 GB**. Riavvia il sistema affinché le modifiche abbiano effetto.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Su Linux, ROCm utilizza un pool di memoria di sistema condivisa, configurato per impostazione predefinita alla metà della memoria di sistema.

Questa quantità può essere aumentata modificando l'impostazione delle pagine del Translation Table Manager (TTM) del kernel, seguendo le istruzioni riportate di seguito. AMD consiglia di impostare la VRAM dedicata minima nel BIOS (0,5 GB).

* Installa l'utility pipx e aggiungi il percorso per i wheel installati con pipx nel percorso di ricerca del sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installa il wheel amd-debug-tools da PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Esegui lo strumento amd-ttm per interrogare le impostazioni correnti relative alla memoria condivisa.
  ```bash
  amd-ttm
  ```

* Riconfigura le impostazioni della memoria condivisa su **120 GB**:
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
| Switch Ethernet 10 Gbps | 1 | Switch centrale che consente la comunicazione tra più nodi Ryzen AI Halo (almeno 2 porte) |
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
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) con il carico di lavoro **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Configurazione dell'hardware fisico

> **Nota**: completa questo passaggio sia sulla Macchina 1 sia sulla Macchina 2.

Collega ciascuna unità Ryzen AI Halo allo switch Ethernet utilizzando un cavo Cat 7 (o superiore). Questo stabilisce il collegamento a 10 Gbps utilizzato per la comunicazione ad alta velocità tra i nodi.
<!-- @os:linux -->
### 1. Determinare le interfacce di rete

Su ciascuna macchina, individua il nome della sua interfaccia di rete e annotalo (di seguito verrà indicato come `IFNAME`). Esegui:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Questo stampa direttamente il nome dell'interfaccia, ad esempio:

```bash
enp191s0
```

### 2. Verificare la velocità dei collegamenti di rete

Conferma che il collegamento sia attivo e funzioni a piena velocità controllando la velocità della tua interfaccia:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: sostituisci `<IFNAME>` con il nome dell'interfaccia di output ottenuto in [1. Determinare le interfacce di rete](#1-determinare-le-interfacce-di-rete)

Dovresti vedere una velocità di `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: se la velocità è inferiore a `10000Mb/s` o il collegamento non si attiva, controlla il collegamento del cavo e verifica che la porta dello switch sia impostata su 10 Gbps. Alcuni switch richiedono la disattivazione dell'auto-negoziazione e l'impostazione manuale della velocità del collegamento; fai riferimento alla documentazione del tuo switch.

<!-- @os:end -->

<!-- @os:windows -->
### Verifica della velocità del collegamento di rete

Su ciascuna macchina, controlla la velocità del collegamento delle tue interfacce di rete:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

La tua interfaccia Ethernet dovrebbe risultare `Up` e funzionare a `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Nota**: se la velocità è inferiore a `10 Gbps` o il collegamento non si attiva, controlla il collegamento del cavo e verifica che la porta dello switch sia impostata su 10 Gbps. Alcuni switch richiedono la disattivazione dell'auto-negoziazione e l'impostazione manuale della velocità del collegamento; fai riferimento alla documentazione del tuo switch.

<!-- @os:end -->

## Installazione di llama.cpp

> **Nota**: completa questo passaggio sia sulla Macchina 1 sia sulla Macchina 2.

Sono disponibili due opzioni di installazione:

- [Opzione 1: Lemonade SDK (consigliata)](#option-1-lemonade-sdk-recommended) - binari precompilati, configurazione più rapida
- [Opzione 2: Build manuale dai sorgenti](#option-2-manual-source-build) - build dai sorgenti con pieno controllo sui flag di compilazione

### Opzione 1: Lemonade SDK (consigliata)

Lemonade SDK fornisce build notturne di llama.cpp con accelerazione AMD ROCm 7, destinate a GPU come gfx1151 (Strix Halo / Ryzen AI Max+ 395) e altre architetture Radeon recenti.

<!-- @os:windows -->
#### Passo 1: Scaricare i binari precompilati

Passa alla pagina dell'ultima release e scarica l'archivio corrispondente alla tua piattaforma e al target GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Scarica il file denominato `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (dove `xxxx` è il numero di build).

#### Passo 2: Estrarre i binari

Decomprimi l'archivio scaricato:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Questa directory ora contiene build abilitate per ROCm di `llama-cli.exe`, `llama-server.exe` e `rpc-server.exe`, precompilate per il tuo sistema Ryzen AI Halo.

#### Passo 3: Verificare il rilevamento della GPU

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
#### Passo 1: Scaricare i binari precompilati

Passa alla pagina dell'ultima release e scarica l'archivio corrispondente alla tua piattaforma e al target GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Scarica il file denominato `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (dove `xxxx` è il numero di build).

#### Passo 2: Estrarre e preparare i binari

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Questa directory ora contiene build abilitate per ROCm di `llama-cli`, `llama-server` e `rpc-server`, precompilate per il tuo sistema Ryzen AI Halo.

#### Passo 3: Verificare il rilevamento della GPU

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
Con llama.cpp preparato su ogni nodo, procedi con [Download del modello](#downloading-the-model).

### Opzione 2: Build manuale dal sorgente

<!-- @os:windows -->
#### Passo 1: Compilare llama.cpp

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

| Flag di build | Scopo |
|-----------|---------|
| `-DGGML_HIP=ON` | Abilita lo stack software ROCm/HIP |
| `-DGGML_RPC=ON` | Abilita RPC per l'inferenza distribuita |
| `-DGPU_TARGETS=gfx1151` | Ha come target la GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Utilizza il sistema di build Ninja |

#### Passo 2: Verificare il rilevamento della GPU

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

#### Passo 3: Aggiungere HIP al tuo path utente

Il passo di build precedente ha impostato `%HIP_PATH%\bin` solo per la sessione corrente. Per rendere le librerie HIP disponibili in qualsiasi terminale (non solo nell'x64 Native Tools Command Prompt), aggiungilo permanentemente al tuo `PATH` utente:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Con llama.cpp preparato su ogni nodo, procedi con [Download del modello](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Passo 1: Compilare llama.cpp

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

| Flag di build | Scopo |
|-----------|---------|
| `-DGGML_HIP=ON` | Abilita lo stack software ROCm |
| `-DGGML_RPC=ON` | Abilita RPC per l'inferenza distribuita |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Abilita rocWMMA per un Flash Attention avanzato sulle GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Ha come target la GPU Ryzen AI Halo (Radeon 8060s) |

Per ulteriori opzioni di build, consulta la [documentazione di build di llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Passo 2: Verificare il rilevamento della GPU

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

Con llama.cpp preparato su ogni nodo, procedi con [Download del modello](#downloading-the-model).
<!-- @os:end -->

## Download del modello

Questo playbook utilizza [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), un modello con 358 miliardi di parametri nella quantizzazione `Q4_K_XL` di [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Con questa quantizzazione il modello richiede circa 205GB di spazio di archiviazione e rientra nella memoria GPU combinata di due nodi Ryzen AI Halo.

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

> **Nota**: il download del modello deve essere completato sulla Macchina 1 (il controller). I nodi worker RPC non necessitano di una copia locale dei file del modello.

## Avvio del modello sul cluster

Il motore RPC (Remote Procedure Call) di llama.cpp consente a una singola istanza di llama.cpp di scaricare i livelli del modello su worker remoti tramite rete. Una macchina funge da **controller** (Macchina 1), gestendo la tokenizzazione, la pianificazione e l'orchestrazione. L'altra macchina esegue un leggero **server RPC** (Macchina 2) che espone la propria memoria GPU e la capacità di calcolo al controller.

Al momento del caricamento, llama.cpp suddivide il modello su entrambi i nodi. Una volta caricato, l'inferenza procede come se fosse eseguita su un unico acceleratore. RPC gestisce i trasferimenti di tensori e la sincronizzazione dietro le quinte.

### Passo 1: Avviare il server RPC (Macchina 2)

Sulla Macchina 2, avvia il server RPC per esporre le sue risorse GPU al controller:
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Flag | Scopo |
|------|---------|
| `-p` | Porta su cui trasmettere il server RPC |
| `-c` | Abilita una cache locale per i tensori di grandi dimensioni, evitando trasferimenti di rete ripetuti durante il caricamento del modello |
| `--host` | Indirizzo IP a cui associare il server RPC (`0.0.0.0` per tutte le interfacce) |

Per ulteriori opzioni, consulta la [documentazione RPC di llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Passo 2: Avviare il modello (Macchina 1)

Con il server RPC in esecuzione sulla Macchina 2, avvia l'inferenza dalla Macchina 1 utilizzando `llama-cli` oppure `llama-server`.

#### llama-cli

`llama-cli` fornisce un'interfaccia basata su terminale per interagire direttamente con il modello. È ideale per il benchmarking, il debug e la sperimentazione a basso livello.

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

> **Trovare `<RPC_WORKER_IP>`**: sulla Macchina 2, esegui `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: esegui questo comando nel Terminale (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Trovare `<RPC_WORKER_IP>`**: sulla Macchina 2, esegui `ipconfig | findstr /C:"IPv4"` nel Terminale (Powershell) per trovare il suo indirizzo IP locale.

<!-- @os:end -->

Una volta in esecuzione, `llama-cli` mostra l'avanzamento del caricamento del modello e apre un prompt interattivo in cui puoi chattare direttamente con il modello:

![llama-cli in esecuzione con GLM 4.7 su due nodi](assets/llama-cli-example.png)
#### llama-server

`llama-server` espone lo stesso motore di inferenza attraverso un processo server persistente con un'interfaccia web integrata e un'API HTTP compatibile con OpenAI. Questa è l'interfaccia preferita per distribuzioni di lunga durata, accesso multi-utente e integrazione con strumenti esterni.

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

> **Individuazione di `<RPC_WORKER_IP>`**: Sulla Macchina 2, eseguire `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: Eseguire questo comando nel Terminale (Powershell).

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

> **Individuazione di `<RPC_WORKER_IP>`**: Sulla Macchina 2, eseguire `ipconfig | findstr /C:"IPv4"` nel Terminale (Powershell) per trovare il suo indirizzo IP locale.
<!-- @os:end -->

Una volta avviato, aprire `http://<HOST_IP>:8081` nel browser per accedere all'interfaccia web integrata. Questa fornisce un'interfaccia di chat basata su browser per interagire con il modello:

![Interfaccia web di llama-server in esecuzione con GLM 4.7 su due nodi](assets/llama-server-example.png)

<!-- @os:linux -->
> **Individuazione di `<HOST_IP>`**: Sulla Macchina 1, eseguire `hostname -I | awk '{print $1}'` per trovare il suo indirizzo IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Individuazione di `<HOST_IP>`**: Sulla Macchina 1, eseguire `ipconfig | findstr /C:"IPv4"` nel Terminale (Powershell) per trovare il suo indirizzo IP locale.
<!-- @os:end -->

#### Riferimento parametri

| Flag | Scopo |
|------|---------|
| `-m` | Percorso del file modello GGUF (usare il primo shard, `00001-of-00005`) |
| `-c` | Dimensione del contesto in token. Valori più grandi utilizzano più memoria |
| `-fa on` | Abilita rocWMMA Flash Attention per prestazioni migliorate sulle GPU AMD |
| `-ngl 999` | Trasferisce tutti i layer del modello alla GPU |
| `--no-mmap` | Disabilita il memory-mapping, riducendo i tempi di caricamento quando la dimensione del modello supera la RAM di sistema ma rientra nella VRAM |
| `--host` | IP a cui associare `llama-server` (solo `llama-server`) |
| `--port` | Porta su cui servire l'API HTTP (solo `llama-server`) |
| `--rpc` | Elenco separato da virgole di endpoint worker RPC (`IP:port`) |

Per l'utilizzo completo dei parametri, fare riferimento alla [documentazione di llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) e alla [documentazione di llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Prossimi passi

- **Connettere applicazioni di terze parti**: `llama-server` espone un'API compatibile con OpenAI. Puntare qualsiasi applicazione compatibile con OpenAI (come Open WebUI) verso `http://<HOST_IP>:8081` con una chiave API segnaposto qualsiasi (ad es. `none`) per connettersi al proprio cluster
- **Esplorare altri modelli**: Sfogliare i GGUF quantizzati su [Hugging Face](https://huggingface.co/models?search=gguf) per trovare modelli che rientrano nella memoria GPU combinata del proprio cluster
- **Scalare a quattro nodi**: Aggiungere altri due sistemi Ryzen AI Halo come worker RPC aggiuntivi per accedere a modelli su scala di 1 trilione di parametri. Passare endpoint aggiuntivi a `--rpc` come elenco separato da virgole (ad es. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)