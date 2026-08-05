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

# Clustrování dvou systémů Ryzen™ AI Halo pomocí RPC

## Přehled

Váš systém Ryzen™ AI Halo je již schopen lokálně spouštět velké jazykové modely. Clustrování jde ještě dál – kombinuje paměť GPU více systémů přes lokální síť, čímž vám dává přístup k ještě větším modelům se silnějším uvažováním, lepší generací kódu a hlubším porozuměním více jazykům, a to vše zcela na vašem vlastním hardwaru.

Tato příručka vás naučí, jak sestavit cluster ze dvou systémů Ryzen AI Halo pomocí RPC enginu nástroje llama.cpp a spustit model GLM 4.7 s 358 miliardami parametrů na obou strojích s akcelerací AMD ROCm™.

## Co se naučíte

- Jak rozšířit alokaci VRAM na systémech Ryzen AI Halo
- Instalaci nástroje llama.cpp s podporou ROCm a RPC
- Konfiguraci RPC workeru a spuštění distribuované inference napříč dvěma uzly
- Spuštění modelu s 358 miliardami parametrů na dvou propojených systémech Ryzen AI Halo v síti

## Nastavení konfigurace paměti

> **Poznámka**: Tento krok proveďte na obou strojích – Machine 1 i Machine 2.

<!-- @os:windows -->
Ve Windows, chcete-li spouštět větší modely vyžadující více paměti, je potřeba použít alokaci AMD Variable Graphics Memory (VRAM pro iGPU).

Toho lze dosáhnout otevřením ovládacího panelu AMD Software: Adrenalin Edition a přechodem na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavte hodnotu na **96 GB**. Aby se změny projevily, restartujte prosím systém.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V Linuxu ROCm využívá sdílenou fond systémové paměti, který je ve výchozím nastavení nakonfigurován na polovinu velikosti systémové paměti.

Toto množství lze zvýšit změnou nastavení stránek Translation Table Manager (TTM) v jádře podle následujících pokynů. AMD doporučuje v BIOSu nastavit minimální vyhrazenou VRAM (0,5 GB).

* Nainstalujte nástroj pipx a přidejte cestu k balíčkům (wheels) nainstalovaným pomocí pipx do systémové vyhledávací cesty.

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

* Znovu nakonfigurujte nastavení sdílené paměti na **120 GB**:
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
| 10Gb ethernetový přepínač | 1 | Centrální přepínač umožňující komunikaci mezi více uzly Ryzen AI Halo (alespoň 2 porty) |
| Ethernetový kabel | 2 | Připojuje každou jednotku Halo k přepínači (doporučen Cat 7 nebo vyšší) |

> **Poznámka**: K připojení obou jednotek Ryzen AI Halo jsou potřeba dva porty ethernetového přepínače. Třetí port je potřeba, pokud k modelu přistupujete ze samostatného klientského stroje namísto z jedné z jednotek Halo.

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

## Fyzická instalace hardwaru

> **Poznámka**: Tento krok proveďte na obou strojích – Machine 1 i Machine 2.

Připojte každou jednotku Ryzen AI Halo k ethernetovému přepínači pomocí kabelu Cat 7 (nebo vyššího). Tím se vytvoří 10Gb spoj používaný pro vysokorychlostní komunikaci mezi uzly.
<!-- @os:linux -->
### 1. Zjištění síťových rozhraní

Na každém stroji zjistěte název jeho síťového rozhraní a poznamenejte si ho (dále bude uváděn jako `IFNAME`). Spusťte:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Toto vypíše přímo název rozhraní, například:

```bash
enp191s0
```

### 2. Ověření rychlosti síťového spoje

Potvrďte, že je spoj aktivní a běží plnou rychlostí, kontrolou rychlosti vašeho rozhraní:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupním názvem rozhraní z kroku [1. Zjištění síťových rozhraní](#1-determine-network-interfaces)

Měli byste vidět rychlost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Pokud je rychlost nižší než `10000Mb/s` nebo se spoj nenaváže, zkontrolujte zapojení kabelu a ověřte, že je port přepínače nastaven na 10 Gb/s. Některé přepínače vyžadují vypnutí automatické negociace a ruční nastavení rychlosti spoje; podrobnosti naleznete v dokumentaci vašeho přepínače.

<!-- @os:end -->

<!-- @os:windows -->
### Ověření rychlosti síťového spoje

Na každém stroji zkontrolujte rychlost spoje vašich síťových rozhraní:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaše ethernetové rozhraní by mělo být `Up` a běžet rychlostí `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Poznámka**: Pokud je rychlost nižší než `10 Gbps` nebo se spoj nenaváže, zkontrolujte zapojení kabelu a ověřte, že je port přepínače nastaven na 10 Gb/s. Některé přepínače vyžadují vypnutí automatické negociace a ruční nastavení rychlosti spoje; podrobnosti naleznete v dokumentaci vašeho přepínače.

<!-- @os:end -->

## Instalace llama.cpp

> **Poznámka**: Tento krok proveďte na obou strojích – Machine 1 i Machine 2.

K dispozici jsou dvě možnosti instalace:

- [Možnost 1: Lemonade SDK (doporučeno)](#option-1-lemonade-sdk-recommended) – předkompilované binární soubory, nejrychlejší nastavení
- [Možnost 2: Ruční sestavení ze zdrojového kódu](#option-2-manual-source-build) – sestavení ze zdrojového kódu s plnou kontrolou nad příznaky sestavení

### Možnost 1: Lemonade SDK (doporučeno)

Lemonade SDK poskytuje noční sestavení nástroje llama.cpp s akcelerací AMD ROCm 7, cílené na GPU jako gfx1151 (Strix Halo / Ryzen AI Max+ 395) a další nedávné architektury Radeon.

<!-- @os:windows -->
#### Krok 1: Stažení předsestavených binárních souborů

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
#### Krok 1: Stažení předsestavených binárních souborů

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
Jakmile je llama.cpp připraven na každém uzlu, pokračujte na [Stažení modelu](#downloading-the-model).

### Možnost 2: Ruční sestavení ze zdrojového kódu

<!-- @os:windows -->
#### Krok 1: Sestavení llama.cpp

Otevřete **x64 Native Tools Command Prompt** (nainstalovaný spolu s Visual Studio Build Tools) a naklonujte repozitář:

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

| Přepínač sestavení | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povolí softwarový stack ROCm/HIP |
| `-DGGML_RPC=ON` | Povolí RPC pro distribuovanou inferenci |
| `-DGPU_TARGETS=gfx1151` | Cílí na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Použije systém sestavení Ninja |

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

Výše uvedený krok sestavení nastavil `%HIP_PATH%\bin` pouze pro aktuální relaci. Aby byly knihovny HIP dostupné v libovolném terminálu (nejen v x64 Native Tools Command Prompt), přidejte je trvale do uživatelské proměnné `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Jakmile je llama.cpp připraven na každém uzlu, pokračujte na [Stažení modelu](#downloading-the-model).
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

| Přepínač sestavení | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povolí softwarový stack ROCm |
| `-DGGML_RPC=ON` | Povolí RPC pro distribuovanou inferenci |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Povolí rocWMMA pro vylepšenou funkci Flash Attention na GPU AMD |
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

Jakmile je llama.cpp připraven na každém uzlu, pokračujte na [Stažení modelu](#downloading-the-model).
<!-- @os:end -->

## Stažení modelu

Tento návod používá [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model s 358B parametry v kvantizaci `Q4_K_XL` od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Při této kvantizaci vyžaduje model přibližně 205 GB úložného prostoru a vejde se do kombinované paměti GPU dvou uzlů Ryzen AI Halo.

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

> **Poznámka**: Stažení modelu musí být dokončeno na počítači 1 (řadiči). Uzly RPC pracovníka nepotřebují lokální kopii souborů modelu.

## Spuštění modelu na clusteru

Modul llama.cpp RPC (Remote Procedure Call) umožňuje jediné instanci llama.cpp odsunout vrstvy modelu na vzdálené pracovní uzly přes síť. Jeden počítač funguje jako **řadič** (počítač 1) a zajišťuje tokenizaci, plánování a orchestraci. Druhý počítač spouští lehký **RPC server** (počítač 2), který zpřístupňuje svou paměť GPU a výpočetní výkon řadiči.

Při načítání llama.cpp rozdělí model mezi oba uzly. Po načtení probíhá inference, jako by běžela na jediném akcelerátoru. RPC v pozadí zajišťuje přenosy tenzorů a synchronizaci.

### Krok 1: Spuštění RPC serveru (počítač 2)

Na počítači 2 spusťte RPC server, aby zpřístupnil své zdroje GPU řadiči:
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

| Přepínač | Účel |
|------|---------|
| `-p` | Port, na kterém se bude vysílat RPC server |
| `-c` | Povolí lokální mezipaměť pro velké tenzory, čímž se zabrání opakovaným síťovým přenosům během načítání modelu |
| `--host` | IP adresa, na kterou se má RPC server navázat (`0.0.0.0` pro všechna rozhraní) |

Další možnosti naleznete v [dokumentaci k RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Spuštění modelu (počítač 1)

Se spuštěným RPC serverem na počítači 2 spusťte inferenci z počítače 1 pomocí buď `llama-cli`, nebo `llama-server`.

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

> **Zjištění `<RPC_WORKER_IP>`**: Na počítači 2 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu.
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

> **Zjištění `<RPC_WORKER_IP>`**: Na počítači 2 spusťte `ipconfig | findstr /C:"IPv4"` v terminálu (Powershell), abyste zjistili jeho lokální IP adresu.

<!-- @os:end -->

Po spuštění zobrazuje `llama-cli` průběh načítání modelu a otevře interaktivní výzvu, kde můžete přímo komunikovat s modelem:

![llama-cli spouštějící GLM 4.7 na dvou uzlech](assets/llama-cli-example.png)
#### llama-server

`llama-server` zpřístupňuje stejný inferenční engine prostřednictvím trvalého serverového procesu s integrovaným webovým rozhraním a HTTP API kompatibilním s OpenAI. Toto je preferované rozhraní pro dlouhodobě běžící nasazení, přístup více uživatelů a integraci s externími nástroji.

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

> **Zjištění `<RPC_WORKER_IP>`**: Na Strojí 2 spusťte `hostname -I | awk '{print $1}'`, čímž zjistíte jeho lokální IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento příkaz spusťte v Terminálu (Powershell).

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

> **Zjištění `<RPC_WORKER_IP>`**: Na Strojí 2 spusťte `ipconfig | findstr /C:"IPv4"` v Terminálu (Powershell), čímž zjistíte jeho lokální IP adresu.
<!-- @os:end -->

Po spuštění otevřete v prohlížeči adresu `http://<HOST_IP>:8081`, čímž získáte přístup k integrovanému webovému rozhraní. To poskytuje chatovací rozhraní v prohlížeči pro interakci s modelem:

![Webové rozhraní llama-server běžící s GLM 4.7 na dvou uzlech](assets/llama-server-example.png)

<!-- @os:linux -->
> **Zjištění `<HOST_IP>`**: Na Strojí 1 spusťte `hostname -I | awk '{print $1}'`, čímž zjistíte jeho lokální IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Zjištění `<HOST_IP>`**: Na Strojí 1 spusťte `ipconfig | findstr /C:"IPv4"` v Terminálu (Powershell), čímž zjistíte jeho lokální IP adresu.
<!-- @os:end -->

#### Přehled parametrů

| Přepínač | Účel |
|------|---------|
| `-m` | Cesta k souboru modelu GGUF (použijte první díl, `00001-of-00005`) |
| `-c` | Velikost kontextu v tokenech. Vyšší hodnoty spotřebují více paměti |
| `-fa on` | Zapíná rocWMMA Flash Attention pro zlepšený výkon na GPU AMD |
| `-ngl 999` | Přesune všechny vrstvy modelu na GPU |
| `--no-mmap` | Vypíná mapování paměti, což zkracuje dobu načítání, pokud velikost modelu přesahuje systémovou RAM, ale vejde se do VRAM |
| `--host` | IP adresa, na kterou se má `llama-server` navázat (pouze pro `llama-server`) |
| `--port` | Port, na kterém se má poskytovat HTTP API (pouze pro `llama-server`) |
| `--rpc` | Seznam koncových bodů RPC pracovníků oddělených čárkami (`IP:port`) |

Úplný popis parametrů naleznete v dokumentaci [llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) a v dokumentaci [llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Další kroky

- **Připojení aplikací třetích stran**: `llama-server` zpřístupňuje API kompatibilní s OpenAI. Nasměrujte libovolnou aplikaci kompatibilní s OpenAI (například Open WebUI) na adresu `http://<HOST_IP>:8081` s libovolným zástupným API klíčem (např. `none`), čímž se připojíte ke svému clusteru
- **Prozkoumání dalších modelů**: Procházejte kvantizované GGUF soubory na [Hugging Face](https://huggingface.co/models?search=gguf) a najděte modely, které se vejdou do kombinované paměti GPU vašeho clusteru
- **Škálování na čtyři uzly**: Přidejte další dva systémy Ryzen AI Halo jako další RPC pracovníky pro přístup k modelům v řádu 1 bilionu parametrů. Předejte další koncové body přepínači `--rpc` jako seznam oddělený čárkami (např. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)