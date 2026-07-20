<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> Deze playbook maakt gebruik van speciale tags die GitHub niet kan weergeven. Ga naar [amd.com/playbooks](https://amd.com/playbooks) om deze inhoud correct te bekijken.

<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Voor deze playbook is minimaal **32GB** aan systeemgeheugen vereist.
<!-- @device:end -->

## Overzicht

Codeer-agents zijn krachtige tools waarmee ontwikkelaars kunnen samenwerken met AI-agents die worden aangedreven door Large Language Models (LLMs). Ze kunnen worden geïntegreerd in de ontwikkelomgeving, zoals de terminal of VS Code, waardoor ze naadloos kunnen worden opgenomen in de workflow van een ontwikkelaar.

Deze tutorial laat zien hoe je Cline, VS Code en LM Studio gebruikt om een codeer-agent volledig lokaal op je eigen machine uit te voeren.

## Wat je gaat leren

* Hoe je VS Code samen met de Cline-codeer-agent uitvoert om softwareontwikkelingstaken te ondersteunen.
* Hoe je Cline configureert om te communiceren met LM Studio voor lokale inferentie van codeer-agents.
* Hoe je lokale codeer-agents gebruikt om praktische softwareontwikkelingsproblemen op te lossen.

## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates
> **Opmerking**: Als VS Code niet is geïnstalleerd, kun je het installeren via het Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Software-vereisten installeren

<!-- @require:lmstudio,vscode -->

## LM Studio starten en configureren

We gebruiken LM Studio om het LLM te hosten dat de codeer-agent aandrijft.

- Zoek in de zoekbalk naar `LM Studio` en start de applicatie. Je krijgt de volgende pagina te zien.

![LM Studio-startscherm](assets/initial-lm-studio.png)

Vervolgens moeten we het LLM op het systeem laden. We gaan het model `Qwen3-Coder-30B-A3B` gebruiken met een grote contextlengte. (Gebruik het tabblad Model om het te installeren als je dat nog niet hebt gedaan).
- Klik op de zoekbalk bovenaan het LM Studio-venster of druk op `CTRL+L`. Klik op de schakelaar `Manually choose model load parameters` en klik vervolgens op het Qwen3-Coder-30B-A3B-model.
- Wijzig de contextlengte van `4096` naar `32768` en zorg ervoor dat `GPU Offload` op het maximum staat. Klik vervolgens op `Load Model`

![Model selecteren](assets/model-list-zoomed.png)

We gebruiken een grote contextlengte zodat de agent grote codebases kan verwerken en de aangebrachte wijzigingen kan onthouden.

![Model configureren](assets/selecting-model-zoomed.png)

Vervolgens moeten we de LM Studio Server inschakelen.
- Klik links in LM Studio op het tabblad Developer of druk op `CTRL+2`.
- Controleer de statusschakelaar en zorg ervoor dat deze op `Running` staat.

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

## VS Code starten en configureren

We installeren de Cline-extensie in VS Code en verbinden deze met de LM Studio-server die we zojuist hebben gemaakt.
- Zoek in de zoekbalk naar `VS Code` en start de applicatie.
- Klik op het `Extensions`-icoon in de linkerkolom van VS Code en zoek naar `Cline`. Klik vervolgens op de knop `Install`.

![Cline-extensie installeren](assets/installing-cline-vscode-extension.png)

- Links zou nu een Cline-icoon zichtbaar moeten zijn. Klik hierop om Cline te openen. Er verschijnt een venster met de vraag `How will you use Cline?` Omdat we een lokaal LLM gaan gebruiken dat via LM Studio draait, selecteer je `Bring my own API Key` en klik je op `Continue`.

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
- Stel de API Provider in op `LM Studio` en het model op `Qwen3-Coder-30B-A3B-GGUF`.

>**Tip**: Er zijn mogelijk nieuwere modellen beschikbaar. Overweeg om Qwen3.6-modellen te downloaden en hiernaar over te schakelen indien gewenst.


![Modelconfiguratie](assets/cline-model-configuration-zoomed.png)

## Je eerste project maken

Laten we onze lokale agent gebruiken om een website te maken! Open VS Code in een map naar keuze waarin Cline de bestanden zal aanmaken.
- Ga hiervoor naar `File -> Open Folder` linksboven in VS Code en kies een map zoals `Documents`.

![Lege map in VS Code](assets/open-cline-test.png)

Nu zijn we klaar om de lokale codeer-agent aan te sturen.
- Klik op de Cline-extensie in de linkerkolom en voer een prompt in om de agent te starten. Gebruik bijvoorbeeld de volgende prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

De agent begint vervolgens bestanden aan te maken op basis van de prompt. Als gebruiker kun je in VS Code live zien hoe de code wordt gegenereerd, zoals hieronder wordt getoond. Mogelijk moet je telkens op `Save` klikken wanneer Cline een bestand wil aanmaken.

![Codegeneratie met Cline](assets/cline-code-generation.png)

Nadat de software is gegenereerd, is de agent klaar en kun je de applicatie uitvoeren. In dit geval heeft de agent naar drie bestanden geschreven: `index.html`, `script.js` en `styles.css`. Door simpelweg te dubbelklikken op het HTML-bestand kunnen we de gegenereerde website laden en ermee interacteren.

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
## Volgende stappen

Nadat u de website hebt gegenereerd, kunt u met Cline blijven samenwerken om de website te verbeteren. Twee mogelijke verbeteringen zijn:

- **Documentatie**: Door de agent te prompten met `Add a README` genereert de agent een `README.md`-bestand dat de website documenteert.
- **Animatie**: Prompt het model met `Add an animation that visually represents a large language model running on a laptop.` om een animatie aan de website toe te voegen.

We moedigen de lezer aan om te proberen andere applicaties te genereren met deze opstelling. Hieronder staan enkele leuke voorbeelden die we hebben uitgeprobeerd:

- **Retro Arcade Games**: Probeer enkele andere prompts. Het kan ook leuk zijn om de agent retro-stijl games in Python te laten maken met het `PyGame`-pakket met de volgende prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Data-analyse**: Een gebied waarop codeeragenten bijzonder nuttig zijn, is dat van scripting en data-analyse. Dit is een prompt om de mogelijkheid van het lokale model om data-analysesoftware voor het visualiseren van aandelenkoersen te genereren te demonstreren:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Bronnen

Hieronder vindt u enkele aanvullende bronnen om meer te leren over Coding Agents, Cline en het uitvoeren van workloads op 

* Meer informatie over het AMD LM Studio-partnerschap en de integratie: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD-blog over het uitvoeren van Cline op AMD Ryzen™ AI- en Radeon™ Graphics-kaarten: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline-blog over het lokaal uitvoeren van codeeragenten op AI-pc's: https://cline.bot/blog/local-models-amd