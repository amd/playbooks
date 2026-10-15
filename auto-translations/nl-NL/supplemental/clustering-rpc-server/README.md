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

Uw Ryzen™ AI Halo is al in staat om grote taalmodellen lokaal uit te voeren. Clustering gaat hier nog een stap verder door het GPU-geheugen van meerdere systemen over een lokaal netwerk te combineren, waardoor u toegang krijgt tot nog grotere modellen met sterkere redeneervaardigheden, betere codegeneratie en diepgaander meertalig begrip, allemaal volledig op uw eigen hardware.

Deze handleiding leert u hoe u twee Ryzen AI Halo-systemen clustert met de RPC-engine van llama.cpp en hoe u GLM 4.7, een model met 358 miljard parameters, uitvoert op beide machines met AMD ROCm™-versnelling.

## Wat u zult leren

- Hoe u de VRAM-toewijzing op Ryzen AI Halo-systemen kunt uitbreiden
- Het installeren van llama.cpp met ondersteuning voor ROCm en RPC
- Het configureren van een RPC-worker en het starten van gedistribueerde inferentie op twee nodes
- Het uitvoeren van een model met 358 miljard parameters op twee genetwerkte Ryzen AI Halo-systemen

## De geheugenconfiguratie instellen

> **Opmerking**: Voltooi deze stap op zowel Machine 1 als Machine 2.

<!-- @os:windows -->
Op Windows moeten we, om grotere modellen uit te voeren die meer geheugen vereisen, de toewijzing van AMD Variable Graphics Memory (iGPU VRAM) gebruiken.

Dit kan door het configuratiescherm AMD Software: Adrenalin Edition te openen en te navigeren naar: `Performance > Tuning > AMD Variable Graphics Memory`. Stel de waarde in op **96 GB**. Start het systeem opnieuw op om de wijzigingen door te voeren.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Op Linux gebruikt ROCm een gedeelde systeemgeheugenpool, en deze pool is standaard geconfigureerd op de helft van het systeemgeheugen.

Deze hoeveelheid kan worden verhoogd door de Translation Table Manager (TTM)-paginainstelling van de kernel te wijzigen, volgens de onderstaande instructies. AMD raadt aan om het minimale toegewezen VRAM in de BIOS in te stellen (0,5 GB).

* Installeer de pipx-utility en voeg het pad voor door pipx geïnstalleerde wheels toe aan het zoekpad van het systeem.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installeer de amd-debug-tools wheel vanaf PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Voer de amd-ttm-tool uit om de huidige instellingen voor gedeeld geheugen op te vragen.
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

Voor deze handleiding zijn twee Ryzen AI Halo-eenheden en één ethernetswitch nodig, verbonden in een stertopologie waarbij elke eenheid rechtstreeks met de switch is verbonden.

| Onderdeel | Aantal | Beschrijving |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Compute-nodes die het cluster vormen |
| 10Gbps-ethernetswitch | 1 | Centrale switch om communicatie tussen meerdere Ryzen AI Halo-nodes mogelijk te maken (minstens 2 poorten) |
| Ethernetkabel | 2 | Verbindt elke Halo-eenheid met de switch (Cat 7 of hoger aanbevolen) |

> **Opmerking**: Er zijn twee poorten op de ethernetswitch nodig om de twee Ryzen AI Halo-eenheden te verbinden. Een derde poort is vereist als u het model benadert vanaf een aparte clientmachine in plaats van vanaf een van de Halo-eenheden.

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

## Fysieke hardware-installatie

> **Opmerking**: Voltooi deze stap op zowel Machine 1 als Machine 2.

Sluit elke Ryzen AI Halo-eenheid aan op de ethernetswitch met een Cat 7-kabel (of hoger). Dit brengt de 10Gbps-verbinding tot stand die wordt gebruikt voor snelle communicatie tussen de nodes.
<!-- @os:linux -->
### 1. De netwerkinterfaces bepalen

Zoek op elke machine de naam van de netwerkinterface en noteer deze (hieronder aangeduid als `IFNAME`). Voer uit:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dit toont de interfacenaam direct, bijvoorbeeld:

```bash
enp191s0
```

### 2. De netwerklinksnelheden verifiëren

Controleer of de verbinding actief is en op volle snelheid draait door de snelheid van uw interface te controleren:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opmerking**: Vervang `<IFNAME>` door de uitvoerinterfacenaam uit [1. De netwerkinterfaces bepalen](#1-determine-network-interfaces)

U zou een snelheid van `10000Mb/s` moeten zien:

```bash
	Speed: 10000Mb/s
```

> **Opmerking**: Als de snelheid lager is dan `10000Mb/s` of de verbinding niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat auto-onderhandeling wordt uitgeschakeld en de linksnelheid handmatig wordt ingesteld; raadpleeg de documentatie van uw switch.

<!-- @os:end -->

<!-- @os:windows -->
### De netwerklinksnelheid verifiëren

Controleer op elke machine de linksnelheid van uw netwerkinterfaces:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Uw ethernetinterface moet `Up` zijn en draaien op `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Opmerking**: Als de snelheid lager is dan `10 Gbps` of de verbinding niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat auto-onderhandeling wordt uitgeschakeld en de linksnelheid handmatig wordt ingesteld; raadpleeg de documentatie van uw switch.

<!-- @os:end -->

## llama.cpp installeren

> **Opmerking**: Voltooi deze stap op zowel Machine 1 als Machine 2.

Er zijn twee installatieopties beschikbaar:

- [Optie 1: Lemonade SDK (Aanbevolen)](#option-1-lemonade-sdk-recommended) - vooraf gebouwde binaries, snelste installatie
- [Optie 2: Handmatige build vanaf broncode](#option-2-manual-source-build) - bouwen vanaf broncode met volledige controle over buildvlaggen

### Optie 1: Lemonade SDK (Aanbevolen)

De Lemonade SDK biedt nightly builds van llama.cpp met AMD ROCm 7-versnelling, gericht op GPU's zoals gfx1151 (Strix Halo / Ryzen AI Max+ 395) en andere recente Radeon-architecturen.

<!-- @os:windows -->
#### Stap 1: Download de vooraf gebouwde binaries

Navigeer naar de laatste release-pagina en download het archief dat overeenkomt met uw platform en GPU-doel:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download het bestand met de naam `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (waarbij `xxxx` het buildnummer is).

#### Stap 2: Pak de binaries uit

Pak het gedownloade archief uit:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Deze map bevat nu ROCm-geschikte builds van `llama-cli.exe`, `llama-server.exe` en `rpc-server.exe`, vooraf gecompileerd voor uw Ryzen AI Halo-systeem.

#### Stap 3: Controleer GPU-detectie

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
#### Stap 1: Download de vooraf gebouwde binaries

Navigeer naar de laatste release-pagina en download het archief dat overeenkomt met uw platform en GPU-doel:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download het bestand met de naam `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (waarbij `xxxx` het buildnummer is).

#### Stap 2: Pak de binaries uit en bereid ze voor

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Deze map bevat nu ROCm-geschikte builds van `llama-cli`, `llama-server` en `rpc-server`, vooraf gecompileerd voor uw Ryzen AI Halo-systeem.

#### Stap 3: Controleer GPU-detectie

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
Zodra llama.cpp op elk knooppunt is voorbereid, gaat u verder met [Het model downloaden](#downloading-the-model).

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

| Buildvlag | Doel |
|-----------|---------|
| `-DGGML_HIP=ON` | Schakelt de ROCm/HIP-softwarestack in |
| `-DGGML_RPC=ON` | Schakelt RPC in voor gedistribueerde inferentie |
| `-DGPU_TARGETS=gfx1151` | Richt zich op de Ryzen AI Halo GPU (Radeon 8060s) |
| `-G Ninja` | Gebruikt het Ninja-buildsysteem |

#### Stap 2: Controleer GPU-detectie

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

De bovenstaande buildstap heeft `%HIP_PATH%\bin` alleen voor de huidige sessie ingesteld. Om de HIP-bibliotheken beschikbaar te maken in elke terminal (niet alleen de x64 Native Tools Command Prompt), voegt u dit permanent toe aan uw gebruikers-`PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Zodra llama.cpp op elk knooppunt is voorbereid, gaat u verder met [Het model downloaden](#downloading-the-model).
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

| Buildvlag | Doel |
|-----------|---------|
| `-DGGML_HIP=ON` | Schakelt de ROCm-softwarestack in |
| `-DGGML_RPC=ON` | Schakelt RPC in voor gedistribueerde inferentie |
| `-DAMDGPU_TARGETS="gfx1151"` | Richt zich op de Ryzen AI Halo GPU (Radeon 8060s) |

Raadpleeg voor meer buildopties de [llama.cpp-builddocumentatie](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Stap 2: Controleer GPU-detectie

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

Zodra llama.cpp op elk knooppunt is voorbereid, gaat u verder met [Het model downloaden](#downloading-the-model).
<!-- @os:end -->

## Het model downloaden

Dit playbook gebruikt [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), een model met 358B parameters in de `Q4_K_XL`-kwantisering van [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Bij deze kwantisering vereist het model ongeveer 205 GB opslag en past het binnen het gecombineerde GPU-geheugen van twee Ryzen AI Halo-knooppunten.

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

> **Opmerking**: Het downloaden van het model moet worden voltooid op Machine 1 (de controller). De RPC-workerknooppunten hebben geen lokale kopie van de modelbestanden nodig.

## Het model op de cluster starten

De llama.cpp RPC-engine (Remote Procedure Call) stelt een enkele llama.cpp-instantie in staat om modellagen over het netwerk over te dragen naar externe workers. Eén machine fungeert als de **controller** (Machine 1) en handelt tokenisatie, planning en orchestratie af. De andere machine draait een lichtgewicht **RPC-server** (Machine 2) die zijn GPU-geheugen en rekenkracht beschikbaar stelt aan de controller.

Bij het laden verdeelt llama.cpp het model over beide knooppunten. Eenmaal geladen, verloopt de inferentie alsof deze op één enkele accelerator draait. RPC handelt tensoroverdrachten en synchronisatie op de achtergrond af.

### Stap 1: Start de RPC-server (Machine 2)

Start op Machine 2 de RPC-server om de GPU-bronnen ervan aan de controller beschikbaar te stellen:
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
| `-c` | Schakelt een lokale cache in voor grote tensors, waardoor herhaalde netwerkoverdrachten tijdens het laden van het model worden vermeden |
| `--host` | IP-adres waaraan de RPC-server wordt gebonden (`0.0.0.0` voor alle interfaces) |

Raadpleeg voor meer opties de [llama.cpp RPC-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Stap 2: Start het model (Machine 1)

Nu de RPC-server op Machine 2 draait, start u de inferentie vanaf Machine 1 met behulp van ofwel `llama-cli` ofwel `llama-server`.

#### llama-cli

`llama-cli` biedt een terminalgebaseerde interface om rechtstreeks met het model te communiceren. Het is ideaal voor benchmarking, debuggen en laagniveau-experimenten.

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
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` vinden**: Voer op Machine 2 `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.

<!-- @os:end -->

Zodra deze draait, toont `llama-cli` de voortgang van het laden van het model en opent een interactieve prompt waarin u rechtstreeks met het model kunt chatten:

![llama-cli draait GLM 4.7 over twee knooppunten](assets/llama-cli-example.png)
#### llama-server

`llama-server` biedt dezelfde inferentie-engine aan via een persistent serverproces met een geïntegreerde webinterface en een OpenAI-compatibele HTTP-API. Dit is de voorkeursinterface voor langer lopende implementaties, toegang door meerdere gebruikers en integratie met externe tools.

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
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` vinden**: Voer op Machine 2 `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.
<!-- @os:end -->

Zodra de server is gestart, open je `http://<HOST_IP>:8081` in je browser om toegang te krijgen tot de ingebouwde webinterface. Dit biedt een op de browser gebaseerde chatinterface om met het model te communiceren:

![llama-server webinterface met GLM 4.7 op twee nodes](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` vinden**: Voer op Machine 1 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` vinden**: Voer op Machine 1 `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.
<!-- @os:end -->

#### Parameterreferentie

| Vlag | Doel |
|------|---------|
| `-m` | Pad naar het GGUF-modelbestand (gebruik het eerste shard, `00001-of-00005`) |
| `-c` | Contextgrootte in tokens. Grotere waarden gebruiken meer geheugen |
| `-fa on` | Schakelt rocWMMA Flash Attention in voor verbeterde prestaties op AMD GPU's |
| `-ngl 999` | Verplaatst alle modellagen naar de GPU |
| `-lm none` | Stelt de modelladingsmodus in op `none`, waardoor memory-mapping wordt uitgeschakeld om de laadtijden te verkorten wanneer de modelgrootte groter is dan het systeem-RAM maar wel binnen het VRAM past |
| `--host` | IP waaraan `llama-server` wordt gebonden (alleen `llama-server`) |
| `--port` | Poort waarop de HTTP-API wordt aangeboden (alleen `llama-server`) |
| `--rpc` | Door komma's gescheiden lijst van RPC-worker-eindpunten (`IP:port`) |

Raadpleeg voor volledig parametergebruik de [llama-cli-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) en [llama-server-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Volgende stappen

- **Applicaties van derden verbinden**: `llama-server` biedt een OpenAI-compatibele API. Wijs elke OpenAI-compatibele applicatie (zoals Open WebUI) naar `http://<HOST_IP>:8081` met een willekeurige placeholder-API-sleutel (bijv. `none`) om verbinding te maken met je cluster
- **Andere modellen verkennen**: Blader door gekwantiseerde GGUF's op [Hugging Face](https://huggingface.co/models?search=gguf) om modellen te vinden die binnen het gecombineerde GPU-geheugen van je cluster passen
- **Opschalen naar vier nodes**: Voeg twee extra Ryzen AI Halo-systemen toe als aanvullende RPC-workers om toegang te krijgen tot modellen op een schaal van 1 biljoen parameters. Geef extra eindpunten door aan `--rpc` als een door komma's gescheiden lijst (bijv. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)