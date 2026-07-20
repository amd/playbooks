<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Denna spelbok använder speciella taggar som GitHub inte kan rendera. Besök [amd.com/playbooks](https://amd.com/playbooks) för att förhandsgranska innehållet korrekt.
<!-- @github-only:end -->

# Klustring av två Ryzen™ AI Halo med RPC

## Översikt

Din Ryzen™ AI Halo kan redan köra stora språkmodeller lokalt. Klustring tar detta ett steg längre genom att kombinera GPU-minnet från flera system över ett lokalt nätverk, vilket ger dig tillgång till ännu större modeller med starkare resonemang, bättre kodgenerering och djupare flerspråkig förståelse, allt helt på din egen hårdvara.

Denna spelbok lär dig hur du klustrar två Ryzen AI Halo-system med hjälp av llama.cpp:s RPC-motor och kör GLM 4.7, en modell med 358 miljarder parametrar, på båda maskinerna med AMD ROCm™-acceleration.

## Vad du kommer att lära dig

- Hur man utökar VRAM-tilldelningen på Ryzen AI Halo-system
- Installera llama.cpp med ROCm- och RPC-stöd
- Konfigurera en RPC-worker och starta distribuerad inferens över två noder
- Köra en modell med 358 miljarder parametrar över två nätverksanslutna Ryzen AI Halo-system

## Ställa in minneskonfigurationen

> **Obs**: Slutför detta steg på både Machine 1 och Machine 2.

<!-- @os:windows -->
På Windows, för att köra större modeller som kräver mer minne, behöver vi använda tilldelningen av AMD Variable Graphics Memory (iGPU VRAM).

Detta görs genom att öppna kontrollpanelen AMD Software: Adrenalin Edition och navigera till: `Performance > Tuning > AMD Variable Graphics Memory`. Ställ in värdet till **96 GB**. Starta om systemet för att ändringarna ska träda i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
På Linux använder ROCm en delad systemminnespool, och denna pool är som standard konfigurerad till hälften av systemminnet.

Denna mängd kan ökas genom att ändra kärnans Translation Table Manager (TTM)-sidinställning, enligt följande instruktioner. AMD rekommenderar att ställa in minsta dedikerade VRAM i BIOS (0.5 GB).

* Installera verktyget pipx och lägg till sökvägen för pipx-installerade wheels i systemets sökväg.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installera amd-debug-tools-wheelen från PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kör verktyget amd-ttm för att fråga efter aktuella inställningar för delat minne.
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
## Kontrollera om det finns programvaruuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->
## Förutsättningar

### Hårdvara

Denna spelbok kräver två Ryzen AI Halo-enheter och en Ethernet-switch, anslutna i en stjärntopologi där varje enhet är direktansluten till switchen.

| Komponent | Antal | Beskrivning |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Beräkningsnoder som utgör klustret |
| Ethernet-switch på 10 Gbps | 1 | Central switch som möjliggör kommunikation mellan flera Ryzen AI Halo-noder (minst 2 portar) |
| Ethernet-kabel | 2 | Ansluter varje Halo-enhet till switchen (Cat 7 eller högre rekommenderas) |

> **Obs**: Två portar på Ethernet-switchen krävs för att ansluta de två Ryzen AI Halo-enheterna. En tredje port krävs om du kommer åt modellen från en separat klientmaskin istället för från en av Halo-enheterna.

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

> **Obs**: Slutför detta steg på både Machine 1 och Machine 2.

Anslut varje Ryzen AI Halo-enhet till Ethernet-switchen med en Cat 7-kabel (eller högre). Detta upprättar den 10Gbps-länk som används för höghastighetskommunikation mellan noderna.
<!-- @os:linux -->
### 1. Fastställ nätverksgränssnitt

På varje maskin, hitta namnet på dess nätverksgränssnitt och notera det (det kommer nedan att kallas `IFNAME`). Kör:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Detta skriver ut gränssnittsnamnet direkt, till exempel:

```bash
enp191s0
```

### 2. Verifiera nätverkslänkarnas hastigheter

Bekräfta att länken är aktiv och körs med full hastighet genom att kontrollera hastigheten för ditt gränssnitt:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Obs**: Ersätt `<IFNAME>` med utdatans gränssnittsnamn från [1. Fastställ nätverksgränssnitt](#1-determine-network-interfaces)

Du bör se en hastighet på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Obs**: Om hastigheten är lägre än `10000Mb/s` eller om länken inte kommer upp, kontrollera kabelanslutningen och bekräfta att switchporten är inställd på 10Gbps. Vissa switchar kräver att auto-förhandling inaktiveras och att länkhastigheten ställs in manuellt; se din switchs dokumentation.

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

> **Obs**: Om hastigheten är lägre än `10 Gbps` eller om länken inte kommer upp, kontrollera kabelanslutningen och bekräfta att switchporten är inställd på 10Gbps. Vissa switchar kräver att auto-förhandling inaktiveras och att länkhastigheten ställs in manuellt; se din switchs dokumentation.

<!-- @os:end -->

## Installera llama.cpp

> **Obs**: Slutför detta steg på både Machine 1 och Machine 2.

Två installationsalternativ finns tillgängliga:

- [Alternativ 1: Lemonade SDK (Rekommenderas)](#option-1-lemonade-sdk-recommended) - färdigbyggda binärfiler, snabbast installation
- [Alternativ 2: Manuellt källkodsbygge](#option-2-manual-source-build) - bygg från källkod med full kontroll över byggflaggor

### Alternativ 1: Lemonade SDK (Rekommenderas)

Lemonade SDK tillhandahåller nattliga byggen av llama.cpp med AMD ROCm 7-acceleration, riktade mot GPU:er som gfx1151 (Strix Halo / Ryzen AI Max+ 395) och andra senare Radeon-arkitekturer.

<!-- @os:windows -->
#### Steg 1: Ladda ner de förbyggda binärfilerna

Navigera till den senaste versionssidan och ladda ner arkivet som matchar din plattform och GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Ladda ner filen med namnet `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (där `xxxx` är byggnumret).

#### Steg 2: Packa upp binärfilerna

Packa upp det nedladdade arkivet:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Den här katalogen innehåller nu ROCm-aktiverade byggen av `llama-cli.exe`, `llama-server.exe` och `rpc-server.exe`, förkompilerade för ditt Ryzen AI Halo-system.

#### Steg 3: Verifiera GPU-identifiering

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
#### Steg 1: Ladda ner de förbyggda binärfilerna

Navigera till den senaste versionssidan och ladda ner arkivet som matchar din plattform och GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Ladda ner filen med namnet `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (där `xxxx` är byggnumret).

#### Steg 2: Packa upp och förbered binärfilerna

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Den här katalogen innehåller nu ROCm-aktiverade byggen av `llama-cli`, `llama-server` och `rpc-server`, förkompilerade för ditt Ryzen AI Halo-system.

#### Steg 3: Verifiera GPU-identifiering

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
När llama.cpp är förberett på varje nod fortsätter du till [Ladda ner modellen](#downloading-the-model).

### Alternativ 2: Manuellt källkodsbygge

<!-- @os:windows -->
#### Steg 1: Bygg llama.cpp

Öppna **x64 Native Tools Command Prompt** (installeras med Visual Studio Build Tools) och klona lagringsplatsen:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Lägg till HIP i din sökväg och bygg med stöd för ROCm och RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Byggflagga | Syfte |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiverar ROCm/HIP-programvarustacken |
| `-DGGML_RPC=ON` | Aktiverar RPC för distribuerad inferens |
| `-DGPU_TARGETS=gfx1151` | Riktar in sig på Ryzen AI Halo-GPU:n (Radeon 8060s) |
| `-G Ninja` | Använder byggsystemet Ninja |

#### Steg 2: Verifiera GPU-identifiering

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

Byggsteget ovan angav `%HIP_PATH%\bin` endast för den aktuella sessionen. För att göra HIP-biblioteken tillgängliga i alla terminaler (inte bara i x64 Native Tools Command Prompt), lägg till den permanent i din användar-`PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

När llama.cpp är förberett på varje nod fortsätter du till [Ladda ner modellen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Steg 1: Bygg llama.cpp

Klona lagringsplatsen:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Bygg med stöd för ROCm och RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Byggflagga | Syfte |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiverar ROCm-programvarustacken |
| `-DGGML_RPC=ON` | Aktiverar RPC för distribuerad inferens |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Aktiverar rocWMMA för förbättrad Flash Attention på AMD-GPU:er |
| `-DAMDGPU_TARGETS="gfx1151"` | Riktar in sig på Ryzen AI Halo-GPU:n (Radeon 8060s) |

För fler byggalternativ, se [dokumentationen för llama.cpp-bygge](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Steg 2: Verifiera GPU-identifiering

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

När llama.cpp är förberett på varje nod fortsätter du till [Ladda ner modellen](#downloading-the-model).
<!-- @os:end -->

## Ladda ner modellen

Den här handboken använder [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), en modell med 358 miljarder parametrar i kvantiseringen `Q4_K_XL` från [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Vid denna kvantisering kräver modellen cirka 205 GB lagringsutrymme och ryms inom det kombinerade GPU-minnet på två Ryzen AI Halo-noder.

Ladda ner GGUF-filerna med hjälp av Hugging Face CLI:
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

> **Obs!**: Modellnedladdningen måste slutföras på maskin 1 (styrenheten). RPC-arbetsnoderna behöver inte en lokal kopia av modellfilerna.

## Starta modellen i klustret

RPC-motorn (Remote Procedure Call) i llama.cpp gör det möjligt för en enda llama.cpp-instans att avlasta modellager till fjärrarbetare via nätverket. En maskin agerar som **styrenhet** (maskin 1) och hanterar tokenisering, schemaläggning och orkestrering. Den andra maskinen kör en lättviktig **RPC-server** (maskin 2) som exponerar sitt GPU-minne och sin beräkningskraft för styrenheten.

Vid inläsningstillfället delar llama.cpp upp modellen mellan båda noderna. När den väl är inläst fortlöper inferensen som om den kördes på en enda accelerator. RPC hanterar tensoröverföringar och synkronisering i bakgrunden.

### Steg 1: Starta RPC-servern (maskin 2)

På maskin 2 startar du RPC-servern för att exponera dess GPU-resurser för styrenheten:
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
|------|---------|
| `-p` | Port att sända RPC-servern på |
| `-c` | Aktiverar en lokal cache för stora tensorer, vilket undviker upprepade nätverksöverföringar vid modellinläsning |
| `--host` | IP-adress att binda RPC-servern till (`0.0.0.0` för alla gränssnitt) |

För fler alternativ, se [RPC-dokumentationen för llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Steg 2: Starta modellen (maskin 1)

Med RPC-servern igång på maskin 2 startar du inferens från maskin 1 med antingen `llama-cli` eller `llama-server`.

#### llama-cli

`llama-cli` erbjuder ett terminalbaserat gränssnitt för att interagera direkt med modellen. Det är idealiskt för prestandamätning, felsökning och experiment på låg nivå.

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

> **Hitta `<RPC_WORKER_IP>`**: På maskin 2 kör du `hostname -I | awk '{print $1}'` för att hitta dess lokala IP-adress.
<!-- @os:end -->

<!-- @os:windows -->
> **Obs!**: Kör detta kommando i Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Hitta `<RPC_WORKER_IP>`**: På maskin 2 kör du `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) för att hitta dess lokala IP-adress.

<!-- @os:end -->

När den väl körs visar `llama-cli` modellens inläsningsförlopp och går in i en interaktiv prompt där du kan chatta direkt med modellen:

![llama-cli som kör GLM 4.7 över två noder](assets/llama-cli-example.png)
#### llama-server

`llama-server` exponerar samma inferensmotor genom en beständig serverprocess med ett integrerat webbgränssnitt och ett OpenAI-kompatibelt HTTP-API. Det här är det föredragna gränssnittet för mer långvariga driftsättningar, åtkomst för flera användare och integration med externa verktyg.

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

> **Hitta `<RPC_WORKER_IP>`**: På maskin 2 kör du `hostname -I | awk '{print $1}'` för att hitta dess lokala IP-adress.
<!-- @os:end -->

<!-- @os:windows -->
> **Obs!**: Kör det här kommandot i Terminal (Powershell).

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

> **Hitta `<RPC_WORKER_IP>`**: På maskin 2 kör du `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) för att hitta dess lokala IP-adress.
<!-- @os:end -->

När servern har startats öppnar du `http://<HOST_IP>:8081` i webbläsaren för att komma åt det inbyggda webbgränssnittet. Det ger ett webbläsarbaserat chattgränssnitt för att interagera med modellen:

![llama-server webbgränssnitt som kör GLM 4.7 över två noder](assets/llama-server-example.png)

<!-- @os:linux -->
> **Hitta `<HOST_IP>`**: På maskin 1 kör du `hostname -I | awk '{print $1}'` för att hitta dess lokala IP-adress.
<!-- @os:end -->

<!-- @os:windows -->
> **Hitta `<HOST_IP>`**: På maskin 1 kör du `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) för att hitta dess lokala IP-adress.
<!-- @os:end -->

#### Parameterreferens

| Flagga | Syfte |
|------|---------|
| `-m` | Sökväg till GGUF-modellfilen (använd det första fragmentet, `00001-of-00005`) |
| `-c` | Kontextstorlek i tokens. Större värden använder mer minne |
| `-fa on` | Aktiverar rocWMMA Flash Attention för förbättrad prestanda på AMD-GPU:er |
| `-ngl 999` | Avlastar alla modellager till GPU:n |
| `--no-mmap` | Inaktiverar minnesmappning, vilket minskar laddningstider när modellstorleken överstiger systemminnet men får plats i VRAM |
| `--host` | IP att binda `llama-server` till (endast `llama-server`) |
| `--port` | Port att köra HTTP-API:et på (endast `llama-server`) |
| `--rpc` | Kommaseparerad lista över RPC-arbetsendpunkter (`IP:port`) |

För fullständig parameteranvändning, se [llama-cli-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) och [llama-server-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Nästa steg

- **Anslut tredjepartsapplikationer**: `llama-server` exponerar ett OpenAI-kompatibelt API. Peka valfri OpenAI-kompatibel applikation (till exempel Open WebUI) mot `http://<HOST_IP>:8081` med en godtycklig platshållar-API-nyckel (t.ex. `none`) för att ansluta till klustret
- **Utforska andra modeller**: Bläddra bland kvantiserade GGUF-filer på [Hugging Face](https://huggingface.co/models?search=gguf) för att hitta modeller som ryms inom klustrets sammanlagda GPU-minne
- **Skala upp till fyra noder**: Lägg till ytterligare två Ryzen AI Halo-system som ytterligare RPC-arbetare för att få tillgång till modeller i storleksklassen 1 biljon parametrar. Ange ytterligare endpoints till `--rpc` som en kommaseparerad lista (t.ex. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)