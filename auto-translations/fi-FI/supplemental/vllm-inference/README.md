<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tämä playbook käyttää erityistunnisteita, joita GitHub ei pysty renderöimään. Katso sisältö oikein osoitteessa [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->


## Yleiskatsaus

vLLM on suorituskykyinen päättelykone, joka on suunniteltu suurille kielimalleille (LLM). Se tarjoaa optimoidun palvelun jatkuvalla eräajolla korkean suorituskyvyn saavuttamiseksi sekä OpenAI-yhteensopivan API:n saumattomaan sovellusintegraatioon. Tämä tekee vLLM:stä erinomaisen valinnan tuotantokäyttöönottoon, jossa nopeus ja resurssitehokkuus ovat kriittisiä.

Tämä playbook opettaa sinulle, kuinka LLM-malleja palvellaan kontitetun vLLM:n avulla integroidulla GPU:lla ja kuinka mallien kanssa ollaan vuorovaikutuksessa OpenAI Python API:n kautta.

## Mitä opit

- Kuinka vLLM-palvelin asetetaan ja käynnistetään AMD ROCm™-tuella
- Kuinka mallien kanssa ollaan vuorovaikutuksessa OpenAI-yhteensopivien API-päätepisteiden kautta
- Kuinka kehotteita lähetetään paikalliselle palvelimelle `vllm-prompt`-komennolla

## Muistikonfiguraation asettaminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

> **Huomio**: Jos VS Code ei ole asennettuna, voit asentaa sen AMD Ryzen™ AI Developer Centerin avulla.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmistoedellytysten asentaminen

Tämä playbook käyttää valmiiksi rakennettua konttikuvaa, joka sisältää vLLM:n, ROCm-tuen ja palvelimen käynnistämiseen tarvittavat apuskriptit. Sinun ei tarvitse asentaa PyTorchia, vLLM:ää tai paikallisia playbook-skriptejä manuaalisesti.

Isäntäpuolella ei ole vLLM-asennusvaihetta. Käynnistä vLLM komennolla:

```bash
vllm-launch
```

Käynnistysohjelma käynnistää kontin, kohdistaa integroituun GPU:hun ja avaa paikallisen OpenAI-yhteensopivan vLLM-palvelimen. Vaihtoehtoisesti voit napsauttaa vLLM-kuvaketta tehtäväpalkissa.

## Pikaopas

### 1. Varmista, että vLLM-palvelin on käynnissä

`vllm-launch`-komennon kaiken alustaminen voi kestää muutaman minuutin. Kun se käynnistyy, palvelin on saatavilla osoitteessa `http://localhost:8001`. Pidä käynnistystermiaali auki, koska palvelin toimii etualalla, ja avaa sitten erillinen terminaali jäljellä olevia vaiheita varten. Alla olevissa esimerkeissä käytetään `Qwen/Qwen3-1.7B`-mallia; jos käynnistysohjelmasi on konfiguroitu eri mallille, korvaa kyseinen malli-ID pyynnöissä.

### 2. Lähetä kehote

Käytä tarjottua `vllm-prompt`-skriptiä lähettääksesi pyynnön paikalliselle vLLM OpenAI-yhteensopivalle palvelimelle:

```bash
vllm-prompt "Tell me a story"
```

### 3. Keskustele mallin kanssa OpenAI Python API:n avulla

Koska vLLM tarjoaa OpenAI-yhteensopivan API:n, voit käyttää `openai` Python-pakettia vuorovaikutukseen sen kanssa.

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

Luo `OpenAI`-asiakas, joka osoittaa paikalliseen vLLM-palvelimeen OpenAI:n palvelimien sijaan. `api_key` on asiakkaan vaatima, mutta vLLM ei validoi sitä, joten mikä tahansa merkkijono toimii:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Lähetä sitten chat-täydennyspyyntö. Tässä käytetään samaa viestimuotoa kuin OpenAI API:ssa — lista viestejä rooleilla kuten `"user"` ja `"assistant"`. `stream=True`-asetus tarkoittaa, että vastaus saapuu vähitellen eikä kerralla:

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

Iteroi lopuksi virtautettujen osien yli ja tulosta jokainen tekstinpätkä sitä mukaa kuin se saapuu:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Mukana oleva [chat_with_model.py](assets/chat_with_model.py)-skripti sisältää koko esimerkin ja on ladattavissa.


## Vianmääritys

### Yhteys evätty

Varmista, että palvelin on käynnissä:
```bash
curl http://localhost:8001/health
```

## Yhteenveto

Tässä playbookissa opit:

- Käynnistämään kontitetun vLLM:n ROCm-tuella integroidulla GPU:lla
- Käynnistämään vLLM-palvelimen OpenAI-yhteensopivilla API-päätepisteillä portissa 8001
- Lähettämään kehotteita `vllm-prompt`-komennolla
- Tekemään API-kutsuja vLLM-palvelimelle sekä virtautus- että ei-virtautuspyynöillä
- Vianmäärittämään yleisiä ongelmia palvelimen käynnistyksen, muistin ja asiakasyhteyksien kanssa

Sinulla on nyt kontitettu vLLM-käyttöönotto suurten kielimallien palvelemiseen optimoidulla suorituskyvyllä integroidulla GPU:lla.

## Seuraavat vaiheet

- **Kokeile eri malleja** — Vaihda malli `vllm-launch`-konfiguraatiossa kokeillaksesi eri LLM-malleja ja vertaillaksesi suorituskykyä.
- **Rakenna sovellus** — Käytä OpenAI-yhteensopivaa API:a integroidaksesi vLLM:n Python-sovellukseen, chatbottiin tai automaatiotyönkulkuun.
- **Hienosäädä ja palvele** — Hienosäädä malli LoRA:n tai QLoRA:n avulla ja ota se sitten käyttöön vLLM:llä optimoitua päättelyä varten.

## Lisäresurssit

- **[vLLM:n virallinen dokumentaatio](https://docs.vllm.ai/)** — Kattavat oppaat ja API-viitteet
- **[vLLM GitHub-repositorio](https://github.com/vllm-project/vllm)** — Lähdekoodi, ongelmat ja yhteisökeskustelut