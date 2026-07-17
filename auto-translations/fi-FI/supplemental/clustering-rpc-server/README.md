<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Kahden Ryzen™ AI Halon klusterointi RPC:llä

## Yleiskatsaus

Ryzen™ AI Halo pystyy jo nyt ajamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän pidemmälle yhdistämällä useiden järjestelmien GPU-muistin paikallisverkon yli, jolloin käytettävissäsi on entistä suurempia malleja, joilla on parempi päättelykyky, laadukkaampi koodintuotanto ja syvempi monikielinen ymmärrys – kaikki täysin omalla laitteistollasi.

Tässä playbook-oppaassa opit klusteroimaan kaksi Ryzen AI Halo -järjestelmää llama.cpp:n RPC-moottorin avulla ja ajamaan GLM 4.7:n, 358 miljardin parametrin mallin, molemmilla koneilla AMD ROCm™-kiihdytyksen avulla.

## Mitä opit

- Kuinka laajentaa VRAM-allokointia Ryzen AI Halo -järjestelmissä
- llama.cpp:n asentaminen ROCm- ja RPC-tuella
- RPC-työntekijän konfigurointi ja hajautetun inferenssin käynnistäminen kahden solmun välillä
- 358 miljardin parametrin mallin ajaminen kahdella verkotetuilla Ryzen AI Halo -järjestelmällä

## Muistikonfiguraation asettaminen

> **Huomio**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

<!-- @os:windows -->
Windowsissa suurempien mallien ajaminen, jotka vaativat enemmän muistia, edellyttää AMD Variable Graphics Memory (iGPU VRAM) -allokoinnin käyttöä.

Tämä onnistuu avaamalla AMD Software: Adrenalin Edition -ohjauspaneeli ja siirtymällä kohtaan: `Performance > Tuning > AMD Variable Graphics Memory`. Aseta arvoksi **96 GB**. Käynnistä järjestelmä uudelleen muutosten voimaantuloa varten.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxissa ROCm käyttää jaettua järjestelmämuistipoolia, joka on oletuksena konfiguroitu puoleen järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla ytimen Translation Table Manager (TTM) -sivuasetusta seuraavien ohjeiden mukaisesti. AMD suosittelee asettamaan BIOS:ssa minimidedikoidun VRAM:n (0,5 GB).

* Asenna pipx-apuohjelma ja lisää pipx:n asentamien pakettien polku järjestelmän hakupolkuun.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Asenna amd-debug-tools-paketti PyPI:stä.
  ```bash
  pipx install amd-debug-tools
  ```

* Aja amd-ttm-työkalu kysyäksesi jaetun muistin nykyiset asetukset.
  ```bash
  amd-ttm
  ```

* Konfiguroi jaetun muistin asetukset uudelleen arvoon **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Käynnistä järjestelmä uudelleen muutosten voimaantuloa varten.


<!-- @os:end -->
<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->
## Edellytykset

### Laitteisto

Tämä playbook-opas vaatii kaksi Ryzen AI Halo -yksikköä ja yhden Ethernet-kytkimen, jotka on kytketty tähtitopologiassa siten, että kukin yksikkö on johdotettu suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Laskentasolmut, jotka muodostavat klusterin |
| 10 Gbps:n Ethernet-kytkin | 1 | Keskuskytkin usean solmun Ryzen AI Halo -viestintää varten (vähintään 2 porttia) |
| Ethernet-kaapeli | 2 | Yhdistää jokaisen Halo-yksikön kytkimeen (Cat 7 tai parempi suositellaan) |

> **Huomio**: Kahden Ryzen AI Halo -yksikön yhdistämiseen tarvitaan kaksi Ethernet-kytkimen porttia. Kolmas portti tarvitaan, jos käytät mallia erilliseltä asiakaskoneelta yhden Halo-yksikön sijaan.

### Ohjelmisto
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Asenna seuraavat:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) **Desktop Development with C++** -työmäärällä
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyysinen laitteistokokoonpano

> **Huomio**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

Kytke jokainen Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 (tai parempi) -kaapelilla. Tämä muodostaa 10 Gbps:n yhteyden, jota käytetään solmujen väliseen nopeaan viestintään.
<!-- @os:linux -->
### 1. Määritä verkkoliitännät

Etsi jokaisella koneella sen verkkoliitännän nimi ja kirjaa se muistiin (siihen viitataan alla nimellä `IFNAME`). Aja:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tämä tulostaa liitännän nimen suoraan, esimerkiksi:

```bash
enp191s0
```

### 2. Tarkista verkkoyhteyden nopeudet

Vahvista, että yhteys on aktiivinen ja toimii täydellä nopeudella tarkistamalla liitäntäsi nopeus:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Huomio**: Korvaa `<IFNAME>` kohdasta [1. Määritä verkkoliitännät](#1-determine-network-interfaces) saadulla liitännän nimellä.

Sinun pitäisi nähdä nopeus `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomio**: Jos nopeus on alle `10000Mb/s` tai yhteys ei muodostu, tarkista kaapeliyhteys ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Joissakin kytkimissä automaattinen neuvottelu täytyy poistaa käytöstä ja linkin nopeus asettaa manuaalisesti; katso kytkimesi dokumentaatiota.

<!-- @os:end -->

<!-- @os:windows -->
### Tarkista verkkoyhteyden nopeus

Tarkista jokaisella koneella verkkoliitäntöjesi linkin nopeus:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet-liitäntäsi pitäisi olla `Up` ja toimia nopeudella `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Huomio**: Jos nopeus on alle `10 Gbps` tai yhteys ei muodostu, tarkista kaapeliyhteys ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Joissakin kytkimissä automaattinen neuvottelu täytyy poistaa käytöstä ja linkin nopeus asettaa manuaalisesti; katso kytkimesi dokumentaatiota.

<!-- @os:end -->

## llama.cpp:n asentaminen

> **Huomio**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

Käytettävissä on kaksi asennusvaihtoehtoa:

- [Vaihtoehto 1: Lemonade SDK (suositellaan)](#option-1-lemonade-sdk-recommended) – valmiiksi käännetyt binäärit, nopein asennus
- [Vaihtoehto 2: Manuaalinen lähdekoodikäännös](#option-2-manual-source-build) – käännä lähdekoodista täydellä hallinnalla käännöslipuista

### Vaihtoehto 1: Lemonade SDK (suositellaan)

Lemonade SDK tarjoaa llama.cpp:n yörakennukset AMD ROCm 7 -kiihdytyksellä, kohdistuen GPU:ihin kuten gfx1151 (Strix Halo / Ryzen AI Max+ 395) ja muihin uusiin Radeon-arkkitehtuureihin.

<!-- @os:windows -->
#### Vaihe 1: Lataa valmiiksi käännetyt binäärit

Siirry uusimmalle julkaisusivulle ja lataa alustasi ja GPU-kohteesi mukainen arkisto:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (jossa `xxxx` on rakennusnumero).

#### Vaihe 2: Pura binäärit

Pura ladattu arkisto:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tämä hakemisto sisältää nyt ROCm-yhteensopivat käännökset tiedostoista `llama-cli.exe`, `llama-server.exe` ja `rpc-server.exe`, esikoottuna Ryzen AI Halo -järjestelmällesi.

#### Vaihe 3: Tarkista GPU:n tunnistus

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

Siirry uusimmalle julkaisusivulle ja lataa alustasi ja GPU-kohteesi mukainen arkisto:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (jossa `xxxx` on rakennusnumero).

#### Vaihe 2: Pura ja valmistele binäärit

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Tämä hakemisto sisältää nyt ROCm-yhteensopivat käännökset tiedostoista `llama-cli`, `llama-server` ja `rpc-server`, esikoottuna Ryzen AI Halo -järjestelmällesi.

#### Vaihe 3: Tarkista GPU:n tunnistus

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
Kun llama.cpp on valmisteltu jokaisella solmulla, siirry kohtaan [Mallin lataaminen](#downloading-the-model).

### Vaihtoehto 2: Manuaalinen lähdekoodikäännös

<!-- @os:windows -->
#### Vaihe 1: Käännä llama.cpp

Avaa **x64 Native Tools Command Prompt** (asennettu Visual Studio Build Toolsin mukana) ja kloonaa repositorio:

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
| `-DGGML_RPC=ON` | Ottaa käyttöön RPC:n hajautettua inferenssiä varten |
| `-DGPU_TARGETS=gfx1151` | Kohdistuu Ryzen AI Halo GPU:hun (Radeon 8060s) |
| `-G Ninja` | Käyttää Ninja-rakennusjärjestelmää |

#### Vaihe 2: Tarkista GPU:n tunnistus

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

Yllä oleva käännösvaihe asetti `%HIP_PATH%\bin` vain nykyiselle istunnolle. Jotta HIP-kirjastot olisivat käytettävissä missä tahansa terminaalissa (ei vain x64 Native Tools Command Promptissa), lisää se pysyvästi käyttäjän `PATH`-muuttujaan:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Kun llama.cpp on valmisteltu jokaisella solmulla, siirry kohtaan [Mallin lataaminen](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Vaihe 1: Käännä llama.cpp

Kloonaa repositorio:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Käännä ROCm- ja RPC-tuella:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Käännöslippu | Tarkoitus |
|-----------|---------|
| `-DGGML_HIP=ON` | Ottaa käyttöön ROCm-ohjelmistopinon |
| `-DGGML_RPC=ON` | Ottaa käyttöön RPC:n hajautettua inferenssiä varten |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Ottaa käyttöön rocWMMA:n parannetun Flash Attentionin AMD GPU:ille |
| `-DAMDGPU_TARGETS="gfx1151"` | Kohdistuu Ryzen AI Halo GPU:hun (Radeon 8060s) |

Lisää käännösvaihtoehtoja löydät [llama.cpp:n käännösdokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Vaihe 2: Tarkista GPU:n tunnistus

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

Kun llama.cpp on valmisteltu jokaisella solmulla, siirry kohtaan [Mallin lataaminen](#downloading-the-model).
<!-- @os:end -->

## Mallin lataaminen

Tässä playbook-oppaassa käytetään [GLM 4.7:ää](https://huggingface.co/zai-org/GLM-4.7), 358 miljardin parametrin mallia `Q4_K_XL`-kvantisoinnilla [Unslothilta](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Tässä kvantisoinnissa malli vaatii noin 205 GB tallennustilaa ja mahtuu kahden Ryzen AI Halo -solmun yhdistettyyn GPU-muistiin.

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

> **Huomio**: Mallin lataus täytyy suorittaa Koneella 1 (ohjain). RPC-työntekijäsolmut eivät tarvitse paikallista kopiota mallitiedostoista.

## Mallin käynnistäminen klusterissa

llama.cpp:n RPC (Remote Procedure Call) -moottori mahdollistaa sen, että yksittäinen llama.cpp-instanssi voi siirtää mallikerroksia etätyöntekijöille verkon yli. Yksi kone toimii **ohjaimena** (Kone 1) hoitaen tokenoinnin, ajoituksen ja orkestroinnin. Toinen kone ajaa kevyttä **RPC-palvelinta** (Kone 2), joka tarjoaa GPU-muistinsa ja laskentatehonsa ohjaimen käyttöön.

Latausvaiheessa llama.cpp jakaa mallin molempien solmujen kesken. Kun malli on ladattu, inferenssi etenee kuin se ajaisi yhdellä kiihdyttimellä. RPC hoitaa tensorisiirrot ja synkronoinnin taustalla.

### Vaihe 1: Käynnistä RPC-palvelin (Kone 2)

Käynnistä Koneella 2 RPC-palvelin tarjotaksesi sen GPU-resurssit ohjaimen käyttöön:
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
| `-p` | Portti, johon RPC-palvelin lähettää |
| `-c` | Ottaa käyttöön paikallisen välimuistin suurille tensoreille, välttäen toistuvat verkkosiirrot mallin latauksen aikana |
| `--host` | IP-osoite, johon RPC-palvelin sidotaan (`0.0.0.0` kaikille liitännöille) |

Lisää vaihtoehtoja löydät [llama.cpp:n RPC-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Vaihe 2: Käynnistä malli (Kone 1)

Kun RPC-palvelin on käynnissä Koneella 2, käynnistä inferenssi Koneelta 1 käyttäen joko `llama-cli`:tä tai `llama-server`:iä.

#### llama-cli

`llama-cli` tarjoaa terminaalipohjaisen käyttöliittymän mallin kanssa suoraan vuorovaikuttamiseen. Se sopii erinomaisesti vertailutestaukseen, virheenkorjaukseen ja matalan tason kokeiluihin.

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

> **`<RPC_WORKER_IP>`:n löytäminen**: Aja Koneella 2 `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomio**: Aja tämä komento Terminalissa (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>`:n löytäminen**: Aja Koneella 2 `ipconfig | findstr /C:"IPv4"` Terminalissa (Powershell) löytääksesi sen paikallisen IP-osoitteen.

<!-- @os:end -->

Kun `llama-cli` on käynnissä, se näyttää mallin latauksen edistymisen ja siirtyy interaktiiviseen kehotteeseen, jossa voit jutella suoraan mallin kanssa:

![llama-cli ajaa GLM 4.7:ää kahden solmun välillä](assets/llama-cli-example.png)

#### llama-server

`llama-server` tarjoaa saman inferenssimoottorin pysyvän palveluprosessin kautta, jossa on integroitu web-käyttöliittymä ja OpenAI-yhteensopiva HTTP-rajapinta. Tämä on suositeltava käyttöliittymä pitkäkestoisempiin käyttöönottoihin, usean käyttäjän käyttöön ja integraatioon ulkoisten työkalujen kanssa.

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

> **`<RPC_WORKER_IP>`:n löytäminen**: Aja Koneella 2 `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomio**: Aja tämä komento Terminalissa (Powershell).

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

> **`<RPC_WORKER_IP>`:n löytäminen**: Aja Koneella 2 `ipconfig | findstr /C:"IPv4"` Terminalissa (Powershell) löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

Kun palvelin on käynnistynyt, avaa `http://<HOST_IP>:8081` selaimessasi päästäksesi sisäänrakennettuun web-käyttöliittymään. Tämä tarjoaa selainpohjaisen chat-käyttöliittymän mallin kanssa vuorovaikuttamiseen:

![llama-server web-käyttöliittymä ajaa GLM 4.7:ää kahden solmun välillä](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>`:n löytäminen**: Aja Koneella 1 `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>`:n löytäminen**: Aja Koneella 1 `ipconfig | findstr /C:"IPv4"` Terminalissa (Powershell) löytääksesi sen paikallisen IP-osoitteen.
<!-- @os:end -->

#### Parametriviite

| Lippu | Tarkoitus |
|------|---------|
| `-m` | Polku GGUF-mallitiedostoon (käytä ensimmäistä sirpaletta, `00001-of-00005`) |
| `-c` | Kontekstin koko tokeneina. Suuremmat arvot käyttävät enemmän muistia |
| `-fa on` | Ottaa käyttöön rocWMMA Flash Attentionin parantaakseen suorituskykyä AMD GPU:illa |
| `-ngl 999` | Siirtää kaikki mallikerrokset GPU:lle |
| `--no-mmap` | Poistaa muistikuvauksen käytöstä, lyhentäen latausaikoja kun mallin koko ylittää järjestelmämuistin mutta mahtuu VRAM:iin |
| `--host` | IP, johon `llama-server` sidotaan (vain `llama-server`) |
| `--port` | Portti, jossa HTTP-rajapintaa tarjotaan (vain `llama-server`) |
| `--rpc` | Pilkuilla erotettu lista RPC-työntekijöiden päätepisteistä (`IP:portti`) |

Täydellinen parametrien käyttö löytyy [llama-cli-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) ja [llama-server-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Seuraavat vaiheet

- **Yhdistä kolmannen osapuolen sovellukset**: `llama-server` tarjoaa OpenAI-yhteensopivan rajapinnan. Osoita mikä tahansa OpenAI-yhteensopiva sovellus (kuten Open WebUI) osoitteeseen `http://<HOST_IP>:8081` millä tahansa paikkamerkki-API-avaimella (esim. `none`) yhdistääksesi klusteriisi
- **Tutustu muihin malleihin**: Selaa kvantisoituja GGUF-malleja [Hugging Facessa](https://huggingface.co/models?search=gguf) löytääksesi malleja, jotka mahtuvat klusterisi yhdistettyyn GPU-muistiin
- **Skaalaa neljään solmuun**: Lisää kaksi Ryzen AI Halo -järjestelmää lisäisinä RPC-työntekijöinä päästäksesi käsiksi biljoonan parametrin kokoluokan malleihin. Välitä lisäpäätepisteet `--rpc`-lipulle pilkuilla erotettuna listana (esim. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)