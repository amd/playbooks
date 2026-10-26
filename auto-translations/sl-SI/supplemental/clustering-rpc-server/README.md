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

# Gručenje dveh naprav Ryzen™ AI Halo z RPC

## Pregled

Vaš Ryzen™ AI Halo je že sposoben lokalno zaganjati velike jezikovne modele. Gručenje to zmožnost popelje še dlje, saj združi pomnilnik GPE več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z močnejšim sklepanjem, boljšim generiranjem kode in globljim razumevanjem več jezikov – vse to popolnoma na vaši lastni strojni opremi.

Ta vodnik vas nauči, kako združiti dva sistema Ryzen AI Halo v gručo z uporabo RPC pogona iz llama.cpp ter zagnati GLM 4.7, model s 358 milijardami parametrov, na obeh napravah hkrati z pospeševanjem AMD ROCm™.

## Kaj se boste naučili

- Kako razširiti dodelitev pomnilnika VRAM na sistemih Ryzen AI Halo
- Namestitev llama.cpp s podporo za ROCm in RPC
- Konfiguracijo delavca RPC in zagon porazdeljenega sklepanja na dveh vozliščih
- Zagon modela s 358 milijardami parametrov na dveh medsebojno povezanih sistemih Ryzen AI Halo

## Nastavitev konfiguracije pomnilnika

> **Opomba**: Ta korak izvedite na obeh napravah, Machine 1 in Machine 2.

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Zagon modelov blizu ali nad 128 GB:** Na sistemih AMD Ryzen™ AI Max 400 Series (Gorgon Halo) z operacijskim sistemom Windows modeli, ki se približujejo ali presegajo 128 GB pomnilnika, za brezhibno delovanje zahtevajo dodatno konfiguracijo. Pred nalaganjem modela sledite navodilom v dokumentu [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines).
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
V operacijskem sistemu Windows moramo za zagon večjih modelov, ki zahtevajo več pomnilnika, uporabiti dodelitev pomnilnika AMD Variable Graphics Memory (iGPU VRAM).

To storite tako, da odprete nadzorno ploščo AMD Software: Adrenalin Edition in se pomaknete na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavite vrednost na **96 GB**. Za uveljavitev sprememb ponovno zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V sistemu Linux ROCm uporablja skupen pomnilniški bazen sistemskega pomnilnika, ki je privzeto nastavljen na polovico sistemskega pomnilnika.

To vrednost lahko povečate tako, da spremenite nastavitev strani jedrnega upravitelja prevodnih tabel (Translation Table Manager – TTM), kot je opisano v naslednjih navodilih. AMD priporoča, da v BIOS-u nastavite minimalni namenski VRAM (0,5 GB).

* Namestite orodje pipx in dodajte pot do paketov, nameščenih s pipx, v sistemsko iskalno pot.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite paket amd-debug-tools iz PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Zaženite orodje amd-ttm, da preverite trenutne nastavitve skupnega pomnilnika.
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
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->
## Predpogoji

### Strojna oprema

Ta vodnik zahteva dve napravi Ryzen AI Halo in eno Ethernet stikalo, povezani v zvezdasto topologijo, pri čemer je vsaka naprava neposredno povezana s stikalom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računska vozlišča, ki tvorita gručo |
| 10Gbps Ethernet stikalo | 1 | Centralno stikalo, ki omogoča komunikacijo med več vozlišči Ryzen AI Halo (vsaj 2 vrat) |
| Ethernet kabel | 2 | Povezuje vsako napravo Halo s stikalom (priporočena kategorija Cat 7 ali višja) |

> **Opomba**: Za povezavo obeh naprav Ryzen AI Halo sta potrebni dve vrati Ethernet stikala. Tretja vrata so potrebna, če do modela dostopate z ločene odjemalske naprave in ne z ene od naprav Halo.

### Programska oprema
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Namestite:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) z delovno obremenitvijo **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Namestitev fizične strojne opreme

> **Opomba**: Ta korak izvedite na obeh napravah, Machine 1 in Machine 2.

Vsako napravo Ryzen AI Halo povežite z Ethernet stikalom s kablom kategorije Cat 7 (ali višje). S tem vzpostavite 10Gbps povezavo, ki se uporablja za visokohitrostno komunikacijo med vozlišči.
<!-- @os:linux -->
### 1. Določitev omrežnih vmesnikov

Na vsaki napravi poiščite ime njenega omrežnega vmesnika in si ga zapišite (v nadaljevanju bo poimenovano `IFNAME`). Zaženite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

To neposredno izpiše ime vmesnika, na primer:

```bash
enp191s0
```

### 2. Preverjanje hitrosti omrežne povezave

Preverite, ali je povezava aktivna in deluje s polno hitrostjo, tako da preverite hitrost svojega vmesnika:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opomba**: Nadomestite `<IFNAME>` z imenom izhodnega vmesnika iz razdelka [1. Določitev omrežnih vmesnikov](#1-determine-network-interfaces)

Videti bi morali hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali povezava ne vzpostavi, preverite povezavo kabla in potrdite, da so vrata stikala nastavljena na 10Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje in ročno nastavite hitrost povezave; za podrobnosti glejte dokumentacijo svojega stikala.

<!-- @os:end -->

<!-- @os:windows -->
### Preverjanje hitrosti omrežne povezave

Na vsaki napravi preverite hitrost povezave svojih omrežnih vmesnikov:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš Ethernet vmesnik bi moral biti `Up` in delovati s hitrostjo `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Opomba**: Če je hitrost nižja od `10 Gbps` ali povezava ne vzpostavi, preverite povezavo kabla in potrdite, da so vrata stikala nastavljena na 10Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje in ročno nastavite hitrost povezave; za podrobnosti glejte dokumentacijo svojega stikala.

<!-- @os:end -->

## Nameščanje llama.cpp

> **Opomba**: Ta korak izvedite na obeh napravah, Machine 1 in Machine 2.

Na voljo sta dve možnosti namestitve:

- [Možnost 1: Lemonade SDK (priporočeno)](#option-1-lemonade-sdk-recommended) – vnaprej izdelane binarne datoteke, najhitrejša namestitev
- [Možnost 2: ročna izgradnja iz izvorne kode](#option-2-manual-source-build) – izgradnja iz izvorne kode s popolnim nadzorom nad zastavicami gradnje
### Možnost 1: Lemonade SDK (priporočeno)

Lemonade SDK ponuja nočne (nightly) izgradnje orodja llama.cpp s pospeševanjem AMD ROCm 7, namenjene GPU-jem, kot je gfx1151 (Strix Halo / Ryzen AI Max+ 395), in drugim novejšim arhitekturam Radeon.

<!-- @os:windows -->
#### 1. korak: Prenos vnaprej izdelanih binarnih datotek

Pojdite na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljnemu GPU-ju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka izdaje).

#### 2. korak: Razširitev binarnih datotek

Razširite preneseni arhiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ta mapa zdaj vsebuje izgradnje `llama-cli.exe`, `llama-server.exe` in `rpc-server.exe` s podporo za ROCm, prevedene posebej za vaš sistem Ryzen AI Halo.

#### 3. korak: Preverjanje zaznave GPU-ja

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
#### 1. korak: Prenos vnaprej izdelanih binarnih datotek

Pojdite na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljnemu GPU-ju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka izdaje).

#### 2. korak: Razširitev in priprava binarnih datotek

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ta mapa zdaj vsebuje izgradnje `llama-cli`, `llama-server` in `rpc-server` s podporo za ROCm, prevedene posebej za vaš sistem Ryzen AI Halo.

#### 3. korak: Preverjanje zaznave GPU-ja

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
Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s poglavjem [Prenos modela](#downloading-the-model).

### Možnost 2: Ročna izgradnja iz izvorne kode

<!-- @os:windows -->
#### 1. korak: Izgradnja llama.cpp

Odprite **ukazni poziv x64 Native Tools** (nameščen z Visual Studio Build Tools) in klonirajte repozitorij:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Dodajte HIP v svojo pot in izvedite izgradnjo s podporo za ROCm in RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Zastavica izgradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programski sklad ROCm/HIP |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DGPU_TARGETS=gfx1151` | Cilja na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Uporablja sistem izgradnje Ninja |

#### 2. korak: Preverjanje zaznave GPU-ja

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

#### 3. korak: Trajno dodajanje HIP v uporabniško pot

Zgornji korak izgradnje je nastavil `%HIP_PATH%\bin` samo za trenutno sejo. Da bodo knjižnice HIP na voljo v katerem koli terminalu (ne le v ukaznem pozivu x64 Native Tools), jo trajno dodajte v svojo uporabniško spremenljivko `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s poglavjem [Prenos modela](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### 1. korak: Izgradnja llama.cpp

Klonirajte repozitorij:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Izvedite izgradnjo s podporo za ROCm in RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Zastavica izgradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programski sklad ROCm |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DAMDGPU_TARGETS="gfx1151"` | Cilja na GPU Ryzen AI Halo (Radeon 8060s) |

Za več možnosti izgradnje si oglejte [dokumentacijo o izgradnji llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### 2. korak: Preverjanje zaznave GPU-ja

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

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s poglavjem [Prenos modela](#downloading-the-model).
<!-- @os:end -->

## Prenos modela

Ta vodnik uporablja [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model s 358 milijardami parametrov v kvantizaciji `Q4_K_XL` podjetja [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri tej kvantizaciji model zahteva približno 205 GB prostora za shranjevanje in se prilega skupnemu pomnilniku GPU-jev dveh vozlišč Ryzen AI Halo.

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

> **Opomba**: Prenos modela je treba opraviti na stroju 1 (krmilniku). Delovna vozlišča RPC ne potrebujejo lokalne kopije datotek modela.

## Zagon modela v gruči

Mehanizem RPC (Remote Procedure Call) v llama.cpp omogoča, da en sam primerek llama.cpp razbremeni plasti modela na oddaljene delavce prek omrežja. En stroj deluje kot **krmilnik** (stroj 1) ter skrbi za tokenizacijo, razvrščanje in orkestracijo. Drugi stroj poganja lahek **strežnik RPC** (stroj 2), ki krmilniku izpostavi svoj pomnilnik GPU in računsko zmogljivost.

Ob nalaganju llama.cpp razdeli model med obema vozliščema. Ko je model naložen, sklepanje poteka tako, kot da bi teklo na enem samem pospeševalniku. RPC v ozadju poskrbi za prenos tenzorjev in sinhronizacijo.

### 1. korak: Zagon strežnika RPC (stroj 2)

Na stroju 2 zaženite strežnik RPC, da krmilniku izpostavite njegove vire GPU:
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
| `--host` | Naslov IP, na katerega se veže strežnik RPC (`0.0.0.0` za vse vmesnike) |

Za več možnosti si oglejte [dokumentacijo RPC za llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### 2. korak: Zagon modela (stroj 1)

Ko strežnik RPC teče na stroju 2, zaženite sklepanje s stroja 1 z uporabo `llama-cli` ali `llama-server`.
#### llama-cli

`llama-cli` zagotavlja terminalski vmesnik za neposredno interakcijo z modelom. Idealen je za primerjalne teste, odpravljanje napak in nizkonivojsko eksperimentiranje.

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

> **Iskanje `<RPC_WORKER_IP>`**: Na napravi 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni IP-naslov.
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

> **Iskanje `<RPC_WORKER_IP>`**: Na napravi 2 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njen lokalni IP-naslov.

<!-- @os:end -->

Ko se zažene, `llama-cli` prikaže napredek nalaganja modela in odpre interaktivni poziv, kjer lahko neposredno klepetate z modelom:

![llama-cli zaganja GLM 4.7 na dveh vozliščih](assets/llama-cli-example.png)

#### llama-server

`llama-server` izpostavi isti mehanizem za sklepanje prek trajnega strežniškega procesa z vgrajenim spletnim vmesnikom in HTTP API-jem, združljivim z OpenAI. To je priporočen vmesnik za dolgotrajnejše uvedbe, dostop več uporabnikov hkrati in povezovanje z zunanjimi orodji.

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

> **Iskanje `<RPC_WORKER_IP>`**: Na napravi 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni IP-naslov.
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

> **Iskanje `<RPC_WORKER_IP>`**: Na napravi 2 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njen lokalni IP-naslov.
<!-- @os:end -->

Ko se zažene, odprite `http://<HOST_IP>:8081` v brskalniku za dostop do vgrajenega spletnega vmesnika. Ta ponuja klepetalni vmesnik v brskalniku za interakcijo z modelom:

![llama-server spletni vmesnik zaganja GLM 4.7 na dveh vozliščih](assets/llama-server-example.png)

<!-- @os:linux -->
> **Iskanje `<HOST_IP>`**: Na napravi 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni IP-naslov.
<!-- @os:end -->

<!-- @os:windows -->
> **Iskanje `<HOST_IP>`**: Na napravi 1 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njen lokalni IP-naslov.
<!-- @os:end -->

#### Priročnik parametrov

| Zastavica | Namen |
|------|---------|
| `-m` | Pot do datoteke modela GGUF (uporabite prvi delček, `00001-of-00005`) |
| `-c` | Velikost konteksta v žetonih. Večje vrednosti porabijo več pomnilnika |
| `-fa on` | Omogoči rocWMMA Flash Attention za izboljšano zmogljivost na GPU-jih AMD |
| `-ngl 999` | Prenese vse plasti modela na GPU |
| `-lm none` | Nastavi način nalaganja modela na `none`, kar onemogoči preslikavo v pomnilnik (memory-mapping) in skrajša čase nalaganja, kadar velikost modela presega sistemski RAM, vendar se prilega v VRAM |
| `--host` | IP-naslov, na katerega naj se veže `llama-server` (samo za `llama-server`) |
| `--port` | Vrata, na katerih se streže HTTP API (samo za `llama-server`) |
| `--rpc` | Z vejico ločen seznam končnih točk RPC delavcev (`IP:port`) |

Za celoten pregled uporabe parametrov glejte [dokumentacijo za llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) in [dokumentacijo za llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Naslednji koraki

- **Povežite aplikacije tretjih oseb**: `llama-server` izpostavlja API, združljiv z OpenAI. Usmerite katero koli aplikacijo, združljivo z OpenAI (na primer Open WebUI), na `http://<HOST_IP>:8081` z nadomestnim API-ključem (npr. `none`), da se povežete s svojim grozdom
- **Raziščite druge modele**: Prebrskajte kvantizirane GGUF-je na [Hugging Face](https://huggingface.co/models?search=gguf) in poiščite modele, ki se prilegajo skupnemu pomnilniku GPU-jev vašega grozda
- **Razširite na štiri vozlišča**: Dodajte še dva sistema Ryzen AI Halo kot dodatna RPC delavca za dostop do modelov v obsegu 1 bilijona parametrov. Dodatne končne točke posredujte `--rpc` kot z vejico ločen seznam (npr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)