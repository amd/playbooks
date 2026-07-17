<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Klustring av två Ryzen™ AI Halos med RPC

## Översikt

Din Ryzen™ AI Halo kan redan köra stora språkmodeller lokalt. Klustring tar detta ett steg längre genom att kombinera GPU-minnet från flera system över ett lokalt nätverk, vilket ger dig tillgång till ännu större modeller med starkare resonemang, bättre kodgenerering och djupare flerspråkig förståelse – allt helt på din egen hårdvara.

Den här spelboken lär dig hur du klustrar två Ryzen AI Halo-system med llama.cpp:s RPC-motor och kör GLM 4.7, en modell med 358 miljarder parametrar, över båda maskinerna med AMD ROCm™-acceleration.

## Vad du kommer att lära dig

- Hur du utökar VRAM-allokeringen på Ryzen AI Halo-system
- Installation av llama.cpp med ROCm- och RPC-stöd
- Konfigurering av en RPC-worker och start av distribuerad inferens över två noder
- Körning av en modell med 358 miljarder parametrar över två nätverksanslutna Ryzen AI Halo-system

## Ange minneskonfigurationen

> **Obs**: Slutför det här steget på både Maskin 1 och Maskin 2.

<!-- @os:windows -->
På Windows, för att köra större modeller som kräver mer minne, behöver vi använda AMD Variable Graphics Memory (iGPU VRAM)-allokeringen.

Detta kan göras genom att öppna kontrollpanelen AMD Software: Adrenalin Edition och navigera till: `Performance > Tuning > AMD Variable Graphics Memory`. Ange värdet till **96 GB**. Starta om systemet för att ändringarna ska träda i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
På Linux använder ROCm en delad systemminnespol, och denna pool är som standard konfigurerad till hälften av systemminnet.

Denna mängd kan ökas genom att ändra kärnans TTM-sidinställning (Translation Table Manager), med följande instruktioner. AMD rekommenderar att ange det minsta dedikerade VRAM i BIOS (0,5 GB).

* Installera pipx-verktyget och lägg till sökvägen för pipx-installerade paket i systemets sökväg.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installera amd-debug-tools-paketet från PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kör amd-ttm-verktyget för att fråga de aktuella inställningarna för delat minne.
  ```bash
  amd-ttm
  ```

* Konfigurera om inställningarna för delat minne till **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Starta om systemet för att ändringarna ska träda i kraft.


<!-- @os:end -->
<!-- @device:halo_box -->
## Kontrollera programvaruuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->
## Förutsättningar

### Hårdvara

Den här spelboken kräver två Ryzen AI Halo-enheter och en Ethernet-switch, anslutna i en stjärntopologi där varje enhet är direkt ansluten till switchen.

| Komponent | Antal | Beskrivning |
|-----------|-------|-------------|
| Ryzen AI Halo | 2 | Beräkningsnoder som bildar klustret |
| 10 Gbps Ethernet-switch | 1 | Central switch för kommunikation mellan flera Ryzen AI Halo-noder (minst 2 portar) |
| Ethernet-kabel | 2 | Ansluter varje Halo-enhet till switchen (Cat 7 eller högre rekommenderas) |

> **Obs**: Två Ethernet-switchportar krävs för att ansluta de två Ryzen AI Halo-enheterna. En tredje port krävs om du ansluter till modellen från en separat klientmaskin istället för från en av Halo-enheterna.

### Programvara
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Installera:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) med arbetsbelastningen **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fysisk hårdvaruinstallation

> **Obs**: Slutför det här steget på både Maskin 1 och Maskin 2.

Anslut varje Ryzen AI Halo-enhet till Ethernet-switchen med en Cat 7-kabel (eller högre). Detta upprättar 10 Gbps-länken som används för höghastighets­kommunikation mellan noderna.
<!-- @os:linux -->
### 1. Identifiera nätverksgränssnitt

På varje maskin, hitta namnet på dess nätverksgränssnitt och notera det (det kommer att refereras till nedan som `IFNAME`). Kör:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Detta skriver ut gränssnittsnamnet direkt, till exempel:

```bash
enp191s0
```

### 2. Verifiera nätverkslänkhastigheter

Bekräfta att länken är aktiv och körs med full hastighet genom att kontrollera hastigheten på ditt gränssnitt:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Obs**: Ersätt `<IFNAME>` med det gränssnittsnamn som visades i [1. Identifiera nätverksgränssnitt](#1-determine-network-interfaces)

Du bör se en hastighet på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Obs**: Om hastigheten är lägre än `10000Mb/s` eller länken inte kommer upp, kontrollera kabelanslutningen och bekräfta att switchporten är inställd på 10 Gbps. Vissa switchar kräver att auto-negotiation inaktiveras och att länkhastigheten ställs in manuellt; se din switchs dokumentation.

<!-- @os:end -->

<!-- @os:windows -->
### Verifiera nätverkslänkhastighet

På varje maskin, kontrollera länkhastigheten för dina nätverksgränssnitt:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ditt Ethernet-gränssnitt bör vara `Up` och köras med `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Obs**: Om hastigheten är lägre än `10 Gbps` eller länken inte kommer upp, kontrollera kabelanslutningen och bekräfta att switchporten är inställd på 10 Gbps. Vissa switchar kräver att auto-negotiation inaktiveras och att länkhastigheten ställs in manuellt; se din switchs dokumentation.

<!-- @os:end -->

## Installation av llama.cpp

> **Obs**: Slutför det här steget på både Maskin 1 och Maskin 2.

Två installationsalternativ finns tillgängliga:

- [Alternativ 1: Lemonade SDK (Rekommenderas)](#option-1-lemonade-sdk-recommended) – förbyggda binärer, snabbast installation
- [Alternativ 2: Manuell källkodsbyggnad](#option-2-manual-source-build) – bygg från källkod med full kontroll över byggflaggor

### Alternativ 1: Lemonade SDK (Rekommenderas)

Lemonade SDK tillhandahåller nattliga byggen av llama.cpp med AMD ROCm 7-acceleration, riktade mot GPU:er som gfx1151 (Strix Halo / Ryzen AI Max+ 395) och andra nyliga Radeon-arkitekturer.

<!-- @os:windows -->
#### Steg 1: Ladda ned de förbyggda binärerna

Navigera till den senaste releasesidan och ladda ned arkivet som matchar din plattform och GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Ladda ned filen med namnet `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (där `xxxx` är byggnumret).

#### Steg 2: Extrahera binärerna

Packa upp det nedladdade arkivet:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Den här katalogen innehåller nu ROCm-aktiverade byggen av `llama-cli.exe`, `llama-server.exe` och `rpc-server.exe`, förkompilerade för ditt Ryzen AI Halo-system.

#### Steg 3: Verifiera GPU-detektering

```bash
.\llama-cli.exe --list-devices
```

Förväntad utdata:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Steg 1: Ladda ned de förbyggda binärerna

Navigera till den senaste releasesidan och ladda ned arkivet som matchar din plattform och GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Ladda ned filen med namnet `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (där `xxxx` är byggnumret).

#### Steg 2: Extrahera och förbered binärerna

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Den här katalogen innehåller nu ROCm-aktiverade byggen av `llama-cli`, `llama-server` och `rpc-server`, förkompilerade för ditt Ryzen AI Halo-system.

#### Steg 3: Verifiera GPU-detektering

```bash
./llama-cli --list-devices
```

Förväntad utdata:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Med llama.cpp förberett på varje nod, fortsätt till [Ladda ned modellen](#downloading-the-model).

### Alternativ 2: Manuell källkodsbyggnad

<!-- @os:windows -->
#### Steg 1: Bygg llama.cpp

Öppna **x64 Native Tools Command Prompt** (installerat med Visual Studio Build Tools) och klona repositoryt:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Lägg till HIP i din sökväg och bygg med ROCm- och RPC-stöd:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Byggflagga | Syfte |
|-----------|-------|
| `-DGGML_HIP=ON` | Aktiverar ROCm/HIP-programvarustacken |
| `-DGGML_RPC=ON` | Aktiverar RPC för distribuerad inferens |
| `-DGPU_TARGETS=gfx1151` | Riktar sig mot Ryzen AI Halo GPU (Radeon 8060s) |
| `-G Ninja` | Använder Ninja-byggsystemet |

#### Steg 2: Verifiera GPU-detektering

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Förväntad utdata:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Steg 3: Lägg till HIP i din användarsökväg

Byggsteget ovan ställde in `%HIP_PATH%\bin` enbart för den aktuella sessionen. För att göra HIP-biblioteken tillgängliga i valfri terminal (inte bara x64 Native Tools Command Prompt), lägg till det permanent i din användares `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Med llama.cpp förberett på varje nod, fortsätt till [Ladda ned modellen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Steg 1: Bygg llama.cpp

Klona repositoryt:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Bygg med ROCm- och RPC-stöd:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Byggflagga | Syfte |
|-----------|-------|
| `-DGGML_HIP=ON` | Aktiverar ROCm-programvarustacken |
| `-DGGML_RPC=ON` | Aktiverar RPC för distribuerad inferens |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Aktiverar rocWMMA för förbättrad Flash Attention på AMD GPU:er |
| `-DAMDGPU_TARGETS="gfx1151"` | Riktar sig mot Ryzen AI Halo GPU (Radeon 8060s) |

För fler bygginställningar, se [llama.cpp-byggdokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Steg 2: Verifiera GPU-detektering

```bash
cd rocm/bin
./llama-cli --list-devices
```

Förväntad utdata:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Med llama.cpp förberett på varje nod, fortsätt till [Ladda ned modellen](#downloading-the-model).
<!-- @os:end -->

## Ladda ned modellen

Den här spelboken använder [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), en modell med 358 miljarder parametrar i `Q4_K_XL`-kvantisering från [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Vid denna kvantisering kräver modellen ungefär 205 GB lagringsutrymme och ryms inom det kombinerade GPU-minnet hos två Ryzen AI Halo-noder.

Ladda ned GGUF-filerna med Hugging Face CLI:
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

> **Obs**: Modellnedladdningen måste slutföras på Maskin 1 (kontrollanten). RPC-workernoderna behöver ingen lokal kopia av modellfiler.

## Starta modellen på klustret

llama.cpp:s RPC-motor (Remote Procedure Call) gör det möjligt för en enda llama.cpp-instans att avlasta modellager till fjärrworkers över nätverket. En maskin fungerar som **kontrollant** (Maskin 1) och hanterar tokenisering, schemaläggning och orkestrering. Den andra maskinen kör en lättviktig **RPC-server** (Maskin 2) som exponerar sitt GPU-minne och sin beräkningskapacitet för kontrollanten.

Vid laddningstillfället delar llama.cpp upp modellen över båda noderna. När den väl är laddad fortlöper inferensen som om den kördes på en enda accelerator. RPC hanterar tensoröverföringar och synkronisering i bakgrunden.

### Steg 1: Starta RPC-servern (Maskin 2)

På Maskin 2, starta RPC-servern för att exponera dess GPU-resurser för kontrollanten:
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

| Flagga | Syfte |
|--------|-------|
| `-p` | Port att sända RPC-servern på |
| `-c` | Aktiverar en lokal cache för stora tensorer, vilket undviker upprepade nätverksöverföringar vid modelladdning |
| `--host` | IP-adress att binda RPC-servern till (`0.0.0.0` för alla gränssnitt) |

För fler alternativ, se [llama.cpp RPC-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Steg 2: Starta modellen (Maskin 1)

Med RPC-servern igång på Maskin 2, starta inferens från Maskin 1 med antingen `llama-cli` eller `llama-server`.

#### llama-cli

`llama-cli` tillhandahåller ett terminalbaserat gränssnitt för direkt interaktion med modellen. Det är idealiskt för benchmarking, felsökning och experimentering på låg nivå.

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

> **Hitta `<RPC_WORKER_IP>`**: På Maskin 2, kör `hostname -I | awk '{print $1}'` för att hitta dess lokala IP-adress.
<!-- @os:end -->

<!-- @os:windows -->
> **Obs**: Kör det här kommandot i Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Hitta `<RPC_WORKER_IP>`**: På Maskin 2, kör `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) för att hitta dess lokala IP-adress.

<!-- @os:end -->

När det körs visar `llama-cli` modelladdningens förlopp och öppnar en interaktiv prompt där du kan chatta direkt med modellen:

![llama-cli kör GLM 4.7 över två noder](assets/llama-cli-example.png)

#### llama-server

`llama-server` exponerar samma inferensmotor via en beständig serverprocess med ett integrerat webb-UI och ett OpenAI-kompatibelt HTTP-API. Detta är det föredragna gränssnittet för längre driftsättningar, åtkomst för flera användare och integration med externa verktyg.

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

> **Hitta `<RPC_WORKER_IP>`**: På Maskin 2, kör `hostname -I | awk '{print $1}'` för att hitta dess lokala IP-adress.
<!-- @os:end -->

<!-- @os:windows -->
> **Obs**: Kör det här kommandot i Terminal (Powershell).

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

> **Hitta `<RPC_WORKER_IP>`**: På Maskin 2, kör `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) för att hitta dess lokala IP-adress.
<!-- @os:end -->

När det startats, öppna `http://<HOST_IP>:8081` i din webbläsare för att komma åt det inbyggda webb-UI:t. Detta tillhandahåller ett webbläsarbaserat chattgränssnitt för interaktion med modellen:

![llama-server webb-UI kör GLM 4.7 över två noder](assets/llama-server-example.png)

<!-- @os:linux -->
> **Hitta `<HOST_IP>`**: På Maskin 1, kör `hostname -I | awk '{print $1}'` för att hitta dess lokala IP-adress.
<!-- @os:end -->

<!-- @os:windows -->
> **Hitta `<HOST_IP>`**: På Maskin 1, kör `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) för att hitta dess lokala IP-adress.
<!-- @os:end -->

#### Parameterreferens

| Flagga | Syfte |
|--------|-------|
| `-m` | Sökväg till GGUF-modellfilen (använd den första skärvan, `00001-of-00005`) |
| `-c` | Kontextstorlek i tokens. Större värden använder mer minne |
| `-fa on` | Aktiverar rocWMMA Flash Attention för förbättrad prestanda på AMD GPU:er |
| `-ngl 999` | Avlastar alla modellager till GPU:n |
| `--no-mmap` | Inaktiverar minnesmappning, vilket minskar laddningstider när modellstorleken överstiger systemets RAM men ryms i VRAM |
| `--host` | IP att binda `llama-server` till (endast `llama-server`) |
| `--port` | Port att servera HTTP-API:et på (endast `llama-server`) |
| `--rpc` | Kommaseparerad lista över RPC-worker-slutpunkter (`IP:port`) |

För fullständig parameteranvändning, se [llama-cli-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) och [llama-server-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Nästa steg

- **Anslut tredjepartsapplikationer**: `llama-server` exponerar ett OpenAI-kompatibelt API. Peka valfri OpenAI-kompatibel applikation (som Open WebUI) mot `http://<HOST_IP>:8081` med valfri platshållar-API-nyckel (t.ex. `none`) för att ansluta till ditt kluster
- **Utforska andra modeller**: Bläddra bland kvantiserade GGUF:er på [Hugging Face](https://huggingface.co/models?search=gguf) för att hitta modeller som ryms inom klustrets kombinerade GPU-minne
- **Skala till fyra noder**: Lägg till ytterligare två Ryzen AI Halo-system som extra RPC-workers för att få tillgång till modeller i biljonparameterskalan. Skicka ytterligare slutpunkter till `--rpc` som en kommaseparerad lista (t.ex. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)