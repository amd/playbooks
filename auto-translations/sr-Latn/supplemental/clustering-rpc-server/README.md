<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Klasterovanje dva Ryzen™ AI Halo sistema pomoću RPC-a

## Pregled

Vaš Ryzen™ AI Halo je već sposoban da lokalno pokreće velike jezičke modele. Klasterovanje ide korak dalje kombinovanjem GPU memorije više sistema preko lokalne mreže, dajući vam pristup još većim modelima sa snažnijim rezonovanjem, boljim generisanjem koda i dubljim višejezičnim razumevanjem — sve to isključivo na vašem sopstvenom hardveru.

Ovaj priručnik vas uči kako da klasterujete dva Ryzen AI Halo sistema koristeći RPC engine llama.cpp-a i pokrenete GLM 4.7, model sa 358B parametara, na oba računara uz AMD ROCm™ akceleraciju.

## Šta ćete naučiti

- Kako da proširite alokaciju VRAM-a na Ryzen AI Halo sistemima
- Instalacija llama.cpp sa ROCm i RPC podrškom
- Konfigurisanje RPC radnika i pokretanje distribuiranog zaključivanja na dva čvora
- Pokretanje modela sa 358B parametara na dva umrežena Ryzen AI Halo sistema

## Podešavanje konfiguracije memorije

> **Napomena**: Ovaj korak izvršite na oba računara — Računaru 1 i Računaru 2.

<!-- @os:windows -->
Na Windows-u, da bismo pokrenuli veće modele koji zahtevaju više memorije, potrebno je da koristimo AMD Variable Graphics Memory (iGPU VRAM) alokaciju.

To se može uraditi otvaranjem kontrolne table AMD Software: Adrenalin Edition i navigacijom do: `Performance > Tuning > AMD Variable Graphics Memory`. Postavite vrednost na **96 GB**. Molimo vas da restartujete sistem kako bi promene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Na Linux-u, ROCm koristi zajednički skup sistemske memorije, koji je podrazumevano konfigurisan na polovinu sistemske memorije.

Ovaj iznos se može povećati promenom podešavanja stranica Translation Table Manager (TTM) kernela, prema sledećim uputstvima. AMD preporučuje postavljanje minimalnog namenskog VRAM-a u BIOS-u (0,5 GB).

* Instalirajte pipx uslužni program i dodajte putanju za pipx instalirane pakete u sistemsku putanju pretrage.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalirajte amd-debug-tools paket sa PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Pokrenite amd-ttm alat da biste upitali trenutna podešavanja za deljenu memoriju.
  ```bash
  amd-ttm
  ```

* Rekonfigurirajte podešavanja deljene memorije na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte sistem kako bi promene stupile na snagu.


<!-- @os:end -->
<!-- @device:halo_box -->
## Proverite softverska ažuriranja

<!-- @require:software-update -->
<!-- @device:end -->
## Preduslovi

### Hardver

Ovaj priručnik zahteva dve Ryzen AI Halo jedinice i jedan Ethernet svič, povezane u zvezdastoj topologiji pri čemu je svaka jedinica direktno žičano povezana sa svičem.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računarski čvorovi koji čine klaster |
| 10Gbps Ethernet svič | 1 | Centralni svič koji omogućava komunikaciju između više Ryzen AI Halo čvorova (najmanje 2 porta) |
| Ethernet kabl | 2 | Povezuje svaku Halo jedinicu sa svičem (preporučuje se Cat 7 ili viši) |

> **Napomena**: Dva porta Ethernet sviča su potrebna za povezivanje dve Ryzen AI Halo jedinice. Treći port je potreban ako modelu pristupate sa zasebnog klijentskog računara umesto sa jedne od Halo jedinica.

### Softver
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Molimo instalirajte:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) sa radnim opterećenjem **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Postavljanje fizičkog hardvera

> **Napomena**: Ovaj korak izvršite na oba računara — Računaru 1 i Računaru 2.

Povežite svaku Ryzen AI Halo jedinicu sa Ethernet svičem koristeći Cat 7 (ili viši) kabl. Time se uspostavlja 10Gbps veza koja se koristi za brzu komunikaciju između čvorova.
<!-- @os:linux -->
### 1. Određivanje mrežnih interfejsa

Na svakom računaru pronađite naziv njegovog mrežnog interfejsa i zabeležite ga (u nastavku će biti naveden kao `IFNAME`). Pokrenite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ovo direktno ispisuje naziv interfejsa, na primer:

```bash
enp191s0
```

### 2. Provera brzina mrežne veze

Potvrdite da je veza aktivna i da radi punom brzinom proverom brzine vašeg interfejsa:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Napomena**: Zamenite `<IFNAME>` nazivom izlaznog interfejsa iz koraka [1. Određivanje mrežnih interfejsa](#1-determine-network-interfaces)

Trebalo bi da vidite brzinu od `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Napomena**: Ako je brzina manja od `10000Mb/s` ili veza ne uspostavi konekciju, proverite kablovski priključak i potvrdite da je port sviča podešen na 10Gbps. Neki svičevi zahtevaju da se onemogući automatsko pregovaranje i da se brzina veze postavi ručno; pogledajte dokumentaciju vašeg sviča.

<!-- @os:end -->

<!-- @os:windows -->
### Provera brzine mrežne veze

Na svakom računaru proverite brzinu veze vaših mrežnih interfejsa:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš Ethernet interfejs bi trebalo da bude `Up` i da radi na `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Napomena**: Ako je brzina manja od `10 Gbps` ili veza ne uspostavi konekciju, proverite kablovski priključak i potvrdite da je port sviča podešen na 10Gbps. Neki svičevi zahtevaju da se onemogući automatsko pregovaranje i da se brzina veze postavi ručno; pogledajte dokumentaciju vašeg sviča.

<!-- @os:end -->

## Instalacija llama.cpp

> **Napomena**: Ovaj korak izvršite na oba računara — Računaru 1 i Računaru 2.

Dostupne su dve opcije instalacije:

- [Opcija 1: Lemonade SDK (Preporučeno)](#option-1-lemonade-sdk-recommended) — unapred izgrađeni binarni fajlovi, najbrže podešavanje
- [Opcija 2: Ručna izgradnja iz izvornog koda](#option-2-manual-source-build) — izgradnja iz izvornog koda sa punom kontrolom nad zastavicama izgradnje

### Opcija 1: Lemonade SDK (Preporučeno)

Lemonade SDK pruža noćne verzije llama.cpp sa AMD ROCm 7 akceleracijom, ciljajući GPU-ove kao što su gfx1151 (Strix Halo / Ryzen AI Max+ 395) i druge novije Radeon arhitekture.

<!-- @os:windows -->
#### Korak 1: Preuzmite unapred izgrađene binarne fajlove

Idite na stranicu najnovijeg izdanja i preuzmite arhivu koja odgovara vašoj platformi i GPU cilju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (gde je `xxxx` broj verzije).

#### Korak 2: Raspakujte binarne fajlove

Raspakujte preuzetu arhivu:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ovaj direktorijum sada sadrži ROCm-omogućene verzije `llama-cli.exe`, `llama-server.exe` i `rpc-server.exe`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

#### Korak 3: Proverite detekciju GPU-a

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
#### Korak 1: Preuzmite unapred izgrađene binarne fajlove

Idite na stranicu najnovijeg izdanja i preuzmite arhivu koja odgovara vašoj platformi i GPU cilju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Preuzmite fajl pod nazivom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (gde je `xxxx` broj verzije).

#### Korak 2: Raspakujte i pripremite binarne fajlove

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ovaj direktorijum sada sadrži ROCm-omogućene verzije `llama-cli`, `llama-server` i `rpc-server`, unapred kompajlirane za vaš Ryzen AI Halo sistem.

#### Korak 3: Proverite detekciju GPU-a

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
Sa pripremljenim llama.cpp na svakom čvoru, nastavite na [Preuzimanje modela](#downloading-the-model).

### Opcija 2: Ručna izgradnja iz izvornog koda

<!-- @os:windows -->
#### Korak 1: Izgradite llama.cpp

Otvorite **x64 Native Tools Command Prompt** (instaliran sa Visual Studio Build Tools) i klonirajte repozitorijum:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Dodajte HIP u svoju putanju i izgradite sa ROCm i RPC podrškom:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Zastavica izgradnje | Svrha |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogućava ROCm/HIP softverski stek |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuirano zaključivanje |
| `-DGPU_TARGETS=gfx1151` | Cilja Ryzen AI Halo GPU (Radeon 8060s) |
| `-G Ninja` | Koristi Ninja sistem za izgradnju |

#### Korak 2: Proverite detekciju GPU-a

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

#### Korak 3: Dodajte HIP u vašu korisničku putanju

Gornji korak izgradnje je postavio `%HIP_PATH%\bin` samo za trenutnu sesiju. Da biste HIP biblioteke učinili dostupnim u bilo kom terminalu (ne samo u x64 Native Tools Command Prompt), dodajte ih trajno u vašu korisničku `PATH` promenljivu:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Sa pripremljenim llama.cpp na svakom čvoru, nastavite na [Preuzimanje modela](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Izgradite llama.cpp

Klonirajte repozitorijum:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Izgradite sa ROCm i RPC podrškom:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Zastavica izgradnje | Svrha |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogućava ROCm softverski stek |
| `-DGGML_RPC=ON` | Omogućava RPC za distribuirano zaključivanje |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Omogućava rocWMMA za poboljšanu Flash Attention na AMD GPU-ovima |
| `-DAMDGPU_TARGETS="gfx1151"` | Cilja Ryzen AI Halo GPU (Radeon 8060s) |

Za više opcija izgradnje, pogledajte [llama.cpp dokumentaciju za izgradnju](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Korak 2: Proverite detekciju GPU-a

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

Sa pripremljenim llama.cpp na svakom čvoru, nastavite na [Preuzimanje modela](#downloading-the-model).
<!-- @os:end -->

## Preuzimanje modela

Ovaj priručnik koristi [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model sa 358B parametara u `Q4_K_XL` kvantizaciji od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri ovoj kvantizaciji model zahteva oko 205GB prostora za skladištenje i staje u kombinovanu GPU memoriju dva Ryzen AI Halo čvora.

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

> **Napomena**: Preuzimanje modela mora biti završeno na Računaru 1 (kontroleru). RPC radni čvorovi ne trebaju lokalnu kopiju fajlova modela.

## Pokretanje modela na klasteru

RPC (Remote Procedure Call) engine llama.cpp-a omogućava jednoj instanci llama.cpp-a da prebaci slojeve modela na udaljene radnike preko mreže. Jedan računar deluje kao **kontroler** (Računar 1), rukujući tokenizacijom, raspoređivanjem i orkestriranjem. Drugi računar pokreće lagani **RPC server** (Računar 2) koji izlaže svoju GPU memoriju i računarsku snagu kontroleru.

Pri učitavanju, llama.cpp deli model na oba čvora. Kada se učita, zaključivanje se odvija kao da radi na jednom akceleratoru. RPC rukuje prenosima tenzora i sinhronizacijom u pozadini.

### Korak 1: Pokrenite RPC server (Računar 2)

Na Računaru 2, pokrenite RPC server da biste izložili njegove GPU resurse kontroleru:
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

| Zastavica | Svrha |
|------|---------|
| `-p` | Port na kome se emituje RPC server |
| `-c` | Omogućava lokalni keš za velike tenzore, izbegavajući ponovljene mrežne prenose tokom učitavanja modela |
| `--host` | IP adresa na koju se vezuje RPC server (`0.0.0.0` za sve interfejse) |

Za više opcija, pogledajte [llama.cpp RPC dokumentaciju](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Pokrenite model (Računar 1)

Sa RPC serverom koji radi na Računaru 2, pokrenite zaključivanje sa Računara 1 koristeći `llama-cli` ili `llama-server`.

#### llama-cli

`llama-cli` pruža interfejs zasnovan na terminalu za direktnu interakciju sa modelom. Idealan je za merenje performansi, otklanjanje grešaka i eksperimentisanje na niskom nivou.

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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Računaru 2, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njegovu lokalnu IP adresu.
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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Računaru 2, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminalu (Powershell) da biste pronašli njegovu lokalnu IP adresu.

<!-- @os:end -->

Kada se pokrene, `llama-cli` prikazuje napredak učitavanja modela i ulazi u interaktivni prompt gde možete direktno razgovarati sa modelom:

![llama-cli koji pokreće GLM 4.7 na dva čvora](assets/llama-cli-example.png)

#### llama-server

`llama-server` izlaže isti engine za zaključivanje kroz trajni serverski proces sa integrisanim web UI-jem i OpenAI-kompatibilnim HTTP API-jem. Ovo je preferirani interfejs za dugotrajna pokretanja, pristup više korisnika i integraciju sa spoljnim alatima.

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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Računaru 2, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njegovu lokalnu IP adresu.
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

> **Pronalaženje `<RPC_WORKER_IP>`**: Na Računaru 2, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminalu (Powershell) da biste pronašli njegovu lokalnu IP adresu.
<!-- @os:end -->

Kada se pokrene, otvorite `http://<HOST_IP>:8081` u vašem pregledaču da biste pristupili ugrađenom web UI-ju. Ovo pruža interfejs za razgovor zasnovan na pregledaču za interakciju sa modelom:

![llama-server web UI koji pokreće GLM 4.7 na dva čvora](assets/llama-server-example.png)

<!-- @os:linux -->
> **Pronalaženje `<HOST_IP>`**: Na Računaru 1, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njegovu lokalnu IP adresu.
<!-- @os:end -->

<!-- @os:windows -->
> **Pronalaženje `<HOST_IP>`**: Na Računaru 1, pokrenite `ipconfig | findstr /C:"IPv4"` u Terminalu (Powershell) da biste pronašli njegovu lokalnu IP adresu.
<!-- @os:end -->

#### Referenca parametara

| Zastavica | Svrha |
|------|---------|
| `-m` | Putanja do GGUF fajla modela (koristite prvi deo, `00001-of-00005`) |
| `-c` | Veličina konteksta u tokenima. Veće vrednosti koriste više memorije |
| `-fa on` | Omogućava rocWMMA Flash Attention za poboljšane performanse na AMD GPU-ovima |
| `-ngl 999` | Prebacuje sve slojeve modela na GPU |
| `--no-mmap` | Onemogućava mapiranje memorije, smanjujući vreme učitavanja kada veličina modela premašuje sistemski RAM ali staje u VRAM |
| `--host` | IP na koji se vezuje `llama-server` (samo za `llama-server`) |
| `--port` | Port na kome se servira HTTP API (samo za `llama-server`) |
| `--rpc` | Lista RPC radnih krajnjih tačaka odvojena zarezima (`IP:port`) |

Za potpunu upotrebu parametara, pogledajte [llama-cli dokumentaciju](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) i [llama-server dokumentaciju](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Sledeći koraci

- **Povežite aplikacije trećih strana**: `llama-server` izlaže OpenAI-kompatibilan API. Usmerite bilo koju OpenAI-kompatibilnu aplikaciju (kao što je Open WebUI) na `http://<HOST_IP>:8081` sa bilo kojim API ključem kao rezervom (npr. `none`) da biste se povezali sa vašim klasterom
- **Istražite druge modele**: Pregledajte kvantizovane GGUF-ove na [Hugging Face](https://huggingface.co/models?search=gguf) da biste pronašli modele koji staju u kombinovanu GPU memoriju vašeg klastera
- **Skaliranje na četiri čvora**: Dodajte još dva Ryzen AI Halo sistema kao dodatne RPC radnike da biste pristupili modelima na skali od 1 bilion parametara. Prosledite dodatne krajnje tačke u `--rpc` kao listu odvojenu zarezima (npr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)