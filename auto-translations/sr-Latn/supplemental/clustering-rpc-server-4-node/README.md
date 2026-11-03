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

Vaš Ryzen™ AI Halo sistem je već sposoban da lokalno pokreće velike jezičke modele. Klasterovanje ovo podiže na viši nivo kombinovanjem GPU memorije više sistema preko lokalne mreže, omogućavajući vam pristup još većim modelima sa jačim rezonovanjem, boljim generisanjem koda i dubljim višejezičkim razumevanjem, sve u potpunosti na vašem sopstvenom hardveru.

Ovaj priručnik vas uči kako da klasterujete četiri Ryzen AI Halo sistema koristeći RPC mehanizam iz llama.cpp i pokrenete Kimi K2.6, veliki model tipa mixture-of-experts, na sve četiri mašine uz ubrzanje pomoću AMD ROCm™.

## Šta ćete naučiti

- Kako da proširite alokaciju VRAM-a na Ryzen AI Halo sistemima
- Instaliranje llama.cpp sa ROCm i RPC podrškom
- Konfigurisanje RPC radnih procesa i pokretanje distribuirane inferencije na četiri čvora
- Pokretanje modela sa 1T parametara na četiri umrežena Ryzen AI Halo sistema

## Podešavanje konfiguracije memorije

> **Napomena**: Ovaj korak izvršite na svim četiri mašinama (od Mašine 1 do Mašine 4).

<!-- @os:windows -->
Na Windows-u, da bismo pokretali veće modele koji zahtevaju više memorije, potrebno je da koristimo alokaciju AMD Variable Graphics Memory (iGPU VRAM).

Ovo se može uraditi otvaranjem kontrolne table AMD Software: Adrenalin Edition i navigacijom do: `Performance > Tuning > AMD Variable Graphics Memory`. Podesite vrednost na **96 GB**. Molimo restartujte sistem da bi promene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Na Linux-u, ROCm koristi zajednički skup memorije sistema, a ovaj skup je podrazumevano konfigurisan na polovinu memorije sistema.

Ova količina se može povećati promenom podešavanja stranica kernela Translation Table Manager (TTM), prema sledećim uputstvima. AMD preporučuje podešavanje minimalne namenske VRAM memorije u BIOS-u (0.5 GB).

* Instalirajte alat pipx i dodajte putanju za pipx instalirane wheel pakete u sistemsku putanju pretrage.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalirajte amd-debug-tools wheel paket sa PyPI.
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

* Restartujte sistem da bi promene stupile na snagu.


<!-- @os:end -->
<!-- @device:halo_box -->
## Provera dostupnosti softverskih ažuriranja

<!-- @require:software-update -->
<!-- @device:end -->
## Preduslovi

### Hardver

Ovaj priručnik zahteva četiri jedinice Ryzen AI Halo i jedan Ethernet svič, povezane u topologiju zvezde, gde je svaka jedinica direktno povezana kablom sa svičom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Kompute čvorovi koji čine klaster |
| Ethernet svič od 10Gbps | 1 | Centralni svič koji omogućava komunikaciju više Ryzen AI Halo čvorova (najmanje 4 porta) |
| Ethernet kabl | 4 | Povezuje svaku Halo jedinicu sa svičom (preporučuje se Cat 7 ili viši) |

> **Napomena**: Potrebna su četiri porta na Ethernet sviču da bi se povezale četiri Ryzen AI Halo jedinice. Peti port je potreban ako modelu pristupate sa posebne klijentske mašine umesto sa jedne od Halo jedinica.

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

## Fizička postavka hardvera

> **Napomena**: Ovaj korak izvršite na svim četiri mašinama (od Mašine 1 do Mašine 4).

Povežite svaku Ryzen AI Halo jedinicu sa Ethernet svičom koristeći Cat 7 (ili viši) kabl. Ovo uspostavlja 10Gbps vezu koja se koristi za komunikaciju velike brzine između čvorova.
<!-- @os:linux -->
### 1. Utvrđivanje mrežnih interfejsa

Na svakoj mašini pronađite naziv njenog mrežnog interfejsa i zabeležite ga (u nastavku će se na njega pozivati kao `IFNAME`). Pokrenite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ovo direktno ispisuje naziv interfejsa, na primer:

```bash
enp191s0
```

### 2. Provera brzina mrežnih veza

Potvrdite da je veza aktivna i da radi punom brzinom proverom brzine vašeg interfejsa:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Napomena**: Zamenite `<IFNAME>` nazivom izlaznog interfejsa iz koraka [1. Utvrđivanje mrežnih interfejsa](#1-determine-network-interfaces)

Trebalo bi da vidite brzinu od `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Napomena**: Ako je brzina niža od `10000Mb/s` ili veza ne uspostavi konekciju, proverite kablovsku vezu i potvrdite da je port sviča podešen na 10Gbps. Neki svičevi zahtevaju da se automatska pregovaranje (auto-negotiation) onemogući i da se brzina veze podesi ručno; pogledajte dokumentaciju svog sviča.

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

> **Napomena**: Ako je brzina niža od `10 Gbps` ili veza ne uspostavi konekciju, proverite kablovsku vezu i potvrdite da je port sviča podešen na 10Gbps. Neki svičevi zahtevaju da se automatska pregovaranje (auto-negotiation) onemogući i da se brzina veze podesi ručno; pogledajte dokumentaciju svog sviča.

<!-- @os:end -->

## Instaliranje llama.cpp

> **Napomena**: Ovaj korak izvršite na svim četiri mašinama (od Mašine 1 do Mašine 4).

Dostupne su dve opcije instalacije:

- [Opcija 1: Lemonade SDK (preporučeno)](#option-1-lemonade-sdk-recommended) - unapred izgrađeni binarni fajlovi, najbrža postavka
- [Opcija 2: Ručna izgradnja iz izvornog koda](#option-2-manual-source-build) - izgradnja iz izvornog koda uz potpunu kontrolu nad opcijama izgradnje

### Opcija 1: Lemonade SDK (preporučeno)

Lemonade SDK pruža noćne (nightly) verzije build-ova llama.cpp sa ubrzanjem AMD ROCm 7, namenjene GPU-ovima kao što je gfx1151 (Strix Halo / Ryzen AI Max+ 395) i drugim novijim Radeon arhitekturama.

<!-- @os:windows -->
#### Korak 1: Preuzimanje unapred izgrađenih binarnih fajlova

Idite na stranicu najnovijeg izdanja i preuzmite arhivu koja odgovara vašoj platformi i GPU cilju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (gde je `xxxx` broj izdanja).

#### Korak 2: Raspakivanje binarnih fajlova

Raspakujte preuzetu arhivu:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ovaj direktorijum sada sadrži ROCm-omogućene verzije fajlova `llama-cli.exe`, `llama-server.exe` i `ggml-rpc-server.exe`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

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

Preuzmite fajl pod nazivom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (gde je `xxxx` broj izdanja).

#### Korak 2: Raspakivanje i priprema binarnih fajlova

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ovaj direktorijum sada sadrži ROCm-omogućene verzije fajlova `llama-cli`, `llama-server` i `rpc-server`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

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

### Opcija 2: Ručna izgradnja iz izvornog koda

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

| Oznaka izgradnje | Svrha |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogućava ROCm/HIP softverski steka |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuirano zaključivanje |
| `-DGPU_TARGETS=gfx1151` | Cilja Ryzen AI Halo GPU (Radeon 8060s) |
| `-G Ninja` | Koristi sistem za izgradnju Ninja |

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

Gore navedeni korak izgradnje postavio je `%HIP_PATH%\bin` samo za trenutnu sesiju. Da biste HIP biblioteke učinili dostupnim u bilo kom terminalu (ne samo u x64 Native Tools Command Prompt-u), trajno ga dodajte u vašu korisničku `PATH`:

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

| Oznaka izgradnje | Svrha |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogućava ROCm softverski steka |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuirano zaključivanje |
| `-DAMDGPU_TARGETS="gfx1151"` | Cilja Ryzen AI Halo GPU (Radeon 8060s) |

Za više opcija izgradnje, pogledajte [dokumentaciju za izgradnju llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Ovaj vodič koristi [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) u kvantizaciji `UD-Q2_K_XL` sa [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Ova kvantizacija stane u kombinovanu GPU memoriju četiri Ryzen AI Halo čvora.

Preuzmite GGUF fajlove pomoću Hugging Face CLI-ja:
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

> **Napomena**: Preuzimanje modela mora biti završeno na Mašini 1 (kontroleru). Radnim RPC čvorovima (Mašine 2, 3 i 4) nije potrebna lokalna kopija fajlova modela.

## Pokretanje modela na klasteru

RPC (Remote Procedure Call) mehanizam llama.cpp omogućava jednoj instanci llama.cpp da prebaci slojeve modela na udaljene radne čvorove preko mreže. Jedna mašina deluje kao **kontroler** (Mašina 1), rukujući tokenizacijom, zakazivanjem i orkestracijom. Preostale tri mašine svaka pokreće lagani **RPC server** (Mašine 2, 3 i 4) koji izlaže svoju GPU memoriju i procesorsku snagu kontroleru.

Prilikom učitavanja, llama.cpp deli model na svih četiri čvora. Kada se učita, zaključivanje se odvija kao da radi na jednom akceleratoru. RPC u pozadini rukuje prenosom tenzora i sinhronizacijom.

### Korak 1: Pokretanje RPC servera (Mašine 2, 3 i 4)

Na svakoj od Mašina 2, 3 i 4, pokrenite RPC server da biste izložili njene GPU resurse kontroleru:
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

Za više opcija, pogledajte [dokumentaciju za llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Pokretanje modela (Mašina 1)

Kada su RPC serveri pokrenuti na Mašinama 2, 3 i 4, pokrenite zaključivanje sa Mašine 1 koristeći `llama-cli` ili `llama-server`.
#### llama-cli

`llama-cli` obezbeđuje interfejs zasnovan na terminalu za direktnu interakciju sa modelom. Idealan je za benchmarking, otklanjanje grešaka i eksperimentisanje na niskom nivou.

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

> **Pronalaženje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na svakom od mašina 2, 3 i 4, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Pokrenite ovu komandu u terminalu (Powershell).

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

> **Pronalaženje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na svakom od mašina 2, 3 i 4, pokrenite `ipconfig | findstr /C:"IPv4"` u terminalu (Powershell) da biste pronašli njenu lokalnu IP adresu.

<!-- @os:end -->

Kada se pokrene, `llama-cli` prikazuje napredak učitavanja modela i otvara interaktivni prompt u kojem možete direktno da ćaskate sa modelom:

![llama-cli pokreće Kimi K2.6 na četiri čvora](assets/llama-cli-example.png)

#### llama-server

`llama-server` izlaže isti mehanizam za zaključivanje kroz trajni serverski proces sa integrisanim veb korisničkim interfejsom i HTTP API-jem kompatibilnim sa OpenAI. Ovo je preporučeni interfejs za implementacije koje duže traju, pristup više korisnika i integraciju sa spoljašnjim alatima.

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

> **Pronalaženje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na svakom od mašina 2, 3 i 4, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Pokrenite ovu komandu u terminalu (Powershell).

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

> **Pronalaženje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na svakom od mašina 2, 3 i 4, pokrenite `ipconfig | findstr /C:"IPv4"` u terminalu (Powershell) da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

Kada se pokrene, otvorite `http://<HOST_IP>:8081` u pregledaču da biste pristupili ugrađenom veb korisničkom interfejsu. Ovo obezbeđuje interfejs za ćaskanje zasnovan na pregledaču za interakciju sa modelom:

![llama-server veb korisnički interfejs pokreće Kimi K2.6 na četiri čvora](assets/llama-server-example.png)

<!-- @os:linux -->
> **Pronalaženje `<HOST_IP>`**: Na Mašini 1, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Pronalaženje `<HOST_IP>`**: Na Mašini 1, pokrenite `ipconfig | findstr /C:"IPv4"` u terminalu (Powershell) da biste pronašli njenu lokalnu IP adresu.
<!-- @os:end -->

#### Referenca parametara

| Oznaka | Svrha |
|------|---------|
| `-m` | Putanja do GGUF fajla modela (koristite prvi deo, `00001-of-00008`) |
| `-c` | Veličina konteksta u tokenima. Veće vrednosti koriste više memorije |
| `-fa on` | Omogućava rocWMMA Flash Attention za poboljšane performanse na AMD GPU-ima |
| `-ngl 999` | Prebacuje sve slojeve modela na GPU |
| `-lm none` | Podešava režim učitavanja modela na `none`, onemogućavajući mapiranje u memoriju kako bi se smanjilo vreme učitavanja kada veličina modela premašuje sistemsku RAM memoriju, ali stane u VRAM |
| `-b` | Logička veličina serije u tokenima. Podešavanje na 4096 balansira propusnost i korišćenje memorije na čvorovima |
| `-ub` | Fizička (mikro) veličina serije za obradu prompta. Podudaranje sa `-b` izbegava nepotreban dodatni trošak fragmentacije |
| `--host` | IP adresa na koju se vezuje `llama-server` (samo za `llama-server`) |
| `--port` | Port na kojem se poslužuje HTTP API (samo za `llama-server`) |
| `--rpc` | Lista RPC krajnjih tačaka radnika razdvojenih zarezom (`IP:port`) |

Za potpuno korišćenje parametara, pogledajte [dokumentaciju za llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) i [dokumentaciju za llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Sledeći koraci

- **Povežite aplikacije trećih strana**: `llama-server` izlaže API kompatibilan sa OpenAI. Usmerite bilo koju aplikaciju kompatibilnu sa OpenAI (kao što je Open WebUI) na `http://<HOST_IP>:8081` sa bilo kojim rezervisanim API ključem (npr. `none`) da biste se povezali sa svojim klasterom
- **Istražite druge modele**: Pregledajte kvantizovane GGUF fajlove na [Hugging Face](https://huggingface.co/models?search=gguf) da biste pronašli modele koji stanu u kombinovanu GPU memoriju vašeg klastera
- **Skalirajte iznad četiri čvora**: Dodajte dodatne Ryzen AI Halo sisteme kao dodatne RPC radnike da biste pristupili modelima iznad razmera od 1 triliona parametara. Prosledite dodatne krajnje tačke `--rpc` opciji kao listu razdvojenu zarezom (npr. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)