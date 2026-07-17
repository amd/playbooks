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

## Översikt

Kodningsagenter är kraftfulla verktyg som stärker utvecklare genom samarbete med AI-agenter som drivs av stora språkmodeller (LLM:er). De kan integreras i utvecklingsmiljön, till exempel i terminalen eller VS Code, vilket möjliggör sömlös integration i en utvecklares arbetsflöde.

Den här handledningen visar hur du använder Cline, VS Code och LM Studio för att köra en kodningsagent helt på din lokala dator.

## Vad du kommer att lära dig

* Hur du kör VS Code med Cline-kodningsagenten för att få hjälp med programvaruutvecklingsuppgifter.
* Hur du konfigurerar Cline för att kommunicera med LM Studio för lokal inferens av kodningsagenter.
* Hur du använder lokala kodningsagenter för att lösa verkliga programvaruutvecklingsuppgifter.

## Ange minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera programvaruuppdateringar
> **Obs**: Om VS Code inte är installerat kan du installera det via Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installera programvarukrav

<!-- @require:lmstudio,vscode -->

## Starta och konfigurera LM Studio

Vi kommer att använda LM Studio för att köra den LLM som driver kodningsagenten.

- I sökfältet söker du efter `LM Studio` och startar programmet. Du möts av följande sida.

![LM Studio startskärm](assets/initial-lm-studio.png)

Därefter måste vi läsa in LLM:en på systemet. Vi kommer att använda modellen `Qwen3-Coder-30B-A3B` med en stor kontextlängd. (Använd fliken Model för att installera den om du inte redan har gjort det).
- Klicka på sökfältet längst upp i LM Studio-fönstret eller tryck på `CTRL+L`. Klicka på reglaget `Manually choose model load parameters` och klicka sedan på modellen Qwen3-Coder-30B-A3B.
- Ändra kontextlängden från `4096` till `32768` och se till att `GPU Offload` är inställt på max. Klicka sedan på `Load Model`.

![Välja modell](assets/model-list-zoomed.png)

Vi använder en stor kontextlängd så att agenten kan bearbeta stora kodbaser och komma ihåg ändringar som har gjorts.

![Konfigurera modell](assets/selecting-model-zoomed.png)

Därefter måste vi aktivera LM Studio-servern.
- Klicka på fliken Developer eller tryck på `CTRL+2` i LM Studio till vänster.
- Kontrollera statustogeln och se till att den är inställd på `Running`.

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

## Starta och konfigurera VS Code

Vi kommer att installera Cline-tillägget i VS Code och ansluta det till LM Studio-servern vi just skapade.
- I sökfältet söker du efter `VS Code` och startar programmet.
- Klicka på ikonen `Extensions` i den vänstra kolumnen i VS Code och sök efter `Cline`. Klicka sedan på knappen `Install`.

![Installera Cline-tillägget](assets/installing-cline-vscode-extension.png)

- En Cline-ikon bör visas till vänster. Klicka på den för att öppna Cline. Ett fönster visas med frågan `How will you use Cline?` Eftersom vi kommer att använda en lokal LLM som körs via LM Studio väljer du `Bring my own API Key` och klickar på `Continue`.

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

![Kontoskapande](assets/cline-how-will-you-use-cline-zoomed.png)

Därefter måste vi konfigurera Cline för att kommunicera med LM Studio-servern som vi ställde in.
- Ange API-leverantören till `LM Studio` och modellen till `Qwen3-Coder-30B-A3B-GGUF`.

>**Tips**: Nyare modeller kan vara tillgängliga. Överväg att ladda ned och byta till Qwen3.6-modeller om så önskas.


![Modellkonfiguration](assets/cline-model-configuration-zoomed.png)

## Skapa ditt första projekt

Låt oss använda vår lokala agent för att skapa en webbplats! Öppna VSCode i en valfri katalog där Cline kommer att skapa filerna.
- Gör detta genom att gå till `File -> Open Folder` längst upp till vänster i VS Code och välj en mapp som `Documents`.

![VS Code tom mapp](assets/open-cline-test.png)

Nu är vi redo att ge instruktioner till den lokala kodningsagenten.
- Klicka på Cline-tillägget i den vänstra kolumnen och ange en prompt för att starta agenten. Som exempel kan vi använda följande prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agenten börjar sedan skapa filer enligt prompten. Som användare kan du se koden genereras i VS Code enligt nedan. Du kan behöva klicka på `Save` varje gång Cline vill skapa en fil.

![Cline kodgenerering](assets/cline-code-generation.png)

Efter att ha genererat programvaran är agenten klar och du kan köra programmet. I det här fallet skrev agenten till tre filer: `index.html`, `script.js` och `styles.css`. Genom att helt enkelt dubbelklicka på HTML-filen kan vi läsa in och interagera med den genererade webbplatsen.

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

## Nästa steg

Efter att ha genererat webbplatsen kan du fortsätta att arbeta med Cline för att förbättra den. Två möjliga förbättringar är:

- **Dokumentation**: Att ge agenten prompten `Add a README` räcker för att agenten ska generera en `README.md`-fil som dokumenterar webbplatsen.
- **Animation**: Ge modellen prompten `Add an animation that visually represents a large language model running on a laptop.` för att lägga till en animation på webbplatsen.

Vi uppmuntrar läsaren att försöka generera andra program med den här konfigurationen. Nedan följer några roliga exempel som vi har provat:

- **Retro-arkadspel**: Prova andra prompter. Det kan också vara roligt att låta agenten skapa retrostilsspel i Python med paketet `PyGame` med följande prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Dataanalys**: Ett område där kodningsagenter är särskilt användbara är skriptning och dataanalys. Här är en prompt som visar den lokala modellens förmåga att generera dataanalysprogramvara för visualisering av aktiekurser:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Resurser

Nedan finns ytterligare resurser för att lära dig mer om kodningsagenter, Cline och att köra arbetsbelastningar på

* Mer information om AMD:s LM Studio-partnerskap och integration: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD-blogg som beskriver hur man kör Cline på AMD Ryzen™ AI och Radeon™-grafikkort: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Clines blogg om att köra kodningsagenter lokalt på AI-datorer: https://cline.bot/blog/local-models-amd