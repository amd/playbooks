<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Povezovanje dveh sistemov Ryzen™ AI Halo v gručo z RPC

## Pregled

Vaš sistem Ryzen™ AI Halo je že sposoben lokalno poganjati velike jezikovne modele. Povezovanje v gručo (clustering) to nadgradi tako, da združi pomnilnik GPU več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z močnejšim sklepanjem, boljšim generiranjem kode in globljim razumevanjem več jezikov, vse povsem na vaši lastni strojni opremi.

Ta priročnik vas nauči, kako v gručo povezati dva sistema Ryzen AI Halo z uporabo RPC mehanizma llama.cpp in poganjati GLM 4.7, model s 358 milijardami parametrov, na obeh napravah hkrati z pospeševanjem AMD ROCm™.

## Kaj se boste naučili

- Kako razširiti dodelitev pomnilnika VRAM na sistemih Ryzen AI Halo
- Namestitev llama.cpp s podporo za ROCm in RPC
- Konfiguracija delavca RPC (RPC worker) in zagon porazdeljenega sklepanja med dvema vozliščema
- Poganjanje modela s 358 milijardami parametrov na dveh omreženih sistemih Ryzen AI Halo

## Nastavitev konfiguracije pomnilnika

> **Opomba**: Ta korak izvedite na obeh napravah, Machine 1 in Machine 2.

<!-- @os:windows -->
V sistemu Windows moramo za poganjanje večjih modelov, ki zahtevajo več pomnilnika, uporabiti dodelitev AMD Variable Graphics Memory (iGPU VRAM).

To storite tako, da odprete nadzorno ploščo AMD Software: Adrenalin Edition in se pomaknete do: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavite vrednost na **96 GB**. Za uveljavitev sprememb sistem ponovno zaženite.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V sistemu Linux ROCm uporablja skupen pomnilniški bazen sistema, ta bazen pa je privzeto konfiguriran na polovico sistemskega pomnilnika.

To količino lahko povečate s spremembo nastavitve strani Translation Table Manager (TTM) v jedru, in sicer po naslednjih navodilih. AMD priporoča, da v BIOS-u nastavite minimalen namenski VRAM (0,5 GB).

* Namestite pripomoček pipx in dodajte pot za paketke, nameščene s pipx, v iskalno pot sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite paket amd-debug-tools iz PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Zaženite orodje amd-ttm za poizvedbo o trenutnih nastavitvah skupnega pomnilnika.
  ```bash
  amd-ttm
  ```

* Ponovno konfigurirajte nastavitve skupnega pomnilnika na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Za uveljavitev sprememb sistem ponovno zaženite.


<!-- @os:end -->
<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->
## Predpogoji

### Strojna oprema

Ta priročnik zahteva dve enoti Ryzen AI Halo in eno omrežno stikalo (Ethernet switch), povezane v zvezdno topologijo, pri čemer je vsaka enota povezana neposredno s stikalom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računalniška vozlišča, ki sestavljata gručo |
| 10 Gbps omrežno stikalo | 1 | Centralno stikalo, ki omogoča komunikacijo med več vozlišči Ryzen AI Halo (vsaj 2 vrat) |
| Ethernet kabel | 2 | Povezuje vsako enoto Halo s stikalom (priporočeno Cat 7 ali višje) |

> **Opomba**: Za povezavo obeh enot Ryzen AI Halo sta potrebni dve vrati omrežnega stikala. Tretja vrata so potrebna, če do modela dostopate z ločenega odjemalskega računalnika namesto z ene od enot Halo.

### Programska oprema
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Namestite:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) z delovnim okoljem **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizična namestitev strojne opreme

> **Opomba**: Ta korak izvedite na obeh napravah, Machine 1 in Machine 2.

Vsako enoto Ryzen AI Halo povežite z omrežnim stikalom prek kabla Cat 7 (ali višje). S tem vzpostavite 10 Gbps povezavo, ki se uporablja za visokohitrostno komunikacijo med vozlišči.
<!-- @os:linux -->
### 1. Ugotovitev omrežnih vmesnikov

Na vsakem računalniku poiščite ime njegovega omrežnega vmesnika in si ga zapišite (v nadaljevanju se bo imenoval `IFNAME`). Zaženite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

To izpiše ime vmesnika neposredno, na primer:

```bash
enp191s0
```

### 2. Preverjanje hitrosti omrežne povezave

Potrdite, da je povezava aktivna in deluje s polno hitrostjo, tako da preverite hitrost svojega vmesnika:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opomba**: Zamenjajte `<IFNAME>` z imenom izhodnega vmesnika iz [1. Ugotovitev omrežnih vmesnikov](#1-determine-network-interfaces)

Videti bi morali hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali povezava ne vzpostavi, preverite povezavo kabla in potrdite, da so vrata stikala nastavljena na 10 Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje (auto-negotiation) in hitrost povezave nastavite ročno; za več informacij glejte dokumentacijo svojega stikala.

<!-- @os:end -->

<!-- @os:windows -->
### Preverjanje hitrosti omrežne povezave

Na vsakem računalniku preverite hitrost povezave svojih omrežnih vmesnikov:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš Ethernet vmesnik bi moral biti `Up` in delovati pri `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Opomba**: Če je hitrost nižja od `10 Gbps` ali povezava ne vzpostavi, preverite povezavo kabla in potrdite, da so vrata stikala nastavljena na 10 Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje (auto-negotiation) in hitrost povezave nastavite ročno; za več informacij glejte dokumentacijo svojega stikala.

<!-- @os:end -->

## Nameščanje llama.cpp

> **Opomba**: Ta korak izvedite na obeh napravah, Machine 1 in Machine 2.

Na voljo sta dve možnosti namestitve:

- [Možnost 1: Lemonade SDK (priporočeno)](#option-1-lemonade-sdk-recommended) - vnaprej zgrajene binarne datoteke, najhitrejša nastavitev
- [Možnost 2: Ročna gradnja iz izvorne kode](#option-2-manual-source-build) - gradnja iz izvorne kode s popolnim nadzorom nad gradbenimi zastavicami

### Možnost 1: Lemonade SDK (priporočeno)

Lemonade SDK zagotavlja nočne (nightly) gradnje llama.cpp s pospeševanjem AMD ROCm 7, namenjene GPU-jem, kot sta gfx1151 (Strix Halo / Ryzen AI Max+ 395) in drugim novejšim arhitekturam Radeon.

<!-- @os:windows -->
#### Korak 1: Prenesite vnaprej zgrajene binarne datoteke

Pojdite na stran z zadnjo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljnemu GPE-ju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka gradnje).

#### Korak 2: Razpakirajte binarne datoteke

Razširite preneseni arhiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ta imenik zdaj vsebuje z ROCm omogočene gradnje `llama-cli.exe`, `llama-server.exe` in `rpc-server.exe`, prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverite zaznavo GPE-ja

```bash
.\llama-cli.exe --list-devices
```

Pričakovani izpis:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Prenesite vnaprej zgrajene binarne datoteke

Pojdite na stran z zadnjo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljnemu GPE-ju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka gradnje).

#### Korak 2: Razpakirajte in pripravite binarne datoteke

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ta imenik zdaj vsebuje z ROCm omogočene gradnje `llama-cli`, `llama-server` in `rpc-server`, prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverite zaznavo GPE-ja

```bash
./llama-cli --list-devices
```

Pričakovani izpis:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s [Prenašanjem modela](#downloading-the-model).

### Možnost 2: Ročna gradnja iz izvorne kode

<!-- @os:windows -->
#### Korak 1: Zgradite llama.cpp

Odprite **x64 Native Tools Command Prompt** (nameščen skupaj z Visual Studio Build Tools) in klonirajte repozitorij:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Dodajte HIP na svojo pot in zgradite s podporo za ROCm in RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Zastavica gradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programski sklad ROCm/HIP |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DGPU_TARGETS=gfx1151` | Cilja na GPE Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Uporablja gradbeni sistem Ninja |

#### Korak 2: Preverite zaznavo GPE-ja

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Pričakovani izpis:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Korak 3: Dodajte HIP v svojo uporabniško pot

Zgornji korak gradnje je nastavil `%HIP_PATH%\bin` samo za trenutno sejo. Da bodo knjižnice HIP na voljo v katerem koli terminalu (ne le v x64 Native Tools Command Prompt), jih trajno dodajte v svojo uporabniško spremenljivko `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s [Prenašanjem modela](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Zgradite llama.cpp

Klonirajte repozitorij:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Zgradite s podporo za ROCm in RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Zastavica gradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programski sklad ROCm |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Omogoči rocWMMA za izboljšano funkcijo Flash Attention na GPE-jih AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Cilja na GPE Ryzen AI Halo (Radeon 8060s) |

Za več možnosti gradnje glejte [dokumentacijo za gradnjo llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Korak 2: Preverite zaznavo GPE-ja

```bash
cd rocm/bin
./llama-cli --list-devices
```

Pričakovani izpis:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s [Prenašanjem modela](#downloading-the-model).
<!-- @os:end -->

## Prenašanje modela

Ta priročnik uporablja [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model s 358 milijardami parametrov v kvantizaciji `Q4_K_XL` podjetja [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri tej kvantizaciji model potrebuje približno 205 GB prostora za shranjevanje in se prilega skupnemu pomnilniku GPE-ja dveh vozlišč Ryzen AI Halo.

Prenesite datoteke GGUF z uporabo vmesnika Hugging Face CLI:
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

> **Opomba**: Prenos modela mora biti opravljen na Napravi 1 (krmilnik). Delovna vozlišča RPC ne potrebujejo lokalne kopije datotek modela.

## Zagon modela v grozdu

Motor llama.cpp RPC (Remote Procedure Call) omogoča, da en sam primerek llama.cpp razbremeni plasti modela na oddaljene delovne enote prek omrežja. Ena naprava deluje kot **krmilnik** (Naprava 1), ki skrbi za tokenizacijo, razporejanje in orkestracijo. Druga naprava izvaja lahek **strežnik RPC** (Naprava 2), ki izpostavi svoj pomnilnik GPE-ja in računsko zmogljivost krmilniku.

Ob nalaganju llama.cpp razdeli model med obe vozlišči. Ko je model naložen, sklepanje poteka, kot da bi teklo na enem samem pospeševalniku. RPC v ozadju skrbi za prenose tenzorjev in sinhronizacijo.

### Korak 1: Zaženite strežnik RPC (Naprava 2)

Na Napravi 2 zaženite strežnik RPC, da izpostavite njene vire GPE-ja krmilniku:
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

| Zastavica | Namen |
|------|---------|
| `-p` | Vrata, na katerih se oddaja strežnik RPC |
| `-c` | Omogoči lokalni predpomnilnik za velike tenzorje, s čimer se izogne ponavljajočim se omrežnim prenosom med nalaganjem modela |
| `--host` | IP naslov, na katerega je vezan strežnik RPC (`0.0.0.0` za vse vmesnike) |

Za več možnosti glejte [dokumentacijo llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Zaženite model (Naprava 1)

Ko strežnik RPC teče na Napravi 2, zaženite sklepanje z Naprave 1 z uporabo bodisi `llama-cli` bodisi `llama-server`.

#### llama-cli

`llama-cli` ponuja vmesnik na osnovi terminala za neposredno interakcijo z modelom. Idealen je za primerjalno testiranje, odpravljanje napak in eksperimentiranje na nizki ravni.

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

> **Iskanje `<RPC_WORKER_IP>`**: Na Napravi 2 zaženite `hostname -I | awk '{print $1}'`, da najdete njen lokalni IP naslov.
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba**: Ta ukaz zaženite v terminalu (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Iskanje `<RPC_WORKER_IP>`**: Na Napravi 2 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da najdete njen lokalni IP naslov.

<!-- @os:end -->

Ko teče, `llama-cli` prikaže napredek nalaganja modela in vstopi v interaktivni poziv, kjer se lahko neposredno pogovarjate z modelom:

![llama-cli poganja GLM 4.7 na dveh vozliščih](assets/llama-cli-example.png)
#### llama-server

`llama-server` izpostavi isti sklepalni pogon prek trajnega strežniškega procesa z vgrajenim spletnim vmesnikom (web UI) in HTTP API-jem, združljivim z OpenAI. To je priporočen vmesnik za dolgotrajnejše postavitve, dostop več uporabnikov in integracijo z zunanjimi orodji.

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

> **Iskanje `<RPC_WORKER_IP>`**: Na Napravi 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni naslov IP.
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

> **Iskanje `<RPC_WORKER_IP>`**: Na Napravi 2 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njen lokalni naslov IP.
<!-- @os:end -->

Ko je zagnan, odprite `http://<HOST_IP>:8081` v svojem brskalniku za dostop do vgrajenega spletnega vmesnika. Ta ponuja klepetalni vmesnik, ki temelji na brskalniku, za interakcijo z modelom:

![Spletni vmesnik llama-server, ki poganja GLM 4.7 na dveh vozliščih](assets/llama-server-example.png)

<!-- @os:linux -->
> **Iskanje `<HOST_IP>`**: Na Napravi 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni naslov IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Iskanje `<HOST_IP>`**: Na Napravi 1 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njen lokalni naslov IP.
<!-- @os:end -->

#### Sklic na parametre

| Zastavica | Namen |
|------|---------|
| `-m` | Pot do datoteke modela GGUF (uporabite prvi del, `00001-of-00005`) |
| `-c` | Velikost konteksta v žetonih. Večje vrednosti porabijo več pomnilnika |
| `-fa on` | Omogoči rocWMMA Flash Attention za izboljšano zmogljivost na grafičnih procesorjih AMD |
| `-ngl 999` | Naloži vse plasti modela na GPU |
| `--no-mmap` | Onemogoči preslikavo pomnilnika (memory-mapping), kar skrajša čase nalaganja, kadar velikost modela presega sistemski RAM, vendar se prilega v VRAM |
| `--host` | Naslov IP, na katerega se veže `llama-server` (samo `llama-server`) |
| `--port` | Vrata, na katerih se strežе HTTP API (samo `llama-server`) |
| `--rpc` | Z vejico ločen seznam končnih točk delavcev RPC (`IP:port`) |

Za popoln pregled uporabe parametrov si oglejte [dokumentacijo llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) in [dokumentacijo llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Naslednji koraki

- **Povežite aplikacije tretjih oseb**: `llama-server` izpostavi API, združljiv z OpenAI. Usmerite katero koli aplikacijo, združljivo z OpenAI (na primer Open WebUI), na `http://<HOST_IP>:8081` s poljubnim rezervnim ključem API (npr. `none`), da se povežete s svojim gručo
- **Raziščite druge modele**: Prebrskajte kvantizirane GGUF-je na [Hugging Face](https://huggingface.co/models?search=gguf), da poiščete modele, ki se prilegajo skupnemu pomnilniku GPU vaše gruče
- **Razširite na štiri vozlišča**: Dodajte še dva sistema Ryzen AI Halo kot dodatna delavca RPC za dostop do modelov v razredu 1 bilijona parametrov. Dodatne končne točke posredujte parametru `--rpc` kot seznam, ločen z vejicami (npr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)