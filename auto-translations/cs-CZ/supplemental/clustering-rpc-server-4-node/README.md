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

# Clustering čtyř Ryzen™ AI Halo pomocí RPC

## Přehled

Váš Ryzen™ AI Halo je již schopen spouštět velké jazykové modely lokálně. Clustering jde ještě dál – kombinuje paměť GPU napříč více systémy prostřednictvím lokální sítě a poskytuje vám přístup k ještě větším modelům se silnějším uvažováním, lepším generováním kódu a hlubším porozuměním více jazykům, a to zcela na vašem vlastním hardwaru.

Tento playbook vás naučí, jak vytvořit cluster ze čtyř systémů Ryzen AI Halo pomocí RPC enginu z llama.cpp a spustit Kimi K2.6, velký model typu mixture-of-experts, napříč všemi čtyřmi počítači s akcelerací AMD ROCm™.

## Co se naučíte

- Jak rozšířit alokaci VRAM na systémech Ryzen AI Halo
- Instalaci llama.cpp s podporou ROCm a RPC
- Konfiguraci RPC workerů a spuštění distribuované inference napříč čtyřmi uzly
- Spuštění modelu s 1T parametry napříč čtyřmi propojenými systémy Ryzen AI Halo

## Nastavení konfigurace paměti

> **Poznámka**: Tento krok proveďte na všech čtyřech počítačích (Počítač 1 až Počítač 4).

<!-- @os:windows -->
Ve Windows, abychom mohli spouštět větší modely vyžadující více paměti, potřebujeme použít alokaci AMD Variable Graphics Memory (iGPU VRAM).

To lze provést otevřením ovládacího panelu AMD Software: Adrenalin Edition a přechodem na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavte hodnotu na **96 GB**. Poté restartujte systém, aby se změny projevily.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V Linuxu využívá ROCm sdílený fond systémové paměti, který je ve výchozím nastavení nakonfigurován na polovinu systémové paměti.

Tuto hodnotu lze zvýšit změnou nastavení stránek Translation Table Manager (TTM) v jádře, a to podle následujících pokynů. AMD doporučuje nastavit minimální vyhrazenou VRAM v BIOSu (0,5 GB).

* Nainstalujte nástroj pipx a přidejte cestu k nainstalovaným wheel balíčkům pipx do systémové cesty pro vyhledávání.

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

* Přenastavte hodnoty sdílené paměti na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte systém, aby se změny projevily.


<!-- @os:end -->
<!-- @device:halo_box -->
## Zkontrolujte aktualizace softwaru

<!-- @require:software-update -->
<!-- @device:end -->
## Předpoklady

### Hardware

Tento playbook vyžaduje čtyři jednotky Ryzen AI Halo a jeden ethernetový switch, propojené v topologii hvězdy, přičemž každá jednotka je připojena přímo ke switchi.

| Komponenta | Množství | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Výpočetní uzly tvořící cluster |
| 10Gbps ethernetový switch | 1 | Centrální switch umožňující komunikaci více uzlů Ryzen AI Halo (alespoň 4 porty) |
| Ethernetový kabel | 4 | Připojuje každou jednotku Halo ke switchi (doporučen Cat 7 nebo vyšší) |

> **Poznámka**: Pro připojení čtyř jednotek Ryzen AI Halo jsou zapotřebí čtyři porty ethernetového switche. Pátý port je zapotřebí, pokud k modelu přistupujete z odděleného klientského počítače namísto z jedné z jednotek Halo.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Nainstalujte:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) se sadou nástrojů **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyzické nastavení hardwaru

> **Poznámka**: Tento krok proveďte na všech čtyřech počítačích (Počítač 1 až Počítač 4).

Připojte každou jednotku Ryzen AI Halo k ethernetovému switchi pomocí kabelu Cat 7 (nebo vyššího). Tím se vytvoří 10Gbps spojení používané pro vysokorychlostní komunikaci mezi uzly.
<!-- @os:linux -->
### 1. Zjištění síťových rozhraní

Na každém počítači zjistěte název jeho síťového rozhraní a poznamenejte si jej (dále bude označováno jako `IFNAME`). Spusťte:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tím se přímo vypíše název rozhraní, například:

```bash
enp191s0
```

### 2. Ověření rychlosti síťového spojení

Potvrďte, že je spojení aktivní a běží na plnou rychlost, kontrolou rychlosti vašeho rozhraní:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupním názvem rozhraní z kroku [1. Zjištění síťových rozhraní](#1-determine-network-interfaces)

Měli byste vidět rychlost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Pokud je rychlost nižší než `10000Mb/s` nebo se spojení nenaváže, zkontrolujte připojení kabelu a potvrďte, že je port switche nastaven na 10Gbps. Některé switche vyžadují vypnutí automatického vyjednávání a ruční nastavení rychlosti spojení; podrobnosti naleznete v dokumentaci vašeho switche.

<!-- @os:end -->

<!-- @os:windows -->
### Ověření rychlosti síťového spojení

Na každém počítači zkontrolujte rychlost spojení svých síťových rozhraní:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaše ethernetové rozhraní by mělo být `Up` a fungovat rychlostí `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Poznámka**: Pokud je rychlost nižší než `10 Gbps` nebo se spojení nenaváže, zkontrolujte připojení kabelu a potvrďte, že je port switche nastaven na 10Gbps. Některé switche vyžadují vypnutí automatického vyjednávání a ruční nastavení rychlosti spojení; podrobnosti naleznete v dokumentaci vašeho switche.

<!-- @os:end -->

## Instalace llama.cpp

> **Poznámka**: Tento krok proveďte na všech čtyřech počítačích (Počítač 1 až Počítač 4).

K dispozici jsou dvě možnosti instalace:

- [Možnost 1: Lemonade SDK (Doporučeno)](#option-1-lemonade-sdk-recommended) – předpřipravené binární soubory, nejrychlejší nastavení
- [Možnost 2: Ruční sestavení ze zdrojového kódu](#option-2-manual-source-build) – sestavení ze zdrojového kódu s plnou kontrolou nad příznaky sestavení

### Možnost 1: Lemonade SDK (Doporučeno)

Lemonade SDK poskytuje noční sestavení llama.cpp s akcelerací AMD ROCm 7, cílené na GPU jako gfx1151 (Strix Halo / Ryzen AI Max+ 395) a další novější architektury Radeon.

<!-- @os:windows -->
#### Krok 1: Stažení předem sestavených binárních souborů

Přejděte na stránku nejnovější verze a stáhněte archiv odpovídající vaší platformě a cílovému GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stáhněte soubor s názvem `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo sestavení).

#### Krok 2: Rozbalení binárních souborů

Rozbalte stažený archiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tento adresář nyní obsahuje sestavení `llama-cli.exe`, `llama-server.exe` a `ggml-rpc-server.exe` s podporou ROCm, předkompilovaná pro váš systém Ryzen AI Halo.

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
#### Krok 1: Stažení předem sestavených binárních souborů

Přejděte na stránku nejnovější verze a stáhněte archiv odpovídající vaší platformě a cílovému GPU:

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
Jakmile je llama.cpp připraveno na každém uzlu, pokračujte na [Stažení modelu](#downloading-the-model).

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

Výše uvedený krok sestavení nastavil `%HIP_PATH%\bin` pouze pro aktuální relaci. Aby byly knihovny HIP dostupné v jakémkoli terminálu (nejen v x64 Native Tools Command Prompt), přidejte ji trvale do uživatelské proměnné `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Jakmile je llama.cpp připraveno na každém uzlu, pokračujte na [Stažení modelu](#downloading-the-model).
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

| Přepínač sestavení | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povolí softwarový stack ROCm |
| `-DGGML_RPC=ON` | Povolí RPC pro distribuovanou inferenci |
| `-DAMDGPU_TARGETS="gfx1151"` | Cílí na GPU Ryzen AI Halo (Radeon 8060s) |

Další možnosti sestavení najdete v [dokumentaci k sestavení llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Jakmile je llama.cpp připraveno na každém uzlu, pokračujte na [Stažení modelu](#downloading-the-model).
<!-- @os:end -->

## Stažení modelu

Tato příručka používá [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) v kvantizaci `UD-Q2_K_XL` od [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Tato kvantizace se vejde do kombinované paměti GPU čtyř uzlů Ryzen AI Halo.

Stáhněte soubory GGUF pomocí rozhraní Hugging Face CLI:
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

> **Poznámka**: Stažení modelu musí být dokončeno na Machine 1 (řadiči). Uzly RPC pracovníků (Machine 2, 3 a 4) nepotřebují lokální kopii souborů modelu.

## Spuštění modelu na clusteru

Modul RPC (Remote Procedure Call) v llama.cpp umožňuje, aby jedna instance llama.cpp odesílala vrstvy modelu ke vzdáleným pracovníkům přes síť. Jeden počítač funguje jako **řadič** (Machine 1) a stará se o tokenizaci, plánování a orchestraci. Zbývající tři počítače spouštějí každý odlehčený **RPC server** (Machine 2, 3 a 4), který zpřístupňuje svou paměť GPU a výpočetní výkon řadiči.

Při načítání llama.cpp rozdělí model mezi všechny čtyři uzly. Po načtení probíhá inference, jako by běžela na jediném akcelerátoru. RPC se na pozadí stará o přenos tenzorů a synchronizaci.

### Krok 1: Spuštění RPC serverů (Machine 2, 3 a 4)

Na každém z počítačů Machine 2, 3 a 4 spusťte RPC server, aby zpřístupnil své prostředky GPU řadiči:
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
| `-p` | Port, na kterém je RPC server vysílán |
| `-c` | Povolí lokální mezipaměť pro velké tenzory, čímž se zabrání opakovaným síťovým přenosům během načítání modelu |
| `--host` | IP adresa, na kterou je RPC server navázán (`0.0.0.0` pro všechna rozhraní) |

Další možnosti najdete v [dokumentaci k RPC v llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Spuštění modelu (Machine 1)

Jakmile RPC servery běží na počítačích Machine 2, 3 a 4, spusťte inferenci z Machine 1 pomocí buď `llama-cli`, nebo `llama-server`.
#### llama-cli

`llama-cli` poskytuje terminálové rozhraní pro přímou interakci s modelem. Je ideální pro benchmarking, ladění a experimentování na nízké úrovni.

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

> **Zjištění `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na každém ze strojů 2, 3 a 4 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento příkaz spusťte v Terminálu (Powershell).

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

> **Zjištění `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na každém ze strojů 2, 3 a 4 spusťte `ipconfig | findstr /C:"IPv4"` v Terminálu (Powershell), abyste zjistili jeho lokální IP adresu.

<!-- @os:end -->

Po spuštění `llama-cli` zobrazí průběh načítání modelu a přejde do interaktivního promptu, kde můžete přímo komunikovat s modelem:

![llama-cli spuštěný s Kimi K2.6 na čtyřech uzlech](assets/llama-cli-example.png)

#### llama-server

`llama-server` zpřístupňuje stejný inferenční engine prostřednictvím trvalého serverového procesu s integrovaným webovým rozhraním a API kompatibilním s OpenAI. Toto je preferované rozhraní pro déletrvající nasazení, přístup více uživatelů a integraci s externími nástroji.

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

> **Zjištění `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na každém ze strojů 2, 3 a 4 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento příkaz spusťte v Terminálu (Powershell).

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

> **Zjištění `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na každém ze strojů 2, 3 a 4 spusťte `ipconfig | findstr /C:"IPv4"` v Terminálu (Powershell), abyste zjistili jeho lokální IP adresu.
<!-- @os:end -->

Po spuštění otevřete v prohlížeči `http://<HOST_IP>:8081`, abyste získali přístup ke vestavěnému webovému rozhraní. To poskytuje chatovací rozhraní v prohlížeči pro interakci s modelem:

![Webové rozhraní llama-server spuštěné s Kimi K2.6 na čtyřech uzlech](assets/llama-server-example.png)

<!-- @os:linux -->
> **Zjištění `<HOST_IP>`**: Na stroji 1 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Zjištění `<HOST_IP>`**: Na stroji 1 spusťte `ipconfig | findstr /C:"IPv4"` v Terminálu (Powershell), abyste zjistili jeho lokální IP adresu.
<!-- @os:end -->

#### Přehled parametrů

| Příznak | Účel |
|------|---------|
| `-m` | Cesta k souboru modelu GGUF (použijte první díl, `00001-of-00008`) |
| `-c` | Velikost kontextu v tokenech. Vyšší hodnoty využívají více paměti |
| `-fa on` | Povolí rocWMMA Flash Attention pro vyšší výkon na AMD GPU |
| `-ngl 999` | Přesune všechny vrstvy modelu na GPU |
| `-lm none` | Nastaví režim načítání modelu na `none`, čímž zakáže mapování paměti (memory-mapping) za účelem zkrácení doby načítání v případech, kdy velikost modelu přesahuje kapacitu systémové RAM, ale vejde se do VRAM |
| `-b` | Logická velikost dávky v tokenech. Nastavení na 4096 vyvažuje propustnost a využití paměti napříč uzly |
| `-ub` | Fyzická (mikro) velikost dávky pro zpracování promptu. Shoda s `-b` zamezuje zbytečné režii při dělení na části |
| `--host` | IP adresa, na kterou se má navázat `llama-server` (pouze `llama-server`) |
| `--port` | Port, na kterém se poskytuje HTTP API (pouze `llama-server`) |
| `--rpc` | Čárkami oddělený seznam koncových bodů RPC pracovníků (`IP:port`) |

Úplné informace o použití parametrů naleznete v [dokumentaci k llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) a [dokumentaci k llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Další kroky

- **Připojení aplikací třetích stran**: `llama-server` zpřístupňuje API kompatibilní s OpenAI. Nasměrujte jakoukoli aplikaci kompatibilní s OpenAI (například Open WebUI) na `http://<HOST_IP>:8081` s libovolným zástupným API klíčem (např. `none`), abyste se připojili ke svému clusteru
- **Objevování dalších modelů**: Procházejte kvantizované GGUF soubory na [Hugging Face](https://huggingface.co/models?search=gguf), abyste našli modely, které se vejdou do kombinované paměti GPU vašeho clusteru
- **Škálování nad rámec čtyř uzlů**: Přidejte další systémy Ryzen AI Halo jako další RPC pracovníky, abyste získali přístup k modelům přesahujícím škálu 1 bilionu parametrů. Předejte další koncové body parametru `--rpc` jako čárkami oddělený seznam (např. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)