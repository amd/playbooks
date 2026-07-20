<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tato příručka používá speciální značky, které GitHub neumí zobrazit. Pro správné zobrazení tohoto obsahu navštivte prosím [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

# Clustrování dvou Ryzen™ AI Halo pomocí RPC

## Přehled

Váš Ryzen™ AI Halo je již schopen lokálně spouštět velké jazykové modely. Clustrování tuto schopnost posouvá dál tím, že spojuje GPU paměť více systémů přes lokální síť, což vám umožní přístup k ještě větším modelům se silnějším uvažováním, lepší generací kódu a hlubším porozuměním více jazykům, a to zcela na vašem vlastním hardwaru.

Tato příručka vás naučí, jak nastavit cluster ze dvou systémů Ryzen AI Halo pomocí RPC enginu z llama.cpp a spustit GLM 4.7, model s 358 miliardami parametrů, na obou strojích současně s akcelerací AMD ROCm™.

## Co se naučíte

- Jak rozšířit alokaci VRAM na systémech Ryzen AI Halo
- Instalaci llama.cpp s podporou ROCm a RPC
- Konfiguraci RPC workeru a spuštění distribuovaného inferenčního zpracování napříč dvěma uzly
- Spuštění modelu se 358 miliardami parametrů na dvou propojených systémech Ryzen AI Halo

## Nastavení konfigurace paměti

> **Poznámka**: Tento krok proveďte na Machine 1 i Machine 2.

<!-- @os:windows -->
Ve Windows je pro spouštění větších modelů, které vyžadují více paměti, potřeba použít alokaci AMD Variable Graphics Memory (iGPU VRAM).

To lze provést otevřením ovládacího panelu AMD Software: Adrenalin Edition a přechodem na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavte hodnotu na **96 GB**. Pro projevení změn restartujte systém.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Na Linuxu ROCm využívá sdílený pool systémové paměti, který je ve výchozím nastavení konfigurován na polovinu systémové paměti.

Toto množství lze zvýšit změnou nastavení stránkování Translation Table Manager (TTM) v jádře pomocí následujících pokynů. AMD doporučuje v BIOSu nastavit minimální vyhrazenou VRAM (0,5 GB).

* Nainstalujte nástroj pipx a přidejte cestu k balíčkům instalovaným pomocí pipx do systémové cesty vyhledávání.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainstalujte balíček amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spusťte nástroj amd-ttm pro zjištění aktuálního nastavení sdílené paměti.
  ```bash
  amd-ttm
  ```

* Nastavte znovu velikost sdílené paměti na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte systém, aby se změny projevily.


<!-- @os:end -->
<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->
## Předpoklady

### Hardware

Tato příručka vyžaduje dvě jednotky Ryzen AI Halo a jeden ethernetový přepínač, zapojené v topologii hvězdy, přičemž každá jednotka je připojena přímo k přepínači.

| Komponenta | Množství | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočetní uzly tvořící cluster |
| 10Gbps ethernetový přepínač | 1 | Centrální přepínač umožňující komunikaci více uzlů Ryzen AI Halo (alespoň 2 porty) |
| Ethernetový kabel | 2 | Připojuje každou jednotku Halo k přepínači (doporučeno Cat 7 nebo vyšší) |

> **Poznámka**: Pro připojení obou jednotek Ryzen AI Halo jsou potřeba dva porty ethernetového přepínače. Třetí port je potřeba, pokud k modelu přistupujete ze samostatného klientského stroje místo z jedné z jednotek Halo.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Nainstalujte prosím:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) s pracovní zátěží **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyzické nastavení hardwaru

> **Poznámka**: Tento krok proveďte na Machine 1 i Machine 2.

Připojte každou jednotku Ryzen AI Halo k ethernetovému přepínači pomocí kabelu Cat 7 (nebo vyššího). Tím se vytvoří 10Gbps propojení používané pro vysokorychlostní komunikaci mezi uzly.
<!-- @os:linux -->
### 1. Zjištění síťových rozhraní

Na každém stroji zjistěte název síťového rozhraní a poznamenejte si ho (dále bude označován jako `IFNAME`). Spusťte:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tím se přímo vypíše název rozhraní, například:

```bash
enp191s0
```

### 2. Ověření rychlosti síťového propojení

Ověřte, že je propojení aktivní a běží plnou rychlostí, kontrolou rychlosti vašeho rozhraní:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupním názvem rozhraní z kroku [1. Zjištění síťových rozhraní](#1-determine-network-interfaces)

Měli byste vidět rychlost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Pokud je rychlost nižší než `10000Mb/s` nebo se propojení nenaváže, zkontrolujte kabelové připojení a ověřte, že je port přepínače nastaven na 10Gbps. Některé přepínače vyžadují zakázání automatického vyjednávání a ruční nastavení rychlosti propojení; podrobnosti naleznete v dokumentaci k vašemu přepínači.

<!-- @os:end -->

<!-- @os:windows -->
### Ověření rychlosti síťového propojení

Na každém stroji zkontrolujte rychlost propojení vašich síťových rozhraní:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaše ethernetové rozhraní by mělo být `Up` a fungovat rychlostí `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Poznámka**: Pokud je rychlost nižší než `10 Gbps` nebo se propojení nenaváže, zkontrolujte kabelové připojení a ověřte, že je port přepínače nastaven na 10Gbps. Některé přepínače vyžadují zakázání automatického vyjednávání a ruční nastavení rychlosti propojení; podrobnosti naleznete v dokumentaci k vašemu přepínači.

<!-- @os:end -->

## Instalace llama.cpp

> **Poznámka**: Tento krok proveďte na Machine 1 i Machine 2.

K dispozici jsou dvě možnosti instalace:

- [Možnost 1: Lemonade SDK (doporučeno)](#option-1-lemonade-sdk-recommended) – předkompilované binární soubory, nejrychlejší nastavení
- [Možnost 2: Ruční sestavení ze zdrojového kódu](#option-2-manual-source-build) – sestavení ze zdrojového kódu s plnou kontrolou nad příznaky sestavení

### Možnost 1: Lemonade SDK (doporučeno)

Lemonade SDK poskytuje nightly buildy llama.cpp s akcelerací AMD ROCm 7, cílené na GPU jako gfx1151 (Strix Halo / Ryzen AI Max+ 395) a další nedávné architektury Radeon.

<!-- @os:windows -->
#### Step 1: Stažení předem sestavených binárních souborů

Přejděte na stránku s nejnovějším vydáním a stáhněte archiv odpovídající vaší platformě a cílovému GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stáhněte soubor s názvem `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo sestavení).

#### Step 2: Rozbalení binárních souborů

Rozbalte stažený archiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tento adresář nyní obsahuje sestavení `llama-cli.exe`, `llama-server.exe` a `rpc-server.exe` s podporou ROCm, předkompilovaná pro váš systém Ryzen AI Halo.

#### Step 3: Ověření detekce GPU

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
#### Step 1: Stažení předem sestavených binárních souborů

Přejděte na stránku s nejnovějším vydáním a stáhněte archiv odpovídající vaší platformě a cílovému GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stáhněte soubor s názvem `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo sestavení).

#### Step 2: Rozbalení a příprava binárních souborů

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Tento adresář nyní obsahuje sestavení `llama-cli`, `llama-server` a `rpc-server` s podporou ROCm, předkompilovaná pro váš systém Ryzen AI Halo.

#### Step 3: Ověření detekce GPU

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
Jakmile je llama.cpp připraveno na obou uzlech, pokračujte částí [Stažení modelu](#downloading-the-model).

### Možnost 2: Ruční sestavení ze zdrojového kódu

<!-- @os:windows -->
#### Step 1: Sestavení llama.cpp

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

| Přepínač sestavení | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povolí softwarový zásobník ROCm/HIP |
| `-DGGML_RPC=ON` | Povolí RPC pro distribuovanou inferenci |
| `-DGPU_TARGETS=gfx1151` | Cílí na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Používá sestavovací systém Ninja |

#### Step 2: Ověření detekce GPU

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

#### Step 3: Trvalé přidání HIP do uživatelské cesty

Výše uvedený krok sestavení nastavil `%HIP_PATH%\bin` pouze pro aktuální relaci. Aby byly knihovny HIP dostupné v jakémkoli terminálu (nejen v x64 Native Tools Command Prompt), přidejte je trvale do své uživatelské proměnné `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Jakmile je llama.cpp připraveno na obou uzlech, pokračujte částí [Stažení modelu](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: Sestavení llama.cpp

Naklonujte repozitář:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Sestavte s podporou ROCm a RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Přepínač sestavení | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povolí softwarový zásobník ROCm |
| `-DGGML_RPC=ON` | Povolí RPC pro distribuovanou inferenci |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Povolí rocWMMA pro vylepšenou funkci Flash Attention na GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Cílí na GPU Ryzen AI Halo (Radeon 8060s) |

Další možnosti sestavení naleznete v [dokumentaci k sestavení llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Step 2: Ověření detekce GPU

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

Jakmile je llama.cpp připraveno na obou uzlech, pokračujte částí [Stažení modelu](#downloading-the-model).
<!-- @os:end -->

## Stažení modelu

Tato příručka používá [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model se 358 miliardami parametrů v kvantizaci `Q4_K_XL` od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Při této kvantizaci vyžaduje model přibližně 205 GB úložného prostoru a vejde se do kombinované paměti GPU dvou uzlů Ryzen AI Halo.

Stáhněte soubory GGUF pomocí rozhraní příkazového řádku Hugging Face:
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

> **Poznámka**: Stažení modelu musí být dokončeno na Machine 1 (řadiči). Uzly RPC worker nepotřebují místní kopii souborů modelu.

## Spuštění modelu v clusteru

Engine llama.cpp RPC (Remote Procedure Call) umožňuje jediné instanci llama.cpp přesunout vrstvy modelu na vzdálené workery přes síť. Jeden stroj funguje jako **řadič** (Machine 1) a zajišťuje tokenizaci, plánování a orchestraci. Druhý stroj spouští lehký **server RPC** (Machine 2), který zpřístupňuje řadiči svou paměť GPU a výpočetní výkon.

Při načítání llama.cpp rozdělí model mezi oba uzly. Jakmile je model načten, inference probíhá, jako by běžela na jediném akcelerátoru. RPC na pozadí zajišťuje přenosy tenzorů a synchronizaci.

### Step 1: Spuštění serveru RPC (Machine 2)

Na stroji Machine 2 spusťte server RPC, aby zpřístupnil své prostředky GPU řadiči:
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

| Přepínač | Účel |
|------|---------|
| `-p` | Port, na kterém se vysílá server RPC |
| `-c` | Povolí lokální mezipaměť pro velké tenzory, čímž se předejde opakovaným síťovým přenosům během načítání modelu |
| `--host` | IP adresa, na kterou se server RPC naváže (`0.0.0.0` pro všechna rozhraní) |

Další možnosti naleznete v [dokumentaci k RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Step 2: Spuštění modelu (Machine 1)

Jakmile server RPC běží na stroji Machine 2, spusťte inferenci na stroji Machine 1 pomocí `llama-cli` nebo `llama-server`.

#### llama-cli

`llama-cli` poskytuje terminálové rozhraní pro přímou interakci s modelem. Je ideální pro benchmarking, ladění a experimentování na nízké úrovni.

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

> **Zjištění `<RPC_WORKER_IP>`**: Na stroji Machine 2 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho místní IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento příkaz spusťte v terminálu (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Zjištění `<RPC_WORKER_IP>`**: Na stroji Machine 2 spusťte v terminálu (Powershell) příkaz `ipconfig | findstr /C:"IPv4"`, abyste zjistili jeho místní IP adresu.

<!-- @os:end -->

Po spuštění zobrazuje `llama-cli` průběh načítání modelu a přejde do interaktivního režimu, kde můžete přímo komunikovat s modelem:

![llama-cli spouštějící model GLM 4.7 na dvou uzlech](assets/llama-cli-example.png)
#### llama-server

`llama-server` zpřístupňuje stejný inferenční engine prostřednictvím trvalého serverového procesu s integrovaným webovým rozhraním a HTTP API kompatibilním s OpenAI. Toto rozhraní je preferovanou volbou pro dlouhodobě běžící nasazení, přístup více uživatelů a integraci s externími nástroji.

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

> **Zjištění `<RPC_WORKER_IP>`**: Na počítači 2 spusťte příkaz `hostname -I | awk '{print $1}'`, abyste zjistili jeho místní IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento příkaz spusťte v terminálu (Powershell).

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

> **Zjištění `<RPC_WORKER_IP>`**: Na počítači 2 spusťte v terminálu (Powershell) příkaz `ipconfig | findstr /C:"IPv4"`, abyste zjistili jeho místní IP adresu.
<!-- @os:end -->

Po spuštění otevřete v prohlížeči adresu `http://<HOST_IP>:8081`, čímž získáte přístup k integrovanému webovému rozhraní. To poskytuje chatovací rozhraní v prohlížeči pro interakci s modelem:

![Webové rozhraní llama-server se spuštěným modelem GLM 4.7 na dvou uzlech](assets/llama-server-example.png)

<!-- @os:linux -->
> **Zjištění `<HOST_IP>`**: Na počítači 1 spusťte příkaz `hostname -I | awk '{print $1}'`, abyste zjistili jeho místní IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Zjištění `<HOST_IP>`**: Na počítači 1 spusťte v terminálu (Powershell) příkaz `ipconfig | findstr /C:"IPv4"`, abyste zjistili jeho místní IP adresu.
<!-- @os:end -->

#### Přehled parametrů

| Příznak | Účel |
|------|---------|
| `-m` | Cesta k souboru modelu GGUF (použijte první část, `00001-of-00005`) |
| `-c` | Velikost kontextu v tokenech. Vyšší hodnoty využívají více paměti |
| `-fa on` | Povoluje rocWMMA Flash Attention pro vyšší výkon na GPU AMD |
| `-ngl 999` | Přenese všechny vrstvy modelu na GPU |
| `--no-mmap` | Zakáže mapování paměti, čímž zkrátí dobu načítání, pokud velikost modelu přesahuje kapacitu systémové paměti RAM, ale vejde se do VRAM |
| `--host` | IP adresa, na kterou se má `llama-server` navázat (pouze `llama-server`) |
| `--port` | Port, na kterém se zpřístupní HTTP API (pouze `llama-server`) |
| `--rpc` | Seznam koncových bodů RPC pracovníků oddělených čárkami (`IP:port`) |

Úplný popis použití parametrů najdete v dokumentaci [llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) a v dokumentaci [llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Další kroky

- **Připojení aplikací třetích stran**: `llama-server` zpřístupňuje API kompatibilní s OpenAI. Nasměrujte libovolnou aplikaci kompatibilní s OpenAI (například Open WebUI) na adresu `http://<HOST_IP>:8081` s libovolným zástupným API klíčem (např. `none`), abyste ji připojili ke svému clusteru
- **Prozkoumání dalších modelů**: Procházejte kvantizované modely GGUF na [Hugging Face](https://huggingface.co/models?search=gguf) a najděte modely, které se vejdou do celkové paměti GPU vašeho clusteru
- **Rozšíření na čtyři uzly**: Přidejte další dva systémy Ryzen AI Halo jako další RPC pracovníky, abyste získali přístup k modelům o velikosti až 1 bilion parametrů. Předejte další koncové body parametru `--rpc` jako seznam oddělený čárkami (např. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)