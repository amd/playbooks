<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ez a playbook legalább **32 GB** rendszermemóriát igényel.
<!-- @device:end -->

## Áttekintés

A kódoló ügynökök (coding agents) hatékony eszközök, amelyek a nagy nyelvi modellek (LLM-ek) által támogatott AI-ügynökökkel való együttműködésen keresztül segítik a fejlesztők munkáját. Beágyazhatók a fejlesztői környezetbe, például a terminálba vagy a VS Code-ba, így zökkenőmentesen illeszkednek a fejlesztő munkafolyamatába.

Ez az útmutató bemutatja, hogyan használhatod a Cline-t, a VS Code-ot és az LM Studio-t egy teljesen a helyi gépeden futó kódoló ügynök futtatásához.

## Amit meg fogsz tanulni

* Hogyan futtasd a VS Code-ot a Cline kódoló ügynökkel a szoftverfejlesztési feladatok elősegítéséhez.
* Hogyan konfiguráld a Cline-t, hogy az LM Studio-val kommunikáljon a kódoló ügynökök helyi következtetéséhez (inference).
* Hogyan használj helyi kódoló ügynököket valós szoftverfejlesztési feladatok megoldásához.

<!-- @device:halo_box,halo,stx,krk -->
## Memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések keresése
> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheted a Ryzen AI Developer Center segítségével.

<!-- @require:software-update -->
<!-- @device:end -->

## A szükséges szoftverek telepítése

<!-- @require:lmstudio,vscode -->

## Az LM Studio indítása és konfigurálása

Az LM Studio-t fogjuk használni a kódoló ügynököt működtető LLM kiszolgálásához.

- A keresősávban keress rá az `LM Studio` névre, és indítsd el az alkalmazást. A következő oldal fog megjelenni.

![LM Studio kezdőképernyő](assets/initial-lm-studio.png)

Ezután be kell töltenünk az LLM-et a rendszerbe. A `Qwen3-Coder-30B-A3B` modellt fogjuk használni nagy kontextushosszal. (Ha még nincs telepítve, használd a Model fület a telepítéshez.)
- Kattints a keresősávra az LM Studio ablak tetején, vagy nyomd meg a `CTRL+L` billentyűkombinációt. Kattints a `Manually choose model load parameters` kapcsolóra, majd kattints a Qwen3-Coder-30B-A3B modellre.
- Változtasd meg a kontextushosszt `4096`-ról `32768`-ra, és győződj meg róla, hogy a `GPU Offload` a maximumon van. Ezután kattints a `Load Model` gombra.

![Modell kiválasztása](assets/model-list-zoomed.png)

Nagy kontextushosszt használunk, hogy az ügynök nagy kódbázisokat is fel tudjon dolgozni, és emlékezzen a végrehajtott módosításokra.

![Modell konfigurálása](assets/selecting-model-zoomed.png)

Ezután engedélyeznünk kell az LM Studio szervert.
- Kattints a Developer fülre, vagy nyomd meg a `CTRL+2` billentyűkombinációt az LM Studio bal oldalán.
- Ellenőrizd az állapotkapcsolót, és győződj meg róla, hogy `Running` értékre van állítva.

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

## A VS Code indítása és konfigurálása

Telepíteni fogjuk a Cline bővítményt a VS Code-ba, és összekapcsoljuk az imént létrehozott LM Studio szerverrel.
- A keresősávban keress rá a `VS Code` névre, és indítsd el az alkalmazást.
- Kattints az `Extensions` ikonra a VS Code bal oldali oszlopában, és keress rá a `Cline` névre. Ezután kattints az `Install` gombra.

![Cline bővítmény telepítése](assets/installing-cline-vscode-extension.png)

- Ekkor egy Cline ikon jelenik meg a bal oldalon. Kattints rá a Cline megnyitásához. Megjelenik egy ablak, amely megkérdezi: `How will you use Cline?` Mivel az LM Studio-n keresztül futó helyi LLM-et fogjuk használni, válaszd a `Bring my own API Key` lehetőséget, majd kattints a `Continue` gombra.

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
- Állítsd az API Provider értékét `LM Studio`-ra, a modellt pedig `Qwen3-Coder-30B-A3B-GGUF`-ra.

>**Tipp**: Előfordulhat, hogy újabb modellek is elérhetők. Ha szeretnéd, fontold meg a Qwen3.6 modellek letöltését és azokra való átváltást.


![Modell konfigurálása](assets/cline-model-configuration-zoomed.png)

## Az első projekt létrehozása

Használjuk a helyi ügynökünket egy weboldal létrehozásához! Nyisd meg a VSCode-ot egy tetszőleges könyvtárban, ahol a Cline létre fogja hozni a fájlokat.
- Ehhez lépj a `File -> Open Folder` menüpontra a VS Code bal felső sarkában, és válassz egy mappát, például a `Documents` mappát.

![Üres mappa a VS Code-ban](assets/open-cline-test.png)

Most már készen állunk arra, hogy utasítást adjunk a helyi kódoló ügynöknek.
- Kattints a bal oldali oszlopban a Cline bővítményre, és írj be egy promptot az ügynök elindításához. Például használjuk a következő promptot:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Az ügynök ezután elkezdi létrehozni a fájlokat a prompt alapján. Felhasználóként figyelemmel kísérheted a kód generálását a VS Code-ban, az alábbiakban látható módon. Előfordulhat, hogy minden alkalommal rá kell kattintanod a `Save` gombra, amikor a Cline egy fájlt szeretne létrehozni.

![Cline kódgenerálás](assets/cline-code-generation.png)

A szoftver legenerálása után az ügynök feladata befejeződött, és futtathatod az alkalmazást. Ebben az esetben az ügynök három fájlt hozott létre: `index.html`, `script.js` és `styles.css`. Egyszerűen dupla kattintással a HTML fájlra betölthetjük és megnyithatjuk a generált weboldalt.

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

## Következő lépések

A weboldal legenerálása után folytathatod a munkát a Cline-nal a weboldal továbbfejlesztése érdekében. Két lehetséges fejlesztés:

- **Dokumentáció**: Elegendő az `Add a README` utasítást megadni az ügynöknek, és az egy `README.md` fájlt generál, amely dokumentálja a weboldalt.
- **Animáció**: Adj a modellnek egy `Add an animation that visually represents a large language model running on a laptop.` promptot, hogy animációt generáljon a weboldalhoz.

Arra biztatjuk az olvasót, hogy próbáljon más alkalmazásokat is generálni ezzel a beállítással. Íme néhány szórakoztató példa, amit mi is kipróbáltunk:

- **Retro arcade játékok**: Próbálj ki más promptokat is. Az is szórakoztató lehet, ha az ügynök retró stílusú játékokat hoz létre Pythonban a `PyGame` csomag segítségével, a következő prompttal:

```code
Create a simple pong game using the PyGame python package.
```

- **Adatelemzés**: Az egyik terület, ahol a kódoló ügynökök különösen hasznosak, a szkriptelés és az adatelemzés. Ez egy prompt, amely bemutatja a helyi modell képességét részvényárfolyamok vizualizációját szolgáló adatelemző szoftver generálására:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Erőforrások

Az alábbiakban további erőforrásokat talál a Coding Agentekről, a Cline-ról, valamint a munkaterhelések futtatásáról szóló bővebb tájékozódáshoz.

* További információk az AMD és az LM Studio partnerségéről és integrációjáról: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD blogbejegyzés a Cline futtatásáról AMD Ryzen™ AI és Radeon™ grafikus kártyákon: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline blogbejegyzés a kódoló ágensek helyi futtatásáról AI PC-ken: https://cline.bot/blog/local-models-amd