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

# Clustrovanie dvoch Ryzen™ AI Halo zariadení pomocou RPC

## Prehľad

Váš Ryzen™ AI Halo je už schopný lokálne spúšťať veľké jazykové modely. Clustrovanie posúva tieto možnosti ešte ďalej, pretože kombinuje pamäť GPU viacerých systémov cez lokálnu sieť, čím vám poskytuje prístup k ešte väčším modelom so silnejším uvažovaním, lepším generovaním kódu a hlbším viacjazyčným porozumením – a to všetko výhradne na vašom vlastnom hardvéri.

Táto príručka vás naučí, ako naclustrovať dva systémy Ryzen AI Halo pomocou RPC engine z llama.cpp a spustiť model GLM 4.7 s 358B parametrami naprieč oboma strojmi s akceleráciou AMD ROCm™.

## Čo sa naučíte

- Ako rozšíriť alokáciu VRAM na systémoch Ryzen AI Halo
- Inštaláciu llama.cpp s podporou ROCm a RPC
- Konfiguráciu RPC workera a spustenie distribuovanej inferencie naprieč dvoma uzlami
- Spustenie modelu so 358B parametrami naprieč dvoma sieťovo prepojenými systémami Ryzen AI Halo

## Nastavenie konfigurácie pamäte

> **Poznámka**: Tento krok vykonajte na Machine 1 aj Machine 2.

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Spúšťanie modelov s veľkosťou blízko alebo nad 128 GB:** Na systémoch AMD Ryzen™ AI Max 400 Series (Gorgon Halo) so systémom Windows vyžadujú modely, ktoré sa blížia k 128 GB pamäte alebo ju presahujú, dodatočnú konfiguráciu, aby fungovali bez chýb. Pred načítaním modelu postupujte podľa pokynov v dokumente [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines).
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Vo Windows, ak chcete spúšťať väčšie modely, ktoré vyžadujú viac pamäte, potrebujeme použiť alokáciu AMD Variable Graphics Memory (iGPU VRAM).

Toto je možné nastaviť otvorením ovládacieho panela AMD Software: Adrenalin Edition a prechodom na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavte hodnotu na **96 GB**. Aby sa zmeny prejavili, reštartujte systém.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V systéme Linux ROCm využíva zdieľaný pool systémovej pamäte, ktorý je štandardne nakonfigurovaný na polovicu systémovej pamäte.

Toto množstvo je možné zvýšiť zmenou nastavenia stránok Translation Table Manager (TTM) jadra podľa nasledujúcich pokynov. AMD odporúča nastaviť minimálnu vyhradenú VRAM v BIOSe (0,5 GB).

* Nainštalujte nástroj pipx a pridajte cestu pre pipx nainštalované wheely do systémovej vyhľadávacej cesty.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainštalujte wheel amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spustite nástroj amd-ttm na zistenie aktuálneho nastavenia zdieľanej pamäte.
  ```bash
  amd-ttm
  ```

* Rekonfigurujte nastavenia zdieľanej pamäte na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reštartujte systém, aby sa zmeny prejavili.


<!-- @os:end -->
<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

<!-- @require:software-update -->
<!-- @device:end -->
## Predpoklady

### Hardvér

Táto príručka vyžaduje dve jednotky Ryzen AI Halo a jeden ethernetový switch, zapojené v topológii hviezdy, pričom každá jednotka je priamo prepojená so switchom.

| Komponent | Množstvo | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočtové uzly tvoriace cluster |
| 10Gbps ethernetový switch | 1 | Centrálny switch umožňujúci komunikáciu viacerých uzlov Ryzen AI Halo (aspoň 2 porty) |
| Ethernetový kábel | 2 | Pripája každú jednotku Halo k switchu (odporúča sa Cat 7 alebo vyšší) |

> **Poznámka**: Na pripojenie dvoch jednotiek Ryzen AI Halo sú potrebné dva porty ethernetového switcha. Tretí port je potrebný, ak k modelu pristupujete zo samostatného klientskeho stroja namiesto jednej z jednotiek Halo.

### Softvér
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Nainštalujte:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) s pracovným zaťažením **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyzické nastavenie hardvéru

> **Poznámka**: Tento krok vykonajte na Machine 1 aj Machine 2.

Pripojte každú jednotku Ryzen AI Halo k ethernetovému switchu pomocou kábla Cat 7 (alebo vyššieho). Tým sa vytvorí 10Gbps spojenie používané na vysokorýchlostnú komunikáciu medzi uzlami.
<!-- @os:linux -->
### 1. Zistenie sieťových rozhraní

Na každom stroji nájdite názov jeho sieťového rozhrania a poznačte si ho (ďalej bude označovaný ako `IFNAME`). Spustite:

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

> **Poznámka**: Nahraďte `<IFNAME>` názvom výstupného rozhrania z [1. Zistenie sieťových rozhraní](#1-determine-network-interfaces)

Mali by ste vidieť rýchlosť `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10000Mb/s` alebo sa spojenie nenadviaže, skontrolujte pripojenie kábla a overte, že port switcha je nastavený na 10Gbps. Niektoré switche vyžadujú vypnutie automatického vyjednávania a manuálne nastavenie rýchlosti spojenia; postupujte podľa dokumentácie vášho switcha.

<!-- @os:end -->

<!-- @os:windows -->
### Overenie rýchlosti sieťového spojenia

Na každom stroji skontrolujte rýchlosť spojenia vašich sieťových rozhraní:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaše ethernetové rozhranie by malo byť `Up` a bežať na `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10 Gbps` alebo sa spojenie nenadviaže, skontrolujte pripojenie kábla a overte, že port switcha je nastavený na 10Gbps. Niektoré switche vyžadujú vypnutie automatického vyjednávania a manuálne nastavenie rýchlosti spojenia; postupujte podľa dokumentácie vášho switcha.

<!-- @os:end -->

## Inštalácia llama.cpp

> **Poznámka**: Tento krok vykonajte na Machine 1 aj Machine 2.

K dispozícii sú dve možnosti inštalácie:

- [Možnosť 1: Lemonade SDK (odporúčané)](#option-1-lemonade-sdk-recommended) - predpripravené binárne súbory, najrýchlejšie nastavenie
- [Možnosť 2: Manuálne zostavenie zo zdrojového kódu](#option-2-manual-source-build) - zostavenie zo zdrojového kódu s plnou kontrolou nad zostavovacími príznakmi
### Možnosť 1: Lemonade SDK (odporúčané)

Lemonade SDK poskytuje nočné (nightly) zostavenia llama.cpp s akceleráciou AMD ROCm 7, zamerané na GPU, ako je gfx1151 (Strix Halo / Ryzen AI Max+ 395), a ďalšie nedávne architektúry Radeon.

<!-- @os:windows -->
#### Krok 1: Stiahnutie predpripravených binárnych súborov

Prejdite na stránku s najnovším vydaním a stiahnite archív zodpovedajúci vašej platforme a cieľovému GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stiahnite súbor s názvom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo zostavenia).

#### Krok 2: Rozbalenie binárnych súborov

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

Prejdite na stránku s najnovším vydaním a stiahnite archív zodpovedajúci vašej platforme a cieľovému GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stiahnite súbor s názvom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo zostavenia).

#### Krok 2: Rozbalenie a príprava binárnych súborov

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
Po príprave llama.cpp na každom uzle pokračujte časťou [Sťahovanie modelu](#downloading-the-model).

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
| `-DGGML_HIP=ON` | Povolí softvérový stack ROCm/HIP |
| `-DGGML_RPC=ON` | Povolí RPC pre distribuovanú inferenciu |
| `-DGPU_TARGETS=gfx1151` | Zameria sa na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Použije zostavovací systém Ninja |

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

#### Krok 3: Pridanie HIP do používateľskej cesty

Vyššie uvedený krok zostavenia nastavil `%HIP_PATH%\bin` len pre aktuálnu reláciu. Aby boli knižnice HIP dostupné v akomkoľvek termináli (nielen v x64 Native Tools Command Prompt), pridajte ho natrvalo do svojej používateľskej premennej `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Po príprave llama.cpp na každom uzle pokračujte časťou [Sťahovanie modelu](#downloading-the-model).
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
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Príznak zostavenia | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povolí softvérový stack ROCm |
| `-DGGML_RPC=ON` | Povolí RPC pre distribuovanú inferenciu |
| `-DAMDGPU_TARGETS="gfx1151"` | Zameria sa na GPU Ryzen AI Halo (Radeon 8060s) |

Ďalšie možnosti zostavenia nájdete v [dokumentácii k zostavovaniu llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Po príprave llama.cpp na každom uzle pokračujte časťou [Sťahovanie modelu](#downloading-the-model).
<!-- @os:end -->

## Sťahovanie modelu

Táto príručka používa [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model so 358 miliardami parametrov v kvantizácii `Q4_K_XL` od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri tejto kvantizácii vyžaduje model približne 205 GB úložného priestoru a zmestí sa do kombinovanej pamäte GPU dvoch uzlov Ryzen AI Halo.

Stiahnite súbory GGUF pomocou rozhrania Hugging Face CLI:
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

> **Poznámka**: Stiahnutie modelu musí byť dokončené na stroji Machine 1 (ovládač). Pracovné uzly RPC nepotrebujú lokálnu kópiu súborov modelu.

## Spustenie modelu na klastri

Mechanizmus llama.cpp RPC (Remote Procedure Call) umožňuje jednej inštancii llama.cpp odovzdávať vrstvy modelu vzdialeným pracovným staniciam cez sieť. Jeden stroj funguje ako **ovládač** (Machine 1), ktorý zabezpečuje tokenizáciu, plánovanie a orchestráciu. Druhý stroj spúšťa odľahčený **RPC server** (Machine 2), ktorý sprístupňuje svoju pamäť GPU a výpočtový výkon ovládaču.

Pri načítaní rozdeľuje llama.cpp model medzi oba uzly. Po načítaní prebieha inferencia, akoby bežala na jednom akcelerátore. RPC zabezpečuje prenos tenzorov a synchronizáciu na pozadí.

### Krok 1: Spustenie RPC servera (Machine 2)

Na stroji Machine 2 spustite RPC server, aby sprístupnil svoje zdroje GPU ovládaču:
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
| `-c` | Povolí lokálnu vyrovnávaciu pamäť pre veľké tenzory, čím sa predíde opakovaným sieťovým prenosom počas načítavania modelu |
| `--host` | IP adresa, na ktorú sa má naviazať RPC server (`0.0.0.0` pre všetky rozhrania) |

Ďalšie možnosti nájdete v [dokumentácii k RPC pre llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Spustenie modelu (Machine 1)

Keď RPC server beží na stroji Machine 2, spustite inferenciu zo stroja Machine 1 pomocou buď `llama-cli`, alebo `llama-server`.
#### llama-cli

`llama-cli` poskytuje terminálové rozhranie na priamu interakciu s modelom. Je ideálny na benchmarking, ladenie a experimentovanie na nízkej úrovni.

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

> **Zistenie `<RPC_WORKER_IP>`**: Na Zariadení 2 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento príkaz spustite v termináli (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Zistenie `<RPC_WORKER_IP>`**: Na Zariadení 2 spustite `ipconfig | findstr /C:"IPv4"` v termináli (Powershell), aby ste zistili jeho lokálnu IP adresu.

<!-- @os:end -->

Po spustení `llama-cli` zobrazí priebeh načítavania modelu a vstúpi do interaktívneho promptu, kde môžete priamo chatovať s modelom:

![llama-cli spúšťajúci GLM 4.7 na dvoch uzloch](assets/llama-cli-example.png)

#### llama-server

`llama-server` sprístupňuje rovnaký inferenčný engine prostredníctvom trvalého serverového procesu s integrovaným webovým rozhraním a s OpenAI-kompatibilným HTTP API. Toto je preferované rozhranie pre dlhodobejšie nasadenia, prístup viacerých používateľov a integráciu s externými nástrojmi.

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

> **Zistenie `<RPC_WORKER_IP>`**: Na Zariadení 2 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento príkaz spustite v termináli (Powershell).

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

> **Zistenie `<RPC_WORKER_IP>`**: Na Zariadení 2 spustite `ipconfig | findstr /C:"IPv4"` v termináli (Powershell), aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

Po spustení otvorte `http://<HOST_IP>:8081` vo svojom prehliadači, aby ste získali prístup k vstavanému webovému rozhraniu. Toto poskytuje chatovacie rozhranie v prehliadači na interakciu s modelom:

![webové rozhranie llama-server spúšťajúce GLM 4.7 na dvoch uzloch](assets/llama-server-example.png)

<!-- @os:linux -->
> **Zistenie `<HOST_IP>`**: Na Zariadení 1 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Zistenie `<HOST_IP>`**: Na Zariadení 1 spustite `ipconfig | findstr /C:"IPv4"` v termináli (Powershell), aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

#### Referencia parametrov

| Príznak | Účel |
|------|---------|
| `-m` | Cesta k súboru modelu GGUF (použite prvý úlomok, `00001-of-00005`) |
| `-c` | Veľkosť kontextu v tokenoch. Vyššie hodnoty využívajú viac pamäte |
| `-fa on` | Zapína rocWMMA Flash Attention pre zlepšený výkon na AMD GPU |
| `-ngl 999` | Presunie všetky vrstvy modelu na GPU |
| `-lm none` | Nastaví režim načítania modelu na `none`, čím sa vypne memory-mapping na zníženie času načítania, keď je veľkosť modelu väčšia ako systémová RAM, ale zmestí sa do VRAM |
| `--host` | IP adresa, na ktorú sa má naviazať `llama-server` (iba `llama-server`) |
| `--port` | Port, na ktorom sa má poskytovať HTTP API (iba `llama-server`) |
| `--rpc` | Zoznam koncových bodov RPC pracovných uzlov oddelených čiarkami (`IP:port`) |

Úplné použitie parametrov nájdete v [dokumentácii k llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) a [dokumentácii k llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Ďalšie kroky

- **Pripojenie aplikácií tretích strán**: `llama-server` sprístupňuje OpenAI-kompatibilné API. Nasmerujte akúkoľvek OpenAI-kompatibilnú aplikáciu (napríklad Open WebUI) na `http://<HOST_IP>:8081` s akýmkoľvek zástupným API kľúčom (napr. `none`), aby ste sa pripojili k svojmu klastru
- **Preskúmanie ďalších modelov**: Prehliadajte kvantizované GGUF súbory na [Hugging Face](https://huggingface.co/models?search=gguf), aby ste našli modely, ktoré sa zmestia do kombinovanej pamäte GPU vášho klastra
- **Škálovanie na štyri uzly**: Pridajte ďalšie dva systémy Ryzen AI Halo ako ďalšie RPC pracovné uzly, aby ste získali prístup k modelom v mierke 1 bilión parametrov. Odovzdajte ďalšie koncové body do `--rpc` ako zoznam oddelený čiarkami (napr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)