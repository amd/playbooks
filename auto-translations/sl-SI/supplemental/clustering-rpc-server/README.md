<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, nekateri koraki, ukazi, prenosi ali razpoložljivost izdelkov pa se lahko razlikujejo glede na vaš jezik ali regijo. Če se vam kaj zdi napačno, upoštevajte, da je izvirni angleški playbook merodajni vir.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> Ta priročnik uporablja posebne oznake, ki jih GitHub ne more upodobiti. Za pravilen predogled te vsebine obiščite [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

# Povezovanje dveh sistemov Ryzen™ AI Halo v gručo z uporabo RPC

## Pregled

Vaš sistem Ryzen™ AI Halo že zdaj omogoča lokalno izvajanje velikih jezikovnih modelov. Povezovanje v gručo (clustering) to zmožnost razširi še dlje, saj združi GPU pomnilnik več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z močnejšim sklepanjem, boljšim generiranjem kode in globljim razumevanjem več jezikov – vse to popolnoma na vaši lastni strojni opremi.

Ta priročnik vas nauči, kako povezati dva sistema Ryzen AI Halo v gručo z uporabo RPC pogona llama.cpp in kako izvajati GLM 4.7, model s 358 milijardami parametrov, na obeh napravah hkrati z pospeševanjem AMD ROCm™.

## Kaj se boste naučili

- Kako razširiti dodelitev VRAM na sistemih Ryzen AI Halo
- Namestitev llama.cpp s podporo za ROCm in RPC
- Konfiguracija delavca RPC (RPC worker) in zagon porazdeljenega sklepanja na dveh vozliščih
- Izvajanje modela s 358 milijardami parametrov na dveh omrežno povezanih sistemih Ryzen AI Halo

## Nastavitev konfiguracije pomnilnika

> **Opomba**: Ta korak izvedite tako na Napravi 1 kot na Napravi 2.

<!-- @os:windows -->
V sistemu Windows moramo za izvajanje večjih modelov, ki zahtevajo več pomnilnika, uporabiti dodelitev AMD Variable Graphics Memory (iGPU VRAM).

To storite tako, da odprete nadzorno ploščo AMD Software: Adrenalin Edition in se pomaknete na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavite vrednost na **96 GB**. Za uveljavitev sprememb ponovno zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V sistemu Linux ROCm uporablja skupni bazen sistemskega pomnilnika, ki je privzeto nastavljen na polovico celotnega sistemskega pomnilnika.

To količino lahko povečate s spremembo nastavitve strani upravitelja prevajalnih tabel (Translation Table Manager, TTM) v jedru, in sicer po naslednjih navodilih. AMD priporoča, da v BIOS-u nastavite minimalni namenski VRAM (0,5 GB).

* Namestite orodje pipx in dodajte pot za wheel pakete, nameščene s pipx, v sistemsko iskalno pot.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite wheel paket amd-debug-tools iz PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Zaženite orodje amd-ttm za poizvedbo trenutnih nastavitev skupnega pomnilnika.
  ```bash
  amd-ttm
  ```

* Ponovno konfigurirajte nastavitve skupnega pomnilnika na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Za uveljavitev sprememb ponovno zaženite sistem.


<!-- @os:end -->
<!-- @device:halo_box -->
## Preverjanje programskih posodobitev

<!-- @require:software-update -->
<!-- @device:end -->
## Predpogoji

### Strojna oprema

Ta priročnik zahteva dve enoti Ryzen AI Halo in eno omrežno stikalo Ethernet, povezani v zvezdno topologijo, pri čemer je vsaka enota neposredno povezana s stikalom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računalniška vozlišča, ki tvorita gručo |
| 10Gbps Ethernet stikalo | 1 | Osrednje stikalo, ki omogoča komunikacijo med več vozlišči Ryzen AI Halo (vsaj 2 vrat) |
| Ethernet kabel | 2 | Povezuje vsako enoto Halo s stikalom (priporočljiv Cat 7 ali višji) |

> **Opomba**: Za povezavo dveh enot Ryzen AI Halo sta potrebna dva vrata na Ethernet stikalu. Tretja vrata so potrebna, če do modela dostopate iz ločenega odjemalskega računalnika namesto iz ene od enot Halo.

### Programska oprema
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Namestite:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) z delovnim tokom **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizična nastavitev strojne opreme

> **Opomba**: Ta korak izvedite tako na Napravi 1 kot na Napravi 2.

Povežite vsako enoto Ryzen AI Halo z Ethernet stikalom z uporabo kabla Cat 7 (ali višjega). S tem vzpostavite 10Gbps povezavo, ki se uporablja za visokohitrostno komunikacijo med vozlišči.
<!-- @os:linux -->
### 1. Določanje omrežnih vmesnikov

Na vsaki napravi poiščite ime njenega omrežnega vmesnika in si ga zapišite (v nadaljevanju bo imenovan `IFNAME`). Zaženite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

To izpiše ime vmesnika neposredno, na primer:

```bash
enp191s0
```

### 2. Preverjanje hitrosti omrežne povezave

Potrdite, da je povezava aktivna in deluje s polno hitrostjo, tako da preverite hitrost vašega vmesnika:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opomba**: Zamenjajte `<IFNAME>` z izhodnim imenom vmesnika iz [1. Določanje omrežnih vmesnikov](#1-determine-network-interfaces)

Videti bi morali hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali če povezava ne vzpostavi, preverite kabelsko povezavo in potrdite, da so vrata stikala nastavljena na 10Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje (auto-negotiation) in ročno nastavite hitrost povezave; oglejte si dokumentacijo svojega stikala.

<!-- @os:end -->

<!-- @os:windows -->
### Preverjanje hitrosti omrežne povezave

Na vsaki napravi preverite hitrost povezave vaših omrežnih vmesnikov:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš Ethernet vmesnik bi moral biti `Up` in delovati pri `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Opomba**: Če je hitrost nižja od `10 Gbps` ali če povezava ne vzpostavi, preverite kabelsko povezavo in potrdite, da so vrata stikala nastavljena na 10Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje (auto-negotiation) in ročno nastavite hitrost povezave; oglejte si dokumentacijo svojega stikala.

<!-- @os:end -->

## Nameščanje llama.cpp

> **Opomba**: Ta korak izvedite tako na Napravi 1 kot na Napravi 2.

Na voljo sta dve možnosti namestitve:

- [Možnost 1: Lemonade SDK (priporočeno)](#option-1-lemonade-sdk-recommended) – vnaprej pripravljene binarne datoteke, najhitrejša namestitev
- [Možnost 2: Ročna izgradnja iz izvorne kode](#option-2-manual-source-build) – izgradnja iz izvorne kode s popolnim nadzorom nad zastavicami izgradnje

### Možnost 1: Lemonade SDK (priporočeno)

Lemonade SDK ponuja nočne (nightly) izgradnje llama.cpp s pospeševanjem AMD ROCm 7, namenjene GPU-jem, kot je gfx1151 (Strix Halo / Ryzen AI Max+ 395), in drugim novejšim arhitekturam Radeon.

<!-- @os:windows -->
#### Step 1: Prenesite vnaprej pripravljene binarne datoteke

Pojdite na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljnemu GPU-ju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka izdaje).

#### Korak 2: Razpakirajte binarne datoteke

Razširite preneseni arhiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ta mapa zdaj vsebuje z ROCm omogočene izgradnje datotek `llama-cli.exe`, `llama-server.exe` in `rpc-server.exe`, prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverite zaznavanje GPU-ja

```bash
.\llama-cli.exe --list-devices
```

Pričakovan izpis:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Prenesite vnaprej pripravljene binarne datoteke

Pojdite na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljnemu GPU-ju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka izdaje).

#### Korak 2: Razpakirajte in pripravite binarne datoteke

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ta mapa zdaj vsebuje z ROCm omogočene izgradnje datotek `llama-cli`, `llama-server` in `rpc-server`, prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverite zaznavanje GPU-ja

```bash
./llama-cli --list-devices
```

Pričakovan izpis:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte na [Prenos modela](#downloading-the-model).

### Možnost 2: Ročna izgradnja iz izvorne kode

<!-- @os:windows -->
#### Korak 1: Izgradite llama.cpp

Odprite **x64 Native Tools Command Prompt** (nameščen z Visual Studio Build Tools) in klonirajte repozitorij:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Dodajte HIP v svojo pot in izgradite s podporo za ROCm in RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Zastavica gradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programski sklad ROCm/HIP |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DGPU_TARGETS=gfx1151` | Ciljanje na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Uporablja sistem za gradnjo Ninja |

#### Korak 2: Preverite zaznavanje GPU-ja

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Pričakovan izpis:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Korak 3: Dodajte HIP v svojo uporabniško pot

Zgornji korak gradnje je nastavil `%HIP_PATH%\bin` le za trenutno sejo. Da bodo knjižnice HIP na voljo v katerem koli terminalu (ne le v x64 Native Tools Command Prompt), jo trajno dodajte v uporabniško pot `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte na [Prenos modela](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Izgradite llama.cpp

Klonirajte repozitorij:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Izgradite s podporo za ROCm in RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Zastavica gradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programski sklad ROCm |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Omogoči rocWMMA za izboljšano Flash Attention na GPU-jih AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Ciljanje na GPU Ryzen AI Halo (Radeon 8060s) |

Za več možnosti gradnje glejte [dokumentacijo za gradnjo llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Korak 2: Preverite zaznavanje GPU-ja

```bash
cd rocm/bin
./llama-cli --list-devices
```

Pričakovan izpis:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte na [Prenos modela](#downloading-the-model).
<!-- @os:end -->

## Prenos modela

Ta priročnik uporablja [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model s 358 milijardami parametrov v kvantizaciji `Q4_K_XL` podjetja [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri tej kvantizaciji model zahteva približno 205 GB shrambe in se prilega skupnemu pomnilniku GPU-jev dveh vozlišč Ryzen AI Halo.

Prenesite datoteke GGUF s pomočjo Hugging Face CLI:
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

> **Opomba**: Prenos modela je treba dokončati na Napravi 1 (nadzorniku). Delovna vozlišča RPC ne potrebujejo lokalne kopije datotek modela.

## Zagon modela v gruči

Mehanizem llama.cpp RPC (Remote Procedure Call) omogoča, da posamezna instanca llama.cpp razporedi plasti modela na oddaljene delovne naprave prek omrežja. Ena naprava deluje kot **nadzornik** (Naprava 1) in skrbi za tokenizacijo, razporejanje in orkestracijo. Druga naprava poganja lahek **RPC strežnik** (Naprava 2), ki nadzorniku izpostavi svoj pomnilnik in računsko zmogljivost GPU-ja.

Ob nalaganju llama.cpp razdeli model med obe vozlišči. Ko je model naložen, sklepanje poteka, kot da bi teklo na enem samem pospeševalniku. RPC v ozadju poskrbi za prenose tenzorjev in sinhronizacijo.

### Korak 1: Zaženite RPC strežnik (Naprava 2)

Na Napravi 2 zaženite RPC strežnik, da nadzorniku izpostavite njene vire GPU-ja:
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

| Zastavica | Namen |
|------|---------|
| `-p` | Vrata, na katerih se oddaja RPC strežnik |
| `-c` | Omogoči lokalni predpomnilnik za velike tenzorje, s čimer se izogne ponovnim omrežnim prenosom med nalaganjem modela |
| `--host` | IP naslov, na katerega se veže RPC strežnik (`0.0.0.0` za vse vmesnike) |

Za več možnosti glejte [dokumentacijo RPC za llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Zaženite model (Naprava 1)

Ko RPC strežnik teče na Napravi 2, zaženite sklepanje z Naprave 1 z uporabo bodisi `llama-cli` bodisi `llama-server`.

#### llama-cli

`llama-cli` ponuja terminalski vmesnik za neposredno interakcijo z modelom. Idealen je za primerjalno testiranje, odpravljanje napak in nizkonivojsko eksperimentiranje.

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

> **Iskanje `<RPC_WORKER_IP>`**: Na Napravi 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni IP naslov.
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba**: To ukaz zaženite v terminalu (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Iskanje `<RPC_WORKER_IP>`**: Na Napravi 2 v terminalu (Powershell) zaženite `ipconfig | findstr /C:"IPv4"`, da poiščete njen lokalni IP naslov.

<!-- @os:end -->

Ko je zagnan, `llama-cli` prikaže napredek nalaganja modela in vstopi v interaktivni poziv, kjer se lahko neposredno pogovarjate z modelom:

![llama-cli izvaja GLM 4.7 na dveh vozliščih](assets/llama-cli-example.png)
#### llama-server

`llama-server` izpostavi isti sklepalni pogon prek trajnega strežniškega procesa z vgrajenim spletnim vmesnikom in HTTP API-jem, združljivim z OpenAI. To je priporočljiv vmesnik za dolgotrajnejše postavitve, dostop več uporabnikov in integracijo z zunanjimi orodji.

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

> **Iskanje `<RPC_WORKER_IP>`**: Na napravi 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni naslov IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba**: Ta ukaz zaženite v terminalu (Powershell).

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

> **Iskanje `<RPC_WORKER_IP>`**: Na napravi 2 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njen lokalni naslov IP.
<!-- @os:end -->

Ko je zagnan, odprite `http://<HOST_IP>:8081` v brskalniku za dostop do vgrajenega spletnega vmesnika. Ta ponuja klepetalni vmesnik v brskalniku za interakcijo z modelom:

![Spletni vmesnik llama-server, ki izvaja GLM 4.7 na dveh vozliščih](assets/llama-server-example.png)

<!-- @os:linux -->
> **Iskanje `<HOST_IP>`**: Na napravi 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni naslov IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Iskanje `<HOST_IP>`**: Na napravi 1 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njen lokalni naslov IP.
<!-- @os:end -->

#### Referenca parametrov

| Zastavica | Namen |
|------|---------|
| `-m` | Pot do datoteke modela GGUF (uporabite prvi del, `00001-of-00005`) |
| `-c` | Velikost konteksta v žetonih. Večje vrednosti porabijo več pomnilnika |
| `-fa on` | Omogoči rocWMMA Flash Attention za izboljšano zmogljivost na GPU-jih AMD |
| `-ngl 999` | Prenese vse plasti modela na GPU |
| `--no-mmap` | Onemogoči preslikavo pomnilnika (memory-mapping), kar skrajša čase nalaganja, ko velikost modela presega sistemski RAM, a se prilega VRAM-u |
| `--host` | Naslov IP, na katerega se veže `llama-server` (samo `llama-server`) |
| `--port` | Vrata, na katerih se strežе HTTP API (samo `llama-server`) |
| `--rpc` | Z vejico ločen seznam končnih točk delavcev RPC (`IP:port`) |

Za popolno uporabo parametrov glejte [dokumentacijo llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) in [dokumentacijo llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Naslednji koraki

- **Povežite aplikacije tretjih oseb**: `llama-server` izpostavi API, združljiv z OpenAI. Usmerite katero koli aplikacijo, združljivo z OpenAI (na primer Open WebUI), na `http://<HOST_IP>:8081` z nadomestnim ključem API (npr. `none`), da jo povežete s svojim gručo (cluster)
- **Raziščite druge modele**: Prebrskajte kvantizirane GGUF-je na [Hugging Face](https://huggingface.co/models?search=gguf), da poiščete modele, ki se prilegajo skupnemu pomnilniku GPU vaše gruče
- **Razširite na štiri vozlišča**: Dodajte dva dodatna sistema Ryzen AI Halo kot dodatna delavca RPC za dostop do modelov na ravni bilijona parametrov. Podajte dodatne končne točke v `--rpc` kot seznam, ločen z vejicami (npr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)