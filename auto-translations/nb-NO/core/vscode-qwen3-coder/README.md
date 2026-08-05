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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Denne oppskriften krever minst **32GB** systemminne.
<!-- @device:end -->

## Oversikt

Kodeagenter er kraftige verktøy som gir utviklere mulighet til å samarbeide med AI-agenter drevet av store språkmodeller (LLM-er). De kan bygges inn i utviklingsmiljøet, som terminalen eller VS Code, slik at de sømløst kan integreres i en utviklers arbeidsflyt.

Denne veiledningen viser hvordan du bruker Cline, VS Code og LM Studio til å kjøre en kodeagent helt lokalt på maskinen din.

## Hva du vil lære

* Hvordan kjøre VS Code med Cline-kodeagenten for å bistå med programvareutviklingsoppgaver.
* Hvordan konfigurere Cline til å kommunisere med LM Studio for lokal inferens av kodeagenter.
* Hvordan bruke lokale kodeagenter til å løse virkelige programvareutviklingsoppgaver. 

## Konfigurere minneinnstillinger

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Se etter programvareoppdateringer
> **Merk**: Hvis VS Code ikke er installert, kan du installere det med Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installere forutsetninger for programvare

<!-- @require:lmstudio,vscode -->

## Start og konfigurer LM Studio

Vi skal bruke LM Studio til å servere LLM-en som driver kodeagenten.

- I søkefeltet søker du etter `LM Studio` og starter applikasjonen. Du vil da bli møtt av følgende side.

![LM Studio Initial Screen](assets/initial-lm-studio.png)

Deretter må vi laste LLM-en på systemet. Vi kommer til å bruke modellen `Qwen3-Coder-30B-A3B` med en stor kontekstlengde. (Bruk Model-fanen til å installere den hvis du ikke allerede har gjort det).
- Klikk på søkefeltet øverst i LM Studio-vinduet, eller trykk `CTRL+L`. Klikk på bryteren `Manually choose model load parameters`, og klikk deretter på modellen Qwen3-Coder-30B-A3B.
- Endre kontekstlengden fra `4096` til `32768`, og sørg for at `GPU Offload` er satt til maks. Klikk deretter på `Load Model`

![Selecting Model](assets/model-list-zoomed.png)

Vi bruker en stor kontekstlengde slik at agenten kan behandle store kodebaser og huske endringer som er gjort.

![Configuring Model](assets/selecting-model-zoomed.png)

Deretter må vi aktivere LM Studio-serveren. 
- Klikk på Developer-fanen, eller trykk `CTRL+2` i LM Studio til venstre.
- Kryss av statusbryteren og sørg for at den er satt til `Running`.

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

![Server Status](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
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
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Start og konfigurer VS Code

Vi skal installere Cline-utvidelsen i VS Code og koble den til LM Studio-serveren vi nettopp opprettet.
- I søkefeltet søker du etter `VS Code` og starter applikasjonen.
- Klikk på `Extensions`-ikonet i venstre kolonne i VS Code og søk etter `Cline`. Klikk deretter på `Install`-knappen. 

![Installing Cline Extension](assets/installing-cline-vscode-extension.png)

- Et Cline-ikon skal nå vises til venstre. Klikk på det for å åpne Cline. Det vil dukke opp et vindu som spør `How will you use Cline?` Siden vi skal bruke en lokal LLM som kjører via LM Studio, velger du `Bring my own API Key` og trykker på `Continue`. 

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

![Account Creation](assets/cline-how-will-you-use-cline-zoomed.png)

Deretter må vi konfigurere Cline til å kommunisere med LM Studio-serveren vi har satt opp. 
- Sett API Provider til `LM Studio` og modellen til `Qwen3-Coder-30B-A3B-GGUF`. 

>**Tips**: Nyere modeller kan være tilgjengelige. Vurder å laste ned og bytte til Qwen3.6-modeller hvis ønskelig.


![Model Configuration](assets/cline-model-configuration-zoomed.png)

## Opprette ditt første prosjekt

La oss bruke vår lokale agent til å lage et nettsted! Åpne VS Code til en mappe du velger, hvor Cline vil opprette filene.
- For å gjøre dette, gå til `File -> Open Folder` øverst til venstre i VS Code og velg en mappe som `Documents`.

![VS Code Empty Folder](assets/open-cline-test.png)

Nå er vi klare til å be den lokale kodeagenten om å gjøre noe. 
- Klikk på Cline-utvidelsen i venstre kolonne og skriv inn en prompt for å sette i gang agenten. La oss for eksempel bruke følgende prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agenten vil deretter begynne å opprette filer i henhold til prompten. Som bruker kan du se koden bli generert i VS Code, som vist nedenfor. Du må kanskje klikke på `Save` hver gang Cline ønsker å opprette en fil. 

![Cline Code Generation](assets/cline-code-generation.png)

Etter at programvaren er generert, er agenten ferdig, og du kan kjøre applikasjonen. I dette tilfellet skrev agenten til tre filer: `index.html`, `script.js` og `styles.css`. Ved å dobbeltklikke på HTML-filen kan vi laste inn og samhandle med det genererte nettstedet.

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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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
## Neste steg

Etter at nettstedet er generert, kan du fortsette å jobbe med Cline for å forbedre nettstedet. To mulige forbedringer er:

- **Dokumentasjon**: Å be agenten med `Add a README` er alt som trengs for at agenten skal generere en `README.md`-fil som dokumenterer nettstedet.
- **Animasjon**: Be modellen med `Add an animation that visually represents a large language model running on a laptop.` for å generere en animasjon til nettstedet.

Vi oppfordrer leseren til å prøve å generere andre applikasjoner ved hjelp av dette oppsettet. Under følger noen morsomme eksempler vi har prøvd:

- **Retro arkadespill**: Prøv noen andre prompter. Det kan også være gøy for agenten å lage spill i retrostil i Python ved hjelp av `PyGame`-pakken med følgende prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Dataanalyse**: Et område hvor kodeagenter er spesielt nyttige, er skripting og dataanalyse. Dette er en prompt for å vise frem den lokale modellens evne til å generere programvare for dataanalyse for visualisering av aksjekurser:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Ressurser

Under følger noen tilleggsressurser for å lære mer om kodeagenter, Cline, og kjøring av arbeidsbelastninger på 

* Mer informasjon om AMDs partnerskap og integrasjon med LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD-blogginnlegg som viser hvordan man kjører Cline på AMD Ryzen™ AI- og Radeon™-grafikkort: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline-blogginnlegg om å kjøre kodeagenter lokalt på AI-PC-er: https://cline.bot/blog/local-models-amd