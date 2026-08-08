<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Oversikt

vLLM er en høytytende inferensmotor designet for store språkmodeller (LLM-er). Den tilbyr optimalisert servering med kontinuerlig batching for høy gjennomstrømning og et OpenAI-kompatibelt API for sømløs applikasjonsintegrasjon. Dette gjør vLLM godt egnet for produksjonsdistribusjoner hvor hastighet og ressurseffektivitet er kritisk.

Denne veiledningen lærer deg hvordan du serverer LLM-er ved hjelp av containerisert vLLM på den integrerte GPU-en og hvordan du samhandler med modeller gjennom OpenAI Python API.

## Hva du vil lære

- Hvordan du setter opp og starter en vLLM-server med AMD ROCm™-støtte
- Hvordan du samhandler med modeller via OpenAI-kompatible API-endepunkter
- Hvordan du sender forespørsler til den lokale serveren med `vllm-prompt`

## Konfigurere minnet

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sjekk etter programvareoppdateringer

> **Merk**: Hvis VS Code ikke er installert, kan du installere det med AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installere forutsetninger for programvare

vLLM kjører i en forhåndsbygget container med ROCm og dens avhengigheter allerede tilpasset. Ingen ytterligere installasjon kreves.

Det er ikke noe installasjonstrinn for vLLM på vertsmaskinen. Start vLLM med:

```bash
vllm-launch
```

Startprogrammet starter containeren, retter seg mot den integrerte GPU-en, og eksponerer en lokal OpenAI-kompatibel vLLM-server. Alternativt kan du klikke på vLLM-ikonet i oppgavelinjen.

## Hurtigstart

### 1. Bekreft at vLLM-serveren kjører

`vllm-launch` kan ta et par minutter å initialisere alt. Når den starter, er serveren tilgjengelig på `http://localhost:8001`. Hold lanseringsterminalen åpen fordi serveren kjører i forgrunnen, og åpne deretter en separat terminal for de gjenværende trinnene. Eksemplene nedenfor bruker `Qwen/Qwen3-1.7B`; hvis startprogrammet ditt er konfigurert for en annen modell, erstatt den modell-ID-en i forespørslene.

### 2. Send en forespørsel

Bruk det medfølgende `vllm-prompt`-skriptet for å sende en forespørsel til den lokale OpenAI-kompatible vLLM-serveren:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chat med modellen ved hjelp av OpenAI Python API

Siden vLLM eksponerer et OpenAI-kompatibelt API, kan du bruke `openai` Python-pakken for å samhandle med den.

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

Opprett en `OpenAI`-klient som peker mot den lokale vLLM-serveren i stedet for OpenAIs servere. `api_key` kreves av klienten, men vLLM validerer den ikke, så hvilken som helst streng fungerer:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Send deretter en chat completion-forespørsel. Denne bruker samme meldingsformat som OpenAI API-et — en liste med meldinger med roller som `"user"` og `"assistant"`. Ved å sette `stream=True` vil svaret komme trinnvis i stedet for alt på én gang:

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

Til slutt, gå gjennom de strømmede delene og skriv ut hver tekstbit etter hvert som den ankommer:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Det medfølgende [chat_with_model.py](assets/chat_with_model.py)-skriptet inneholder hele eksempelet og kan lastes ned.


## Velge og konfigurere en modell

Som standard serverer `vllm-launch` `Qwen/Qwen3-1.7B` som en testmodell på port `8001`. Du kan endre modellen, porten og vLLM-serveringsparametrene uten å bygge om eller redigere containeren på nytt.

### Modeller testet av AMD

Følgende modeller er forhåndskonfigurert og validert av AMD:

| Modell | Merknader |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Standardmodell. Lettvekts og rask å laste. |
| `openai/gpt-oss-20b` | Større modell for svar av høyere kvalitet. |

### Starte en annen modell

Send modell-ID-en med `--model` (eller `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Endre porten

Send en port over 1024 med `--port` (eller `-p`); standarden er `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Hvis du endrer porten, må du peke klientens `base_url` til den samme porten (for eksempel `http://localhost:8080/v1`).

### Sende ekstra vLLM-parametre

Eventuelle ytterligere argumenter videresendes direkte til vLLM, slik at du kan justere serveringsatferd som kontekstlengde eller datatype. Det finnes to måter å oppgi dem på.

**Inline**, etter startprogramalternativene:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Vedvarende**, i en konfigurasjonsfil på `~/.local/share/vLLM/vllm-launch.conf`. Denne filen finnes ikke som standard — opprett den og legg til argumentene dine som en Bash-array:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Bruk `+=` for å legge til standardargumentene i stedet for å erstatte dem:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

For å se alle startprogramalternativer når som helst, kjør:

```bash
vllm-launch --help
```

### Hvor modeller lagres

`vllm-launch` ser etter modeller på to steder:

| Plassering | Sti |
|----------|------|
| Systemmodeller | `/var/cache/models` |
| Brukermodeller | `~/.local/share/vLLM/models` |

Du kan plassere en nedlastet modell i én av mappene og starte den ved å sende stien eller ID-en til `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Merk**: Å kjøre din egen nedlastede modell på denne måten forventes å fungere når modellen er plassert i én av mappene ovenfor, men denne arbeidsflyten er ennå ikke offisielt validert av AMD.

## Feilsøking

### Tilkobling avvist

Sørg for at serveren kjører:
```bash
curl http://localhost:8001/health
```

## Oppsummering

I denne veiledningen lærte du hvordan du:

- Starter containerisert vLLM med ROCm-støtte på den integrerte GPU-en
- Starter en vLLM-server med OpenAI-kompatible API-endepunkter på port 8001
- Sender forespørsler med `vllm-prompt`
- Utfører API-kall til vLLM-serveren ved hjelp av både strømmede og ikke-strømmede forespørsler
- Feilsøker vanlige problemer med serveroppstart, minne og klienttilkoblinger

Du har nå en containerisert vLLM-distribusjon for å servere store språkmodeller med optimalisert ytelse på den integrerte GPU-en.

## Neste steg

- **Prøv forskjellige modeller** — Bruk `vllm-launch --model <model>` for å eksperimentere med forskjellige LLM-er og sammenligne ytelse (se [Velge og konfigurere en modell](#choosing-and-configuring-a-model)).
- **Bygg en applikasjon** — Bruk det OpenAI-kompatible API-et for å integrere vLLM i en Python-app, chatbot eller automatiseringsarbeidsflyt.
- **Finjuster og server** — Finjuster en modell med LoRA eller QLoRA, og distribuer den deretter med vLLM for optimalisert inferens.
## Ytterligere ressurser

- **[Offisiell vLLM-dokumentasjon](https://docs.vllm.ai/)** — Omfattende veiledninger og API-referanser
- **[vLLM GitHub-repositorium](https://github.com/vllm-project/vllm)** — Kildekode, saker og fellesskapsdiskusjoner