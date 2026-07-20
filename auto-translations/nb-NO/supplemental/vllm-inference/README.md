<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Denne oppskriften bruker spesielle tagger som GitHub ikke kan gjengi. Besøk [amd.com/playbooks](https://amd.com/playbooks) for å forhåndsvise dette innholdet på riktig måte.
<!-- @github-only:end -->


## Oversikt

vLLM er en høytytende inferensmotor designet for store språkmodeller (LLM-er). Den tilbyr optimalisert servering med kontinuerlig batching for høy gjennomstrømning og et OpenAI-kompatibelt API for sømløs applikasjonsintegrasjon. Dette gjør vLLM godt egnet for produksjonsdistribusjoner hvor hastighet og ressurseffektivitet er avgjørende.

Denne oppskriften lærer deg hvordan du server LLM-er ved hjelp av containerisert vLLM på det integrerte GPU-et og samhandler med modeller gjennom OpenAI Python API.

## Hva du vil lære

- Hvordan sette opp og starte en vLLM-server med AMD ROCm™-støtte
- Hvordan samhandle med modeller via OpenAI-kompatible API-endepunkter
- Hvordan sende ledetekster til den lokale serveren med `vllm-prompt`

## Konfigurere minne

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Se etter programvareoppdateringer

> **Merk**: Hvis VS Code ikke er installert, kan du installere det med AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installere nødvendig programvare

Denne oppskriften bruker et forhåndsbygget containerbilde som inkluderer vLLM, ROCm-støtte, og hjelpeskriptene som trengs for å starte serveren. Du trenger ikke å installere PyTorch, vLLM eller lokale oppskriftsskript manuelt.

Det er ikke noe trinn for vLLM-installasjon på verten. Start vLLM med:

```bash
vllm-launch
```

Starteren starter containeren, retter seg mot det integrerte GPU-et, og eksponerer en lokal OpenAI-kompatibel vLLM-server. Alternativt kan du klikke på vLLM-ikonet i oppgavelinjen.

## Hurtigstart

### 1. Bekreft at vLLM-serveren kjører

`vllm-launch` kan ta et par minutter på å initialisere alt. Når den starter, er serveren tilgjengelig på `http://localhost:8001`. Hold lanseringsterminalen åpen fordi serveren kjører i forgrunnen, og åpne deretter en separat terminal for de resterende trinnene. Eksemplene nedenfor bruker `Qwen/Qwen3-1.7B`; hvis starteren din er konfigurert for en annen modell, sett inn den modell-ID-en i forespørslene.

### 2. Send en ledetekst

Bruk det medfølgende `vllm-prompt`-skriptet til å sende en forespørsel til den lokale vLLM OpenAI-kompatible serveren:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chat med modellen ved hjelp av OpenAI Python API

Siden vLLM eksponerer et OpenAI-kompatibelt API, kan du bruke `openai`-Python-pakken til å samhandle med det.

Opprett først et virtuelt Python-miljø:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Installer OpenAI-pakken
```bash
pip install openai
```

Opprett en `OpenAI`-klient som peker mot den lokale vLLM-serveren i stedet for OpenAIs servere. `api_key` er påkrevd av klienten, men vLLM validerer den ikke, så enhver streng fungerer:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Send deretter en chat-fullføringsforespørsel. Dette bruker samme meldingsformat som OpenAI API — en liste med meldinger med roller som `"user"` og `"assistant"`. Ved å sette `stream=True` vil svaret komme inkrementelt i stedet for alt på én gang:

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

Til slutt, gå gjennom de strømmede bitene og skriv ut hver tekstbit etter hvert som den ankommer:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Det medfølgende [chat_with_model.py](assets/chat_with_model.py)-skriptet inneholder hele eksempelet og kan lastes ned.


## Feilsøking

### Tilkobling avvist

Sørg for at serveren kjører:
```bash
curl http://localhost:8001/health
```

## Sammendrag

I denne oppskriften lærte du hvordan du:

- Starter containerisert vLLM med ROCm-støtte på det integrerte GPU-et
- Starter en vLLM-server med OpenAI-kompatible API-endepunkter på port 8001
- Sender ledetekster med `vllm-prompt`
- Gjør API-kall til vLLM-serveren ved bruk av både strømmende og ikke-strømmende forespørsler
- Feilsøker vanlige problemer med serverstart, minne og klienttilkoblinger

Du har nå en containerisert vLLM-distribusjon for servering av store språkmodeller med optimalisert ytelse på det integrerte GPU-et.

## Neste steg

- **Prøv forskjellige modeller** — Bytt ut modellen i `vllm-launch`-konfigurasjonen for å eksperimentere med ulike LLM-er og sammenligne ytelse.
- **Bygg en applikasjon** — Bruk det OpenAI-kompatible API-et til å integrere vLLM i en Python-app, chatbot, eller automatiseringsarbeidsflyt.
- **Finjuster og server** — Finjuster en modell ved hjelp av LoRA eller QLoRA, og distribuer den deretter med vLLM for optimalisert inferens.

## Flere ressurser

- **[Offisiell vLLM-dokumentasjon](https://docs.vllm.ai/)** — Omfattende veiledninger og API-referanser
- **[vLLM GitHub-repositorium](https://github.com/vllm-project/vllm)** — Kildekode, saker, og fellesskapsdiskusjoner