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

## Yleiskatsaus

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Tämä ohjekirja edellyttää vähintään **32 Gt** järjestelmämuistia.
<!-- @device:end -->

n8n on työnkulkujen automatisointialusta, jonka avulla voit yhdistää sovelluksia ja palveluita visuaalisen, solmupohjaisen editorin avulla.

Tämä ohjekirja opastaa sinut asentamaan tekoälypohjaisen talousuutisten tiivistäjän, joka kerää tietoja AP News -sivuston talousosiosta, poimii keskeiset otsikot ja käyttää järjestelmässäsi paikallisesti ajettavaa suurta kielimallia (LLM) sijoittajille suunnatun yhteenvedon luomiseen.

## Mitä opit

- Kuinka asentaa ja käynnistää n8n
- Valmiiksi rakennetun työnkulun tuominen ja määrittäminen
- Yhteyden muodostaminen Lemonadeen n8n:n natiivin integraation avulla
- Työnkulun solmujen ja tietovirran ymmärtäminen

## Mikä on Lemonade?

[Lemonade](https://lemonade-server.ai) on AMD-laitteistolle rakennettu paikallinen LLM-palvelualusta. Se tarjoaa OpenAI-yhteensopivan API:n, joka toimii kokonaan omalla koneellasi – tietosi eivät koskaan poistu laitteeltasi.

Tässä ohjekirjassa käytämme Lemonadea paikallisen LLM:n tarjoamiseen, johon n8n muodostaa yhteyden tekoälypohjaisia tehtäviä varten.

n8n sisältää **natiivin Lemonade-solmun** (`Lemonade Chat Model`), joka tarjoaa ensiluokkaisen integraation – manuaalista määritystä ei tarvita. Tämä tekee paikallisen LLM:n yhdistämisestä automaatiotyönkulkuihin suoraviivaista.

## Muistin määrityksen asettaminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen
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

> **Huom**: Saatat nähdä joitakin npm-varoituksia. Tämä on odotettavissa.

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
> **Vinkki**: Windows-käyttäjien on ehkä muutettava PowerShellin suoritustapaperiaatetta (esim.
> asettamalla se arvoon RemoteSigned tai Unrestricted) ennen tiettyjen Powershell-komentojen suorittamista.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH-ongelma**: Jos `n8n --version` ilmoittaa, ettei komentoa löydy, varmista, että npm:n globaali bin-hakemisto on käyttäjän `PATH`-muuttujassa. Tavallinen asennuspolku on `C:\Users\<username>\AppData\Roaming\npm`.
> Lisää tämä käyttäjän polkuun (Muokkaa järjestelmän ympäristömuuttujia > Ympäristömuuttujat > Muokkaa käyttäjän polkua) ja lataa terminaali uudelleen.

<!-- @os:end -->

<!-- @os:linux -->
Käytämme nyt Podman-palvelua n8n-asennuksemme konteinerointiin.

Lataa seuraava tiedosto valitsemaasi hakemistoon: [compose.yml](assets/compose.yml)

Suorita kyseisessä hakemistossa seuraava komento:
```bash
podman compose up -d
```

Tämän pitäisi asentaa n8n ja kirjoittaa pysyvään tallennustilaan.

Käynnistä n8n kirjoittamalla `localhost:5678` selaimesi osoitepalkkiin.
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
n8n käynnistää paikallisen web-palvelimen. Paina `'o'` tai avaa selaimesi osoitteeseen `http://localhost:5678` päästäksesi editoriin.
<!-- @os:end -->


> **Vinkki**: Pidä terminaali-ikkuna auki n8n:ää käyttäessäsi. Sen sulkeminen saattaa pysäyttää palvelimen.

## Lemonaden käynnistäminen

Lemonade on paikallinen palvelin, joka ajaa mallia ja muodostaa yhteyden n8n:ään.

<!-- @os:linux -->
Avaa Lemonade GUI napsauttamalla Lemonade-kuvaketta tehtäväpalkissa. Voit selata malleja, taustajärjestelmiä ja ladata esiasennetut mallit täältä.
<!-- @os:end -->

<!-- @os:windows -->
Avaa Lemonade GUI napsauttamalla Lemonade-kuvaketta. Napsauta ilmaisinalueen kuvaketta hiiren oikealla painikkeella avataksesi sovelluksen. Sen jälkeen voit lisätä malleja, taustajärjestelmiä ja ladata esiasennetut mallit.
<!-- @os:end -->

>**Vinkki**: Kun Lemonade on käynnissä, sen GUI on käytettävissä myös osoitteessa http://localhost:13305

Vaihtoehtoisesti voit avata terminaalin ja ajaa komennon `lemonade list` nähdäksesi, mitkä mallit on asennettu. Suorita sitten:

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
3. Kun olet kirjautunut sisään, näet n8n-hallintapaneelin

> **Vinkki**: Jos jäät ulos tilistäsi, kokeile komentoa `n8n user-management:reset`

### Vaihe 2: Tuo työnkulku

Olemme tarjonneet valmiiksi rakennetun työnkulun, jonka voit tuoda suoraan:

1. Lataa seuraava työnkulkutiedosto: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Napsauta **Start from Scratch** avataksesi työnkulkueditorin. Vaihtoehtoisesti napsauta + -painiketta vasemmassa yläkulmassa ja valitse sitten **Add workflow**.
3. Napsauta **...**-valikkoa (kolme pistettä) oikeassa yläkulmassa ja valitse **Import from file**
4. Valitse ladattu `financial-news-workflow.json`-tiedosto
5. Työnkulku näkyy nyt työalueella
### Vaiheen 3 ymmärtäminen: Työnkulku

Tuotu työnkulku sisältää 9 toisiinsa yhdistettyä solmua:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Solmu | Tarkoitus |
|------|---------|
| **When clicking 'Execute workflow'** | Manuaalinen liipaisin työnkulun käynnistämiseen |
| **Fetch Financial News Webpage** | HTTP GET -pyyntö osoitteeseen `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Wait-solmu, joka varmistaa, että sivun sisältö on ladattu kokonaan |
| **Extract News Headlines & Text** | HTML-solmu, joka poimii otsikot, toimituksen valinnat, pääuutiset ja alueelliset uutiset CSS-valitsimien avulla |
| **Clean Extracted News Data** | Set-solmu, joka yhdistää kaiken poimitun tiedon yhdeksi tekstikentäksi |
| **AI Financial News Summarizer** | AI-agentti, joka käsittelee uutiset talousanalyytikon järjestelmäkehotteen avulla |
| **Lemonade Chat Model** | Yhdistää paikalliseen Lemonade-palvelimeen, jolla LLM on käynnissä |
| **Structured Output Parser** | Muotoilee AI:n tuloksen jäsennellyksi JSON-muodoksi |
| **Convert to File** | Muuntaa yhteenvedon ladattavaksi tiedostoksi |

### Vaihe 4: Määritä Lemonade-tunnistetiedot

Ennen työnkulun suorittamista sinun on yhdistettävä se paikalliseen Lemonade-palvelimeesi:

1. Kaksoisnapsauta **Lemonade Chat Model** -solmua n8n:ssä
2. Valitse avattavasta **Credential to connect with** -valikosta **Create New Credential**
3. Syötä alla olevan taulukon arvot ja valitse Tallenna.
4. Valitse asianmukainen malli, jonka olet ladannut Lemonade Serveriin.

  | Kenttä | Arvo |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Huomio**: Ennen testausta suorita `lemonade status` päätteessä varmistaaksesi, että Lemonade-palvelin on käynnissä.
<!-- @device:halo_box -->
> Tämä työnkulku käyttää GPT-OSS-120B-mallia, joka on esiasennettu Lemonadeen. Voit vaihtaa tämän toiseen ladattuun malliin Lemonade Chat Model -solmun asetuksissa.
<!-- @device:end -->

### Vaihe 5: Testaa työnkulku

1. Varmista, että Lemonade on käynnissä ja malli on ladattu
2. Napsauta **Execute workflow** -painiketta työtilan alaosan keskellä
3. Seuraa, kuinka kukin solmu suoritetaan vasemmalta oikealle – ne muuttuvat vihreiksi valmistuttuaan
4. Kaksoisnapsauta **AI Financial News Summarizer** -solmua nähdäksesi luodun yhteenvedon alapaneelissa.
5. Kaksoisnapsauta **Convert to File** -solmua ladataksesi vastaavan tekstitiedoston alapaneelissa.

## AI-agentin ymmärtäminen

AI Financial News Summarizer käyttää talousanalyysiin suunniteltua järjestelmäkehotetta:

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

Napsauta työnkulun nimeä yläreunassa ja nimeä se uudelleen halutessasi. Työnkulut tallentuvat automaattisesti työskennellessäsi.

## Seuraavat vaiheet

- **Ajasta automaatio**: Korvaa Manual Trigger **Schedule Trigger** -solmulla, jotta työnkulku suoritetaan päivittäin
- **Lähetä ilmoituksia**: Lisää **Discord**-, **Slack**- tai **Email**-solmu yhteenvetojen vastaanottamiseksi
- **Kokeile eri malleja**: Vaihda malli Lemonade Chat Model -solmussa kokeillaksesi erilaisia LLM-malleja
- **Mukauta poimintaa**: Muokkaa HTML Extract -solmun CSS-valitsimia kohdistaaksesi eri uutisosioihin
- **Kokeile eri taustajärjestelmiä**: n8n tukee myös [Ollamaa](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studiota ja muita paikallisia LLM-taustajärjestelmiä

### Tutustu n8n-malleihin

n8n:ssä on satoja valmiiksi rakennettuja työnkulkumalleja. Selaa virallista mallikirjastoa osoitteessa:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Etsi "AI", "LLM" tai "automation" löytääksesi työnkulkuja, joita voit tuoda ja mukauttaa.

Lisätietoja saat [n8n-dokumentaatiosta](https://docs.n8n.io/).

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