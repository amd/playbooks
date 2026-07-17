<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tento playbook používá speciální tagy, které GitHub nedokáže zobrazit. Pro správné zobrazení tohoto obsahu navštivte [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Přehled

🍋 **Lemonade** je open-source lokální AI server, který vám umožňuje spouštět velké jazykové modely (LLM), generátory obrázků a audio modely přímo na vašem vlastním hardwaru. Modely zpřístupňuje prostřednictvím průmyslově standardního **OpenAI API**, takže jakákoli aplikace, která funguje s OpenAI, může okamžitě fungovat i s Lemonade. Po dokončení tohoto playbooku budete používat Lemonade ke spouštění modelů lokálně na svém počítači.

## Co se naučíte

Po dokončení tohoto playbooku budete schopni:

* **Nainstalovat Lemonade Server** a ověřit, že běží.
* **Stáhnout LLM a chatovat s ním** pomocí jediného příkazu.
* **Prozkoumat webové rozhraní** a vyzkoušet různé modality, jako je rozpoznávání obrazu, převod řeči na text a generování obrázků.
* **Přepínat GPU backendy** mezi Vulkan a AMD ROCm™ softwarem.
* **Vytvořit Python aplikaci** poháněnou lokálním LLM pomocí OpenAI-kompatibilního API.
<!-- @device:halo_box,halo,stx,krk -->
* **Spouštět modely na AMD Neural Processing Unit (NPU)** pomocí režimů Hybrid a FLM na hardwaru AMD Ryzen™ AI.
<!-- @device:end -->

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

Než začnete, ujistěte se, že máte:

- PC s operačním systémem **Windows 11** nebo podporovanou distribucí **Linux** (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** je doporučeno pro runtime model používaný v krocích 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** je doporučeno, pokud chcete použít větší model pro generování kódu v kroku 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB volného místa na disku**, v závislosti na modelech, které stáhnete. Největší model v tomto průvodci má přibližně 20 GB.
- **Python 3.10–3.13** (používá se v části s Python aplikací)
- Připojení k internetu (kabelové nebo bezdrátové)
<!-- @device:halo_box,halo,stx,krk -->
- [Volitelné] AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 series nebo Z2 Extreme) s nejnovějším nainstalovaným ovladačem z [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), pokud chcete spustit model na NPU.
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

## Základní koncepty — Jak fungují lokální AI servery

Než spustíme model, je dobré pochopit, *proč* jsou věci nastaveny tímto způsobem. Lemonade je **lokální model server** — proces, který načítá AI modely do paměti a zpřístupňuje je aplikacím přes HTTP, stejně jako by to dělala cloudová AI služba.

### Proč server?

| Výhoda | Co to pro vás znamená |
|---------|----------------------|
| **Zjednodušená integrace** | Aplikace komunikují s jedním HTTP API místo toho, aby se musely vypořádat s hardwarově specifickými C++ nebo Python knihovnami. |
| **Sdílené modely** | Jeden načtený model může obsluhovat více aplikací najednou, bez duplicitních kopií, které by spotřebovávaly vaši RAM. |
| **Přenositelnost z cloudu na lokální prostředí** | Kód napsaný pro cloudové API OpenAI funguje s Lemonade po změně jediné URL. |
| **Oddělení zodpovědností** | Správu modelů, streamování a odolnost vůči chybám zajišťuje server, takže se vývojáři mohou soustředit na svou aplikaci. |

### Standard OpenAI API

Lemonade implementuje **OpenAI API** — stejné rozhraní, které používají ChatGPT, Azure OpenAI a desítky dalších služeb. Model konverzace je jednoduchý:

| Role | Kdo mluví |
|------|---------------|
| **system** | Instrukce pro model (persona, omezení, dostupné nástroje) |
| **user** | Zprávy od člověka (nebo aplikace) modelu |
| **assistant** | Odpovědi generované modelem |

To znamená, že jakákoli knihovna nebo aplikace, která podporuje OpenAI, může komunikovat s Lemonade tak, že ji nasměruje na `http://localhost:13305/api/v1`, zatímco Lemonade Server běží.

## Hlavní aktivita — Váš první lokální AI chat

Pojďme stáhnout LLM a vést s ním konverzaci, přičemž AI poběží zcela na vašem vlastním počítači.

### Krok 1: Stažení a spuštění modelu

Lemonade je dodáváno s kurátorskou knihovnou modelů. Začněme s **Gemma-4-E2B-it** — schopným a kompaktním modelem, který zahrnuje podporu rozpoznávání obrazu. Otevřete terminál a spusťte:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Tento jediný příkaz provede tři věci:

1. **Stáhne** model (~3 GB) z Hugging Face, pokud ještě není stažen. (Může chvíli trvat)
2. **Spustí** proces Lemonade Server na portu 13305.
3. **Otevře Lemonade App**, abyste mohli začít chatovat s modelem.


<!-- @os:windows -->
Ve Windows se Lemonade App spustí automaticky a můžete okamžitě začít chatovat. Pokud jste nainstalovali balíček `minimal.msi`, aplikace není součástí instalace. Chcete-li začít chatovat, otevřete webový prohlížeč a přejděte na `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
V Linuxu otevřete prohlížeč a přejděte na `http://localhost:13305` pro přístup k webové aplikaci.
<!-- @os:end -->

Zkuste napsat otázku:

```
What are three fun facts about lemons?
```

Model odpoví přímo v okně chatu. **Gratulujeme! Spouštíte velký jazykový model lokálně.**

![Lemonade App se zobrazenými logy](../../dependencies/assets/ChatwithLogs.png)

V podokně Server Logs v Lemonade App najdete telemetrická data o výkonu modelu po každé odpovědi. Například:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Krok 2: Prozkoumání webového rozhraní a různých modalit

Lemonade obsahuje vestavěné webové rozhraní, kde můžete:

- **Interagovat** s načteným modelem v známém okně chatu
- **Procházet modely** na záložce Model Manager
- **Stahovat nové modely** jedním kliknutím

Zkuste přepínat mezi různými modalitami pomocí záložky **Model Manager** ve webovém rozhraní, kde můžete procházet modely podle receptury nebo kategorie:

1. **Rozpoznávání obrazu:** Model `Gemma-4-E2B-it-GGUF`, který již máte načtený, podporuje rozpoznávání obrazu. Vložte obrázek do chatovacího pole a požádejte model, aby ho popsal.
2. **Generování obrázků:** V kategorii Image stáhněte model pro generování obrázků, například `SDXL-Turbo`, z Model Manageru, poté použijte Lemonade Image Generator k zadání promptu a lokálnímu generování obrázku.
3. **Audio:** V kategorii Audio stáhněte audio model, například `Whisper-Tiny`, který umí převod řeči na text. Poskytněte zvukovou nahrávku k lokálnímu přepisu. Pro převod textu na řeč vyzkoušejte jeden z modelů v kategorii Speech, například `kokoro-v1`.

![Více modalit s Lemonade](../../dependencies/assets/multi_modality.png)

### Krok 3: Vyzkoušení modelu s jiným backendem

Pokud najedete myší na model v Lemonade App, zobrazí se ikona ozubeného kola. Kliknutím na ni můžete vybrat možnosti pro daný model, včetně výběru požadovaného backendu.

Ve výchozím nastavení používá Lemonade Vulkan pro GPU akceleraci. Pokud máte podporovaný AMD diskrétní GPU, můžete přepnout na ROCm.

![Lemonade výběr backendu](../../dependencies/assets/lemonademodeloptions.png)

Pro správu nainstalovaných backendů klikněte na tlačítko backendu v levém sloupci.

Alternativně můžete backend specifikovat pomocí následujícího příkazu:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Výchozí backend můžete také nastavit pomocí proměnné prostředí `LEMONADE_LLAMACPP` s hodnotami: `vulkan`, `rocm` nebo `cpu`.

---

## Jdeme hlouběji — Vytvořte AI aplikaci v Pythonu

Skutečná síla lokálního AI serveru spočívá v tom, že se k němu může připojit jakákoli aplikace pomocí pouhých několika řádků kódu. Abychom to dokázali, vytvoříme malý, ale funkční **generátor studijních kartiček** — zadáte mu téma, vygeneruje kartičky a vy se můžete interaktivně zkoušet.

### Krok 4: Spuštění serveru

Ověřte, že Lemonade server běží. Po instalaci se obvykle spouští automaticky na pozadí. Pro ověření spusťte:

```
lemonade status
```

Měli byste vidět zprávu podobnou: `Server is running on port 13305`.

Pokud server neběží, spusťte ho otevřením aplikace Lemonade. Použijte výchozí port **13305** (můžete ho potvrdit nebo vybrat z ikony v systémové liště).

### Krok 5: Instalace OpenAI Python klienta

V terminálu vytvořte venv a nainstalujte OpenAI Python klienta pomocí následujících příkazů:
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

Stáhněme jiný model pro generování kódu: `Qwen3.5-35B-A3B-GGUF`. Jedná se o velký (~20 GB) a výkonný model, který je nejvhodnější pro systémy s 32 GB+ RAM. Pokud máte méně dostupné RAM, zkuste místo toho `Qwen3.5-9B-GGUF` (~6 GB).

Můžete ho stáhnout z rozhraní nebo spustit následující příkaz:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Zadejte následující prompt do Lemonade Chat UI pro vygenerování kódu jednoduché aplikace s kartičkami.

Použijeme Qwen3.5-35B-A3B-GGUF (větší model lépe vhodný pro psaní kódu) k vygenerování naší Python aplikace, a samotná aplikace bude za běhu volat Gemma-4-E2B-it-GGUF (menší model, který jste již stáhli). Kód pak lze zkopírovat do souboru dle vašeho výběru a spustit v Pythonu.

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

> **Tip**: Dodrželi jsme standardní inženýrské postupy prostřednictvím důkladného vytváření promptů a použitím systému dvou modelů pro optimalizaci zdrojů a rychlosti.

Pro vaše pohodlí jsme poskytli ukázkový výstup v souboru [`flashcards.py`](assets/flashcards.py). Neváhejte ho stáhnout do svého adresáře. V každém případě byste nyní měli mít Python soubor, který lze spustit.

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

**Co byste měli vidět:**

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

Přibližně na 150 řádcích kódu jste vytvořili plně funkční studijní nástroj poháněný lokálním LLM. Není třeba spravovat žádný API klíč, nejsou žádné náklady za používání a žádná data neopustí váš počítač.

> **Klíčový poznatek:** Všimněte si, že řádek `client = OpenAI(base_url=...) ` je *jediná* věc, která tuto aplikaci váže na Lemonade místo cloudového OpenAI. Zbytek kódu je identický s tím, co byste napsali pro jakoukoli OpenAI-kompatibilní službu. Pokud jste někdy používali Python knihovnu OpenAI, již víte, jak vytvářet aplikace s Lemonade.

### Co toto demonstruje

Tato malá aplikace ukazuje několik reálných integračních vzorů:

| Vzor | Kde se objevuje |
|---------|-----------------|
| **Systémové prompty** | Zpráva `"system"` říká LLM, aby výstup byl strukturovaný JSON |
| **Strukturovaný výstup** | Aplikace parsuje odpověď LLM jako JSON pro vytvoření kartiček |
| **Bezstavové požadavky** | Každé volání `generate_flashcards()` je nezávislé |
| **Zpracování chyb** | `try/except` elegantně zpracovává případy, kdy výstup LLM není platný JSON |

Tyto stejné vzory lze škálovat na jakoukoli aplikaci, jako jsou chatboti, asistenti pro kód, generátory obsahu nebo automatizační nástroje.

#### Bonusová výzva

* Pro přidanou výzvu zkuste aktualizovat aplikaci tak, aby kartičky byly přečteny uživateli nahlas, s odkazem na příklad uvedený [zde](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Spouštění modelů na NPU (volitelné)

Pokud máte Ryzen AI 300/400/Max 300 series nebo Z2 Extreme, vaše zařízení má vestavěnou **Neural Processing Unit (NPU)** — dedikovaný čip navržený speciálně pro AI úlohy. Spouštění modelů na NPU je energeticky úspornější než použití GPU, což ho činí ideálním pro AI úlohy na pozadí, delší relace a použití na baterii.

Lemonade podporuje tři režimy provádění na NPU, všechny transparentní za stejným OpenAI API:

| Režim | Jak funguje | Receptura | Příklady modelů |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU zpracovává prompt, iGPU generuje tokeny | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Pouze NPU** | Celá inference běží na NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Používá engine FastFlowLM na NPU, optimalizovaný pro AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Požadavky

- Procesor **AMD Ryzen AI 300/400 series nebo Z2 series**
- Pro modely **FLM**: Runtime FLM lze nainstalovat z aplikace Lemonade nebo ho Lemonade automaticky nainstaluje při spuštění FLM modelu. Chcete-li se dozvědět více o FastFlowLM, viz [zde](https://fastflowlm.com/docs/).


### Krok 8: Spuštění hybridního modelu

Hybridní modely rozdělují práci mezi NPU a iGPU pro dobrý poměr rychlosti a efektivity. V Lemonade App vyberte model ze seznamu `Ryzen AI LLM`, například `Qwen3-4B-Hybrid`, nebo ho spusťte pomocí následujícího příkazu:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade automaticky detekuje váš NPU a nainstaluje backend **Ryzen AI LLM**.

> **Co se děje pod kapotou?** Když odešlete zprávu, NPU zpracuje celý váš prompt paralelně (toto se nazývá „prefill"). Poté iGPU převezme řízení a generuje odpověď jeden token po druhém (toto se nazývá „decode"). Tento hybridní přístup využívá silné stránky každého čipu.

### Krok 9: Spuštění FLM modelu

Modely FastFlowLM (FLM) jsou specificky optimalizovány pro architekturu AMD XDNA2 NPU a mohou být pro svou velikost velmi rychlé. Například vyberte `qwen3.5-4b-FLM` ze seznamu `FastFlowLM NPU` nebo použijte následující příkaz:

<!-- @os:windows -->
Povolení `FastFlowLM` ve Windows:

* Otevřete nabídku `Backends Manager`.
* Najděte kategorii backendu `FastFlowLM NPU`.
* Klikněte na Install NPU.
* Po dokončení instalace bude v rozbalovací nabídce FFLM k dispozici přibližně 36 výchozích modelů.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Při prvním spuštění aplikace `Lemonade` není backend `FastFlowNPU` ve výchozím nastavení povolen.
Lokální aplikace otevře instalační stránku, která vás provede nastavením.

Povolení `FastFlowLM` v Linuxu:

* Otevřete aplikaci `Lemonade`.
* Navštivte [oficiální dokumentaci FLM](https://lemonade-server.ai/flm_npu_linux.html) a postupujte podle kroků instalace FLM výběrem vaší linuxové distribuce.
* Povolte backporty podle pokynů na instalační stránce.
* Stáhněte nejnovější vydání `v0.9.x` ze [stránky tagů](https://github.com/FastFlowLM/FastFlowLM/tags).
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Pro AMD Halo Developer Platform se ujistěte, že jste vybrali Debian 13.
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
* Doporučeno: Ukončete `Lemonade App` a znovu ji otevřete, aby byly změny detekovány.
* Doporučeno: Otevřete `Backends Manager` a klikněte na Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Po úspěšné instalaci byste měli vidět, že `flm:npu` bylo dokončeno ve **Download Manageru** uvnitř **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Poté můžete vybrat libovolný z dostupných FFLM modelů a začít používat NPU backend.

Pro konkrétní model stáhněte požadovaný model ze [stránky modelů](https://fastflowlm.com/docs/models/qwen/) a ověřte ho pomocí příkazu Shell uvedeného v dokumentaci.
```
flm run qwen3.5-4b-FLM
```
nebo přes 
```
lemonade run qwen3.5-4b-FLM
```

FLM modely zahrnují některé z nejpopulárnějších architektur (Gemma 3, Qwen 3, Llama 3 a DeepSeek R1) a jejich velikost se pohybuje od méně než 1 GB do více než 13 GB.
Lemonade automaticky detekuje váš NPU a nainstaluje backend **FastFlowLM NPU**.

<!-- @os:windows -->
> **Tip:** Pro nejlepší výkon NPU povolte turbo režim:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Přepínání modelů

Aplikace s kartičkami z kroku 6 funguje i s NPU modely — stačí změnit název modelu:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Další kroky

Máte lokální AI server běžící na vlastním hardwaru — zde je, kam se vydat dál:

1. **Připojte své oblíbené aplikace**: Lemonade funguje ihned po instalaci s [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) a [mnoha dalšími](https://lemonade-server.ai/marketplace).

2. **Prozkoumejte více modelů**: Prozkoumejte celou [knihovnu modelů](https://lemonade-server.ai/docs/server/server_models/) a najděte modely optimalizované pro kódování, uvažování, rozpoznávání obrazu a další. Použijte Lemonade App nebo `lemonade list` k zobrazení dostupných možností.

3. **Odemkněte GPU akceleraci ROCm**: Pokud máte podporovaný AMD GPU, přepněte na backend ROCm: `lemonade config set llamacpp.backend=rocm`. Viz [podporované AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Přečtěte si úplnou specifikaci API**: Lemonade podporuje dokončování chatu, embeddingy, přepis audia, generování obrázků, převod textu na řeč a další. Viz [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) pro každý endpoint.

5. **Přispějte**: Lemonade je open source. Podívejte se na [průvodce přispíváním](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) a hledejte [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).