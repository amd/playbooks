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

# Klyngedannelse af fire Ryzen™ AI Halos med RPC

## Oversigt

Din Ryzen™ AI Halo er allerede i stand til at køre store sprogmodeller lokalt. Klyngedannelse tager dette et skridt videre ved at kombinere GPU-hukommelsen fra flere systemer over et lokalt netværk, hvilket giver dig adgang til endnu større modeller med stærkere ræsonnementsevner, bedre kodegenerering og dybere flersproget forståelse, alt sammen udelukkende på din egen hardware.

Denne playbook lærer dig, hvordan du danner en klynge af fire Ryzen AI Halo-systemer ved hjælp af llama.cpp's RPC-motor og kører Kimi K2.6, en stor mixture-of-experts-model, på tværs af alle fire maskiner med AMD ROCm™-acceleration.

## Hvad du vil lære

- Hvordan du udvider VRAM-allokeringen på Ryzen AI Halo-systemer
- Installation af llama.cpp med ROCm- og RPC-understøttelse
- Konfiguration af RPC-workers og opstart af distribueret inferens på tværs af fire noder
- Kørsel af en model med 1T parametre på tværs af fire netværksforbundne Ryzen AI Halo-systemer

## Konfiguration af hukommelsesindstillinger

> **Bemærk**: Udfør dette trin på alle fire maskiner (Maskine 1 til Maskine 4).

<!-- @os:windows -->
På Windows skal vi, for at køre større modeller, der kræver mere hukommelse, bruge AMD Variable Graphics Memory-allokeringen (iGPU VRAM).

Dette kan gøres ved at åbne AMD Software: Adrenalin Edition-kontrolpanelet og navigere til: `Performance > Tuning > AMD Variable Graphics Memory`. Sæt værdien til **96 GB**. Genstart systemet, for at ændringerne træder i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
På Linux benytter ROCm en delt systemhukommelsespulje, og denne pulje er som standard konfigureret til halvdelen af systemhukommelsen.

Denne mængde kan øges ved at ændre kernens Translation Table Manager (TTM)-sideindstilling ved hjælp af følgende instruktioner. AMD anbefaler at indstille den minimale dedikerede VRAM i BIOS'en (0,5 GB).

* Installer pipx-værktøjet, og tilføj stien til pipx-installerede wheels til systemets søgesti.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installer amd-debug-tools-wheelen fra PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kør amd-ttm-værktøjet for at forespørge de nuværende indstillinger for delt hukommelse.
  ```bash
  amd-ttm
  ```

* Genkonfigurer indstillingerne for delt hukommelse til **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Genstart systemet, for at ændringerne træder i kraft.


<!-- @os:end -->
<!-- @device:halo_box -->
## Tjek for softwareopdateringer

<!-- @require:software-update -->
<!-- @device:end -->
## Forudsætninger

### Hardware

Denne playbook kræver fire Ryzen AI Halo-enheder og én Ethernet-switch, forbundet i en stjernetopologi, hvor hver enhed er kablet direkte til switchen.

| Komponent | Antal | Beskrivelse |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Beregningsnoder, der udgør klyngen |
| 10 Gbps Ethernet-switch | 1 | Central switch, der muliggør kommunikation mellem flere Ryzen AI Halo-noder (mindst 4 porte) |
| Ethernet-kabel | 4 | Forbinder hver Halo-enhed til switchen (Cat 7 eller højere anbefales) |

> **Bemærk**: Der kræves fire Ethernet-switch-porte for at forbinde de fire Ryzen AI Halo-enheder. Der kræves en femte port, hvis du tilgår modellen fra en separat klientmaskine i stedet for fra en af Halo-enhederne.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Installer venligst:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) med **Desktop Development with C++**-arbejdsbyrden
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fysisk hardwareopsætning

> **Bemærk**: Udfør dette trin på alle fire maskiner (Maskine 1 til Maskine 4).

Forbind hver Ryzen AI Halo-enhed til Ethernet-switchen med et Cat 7-kabel (eller højere). Dette etablerer den 10 Gbps-forbindelse, der bruges til højhastighedskommunikation mellem noderne.
<!-- @os:linux -->
### 1. Bestem netværksgrænseflader

Find på hver maskine navnet på dens netværksgrænseflade, og noter det (det vil nedenfor blive benævnt `IFNAME`). Kør:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dette udskriver grænsefladenavnet direkte, for eksempel:

```bash
enp191s0
```

### 2. Bekræft netværksforbindelsens hastighed

Bekræft, at forbindelsen er aktiv og kører med fuld hastighed, ved at tjekke hastigheden på din grænseflade:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Bemærk**: Erstat `<IFNAME>` med navnet på outputgrænsefladen fra [1. Bestem netværksgrænseflader](#1-determine-network-interfaces)

Du bør se en hastighed på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Bemærk**: Hvis hastigheden er lavere end `10000Mb/s`, eller forbindelsen ikke etableres, skal du kontrollere kabelforbindelsen og bekræfte, at switchporten er sat til 10 Gbps. Nogle switche kræver, at auto-forhandling deaktiveres, og at linkhastigheden indstilles manuelt; se dokumentationen til din switch.

<!-- @os:end -->

<!-- @os:windows -->
### Bekræft netværksforbindelsens hastighed

Tjek på hver maskine hastigheden på dine netværksgrænseflader:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Din Ethernet-grænseflade bør være `Up` og køre med `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Bemærk**: Hvis hastigheden er lavere end `10 Gbps`, eller forbindelsen ikke etableres, skal du kontrollere kabelforbindelsen og bekræfte, at switchporten er sat til 10 Gbps. Nogle switche kræver, at auto-forhandling deaktiveres, og at linkhastigheden indstilles manuelt; se dokumentationen til din switch.

<!-- @os:end -->

## Installation af llama.cpp

> **Bemærk**: Udfør dette trin på alle fire maskiner (Maskine 1 til Maskine 4).

Der er to installationsmuligheder tilgængelige:

- [Mulighed 1: Lemonade SDK (Anbefalet)](#option-1-lemonade-sdk-recommended) - præbyggede binærfiler, hurtigste opsætning
- [Mulighed 2: Manuel kildekodebygning](#option-2-manual-source-build) - byg fra kildekode med fuld kontrol over byggeflag

### Mulighed 1: Lemonade SDK (Anbefalet)

Lemonade SDK leverer natlige builds af llama.cpp med AMD ROCm 7-acceleration, målrettet GPU'er som gfx1151 (Strix Halo / Ryzen AI Max+ 395) og andre nyere Radeon-arkitekturer.

<!-- @os:windows -->
#### Trin 1: Download de præbyggede binærfiler

Naviger til den nyeste udgivelsesside, og download den arkivfil, der matcher din platform og GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download filen med navnet `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (hvor `xxxx` er build-nummeret).

#### Trin 2: Udpak binærfilerne

Udpak det downloadede arkiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Denne mappe indeholder nu ROCm-aktiverede builds af `llama-cli.exe`, `llama-server.exe` og `ggml-rpc-server.exe`, forudkompileret til dit Ryzen AI Halo-system.

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

Naviger til den nyeste udgivelsesside, og download den arkivfil, der matcher din platform og GPU-mål:

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

### Mulighed 2: Manuel kildekodebygning

<!-- @os:windows -->
#### Trin 1: Byg llama.cpp

Åbn **x64 Native Tools Command Prompt** (installeret sammen med Visual Studio Build Tools), og klon repositoriet:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Tilføj HIP til din sti, og byg med ROCm- og RPC-understøttelse:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Build-flag | Formål |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiverer ROCm/HIP-softwarestakken |
| `-DGGML_RPC=ON` | Aktiverer RPC til distribueret inferens |
| `-DGPU_TARGETS=gfx1151` | Sigter mod Ryzen AI Halo-GPU'en (Radeon 8060s) |
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

Ovenstående build-trin angav `%HIP_PATH%\bin` kun for den aktuelle session. For at gøre HIP-bibliotekerne tilgængelige i alle terminaler (ikke kun i x64 Native Tools Command Prompt), skal du tilføje den permanent til din bruger-`PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Når llama.cpp er klargjort på hver node, fortsæt til [Download af modellen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Trin 1: Byg llama.cpp

Klon repositoriet:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Byg med ROCm- og RPC-understøttelse:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build-flag | Formål |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiverer ROCm-softwarestakken |
| `-DGGML_RPC=ON` | Aktiverer RPC til distribueret inferens |
| `-DAMDGPU_TARGETS="gfx1151"` | Sigter mod Ryzen AI Halo-GPU'en (Radeon 8060s) |

For flere buildmuligheder henvises til [llama.cpp-builddokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Denne playbook bruger [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) i `UD-Q2_K_XL`-kvantiseringen fra [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Denne kvantisering passer inden for den samlede GPU-hukommelse på fire Ryzen AI Halo-noder.

Download GGUF-filerne ved hjælp af Hugging Face CLI:
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

> **Bemærk**: Modeldownloaden skal gennemføres på Maskine 1 (controlleren). RPC-worker-noderne (Maskine 2, 3 og 4) skal ikke have en lokal kopi af modelfilerne.

## Start af modellen på klyngen

llama.cpp RPC-motoren (Remote Procedure Call) gør det muligt for én enkelt llama.cpp-instans at aflaste modellag til fjern-workere over netværket. Én maskine fungerer som **controller** (Maskine 1) og håndterer tokenisering, planlægning og orkestrering. De tre øvrige maskiner kører hver især en let **RPC-server** (Maskine 2, 3 og 4), som stiller deres GPU-hukommelse og -beregningskraft til rådighed for controlleren.

Ved indlæsning opdeler llama.cpp modellen på tværs af alle fire noder. Når den er indlæst, forløber inferensen, som om den kørte på én enkelt accelerator. RPC håndterer tensor-overførsler og synkronisering i baggrunden.

### Trin 1: Start RPC-serverne (Maskine 2, 3 og 4)

Start på hver af Maskine 2, 3 og 4 RPC-serveren for at stille dens GPU-ressourcer til rådighed for controlleren:
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
| `-c` | Aktiverer en lokal cache til store tensorer, hvilket undgår gentagne netværksoverførsler under modelindlæsning |
| `--host` | IP-adresse, som RPC-serveren skal bindes til (`0.0.0.0` for alle grænseflader) |

For flere muligheder henvises til [llama.cpp RPC-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Trin 2: Start modellen (Maskine 1)

Når RPC-serverne kører på Maskine 2, 3 og 4, skal du starte inferensen fra Maskine 1 ved hjælp af enten `llama-cli` eller `llama-server`.
#### llama-cli

`llama-cli` giver en terminalbaseret grænseflade til at interagere direkte med modellen. Den er ideel til benchmarking, fejlfinding og eksperimentering på lavt niveau.

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

> **Sådan findes `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Kør `hostname -I | awk '{print $1}'` på hver af Maskine 2, 3 og 4 for at finde dens lokale IP-adresse.
<!-- @os:end -->

<!-- @os:windows -->
> **Bemærk**: Kør denne kommando i Terminal (Powershell).

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

> **Sådan findes `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Kør `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) på hver af Maskine 2, 3 og 4 for at finde dens lokale IP-adresse.

<!-- @os:end -->

Når den kører, viser `llama-cli` modellens indlæsningsforløb og åbner en interaktiv prompt, hvor du kan chatte direkte med modellen:

![llama-cli kører Kimi K2.6 på tværs af fire noder](assets/llama-cli-example.png)

#### llama-server

`llama-server` eksponerer den samme inferensmotor gennem en vedvarende serverproces med en integreret web-UI og en OpenAI-kompatibel HTTP-API. Dette er den foretrukne grænseflade til langvarige implementeringer, adgang for flere brugere og integration med eksternt værktøj.

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

> **Sådan findes `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Kør `hostname -I | awk '{print $1}'` på hver af Maskine 2, 3 og 4 for at finde dens lokale IP-adresse.
<!-- @os:end -->

<!-- @os:windows -->
> **Bemærk**: Kør denne kommando i Terminal (Powershell).

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

> **Sådan findes `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Kør `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) på hver af Maskine 2, 3 og 4 for at finde dens lokale IP-adresse.
<!-- @os:end -->

Når den er startet, kan du åbne `http://<HOST_IP>:8081` i din browser for at få adgang til den indbyggede web-UI. Dette giver en browserbaseret chatgrænseflade til at interagere med modellen:

![llama-server web-UI kører Kimi K2.6 på tværs af fire noder](assets/llama-server-example.png)

<!-- @os:linux -->
> **Sådan findes `<HOST_IP>`**: Kør `hostname -I | awk '{print $1}'` på Maskine 1 for at finde dens lokale IP-adresse.
<!-- @os:end -->

<!-- @os:windows -->
> **Sådan findes `<HOST_IP>`**: Kør `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) på Maskine 1 for at finde dens lokale IP-adresse.
<!-- @os:end -->

#### Parameterreference

| Flag | Formål |
|------|---------|
| `-m` | Sti til GGUF-modelfilen (brug det første shard, `00001-of-00008`) |
| `-c` | Kontekststørrelse i tokens. Større værdier bruger mere hukommelse |
| `-fa on` | Aktiverer rocWMMA Flash Attention for forbedret ydeevne på AMD-GPU'er |
| `-ngl 999` | Aflaster alle modellag til GPU'en |
| `-lm none` | Sætter modellens indlæsningstilstand til `none`, hvilket deaktiverer memory-mapping for at reducere indlæsningstider, når modelstørrelsen overstiger system-RAM, men passer i VRAM |
| `-b` | Logisk batchstørrelse i tokens. Sættes til 4096 for at balancere gennemløb og hukommelsesforbrug på tværs af noder |
| `-ub` | Fysisk (mikro) batchstørrelse til promptbehandling. At matche `-b` undgår unødvendig overhead ved opdeling |
| `--host` | IP, som `llama-server` skal bindes til (kun `llama-server`) |
| `--port` | Port, som HTTP-API'et serveres på (kun `llama-server`) |
| `--rpc` | Kommasepareret liste over RPC worker-endepunkter (`IP:port`) |

For fuld parameterbrug henvises der til [llama-cli-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) og [llama-server-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Næste trin

- **Tilslut tredjepartsapplikationer**: `llama-server` eksponerer en OpenAI-kompatibel API. Peg enhver OpenAI-kompatibel applikation (såsom Open WebUI) mod `http://<HOST_IP>:8081` med en vilkårlig pladsholder-API-nøgle (f.eks. `none`) for at oprette forbindelse til din klynge
- **Udforsk andre modeller**: Gennemse kvantiserede GGUF'er på [Hugging Face](https://huggingface.co/models?search=gguf) for at finde modeller, der passer inden for din klynges samlede GPU-hukommelse
- **Skaler ud over fire noder**: Tilføj flere Ryzen AI Halo-systemer som yderligere RPC workers for at få adgang til modeller ud over 1 billion parametre. Send yderligere endepunkter til `--rpc` som en kommasepareret liste (f.eks. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)