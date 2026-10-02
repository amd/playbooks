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

# Neljän Ryzen™ AI Halo -järjestelmän klusterointi RCCL:llä

## Yleiskatsaus

Ryzen™ AI Halo -järjestelmäsi pystyy jo nyt ajamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän pidemmälle yhdistämällä useamman järjestelmän GPU-muistin paikallisverkon yli, jolloin pääset käsiksi vielä suurempiin malleihin, joilla on vahvempi päättelykyky, parempi koodin generointi ja syvempi monikielinen ymmärrys – täysin omalla laitteistollasi.

Tämä opas opettaa sinulle, kuinka klusteroida neljä Ryzen AI Halo -järjestelmää RCCL:llä (ROCm Communication Collectives Library) vLLM:n kanssa ja ajaa Qwen3.5-397B-mallia, jossa on 397 miljardia parametria, kaikilla neljällä koneella ROCm-kiihdytyksellä.

## Mitä opit

- Kuinka laajentaa VRAM-allokointia Ryzen AI Halo -järjestelmissä
- vLLM:n käynnistäminen ROCm-tuella
- RCCL:n määrittäminen monen solmun tensor-rinnakkaista päättelyä varten neljällä Ryzen AI Halo -järjestelmällä
- 397 miljardin parametrin mallin ajaminen neljällä verkotetulla Ryzen AI Halo -järjestelmällä

## Edellytykset

### Laitteisto

Tämä opas edellyttää neljää Ryzen AI Halo -yksikköä ja yhtä Ethernet-kytkintä, jotka on kytketty tähtitopologiaan siten, että jokainen yksikkö on kytketty suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Klusterin muodostavat laskentasolmut |
| 10 Gbps Ethernet-kytkin | 1 | Keskitetty kytkin, joka mahdollistaa usean solmun Ryzen AI Halo -viestinnän (vähintään 4 porttia) |
| Ethernet-kaapeli | 4 | Yhdistää kunkin Halo-yksikön kytkimeen (Cat 7 tai korkeampi suositeltava) |

> **Huomautus**: Neljän Ethernet-kytkimen portin käyttö vaaditaan neljän Ryzen AI Halo -yksikön yhdistämiseksi. Viides portti vaaditaan, jos käytät mallia erillisestä asiakaskoneesta yhden Halo-yksikön sijaan.

### Ohjelmisto
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Laitteiston fyysinen asennus

> **Huomautus**: Suorita tämä vaihe kaikilla neljällä koneella (Kone 1–Kone 4).

Yhdistä jokainen Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 (tai korkeamman) kaapelilla. Tämä muodostaa 10 Gbps -yhteyden, jota käytetään nopeaan solmujen väliseen viestintään.

### 1. Verkkoliitäntöjen määrittäminen

Selvitä kullakin koneella sen verkkoliitännän nimi ja merkitse se muistiin (siihen viitataan ohjeiden lopussa nimellä `IFNAME`). Suorita:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tämä tulostaa liitännän nimen suoraan, esimerkiksi:

```bash
enp191s0
```

### 2. Verkkoyhteyden nopeuksien vahvistaminen

Varmista, että yhteys on aktiivinen ja toimii täydellä nopeudella tarkistamalla liitäntäsi nopeus:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Huomautus**: Korvaa `<IFNAME>` liitännän nimellä kohdasta [1. Verkkoliitäntöjen määrittäminen](#1-determine-network-interfaces)

Nopeuden tulisi olla `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomautus**: Jos nopeus on alhaisempi kuin `10000Mb/s` tai yhteys ei muodostu, tarkista kaapelikytkentä ja varmista, että kytkimen portti on asetettu 10 Gbps -nopeuteen. Jotkin kytkimet edellyttävät automaattisen neuvottelun poistamista käytöstä ja yhteysnopeuden asettamista manuaalisesti; katso lisätietoja kytkimesi dokumentaatiosta.

## VRAM-allokoinnin laajentaminen

> **Huomautus**: Suorita tämä vaihe kaikilla neljällä koneella (Kone 1–Kone 4).

### Muistin määrittäminen suurten mallien ajamista varten

Linuxissa ROCm käyttää jaettua järjestelmämuistipoolia, ja tämä pooli on oletusarvoisesti asetettu puoleen järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla ytimen Translation Table Manager (TTM) -sivuasetusta seuraavien ohjeiden mukaisesti. AMD suosittelee asettamaan vähimmäismäärän omistettua VRAM-muistia BIOSissa (0,5 GB).

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

## vLLM-säiliön alustus

> **Huomautus**: Suorita tämä vaihe kaikilla neljällä koneella (Kone 1–Kone 4).

Ryzen AI Halo -järjestelmäsi tulee mukana vLLM:n kanssa valmiiksi rakennetussa säiliökuvassa, jota ajat Podmanilla, ilmaisella avoimen lähdekoodin säiliötyökalulla.

### 1. Luo mallin latauskansio

Kun palvelet Qwen3.5-397B-mallia tässä oppaassa, vLLM lataa mallin painot automaattisesti järjestelmääsi. Jotta nämä painot ovat käytettävissä säiliön sisältä, luo ensin models-kansio, jonka säiliö voi liittää:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Käynnistä vLLM-säiliö

Alla oleva komento käynnistää säiliön ja vie sinut interaktiiviseen komentokehotteeseen. Se liittää juuri luomasi models-kansion ja välittää `IFNAME`-arvosi muuttujille `NCCL_SOCKET_IFNAME` ja `GLOO_SOCKET_IFNAME`, kertoen RCCL:lle (kirjasto, jota vLLM käyttää GPU:iden koordinointiin klusterin yli) mitä liitäntää käyttää.

Käynnistä säiliö komennolla:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Huomautus**: Korvaa `<IFNAME>` liitännän nimellä kohdasta [1. Verkkoliitäntöjen määrittäminen](#1-determine-network-interfaces)

## Mallin ajaminen klusterissa

vLLM käyttää Ray:tä klusterin orkestrointiin ja RCCL:ää GPU-GPU-viestinnän käsittelyyn solmujen välillä. Yksi kone toimii päätysolmuna (Kone 1) ja koordinoi päättelyä. Kolme muuta liittyvät työläissolmuina (Koneet 2, 3 ja 4), tuoden mukanaan oman GPU-muistinsa ja laskentatehonsa.

> **Huomautus**: Ray on valinnainen vLLM:n riippuvuus, ja se on saatavilla vain valmiiksi määritetyn Podman-säiliön sisältä.

Käynnistyksen yhteydessä vLLM jakaa mallin kaikkien neljän solmun kesken tensor-rinnakkaisuutta käyttäen. Kun malli on ladattu, päättely etenee ikään kuin se ajettaisiin yhdellä kiihdyttimellä.

#### Ray-muistin loppumisvirheiden (OOM) estäminen

Oletusarvoisesti Ray tarkkailee isäntäkoneen muistinkäyttöä jokaisessa solmussa ja lopettaa suurimman prosessin, kun muistinkäyttö ylittää 95 %. Ryzen™ AI Halo -järjestelmässäsi GPU ja isäntäkone jakavat yhden muistipoolin, joten mallin lataaminen voi laukaista `ray.exceptions.OutOfMemoryError`-virheen ja lopettaa työläisprosessin.

Tämän estämiseksi viemme (export) `RAY_memory_monitor_refresh_ms=0` jokaisella koneella ennen klusterin käynnistämistä ja siihen liittymistä.
### Vaihe 1: Käynnistä Ray-päänoodi (Kone 1)

Käynnistä Koneella 1 Ray-päänoodi klusterin alustamiseksi:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>`:n selvittäminen**: Suorita Koneella 1 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.

### Vaihe 2: Liity klusteriin (Koneet 2, 3 ja 4)

Yhdistä kullakin Koneista 2, 3 ja 4 päänoodiin klusterin muodostamiseksi:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **`<MACHINE_N_IP>`:n selvittäminen**: Suorita kullakin työntekijäkoneella komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.

### Vaihe 3: Tarjoa mallia (Kone 1)

Käynnistä Koneella 1 vLLM-palvelin. Tämä lataa mallin automaattisesti ja alkaa tarjota sitä kaikilla neljällä noodilla:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.8 \
  --dtype float16 \
  --tensor-parallel-size 4 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Parametriviite

| Lippu | Tarkoitus |
|------|---------|
| `--port` | Portti, jolla HTTP API:a tarjotaan |
| `--host` | IP-osoite, johon palvelin sidotaan (`0.0.0.0` kaikille rajapinnoille) |
| `--max-model-len` | Suurin konteksin pituus merkkijonoina (tokeneina) |
| `--gpu-memory-utilization` | GPU-muistin varattava osuus (0,0–1,0) |
| `--dtype` | Mallin painojen tietotyyppi |
| `--tensor-parallel-size` | GPU-yksiköiden määrä, joiden kesken malli jaetaan (asetetaan klusterin GPU-yksiköiden kokonaismäärään) |
| `--distributed-executor-backend` | Taustajärjestelmä monisolmuiselle suoritukselle (`ray` klusteriasennuksille) |
| `--enforce-eager` | Poistaa CUDA-graafien kääntämisen käytöstä yhteensopivuuden vuoksi |
| `--language-model-only` | Ohittaa apukomponenttien (esim. näköenkooderin) lataamisen |
| `--reasoning-parser` | Ottaa käyttöön mallin jäsennellyn päättelytulosteen jäsentämisen |

Katso täydelliset parametrien käyttöohjeet [vLLM-dokumentaatiosta](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Mallin käyttäminen

vLLM tarjoaa OpenAI-yhteensopivan API:n, joten voit yhdistää minkä tahansa yhteensopivan asiakasohjelman tai käyttöliittymän klusteriisi. Yksi suosittu vaihtoehto on [Open WebUI](https://github.com/open-webui/open-webui), joka tarjoaa selainpohjaisen chat-käyttöliittymän.

Yhdistä Open WebUI vLLM-päätepisteeseesi seuraavasti:

1. Avaa **Settings** > **Admin Panel** > **Connections**
2. Napsauta **+**-painiketta kohdassa **Manage OpenAI API Connections**
3. Aseta **Connection Type** -asetukseksi **External**
4. Aseta **URL**-arvoksi `http://<MACHINE_1_IP>:7000/v1`
5. Valitse **Auth**-kohdassa pudotusvalikosta **None**
6. Jätä **Model IDs** tyhjäksi, jotta kaikki mallit löydetään automaattisesti päätepisteestä

> **`<MACHINE_1_IP>`:n selvittäminen**: Suorita Koneella 1 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi. Jos käytät Open WebUI:ta itse Koneelta 1, voit käyttää osoitetta `http://localhost:7000/v1`.

![Open WebUI -yhteysasetukset vLLM-päätepisteelle](assets/openwebui-connection.png)

Kun yhteys on muodostettu, valitse malli Open WebUI:n mallien pudotusvalikosta ja aloita keskustelu. Malli toimii nyt kaikilla neljällä Ryzen AI Halo -noodillasi:

![Keskustelu mallin Qwen3.5-397B kanssa Open WebUI:ssa](assets/openwebui-chat.png)

## Seuraavat vaiheet

- **Tutustu muihin malleihin**: Löydä uusia malleja [Hugging Facesta](https://huggingface.co/models?&sort=trending), jotka mahtuvat klusterisi yhdistettyyn GPU-muistiin
- **Laajenna yli neljän noodin**: Lisää lisää Ryzen AI Halo -järjestelmiä Ray-työntekijöinä, jotta mallit voidaan jakaa yhä useammalle GPU:lle. Seuraa kohtaa [Vaihe 2: Liity klusteriin](#step-2-join-the-cluster-machines-2-3-and-4) jokaisella lisätyöntekijällä ja kasvata `--tensor-parallel-size`-arvoa vastaavasti
- **Kokeile muita rinnakkaisuusstrategioita**: vLLM tukee [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) -toimintoa mixture-of-experts-malleille ja [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) -toimintoa suuremman läpisyötön saavuttamiseksi. Kokeile asetuksia `--enable-expert-parallel` ja `--data-parallel-size` löytääksesi parhaan kokoonpanon työkuormallesi