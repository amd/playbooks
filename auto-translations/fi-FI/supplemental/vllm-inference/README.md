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


## Yleiskatsaus

vLLM on suorituskykyinen päättelymoottori, joka on suunniteltu suuria kielimalleja (LLM) varten. Se tarjoaa optimoitua palvelua jatkuvalla eräkäsittelyllä (continuous batching) suurta läpäisyä varten sekä OpenAI-yhteensopivan API:n saumatonta sovellusintegraatiota varten. Tämä tekee vLLM:stä erinomaisen tuotantoympäristöihin, joissa nopeus ja resurssitehokkuus ovat kriittisiä.

Tässä ohjekirjassa opit palvelemaan LLM-malleja käyttämällä konteinoitua vLLM:ää integroidulla GPU:lla ja olemaan vuorovaikutuksessa mallien kanssa OpenAI Python API:n kautta.

## Mitä opit

- Miten asennat ja käynnistät vLLM-palvelimen AMD ROCm™ -tuella
- Miten olet vuorovaikutuksessa mallien kanssa OpenAI-yhteensopivien API-päätepisteiden kautta
- Miten lähetät kehotteita paikalliselle palvelimelle komennolla `vllm-prompt`

## Muistiasetusten määrittäminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

> **Huomautus**: Jos VS Code ei ole asennettuna, voit asentaa sen AMD Ryzen™ AI Developer Centerin avulla.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

vLLM toimii valmiiksi rakennetussa kontissa, jossa ROCm ja sen riippuvuudet on esiasennettu yhteensopiviksi. Lisäasennuksia ei tarvita.

Erillistä isäntäkoneen puoleista vLLM-asennusvaihetta ei ole. Käynnistä vLLM komennolla:

```bash
vllm-launch
```

Käynnistin käynnistää kontin, kohdistaa integroituun GPU:hun ja avaa paikallisen OpenAI-yhteensopivan vLLM-palvelimen. Vaihtoehtoisesti voit napsauttaa vLLM-kuvaketta tehtäväpalkissa.

## Pika-aloitus

### 1. Varmista, että vLLM-palvelin on käynnissä

Komennon `vllm-launch` alustus voi kestää pari minuuttia. Kun se on käynnistynyt, palvelin on saatavilla osoitteessa `http://localhost:8001`. Pidä käynnistyspääteikkuna auki, koska palvelin toimii etualalla, ja avaa jäljellä olevia vaiheita varten erillinen pääteikkuna. Alla olevissa esimerkeissä käytetään mallia `Qwen/Qwen3-1.7B`; jos käynnistin on määritetty käyttämään eri mallia, korvaa tuo malli-ID pyynnöissä.

### 2. Lähetä kehote

Käytä mukana toimitettua `vllm-prompt`-skriptiä lähettääksesi pyynnön paikalliselle vLLM:n OpenAI-yhteensopivalle palvelimelle:

```bash
vllm-prompt "Tell me a story"
```

### 3. Keskustele mallin kanssa OpenAI Python API:n avulla

Koska vLLM tarjoaa OpenAI-yhteensopivan API:n, voit käyttää `openai` Python-pakettia sen kanssa vuorovaikutukseen.

Luo ensin Python-virtuaaliympäristö:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Asenna OpenAI-paketti
```bash
pip install openai
```

Luo `OpenAI`-asiakas, joka osoittaa paikalliseen vLLM-palvelimeen OpenAI:n palvelimien sijaan. Asiakas vaatii `api_key`-arvon, mutta vLLM ei validoi sitä, joten mikä tahansa merkkijono kelpaa:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Lähetä sitten keskustelupäätöspyyntö (chat completion). Tässä käytetään samaa viestimuotoa kuin OpenAI API:ssa — lista viestejä, joilla on rooleja kuten `"user"` ja `"assistant"`. Asetuksella `stream=True` vastaus saapuu vähitellen sen sijaan, että se saapuisi kerralla:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

Lopuksi käy läpi suoratoistetut osat ja tulosta jokainen tekstinpätkä sitä mukaa kun se saapuu:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Mukana oleva skripti [chat_with_model.py](assets/chat_with_model.py) sisältää koko esimerkin ja se on ladattavissa.


## Mallin valitseminen ja määrittäminen

Oletusarvoisesti `vllm-launch` palvelee testimallia `Qwen/Qwen3-1.7B` portissa `8001`. Voit vaihtaa mallia, porttia ja vLLM:n palveluparametreja ilman kontin uudelleenrakentamista tai muokkaamista.

### AMD:n testaamat mallit

Seuraavat mallit on esikonfiguroitu ja validoitu AMD:n toimesta:

| Malli | Huomautukset |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Oletusmalli. Kevyt ja nopea ladata. |
| `openai/gpt-oss-20b` | Suurempi malli laadukkaampia vastauksia varten. |

### Eri mallin käynnistäminen

Anna malli-ID valitsimella `--model` (tai `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Portin vaihtaminen

Anna portti, joka on suurempi kuin 1024, valitsimella `--port` (tai `-p`); oletusarvo on `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Jos vaihdat porttia, osoita asiakkaan `base_url` samaan porttiin (esimerkiksi `http://localhost:8080/v1`).

### Lisäparametrien välittäminen vLLM:lle

Kaikki lisäargumentit välitetään suoraan vLLM:lle, joten voit säätää palvelun toimintaa, kuten kontekstin pituutta tai tietotyyppiä. Näiden antamiseen on kaksi tapaa.

**Rivin sisällä (inline)**, käynnistimen valitsinten jälkeen:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Pysyvästi**, määritystiedostossa osoitteessa `~/.local/share/vLLM/vllm-launch.conf`. Tätä tiedostoa ei ole oletuksena olemassa — luo se ja lisää argumenttisi Bash-taulukkona:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Käytä `+=`-operaattoria lisätäksesi oletusargumenttien perään niiden korvaamisen sijaan:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Nähdäksesi kaikki käynnistimen valinnat milloin tahansa, suorita:

```bash
vllm-launch --help
```

### Mistä malleja etsitään

`vllm-launch` etsii malleja kahdesta sijainnista:

| Sijainti | Polku |
|----------|------|
| Järjestelmämallit | `/var/cache/models` |
| Käyttäjän mallit | `~/.local/share/vLLM/models` |

Voit sijoittaa ladatun mallin kumpaan tahansa hakemistoon ja käynnistää sen antamalla sen polun tai ID:n valitsimelle `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Huomautus**: Oman ladatun mallin ajamisen tällä tavalla odotetaan toimivan, kunhan malli on sijoitettu johonkin yllä mainituista hakemistoista, mutta AMD ei ole vielä virallisesti validoinut tätä työnkulkua.

## Vianmääritys

### Yhteys evätty

Varmista, että palvelin on käynnissä:
```bash
curl http://localhost:8001/health
```

## Yhteenveto

Tässä ohjekirjassa opit, miten:

- Käynnistät konteinoidun vLLM:n ROCm-tuella integroidulla GPU:lla
- Käynnistät vLLM-palvelimen, jossa on OpenAI-yhteensopivat API-päätepisteet portissa 8001
- Lähetät kehotteita komennolla `vllm-prompt`
- Teet API-kutsuja vLLM-palvelimelle sekä suoratoisto- että ei-suoratoistopyynnöillä
- Ratkaiset yleisiä ongelmia palvelimen käynnistyksessä, muistissa ja asiakasyhteyksissä

Sinulla on nyt konteinoitu vLLM-käyttöönotto suurten kielimallien palvelemiseen optimoidulla suorituskyvyllä integroidulla GPU:lla.

## Seuraavat vaiheet

- **Kokeile eri malleja** — Käytä komentoa `vllm-launch --model <model>` kokeillaksesi eri LLM-malleja ja vertaillaksesi suorituskykyä (katso [Mallin valitseminen ja määrittäminen](#choosing-and-configuring-a-model)).
- **Rakenna sovellus** — Käytä OpenAI-yhteensopivaa API:a integroidaksesi vLLM:n Python-sovellukseen, chatbottiin tai automaatiotyönkulkuun.
- **Hienosäädä ja palvele** — Hienosäädä malli käyttäen LoRA- tai QLoRA-menetelmää ja ota se sitten käyttöön vLLM:llä optimoitua päättelyä varten.
## Lisäresurssit

- **[vLLM:n virallinen dokumentaatio](https://docs.vllm.ai/)** — Kattavia oppaita ja API-viitteitä
- **[vLLM:n GitHub-repositorio](https://github.com/vllm-project/vllm)** — Lähdekoodi, ongelmat ja yhteisön keskustelut