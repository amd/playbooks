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

Vaš sistem Ryzen™ AI Halo je že sposoben lokalno zaganjati velike jezikovne modele. Gručenje to zmožnost razširi še dlje, saj združi GPU-pomnilnik več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z močnejšim sklepanjem, boljšim generiranjem kode in globljim večjezičnim razumevanjem – vse to popolnoma na vaši lastni strojni opremi.

Ta priročnik vas nauči, kako gručiti štiri sisteme Ryzen AI Halo z uporabo motorja RPC iz llama.cpp in kako na vseh štirih strojih z pospeševanjem AMD ROCm™ zagnati Kimi K2.6, velik model tipa mešanica strokovnjakov (mixture-of-experts).

## Kaj se boste naučili

- Kako razširiti dodelitev VRAM na sistemih Ryzen AI Halo
- Namestitev llama.cpp s podporo za ROCm in RPC
- Konfiguracija delavcev RPC in zagon porazdeljenega sklepanja na štirih vozliščih
- Zagon modela z 1T parametri na štirih omrežno povezanih sistemih Ryzen AI Halo

## Nastavitev konfiguracije pomnilnika

> **Opomba**: Ta korak izvedite na vseh štirih strojih (od stroja 1 do stroja 4).

<!-- @os:windows -->
V sistemu Windows za zagon večjih modelov, ki zahtevajo več pomnilnika, moramo uporabiti dodelitev AMD Variable Graphics Memory (iGPU VRAM).

To storite tako, da odprete nadzorno ploščo AMD Software: Adrenalin Edition in se pomaknete na: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavite vrednost na **96 GB**. Za uveljavitev sprememb znova zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V sistemu Linux ROCm uporablja skupni sistemski pomnilniški nabor, ki je privzeto nastavljen na polovico sistemskega pomnilnika.

To količino lahko povečate s spremembo nastavitve strani upravitelja preslikovalne tabele (Translation Table Manager – TTM) v jedru, po naslednjih navodilih. AMD priporoča, da v BIOS-u nastavite najmanjši namenski VRAM (0,5 GB).

* Namestite pripomoček pipx in dodajte pot za kolesa (wheels), nameščena s pipx, v sistemsko iskalno pot.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite kolo amd-debug-tools iz PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Zaženite orodje amd-ttm, da poizvedujete o trenutnih nastavitvah skupnega pomnilnika.
  ```bash
  amd-ttm
  ```

* Ponovno konfigurirajte nastavitve skupnega pomnilnika na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Znova zaženite sistem, da se spremembe uveljavijo.


<!-- @os:end -->
<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->
## Predpogoji

### Strojna oprema

Ta priročnik zahteva štiri enote Ryzen AI Halo in eno Ethernet stikalo, povezane v zvezdasto topologijo, pri čemer je vsaka enota povezana neposredno s stikalom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Računska vozlišča, ki tvorijo gručo |
| 10-gigabitno Ethernet stikalo | 1 | Osrednje stikalo za omogočanje komunikacije med večimi vozlišči Ryzen AI Halo (vsaj 4 vrata) |
| Ethernet kabel | 4 | Povezuje vsako enoto Halo s stikalom (priporočena kategorija Cat 7 ali višja) |

> **Opomba**: Za povezavo štirih enot Ryzen AI Halo so potrebna štiri vrata na Ethernet stikalu. Peta vrata so potrebna, če do modela dostopate z ločenega odjemalskega stroja namesto iz ene od enot Halo.

### Programska oprema
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Namestite:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) z delovnim naborom **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizična namestitev strojne opreme

> **Opomba**: Ta korak izvedite na vseh štirih strojih (od stroja 1 do stroja 4).

Povežite vsako enoto Ryzen AI Halo s stikalom Ethernet z uporabo kabla kategorije Cat 7 (ali višje). To vzpostavi 10-gigabitno povezavo, ki se uporablja za visokohitrostno komunikacijo med vozlišči.
<!-- @os:linux -->
### 1. Ugotavljanje omrežnih vmesnikov

Na vsakem stroju poiščite ime njegovega omrežnega vmesnika in si ga zapišite (v nadaljevanju bo poimenovan `IFNAME`). Zaženite:

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

> **Opomba**: Zamenjajte `<IFNAME>` z imenom izhodnega vmesnika iz poglavja [1. Ugotavljanje omrežnih vmesnikov](#1-determine-network-interfaces)

Videti bi morali hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali se povezava ne vzpostavi, preverite kabelsko povezavo in potrdite, da je vrata stikala nastavljena na 10 Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje (auto-negotiation) in hitrost povezave nastavite ročno; oglejte si dokumentacijo svojega stikala.

<!-- @os:end -->

<!-- @os:windows -->
### Preverjanje hitrosti omrežne povezave

Na vsakem stroju preverite hitrost povezave svojih omrežnih vmesnikov:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš Ethernet vmesnik bi moral biti `Up` in delovati pri `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Opomba**: Če je hitrost nižja od `10 Gbps` ali se povezava ne vzpostavi, preverite kabelsko povezavo in potrdite, da je vrata stikala nastavljena na 10 Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje (auto-negotiation) in hitrost povezave nastavite ročno; oglejte si dokumentacijo svojega stikala.

<!-- @os:end -->

## Nameščanje llama.cpp

> **Opomba**: Ta korak izvedite na vseh štirih strojih (od stroja 1 do stroja 4).

Na voljo sta dve možnosti namestitve:

- [Možnost 1: Lemonade SDK (priporočeno)](#option-1-lemonade-sdk-recommended) – vnaprej pripravljene binarne datoteke, najhitrejša namestitev
- [Možnost 2: Ročna izgradnja iz izvorne kode](#option-2-manual-source-build) – izgradnja iz izvorne kode s popolnim nadzorom nad zastavicami gradnje

### Možnost 1: Lemonade SDK (priporočeno)

Lemonade SDK ponuja nočne (nightly) izgradnje llama.cpp s pospeševanjem AMD ROCm 7, namenjene GPU-jem, kot je gfx1151 (Strix Halo / Ryzen AI Max+ 395), ter drugim novejšim arhitekturam Radeon.

<!-- @os:windows -->
#### Korak 1: Prenos vnaprej izdelanih binarnih datotek

Pomaknite se na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljnemu GPU-ju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka gradnje).

#### Korak 2: Razpakiranje binarnih datotek

Razpakirajte preneseni arhiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ta imenik zdaj vsebuje z ROCm omogočene gradnje `llama-cli.exe`, `llama-server.exe` in `ggml-rpc-server.exe`, prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverjanje zaznavanja GPU-ja

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
#### Korak 1: Prenos vnaprej izdelanih binarnih datotek

Pomaknite se na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljnemu GPU-ju:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka gradnje).

#### Korak 2: Razpakiranje in priprava binarnih datotek

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ta imenik zdaj vsebuje z ROCm omogočene gradnje `llama-cli`, `llama-server` in `rpc-server`, prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverjanje zaznavanja GPU-ja

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
Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte na [Prenos modela](#downloading-the-model).

### Možnost 2: Ročna gradnja iz izvorne kode

<!-- @os:windows -->
#### Korak 1: Gradnja llama.cpp

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
| `-DGPU_TARGETS=gfx1151` | Cilja GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Uporablja gradbeni sistem Ninja |

#### Korak 2: Preverjanje zaznavanja GPU-ja

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

#### Korak 3: Dodajanje HIP-a v uporabniško pot

Zgornji korak gradnje je nastavil `%HIP_PATH%\bin` samo za trenutno sejo. Da bodo knjižnice HIP na voljo v katerem koli terminalu (ne samo v x64 Native Tools Command Prompt), jih trajno dodajte v svojo uporabniško spremenljivko `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte na [Prenos modela](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Gradnja llama.cpp

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
| `-DAMDGPU_TARGETS="gfx1151"` | Cilja GPU Ryzen AI Halo (Radeon 8060s) |

Za več možnosti gradnje glejte [dokumentacijo za gradnjo llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Korak 2: Preverjanje zaznavanja GPU-ja

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

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte na [Prenos modela](#downloading-the-model).
<!-- @os:end -->

## Prenos modela

Ta priročnik uporablja [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) v kvantizaciji `UD-Q2_K_XL` podjetja [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Ta kvantizacija se prilega skupnemu pomnilniku GPU-ja štirih vozlišč Ryzen AI Halo.

Prenesite datoteke GGUF z uporabo Hugging Face CLI:
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

> **Opomba**: Prenos modela mora biti dokončan na Napravi 1 (kontrolerju). Delovna vozlišča RPC (naprave 2, 3 in 4) ne potrebujejo lokalne kopije datotek modela.

## Zagon modela v gruči

Modul RPC (Remote Procedure Call) llama.cpp omogoča, da ena instanca llama.cpp razbremeni plasti modela na oddaljene delovne enote prek omrežja. Ena naprava deluje kot **kontroler** (Naprava 1), ki skrbi za tokenizacijo, razporejanje in orkestracijo. Preostale tri naprave vsaka poganjajo lahek **strežnik RPC** (naprave 2, 3 in 4), ki kontrolerju izpostavijo svoj pomnilnik GPU-ja in računsko zmogljivost.

Ob nalaganju llama.cpp razdeli model med vsa štiri vozlišča. Ko je model naložen, sklepanje poteka, kot da bi teklo na enem samem pospeševalniku. RPC v ozadju poskrbi za prenos tenzorjev in sinhronizacijo.

### Korak 1: Zagon strežnikov RPC (naprave 2, 3 in 4)

Na vsaki od naprav 2, 3 in 4 zaženite strežnik RPC, da izpostavite njene vire GPU-ja kontrolerju:
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
| `-c` | Omogoči lokalni predpomnilnik za velike tenzorje, kar prepreči ponavljajoče se omrežne prenose med nalaganjem modela |
| `--host` | IP-naslov, na katerega se veže strežnik RPC (`0.0.0.0` za vse vmesnike) |

Za več možnosti glejte [dokumentacijo RPC za llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Zagon modela (Naprava 1)

Ko strežniki RPC tečejo na napravah 2, 3 in 4, zaženite sklepanje na Napravi 1 z uporabo `llama-cli` ali `llama-server`.
#### llama-cli

`llama-cli` ponuja terminalski vmesnik za neposredno interakcijo z modelom. Idealen je za primerjalno ocenjevanje (benchmarking), odpravljanje napak in nizkonivojsko eksperimentiranje.

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

> **Iskanje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na vsakem od strojev 2, 3 in 4 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni IP naslov.
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba**: To ukaz zaženite v terminalu (Powershell).

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

> **Iskanje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na vsakem od strojev 2, 3 in 4 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njegov lokalni IP naslov.

<!-- @os:end -->

Ko se zažene, `llama-cli` prikaže napredek nalaganja modela in vstopi v interaktivni poziv, kjer se lahko neposredno pogovarjate z modelom:

![llama-cli, ki poganja Kimi K2.6 na štirih vozliščih](assets/llama-cli-example.png)

#### llama-server

`llama-server` izpostavi isti sklepalni pogon prek trajnega strežniškega procesa z vgrajenim spletnim vmesnikom in HTTP API-jem, združljivim z OpenAI. To je prednostni vmesnik za dolgotrajnejše uvedbe, dostop več uporabnikov in integracijo z zunanjimi orodji.

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

> **Iskanje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na vsakem od strojev 2, 3 in 4 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni IP naslov.
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba**: To ukaz zaženite v terminalu (Powershell).

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

> **Iskanje `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na vsakem od strojev 2, 3 in 4 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njegov lokalni IP naslov.
<!-- @os:end -->

Ko je zagnan, odprite `http://<HOST_IP>:8081` v brskalniku za dostop do vgrajenega spletnega vmesnika. Ta ponuja klepetalni vmesnik v brskalniku za interakcijo z modelom:

![Spletni vmesnik llama-server, ki poganja Kimi K2.6 na štirih vozliščih](assets/llama-server-example.png)

<!-- @os:linux -->
> **Iskanje `<HOST_IP>`**: Na stroju 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni IP naslov.
<!-- @os:end -->

<!-- @os:windows -->
> **Iskanje `<HOST_IP>`**: Na stroju 1 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njegov lokalni IP naslov.
<!-- @os:end -->

#### Referenca parametrov

| Zastavica | Namen |
|------|---------|
| `-m` | Pot do GGUF datoteke modela (uporabite prvi delček, `00001-of-00008`) |
| `-c` | Velikost konteksta v žetonih. Večje vrednosti porabijo več pomnilnika |
| `-fa on` | Omogoči rocWMMA Flash Attention za izboljšano zmogljivost na GPU-jih AMD |
| `-ngl 999` | Prenese vse plasti modela na GPU |
| `-lm none` | Nastavi način nalaganja modela na `none`, kar onemogoči preslikavo v pomnilnik (memory-mapping) in skrajša čas nalaganja, kadar velikost modela presega sistemski RAM, vendar se prilega v VRAM |
| `-b` | Logična velikost paketa v žetonih. Nastavitev na 4096 uravnoteži pretočnost in porabo pomnilnika na vseh vozliščih |
| `-ub` | Fizična (mikro) velikost paketa za obdelavo poziva. Ujemanje z `-b` prepreči nepotreben dodatni obremenitveni strošek razdrobitve |
| `--host` | IP naslov, na katerega se veže `llama-server` (samo `llama-server`) |
| `--port` | Vrata za strežbo HTTP API-ja (samo `llama-server`) |
| `--rpc` | Z vejico ločen seznam končnih točk delavcev RPC (`IP:port`) |

Za popoln pregled uporabe parametrov glejte [dokumentacijo za llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) in [dokumentacijo za llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Naslednji koraki

- **Povežite aplikacije tretjih oseb**: `llama-server` izpostavi API, združljiv z OpenAI. Usmerite katero koli aplikacijo, združljivo z OpenAI (na primer Open WebUI), na `http://<HOST_IP>:8081` s poljubnim nadomestnim API-ključem (npr. `none`), da se povežete s svojim gručo (cluster)
- **Raziščite druge modele**: Prebrskajte kvantizirane GGUF-je na [Hugging Face](https://huggingface.co/models?search=gguf), da poiščete modele, ki se prilegajo skupnemu GPU pomnilniku vaše gruče
- **Razširite čez štiri vozlišča**: Dodajte dodatne sisteme Ryzen AI Halo kot dodatne delavce RPC za dostop do modelov onkraj velikostnega razreda 1 bilijon parametrov. Podajte dodatne končne točke v `--rpc` kot z vejico ločen seznam (npr. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)