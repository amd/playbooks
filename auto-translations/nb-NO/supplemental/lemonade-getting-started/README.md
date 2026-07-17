<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Denne spilleboken bruker spesielle tagger som GitHub ikke kan gjengi. Besøk [amd.com/playbooks](https://amd.com/playbooks) for å forhåndsvise innholdet korrekt.
<!-- @github-only:end -->

## Oversikt

🍋 **Lemonade** er en åpen kildekode lokal AI-server som lar deg kjøre store språkmodeller (LLM-er), bildegeneratorer og lydmodeller direkte på din egen maskinvare. Den eksponerer modellene gjennom den bransjestandardiserte **OpenAI API**, slik at enhver app som fungerer med OpenAI umiddelbart kan fungere med Lemonade. Innen slutten av spilleboken vil du bruke Lemonade til å kjøre modeller lokalt på maskinen din.

## Hva Du Vil Lære

Innen slutten av denne spilleboken vil du kunne:

* **Installere Lemonade Server** og bekrefte at den kjører.
* **Laste ned og chatte med en LLM** ved hjelp av én enkelt kommando.
* **Utforske nettgrensesnittet** og prøve ulike modaliteter som syn, tale-til-tekst og bildegenerering.
* **Bytte GPU-backend** mellom Vulkan og AMD ROCm™-programvare.
* **Bygge en Python-app** drevet av en lokal LLM ved hjelp av det OpenAI-kompatible API-et.
<!-- @device:halo_box,halo,stx,krk -->
* **Kjøre modeller på AMD Neural Processing Unit (NPU)** ved hjelp av Hybrid- og FLM-kjøringsmodi på AMD Ryzen™ AI-maskinvare.
<!-- @device:end -->

## Konfigurere Minneinnstillingen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Se Etter Programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installere Programvareforutsetninger

Før du begynner, sørg for at du har:

- En PC som kjører **Windows 11** eller en støttet **Linux**-distribusjon (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** anbefales for kjøretidsmodellen som brukes i trinn 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** anbefales hvis du vil bruke den større kodegeneringsmodellen i trinn 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB ledig diskplass**, avhengig av hvilke modeller du laster ned. Den største modellen i denne veiledningen er omtrent 20 GB.
- **Python 3.10–3.13** (brukes i Python-app-seksjonen)
- En internettforbindelse (kablet eller trådløs)
<!-- @device:halo_box,halo,stx,krk -->
- [Valgfritt] En AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300-serien eller Z2 Extreme) med den nyeste driveren installert fra [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) hvis du vil kjøre en modell på NPU-en.
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

## Kjernekonsepter — Slik Fungerer Lokale AI-servere

Før vi kjører en modell, er det verdt å forstå *hvorfor* ting er satt opp på denne måten. Lemonade er en **lokal modellserver**, en prosess som laster AI-modeller inn i minnet og eksponerer dem for applikasjoner over HTTP, akkurat som en sky-AI-tjeneste ville gjort.

### Hvorfor en Server?

| Fordel | Hva Det Betyr for Deg |
|---------|----------------------|
| **Forenklet integrasjon** | Apper kommuniserer med ett HTTP API i stedet for å håndtere maskinvarespesifikke C++- eller Python-biblioteker. |
| **Delte modeller** | En enkelt lastet modell kan betjene flere apper samtidig, uten dupliserte kopier som spiser opp RAM-en din. |
| **Sky-til-lokal portabilitet** | Kode skrevet for OpenAIs sky-API fungerer med Lemonade ved å endre én URL. |
| **Separasjon av ansvarsområder** | Modellhåndtering, strømming og feiltoleranse håndteres av serveren slik at utviklere kan fokusere på appen sin. |

### OpenAI API-standarden

Lemonade implementerer **OpenAI API**, det samme grensesnittet som brukes av ChatGPT, Azure OpenAI og dusinvis av andre tjenester. Samtalemodellen er enkel:

| Rolle | Hvem Som Snakker |
|------|---------------|
| **system** | Instruksjoner til modellen (persona, begrensninger, tilgjengelige verktøy) |
| **user** | Meldinger fra mennesket (eller applikasjonen) til modellen |
| **assistant** | Svar generert av modellen |

Dette betyr at ethvert bibliotek eller app som støtter OpenAI kan kommunisere med Lemonade ved å peke det mot `http://localhost:13305/api/v1` mens Lemonade Server kjører.

## Hovedaktivitet — Din Første Lokale AI-chat

La oss laste ned en LLM og ha en samtale med den, og kjøre AI-en helt på din egen maskin.

### Trinn 1: Last ned og Kjør en Modell

Lemonade leveres med et kuratert modellbibliotek. La oss starte med **Gemma-4-E2B-it**, en kapabel og kompakt modell som inkluderer synsstøtte. Åpne en terminal og kjør:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Denne enkle kommandoen gjør tre ting:

1. **Laster ned** modellen (~3 GB) fra Hugging Face, hvis den ikke allerede er lastet ned. (Kan ta litt tid)
2. **Starter** Lemonade Server-prosessen på port 13305.
3. **Åpner Lemonade App** slik at du kan begynne å chatte med modellen.


<!-- @os:windows -->
På Windows starter Lemonade App automatisk og du kan begynne å chatte umiddelbart. Hvis du installerte `minimal.msi`-pakken, er ikke appen inkludert. For å begynne å chatte, åpne nettleseren din og gå til `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
På Linux, åpne nettleseren din og naviger til `http://localhost:13305` for å få tilgang til nettappen.
<!-- @os:end -->

Prøv å skrive et spørsmål:

```
What are three fun facts about lemons?
```

Modellen vil svare direkte i chatvinduet. **Gratulerer! Du kjører en stor språkmodell lokalt.**

![Lemonade App med logger vist](../../dependencies/assets/ChatwithLogs.png)

I Server Logs-ruten i Lemonade App kan du finne telemetridata om modellens ytelse etter hvert svar. For eksempel:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Trinn 2: Utforsk Nettgrensesnittet og Ulike Modaliteter

Lemonade inkluderer et innebygd nettgrensesnitt der du kan:

- **Samhandle** med den lastede modellen i et kjent chatvindu
- **Bla gjennom modeller** i Model Manager-fanen
- **Laste ned nye modeller** med ett klikk

Prøv å bytte mellom ulike modaliteter ved hjelp av **Model Manager**-fanen i nettgrensesnittet der du kan bla gjennom modeller etter Oppskrift eller etter Kategori:

1. **Syn:** `Gemma-4-E2B-it-GGUF`-modellen du allerede har lastet støtter syn. Lim inn et bilde i chatboksen og be modellen om å beskrive det.
2. **Bildegenerering:** I Bilde-kategorien, last ned en bildemodell som `SDXL-Turbo` fra Model Manager, og bruk deretter Lemonade Image Generator til å skrive en prompt og generere et bilde lokalt.
3. **Lyd:** I Lyd-kategorien, last ned en lydmodell som `Whisper-Tiny`, som kan gjøre tale-til-tekst. Gi en lydopptak for å transkribere det lokalt. For tekst-til-tale, prøv en av modellene i Tale-kategorien, som `kokoro-v1`.

![Multi-modalitet med Lemonade](../../dependencies/assets/multi_modality.png)

### Trinn 3: Prøv en Modell med en Annen Backend

Hvis du holder musepekeren over en modell i Lemonade App, vil du se et tannhjulikon. Å klikke på dette lar deg velge alternativer for modellen, inkludert å velge ønsket backend.

Som standard bruker Lemonade Vulkan for GPU-akselerasjon. Hvis du har en støttet AMD diskret GPU, kan du bytte til ROCm.

![Lemonade Velg Backend](../../dependencies/assets/lemonademodeloptions.png)

For å administrere dine installerte backends, klikk på backend-knappen i den venstre kolonnen.

Alternativt kan du spesifisere backend ved hjelp av følgende kommando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Du kan også angi din standard backend ved hjelp av miljøvariabelen `LEMONADE_LLAMACPP` med verdiene: `vulkan`, `rocm` eller `cpu`.

---

## Gå Dypere — Bygg en AI-drevet App med Python

Den virkelige kraften til en lokal AI-server er at enhver applikasjon kan koble seg til den ved hjelp av bare noen få kodelinjer. For å bevise det, la oss bygge en liten men funksjonell **studieflashkort-generator** der du gir den et emne, den genererer flashkort, og du kan teste deg selv interaktivt.

### Trinn 4: Start Serveren

Bekreft at Lemonade-serveren kjører. Den starter vanligvis automatisk i bakgrunnen etter installasjon. For å bekrefte, kjør:

```
lemonade status
```

Du bør se en melding som: `Server is running on port 13305`.

Hvis serveren ikke kjører, start den ved å åpne Lemonade-appen. Bruk standardporten **13305** (du kan bekrefte eller velge dette fra systemstatusfeltikonet).

### Trinn 5: Installer OpenAI Python-klienten

I en terminal, opprett et venv og installer OpenAI Python-klienten ved hjelp av følgende kommandoer:
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

### Trinn 6: Bygg Flashkort-appen

La oss laste ned en annen modell for å generere kode: `Qwen3.5-35B-A3B-GGUF`. Dette er en stor (~20 GB) og ytelsesdyktig modell som passer best for systemer med 32 GB+ RAM. Hvis du har mindre RAM tilgjengelig, prøv `Qwen3.5-9B-GGUF` (~6 GB) i stedet.

Du kan laste den ned fra grensesnittet eller kjøre følgende:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Legg inn følgende prompt i Lemonade Chat UI for å generere kode for en enkel Flashkort-app.

Vi vil bruke Qwen3.5-35B-A3B-GGUF (en større modell som er bedre til å skrive kode) for å generere Python-appen vår, og selve appen vil kalle Gemma-4-E2B-it-GGUF (den mindre modellen du allerede lastet ned) ved kjøretid. Koden kan deretter kopieres til en valgfri fil for å kjøres i Python.

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

> **Tips**: Vi har fulgt standard ingeniørpraksis gjennom grundig promptoppretting og ved å bruke et to-modell-system for å optimalisere ressurser og hastighet.

For din bekvemmelighet har vi levert eksempelutdata i [`flashcards.py`](assets/flashcards.py). Du er velkommen til å laste den ned til katalogen din. Uansett bør du nå ha en Python-fil som kan kjøres.

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


### Trinn 7: Kjør den Genererte Koden

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

På omtrent 150 kodelinjer har du bygget et fullt funksjonelt studieverktøy drevet av en lokal LLM. Det er ingen API-nøkkel å administrere, ingen brukskostnader, og ingen data forlater noen gang maskinen din.

> **Viktig innsikt:** Legg merke til at `client = OpenAI(base_url=...) `-linjen er det *eneste* som knytter denne appen til Lemonade i stedet for OpenAIs sky. Resten av koden er identisk med det du ville skrevet mot enhver OpenAI-kompatibel tjeneste. Hvis du noen gang har brukt OpenAI Python-biblioteket, vet du allerede hvordan du bygger apper med Lemonade.

### Hva Dette Demonstrerer

Denne lille appen øver på flere virkelige integrasjonsmønstre:

| Mønster | Hvor Det Vises |
|---------|-----------------|
| **Systemprompts** | `"system"`-meldingen forteller LLM-en å sende ut strukturert JSON |
| **Strukturert utdata** | Appen analyserer LLM-ens svar som JSON for å bygge flashkort |
| **Tilstandsløse forespørsler** | Hvert `generate_flashcards()`-kall er uavhengig |
| **Feilhåndtering** | `try/except` håndterer på en elegant måte tilfeller der LLM-ens utdata ikke er gyldig JSON |

Disse samme mønstrene skalerer til enhver applikasjon som chatbots, kodeassistenter, innholdsgeneratorer og automatiseringsverktøy.

#### Bonusutfordring

* For en ekstra utfordring, prøv å oppdatere appen slik at flashkortene leses opp for brukeren ved å referere til eksempelet gitt [her](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Kjøre Modeller på NPU-en (Valgfritt)

Hvis du har en Ryzen AI 300/400/Max 300-serie eller Z2 Extreme, har enheten din en innebygd **Neural Processing Unit (NPU)**, en dedikert brikke spesielt designet for AI-arbeidsbelastninger. Å kjøre modeller på NPU-en er mer energieffektivt enn å bruke GPU-en, noe som gjør det ideelt for bakgrunns-AI-oppgaver, lengre økter og batteridrevet bruk.

Lemonade støtter tre NPU-kjøringsmodi, alle transparente bak det samme OpenAI API:

| Modus | Slik Fungerer Det | Oppskrift | Eksempelmodeller |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU behandler prompten, iGPU genererer tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Kun NPU** | Hele inferensen kjører på NPU-en | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Bruker FastFlowLM-motoren på NPU-en, optimalisert for AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Krav

- **AMD Ryzen AI 300/400-serie eller Z2-serie** prosessor
- For **FLM**-modeller: FLM-kjøretiden kan installeres fra Lemonade-appen, eller Lemonade vil automatisk installere FLM-kjøretiden når en FLM-modell kjøres. For å lære mer om FastFlowLM, se [her](https://fastflowlm.com/docs/).


### Trinn 8: Kjør en Hybrid-modell

Hybridmodeller deler arbeid mellom NPU-en og iGPU-en for en god balanse mellom hastighet og effektivitet. I Lemonade App, velg en modell fra `Ryzen AI LLM`-listen, for eksempel `Qwen3-4B-Hybrid`, eller kjør den ved hjelp av følgende kommando:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade oppdager NPU-en din automatisk og installerer **Ryzen AI LLM**-backend.

> **Hva skjer under panseret?** Når du sender en melding, behandler NPU-en hele prompten din parallelt (dette kalles "prefill"). Deretter tar iGPU-en over for å generere svaret ett token om gangen (dette kalles "decode"). Denne hybridtilnærmingen spiller på styrkene til hver brikke.

### Trinn 9: Kjør en FLM-modell

FastFlowLM (FLM)-modeller er spesifikt optimalisert for AMDs XDNA2 NPU-arkitektur og kan være svært raske for sin størrelse. For eksempel, velg `qwen3.5-4b-FLM` fra `FastFlowLM NPU`-listen eller bruk følgende kommando:

<!-- @os:windows -->
For å aktivere `FastFlowLM` på Windows:

* Åpne `Backends Manager`-menyen.
* Finn `FastFlowLM NPU`-backend-kategorien.
* Klikk Installer NPU.
* Når installasjonen er fullført, vil ~36 standardmodeller være tilgjengelige under FFLM-rullegardinmenyen.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Når `Lemonade`-appen startes for første gang, er ikke `FastFlowNPU`-backend aktivert som standard.
Den lokale appen vil åpne installasjonssiden for å veilede deg gjennom oppsettet.

For å aktivere `FastFlowLM` på Linux:

* Åpne `Lemonade`-appen.
* Besøk den [offisielle FLM](https://lemonade-server.ai/flm_npu_linux.html)-dokumentasjonen og følg installasjonstrinnene for FLM ved å velge din Linux-distribusjon.
* Aktiver backports som instruert på installasjonssiden.
* Last ned den nyeste `v0.9.x`-utgivelsen fra [tags-siden](https://github.com/FastFlowLM/FastFlowLM/tags).
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
* Anbefalt: Åpne `Backends Manager` og klikk Installer `FastFlowNPU`-backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Etter en vellykket installasjon bør du se at `flm:npu` er fullført i **Download Manager** inne i **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Du kan deretter velge hvilken som helst av de tilgjengelige FFLM-modellene og begynne å bruke NPU-backend.

For en spesifikk modell, last ned ønsket modell fra [modellsiden](https://fastflowlm.com/docs/models/qwen/) og valider den ved hjelp av Shell-kommandoen som er gitt i dokumentasjonen.
```
flm run qwen3.5-4b-FLM
```
eller via 
```
lemonade run qwen3.5-4b-FLM
```

FLM-modeller inkluderer noen av de mest populære arkitekturene (Gemma 3, Qwen 3, Llama 3 og DeepSeek R1) og varierer fra under 1 GB til over 13 GB.
Lemonade oppdager NPU-en din automatisk og installerer **FastFlowLM NPU**-backend.

<!-- @os:windows -->
> **Tips:** For best NPU-ytelse, aktiver turbo-modus:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Bytte Modeller

Flashkort-appen fra trinn 6 fungerer også med NPU-modeller, bare endre modellnavnet:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Neste Steg

Du har en lokal AI-server som kjører på din egen maskinvare, her er hvor du kan gå videre:

1. **Koble til favorittappene dine**: Lemonade fungerer rett ut av boksen med [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) og [mange flere](https://lemonade-server.ai/marketplace).

2. **Bla gjennom flere modeller**: Utforsk det fullstendige [modellbiblioteket](https://lemonade-server.ai/docs/server/server_models/) for å finne modeller optimalisert for koding, resonnering, syn og mer. Bruk Lemonade App eller `lemonade list` for å se hva som er tilgjengelig.

3. **Lås opp ROCm GPU-akselerasjon**: Hvis du har en støttet AMD GPU, bytt til ROCm-backend: `lemonade config set llamacpp.backend=rocm`. Se [støttede AMD GPU-er](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Les den fullstendige API-spesifikasjonen**: Lemonade støtter chat-fullføringer, innbygginger, lydtranskripsjon, bildegenerering, tekst-til-tale og mer. Se [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) for hvert endepunkt.

5. **Bidra**: Lemonade er åpen kildekode. Sjekk ut [bidragsguiden](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) og se etter [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).