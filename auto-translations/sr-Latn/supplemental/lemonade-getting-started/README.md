<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ovaj priručnik koristi posebne oznake koje GitHub ne može da prikaže. Posetite [amd.com/playbooks](https://amd.com/playbooks) da biste ispravno pregledali ovaj sadržaj.
<!-- @github-only:end -->

## Pregled

🍋 **Lemonade** je open-source lokalni AI server koji vam omogućava da pokrećete velike jezičke modele (LLM-ove), generatore slika i audio modele direktno na sopstvenom hardveru. Modeli se izlažu putem industrijskog standarda **OpenAI API**, tako da svaka aplikacija koja radi sa OpenAI-jem može odmah da radi i sa Lemonade-om. Do kraja ovog priručnika koristićete Lemonade za pokretanje modela lokalno na vašem računaru.

## Šta ćete naučiti

Do kraja ovog priručnika bićete u mogućnosti da:

* **Instalirate Lemonade Server** i proverite da li radi.
* **Preuzmete i ćaskate sa LLM-om** koristeći jednu komandu.
* **Istražite web korisnički interfejs** i isprobate različite modalitete kao što su vid, pretvaranje govora u tekst i generisanje slika.
* **Prebacujete GPU pozadinske sisteme** između Vulkan-a i AMD ROCm™ softvera.
* **Napravite Python aplikaciju** pokretanu lokalnim LLM-om koristeći OpenAI-kompatibilan API.
<!-- @device:halo_box,halo,stx,krk -->
* **Pokrenete modele na AMD Neural Processing Unit (NPU)** koristeći Hybrid i FLM režime izvršavanja na AMD Ryzen™ AI hardveru.
<!-- @device:end -->

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje potrebnog softvera

Pre nego što počnete, uverite se da imate:

- Računar sa operativnim sistemom **Windows 11** ili podržanom **Linux** distribucijom (Ubuntu 24.04+, Fedora, Debian)
- Preporučuje se **16 GB RAM-a** za runtime model korišćen u koracima 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** se preporučuje ako želite da koristite veći model za generisanje koda u koraku 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB slobodnog prostora na disku**, u zavisnosti od modela koje preuzimate. Najveći model u ovom vodiču ima oko 20 GB.
- **Python 3.10–3.13** (koristi se u delu o Python aplikaciji)
- Internet konekcija (žična ili bežična)
<!-- @device:halo_box,halo,stx,krk -->
- [Opciono] AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 serija ili Z2 Extreme) sa najnovijim upravljačkim programom instaliranim sa [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) ako želite da pokrenete model na NPU-u.
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

## Osnovni koncepti — Kako funkcionišu lokalni AI serveri

Pre nego što pokrenemo model, vredi razumeti *zašto* je sve postavljeno na ovaj način. Lemonade je **lokalni server za modele**, proces koji učitava AI modele u memoriju i izlaže ih aplikacijama putem HTTP-a, baš kao što bi to radila i neka cloud AI usluga.

### Zašto server?

| Prednost | Šta to znači za vas |
|---------|----------------------|
| **Pojednostavljena integracija** | Aplikacije komuniciraju sa jednim HTTP API-jem umesto da se bave hardverski specifičnim C++ ili Python bibliotekama. |
| **Deljeni modeli** | Jedan učitani model može da opslužuje više aplikacija istovremeno, bez dupliranih kopija koje troše vaš RAM. |
| **Prenosivost sa cloud-a na lokalno** | Kod napisan za OpenAI-jev cloud API radi sa Lemonade-om uz izmenu samo jednog URL-a. |
| **Razdvajanje odgovornosti** | Upravljanje modelima, striming i tolerancija na greške obrađuju se od strane servera, tako da programeri mogu da se fokusiraju na svoju aplikaciju. |

### OpenAI API standard

Lemonade implementira **OpenAI API**, isti interfejs koji koriste ChatGPT, Azure OpenAI i desetine drugih usluga. Model konverzacije je jednostavan:

| Uloga | Ko govori |
|------|---------------|
| **system** | Instrukcije za model (persona, ograničenja, dostupni alati) |
| **user** | Poruke od čoveka (ili aplikacije) upućene modelu |
| **assistant** | Odgovori koje generiše model |

Ovo znači da bilo koja biblioteka ili aplikacija koja podržava OpenAI može da komunicira sa Lemonade-om usmeravanjem na `http://localhost:13305/api/v1` dok Lemonade Server radi.

## Glavna aktivnost — Vaš prvi lokalni AI razgovor

Hajde da preuzmemo LLM i vodimo razgovor sa njim, pokrećući AI u potpunosti na vašoj sopstvenoj mašini.

### Korak 1: Preuzmite i pokrenite model

Lemonade dolazi sa pažljivo odabranom bibliotekom modela. Počnimo sa **Gemma-4-E2B-it**, sposobnim i kompaktnim modelom koji uključuje podršku za vid. Otvorite terminal i pokrenite:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Ova jedna komanda radi tri stvari:

1. **Preuzima** model (~3 GB) sa Hugging Face, ako već nije preuzet. (Može potrajati)
2. **Pokreće** proces Lemonade Server na portu 13305.
3. **Otvara Lemonade App** kako biste mogli odmah da počnete da ćaskate sa modelom.


<!-- @os:windows -->
Na Windows-u, Lemonade App se pokreće automatski i možete odmah početi da ćaskate. Ako ste instalirali `minimal.msi` paket, aplikacija nije uključena. Da biste počeli da ćaskate, otvorite svoj veb pregledač i idite na `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
Na Linux-u, otvorite pregledač i idite na `http://localhost:13305` da biste pristupili web aplikaciji.
<!-- @os:end -->

Pokušajte da otkucate pitanje:

```
What are three fun facts about lemons?
```

Model će odgovoriti direktno u prozoru za ćaskanje. **Čestitamo! Pokrećete veliki jezički model lokalno.**

![Lemonade App sa prikazanim logovima](../../dependencies/assets/ChatwithLogs.png)

U oknu Server Logs u Lemonade App-u, možete pronaći telemetrijske podatke o performansama modela nakon svakog odgovora. Na primer:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Korak 2: Istražite veb-interfejs i različite modalitete

Lemonade uključuje ugrađeni veb-interfejs u kojem možete da:

- **Komunicirate** sa učitanim modelom u poznatom prozoru za ćaskanje
- **Pregledate modele** na kartici Model Manager
- **Preuzimate nove modele** jednim klikom

Pokušajte da prebacujete između različitih modaliteta koristeći karticu **Model Manager** u veb UI-ju, gde možete pregledati modele po Recipe ili po Category:

1. **Vision:** Model `Gemma-4-E2B-it-GGUF` koji ste već učitali podržava vision. Nalepite sliku u polje za ćaskanje i zamolite model da je opiše.
2. **Generisanje slika:** U kategoriji Image, preuzmite model za slike kao što je `SDXL-Turbo` iz Model Manager-a, a zatim koristite Lemonade Image Generator da unesete upit i lokalno generišete sliku.
3. **Zvuk:** U kategoriji Audio, preuzmite audio model kao što je `Whisper-Tiny`, koji može da pretvara govor u tekst. Obezbedite audio snimak da biste ga lokalno transkribovali. Za pretvaranje teksta u govor, isprobajte jedan od modela u kategoriji Speech, kao što je `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### Korak 3: Isprobajte model sa drugačijim bekendom

Ako pređete mišem preko modela u Lemonade App, videćete ikonicu zupčanika. Klikom na nju možete izabrati opcije za model, uključujući izbor željenog bekenda.

Podrazumevano, Lemonade koristi Vulkan za GPU akceleraciju. Ako imate podržan AMD diskretni GPU, možete se prebaciti na ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

Da biste upravljali instaliranim bekendima, kliknite na dugme za bekend u krajnjoj levoj koloni.

Alternativno, možete odrediti bekend koristeći sledeću komandu:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Podrazumevani bekend takođe možete podesiti pomoću promenljive okruženja `LEMONADE_LLAMACPP` sa vrednostima: `vulkan`, `rocm` ili `cpu`.

---

## Idemo dublje — Napravite AI aplikaciju uz pomoć Python-a

Prava snaga lokalnog AI servera je u tome što se bilo koja aplikacija može povezati na njega koristeći samo nekoliko linija koda. Da bismo to dokazali, napravimo mali, ali funkcionalan **generator kartica za učenje (flashcard)**, gde mu date temu, on generiše kartice, a vi sebe možete interaktivno ispitivati.

### Korak 4: Pokrenite server

Proverite da li je Lemonade server pokrenut. Obično se automatski pokreće u pozadini nakon instalacije. Da biste proverili, pokrenite:

```
lemonade status
```

Trebalo bi da vidite poruku poput: `Server is running on port 13305`.

Ako server nije pokrenut, pokrenite ga otvaranjem Lemonade aplikacije. Koristite podrazumevani port **13305** (možete ga potvrditi ili izabrati sa ikonice u traci).

### Korak 5: Instalirajte OpenAI Python klijent

U terminalu, kreirajte venv i instalirajte OpenAI Python klijent koristeći sledeće komande:
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

### Korak 6: Napravite aplikaciju za kartice za učenje

Preuzmimo drugačiji model za generisanje koda: `Qwen3.5-35B-A3B-GGUF`. Ovo je veliki (~20 GB) i performantan model, najpogodniji za sisteme sa 32 GB+ RAM-a. Ako imate manje dostupnog RAM-a, umesto njega isprobajte `Qwen3.5-9B-GGUF` (~6 GB).

Možete ga preuzeti iz UI-ja ili pokrenuti sledeće:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Unesite sledeći upit u Lemonade Chat UI da biste generisali kod za jednostavnu aplikaciju za kartice za učenje (Flashcard app).

Koristićemo Qwen3.5-35B-A3B-GGUF (veći model koji je bolji u pisanju koda) da generišemo našu Python aplikaciju, dok će sama aplikacija tokom izvršavanja pozivati Gemma-4-E2B-it-GGUF (manji model koji ste već preuzeli). Kod se zatim može kopirati u fajl po vašem izboru da bi se pokrenuo u Python-u.

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

> **Savet**: Poštovali smo standardne inženjerske prakse kroz temeljno kreiranje upita i korišćenjem sistema sa dva modela radi optimizacije resursa i brzine.

Radi vaše praktičnosti, obezbedili smo primer izlaza u fajlu [`flashcards.py`](assets/flashcards.py). Slobodno ga preuzmite u svoj direktorijum. U svakom slučaju, sada biste trebalo da imate Python fajl koji se može pokrenuti.

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


### Korak 7: Pokrenite generisani kod

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Evo šta bi trebalo da vidite:**

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

U oko 150 linija koda napravili ste potpuno funkcionalan alat za učenje pokretan lokalnim LLM-om. Nema API ključa kojim treba upravljati, nema troškova korišćenja, i nikakvi podaci nikada ne napuštaju vaš uređaj.

> **Ključni uvid:** Primetite da je linija `client = OpenAI(base_url=...) ` *jedina* stvar koja povezuje ovu aplikaciju sa Lemonade umesto sa OpenAI-jevim oblakom (cloud). Ostatak koda je identičan onome što biste napisali za bilo koju uslugu kompatibilnu sa OpenAI-jem. Ako ste ikada koristili OpenAI Python biblioteku, već znate kako da pravite aplikacije uz pomoć Lemonade.

### Šta ovo pokazuje

Ova mala aplikacija demonstrira nekoliko obrazaca integracije iz stvarnog sveta:

| Obrazac | Gde se pojavljuje |
|---------|-----------------|
| **Sistemski upiti** | Poruka `"system"` govori LLM-u da izlazni podatak bude u strukturisanom JSON formatu |
| **Strukturisan izlaz** | Aplikacija parsira odgovor LLM-a kao JSON da bi napravila kartice za učenje |
| **Zahtevi bez stanja (stateless)** | Svaki poziv `generate_flashcards()` je nezavisan |
| **Rukovanje greškama** | Blok `try/except` glatko rukuje slučajevima kada izlaz LLM-a nije validan JSON |

Isti ovi obrasci se skaliraju na bilo koju aplikaciju, poput chatbot-ova, asistenata za kod, generatora sadržaja, alata za automatizaciju.

#### Bonus izazov

* Za dodatni izazov, pokušajte da ažurirate aplikaciju tako da kartice budu pročitane korisniku naglas, koristeći kao referencu primer dostupan [ovde](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Pokretanje modela na NPU-u (opciono)

Ako imate Ryzen AI 300/400/Max 300 seriju ili Z2 Extreme, vaš uređaj ima ugrađenu **Neural Processing Unit (NPU)**, namenski čip dizajniran posebno za AI opterećenja. Pokretanje modela na NPU-u je energetski efikasnije nego korišćenje GPU-a, što ga čini idealnim za AI zadatke u pozadini, duže sesije i rad na baterijsko napajanje.

Lemonade podržava tri režima izvršavanja na NPU-u, potpuno transparentno iza istog OpenAI API-ja:

| Režim | Kako funkcioniše | Recept | Primeri modela |
|------|-------------|--------|----------------|
| **Hibridni (NPU + iGPU)** | NPU obrađuje prompt, iGPU generiše tokene | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Samo NPU** | Celokupno zaključivanje se izvršava na NPU-u | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Koristi FastFlowLM engine na NPU-u, optimizovano za AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Zahtevi

- **AMD Ryzen AI 300/400 serija ili Z2 serija** procesor
- Za **FLM** modele: FLM runtime se može instalirati iz same Lemonade aplikacije ili će Lemonade automatski instalirati FLM runtime prilikom pokretanja FLM modela. Da biste saznali više o FastFlowLM-u, pogledajte [ovde](https://fastflowlm.com/docs/).


### Korak 8: Pokretanje hibridnog modela

Hibridni modeli dele posao između NPU-a i iGPU-a radi dobrog balansa brzine i efikasnosti. U Lemonade aplikaciji, izaberite model sa liste `Ryzen AI LLM`, na primer, `Qwen3-4B-Hybrid`, ili ga pokrenite pomoću sledeće komande:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade automatski detektuje vaš NPU i instalira **Ryzen AI LLM** backend.

> **Šta se dešava u pozadini?** Kada pošaljete poruku, NPU paralelno obrađuje ceo vaš prompt (ovo se naziva "prefill"). Zatim, iGPU preuzima kontrolu da generiše odgovor token po token (ovo se naziva "decode"). Ovaj hibridni pristup koristi prednosti svakog čipa.

### Korak 9: Pokretanje FLM modela

FastFlowLM (FLM) modeli su posebno optimizovani za AMD-ovu XDNA2 NPU arhitekturu i mogu biti veoma brzi u odnosu na svoju veličinu. Na primer, izaberite `qwen3.5-4b-FLM` sa liste `FastFlowLM NPU` ili koristite sledeću komandu:

<!-- @os:windows -->
Da biste omogućili `FastFlowLM` na Windows-u:

* Otvorite meni `Backends Manager`.
* Pronađite kategoriju backend-a `FastFlowLM NPU`.
* Kliknite Install NPU.
* Nakon što se instalacija završi, ~36 podrazumevanih modela biće dostupno u padajućem meniju FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Kada se aplikacija `Lemonade` pokrene prvi put, backend `FastFlowNPU` nije podrazumevano omogućen.
Lokalna aplikacija će otvoriti stranicu za instalaciju kako bi vas provela kroz podešavanje.

Da biste omogućili `FastFlowLM` na Linux-u:

* Otvorite `Lemonade` aplikaciju.
* Posetite [zvaničnu FLM](https://lemonade-server.ai/flm_npu_linux.html) dokumentaciju i pratite korake instalacije za FLM tako što ćete odabrati svoju Linux distribuciju.
* Omogućite backports prema uputstvu na stranici za instalaciju.
* Preuzmite najnovije `v0.9.x` izdanje sa [stranice sa oznakama (tags)](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Za AMD Halo Developer Platform, obavezno izaberite Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Instalirajte preuzeti `.deb` paket.
* Preporučeno: Zatvorite `Lemonade App` i ponovo je otvorite kako bi se promene detektovale.
* Preporučeno: Otvorite `Backends Manager` i kliknite Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Nakon uspešne instalacije, trebalo bi da vidite da je `flm:npu` završen u **Download Manager**-u unutar **Lemonade Desktop App**-a.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Zatim možete izabrati bilo koji od dostupnih FFLM modela i početi da koristite NPU backend.

Za određeni model, preuzmite željeni model sa [stranice sa modelima](https://fastflowlm.com/docs/models/qwen/) i proverite ga koristeći Shell komandu datu u dokumentaciji.
```
flm run qwen3.5-4b-FLM
```
ili putem 
```
lemonade run qwen3.5-4b-FLM
```

FLM modeli uključuju neke od najpopularnijih arhitektura (Gemma 3, Qwen 3, Llama 3 i DeepSeek R1) i kreću se od manje od 1 GB do preko 13 GB.
Lemonade automatski detektuje vaš NPU i instalira **FastFlowLM NPU** backend.

<!-- @os:windows -->
> **Savet:** Za najbolje performanse NPU-a, omogućite turbo režim:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Promena modela

Aplikacija za kartice za učenje iz Koraka 6 radi i sa NPU modelima, samo promenite naziv modela:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Sledeći koraci

Imate lokalni AI server pokrenut na sopstvenom hardveru, evo šta možete uraditi dalje:

1. **Povežite svoje omiljene aplikacije**: Lemonade radi odmah po instalaciji sa [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/), i [mnogim drugim](https://lemonade-server.ai/marketplace).

2. **Istražite više modela**: Pregledajte kompletnu [biblioteku modela](https://lemonade-server.ai/docs/server/server_models/) kako biste pronašli modele optimizovane za programiranje, rezonovanje, vid i drugo. Koristite Lemonade aplikaciju ili `lemonade list` da vidite šta je dostupno.

3. **Otključajte ROCm GPU akceleraciju**: Ako imate podržani AMD GPU, prebacite se na ROCm backend: `lemonade config set llamacpp.backend=rocm`. Pogledajte [podržane AMD GPU-ove](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Pročitajte kompletnu API specifikaciju**: Lemonade podržava chat completions, embeddings, transkripciju zvuka, generisanje slika, pretvaranje teksta u govor i drugo. Pogledajte [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) za svaki endpoint.

5. **Doprinesite**: Lemonade je otvorenog koda. Pogledajte [vodič za doprinošenje](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) i potražite [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).