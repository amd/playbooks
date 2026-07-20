<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Denna spelbok använder särskilda taggar som GitHub inte kan rendera. Besök [amd.com/playbooks](https://amd.com/playbooks) för att förhandsgranska detta innehåll korrekt.
<!-- @github-only:end -->

## Översikt

🍋 **Lemonade** är en lokal AI-server med öppen källkod som låter dig köra stora språkmodeller (LLM:er), bildgeneratorer och ljudmodeller direkt på din egen hårdvara. Den exponerar modellerna via branschstandarden **OpenAI API**, så alla appar som fungerar med OpenAI kan omedelbart fungera med Lemonade. I slutet av denna spelbok kommer du att använda Lemonade för att köra modeller lokalt på din dator.

## Vad du kommer att lära dig

I slutet av denna spelbok kommer du att kunna:

* **Installera Lemonade Server** och verifiera att den körs.
* **Ladda ner och chatta med en LLM** med hjälp av ett enda kommando.
* **Utforska webbgränssnittet** och prova olika modaliteter som vision, tal-till-text och bildgenerering.
* **Växla GPU-backends** mellan Vulkan och AMD ROCm™-programvara.
* **Bygga en Python-app** som drivs av en lokal LLM med hjälp av det OpenAI-kompatibla API:et.
<!-- @device:halo_box,halo,stx,krk -->
* **Köra modeller på AMD Neural Processing Unit (NPU)** med hjälp av Hybrid- och FLM-körningslägen på AMD Ryzen™ AI-hårdvara.
<!-- @device:end -->

## Ställa in minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera om det finns programvaruuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Installera nödvändig programvara

Innan du börjar, se till att du har:

- En dator som kör **Windows 11** eller en distribution av **Linux** som stöds (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** rekommenderas för körningsmodellen som används i steg 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** rekommenderas om du vill använda den större kodgenereringsmodellen i steg 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB ledigt diskutrymme**, beroende på vilka modeller du laddar ner. Den största modellen i denna guide är cirka 20 GB.
- **Python 3.10–3.13** (används i avsnittet om Python-appen)
- En internetanslutning (trådbunden eller trådlös)
<!-- @device:halo_box,halo,stx,krk -->
- [Valfritt] En AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300-serien eller Z2 Extreme) med den senaste drivrutinen installerad från [Installationsinstruktioner för Ryzen AI Software](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) om du vill köra en modell på NPU:n.
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

## Grundläggande koncept — Hur lokala AI-servrar fungerar

Innan vi kör en modell är det värt att förstå *varför* saker och ting är uppsatta på detta sätt. Lemonade är en **lokal modellserver**, en process som laddar in AI-modeller i minnet och exponerar dem för applikationer via HTTP, precis som en molnbaserad AI-tjänst skulle göra.

### Varför en server?

| Fördel | Vad det betyder för dig |
|---------|----------------------|
| **Förenklad integration** | Appar kommunicerar med ett enda HTTP-API istället för att hantera hårdvaruspecifika C++- eller Python-bibliotek. |
| **Delade modeller** | En enda inladdad modell kan betjäna flera appar samtidigt, utan dubbletter som äter upp ditt RAM. |
| **Portabilitet mellan moln och lokalt** | Kod skriven för OpenAI:s moln-API fungerar med Lemonade genom att ändra en URL. |
| **Ansvarsseparation** | Modellhantering, strömning och feltolerans hanteras av servern så att utvecklare kan fokusera på sin app. |

### OpenAI API-standarden

Lemonade implementerar **OpenAI API**, samma gränssnitt som används av ChatGPT, Azure OpenAI och dussintals andra tjänster. Konversationsmodellen är enkel:

| Roll | Vem som pratar |
|------|---------------|
| **system** | Instruktioner till modellen (persona, begränsningar, tillgängliga verktyg) |
| **user** | Meddelanden från människan (eller applikationen) till modellen |
| **assistant** | Svar genererade av modellen |

Detta innebär att alla bibliotek eller appar som stöder OpenAI kan kommunicera med Lemonade genom att peka den mot `http://localhost:13305/api/v1` medan Lemonade Server körs.

## Huvudaktivitet — Din första lokala AI-chatt

Låt oss ladda ner en LLM och föra en konversation med den, och köra AI:n helt på din egen dator.

### Steg 1: Ladda ner och kör en modell

Lemonade levereras med ett noggrant sammanställt modellbibliotek. Låt oss börja med **Gemma-4-E2B-it**, en kapabel och kompakt modell som inkluderar stöd för vision. Öppna en terminal och kör:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Detta enda kommando gör tre saker:

1. **Laddar ner** modellen (~3 GB) från Hugging Face, om den inte redan är nedladdad. (Kan ta lite tid)
2. **Startar** Lemonade Server-processen på port 13305.
3. **Öppnar Lemonade App** så att du kan börja chatta med modellen.


<!-- @os:windows -->
På Windows startas Lemonade App automatiskt och du kan börja chatta direkt. Om du installerade `minimal.msi`-paketet ingår inte appen. För att börja chatta, öppna din webbläsare och gå till `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
På Linux öppnar du din webbläsare och navigerar till `http://localhost:13305` för att komma åt webbappen.
<!-- @os:end -->

Prova att skriva en fråga:

```
What are three fun facts about lemons?
```

Modellen kommer att svara direkt i chattfönstret. **Grattis! Du kör nu en stor språkmodell lokalt.**

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

- **Interagera** med den inlästa modellen i ett bekant chattfönster
- **Bläddra bland modeller** på fliken Model Manager
- **Ladda ner nya modeller** med ett enda klick

Prova att växla mellan olika modaliteter genom att använda fliken **Model Manager** i webbgränssnittet, där du kan bläddra bland modeller efter Recipe eller efter Category:

1. **Vision:** Modellen `Gemma-4-E2B-it-GGUF` som du redan har läst in stöder vision. Klistra in en bild i chattrutan och be modellen beskriva den.
2. **Bildgenerering:** I kategorin Image kan du ladda ner en bildmodell, till exempel `SDXL-Turbo`, från Model Manager och sedan använda Lemonade Image Generator för att skriva en prompt och generera en bild lokalt.
3. **Ljud:** I kategorin Audio kan du ladda ner en ljudmodell, till exempel `Whisper-Tiny`, som kan göra tal-till-text. Tillhandahåll en ljudinspelning för att transkribera den lokalt. För text-till-tal kan du prova en av modellerna i kategorin Speech, till exempel `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### Steg 3: Prova en modell med en annan backend

Om du för muspekaren över en modell i Lemonade-appen ser du en kugghjulsikon. Om du klickar på den kan du välja alternativ för modellen, inklusive önskad backend.

Som standard använder Lemonade Vulkan för GPU-acceleration. Om du har en AMD-diskret GPU som stöds kan du växla till ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

För att hantera dina installerade backendar klickar du på backend-knappen i den vänstraste kolumnen.

Alternativt kan du ange backend med hjälp av följande kommando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Du kan även ställa in din standardbackend med hjälp av miljövariabeln `LEMONADE_LLAMACPP` med värdena: `vulkan`, `rocm` eller `cpu`.

---

## Gå djupare — bygg en AI-driven app med Python

Den verkliga styrkan hos en lokal AI-server är att vilken applikation som helst kan ansluta till den med bara några rader kod. För att bevisa det ska vi bygga en liten men fungerande **generator för studiekort (flashcards)** där du anger ett ämne, den genererar studiekort, och du kan förhöra dig själv interaktivt.

### Steg 4: Starta servern

Kontrollera att Lemonade-servern körs. Den startar vanligtvis automatiskt i bakgrunden efter installationen. Kör följande för att verifiera:

```
lemonade status
```

Du bör se ett meddelande liknande: `Server is running on port 13305`.

Om servern inte körs startar du den genom att öppna Lemonade-appen. Använd standardporten **13305** (du kan bekräfta eller välja den från ikonen i systemfältet).

### Steg 5: Installera OpenAI Python Client

Öppna en terminal, skapa en venv och installera OpenAI Python Client med hjälp av följande kommandon:
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

Låt oss ladda ner en annan modell för att generera kod: `Qwen3.5-35B-A3B-GGUF`. Detta är en stor (~20 GB) och prestandastark modell som passar bäst för system med 32 GB+ RAM. Om du har mindre RAM tillgängligt kan du istället prova `Qwen3.5-9B-GGUF` (~6 GB).

Du kan ladda ner den från gränssnittet eller köra följande:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Mata in följande prompt i Lemonade Chat UI för att generera kod till en enkel Flashcard-app.

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

> **Tips**: Vi har följt standardpraxis inom teknik genom noggrann prompt-utformning och genom att använda ett tvåmodellssystem för att optimera resurser och hastighet.

För din bekvämlighet har vi tillhandahållit ett exempel på utdata i [`flashcards.py`](assets/flashcards.py). Du kan gärna ladda ner den till din katalog. Oavsett vilket bör du nu ha en Python-fil som kan köras.

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

Med cirka 150 rader kod har du byggt ett fullt fungerande studieverktyg drivet av en lokal LLM. Det finns ingen API-nyckel att hantera, inga användningskostnader, och ingen data lämnar någonsin din dator.

> **Viktig insikt:** Lägg märke till att raden `client = OpenAI(base_url=...) ` är det *enda* som kopplar den här appen till Lemonade istället för OpenAIs moln. Resten av koden är identisk med vad du skulle skriva mot vilken OpenAI-kompatibel tjänst som helst. Om du någonsin har använt OpenAI Python-biblioteket vet du redan hur man bygger appar med Lemonade.

### Vad detta visar

Den här lilla appen demonstrerar flera verkliga integrationsmönster:

| Mönster | Var det förekommer |
|---------|-----------------|
| **Systemprompter** | Meddelandet `"system"` instruerar LLM:en att generera strukturerad JSON |
| **Strukturerad utdata** | Appen tolkar LLM:ens svar som JSON för att bygga studiekort |
| **Tillståndslösa förfrågningar** | Varje anrop till `generate_flashcards()` är oberoende |
| **Felhantering** | `try/except` hanterar smidigt fall där LLM:ens utdata inte är giltig JSON |

Dessa mönster kan användas i alla typer av applikationer, till exempel chattbottar, kodassistenter, innehållsgeneratorer och automatiseringsverktyg.

#### Bonusutmaning

* Som en extra utmaning kan du prova att uppdatera appen så att studiekorten läses upp för användaren genom att referera till exemplet som finns [här](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Köra modeller på NPU:n (valfritt)

Om du har en Ryzen AI 300/400/Max 300-serie eller Z2 Extreme har din enhet en inbyggd **Neural Processing Unit (NPU)**, ett dedikerat chip utformat specifikt för AI-arbetsbelastningar. Att köra modeller på NPU:n är mer energieffektivt än att använda GPU:n, vilket gör den idealisk för AI-uppgifter i bakgrunden, längre sessioner och batteridriven användning.

Lemonade stöder tre NPU-exekveringslägen, alla transparenta bakom samma OpenAI API:

| Läge | Hur det fungerar | Recept | Exempelmodeller |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU:n bearbetar prompten, iGPU:n genererar tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Endast NPU** | Hela inferensen körs på NPU:n | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Använder FastFlowLM-motorn på NPU:n, optimerad för AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Krav

- **AMD Ryzen AI 300/400-serien eller Z2-serien**-processor
- För **FLM**-modeller: FLM-körtidsmiljön kan installeras från Lemonade-appen, eller så kommer Lemonade automatiskt att installera FLM-körtidsmiljön när en FLM-modell körs. Läs mer om FastFlowLM [här](https://fastflowlm.com/docs/).


### Steg 8: Kör en hybridmodell

Hybridmodeller delar upp arbetet mellan NPU:n och iGPU:n för en bra balans mellan hastighet och effektivitet. I Lemonade-appen väljer du en modell från listan `Ryzen AI LLM`, till exempel `Qwen3-4B-Hybrid`, eller kör den med följande kommando:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade upptäcker din NPU automatiskt och installerar backend-lösningen **Ryzen AI LLM**.

> **Vad händer under huven?** När du skickar ett meddelande bearbetar NPU:n hela din prompt parallellt (detta kallas "prefill"). Sedan tar iGPU:n över för att generera svaret en token i taget (detta kallas "decode"). Detta hybridtillvägagångssätt drar nytta av varje chips styrkor.

### Steg 9: Kör en FLM-modell

FastFlowLM (FLM)-modeller är särskilt optimerade för AMD:s XDNA2 NPU-arkitektur och kan vara mycket snabba i förhållande till sin storlek. Välj till exempel `qwen3.5-4b-FLM` från listan `FastFlowLM NPU`, eller använd följande kommando:

<!-- @os:windows -->
Så här aktiverar du `FastFlowLM` på Windows:

* Öppna menyn `Backends Manager`.
* Leta upp backend-kategorin `FastFlowLM NPU`.
* Klicka på Install NPU.
* När installationen är klar kommer cirka 36 standardmodeller att finnas tillgängliga under FFLM-rullgardinsmenyn.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
När appen `Lemonade` startas för första gången är backend-lösningen `FastFlowNPU` inte aktiverad som standard.
Den lokala appen öppnar installationssidan för att guida dig genom installationen.

Så här aktiverar du `FastFlowLM` på Linux:

* Öppna appen `Lemonade`.
* Besök den [officiella FLM](https://lemonade-server.ai/flm_npu_linux.html)-dokumentationen och följ installationsstegen för FLM genom att välja din Linux-distribution.
* Aktivera backports enligt anvisningarna på installationssidan.
* Ladda ner den senaste `v0.9.x`-utgåvan från [taggsidan](https://github.com/FastFlowLM/FastFlowLM/tags).'
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
Du kan sedan välja valfri tillgänglig FFLM-modell och börja använda NPU-backend-lösningen.

För en specifik modell laddar du ner önskad modell från [modellsidan](https://fastflowlm.com/docs/models/qwen/) och validerar den med hjälp av det Shell-kommando som anges i dokumentationen.
```
flm run qwen3.5-4b-FLM
```
eller via 
```
lemonade run qwen3.5-4b-FLM
```

FLM-modeller inkluderar några av de mest populära arkitekturerna (Gemma 3, Qwen 3, Llama 3 och DeepSeek R1) och sträcker sig från under 1 GB till över 13 GB.
Lemonade upptäcker din NPU automatiskt och installerar backend-lösningen **FastFlowLM NPU**.

<!-- @os:windows -->
> **Tips:** För bästa NPU-prestanda, aktivera turboläge:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Byta modeller

Flashcard-appen från steg 6 fungerar även med NPU-modeller, ändra bara modellnamnet:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Nästa steg

Du har nu en lokal AI-server som körs på din egen hårdvara, här är vart du kan gå härnäst:

1. **Anslut dina favoritappar**: Lemonade fungerar direkt med [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/), och [många fler](https://lemonade-server.ai/marketplace).

2. **Utforska fler modeller**: Utforska hela [modellbiblioteket](https://lemonade-server.ai/docs/server/server_models/) för att hitta modeller optimerade för kodning, resonemang, vision med mera. Använd Lemonade-appen eller `lemonade list` för att se vad som finns tillgängligt.

3. **Lås upp ROCm GPU-acceleration**: Om du har en AMD GPU som stöds, byt till ROCm-backend-lösningen: `lemonade config set llamacpp.backend=rocm`. Se [AMD GPU:er som stöds](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Läs hela API-specifikationen**: Lemonade stöder chattkompletteringar, embeddings, ljudtranskribering, bildgenerering, text-till-tal med mera. Se [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) för varje slutpunkt.

5. **Bidra**: Lemonade är öppen källkod. Kolla in [bidragsguiden](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) och leta efter [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).