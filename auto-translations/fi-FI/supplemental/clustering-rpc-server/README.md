<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Kahden Ryzen™ AI Halo -järjestelmän klusterointi RPC:llä

## Yleiskatsaus

Ryzen™ AI Halosi pystyy jo suorittamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän vielä pidemmälle yhdistämällä useiden järjestelmien GPU-muistin paikallisen verkon yli, jolloin saat käyttöösi entistä suurempia malleja, joissa on vahvempi päättelykyky, parempi koodin generointi ja syvempi monikielinen ymmärrys – täysin omalla laitteistollasi.

Tämä ohjekirja opastaa, miten klusteroidaan kaksi Ryzen AI Halo -järjestelmää käyttäen llama.cpp:n RPC-moottoria ja ajetaan GLM 4.7:ää, 358 miljardin parametrin mallia, molemmilla koneilla AMD ROCm™ -kiihdytyksellä.

## Mitä opit

- Miten laajennetaan VRAM-varausta Ryzen AI Halo -järjestelmissä
- llama.cpp:n asentaminen ROCm- ja RPC-tuella
- RPC-työntekijän määrittäminen ja hajautetun päättelyn käynnistäminen kahdella solmulla
- 358 miljardin parametrin mallin ajaminen kahdella verkotetulla Ryzen AI Halo -järjestelmällä

## Muistiasetuksen määrittäminen

> **Huomio**: Tee tämä vaihe sekä Koneella 1 että Koneella 2.

<!-- @os:windows -->
Windowsissa, jotta voidaan ajaa suurempia malleja, jotka vaativat enemmän muistia, on käytettävä AMD Variable Graphics Memory (iGPU VRAM) -varausta.

Tämä tehdään avaamalla AMD Software: Adrenalin Edition -ohjauspaneeli ja siirtymällä kohtaan: `Performance > Tuning > AMD Variable Graphics Memory`. Aseta arvoksi **96 GB**. Käynnistä järjestelmä uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxissa ROCm käyttää jaettua järjestelmämuistivarantoa, ja tämä varanto on oletusarvoisesti asetettu puoleen järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla ytimen Translation Table Manager (TTM) -sivuasetusta seuraavien ohjeiden mukaisesti. AMD suosittelee asettamaan BIOS:ssa minimin varatun VRAM:in arvoksi (0,5 GB).

* Asenna pipx-työkalu ja lisää pipx:llä asennettujen pakettien polku järjestelmän hakupolkuun.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Asenna amd-debug-tools-paketti PyPI:stä.
  ```bash
  pipx install amd-debug-tools
  ```

* Suorita amd-ttm-työkalu tarkistaaksesi nykyiset jaetun muistin asetukset.
  ```bash
  amd-ttm
  ```

* Määritä jaetun muistin asetukset uudelleen arvoon **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Käynnistä järjestelmä uudelleen, jotta muutokset tulevat voimaan.


<!-- @os:end -->
<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->
## Esivaatimukset

### Laitteisto

Tämä ohjekirja edellyttää kahta Ryzen AI Halo -yksikköä ja yhtä Ethernet-kytkintä, jotka on kytketty tähtitopologiaan siten, että kumpikin yksikkö on kytketty suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Laskentasolmut, jotka muodostavat klusterin |
| 10 Gbps Ethernet-kytkin | 1 | Keskuskytkin, joka mahdollistaa usean solmun Ryzen AI Halo -kommunikoinnin (vähintään 2 porttia) |
| Ethernet-kaapeli | 2 | Yhdistää kunkin Halo-yksikön kytkimeen (suositellaan Cat 7 tai parempi) |

> **Huomio**: Kahta Ethernet-kytkimen porttia tarvitaan kahden Ryzen AI Halo -yksikön yhdistämiseen. Kolmas portti tarvitaan, jos käytät mallia erillisestä asiakaskoneesta yhden Halo-yksikön sijaan.

### Ohjelmisto
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Asenna seuraavat:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) **Desktop Development with C++** -työkuormalla
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyysisen laitteiston asennus

> **Huomio**: Tee tämä vaihe sekä Koneella 1 että Koneella 2.

Yhdistä kukin Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 (tai parempaa) kaapelia käyttäen. Tämä muodostaa 10 Gbps -yhteyden, jota käytetään solmujen väliseen nopeaan kommunikointiin.
<!-- @os:linux -->
### 1. Verkkoliitäntöjen määrittäminen

Selvitä kummallakin koneella sen verkkoliitännän nimi ja merkitse se muistiin (siihen viitataan jäljempänä nimellä `IFNAME`). Suorita:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tämä tulostaa liitännän nimen suoraan, esimerkiksi:

```bash
enp191s0
```

### 2. Verkkoyhteyden nopeuksien tarkistaminen

Varmista, että yhteys on aktiivinen ja toimii täydellä nopeudella tarkistamalla liitäntäsi nopeus:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Huomio**: Korvaa `<IFNAME>` liitännän nimellä kohdasta [1. Verkkoliitäntöjen määrittäminen](#1-determine-network-interfaces)

Sinun tulisi nähdä nopeus `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomio**: Jos nopeus on alempi kuin `10000Mb/s` tai yhteys ei muodostu, tarkista kaapeliyhteys ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Jotkin kytkimet vaativat automaattisen neuvottelun poistamista käytöstä ja yhteysnopeuden asettamista manuaalisesti; katso ohjeet kytkimesi dokumentaatiosta.

<!-- @os:end -->

<!-- @os:windows -->
### Verkkoyhteyden nopeuden tarkistaminen

Tarkista kummallakin koneella verkkoliitäntöjesi yhteysnopeus:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet-liitäntäsi tulisi olla `Up`-tilassa ja toimia nopeudella `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Huomio**: Jos nopeus on alempi kuin `10 Gbps` tai yhteys ei muodostu, tarkista kaapeliyhteys ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Jotkin kytkimet vaativat automaattisen neuvottelun poistamista käytöstä ja yhteysnopeuden asettamista manuaalisesti; katso ohjeet kytkimesi dokumentaatiosta.

<!-- @os:end -->

## llama.cpp:n asentaminen

> **Huomio**: Tee tämä vaihe sekä Koneella 1 että Koneella 2.

Käytettävissä on kaksi asennusvaihtoehtoa:

- [Vaihtoehto 1: Lemonade SDK (suositeltu)](#option-1-lemonade-sdk-recommended) – valmiiksi käännetyt binäärit, nopein käyttöönotto
- [Vaihtoehto 2: Manuaalinen lähdekoodista kääntäminen](#option-2-manual-source-build) – rakenna lähdekoodista täydellä hallinnalla käännösasetuksiin

### Vaihtoehto 1: Lemonade SDK (suositeltu)

Lemonade SDK tarjoaa öisin päivitettyjä llama.cpp-käännöksiä AMD ROCm 7 -kiihdytyksellä, kohdistuen GPU:ihin kuten gfx1151 (Strix Halo / Ryzen AI Max+ 395) ja muihin uudempiin Radeon-arkkitehtuureihin.

<!-- @os:windows -->
#### Vaihe 1: Lataa valmiiksi käännetyt binaarit

Siirry uusimman julkaisun sivulle ja lataa alustaasi ja GPU-kohdettasi vastaava arkisto:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (jossa `xxxx` on koontiversion numero).

#### Vaihe 2: Pura binaarit

Pura ladattu arkisto:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tämä hakemisto sisältää nyt ROCm-tuetut käännökset tiedostoista `llama-cli.exe`, `llama-server.exe` ja `rpc-server.exe`, jotka on esikäännetty Ryzen AI Halo -järjestelmääsi varten.

#### Vaihe 3: Vahvista GPU:n tunnistaminen

```bash
.\llama-cli.exe --list-devices
```

Odotettu tuloste:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Vaihe 1: Lataa valmiiksi käännetyt binaarit

Siirry uusimman julkaisun sivulle ja lataa alustaasi ja GPU-kohdettasi vastaava arkisto:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (jossa `xxxx` on koontiversion numero).

#### Vaihe 2: Pura ja valmistele binaarit

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Tämä hakemisto sisältää nyt ROCm-tuetut käännökset tiedostoista `llama-cli`, `llama-server` ja `rpc-server`, jotka on esikäännetty Ryzen AI Halo -järjestelmääsi varten.

#### Vaihe 3: Vahvista GPU:n tunnistaminen

```bash
./llama-cli --list-devices
```

Odotettu tuloste:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Kun llama.cpp on valmisteltu jokaisella solmulla, jatka kohtaan [Mallin lataaminen](#downloading-the-model).

### Vaihtoehto 2: Manuaalinen lähdekoodista koontaminen

<!-- @os:windows -->
#### Vaihe 1: Koonna llama.cpp

Avaa **x64 Native Tools Command Prompt** (asennettu Visual Studio Build Toolsin mukana) ja kloonaa repositorio:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Lisää HIP polkuusi ja koonna ROCm- ja RPC-tuella:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Koontilippu | Tarkoitus |
|-----------|---------|
| `-DGGML_HIP=ON` | Ottaa käyttöön ROCm/HIP-ohjelmistopinon |
| `-DGGML_RPC=ON` | Ottaa käyttöön RPC:n hajautettua päättelyä varten |
| `-DGPU_TARGETS=gfx1151` | Kohdistaa Ryzen AI Halo -GPU:hun (Radeon 8060s) |
| `-G Ninja` | Käyttää Ninja-koontijärjestelmää |

#### Vaihe 2: Vahvista GPU:n tunnistaminen

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Odotettu tuloste:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Vaihe 3: Lisää HIP käyttäjäpolkuusi

Yllä oleva koontivaihe asetti `%HIP_PATH%\bin` -muuttujan vain nykyistä istuntoa varten. Jotta HIP-kirjastot ovat käytettävissä missä tahansa terminaalissa (ei vain x64 Native Tools Command Promptissa), lisää se pysyvästi käyttäjäsi `PATH`-muuttujaan:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Kun llama.cpp on valmisteltu jokaisella solmulla, jatka kohtaan [Mallin lataaminen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Vaihe 1: Koonna llama.cpp

Kloonaa repositorio:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Koonna ROCm- ja RPC-tuella:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Koontilippu | Tarkoitus |
|-----------|---------|
| `-DGGML_HIP=ON` | Ottaa käyttöön ROCm-ohjelmistopinon |
| `-DGGML_RPC=ON` | Ottaa käyttöön RPC:n hajautettua päättelyä varten |
| `-DAMDGPU_TARGETS="gfx1151"` | Kohdistaa Ryzen AI Halo -GPU:hun (Radeon 8060s) |

Lisää koontivaihtoehtoja löydät [llama.cpp-koontidokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Vaihe 2: Vahvista GPU:n tunnistaminen

```bash
cd rocm/bin
./llama-cli --list-devices
```

Odotettu tuloste:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Kun llama.cpp on valmisteltu jokaisella solmulla, jatka kohtaan [Mallin lataaminen](#downloading-the-model).
<!-- @os:end -->

## Mallin lataaminen

Tässä ohjeessa käytetään [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) -mallia, joka on 358 miljardin parametrin malli `Q4_K_XL`-kvantisointina lähteestä [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Tällä kvantisointitasolla malli vaatii noin 205 Gt tallennustilaa ja mahtuu kahden Ryzen AI Halo -solmun yhdistetyn GPU-muistin sisään.

Lataa GGUF-tiedostot Hugging Face CLI:n avulla:
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

> **Huomio**: Mallin lataaminen on tehtävä koneella 1 (ohjaimella). RPC-työntekijäsolmut eivät tarvitse paikallista kopiota mallitiedostoista.

## Mallin käynnistäminen klusterissa

llama.cpp:n RPC (Remote Procedure Call) -moottori mahdollistaa sen, että yksi llama.cpp-instanssi voi siirtää mallin kerroksia etätyöntekijöille verkon yli. Yksi kone toimii **ohjaimena** (kone 1) ja hoitaa tokenisoinnin, ajastuksen ja orkestroinnin. Toinen kone käyttää kevyttä **RPC-palvelinta** (kone 2), joka tarjoaa GPU-muistinsa ja laskentatehonsa ohjaimen käyttöön.

Latausvaiheessa llama.cpp jakaa mallin molempien solmujen kesken. Kun malli on ladattu, päättely etenee ikään kuin sitä ajettaisiin yhdellä kiihdyttimellä. RPC hoitaa tensorien siirrot ja synkroinnin taustalla.

### Vaihe 1: Käynnistä RPC-palvelin (kone 2)

Käynnistä koneella 2 RPC-palvelin, joka tarjoaa sen GPU-resurssit ohjaimen käyttöön:
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

| Lippu | Tarkoitus |
|------|---------|
| `-p` | Portti, jossa RPC-palvelin lähettää tietoa |
| `-c` | Ottaa käyttöön paikallisen välimuistin suurille tensoreille, jolloin vältetään toistuvat verkkosiirrot mallin latauksen aikana |
| `--host` | IP-osoite, johon RPC-palvelin sidotaan (`0.0.0.0` kaikille rajapinnoille) |

Lisätietoja löydät [llama.cpp:n RPC-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Vaihe 2: Käynnistä malli (kone 1)

Kun RPC-palvelin on käynnissä koneella 2, käynnistä päättely koneelta 1 käyttäen joko `llama-cli`- tai `llama-server`-työkalua.

#### llama-cli

`llama-cli` tarjoaa pääteliittymän, jonka avulla voit olla suoraan vuorovaikutuksessa mallin kanssa. Se sopii erinomaisesti suorituskykytestaukseen, virheenkorjaukseen ja matalan tason kokeiluun.

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

> **`<RPC_WORKER_IP>`:n löytäminen**: Suorita koneella 2 komento `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomio**: Suorita tämä komento Terminaalissa (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>`:n löytäminen**: Suorita koneella 2 komento `ipconfig | findstr /C:"IPv4"` Terminaalissa (Powershell) löytääksesi sen paikallisen IP-osoitteen.

<!-- @os:end -->

Kun `llama-cli` on käynnissä, se näyttää mallin latauksen edistymisen ja avaa interaktiivisen kehotteen, jossa voit keskustella suoraan mallin kanssa:

![llama-cli ajaa GLM 4.7 -mallia kahdella solmulla](assets/llama-cli-example.png)
#### llama-server

`llama-server` tarjoaa saman päättelymoottorin pysyvän palvelinprosessin kautta, jossa on integroitu web-käyttöliittymä ja OpenAI-yhteensopiva HTTP-API. Tämä on ensisijainen käyttöliittymä pidempikestoisiin käyttöönottoihin, useiden käyttäjien käyttöön ja integrointiin ulkoisten työkalujen kanssa.

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

> **`<RPC_WORKER_IP>`:n löytäminen**: Suorita Koneella 2 komento `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomio**: Suorita tämä komento Terminalissa (Powershell).

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

> **`<RPC_WORKER_IP>`:n löytäminen**: Suorita Koneella 2 komento `ipconfig | findstr /C:"IPv4"` Terminalissa (Powershell) löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

Kun palvelin on käynnistetty, avaa selaimessa osoite `http://<HOST_IP>:8081` päästäksesi sisäänrakennettuun web-käyttöliittymään. Tämä tarjoaa selainpohjaisen chat-käyttöliittymän mallin kanssa vuorovaikutukseen:

![llama-server-web-käyttöliittymä, jossa GLM 4.7 ajetaan kahdella solmulla](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>`:n löytäminen**: Suorita Koneella 1 komento `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>`:n löytäminen**: Suorita Koneella 1 komento `ipconfig | findstr /C:"IPv4"` Terminalissa (Powershell) löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

#### Parametriviite

| Lippu | Tarkoitus |
|------|---------|
| `-m` | GGUF-mallitiedoston polku (käytä ensimmäistä osaa, `00001-of-00005`) |
| `-c` | Kontekstin koko tokeneina. Suuremmat arvot käyttävät enemmän muistia |
| `-fa on` | Ottaa käyttöön rocWMMA Flash Attentionin, joka parantaa suorituskykyä AMD-näytönohjaimilla |
| `-ngl 999` | Siirtää kaikki mallin kerrokset GPU:lle |
| `-lm none` | Asettaa mallin latausmoodin arvoon `none`, mikä poistaa muistikartoituksen käytöstä ja lyhentää latausaikoja, kun mallin koko ylittää järjestelmän RAM-muistin mutta mahtuu VRAM-muistiin |
| `--host` | IP-osoite, johon `llama-server` sidotaan (vain `llama-server`) |
| `--port` | Portti, jossa HTTP-API tarjotaan (vain `llama-server`) |
| `--rpc` | Pilkuilla eroteltu luettelo RPC-työntekijöiden päätepisteistä (`IP:portti`) |

Katso täydelliset parametrien käyttöohjeet [llama-cli-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) ja [llama-server-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Seuraavat vaiheet

- **Yhdistä kolmannen osapuolen sovelluksia**: `llama-server` tarjoaa OpenAI-yhteensopivan API:n. Osoita mikä tahansa OpenAI-yhteensopiva sovellus (kuten Open WebUI) osoitteeseen `http://<HOST_IP>:8081` millä tahansa paikkamerkki-API-avaimella (esim. `none`) yhdistääksesi klusteriisi
- **Tutustu muihin malleihin**: Selaa kvantisoituja GGUF-tiedostoja [Hugging Facessa](https://huggingface.co/models?search=gguf) löytääksesi malleja, jotka mahtuvat klusterisi yhteenlaskettuun GPU-muistiin
- **Skaalaa neljään solmuun**: Lisää kaksi ylimääräistä Ryzen AI Halo -järjestelmää lisätyöntekijöiksi (RPC workers) päästäksesi käsiksi malleihin, joiden koko on jopa biljoona parametria. Anna lisäpäätepisteet parametrille `--rpc` pilkuilla eroteltuna luettelona (esim. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)