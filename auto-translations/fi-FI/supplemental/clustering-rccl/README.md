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

# Kahden Ryzen™ AI Halo -järjestelmän klusterointi RCCL:llä

## Yleiskatsaus

Ryzen™ AI Halosi pystyy jo suorittamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän askeleen pidemmälle yhdistämällä useamman järjestelmän GPU-muistin paikallisverkon yli, jolloin pääset käsiksi entistä suurempiin malleihin, joilla on vahvempi päättelykyky, parempi koodin generointi ja syvempi monikielinen ymmärrys — kaikki täysin omalla laitteistollasi.

Tämä opas opettaa, miten klusteroit kaksi Ryzen AI Halo -järjestelmää käyttäen RCCL:ää (ROCm Communication Collectives Library) yhdessä vLLM:n kanssa, ja miten ajat Qwen3.5-397B-mallia, jossa on 397 miljardia parametria, molemmilla koneilla ROCm-kiihdytyksellä.

## Mitä opit

- Miten laajennat VRAM-muistivarauksen Ryzen AI Halo -järjestelmissä
- vLLM:n käynnistäminen ROCm-tuella
- RCCL:n määrittäminen usean solmun tensori-rinnakkaista päättelyä varten kahden Ryzen AI Halo -järjestelmän välillä
- 397 miljardin parametrin mallin ajaminen kahdella verkotetulla Ryzen AI Halo -järjestelmällä

## Vaatimukset

### Laitteisto

Tämä opas edellyttää kahta Ryzen AI Halo -yksikköä ja yhtä Ethernet-kytkintä, jotka on kytketty tähtitopologiaan siten, että kukin yksikkö on yhdistetty suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Laskentasolmut, jotka muodostavat klusterin |
| 10 Gbps Ethernet-kytkin | 1 | Keskuskytkin, joka mahdollistaa useamman solmun Ryzen AI Halo -kommunikoinnin (vähintään 2 porttia) |
| Ethernet-kaapeli | 2 | Yhdistää kunkin Halo-yksikön kytkimeen (suositellaan Cat 7 -kaapelia tai parempaa) |

> **Huomautus**: Kahden Ryzen AI Halo -yksikön yhdistämiseen tarvitaan kaksi Ethernet-kytkimen porttia. Kolmas portti tarvitaan, jos käytät mallia erillisestä asiakaskoneesta yhden Halo-yksikön sijaan.

### Ohjelmisto
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Laitteiston fyysinen käyttöönotto

> **Huomautus**: Suorita tämä vaihe sekä koneella 1 että koneella 2.

Yhdistä kukin Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 -kaapelilla (tai paremmalla). Tämä luo 10 Gbps -yhteyden, jota käytetään solmujen välisessä nopeassa kommunikoinnissa.

### 1. Verkkoliittymien määrittäminen

Selvitä kummankin koneen verkkoliittymän nimi ja kirjaa se ylös (siihen viitataan ohjeiden lopussa nimellä `IFNAME`). Suorita:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tämä tulostaa liittymän nimen suoraan, esimerkiksi:

```bash
enp191s0
```

### 2. Verkkoyhteyden nopeuksien tarkistaminen

Varmista, että yhteys on aktiivinen ja toimii täydellä nopeudella tarkistamalla liittymäsi nopeus:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Huomautus**: Korvaa `<IFNAME>` liittymän nimellä, jonka sait kohdasta [1. Verkkoliittymien määrittäminen](#1-determine-network-interfaces)

Nopeuden pitäisi olla `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomautus**: Jos nopeus on pienempi kuin `10000Mb/s` tai yhteys ei muodostu, tarkista kaapeliliitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps -nopeuteen. Joissakin kytkimissä automaattinen neuvottelu (auto-negotiation) täytyy poistaa käytöstä ja yhteysnopeus asettaa manuaalisesti; katso lisätietoja kytkimesi dokumentaatiosta.

## VRAM-muistivarauksen laajentaminen

> **Huomautus**: Suorita tämä vaihe sekä koneella 1 että koneella 2.

### Muistin määritys suurten mallien ajamista varten

Linuxissa ROCm käyttää jaettua järjestelmämuistin poolia, ja tämä pooli on oletusarvoisesti määritetty puoleen järjestelmän muistista.

Tätä määrää voidaan kasvattaa muuttamalla ytimen Translation Table Manager (TTM) -sivuasetusta seuraavien ohjeiden mukaisesti. AMD suosittelee asettamaan BIOS:ssa minimivarattu VRAM (0,5 Gt).

* Asenna pipx-työkalu ja lisää pipx:llä asennettujen wheel-pakettien polku järjestelmän hakupolkuun.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Asenna amd-debug-tools-wheel PyPI:stä.
  ```bash
  pipx install amd-debug-tools
  ```

* Suorita amd-ttm-työkalu jaetun muistin nykyisten asetusten kyselyä varten.
  ```bash
  amd-ttm
  ```

* Määritä jaetun muistin asetukset uudelleen arvoon **120 Gt**:
  ```bash
  amd-ttm --set 120
  ```

* Käynnistä järjestelmä uudelleen, jotta muutokset tulevat voimaan.

## vLLM-säiliön alustus

> **Huomautus**: Suorita tämä vaihe sekä koneella 1 että koneella 2.

Ryzen AI Halosi toimitetaan vLLM:n kanssa valmiiksi rakennetun säiliökuvan sisällä, jota ajetaan Podmanilla, ilmaisella ja avoimen lähdekoodin säiliötyökalulla.

### 1. Luo mallien latauskansio

Kun tarjoat Qwen3.5-397B-mallia tässä oppaassa, vLLM lataa mallin painot automaattisesti järjestelmääsi. Jotta nämä painot ovat saatavilla säiliön sisältä, luo ensin models-kansio, jonka säiliö voi liittää:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Käynnistä vLLM-säiliö

Alla oleva komento käynnistää säiliön ja vie sinut interaktiiviseen komentotulkkiin. Se liittää juuri luomasi models-kansion ja välittää `IFNAME`-muuttujasi `NCCL_SOCKET_IFNAME`- ja `GLOO_SOCKET_IFNAME`-muuttujiin, mikä kertoo RCCL:lle (kirjasto, jota vLLM käyttää GPU:iden koordinointiin klusterin yli) mitä liittymää käyttää.

Käynnistä säiliö komennolla:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Huomautus**: Korvaa `<IFNAME>` liittymän nimellä, jonka sait kohdasta [1. Verkkoliittymien määrittäminen](#1-determine-network-interfaces)

## Mallin ajaminen klusterissa

vLLM käyttää Ray:tä klusterin orkestrointiin ja RCCL:ää GPU:iden väliseen kommunikointiin solmujen kesken. Yksi kone toimii **päänä (head node)** (kone 1), koordinoiden päättelyä. Toinen liittyy **työsolmuna (worker node)** (kone 2), tuoden mukanaan oman GPU-muistinsa ja laskentatehonsa.

> **Huomautus**: Ray on vLLM:n valinnainen riippuvuus ja saatavilla vain valmiiksi määritetyn Podman-säiliön sisältä.

Käynnistyksen yhteydessä vLLM jakaa mallin molempien solmujen kesken tensori-rinnakkaisuutta käyttäen. Kun malli on ladattu, päättely etenee ikään kuin sitä ajettaisiin yhdellä kiihdyttimellä.

#### Ray:n muistinloppumisvirheiden (OOM) estäminen

Oletusarvoisesti Ray valvoo kunkin solmun isäntämuistia ja sulkee suurimman prosessin, kun muistinkäyttö ylittää 95 %. Ryzen™ AI Halossasi GPU ja isäntä jakavat saman muistipoolin, joten mallin lataaminen voi laukaista `ray.exceptions.OutOfMemoryError`-virheen ja sulkea työprosessin.

Tämän estämiseksi viemme `RAY_memory_monitor_refresh_ms=0`-ympäristömuuttujan kummallakin koneella ennen klusterin käynnistämistä ja siihen liittymistä.
### Vaihe 1: Ray-päänoodin käynnistäminen (Kone 1)

Käynnistä Koneella 1 Ray-päänoodi klusterin alustamiseksi:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>`:n selvittäminen**: Aja Koneella 1 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.

### Vaihe 2: Klusteriin liittyminen (Kone 2)

Yhdistä Koneella 2 päänoodiin klusterin muodostamiseksi:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>`:n selvittäminen**: Aja Koneella 2 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.

### Vaihe 3: Mallin tarjoaminen (Kone 1)

Käynnistä Koneella 1 vLLM-palvelin. Tämä lataa mallin automaattisesti ja alkaa tarjota sitä molempien noodien kautta:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Parametriviite

| Lippu | Tarkoitus |
|------|---------|
| `--port` | Portti, jossa HTTP-rajapintaa tarjotaan |
| `--host` | IP-osoite, johon palvelin sidotaan (`0.0.0.0` kaikille liitännöille) |
| `--max-model-len` | Suurin kontekstin pituus tokeneina |
| `--gpu-memory-utilization` | Osuus GPU-muistista, joka varataan (0.0–1.0) |
| `--dtype` | Mallin painojen tietotyyppi |
| `--tensor-parallel-size` | Niiden GPU:iden määrä, joiden kesken malli jaetaan (aseta klusterin GPU:iden kokonaismäärään) |
| `--distributed-executor-backend` | Taustajärjestelmä usean noodin suoritusta varten (`ray` klusterikäyttöönotoissa) |
| `--enforce-eager` | Poistaa CUDA-graafien kääntämisen käytöstä yhteensopivuuden vuoksi |
| `--language-model-only` | Ohittaa apumallikomponenttien (esim. näköenkooderin) lataamisen |
| `--reasoning-parser` | Ottaa käyttöön mallin jäsennellyn päättelytulosteen jäsentämisen |

Täydelliset parametrien käyttöohjeet löydät [vLLM-dokumentaatiosta](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Mallin käyttäminen

vLLM tarjoaa OpenAI-yhteensopivan API:n, joten voit yhdistää minkä tahansa yhteensopivan asiakasohjelman tai käyttöliittymän klusteriisi. Yksi suosittu vaihtoehto on [Open WebUI](https://github.com/open-webui/open-webui), joka tarjoaa selainpohjaisen keskusteluliittymän.

Yhdistä Open WebUI vLLM-päätepisteeseesi seuraavasti:

1. Avaa **Settings** > **Admin Panel** > **Connections**
2. Napsauta **+**-painiketta kohdassa **Manage OpenAI API Connections**
3. Aseta **Connection Type**-arvoksi **External**
4. Aseta **URL**-arvoksi `http://<MACHINE_1_IP>:7000/v1`
5. Valitse **Auth**-kohdassa pudotusvalikosta **None**
6. Jätä **Model IDs** tyhjäksi, jotta kaikki päätepisteen mallit havaitaan automaattisesti

> **`<MACHINE_1_IP>`:n selvittäminen**: Aja Koneella 1 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi. Jos käytät Open WebUI:tä itse Koneelta 1, voit käyttää osoitetta `http://localhost:7000/v1`.

![Open WebUI:n yhteysasetukset vLLM-päätepisteelle](assets/openwebui-connection.png)

Kun yhteys on muodostettu, valitse malli Open WebUI:n mallien pudotusvalikosta ja aloita keskustelu. Malli toimii nyt molempien Ryzen AI Halo -noodiesi kautta:

![Keskustelu Qwen3.5-397B:n kanssa Open WebUI:ssa](assets/openwebui-chat.png)

## Seuraavat vaiheet

- **Tutustu muihin malleihin**: Löydä uusia malleja [Hugging Facesta](https://huggingface.co/models?&sort=trending), jotka mahtuvat klusterisi yhdistettyyn GPU-muistiin
- **Laajenna neljään noodiin**: Lisää kaksi Ryzen AI Halo -järjestelmää lisää Ray-työntekijöiksi, jotta mallit voidaan jakaa vieläkin useamman GPU:n kesken. Tämä edellyttää Ethernet-kytkintä, jossa on vähintään neljä porttia, yksi jokaista noodia varten. Noudata [Vaihe 2: Klusteriin liittyminen](#step-2-join-the-cluster-machine-2) -ohjeita jokaisella lisätyöntekijällä ja kasvata `--tensor-parallel-size`-arvoa vastaavasti
- **Kokeile muita rinnakkaisuusstrategioita**: vLLM tukee [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) -toimintoa mixture-of-experts-malleille ja [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) -toimintoa suuremman läpisyötön saavuttamiseksi. Kokeile `--enable-expert-parallel`- ja `--data-parallel-size`-asetuksia löytääksesi parhaan kokoonpanon työkuormallesi