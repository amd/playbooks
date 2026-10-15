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

# Zhlukovanie (clustering) štyroch Ryzen™ AI Halo systémov pomocou RPC

## Prehľad

Váš Ryzen™ AI Halo je už schopný lokálne spúšťať veľké jazykové modely. Zhlukovanie (clustering) posúva túto možnosť ešte ďalej tým, že kombinuje pamäť GPU viacerých systémov cez lokálnu sieť, čím vám dáva prístup k ešte väčším modelom so silnejším uvažovaním, lepším generovaním kódu a hlbším viacjazyčným porozumením – to všetko úplne na vašom vlastnom hardvéri.

Táto príručka vás naučí, ako zhlukovať štyri systémy Ryzen AI Halo pomocou RPC engine z llama.cpp a spustiť Kimi K2.6, veľký model typu mixture-of-experts, naprieč všetkými štyrmi zariadeniami s akceleráciou AMD ROCm™.

## Čo sa naučíte

- Ako rozšíriť alokáciu VRAM na systémoch Ryzen AI Halo
- Inštaláciu llama.cpp s podporou ROCm a RPC
- Konfiguráciu RPC workerov a spustenie distribuovanej inferencie naprieč štyrmi uzlami
- Spustenie modelu s 1T parametrami naprieč štyrmi prepojenými systémami Ryzen AI Halo

## Nastavenie konfigurácie pamäte

> **Poznámka**: Tento krok vykonajte na všetkých štyroch zariadeniach (Zariadenie 1 až Zariadenie 4).

<!-- @os:windows -->
V systéme Windows, ak chcete spúšťať väčšie modely vyžadujúce viac pamäte, je potrebné použiť alokáciu AMD Variable Graphics Memory (iGPU VRAM).

To možno urobiť otvorením ovládacieho panela AMD Software: Adrenalin Edition a prechodom na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavte hodnotu na **96 GB**. Reštartujte systém, aby sa zmeny prejavili.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V systéme Linux využíva ROCm zdieľaný fond systémovej pamäte, ktorý je predvolene nastavený na polovicu systémovej pamäte.

Toto množstvo je možné zvýšiť zmenou nastavenia stránok Translation Table Manager (TTM) jadra podľa nasledujúcich pokynov. AMD odporúča nastaviť minimálnu vyhradenú VRAM v BIOSe (0.5 GB).

* Nainštalujte nástroj pipx a pridajte cestu k balíkom nainštalovaným cez pipx do systémovej vyhľadávacej cesty.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainštalujte balík amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spustite nástroj amd-ttm na zistenie aktuálneho nastavenia zdieľanej pamäte.
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

Táto príručka vyžaduje štyri jednotky Ryzen AI Halo a jeden ethernetový prepínač, zapojené v topológii hviezda, pričom každá jednotka je pripojená priamo k prepínaču.

| Komponent | Množstvo | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Výpočtové uzly tvoriace zhluk (cluster) |
| 10Gbps ethernetový prepínač | 1 | Centrálny prepínač umožňujúci komunikáciu viacerých uzlov Ryzen AI Halo (aspoň 4 porty) |
| Ethernetový kábel | 4 | Prepája každú jednotku Halo s prepínačom (odporúča sa Cat 7 alebo vyšší) |

> **Poznámka**: Na pripojenie štyroch jednotiek Ryzen AI Halo sú potrebné štyri porty ethernetového prepínača. Piaty port je potrebný, ak k modelu pristupujete zo samostatného klientskeho zariadenia namiesto z jednej z jednotiek Halo.

### Softvér
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Nainštalujte:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) s balíkom pracovných úloh **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Nastavenie fyzického hardvéru

> **Poznámka**: Tento krok vykonajte na všetkých štyroch zariadeniach (Zariadenie 1 až Zariadenie 4).

Pripojte každú jednotku Ryzen AI Halo k ethernetovému prepínaču pomocou kábla Cat 7 (alebo vyššieho). Tým sa vytvorí 10Gbps prepojenie použité pre vysokorýchlostnú komunikáciu medzi uzlami.
<!-- @os:linux -->
### 1. Zistenie sieťových rozhraní

Na každom zariadení zistite názov jeho sieťového rozhrania a poznačte si ho (nižšie sa naň bude odkazovať ako `IFNAME`). Spustite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Toto priamo vypíše názov rozhrania, napríklad:

```bash
enp191s0
```

### 2. Overenie rýchlosti sieťového pripojenia

Overte, že je pripojenie aktívne a beží plnou rýchlosťou kontrolou rýchlosti vášho rozhrania:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` názvom výstupného rozhrania z kroku [1. Zistenie sieťových rozhraní](#1-determine-network-interfaces)

Mali by ste vidieť rýchlosť `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10000Mb/s` alebo sa pripojenie nenadviaže, skontrolujte pripojenie kábla a overte, že je port prepínača nastavený na 10Gbps. Niektoré prepínače vyžadujú vypnutie automatického vyjednávania (auto-negotiation) a manuálne nastavenie rýchlosti pripojenia; postupujte podľa dokumentácie svojho prepínača.

<!-- @os:end -->

<!-- @os:windows -->
### Overenie rýchlosti sieťového pripojenia

Na každom zariadení skontrolujte rýchlosť pripojenia svojich sieťových rozhraní:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaše ethernetové rozhranie by malo byť `Up` a bežať rýchlosťou `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10 Gbps` alebo sa pripojenie nenadviaže, skontrolujte pripojenie kábla a overte, že je port prepínača nastavený na 10Gbps. Niektoré prepínače vyžadujú vypnutie automatického vyjednávania (auto-negotiation) a manuálne nastavenie rýchlosti pripojenia; postupujte podľa dokumentácie svojho prepínača.

<!-- @os:end -->

## Inštalácia llama.cpp

> **Poznámka**: Tento krok vykonajte na všetkých štyroch zariadeniach (Zariadenie 1 až Zariadenie 4).

K dispozícii sú dve možnosti inštalácie:

- [Možnosť 1: Lemonade SDK (odporúčané)](#option-1-lemonade-sdk-recommended) – vopred zostavené binárne súbory, najrýchlejšie nastavenie
- [Možnosť 2: Manuálne zostavenie zo zdrojového kódu](#option-2-manual-source-build) – zostavenie zo zdrojového kódu s plnou kontrolou nad parametrami zostavenia

### Možnosť 1: Lemonade SDK (odporúčané)

Lemonade SDK poskytuje nočné zostavenia (nightly builds) llama.cpp s akceleráciou AMD ROCm 7, zamerané na GPU ako gfx1151 (Strix Halo / Ryzen AI Max+ 395) a ďalšie novšie architektúry Radeon.

<!-- @os:windows -->
#### Krok 1: Stiahnutie predpripravených binárnych súborov

Prejdite na stránku najnovšieho vydania a stiahnite archív zodpovedajúci vašej platforme a cieľovej GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stiahnite súbor s názvom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo zostavenia).

#### Krok 2: Rozbalenie binárnych súborov

Rozbaľte stiahnutý archív:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tento adresár teraz obsahuje zostavy `llama-cli.exe`, `llama-server.exe` a `ggml-rpc-server.exe` s podporou ROCm, prekompilované pre váš systém Ryzen AI Halo.

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

Prejdite na stránku najnovšieho vydania a stiahnite archív zodpovedajúci vašej platforme a cieľovej GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Stiahnite súbor s názvom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kde `xxxx` je číslo zostavenia).

#### Krok 2: Rozbalenie a príprava binárnych súborov

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Tento adresár teraz obsahuje zostavy `llama-cli`, `llama-server` a `rpc-server` s podporou ROCm, prekompilované pre váš systém Ryzen AI Halo.

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

Pridajte HIP do vašej cesty a zostavte s podporou ROCm a RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Príznak zostavenia | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povolí softvérový zásobník ROCm/HIP |
| `-DGGML_RPC=ON` | Povolí RPC pre distribuovanú inferenciu |
| `-DGPU_TARGETS=gfx1151` | Cieli na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Použije systém zostavovania Ninja |

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

#### Krok 3: Trvalé pridanie HIP do používateľskej cesty

Vyššie uvedený krok zostavenia nastavil `%HIP_PATH%\bin` iba pre aktuálnu reláciu. Aby boli knižnice HIP dostupné v akomkoľvek termináli (nielen v x64 Native Tools Command Prompt), pridajte ju natrvalo do vašej používateľskej premennej `PATH`:

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
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Príznak zostavenia | Účel |
|-----------|---------|
| `-DGGML_HIP=ON` | Povolí softvérový zásobník ROCm |
| `-DGGML_RPC=ON` | Povolí RPC pre distribuovanú inferenciu |
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

Táto príručka používa model [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) v kvantizácii `UD-Q2_K_XL` od [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Táto kvantizácia sa zmestí do kombinovanej pamäte GPU štyroch uzlov Ryzen AI Halo.

Stiahnite súbory GGUF pomocou Hugging Face CLI:
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

> **Poznámka**: Stiahnutie modelu je potrebné dokončiť na počítači Machine 1 (controller). Uzly RPC worker (počítače Machine 2, 3 a 4) nepotrebujú lokálnu kópiu súborov modelu.

## Spustenie modelu v klastri

Engine RPC (Remote Procedure Call) v llama.cpp umožňuje jednej inštancii llama.cpp odovzdávať vrstvy modelu vzdialeným pracovným uzlom cez sieť. Jeden počítač funguje ako **controller** (Machine 1) a stará sa o tokenizáciu, plánovanie a orchestráciu. Ostatné tri počítače (Machine 2, 3 a 4) spúšťajú odľahčený **RPC server**, ktorý sprístupňuje ich pamäť GPU a výpočtový výkon controlleru.

Pri načítaní llama.cpp rozdelí model medzi všetky štyri uzly. Po načítaní prebieha inferencia, akoby sa vykonávala na jedinom akcelerátore. RPC sa v pozadí stará o prenos tenzorov a synchronizáciu.

### Krok 1: Spustenie RPC serverov (počítače Machine 2, 3 a 4)

Na každom z počítačov Machine 2, 3 a 4 spustite RPC server, aby sprístupnil svoje zdroje GPU controlleru:
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
| `-c` | Povolí lokálnu vyrovnávaciu pamäť pre veľké tenzory, čím sa zabráni opakovaným sieťovým prenosom počas načítavania modelu |
| `--host` | IP adresa, na ktorú sa naviaže RPC server (`0.0.0.0` pre všetky rozhrania) |

Ďalšie možnosti nájdete v [dokumentácii k RPC v llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Spustenie modelu (Machine 1)

Keď sú RPC servery spustené na počítačoch Machine 2, 3 a 4, spustite inferenciu z počítača Machine 1 pomocou buď `llama-cli`, alebo `llama-server`.
#### llama-cli

`llama-cli` poskytuje terminálové rozhranie na priamu interakciu s modelom. Je ideálny na benchmarking, ladenie a experimentovanie na nízkej úrovni.

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

> **Zisťovanie `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na každom zo strojov 2, 3 a 4 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento príkaz spustite v termináli (Powershell).

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

> **Zisťovanie `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na každom zo strojov 2, 3 a 4 spustite v termináli (Powershell) `ipconfig | findstr /C:"IPv4"`, aby ste zistili jeho lokálnu IP adresu.

<!-- @os:end -->

Po spustení `llama-cli` zobrazí priebeh načítavania modelu a otvorí interaktívny príkazový riadok, kde môžete priamo komunikovať s modelom:

![llama-cli spúšťajúci Kimi K2.6 na štyroch uzloch](assets/llama-cli-example.png)

#### llama-server

`llama-server` sprístupňuje ten istý inferenčný engine prostredníctvom trvalého serverového procesu s integrovaným webovým používateľským rozhraním a HTTP API kompatibilným s OpenAI. Toto je preferované rozhranie pre dlhodobejšie nasadenia, prístup viacerých používateľov a integráciu s externými nástrojmi.

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

> **Zisťovanie `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na každom zo strojov 2, 3 a 4 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Tento príkaz spustite v termináli (Powershell).

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

> **Zisťovanie `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na každom zo strojov 2, 3 a 4 spustite v termináli (Powershell) `ipconfig | findstr /C:"IPv4"`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

Po spustení otvorte v prehliadači `http://<HOST_IP>:8081`, aby ste získali prístup k zabudovanému webovému rozhraniu. To poskytuje chatové rozhranie na báze prehliadača na interakciu s modelom:

![Webové rozhranie llama-server spúšťajúce Kimi K2.6 na štyroch uzloch](assets/llama-server-example.png)

<!-- @os:linux -->
> **Zisťovanie `<HOST_IP>`**: Na stroji 1 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Zisťovanie `<HOST_IP>`**: Na stroji 1 spustite v termináli (Powershell) `ipconfig | findstr /C:"IPv4"`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

#### Referencia parametrov

| Príznak | Účel |
|------|---------|
| `-m` | Cesta k súboru modelu GGUF (použite prvý fragment, `00001-of-00008`) |
| `-c` | Veľkosť kontextu v tokenoch. Vyššie hodnoty používajú viac pamäte |
| `-fa on` | Zapne rocWMMA Flash Attention pre lepší výkon na GPU AMD |
| `-ngl 999` | Presunie všetky vrstvy modelu na GPU |
| `-lm none` | Nastaví režim načítania modelu na `none`, čím sa vypne mapovanie pamäte (memory-mapping) na skrátenie času načítania, keď veľkosť modelu presahuje veľkosť systémovej RAM, ale zmestí sa do VRAM |
| `-b` | Logická veľkosť dávky (batch) v tokenoch. Nastavenie na 4096 vyváži priepustnosť a využitie pamäte naprieč uzlami |
| `-ub` | Fyzická (mikro) veľkosť dávky pre spracovanie promptu. Zhoda s `-b` zabraňuje zbytočnej réžii spôsobenej delením na časti |
| `--host` | IP adresa, na ktorú sa má naviazať `llama-server` (iba `llama-server`) |
| `--port` | Port, na ktorom sa poskytuje HTTP API (iba `llama-server`) |
| `--rpc` | Zoznam koncových bodov RPC pracovných uzlov oddelených čiarkami (`IP:port`) |

Úplné informácie o použití parametrov nájdete v [dokumentácii k llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) a [dokumentácii k llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Ďalšie kroky

- **Pripojenie aplikácií tretích strán**: `llama-server` poskytuje API kompatibilné s OpenAI. Nasmerujte ľubovoľnú aplikáciu kompatibilnú s OpenAI (napríklad Open WebUI) na `http://<HOST_IP>:8081` s ľubovoľným zástupným API kľúčom (napr. `none`), aby ste sa pripojili k vášmu klastru
- **Preskúmanie ďalších modelov**: Prehľadajte kvantizované GGUF na [Hugging Face](https://huggingface.co/models?search=gguf) a nájdite modely, ktoré sa zmestia do kombinovanej pamäte GPU vášho klastra
- **Škálovanie nad rámec štyroch uzlov**: Pridajte ďalšie systémy Ryzen AI Halo ako ďalšie pracovné uzly RPC, aby ste získali prístup k modelom presahujúcim úroveň 1 bilión parametrov. Odovzdajte ďalšie koncové body parametru `--rpc` ako zoznam oddelený čiarkami (napr. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)