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

## Overzicht

Codeeragenten zijn krachtige hulpmiddelen die ontwikkelaars ondersteunen door samenwerking met AI-agenten die worden aangedreven door Large Language Models (LLM's). Ze kunnen worden geïntegreerd in de ontwikkelomgeving, zoals de terminal of VS Code, waardoor een naadloze integratie in de workflow van een ontwikkelaar mogelijk is.

Deze tutorial laat zien hoe je Cline, VS Code en LM Studio gebruikt om een codeeragent volledig op je lokale machine te draaien.

## Wat Je Leert

* Hoe je VS Code met de Cline-codeeragent gebruikt om te helpen bij softwareontwikkelingstaken.
* Hoe je Cline configureert om te communiceren met LM Studio voor lokale inferentie van codeeragenten.
* Hoe je lokale codeeragenten gebruikt om echte softwareontwikkelingstaken op te lossen.

## De Geheugenconfiguratie Instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleer op Software-updates
> **Opmerking**: Als VS Code niet is geïnstalleerd, kun je het installeren via het Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Softwarevereisten Installeren

<!-- @require:lmstudio,vscode -->

## LM Studio Starten en Configureren

We gebruiken LM Studio om de LLM te serveren die de codeeragent aandrijft.

- Zoek in de zoekbalk naar `LM Studio` en start de applicatie. Je wordt begroet door de volgende pagina.

![LM Studio beginscherm](assets/initial-lm-studio.png)

Vervolgens moeten we de LLM op het systeem laden. We gaan het model `Qwen3-Coder-30B-A3B` gebruiken met een grote contextlengte. (Gebruik het tabblad Model om het te installeren als je dat nog niet hebt gedaan).
- Klik op de zoekbalk bovenaan het LM Studio-venster of druk op `CTRL+L`. Klik op de schakelaar `Manually choose model load parameters` en klik vervolgens op het Qwen3-Coder-30B-A3B-model.
- Verander de contextlengte van `4096` naar `32768` en zorg ervoor dat `GPU Offload` op het maximum staat. Klik daarna op `Load Model`.

![Model selecteren](assets/model-list-zoomed.png)

We gebruiken een grote contextlengte zodat de agent grote codebases kan verwerken en wijzigingen kan onthouden die zijn aangebracht.

![Model configureren](assets/selecting-model-zoomed.png)

Vervolgens moeten we de LM Studio-server inschakelen.
- Klik op het tabblad Developer of druk op `CTRL+2` in LM Studio aan de linkerkant.
- Controleer de statusschakelaar en zorg ervoor dat deze is ingesteld op `Running`.

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

## VS Code Starten en Configureren

We installeren de Cline-extensie in VS Code en verbinden deze met de LM Studio-server die we zojuist hebben aangemaakt.
- Zoek in de zoekbalk naar `VS Code` en start de applicatie.
- Klik op het pictogram `Extensions` in de linkerkolom van VS Code en zoek naar `Cline`. Klik vervolgens op de knop `Install`.

![Cline-extensie installeren](assets/installing-cline-vscode-extension.png)

- Er zou een Cline-pictogram aan de linkerkant aanwezig moeten zijn. Klik daarop om Cline te openen. Er verschijnt een venster met de vraag `How will you use Cline?` Omdat we een lokale LLM via LM Studio gaan gebruiken, selecteer je `Bring my own API Key` en klik je op `Continue`.

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

![Account aanmaken](assets/cline-how-will-you-use-cline-zoomed.png)

Vervolgens moeten we Cline configureren om te communiceren met de LM Studio-server die we hebben ingesteld.
- Stel de API-provider in op `LM Studio` en het model op `Qwen3-Coder-30B-A3B-GGUF`.

>**Tip**: Nieuwere modellen zijn mogelijk beschikbaar. Overweeg om Qwen3.6-modellen te downloaden en naar over te schakelen als gewenst.


![Modelconfiguratie](assets/cline-model-configuration-zoomed.png)

## Je Eerste Project Aanmaken

Laten we onze lokale agent gebruiken om een website te maken! Open VSCode in een map naar keuze waar Cline de bestanden zal aanmaken.
- Ga hiervoor naar `File -> Open Folder` linksboven in VS Code en kies een map zoals `Documents`.

![VS Code lege map](assets/open-cline-test.png)

Nu zijn we klaar om de lokale codeeragent te prompten.
- Klik op de Cline-extensie in de linkerkolom en voer een prompt in om de agent te starten. Laten we als voorbeeld de volgende prompt gebruiken:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

De agent zal vervolgens bestanden beginnen aan te maken op basis van de prompt. Als gebruiker kun je toekijken hoe de code wordt gegenereerd in VS Code zoals hieronder weergegeven. Mogelijk moet je elke keer op `Save` klikken wanneer Cline een bestand wil aanmaken.

![Cline-codegeneratie](assets/cline-code-generation.png)

Na het genereren van de software is de agent klaar en kun je de applicatie uitvoeren. In dit geval heeft de agent drie bestanden geschreven: `index.html`, `script.js` en `styles.css`. Door simpelweg te dubbelklikken op het HTML-bestand kunnen we de gegenereerde website laden en ermee interageren.

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

## Volgende Stappen

Na het genereren van de website kun je blijven samenwerken met Cline om de website te verbeteren. Twee mogelijke verbeteringen zijn:

- **Documentatie**: De agent prompten met `Add a README` is alles wat nodig is voor de agent om een `README.md`-bestand te genereren dat de website documenteert.
- **Animatie**: Prompt het model met `Add an animation that visually represents a large language model running on a laptop.` om een animatie aan de website toe te voegen.

We moedigen de lezer aan om andere applicaties te genereren met deze opzet. Hieronder staan enkele leuke voorbeelden die we hebben geprobeerd:

- **Retro Arcadespellen**: Probeer andere prompts. Het kan ook leuk zijn om de agent retrostijl spellen te laten maken in Python met het `PyGame`-pakket met de volgende prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Gegevensanalyse**: Een gebied waar codeeragenten bijzonder nuttig zijn, is dat van scripting en gegevensanalyse. Dit is een prompt om de mogelijkheid van het lokale model te demonstreren om gegevensanalysesoftware te genereren voor visualisatie van aandelenkoersen:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Bronnen

Hieronder staan enkele aanvullende bronnen om meer te leren over codeeragenten, Cline en het uitvoeren van workloads op

* Meer informatie over de AMD LM Studio-samenwerking en integratie: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD-blog over het uitvoeren van Cline op AMD Ryzen™ AI en Radeon™ grafische kaarten: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline-blog over het lokaal uitvoeren van codeeragenten op AI-pc's: https://cline.bot/blog/local-models-amd