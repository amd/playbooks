<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

🍋 **Lemonade** je odprtokodni lokalni strežnik za umetno inteligenco, ki vam omogoča zagon velikih jezikovnih modelov (LLM), generatorjev slik in zvočnih modelov neposredno na vaši lastni strojni opremi. Modele izpostavi prek standardnega industrijskega **API-ja OpenAI**, zato lahko vsaka aplikacija, ki deluje z OpenAI, takoj deluje tudi z Lemonade. Do konca tega vodnika boste uporabljali Lemonade za lokalni zagon modelov na svojem računalniku.

## Kaj se boste naučili

Do konca tega vodnika boste znali:

* **Namestiti Lemonade Server** in preveriti, ali se izvaja.
* **Prenesti LLM in klepetati z njim** z enim samim ukazom.
* **Raziskati spletni uporabniški vmesnik** in preizkusiti različne modalnosti, kot so vid, pretvorba govora v besedilo in generiranje slik.
* **Preklapljati med zaledji GPU** med Vulkan in programsko opremo AMD ROCm™.
* **Zgraditi aplikacijo v Pythonu**, ki jo poganja lokalni LLM z uporabo API-ja, združljivega z OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Zaganjati modele na AMD Neural Processing Unit (NPU)** z uporabo načinov izvajanja Hybrid in FLM na strojni opremi AMD Ryzen™ AI.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev potrebne programske opreme

Preden začnete, se prepričajte, da imate:

- Osebni računalnik z operacijskim sistemom **Windows 11** ali podprto distribucijo **Linux** (Ubuntu 24.04+, Fedora, Debian)
- Priporočenih je **16 GB pomnilnika RAM** za izvajalni model, uporabljen v korakih 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** je priporočeno, če želite uporabiti večji model za generiranje kode v koraku 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB prostega prostora na disku**, odvisno od modelov, ki jih prenesete. Največji model v tem vodniku obsega približno 20 GB.
- **Python 3.10–3.13** (uporabljen v razdelku o aplikaciji v Pythonu)
- Internetno povezavo (žično ali brezžično)
<!-- @device:halo_box,halo,stx,krk -->
- [Neobvezno] AMD XDNA 2 NPU (serija Ryzen AI 300/400/Max 300 ali Z2 Extreme) z najnovejšim gonilnikom, nameščenim iz [Navodil za namestitev programske opreme Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), če želite zagnati model na NPU.
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

## Temeljni koncepti — kako delujejo lokalni strežniki za umetno inteligenco

Preden zaženemo model, je vredno razumeti, *zakaj* je stvari postavljena na ta način. Lemonade je **lokalni strežnik za modele**, proces, ki naloži modele umetne inteligence v pomnilnik in jih prek HTTP izpostavi aplikacijam, tako kot bi to storila storitev umetne inteligence v oblaku.

### Zakaj strežnik?

| Prednost | Kaj to pomeni za vas |
|---------|----------------------|
| **Poenostavljena integracija** | Aplikacije komunicirajo prek enega samega HTTP API-ja namesto uporabe knjižnic C++ ali Python, specifičnih za strojno opremo. |
| **Skupni modeli** | En sam naložen model lahko istočasno streže več aplikacijam, brez podvojenih kopij, ki bi zasedale pomnilnik RAM. |
| **Prenosljivost iz oblaka na lokalno** | Koda, napisana za oblačni API OpenAI, deluje z Lemonade z zamenjavo enega samega URL-ja. |
| **Ločevanje odgovornosti** | Upravljanje modelov, pretakanje in odpornost na napake obravnava strežnik, tako da se lahko razvijalci osredotočijo na svojo aplikacijo. |

### Standard API OpenAI

Lemonade implementira **API OpenAI**, isti vmesnik, ki ga uporabljajo ChatGPT, Azure OpenAI in številne druge storitve. Model pogovora je preprost:

| Vloga | Kdo govori |
|------|---------------|
| **system** | Navodila modelu (osebnost, omejitve, razpoložljiva orodja) |
| **user** | Sporočila od človeka (ali aplikacije) modelu |
| **assistant** | Odgovori, ki jih ustvari model |

To pomeni, da lahko katera koli knjižnica ali aplikacija, ki podpira OpenAI, komunicira z Lemonade, tako da jo usmerite na `http://localhost:13305/api/v1`, medtem ko se izvaja Lemonade Server.

## Glavna dejavnost — vaš prvi lokalni klepet z umetno inteligenco

Prenesimo LLM in se z njim pogovorimo, pri čemer bo umetna inteligenca v celoti delovala na vašem lastnem računalniku.

### Korak 1: Prenos in zagon modela

Lemonade se dobavlja s skrbno izbrano knjižnico modelov. Začnimo z modelom **Gemma-4-E2B-it**, zmogljivim in kompaktnim modelom, ki vključuje podporo za vid. Odprite terminal in zaženite:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Ta en sam ukaz naredi tri stvari:

1. **Prenese** model (~3 GB) iz Hugging Face, če še ni prenesen. (Lahko traja nekaj časa)
2. **Zažene** proces Lemonade Server na vratih 13305.
3. **Odpre Lemonade App**, tako da lahko takoj začnete klepetati z modelom.


<!-- @os:windows -->
V sistemu Windows se Lemonade App zažene samodejno in takoj lahko začnete klepetati. Če ste namestili paket `minimal.msi`, aplikacija ni vključena. Za začetek klepeta odprite spletni brskalnik in pojdite na `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
V sistemu Linux odprite brskalnik in pojdite na `http://localhost:13305`, da dostopate do spletne aplikacije.
<!-- @os:end -->

Poskusite vnesti vprašanje:

```
What are three fun facts about lemons?
```

Model bo odgovoril neposredno v klepetalnem oknu. **Čestitamo! Lokalno poganjate velik jezikovni model.**

![Lemonade App s prikazanimi dnevniki](../../dependencies/assets/ChatwithLogs.png)

V podoknu Server Logs v aplikaciji Lemonade App lahko po vsakem odgovoru najdete podatke o telemetriji glede zmogljivosti modela. Na primer:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Korak 2: Raziščite spletni vmesnik in različne načine delovanja

Lemonade vključuje vgrajen spletni vmesnik, kjer lahko:

- **Komunicirate** z naloženim modelom v znanem klepetalnem oknu
- **Brskate po modelih** v zavihku Model Manager
- **Prenesete nove modele** z enim klikom

Preizkusite preklapljanje med različnimi načini delovanja z zavihkom **Model Manager** v spletnem vmesniku, kjer lahko brskate po modelih glede na Recipe ali Category:

1. **Vizija:** Model `Gemma-4-E2B-it-GGUF`, ki ga imate že naloženega, podpira vizijo. Prilepite sliko v klepetalno okno in prosite model, naj jo opiše.
2. **Generiranje slik:** V kategoriji Image prenesite model za slike, kot je `SDXL-Turbo`, iz Model Managerja, nato pa uporabite Lemonade Image Generator, da vnesete poziv in lokalno ustvarite sliko.
3. **Zvok:** V kategoriji Audio prenesite zvočni model, kot je `Whisper-Tiny`, ki lahko pretvarja govor v besedilo. Priskrbite posnetek zvoka za lokalno transkripcijo. Za pretvorbo besedila v govor preizkusite enega izmed modelov v kategoriji Speech, kot je `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### Korak 3: Preizkusite model z drugim ogrodjem (backend)

Če se z miško zadržite nad modelom v aplikaciji Lemonade, se prikaže ikona zobnika. S klikom nanjo lahko izberete možnosti za model, vključno z izbiro želenega ogrodja (backend).

Lemonade privzeto uporablja Vulkan za pospeševanje z GPU. Če imate podprt namenski AMD GPU, lahko preklopite na ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

Za upravljanje nameščenih ogrodij kliknite gumb za ogrodje v skrajno levem stolpcu.

Ogrodje lahko določite tudi z naslednjim ukazom:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Privzeto ogrodje lahko nastavite tudi z okoljsko spremenljivko `LEMONADE_LLAMACPP`, z vrednostmi: `vulkan`, `rocm` ali `cpu`.

---

## Poglobimo se — izdelava aplikacije z umetno inteligenco v Pythonu

Prava moč lokalnega strežnika za umetno inteligenco je v tem, da se lahko nanj poveže katera koli aplikacija z le nekaj vrsticami kode. Da bi to dokazali, izdelajmo majhen, a povsem funkcionalen **generator študijskih kartic (flashcard)**, kjer navedete temo, aplikacija ustvari kartice, vi pa se lahko interaktivno preverjate.

### Korak 4: Zaženite strežnik

Preverite, ali strežnik Lemonade deluje. Po namestitvi se običajno samodejno zažene v ozadju. Za preverjanje zaženite:

```
lemonade status
```

Videti bi morali sporočilo, podobno: `Server is running on port 13305`.

Če strežnik ne deluje, ga zaženite z odprtjem aplikacije Lemonade. Uporabite privzeta vrata **13305** (lahko jih potrdite ali izberete v ikoni v sistemski vrstici).

### Korak 5: Namestite odjemalec OpenAI Python Client

V terminalu ustvarite venv in namestite odjemalec OpenAI Python Client z naslednjimi ukazi:
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

### Korak 6: Izdelajte aplikacijo za kartice (flashcard app)

Prenesimo drugačen model za generiranje kode: `Qwen3.5-35B-A3B-GGUF`. To je velik (~20 GB) in zmogljiv model, najprimernejši za sisteme z 32 GB+ pomnilnika RAM. Če imate na voljo manj RAM-a, namesto tega preizkusite `Qwen3.5-9B-GGUF` (~6 GB).

Prenesete ga lahko prek uporabniškega vmesnika ali z naslednjim ukazom:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Vnesite naslednji poziv v Lemonade Chat UI, da ustvarite kodo za preprosto aplikacijo za kartice (Flashcard app).

Za ustvarjanje naše Python aplikacije bomo uporabili Qwen3.5-35B-A3B-GGUF (večji model, boljši pri pisanju kode), sama aplikacija pa bo med izvajanjem klicala Gemma-4-E2B-it-GGUF (manjši model, ki ste ga že prenesli). Kodo lahko nato kopirate v datoteko po vaši izbiri, da jo zaženete v Pythonu.

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

> **Nasvet**: Sledili smo standardnim inženirskim praksam s temeljito izdelavo poziva in uporabo sistema z dvema modeloma za optimizacijo virov in hitrosti.

Za vaše udobje smo priložili vzorčni izpis v datoteki [`flashcards.py`](assets/flashcards.py). Prosto jo prenesite v svoj imenik. V vsakem primeru bi zdaj morali imeti Python datoteko, ki jo je mogoče zagnati.

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


### Korak 7: Zaženite ustvarjeno kodo

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Tole bi morali videti:**

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

V približno 150 vrsticah kode ste izdelali povsem funkcionalno študijsko orodje, ki ga poganja lokalni LLM. Ni ključa API za upravljanje, ni stroškov uporabe in noben podatek ne zapusti vaše naprave.

> **Ključno spoznanje:** Opazite, da je vrstica `client = OpenAI(base_url=...) ` *edina* stvar, ki to aplikacijo povezuje z Lemonade namesto z oblakom OpenAI. Preostala koda je enaka tisti, ki bi jo napisali za katero koli storitev, združljivo z OpenAI. Če ste kdaj uporabljali knjižnico OpenAI Python, že znate izdelovati aplikacije z Lemonade.

### Kaj to dokazuje

Ta majhna aplikacija prikazuje več realnih integracijskih vzorcev:

| Vzorec | Kje se pojavi |
|---------|-----------------|
| **Sistemski pozivi** | Sporočilo `"system"` naroči LLM-ju, naj izpiše strukturiran JSON |
| **Strukturiran izpis** | Aplikacija razčleni odgovor LLM-ja kot JSON za izdelavo kartic |
| **Brezstanjske zahteve** | Vsak klic `generate_flashcards()` je neodvisen |
| **Obravnava napak** | `try/except` elegantno obravnava primere, ko izpis LLM-ja ni veljaven JSON |

Ti isti vzorci se prenesejo na katero koli aplikacijo, kot so klepetalni boti, pomočniki za kodiranje, generatorji vsebin, orodja za avtomatizacijo.

#### Dodaten izziv

* Za dodaten izziv poskusite posodobiti aplikacijo tako, da bo kartice uporabniku prebrala na glas, s sklicevanjem na primer, ki je na voljo [tukaj](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Zagon modelov na NPE (neobvezno)

Če imate procesor Ryzen AI serije 300/400/Max 300 ali Z2 Extreme, ima vaša naprava vgrajeno **nevronsko procesno enoto (NPU)**, namenski čip, zasnovan posebej za obremenitve umetne inteligence. Zagon modelov na NPE je energijsko učinkovitejši kot uporaba GPE, zaradi česar je idealen za AI opravila v ozadju, daljše seje in uporabo na baterijsko napajanje.

Lemonade podpira tri načine izvajanja na NPE, vsi so transparentni znotraj istega OpenAI API:

| Način | Kako deluje | Recept | Primeri modelov |
|------|-------------|--------|----------------|
| **Hibridni (NPE + iGPE)** | NPE obdela poziv, iGPE generira žetone | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Samo NPE** | Celoten sklep se izvaja na NPE | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Uporablja mehanizem FastFlowLM na NPE, optimiziran za AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Zahteve

- Procesor **AMD Ryzen AI serije 300/400 ali serije Z2**
- Za modele **FLM**: čas izvajanja FLM lahko namestite iz aplikacije Lemonade, sicer bo Lemonade samodejno namestil čas izvajanja FLM ob zagonu modela FLM. Če želite izvedeti več o FastFlowLM, glejte [tukaj](https://fastflowlm.com/docs/).


### Korak 8: Zagon hibridnega modela

Hibridni modeli razdelijo delo med NPE in iGPE za dobro ravnovesje med hitrostjo in učinkovitostjo. V aplikaciji Lemonade izberite model s seznama `Ryzen AI LLM`, na primer `Qwen3-4B-Hybrid`, ali ga zaženite z naslednjim ukazom:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade samodejno zazna vašo NPE in namesti zaledje **Ryzen AI LLM**.

> **Kaj se dogaja v ozadju?** Ko pošljete sporočilo, NPE obdela celoten vaš poziv vzporedno (temu pravimo »prefill«). Nato iGPE prevzame nadzor za generiranje odgovora, žeton za žetonom (temu pravimo »decode«). Ta hibridni pristop izkoristi prednosti vsakega čipa.

### Korak 9: Zagon modela FLM

Modeli FastFlowLM (FLM) so posebej optimizirani za arhitekturo NPE AMD XDNA2 in so lahko glede na svojo velikost zelo hitri. Na primer, izberite `qwen3.5-4b-FLM` s seznama `FastFlowLM NPU` ali uporabite naslednji ukaz:

<!-- @os:windows -->
Če želite omogočiti `FastFlowLM` v sistemu Windows:

* Odprite meni `Backends Manager`.
* Poiščite kategorijo zaledja `FastFlowLM NPU`.
* Kliknite Install NPU.
* Ko je namestitev končana, bo pod spustnim menijem FFLM na voljo približno 36 privzetih modelov.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Ko je aplikacija `Lemonade` zagnana prvič, zaledje `FastFlowNPU` privzeto ni omogočeno.
Lokalna aplikacija bo odprla stran za namestitev, ki vas bo vodila skozi nastavitev.

Če želite omogočiti `FastFlowLM` v sistemu Linux:

* Odprite aplikacijo `Lemonade`.
* Obiščite [uradno dokumentacijo FLM](https://lemonade-server.ai/flm_npu_linux.html) in sledite korakom namestitve za FLM tako, da izberete svojo distribucijo Linuxa.
* Omogočite backports, kot je navedeno na strani za namestitev.
* Prenesite najnovejšo izdajo `v0.9.x` s [strani z oznakami](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Za AMD Halo Developer Platform se prepričajte, da izberete Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Namestite prenesen paket `.deb`.
* Priporočeno: zaprite aplikacijo `Lemonade App` in jo znova odprite, da se spremembe zaznajo.
* Priporočeno: odprite `Backends Manager` in kliknite Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Po uspešni namestitvi bi morali videti, da je `flm:npu` dokončan v **upravitelju prenosov** znotraj **namizne aplikacije Lemonade**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Nato lahko izberete katerega koli od razpoložljivih modelov FFLM in začnete uporabljati zaledje NPE.

Za specifičen model prenesite želeni model s [strani z modeli](https://fastflowlm.com/docs/models/qwen/) in ga preverite z ukazom Shell, navedenim v dokumentaciji.
```
flm run qwen3.5-4b-FLM
```
ali prek 
```
lemonade run qwen3.5-4b-FLM
```

Modeli FLM vključujejo nekatere najbolj priljubljene arhitekture (Gemma 3, Qwen 3, Llama 3 in DeepSeek R1) ter segajo od pod 1 GB do več kot 13 GB.
Lemonade samodejno zazna vašo NPE in namesti zaledje **FastFlowLM NPU**.

<!-- @os:windows -->
> **Nasvet:** za najboljšo zmogljivost NPE omogočite turbo način:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Preklapljanje med modeli

Aplikacija za učne kartice iz koraka 6 deluje tudi z modeli NPE, le spremenite ime modela:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Naslednji koraki

Zdaj imate lokalni AI strežnik, ki teče na vaši lastni strojni opremi, tukaj je, kam nadaljevati:

1. **Povežite svoje priljubljene aplikacije**: Lemonade deluje takoj po namestitvi z [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) in [še mnogimi drugimi](https://lemonade-server.ai/marketplace).

2. **Prebrskajte več modelov**: Raziščite celotno [knjižnico modelov](https://lemonade-server.ai/docs/server/server_models/), da najdete modele, optimizirane za kodiranje, sklepanje, vid in več. Uporabite aplikacijo Lemonade ali ukaz `lemonade list`, da si ogledate, kaj je na voljo.

3. **Odklenite pospeševanje GPE ROCm**: Če imate podprto AMD GPE, preklopite na zaledje ROCm: `lemonade config set llamacpp.backend=rocm`. Glejte [podprte AMD GPE-je](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Preberite celotno specifikacijo API**: Lemonade podpira dopolnjevanje pogovorov, vdelave, prepis zvoka, generiranje slik, pretvorbo besedila v govor in več. Za vsako končno točko glejte [specifikacijo strežnika](https://lemonade-server.ai/docs/server/server_spec/).

5. **Prispevajte**: Lemonade je odprtokoden. Oglejte si [vodnik za prispevanje](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) in poiščite [dobre prve težave](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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