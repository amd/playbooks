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

# Gručenje dveh Ryzen™ AI Halo sistemov z RPC

## Pregled

Vaš Ryzen™ AI Halo že zdaj omogoča lokalno zaganjanje velikih jezikovnih modelov. Gručenje to zmožnost razširi še dlje, saj združuje pomnilnik GPU več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z boljšim sklepanjem, boljšim generiranjem kode in globljim večjezičnim razumevanjem – vse to popolnoma na vaši lastni strojni opremi.

Ta vodnik vas nauči, kako gručiti dva sistema Ryzen AI Halo z uporabo mehanizma RPC iz llama.cpp in kako zagnati GLM 4.7, model s 358 milijardami parametrov, na obeh napravah hkrati z pospeševanjem AMD ROCm™.

## Kaj se boste naučili

- Kako razširiti dodelitev pomnilnika VRAM na sistemih Ryzen AI Halo
- Namestitev llama.cpp s podporo za ROCm in RPC
- Konfiguriranje delavca RPC in zagon porazdeljenega sklepanja med dvema vozliščema
- Zagon modela s 358 milijardami parametrov na dveh povezanih sistemih Ryzen AI Halo v omrežju

## Nastavitev konfiguracije pomnilnika

> **Opomba**: Ta korak izvedite na Napravi 1 in Napravi 2.

<!-- @os:windows -->
V sistemu Windows moramo za zagon večjih modelov, ki zahtevajo več pomnilnika, uporabiti dodelitev AMD Variable Graphics Memory (iGPU VRAM).

To storite tako, da odprete nadzorno ploščo AMD Software: Adrenalin Edition in se pomaknete na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavite vrednost na **96 GB**. Sistem ponovno zaženite, da se spremembe uveljavijo.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V sistemu Linux ROCm uporablja skupni pomnilniški bazen sistema, ta bazen pa je privzeto nastavljen na polovico sistemskega pomnilnika.

To količino je mogoče povečati s spremembo nastavitve strani upravitelja Translation Table Manager (TTM) jedra po naslednjih navodilih. AMD priporoča, da v BIOS-u nastavite minimalni namenski VRAM (0,5 GB).

* Namestite orodje pipx in dodajte pot za wheel pakete, nameščene s pipx, v sistemsko iskalno pot.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite wheel paket amd-debug-tools iz PyPI.
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

* Ponovno zaženite sistem, da se spremembe uveljavijo.


<!-- @os:end -->
<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->
## Predpogoji

### Strojna oprema

Ta vodnik zahteva dve enoti Ryzen AI Halo in eno stikalo Ethernet, povezani v zvezdno topologijo, pri čemer je vsaka enota povezana neposredno s stikalom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računalniška vozlišča, ki tvorita gručo |
| 10Gbps stikalo Ethernet | 1 | Osrednje stikalo, ki omogoča komunikacijo med večimi vozlišči Ryzen AI Halo (vsaj 2 vrat) |
| Kabel Ethernet | 2 | Povezuje vsako enoto Halo s stikalom (priporočen Cat 7 ali višji) |

> **Opomba**: Za povezavo obeh enot Ryzen AI Halo sta potrebni dve vrata stikala Ethernet. Tretja vrata so potrebna, če do modela dostopate z ločenega odjemalskega računalnika namesto z ene od enot Halo.

### Programska oprema
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Namestite naslednje:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) z delovnim tokom **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizična nastavitev strojne opreme

> **Opomba**: Ta korak izvedite na Napravi 1 in Napravi 2.

Povežite vsako enoto Ryzen AI Halo s stikalom Ethernet z uporabo kabla Cat 7 (ali višjega). S tem vzpostavite 10Gbps povezavo, ki se uporablja za hitro komunikacijo med vozlišči.
<!-- @os:linux -->
### 1. Določitev omrežnih vmesnikov

Na vsaki napravi poiščite ime njenega omrežnega vmesnika in si ga zapišite (v nadaljevanju bo imenovan `IFNAME`). Zaženite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

To izpiše ime vmesnika neposredno, na primer:

```bash
enp191s0
```

### 2. Preverjanje hitrosti omrežne povezave

Preverite, da je povezava aktivna in deluje s polno hitrostjo, tako da preverite hitrost vašega vmesnika:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opomba**: Zamenjajte `<IFNAME>` z imenom izhodnega vmesnika iz [1. Določitev omrežnih vmesnikov](#1-determine-network-interfaces)

Videti bi morali hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali če povezava ne vzpostavi, preverite povezavo kabla in potrdite, da so vrata stikala nastavljena na 10Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje in hitrost povezave nastavite ročno; glejte dokumentacijo svojega stikala.

<!-- @os:end -->

<!-- @os:windows -->
### Preverjanje hitrosti omrežne povezave

Na vsaki napravi preverite hitrost povezave svojih omrežnih vmesnikov:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš vmesnik Ethernet bi moral biti `Up` in delovati s hitrostjo `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Opomba**: Če je hitrost nižja od `10 Gbps` ali če povezava ne vzpostavi, preverite povezavo kabla in potrdite, da so vrata stikala nastavljena na 10Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje in hitrost povezave nastavite ročno; glejte dokumentacijo svojega stikala.

<!-- @os:end -->

## Namestitev llama.cpp

> **Opomba**: Ta korak izvedite na Napravi 1 in Napravi 2.

Na voljo sta dve možnosti namestitve:

- [Možnost 1: Lemonade SDK (priporočeno)](#option-1-lemonade-sdk-recommended) – vnaprej zgrajene binarne datoteke, najhitrejša nastavitev
- [Možnost 2: Ročna izgradnja iz vira](#option-2-manual-source-build) – izgradnja iz izvorne kode s popolnim nadzorom nad zastavicami izgradnje

### Možnost 1: Lemonade SDK (priporočeno)

Lemonade SDK zagotavlja nočne (nightly) izgradnje llama.cpp s pospeševanjem AMD ROCm 7, namenjene GPU-jem, kot je gfx1151 (Strix Halo / Ryzen AI Max+ 395), in drugim novejšim arhitekturam Radeon.

<!-- @os:windows -->
#### Korak 1: Prenesite vnaprej izdelane binarne datoteke

Pojdite na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljni GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka izdaje).

#### Korak 2: Razpakirajte binarne datoteke

Razpakirajte prenešeni arhiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ta mapa zdaj vsebuje z ROCm omogočene gradnje `llama-cli.exe`, `llama-server.exe` in `rpc-server.exe`, ki so prevnaprej prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverite zaznavo GPE

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
#### Korak 1: Prenesite vnaprej izdelane binarne datoteke

Pojdite na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljni GPE:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka izdaje).

#### Korak 2: Razpakirajte in pripravite binarne datoteke

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ta mapa zdaj vsebuje z ROCm omogočene gradnje `llama-cli`, `llama-server` in `rpc-server`, ki so prevnaprej prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverite zaznavo GPE

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
Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s [Prenos modela](#downloading-the-model).

### Možnost 2: Ročna gradnja iz izvorne kode

<!-- @os:windows -->
#### Korak 1: Zgradite llama.cpp

Odprite **x64 Native Tools Command Prompt** (nameščen skupaj z Visual Studio Build Tools) in klonirajte repozitorij:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Dodajte HIP na svojo pot in zgradite s podporo ROCm in RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Zastavica gradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programski sklad ROCm/HIP |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DGPU_TARGETS=gfx1151` | Cilja GPE Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Uporablja sistem gradnje Ninja |

#### Korak 2: Preverite zaznavo GPE

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

#### Korak 3: Dodajte HIP na svojo uporabniško pot

Zgornji korak gradnje je nastavil `%HIP_PATH%\bin` samo za trenutno sejo. Da bodo knjižnice HIP na voljo v katerem koli terminalu (ne samo v x64 Native Tools Command Prompt), jih trajno dodajte v uporabniško `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s [Prenos modela](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Zgradite llama.cpp

Klonirajte repozitorij:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Zgradite s podporo ROCm in RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Zastavica gradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programski sklad ROCm |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DAMDGPU_TARGETS="gfx1151"` | Cilja GPE Ryzen AI Halo (Radeon 8060s) |

Za več možnosti gradnje glejte [dokumentacijo za gradnjo llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Korak 2: Preverite zaznavo GPE

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

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s [Prenos modela](#downloading-the-model).
<!-- @os:end -->

## Prenos modela

Ta priročnik uporablja [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model s 358 milijardami parametrov v kvantizaciji `Q4_K_XL` podjetja [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri tej kvantizaciji model zahteva približno 205 GB prostora za shranjevanje in se prilega skupnemu pomnilniku GPE dveh vozlišč Ryzen AI Halo.

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

> **Opomba**: Prenos modela je treba dokončati na napravi 1 (krmilniku). Delovna vozlišča RPC ne potrebujejo lokalne kopije datotek modela.

## Zagon modela v gruči

Mehanizem llama.cpp RPC (Remote Procedure Call) omogoča, da ena sama instanca llama.cpp razbremeni plasti modela na oddaljene delavce prek omrežja. Ena naprava deluje kot **krmilnik** (naprava 1), ki skrbi za tokenizacijo, razporejanje in orkestracijo. Druga naprava izvaja lahek **strežnik RPC** (naprava 2), ki krmilniku izpostavi svoj pomnilnik GPE in računsko zmogljivost.

Ob nalaganju llama.cpp razdeli model med obe vozlišči. Ko je model naložen, sklepanje poteka, kot da bi teklo na enem samem pospeševalniku. RPC v ozadju upravlja s prenosi tenzorjev in sinhronizacijo.

### Korak 1: Zaženite strežnik RPC (naprava 2)

Na napravi 2 zaženite strežnik RPC, da krmilniku izpostavite njene vire GPE:
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
| `-c` | Omogoči lokalni predpomnilnik za velike tenzorje, s čimer se izognemo ponavljajočim se omrežnim prenosom med nalaganjem modela |
| `--host` | Naslov IP, na katerega je vezan strežnik RPC (`0.0.0.0` za vse vmesnike) |

Za več možnosti glejte [dokumentacijo za llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Zaženite model (naprava 1)

Ko strežnik RPC teče na napravi 2, zaženite sklepanje z naprave 1 z uporabo `llama-cli` ali `llama-server`.

#### llama-cli

`llama-cli` ponuja terminalski vmesnik za neposredno interakcijo z modelom. Idealen je za primerjalno testiranje, odpravljanje napak in nizkonivojsko eksperimentiranje.

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

> **Iskanje `<RPC_WORKER_IP>`**: Na napravi 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni naslov IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba**: Ta ukaz zaženite v terminalu (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Iskanje `<RPC_WORKER_IP>`**: Na napravi 2 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njen lokalni naslov IP.

<!-- @os:end -->

Ko teče, `llama-cli` prikaže napredek nalaganja modela in odpre interaktivni poziv, kjer se lahko pogovarjate neposredno z modelom:

![llama-cli, ki izvaja GLM 4.7 na dveh vozliščih](assets/llama-cli-example.png)
#### llama-server

`llama-server` izpostavi isti sklep prek trajnega strežniškega procesa z integriranim spletnim vmesnikom in HTTP API-jem, združljivim z OpenAI. To je priporočeni vmesnik za dolgotrajnejše uvedbe, dostop več uporabnikov in povezovanje z zunanjimi orodji.

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
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Iskanje `<RPC_WORKER_IP>`**: Na Napravi 2 v terminalu (Powershell) zaženite `ipconfig | findstr /C:"IPv4"`, da poiščete njen lokalni naslov IP.
<!-- @os:end -->

Ko se strežnik zažene, odprite `http://<HOST_IP>:8081` v brskalniku za dostop do vgrajenega spletnega vmesnika. Ta ponuja klepetalni vmesnik v brskalniku za interakcijo z modelom:

![Spletni vmesnik llama-server, ki poganja GLM 4.7 na dveh vozliščih](assets/llama-server-example.png)

<!-- @os:linux -->
> **Iskanje `<HOST_IP>`**: Na Napravi 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni naslov IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Iskanje `<HOST_IP>`**: Na Napravi 1 v terminalu (Powershell) zaženite `ipconfig | findstr /C:"IPv4"`, da poiščete njen lokalni naslov IP.
<!-- @os:end -->

#### Referenca parametrov

| Zastavica | Namen |
|------|---------|
| `-m` | Pot do datoteke modela GGUF (uporabite prvi del, `00001-of-00005`) |
| `-c` | Velikost konteksta v žetonih. Večje vrednosti porabijo več pomnilnika |
| `-fa on` | Omogoči rocWMMA Flash Attention za izboljšano zmogljivost na GPE-jih AMD |
| `-ngl 999` | Prenese vse plasti modela na GPE |
| `-lm none` | Nastavi način nalaganja modela na `none`, kar onemogoči preslikavo pomnilnika (memory-mapping) za krajše čase nalaganja, kadar velikost modela presega sistemski RAM, vendar se prilega v VRAM |
| `--host` | Naslov IP, na katerega naj se `llama-server` poveže (samo za `llama-server`) |
| `--port` | Vrata za posredovanje HTTP API-ja (samo za `llama-server`) |
| `--rpc` | Z vejico ločen seznam končnih točk delavcev RPC (`IP:port`) |

Za popolno uporabo parametrov glejte [dokumentacijo za llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) in [dokumentacijo za llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Naslednji koraki

- **Povežite aplikacije tretjih oseb**: `llama-server` izpostavi API, združljiv z OpenAI. Usmerite katero koli aplikacijo, združljivo z OpenAI (na primer Open WebUI), na `http://<HOST_IP>:8081` z nadomestnim ključem API po meri (npr. `none`), da jo povežete s svojim gručo
- **Raziščite druge modele**: Prebrskajte kvantizirane datoteke GGUF na [Hugging Face](https://huggingface.co/models?search=gguf), da poiščete modele, ki se prilegajo skupnemu pomnilniku GPE vaše gruče
- **Razširite na štiri vozlišča**: Dodajte še dva sistema Ryzen AI Halo kot dodatna delavca RPC za dostop do modelov v velikostnem razredu bilijona parametrov. Podajte dodatne končne točke za `--rpc` kot z vejico ločen seznam (npr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)