<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overzicht

🍋 **Lemonade** is een open-source lokale AI-server waarmee je grote taalmodellen (LLM's), afbeeldingsgeneratoren en audiomodellen rechtstreeks op je eigen hardware kunt uitvoeren. De modellen worden beschikbaar gesteld via de industriestandaard **OpenAI API**, zodat elke app die werkt met OpenAI direct ook met Lemonade kan werken. Aan het einde van dit playbook gebruik je Lemonade om modellen lokaal op je machine uit te voeren.

## Wat Je Leert

Aan het einde van dit playbook kun je:

* **Lemonade Server installeren** en verifiëren dat het actief is.
* **Een LLM downloaden en ermee chatten** met één enkel commando.
* **De webinterface verkennen** en verschillende modaliteiten uitproberen, zoals vision, spraak-naar-tekst en afbeeldingsgeneratie.
* **Wisselen tussen GPU-backends** tussen Vulkan en AMD ROCm™-software.
* **Een Python-app bouwen** aangedreven door een lokale LLM via de OpenAI-compatibele API.
<!-- @device:halo_box,halo,stx,krk -->
* **Modellen uitvoeren op de AMD Neural Processing Unit (NPU)** met behulp van Hybrid- en FLM-uitvoeringsmodi op AMD Ryzen™ AI-hardware.
<!-- @device:end -->

## De Geheugenconfiguratie Instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op Software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Softwarevereisten Installeren

Zorg er voor je begint voor dat je het volgende hebt:

- Een pc met **Windows 11** of een ondersteunde **Linux**-distributie (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** wordt aanbevolen voor het runtimemodel dat wordt gebruikt in stappen 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** wordt aanbevolen als je het grotere codegeneratiemodel in stap 6 wilt gebruiken (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB vrije schijfruimte**, afhankelijk van de modellen die je downloadt. Het grootste model in deze handleiding is ongeveer 20 GB.
- **Python 3.10–3.13** (gebruikt in het gedeelte over de Python-app)
- Een internetverbinding (bedraad of draadloos)
<!-- @device:halo_box,halo,stx,krk -->
- [Optioneel] Een AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300-serie of Z2 Extreme) met het nieuwste stuurprogramma geïnstalleerd via de [Ryzen AI Software-installatie-instructies](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) als je een model op de NPU wilt uitvoeren.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

---

## Kernconcepten — Hoe Lokale AI-servers Werken

Voordat we een model uitvoeren, is het de moeite waard om te begrijpen *waarom* dingen op deze manier zijn opgezet. Lemonade is een **lokale modelserver**, een proces dat AI-modellen in het geheugen laadt en ze beschikbaar stelt aan applicaties via HTTP, net zoals een cloud-AI-dienst dat zou doen.

### Waarom een Server?

| Voordeel | Wat Het voor Jou Betekent |
|---------|----------------------|
| **Vereenvoudigde integratie** | Apps communiceren met één HTTP API in plaats van te werken met hardware-specifieke C++- of Python-bibliotheken. |
| **Gedeelde modellen** | Eén geladen model kan meerdere apps tegelijk bedienen, zonder dubbele kopieën die je RAM opslokken. |
| **Portabiliteit van cloud naar lokaal** | Code geschreven voor de cloud-API van OpenAI werkt met Lemonade door slechts één URL te wijzigen. |
| **Scheiding van verantwoordelijkheden** | Modelbeheer, streaming en foutbestendigheid worden afgehandeld door de server, zodat ontwikkelaars zich kunnen richten op hun app. |

### De OpenAI API-standaard

Lemonade implementeert de **OpenAI API**, dezelfde interface die wordt gebruikt door ChatGPT, Azure OpenAI en tientallen andere diensten. Het gespreksmodel is eenvoudig:

| Rol | Wie Er Spreekt |
|------|---------------|
| **system** | Instructies aan het model (persona, beperkingen, beschikbare tools) |
| **user** | Berichten van de mens (of applicatie) aan het model |
| **assistant** | Antwoorden gegenereerd door het model |

Dit betekent dat elke bibliotheek of app die OpenAI ondersteunt, met Lemonade kan communiceren door deze te verwijzen naar `http://localhost:13305/api/v1` terwijl Lemonade Server actief is.

## Hoofdactiviteit — Je Eerste Lokale AI-chat

Laten we een LLM downloaden en er een gesprek mee voeren, waarbij de AI volledig op je eigen machine draait.

### Stap 1: Een Model Downloaden en Uitvoeren

Lemonade wordt geleverd met een samengestelde modelbibliotheek. Laten we beginnen met **Gemma-4-E2B-it**, een capabel en compact model dat ook vision-ondersteuning biedt. Open een terminal en voer het volgende uit:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Dit enkele commando doet drie dingen:

1. **Downloadt** het model (~3 GB) van Hugging Face, als het nog niet is gedownload. (Dit kan enige tijd duren)
2. **Start** het Lemonade Server-proces op poort 13305.
3. **Opent Lemonade App** zodat je direct kunt beginnen met chatten met het model.


<!-- @os:windows -->
Op Windows wordt de Lemonade App automatisch gestart en kun je direct beginnen met chatten. Als je het `minimal.msi`-pakket hebt geïnstalleerd, is de app niet inbegrepen. Om te beginnen met chatten, open je je webbrowser en ga je naar `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
Op Linux open je je browser en navigeer je naar `http://localhost:13305` om toegang te krijgen tot de webapp.
<!-- @os:end -->

Probeer een vraag te typen:

```
What are three fun facts about lemons?
```

Het model reageert direct in het chatvenster. **Gefeliciteerd! Je voert een groot taalmodel lokaal uit.**

![Lemonade App met weergegeven logboeken](../../dependencies/assets/ChatwithLogs.png)

In het deelvenster Serverlogboeken in de Lemonade App kun je na elke reactie telemetriegegevens vinden over de prestaties van het model. Bijvoorbeeld:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Stap 2: De Webinterface en Verschillende Modaliteiten Verkennen

Lemonade bevat een ingebouwde webinterface waar je:

- **Kunt communiceren** met het geladen model in een vertrouwd chatvenster
- **Modellen kunt bekijken** in het tabblad Modelbeheer
- **Nieuwe modellen kunt downloaden** met één klik

Probeer te wisselen tussen verschillende modaliteiten via het tabblad **Modelbeheer** in de webinterface, waar je modellen kunt bekijken op Recept of op Categorie:

1. **Vision:** Het `Gemma-4-E2B-it-GGUF`-model dat je al hebt geladen, ondersteunt vision. Plak een afbeelding in het chatvenster en vraag het model deze te beschrijven.
2. **Afbeeldingsgeneratie:** Download in de categorie Afbeelding een afbeeldingsmodel zoals `SDXL-Turbo` via de Modelbeheerder, en gebruik vervolgens de Lemonade-afbeeldingsgenerator om een prompt in te typen en lokaal een afbeelding te genereren.
3. **Audio:** Download in de categorie Audio een audiomodel zoals `Whisper-Tiny`, dat spraak-naar-tekst kan uitvoeren. Geef een audio-opname op om deze lokaal te transcriberen. Voor tekst-naar-spraak kun je een van de modellen in de categorie Spraak proberen, zoals `kokoro-v1`.

![Multi-modaliteit met Lemonade](../../dependencies/assets/multi_modality.png)

### Stap 3: Een Model met een Andere Backend Uitproberen

Als je over een model in de Lemonade App beweegt, zie je een tandwielpictogram. Door hierop te klikken kun je opties voor het model selecteren, inclusief het kiezen van de gewenste backend.

Standaard gebruikt Lemonade Vulkan voor GPU-versnelling. Als je een ondersteunde AMD discrete GPU hebt, kun je overschakelen naar ROCm.

![Lemonade Backend Selecteren](../../dependencies/assets/lemonademodeloptions.png)

Om je geïnstalleerde backends te beheren, klik je op de backendknop in de meest linkse kolom.

Je kunt de backend ook opgeven met het volgende commando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Je kunt ook je standaard backend instellen via de omgevingsvariabele `LEMONADE_LLAMACPP` met de waarden: `vulkan`, `rocm` of `cpu`.

---

## Dieper Gaan — Een AI-aangedreven App Bouwen met Python

De echte kracht van een lokale AI-server is dat elke applicatie er verbinding mee kan maken met slechts een paar regels code. Om dit te bewijzen, bouwen we een kleine maar functionele **studieflashcard-generator** waarbij je een onderwerp opgeeft, het flashcards genereert en je jezelf interactief kunt overhoren.

### Stap 4: De Server Starten

Controleer of de Lemonade-server actief is. Deze start doorgaans automatisch op de achtergrond na de installatie. Voer het volgende uit om dit te verifiëren:

```
lemonade status
```

Je zou een bericht moeten zien zoals: `Server is running on port 13305`.

Als de server niet actief is, start je deze door de Lemonade-app te openen. Gebruik de standaardpoort **13305** (je kunt dit bevestigen of selecteren via het systeemvakpictogram).

### Stap 5: De OpenAI Python-client Installeren

Maak in een terminal een venv aan en installeer de OpenAI Python-client met de volgende commando's:
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### Stap 6: De Flashcard-app Bouwen

Laten we een ander model downloaden om code te genereren: `Qwen3.5-35B-A3B-GGUF`. Dit is een groot (~20 GB) en krachtig model dat het best geschikt is voor systemen met 32 GB+ RAM. Als je minder RAM beschikbaar hebt, probeer dan `Qwen3.5-9B-GGUF` (~6 GB) in plaats daarvan.

Je kunt het downloaden via de UI of het volgende uitvoeren:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Voer de volgende prompt in de Lemonade Chat UI in om code te genereren voor een eenvoudige Flashcard-app.

We gebruiken Qwen3.5-35B-A3B-GGUF (een groter model dat beter is in het schrijven van code) om onze Python-app te genereren, en de app zelf roept Gemma-4-E2B-it-GGUF (het kleinere model dat je al hebt gedownload) aan tijdens de uitvoering. De code kan vervolgens worden gekopieerd naar een bestand naar keuze om in Python te worden uitgevoerd.

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **Tip**: We hebben standaard engineeringpraktijken gevolgd door grondige promptcreatie en door een tweemodelssysteem te gebruiken om resources en snelheid te optimaliseren.

Voor je gemak hebben we voorbeelduitvoer beschikbaar gesteld in [`flashcards.py`](assets/flashcards.py). Je kunt het gerust naar je map downloaden. Hoe dan ook, je zou nu een Python-bestand moeten hebben dat kan worden uitgevoerd.

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### Stap 7: De Gegenereerde Code Uitvoeren

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Dit is wat je zou moeten zien:**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

In ongeveer 150 regels code heb je een volledig functioneel studiehulpmiddel gebouwd, aangedreven door een lokale LLM. Er is geen API-sleutel te beheren, geen gebruikskosten en er verlaat nooit data je machine.

> **Belangrijk inzicht:** Let op de regel `client = OpenAI(base_url=...) ` — dit is het *enige* wat deze app aan Lemonade koppelt in plaats van aan de cloud van OpenAI. De rest van de code is identiek aan wat je zou schrijven voor elke OpenAI-compatibele dienst. Als je ooit de OpenAI Python-bibliotheek hebt gebruikt, weet je al hoe je apps met Lemonade bouwt.

### Wat Dit Aantoont

Deze kleine app maakt gebruik van verschillende praktische integratiepatronen:

| Patroon | Waar Het Voorkomt |
|---------|-----------------|
| **Systeemprompts** | Het `"system"`-bericht vertelt de LLM om gestructureerde JSON uit te voeren |
| **Gestructureerde uitvoer** | De app parseert de reactie van de LLM als JSON om flashcards te maken |
| **Staatloze verzoeken** | Elke `generate_flashcards()`-aanroep is onafhankelijk |
| **Foutafhandeling** | De `try/except` handelt op een nette manier gevallen af waarbij de uitvoer van de LLM geen geldige JSON is |

Dezelfde patronen zijn schaalbaar naar elke applicatie, zoals chatbots, codeassistenten, contentgeneratoren en automatiseringstools.

#### Bonusuitdaging

* Probeer als extra uitdaging de app bij te werken zodat de flashcards aan de gebruiker worden voorgelezen, door te verwijzen naar het voorbeeld dat [hier](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) wordt gegeven.

---

<!-- @device:halo_box,halo,stx,krk -->
## Modellen Uitvoeren op de NPU (Optioneel)

Als je een Ryzen AI 300/400/Max 300-serie of Z2 Extreme hebt, beschikt je apparaat over een ingebouwde **Neural Processing Unit (NPU)**, een speciale chip die specifiek is ontworpen voor AI-workloads. Het uitvoeren van modellen op de NPU is energiezuiniger dan het gebruik van de GPU, waardoor het ideaal is voor AI-taken op de achtergrond, langere sessies en gebruik op batterijstroom.

Lemonade ondersteunt drie NPU-uitvoeringsmodi, allemaal transparant achter dezelfde OpenAI API:

| Modus | Hoe Het Werkt | Recept | Voorbeeldmodellen |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU verwerkt de prompt, iGPU genereert tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Alleen NPU** | Volledige inferentie wordt uitgevoerd op de NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Gebruikt de FastFlowLM-engine op de NPU, geoptimaliseerd voor AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Vereisten

- **AMD Ryzen AI 300/400-serie of Z2-serie** processor
- Voor **FLM**-modellen: De FLM-runtime kan worden geïnstalleerd vanuit de Lemonade-app, of Lemonade installeert de FLM-runtime automatisch bij het uitvoeren van een FLM-model. Zie [hier](https://fastflowlm.com/docs/) voor meer informatie over FastFlowLM.


### Stap 8: Een Hybrid-model Uitvoeren

Hybrid-modellen verdelen het werk tussen de NPU en iGPU voor een goede balans tussen snelheid en efficiëntie. Selecteer in de Lemonade App een model uit de lijst `Ryzen AI LLM`, bijvoorbeeld `Qwen3-4B-Hybrid`, of voer het uit met het volgende commando:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade detecteert je NPU automatisch en installeert de **Ryzen AI LLM**-backend.

> **Wat gebeurt er achter de schermen?** Wanneer je een bericht verstuurt, verwerkt de NPU je volledige prompt parallel (dit wordt "prefill" genoemd). Vervolgens neemt de iGPU het over om de reactie token voor token te genereren (dit wordt "decode" genoemd). Deze hybride aanpak speelt in op de sterke punten van elke chip.

### Stap 9: Een FLM-model Uitvoeren

FastFlowLM (FLM)-modellen zijn specifiek geoptimaliseerd voor de XDNA2 NPU-architectuur van AMD en kunnen voor hun omvang zeer snel zijn. Selecteer bijvoorbeeld `qwen3.5-4b-FLM` uit de lijst `FastFlowLM NPU` of gebruik het volgende commando:

<!-- @os:windows -->
Om `FastFlowLM` op Windows in te schakelen:

* Open het menu `Backends Manager`.
* Zoek de backendcategorie `FastFlowLM NPU`.
* Klik op NPU installeren.
* Zodra de installatie is voltooid, zijn er ~36 standaardmodellen beschikbaar in het FFLM-vervolgkeuzemenu.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Wanneer de `Lemonade`-app voor de eerste keer wordt gestart, is de `FastFlowNPU`-backend standaard niet ingeschakeld.
De lokale app opent de installatiepagina om je door de installatie te begeleiden.

Om `FastFlowLM` op Linux in te schakelen:

* Open de `Lemonade`-app.
* Bezoek de [officiële FLM](https://lemonade-server.ai/flm_npu_linux.html)-documentatie en volg de installatiestappen voor FLM door je Linux-distributie te selecteren.
* Schakel backports in zoals aangegeven op de installatiepagina.
* Download de nieuwste `v0.9.x`-release van de [tagspagina](https://github.com/FastFlowLM/FastFlowLM/tags).
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Zorg er voor AMD Halo Developer Platform voor dat je Debian 13 kiest.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Installeer het gedownloade `.deb`-pakket.
* Aanbevolen: Sluit de `Lemonade App` en open deze opnieuw zodat de wijzigingen worden gedetecteerd.
* Aanbevolen: Open `Backends Manager` en klik op `FastFlowNPU`-backend installeren.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Na een geslaagde installatie zou je moeten zien dat `flm:npu` is voltooid in de **Downloadbeheerder** in de **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Je kunt vervolgens een van de beschikbare FFLM-modellen selecteren en de NPU-backend gaan gebruiken.

Voor een specifiek model download je het gewenste model van de [modelspagina](https://fastflowlm.com/docs/models/qwen/) en valideer je het met het Shell-commando dat in de documentatie wordt gegeven.
```
flm run qwen3.5-4b-FLM
```
of via 
```
lemonade run qwen3.5-4b-FLM
```

FLM-modellen omvatten enkele van de populairste architecturen (Gemma 3, Qwen 3, Llama 3 en DeepSeek R1) en variëren van minder dan 1 GB tot meer dan 13 GB.
Lemonade detecteert je NPU automatisch en installeert de **FastFlowLM NPU**-backend.

<!-- @os:windows -->
> **Tip:** Voor de beste NPU-prestaties schakel je de turbomodus in:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Wisselen van Model

De flashcard-app uit stap 6 werkt ook met NPU-modellen — verander gewoon de modelnaam:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Volgende Stappen

Je hebt een lokale AI-server die op je eigen hardware draait — hier is waar je naartoe kunt gaan:

1. **Verbind je favoriete apps**: Lemonade werkt direct samen met [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) en [nog veel meer](https://lemonade-server.ai/marketplace).

2. **Verken meer modellen**: Bekijk de volledige [modelbibliotheek](https://lemonade-server.ai/docs/server/server_models/) om modellen te vinden die zijn geoptimaliseerd voor codering, redeneren, vision en meer. Gebruik de Lemonade App of `lemonade list` om te zien wat er beschikbaar is.

3. **Ontgrendel ROCm GPU-versnelling**: Als je een ondersteunde AMD GPU hebt, schakel je over naar de ROCm-backend: `lemonade config set llamacpp.backend=rocm`. Zie [ondersteunde AMD GPU's](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Lees de volledige API-specificatie**: Lemonade ondersteunt chatcompletions, embeddings, audiotranscriptie, afbeeldingsgeneratie, tekst-naar-spraak en meer. Zie de [Serverspecificatie](https://lemonade-server.ai/docs/server/server_spec/) voor elk eindpunt.

5. **Draag bij**: Lemonade is open source. Bekijk de [bijdragegids](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) en zoek naar [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).