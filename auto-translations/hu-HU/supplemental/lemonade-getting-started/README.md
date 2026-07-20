<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ez a playbook olyan speciális címkéket használ, amelyeket a GitHub nem tud megjeleníteni. A tartalom helyes előnézetéhez látogasson el a [amd.com/playbooks](https://amd.com/playbooks) oldalra.
<!-- @github-only:end -->

## Áttekintés

🍋 A **Lemonade** egy nyílt forráskódú, helyi AI szerver, amellyel nagy nyelvi modelleket (LLM-eket), képgenerátorokat és hangmodelleket futtathat közvetlenül a saját hardverén. A modelleket az iparági szabványnak számító **OpenAI API**-n keresztül teszi elérhetővé, így minden alkalmazás, amely az OpenAI-jal működik, azonnal együtt tud működni a Lemonade-del is. A playbook végére a Lemonade-et fogja használni modellek helyi futtatására a gépén.

## Amit meg fog tanulni

Ennek a playbooknak a végére képes lesz:

* **Telepíteni a Lemonade Servert**, és ellenőrizni, hogy fut-e.
* **Letölteni egy LLM-et, és beszélgetni vele** egyetlen paranccsal.
* **Felfedezni a webes felhasználói felületet**, és kipróbálni különböző módozatokat, például a látást, a beszédfelismerést és a képgenerálást.
* **Váltani a GPU háttérrendszerek** között Vulkan és AMD ROCm™ szoftver között.
* **Egy Python alkalmazást építeni**, amelyet egy helyi LLM hajt meg, az OpenAI-kompatibilis API segítségével.
<!-- @device:halo_box,halo,stx,krk -->
* **Modelleket futtatni az AMD Neural Processing Unit (NPU) egységen** Hybrid és FLM végrehajtási módok használatával AMD Ryzen™ AI hardveren.
<!-- @device:end -->

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftveres előfeltételek telepítése

Mielőtt elkezdené, győződjön meg arról, hogy rendelkezik a következőkkel:

- Egy **Windows 11**-et vagy egy támogatott **Linux**-disztribúciót (Ubuntu 24.04+, Fedora, Debian) futtató számítógép
- **16 GB RAM** ajánlott az 1–7. lépésben használt futtatási modellhez (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** ajánlott, ha a 6. lépésben szereplő nagyobb kódgeneráló modellt (`Qwen3.5-35B-A3B-GGUF`, ~20 GB) szeretné használni.
- **~4–30 GB szabad lemezterület**, a letöltött modellektől függően. Az útmutatóban szereplő legnagyobb modell körülbelül 20 GB.
- **Python 3.10–3.13** (a Python alkalmazás szakaszban használva)
- Internetkapcsolat (vezetékes vagy vezeték nélküli)
<!-- @device:halo_box,halo,stx,krk -->
- [Opcionális] Egy AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 sorozat vagy Z2 Extreme) a legújabb, a [Ryzen AI szoftver telepítési útmutatójából](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) telepített illesztőprogrammal, ha modellt szeretne futtatni az NPU-n.
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

Mielőtt futtatnánk egy modellt, érdemes megérteni, *miért* van így beállítva a rendszer. A Lemonade egy **helyi modellszerver**, azaz egy olyan folyamat, amely AI modelleket tölt be a memóriába, és HTTP-n keresztül teszi elérhetővé őket az alkalmazások számára, akárcsak egy felhőalapú AI-szolgáltatás.

### Miért szerver?

| Előny | Mit jelent ez az Ön számára |
|---------|----------------------|
| **Egyszerűsített integráció** | Az alkalmazások egyetlen HTTP API-val kommunikálnak, ahelyett, hogy hardverspecifikus C++ vagy Python könyvtárakkal kellene foglalkozniuk. |
| **Megosztott modellek** | Egyetlen betöltött modell egyszerre több alkalmazást is kiszolgálhat, nincs szükség duplikált másolatokra, amelyek feleslegesen foglalják a RAM-ot. |
| **Felhőből helyibe való hordozhatóság** | Az OpenAI felhőalapú API-jához írt kód a Lemonade-del is működik, csak egyetlen URL-t kell megváltoztatni. |
| **Feladatok szétválasztása** | A modellkezelést, a streamelést és a hibatűrést a szerver kezeli, így a fejlesztők az alkalmazásukra koncentrálhatnak. |

### Az OpenAI API szabvány

A Lemonade az **OpenAI API**-t valósítja meg, ugyanazt az interfészt, amelyet a ChatGPT, az Azure OpenAI és számos más szolgáltatás is használ. A beszélgetési modell egyszerű:

| Szerep | Ki beszél |
|------|---------------|
| **system** | Utasítások a modell számára (személyiség, korlátozások, elérhető eszközök) |
| **user** | Üzenetek az embertől (vagy alkalmazástól) a modell felé |
| **assistant** | A modell által generált válaszok |

Ez azt jelenti, hogy bármely könyvtár vagy alkalmazás, amely támogatja az OpenAI-t, kommunikálhat a Lemonade-del, ha a `http://localhost:13305/api/v1` címre mutat, miközben a Lemonade Server fut.

## Fő tevékenység — Az első helyi AI-beszélgetése

Töltsünk le egy LLM-et, és beszélgessünk vele, az AI-t teljes egészében a saját gépünkön futtatva.

### 1. lépés: Modell letöltése és futtatása

A Lemonade egy válogatott modellkönyvtárral érkezik. Kezdjük a **Gemma-4-E2B-it** modellel, amely egy kompakt, mégis nagy teljesítményű modell, és beépített képfelismerő (vision) támogatással rendelkezik. Nyisson meg egy terminált, és futtassa a következőt:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Ez az egyetlen parancs három dolgot tesz:

1. **Letölti** a modellt (~3 GB) a Hugging Face-ről, ha még nincs letöltve. (Eltarthat egy ideig)
2. **Elindítja** a Lemonade Server folyamatot a 13305-ös porton.
3. **Megnyitja a Lemonade Appot**, hogy azonnal beszélgethessen a modellel.


<!-- @os:windows -->
Windows rendszeren a Lemonade App automatikusan elindul, és azonnal elkezdhet beszélgetni. Ha a `minimal.msi` csomagot telepítette, az alkalmazás nincs benne. A beszélgetés megkezdéséhez nyissa meg a webböngészőjét, és keresse fel a `http://localhost:13305` címet.
<!-- @os:end -->

<!-- @os:linux -->
Linux rendszeren nyissa meg a böngészőjét, és navigáljon a `http://localhost:13305` címre a webalkalmazás eléréséhez.
<!-- @os:end -->

Próbáljon meg beírni egy kérdést:

```
What are three fun facts about lemons?
```

A modell közvetlenül a beszélgetőablakban fog válaszolni. **Gratulálunk! Egy nagy nyelvi modellt futtat helyben.**

![Lemonade App naplókkal megjelenítve](../../dependencies/assets/ChatwithLogs.png)

A Lemonade App Server Logs paneljén megtalálhatja a modell teljesítményére vonatkozó telemetriai adatokat minden válasz után. Például:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### 2. lépés: Fedezze fel a webes felületet és a különböző modalitásokat

A Lemonade beépített webes felülettel rendelkezik, amellyel:

- **Interakcióba léphet** a betöltött modellel egy jól ismert csevegőablakban
- **Böngészheti a modelleket** a Model Manager fülön
- **Új modelleket tölthet le** egy kattintással

Próbáljon meg váltani a különböző modalitások között a webes felület **Model Manager** fülén, ahol a modelleket Recipe vagy Category szerint böngészheti:

1. **Vizuális feldolgozás:** A már betöltött `Gemma-4-E2B-it-GGUF` modell támogatja a képi bemenetet. Illesszen be egy képet a csevegőmezőbe, és kérje meg a modellt, hogy írja le azt.
2. **Képgenerálás:** Az Image kategóriában töltsön le egy képmodellt, például az `SDXL-Turbo` modellt a Model Managerből, majd használja a Lemonade Image Generatort egy prompt beírásához és a kép helyi generálásához.
3. **Hang:** Az Audio kategóriában töltsön le egy hangmodellt, például a `Whisper-Tiny` modellt, amely képes beszéd szöveggé alakítására. Adjon meg egy hangfelvételt a helyi átírásához. Szöveg hanggá alakításához próbáljon ki egy modellt a Speech kategóriából, például a `kokoro-v1` modellt.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### 3. lépés: Próbáljon ki egy modellt egy másik háttérrendszerrel

Ha az egérmutatót egy modell fölé viszi a Lemonade alkalmazásban, megjelenik egy fogaskerék ikon. Erre kattintva kiválaszthatja a modell beállításait, beleértve a kívánt háttérrendszer kiválasztását is.

Alapértelmezés szerint a Lemonade a Vulkan technológiát használja a GPU-gyorsításhoz. Ha támogatott AMD diszkrét GPU-val rendelkezik, átválthat a ROCm-re.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

A telepített háttérrendszerek kezeléséhez kattintson a legbaloldalibb oszlopban található háttérrendszer gombra.

Alternatív megoldásként a háttérrendszert a következő paranccsal is megadhatja:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Az alapértelmezett háttérrendszert a `LEMONADE_LLAMACPP` környezeti változó segítségével is beállíthatja a következő értékekkel: `vulkan`, `rocm` vagy `cpu`.

---

## Mélyebbre ásva — Építsünk AI-alapú alkalmazást Python nyelven

A helyi AI-kiszolgáló igazi ereje abban rejlik, hogy bármely alkalmazás csatlakozhat hozzá mindössze néhány sornyi kóddal. Ennek bizonyítására építsünk egy kicsi, de működőképes **tanulókártya-generátort**, amelynek megadunk egy témát, ő legenerálja a kártyákat, és interaktívan kikérdezheti magát velük.

### 4. lépés: Indítsa el a kiszolgálót

Ellenőrizze, hogy a Lemonade kiszolgáló fut-e. Jellemzően automatikusan elindul a háttérben a telepítés után. Az ellenőrzéshez futtassa:

```
lemonade status
```

A következőhöz hasonló üzenetet kell látnia: `Server is running on port 13305`.

Ha a kiszolgáló nem fut, indítsa el a Lemonade alkalmazás megnyitásával. Használja az alapértelmezett **13305**-ös portot (ezt megerősítheti vagy kiválaszthatja a tálcaikonból).

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

### 6. lépés: Építse fel a tanulókártya-alkalmazást

Töltsünk le egy másik modellt kódgeneráláshoz: `Qwen3.5-35B-A3B-GGUF`. Ez egy nagy (~20 GB) és nagy teljesítményű modell, amely leginkább 32 GB+ RAM-mal rendelkező rendszerekhez ajánlott. Ha kevesebb RAM áll rendelkezésére, próbálja ki inkább a `Qwen3.5-9B-GGUF` modellt (~6 GB).

Letöltheti a felhasználói felületről, vagy futtassa a következőt:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Adja meg a következő promptot a Lemonade Chat felületén, hogy kódot generáljon egy egyszerű Flashcard alkalmazáshoz.

A Qwen3.5-35B-A3B-GGUF modellt (egy nagyobb, kódírásban jobb modellt) fogjuk használni a Python alkalmazásunk generálásához, és maga az alkalmazás futásidőben a Gemma-4-E2B-it-GGUF modellt (a már letöltött kisebb modellt) fogja hívni. A kód ezután átmásolható egy Ön által választott fájlba, hogy Pythonban futtatható legyen.

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

> **Tipp**: A gondos prompt-tervezéssel és egy kétmodelles rendszer alkalmazásával a szabványos mérnöki gyakorlatot követtük az erőforrások és a sebesség optimalizálása érdekében.

Kényelme érdekében mintakimenetet biztosítottunk a [`flashcards.py`](assets/flashcards.py) fájlban. Nyugodtan töltse le a saját könyvtárába. Bármelyik esetben most már rendelkeznie kell egy futtatható Python fájllal.

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

**Íme, mit kell látnia:**

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

Mindössze körülbelül 150 sornyi kóddal egy teljesen működőképes tanulóeszközt épített, amelyet egy helyi LLM hajt meg. Nincs kezelendő API-kulcs, nincsenek használati költségek, és semmilyen adat nem hagyja el a gépét.

> **Fő tanulság:** Figyelje meg, hogy a `client = OpenAI(base_url=...) ` sor az *egyetlen* dolog, amely ezt az alkalmazást a Lemonade-hez köti az OpenAI felhője helyett. A kód többi része megegyezik azzal, amit bármely OpenAI-kompatibilis szolgáltatás esetén írna. Ha már használta az OpenAI Python könyvtárat, máris tudja, hogyan építsen alkalmazásokat a Lemonade segítségével.

### Mit demonstrál ez

Ez a kis alkalmazás számos valós integrációs mintát alkalmaz:

| Minta | Hol jelenik meg |
|---------|-----------------|
| **Rendszer promptok** | A `"system"` üzenet utasítja az LLM-et strukturált JSON kimenet generálására |
| **Strukturált kimenet** | Az alkalmazás JSON-ként elemzi az LLM válaszát a tanulókártyák létrehozásához |
| **Állapotmentes kérések** | Minden `generate_flashcards()` hívás önálló |
| **Hibakezelés** | A `try/except` szabályosan kezeli azokat az eseteket, amikor az LLM kimenete nem érvényes JSON |

Ezek a minták bármely alkalmazásra skálázhatók, mint például chatbotok, kódasszisztensek, tartalomgenerátorok, automatizálási eszközök.

#### Bónusz kihívás

* Extra kihívásként próbálja meg úgy módosítani az alkalmazást, hogy a tanulókártyákat felolvassa a felhasználónak, az [itt](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) elérhető példára hivatkozva.

---

<!-- @device:halo_box,halo,stx,krk -->
## Modellek futtatása NPU-n (opcionális)

Ha Ryzen AI 300/400/Max 300 sorozatú vagy Z2 Extreme készüléked van, az eszközöd rendelkezik egy beépített **Neurális Feldolgozó Egységgel (NPU)**, egy kifejezetten AI-terhelésekre tervezett dedikált chippel. A modellek NPU-n történő futtatása energiahatékonyabb, mint a GPU használata, ami ideálissá teszi háttérben futó AI-feladatokhoz, hosszabb munkamenetekhez és akkumulátoros használathoz.

A Lemonade háromféle NPU-végrehajtási módot támogat, amelyek mindegyike átlátszó módon, ugyanazon OpenAI API mögött érhető el:

| Mód | Működés | Recept | Példa modellek |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | Az NPU feldolgozza a promptot, az iGPU generálja a tokeneket | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Csak NPU** | A teljes következtetés az NPU-n fut | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | A FastFlowLM motort használja az NPU-n, optimalizálva az AMD XDNA2-höz | FLM (`flm`) | qwen3.5-4b-FLM |

### Követelmények

- **AMD Ryzen AI 300/400 sorozatú vagy Z2 sorozatú** processzor
- **FLM** modellekhez: Az FLM futtatókörnyezet telepíthető a Lemonade alkalmazáson belülről, vagy a Lemonade automatikusan telepíti az FLM futtatókörnyezetet FLM modell futtatásakor. A FastFlowLM-ről bővebben [itt](https://fastflowlm.com/docs/) olvashatsz.


### 8. lépés: Hybrid modell futtatása

A hibrid modellek megosztják a munkát az NPU és az iGPU között, így jó egyensúlyt biztosítanak a sebesség és a hatékonyság között. A Lemonade alkalmazásban válassz egy modellt a `Ryzen AI LLM` listából, például a `Qwen3-4B-Hybrid`-et, vagy futtasd a következő paranccsal:

```
lemonade run Qwen3-4B-Hybrid
```

A Lemonade automatikusan felismeri az NPU-t, és telepíti a **Ryzen AI LLM** háttérrendszert.

> **Mi történik a háttérben?** Amikor elküldesz egy üzenetet, az NPU párhuzamosan dolgozza fel a teljes promptot (ezt hívjuk "prefill"-nek). Ezután az iGPU veszi át a feladatot, és tokenenként generálja a választ (ezt hívjuk "decode"-nak). Ez a hibrid megközelítés kihasználja mindkét chip erősségeit.

### 9. lépés: FLM modell futtatása

A FastFlowLM (FLM) modellek kifejezetten az AMD XDNA2 NPU architektúrájára vannak optimalizálva, és méretükhöz képest nagyon gyorsak lehetnek. Például válaszd a `qwen3.5-4b-FLM` modellt a `FastFlowLM NPU` listából, vagy használd a következő parancsot:

<!-- @os:windows -->
A `FastFlowLM` engedélyezése Windows rendszeren:

* Nyisd meg a `Backends Manager` menüt.
* Keresd meg a `FastFlowLM NPU` háttérrendszer-kategóriát.
* Kattints az Install NPU gombra.
* A telepítés befejezése után körülbelül 36 alapértelmezett modell lesz elérhető az FFLM legördülő menüben.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Amikor a `Lemonade` alkalmazást először indítod el, a `FastFlowNPU` háttérrendszer alapértelmezetten nincs engedélyezve. 
A helyi alkalmazás megnyitja a telepítési oldalt, hogy végigvezessen a beállításon.

A `FastFlowLM` engedélyezése Linux rendszeren:

* Nyisd meg a `Lemonade` alkalmazást.
* Látogass el a [hivatalos FLM](https://lemonade-server.ai/flm_npu_linux.html) dokumentációhoz, és kövesd az FLM telepítési lépéseit a Linux disztribúciód kiválasztásával.
* Engedélyezd a backportokat a telepítési oldalon leírtak szerint.
* Töltsd le a legújabb `v0.9.x` kiadást a [tags oldalról](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Az AMD Halo Developer Platform esetén ügyelj arra, hogy a Debian 13-at válaszd.
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
* Ajánlott: Lépj ki a `Lemonade App`-ból, majd nyisd meg újra, hogy a változások érvényesüljenek.
* Ajánlott: Nyisd meg a `Backends Manager`-t, és kattints az `FastFlowNPU` Backend telepítésére.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Sikeres telepítés után a **Download Manager**-ben, a **Lemonade Desktop App**-on belül azt kell látnod, hogy az `flm:npu` befejeződött.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Ezután kiválaszthatod bármelyik elérhető FFLM modellt, és elkezdheted használni az NPU háttérrendszert.

Adott modellhez töltsd le a kívánt modellt a [modellek oldaláról](https://fastflowlm.com/docs/models/qwen/), és ellenőrizd a dokumentációban megadott Shell paranccsal.
```
flm run qwen3.5-4b-FLM
```
vagy 
```
lemonade run qwen3.5-4b-FLM
```
 segítségével
Az FLM modellek a legnépszerűbb architektúrák közül néhányat tartalmaznak (Gemma 3, Qwen 3, Llama 3 és DeepSeek R1), és méretük 1 GB alattitól 13 GB felettiig terjed.
A Lemonade automatikusan felismeri az NPU-t, és telepíti a **FastFlowLM NPU** háttérrendszert.

<!-- @os:windows -->
> **Tipp:** A legjobb NPU-teljesítmény érdekében engedélyezd a turbó módot:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Modellek váltása

A 6. lépésből származó memóriakártya-alkalmazás NPU modellekkel is működik, csak cseréld ki a modell nevét:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Következő lépések

Van egy helyi AI szervered, amely a saját hardveredet futtatja, íme, hogy merre tovább:

1. **Kösd össze kedvenc alkalmazásaiddal**: A Lemonade dobozból működik a [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), az [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), a [Continue](https://lemonade-server.ai/docs/server/apps/continue/), az [n8n](https://n8n.io/integrations/lemonade-model/) és [még sok más](https://lemonade-server.ai/marketplace) alkalmazással.

2. **Böngéssz több modellt**: Fedezd fel a teljes [modellkönyvtárat](https://lemonade-server.ai/docs/server/server_models/), hogy megtaláld a kódoláshoz, következtetéshez, látáshoz és egyéb feladatokhoz optimalizált modelleket. Használd a Lemonade alkalmazást vagy a `lemonade list` parancsot, hogy megnézd, mi érhető el.

3. **Oldd fel a ROCm GPU-gyorsítást**: Ha támogatott AMD GPU-val rendelkezel, válts a ROCm háttérrendszerre: `lemonade config set llamacpp.backend=rocm`. Lásd a [támogatott AMD GPU-kat](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Olvasd el a teljes API specifikációt**: A Lemonade támogatja a chat completions, beágyazások, audio átiratkészítés, képgenerálás, szövegfelolvasás és egyéb funkciókat. Nézd meg a [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) oldalt az összes végpontért.

5. **Járulj hozzá**: A Lemonade nyílt forráskódú. Nézd meg a [közreműködési útmutatót](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md), és keress [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) címkéjű feladatokat.