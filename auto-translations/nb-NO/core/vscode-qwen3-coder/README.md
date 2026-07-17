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

## Oversikt

Kodingsagenter er kraftige verktøy som styrker utviklere gjennom samarbeid med AI-agenter støttet av store språkmodeller (LLM-er). De kan bygges inn i utviklingsmiljøet, for eksempel terminalen eller VS Code, og muliggjør sømløs integrering i en utviklers arbeidsflyt.

Denne opplæringen viser hvordan du bruker Cline, VS Code og LM Studio til å kjøre en kodingsagent helt på din lokale maskin.

## Hva du vil lære

* Hvordan du kjører VS Code med Cline-kodingsagenten for å hjelpe med programvareutviklingsoppgaver.
* Hvordan du konfigurerer Cline til å kommunisere med LM Studio for lokal inferens av kodingsagenter.
* Hvordan du bruker lokale kodingsagenter til å løse virkelige programvareutviklingsoppgaver.

## Angi minnekonfigurasjonen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Se etter programvareoppdateringer
> **Merk**: Hvis VS Code ikke er installert, kan du installere det med Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installere programvareforutsetninger

<!-- @require:lmstudio,vscode -->

## Start og konfigurer LM Studio

Vi vil bruke LM Studio til å betjene LLM-en som driver kodingsagenten.

- I søkefeltet søker du etter `LM Studio` og starter programmet. Du vil bli møtt av følgende side.

![LM Studio startskjerm](assets/initial-lm-studio.png)

Deretter må vi laste LLM-en på systemet. Vi skal bruke modellen `Qwen3-Coder-30B-A3B` med en stor kontekstlengde. (Bruk Modell-fanen til å installere den hvis du ikke allerede har gjort det).
- Klikk på søkefeltet øverst i LM Studio-vinduet eller trykk `CTRL+L`. Klikk på bryteren `Manually choose model load parameters` og klikk deretter på Qwen3-Coder-30B-A3B-modellen.
- Endre kontekstlengden fra `4096` til `32768`, og sørg for at `GPU Offload` er på maks. Klikk deretter `Load Model`.

![Velge modell](assets/model-list-zoomed.png)

Vi bruker en stor kontekstlengde slik at agenten kan behandle store kodebaser og huske endringer som er gjort.

![Konfigurere modell](assets/selecting-model-zoomed.png)

Deretter må vi aktivere LM Studio-serveren.
- Klikk på Developer-fanen eller trykk `CTRL+2` i LM Studio til venstre.
- Sjekk statustoggleren og sørg for at den er satt til `Running`.

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

Vi vil installere Cline-utvidelsen i VS Code og koble den til LM Studio-serveren vi nettopp opprettet.
- I søkefeltet søker du etter `VS Code` og starter programmet.
- Klikk på `Extensions`-ikonet i venstre kolonne i VS Code og søk etter `Cline`. Klikk deretter på `Install`-knappen.

![Installere Cline-utvidelsen](assets/installing-cline-vscode-extension.png)

- Et Cline-ikon skal være synlig til venstre. Klikk på det for å åpne Cline. Det vil vises et vindu som spør `How will you use Cline?` Siden vi skal bruke en lokal LLM som kjører via LM Studio, velger du `Bring my own API Key` og klikker `Continue`.

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

![Kontooppretting](assets/cline-how-will-you-use-cline-zoomed.png)

Deretter må vi konfigurere Cline til å kommunisere med LM Studio-serveren vi satte opp.
- Sett API-leverandøren til `LM Studio` og modellen til `Qwen3-Coder-30B-A3B-GGUF`.

>**Tips**: Nyere modeller kan være tilgjengelige. Vurder å laste ned og bytte til Qwen3.6-modeller hvis ønskelig.


![Modellkonfigurasjon](assets/cline-model-configuration-zoomed.png)

## Opprette ditt første prosjekt

La oss bruke vår lokale agent til å lage et nettsted! Åpne VSCode i en valgfri mappe der Cline vil opprette filene.
- For å gjøre dette, gå til `File -> Open Folder` øverst til venstre i VS Code og velg en mappe som `Documents`.

![VS Code tom mappe](assets/open-cline-test.png)

Nå er vi klare til å gi den lokale kodingsagenten en forespørsel.
- Klikk på Cline-utvidelsen i venstre kolonne og skriv inn en forespørsel for å starte agenten. Som et eksempel kan vi bruke følgende forespørsel:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agenten vil deretter begynne å opprette filer i henhold til forespørselen. Som bruker kan du se koden bli generert i VS Code som vist nedenfor. Det kan hende du må klikke `Save` hver gang Cline ønsker å opprette en fil.

![Cline kodegenering](assets/cline-code-generation.png)

Etter at programvaren er generert, er agenten ferdig og du kan kjøre programmet. I dette tilfellet skrev agenten til tre filer: `index.html`, `script.js` og `styles.css`. Ved å dobbeltklikke på HTML-filen kan vi laste inn og samhandle med det genererte nettstedet.

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

## Neste steg

Etter at nettstedet er generert, kan du fortsette å arbeide med Cline for å forbedre nettstedet. To mulige forbedringer er:

- **Dokumentasjon**: Å gi agenten forespørselen `Add a README` er alt som trengs for at agenten skal generere en `README.md`-fil som dokumenterer nettstedet.
- **Animasjon**: Gi modellen forespørselen `Add an animation that visually represents a large language model running on a laptop.` for å legge til en animasjon på nettstedet.

Vi oppfordrer leseren til å prøve å generere andre programmer ved hjelp av dette oppsettet. Nedenfor er noen morsomme eksempler vi har prøvd:

- **Retro arkadespill**: Prøv noen andre forespørsler. Det kan også være morsomt å la agenten lage retrostilte spill i Python ved hjelp av `PyGame`-pakken med følgende forespørsel:

```code
Create a simple pong game using the PyGame python package.
```

- **Dataanalyse**: Ett område der kodingsagenter er spesielt nyttige, er skripting og dataanalyse. Dette er en forespørsel for å vise den lokale modellens evne til å generere dataanalyseprogramvare for visualisering av aksjekurser:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Ressurser

Nedenfor finner du noen tilleggsressurser for å lære mer om kodingsagenter, Cline og kjøring av arbeidsbelastninger på

* Mer informasjon om AMD LM Studio-partnerskapet og integrasjonen: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD-blogg som viser hvordan du kjører Cline på AMD Ryzen™ AI og Radeon™-grafikkort: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline-blogg om kjøring av kodingsagenter lokalt på AI-PC-er: https://cline.bot/blog/local-models-amd