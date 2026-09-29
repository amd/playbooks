<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

## Áttekintés

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

🍋 A **Lemonade** egy nyílt forráskódú, helyi AI szerver, amellyel nagy nyelvi modelleket (LLM-eket), képgenerátorokat és hangmodelleket futtathat közvetlenül a saját hardverén. A modelleket az iparági szabványnak számító **OpenAI API**-n keresztül teszi elérhetővé, így bármely alkalmazás, amely az OpenAI-jal működik, azonnal képes lesz együttműködni a Lemonade-del is. A gyakorlati útmutató végére a Lemonade segítségével fog modelleket futtatni helyben, a saját gépén.

## Amit tanulni fog

Az útmutató végére képes lesz:

* **Telepíteni a Lemonade Servert**, és ellenőrizni, hogy fut-e.
* **Letölteni egy LLM-et és beszélgetni vele** egyetlen paranccsal.
* **Felfedezni a webes felhasználói felületet**, és kipróbálni különféle modalitásokat, például a látást, a beszédfelismerést és a képgenerálást.
* **Váltani a GPU háttérrendszerek** (backendek) között Vulkan és AMD ROCm™ szoftver között.
* **Egy Python alkalmazást építeni**, amelyet egy helyi LLM hajt meg, az OpenAI-kompatibilis API segítségével.
<!-- @device:halo_box,halo,stx,krk -->
* **Modelleket futtatni az AMD Neural Processing Unit (NPU) egységen**, Hybrid és FLM végrehajtási módok használatával AMD Ryzen™ AI hardveren.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szükséges szoftverek telepítése

Mielőtt elkezdené, győződjön meg róla, hogy rendelkezik a következőkkel:

- Egy PC, amelyen **Windows 11** vagy egy támogatott **Linux** disztribúció (Ubuntu 24.04+, Fedora, Debian) fut
- **16 GB RAM** ajánlott az 1–7. lépésekben használt futásidejű modellhez (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** ajánlott, ha a 6. lépésben szereplő nagyobb kódgeneráló modellt (`Qwen3.5-35B-A3B-GGUF`, ~20 GB) szeretné használni.
- **~4–30 GB szabad lemezterület**, a letöltött modellektől függően. Az útmutatóban szereplő legnagyobb modell körülbelül 20 GB.
- **Python 3.10–3.13** (a Python alkalmazás szakaszban kerül felhasználásra)
- Internetkapcsolat (vezetékes vagy vezeték nélküli)
<!-- @device:halo_box,halo,stx,krk -->
- [Opcionális] Egy AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 sorozat vagy Z2 Extreme), a legújabb, [Ryzen AI Software telepítési útmutatóból](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) telepített illesztőprogrammal, ha a modellt az NPU-n szeretné futtatni.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

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
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
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

## Alapfogalmak — Hogyan működnek a helyi AI szerverek

Mielőtt futtatnánk egy modellt, érdemes megérteni, *miért* van így felépítve minden. A Lemonade egy **helyi modellszerver**, azaz egy olyan folyamat, amely betölti az AI modelleket a memóriába, és HTTP-n keresztül elérhetővé teszi őket az alkalmazások számára, pontosan úgy, ahogy egy felhőalapú AI szolgáltatás is tenné.

### Miért szerver?

| Előny | Mit jelent ez Önnek |
|---------|----------------------|
| **Egyszerűsített integráció** | Az alkalmazások egyetlen HTTP API-val kommunikálnak, ahelyett hogy hardverspecifikus C++ vagy Python könyvtárakkal kellene foglalkozniuk. |
| **Megosztott modellek** | Egyetlen betöltött modell egyszerre több alkalmazást is kiszolgálhat, így nincs szükség duplikált másolatokra, amelyek feleslegesen foglalják a RAM-ot. |
| **Felhőből helyi környezetbe való hordozhatóság** | Az OpenAI felhőalapú API-jához írt kód a Lemonade-del is működik, mindössze egyetlen URL megváltoztatásával. |
| **Feladatok szétválasztása** | A modellkezelést, a streamelést és a hibatűrést a szerver kezeli, így a fejlesztők az alkalmazásukra koncentrálhatnak. |

### Az OpenAI API szabvány

A Lemonade az **OpenAI API**-t valósítja meg, ugyanazt az interfészt, amelyet a ChatGPT, az Azure OpenAI és számos más szolgáltatás is használ. A beszélgetési modell egyszerű:

| Szerepkör | Ki beszél |
|------|---------------|
| **system** | Utasítások a modell számára (személyiség, korlátozások, elérhető eszközök) |
| **user** | Az embertől (vagy alkalmazástól) a modellnek küldött üzenetek |
| **assistant** | A modell által generált válaszok |

Ez azt jelenti, hogy bármely könyvtár vagy alkalmazás, amely támogatja az OpenAI-t, kommunikálhat a Lemonade-del, ha a `http://localhost:13305/api/v1` címre irányítja, miközben a Lemonade Server fut.

## Fő tevékenység — Az első helyi AI beszélgetése

Töltsünk le egy LLM-et, és beszélgessünk vele, miközben az AI teljes egészében a saját gépünkön fut.

### 1. lépés: Modell letöltése és futtatása

A Lemonade egy válogatott modellkönyvtárral érkezik. Kezdjük a **Gemma-4-E2B-it** modellel, amely egy képes és kompakt modell, amely tartalmaz látástámogatást is. Nyisson meg egy terminált, és futtassa a következőt:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Ez az egyetlen parancs három dolgot végez el:

1. **Letölti** a modellt (~3 GB) a Hugging Face-ről, ha még nincs letöltve. (Eltarthat egy ideig)
2. **Elindítja** a Lemonade Server folyamatot a 13305-ös porton.
3. **Megnyitja a Lemonade App**-ot, hogy azonnal beszélgethessen a modellel.


<!-- @os:windows -->
Windows rendszeren a Lemonade App automatikusan elindul, és azonnal elkezdhet beszélgetni. Ha a `minimal.msi` csomagot telepítette, az alkalmazás nem szerepel benne. A beszélgetés elindításához nyissa meg a webböngészőjét, és keresse fel a `http://localhost:13305` címet.
<!-- @os:end -->

<!-- @os:linux -->
Linux rendszeren nyissa meg a böngészőjét, és navigáljon a `http://localhost:13305` címre a webes alkalmazás eléréséhez.
<!-- @os:end -->

Próbáljon meg beírni egy kérdést:

```
What are three fun facts about lemons?
```

A modell közvetlenül a beszélgetőablakban fog válaszolni. **Gratulálunk! Éppen egy nagy nyelvi modellt futtat helyben.**

![Lemonade App naplókkal megjelenítve](../../dependencies/assets/ChatwithLogs.png)

A Lemonade App Server Logs paneljén megtalálhatja a modell teljesítményére vonatkozó telemetriai adatokat minden egyes válasz után. Például:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### 2. lépés: Fedezze fel a webes felületet és a különböző moduladitásokat

A Lemonade tartalmaz egy beépített webes felületet, ahol a következőket teheti:

- **Interakció** a betöltött modellel egy ismerős chat ablakban
- **Modellek böngészése** a Model Manager fülön
- **Új modellek letöltése** egy kattintással

Próbálja ki a különböző modalitások közötti váltást a webes felület **Model Manager** fülén, ahol a modelleket Recipe vagy Category szerint böngészheti:

1. **Vision:** A már betöltött `Gemma-4-E2B-it-GGUF` modell támogatja a vizuális bemenetet. Illesszen be egy képet a chat ablakba, és kérje meg a modellt, hogy írja le azt.
2. **Image generation:** Az Image kategóriában töltsön le egy képgeneráló modellt, például `SDXL-Turbo`, a Model Managerből, majd használja a Lemonade Image Generatort egy prompt beírásához és egy kép helyi generálásához.
3. **Audio:** Az Audio kategóriában töltsön le egy hangmodellt, például `Whisper-Tiny`-t, amely beszédet tud szöveggé alakítani. Adjon meg egy hangfelvételt a helyi átiratkészítéshez. Szöveg-beszéd átalakításhoz próbálja ki a Speech kategória valamelyik modelljét, például a `kokoro-v1`-et.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### 3. lépés: Próbáljon ki egy modellt egy másik háttérrendszerrel

Ha az egérrel a Lemonade App egy modellje fölé viszi a kurzort, egy fogaskerék ikont fog látni. Erre kattintva kiválaszthatja a modell beállításait, beleértve a kívánt háttérrendszer kiválasztását is.

Alapértelmezés szerint a Lemonade a Vulkan-t használja a GPU-gyorsításhoz. Ha rendelkezik támogatott AMD különálló GPU-val, átválthat ROCm-re.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

A telepített háttérrendszerek kezeléséhez kattintson a legbaloldalibb oszlopban található háttérrendszer gombra.

Alternatív megoldásként a háttérrendszert a következő paranccsal is megadhatja:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Az alapértelmezett háttérrendszert a `LEMONADE_LLAMACPP` környezeti változóval is beállíthatja, a következő értékekkel: `vulkan`, `rocm` vagy `cpu`.

---

## Mélyebbre ásva — Építsünk egy AI-alapú alkalmazást Pythonban

A helyi AI szerver igazi ereje abban rejlik, hogy bármilyen alkalmazás mindössze néhány sornyi kóddal csatlakozhat hozzá. Ennek bizonyítására építsünk egy kicsi, de működőképes **tanulókártya-generátort**, amelynek megadunk egy témát, az legenerálja a kártyákat, majd interaktívan kikérdezhetjük magunkat velük.

### 4. lépés: Indítsa el a szervert

Ellenőrizze, hogy fut-e a Lemonade szerver. A telepítés után jellemzően automatikusan elindul a háttérben. Az ellenőrzéshez futtassa:

```
lemonade status
```

Egy ehhez hasonló üzenetet kell látnia: `Server is running on port 13305`.

Ha a szerver nem fut, indítsa el a Lemonade alkalmazás megnyitásával. Használja az alapértelmezett **13305**-ös portot (ezt megerősítheti vagy kiválaszthatja a tálcaikonból).

### 5. lépés: Telepítse az OpenAI Python klienst

Egy terminálban hozzon létre egy venv-et, és telepítse az OpenAI Python klienst a következő parancsokkal:
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

### 6. lépés: Építse meg a tanulókártya-alkalmazást

Töltsünk le egy másik modellt kódgenerálásra: `Qwen3.5-35B-A3B-GGUF`. Ez egy nagy (~20 GB) és teljesítményes modell, amely leginkább 32 GB+ RAM-mal rendelkező rendszereknek felel meg. Ha kevesebb RAM áll rendelkezésre, próbálja inkább a `Qwen3.5-9B-GGUF`-ot (~6 GB).

Letöltheti a felhasználói felületről, vagy futtassa a következőt:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Adja meg a következő promptot a Lemonade Chat UI-nak, hogy egy egyszerű Flashcard alkalmazáshoz generáljon kódot.

A Qwen3.5-35B-A3B-GGUF-ot (egy nagyobb modell, amely jobb a kódírásban) fogjuk használni a Python alkalmazásunk generálásához, és maga az alkalmazás futásidőben a Gemma-4-E2B-it-GGUF-ot (a már letöltött kisebb modellt) fogja hívni. A kód ezután átmásolható egy tetszőleges fájlba, amit Pythonban futtathatunk.

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

> **Tipp**: Alapos prompt-tervezéssel és kétmodelles rendszer alkalmazásával a szokásos mérnöki gyakorlatokat követtük, az erőforrások és a sebesség optimalizálása érdekében.

Kényelme érdekében biztosítottunk egy minta kimenetet a [`flashcards.py`](assets/flashcards.py) fájlban. Bátran töltse le a saját könyvtárába. Bármelyik esetben is, most már rendelkeznie kell egy futtatható Python fájllal.

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


### 7. lépés: Futtassa a generált kódot

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Ezt kell látnia:**

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

Mindössze körülbelül 150 sornyi kóddal egy teljesen működőképes, helyi LLM által működtetett tanulóeszközt építettünk. Nincs kezelendő API-kulcs, nincs használati költség, és semmilyen adat nem hagyja el a gépét.

> **Fontos meglátás:** Figyelje meg, hogy a `client = OpenAI(base_url=...) ` sor az *egyetlen* dolog, amely ezt az alkalmazást a Lemonade-hez köti az OpenAI felhője helyett. A kód többi része megegyezik azzal, amit bármely OpenAI-kompatibilis szolgáltatás ellen írna. Ha valaha használta az OpenAI Python könyvtárat, már tudja, hogyan kell alkalmazásokat építeni a Lemonade-del.

### Mit mutat be ez

Ez a kis alkalmazás számos valós integrációs mintát mutat be:

| Minta | Hol jelenik meg |
|---------|-----------------|
| **System promptok** | A `"system"` üzenet utasítja az LLM-et, hogy strukturált JSON-t adjon ki |
| **Strukturált kimenet** | Az alkalmazás JSON-ként elemzi az LLM válaszát a tanulókártyák felépítéséhez |
| **Állapotmentes kérések** | Minden egyes `generate_flashcards()` hívás független |
| **Hibakezelés** | A `try/except` elegánsan kezeli azokat az eseteket, amikor az LLM kimenete nem érvényes JSON |

Ugyanezek a minták bármilyen alkalmazásra skálázhatók, mint például chatbotokra, kódasszisztensekre, tartalomgenerátorokra, automatizálási eszközökre.

#### Bónusz kihívás

* Extra kihívásként próbálja meg úgy frissíteni az alkalmazást, hogy a tanulókártyákat felolvassa a felhasználónak, az [itt](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) megadott példa alapján.

---

<!-- @device:halo_box,halo,stx,krk -->
# Modellek futtatása az NPU-n (opcionális)

Ha Ryzen AI 300/400/Max 300 sorozatú vagy Z2 Extreme eszközzel rendelkezik, az eszközében beépített **Neurális Feldolgozó Egység (NPU)** található, amely kifejezetten AI munkaterhelésekhez tervezett dedikált chip. A modellek NPU-n történő futtatása energiahatékonyabb, mint a GPU használata, ami ideálissá teszi háttérben futó AI feladatokhoz, hosszabb munkamenetekhez és akkumulátoros használathoz.

A Lemonade háromféle NPU futtatási módot támogat, amelyek mindegyike ugyanazon OpenAI API mögött, átláthatóan működik:

| Mód | Működés | Recept | Példa modellek |
|------|-------------|--------|----------------|
| **Hibrid (NPU + iGPU)** | Az NPU dolgozza fel a promptot, az iGPU generálja a tokeneket | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Csak NPU** | A teljes következtetés az NPU-n fut | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | A FastFlowLM motort használja az NPU-n, az AMD XDNA2-re optimalizálva | FLM (`flm`) | qwen3.5-4b-FLM |

### Követelmények

- **AMD Ryzen AI 300/400 sorozatú vagy Z2 sorozatú** processzor
- **FLM** modellekhez: Az FLM futtatókörnyezet telepíthető a Lemonade alkalmazáson belülről, vagy a Lemonade automatikusan telepíti az FLM futtatókörnyezetet egy FLM modell futtatásakor. A FastFlowLM-ről bővebben [itt](https://fastflowlm.com/docs/) olvashat.


### 8. lépés: Hibrid modell futtatása

A hibrid modellek megosztják a munkát az NPU és az iGPU között, ezáltal jó egyensúlyt biztosítanak a sebesség és a hatékonyság között. A Lemonade alkalmazásban válasszon egy modellt a `Ryzen AI LLM` listából, például a `Qwen3-4B-Hybrid` modellt, vagy futtassa a következő paranccsal:

```
lemonade run Qwen3-4B-Hybrid
```

A Lemonade automatikusan felismeri az NPU-t, és telepíti a **Ryzen AI LLM** háttérrendszert.

> **Mi történik a háttérben?** Amikor üzenetet küld, az NPU párhuzamosan dolgozza fel a teljes promptot (ezt nevezik „prefill”-nek, azaz előtöltésnek). Ezután az iGPU veszi át a feladatot, és tokenenként generálja a választ (ezt nevezik „decode”-nak, azaz dekódolásnak). Ez a hibrid megközelítés mindkét chip erősségeit kihasználja.

### 9. lépés: FLM modell futtatása

A FastFlowLM (FLM) modellek kifejezetten az AMD XDNA2 NPU architektúrájára vannak optimalizálva, és méretükhöz képest nagyon gyorsak lehetnek. Válassza például a `qwen3.5-4b-FLM` modellt a `FastFlowLM NPU` listából, vagy használja a következő parancsot:

<!-- @os:windows -->
A `FastFlowLM` engedélyezése Windows rendszeren:

* Nyissa meg a `Backends Manager` menüt.
* Keresse meg a `FastFlowLM NPU` háttérrendszer-kategóriát.
* Kattintson az Install NPU gombra.
* A telepítés befejezése után körülbelül 36 alapértelmezett modell lesz elérhető az FFLM legördülő menüben.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Amikor a `Lemonade` alkalmazást először indítja el, a `FastFlowNPU` háttérrendszer alapértelmezés szerint nincs engedélyezve.
A helyi alkalmazás megnyitja a telepítési oldalt, hogy végigvezesse a beállításon.

A `FastFlowLM` engedélyezése Linux rendszeren:

* Nyissa meg a `Lemonade` alkalmazást.
* Látogasson el a [hivatalos FLM](https://lemonade-server.ai/flm_npu_linux.html) dokumentációhoz, és kövesse az FLM telepítési lépéseit a Linux disztribúciójának kiválasztásával.
* Engedélyezze a backportokat a telepítési oldalon leírtak szerint.
* Töltse le a legújabb `v0.9.x` kiadást a [tags oldalról](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Az AMD Halo Developer Platform esetén ügyeljen arra, hogy a Debian 13 verziót válassza.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Telepítse a letöltött `.deb` csomagot.
* Javasolt: Lépjen ki a `Lemonade App` alkalmazásból, majd nyissa meg újra, hogy a változások érzékelhetők legyenek.
* Javasolt: Nyissa meg a `Backends Manager` menüt, és kattintson a `FastFlowNPU` háttérrendszer telepítésére.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Sikeres telepítés után látnia kell, hogy az `flm:npu` befejeződött a **Lemonade Desktop App** **Download Manager** (Letöltéskezelő) részében.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Ezután kiválaszthatja bármelyik elérhető FFLM modellt, és elkezdheti használni az NPU háttérrendszert.

Adott modell esetén töltse le a kívánt modellt a [modellek oldaláról](https://fastflowlm.com/docs/models/qwen/), és ellenőrizze azt a dokumentációban megadott Shell paranccsal.
```
flm run qwen3.5-4b-FLM
```
vagy 
```
lemonade run qwen3.5-4b-FLM
```
 segítségével
Az FLM modellek a legnépszerűbb architektúrák némelyikét tartalmazzák (Gemma 3, Qwen 3, Llama 3 és DeepSeek R1), méretük pedig 1 GB alattitól egészen 13 GB felettiig terjed.
A Lemonade automatikusan felismeri az NPU-t, és telepíti a **FastFlowLM NPU** háttérrendszert.

<!-- @os:windows -->
> **Tipp:** A legjobb NPU teljesítmény érdekében engedélyezze a turbó módot:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Modellek váltása

A 6. lépésben szereplő tanulókártya-alkalmazás NPU modellekkel is működik, csak cserélje ki a modell nevét:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Következő lépések

Most már van egy saját hardverén futó helyi AI szerver, íme, hogyan folytathatja:

1. **Csatlakoztassa kedvenc alkalmazásait**: A Lemonade dobozból is működik a [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), az [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), a [Continue](https://lemonade-server.ai/docs/server/apps/continue/), az [n8n](https://n8n.io/integrations/lemonade-model/) és [még sok más](https://lemonade-server.ai/marketplace) alkalmazással.

2. **Böngésszen több modell között**: Fedezze fel a teljes [modellkönyvtárat](https://lemonade-server.ai/docs/server/server_models/), hogy kódoláshoz, következtetéshez, látáshoz és egyéb feladatokhoz optimalizált modelleket találjon. Használja a Lemonade alkalmazást vagy a `lemonade list` parancsot az elérhető modellek megtekintéséhez.

3. **Oldja fel a ROCm GPU gyorsítást**: Ha támogatott AMD GPU-val rendelkezik, váltson a ROCm háttérrendszerre: `lemonade config set llamacpp.backend=rocm`. Lásd a [támogatott AMD GPU-kat](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Olvassa el a teljes API specifikációt**: A Lemonade támogatja a csevegés-kiegészítéseket, beágyazásokat, hangátiratkészítést, képgenerálást, szöveg-hang átalakítást és egyebeket. Az összes végpontot lásd a [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) dokumentumban.

5. **Járuljon hozzá**: A Lemonade nyílt forráskódú. Nézze meg a [hozzájárulási útmutatót](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md), és keresse a [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) címkéjű bejegyzéseket.

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