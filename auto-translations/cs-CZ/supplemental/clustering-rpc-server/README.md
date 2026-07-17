<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering Two Ryzen™ AI Halos with RPC

## Přehled

Váš Ryzen™ AI Halo je již schopen spouštět velké jazykové modely lokálně. Clustering to posouvá dál tím, že kombinuje GPU paměť více systémů přes lokální síť, čímž získáte přístup k ještě větším modelům se silnějším uvažováním, lepším generováním kódu a hlubším vícejazyčným porozuměním – vše zcela na vlastním hardwaru.

Tento playbook vás naučí, jak propojit dva systémy Ryzen AI Halo do clusteru pomocí RPC enginu llama.cpp a spustit GLM 4.7, model s 358 miliardami parametrů, na obou strojích s akcelerací AMD ROCm™.

## Co se naučíte

- Jak rozšířit alokaci VRAM na systémech Ryzen AI Halo
- Instalaci llama.cpp s podporou ROCm a RPC
- Konfiguraci RPC workeru a spuštění distribuované inference přes dva uzly
- Spuštění modelu s 358 miliardami parametrů na dvou propojených systémech Ryzen AI Halo

## Nastavení konfigurace paměti

> **Poznámka**: Tento krok proveďte na obou strojích – Machine 1 i Machine 2.

<!-- @os:windows -->
Ve Windows je pro spouštění větších modelů vyžadujících vyšší paměť nutné použít alokaci AMD Variable Graphics Memory (iGPU VRAM).

To lze provést otevřením ovládacího panelu AMD Software: Adrenalin Edition a přechodem na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavte hodnotu na **96 GB**. Pro uplatnění změn prosím restartujte systém.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V Linuxu ROCm využívá sdílený systémový paměťový pool, který je ve výchozím nastavení nakonfigurován na polovinu systémové paměti.

Toto množství lze zvýšit změnou nastavení stránky Translation Table Manager (TTM) jádra podle následujících pokynů. AMD doporučuje nastavit minimální vyhrazenou VRAM v BIOSu (0,5 GB).

* Nainstalujte nástroj pipx a přidejte cestu pro pipx nainstalovaná kola do systémové vyhledávací cesty.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainstalujte balíček amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spusťte nástroj amd-ttm pro dotaz na aktuální nastavení sdílené paměti.
  ```bash
  amd-ttm
  ```

* Překonfigurujte nastavení sdílené paměti na **120 GB**:
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

Tento playbook vyžaduje dvě jednotky Ryzen AI Halo a jeden ethernetový switch, propojené v hvězdicové topologii, přičemž každá jednotka je přímo zapojena do switche.

| Komponenta | Množství | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočetní uzly tvořící cluster |
| 10Gbps ethernetový switch | 1 | Centrální switch umožňující komunikaci více uzlů Ryzen AI Halo (alespoň 2 porty) |
| Ethernetový kabel | 2 | Propojuje každou jednotku Halo se switchem (doporučen Cat 7 nebo vyšší) |

> **Poznámka**: Pro připojení dvou jednotek Ryzen AI Halo jsou potřeba dva porty ethernetového switche. Třetí port je vyžadován, pokud přistupujete k modelu ze samostatného klientského stroje místo z jedné z jednotek Halo.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Prosím nainstalujte:
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

> **Poznámka**: Tento krok proveďte na obou strojích – Machine 1 i Machine 2.

Připojte každou jednotku Ryzen AI Halo k ethernetovému switchi pomocí kabelu Cat 7 (nebo vyššího). Tím se vytvoří 10Gbps linka používaná pro vysokorychlostní komunikaci mezi uzly.
<!-- @os:linux -->
### 1. Určení síťových rozhraní

Na každém stroji zjistěte název jeho síťového rozhraní a poznamenejte si ho (níže bude označován jako `IFNAME`). Spusťte:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tím se přímo vypíše název rozhraní, například:

```bash
enp191s0
```

### 2. Ověření rychlostí síťového spojení

Potvrďte, že linka je aktivní a běží na plné rychlosti, kontrolou rychlosti vašeho rozhraní:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` názvem výstupního rozhraní z části [1. Určení síťových rozhraní](#1-determine-network-interfaces)

Měli byste vidět rychlost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Pokud je rychlost nižší než `10000Mb/s` nebo linka nenabíhá, zkontrolujte připojení kabelu a ověřte, že port switche je nastaven na 10Gbps. Některé switche vyžadují vypnutí automatického vyjednávání a ruční nastavení rychlosti linky; viz dokumentaci vašeho switche.

<!-- @os:end -->

<!-- @os:windows -->
### Ověření rychlosti síťového spojení

Na každém stroji zkontrolujte rychlost linky vašich síťových rozhraní:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaše ethernetové rozhraní by mělo být `Up` a běžet na `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Poznámka**: Pokud je rychlost nižší než `10 Gbps` nebo linka nenabíhá, zkontrolujte připojení kabelu a ověřte, že port switche je nastaven na 10Gbps. Některé switche vyžadují vypnutí automatického vyjednávání a ruční nastavení rychlosti linky; viz dokumentaci vašeho switche.

<!-- @os:end -->

## Instalace llama.cpp

> **Poznámka**: Tento krok proveďte na obou strojích – Machine 1 i Machine 2.

K dispozici jsou dvě možnosti instalace:

- [Možnost 1: Lemonade SDK (Doporučeno)](#option-1-lemonade-sdk-recommended) – předkompilované binárky, nejrychlejší nastavení
- [Možnost 2: Ruční sestavení ze zdrojového kódu](#option-2-manual-source-build) – sestavení ze zdroje s plnou kontrolou nad příznaky sestavení

### Možnost 1: Lemonade SDK (Doporučeno)

Lemonade SDK poskytuje noční sestavení llama.cpp s akcelerací AMD ROCm 7, zaměřená na GPU jako gfx1151 (Strix Halo / Ryzen AI Max+ 395) a další nedávné architektury Radeon.

<!-- @os:windows -->
#### Krok 1: Stažení předkompilovaných binárních souborů

Přejděte na stránku nejnovějšího vydání a stáhněte archiv odpovídající vaší platformě a cílovému GPU:

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

Přejděte na stránku nejnovějšího vydání a stáhněte archiv odpovídající vaší platformě a cílovému GPU:

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
Po přípravě llama.cpp na každém uzlu pokračujte na [Stažení modelu](#downloading-the-model).

### Možnost 2: Ruční sestavení ze zdrojového kódu

<!-- @os:windows -->
#### Krok 1: Sestavení llama.cpp

Otevřete **x64 Native Tools Command Prompt** (nainstalovaný s Visual Studio Build Tools) a naklonujte repozitář:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Přidejte HIP do cesty a sestavte s podporou ROCm a RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Příznak sestavení | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povoluje softwarový zásobník ROCm/HIP |
| `-DGGML_RPC=ON` | Povoluje RPC pro distribuovanou inferenci |
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

#### Krok 3: Přidání HIP do uživatelské cesty

Výše uvedený krok sestavení nastavil `%HIP_PATH%\bin` pouze pro aktuální relaci. Aby byly knihovny HIP dostupné v jakémkoli terminálu (nejen v x64 Native Tools Command Prompt), přidejte je trvale do uživatelské proměnné `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Po přípravě llama.cpp na každém uzlu pokračujte na [Stažení modelu](#downloading-the-model).
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
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Příznak sestavení | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povoluje softwarový zásobník ROCm |
| `-DGGML_RPC=ON` | Povoluje RPC pro distribuovanou inferenci |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Povoluje rocWMMA pro vylepšenou Flash Attention na GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Cílí na GPU Ryzen AI Halo (Radeon 8060s) |

Další možnosti sestavení naleznete v [dokumentaci sestavení llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Po přípravě llama.cpp na každém uzlu pokračujte na [Stažení modelu](#downloading-the-model).
<!-- @os:end -->

## Stažení modelu

Tento playbook používá [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model s 358 miliardami parametrů v kvantizaci `Q4_K_XL` od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Při této kvantizaci model vyžaduje přibližně 205 GB úložiště a vejde se do kombinované GPU paměti dvou uzlů Ryzen AI Halo.

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

> **Poznámka**: Stažení modelu musí být dokončeno na Machine 1 (kontroléru). Uzly RPC workeru nepotřebují lokální kopii souborů modelu.

## Spuštění modelu na clusteru

RPC (Remote Procedure Call) engine llama.cpp umožňuje jedné instanci llama.cpp přenést vrstvy modelu na vzdálené workery přes síť. Jeden stroj funguje jako **kontrolér** (Machine 1), který zajišťuje tokenizaci, plánování a orchestraci. Druhý stroj provozuje lehký **RPC server** (Machine 2), který zpřístupňuje svou GPU paměť a výpočetní kapacitu kontroléru.

Při načítání llama.cpp rozdělí model mezi oba uzly. Po načtení probíhá inference, jako by běžela na jediném akcelerátoru. RPC zajišťuje přenosy tenzorů a synchronizaci na pozadí.

### Krok 1: Spuštění RPC serveru (Machine 2)

Na Machine 2 spusťte RPC server, aby zpřístupnil své GPU prostředky kontroléru:
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

| Příznak | Účel |
|------|---------|
| `-p` | Port, na kterém bude RPC server vysílat |
| `-c` | Povoluje lokální mezipaměť pro velké tenzory, čímž se zabraňuje opakovaným síťovým přenosům při načítání modelu |
| `--host` | IP adresa, na které bude RPC server naslouchat (`0.0.0.0` pro všechna rozhraní) |

Další možnosti naleznete v [dokumentaci RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Spuštění modelu (Machine 1)

Se spuštěným RPC serverem na Machine 2 spusťte inferenci z Machine 1 pomocí `llama-cli` nebo `llama-server`.

#### llama-cli

`llama-cli` poskytuje terminálové rozhraní pro přímou interakci s modelem. Je ideální pro benchmarking, ladění a nízkoúrovňové experimenty.

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

> **Nalezení `<RPC_WORKER_IP>`**: Na Machine 2 spusťte `hostname -I | awk '{print $1}'` pro zjištění jeho lokální IP adresy.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Spusťte tento příkaz v Terminálu (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Nalezení `<RPC_WORKER_IP>`**: Na Machine 2 spusťte `ipconfig | findstr /C:"IPv4"` v Terminálu (Powershell) pro zjištění jeho lokální IP adresy.

<!-- @os:end -->

Po spuštění `llama-cli` zobrazí průběh načítání modelu a přejde do interaktivní výzvy, kde můžete přímo chatovat s modelem:

![llama-cli spuštěný s GLM 4.7 přes dva uzly](assets/llama-cli-example.png)

#### llama-server

`llama-server` zpřístupňuje stejný inference engine prostřednictvím trvalého serverového procesu s integrovaným webovým uživatelským rozhraním a HTTP API kompatibilním s OpenAI. Toto je preferované rozhraní pro déle běžící nasazení, přístup více uživatelů a integraci s externími nástroji.

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

> **Nalezení `<RPC_WORKER_IP>`**: Na Machine 2 spusťte `hostname -I | awk '{print $1}'` pro zjištění jeho lokální IP adresy.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Spusťte tento příkaz v Terminálu (Powershell).

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

> **Nalezení `<RPC_WORKER_IP>`**: Na Machine 2 spusťte `ipconfig | findstr /C:"IPv4"` v Terminálu (Powershell) pro zjištění jeho lokální IP adresy.
<!-- @os:end -->

Po spuštění otevřete `http://<HOST_IP>:8081` v prohlížeči pro přístup k vestavěnému webovému uživatelskému rozhraní. To poskytuje chatovací rozhraní v prohlížeči pro interakci s modelem:

![Webové uživatelské rozhraní llama-server spuštěné s GLM 4.7 přes dva uzly](assets/llama-server-example.png)

<!-- @os:linux -->
> **Nalezení `<HOST_IP>`**: Na Machine 1 spusťte `hostname -I | awk '{print $1}'` pro zjištění jeho lokální IP adresy.
<!-- @os:end -->

<!-- @os:windows -->
> **Nalezení `<HOST_IP>`**: Na Machine 1 spusťte `ipconfig | findstr /C:"IPv4"` v Terminálu (Powershell) pro zjištění jeho lokální IP adresy.
<!-- @os:end -->

#### Přehled parametrů

| Příznak | Účel |
|------|---------|
| `-m` | Cesta k souboru modelu GGUF (použijte první část, `00001-of-00005`) |
| `-c` | Velikost kontextu v tokenech. Větší hodnoty využívají více paměti |
| `-fa on` | Povoluje rocWMMA Flash Attention pro lepší výkon na GPU AMD |
| `-ngl 999` | Přenese všechny vrstvy modelu na GPU |
| `--no-mmap` | Zakáže mapování paměti, čímž zkrátí dobu načítání, když velikost modelu překračuje systémovou RAM, ale vejde se do VRAM |
| `--host` | IP adresa, na které bude `llama-server` naslouchat (pouze `llama-server`) |
| `--port` | Port, na kterém bude servírováno HTTP API (pouze `llama-server`) |
| `--rpc` | Čárkami oddělený seznam koncových bodů RPC workerů (`IP:port`) |

Úplné použití parametrů naleznete v [dokumentaci llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) a [dokumentaci llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Další kroky

- **Připojení aplikací třetích stran**: `llama-server` zpřístupňuje API kompatibilní s OpenAI. Nasměrujte jakoukoli aplikaci kompatibilní s OpenAI (například Open WebUI) na `http://<HOST_IP>:8081` s libovolným zástupným klíčem API (např. `none`) pro připojení ke clusteru
- **Prozkoumejte další modely**: Procházejte kvantizované GGUFy na [Hugging Face](https://huggingface.co/models?search=gguf) a najděte modely, které se vejdou do kombinované GPU paměti vašeho clusteru
- **Škálování na čtyři uzly**: Přidejte další dva systémy Ryzen AI Halo jako dodatečné RPC workery pro přístup k modelům na úrovni 1 bilionu parametrů. Předejte další koncové body do `--rpc` jako čárkami oddělený seznam (např. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)