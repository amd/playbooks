<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustrovanie dvoch Ryzen™ AI Halo systémov pomocou RPC

## Prehľad

Váš Ryzen™ AI Halo je už teraz schopný lokálne spúšťať veľké jazykové modely. Clustrovanie posúva túto schopnosť ešte ďalej tým, že kombinuje GPU pamäť viacerých systémov cez lokálnu sieť, čo vám umožní pracovať s ešte väčšími modelmi so silnejším uvažovaním, lepším generovaním kódu a hlbším viacjazyčným porozumením, a to úplne na vašom vlastnom hardvéri.

Táto príručka vás naučí, ako clustrovať dva systémy Ryzen AI Halo pomocou RPC engine z llama.cpp a ako spustiť GLM 4.7, model so 358 miliardami parametrov, naprieč oboma zariadeniami s akceleráciou AMD ROCm™.

## Čo sa naučíte

- Ako rozšíriť alokáciu VRAM na systémoch Ryzen AI Halo
- Inštaláciu llama.cpp s podporou ROCm a RPC
- Konfiguráciu RPC workera a spustenie distribuovanej inferencie naprieč dvomi uzlami
- Spustenie modelu so 358 miliardami parametrov naprieč dvomi prepojenými systémami Ryzen AI Halo

## Nastavenie konfigurácie pamäte

> **Poznámka**: Tento krok vykonajte na Machine 1 aj Machine 2.

<!-- @os:windows -->
Na systéme Windows, ak chcete spúšťať väčšie modely vyžadujúce vyššiu pamäť, musíme použiť alokáciu AMD Variable Graphics Memory (iGPU VRAM).

To sa dá vykonať otvorením ovládacieho panela AMD Software: Adrenalin Edition a prechodom do: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavte hodnotu na **96 GB**. Po zmene reštartujte systém, aby sa zmeny prejavili.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V systéme Linux ROCm využíva zdieľaný fond systémovej pamäte, ktorý je predvolene nakonfigurovaný na polovicu systémovej pamäte.

Toto množstvo je možné zvýšiť zmenou nastavenia stránok Translation Table Manager (TTM) v jadre podľa nasledujúcich pokynov. AMD odporúča nastaviť minimálnu vyhradenú VRAM v BIOSe (0,5 GB).

* Nainštalujte nástroj pipx a pridajte cestu k balíčkom nainštalovaným cez pipx do vyhľadávacej cesty systému.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainštalujte balík amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spustite nástroj amd-ttm na zistenie aktuálnych nastavení zdieľanej pamäte.
  ```bash
  amd-ttm
  ```

* Zmeňte nastavenia zdieľanej pamäte na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reštartujte systém, aby sa zmeny prejavili.


<!-- @os:end -->
<!-- @device:halo_box -->
## Skontrolujte aktualizácie softvéru

<!-- @require:software-update -->
<!-- @device:end -->
## Predpoklady

### Hardvér

Táto príručka vyžaduje dve jednotky Ryzen AI Halo a jeden Ethernet switch, zapojené v hviezdicovej topológii, pričom každá jednotka je priamo pripojená k switchu.

| Komponent | Množstvo | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočtové uzly tvoriace cluster |
| 10Gbps Ethernet switch | 1 | Centrálny switch umožňujúci komunikáciu viacerých uzlov Ryzen AI Halo (aspoň 2 porty) |
| Ethernet kábel | 2 | Pripája každú jednotku Halo k switchu (odporúča sa Cat 7 alebo vyšší) |

> **Poznámka**: Na pripojenie dvoch jednotiek Ryzen AI Halo sú potrebné dva porty Ethernet switchu. Tretí port je potrebný, ak k modelu pristupujete zo samostatného klientskeho zariadenia namiesto jednej z jednotiek Halo.

### Softvér
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Nainštalujte:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) so súčasťou **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyzické nastavenie hardvéru

> **Poznámka**: Tento krok vykonajte na Machine 1 aj Machine 2.

Pripojte každú jednotku Ryzen AI Halo k Ethernet switchu pomocou kábla Cat 7 (alebo vyššieho). Tým sa vytvorí 10Gbps spojenie použité pre vysokorýchlostnú komunikáciu medzi uzlami.
<!-- @os:linux -->
### 1. Zistenie sieťových rozhraní

Na každom zariadení zistite názov jeho sieťového rozhrania a poznačte si ho (ďalej bude uvedený ako `IFNAME`). Spustite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Toto priamo vypíše názov rozhrania, napríklad:

```bash
enp191s0
```

### 2. Overenie rýchlosti sieťového spojenia

Overte, že spojenie je aktívne a beží na plnej rýchlosti, kontrolou rýchlosti vášho rozhrania:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupným názvom rozhrania z časti [1. Zistenie sieťových rozhraní](#1-determine-network-interfaces)

Mali by ste vidieť rýchlosť `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10000Mb/s` alebo sa spojenie nenadviaže, skontrolujte pripojenie kábla a overte, že port switchu je nastavený na 10Gbps. Niektoré switche vyžadujú zakázanie automatického vyjednávania a manuálne nastavenie rýchlosti spojenia; postupujte podľa dokumentácie vášho switchu.

<!-- @os:end -->

<!-- @os:windows -->
### Overenie rýchlosti sieťového spojenia

Na každom zariadení skontrolujte rýchlosť spojenia vašich sieťových rozhraní:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaše Ethernet rozhranie by malo byť `Up` a bežať na `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10 Gbps` alebo sa spojenie nenadviaže, skontrolujte pripojenie kábla a overte, že port switchu je nastavený na 10Gbps. Niektoré switche vyžadujú zakázanie automatického vyjednávania a manuálne nastavenie rýchlosti spojenia; postupujte podľa dokumentácie vášho switchu.

<!-- @os:end -->

## Inštalácia llama.cpp

> **Poznámka**: Tento krok vykonajte na Machine 1 aj Machine 2.

K dispozícii sú dve možnosti inštalácie:

- [Možnosť 1: Lemonade SDK (odporúčané)](#option-1-lemonade-sdk-recommended) - vopred zostavené binárne súbory, najrýchlejšie nastavenie
- [Možnosť 2: Manuálne zostavenie zo zdrojového kódu](#option-2-manual-source-build) - zostavenie zo zdrojového kódu s plnou kontrolou nad zostavovacími príznakmi

### Možnosť 1: Lemonade SDK (odporúčané)

Lemonade SDK poskytuje nočné zostavenia (nightly builds) llama.cpp s akceleráciou AMD ROCm 7, cielené na GPU ako gfx1151 (Strix Halo / Ryzen AI Max+ 395) a ďalšie novšie architektúry Radeon.

<!-- @os:windows -->
#### Krok 1: Stiahnutie predpripravených binárnych súborov

Prejdite na stránku najnovšieho vydania a stiahnite si archív zodpovedajúci vašej platforme a cieľovej GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stiahnite súbor s názvom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo zostavenia).

#### Krok 2: Extrahovanie binárnych súborov

Rozbaľte stiahnutý archív:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tento adresár teraz obsahuje zostavenia `llama-cli.exe`, `llama-server.exe` a `rpc-server.exe` s podporou ROCm, prekompilované pre váš systém Ryzen AI Halo.

#### Krok 3: Overenie detekcie GPU

```bash
.\llama-cli.exe --list-devices
```

Očakávaný výstup:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Krok 1: Stiahnutie predpripravených binárnych súborov

Prejdite na stránku najnovšieho vydania a stiahnite si archív zodpovedajúci vašej platforme a cieľovej GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stiahnite súbor s názvom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo zostavenia).

#### Krok 2: Extrahovanie a príprava binárnych súborov

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Tento adresár teraz obsahuje zostavenia `llama-cli`, `llama-server` a `rpc-server` s podporou ROCm, prekompilované pre váš systém Ryzen AI Halo.

#### Krok 3: Overenie detekcie GPU

```bash
./llama-cli --list-devices
```

Očakávaný výstup:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Po pripravení llama.cpp na každom uzle pokračujte na [Stiahnutie modelu](#downloading-the-model).

### Možnosť 2: Manuálne zostavenie zo zdrojového kódu

<!-- @os:windows -->
#### Krok 1: Zostavenie llama.cpp

Otvorte **x64 Native Tools Command Prompt** (nainštalovaný spolu s Visual Studio Build Tools) a naklonujte repozitár:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Pridajte HIP do svojej cesty a zostavte s podporou ROCm a RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Príznak zostavenia | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povoľuje softvérový stack ROCm/HIP |
| `-DGGML_RPC=ON` | Povoľuje RPC pre distribuovanú inferenciu |
| `-DGPU_TARGETS=gfx1151` | Cieli na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Používa systém zostavenia Ninja |

#### Krok 2: Overenie detekcie GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Očakávaný výstup:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Krok 3: Pridanie HIP do vašej používateľskej cesty

Vyššie uvedený krok zostavenia nastavil `%HIP_PATH%\bin` iba pre aktuálnu reláciu. Aby boli knižnice HIP dostupné v ľubovoľnom termináli (nielen v x64 Native Tools Command Prompt), pridajte ho trvalo do svojej používateľskej premennej `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Po pripravení llama.cpp na každom uzle pokračujte na [Stiahnutie modelu](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Krok 1: Zostavenie llama.cpp

Naklonujte repozitár:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Zostavte s podporou ROCm a RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Príznak zostavenia | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povoľuje softvérový stack ROCm |
| `-DGGML_RPC=ON` | Povoľuje RPC pre distribuovanú inferenciu |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Povoľuje rocWMMA pre vylepšenú Flash Attention na AMD GPU |
| `-DAMDGPU_TARGETS="gfx1151"` | Cieli na GPU Ryzen AI Halo (Radeon 8060s) |

Ďalšie možnosti zostavenia nájdete v [dokumentácii k zostaveniu llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Krok 2: Overenie detekcie GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Očakávaný výstup:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Po pripravení llama.cpp na každom uzle pokračujte na [Stiahnutie modelu](#downloading-the-model).
<!-- @os:end -->

## Stiahnutie modelu

Tento návod používa [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model so 358B parametrami v kvantizácii `Q4_K_XL` od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri tejto kvantizácii vyžaduje model približne 205 GB úložného priestoru a zmestí sa do kombinovanej pamäte GPU dvoch uzlov Ryzen AI Halo.

Stiahnite súbory GGUF pomocou Hugging Face CLI:
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

> **Poznámka**: Stiahnutie modelu musí byť dokončené na počítači 1 (kontrolér). Uzly RPC worker nepotrebujú lokálnu kópiu súborov modelu.

## Spustenie modelu v klastri

Modul RPC (Remote Procedure Call) v llama.cpp umožňuje jednej inštancii llama.cpp odovzdávať vrstvy modelu vzdialeným pracovným uzlom cez sieť. Jeden počítač funguje ako **kontrolér** (počítač 1), pričom zabezpečuje tokenizáciu, plánovanie a orchestráciu. Druhý počítač spúšťa odľahčený **RPC server** (počítač 2), ktorý sprístupňuje svoju pamäť GPU a výpočtový výkon kontroléru.

Pri načítaní llama.cpp rozdelí model medzi oba uzly. Po načítaní prebieha inferencia, akoby bežala na jedinom akcelerátore. RPC na pozadí zabezpečuje prenosy tenzorov a synchronizáciu.

### Krok 1: Spustenie RPC servera (počítač 2)

Na počítači 2 spustite RPC server, ktorý sprístupní jeho zdroje GPU kontroléru:
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

| Príznak | Účel |
|------|---------|
| `-p` | Port, na ktorom sa vysiela RPC server |
| `-c` | Povoľuje lokálnu vyrovnávaciu pamäť pre veľké tenzory, čím sa zabráni opakovaným sieťovým prenosom počas načítavania modelu |
| `--host` | IP adresa, na ktorú sa má naviazať RPC server (`0.0.0.0` pre všetky rozhrania) |

Ďalšie možnosti nájdete v [dokumentácii k RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Spustenie modelu (počítač 1)

Keď RPC server beží na počítači 2, spustite inferenciu z počítača 1 pomocou `llama-cli` alebo `llama-server`.

#### llama-cli

`llama-cli` poskytuje terminálové rozhranie na priamu interakciu s modelom. Je ideálny na benchmarking, ladenie a experimentovanie na nízkej úrovni.

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

> **Zistenie `<RPC_WORKER_IP>`**: Na počítači 2 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Spustite tento príkaz v termináli (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Zistenie `<RPC_WORKER_IP>`**: Na počítači 2 spustite `ipconfig | findstr /C:"IPv4"` v termináli (Powershell), aby ste zistili jeho lokálnu IP adresu.

<!-- @os:end -->

Po spustení `llama-cli` zobrazuje priebeh načítavania modelu a prejde do interaktívneho promptu, kde môžete priamo komunikovať s modelom formou chatu:

![llama-cli spúšťajúci GLM 4.7 naprieč dvoma uzlami](assets/llama-cli-example.png)
#### llama-server

`llama-server` sprístupňuje ten istý inferenčný engine prostredníctvom trvalého serverového procesu s integrovaným webovým rozhraním a HTTP API kompatibilným s OpenAI. Toto je preferované rozhranie pre dlhodobejšie nasadenia, prístup viacerých používateľov a integráciu s externými nástrojmi.

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

> **Nájdenie `<RPC_WORKER_IP>`**: Na počítači 2 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento príkaz spustite v Termináli (Powershell).

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

> **Nájdenie `<RPC_WORKER_IP>`**: Na počítači 2 spustite `ipconfig | findstr /C:"IPv4"` v Termináli (Powershell), aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

Po spustení otvorte v prehliadači `http://<HOST_IP>:8081`, aby ste získali prístup k vstavanému webovému rozhraniu. Toto poskytuje chatovacie rozhranie v prehliadači na interakciu s modelom:

![Webové rozhranie llama-server so spusteným GLM 4.7 na dvoch uzloch](assets/llama-server-example.png)

<!-- @os:linux -->
> **Nájdenie `<HOST_IP>`**: Na počítači 1 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Nájdenie `<HOST_IP>`**: Na počítači 1 spustite `ipconfig | findstr /C:"IPv4"` v Termináli (Powershell), aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

#### Prehľad parametrov

| Príznak | Účel |
|------|---------|
| `-m` | Cesta k súboru modelu GGUF (použite prvý fragment, `00001-of-00005`) |
| `-c` | Veľkosť kontextu v tokenoch. Väčšie hodnoty využívajú viac pamäte |
| `-fa on` | Zapína rocWMMA Flash Attention pre zlepšený výkon na GPU AMD |
| `-ngl 999` | Presunie všetky vrstvy modelu na GPU |
| `--no-mmap` | Vypne mapovanie pamäte, čo skracuje časy načítania, keď veľkosť modelu presahuje systémovú pamäť RAM, ale zmestí sa do VRAM |
| `--host` | IP adresa, na ktorú sa má naviazať `llama-server` (iba `llama-server`) |
| `--port` | Port, na ktorom sa poskytuje HTTP API (iba `llama-server`) |
| `--rpc` | Zoznam koncových bodov RPC pracovníkov oddelených čiarkou (`IP:port`) |

Úplné použitie parametrov nájdete v dokumentácii [llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) a v dokumentácii [llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Ďalšie kroky

- **Pripojenie aplikácií tretích strán**: `llama-server` sprístupňuje API kompatibilné s OpenAI. Nasmerujte akúkoľvek aplikáciu kompatibilnú s OpenAI (napríklad Open WebUI) na adresu `http://<HOST_IP>:8081` so zástupným API kľúčom (napr. `none`), aby ste sa pripojili k vášmu klastru
- **Preskúmanie ďalších modelov**: Prehliadajte kvantizované súbory GGUF na [Hugging Face](https://huggingface.co/models?search=gguf) a nájdite modely, ktoré sa zmestia do kombinovanej pamäte GPU vášho klastra
- **Škálovanie na štyri uzly**: Pridajte ďalšie dva systémy Ryzen AI Halo ako dodatočných RPC pracovníkov, aby ste získali prístup k modelom v rozsahu 1 bilióna parametrov. Odovzdajte ďalšie koncové body parametru `--rpc` ako zoznam oddelený čiarkou (napr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)