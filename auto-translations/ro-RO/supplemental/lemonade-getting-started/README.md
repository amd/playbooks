<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->
## Prezentare generală

🍋 **Lemonade** este un server AI local open-source care vă permite să rulați modele lingvistice de mari dimensiuni (LLM), generatoare de imagini și modele audio direct pe propriul hardware. Acesta expune modelele prin intermediul standardului industrial **OpenAI API**, astfel încât orice aplicație care funcționează cu OpenAI poate funcționa instantaneu cu Lemonade. Până la finalul acestui ghid, veți folosi Lemonade pentru a rula modele local pe mașina dumneavoastră.

## Ce veți învăța

Până la finalul acestui ghid veți putea să:

* **Instalați Lemonade Server** și să verificați dacă rulează.
* **Descărcați și conversați cu un LLM** folosind o singură comandă.
* **Explorați interfața web** și să încercați diferite modalități, precum viziune, speech-to-text și generare de imagini.
* **Comutați între backend-urile GPU** Vulkan și AMD ROCm™ software.
* **Construiți o aplicație Python** alimentată de un LLM local, folosind API-ul compatibil cu OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Rulați modele pe unitatea de procesare neuronală AMD (NPU)** utilizând modurile de execuție Hybrid și FLM pe hardware-ul AMD Ryzen™ AI.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Configurarea Memoriei
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificați actualizările software
<!-- @require:software-update -->
<!-- @device:end -->
## Instalarea prerechizitelor software

Înainte de a începe, asigurați-vă că aveți:

- Un PC pe care rulează **Windows 11** sau o distribuție **Linux** compatibilă (Ubuntu 24.04+, Fedora, Debian)
- Se recomandă **16 GB de RAM** pentru modelul runtime utilizat în Pașii 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). Se recomandă **32 GB+** dacă doriți să utilizați modelul de generare de cod mai mare din Pasul 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB de spațiu liber pe disc**, în funcție de modelele pe care le descărcați. Cel mai mare model din acest ghid are aproximativ 20 GB.
- **Python 3.10–3.13** (utilizat în secțiunea aplicației Python)
- O conexiune la internet (prin cablu sau wireless)
<!-- @device:halo_box,halo,stx,krk -->
- [Opțional] Un NPU AMD XDNA 2 (Ryzen AI 300/400/Max 300 series sau Z2 Extreme) cu cel mai recent driver instalat din [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) dacă doriți să rulați un model pe NPU.
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

## Concepte de bază — Cum funcționează serverele locale de AI

Înainte de a rula un model, merită să înțelegem *de ce* lucrurile sunt configurate în acest fel. Lemonade este un **server local de modele**, un proces care încarcă modele AI în memorie și le expune aplicațiilor prin HTTP, la fel cum ar face-o un serviciu AI din cloud.

### De ce un server?

| Beneficiu | Ce înseamnă pentru tine |
|---------|----------------------|
| **Integrare simplificată** | Aplicațiile comunică cu un singur API HTTP în loc să folosească biblioteci C++ sau Python specifice hardware-ului. |
| **Modele partajate** | Un singur model încărcat poate deservi mai multe aplicații simultan, fără copii duplicate care să consume RAM-ul. |
| **Portabilitate cloud-la-local** | Codul scris pentru API-ul cloud OpenAI funcționează cu Lemonade prin schimbarea unui singur URL. |
| **Separarea responsabilităților** | Gestionarea modelelor, streaming-ul și toleranța la erori sunt gestionate de server, astfel încât dezvoltatorii se pot concentra pe aplicația lor. |

### Standardul API OpenAI

Lemonade implementează **API-ul OpenAI**, aceeași interfață utilizată de ChatGPT, Azure OpenAI și zeci de alte servicii. Modelul conversației este simplu:

| Rol | Cine vorbește |
|------|---------------|
| **system** | Instrucțiuni pentru model (persona, restricții, instrumente disponibile) |
| **user** | Mesaje de la om (sau aplicație) către model |
| **assistant** | Răspunsuri generate de model |

Aceasta înseamnă că orice bibliotecă sau aplicație care suportă OpenAI poate comunica cu Lemonade prin direcționarea către `http://localhost:13305/api/v1` în timp ce Lemonade Server rulează.

## Activitatea principală — Prima ta conversație AI locală

Haideți să descărcăm un LLM și să purtăm o conversație cu el, rulând AI-ul în întregime pe propriul dispozitiv.

### Pasul 1: Descarcă și rulează un model

Lemonade vine cu o bibliotecă de modele atent selectate. Să începem cu **Gemma-4-E2B-it**, un model capabil și compact care include suport pentru viziune. Deschide un terminal și rulează:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Această comandă unică realizează trei lucruri:

1. **Descarcă** modelul (~3 GB) de pe Hugging Face, dacă acesta nu este deja descărcat. (Poate dura ceva timp)
2. **Pornește** procesul Lemonade Server pe portul 13305.
3. **Deschide Lemonade App** astfel încât să poți începe să discuți cu modelul.
<!-- @os:windows -->
Pe Windows, aplicația Lemonade App pornește automat și puteți începe să discutați imediat. Dacă ați instalat pachetul `minimal.msi`, aplicația nu este inclusă. Pentru a începe să discutați, deschideți browserul web și accesați `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
Pe Linux, deschideți browser-ul și navigați la `http://localhost:13305` pentru a accesa aplicația web.
<!-- @os:end -->
Încearcă să scrii o întrebare:

```
What are three fun facts about lemons?
```

Modelul va răspunde direct în fereastra de chat. **Felicitări! Rulați local un model lingvistic de mari dimensiuni.**

![Lemonade App with Logs displayed](../../dependencies/assets/ChatwithLogs.png)

În panoul Server Logs din Lemonade App, puteți găsi date de telemetrie despre performanța modelului după fiecare răspuns. De exemplu:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Pasul 2: Explorați interfața web și diferitele modalități

Lemonade include o interfață web integrată în care puteți:

- **Interacționa** cu modelul încărcat într-o fereastră de chat familiară
- **Răsfoi modele** în fila Model Manager
- **Descărca modele noi** cu un singur clic

Încercați să comutați între diferite modalități utilizând fila **Model Manager** din interfața web, unde puteți răsfoi modelele după Rețetă (Recipe) sau după Categorie:

1. **Vision:** Modelul `Gemma-4-E2B-it-GGUF` pe care l-ați încărcat deja acceptă vision. Inserați o imagine în caseta de chat și cereți modelului să o descrie.
2. **Generare de imagini:** În categoria Image, descărcați un model de imagine precum `SDXL-Turbo` din Model Manager, apoi utilizați Lemonade Image Generator pentru a introduce un prompt și a genera o imagine local.
3. **Audio:** În categoria Audio, descărcați un model audio precum `Whisper-Tiny`, care poate face conversie voce-text (speech-to-text). Furnizați o înregistrare audio pentru a o transcrie local. Pentru conversie text-voce (text-to-speech), încercați unul dintre modelele din categoria Speech, precum `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### Pasul 3: Încercați un model cu un backend diferit

Dacă poziționați cursorul deasupra unui model în Lemonade App, veți vedea o pictogramă de roată dințată. Făcând clic pe aceasta puteți selecta opțiuni pentru model, inclusiv alegerea backend-ului dorit.

În mod implicit, Lemonade folosește Vulkan pentru accelerare GPU. Dacă aveți un GPU discret AMD compatibil, puteți comuta la ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

Pentru a gestiona backend-urile instalate, faceți clic pe butonul de backend din coloana cea mai din stânga.

Alternativ, puteți specifica backend-ul folosind următoarea comandă:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

De asemenea, puteți seta backend-ul implicit folosind variabila de mediu `LEMONADE_LLAMACPP` cu valorile: `vulkan`, `rocm`, sau `cpu`.

---

## Aprofundare — Construiți o aplicație bazată pe AI cu Python

Adevărata putere a unui server AI local constă în faptul că orice aplicație se poate conecta la el folosind doar câteva linii de cod. Pentru a demonstra acest lucru, să construim un **generator de fișe de studiu (flashcard)** mic, dar funcțional, unde îi dați un subiect, generează fișe de studiu, iar dumneavoastră vă puteți testa interactiv cunoștințele.

### Pasul 4: Porniți serverul

Verificați că serverul Lemonade rulează. De obicei pornește automat în fundal după instalare. Pentru a verifica, rulați:

```
lemonade status
```

Ar trebui să vedeți un mesaj precum: `Server is running on port 13305`.

Dacă serverul nu rulează, porniți-l deschizând aplicația Lemonade. Utilizați portul implicit **13305** (îl puteți confirma sau selecta din pictograma din bara de sistem).

### Pasul 5: Instalați clientul Python OpenAI

Într-un terminal, creați un venv și instalați clientul Python OpenAI folosind următoarele comenzi:
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

### Pasul 6: Construiți aplicația Flashcard

Să descărcăm un model diferit pentru a genera cod: `Qwen3.5-35B-A3B-GGUF`. Acesta este un model mare (~20 GB) și performant, cel mai potrivit pentru sisteme cu 32 GB+ RAM. Dacă aveți mai puțină memorie RAM disponibilă, încercați în schimb `Qwen3.5-9B-GGUF` (~6 GB).

Îl puteți descărca din interfața utilizator sau puteți rula următoarele:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Introduceți următorul prompt în Lemonade Chat UI pentru a genera cod pentru o aplicație Flashcard simplă.

Vom folosi Qwen3.5-35B-A3B-GGUF (un model mai mare, mai bun la scrierea de cod) pentru a genera aplicația noastră Python, iar aplicația în sine va apela Gemma-4-E2B-it-GGUF (modelul mai mic pe care l-ați descărcat deja) la momentul execuției. Codul poate fi apoi copiat într-un fișier la alegere pentru a fi rulat în Python.

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

> **Sugestie**: Am urmat practicile standard de inginerie printr-o creare atentă a promptului și prin utilizarea unui sistem cu două modele pentru a optimiza resursele și viteza.

Pentru comoditatea dumneavoastră, am furnizat un exemplu de rezultat în [`flashcards.py`](assets/flashcards.py). Nu ezitați să îl descărcați în directorul dumneavoastră. În orice caz, ar trebui să aveți acum un fișier Python care poate fi rulat.

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


### Pasul 7: Rulați codul generat

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Iată ce ar trebui să vedeți:**

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

În aproximativ 150 de linii de cod ați construit un instrument de studiu complet funcțional, alimentat de un LLM local. Nu există nicio cheie API de gestionat, niciun cost de utilizare și niciun date care să părăsească vreodată calculatorul dumneavoastră.

> **Observație cheie:** Observați că linia `client = OpenAI(base_url=...) ` este *singurul* lucru care leagă această aplicație de Lemonade în loc de cloud-ul OpenAI. Restul codului este identic cu ceea ce ați scrie pentru orice serviciu compatibil cu OpenAI. Dacă ați folosit vreodată biblioteca Python OpenAI, știți deja cum să construiți aplicații cu Lemonade.

### Ce demonstrează acest lucru

Această aplicație mică pune în practică mai multe modele reale de integrare:

| Model | Unde apare |
|---------|-----------------|
| **Prompturi de sistem** | Mesajul `"system"` îi spune LLM-ului să genereze un output JSON structurat |
| **Output structurat** | Aplicația analizează răspunsul LLM-ului ca JSON pentru a construi fișele de studiu |
| **Cereri fără stare (stateless)** | Fiecare apel `generate_flashcards()` este independent |
| **Gestionarea erorilor** | Blocul `try/except` gestionează elegant cazurile în care output-ul LLM-ului nu este JSON valid |

Aceleași modele se pot extinde la orice aplicație, precum chatboturi, asistenți de cod, generatoare de conținut, instrumente de automatizare.

#### Provocare bonus

* Pentru o provocare suplimentară, încercați să actualizați aplicația astfel încât fișele de studiu să fie citite utilizatorului, făcând referire la exemplul furnizat [aici](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
# Rularea modelelor pe NPU (opțional)

Dacă aveți un Ryzen AI 300/400/Max 300 series sau Z2 Extreme, dispozitivul dvs. are un **Neural Processing Unit (NPU)** integrat, un cip dedicat conceput special pentru sarcini de AI. Rularea modelelor pe NPU este mai eficientă din punct de vedere energetic decât utilizarea GPU-ului, ceea ce o face ideală pentru sarcini AI care rulează în fundal, sesiuni mai lungi și utilizare pe baterie.

Lemonade acceptă trei moduri de execuție NPU, toate fiind transparente în spatele aceluiași API OpenAI:

| Mod | Cum funcționează | Rețetă | Modele exemplu |
|------|-------------|--------|----------------|
| **Hibrid (NPU + iGPU)** | NPU-ul procesează prompt-ul, iGPU-ul generează token-uri | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Doar NPU** | Întreaga inferență rulează pe NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Utilizează motorul FastFlowLM pe NPU, optimizat pentru AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Cerințe

- Procesor **AMD Ryzen AI 300/400 series sau Z2 series**
- Pentru modele **FLM**: Runtime-ul FLM poate fi instalat din aplicația Lemonade sau Lemonade va instala automat runtime-ul FLM la rularea unui model FLM. Pentru a afla mai multe despre FastFlowLM, consultați [aici](https://fastflowlm.com/docs/).


### Pasul 8: Rulați un model Hybrid

Modelele hibride împart munca între NPU și iGPU pentru un echilibru bun între viteză și eficiență. În aplicația Lemonade, selectați un model din lista `Ryzen AI LLM`, de exemplu, `Qwen3-4B-Hybrid`, sau rulați-l folosind următoarea comandă:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade detectează automat NPU-ul dvs. și instalează backend-ul **Ryzen AI LLM**.

> **Ce se întâmplă în culise?** Când trimiteți un mesaj, NPU-ul procesează întregul prompt în paralel (acest lucru se numește „prefill"). Apoi, iGPU-ul preia controlul pentru a genera răspunsul câte un token la un moment dat (acest lucru se numește „decode"). Această abordare hibridă valorifică punctele forte ale fiecărui cip.

### Pasul 9: Rulați un model FLM

Modelele FastFlowLM (FLM) sunt optimizate în mod specific pentru arhitectura NPU XDNA2 a AMD și pot fi foarte rapide raportat la dimensiunea lor. De exemplu, selectați `qwen3.5-4b-FLM` din lista `FastFlowLM NPU` sau utilizați următoarea comandă:

<!-- @os:windows -->
Pentru a activa `FastFlowLM` pe Windows:

* Deschideți meniul `Backends Manager`.
* Localizați categoria backend `FastFlowLM NPU`.
* Faceți clic pe Install NPU.
* Odată ce instalarea este completă, aproximativ 36 de modele implicite vor fi disponibile în meniul derulant FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Când aplicația `Lemonade` este lansată pentru prima dată, backend-ul `FastFlowNPU` nu este activat implicit. 
Aplicația locală va deschide pagina de instalare pentru a vă ghida prin procesul de configurare.

Pentru a activa `FastFlowLM` pe Linux:

* Deschideți aplicația `Lemonade`.
* Vizitați documentația [oficială FLM](https://lemonade-server.ai/flm_npu_linux.html) și urmați pașii de instalare pentru FLM selectând distribuția dvs. Linux.
* Activați backports conform instrucțiunilor de pe pagina de instalare.
* Descărcați cea mai recentă versiune `v0.9.x` de pe [pagina de tag-uri](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Pentru AMD Halo Developer Platform, asigurați-vă că alegeți Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Instalați pachetul `.deb` descărcat.
* Recomandat: Închideți aplicația `Lemonade App` și deschideți-o din nou pentru ca modificările să fie detectate.
* Recomandat: Deschideți `Backends Manager` și faceți clic pe Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
După o instalare reușită, ar trebui să vedeți că `flm:npu` s-a finalizat în **Download Manager** din interiorul **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Puteți apoi selecta oricare dintre modelele FFLM disponibile și puteți începe să utilizați backend-ul NPU.

Pentru un model specific, descărcați modelul dorit de pe [pagina de modele](https://fastflowlm.com/docs/models/qwen/) și validați-l folosind comanda Shell furnizată în documentație.
```
flm run qwen3.5-4b-FLM
```
sau prin 
```
lemonade run qwen3.5-4b-FLM
```

Modelele FLM includ unele dintre cele mai populare arhitecturi (Gemma 3, Qwen 3, Llama 3 și DeepSeek R1) și variază de la sub 1 GB la peste 13 GB.
Lemonade detectează automat NPU-ul dvs. și instalează backend-ul **FastFlowLM NPU**.

<!-- @os:windows -->
> **Sfat:** Pentru cea mai bună performanță NPU, activați modul turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Schimbarea modelelor

Aplicația de flashcard-uri din Pasul 6 funcționează și cu modele NPU, doar schimbați numele modelului:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Pași următori

Aveți un server AI local care rulează pe propriul dvs. hardware, iată unde puteți merge în continuare:

1. **Conectați aplicațiile dvs. preferate**: Lemonade funcționează din start cu [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) și [multe altele](https://lemonade-server.ai/marketplace).

2. **Explorați mai multe modele**: Explorați [biblioteca completă de modele](https://lemonade-server.ai/docs/server/server_models/) pentru a găsi modele optimizate pentru programare, raționament, viziune și multe altele. Utilizați aplicația Lemonade sau `lemonade list` pentru a vedea ce este disponibil.

3. **Deblocați accelerarea GPU ROCm**: Dacă aveți un GPU AMD compatibil, comutați la backend-ul ROCm: `lemonade config set llamacpp.backend=rocm`. Consultați [GPU-urile AMD compatibile](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Citiți specificația API completă**: Lemonade acceptă chat completions, embeddings, transcriere audio, generare de imagini, text-to-speech și multe altele. Consultați [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) pentru fiecare endpoint.

5. **Contribuiți**: Lemonade este open source. Consultați [ghidul de contribuție](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) și căutați [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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