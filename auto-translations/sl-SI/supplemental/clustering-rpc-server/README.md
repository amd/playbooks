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

# Gručenje dveh sistemov Ryzen™ AI Halo z RPC

## Pregled

Vaš sistem Ryzen™ AI Halo je že sposoben lokalno zaganjati velike jezikovne modele. Gručenje to zmožnost razširi še dlje, saj združi pomnilnik GPE (GPU) več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z močnejšim sklepanjem, boljšim generiranjem kode in globljim večjezičnim razumevanjem, in sicer povsem na vaši lastni strojni opremi.

Ta vodnik vas nauči, kako gručiti dva sistema Ryzen AI Halo z uporabo RPC pogona llama.cpp in zagnati GLM 4.7, model s 358 milijardami parametrov, na obeh napravah hkrati z pospeševanjem AMD ROCm™.

## Kaj se boste naučili

- Kako razširiti dodelitev pomnilnika VRAM na sistemih Ryzen AI Halo
- Namestitev llama.cpp s podporo za ROCm in RPC
- Konfiguracija RPC delovnega procesa in zagon porazdeljenega sklepanja med dvema vozliščema
- Zagon modela s 358 milijardami parametrov na dveh mrežno povezanih sistemih Ryzen AI Halo

## Nastavitev konfiguracije pomnilnika

> **Opomba**: Ta korak izvedite na Napravi 1 in Napravi 2.

<!-- @os:windows -->
V sistemu Windows moramo za zagon večjih modelov, ki zahtevajo več pomnilnika, uporabiti dodelitev AMD Variable Graphics Memory (iGPU VRAM).

To lahko storite tako, da odprete nadzorno ploščo AMD Software: Adrenalin Edition in se pomaknete do: `Performance > Tuning > AMD Variable Graphics Memory`. Nastavite vrednost na **96 GB**. Za uveljavitev sprememb ponovno zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
V sistemu Linux ROCm uporablja skupni bazen sistemskega pomnilnika, ki je privzeto nastavljen na polovico sistemskega pomnilnika.

To količino lahko povečate s spremembo nastavitve strani Translation Table Manager (TTM) v jedru, po naslednjih navodilih. AMD priporoča, da v BIOS-u nastavite najmanjši namenski VRAM (0,5 GB).

* Namestite orodje pipx in dodajte pot do namestitev pipx v sistemsko iskalno pot.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite paket amd-debug-tools iz PyPI.
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

Za ta vodnik potrebujete dve enoti Ryzen AI Halo in eno omrežno stikalo Ethernet, povezane v zvezdno topologijo, pri čemer je vsaka enota povezana neposredno s stikalom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računalniška vozlišča, ki tvorita gručo |
| Omrežno stikalo Ethernet 10 Gb/s | 1 | Osrednje stikalo, ki omogoča komunikacijo med več vozlišči Ryzen AI Halo (vsaj 2 vrat) |
| Kabel Ethernet | 2 | Povezuje vsako enoto Halo s stikalom (priporočen Cat 7 ali višji) |

> **Opomba**: Za povezavo obeh enot Ryzen AI Halo sta potrebni dve vrata omrežnega stikala. Tretja vrata so potrebna, če do modela dostopate z ločenega odjemalskega računalnika namesto ene od enot Halo.

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

## Fizična nastavitev strojne opreme

> **Opomba**: Ta korak izvedite na Napravi 1 in Napravi 2.

Povežite vsako enoto Ryzen AI Halo z omrežnim stikalom Ethernet s kablom Cat 7 (ali višje). To vzpostavi povezavo s hitrostjo 10 Gb/s, ki se uporablja za hitro komunikacijo med vozlišči.
<!-- @os:linux -->
### 1. Določitev omrežnih vmesnikov

Na vsaki napravi poiščite ime njenega omrežnega vmesnika in si ga zapišite (v nadaljevanju se bo imenoval `IFNAME`). Zaženite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

To neposredno izpiše ime vmesnika, na primer:

```bash
enp191s0
```

### 2. Preverjanje hitrosti omrežne povezave

Potrdite, da je povezava aktivna in deluje s polno hitrostjo, tako da preverite hitrost svojega vmesnika:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opomba**: Zamenjajte `<IFNAME>` z izhodnim imenom vmesnika iz [1. Določitev omrežnih vmesnikov](#1-determine-network-interfaces)

Videti bi morali hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali povezava ne vzpostavi, preverite priključitev kabla in potrdite, da je vrata stikala nastavljena na 10 Gb/s. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje in ročno nastavite hitrost povezave; oglejte si dokumentacijo svojega stikala.

<!-- @os:end -->

<!-- @os:windows -->
### Preverjanje hitrosti omrežne povezave

Na vsaki napravi preverite hitrost povezave svojih omrežnih vmesnikov:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Vaš vmesnik Ethernet bi moral biti `Up` in delovati pri hitrosti `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Opomba**: Če je hitrost nižja od `10 Gbps` ali povezava ne vzpostavi, preverite priključitev kabla in potrdite, da je vrata stikala nastavljena na 10 Gb/s. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje in ročno nastavite hitrost povezave; oglejte si dokumentacijo svojega stikala.

<!-- @os:end -->

## Namestitev llama.cpp

> **Opomba**: Ta korak izvedite na Napravi 1 in Napravi 2.

Na voljo sta dve možnosti namestitve:

- [Možnost 1: Lemonade SDK (priporočeno)](#option-1-lemonade-sdk-recommended) – vnaprej zgrajene binarne datoteke, najhitrejša nastavitev
- [Možnost 2: Ročna gradnja iz izvorne kode](#option-2-manual-source-build) – gradnja iz izvorne kode s popolnim nadzorom nad gradbenimi zastavicami

### Možnost 1: Lemonade SDK (priporočeno)

Lemonade SDK zagotavlja nočne gradnje llama.cpp s pospeševanjem AMD ROCm 7, namenjene GPE-jem, kot je gfx1151 (Strix Halo / Ryzen AI Max+ 395), in drugim novejšim arhitekturam Radeon.

<!-- @os:windows -->
#### Korak 1: Prenos vnaprej pripravljenih binarnih datotek

Pojdite na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljni GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka izdaje).

#### Korak 2: Razpakiranje binarnih datotek

Razpakirajte prenesen arhiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ta imenik zdaj vsebuje gradnje `llama-cli.exe`, `llama-server.exe` in `rpc-server.exe`, omogočene za ROCm, ki so bile predhodno prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverjanje zaznavanja GPU

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
#### Korak 1: Prenos vnaprej pripravljenih binarnih datotek

Pojdite na stran z najnovejšo izdajo in prenesite arhiv, ki ustreza vaši platformi in ciljni GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Prenesite datoteko z imenom `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (kjer je `xxxx` številka izdaje).

#### Korak 2: Razpakiranje in priprava binarnih datotek

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ta imenik zdaj vsebuje gradnje `llama-cli`, `llama-server` in `rpc-server`, omogočene za ROCm, ki so bile predhodno prevedene za vaš sistem Ryzen AI Halo.

#### Korak 3: Preverjanje zaznavanja GPU

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
Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s [prenosom modela](#downloading-the-model).

### Možnost 2: Ročna gradnja iz izvorne kode

<!-- @os:windows -->
#### Korak 1: Gradnja llama.cpp

Odprite **x64 Native Tools Command Prompt** (nameščen skupaj z Visual Studio Build Tools) in klonirajte repozitorij:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Dodajte HIP na svojo pot in zgradite z omogočeno podporo za ROCm in RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Zastavica gradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programsko zbirko ROCm/HIP |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DGPU_TARGETS=gfx1151` | Ciljanje na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Uporablja gradbeni sistem Ninja |

#### Korak 2: Preverjanje zaznavanja GPU

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

#### Korak 3: Trajno dodajanje HIP na uporabniško pot

Zgornji korak gradnje je nastavil `%HIP_PATH%\bin` samo za trenutno sejo. Da bodo knjižnice HIP na voljo v katerem koli terminalu (ne samo v x64 Native Tools Command Prompt), jih trajno dodajte na uporabniško spremenljivko `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s [prenosom modela](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Korak 1: Gradnja llama.cpp

Klonirajte repozitorij:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Zgradite z omogočeno podporo za ROCm in RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Zastavica gradnje | Namen |
|-----------|---------|
| `-DGGML_HIP=ON` | Omogoči programsko zbirko ROCm |
| `-DGGML_RPC=ON` | Omogoči RPC za porazdeljeno sklepanje |
| `-DAMDGPU_TARGETS="gfx1151"` | Ciljanje na GPU Ryzen AI Halo (Radeon 8060s) |

Za več možnosti gradnje glejte [dokumentacijo o gradnji llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Korak 2: Preverjanje zaznavanja GPU

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

Ko je llama.cpp pripravljen na vsakem vozlišču, nadaljujte s [prenosom modela](#downloading-the-model).
<!-- @os:end -->

## Prenos modela

Ta vodnik uporablja [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), model s 358 milijardami parametrov v kvantizaciji `Q4_K_XL` podjetja [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Pri tej kvantizaciji model zahteva približno 205 GB prostora za shranjevanje in se prilega skupnemu pomnilniku GPU dveh vozlišč Ryzen AI Halo.

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

> **Opomba**: Prenos modela je treba opraviti na Napravi 1 (krmilniku). Delovna vozlišča RPC ne potrebujejo lokalne kopije datotek modela.

## Zagon modela v gruči

Motor llama.cpp RPC (Remote Procedure Call) omogoča, da ena instanca llama.cpp odloži plasti modela na oddaljene delovne postaje po omrežju. Ena naprava deluje kot **krmilnik** (Naprava 1), ki skrbi za tokenizacijo, razporejanje in orkestracijo. Druga naprava zažene lahek **RPC strežnik** (Naprava 2), ki krmilniku izpostavi svoj pomnilnik GPU in računsko zmogljivost.

Ob nalaganju llama.cpp razdeli model na obe vozlišči. Ko je model naložen, sklepanje poteka tako, kot da bi teklo na enem samem pospeševalniku. RPC v ozadju poskrbi za prenos tenzorjev in sinhronizacijo.

### Korak 1: Zagon RPC strežnika (Naprava 2)

Na Napravi 2 zaženite RPC strežnik, da krmilniku izpostavite njegove vire GPU:
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
| `-p` | Vrata, na katerih se oddaja RPC strežnik |
| `-c` | Omogoči lokalni predpomnilnik za velike tenzorje, kar preprečuje ponavljajoče se omrežne prenose med nalaganjem modela |
| `--host` | Naslov IP, na katerega se veže RPC strežnik (`0.0.0.0` za vse vmesnike) |

Za več možnosti glejte [dokumentacijo o RPC v llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Korak 2: Zagon modela (Naprava 1)

Ko RPC strežnik teče na Napravi 2, zaženite sklepanje z Naprave 1 z uporabo `llama-cli` ali `llama-server`.

#### llama-cli

`llama-cli` ponuja vmesnik v terminalu za neposredno interakcijo z modelom. Idealen je za primerjalne teste, odpravljanje napak in eksperimentiranje na nizki ravni.

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

> **Iskanje `<RPC_WORKER_IP>`**: Na Napravi 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni naslov IP.
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

> **Iskanje `<RPC_WORKER_IP>`**: Na Napravi 2 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njen lokalni naslov IP.

<!-- @os:end -->

Ko se zažene, `llama-cli` prikaže napredek nalaganja modela in vstopi v interaktivni poziv, kjer se lahko neposredno pogovarjate z modelom:

![llama-cli izvaja GLM 4.7 na dveh vozliščih](assets/llama-cli-example.png)
#### llama-server

`llama-server` izpostavi isti mehanizem za sklepanje prek trajnega strežniškega procesa z integriranim spletnim vmesnikom in HTTP API-jem, združljivim z OpenAI. To je priporočeni vmesnik za daljša postavitve, dostop več uporabnikov in integracijo z zunanjimi orodji.

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

> **Iskanje `<RPC_WORKER_IP>`**: Na napravi 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni IP naslov.
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

> **Iskanje `<RPC_WORKER_IP>`**: Na napravi 2 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njen lokalni IP naslov.
<!-- @os:end -->

Ko je zagnan, odprite `http://<HOST_IP>:8081` v svojem brskalniku, da dostopite do vgrajenega spletnega vmesnika. Ta ponuja klepetalni vmesnik v brskalniku za interakcijo z modelom:

![Spletni vmesnik llama-server, ki poganja GLM 4.7 na dveh vozliščih](assets/llama-server-example.png)

<!-- @os:linux -->
> **Iskanje `<HOST_IP>`**: Na napravi 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni IP naslov.
<!-- @os:end -->

<!-- @os:windows -->
> **Iskanje `<HOST_IP>`**: Na napravi 1 zaženite `ipconfig | findstr /C:"IPv4"` v terminalu (Powershell), da poiščete njen lokalni IP naslov.
<!-- @os:end -->

#### Referenca parametrov

| Zastavica | Namen |
|------|---------|
| `-m` | Pot do datoteke modela GGUF (uporabite prvi del, `00001-of-00005`) |
| `-c` | Velikost konteksta v žetonih. Večje vrednosti porabijo več pomnilnika |
| `-fa on` | Omogoči rocWMMA Flash Attention za izboljšano zmogljivost na AMD GPU-jih |
| `-ngl 999` | Prenese vse plasti modela na GPU |
| `-lm none` | Nastavi način nalaganja modela na `none`, kar onemogoči preslikavo pomnilnika (memory-mapping) za skrajšanje časa nalaganja, ko velikost modela presega sistemski RAM, vendar se še vedno prilega VRAM-u |
| `--host` | IP naslov, na katerega se poveže `llama-server` (samo `llama-server`) |
| `--port` | Vrata, na katerih se streže HTTP API (samo `llama-server`) |
| `--rpc` | Z vejico ločen seznam končnih točk delavcev RPC (`IP:port`) |

Za popolno uporabo parametrov glejte [dokumentacijo llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) in [dokumentacijo llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Naslednji koraki

- **Povežite aplikacije tretjih oseb**: `llama-server` izpostavi API, združljiv z OpenAI. Usmerite katero koli aplikacijo, združljivo z OpenAI (na primer Open WebUI), na `http://<HOST_IP>:8081` z nadomestnim API ključem (npr. `none`), da se povežete s svojim gručo (clusterjem)
- **Raziščite druge modele**: Prebrskajte kvantizirane GGUF-je na [Hugging Face](https://huggingface.co/models?search=gguf), da poiščete modele, ki se prilegajo skupnemu pomnilniku GPU vaše gruče
- **Razširite na štiri vozlišča**: Dodajte še dva sistema Ryzen AI Halo kot dodatna delavca RPC za dostop do modelov v obsegu bilijon parametrov. Podajte dodatne končne točke `--rpc` kot seznam, ločen z vejicami (npr. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)