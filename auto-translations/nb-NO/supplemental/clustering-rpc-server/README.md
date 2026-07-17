<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering av to Ryzen™ AI Halos med RPC

## Oversikt

Din Ryzen™ AI Halo er allerede i stand til å kjøre store språkmodeller lokalt. Clustering tar dette videre ved å kombinere GPU-minnet fra flere systemer over et lokalt nettverk, noe som gir deg tilgang til enda større modeller med sterkere resonnering, bedre kodegenerering og dypere flerspråklig forståelse – alt helt på din egen maskinvare.

Denne playbooken lærer deg hvordan du klustrer to Ryzen AI Halo-systemer ved hjelp av llama.cpp sin RPC-motor og kjører GLM 4.7, en modell med 358 milliarder parametere, på tvers av begge maskinene med AMD ROCm™-akselerasjon.

## Hva du vil lære

- Hvordan du utvider VRAM-allokeringen på Ryzen AI Halo-systemer
- Installasjon av llama.cpp med ROCm og RPC-støtte
- Konfigurering av en RPC-arbeider og oppstart av distribuert inferens på tvers av to noder
- Kjøring av en modell med 358 milliarder parametere på tvers av to nettverkstilkoblede Ryzen AI Halo-systemer

## Angi minnekonfigurasjonen

> **Merk**: Fullfør dette trinnet på både Maskin 1 og Maskin 2.

<!-- @os:windows -->
På Windows, for å kjøre større modeller som krever mer minne, må vi bruke AMD Variable Graphics Memory (iGPU VRAM)-allokeringen.

Dette kan gjøres ved å åpne AMD Software: Adrenalin Edition-kontrollpanelet og navigere til: `Performance > Tuning > AMD Variable Graphics Memory`. Sett verdien til **96 GB**. Start systemet på nytt for at endringene skal tre i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
På Linux bruker ROCm en delt systemminnepool, og denne poolen er som standard konfigurert til halvparten av systemminnet.

Denne mengden kan økes ved å endre kjernens Translation Table Manager (TTM)-sideinnstilling, med følgende instruksjoner. AMD anbefaler å sette minimum dedikert VRAM i BIOS (0,5 GB).

* Installer pipx-verktøyet og legg til stien for pipx-installerte pakker i systemets søkesti.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installer amd-debug-tools-pakken fra PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kjør amd-ttm-verktøyet for å spørre om gjeldende innstillinger for delt minne.
  ```bash
  amd-ttm
  ```

* Rekonfigurer innstillingene for delt minne til **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Start systemet på nytt for at endringene skal tre i kraft.


<!-- @os:end -->
<!-- @device:halo_box -->
## Se etter programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->
## Forutsetninger

### Maskinvare

Denne playbooken krever to Ryzen AI Halo-enheter og én Ethernet-svitsj, koblet i en stjernetopologi der hver enhet er kablet direkte til svitsjen.

| Komponent | Antall | Beskrivelse |
|-----------|--------|-------------|
| Ryzen AI Halo | 2 | Beregningsnoder som utgjør klusteret |
| 10Gbps Ethernet-svitsj | 1 | Sentral svitsj for å muliggjøre kommunikasjon mellom flere Ryzen AI Halo-noder (minst 2 porter) |
| Ethernet-kabel | 2 | Kobler hver Halo-enhet til svitsjen (Cat 7 eller høyere anbefales) |

> **Merk**: To Ethernet-svitsjeporter kreves for å koble til de to Ryzen AI Halo-enhetene. En tredje port kreves hvis du får tilgang til modellen fra en separat klientmaskin i stedet for fra en av Halo-enhetene.

### Programvare
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Installer:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) med arbeidsmengden **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Oppsett av fysisk maskinvare

> **Merk**: Fullfør dette trinnet på både Maskin 1 og Maskin 2.

Koble hver Ryzen AI Halo-enhet til Ethernet-svitsjen med en Cat 7-kabel (eller høyere). Dette etablerer 10Gbps-forbindelsen som brukes til høyhastighets kommunikasjon mellom nodene.
<!-- @os:linux -->
### 1. Finn nettverksgrensesnitt

På hver maskin, finn navnet på nettverksgrensesnittet og noter det ned (det vil bli referert til nedenfor som `IFNAME`). Kjør:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dette skriver ut grensesnittnavnet direkte, for eksempel:

```bash
enp191s0
```

### 2. Verifiser nettverkslinkshastigheter

Bekreft at linken er aktiv og kjører med full hastighet ved å sjekke hastigheten på grensesnittet ditt:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Merk**: Erstatt `<IFNAME>` med grensesnittnavnet fra [1. Finn nettverksgrensesnitt](#1-determine-network-interfaces)

Du bør se en hastighet på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Merk**: Hvis hastigheten er lavere enn `10000Mb/s` eller linken ikke kommer opp, sjekk kabelforbindelsen og bekreft at svitsjeporten er satt til 10Gbps. Noen svitsjer krever at auto-forhandling deaktiveres og at linkshastigheten settes manuelt; se svitsjens dokumentasjon.

<!-- @os:end -->

<!-- @os:windows -->
### Verifiser nettverkslinkshastighet

På hver maskin, sjekk linkshastigheten på nettverksgrensesnittene dine:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet-grensesnittet ditt bør være `Up` og kjøre med `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Merk**: Hvis hastigheten er lavere enn `10 Gbps` eller linken ikke kommer opp, sjekk kabelforbindelsen og bekreft at svitsjeporten er satt til 10Gbps. Noen svitsjer krever at auto-forhandling deaktiveres og at linkshastigheten settes manuelt; se svitsjens dokumentasjon.

<!-- @os:end -->

## Installasjon av llama.cpp

> **Merk**: Fullfør dette trinnet på både Maskin 1 og Maskin 2.

To installasjonsalternativer er tilgjengelige:

- [Alternativ 1: Lemonade SDK (Anbefalt)](#option-1-lemonade-sdk-recommended) – forhåndsbygde binærfiler, raskest oppsett
- [Alternativ 2: Manuell kildekodebygging](#option-2-manual-source-build) – bygg fra kildekode med full kontroll over byggeflagg

### Alternativ 1: Lemonade SDK (Anbefalt)

Lemonade SDK tilbyr nattlige bygg av llama.cpp med AMD ROCm 7-akselerasjon, rettet mot GPU-er som gfx1151 (Strix Halo / Ryzen AI Max+ 395) og andre nylige Radeon-arkitekturer.

<!-- @os:windows -->
#### Trinn 1: Last ned de forhåndsbygde binærfilene

Naviger til den nyeste utgivelsessiden og last ned arkivet som samsvarer med din plattform og GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Last ned filen med navn `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (der `xxxx` er byggenummeret).

#### Trinn 2: Pakk ut binærfilene

Pakk ut det nedlastede arkivet:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Denne mappen inneholder nå ROCm-aktiverte bygg av `llama-cli.exe`, `llama-server.exe` og `rpc-server.exe`, forhåndskompilert for ditt Ryzen AI Halo-system.

#### Trinn 3: Verifiser GPU-deteksjon

```bash
.\llama-cli.exe --list-devices
```

Forventet utdata:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Trinn 1: Last ned de forhåndsbygde binærfilene

Naviger til den nyeste utgivelsessiden og last ned arkivet som samsvarer med din plattform og GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Last ned filen med navn `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (der `xxxx` er byggenummeret).

#### Trinn 2: Pakk ut og klargjør binærfilene

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Denne mappen inneholder nå ROCm-aktiverte bygg av `llama-cli`, `llama-server` og `rpc-server`, forhåndskompilert for ditt Ryzen AI Halo-system.

#### Trinn 3: Verifiser GPU-deteksjon

```bash
./llama-cli --list-devices
```

Forventet utdata:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Med llama.cpp klargjort på hver node, fortsett til [Nedlasting av modellen](#downloading-the-model).

### Alternativ 2: Manuell kildekodebygging

<!-- @os:windows -->
#### Trinn 1: Bygg llama.cpp

Åpne **x64 Native Tools Command Prompt** (installert med Visual Studio Build Tools) og klon repositoriet:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Legg til HIP i stien din og bygg med ROCm og RPC-støtte:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Byggeflagg | Formål |
|-----------|--------|
| `-DGGML_HIP=ON` | Aktiverer ROCm/HIP-programvarestakken |
| `-DGGML_RPC=ON` | Aktiverer RPC for distribuert inferens |
| `-DGPU_TARGETS=gfx1151` | Retter seg mot Ryzen AI Halo GPU (Radeon 8060s) |
| `-G Ninja` | Bruker Ninja-byggesystemet |

#### Trinn 2: Verifiser GPU-deteksjon

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Forventet utdata:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Trinn 3: Legg til HIP i brukerens sti

Byggetrinnet ovenfor satte `%HIP_PATH%\bin` kun for gjeldende økt. For å gjøre HIP-bibliotekene tilgjengelige i alle terminaler (ikke bare x64 Native Tools Command Prompt), legg det til i brukerens `PATH` permanent:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Med llama.cpp klargjort på hver node, fortsett til [Nedlasting av modellen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Trinn 1: Bygg llama.cpp

Klon repositoriet:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Bygg med ROCm og RPC-støtte:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Byggeflagg | Formål |
|-----------|--------|
| `-DGGML_HIP=ON` | Aktiverer ROCm-programvarestakken |
| `-DGGML_RPC=ON` | Aktiverer RPC for distribuert inferens |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Aktiverer rocWMMA for forbedret Flash Attention på AMD GPU-er |
| `-DAMDGPU_TARGETS="gfx1151"` | Retter seg mot Ryzen AI Halo GPU (Radeon 8060s) |

For flere byggealternativer, se [llama.cpp-byggdokumentasjonen](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Trinn 2: Verifiser GPU-deteksjon

```bash
cd rocm/bin
./llama-cli --list-devices
```

Forventet utdata:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Med llama.cpp klargjort på hver node, fortsett til [Nedlasting av modellen](#downloading-the-model).
<!-- @os:end -->

## Nedlasting av modellen

Denne playbooken bruker [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), en modell med 358 milliarder parametere i `Q4_K_XL`-kvantisering fra [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Ved denne kvantiseringen krever modellen omtrent 205 GB lagringsplass og får plass innenfor det kombinerte GPU-minnet til to Ryzen AI Halo-noder.

Last ned GGUF-filene ved hjelp av Hugging Face CLI:
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

> **Merk**: Nedlastingen av modellen må fullføres på Maskin 1 (kontrolleren). RPC-arbeidernodene trenger ikke en lokal kopi av modellfilen.

## Starte modellen på klusteret

llama.cpp sin RPC-motor (Remote Procedure Call) lar én llama.cpp-instans avlaste modellag til eksterne arbeidere over nettverket. Én maskin fungerer som **kontroller** (Maskin 1), og håndterer tokenisering, planlegging og orkestrering. Den andre maskinen kjører en lettvekts **RPC-server** (Maskin 2) som eksponerer sitt GPU-minne og sin beregningskraft for kontrolleren.

Ved innlasting deler llama.cpp modellen på tvers av begge nodene. Når den er lastet, foregår inferens som om den kjørte på én enkelt akselerator. RPC håndterer tensoroverføringer og synkronisering i bakgrunnen.

### Trinn 1: Start RPC-serveren (Maskin 2)

På Maskin 2, start RPC-serveren for å eksponere GPU-ressursene til kontrolleren:
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

| Flagg | Formål |
|-------|--------|
| `-p` | Port som RPC-serveren kringkastes på |
| `-c` | Aktiverer en lokal hurtigbuffer for store tensorer, og unngår gjentatte nettverksoverføringer under modelllasting |
| `--host` | IP-adresse som RPC-serveren bindes til (`0.0.0.0` for alle grensesnitt) |

For flere alternativer, se [llama.cpp RPC-dokumentasjonen](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Trinn 2: Start modellen (Maskin 1)

Med RPC-serveren kjørende på Maskin 2, start inferens fra Maskin 1 ved hjelp av enten `llama-cli` eller `llama-server`.

#### llama-cli

`llama-cli` gir et terminalbasert grensesnitt for direkte interaksjon med modellen. Det er ideelt for benchmarking, feilsøking og lavnivå-eksperimentering.

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

> **Finne `<RPC_WORKER_IP>`**: På Maskin 2, kjør `hostname -I | awk '{print $1}'` for å finne den lokale IP-adressen.
<!-- @os:end -->

<!-- @os:windows -->
> **Merk**: Kjør denne kommandoen i Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Finne `<RPC_WORKER_IP>`**: På Maskin 2, kjør `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for å finne den lokale IP-adressen.

<!-- @os:end -->

Når den kjører, viser `llama-cli` fremdrift for modelllasting og åpner en interaktiv ledetekst der du kan chatte direkte med modellen:

![llama-cli kjører GLM 4.7 på tvers av to noder](assets/llama-cli-example.png)

#### llama-server

`llama-server` eksponerer den samme inferensmotoren gjennom en vedvarende serverprosess med et integrert nettgrensesnitt og et OpenAI-kompatibelt HTTP API. Dette er det foretrukne grensesnittet for lengre kjøringer, flerbrukertilgang og integrasjon med eksterne verktøy.

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

> **Finne `<RPC_WORKER_IP>`**: På Maskin 2, kjør `hostname -I | awk '{print $1}'` for å finne den lokale IP-adressen.
<!-- @os:end -->

<!-- @os:windows -->
> **Merk**: Kjør denne kommandoen i Terminal (Powershell).

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

> **Finne `<RPC_WORKER_IP>`**: På Maskin 2, kjør `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for å finne den lokale IP-adressen.
<!-- @os:end -->

Når den er startet, åpne `http://<HOST_IP>:8081` i nettleseren din for å få tilgang til det innebygde nettgrensesnittet. Dette gir et nettleserbasert chat-grensesnitt for interaksjon med modellen:

![llama-server nettgrensesnitt kjører GLM 4.7 på tvers av to noder](assets/llama-server-example.png)

<!-- @os:linux -->
> **Finne `<HOST_IP>`**: På Maskin 1, kjør `hostname -I | awk '{print $1}'` for å finne den lokale IP-adressen.
<!-- @os:end -->

<!-- @os:windows -->
> **Finne `<HOST_IP>`**: På Maskin 1, kjør `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for å finne den lokale IP-adressen.
<!-- @os:end -->

#### Parameterreferanse

| Flagg | Formål |
|-------|--------|
| `-m` | Sti til GGUF-modellfilen (bruk den første delen, `00001-of-00005`) |
| `-c` | Kontekststørrelse i tokens. Større verdier bruker mer minne |
| `-fa on` | Aktiverer rocWMMA Flash Attention for forbedret ytelse på AMD GPU-er |
| `-ngl 999` | Avlaster alle modellag til GPU-en |
| `--no-mmap` | Deaktiverer minnekartlegging, noe som reduserer lastetider når modellstørrelsen overstiger system-RAM men får plass i VRAM |
| `--host` | IP som `llama-server` bindes til (kun `llama-server`) |
| `--port` | Port som HTTP API-et betjenes på (kun `llama-server`) |
| `--rpc` | Kommaseparert liste over RPC-arbeiderendepunkter (`IP:port`) |

For full parameterbruk, se [llama-cli-dokumentasjonen](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) og [llama-server-dokumentasjonen](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Neste steg

- **Koble til tredjepartsapplikasjoner**: `llama-server` eksponerer et OpenAI-kompatibelt API. Pek en hvilken som helst OpenAI-kompatibel applikasjon (som Open WebUI) mot `http://<HOST_IP>:8081` med en valgfri API-nøkkel (f.eks. `none`) for å koble til klusteret ditt
- **Utforsk andre modeller**: Bla gjennom kvantiserte GGUFer på [Hugging Face](https://huggingface.co/models?search=gguf) for å finne modeller som får plass innenfor klusterets kombinerte GPU-minne
- **Skaler til fire noder**: Legg til to flere Ryzen AI Halo-systemer som ekstra RPC-arbeidere for å få tilgang til modeller i billionparameter-skalaen. Send ytterligere endepunkter til `--rpc` som en kommaseparert liste (f.eks. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)