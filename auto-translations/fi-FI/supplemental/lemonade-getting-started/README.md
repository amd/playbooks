<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> Tässä ohjekirjassa käytetään erikoismerkintöjä, joita GitHub ei pysty renderöimään. Käy osoitteessa [amd.com/playbooks](https://amd.com/playbooks), jotta näet tämän sisällön oikein esikatseltuna.
<!-- @github-only:end -->

## Yleiskatsaus

🍋 **Lemonade** on avoimen lähdekoodin paikallinen tekoälypalvelin, jonka avulla voit suorittaa suuria kielimalleja (LLM), kuvageneraattoreita ja äänimalleja suoraan omalla laitteistollasi. Se tarjoaa mallit käyttöön alan standardin mukaisen **OpenAI API**:n kautta, joten mikä tahansa OpenAI:n kanssa toimiva sovellus toimii heti myös Lemonaden kanssa. Tämän ohjekirjan lopussa käytät Lemonadea mallien suorittamiseen paikallisesti omalla koneellasi.

## Mitä opit

Tämän ohjekirjan lopussa osaat:

* **Asentaa Lemonade Serverin** ja varmistaa, että se on käynnissä.
* **Ladata LLM-mallin ja keskustella sen kanssa** yhdellä komennolla.
* **Tutustua verkkokäyttöliittymään** ja kokeilla eri modaliteetteja, kuten näköä, puheentunnistusta ja kuvan generointia.
* **Vaihtaa GPU-taustajärjestelmää** Vulkanin ja AMD ROCm™ -ohjelmiston välillä.
* **Rakentaa Python-sovelluksen**, jota käyttää paikallinen LLM OpenAI-yhteensopivan API:n avulla.
<!-- @device:halo_box,halo,stx,krk -->
* **Suorittaa malleja AMD:n neuroverkkoprosessorilla (NPU)** käyttäen Hybrid- ja FLM-suoritustiloja AMD Ryzen™ AI -laitteistolla.
<!-- @device:end -->

## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

Ennen kuin aloitat, varmista, että sinulla on:

- Tietokone, jossa on **Windows 11** tai tuettu **Linux**-jakelu (Ubuntu 24.04+, Fedora, Debian)
- **16 Gt RAM-muistia** suositellaan vaiheissa 1–7 käytettävälle ajonaikaiselle mallille (`Gemma-4-E2B-it-GGUF`, ~3 Gt). **32 Gt tai enemmän** suositellaan, jos haluat käyttää suurempaa koodin generointimallia vaiheessa 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 Gt).
- **Noin 4–30 Gt vapaata levytilaa** ladattavista malleista riippuen. Tämän oppaan suurin malli on noin 20 Gt.
- **Python 3.10–3.13** (käytetään Python-sovellusosiossa)
- Internet-yhteys (langallinen tai langaton)
<!-- @device:halo_box,halo,stx,krk -->
- [Valinnainen] AMD XDNA 2 -NPU (Ryzen AI 300/400/Max 300 -sarja tai Z2 Extreme) uusimmalla ajurilla asennettuna [Ryzen AI -ohjelmiston asennusohjeista](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), jos haluat suorittaa mallin NPU:lla.
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

## Ydinkäsitteet — Miten paikalliset tekoälypalvelimet toimivat

Ennen kuin suoritamme mallin, kannattaa ymmärtää, *miksi* asiat on järjestetty tällä tavalla. Lemonade on **paikallinen mallipalvelin** eli prosessi, joka lataa tekoälymallit muistiin ja tarjoaa ne sovellusten käyttöön HTTP:n välityksellä, aivan kuten pilvipohjainen tekoälypalvelu tekisi.

### Miksi palvelin?

| Hyöty | Mitä se tarkoittaa sinulle |
|---------|----------------------|
| **Yksinkertaistettu integrointi** | Sovellukset keskustelevat yhden HTTP-API:n kanssa sen sijaan, että käsittelisivät laitteistokohtaisia C++- tai Python-kirjastoja. |
| **Jaetut mallit** | Yksi ladattu malli voi palvella useita sovelluksia samanaikaisesti, eikä kopioita tarvita syömään RAM-muistiasi. |
| **Siirrettävyys pilvestä paikalliseen** | OpenAI:n pilvi-API:lle kirjoitettu koodi toimii Lemonaden kanssa vaihtamalla vain yhden URL-osoitteen. |
| **Vastuiden erottaminen** | Mallien hallinnan, striimauksen ja vikasietoisuuden hoitaa palvelin, jotta kehittäjät voivat keskittyä omaan sovellukseensa. |

### OpenAI API -standardi

Lemonade toteuttaa **OpenAI API**:n, saman rajapinnan, jota käyttävät ChatGPT, Azure OpenAI ja kymmenet muut palvelut. Keskustelumalli on yksinkertainen:

| Rooli | Kuka puhuu |
|------|---------------|
| **system** | Ohjeet mallille (persoona, rajoitteet, käytettävissä olevat työkalut) |
| **user** | Ihmisen (tai sovelluksen) viestit mallille |
| **assistant** | Mallin generoimat vastaukset |

Tämä tarkoittaa, että mikä tahansa kirjasto tai sovellus, joka tukee OpenAI:ta, voi keskustella Lemonaden kanssa osoittamalla sen osoitteeseen `http://localhost:13305/api/v1`, kun Lemonade Server on käynnissä.

## Pääharjoitus — Ensimmäinen paikallinen tekoälykeskustelusi

Ladataan LLM-malli ja keskustellaan sen kanssa suorittaen tekoäly kokonaan omalla koneellasi.

### Vaihe 1: Lataa ja suorita malli

Lemonade toimitetaan valikoidun mallikirjaston kanssa. Aloitetaan **Gemma-4-E2B-it**-mallilla, joka on tehokas ja kompakti ja sisältää näkötuen. Avaa pääte ja suorita:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Tämä yksi komento tekee kolme asiaa:

1. **Lataa** mallin (~3 Gt) Hugging Facesta, jos sitä ei ole vielä ladattu. (Voi kestää jonkin aikaa)
2. **Käynnistää** Lemonade Server -prosessin portissa 13305.
3. **Avaa Lemonade Appin**, jotta voit aloittaa keskustelun mallin kanssa.


<!-- @os:windows -->
Windowsissa Lemonade App käynnistyy automaattisesti, ja voit aloittaa keskustelun heti. Jos asensit `minimal.msi`-paketin, sovellus ei sisälly siihen. Aloita keskustelu avaamalla verkkoselain ja siirtymällä osoitteeseen `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
Linuxissa avaa selain ja siirry osoitteeseen `http://localhost:13305` päästäksesi verkkosovellukseen.
<!-- @os:end -->

Kokeile kirjoittaa kysymys:

```
What are three fun facts about lemons?
```

Malli vastaa suoraan keskusteluikkunassa. **Onnittelut! Suoritat suurta kielimallia paikallisesti.**

![Lemonade App näyttäen lokit](../../dependencies/assets/ChatwithLogs.png)

Lemonade Appin Server Logs -paneelista löydät telemetriatietoa mallin suorituskyvystä jokaisen vastauksen jälkeen. Esimerkiksi:

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

- **Keskustella** ladatun mallin kanssa tutussa chat-ikkunassa
- **Selata malleja** Model Manager -välilehdellä
- **Ladata uusia malleja** yhdellä napsautuksella

Kokeile vaihdella eri modaliteettien välillä käyttämällä verkkokäyttöliittymän **Model Manager** -välilehteä, jossa voit selata malleja Recipe- tai Category-luokkien mukaan:

1. **Näkö:** Jo lataamasi `Gemma-4-E2B-it-GGUF`-malli tukee näköä. Liitä kuva chat-ikkunaan ja pyydä mallia kuvailemaan sitä.
2. **Kuvan generointi:** Lataa Image-kategoriasta kuvamalli, kuten `SDXL-Turbo`, Model Managerista ja käytä sitten Lemonade Image Generatoria kirjoittamaan kehote ja luomaan kuva paikallisesti.
3. **Ääni:** Lataa Audio-kategoriasta äänimalli, kuten `Whisper-Tiny`, joka osaa muuntaa puheen tekstiksi. Anna sille äänitallenne litteroitavaksi paikallisesti. Tekstistä puheeksi -toimintoa varten kokeile jotain Speech-kategorian mallia, kuten `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### Vaihe 3: Kokeile mallia eri taustajärjestelmällä

Kun viet hiiren mallin päälle Lemonade-sovelluksessa, näet hammasrataskuvakkeen. Sitä napsauttamalla voit valita mallin asetuksia, mukaan lukien haluamasi taustajärjestelmän.

Oletuksena Lemonade käyttää Vulkania GPU-kiihdytykseen. Jos sinulla on tuettu AMD-erillisnäytönohjain, voit vaihtaa ROCm:ään.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

Voit hallita asennettuja taustajärjestelmiä napsauttamalla taustajärjestelmäpainiketta vasemmanpuoleisimmassa sarakkeessa.

Vaihtoehtoisesti voit määrittää taustajärjestelmän seuraavalla komennolla:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Voit myös asettaa oletustaustajärjestelmän ympäristömuuttujalla `LEMONADE_LLAMACPP` seuraavilla arvoilla: `vulkan`, `rocm` tai `cpu`.

---

## Syvemmälle — rakenna Python-pohjainen tekoälysovellus

Paikallisen tekoälypalvelimen todellinen voima on siinä, että mikä tahansa sovellus voi muodostaa siihen yhteyden vain muutamalla rivillä koodia. Todistaaksemme tämän, rakennetaan pieni mutta toimiva **opiskelun tukisanakone (flashcard generator)**, jolle annat aiheen, se luo opiskelukortit, ja voit sitten testata itseäsi interaktiivisesti.

### Vaihe 4: Käynnistä palvelin

Varmista, että Lemonade-palvelin on käynnissä. Se käynnistyy tyypillisesti automaattisesti taustalla asennuksen jälkeen. Varmistaaksesi tämän, suorita:

```
lemonade status
```

Sinun pitäisi nähdä viesti kuten: `Server is running on port 13305`.

Jos palvelin ei ole käynnissä, käynnistä se avaamalla Lemonade-sovellus. Käytä oletusporttia **13305** (voit vahvistaa tai valita tämän ilmoitusalueen kuvakkeesta).

### Vaihe 5: Asenna OpenAI Python -asiakas

Luo terminaalissa venv ja asenna OpenAI Python -asiakas seuraavilla komennoilla:
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

Ladataan eri malli koodin generointiin: `Qwen3.5-35B-A3B-GGUF`. Tämä on suuri (~20 Gt) ja suorituskykyinen malli, joka sopii parhaiten järjestelmiin, joissa on vähintään 32 Gt RAM-muistia. Jos käytettävissä on vähemmän RAM-muistia, kokeile sen sijaan mallia `Qwen3.5-9B-GGUF` (~6 Gt).

Voit ladata sen käyttöliittymästä tai suorittaa seuraavan:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Syötä seuraava kehote Lemonade Chat UI:hin, jotta se generoi koodin yksinkertaiselle Flashcard-sovellukselle.

Käytämme mallia Qwen3.5-35B-A3B-GGUF (suurempi malli, joka on parempi koodin kirjoittamisessa) generoimaan Python-sovelluksemme, ja itse sovellus kutsuu ajon aikana mallia Gemma-4-E2B-it-GGUF (jo lataamasi pienempi malli). Koodi voidaan sitten kopioida haluamaasi tiedostoon suoritettavaksi Pythonissa.

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

> **Vinkki**: Olemme noudattaneet vakiintuneita insinöörikäytäntöjä huolellisen kehotteen suunnittelun kautta ja käyttämällä kahden mallin järjestelmää resurssien ja nopeuden optimoimiseksi.

Käytännöllisyyden vuoksi olemme tarjonneet esimerkkilähtökoodin tiedostossa [`flashcards.py`](assets/flashcards.py). Voit vapaasti ladata sen omaan hakemistoosi. Joka tapauksessa sinulla pitäisi nyt olla Python-tiedosto, joka voidaan suorittaa.

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


### Vaihe 7: Suorita generoitu koodi

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Näin sen pitäisi näyttää:**

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

Noin 150 koodirivillä olet rakentanut täysin toimivan opiskelutyökalun, jota pyörittää paikallinen LLM. API-avainta ei tarvitse hallita, käyttökustannuksia ei ole, eikä mikään data koskaan poistu koneeltasi.

> **Keskeinen oivallus:** Huomaa, että rivi `client = OpenAI(base_url=...) ` on *ainoa* asia, joka sitoo tämän sovelluksen Lemonadeen OpenAI:n pilvipalvelun sijaan. Loppuosa koodista on identtinen sen kanssa, mitä kirjoittaisit mitä tahansa OpenAI-yhteensopivaa palvelua vastaan. Jos olet joskus käyttänyt OpenAI Python -kirjastoa, tiedät jo, miten Lemonaden kanssa rakennetaan sovelluksia.

### Mitä tämä osoittaa

Tämä pieni sovellus harjoittelee useita todellisen maailman integraatiomalleja:

| Malli | Missä se esiintyy |
|---------|-----------------|
| **Järjestelmäkehotteet** | `"system"`-viesti kertoo LLM:lle, että sen tulee tuottaa jäsennelty JSON |
| **Jäsennelty tuloste** | Sovellus jäsentää LLM:n vastauksen JSON-muodossa rakentaakseen opiskelukortteja |
| **Tilattomat pyynnöt** | Jokainen `generate_flashcards()`-kutsu on itsenäinen |
| **Virheenkäsittely** | `try/except` käsittelee sulavasti tapaukset, joissa LLM:n tuloste ei ole kelvollista JSON:ia |

Samat mallit skaalautuvat mihin tahansa sovellukseen, kuten chatboteihin, koodiavustajiin, sisällöntuottajiin ja automaatiotyökaluihin.

#### Lisähaaste

* Lisähaasteena voit kokeilla päivittää sovellusta niin, että opiskelukortit luetaan käyttäjälle ääneen viittaamalla [tähän](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) tarjottuun esimerkkiin.

---

<!-- @device:halo_box,halo,stx,krk -->
## Mallien suorittaminen NPU:lla (valinnainen)

Jos sinulla on Ryzen AI 300/400/Max 300 -sarja tai Z2 Extreme, laitteessasi on sisäänrakennettu **Neural Processing Unit (NPU)**, erityisesti tekoälytyökuormia varten suunniteltu erillinen piiri. Mallien suorittaminen NPU:lla on virrankäytöltään tehokkaampaa kuin GPU:n käyttäminen, mikä tekee siitä ihanteellisen taustalla suoritettaviin tekoälytehtäviin, pidempiin istuntoihin ja akkukäyttöön.

Lemonade tukee kolmea NPU-suoritustilaa, ja kaikki toimivat läpinäkyvästi saman OpenAI API:n takana:

| Tila | Toimintatapa | Resepti | Esimerkkimallit |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU käsittelee kehotteen, iGPU luo tokenit | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Vain NPU** | Koko päättely suoritetaan NPU:lla | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Käyttää FastFlowLM-moottoria NPU:lla, optimoitu AMD XDNA2:lle | FLM (`flm`) | qwen3.5-4b-FLM |

### Vaatimukset

- **AMD Ryzen AI 300/400 -sarjan tai Z2-sarjan** suoritin
- **FLM**-malleille: FLM-ajoympäristön voi asentaa Lemonade-sovelluksen sisältä, tai Lemonade asentaa FLM-ajoympäristön automaattisesti FLM-mallia suoritettaessa. Lisätietoja FastFlowLM:stä löydät [täältä](https://fastflowlm.com/docs/).


### Vaihe 8: Hybridimallin suorittaminen

Hybridimallit jakavat työn NPU:n ja iGPU:n kesken, mikä tarjoaa hyvän tasapainon nopeuden ja tehokkuuden välillä. Valitse Lemonade-sovelluksessa malli `Ryzen AI LLM` -listalta, esimerkiksi `Qwen3-4B-Hybrid`, tai suorita se seuraavalla komennolla:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade tunnistaa NPU:n automaattisesti ja asentaa **Ryzen AI LLM** -taustajärjestelmän.

> **Mitä pinnan alla tapahtuu?** Kun lähetät viestin, NPU käsittelee koko kehotteesi rinnakkain (tätä kutsutaan "prefill"-vaiheeksi). Sen jälkeen iGPU ottaa ohjat ja luo vastauksen yksi token kerrallaan (tätä kutsutaan "decode"-vaiheeksi). Tämä hybridilähestymistapa hyödyntää kummankin piirin vahvuuksia.

### Vaihe 9: FLM-mallin suorittaminen

FastFlowLM (FLM) -mallit on erityisesti optimoitu AMD:n XDNA2 NPU-arkkitehtuurille, ja ne voivat olla erittäin nopeita kokoonsa nähden. Valitse esimerkiksi `qwen3.5-4b-FLM` `FastFlowLM NPU` -listalta tai käytä seuraavaa komentoa:

<!-- @os:windows -->
`FastFlowLM`-toiminnon ottaminen käyttöön Windowsissa:

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

`FastFlowLM`-toiminnon ottaminen käyttöön Linuxissa:

* Avaa `Lemonade`-sovellus.
* Käy [virallisessa FLM](https://lemonade-server.ai/flm_npu_linux.html)-dokumentaatiossa ja seuraa FLM:n asennusohjeita valitsemalla Linux-jakelusi.
* Ota backports-pakettivarasto käyttöön asennussivun ohjeiden mukaisesti.
* Lataa uusin `v0.9.x`-julkaisu [tags-sivulta](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
AMD Halo Developer Platformille varmista, että valitset Debian 13:n.
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
Onnistuneen asennuksen jälkeen `flm:npu`-kohdan pitäisi näkyä valmiina **Lemonade Desktop App** -sovelluksen **Download Manager** -osiossa.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Voit sitten valita minkä tahansa saatavilla olevista FFLM-malleista ja alkaa käyttää NPU-taustajärjestelmää.

Jos haluat tietyn mallin, lataa haluamasi malli [mallisivulta](https://fastflowlm.com/docs/models/qwen/) ja vahvista se dokumentaatiossa annetulla Shell-komennolla.
```
flm run qwen3.5-4b-FLM
```
tai 
```
lemonade run qwen3.5-4b-FLM
```
 kautta
FLM-mallit sisältävät joitakin suosituimmista arkkitehtuureista (Gemma 3, Qwen 3, Llama 3 ja DeepSeek R1), ja niiden koko vaihtelee alle 1 Gt:sta yli 13 Gt:aan.
Lemonade tunnistaa NPU:n automaattisesti ja asentaa **FastFlowLM NPU** -taustajärjestelmän.

<!-- @os:windows -->
> **Vinkki:** Saadaksesi parhaan NPU-suorituskyvyn, ota turbotila käyttöön:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Mallien vaihtaminen

Vaiheen 6 muistikorttisovellus toimii myös NPU-malleilla, vaihda vain mallin nimi:

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

1. **Yhdistä suosikkisovelluksesi**: Lemonade toimii suoraan käyttöönotosta [VS Code Copilotin](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI:n](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continuen](https://lemonade-server.ai/docs/server/apps/continue/), [n8n:n](https://n8n.io/integrations/lemonade-model/) ja [monien muiden](https://lemonade-server.ai/marketplace) kanssa.

2. **Selaa lisää malleja**: Tutustu koko [mallikirjastoon](https://lemonade-server.ai/docs/server/server_models/) löytääksesi malleja, jotka on optimoitu koodaukseen, päättelyyn, näkemiseen ja muuhun. Käytä Lemonade-sovellusta tai `lemonade list` -komentoa nähdäksesi, mitä on saatavilla.

3. **Vapauta ROCm GPU-kiihdytys**: Jos sinulla on tuettu AMD GPU, vaihda ROCm-taustajärjestelmään: `lemonade config set llamacpp.backend=rocm`. Katso [tuetut AMD GPU:t](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Lue koko API-spesifikaatio**: Lemonade tukee chat-täydennyksiä, upotuksia, äänen litterointia, kuvien luontia, puheeksi muuntamista ja muuta. Katso [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) kaikkien päätepisteiden osalta.

5. **Osallistu**: Lemonade on avoimen lähdekoodin projekti. Tutustu [osallistumisoppaaseen](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) ja etsi [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) -merkittyjä tehtäviä.