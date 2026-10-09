<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Overzicht

vLLM is een krachtige inference-engine die is ontworpen voor grote taalmodellen (LLM's). Het biedt geoptimaliseerde serving met continuous batching voor hoge doorvoer en een OpenAI-compatibele API voor naadloze applicatie-integratie. Dit maakt vLLM uitstekend geschikt voor productie-implementaties waarbij snelheid en efficiënt resourcegebruik cruciaal zijn.

Dit playbook leert je hoe je LLM's kunt serveren met behulp van gecontaineriseerde vLLM op de geïntegreerde GPU en hoe je met modellen kunt communiceren via de OpenAI Python API.

## Wat je gaat leren

- Hoe je een vLLM-server opzet en start met ondersteuning voor AMD ROCm™
- Hoe je communiceert met modellen via OpenAI-compatibele API-endpoints
- Hoe je prompts naar de lokale server stuurt met `vllm-prompt`

## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates

> **Opmerking**: Als VS Code niet is geïnstalleerd, kun je het installeren via AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Software-vereisten installeren

vLLM draait in een vooraf gebouwde container waarin ROCm en de bijbehorende afhankelijkheden al op elkaar zijn afgestemd. Er is geen aanvullende installatie vereist.

Er is geen stap nodig om vLLM op de host te installeren. Start vLLM met:

```bash
vllm-launch
```

De launcher start de container, richt zich op de geïntegreerde GPU en stelt een lokale OpenAI-compatibele vLLM-server beschikbaar. Als alternatief kun je op het vLLM-pictogram in de taakbalk klikken.

## Snel aan de slag

### 1. Bevestig dat de vLLM-server draait

Het kan een paar minuten duren voordat `vllm-launch` alles heeft geïnitialiseerd. Zodra de server is gestart, is deze beschikbaar op `http://localhost:8001`. Houd de terminal waarin je de launcher hebt gestart open, omdat de server op de voorgrond draait, en open een afzonderlijke terminal voor de resterende stappen. In de onderstaande voorbeelden wordt `Qwen/Qwen3-1.7B` gebruikt; als je launcher is geconfigureerd voor een ander model, vervang je dat model-ID dan in de aanvragen.

### 2. Stuur een prompt

Gebruik het meegeleverde `vllm-prompt`-script om een aanvraag te sturen naar de lokale, OpenAI-compatibele vLLM-server:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chat met het model via de OpenAI Python API

Omdat vLLM een OpenAI-compatibele API biedt, kun je het Python-pakket `openai` gebruiken om ermee te communiceren.

Maak eerst een virtuele Python-omgeving aan:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->

Installeer het OpenAI-pakket
```bash
pip install openai
```

Maak een `OpenAI`-client aan die verwijst naar de lokale vLLM-server in plaats van naar de servers van OpenAI. De `api_key` is verplicht voor de client, maar vLLM valideert deze niet, dus elke willekeurige string werkt:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Stuur vervolgens een chat-completion-aanvraag. Dit gebruikt hetzelfde berichtformaat als de OpenAI API — een lijst met berichten met rollen zoals `"user"` en `"assistant"`. Door `stream=True` in te stellen, komt het antwoord geleidelijk binnen in plaats van in één keer:

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

Doorloop ten slotte de gestreamde brokken en print elk stukje tekst zodra het binnenkomt:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Het meegeleverde script [chat_with_model.py](assets/chat_with_model.py) bevat het volledige voorbeeld en kan worden gedownload.


## Een model kiezen en configureren

Standaard serveert `vllm-launch` `Qwen/Qwen3-1.7B` als testmodel op poort `8001`. Je kunt het model, de poort en de vLLM-serveringsparameters wijzigen zonder de container opnieuw te bouwen of te bewerken.

### Door AMD geteste modellen

De volgende modellen zijn vooraf geconfigureerd en door AMD gevalideerd:

| Model | Opmerkingen |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Standaardmodel. Lichtgewicht en snel te laden. |
| `openai/gpt-oss-20b` | Groter model voor antwoorden van hogere kwaliteit. |

### Een ander model starten

Geef het model-ID op met `--model` (of `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### De poort wijzigen

Geef een poort hoger dan 1024 op met `--port` (of `-p`); de standaardwaarde is `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Als je de poort wijzigt, zorg er dan voor dat de `base_url` van je client naar dezelfde poort verwijst (bijvoorbeeld `http://localhost:8080/v1`).

### Extra vLLM-parameters doorgeven

Eventuele extra argumenten worden rechtstreeks doorgestuurd naar vLLM, zodat je het servingsgedrag kunt afstemmen, zoals de contextlengte of het datatype. Er zijn twee manieren om deze op te geven.

**Inline**, na de launcheropties:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Permanent**, in een configuratiebestand op `~/.local/share/vLLM/vllm-launch.conf`. Dit bestand bestaat standaard niet — maak het aan en voeg je argumenten toe als een Bash-array:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Gebruik `+=` om argumenten toe te voegen aan de standaardargumenten in plaats van ze te vervangen:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Om op elk moment alle launcheropties te bekijken, voer je uit:

```bash
vllm-launch --help
```

### Waar modellen worden opgeslagen

`vllm-launch` zoekt naar modellen op twee locaties:

| Locatie | Pad |
|----------|------|
| Systeemmodellen | `/var/cache/models` |
| Gebruikersmodellen | `~/.local/share/vLLM/models` |

Je kunt een gedownload model in een van beide mappen plaatsen en het starten door het pad of ID ervan door te geven aan `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Opmerking**: Het is te verwachten dat het op deze manier draaien van je eigen gedownloade model werkt zodra het model in een van bovenstaande mappen is geplaatst, maar deze workflow is nog niet officieel door AMD gevalideerd.

## Problemen oplossen

### Verbinding geweigerd

Zorg ervoor dat de server draait:
```bash
curl http://localhost:8001/health
```

## Samenvatting

In dit playbook heb je geleerd hoe je:

- Gecontaineriseerde vLLM start met ondersteuning voor ROCm op de geïntegreerde GPU
- Een vLLM-server start met OpenAI-compatibele API-endpoints op poort 8001
- Prompts verstuurt met `vllm-prompt`
- API-aanroepen doet naar de vLLM-server, zowel met streaming als non-streaming aanvragen
- Veelvoorkomende problemen oplost met het opstarten van de server, geheugen en clientverbindingen

Je beschikt nu over een gecontaineriseerde vLLM-implementatie voor het serveren van grote taalmodellen met geoptimaliseerde prestaties op de geïntegreerde GPU.

## Volgende stappen

- **Probeer verschillende modellen** — Gebruik `vllm-launch --model <model>` om te experimenteren met verschillende LLM's en de prestaties te vergelijken (zie [Een model kiezen en configureren](#choosing-and-configuring-a-model)).
- **Bouw een applicatie** — Gebruik de OpenAI-compatibele API om vLLM te integreren in een Python-app, chatbot of automatiseringsworkflow.
- **Fine-tune en serveer** — Fine-tune een model met behulp van LoRA of QLoRA, en implementeer het vervolgens met vLLM voor geoptimaliseerde inference.
## Aanvullende bronnen

- **[Officiële vLLM-documentatie](https://docs.vllm.ai/)** — Uitgebreide handleidingen en API-referenties
- **[vLLM GitHub-repository](https://github.com/vllm-project/vllm)** — Broncode, issues en community-discussies