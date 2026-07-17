<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

## Yleiskatsaus

Koodausagentit ovat tehokkaita työkaluja, jotka tukevat kehittäjiä yhteistyössä tekoälyagenttien kanssa, joiden taustalla toimivat suuret kielimallit (LLM). Ne voidaan integroida kehitysympäristöön, kuten terminaaliin tai VS Code -editoriin, mahdollistaen saumattoman liittämisen kehittäjän työnkulkuun.

Tässä opetusohjelmassa esitellään, kuinka Clinea, VS Codea ja LM Studiota käytetään koodausagentin ajamiseen kokonaan paikallisella koneella.

## Mitä opit

* Kuinka ajaa VS Codea Cline-koodausagentin kanssa ohjelmistokehitystehtävien tueksi.
* Kuinka määrittää Cline kommunikoimaan LM Studion kanssa koodausagenttien paikallista inferenssiä varten.
* Kuinka käyttää paikallisia koodausagentteja todellisten ohjelmistokehitystehtävien ratkaisemiseen.

## Muistikonfiguraation asettaminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomio**: Jos VS Code ei ole asennettuna, voit asentaa sen Ryzen AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmistoedellytysten asentaminen

<!-- @require:lmstudio,vscode -->

## LM Studion käynnistäminen ja määrittäminen

Käytämme LM Studiota koodausagenttia ohjaavan LLM:n palvelemiseen.

- Kirjoita hakupalkkiin `LM Studio` ja käynnistä sovellus. Sinut toivottaa tervetulleeksi seuraava sivu.

![LM Studio -aloitusnäyttö](assets/initial-lm-studio.png)

Seuraavaksi meidän on ladattava LLM järjestelmään. Käytämme `Qwen3-Coder-30B-A3B`-mallia suurella kontekstin pituudella. (Käytä Model-välilehteä sen asentamiseen, jos et ole vielä tehnyt niin).
- Napsauta LM Studio -ikkunan yläosassa olevaa hakupalkkia tai paina `CTRL+L`. Napsauta kytkintä `Manually choose model load parameters` ja napsauta sitten Qwen3-Coder-30B-A3B-mallia.
- Muuta kontekstin pituus `4096`:sta `32768`:aan ja varmista, että `GPU Offload` on maksimissaan. Napsauta sitten `Load Model`.

![Mallin valitseminen](assets/model-list-zoomed.png)

Käytämme suurta kontekstin pituutta, jotta agentti voi käsitellä suuria koodikantoja ja muistaa tehdyt muutokset.

![Mallin määrittäminen](assets/selecting-model-zoomed.png)

Seuraavaksi meidän on otettava LM Studio -palvelin käyttöön.
- Napsauta Developer-välilehteä tai paina `CTRL+2` LM Studiossa vasemmalla.
- Tarkista tilakytkimen asento ja varmista, että se on asetettu tilaan `Running`.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![Palvelimen tila](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## VS Coden käynnistäminen ja määrittäminen

Asennamme Cline-laajennuksen VS Codeen ja yhdistämme sen juuri luomaamme LM Studio -palvelimeen.
- Kirjoita hakupalkkiin `VS Code` ja käynnistä sovellus.
- Napsauta VS Coden vasemmassa sarakkeessa olevaa `Extensions`-kuvaketta ja etsi `Cline`. Napsauta sitten `Install`-painiketta.

![Cline-laajennuksen asentaminen](assets/installing-cline-vscode-extension.png)

- Vasemmalla pitäisi näkyä Cline-kuvake. Napsauta sitä avataksesi Clinen. Näkyviin tulee ikkuna, jossa kysytään `How will you use Cline?` Koska käytämme LM Studion kautta ajettavaa paikallista LLM:ää, valitse `Bring my own API Key` ja napsauta `Continue`.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Tilin luominen](assets/cline-how-will-you-use-cline-zoomed.png)

Seuraavaksi meidän on määritettävä Cline kommunikoimaan asettamamme LM Studio -palvelimen kanssa.
- Aseta API-palveluntarjoajaksi `LM Studio` ja malliksi `Qwen3-Coder-30B-A3B-GGUF`.

>**Vinkki**: Uudempia malleja saattaa olla saatavilla. Harkitse Qwen3.6-mallien lataamista ja vaihtamista niihin, jos haluat.


![Mallin määrittäminen](assets/cline-model-configuration-zoomed.png)

## Ensimmäisen projektin luominen

Käytetään paikallista agenttiamme verkkosivuston luomiseen! Avaa VSCode haluamaasi hakemistoon, johon Cline luo tiedostot.
- Tee tämä siirtymällä VS Coden vasemmassa yläkulmassa kohtaan `File -> Open Folder` ja valitsemalla kansio, kuten `Documents`.

![VS Code tyhjä kansio](assets/open-cline-test.png)

Nyt olemme valmiita antamaan kehotteen paikalliselle koodausagentille.
- Napsauta vasemmassa sarakkeessa olevaa Cline-laajennusta ja anna kehote agentin käynnistämiseksi. Esimerkkinä käytetään seuraavaa kehotetta:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agentti alkaa sitten luoda tiedostoja kehotteen mukaisesti. Käyttäjänä voit seurata koodin luomista VS Codessa alla esitetyllä tavalla. Sinun saattaa täytyä napsauttaa `Save` aina, kun Cline haluaa luoda tiedoston.

![Clinen koodin luominen](assets/cline-code-generation.png)

Ohjelmiston luomisen jälkeen agentti on valmis ja voit ajaa sovelluksen. Tässä tapauksessa agentti kirjoitti kolmeen tiedostoon: `index.html`, `script.js` ja `styles.css`. Kaksoisnapsauttamalla HTML-tiedostoa voimme ladata ja käyttää luotua verkkosivustoa.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

## Seuraavat vaiheet

Verkkosivuston luomisen jälkeen voit jatkaa Clinen kanssa työskentelyä sivuston parantamiseksi. Kaksi mahdollista parannusta ovat:

- **Dokumentaatio**: Agentin kehottaminen komennolla `Add a README` riittää siihen, että agentti luo `README.md`-tiedoston, joka dokumentoi verkkosivuston.
- **Animaatio**: Kehota mallia komennolla `Add an animation that visually represents a large language model running on a laptop.` lisätäksesi animaation verkkosivustolle.

Kannustamme lukijaa kokeilemaan muiden sovellusten luomista tällä asetuksella. Alla on joitakin hauskoja esimerkkejä, joita olemme kokeilleet:

- **Retro-arkadiapelit**: Kokeile muita kehotteita. Voi myös olla hauskaa antaa agentin luoda retro-tyylisiä pelejä Pythonilla käyttäen `PyGame`-pakettia seuraavalla kehotteella:

```code
Create a simple pong game using the PyGame python package.
```

- **Data-analyysi**: Yksi alue, jolla koodausagentit ovat erityisen hyödyllisiä, on skriptaus ja data-analyysi. Tässä on kehote, joka esittelee paikallisen mallin kykyä luoda data-analyysiohjelmistoa osakkeiden hintojen visualisointiin:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Resurssit

Alla on lisäresursseja koodausagenteista, Clinesta ja työkuormien ajamisesta lisätietojen saamiseksi.

* Lisätietoja AMD:n ja LM Studion kumppanuudesta ja integraatiosta: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD:n blogi Clinen ajamisesta AMD Ryzen™ AI- ja Radeon™-näytönohjaimilla: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Clinen blogi koodausagenttien paikallisesta ajamisesta tekoälytietokoneilla: https://cline.bot/blog/local-models-amd