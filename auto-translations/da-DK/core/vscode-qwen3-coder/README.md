<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

## Oversigt

Kodningsagenter er kraftfulde værktøjer, der styrker udviklere gennem samarbejde med AI-agenter understøttet af Large Language Models (LLM'er). De kan integreres i udviklingsmiljøet, f.eks. i terminalen eller VS Code, hvilket muliggør problemfri integration i en udviklers arbejdsgang.

Denne vejledning demonstrerer, hvordan man bruger Cline, VS Code og LM Studio til at køre en kodningsagent udelukkende på din lokale maskine.

## Hvad du vil lære

* Hvordan man kører VS Code med Cline-kodningsagenten til at hjælpe med softwareudviklingsopgaver.
* Hvordan man konfigurerer Cline til at kommunikere med LM Studio til lokal inferens af kodningsagenter.
* Hvordan man bruger lokale kodningsagenter til at løse virkelige softwareudviklingsopgaver.

## Indstilling af hukommelseskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontroller for softwareopdateringer
> **Bemærk**: Hvis VS Code ikke er installeret, kan du installere det med Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger

<!-- @require:lmstudio,vscode -->

## Start og konfigurer LM Studio

Vi vil bruge LM Studio til at betjene den LLM, der driver kodningsagenten.

- I søgefeltet søger du efter `LM Studio` og starter applikationen. Du vil blive mødt af følgende side.

![LM Studio startskærm](assets/initial-lm-studio.png)

Dernæst skal vi indlæse LLM'en på systemet. Vi vil bruge modellen `Qwen3-Coder-30B-A3B` med en stor kontekstlængde. (Brug fanen Model til at installere den, hvis du ikke allerede har gjort det).
- Klik på søgefeltet øverst i LM Studio-vinduet, eller tryk på `CTRL+L`. Klik på kontakten `Manually choose model load parameters`, og klik derefter på Qwen3-Coder-30B-A3B-modellen.
- Skift kontekstlængden fra `4096` til `32768`, og sørg for, at `GPU Offload` er på maksimum. Klik derefter på `Load Model`.

![Valg af model](assets/model-list-zoomed.png)

Vi bruger en stor kontekstlængde, så agenten kan behandle store kodebaser og huske ændringer, der er foretaget.

![Konfiguration af model](assets/selecting-model-zoomed.png)

Dernæst skal vi aktivere LM Studio-serveren.
- Klik på fanen Developer, eller tryk på `CTRL+2` i LM Studio til venstre.
- Kontroller statuskontakten, og sørg for, at den er indstillet til `Running`.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![Serverstatus](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Start og konfigurer VS Code

Vi vil installere Cline-udvidelsen i VS Code og forbinde den til den LM Studio-server, vi netop har oprettet.
- I søgefeltet søger du efter `VS Code` og starter applikationen.
- Klik på ikonet `Extensions` i venstre kolonne i VS Code, og søg efter `Cline`. Klik derefter på knappen `Install`.

![Installation af Cline-udvidelse](assets/installing-cline-vscode-extension.png)

- Et Cline-ikon bør være synligt til venstre. Klik på det for at åbne Cline. Der vises et vindue med spørgsmålet `How will you use Cline?` Da vi vil bruge en lokal LLM, der kører via LM Studio, skal du vælge `Bring my own API Key` og klikke på `Continue`.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Kontooprettelse](assets/cline-how-will-you-use-cline-zoomed.png)

Dernæst skal vi konfigurere Cline til at kommunikere med den LM Studio-server, vi har opsat.
- Indstil API-udbyderen til `LM Studio` og modellen til `Qwen3-Coder-30B-A3B-GGUF`.

>**Tip**: Nyere modeller kan være tilgængelige. Overvej at downloade og skifte til Qwen3.6-modeller, hvis det ønskes.


![Modelkonfiguration](assets/cline-model-configuration-zoomed.png)

## Oprettelse af dit første projekt

Lad os bruge vores lokale agent til at oprette et websted! Åbn VSCode i en mappe efter eget valg, hvor Cline vil oprette filerne.
- For at gøre dette skal du gå til `File -> Open Folder` øverst til venstre i VS Code og vælge en mappe som f.eks. `Documents`.

![VS Code tom mappe](assets/open-cline-test.png)

Nu er vi klar til at give den lokale kodningsagent en prompt.
- Klik på Cline-udvidelsen i venstre kolonne, og indtast en prompt for at starte agenten. Som eksempel kan vi bruge følgende prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agenten vil derefter begynde at oprette filer i henhold til prompten. Som bruger kan du se koden blive genereret i VS Code som vist nedenfor. Du skal muligvis klikke på `Save` hver gang Cline ønsker at oprette en fil.

![Cline-kodegenerering](assets/cline-code-generation.png)

Efter generering af softwaren er agenten færdig, og du kan køre applikationen. I dette tilfælde skrev agenten til tre filer: `index.html`, `script.js` og `styles.css`. Ved blot at dobbeltklikke på HTML-filen kan vi indlæse og interagere med det genererede websted.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

## Næste skridt

Efter generering af webstedet kan du fortsætte med at arbejde med Cline for at forbedre webstedet. To mulige forbedringer er:

- **Dokumentation**: At give agenten prompten `Add a README` er alt, hvad der er nødvendigt for, at agenten genererer en `README.md`-fil, der dokumenterer webstedet.
- **Animation**: Giv modellen prompten `Add an animation that visually represents a large language model running on a laptop.` for at tilføje en animation til webstedet.

Vi opfordrer læseren til at forsøge at generere andre applikationer ved hjælp af denne opsætning. Nedenfor er nogle sjove eksempler, vi har prøvet:

- **Retro-arkadespil**: Prøv nogle andre prompts. Det kan også være sjovt at lade agenten oprette retro-stilede spil i Python ved hjælp af `PyGame`-pakken med følgende prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Dataanalyse**: Et område, hvor kodningsagenter er særligt nyttige, er scripting og dataanalyse. Dette er en prompt til at vise den lokale models evne til at generere dataanalysesoftware til visualisering af aktiekurser:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Ressourcer

Nedenfor er nogle yderligere ressourcer til at lære mere om kodningsagenter, Cline og kørsel af arbejdsbelastninger på

* Mere information om AMD LM Studio-partnerskabet og integrationen: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD-blog, der gennemgår kørsel af Cline på AMD Ryzen™ AI og Radeon™ grafikkort: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline-blog om kørsel af kodningsagenter lokalt på AI-pc'er: https://cline.bot/blog/local-models-amd