<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Združevanje dveh sistemov Ryzen™ AI Halo z RPC

## Pregled

Vaš sistem Ryzen™ AI Halo je že zmožen lokalno poganjati velike jezikovne modele. Združevanje v gručo to nadgradi s kombiniranjem pomnilnika GPU več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z močnejšim sklepanjem, boljšim generiranjem kode in globljim večjezičnim razumevanjem – vse skupaj povsem na vaši lastni strojni opremi.

Ta priročnik vas uči, kako združiti dva sistema Ryzen AI Halo v gručo z uporabo RPC pogona llama.cpp in poganjati GLM 4.7, model s 358 milijardami parametrov, na obeh strojih s pospeševanjem AMD ROCm™.

## Kaj se boste naučili

- Kako razširiti dodelitev VRAM na sistemih Ryzen AI Halo
- Namestitev llama.cpp s podporo za ROCm in RPC
- Konfiguracija delavca RPC in zagon porazdeljenega sklepanja na dveh vozliščih
- Poganjanje modela s 358 milijardami parametrov na dveh omrežno povezanih sistemih Ryzen AI Halo

## Nastavitev konfiguracije pomnilnika

> **Opomba**: Ta korak izvedite na obeh strojih – Stroju 1 in Stroju 2.

<!-- @os:windows -->
V sistemu Windows moramo za poganjanje večjih modelov, ki zahtevajo več pomnilnika, uporabiti dodelitev AMD Variable Graphics Memory (iGPU VRAM).

To storite tako, da odprete nadzorno ploščo AMD Software: Adrenalin Edition in se pomaknete na: `Performance > Tuning > AMD Variable Graphics Memory`. Vrednost nastavite na **96 GB**. Za uveljavitev sprememb znova zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V sistemu Linux ROCm uporablja skupni sistemski pomnilniški bazen, ki je privzeto konfiguriran na polovico sistemskega pomnilnika.

To količino je mogoče povečati s spremembo nastavitve strani Translation Table Manager (TTM) jedra, po naslednjih navodilih. AMD priporoča nastavitev minimalnega namenskega VRAM v BIOS-u (0,5 GB).

* Namestite pripomoček pipx in dodajte pot za kolesa, nameščena s pipx, v sistemsko iskalno pot.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite kolo amd-debug-tools iz PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Zaženite orodje amd-ttm za poizvedbo o trenutnih nastavitvah skupnega pomnilnika.
  ```bash
  amd-ttm
  ```

* Znova konfigurirajte nastavitve skupnega pomnilnika na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Znova zaženite sistem, da bodo spremembe začele veljati.


<!-- @os:end -->
<!-- @device:halo_box -->
## Preverite posodobitve programske opreme

<!-- @require:software-update -->
<!-- @device:end -->
## Predpogoji

### Strojna oprema

Ta priročnik zahteva dve enoti Ryzen AI Halo in en stikalo Ethernet, povezano v zvezdasto topologijo, pri čemer je vsaka enota neposredno žično priključena na stikalo.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računska vozlišča, ki tvorijo gručo |
| 10Gbps stikalo Ethernet | 1 | Centralno stikalo za omogočanje komunikacije med vozlišči Ryzen AI Halo (vsaj 2 vrati) |
| Kabel Ethernet | 2 | Poveže vsako enoto Halo s stikalom (priporočen Cat 7 ali višji) |

> **Opomba**: Za povezavo dveh enot Ryzen AI Halo sta potrebni dve vrati stikala Ethernet. Tretja vrata so potrebna, če do modela dostopate z ločenega odjemalskega stroja namesto z ene od enot Halo.

### Programska oprema
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Namestite:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) z delovnim obremenilom **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Namestitev fizične strojne opreme

> **Opomba**: Ta korak izvedite na obeh strojih – Stroju 1 in Stroju 2.

Vsako enoto Ryzen AI Halo povežite s stikalom Ethernet s kablom Cat 7 (ali višjim). S tem vzpostavite 10Gbps povezavo, ki se uporablja za hitro komunikacijo med vozlišči.
<!-- @os:linux -->
### 1. Določite omrežne vmesnike

Na vsakem stroju poiščite ime njegovega omrežnega vmesnika in si ga zabeležite (v nadaljevanju bo naveden kot `IFNAME`). Zaženite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

To neposredno izpiše ime vmesnika, na primer:

```bash
enp191s0
```

### 2. Preverite hitrosti omrežnih povezav

Potrdite, da je povezava aktivna in deluje pri polni hitrosti, tako da preverite hitrost vašega vmesnika:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opomba**: Zamenjajte `<IFNAME>` z imenom izhodnega vmesnika iz razdelka [1. Določite omrežne vmesnike](#1-determine-network-interfaces)

Videti bi morali hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali se povezava ne vzpostavi, preverite kabelsko priključitev in potrdite, da je vrata stikala nastavljeno na 10Gbps. Nekatera stikala zahtevajo onemogočanje samodejnega pogajanja in ročno nastavitev hitrosti povezave; glejte dokumentacijo vašega stikala.

<!-- @os:end -->

<!-- @os:windows -->
### Preverite hitrost omrežne povezave

Na vsakem stroju preverite hitrost povezave vaših omrežnih vmesnikov:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš vmesnik Ethernet bi moral biti `Up` in delovati pri `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Opomba**: Če je hitrost nižja od `10 Gbps` ali se povezava ne vzpostavi, preverite kabelsko priključitev in potrdite, da je vrata stikala nastavljeno na 10Gbps. Nekatera stikala zahtevajo onemogočanje samodejnega pogajanja in ročno nastavitev hitrosti povezave; glejte dokumentacijo vašega stikala.

<!-- @os:end -->

## Namestitev llama.cpp

> **Opomba**: Ta korak izvedite na obeh strojih – Stroju 1 in Stroju 2.

Na voljo sta dve možnosti namestitve:

- [Možnost 1: Lemonade SDK (priporočeno)](#option-1-lemonade-sdk-recommended) – vnaprej zgrajene binarne datoteke, najhitrejša namestitev
- [Možnost 2: Ročna gradnja iz izvorne kode](#option-2-manual-source-build) – gradnja iz izvorne kode s popolnim nadzorom nad zastavicami gradnje

### Možnost 1: Lemonade SDK (priporočeno)

Lemonade SDK zagotavlja nočne gradnje llama.cpp s pospeševanjem AMD ROCm 7, ki ciljajo na GPU-je, kot je gfx1151 (Strix Halo / Ryzen AI Max+ 395) in druge nedavne arhitekture Radeon.

<!-- @os:windows -->
#### Korak 1: Prenesite vnaprej zgrajene binarne datoteke

Pojdite na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in cilju GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka gradnje).

#### Korak 2: Razpakirajte binarne datoteke

Razpakirajte preneseni arhiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ta imenik zdaj vsebuje gradnje `llama-cli.exe`, `llama-server.exe` in `rpc-server.exe` z omogočenim ROCm, predhodno prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverite zaznavanje GPU

```bash
.\llama-cli.exe --list-devices
```

Pričakovani izhod:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Prenesite vnaprej zgrajene binarne datoteke

Pojdite na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in cilju GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka gradnje).

#### Korak 2: Razpakirajte in pripravite binarne datoteke

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ta imenik zdaj vsebuje gradnje `llama-cli`, `llama-server` in `rpc-server` z omogočenim ROCm, predhodno prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverite zaznavanje GPU

```bash
./llama-cli --list-devices
```

Pričakovani izhod:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte z razdelkom [Prenos modela](#downloading-the-model).

### Možnost 2: Ročna gradnja iz izvorne kode

<!-- @os:windows -->
#### Korak 1: Zgradite llama.cpp

Odprite **x64 Native Tools Command Prompt** (nameščen z Visual Studio Build Tools) in klonirajte repozitorij:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Dodajte HIP v svojo pot in zgradite s podporo za ROCm in RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Zastavica gradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programski sklad ROCm/HIP |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DGPU_TARGETS=gfx1151` | Cilja na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Uporablja sistem za gradnjo Ninja |

#### Korak 2: Preverite zaznavanje GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Pričakovani izhod:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Korak 3: Dodajte HIP v svojo uporabniško pot

Zgornji korak gradnje je nastavil `%HIP_PATH%\bin` samo za trenutno sejo. Da bodo knjižnice HIP na voljo v katerem koli terminalu (ne samo v x64 Native Tools Command Prompt), jo trajno dodajte v svojo uporabniško `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte z razdelkom [Prenos modela](#downloading-the-model).
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
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Omogoči rocWMMA za izboljšano Flash Attention na GPU-jih AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Cilja na GPU Ryzen AI Halo (Radeon 8060s) |

Za več možnosti gradnje glejte [dokumentacijo za gradnjo llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Korak 2: Preverite zaznavanje GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Pričakovani izhod:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte z razdelkom [Prenos modela](#downloading-the-model).
<!-- @os:end -->

## Prenos modela

Ta priročnik uporablja [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model s 358 milijardami parametrov v kvantizaciji `Q4_K_XL` od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri tej kvantizaciji model zahteva približno 205 GB prostora za shranjevanje in se prilega skupnemu pomnilniku GPU dveh vozlišč Ryzen AI Halo.

Prenesite datoteke GGUF z uporabo Hugging Face CLI:
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

> **Opomba**: Prenos modela mora biti dokončan na Stroju 1 (krmilniku). Delavska vozlišča RPC ne potrebujejo lokalne kopije datotek modela.

## Zagon modela na gruči

RPC (Remote Procedure Call) pogon llama.cpp omogoča eni instanci llama.cpp, da razloži plasti modela na oddaljene delavce prek omrežja. En stroj deluje kot **krmilnik** (Stroj 1) in skrbi za tokenizacijo, razporejanje in orkestracijo. Drugi stroj poganja lahek **strežnik RPC** (Stroj 2), ki krmilniku izpostavi svoj pomnilnik GPU in računalniške zmogljivosti.

Ob nalaganju llama.cpp razdeli model med obe vozlišči. Ko je naložen, sklepanje poteka, kot da bi teklo na enem pospeševalniku. RPC v ozadju skrbi za prenose tenzorjev in sinhronizacijo.

### Korak 1: Zaženite strežnik RPC (Stroj 2)

Na Stroju 2 zaženite strežnik RPC, da krmilniku izpostavite njegove vire GPU:
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
| `-p` | Vrata, na katerih se oddaja strežnik RPC |
| `-c` | Omogoči lokalni predpomnilnik za velike tenzorje in se s tem izogne ponavljajočim se omrežnim prenosom med nalaganjem modela |
| `--host` | Naslov IP, na katerega se poveže strežnik RPC (`0.0.0.0` za vse vmesnike) |

Za več možnosti glejte [dokumentacijo llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Zaženite model (Stroj 1)

Ko strežnik RPC teče na Stroju 2, zaženite sklepanje s Stroja 1 z uporabo `llama-cli` ali `llama-server`.

#### llama-cli

`llama-cli` zagotavlja terminalski vmesnik za neposredno interakcijo z modelom. Idealen je za primerjalno testiranje, odpravljanje napak in nizkonivojsko eksperimentiranje.

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

> **Iskanje `<RPC_WORKER_IP>`**: Na Stroju 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni naslov IP.
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

> **Iskanje `<RPC_WORKER_IP>`**: Na Stroju 2 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njegov lokalni naslov IP.

<!-- @os:end -->

Ko se zažene, `llama-cli` prikaže napredek nalaganja modela in vstopi v interaktivni poziv, kjer se lahko neposredno pogovarjate z modelom:

![llama-cli, ki poganja GLM 4.7 na dveh vozliščih](assets/llama-cli-example.png)

#### llama-server

`llama-server` izpostavi isti sklepalni pogon prek trajnega strežniškega procesa z integriranim spletnim vmesnikom in HTTP API-jem, združljivim z OpenAI. To je prednostni vmesnik za daljše namestitve, dostop več uporabnikov in integracijo z zunanjimi orodji.

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

> **Iskanje `<RPC_WORKER_IP>`**: Na Stroju 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni naslov IP.
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

> **Iskanje `<RPC_WORKER_IP>`**: Na Stroju 2 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njegov lokalni naslov IP.
<!-- @os:end -->

Ko se zažene, odprite `http://<HOST_IP>:8081` v brskalniku za dostop do vgrajenega spletnega vmesnika. Ta zagotavlja brskalniški klepetalni vmesnik za interakcijo z modelom:

![Spletni vmesnik llama-server, ki poganja GLM 4.7 na dveh vozliščih](assets/llama-server-example.png)

<!-- @os:linux -->
> **Iskanje `<HOST_IP>`**: Na Stroju 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni naslov IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Iskanje `<HOST_IP>`**: Na Stroju 1 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njegov lokalni naslov IP.
<!-- @os:end -->

#### Referenca parametrov

| Zastavica | Namen |
|------|---------|
| `-m` | Pot do datoteke modela GGUF (uporabite prvi delček, `00001-of-00005`) |
| `-c` | Velikost konteksta v žetonih. Večje vrednosti porabijo več pomnilnika |
| `-fa on` | Omogoči rocWMMA Flash Attention za izboljšano zmogljivost na GPU-jih AMD |
| `-ngl 999` | Razloži vse plasti modela na GPU |
| `--no-mmap` | Onemogoči preslikavo pomnilnika, kar skrajša čase nalaganja, ko velikost modela presega sistemski RAM, a se prilega v VRAM |
| `--host` | IP, na katerega se poveže `llama-server` (samo `llama-server`) |
| `--port` | Vrata za strežbo HTTP API-ja (samo `llama-server`) |
| `--rpc` | Z vejicami ločen seznam končnih točk delavcev RPC (`IP:vrata`) |

Za celotno uporabo parametrov glejte [dokumentacijo llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) in [dokumentacijo llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Naslednji koraki

- **Povežite aplikacije tretjih oseb**: `llama-server` izpostavi API, združljiv z OpenAI. Usmerite katero koli aplikacijo, združljivo z OpenAI (kot je Open WebUI), na `http://<HOST_IP>:8081` s katerim koli nadomestnim ključem API (npr. `none`), da se povežete z vašo gručo
- **Raziščite druge modele**: Brskajte po kvantiziranih datotekah GGUF na [Hugging Face](https://huggingface.co/models?search=gguf), da poiščete modele, ki se prilegajo skupnemu pomnilniku GPU vaše gruče
- **Razširite na štiri vozlišča**: Dodajte še dva sistema Ryzen AI Halo kot dodatna delavca RPC za dostop do modelov na ravni 1 bilijona parametrov. Posredujte dodatne končne točke v `--rpc` kot seznam, ločen z vejicami (npr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)