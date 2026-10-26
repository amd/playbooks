<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Twee Ryzen™ AI Halo's clusteren met RPC

## Overzicht

Je Ryzen™ AI Halo kan al lokaal grote taalmodellen uitvoeren. Clustering gaat hierin nog verder door het GPU-geheugen van meerdere systemen via een lokaal netwerk te combineren, wat je toegang geeft tot nog grotere modellen met sterkere redeneervaardigheden, betere codegeneratie en diepgaander meertalig begrip, volledig op je eigen hardware.

Deze playbook leert je hoe je twee Ryzen AI Halo-systemen clustert met behulp van de RPC-engine van llama.cpp en GLM 4.7, een model met 358B parameters, op beide machines laat draaien met AMD ROCm™-acceleratie.

## Wat je gaat leren

- Hoe je de VRAM-toewijzing op Ryzen AI Halo-systemen uitbreidt
- Het installeren van llama.cpp met ROCm- en RPC-ondersteuning
- Het configureren van een RPC-worker en het starten van gedistribueerde inferentie over twee nodes
- Het uitvoeren van een model met 358B parameters op twee genetwerkte Ryzen AI Halo-systemen

## De geheugenconfiguratie instellen

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Modellen uitvoeren rond of boven 128 GB:** Op systemen met AMD Ryzen™ AI Max 400 Series (Gorgon Halo) waarop Windows draait, vereisen modellen die 128 GB geheugen benaderen of overschrijden extra configuratie om zonder fouten te draaien. Volg de [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) voordat je het model laadt.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Op Windows moeten we, om grotere modellen uit te voeren die meer geheugen vereisen, gebruikmaken van de AMD Variable Graphics Memory-toewijzing (iGPU VRAM).

Dit kan door het configuratiescherm AMD Software: Adrenalin Edition te openen en te navigeren naar: `Performance > Tuning > AMD Variable Graphics Memory`. Stel de waarde in op **96 GB**. Start het systeem opnieuw op zodat de wijzigingen van kracht worden.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Op Linux gebruikt ROCm een gedeelde systeemgeheugenpool, en deze pool is standaard geconfigureerd op de helft van het systeemgeheugen.

Deze hoeveelheid kan worden vergroot door de pagina-instelling van de kernel's Translation Table Manager (TTM) te wijzigen, volgens de onderstaande instructies. AMD raadt aan om het minimale toegewezen VRAM in te stellen in de BIOS (0,5 GB).

* Installeer het pipx-hulpprogramma en voeg het pad voor door pipx geïnstalleerde wheels toe aan het systeemzoekpad.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installeer de amd-debug-tools wheel van PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Voer het amd-ttm-hulpprogramma uit om de huidige instellingen voor gedeeld geheugen op te vragen.
  ```bash
  amd-ttm
  ```

* Configureer de instellingen voor gedeeld geheugen opnieuw naar **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Start het systeem opnieuw op zodat de wijzigingen van kracht worden.


<!-- @os:end -->
<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->
## Vereisten

### Hardware

Deze playbook vereist twee Ryzen AI Halo-units en één Ethernet-switch, verbonden in een stertopologie waarbij elke unit rechtstreeks met de switch is verbonden.

| Onderdeel | Aantal | Beschrijving |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Rekennodes die het cluster vormen |
| 10Gbps Ethernet-switch | 1 | Centrale switch om communicatie tussen meerdere Ryzen AI Halo-nodes mogelijk te maken (minimaal 2 poorten) |
| Ethernet-kabel | 2 | Verbindt elke Halo-unit met de switch (Cat 7 of hoger aanbevolen) |

> **Opmerking**: Er zijn twee Ethernet-switchpoorten nodig om de twee Ryzen AI Halo-units met elkaar te verbinden. Een derde poort is nodig als je het model benadert vanaf een afzonderlijke clientmachine in plaats van vanaf een van de Halo-units.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Installeer:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) met de workload **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fysieke hardwareopstelling

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Verbind elke Ryzen AI Halo-unit met de Ethernet-switch met behulp van een Cat 7-kabel (of hoger). Dit zorgt voor de 10Gbps-verbinding die wordt gebruikt voor snelle communicatie tussen de nodes.
<!-- @os:linux -->
### 1. De netwerkinterfaces bepalen

Zoek op elke machine de naam van de netwerkinterface en noteer deze (hierna aangeduid als `IFNAME`). Voer uit:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dit toont de interfacenaam direct, bijvoorbeeld:

```bash
enp191s0
```

### 2. De netwerklinksnelheden verifiëren

Controleer of de verbinding actief is en op volle snelheid draait door de snelheid van je interface te controleren:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opmerking**: Vervang `<IFNAME>` door de naam van de uitvoerinterface uit [1. De netwerkinterfaces bepalen](#1-determine-network-interfaces)

Je zou een snelheid van `10000Mb/s` moeten zien:

```bash
	Speed: 10000Mb/s
```

> **Opmerking**: Als de snelheid lager is dan `10000Mb/s` of de verbinding niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat auto-onderhandeling wordt uitgeschakeld en de linksnelheid handmatig wordt ingesteld; raadpleeg de documentatie van je switch.

<!-- @os:end -->

<!-- @os:windows -->
### De netwerklinksnelheid verifiëren

Controleer op elke machine de linksnelheid van je netwerkinterfaces:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Je Ethernet-interface zou `Up` moeten zijn en moeten draaien op `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Opmerking**: Als de snelheid lager is dan `10 Gbps` of de verbinding niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat auto-onderhandeling wordt uitgeschakeld en de linksnelheid handmatig wordt ingesteld; raadpleeg de documentatie van je switch.

<!-- @os:end -->

## llama.cpp installeren

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Er zijn twee installatieopties beschikbaar:

- [Optie 1: Lemonade SDK (aanbevolen)](#option-1-lemonade-sdk-recommended) - vooraf gebouwde binaries, snelste installatie
- [Optie 2: Handmatige build vanuit broncode](#option-2-manual-source-build) - bouw vanuit broncode met volledige controle over buildvlaggen
### Optie 1: Lemonade SDK (Aanbevolen)

De Lemonade SDK biedt nightly builds van llama.cpp met AMD ROCm 7-versnelling, gericht op GPU's zoals gfx1151 (Strix Halo / Ryzen AI Max+ 395) en andere recente Radeon-architecturen.

<!-- @os:windows -->
#### Stap 1: Download de voorgebouwde binaries

Navigeer naar de nieuwste release-pagina en download het archief dat overeenkomt met uw platform en GPU-doel:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download het bestand met de naam `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (waarbij `xxxx` het buildnummer is).

#### Stap 2: Pak de binaries uit

Pak het gedownloade archief uit:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Deze map bevat nu ROCm-geschikte builds van `llama-cli.exe`, `llama-server.exe` en `rpc-server.exe`, voorgecompileerd voor uw Ryzen AI Halo-systeem.

#### Stap 3: Verifieer GPU-detectie

```bash
.\llama-cli.exe --list-devices
```

Verwachte uitvoer:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Stap 1: Download de voorgebouwde binaries

Navigeer naar de nieuwste release-pagina en download het archief dat overeenkomt met uw platform en GPU-doel:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download het bestand met de naam `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (waarbij `xxxx` het buildnummer is).

#### Stap 2: Pak de binaries uit en bereid ze voor

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Deze map bevat nu ROCm-geschikte builds van `llama-cli`, `llama-server` en `rpc-server`, voorgecompileerd voor uw Ryzen AI Halo-systeem.

#### Stap 3: Verifieer GPU-detectie

```bash
./llama-cli --list-devices
```

Verwachte uitvoer:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Zodra llama.cpp op elke node is voorbereid, gaat u verder met [Het model downloaden](#downloading-the-model).

### Optie 2: Handmatige bronbuild

<!-- @os:windows -->
#### Stap 1: Bouw llama.cpp

Open de **x64 Native Tools Command Prompt** (geïnstalleerd met Visual Studio Build Tools) en kloon de repository:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Voeg HIP toe aan uw pad en bouw met ondersteuning voor ROCm en RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Build-vlag | Doel |
|-----------|---------|
| `-DGGML_HIP=ON` | Schakelt de ROCm/HIP-softwarestack in |
| `-DGGML_RPC=ON` | Schakelt RPC in voor gedistribueerde inferentie |
| `-DGPU_TARGETS=gfx1151` | Richt zich op de Ryzen AI Halo GPU (Radeon 8060s) |
| `-G Ninja` | Gebruikt het Ninja-buildsysteem |

#### Stap 2: Verifieer GPU-detectie

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Verwachte uitvoer:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Stap 3: Voeg HIP toe aan uw gebruikerspad

De bouwstap hierboven heeft `%HIP_PATH%\bin` alleen voor de huidige sessie ingesteld. Om de HIP-bibliotheken permanent beschikbaar te maken in elke terminal (niet alleen de x64 Native Tools Command Prompt), voegt u het permanent toe aan uw gebruikers-`PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Zodra llama.cpp op elke node is voorbereid, gaat u verder met [Het model downloaden](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Stap 1: Bouw llama.cpp

Kloon de repository:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Bouw met ondersteuning voor ROCm en RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build-vlag | Doel |
|-----------|---------|
| `-DGGML_HIP=ON` | Schakelt de ROCm-softwarestack in |
| `-DGGML_RPC=ON` | Schakelt RPC in voor gedistribueerde inferentie |
| `-DAMDGPU_TARGETS="gfx1151"` | Richt zich op de Ryzen AI Halo GPU (Radeon 8060s) |

Raadpleeg voor meer buildopties de [llama.cpp-builddocumentatie](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Stap 2: Verifieer GPU-detectie

```bash
cd rocm/bin
./llama-cli --list-devices
```

Verwachte uitvoer:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Zodra llama.cpp op elke node is voorbereid, gaat u verder met [Het model downloaden](#downloading-the-model).
<!-- @os:end -->

## Het model downloaden

Dit playbook gebruikt [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), een model met 358B parameters in de `Q4_K_XL`-kwantisering van [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Bij deze kwantisering vereist het model ongeveer 205 GB aan opslag en past het binnen het gecombineerde GPU-geheugen van twee Ryzen AI Halo-nodes.

Download de GGUF-bestanden met behulp van de Hugging Face CLI:
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

> **Opmerking**: De modeldownload moet worden voltooid op Machine 1 (de controller). De RPC-workernodes hebben geen lokale kopie van de modelbestanden nodig.

## Het model starten op de cluster

Met de llama.cpp RPC-engine (Remote Procedure Call) kan één llama.cpp-instantie modellagen offloaden naar externe workers via het netwerk. Eén machine fungeert als de **controller** (Machine 1), die tokenisatie, planning en orkestratie afhandelt. De andere machine draait een lichtgewicht **RPC-server** (Machine 2) die zijn GPU-geheugen en rekenkracht beschikbaar stelt aan de controller.

Tijdens het laden verdeelt llama.cpp het model over beide nodes. Zodra het model is geladen, verloopt de inferentie alsof deze op één enkele versneller draait. RPC regelt de tensoroverdrachten en synchronisatie op de achtergrond.

### Stap 1: Start de RPC-server (Machine 2)

Start op Machine 2 de RPC-server om de GPU-resources beschikbaar te stellen aan de controller:
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

| Vlag | Doel |
|------|---------|
| `-p` | Poort waarop de RPC-server wordt uitgezonden |
| `-c` | Schakelt een lokale cache voor grote tensoren in, waardoor herhaalde netwerkoverdrachten tijdens het laden van het model worden vermeden |
| `--host` | IP-adres waaraan de RPC-server wordt gebonden (`0.0.0.0` voor alle interfaces) |

Raadpleeg voor meer opties de [llama.cpp RPC-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Stap 2: Start het model (Machine 1)

Nu de RPC-server op Machine 2 draait, start u de inferentie vanaf Machine 1 met `llama-cli` of `llama-server`.
#### llama-cli

`llama-cli` biedt een terminal-gebaseerde interface voor rechtstreekse interactie met het model. Het is ideaal voor benchmarking, debugging en low-level experimenten.

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

> **`<RPC_WORKER_IP>` vinden**: Voer op Machine 2 het commando `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking**: Voer dit commando uit in Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` vinden**: Voer op Machine 2 het commando `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.

<!-- @os:end -->

Eenmaal actief, toont `llama-cli` de voortgang van het laden van het model en opent een interactieve prompt waarin je rechtstreeks met het model kunt chatten:

![llama-cli waarop GLM 4.7 op twee nodes draait](assets/llama-cli-example.png)

#### llama-server

`llama-server` stelt dezelfde inference-engine beschikbaar via een persistent serverproces met een geïntegreerde webinterface en een OpenAI-compatibele HTTP-API. Dit is de voorkeursinterface voor langduriger draaiende implementaties, toegang door meerdere gebruikers en integratie met externe tooling.

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

> **`<RPC_WORKER_IP>` vinden**: Voer op Machine 2 het commando `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking**: Voer dit commando uit in Terminal (Powershell).

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

> **`<RPC_WORKER_IP>` vinden**: Voer op Machine 2 het commando `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.
<!-- @os:end -->

Eenmaal gestart, open `http://<HOST_IP>:8081` in je browser om toegang te krijgen tot de ingebouwde webinterface. Dit biedt een browsergebaseerde chatinterface voor interactie met het model:

![llama-server webinterface waarop GLM 4.7 op twee nodes draait](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` vinden**: Voer op Machine 1 het commando `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` vinden**: Voer op Machine 1 het commando `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.
<!-- @os:end -->

#### Parameterreferentie

| Vlag | Doel |
|------|---------|
| `-m` | Pad naar het GGUF-modelbestand (gebruik de eerste shard, `00001-of-00005`) |
| `-c` | Contextgrootte in tokens. Grotere waarden gebruiken meer geheugen |
| `-fa on` | Schakelt rocWMMA Flash Attention in voor verbeterde prestaties op AMD-GPU's |
| `-ngl 999` | Offload alle modellagen naar de GPU |
| `-lm none` | Stelt de modelladermodus in op `none`, waardoor memory-mapping wordt uitgeschakeld om laadtijden te verkorten wanneer de modelgrootte groter is dan het systeemgeheugen maar wel in VRAM past |
| `--host` | IP waarop `llama-server` wordt gebonden (alleen `llama-server`) |
| `--port` | Poort waarop de HTTP-API wordt aangeboden (alleen `llama-server`) |
| `--rpc` | Kommagescheiden lijst van RPC-worker-endpoints (`IP:port`) |

Voor volledig gebruik van de parameters, raadpleeg de [llama-cli-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) en [llama-server-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Volgende stappen

- **Applicaties van derden verbinden**: `llama-server` biedt een OpenAI-compatibele API. Richt een willekeurige OpenAI-compatibele applicatie (zoals Open WebUI) op `http://<HOST_IP>:8081` met een willekeurige placeholder-API-sleutel (bijv. `none`) om verbinding te maken met je cluster
- **Andere modellen verkennen**: Blader door gekwantiseerde GGUF's op [Hugging Face](https://huggingface.co/models?search=gguf) om modellen te vinden die binnen het gecombineerde GPU-geheugen van je cluster passen
- **Opschalen naar vier nodes**: Voeg twee extra Ryzen AI Halo-systemen toe als aanvullende RPC-workers om toegang te krijgen tot modellen op de schaal van 1 biljoen parameters. Geef extra endpoints door aan `--rpc` als een kommagescheiden lijst (bijv. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)