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

# Gručenje štirih sistemov Ryzen™ AI Halo z RPC

## Pregled

Vaš sistem Ryzen™ AI Halo je že sposoben lokalno poganjati velike jezikovne modele. Gručenje gre še korak dlje, saj združi pomnilnik GPU več sistemov preko lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z močnejšim sklepanjem, boljšim generiranjem kode in globljim večjezičnim razumevanjem – vse to v celoti na vaši lastni strojni opremi.

Ta vodnik vas nauči, kako gručiti štiri sisteme Ryzen AI Halo z uporabo RPC pogona iz llama.cpp ter kako na vseh štirih napravah s pospeševanjem AMD ROCm™ poganjati Kimi K2.6, velik model tipa mešanica strokovnjakov (mixture-of-experts).

## Kaj se boste naučili

- Kako razširiti dodelitev pomnilnika VRAM na sistemih Ryzen AI Halo
- Namestitev llama.cpp s podporo za ROCm in RPC
- Konfiguracija delovnih vozlišč RPC in zagon porazdeljenega sklepanja na štirih vozliščih
- Zagon modela z 1 bilijonom parametrov na štirih omreženih sistemih Ryzen AI Halo

## Nastavitev konfiguracije pomnilnika

> **Opomba**: Ta korak izvedite na vseh štirih napravah (naprava 1 do naprave 4).

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Poganjanje modelov v bližini ali nad 128 GB:** Na sistemih AMD Ryzen™ AI Max 400 Series (Gorgon Halo) z operacijskim sistemom Windows modeli, ki se približujejo ali presegajo 128 GB pomnilnika, zahtevajo dodatno konfiguracijo za delovanje brez napak. Pred nalaganjem modela sledite navodilom v dokumentu [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines).
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Na operacijskem sistemu Windows je za zagon večjih modelov, ki zahtevajo več pomnilnika, potrebno uporabiti dodelitev pomnilnika AMD Variable Graphics Memory (iGPU VRAM).

To storite tako, da odprete nadzorno ploščo AMD Software: Adrenalin Edition in se pomaknete na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavite vrednost na **96 GB**. Ponovno zaženite sistem, da se spremembe uveljavijo.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V sistemu Linux ROCm uporablja skupni nabor sistemskega pomnilnika, ki je privzeto nastavljen na polovico sistemskega pomnilnika.

To vrednost lahko povečate s spremembo nastavitve strani jedrovega upravitelja prevodnih tabel (Translation Table Manager – TTM), kot je opisano v naslednjih navodilih. AMD priporoča, da v BIOS-u nastavite minimalno namenjeno količino VRAM (0,5 GB).

* Namestite orodje pipx in dodajte pot do z njim nameščenih kolesc (wheels) v sistemsko iskalno pot.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite kolo amd-debug-tools iz PyPI.
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

* Ponovno zaženite sistem, da se spremembe uveljavijo.


<!-- @os:end -->
<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->
## Predpogoji

### Strojna oprema

Ta vodnik zahteva štiri enote Ryzen AI Halo in eno Ethernet stikalo, povezane v zvezdasto topologijo, pri čemer je vsaka enota neposredno povezana s stikalom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Računska vozlišča, ki sestavljajo gručo |
| 10Gbps Ethernet stikalo | 1 | Centralno stikalo, ki omogoča komunikacijo med več vozlišči Ryzen AI Halo (vsaj 4 vrata) |
| Ethernet kabel | 4 | Povezuje vsako enoto Halo s stikalom (priporočen Cat 7 ali višji) |

> **Opomba**: Za povezavo štirih enot Ryzen AI Halo so potrebna štiri vrata Ethernet stikala. Peto vrata so potrebna, če do modela dostopate z ločene odjemalske naprave namesto z ene od enot Halo.

### Programska oprema
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Namestite:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) z delovnim obremenitvijo **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizična namestitev strojne opreme

> **Opomba**: Ta korak izvedite na vseh štirih napravah (naprava 1 do naprave 4).

Povežite vsako enoto Ryzen AI Halo z Ethernet stikalom s kablom Cat 7 (ali višjim). S tem vzpostavite 10Gbps povezavo, ki se uporablja za visokohitrostno komunikacijo med vozlišči.
<!-- @os:linux -->
### 1. Določitev omrežnih vmesnikov

Na vsaki napravi poiščite ime njenega omrežnega vmesnika in si ga zapomnite (v nadaljevanju bo poimenovan `IFNAME`). Zaženite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

To izpiše ime vmesnika neposredno, na primer:

```bash
enp191s0
```

### 2. Preverjanje hitrosti omrežnih povezav

Potrdite, da je povezava aktivna in deluje s polno hitrostjo, tako da preverite hitrost svojega vmesnika:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opomba**: Nadomestite `<IFNAME>` z izhodnim imenom vmesnika iz [1. Določitev omrežnih vmesnikov](#1-determine-network-interfaces)

Videti bi morali hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali se povezava ne vzpostavi, preverite povezavo kabla in se prepričajte, da so vrata stikala nastavljena na 10Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje in hitrost povezave nastavite ročno; za podrobnosti glejte dokumentacijo svojega stikala.

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

> **Opomba**: Če je hitrost nižja od `10 Gbps` ali se povezava ne vzpostavi, preverite povezavo kabla in se prepričajte, da so vrata stikala nastavljena na 10Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje in hitrost povezave nastavite ročno; za podrobnosti glejte dokumentacijo svojega stikala.

<!-- @os:end -->

## Namestitev llama.cpp

> **Opomba**: Ta korak izvedite na vseh štirih napravah (naprava 1 do naprave 4).

Na voljo sta dve možnosti namestitve:

- [Možnost 1: Lemonade SDK (priporočeno)](#option-1-lemonade-sdk-recommended) - vnaprej izdelane binarne datoteke, najhitrejša namestitev
- [Možnost 2: Ročna izdelava iz izvorne kode](#option-2-manual-source-build) - izdelava iz izvorne kode s polnim nadzorom nad zastavicami izdelave
### Možnost 1: Lemonade SDK (priporočeno)

Lemonade SDK ponuja nočne (nightly) izgradnje llama.cpp s pospeševanjem AMD ROCm 7, namenjene GPE-jem, kot je gfx1151 (Strix Halo / Ryzen AI Max+ 395), in drugim novejšim arhitekturam Radeon.

<!-- @os:windows -->
#### Korak 1: Prenos vnaprej izgrajenih binarnih datotek

Pojdite na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljnemu GPE-ju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka izgradnje).

#### Korak 2: Razširitev binarnih datotek

Razširite preneseni arhiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ta mapa zdaj vsebuje izgradnje `llama-cli.exe`, `llama-server.exe` in `ggml-rpc-server.exe` s podporo ROCm, prevedene posebej za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverjanje zaznavanja GPE-ja

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
#### Korak 1: Prenos vnaprej izgrajenih binarnih datotek

Pojdite na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljnemu GPE-ju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka izgradnje).

#### Korak 2: Razširitev in priprava binarnih datotek

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ta mapa zdaj vsebuje izgradnje `llama-cli`, `llama-server` in `rpc-server` s podporo ROCm, prevedene posebej za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverjanje zaznavanja GPE-ja

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
Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s [Prenašanje modela](#downloading-the-model).

### Možnost 2: Ročna izgradnja iz izvorne kode

<!-- @os:windows -->
#### Korak 1: Izgradnja llama.cpp

Odprite **x64 Native Tools Command Prompt** (nameščen z Visual Studio Build Tools) in klonirajte repozitorij:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Dodajte HIP na svojo pot in izgradite s podporo za ROCm in RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Zastavica izgradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programsko zbirko ROCm/HIP |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DGPU_TARGETS=gfx1151` | Cilja GPE Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Uporablja izgradbeni sistem Ninja |

#### Korak 2: Preverjanje zaznavanja GPE-ja

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

#### Korak 3: Dodajanje HIP na uporabniško pot

Zgornji korak izgradnje je nastavil `%HIP_PATH%\bin` samo za trenutno sejo. Da bodo knjižnice HIP na voljo v katerem koli terminalu (ne le v x64 Native Tools Command Prompt), jih trajno dodajte v uporabniško spremenljivko `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s [Prenašanje modela](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Izgradnja llama.cpp

Klonirajte repozitorij:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Izgradite s podporo za ROCm in RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Zastavica izgradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programsko zbirko ROCm |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DAMDGPU_TARGETS="gfx1151"` | Cilja GPE Ryzen AI Halo (Radeon 8060s) |

Za več možnosti izgradnje glejte [dokumentacijo o izgradnji llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Korak 2: Preverjanje zaznavanja GPE-ja

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

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s [Prenašanje modela](#downloading-the-model).
<!-- @os:end -->

## Prenašanje modela

Ta vodnik uporablja [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) v kvantizaciji `UD-Q2_K_XL` od [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Ta kvantizacija se prilega skupnemu pomnilniku GPE-jev štirih vozlišč Ryzen AI Halo.

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

> **Opomba**: Prenos modela mora biti opravljen na Napravi 1 (krmilniku). Delovna vozlišča RPC (Naprave 2, 3 in 4) ne potrebujejo lokalne kopije datotek modela.

## Zagon modela v gruči

Mehanizem RPC (Remote Procedure Call) v llama.cpp omogoča, da en primerek llama.cpp razbremeni plasti modela na oddaljene delovne naprave prek omrežja. Ena naprava deluje kot **krmilnik** (Naprava 1) in skrbi za tokenizacijo, razporejanje in orkestracijo. Preostale tri naprave vsaka poganja lahek **strežnik RPC** (Naprave 2, 3 in 4), ki krmilniku izpostavi svoj pomnilnik GPE-ja in zmogljivost za izračune.

Ob nalaganju llama.cpp razdeli model na vsa štiri vozlišča. Po nalaganju sklepanje poteka, kot da bi teklo na enem samem pospeševalniku. RPC v ozadju poskrbi za prenose tenzorjev in sinhronizacijo.

### Korak 1: Zagon strežnikov RPC (Naprave 2, 3 in 4)

Na vsaki od Naprav 2, 3 in 4 zaženite strežnik RPC, da krmilniku izpostavite njene vire GPE-ja:
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
| `-p` | Vrata za oddajanje strežnika RPC |
| `-c` | Omogoči lokalni predpomnilnik za velike tenzorje, s čimer se izogne ponavljajočim se omrežnim prenosom med nalaganjem modela |
| `--host` | IP-naslov, na katerega se veže strežnik RPC (`0.0.0.0` za vse vmesnike) |

Za več možnosti glejte [dokumentacijo o RPC v llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Zagon modela (Naprava 1)

Ko strežniki RPC tečejo na Napravah 2, 3 in 4, zaženite sklepanje z Naprave 1 z uporabo `llama-cli` ali `llama-server`.
#### llama-cli

`llama-cli` zagotavlja vmesnik na osnovi terminala za neposredno interakcijo z modelom. Idealen je za primerjalno testiranje, odpravljanje napak in nizkonivojsko eksperimentiranje.

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

> **Iskanje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na vsakem izmed strojev 2, 3 in 4 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni naslov IP.
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

> **Iskanje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na vsakem izmed strojev 2, 3 in 4 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njegov lokalni naslov IP.

<!-- @os:end -->

Ko je zagnan, `llama-cli` prikaže napredek nalaganja modela in vstopi v interaktivni poziv, kjer lahko klepetate neposredno z modelom:

![llama-cli, ki izvaja Kimi K2.6 na štirih vozliščih](assets/llama-cli-example.png)

#### llama-server

`llama-server` izpostavi isti mehanizem za sklepanje prek trajnega strežniškega procesa z vgrajenim spletnim uporabniškim vmesnikom in HTTP API-jem, združljivim s OpenAI. To je priporočen vmesnik za dolgotrajnejše uvedbe, dostop več uporabnikov in integracijo z zunanjimi orodji.

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

> **Iskanje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na vsakem izmed strojev 2, 3 in 4 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni naslov IP.
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

> **Iskanje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na vsakem izmed strojev 2, 3 in 4 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njegov lokalni naslov IP.
<!-- @os:end -->

Ko je zagnan, v brskalniku odprite `http://<HOST_IP>:8081`, da dostopate do vgrajenega spletnega uporabniškega vmesnika. Ta zagotavlja klepetalni vmesnik v brskalniku za interakcijo z modelom:

![spletni uporabniški vmesnik llama-server, ki izvaja Kimi K2.6 na štirih vozliščih](assets/llama-server-example.png)

<!-- @os:linux -->
> **Iskanje `<HOST_IP>`**: Na stroju 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni naslov IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Iskanje `<HOST_IP>`**: Na stroju 1 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njegov lokalni naslov IP.
<!-- @os:end -->

#### Referenca parametrov

| Zastavica | Namen |
|------|---------|
| `-m` | Pot do datoteke modela GGUF (uporabite prvi del, `00001-of-00008`) |
| `-c` | Velikost konteksta v žetonih (tokenih). Večje vrednosti porabijo več pomnilnika |
| `-fa on` | Omogoči rocWMMA Flash Attention za izboljšano zmogljivost na GPU-jih AMD |
| `-ngl 999` | Prenese vse plasti modela na GPU |
| `-lm none` | Nastavi način nalaganja modela na `none`, kar onemogoči preslikavo pomnilnika (memory-mapping) in skrajša čase nalaganja, kadar velikost modela presega sistemski RAM, a se prilega v VRAM |
| `-b` | Logična velikost paketa v žetonih (tokenih). Nastavitev na 4096 uravnoteži prepustnost in porabo pomnilnika med vozlišči |
| `-ub` | Fizična (mikro) velikost paketa za obdelavo poziva. Ujemanje z `-b` se izogne nepotrebnim stroškom razkosavanja |
| `--host` | Naslov IP, na katerega naj se `llama-server` priklopi (samo `llama-server`) |
| `--port` | Vrata, na katerih se streže HTTP API (samo `llama-server`) |
| `--rpc` | Z vejico ločen seznam končnih točk delavcev RPC (`IP:port`) |

Za celoten opis uporabe parametrov glejte [dokumentacijo za llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) in [dokumentacijo za llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Naslednji koraki

- **Povežite aplikacije tretjih oseb**: `llama-server` izpostavi API, združljiv s OpenAI. Katero koli aplikacijo, združljivo s OpenAI (na primer Open WebUI), usmerite na `http://<HOST_IP>:8081` s poljubnim nadomestnim ključem API (npr. `none`), da se povežete s svojim grozdom
- **Raziščite druge modele**: Prebrskajte kvantizirane modele GGUF na [Hugging Face](https://huggingface.co/models?search=gguf), da poiščete modele, ki se prilegajo v skupni pomnilnik GPU vašega grozda
- **Razširite se čez štiri vozlišča**: Dodajte nadaljnje sisteme Ryzen AI Halo kot dodatne delavce RPC, da dostopate do modelov, ki presegajo obseg 1 bilijona parametrov. Dodatne končne točke posredujte `--rpc` kot z vejico ločen seznam (npr. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)