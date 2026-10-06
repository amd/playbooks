<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad

🍋 **Lemonade** je open-source lokálny AI server, ktorý vám umožňuje spúšťať veľké jazykové modely (LLM), generátory obrázkov a audio modely priamo na vašom vlastnom hardvéri. Sprístupňuje modely prostredníctvom štandardného priemyselného rozhrania **OpenAI API**, takže akákoľvek aplikácia, ktorá funguje s OpenAI, môže okamžite fungovať aj s Lemonade. Na konci tohto príručka budete pomocou Lemonade spúšťať modely lokálne na svojom počítači.

## Čo sa naučíte

Na konci tejto príručky budete schopní:

* **Nainštalovať Lemonade Server** a overiť, že beží.
* **Stiahnuť a chatovať s LLM** pomocou jediného príkazu.
* **Preskúmať webové rozhranie** a vyskúšať rôzne modality, ako napríklad videnie, prevod reči na text a generovanie obrázkov.
* **Prepínať GPU backendy** medzi Vulkan a softvérom AMD ROCm™.
* **Vytvoriť Python aplikáciu** poháňanú lokálnym LLM pomocou rozhrania kompatibilného s OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Spúšťať modely na AMD Neural Processing Unit (NPU)** pomocou hybridného a FLM režimu vykonávania na hardvéri AMD Ryzen™ AI.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

Predtým, než začnete, uistite sa, že máte:

- PC so systémom **Windows 11** alebo podporovanou distribúciou **Linux** (Ubuntu 24.04+, Fedora, Debian)
- Odporúča sa **16 GB RAM** pre runtime model použitý v krokoch 1 – 7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** sa odporúča, ak chcete použiť väčší model na generovanie kódu v kroku 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4 – 30 GB voľného miesta na disku**, v závislosti od modelov, ktoré si stiahnete. Najväčší model v tomto návode má približne 20 GB.
- **Python 3.10 – 3.13** (používaný v časti o Python aplikácii)
- internetové pripojenie (káblové alebo bezdrôtové)
<!-- @device:halo_box,halo,stx,krk -->
- [Voliteľné] AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 série alebo Z2 Extreme) s nainštalovaným najnovším ovládačom z [Pokynov na inštaláciu softvéru Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), ak chcete spúšťať model na NPU.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade-models-gemma-4-e2b -->

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

## Základné koncepty — Ako fungujú lokálne AI servery

Predtým, než spustíme model, oplatí sa pochopiť, *prečo* je všetko nastavené týmto spôsobom. Lemonade je **lokálny model server**, proces, ktorý načíta AI modely do pamäte a sprístupňuje ich aplikáciám prostredníctvom HTTP, rovnako ako by to robila cloudová AI služba.

### Prečo server?

| Výhoda | Čo to pre vás znamená |
|---------|----------------------|
| **Zjednodušená integrácia** | Aplikácie komunikujú s jedným HTTP API namiesto riešenia hardvérovo špecifických C++ alebo Python knižníc. |
| **Zdieľané modely** | Jeden načítaný model môže obsluhovať viacero aplikácií naraz, bez duplicitných kópií zaberajúcich vašu RAM. |
| **Prenositeľnosť z cloudu na lokálne prostredie** | Kód napísaný pre cloudové API OpenAI funguje s Lemonade po zmene jednej URL adresy. |
| **Oddelenie zodpovedností** | Správu modelov, streamovanie a odolnosť voči chybám rieši server, aby sa vývojári mohli sústrediť na svoju aplikáciu. |

### Štandard OpenAI API

Lemonade implementuje **OpenAI API**, rovnaké rozhranie, aké používa ChatGPT, Azure OpenAI a desiatky ďalších služieb. Model konverzácie je jednoduchý:

| Rola | Kto hovorí |
|------|---------------|
| **system** | Pokyny pre model (persóna, obmedzenia, dostupné nástroje) |
| **user** | Správy od človeka (alebo aplikácie) smerom k modelu |
| **assistant** | Odpovede vygenerované modelom |

To znamená, že akákoľvek knižnica alebo aplikácia, ktorá podporuje OpenAI, môže komunikovať s Lemonade jednoduchým nasmerovaním na `http://localhost:13305/api/v1`, pokiaľ Lemonade Server beží.

## Hlavná aktivita — Váš prvý lokálny AI chat

Poďme si stiahnuť LLM a viesť s ním konverzáciu, pričom celá AI beží priamo na vašom vlastnom počítači.

### Krok 1: Stiahnutie a spustenie modelu

Lemonade sa dodáva s kurátorovanou knižnicou modelov. Začnime s modelom **Gemma-4-E2B-it**, schopným a kompaktným modelom, ktorý zahŕňa podporu videnia. Otvorte terminál a spustite:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Tento jediný príkaz robí tri veci:

1. **Stiahne** model (~3 GB) z Hugging Face, ak ešte nie je stiahnutý. (Môže to chvíľu trvať)
2. **Spustí** proces Lemonade Server na porte 13305.
3. **Otvorí Lemonade App**, aby ste mohli začať chatovať s modelom.


<!-- @os:windows -->
Na Windows sa aplikácia Lemonade App spustí automaticky a môžete okamžite začať chatovať. Ak ste nainštalovali balík `minimal.msi`, aplikácia nie je súčasťou. Ak chcete začať chatovať, otvorte webový prehliadač a prejdite na `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
Na Linuxe otvorte prehliadač a prejdite na `http://localhost:13305`, aby ste získali prístup k webovej aplikácii.
<!-- @os:end -->

Skúste napísať otázku:

```
What are three fun facts about lemons?
```

Model odpovie priamo v okne chatu. **Gratulujeme! Spúšťate veľký jazykový model lokálne.**

![Lemonade App so zobrazenými logmi](../../dependencies/assets/ChatwithLogs.png)

V paneli Server Logs v aplikácii Lemonade App nájdete telemetrické údaje o výkone modelu po každej odpovedi. Napríklad:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Krok 2: Preskúmajte webové rozhranie a rôzne modality

Lemonade obsahuje vstavané webové rozhranie, v ktorom môžete:

- **Komunikovať** s načítaným modelom v známom chatovacom okne
- **Prehliadať modely** na karte Model Manager
- **Sťahovať nové modely** jedným kliknutím

Skúste prepínať medzi rôznymi modalitami pomocou karty **Model Manager** vo webovom rozhraní, kde môžete prehliadať modely podľa receptu (Recipe) alebo kategórie (Category):

1. **Vízia:** Model `Gemma-4-E2B-it-GGUF`, ktorý už máte načítaný, podporuje víziu. Vložte obrázok do chatovacieho poľa a požiadajte model, aby ho opísal.
2. **Generovanie obrázkov:** V kategórii Image si z Model Manager stiahnite model na generovanie obrázkov, napríklad `SDXL-Turbo`, a potom použite Lemonade Image Generator na zadanie promptu a vygenerovanie obrázka lokálne.
3. **Zvuk:** V kategórii Audio si stiahnite zvukový model, napríklad `Whisper-Tiny`, ktorý dokáže prevádzať reč na text. Poskytnite nahrávku zvuku na jej lokálny prepis. Na prevod textu na reč vyskúšajte jeden z modelov v kategórii Speech, napríklad `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### Krok 3: Vyskúšajte model s iným backendom

Ak prejdete kurzorom nad model v aplikácii Lemonade, zobrazí sa ikona ozubeného kolieska. Kliknutím na ňu môžete vybrať možnosti pre daný model, vrátane výberu požadovaného backendu.

Lemonade štandardne používa pre GPU akceleráciu Vulkan. Ak máte podporovanú diskrétnu GPU od AMD, môžete prepnúť na ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

Na správu nainštalovaných backendov kliknite na tlačidlo backendu v najľavejšom stĺpci.

Alternatívne môžete zadať backend pomocou nasledujúceho príkazu:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Predvolený backend môžete nastaviť aj pomocou premennej prostredia `LEMONADE_LLAMACPP` s hodnotami: `vulkan`, `rocm` alebo `cpu`.

---

## Ďalej do hĺbky — Vytvorte si aplikáciu s AI v Pythone

Skutočná sila lokálneho AI servera spočíva v tom, že sa k nemu môže pripojiť akákoľvek aplikácia pomocou len niekoľkých riadkov kódu. Na dôkaz si vytvoríme malý, ale funkčný **generátor študijných kartičiek**, ktorému zadáte tému, on vygeneruje kartičky a vy sa môžete interaktívne skúšať.

### Krok 4: Spustite server

Overte, že server Lemonade beží. Zvyčajne sa po inštalácii spustí automaticky na pozadí. Na overenie spustite:

```
lemonade status
```

Mali by ste vidieť správu podobnú tejto: `Server is running on port 13305`.

Ak server nebeží, spustite ho otvorením aplikácie Lemonade. Použite predvolený port **13305** (môžete ho potvrdiť alebo vybrať z ikony v systémovej lište).

### Krok 5: Nainštalujte klienta OpenAI Python

V termináli vytvorte venv a nainštalujte klienta OpenAI Python pomocou nasledujúcich príkazov:
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

### Krok 6: Vytvorte aplikáciu s kartičkami

Stiahnime si iný model na generovanie kódu: `Qwen3.5-35B-A3B-GGUF`. Je to veľký (~20 GB) a výkonný model, ktorý je najvhodnejší pre systémy s 32 GB+ RAM. Ak máte k dispozícii menej RAM, vyskúšajte namiesto neho `Qwen3.5-9B-GGUF` (~6 GB).

Môžete si ho stiahnuť z používateľského rozhrania alebo spustiť nasledujúce:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Zadajte nasledujúci prompt do Lemonade Chat UI na vygenerovanie kódu pre jednoduchú aplikáciu s kartičkami.

Na vygenerovanie našej Python aplikácie použijeme Qwen3.5-35B-A3B-GGUF (väčší model, ktorý je lepší v písaní kódu), pričom samotná aplikácia bude počas behu volať Gemma-4-E2B-it-GGUF (menší model, ktorý ste si už stiahli). Kód potom môžete skopírovať do súboru podľa vlastného výberu, aby ste ho mohli spustiť v Pythone.

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

> **Tip**: Dodržali sme štandardné inžinierske postupy prostredníctvom dôkladnej tvorby promptu a použitím systému s dvoma modelmi na optimalizáciu zdrojov a rýchlosti.

Pre vaše pohodlie sme poskytli ukážkový výstup v súbore [`flashcards.py`](assets/flashcards.py). Môžete si ho voľne stiahnuť do svojho adresára. Tak či onak, teraz by ste mali mať Python súbor, ktorý je možné spustiť.

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


### Krok 7: Spustite vygenerovaný kód

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Tu je to, čo by ste mali vidieť:**

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

Približne v 150 riadkoch kódu ste vytvorili plne funkčný študijný nástroj poháňaný lokálnym LLM. Nemusíte spravovať žiadny API kľúč, nevznikajú žiadne náklady na používanie a žiadne dáta nikdy neopustia váš počítač.

> **Kľúčový poznatok:** Všimnite si, že riadok `client = OpenAI(base_url=...) ` je *jediná* vec, ktorá spája túto aplikáciu s Lemonade namiesto cloudu OpenAI. Zvyšok kódu je rovnaký, ako by ste napísali pre akúkoľvek službu kompatibilnú s OpenAI. Ak ste niekedy použili knižnicu OpenAI Python, už viete, ako stavať aplikácie s Lemonade.

### Čo to demonštruje

Táto malá aplikácia využíva niekoľko reálnych integračných vzorov:

| Vzor | Kde sa vyskytuje |
|---------|-----------------|
| **Systémové prompty** | Správa `"system"` inštruuje LLM, aby vygeneroval štruktúrovaný JSON |
| **Štruktúrovaný výstup** | Aplikácia analyzuje odpoveď LLM ako JSON na vytvorenie kartičiek |
| **Bezstavové požiadavky** | Každé volanie `generate_flashcards()` je nezávislé |
| **Spracovanie chýb** | `try/except` elegantne ošetrí prípady, keď výstup LLM nie je platný JSON |

Tieto rovnaké vzory sa dajú škálovať na akúkoľvek aplikáciu, ako sú chatboty, asistenti pre kód, generátory obsahu či automatizačné nástroje.

#### Bonusová výzva

* Pre dodatočnú výzvu skúste upraviť aplikáciu tak, aby boli kartičky používateľovi prečítané nahlas, pričom sa budete riadiť príkladom uvedeným [tu](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Spúšťanie modelov na NPU (voliteľné)

Ak vlastníte zariadenie radu Ryzen AI 300/400/Max 300 alebo Z2 Extreme, vaše zariadenie má zabudovanú **neurónovú spracovateľskú jednotku (NPU)**, vyhradený čip navrhnutý špeciálne pre AI úlohy. Spúšťanie modelov na NPU je energeticky efektívnejšie než používanie GPU, čo ho robí ideálnym pre úlohy AI na pozadí, dlhšie relácie a používanie na batériu.

Lemonade podporuje tri režimy vykonávania na NPU, všetky transparentné za rovnakým OpenAI API:

| Režim | Ako to funguje | Recept | Príklady modelov |
|------|-------------|--------|----------------|
| **Hybridný (NPU + iGPU)** | NPU spracováva výzvu, iGPU generuje tokeny | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Len NPU** | Celá inferencia beží na NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Používa FastFlowLM engine na NPU, optimalizovaný pre AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Požiadavky

- Procesor **AMD Ryzen AI radu 300/400 alebo Z2**
- Pre modely **FLM**: Runtime FLM je možné nainštalovať priamo v aplikácii Lemonade, prípadne ho Lemonade automaticky nainštaluje pri spustení modelu FLM. Viac informácií o FastFlowLM nájdete [tu](https://fastflowlm.com/docs/).


### Krok 8: Spustenie hybridného modelu

Hybridné modely rozdeľujú prácu medzi NPU a iGPU pre dobrú rovnováhu medzi rýchlosťou a efektivitou. V aplikácii Lemonade vyberte model zo zoznamu `Ryzen AI LLM`, napríklad `Qwen3-4B-Hybrid`, alebo ho spustite pomocou nasledujúceho príkazu:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade automaticky rozpozná vašu NPU a nainštaluje backend **Ryzen AI LLM**.

> **Čo sa deje v pozadí?** Keď odošlete správu, NPU spracuje celú vašu výzvu paralelne (tento proces sa nazýva „prefill“). Následne iGPU prevezme generovanie odpovede jeden token po druhom (tento proces sa nazýva „decode“). Tento hybridný prístup využíva silné stránky každého čipu.

### Krok 9: Spustenie modelu FLM

Modely FastFlowLM (FLM) sú špecificky optimalizované pre architektúru NPU AMD XDNA2 a vzhľadom na svoju veľkosť môžu byť veľmi rýchle. Napríklad vyberte `qwen3.5-4b-FLM` zo zoznamu `FastFlowLM NPU` alebo použite nasledujúci príkaz:

<!-- @os:windows -->
Pre povolenie `FastFlowLM` vo Windows:

* Otvorte menu `Backends Manager`.
* Nájdite kategóriu backendu `FastFlowLM NPU`.
* Kliknite na Install NPU.
* Po dokončení inštalácie bude dostupných ~36 predvolených modelov v rozbaľovacom menu FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Keď je aplikácia `Lemonade` spustená prvýkrát, backend `FastFlowNPU` nie je predvolene povolený.
Lokálna aplikácia otvorí inštalačnú stránku, ktorá vás prevedie nastavením.

Pre povolenie `FastFlowLM` v Linuxe:

* Otvorte aplikáciu `Lemonade`.
* Navštívte oficiálnu dokumentáciu [official FLM](https://lemonade-server.ai/flm_npu_linux.html) a postupujte podľa inštalačných krokov pre FLM výberom vašej distribúcie Linuxu.
* Povoľte backports podľa pokynov na inštalačnej stránke.
* Stiahnite si najnovšiu verziu `v0.9.x` zo [stránky s tagmi](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Pre AMD Halo Developer Platform sa uistite, že ste vybrali Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Nainštalujte stiahnutý balík `.deb`.
* Odporúčané: Ukončite aplikáciu `Lemonade App` a znovu ju otvorte, aby sa zmeny prejavili.
* Odporúčané: Otvorte `Backends Manager` a kliknite na Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Po úspešnej inštalácii by ste mali vidieť, že `flm:npu` je dokončené v **Download Manager** v aplikácii **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Následne môžete vybrať ktorýkoľvek z dostupných modelov FFLM a začať používať backend NPU.

Pre konkrétny model si stiahnite požadovaný model zo [stránky s modelmi](https://fastflowlm.com/docs/models/qwen/) a overte ho pomocou shell príkazu uvedeného v dokumentácii.
```
flm run qwen3.5-4b-FLM
```
alebo cez 
```
lemonade run qwen3.5-4b-FLM
```

Modely FLM zahŕňajú niektoré z najpopulárnejších architektúr (Gemma 3, Qwen 3, Llama 3 a DeepSeek R1) a ich veľkosť sa pohybuje od menej ako 1 GB do viac ako 13 GB.
Lemonade automaticky rozpozná vašu NPU a nainštaluje backend **FastFlowLM NPU**.

<!-- @os:windows -->
> **Tip:** Pre najlepší výkon NPU povoľte turbo režim:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Prepínanie modelov

Aplikácia na kartičky z Kroku 6 funguje aj s modelmi NPU, stačí zmeniť názov modelu:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Ďalšie kroky

Máte spustený lokálny AI server na vlastnom hardvéri, tu je návod, kam pokračovať ďalej:

1. **Prepojte svoje obľúbené aplikácie**: Lemonade funguje priamo po inštalácii s [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) a [mnohými ďalšími](https://lemonade-server.ai/marketplace).

2. **Preskúmajte ďalšie modely**: Prezrite si celú [knižnicu modelov](https://lemonade-server.ai/docs/server/server_models/) a nájdite modely optimalizované pre programovanie, uvažovanie, videnie a ďalšie. Použite aplikáciu Lemonade alebo `lemonade list` na zobrazenie dostupných možností.

3. **Odomknite akceleráciu GPU pomocou ROCm**: Ak vlastníte podporované GPU od AMD, prepnite na backend ROCm: `lemonade config set llamacpp.backend=rocm`. Pozrite si [podporované GPU od AMD](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Prečítajte si úplnú špecifikáciu API**: Lemonade podporuje chat completions, embeddings, prepis zvuku, generovanie obrázkov, prevod textu na reč a ďalšie. Pozrite si [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) pre všetky koncové body.

5. **Prispejte**: Lemonade je open source. Pozrite si [sprievodcu prispievaním](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) a vyhľadajte [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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