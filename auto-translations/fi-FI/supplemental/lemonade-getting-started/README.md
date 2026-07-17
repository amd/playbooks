<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tämä playbook käyttää erityisiä tageja, joita GitHub ei pysty renderöimään. Vieraile osoitteessa [amd.com/playbooks](https://amd.com/playbooks) nähdäksesi tämän sisällön oikein.
<!-- @github-only:end -->

## Yleiskatsaus

🍋 **Lemonade** on avoimen lähdekoodin paikallinen AI-palvelin, jonka avulla voit ajaa suuria kielimalleja (LLM), kuvageneraattoreita ja äänimalleja suoraan omalla laitteistollasi. Se tarjoaa mallit alan standardin mukaisen **OpenAI API** -rajapinnan kautta, joten mikä tahansa sovellus, joka toimii OpenAI:n kanssa, toimii välittömästi myös Lemonaden kanssa. Playbook-oppaan loppuun mennessä käytät Lemonadea mallien ajamiseen paikallisesti omalla koneellasi.

## Mitä opit

Tämän playbook-oppaan lopussa osaat:

* **Asentaa Lemonade Serverin** ja varmistaa, että se toimii.
* **Ladata LLM:n ja keskustella sen kanssa** yhdellä komennolla.
* **Tutustua web-käyttöliittymään** ja kokeilla eri modaliteetteja, kuten näköä, puheentunnistusta ja kuvagenerointia.
* **Vaihtaa GPU-taustajärjestelmiä** Vulkanin ja AMD ROCm™-ohjelmiston välillä.
* **Rakentaa Python-sovelluksen**, jota ohjaa paikallinen LLM OpenAI-yhteensopivan API:n avulla.
<!-- @device:halo_box,halo,stx,krk -->
* **Ajaa malleja AMD Neural Processing Unit (NPU) -yksiköllä** käyttäen Hybrid- ja FLM-suoritustiloja AMD Ryzen™ AI -laitteistolla.
<!-- @device:end -->

## Muistikonfiguraation asettaminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmistoedellytysten asentaminen

Ennen kuin aloitat, varmista, että sinulla on:

- PC, jossa on **Windows 11** tai tuettu **Linux**-jakelu (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** on suositeltava ajonaikaiselle mallille, jota käytetään vaiheissa 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** on suositeltava, jos haluat käyttää suurempaa koodingenerointimallia vaiheessa 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB vapaata levytilaa** ladattavien mallien mukaan. Tämän oppaan suurin malli on noin 20 GB.
- **Python 3.10–3.13** (käytetään Python-sovellus-osiossa)
- Internet-yhteys (langallinen tai langaton)
<!-- @device:halo_box,halo,stx,krk -->
- [Valinnainen] AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 -sarja tai Z2 Extreme) uusimmalla ohjaimella asennettuna osoitteesta [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), jos haluat ajaa mallin NPU:lla.
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

## Peruskäsitteet — Miten paikalliset AI-palvelimet toimivat

Ennen kuin ajamme mallin, on hyödyllistä ymmärtää *miksi* asiat on järjestetty tällä tavalla. Lemonade on **paikallinen malliserveeri**, prosessi, joka lataa AI-mallit muistiin ja tarjoaa ne sovelluksille HTTP:n kautta, aivan kuten pilvi-AI-palvelu tekisi.

### Miksi palvelin?

| Hyöty | Mitä se tarkoittaa sinulle |
|---------|----------------------|
| **Yksinkertaistettu integraatio** | Sovellukset kommunikoivat yhden HTTP API:n kautta sen sijaan, että ne käsittelisivät laitteistokohtaisia C++- tai Python-kirjastoja. |
| **Jaetut mallit** | Yksi ladattu malli voi palvella useita sovelluksia samanaikaisesti ilman, että RAM-muistia kuluttavia kaksoiskappaleita syntyy. |
| **Pilvestä paikalliseen siirrettävyys** | OpenAI:n pilvi-API:lle kirjoitettu koodi toimii Lemonaden kanssa muuttamalla yhtä URL-osoitetta. |
| **Vastuualueiden erottelu** | Mallinhallinta, suoratoisto ja vikasietoisuus ovat palvelimen vastuulla, joten kehittäjät voivat keskittyä omaan sovellukseensa. |

### OpenAI API -standardi

Lemonade toteuttaa **OpenAI API** -rajapinnan, saman käyttöliittymän, jota käyttävät ChatGPT, Azure OpenAI ja kymmenet muut palvelut. Keskustelumalli on yksinkertainen:

| Rooli | Kuka puhuu |
|------|---------------|
| **system** | Ohjeet mallille (persoona, rajoitukset, käytettävissä olevat työkalut) |
| **user** | Viestit ihmiseltä (tai sovellukselta) mallille |
| **assistant** | Mallin tuottamat vastaukset |

Tämä tarkoittaa, että mikä tahansa kirjasto tai sovellus, joka tukee OpenAI:ta, voi kommunikoida Lemonaden kanssa osoittamalla sen osoitteeseen `http://localhost:13305/api/v1` Lemonade Serverin ollessa käynnissä.

## Pääaktiviteetti — Ensimmäinen paikallinen AI-keskustelu

Ladataan LLM ja käydään sen kanssa keskustelu, jolloin AI toimii kokonaan omalla koneellasi.

### Vaihe 1: Lataa ja aja malli

Lemonadessa on kuratoitu mallikirjasto. Aloitetaan **Gemma-4-E2B-it** -mallilla, joka on tehokas ja kompakti malli, joka sisältää näkötuen. Avaa terminaali ja suorita:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Tämä yksittäinen komento tekee kolme asiaa:

1. **Lataa** mallin (~3 GB) Hugging Facesta, jos sitä ei ole jo ladattu. (Voi kestää jonkin aikaa)
2. **Käynnistää** Lemonade Server -prosessin portissa 13305.
3. **Avaa Lemonade App** -sovelluksen, jotta voit aloittaa keskustelun mallin kanssa.


<!-- @os:windows -->
Windowsissa Lemonade App käynnistyy automaattisesti ja voit aloittaa keskustelun välittömästi. Jos asensit `minimal.msi`-paketin, sovellus ei sisälly siihen. Aloittaaksesi keskustelun, avaa selain ja siirry osoitteeseen `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
Linuxissa avaa selain ja siirry osoitteeseen `http://localhost:13305` päästäksesi web-sovellukseen.
<!-- @os:end -->

Kokeile kirjoittaa kysymys:

```
What are three fun facts about lemons?
```

Malli vastaa suoraan chat-ikkunassa. **Onnittelut! Ajat suurta kielimallia paikallisesti.**

![Lemonade App lokien kanssa näytettynä](../../dependencies/assets/ChatwithLogs.png)

Lemonade App -sovelluksen Server Logs -ruudussa näet telemetriatietoja mallin suorituskyvystä jokaisen vastauksen jälkeen. Esimerkiksi:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Vaihe 2: Tutustu verkkokäyttöliittymään ja eri modaliteetteihin

Lemonade sisältää sisäänrakennetun verkkokäyttöliittymän, jossa voit:

- **Olla vuorovaikutuksessa** ladatun mallin kanssa tutun chat-ikkunan kautta
- **Selata malleja** Model Manager -välilehdellä
- **Ladata uusia malleja** yhdellä napsautuksella

Kokeile vaihtaa eri modaliteettien välillä käyttämällä verkkokäyttöliittymän **Model Manager** -välilehteä, jossa voit selata malleja reseptin tai kategorian mukaan:

1. **Näkökyky:** Ladattu `Gemma-4-E2B-it-GGUF`-malli tukee näkökykyä. Liitä kuva chat-kenttään ja pyydä mallia kuvailemaan se.
2. **Kuvien luominen:** Lataa Image-kategoriasta kuvamalli, kuten `SDXL-Turbo`, Model Managerista, ja käytä sitten Lemonade Image Generatoria kirjoittaaksesi kehotteen ja luodaksesi kuvan paikallisesti.
3. **Ääni:** Lataa Audio-kategoriasta äänimaalli, kuten `Whisper-Tiny`, joka osaa muuntaa puheen tekstiksi. Anna äänitallenne litteroitavaksi paikallisesti. Tekstistä puheeksi -toimintoa varten kokeile jotakin Speech-kategorian malleista, kuten `kokoro-v1`.

![Multimodaalisuus Lemonaden kanssa](../../dependencies/assets/multi_modality.png)

### Vaihe 3: Kokeile mallia eri taustajärjestelmällä

Jos viet hiiren Lemonade App -sovelluksessa mallin päälle, näet hammaspyöräkuvakkeen. Napsauttamalla sitä voit valita mallille asetuksia, mukaan lukien haluamasi taustajärjestelmän.

Oletuksena Lemonade käyttää Vulkania GPU-kiihdytykseen. Jos sinulla on tuettu AMD:n erillinen GPU, voit vaihtaa ROCmiin.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

Hallinnoi asennettuja taustajärjestelmiä napsauttamalla vasemmanpuoleisimman sarakkeen taustajärjestelmäpainiketta.

Vaihtoehtoisesti voit määrittää taustajärjestelmän seuraavalla komennolla:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Voit myös asettaa oletusarvoisen taustajärjestelmän ympäristömuuttujan `LEMONADE_LLAMACPP` avulla arvoilla: `vulkan`, `rocm` tai `cpu`.

---

## Syvemmälle — Rakenna tekoälypohjainen sovellus Pythonilla

Paikallisen tekoälypalvelimen todellinen voima on siinä, että mikä tahansa sovellus voi muodostaa yhteyden siihen muutamalla koodirivillä. Todistetaan tämä rakentamalla pieni mutta toimiva **opiskelun muistikorttisovellus**, jolle annat aiheen, se luo muistikortit ja voit testata itseäsi vuorovaikutteisesti.

### Vaihe 4: Käynnistä palvelin

Varmista, että Lemonade-palvelin on käynnissä. Se käynnistyy yleensä automaattisesti taustalla asennuksen jälkeen. Tarkista tämä suorittamalla:

```
lemonade status
```

Sinun pitäisi nähdä viesti: `Server is running on port 13305`.

Jos palvelin ei ole käynnissä, käynnistä se avaamalla Lemonade-sovellus. Käytä oletusporttia **13305** (voit vahvistaa tai valita sen ilmaisinalueen kuvakkeesta).

### Vaihe 5: Asenna OpenAI Python -asiakasohjelma

Luo terminaalissa venv ja asenna OpenAI Python -asiakasohjelma seuraavilla komennoilla:
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

### Vaihe 6: Rakenna muistikorttisovellus

Ladataan eri malli koodin luomista varten: `Qwen3.5-35B-A3B-GGUF`. Tämä on suuri (~20 Gt) ja suorituskykyinen malli, joka sopii parhaiten järjestelmiin, joissa on vähintään 32 Gt RAM-muistia. Jos käytettävissä on vähemmän RAM-muistia, kokeile `Qwen3.5-9B-GGUF` (~6 Gt).

Voit ladata sen käyttöliittymästä tai suorittaa seuraavan:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Syötä seuraava kehote Lemonade Chat UI:hin luodaksesi koodin yksinkertaiselle muistikorttisovellukselle.

Käytämme Qwen3.5-35B-A3B-GGUF:ia (suurempaa mallia, joka on parempi koodin kirjoittamisessa) Python-sovelluksemme luomiseen, ja sovellus itse kutsuu Gemma-4-E2B-it-GGUF:ia (pienempää mallia, jonka olet jo ladannut) suorituksen aikana. Koodi voidaan sitten kopioida haluamaasi tiedostoon Pythonissa ajettavaksi.

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

> **Vinkki**: Olemme noudattaneet standardeja ohjelmistokäytäntöjä huolellisen kehotteen luomisen ja kahden mallin järjestelmän avulla resurssien ja nopeuden optimoimiseksi.

Käytännöllisyyden vuoksi olemme tarjonneet esimerkkitulosteen tiedostossa [`flashcards.py`](assets/flashcards.py). Lataa se vapaasti hakemistoosi. Joka tapauksessa sinulla pitäisi nyt olla Python-tiedosto, joka voidaan ajaa.

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


### Vaihe 7: Aja luotu koodi

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Tässä on mitä sinun pitäisi nähdä:**

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

Noin 150 koodirivillä olet rakentanut täysin toimivan opiskelutyökalun, jota paikallinen LLM ohjaa. Ei API-avainta hallittavaksi, ei käyttökustannuksia eikä tietoja koskaan lähde koneeltasi.

> **Keskeinen havainto:** Huomaa, että `client = OpenAI(base_url=...) `-rivi on *ainoa* asia, joka sitoo tämän sovelluksen Lemonadeen OpenAI:n pilven sijaan. Muu koodi on identtistä sen kanssa, mitä kirjoittaisit mille tahansa OpenAI-yhteensopivalle palvelulle. Jos olet koskaan käyttänyt OpenAI Python -kirjastoa, tiedät jo kuinka rakentaa sovelluksia Lemonaden kanssa.

### Mitä tämä osoittaa

Tämä pieni sovellus harjoittaa useita tosielämän integrointimalleja:

| Malli | Missä se esiintyy |
|---------|-----------------|
| **Järjestelmäkehotteet** | `"system"`-viesti käskee LLM:ää tuottamaan jäsenneltyä JSON-muotoa |
| **Jäsennelty tuloste** | Sovellus jäsentää LLM:n vastauksen JSON-muodossa muistikorttien rakentamiseksi |
| **Tilattomia pyyntöjä** | Jokainen `generate_flashcards()`-kutsu on itsenäinen |
| **Virheenkäsittely** | `try/except` käsittelee sulavasti tapaukset, joissa LLM:n tuloste ei ole kelvollista JSON-muotoa |

Nämä samat mallit skaalautuvat mihin tahansa sovellukseen, kuten chatbotteihin, koodiavustajiin, sisällöntuottajiin ja automaatiotyökaluihin.

#### Lisähaaste

* Lisähaasteena kokeile päivittää sovellus niin, että muistikortit luetaan käyttäjälle ääneen viittaamalla [tässä](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) annettuun esimerkkiin.

---

<!-- @device:halo_box,halo,stx,krk -->
## Mallien ajaminen NPU:lla (valinnainen)

Jos sinulla on Ryzen AI 300/400/Max 300 -sarja tai Z2 Extreme, laitteessasi on sisäänrakennettu **Neural Processing Unit (NPU)**, erityisesti tekoälytyökuormia varten suunniteltu erillinen piiri. Mallien ajaminen NPU:lla on energiatehokkaampaa kuin GPU:n käyttö, mikä tekee siitä ihanteellisen tausta-tekoälytehtäviin, pidempiin istuntoihin ja akkukäyttöön.

Lemonade tukee kolmea NPU-suoritustilaa, jotka kaikki toimivat läpinäkyvästi saman OpenAI API:n kautta:

| Tila | Toimintaperiaate | Resepti | Esimerkkimallit |
|------|-----------------|---------|-----------------|
| **Hybridi (NPU + iGPU)** | NPU käsittelee kehotteen, iGPU tuottaa tokenit | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Vain NPU** | Koko päättely suoritetaan NPU:lla | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Käyttää FastFlowLM-moottoria NPU:lla, optimoitu AMD XDNA2:lle | FLM (`flm`) | qwen3.5-4b-FLM |

### Vaatimukset

- **AMD Ryzen AI 300/400 -sarja tai Z2-sarja** -prosessori
- **FLM**-malleja varten: FLM-ajoympäristö voidaan asentaa Lemonade-sovelluksesta, tai Lemonade asentaa FLM-ajoympäristön automaattisesti FLM-mallia ajettaessa. Lisätietoja FastFlowLM:stä löydät [täältä](https://fastflowlm.com/docs/).


### Vaihe 8: Aja hybridimalli

Hybridimallit jakavat työn NPU:n ja iGPU:n välillä hyvän nopeuden ja tehokkuuden tasapainon saavuttamiseksi. Valitse Lemonade-sovelluksessa malli `Ryzen AI LLM` -listalta, esimerkiksi `Qwen3-4B-Hybrid`, tai aja se seuraavalla komennolla:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade tunnistaa NPU:si automaattisesti ja asentaa **Ryzen AI LLM** -taustapalvelun.

> **Mitä tapahtuu pinnan alla?** Kun lähetät viestin, NPU käsittelee koko kehotteesi rinnakkain (tätä kutsutaan "esitäytöksi"). Sen jälkeen iGPU ottaa ohjat ja tuottaa vastauksen yksi token kerrallaan (tätä kutsutaan "dekoodaukseksi"). Tämä hybridilähestymistapa hyödyntää kummankin piirin vahvuuksia.

### Vaihe 9: Aja FLM-malli

FastFlowLM (FLM) -mallit on erityisesti optimoitu AMD:n XDNA2 NPU -arkkitehtuurille ja voivat olla hyvin nopeita kokoonsa nähden. Valitse esimerkiksi `qwen3.5-4b-FLM` `FastFlowLM NPU` -listalta tai käytä seuraavaa komentoa:

<!-- @os:windows -->
`FastFlowLM`:n käyttöönotto Windowsissa:

* Avaa `Backends Manager` -valikko.
* Etsi `FastFlowLM NPU` -taustapalvelukategoria.
* Napsauta Install NPU.
* Kun asennus on valmis, noin 36 oletusmalleja on saatavilla FFLM-pudotusvalikosta.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Kun `Lemonade`-sovellus käynnistetään ensimmäistä kertaa, `FastFlowNPU`-taustapalvelu ei ole oletuksena käytössä.
Paikallinen sovellus avaa asennussivun ohjatakseen sinut asennuksen läpi.

`FastFlowLM`:n käyttöönotto Linuxissa:

* Avaa `Lemonade`-sovellus.
* Vieraile [virallisessa FLM](https://lemonade-server.ai/flm_npu_linux.html) -dokumentaatiossa ja seuraa FLM:n asennusohjeita valitsemalla Linux-jakeluversio.
* Ota käyttöön backportit asennussivun ohjeiden mukaisesti.
* Lataa uusin `v0.9.x`-julkaisu [tags-sivulta](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
AMD Halo Developer Platform -alustaa varten muista valita Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Asenna ladattu `.deb`-paketti.
* Suositus: Sulje `Lemonade App` ja avaa se uudelleen, jotta muutokset havaitaan.
* Suositus: Avaa `Backends Manager` ja napsauta Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Onnistuneen asennuksen jälkeen sinun pitäisi nähdä, että `flm:npu` on valmistunut **Lemonade Desktop App** -sovelluksen **Download Manager** -osiossa.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Voit sitten valita minkä tahansa saatavilla olevista FFLM-malleista ja aloittaa NPU-taustapalvelun käytön.

Tiettyä mallia varten lataa haluamasi malli [mallisivulta](https://fastflowlm.com/docs/models/qwen/) ja vahvista se dokumentaatiossa annetulla Shell-komennolla.
```
flm run qwen3.5-4b-FLM
```
tai 
```
lemonade run qwen3.5-4b-FLM
```
 kautta
FLM-mallit sisältävät joitakin suosituimmista arkkitehtuureista (Gemma 3, Qwen 3, Llama 3 ja DeepSeek R1) ja niiden koko vaihtelee alle 1 GB:stä yli 13 GB:hen.
Lemonade tunnistaa NPU:si automaattisesti ja asentaa **FastFlowLM NPU** -taustapalvelun.

<!-- @os:windows -->
> **Vinkki:** Parhaan NPU-suorituskyvyn saavuttamiseksi ota turbo-tila käyttöön:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Mallien vaihtaminen

Vaiheen 6 muistikorttisovellus toimii myös NPU-mallien kanssa – muuta vain mallin nimi:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Seuraavat vaiheet

Sinulla on paikallinen tekoälypalvelin käynnissä omalla laitteistollasi – tässä on mitä tehdä seuraavaksi:

1. **Yhdistä suosikkisovelluksesi**: Lemonade toimii suoraan [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)in, [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)n, [Continue](https://lemonade-server.ai/docs/server/apps/continue/)n, [n8n](https://n8n.io/integrations/lemonade-model/)n ja [monien muiden](https://lemonade-server.ai/marketplace) kanssa.

2. **Selaa lisää malleja**: Tutustu koko [mallikirjastoon](https://lemonade-server.ai/docs/server/server_models/) löytääksesi koodaukseen, päättelyyn, näkökykyyn ja muuhun optimoituja malleja. Käytä Lemonade-sovellusta tai `lemonade list` -komentoa nähdäksesi saatavilla olevat mallit.

3. **Ota ROCm GPU -kiihdytys käyttöön**: Jos sinulla on tuettu AMD GPU, vaihda ROCm-taustapalveluun: `lemonade config set llamacpp.backend=rocm`. Katso [tuetut AMD GPU:t](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Lue koko API-määrittely**: Lemonade tukee chat-täydennyksiä, upotuksia, äänen transkriptiota, kuvien luontia, tekstistä puheeksi -muunnosta ja paljon muuta. Katso [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) kaikkien päätepisteiden osalta.

5. **Osallistu kehitykseen**: Lemonade on avoimen lähdekoodin projekti. Tutustu [osallistumisoppaaseen](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) ja etsi [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) -tehtäviä.