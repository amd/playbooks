<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Översikt

🍋 **Lemonade** är en AI-server med öppen källkod för lokal körning som låter dig köra stora språkmodeller (LLM:er), bildgeneratorer och ljudmodeller direkt på din egen hårdvara. Den exponerar modellerna via det branschstandardiserade **OpenAI API**, så alla appar som fungerar med OpenAI kan omedelbart fungera med Lemonade. När du har gått igenom den här guiden kommer du att använda Lemonade för att köra modeller lokalt på din dator.

## Vad du kommer att lära dig

När du har gått igenom den här guiden kommer du att kunna:

* **Installera Lemonade Server** och verifiera att den körs.
* **Ladda ner och chatta med en LLM** med ett enda kommando.
* **Utforska webbgränssnittet** och prova olika modaliteter som syn, tal-till-text och bildgenerering.
* **Växla GPU-backend** mellan Vulkan och AMD ROCm™-mjukvara.
* **Bygga en Python-app** driven av en lokal LLM med hjälp av det OpenAI-kompatibla API:et.
<!-- @device:halo_box,halo,stx,krk -->
* **Köra modeller på AMD:s Neural Processing Unit (NPU)** med Hybrid- och FLM-körlägen på AMD Ryzen™ AI-hårdvara.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Ställa in minneskonfigurationen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrollera om det finns programvaruuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Installera nödvändig programvara

Innan du börjar, se till att du har:

- En dator med **Windows 11** eller en Linux-distribution som stöds (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** rekommenderas för körtidsmodellen som används i steg 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** rekommenderas om du vill använda den större kodgenereringsmodellen i steg 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB ledigt diskutrymme**, beroende på vilka modeller du laddar ner. Den största modellen i den här guiden är cirka 20 GB.
- **Python 3.10–3.13** (används i avsnittet om Python-appen)
- En internetanslutning (trådbunden eller trådlös)
<!-- @device:halo_box,halo,stx,krk -->
- [Valfritt] En AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300-serien eller Z2 Extreme) med den senaste drivrutinen installerad från [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) om du vill köra en modell på NPU:n.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade-models-gemma-4-e2b -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
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

## Grundläggande koncept — Hur lokala AI-servrar fungerar

Innan vi kör en modell är det värt att förstå *varför* saker är uppsatta på det här sättet. Lemonade är en **lokal modellserver**, en process som laddar AI-modeller i minnet och exponerar dem för applikationer via HTTP, precis som en molnbaserad AI-tjänst skulle göra.

### Varför en server?

| Fördel | Vad det betyder för dig |
|---------|----------------------|
| **Förenklad integration** | Appar kommunicerar med ett enda HTTP-API istället för att hantera hårdvaruspecifika C++- eller Python-bibliotek. |
| **Delade modeller** | En enda laddad modell kan betjäna flera appar samtidigt, utan duplicerade kopior som tar upp ditt RAM-minne. |
| **Portabilitet mellan moln och lokalt** | Kod skriven för OpenAI:s molnbaserade API fungerar med Lemonade genom att bara ändra en URL. |
| **Åtskillnad av ansvarsområden** | Modellhantering, strömning och feltolerans hanteras av servern så att utvecklare kan fokusera på sin app. |

### OpenAI API-standarden

Lemonade implementerar **OpenAI API**, samma gränssnitt som används av ChatGPT, Azure OpenAI och dussintals andra tjänster. Konversationsmodellen är enkel:

| Roll | Vem som talar |
|------|---------------|
| **system** | Instruktioner till modellen (persona, begränsningar, tillgängliga verktyg) |
| **user** | Meddelanden från människan (eller applikationen) till modellen |
| **assistant** | Svar som genereras av modellen |

Det innebär att alla bibliotek eller appar som stöder OpenAI kan kommunicera med Lemonade genom att peka den mot `http://localhost:13305/api/v1` medan Lemonade Server körs.

## Huvudaktivitet — Din första lokala AI-chatt

Låt oss ladda ner en LLM och föra ett samtal med den, och köra AI:n helt och hållet på din egen dator.

### Steg 1: Ladda ner och kör en modell

Lemonade levereras med ett noggrant sammanställt modellbibliotek. Låt oss börja med **Gemma-4-E2B-it**, en kapabel och kompakt modell som inkluderar stöd för syn. Öppna en terminal och kör:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Det här enstaka kommandot gör tre saker:

1. **Laddar ner** modellen (~3 GB) från Hugging Face, om den inte redan har laddats ner. (Kan ta en stund)
2. **Startar** Lemonade Server-processen på port 13305.
3. **Öppnar Lemonade App** så att du kan börja chatta med modellen.


<!-- @os:windows -->
I Windows startas Lemonade App automatiskt och du kan börja chatta direkt. Om du installerade paketet `minimal.msi` ingår inte appen. För att börja chatta, öppna din webbläsare och gå till `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
I Linux öppnar du din webbläsare och navigerar till `http://localhost:13305` för att komma åt webbappen.
<!-- @os:end -->

Prova att skriva en fråga:

```
What are three fun facts about lemons?
```

Modellen svarar direkt i chattfönstret. **Grattis! Du kör nu en stor språkmodell lokalt.**

![Lemonade App med loggar visade](../../dependencies/assets/ChatwithLogs.png)

I panelen Server Logs i Lemonade App kan du hitta telemetridata om modellens prestanda efter varje svar. Till exempel:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Steg 2: Utforska webbgränssnittet och olika modaliteter

Lemonade har ett inbyggt webbgränssnitt där du kan:

- **Interagera** med den laddade modellen i ett välbekant chattfönster
- **Bläddra bland modeller** på fliken Model Manager
- **Ladda ner nya modeller** med ett klick

Prova att växla mellan olika modaliteter med fliken **Model Manager** i webbgränssnittet, där du kan bläddra bland modeller efter Recipe eller efter Category:

1. **Vision:** Modellen `Gemma-4-E2B-it-GGUF` som du redan har laddat stöder vision. Klistra in en bild i chattrutan och be modellen beskriva den.
2. **Bildgenerering:** I kategorin Image, ladda ner en bildmodell som `SDXL-Turbo` från Model Manager, och använd sedan Lemonade Image Generator för att skriva en prompt och generera en bild lokalt.
3. **Ljud:** I kategorin Audio, ladda ner en ljudmodell som `Whisper-Tiny`, som kan göra tal-till-text. Ange en ljudinspelning för att transkribera den lokalt. För text-till-tal, prova en av modellerna i kategorin Speech, till exempel `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### Steg 3: Prova en modell med en annan backend

Om du håller muspekaren över en modell i Lemonade App ser du en kugghjulsikon. Om du klickar på den kan du välja alternativ för modellen, inklusive att välja önskad backend.

Som standard använder Lemonade Vulkan för GPU-acceleration. Om du har en AMD diskret GPU som stöds kan du byta till ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

För att hantera dina installerade backend-alternativ klickar du på backend-knappen i den vänstra kolumnen.

Alternativt kan du ange backend med följande kommando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Du kan även ställa in din standardbackend med miljövariabeln `LEMONADE_LLAMACPP` med värdena: `vulkan`, `rocm` eller `cpu`.

---

## Gå djupare — Bygg en AI-driven app med Python

Den verkliga styrkan med en lokal AI-server är att vilken applikation som helst kan ansluta till den med bara några rader kod. För att bevisa det ska vi bygga en liten men fungerande **generator för studiekort (flashcards)** där du anger ett ämne, den genererar flashcards, och du kan testa dig själv interaktivt.

### Steg 4: Starta servern

Verifiera att Lemonade-servern körs. Den startar vanligtvis automatiskt i bakgrunden efter installationen. För att verifiera, kör:

```
lemonade status
```

Du bör se ett meddelande som: `Server is running on port 13305`.

Om servern inte körs, starta den genom att öppna Lemonade-appen. Använd standardporten **13305** (du kan bekräfta eller välja denna från ikonen i systemfältet).

### Steg 5: Installera OpenAI Python-klienten

I en terminal, skapa en venv och installera OpenAI Python-klienten med följande kommandon:
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

Låt oss ladda ner en annan modell för att generera kod: `Qwen3.5-35B-A3B-GGUF`. Detta är en stor (~20 GB) och prestandastark modell som passar bäst för system med 32 GB+ RAM. Om du har mindre RAM tillgängligt, prova `Qwen3.5-9B-GGUF` (~6 GB) istället.

Du kan ladda ner den från gränssnittet eller köra följande:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Mata in följande prompt i Lemonade Chat UI för att generera kod för en enkel Flashcard-app.

Vi använder Qwen3.5-35B-A3B-GGUF (en större modell som är bättre på att skriva kod) för att generera vår Python-app, och själva appen kommer att anropa Gemma-4-E2B-it-GGUF (den mindre modellen du redan har laddat ner) vid körning. Koden kan sedan kopieras till en fil du väljer för att köras i Python.

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

> **Tips**: Vi har följt standardmetoder för ingenjörskonst genom noggrann promptutformning och genom att använda ett system med två modeller för att optimera resurser och hastighet.

För din bekvämlighet har vi tillhandahållit en exempel på utdata i [`flashcards.py`](assets/flashcards.py). Du är välkommen att ladda ner den till din katalog. Hur som helst bör du nu ha en Python-fil som kan köras.

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


### Steg 7: Kör den genererade koden

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Så här bör det se ut:**

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

Med omkring 150 rader kod har du byggt ett fullt fungerande studieverktyg som drivs av en lokal LLM. Det finns ingen API-nyckel att hantera, inga användningskostnader, och ingen data lämnar någonsin din maskin.

> **Viktig insikt:** Lägg märke till att raden `client = OpenAI(base_url=...) ` är det *enda* som kopplar den här appen till Lemonade istället för OpenAI:s molntjänst. Resten av koden är identisk med vad du skulle skriva mot vilken OpenAI-kompatibel tjänst som helst. Om du någonsin har använt OpenAI Python-biblioteket vet du redan hur man bygger appar med Lemonade.

### Vad detta visar

Den här lilla appen övar på flera verkliga integrationsmönster:

| Mönster | Var det förekommer |
|---------|-----------------|
| **Systemprompter** | Meddelandet `"system"` säger åt LLM:en att mata ut strukturerad JSON |
| **Strukturerad utdata** | Appen tolkar LLM:ens svar som JSON för att bygga flashcards |
| **Tillståndslösa förfrågningar** | Varje anrop till `generate_flashcards()` är oberoende |
| **Felhantering** | `try/except` hanterar smidigt de fall där LLM:ens utdata inte är giltig JSON |

Samma mönster skalar till vilken applikation som helst, till exempel chattbottar, kodassistenter, innehållsgeneratorer och automatiseringsverktyg.

#### Bonusutmaning

* För en extra utmaning, prova att uppdatera appen så att flashcards läses upp för användaren genom att referera till exemplet som finns [här](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Kör modeller på NPU:n (valfritt)

Om du har en Ryzen AI 300/400/Max 300-serie eller Z2 Extreme har din enhet en inbyggd **Neural Processing Unit (NPU)**, ett dedikerat chip som är särskilt utformat för AI-arbetsbelastningar. Att köra modeller på NPU:n är mer energieffektivt än att använda GPU:n, vilket gör det idealiskt för AI-uppgifter i bakgrunden, längre sessioner och batteridriven användning.

Lemonade stöder tre NPU-exekveringslägen, alla transparenta bakom samma OpenAI API:

| Läge | Hur det fungerar | Recept | Exempelmodeller |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU:n bearbetar prompten, iGPU:n genererar tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Endast NPU** | Hela inferensen körs på NPU:n | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Använder FastFlowLM-motorn på NPU:n, optimerad för AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Krav

- Processor från **AMD Ryzen AI 300/400-serien eller Z2-serien**
- För **FLM**-modeller: FLM-körtiden kan installeras inifrån Lemonade-appen, eller så installerar Lemonade automatiskt FLM-körtiden när en FLM-modell körs. Läs mer om FastFlowLM [här](https://fastflowlm.com/docs/).


### Steg 8: Kör en hybridmodell

Hybridmodeller delar upp arbetet mellan NPU:n och iGPU:n för en bra balans mellan hastighet och effektivitet. I Lemonade-appen väljer du en modell från listan `Ryzen AI LLM`, till exempel `Qwen3-4B-Hybrid`, eller kör den med följande kommando:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade identifierar din NPU automatiskt och installerar **Ryzen AI LLM**-backend.

> **Vad händer bakom kulisserna?** När du skickar ett meddelande bearbetar NPU:n hela din prompt parallellt (detta kallas "prefill"). Sedan tar iGPU:n över för att generera svaret en token i taget (detta kallas "decode"). Detta hybridtillvägagångssätt utnyttjar varje chips styrkor.

### Steg 9: Kör en FLM-modell

FastFlowLM-modeller (FLM) är specifikt optimerade för AMD:s XDNA2 NPU-arkitektur och kan vara mycket snabba för sin storlek. Välj till exempel `qwen3.5-4b-FLM` från listan `FastFlowLM NPU`, eller använd följande kommando:

<!-- @os:windows -->
För att aktivera `FastFlowLM` på Windows:

* Öppna menyn `Backends Manager`.
* Leta reda på backend-kategorin `FastFlowLM NPU`.
* Klicka på Install NPU.
* När installationen är klar kommer cirka 36 standardmodeller att finnas tillgängliga under rullgardinsmenyn FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
När `Lemonade`-appen startas för första gången är backend `FastFlowNPU` inte aktiverad som standard.
Den lokala appen öppnar installationssidan för att guida dig genom installationen.

För att aktivera `FastFlowLM` på Linux:

* Öppna `Lemonade`-appen.
* Besök den [officiella FLM](https://lemonade-server.ai/flm_npu_linux.html)-dokumentationen och följ installationsstegen för FLM genom att välja din Linux-distribution.
* Aktivera backports enligt instruktionerna på installationssidan.
* Ladda ner den senaste `v0.9.x`-utgåvan från [tagg-sidan](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
För AMD Halo Developer Platform, se till att välja Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Installera det nedladdade `.deb`-paketet.
* Rekommenderas: Avsluta `Lemonade App` och öppna den igen så att ändringarna upptäcks.
* Rekommenderas: Öppna `Backends Manager` och klicka på Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Efter en lyckad installation bör du se att `flm:npu` har slutförts i **Download Manager** inuti **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Du kan sedan välja vilken som helst av de tillgängliga FFLM-modellerna och börja använda NPU-backenden.

För en specifik modell, ladda ner önskad modell från [modellsidan](https://fastflowlm.com/docs/models/qwen/) och validera den med Shell-kommandot som anges i dokumentationen.
```
flm run qwen3.5-4b-FLM
```
eller via 
```
lemonade run qwen3.5-4b-FLM
```

FLM-modeller innefattar några av de mest populära arkitekturerna (Gemma 3, Qwen 3, Llama 3 och DeepSeek R1) och varierar från under 1 GB till över 13 GB.
Lemonade identifierar din NPU automatiskt och installerar **FastFlowLM NPU**-backend.

<!-- @os:windows -->
> **Tips:** För bästa NPU-prestanda, aktivera turboläge:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Byta modell

Flashcard-appen från steg 6 fungerar även med NPU-modeller, byt bara modellnamn:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Nästa steg

Du har en lokal AI-server igång på din egen hårdvara, här är vart du kan gå härnäst:

1. **Anslut dina favoritappar**: Lemonade fungerar direkt med [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) och [många fler](https://lemonade-server.ai/marketplace).

2. **Utforska fler modeller**: Utforska hela [modellbiblioteket](https://lemonade-server.ai/docs/server/server_models/) för att hitta modeller optimerade för kodning, resonemang, syn med mera. Använd Lemonade-appen eller `lemonade list` för att se vad som finns tillgängligt.

3. **Lås upp ROCm GPU-acceleration**: Om du har ett AMD GPU som stöds, byt till ROCm-backend: `lemonade config set llamacpp.backend=rocm`. Se [AMD GPU:er som stöds](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Läs hela API-specifikationen**: Lemonade stöder chattkompletteringar, inbäddningar, ljudtranskribering, bildgenerering, text-till-tal och mer. Se [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) för varje slutpunkt.

5. **Bidra**: Lemonade är öppen källkod. Kolla in [bidragsguiden](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) och leta efter [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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