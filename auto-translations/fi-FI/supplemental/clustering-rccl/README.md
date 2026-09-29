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

Ryzen™ AI Halo -järjestelmäsi pystyy jo suorittamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän askeleen pidemmälle yhdistämällä useiden järjestelmien GPU-muistin paikallisverkon yli, jolloin pääset käsiksi vieläkin suurempiin malleihin, joilla on vahvempi päättelykyky, parempi koodin generointi ja syvempi monikielinen ymmärrys – täysin omalla laitteistollasi.

Tämä opas opastaa, miten klusteroit kaksi Ryzen AI Halo -järjestelmää käyttäen RCCL:ää (ROCm Communication Collectives Library) yhdessä vLLM:n kanssa ja suoritat Qwen3.5-397B-mallin, joka on 397 miljardin parametrin malli, molemmilla koneilla ROCm-kiihdytyksellä.

## Mitä opit

- Kuinka laajentaa VRAM-muistin allokointia Ryzen AI Halo -järjestelmissä
- vLLM:n käynnistäminen ROCm-tuella
- RCCL:n konfigurointi monisolmuiseen tensori-rinnakkaiseen päättelyyn kahden Ryzen AI Halo -järjestelmän välillä
- 397 miljardin parametrin mallin suorittaminen kahdella verkotetulla Ryzen AI Halo -järjestelmällä

## Edellytykset

### Laitteisto

Tämä opas vaatii kaksi Ryzen AI Halo -yksikköä ja yhden Ethernet-kytkimen, jotka on kytketty tähtitopologiaan siten, että kumpikin yksikkö on kytketty suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Klusterin muodostavat laskentasolmut |
| 10 Gbps:n Ethernet-kytkin | 1 | Keskuskytkin, joka mahdollistaa Ryzen AI Halo -yksiköiden välisen monisolmuisen viestinnän (vähintään 2 porttia) |
| Ethernet-kaapeli | 2 | Yhdistää kunkin Halo-yksikön kytkimeen (suositellaan Cat 7 -kaapelia tai parempaa) |

> **Huomautus**: Kahden Ethernet-kytkimen portin yhdistäminen vaatii kaksi Ryzen AI Halo -yksikköä. Kolmas portti vaaditaan, jos käytät mallia erillisestä asiakaskoneesta yhden Halo-yksikön sijaan.

### Ohjelmisto
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Laitteiston fyysinen asennus

> **Huomautus**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

Yhdistä kumpikin Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 (tai parempi) -kaapelilla. Tämä muodostaa 10 Gbps:n yhteyden, jota käytetään solmujen väliseen nopeaan tiedonsiirtoon.

### 1. Verkkoliitäntöjen määrittäminen

Selvitä kummankin koneen verkkoliitännän nimi ja kirjoita se muistiin (siihen viitataan ohjeiden lopussa nimellä `IFNAME`). Suorita:

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

> **Huomautus**: Korvaa `<IFNAME>` liitännän nimellä kohdasta [1. Verkkoliitäntöjen määrittäminen](#1-determine-network-interfaces)

Näet nopeuden `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomautus**: Jos nopeus on pienempi kuin `10000Mb/s` tai yhteys ei muodostu, tarkista kaapelointi ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Joissakin kytkimissä automaattinen neuvottelu on poistettava käytöstä ja yhteysnopeus asetettava manuaalisesti; katso tarkemmat ohjeet kytkimesi dokumentaatiosta.

## VRAM-muistin allokoinnin laajentaminen

> **Huomautus**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

### Muistin konfigurointi suurten mallien suorittamista varten

Linuxissa ROCm käyttää jaettua järjestelmämuistin poolia, ja tämä pooli on oletuksena määritetty puoleen järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla ytimen Translation Table Manager (TTM) -sivuasetusta seuraavien ohjeiden mukaisesti. AMD suosittelee asettamaan vähimmäismäärän omistettua VRAM-muistia BIOSissa (0.5 GB).

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

## vLLM-säiliön alustaminen

> **Huomautus**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

Ryzen AI Halo -järjestelmäsi sisältää vLLM:n valmiiksi paketoituna säiliökuvana, jota ajetaan Podmanilla, ilmaisella ja avoimen lähdekoodin säiliötyökalulla.

### 1. Mallin latauskansion luominen

Kun tarjoat Qwen3.5-397B-mallia tässä oppaassa, vLLM lataa mallin painot automaattisesti järjestelmääsi. Jotta nämä painot ovat käytettävissä säiliön sisältä, luo ensin models-kansio, jonka säiliö voi liittää:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLM-säiliön käynnistäminen

Alla oleva komento käynnistää säiliön ja vie sinut interaktiiviseen komentotulkkiin. Se liittää juuri luomasi models-kansion ja välittää `IFNAME`-arvosi muuttujiin `NCCL_SOCKET_IFNAME` ja `GLOO_SOCKET_IFNAME`, jotka kertovat RCCL:lle (kirjasto, jota vLLM käyttää GPU:iden koordinointiin klusterin yli), mitä liitäntää käyttää.

Käynnistä säiliö komennolla:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Huomautus**: Korvaa `<IFNAME>` liitännän nimellä kohdasta [1. Verkkoliitäntöjen määrittäminen](#1-determine-network-interfaces)

## Mallin suorittaminen klusterissa

vLLM käyttää Rayta klusterin orkestrointiin ja RCCL:ää GPU-solmujen välisen viestinnän hoitamiseen. Yksi kone toimii **päänsolmuna** (Kone 1) ja koordinoi päättelyä. Toinen liittyy **työntekijäsolmuna** (Kone 2) tarjoten oman GPU-muistinsa ja laskentatehonsa.

> **Huomautus**: Ray on vLLM:n valinnainen riippuvuus ja on saatavilla ainoastaan esikonfiguroidun Podman-säiliön sisältä.

Käynnistyksessä vLLM jakaa mallin molempien solmujen kesken tensori-rinnakkaisuutta käyttäen. Latauksen jälkeen päättely etenee ikään kuin se ajettaisiin yhdellä kiihdyttimellä.

#### Ray OOM -virheiden estäminen

Oletusarvoisesti Ray valvoo kunkin solmun isäntämuistia ja sulkee suurimman prosessin, kun muistinkäyttö ylittää 95 %. Ryzen™ AI Halo -järjestelmässäsi GPU ja isäntä jakavat saman muistipoolin, joten mallin lataaminen voi laukaista `ray.exceptions.OutOfMemoryError`-virheen ja sulkea työntekijäprosessin.

Tämän estämiseksi asetamme `RAY_memory_monitor_refresh_ms=0`-ympäristömuuttujan kummallakin koneella ennen klusterin käynnistämistä ja siihen liittymistä.
### Vaihe 1: Käynnistä Ray-päänoodi (Kone 1)

Käynnistä Koneella 1 Ray-päänoodi klusterin alustamiseksi:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>`:n selvittäminen**: Suorita Koneella 1 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.

### Vaihe 2: Liity klusteriin (Kone 2)

Muodosta Koneella 2 yhteys päänoodiin klusterin luomiseksi:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>`:n selvittäminen**: Suorita Koneella 2 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.

### Vaihe 3: Palvele mallia (Kone 1)

Käynnistä Koneella 1 vLLM-palvelin. Tämä lataa automaattisesti mallin ja alkaa palvella sitä molempien noodien kautta:

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

#### Parametriviittaus

| Lippu | Tarkoitus |
|------|---------|
| `--port` | Portti, jossa HTTP-rajapintaa tarjotaan |
| `--host` | IP-osoite, johon palvelin sidotaan (`0.0.0.0` kaikille verkkoliitännöille) |
| `--max-model-len` | Enimmäiskontekstipituus tokeneina |
| `--gpu-memory-utilization` | GPU-muistin osuus, joka varataan (0,0–1,0) |
| `--dtype` | Mallin painojen datatyyppi |
| `--tensor-parallel-size` | GPU:iden lukumäärä, joiden kesken malli jaetaan (aseta klusterin GPU:iden kokonaismäärään) |
| `--distributed-executor-backend` | Taustajärjestelmä usean noodin suoritukseen (`ray` klusterikäyttöönotoille) |
| `--enforce-eager` | Poistaa CUDA-graafien käännön käytöstä yhteensopivuuden vuoksi |
| `--language-model-only` | Ohittaa apumallikomponenttien (esim. näköenkooderin) lataamisen |
| `--reasoning-parser` | Ottaa käyttöön mallin jäsennellyn päättelytuloksen jäsentämisen |

Täydelliset parametrien käyttöohjeet löytyvät [vLLM-dokumentaatiosta](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Mallin käyttäminen

vLLM tarjoaa OpenAI-yhteensopivan rajapinnan, joten voit yhdistää minkä tahansa yhteensopivan asiakasohjelman tai käyttöliittymän klusteriisi. Yksi suosittu vaihtoehto on [Open WebUI](https://github.com/open-webui/open-webui), joka tarjoaa selainpohjaisen keskustelukäyttöliittymän.

Yhdistä Open WebUI vLLM-päätepisteeseesi seuraavasti:

1. Avaa **Settings** > **Admin Panel** > **Connections**
2. Napsauta **+**-painiketta kohdassa **Manage OpenAI API Connections**
3. Aseta **Connection Type** arvoon **External**
4. Aseta **URL** arvoon `http://<MACHINE_1_IP>:7000/v1`
5. Valitse kohdassa **Auth** avattavasta valikosta **None**
6. Jätä **Model IDs** tyhjäksi, jotta kaikki mallit löytyvät automaattisesti päätepisteestä

> **`<MACHINE_1_IP>`:n selvittäminen**: Suorita Koneella 1 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi. Jos käytät Open WebUI:ta Koneelta 1 itseltään, voit käyttää osoitetta `http://localhost:7000/v1`.

![Open WebUI -yhteysasetukset vLLM-päätepisteelle](assets/openwebui-connection.png)

Kun yhteys on muodostettu, valitse malli Open WebUI:n mallien pudotusvalikosta ja aloita keskustelu. Malli toimii nyt molempien Ryzen AI Halo -noodiesi kesken:

![Keskustelu Qwen3.5-397B:n kanssa Open WebUI:ssa](assets/openwebui-chat.png)

## Seuraavat vaiheet

- **Tutustu muihin malleihin**: Löydä uusia malleja [Hugging Facesta](https://huggingface.co/models?&sort=trending), jotka mahtuvat klusterisi yhdistettyyn GPU-muistiin
- **Laajenna neljään noodiin**: Lisää kaksi Ryzen AI Halo -järjestelmää lisää Ray-työntekijöiksi, jotta mallit voidaan jakaa vieläkin useamman GPU:n kesken. Tämä vaatii Ethernet-kytkimen, jossa on vähintään neljä porttia, yksi jokaista noodia varten. Seuraa [Vaihetta 2: Liity klusteriin](#step-2-join-the-cluster-machine-2) jokaisella lisätyöntekijällä ja kasvata `--tensor-parallel-size`-arvoa vastaavasti
- **Kokeile muita rinnakkaisuusstrategioita**: vLLM tukee [asiantuntijarinnakkaisuutta](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) mixture-of-experts-malleille ja [datarinnakkaisuutta](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) suuremman läpisyötön saavuttamiseksi. Kokeile `--enable-expert-parallel`- ja `--data-parallel-size`-parametreja löytääksesi parhaan kokoonpanon työkuormallesi