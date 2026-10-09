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

vLLM on suorituskykyinen päättelymoottori, joka on suunniteltu suuria kielimalleja (LLM) varten. Se tarjoaa optimoidun palvelun jatkuvalla eräkäsittelyllä suurta suoritustehoa varten sekä OpenAI-yhteensopivan API:n saumatonta sovellusintegraatiota varten. Tämä tekee vLLM:stä erinomaisen tuotantokäyttöönottoihin, joissa nopeus ja resurssitehokkuus ovat kriittisiä.

Tämä opas opettaa, miten LLM-malleja palvellaan käyttäen konteriloitua vLLM:ää integroidulla GPU:lla ja miten malleja käytetään OpenAI Python API:n kautta.

## Mitä opit

- Miten vLLM-palvelin asennetaan ja käynnistetään AMD ROCm™ -tuella
- Miten malleja käytetään OpenAI-yhteensopivien API-päätepisteiden kautta
- Miten kehotteita lähetetään paikalliselle palvelimelle komennolla `vllm-prompt`

## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

> **Huomautus**: Jos VS Code ei ole asennettuna, voit asentaa sen AMD Ryzen™ AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmistojen esivaatimusten asentaminen

vLLM toimii valmiiksi rakennetussa kontissa, jossa ROCm ja sen riippuvuudet on valmiiksi täsmätty. Lisäasennuksia ei tarvita.

Isäntäkoneen puolella ei ole erillistä vLLM-asennusvaihetta. Käynnistä vLLM komennolla:

```bash
vllm-launch
```

Käynnistin käynnistää kontin, kohdistaa sen integroituun GPU:hun ja tarjoaa paikallisen OpenAI-yhteensopivan vLLM-palvelimen. Vaihtoehtoisesti napsauta vLLM-kuvaketta tehtäväpalkissa.

## Pika-aloitus

### 1. Vahvista, että vLLM-palvelin on käynnissä

`vllm-launch`-komennon alustaminen voi kestää pari minuuttia. Kun se käynnistyy, palvelin on saatavilla osoitteessa `http://localhost:8001`. Pidä käynnistysterminaali auki, koska palvelin toimii etualalla, ja avaa erillinen terminaali jäljellä oleville vaiheille. Alla olevat esimerkit käyttävät mallia `Qwen/Qwen3-1.7B`; jos käynnistin on määritetty käyttämään eri mallia, korvaa se pyynnöissä käyttämälläsi malli-ID:llä.

### 2. Lähetä kehote

Käytä mukana tulevaa `vllm-prompt`-skriptiä pyynnön lähettämiseen paikalliselle vLLM OpenAI-yhteensopivalle palvelimelle:

```bash
vllm-prompt "Tell me a story"
```

### 3. Keskustele mallin kanssa OpenAI Python API:n avulla

Koska vLLM tarjoaa OpenAI-yhteensopivan API:n, voit käyttää `openai`-Python-pakettia sen kanssa vuorovaikutukseen.

Luo ensin Python-virtuaaliympäristö:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->

Asenna OpenAI-paketti
```bash
pip install openai
```

Luo `OpenAI`-asiakas, joka osoittaa paikalliseen vLLM-palvelimeen OpenAI:n palvelinten sijaan. Asiakas vaatii `api_key`-arvon, mutta vLLM ei validoi sitä, joten mikä tahansa merkkijono toimii:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Lähetä sitten keskustelutäydennyspyyntö. Tämä käyttää samaa viestimuotoa kuin OpenAI API — lista viestejä, joilla on rooleja kuten `"user"` ja `"assistant"`. Asettamalla `stream=True` vastaus saapuu vähitellen eikä kerralla:

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

Lopuksi käy läpi suoratoistetut osat ja tulosta jokainen tekstinpala sitä mukaa, kun se saapuu:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Mukana oleva [chat_with_model.py](assets/chat_with_model.py)-skripti sisältää koko esimerkin ja se on ladattavissa.


## Mallin valitseminen ja määrittäminen

Oletuksena `vllm-launch` palvelee mallia `Qwen/Qwen3-1.7B` testimallina portissa `8001`. Voit vaihtaa mallia, porttia ja vLLM:n palveluparametreja ilman kontin uudelleenrakentamista tai muokkaamista.

### AMD:n testaamat mallit

Seuraavat mallit on esimääritetty ja AMD on validoinut ne:

| Malli | Huomautukset |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Oletusmalli. Kevyt ja nopea ladata. |
| `openai/gpt-oss-20b` | Suurempi malli korkealaatuisempia vastauksia varten. |

### Eri mallin käynnistäminen

Anna malli-ID:n valitsimella `--model` (tai `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Portin vaihtaminen

Anna portti, joka on suurempi kuin 1024, valitsimella `--port` (tai `-p`); oletusarvo on `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Jos vaihdat porttia, osoita asiakkaan `base_url` samaan porttiin (esimerkiksi `http://localhost:8080/v1`).

### Ylimääräisten vLLM-parametrien välittäminen

Kaikki lisäargumentit välitetään suoraan vLLM:lle, joten voit säätää palvelun toimintaa, kuten kontekstin pituutta tai tietotyyppiä. Niitä voi antaa kahdella tavalla.

**Rivillä**, käynnistimen valitsimien jälkeen:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Pysyvästi**, määritystiedostossa `~/.local/share/vLLM/vllm-launch.conf`. Tätä tiedostoa ei ole oletuksena olemassa — luo se ja lisää argumenttisi Bash-taulukkona:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Käytä `+=`-operaattoria lisätäksesi oletusargumentteihin niiden korvaamisen sijaan:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Nähdäksesi kaikki käynnistimen valinnat milloin tahansa, suorita:

```bash
vllm-launch --help
```

### Missä mallit tallennetaan

`vllm-launch` etsii malleja kahdesta sijainnista:

| Sijainti | Polku |
|----------|------|
| Järjestelmämallit | `/var/cache/models` |
| Käyttäjämallit | `~/.local/share/vLLM/models` |

Voit sijoittaa ladatun mallin kumpaan tahansa hakemistoon ja käynnistää sen antamalla sen polun tai ID:n valitsimelle `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Huomautus**: Oman ladatun mallin suorittamisen tällä tavalla odotetaan toimivan, kun malli on sijoitettu johonkin yllä mainituista hakemistoista, mutta AMD ei ole vielä virallisesti validoinut tätä työnkulkua.

## Vianmääritys

### Yhteys evätty

Varmista, että palvelin on käynnissä:
```bash
curl http://localhost:8001/health
```

## Yhteenveto

Tässä oppaassa opit:

- Käynnistämään konteriloidun vLLM:n ROCm-tuella integroidulla GPU:lla
- Käynnistämään vLLM-palvelimen OpenAI-yhteensopivilla API-päätepisteillä portissa 8001
- Lähettämään kehotteita komennolla `vllm-prompt`
- Tekemään API-kutsuja vLLM-palvelimeen käyttäen sekä suoratoisto- että ei-suoratoistopyyntöjä
- Ratkaisemaan yleisiä ongelmia palvelimen käynnistyksessä, muistissa ja asiakasyhteyksissä

Sinulla on nyt konteriloitu vLLM-käyttöönotto suurten kielimallien palvelemiseen optimoidulla suorituskyvyllä integroidulla GPU:lla.

## Seuraavat vaiheet

- **Kokeile eri malleja** — Käytä komentoa `vllm-launch --model <model>` kokeillaksesi eri LLM-malleja ja vertaillaksesi suorituskykyä (katso [Mallin valitseminen ja määrittäminen](#choosing-and-configuring-a-model)).
- **Rakenna sovellus** — Käytä OpenAI-yhteensopivaa API:a integroidaksesi vLLM:n Python-sovellukseen, chatbottiin tai automaatiotyönkulkuun.
- **Hienosäädä ja palvele** — Hienosäädä mallia käyttäen LoRA:a tai QLoRA:a ja ota se sitten käyttöön vLLM:llä optimoitua päättelyä varten.
## Lisäresurssit

- **[vLLM:n virallinen dokumentaatio](https://docs.vllm.ai/)** — Kattavat oppaat ja API-viitteet
- **[vLLM:n GitHub-repositorio](https://github.com/vllm-project/vllm)** — Lähdekoodi, ongelmat ja yhteisökeskustelut