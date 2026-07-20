<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tässä ohjekirjassa käytetään erikoismerkintöjä, joita GitHub ei pysty renderöimään. Käy osoitteessa [amd.com/playbooks](https://amd.com/playbooks) nähdäksesi tämän sisällön oikein esikatseltuna.
<!-- @github-only:end -->


## Yleiskatsaus

vLLM on suorituskykyinen päättelymoottori, joka on suunniteltu suurten kielimallien (LLM) käyttöön. Se tarjoaa optimoidun palvelun jatkuvalla eräkäsittelyllä suurta suoritustehoa varten sekä OpenAI-yhteensopivan API:n saumatonta sovellusintegraatiota varten. Tämä tekee vLLM:stä erinomaisen tuotantokäyttöönottoihin, joissa nopeus ja resurssitehokkuus ovat kriittisiä.

Tässä ohjekirjassa opit palvelemaan LLM-malleja konteroidun vLLM:n avulla integroidulla GPU:lla ja olemaan vuorovaikutuksessa mallien kanssa OpenAI Python API:n kautta.

## Mitä opit

- Miten vLLM-palvelin määritetään ja käynnistetään AMD ROCm™ -tuella
- Miten mallien kanssa ollaan vuorovaikutuksessa OpenAI-yhteensopivien API-päätepisteiden kautta
- Miten kehotteita lähetetään paikalliselle palvelimelle komennolla `vllm-prompt`

## Muistin määrittäminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

> **Huomautus**: Jos VS Code ei ole asennettuna, voit asentaa sen AMD Ryzen™ AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston edellytysten asentaminen

Tässä ohjekirjassa käytetään valmiiksi rakennettua konttikuvaa, joka sisältää vLLM:n, ROCm-tuen ja palvelimen käynnistämiseen tarvittavat apuskriptit. Sinun ei tarvitse asentaa PyTorchia, vLLM:ää tai paikallisia ohjekirjan skriptejä manuaalisesti.

Isäntäkoneen puolella ei ole erillistä vLLM-asennusvaihetta. Käynnistä vLLM komennolla:

```bash
vllm-launch
```

Käynnistin käynnistää kontin, kohdistaa toiminnan integroituun GPU:hun ja avaa paikallisen OpenAI-yhteensopivan vLLM-palvelimen. Vaihtoehtoisesti voit napsauttaa vLLM-kuvaketta tehtäväpalkissa.

## Pika-aloitus

### 1. Varmista, että vLLM-palvelin on käynnissä

`vllm-launch`-komennon alustus voi kestää pari minuuttia. Kun se on käynnistynyt, palvelin on saatavilla osoitteessa `http://localhost:8001`. Pidä käynnistysterminaali auki, koska palvelin toimii etualalla, ja avaa erillinen terminaali jäljellä oleviin vaiheisiin. Alla olevat esimerkit käyttävät mallia `Qwen/Qwen3-1.7B`; jos käynnistin on määritetty käyttämään eri mallia, korvaa kyseinen malli-ID pyynnöissä.

### 2. Lähetä kehote

Käytä mukana tulevaa `vllm-prompt`-skriptiä pyynnön lähettämiseen paikalliselle vLLM:n OpenAI-yhteensopivalle palvelimelle:

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

Lähetä sitten keskustelun täydennyspyyntö. Tämä käyttää samaa viestimuotoa kuin OpenAI:n API — lista viestejä, joilla on rooleja kuten `"user"` ja `"assistant"`. Asettamalla `stream=True` vastaus saapuu vaiheittain kokonaisen vastauksen sijaan:

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

Lopuksi käy läpi suoratoistetut osat ja tulosta jokainen tekstin pala sitä mukaa kun se saapuu:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Mukana oleva [chat_with_model.py](assets/chat_with_model.py)-skripti sisältää koko esimerkin ja se voidaan ladata.


## Vianmääritys

### Yhteys evätty

Varmista, että palvelin on käynnissä:
```bash
curl http://localhost:8001/health
```

## Yhteenveto

Tässä ohjekirjassa opit, miten:

- Käynnistetään konteroitu vLLM ROCm-tuella integroidulla GPU:lla
- Käynnistetään vLLM-palvelin OpenAI-yhteensopivilla API-päätepisteillä portissa 8001
- Lähetetään kehotteita komennolla `vllm-prompt`
- Tehdään API-kutsuja vLLM-palvelimelle sekä suoratoisto- että ei-suoratoistopyynnöillä
- Ratkaistaan yleisiä ongelmia palvelimen käynnistyksessä, muistissa ja asiakasyhteyksissä

Sinulla on nyt konteroitu vLLM-käyttöönotto suurten kielimallien palvelemiseen optimoidulla suorituskyvyllä integroidulla GPU:lla.

## Seuraavat vaiheet

- **Kokeile eri malleja** — Vaihda mallia `vllm-launch`-määrityksessä kokeillaksesi eri LLM-malleja ja vertaillaksesi suorituskykyä.
- **Rakenna sovellus** — Käytä OpenAI-yhteensopivaa API:a integroidaksesi vLLM:n Python-sovellukseen, chatbotiin tai automaatiotyönkulkuun.
- **Hienosäädä ja palvele** — Hienosäädä mallia käyttäen LoRA:a tai QLoRA:a, ja ota se sitten käyttöön vLLM:llä optimoitua päättelyä varten.

## Lisäresurssit

- **[vLLM:n virallinen dokumentaatio](https://docs.vllm.ai/)** — Kattavat oppaat ja API-viitteet
- **[vLLM:n GitHub-repositorio](https://github.com/vllm-project/vllm)** — Lähdekoodi, ongelmat ja yhteisön keskustelut