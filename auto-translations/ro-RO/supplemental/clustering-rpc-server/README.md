<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clusterizarea a Două Sisteme Ryzen™ AI Halo cu RPC

## Prezentare generală

Sistemul tău Ryzen™ AI Halo este deja capabil să ruleze modele de limbaj de mari dimensiuni local. Clusterizarea duce acest lucru mai departe, combinând memoria GPU a mai multor sisteme printr-o rețea locală, oferindu-ți acces la modele și mai mari, cu raționament mai puternic, generare de cod mai bună și o înțelegere multilingvă mai profundă, totul în întregime pe propriul tău hardware.

Acest ghid te învață cum să clusterizezi două sisteme Ryzen AI Halo folosind motorul RPC al llama.cpp și cum să rulezi GLM 4.7, un model cu 358B parametri, pe ambele mașini cu accelerare AMD ROCm™.

## Ce vei învăța

- Cum să extinzi alocarea VRAM pe sistemele Ryzen AI Halo
- Instalarea llama.cpp cu suport ROCm și RPC
- Configurarea unui worker RPC și lansarea inferenței distribuite pe două noduri
- Rularea unui model cu 358B parametri pe două sisteme Ryzen AI Halo conectate în rețea

## Configurarea Memoriei

> **Notă**: Finalizează acest pas atât pe Mașina 1, cât și pe Mașina 2.

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Rularea modelelor aproape de sau peste 128 GB:** Pe sistemele AMD Ryzen™ AI Max 400 Series (Gorgon Halo) care rulează Windows, modelele care se apropie sau depășesc 128 GB de memorie necesită o configurare suplimentară pentru a rula fără erori. Urmează [Ghidul AMD Ryzen AI Max PRO 400 Series pentru Sistemul de Operare Windows](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) înainte de a încărca modelul.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Pe Windows, pentru a rula modele mai mari care necesită memorie mai multă, trebuie să folosim alocarea AMD Variable Graphics Memory (iGPU VRAM).

Acest lucru se poate face deschizând panoul de control AMD Software: Adrenalin Edition și navigând la: `Performance > Tuning > AMD Variable Graphics Memory`. Setează valoarea la **96 GB**. Te rugăm să repornești sistemul pentru ca modificările să intre în vigoare.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Pe Linux, ROCm utilizează un pool de memorie partajată a sistemului, iar acest pool este configurat implicit la jumătate din memoria sistemului.

Această valoare poate fi mărită prin schimbarea setării paginii Translation Table Manager (TTM) a kernelului, folosind instrucțiunile de mai jos. AMD recomandă setarea VRAM-ului dedicat minim în BIOS (0,5 GB).

* Instalează utilitarul pipx și adaugă calea pentru pachetele wheel instalate de pipx în calea de căutare a sistemului.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalează pachetul wheel amd-debug-tools de pe PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Rulează instrumentul amd-ttm pentru a interoga setările curente pentru memoria partajată.
  ```bash
  amd-ttm
  ```

* Reconfigurează setările de memorie partajată la **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Repornește sistemul pentru ca modificările să intre în vigoare.


<!-- @os:end -->
<!-- @device:halo_box -->
## Verificarea Actualizărilor de Software

<!-- @require:software-update -->
<!-- @device:end -->
## Cerințe preliminare

### Hardware

Acest ghid necesită două unități Ryzen AI Halo și un switch Ethernet, conectate într-o topologie stea, fiecare unitate fiind conectată direct la switch.

| Componentă | Cantitate | Descriere |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Noduri de calcul care formează clusterul |
| Switch Ethernet 10Gbps | 1 | Switch central pentru a permite comunicarea multi-nod Ryzen AI Halo (cel puțin 2 porturi) |
| Cablu Ethernet | 2 | Conectează fiecare unitate Halo la switch (se recomandă Cat 7 sau superior) |

> **Notă**: Sunt necesare două porturi ale switch-ului Ethernet pentru a conecta cele două unități Ryzen AI Halo. Este necesar un al treilea port dacă accesezi modelul de pe o mașină client separată, în loc de pe una dintre unitățile Halo.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Te rugăm să instalezi:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) cu pachetul de lucru **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Configurarea Hardware-ului Fizic

> **Notă**: Finalizează acest pas atât pe Mașina 1, cât și pe Mașina 2.

Conectează fiecare unitate Ryzen AI Halo la switch-ul Ethernet folosind un cablu Cat 7 (sau superior). Aceasta stabilește legătura de 10Gbps folosită pentru comunicarea de mare viteză între noduri.
<!-- @os:linux -->
### 1. Determinarea Interfețelor de Rețea

Pe fiecare mașină, află numele interfeței sale de rețea și notează-l (va fi menționat mai jos ca `IFNAME`). Rulează:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Aceasta afișează numele interfeței direct, de exemplu:

```bash
enp191s0
```

### 2. Verificarea Vitezelor Legăturii de Rețea

Confirmă că legătura este activă și rulează la viteză maximă verificând viteza interfeței tale:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Notă**: Înlocuiește `<IFNAME>` cu numele interfeței de ieșire din [1. Determinarea Interfețelor de Rețea](#1-determinarea-interfețelor-de-rețea)

Ar trebui să vezi o viteză de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Notă**: Dacă viteza este mai mică decât `10000Mb/s` sau legătura nu se stabilește, verifică conexiunea cablului și confirmă că portul switch-ului este setat la 10Gbps. Unele switch-uri necesită dezactivarea auto-negocierii și setarea manuală a vitezei legăturii; consultă documentația switch-ului tău.

<!-- @os:end -->

<!-- @os:windows -->
### Verificarea Vitezei Legăturii de Rețea

Pe fiecare mașină, verifică viteza legăturii interfețelor tale de rețea:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Interfața ta Ethernet ar trebui să fie `Up` și să ruleze la `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Notă**: Dacă viteza este mai mică decât `10 Gbps` sau legătura nu se stabilește, verifică conexiunea cablului și confirmă că portul switch-ului este setat la 10Gbps. Unele switch-uri necesită dezactivarea auto-negocierii și setarea manuală a vitezei legăturii; consultă documentația switch-ului tău.

<!-- @os:end -->

## Instalarea llama.cpp

> **Notă**: Finalizează acest pas atât pe Mașina 1, cât și pe Mașina 2.

Sunt disponibile două opțiuni de instalare:

- [Opțiunea 1: Lemonade SDK (Recomandat)](#option-1-lemonade-sdk-recommended) - binare precompilate, configurare cea mai rapidă
- [Opțiunea 2: Compilare Manuală din Sursă](#option-2-manual-source-build) - compilează din sursă cu control complet asupra flag-urilor de compilare
### Opțiunea 1: Lemonade SDK (Recomandat)

Lemonade SDK oferă build-uri nocturne ale llama.cpp cu accelerare AMD ROCm 7, vizând GPU-uri precum gfx1151 (Strix Halo / Ryzen AI Max+ 395) și alte arhitecturi Radeon recente.

<!-- @os:windows -->
#### Pasul 1: Descărcați binarele precompilate

Navigați la pagina celei mai recente versiuni și descărcați arhiva corespunzătoare platformei și GPU-ului dumneavoastră țintă:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Descărcați fișierul numit `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (unde `xxxx` este numărul build-ului).

#### Pasul 2: Extrageți binarele

Dezarhivați arhiva descărcată:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Acest director conține acum build-uri ROCm ale `llama-cli.exe`, `llama-server.exe` și `rpc-server.exe`, precompilate pentru sistemul dumneavoastră Ryzen AI Halo.

#### Pasul 3: Verificați detectarea GPU-ului

```bash
.\llama-cli.exe --list-devices
```

Rezultat așteptat:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Pasul 1: Descărcați binarele precompilate

Navigați la pagina celei mai recente versiuni și descărcați arhiva corespunzătoare platformei și GPU-ului dumneavoastră țintă:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Descărcați fișierul numit `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (unde `xxxx` este numărul build-ului).

#### Pasul 2: Extrageți și pregătiți binarele

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Acest director conține acum build-uri ROCm ale `llama-cli`, `llama-server` și `rpc-server`, precompilate pentru sistemul dumneavoastră Ryzen AI Halo.

#### Pasul 3: Verificați detectarea GPU-ului

```bash
./llama-cli --list-devices
```

Rezultat așteptat:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Cu llama.cpp pregătit pe fiecare nod, continuați cu [Descărcarea modelului](#downloading-the-model).

### Opțiunea 2: Build manual din sursă

<!-- @os:windows -->
#### Pasul 1: Compilați llama.cpp

Deschideți **x64 Native Tools Command Prompt** (instalat împreună cu Visual Studio Build Tools) și clonați depozitul:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Adăugați HIP la calea dumneavoastră și compilați cu suport pentru ROCm și RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Indicator de build | Scop |
|-----------|---------|
| `-DGGML_HIP=ON` | Activează stiva software ROCm/HIP |
| `-DGGML_RPC=ON` | Activează RPC pentru inferență distribuită |
| `-DGPU_TARGETS=gfx1151` | Vizează GPU-ul Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Utilizează sistemul de build Ninja |

#### Pasul 2: Verificați detectarea GPU-ului

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Rezultat așteptat:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Pasul 3: Adăugați HIP la calea de utilizator

Pasul de build de mai sus a setat `%HIP_PATH%\bin` doar pentru sesiunea curentă. Pentru a face bibliotecile HIP disponibile în orice terminal (nu doar în x64 Native Tools Command Prompt), adăugați-o permanent la `PATH`-ul dumneavoastră de utilizator:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Cu llama.cpp pregătit pe fiecare nod, continuați cu [Descărcarea modelului](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Pasul 1: Compilați llama.cpp

Clonați depozitul:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Compilați cu suport pentru ROCm și RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Indicator de build | Scop |
|-----------|---------|
| `-DGGML_HIP=ON` | Activează stiva software ROCm |
| `-DGGML_RPC=ON` | Activează RPC pentru inferență distribuită |
| `-DAMDGPU_TARGETS="gfx1151"` | Vizează GPU-ul Ryzen AI Halo (Radeon 8060s) |

Pentru mai multe opțiuni de build, consultați [documentația de build pentru llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Pasul 2: Verificați detectarea GPU-ului

```bash
cd rocm/bin
./llama-cli --list-devices
```

Rezultat așteptat:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Cu llama.cpp pregătit pe fiecare nod, continuați cu [Descărcarea modelului](#downloading-the-model).
<!-- @os:end -->

## Descărcarea modelului

Acest playbook utilizează [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), un model cu 358B parametri în cuantizarea `Q4_K_XL` de la [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). La această cuantizare, modelul necesită aproximativ 205GB de stocare și se încadrează în memoria GPU combinată a două noduri Ryzen AI Halo.

Descărcați fișierele GGUF utilizând Hugging Face CLI:
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

> **Notă**: Descărcarea modelului trebuie finalizată pe Mașina 1 (controlerul). Nodurile worker RPC nu au nevoie de o copie locală a fișierelor modelului.

## Lansarea modelului pe cluster

Motorul llama.cpp RPC (Remote Procedure Call) permite unei singure instanțe llama.cpp să descarce straturi ale modelului către workeri la distanță, prin rețea. O mașină acționează ca **controler** (Mașina 1), ocupându-se de tokenizare, planificare și orchestrare. Cealaltă mașină rulează un **server RPC** ușor (Mașina 2) care expune memoria GPU și puterea de calcul a sa controlerului.

La momentul încărcării, llama.cpp fragmentează modelul pe ambele noduri. Odată încărcat, inferența se desfășoară ca și cum ar rula pe un singur accelerator. RPC gestionează transferurile de tensori și sincronizarea în fundal.

### Pasul 1: Porniți serverul RPC (Mașina 2)

Pe Mașina 2, porniți serverul RPC pentru a expune resursele sale GPU către controler:
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

| Indicator | Scop |
|------|---------|
| `-p` | Portul pe care este difuzat serverul RPC |
| `-c` | Activează o memorie cache locală pentru tensori mari, evitând transferurile repetate prin rețea în timpul încărcării modelului |
| `--host` | Adresa IP la care se leagă serverul RPC (`0.0.0.0` pentru toate interfețele) |

Pentru mai multe opțiuni, consultați [documentația RPC pentru llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Pasul 2: Lansați modelul (Mașina 1)

Cu serverul RPC rulând pe Mașina 2, lansați inferența de pe Mașina 1 utilizând fie `llama-cli`, fie `llama-server`.
#### llama-cli

`llama-cli` oferă o interfață bazată pe terminal pentru interacțiunea directă cu modelul. Este ideală pentru benchmarking, depanare și experimentare la nivel scăzut.

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

> **Găsirea `<RPC_WORKER_IP>`**: Pe Mașina 2, rulați `hostname -I | awk '{print $1}'` pentru a găsi adresa sa IP locală.
<!-- @os:end -->

<!-- @os:windows -->
> **Notă**: Rulați această comandă în Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Găsirea `<RPC_WORKER_IP>`**: Pe Mașina 2, rulați `ipconfig | findstr /C:"IPv4"` în Terminal (Powershell) pentru a găsi adresa sa IP locală.

<!-- @os:end -->

Odată pornit, `llama-cli` afișează progresul încărcării modelului și intră într-un prompt interactiv unde puteți discuta direct cu modelul:

![llama-cli rulând GLM 4.7 pe două noduri](assets/llama-cli-example.png)

#### llama-server

`llama-server` expune același motor de inferență printr-un proces de server persistent cu o interfață web integrată și un API HTTP compatibil cu OpenAI. Aceasta este interfața preferată pentru implementări pe termen mai lung, acces multi-utilizator și integrarea cu instrumente externe.

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

> **Găsirea `<RPC_WORKER_IP>`**: Pe Mașina 2, rulați `hostname -I | awk '{print $1}'` pentru a găsi adresa sa IP locală.
<!-- @os:end -->

<!-- @os:windows -->
> **Notă**: Rulați această comandă în Terminal (Powershell).

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

> **Găsirea `<RPC_WORKER_IP>`**: Pe Mașina 2, rulați `ipconfig | findstr /C:"IPv4"` în Terminal (Powershell) pentru a găsi adresa sa IP locală.
<!-- @os:end -->

Odată pornit, deschideți `http://<HOST_IP>:8081` în browserul dvs. pentru a accesa interfața web încorporată. Aceasta oferă o interfață de chat bazată pe browser pentru interacțiunea cu modelul:

![interfața web llama-server rulând GLM 4.7 pe două noduri](assets/llama-server-example.png)

<!-- @os:linux -->
> **Găsirea `<HOST_IP>`**: Pe Mașina 1, rulați `hostname -I | awk '{print $1}'` pentru a găsi adresa sa IP locală.
<!-- @os:end -->

<!-- @os:windows -->
> **Găsirea `<HOST_IP>`**: Pe Mașina 1, rulați `ipconfig | findstr /C:"IPv4"` în Terminal (Powershell) pentru a găsi adresa sa IP locală.
<!-- @os:end -->

#### Referință parametri

| Flag | Scop |
|------|---------|
| `-m` | Calea către fișierul model GGUF (folosiți primul shard, `00001-of-00005`) |
| `-c` | Dimensiunea contextului în tokeni. Valori mai mari folosesc mai multă memorie |
| `-fa on` | Activează rocWMMA Flash Attention pentru performanță îmbunătățită pe GPU-uri AMD |
| `-ngl 999` | Transferă toate straturile modelului pe GPU |
| `-lm none` | Setează modul de încărcare a modelului la `none`, dezactivând memory-mapping pentru a reduce timpii de încărcare atunci când dimensiunea modelului depășește RAM-ul sistemului, dar încape în VRAM |
| `--host` | IP-ul la care se leagă `llama-server` (doar `llama-server`) |
| `--port` | Portul pe care se furnizează API-ul HTTP (doar `llama-server`) |
| `--rpc` | Listă separată prin virgulă a endpoint-urilor RPC worker (`IP:port`) |

Pentru utilizarea completă a parametrilor, consultați [documentația llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) și [documentația llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Pașii următori

- **Conectați aplicații terțe**: `llama-server` expune un API compatibil cu OpenAI. Îndreptați orice aplicație compatibilă cu OpenAI (precum Open WebUI) către `http://<HOST_IP>:8081` cu orice cheie API substitutivă (de exemplu, `none`) pentru a vă conecta la cluster
- **Explorați alte modele**: Răsfoiți GGUF-uri cuantizate pe [Hugging Face](https://huggingface.co/models?search=gguf) pentru a găsi modele care se încadrează în memoria GPU combinată a clusterului dvs.
- **Scalați la patru noduri**: Adăugați încă două sisteme Ryzen AI Halo ca worker-i RPC suplimentari pentru a accesa modele la scara de 1 trilion de parametri. Transmiteți endpoint-uri suplimentare către `--rpc` ca listă separată prin virgulă (de exemplu, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)