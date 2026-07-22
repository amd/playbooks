<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden er automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte trinn, kommandoer, nedlastinger eller produkttilgjengelighet kan variere i ditt språk eller din region. Hvis noe ser feil ut, bør du behandle den originale engelske veiledningen som den korrekte kilden.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> Denne playbooken bruker spesielle tagger som GitHub ikke kan gjengi. Besøk [amd.com/playbooks](https://amd.com/playbooks) for å forhåndsvise dette innholdet korrekt.
<!-- @github-only:end -->

# Klynging av to Ryzen™ AI Halo med RPC

## Oversikt

Din Ryzen™ AI Halo er allerede i stand til å kjøre store språkmodeller lokalt. Klynging tar dette videre ved å kombinere GPU-minnet til flere systemer over et lokalt nettverk, noe som gir deg tilgang til enda større modeller med sterkere resonnering, bedre kodegenerering og dypere flerspråklig forståelse, helt på din egen maskinvare.

Denne playbooken lærer deg hvordan du klynger to Ryzen AI Halo-systemer ved hjelp av llama.cpp sin RPC-motor og kjører GLM 4.7, en modell med 358 milliarder parametere, på tvers av begge maskinene med AMD ROCm™-akselerasjon.

## Hva du vil lære

- Hvordan utvide VRAM-tildeling på Ryzen AI Halo-systemer
- Installere llama.cpp med ROCm- og RPC-støtte
- Konfigurere en RPC-arbeider og starte distribuert inferens på tvers av to noder
- Kjøre en modell med 358 milliarder parametere på tvers av to nettverkstilkoblede Ryzen AI Halo-systemer

## Konfigurere minneinnstillingene

> **Merk**: Fullfør dette trinnet på både Maskin 1 og Maskin 2.

<!-- @os:windows -->
På Windows, for å kjøre større modeller som krever mer minne, må vi bruke AMD Variable Graphics Memory (iGPU VRAM)-tildeling.

Dette kan gjøres ved å åpne kontrollpanelet AMD Software: Adrenalin Edition og navigere til: `Performance > Tuning > AMD Variable Graphics Memory`. Sett verdien til **96 GB**. Vennligst start systemet på nytt for at endringene skal tre i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
På Linux bruker ROCm en delt systemminnepool, og denne poolen er som standard konfigurert til halvparten av systemminnet.

Denne mengden kan økes ved å endre kjernens Translation Table Manager (TTM)-sideinnstilling, med følgende instruksjoner. AMD anbefaler å sette minimum dedikert VRAM i BIOS (0,5 GB).

* Installer pipx-verktøyet og legg til stien for pipx-installerte wheels i systemets søkesti.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installer amd-debug-tools-wheelen fra PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kjør amd-ttm-verktøyet for å hente gjeldende innstillinger for delt minne.
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
## Sjekk for programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->
## Forutsetninger

### Maskinvare

Denne playbooken krever to Ryzen AI Halo-enheter og én Ethernet-svitsj, koblet sammen i en stjernetopologi der hver enhet er koblet direkte til svitsjen.

| Komponent | Antall | Beskrivelse |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Beregningsnoder som utgjør klyngen |
| 10Gbps Ethernet-svitsj | 1 | Sentral svitsj som muliggjør kommunikasjon mellom flere Ryzen AI Halo-noder (minst 2 porter) |
| Ethernet-kabel | 2 | Kobler hver Halo-enhet til svitsjen (Cat 7 eller høyere anbefales) |

> **Merk**: To porter på Ethernet-svitsjen er nødvendig for å koble sammen de to Ryzen AI Halo-enhetene. En tredje port er nødvendig hvis du får tilgang til modellen fra en separat klientmaskin i stedet for fra én av Halo-enhetene.

### Programvare
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Vennligst installer:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) med arbeidsbelastningen **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fysisk maskinvareoppsett

> **Merk**: Fullfør dette trinnet på både Maskin 1 og Maskin 2.

Koble hver Ryzen AI Halo-enhet til Ethernet-svitsjen med en Cat 7 (eller høyere) kabel. Dette etablerer 10Gbps-koblingen som brukes for høyhastighetskommunikasjon mellom nodene.
<!-- @os:linux -->
### 1. Bestem nettverksgrensesnitt

På hver maskin, finn navnet på nettverksgrensesnittet og noter det ned (det vil bli omtalt nedenfor som `IFNAME`). Kjør:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dette skriver ut grensesnittnavnet direkte, for eksempel:

```bash
enp191s0
```

### 2. Bekreft nettverkslinkhastigheter

Bekreft at koblingen er aktiv og kjører med full hastighet ved å sjekke hastigheten til grensesnittet ditt:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Merk**: Erstatt `<IFNAME>` med grensesnittnavnet fra utdataen i [1. Bestem nettverksgrensesnitt](#1-determine-network-interfaces)

Du bør se en hastighet på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Merk**: Hvis hastigheten er lavere enn `10000Mb/s`, eller koblingen ikke kommer opp, sjekk kabeltilkoblingen og bekreft at svitsjporten er satt til 10Gbps. Enkelte svitsjer krever at auto-forhandling deaktiveres og linkhastigheten settes manuelt; se dokumentasjonen for svitsjen din.

<!-- @os:end -->

<!-- @os:windows -->
### Bekreft nettverkslinkhastighet

På hver maskin, sjekk linkhastigheten til nettverksgrensesnittene dine:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet-grensesnittet ditt bør være `Up` og kjøre med `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Merk**: Hvis hastigheten er lavere enn `10 Gbps`, eller koblingen ikke kommer opp, sjekk kabeltilkoblingen og bekreft at svitsjporten er satt til 10Gbps. Enkelte svitsjer krever at auto-forhandling deaktiveres og linkhastigheten settes manuelt; se dokumentasjonen for svitsjen din.

<!-- @os:end -->

## Installere llama.cpp

> **Merk**: Fullfør dette trinnet på både Maskin 1 og Maskin 2.

To installasjonsalternativer er tilgjengelige:

- [Alternativ 1: Lemonade SDK (anbefalt)](#option-1-lemonade-sdk-recommended) - ferdigbygde binærfiler, raskeste oppsett
- [Alternativ 2: Manuell kildekodebygging](#option-2-manual-source-build) - bygg fra kildekode med full kontroll over byggeflagg

### Alternativ 1: Lemonade SDK (anbefalt)

Lemonade SDK tilbyr nattlige bygg av llama.cpp med AMD ROCm 7-akselerasjon, rettet mot GPU-er som gfx1151 (Strix Halo / Ryzen AI Max+ 395) og andre nyere Radeon-arkitekturer.

<!-- @os:windows -->
#### Trinn 1: Last ned de forhåndsbygde binærfilene

Naviger til den nyeste utgivelsessiden og last ned arkivet som samsvarer med din plattform og GPU-mål:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Last ned filen med navnet `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (der `xxxx` er byggenummeret).

#### Trinn 2: Pakk ut binærfilene

Pakk ut det nedlastede arkivet:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Denne mappen inneholder nå ROCm-aktiverte bygg av `llama-cli.exe`, `llama-server.exe` og `rpc-server.exe`, forhåndskompilert for ditt Ryzen AI Halo-system.

#### Trinn 3: Bekreft GPU-gjenkjenning

```bash
.\llama-cli.exe --list-devices
```

Forventet resultat:

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

Last ned filen med navnet `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (der `xxxx` er byggenummeret).

#### Trinn 2: Pakk ut og klargjør binærfilene

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Denne mappen inneholder nå ROCm-aktiverte bygg av `llama-cli`, `llama-server` og `rpc-server`, forhåndskompilert for ditt Ryzen AI Halo-system.

#### Trinn 3: Bekreft GPU-gjenkjenning

```bash
./llama-cli --list-devices
```

Forventet resultat:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Når llama.cpp er klargjort på hver node, fortsett til [Nedlasting av modellen](#downloading-the-model).

### Alternativ 2: Manuell kildebygging

<!-- @os:windows -->
#### Trinn 1: Bygg llama.cpp

Åpne **x64 Native Tools Command Prompt** (installert med Visual Studio Build Tools) og klon depotet:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Legg til HIP i banen din og bygg med støtte for ROCm og RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Byggeflagg | Formål |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiverer ROCm/HIP-programvarestakken |
| `-DGGML_RPC=ON` | Aktiverer RPC for distribuert inferens |
| `-DGPU_TARGETS=gfx1151` | Retter seg mot Ryzen AI Halo-GPU-en (Radeon 8060s) |
| `-G Ninja` | Bruker Ninja-byggesystemet |

#### Trinn 2: Bekreft GPU-gjenkjenning

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Forventet resultat:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Trinn 3: Legg HIP til i brukerbanen din

Byggetrinnet ovenfor satte `%HIP_PATH%\bin` kun for gjeldende økt. For å gjøre HIP-bibliotekene tilgjengelige i en hvilken som helst terminal (ikke bare x64 Native Tools Command Prompt), må du legge det permanent til i brukerens `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Når llama.cpp er klargjort på hver node, fortsett til [Nedlasting av modellen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Trinn 1: Bygg llama.cpp

Klon depotet:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Bygg med støtte for ROCm og RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Byggeflagg | Formål |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiverer ROCm-programvarestakken |
| `-DGGML_RPC=ON` | Aktiverer RPC for distribuert inferens |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Aktiverer rocWMMA for forbedret Flash Attention på AMD-GPU-er |
| `-DAMDGPU_TARGETS="gfx1151"` | Retter seg mot Ryzen AI Halo-GPU-en (Radeon 8060s) |

For flere byggealternativer, se [byggedokumentasjonen for llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Trinn 2: Bekreft GPU-gjenkjenning

```bash
cd rocm/bin
./llama-cli --list-devices
```

Forventet resultat:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Når llama.cpp er klargjort på hver node, fortsett til [Nedlasting av modellen](#downloading-the-model).
<!-- @os:end -->

## Nedlasting av modellen

Denne oppskriften bruker [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), en modell med 358 milliarder parametere i `Q4_K_XL`-kvantiseringen fra [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Ved denne kvantiseringen krever modellen omtrent 205 GB lagringsplass og passer innenfor den kombinerte GPU-minnekapasiteten til to Ryzen AI Halo-noder.

Last ned GGUF-filene ved hjelp av Hugging Face-CLI-en:
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

> **Merk**: Modellnedlastingen må fullføres på Maskin 1 (kontrolleren). RPC-arbeidernodene trenger ikke en lokal kopi av modellfilene.

## Starte modellen på klyngen

llama.cpp RPC-motoren (Remote Procedure Call) lar en enkelt llama.cpp-instans avlaste modellag til eksterne arbeidere over nettverket. Én maskin fungerer som **kontrolleren** (Maskin 1), og håndterer tokenisering, planlegging og orkestrering. Den andre maskinen kjører en lettvekts **RPC-server** (Maskin 2) som eksponerer sitt GPU-minne og beregningskraft til kontrolleren.

Ved lastetidspunktet fordeler llama.cpp modellen på tvers av begge nodene. Når modellen er lastet, foregår inferens som om den kjører på én enkelt akselerator. RPC håndterer tensoroverføringer og synkronisering bak kulissene.

### Trinn 1: Start RPC-serveren (Maskin 2)

På Maskin 2, start RPC-serveren for å eksponere sine GPU-ressurser til kontrolleren:
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
|------|---------|
| `-p` | Port RPC-serveren kringkastes på |
| `-c` | Aktiverer en lokal cache for store tensorer, som unngår gjentatte nettverksoverføringer under modellasting |
| `--host` | IP-adresse som RPC-serveren skal bindes til (`0.0.0.0` for alle grensesnitt) |

For flere alternativer, se [RPC-dokumentasjonen for llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Trinn 2: Start modellen (Maskin 1)

Med RPC-serveren kjørende på Maskin 2, start inferens fra Maskin 1 med enten `llama-cli` eller `llama-server`.

#### llama-cli

`llama-cli` tilbyr et terminalbasert grensesnitt for direkte samhandling med modellen. Det er ideelt for benchmarking, feilsøking og eksperimentering på lavt nivå.

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

> **Finne `<RPC_WORKER_IP>`**: På Maskin 2, kjør `hostname -I | awk '{print $1}'` for å finne dens lokale IP-adresse.
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

> **Finne `<RPC_WORKER_IP>`**: På Maskin 2, kjør `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for å finne dens lokale IP-adresse.

<!-- @os:end -->

Når den kjører, viser `llama-cli` fremdriften for modellasting og går inn i en interaktiv ledetekst der du kan chatte direkte med modellen:

![llama-cli som kjører GLM 4.7 på tvers av to noder](assets/llama-cli-example.png)
#### llama-server

`llama-server` eksponerer den samme inferensmotoren gjennom en persistent serverprosess med et integrert web-UI og et OpenAI-kompatibelt HTTP-API. Dette er det foretrukne grensesnittet for lengre driftsperioder, tilgang for flere brukere og integrasjon med eksterne verktøy.

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

> **Finne `<RPC_WORKER_IP>`**: På maskin 2 kjører du `hostname -I | awk '{print $1}'` for å finne den lokale IP-adressen.
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

> **Finne `<RPC_WORKER_IP>`**: På maskin 2 kjører du `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for å finne den lokale IP-adressen.
<!-- @os:end -->

Når den er startet, åpne `http://<HOST_IP>:8081` i nettleseren for å få tilgang til det innebygde web-UI-et. Dette gir et nettleserbasert chattegrensesnitt for å interagere med modellen:

![llama-server web-UI som kjører GLM 4.7 på tvers av to noder](assets/llama-server-example.png)

<!-- @os:linux -->
> **Finne `<HOST_IP>`**: På maskin 1 kjører du `hostname -I | awk '{print $1}'` for å finne den lokale IP-adressen.
<!-- @os:end -->

<!-- @os:windows -->
> **Finne `<HOST_IP>`**: På maskin 1 kjører du `ipconfig | findstr /C:"IPv4"` i Terminal (Powershell) for å finne den lokale IP-adressen.
<!-- @os:end -->

#### Parameterreferanse

| Flagg | Formål |
|------|---------|
| `-m` | Sti til GGUF-modellfilen (bruk det første fragmentet, `00001-of-00005`) |
| `-c` | Kontekststørrelse i tokens. Større verdier bruker mer minne |
| `-fa on` | Aktiverer rocWMMA Flash Attention for forbedret ytelse på AMD-GPU-er |
| `-ngl 999` | Overfører alle modellag til GPU-en |
| `--no-mmap` | Deaktiverer minneprojisering, noe som reduserer lastetider når modellstørrelsen overstiger systemets RAM, men får plass i VRAM |
| `--host` | IP å binde `llama-server` til (kun `llama-server`) |
| `--port` | Port for å tilby HTTP-API-et på (kun `llama-server`) |
| `--rpc` | Kommaseparert liste over RPC-arbeidsendepunkter (`IP:port`) |

For fullstendig parameterbruk, se [llama-cli-dokumentasjonen](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) og [llama-server-dokumentasjonen](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Neste steg

- **Koble til tredjepartsapplikasjoner**: `llama-server` eksponerer et OpenAI-kompatibelt API. Pek en hvilken som helst OpenAI-kompatibel applikasjon (som Open WebUI) mot `http://<HOST_IP>:8081` med en vilkårlig plassholder-API-nøkkel (f.eks. `none`) for å koble til klyngen din
- **Utforsk andre modeller**: Bla gjennom kvantiserte GGUF-er på [Hugging Face](https://huggingface.co/models?search=gguf) for å finne modeller som får plass innenfor klyngens samlede GPU-minne
- **Skaler til fire noder**: Legg til to ekstra Ryzen AI Halo-systemer som ytterligere RPC-arbeidere for å få tilgang til modeller i skalaen 1 billion parametere. Send flere endepunkter til `--rpc` som en kommaseparert liste (f.eks. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)