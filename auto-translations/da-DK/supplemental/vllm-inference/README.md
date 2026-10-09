<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Oversigt

vLLM er en højtydende inferensmotor designet til store sprogmodeller (LLM'er). Den leverer optimeret servering med kontinuerlig batching for høj gennemstrømning og et OpenAI-kompatibelt API til problemfri applikationsintegration. Det gør vLLM velegnet til produktionsimplementeringer, hvor hastighed og ressourceeffektivitet er afgørende.

Denne playbook lærer dig, hvordan du serverer LLM'er ved hjælp af containeriseret vLLM på den integrerede GPU og interagerer med modeller gennem OpenAI Python API'et.

## Hvad du vil lære

- Hvordan du opsætter og starter en vLLM-server med AMD ROCm™-understøttelse
- Hvordan du interagerer med modeller via OpenAI-kompatible API-endpoints
- Hvordan du sender prompts til den lokale server med `vllm-prompt`

## Indstilling af hukommelseskonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tjek for softwareopdateringer

> **Bemærk**: Hvis VS Code ikke er installeret, kan du installere det med AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger

vLLM kører i en foruddefineret container med ROCm og dens afhængigheder allerede matchet. Ingen yderligere installation er nødvendig.

Der er intet installationstrin for vLLM på værten. Start vLLM med:

```bash
vllm-launch
```

Launcheren starter containeren, retter sig mod den integrerede GPU og eksponerer en lokal OpenAI-kompatibel vLLM-server. Alternativt kan du klikke på vLLM-ikonet i proceslinjen.

## Hurtig start

### 1. Bekræft, at vLLM-serveren kører

`vllm-launch` kan tage et par minutter om at initialisere alt. Når den er startet, er serveren tilgængelig på `http://localhost:8001`. Hold launch-terminalen åben, da serveren kører i forgrunden, og åbn derefter en separat terminal til de resterende trin. Eksemplerne nedenfor bruger `Qwen/Qwen3-1.7B`; hvis din launcher er konfigureret til en anden model, skal du erstatte det pågældende model-ID i anmodningerne.

### 2. Send en prompt

Brug det medfølgende `vllm-prompt`-script til at sende en anmodning til den lokale, OpenAI-kompatible vLLM-server:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chat med modellen ved hjælp af OpenAI Python API

Da vLLM eksponerer et OpenAI-kompatibelt API, kan du bruge `openai` Python-pakken til at interagere med det.

Opret først et Python-virtuelt miljø:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->

Installer OpenAI-pakken
```bash
pip install openai
```

Opret en `OpenAI`-klient, der peger på den lokale vLLM-server i stedet for OpenAI's servere. `api_key` er påkrævet af klienten, men vLLM validerer den ikke, så enhver streng fungerer:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Send derefter en chat completion-anmodning. Denne bruger det samme beskedformat som OpenAI API'et — en liste af beskeder med roller som `"user"` og `"assistant"`. Hvis du sætter `stream=True`, betyder det, at svaret ankommer trinvist i stedet for alt på én gang:

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

Til sidst iterer du over de streamede chunks og udskriver hver stykke tekst, efterhånden som den ankommer:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Det medfølgende [chat_with_model.py](assets/chat_with_model.py)-script indeholder hele eksemplet og kan downloades.


## Valg og konfiguration af en model

Som standard serverer `vllm-launch` `Qwen/Qwen3-1.7B` som testmodel på port `8001`. Du kan ændre modellen, porten og vLLM-serveringsparametrene uden at genbygge eller redigere containeren.

### Modeller testet af AMD

Følgende modeller er forudkonfigureret og valideret af AMD:

| Model | Noter |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Standardmodel. Letvægts og hurtig at indlæse. |
| `openai/gpt-oss-20b` | Større model til svar af højere kvalitet. |

### Start af en anden model

Angiv model-ID'et med `--model` (eller `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Ændring af porten

Angiv en port over 1024 med `--port` (eller `-p`); standarden er `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Hvis du ændrer porten, skal du pege din klients `base_url` på den samme port (for eksempel `http://localhost:8080/v1`).

### Angivelse af ekstra vLLM-parametre

Alle yderligere argumenter videresendes direkte til vLLM, så du kan finjustere serveringsadfærd som f.eks. kontekstlængde eller datatype. Der er to måder at angive dem på.

**Inline**, efter launcher-indstillingerne:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Permanent**, i en konfigurationsfil på `~/.local/share/vLLM/vllm-launch.conf`. Denne fil findes ikke som standard — opret den, og tilføj dine argumenter som et Bash-array:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Brug `+=` for at tilføje til standardargumenterne i stedet for at erstatte dem:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Hvis du vil se alle launcher-indstillinger på et hvilket som helst tidspunkt, skal du køre:

```bash
vllm-launch --help
```

### Hvor modeller er gemt

`vllm-launch` leder efter modeller på to steder:

| Placering | Sti |
|----------|------|
| Systemmodeller | `/var/cache/models` |
| Brugermodeller | `~/.local/share/vLLM/models` |

Du kan placere en downloadet model i en af mapperne og starte den ved at angive dens sti eller ID til `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Bemærk**: Det forventes, at det virker at køre din egen downloadede model på denne måde, når modellen er placeret i en af mapperne ovenfor, men denne arbejdsgang er endnu ikke officielt valideret af AMD.

## Fejlfinding

### Forbindelse afvist

Sørg for, at serveren kører:
```bash
curl http://localhost:8001/health
```

## Opsummering

I denne playbook lærte du, hvordan du:

- Starter containeriseret vLLM med ROCm-understøttelse på den integrerede GPU
- Starter en vLLM-server med OpenAI-kompatible API-endpoints på port 8001
- Sender prompts med `vllm-prompt`
- Foretager API-kald til vLLM-serveren ved hjælp af både streaming- og ikke-streaming-anmodninger
- Fejlfinder almindelige problemer med serverstart, hukommelse og klientforbindelser

Du har nu en containeriseret vLLM-implementering til servering af store sprogmodeller med optimeret ydeevne på den integrerede GPU.

## Næste skridt

- **Prøv forskellige modeller** — Brug `vllm-launch --model <model>` til at eksperimentere med forskellige LLM'er og sammenligne ydeevne (se [Valg og konfiguration af en model](#choosing-and-configuring-a-model)).
- **Byg en applikation** — Brug det OpenAI-kompatible API til at integrere vLLM i en Python-app, chatbot eller automatiseringsworkflow.
- **Finjustér og server** — Finjustér en model ved hjælp af LoRA eller QLoRA, og implementér den derefter med vLLM til optimeret inferens.
## Yderligere ressourcer

- **[vLLM officiel dokumentation](https://docs.vllm.ai/)** — Omfattende guides og API-referencer
- **[vLLM GitHub-repository](https://github.com/vllm-project/vllm)** — Kildekode, problemer og community-diskussioner