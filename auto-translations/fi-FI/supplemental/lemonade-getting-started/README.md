<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus

🍋 **Lemonade** on avoimen lähdekoodin paikallinen tekoälypalvelin, jonka avulla voit ajaa suuria kielimalleja (LLM), kuvageneraattoreita ja äänimalleja suoraan omalla laitteistollasi. Se paljastaa mallit alan standardin **OpenAI API**:n kautta, joten mikä tahansa OpenAI:n kanssa toimiva sovellus toimii heti myös Lemonaden kanssa. Tämän oppaan lopussa käytät Lemonadea ajamaan malleja paikallisesti omalla koneellasi.

## Mitä opit

Tämän oppaan lopussa osaat:

* **Asentaa Lemonade Serverin** ja varmistaa, että se toimii.
* **Ladata kielimallin ja keskustella sen kanssa** yhdellä komennolla.
* **Tutustua web-käyttöliittymään** ja kokeilla eri modaliteetteja, kuten näköä, puheentunnistusta ja kuvantuotantoa.
* **Vaihtaa GPU-taustajärjestelmää** Vulkanin ja AMD ROCm™ -ohjelmiston välillä.
* **Rakentaa Python-sovelluksen**, jota käyttää paikallinen LLM OpenAI-yhteensopivan API:n avulla.
<!-- @device:halo_box,halo,stx,krk -->
* **Ajaa malleja AMD Neural Processing Unitilla (NPU)** käyttäen Hybrid- ja FLM-suoritustiloja AMD Ryzen™ AI -laitteistolla.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmistovaatimusten asentaminen

Ennen kuin aloitat, varmista, että sinulla on:

- PC, jossa on **Windows 11** tai tuettu **Linux**-jakelu (Ubuntu 24.04+, Fedora, Debian)
- **16 Gt RAM-muistia** suositellaan vaiheissa 1–7 käytettävälle ajonaikaiselle mallille (`Gemma-4-E2B-it-GGUF`, ~3 Gt). **32 Gt+** suositellaan, jos haluat käyttää suurempaa koodigenerointimallia vaiheessa 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 Gt).
- **~4–30 Gt vapaata levytilaa** ladattavista malleista riippuen. Tämän oppaan suurin malli on noin 20 Gt.
- **Python 3.10–3.13** (käytetään Python-sovellusosiossa)
- Internet-yhteys (langallinen tai langaton)
<!-- @device:halo_box,halo,stx,krk -->
- [Valinnainen] AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 -sarja tai Z2 Extreme), johon on asennettu uusin ajuri osoitteesta [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), jos haluat ajaa mallia NPU:lla.
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

## Peruskäsitteet — Miten paikalliset tekoälypalvelimet toimivat

Ennen kuin ajamme mallia, kannattaa ymmärtää *miksi* asiat on järjestetty tällä tavalla. Lemonade on **paikallinen mallipalvelin**, eli prosessi, joka lataa tekoälymallit muistiin ja tarjoaa ne sovelluksille HTTP:n kautta, aivan kuten pilvipohjainen tekoälypalvelu tekisi.

### Miksi palvelin?

| Hyöty | Mitä se tarkoittaa sinulle |
|---------|----------------------|
| **Yksinkertaisempi integrointi** | Sovellukset kommunikoivat yhden HTTP-API:n kautta sen sijaan, että käsittelisivät laitteistokohtaisia C++- tai Python-kirjastoja. |
| **Jaetut mallit** | Yksi ladattu malli voi palvella useita sovelluksia kerralla, eikä päällekkäisiä kopioita kuluta RAM-muistiasi. |
| **Siirrettävyys pilvestä paikalliseen** | OpenAI:n pilvi-API:lle kirjoitettu koodi toimii Lemonaden kanssa vain yhtä URL-osoitetta vaihtamalla. |
| **Vastuiden eriyttäminen** | Mallien hallinnan, striimauksen ja vikasietoisuuden hoitaa palvelin, jotta kehittäjät voivat keskittyä omaan sovellukseensa. |

### OpenAI API -standardi

Lemonade toteuttaa **OpenAI API**:n, saman rajapinnan, jota käyttävät ChatGPT, Azure OpenAI ja kymmenet muut palvelut. Keskustelumalli on yksinkertainen:

| Rooli | Kuka puhuu |
|------|---------------|
| **system** | Ohjeet mallille (persoona, rajoitukset, käytettävissä olevat työkalut) |
| **user** | Ihmiseltä (tai sovellukselta) mallille lähetetyt viestit |
| **assistant** | Mallin tuottamat vastaukset |

Tämä tarkoittaa, että mikä tahansa kirjasto tai sovellus, joka tukee OpenAI:ta, voi kommunikoida Lemonaden kanssa osoittamalla osoitteeseen `http://localhost:13305/api/v1` Lemonade Serverin ollessa käynnissä.

## Pääharjoitus — Ensimmäinen paikallinen tekoälykeskustelusi

Ladataan LLM ja käydään sen kanssa keskustelu, jossa tekoäly toimii kokonaan omalla koneellasi.

### Vaihe 1: Lataa ja aja malli

Lemonade sisältää kuratoidun mallikirjaston. Aloitetaan **Gemma-4-E2B-it**-mallilla, joka on kyvykäs ja kompakti malli, joka sisältää myös näkötuen. Avaa pääte ja suorita:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Tämä yksittäinen komento tekee kolme asiaa:

1. **Lataa** mallin (~3 Gt) Hugging Facesta, jos sitä ei ole vielä ladattu. (Voi kestää jonkin aikaa)
2. **Käynnistää** Lemonade Server -prosessin portissa 13305.
3. **Avaa Lemonade Appin**, jotta voit aloittaa keskustelun mallin kanssa.


<!-- @os:windows -->
Windowsilla Lemonade App käynnistyy automaattisesti, ja voit aloittaa keskustelun heti. Jos asensit `minimal.msi`-paketin, sovellus ei sisälly siihen. Aloittaaksesi keskustelun, avaa selaimesi ja siirry osoitteeseen `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
Linuxilla avaa selaimesi ja siirry osoitteeseen `http://localhost:13305` päästäksesi web-sovellukseen.
<!-- @os:end -->

Kokeile kirjoittaa kysymys:

```
What are three fun facts about lemons?
```

Malli vastaa suoraan chat-ikkunassa. **Onnittelut! Ajat suurta kielimallia paikallisesti.**

![Lemonade App with Logs displayed](../../dependencies/assets/ChatwithLogs.png)

Lemonade Appin Server Logs -paneelissa löydät telemetriatiedot mallin suorituskyvystä jokaisen vastauksen jälkeen. Esimerkiksi:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Vaihe 2: Tutustu verkkokäyttöliittymään ja eri toimintatiloihin

Lemonade sisältää sisäänrakennetun verkkokäyttöliittymän, jonka avulla voit:

- **Keskustella** ladatun mallin kanssa tutussa chat-ikkunassa
- **Selata malleja** Model Manager -välilehdellä
- **Ladata uusia malleja** yhdellä napsautuksella

Kokeile eri toimintatilojen välillä vaihtamista käyttämällä verkkokäyttöliittymän **Model Manager**-välilehteä, jossa voit selata malleja Recipe- tai Category-luokittelun mukaan:

1. **Vision:** Jo lataamasi `Gemma-4-E2B-it-GGUF`-malli tukee näkötoimintoja. Liitä kuva chat-ikkunaan ja pyydä mallia kuvailemaan sitä.
2. **Kuvien luonti:** Image-kategoriassa lataa kuvamalli, kuten `SDXL-Turbo`, Model Managerista, ja käytä sitten Lemonade Image Generatoria kirjoittaaksesi kehotteen ja luodaksesi kuvan paikallisesti.
3. **Ääni:** Audio-kategoriassa lataa äänimalli, kuten `Whisper-Tiny`, joka pystyy puheentunnistukseen tekstiksi. Anna äänitallenne litteroitavaksi paikallisesti. Tekstistä puheeksi -toimintoa varten kokeile jotakin Speech-kategorian malleista, kuten `kokoro-v1`.

![Monitoimintoisuus Lemonaden kanssa](../../dependencies/assets/multi_modality.png)

### Vaihe 3: Kokeile mallia eri taustajärjestelmällä

Kun viet hiiren mallin päälle Lemonade-sovelluksessa, näet hammasrataskuvakkeen. Napsauttamalla sitä voit valita mallille asetuksia, mukaan lukien halutun taustajärjestelmän valinnan.

Oletusarvoisesti Lemonade käyttää Vulkania GPU-kiihdytykseen. Jos sinulla on tuettu AMD-erillisnäytönohjain, voit vaihtaa ROCm:ään.

![Lemonaden taustajärjestelmän valinta](../../dependencies/assets/lemonademodeloptions.png)

Hallitaksesi asennettuja taustajärjestelmiä, napsauta vasemmanpuoleisimman sarakkeen taustajärjestelmäpainiketta.

Vaihtoehtoisesti voit määrittää taustajärjestelmän seuraavalla komennolla:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Voit myös asettaa oletustaustajärjestelmän ympäristömuuttujalla `LEMONADE_LLAMACPP` arvoilla: `vulkan`, `rocm` tai `cpu`.

---

## Syvemmälle — Rakenna Python-pohjainen tekoälysovellus

Paikallisen tekoälypalvelimen todellinen voima piilee siinä, että mikä tahansa sovellus voi muodostaa siihen yhteyden vain muutamalla koodirivillä. Todistaaksemme tämän, rakennetaan pieni mutta toimiva **opiskelukorttien generaattori**, jolle annat aiheen, se luo opiskelukortit, ja voit testata itseäsi interaktiivisesti.

### Vaihe 4: Käynnistä palvelin

Varmista, että Lemonade-palvelin on käynnissä. Se käynnistyy tyypillisesti automaattisesti taustalla asennuksen jälkeen. Voit varmistaa tämän suorittamalla:

```
lemonade status
```

Näet viestin, kuten: `Server is running on port 13305`.

Jos palvelin ei ole käynnissä, käynnistä se avaamalla Lemonade-sovellus. Käytä oletusporttia **13305** (voit varmistaa tai valita tämän ilmaisinalueen kuvakkeesta).

### Vaihe 5: Asenna OpenAI Python -asiakas

Luo pääteikkunassa venv ja asenna OpenAI Python -asiakas seuraavilla komennoilla:
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

### Vaihe 6: Rakenna opiskelukorttisovellus

Ladataan koodin generointia varten eri malli: `Qwen3.5-35B-A3B-GGUF`. Tämä on suuri (~20 Gt) ja tehokas malli, joka sopii parhaiten järjestelmiin, joissa on vähintään 32 Gt RAM-muistia. Jos käytettävissäsi on vähemmän RAM-muistia, kokeile sen sijaan mallia `Qwen3.5-9B-GGUF` (~6 Gt).

Voit ladata sen käyttöliittymästä tai suorittaa seuraavan:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Syötä seuraava kehote Lemonade Chat UI:hin luodaksesi koodia yksinkertaiselle Flashcard-sovellukselle.

Käytämme mallia Qwen3.5-35B-A3B-GGUF (suurempi malli, joka on parempi koodin kirjoittamisessa) Python-sovelluksemme luomiseen, ja itse sovellus kutsuu ajon aikana mallia Gemma-4-E2B-it-GGUF (jo lataamasi pienempi malli). Koodi voidaan sitten kopioida valitsemaasi tiedostoon Pythonissa suoritettavaksi.

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

> **Vinkki**: Olemme noudattaneet standardeja tekniikkakäytäntöjä huolellisen kehotteiden laadinnan ja kahden mallin järjestelmän käytön avulla resurssien ja nopeuden optimoimiseksi.

Mukavuutesi vuoksi olemme toimittaneet esimerkkitulosteen tiedostossa [`flashcards.py`](assets/flashcards.py). Voit vapaasti ladata sen omaan hakemistoosi. Joka tapauksessa, sinulla pitäisi nyt olla Python-tiedosto, jota voidaan suorittaa.

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


### Vaihe 7: Suorita luotu koodi

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

Noin 150 koodirivillä olet rakentanut täysin toimivan opiskelutyökalun, jota pyörittää paikallinen LLM. Ei API-avainta hallittavaksi, ei käyttökustannuksia, eikä mitään dataa poistu koneeltasi.

> **Keskeinen oivallus:** Huomaa, että `client = OpenAI(base_url=...) `-rivi on *ainoa* asia, joka sitoo tämän sovelluksen Lemonadeen OpenAI-pilvipalvelun sijaan. Muu koodi on identtinen sen kanssa, mitä kirjoittaisit mitä tahansa OpenAI-yhteensopivaa palvelua vasten. Jos olet koskaan käyttänyt OpenAI Python -kirjastoa, osaat jo rakentaa sovelluksia Lemonadella.

### Mitä tämä osoittaa

Tämä pieni sovellus harjoittaa useita todellisen maailman integraatiomalleja:

| Malli | Missä se esiintyy |
|---------|-----------------|
| **Järjestelmäkehotteet** | `"system"`-viesti kertoo LLM:lle, että sen tulee tuottaa jäsennelty JSON |
| **Jäsennelty tuloste** | Sovellus jäsentää LLM:n vastauksen JSON:ina rakentaakseen opiskelukortit |
| **Tilattomat pyynnöt** | Jokainen `generate_flashcards()`-kutsu on itsenäinen |
| **Virheenkäsittely** | `try/except` käsittelee sulavasti tapaukset, joissa LLM:n tuloste ei ole kelvollista JSON:ia |

Nämä samat mallit skaalautuvat mihin tahansa sovellukseen, kuten chatboteihin, koodiavustajiin, sisällöntuottajiin ja automaatiotyökaluihin.

#### Bonushaaste

* Lisähaastetta varten kokeile päivittää sovellusta niin, että opiskelukortit luetaan käyttäjälle ääneen viittaamalla [tähän](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) annettuun esimerkkiin.

---

<!-- @device:halo_box,halo,stx,krk -->
## Mallien suorittaminen NPU:lla (valinnainen)

Jos sinulla on Ryzen AI 300/400/Max 300 -sarjan tai Z2 Extreme -laite, laitteessasi on sisäänrakennettu **Neural Processing Unit (NPU)**, eli erillinen siru, joka on suunniteltu erityisesti tekoälykuormituksia varten. Mallien suorittaminen NPU:lla on virrankulutukseltaan tehokkaampaa kuin GPU:n käyttö, mikä tekee siitä ihanteellisen taustalla suoritettaville tekoälytehtäville, pidemmille istunnoille ja akkukäytölle.

Lemonade tukee kolmea NPU-suoritustilaa, jotka kaikki toimivat läpinäkyvästi saman OpenAI API:n takana:

| Tila | Toimintaperiaate | Resepti | Esimerkkimallit |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU käsittelee kehotteen, iGPU generoi tokenit | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Vain NPU** | Koko päättely suoritetaan NPU:lla | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Käyttää FastFlowLM-moottoria NPU:lla, optimoitu AMD XDNA2:lle | FLM (`flm`) | qwen3.5-4b-FLM |

### Vaatimukset

- **AMD Ryzen AI 300/400 -sarjan tai Z2-sarjan** suoritin
- **FLM**-malleille: FLM-ajoympäristön voi asentaa Lemonade-sovelluksen sisältä, tai Lemonade asentaa FLM-ajoympäristön automaattisesti FLM-mallia suoritettaessa. Lisätietoja FastFlowLM:stä saat [täältä](https://fastflowlm.com/docs/).


### Vaihe 8: Hybridimallin suorittaminen

Hybridimallit jakavat työn NPU:n ja iGPU:n kesken saavuttaakseen hyvän tasapainon nopeuden ja tehokkuuden välillä. Valitse Lemonade-sovelluksessa malli `Ryzen AI LLM` -listalta, esimerkiksi `Qwen3-4B-Hybrid`, tai suorita se seuraavalla komennolla:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade tunnistaa NPU:si automaattisesti ja asentaa **Ryzen AI LLM** -taustajärjestelmän.

> **Mitä konepellin alla tapahtuu?** Kun lähetät viestin, NPU käsittelee koko kehotteesi rinnakkain (tätä kutsutaan "esitäytöksi", engl. "prefill"). Sen jälkeen iGPU ottaa vastuun ja generoi vastauksen yksi token kerrallaan (tätä kutsutaan "purkamiseksi", engl. "decode"). Tämä hybridilähestymistapa hyödyntää kummankin sirun vahvuuksia.

### Vaihe 9: FLM-mallin suorittaminen

FastFlowLM (FLM) -mallit on erityisesti optimoitu AMD:n XDNA2-NPU-arkkitehtuurille, ja ne voivat olla erittäin nopeita kokoonsa nähden. Valitse esimerkiksi `qwen3.5-4b-FLM` `FastFlowLM NPU` -listalta tai käytä seuraavaa komentoa:

<!-- @os:windows -->
FastFlowLM-tuen ottaminen käyttöön Windowsissa:

* Avaa `Backends Manager` -valikko.
* Etsi `FastFlowLM NPU` -taustajärjestelmäkategoria.
* Napsauta Install NPU.
* Kun asennus on valmis, noin 36 oletusmallia on saatavilla FFLM-pudotusvalikossa.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Kun `Lemonade`-sovellus käynnistetään ensimmäistä kertaa, `FastFlowNPU`-taustajärjestelmä ei ole oletuksena käytössä. 
Paikallinen sovellus avaa asennussivun, joka opastaa sinut asennuksen läpi.

FastFlowLM-tuen ottaminen käyttöön Linuxissa:

* Avaa `Lemonade`-sovellus.
* Käy [virallisessa FLM](https://lemonade-server.ai/flm_npu_linux.html) -dokumentaatiossa ja seuraa FLM:n asennusohjeita valitsemalla oma Linux-jakelusi.
* Ota backports käyttöön asennussivun ohjeiden mukaisesti.
* Lataa uusin `v0.9.x`-julkaisu [tags-sivulta](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
AMD Halo Developer Platform -alustalle: valitse ehdottomasti Debian 13.
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
Onnistuneen asennuksen jälkeen näet, että `flm:npu` on valmistunut **Lemonade Desktop App** -sovelluksen **Download Manager** -osiossa.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Voit sitten valita minkä tahansa saatavilla olevista FFLM-malleista ja alkaa käyttää NPU-taustajärjestelmää.

Tietylle mallille: lataa haluamasi malli [mallisivulta](https://fastflowlm.com/docs/models/qwen/) ja vahvista se dokumentaatiossa annetulla Shell-komennolla.
```
flm run qwen3.5-4b-FLM
```
tai käyttämällä 
```
lemonade run qwen3.5-4b-FLM
```

FLM-mallit kattavat joitakin suosituimmista arkkitehtuureista (Gemma 3, Qwen 3, Llama 3 ja DeepSeek R1) ja vaihtelevat alle 1 Gt:sta yli 13 Gt:hen.
Lemonade tunnistaa NPU:si automaattisesti ja asentaa **FastFlowLM NPU** -taustajärjestelmän.

<!-- @os:windows -->
> **Vinkki:** Parhaan NPU-suorituskyvyn saavuttamiseksi ota turbo-tila käyttöön:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Mallien vaihtaminen

Vaiheen 6 flashcard-sovellus toimii myös NPU-malleilla, vaihda vain mallin nimi:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Seuraavat vaiheet

Sinulla on nyt paikallinen tekoälypalvelin käynnissä omalla laitteistollasi. Tässä on seuraavat askeleet:

1. **Yhdistä suosikkisovelluksesi**: Lemonade toimii suoraan pakkauksesta [VS Code Copilotin](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI:n](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continuen](https://lemonade-server.ai/docs/server/apps/continue/), [n8n:n](https://n8n.io/integrations/lemonade-model/) ja [monien muiden](https://lemonade-server.ai/marketplace) kanssa.

2. **Selaa lisää malleja**: Tutustu koko [mallikirjastoon](https://lemonade-server.ai/docs/server/server_models/) löytääksesi koodaukseen, päättelyyn, näkötehtäviin ja muuhun optimoituja malleja. Käytä Lemonade-sovellusta tai `lemonade list` -komentoa nähdäksesi saatavilla olevat mallit.

3. **Ota käyttöön ROCm GPU-kiihdytys**: Jos sinulla on tuettu AMD GPU, vaihda ROCm-taustajärjestelmään: `lemonade config set llamacpp.backend=rocm`. Katso [tuetut AMD GPU:t](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Lue koko API-spesifikaatio**: Lemonade tukee chat-täydennyksiä, upotuksia, äänen litterointia, kuvantuotantoa, tekstistä puheeksi -toimintoa ja muuta. Katso [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) kaikkien päätepisteiden osalta.

5. **Osallistu kehitykseen**: Lemonade on avoimen lähdekoodin projekti. Tutustu [osallistumisoppaaseen](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) ja etsi [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) -merkittyjä tehtäviä.

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