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

Vaš Ryzen™ AI Halo sistem je već sposoban da lokalno pokreće velike jezičke modele. Klasterovanje ovo dodatno unapređuje kombinovanjem GPU memorije više sistema preko lokalne mreže, dajući vam pristup još većim modelima sa snažnijim rezonovanjem, boljom generacijom koda i dubljim razumevanjem više jezika, sve u potpunosti na vašem sopstvenom hardveru.

Ovaj playbook vas uči kako da klasterujete dva Ryzen AI Halo sistema koristeći RPC mehanizam llama.cpp i pokrenete GLM 4.7, model sa 358 milijardi parametara, na obe mašine uz AMD ROCm™ akceleraciju.

## Šta ćete naučiti

- Kako da proširite alokaciju VRAM-a na Ryzen AI Halo sistemima
- Instaliranje llama.cpp sa podrškom za ROCm i RPC
- Konfigurisanje RPC radnog procesa (worker) i pokretanje distribuirane inferencije na dva čvora
- Pokretanje modela sa 358 milijardi parametara na dva umrežena Ryzen AI Halo sistema

## Podešavanje konfiguracije memorije

> **Napomena**: Izvršite ovaj korak i na Mašini 1 i na Mašini 2.

<!-- @os:windows -->
Na Windows-u, da biste pokretali veće modele koji zahtevaju više memorije, potrebno je da koristimo alokaciju AMD Variable Graphics Memory (iGPU VRAM).

Ovo se može uraditi otvaranjem kontrolne table AMD Software: Adrenalin Edition i navigacijom do: `Performance > Tuning > AMD Variable Graphics Memory`. Postavite vrednost na **96 GB**. Molimo restartujte sistem kako bi promene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Na Linux-u, ROCm koristi deljeni pool sistemske memorije, i ovaj pool je podrazumevano konfigurisan na polovinu sistemske memorije.

Ova količina se može povećati promenom podešavanja stranica kernel-ovog Translation Table Manager-a (TTM), prema sledećim uputstvima. AMD preporučuje da se u BIOS-u podesi minimalna namenska VRAM memorija (0.5 GB).

* Instalirajte pipx alatku i dodajte putanju za pipx instalirane wheel-ove u sistemsku putanju pretrage.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalirajte amd-debug-tools wheel sa PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Pokrenite alatku amd-ttm da biste dobili trenutna podešavanja za deljenu memoriju.
  ```bash
  amd-ttm
  ```

* Rekonfigurišite podešavanja deljene memorije na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte sistem kako bi promene stupile na snagu.


<!-- @os:end -->
<!-- @device:halo_box -->
## Provera ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->
## Preduslovi

### Hardver

Ovaj playbook zahteva dve Ryzen AI Halo jedinice i jedan Ethernet switch, povezane u zvezdastoj topologiji, pri čemu je svaka jedinica direktno povezana kablom sa switch-om.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Kompjuterski čvorovi koji čine klaster |
| 10Gbps Ethernet switch | 1 | Centralni switch koji omogućava komunikaciju između više Ryzen AI Halo čvorova (najmanje 2 porta) |
| Ethernet kabl | 2 | Povezuje svaku Halo jedinicu sa switch-om (preporučuje se Cat 7 ili viši) |

> **Napomena**: Potrebna su dva porta na Ethernet switch-u da bi se povezale dve Ryzen AI Halo jedinice. Treći port je potreban ako pristupate modelu sa posebne klijentske mašine umesto sa jedne od Halo jedinica.

### Softver
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Molimo instalirajte:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) sa radnim opterećenjem (workload) **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizičko podešavanje hardvera

> **Napomena**: Izvršite ovaj korak i na Mašini 1 i na Mašini 2.

Povežite svaku Ryzen AI Halo jedinicu sa Ethernet switch-om koristeći Cat 7 (ili viši) kabl. Ovo uspostavlja 10Gbps vezu koja se koristi za brzu komunikaciju između čvorova.
<!-- @os:linux -->
### 1. Utvrđivanje mrežnih interfejsa

Na svakoj mašini pronađite naziv njenog mrežnog interfejsa i zabeležite ga (u nastavku će biti nazivan `IFNAME`). Pokrenite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ovo direktno ispisuje naziv interfejsa, na primer:

```bash
enp191s0
```

### 2. Provera brzine mrežne veze

Potvrdite da je veza aktivna i da radi punom brzinom proverom brzine vašeg interfejsa:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Napomena**: Zamenite `<IFNAME>` izlaznim nazivom interfejsa iz odeljka [1. Utvrđivanje mrežnih interfejsa](#1-determine-network-interfaces)

Trebalo bi da vidite brzinu od `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Napomena**: Ako je brzina niža od `10000Mb/s` ili veza ne uspostavi, proverite priključak kabla i potvrdite da je port na switch-u podešen na 10Gbps. Neki switch-evi zahtevaju da se auto-negotiation onemogući i brzina veze ručno podesi; pogledajte dokumentaciju vašeg switch-a.

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

> **Napomena**: Ako je brzina niža od `10 Gbps` ili veza ne uspostavi, proverite priključak kabla i potvrdite da je port na switch-u podešen na 10Gbps. Neki switch-evi zahtevaju da se auto-negotiation onemogući i brzina veze ručno podesi; pogledajte dokumentaciju vašeg switch-a.

<!-- @os:end -->

## Instaliranje llama.cpp

> **Napomena**: Izvršite ovaj korak i na Mašini 1 i na Mašini 2.

Dostupne su dve opcije instalacije:

- [Opcija 1: Lemonade SDK (Preporučeno)](#option-1-lemonade-sdk-recommended) - unapred izgrađeni binarni fajlovi, najbrže podešavanje
- [Opcija 2: Ručno pravljenje iz izvornog koda](#option-2-manual-source-build) - izgradnja iz izvornog koda uz potpunu kontrolu nad opcijama izgradnje

### Opcija 1: Lemonade SDK (Preporučeno)

Lemonade SDK pruža noćna (nightly) izdanja llama.cpp sa AMD ROCm 7 akceleracijom, namenjena GPU-ovima kao što su gfx1151 (Strix Halo / Ryzen AI Max+ 395) i drugim novijim Radeon arhitekturama.

<!-- @os:windows -->
#### Korak 1: Preuzimanje unapred izgrađenih binarnih fajlova

Idite na stranicu sa najnovijim izdanjem i preuzmite arhivu koja odgovara vašoj platformi i GPU cilju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (gde je `xxxx` broj build-a).

#### Korak 2: Raspakivanje binarnih fajlova

Raspakujte preuzetu arhivu:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ovaj direktorijum sada sadrži ROCm-omogućene verzije `llama-cli.exe`, `llama-server.exe` i `rpc-server.exe`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

#### Korak 3: Provera prepoznavanja GPU-a

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

Idite na stranicu sa najnovijim izdanjem i preuzmite arhivu koja odgovara vašoj platformi i GPU cilju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (gde je `xxxx` broj build-a).

#### Korak 2: Raspakivanje i priprema binarnih fajlova

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ovaj direktorijum sada sadrži ROCm-omogućene verzije `llama-cli`, `llama-server` i `rpc-server`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

#### Korak 3: Provera prepoznavanja GPU-a

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

### Opcija 2: Ručno građenje iz izvornog koda

<!-- @os:windows -->
#### Korak 1: Građenje llama.cpp

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

| Zastavica (Build Flag) | Svrha |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogućava ROCm/HIP softverski stek |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuirano zaključivanje |
| `-DGPU_TARGETS=gfx1151` | Cilja Ryzen AI Halo GPU (Radeon 8060s) |
| `-G Ninja` | Koristi Ninja sistem za građenje |

#### Korak 2: Provera prepoznavanja GPU-a

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

Gornji korak izgradnje postavio je `%HIP_PATH%\bin` samo za trenutnu sesiju. Da biste omogućili dostupnost HIP biblioteka u bilo kom terminalu (ne samo u x64 Native Tools Command Prompt-u), trajno ga dodajte u vašu korisničku `PATH` promenljivu:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Kada je llama.cpp pripremljen na svakom čvoru, nastavite na [Preuzimanje modela](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Građenje llama.cpp

Klonirajte repozitorijum:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Izgradite sa podrškom za ROCm i RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Zastavica (Build Flag) | Svrha |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogućava ROCm softverski stek |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuirano zaključivanje |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Omogućava rocWMMA za unapređenu Flash Attention na AMD GPU-ovima |
| `-DAMDGPU_TARGETS="gfx1151"` | Cilja Ryzen AI Halo GPU (Radeon 8060s) |

Za više opcija građenja, pogledajte [dokumentaciju za građenje llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Korak 2: Provera prepoznavanja GPU-a

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

Ovaj vodič koristi [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model sa 358 milijardi parametara u `Q4_K_XL` kvantizaciji od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri ovoj kvantizaciji, modelu je potrebno približno 205 GB memorijskog prostora, što stane u kombinovanu GPU memoriju dva Ryzen AI Halo čvora.

Preuzmite GGUF fajlove pomoću Hugging Face CLI alata:
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

> **Napomena**: Preuzimanje modela mora biti izvršeno na Mašini 1 (kontroloru). RPC radnim čvorovima nije potrebna lokalna kopija fajlova modela.

## Pokretanje modela na klasteru

RPC (Remote Procedure Call) mehanizam llama.cpp-a omogućava jednoj instanci llama.cpp-a da prebaci slojeve modela na udaljene radne čvorove preko mreže. Jedna mašina deluje kao **kontroler** (Mašina 1), obavljajući tokenizaciju, raspoređivanje i orkestraciju. Druga mašina pokreće lagani **RPC server** (Mašina 2) koji izlaže svoju GPU memoriju i računarske resurse kontroloru.

U trenutku učitavanja, llama.cpp deli model na oba čvora. Kada je model učitan, zaključivanje se odvija kao da se izvršava na jednom akceleratoru. RPC iza scene rukuje transferima tenzora i sinhronizacijom.

### Korak 1: Pokretanje RPC servera (Mašina 2)

Na Mašini 2, pokrenite RPC server kako biste izložili njene GPU resurse kontroloru:
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
| `-p` | Port na kome se emituje RPC server |
| `-c` | Omogućava lokalni keš za velike tenzore, izbegavajući ponovljene mrežne transfere prilikom učitavanja modela |
| `--host` | IP adresa na koju se vezuje RPC server (`0.0.0.0` za sve interfejse) |

Za više opcija, pogledajte [dokumentaciju za llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Pokretanje modela (Mašina 1)

Kada je RPC server pokrenut na Mašini 2, pokrenite zaključivanje sa Mašine 1 koristeći `llama-cli` ili `llama-server`.

#### llama-cli

`llama-cli` pruža interfejs zasnovan na terminalu za direktnu interakciju sa modelom. Idealan je za merenje performansi, debagovanje i eksperimentisanje na niskom nivou.

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
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Mašini 2, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminalu (Powershell) da biste pronašli njenu lokalnu IP adresu.

<!-- @os:end -->

Kada se pokrene, `llama-cli` prikazuje napredak učitavanja modela i ulazi u interaktivni prompt gde možete direktno da ćaskate sa modelom:

![llama-cli pokreće GLM 4.7 na dva čvora](assets/llama-cli-example.png)
#### llama-server

`llama-server` izlaže isti inferencijski mehanizam kroz trajni server proces sa integrisanim veb UI-jem i OpenAI-kompatibilnim HTTP API-jem. Ovo je preporučeni interfejs za dugotrajnija raspoređivanja, pristup više korisnika i integraciju sa spoljnim alatima.

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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Mašini 2, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Pokrenite ovu komandu u Terminalu (Powershell).

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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Mašini 2, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminalu (Powershell) da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

Kada se pokrene, otvorite `http://<HOST_IP>:8081` u pregledaču da biste pristupili ugrađenom veb UI-ju. Ovo pruža čet interfejs zasnovan na pregledaču za interakciju sa modelom:

![llama-server veb UI koji pokreće GLM 4.7 na dva čvora](assets/llama-server-example.png)

<!-- @os:linux -->
> **Pronalaženje `<HOST_IP>`**: Na Mašini 1, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Pronalaženje `<HOST_IP>`**: Na Mašini 1, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminalu (Powershell) da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

#### Referenca parametara

| Oznaka | Svrha |
|------|---------|
| `-m` | Putanja do GGUF fajla modela (koristite prvi deo, `00001-of-00005`) |
| `-c` | Veličina konteksta u tokenima. Veće vrednosti koriste više memorije |
| `-fa on` | Omogućava rocWMMA Flash Attention za poboljšane performanse na AMD GPU-ovima |
| `-ngl 999` | Prebacuje sve slojeve modela na GPU |
| `--no-mmap` | Onemogućava mapiranje memorije, smanjujući vreme učitavanja kada veličina modela premašuje sistemski RAM ali stane u VRAM |
| `--host` | IP adresa na koju se vezuje `llama-server` (samo za `llama-server`) |
| `--port` | Port na kom se servira HTTP API (samo za `llama-server`) |
| `--rpc` | Lista RPC radnih krajnjih tačaka razdvojenih zapetama (`IP:port`) |

Za potpunu upotrebu parametara, pogledajte [llama-cli dokumentaciju](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) i [llama-server dokumentaciju](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Sledeći koraci

- **Povezivanje aplikacija trećih strana**: `llama-server` izlaže OpenAI-kompatibilan API. Usmerite bilo koju OpenAI-kompatibilnu aplikaciju (kao što je Open WebUI) na `http://<HOST_IP>:8081` sa proizvoljnim zamenskim API ključem (npr., `none`) da biste se povezali sa vašim klasterom
- **Istražite druge modele**: Pregledajte kvantizovane GGUF fajlove na [Hugging Face](https://huggingface.co/models?search=gguf) da biste pronašli modele koji stanu u kombinovanu GPU memoriju vašeg klastera
- **Skaliranje na četiri čvora**: Dodajte još dva Ryzen AI Halo sistema kao dodatne RPC radne jedinice da biste pristupili modelima na skali od 1 triliona parametara. Prosledite dodatne krajnje tačke uz `--rpc` kao listu razdvojenu zapetama (npr., `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)