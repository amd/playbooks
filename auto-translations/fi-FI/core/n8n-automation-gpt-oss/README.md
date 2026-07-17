<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tämä playbook käyttää erityisiä tageja, joita GitHub ei pysty renderöimään. Vieraile osoitteessa [amd.com/playbooks](https://amd.com/playbooks) nähdäksesi tämän sisällön oikein.
<!-- @github-only:end -->

## Yleiskatsaus

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Tämä playbook vaatii vähintään **32 Gt** järjestelmämuistia.
<!-- @device:end -->

n8n on työnkulun automatisointialusta, jonka avulla voit yhdistää sovelluksia ja palveluita visuaalisen solmupohjaisen editorin avulla.

Tämä playbook opettaa sinulle, kuinka voit luoda tekoälypohjaisen talousutisten tiivistäjän, joka hakee AP Newsin taloussivuston sisältöä, poimii tärkeimmät otsikot ja käyttää paikallisesti järjestelmälläsi toimivaa LLM:ää sijoittajakeskeisen yhteenvedon luomiseen.

## Mitä opit

- Kuinka asentaa ja käynnistää n8n
- Valmiiksi rakennetun työnkulun tuominen ja määrittäminen
- Yhdistäminen Lemonadeen n8n:n natiivin integraation avulla
- Työnkulun solmujen ja tietovirran ymmärtäminen

## Mikä on Lemonade?

[Lemonade](https://lemonade-server.ai) on paikallinen LLM-palvelualusta, joka on rakennettu AMD-laitteistolle. Se tarjoaa OpenAI-yhteensopivan API:n, joka toimii kokonaan omalla koneellasi – tietosi eivät koskaan poistu laitteeltasi.

Tässä playbookissa käytämme Lemonadea paikallisen LLM:n palvelemiseen, johon n8n yhdistää tekoälypohjaisiin tehtäviin.

n8n sisältää **natiivin Lemonade-solmun** (`Lemonade Chat Model`), joka tarjoaa ensiluokkaisen integraation – manuaalista konfigurointia ei tarvita. Tämä tekee paikallisen LLM:n yhdistämisestä automatisointityönkulkuihin suoraviivaista.

## Muistikonfiguraation asettaminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmistoedellytysten asentaminen
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
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
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## n8n:n asentaminen
<!-- @os:windows -->
Asenna n8n globaalisti npm:n avulla.

> **Huomio**: Saatat nähdä joitakin npm-varoituksia. Tämä on odotettua.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Vinkki**: Windows-käyttäjien saattaa olla tarpeen muokata PowerShell-suorituskäytäntöään (esim.
> asettamalla se RemoteSigned- tai Unrestricted-tilaan) ennen joidenkin PowerShell-komentojen suorittamista.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH-ongelma**: Jos `n8n --version` ilmoittaa, että komentoa ei löydy, varmista, että npm:n globaali bin-hakemisto on käyttäjän `PATH`-muuttujassa. Tavallinen asennuspolku on `C:\Users\<username>\AppData\Roaming\npm`. 
> Lisää tämä käyttäjän polkuun (Muokkaa järjestelmän ympäristömuuttujia > Ympäristömuuttujat > Muokkaa käyttäjän polkua) ja lataa terminaali uudelleen.

<!-- @os:end -->

<!-- @os:linux -->
Käytämme nyt Podman-palvelua n8n-asennuksemme kontainerointiin.

Lataa seuraava tiedosto haluamaasi hakemistoon: [compose.yml](assets/compose.yml)

Suorita kyseisessä hakemistossa seuraava komento:
```bash
podman compose up -d
```

Tämän pitäisi asentaa n8n ja kirjoittaa pysyvään tallennustilaan.

Käynnistä n8n kirjoittamalla `localhost:5678` selaimen osoitepalkkiin.
<!-- @os:end -->

<!-- @os:windows -->
## n8n:n käynnistäminen

Käynnistä n8n terminaalista:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n käynnistää paikallisen verkkopalvelimen. Paina `'o'` tai avaa selaimesi osoitteeseen `http://localhost:5678` päästäksesi editoriin.
<!-- @os:end -->


> **Vinkki**: Pidä terminaali-ikkuna auki n8n:ää käyttäessäsi. Sen sulkeminen saattaa pysäyttää palvelimen.

## Lemonaden käynnistäminen

Lemonade on paikallinen palvelin, joka ajaa mallia ja yhdistää n8n:ään.

<!-- @os:linux -->
Avaa Lemonade-käyttöliittymä napsauttamalla tehtäväpalkin Lemonade-kuvaketta. Voit selata malleja, taustajärjestelmiä ja ladata esiasennettuja malleja täältä.
<!-- @os:end -->

<!-- @os:windows -->
Avaa Lemonade-käyttöliittymä napsauttamalla Lemonade-kuvaketta. Napsauta hiiren oikealla painikkeella ilmaisinalueen kuvaketta avataksesi sovelluksen. Tämän jälkeen voit lisätä malleja, taustajärjestelmiä ja ladata esiasennettuja malleja.
<!-- @os:end -->

>**Vinkki**: Kun Lemonade on käynnissä, sen käyttöliittymä on myös saatavilla osoitteessa http://localhost:13305

Vaihtoehtoisesti voit avata terminaalin ja suorittaa `lemonade list` nähdäksesi asennetut mallit. Suorita sitten:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## Työnkulun määrittäminen

### Vaihe 1: Rekisteröidy tai kirjaudu sisään n8n:ään

Kun avaat n8n:n ensimmäistä kertaa, sinua pyydetään luomaan tili tai kirjautumaan sisään:

1. Avaa `http://localhost:5678` selaimessasi
2. Luo uusi paikallinen tili sähköpostiosoitteellasi tai kirjaudu sisään, jos sinulla on jo tili
3. Kirjautumisen jälkeen näet n8n-kojelaudan

> **Vinkki**: Jos olet lukittu ulos tililtäsi, kokeile `n8n user-management:reset`

### Vaihe 2: Tuo työnkulku

Olemme toimittaneet valmiiksi rakennetun työnkulun, jonka voit tuoda suoraan:

1. Lataa seuraava työnkulutiedosto: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Napsauta **Start from Scratch** avataksesi työnkulkueditorin. Vaihtoehtoisesti napsauta + -painiketta vasemmassa yläkulmassa ja sitten **Add workflow**.
3. Napsauta **...** -valikkoa (kolme pistettä) oikeassa yläpalkissa ja valitse **Import from file**
4. Valitse ladattu `financial-news-workflow.json`-tiedosto
5. Työnkulku ilmestyy kankaalle


### Vaihe 3: Työnkulun ymmärtäminen

Tuotu työnkulku sisältää 9 yhdistettyä solmua:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Solmu | Tarkoitus |
|------|---------|
| **When clicking 'Execute workflow'** | Manuaalinen käynnistin työnkulun aloittamiseksi |
| **Fetch Financial News Webpage** | HTTP GET -pyyntö osoitteeseen `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Odotussolmu, joka varmistaa sivun sisällön täydellisen latautumisen |
| **Extract News Headlines & Text** | HTML-solmu, joka poimii otsikot, toimittajien valinnat, tärkeimmät uutiset ja alueelliset uutiset CSS-valitsimien avulla |
| **Clean Extracted News Data** | Set-solmu, joka yhdistää kaikki poimitut tiedot yhdeksi tekstikentäksi |
| **AI Financial News Summarizer** | Tekoälyagentti, joka käsittelee uutiset talousanalyytikon järjestelmäkehotteen avulla |
| **Lemonade Chat Model** | Yhdistää paikalliseen Lemonade-palvelimeen, joka ajaa LLM:ää |
| **Structured Output Parser** | Muotoilee tekoälyn tulosteen jäsennellyksi JSON-muodoksi |
| **Convert to File** | Muuntaa yhteenvedon ladattavaksi tiedostoksi |

### Vaihe 4: Lemonade-tunnistetietojen määrittäminen

Ennen työnkulun suorittamista sinun on yhdistettävä se paikalliseen Lemonade-palvelimeesi:

1. Kaksoisnapsauta **Lemonade Chat Model** -solmua n8n:ssä
2. Valitse pudotusvalikosta **Credential to connect with** ja valitse **Create New Credential**
3. Syötä alla olevan taulukon arvot ja napsauta tallenna.
4. Valitse asianmukainen malli, jonka olet ladannut Lemonade-palvelimeen.

  | Kenttä | Arvo |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Huomio**: Ennen testaamista suorita `lemonade status` terminaalissa varmistaaksesi, että Lemonade-palvelin on käynnissä.
<!-- @device:halo_box -->
> Tämä työnkulku käyttää GPT-OSS-120B:tä, joka on esiasennettuna Lemonadessa. Voit vaihtaa tämän muihin ladattuihin malleihin Lemonade Chat Model -solmun asetuksissa.
<!-- @device:end -->

### Vaihe 5: Testaa työnkulku

1. Varmista, että Lemonade on käynnissä ja malli on ladattuna
2. Napsauta **Execute workflow** kankaan alaosassa keskellä
3. Seuraa jokaisen solmun suorittamista vasemmalta oikealle – ne muuttuvat vihreiksi valmistuessaan
4. Kaksoisnapsauta **AI Financial News Summarizer** -solmua nähdäksesi luodun yhteenvedon alareunassa.
5. Kaksoisnapsauta **Convert to File** -solmua ladataksesi vastaavan tekstitiedoston alareunasta.

## Tekoälyagentin ymmärtäminen

AI Financial News Summarizer käyttää talousanalyysiä varten suunniteltua järjestelmäkehottetta:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agentti vastaanottaa puhdistetun uutisdatan ja tuottaa jäsennellyn yhteenvedon markkinatunnelmasta.

### Työnkulun tallentaminen

Napsauta työnkulun nimeä yläosassa ja nimeä se uudelleen halutessasi. Työnkulut tallentuvat automaattisesti työskennellessäsi.

## Seuraavat vaiheet

- **Aikatauluta automaatio**: Korvaa manuaalinen käynnistin **Schedule Trigger** -käynnistimellä päivittäistä ajoa varten
- **Lähetä ilmoituksia**: Lisää **Discord**-, **Slack**- tai **Email**-solmu yhteenvetojen vastaanottamiseksi
- **Kokeile eri malleja**: Vaihda malli Lemonade Chat Model -solmussa kokeillaksesi eri LLM:iä
- **Mukauta poimintaa**: Muokkaa HTML Extract -solmun CSS-valitsimia kohdistamaan eri uutisosioihin
- **Kokeile eri taustajärjestelmiä**: n8n tukee myös [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model):a, LM Studio:ta ja muita paikallisia LLM-taustajärjestelmiä

### Tutustu n8n-malleihin

n8n:llä on satoja valmiiksi rakennettuja työnkulkumalleja. Selaa virallista mallikirjastoa osoitteessa:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Etsi "AI", "LLM" tai "automation" löytääksesi työnkulkuja, joita voit tuoda ja mukauttaa.

Lisätietoja löydät [n8n-dokumentaatiosta](https://docs.n8n.io/).