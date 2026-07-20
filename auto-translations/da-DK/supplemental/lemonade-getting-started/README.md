<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Denne playbook bruger specielle tags, som GitHub ikke kan gengive. Besøg venligst [amd.com/playbooks](https://amd.com/playbooks) for at få vist dette indhold korrekt.
<!-- @github-only:end -->

## Oversigt

🍋 **Lemonade** er en open source lokal AI-server, der lader dig køre store sprogmodeller (LLM'er), billedgeneratorer og lydmodeller direkte på din egen hardware. Den eksponerer modellerne gennem den branchestandardiserede **OpenAI API**, så enhver app, der fungerer med OpenAI, øjeblikkeligt kan fungere med Lemonade. Ved afslutningen af denne playbook vil du bruge Lemonade til at køre modeller lokalt på din maskine.

## Hvad du vil lære

Ved afslutningen af denne playbook vil du kunne:

* **Installere Lemonade Server** og bekræfte, at den kører.
* **Downloade og chatte med en LLM** ved hjælp af en enkelt kommando.
* **Udforske web-UI'en** og prøve forskellige modaliteter såsom vision, tale-til-tekst og billedgenerering.
* **Skifte GPU-backends** mellem Vulkan og AMD ROCm™ software.
* **Bygge en Python-app** drevet af en lokal LLM ved hjælp af det OpenAI-kompatible API.
<!-- @device:halo_box,halo,stx,krk -->
* **Køre modeller på AMD Neural Processing Unit (NPU)** ved hjælp af Hybrid- og FLM-eksekveringstilstande på AMD Ryzen™ AI-hardware.
<!-- @device:end -->

## Indstilling af hukommelseskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tjek for softwareopdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger

Før du begynder, skal du sikre dig, at du har:

- En pc, der kører **Windows 11** eller en understøttet **Linux**-distribution (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** anbefales til den runtime-model, der bruges i trin 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** anbefales, hvis du vil bruge den større kodegenereringsmodel i trin 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB ledig diskplads**, afhængigt af de modeller, du downloader. Den største model i denne guide er cirka 20 GB.
- **Python 3.10–3.13** (bruges i afsnittet om Python-appen)
- En internetforbindelse (kablet eller trådløs)
<!-- @device:halo_box,halo,stx,krk -->
- [Valgfrit] En AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300-serien eller Z2 Extreme) med den nyeste driver installeret fra [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), hvis du vil køre en model på NPU'en.
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

## Kernebegreber — Hvordan lokale AI-servere fungerer

Før vi kører en model, er det værd at forstå *hvorfor* tingene er sat op på denne måde. Lemonade er en **lokal modelserver**, en proces, der indlæser AI-modeller i hukommelsen og eksponerer dem til applikationer via HTTP, ligesom en cloud-AI-tjeneste ville gøre.

### Hvorfor en server?

| Fordel | Hvad det betyder for dig |
|---------|----------------------|
| **Forenklet integration** | Apps taler med ét HTTP-API i stedet for at skulle håndtere hardwarespecifikke C++- eller Python-biblioteker. |
| **Delte modeller** | En enkelt indlæst model kan betjene flere apps på én gang, uden dublerede kopier, der spiser din RAM. |
| **Portabilitet fra cloud til lokal** | Kode skrevet til OpenAI's cloud-API fungerer med Lemonade ved blot at ændre én URL. |
| **Adskillelse af ansvar** | Modelhåndtering, streaming og fejltolerance håndteres af serveren, så udviklere kan fokusere på deres app. |

### OpenAI API-standarden

Lemonade implementerer **OpenAI API**, den samme grænseflade som bruges af ChatGPT, Azure OpenAI og adskillige andre tjenester. Samtalemodellen er enkel:

| Rolle | Hvem taler |
|------|---------------|
| **system** | Instruktioner til modellen (persona, begrænsninger, tilgængelige værktøjer) |
| **user** | Beskeder fra mennesket (eller applikationen) til modellen |
| **assistant** | Svar genereret af modellen |

Det betyder, at ethvert bibliotek eller enhver app, der understøtter OpenAI, kan tale med Lemonade ved at pege den mod `http://localhost:13305/api/v1`, mens Lemonade Server kører.

## Hovedaktivitet — Din første lokale AI-chat

Lad os downloade en LLM og føre en samtale med den, hvor AI'en kører fuldstændigt på din egen maskine.

### Trin 1: Download og kør en model

Lemonade leveres med et udvalgt modelbibliotek. Lad os starte med **Gemma-4-E2B-it**, en dygtig og kompakt model, der inkluderer understøttelse af vision. Åbn en terminal og kør:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Denne enkelte kommando gør tre ting:

1. **Downloader** modellen (~3 GB) fra Hugging Face, hvis den ikke allerede er downloadet. (Kan tage noget tid)
2. **Starter** Lemonade Server-processen på port 13305.
3. **Åbner Lemonade App**, så du kan begynde at chatte med modellen.


<!-- @os:windows -->
På Windows starter Lemonade App automatisk, og du kan begynde at chatte med det samme. Hvis du har installeret `minimal.msi`-pakken, er appen ikke inkluderet. For at begynde at chatte skal du åbne din webbrowser og gå til `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
På Linux skal du åbne din browser og navigere til `http://localhost:13305` for at få adgang til web-appen.
<!-- @os:end -->

Prøv at skrive et spørgsmål:

```
What are three fun facts about lemons?
```

Modellen vil svare direkte i chatvinduet. **Tillykke! Du kører nu en stor sprogmodel lokalt.**

![Lemonade App med logs vist](../../dependencies/assets/ChatwithLogs.png)

I panelet Server Logs i Lemonade App kan du finde telemetridata om modellens ydeevne efter hvert svar. For eksempel:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Trin 2: Udforsk webgrænsefladen og forskellige modaliteter

Lemonade indeholder en indbygget webgrænseflade, hvor du kan:

- **Interagere** med den indlæste model i et velkendt chatvindue
- **Gennemse modeller** under fanen Model Manager
- **Downloade nye modeller** med ét klik

Prøv at skifte mellem forskellige modaliteter ved hjælp af fanen **Model Manager** i webgrænsefladen, hvor du kan gennemse modeller efter Recipe eller efter Category:

1. **Vision:** Modellen `Gemma-4-E2B-it-GGUF`, som du allerede har indlæst, understøtter vision. Indsæt et billede i chatboksen, og bed modellen om at beskrive det.
2. **Billedgenerering:** I kategorien Image kan du downloade en billedmodel som f.eks. `SDXL-Turbo` fra Model Manager og derefter bruge Lemonade Image Generator til at skrive en prompt og generere et billede lokalt.
3. **Lyd:** I kategorien Audio kan du downloade en lydmodel som f.eks. `Whisper-Tiny`, der kan udføre speech-to-text. Angiv en lydoptagelse for at transskribere den lokalt. For text-to-speech kan du prøve en af modellerne i kategorien Speech, f.eks. `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### Trin 3: Prøv en model med en anden backend

Hvis du holder musen over en model i Lemonade-appen, ser du et tandhjulsikon. Klikker du på dette, kan du vælge indstillinger for modellen, herunder den ønskede backend.

Som standard bruger Lemonade Vulkan til GPU-acceleration. Hvis du har en understøttet AMD-diskret GPU, kan du skifte til ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

For at administrere dine installerede backends skal du klikke på backend-knappen i kolonnen længst til venstre.

Alternativt kan du angive backend ved hjælp af følgende kommando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Du kan også indstille din standardbackend ved hjælp af miljøvariablen `LEMONADE_LLAMACPP` med værdierne: `vulkan`, `rocm` eller `cpu`.

---

## Gå i dybden — Byg en AI-drevet app med Python

Den egentlige styrke ved en lokal AI-server er, at enhver applikation kan oprette forbindelse til den med blot nogle få linjer kode. For at bevise det skal vi bygge en lille, men funktionel **studieflashcard-generator**, hvor du angiver et emne, og den genererer flashcards, som du derefter kan quizze dig selv med interaktivt.

### Trin 4: Start serveren

Bekræft, at Lemonade-serveren kører. Den starter typisk automatisk i baggrunden efter installation. For at bekræfte dette skal du køre:

```
lemonade status
```

Du skulle se en besked som: `Server is running on port 13305`.

Hvis serveren ikke kører, skal du starte den ved at åbne Lemonade-appen. Brug standardporten **13305** (du kan bekræfte eller vælge denne fra proceslinjeikonet).

### Trin 5: Installer OpenAI Python Client

I en terminal skal du oprette et venv og installere OpenAI Python Client ved hjælp af følgende kommandoer:
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

### Trin 6: Byg flashcard-appen

Lad os downloade en anden model til at generere kode: `Qwen3.5-35B-A3B-GGUF`. Dette er en stor (~20 GB) og performant model, der er bedst egnet til systemer med 32 GB+ RAM. Hvis du har mindre RAM til rådighed, kan du i stedet prøve `Qwen3.5-9B-GGUF` (~6 GB).

Du kan downloade den fra brugergrænsefladen eller køre følgende:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Indsæt følgende prompt i Lemonade Chat UI for at generere kode til en simpel Flashcard-app.

Vi vil bruge Qwen3.5-35B-A3B-GGUF (en større model, som er bedre til at skrive kode) til at generere vores Python-app, og selve appen vil kalde Gemma-4-E2B-it-GGUF (den mindre model, du allerede har downloadet) ved runtime. Koden kan derefter kopieres til en fil efter eget valg, som kan køres i Python.

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

> **Tip**: Vi har fulgt god ingeniørpraksis ved grundig prompt-udformning og ved at bruge et to-model-system for at optimere ressourcer og hastighed.

For nemheds skyld har vi leveret et eksempel på output i [`flashcards.py`](assets/flashcards.py). Du er velkommen til at downloade den til dit bibliotek. Under alle omstændigheder bør du nu have en Python-fil, der kan køres.

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


### Trin 7: Kør den genererede kode

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Her er, hvad du bør se:**

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

På omkring 150 linjer kode har du bygget et fuldt funktionelt studieværktøj drevet af en lokal LLM. Der er ingen API-nøgle at administrere, ingen brugsomkostninger, og ingen data forlader nogensinde din maskine.

> **Vigtig indsigt:** Bemærk, at linjen `client = OpenAI(base_url=...) ` er det *eneste*, der binder denne app til Lemonade i stedet for OpenAI's cloud. Resten af koden er identisk med, hvad du ville skrive mod enhver OpenAI-kompatibel tjeneste. Hvis du nogensinde har brugt OpenAI Python-biblioteket, ved du allerede, hvordan man bygger apps med Lemonade.

### Hvad dette demonstrerer

Denne lille app bruger flere virkelige integrationsmønstre:

| Mønster | Hvor det optræder |
|---------|-----------------|
| **Systemprompter** | `"system"`-beskeden fortæller LLM'en at output skal være struktureret JSON |
| **Struktureret output** | Appen fortolker LLM'ens svar som JSON for at bygge flashcards |
| **Statsløse forespørgsler** | Hvert `generate_flashcards()`-kald er uafhængigt |
| **Fejlhåndtering** | `try/except` håndterer elegant tilfælde, hvor LLM'ens output ikke er gyldig JSON |

Disse samme mønstre skalerer til enhver applikation, såsom chatbots, kodeassistenter, indholdsgeneratorer og automatiseringsværktøjer.

#### Bonusudfordring

* For en ekstra udfordring kan du prøve at opdatere appen, så flashcards bliver læst højt for brugeren, ved at tage udgangspunkt i eksemplet [her](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Kørsel af modeller på NPU'en (valgfrit)

Hvis du har en Ryzen AI 300/400/Max 300-serie eller Z2 Extreme, har din enhed en indbygget **Neural Processing Unit (NPU)**, en dedikeret chip designet specifikt til AI-arbejdsbelastninger. Kørsel af modeller på NPU'en er mere strømeffektiv end at bruge GPU'en, hvilket gør den ideel til AI-opgaver i baggrunden, længere sessioner og batteridrevet brug.

Lemonade understøtter tre NPU-eksekveringstilstande, som alle er transparente bag den samme OpenAI API:

| Tilstand | Sådan fungerer det | Recipe | Eksempelmodeller |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU behandler prompten, iGPU genererer tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Kun NPU** | Hele inferensen kører på NPU'en | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Bruger FastFlowLM-motoren på NPU'en, optimeret til AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Krav

- **AMD Ryzen AI 300/400-serie eller Z2-serie** processor
- For **FLM**-modeller: FLM-runtimen kan installeres direkte fra Lemonade-appen, eller Lemonade installerer automatisk FLM-runtimen, når en FLM-model køres. For at lære mere om FastFlowLM, se [her](https://fastflowlm.com/docs/).


### Trin 8: Kør en hybrid model

Hybride modeller fordeler arbejdet mellem NPU'en og iGPU'en for at opnå en god balance mellem hastighed og effektivitet. I Lemonade-appen skal du vælge en model fra `Ryzen AI LLM`-listen, for eksempel `Qwen3-4B-Hybrid`, eller køre den med følgende kommando:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade registrerer automatisk din NPU og installerer **Ryzen AI LLM**-backenden.

> **Hvad sker der i baggrunden?** Når du sender en besked, behandler NPU'en hele din prompt parallelt (dette kaldes "prefill"). Derefter overtager iGPU'en for at generere svaret ét token ad gangen (dette kaldes "decode"). Denne hybride tilgang udnytter hver chips styrker.

### Trin 9: Kør en FLM-model

FastFlowLM (FLM)-modeller er specifikt optimeret til AMD's XDNA2 NPU-arkitektur og kan være meget hurtige i forhold til deres størrelse. Vælg for eksempel `qwen3.5-4b-FLM` fra `FastFlowLM NPU`-listen, eller brug følgende kommando:

<!-- @os:windows -->
Sådan aktiverer du `FastFlowLM` på Windows:

* Åbn menuen `Backends Manager`.
* Find backend-kategorien `FastFlowLM NPU`.
* Klik på Install NPU.
* Når installationen er fuldført, vil ~36 standardmodeller være tilgængelige under FFLM-dropdown-menuen.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Når `Lemonade`-appen startes for første gang, er `FastFlowNPU`-backenden ikke aktiveret som standard.
Den lokale app åbner installationssiden for at guide dig gennem opsætningen.

Sådan aktiverer du `FastFlowLM` på Linux:

* Åbn `Lemonade`-appen.
* Besøg den [officielle FLM](https://lemonade-server.ai/flm_npu_linux.html)-dokumentation, og følg installationstrinnene for FLM ved at vælge din Linux-distribution.
* Aktivér backports som beskrevet på installationssiden.
* Download den nyeste `v0.9.x`-udgivelse fra [tags-siden](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
For AMD Halo Developer Platform skal du sørge for at vælge Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Installér den downloadede `.deb`-pakke.
* Anbefalet: Luk `Lemonade App` og åbn den igen, så ændringerne registreres.
* Anbefalet: Åbn `Backends Manager`, og klik på Install `FastFlowNPU`-backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Efter en vellykket installation bør du se, at `flm:npu` er fuldført i **Download Manager** inde i **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Du kan derefter vælge en hvilken som helst af de tilgængelige FFLM-modeller og begynde at bruge NPU-backenden.

For en specifik model kan du downloade den ønskede model fra [modelsiden](https://fastflowlm.com/docs/models/qwen/) og validere den ved hjælp af Shell-kommandoen, der er angivet i dokumentationen.
```
flm run qwen3.5-4b-FLM
```
eller via 
```
lemonade run qwen3.5-4b-FLM
```

FLM-modeller omfatter nogle af de mest populære arkitekturer (Gemma 3, Qwen 3, Llama 3 og DeepSeek R1) og spænder fra under 1 GB til over 13 GB.
Lemonade registrerer automatisk din NPU og installerer **FastFlowLM NPU**-backenden.

<!-- @os:windows -->
> **Tip:** For den bedste NPU-ydeevne skal du aktivere turbo-tilstand:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Skift af modeller

Flashcard-appen fra trin 6 fungerer også med NPU-modeller, du skal blot ændre modelnavnet:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Næste skridt

Du har nu en lokal AI-server, der kører på din egen hardware. Her er, hvad du kan gøre næste:

1. **Forbind dine yndlingsapps**: Lemonade fungerer ud af boksen med [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) og [mange flere](https://lemonade-server.ai/marketplace).

2. **Gennemse flere modeller**: Udforsk hele [modelbiblioteket](https://lemonade-server.ai/docs/server/server_models/) for at finde modeller optimeret til kodning, ræsonnement, syn og meget mere. Brug Lemonade-appen eller `lemonade list` for at se, hvad der er tilgængeligt.

3. **Lås op for ROCm GPU-acceleration**: Hvis du har en understøttet AMD GPU, skal du skifte til ROCm-backenden: `lemonade config set llamacpp.backend=rocm`. Se [understøttede AMD GPU'er](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Læs hele API-specifikationen**: Lemonade understøtter chat completions, embeddings, lydtranskription, billedgenerering, tekst-til-tale og mere. Se [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) for hvert endpoint.

5. **Bidrag**: Lemonade er open source. Se [bidragsguiden](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md), og kig efter [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).