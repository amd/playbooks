<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ez a playbook olyan speciális címkéket használ, amelyeket a GitHub nem tud megjeleníteni. A tartalom megfelelő előnézetéhez látogass el az [amd.com/playbooks](https://amd.com/playbooks) oldalra.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ehhez a playbookhoz legalább **32 GB** rendszermemória szükséges.
<!-- @device:end -->

## Áttekintés

A kódoló ügynökök (coding agents) hatékony eszközök, amelyek a fejlesztőket a nagy nyelvi modellekre (LLM) épülő AI-ügynökökkel való együttműködés révén segítik. Beilleszthetők a fejlesztői környezetbe, például a terminálba vagy a VS Code-ba, így zökkenőmentesen integrálódnak a fejlesztő munkafolyamatába.

Ez az útmutató bemutatja, hogyan futtathatsz teljes egészében helyi gépen egy kódoló ügynököt a Cline, a VS Code és az LM Studio segítségével.

## Amit tanulni fogsz

* Hogyan futtasd a VS Code-ot a Cline kódoló ügynökkel a szoftverfejlesztési feladatok segítésére.
* Hogyan konfiguráld a Cline-t úgy, hogy kommunikáljon az LM Studióval a kódoló ügynökök helyi következtetéséhez (inference).
* Hogyan használj helyi kódoló ügynököket valós szoftverfejlesztési problémák megoldásához. 

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheted a Ryzen AI Developer Centerrel.

<!-- @require:software-update -->
<!-- @device:end -->

## A szoftveres előfeltételek telepítése

<!-- @require:lmstudio,vscode -->

## Az LM Studio indítása és konfigurálása

Az LM Studiót fogjuk használni a kódoló ügynököt működtető LLM kiszolgálására.

- A keresősávban keress rá az `LM Studio`-ra, és indítsd el az alkalmazást. A következő oldal fog megjelenni.

![LM Studio kezdőképernyő](assets/initial-lm-studio.png)

Ezután be kell töltenünk az LLM-et a rendszerbe. A `Qwen3-Coder-30B-A3B` modellt fogjuk használni nagy kontextushosszal. (Ha még nincs telepítve, a Model fülön telepítheted).
- Kattints a keresősávra az LM Studio ablak tetején, vagy nyomd meg a `CTRL+L` billentyűkombinációt. Kattints a `Manually choose model load parameters` kapcsolóra, majd válaszd a Qwen3-Coder-30B-A3B modellt.
- Változtasd meg a kontextushosszt `4096`-ról `32768`-ra, és győződj meg róla, hogy a `GPU Offload` a maximumon van. Majd kattints a `Load Model` gombra.

![Modell kiválasztása](assets/model-list-zoomed.png)

Nagy kontextushosszt használunk, hogy az ügynök nagy kódbázisokat tudjon feldolgozni, és emlékezzen a végrehajtott módosításokra.

![Modell konfigurálása](assets/selecting-model-zoomed.png)

Ezután engedélyeznünk kell az LM Studio szervert. 
- Kattints a Developer fülre, vagy nyomd meg a `CTRL+2` billentyűkombinációt az LM Studio bal oldalán.
- Ellenőrizd a státuszkapcsolót, és győződj meg róla, hogy `Running` állapotban van.

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

![Szerver állapota](assets/lm-studio-server-status.png)

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

## A VS Code indítása és konfigurálása

Telepítjük a Cline bővítményt a VS Code-ban, és csatlakoztatjuk az imént létrehozott LM Studio szerverhez.
- A keresősávban keress rá a `VS Code`-ra, és indítsd el az alkalmazást.
- Kattints az `Extensions` ikonra a VS Code bal oldali oszlopában, és keress rá a `Cline`-ra. Majd kattints az `Install` gombra. 

![A Cline bővítmény telepítése](assets/installing-cline-vscode-extension.png)

- Egy Cline ikonnak meg kell jelennie a bal oldalon. Kattints rá a Cline megnyitásához. Megjelenik egy ablak a `How will you use Cline?` kérdéssel. Mivel egy helyi LLM-et fogunk használni, amely az LM Studión keresztül fut, válaszd a `Bring my own API Key` opciót, majd kattints a `Continue` gombra. 

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

![Fiók létrehozása](assets/cline-how-will-you-use-cline-zoomed.png)

Ezután konfigurálnunk kell a Cline-t, hogy kommunikáljon az általunk beállított LM Studio szerverrel. 
- Állítsd be az API Provider mezőt `LM Studio`-ra, a modellt pedig `Qwen3-Coder-30B-A3B-GGUF`-re. 

>**Tipp**: Előfordulhat, hogy újabb modellek is elérhetők. Ha szeretnéd, fontold meg a Qwen3.6 modellek letöltését és azokra való váltást.


![Modell konfigurálása](assets/cline-model-configuration-zoomed.png)

## Az első projekt létrehozása

Használjuk a helyi ügynökünket egy weboldal létrehozásához! Nyisd meg a VSCode-ot egy általad választott könyvtárban, ahová a Cline létrehozza majd a fájlokat.
- Ehhez kattints a `File -> Open Folder` menüpontra a VS Code bal felső sarkában, és válassz egy mappát, például a `Documents`-t.

![Üres mappa a VS Code-ban](assets/open-cline-test.png)

Most már készen állunk arra, hogy utasítást adjunk a helyi kódoló ügynöknek. 
- Kattints a Cline bővítményre a bal oldali oszlopban, és írj be egy promptot az ügynök elindításához. Példaként használjuk a következő promptot:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Az ügynök ezután megkezdi a fájlok létrehozását a prompt alapján. Felhasználóként végignézheted, ahogy a kód a VS Code-ban generálódik, amint az alább látható. Előfordulhat, hogy minden alkalommal rá kell kattintanod a `Save` gombra, amikor a Cline egy fájlt szeretne létrehozni. 

![Cline kódgenerálás](assets/cline-code-generation.png)

A szoftver előállítása után az ügynök feladata véget ér, és futtathatod az alkalmazást. Ebben az esetben az ügynök három fájlt írt: `index.html`, `script.js` és `styles.css`. Egyszerűen dupla kattintással a HTML fájlon betölthetjük és használhatjuk a generált weboldalt.

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
## Következő lépések

A weboldal legenerálása után továbbra is dolgozhat a Cline-nal a weboldal továbbfejlesztésén. Két lehetséges fejlesztés a következő:

- **Dokumentáció**: Az ügynök felkérése a `Add a README` paranccsal önmagában elegendő ahhoz, hogy az ügynök létrehozzon egy `README.md` fájlt, amely dokumentálja a weboldalt.
- **Animáció**: Kérje meg a modellt a `Add an animation that visually represents a large language model running on a laptop.` paranccsal, hogy generáljon egy animációt a weboldalhoz.

Biztatjuk az olvasót, hogy próbáljon meg más alkalmazásokat is generálni ezzel a beállítással. Az alábbiakban néhány szórakoztató példát mutatunk be, amelyeket kipróbáltunk:

- **Retro Arcade Games**: Próbáljon ki más promptokat is. Az ügynök számára az is szórakoztató lehet, ha retro stílusú játékokat hoz létre Pythonban a `PyGame` csomag használatával, a következő prompttal:

```code
Create a simple pong game using the PyGame python package.
```

- **Adatelemzés**: Az egyik terület, ahol a kódoló ügynökök különösen hasznosak, a szkriptelés és az adatelemzés. Ez egy prompt, amely bemutatja a helyi modell képességét részvényárfolyam-vizualizációhoz szükséges adatelemző szoftver generálására:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Erőforrások

Az alábbiakban további erőforrásokat talál, amelyekkel többet tudhat meg a kódoló ügynökökről, a Cline-ról és a munkaterhelések futtatásáról 

* További információk az AMD és az LM Studio partnerségéről és integrációjáról: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD blogbejegyzés a Cline futtatásáról AMD Ryzen™ AI és Radeon™ grafikus kártyákon: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline blogbejegyzés a kódoló ügynökök helyi futtatásáról AI PC-ken: https://cline.bot/blog/local-models-amd