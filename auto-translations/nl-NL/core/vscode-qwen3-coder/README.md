<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Deze playbook vereist minimaal **32GB** aan systeemgeheugen.
<!-- @device:end -->

## Overzicht

Coding agents zijn krachtige tools die ontwikkelaars ondersteunen door samenwerking met AI-agents die worden aangedreven door Large Language Models (LLM's). Ze kunnen worden geïntegreerd in de ontwikkelomgeving, zoals de terminal of VS Code, waardoor ze naadloos kunnen worden opgenomen in de workflow van een ontwikkelaar.

Deze tutorial laat zien hoe je Cline, VS Code en LM Studio kunt gebruiken om een coding agent volledig op je lokale machine te laten draaien.

## Wat je leert

* Hoe je VS Code met de Cline coding agent uitvoert om te helpen bij software engineering-taken.
* Hoe je Cline configureert om te communiceren met LM Studio voor lokale inferentie van coding agents.
* Hoe je lokale coding agents gebruikt om praktijkgerichte software engineering-problemen op te lossen.

<!-- @device:halo_box,halo,stx,krk -->
## De geheugenconfiguratie instellen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Controleren op software-updates
> **Opmerking**: Als VS Code niet is geïnstalleerd, kun je het installeren via Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Software-vereisten installeren

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lmstudio,vscode -->
<!-- @prereq:lmstudio-models-qwen3-coder-30b,lmstudio,vscode -->

## LM Studio starten en configureren

We gebruiken LM Studio om de LLM te hosten die de coding agent aandrijft.

- Zoek in de zoekbalk naar `LM Studio` en start de applicatie. Je wordt begroet met de volgende pagina.

![LM Studio Initial Screen](assets/initial-lm-studio.png)

Vervolgens moeten we de LLM op het systeem laden. We gaan het model `Qwen3-Coder-30B-A3B` gebruiken met een grote contextlengte. (Gebruik het tabblad Model om het te installeren als je dit nog niet hebt gedaan).
- Klik op de zoekbalk bovenaan het LM Studio-venster of druk op `CTRL+L`. Klik op de schakelaar `Manually choose model load parameters` en klik vervolgens op het model Qwen3-Coder-30B-A3B.
- Wijzig de contextlengte van `4096` naar `32768`, en zorg ervoor dat `GPU Offload` op maximum staat. Klik vervolgens op `Load Model`

![Selecting Model](assets/model-list-zoomed.png)

We gebruiken een grote contextlengte zodat de agent grote codebases kan verwerken en wijzigingen die zijn aangebracht kan onthouden.

![Configuring Model](assets/selecting-model-zoomed.png)

Vervolgens moeten we de LM Studio Server inschakelen.
- Klik op het tabblad Developer of druk op `CTRL+2` links in LM Studio.
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

## VS Code starten en configureren

We installeren de Cline-extensie in VS Code en verbinden deze met de LM Studio-server die we zojuist hebben opgezet.
- Zoek in de zoekbalk naar `VS Code` en start de applicatie.
- Klik op het `Extensions`-icoon in de linkerkolom van VS Code en zoek naar `Cline`. Klik vervolgens op de knop `Install`.

![Installing Cline Extension](assets/installing-cline-vscode-extension.png)

- Er zou nu een Cline-icoon links aanwezig moeten zijn. Klik hierop om Cline te openen. Er verschijnt een venster met de vraag `How will you use Cline?` Omdat we een lokale LLM gaan gebruiken die via LM Studio draait, selecteer je `Bring my own API Key` en klik je op `Continue`.

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

Vervolgens moeten we Cline configureren om te communiceren met de LM Studio-server die we hebben opgezet.
- Stel de API Provider in op `LM Studio` en het model op `Qwen3-Coder-30B-A3B-GGUF`.

>**Tip**: Er zijn mogelijk nieuwere modellen beschikbaar. Overweeg om Qwen3.6-modellen te downloaden en hiernaar over te schakelen indien gewenst.


![Model Configuration](assets/cline-model-configuration-zoomed.png)

## Je eerste project maken

Laten we onze lokale agent gebruiken om een website te maken! Open VS Code in een map naar keuze waar Cline de bestanden zal aanmaken.
- Ga hiervoor naar `File -> Open Folder` linksboven in VS Code en kies een map zoals `Documents`.

![VS Code Empty Folder](assets/open-cline-test.png)

Nu zijn we klaar om de lokale coding agent te prompten.
- Klik op de Cline-extensie in de linkerkolom en voer een prompt in om de agent te starten. Laten we als voorbeeld de volgende prompt gebruiken:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

De agent begint vervolgens met het maken van bestanden volgens de prompt. Als gebruiker kun je in VS Code bekijken hoe de code wordt gegenereerd, zoals hieronder weergegeven. Mogelijk moet je `Save` klikken telkens wanneer Cline een bestand wil aanmaken.

![Cline Code Generation](assets/cline-code-generation.png)

Na het genereren van de software is de agent klaar en kun je de applicatie uitvoeren. In dit geval heeft de agent naar drie bestanden geschreven: `index.html`, `script.js` en `styles.css`. Door simpelweg dubbel te klikken op het HTML-bestand kunnen we de gegenereerde website laden en ermee interacteren.

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

## Volgende stappen

Na het genereren van de website kun je met Cline blijven samenwerken om de website te verbeteren. Twee mogelijke verbeteringen zijn:

- **Documentatie**: Door de agent te prompten met `Add a README` genereert de agent een `README.md`-bestand dat de website documenteert.
- **Animatie**: Prompt het model met `Add an animation that visually represents a large language model running on a laptop.` om een animatie aan de website toe te voegen.

We moedigen de lezer aan om te proberen andere applicaties te genereren met deze opzet. Hieronder volgen enkele leuke voorbeelden die we hebben uitgeprobeerd:

- **Retro Arcade Games**: Probeer enkele andere prompts. Het kan ook leuk zijn als de agent retro-stijl games in Python maakt met gebruik van het `PyGame`-pakket met de volgende prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Data-analyse**: Een gebied waarop coding agents bijzonder nuttig zijn, is scripting en data-analyse. Dit is een prompt om de mogelijkheden van het lokale model te demonstreren voor het genereren van data-analysesoftware voor het visualiseren van aandelenkoersen:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Bronnen

Hieronder vindt u enkele aanvullende bronnen om meer te weten te komen over Coding Agents, Cline en het uitvoeren van workloads op 

* Meer informatie over het AMD LM Studio-partnerschap en de integratie: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD-blog over het uitvoeren van Cline op AMD Ryzen™ AI- en Radeon™ Graphics-kaarten: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline-blog over het lokaal uitvoeren van coding agents op AI PC's: https://cline.bot/blog/local-models-amd