<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Sammenkobling af to Ryzen™ AI Halo-systemer med RPC

## Oversigt

Din Ryzen™ AI Halo er allerede i stand til at køre store sprogmodeller lokalt. Ved at klynge (clustre) flere systemer sammen kan du gå et skridt videre og kombinere GPU-hukommelsen fra flere systemer over et lokalt netværk, hvilket giver dig adgang til endnu større modeller med stærkere ræsonnementsevner, bedre kodegenerering og dybere flersproget forståelse – alt sammen på din egen hardware.

Denne playbook viser dig, hvordan du klynger to Ryzen AI Halo-systemer sammen ved hjælp af llama.cpp's RPC-motor og kører GLM 4.7, en model med 358 milliarder parametre, på tværs af begge maskiner med AMD ROCm™-acceleration.

## Hvad du vil lære

- Hvordan du udvider VRAM-tildelingen på Ryzen AI Halo-systemer
- Installation af llama.cpp med ROCm- og RPC-understøttelse
- Konfiguration af en RPC-worker og opstart af distribueret inferens på tværs af to noder
- Kørsel af en model med 358 milliarder parametre på tværs af to netværksforbundne Ryzen AI Halo-systemer

## Indstilling af hukommelseskonfigurationen

> **Bemærk**: Udfør dette trin på både Maskine 1 og Maskine 2.

<!-- @os:windows -->
På Windows skal vi for at kunne køre større modeller, der kræver mere hukommelse, bruge tildelingen af AMD Variable Graphics Memory (iGPU VRAM).

Dette kan gøres ved at åbne kontrolpanelet AMD Software: Adrenalin Edition og navigere til: `Performance > Tuning > AMD Variable Graphics Memory`. Sæt værdien til **96 GB**. Genstart systemet, for at ændringerne træder i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
På Linux benytter ROCm en delt systemhukommelsespulje, og denne pulje er som standard konfigureret til halvdelen af systemhukommelsen.

Denne mængde kan øges ved at ændre kernens Translation Table Manager (TTM) page-indstilling ved hjælp af følgende instruktioner. AMD anbefaler, at du indstiller den minimale dedikerede VRAM i BIOS (0,5 GB).

* Installer pipx-værktøjet, og tilføj stien for pipx-installerede wheels til systemets søgesti.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installer amd-debug-tools wheel'en fra PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kør amd-ttm-værktøjet for at forespørge de nuværende indstillinger for delt hukommelse.
  ```bash
  amd-ttm
  ```

* Konfigurer indstillingerne for delt hukommelse til **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Genstart systemet, for at ændringerne træder i kraft.


<!-- @os:end -->
<!-- @device:halo_box -->
## Kontrollér for softwareopdateringer

<!-- @require:software-update -->
<!-- @device:end -->
## Forudsætninger

### Hardware

Denne playbook kræver to Ryzen AI Halo-enheder og én Ethernet-switch, forbundet i en stjernetopologi, hvor hver enhed er forbundet direkte til switchen.

| Komponent | Antal | Beskrivelse |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Compute-noder, der udgør klyngen |
| 10Gbps Ethernet-switch | 1 | Central switch, der muliggør kommunikation mellem flere Ryzen AI Halo-noder (mindst 2 porte) |
| Ethernet-kabel | 2 | Forbinder hver Halo-enhed til switchen (Cat 7 eller højere anbefales) |

> **Bemærk**: Der kræves to porte på Ethernet-switchen for at forbinde de to Ryzen AI Halo-enheder. Der kræves en tredje port, hvis du tilgår modellen fra en separat klientmaskine i stedet for fra en af Halo-enhederne.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Installer venligst:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) med arbejdsbelastningen **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fysisk hardwareopsætning

> **Bemærk**: Udfør dette trin på både Maskine 1 og Maskine 2.

Forbind hver Ryzen AI Halo-enhed til Ethernet-switchen ved hjælp af et Cat 7-kabel (eller højere). Dette etablerer 10Gbps-forbindelsen, der bruges til højhastighedskommunikation mellem noderne.
<!-- @os:linux -->
### 1. Bestem netværksgrænseflader

Find navnet på netværksgrænsefladen på hver maskine, og notér det (det vil herefter blive omtalt som `IFNAME`). Kør:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dette udskriver grænsefladenavnet direkte, for eksempel:

```bash
enp191s0
```

### 2. Bekræft netværksforbindelsens hastighed

Bekræft, at forbindelsen er aktiv og kører med fuld hastighed, ved at kontrollere hastigheden på din grænseflade:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Bemærk**: Erstat `<IFNAME>` med navnet på output-grænsefladen fra [1. Bestem netværksgrænseflader](#1-determine-network-interfaces)

Du bør se en hastighed på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Bemærk**: Hvis hastigheden er lavere end `10000Mb/s`, eller forbindelsen ikke etableres, skal du kontrollere kabelforbindelsen og bekræfte, at switch-porten er indstillet til 10Gbps. Nogle switche kræver, at auto-forhandling deaktiveres, og at linkhastigheden indstilles manuelt; se din switchs dokumentation for mere information.

<!-- @os:end -->

<!-- @os:windows -->
### Bekræft netværksforbindelsens hastighed

Kontrollér hastigheden på netværksgrænsefladerne på hver maskine:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Din Ethernet-grænseflade bør være `Up` og køre med `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Bemærk**: Hvis hastigheden er lavere end `10 Gbps`, eller forbindelsen ikke etableres, skal du kontrollere kabelforbindelsen og bekræfte, at switch-porten er indstillet til 10Gbps. Nogle switche kræver, at auto-forhandling deaktiveres, og at linkhastigheden indstilles manuelt; se din switchs dokumentation for mere information.

<!-- @os:end -->

## Installation af llama.cpp

> **Bemærk**: Udfør dette trin på både Maskine 1 og Maskine 2.

To installationsmuligheder er tilgængelige:

- [Mulighed 1: Lemonade SDK (Anbefalet)](#option-1-lemonade-sdk-recommended) - færdigbyggede binærfiler, hurtigste opsætning
- [Mulighed 2: Manuel build fra kildekode](#option-2-manual-source-build) - byg fra kildekode med fuld kontrol over build-flag

### Mulighed 1: Lemonade SDK (Anbefalet)

Lemonade SDK leverer natlige builds af llama.cpp med AMD ROCm 7-acceleration, målrettet GPU'er som gfx1151 (Strix Halo / Ryzen AI Max+ 395) og andre nyere Radeon-arkitekturer.

<!-- @os:windows -->
#### Trin 1: Download de præbyggede binærfiler

Naviger til den nyeste udgivelsesside, og download det arkiv, der matcher din platform og GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download filen med navnet `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (hvor `xxxx` er build-nummeret).

#### Trin 2: Udpak binærfilerne

Udpak det downloadede arkiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Denne mappe indeholder nu ROCm-aktiverede builds af `llama-cli.exe`, `llama-server.exe` og `rpc-server.exe`, forudkompileret til dit Ryzen AI Halo-system.

#### Trin 3: Bekræft GPU-registrering

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
#### Trin 1: Download de præbyggede binærfiler

Naviger til den nyeste udgivelsesside, og download det arkiv, der matcher din platform og GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download filen med navnet `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (hvor `xxxx` er build-nummeret).

#### Trin 2: Udpak og forbered binærfilerne

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Denne mappe indeholder nu ROCm-aktiverede builds af `llama-cli`, `llama-server` og `rpc-server`, forudkompileret til dit Ryzen AI Halo-system.

#### Trin 3: Bekræft GPU-registrering

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
Når llama.cpp er klargjort på hver node, fortsæt til [Download af modellen](#downloading-the-model).

### Mulighed 2: Manuel kildekode-build

<!-- @os:windows -->
#### Trin 1: Byg llama.cpp

Åbn **x64 Native Tools Command Prompt** (installeret sammen med Visual Studio Build Tools), og klon repositoryet:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Tilføj HIP til din sti, og byg med understøttelse af ROCm og RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Build-flag | Formål |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiverer ROCm/HIP-softwarestakken |
| `-DGGML_RPC=ON` | Aktiverer RPC til distribueret inferens |
| `-DGPU_TARGETS=gfx1151` | Målretter mod Ryzen AI Halo-GPU'en (Radeon 8060s) |
| `-G Ninja` | Bruger Ninja-buildsystemet |

#### Trin 2: Bekræft GPU-registrering

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

Ovenstående build-trin angav `%HIP_PATH%\bin` kun for den aktuelle session. For at gøre HIP-bibliotekerne tilgængelige i enhver terminal (ikke kun x64 Native Tools Command Prompt), skal du tilføje det til din bruger-`PATH` permanent:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Når llama.cpp er klargjort på hver node, fortsæt til [Download af modellen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Trin 1: Byg llama.cpp

Klon repositoryet:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Byg med understøttelse af ROCm og RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build-flag | Formål |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiverer ROCm-softwarestakken |
| `-DGGML_RPC=ON` | Aktiverer RPC til distribueret inferens |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Aktiverer rocWMMA for forbedret Flash Attention på AMD-GPU'er |
| `-DAMDGPU_TARGETS="gfx1151"` | Målretter mod Ryzen AI Halo-GPU'en (Radeon 8060s) |

For flere build-indstillinger henvises til [byggedokumentationen for llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Trin 2: Bekræft GPU-registrering

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

Når llama.cpp er klargjort på hver node, fortsæt til [Download af modellen](#downloading-the-model).
<!-- @os:end -->

## Download af modellen

Denne playbook bruger [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), en model med 358 milliarder parametre i `Q4_K_XL`-kvantiseringen fra [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Ved denne kvantisering kræver modellen cirka 205 GB lagerplads og passer inden for den samlede GPU-hukommelse på to Ryzen AI Halo-noder.

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

> **Bemærk**: Modeldownloadet skal gennemføres på Maskine 1 (controlleren). RPC-worker-noderne behøver ikke en lokal kopi af modelfilerne.

## Start af modellen på klyngen

RPC-motoren (Remote Procedure Call) i llama.cpp gør det muligt for en enkelt llama.cpp-instans at overføre modellag til fjernarbejdere over netværket. Én maskine fungerer som **controller** (Maskine 1) og håndterer tokenisering, planlægning og orkestrering. Den anden maskine kører en letvægts **RPC-server** (Maskine 2), der stiller sin GPU-hukommelse og beregningskraft til rådighed for controlleren.

Ved indlæsning fordeler llama.cpp modellen på tværs af begge noder. Når modellen er indlæst, forløber inferensen, som om den kørte på en enkelt accelerator. RPC håndterer tensoroverførsler og synkronisering bag kulisserne.

### Trin 1: Start RPC-serveren (Maskine 2)

På Maskine 2 skal du starte RPC-serveren for at stille dens GPU-ressourcer til rådighed for controlleren:
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

| Flag | Formål |
|------|---------|
| `-p` | Port, som RPC-serveren udsendes på |
| `-c` | Aktiverer en lokal cache til store tensorer, hvilket undgår gentagne netværksoverførsler under indlæsning af modellen |
| `--host` | IP-adresse, som RPC-serveren skal bindes til (`0.0.0.0` for alle interfaces) |

For flere indstillinger henvises til [RPC-dokumentationen for llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Trin 2: Start modellen (Maskine 1)

Når RPC-serveren kører på Maskine 2, kan du starte inferens fra Maskine 1 ved hjælp af enten `llama-cli` eller `llama-server`.

#### llama-cli

`llama-cli` giver en terminalbaseret grænseflade til direkte interaktion med modellen. Den er ideel til benchmarking, fejlfinding og eksperimenter på lavt niveau.

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

> **Sådan finder du `<RPC_WORKER_IP>`**: Kør `hostname -I | awk '{print $1}'` på Maskine 2 for at finde dens lokale IP-adresse.
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

> **Sådan finder du `<RPC_WORKER_IP>`**: Kør `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) på Maskine 2 for at finde dens lokale IP-adresse.

<!-- @os:end -->

Når den kører, viser `llama-cli` fremskridtet for modelindlæsningen og starter en interaktiv prompt, hvor du kan chatte direkte med modellen:

![llama-cli der kører GLM 4.7 på tværs af to noder](assets/llama-cli-example.png)
#### llama-server

`llama-server` eksponerer den samme inferensmotor gennem en vedvarende serverproces med en integreret webbrugerflade og en OpenAI-kompatibel HTTP-API. Dette er den foretrukne grænseflade til implementeringer, der kører i længere tid, adgang for flere brugere og integration med eksterne værktøjer.

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

> **Finder `<RPC_WORKER_IP>`**: På maskine 2, kør `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse.
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

> **Finder `<RPC_WORKER_IP>`**: På maskine 2, kør `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for at finde dens lokale IP-adresse.
<!-- @os:end -->

Når den er startet, skal du åbne `http://<HOST_IP>:8081` i din browser for at få adgang til den indbyggede webbrugerflade. Denne giver en browserbaseret chatgrænseflade til at interagere med modellen:

![llama-server webbrugerflade, der kører GLM 4.7 på tværs af to noder](assets/llama-server-example.png)

<!-- @os:linux -->
> **Finder `<HOST_IP>`**: På maskine 1, kør `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse.
<!-- @os:end -->

<!-- @os:windows -->
> **Finder `<HOST_IP>`**: På maskine 1, kør `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for at finde dens lokale IP-adresse.
<!-- @os:end -->

#### Parameterreference

| Flag | Formål |
|------|---------|
| `-m` | Sti til GGUF-modelfilen (brug det første shard, `00001-of-00005`) |
| `-c` | Kontekststørrelse i tokens. Større værdier bruger mere hukommelse |
| `-fa on` | Aktiverer rocWMMA Flash Attention for forbedret ydeevne på AMD-GPU'er |
| `-ngl 999` | Overfører alle modellag til GPU'en |
| `--no-mmap` | Deaktiverer hukommelsesmapping, hvilket reducerer indlæsningstider, når modelstørrelsen overstiger system-RAM, men passer i VRAM |
| `--host` | IP, som `llama-server` skal bindes til (kun `llama-server`) |
| `--port` | Port, som HTTP-API'en skal betjenes på (kun `llama-server`) |
| `--rpc` | Kommasepareret liste over RPC-worker-endepunkter (`IP:port`) |

For fuld information om parameterbrug, se [llama-cli-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) og [llama-server-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Næste trin

- **Forbind tredjepartsapplikationer**: `llama-server` eksponerer en OpenAI-kompatibel API. Peg enhver OpenAI-kompatibel applikation (såsom Open WebUI) mod `http://<HOST_IP>:8081` med en vilkårlig pladsholder-API-nøgle (f.eks. `none`) for at forbinde til din klynge
- **Udforsk andre modeller**: Gennemse kvantiserede GGUF'er på [Hugging Face](https://huggingface.co/models?search=gguf) for at finde modeller, der passer inden for din klynges samlede GPU-hukommelse
- **Skaler til fire noder**: Tilføj to yderligere Ryzen AI Halo-systemer som ekstra RPC-workere for at få adgang til modeller i størrelsesordenen 1 billion parametre. Angiv yderligere endepunkter til `--rpc` som en kommasepareret liste (f.eks. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)