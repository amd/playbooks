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

# Clustering di quattro Ryzen™ AI Halo con RPC

## Panoramica

Il tuo Ryzen™ AI Halo è già in grado di eseguire modelli linguistici di grandi dimensioni in locale. Il clustering porta questa capacità oltre, combinando la memoria GPU di più sistemi tramite una rete locale, offrendoti accesso a modelli ancora più grandi con un ragionamento più solido, una migliore generazione di codice e una comprensione multilingue più approfondita, il tutto interamente sul tuo hardware.

Questa guida ti insegna come mettere in cluster quattro sistemi Ryzen AI Halo utilizzando il motore RPC di llama.cpp ed eseguire Kimi K2.6, un grande modello mixture-of-experts, su tutte e quattro le macchine con l'accelerazione AMD ROCm™.

## Cosa Imparerai

- Come estendere l'allocazione di VRAM sui sistemi Ryzen AI Halo
- Come installare llama.cpp con supporto ROCm e RPC
- Come configurare i worker RPC e avviare l'inferenza distribuita su quattro nodi
- Come eseguire un modello con 1T di parametri su quattro sistemi Ryzen AI Halo collegati in rete

## Impostazione della Configurazione della Memoria

> **Nota**: Completa questo passaggio su tutte e quattro le macchine (Macchina 1 fino a Macchina 4).

<!-- @os:windows -->
Su Windows, per eseguire modelli più grandi che richiedono più memoria, è necessario utilizzare l'allocazione AMD Variable Graphics Memory (iGPU VRAM).

Questo può essere fatto aprendo il pannello di controllo AMD Software: Adrenalin Edition e navigando su: `Performance > Tuning > AMD Variable Graphics Memory`. Imposta il valore su **96 GB**. Riavvia il sistema affinché le modifiche abbiano effetto.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Su Linux, ROCm utilizza un pool di memoria di sistema condiviso, e questo pool è configurato per impostazione predefinita a metà della memoria di sistema.

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

* Esegui lo strumento amd-ttm per interrogare le impostazioni attuali per la memoria condivisa.
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
## Verifica degli Aggiornamenti Software

<!-- @require:software-update -->
<!-- @device:end -->
## Prerequisiti

### Hardware

Questa guida richiede quattro unità Ryzen AI Halo e uno switch Ethernet, collegati in una topologia a stella con ogni unità cablata direttamente allo switch.

| Componente | Quantità | Descrizione |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Nodi di calcolo che formano il cluster |
| Switch Ethernet 10Gbps | 1 | Switch centrale per consentire la comunicazione multi-nodo dei Ryzen AI Halo (almeno 4 porte) |
| Cavo Ethernet | 4 | Collega ogni unità Halo allo switch (Cat 7 o superiore consigliato) |

> **Nota**: Sono necessarie quattro porte dello switch Ethernet per collegare le quattro unità Ryzen AI Halo. È necessaria una quinta porta se accedi al modello da una macchina client separata anziché da una delle unità Halo.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Installa:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) con il workload **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Configurazione dell'Hardware Fisico

> **Nota**: Completa questo passaggio su tutte e quattro le macchine (Macchina 1 fino a Macchina 4).

Collega ciascuna unità Ryzen AI Halo allo switch Ethernet utilizzando un cavo Cat 7 (o superiore). Questo stabilisce il collegamento a 10Gbps utilizzato per la comunicazione ad alta velocità tra i nodi.
<!-- @os:linux -->
### 1. Determinare le Interfacce di Rete

Su ciascuna macchina, individua il nome della sua interfaccia di rete e annotalo (verrà indicato di seguito come `IFNAME`). Esegui:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Questo stampa direttamente il nome dell'interfaccia, ad esempio:

```bash
enp191s0
```

### 2. Verificare le Velocità del Collegamento di Rete

Conferma che il collegamento sia attivo e funzioni alla massima velocità controllando la velocità della tua interfaccia:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: Sostituisci `<IFNAME>` con il nome dell'interfaccia di output ottenuto in [1. Determinare le Interfacce di Rete](#1-determine-network-interfaces)

Dovresti vedere una velocità di `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: Se la velocità è inferiore a `10000Mb/s` o il collegamento non si attiva, controlla il collegamento del cavo e conferma che la porta dello switch sia impostata su 10Gbps. Alcuni switch richiedono la disattivazione dell'auto-negoziazione e l'impostazione manuale della velocità del collegamento; consulta la documentazione del tuo switch.

<!-- @os:end -->

<!-- @os:windows -->
### Verifica della Velocità del Collegamento di Rete

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

> **Nota**: Se la velocità è inferiore a `10 Gbps` o il collegamento non si attiva, controlla il collegamento del cavo e conferma che la porta dello switch sia impostata su 10Gbps. Alcuni switch richiedono la disattivazione dell'auto-negoziazione e l'impostazione manuale della velocità del collegamento; consulta la documentazione del tuo switch.

<!-- @os:end -->

## Installazione di llama.cpp

> **Nota**: Completa questo passaggio su tutte e quattro le macchine (Macchina 1 fino a Macchina 4).

Sono disponibili due opzioni di installazione:

- [Opzione 1: Lemonade SDK (Consigliata)](#option-1-lemonade-sdk-recommended) - binari precompilati, configurazione più rapida
- [Opzione 2: Build Manuale da Sorgente](#option-2-manual-source-build) - build da sorgente con pieno controllo sui flag di build

### Opzione 1: Lemonade SDK (Consigliata)

Il Lemonade SDK fornisce build notturne di llama.cpp con accelerazione AMD ROCm 7, mirate a GPU come gfx1151 (Strix Halo / Ryzen AI Max+ 395) e altre architetture Radeon recenti.

<!-- @os:windows -->
#### Passaggio 1: Scarica i binari precompilati

Vai alla pagina dell'ultima release e scarica l'archivio corrispondente alla tua piattaforma e al target GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Scarica il file denominato `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (dove `xxxx` è il numero di build).

#### Passaggio 2: Estrai i binari

Estrai l'archivio scaricato:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Questa directory ora contiene build abilitate per ROCm di `llama-cli.exe`, `llama-server.exe` e `ggml-rpc-server.exe`, precompilate per il tuo sistema Ryzen AI Halo.

#### Passaggio 3: Verifica il rilevamento della GPU

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
#### Passaggio 1: Scarica i binari precompilati

Vai alla pagina dell'ultima release e scarica l'archivio corrispondente alla tua piattaforma e al target GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Scarica il file denominato `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (dove `xxxx` è il numero di build).

#### Passaggio 2: Estrai e prepara i binari

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Questa directory ora contiene build abilitate per ROCm di `llama-cli`, `llama-server` e `rpc-server`, precompilate per il tuo sistema Ryzen AI Halo.

#### Passaggio 3: Verifica il rilevamento della GPU

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
Dopo aver preparato llama.cpp su ciascun nodo, procedi con [Scaricamento del modello](#downloading-the-model).

### Opzione 2: Build manuale dai sorgenti

<!-- @os:windows -->
#### Passaggio 1: Compila llama.cpp

Apri il **x64 Native Tools Command Prompt** (installato con Visual Studio Build Tools) e clona il repository:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Aggiungi HIP al tuo percorso e compila con supporto ROCm e RPC:

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

#### Passaggio 2: Verifica il rilevamento della GPU

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

#### Passaggio 3: Aggiungi HIP al tuo percorso utente

Il passaggio di build precedente ha impostato `%HIP_PATH%\bin` solo per la sessione corrente. Per rendere disponibili le librerie HIP in qualsiasi terminale (non solo nel x64 Native Tools Command Prompt), aggiungilo in modo permanente al tuo `PATH` utente:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Dopo aver preparato llama.cpp su ciascun nodo, procedi con [Scaricamento del modello](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Passaggio 1: Compila llama.cpp

Clona il repository:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Compila con supporto ROCm e RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Flag di build | Scopo |
|-----------|---------|
| `-DGGML_HIP=ON` | Abilita lo stack software ROCm |
| `-DGGML_RPC=ON` | Abilita RPC per l'inferenza distribuita |
| `-DAMDGPU_TARGETS="gfx1151"` | Ha come target la GPU Ryzen AI Halo (Radeon 8060s) |

Per ulteriori opzioni di build, consulta la [documentazione di build di llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Passaggio 2: Verifica il rilevamento della GPU

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

Dopo aver preparato llama.cpp su ciascun nodo, procedi con [Scaricamento del modello](#downloading-the-model).
<!-- @os:end -->

## Scaricamento del modello

Questo playbook utilizza [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) nella quantizzazione `UD-Q2_K_XL` di [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Questa quantizzazione rientra nella memoria GPU combinata di quattro nodi Ryzen AI Halo.

Scarica i file GGUF utilizzando la CLI di Hugging Face:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **Nota**: il download del modello deve essere completato sulla Macchina 1 (il controller). I nodi worker RPC (Macchine 2, 3 e 4) non necessitano di una copia locale dei file del modello.

## Avvio del modello sul cluster

Il motore RPC (Remote Procedure Call) di llama.cpp consente a una singola istanza di llama.cpp di scaricare i livelli del modello su worker remoti tramite rete. Una macchina agisce come **controller** (Macchina 1), gestendo la tokenizzazione, la pianificazione e l'orchestrazione. Le altre tre macchine eseguono ciascuna un leggero **server RPC** (Macchine 2, 3 e 4) che espone la propria memoria GPU e la capacità di calcolo al controller.

Al momento del caricamento, llama.cpp suddivide il modello tra tutti e quattro i nodi. Una volta caricato, l'inferenza procede come se venisse eseguita su un singolo acceleratore. RPC gestisce i trasferimenti dei tensori e la sincronizzazione dietro le quinte.

### Passaggio 1: Avvia i server RPC (Macchine 2, 3 e 4)

Su ciascuna delle Macchine 2, 3 e 4, avvia il server RPC per esporre le sue risorse GPU al controller:
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
| `-c` | Abilita una cache locale per i tensori di grandi dimensioni, evitando trasferimenti ripetuti sulla rete durante il caricamento del modello |
| `--host` | Indirizzo IP a cui associare il server RPC (`0.0.0.0` per tutte le interfacce) |

Per ulteriori opzioni, consulta la [documentazione RPC di llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Passaggio 2: Avvia il modello (Macchina 1)

Con i server RPC in esecuzione sulle Macchine 2, 3 e 4, avvia l'inferenza dalla Macchina 1 utilizzando `llama-cli` o `llama-server`.
#### llama-cli

`llama-cli` fornisce un'interfaccia basata su terminale per interagire direttamente con il modello. È ideale per il benchmarking, il debugging e la sperimentazione a basso livello.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Individuazione di `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: su ciascuna delle Macchine 2, 3 e 4, eseguire `hostname -I | awk '{print $1}'` per trovare il proprio indirizzo IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: eseguire questo comando in Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Individuazione di `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: su ciascuna delle Macchine 2, 3 e 4, eseguire `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) per trovare il proprio indirizzo IP locale.

<!-- @os:end -->

Una volta avviato, `llama-cli` mostra l'avanzamento del caricamento del modello e apre un prompt interattivo in cui è possibile conversare direttamente con il modello:

![llama-cli in esecuzione con Kimi K2.6 su quattro nodi](assets/llama-cli-example.png)

#### llama-server

`llama-server` espone lo stesso motore di inferenza tramite un processo server persistente con un'interfaccia web integrata e un'API HTTP compatibile con OpenAI. Questa è l'interfaccia preferita per le distribuzioni di lunga durata, l'accesso multiutente e l'integrazione con strumenti esterni.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Individuazione di `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: su ciascuna delle Macchine 2, 3 e 4, eseguire `hostname -I | awk '{print $1}'` per trovare il proprio indirizzo IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: eseguire questo comando in Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Individuazione di `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: su ciascuna delle Macchine 2, 3 e 4, eseguire `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) per trovare il proprio indirizzo IP locale.
<!-- @os:end -->

Una volta avviato, aprire `http://<HOST_IP>:8081` nel browser per accedere all'interfaccia web integrata. Questa fornisce un'interfaccia di chat basata su browser per interagire con il modello:

![Interfaccia web di llama-server in esecuzione con Kimi K2.6 su quattro nodi](assets/llama-server-example.png)

<!-- @os:linux -->
> **Individuazione di `<HOST_IP>`**: sulla Macchina 1, eseguire `hostname -I | awk '{print $1}'` per trovare il proprio indirizzo IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Individuazione di `<HOST_IP>`**: sulla Macchina 1, eseguire `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) per trovare il proprio indirizzo IP locale.
<!-- @os:end -->

#### Riferimento dei parametri

| Flag | Scopo |
|------|---------|
| `-m` | Percorso del file modello GGUF (utilizzare il primo shard, `00001-of-00008`) |
| `-c` | Dimensione del contesto in token. Valori più elevati utilizzano più memoria |
| `-fa on` | Abilita rocWMMA Flash Attention per prestazioni migliorate sulle GPU AMD |
| `-ngl 999` | Trasferisce tutti i livelli del modello sulla GPU |
| `-lm none` | Imposta la modalità di caricamento del modello su `none`, disabilitando il memory-mapping per ridurre i tempi di caricamento quando la dimensione del modello supera la RAM di sistema ma rientra nella VRAM |
| `-b` | Dimensione del batch logico in token. Impostare a 4096 bilancia throughput e utilizzo della memoria tra i nodi |
| `-ub` | Dimensione del batch fisico (micro) per l'elaborazione del prompt. Farla corrispondere a `-b` evita overhead di suddivisione non necessari |
| `--host` | IP a cui associare `llama-server` (solo `llama-server`) |
| `--port` | Porta su cui servire l'API HTTP (solo `llama-server`) |
| `--rpc` | Elenco separato da virgole di endpoint RPC worker (`IP:port`) |

Per l'utilizzo completo dei parametri, fare riferimento alla [documentazione di llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) e alla [documentazione di llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Passaggi successivi

- **Connettere applicazioni di terze parti**: `llama-server` espone un'API compatibile con OpenAI. Puntare qualsiasi applicazione compatibile con OpenAI (come Open WebUI) a `http://<HOST_IP>:8081` con una chiave API segnaposto qualsiasi (ad es. `none`) per connettersi al proprio cluster
- **Esplorare altri modelli**: sfogliare i GGUF quantizzati su [Hugging Face](https://huggingface.co/models?search=gguf) per trovare modelli che rientrino nella memoria GPU combinata del proprio cluster
- **Espandere oltre quattro nodi**: aggiungere ulteriori sistemi Ryzen AI Halo come RPC worker aggiuntivi per accedere a modelli oltre la scala di 1 trilione di parametri. Passare endpoint aggiuntivi a `--rpc` come elenco separato da virgole (ad es. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)