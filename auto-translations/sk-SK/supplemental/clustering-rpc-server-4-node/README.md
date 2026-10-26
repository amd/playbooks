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

# Klastrovanie štyroch systémov Ryzen™ AI Halo pomocou RPC

## Prehľad

Váš Ryzen™ AI Halo už dokáže lokálne spúšťať veľké jazykové modely. Klastrovanie posúva túto schopnosť ešte ďalej tým, že kombinuje pamäť GPU viacerých systémov cez lokálnu sieť, čím vám poskytuje prístup k ešte väčším modelom so silnejším uvažovaním, lepším generovaním kódu a hlbším viacjazyčným porozumením – a to úplne na vlastnom hardvéri.

Táto príručka vás naučí, ako klastrovať štyri systémy Ryzen AI Halo pomocou RPC enginu nástroja llama.cpp a spustiť Kimi K2.6, veľký mixture-of-experts model, naprieč všetkými štyrmi strojmi s akceleráciou AMD ROCm™.

## Čo sa naučíte

- Ako rozšíriť alokáciu VRAM na systémoch Ryzen AI Halo
- Inštaláciu llama.cpp s podporou ROCm a RPC
- Konfiguráciu RPC pracovných uzlov a spustenie distribuovanej inferencie naprieč štyrmi uzlami
- Spustenie modelu s 1 biliónom parametrov naprieč štyrmi prepojenými systémami Ryzen AI Halo

## Nastavenie konfigurácie pamäte

> **Poznámka**: Tento krok dokončite na všetkých štyroch strojoch (Stroj 1 až Stroj 4).

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Spúšťanie modelov s veľkosťou blízkou alebo presahujúcou 128 GB:** Na systémoch AMD Ryzen™ AI Max 400 Series (Gorgon Halo) so systémom Windows vyžadujú modely, ktoré sa blížia k 128 GB pamäte alebo ju prekračujú, dodatočnú konfiguráciu, aby fungovali bez chýb. Pred načítaním modelu postupujte podľa [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines).
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
V systéme Windows, ak chcete spúšťať väčšie modely vyžadujúce vyššiu pamäť, musíme použiť alokáciu AMD Variable Graphics Memory (iGPU VRAM).

To je možné urobiť otvorením ovládacieho panela AMD Software: Adrenalin Edition a prechodom na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavte hodnotu na **96 GB**. Reštartujte systém, aby sa zmeny prejavili.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V systéme Linux využíva ROCm zdieľaný fond systémovej pamäte, ktorý je štandardne nakonfigurovaný na polovicu systémovej pamäte.

Toto množstvo je možné zvýšiť zmenou nastavenia stránok Translation Table Manager (TTM) jadra podľa nasledujúcich pokynov. AMD odporúča nastaviť minimálnu vyhradenú VRAM v BIOSe (0,5 GB).

* Nainštalujte nástroj pipx a pridajte cestu k wheelom nainštalovaným cez pipx do systémovej vyhľadávacej cesty.

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

* Nakonfigurujte nastavenia zdieľanej pamäte na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reštartujte systém, aby sa zmeny prejavili.


<!-- @os:end -->
<!-- @device:halo_box -->
## Kontrola softvérových aktualizácií

<!-- @require:software-update -->
<!-- @device:end -->
## Predpoklady

### Hardvér

Táto príručka vyžaduje štyri jednotky Ryzen AI Halo a jeden ethernetový switch, zapojené v hviezdicovej topológii, pričom každá jednotka je priamo pripojená k switchu.

| Komponent | Množstvo | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Výpočtové uzly tvoriace klaster |
| 10Gbps ethernetový switch | 1 | Centrálny switch umožňujúci komunikáciu medzi viacerými uzlami Ryzen AI Halo (minimálne 4 porty) |
| Ethernetový kábel | 4 | Prepája každú jednotku Halo so switchom (odporúča sa Cat 7 alebo vyšší) |

> **Poznámka**: Na pripojenie štyroch jednotiek Ryzen AI Halo sú potrebné štyri porty ethernetového switchu. Piaty port je potrebný, ak pristupujete k modelu zo samostatného klientskeho stroja namiesto jednej z jednotiek Halo.

### Softvér
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Nainštalujte:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) so sadou **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyzické nastavenie hardvéru

> **Poznámka**: Tento krok dokončite na všetkých štyroch strojoch (Stroj 1 až Stroj 4).

Pripojte každú jednotku Ryzen AI Halo k ethernetovému switchu pomocou kábla Cat 7 (alebo vyššieho). Tým sa vytvorí 10Gbps spojenie používané pre vysokorýchlostnú komunikáciu medzi uzlami.
<!-- @os:linux -->
### 1. Zistenie sieťových rozhraní

Na každom stroji zistite názov jeho sieťového rozhrania a poznačte si ho (ďalej sa naň bude odkazovať ako `IFNAME`). Spustite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tento príkaz priamo vypíše názov rozhrania, napríklad:

```bash
enp191s0
```

### 2. Overenie rýchlosti sieťového spojenia

Overte, že spojenie je aktívne a beží plnou rýchlosťou, skontrolovaním rýchlosti vášho rozhrania:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` názvom výstupného rozhrania z [1. Zistenie sieťových rozhraní](#1-determine-network-interfaces)

Mali by ste vidieť rýchlosť `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10000Mb/s` alebo spojenie nefunguje, skontrolujte pripojenie kábla a potvrďte, že je port switchu nastavený na 10Gbps. Niektoré switche vyžadujú vypnutie automatického vyjednávania rýchlosti (auto-negotiation) a manuálne nastavenie rýchlosti spojenia; postupujte podľa dokumentácie k vášmu switchu.

<!-- @os:end -->

<!-- @os:windows -->
### Overenie rýchlosti sieťového spojenia

Na každom stroji skontrolujte rýchlosť spojenia vašich sieťových rozhraní:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaše ethernetové rozhranie by malo byť `Up` a bežať rýchlosťou `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10 Gbps` alebo spojenie nefunguje, skontrolujte pripojenie kábla a potvrďte, že je port switchu nastavený na 10Gbps. Niektoré switche vyžadujú vypnutie automatického vyjednávania rýchlosti (auto-negotiation) a manuálne nastavenie rýchlosti spojenia; postupujte podľa dokumentácie k vášmu switchu.

<!-- @os:end -->

## Inštalácia llama.cpp

> **Poznámka**: Tento krok dokončite na všetkých štyroch strojoch (Stroj 1 až Stroj 4).

K dispozícii sú dve možnosti inštalácie:

- [Možnosť 1: Lemonade SDK (odporúčané)](#option-1-lemonade-sdk-recommended) - vopred zostavené binárne súbory, najrýchlejšie nastavenie
- [Možnosť 2: Manuálne zostavenie zo zdrojového kódu](#option-2-manual-source-build) - zostavenie zo zdrojového kódu s plnou kontrolou nad zostavovacími príznakmi
### Možnosť 1: Lemonade SDK (odporúčané)

Lemonade SDK poskytuje nočné (nightly) zostavenia llama.cpp s akceleráciou AMD ROCm 7, zamerané na GPU ako gfx1151 (Strix Halo / Ryzen AI Max+ 395) a ďalšie nedávne architektúry Radeon.

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

Tento adresár teraz obsahuje zostavenia `llama-cli.exe`, `llama-server.exe` a `ggml-rpc-server.exe` s podporou ROCm, predkompilované pre váš systém Ryzen AI Halo.

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

Tento adresár teraz obsahuje zostavenia `llama-cli`, `llama-server` a `rpc-server` s podporou ROCm, predkompilované pre váš systém Ryzen AI Halo.

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
| `-DGPU_TARGETS=gfx1151` | Zacieľuje na GPU Ryzen AI Halo (Radeon 8060s) |
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

Vyššie uvedený krok zostavenia nastavil `%HIP_PATH%\bin` len pre aktuálnu reláciu. Aby boli knižnice HIP dostupné v akomkoľvek termináli (nielen v x64 Native Tools Command Prompt), pridajte ju trvalo do svojej používateľskej premennej `PATH`:

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
| `-DAMDGPU_TARGETS="gfx1151"` | Zacieľuje na GPU Ryzen AI Halo (Radeon 8060s) |

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

Po príprave llama.cpp na každom uzle pokračujte časťou [Sťahovanie modelu](#downloading-the-model).
<!-- @os:end -->

## Sťahovanie modelu

Tento návod (playbook) používa [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) v kvantizácii `UD-Q2_K_XL` od [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Táto kvantizácia sa zmestí do kombinovanej pamäte GPU štyroch uzlov Ryzen AI Halo.

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

> **Poznámka**: Sťahovanie modelu musí byť dokončené na Počítači 1 (riadiaci počítač). Uzly RPC worker (počítače 2, 3 a 4) nepotrebujú lokálnu kópiu súborov modelu.

## Spustenie modelu na klastri

Engine llama.cpp RPC (Remote Procedure Call) umožňuje, aby jedna inštancia llama.cpp odovzdávala vrstvy modelu vzdialeným pracovným uzlom cez sieť. Jeden počítač funguje ako **riadiaci počítač** (Počítač 1), ktorý zabezpečuje tokenizáciu, plánovanie a orchestráciu. Ostatné tri počítače spúšťajú odľahčený **RPC server** (počítače 2, 3 a 4), ktorý sprístupňuje svoju pamäť GPU a výpočtový výkon riadiacemu počítaču.

Pri načítaní rozdeľuje llama.cpp model medzi všetky štyri uzly. Po načítaní prebieha inferencia, akoby bežala na jedinom akcelerátore. RPC na pozadí rieši prenosy tenzorov a synchronizáciu.

### Krok 1: Spustenie RPC serverov (počítače 2, 3 a 4)

Na každom z počítačov 2, 3 a 4 spustite RPC server, aby ste sprístupnili jeho GPU zdroje riadiacemu počítaču:
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
| `-p` | Port, na ktorom sa má vysielať RPC server |
| `-c` | Povolí lokálnu vyrovnávaciu pamäť pre veľké tenzory, čím sa predíde opakovaným prenosom cez sieť počas načítavania modelu |
| `--host` | IP adresa, na ktorú sa má naviazať RPC server (`0.0.0.0` pre všetky rozhrania) |

Ďalšie možnosti nájdete v [dokumentácii k RPC pre llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Spustenie modelu (Počítač 1)

Keď sú RPC servery spustené na počítačoch 2, 3 a 4, spustite inferenciu z Počítača 1 pomocou buď `llama-cli`, alebo `llama-server`.
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

> **Nájdenie `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na každom zo strojov 2, 3 a 4 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
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

> **Nájdenie `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na každom zo strojov 2, 3 a 4 spustite `ipconfig | findstr /C:"IPv4"` v termináli (Powershell), aby ste zistili jeho lokálnu IP adresu.

<!-- @os:end -->

Po spustení `llama-cli` zobrazí priebeh načítavania modelu a prejde do interaktívneho príkazového riadka, kde môžete priamo komunikovať s modelom:

![llama-cli running Kimi K2.6 across four nodes](assets/llama-cli-example.png)

#### llama-server

`llama-server` sprístupňuje ten istý inferenčný engine prostredníctvom trvalého serverového procesu s integrovaným webovým rozhraním a HTTP API kompatibilným s OpenAI. Toto je preferované rozhranie pre dlhodobo bežiace nasadenia, prístup viacerých používateľov a integráciu s externými nástrojmi.

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

> **Nájdenie `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na každom zo strojov 2, 3 a 4 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
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

> **Nájdenie `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na každom zo strojov 2, 3 a 4 spustite `ipconfig | findstr /C:"IPv4"` v termináli (Powershell), aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

Po spustení otvorte vo svojom prehliadači `http://<HOST_IP>:8081`, aby ste získali prístup k zabudovanému webovému rozhraniu. Toto poskytuje rozhranie na komunikáciu s modelom vo forme chatu v prehliadači:

![llama-server web UI running Kimi K2.6 across four nodes](assets/llama-server-example.png)

<!-- @os:linux -->
> **Nájdenie `<HOST_IP>`**: Na stroji 1 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Nájdenie `<HOST_IP>`**: Na stroji 1 spustite `ipconfig | findstr /C:"IPv4"` v termináli (Powershell), aby ste zistili jeho lokálnu IP adresu.
<!-- @os:end -->

#### Referencia parametrov

| Príznak | Účel |
|------|---------|
| `-m` | Cesta k súboru modelu GGUF (použite prvý fragment, `00001-of-00008`) |
| `-c` | Veľkosť kontextu v tokenoch. Vyššie hodnoty využívajú viac pamäte |
| `-fa on` | Povolí rocWMMA Flash Attention na zlepšenie výkonu na GPU od AMD |
| `-ngl 999` | Presunie všetky vrstvy modelu na GPU |
| `-lm none` | Nastaví režim načítavania modelu na `none`, čím sa zakáže mapovanie pamäte (memory-mapping) a skráti sa čas načítania, keď je veľkosť modelu väčšia ako systémová RAM, ale zmestí sa do VRAM |
| `-b` | Logická veľkosť dávky (batch) v tokenoch. Nastavenie na 4096 vyvažuje priepustnosť a využitie pamäte medzi uzlami |
| `-ub` | Fyzická (mikro) veľkosť dávky na spracovanie promptu. Zhoda s `-b` zabraňuje zbytočnej réžii spôsobenej delením na časti |
| `--host` | IP adresa, na ktorú sa má naviazať `llama-server` (iba pre `llama-server`) |
| `--port` | Port, na ktorom sa poskytuje HTTP API (iba pre `llama-server`) |
| `--rpc` | Čiarkami oddelený zoznam koncových bodov RPC pracovných uzlov (`IP:port`) |

Úplné informácie o použití parametrov nájdete v dokumentácii [llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) a dokumentácii [llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Ďalšie kroky

- **Pripojenie aplikácií tretích strán**: `llama-server` sprístupňuje API kompatibilné s OpenAI. Nasmerujte akúkoľvek aplikáciu kompatibilnú s OpenAI (napríklad Open WebUI) na `http://<HOST_IP>:8081` s ľubovoľným zástupným API kľúčom (napr. `none`), aby ste sa pripojili k svojmu clusteru
- **Preskúmanie ďalších modelov**: Prehľadajte kvantizované GGUF na [Hugging Face](https://huggingface.co/models?search=gguf), aby ste našli modely, ktoré sa zmestia do kombinovanej pamäte GPU vášho clustra
- **Škálovanie nad rámec štyroch uzlov**: Pridajte ďalšie systémy Ryzen AI Halo ako ďalšie RPC pracovné uzly, aby ste získali prístup k modelom presahujúcim rozsah 1 bilióna parametrov. Odovzdajte ďalšie koncové body parametru `--rpc` ako čiarkami oddelený zoznam (napr. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)