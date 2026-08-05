<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Panoramica

🍋 **Lemonade** è un server AI locale open-source che ti permette di eseguire modelli linguistici di grandi dimensioni (LLM), generatori di immagini e modelli audio direttamente sul tuo hardware. Espone i modelli tramite l'**OpenAI API**, lo standard di riferimento del settore, in modo che qualsiasi app compatibile con OpenAI possa funzionare istantaneamente con Lemonade. Alla fine di questo playbook, utilizzerai Lemonade per eseguire modelli localmente sul tuo computer.

## Cosa imparerai

Alla fine di questo playbook sarai in grado di:

* **Installare Lemonade Server** e verificare che sia in esecuzione.
* **Scaricare e chattare con un LLM** utilizzando un singolo comando.
* **Esplorare la web UI** e provare diverse modalità come visione, riconoscimento vocale e generazione di immagini.
* **Passare da un backend GPU all'altro** tra Vulkan e AMD ROCm™ software.
* **Creare un'app Python** basata su un LLM locale utilizzando l'API compatibile con OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Eseguire modelli sull'AMD Neural Processing Unit (NPU)** utilizzando le modalità di esecuzione Hybrid e FLM su hardware AMD Ryzen™ AI.
<!-- @device:end -->

## Impostazione della configurazione della memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli aggiornamenti software

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei prerequisiti software

Prima di iniziare, assicurati di avere:

- Un PC con **Windows 11** o una distribuzione **Linux** supportata (Ubuntu 24.04+, Fedora, Debian)
- Sono consigliati **16 GB di RAM** per il modello di runtime utilizzato nei passaggi da 1 a 7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). Sono consigliati **32 GB+** se desideri utilizzare il modello di generazione di codice più grande nel passaggio 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB di spazio libero su disco**, a seconda dei modelli scaricati. Il modello più grande in questa guida è di circa 20 GB.
- **Python 3.10–3.13** (utilizzato nella sezione dedicata all'app Python)
- Una connessione internet (cablata o wireless)
<!-- @device:halo_box,halo,stx,krk -->
- [Opzionale] Un AMD XDNA 2 NPU (Ryzen AI serie 300/400/Max 300 o Z2 Extreme) con l'ultimo driver installato da [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) se desideri eseguire un modello sull'NPU.
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
```bash
winget upgrade -e --id AMD.LemonadeServer
lemonade --version
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

## Concetti fondamentali — Come funzionano i server AI locali

Prima di eseguire un modello, è utile capire *perché* le cose sono impostate in questo modo. Lemonade è un **server di modelli locale**, un processo che carica i modelli AI in memoria e li espone alle applicazioni tramite HTTP, proprio come farebbe un servizio AI in cloud.

### Perché un server?

| Vantaggio | Cosa significa per te |
|---------|----------------------|
| **Integrazione semplificata** | Le app comunicano con un'unica API HTTP invece di gestire librerie C++ o Python specifiche per l'hardware. |
| **Modelli condivisi** | Un unico modello caricato può servire più app contemporaneamente, senza copie duplicate che occupano la tua RAM. |
| **Portabilità dal cloud al locale** | Il codice scritto per l'API cloud di OpenAI funziona con Lemonade semplicemente cambiando un URL. |
| **Separazione delle responsabilità** | La gestione dei modelli, lo streaming e la tolleranza agli errori sono gestiti dal server, così gli sviluppatori possono concentrarsi sulla propria app. |

### Lo standard OpenAI API

Lemonade implementa l'**OpenAI API**, la stessa interfaccia utilizzata da ChatGPT, Azure OpenAI e decine di altri servizi. Il modello di conversazione è semplice:

| Ruolo | Chi sta parlando |
|------|---------------|
| **system** | Istruzioni per il modello (persona, vincoli, strumenti disponibili) |
| **user** | Messaggi inviati dall'utente umano (o dall'applicazione) al modello |
| **assistant** | Risposte generate dal modello |

Questo significa che qualsiasi libreria o app che supporta OpenAI può comunicare con Lemonade puntando a `http://localhost:13305/api/v1` mentre Lemonade Server è in esecuzione.

## Attività principale — La tua prima chat AI locale

Scarichiamo un LLM e avviamo una conversazione con esso, eseguendo l'AI interamente sul tuo computer.

### Passaggio 1: Scaricare ed eseguire un modello

Lemonade viene fornito con una libreria di modelli curata. Iniziamo con **Gemma-4-E2B-it**, un modello compatto e capace che include il supporto per la visione. Apri un terminale ed esegui:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Questo singolo comando esegue tre operazioni:

1. **Scarica** il modello (~3 GB) da Hugging Face, se non è già stato scaricato. (Potrebbe richiedere del tempo)
2. **Avvia** il processo di Lemonade Server sulla porta 13305.
3. **Apre Lemonade App** in modo da poter iniziare a chattare con il modello.


<!-- @os:windows -->
Su Windows, Lemonade App si avvia automaticamente e puoi iniziare subito a chattare. Se hai installato il pacchetto `minimal.msi`, l'app non è inclusa. Per iniziare a chattare, apri il tuo browser web e vai su `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
Su Linux, apri il tuo browser e naviga su `http://localhost:13305` per accedere alla web app.
<!-- @os:end -->

Prova a digitare una domanda:

```
What are three fun facts about lemons?
```

Il modello risponderà direttamente nella finestra della chat. **Congratulazioni! Stai eseguendo un modello linguistico di grandi dimensioni in locale.**

![Lemonade App con i log visualizzati](../../dependencies/assets/ChatwithLogs.png)

Nel pannello Server Logs di Lemonade App, puoi trovare i dati di telemetria sulle prestazioni del modello dopo ogni risposta. Ad esempio:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Passaggio 2: Esplora l'interfaccia web e le diverse modalità

Lemonade include un'interfaccia web integrata dove puoi:

- **Interagire** con il modello caricato in una familiare finestra di chat
- **Sfogliare i modelli** nella scheda Model Manager
- **Scaricare nuovi modelli** con un clic

Prova a passare tra diverse modalità utilizzando la scheda **Model Manager** nell'interfaccia web, dove puoi sfogliare i modelli per Recipe o per Categoria:

1. **Visione:** Il modello `Gemma-4-E2B-it-GGUF` che hai già caricato supporta la visione. Incolla un'immagine nella casella di chat e chiedi al modello di descriverla.
2. **Generazione di immagini:** Nella categoria Image, scarica un modello di immagini come `SDXL-Turbo` dal Model Manager, quindi usa il Lemonade Image Generator per digitare un prompt e generare un'immagine localmente.
3. **Audio:** Nella categoria Audio, scarica un modello audio come `Whisper-Tiny`, che può eseguire il riconoscimento vocale (speech-to-text). Fornisci una registrazione audio per trascriverla localmente. Per la sintesi vocale (text-to-speech), prova uno dei modelli nella categoria Speech, come `kokoro-v1`.

![Multi-Modalità con Lemonade](../../dependencies/assets/multi_modality.png)

### Passaggio 3: Prova un modello con un backend diverso

Se passi il mouse su un modello nell'app Lemonade, vedrai un'icona a forma di ingranaggio. Facendo clic su di essa puoi selezionare le opzioni per il modello, incluso la scelta del backend desiderato.

Per impostazione predefinita, Lemonade utilizza Vulkan per l'accelerazione GPU. Se disponi di una GPU discreta AMD supportata, puoi passare a ROCm.

![Selezione backend Lemonade](../../dependencies/assets/lemonademodeloptions.png)

Per gestire i backend installati, fai clic sul pulsante del backend nella colonna più a sinistra.

In alternativa, puoi specificare il backend utilizzando il seguente comando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Puoi anche impostare il backend predefinito utilizzando la variabile d'ambiente `LEMONADE_LLAMACPP` con i valori: `vulkan`, `rocm` o `cpu`.

---

## Andare più a fondo — Crea un'app basata su AI con Python

Il vero punto di forza di un server AI locale è che qualsiasi applicazione può connettersi ad esso utilizzando solo poche righe di codice. Per dimostrarlo, costruiamo un piccolo ma funzionale **generatore di flashcard per lo studio** in cui fornisci un argomento, questo genera le flashcard, e puoi metterti alla prova in modo interattivo.

### Passaggio 4: Avvia il server

Verifica che il server Lemonade sia in esecuzione. Solitamente si avvia automaticamente in background dopo l'installazione. Per verificarlo, esegui:

```
lemonade status
```

Dovresti vedere un messaggio simile a: `Server is running on port 13305`.

Se il server non è in esecuzione, avvialo aprendo l'app Lemonade. Usa la porta predefinita **13305** (puoi confermarla o selezionarla dall'icona nella barra delle applicazioni).

### Passaggio 5: Installa il client Python OpenAI

In un terminale, crea un venv e installa il client Python OpenAI utilizzando i seguenti comandi:
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

### Passaggio 6: Costruisci l'app Flashcard

Scarichiamo un modello diverso per generare codice: `Qwen3.5-35B-A3B-GGUF`. Si tratta di un modello grande (~20 GB) e performante, più adatto a sistemi con 32 GB+ di RAM. Se hai meno RAM disponibile, prova invece `Qwen3.5-9B-GGUF` (~6 GB).

Puoi scaricarlo dall'interfaccia utente oppure eseguire il seguente comando:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Inserisci il seguente prompt nella Lemonade Chat UI per generare il codice di una semplice app Flashcard.

Useremo Qwen3.5-35B-A3B-GGUF (un modello più grande, più abile nella scrittura di codice) per generare la nostra app Python, e l'app stessa chiamerà Gemma-4-E2B-it-GGUF (il modello più piccolo che hai già scaricato) durante l'esecuzione. Il codice può quindi essere copiato in un file a tua scelta per essere eseguito in Python.

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

> **Suggerimento**: Abbiamo seguito le pratiche ingegneristiche standard attraverso una creazione accurata del prompt e utilizzando un sistema a due modelli per ottimizzare risorse e velocità.

Per tua comodità, abbiamo fornito un esempio di output in [`flashcards.py`](assets/flashcards.py). Sentiti libero di scaricarlo nella tua directory. In entrambi i casi, ora dovresti avere un file Python pronto per essere eseguito.

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


### Passaggio 7: Esegui il codice generato

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Ecco cosa dovresti vedere:**

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

In circa 150 righe di codice hai costruito uno strumento di studio completamente funzionale basato su un LLM locale. Non c'è nessuna chiave API da gestire, nessun costo di utilizzo, e nessun dato lascia mai il tuo computer.

> **Punto chiave:** Nota che la riga `client = OpenAI(base_url=...) ` è l'*unica* cosa che collega questa app a Lemonade invece che al cloud di OpenAI. Il resto del codice è identico a quello che scriveresti per qualsiasi servizio compatibile con OpenAI. Se hai mai usato la libreria Python di OpenAI, sai già come costruire app con Lemonade.

### Cosa dimostra questo esempio

Questa piccola app illustra diversi pattern di integrazione reali:

| Pattern | Dove appare |
|---------|-----------------|
| **Prompt di sistema** | Il messaggio `"system"` indica all'LLM di produrre un output JSON strutturato |
| **Output strutturato** | L'app analizza la risposta dell'LLM come JSON per costruire le flashcard |
| **Richieste stateless** | Ogni chiamata a `generate_flashcards()` è indipendente |
| **Gestione degli errori** | Il blocco `try/except` gestisce con eleganza i casi in cui l'output dell'LLM non è JSON valido |

Questi stessi pattern si adattano a qualsiasi applicazione, come chatbot, assistenti per il codice, generatori di contenuti, strumenti di automazione.

#### Sfida bonus

* Per una sfida in più, prova ad aggiornare l'app in modo che le flashcard vengano lette all'utente, facendo riferimento all'esempio fornito [qui](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Esecuzione di modelli sulla NPU (opzionale)

Se possiedi un dispositivo Ryzen AI serie 300/400/Max 300 o Z2 Extreme, il tuo dispositivo dispone di una **Neural Processing Unit (NPU)** integrata, un chip dedicato progettato specificamente per i carichi di lavoro AI. Eseguire modelli sulla NPU è più efficiente dal punto di vista energetico rispetto all'utilizzo della GPU, il che la rende ideale per attività AI in background, sessioni prolungate e utilizzo a batteria.

Lemonade supporta tre modalità di esecuzione NPU, tutte trasparenti dietro la stessa OpenAI API:

| Modalità | Come Funziona | Recipe | Modelli di Esempio |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | La NPU elabora il prompt, la iGPU genera i token | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Solo NPU** | L'intera inferenza viene eseguita sulla NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Utilizza il motore FastFlowLM sulla NPU, ottimizzato per AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Requisiti

- Processore **AMD Ryzen AI serie 300/400 o Z2**
- Per i modelli **FLM**: il runtime FLM può essere installato dall'interno dell'app Lemonade, oppure Lemonade installerà automaticamente il runtime FLM quando esegui un modello FLM. Per saperne di più su FastFlowLM, consulta [qui](https://fastflowlm.com/docs/).


### Passaggio 8: Esegui un modello Hybrid

I modelli Hybrid suddividono il lavoro tra la NPU e la iGPU per un buon equilibrio tra velocità ed efficienza. Nell'app Lemonade, seleziona un modello dall'elenco `Ryzen AI LLM`, ad esempio `Qwen3-4B-Hybrid`, oppure eseguilo utilizzando il seguente comando:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade rileva automaticamente la tua NPU e installa il backend **Ryzen AI LLM**.

> **Cosa succede dietro le quinte?** Quando invii un messaggio, la NPU elabora l'intero prompt in parallelo (questo processo si chiama "prefill"). Poi, la iGPU subentra per generare la risposta un token alla volta (questo processo si chiama "decode"). Questo approccio ibrido sfrutta i punti di forza di ciascun chip.

### Passaggio 9: Esegui un modello FLM

I modelli FastFlowLM (FLM) sono specificamente ottimizzati per l'architettura NPU XDNA2 di AMD e possono essere molto veloci rispetto alle loro dimensioni. Ad esempio, seleziona `qwen3.5-4b-FLM` dall'elenco `FastFlowLM NPU` oppure utilizza il seguente comando:

<!-- @os:windows -->
Per abilitare `FastFlowLM` su Windows:

* Apri il menu `Backends Manager`.
* Individua la categoria del backend `FastFlowLM NPU`.
* Fai clic su Install NPU.
* Una volta completata l'installazione, saranno disponibili circa 36 modelli predefiniti nel menu a discesa FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Quando l'app `Lemonade` viene avviata per la prima volta, il backend `FastFlowNPU` non è abilitato per impostazione predefinita.
L'app locale aprirà la pagina di installazione per guidarti attraverso la configurazione.

Per abilitare `FastFlowLM` su Linux:

* Apri l'app `Lemonade`.
* Visita la documentazione [ufficiale FLM](https://lemonade-server.ai/flm_npu_linux.html) e segui i passaggi di installazione per FLM selezionando la tua distribuzione Linux.
* Abilita i backports come indicato nella pagina di installazione.
* Scarica l'ultima release `v0.9.x` dalla [pagina dei tag](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Nota]
Per la piattaforma AMD Halo Developer, assicurati di scegliere Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Installa il pacchetto `.deb` scaricato.
* Consigliato: chiudi la `Lemonade App` e riaprila in modo che le modifiche vengano rilevate.
* Consigliato: apri `Backends Manager` e fai clic su Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Dopo un'installazione riuscita, dovresti vedere che `flm:npu` è stato completato in **Download Manager** all'interno della **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Puoi quindi selezionare uno qualsiasi dei modelli FFLM disponibili e iniziare a utilizzare il backend NPU.

Per un modello specifico, scarica il modello desiderato dalla [pagina dei modelli](https://fastflowlm.com/docs/models/qwen/) e convalidalo utilizzando il comando Shell fornito nella documentazione.
```
flm run qwen3.5-4b-FLM
```
oppure tramite 
```
lemonade run qwen3.5-4b-FLM
```

I modelli FLM includono alcune delle architetture più popolari (Gemma 3, Qwen 3, Llama 3 e DeepSeek R1) e vanno da meno di 1 GB a oltre 13 GB.
Lemonade rileva automaticamente la tua NPU e installa il backend **FastFlowLM NPU**.

<!-- @os:windows -->
> **Suggerimento:** per prestazioni NPU ottimali, abilita la modalità turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Cambio di Modelli

L'app di flashcard del Passaggio 6 funziona anche con i modelli NPU, basta cambiare il nome del modello:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Prossimi Passi

Ora hai un server AI locale in esecuzione sul tuo hardware, ecco dove andare avanti:

1. **Collega le tue app preferite**: Lemonade funziona immediatamente con [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) e [molte altre](https://lemonade-server.ai/marketplace).

2. **Esplora altri modelli**: esplora la [libreria completa dei modelli](https://lemonade-server.ai/docs/server/server_models/) per trovare modelli ottimizzati per programmazione, ragionamento, visione e altro ancora. Usa la Lemonade App o `lemonade list` per vedere cosa è disponibile.

3. **Sblocca l'accelerazione GPU ROCm**: se possiedi una GPU AMD supportata, passa al backend ROCm: `lemonade config set llamacpp.backend=rocm`. Consulta le [GPU AMD supportate](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Leggi le specifiche complete dell'API**: Lemonade supporta chat completions, embeddings, trascrizione audio, generazione di immagini, sintesi vocale e altro ancora. Consulta la [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) per ogni endpoint.

5. **Contribuisci**: Lemonade è open source. Consulta la [guida ai contributi](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) e cerca le [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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