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

# Klasterovanje četiri Ryzen™ AI Halo sistema pomoću RPC-a

## Pregled

Vaš Ryzen™ AI Halo je već sposoban da lokalno pokreće velike jezičke modele. Klasterovanje ovo unapređuje kombinovanjem GPU memorije više sistema preko lokalne mreže, dajući vam pristup još većim modelima sa jačim rezonovanjem, boljim generisanjem koda i dubljim višejezičkim razumevanjem, sve u potpunosti na sopstvenom hardveru.

Ovaj vodič vas uči kako da klasterujete četiri Ryzen AI Halo sistema koristeći RPC mehanizam alata llama.cpp i pokrenete Kimi K2.6, veliki mixture-of-experts model, na sve četiri mašine uz AMD ROCm™ akceleraciju.

## Šta ćete naučiti

- Kako da proširite alokaciju VRAM-a na Ryzen AI Halo sistemima
- Instaliranje llama.cpp sa podrškom za ROCm i RPC
- Konfigurisanje RPC radnika i pokretanje distribuiranog zaključivanja na četiri čvora
- Pokretanje modela sa 1 bilionom parametara na četiri umrežena Ryzen AI Halo sistema

## Podešavanje konfiguracije memorije

> **Napomena**: Izvršite ovaj korak na sve četiri mašine (Mašina 1 do Mašine 4).

<!-- @os:windows -->
Na sistemu Windows, da biste pokretali veće modele kojima je potrebna veća memorija, potrebno je da koristimo alokaciju AMD Variable Graphics Memory (iGPU VRAM).

Ovo se može uraditi otvaranjem kontrolne table AMD Software: Adrenalin Edition i navigacijom do: `Performance > Tuning > AMD Variable Graphics Memory`. Postavite vrednost na **96 GB**. Molimo restartujte sistem da bi izmene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Na sistemu Linux, ROCm koristi deljeni sistemski memorijski pul, i ovaj pul je podrazumevano konfigurisan na polovinu sistemske memorije.

Ova količina se može povećati promenom podešavanja stranica kernelovog Translation Table Manager-a (TTM), prateći sledeća uputstva. AMD preporučuje da se u BIOS-u podesi minimalna namenska VRAM memorija (0.5 GB).

* Instalirajte alat pipx i dodajte putanju za pipx instalirane wheel pakete u sistemsku putanju pretrage.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalirajte amd-debug-tools wheel sa PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Pokrenite alat amd-ttm da biste proverili trenutna podešavanja za deljenu memoriju.
  ```bash
  amd-ttm
  ```

* Ponovo konfigurišite podešavanja deljene memorije na **120 GB**:
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

Ovaj vodič zahteva četiri Ryzen AI Halo jedinice i jedan Ethernet switch, povezane u zvezdastu topologiju gde je svaka jedinica direktno povezana sa switch-om.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Kompjuterski čvorovi koji čine klaster |
| 10Gbps Ethernet switch | 1 | Centralni switch koji omogućava komunikaciju više Ryzen AI Halo čvorova (najmanje 4 porta) |
| Ethernet kabl | 4 | Povezuje svaku Halo jedinicu sa switch-om (preporučuje se Cat 7 ili viši) |

> **Napomena**: Potrebna su četiri porta na Ethernet switch-u da bi se povezale četiri Ryzen AI Halo jedinice. Peti port je potreban ako pristupate modelu sa posebne klijentske mašine umesto sa jedne od Halo jedinica.

### Softver
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Molimo instalirajte:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) uz radno okruženje **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizičko podešavanje hardvera

> **Napomena**: Izvršite ovaj korak na sve četiri mašine (Mašina 1 do Mašine 4).

Povežite svaku Ryzen AI Halo jedinicu sa Ethernet switch-om koristeći Cat 7 (ili viši) kabl. Ovo uspostavlja 10Gbps vezu koja se koristi za brzu komunikaciju između čvorova.
<!-- @os:linux -->
### 1. Utvrđivanje mrežnih interfejsa

Na svakoj mašini, pronađite naziv njenog mrežnog interfejsa i zabeležite ga (dalje u tekstu se naziva `IFNAME`). Pokrenite:

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

> **Napomena**: Ako je brzina niža od `10000Mb/s` ili veza ne uspostavlja, proverite kablovsku vezu i potvrdite da je port na switch-u podešen na 10Gbps. Neki switch-evi zahtevaju da se auto-negotiation isključi i da se brzina veze podesi ručno; pogledajte dokumentaciju vašeg switch-a.

<!-- @os:end -->

<!-- @os:windows -->
### Provera brzine mrežne veze

Na svakoj mašini, proverite brzinu veze vaših mrežnih interfejsa:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš Ethernet interfejs treba da bude `Up` i da radi na `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Napomena**: Ako je brzina niža od `10 Gbps` ili veza ne uspostavlja, proverite kablovsku vezu i potvrdite da je port na switch-u podešen na 10Gbps. Neki switch-evi zahtevaju da se auto-negotiation isključi i da se brzina veze podesi ručno; pogledajte dokumentaciju vašeg switch-a.

<!-- @os:end -->

## Instaliranje llama.cpp

> **Napomena**: Izvršite ovaj korak na sve četiri mašine (Mašina 1 do Mašine 4).

Dostupne su dve opcije instalacije:

- [Opcija 1: Lemonade SDK (preporučeno)](#option-1-lemonade-sdk-recommended) - unapred izgrađene binarne datoteke, najbrže podešavanje
- [Opcija 2: Ručna izgradnja iz izvornog koda](#option-2-manual-source-build) - izgradnja iz izvornog koda uz punu kontrolu nad opcijama izgradnje

### Opcija 1: Lemonade SDK (preporučeno)

Lemonade SDK pruža noćne verzije alata llama.cpp sa AMD ROCm 7 akceleracijom, namenjene GPU-ovima kao što su gfx1151 (Strix Halo / Ryzen AI Max+ 395) i drugim novijim Radeon arhitekturama.

<!-- @os:windows -->
#### Korak 1: Preuzimanje unapred izgrađenih binarnih fajlova

Idite na stranicu najnovijeg izdanja i preuzmite arhivu koja odgovara vašoj platformi i ciljnoj GPU jedinici:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (gde je `xxxx` broj build-a).

#### Korak 2: Raspakivanje binarnih fajlova

Otpakujte preuzetu arhivu:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ovaj direktorijum sada sadrži ROCm verzije alata `llama-cli.exe`, `llama-server.exe` i `ggml-rpc-server.exe`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

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

Idite na stranicu najnovijeg izdanja i preuzmite arhivu koja odgovara vašoj platformi i ciljnoj GPU jedinici:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (gde je `xxxx` broj build-a).

#### Korak 2: Raspakivanje i priprema binarnih fajlova

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ovaj direktorijum sada sadrži ROCm verzije alata `llama-cli`, `llama-server` i `rpc-server`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

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
| `-DGGML_HIP=ON` | Omogućava ROCm/HIP softverski stek |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuirano zaključivanje |
| `-DGPU_TARGETS=gfx1151` | Cilja Ryzen AI Halo GPU (Radeon 8060s) |
| `-G Ninja` | Koristi Ninja sistem za izgradnju |

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

#### Korak 3: Dodavanje HIP-a u vašu korisničku putanju

Prethodni korak izgradnje je postavio `%HIP_PATH%\bin` samo za tekuću sesiju. Da bi HIP biblioteke bile dostupne u bilo kom terminalu (ne samo u x64 Native Tools Command Prompt-u), dodajte je trajno u vašu korisničku `PATH` promenljivu:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Kada je llama.cpp pripremljen na svakom čvoru, nastavite na [Preuzimanje modela](#downloading-the-model).
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
| `-DGGML_RPC=ON` | Omogućava RPC za distribuirano zaključivanje |
| `-DAMDGPU_TARGETS="gfx1151"` | Cilja Ryzen AI Halo GPU (Radeon 8060s) |

Za više opcija izgradnje, pogledajte [dokumentaciju o izgradnji llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Ovaj vodič koristi [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) u kvantizaciji `UD-Q2_K_XL` iz [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Ova kvantizacija stane u kombinovanu GPU memoriju četiri Ryzen AI Halo čvora.

Preuzmite GGUF fajlove pomoću Hugging Face CLI alata:
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

> **Napomena**: Preuzimanje modela mora biti završeno na Mašini 1 (kontroloru). Radni čvorovi za RPC (Mašine 2, 3 i 4) ne moraju imati lokalnu kopiju fajlova modela.

## Pokretanje modela na klasteru

RPC (Remote Procedure Call) mehanizam u okviru llama.cpp omogućava da jedna instanca llama.cpp prebaci slojeve modela na udaljene radne čvorove preko mreže. Jedna mašina deluje kao **kontrolor** (Mašina 1), zadužena za tokenizaciju, raspoređivanje i orkestraciju. Preostale tri mašine svaka pokreće lagani **RPC server** (Mašine 2, 3 i 4) koji izlaže svoju GPU memoriju i računarske resurse kontroloru.

Prilikom učitavanja, llama.cpp deli model na sve četiri čvora. Nakon učitavanja, zaključivanje se odvija kao da se izvršava na jednom akceleratoru. RPC u pozadini upravlja transferom tenzora i sinhronizacijom.

### Korak 1: Pokretanje RPC servera (Mašine 2, 3 i 4)

Na svakoj od Mašina 2, 3 i 4, pokrenite RPC server kako biste izložili njene GPU resurse kontroloru:
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
| `-p` | Port za emitovanje RPC servera |
| `-c` | Omogućava lokalni keš za velike tenzore, izbegavajući ponovljene mrežne transfere tokom učitavanja modela |
| `--host` | IP adresa na koju se vezuje RPC server (`0.0.0.0` za sve interfejse) |

Za više opcija, pogledajte [dokumentaciju o RPC-u za llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Pokretanje modela (Mašina 1)

Kada su RPC serveri pokrenuti na Mašinama 2, 3 i 4, pokrenite zaključivanje sa Mašine 1 koristeći `llama-cli` ili `llama-server`.
#### llama-cli

`llama-cli` obezbeđuje interfejs zasnovan na terminalu za direktnu interakciju sa modelom. Idealan je za benčmarking, otklanjanje grešaka i eksperimentisanje na niskom nivou.

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

> **Pronalaženje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na svakoj od mašina 2, 3 i 4, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Pokrenite ovu komandu u Terminal-u (Powershell).

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

> **Pronalaženje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na svakoj od mašina 2, 3 i 4, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminal-u (Powershell) da biste pronašli njenu lokalnu IP adresu.

<!-- @os:end -->

Kada se pokrene, `llama-cli` prikazuje napredak učitavanja modela i ulazi u interaktivni prompt gde možete direktno da razgovarate sa modelom:

![llama-cli pokreće Kimi K2.6 na četiri čvora](assets/llama-cli-example.png)

#### llama-server

`llama-server` izlaže isti mehanizam za zaključivanje kroz trajni serverski proces sa integrisanim veb korisničkim interfejsom i HTTP API-jem kompatibilnim sa OpenAI. Ovo je preferirani interfejs za dugotrajnija raspoređivanja, pristup više korisnika i integraciju sa spoljnim alatima.

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

> **Pronalaženje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na svakoj od mašina 2, 3 i 4, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Pokrenite ovu komandu u Terminal-u (Powershell).

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

> **Pronalaženje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na svakoj od mašina 2, 3 i 4, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminal-u (Powershell) da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

Kada se pokrene, otvorite `http://<HOST_IP>:8081` u pregledaču da biste pristupili ugrađenom veb korisničkom interfejsu. Ovo obezbeđuje interfejs za ćaskanje zasnovan na pregledaču za interakciju sa modelom:

![llama-server veb korisnički interfejs pokreće Kimi K2.6 na četiri čvora](assets/llama-server-example.png)

<!-- @os:linux -->
> **Pronalaženje `<HOST_IP>`**: Na mašini 1, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Pronalaženje `<HOST_IP>`**: Na mašini 1, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminal-u (Powershell) da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

#### Referenca parametara

| Oznaka | Svrha |
|------|---------|
| `-m` | Putanja do GGUF fajla modela (koristite prvi deo, `00001-of-00008`) |
| `-c` | Veličina konteksta u tokenima. Veće vrednosti koriste više memorije |
| `-fa on` | Omogućava rocWMMA Flash Attention za poboljšane performanse na AMD GPU-ovima |
| `-ngl 999` | Prebacuje sve slojeve modela na GPU |
| `-lm none` | Postavlja režim učitavanja modela na `none`, onemogućavajući memorijsko mapiranje kako bi se smanjilo vreme učitavanja kada veličina modela premašuje sistemski RAM, ali stane u VRAM |
| `-b` | Logička veličina serije u tokenima. Postavljanje na 4096 balansira propusnost i upotrebu memorije na čvorovima |
| `-ub` | Fizička (mikro) veličina serije za obradu prompta. Poklapanje sa `-b` izbegava nepotrebno opterećenje usled deljenja na delove |
| `--host` | IP adresa na koju se vezuje `llama-server` (samo za `llama-server`) |
| `--port` | Port na kome se opslužuje HTTP API (samo za `llama-server`) |
| `--rpc` | Lista RPC krajnjih tačaka radnika (worker-a) razdvojenih zarezom (`IP:port`) |

Za potpuno korišćenje parametara, pogledajte [dokumentaciju za llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) i [dokumentaciju za llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Sledeći koraci

- **Povežite aplikacije trećih strana**: `llama-server` izlaže API kompatibilan sa OpenAI. Usmerite bilo koju aplikaciju kompatibilnu sa OpenAI (kao što je Open WebUI) na `http://<HOST_IP>:8081` sa bilo kojim rezervisanim API ključem (npr. `none`) da biste se povezali sa vašim klasterom
- **Istražite druge modele**: Pregledajte kvantizovane GGUF fajlove na [Hugging Face](https://huggingface.co/models?search=gguf) da biste pronašli modele koji stanu u ukupnu GPU memoriju vašeg klastera
- **Proširite se preko četiri čvora**: Dodajte dodatne Ryzen AI Halo sisteme kao dodatne RPC radnike (worker-e) da biste pristupili modelima iznad skale od 1 triliona parametara. Prosledite dodatne krajnje tačke u `--rpc` kao listu razdvojenu zarezom (npr. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)