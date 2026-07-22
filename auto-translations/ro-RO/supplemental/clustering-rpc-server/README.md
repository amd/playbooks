<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din engleză și nu a fost revizuită de o persoană. Poate conține erori, iar unii pași, comenzi, descărcări sau disponibilitatea produselor pot diferi în funcție de limba sau regiunea dumneavoastră. Dacă ceva pare incorect, considerați playbook-ul original în limba engleză drept sursă de referință.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> Acest playbook folosește etichete speciale pe care GitHub nu le poate reda. Vă rugăm să vizitați [amd.com/playbooks](https://amd.com/playbooks) pentru a previzualiza corect acest conținut.
<!-- @github-only:end -->

# Clusterizarea a Două Sisteme Ryzen™ AI Halo cu RPC

## Prezentare Generală

Sistemul dumneavoastră Ryzen™ AI Halo este deja capabil să ruleze modele lingvistice mari la nivel local. Clusterizarea duce acest lucru mai departe, combinând memoria GPU a mai multor sisteme printr-o rețea locală, oferindu-vă acces la modele și mai mari, cu raționament mai puternic, generare de cod mai bună și o înțelegere multilingvă mai profundă, totul complet pe propriul dumneavoastră hardware.

Acest playbook vă învață cum să clusterizați două sisteme Ryzen AI Halo folosind motorul RPC al llama.cpp și cum să rulați GLM 4.7, un model cu 358 de miliarde de parametri, pe ambele mașini cu accelerare AMD ROCm™.

## Ce Veți Învăța

- Cum să extindeți alocarea VRAM pe sistemele Ryzen AI Halo
- Instalarea llama.cpp cu suport ROCm și RPC
- Configurarea unui worker RPC și lansarea inferenței distribuite pe două noduri
- Rularea unui model cu 358 de miliarde de parametri pe două sisteme Ryzen AI Halo conectate în rețea

## Configurarea Memoriei

> **Notă**: Finalizați acest pas atât pe Mașina 1, cât și pe Mașina 2.

<!-- @os:windows -->
Pe Windows, pentru a rula modele mai mari care necesită mai multă memorie, trebuie să folosim alocarea AMD Variable Graphics Memory (iGPU VRAM).

Acest lucru se poate face deschizând panoul de control AMD Software: Adrenalin Edition și navigând la: `Performance > Tuning > AMD Variable Graphics Memory`. Setați valoarea la **96 GB**. Vă rugăm să reporniți sistemul pentru ca modificările să aibă efect.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Pe Linux, ROCm utilizează un pool de memorie de sistem partajat, iar acest pool este configurat implicit la jumătate din memoria sistemului.

Această valoare poate fi mărită modificând setarea paginilor Translation Table Manager (TTM) a kernelului, conform instrucțiunilor de mai jos. AMD recomandă setarea VRAM-ului dedicat minim în BIOS (0,5 GB).

* Instalați utilitarul pipx și adăugați calea pentru wheel-urile instalate de pipx în calea de căutare a sistemului.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalați pachetul wheel amd-debug-tools de pe PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Rulați instrumentul amd-ttm pentru a interoga setările curente ale memoriei partajate.
  ```bash
  amd-ttm
  ```

* Reconfigurați setările memoriei partajate la **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reporniți sistemul pentru ca modificările să aibă efect.


<!-- @os:end -->
<!-- @device:halo_box -->
## Verificați Actualizările de Software

<!-- @require:software-update -->
<!-- @device:end -->
## Cerințe Preliminare

### Hardware

Acest playbook necesită două unități Ryzen AI Halo și un switch Ethernet, conectate într-o topologie stea, fiecare unitate fiind conectată direct la switch.

| Componentă | Cantitate | Descriere |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Noduri de calcul care formează clusterul |
| Switch Ethernet 10Gbps | 1 | Switch central care permite comunicarea multi-nod Ryzen AI Halo (cel puțin 2 porturi) |
| Cablu Ethernet | 2 | Conectează fiecare unitate Halo la switch (se recomandă Cat 7 sau superior) |

> **Notă**: Sunt necesare două porturi de switch Ethernet pentru a conecta cele două unități Ryzen AI Halo. Un al treilea port este necesar dacă accesați modelul dintr-o mașină client separată, în loc de una dintre unitățile Halo.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Vă rugăm să instalați:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) cu sarcina de lucru **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Configurarea Fizică a Hardware-ului

> **Notă**: Finalizați acest pas atât pe Mașina 1, cât și pe Mașina 2.

Conectați fiecare unitate Ryzen AI Halo la switch-ul Ethernet folosind un cablu Cat 7 (sau superior). Aceasta stabilește legătura de 10Gbps utilizată pentru comunicarea de mare viteză între noduri.
<!-- @os:linux -->
### 1. Determinarea Interfețelor de Rețea

Pe fiecare mașină, aflați numele interfeței sale de rețea și notați-l (va fi denumit mai jos `IFNAME`). Rulați:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Aceasta afișează direct numele interfeței, de exemplu:

```bash
enp191s0
```

### 2. Verificarea Vitezelor Legăturii de Rețea

Confirmați că legătura este activă și rulează la viteză maximă verificând viteza interfeței dumneavoastră:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Notă**: Înlocuiți `<IFNAME>` cu numele interfeței de ieșire din [1. Determinarea Interfețelor de Rețea](#1-determine-network-interfaces)

Ar trebui să vedeți o viteză de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Notă**: Dacă viteza este mai mică de `10000Mb/s` sau legătura nu se stabilește, verificați conexiunea cablului și confirmați că portul switch-ului este setat la 10Gbps. Unele switch-uri necesită dezactivarea auto-negocierii și setarea manuală a vitezei legăturii; consultați documentația switch-ului dumneavoastră.

<!-- @os:end -->

<!-- @os:windows -->
### Verificarea Vitezei Legăturii de Rețea

Pe fiecare mașină, verificați viteza legăturii interfețelor dumneavoastră de rețea:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Interfața dumneavoastră Ethernet ar trebui să fie `Up` și să ruleze la `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Notă**: Dacă viteza este mai mică de `10 Gbps` sau legătura nu se stabilește, verificați conexiunea cablului și confirmați că portul switch-ului este setat la 10Gbps. Unele switch-uri necesită dezactivarea auto-negocierii și setarea manuală a vitezei legăturii; consultați documentația switch-ului dumneavoastră.

<!-- @os:end -->

## Instalarea llama.cpp

> **Notă**: Finalizați acest pas atât pe Mașina 1, cât și pe Mașina 2.

Sunt disponibile două opțiuni de instalare:

- [Opțiunea 1: Lemonade SDK (Recomandat)](#option-1-lemonade-sdk-recommended) - binare precompilate, configurare cea mai rapidă
- [Opțiunea 2: Compilare Manuală din Sursă](#option-2-manual-source-build) - compilare din sursă cu control complet asupra opțiunilor de compilare

### Opțiunea 1: Lemonade SDK (Recomandat)

Lemonade SDK oferă versiuni nocturne (nightly builds) ale llama.cpp cu accelerare AMD ROCm 7, vizând GPU-uri precum gfx1151 (Strix Halo / Ryzen AI Max+ 395) și alte arhitecturi Radeon recente.

<!-- @os:windows -->
#### Pasul 1: Descărcați binarele precompilate

Navigați la pagina celei mai recente versiuni și descărcați arhiva corespunzătoare platformei și țintei GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Descărcați fișierul denumit `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (unde `xxxx` reprezintă numărul versiunii de build).

#### Pasul 2: Extrageți binarele

Dezarhivați arhiva descărcată:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Acest director conține acum versiunile compilate cu suport ROCm ale fișierelor `llama-cli.exe`, `llama-server.exe` și `rpc-server.exe`, precompilate pentru sistemul dumneavoastră Ryzen AI Halo.

#### Pasul 3: Verificați detectarea GPU

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

Navigați la pagina celei mai recente versiuni și descărcați arhiva corespunzătoare platformei și țintei GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Descărcați fișierul denumit `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (unde `xxxx` reprezintă numărul versiunii de build).

#### Pasul 2: Extrageți și pregătiți binarele

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Acest director conține acum versiunile compilate cu suport ROCm ale fișierelor `llama-cli`, `llama-server` și `rpc-server`, precompilate pentru sistemul dumneavoastră Ryzen AI Halo.

#### Pasul 3: Verificați detectarea GPU

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
După ce llama.cpp a fost pregătit pe fiecare nod, continuați cu [Descărcarea modelului](#downloading-the-model).

### Opțiunea 2: Compilare manuală din sursă

<!-- @os:windows -->
#### Pasul 1: Compilați llama.cpp

Deschideți **x64 Native Tools Command Prompt** (instalat împreună cu Visual Studio Build Tools) și clonați depozitul:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Adăugați HIP la calea dumneavoastră (path) și compilați cu suport ROCm și RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Indicator de compilare | Scop |
|-----------|---------|
| `-DGGML_HIP=ON` | Activează stiva de software ROCm/HIP |
| `-DGGML_RPC=ON` | Activează RPC pentru inferență distribuită |
| `-DGPU_TARGETS=gfx1151` | Vizează GPU-ul Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Utilizează sistemul de compilare Ninja |

#### Pasul 2: Verificați detectarea GPU

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

#### Pasul 3: Adăugați HIP la calea de utilizator (User Path)

Pasul de compilare de mai sus a setat `%HIP_PATH%\bin` doar pentru sesiunea curentă. Pentru a face bibliotecile HIP disponibile în orice terminal (nu doar în x64 Native Tools Command Prompt), adăugați-l permanent la `PATH`-ul de utilizator:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

După ce llama.cpp a fost pregătit pe fiecare nod, continuați cu [Descărcarea modelului](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Pasul 1: Compilați llama.cpp

Clonați depozitul:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Compilați cu suport ROCm și RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Indicator de compilare | Scop |
|-----------|---------|
| `-DGGML_HIP=ON` | Activează stiva de software ROCm |
| `-DGGML_RPC=ON` | Activează RPC pentru inferență distribuită |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Activează rocWMMA pentru Flash Attention îmbunătățit pe GPU-uri AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Vizează GPU-ul Ryzen AI Halo (Radeon 8060s) |

Pentru mai multe opțiuni de compilare, consultați [documentația de compilare llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Pasul 2: Verificați detectarea GPU

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

După ce llama.cpp a fost pregătit pe fiecare nod, continuați cu [Descărcarea modelului](#downloading-the-model).
<!-- @os:end -->

## Descărcarea modelului

Acest ghid utilizează [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), un model cu 358 de miliarde de parametri, în cuantizarea `Q4_K_XL` de la [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). La această cuantizare, modelul necesită aproximativ 205 GB de spațiu de stocare și încape în memoria GPU combinată a două noduri Ryzen AI Halo.

Descărcați fișierele GGUF utilizând CLI-ul Hugging Face:
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

> **Notă**: Descărcarea modelului trebuie finalizată pe Mașina 1 (controlerul). Nodurile RPC worker nu au nevoie de o copie locală a fișierelor modelului.

## Lansarea modelului pe cluster

Motorul RPC (Remote Procedure Call) al llama.cpp permite unei singure instanțe llama.cpp să delege straturile modelului către workeri de la distanță, prin rețea. O mașină acționează ca **controler** (Mașina 1), gestionând tokenizarea, planificarea și orchestrarea. Cealaltă mașină rulează un **server RPC** ușor (Mașina 2), care expune memoria GPU și puterea de calcul către controler.

La încărcare, llama.cpp fragmentează modelul pe ambele noduri. Odată încărcat, inferența se desfășoară ca și cum ar rula pe un singur accelerator. RPC gestionează transferurile de tensori și sincronizarea în fundal.

### Pasul 1: Porniți serverul RPC (Mașina 2)

Pe Mașina 2, porniți serverul RPC pentru a expune resursele sale GPU către controler:
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

| Indicator | Scop |
|------|---------|
| `-p` | Portul pe care este difuzat serverul RPC |
| `-c` | Activează un cache local pentru tensorii mari, evitând transferurile repetate prin rețea în timpul încărcării modelului |
| `--host` | Adresa IP la care este legat serverul RPC (`0.0.0.0` pentru toate interfețele) |

Pentru mai multe opțiuni, consultați [documentația RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Pasul 2: Lansați modelul (Mașina 1)

Cu serverul RPC rulând pe Mașina 2, lansați inferența de pe Mașina 1 utilizând fie `llama-cli`, fie `llama-server`.

#### llama-cli

`llama-cli` oferă o interfață bazată pe terminal pentru a interacționa direct cu modelul. Este ideală pentru benchmarking, depanare și experimentare la nivel de bază.

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
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Găsirea `<RPC_WORKER_IP>`**: Pe Mașina 2, rulați `ipconfig | findstr /C:"IPv4"` în Terminal (Powershell) pentru a găsi adresa sa IP locală.

<!-- @os:end -->

După pornire, `llama-cli` afișează progresul încărcării modelului și intră într-un prompt interactiv unde puteți conversa direct cu modelul:

![llama-cli rulând GLM 4.7 pe două noduri](assets/llama-cli-example.png)
#### llama-server

`llama-server` expune același motor de inferență printr-un proces de server persistent, cu o interfață web integrată și un API HTTP compatibil cu OpenAI. Aceasta este interfața preferată pentru implementări de durată mai lungă, acces multi-utilizator și integrare cu instrumente externe.

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
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Găsirea `<RPC_WORKER_IP>`**: Pe Mașina 2, rulați `ipconfig | findstr /C:"IPv4"` în Terminal (Powershell) pentru a găsi adresa sa IP locală.
<!-- @os:end -->

După pornire, deschideți `http://<HOST_IP>:8081` în browser pentru a accesa interfața web integrată. Aceasta oferă o interfață de chat bazată pe browser pentru interacțiunea cu modelul:

![Interfața web llama-server rulând GLM 4.7 pe două noduri](assets/llama-server-example.png)

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
| `-c` | Dimensiunea contextului în tokeni. Valorile mai mari folosesc mai multă memorie |
| `-fa on` | Activează rocWMMA Flash Attention pentru performanțe îmbunătățite pe GPU-uri AMD |
| `-ngl 999` | Delegă toate straturile modelului către GPU |
| `--no-mmap` | Dezactivează maparea memoriei, reducând timpii de încărcare atunci când dimensiunea modelului depășește RAM-ul sistemului, dar încape în VRAM |
| `--host` | IP-ul la care este atașat `llama-server` (doar `llama-server`) |
| `--port` | Portul pe care este servit API-ul HTTP (doar `llama-server`) |
| `--rpc` | Listă separată prin virgulă a punctelor finale ale workerilor RPC (`IP:port`) |

Pentru utilizarea completă a parametrilor, consultați [documentația llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) și [documentația llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Pași următori

- **Conectați aplicații terțe**: `llama-server` expune un API compatibil cu OpenAI. Îndreptați orice aplicație compatibilă cu OpenAI (cum ar fi Open WebUI) către `http://<HOST_IP>:8081` cu orice cheie API de tip placeholder (de ex., `none`) pentru a vă conecta la cluster
- **Explorați alte modele**: Răsfoiți fișierele GGUF cuantizate pe [Hugging Face](https://huggingface.co/models?search=gguf) pentru a găsi modele care se încadrează în memoria GPU combinată a clusterului dumneavoastră
- **Extindeți la patru noduri**: Adăugați încă două sisteme Ryzen AI Halo ca workeri RPC suplimentari pentru a accesa modele la scara de 1 trilion de parametri. Transmiteți puncte finale suplimentare către `--rpc` sub forma unei liste separate prin virgulă (de ex., `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)