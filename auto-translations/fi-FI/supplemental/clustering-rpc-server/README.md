<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se saattaa sisältää virheitä, ja jotkin vaiheet, komennot, lataukset tai tuotteiden saatavuus voivat vaihdella kielesi tai alueesi mukaan. Jos jokin vaikuttaa virheelliseltä, pidä alkuperäistä englanninkielistä playbookia ensisijaisena lähteenä.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> Tässä ohjekirjassa käytetään erityismerkintöjä, joita GitHub ei pysty renderöimään. Käy osoitteessa [amd.com/playbooks](https://amd.com/playbooks) nähdäksesi tämän sisällön oikein esikatseltuna.
<!-- @github-only:end -->

# Kahden Ryzen™ AI Halo -järjestelmän klusterointi RPC:llä

## Yleiskatsaus

Ryzen™ AI Halosi pystyy jo suorittamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän askeleen pidemmälle yhdistämällä useiden järjestelmien GPU-muistin paikallisverkon yli, jolloin pääset käsiksi vieläkin suurempiin malleihin, joilla on vahvempi päättelykyky, parempi koodin generointi ja syvempi monikielinen ymmärrys – kaikki täysin omalla laitteistollasi.

Tämä ohjekirja opettaa, kuinka klusteroit kaksi Ryzen AI Halo -järjestelmää llama.cpp:n RPC-moottorilla ja ajat GLM 4.7:ää, 358 miljardin parametrin mallia, molemmilla koneilla AMD ROCm™ -kiihdytyksellä.

## Mitä opit

- Kuinka laajentaa VRAM-allokointia Ryzen AI Halo -järjestelmissä
- llama.cpp:n asentaminen ROCm- ja RPC-tuella
- RPC-työntekijän (worker) määrittäminen ja hajautetun päättelyn käynnistäminen kahdella solmulla
- 358 miljardin parametrin mallin ajaminen kahdella verkotetulla Ryzen AI Halo -järjestelmällä

## Muistiasetusten määrittäminen

> **Huomautus**: Suorita tämä vaihe sekä koneella 1 että koneella 2.

<!-- @os:windows -->
Windowsissa suurempien, enemmän muistia vaativien mallien ajamiseen tarvitaan AMD Variable Graphics Memory (iGPU VRAM) -allokointia.

Tämä voidaan tehdä avaamalla AMD Software: Adrenalin Edition -hallintapaneeli ja siirtymällä kohtaan: `Performance > Tuning > AMD Variable Graphics Memory`. Aseta arvoksi **96 GB**. Käynnistä järjestelmä uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxissa ROCm käyttää jaettua järjestelmämuistipoolia, ja tämä pooli on oletusarvoisesti määritetty puoleen järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla kernelin Translation Table Manager (TTM) -sivuasetusta seuraavien ohjeiden mukaisesti. AMD suosittelee asettamaan minimin varatulle VRAM-muistille BIOSissa (0.5 GB).

* Asenna pipx-työkalu ja lisää pipx:llä asennettujen wheelien polku järjestelmän hakupolkuun.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Asenna amd-debug-tools-wheel PyPI:stä.
  ```bash
  pipx install amd-debug-tools
  ```

* Suorita amd-ttm-työkalu tarkistaaksesi nykyiset jaetun muistin asetukset.
  ```bash
  amd-ttm
  ```

* Aseta jaetun muistin asetukset uudelleen arvoon **120 GB**:
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

Tämä ohjekirja edellyttää kahta Ryzen AI Halo -yksikköä ja yhtä Ethernet-kytkintä, kytkettynä tähtitopologiaan siten, että kukin yksikkö on kytketty suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Klusterin muodostavat laskentasolmut |
| 10 Gbps Ethernet-kytkin | 1 | Keskitetty kytkin, joka mahdollistaa usean solmun välisen Ryzen AI Halo -viestinnän (vähintään 2 porttia) |
| Ethernet-kaapeli | 2 | Yhdistää kunkin Halo-yksikön kytkimeen (suositellaan Cat 7 -kaapelia tai parempaa) |

> **Huomautus**: Kahden Ryzen AI Halo -yksikön yhdistämiseen tarvitaan kaksi Ethernet-kytkimen porttia. Kolmas portti tarvitaan, jos käytät mallia erillisestä asiakaskoneesta eikä jommastakummasta Halo-yksiköstä.

### Ohjelmisto
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Asenna seuraavat:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) ja **Desktop Development with C++** -työkuorma
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyysisen laitteiston asennus

> **Huomautus**: Suorita tämä vaihe sekä koneella 1 että koneella 2.

Yhdistä kukin Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 -kaapelilla (tai paremmalla). Tämä muodostaa 10 Gbps-yhteyden, jota käytetään solmujen väliseen nopeaan viestintään.
<!-- @os:linux -->
### 1. Määritä verkkoliitännät

Selvitä kummallakin koneella sen verkkoliitännän nimi ja kirjoita se muistiin (siihen viitataan jäljempänä nimellä `IFNAME`). Suorita:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tämä tulostaa liitännän nimen suoraan, esimerkiksi:

```bash
enp191s0
```

### 2. Vahvista verkkoyhteyden nopeudet

Varmista, että yhteys on aktiivinen ja toimii täydellä nopeudella tarkistamalla liitäntäsi nopeus:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Huomautus**: Korvaa `<IFNAME>` kohdassa [1. Määritä verkkoliitännät](#1-determine-network-interfaces) saadulla liitännän nimellä

Sinun pitäisi nähdä nopeus `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomautus**: Jos nopeus on alhaisempi kuin `10000Mb/s` tai yhteys ei muodostu, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Jotkin kytkimet edellyttävät automaattisen neuvottelun poistamista käytöstä ja yhteysnopeuden asettamista manuaalisesti; katso ohjeet kytkimesi dokumentaatiosta.

<!-- @os:end -->

<!-- @os:windows -->
### Vahvista verkkoyhteyden nopeus

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

> **Huomautus**: Jos nopeus on alhaisempi kuin `10 Gbps` tai yhteys ei muodostu, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Jotkin kytkimet edellyttävät automaattisen neuvottelun poistamista käytöstä ja yhteysnopeuden asettamista manuaalisesti; katso ohjeet kytkimesi dokumentaatiosta.

<!-- @os:end -->

## llama.cpp:n asentaminen

> **Huomautus**: Suorita tämä vaihe sekä koneella 1 että koneella 2.

Käytettävissä on kaksi asennusvaihtoehtoa:

- [Vaihtoehto 1: Lemonade SDK (suositeltu)](#option-1-lemonade-sdk-recommended) - valmiiksi käännetyt binäärit, nopein asennustapa
- [Vaihtoehto 2: Manuaalinen lähdekoodista kääntäminen](#option-2-manual-source-build) - kääntäminen lähdekoodista täydellä hallinnalla käännöslippuihin

### Vaihtoehto 1: Lemonade SDK (suositeltu)

Lemonade SDK tarjoaa öisin päivitettyjä (nightly) llama.cpp-käännöksiä AMD ROCm 7 -kiihdytyksellä, kohdistuen GPU:ihin kuten gfx1151 (Strix Halo / Ryzen AI Max+ 395) ja muihin uusiin Radeon-arkkitehtuureihin.

<!-- @os:windows -->
#### Vaihe 1: Esiladottujen binaaritiedostojen lataaminen

Siirry uusimman julkaisun sivulle ja lataa alustaasi ja GPU-kohdettasi vastaava arkisto:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (jossa `xxxx` on koontiversion numero).

#### Vaihe 2: Binaaritiedostojen purkaminen

Pura ladattu arkisto:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tämä hakemisto sisältää nyt ROCm-yhteensopivat koontiversiot tiedostoista `llama-cli.exe`, `llama-server.exe` ja `rpc-server.exe`, jotka on esikäännetty Ryzen AI Halo -järjestelmääsi varten.

#### Vaihe 3: GPU:n tunnistamisen tarkistaminen

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
#### Vaihe 1: Esiladottujen binaaritiedostojen lataaminen

Siirry uusimman julkaisun sivulle ja lataa alustaasi ja GPU-kohdettasi vastaava arkisto:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (jossa `xxxx` on koontiversion numero).

#### Vaihe 2: Binaaritiedostojen purkaminen ja valmisteleminen

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Tämä hakemisto sisältää nyt ROCm-yhteensopivat koontiversiot tiedostoista `llama-cli`, `llama-server` ja `rpc-server`, jotka on esikäännetty Ryzen AI Halo -järjestelmääsi varten.

#### Vaihe 3: GPU:n tunnistamisen tarkistaminen

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
Kun llama.cpp on valmisteltu kummallakin solmulla, jatka kohtaan [Mallin lataaminen](#downloading-the-model).

### Vaihtoehto 2: Manuaalinen lähdekoodista koontaminen

<!-- @os:windows -->
#### Vaihe 1: llama.cpp:n koontaminen

Avaa **x64 Native Tools Command Prompt** (asennettu Visual Studio Build Toolsin mukana) ja kloonaa arkisto:

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

#### Vaihe 2: GPU:n tunnistamisen tarkistaminen

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

#### Vaihe 3: HIP:n lisääminen käyttäjän polkuun

Yllä oleva koontivaihe asetti `%HIP_PATH%\bin`-muuttujan vain nykyistä istuntoa varten. Jotta HIP-kirjastot ovat käytettävissä missä tahansa päätteessä (ei vain x64 Native Tools Command Promptissa), lisää se pysyvästi käyttäjän `PATH`-muuttujaan:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Kun llama.cpp on valmisteltu kummallakin solmulla, jatka kohtaan [Mallin lataaminen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Vaihe 1: llama.cpp:n koontaminen

Kloonaa arkisto:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Koonna ROCm- ja RPC-tuella:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Koontilippu | Tarkoitus |
|-----------|---------|
| `-DGGML_HIP=ON` | Ottaa käyttöön ROCm-ohjelmistopinon |
| `-DGGML_RPC=ON` | Ottaa käyttöön RPC:n hajautettua päättelyä varten |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Ottaa käyttöön rocWMMA:n parannettua Flash Attentionia varten AMD GPU:issa |
| `-DAMDGPU_TARGETS="gfx1151"` | Kohdistaa Ryzen AI Halo -GPU:hun (Radeon 8060s) |

Lisätietoja koontiasetuksista löydät kohdasta [llama.cpp-koontidokumentaatio](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Vaihe 2: GPU:n tunnistamisen tarkistaminen

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

Kun llama.cpp on valmisteltu kummallakin solmulla, jatka kohtaan [Mallin lataaminen](#downloading-the-model).
<!-- @os:end -->

## Mallin lataaminen

Tämä toimintaohje käyttää mallia [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), joka on 358 miljardin parametrin malli `Q4_K_XL`-kvantisoinnilla lähteestä [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Tällä kvantisoinnilla malli vaatii noin 205 Gt tallennustilaa ja mahtuu kahden Ryzen AI Halo -solmun yhdistettyyn GPU-muistiin.

Lataa GGUF-tiedostot Hugging Face -komentorivityökalulla:
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

> **Huomautus**: Mallin lataaminen on suoritettava koneella 1 (ohjaimella). RPC-työntekijäsolmujen ei tarvitse sisältää paikallista kopiota mallitiedostoista.

## Mallin käynnistäminen klusterissa

Llama.cpp:n RPC-moottori (Remote Procedure Call) mahdollistaa sen, että yksi llama.cpp-instanssi voi siirtää mallin kerroksia verkon yli etätyöntekijöille. Yksi kone toimii **ohjaimena** (kone 1) ja huolehtii tokenisoinnista, ajoituksesta ja orkestroinnista. Toinen kone suorittaa kevyttä **RPC-palvelinta** (kone 2), joka altistaa GPU-muistinsa ja laskentatehonsa ohjaimen käyttöön.

Latausvaiheessa llama.cpp jakaa mallin molempien solmujen kesken. Kun malli on ladattu, päättely etenee ikään kuin se toimisi yhdellä kiihdyttimellä. RPC hoitaa tensorisiirrot ja synkronoinnin taustalla.

### Vaihe 1: RPC-palvelimen käynnistäminen (kone 2)

Käynnistä koneella 2 RPC-palvelin, jotta sen GPU-resurssit näkyvät ohjaimelle:
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

| Lippu | Tarkoitus |
|------|---------|
| `-p` | Portti, jolla RPC-palvelinta lähetetään |
| `-c` | Ottaa käyttöön paikallisen välimuistin suurille tensoreille, mikä välttää toistuvat verkkosiirrot mallin latauksen aikana |
| `--host` | IP-osoite, johon RPC-palvelin sidotaan (`0.0.0.0` kaikille rajapinnoille) |

Lisätietoja löydät kohdasta [llama.cpp:n RPC-dokumentaatio](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Vaihe 2: Mallin käynnistäminen (kone 1)

Kun RPC-palvelin on käynnissä koneella 2, käynnistä päättely koneelta 1 käyttäen joko `llama-cli`- tai `llama-server`-työkalua.

#### llama-cli

`llama-cli` tarjoaa pääteliittymän suoraan mallin kanssa vuorovaikutukseen. Se sopii erinomaisesti suorituskykytestaukseen, virheenkorjaukseen ja matalan tason kokeiluun.

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

> **`<RPC_WORKER_IP>`:n löytäminen**: Suorita koneella 2 komento `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus**: Suorita tämä komento päätteessä (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>`:n löytäminen**: Suorita koneella 2 komento `ipconfig | findstr /C:"IPv4"` päätteessä (Powershell) löytääksesi sen paikallisen IP-osoitteen.

<!-- @os:end -->

Kun ohjelma on käynnissä, `llama-cli` näyttää mallin latauksen edistymisen ja avaa interaktiivisen kehotteen, jossa voit keskustella suoraan mallin kanssa:

![llama-cli suorittamassa GLM 4.7 -mallia kahdella solmulla](assets/llama-cli-example.png)
#### llama-server

`llama-server` tarjoaa saman päättelymoottorin pysyvän palvelinprosessin kautta, johon sisältyy integroitu web-käyttöliittymä ja OpenAI-yhteensopiva HTTP-API. Tämä on suositeltu käyttöliittymä pidempikestoisiin käyttöönottoihin, useiden käyttäjien pääsyyn ja integrointiin ulkoisten työkalujen kanssa.

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

> **`<RPC_WORKER_IP>`-osoitteen selvittäminen**: Suorita Koneella 2 komento `hostname -I | awk '{print $1}'` selvittääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomio**: Suorita tämä komento Terminaalissa (Powershell).

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

> **`<RPC_WORKER_IP>`-osoitteen selvittäminen**: Suorita Koneella 2 komento `ipconfig | findstr /C:"IPv4"` Terminaalissa (Powershell) selvittääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

Kun palvelin on käynnistetty, avaa selaimessasi `http://<HOST_IP>:8081` päästäksesi sisäänrakennettuun web-käyttöliittymään. Tämä tarjoaa selainpohjaisen keskusteluliittymän mallin kanssa vuorovaikutukseen:

![llama-server-web-käyttöliittymä, jossa GLM 4.7 käynnissä kahdella solmulla](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>`-osoitteen selvittäminen**: Suorita Koneella 1 komento `hostname -I | awk '{print $1}'` selvittääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>`-osoitteen selvittäminen**: Suorita Koneella 1 komento `ipconfig | findstr /C:"IPv4"` Terminaalissa (Powershell) selvittääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

#### Parametriviite

| Lippu | Tarkoitus |
|------|---------|
| `-m` | Polku GGUF-mallitiedostoon (käytä ensimmäistä osaa, `00001-of-00005`) |
| `-c` | Kontekstikoko tokeneina. Suuremmat arvot käyttävät enemmän muistia |
| `-fa on` | Ottaa käyttöön rocWMMA Flash Attention -toiminnon parantaakseen suorituskykyä AMD-GPU:illa |
| `-ngl 999` | Siirtää kaikki mallin kerrokset GPU:lle |
| `--no-mmap` | Poistaa muistikartoituksen käytöstä, mikä lyhentää latausaikoja, kun mallin koko ylittää järjestelmän RAM-muistin mutta mahtuu VRAM-muistiin |
| `--host` | IP-osoite, johon `llama-server` sidotaan (vain `llama-server`) |
| `--port` | Portti, jossa HTTP-API tarjoillaan (vain `llama-server`) |
| `--rpc` | Pilkuin eroteltu luettelo RPC-työntekijöiden päätepisteistä (`IP:port`) |

Katso koko parametrien käyttöohjeet [llama-cli-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) ja [llama-server-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Seuraavat vaiheet

- **Yhdistä kolmannen osapuolen sovelluksia**: `llama-server` tarjoaa OpenAI-yhteensopivan API:n. Osoita mikä tahansa OpenAI-yhteensopiva sovellus (kuten Open WebUI) osoitteeseen `http://<HOST_IP>:8081` käyttäen mitä tahansa paikkamerkki-API-avainta (esim. `none`) yhdistääksesi klusteriisi
- **Tutustu muihin malleihin**: Selaa kvantisoituja GGUF-malleja [Hugging Facessa](https://huggingface.co/models?search=gguf) löytääksesi malleja, jotka mahtuvat klusterisi yhdistettyyn GPU-muistiin
- **Skaalaa neljään solmuun**: Lisää kaksi muuta Ryzen AI Halo -järjestelmää lisä-RPC-työntekijöiksi päästäksesi käsiksi biljoonan parametrin kokoluokan malleihin. Anna lisää päätepisteitä `--rpc`-parametrille pilkuin eroteltuna luettelona (esim. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)