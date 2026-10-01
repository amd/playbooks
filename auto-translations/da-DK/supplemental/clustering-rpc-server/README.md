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

# Klyngedannelse af to Ryzen™ AI Halo-systemer med RPC

## Oversigt

Din Ryzen™ AI Halo kan allerede køre store sprogmodeller lokalt. Klyngedannelse tager dette et skridt videre ved at kombinere GPU-hukommelsen fra flere systemer over et lokalt netværk, hvilket giver dig adgang til endnu større modeller med stærkere ræsonnement, bedre kodegenerering og dybere flersproget forståelse – alt sammen fuldstændigt på din egen hardware.

Denne playbook viser dig, hvordan du danner en klynge af to Ryzen AI Halo-systemer ved hjælp af llama.cpp's RPC-motor og kører GLM 4.7, en model med 358 milliarder parametre, på tværs af begge maskiner med AMD ROCm™-acceleration.

## Hvad du vil lære

- Hvordan du udvider VRAM-allokeringen på Ryzen AI Halo-systemer
- Installation af llama.cpp med ROCm- og RPC-understøttelse
- Konfiguration af en RPC-worker og igangsættelse af distribueret inferens på tværs af to noder
- Kørsel af en model med 358 milliarder parametre på tværs af to netværksforbundne Ryzen AI Halo-systemer

## Angivelse af hukommelseskonfigurationen

> **Bemærk**: Udfør dette trin på både Maskine 1 og Maskine 2.

<!-- @os:windows -->
På Windows skal vi bruge AMD Variable Graphics Memory (iGPU VRAM)-allokeringen for at kunne køre større modeller, der kræver mere hukommelse.

Dette kan gøres ved at åbne kontrolpanelet AMD Software: Adrenalin Edition og navigere til: `Performance > Tuning > AMD Variable Graphics Memory`. Sæt værdien til **96 GB**. Genstart systemet, for at ændringerne træder i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
På Linux benytter ROCm en delt systemhukommelsespulje, og denne pulje er som standard konfigureret til halvdelen af systemhukommelsen.

Denne mængde kan øges ved at ændre kernens Translation Table Manager (TTM)-sideindstilling ved hjælp af nedenstående instruktioner. AMD anbefaler at indstille den minimale dedikerede VRAM i BIOS'en (0,5 GB).

* Installer pipx-værktøjet, og tilføj stien for pipx-installerede wheels til systemets søgesti.

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

* Omkonfigurer indstillingerne for delt hukommelse til **120 GB**:
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

Denne playbook kræver to Ryzen AI Halo-enheder og en Ethernet-switch, forbundet i en stjernetopologi, hvor hver enhed er forbundet direkte til switchen.

| Komponent | Antal | Beskrivelse |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Beregningsnoder, der udgør klyngen |
| 10Gbps Ethernet-switch | 1 | Central switch, der muliggør kommunikation mellem flere Ryzen AI Halo-noder (mindst 2 porte) |
| Ethernet-kabel | 2 | Forbinder hver Halo-enhed til switchen (Cat 7 eller højere anbefales) |

> **Bemærk**: Der kræves to porte på Ethernet-switchen for at forbinde de to Ryzen AI Halo-enheder. En tredje port er nødvendig, hvis du tilgår modellen fra en separat klientmaskine i stedet for fra en af Halo-enhederne.

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

Find navnet på netværksgrænsefladen på hver maskine, og noter det ned (det vil herefter blive omtalt som `IFNAME`). Kør:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dette udskriver grænsefladenavnet direkte, for eksempel:

```bash
enp191s0
```

### 2. Bekræft netværkslinkhastigheder

Bekræft, at forbindelsen er aktiv og kører med fuld hastighed, ved at kontrollere hastigheden på din grænseflade:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Bemærk**: Erstat `<IFNAME>` med det udskrevne grænsefladenavn fra [1. Bestem netværksgrænseflader](#1-determine-network-interfaces)

Du bør se en hastighed på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Bemærk**: Hvis hastigheden er lavere end `10000Mb/s`, eller forbindelsen ikke etableres, skal du kontrollere kabelforbindelsen og bekræfte, at switch-porten er indstillet til 10Gbps. Nogle switches kræver, at auto-forhandling deaktiveres, og linkhastigheden indstilles manuelt; se dokumentationen til din switch.

<!-- @os:end -->

<!-- @os:windows -->
### Bekræft netværkslinkhastighed

Kontrollér linkhastigheden for dine netværksgrænseflader på hver maskine:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Din Ethernet-grænseflade bør være `Up` og køre med `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Bemærk**: Hvis hastigheden er lavere end `10 Gbps`, eller forbindelsen ikke etableres, skal du kontrollere kabelforbindelsen og bekræfte, at switch-porten er indstillet til 10Gbps. Nogle switches kræver, at auto-forhandling deaktiveres, og linkhastigheden indstilles manuelt; se dokumentationen til din switch.

<!-- @os:end -->

## Installation af llama.cpp

> **Bemærk**: Udfør dette trin på både Maskine 1 og Maskine 2.

Der findes to installationsmuligheder:

- [Mulighed 1: Lemonade SDK (Anbefalet)](#option-1-lemonade-sdk-recommended) – foruddefinerede binærfiler, hurtigst opsætning
- [Mulighed 2: Manuel kildekodeopbygning](#option-2-manual-source-build) – byg fra kildekode med fuld kontrol over build-flag

### Mulighed 1: Lemonade SDK (Anbefalet)

Lemonade SDK leverer natlige builds af llama.cpp med AMD ROCm 7-acceleration målrettet GPU'er som gfx1151 (Strix Halo / Ryzen AI Max+ 395) og andre nyere Radeon-arkitekturer.

<!-- @os:windows -->
#### Trin 1: Download de præbyggede binærfiler

Gå til den seneste udgivelsesside, og download det arkiv, der matcher din platform og GPU-mål:

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

Gå til den seneste udgivelsesside, og download det arkiv, der matcher din platform og GPU-mål:

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
Når llama.cpp er klargjort på hver node, fortsæt til [Downloading the Model](#downloading-the-model).

### Mulighed 2: Manuel kildekodebygning

<!-- @os:windows -->
#### Trin 1: Byg llama.cpp

Åbn **x64 Native Tools Command Prompt** (installeret sammen med Visual Studio Build Tools), og klon repositoriet:

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

Bygningstrinnet ovenfor angav `%HIP_PATH%\bin` kun for den nuværende session. For at gøre HIP-bibliotekerne tilgængelige i enhver terminal (ikke kun x64 Native Tools Command Prompt), skal du tilføje det permanent til din bruger-`PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Når llama.cpp er klargjort på hver node, fortsæt til [Downloading the Model](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Trin 1: Byg llama.cpp

Klon repositoriet:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Byg med understøttelse af ROCm og RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build-flag | Formål |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiverer ROCm-softwarestakken |
| `-DGGML_RPC=ON` | Aktiverer RPC til distribueret inferens |
| `-DAMDGPU_TARGETS="gfx1151"` | Målretter mod Ryzen AI Halo-GPU'en (Radeon 8060s) |

For flere buildindstillinger henvises til [llama.cpp build documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Når llama.cpp er klargjort på hver node, fortsæt til [Downloading the Model](#downloading-the-model).
<!-- @os:end -->

## Download af modellen

Denne playbook bruger [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), en model med 358B parametre i `Q4_K_XL`-kvantiseringen fra [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Ved denne kvantisering kræver modellen omkring 205 GB lagerplads og passer inden for den samlede GPU-hukommelse på to Ryzen AI Halo-noder.

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

> **Bemærk**: Modeldownloadet skal gennemføres på Machine 1 (controlleren). RPC-arbejdsnoderne behøver ikke en lokal kopi af modelfilerne.

## Start af modellen på klyngen

llama.cpp RPC-motoren (Remote Procedure Call) gør det muligt for en enkelt llama.cpp-instans at overføre modellag til fjernarbejdere over netværket. Én maskine fungerer som **controller** (Machine 1) og håndterer tokenisering, planlægning og orkestrering. Den anden maskine kører en let **RPC-server** (Machine 2), der stiller sin GPU-hukommelse og beregningskraft til rådighed for controlleren.

Ved indlæsningstidspunktet opdeler llama.cpp modellen på tværs af begge noder. Når modellen er indlæst, foregår inferens, som om den kørte på en enkelt accelerator. RPC håndterer tensor-overførsler og synkronisering bag kulisserne.

### Trin 1: Start RPC-serveren (Machine 2)

På Machine 2 skal du starte RPC-serveren for at stille dens GPU-ressourcer til rådighed for controlleren:
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
| `--host` | IP-adresse, som RPC-serveren skal binde til (`0.0.0.0` for alle interfaces) |

For flere indstillinger henvises til [llama.cpp RPC documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Trin 2: Start modellen (Machine 1)

Med RPC-serveren kørende på Machine 2 kan du starte inferens fra Machine 1 ved hjælp af enten `llama-cli` eller `llama-server`.

#### llama-cli

`llama-cli` giver en terminalbaseret grænseflade til direkte interaktion med modellen. Den er ideel til benchmarking, fejlfinding og eksperimenter på lavt niveau.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **Sådan finder du `<RPC_WORKER_IP>`**: Kør `hostname -I | awk '{print $1}'` på Machine 2 for at finde dens lokale IP-adresse.
<!-- @os:end -->

<!-- @os:windows -->
> **Bemærk**: Kør denne kommando i Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Sådan finder du `<RPC_WORKER_IP>`**: Kør `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) på Machine 2 for at finde dens lokale IP-adresse.

<!-- @os:end -->

Når den kører, viser `llama-cli` fremdriften for modelindlæsning og åbner en interaktiv prompt, hvor du kan chatte direkte med modellen:

![llama-cli kører GLM 4.7 på tværs af to noder](assets/llama-cli-example.png)
#### llama-server

`llama-server` eksponerer den samme inferensmotor gennem en persistent serverproces med en integreret web-UI og et OpenAI-kompatibelt HTTP API. Dette er den foretrukne grænseflade til langvarige implementeringer, adgang for flere brugere og integration med eksterne værktøjer.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **Find `<RPC_WORKER_IP>`**: På maskine 2 skal du køre `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse.
<!-- @os:end -->

<!-- @os:windows -->
> **Bemærk**: Kør denne kommando i Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Find `<RPC_WORKER_IP>`**: På maskine 2 skal du køre `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for at finde dens lokale IP-adresse.
<!-- @os:end -->

Når den er startet, skal du åbne `http://<HOST_IP>:8081` i din browser for at få adgang til den indbyggede web-UI. Dette giver en browserbaseret chatgrænseflade til at interagere med modellen:

![llama-server web-UI, der kører GLM 4.7 på tværs af to noder](assets/llama-server-example.png)

<!-- @os:linux -->
> **Find `<HOST_IP>`**: På maskine 1 skal du køre `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse.
<!-- @os:end -->

<!-- @os:windows -->
> **Find `<HOST_IP>`**: På maskine 1 skal du køre `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for at finde dens lokale IP-adresse.
<!-- @os:end -->

#### Parameterreference

| Flag | Formål |
|------|---------|
| `-m` | Sti til GGUF-modelfilen (brug det første shard, `00001-of-00005`) |
| `-c` | Kontekststørrelse i tokens. Større værdier bruger mere hukommelse |
| `-fa on` | Aktiverer rocWMMA Flash Attention for forbedret ydeevne på AMD-GPU'er |
| `-ngl 999` | Overfører alle modellag til GPU'en |
| `-lm none` | Sætter modellens indlæsningstilstand til `none`, hvilket deaktiverer memory-mapping for at reducere indlæsningstider, når modelstørrelsen overstiger systemets RAM, men passer i VRAM |
| `--host` | IP, som `llama-server` skal bindes til (kun `llama-server`) |
| `--port` | Port, hvorpå HTTP API'et skal betjenes (kun `llama-server`) |
| `--rpc` | Kommasepareret liste over RPC-worker-endpoints (`IP:port`) |

For fuld parameterbrug henvises til [llama-cli-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) og [llama-server-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Næste trin

- **Forbind tredjepartsapplikationer**: `llama-server` eksponerer et OpenAI-kompatibelt API. Peg enhver OpenAI-kompatibel applikation (såsom Open WebUI) mod `http://<HOST_IP>:8081` med en vilkårlig pladsholder-API-nøgle (f.eks. `none`) for at oprette forbindelse til din klynge
- **Udforsk andre modeller**: Gennemse kvantiserede GGUF'er på [Hugging Face](https://huggingface.co/models?search=gguf) for at finde modeller, der passer inden for din klynges samlede GPU-hukommelse
- **Skalér til fire noder**: Tilføj to yderligere Ryzen AI Halo-systemer som ekstra RPC-workere for at få adgang til modeller i størrelsesordenen 1 billion parametre. Send yderligere endpoints til `--rpc` som en kommasepareret liste (f.eks. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)