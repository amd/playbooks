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

# Neljän Ryzen™ AI Halo -järjestelmän klusterointi RPC:n avulla

## Yleiskatsaus

Ryzen™ AI Halo -järjestelmäsi pystyy jo ajamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän pidemmälle yhdistämällä useiden järjestelmien GPU-muistin paikallisverkon kautta, jolloin käytössäsi on vielä suurempia malleja, joilla on vahvempi päättelykyky, parempi koodin generointi ja syvempi monikielinen ymmärrys – täysin omalla laitteistollasi.

Tämä opas opettaa, miten voit klusteroida neljä Ryzen AI Halo -järjestelmää käyttäen llama.cpp:n RPC-moottoria ja ajaa Kimi K2.6:ta, suurta mixture-of-experts-mallia, kaikilla neljällä koneella AMD ROCm™ -kiihdytyksen avulla.

## Mitä opit

- Miten laajentaa VRAM-allokointia Ryzen AI Halo -järjestelmissä
- llama.cpp:n asentaminen ROCm- ja RPC-tuella
- RPC-työntekijöiden määrittäminen ja hajautetun päättelyn käynnistäminen neljässä solmussa
- 1 biljoonan parametrin mallin ajaminen neljässä verkotetussa Ryzen AI Halo -järjestelmässä

## Muistiasetuksen määrittäminen

> **Huomautus**: Suorita tämä vaihe kaikilla neljällä koneella (Kone 1–Kone 4).

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Lähes 128 Gt:n tai sitä suurempien mallien ajaminen:** AMD Ryzen™ AI Max 400 -sarjan (Gorgon Halo) järjestelmissä, joissa käytetään Windowsia, mallit, jotka lähestyvät tai ylittävät 128 Gt muistia, vaativat lisämäärityksiä toimiakseen ilman virheitä. Seuraa [AMD Ryzen AI Max PRO 400 -sarjan Windows-käyttöjärjestelmän ohjeita](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) ennen mallin lataamista.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Windowsissa, jos haluat ajaa suurempia malleja, jotka vaativat enemmän muistia, meidän tulee käyttää AMD Variable Graphics Memory (iGPU VRAM) -allokointia.

Tämä voidaan tehdä avaamalla AMD Software: Adrenalin Edition -ohjauspaneeli ja siirtymällä kohtaan: `Performance > Tuning > AMD Variable Graphics Memory`. Aseta arvoksi **96 Gt**. Käynnistä järjestelmä uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxissa ROCm käyttää jaettua järjestelmämuistin poolia, ja tämä pooli on oletusarvoisesti määritetty puoleen järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla kernelin Translation Table Managerin (TTM) sivuasetusta seuraavien ohjeiden mukaisesti. AMD suosittelee asettamaan vähimmäismäärän dedikoitua VRAM-muistia BIOSissa (0,5 Gt).

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

* Määritä jaetun muistin asetukset uudelleen arvoon **120 Gt**:
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

Tämä opas edellyttää neljää Ryzen AI Halo -yksikköä ja yhtä Ethernet-kytkintä, jotka on kytketty tähtitopologiaan siten, että kukin yksikkö on kytketty suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Klusterin muodostavat laskentasolmut |
| 10 Gbps Ethernet-kytkin | 1 | Keskuskytkin, joka mahdollistaa usean solmun Ryzen AI Halo -viestinnän (vähintään 4 porttia) |
| Ethernet-kaapeli | 4 | Yhdistää kunkin Halo-yksikön kytkimeen (suositellaan Cat 7 tai parempaa) |

> **Huomautus**: Neljän Ethernet-kytkinportin yhdistäminen vaatii neljä Ryzen AI Halo -yksikköä. Viides portti tarvitaan, jos käytät mallia erillisestä asiakaskoneesta sen sijaan, että käyttäisit sitä jostakin Halo-yksiköstä.

### Ohjelmisto
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Asenna seuraavat:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) ja **Desktop Development with C++** -työkuorma
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fyysisen laitteiston asennus

> **Huomautus**: Suorita tämä vaihe kaikilla neljällä koneella (Kone 1–Kone 4).

Yhdistä jokainen Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 (tai parempi) -kaapelilla. Tämä muodostaa 10 Gbps -yhteyden, jota käytetään solmujen välisessä nopeassa viestinnässä.
<!-- @os:linux -->
### 1. Verkkoliitäntöjen määrittäminen

Selvitä kullakin koneella sen verkkoliitännän nimi ja kirjaa se muistiin (siihen viitataan jäljempänä nimellä `IFNAME`). Suorita:

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

> **Huomautus**: Korvaa `<IFNAME>` lähtöliitännän nimellä kohdasta [1. Verkkoliitäntöjen määrittäminen](#1-determine-network-interfaces)

Sinun pitäisi nähdä nopeus `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomautus**: Jos nopeus on alhaisempi kuin `10000Mb/s` tai yhteys ei muodostu, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps -nopeuteen. Jotkin kytkimet vaativat, että automaattinen neuvottelu poistetaan käytöstä ja yhteysnopeus asetetaan manuaalisesti; katso lisätietoja kytkimesi dokumentaatiosta.

<!-- @os:end -->

<!-- @os:windows -->
### Verkkoyhteyden nopeuden tarkistaminen

Tarkista kunkin koneen verkkoliitäntöjen yhteysnopeus:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet-liitäntäsi pitäisi olla tilassa `Up` ja toimia nopeudella `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Huomautus**: Jos nopeus on alhaisempi kuin `10 Gbps` tai yhteys ei muodostu, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps -nopeuteen. Jotkin kytkimet vaativat, että automaattinen neuvottelu poistetaan käytöstä ja yhteysnopeus asetetaan manuaalisesti; katso lisätietoja kytkimesi dokumentaatiosta.

<!-- @os:end -->

## llama.cpp:n asentaminen

> **Huomautus**: Suorita tämä vaihe kaikilla neljällä koneella (Kone 1–Kone 4).

Käytettävissä on kaksi asennusvaihtoehtoa:

- [Vaihtoehto 1: Lemonade SDK (suositeltu)](#option-1-lemonade-sdk-recommended) – valmiiksi käännetyt binäärit, nopein tapa
- [Vaihtoehto 2: Manuaalinen lähdekoodista kääntäminen](#option-2-manual-source-build) – käännä lähdekoodista täydellä hallinnalla käännöslippujen suhteen
### Vaihtoehto 1: Lemonade SDK (suositeltu)

Lemonade SDK tarjoaa öisin päivittyviä llama.cpp-käännöksiä AMD ROCm 7 -kiihdytyksellä, kohdistettuna GPU-malleihin kuten gfx1151 (Strix Halo / Ryzen AI Max+ 395) sekä muihin uusiin Radeon-arkkitehtuureihin.

<!-- @os:windows -->
#### Vaihe 1: Lataa esikäännetyt binäärit

Siirry uusimman julkaisun sivulle ja lataa alustaasi ja GPU-kohdettasi vastaava arkisto:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (jossa `xxxx` on käännösnumero).

#### Vaihe 2: Pura binäärit

Pura ladattu arkisto:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Tämä hakemisto sisältää nyt ROCm-tuetut käännökset tiedostoista `llama-cli.exe`, `llama-server.exe` ja `ggml-rpc-server.exe`, esikäännettynä Ryzen AI Halo -järjestelmällesi.

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
#### Vaihe 1: Lataa esikäännetyt binäärit

Siirry uusimman julkaisun sivulle ja lataa alustaasi ja GPU-kohdettasi vastaava arkisto:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Lataa tiedosto nimeltä `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (jossa `xxxx` on käännösnumero).

#### Vaihe 2: Pura ja valmistele binäärit

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Tämä hakemisto sisältää nyt ROCm-tuetut käännökset tiedostoista `llama-cli`, `llama-server` ja `rpc-server`, esikäännettynä Ryzen AI Halo -järjestelmällesi.

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

### Vaihtoehto 2: Manuaalinen lähdekoodista kääntäminen

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

#### Vaihe 3: Lisää HIP käyttäjäpolkuusi

Yllä oleva käännösvaihe asetti `%HIP_PATH%\bin`-polun vain nykyistä istuntoa varten. Jotta HIP-kirjastot olisivat käytettävissä missä tahansa päätteessä (ei vain x64 Native Tools Command Promptissa), lisää se pysyvästi käyttäjäsi `PATH`-muuttujaan:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Kun llama.cpp on valmisteltu jokaisessa solmussa, jatka kohtaan [Mallin lataaminen](#downloading-the-model).
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
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Käännöslippu | Tarkoitus |
|-----------|---------|
| `-DGGML_HIP=ON` | Ottaa käyttöön ROCm-ohjelmistopinon |
| `-DGGML_RPC=ON` | Ottaa käyttöön RPC:n hajautettua päättelyä varten |
| `-DAMDGPU_TARGETS="gfx1151"` | Kohdistaa Ryzen AI Halo -GPU:hun (Radeon 8060s) |

Lisää käännösvaihtoehtoja löydät [llama.cpp:n käännösdokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Tämä opas käyttää mallia [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) `UD-Q2_K_XL`-kvantisoinnissa, jonka tarjoaa [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Tämä kvantisointi mahtuu neljän Ryzen AI Halo -solmun yhdistettyyn GPU-muistiin.

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

> **Huomautus**: Mallin lataaminen tulee tehdä Koneella 1 (ohjain). RPC-työntekijäsolmujen (Koneet 2, 3 ja 4) ei tarvitse sisältää paikallista kopiota mallitiedostoista.

## Mallin käynnistäminen klusterissa

llama.cpp:n RPC (Remote Procedure Call) -moottori mahdollistaa sen, että yksi llama.cpp-instanssi voi siirtää mallin kerroksia etätyöntekijöille verkon yli. Yksi kone toimii **ohjaimena** (Kone 1) ja huolehtii tokenisoinnista, aikataulutuksesta ja orkestroinnista. Kolme muuta konetta kukin suorittavat kevyttä **RPC-palvelinta** (Koneet 2, 3 ja 4), jotka tarjoavat GPU-muistinsa ja laskentatehonsa ohjaimen käyttöön.

Latauksen aikana llama.cpp jakaa mallin kaikkien neljän solmun kesken. Kun malli on ladattu, päättely etenee ikään kuin se toimisi yhdellä kiihdyttimellä. RPC huolehtii tensorien siirroista ja synkronoinnista taustalla.

### Vaihe 1: Käynnistä RPC-palvelimet (Koneet 2, 3 ja 4)

Käynnistä jokaisella koneista 2, 3 ja 4 RPC-palvelin, jotta sen GPU-resurssit tulevat ohjaimen käyttöön:
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
| `-p` | Portti, jossa RPC-palvelin julkaistaan |
| `-c` | Ottaa käyttöön paikallisen välimuistin suurille tensoreille, mikä välttää toistuvat verkkosiirrot mallin latauksen aikana |
| `--host` | IP-osoite, johon RPC-palvelin sidotaan (`0.0.0.0` kaikille liitäntöille) |

Lisätietoja löydät [llama.cpp:n RPC-dokumentaatiosta](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Vaihe 2: Käynnistä malli (Kone 1)

Kun RPC-palvelimet ovat käynnissä Koneilla 2, 3 ja 4, käynnistä päättely Koneelta 1 joko `llama-cli`- tai `llama-server`-komennolla.
#### llama-cli

`llama-cli` tarjoaa päätepohjaisen käyttöliittymän, jolla voi olla suoraan vuorovaikutuksessa mallin kanssa. Se soveltuu hyvin suorituskyvyn vertailuun, virheenjäljitykseen ja matalan tason kokeiluun.

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

> **`<RPC_WORKER_2_IP>`-, `<RPC_WORKER_3_IP>`- ja `<RPC_WORKER_4_IP>`-osoitteiden selvittäminen**: Suorita kullakin koneista 2, 3 ja 4 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomio**: Suorita tämä komento Terminalissa (Powershell).

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

> **`<RPC_WORKER_2_IP>`-, `<RPC_WORKER_3_IP>`- ja `<RPC_WORKER_4_IP>`-osoitteiden selvittäminen**: Suorita kullakin koneista 2, 3 ja 4 komento `ipconfig | findstr /C:"IPv4"` Terminalissa (Powershell) sen paikallisen IP-osoitteen selvittämiseksi.

<!-- @os:end -->

Kun `llama-cli` on käynnissä, se näyttää mallin latauksen edistymisen ja avaa interaktiivisen kehotteen, jossa voit keskustella mallin kanssa suoraan:

![llama-cli, joka suorittaa Kimi K2.6:ta neljän solmun verkossa](assets/llama-cli-example.png)

#### llama-server

`llama-server` tarjoaa saman päättelymoottorin pysyvän palvelinprosessin kautta, johon sisältyy integroitu verkkokäyttöliittymä ja OpenAI-yhteensopiva HTTP-rajapinta. Tämä on suositeltu käyttöliittymä pidempikestoisiin käyttöönottoihin, useamman käyttäjän pääsyyn ja integrointiin ulkoisten työkalujen kanssa.

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

> **`<RPC_WORKER_2_IP>`-, `<RPC_WORKER_3_IP>`- ja `<RPC_WORKER_4_IP>`-osoitteiden selvittäminen**: Suorita kullakin koneista 2, 3 ja 4 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomio**: Suorita tämä komento Terminalissa (Powershell).

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

> **`<RPC_WORKER_2_IP>`-, `<RPC_WORKER_3_IP>`- ja `<RPC_WORKER_4_IP>`-osoitteiden selvittäminen**: Suorita kullakin koneista 2, 3 ja 4 komento `ipconfig | findstr /C:"IPv4"` Terminalissa (Powershell) sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

Kun palvelin on käynnistetty, avaa selaimessasi osoite `http://<HOST_IP>:8081` käyttääksesi sisäänrakennettua verkkokäyttöliittymää. Tämä tarjoaa selainpohjaisen keskusteluliittymän mallin kanssa vuorovaikutukseen:

![llama-server-verkkokäyttöliittymä, joka suorittaa Kimi K2.6:ta neljän solmun verkossa](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>`-osoitteen selvittäminen**: Suorita koneella 1 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>`-osoitteen selvittäminen**: Suorita koneella 1 komento `ipconfig | findstr /C:"IPv4"` Terminalissa (Powershell) sen paikallisen IP-osoitteen selvittämiseksi.
<!-- @os:end -->

#### Parametriviite

| Lippu | Tarkoitus |
|------|---------|
| `-m` | Polku GGUF-mallitiedostoon (käytä ensimmäistä osaa, `00001-of-00008`) |
| `-c` | Kontekstin koko tokeneina. Suuremmat arvot käyttävät enemmän muistia |
| `-fa on` | Ottaa käyttöön rocWMMA Flash Attentionin, mikä parantaa suorituskykyä AMD-GPU:illa |
| `-ngl 999` | Siirtää kaikki mallin kerrokset GPU:lle |
| `-lm none` | Asettaa mallin latausmoodiksi `none`, mikä poistaa muistiin kartoituksen käytöstä latausaikojen lyhentämiseksi, kun mallin koko ylittää järjestelmän RAM-muistin mutta mahtuu VRAM-muistiin |
| `-b` | Looginen eräkoko tokeneina. Arvo 4096 tasapainottaa suorituskykyä ja muistin käyttöä solmujen välillä |
| `-ub` | Fyysinen (mikro) eräkoko kehotteen käsittelyä varten. Saman arvon käyttäminen kuin `-b`:lle välttää tarpeettoman pilkkomisen aiheuttaman ylikuormituksen |
| `--host` | IP-osoite, johon `llama-server` sidotaan (vain `llama-server`) |
| `--port` | Portti, jossa HTTP-rajapintaa tarjotaan (vain `llama-server`) |
| `--rpc` | Pilkuin eroteltu luettelo RPC-työntekijäpäätepisteistä (`IP:portti`) |

Täydellisen parametrikäytön osalta, katso [llama-cli-dokumentaatio](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) ja [llama-server-dokumentaatio](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Seuraavat vaiheet

- **Yhdistä kolmannen osapuolen sovelluksia**: `llama-server` tarjoaa OpenAI-yhteensopivan rajapinnan. Osoita mikä tahansa OpenAI-yhteensopiva sovellus (kuten Open WebUI) osoitteeseen `http://<HOST_IP>:8081` käyttäen mitä tahansa paikkamerkki-API-avainta (esim. `none`) yhdistääksesi klusteriisi
- **Tutustu muihin malleihin**: Selaa kvantisoituja GGUF-tiedostoja [Hugging Facessa](https://huggingface.co/models?search=gguf) löytääksesi malleja, jotka mahtuvat klusterisi yhteenlaskettuun GPU-muistiin
- **Skaalaa yli neljän solmun**: Lisää uusia Ryzen AI Halo -järjestelmiä lisätyöntekijöiksi (RPC worker) päästäksesi käsiksi malleihin, jotka ylittävät biljoonan parametrin skaalan. Välitä lisäpäätepisteet `--rpc`-lipulle pilkuin eroteltuna luettelona (esim. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)