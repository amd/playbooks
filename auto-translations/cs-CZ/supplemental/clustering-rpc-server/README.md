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

# Clustrování dvou Ryzen™ AI Halo pomocí RPC

## Přehled

Váš Ryzen™ AI Halo je již schopen lokálně spouštět velké jazykové modely. Clustrování posouvá tuto schopnost dále tím, že kombinuje paměť GPU více systémů přes lokální síť, což vám umožňuje přístup k ještě větším modelům se silnějším uvažováním, lepší generací kódu a hlubším vícejazyčným porozuměním, a to zcela na vašem vlastním hardwaru.

Tento playbook vás naučí, jak clustrovat dva systémy Ryzen AI Halo pomocí RPC enginu nástroje llama.cpp a spustit model GLM 4.7 s 358 miliardami parametrů napříč oběma stroji s akcelerací AMD ROCm™.

## Co se naučíte

- Jak rozšířit alokaci VRAM na systémech Ryzen AI Halo
- Instalaci llama.cpp s podporou ROCm a RPC
- Konfiguraci RPC workeru a spuštění distribuované inference napříč dvěma uzly
- Spuštění modelu se 358 miliardami parametrů napříč dvěma propojenými systémy Ryzen AI Halo v síti

## Nastavení konfigurace paměti

> **Poznámka**: Tento krok dokončete na Stroji 1 i Stroji 2.

<!-- @os:windows -->
Ve Windows, abychom mohli spouštět větší modely vyžadující více paměti, musíme použít alokaci AMD Variable Graphics Memory (iGPU VRAM).

Toho lze docílit otevřením ovládacího panelu AMD Software: Adrenalin Edition a přechodem do: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavte hodnotu na **96 GB**. Aby se změny projevily, systém restartujte.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Na Linuxu využívá ROCm sdílený fond systémové paměti, který je ve výchozím nastavení nakonfigurován na polovinu systémové paměti.

Toto množství lze zvýšit změnou nastavení stránek jádrového Translation Table Manager (TTM), a to podle následujících pokynů. AMD doporučuje nastavit minimální vyhrazenou VRAM v BIOSu (0,5 GB).

* Nainstalujte nástroj pipx a přidejte cestu k balíčkům instalovaným přes pipx do systémové cesty pro vyhledávání.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainstalujte balíček amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spusťte nástroj amd-ttm a zjistěte aktuální nastavení sdílené paměti.
  ```bash
  amd-ttm
  ```

* Přenastavte hodnoty sdílené paměti na **120 GB**:
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

Tento playbook vyžaduje dvě jednotky Ryzen AI Halo a jeden ethernetový přepínač, propojené v topologii typu hvězda, kde je každá jednotka přímo připojena k přepínači.

| Komponenta | Množství | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočetní uzly tvořící cluster |
| 10Gbps ethernetový přepínač | 1 | Centrální přepínač umožňující komunikaci více uzlů Ryzen AI Halo (alespoň 2 porty) |
| Ethernetový kabel | 2 | Připojuje každou jednotku Halo k přepínači (doporučeno Cat 7 nebo vyšší) |

> **Poznámka**: Pro připojení obou jednotek Ryzen AI Halo jsou zapotřebí dva porty ethernetového přepínače. Třetí port je zapotřebí, pokud k modelu přistupujete ze samostatného klientského stroje namísto z jedné z jednotek Halo.

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

## Nastavení fyzického hardwaru

> **Poznámka**: Tento krok dokončete na Stroji 1 i Stroji 2.

Připojte každou jednotku Ryzen AI Halo k ethernetovému přepínači pomocí kabelu Cat 7 (nebo vyššího). Tím vznikne 10Gbps spoj používaný pro vysokorychlostní komunikaci mezi uzly.
<!-- @os:linux -->
### 1. Zjištění síťových rozhraní

Na každém stroji zjistěte název jeho síťového rozhraní a poznamenejte si ho (dále bude označován jako `IFNAME`). Spusťte:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tím se přímo vypíše název rozhraní, například:

```bash
enp191s0
```

### 2. Ověření rychlosti síťového spoje

Potvrďte, že je spoj aktivní a běží na plnou rychlost, kontrolou rychlosti vašeho rozhraní:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupním názvem rozhraní z kroku [1. Zjištění síťových rozhraní](#1-determine-network-interfaces)

Měli byste vidět rychlost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Pokud je rychlost nižší než `10000Mb/s` nebo se spoj nenaváže, zkontrolujte připojení kabelu a ověřte, že je port přepínače nastaven na 10 Gbps. Některé přepínače vyžadují vypnutí automatického vyjednávání a ruční nastavení rychlosti spoje; nahlédněte do dokumentace svého přepínače.

<!-- @os:end -->

<!-- @os:windows -->
### Ověření rychlosti síťového spoje

Na každém stroji zkontrolujte rychlost spoje svých síťových rozhraní:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaše ethernetové rozhraní by mělo být `Up` a běžet rychlostí `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Poznámka**: Pokud je rychlost nižší než `10 Gbps` nebo se spoj nenaváže, zkontrolujte připojení kabelu a ověřte, že je port přepínače nastaven na 10 Gbps. Některé přepínače vyžadují vypnutí automatického vyjednávání a ruční nastavení rychlosti spoje; nahlédněte do dokumentace svého přepínače.

<!-- @os:end -->

## Instalace llama.cpp

> **Poznámka**: Tento krok dokončete na Stroji 1 i Stroji 2.

K dispozici jsou dvě možnosti instalace:

- [Možnost 1: Lemonade SDK (doporučeno)](#option-1-lemonade-sdk-recommended) – předpřipravené binární soubory, nejrychlejší nastavení
- [Možnost 2: Manuální sestavení ze zdroje](#option-2-manual-source-build) – sestavení ze zdrojového kódu s plnou kontrolou nad příznaky sestavení

### Možnost 1: Lemonade SDK (doporučeno)

Lemonade SDK poskytuje noční sestavení llama.cpp s akcelerací AMD ROCm 7, cílené na GPU, jako je gfx1151 (Strix Halo / Ryzen AI Max+ 395), a další nedávné architektury Radeon.

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

### Možnost 2: Ruční sestavení ze zdrojového kódu

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
| `-DGGML_HIP=ON` | Povolí softwarový zásobník ROCm/HIP |
| `-DGGML_RPC=ON` | Povolí RPC pro distribuovanou inferenci |
| `-DGPU_TARGETS=gfx1151` | Cílí na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Používá sestavovací systém Ninja |

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
| `-DGGML_HIP=ON` | Povolí softwarový zásobník ROCm |
| `-DGGML_RPC=ON` | Povolí RPC pro distribuovanou inferenci |
| `-DAMDGPU_TARGETS="gfx1151"` | Cílí na GPU Ryzen AI Halo (Radeon 8060s) |

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

Tento návod používá [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model s 358 miliardami parametrů v kvantizaci `Q4_K_XL` od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Při této kvantizaci vyžaduje model přibližně 205 GB úložného prostoru a vejde se do kombinované paměti GPU dvou uzlů Ryzen AI Halo.

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

> **Poznámka**: Stahování modelu musí být dokončeno na stroji Machine 1 (řadiči). Uzly RPC workerů nepotřebují lokální kopii souborů modelu.

## Spuštění modelu v clusteru

Engine llama.cpp RPC (Remote Procedure Call) umožňuje jediné instanci llama.cpp odsunout vrstvy modelu na vzdálené workery po síti. Jeden stroj funguje jako **řadič** (Machine 1) a zajišťuje tokenizaci, plánování a orchestraci. Druhý stroj spouští lehký **RPC server** (Machine 2), který zpřístupní svou paměť GPU a výpočetní výkon řadiči.

Při načítání llama.cpp rozdělí model mezi oba uzly. Po načtení probíhá inference, jako by běžela na jediném akcelerátoru. RPC v pozadí zajišťuje přenosy tenzorů a synchronizaci.

### Krok 1: Spuštění RPC serveru (Machine 2)

Na Machine 2 spusťte RPC server, aby zpřístupnil své prostředky GPU řadiči:
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
| `-p` | Port, na kterém se RPC server vysílá |
| `-c` | Povolí lokální cache pro velké tenzory, čímž se předchází opakovaným síťovým přenosům během načítání modelu |
| `--host` | IP adresa, na kterou se RPC server naváže (`0.0.0.0` pro všechna rozhraní) |

Další možnosti naleznete v [dokumentaci RPC pro llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Spuštění modelu (Machine 1)

Se spuštěným RPC serverem na Machine 2 spusťte inferenci z Machine 1 pomocí `llama-cli` nebo `llama-server`.

#### llama-cli

`llama-cli` poskytuje terminálové rozhraní pro přímou interakci s modelem. Je ideální pro benchmarking, ladění a experimentování na nízké úrovni.

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

> **Zjištění `<RPC_WORKER_IP>`**: Na Machine 2 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili její lokální IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento příkaz spusťte v terminálu (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Zjištění `<RPC_WORKER_IP>`**: Na Machine 2 spusťte `ipconfig | findstr /C:"IPv4"` v terminálu (Powershell), abyste zjistili její lokální IP adresu.

<!-- @os:end -->

Po spuštění zobrazí `llama-cli` průběh načítání modelu a přejde do interaktivního promptu, ve kterém můžete s modelem přímo konverzovat:

![llama-cli spuštěný s modelem GLM 4.7 na dvou uzlech](assets/llama-cli-example.png)
#### llama-server

`llama-server` zpřístupňuje stejný inferenční engine prostřednictvím trvalého serverového procesu s integrovaným webovým rozhraním a HTTP API kompatibilním s OpenAI. Toto rozhraní je preferovanou volbou pro dlouhodoběji běžící nasazení, přístup více uživatelů a integraci s externími nástroji.

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

> **Zjištění `<RPC_WORKER_IP>`**: Na Zařízení 2 spusťte `hostname -I | awk '{print $1}'`, čímž zjistíte jeho místní IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento příkaz spusťte v terminálu (Powershell).

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

> **Zjištění `<RPC_WORKER_IP>`**: Na Zařízení 2 spusťte `ipconfig | findstr /C:"IPv4"` v terminálu (Powershell), čímž zjistíte jeho místní IP adresu.
<!-- @os:end -->

Po spuštění otevřete ve svém prohlížeči adresu `http://<HOST_IP>:8081`, čímž získáte přístup k integrovanému webovému rozhraní. To poskytuje webové chatovací rozhraní pro interakci s modelem:

![Webové rozhraní llama-server se spuštěným modelem GLM 4.7 na dvou uzlech](assets/llama-server-example.png)

<!-- @os:linux -->
> **Zjištění `<HOST_IP>`**: Na Zařízení 1 spusťte `hostname -I | awk '{print $1}'`, čímž zjistíte jeho místní IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Zjištění `<HOST_IP>`**: Na Zařízení 1 spusťte `ipconfig | findstr /C:"IPv4"` v terminálu (Powershell), čímž zjistíte jeho místní IP adresu.
<!-- @os:end -->

#### Přehled parametrů

| Příznak | Účel |
|------|---------|
| `-m` | Cesta k souboru modelu GGUF (použijte první díl, `00001-of-00005`) |
| `-c` | Velikost kontextu v tokenech. Vyšší hodnoty spotřebovávají více paměti |
| `-fa on` | Povolí rocWMMA Flash Attention pro vyšší výkon na GPU AMD |
| `-ngl 999` | Přesune všechny vrstvy modelu na GPU |
| `-lm none` | Nastaví režim načítání modelu na `none`, čímž se vypne mapování paměti (memory-mapping) za účelem zkrácení doby načítání v případech, kdy je velikost modelu větší než systémová RAM, ale vejde se do VRAM |
| `--host` | IP adresa, na kterou se má `llama-server` navázat (pouze `llama-server`) |
| `--port` | Port, na kterém se poskytuje HTTP API (pouze `llama-server`) |
| `--rpc` | Čárkami oddělený seznam koncových bodů RPC pracovních uzlů (`IP:port`) |

Úplný popis použití parametrů naleznete v [dokumentaci k llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) a [dokumentaci k llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Další kroky

- **Připojení aplikací třetích stran**: `llama-server` zpřístupňuje API kompatibilní s OpenAI. Nasměrujte libovolnou aplikaci kompatibilní s OpenAI (například Open WebUI) na adresu `http://<HOST_IP>:8081` s jakýmkoli náhradním API klíčem (např. `none`) a připojíte se tak ke svému clusteru
- **Prozkoumání dalších modelů**: Procházejte kvantizované soubory GGUF na [Hugging Face](https://huggingface.co/models?search=gguf) a najděte modely, které se vejdou do celkové kombinované paměti GPU vašeho clusteru
- **Škálování na čtyři uzly**: Přidáním dalších dvou systémů Ryzen AI Halo jako dalších pracovních uzlů RPC získáte přístup k modelům v řádu bilionu parametrů. Předejte další koncové body parametru `--rpc` formou čárkami odděleného seznamu (např. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)