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

# Clustering a patru unități Ryzen™ AI Halo cu RPC

## Prezentare generală

Ryzen™ AI Halo poate deja rula modele de limbaj de mari dimensiuni local. Clustering-ul duce acest lucru mai departe, combinând memoria GPU a mai multor sisteme printr-o rețea locală, oferindu-vă acces la modele și mai mari, cu raționament mai puternic, generare de cod mai bună și o înțelegere multilingvă mai profundă, totul complet pe propriul hardware.

Acest ghid vă învață cum să grupați patru sisteme Ryzen AI Halo folosind motorul RPC al llama.cpp și cum să rulați Kimi K2.6, un model mare de tip mixture-of-experts, pe toate cele patru mașini cu accelerare AMD ROCm™.

## Ce veți învăța

- Cum să extindeți alocarea VRAM pe sistemele Ryzen AI Halo
- Instalarea llama.cpp cu suport ROCm și RPC
- Configurarea worker-ilor RPC și lansarea inferenței distribuite pe patru noduri
- Rularea unui model cu 1T parametri pe patru sisteme Ryzen AI Halo conectate în rețea

## Configurarea memoriei

> **Notă**: Finalizați acest pas pe toate cele patru mașini (Mașina 1 până la Mașina 4).

<!-- @os:windows -->
Pe Windows, pentru a rula modele mai mari care necesită mai multă memorie, trebuie să folosim alocarea AMD Variable Graphics Memory (iGPU VRAM).

Acest lucru se poate face deschizând panoul de control AMD Software: Adrenalin Edition și navigând la: `Performance > Tuning > AMD Variable Graphics Memory`. Setați valoarea la **96 GB**. Vă rugăm să reporniți sistemul pentru ca modificările să aibă efect.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Pe Linux, ROCm utilizează un pool de memorie de sistem partajat, iar acest pool este configurat implicit la jumătate din memoria sistemului.

Această cantitate poate fi mărită prin schimbarea setării paginii Translation Table Manager (TTM) a kernelului, urmând instrucțiunile de mai jos. AMD recomandă setarea VRAM-ului dedicat minim în BIOS (0.5 GB).

* Instalați utilitarul pipx și adăugați calea pentru wheel-urile instalate prin pipx în calea de căutare a sistemului.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalați wheel-ul amd-debug-tools din PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Rulați instrumentul amd-ttm pentru a interoga setările curente pentru memoria partajată.
  ```bash
  amd-ttm
  ```

* Reconfigurați setările de memorie partajată la **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reporniți sistemul pentru ca modificările să aibă efect.


<!-- @os:end -->
<!-- @device:halo_box -->
## Verificați actualizările software

<!-- @require:software-update -->
<!-- @device:end -->
## Cerințe preliminare

### Hardware

Acest ghid necesită patru unități Ryzen AI Halo și un switch Ethernet, conectate într-o topologie stea, fiecare unitate fiind cablată direct la switch.

| Componentă | Cantitate | Descriere |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Noduri de calcul care formează clusterul |
| Switch Ethernet 10Gbps | 1 | Switch central care permite comunicarea multi-nod Ryzen AI Halo (cel puțin 4 porturi) |
| Cablu Ethernet | 4 | Conectează fiecare unitate Halo la switch (se recomandă Cat 7 sau superior) |

> **Notă**: Sunt necesare patru porturi de switch Ethernet pentru a conecta cele patru unități Ryzen AI Halo. Este necesar un al cincilea port dacă accesați modelul de pe o mașină client separată, în loc de la una dintre unitățile Halo.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Vă rugăm să instalați:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) cu sarcina de lucru **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Configurarea hardware fizică

> **Notă**: Finalizați acest pas pe toate cele patru mașini (Mașina 1 până la Mașina 4).

Conectați fiecare unitate Ryzen AI Halo la switch-ul Ethernet folosind un cablu Cat 7 (sau superior). Aceasta stabilește legătura de 10Gbps folosită pentru comunicarea de mare viteză între noduri.
<!-- @os:linux -->
### 1. Determinarea interfețelor de rețea

Pe fiecare mașină, aflați numele interfeței de rețea și notați-l (va fi denumit mai jos `IFNAME`). Rulați:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Aceasta afișează direct numele interfeței, de exemplu:

```bash
enp191s0
```

### 2. Verificarea vitezelor legăturii de rețea

Confirmați că legătura este activă și rulează la viteză maximă verificând viteza interfeței dvs.:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Notă**: Înlocuiți `<IFNAME>` cu numele interfeței de ieșire din [1. Determinarea interfețelor de rețea](#1-determine-network-interfaces)

Ar trebui să vedeți o viteză de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Notă**: Dacă viteza este mai mică decât `10000Mb/s` sau legătura nu se activează, verificați conexiunea cablului și confirmați că portul switch-ului este setat la 10Gbps. Unele switch-uri necesită dezactivarea auto-negocierii și setarea manuală a vitezei legăturii; consultați documentația switch-ului dvs.

<!-- @os:end -->

<!-- @os:windows -->
### Verificarea vitezei legăturii de rețea

Pe fiecare mașină, verificați viteza legăturii interfețelor dvs. de rețea:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Interfața dvs. Ethernet ar trebui să fie `Up` și să ruleze la `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Notă**: Dacă viteza este mai mică decât `10 Gbps` sau legătura nu se activează, verificați conexiunea cablului și confirmați că portul switch-ului este setat la 10Gbps. Unele switch-uri necesită dezactivarea auto-negocierii și setarea manuală a vitezei legăturii; consultați documentația switch-ului dvs.

<!-- @os:end -->

## Instalarea llama.cpp

> **Notă**: Finalizați acest pas pe toate cele patru mașini (Mașina 1 până la Mașina 4).

Sunt disponibile două opțiuni de instalare:

- [Opțiunea 1: Lemonade SDK (Recomandat)](#option-1-lemonade-sdk-recommended) - binare pre-compilate, configurare cea mai rapidă
- [Opțiunea 2: Compilare manuală din sursă](#option-2-manual-source-build) - compilare din sursă cu control total asupra flag-urilor de build

### Opțiunea 1: Lemonade SDK (Recomandat)

Lemonade SDK oferă build-uri nocturne ale llama.cpp cu accelerare AMD ROCm 7, vizând GPU-uri precum gfx1151 (Strix Halo / Ryzen AI Max+ 395) și alte arhitecturi Radeon recente.

<!-- @os:windows -->
#### Pasul 1: Descărcați binarele precompilate

Accesați pagina cu cea mai recentă versiune și descărcați arhiva corespunzătoare platformei și țintei GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Descărcați fișierul numit `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (unde `xxxx` este numărul versiunii de compilare).

#### Pasul 2: Extrageți binarele

Dezarhivați arhiva descărcată:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Acest director conține acum versiuni compilate cu suport ROCm ale fișierelor `llama-cli.exe`, `llama-server.exe` și `ggml-rpc-server.exe`, precompilate pentru sistemul dumneavoastră Ryzen AI Halo.

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

Accesați pagina cu cea mai recentă versiune și descărcați arhiva corespunzătoare platformei și țintei GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Descărcați fișierul numit `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (unde `xxxx` este numărul versiunii de compilare).

#### Pasul 2: Extrageți și pregătiți binarele

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Acest director conține acum versiuni compilate cu suport ROCm ale fișierelor `llama-cli`, `llama-server` și `rpc-server`, precompilate pentru sistemul dumneavoastră Ryzen AI Halo.

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

### Opțiunea 2: Compilare manuală din surse

<!-- @os:windows -->
#### Pasul 1: Compilați llama.cpp

Deschideți **x64 Native Tools Command Prompt** (instalat împreună cu Visual Studio Build Tools) și clonați depozitul:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Adăugați HIP în calea dumneavoastră și compilați cu suport ROCm și RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Flag de compilare | Scop |
|-----------|---------|
| `-DGGML_HIP=ON` | Activează stiva software ROCm/HIP |
| `-DGGML_RPC=ON` | Activează RPC pentru inferență distribuită |
| `-DGPU_TARGETS=gfx1151` | Vizează GPU-ul Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Utilizează sistemul de compilare Ninja |

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

#### Pasul 3: Adăugați HIP în calea dumneavoastră de utilizator

Pasul de compilare de mai sus a setat `%HIP_PATH%\bin` doar pentru sesiunea curentă. Pentru a face bibliotecile HIP disponibile în orice terminal (nu doar în x64 Native Tools Command Prompt), adăugați-o permanent în `PATH`-ul de utilizator:

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

Compilați cu suport ROCm și RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Flag de compilare | Scop |
|-----------|---------|
| `-DGGML_HIP=ON` | Activează stiva software ROCm |
| `-DGGML_RPC=ON` | Activează RPC pentru inferență distribuită |
| `-DAMDGPU_TARGETS="gfx1151"` | Vizează GPU-ul Ryzen AI Halo (Radeon 8060s) |

Pentru mai multe opțiuni de compilare, consultați [documentația de compilare llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Acest ghid utilizează [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) în cuantizarea `UD-Q2_K_XL` de la [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Această cuantizare se încadrează în memoria GPU combinată a patru noduri Ryzen AI Halo.

Descărcați fișierele GGUF utilizând interfața de linie de comandă Hugging Face:
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

> **Notă**: Descărcarea modelului trebuie finalizată pe Mașina 1 (controlerul). Nodurile de lucru RPC (Mașinile 2, 3 și 4) nu au nevoie de o copie locală a fișierelor modelului.

## Lansarea modelului pe cluster

Motorul RPC (Remote Procedure Call) al llama.cpp permite unei singure instanțe llama.cpp să descarce straturile modelului către lucrători aflați la distanță, prin rețea. O mașină acționează ca **controler** (Mașina 1), gestionând tokenizarea, planificarea și orchestrarea. Celelalte trei mașini rulează fiecare un **server RPC** ușor (Mașinile 2, 3 și 4) care expune memoria GPU și puterea de calcul către controler.

La momentul încărcării, llama.cpp fragmentează modelul pe toate cele patru noduri. Odată încărcat, inferența decurge ca și cum ar rula pe un singur accelerator. RPC gestionează transferurile de tensori și sincronizarea în culise.

### Pasul 1: Porniți serverele RPC (Mașinile 2, 3 și 4)

Pe fiecare dintre Mașinile 2, 3 și 4, porniți serverul RPC pentru a expune resursele sale GPU către controler:
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

| Flag | Scop |
|------|---------|
| `-p` | Portul pe care este difuzat serverul RPC |
| `-c` | Activează o memorie cache locală pentru tensorii mari, evitând transferurile repetate prin rețea în timpul încărcării modelului |
| `--host` | Adresa IP la care este atașat serverul RPC (`0.0.0.0` pentru toate interfețele) |

Pentru mai multe opțiuni, consultați [documentația RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Pasul 2: Lansați modelul (Mașina 1)

Cu serverele RPC pornite pe Mașinile 2, 3 și 4, lansați inferența de pe Mașina 1 utilizând fie `llama-cli`, fie `llama-server`.
#### llama-cli

`llama-cli` oferă o interfață bazată pe terminal pentru interacțiunea directă cu modelul. Este ideală pentru benchmarking, depanare și experimentare la nivel scăzut.

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

> **Găsirea `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Pe fiecare dintre Mașinile 2, 3 și 4, rulați `hostname -I | awk '{print $1}'` pentru a găsi adresa IP locală.
<!-- @os:end -->

<!-- @os:windows -->
> **Notă**: Rulați această comandă în Terminal (Powershell).

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

> **Găsirea `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Pe fiecare dintre Mașinile 2, 3 și 4, rulați `ipconfig | findstr /C:"IPv4"` în Terminal (Powershell) pentru a găsi adresa IP locală.

<!-- @os:end -->

Odată pornit, `llama-cli` afișează progresul încărcării modelului și intră într-un prompt interactiv unde puteți discuta direct cu modelul:

![llama-cli rulând Kimi K2.6 pe patru noduri](assets/llama-cli-example.png)

#### llama-server

`llama-server` expune același motor de inferență printr-un proces de server persistent, cu o interfață web integrată și un API HTTP compatibil OpenAI. Aceasta este interfața preferată pentru implementări de durată mai lungă, acces multi-utilizator și integrare cu instrumente externe.

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

> **Găsirea `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Pe fiecare dintre Mașinile 2, 3 și 4, rulați `hostname -I | awk '{print $1}'` pentru a găsi adresa IP locală.
<!-- @os:end -->

<!-- @os:windows -->
> **Notă**: Rulați această comandă în Terminal (Powershell).

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

> **Găsirea `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Pe fiecare dintre Mașinile 2, 3 și 4, rulați `ipconfig | findstr /C:"IPv4"` în Terminal (Powershell) pentru a găsi adresa IP locală.
<!-- @os:end -->

Odată pornit, deschideți `http://<HOST_IP>:8081` în browser pentru a accesa interfața web integrată. Aceasta oferă o interfață de chat bazată pe browser pentru interacțiunea cu modelul:

![interfața web llama-server rulând Kimi K2.6 pe patru noduri](assets/llama-server-example.png)

<!-- @os:linux -->
> **Găsirea `<HOST_IP>`**: Pe Mașina 1, rulați `hostname -I | awk '{print $1}'` pentru a găsi adresa IP locală.
<!-- @os:end -->

<!-- @os:windows -->
> **Găsirea `<HOST_IP>`**: Pe Mașina 1, rulați `ipconfig | findstr /C:"IPv4"` în Terminal (Powershell) pentru a găsi adresa IP locală.
<!-- @os:end -->

#### Referință parametri

| Flag | Scop |
|------|---------|
| `-m` | Calea către fișierul model GGUF (utilizați primul shard, `00001-of-00008`) |
| `-c` | Dimensiunea contextului în tokeni. Valorile mai mari folosesc mai multă memorie |
| `-fa on` | Activează rocWMMA Flash Attention pentru performanță îmbunătățită pe GPU-urile AMD |
| `-ngl 999` | Descarcă toate straturile modelului pe GPU |
| `-lm none` | Setează modul de încărcare a modelului la `none`, dezactivând memory-mapping-ul pentru a reduce timpii de încărcare atunci când dimensiunea modelului depășește RAM-ul sistemului, dar încape în VRAM |
| `-b` | Dimensiunea logică a batch-ului în tokeni. Setarea la 4096 echilibrează debitul și utilizarea memoriei între noduri |
| `-ub` | Dimensiunea fizică (micro) a batch-ului pentru procesarea prompt-ului. Potrivirea cu `-b` evită overhead-ul inutil de fragmentare |
| `--host` | IP-ul la care se conectează `llama-server` (doar `llama-server`) |
| `--port` | Portul pe care este servit API-ul HTTP (doar `llama-server`) |
| `--rpc` | Listă separată prin virgulă de endpoint-uri de workeri RPC (`IP:port`) |

Pentru utilizarea completă a parametrilor, consultați [documentația llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) și [documentația llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Pașii următori

- **Conectați aplicații terțe**: `llama-server` expune un API compatibil OpenAI. Direcționați orice aplicație compatibilă OpenAI (precum Open WebUI) către `http://<HOST_IP>:8081` cu orice cheie API de tip placeholder (de ex., `none`) pentru a vă conecta la cluster
- **Explorați alte modele**: Răsfoiți GGUF-uri cuantizate pe [Hugging Face](https://huggingface.co/models?search=gguf) pentru a găsi modele care se încadrează în memoria GPU combinată a clusterului dumneavoastră
- **Extindeți dincolo de patru noduri**: Adăugați sisteme Ryzen AI Halo suplimentare ca workeri RPC adiționali pentru a accesa modele dincolo de scara de 1 trilion de parametri. Transmiteți endpoint-uri suplimentare către `--rpc` sub formă de listă separată prin virgulă (de ex., `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)