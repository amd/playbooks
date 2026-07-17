<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Dit playbook gebruikt speciale tags die GitHub niet kan weergeven. Bezoek [amd.com/playbooks](https://amd.com/playbooks) om deze inhoud correct te bekijken.
<!-- @github-only:end -->


## Overzicht

vLLM is een krachtige inference-engine ontworpen voor grote taalmodellen (LLM's). Het biedt geoptimaliseerde serving met continue batching voor hoge doorvoer en een OpenAI-compatibele API voor naadloze applicatie-integratie. Dit maakt vLLM uitstekend geschikt voor productie-implementaties waarbij snelheid en resource-efficiëntie cruciaal zijn.

Dit playbook leert je hoe je LLM's kunt serveren met behulp van gecontaineriseerde vLLM op de geïntegreerde GPU en hoe je via de OpenAI Python API met modellen kunt communiceren.

## Wat Je Leert

- Hoe je een vLLM-server instelt en start met AMD ROCm™-ondersteuning
- Hoe je via OpenAI-compatibele API-eindpunten met modellen communiceert
- Hoe je prompts naar de lokale server stuurt met `vllm-prompt`

## De Geheugenconfiguratie Instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op Software-updates

> **Opmerking**: Als VS Code niet is geïnstalleerd, kun je het installeren via het AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Softwarevereisten Installeren

Dit playbook maakt gebruik van een vooraf gebouwde containerimage die vLLM, ROCm-ondersteuning en de hulpscripts bevat die nodig zijn om de server te starten. Je hoeft PyTorch, vLLM of lokale playbook-scripts niet handmatig te installeren.

Er is geen vLLM-installatiestap aan de hostzijde. Start vLLM met:

```bash
vllm-launch
```

De launcher start de container, richt zich op de geïntegreerde GPU en stelt een lokale OpenAI-compatibele vLLM-server beschikbaar. Je kunt ook op het vLLM-pictogram in de taakbalk klikken.

## Snel Starten

### 1. Bevestig dat de vLLM-server Actief Is

Het kan een paar minuten duren voordat `vllm-launch` alles heeft geïnitialiseerd. Zodra het is gestart, is de server beschikbaar op `http://localhost:8001`. Houd de launchterminal open omdat de server op de voorgrond draait, en open vervolgens een aparte terminal voor de overige stappen. De onderstaande voorbeelden gebruiken `Qwen/Qwen3-1.7B`; als je launcher is geconfigureerd voor een ander model, vervang dan dat model-ID in de verzoeken.

### 2. Een Prompt Versturen

Gebruik het meegeleverde `vllm-prompt`-script om een verzoek te sturen naar de lokale OpenAI-compatibele vLLM-server:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chatten met het model via de OpenAI Python API

Omdat vLLM een OpenAI-compatibele API blootstelt, kun je het `openai` Python-pakket gebruiken om ermee te communiceren.

Maak eerst een virtuele Python-omgeving aan:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Installeer het OpenAI-pakket
```bash
pip install openai
```

Maak een `OpenAI`-client aan die verwijst naar de lokale vLLM-server in plaats van de servers van OpenAI. De `api_key` is vereist door de client, maar vLLM valideert deze niet, dus elke willekeurige string werkt:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Stuur vervolgens een chat-completion-verzoek. Dit gebruikt hetzelfde berichtformaat als de OpenAI API — een lijst van berichten met rollen zoals `"user"` en `"assistant"`. Het instellen van `stream=True` betekent dat het antwoord stapsgewijs aankomt in plaats van alles tegelijk:

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

Itereer ten slotte over de gestreamde fragmenten en druk elk stuk tekst af zodra het binnenkomt:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Het meegeleverde [chat_with_model.py](assets/chat_with_model.py)-script bevat het volledige voorbeeld en kan worden gedownload.


## Probleemoplossing

### Verbinding geweigerd

Zorg ervoor dat de server actief is:
```bash
curl http://localhost:8001/health
```

## Samenvatting

In dit playbook heb je geleerd hoe je:

- Gecontaineriseerde vLLM met ROCm-ondersteuning start op de geïntegreerde GPU
- Een vLLM-server start met OpenAI-compatibele API-eindpunten op poort 8001
- Prompts verstuurt met `vllm-prompt`
- API-aanroepen doet naar de vLLM-server met zowel streaming- als niet-streaming-verzoeken
- Veelvoorkomende problemen oplost met het opstarten van de server, geheugen en clientverbindingen

Je beschikt nu over een gecontaineriseerde vLLM-implementatie voor het serveren van grote taalmodellen met geoptimaliseerde prestaties op de geïntegreerde GPU.

## Volgende Stappen

- **Probeer verschillende modellen** — Wissel het model in de `vllm-launch`-configuratie om te experimenteren met verschillende LLM's en prestaties te vergelijken.
- **Bouw een applicatie** — Gebruik de OpenAI-compatibele API om vLLM te integreren in een Python-app, chatbot of automatiseringsworkflow.
- **Verfijn en serveer** — Verfijn een model met LoRA of QLoRA en implementeer het vervolgens met vLLM voor geoptimaliseerde inference.

## Aanvullende Bronnen

- **[vLLM Officiële Documentatie](https://docs.vllm.ai/)** — Uitgebreide handleidingen en API-referenties
- **[vLLM GitHub Repository](https://github.com/vllm-project/vllm)** — Broncode, problemen en communitydiscussies