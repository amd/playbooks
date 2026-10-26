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

Vaš Ryzen™ AI Halo sistem je već sposoban da pokreće velike jezičke modele lokalno. Klasterovanje ovo podiže na viši nivo kombinovanjem GPU memorije više sistema preko lokalne mreže, omogućavajući vam pristup još većim modelima sa jačim rezonovanjem, boljim generisanjem koda i dubljim razumevanjem više jezika, a sve to isključivo na sopstvenom hardveru.

Ovaj vodič vas uči kako da klasterujete dva Ryzen AI Halo sistema koristeći RPC mehanizam iz llama.cpp i pokrenete GLM 4.7, model sa 358 milijardi parametara, na oba uređaja uz AMD ROCm™ akceleraciju.

## Šta ćete naučiti

- Kako da proširite alokaciju VRAM-a na Ryzen AI Halo sistemima
- Instaliranje llama.cpp sa podrškom za ROCm i RPC
- Konfigurisanje RPC radnika (worker) i pokretanje distribuirane inferencije na dva čvora
- Pokretanje modela sa 358 milijardi parametara na dva umrežena Ryzen AI Halo sistema

## Podešavanje konfiguracije memorije

> **Napomena**: Ovaj korak obavite i na Mašini 1 i na Mašini 2.

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Pokretanje modela blizu ili iznad 128 GB:** Na AMD Ryzen™ AI Max 400 Series (Gorgon Halo) sistemima sa operativnim sistemom Windows, modeli koji se približavaju ili prevazilaze 128 GB memorije zahtevaju dodatnu konfiguraciju kako bi se pokrenuli bez grešaka. Pratite [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) pre učitavanja modela.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Na operativnom sistemu Windows, da biste pokrenuli veće modele kojima je potrebno više memorije, potrebno je da koristimo alokaciju AMD Variable Graphics Memory (iGPU VRAM).

Ovo se može uraditi otvaranjem kontrolne table AMD Software: Adrenalin Edition i navigacijom do: `Performance > Tuning > AMD Variable Graphics Memory`. Postavite vrednost na **96 GB**. Molimo vas da restartujete sistem kako bi izmene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Na Linuxu, ROCm koristi zajednički pool sistemske memorije, a ovaj pool je podrazumevano podešen na polovinu sistemske memorije.

Ova količina se može povećati promenom podešavanja Translation Table Manager (TTM) stranica u kernelu, prema sledećim uputstvima. AMD preporučuje da se u BIOS-u podesi minimalna namenska VRAM memorija (0.5 GB).

* Instalirajte pipx alatku i dodajte putanju za pipx instalirane wheel-ove u sistemsku pretragu putanja.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalirajte amd-debug-tools wheel sa PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Pokrenite alatku amd-ttm da proverite trenutna podešavanja za zajedničku memoriju.
  ```bash
  amd-ttm
  ```

* Rekonfigurišite podešavanja zajedničke memorije na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte sistem kako bi izmene stupile na snagu.


<!-- @os:end -->
<!-- @device:halo_box -->
## Proverite ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->
## Preduslovi

### Hardver

Za ovaj vodič su potrebna dva Ryzen AI Halo uređaja i jedan Ethernet svič, povezani u zvezda (star) topologiji, pri čemu je svaki uređaj povezan direktno sa svičem.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računarski čvorovi koji čine klaster |
| 10Gbps Ethernet svič | 1 | Centralni svič koji omogućava komunikaciju više Ryzen AI Halo čvorova (najmanje 2 porta) |
| Ethernet kabl | 2 | Povezuje svaki Halo uređaj sa svičem (preporučuje se Cat 7 ili viši) |

> **Napomena**: Potrebna su dva porta na Ethernet sviču da bi se povezala dva Ryzen AI Halo uređaja. Treći port je potreban ako pristupate modelu sa posebnog klijentskog računara umesto sa jednog od Halo uređaja.

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

> **Napomena**: Ovaj korak obavite i na Mašini 1 i na Mašini 2.

Povežite svaki Ryzen AI Halo uređaj sa Ethernet svičem koristeći Cat 7 (ili viši) kabl. Ovim se uspostavlja 10Gbps veza koja se koristi za komunikaciju velike brzine između čvorova.
<!-- @os:linux -->
### 1. Određivanje mrežnih interfejsa

Na svakoj mašini pronađite ime njenog mrežnog interfejsa i zapišite ga (u daljem tekstu će biti označen kao `IFNAME`). Pokrenite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ovo direktno ispisuje ime interfejsa, na primer:

```bash
enp191s0
```

### 2. Provera brzina mrežnih veza

Potvrdite da je veza aktivna i da radi punom brzinom proverom brzine vašeg interfejsa:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Napomena**: Zamenite `<IFNAME>` izlaznim imenom interfejsa iz [1. Određivanje mrežnih interfejsa](#1-determine-network-interfaces)

Trebalo bi da vidite brzinu od `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Napomena**: Ako je brzina niža od `10000Mb/s` ili veza ne uspostavi, proverite kablovsku vezu i potvrdite da je port na sviču podešen na 10Gbps. Nekim svičevima je potrebno da se automatsko pregovaranje (auto-negotiation) isključi i da se brzina veze podesi ručno; pogledajte dokumentaciju vašeg sviča.

<!-- @os:end -->

<!-- @os:windows -->
### Provera brzine mrežne veze

Na svakoj mašini proverite brzinu veze vaših mrežnih interfejsa:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš Ethernet interfejs bi trebalo da bude `Up` i da radi brzinom od `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Napomena**: Ako je brzina niža od `10 Gbps` ili veza ne uspostavi, proverite kablovsku vezu i potvrdite da je port na sviču podešen na 10Gbps. Nekim svičevima je potrebno da se automatsko pregovaranje (auto-negotiation) isključi i da se brzina veze podesi ručno; pogledajte dokumentaciju vašeg sviča.

<!-- @os:end -->

## Instaliranje llama.cpp

> **Napomena**: Ovaj korak obavite i na Mašini 1 i na Mašini 2.

Dostupne su dve opcije instalacije:

- [Opcija 1: Lemonade SDK (Preporučeno)](#option-1-lemonade-sdk-recommended) - unapred izgrađene binarne datoteke, najbrže podešavanje
- [Opcija 2: Ručno građenje iz izvornog koda](#option-2-manual-source-build) - građenje iz izvornog koda uz punu kontrolu nad opcijama izgradnje
### Opcija 1: Lemonade SDK (preporučeno)

Lemonade SDK obezbeđuje noćne (nightly) verzije llama.cpp sa AMD ROCm 7 akceleracijom, namenjene GPU-ovima kao što je gfx1151 (Strix Halo / Ryzen AI Max+ 395) i drugim novijim Radeon arhitekturama.

<!-- @os:windows -->
#### Korak 1: Preuzimanje unapred izgrađenih binarnih fajlova

Idite na stranicu sa najnovijim izdanjem i preuzmite arhivu koja odgovara vašoj platformi i ciljnom GPU-u:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (gde je `xxxx` broj build-a).

#### Korak 2: Raspakivanje binarnih fajlova

Raspakujte preuzetu arhivu:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ovaj direktorijum sada sadrži ROCm-omogućene verzije `llama-cli.exe`, `llama-server.exe` i `rpc-server.exe`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

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

Idite na stranicu sa najnovijim izdanjem i preuzmite arhivu koja odgovara vašoj platformi i ciljnom GPU-u:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (gde je `xxxx` broj build-a).

#### Korak 2: Raspakivanje i priprema binarnih fajlova

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ovaj direktorijum sada sadrži ROCm-omogućene verzije `llama-cli`, `llama-server` i `rpc-server`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

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

| Build oznaka | Namena |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogućava ROCm/HIP softverski stek |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuirano zaključivanje |
| `-DGPU_TARGETS=gfx1151` | Ciljanje Ryzen AI Halo GPU-a (Radeon 8060s) |
| `-G Ninja` | Koristi Ninja sistem za build |

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

Prethodni korak build-a je postavio `%HIP_PATH%\bin` samo za trenutnu sesiju. Da biste učinili HIP biblioteke dostupnim u bilo kom terminalu (ne samo u x64 Native Tools Command Prompt-u), trajno ga dodajte u korisničku `PATH`:

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
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build oznaka | Namena |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogućava ROCm softverski stek |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuirano zaključivanje |
| `-DAMDGPU_TARGETS="gfx1151"` | Ciljanje Ryzen AI Halo GPU-a (Radeon 8060s) |

Za dodatne opcije build-a, pogledajte [dokumentaciju za build llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Ovaj vodič koristi [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model sa 358 milijardi parametara u `Q4_K_XL` kvantizaciji od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri ovoj kvantizaciji model zahteva otprilike 205 GB prostora za skladištenje i stane u zajedničku GPU memoriju dva Ryzen AI Halo čvora.

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

> **Napomena**: Preuzimanje modela mora biti završeno na Mašini 1 (kontroleru). RPC radnim čvorovima nije potrebna lokalna kopija fajlova modela.

## Pokretanje modela na klasteru

llama.cpp RPC (Remote Procedure Call) mehanizam omogućava da jedna instanca llama.cpp prebaci slojeve modela na udaljene radne čvorove preko mreže. Jedna mašina ima ulogu **kontrolera** (Mašina 1), zadužena za tokenizaciju, raspoređivanje i orkestraciju. Druga mašina pokreće lagani **RPC server** (Mašina 2) koji izlaže svoju GPU memoriju i procesorsku snagu kontroleru.

U trenutku učitavanja, llama.cpp deli model na oba čvora. Nakon učitavanja, zaključivanje se odvija kao da radi na jednom akceleratoru. RPC se u pozadini brine o prenosu tenzora i sinhronizaciji.

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

| Oznaka | Namena |
|------|---------|
| `-p` | Port na kome se emituje RPC server |
| `-c` | Omogućava lokalni keš za velike tenzore, izbegavajući ponovljene prenose preko mreže tokom učitavanja modela |
| `--host` | IP adresa na koju se vezuje RPC server (`0.0.0.0` za sve interfejse) |

Za dodatne opcije, pogledajte [dokumentaciju za llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Pokretanje modela (Mašina 1)

Kada je RPC server pokrenut na Mašini 2, pokrenite zaključivanje sa Mašine 1 koristeći ili `llama-cli` ili `llama-server`.
#### llama-cli

`llama-cli` obezbeđuje interfejs zasnovan na terminalu za direktnu interakciju sa modelom. Idealan je za benčmarking, debagovanje i eksperimentisanje na niskom nivou.

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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Mašini 2, pokrenite `hostname -I | awk '{print $1}'` da pronađete njenu lokalnu IP adresu.
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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Mašini 2, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminalu (Powershell) da pronađete njenu lokalnu IP adresu.

<!-- @os:end -->

Kada se pokrene, `llama-cli` prikazuje napredak učitavanja modela i ulazi u interaktivni prompt gde možete direktno razgovarati sa modelom:

![llama-cli pokreće GLM 4.7 preko dva čvora](assets/llama-cli-example.png)

#### llama-server

`llama-server` izlaže isti mehanizam za zaključivanje kroz trajni serverski proces sa integrisanim veb UI-jem i HTTP API-jem kompatibilnim sa OpenAI. Ovo je preferirani interfejs za dugotrajnija raspoređivanja, višekorisnički pristup i integraciju sa spoljnim alatima.

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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Mašini 2, pokrenite `hostname -I | awk '{print $1}'` da pronađete njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Pokrenite ovu komandu u Terminalu (Powershell).

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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Mašini 2, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminalu (Powershell) da pronađete njenu lokalnu IP adresu.
<!-- @os:end -->

Kada se pokrene, otvorite `http://<HOST_IP>:8081` u svom pregledaču da pristupite ugrađenom veb UI-ju. Ovo pruža interfejs za ćaskanje zasnovan na pregledaču za interakciju sa modelom:

![llama-server veb UI pokreće GLM 4.7 preko dva čvora](assets/llama-server-example.png)

<!-- @os:linux -->
> **Pronalaženje `<HOST_IP>`**: Na Mašini 1, pokrenite `hostname -I | awk '{print $1}'` da pronađete njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Pronalaženje `<HOST_IP>`**: Na Mašini 1, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminalu (Powershell) da pronađete njenu lokalnu IP adresu.
<!-- @os:end -->

#### Referenca parametara

| Oznaka | Svrha |
|------|---------|
| `-m` | Putanja do GGUF fajla modela (koristite prvi deo, `00001-of-00005`) |
| `-c` | Veličina konteksta u tokenima. Veće vrednosti koriste više memorije |
| `-fa on` | Omogućava rocWMMA Flash Attention za poboljšane performanse na AMD GPU-ovima |
| `-ngl 999` | Prebacuje sve slojeve modela na GPU |
| `-lm none` | Postavlja režim učitavanja modela na `none`, onemogućavajući mapiranje memorije radi smanjenja vremena učitavanja kada veličina modela prevazilazi sistemski RAM, ali staje u VRAM |
| `--host` | IP adresa na koju se vezuje `llama-server` (samo za `llama-server`) |
| `--port` | Port na kome se servira HTTP API (samo za `llama-server`) |
| `--rpc` | Lista RPC radnih krajnjih tačaka odvojenih zarezom (`IP:port`) |

Za potpuno korišćenje parametara, pogledajte [dokumentaciju za llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) i [dokumentaciju za llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Sledeći koraci

- **Povežite aplikacije trećih strana**: `llama-server` izlaže API kompatibilan sa OpenAI. Usmerite bilo koju aplikaciju kompatibilnu sa OpenAI (poput Open WebUI) na `http://<HOST_IP>:8081` sa bilo kojim rezervisanim API ključem (npr. `none`) da se povežete sa svojim klasterom
- **Istražite druge modele**: Pregledajte kvantizovane GGUF fajlove na [Hugging Face](https://huggingface.co/models?search=gguf) da pronađete modele koji staju u kombinovanu GPU memoriju vašeg klastera
- **Skalirajte na četiri čvora**: Dodajte još dva Ryzen AI Halo sistema kao dodatne RPC radnike da biste pristupili modelima u razmeri od 1 triliona parametara. Prosledite dodatne krajnje tačke parametru `--rpc` kao listu odvojenu zarezom (npr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)