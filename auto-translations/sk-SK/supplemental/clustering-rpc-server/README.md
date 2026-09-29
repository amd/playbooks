<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Zhlukovanie dvoch Ryzen™ AI Halo systémov pomocou RPC

## Prehľad

Váš Ryzen™ AI Halo je už schopný lokálne spúšťať veľké jazykové modely. Zhlukovanie posúva túto schopnosť ešte ďalej, spojením GPU pamäte viacerých systémov cez lokálnu sieť, čo vám umožní prístup k ešte väčším modelom so silnejším uvažovaním, lepším generovaním kódu a hlbším viacjazyčným porozumením, a to všetko úplne na vašom vlastnom hardvéri.

Tento návod vás naučí, ako zhlukovať dva systémy Ryzen AI Halo pomocou RPC engine z llama.cpp a spustiť GLM 4.7, model s 358 miliardami parametrov, na oboch strojoch s akceleráciou AMD ROCm™.

## Čo sa naučíte

- Ako rozšíriť alokáciu VRAM na systémoch Ryzen AI Halo
- Inštaláciu llama.cpp s podporou ROCm a RPC
- Konfiguráciu RPC workera a spustenie distribuovanej inferencie naprieč dvoma uzlami
- Spustenie modelu so 358 miliardami parametrov naprieč dvoma prepojenými systémami Ryzen AI Halo

## Nastavenie konfigurácie pamäte

> **Poznámka**: Tento krok dokončite na Zariadení 1 aj Zariadení 2.

<!-- @os:windows -->
Na Windows, pre spúšťanie väčších modelov, ktoré vyžadujú vyššiu pamäť, potrebujeme použiť alokáciu AMD Variable Graphics Memory (iGPU VRAM).

To sa dá vykonať otvorením ovládacieho panela AMD Software: Adrenalin Edition a prechodom na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavte hodnotu na **96 GB**. Reštartujte systém, aby sa zmeny prejavili.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Na Linuxe ROCm využíva zdieľaný fond systémovej pamäte a tento fond je štandardne nastavený na polovicu systémovej pamäte.

Túto hodnotu je možné zvýšiť zmenou nastavenia Translation Table Manager (TTM) stránok jadra podľa nasledujúcich pokynov. AMD odporúča nastaviť minimálnu vyhradenú VRAM v BIOSe (0,5 GB).

* Nainštalujte nástroj pipx a pridajte cestu k inštaláciám pipx wheels do vyhľadávacej cesty systému.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainštalujte wheel amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spustite nástroj amd-ttm na zistenie aktuálnych nastavení zdieľanej pamäte.
  ```bash
  amd-ttm
  ```

* Prekonfigurujte nastavenia zdieľanej pamäte na **120 GB**:
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

Tento návod vyžaduje dve jednotky Ryzen AI Halo a jeden Ethernet switch, zapojené v topológii hviezdy, pričom každá jednotka je priamo pripojená k switchu.

| Komponent | Množstvo | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočtové uzly tvoriace klaster |
| 10Gbps Ethernet switch | 1 | Centrálny switch umožňujúci komunikáciu viacerých uzlov Ryzen AI Halo (aspoň 2 porty) |
| Ethernet kábel | 2 | Pripája každú jednotku Halo k switchu (odporúčaný Cat 7 alebo vyšší) |

> **Poznámka**: Na pripojenie dvoch jednotiek Ryzen AI Halo sú potrebné dva porty Ethernet switchu. Tretí port je potrebný, ak k modelu pristupujete zo samostatného klientskeho stroja namiesto jednej z jednotiek Halo.

### Softvér
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Nainštalujte, prosím:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) so záťažou **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Nastavenie fyzického hardvéru

> **Poznámka**: Tento krok dokončite na Zariadení 1 aj Zariadení 2.

Pripojte každú jednotku Ryzen AI Halo k Ethernet switchu pomocou kábla Cat 7 (alebo vyššieho). Tým sa vytvorí 10Gbps spojenie použité na vysokorýchlostnú komunikáciu medzi uzlami.
<!-- @os:linux -->
### 1. Zistenie sieťových rozhraní

Na každom stroji zistite názov jeho sieťového rozhrania a poznamenajte si ho (ďalej bude uvádzaný ako `IFNAME`). Spustite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Toto priamo vypíše názov rozhrania, napríklad:

```bash
enp191s0
```

### 2. Overenie rýchlosti sieťového spojenia

Potvrďte, že spojenie je aktívne a beží plnou rýchlosťou, kontrolou rýchlosti vášho rozhrania:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupným názvom rozhrania z časti [1. Zistenie sieťových rozhraní](#1-determine-network-interfaces)

Mali by ste vidieť rýchlosť `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10000Mb/s` alebo sa spojenie nenaviaže, skontrolujte pripojenie kábla a potvrďte, že port switchu je nastavený na 10Gbps. Niektoré switche vyžadujú zakázanie automatickej negociácie a manuálne nastavenie rýchlosti spojenia; pozrite si dokumentáciu vášho switchu.

<!-- @os:end -->

<!-- @os:windows -->
### Overenie rýchlosti sieťového spojenia

Na každom stroji skontrolujte rýchlosť spojenia vašich sieťových rozhraní:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaše Ethernet rozhranie by malo byť `Up` a bežať rýchlosťou `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10 Gbps` alebo sa spojenie nenaviaže, skontrolujte pripojenie kábla a potvrďte, že port switchu je nastavený na 10Gbps. Niektoré switche vyžadujú zakázanie automatickej negociácie a manuálne nastavenie rýchlosti spojenia; pozrite si dokumentáciu vášho switchu.

<!-- @os:end -->

## Inštalácia llama.cpp

> **Poznámka**: Tento krok dokončite na Zariadení 1 aj Zariadení 2.

K dispozícii sú dve možnosti inštalácie:

- [Možnosť 1: Lemonade SDK (Odporúčané)](#option-1-lemonade-sdk-recommended) - vopred zostavené binárne súbory, najrýchlejšie nastavenie
- [Možnosť 2: Manuálne zostavenie zo zdroja](#option-2-manual-source-build) - zostavenie zo zdrojového kódu s plnou kontrolou nad zostavovacími príznakmi

### Možnosť 1: Lemonade SDK (Odporúčané)

Lemonade SDK poskytuje nočné zostavenia (nightly builds) llama.cpp s akceleráciou AMD ROCm 7, zamerané na GPU ako gfx1151 (Strix Halo / Ryzen AI Max+ 395) a ďalšie nedávne architektúry Radeon.

<!-- @os:windows -->
#### Krok 1: Stiahnutie predpripravených binárnych súborov

Prejdite na stránku najnovšieho vydania a stiahnite archív zodpovedajúci vašej platforme a cieľovému GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stiahnite súbor s názvom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo zostavenia).

#### Krok 2: Rozbalenie binárnych súborov

Rozbaľte stiahnutý archív:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tento adresár teraz obsahuje zostavy `llama-cli.exe`, `llama-server.exe` a `rpc-server.exe` s podporou ROCm, predkompilované pre váš systém Ryzen AI Halo.

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

Prejdite na stránku najnovšieho vydania a stiahnite archív zodpovedajúci vašej platforme a cieľovému GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stiahnite súbor s názvom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo zostavenia).

#### Krok 2: Rozbalenie a príprava binárnych súborov

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Tento adresár teraz obsahuje zostavy `llama-cli`, `llama-server` a `rpc-server` s podporou ROCm, predkompilované pre váš systém Ryzen AI Halo.

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
Keď je llama.cpp pripravený na každom uzle, pokračujte časťou [Stiahnutie modelu](#downloading-the-model).

### Možnosť 2: Manuálne zostavenie zo zdrojového kódu

<!-- @os:windows -->
#### Krok 1: Zostavenie llama.cpp

Otvorte **x64 Native Tools Command Prompt** (nainštalovaný spolu s Visual Studio Build Tools) a naklonujte repozitár:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Pridajte HIP do cesty a zostavte s podporou ROCm a RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Príznak zostavenia | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povolí softvérový stack ROCm/HIP |
| `-DGGML_RPC=ON` | Povolí RPC pre distribuovanú inferenciu |
| `-DGPU_TARGETS=gfx1151` | Zacieli na GPU Ryzen AI Halo (Radeon 8060s) |
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

Vyššie uvedený krok zostavenia nastavil `%HIP_PATH%\bin` iba pre aktuálnu reláciu. Aby boli knižnice HIP dostupné v akomkoľvek termináli (nielen v x64 Native Tools Command Prompt), pridajte ju natrvalo do používateľskej premennej `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Keď je llama.cpp pripravený na každom uzle, pokračujte časťou [Stiahnutie modelu](#downloading-the-model).
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
| `-DAMDGPU_TARGETS="gfx1151"` | Zacieli na GPU Ryzen AI Halo (Radeon 8060s) |

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

Keď je llama.cpp pripravený na každom uzle, pokračujte časťou [Stiahnutie modelu](#downloading-the-model).
<!-- @os:end -->

## Stiahnutie modelu

Táto príručka používa [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model s 358 miliardami parametrov v kvantizácii `Q4_K_XL` od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri tejto kvantizácii vyžaduje model približne 205 GB úložného priestoru a zmestí sa do kombinovanej pamäte GPU dvoch uzlov Ryzen AI Halo.

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

> **Poznámka**: Stiahnutie modelu musí byť dokončené na Zariadení 1 (kontrolér). Uzly pracujúce ako RPC pracovníci nepotrebujú lokálnu kópiu súborov modelu.

## Spustenie modelu na klastri

Nástroj llama.cpp RPC (Remote Procedure Call) umožňuje jednej inštancii llama.cpp odovzdávať vrstvy modelu vzdialeným pracovníkom cez sieť. Jeden počítač funguje ako **kontrolér** (Zariadenie 1), ktorý zabezpečuje tokenizáciu, plánovanie a orchestráciu. Druhý počítač spúšťa ľahký **RPC server** (Zariadenie 2), ktorý sprístupňuje svoju pamäť GPU a výpočtový výkon kontroléru.

Pri načítavaní llama.cpp rozdelí model medzi oba uzly. Po načítaní prebieha inferencia, akoby bežala na jedinom akcelerátore. RPC na pozadí zabezpečuje prenosy tenzorov a synchronizáciu.

### Krok 1: Spustenie RPC servera (Zariadenie 2)

Na Zariadení 2 spustite RPC server, aby sprístupnil svoje zdroje GPU kontroléru:
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
| `--host` | IP adresa, na ktorú sa má RPC server naviazať (`0.0.0.0` pre všetky rozhrania) |

Ďalšie možnosti nájdete v [dokumentácii RPC pre llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Spustenie modelu (Zariadenie 1)

Keď je RPC server spustený na Zariadení 2, spustite inferenciu zo Zariadenia 1 pomocou `llama-cli` alebo `llama-server`.

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

> **Zisťovanie `<RPC_WORKER_IP>`**: Na Zariadení 2 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
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

> **Zisťovanie `<RPC_WORKER_IP>`**: Na Zariadení 2 spustite `ipconfig | findstr /C:"IPv4"` v termináli (Powershell), aby ste zistili jeho lokálnu IP adresu.

<!-- @os:end -->

Po spustení `llama-cli` zobrazuje priebeh načítavania modelu a vstúpi do interaktívneho príkazového riadku, kde môžete priamo komunikovať s modelom:

![llama-cli spúšťajúci GLM 4.7 na dvoch uzloch](assets/llama-cli-example.png)
#### llama-server

`llama-server` sprístupňuje ten istý inferenčný engine prostredníctvom perzistentného serverového procesu s integrovaným webovým rozhraním a HTTP API kompatibilným s OpenAI. Toto je preferované rozhranie pre dlhodobejšie nasadenia, prístup viacerých používateľov a integráciu s externými nástrojmi.

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

> **Zisťovanie `<RPC_WORKER_IP>`**: Na Zariadení 2 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
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

> **Zisťovanie `<RPC_WORKER_IP>`**: Na Zariadení 2 spustite `ipconfig | findstr /C:"IPv4"` v termináli (Powershell), aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

Po spustení otvorte vo svojom prehliadači `http://<HOST_IP>:8081`, aby ste získali prístup k vstavanému webovému rozhraniu. Tá poskytuje rozhranie na chatovanie v prehliadači na interakciu s modelom:

![Webové rozhranie llama-server so spusteným GLM 4.7 na dvoch uzloch](assets/llama-server-example.png)

<!-- @os:linux -->
> **Zisťovanie `<HOST_IP>`**: Na Zariadení 1 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Zisťovanie `<HOST_IP>`**: Na Zariadení 1 spustite `ipconfig | findstr /C:"IPv4"` v termináli (Powershell), aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

#### Referencia parametrov

| Príznak | Účel |
|------|---------|
| `-m` | Cesta k súboru modelu GGUF (použite prvý fragment, `00001-of-00005`) |
| `-c` | Veľkosť kontextu v tokenoch. Vyššie hodnoty využívajú viac pamäte |
| `-fa on` | Povolí rocWMMA Flash Attention na zlepšenie výkonu na GPU AMD |
| `-ngl 999` | Presunie všetky vrstvy modelu na GPU |
| `-lm none` | Nastaví režim načítania modelu na `none`, čím sa vypne mapovanie pamäte (memory-mapping) na skrátenie času načítania, keď je veľkosť modelu väčšia ako systémová RAM, ale zmestí sa do VRAM |
| `--host` | IP adresa, na ktorú sa naviaže `llama-server` (iba `llama-server`) |
| `--port` | Port, na ktorom sa poskytuje HTTP API (iba `llama-server`) |
| `--rpc` | Zoznam koncových bodov RPC pracovníkov oddelených čiarkami (`IP:port`) |

Úplné informácie o použití parametrov nájdete v [dokumentácii k llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) a [dokumentácii k llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Ďalšie kroky

- **Pripojenie aplikácií tretích strán**: `llama-server` sprístupňuje API kompatibilné s OpenAI. Nasmerujte akúkoľvek aplikáciu kompatibilnú s OpenAI (napríklad Open WebUI) na `http://<HOST_IP>:8081` s ľubovoľným zástupným API kľúčom (napr. `none`), aby ste sa pripojili k svojmu klastru
- **Preskúmanie ďalších modelov**: Prehľadajte kvantizované GGUF súbory na [Hugging Face](https://huggingface.co/models?search=gguf), aby ste našli modely, ktoré sa zmestia do kombinovanej pamäte GPU vášho klastra
- **Škálovanie na štyri uzly**: Pridajte ďalšie dva systémy Ryzen AI Halo ako ďalších RPC pracovníkov, aby ste získali prístup k modelom v rozsahu 1 bilión parametrov. Ďalšie koncové body odovzdajte parametru `--rpc` ako zoznam oddelený čiarkami (napr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)