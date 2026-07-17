<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Kahden Ryzen™ AI Halon klusterointi RCCL:llä

## Yleiskatsaus

Ryzen™ AI Halo pystyy jo nyt ajamaan suuria kielimalleja paikallisesti. Klusterointi vie tämän pidemmälle yhdistämällä useiden järjestelmien GPU-muistin paikallisverkon yli, antaen sinulle pääsyn entistä suurempiin malleihin, joilla on vahvempi päättelykyky, parempi koodintuotanto ja syvempi monikielinen ymmärrys – kaikki täysin omalla laitteistollasi.

Tämä playbook opettaa sinulle, kuinka klusteroida kaksi Ryzen AI Halo -järjestelmää käyttämällä RCCL:ää (ROCm Communication Collectives Library) vLLM:n kanssa ja ajaa Qwen3.5-397B, 397 miljardin parametrin malli, molemmilla koneilla ROCm-kiihdytyksen avulla.

## Mitä opit

- Kuinka laajentaa VRAM-allokointia Ryzen AI Halo -järjestelmissä
- vLLM:n käynnistäminen ROCm-tuella
- RCCL:n konfigurointi monisolmuiseen tensor-rinnakkaiseen inferenssiin kahden Ryzen AI Halo -järjestelmän välillä
- 397 miljardin parametrin mallin ajaminen kahdella verkotetuilla Ryzen AI Halo -järjestelmällä

## Edellytykset

### Laitteisto

Tämä playbook vaatii kaksi Ryzen AI Halo -yksikköä ja yhden Ethernet-kytkimen, jotka on kytketty tähtitopologiassa siten, että kukin yksikkö on johdotettu suoraan kytkimeen.

| Komponentti | Määrä | Kuvaus |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Laskentasolmut, jotka muodostavat klusterin |
| 10 Gbps:n Ethernet-kytkin | 1 | Keskuskytkin monisolmuisen Ryzen AI Halo -viestinnän mahdollistamiseksi (vähintään 2 porttia) |
| Ethernet-kaapeli | 2 | Yhdistää jokaisen Halo-yksikön kytkimeen (Cat 7 tai korkeampi suositellaan) |

> **Huomio**: Kahden Ryzen AI Halo -yksikön yhdistämiseen tarvitaan kaksi Ethernet-kytkimen porttia. Kolmas portti tarvitaan, jos käytät mallia erilliseltä asiakaskoneelta yhden Halo-yksikön sijaan.

### Ohjelmisto
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fyysinen laitteistoasennus

> **Huomio**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

Kytke jokainen Ryzen AI Halo -yksikkö Ethernet-kytkimeen Cat 7 (tai korkeamman luokan) kaapelilla. Tämä muodostaa 10 Gbps:n yhteyden, jota käytetään solmujen väliseen nopean tiedonsiirron viestintään.

### 1. Määritä verkkoliitännät

Etsi jokaisella koneella sen verkkoliitännän nimi ja kirjaa se muistiin (siihen viitataan loppuohjeissa nimellä `IFNAME`). Suorita:

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

> **Huomio**: Korvaa `<IFNAME>` kohdasta [1. Määritä verkkoliitännät](#1-determine-network-interfaces) saadulla liitännän nimellä

Sinun pitäisi nähdä nopeus `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Huomio**: Jos nopeus on alle `10000Mb/s` tai yhteys ei muodostu, tarkista kaapeliyhteys ja varmista, että kytkimen portti on asetettu 10 Gbps:iin. Jotkin kytkimet vaativat automaattisen neuvottelun poistamista käytöstä ja linkin nopeuden asettamista manuaalisesti; katso kytkimesi dokumentaatiota.

## VRAM-allokoinnin laajentaminen

> **Huomio**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

### Muistikonfiguraatio suurten mallien ajamiseen

Linuxissa ROCm hyödyntää jaettua järjestelmämuistipoolia, ja tämä pooli on oletuksena konfiguroitu puoleen järjestelmämuistista.

Tätä määrää voidaan kasvattaa muuttamalla ytimen Translation Table Manager (TTM) -sivuasetusta seuraavien ohjeiden mukaisesti. AMD suosittelee asettamaan BIOS:ssa minimidedikoitu VRAM (0,5 GB).

* Asenna pipx-apuohjelma ja lisää pipx:n asentamien pakettien polku järjestelmän hakupolkuun.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Asenna amd-debug-tools-paketti PyPI:stä.
  ```bash
  pipx install amd-debug-tools
  ```

* Suorita amd-ttm-työkalu jaetun muistin nykyisten asetusten kyselyyn.
  ```bash
  amd-ttm
  ```

* Konfiguroi jaetun muistin asetukset uudelleen **120 GB**:ksi:
  ```bash
  amd-ttm --set 120
  ```

* Käynnistä järjestelmä uudelleen, jotta muutokset tulevat voimaan.

## vLLM-säilön alustus

> **Huomio**: Suorita tämä vaihe sekä Koneella 1 että Koneella 2.

Ryzen AI Halo toimitetaan vLLM:n kanssa pakattuna valmiiksi rakennettuun säilökuvaan, jota ajetaan Podmanilla, vapaalla ja avoimen lähdekoodin säilötyökalulla.

### 1. Luo mallien lataushakemisto

Kun tarjoilet tässä playbookissa Qwen3.5-397B-mallia, vLLM lataa mallin painot automaattisesti järjestelmääsi. Jotta nämä painot ovat käytettävissä säilön sisältä, luo ensin mallihakemisto, jonka säilö voi liittää:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Käynnistä vLLM-säilö

Alla oleva komento käynnistää säilön ja avaa interaktiivisen komentotulkin. Se liittää juuri luomasi mallihakemiston ja välittää `IFNAME`-arvosi `NCCL_SOCKET_IFNAME`- ja `GLOO_SOCKET_IFNAME`-muuttujille, kertoen RCCL:lle (kirjastolle, jota vLLM käyttää GPU:iden koordinointiin klusterissa), mitä liitäntää käyttää.

Käynnistä säilö komennolla:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Huomio**: Korvaa `<IFNAME>` kohdasta [1. Määritä verkkoliitännät](#1-determine-network-interfaces) saadulla liitännän nimellä

## Mallin ajaminen klusterissa

vLLM käyttää Rayta klusterin orkestrointiin ja RCCL:ää GPU:iden väliseen viestintään solmujen välillä. Yksi kone toimii **pääsolmuna** (Kone 1) koordinoiden inferenssiä. Toinen liittyy **työntekijäsolmuna** (Kone 2) tarjoten GPU-muistiaan ja laskentatehonsa.

> **Huomio**: Ray on vLLM:n valinnainen riippuvuus ja on saatavilla vain valmiiksi konfiguroidun Podman-säilön sisältä.

Käynnistyksen yhteydessä vLLM jakaa mallin molemmille solmuille tensor-rinnakkaisuuden avulla. Kun malli on ladattu, inferenssi etenee kuin se toimisi yhdellä kiihdyttimellä.

### Vaihe 1: Käynnistä Ray-pääsolmu (Kone 1)

Koneella 1 käynnistä Ray-pääsolmu klusterin alustamiseksi:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>`-osoitteen löytäminen**: Koneella 1 suorita `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen.

### Vaihe 2: Liity klusteriin (Kone 2)

Koneella 2 muodosta yhteys pääsolmuun klusterin muodostamiseksi:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>`-osoitteen löytäminen**: Koneella 2 suorita `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen.

### Vaihe 3: Tarjoile malli (Kone 1)

Koneella 1 käynnistä vLLM-palvelin. Tämä lataa mallin automaattisesti ja alkaa tarjoilla sitä molemmilla solmuilla:

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
| `--port` | Portti, jossa HTTP API:a tarjoillaan |
| `--host` | IP-osoite, johon palvelin sidotaan (`0.0.0.0` kaikille liitännöille) |
| `--max-model-len` | Enimmäiskontekstin pituus tokeneina |
| `--gpu-memory-utilization` | Allokoitavan GPU-muistin osuus (0,0–1,0) |
| `--dtype` | Mallin painojen tietotyyppi |
| `--tensor-parallel-size` | GPU:iden määrä, joille malli jaetaan (aseta klusterin GPU:iden kokonaismäärään) |
| `--distributed-executor-backend` | Taustajärjestelmä monisolmuiseen suoritukseen (`ray` klusterikäyttöönotoissa) |
| `--enforce-eager` | Poistaa CUDA-graafin kääntämisen käytöstä yhteensopivuuden vuoksi |
| `--language-model-only` | Ohittaa apumallien komponenttien lataamisen (esim. näköenkooder) |
| `--reasoning-parser` | Ottaa käyttöön jäsennellyn päättelytulosteen jäsentämisen mallille |

Täydellisen parametrien käytön osalta katso [vLLM-dokumentaatio](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Mallin käyttäminen

vLLM tarjoaa OpenAI-yhteensopivan API:n, joten voit yhdistää minkä tahansa yhteensopivan asiakkaan tai käyttöliittymän klusteriisi. Yksi suosittu vaihtoehto on [Open WebUI](https://github.com/open-webui/open-webui), joka tarjoaa selainpohjaisen chat-käyttöliittymän.

Open WebUI:n yhdistämiseksi vLLM-päätepisteeseen:

1. Avaa **Asetukset** > **Hallintapaneeli** > **Yhteydet**
2. Napsauta **+** kohdassa **Hallitse OpenAI API -yhteyksiä**
3. Aseta **Yhteystyyppi** arvoon **Ulkoinen**
4. Aseta **URL** arvoon `http://<MACHINE_1_IP>:7000/v1`
5. Kohdassa **Todennus** valitse **Ei mitään** pudotusvalikosta
6. Jätä **Mallitunnukset** tyhjäksi, jotta kaikki mallit löydetään automaattisesti päätepisteestä

> **`<MACHINE_1_IP>`-osoitteen löytäminen**: Koneella 1 suorita `hostname -I | awk '{print $1}'` löytääksesi sen paikallisen IP-osoitteen. Jos käytät Open WebUI:ta Koneelta 1 itseltään, voit käyttää osoitetta `http://localhost:7000/v1`.

![Open WebUI -yhteysasetukset vLLM-päätepisteelle](assets/openwebui-connection.png)

Kun yhteys on muodostettu, valitse malli Open WebUI:n mallin pudotusvalikosta ja aloita keskustelu. Malli toimii nyt molemmilla Ryzen AI Halo -solmuillasi:

![Keskustelu Qwen3.5-397B:n kanssa Open WebUI:ssa](assets/openwebui-chat.png)

## Seuraavat vaiheet

- **Tutustu muihin malleihin**: Löydä uusia malleja [Hugging Facesta](https://huggingface.co/models?&sort=trending), jotka mahtuvat klusterisi yhdistettyyn GPU-muistiin
- **Skaalaa neljään solmuun**: Lisää kaksi Ryzen AI Halo -järjestelmää lisätyöntekijöinä Ray-klusteriin jakaaksesi mallit entistä useammalle GPU:lle. Tämä vaatii Ethernet-kytkimen, jossa on vähintään neljä porttia, yksi kullekin solmulle. Seuraa kohtaa [Vaihe 2: Liity klusteriin](#step-2-join-the-cluster-machine-2) jokaisella lisätyöntekijällä ja kasvata `--tensor-parallel-size`-arvoa vastaavasti
- **Kokeile muita rinnakkaisuusstrategioita**: vLLM tukee [asiantuntijarinnakkaisuutta](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) mixture-of-experts-malleille ja [datarinnakkaisuutta](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) korkeamman suorituskyvyn saavuttamiseksi. Kokeile `--enable-expert-parallel`- ja `--data-parallel-size`-asetuksia löytääksesi parhaan konfiguraation työkuormallesi