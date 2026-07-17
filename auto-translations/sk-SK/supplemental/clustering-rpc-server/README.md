<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Zhlukovaníe dvoch Ryzen™ AI Halo systémov pomocou RPC

## Prehľad

Váš Ryzen™ AI Halo je už schopný spúšťať veľké jazykové modely lokálne. Zhlukovaníe posúva túto možnosť ďalej kombináciou GPU pamäte viacerých systémov cez lokálnu sieť, čím získate prístup k ešte väčším modelom so silnejším uvažovaním, lepším generovaním kódu a hlbším viacjazyčným porozumením – všetko výhradne na vlastnom hardvéri.

Tento playbook vás naučí, ako zhlukiť dva Ryzen AI Halo systémy pomocou RPC enginu llama.cpp a spustiť GLM 4.7, model s 358 miliardami parametrov, naprieč oboma strojmi s akceleráciou AMD ROCm™.

## Čo sa naučíte

- Ako rozšíriť alokáciu VRAM na Ryzen AI Halo systémoch
- Inštalácia llama.cpp s podporou ROCm a RPC
- Konfigurácia RPC pracovníka a spustenie distribuovanej inferencie naprieč dvoma uzlami
- Spustenie modelu s 358 miliardami parametrov naprieč dvoma sieťovo prepojenými Ryzen AI Halo systémami

## Nastavenie konfigurácie pamäte

> **Poznámka**: Tento krok vykonajte na oboch strojoch – Stroji 1 aj Stroji 2.

<!-- @os:windows -->
V systéme Windows, na spúšťanie väčších modelov vyžadujúcich vyššiu pamäť, je potrebné použiť alokáciu AMD Variable Graphics Memory (iGPU VRAM).

Toto je možné vykonať otvorením ovládacieho panela AMD Software: Adrenalin Edition a navigáciou na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavte hodnotu na **96 GB**. Pre uplatnenie zmien reštartujte systém.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V systéme Linux ROCm využíva zdieľaný systémový pamäťový fond, ktorý je predvolene nakonfigurovaný na polovicu systémovej pamäte.

Toto množstvo je možné zvýšiť zmenou nastavenia stránky Translation Table Manager (TTM) jadra podľa nasledujúcich pokynov. AMD odporúča nastaviť minimálnu dedikovanú VRAM v BIOS (0,5 GB).

* Nainštalujte nástroj pipx a pridajte cestu pre kolieska nainštalované cez pipx do systémovej vyhľadávacej cesty.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainštalujte koleso amd-debug-tools z PyPI.
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

* Pre uplatnenie zmien reštartujte systém.


<!-- @os:end -->
<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

<!-- @require:software-update -->
<!-- @device:end -->
## Predpoklady

### Hardvér

Tento playbook vyžaduje dve jednotky Ryzen AI Halo a jeden ethernetový prepínač, prepojené v hviezdicovej topológii, pričom každá jednotka je priamo zapojená do prepínača.

| Komponent | Množstvo | Popis |
|-----------|----------|-------|
| Ryzen AI Halo | 2 | Výpočtové uzly tvoriace zhluk |
| 10Gbps ethernetový prepínač | 1 | Centrálny prepínač umožňujúci komunikáciu medzi uzlami Ryzen AI Halo (minimálne 2 porty) |
| Ethernetový kábel | 2 | Prepája každú jednotku Halo s prepínačom (odporúča sa Cat 7 alebo vyšší) |

> **Poznámka**: Na prepojenie dvoch jednotiek Ryzen AI Halo sú potrebné dva porty ethernetového prepínača. Tretí port je potrebný, ak pristupujete k modelu zo samostatného klientského stroja namiesto jednej z jednotiek Halo.

### Softvér
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Nainštalujte:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) s pracovnou záťažou **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyzické nastavenie hardvéru

> **Poznámka**: Tento krok vykonajte na oboch strojoch – Stroji 1 aj Stroji 2.

Pripojte každú jednotku Ryzen AI Halo k ethernetovému prepínaču pomocou kábla Cat 7 (alebo vyššieho). Tým sa vytvorí 10Gbps linka používaná na vysokorýchlostnú komunikáciu medzi uzlami.
<!-- @os:linux -->
### 1. Určenie sieťových rozhraní

Na každom stroji zistite názov jeho sieťového rozhrania a poznačte si ho (nižšie bude označovaný ako `IFNAME`). Spustite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Toto vypíše názov rozhrania priamo, napríklad:

```bash
enp191s0
```

### 2. Overenie rýchlostí sieťovej linky

Potvrďte, že linka je aktívna a beží na plnej rýchlosti, kontrolou rýchlosti vášho rozhrania:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` názvom výstupného rozhrania z kroku [1. Určenie sieťových rozhraní](#1-determine-network-interfaces)

Mali by ste vidieť rýchlosť `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10000Mb/s` alebo linka sa nespustí, skontrolujte káblové pripojenie a overte, či je port prepínača nastavený na 10Gbps. Niektoré prepínače vyžadujú vypnutie automatického vyjednávania a manuálne nastavenie rýchlosti linky; pozrite si dokumentáciu vášho prepínača.

<!-- @os:end -->

<!-- @os:windows -->
### Overenie rýchlosti sieťovej linky

Na každom stroji skontrolujte rýchlosť linky vašich sieťových rozhraní:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaše ethernetové rozhranie by malo byť `Up` a bežať na `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10 Gbps` alebo linka sa nespustí, skontrolujte káblové pripojenie a overte, či je port prepínača nastavený na 10Gbps. Niektoré prepínače vyžadujú vypnutie automatického vyjednávania a manuálne nastavenie rýchlosti linky; pozrite si dokumentáciu vášho prepínača.

<!-- @os:end -->

## Inštalácia llama.cpp

> **Poznámka**: Tento krok vykonajte na oboch strojoch – Stroji 1 aj Stroji 2.

K dispozícii sú dve možnosti inštalácie:

- [Možnosť 1: Lemonade SDK (Odporúčané)](#option-1-lemonade-sdk-recommended) – predpripravené binárne súbory, najrýchlejšie nastavenie
- [Možnosť 2: Manuálne zostavenie zo zdrojového kódu](#option-2-manual-source-build) – zostavenie zo zdrojového kódu s plnou kontrolou nad príznakmi zostavenia

### Možnosť 1: Lemonade SDK (Odporúčané)

Lemonade SDK poskytuje nočné zostavenia llama.cpp s akceleráciou AMD ROCm 7, zacielené na GPU ako gfx1151 (Strix Halo / Ryzen AI Max+ 395) a ďalšie nedávne architektúry Radeon.

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

Tento adresár teraz obsahuje zostavenia `llama-cli.exe`, `llama-server.exe` a `rpc-server.exe` s podporou ROCm, predkompilované pre váš Ryzen AI Halo systém.

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

Tento adresár teraz obsahuje zostavenia `llama-cli`, `llama-server` a `rpc-server` s podporou ROCm, predkompilované pre váš Ryzen AI Halo systém.

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
Po príprave llama.cpp na každom uzle pokračujte na [Stiahnutie modelu](#downloading-the-model).

### Možnosť 2: Manuálne zostavenie zo zdrojového kódu

<!-- @os:windows -->
#### Krok 1: Zostavenie llama.cpp

Otvorte **x64 Native Tools Command Prompt** (nainštalovaný s Visual Studio Build Tools) a naklonujte repozitár:

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
| `-DGGML_HIP=ON` | Aktivuje softvérový zásobník ROCm/HIP |
| `-DGGML_RPC=ON` | Aktivuje RPC pre distribuovanú inferenciu |
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

#### Krok 3: Pridanie HIP do používateľskej cesty PATH

Vyššie uvedený krok zostavenia nastavil `%HIP_PATH%\bin` iba pre aktuálnu reláciu. Aby boli knižnice HIP dostupné v akomkoľvek termináli (nielen v x64 Native Tools Command Prompt), pridajte ich trvalo do používateľskej premennej `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Po príprave llama.cpp na každom uzle pokračujte na [Stiahnutie modelu](#downloading-the-model).
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
| `-DGGML_HIP=ON` | Aktivuje softvérový zásobník ROCm |
| `-DGGML_RPC=ON` | Aktivuje RPC pre distribuovanú inferenciu |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Aktivuje rocWMMA pre vylepšenú Flash Attention na AMD GPU |
| `-DAMDGPU_TARGETS="gfx1151"` | Cieli na GPU Ryzen AI Halo (Radeon 8060s) |

Ďalšie možnosti zostavenia nájdete v [dokumentácii zostavenia llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Po príprave llama.cpp na každom uzle pokračujte na [Stiahnutie modelu](#downloading-the-model).
<!-- @os:end -->

## Stiahnutie modelu

Tento playbook používa [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model s 358 miliardami parametrov v kvantizácii `Q4_K_XL` od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri tejto kvantizácii model vyžaduje približne 205 GB úložného priestoru a zmestí sa do kombinovanej GPU pamäte dvoch uzlov Ryzen AI Halo.

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

> **Poznámka**: Stiahnutie modelu musí byť dokončené na Stroji 1 (kontrolér). Uzly RPC pracovníkov nepotrebujú lokálnu kópiu súborov modelu.

## Spustenie modelu na zhluku

RPC (Remote Procedure Call) engine llama.cpp umožňuje jednej inštancii llama.cpp preniesť vrstvy modelu na vzdialených pracovníkov cez sieť. Jeden stroj funguje ako **kontrolér** (Stroj 1), ktorý zabezpečuje tokenizáciu, plánovanie a orchestráciu. Druhý stroj spúšťa ľahký **RPC server** (Stroj 2), ktorý sprístupňuje svoju GPU pamäť a výpočtový výkon kontroléru.

Pri načítaní llama.cpp rozdelí model naprieč oboma uzlami. Po načítaní prebieha inferencia, akoby bežala na jednom akcelerátore. RPC zabezpečuje prenosy tenzorov a synchronizáciu na pozadí.

### Krok 1: Spustenie RPC servera (Stroj 2)

Na Stroji 2 spustite RPC server, aby sprístupnil svoje GPU zdroje kontroléru:
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

| Príznak | Účel |
|------|---------|
| `-p` | Port, na ktorom bude RPC server vysielať |
| `-c` | Aktivuje lokálnu vyrovnávaciu pamäť pre veľké tenzory, čím sa predchádza opakovaným sieťovým prenosom počas načítavania modelu |
| `--host` | IP adresa, na ktorú sa RPC server naviaže (`0.0.0.0` pre všetky rozhrania) |

Ďalšie možnosti nájdete v [dokumentácii RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Spustenie modelu (Stroj 1)

Po spustení RPC servera na Stroji 2 spustite inferenciu zo Stroja 1 pomocou `llama-cli` alebo `llama-server`.

#### llama-cli

`llama-cli` poskytuje terminálové rozhranie na priamu interakciu s modelom. Je ideálny na benchmarking, ladenie a nízkoúrovňové experimenty.

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

> **Nájdenie `<RPC_WORKER_IP>`**: Na Stroji 2 spustite `hostname -I | awk '{print $1}'` na zistenie jeho lokálnej IP adresy.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Spustite tento príkaz v Termináli (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Nájdenie `<RPC_WORKER_IP>`**: Na Stroji 2 spustite `ipconfig | findstr /C:"IPv4"` v Termináli (Powershell) na zistenie jeho lokálnej IP adresy.

<!-- @os:end -->

Po spustení `llama-cli` zobrazí priebeh načítavania modelu a vstúpi do interaktívnej výzvy, kde môžete priamo chatovať s modelom:

![llama-cli spúšťajúci GLM 4.7 naprieč dvoma uzlami](assets/llama-cli-example.png)

#### llama-server

`llama-server` sprístupňuje rovnaký inferenčný engine prostredníctvom trvalého serverového procesu s integrovaným webovým rozhraním a HTTP API kompatibilným s OpenAI. Toto je preferované rozhranie pre dlhodobejšie nasadenia, prístup viacerých používateľov a integráciu s externými nástrojmi.

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

> **Nájdenie `<RPC_WORKER_IP>`**: Na Stroji 2 spustite `hostname -I | awk '{print $1}'` na zistenie jeho lokálnej IP adresy.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Spustite tento príkaz v Termináli (Powershell).

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

> **Nájdenie `<RPC_WORKER_IP>`**: Na Stroji 2 spustite `ipconfig | findstr /C:"IPv4"` v Termináli (Powershell) na zistenie jeho lokálnej IP adresy.
<!-- @os:end -->

Po spustení otvorte `http://<HOST_IP>:8081` vo svojom prehliadači pre prístup k vstavanému webovému rozhraniu. Toto poskytuje chatové rozhranie v prehliadači na interakciu s modelom:

![Webové rozhranie llama-server spúšťajúce GLM 4.7 naprieč dvoma uzlami](assets/llama-server-example.png)

<!-- @os:linux -->
> **Nájdenie `<HOST_IP>`**: Na Stroji 1 spustite `hostname -I | awk '{print $1}'` na zistenie jeho lokálnej IP adresy.
<!-- @os:end -->

<!-- @os:windows -->
> **Nájdenie `<HOST_IP>`**: Na Stroji 1 spustite `ipconfig | findstr /C:"IPv4"` v Termináli (Powershell) na zistenie jeho lokálnej IP adresy.
<!-- @os:end -->

#### Referencia parametrov

| Príznak | Účel |
|------|---------|
| `-m` | Cesta k súboru modelu GGUF (použite prvý úsek, `00001-of-00005`) |
| `-c` | Veľkosť kontextu v tokenoch. Väčšie hodnoty využívajú viac pamäte |
| `-fa on` | Aktivuje rocWMMA Flash Attention pre lepší výkon na AMD GPU |
| `-ngl 999` | Prenáša všetky vrstvy modelu na GPU |
| `--no-mmap` | Deaktivuje mapovanie pamäte, čím sa skracujú časy načítavania, keď veľkosť modelu presahuje systémovú RAM, ale zmestí sa do VRAM |
| `--host` | IP adresa, na ktorú sa naviaže `llama-server` (iba pre `llama-server`) |
| `--port` | Port, na ktorom bude slúžiť HTTP API (iba pre `llama-server`) |
| `--rpc` | Čiarkami oddelený zoznam koncových bodov RPC pracovníkov (`IP:port`) |

Úplné použitie parametrov nájdete v [dokumentácii llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) a [dokumentácii llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Ďalšie kroky

- **Pripojenie aplikácií tretích strán**: `llama-server` sprístupňuje API kompatibilné s OpenAI. Nasmerujte akúkoľvek aplikáciu kompatibilnú s OpenAI (napríklad Open WebUI) na `http://<HOST_IP>:8081` s ľubovoľným zástupným kľúčom API (napr. `none`) pre pripojenie k vášmu zhluku
- **Preskúmanie ďalších modelov**: Prehliadajte kvantizované GGUF súbory na [Hugging Face](https://huggingface.co/models?search=gguf) a nájdite modely, ktoré sa zmestia do kombinovanej GPU pamäte vášho zhluku
- **Rozšírenie na štyri uzly**: Pridajte ďalšie dva Ryzen AI Halo systémy ako dodatočných RPC pracovníkov pre prístup k modelom na úrovni 1 bilióna parametrov. Odovzdajte ďalšie koncové body do `--rpc` ako čiarkami oddelený zoznam (napr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)