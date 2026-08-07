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

vLLM is een krachtige inference-engine ontworpen voor large language models (LLM's). Het biedt geoptimaliseerde serving met continuous batching voor hoge doorvoer en een OpenAI-compatibele API voor naadloze applicatie-integratie. Dit maakt vLLM uitstekend geschikt voor productie-implementaties waarbij snelheid en efficiënt gebruik van resources cruciaal zijn.

Dit playbook leert je hoe je LLM's kunt serveren met behulp van gecontaineriseerde vLLM op de geïntegreerde GPU en hoe je met modellen kunt communiceren via de OpenAI Python API.

## Wat Je Zult Leren

- Hoe je een vLLM-server opzet en start met ondersteuning voor AMD ROCm™
- Hoe je communiceert met modellen via OpenAI-compatibele API-eindpunten
- Hoe je prompts naar de lokale server stuurt met `vllm-prompt`

## De Geheugenconfiguratie Instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op Software-updates

> **Opmerking**: Als VS Code niet is geïnstalleerd, kun je het installeren via AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Softwarevereisten Installeren

vLLM draait in een vooraf gebouwde container met ROCm en bijbehorende afhankelijkheden die vooraf zijn afgestemd. Er is geen extra installatie vereist.

Er is geen installatiestap voor vLLM aan de host-kant nodig. Start vLLM met:

```bash
vllm-launch
```

De launcher start de container, richt zich op de geïntegreerde GPU en stelt een lokale OpenAI-compatibele vLLM-server beschikbaar. Klik als alternatief op het vLLM-pictogram in de taakbalk.

## Snelstart

### 1. Bevestig dat de vLLM-server Draait

Het kan enkele minuten duren voordat `vllm-launch` alles heeft geïnitialiseerd. Zodra deze start, is de server beschikbaar op `http://localhost:8001`. Houd de start-terminal open, omdat de server op de voorgrond draait, en open een aparte terminal voor de resterende stappen. De voorbeelden hieronder gebruiken `Qwen/Qwen3-1.7B`; als jouw launcher is geconfigureerd voor een ander model, vervang dan dat model-ID in de verzoeken.

### 2. Verstuur een Prompt

Gebruik het meegeleverde `vllm-prompt`-script om een verzoek naar de lokale OpenAI-compatibele vLLM-server te sturen:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chat met het model via de OpenAI Python API

Omdat vLLM een OpenAI-compatibele API blootstelt, kun je het `openai` Python-pakket gebruiken om ermee te communiceren.

Maak eerst een Python virtuele omgeving:

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

Maak een `OpenAI`-client aan die verwijst naar de lokale vLLM-server in plaats van naar de servers van OpenAI. De `api_key` is verplicht voor de client, maar vLLM controleert deze niet, dus elke tekenreeks werkt:

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

Doorloop tot slot de gestreamde chunks en druk elk stukje tekst af zodra het binnenkomt:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Het meegeleverde [chat_with_model.py](assets/chat_with_model.py)-script bevat het volledige voorbeeld en kan worden gedownload.


## Een Model Kiezen en Configureren

Standaard serveert `vllm-launch` `Qwen/Qwen3-1.7B` als testmodel op poort `8001`. Je kunt het model, de poort en de vLLM-serveerparameters wijzigen zonder de container opnieuw te bouwen of te bewerken.

### Door AMD Geteste Modellen

De volgende modellen zijn vooraf geconfigureerd en gevalideerd door AMD:

| Model | Opmerkingen |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Standaardmodel. Lichtgewicht en snel te laden. |
| `openai/gpt-oss-20b` | Groter model voor antwoorden van hogere kwaliteit. |

### Een Ander Model Starten

Geef het model-ID op met `--model` (of `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### De Poort Wijzigen

Geef een poort boven 1024 op met `--port` (of `-p`); de standaardwaarde is `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Als je de poort wijzigt, richt de `base_url` van je client dan op dezelfde poort (bijvoorbeeld `http://localhost:8080/v1`).

### Extra vLLM-parameters Doorgeven

Alle extra argumenten worden rechtstreeks doorgestuurd naar vLLM, zodat je het serveergedrag kunt afstemmen, zoals de contextlengte of het datatype. Er zijn twee manieren om deze op te geven.

**Inline**, na de launcher-opties:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Permanent**, in een configuratiebestand op `~/.local/share/vLLM/vllm-launch.conf`. Dit bestand bestaat standaard niet — maak het aan en voeg je argumenten toe als een Bash-array:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Gebruik `+=` om toe te voegen aan de standaardargumenten in plaats van deze te vervangen:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Om op elk moment alle launcher-opties te bekijken, voer je uit:

```bash
vllm-launch --help
```

### Waar Modellen Worden Opgeslagen

`vllm-launch` zoekt naar modellen op twee locaties:

| Locatie | Pad |
|----------|------|
| Systeemmodellen | `/var/cache/models` |
| Gebruikersmodellen | `~/.local/share/vLLM/models` |

Je kunt een gedownload model in een van beide mappen plaatsen en het starten door het pad of ID ervan door te geven aan `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Opmerking**: Het op deze manier draaien van je eigen gedownloade model zou moeten werken zodra het model in een van de bovenstaande mappen is geplaatst, maar deze workflow is nog niet officieel gevalideerd door AMD.

## Probleemoplossing

### Verbinding Geweigerd

Zorg ervoor dat de server draait:
```bash
curl http://localhost:8001/health
```

## Samenvatting

In dit playbook heb je geleerd hoe je:

- Gecontaineriseerde vLLM start met ondersteuning voor ROCm op de geïntegreerde GPU
- Een vLLM-server start met OpenAI-compatibele API-eindpunten op poort 8001
- Prompts verstuurt met `vllm-prompt`
- API-aanroepen doet naar de vLLM-server met zowel streaming- als niet-streamingverzoeken
- Veelvoorkomende problemen oplost met het opstarten van de server, geheugen en clientverbindingen

Je beschikt nu over een gecontaineriseerde vLLM-implementatie voor het serveren van large language models met geoptimaliseerde prestaties op de geïntegreerde GPU.

## Volgende Stappen

- **Probeer verschillende modellen** — Gebruik `vllm-launch --model <model>` om te experimenteren met verschillende LLM's en de prestaties te vergelijken (zie [Een Model Kiezen en Configureren](#choosing-and-configuring-a-model)).
- **Bouw een applicatie** — Gebruik de OpenAI-compatibele API om vLLM te integreren in een Python-app, chatbot of automatiseringsworkflow.
- **Fine-tunen en serveren** — Fine-tune een model met behulp van LoRA of QLoRA, en implementeer het vervolgens met vLLM voor geoptimaliseerde inference.
## Aanvullende bronnen

- **[Officiële vLLM-documentatie](https://docs.vllm.ai/)** — Uitgebreide handleidingen en API-referenties
- **[vLLM GitHub-repository](https://github.com/vllm-project/vllm)** — Broncode, issues en communitydiscussies