<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Tämä ohje vaatii vähintään **32 Gt** järjestelmämuistia.
<!-- @device:end -->

## Yleiskatsaus

Koodausagentit ovat tehokkaita työkaluja, jotka antavat kehittäjille mahdollisuuden tehdä yhteistyötä suurten kielimallien (LLM) tukemien tekoälyagenttien kanssa. Ne voidaan upottaa kehitysympäristöön, kuten päätteeseen tai VS Codeen, mikä mahdollistaa saumattoman integroinnin kehittäjän työnkulkuun.

Tässä opastuksessa näytetään, miten Cline, VS Code ja LM Studio otetaan käyttöön koodausagentin suorittamiseksi kokonaan paikallisella koneella.

## Mitä opit

* Miten VS Codea käytetään Cline-koodausagentin kanssa ohjelmistosuunnittelutehtävien tukena.
* Miten Cline määritetään kommunikoimaan LM Studion kanssa koodausagenttien paikallista päättelyä varten.
* Miten paikallisia koodausagentteja käytetään todellisten ohjelmistosuunnittelutehtävien ratkaisemiseen. 

<!-- @device:halo_box,halo,stx,krk -->
## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomautus**: Jos VS Code ei ole asennettuna, voit asentaa sen Ryzen AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston edellytysten asentaminen

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lmstudio,vscode -->
<!-- @prereq:lmstudio-models-qwen3-coder-30b,lmstudio,vscode -->

## LM Studion käynnistäminen ja määrittäminen

Käytämme LM Studiota palvelemaan koodausagenttia käyttävää LLM:ää.

- Kirjoita hakupalkkiin `LM Studio` ja käynnistä sovellus. Sinua tervehtii seuraava näkymä.

![LM Studion aloitusnäyttö](assets/initial-lm-studio.png)

Seuraavaksi meidän täytyy ladata LLM järjestelmään. Käytämme `Qwen3-Coder-30B-A3B`-mallia suurella kontekstipituudella. (Käytä Model-välilehteä sen asentamiseen, jos et ole vielä tehnyt niin).
- Napsauta LM Studio -ikkunan yläreunan hakupalkkia tai paina `CTRL+L`. Napsauta kytkintä `Manually choose model load parameters` ja napsauta sitten Qwen3-Coder-30B-A3B-mallia.
- Muuta kontekstipituus arvosta `4096` arvoon `32768` ja varmista, että `GPU Offload` on maksimissaan. Napsauta sitten `Load Model`

![Mallin valitseminen](assets/model-list-zoomed.png)

Käytämme suurta kontekstipituutta, jotta agentti pystyy käsittelemään laajoja koodikantoja ja muistamaan tehdyt muutokset.

![Mallin määrittäminen](assets/selecting-model-zoomed.png)

Seuraavaksi meidän täytyy ottaa käyttöön LM Studio Server. 
- Napsauta LM Studion vasemmassa reunassa olevaa Developer-välilehteä tai paina `CTRL+2`.
- Tarkista tilan vaihtokytkin ja varmista, että se on asennossa `Running`.

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
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
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
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## VS Coden käynnistäminen ja määrittäminen

Asennamme Cline-laajennuksen VS Codeen ja yhdistämme sen juuri luomaamme LM Studio -palvelimeen.
- Kirjoita hakupalkkiin `VS Code` ja käynnistä sovellus.
- Napsauta VS Coden vasemmassa reunassa olevaa `Extensions`-kuvaketta ja hae `Cline`. Napsauta sitten `Install`-painiketta. 

![Cline-laajennuksen asentaminen](assets/installing-cline-vscode-extension.png)

- Vasemmassa reunassa pitäisi nyt näkyä Cline-kuvake. Napsauta sitä avataksesi Clinen. Esiin tulee ikkuna, jossa kysytään `How will you use Cline?`. Koska käytämme paikallista LLM:ää, jota ajetaan LM Studion kautta, valitse `Bring my own API Key` ja napsauta `Continue`. 

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

Seuraavaksi meidän täytyy määrittää Cline kommunikoimaan juuri perustamamme LM Studio -palvelimen kanssa. 
- Aseta API Provider -asetukseksi `LM Studio` ja malliksi `Qwen3-Coder-30B-A3B-GGUF`. 

>**Vinkki**: Uudempia malleja saattaa olla saatavilla. Harkitse Qwen3.6-mallien lataamista ja niihin siirtymistä, jos haluat.


![Mallin määrittäminen](assets/cline-model-configuration-zoomed.png)

## Ensimmäisen projektin luominen

Käytetään paikallista agenttiamme verkkosivuston luomiseen! Avaa VSCode haluamaasi hakemistoon, johon Cline luo tiedostot.
- Tee tämä valitsemalla VS Coden vasemmasta yläkulmasta `File -> Open Folder` ja valitse esimerkiksi `Documents`-kansio.

![Tyhjä VS Code -kansio](assets/open-cline-test.png)

Nyt olemme valmiita antamaan kehotteen paikalliselle koodausagentille. 
- Napsauta vasemmassa reunassa olevaa Cline-laajennusta ja syötä kehote agentin käynnistämiseksi. Käytetään esimerkkinä seuraavaa kehotetta:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agentti alkaa tämän jälkeen luoda tiedostoja kehotteen mukaisesti. Käyttäjänä voit seurata koodin generoitumista VS Codessa alla näkyvällä tavalla. Saatat joutua napsauttamaan `Save`-painiketta joka kerta, kun Cline haluaa luoda tiedoston. 

![Clinen koodin generointi](assets/cline-code-generation.png)

Ohjelmiston luomisen jälkeen agentin työ on valmis, ja voit ajaa sovelluksen. Tässä tapauksessa agentti kirjoitti kolme tiedostoa: `index.html`, `script.js` ja `styles.css`. Kaksoisnapsauttamalla HTML-tiedostoa voimme ladata ja käyttää luotua verkkosivustoa.

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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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

Verkkosivuston luomisen jälkeen voit jatkaa yhteistyötä Clinen kanssa parantaaksesi sivustoa. Kaksi mahdollista parannusta ovat:

- **Dokumentaatio**: Kehotteen `Add a README` antaminen agentille riittää siihen, että agentti luo `README.md`-tiedoston, joka dokumentoi verkkosivuston.
- **Animaatio**: Anna mallille kehote `Add an animation that visually represents a large language model running on a laptop.`, jotta sivustolle luodaan animaatio.

Kannustamme lukijaa kokeilemaan muiden sovellusten luomista tällä kokoonpanolla. Alla on muutamia hauskoja esimerkkejä, joita olemme kokeilleet:

- **Retropeliklassikot**: Kokeile muita kehotteita. Agentin voi myös olla hauska luoda retrotyylisiä pelejä Pythonilla `PyGame`-pakettia käyttäen seuraavalla kehotteella:

```code
Create a simple pong game using the PyGame python package.
```

- **Data-analyysi**: Yksi alue, jolla koodausagentit ovat erityisen hyödyllisiä, on skriptien kirjoittaminen ja data-analyysi. Tämä kehote havainnollistaa paikallisen mallin kykyä luoda data-analyysiohjelmistoa osakekurssien visualisointia varten:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Resurssit

Alla on lisäresursseja, joiden avulla voit oppia lisää Coding Agenteista, Clinestä ja työkuormien ajamisesta

* Lisätietoja AMD:n ja LM Studion kumppanuudesta ja integraatiosta: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD:n blogikirjoitus, jossa käydään läpi Clinen käyttöä AMD Ryzen™ AI- ja Radeon™-näytönohjaimilla: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Clinen blogikirjoitus koodausagenttien paikallisesta ajamisesta AI-tietokoneilla: https://cline.bot/blog/local-models-amd