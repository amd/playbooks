<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Twee Ryzen™ AI Halos clusteren met RPC

## Overzicht

Uw Ryzen™ AI Halo is al in staat om grote taalmodellen lokaal uit te voeren. Clustering gaat een stap verder door het GPU-geheugen van meerdere systemen via een lokaal netwerk te combineren, waardoor u toegang krijgt tot nog grotere modellen met sterkere redeneervaardigheden, betere codegeneratie en dieper meertalig begrip — allemaal volledig op uw eigen hardware.

Dit playbook leert u hoe u twee Ryzen AI Halo-systemen kunt clusteren met behulp van de RPC-engine van llama.cpp en GLM 4.7, een model met 358 miljard parameters, kunt uitvoeren over beide machines met AMD ROCm™-versnelling.

## Wat u leert

- Hoe u de VRAM-toewijzing op Ryzen AI Halo-systemen uitbreidt
- llama.cpp installeren met ROCm- en RPC-ondersteuning
- Een RPC-worker configureren en gedistribueerde inferentie starten over twee nodes
- Een model met 358 miljard parameters uitvoeren over twee via een netwerk verbonden Ryzen AI Halo-systemen

## De geheugenconfiguratie instellen

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

<!-- @os:windows -->
Op Windows moeten we, om grotere modellen uit te voeren die meer geheugen vereisen, de AMD Variable Graphics Memory (iGPU VRAM)-toewijzing gebruiken.

Dit kan worden gedaan door het AMD Software: Adrenalin Edition-configuratiescherm te openen en te navigeren naar: `Performance > Tuning > AMD Variable Graphics Memory`. Stel de waarde in op **96 GB**. Start het systeem opnieuw op om de wijzigingen door te voeren.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Op Linux maakt ROCm gebruik van een gedeelde systeemgeheugenpool, die standaard is geconfigureerd op de helft van het systeemgeheugen.

Deze hoeveelheid kan worden vergroot door de Translation Table Manager (TTM)-pagina-instelling van de kernel te wijzigen, met behulp van de volgende instructies. AMD raadt aan om het minimale toegewezen VRAM in het BIOS in te stellen (0,5 GB).

* Installeer het pipx-hulpprogramma en voeg het pad voor door pipx geïnstalleerde wheels toe aan het systeemzoekpad.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installeer het amd-debug-tools-wheel van PyPI.
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

* Start het systeem opnieuw op om de wijzigingen door te voeren.


<!-- @os:end -->
<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->
## Vereisten

### Hardware

Dit playbook vereist twee Ryzen AI Halo-eenheden en één Ethernet-switch, verbonden in een sterstopologie waarbij elke eenheid rechtstreeks op de switch is aangesloten.

| Component | Aantal | Beschrijving |
|-----------|--------|--------------|
| Ryzen AI Halo | 2 | Rekenknooppunten die het cluster vormen |
| 10Gbps Ethernet-switch | 1 | Centrale switch voor communicatie tussen meerdere Ryzen AI Halo-nodes (minimaal 2 poorten) |
| Ethernet-kabel | 2 | Verbindt elke Halo-eenheid met de switch (Cat 7 of hoger aanbevolen) |

> **Opmerking**: Er zijn twee Ethernet-switchpoorten nodig om de twee Ryzen AI Halo-eenheden te verbinden. Een derde poort is vereist als u het model benadert vanaf een afzonderlijke clientmachine in plaats van vanaf een van de Halo-eenheden.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Installeer:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) met de workload **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fysieke hardware-installatie

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Verbind elke Ryzen AI Halo-eenheid met de Ethernet-switch via een Cat 7-kabel (of hoger). Dit legt de 10Gbps-verbinding aan die wordt gebruikt voor snelle communicatie tussen de nodes.
<!-- @os:linux -->
### 1. Netwerkinterfaces bepalen

Zoek op elke machine de naam van de netwerkinterface op en noteer deze (hieronder wordt ernaar verwezen als `IFNAME`). Voer uit:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dit geeft de interfacenaam direct weer, bijvoorbeeld:

```bash
enp191s0
```

### 2. Netwerkverbindingssnelheden verifiëren

Bevestig dat de verbinding actief is en op volledige snelheid werkt door de snelheid van uw interface te controleren:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opmerking**: Vervang `<IFNAME>` door de naam van de uitvoerinterface uit [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

U zou een snelheid van `10000Mb/s` moeten zien:

```bash
	Speed: 10000Mb/s
```

> **Opmerking**: Als de snelheid lager is dan `10000Mb/s` of de verbinding niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Bij sommige switches moet automatische onderhandeling worden uitgeschakeld en de verbindingssnelheid handmatig worden ingesteld; raadpleeg de documentatie van uw switch.

<!-- @os:end -->

<!-- @os:windows -->
### Netwerkverbindingssnelheid verifiëren

Controleer op elke machine de verbindingssnelheid van uw netwerkinterfaces:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Uw Ethernet-interface zou `Up` moeten zijn en op `10 Gbps` moeten werken:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Opmerking**: Als de snelheid lager is dan `10 Gbps` of de verbinding niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Bij sommige switches moet automatische onderhandeling worden uitgeschakeld en de verbindingssnelheid handmatig worden ingesteld; raadpleeg de documentatie van uw switch.

<!-- @os:end -->

## llama.cpp installeren

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Er zijn twee installatieopties beschikbaar:

- [Optie 1: Lemonade SDK (Aanbevolen)](#option-1-lemonade-sdk-recommended) - vooraf gebouwde binaries, snelste installatie
- [Optie 2: Handmatige bronbouw](#option-2-manual-source-build) - bouwen vanuit broncode met volledige controle over bouwvlaggen

### Optie 1: Lemonade SDK (Aanbevolen)

De Lemonade SDK biedt nightly builds van llama.cpp met AMD ROCm 7-versnelling, gericht op GPU's zoals gfx1151 (Strix Halo / Ryzen AI Max+ 395) en andere recente Radeon-architecturen.

<!-- @os:windows -->
#### Stap 1: De vooraf gebouwde binaries downloaden

Navigeer naar de pagina met de nieuwste release en download het archief dat overeenkomt met uw platform en GPU-doel:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download het bestand met de naam `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (waarbij `xxxx` het buildnummer is).

#### Stap 2: De binaries uitpakken

Pak het gedownloade archief uit:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Deze map bevat nu ROCm-ingeschakelde builds van `llama-cli.exe`, `llama-server.exe` en `rpc-server.exe`, vooraf gecompileerd voor uw Ryzen AI Halo-systeem.

#### Stap 3: GPU-detectie verifiëren

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
#### Stap 1: De vooraf gebouwde binaries downloaden

Navigeer naar de pagina met de nieuwste release en download het archief dat overeenkomt met uw platform en GPU-doel:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download het bestand met de naam `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (waarbij `xxxx` het buildnummer is).

#### Stap 2: De binaries uitpakken en voorbereiden

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Deze map bevat nu ROCm-ingeschakelde builds van `llama-cli`, `llama-server` en `rpc-server`, vooraf gecompileerd voor uw Ryzen AI Halo-systeem.

#### Stap 3: GPU-detectie verifiëren

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
Nu llama.cpp op elk knooppunt is voorbereid, gaat u verder naar [Het model downloaden](#downloading-the-model).

### Optie 2: Handmatige bronbouw

<!-- @os:windows -->
#### Stap 1: llama.cpp bouwen

Open de **x64 Native Tools Command Prompt** (geïnstalleerd met Visual Studio Build Tools) en kloon de repository:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Voeg HIP toe aan uw pad en bouw met ROCm- en RPC-ondersteuning:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Bouwvlag | Doel |
|----------|------|
| `-DGGML_HIP=ON` | Schakelt de ROCm/HIP-softwarestack in |
| `-DGGML_RPC=ON` | Schakelt RPC in voor gedistribueerde inferentie |
| `-DGPU_TARGETS=gfx1151` | Richt zich op de Ryzen AI Halo GPU (Radeon 8060s) |
| `-G Ninja` | Gebruikt het Ninja-bouwsysteem |

#### Stap 2: GPU-detectie verifiëren

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

#### Stap 3: HIP toevoegen aan uw gebruikerspad

De bovenstaande bouwstap heeft `%HIP_PATH%\bin` alleen voor de huidige sessie ingesteld. Om de HIP-bibliotheken beschikbaar te maken in elke terminal (niet alleen de x64 Native Tools Command Prompt), voegt u deze permanent toe aan uw gebruikers-`PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Nu llama.cpp op elk knooppunt is voorbereid, gaat u verder naar [Het model downloaden](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Stap 1: llama.cpp bouwen

Kloon de repository:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Bouw met ROCm- en RPC-ondersteuning:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Bouwvlag | Doel |
|----------|------|
| `-DGGML_HIP=ON` | Schakelt de ROCm-softwarestack in |
| `-DGGML_RPC=ON` | Schakelt RPC in voor gedistribueerde inferentie |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Schakelt rocWMMA in voor verbeterde Flash Attention op AMD GPU's |
| `-DAMDGPU_TARGETS="gfx1151"` | Richt zich op de Ryzen AI Halo GPU (Radeon 8060s) |

Voor meer bouwopties raadpleegt u de [llama.cpp-bouwdocumentatie](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Stap 2: GPU-detectie verifiëren

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

Nu llama.cpp op elk knooppunt is voorbereid, gaat u verder naar [Het model downloaden](#downloading-the-model).
<!-- @os:end -->

## Het model downloaden

Dit playbook maakt gebruik van [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), een model met 358 miljard parameters in de `Q4_K_XL`-kwantisering van [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Bij deze kwantisering vereist het model ongeveer 205 GB aan opslag en past het binnen het gecombineerde GPU-geheugen van twee Ryzen AI Halo-nodes.

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

> **Opmerking**: Het downloaden van het model moet worden voltooid op Machine 1 (de controller). De RPC-worker-nodes hebben geen lokale kopie van de modelbestanden nodig.

## Het model starten op het cluster

De RPC-engine (Remote Procedure Call) van llama.cpp stelt één llama.cpp-instantie in staat om modellagen via het netwerk te offloaden naar externe workers. Één machine fungeert als de **controller** (Machine 1), die tokenisatie, planning en orkestratie afhandelt. De andere machine draait een lichtgewicht **RPC-server** (Machine 2) die zijn GPU-geheugen en rekenkracht beschikbaar stelt aan de controller.

Bij het laden verdeelt llama.cpp het model over beide nodes. Zodra het model is geladen, verloopt de inferentie alsof het op één enkele versneller wordt uitgevoerd. RPC verwerkt tensoroverdrachten en synchronisatie op de achtergrond.

### Stap 1: De RPC-server starten (Machine 2)

Start op Machine 2 de RPC-server om de GPU-resources beschikbaar te stellen aan de controller:
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

| Vlag | Doel |
|------|------|
| `-p` | Poort waarop de RPC-server wordt uitgezonden |
| `-c` | Schakelt een lokale cache in voor grote tensoren, waardoor herhaalde netwerkoverdrachten tijdens het laden van het model worden vermeden |
| `--host` | IP-adres waaraan de RPC-server wordt gebonden (`0.0.0.0` voor alle interfaces) |

Voor meer opties raadpleegt u de [llama.cpp RPC-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Stap 2: Het model starten (Machine 1)

Met de RPC-server actief op Machine 2 start u de inferentie vanaf Machine 1 met behulp van `llama-cli` of `llama-server`.

#### llama-cli

`llama-cli` biedt een terminalgebaseerde interface voor directe interactie met het model. Het is ideaal voor benchmarking, foutopsporing en experimenten op laag niveau.

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

> **`<RPC_WORKER_IP>` vinden**: Voer op Machine 2 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking**: Voer dit commando uit in Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` vinden**: Voer op Machine 2 `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.

<!-- @os:end -->

Zodra het actief is, toont `llama-cli` de voortgang van het laden van het model en opent het een interactieve prompt waar u rechtstreeks met het model kunt chatten:

![llama-cli met GLM 4.7 over twee nodes](assets/llama-cli-example.png)

#### llama-server

`llama-server` stelt dezelfde inferentie-engine beschikbaar via een persistent serverproces met een geïntegreerde web-UI en een OpenAI-compatibele HTTP API. Dit is de voorkeurinterface voor langdurige implementaties, toegang door meerdere gebruikers en integratie met externe tooling.

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

> **`<RPC_WORKER_IP>` vinden**: Voer op Machine 2 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking**: Voer dit commando uit in Terminal (Powershell).

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

> **`<RPC_WORKER_IP>` vinden**: Voer op Machine 2 `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.
<!-- @os:end -->

Zodra de server is gestart, opent u `http://<HOST_IP>:8081` in uw browser om toegang te krijgen tot de ingebouwde web-UI. Dit biedt een browsergebaseerde chatinterface voor interactie met het model:

![llama-server web-UI met GLM 4.7 over twee nodes](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` vinden**: Voer op Machine 1 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` vinden**: Voer op Machine 1 `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.
<!-- @os:end -->

#### Parameterreferentie

| Vlag | Doel |
|------|------|
| `-m` | Pad naar het GGUF-modelbestand (gebruik de eerste shard, `00001-of-00005`) |
| `-c` | Contextgrootte in tokens. Grotere waarden gebruiken meer geheugen |
| `-fa on` | Schakelt rocWMMA Flash Attention in voor verbeterde prestaties op AMD GPU's |
| `-ngl 999` | Offloadt alle modellagen naar de GPU |
| `--no-mmap` | Schakelt geheugenafbeelding uit, waardoor laadtijden worden verkort wanneer de modelgrootte het systeemgeheugen overschrijdt maar binnen het VRAM past |
| `--host` | IP waaraan `llama-server` wordt gebonden (alleen `llama-server`) |
| `--port` | Poort waarop de HTTP API wordt aangeboden (alleen `llama-server`) |
| `--rpc` | Door komma's gescheiden lijst van RPC-worker-eindpunten (`IP:poort`) |

Voor volledig parametergebruik raadpleegt u de [llama-cli-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) en de [llama-server-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Volgende stappen

- **Verbinding maken met toepassingen van derden**: `llama-server` stelt een OpenAI-compatibele API beschikbaar. Wijs elke OpenAI-compatibele toepassing (zoals Open WebUI) naar `http://<HOST_IP>:8081` met een willekeurige tijdelijke API-sleutel (bijv. `none`) om verbinding te maken met uw cluster
- **Andere modellen verkennen**: Blader door gekwantiseerde GGUF's op [Hugging Face](https://huggingface.co/models?search=gguf) om modellen te vinden die passen binnen het gecombineerde GPU-geheugen van uw cluster
- **Uitbreiden naar vier nodes**: Voeg twee extra Ryzen AI Halo-systemen toe als aanvullende RPC-workers om toegang te krijgen tot modellen op de schaal van 1 biljoen parameters. Geef extra eindpunten door aan `--rpc` als een door komma's gescheiden lijst (bijv. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)