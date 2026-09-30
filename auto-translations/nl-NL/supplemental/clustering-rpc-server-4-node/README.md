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

# Vier Ryzen™ AI Halo's clusteren met RPC

## Overzicht

Uw Ryzen™ AI Halo is al in staat om grote taalmodellen lokaal uit te voeren. Clustering gaat hierin nog verder door het GPU-geheugen van meerdere systemen via een lokaal netwerk te combineren, waardoor u toegang krijgt tot nog grotere modellen met sterker redeneervermogen, betere codegeneratie en dieper meertalig begrip, volledig op uw eigen hardware.

Deze handleiding leert u hoe u vier Ryzen AI Halo-systemen clustert met behulp van de RPC-engine van llama.cpp en Kimi K2.6 uitvoert, een groot mixture-of-experts-model, op alle vier de machines met AMD ROCm™-acceleratie.

## Wat u zult leren

- Hoe u de VRAM-toewijzing op Ryzen AI Halo-systemen kunt uitbreiden
- Het installeren van llama.cpp met ondersteuning voor ROCm en RPC
- Het configureren van RPC-workers en het starten van gedistribueerde inferentie op vier nodes
- Het uitvoeren van een model met 1T parameters op vier genetwerkte Ryzen AI Halo-systemen

## De geheugenconfiguratie instellen

> **Opmerking**: Voer deze stap uit op alle vier de machines (Machine 1 tot en met Machine 4).

<!-- @os:windows -->
Op Windows moeten we, om grotere modellen uit te voeren die meer geheugen vereisen, de AMD Variable Graphics Memory-toewijzing (iGPU VRAM) gebruiken.

Dit kan door het bedieningspaneel AMD Software: Adrenalin Edition te openen en te navigeren naar: `Performance > Tuning > AMD Variable Graphics Memory`. Stel de waarde in op **96 GB**. Start het systeem opnieuw op om de wijzigingen door te voeren.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Op Linux gebruikt ROCm een gedeelde systeemgeheugenpool, en deze pool is standaard geconfigureerd op de helft van het systeemgeheugen.

Deze hoeveelheid kan worden verhoogd door de Translation Table Manager (TTM)-paginainstelling van de kernel te wijzigen, volgens de onderstaande instructies. AMD raadt aan om het minimale toegewezen VRAM in de BIOS in te stellen (0,5 GB).

* Installeer het pipx-hulpprogramma en voeg het pad voor door pipx geïnstalleerde wheels toe aan het zoekpad van het systeem.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installeer de amd-debug-tools-wheel vanaf PyPI.
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

* Start het systeem opnieuw op zodat de wijzigingen worden doorgevoerd.


<!-- @os:end -->
<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->
## Vereisten

### Hardware

Deze handleiding vereist vier Ryzen AI Halo-eenheden en één Ethernet-switch, verbonden in een stertopologie waarbij elke eenheid rechtstreeks op de switch is aangesloten.

| Component | Aantal | Beschrijving |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Computernodes die het cluster vormen |
| 10Gbps Ethernet-switch | 1 | Centrale switch om communicatie tussen meerdere Ryzen AI Halo-nodes mogelijk te maken (minimaal 4 poorten) |
| Ethernet-kabel | 4 | Verbindt elke Halo-eenheid met de switch (Cat 7 of hoger aanbevolen) |

> **Opmerking**: Er zijn vier Ethernet-switchpoorten nodig om de vier Ryzen AI Halo-eenheden te verbinden. Een vijfde poort is nodig als u het model benadert vanaf een aparte clientmachine in plaats van vanaf een van de Halo-eenheden.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Installeer:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) met de werklast **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fysieke hardware-installatie

> **Opmerking**: Voer deze stap uit op alle vier de machines (Machine 1 tot en met Machine 4).

Sluit elke Ryzen AI Halo-eenheid aan op de Ethernet-switch met een Cat 7-kabel (of hoger). Dit brengt de 10Gbps-verbinding tot stand die wordt gebruikt voor snelle communicatie tussen de nodes.
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

Controleer of de link actief is en op volle snelheid draait door de snelheid van uw interface te controleren:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opmerking**: Vervang `<IFNAME>` door de uitvoerinterfacenaam uit [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

U zou een snelheid van `10000Mb/s` moeten zien:

```bash
	Speed: 10000Mb/s
```

> **Opmerking**: Als de snelheid lager is dan `10000Mb/s` of de link niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat auto-onderhandeling wordt uitgeschakeld en de linksnelheid handmatig wordt ingesteld; raadpleeg de documentatie van uw switch.

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

> **Opmerking**: Als de snelheid lager is dan `10 Gbps` of de link niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat auto-onderhandeling wordt uitgeschakeld en de linksnelheid handmatig wordt ingesteld; raadpleeg de documentatie van uw switch.

<!-- @os:end -->

## llama.cpp installeren

> **Opmerking**: Voer deze stap uit op alle vier de machines (Machine 1 tot en met Machine 4).

Er zijn twee installatieopties beschikbaar:

- [Optie 1: Lemonade SDK (aanbevolen)](#option-1-lemonade-sdk-recommended) - vooraf gebouwde binaries, snelste installatie
- [Optie 2: Handmatige build vanaf broncode](#option-2-manual-source-build) - bouwen vanaf de broncode met volledige controle over de build-vlaggen

### Optie 1: Lemonade SDK (aanbevolen)

De Lemonade SDK biedt nightly builds van llama.cpp met AMD ROCm 7-acceleratie, gericht op GPU's zoals gfx1151 (Strix Halo / Ryzen AI Max+ 395) en andere recente Radeon-architecturen.

<!-- @os:windows -->
#### Stap 1: Download de vooraf gebouwde binaries

Ga naar de nieuwste releasepagina en download het archief dat overeenkomt met uw platform en GPU-doel:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download het bestand met de naam `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (waarbij `xxxx` het buildnummer is).

#### Stap 2: Pak de binaries uit

Pak het gedownloade archief uit:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Deze map bevat nu ROCm-compatibele builds van `llama-cli.exe`, `llama-server.exe` en `ggml-rpc-server.exe`, vooraf gecompileerd voor uw Ryzen AI Halo-systeem.

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

Ga naar de nieuwste releasepagina en download het archief dat overeenkomt met uw platform en GPU-doel:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download het bestand met de naam `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (waarbij `xxxx` het buildnummer is).

#### Stap 2: Pak de binaries uit en bereid ze voor

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
Nu llama.cpp op elk knooppunt gereed is, gaat u verder naar [Het model downloaden](#downloading-the-model).

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

De bovenstaande buildstap heeft `%HIP_PATH%\bin` alleen voor de huidige sessie ingesteld. Om de HIP-bibliotheken in elke terminal beschikbaar te maken (niet alleen in de x64 Native Tools Command Prompt), voegt u dit permanent toe aan uw gebruikers-`PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Nu llama.cpp op elk knooppunt gereed is, gaat u verder naar [Het model downloaden](#downloading-the-model).
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

Nu llama.cpp op elk knooppunt gereed is, gaat u verder naar [Het model downloaden](#downloading-the-model).
<!-- @os:end -->

## Het model downloaden

Dit playbook gebruikt [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) in de `UD-Q2_K_XL`-kwantisering van [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Deze kwantisering past binnen het gecombineerde GPU-geheugen van vier Ryzen AI Halo-knooppunten.

Download de GGUF-bestanden met de Hugging Face CLI:
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

> **Opmerking**: Het downloaden van het model moet worden voltooid op Machine 1 (de controller). De RPC-workerknooppunten (Machines 2, 3 en 4) hebben geen lokale kopie van de modelbestanden nodig.

## Het model op de cluster starten

Met de llama.cpp RPC-engine (Remote Procedure Call) kan één llama.cpp-instantie modellagen offloaden naar externe workers via het netwerk. Eén machine fungeert als de **controller** (Machine 1) en behandelt tokenisatie, planning en orkestratie. De andere drie machines draaien elk een lichtgewicht **RPC-server** (Machines 2, 3 en 4) die hun GPU-geheugen en rekenkracht beschikbaar stellen aan de controller.

Tijdens het laden verdeelt llama.cpp het model over alle vier de knooppunten. Zodra het geladen is, verloopt de inferentie alsof deze op één enkele accelerator draait. RPC handelt tensoroverdrachten en synchronisatie op de achtergrond af.

### Stap 1: Start de RPC-servers (Machines 2, 3 en 4)

Start op elk van Machines 2, 3 en 4 de RPC-server om de GPU-bronnen aan de controller beschikbaar te stellen:
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
| `-c` | Schakelt een lokale cache in voor grote tensoren, waardoor herhaalde netwerkoverdrachten tijdens het laden van het model worden vermeden |
| `--host` | IP-adres waaraan de RPC-server wordt gekoppeld (`0.0.0.0` voor alle interfaces) |

Raadpleeg voor meer opties de [llama.cpp RPC-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Stap 2: Start het model (Machine 1)

Nu de RPC-servers op Machines 2, 3 en 4 draaien, start u de inferentie vanaf Machine 1 met behulp van `llama-cli` of `llama-server`.
#### llama-cli

`llama-cli` biedt een terminalgebaseerde interface voor directe interactie met het model. Het is ideaal voor benchmarking, debuggen en laagdrempelig experimenteren.

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

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` vinden**: Voer op elk van Machine 2, 3 en 4 het commando `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking**: Voer dit commando uit in Terminal (Powershell).

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

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` vinden**: Voer op elk van Machine 2, 3 en 4 het commando `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.

<!-- @os:end -->

Zodra het draait, toont `llama-cli` de voortgang van het laden van het model en opent een interactieve prompt waarin u direct met het model kunt chatten:

![llama-cli met Kimi K2.6 op vier nodes](assets/llama-cli-example.png)

#### llama-server

`llama-server` biedt dezelfde inference-engine via een blijvend serverproces met een geïntegreerde web-UI en een OpenAI-compatibele HTTP-API. Dit is de voorkeursinterface voor langer lopende implementaties, toegang door meerdere gebruikers en integratie met externe tools.

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

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` vinden**: Voer op elk van Machine 2, 3 en 4 het commando `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking**: Voer dit commando uit in Terminal (Powershell).

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

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` vinden**: Voer op elk van Machine 2, 3 en 4 het commando `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.
<!-- @os:end -->

Open na het starten `http://<HOST_IP>:8081` in uw browser om toegang te krijgen tot de ingebouwde web-UI. Deze biedt een browsergebaseerde chatinterface voor interactie met het model:

![llama-server web-UI met Kimi K2.6 op vier nodes](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` vinden**: Voer op Machine 1 het commando `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` vinden**: Voer op Machine 1 het commando `ipconfig | findstr /C:"IPv4"` uit in Terminal (Powershell) om het lokale IP-adres te vinden.
<!-- @os:end -->

#### Parameterreferentie

| Vlag | Doel |
|------|---------|
| `-m` | Pad naar het GGUF-modelbestand (gebruik de eerste shard, `00001-of-00008`) |
| `-c` | Contextgrootte in tokens. Grotere waarden gebruiken meer geheugen |
| `-fa on` | Schakelt rocWMMA Flash Attention in voor verbeterde prestaties op AMD GPU's |
| `-ngl 999` | Verplaatst alle modellagen naar de GPU |
| `-lm none` | Stelt de modelladermodus in op `none`, waardoor memory-mapping wordt uitgeschakeld om laadtijden te verkorten wanneer de modelgrootte groter is dan het systeem-RAM maar wel in het VRAM past |
| `-b` | Logische batchgrootte in tokens. Instellen op 4096 balanceert doorvoer en geheugengebruik over de nodes |
| `-ub` | Fysieke (micro) batchgrootte voor promptverwerking. Overeenkomen met `-b` voorkomt onnodige chunking-overhead |
| `--host` | IP waarop `llama-server` moet worden gebonden (alleen `llama-server`) |
| `--port` | Poort waarop de HTTP-API wordt aangeboden (alleen `llama-server`) |
| `--rpc` | Komma-gescheiden lijst van RPC-worker-eindpunten (`IP:port`) |

Zie voor volledig gebruik van parameters de [llama-cli-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) en de [llama-server-documentatie](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Volgende stappen

- **Applicaties van derden verbinden**: `llama-server` biedt een OpenAI-compatibele API. Wijs elke OpenAI-compatibele applicatie (zoals Open WebUI) naar `http://<HOST_IP>:8081` met een willekeurige tijdelijke API-sleutel (bijv. `none`) om verbinding te maken met uw cluster
- **Andere modellen verkennen**: Blader door gekwantiseerde GGUF's op [Hugging Face](https://huggingface.co/models?search=gguf) om modellen te vinden die passen binnen het gecombineerde GPU-geheugen van uw cluster
- **Opschalen naar meer dan vier nodes**: Voeg extra Ryzen AI Halo-systemen toe als extra RPC-workers om toegang te krijgen tot modellen groter dan 1 biljoen parameters. Geef extra eindpunten door aan `--rpc` als een komma-gescheiden lijst (bijv. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)