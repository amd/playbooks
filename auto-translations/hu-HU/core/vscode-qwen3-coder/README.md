<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ez a playbook speciális címkéket használ, amelyeket a GitHub nem tud megjeleníteni. A tartalom helyes előnézetéhez látogasson el az [amd.com/playbooks](https://amd.com/playbooks) oldalra.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ez a playbook legalább **32 GB** rendszermemóriát igényel.
<!-- @device:end -->

## Áttekintés

A kódolási ügynökök hatékony eszközök, amelyek a fejlesztőket Nagy Nyelvi Modelleken (LLM-eken) alapuló AI ügynökökkel való együttműködés révén segítik. Beágyazhatók a fejlesztői környezetbe, például a terminálba vagy a VS Code-ba, lehetővé téve a zökkenőmentes integrációt a fejlesztő munkafolyamatába.

Ez az oktatóanyag bemutatja, hogyan használható a Cline, a VS Code és a LM Studio egy kódolási ügynök teljes mértékben helyi gépen való futtatásához.

## Mit fog megtanulni

* Hogyan futtassa a VS Code-ot a Cline kódolási ügynökkel a szoftverfejlesztési feladatok támogatásához.
* Hogyan konfigurálja a Cline-t, hogy kommunikáljon a LM Studio-val a kódolási ügynökök helyi következtetéséhez.
* Hogyan használja a helyi kódolási ügynököket valós szoftverfejlesztési feladatok megoldásához.

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, a Ryzen AI Developer Center segítségével telepítheti.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése

<!-- @require:lmstudio,vscode -->

## A LM Studio elindítása és konfigurálása

A LM Studio-t fogjuk használni a kódolási ügynököt működtető LLM kiszolgálásához.

- A keresősávban keressen rá a `LM Studio` kifejezésre, és indítsa el az alkalmazást. A következő oldal fogadja majd.

![LM Studio kezdőképernyő](assets/initial-lm-studio.png)

Ezután be kell tölteni az LLM-et a rendszerre. A `Qwen3-Coder-30B-A3B` modellt fogjuk használni nagy kontextushosszal. (Ha még nem tette meg, a Model fülön telepítheti.)
- Kattintson a LM Studio ablak tetején lévő keresősávra, vagy nyomja meg a `CTRL+L` billentyűkombinációt. Kattintson a `Manually choose model load parameters` kapcsolóra, majd kattintson a Qwen3-Coder-30B-A3B modellre.
- Módosítsa a kontextushosszt `4096`-ról `32768`-ra, és győződjön meg arról, hogy a `GPU Offload` maximumon van. Ezután kattintson a `Load Model` gombra.

![Modell kiválasztása](assets/model-list-zoomed.png)

Nagy kontextushosszt használunk, hogy az ügynök nagy kódbázisokat is fel tudjon dolgozni, és emlékezzen az elvégzett módosításokra.

![Modell konfigurálása](assets/selecting-model-zoomed.png)

Ezután engedélyezni kell a LM Studio szervert.
- Kattintson a Developer fülre, vagy nyomja meg a `CTRL+2` billentyűkombinációt a LM Studio bal oldalán.
- Ellenőrizze az állapotkapcsolót, és győződjön meg arról, hogy `Running` állapotban van.

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

## A VS Code elindítása és konfigurálása

Telepítjük a Cline bővítményt a VS Code-ba, és csatlakoztatjuk az imént létrehozott LM Studio szerverhez.
- A keresősávban keressen rá a `VS Code` kifejezésre, és indítsa el az alkalmazást.
- Kattintson a VS Code bal oszlopában lévő `Extensions` ikonra, és keressen rá a `Cline` kifejezésre. Ezután kattintson az `Install` gombra.

![A Cline bővítmény telepítése](assets/installing-cline-vscode-extension.png)

- A bal oldalon megjelenik egy Cline ikon. Kattintson rá a Cline megnyitásához. Megjelenik egy ablak, amely megkérdezi: `How will you use Cline?` Mivel helyi LLM-et fogunk használni a LM Studio-n keresztül, válassza a `Bring my own API Key` lehetőséget, majd kattintson a `Continue` gombra.

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

Ezután konfigurálni kell a Cline-t, hogy kommunikáljon a beállított LM Studio szerverrel.
- Állítsa az API-szolgáltatót `LM Studio`-ra, a modellt pedig `Qwen3-Coder-30B-A3B-GGUF`-re.

>**Tipp**: Újabb modellek is elérhetők lehetnek. Szükség esetén fontolja meg a Qwen3.6 modellek letöltését és arra való váltást.


![Modellkonfiguráció](assets/cline-model-configuration-zoomed.png)

## Az első projekt létrehozása

Használjuk a helyi ügynököt egy weboldal létrehozásához! Nyissa meg a VSCode-ot egy tetszőleges könyvtárban, ahol a Cline létrehozza a fájlokat.
- Ehhez lépjen a VS Code bal felső sarkában a `File -> Open Folder` menüpontra, és válasszon egy mappát, például a `Documents` mappát.

![VS Code üres mappa](assets/open-cline-test.png)

Most készen állunk a helyi kódolási ügynök utasítással való ellátására.
- Kattintson a bal oszlopban lévő Cline bővítményre, és adjon meg egy utasítást az ügynök elindításához. Példaként használjuk a következő utasítást:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Az ügynök ezután elkezdi létrehozni a fájlokat az utasítás szerint. Felhasználóként figyelheti a kód generálását a VS Code-ban az alábbiakban látható módon. Előfordulhat, hogy minden alkalommal, amikor a Cline fájlt szeretne létrehozni, a `Save` gombra kell kattintania.

![Cline kódgenerálás](assets/cline-code-generation.png)

A szoftver generálása után az ügynök befejezi a munkát, és futtathatja az alkalmazást. Ebben az esetben az ügynök három fájlba írt: `index.html`, `script.js` és `styles.css`. A HTML-fájlra duplán kattintva betöltheti és használhatja a generált weboldalt.

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

A weboldal generálása után folytathatja a munkát a Cline-nal a weboldal fejlesztése érdekében. Két lehetséges fejlesztés:

- **Dokumentáció**: Az ügynök `Add a README` utasítással való ellátása elegendő ahhoz, hogy az ügynök létrehozzon egy `README.md` fájlt, amely dokumentálja a weboldalt.
- **Animáció**: Az `Add an animation that visually represents a large language model running on a laptop.` utasítással animációt adhat a weboldalhoz.

Bátorítjuk az olvasót, hogy próbáljon más alkalmazásokat is generálni ezzel a beállítással. Az alábbiakban néhány szórakoztató példát mutatunk be, amelyeket kipróbáltunk:

- **Retró arcade játékok**: Próbáljon ki más utasításokat. Szórakoztató lehet, ha az ügynök retró stílusú játékokat hoz létre Pythonban a `PyGame` csomag használatával a következő utasítással:

```code
Create a simple pong game using the PyGame python package.
```

- **Adatelemzés**: Az egyik terület, ahol a kódolási ügynökök különösen hasznosak, a szkriptelés és az adatelemzés. Ez egy utasítás a helyi modell azon képességének bemutatására, hogy részvényárfolyam-vizualizációhoz adatelemző szoftvert generáljon:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Erőforrások

Az alábbiakban további erőforrások találhatók a kódolási ügynökökről, a Cline-ról és a munkaterhelések futtatásáról való további tájékozódáshoz.

* További információ az AMD és a LM Studio partnerségéről és integrációjáról: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD blog a Cline AMD Ryzen™ AI és Radeon™ grafikus kártyákon való futtatásáról: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline blog a kódolási ügynökök helyi futtatásáról AI PC-ken: https://cline.bot/blog/local-models-amd