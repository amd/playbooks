<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Klasterovanje dva Ryzen™ AI Halo sistema pomoću RPC-a

## Pregled

Vaš Ryzen™ AI Halo sistem je već sposoban da lokalno pokreće velike jezičke modele. Klasterovanje ovo dodatno unapređuje kombinovanjem GPU memorije više sistema preko lokalne mreže, omogućavajući vam pristup još većim modelima sa jačim rezonovanjem, boljom generacijom koda i dubljim razumevanjem više jezika, potpuno na sopstvenom hardveru.

Ovaj vodič vas uči kako da klasterujete dva Ryzen AI Halo sistema koristeći llama.cpp RPC mehanizam i pokrenete GLM 4.7, model sa 358 milijardi parametara, na obe mašine uz AMD ROCm™ akceleraciju.

## Šta ćete naučiti

- Kako da proširite alokaciju VRAM-a na Ryzen AI Halo sistemima
- Instaliranje llama.cpp sa ROCm i RPC podrškom
- Konfigurisanje RPC radnog procesa i pokretanje distribuiranog zaključivanja na dva čvora
- Pokretanje modela sa 358 milijardi parametara na dva umrežena Ryzen AI Halo sistema

## Podešavanje konfiguracije memorije

> **Napomena**: Ovaj korak izvršite i na Mašini 1 i na Mašini 2.

<!-- @os:windows -->
Na Windows-u, da bismo pokretali veće modele koji zahtevaju više memorije, potrebno je da koristimo AMD Variable Graphics Memory (iGPU VRAM) alokaciju.

Ovo se može uraditi otvaranjem kontrolne table AMD Software: Adrenalin Edition i navigacijom do: `Performance > Tuning > AMD Variable Graphics Memory`. Podesite vrednost na **96 GB**. Molimo restartujte sistem da bi izmene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Na Linux-u, ROCm koristi deljeni pool sistemske memorije, a ovaj pool je podrazumevano konfigurisan na polovinu sistemske memorije.

Ova količina se može povećati promenom podešavanja stranica u kernel Translation Table Manager-u (TTM), prateći sledeća uputstva. AMD preporučuje da se u BIOS-u podesi minimalna namenska VRAM memorija (0.5 GB).

* Instalirajte pipx alat i dodajte putanju za pipx instalirane wheel pakete u sistemsku putanju za pretragu.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalirajte amd-debug-tools wheel paket sa PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Pokrenite amd-ttm alat da biste proverili trenutna podešavanja za deljenu memoriju.
  ```bash
  amd-ttm
  ```

* Rekonfigurišite podešavanja deljene memorije na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte sistem da bi izmene stupile na snagu.


<!-- @os:end -->
<!-- @device:halo_box -->
## Proverite ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->
## Preduslovi

### Hardver

Ovaj vodič zahteva dve Ryzen AI Halo jedinice i jedan Ethernet svič, povezane u zvezda topologiji sa svakom jedinicom direktno povezanom kablom na svič.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računski čvorovi koji čine klaster |
| 10Gbps Ethernet svič | 1 | Centralni svič koji omogućava komunikaciju više Ryzen AI Halo čvorova (najmanje 2 porta) |
| Ethernet kabl | 2 | Povezuje svaku Halo jedinicu sa svičem (preporučuje se Cat 7 ili viši) |

> **Napomena**: Potrebna su dva porta na Ethernet sviču da bi se povezale dve Ryzen AI Halo jedinice. Treći port je potreban ukoliko modelu pristupate sa posebne klijentske mašine, umesto sa jedne od Halo jedinica.

### Softver
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Molimo instalirajte:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) sa radnim opterećenjem **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizičko postavljanje hardvera

> **Napomena**: Ovaj korak izvršite i na Mašini 1 i na Mašini 2.

Povežite svaku Ryzen AI Halo jedinicu sa Ethernet svičem koristeći Cat 7 (ili viši) kabl. Ovo uspostavlja 10Gbps vezu koja se koristi za brzu komunikaciju između čvorova.
<!-- @os:linux -->
### 1. Utvrđivanje mrežnih interfejsa

Na svakoj mašini pronađite ime njenog mrežnog interfejsa i zabeležite ga (u nastavku će se pominjati kao `IFNAME`). Pokrenite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ovo direktno ispisuje ime interfejsa, na primer:

```bash
enp191s0
```

### 2. Provera brzine mrežne veze

Potvrdite da je veza aktivna i da radi punom brzinom proverom brzine vašeg interfejsa:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Napomena**: Zamenite `<IFNAME>` sa izlaznim imenom interfejsa iz [1. Utvrđivanje mrežnih interfejsa](#1-determine-network-interfaces)

Trebalo bi da vidite brzinu od `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Napomena**: Ako je brzina manja od `10000Mb/s` ili veza ne uspostavlja, proverite kablovsku vezu i potvrdite da je port na sviču podešen na 10Gbps. Neki svičevi zahtevaju da se auto-negotiation isključi i brzina veze ručno podesi; pogledajte dokumentaciju svog sviča.

<!-- @os:end -->

<!-- @os:windows -->
### Provera brzine mrežne veze

Na svakoj mašini proverite brzinu veze vaših mrežnih interfejsa:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš Ethernet interfejs bi trebalo da bude `Up` i da radi na `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Napomena**: Ako je brzina manja od `10 Gbps` ili veza ne uspostavlja, proverite kablovsku vezu i potvrdite da je port na sviču podešen na 10Gbps. Neki svičevi zahtevaju da se auto-negotiation isključi i brzina veze ručno podesi; pogledajte dokumentaciju svog sviča.

<!-- @os:end -->

## Instaliranje llama.cpp

> **Napomena**: Ovaj korak izvršite i na Mašini 1 i na Mašini 2.

Dostupne su dve opcije instalacije:

- [Opcija 1: Lemonade SDK (preporučeno)](#option-1-lemonade-sdk-recommended) - unapred izgrađene binarne datoteke, najbrže podešavanje
- [Opcija 2: Ručna izgradnja iz izvornog koda](#option-2-manual-source-build) - izgradnja iz izvornog koda sa punom kontrolom nad opcijama izgradnje

### Opcija 1: Lemonade SDK (preporučeno)

Lemonade SDK pruža noćne (nightly) verzije llama.cpp sa AMD ROCm 7 akceleracijom, namenjene GPU-ovima kao što je gfx1151 (Strix Halo / Ryzen AI Max+ 395) i drugim novijim Radeon arhitekturama.

<!-- @os:windows -->
#### Korak 1: Preuzimanje unapred izgrađenih binarnih fajlova

Idite na stranicu najnovijeg izdanja i preuzmite arhivu koja odgovara vašoj platformi i GPU cilju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (gde je `xxxx` broj build-a).

#### Korak 2: Raspakivanje binarnih fajlova

Raspakujte preuzetu arhivu:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ovaj direktorijum sada sadrži ROCm verzije programa `llama-cli.exe`, `llama-server.exe` i `rpc-server.exe`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

#### Korak 3: Provera detekcije GPU-a

```bash
.\llama-cli.exe --list-devices
```

Očekivani izlaz:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Preuzimanje unapred izgrađenih binarnih fajlova

Idite na stranicu najnovijeg izdanja i preuzmite arhivu koja odgovara vašoj platformi i GPU cilju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (gde je `xxxx` broj build-a).

#### Korak 2: Raspakivanje i priprema binarnih fajlova

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ovaj direktorijum sada sadrži ROCm verzije programa `llama-cli`, `llama-server` i `rpc-server`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

#### Korak 3: Provera detekcije GPU-a

```bash
./llama-cli --list-devices
```

Očekivani izlaz:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Kada je llama.cpp pripremljen na svakom čvoru, nastavite sa [Preuzimanjem modela](#downloading-the-model).

### Opcija 2: Ručno izgrađivanje iz izvornog koda

<!-- @os:windows -->
#### Korak 1: Izgradnja llama.cpp

Otvorite **x64 Native Tools Command Prompt** (instaliran uz Visual Studio Build Tools) i klonirajte repozitorijum:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Dodajte HIP u vašu putanju i izgradite sa podrškom za ROCm i RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Build oznaka | Svrha |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogućava ROCm/HIP softverski steka |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuiranu inferenciju |
| `-DGPU_TARGETS=gfx1151` | Cilja Ryzen AI Halo GPU (Radeon 8060s) |
| `-G Ninja` | Koristi Ninja build sistem |

#### Korak 2: Provera detekcije GPU-a

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Očekivani izlaz:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Korak 3: Trajno dodavanje HIP-a u korisničku putanju

Gornji korak izgradnje postavio je `%HIP_PATH%\bin` samo za trenutnu sesiju. Da bi HIP biblioteke bile dostupne u bilo kom terminalu (ne samo u x64 Native Tools Command Prompt-u), trajno ga dodajte u vašu korisničku `PATH` promenljivu:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Kada je llama.cpp pripremljen na svakom čvoru, nastavite sa [Preuzimanjem modela](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Izgradnja llama.cpp

Klonirajte repozitorijum:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Izgradite sa podrškom za ROCm i RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build oznaka | Svrha |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogućava ROCm softverski stek |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuiranu inferenciju |
| `-DAMDGPU_TARGETS="gfx1151"` | Cilja Ryzen AI Halo GPU (Radeon 8060s) |

Za dodatne opcije izgradnje, pogledajte [dokumentaciju za izgradnju llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Korak 2: Provera detekcije GPU-a

```bash
cd rocm/bin
./llama-cli --list-devices
```

Očekivani izlaz:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Kada je llama.cpp pripremljen na svakom čvoru, nastavite sa [Preuzimanjem modela](#downloading-the-model).
<!-- @os:end -->

## Preuzimanje modela

Ovaj vodič koristi [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model sa 358 milijardi parametara u kvantizaciji `Q4_K_XL` od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri ovoj kvantizaciji model zahteva otprilike 205GB prostora za skladištenje i staje u kombinovanu GPU memoriju dva Ryzen AI Halo čvora.

Preuzmite GGUF fajlove pomoću Hugging Face CLI-ja:
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

> **Napomena**: Preuzimanje modela mora biti završeno na Mašini 1 (kontroleru). Radnim čvorovima (RPC worker) nije potrebna lokalna kopija fajlova modela.

## Pokretanje modela na klasteru

RPC (Remote Procedure Call) mehanizam u llama.cpp omogućava jednoj instanci llama.cpp da preusmeri slojeve modela na udaljene radne čvorove preko mreže. Jedna mašina deluje kao **kontroler** (Mašina 1), obavljajući tokenizaciju, raspoređivanje i orkestraciju. Druga mašina pokreće lagani **RPC server** (Mašina 2) koji izlaže svoju GPU memoriju i računsku snagu kontroleru.

Prilikom učitavanja, llama.cpp deli model na oba čvora. Kada se učita, inferencija se odvija kao da radi na jednom akceleratoru. RPC u pozadini upravlja prenosom tenzora i sinhronizacijom.

### Korak 1: Pokretanje RPC servera (Mašina 2)

Na Mašini 2, pokrenite RPC server da bi izložio svoje GPU resurse kontroleru:
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

| Oznaka | Svrha |
|------|---------|
| `-p` | Port na kojem se emituje RPC server |
| `-c` | Omogućava lokalni keš za velike tenzore, izbegavajući ponovljene mrežne prenose tokom učitavanja modela |
| `--host` | IP adresa na koju se povezuje RPC server (`0.0.0.0` za sve interfejse) |

Za dodatne opcije, pogledajte [dokumentaciju za llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Pokretanje modela (Mašina 1)

Kada je RPC server pokrenut na Mašini 2, pokrenite inferenciju sa Mašine 1 koristeći `llama-cli` ili `llama-server`.

#### llama-cli

`llama-cli` pruža terminalski interfejs za direktnu interakciju sa modelom. Idealan je za merenje performansi, otklanjanje grešaka i eksperimentisanje na niskom nivou.

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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Mašini 2, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Pokrenite ovu komandu u Terminal-u (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Mašini 2, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminal-u (Powershell) da biste pronašli njenu lokalnu IP adresu.

<!-- @os:end -->

Kada se pokrene, `llama-cli` prikazuje napredak učitavanja modela i ulazi u interaktivni prompt gde možete direktno da ćaskate sa modelom:

![llama-cli pokreće GLM 4.7 na dva čvora](assets/llama-cli-example.png)
#### llama-server

`llama-server` izlaže isti mehanizam za zaključivanje kroz trajni serverski proces sa integrisanim veb UI-jem i HTTP API-jem kompatibilnim sa OpenAI. Ovo je preferirani interfejs za dugotrajna raspoređivanja, pristup više korisnika i integraciju sa spoljnim alatima.

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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na mašini 2, pokrenite `hostname -I | awk '{print $1}'` da pronađete njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Pokrenite ovu komandu u terminalu (Powershell).

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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na mašini 2, pokrenite `ipconfig | findstr /C:"IPv4"` u terminalu (Powershell) da pronađete njenu lokalnu IP adresu.
<!-- @os:end -->

Kada se pokrene, otvorite `http://<HOST_IP>:8081` u pregledaču da pristupite ugrađenom veb UI-ju. Ovo pruža interfejs za ćaskanje zasnovan na pregledaču za interakciju sa modelom:

![llama-server veb UI koji pokreće GLM 4.7 na dva čvora](assets/llama-server-example.png)

<!-- @os:linux -->
> **Pronalaženje `<HOST_IP>`**: Na mašini 1, pokrenite `hostname -I | awk '{print $1}'` da pronađete njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Pronalaženje `<HOST_IP>`**: Na mašini 1, pokrenite `ipconfig | findstr /C:"IPv4"` u terminalu (Powershell) da pronađete njenu lokalnu IP adresu.
<!-- @os:end -->

#### Referenca parametara

| Oznaka | Svrha |
|------|---------|
| `-m` | Putanja do GGUF fajla modela (koristite prvi deo, `00001-of-00005`) |
| `-c` | Veličina konteksta u tokenima. Veće vrednosti koriste više memorije |
| `-fa on` | Omogućava rocWMMA Flash Attention za poboljšane performanse na AMD GPU-ovima |
| `-ngl 999` | Prebacuje sve slojeve modela na GPU |
| `-lm none` | Postavlja režim učitavanja modela na `none`, onemogućavajući mapiranje memorije radi smanjenja vremena učitavanja kada veličina modela premašuje sistemski RAM, ali stane u VRAM |
| `--host` | IP adresa na koju se vezuje `llama-server` (samo `llama-server`) |
| `--port` | Port na kom se opslužuje HTTP API (samo `llama-server`) |
| `--rpc` | Lista RPC krajnjih tačaka radnika razdvojenih zarezom (`IP:port`) |

Za kompletno korišćenje parametara, pogledajte [dokumentaciju za llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) i [dokumentaciju za llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Sledeći koraci

- **Povezivanje aplikacija trećih strana**: `llama-server` izlaže API kompatibilan sa OpenAI. Usmerite bilo koju aplikaciju kompatibilnu sa OpenAI (kao što je Open WebUI) na `http://<HOST_IP>:8081` sa bilo kojim rezervisanim API ključem (npr. `none`) da se povežete na svoj klaster
- **Istraživanje drugih modela**: Pregledajte kvantizovane GGUF fajlove na [Hugging Face](https://huggingface.co/models?search=gguf) da pronađete modele koji stanu u kombinovanu GPU memoriju vašeg klastera
- **Skaliranje na četiri čvora**: Dodajte još dva Ryzen AI Halo sistema kao dodatne RPC radnike da biste pristupili modelima na skali od 1 triliona parametara. Prosledite dodatne krajnje tačke u `--rpc` kao listu razdvojenu zarezom (npr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)