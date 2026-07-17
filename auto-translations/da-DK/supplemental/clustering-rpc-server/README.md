<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering af to Ryzen™ AI Halos med RPC

## Oversigt

Din Ryzen™ AI Halo er allerede i stand til at køre store sprogmodeller lokalt. Clustering tager dette videre ved at kombinere GPU-hukommelsen fra flere systemer over et lokalt netværk, hvilket giver dig adgang til endnu større modeller med stærkere ræsonnering, bedre kodegenerering og dybere flersproget forståelse – alt sammen udelukkende på din egen hardware.

Dette playbook lærer dig, hvordan du klustrer to Ryzen AI Halo-systemer ved hjælp af llama.cpp's RPC-motor og kører GLM 4.7, en model med 358B parametre, på tværs af begge maskiner med AMD ROCm™-acceleration.

## Hvad du vil lære

- Hvordan du udvider VRAM-allokeringen på Ryzen AI Halo-systemer
- Installation af llama.cpp med ROCm og RPC-understøttelse
- Konfiguration af en RPC-worker og lancering af distribueret inferens på tværs af to noder
- Kørsel af en model med 358B parametre på tværs af to netværksforbundne Ryzen AI Halo-systemer

## Indstilling af hukommelseskonfigurationen

> **Bemærk**: Gennemfør dette trin på både Maskine 1 og Maskine 2.

<!-- @os:windows -->
På Windows skal vi bruge AMD Variable Graphics Memory (iGPU VRAM)-allokeringen for at køre større modeller, der kræver mere hukommelse.

Dette kan gøres ved at åbne AMD Software: Adrenalin Edition-kontrolpanelet og navigere til: `Performance > Tuning > AMD Variable Graphics Memory`. Sæt værdien til **96 GB**. Genstart venligst systemet for at ændringerne træder i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
På Linux anvender ROCm en delt systemhukommelsespulje, og denne pulje er som standard konfigureret til halvdelen af systemhukommelsen.

Denne mængde kan øges ved at ændre kernelens Translation Table Manager (TTM)-sideindstilling med følgende instruktioner. AMD anbefaler at indstille den minimale dedikerede VRAM i BIOS (0,5 GB).

* Installer pipx-hjælpeprogrammet og tilføj stien til pipx-installerede wheels i systemets søgesti.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installer amd-debug-tools-wheelet fra PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kør amd-ttm-værktøjet for at forespørge de aktuelle indstillinger for delt hukommelse.
  ```bash
  amd-ttm
  ```

* Rekonfigurer indstillingerne for delt hukommelse til **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Genstart systemet for at ændringerne træder i kraft.


<!-- @os:end -->
<!-- @device:halo_box -->
## Kontroller for softwareopdateringer

<!-- @require:software-update -->
<!-- @device:end -->
## Forudsætninger

### Hardware

Dette playbook kræver to Ryzen AI Halo-enheder og én Ethernet-switch, forbundet i en stjerne-topologi, hvor hver enhed er kablet direkte til switchen.

| Komponent | Antal | Beskrivelse |
|-----------|-------|-------------|
| Ryzen AI Halo | 2 | Beregningsnoder, der udgør klusteret |
| 10Gbps Ethernet-switch | 1 | Central switch til at muliggøre kommunikation mellem flere Ryzen AI Halo-noder (mindst 2 porte) |
| Ethernet-kabel | 2 | Forbinder hver Halo-enhed til switchen (Cat 7 eller højere anbefales) |

> **Bemærk**: To Ethernet-switchporte er nødvendige for at forbinde de to Ryzen AI Halo-enheder. En tredje port er nødvendig, hvis du tilgår modellen fra en separat klientmaskine i stedet for fra en af Halo-enhederne.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Installer venligst:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) med arbejdsbyrden **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fysisk hardwareopsætning

> **Bemærk**: Gennemfør dette trin på både Maskine 1 og Maskine 2.

Forbind hver Ryzen AI Halo-enhed til Ethernet-switchen med et Cat 7-kabel (eller højere). Dette etablerer den 10Gbps-forbindelse, der bruges til højthastighedskommunikation mellem noderne.
<!-- @os:linux -->
### 1. Bestem netværksgrænseflader

På hver maskine skal du finde navnet på dens netværksgrænseflade og notere det (det vil blive refereret til nedenfor som `IFNAME`). Kør:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dette udskriver grænsefladenavnet direkte, for eksempel:

```bash
enp191s0
```

### 2. Verificer netværksforbindelseshastigheder

Bekræft, at forbindelsen er aktiv og kører ved fuld hastighed ved at kontrollere hastigheden på din grænseflade:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Bemærk**: Erstat `<IFNAME>` med det outputgrænsefladenavnet fra [1. Bestem netværksgrænseflader](#1-determine-network-interfaces)

Du bør se en hastighed på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Bemærk**: Hvis hastigheden er lavere end `10000Mb/s`, eller forbindelsen ikke kommer op, skal du kontrollere kabelopkoblingen og bekræfte, at switchporten er indstillet til 10Gbps. Nogle switches kræver, at auto-forhandling deaktiveres, og at forbindelseshastigheden indstilles manuelt; se din switches dokumentation.

<!-- @os:end -->

<!-- @os:windows -->
### Verificer netværksforbindelseshastighed

På hver maskine skal du kontrollere forbindelseshastigheden på dine netværksgrænseflader:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Din Ethernet-grænseflade bør være `Up` og køre ved `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Bemærk**: Hvis hastigheden er lavere end `10 Gbps`, eller forbindelsen ikke kommer op, skal du kontrollere kabelopkoblingen og bekræfte, at switchporten er indstillet til 10Gbps. Nogle switches kræver, at auto-forhandling deaktiveres, og at forbindelseshastigheden indstilles manuelt; se din switches dokumentation.

<!-- @os:end -->

## Installation af llama.cpp

> **Bemærk**: Gennemfør dette trin på både Maskine 1 og Maskine 2.

To installationsmuligheder er tilgængelige:

- [Mulighed 1: Lemonade SDK (Anbefalet)](#option-1-lemonade-sdk-recommended) - færdigbyggede binære filer, hurtigste opsætning
- [Mulighed 2: Manuel kildebygge](#option-2-manual-source-build) - byg fra kilde med fuld kontrol over byggeflags

### Mulighed 1: Lemonade SDK (Anbefalet)

Lemonade SDK leverer nightly builds af llama.cpp med AMD ROCm 7-acceleration, der målretter GPU'er som gfx1151 (Strix Halo / Ryzen AI Max+ 395) og andre nyere Radeon-arkitekturer.

<!-- @os:windows -->
#### Trin 1: Download de færdigbyggede binære filer

Naviger til den seneste udgivelsesside og download arkivet, der matcher din platform og GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download filen med navnet `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (hvor `xxxx` er byggenummeret).

#### Trin 2: Udpak de binære filer

Udpak det downloadede arkiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Denne mappe indeholder nu ROCm-aktiverede builds af `llama-cli.exe`, `llama-server.exe` og `rpc-server.exe`, forudkompileret til dit Ryzen AI Halo-system.

#### Trin 3: Verificer GPU-detektion

```bash
.\llama-cli.exe --list-devices
```

Forventet output:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Trin 1: Download de færdigbyggede binære filer

Naviger til den seneste udgivelsesside og download arkivet, der matcher din platform og GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download filen med navnet `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (hvor `xxxx` er byggenummeret).

#### Trin 2: Udpak og forbered de binære filer

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Denne mappe indeholder nu ROCm-aktiverede builds af `llama-cli`, `llama-server` og `rpc-server`, forudkompileret til dit Ryzen AI Halo-system.

#### Trin 3: Verificer GPU-detektion

```bash
./llama-cli --list-devices
```

Forventet output:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Med llama.cpp forberedt på hver node skal du fortsætte til [Download af modellen](#downloading-the-model).

### Mulighed 2: Manuel kildebygge

<!-- @os:windows -->
#### Trin 1: Byg llama.cpp

Åbn **x64 Native Tools Command Prompt** (installeret med Visual Studio Build Tools) og klon repositoriet:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Tilføj HIP til din sti og byg med ROCm og RPC-understøttelse:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Byggeflag | Formål |
|-----------|--------|
| `-DGGML_HIP=ON` | Aktiverer ROCm/HIP-softwarestakken |
| `-DGGML_RPC=ON` | Aktiverer RPC til distribueret inferens |
| `-DGPU_TARGETS=gfx1151` | Målretter Ryzen AI Halo GPU (Radeon 8060s) |
| `-G Ninja` | Bruger Ninja-byggesystemet |

#### Trin 2: Verificer GPU-detektion

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Forventet output:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Trin 3: Tilføj HIP til din brugersti

Byggetrinnet ovenfor indstillede `%HIP_PATH%\bin` kun for den aktuelle session. For at gøre HIP-bibliotekerne tilgængelige i enhver terminal (ikke kun x64 Native Tools Command Prompt) skal du tilføje det permanent til din bruger-`PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Med llama.cpp forberedt på hver node skal du fortsætte til [Download af modellen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Trin 1: Byg llama.cpp

Klon repositoriet:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Byg med ROCm og RPC-understøttelse:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Byggeflag | Formål |
|-----------|--------|
| `-DGGML_HIP=ON` | Aktiverer ROCm-softwarestakken |
| `-DGGML_RPC=ON` | Aktiverer RPC til distribueret inferens |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Aktiverer rocWMMA til forbedret Flash Attention på AMD GPU'er |
| `-DAMDGPU_TARGETS="gfx1151"` | Målretter Ryzen AI Halo GPU (Radeon 8060s) |

For flere byggemuligheder, se [llama.cpp-byggedokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Trin 2: Verificer GPU-detektion

```bash
cd rocm/bin
./llama-cli --list-devices
```

Forventet output:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Med llama.cpp forberedt på hver node skal du fortsætte til [Download af modellen](#downloading-the-model).
<!-- @os:end -->

## Download af modellen

Dette playbook bruger [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), en model med 358B parametre i `Q4_K_XL`-kvantiseringen fra [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Ved denne kvantisering kræver modellen cirka 205 GB lagerplads og passer inden for den kombinerede GPU-hukommelse fra to Ryzen AI Halo-noder.

Download GGUF-filerne ved hjælp af Hugging Face CLI:
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

> **Bemærk**: Modeldownloaden skal gennemføres på Maskine 1 (controlleren). RPC-worker-noderne behøver ikke en lokal kopi af modelfilerne.

## Lancering af modellen på klusteret

llama.cpp RPC-motoren (Remote Procedure Call) giver en enkelt llama.cpp-instans mulighed for at aflaste modellag til fjernworkere over netværket. Én maskine fungerer som **controller** (Maskine 1), der håndterer tokenisering, planlægning og orkestrering. Den anden maskine kører en letvægts **RPC-server** (Maskine 2), der eksponerer sin GPU-hukommelse og beregningskraft til controlleren.

Ved indlæsningstidspunktet opdeler llama.cpp modellen på tværs af begge noder. Når den er indlæst, forløber inferens, som om den kørte på en enkelt accelerator. RPC håndterer tensoroverførsler og synkronisering i baggrunden.

### Trin 1: Start RPC-serveren (Maskine 2)

På Maskine 2 skal du starte RPC-serveren for at eksponere dens GPU-ressourcer til controlleren:
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

| Flag | Formål |
|------|--------|
| `-p` | Port til at udsende RPC-serveren på |
| `-c` | Aktiverer en lokal cache til store tensorer, hvilket undgår gentagne netværksoverførsler under modelindlæsning |
| `--host` | IP-adresse til at binde RPC-serveren til (`0.0.0.0` for alle grænseflader) |

For flere muligheder, se [llama.cpp RPC-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Trin 2: Lancér modellen (Maskine 1)

Med RPC-serveren kørende på Maskine 2 skal du lancere inferens fra Maskine 1 ved hjælp af enten `llama-cli` eller `llama-server`.

#### llama-cli

`llama-cli` giver en terminalbaseret grænseflade til direkte interaktion med modellen. Den er ideel til benchmarking, fejlfinding og lavniveaueksperimenter.

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

> **Find `<RPC_WORKER_IP>`**: På Maskine 2 skal du køre `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse.
<!-- @os:end -->

<!-- @os:windows -->
> **Bemærk**: Kør denne kommando i Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Find `<RPC_WORKER_IP>`**: På Maskine 2 skal du køre `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for at finde dens lokale IP-adresse.

<!-- @os:end -->

Når den kører, viser `llama-cli` modelindlæsningsfremskridt og åbner en interaktiv prompt, hvor du kan chatte direkte med modellen:

![llama-cli kørende GLM 4.7 på tværs af to noder](assets/llama-cli-example.png)

#### llama-server

`llama-server` eksponerer den samme inferensmotor gennem en vedvarende serverproces med en integreret web-UI og en OpenAI-kompatibel HTTP API. Dette er den foretrukne grænseflade til længerevarende deployments, flerbrugeradgang og integration med eksternt værktøj.

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

> **Find `<RPC_WORKER_IP>`**: På Maskine 2 skal du køre `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse.
<!-- @os:end -->

<!-- @os:windows -->
> **Bemærk**: Kør denne kommando i Terminal (Powershell).

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

> **Find `<RPC_WORKER_IP>`**: På Maskine 2 skal du køre `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for at finde dens lokale IP-adresse.
<!-- @os:end -->

Når den er startet, skal du åbne `http://<HOST_IP>:8081` i din browser for at få adgang til den indbyggede web-UI. Dette giver en browserbaseret chatgrænseflade til interaktion med modellen:

![llama-server web-UI kørende GLM 4.7 på tværs af to noder](assets/llama-server-example.png)

<!-- @os:linux -->
> **Find `<HOST_IP>`**: På Maskine 1 skal du køre `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse.
<!-- @os:end -->

<!-- @os:windows -->
> **Find `<HOST_IP>`**: På Maskine 1 skal du køre `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for at finde dens lokale IP-adresse.
<!-- @os:end -->

#### Parameterreference

| Flag | Formål |
|------|--------|
| `-m` | Sti til GGUF-modelfilen (brug det første shard, `00001-of-00005`) |
| `-c` | Kontekststørrelse i tokens. Større værdier bruger mere hukommelse |
| `-fa on` | Aktiverer rocWMMA Flash Attention for forbedret ydeevne på AMD GPU'er |
| `-ngl 999` | Aflaster alle modellag til GPU'en |
| `--no-mmap` | Deaktiverer hukommelsesmapping, hvilket reducerer indlæsningstider, når modelstørrelsen overstiger system-RAM, men passer i VRAM |
| `--host` | IP til at binde `llama-server` til (kun `llama-server`) |
| `--port` | Port til at betjene HTTP API'en på (kun `llama-server`) |
| `--rpc` | Kommasepareret liste over RPC-worker-endepunkter (`IP:port`) |

For fuld parameterbrug, se [llama-cli-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) og [llama-server-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Næste skridt

- **Forbind tredjepartsapplikationer**: `llama-server` eksponerer en OpenAI-kompatibel API. Peg enhver OpenAI-kompatibel applikation (såsom Open WebUI) på `http://<HOST_IP>:8081` med en vilkårlig placeholder-API-nøgle (f.eks. `none`) for at oprette forbindelse til dit kluster
- **Udforsk andre modeller**: Gennemse kvantiserede GGUFs på [Hugging Face](https://huggingface.co/models?search=gguf) for at finde modeller, der passer inden for dit klusters kombinerede GPU-hukommelse
- **Skaler til fire noder**: Tilføj to yderligere Ryzen AI Halo-systemer som ekstra RPC-workers for at få adgang til modeller på 1 billion parameter-skalaen. Send yderligere endepunkter til `--rpc` som en kommasepareret liste (f.eks. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)