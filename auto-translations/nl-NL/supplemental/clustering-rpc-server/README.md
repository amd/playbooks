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

Uw Ryzen™ AI Halo is al in staat om grote taalmodellen lokaal uit te voeren. Clustering gaat hier nog verder in door het GPU-geheugen van meerdere systemen te combineren via een lokaal netwerk, waardoor u toegang krijgt tot nog grotere modellen met sterkere redenering, betere codegeneratie en dieper meertalig begrip, volledig op uw eigen hardware.

Deze playbook leert u hoe u twee Ryzen AI Halo-systemen clustert met behulp van de RPC-engine van llama.cpp en hoe u GLM 4.7, een model met 358 miljard parameters, uitvoert op beide machines met AMD ROCm™-acceleratie.

## Wat u leert

- Hoe u de VRAM-toewijzing op Ryzen AI Halo-systemen kunt uitbreiden
- llama.cpp installeren met ROCm- en RPC-ondersteuning
- Een RPC-worker configureren en gedistribueerde inferentie starten op twee nodes
- Een model met 358 miljard parameters uitvoeren op twee genetwerkte Ryzen AI Halo-systemen

## De geheugenconfiguratie instellen

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

<!-- @os:windows -->
Op Windows moet u, om grotere modellen te kunnen uitvoeren die meer geheugen vereisen, de AMD Variable Graphics Memory (iGPU VRAM)-toewijzing gebruiken.

Dit kan door het configuratiescherm AMD Software: Adrenalin Edition te openen en te navigeren naar: `Performance > Tuning > AMD Variable Graphics Memory`. Stel de waarde in op **96 GB**. Start het systeem opnieuw op zodat de wijzigingen worden toegepast.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Op Linux gebruikt ROCm een gedeelde systeemgeheugenpool, en deze pool is standaard geconfigureerd op de helft van het systeemgeheugen.

Deze hoeveelheid kan worden verhoogd door de paginainstelling van de Translation Table Manager (TTM) van de kernel te wijzigen, met behulp van de volgende instructies. AMD raadt aan om de minimale toegewezen VRAM in de BIOS in te stellen (0,5 GB).

* Installeer het pipx-hulpprogramma en voeg het pad voor door pipx geïnstalleerde wheels toe aan het systeemzoekpad.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installeer de amd-debug-tools wheel vanaf PyPI.
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

* Start het systeem opnieuw op zodat de wijzigingen worden toegepast.


<!-- @os:end -->
<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->
## Vereisten

### Hardware

Deze playbook vereist twee Ryzen AI Halo-eenheden en één Ethernet-switch, verbonden in een stertopologie waarbij elke eenheid rechtstreeks op de switch is aangesloten.

| Onderdeel | Aantal | Beschrijving |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Compute nodes die het cluster vormen |
| 10Gbps Ethernet-switch | 1 | Centrale switch voor communicatie tussen meerdere Ryzen AI Halo-nodes (minstens 2 poorten) |
| Ethernet-kabel | 2 | Verbindt elke Halo-eenheid met de switch (Cat 7 of hoger aanbevolen) |

> **Opmerking**: Er zijn twee Ethernet-switchpoorten nodig om de twee Ryzen AI Halo-eenheden te verbinden. Een derde poort is nodig als u toegang krijgt tot het model vanaf een aparte clientmachine in plaats van vanaf een van de Halo-eenheden.

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

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Sluit elke Ryzen AI Halo-eenheid aan op de Ethernet-switch met een Cat 7-kabel (of hoger). Dit vormt de 10Gbps-verbinding die wordt gebruikt voor snelle communicatie tussen de nodes.
<!-- @os:linux -->
### 1. Netwerkinterfaces bepalen

Zoek op elke machine de naam van de netwerkinterface en noteer deze (hierna aangeduid als `IFNAME`). Voer uit:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dit toont de interfacenaam direct, bijvoorbeeld:

```bash
enp191s0
```

### 2. Netwerklinksnelheden verifiëren

Bevestig dat de verbinding actief is en op volle snelheid draait door de snelheid van uw interface te controleren:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opmerking**: Vervang `<IFNAME>` door de uitvoerinterfacenaam uit [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

U zou een snelheid van `10000Mb/s` moeten zien:

```bash
	Speed: 10000Mb/s
```

> **Opmerking**: Als de snelheid lager is dan `10000Mb/s` of de verbinding niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat automatische onderhandeling wordt uitgeschakeld en de linksnelheid handmatig wordt ingesteld; raadpleeg de documentatie van uw switch.

<!-- @os:end -->

<!-- @os:windows -->
### Netwerklinksnelheid verifiëren

Controleer op elke machine de linksnelheid van uw netwerkinterfaces:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Uw Ethernet-interface moet `Up` zijn en draaien op `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Opmerking**: Als de snelheid lager is dan `10 Gbps` of de verbinding niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat automatische onderhandeling wordt uitgeschakeld en de linksnelheid handmatig wordt ingesteld; raadpleeg de documentatie van uw switch.

<!-- @os:end -->

## llama.cpp installeren

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Er zijn twee installatieopties beschikbaar:

- [Optie 1: Lemonade SDK (aanbevolen)](#option-1-lemonade-sdk-recommended) - vooraf gebouwde binaries, snelste installatie
- [Optie 2: Handmatige build vanaf broncode](#option-2-manual-source-build) - build vanaf de broncode met volledige controle over build-vlaggen

### Optie 1: Lemonade SDK (aanbevolen)

De Lemonade SDK biedt nightly builds van llama.cpp met AMD ROCm 7-acceleratie, gericht op GPU's zoals gfx1151 (Strix Halo / Ryzen AI Max+ 395) en andere recente Radeon-architecturen.

<!-- @os:windows -->
#### Stap 1: Download de vooraf gebouwde binaries

Ga naar de laatste release-pagina en download het archief dat overeenkomt met uw platform en GPU-doel:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download het bestand met de naam `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (waarbij `xxxx` het buildnummer is).

#### Stap 2: Pak de binaries uit

Pak het gedownloade archief uit:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Deze map bevat nu ROCm-compatibele builds van `llama-cli.exe`, `llama-server.exe` en `rpc-server.exe`, vooraf gecompileerd voor uw Ryzen AI Halo-systeem.

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

Ga naar de laatste release-pagina en download het archief dat overeenkomt met uw platform en GPU-doel:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download het bestand met de naam `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (waarbij `xxxx` het buildnummer is).

#### Stap 2: Pak de binaries uit en maak ze klaar

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Deze map bevat nu ROCm-compatibele builds van `llama-cli`, `llama-server` en `rpc-server`, vooraf gecompileerd voor uw Ryzen AI Halo-systeem.

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
Zodra llama.cpp op elke node is voorbereid, gaat u verder met [Het model downloaden](#downloading-the-model).

### Optie 2: Handmatige build vanuit de broncode

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

De bovenstaande buildstap heeft `%HIP_PATH%\bin` alleen voor de huidige sessie ingesteld. Om de HIP-bibliotheken beschikbaar te maken in elke terminal (niet alleen de x64 Native Tools Command Prompt), voegt u het permanent toe aan uw gebruikers-`PATH`:

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
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build-vlag | Doel |
|-----------|---------|
| `-DGGML_HIP=ON` | Schakelt de ROCm-softwarestack in |
| `-DGGML_RPC=ON` | Schakelt RPC in voor gedistribueerde inferentie |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Schakelt rocWMMA in voor verbeterde Flash Attention op AMD GPU's |
| `-DAMDGPU_TARGETS="gfx1151"` | Richt zich op de Ryzen AI Halo GPU (Radeon 8060s) |

Zie voor meer buildopties de [llama.cpp-builddocumentatie](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Zodra llama.cpp op elke node is voorbereid, gaat u verder met [Het model downloaden](#downloading-the-model).
<!-- @os:end -->

## Het model downloaden

Dit playbook gebruikt [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), een model met 358 miljard parameters in de `Q4_K_XL`-kwantisatie van [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Bij deze kwantisatie vereist het model ongeveer 205 GB aan opslag en past het binnen het gecombineerde GPU-geheugen van twee Ryzen AI Halo-nodes.

Download de GGUF-bestanden met de Hugging Face CLI:
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

> **Opmerking**: Het downloaden van het model moet worden voltooid op Machine 1 (de controller). De RPC-workernodes hebben geen lokale kopie van de modelbestanden nodig.

## Het model op de cluster starten

De llama.cpp RPC-engine (Remote Procedure Call) stelt één enkele llama.cpp-instantie in staat om modellagen via het netwerk uit te besteden aan externe workers. Eén machine fungeert als de **controller** (Machine 1), en handelt tokenisatie, planning en orkestratie af. De andere machine draait een lichtgewicht **RPC-server** (Machine 2) die zijn GPU-geheugen en rekenkracht beschikbaar stelt aan de controller.

Bij het laden verdeelt llama.cpp het model over beide nodes. Zodra het geladen is, verloopt de inferentie alsof deze op één enkele accelerator draait. RPC handelt de overdracht en synchronisatie van tensors op de achtergrond af.

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
| `-c` | Schakelt een lokale cache in voor grote tensors, waardoor herhaalde netwerkoverdrachten tijdens het laden van het model worden voorkomen |
| `--host` | IP-adres waaraan de RPC-server wordt gekoppeld (`0.0.0.0` voor alle interfaces) |

Zie voor meer opties de [llama.cpp RPC-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Stap 2: Start het model (Machine 1)

Terwijl de RPC-server op Machine 2 draait, start u de inferentie vanaf Machine 1 met behulp van `llama-cli` of `llama-server`.

#### llama-cli

`llama-cli` biedt een op de terminal gebaseerde interface voor directe interactie met het model. Het is ideaal voor benchmarking, debuggen en experimenteren op laag niveau.

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

> **Het vinden van `<RPC_WORKER_IP>`**: Voer op Machine 2 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking**: Voer deze opdracht uit in Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Het vinden van `<RPC_WORKER_IP>`**: Voer op Machine 2 `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.

<!-- @os:end -->

Eenmaal actief toont `llama-cli` de voortgang van het laden van het model en opent een interactieve prompt waarin u direct met het model kunt chatten:

![llama-cli met GLM 4.7 op twee nodes](assets/llama-cli-example.png)
#### llama-server

`llama-server` biedt dezelfde inference-engine via een persistent serverproces met een geïntegreerde web-UI en een OpenAI-compatibele HTTP-API. Dit is de voorkeursinterface voor langer draaiende implementaties, toegang voor meerdere gebruikers en integratie met externe tooling.

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

Open na het starten `http://<HOST_IP>:8081` in uw browser om toegang te krijgen tot de ingebouwde web-UI. Dit biedt een browsergebaseerde chatinterface voor interactie met het model:

![llama-server web UI met GLM 4.7 op twee nodes](assets/llama-server-example.png)

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
| `-fa on` | Schakelt rocWMMA Flash Attention in voor verbeterde prestaties op AMD-GPU's |
| `-ngl 999` | Verplaatst alle modellagen naar de GPU |
| `--no-mmap` | Schakelt memory-mapping uit, wat de laadtijden verkort wanneer de modelgrootte groter is dan het systeem-RAM maar wel past in VRAM |
| `--host` | IP waaraan `llama-server` gebonden moet worden (alleen `llama-server`) |
| `--port` | Poort waarop de HTTP-API wordt aangeboden (alleen `llama-server`) |
| `--rpc` | Kommagescheiden lijst van RPC-worker-eindpunten (`IP:port`) |

Raadpleeg voor volledig gebruik van de parameters de [llama-cli documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) en [llama-server documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Volgende stappen

- **Applicaties van derden verbinden**: `llama-server` biedt een OpenAI-compatibele API. Wijs een OpenAI-compatibele applicatie (zoals Open WebUI) naar `http://<HOST_IP>:8081` met een willekeurige placeholder-API-sleutel (bijv. `none`) om verbinding te maken met uw cluster
- **Andere modellen verkennen**: Blader door gekwantiseerde GGUF's op [Hugging Face](https://huggingface.co/models?search=gguf) om modellen te vinden die passen binnen het gecombineerde GPU-geheugen van uw cluster
- **Opschalen naar vier nodes**: Voeg twee extra Ryzen AI Halo-systemen toe als extra RPC-workers om toegang te krijgen tot modellen op de schaal van 1 biljoen parameters. Geef extra eindpunten door aan `--rpc` als een kommagescheiden lijst (bijv. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)