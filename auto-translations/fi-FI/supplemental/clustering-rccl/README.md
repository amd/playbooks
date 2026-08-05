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

Ryzen™ AI Halo -järjestelmäsi pystyy jo nyt ajamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän vielä pidemmälle yhdistämällä useiden järjestelmien GPU-muistin paikallisverkon yli, jolloin käytettävissäsi on entistä suurempia malleja vahvemmalla päättelykyvyllä, paremmalla koodin generoinnilla ja syvemmällä monikielisellä ymmärryksellä – täysin omalla laitteistollasi.

Tämä ohjekirja opastaa sinua klusteroimaan kaksi Ryzen AI Halo -järjestelmää RCCL:n (ROCm Communication Collectives Library) avulla käyttäen vLLM:ää, ja ajamaan Qwen3.5-397B-mallia, jossa on 397 miljardia parametria, molemmilla koneilla ROCm-kiihdytyksen avulla.

## Mitä opit

- Kuinka laajentaa VRAM-varausta Ryzen AI Halo -järjestelmissä
- vLLM:n käynnistäminen ROCm-tuella
- RCCL:n määrittäminen usean solmun tensori-rinnakkaista päättelyä varten kahden Ryzen AI Halo -järjestelmän välillä
- 397 miljardin parametrin mallin ajaminen kahdella verkotetulla Ryzen AI Halo -järjestelmällä

## Esivaatimukset

### Laitteisto

Tämä ohjekirja vaatii kaksi Ryzen AI Halo -yksikköä ja yhden Ethernet-kytkimen, jotka on kytketty tähtitopologiaan siten, että kumpikin yksikkö on kytketty suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Klusterin muodostavat laskentasolmut |
| 10 Gbps:n Ethernet-kytkin | 1 | Keskuskytkin, joka mahdollistaa usean Ryzen AI Halo -solmun välisen viestinnän (vähintään 2 porttia) |
| Ethernet-kaapeli | 2 | Yhdistää kunkin Halo-yksikön kytkimeen (suositellaan Cat 7 -kaapelia tai parempaa) |

> **Huomautus**: Kahden Ryzen AI Halo -yksikön yhdistämiseen tarvitaan kaksi Ethernet-kytkimen porttia. Kolmas portti tarvitaan, jos käytät mallia erillisestä asiakaskoneesta yhden Halo-yksikön sijaan.

### Ohjelmisto
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fyysisen laitteiston käyttöönotto

> **Huomautus**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

Yhdistä kukin Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 -kaapelilla (tai paremmalla). Tämä muodostaa 10 Gbps:n yhteyden, jota käytetään solmujen väliseen nopeaan tiedonsiirtoon.

### 1. Verkkoliitäntöjen määrittäminen

Selvitä kummankin koneen verkkoliitännän nimi ja kirjaa se ylös (siihen viitataan jäljempänä ohjeissa nimellä `IFNAME`). Suorita:

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

> **Huomautus**: Korvaa `<IFNAME>` liitännän nimellä, joka saatiin kohdasta [1. Verkkoliitäntöjen määrittäminen](#1-determine-network-interfaces)

Nopeuden pitäisi näkyä muodossa `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomautus**: Jos nopeus on alle `10000Mb/s` tai yhteys ei muodostu, tarkista kaapelin liitäntä ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Jotkin kytkimet vaativat automaattisen neuvottelun poistamista käytöstä ja yhteysnopeuden asettamista manuaalisesti; katso lisätietoja kytkimesi dokumentaatiosta.

## VRAM-varauksen laajentaminen

> **Huomautus**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

### Muistiasetukset suurten mallien ajamista varten

Linuxissa ROCm käyttää jaettua järjestelmämuistin poolia, ja tämä pooli on oletusarvoisesti asetettu puoleen järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla ytimen Translation Table Manager (TTM) -sivuasetusta seuraavien ohjeiden mukaisesti. AMD suosittelee asettamaan BIOSissa vähimmäismäärän varattua VRAM-muistia (0,5 Gt).

* Asenna pipx-työkalu ja lisää pipx:n asentamien wheel-pakettien polku järjestelmän hakupolkuun.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Asenna amd-debug-tools-wheel PyPI:stä.
  ```bash
  pipx install amd-debug-tools
  ```

* Suorita amd-ttm-työkalu tarkistaaksesi jaetun muistin nykyiset asetukset.
  ```bash
  amd-ttm
  ```

* Määritä jaetun muistin asetukset uudelleen arvoon **120 Gt**:
  ```bash
  amd-ttm --set 120
  ```

* Käynnistä järjestelmä uudelleen, jotta muutokset tulevat voimaan.

## vLLM-säiliön alustaminen

> **Huomautus**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

Ryzen AI Halo -järjestelmäsi tulee mukana valmiiksi rakennetun säiliökuvan sisällä olevan vLLM:n kanssa, jota ajetaan Podmanilla, ilmaisella ja avoimen lähdekoodin säiliötyökalulla.

### 1. Mallin latauskansion luominen

Kun palvelet Qwen3.5-397B-mallia tässä ohjekirjassa, vLLM lataa mallin painot automaattisesti järjestelmääsi. Jotta nämä painot olisivat käytettävissä säiliön sisältä, luo ensin mallikansio, jonka säiliö voi liittää:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLM-säiliön käynnistäminen

Alla oleva komento käynnistää säiliön ja vie sinut interaktiiviseen komentotulkkiin. Se liittää juuri luomasi mallikansion ja välittää `IFNAME`-arvosi muuttujille `NCCL_SOCKET_IFNAME` ja `GLOO_SOCKET_IFNAME`, jotka kertovat RCCL:lle (kirjastolle, jota vLLM käyttää GPU:iden koordinointiin klusterin yli), mitä liitäntää käytetään.

Käynnistä säiliö komennolla:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Huomautus**: Korvaa `<IFNAME>` liitännän nimellä, joka saatiin kohdasta [1. Verkkoliitäntöjen määrittäminen](#1-determine-network-interfaces)

## Mallin ajaminen klusterissa

vLLM käyttää Ray-kirjastoa klusterin orkestrointiin ja RCCL:ää GPU-laitteiden väliseen viestintään solmujen välillä. Yksi kone toimii **pääsolmuna** (Kone 1) ja koordinoi päättelyä. Toinen liittyy mukaan **työntekijäsolmuna** (Kone 2), tuoden mukanaan oman GPU-muistinsa ja laskentatehonsa.

> **Huomautus**: Ray on vLLM:n valinnainen riippuvuus, ja se on saatavilla vain esikonfiguroidun Podman-säiliön sisältä.

Käynnistyksen yhteydessä vLLM jakaa mallin kummallekin solmulle tensori-rinnakkaisuutta käyttäen. Kun malli on ladattu, päättely etenee ikään kuin se ajettaisiin yhdellä kiihdyttimellä.

### Vaihe 1: Ray-pääsolmun käynnistäminen (Kone 1)

Käynnistä Koneella 1 Ray-pääsolmu klusterin alustamiseksi:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>`:n löytäminen**: Suorita Koneella 1 komento `hostname -I | awk '{print $1}'` selvittääksesi sen paikallisen IP-osoitteen.
### Vaihe 2: Liity klusteriin (kone 2)

Muodosta koneella 2 yhteys päänoodiin klusterin muodostamiseksi:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Kohteen `<MACHINE_2_IP>` löytäminen**: Aja koneella 2 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.

### Vaihe 3: Tarjoa mallia (kone 1)

Käynnistä koneella 1 vLLM-palvelin. Tämä lataa mallin automaattisesti ja alkaa tarjota sitä molempien noodien kesken:

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
| `--host` | IP-osoite, johon palvelin sidotaan (`0.0.0.0` kaikille rajapinnoille) |
| `--max-model-len` | Suurin kontekstipituus tokeneina |
| `--gpu-memory-utilization` | Osuus GPU-muistista, joka varataan (0.0–1.0) |
| `--dtype` | Mallin painojen tietotyyppi |
| `--tensor-parallel-size` | GPU:iden määrä, joiden kesken malli jaetaan (aseta klusterin GPU:iden kokonaismäärään) |
| `--distributed-executor-backend` | Taustajärjestelmä usean noodin suoritukseen (`ray` klusteripohjaisiin käyttöönottoihin) |
| `--enforce-eager` | Poistaa CUDA-graafien kääntämisen käytöstä yhteensopivuuden vuoksi |
| `--language-model-only` | Ohittaa apumallikomponenttien (esim. näköenkooderin) lataamisen |
| `--reasoning-parser` | Ottaa käyttöön mallin jäsennellyn päättelytulosteen |

Katso täydelliset parametrien käyttöohjeet [vLLM-dokumentaatiosta](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Mallin käyttäminen

vLLM tarjoaa OpenAI-yhteensopivan rajapinnan, joten voit yhdistää minkä tahansa yhteensopivan asiakasohjelman tai käyttöliittymän klusteriisi. Yksi suosittu vaihtoehto on [Open WebUI](https://github.com/open-webui/open-webui), joka tarjoaa selainpohjaisen keskusteluliittymän.

Yhdistä Open WebUI vLLM-päätepisteeseesi seuraavasti:

1. Avaa **Settings** > **Admin Panel** > **Connections**
2. Napsauta kohdan **Manage OpenAI API Connections** kohtaa **+**
3. Aseta **Connection Type** -asetukseksi **External**
4. Aseta **URL**-kentäksi `http://<MACHINE_1_IP>:7000/v1`
5. Valitse kohdassa **Auth** pudotusvalikosta **None**
6. Jätä **Model IDs** tyhjäksi, jotta kaikki päätepisteen mallit tunnistetaan automaattisesti

> **Kohteen `<MACHINE_1_IP>` löytäminen**: Aja koneella 1 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi. Jos käytät Open WebUI:ta koneelta 1 itseltään, voit käyttää osoitetta `http://localhost:7000/v1`.

![Open WebUI -yhteysasetukset vLLM-päätepisteelle](assets/openwebui-connection.png)

Kun yhteys on muodostettu, valitse malli Open WebUI:n mallien pudotusvalikosta ja aloita keskustelu. Malli toimii nyt molempien Ryzen AI Halo -noodiesi kesken:

![Keskustelu Qwen3.5-397B:n kanssa Open WebUI:ssa](assets/openwebui-chat.png)

## Seuraavat vaiheet

- **Tutustu muihin malleihin**: Löydä uusia malleja [Hugging Facesta](https://huggingface.co/models?&sort=trending), jotka mahtuvat klusterisi yhdistettyyn GPU-muistiin
- **Skaalaa neljään noodiin**: Lisää kaksi uutta Ryzen AI Halo -järjestelmää lisä-Ray-työntekijöiksi, jotta mallit voidaan jakaa yhä useamman GPU:n kesken. Tämä edellyttää Ethernet-kytkintä, jossa on vähintään neljä porttia, yksi kutakin noodia kohden. Seuraa kohtaa [Vaihe 2: Liity klusteriin](#step-2-join-the-cluster-machine-2) jokaisella lisätyöntekijällä ja kasvata `--tensor-parallel-size`-arvoa vastaavasti
- **Kokeile muita rinnakkaisuusstrategioita**: vLLM tukee [asiantuntijarinnakkaisuutta](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) (expert parallel) mixture-of-experts-malleille ja [datarinnakkaisuutta](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) (data parallel) suuremman läpisyötön saavuttamiseksi. Kokeile `--enable-expert-parallel`- ja `--data-parallel-size`-asetuksia löytääksesi työkuormallesi parhaan konfiguraation