<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Přehled

🍋 **Lemonade** je open-source lokální AI server, který vám umožňuje spouštět velké jazykové modely (LLM), generátory obrázků a audio modely přímo na vašem vlastním hardwaru. Modely zpřístupňuje prostřednictvím standardního rozhraní **OpenAI API**, takže jakákoli aplikace, která funguje s OpenAI, může okamžitě fungovat i s Lemonade. Na konci tohoto playbooku budete používat Lemonade ke spouštění modelů lokálně na vašem počítači.

## Co se naučíte

Na konci tohoto playbooku budete schopni:

* **Nainstalovat Lemonade Server** a ověřit, že běží.
* **Stáhnout LLM a vést s ním konverzaci** pomocí jediného příkazu.
* **Prozkoumat webové uživatelské rozhraní** a vyzkoušet různé modality, jako je vidění, přepis řeči na text a generování obrázků.
* **Přepínat mezi GPU backendy** Vulkan a software AMD ROCm™.
* **Vytvořit Python aplikaci** poháněnou lokálním LLM pomocí rozhraní kompatibilního s OpenAI API.
<!-- @device:halo_box,halo,stx,krk -->
* **Spouštět modely na AMD Neural Processing Unit (NPU)** pomocí režimů běhu Hybrid a FLM na hardwaru AMD Ryzen™ AI.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Nastavení konfigurace paměti

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

Než začnete, ujistěte se, že máte:

- PC se systémem **Windows 11** nebo podporovanou distribucí **Linuxu** (Ubuntu 24.04+, Fedora, Debian)
- Pro runtime model používaný v krocích 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB) se doporučuje **16 GB RAM**. **32 GB+** se doporučuje, pokud chcete v kroku 6 použít větší model pro generování kódu (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB volného místa na disku**, v závislosti na modelech, které stáhnete. Největší model v tomto průvodci má přibližně 20 GB.
- **Python 3.10–3.13** (používaný v sekci o Python aplikaci)
- Internetové připojení (kabelové nebo bezdrátové)
<!-- @device:halo_box,halo,stx,krk -->
- [Volitelné] AMD XDNA 2 NPU (řada Ryzen AI 300/400/Max 300 nebo Z2 Extreme) s nejnovějším ovladačem nainstalovaným z [Pokynů k instalaci softwaru Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), pokud chcete spouštět model na NPU.
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

## Základní koncepty — Jak fungují lokální AI servery

Než spustíme model, stojí za to pochopit, *proč* je vše nastaveno tímto způsobem. Lemonade je **lokální server modelů**, proces, který načítá AI modely do paměti a zpřístupňuje je aplikacím přes HTTP, stejně jako by to dělala cloudová AI služba.

### Proč server?

| Výhoda | Co to pro vás znamená |
|---------|----------------------|
| **Zjednodušená integrace** | Aplikace komunikují s jedním HTTP API namísto práce s knihovnami C++ nebo Python specifickými pro hardware. |
| **Sdílené modely** | Jeden načtený model může obsluhovat více aplikací najednou, žádné duplicitní kopie zabírající vaši RAM. |
| **Přenositelnost z cloudu do lokálního prostředí** | Kód napsaný pro cloudové API OpenAI funguje s Lemonade po změně jedné URL. |
| **Oddělení odpovědností** | Správu modelů, streamování a odolnost proti chybám řeší server, takže se vývojáři mohou soustředit na svou aplikaci. |

### Standard OpenAI API

Lemonade implementuje **OpenAI API**, stejné rozhraní, jaké používá ChatGPT, Azure OpenAI a desítky dalších služeb. Model konverzace je jednoduchý:

| Role | Kdo mluví |
|------|---------------|
| **system** | Instrukce pro model (persona, omezení, dostupné nástroje) |
| **user** | Zprávy od člověka (nebo aplikace) směrem k modelu |
| **assistant** | Odpovědi generované modelem |

To znamená, že jakákoli knihovna nebo aplikace, která podporuje OpenAI, může komunikovat s Lemonade tak, že ji nasměrujete na `http://localhost:13305/api/v1`, zatímco Lemonade Server běží.

## Hlavní aktivita — Váš první lokální AI chat

Pojďme stáhnout LLM a vést s ním konverzaci, přičemž AI poběží zcela na vašem vlastním počítači.

### Krok 1: Stažení a spuštění modelu

Lemonade je dodáván s pečlivě vybranou knihovnou modelů. Začněme s **Gemma-4-E2B-it**, výkonným a kompaktním modelem, který zahrnuje podporu vidění. Otevřete terminál a spusťte:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Tento jediný příkaz provede tři věci:

1. **Stáhne** model (~3 GB) z Hugging Face, pokud ještě není stažen. (Může to chvíli trvat)
2. **Spustí** proces Lemonade Server na portu 13305.
3. **Otevře Lemonade App**, abyste mohli začít s modelem konverzovat.


<!-- @os:windows -->
Ve Windows se Lemonade App spustí automaticky a můžete okamžitě začít konverzovat. Pokud jste nainstalovali balíček `minimal.msi`, aplikace není součástí instalace. Pro zahájení konverzace otevřete webový prohlížeč a přejděte na `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
V Linuxu otevřete prohlížeč a přejděte na `http://localhost:13305`, abyste získali přístup k webové aplikaci.
<!-- @os:end -->

Zkuste napsat otázku:

```
What are three fun facts about lemons?
```

Model odpoví přímo v chatovacím okně. **Gratulujeme! Nyní spouštíte velký jazykový model lokálně.**

![Lemonade App se zobrazenými logy](../../dependencies/assets/ChatwithLogs.png)

V panelu Server Logs v aplikaci Lemonade App najdete po každé odpovědi telemetrická data o výkonu modelu. Například:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Krok 2: Prozkoumejte webové rozhraní a různé modality

Lemonade obsahuje integrované webové rozhraní, ve kterém můžete:

- **Komunikovat** s načteným modelem ve známém chatovacím okně
- **Procházet modely** na kartě Model Manager
- **Stahovat nové modely** jedním kliknutím

Zkuste přepínat mezi různými modalitami pomocí karty **Model Manager** ve webovém UI, kde můžete procházet modely podle Recipe nebo podle Category:

1. **Vize:** Model `Gemma-4-E2B-it-GGUF`, který již máte načtený, podporuje vizi. Vložte obrázek do chatovacího pole a požádejte model, aby ho popsal.
2. **Generování obrázků:** V kategorii Image stáhněte z Model Manageru model pro generování obrázků, například `SDXL-Turbo`, a poté pomocí Lemonade Image Generator zadejte prompt a vygenerujte obrázek lokálně.
3. **Audio:** V kategorii Audio stáhněte audio model, například `Whisper-Tiny`, který umí převádět řeč na text. Poskytněte nahrávku zvuku, abyste ji přepsali lokálně. Pro převod textu na řeč vyzkoušejte některý z modelů v kategorii Speech, například `kokoro-v1`.

![Multi-modalita s Lemonade](../../dependencies/assets/multi_modality.png)

### Krok 3: Vyzkoušejte model s jiným backendem

Pokud najedete myší na model v aplikaci Lemonade App, zobrazí se ikona ozubeného kola. Kliknutím na ni můžete vybrat možnosti pro daný model, včetně volby požadovaného backendu.

Lemonade standardně používá pro GPU akceleraci Vulkan. Pokud máte podporovanou samostatnou AMD GPU, můžete přepnout na ROCm.

![Výběr backendu v Lemonade](../../dependencies/assets/lemonademodeloptions.png)

Chcete-li spravovat nainstalované backendy, klikněte na tlačítko backendu v nejlevějším sloupci.

Backend můžete také zadat pomocí následujícího příkazu:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Výchozí backend můžete rovněž nastavit pomocí proměnné prostředí `LEMONADE_LLAMACPP` s hodnotami: `vulkan`, `rocm` nebo `cpu`.

---

## Jdeme dál — vytvoření aplikace s umělou inteligencí v Pythonu

Skutečná síla lokálního AI serveru spočívá v tom, že se k němu může připojit libovolná aplikace pomocí pouhých několika řádků kódu. Abychom to dokázali, pojďme vytvořit malou, ale funkční **generátor studijních kartiček**, kterému zadáte téma, on vygeneruje kartičky a vy si můžete interaktivně udělat kvíz.

### Krok 4: Spuštění serveru

Ověřte, že server Lemonade běží. Obvykle se po instalaci spustí automaticky na pozadí. Ověření provedete spuštěním:

```
lemonade status
```

Měli byste vidět zprávu podobnou této: `Server is running on port 13305`.

Pokud server neběží, spusťte ho otevřením aplikace Lemonade. Použijte výchozí port **13305** (můžete jej potvrdit nebo vybrat z ikony v systémové liště).

### Krok 5: Instalace OpenAI Python Client

V terminálu vytvořte venv a nainstalujte OpenAI Python Client pomocí následujících příkazů:
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

### Krok 6: Vytvoření aplikace s kartičkami

Stáhněme si jiný model pro generování kódu: `Qwen3.5-35B-A3B-GGUF`. Jedná se o velký (~20 GB) a výkonný model, který je nejvhodnější pro systémy s 32 GB+ RAM. Pokud máte k dispozici méně RAM, vyzkoušejte místo něj `Qwen3.5-9B-GGUF` (~6 GB).

Stáhnout jej můžete z UI nebo spuštěním následujícího příkazu:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Zadejte následující prompt do Lemonade Chat UI, abyste vygenerovali kód pro jednoduchou aplikaci s kartičkami.

Pro generování naší Python aplikace použijeme Qwen3.5-35B-A3B-GGUF (větší model, který lépe píše kód), přičemž samotná aplikace bude za běhu volat Gemma-4-E2B-it-GGUF (menší model, který už máte stažený). Kód pak můžete zkopírovat do souboru dle vlastního výběru, aby jej bylo možné spustit v Pythonu.

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

> **Tip**: Dodrželi jsme standardní inženýrské postupy díky pečlivé tvorbě promptu a použití dvoumodelového systému pro optimalizaci zdrojů a rychlosti.

Pro vaše pohodlí jsme poskytli ukázkový výstup v souboru [`flashcards.py`](assets/flashcards.py). Neváhejte si jej stáhnout do svého adresáře. Tak či onak byste nyní měli mít Python soubor, který lze spustit.

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


### Krok 7: Spuštění vygenerovaného kódu

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Zde je, co byste měli vidět:**

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

Přibližně ve 150 řádcích kódu jste vytvořili plně funkční studijní nástroj poháněný lokálním LLM. Není třeba spravovat žádný API klíč, nevznikají žádné náklady za používání a žádná data neopouštějí váš počítač.

> **Klíčový poznatek:** Všimněte si, že řádek `client = OpenAI(base_url=...)` je *jediná* věc, která tuto aplikaci váže na Lemonade místo na cloud OpenAI. Zbytek kódu je identický s tím, co byste napsali pro jakoukoli službu kompatibilní s OpenAI. Pokud jste někdy použili knihovnu OpenAI Python, už víte, jak vytvářet aplikace s Lemonade.

### Co to ukazuje

Tato malá aplikace demonstruje několik reálných integračních vzorů:

| Vzor | Kde se vyskytuje |
|---------|-----------------|
| **Systémové prompty** | Zpráva `"system"` říká LLM, aby vygeneroval strukturovaný JSON |
| **Strukturovaný výstup** | Aplikace parsuje odpověď LLM jako JSON, aby vytvořila kartičky |
| **Bezstavové požadavky** | Každé volání `generate_flashcards()` je nezávislé |
| **Ošetření chyb** | `try/except` elegantně ošetřuje případy, kdy výstup LLM není platný JSON |

Tyto stejné vzory se škálují na libovolnou aplikaci, například chatboty, asistenty pro psaní kódu, generátory obsahu, automatizační nástroje.

#### Bonusová výzva

* Pro dodatečnou výzvu zkuste aplikaci upravit tak, aby uživateli kartičky předčítala nahlas, přičemž vycházejte z příkladu uvedeného [zde](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Spouštění modelů na NPU (volitelné)

Pokud máte Ryzen AI 300/400/Max 300 series nebo Z2 Extreme, vaše zařízení obsahuje vestavěnou **Neural Processing Unit (NPU)**, specializovaný čip navržený speciálně pro AI workloady. Spouštění modelů na NPU je energeticky úspornější než použití GPU, což je ideální pro AI úlohy na pozadí, delší relace a provoz na baterii.

Lemonade podporuje tři režimy provádění na NPU, všechny transparentně dostupné přes stejné OpenAI API:

| Režim | Jak to funguje | Recipe | Příklady modelů |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU zpracovává prompt, iGPU generuje tokeny | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Pouze NPU** | Celá inference běží na NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Používá FastFlowLM engine na NPU, optimalizováno pro AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Požadavky

- Procesor **AMD Ryzen AI 300/400 series nebo Z2 series**
- Pro modely **FLM**: Runtime FLM lze nainstalovat přímo z aplikace Lemonade, nebo Lemonade automaticky nainstaluje runtime FLM při spuštění modelu FLM. Více informací o FastFlowLM naleznete [zde](https://fastflowlm.com/docs/).


### Krok 8: Spuštění hybridního modelu

Hybridní modely rozdělují práci mezi NPU a iGPU pro dobrou rovnováhu mezi rychlostí a efektivitou. V aplikaci Lemonade vyberte model ze seznamu `Ryzen AI LLM`, například `Qwen3-4B-Hybrid`, nebo jej spusťte pomocí následujícího příkazu:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade automaticky detekuje vaši NPU a nainstaluje backend **Ryzen AI LLM**.

> **Co se děje pod kapotou?** Když odešlete zprávu, NPU zpracuje celý váš prompt paralelně (tomu se říká „prefill"). Poté se ujme iGPU, která generuje odpověď po jednotlivých tokenech (tomu se říká „decode"). Tento hybridní přístup využívá silné stránky každého čipu.

### Krok 9: Spuštění modelu FLM

Modely FastFlowLM (FLM) jsou speciálně optimalizované pro architekturu NPU XDNA2 od AMD a vzhledem ke své velikosti mohou být velmi rychlé. Například vyberte `qwen3.5-4b-FLM` ze seznamu `FastFlowLM NPU` nebo použijte následující příkaz:

<!-- @os:windows -->
Pro aktivaci `FastFlowLM` ve Windows:

* Otevřete menu `Backends Manager`.
* Najděte kategorii backendu `FastFlowLM NPU`.
* Klikněte na Install NPU.
* Po dokončení instalace bude v rozbalovací nabídce FFLM dostupných ~36 výchozích modelů.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Při prvním spuštění aplikace `Lemonade` není backend `FastFlowNPU` ve výchozím nastavení povolen.
Místní aplikace otevře instalační stránku, která vás provede nastavením.

Pro aktivaci `FastFlowLM` v Linuxu:

* Otevřete aplikaci `Lemonade`.
* Navštivte [oficiální dokumentaci FLM](https://lemonade-server.ai/flm_npu_linux.html) a postupujte podle instalačních kroků pro FLM výběrem vaší linuxové distribuce.
* Povolte backports podle pokynů na instalační stránce.
* Stáhněte si nejnovější vydání `v0.9.x` ze [stránky s tagy](https://github.com/FastFlowLM/FastFlowLM/tags).

<!-- @device:halo_box -->
>[!Note]
Pro AMD Halo Developer Platform nezapomeňte zvolit Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Nainstalujte stažený balíček `.deb`.
* Doporučeno: Ukončete aplikaci `Lemonade App` a znovu ji otevřete, aby se změny projevily.
* Doporučeno: Otevřete `Backends Manager` a klikněte na Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Po úspěšné instalaci byste měli vidět, že `flm:npu` byl dokončen ve **Download Manager** uvnitř **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Poté můžete vybrat kterýkoliv z dostupných modelů FFLM a začít používat backend NPU.

Pro konkrétní model stáhněte požadovaný model ze [stránky s modely](https://fastflowlm.com/docs/models/qwen/) a ověřte jej pomocí příkazu Shell uvedeného v dokumentaci.
```
flm run qwen3.5-4b-FLM
```
nebo přes 
```
lemonade run qwen3.5-4b-FLM
```

Modely FLM zahrnují některé z nejpopulárnějších architektur (Gemma 3, Qwen 3, Llama 3 a DeepSeek R1) a pohybují se v rozmezí od méně než 1 GB do více než 13 GB.
Lemonade automaticky detekuje vaši NPU a nainstaluje backend **FastFlowLM NPU**.

<!-- @os:windows -->
> **Tip:** Pro nejlepší výkon NPU povolte turbo režim:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Přepínání modelů

Aplikace s kartičkami ze Kroku 6 funguje i s modely NPU, stačí jen změnit název modelu:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Další kroky

Nyní máte lokální AI server běžící na vlastním hardwaru, zde je návod, kam pokračovat dál:

1. **Propojte své oblíbené aplikace**: Lemonade funguje přímo bez dalšího nastavení s [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) a [mnoha dalšími](https://lemonade-server.ai/marketplace).

2. **Procházejte další modely**: Prozkoumejte celou [knihovnu modelů](https://lemonade-server.ai/docs/server/server_models/) a najděte modely optimalizované pro programování, uvažování, vizi a další. Použijte aplikaci Lemonade nebo `lemonade list` k zobrazení dostupných modelů.

3. **Odemkněte akceleraci ROCm GPU**: Pokud máte podporované AMD GPU, přepněte se na backend ROCm: `lemonade config set llamacpp.backend=rocm`. Viz [podporované AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Přečtěte si úplnou specifikaci API**: Lemonade podporuje chat completions, embeddings, přepis zvuku, generování obrázků, převod textu na řeč a další. Viz [specifikace serveru](https://lemonade-server.ai/docs/server/server_spec/) pro všechny koncové body.

5. **Přispějte**: Lemonade je open source. Podívejte se na [průvodce přispíváním](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) a vyhledejte [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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