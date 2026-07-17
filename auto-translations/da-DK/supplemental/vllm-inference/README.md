<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Oversigt

vLLM er en højtydende inferensmotor designet til store sprogmodeller (LLM'er). Den leverer optimeret servering med kontinuerlig batching for høj gennemstrømning og en OpenAI-kompatibel API til problemfri applikationsintegration. Dette gør vLLM ideel til produktionsinstallationer, hvor hastighed og ressourceeffektivitet er afgørende.

Dette playbook lærer dig, hvordan du serverer LLM'er ved hjælp af containeriseret vLLM på den integrerede GPU og interagerer med modeller via OpenAI Python API.

## Hvad du vil lære

- Sådan opsætter og starter du en vLLM-server med AMD ROCm™-understøttelse
- Sådan interagerer du med modeller via OpenAI-kompatible API-endepunkter
- Sådan sender du prompter til den lokale server med `vllm-prompt`

## Indstilling af hukommelseskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tjek for softwareopdateringer

> **Bemærk**: Hvis VS Code ikke er installeret, kan du installere det med AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger

Dette playbook bruger et færdigbygget container-image, der inkluderer vLLM, ROCm-understøttelse og de hjælpescripts, der er nødvendige for at starte serveren. Du behøver ikke at installere PyTorch, vLLM eller lokale playbook-scripts manuelt.

Der er intet vLLM-installationstrin på værtssiden. Start vLLM med:

```bash
vllm-launch
```

Starteren starter containeren, målretter den integrerede GPU og eksponerer en lokal OpenAI-kompatibel vLLM-server. Alternativt kan du klikke på vLLM-ikonet i proceslinjen.

## Hurtig start

### 1. Bekræft at vLLM-serveren kører

`vllm-launch` kan tage et par minutter at initialisere alt. Når den starter, er serveren tilgængelig på `http://localhost:8001`. Hold startterminalen åben, da serveren kører i forgrunden, og åbn derefter en separat terminal til de resterende trin. Eksemplerne nedenfor bruger `Qwen/Qwen3-1.7B`; hvis din starter er konfigureret til en anden model, skal du erstatte det pågældende model-ID i anmodningerne.

### 2. Send en prompt

Brug det medfølgende `vllm-prompt`-script til at sende en anmodning til den lokale vLLM OpenAI-kompatible server:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chat med modellen ved hjælp af OpenAI Python API

Da vLLM eksponerer en OpenAI-kompatibel API, kan du bruge `openai` Python-pakken til at interagere med den.

Opret først et virtuelt Python-miljø:

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

Opret en `OpenAI`-klient, der peger på den lokale vLLM-server i stedet for OpenAI's servere. `api_key` er påkrævet af klienten, men vLLM validerer den ikke, så enhver streng fungerer:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Send derefter en chat-fuldførelsesanmodning. Dette bruger samme meddelelsesformat som OpenAI API — en liste over meddelelser med roller som `"user"` og `"assistant"`. Indstilling af `stream=True` betyder, at svaret ankommer trinvist frem for alt på én gang:

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

Til sidst skal du iterere over de streamede bidder og udskrive hvert tekststykke, efterhånden som det ankommer:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Det medfølgende [chat_with_model.py](assets/chat_with_model.py)-script indeholder hele eksemplet og kan downloades.


## Fejlfinding

### Forbindelse afvist

Sørg for, at serveren kører:
```bash
curl http://localhost:8001/health
```

## Opsummering

I dette playbook lærte du, hvordan du:

- Starter containeriseret vLLM med ROCm-understøttelse på den integrerede GPU
- Starter en vLLM-server med OpenAI-kompatible API-endepunkter på port 8001
- Sender prompter med `vllm-prompt`
- Foretager API-kald til vLLM-serveren ved hjælp af både streaming- og ikke-streaming-anmodninger
- Fejlfinder almindelige problemer med serveropstart, hukommelse og klientforbindelser

Du har nu en containeriseret vLLM-installation til servering af store sprogmodeller med optimeret ydeevne på den integrerede GPU.

## Næste skridt

- **Prøv forskellige modeller** — Skift modellen i `vllm-launch`-konfigurationen for at eksperimentere med forskellige LLM'er og sammenligne ydeevne.
- **Byg en applikation** — Brug den OpenAI-kompatible API til at integrere vLLM i en Python-app, chatbot eller automatiseringsworkflow.
- **Finjuster og server** — Finjuster en model ved hjælp af LoRA eller QLoRA, og deploy den derefter med vLLM til optimeret inferens.

## Yderligere ressourcer

- **[vLLM officiel dokumentation](https://docs.vllm.ai/)** — Omfattende vejledninger og API-referencer
- **[vLLM GitHub-repository](https://github.com/vllm-project/vllm)** — Kildekode, problemer og fællesskabsdiskussioner