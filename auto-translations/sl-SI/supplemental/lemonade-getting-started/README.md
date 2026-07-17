<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ta priročnik uporablja posebne oznake, ki jih GitHub ne more prikazati. Za pravilen ogled te vsebine obiščite [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Pregled

🍋 **Lemonade** je odprtokodni lokalni AI strežnik, ki vam omogoča zagon velikih jezikovnih modelov (LLM), generatorjev slik in zvočnih modelov neposredno na vaši lastni strojni opremi. Modele izpostavlja prek industrijsko standardnega **OpenAI API**, tako da vsaka aplikacija, ki deluje z OpenAI, takoj deluje tudi z Lemonade. Do konca priročnika boste z Lemonade lokalno zaganjali modele na svojem računalniku.

## Kaj se boste naučili

Do konca tega priročnika boste znali:

* **Namestiti Lemonade Server** in preveriti, ali deluje.
* **Prenesti LLM in se z njim pogovarjati** z enim samim ukazom.
* **Raziskati spletni vmesnik** in preizkusiti različne modalnosti, kot so vid, pretvorba govora v besedilo in generiranje slik.
* **Preklapljati med GPU zaledji** med Vulkan in AMD ROCm™ programsko opremo.
* **Zgraditi Python aplikacijo**, ki jo poganja lokalni LLM z OpenAI-združljivim API.
<!-- @device:halo_box,halo,stx,krk -->
* **Zaganjati modele na AMD Neural Processing Unit (NPU)** z načini izvajanja Hybrid in FLM na strojni opremi AMD Ryzen™ AI.
<!-- @device:end -->

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev predpogojne programske opreme

Preden začnete, se prepričajte, da imate:

- Računalnik z operacijskim sistemom **Windows 11** ali podprto distribucijo **Linux** (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** je priporočeno za model, ki se uporablja v korakih 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** je priporočeno, če želite uporabiti večji model za generiranje kode v koraku 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB prostega prostora na disku**, odvisno od modelov, ki jih prenesete. Največji model v tem priročniku je velik približno 20 GB.
- **Python 3.10–3.13** (uporablja se v razdelku o Python aplikaciji)
- Internetna povezava (žična ali brezžična)
<!-- @device:halo_box,halo,stx,krk -->
- [Neobvezno] AMD XDNA 2 NPU (serija Ryzen AI 300/400/Max 300 ali Z2 Extreme) z najnovejšim gonilnikom, nameščenim po [navodilih za namestitev programske opreme Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), če želite zagnati model na NPU.
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

## Osnovni koncepti — kako delujejo lokalni AI strežniki

Preden zaženemo model, je vredno razumeti, *zakaj* so stvari nastavljene na ta način. Lemonade je **lokalni strežnik modelov** — proces, ki naloži AI modele v pomnilnik in jih izpostavi aplikacijam prek HTTP, tako kot bi to storila storitev AI v oblaku.

### Zakaj strežnik?

| Prednost | Kaj to pomeni za vas |
|---------|----------------------|
| **Poenostavljena integracija** | Aplikacije komunicirajo z enim HTTP API namesto da bi se ukvarjale s strojno specifičnimi knjižnicami C++ ali Python. |
| **Skupni modeli** | En naložen model lahko hkrati streže več aplikacijam, brez podvojenih kopij, ki bi požirale vaš RAM. |
| **Prenosljivost iz oblaka na lokalno** | Koda, napisana za OpenAI-jev oblačni API, deluje z Lemonade s spremembo enega URL-ja. |
| **Ločitev odgovornosti** | Upravljanje modelov, pretakanje in odpornost na napake so v pristojnosti strežnika, tako da se razvijalci lahko osredotočijo na svojo aplikacijo. |

### Standard OpenAI API

Lemonade implementira **OpenAI API** — enak vmesnik, ki ga uporabljata ChatGPT, Azure OpenAI in desetine drugih storitev. Model pogovora je preprost:

| Vloga | Kdo govori |
|------|---------------|
| **system** | Navodila modelu (osebnost, omejitve, razpoložljiva orodja) |
| **user** | Sporočila od človeka (ali aplikacije) modelu |
| **assistant** | Odgovori, ki jih generira model |

To pomeni, da lahko vsaka knjižnica ali aplikacija, ki podpira OpenAI, komunicira z Lemonade tako, da jo usmerimo na `http://localhost:13305/api/v1`, medtem ko Lemonade Server deluje.

## Glavna dejavnost — vaš prvi lokalni AI pogovor

Prenesimo LLM in se z njim pogovorimo, pri čemer AI v celoti teče na vašem lastnem računalniku.

### Korak 1: Prenos in zagon modela

Lemonade je opremljen s skrbno izbrano knjižnico modelov. Začnimo z **Gemma-4-E2B-it** — zmogljivim in kompaktnim modelom, ki vključuje podporo za vid. Odprite terminal in zaženite:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Ta en ukaz naredi tri stvari:

1. **Prenese** model (~3 GB) s Hugging Face, če še ni prenesen. (Lahko traja nekaj časa)
2. **Zažene** proces Lemonade Server na vratih 13305.
3. **Odpre Lemonade App**, da lahko začnete klepetati z modelom.


<!-- @os:windows -->
V sistemu Windows se Lemonade App zažene samodejno in takoj lahko začnete klepetati. Če ste namestili paket `minimal.msi`, aplikacija ni vključena. Za začetek klepeta odprite spletni brskalnik in pojdite na `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
V sistemu Linux odprite brskalnik in se pomaknite na `http://localhost:13305` za dostop do spletne aplikacije.
<!-- @os:end -->

Poskusite vtipkati vprašanje:

```
What are three fun facts about lemons?
```

Model bo odgovoril neposredno v oknu za klepet. **Čestitamo! Lokalno zaganjate veliki jezikovni model.**

![Lemonade App z prikazanimi dnevniki](../../dependencies/assets/ChatwithLogs.png)

V podoknu dnevnikov strežnika v Lemonade App po vsakem odgovoru najdete telemetrične podatke o zmogljivosti modela. Na primer:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Korak 2: Raziskovanje spletnega vmesnika in različnih modalnosti

Lemonade vključuje vgrajeni spletni vmesnik, kjer lahko:

- **Komunicirate** z naloženim modelom v poznanem oknu za klepet
- **Brskate po modelih** v zavihku Upravitelj modelov
- **Prenesete nove modele** z enim klikom

Poskusite preklapljati med različnimi modalnostmi z zavihkom **Upravitelj modelov** v spletnem vmesniku, kjer lahko brskate po modelih po receptu ali po kategoriji:

1. **Vid:** Model `Gemma-4-E2B-it-GGUF`, ki ga že imate naložen, podpira vid. Prilepite sliko v polje za klepet in prosite model, naj jo opiše.
2. **Generiranje slik:** V kategoriji Slike prenesite model za slike, kot je `SDXL-Turbo`, iz Upravitelja modelov, nato pa z generatorjem slik Lemonade vnesite poziv in lokalno ustvarite sliko.
3. **Zvok:** V kategoriji Zvok prenesite zvočni model, kot je `Whisper-Tiny`, ki zna pretvarjati govor v besedilo. Predložite posnetek zvoka za lokalno transkripcijo. Za pretvorbo besedila v govor preizkusite enega od modelov v kategoriji Govor, na primer `kokoro-v1`.

![Večmodalnost z Lemonade](../../dependencies/assets/multi_modality.png)

### Korak 3: Preizkusite model z drugačnim zaledjem

Če v Lemonade App premaknete kazalec nad model, se prikaže ikona zobnika. S klikom nanjo lahko izberete možnosti za model, vključno z izborom želenega zaledja.

Privzeto Lemonade za pospeševanje GPU uporablja Vulkan. Če imate podprto AMD diskretno GPU, lahko preklopite na ROCm.

![Lemonade izbira zaledja](../../dependencies/assets/lemonademodeloptions.png)

Za upravljanje nameščenih zaledij kliknite gumb za zaledje v skrajno levem stolpcu.

Alternativno lahko zaledje določite z naslednjim ukazom:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Privzeto zaledje lahko nastavite tudi z okoljsko spremenljivko `LEMONADE_LLAMACPP` z vrednostmi: `vulkan`, `rocm` ali `cpu`.

---

## Poglobitev — zgradite aplikacijo z AI v Python

Prava moč lokalnega AI strežnika je v tem, da se nanj lahko poveže vsaka aplikacija z le nekaj vrsticami kode. Da to dokažemo, zgradimo majhen, a funkcionalen **generator učnih kartic**, kjer mu podate temo, on ustvari kartice in se lahko interaktivno preizkušate.

### Korak 4: Zagon strežnika

Preverite, ali Lemonade strežnik deluje. Običajno se po namestitvi samodejno zažene v ozadju. Za preverjanje zaženite:

```
lemonade status
```

Prikazalo bi se sporočilo, kot je: `Server is running on port 13305`.

Če strežnik ne deluje, ga zaženite z odprtjem aplikacije Lemonade. Uporabite privzeta vrata **13305** (to lahko potrdite ali izberete iz ikone v sistemski vrstici).

### Korak 5: Namestitev odjemalca OpenAI Python

V terminalu ustvarite venv in namestite odjemalca OpenAI Python z naslednjimi ukazi:
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

### Korak 6: Izgradnja aplikacije za učne kartice

Prenesimo drug model za generiranje kode: `Qwen3.5-35B-A3B-GGUF`. To je velik (~20 GB) in zmogljiv model, ki je najprimernejši za sisteme z 32 GB+ RAM. Če imate na voljo manj RAM, namesto tega preizkusite `Qwen3.5-9B-GGUF` (~6 GB).

Prenesete ga lahko iz vmesnika ali zaženete naslednje:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

V klepetalni vmesnik Lemonade vnesite naslednji poziv za generiranje kode za preprosto aplikacijo za učne kartice.

Za generiranje naše Python aplikacije bomo uporabili Qwen3.5-35B-A3B-GGUF (večji model, boljši pri pisanju kode), sama aplikacija pa bo med izvajanjem klicala Gemma-4-E2B-it-GGUF (manjši model, ki ste ga že prenesli). Kodo lahko nato kopirate v datoteko po vaši izbiri in jo zaženete v Python.

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

> **Nasvet**: Sledili smo standardnim inženirskim praksam z natančnim oblikovanjem pozivov in z uporabo sistema dveh modelov za optimizacijo virov in hitrosti.

Za vašo priročnost smo zagotovili vzorčni izhod v [`flashcards.py`](assets/flashcards.py). Prenesite ga v svojo mapo. V vsakem primeru bi morali imeti zdaj Python datoteko, ki jo je mogoče zagnati.

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


### Korak 7: Zagon generirane kode

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Tukaj je, kar bi morali videti:**

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

V približno 150 vrsticah kode ste zgradili popolnoma funkcionalno učno orodje, ki ga poganja lokalni LLM. Ni API ključa za upravljanje, ni stroškov uporabe in nobeni podatki nikoli ne zapustijo vašega računalnika.

> **Ključna ugotovitev:** Opazite, da je vrstica `client = OpenAI(base_url=...) ` *edina* stvar, ki to aplikacijo veže na Lemonade namesto na OpenAI-jev oblak. Preostala koda je enaka tisti, ki bi jo napisali za katero koli OpenAI-združljivo storitev. Če ste kdaj uporabljali knjižnico OpenAI Python, že veste, kako graditi aplikacije z Lemonade.

### Kaj to prikazuje

Ta majhna aplikacija preizkuša več vzorcev integracije iz resničnega sveta:

| Vzorec | Kje se pojavi |
|---------|-----------------|
| **Sistemski pozivi** | Sporočilo `"system"` pove LLM, naj izpiše strukturiran JSON |
| **Strukturiran izhod** | Aplikacija razčleni LLM-jev odgovor kot JSON za izgradnjo učnih kartic |
| **Brezstanjske zahteve** | Vsak klic `generate_flashcards()` je neodvisen |
| **Obravnava napak** | `try/except` elegantno obravnava primere, ko izhod LLM ni veljaven JSON |

Ti isti vzorci se razširijo na katero koli aplikacijo, kot so klepetalniki, pomočniki za kodo, generatorji vsebine, orodja za avtomatizacijo.

#### Bonus izziv

* Za dodaten izziv poskusite posodobiti aplikacijo tako, da bo učne kartice prebrala uporabniku, pri čemer si oglejte primer, ki je na voljo [tukaj](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Zaganjanje modelov na NPU (neobvezno)

Če imate serijo Ryzen AI 300/400/Max 300 ali Z2 Extreme, ima vaša naprava vgrajeno **Neural Processing Unit (NPU)** — namenski čip, zasnovan posebej za AI delovne obremenitve. Zaganjanje modelov na NPU je energetsko učinkovitejše kot uporaba GPU, kar ga naredi idealnega za AI naloge v ozadju, daljše seje in uporabo na baterijo.

Lemonade podpira tri načine izvajanja NPU, ki so vsi transparentni za isti OpenAI API:

| Način | Kako deluje | Recept | Primeri modelov |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU obdela poziv, iGPU generira žetone | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Samo NPU** | Celotno sklepanje teče na NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Uporablja motor FastFlowLM na NPU, optimiziran za AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Zahteve

- Procesor **AMD Ryzen AI 300/400 serije ali Z2 serije**
- Za modele **FLM**: Izvajalno okolje FLM je mogoče namestiti iz aplikacije Lemonade ali pa ga Lemonade samodejno namesti pri zagonu modela FLM. Če želite izvedeti več o FastFlowLM, glejte [tukaj](https://fastflowlm.com/docs/).


### Korak 8: Zagon hibridnega modela

Hibridni modeli razdelijo delo med NPU in iGPU za dobro ravnovesje med hitrostjo in učinkovitostjo. V Lemonade App izberite model s seznama `Ryzen AI LLM`, na primer `Qwen3-4B-Hybrid`, ali ga zaženite z naslednjim ukazom:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade samodejno zazna vaš NPU in namesti zaledje **Ryzen AI LLM**.

> **Kaj se dogaja v ozadju?** Ko pošljete sporočilo, NPU vzporedno obdela celoten vaš poziv (to se imenuje "prefill"). Nato iGPU prevzame in generira odgovor en žeton naenkrat (to se imenuje "decode"). Ta hibridni pristop izkorišča prednosti vsakega čipa.

### Korak 9: Zagon modela FLM

Modeli FastFlowLM (FLM) so posebej optimizirani za AMD-jevo arhitekturo XDNA2 NPU in so za svojo velikost lahko zelo hitri. Na primer, izberite `qwen3.5-4b-FLM` s seznama `FastFlowLM NPU` ali uporabite naslednji ukaz:

<!-- @os:windows -->
Za omogočanje `FastFlowLM` v sistemu Windows:

* Odprite meni `Backends Manager`.
* Poiščite kategorijo zaledja `FastFlowLM NPU`.
* Kliknite Install NPU.
* Ko je namestitev končana, bo na voljo ~36 privzetih modelov v spustnem meniju FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Ko se aplikacija `Lemonade` prvič zažene, zaledje `FastFlowNPU` privzeto ni omogočeno.
Lokalna aplikacija bo odprla namestitveno stran, ki vas bo vodila skozi nastavitev.

Za omogočanje `FastFlowLM` v sistemu Linux:

* Odprite aplikacijo `Lemonade`.
* Obiščite [uradno dokumentacijo FLM](https://lemonade-server.ai/flm_npu_linux.html) in sledite korakom namestitve za FLM z izbiro vaše distribucije Linux.
* Omogočite backports, kot je navedeno na namestitveni strani.
* Prenesite najnovejšo različico `v0.9.x` s [strani oznak](https://github.com/FastFlowLM/FastFlowLM/tags).
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Za AMD Halo Developer Platform izberite Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Namestite preneseni paket `.deb`.
* Priporočeno: Zaprite aplikacijo `Lemonade App` in jo znova odprite, da se zaznajo spremembe.
* Priporočeno: Odprite `Backends Manager` in kliknite Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Po uspešni namestitvi bi morali v **Upravitelju prenosov** znotraj **Lemonade Desktop App** videti, da je `flm:npu` dokončan.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Nato lahko izberete katerega koli od razpoložljivih modelov FFLM in začnete uporabljati zaledje NPU.

Za določen model prenesite želeni model s [strani modelov](https://fastflowlm.com/docs/models/qwen/) in ga preverite z ukazom Shell, ki je naveden v dokumentaciji.
```
flm run qwen3.5-4b-FLM
```
ali prek 
```
lemonade run qwen3.5-4b-FLM
```

Modeli FLM vključujejo nekatere najpopularnejše arhitekture (Gemma 3, Qwen 3, Llama 3 in DeepSeek R1) in segajo od manj kot 1 GB do več kot 13 GB.
Lemonade samodejno zazna vaš NPU in namesti zaledje **FastFlowLM NPU**.

<!-- @os:windows -->
> **Nasvet:** Za najboljšo zmogljivost NPU omogočite turbo način:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Preklapljanje modelov

Aplikacija za učne kartice iz koraka 6 deluje tudi z modeli NPU — samo spremenite ime modela:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Naslednji koraki

Lokalni AI strežnik teče na vaši lastni strojni opremi — tukaj je, kam iti naprej:

1. **Povežite svoje najljubše aplikacije**: Lemonade deluje takoj z [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) in [še mnogo več](https://lemonade-server.ai/marketplace).

2. **Brskajte po več modelih**: Raziščite celotno [knjižnico modelov](https://lemonade-server.ai/docs/server/server_models/), da najdete modele, optimizirane za kodiranje, sklepanje, vid in še več. Uporabite Lemonade App ali `lemonade list`, da vidite, kaj je na voljo.

3. **Odklenite pospeševanje GPU z ROCm**: Če imate podprto AMD GPU, preklopite na zaledje ROCm: `lemonade config set llamacpp.backend=rocm`. Glejte [podprte AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Preberite celotno specifikacijo API**: Lemonade podpira dokončanje pogovorov, vdelane predstavitve, transkripcijo zvoka, generiranje slik, pretvorbo besedila v govor in še več. Glejte [specifikacijo strežnika](https://lemonade-server.ai/docs/server/server_spec/) za vsako končno točko.

5. **Prispevajte**: Lemonade je odprtokoden. Oglejte si [vodnik za prispevanje](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) in poiščite [primerne prve težave](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).