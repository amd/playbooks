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

🍋 **Lemonade** er en åpen kildekode lokal AI-server som lar deg kjøre store språkmodeller (LLM-er), bildegeneratorer og lydmodeller direkte på din egen maskinvare. Den eksponerer modellene gjennom bransjestandarden **OpenAI API**, slik at enhver app som fungerer med OpenAI umiddelbart kan fungere med Lemonade. Ved slutten av denne oppskriften vil du bruke Lemonade til å kjøre modeller lokalt på maskinen din.

## Hva du vil lære

Ved slutten av denne oppskriften vil du kunne:

* **Installere Lemonade Server** og bekrefte at den kjører.
* **Laste ned og chatte med en LLM** ved hjelp av én enkelt kommando.
* **Utforske web-grensesnittet** og prøve ulike modaliteter som syn, tale-til-tekst og bildegenerering.
* **Bytte GPU-backend** mellom Vulkan og AMD ROCm™-programvare.
* **Bygge en Python-app** drevet av en lokal LLM ved hjelp av det OpenAI-kompatible API-et.
<!-- @device:halo_box,halo,stx,krk -->
* **Kjøre modeller på AMD Neural Processing Unit (NPU)** ved hjelp av Hybrid- og FLM-kjøremoduser på AMD Ryzen™ AI-maskinvare.
<!-- @device:end -->

## Angi minnekonfigurasjonen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Se etter programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installere nødvendig programvare

Før du begynner, sørg for at du har:

- En PC som kjører **Windows 11** eller en støttet **Linux**-distribusjon (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** anbefales for kjøretidsmodellen som brukes i trinn 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** anbefales hvis du vil bruke den større kodegenereringsmodellen i trinn 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB ledig diskplass**, avhengig av hvilke modeller du laster ned. Den største modellen i denne veiledningen er omtrent 20 GB.
- **Python 3.10–3.13** (brukes i Python-app-delen)
- En internettforbindelse (kablet eller trådløs)
<!-- @device:halo_box,halo,stx,krk -->
- [Valgfritt] En AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300-serien eller Z2 Extreme) med den nyeste driveren installert fra [Ryzen AI-programvareinstallasjonsinstruksjoner](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) hvis du vil kjøre en modell på NPU-en.
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

## Kjernekonsepter — Hvordan lokale AI-servere fungerer

Før vi kjører en modell, er det verdt å forstå *hvorfor* ting er satt opp på denne måten. Lemonade er en **lokal modellserver**, en prosess som laster AI-modeller inn i minnet og eksponerer dem til applikasjoner over HTTP, akkurat som en sky-AI-tjeneste ville gjort.

### Hvorfor en server?

| Fordel | Hva det betyr for deg |
|---------|----------------------|
| **Forenklet integrasjon** | Apper snakker med ett HTTP-API i stedet for å håndtere maskinvarespesifikke C++- eller Python-biblioteker. |
| **Delte modeller** | Én lastet modell kan betjene flere apper samtidig, uten duplikatkopier som spiser opp RAM-en din. |
| **Portabilitet fra sky til lokalt** | Kode skrevet for OpenAIs sky-API fungerer med Lemonade ved å endre én URL. |
| **Separasjon av ansvarsområder** | Modellhåndtering, strømming og feiltoleranse håndteres av serveren, slik at utviklere kan fokusere på appen sin. |

### OpenAI API-standarden

Lemonade implementerer **OpenAI API**, det samme grensesnittet som brukes av ChatGPT, Azure OpenAI og dusinvis av andre tjenester. Samtalemodellen er enkel:

| Rolle | Hvem snakker |
|------|---------------|
| **system** | Instruksjoner til modellen (persona, begrensninger, tilgjengelige verktøy) |
| **user** | Meldinger fra mennesket (eller applikasjonen) til modellen |
| **assistant** | Svar generert av modellen |

Dette betyr at ethvert bibliotek eller enhver app som støtter OpenAI kan snakke med Lemonade ved å peke den mot `http://localhost:13305/api/v1` mens Lemonade Server kjører.

## Hovedaktivitet — Din første lokale AI-chat

La oss laste ned en LLM og ha en samtale med den, og kjøre AI-en helt på din egen maskin.

### Trinn 1: Last ned og kjør en modell

Lemonade leveres med et kuratert modellbibliotek. La oss starte med **Gemma-4-E2B-it**, en dyktig og kompakt modell som inkluderer synstøtte. Åpne en terminal og kjør:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Denne enkeltkommandoen gjør tre ting:

1. **Laster ned** modellen (~3 GB) fra Hugging Face, hvis den ikke allerede er lastet ned. (Kan ta litt tid)
2. **Starter** Lemonade Server-prosessen på port 13305.
3. **Åpner Lemonade App** slik at du kan begynne å chatte med modellen.


<!-- @os:windows -->
På Windows starter Lemonade App automatisk, og du kan begynne å chatte med en gang. Hvis du installerte `minimal.msi`-pakken, er ikke appen inkludert. For å begynne å chatte, åpne nettleseren din og gå til `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
På Linux, åpne nettleseren din og naviger til `http://localhost:13305` for å få tilgang til web-appen.
<!-- @os:end -->

Prøv å skrive et spørsmål:

```
What are three fun facts about lemons?
```

Modellen vil svare direkte i chattevinduet. **Gratulerer! Du kjører nå en stor språkmodell lokalt.**

![Lemonade App med logger vist](../../dependencies/assets/ChatwithLogs.png)

I Server Logs-panelet i Lemonade App finner du telemetridata om modellens ytelse etter hvert svar. For eksempel:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Steg 2: Utforsk webgrensesnittet og de forskjellige modalitetene

Lemonade inkluderer et innebygd webgrensesnitt der du kan:

- **Interagere** med den innlastede modellen i et kjent chattevindu
- **Bla gjennom modeller** i fanen Model Manager
- **Laste ned nye modeller** med ett klikk

Prøv å bytte mellom forskjellige modaliteter ved å bruke fanen **Model Manager** i webgrensesnittet, der du kan bla gjennom modeller etter Recipe eller Category:

1. **Vision:** Modellen `Gemma-4-E2B-it-GGUF` som du allerede har lastet inn, støtter vision. Lim inn et bilde i chatteboksen og be modellen beskrive det.
2. **Bildegenerering:** I kategorien Image kan du laste ned en bildemodell som `SDXL-Turbo` fra Model Manager, og deretter bruke Lemonade Image Generator til å skrive en prompt og generere et bilde lokalt.
3. **Lyd:** I kategorien Audio kan du laste ned en lydmodell som `Whisper-Tiny`, som kan gjøre tale-til-tekst. Gi den en lydopptak for å transkribere det lokalt. For tekst-til-tale kan du prøve en av modellene i kategorien Speech, som `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### Steg 3: Prøv en modell med en annen backend

Hvis du holder musepekeren over en modell i Lemonade App, ser du et tannhjulikon. Klikker du på dette, kan du velge alternativer for modellen, inkludert å velge ønsket backend.

Som standard bruker Lemonade Vulkan for GPU-akselerasjon. Hvis du har et støttet AMD dedikert GPU, kan du bytte til ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

For å administrere de installerte backend-ene dine, klikk på backend-knappen i kolonnen lengst til venstre.

Alternativt kan du angi backend ved å bruke følgende kommando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Du kan også angi standard backend ved hjelp av miljøvariabelen `LEMONADE_LLAMACPP` med verdiene: `vulkan`, `rocm`, eller `cpu`.

---

## Gå dypere — Bygg en AI-drevet app med Python

Den virkelige styrken til en lokal AI-server er at hvilken som helst applikasjon kan koble seg til den med bare noen få linjer kode. For å bevise dette skal vi bygge en liten, men funksjonell **studieflashcard-generator** der du gir den et emne, den genererer flashcards, og du kan teste deg selv interaktivt.

### Steg 4: Start serveren

Bekreft at Lemonade-serveren kjører. Den starter vanligvis automatisk i bakgrunnen etter installasjon. For å bekrefte, kjør:

```
lemonade status
```

Du bør se en melding som: `Server is running on port 13305`.

Hvis serveren ikke kjører, start den ved å åpne Lemonade-appen. Bruk standardporten **13305** (du kan bekrefte eller velge denne fra systemstatusfeltikonet).

### Steg 5: Installer OpenAI Python-klienten

I en terminal, opprett et venv og installer OpenAI Python-klienten med følgende kommandoer:
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

### Steg 6: Bygg flashcard-appen

La oss laste ned en annen modell for å generere kode: `Qwen3.5-35B-A3B-GGUF`. Dette er en stor (~20 GB) og ytelsessterk modell som passer best for systemer med 32 GB+ RAM. Hvis du har mindre tilgjengelig RAM, kan du prøve `Qwen3.5-9B-GGUF` (~6 GB) i stedet.

Du kan laste den ned fra brukergrensesnittet eller kjøre følgende:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Mat inn følgende prompt i Lemonade Chat UI for å generere kode for en enkel Flashcard-app.

Vi bruker Qwen3.5-35B-A3B-GGUF (en større modell som er bedre til å skrive kode) til å generere Python-appen vår, og selve appen vil kalle Gemma-4-E2B-it-GGUF (den mindre modellen du allerede har lastet ned) under kjøring. Koden kan deretter kopieres til en fil etter eget valg for å kjøres i Python.

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

> **Tips**: Vi har fulgt standard ingeniørpraksis gjennom grundig utforming av prompten og ved å bruke et to-modell-system for å optimalisere ressurser og hastighet.

For din bekvemmelighet har vi gitt et eksempel på output i [`flashcards.py`](assets/flashcards.py). Du kan gjerne laste den ned til katalogen din. Uansett hva du velger, bør du nå ha en Python-fil som kan kjøres.

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


### Steg 7: Kjør den genererte koden

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Her er hva du bør se:**

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

I omtrent 150 linjer kode har du bygget et fullt funksjonelt studieverktøy drevet av en lokal LLM. Det er ingen API-nøkkel å administrere, ingen brukskostnader, og ingen data forlater noensinne maskinen din.

> **Nøkkelinnsikt:** Legg merke til at linjen `client = OpenAI(base_url=...) ` er den *eneste* tingen som knytter denne appen til Lemonade i stedet for OpenAIs sky. Resten av koden er identisk med det du ville skrevet mot enhver OpenAI-kompatibel tjeneste. Hvis du noen gang har brukt OpenAI Python-biblioteket, vet du allerede hvordan du bygger apper med Lemonade.

### Hva dette demonstrerer

Denne lille appen tar i bruk flere praktiske integrasjonsmønstre fra den virkelige verden:

| Mønster | Hvor det forekommer |
|---------|-----------------|
| **Systemprompter** | `"system"`-meldingen forteller LLM-en å produsere strukturert JSON |
| **Strukturert output** | Appen tolker LLM-ens respons som JSON for å bygge flashcards |
| **Tilstandsløse forespørsler** | Hvert `generate_flashcards()`-kall er uavhengig |
| **Feilhåndtering** | `try/except` håndterer på en robust måte tilfeller der LLM-ens output ikke er gyldig JSON |

Disse samme mønstrene kan skaleres til enhver applikasjon, som chatbotter, kodeassistenter, innholdsgeneratorer, automatiseringsverktøy.

#### Bonusutfordring

* For en ekstra utfordring kan du prøve å oppdatere appen slik at flashcardene blir lest opp for brukeren, ved å referere til eksempelet gitt [her](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Kjøre modeller på NPU-en (valgfritt)

Hvis du har en Ryzen AI 300/400/Max 300-serie eller Z2 Extreme, har enheten din en innebygd **Neural Processing Unit (NPU)**, en dedikert brikke designet spesifikt for AI-arbeidslaster. Å kjøre modeller på NPU-en er mer strømeffektivt enn å bruke GPU-en, noe som gjør den ideell for AI-oppgaver i bakgrunnen, lengre økter og batteridrevet bruk.

Lemonade støtter tre NPU-kjøremodus, alle transparente bak det samme OpenAI API-et:

| Modus | Hvordan det fungerer | Oppskrift | Eksempelmodeller |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU behandler prompten, iGPU genererer tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Kun NPU** | Hele inferensen kjøres på NPU-en | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Bruker FastFlowLM-motoren på NPU-en, optimalisert for AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Krav

- **AMD Ryzen AI 300/400-serie eller Z2-serie**-prosessor
- For **FLM**-modeller: FLM-kjøretidsmiljøet kan installeres fra Lemonade-appen, eller Lemonade vil automatisk installere FLM-kjøretidsmiljøet når du kjører en FLM-modell. For å lære mer om FastFlowLM, se [her](https://fastflowlm.com/docs/).


### Trinn 8: Kjør en hybridmodell

Hybridmodeller fordeler arbeidet mellom NPU-en og iGPU-en for en god balanse mellom hastighet og effektivitet. I Lemonade-appen velger du en modell fra `Ryzen AI LLM`-listen, for eksempel `Qwen3-4B-Hybrid`, eller kjører den med følgende kommando:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade oppdager NPU-en din automatisk og installerer **Ryzen AI LLM**-motoren.

> **Hva skjer bak kulissene?** Når du sender en melding, behandler NPU-en hele prompten din parallelt (dette kalles "prefill"). Deretter overtar iGPU-en for å generere svaret ett token av gangen (dette kalles "decode"). Denne hybride tilnærmingen utnytter styrkene til hver brikke.

### Trinn 9: Kjør en FLM-modell

FastFlowLM (FLM)-modeller er spesifikt optimalisert for AMDs XDNA2 NPU-arkitektur og kan være svært raske for sin størrelse. Velg for eksempel `qwen3.5-4b-FLM` fra `FastFlowLM NPU`-listen, eller bruk følgende kommando:

<!-- @os:windows -->
For å aktivere `FastFlowLM` på Windows:

* Åpne menyen `Backends Manager`.
* Finn kategorien `FastFlowLM NPU`-motor.
* Klikk Install NPU.
* Når installasjonen er fullført, vil ~36 standardmodeller være tilgjengelige under FFLM-nedtrekksmenyen.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Når `Lemonade`-appen startes for første gang, er ikke `FastFlowNPU`-motoren aktivert som standard. 
Den lokale appen åpner installasjonssiden for å veilede deg gjennom oppsettet.

For å aktivere `FastFlowLM` på Linux:

* Åpne `Lemonade`-appen.
* Besøk den [offisielle FLM](https://lemonade-server.ai/flm_npu_linux.html)-dokumentasjonen og følg installasjonstrinnene for FLM ved å velge din Linux-distribusjon.
* Aktiver backports som instruert på installasjonssiden.
* Last ned den nyeste `v0.9.x`-utgivelsen fra [tags-siden](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
For AMD Halo Developer Platform, sørg for å velge Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Installer den nedlastede `.deb`-pakken.
* Anbefalt: Avslutt `Lemonade App` og åpne den igjen slik at endringene oppdages.
* Anbefalt: Åpne `Backends Manager` og klikk Install `FastFlowNPU`-motor.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Etter en vellykket installasjon bør du se at `flm:npu` er fullført i **Download Manager** inne i **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Du kan deretter velge en av de tilgjengelige FFLM-modellene og begynne å bruke NPU-motoren.

For en spesifikk modell, last ned ønsket modell fra [modellsiden](https://fastflowlm.com/docs/models/qwen/) og valider den med Shell-kommandoen som er oppgitt i dokumentasjonen.
```
flm run qwen3.5-4b-FLM
```
eller via 
```
lemonade run qwen3.5-4b-FLM
```

FLM-modeller inkluderer noen av de mest populære arkitekturene (Gemma 3, Qwen 3, Llama 3 og DeepSeek R1) og varierer fra under 1 GB til over 13 GB.
Lemonade oppdager NPU-en din automatisk og installerer **FastFlowLM NPU**-motoren.

<!-- @os:windows -->
> **Tips:** For best NPU-ytelse, aktiver turbo-modus:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Bytte modeller

Flashkort-appen fra trinn 6 fungerer også med NPU-modeller, bare endre modellnavnet:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Neste steg

Du har nå en lokal AI-server som kjører på din egen maskinvare, her er hvor du kan gå videre:

1. **Koble til favorittappene dine**: Lemonade fungerer rett ut av boksen med [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/), og [mange flere](https://lemonade-server.ai/marketplace).

2. **Utforsk flere modeller**: Utforsk hele [modellbiblioteket](https://lemonade-server.ai/docs/server/server_models/) for å finne modeller optimalisert for koding, resonnering, syn og mer. Bruk Lemonade-appen eller `lemonade list` for å se hva som er tilgjengelig.

3. **Lås opp ROCm GPU-akselerasjon**: Hvis du har en støttet AMD GPU, bytt til ROCm-motoren: `lemonade config set llamacpp.backend=rocm`. Se [støttede AMD GPU-er](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Les hele API-spesifikasjonen**: Lemonade støtter chat-fullføringer, embeddinger, lydtranskribering, bildegenerering, tekst-til-tale og mer. Se [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) for hvert endepunkt.

5. **Bidra**: Lemonade er åpen kildekode. Sjekk ut [bidragsguiden](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) og se etter [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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