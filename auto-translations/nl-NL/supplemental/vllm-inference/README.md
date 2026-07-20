<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Deze playbook maakt gebruik van speciale tags die GitHub niet kan weergeven. Bezoek [amd.com/playbooks](https://amd.com/playbooks) om deze inhoud correct te bekijken.
<!-- @github-only:end -->


## Overzicht

vLLM is een krachtige inference-engine ontworpen voor grote taalmodellen (LLM's). Het biedt geoptimaliseerde serving met continuous batching voor een hoge doorvoer en een OpenAI-compatibele API voor naadloze applicatie-integratie. Dit maakt vLLM uitstekend geschikt voor productieomgevingen waarin snelheid en efficiënt gebruik van resources cruciaal zijn.

Deze playbook leert je hoe je LLM's serveert met behulp van gecontaineriseerde vLLM op de geïntegreerde GPU en hoe je met modellen kunt communiceren via de OpenAI Python API.

## Wat Je Zult Leren

- Hoe je een vLLM-server opzet en start met ondersteuning voor AMD ROCm™
- Hoe je communiceert met modellen via OpenAI-compatibele API-eindpunten
- Hoe je prompts naar de lokale server stuurt met `vllm-prompt`

## De Geheugenconfiguratie Instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op Software-updates

> **Opmerking**: Als VS Code niet is geïnstalleerd, kun je het installeren met AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Software-vereisten Installeren

Deze playbook maakt gebruik van een vooraf gebouwde container-image die vLLM, ROCm-ondersteuning en de hulpscripts bevat die nodig zijn om de server te starten. Je hoeft PyTorch, vLLM of lokale playbook-scripts niet handmatig te installeren.

Er is geen stap voor vLLM-installatie op de host. Start vLLM met:

```bash
vllm-launch
```

De launcher start de container, richt zich op de geïntegreerde GPU en stelt een lokale OpenAI-compatibele vLLM-server beschikbaar. Klik als alternatief op het vLLM-icoon in de taakbalk.

## Snel Aan de Slag

### 1. Bevestig Dat de vLLM-server Actief Is

Het kan een paar minuten duren voordat `vllm-launch` alles heeft geïnitialiseerd. Zodra de server start, is deze beschikbaar op `http://localhost:8001`. Houd de terminal waarin de server is gestart open, aangezien de server op de voorgrond draait, en open vervolgens een aparte terminal voor de resterende stappen. De onderstaande voorbeelden gebruiken `Qwen/Qwen3-1.7B`; als je launcher is geconfigureerd voor een ander model, vervang dan dat model-ID in de verzoeken.

### 2. Verstuur een Prompt

Gebruik het meegeleverde `vllm-prompt`-script om een verzoek te sturen naar de lokale OpenAI-compatibele vLLM-server:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chat met het model met behulp van de OpenAI Python API

Aangezien vLLM een OpenAI-compatibele API beschikbaar stelt, kun je het `openai` Python-pakket gebruiken om ermee te communiceren.

Maak eerst een Python virtuele omgeving aan:

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

Maak een `OpenAI`-client aan die verwijst naar de lokale vLLM-server in plaats van naar de servers van OpenAI. De `api_key` is vereist door de client, maar vLLM valideert deze niet, dus elke tekenreeks werkt:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Verstuur vervolgens een chat completion-verzoek. Dit gebruikt hetzelfde berichtformaat als de OpenAI API — een lijst met berichten met rollen zoals `"user"` en `"assistant"`. Door `stream=True` in te stellen, komt het antwoord stapsgewijs binnen in plaats van in één keer:

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

Loop ten slotte door de gestreamde chunks en print elk stukje tekst zodra het binnenkomt:

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

In deze playbook heb je geleerd hoe je:

- Gecontaineriseerde vLLM start met ROCm-ondersteuning op de geïntegreerde GPU
- Een vLLM-server start met OpenAI-compatibele API-eindpunten op poort 8001
- Prompts verstuurt met `vllm-prompt`
- API-aanroepen doet naar de vLLM-server met zowel streaming als niet-streaming verzoeken
- Veelvoorkomende problemen oplost met het opstarten van de server, geheugen en clientverbindingen

Je beschikt nu over een gecontaineriseerde vLLM-implementatie voor het serveren van grote taalmodellen met geoptimaliseerde prestaties op de geïntegreerde GPU.

## Volgende Stappen

- **Probeer verschillende modellen** — Wissel het model in de `vllm-launch`-configuratie om te experimenteren met verschillende LLM's en de prestaties te vergelijken.
- **Bouw een applicatie** — Gebruik de OpenAI-compatibele API om vLLM te integreren in een Python-app, chatbot of automatiseringsworkflow.
- **Fine-tune en serveer** — Fine-tune een model met LoRA of QLoRA, en implementeer het vervolgens met vLLM voor geoptimaliseerde inference.

## Aanvullende Bronnen

- **[Officiële vLLM-documentatie](https://docs.vllm.ai/)** — Uitgebreide handleidingen en API-referenties
- **[vLLM GitHub-repository](https://github.com/vllm-project/vllm)** — Broncode, issues en community-discussies