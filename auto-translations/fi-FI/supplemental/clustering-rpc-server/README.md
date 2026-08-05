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

# Kahden Ryzen™ AI Halon klusterointi RPC:llä

## Yleiskatsaus

Ryzen™ AI Halosi pystyy jo ajamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän askeleen pidemmälle yhdistämällä useiden järjestelmien GPU-muistin paikallisverkon yli, jolloin käytettävissäsi on entistä suurempia malleja, joilla on vahvempi päättelykyky, parempi koodin generointi ja syvempi monikielinen ymmärrys – kaikki täysin omalla laitteistollasi.

Tässä käyttöoppaassa opit klusteroimaan kaksi Ryzen AI Halo -järjestelmää käyttäen llama.cpp:n RPC-moottoria ja ajamaan GLM 4.7:ää, 358 miljardin parametrin mallia, molemmilla koneilla AMD ROCm™ -kiihdytyksen avulla.

## Mitä opit

- Kuinka laajentaa VRAM-varausta Ryzen AI Halo -järjestelmissä
- llama.cpp:n asentaminen ROCm- ja RPC-tuella
- RPC-työntekijän määrittäminen ja hajautetun päättelyn käynnistäminen kahden noodin välillä
- 358 miljardin parametrin mallin ajaminen kahdella verkotetulla Ryzen AI Halo -järjestelmällä

## Muistiasetuksen määrittäminen

> **Huomautus**: Suorita tämä vaihe sekä koneella 1 että koneella 2.

<!-- @os:windows -->
Windowsissa suurempien mallien ajamiseksi, jotka vaativat enemmän muistia, meidän täytyy käyttää AMD Variable Graphics Memory (iGPU VRAM) -varausta.

Tämä voidaan tehdä avaamalla AMD Software: Adrenalin Edition -ohjauspaneeli ja siirtymällä kohtaan: `Performance > Tuning > AMD Variable Graphics Memory`. Aseta arvoksi **96 GB**. Käynnistä järjestelmä uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxissa ROCm käyttää jaettua järjestelmämuistin poolia, ja tämä pooli on oletusarvoisesti asetettu puoleen järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla kernelin Translation Table Manager (TTM) -sivuasetusta seuraavilla ohjeilla. AMD suosittelee asettamaan minimin dedikoidun VRAM:in BIOSissa (0,5 GB).

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

Tämä käyttöopas vaatii kaksi Ryzen AI Halo -yksikköä ja yhden Ethernet-kytkimen, jotka on kytketty tähtitopologiassa siten, että kukin yksikkö on kytketty suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Laskentanoodit, jotka muodostavat klusterin |
| 10 Gbps Ethernet-kytkin | 1 | Keskuskytkin, joka mahdollistaa usean noodin Ryzen AI Halo -viestinnän (vähintään 2 porttia) |
| Ethernet-kaapeli | 2 | Yhdistää kunkin Halo-yksikön kytkimeen (Cat 7 tai korkeampi suositeltu) |

> **Huomautus**: Kahden Ethernet-kytkimen portin tarvitaan kahden Ryzen AI Halo -yksikön yhdistämiseen. Kolmas portti vaaditaan, jos käytät mallia erillisestä asiakaskoneesta yhden Halo-yksikön sijaan.

### Ohjelmisto
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Asenna:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) ja **Desktop Development with C++** -työkuormalla
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyysisen laitteiston käyttöönotto

> **Huomautus**: Suorita tämä vaihe sekä koneella 1 että koneella 2.

Yhdistä kukin Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 (tai korkeampi) -kaapelilla. Tämä muodostaa 10 Gbps -yhteyden, jota käytetään nopeaan viestintään noodien välillä.
<!-- @os:linux -->
### 1. Verkkoliitäntöjen määrittäminen

Selvitä kummastakin koneesta sen verkkoliitännän nimi ja kirjoita se ylös (siihen viitataan jäljempänä nimellä `IFNAME`). Suorita:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tämä tulostaa liitännän nimen suoraan, esimerkiksi:

```bash
enp191s0
```

### 2. Verkkolinkin nopeuksien tarkistaminen

Varmista, että linkki on aktiivinen ja toimii täydellä nopeudella tarkistamalla liitäntäsi nopeus:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Huomautus**: Korvaa `<IFNAME>` liitännän nimellä, jonka sait kohdasta [1. Verkkoliitäntöjen määrittäminen](#1-determine-network-interfaces)

Sinun pitäisi nähdä nopeus `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomautus**: Jos nopeus on pienempi kuin `10000Mb/s` tai linkki ei nouse ylös, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps:ään. Jotkin kytkimet vaativat automaattisen neuvottelun poistamista käytöstä ja linkin nopeuden asettamista manuaalisesti; katso kytkimesi dokumentaatiota.

<!-- @os:end -->

<!-- @os:windows -->
### Verkkolinkin nopeuden tarkistaminen

Tarkista kummastakin koneesta verkkoliitäntöjesi linkkinopeus:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet-liitäntäsi pitäisi olla tilassa `Up` ja toimia nopeudella `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Huomautus**: Jos nopeus on pienempi kuin `10 Gbps` tai linkki ei nouse ylös, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps:ään. Jotkin kytkimet vaativat automaattisen neuvottelun poistamista käytöstä ja linkin nopeuden asettamista manuaalisesti; katso kytkimesi dokumentaatiota.

<!-- @os:end -->

## llama.cpp:n asentaminen

> **Huomautus**: Suorita tämä vaihe sekä koneella 1 että koneella 2.

Käytettävissä on kaksi asennusvaihtoehtoa:

- [Vaihtoehto 1: Lemonade SDK (suositeltu)](#option-1-lemonade-sdk-recommended) – valmiiksi käännetyt binäärit, nopein käyttöönotto
- [Vaihtoehto 2: Manuaalinen lähdekoodista kääntäminen](#option-2-manual-source-build) – käännä lähdekoodista täydellä hallinnalla käännöslippuihin

### Vaihtoehto 1: Lemonade SDK (suositeltu)

Lemonade SDK tarjoaa yön yli tehtyjä llama.cpp-käännöksiä AMD ROCm 7 -kiihdytyksellä, kohdistuen GPU:ihin kuten gfx1151 (Strix Halo / Ryzen AI Max+ 395) ja muihin uudempiin Radeon-arkkitehtuureihin.

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

Tämä hakemisto sisältää nyt ROCm-yhteensopivat koontiversiot tiedostoista `llama-cli.exe`, `llama-server.exe` ja `rpc-server.exe`, jotka on esikäännetty Ryzen AI Halo -järjestelmääsi varten.

#### Vaihe 3: Varmista GPU:n tunnistus

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

Tämä hakemisto sisältää nyt ROCm-yhteensopivat koontiversiot tiedostoista `llama-cli`, `llama-server` ja `rpc-server`, jotka on esikäännetty Ryzen AI Halo -järjestelmääsi varten.

#### Vaihe 3: Varmista GPU:n tunnistus

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

### Vaihtoehto 2: Manuaalinen lähdekoodikäännös

<!-- @os:windows -->
#### Vaihe 1: Käännä llama.cpp

Avaa **x64 Native Tools Command Prompt** (asennettu Visual Studio Build Toolsin mukana) ja kloonaa arkisto:

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

| Koontivalitsin | Tarkoitus |
|-----------|---------|
| `-DGGML_HIP=ON` | Ottaa käyttöön ROCm/HIP-ohjelmistopinon |
| `-DGGML_RPC=ON` | Ottaa käyttöön RPC:n hajautettua päättelyä varten |
| `-DGPU_TARGETS=gfx1151` | Kohdistaa Ryzen AI Halo -GPU:hun (Radeon 8060s) |
| `-G Ninja` | Käyttää Ninja-koontijärjestelmää |

#### Vaihe 2: Varmista GPU:n tunnistus

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

#### Vaihe 3: Lisää HIP käyttäjäkohtaiseen polkuun

Yllä oleva koontivaihe asetti `%HIP_PATH%\bin`-polun vain nykyistä istuntoa varten. Jotta HIP-kirjastot ovat käytettävissä missä tahansa päätteessä (ei vain x64 Native Tools Command Promptissa), lisää se pysyvästi käyttäjäkohtaiseen `PATH`-muuttujaan:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Kun llama.cpp on valmisteltu jokaisessa solmussa, jatka kohtaan [Mallin lataaminen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Vaihe 1: Käännä llama.cpp

Kloonaa arkisto:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Käännä ROCm- ja RPC-tuella:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Koontivalitsin | Tarkoitus |
|-----------|---------|
| `-DGGML_HIP=ON` | Ottaa käyttöön ROCm-ohjelmistopinon |
| `-DGGML_RPC=ON` | Ottaa käyttöön RPC:n hajautettua päättelyä varten |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Ottaa käyttöön rocWMMA:n parannettua Flash Attentionia varten AMD-GPU:illa |
| `-DAMDGPU_TARGETS="gfx1151"` | Kohdistaa Ryzen AI Halo -GPU:hun (Radeon 8060s) |

Lisää koontivaihtoehtoja löydät [llama.cpp:n koontidokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Vaihe 2: Varmista GPU:n tunnistus

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

Tässä ohjeessa käytetään mallia [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), joka on 358 miljardin parametrin malli `Q4_K_XL`-kvantisoinnissa lähteestä [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Tällä kvantisoinnilla malli vaatii noin 205 Gt tallennustilaa ja mahtuu kahden Ryzen AI Halo -solmun yhdistettyyn GPU-muistiin.

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

> **Huomautus**: Mallin lataus on tehtävä koneella 1 (ohjaimella). RPC-työntekijäsolmujen ei tarvitse säilyttää paikallista kopiota mallitiedostoista.

## Mallin käynnistäminen klusterissa

llama.cpp:n RPC (Remote Procedure Call) -moottorin avulla yksi llama.cpp-instanssi voi siirtää mallin kerroksia etätyöntekijöille verkon yli. Yksi kone toimii **ohjaimena** (kone 1), hoitaen tokenisoinnin, ajastuksen ja orkestroinnin. Toinen kone suorittaa kevyttä **RPC-palvelinta** (kone 2), joka altistaa GPU-muistinsa ja laskentatehonsa ohjaimelle.

Latausvaiheessa llama.cpp jakaa mallin molempien solmujen kesken. Kun malli on ladattu, päättely etenee ikään kuin se toimisi yhdellä kiihdyttimellä. RPC hoitaa tensorien siirrot ja synkronoinnin taustalla.

### Vaihe 1: Käynnistä RPC-palvelin (kone 2)

Käynnistä koneella 2 RPC-palvelin, joka altistaa sen GPU-resurssit ohjaimelle:
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

| Valitsin | Tarkoitus |
|------|---------|
| `-p` | Portti, jossa RPC-palvelinta lähetetään |
| `-c` | Ottaa käyttöön paikallisen välimuistin suurille tensoreille, mikä välttää toistuvat verkkosiirrot mallin latauksen aikana |
| `--host` | IP-osoite, johon RPC-palvelin sidotaan (`0.0.0.0` kaikille rajapinnoille) |

Lisää vaihtoehtoja löydät [llama.cpp:n RPC-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Vaihe 2: Käynnistä malli (kone 1)

Kun RPC-palvelin on käynnissä koneella 2, käynnistä päättely koneelta 1 käyttäen joko `llama-cli`- tai `llama-server`-työkalua.

#### llama-cli

`llama-cli` tarjoaa pääteperustaisen käyttöliittymän, jonka avulla voit olla suoraan vuorovaikutuksessa mallin kanssa. Se sopii erinomaisesti suorituskyvyn testaukseen, virheenkorjaukseen ja matalan tason kokeiluihin.

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

> **`<RPC_WORKER_IP>`-osoitteen löytäminen**: Suorita koneella 2 komento `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus**: Suorita tämä komento Terminal (Powershell) -ohjelmassa.

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>`-osoitteen löytäminen**: Suorita koneella 2 komento `ipconfig | findstr /C:"IPv4"` Terminal (Powershell) -ohjelmassa löytääksesi sen paikallisen IP-osoitteen.

<!-- @os:end -->

Kun malli on käynnissä, `llama-cli` näyttää mallin latauksen edistymisen ja avaa interaktiivisen kehotteen, jossa voit keskustella suoraan mallin kanssa:

![llama-cli suorittamassa GLM 4.7 -mallia kahdella solmulla](assets/llama-cli-example.png)
#### llama-server

`llama-server` tarjoaa saman päättelymoottorin pysyvän palvelinprosessin kautta, jossa on integroitu verkkokäyttöliittymä ja OpenAI-yhteensopiva HTTP-API. Tämä on suositeltu käyttöliittymä pidempikestoisiin käyttöönottoihin, usean käyttäjän käyttöön ja ulkoisten työkalujen integrointiin.

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

> **`<RPC_WORKER_IP>`-osoitteen löytäminen**: Aja koneella 2 komento `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

<!-- @os:windows -->
> **Huom**: Aja tämä komento Terminal (Powershell) -sovelluksessa.

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

> **`<RPC_WORKER_IP>`-osoitteen löytäminen**: Aja koneella 2 komento `ipconfig | findstr /C:"IPv4"` Terminal (Powershell) -sovelluksessa löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

Kun palvelin on käynnistynyt, avaa selaimessasi osoite `http://<HOST_IP>:8081` päästäksesi sisäänrakennettuun verkkokäyttöliittymään. Tämä tarjoaa selainpohjaisen keskusteluliittymän mallin kanssa keskustelemiseen:

![llama-server-verkkokäyttöliittymä käynnissä GLM 4.7 -mallilla kahdella solmulla](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>`-osoitteen löytäminen**: Aja koneella 1 komento `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>`-osoitteen löytäminen**: Aja koneella 1 komento `ipconfig | findstr /C:"IPv4"` Terminal (Powershell) -sovelluksessa löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

#### Parametriviittaus

| Lippu | Tarkoitus |
|------|---------|
| `-m` | Polku GGUF-mallitiedostoon (käytä ensimmäistä osaa, `00001-of-00005`) |
| `-c` | Kontekstin koko tokeneina. Suuremmat arvot käyttävät enemmän muistia |
| `-fa on` | Ottaa käyttöön rocWMMA Flash Attentionin, joka parantaa suorituskykyä AMD-näytönohjaimilla |
| `-ngl 999` | Siirtää kaikki mallin kerrokset GPU:lle |
| `--no-mmap` | Poistaa käytöstä muistiin kartoituksen, mikä lyhentää latausaikoja, kun mallin koko ylittää järjestelmän RAM-muistin mutta mahtuu VRAM-muistiin |
| `--host` | IP-osoite, johon `llama-server` sidotaan (vain `llama-server`) |
| `--port` | Portti, jossa HTTP-API tarjotaan (vain `llama-server`) |
| `--rpc` | Pilkuilla eroteltu luettelo RPC-työntekijöiden päätepisteistä (`IP:portti`) |

Täydelliset parametrien käyttöohjeet löydät [llama-cli-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) ja [llama-server-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Seuraavat vaiheet

- **Yhdistä kolmannen osapuolen sovelluksia**: `llama-server` tarjoaa OpenAI-yhteensopivan API:n. Osoita mikä tahansa OpenAI-yhteensopiva sovellus (kuten Open WebUI) osoitteeseen `http://<HOST_IP>:8081` käyttäen mitä tahansa paikkamerkki-API-avainta (esim. `none`) yhdistääksesi klusteriisi
- **Tutustu muihin malleihin**: Selaa kvantisoituja GGUF-malleja [Hugging Facessa](https://huggingface.co/models?search=gguf) löytääksesi malleja, jotka mahtuvat klusterisi yhdistettyyn GPU-muistiin
- **Skaalaa neljään solmuun**: Lisää kaksi Ryzen AI Halo -järjestelmää lisää RPC-työntekijöiksi päästäksesi käsiksi biljoonan parametrin kokoluokan malleihin. Anna lisää päätepisteitä `--rpc`-parametrille pilkuilla eroteltuna luettelona (esim. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)