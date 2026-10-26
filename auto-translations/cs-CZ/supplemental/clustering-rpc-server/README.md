<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering dvou systémů Ryzen™ AI Halo pomocí RPC

## Přehled

Váš systém Ryzen™ AI Halo již dokáže spouštět velké jazykové modely lokálně. Clustering jde ještě dál – kombinuje paměť GPU více systémů v rámci lokální sítě, čímž vám poskytuje přístup k ještě větším modelům se silnějším uvažováním, lepší generací kódu a hlubším porozuměním více jazykům, a to vše zcela na vašem vlastním hardwaru.

Tento návod vás naučí, jak vytvořit cluster ze dvou systémů Ryzen AI Halo pomocí RPC enginu z llama.cpp a spustit model GLM 4.7 s 358 miliardami parametrů na obou strojích s akcelerací AMD ROCm™.

## Co se naučíte

- Jak rozšířit alokaci VRAM na systémech Ryzen AI Halo
- Instalaci llama.cpp s podporou ROCm a RPC
- Konfiguraci RPC workeru a spuštění distribuovaného inferování napříč dvěma uzly
- Spuštění modelu se 358 miliardami parametrů na dvou propojených systémech Ryzen AI Halo v síti

## Nastavení konfigurace paměti

> **Poznámka**: Tento krok proveďte na stroji 1 i na stroji 2.

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Spouštění modelů s velikostí blízkou nebo přesahující 128 GB:** Na systémech AMD Ryzen™ AI Max 400 Series (Gorgon Halo) se systémem Windows vyžadují modely, které se blíží nebo přesahují 128 GB paměti, další konfiguraci, aby běžely bez chyb. Před načtením modelu postupujte podle pokynů v dokumentu [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines).
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Ve Windows je pro spouštění větších modelů, které vyžadují více paměti, potřeba použít alokaci AMD Variable Graphics Memory (iGPU VRAM).

To lze provést otevřením ovládacího panelu AMD Software: Adrenalin Edition a přechodem na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavte hodnotu na **96 GB**. Aby se změny projevily, restartujte systém.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Na Linuxu využívá ROCm sdílený fond systémové paměti, který je ve výchozím nastavení konfigurován na polovinu systémové paměti.

Toto množství lze zvýšit změnou nastavení stránek Translation Table Manager (TTM) jádra, a to podle následujících pokynů. AMD doporučuje nastavit v BIOSu minimální vyhrazenou VRAM (0,5 GB).

* Nainstalujte nástroj pipx a přidejte cestu k instalovaným wheel balíčkům pipx do vyhledávací cesty systému.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainstalujte wheel balíček amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spusťte nástroj amd-ttm pro zjištění aktuálního nastavení sdílené paměti.
  ```bash
  amd-ttm
  ```

* Nastavte sdílenou paměť na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte systém, aby se změny projevily.


<!-- @os:end -->
<!-- @device:halo_box -->
## Zkontrolujte aktualizace softwaru

<!-- @require:software-update -->
<!-- @device:end -->
## Požadavky

### Hardware

Tento návod vyžaduje dvě jednotky Ryzen AI Halo a jeden ethernetový přepínač, zapojené v topologii hvězdy, přičemž každá jednotka je připojena přímo k přepínači.

| Komponenta | Počet | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočetní uzly tvořící cluster |
| 10Gbps ethernetový přepínač | 1 | Centrální přepínač umožňující komunikaci mezi více uzly Ryzen AI Halo (minimálně 2 porty) |
| Ethernetový kabel | 2 | Propojuje každou jednotku Halo s přepínačem (doporučena kategorie Cat 7 nebo vyšší) |

> **Poznámka**: K propojení dvou jednotek Ryzen AI Halo jsou potřeba dva porty ethernetového přepínače. Třetí port je potřeba, pokud k modelu přistupujete ze samostatného klientského počítače místo z jedné z jednotek Halo.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Nainstalujte prosím:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) s pracovní zátěží **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyzické zapojení hardwaru

> **Poznámka**: Tento krok proveďte na stroji 1 i na stroji 2.

Připojte každou jednotku Ryzen AI Halo k ethernetovému přepínači pomocí kabelu Cat 7 (nebo vyššího). Tím se vytvoří 10Gbps spojení používané pro vysokorychlostní komunikaci mezi uzly.
<!-- @os:linux -->
### 1. Zjištění síťových rozhraní

Na každém stroji zjistěte název jeho síťového rozhraní a poznamenejte si jej (dále bude uváděn jako `IFNAME`). Spusťte:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tím se vypíše přímo název rozhraní, například:

```bash
enp191s0
```

### 2. Ověření rychlosti síťového spojení

Potvrďte, že spojení je aktivní a běží na plné rychlosti, kontrolou rychlosti vašeho rozhraní:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` názvem výstupního rozhraní z kroku [1. Zjištění síťových rozhraní](#1-determine-network-interfaces)

Měli byste vidět rychlost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Pokud je rychlost nižší než `10000Mb/s` nebo se spojení nenaváže, zkontrolujte kabelové připojení a potvrďte, že je port přepínače nastaven na 10Gbps. Některé přepínače vyžadují zakázání automatické negociace a ruční nastavení rychlosti spojení; postupujte podle dokumentace k vašemu přepínači.

<!-- @os:end -->

<!-- @os:windows -->
### Ověření rychlosti síťového spojení

Na každém stroji zkontrolujte rychlost spojení vašich síťových rozhraní:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaše ethernetové rozhraní by mělo být `Up` a běžet rychlostí `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Poznámka**: Pokud je rychlost nižší než `10 Gbps` nebo se spojení nenaváže, zkontrolujte kabelové připojení a potvrďte, že je port přepínače nastaven na 10Gbps. Některé přepínače vyžadují zakázání automatické negociace a ruční nastavení rychlosti spojení; postupujte podle dokumentace k vašemu přepínači.

<!-- @os:end -->

## Instalace llama.cpp

> **Poznámka**: Tento krok proveďte na stroji 1 i na stroji 2.

K dispozici jsou dvě možnosti instalace:

- [Možnost 1: Lemonade SDK (doporučeno)](#option-1-lemonade-sdk-recommended) – předpřipravené binární soubory, nejrychlejší nastavení
- [Možnost 2: Ruční sestavení ze zdrojového kódu](#option-2-manual-source-build) – sestavení ze zdrojového kódu s plnou kontrolou nad parametry sestavení
### Varianta 1: Lemonade SDK (doporučeno)

Lemonade SDK poskytuje noční sestavení llama.cpp s akcelerací AMD ROCm 7, zaměřené na GPU jako gfx1151 (Strix Halo / Ryzen AI Max+ 395) a další novější architektury Radeon.

<!-- @os:windows -->
#### Krok 1: Stažení předkompilovaných binárních souborů

Přejděte na stránku s nejnovějším vydáním a stáhněte archiv odpovídající vaší platformě a cílovému GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stáhněte soubor s názvem `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo sestavení).

#### Krok 2: Rozbalení binárních souborů

Rozbalte stažený archiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tento adresář nyní obsahuje sestavení `llama-cli.exe`, `llama-server.exe` a `rpc-server.exe` s podporou ROCm, předkompilovaná pro váš systém Ryzen AI Halo.

#### Krok 3: Ověření detekce GPU

```bash
.\llama-cli.exe --list-devices
```

Očekávaný výstup:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Krok 1: Stažení předkompilovaných binárních souborů

Přejděte na stránku s nejnovějším vydáním a stáhněte archiv odpovídající vaší platformě a cílovému GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stáhněte soubor s názvem `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo sestavení).

#### Krok 2: Rozbalení a příprava binárních souborů

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Tento adresář nyní obsahuje sestavení `llama-cli`, `llama-server` a `rpc-server` s podporou ROCm, předkompilovaná pro váš systém Ryzen AI Halo.

#### Krok 3: Ověření detekce GPU

```bash
./llama-cli --list-devices
```

Očekávaný výstup:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Po přípravě llama.cpp na každém uzlu pokračujte na [Stahování modelu](#downloading-the-model).

### Varianta 2: Ruční sestavení ze zdrojového kódu

<!-- @os:windows -->
#### Krok 1: Sestavení llama.cpp

Otevřete **x64 Native Tools Command Prompt** (nainstalovaný spolu s Visual Studio Build Tools) a naklonujte repozitář:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Přidejte HIP do své cesty a sestavte s podporou ROCm a RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Příznak sestavení | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povolí softwarový stack ROCm/HIP |
| `-DGGML_RPC=ON` | Povolí RPC pro distribuovanou inferenci |
| `-DGPU_TARGETS=gfx1151` | Zaměří se na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Použije sestavovací systém Ninja |

#### Krok 2: Ověření detekce GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Očekávaný výstup:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Krok 3: Trvalé přidání HIP do uživatelské cesty

Výše uvedený krok sestavení nastavil `%HIP_PATH%\bin` pouze pro aktuální relaci. Aby byly knihovny HIP dostupné v jakémkoli terminálu (nejen v x64 Native Tools Command Prompt), přidejte je trvale do své uživatelské proměnné `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Po přípravě llama.cpp na každém uzlu pokračujte na [Stahování modelu](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Krok 1: Sestavení llama.cpp

Naklonujte repozitář:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Sestavte s podporou ROCm a RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Příznak sestavení | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povolí softwarový stack ROCm |
| `-DGGML_RPC=ON` | Povolí RPC pro distribuovanou inferenci |
| `-DAMDGPU_TARGETS="gfx1151"` | Zaměří se na GPU Ryzen AI Halo (Radeon 8060s) |

Další možnosti sestavení naleznete v [dokumentaci k sestavení llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Krok 2: Ověření detekce GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Očekávaný výstup:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Po přípravě llama.cpp na každém uzlu pokračujte na [Stahování modelu](#downloading-the-model).
<!-- @os:end -->

## Stahování modelu

Tento postup používá [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model se 358 miliardami parametrů v kvantizaci `Q4_K_XL` od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Při této kvantizaci vyžaduje model přibližně 205 GB úložného prostoru a vejde se do společné paměti GPU dvou uzlů Ryzen AI Halo.

Stáhněte soubory GGUF pomocí Hugging Face CLI:
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

> **Poznámka**: Stažení modelu musí proběhnout na Počítači 1 (řadič). Pracovní uzly RPC nepotřebují místní kopii souborů modelu.

## Spuštění modelu v clusteru

Mechanismus llama.cpp RPC (Remote Procedure Call) umožňuje jedné instanci llama.cpp odesílat vrstvy modelu na vzdálené pracovní uzly přes síť. Jeden počítač funguje jako **řadič** (Počítač 1), který zajišťuje tokenizaci, plánování a orchestraci. Druhý počítač spouští lehký **RPC server** (Počítač 2), který zpřístupňuje svou paměť GPU a výpočetní výkon řadiči.

Při načítání llama.cpp rozloží model mezi oba uzly. Po načtení probíhá inference tak, jako by běžela na jediném akcelerátoru. Přenosy tenzorů a synchronizaci na pozadí zajišťuje RPC.

### Krok 1: Spuštění RPC serveru (Počítač 2)

Na Počítači 2 spusťte RPC server, aby zpřístupnil své prostředky GPU řadiči:
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

| Příznak | Účel |
|------|---------|
| `-p` | Port, na kterém se vysílá RPC server |
| `-c` | Povolí místní mezipaměť pro velké tenzory, čímž se předchází opakovaným síťovým přenosům během načítání modelu |
| `--host` | IP adresa, na kterou se RPC server naváže (`0.0.0.0` pro všechna rozhraní) |

Další možnosti naleznete v [dokumentaci k RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Spuštění modelu (Počítač 1)

Jakmile RPC server běží na Počítači 2, spusťte inferenci z Počítače 1 pomocí buď `llama-cli`, nebo `llama-server`.
#### llama-cli

`llama-cli` poskytuje rozhraní založené na terminálu pro přímou interakci s modelem. Je ideální pro benchmarking, ladění a nízkoúrovňové experimentování.

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

> **Zjištění `<RPC_WORKER_IP>`**: Na Machine 2 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento příkaz spusťte v Terminálu (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Zjištění `<RPC_WORKER_IP>`**: Na Machine 2 spusťte `ipconfig | findstr /C:"IPv4"` v Terminálu (Powershell), abyste zjistili jeho lokální IP adresu.

<!-- @os:end -->

Po spuštění `llama-cli` zobrazí průběh načítání modelu a přejde do interaktivního promptu, kde si můžete s modelem přímo povídat:

![llama-cli running GLM 4.7 across two nodes](assets/llama-cli-example.png)

#### llama-server

`llama-server` zpřístupňuje stejný inferenční engine prostřednictvím trvalého serverového procesu s integrovaným webovým rozhraním a HTTP API kompatibilním s OpenAI. Jedná se o preferované rozhraní pro dlouhodobě běžící nasazení, přístup více uživatelů a integraci s externími nástroji.

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

> **Zjištění `<RPC_WORKER_IP>`**: Na Machine 2 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento příkaz spusťte v Terminálu (Powershell).

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

> **Zjištění `<RPC_WORKER_IP>`**: Na Machine 2 spusťte `ipconfig | findstr /C:"IPv4"` v Terminálu (Powershell), abyste zjistili jeho lokální IP adresu.
<!-- @os:end -->

Po spuštění otevřete v prohlížeči adresu `http://<HOST_IP>:8081`, abyste získali přístup k integrovanému webovému rozhraní. To poskytuje chatovací rozhraní v prohlížeči pro interakci s modelem:

![llama-server web UI running GLM 4.7 across two nodes](assets/llama-server-example.png)

<!-- @os:linux -->
> **Zjištění `<HOST_IP>`**: Na Machine 1 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Zjištění `<HOST_IP>`**: Na Machine 1 spusťte `ipconfig | findstr /C:"IPv4"` v Terminálu (Powershell), abyste zjistili jeho lokální IP adresu.
<!-- @os:end -->

#### Přehled parametrů

| Příznak | Účel |
|------|---------|
| `-m` | Cesta k souboru modelu GGUF (použijte první fragment, `00001-of-00005`) |
| `-c` | Velikost kontextu v tokenech. Vyšší hodnoty spotřebovávají více paměti |
| `-fa on` | Povolí rocWMMA Flash Attention pro vyšší výkon na AMD GPU |
| `-ngl 999` | Odloží veškeré vrstvy modelu na GPU |
| `-lm none` | Nastaví režim načítání modelu na `none`, čímž zakáže mapování paměti (memory-mapping) a zkrátí dobu načítání, pokud velikost modelu přesahuje systémovou RAM, ale vejde se do VRAM |
| `--host` | IP adresa, na kterou se má `llama-server` navázat (pouze `llama-server`) |
| `--port` | Port, na kterém bude poskytováno HTTP API (pouze `llama-server`) |
| `--rpc` | Seznam koncových bodů RPC worker oddělených čárkami (`IP:port`) |

Úplný popis parametrů naleznete v [dokumentaci k llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) a [dokumentaci k llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Další kroky

- **Připojte aplikace třetích stran**: `llama-server` zpřístupňuje API kompatibilní s OpenAI. Nasměrujte libovolnou aplikaci kompatibilní s OpenAI (například Open WebUI) na `http://<HOST_IP>:8081` s libovolným zástupným API klíčem (např. `none`) a připojte se tak ke svému clusteru
- **Prozkoumejte další modely**: Procházejte kvantizované soubory GGUF na [Hugging Face](https://huggingface.co/models?search=gguf) a najděte modely, které se vejdou do celkové paměti GPU vašeho clusteru
- **Rozšiřte na čtyři uzly**: Přidejte další dva systémy Ryzen AI Halo jako další RPC workery, abyste získali přístup k modelům o velikosti bilionu parametrů. Předejte další koncové body parametru `--rpc` jako seznam oddělený čárkami (např. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)