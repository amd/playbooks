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

# Neljän Ryzen™ AI Halon klusterointi RPC:llä

## Yleiskatsaus

Ryzen™ AI Halosi pystyy jo nyt ajamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän pidemmälle yhdistämällä useiden järjestelmien GPU-muistin paikallisverkon yli, mikä antaa sinulle pääsyn vielä suurempiin malleihin, joissa on vahvempi päättelykyky, parempi koodin generointi ja syvempi monikielinen ymmärrys, kaikki täysin omalla laitteistollasi.

Tämä ohjekirja opettaa, miten neljä Ryzen AI Halo -järjestelmää klusteroidaan käyttäen llama.cpp:n RPC-moottoria ja miten Kimi K2.6, suuri mixture-of-experts-malli, ajetaan kaikilla neljällä koneella AMD ROCm™ -kiihdytyksellä.

## Mitä opit

- Miten VRAM-muistin allokointia laajennetaan Ryzen AI Halo -järjestelmissä
- llama.cpp:n asentaminen ROCm- ja RPC-tuella
- RPC-työntekijöiden määrittäminen ja hajautetun päättelyn käynnistäminen neljällä solmulla
- 1T-parametrisen mallin ajaminen neljällä verkotetulla Ryzen AI Halo -järjestelmällä

## Muistiasetuksen määrittäminen

> **Huomautus**: Suorita tämä vaihe kaikilla neljällä koneella (Kone 1–Kone 4).

<!-- @os:windows -->
Windowsissa, jotta voidaan ajaa suurempia malleja, jotka vaativat enemmän muistia, meidän täytyy käyttää AMD Variable Graphics Memory (iGPU VRAM) -allokointia.

Tämä voidaan tehdä avaamalla AMD Software: Adrenalin Edition -ohjauspaneeli ja siirtymällä kohtaan: `Performance > Tuning > AMD Variable Graphics Memory`. Aseta arvoksi **96 GB**. Käynnistä järjestelmä uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxissa ROCm käyttää jaettua järjestelmämuistin allasta, ja tämä allas on oletusarvoisesti asetettu puoleen järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla ytimen Translation Table Manager (TTM) -sivuasetusta seuraavien ohjeiden mukaisesti. AMD suosittelee asettamaan minimikäytetyn VRAM:n BIOSissa (0,5 Gt).

* Asenna pipx-työkalu ja lisää pipx:n asentamien wheel-pakettien polku järjestelmän hakupolkuun.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Asenna amd-debug-tools-wheel PyPI:stä.
  ```bash
  pipx install amd-debug-tools
  ```

* Aja amd-ttm-työkalu kysyäksesi jaetun muistin nykyiset asetukset.
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

Tämä ohjekirja vaatii neljä Ryzen AI Halo -yksikköä ja yhden Ethernet-kytkimen, jotka on kytketty tähtitopologiaan siten, että kukin yksikkö on kytketty suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Laskentasolmut, jotka muodostavat klusterin |
| 10 Gbps Ethernet-kytkin | 1 | Keskuskytkin, joka mahdollistaa Ryzen AI Halojen välisen usean solmun viestinnän (vähintään 4 porttia) |
| Ethernet-kaapeli | 4 | Yhdistää kunkin Halo-yksikön kytkimeen (suositellaan Cat 7 tai parempaa) |

> **Huomautus**: Neljän Ethernet-kytkimen portin tarvitaan neljän Ryzen AI Halo -yksikön yhdistämiseen. Viides portti tarvitaan, jos käytät mallia erillisestä asiakaskoneesta yhden Halo-yksikön sijaan.

### Ohjelmisto
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Asenna:
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

> **Huomautus**: Suorita tämä vaihe kaikilla neljällä koneella (Kone 1–Kone 4).

Yhdistä jokainen Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 (tai parempaa) -kaapelilla. Tämä muodostaa 10 Gbps -yhteyden, jota käytetään solmujen väliseen nopeaan viestintään.
<!-- @os:linux -->
### 1. Määritä verkkoliittymät

Selvitä kunkin koneen verkkoliittymän nimi ja kirjaa se muistiin (siihen viitataan jäljempänä nimellä `IFNAME`). Aja:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tämä tulostaa liittymän nimen suoraan, esimerkiksi:

```bash
enp191s0
```

### 2. Vahvista verkkoyhteyksien nopeudet

Vahvista, että yhteys on aktiivinen ja toimii täydellä nopeudella tarkistamalla liittymäsi nopeus:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Huomautus**: Korvaa `<IFNAME>` lähtöliittymän nimellä kohdasta [1. Määritä verkkoliittymät](#1-determine-network-interfaces)

Nopeuden pitäisi näyttää `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomautus**: Jos nopeus on alhaisempi kuin `10000Mb/s` tai yhteyttä ei muodostu, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Jotkin kytkimet vaativat automaattisen neuvottelun poistamista käytöstä ja yhteysnopeuden asettamista manuaalisesti; katso kytkimesi dokumentaatiosta lisätietoja.

<!-- @os:end -->

<!-- @os:windows -->
### Vahvista verkkoyhteyden nopeus

Tarkista kunkin koneen verkkoliittymien yhteysnopeus:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet-liittymäsi pitäisi olla tilassa `Up` ja toimia nopeudella `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Huomautus**: Jos nopeus on alhaisempi kuin `10 Gbps` tai yhteyttä ei muodostu, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Jotkin kytkimet vaativat automaattisen neuvottelun poistamista käytöstä ja yhteysnopeuden asettamista manuaalisesti; katso kytkimesi dokumentaatiosta lisätietoja.

<!-- @os:end -->

## llama.cpp:n asentaminen

> **Huomautus**: Suorita tämä vaihe kaikilla neljällä koneella (Kone 1–Kone 4).

Käytettävissä on kaksi asennusvaihtoehtoa:

- [Vaihtoehto 1: Lemonade SDK (suositeltu)](#option-1-lemonade-sdk-recommended) - valmiiksi käännetyt binaarit, nopein käyttöönotto
- [Vaihtoehto 2: Manuaalinen lähdekoodista kääntäminen](#option-2-manual-source-build) - käännä lähdekoodista täydellä hallinnalla käännösasetuksiin

### Vaihtoehto 1: Lemonade SDK (suositeltu)

Lemonade SDK tarjoaa öisin päivitettäviä llama.cpp-käännöksiä AMD ROCm 7 -kiihdytyksellä, kohdistaen GPU:ihin kuten gfx1151 (Strix Halo / Ryzen AI Max+ 395) ja muihin uudempiin Radeon-arkkitehtuureihin.

<!-- @os:windows -->
#### Vaihe 1: Lataa valmiiksi käännetyt binaaritiedostot

Siirry uusimman julkaisun sivulle ja lataa arkisto, joka vastaa alustaasi ja GPU-kohdettasi:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (jossa `xxxx` on käännösnumero).

#### Vaihe 2: Pura binaaritiedostot

Pura ladattu arkisto:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tämä hakemisto sisältää nyt ROCm-tuetut käännökset tiedostoista `llama-cli.exe`, `llama-server.exe` ja `ggml-rpc-server.exe`, jotka on käännetty valmiiksi Ryzen AI Halo -järjestelmällesi.

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
#### Vaihe 1: Lataa valmiiksi käännetyt binaaritiedostot

Siirry uusimman julkaisun sivulle ja lataa arkisto, joka vastaa alustaasi ja GPU-kohdettasi:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (jossa `xxxx` on käännösnumero).

#### Vaihe 2: Pura ja valmistele binaaritiedostot

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Tämä hakemisto sisältää nyt ROCm-tuetut käännökset tiedostoista `llama-cli`, `llama-server` ja `rpc-server`, jotka on käännetty valmiiksi Ryzen AI Halo -järjestelmällesi.

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

### Vaihtoehto 2: Manuaalinen lähdekoodikäännös

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
| `-DGPU_TARGETS=gfx1151` | Kohdistaa Ryzen AI Halo GPU:hun (Radeon 8060s) |
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

Yllä oleva käännösvaihe asetti `%HIP_PATH%\bin`-polun vain nykyistä istuntoa varten. Jotta HIP-kirjastot olisivat käytettävissä missä tahansa päätteessä (ei vain x64 Native Tools Command Promptissa), lisää se pysyvästi käyttäjäsi `PATH`-muuttujaan:

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
| `-DAMDGPU_TARGETS="gfx1151"` | Kohdistaa Ryzen AI Halo GPU:hun (Radeon 8060s) |

Lisää käännösasetuksia löydät osoitteesta [llama.cpp-käännösdokumentaatio](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Tämä käyttöopas käyttää mallia [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) `UD-Q2_K_XL`-kvantisoinnilla, jonka on toimittanut [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Tämä kvantisointi mahtuu neljän Ryzen AI Halo -solmun yhdistettyyn GPU-muistiin.

Lataa GGUF-tiedostot Hugging Face CLI:n avulla:
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

> **Huomautus**: Mallin lataus on suoritettava koneella 1 (ohjaimella). RPC-työntekijäsolmujen (koneet 2, 3 ja 4) ei tarvitse sisältää paikallista kopiota mallitiedostoista.

## Mallin käynnistäminen klusterissa

Llama.cpp:n RPC-moottori (Remote Procedure Call) mahdollistaa sen, että yksi llama.cpp-instanssi voi siirtää mallin kerroksia etätyöntekijöille verkon yli. Yksi kone toimii **ohjaimena** (kone 1), hoitaen tokenisoinnin, ajastuksen ja orkestroinnin. Kolme muuta konetta ajavat kukin kevyttä **RPC-palvelinta** (koneet 2, 3 ja 4), jotka altistavat GPU-muistinsa ja laskentatehonsa ohjaimelle.

Latausvaiheessa llama.cpp jakaa mallin kaikkien neljän solmun kesken. Kun malli on ladattu, päättely etenee kuin ajettaisiin yhdellä kiihdyttimellä. RPC hoitaa tensorien siirrot ja synkronoinnin taustalla.

### Vaihe 1: Käynnistä RPC-palvelimet (koneet 2, 3 ja 4)

Käynnistä jokaisella koneista 2, 3 ja 4 RPC-palvelin, joka altistaa sen GPU-resurssit ohjaimelle:
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
| `-p` | Portti, jolla RPC-palvelin lähettää |
| `-c` | Ottaa käyttöön paikallisen välimuistin suurille tensoreille, mikä välttää toistuvia verkkosiirtoja mallin latauksen aikana |
| `--host` | IP-osoite, johon RPC-palvelin sidotaan (`0.0.0.0` kaikille rajapinnoille) |

Lisätietoja löydät osoitteesta [llama.cpp:n RPC-dokumentaatio](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Vaihe 2: Käynnistä malli (kone 1)

Kun RPC-palvelimet ovat käynnissä koneilla 2, 3 ja 4, käynnistä päättely koneelta 1 käyttäen joko `llama-cli`- tai `llama-server`-työkalua.
#### llama-cli

`llama-cli` tarjoaa pääteliittymän, jonka avulla voit olla suoraan yhteydessä malliin. Se sopii erinomaisesti vertailutestaukseen, virheenkorjaukseen ja matalan tason kokeiluihin.

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

> **`<RPC_WORKER_2_IP>`-, `<RPC_WORKER_3_IP>`- ja `<RPC_WORKER_4_IP>`-osoitteiden selvittäminen**: Suorita kullakin koneella 2, 3 ja 4 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus**: Suorita tämä komento Terminaalissa (Powershell).

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

> **`<RPC_WORKER_2_IP>`-, `<RPC_WORKER_3_IP>`- ja `<RPC_WORKER_4_IP>`-osoitteiden selvittäminen**: Suorita kullakin koneella 2, 3 ja 4 komento `ipconfig | findstr /C:"IPv4"` Terminaalissa (Powershell) sen paikallisen IP-osoitteen selvittämiseksi.

<!-- @os:end -->

Kun `llama-cli` on käynnissä, se näyttää mallin latauksen edistymisen ja avaa interaktiivisen kehotteen, jossa voit keskustella suoraan mallin kanssa:

![llama-cli käynnissä Kimi K2.6:lla neljässä solmussa](assets/llama-cli-example.png)

#### llama-server

`llama-server` tarjoaa saman päättelymoottorin pysyvän palvelinprosessin kautta, johon sisältyy integroitu web-käyttöliittymä sekä OpenAI-yhteensopiva HTTP-rajapinta. Tämä on suositeltu ratkaisu pidempikestoisiin käyttöönottoihin, useiden käyttäjien käyttöön sekä integrointiin ulkoisten työkalujen kanssa.

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

> **`<RPC_WORKER_2_IP>`-, `<RPC_WORKER_3_IP>`- ja `<RPC_WORKER_4_IP>`-osoitteiden selvittäminen**: Suorita kullakin koneella 2, 3 ja 4 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus**: Suorita tämä komento Terminaalissa (Powershell).

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

> **`<RPC_WORKER_2_IP>`-, `<RPC_WORKER_3_IP>`- ja `<RPC_WORKER_4_IP>`-osoitteiden selvittäminen**: Suorita kullakin koneella 2, 3 ja 4 komento `ipconfig | findstr /C:"IPv4"` Terminaalissa (Powershell) sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

Kun palvelu on käynnistetty, avaa selaimessasi osoite `http://<HOST_IP>:8081` päästäksesi käsiksi sisäänrakennettuun web-käyttöliittymään. Se tarjoaa selainpohjaisen keskusteluliittymän mallin kanssa vuorovaikutukseen:

![llama-server-web-käyttöliittymä käynnissä Kimi K2.6:lla neljässä solmussa](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>`-osoitteen selvittäminen**: Suorita koneella 1 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>`-osoitteen selvittäminen**: Suorita koneella 1 komento `ipconfig | findstr /C:"IPv4"` Terminaalissa (Powershell) sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

#### Parametriviite

| Lippu | Tarkoitus |
|------|---------|
| `-m` | Polku GGUF-mallitiedostoon (käytä ensimmäistä osaa, `00001-of-00008`) |
| `-c` | Kontekstin koko tokeneina. Suuremmat arvot käyttävät enemmän muistia |
| `-fa on` | Ottaa käyttöön rocWMMA Flash Attention -toiminnon suorituskyvyn parantamiseksi AMD-näytönohjaimilla |
| `-ngl 999` | Siirtää kaikki mallin kerrokset GPU:lle |
| `-lm none` | Asettaa mallin lataustilaksi `none`, mikä poistaa käytöstä muistiin kuvauksen (memory-mapping) latausaikojen lyhentämiseksi silloin, kun mallin koko ylittää järjestelmän RAM-muistin mutta mahtuu VRAM-muistiin |
| `-b` | Looginen eräkoko tokeneina. Arvo 4096 tasapainottaa suorituskyvyn ja muistinkäytön solmujen välillä |
| `-ub` | Fyysinen (mikro)eräkoko kehotteen käsittelyä varten. Arvon täsmääminen `-b`-arvon kanssa välttää tarpeettoman pilkkomisen aiheuttaman ylikuormituksen |
| `--host` | IP-osoite, johon `llama-server` sidotaan (vain `llama-server`) |
| `--port` | Portti, jossa HTTP-rajapintaa tarjoillaan (vain `llama-server`) |
| `--rpc` | Pilkuin eroteltu luettelo RPC-työntekijöiden päätepisteistä (`IP:portti`) |

Täydelliset parametritiedot löydät [llama-cli-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) ja [llama-server-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Seuraavat vaiheet

- **Yhdistä kolmannen osapuolen sovelluksia**: `llama-server` tarjoaa OpenAI-yhteensopivan rajapinnan. Osoita mikä tahansa OpenAI-yhteensopiva sovellus (kuten Open WebUI) osoitteeseen `http://<HOST_IP>:8081` käyttäen mitä tahansa paikkamerkki-API-avainta (esim. `none`) yhdistääksesi klusteriisi
- **Tutustu muihin malleihin**: Selaa kvantisoituja GGUF-tiedostoja [Hugging Facessa](https://huggingface.co/models?search=gguf) löytääksesi malleja, jotka mahtuvat klusterisi yhdistettyyn GPU-muistiin
- **Laajenna yli neljän solmun**: Lisää muita Ryzen AI Halo -järjestelmiä ylimääräisinä RPC-työntekijöinä päästäksesi käsiksi yli biljoonan parametrin kokoisiin malleihin. Anna lisäpäätepisteet `--rpc`-parametrille pilkuin eroteltuna luettelona (esim. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)