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

Ryzen™ AI Halo -järjestelmäsi pystyy jo suorittamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän askeleen pidemmälle yhdistämällä useiden järjestelmien GPU-muistin paikallisen verkon välityksellä, mikä antaa sinulle pääsyn vielä suurempiin malleihin, joilla on vahvempi päättelykyky, parempi koodin generointi ja syvempi monikielinen ymmärrys – kaikki täysin omalla laitteistollasi.

Tämä ohjekirja opettaa sinulle, kuinka klusteroida kaksi Ryzen AI Halo -järjestelmää käyttäen llama.cpp:n RPC-moottoria ja suorittaa GLM 4.7:ää, 358 miljardin parametrin mallia, molemmilla koneilla AMD ROCm™ -kiihdytyksellä.

## Mitä opit

- Kuinka laajentaa VRAM-muistin allokointia Ryzen AI Halo -järjestelmissä
- llama.cpp:n asentaminen ROCm- ja RPC-tuella
- RPC-työntekijän määrittäminen ja hajautetun päättelyn käynnistäminen kahden solmun välillä
- 358 miljardin parametrin mallin suorittaminen kahdella verkotetulla Ryzen AI Halo -järjestelmällä

## Muistiasetuksen määrittäminen

> **Huomautus**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

<!-- @os:windows -->
Windowsissa, jotta voidaan suorittaa suurempia malleja, jotka vaativat enemmän muistia, meidän tulee käyttää AMD Variable Graphics Memory (iGPU VRAM) -allokointia.

Tämä voidaan tehdä avaamalla AMD Software: Adrenalin Edition -ohjauspaneeli ja siirtymällä kohtaan: `Performance > Tuning > AMD Variable Graphics Memory`. Aseta arvoksi **96 GB**. Käynnistä järjestelmä uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxissa ROCm hyödyntää jaettua järjestelmämuistin muistivarantoa, ja tämä varanto on oletusarvoisesti asetettu puoleen järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla ytimen Translation Table Manager (TTM) -sivuasetusta seuraavien ohjeiden mukaisesti. AMD suosittelee asettamaan BIOS:ssa vähimmäismäärän varattua VRAM-muistia (0,5 GB).

* Asenna pipx-työkalu ja lisää pipx:llä asennettujen wheel-pakettien polku järjestelmän hakupolkuun.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Asenna amd-debug-tools-wheel PyPI:stä.
  ```bash
  pipx install amd-debug-tools
  ```

* Suorita amd-ttm-työkalu kysyäksesi jaetun muistin nykyiset asetukset.
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

Tämä ohjekirja vaatii kaksi Ryzen AI Halo -yksikköä ja yhden Ethernet-kytkimen, jotka on kytketty tähtitopologiaan siten, että jokainen yksikkö on kytketty suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Klusterin muodostavat laskentasolmut |
| 10 Gbps Ethernet-kytkin | 1 | Keskitetty kytkin, joka mahdollistaa Ryzen AI Halo -yksiköiden välisen viestinnän useiden solmujen kesken (vähintään 2 porttia) |
| Ethernet-kaapeli | 2 | Yhdistää jokaisen Halo-yksikön kytkimeen (suositellaan Cat 7 tai parempaa) |

> **Huomautus**: Kahden Ryzen AI Halo -yksikön yhdistämiseen tarvitaan kaksi Ethernet-kytkimen porttia. Kolmas portti tarvitaan, jos käytät mallia erillisestä asiakaskoneesta yhden Halo-yksikön sijaan.

### Ohjelmisto
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Asenna seuraavat:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) ja **Desktop Development with C++** -työkuormitus
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyysisen laitteiston asennus

> **Huomautus**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

Yhdistä jokainen Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 (tai paremmalla) kaapelilla. Tämä luo 10 Gbps -yhteyden, jota käytetään solmujen väliseen nopeaan viestintään.
<!-- @os:linux -->
### 1. Määritä verkkoliitännät

Selvitä kummankin koneen verkkoliitännän nimi ja kirjoita se muistiin (siihen viitataan alla nimellä `IFNAME`). Suorita:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tämä tulostaa liitännän nimen suoraan, esimerkiksi:

```bash
enp191s0
```

### 2. Tarkista verkkoyhteyden nopeudet

Varmista, että yhteys on aktiivinen ja toimii täydellä nopeudella tarkistamalla liitäntäsi nopeus:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Huomautus**: Korvaa `<IFNAME>` kohdassa [1. Määritä verkkoliitännät](#1-determine-network-interfaces) saadulla liitännän nimellä

Sinun tulisi nähdä nopeus `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomautus**: Jos nopeus on pienempi kuin `10000Mb/s` tai yhteys ei muodostu, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Jotkin kytkimet vaativat automaattisen neuvottelun poistamista käytöstä ja yhteysnopeuden asettamista manuaalisesti; katso lisätietoja kytkimesi dokumentaatiosta.

<!-- @os:end -->

<!-- @os:windows -->
### Tarkista verkkoyhteyden nopeus

Tarkista kummankin koneen verkkoliitäntöjen yhteysnopeus:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet-liitäntäsi tulisi olla `Up`-tilassa ja toimia nopeudella `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Huomautus**: Jos nopeus on pienempi kuin `10 Gbps` tai yhteys ei muodostu, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Jotkin kytkimet vaativat automaattisen neuvottelun poistamista käytöstä ja yhteysnopeuden asettamista manuaalisesti; katso lisätietoja kytkimesi dokumentaatiosta.

<!-- @os:end -->

## llama.cpp:n asentaminen

> **Huomautus**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

Käytettävissä on kaksi asennusvaihtoehtoa:

- [Vaihtoehto 1: Lemonade SDK (Suositeltu)](#option-1-lemonade-sdk-recommended) - valmiiksi käännetyt binaarit, nopein käyttöönotto
- [Vaihtoehto 2: Manuaalinen lähdekoodista kääntäminen](#option-2-manual-source-build) - käännä lähdekoodista täydellä hallinnalla käännöslippujen suhteen

### Vaihtoehto 1: Lemonade SDK (Suositeltu)

Lemonade SDK tarjoaa yön yli tehtyjä käännöksiä llama.cpp:stä AMD ROCm 7 -kiihdytyksellä, kohdistuen GPU:ihin kuten gfx1151 (Strix Halo / Ryzen AI Max+ 395) ja muihin uudempiin Radeon-arkkitehtuureihin.

<!-- @os:windows -->
#### Vaihe 1: Lataa valmiiksi käännetyt binäärit

Siirry uusimman julkaisun sivulle ja lataa arkisto, joka vastaa alustaasi ja GPU-kohdettasi:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (jossa `xxxx` on käännösnumero).

#### Vaihe 2: Pura binäärit

Pura ladattu arkisto:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tämä hakemisto sisältää nyt ROCm-tuetut käännökset tiedostoista `llama-cli.exe`, `llama-server.exe` ja `rpc-server.exe`, esikäännettyinä Ryzen AI Halo -järjestelmällesi.

#### Vaihe 3: Vahvista GPU:n tunnistus

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
#### Vaihe 1: Lataa valmiiksi käännetyt binäärit

Siirry uusimman julkaisun sivulle ja lataa arkisto, joka vastaa alustaasi ja GPU-kohdettasi:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (jossa `xxxx` on käännösnumero).

#### Vaihe 2: Pura ja valmistele binäärit

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Tämä hakemisto sisältää nyt ROCm-tuetut käännökset tiedostoista `llama-cli`, `llama-server` ja `rpc-server`, esikäännettyinä Ryzen AI Halo -järjestelmällesi.

#### Vaihe 3: Vahvista GPU:n tunnistus

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
Kun llama.cpp on valmisteltu jokaisessa solmussa, jatka kohtaan [Mallin lataaminen](#downloading-the-model).

### Vaihtoehto 2: Manuaalinen lähdekoodista kääntäminen

<!-- @os:windows -->
#### Vaihe 1: Käännä llama.cpp

Avaa **x64 Native Tools Command Prompt** (asennettu Visual Studio Build Toolsin mukana) ja kloonaa tietovarasto:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Lisää HIP polkuusi ja käännä ROCm- ja RPC-tuella:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Käännöslippu | Tarkoitus |
|-----------|---------|
| `-DGGML_HIP=ON` | Ottaa käyttöön ROCm/HIP-ohjelmistopinon |
| `-DGGML_RPC=ON` | Ottaa käyttöön RPC:n hajautettua päättelyä varten |
| `-DGPU_TARGETS=gfx1151` | Kohdistaa Ryzen AI Halo -näytönohjaimeen (Radeon 8060s) |
| `-G Ninja` | Käyttää Ninja-käännösjärjestelmää |

#### Vaihe 2: Vahvista GPU:n tunnistus

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

Yllä oleva käännösvaihe asetti `%HIP_PATH%\bin` -muuttujan vain nykyistä istuntoa varten. Jotta HIP-kirjastot olisivat käytettävissä missä tahansa päätteessä (ei vain x64 Native Tools Command Promptissa), lisää se pysyvästi käyttäjäsi `PATH`-muuttujaan:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Kun llama.cpp on valmisteltu jokaisessa solmussa, jatka kohtaan [Mallin lataaminen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Vaihe 1: Käännä llama.cpp

Kloonaa tietovarasto:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Käännä ROCm- ja RPC-tuella:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Käännöslippu | Tarkoitus |
|-----------|---------|
| `-DGGML_HIP=ON` | Ottaa käyttöön ROCm-ohjelmistopinon |
| `-DGGML_RPC=ON` | Ottaa käyttöön RPC:n hajautettua päättelyä varten |
| `-DAMDGPU_TARGETS="gfx1151"` | Kohdistaa Ryzen AI Halo -näytönohjaimeen (Radeon 8060s) |

Lisää käännösvaihtoehtoja löydät [llama.cpp-käännösdokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Vaihe 2: Vahvista GPU:n tunnistus

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

Kun llama.cpp on valmisteltu jokaisessa solmussa, jatka kohtaan [Mallin lataaminen](#downloading-the-model).
<!-- @os:end -->

## Mallin lataaminen

Tämä käyttöopas käyttää [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) -mallia, joka on 358 miljardin parametrin malli `Q4_K_XL`-kvantisoinnilla, lähteenä [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Tällä kvantisoinnilla malli vaatii noin 205 Gt tallennustilaa ja mahtuu kahden Ryzen AI Halo -solmun yhdistetyn GPU-muistin sisään.

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

> **Huomautus**: Mallin lataus on suoritettava koneella 1 (ohjaimella). RPC-työsolmujen ei tarvitse säilyttää paikallista kopiota mallin tiedostoista.

## Mallin käynnistäminen klusterissa

llama.cpp:n RPC (Remote Procedure Call) -moottori mahdollistaa yhden llama.cpp-instanssin ulkoistaa mallin kerroksia etätyöntekijöille verkon yli. Yksi kone toimii **ohjaimena** (kone 1) ja huolehtii tokenisoinnista, ajoituksesta ja orkestroinnista. Toinen kone suorittaa kevyttä **RPC-palvelinta** (kone 2), joka jakaa GPU-muistinsa ja laskentatehonsa ohjaimen käyttöön.

Latausvaiheessa llama.cpp jakaa mallin molempien solmujen kesken. Kun malli on ladattu, päättely etenee ikään kuin se toimisi yhdellä kiihdyttimellä. RPC hoitaa tensorisiirrot ja synkronoinnin taustalla.

### Vaihe 1: Käynnistä RPC-palvelin (kone 2)

Käynnistä RPC-palvelin koneella 2 jakaaksesi sen GPU-resurssit ohjaimen käyttöön:
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
| `-p` | Portti, jolla RPC-palvelin lähetetään |
| `-c` | Ottaa käyttöön paikallisen välimuistin suuria tensoreita varten, mikä välttää toistuvia verkkosiirtoja mallin latauksen aikana |
| `--host` | IP-osoite, johon RPC-palvelin sidotaan (`0.0.0.0` kaikille rajapinnoille) |

Lisätietoja löydät [llama.cpp:n RPC-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Vaihe 2: Käynnistä malli (kone 1)

Kun RPC-palvelin on käynnissä koneella 2, käynnistä päättely koneelta 1 käyttäen joko `llama-cli`- tai `llama-server`-työkalua.

#### llama-cli

`llama-cli` tarjoaa pääteliittymän, jonka avulla voit vuorovaikuttaa suoraan mallin kanssa. Se sopii erinomaisesti suorituskykytestaukseen, virheenkorjaukseen ja matalan tason kokeiluihin.

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
> **Huomautus**: Suorita tämä komento Terminaalissa (Powershell).

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

Kun komento on käynnissä, `llama-cli` näyttää mallin latauksen edistymisen ja avaa interaktiivisen kehotteen, jossa voit keskustella suoraan mallin kanssa:

![llama-cli suorittamassa GLM 4.7:ää kahdessa solmussa](assets/llama-cli-example.png)
#### llama-server

`llama-server` tarjoaa saman päättelymoottorin pysyvän palvelinprosessin kautta, jossa on integroitu web-käyttöliittymä ja OpenAI-yhteensopiva HTTP-API. Tämä on suositeltu käyttöliittymä pidempikestoisiin käyttöönottoihin, usean käyttäjän pääsyyn ja integrointiin ulkoisten työkalujen kanssa.

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

> **`<RPC_WORKER_IP>`:n selvittäminen**: Suorita Koneella 2 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus**: Suorita tämä komento Terminaalissa (Powershell).

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

> **`<RPC_WORKER_IP>`:n selvittäminen**: Suorita Koneella 2 komento `ipconfig | findstr /C:"IPv4"` Terminaalissa (Powershell) sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

Kun palvelin on käynnistetty, avaa selaimessasi osoite `http://<HOST_IP>:8081` päästäksesi sisäänrakennettuun web-käyttöliittymään. Tämä tarjoaa selainpohjaisen keskusteluliittymän mallin kanssa vuorovaikutukseen:

![llama-server-web-käyttöliittymä, joka suorittaa GLM 4.7:ää kahden solmun välillä](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>`:n selvittäminen**: Suorita Koneella 1 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>`:n selvittäminen**: Suorita Koneella 1 komento `ipconfig | findstr /C:"IPv4"` Terminaalissa (Powershell) sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

#### Parametriviite

| Lippu | Tarkoitus |
|------|---------|
| `-m` | Polku GGUF-mallitiedostoon (käytä ensimmäistä osaa, `00001-of-00005`) |
| `-c` | Kontekstin koko tokeneina. Suuremmat arvot käyttävät enemmän muistia |
| `-fa on` | Ottaa käyttöön rocWMMA Flash Attentionin parantaakseen suorituskykyä AMD-näytönohjaimilla |
| `-ngl 999` | Siirtää kaikki mallin kerrokset GPU:lle |
| `-lm none` | Asettaa mallin latausmuodoksi `none`, mikä poistaa käytöstä muistiin kuvantamisen (memory-mapping) latausaikojen lyhentämiseksi silloin, kun mallin koko ylittää järjestelmän RAM-muistin mutta mahtuu VRAM-muistiin |
| `--host` | IP-osoite, johon `llama-server` sidotaan (vain `llama-server`) |
| `--port` | Portti, jossa HTTP-API tarjotaan (vain `llama-server`) |
| `--rpc` | Pilkuilla erotettu luettelo RPC-työntekijöiden päätepisteistä (`IP:port`) |

Katso täydelliset parametrien käyttöohjeet [llama-cli-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) ja [llama-server-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Seuraavat vaiheet

- **Kolmannen osapuolen sovellusten yhdistäminen**: `llama-server` tarjoaa OpenAI-yhteensopivan API:n. Osoita mikä tahansa OpenAI-yhteensopiva sovellus (kuten Open WebUI) osoitteeseen `http://<HOST_IP>:8081` millä tahansa paikkamerkki-API-avaimella (esim. `none`) yhdistääksesi klusteriisi
- **Muiden mallien tutkiminen**: Selaa kvantisoituja GGUF-tiedostoja [Hugging Facessa](https://huggingface.co/models?search=gguf) löytääksesi malleja, jotka mahtuvat klusterisi yhteenlaskettuun GPU-muistiin
- **Skaalaus neljään solmuun**: Lisää kaksi Ryzen AI Halo -järjestelmää lisää RPC-työntekijöiksi päästäksesi käsiksi malleihin, joiden koko on jopa biljoona parametria. Anna lisää päätepisteitä `--rpc`-parametrille pilkuilla erotettuna luettelona (esim. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)