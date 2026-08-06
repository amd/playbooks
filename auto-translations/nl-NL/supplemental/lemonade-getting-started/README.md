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

🍋 **Lemonade** is een open-source lokale AI-server waarmee je grote taalmodellen (LLM's), beeldgeneratoren en audiomodellen rechtstreeks op je eigen hardware kunt uitvoeren. De modellen worden beschikbaar gesteld via de industriestandaard **OpenAI API**, zodat elke applicatie die met OpenAI werkt onmiddellijk ook met Lemonade kan werken. Aan het einde van dit playbook gebruik je Lemonade om modellen lokaal op je machine uit te voeren.

## Wat je leert

Aan het einde van dit playbook kun je:

* **Lemonade Server installeren** en verifiëren dat het draait.
* **Een LLM downloaden en ermee chatten** met één enkele opdracht.
* **De webinterface verkennen** en verschillende modaliteiten uitproberen, zoals visie, spraak-naar-tekst en beeldgeneratie.
* **GPU-backends wisselen** tussen Vulkan en AMD ROCm™-software.
* **Een Python-app bouwen** die wordt aangedreven door een lokale LLM via de OpenAI-compatibele API.
<!-- @device:halo_box,halo,stx,krk -->
* **Modellen uitvoeren op de AMD Neural Processing Unit (NPU)** met behulp van Hybrid- en FLM-uitvoeringsmodi op AMD Ryzen™ AI-hardware.
<!-- @device:end -->

## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Software-vereisten installeren

Zorg ervoor dat je, voordat je begint, het volgende hebt:

- Een pc met **Windows 11** of een ondersteunde **Linux**-distributie (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** wordt aanbevolen voor het runtime-model dat wordt gebruikt in stap 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** wordt aanbevolen als je het grotere codegeneratiemodel in stap 6 wilt gebruiken (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB vrije schijfruimte**, afhankelijk van de modellen die je downloadt. Het grootste model in deze handleiding is ongeveer 20 GB.
- **Python 3.10–3.13** (gebruikt in het gedeelte over de Python-app)
- Een internetverbinding (bekabeld of draadloos)
<!-- @device:halo_box,halo,stx,krk -->
- [Optioneel] Een AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300-serie of Z2 Extreme) met de nieuwste driver geïnstalleerd vanaf [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) als je een model op de NPU wilt uitvoeren.
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
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```bash
winget upgrade -e --id AMD.LemonadeServer
lemonade --version
```
<!-- @test:end -->

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
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

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

## Kernconcepten — Hoe lokale AI-servers werken

Voordat we een model uitvoeren, is het de moeite waard om te begrijpen *waarom* dingen op deze manier zijn ingericht. Lemonade is een **lokale modelserver**, een proces dat AI-modellen in het geheugen laadt en ze via HTTP beschikbaar stelt aan applicaties, net zoals een cloud-AI-service dat zou doen.

### Waarom een server?

| Voordeel | Wat dit voor jou betekent |
|---------|----------------------|
| **Vereenvoudigde integratie** | Apps communiceren met één HTTP API in plaats van te werken met hardwarespecifieke C++- of Python-bibliotheken. |
| **Gedeelde modellen** | Eén geladen model kan meerdere apps tegelijk bedienen, zonder dat er dubbele kopieën je RAM opeten. |
| **Overdraagbaarheid van cloud naar lokaal** | Code die geschreven is voor de cloud-API van OpenAI werkt met Lemonade door slechts één URL te wijzigen. |
| **Scheiding van verantwoordelijkheden** | Modelbeheer, streaming en foutbestendigheid worden afgehandeld door de server, zodat ontwikkelaars zich kunnen richten op hun app. |

### De OpenAI API-standaard

Lemonade implementeert de **OpenAI API**, dezelfde interface die wordt gebruikt door ChatGPT, Azure OpenAI en tientallen andere diensten. Het gespreksmodel is eenvoudig:

| Rol | Wie er spreekt |
|------|---------------|
| **system** | Instructies aan het model (persona, beperkingen, beschikbare tools) |
| **user** | Berichten van de mens (of applicatie) aan het model |
| **assistant** | Antwoorden gegenereerd door het model |

Dit betekent dat elke bibliotheek of app die OpenAI ondersteunt, met Lemonade kan communiceren door deze naar `http://localhost:13305/api/v1` te laten wijzen terwijl Lemonade Server actief is.

## Hoofdactiviteit — Je eerste lokale AI-chat

Laten we een LLM downloaden en er een gesprek mee voeren, waarbij de AI volledig op je eigen machine draait.

### Stap 1: Een model downloaden en uitvoeren

Lemonade wordt geleverd met een samengestelde modelbibliotheek. Laten we beginnen met **Gemma-4-E2B-it**, een krachtig en compact model dat visieondersteuning omvat. Open een terminal en voer het volgende uit:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Deze ene opdracht doet drie dingen:

1. **Downloadt** het model (~3 GB) van Hugging Face, als het nog niet is gedownload. (Dit kan enige tijd duren)
2. **Start** het Lemonade Server-proces op poort 13305.
3. **Opent Lemonade App** zodat je meteen met het model kunt chatten.


<!-- @os:windows -->
Op Windows wordt de Lemonade App automatisch gestart en kun je direct beginnen met chatten. Als je het `minimal.msi`-pakket hebt geïnstalleerd, is de app niet inbegrepen. Om te chatten, open je je webbrowser en ga je naar `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
Open op Linux je browser en navigeer naar `http://localhost:13305` om toegang te krijgen tot de webapp.
<!-- @os:end -->

Probeer een vraag te typen:

```
What are three fun facts about lemons?
```

Het model reageert direct in het chatvenster. **Gefeliciteerd! Je draait nu een groot taalmodel lokaal.**

![Lemonade App met logboeken weergegeven](../../dependencies/assets/ChatwithLogs.png)

In het venster Server Logs in de Lemonade App vind je telemetriegegevens over de prestaties van het model na elk antwoord. Bijvoorbeeld:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Stap 2: Verken de webinterface en de verschillende modaliteiten

Lemonade bevat een ingebouwde webinterface waar u:

- Kunt **communiceren** met het geladen model in een vertrouwd chatvenster
- **Modellen kunt bekijken** in het tabblad Model Manager
- **Nieuwe modellen kunt downloaden** met één klik

Probeer te schakelen tussen verschillende modaliteiten met het tabblad **Model Manager** in de webinterface, waar u modellen kunt bekijken per Recipe of per Category:

1. **Vision:** Het model `Gemma-4-E2B-it-GGUF` dat u al geladen hebt, ondersteunt vision. Plak een afbeelding in het chatvak en vraag het model deze te beschrijven.
2. **Beeldgeneratie:** Download in de categorie Image een beeldmodel zoals `SDXL-Turbo` via de Model Manager en gebruik vervolgens de Lemonade Image Generator om een prompt te typen en lokaal een afbeelding te genereren.
3. **Audio:** Download in de categorie Audio een audiomodel zoals `Whisper-Tiny`, dat spraak-naar-tekst kan uitvoeren. Lever een audio-opname aan om deze lokaal te transcriberen. Probeer voor tekst-naar-spraak een van de modellen in de categorie Speech, zoals `kokoro-v1`.

![Multi-modaliteit met Lemonade](../../dependencies/assets/multi_modality.png)

### Stap 3: Probeer een model met een andere backend

Als u de muis over een model in de Lemonade App houdt, ziet u een tandwielicoontje. Als u hierop klikt, kunt u opties voor het model selecteren, waaronder het kiezen van de gewenste backend.

Standaard gebruikt Lemonade Vulkan voor GPU-versnelling. Als u een ondersteunde AMD discrete GPU hebt, kunt u overschakelen naar ROCm.

![Lemonade Backend selecteren](../../dependencies/assets/lemonademodeloptions.png)

Klik op de backend-knop in de meest linkse kolom om uw geïnstalleerde backends te beheren.

U kunt de backend ook opgeven met het volgende commando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

U kunt ook uw standaardbackend instellen met de omgevingsvariabele `LEMONADE_LLAMACPP`, met de waarden: `vulkan`, `rocm` of `cpu`.

---

## Verder gaan — Bouw een AI-aangedreven app met Python

De echte kracht van een lokale AI-server is dat elke applicatie er verbinding mee kan maken met slechts een paar regels code. Om dit te bewijzen, gaan we een kleine maar functionele **studieflashcardgenerator** bouwen waarbij u een onderwerp opgeeft, deze flashcards genereert, en u uzelf interactief kunt overhoren.

### Stap 4: Start de server

Controleer of de Lemonade-server actief is. Deze start doorgaans automatisch op de achtergrond na installatie. Voer het volgende uit om dit te controleren:

```
lemonade status
```

U zou een bericht moeten zien zoals: `Server is running on port 13305`.

Als de server niet actief is, start deze door de Lemonade-app te openen. Gebruik de standaardpoort **13305** (u kunt dit bevestigen of selecteren vanuit het systeemvakpictogram).

### Stap 5: Installeer de OpenAI Python Client

Maak in een terminal een venv aan en installeer de OpenAI Python Client met de volgende commando's:
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

### Stap 6: Bouw de Flashcard-app

Laten we een ander model downloaden om code te genereren: `Qwen3.5-35B-A3B-GGUF`. Dit is een groot (~20 GB) en performant model dat het meest geschikt is voor systemen met 32 GB+ RAM. Als u minder RAM beschikbaar hebt, probeer dan in plaats daarvan `Qwen3.5-9B-GGUF` (~6 GB).

U kunt het downloaden vanuit de UI of het volgende uitvoeren:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Voer de volgende prompt in de Lemonade Chat UI in om code te genereren voor een eenvoudige Flashcard-app.

We gebruiken Qwen3.5-35B-A3B-GGUF (een groter model dat beter is in het schrijven van code) om onze Python-app te genereren, en de app zelf zal tijdens runtime Gemma-4-E2B-it-GGUF (het kleinere model dat u al hebt gedownload) aanroepen. De code kan vervolgens worden gekopieerd naar een bestand naar keuze om in Python te worden uitgevoerd.

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

> **Tip**: We hebben standaard engineeringpraktijken gevolgd door middel van zorgvuldige promptcreatie en door gebruik te maken van een systeem met twee modellen om resources en snelheid te optimaliseren.

Voor uw gemak hebben we voorbeelduitvoer geleverd in [`flashcards.py`](assets/flashcards.py). U kunt dit gerust downloaden naar uw map. Hoe dan ook, u zou nu een Python-bestand moeten hebben dat kan worden uitgevoerd.

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


### Stap 7: Voer de gegenereerde code uit

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Dit is wat u zou moeten zien:**

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

In ongeveer 150 regels code hebt u een volledig functionele studietool gebouwd, aangedreven door een lokale LLM. Er is geen API-sleutel om te beheren, geen gebruikskosten, en er verlaat nooit data uw machine.

> **Belangrijk inzicht:** Merk op dat de regel `client = OpenAI(base_url=...) ` het *enige* is dat deze app koppelt aan Lemonade in plaats van aan de cloud van OpenAI. De rest van de code is identiek aan wat u zou schrijven tegen elke OpenAI-compatibele service. Als u ooit de OpenAI Python-bibliotheek hebt gebruikt, weet u al hoe u apps met Lemonade kunt bouwen.

### Wat dit aantoont

Deze kleine app demonstreert verschillende integratiepatronen uit de praktijk:

| Patroon | Waar het voorkomt |
|---------|-----------------|
| **Systeemprompts** | Het `"system"`-bericht vertelt de LLM om gestructureerde JSON uit te voeren |
| **Gestructureerde uitvoer** | De app parseert de reactie van de LLM als JSON om flashcards te bouwen |
| **Stateless verzoeken** | Elke aanroep van `generate_flashcards()` is onafhankelijk |
| **Foutafhandeling** | De `try/except` handelt op een nette manier gevallen af waarbij de uitvoer van de LLM geen geldige JSON is |

Diezelfde patronen zijn schaalbaar naar elke applicatie, zoals chatbots, codeassistenten, contentgenerators, automatiseringstools.

#### Bonusuitdaging

* Probeer voor een extra uitdaging de app aan te passen zodat de flashcards aan de gebruiker worden voorgelezen, door te verwijzen naar het voorbeeld dat [hier](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) wordt aangeboden.

---

<!-- @device:halo_box,halo,stx,krk -->
## Modellen uitvoeren op de NPU (optioneel)

Als u een Ryzen AI 300/400/Max 300-serie of Z2 Extreme heeft, beschikt uw apparaat over een ingebouwde **Neural Processing Unit (NPU)**, een speciale chip die specifiek is ontworpen voor AI-workloads. Modellen uitvoeren op de NPU is energie-efficiënter dan het gebruik van de GPU, waardoor het ideaal is voor achtergrond-AI-taken, langere sessies en gebruik op accuvoeding.

Lemonade ondersteunt drie NPU-uitvoeringsmodi, allemaal transparant achter dezelfde OpenAI API:

| Modus | Hoe het werkt | Recept | Voorbeeldmodellen |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU verwerkt de prompt, iGPU genereert tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Alleen NPU** | Volledige inferentie draait op de NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Gebruikt de FastFlowLM-engine op de NPU, geoptimaliseerd voor AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Vereisten

- **AMD Ryzen AI 300/400-serie of Z2-serie**-processor
- Voor **FLM**-modellen: De FLM-runtime kan worden geïnstalleerd vanuit de Lemonade-app, of Lemonade installeert de FLM-runtime automatisch wanneer een FLM-model wordt uitgevoerd. Zie [hier](https://fastflowlm.com/docs/) voor meer informatie over FastFlowLM.


### Stap 8: Een hybride model uitvoeren

Hybride modellen verdelen het werk tussen de NPU en iGPU voor een goede balans tussen snelheid en efficiëntie. Selecteer in de Lemonade App een model uit de lijst `Ryzen AI LLM`, bijvoorbeeld `Qwen3-4B-Hybrid`, of voer het uit met de volgende opdracht:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade detecteert uw NPU automatisch en installeert de **Ryzen AI LLM**-backend.

> **Wat gebeurt er achter de schermen?** Wanneer u een bericht verstuurt, verwerkt de NPU uw volledige prompt parallel (dit heet "prefill"). Vervolgens neemt de iGPU het over om de reactie token voor token te genereren (dit heet "decode"). Deze hybride aanpak benut de sterke punten van elke chip.

### Stap 9: Een FLM-model uitvoeren

FastFlowLM (FLM)-modellen zijn specifiek geoptimaliseerd voor AMD's XDNA2 NPU-architectuur en kunnen zeer snel zijn voor hun formaat. Selecteer bijvoorbeeld `qwen3.5-4b-FLM` uit de lijst `FastFlowLM NPU` of gebruik de volgende opdracht:

<!-- @os:windows -->
Om `FastFlowLM` op Windows in te schakelen:

* Open het menu `Backends Manager`.
* Zoek de backendcategorie `FastFlowLM NPU`.
* Klik op Install NPU.
* Zodra de installatie is voltooid, zijn er ~36 standaardmodellen beschikbaar in het FFLM-vervolgkeuzemenu.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Wanneer de `Lemonade`-app voor het eerst wordt gestart, is de `FastFlowNPU`-backend standaard niet ingeschakeld.
De lokale app opent de installatiepagina om u door de installatie te leiden.

Om `FastFlowLM` op Linux in te schakelen:

* Open de `Lemonade`-app.
* Bezoek de [officiële FLM](https://lemonade-server.ai/flm_npu_linux.html)-documentatie en volg de installatiestappen voor FLM door uw Linux-distributie te selecteren.
* Schakel backports in zoals beschreven op de installatiepagina.
* Download de nieuwste `v0.9.x`-release van de [tags-pagina](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Zorg er bij het AMD Halo Developer Platform voor dat u Debian 13 kiest.
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
* Aanbevolen: Sluit de `Lemonade App` af en open deze opnieuw zodat de wijzigingen worden gedetecteerd.
* Aanbevolen: Open `Backends Manager` en klik op Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Na een geslaagde installatie zou u moeten zien dat `flm:npu` is voltooid in de **Download Manager** binnen de **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
U kunt vervolgens een van de beschikbare FFLM-modellen selecteren en de NPU-backend gaan gebruiken.

Download voor een specifiek model het gewenste model van de [modellenpagina](https://fastflowlm.com/docs/models/qwen/) en valideer het met behulp van de Shell-opdracht die in de documentatie wordt vermeld.
```
flm run qwen3.5-4b-FLM
```
of via 
```
lemonade run qwen3.5-4b-FLM
```

FLM-modellen omvatten enkele van de populairste architecturen (Gemma 3, Qwen 3, Llama 3 en DeepSeek R1) en variëren van minder dan 1 GB tot meer dan 13 GB.
Lemonade detecteert uw NPU automatisch en installeert de **FastFlowLM NPU**-backend.

<!-- @os:windows -->
> **Tip:** Schakel voor de beste NPU-prestaties turbomodus in:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Modellen wisselen

De flashcard-app uit stap 6 werkt ook met NPU-modellen, verander alleen de modelnaam:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Volgende stappen

U heeft nu een lokale AI-server draaien op uw eigen hardware. Dit zijn de volgende stappen:

1. **Verbind uw favoriete apps**: Lemonade werkt out of the box met [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/), en [nog veel meer](https://lemonade-server.ai/marketplace).

2. **Blader door meer modellen**: Verken de volledige [modellenbibliotheek](https://lemonade-server.ai/docs/server/server_models/) om modellen te vinden die geoptimaliseerd zijn voor coderen, redeneren, visie en meer. Gebruik de Lemonade App of `lemonade list` om te zien wat beschikbaar is.

3. **Ontgrendel ROCm GPU-versnelling**: Als u een ondersteunde AMD GPU heeft, schakel dan over naar de ROCm-backend: `lemonade config set llamacpp.backend=rocm`. Zie [ondersteunde AMD GPU's](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Lees de volledige API-specificatie**: Lemonade ondersteunt chatvoltooiingen, embeddings, audiotranscriptie, beeldgeneratie, tekst-naar-spraak en meer. Zie de [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) voor elk eindpunt.

5. **Draag bij**: Lemonade is open source. Bekijk de [bijdragehandleiding](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) en kijk naar [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->