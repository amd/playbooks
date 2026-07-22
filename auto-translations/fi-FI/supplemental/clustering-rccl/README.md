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
> Tässä ohjeessa käytetään erikoismerkintöjä, joita GitHub ei pysty näyttämään oikein. Käy osoitteessa [amd.com/playbooks](https://amd.com/playbooks) nähdäksesi tämän sisällön oikein esikatseltuna.
<!-- @github-only:end -->

# Kahden Ryzen™ AI Halo -järjestelmän klusterointi RCCL:llä

## Yleiskatsaus

Ryzen™ AI Halo -järjestelmäsi pystyy jo nyt ajamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän vielä pidemmälle yhdistämällä useiden järjestelmien GPU-muistin paikallisverkon yli, jolloin käytettävissäsi on entistä suurempia malleja vahvemmalla päättelykyvyllä, paremmalla koodin generoinnilla ja syvemmällä monikielisellä ymmärryksellä – kaikki täysin omalla laitteistollasi.

Tässä ohjeessa opit klusteroimaan kaksi Ryzen AI Halo -järjestelmää käyttäen RCCL:ää (ROCm Communication Collectives Library) yhdessä vLLM:n kanssa ja ajamaan Qwen3.5-397B-mallia, jossa on 397 miljardia parametria, molemmilla koneilla ROCm-kiihdytyksen avulla.

## Mitä opit

- Kuinka laajentaa VRAM-varausta Ryzen AI Halo -järjestelmissä
- vLLM:n käynnistäminen ROCm-tuella
- RCCL:n määrittäminen usean solmun tensor-rinnakkaista päättelyä varten kahden Ryzen AI Halo -järjestelmän välillä
- 397 miljardin parametrin mallin ajaminen kahdella verkotetulla Ryzen AI Halo -järjestelmällä

## Edellytykset

### Laitteisto

Tämä ohje edellyttää kahta Ryzen AI Halo -yksikköä ja yhtä Ethernet-kytkintä, jotka on kytketty tähtitopologiaan siten, että kumpikin yksikkö on kytketty suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Klusterin muodostavat laskentasolmut |
| 10 Gbps:n Ethernet-kytkin | 1 | Keskitetty kytkin, joka mahdollistaa usean Ryzen AI Halo -solmun välisen viestinnän (vähintään 2 porttia) |
| Ethernet-kaapeli | 2 | Yhdistää kummankin Halo-yksikön kytkimeen (suositellaan Cat 7 -kaapelia tai parempaa) |

> **Huomautus**: Kahden Ryzen AI Halo -yksikön kytkemiseen tarvitaan kaksi Ethernet-kytkimen porttia. Kolmas portti tarvitaan, jos käytät mallia erillisestä asiakaskoneesta yhden Halo-yksikön sijaan.

### Ohjelmisto
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Laitteiston fyysinen asennus

> **Huomautus**: Suorita tämä vaihe sekä koneella 1 että koneella 2.

Yhdistä kumpikin Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 -kaapelilla (tai paremmalla). Näin muodostetaan solmujen välinen 10 Gbps:n nopea yhteys.

### 1. Verkkoliitäntöjen määrittäminen

Selvitä kummastakin koneesta sen verkkoliitännän nimi ja kirjaa se muistiin (siihen viitataan ohjeen loppuosassa nimellä `IFNAME`). Suorita:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tämä tulostaa liitännän nimen suoraan, esimerkiksi:

```bash
enp191s0
```

### 2. Verkkoyhteyden nopeuden tarkistaminen

Varmista, että yhteys on aktiivinen ja toimii täydellä nopeudella tarkistamalla liitäntäsi nopeus:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Huomautus**: Korvaa `<IFNAME>` kohdasta [1. Verkkoliitäntöjen määrittäminen](#1-determine-network-interfaces) saadulla liitännän nimellä

Nopeuden pitäisi olla `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomautus**: Jos nopeus on alle `10000Mb/s` tai yhteys ei muodostu, tarkista kaapelikytkentä ja varmista, että kytkimen portti on asetettu 10 Gbps:n nopeuteen. Joissakin kytkimissä automaattinen neuvottelu on ensin poistettava käytöstä ja nopeus asetettava manuaalisesti; katso lisätietoja kytkimesi käyttöoppaasta.

## VRAM-varauksen laajentaminen

> **Huomautus**: Suorita tämä vaihe sekä koneella 1 että koneella 2.

### Muistin määrittäminen suurten mallien ajamista varten

Linuxissa ROCm käyttää jaettua järjestelmämuistin poolia, ja tämä pooli on oletusarvoisesti puolet järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla kernelin Translation Table Manager (TTM) -sivuasetusta alla olevien ohjeiden mukaisesti. AMD suosittelee asettamaan BIOSissa varatun VRAM-muistin vähimmäismääräksi 0,5 Gt.

* Asenna pipx-työkalu ja lisää pipx:llä asennettujen wheel-pakettien polku järjestelmän hakupolkuun.

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

## vLLM-säilön alustaminen

> **Huomautus**: Suorita tämä vaihe sekä koneella 1 että koneella 2.

Ryzen AI Halo -järjestelmäsi tulee mukana vLLM:n kanssa valmiiksi paketoituna säilökuvana, jota ajetaan Podmanilla – ilmaisella ja avoimen lähdekoodin säilötyökalulla.

### 1. Mallien latauskansion luominen

Kun tarjoat Qwen3.5-397B-mallia tässä ohjeessa, vLLM lataa mallin painot automaattisesti järjestelmääsi. Jotta nämä painot ovat käytettävissä säilön sisältä, luo ensin models-kansio, jonka säilö voi liittää:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLM-säilön käynnistäminen

Alla oleva komento käynnistää säilön ja avaa interaktiivisen komentorivin. Se liittää juuri luomasi models-kansion ja välittää `IFNAME`-arvon muuttujiin `NCCL_SOCKET_IFNAME` ja `GLOO_SOCKET_IFNAME`, jolloin RCCL:lle (kirjasto, jota vLLM käyttää GPU:iden koordinointiin klusterin solmujen välillä) kerrotaan, mitä liitäntää käyttää.

Käynnistä säilö komennolla:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Huomautus**: Korvaa `<IFNAME>` kohdasta [1. Verkkoliitäntöjen määrittäminen](#1-determine-network-interfaces) saadulla liitännän nimellä

## Mallin ajaminen klusterissa

vLLM käyttää Ray-kirjastoa klusterin orkestrointiin ja RCCL:ää GPU-yksiköiden väliseen viestintään solmujen välillä. Yksi kone toimii **pääsolmuna** (kone 1) koordinoiden päättelyä. Toinen liittyy klusteriin **työsolmuna** (kone 2) ja tarjoaa oman GPU-muistinsa ja laskentakapasiteettinsa.

> **Huomautus**: Ray on vLLM:n valinnainen riippuvuus, ja se on käytettävissä vain valmiiksi määritetyn Podman-säilön sisällä.

Käynnistyksen yhteydessä vLLM jakaa mallin molempien solmujen kesken tensor-rinnakkaisuutta käyttäen. Kun malli on ladattu, päättely etenee ikään kuin se ajettaisiin yhdellä kiihdyttimellä.

### Vaihe 1: Ray-pääsolmun käynnistäminen (kone 1)

Käynnistä koneella 1 Ray-pääsolmu klusterin alustamiseksi:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>`:n selvittäminen**: Selvitä koneen 1 paikallinen IP-osoite suorittamalla siinä komento `hostname -I | awk '{print $1}'`.
### Vaihe 2: Liity klusteriin (Kone 2)

Muodosta Koneessa 2 yhteys pääsolmuun klusterin muodostamiseksi:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>`:n selvittäminen**: Suorita Koneessa 2 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi.

### Vaihe 3: Tarjoile malli (Kone 1)

Käynnistä Koneessa 1 vLLM-palvelin. Tämä lataa mallin automaattisesti ja alkaa tarjoilla sitä molemmilla solmuilla:

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
| `--port` | Portti, jossa HTTP-rajapintaa tarjoillaan |
| `--host` | IP-osoite, johon palvelin sidotaan (`0.0.0.0` kaikille verkkoliitännöille) |
| `--max-model-len` | Suurin kontekstipituus tokeneina |
| `--gpu-memory-utilization` | GPU-muistista varattava osuus (0.0–1.0) |
| `--dtype` | Mallin painojen tietotyyppi |
| `--tensor-parallel-size` | GPU:iden lukumäärä, joiden kesken malli jaetaan (aseta klusterin GPU:iden kokonaismäärään) |
| `--distributed-executor-backend` | Moninosolmuisen suorituksen taustajärjestelmä (`ray` klusteriasennuksille) |
| `--enforce-eager` | Poistaa CUDA-graafien kääntämisen käytöstä yhteensopivuuden vuoksi |
| `--language-model-only` | Ohittaa apumallikomponenttien (esim. näköenkooderin) lataamisen |
| `--reasoning-parser` | Ottaa käyttöön mallin jäsennellyn päättelytulosteen jäsentämisen |

Täydelliset parametrien käyttöohjeet löydät [vLLM-dokumentaatiosta](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Mallin käyttäminen

vLLM tarjoaa OpenAI-yhteensopivan rajapinnan, joten voit yhdistää minkä tahansa yhteensopivan asiakassovelluksen tai käyttöliittymän klusteriisi. Yksi suosittu vaihtoehto on [Open WebUI](https://github.com/open-webui/open-webui), joka tarjoaa selainpohjaisen keskusteluliittymän.

Yhdistääksesi Open WebUI:n vLLM-päätepisteeseesi:

1. Avaa **Asetukset** > **Ylläpitopaneeli** > **Yhteydet**
2. Napsauta **+**-painiketta kohdassa **Hallitse OpenAI API -yhteyksiä**
3. Aseta **Yhteystyypiksi** **Ulkoinen**
4. Aseta **URL-osoitteeksi** `http://<MACHINE_1_IP>:7000/v1`
5. Valitse kohdassa **Todennus** avattavasta valikosta **Ei mitään**
6. Jätä **Malli-tunnukset** tyhjäksi, jotta kaikki mallit löydetään päätepisteestä automaattisesti

> **`<MACHINE_1_IP>`:n selvittäminen**: Suorita Koneessa 1 komento `hostname -I | awk '{print $1}'` sen paikallisen IP-osoitteen selvittämiseksi. Jos käytät Open WebUI:ta itse Koneesta 1, voit käyttää osoitetta `http://localhost:7000/v1`.

![Open WebUI:n yhteysasetukset vLLM-päätepisteelle](assets/openwebui-connection.png)

Kun yhteys on muodostettu, valitse malli Open WebUI:n mallien pudotusvalikosta ja aloita keskustelu. Malli toimii nyt molemmilla Ryzen AI Halo -solmuillasi:

![Keskustelu Qwen3.5-397B:n kanssa Open WebUI:ssa](assets/openwebui-chat.png)

## Seuraavat vaiheet

- **Tutustu muihin malleihin**: Löydä [Hugging Facesta](https://huggingface.co/models?&sort=trending) uusia malleja, jotka mahtuvat klusterisi yhdistettyyn GPU-muistiin
- **Skaalaa neljään solmuun**: Lisää kaksi Ryzen AI Halo -järjestelmää lisää Ray-työläisiksi, jotta mallit voidaan jakaa vieläkin useamman GPU:n kesken. Tämä vaatii Ethernet-kytkimen, jossa on vähintään neljä porttia, yksi jokaista solmua kohden. Seuraa [Vaihe 2: Liity klusteriin](#step-2-join-the-cluster-machine-2) -ohjetta jokaisella lisätyöläisellä ja kasvata `--tensor-parallel-size`-arvoa vastaavasti
- **Kokeile muita rinnakkaisuusstrategioita**: vLLM tukee [asiantuntijarinnakkaisuutta](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) mixture-of-experts-malleille ja [datarinnakkaisuutta](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) suuremman läpimenon saavuttamiseksi. Kokeile `--enable-expert-parallel`- ja `--data-parallel-size`-parametreja löytääksesi parhaan kokoonpanon työkuormallesi