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

Vaš Ryzen™ AI Halo sistem već je sposoban da lokalno pokreće velike jezičke modele. Klasterovanje ovo dodatno unapređuje kombinovanjem GPU memorije više sistema preko lokalne mreže, pružajući vam pristup još većim modelima sa jačim rezonovanjem, boljom generacijom koda i dubljim višejezičkim razumevanjem, u potpunosti na vašem sopstvenom hardveru.

Ovaj vodič vas uči kako da klasterujete dva Ryzen AI Halo sistema koristeći RPC mehanizam iz llama.cpp i pokrenete GLM 4.7, model sa 358 milijardi parametara, na oba uređaja uz AMD ROCm™ akceleraciju.

## Šta ćete naučiti

- Kako da proširite alokaciju VRAM memorije na Ryzen AI Halo sistemima
- Instaliranje llama.cpp sa ROCm i RPC podrškom
- Konfigurisanje RPC radnika i pokretanje distribuirane inferencije na dva čvora
- Pokretanje modela sa 358 milijardi parametara na dva umrežena Ryzen AI Halo sistema

## Podešavanje konfiguracije memorije

> **Napomena**: Izvršite ovaj korak na Mašini 1 i Mašini 2.

<!-- @os:windows -->
Na Windows sistemu, da bismo pokrenuli veće modele koji zahtevaju više memorije, potrebno je da koristimo alokaciju AMD Variable Graphics Memory (iGPU VRAM).

Ovo se može uraditi otvaranjem kontrolne table AMD Software: Adrenalin Edition i navigacijom do: `Performance > Tuning > AMD Variable Graphics Memory`. Postavite vrednost na **96 GB**. Molimo restartujte sistem da bi izmene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Na Linux sistemu, ROCm koristi zajednički memorijski pul sistema, a ovaj pul je podrazumevano konfigurisan na polovinu memorije sistema.

Ova količina se može povećati promenom podešavanja Translation Table Manager (TTM) stranica u kernelu, pomoću sledećih uputstava. AMD preporučuje da se u BIOS-u podesi minimalna namenska VRAM memorija (0,5 GB).

* Instalirajte alat pipx i dodajte putanju za pipx instalirane wheel pakete u sistemsku putanju pretrage.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalirajte wheel paket amd-debug-tools sa PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Pokrenite alat amd-ttm da biste proverili trenutna podešavanja za deljenu memoriju.
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
## Provera ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->
## Preduslovi

### Hardver

Ovaj vodič zahteva dva Ryzen AI Halo uređaja i jedan Ethernet svič, povezane u zvezdastu topologiju gde je svaki uređaj direktno povezan kablom sa svičem.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Kompjuterski čvorovi koji čine klaster |
| 10Gbps Ethernet svič | 1 | Centralni svič koji omogućava komunikaciju više Ryzen AI Halo čvorova (najmanje 2 porta) |
| Ethernet kabl | 2 | Povezuje svaki Halo uređaj sa svičem (preporučuje se Cat 7 ili viši) |

> **Napomena**: Potrebna su dva porta na Ethernet sviču da bi se povezala dva Ryzen AI Halo uređaja. Treći port je potreban ako modelu pristupate sa posebnog klijentskog računara umesto sa jednog od Halo uređaja.

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

## Podešavanje fizičkog hardvera

> **Napomena**: Izvršite ovaj korak na Mašini 1 i Mašini 2.

Povežite svaki Ryzen AI Halo uređaj sa Ethernet svičem koristeći Cat 7 (ili viši) kabl. Ovim se uspostavlja 10Gbps veza koja se koristi za brzu komunikaciju između čvorova.
<!-- @os:linux -->
### 1. Određivanje mrežnih interfejsa

Na svakoj mašini pronađite naziv njenog mrežnog interfejsa i zabeležite ga (u nastavku će biti nazivan `IFNAME`). Pokrenite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ovo direktno ispisuje naziv interfejsa, na primer:

```bash
enp191s0
```

### 2. Provera brzine mrežne veze

Potvrdite da je veza aktivna i da radi punom brzinom proveravajući brzinu svog interfejsa:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Napomena**: Zamenite `<IFNAME>` izlaznim nazivom interfejsa iz [1. Određivanje mrežnih interfejsa](#1-determine-network-interfaces)

Trebalo bi da vidite brzinu od `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Napomena**: Ako je brzina manja od `10000Mb/s` ili veza ne uspostavi vezu, proverite kablovsku vezu i potvrdite da je port sviča podešen na 10Gbps. Neki svičevi zahtevaju da se auto-negotiation onemogući i brzina veze ručno podesi; pogledajte dokumentaciju vašeg sviča.

<!-- @os:end -->

<!-- @os:windows -->
### Provera brzine mrežne veze

Na svakoj mašini proverite brzinu veze svojih mrežnih interfejsa:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš Ethernet interfejs treba da bude `Up` i da radi na `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Napomena**: Ako je brzina manja od `10 Gbps` ili veza ne uspostavi vezu, proverite kablovsku vezu i potvrdite da je port sviča podešen na 10Gbps. Neki svičevi zahtevaju da se auto-negotiation onemogući i brzina veze ručno podesi; pogledajte dokumentaciju vašeg sviča.

<!-- @os:end -->

## Instaliranje llama.cpp

> **Napomena**: Izvršite ovaj korak na Mašini 1 i Mašini 2.

Dostupne su dve opcije instalacije:

- [Opcija 1: Lemonade SDK (Preporučeno)](#option-1-lemonade-sdk-recommended) - unapred izgrađeni binarni fajlovi, najbrže podešavanje
- [Opcija 2: Ručna izgradnja iz izvornog koda](#option-2-manual-source-build) - izgradnja iz izvornog koda uz potpunu kontrolu nad opcijama izgradnje

### Opcija 1: Lemonade SDK (Preporučeno)

Lemonade SDK pruža noćne (nightly) verzije llama.cpp sa AMD ROCm 7 akceleracijom, namenjene GPU-ovima kao što su gfx1151 (Strix Halo / Ryzen AI Max+ 395) i drugim novijim Radeon arhitekturama.

<!-- @os:windows -->
#### Korak 1: Preuzimanje unapred izgrađenih binarnih fajlova

Idite na stranicu najnovijeg izdanja i preuzmite arhivu koja odgovara vašoj platformi i ciljnom GPU-u:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (gde je `xxxx` broj build-a).

#### Korak 2: Raspakivanje binarnih fajlova

Raspakujte preuzetu arhivu:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ovaj direktorijum sada sadrži ROCm verzije `llama-cli.exe`, `llama-server.exe` i `rpc-server.exe`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

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

Idite na stranicu najnovijeg izdanja i preuzmite arhivu koja odgovara vašoj platformi i ciljnom GPU-u:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (gde je `xxxx` broj build-a).

#### Korak 2: Raspakivanje i priprema binarnih fajlova

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ovaj direktorijum sada sadrži ROCm verzije `llama-cli`, `llama-server` i `rpc-server`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

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
Kada je llama.cpp pripremljen na svakom čvoru, nastavite na [Preuzimanje modela](#downloading-the-model).

### Opcija 2: Ručno kompajliranje iz izvornog koda

<!-- @os:windows -->
#### Korak 1: Kompajliranje llama.cpp

Otvorite **x64 Native Tools Command Prompt** (instaliran uz Visual Studio Build Tools) i klonirajte repozitorijum:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Dodajte HIP u vašu putanju i kompajlirajte sa podrškom za ROCm i RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Zastavica (Flag) | Svrha |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogućava ROCm/HIP softverski stek |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuirano zaključivanje |
| `-DGPU_TARGETS=gfx1151` | Ciljanje Ryzen AI Halo GPU-a (Radeon 8060s) |
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

#### Korak 3: Dodavanje HIP-a u korisničku putanju

Gore navedeni korak kompajliranja postavio je `%HIP_PATH%\bin` samo za trenutnu sesiju. Da biste omogućili dostupnost HIP biblioteka u bilo kom terminalu (ne samo u x64 Native Tools Command Prompt-u), dodajte ga trajno u vašu korisničku `PATH` promenljivu:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Kada je llama.cpp pripremljen na svakom čvoru, nastavite na [Preuzimanje modela](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Kompajliranje llama.cpp

Klonirajte repozitorijum:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Kompajlirajte sa podrškom za ROCm i RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Zastavica (Flag) | Svrha |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogućava ROCm softverski stek |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuirano zaključivanje |
| `-DAMDGPU_TARGETS="gfx1151"` | Ciljanje Ryzen AI Halo GPU-a (Radeon 8060s) |

Za više opcija kompajliranja, pogledajte [dokumentaciju za kompajliranje llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Kada je llama.cpp pripremljen na svakom čvoru, nastavite na [Preuzimanje modela](#downloading-the-model).
<!-- @os:end -->

## Preuzimanje modela

Ovaj vodič koristi [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model sa 358 milijardi parametara u `Q4_K_XL` kvantizaciji od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). U ovoj kvantizaciji modelu je potrebno približno 205GB prostora za skladištenje i stane u kombinovanu GPU memoriju dva Ryzen AI Halo čvora.

Preuzmite GGUF fajlove koristeći Hugging Face CLI:
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

> **Napomena**: Preuzimanje modela mora biti završeno na Mašini 1 (kontroleru). Radnim čvorovima (RPC worker nodes) nije potrebna lokalna kopija fajlova modela.

## Pokretanje modela na klasteru

RPC (Remote Procedure Call) mehanizam u llama.cpp omogućava jednoj instanci llama.cpp da preusmeri slojeve modela na udaljene radne čvorove preko mreže. Jedna mašina deluje kao **kontroler** (Mašina 1), obavljajući tokenizaciju, raspoređivanje i orkestraciju. Druga mašina pokreće lagani **RPC server** (Mašina 2) koji izlaže svoju GPU memoriju i procesorsku snagu kontroleru.

U trenutku učitavanja, llama.cpp deli model na oba čvora. Nakon učitavanja, zaključivanje se odvija kao da radi na jednom akceleratoru. RPC u pozadini upravlja prenosom tenzora i sinhronizacijom.

### Korak 1: Pokretanje RPC servera (Mašina 2)

Na Mašini 2, pokrenite RPC server kako biste izložili njene GPU resurse kontroleru:
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

| Zastavica | Svrha |
|------|---------|
| `-p` | Port na kojem se emituje RPC server |
| `-c` | Omogućava lokalni keš za velike tenzore, izbegavajući ponovljene prenose preko mreže tokom učitavanja modela |
| `--host` | IP adresa na koju se povezuje RPC server (`0.0.0.0` za sve interfejse) |

Za više opcija, pogledajte [dokumentaciju za llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Pokretanje modela (Mašina 1)

Kada je RPC server pokrenut na Mašini 2, pokrenite zaključivanje sa Mašine 1 koristeći `llama-cli` ili `llama-server`.

#### llama-cli

`llama-cli` pruža interfejs zasnovan na terminalu za direktnu interakciju sa modelom. Idealan je za merenje performansi, otklanjanje grešaka i eksperimentisanje na niskom nivou.

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
> **Napomena**: Pokrenite ovu komandu u Terminalu (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Mašini 2, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminalu (Powershell) da biste pronašli njenu lokalnu IP adresu.

<!-- @os:end -->

Kada se pokrene, `llama-cli` prikazuje napredak učitavanja modela i ulazi u interaktivni prompt gde možete direktno da razgovarate sa modelom:

![llama-cli pokreće GLM 4.7 na dva čvora](assets/llama-cli-example.png)
#### llama-server

`llama-server` izlaže isti mehanizam za zaključivanje kroz trajni serverski proces sa integrisanim veb UI-jem i HTTP API-jem kompatibilnim sa OpenAI. Ovo je preporučeni interfejs za dugotrajnija raspoređivanja, pristup više korisnika i integraciju sa spoljnim alatima.

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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na mašini 2, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Pokrenite ovu komandu u Terminal-u (Powershell).

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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na mašini 2, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminal-u (Powershell) da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

Nakon pokretanja, otvorite `http://<HOST_IP>:8081` u svom pretraživaču da biste pristupili ugrađenom veb UI-ju. Ovo pruža interfejs za ćaskanje zasnovan na pretraživaču za interakciju sa modelom:

![llama-server veb UI koji pokreće GLM 4.7 na dva čvora](assets/llama-server-example.png)

<!-- @os:linux -->
> **Pronalaženje `<HOST_IP>`**: Na mašini 1, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Pronalaženje `<HOST_IP>`**: Na mašini 1, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminal-u (Powershell) da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

#### Referenca parametara

| Oznaka | Svrha |
|------|---------|
| `-m` | Putanja do GGUF fajla modela (koristite prvi deo, `00001-of-00005`) |
| `-c` | Veličina konteksta u tokenima. Veće vrednosti koriste više memorije |
| `-fa on` | Omogućava rocWMMA Flash Attention za poboljšane performanse na AMD GPU-ima |
| `-ngl 999` | Prebacuje sve slojeve modela na GPU |
| `-lm none` | Postavlja režim učitavanja modela na `none`, onemogućavajući mapiranje memorije radi smanjenja vremena učitavanja kada veličina modela prevazilazi sistemski RAM, ali stane u VRAM |
| `--host` | IP adresa na koju se vezuje `llama-server` (samo za `llama-server`) |
| `--port` | Port na kom se servira HTTP API (samo za `llama-server`) |
| `--rpc` | Lista RPC krajnjih tačaka radnika, odvojenih zarezom (`IP:port`) |

Za potpuno korišćenje parametara, pogledajte [dokumentaciju za llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) i [dokumentaciju za llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Sledeći koraci

- **Povežite aplikacije trećih strana**: `llama-server` izlaže API kompatibilan sa OpenAI. Usmerite bilo koju aplikaciju kompatibilnu sa OpenAI (kao što je Open WebUI) na `http://<HOST_IP>:8081` sa bilo kojim rezervisanim API ključem (npr. `none`) da biste se povezali sa svojim klasterom
- **Istražite druge modele**: Pregledajte kvantizovane GGUF-ove na [Hugging Face](https://huggingface.co/models?search=gguf) da biste pronašli modele koji stanu u kombinovanu GPU memoriju vašeg klastera
- **Skalirajte na četiri čvora**: Dodajte još dva Ryzen AI Halo sistema kao dodatne RPC radnike da biste pristupili modelima na nivou od 1 triliona parametara. Prosledite dodatne krajnje tačke opciji `--rpc` kao listu odvojenu zarezom (npr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)