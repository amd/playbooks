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

Ryzen™ AI Halo -järjestelmäsi pystyy jo nyt ajamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän pidemmälle yhdistämällä useamman järjestelmän GPU-muistin paikallisverkon kautta, mikä antaa pääsyn vieläkin suurempiin malleihin, joissa on vahvempi päättelykyky, parempi koodin generointi ja syvempi monikielinen ymmärrys – täysin omalla laitteistollasi.

Tämä opas opettaa, miten kaksi Ryzen AI Halo -järjestelmää klusteroidaan käyttäen llama.cpp:n RPC-moottoria, ja miten GLM 4.7, 358 miljardin parametrin malli, ajetaan molemmilla koneilla AMD ROCm™ -kiihdytyksellä.

## Mitä opit

- Kuinka laajentaa VRAM-allokointia Ryzen AI Halo -järjestelmissä
- llama.cpp:n asentaminen ROCm- ja RPC-tuella
- RPC-työntekijän määrittäminen ja hajautetun päättelyn käynnistäminen kahdessa solmussa
- 358 miljardin parametrin mallin ajaminen kahdessa verkotetussa Ryzen AI Halo -järjestelmässä

## Muistiasetuksen määrittäminen

> **Huomautus**: Tee tämä vaihe sekä Koneella 1 että Koneella 2.

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Lähes 128 Gt:n tai sitä suurempien mallien ajaminen:** AMD Ryzen™ AI Max 400 Series (Gorgon Halo) -järjestelmissä, joissa käytetään Windowsia, lähes 128 Gt:n muistia vaativat tai sen ylittävät mallit vaativat lisämäärityksiä toimiakseen virheettömästi. Noudata [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) -ohjeita ennen mallin lataamista.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Windowsissa, jotta voidaan ajaa suurempia malleja, jotka vaativat enemmän muistia, meidän tulee käyttää AMD Variable Graphics Memory (iGPU VRAM) -allokointia.

Tämä onnistuu avaamalla AMD Software: Adrenalin Edition -ohjauspaneeli ja siirtymällä kohtaan: `Performance > Tuning > AMD Variable Graphics Memory`. Aseta arvoksi **96 GB**. Käynnistä järjestelmä uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxissa ROCm käyttää jaettua järjestelmämuistin muistivarantoa, ja tämä varanto on oletusarvoisesti asetettu puoleen järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla kernelin Translation Table Manager (TTM) -sivuasetusta seuraavien ohjeiden mukaisesti. AMD suosittelee asettamaan vähimmäismäärän omistettua VRAM-muistia BIOSissa (0,5 Gt).

* Asenna pipx-työkalu ja lisää pipx:n asentamien wheel-pakettien polku järjestelmän hakupolkuun.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Asenna amd-debug-tools-wheel PyPI:stä.
  ```bash
  pipx install amd-debug-tools
  ```

* Suorita amd-ttm-työkalu, jotta näet jaetun muistin nykyiset asetukset.
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
## Edellytykset

### Laitteisto

Tämä opas edellyttää kahta Ryzen AI Halo -yksikköä ja yhtä Ethernet-kytkintä, jotka on kytketty tähtitopologiaan siten, että kumpikin yksikkö on kytketty suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Laskentasolmut, jotka muodostavat klusterin |
| 10 Gbps Ethernet-kytkin | 1 | Keskuskytkin, joka mahdollistaa usean solmun Ryzen AI Halo -tiedonsiirron (vähintään 2 porttia) |
| Ethernet-kaapeli | 2 | Yhdistää kunkin Halo-yksikön kytkimeen (Cat 7 tai korkeampi suositeltu) |

> **Huomautus**: Kahden Ryzen AI Halo -yksikön yhdistämiseen tarvitaan kaksi Ethernet-kytkimen porttia. Kolmas portti tarvitaan, jos käytät mallia erillisestä asiakaskoneesta yhden Halo-yksikön sijaan.

### Ohjelmisto
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Asenna:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) sisältäen **Desktop Development with C++** -työkuorman
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyysisen laitteiston asennus

> **Huomautus**: Tee tämä vaihe sekä Koneella 1 että Koneella 2.

Yhdistä jokainen Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 (tai korkeamman) kaapelilla. Tämä muodostaa 10 Gbps -yhteyden, jota käytetään nopeaan tiedonsiirtoon solmujen välillä.
<!-- @os:linux -->
### 1. Verkkoliitäntöjen määrittäminen

Selvitä kummallakin koneella sen verkkoliitännän nimi ja kirjaa se muistiin (siihen viitataan jäljempänä nimellä `IFNAME`). Suorita:

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

> **Huomautus**: Korvaa `<IFNAME>` kohdasta [1. Verkkoliitäntöjen määrittäminen](#1-determine-network-interfaces) saadulla liitännän nimellä

Nopeuden tulisi olla `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomautus**: Jos nopeus on alle `10000Mb/s` tai yhteys ei muodostu, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps -nopeuteen. Jotkin kytkimet vaativat automaattisen neuvottelun poistamisen käytöstä ja yhteysnopeuden asettamisen manuaalisesti; katso lisätietoja kytkimesi dokumentaatiosta.

<!-- @os:end -->

<!-- @os:windows -->
### Verkkoyhteyden nopeuden tarkistaminen

Tarkista kummallakin koneella verkkoliitäntöjesi yhteysnopeus:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet-liitäntäsi tulisi olla tilassa `Up` ja toimia nopeudella `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Huomautus**: Jos nopeus on alle `10 Gbps` tai yhteys ei muodostu, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps -nopeuteen. Jotkin kytkimet vaativat automaattisen neuvottelun poistamisen käytöstä ja yhteysnopeuden asettamisen manuaalisesti; katso lisätietoja kytkimesi dokumentaatiosta.

<!-- @os:end -->

## llama.cpp:n asentaminen

> **Huomautus**: Tee tämä vaihe sekä Koneella 1 että Koneella 2.

Käytettävissä on kaksi asennusvaihtoehtoa:

- [Vaihtoehto 1: Lemonade SDK (suositeltu)](#option-1-lemonade-sdk-recommended) – valmiiksi käännetyt binäärit, nopein tapa asentaa
- [Vaihtoehto 2: Manuaalinen lähdekoodista kääntäminen](#option-2-manual-source-build) – käännä lähdekoodista täydellä hallinnalla käännöslippuihin
### Vaihtoehto 1: Lemonade SDK (suositeltu)

Lemonade SDK tarjoaa yön yli koostettuja (nightly) llama.cpp-käännöksiä AMD ROCm 7 -kiihdytyksellä, kohdistettuna GPU-arkkitehtuureihin kuten gfx1151 (Strix Halo / Ryzen AI Max+ 395) ja muihin uudempiin Radeon-arkkitehtuureihin.

<!-- @os:windows -->
#### Vaihe 1: Lataa valmiiksi käännetyt binaaritiedostot

Siirry uusimman julkaisun sivulle ja lataa alustaasi ja GPU-kohteeseesi sopiva arkisto:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (jossa `xxxx` on käännösnumero).

#### Vaihe 2: Pura binaaritiedostot

Pura ladattu arkisto:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tämä hakemisto sisältää nyt ROCm-tuetut käännökset tiedostoista `llama-cli.exe`, `llama-server.exe` ja `rpc-server.exe`, esikäännettyinä Ryzen AI Halo -järjestelmääsi varten.

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
#### Vaihe 1: Lataa valmiiksi käännetyt binaaritiedostot

Siirry uusimman julkaisun sivulle ja lataa alustaasi ja GPU-kohteeseesi sopiva arkisto:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (jossa `xxxx` on käännösnumero).

#### Vaihe 2: Pura ja valmistele binaaritiedostot

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Tämä hakemisto sisältää nyt ROCm-tuetut käännökset tiedostoista `llama-cli`, `llama-server` ja `rpc-server`, esikäännettyinä Ryzen AI Halo -järjestelmääsi varten.

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
Kun llama.cpp on valmisteltu kussakin solmussa, jatka kohtaan [Mallin lataaminen](#downloading-the-model).

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
| `-DGPU_TARGETS=gfx1151` | Kohdistaa Ryzen AI Halo -GPU:hun (Radeon 8060s) |
| `-G Ninja` | Käyttää Ninja-käännösjärjestelmää |

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

Yllä oleva käännösvaihe asetti `%HIP_PATH%\bin`-polun vain nykyistä istuntoa varten. Jotta HIP-kirjastot olisivat käytettävissä missä tahansa päätteessä (ei vain x64 Native Tools Command Promptissa), lisää se pysyvästi käyttäjäsi `PATH`-muuttujaan:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Kun llama.cpp on valmisteltu kussakin solmussa, jatka kohtaan [Mallin lataaminen](#downloading-the-model).
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
| `-DAMDGPU_TARGETS="gfx1151"` | Kohdistaa Ryzen AI Halo -GPU:hun (Radeon 8060s) |

Lisää käännösvalintoja löydät [llama.cpp-käännösdokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Kun llama.cpp on valmisteltu kussakin solmussa, jatka kohtaan [Mallin lataaminen](#downloading-the-model).
<!-- @os:end -->

## Mallin lataaminen

Tässä toimintaohjeessa käytetään mallia [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), 358 miljardin parametrin mallia `Q4_K_XL`-kvantisoinnilla, joka on peräisin [Unslothilta](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Tällä kvantisoinnilla malli vaatii noin 205 Gt tallennustilaa ja mahtuu kahden Ryzen AI Halo -solmun yhdistettyyn GPU-muistiin.

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

> **Huomautus**: Mallin lataaminen on tehtävä koneella 1 (ohjain). RPC-työsolmujen ei tarvitse säilyttää paikallista kopiota mallitiedostoista.

## Mallin käynnistäminen klusterissa

Llama.cpp:n RPC (Remote Procedure Call) -moottori mahdollistaa sen, että yksittäinen llama.cpp-instanssi voi siirtää mallin kerroksia etätyösolmuille verkon yli. Yksi kone toimii **ohjaimena** (kone 1), hoitaen tokenisoinnin, aikataulutuksen ja orkestroinnin. Toinen kone suorittaa kevyttä **RPC-palvelinta** (kone 2), joka tarjoaa GPU-muistinsa ja laskentatehonsa ohjaimen käyttöön.

Latauksen aikana llama.cpp jakaa mallin molempien solmujen kesken osiin. Kun malli on ladattu, päättely etenee kuin se toimisi yhdellä kiihdyttimellä. RPC hoitaa tensorien siirron ja synkronoinnin taustalla.

### Vaihe 1: Käynnistä RPC-palvelin (kone 2)

Käynnistä koneella 2 RPC-palvelin, jotta sen GPU-resurssit saadaan ohjaimen käyttöön:
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
| `-p` | Portti, jossa RPC-palvelinta kuunnellaan |
| `-c` | Ottaa käyttöön paikallisen välimuistin suurille tensoreille, välttäen toistuvia verkkosiirtoja mallin latauksen aikana |
| `--host` | IP-osoite, johon RPC-palvelin sidotaan (`0.0.0.0` kaikille liitännöille) |

Lisätietoja löydät [llama.cpp:n RPC-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Vaihe 2: Käynnistä malli (kone 1)

Kun RPC-palvelin on käynnissä koneella 2, käynnistä päättely koneelta 1 joko `llama-cli`- tai `llama-server`-komennolla.
#### llama-cli

`llama-cli` tarjoaa päätepohjaisen käyttöliittymän, jonka avulla voit olla suoraan vuorovaikutuksessa mallin kanssa. Se soveltuu erinomaisesti suorituskyvyn vertailuun, virheenjäljitykseen ja matalan tason kokeiluun.

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

> **Kohteen `<RPC_WORKER_IP>` selvittäminen**: Suorita Koneella 2 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus**: Suorita tämä komento Terminal-sovelluksessa (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Kohteen `<RPC_WORKER_IP>` selvittäminen**: Suorita Koneella 2 komento `ipconfig | findstr /C:"IPv4"` Terminal-sovelluksessa (Powershell) sen paikallisen IP-osoitteen selvittämiseksi.

<!-- @os:end -->

Kun ohjelma on käynnissä, `llama-cli` näyttää mallin latauksen edistymisen ja avaa interaktiivisen kehotteen, jossa voit keskustella suoraan mallin kanssa:

![llama-cli käynnissä GLM 4.7:llä kahden solmun verkossa](assets/llama-cli-example.png)

#### llama-server

`llama-server` tarjoaa saman päättelymoottorin pysyvän palvelinprosessin kautta, johon sisältyy integroitu verkkokäyttöliittymä ja OpenAI-yhteensopiva HTTP-API. Tämä on suositeltu käyttöliittymä pidempään käynnissä oleville käyttöönotoille, useiden käyttäjien pääsylle ja integroinnille ulkoisten työkalujen kanssa.

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

> **Kohteen `<RPC_WORKER_IP>` selvittäminen**: Suorita Koneella 2 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus**: Suorita tämä komento Terminal-sovelluksessa (Powershell).

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

> **Kohteen `<RPC_WORKER_IP>` selvittäminen**: Suorita Koneella 2 komento `ipconfig | findstr /C:"IPv4"` Terminal-sovelluksessa (Powershell) sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

Kun palvelin on käynnistetty, avaa `http://<HOST_IP>:8081` selaimessasi päästäksesi sisäänrakennettuun verkkokäyttöliittymään. Tämä tarjoaa selainpohjaisen chat-käyttöliittymän mallin kanssa keskustelua varten:

![llama-server-verkkokäyttöliittymä käynnissä GLM 4.7:llä kahden solmun verkossa](assets/llama-server-example.png)

<!-- @os:linux -->
> **Kohteen `<HOST_IP>` selvittäminen**: Suorita Koneella 1 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

<!-- @os:windows -->
> **Kohteen `<HOST_IP>` selvittäminen**: Suorita Koneella 1 komento `ipconfig | findstr /C:"IPv4"` Terminal-sovelluksessa (Powershell) sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

#### Parametriviite

| Lippu | Tarkoitus |
|------|---------|
| `-m` | Polku GGUF-mallitiedostoon (käytä ensimmäistä osaa, `00001-of-00005`) |
| `-c` | Kontekstin koko tokeneina. Suuremmat arvot käyttävät enemmän muistia |
| `-fa on` | Ottaa käyttöön rocWMMA Flash Attentionin suorituskyvyn parantamiseksi AMD-näytönohjaimilla |
| `-ngl 999` | Siirtää kaikki mallin kerrokset GPU:lle |
| `-lm none` | Asettaa mallin latausmoodiksi `none`, mikä poistaa muistikartoituksen käytöstä latausaikojen lyhentämiseksi, kun mallin koko ylittää järjestelmän RAM-muistin mutta mahtuu VRAM-muistiin |
| `--host` | IP-osoite, johon `llama-server` sidotaan (vain `llama-server`) |
| `--port` | Portti, jossa HTTP-API tarjoillaan (vain `llama-server`) |
| `--rpc` | Pilkuin eroteltu luettelo RPC-työntekijäpäätepisteistä (`IP:port`) |

Täydelliset tiedot parametrien käytöstä löydät [llama-cli-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) ja [llama-server-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Seuraavat vaiheet

- **Yhdistä kolmannen osapuolen sovelluksia**: `llama-server` tarjoaa OpenAI-yhteensopivan API:n. Osoita mikä tahansa OpenAI-yhteensopiva sovellus (kuten Open WebUI) osoitteeseen `http://<HOST_IP>:8081` käyttäen mitä tahansa paikkamerkki-API-avainta (esim. `none`) yhdistääksesi klusteriisi
- **Tutustu muihin malleihin**: Selaa kvantisoituja GGUF-tiedostoja [Hugging Facessa](https://huggingface.co/models?search=gguf) löytääksesi malleja, jotka mahtuvat klusterisi yhdistettyyn GPU-muistiin
- **Skaalaa neljään solmuun**: Lisää kaksi muuta Ryzen AI Halo -järjestelmää lisä-RPC-työntekijöiksi päästäksesi käsiksi malleihin, joiden koko on jopa biljoona parametria. Anna lisäpäätepisteet `--rpc`-parametrille pilkuin eroteltuna luettelona (esim. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)