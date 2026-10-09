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

## Áttekintés

🍋 A **Lemonade** egy nyílt forráskódú, helyi AI-szerver, amellyel nagy nyelvi modelleket (LLM-eket), képgenerátorokat és hangmodelleket futtathatsz közvetlenül a saját hardveredenn. A modelleket az iparágban szabványosnak számító **OpenAI API**-n keresztül teszi elérhetővé, így bármely alkalmazás, amely az OpenAI-val működik, azonnal működik a Lemonade-dal is. A playbook végére a Lemonade-ot fogod használni ahhoz, hogy modelleket futtass helyben a gépeden.

## Mit Fogsz Megtanulni

A playbook végére képes leszel:

* **Telepíteni a Lemonade Server-t**, és ellenőrizni, hogy fut-e.
* **Letölteni és beszélgetni egy LLM-mel** egyetlen paranccsal.
* **Felfedezni a webes felhasználói felületet**, és kipróbálni különböző modalitásokat, például képi felismerést, beszéd-szöveg átalakítást és képgenerálást.
* **Váltani a GPU háttérrendszerek között** Vulkan és AMD ROCm™ szoftver között.
* **Készíteni egy Python alkalmazást**, amelyet egy helyi LLM hajt meg, az OpenAI-kompatibilis API segítségével.
<!-- @device:halo_box,halo,stx,krk -->
* **Modelleket futtatni az AMD Neural Processing Unit (NPU)** egységen, Hybrid és FLM végrehajtási módokat használva AMD Ryzen™ AI hardveren.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## A Memóriakonfiguráció Beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések Ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftveres Előfeltételek Telepítése

Mielőtt elkezdenéd, győződj meg róla, hogy rendelkezel a következőkkel:

- Egy számítógép, amelyen **Windows 11** vagy egy támogatott **Linux** disztribúció fut (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** ajánlott az 1–7. lépésekben használt futtatási modellhez (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** ajánlott, ha a nagyobb kódgeneráló modellt szeretnéd használni a 6. lépésben (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB szabad lemezterület**, a letöltött modellektől függően. A legnagyobb modell ebben az útmutatóban körülbelül 20 GB.
- **Python 3.10–3.13** (a Python alkalmazás részben használva)
- Internetkapcsolat (vezetékes vagy vezeték nélküli)
<!-- @device:halo_box,halo,stx,krk -->
- [Opcionális] Egy AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 sorozat vagy Z2 Extreme) a legújabb telepített illesztőprogrammal a [Ryzen AI Szoftver Telepítési Útmutató](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) alapján, ha egy modellt szeretnél futtatni az NPU-n.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade-models-gemma-4-e2b,lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-update-linux timeout=300 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

---

## Alapfogalmak — Hogyan Működnek a Helyi AI-Szerverek

Mielőtt futtatnánk egy modellt, érdemes megérteni, *miért* van így felépítve a rendszer. A Lemonade egy **helyi modellszerver**, egy olyan folyamat, amely AI-modelleket tölt be a memóriába, és HTTP-n keresztül teszi elérhetővé őket az alkalmazások számára, ugyanúgy, ahogy egy felhőalapú AI-szolgáltatás tenné.

### Miért Szerver?

| Előny | Mit Jelent Ez Számodra |
|---------|----------------------|
| **Egyszerűsített integráció** | Az alkalmazások egyetlen HTTP API-n keresztül kommunikálnak, ahelyett, hogy hardverspecifikus C++ vagy Python könyvtárakkal kellene foglalkozniuk. |
| **Megosztott modellek** | Egyetlen betöltött modell egyszerre több alkalmazást is kiszolgálhat, nincs szükség duplikált másolatokra, amelyek feleslegesen fogyasztanák a RAM-ot. |
| **Felhő-helyi hordozhatóság** | Az OpenAI felhőalapú API-jához írt kód a Lemonade-dal is működik, mindössze egyetlen URL megváltoztatásával. |
| **Felelősségek szétválasztása** | A modellkezelést, az adatfolyam-kezelést és a hibatűrést a szerver kezeli, így a fejlesztők az alkalmazásukra összpontosíthatnak. |

### Az OpenAI API Szabvány

A Lemonade az **OpenAI API**-t valósítja meg, ugyanazt az interfészt, amelyet a ChatGPT, az Azure OpenAI és sok más szolgáltatás is használ. A beszélgetési modell egyszerű:

| Szerep | Ki Beszél |
|------|---------------|
| **system** | Utasítások a modell számára (persona, korlátozások, elérhető eszközök) |
| **user** | Üzenetek az embertől (vagy alkalmazástól) a modell felé |
| **assistant** | A modell által generált válaszok |

Ez azt jelenti, hogy bármely könyvtár vagy alkalmazás, amely támogatja az OpenAI-t, kommunikálhat a Lemonade-dal, ha a `http://localhost:13305/api/v1` címre irányítja, amíg a Lemonade Server fut.

## Fő Tevékenység — Az Első Helyi AI Beszélgetésed

Töltsünk le egy LLM-et, és beszélgessünk vele, úgy, hogy az AI teljes egészében a saját gépeden fut.

### 1. Lépés: Modell Letöltése és Futtatása

A Lemonade egy gondosan válogatott modellkönyvtárral érkezik. Kezdjük a **Gemma-4-E2B-it**-tel, egy képes és kompakt modellel, amely tartalmaz képi felismerési támogatást is. Nyiss meg egy terminált, és futtasd:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Ez az egyetlen parancs három dolgot tesz:

1. **Letölti** a modellt (~3 GB) a Hugging Face-ről, ha még nincs letöltve. (Eltarthat egy ideig)
2. **Elindítja** a Lemonade Server folyamatot a 13305-ös porton.
3. **Megnyitja a Lemonade App-ot**, hogy azonnal beszélgethess a modellel.


<!-- @os:windows -->
Windows alatt a Lemonade App automatikusan elindul, és azonnal elkezdhetsz beszélgetni. Ha a `minimal.msi` csomagot telepítetted, az alkalmazás nincs benne. A beszélgetés elkezdéséhez nyisd meg a webböngésződet, és navigálj a `http://localhost:13305` címre.
<!-- @os:end -->

<!-- @os:linux -->
Linux alatt nyisd meg a böngésződet, és navigálj a `http://localhost:13305` címre a webalkalmazás eléréséhez.
<!-- @os:end -->

Próbálj meg beírni egy kérdést:

```
What are three fun facts about lemons?
```

A modell közvetlenül a csevegőablakban fog válaszolni. **Gratulálunk! Egy nagy nyelvi modellt futtatsz helyben.**

![Lemonade App naplókkal megjelenítve](../../dependencies/assets/ChatwithLogs.png)

A Lemonade App Server Logs paneljén telemetriai adatokat találsz a modell teljesítményéről minden válasz után. Például:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### 2. lépés: Fedezd fel a webes felületet és a különböző modalitásokat

A Lemonade tartalmaz egy beépített webes felületet, amelyen keresztül:

- **Interakcióba léphetsz** a betöltött modellel egy ismerős csevegőablakban
- **Böngészhetsz a modellek között** a Model Manager fülön
- **Új modelleket tölthetsz le** egyetlen kattintással

Próbálj meg váltani a különböző modalitások között a webes felület **Model Manager** fülén, ahol a modelleket Recipe vagy Category szerint böngészheted:

1. **Vision:** A már betöltött `Gemma-4-E2B-it-GGUF` modell támogatja a vizuális bemenetet. Illessz be egy képet a csevegőmezőbe, és kérd meg a modellt, hogy írja le azt.
2. **Image generation:** Az Image kategóriában tölts le egy képgeneráló modellt, például az `SDXL-Turbo`-t a Model Managerből, majd a Lemonade Image Generator segítségével írj be egy promptot, és generálj képet helyben.
3. **Audio:** Az Audio kategóriában tölts le egy hangmodellt, például a `Whisper-Tiny`-t, amely beszédet tud szöveggé alakítani. Adj meg egy hangfelvételt, hogy helyben átírja azt szöveggé. Szövegből beszéddé alakításhoz próbáld ki a Speech kategória valamelyik modelljét, például a `kokoro-v1`-et.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### 3. lépés: Próbálj ki egy modellt más háttérrel (backend)

Ha az egérmutatót egy modell fölé viszed a Lemonade appban, megjelenik egy fogaskerék ikon. Erre kattintva kiválaszthatod a modell beállításait, beleértve a kívánt backend kiválasztását is.

A Lemonade alapértelmezés szerint Vulkan-t használ a GPU-gyorsításhoz. Ha támogatott AMD diszkrét GPU-d van, átválthatsz ROCm-re.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

A telepített backendek kezeléséhez kattints a legbaloldalibb oszlopban található backend gombra.

Alternatívaként a backendet a következő paranccsal is megadhatod:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Az alapértelmezett backendet a `LEMONADE_LLAMACPP` környezeti változóval is beállíthatod, a következő értékekkel: `vulkan`, `rocm`, vagy `cpu`.

---

## Mélyebbre ásva — Építs egy AI-alapú alkalmazást Python nyelven

A helyi AI-szerver igazi ereje abban rejlik, hogy bármely alkalmazás csatlakozhat hozzá mindössze néhány sornyi kóddal. Ennek bizonyítására építsünk egy kicsi, de működőképes **tanulókártya-generátort**, ahol megadsz egy témát, az alkalmazás tanulókártyákat generál, és interaktívan kikérdezheted magad.

### 4. lépés: Indítsd el a szervert

Ellenőrizd, hogy a Lemonade szerver fut-e. Telepítés után általában automatikusan elindul a háttérben. Az ellenőrzéshez futtasd:

```
lemonade status
```

Egy ehhez hasonló üzenetet kell látnod: `Server is running on port 13305`.

Ha a szerver nem fut, indítsd el a Lemonade alkalmazás megnyitásával. Használd az alapértelmezett **13305** portot (ezt a tálca ikonjánál megerősítheted vagy kiválaszthatod).

### 5. lépés: Telepítsd az OpenAI Python klienst

Egy terminálban hozz létre egy venv-et, és telepítsd az OpenAI Python klienst a következő parancsokkal:
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### 6. lépés: Építsd meg a Flashcard alkalmazást

Töltsünk le egy másik modellt a kód generálásához: `Qwen3.5-35B-A3B-GGUF`. Ez egy nagy (~20 GB) és nagy teljesítményű modell, amely leginkább 32 GB+ RAM-mal rendelkező rendszerekhez illik. Ha kevesebb RAM áll rendelkezésre, próbáld ki helyette a `Qwen3.5-9B-GGUF`-ot (~6 GB).

Letöltheted a felületről, vagy futtathatod a következőt:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Illeszd be a következő promptot a Lemonade Chat UI-ba, hogy kódot generálj egy egyszerű Flashcard alkalmazáshoz.

A `Qwen3.5-35B-A3B-GGUF` modellt (egy nagyobb modellt, amely jobban ír kódot) fogjuk használni a Python alkalmazásunk generálásához, maga az alkalmazás pedig futásidőben a `Gemma-4-E2B-it-GGUF`-ot (a már letöltött kisebb modellt) hívja meg. A kódot ezután bemásolhatod egy általad választott fájlba, hogy Pythonban futtathasd.

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **Tipp**: A szabványos mérnöki gyakorlatokat követtük az alapos promptkészítéssel és egy kétmodelles rendszer használatával az erőforrások és a sebesség optimalizálása érdekében.

Kényelmed érdekében biztosítottunk egy minta kimenetet a [`flashcards.py`](assets/flashcards.py) fájlban. Nyugodtan töltsd le a saját könyvtáradba. Bármelyik módszert is választod, most már rendelkezned kell egy futtatható Python fájllal.

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### 7. lépés: Futtasd a generált kódot

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Íme, amit látnod kell:**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

Mindössze körülbelül 150 sornyi kódból felépítettél egy teljesen működőképes tanulóeszközt, amelyet egy helyi LLM hajt meg. Nincs kezelendő API-kulcs, nincs használati költség, és soha nem hagyja el az adat a gépedet.

> **Kulcsfontosságú meglátás:** Figyeld meg, hogy a `client = OpenAI(base_url=...) ` sor az *egyetlen* dolog, amely ezt az alkalmazást a Lemonade-hez köti az OpenAI felhője helyett. A kód többi része teljesen megegyezik azzal, amit bármely OpenAI-kompatibilis szolgáltatás ellen írnál. Ha valaha használtad az OpenAI Python könyvtárat, már most tudod, hogyan építs alkalmazásokat a Lemonade-del.

### Mit demonstrál ez

Ez a kis alkalmazás több valós integrációs mintát is bemutat:

| Minta | Hol jelenik meg |
|---------|-----------------|
| **Rendszerpromptok** | A `"system"` üzenet utasítja az LLM-et, hogy strukturált JSON-t adjon ki |
| **Strukturált kimenet** | Az alkalmazás az LLM válaszát JSON-ként elemzi, hogy felépítse a tanulókártyákat |
| **Állapotmentes kérések** | Minden `generate_flashcards()` hívás független |
| **Hibakezelés** | A `try/except` elegánsan kezeli azokat az eseteket, amikor az LLM kimenete nem érvényes JSON |

Ugyanezek a minták bármely alkalmazásra skálázhatók, például chatbotokra, kódasszisztensekre, tartalomgenerátorokra, automatizálási eszközökre.

#### Bónusz kihívás

* Extra kihívásként próbáld meg frissíteni az alkalmazást úgy, hogy a tanulókártyákat felolvassa a felhasználónak, az [itt](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) elérhető példa alapján.

---

<!-- @device:halo_box,halo,stx,krk -->
## Modellek futtatása NPU-n (opcionális)

Ha Ryzen AI 300/400/Max 300 sorozatú vagy Z2 Extreme eszközzel rendelkezel, akkor az eszközödben van egy beépített **Neurális Feldolgozó Egység (NPU)**, egy kifejezetten AI munkaterhelésekhez tervezett dedikált chip. A modellek NPU-n történő futtatása energiahatékonyabb, mint a GPU használata, ami ideálissá teszi háttérben futó AI feladatokhoz, hosszabb munkamenetekhez és akkumulátoros használathoz.

A Lemonade három NPU végrehajtási módot támogat, mindegyik átlátszó módon ugyanazon az OpenAI API-n keresztül érhető el:

| Mód | Működés | Recept | Példamodellek |
|------|-------------|--------|----------------|
| **Hibrid (NPU + iGPU)** | Az NPU feldolgozza a promptot, az iGPU generálja a tokeneket | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Csak NPU** | A teljes következtetés az NPU-n fut | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | A FastFlowLM motort használja az NPU-n, AMD XDNA2-re optimalizálva | FLM (`flm`) | qwen3.5-4b-FLM |

### Követelmények

- **AMD Ryzen AI 300/400 sorozatú vagy Z2 sorozatú** processzor
- **FLM** modellekhez: Az FLM futtatókörnyezet telepíthető a Lemonade alkalmazásból, vagy a Lemonade automatikusan telepíti az FLM futtatókörnyezetet egy FLM modell futtatásakor. A FastFlowLM-ről bővebben [itt](https://fastflowlm.com/docs/) olvashatsz.


### 8. lépés: Hibrid modell futtatása

A hibrid modellek megosztják a munkát az NPU és az iGPU között, így jó egyensúlyt biztosítanak a sebesség és a hatékonyság között. A Lemonade alkalmazásban válassz egy modellt a `Ryzen AI LLM` listából, például a `Qwen3-4B-Hybrid` modellt, vagy futtasd a következő paranccsal:

```
lemonade run Qwen3-4B-Hybrid
```

A Lemonade automatikusan felismeri az NPU-dat, és telepíti a **Ryzen AI LLM** háttérrendszert.

> **Mi történik a háttérben?** Amikor üzenetet küldesz, az NPU párhuzamosan dolgozza fel a teljes promptot (ezt nevezzük „prefill”-nek). Ezután az iGPU veszi át a munkát, és tokenenként generálja a választ (ezt nevezzük „decode”-nak). Ez a hibrid megközelítés mindkét chip erősségeit kihasználja.

### 9. lépés: FLM modell futtatása

A FastFlowLM (FLM) modellek kifejezetten az AMD XDNA2 NPU architektúrájára vannak optimalizálva, és a méretükhöz képest nagyon gyorsak lehetnek. Például válaszd ki a `qwen3.5-4b-FLM` modellt a `FastFlowLM NPU` listából, vagy használd a következő parancsot:

<!-- @os:windows -->
A `FastFlowLM` engedélyezése Windows rendszeren:

* Nyisd meg a `Backends Manager` menüt.
* Keresd meg a `FastFlowLM NPU` háttérrendszer kategóriát.
* Kattints az Install NPU gombra.
* A telepítés befejezése után ~36 alapértelmezett modell lesz elérhető az FFLM legördülő menüben.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Amikor a `Lemonade` alkalmazást először indítod el, a `FastFlowNPU` háttérrendszer alapértelmezés szerint nincs engedélyezve. 
A helyi alkalmazás megnyitja a telepítési oldalt, hogy végigvezessen a beállításon.

A `FastFlowLM` engedélyezése Linux rendszeren:

* Nyisd meg a `Lemonade` alkalmazást.
* Látogass el a [hivatalos FLM](https://lemonade-server.ai/flm_npu_linux.html) dokumentációra, és kövesd az FLM telepítési lépéseit a Linux disztribúciód kiválasztásával.
* Engedélyezd a backportokat a telepítési oldalon leírtak szerint.
* Töltsd le a legújabb `v0.9.x` kiadást a [tags oldalról](https://github.com/FastFlowLM/FastFlowLM/tags).

<!-- @device:halo_box -->
>[!Note]
Az AMD Halo Developer Platform esetén feltétlenül a Debian 13 verziót válaszd.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Telepítsd a letöltött `.deb` csomagot.
* Ajánlott: Zárd be a `Lemonade App`-ot, majd nyisd meg újra, hogy a változások érvénybe lépjenek.
* Ajánlott: Nyisd meg a `Backends Manager`-t, és kattints a `FastFlowNPU` háttérrendszer Install gombjára.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Sikeres telepítés után a **Lemonade Desktop App** **Download Manager** részében azt kell látnod, hogy a `flm:npu` befejeződött.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Ezután kiválaszthatod bármelyik elérhető FFLM modellt, és elkezdheted használni az NPU háttérrendszert.

Egy adott modellhez töltsd le a kívánt modellt a [modellek oldaláról](https://fastflowlm.com/docs/models/qwen/), és érvényesítsd a dokumentációban megadott Shell paranccsal.
```
flm run qwen3.5-4b-FLM
```
vagy 
```
lemonade run qwen3.5-4b-FLM
```

Az FLM modellek néhány legnépszerűbb architektúrát tartalmaznak (Gemma 3, Qwen 3, Llama 3 és DeepSeek R1), és méretük 1 GB alattitól 13 GB felettiig terjed.
A Lemonade automatikusan felismeri az NPU-dat, és telepíti a **FastFlowLM NPU** háttérrendszert.

<!-- @os:windows -->
> **Tipp:** A legjobb NPU teljesítmény érdekében engedélyezd a turbo módot:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Modellek váltása

A 6. lépésből ismert kártyázós alkalmazás NPU modellekkel is működik, csak változtasd meg a modell nevét:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Következő lépések

Most már van egy saját hardvereden futó helyi AI szervered, íme, hogy merre érdemes tovább haladni:

1. **Csatlakoztasd a kedvenc alkalmazásaidat**: A Lemonade dobozból is működik a [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), az [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), a [Continue](https://lemonade-server.ai/docs/server/apps/continue/), az [n8n](https://n8n.io/integrations/lemonade-model/), és [még sok más](https://lemonade-server.ai/marketplace) alkalmazással.

2. **Böngéssz további modellek között**: Fedezd fel a teljes [modellkönyvtárat](https://lemonade-server.ai/docs/server/server_models/), hogy olyan modelleket találj, amelyek kódoláshoz, érveléshez, látáshoz és egyebekhez vannak optimalizálva. Használd a Lemonade alkalmazást vagy a `lemonade list` parancsot, hogy megnézd, mi érhető el.

3. **Oldd fel a ROCm GPU gyorsítást**: Ha rendelkezel egy támogatott AMD GPU-val, válts a ROCm háttérrendszerre: `lemonade config set llamacpp.backend=rocm`. Lásd a [támogatott AMD GPU-kat](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Olvasd el a teljes API specifikációt**: A Lemonade támogatja a chat completions, embeddings, hangátirat, kép generálás, szövegfelolvasás és egyéb funkciókat. Lásd a [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) dokumentumot az összes végponthoz.

5. **Járulj hozzá**: A Lemonade nyílt forráskódú. Nézd meg a [közreműködési útmutatót](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md), és keress [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) címkéjű feladatokat.

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->