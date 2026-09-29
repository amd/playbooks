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

# Gručenje štirih Ryzen™ AI Halo sistemov z RPC

## Pregled

Vaš Ryzen™ AI Halo je že sposoben lokalno poganjati velike jezikovne modele. Gručenje to zmožnost razširi še naprej, saj združi pomnilnik GPE-jev več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z močnejšim sklepanjem, boljšim generiranjem kode in globljim večjezičnim razumevanjem – vse povsem na vaši lastni strojni opremi.

Ta vodnik vas nauči, kako povezati štiri sisteme Ryzen AI Halo v gručo z uporabo RPC pogona knjižnice llama.cpp in kako na vseh štirih napravah hkrati z pospeševanjem AMD ROCm™ poganjati Kimi K2.6, velik model mešanice ekspertov (mixture-of-experts).

## Kaj se boste naučili

- Kako razširiti dodelitev pomnilnika VRAM na sistemih Ryzen AI Halo
- Namestitev llama.cpp s podporo za ROCm in RPC
- Konfiguracija delavcev RPC in zagon porazdeljenega sklepanja na štirih vozliščih
- Zagon modela z 1 bilijonom parametrov na štirih omreženih sistemih Ryzen AI Halo

## Nastavitev konfiguracije pomnilnika

> **Opomba**: Ta korak izvedite na vseh štirih napravah (Naprava 1 do Naprava 4).

<!-- @os:windows -->
V sistemu Windows moramo za zagon večjih modelov, ki zahtevajo večjo količino pomnilnika, uporabiti dodelitev AMD Variable Graphics Memory (pomnilnik VRAM za iGPE).

To storite tako, da odprete nadzorno ploščo AMD Software: Adrenalin Edition in se pomaknete na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavite vrednost na **96 GB**. Za uveljavitev sprememb sistem znova zaženite.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V sistemu Linux ROCm uporablja skupni pomnilniški bazen sistema, ta bazen pa je privzeto konfiguriran na polovico sistemskega pomnilnika.

To količino je mogoče povečati s spremembo nastavitve strani upravljalnika prevodne tabele jedra (Translation Table Manager – TTM), kot je opisano spodaj. AMD priporoča, da v BIOS-u nastavite minimalni namenski pomnilnik VRAM (0,5 GB).

* Namestite pripomoček pipx in dodajte pot za lupinice, nameščene s pipx, v sistemsko iskalno pot.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite lupinico amd-debug-tools iz PyPI.
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

* Za uveljavitev sprememb sistem znova zaženite.


<!-- @os:end -->
<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->
## Predpogoji

### Strojna oprema

Ta vodnik zahteva štiri enote Ryzen AI Halo in eno mrežno stikalo Ethernet, povezane v zvezdasto topologijo, pri čemer je vsaka enota povezana neposredno s stikalom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Izračunska vozlišča, ki tvorijo gručo |
| 10Gbps stikalo Ethernet | 1 | Osrednje stikalo, ki omogoča komunikacijo med več vozlišči Ryzen AI Halo (vsaj 4 vrata) |
| Kabel Ethernet | 4 | Povezuje vsako enoto Halo s stikalom (priporočen Cat 7 ali boljši) |

> **Opomba**: Za povezavo štirih enot Ryzen AI Halo so potrebna štiri vrata na stikalu Ethernet. Peta vrata so potrebna, če do modela dostopate z ločenega odjemalskega računalnika namesto z ene od enot Halo.

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

## Fizična namestitev strojne opreme

> **Opomba**: Ta korak izvedite na vseh štirih napravah (Naprava 1 do Naprava 4).

Vsako enoto Ryzen AI Halo povežite s stikalom Ethernet z uporabo kabla Cat 7 (ali boljšega). S tem vzpostavite 10Gbps povezavo, ki se uporablja za visoko hitrostno komunikacijo med vozlišči.
<!-- @os:linux -->
### 1. Ugotavljanje mrežnih vmesnikov

Na vsaki napravi poiščite ime njenega mrežnega vmesnika in si ga zapišite (v nadaljevanju bo omenjen kot `IFNAME`). Zaženite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

S tem se izpiše ime vmesnika neposredno, na primer:

```bash
enp191s0
```

### 2. Preverjanje hitrosti mrežne povezave

Preverite, da je povezava aktivna in deluje s polno hitrostjo, tako da preverite hitrost svojega vmesnika:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opomba**: Nadomestite `<IFNAME>` z izhodnim imenom vmesnika iz razdelka [1. Ugotavljanje mrežnih vmesnikov](#1-determine-network-interfaces)

Videti bi morali hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali povezava ne vzpostavi, preverite povezavo kabla in potrdite, da so vrata stikala nastavljena na 10Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje in ročno nastavite hitrost povezave; za več informacij glejte dokumentacijo svojega stikala.

<!-- @os:end -->

<!-- @os:windows -->
### Preverjanje hitrosti mrežne povezave

Na vsaki napravi preverite hitrost povezave svojih mrežnih vmesnikov:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš vmesnik Ethernet bi moral biti `Up` (aktiven) in delovati s hitrostjo `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Opomba**: Če je hitrost nižja od `10 Gbps` ali povezava ne vzpostavi, preverite povezavo kabla in potrdite, da so vrata stikala nastavljena na 10Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje in ročno nastavite hitrost povezave; za več informacij glejte dokumentacijo svojega stikala.

<!-- @os:end -->

## Nameščanje llama.cpp

> **Opomba**: Ta korak izvedite na vseh štirih napravah (Naprava 1 do Naprava 4).

Na voljo sta dve možnosti namestitve:

- [Možnost 1: Lemonade SDK (priporočeno)](#option-1-lemonade-sdk-recommended) – vnaprej izdelane binarne datoteke, najhitrejša namestitev
- [Možnost 2: Ročna izgradnja iz izvorne kode](#option-2-manual-source-build) – izgradnja iz izvorne kode s polnim nadzorom nad zastavicami izgradnje

### Možnost 1: Lemonade SDK (priporočeno)

Lemonade SDK ponuja nočne (nightly) izdelke llama.cpp s pospeševanjem AMD ROCm 7, namenjene GPE-jem, kot je gfx1151 (Strix Halo / Ryzen AI Max+ 395), in drugim novejšim arhitekturam Radeon.

<!-- @os:windows -->
#### Korak 1: Prenesite vnaprej pripravljene binarne datoteke

Pojdite na stran z zadnjo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljnemu GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka izdaje).

#### Korak 2: Razpakirajte binarne datoteke

Razpakirajte prenesen arhiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ta imenik zdaj vsebuje z ROCm omogočene izdaje `llama-cli.exe`, `llama-server.exe` in `ggml-rpc-server.exe`, prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverite zaznavo GPU

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

Pojdite na stran z zadnjo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljnemu GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka izdaje).

#### Korak 2: Razpakirajte in pripravite binarne datoteke

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ta imenik zdaj vsebuje z ROCm omogočene izdaje `llama-cli`, `llama-server` in `rpc-server`, prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverite zaznavo GPU

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

### Možnost 2: Ročna gradnja iz izvorne kode

<!-- @os:windows -->
#### Korak 1: Zgradite llama.cpp

Odprite **x64 Native Tools Command Prompt** (nameščen skupaj z orodji Visual Studio Build Tools) in klonirajte repozitorij:

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
| `-DGPU_TARGETS=gfx1151` | Ciljanje na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Uporablja gradbeni sistem Ninja |

#### Korak 2: Preverite zaznavo GPU

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

Zgornji korak gradnje je nastavil `%HIP_PATH%\bin` samo za trenutno sejo. Da bodo knjižnice HIP na voljo v katerem koli terminalu (ne le v x64 Native Tools Command Prompt), jo trajno dodajte v svoj uporabniški `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte na [Prenos modela](#downloading-the-model).
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
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Zastavica gradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programski sklad ROCm |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DAMDGPU_TARGETS="gfx1151"` | Ciljanje na GPU Ryzen AI Halo (Radeon 8060s) |

Za več možnosti gradnje glejte [dokumentacijo za gradnjo llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Korak 2: Preverite zaznavo GPU

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

Ta priročnik uporablja [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) v kvantizaciji `UD-Q2_K_XL` podjetja [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Ta kvantizacija se prilega skupnemu pomnilniku GPU štirih vozlišč Ryzen AI Halo.

Prenesite datoteke GGUF z uporabo vmesnika Hugging Face CLI:
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

> **Opomba**: Prenos modela je treba dokončati na Napravi 1 (kontrolniku). Delovna vozlišča RPC (Naprave 2, 3 in 4) ne potrebujejo lokalne kopije datotek modela.

## Zagon modela v gruči

Mehanizem llama.cpp RPC (Remote Procedure Call) omogoča, da posamezna instanca llama.cpp razporedi sloje modela na oddaljene delavce po omrežju. Ena naprava deluje kot **kontrolnik** (Naprava 1), ki skrbi za tokenizacijo, razporejanje in orkestracijo. Preostale tri naprave vsaka poganjajo lahek **strežnik RPC** (Naprave 2, 3 in 4), ki kontrolniku izpostavijo svoj pomnilnik GPU in računsko zmogljivost.

Ob nalaganju llama.cpp razdeli model na vsa štiri vozlišča. Ko je model naložen, sklepanje poteka, kot da bi teklo na enem samem pospeševalniku. RPC v ozadju skrbi za prenos tenzorjev in sinhronizacijo.

### Korak 1: Zaženite strežnike RPC (Naprave 2, 3 in 4)

Na vsaki od Naprav 2, 3 in 4 zaženite strežnik RPC, da kontrolniku izpostavite svoje vire GPU:
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
| `-c` | Omogoči lokalni predpomnilnik za velike tenzorje in tako prepreči ponavljajoče se omrežne prenose med nalaganjem modela |
| `--host` | Naslov IP, na katerega se veže strežnik RPC (`0.0.0.0` za vse vmesnike) |

Za več možnosti glejte [dokumentacijo za llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Zaženite model (Naprava 1)

Ko strežniki RPC tečejo na Napravah 2, 3 in 4, zaženite sklepanje z Naprave 1 z uporabo bodisi `llama-cli` bodisi `llama-server`.
#### llama-cli

`llama-cli` omogoča vmesnik v terminalu za neposredno interakcijo z modelom. Idealen je za primerjalno testiranje (benchmarking), odpravljanje napak in eksperimentiranje na nizki ravni.

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

> **Iskanje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na vsakem od strojev 2, 3 in 4 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni naslov IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba**: Ta ukaz zaženite v terminalu (Powershell).

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

> **Iskanje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na vsakem od strojev 2, 3 in 4 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njegov lokalni naslov IP.

<!-- @os:end -->

Ko je zagnan, `llama-cli` prikaže napredek nalaganja modela in vstopi v interaktivni poziv, kjer se lahko neposredno pogovarjate z modelom:

![llama-cli, ki izvaja Kimi K2.6 na štirih vozliščih](assets/llama-cli-example.png)

#### llama-server

`llama-server` izpostavi isti inferenčni pogon prek trajnega strežniškega procesa z vgrajenim spletnim uporabniškim vmesnikom in HTTP API-jem, združljivim z OpenAI. To je priporočeni vmesnik za daljše delovanje, dostop več uporabnikov in integracijo z zunanjimi orodji.

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

> **Iskanje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na vsakem od strojev 2, 3 in 4 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni naslov IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba**: Ta ukaz zaženite v terminalu (Powershell).

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

> **Iskanje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na vsakem od strojev 2, 3 in 4 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njegov lokalni naslov IP.
<!-- @os:end -->

Ko se zažene, odprite `http://<HOST_IP>:8081` v brskalniku za dostop do vgrajenega spletnega uporabniškega vmesnika. Ta ponuja klepetalni vmesnik v brskalniku za interakcijo z modelom:

![Spletni uporabniški vmesnik llama-server, ki izvaja Kimi K2.6 na štirih vozliščih](assets/llama-server-example.png)

<!-- @os:linux -->
> **Iskanje `<HOST_IP>`**: Na stroju 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni naslov IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Iskanje `<HOST_IP>`**: Na stroju 1 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njegov lokalni naslov IP.
<!-- @os:end -->

#### Referenca parametrov

| Zastavica | Namen |
|------|---------|
| `-m` | Pot do datoteke modela GGUF (uporabite prvi delček, `00001-of-00008`) |
| `-c` | Velikost konteksta v žetonih (tokens). Večje vrednosti porabijo več pomnilnika |
| `-fa on` | Omogoči rocWMMA Flash Attention za izboljšano zmogljivost na grafičnih procesorjih AMD |
| `-ngl 999` | Preloži vse plasti modela na GPU |
| `-lm none` | Nastavi način nalaganja modela na `none`, kar onemogoči preslikavo pomnilnika (memory-mapping) in skrajša čas nalaganja, kadar velikost modela presega sistemski RAM, a se prilega VRAM-u |
| `-b` | Logična velikost paketa (batch size) v žetonih. Nastavitev na 4096 uravnoteži prepustnost in porabo pomnilnika med vozlišči |
| `-ub` | Fizična (mikro) velikost paketa za obdelavo poziva. Ujemanje z `-b` se izogne nepotrebnim stroškom razčlenjevanja |
| `--host` | Naslov IP, na katerega naj se poveže `llama-server` (samo `llama-server`) |
| `--port` | Vrata za strežbo HTTP API-ja (samo `llama-server`) |
| `--rpc` | Z vejico ločen seznam končnih točk delavcev RPC (`IP:port`) |

Za poln pregled uporabe parametrov glejte [dokumentacijo za llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) in [dokumentacijo za llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Naslednji koraki

- **Povežite aplikacije tretjih oseb**: `llama-server` izpostavi API, združljiv z OpenAI. Katero koli aplikacijo, združljivo z OpenAI (kot je Open WebUI), usmerite na `http://<HOST_IP>:8081` s poljubnim nadomestnim ključem API (npr. `none`), da jo povežete s svojo gručo
- **Raziščite druge modele**: Prebrskajte kvantizirane datoteke GGUF na [Hugging Face](https://huggingface.co/models?search=gguf), da poiščete modele, ki se prilegajo skupnemu pomnilniku GPU vaše gruče
- **Razširite čez štiri vozlišča**: Dodajte dodatne sisteme Ryzen AI Halo kot dodatne delavce RPC za dostop do modelov, ki presegajo obseg 1 bilijona parametrov. Dodatne končne točke posredujte `--rpc` kot z vejico ločen seznam (npr. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)