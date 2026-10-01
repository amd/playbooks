<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Klustring av fyra Ryzen™ AI Halo-system med RPC

## Översikt

Din Ryzen™ AI Halo kan redan köra stora språkmodeller lokalt. Klustring tar detta ett steg längre genom att kombinera GPU-minnet från flera system över ett lokalt nätverk, vilket ger dig tillgång till ännu större modeller med starkare resonemangsförmåga, bättre kodgenerering och djupare flerspråkig förståelse – helt på din egen hårdvara.

Denna guide lär dig hur du klustrar fyra Ryzen AI Halo-system med hjälp av llama.cpp:s RPC-motor och kör Kimi K2.6, en stor mixture-of-experts-modell, på alla fyra maskinerna med AMD ROCm™-acceleration.

## Vad du kommer att lära dig

- Hur du utökar VRAM-tilldelningen på Ryzen AI Halo-system
- Installera llama.cpp med stöd för ROCm och RPC
- Konfigurera RPC-arbetare och starta distribuerad inferens över fyra noder
- Köra en modell med 1T parametrar över fyra sammankopplade Ryzen AI Halo-system

## Ställa in minneskonfigurationen

> **Obs**: Slutför detta steg på alla fyra maskinerna (Maskin 1 till Maskin 4).

<!-- @os:windows -->
På Windows behöver vi, för att kunna köra större modeller som kräver mer minne, använda tilldelningen av AMD Variable Graphics Memory (iGPU VRAM).

Detta kan göras genom att öppna kontrollpanelen AMD Software: Adrenalin Edition och navigera till: `Performance > Tuning > AMD Variable Graphics Memory`. Ställ in värdet till **96 GB**. Starta om systemet för att ändringarna ska börja gälla.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
På Linux använder ROCm en delad systemminnespool, och denna pool är som standard konfigurerad till hälften av systemminnet.

Denna mängd kan ökas genom att ändra kernelns Translation Table Manager (TTM)-sidinställning, enligt instruktionerna nedan. AMD rekommenderar att du ställer in det minsta dedikerade VRAM-värdet i BIOS (0.5 GB).

* Installera verktyget pipx och lägg till sökvägen för pipx-installerade wheels i systemets sökväg.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installera wheel-paketet amd-debug-tools från PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kör verktyget amd-ttm för att fråga efter de aktuella inställningarna för delat minne.
  ```bash
  amd-ttm
  ```

* Konfigurera om inställningarna för delat minne till **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Starta om systemet för att ändringarna ska börja gälla.


<!-- @os:end -->
<!-- @device:halo_box -->
## Kontrollera efter programvaruuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->
## Förutsättningar

### Hårdvara

Denna guide kräver fyra Ryzen AI Halo-enheter och en Ethernet-switch, anslutna i en stjärntopologi där varje enhet är direktansluten till switchen.

| Komponent | Antal | Beskrivning |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Beräkningsnoder som utgör klustret |
| 10 Gbps Ethernet-switch | 1 | Central switch som möjliggör kommunikation mellan flera Ryzen AI Halo-noder (minst 4 portar) |
| Ethernet-kabel | 4 | Ansluter varje Halo-enhet till switchen (Cat 7 eller högre rekommenderas) |

> **Obs**: Fyra portar på Ethernet-switchen krävs för att ansluta de fyra Ryzen AI Halo-enheterna. En femte port krävs om du vill komma åt modellen från en separat klientmaskin istället för från en av Halo-enheterna.

### Programvara
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Installera:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) med arbetsbelastningen **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fysisk maskinvaruinstallation

> **Obs**: Slutför detta steg på alla fyra maskinerna (Maskin 1 till Maskin 4).

Anslut varje Ryzen AI Halo-enhet till Ethernet-switchen med en Cat 7-kabel (eller högre). Detta upprättar den 10 Gbps-länk som används för höghastighetskommunikation mellan noderna.
<!-- @os:linux -->
### 1. Fastställ nätverksgränssnitt

På varje maskin, ta reda på namnet på dess nätverksgränssnitt och notera det (det kommer nedan att kallas `IFNAME`). Kör:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Detta skriver ut gränssnittsnamnet direkt, till exempel:

```bash
enp191s0
```

### 2. Verifiera nätverkslänkens hastighet

Bekräfta att länken är aktiv och kör med full hastighet genom att kontrollera hastigheten på ditt gränssnitt:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Obs**: Ersätt `<IFNAME>` med gränssnittsnamnet från utdata i [1. Fastställ nätverksgränssnitt](#1-determine-network-interfaces)

Du bör se en hastighet på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Obs**: Om hastigheten är lägre än `10000Mb/s` eller länken inte kommer upp, kontrollera kabelanslutningen och bekräfta att switchporten är inställd på 10 Gbps. Vissa switchar kräver att auto-förhandling inaktiveras och att länkhastigheten ställs in manuellt; se dokumentationen för din switch.

<!-- @os:end -->

<!-- @os:windows -->
### Verifiera nätverkslänkens hastighet

Kontrollera på varje maskin hastigheten för dina nätverksgränssnitt:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ditt Ethernet-gränssnitt bör vara `Up` och köra med `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Obs**: Om hastigheten är lägre än `10 Gbps` eller länken inte kommer upp, kontrollera kabelanslutningen och bekräfta att switchporten är inställd på 10 Gbps. Vissa switchar kräver att auto-förhandling inaktiveras och att länkhastigheten ställs in manuellt; se dokumentationen för din switch.

<!-- @os:end -->

## Installera llama.cpp

> **Obs**: Slutför detta steg på alla fyra maskinerna (Maskin 1 till Maskin 4).

Två installationsalternativ finns tillgängliga:

- [Alternativ 1: Lemonade SDK (rekommenderas)](#option-1-lemonade-sdk-recommended) - färdigbyggda binärfiler, snabbaste installationen
- [Alternativ 2: Manuell källkodsbyggnad](#option-2-manual-source-build) - bygg från källkod med full kontroll över byggflaggor

### Alternativ 1: Lemonade SDK (rekommenderas)

Lemonade SDK tillhandahåller nattliga byggen av llama.cpp med AMD ROCm 7-acceleration, riktade mot GPU:er som gfx1151 (Strix Halo / Ryzen AI Max+ 395) och andra nyare Radeon-arkitekturer.

<!-- @os:windows -->
#### Steg 1: Ladda ner de förkompilerade binärfilerna

Navigera till sidan för den senaste versionen och ladda ner arkivet som matchar din plattform och GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Ladda ner filen med namnet `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (där `xxxx` är byggnumret).

#### Steg 2: Packa upp binärfilerna

Packa upp det nedladdade arkivet:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Den här katalogen innehåller nu ROCm-aktiverade byggen av `llama-cli.exe`, `llama-server.exe` och `ggml-rpc-server.exe`, förkompilerade för ditt Ryzen AI Halo-system.

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
#### Steg 1: Ladda ner de förkompilerade binärfilerna

Navigera till sidan för den senaste versionen och ladda ner arkivet som matchar din plattform och GPU-mål:

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

Öppna **x64 Native Tools Command Prompt** (installerad med Visual Studio Build Tools) och klona repositoriet:

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
| `-DGGML_HIP=ON` | Aktiverar ROCm/HIP-mjukvarustacken |
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

Byggsteget ovan angav `%HIP_PATH%\bin` endast för den aktuella sessionen. För att göra HIP-biblioteken tillgängliga i vilken terminal som helst (inte bara i x64 Native Tools Command Prompt) lägger du till det permanent i din användares `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

När llama.cpp är förberett på varje nod fortsätter du till [Ladda ner modellen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Steg 1: Bygg llama.cpp

Klona repositoriet:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Bygg med stöd för ROCm och RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Byggflagga | Syfte |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiverar ROCm-mjukvarustacken |
| `-DGGML_RPC=ON` | Aktiverar RPC för distribuerad inferens |
| `-DAMDGPU_TARGETS="gfx1151"` | Riktar in sig på Ryzen AI Halo-GPU:n (Radeon 8060s) |

För fler byggalternativ, se [byggdokumentationen för llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Den här spelboken använder [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) i kvantiseringen `UD-Q2_K_XL` från [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Denna kvantisering ryms inom det kombinerade GPU-minnet på fyra Ryzen AI Halo-noder.

Ladda ner GGUF-filerna med Hugging Face CLI:
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

> **Obs**: Nedladdningen av modellen måste slutföras på Maskin 1 (kontrollern). RPC-arbetsnoderna (Maskin 2, 3 och 4) behöver ingen lokal kopia av modellfilerna.

## Starta modellen på klustret

RPC-motorn (Remote Procedure Call) i llama.cpp gör det möjligt för en enda llama.cpp-instans att avlasta modellager till fjärrarbetare över nätverket. En maskin fungerar som **kontroller** (Maskin 1) och hanterar tokenisering, schemaläggning och orkestrering. De andra tre maskinerna kör var och en en lättviktig **RPC-server** (Maskin 2, 3 och 4) som exponerar sitt GPU-minne och sin beräkningskraft för kontrollern.

Vid inläsningstillfället delar llama.cpp upp modellen i skärvor över alla fyra noderna. När modellen väl är inläst fortskrider inferensen som om den kördes på en enda accelerator. RPC hanterar tensoröverföringar och synkronisering i bakgrunden.

### Steg 1: Starta RPC-servrarna (Maskin 2, 3 och 4)

På var och en av Maskin 2, 3 och 4, starta RPC-servern för att exponera dess GPU-resurser för kontrollern:
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

| Flagga | Syfte |
|------|---------|
| `-p` | Port att sända ut RPC-servern på |
| `-c` | Aktiverar en lokal cache för stora tensorer, vilket undviker upprepade nätverksöverföringar under modellinläsningen |
| `--host` | IP-adress att binda RPC-servern till (`0.0.0.0` för alla gränssnitt) |

För fler alternativ, se [RPC-dokumentationen för llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Steg 2: Starta modellen (Maskin 1)

Med RPC-servrarna igång på Maskin 2, 3 och 4, starta inferens från Maskin 1 med antingen `llama-cli` eller `llama-server`.
#### llama-cli

`llama-cli` erbjuder ett terminalbaserat gränssnitt för att interagera direkt med modellen. Det är idealiskt för prestandamätning, felsökning och experiment på låg nivå.

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

> **Hitta `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Kör `hostname -I | awk '{print $1}'` på var och en av Maskin 2, 3 och 4 för att hitta dess lokala IP-adress.
<!-- @os:end -->

<!-- @os:windows -->
> **Obs!**: Kör detta kommando i Terminal (Powershell).

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

> **Hitta `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Kör `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) på var och en av Maskin 2, 3 och 4 för att hitta dess lokala IP-adress.

<!-- @os:end -->

När den väl körs visar `llama-cli` modellens laddningsförlopp och öppnar en interaktiv prompt där du kan chatta direkt med modellen:

![llama-cli körs med Kimi K2.6 över fyra noder](assets/llama-cli-example.png)

#### llama-server

`llama-server` exponerar samma inferensmotor genom en beständig serverprocess med ett integrerat webbgränssnitt och ett OpenAI-kompatibelt HTTP-API. Detta är det föredragna gränssnittet för längre driftperioder, åtkomst för flera användare och integration med externa verktyg.

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

> **Hitta `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Kör `hostname -I | awk '{print $1}'` på var och en av Maskin 2, 3 och 4 för att hitta dess lokala IP-adress.
<!-- @os:end -->

<!-- @os:windows -->
> **Obs!**: Kör detta kommando i Terminal (Powershell).

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

> **Hitta `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Kör `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) på var och en av Maskin 2, 3 och 4 för att hitta dess lokala IP-adress.
<!-- @os:end -->

När den har startats, öppna `http://<HOST_IP>:8081` i din webbläsare för att komma åt det inbyggda webbgränssnittet. Detta ger ett webbläsarbaserat chattgränssnitt för att interagera med modellen:

![llama-server-webbgränssnitt körs med Kimi K2.6 över fyra noder](assets/llama-server-example.png)

<!-- @os:linux -->
> **Hitta `<HOST_IP>`**: Kör `hostname -I | awk '{print $1}'` på Maskin 1 för att hitta dess lokala IP-adress.
<!-- @os:end -->

<!-- @os:windows -->
> **Hitta `<HOST_IP>`**: Kör `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) på Maskin 1 för att hitta dess lokala IP-adress.
<!-- @os:end -->

#### Parameterreferens

| Flagga | Syfte |
|------|---------|
| `-m` | Sökväg till GGUF-modellfilen (använd det första fragmentet, `00001-of-00008`) |
| `-c` | Kontextstorlek i token. Större värden använder mer minne |
| `-fa on` | Aktiverar rocWMMA Flash Attention för förbättrad prestanda på AMD-GPU:er |
| `-ngl 999` | Avlastar alla modellager till GPU:n |
| `-lm none` | Ställer in modellens laddningsläge på `none`, vilket inaktiverar minnesmappning för att minska laddningstider när modellstorleken överstiger systemets RAM men ryms i VRAM |
| `-b` | Logisk batchstorlek i token. Att sätta detta till 4096 balanserar genomströmning och minnesanvändning mellan noder |
| `-ub` | Fysisk (mikro) batchstorlek för promptbearbetning. Att matcha `-b` undviker onödig overhead från uppdelning |
| `--host` | IP att binda `llama-server` till (endast `llama-server`) |
| `--port` | Port att servera HTTP-API:et på (endast `llama-server`) |
| `--rpc` | Kommaseparerad lista med RPC-arbetsslutpunkter (`IP:port`) |

För fullständig parameteranvändning, se [llama-cli-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) och [llama-server-dokumentationen](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Nästa steg

- **Anslut tredjepartsapplikationer**: `llama-server` exponerar ett OpenAI-kompatibelt API. Peka valfri OpenAI-kompatibel applikation (till exempel Open WebUI) mot `http://<HOST_IP>:8081` med en godtycklig platshållar-API-nyckel (t.ex. `none`) för att ansluta till ditt kluster
- **Utforska andra modeller**: Bläddra bland kvantiserade GGUF:er på [Hugging Face](https://huggingface.co/models?search=gguf) för att hitta modeller som ryms inom klustrets samlade GPU-minne
- **Skala bortom fyra noder**: Lägg till fler Ryzen AI Halo-system som ytterligare RPC-arbetare för att nå modeller bortom skalan 1 biljon parametrar. Skicka ytterligare slutpunkter till `--rpc` som en kommaseparerad lista (t.ex. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)