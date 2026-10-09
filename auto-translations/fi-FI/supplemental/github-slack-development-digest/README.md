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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Yleiskatsaus

Kehittäjät käyttävät paljon aikaa pieniin toistuviin kierroksiin: merkittyjen pull requestien tarkisteluun, GitHub-kommentteihin vastaamiseen, uusien issueiden priorisointiin, Slack-keskusteluiden muuntamiseen seisontapalaverimuistiinpanoiksi tai häiriöiden jälkiselvityksiksi sekä julkaisu- tai tutkimussignaalien seuraamiseen.
Jokainen kierros on tuttu, mutta se vaatii silti harkintaa: oikean kontekstin keräämistä, sen päättämistä mikä on tärkeää, ja selkeän päivityksen julkaisemista siellä, missä tiimi jo työskentelee.

[OpenHands-automaatiot](https://docs.openhands.dev/openhands/usage/automations/overview) muuttavat nuo kierrokset ajastetuiksi tai tapahtumapohjaisiksi agenttikeskusteluiksi: ajoiksi, joissa AI-ohjelmistoagentti voi lukea kontekstia, kutsua työkaluja ja tuottaa päivityksen.
OpenHands-laajennuskatalogin jaetut automaatiomallit noudattavat tätä kaavaa GitHub-pull requestien tarkistelussa, repositorioiden seurannassa, Linear-issueiden priorisoinnissa, häiriöiden jälkiselvityksissä, Slack-seisontapalaveridigesteissä ja tutkimuskatsauksissa: automaatio herää, käyttää konfiguroituja integraatioita, kuten GitHubia tai Slackia, kontekstin hakemiseen, päättelee tämän kontekstin pohjalta suurella kielimallilla (LLM) ja kirjoittaa tuloksen takaisin.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) on paikallinen ohjaustaso näiden automaatioiden rakentamiseen ja testaamiseen.
Tässä ohjeessa se ajaa OpenHands Agent Serveriä, taustaprosessia joka suorittaa agenttikeskusteluja, ja yhdistää agentin ulkoisiin palveluihin, kuten GitHubiin ja Slackiin.

Jotta työnkulku pysyisi AMD-järjestelmässäsi, agentti keskustelee paikallisen mallin kanssa, jota tarjoilee Lemonade Server.
Lemonade altistaa tämän mallin OpenAI-yhteensopivan API:n kautta, joten Agent Canvas voi konfiguroida sen kuin etäisen OpenAI-tyylisen päätepisteen, samalla kun malli, kehote ja työnkulun konteksti pysyvät paikallisina.

Tässä ohjeessa rakennat yhden konkreettisen automaation: ajastetun GitHub-to-Slack-kehitysdigestin.
Se käyttää GitHubia viimeaikaisen repositoriotoiminnan tarkasteluun, Slackia digestin julkaisuun, Agent Canvas -API-kutsuja automaation konfigurointiin ja testaamiseen sekä Lemonadea LLM:n paikalliseen ajamiseen.

![Arkkitehtuurikaavio, joka näyttää GitHub MCP:n, OpenHands-automaation, Lemonade Serverin ja Slack MCP:n](assets/00-architecture-overview.png)

## Mitä opit

- Kuinka käynnistät Lemonade Serverin ja varmistat, että paikallinen malli vastaa keskustelupyyntöihin
- Kuinka käynnistät Agent Canvasin ja ohjaat sen Agent Serverin osoittamaan paikalliseen LLM:ään
- Kuinka asennat GitHub- ja Slack Model Context Protocol (MCP) -palvelimet Agent Server -API:n kautta
- Kuinka luot ja käynnistät ajastetun OpenHands-automaation, joka julkaisee kehitysdigestin Slackiin
- Kuinka vianmääritys tehdään yleisimmille paikallisen mallin ja automaation virheille

## Peruskäsitteet

| Käsite | Mikä se on | Mihin se sijoittuu tässä ohjeessa |
| --- | --- | --- |
| Lemonade Server | Paikallinen LLM-tarjoilualusta, joka on rakennettu AMD-laitteistolle ja joka altistaa OpenAI-yhteensopivan API:n. Tietosi eivät koskaan poistu koneeltasi. | Ajaa mallia, joka tehostaa agenttia. |
| OpenHands Agent Server | Taustaprosessi, joka suorittaa OpenHands-agenttikeskusteluja. | Isännöi agenttia, sen LLM-profiilia ja sen MCP-palvelimia. |
| Agent Canvas | OpenHandsin paikallinen ohjaustaso, joka ajaa Agent Serveriä ja käyttöliittymää agenttiajojen tarkasteluun. | Käynnistää taustajärjestelmät ja tarjoaa API:n, jota kutsut. |
| MCP-palvelin | Model Context Protocol -palvelin, joka antaa agentille työkaluja ulkoiseen palveluun, kuten GitHubiin tai Slackiin. | Mahdollistaa agentin lukea GitHubia ja kirjoittaa Slackiin. |
| OpenHands-automaatio | Ajastettu tai tapahtumapohjainen agenttikeskustelu, joka hakee kontekstin, päättelee sen pohjalta ja kirjoittaa tuloksen jonnekin. | Tässä rakentamasi GitHub-to-Slack-digesti. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Koodausagentin työnkulut hyötyvät suuremmasta mallista ja kontekstikehyksestä.
> Käytä vähintään 32 Gt järjestelmämuistia, ja suosi 64 Gt tai enemmän suuremmille GGUF-malleille.
<!-- @device:end -->

## Muistikonfiguraation asettaminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Esivaatimukset

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas); host npm is only used by CI to resolve the MCP packages. -->
<!-- @prereq:docker,nodejs,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

Tarvitset:

- Lemonade Server asennettuna noudattaen tavallista [Lemonaden asennusopasta](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 tai uudempi ja `npm`, joita käytetään julkaistun Agent Canvas -komentorivityökalun asentamiseen ja MCP-palvelimien ajamiseen `npx`-komennolla.
- `uv`, Python-pakettienhallinta, jota Agent Canvas käyttää Agent Server -ympäristön rakentamiseen. Jos sitä ei ole vielä asennettu, asenna se [uv:n asennusoppaasta](https://docs.astral.sh/uv/getting-started/installation/).
- Tuore julkaistu `@openhands/agent-canvas`-paketti, jossa on skeemapohjaiset agenttiasetukset, `LLMSummarizingCondenserSettings.max_tokens` ja LLM:n `custom_tokenizer`-tuki.
- Python `transformers`-paketti saatavilla Agent Server -ympäristössä. Sitä tarvitaan keskustelupohjan tokenien laskentaan, kun `custom_tokenizer` on asetettu.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), asennettuna ja käynnissä. Windowsissa Agent Canvas -pino ajetaan julkaistusta Docker-levykuvasta, joka sisältää Node.js:n, `uv`:n, `transformers`-paketin ja `@openhands/agent-canvas`-paketin, joten niitä ei tarvitse asentaa isäntäkoneelle.
<!-- @os:end -->

- GitHub-token, jolla on lukuoikeus repositorioon, josta haluat yhteenvedon.
- Slack-bottitoken (`xoxb-...`), jolla on `chat:write`-oikeus ja kanavan lukuoikeus.
- Slack-tiimitunnus (`T...`).
- Slack-kanavatunnus (`C...`), johon digesti tulisi julkaista.

Kutsu Slack-sovellus kohdekanavaan ennen automaation testaamista.
## Tässä pelikirjassa käytetyt muuttujat

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

Näitä kahta muuttujaa käytetään alla olevissa vahvistuskomennoissa.
Malli, tokenisoija ja muut LLM-asetukset syötetään suoraan Agent Canvas -käyttöliittymään myöhemmissä vaiheissa, joten niiden kirjaimelliset arvot näytetään tarvittaessa suoraan tekstissä.

Seuraavat arvot syötetään Agent Canvas -käyttöliittymään myöhemmissä vaiheissa.
Aseta ne tähän, jotta voit kopioida ne käyttöön:

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

Käytä eksplisiittistä `owner/repo`-arvoa kohteelle `GITHUB_REPO_FILTER`.
Laajat organisaation yleismerkit voivat palauttaa liian paljon MCP-kontekstia paikallisille malleille.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Käynnistä Lemonade Server

Käynnistä malli Lemonade CLI:stä:

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **Valitse laitteistoosi sopiva malli.** `Qwen3.6-35B-A3B-GGUF` (~20 Gt) on vahva malli tähän työnkulkuun, mutta vaatii suuren muistivarannon.
> Jos laitteessasi on rajallisesti muistia tai GPU-VRAM:ia, valitse pienempi GGUF-malli Lemonade-mallikirjastosta ja käytä sen mallitunnusta (ja vastaavaa tokenisoijaa) koko tämän pelikirjan ajan.

> **Huomio:** Ensimmäinen `lemonade run` lataa mallin, jos sitä ei vielä ole saatavilla, mikä voi kestää hetken mallin koosta ja yhteydestäsi riippuen.

Lemonade tarjoaa OpenAI-yhteensopivan API:n osoitteessa:

```text
http://127.0.0.1:13305/api/v1
```

Valinnainen: jos Agent Canvas tai automaation suoritusohjelma ei ole samalla koneella, julkaise Lemonade-päätepiste suojatun tunnelin kautta ja käytä HTTPS-URL-osoitetta LLM-perus-URL-osoitteena.
[ngrok](https://ngrok.com/) tuo paikallisen portin internetiin suojatun HTTPS-URL-osoitteen kautta; se vaatii ilmaisen ngrok-tilin, ja korvaat kohdan `YOUR_NGROK_DOMAIN.ngrok-free.dev` omalla varatulla verkkotunnuksellasi:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Vahvista paikallinen malli

Varmista, että Lemonade voi tarjoilla valittua mallia:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Lähetä sitten pieni keskustelupyyntö:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

Lähetä sitten pieni keskustelupyyntö:

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

Jos tämä palauttaa `choices`-taulukon, Lemonade on valmis Agent Canvasia varten.

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
  "max_tokens": 64
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

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. Käynnistä Agent Canvas

<!-- @os:linux -->
Asenna julkaistu Agent Canvas -paketti ja käynnistä koko pino:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Jos globaali npm-asennus epäonnistuu käyttöoikeusvirheeseen, katso alta npm-käyttöoikeuksien vianmäärityskohta.

Oletusarvoisesti Agent Canvas käynnistyy osoitteessa `http://localhost:8000`.
Avaa kyseinen URL-osoite selaimessasi.
Portilla ei ole erityistä merkitystä—jos 8000 on jo käytössä, anna mikä tahansa vapaa portti käyttäen `--port` (tai `-p`).
Oletusarvoisen paikallisen taustajärjestelmän pitäisi näkyä terveenä aloitusnäytöllä.

> **Huomio:** Ensimmäinen käynnistys rakentaa Agent Serverin `uv`-hallinnoiman Python-ympäristön, joten taustajärjestelmän terveeksi raportoiminen voi kestää muutaman minuutin.

Komento `agent-canvas` käynnistää agenttipalvelimen, automaation taustajärjestelmän ja verkkokäyttöliittymän yhdessä.
Tarvitset vain tämän yhden komennon OpenHandsin ajamiseen paikallisesti.
Tämän pelikirjan loppuosa määrittää kaiken Agent Canvas -käyttöliittymän kautta selaimessasi.
<!-- @os:end -->

<!-- @os:windows -->
Käytä Windowsilla julkaistua Agent Canvas -säiliökuvaa Docker Desktopin kanssa.
Kuva sisältää Agent Serverin, automaation taustajärjestelmän ja verkkokäyttöliittymän, joten sinun ei tarvitse asentaa Node.js:ää, `uv`:tä tai CLI:tä isäntäkoneelle.

Luo ensin kokoonpano- ja työtilakansiot, jotka säiliö liittää:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Hae julkaistu kuva (noin 6 Gt; se on julkinen, joten kirjautumista ei vaadita):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Käynnistä sitten pino:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Avaa `http://localhost:8000/canvas` selaimessasi.
Jos portti 8000 on jo käytössä, yhdistä eri isäntäportti, esimerkiksi `-p 8080:8000`, ja avaa sen sijaan `http://localhost:8080/canvas`.

> **Huomio:** Ensimmäinen käynnistys rakentaa Agent Server -ympäristön säiliön sisällä, joten taustajärjestelmän terveeksi raportoiminen voi kestää muutaman minuutin.

Liitos `.openhands` säilyttää LLM-profiilisi, MCP-palvelimet ja automaatiot säiliön uudelleenkäynnistysten yli.
Tämän pelikirjan loppuosa määrittää kaiken Agent Canvas -käyttöliittymän kautta selaimessasi osoitteessa `http://localhost:8000/canvas`.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->
## 4. Paikallisen LLM:n määrittäminen käyttöliittymässä

Kun Agent Canvas käynnistetään ensimmäistä kertaa, se avaa käyttöönottoprosessin.
Tee prosessissa seuraavat vaiheet:

1. Pidä **OpenHands** valittuna agenttina ja napsauta **Next**.
2. Kohdassa **Set up your LLM** valitse **Advanced**.
3. Pidä **Authentication**-asetuksena **API key**.
4. Aseta **Custom Model**-kenttään `openai/Qwen3.6-35B-A3B-GGUF`.
5. Aseta **Base URL**-kenttään `http://127.0.0.1:13305/api/v1`.
6. Kirjoita **API Key**-kenttään mikä tahansa tyhjentymätön paikkamerkki, kuten `lemonade-local`. Lemonade ei vaadi oikeaa avainta, mutta OpenHands-asiakas tarvitsee arvon lähetettäväksi.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server toimii kontin sisällä, joten aseta **Base URL**-kenttään `http://host.docker.internal:13305/api/v1` osoitteen `http://127.0.0.1:13305/api/v1` sijaan.
> Kontin sisältä katsottuna `127.0.0.1` tarkoittaa itse konttia; `host.docker.internal` tavoittaa Windows-isäntäkoneella käynnissä olevan Lemonaden, ja Docker Desktop tarjoaa kyseisen isäntänimen automaattisesti.
<!-- @os:end -->

Yhteyskenttien tulisi näyttää tältä.
Käyttöliittymä peittää API-avainkentän.

![Agent Canvasin ensikäytön LLM Advanced -asetukset Lemonade-mallilla ja paikallisella Base URL -osoitteella](assets/01-llm-advanced-settings.png)

Valitse sitten **All** ja aseta paikallisen mallin lisäkentät:

1. Vieritä kohtaan **Custom Tokenizer** ja aseta se arvoon `Qwen/Qwen3.6-35B-A3B`.
2. Vieritä kohtaan **LiteLLM Extra Body** ja aseta se arvoon `{"enable_thinking": true}`.
3. Napsauta **Next**.

![Agent Canvasin ensikäytön LLM All -välilehti Qwenin mukautetulla tokenisoijalla](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvasin ensikäytön LLM All -välilehti määritetyllä LiteLLM extra body -asetuksella](assets/03-llm-all-extra-body-settings.png)

LLM-asetusten tulisi näyttää seuraavat tiedot:

| Kenttä | Arvo |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/`-etuliite kertoo LiteLLM:lle, että sen tulee käyttää OpenAI-yhteensopivaa pyyntömuotoilua Lemonade-päätepistettä vasten.
Mukautettu tokenisoija on GGUF-mallin alkuperäinen Hugging Face -tokenisoija; sen avulla OpenHands pystyy laskemaan samat keskustelumallin (chat-template) tokenit, jotka paikallinen mallipalvelin näkee.
Nykyinen ensikäytön LLM-lomake ei näytä kondensoijan (condenser) asetuksia.
Jos Agent Canvas -versiosi paljastaa kondensoijan asetukset myöhemmin kohdassa **Settings > LLM**, käytä arvoa `llm_summarizing` ja aseta enimmäistokenimäärä Lemonaden kontekstiikkunaa pienemmäksi, esimerkiksi `56000`.

## 5. GitHub- ja Slack-MCP-palvelimien asentaminen

Avaa Agent Canvas -käyttöliittymässä **Customize** (tai **Settings > MCP**) lisätäksesi MCP-palvelimet, jotka antavat agentille työkalut GitHubia ja Slackia varten.
Tunnusarvot lähetetään vain paikalliselle Agent Serverille, ja ne tallennetaan salattuina asetuksina.

<!-- @os:windows -->
> **Windows (Docker):** alla olevat `npx`-MCP-palvelinkomennot suoritetaan kontin sisällä, joka sisältää jo Node.js:n, joten isäntäkoneelle ei asenneta mitään ylimääräistä.
> Koska `.openhands` on liitetty (mounted), MCP-palvelimet ja niiden tunnukset säilyvät kontin uudelleenkäynnistysten yli.
<!-- @os:end -->

### GitHub-MCP-palvelin

Lisää uusi MCP-palvelin seuraavilla asetuksilla:

| Kenttä | Arvo |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = GitHub-tunnuksesi |

Käytä GitHub-tunnusta, jolla on lukuoikeus siihen repositorioon, josta haluat yhteenvedon.

### Slack-MCP-palvelin

Lisää toinen MCP-palvelin seuraavilla asetuksilla:

| Kenttä | Arvo |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = yhteenvetokanavasi tunnus |

Aseta `SLACK_CHANNEL_IDS`-arvoksi yhteenvetokanavan tunnus (sama arvo kuin `SLACK_DIGEST_CHANNEL`), jotta agentin ei tarvitse selata jokaista Slack-kanavaa.

Kun olet lisännyt molemmat palvelimet, käytä kummankin kohdalla **Test**-painiketta varmistaaksesi, että yhteys muodostuu ja työkalut tulevat näkyviin.
GitHub-palvelimen tulisi listata GitHub-työkalut, ja Slack-palvelimen tulisi listata Slack-työkalut.

![Agent Canvasin MCP-sivu, jossa GitHub- ja Slack-palvelimet on asennettu](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Yhteenvetoautomaation luominen

Avaa Agent Canvas -käyttöliittymässä **Automations**-sivu ja luo uusi automaatio:

1. Valitse **Create automation** ja valitse tyypiksi **Prompt preset**.
2. Aseta **Name**-kenttään `GitHub Development Digest to Slack`.
3. Aseta **Prompt**-kenttään seuraava teksti ja korvaa repositorio- ja kanavan paikkamerkit omilla arvoillasi:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. Aseta **Trigger**-asetukseksi **Cron** aikataululla `0 9 * * 1-5` (klo 9 arkisin) ja aseta **Timezone**-kenttään oma aikavyöhykkeesi, esimerkiksi `America/New_York`.
5. Aseta **Timeout**-arvoksi `900` sekuntia.
6. Tallenna automaatio.

Automaation tietosivulla näkyy uusi automaatio sekä sen cron-laukaisin ja luotu prompt-preset-aloituspiste (entrypoint).

![Agent Canvasin automaation tietosivu luomisen jälkeen](assets/05-automation-created.png)
## 7. Testaa automaatio

Agent Canvas -käyttöliittymän automaation tietosivulta:

1. Napsauta **Run now** (tai **Dispatch**) suorittaaksesi automaation kerran välittömästi.
2. Seuraa ajolistaa samalla sivulla. Uusimman ajon tilan pitäisi muuttua muotoon `COMPLETED`.
3. Avaa kohde-Slack-kanavasi. Sen pitäisi sisältää luotu yhteenveto.

Sinun ei tarvitse odottaa cron-aikataulun laukeamista—**Run now** käynnistää ajon pyynnöstä, jotta voit varmistaa, että kehote, MCP-yhteydet ja Slack-julkaisu toimivat ennen kuin luotat aikatauluun.

![Agent Canvas -automaation ajo valmistui onnistuneesti](assets/06-automation-run-completed.png)

![Slack-kanava, jossa näkyy luotu OpenHands-yhteenveto](assets/07-slackbot-message.png)

## Vianmääritys

<!-- @os:windows -->
- **Docker-portti 8000 on jo käytössä:** määritä eri isäntäportti, esimerkiksi `docker run ... -p 8080:8000 ...`, ja avaa `http://localhost:8080/canvas`.
- **`docker pull` epäonnistuu tunnistetietovirheeseen** (esimerkiksi "A specified logon session does not exist"): suorita pull-komento interaktiivisesta Windows-istunnosta tai nouda image etukäteen. Image on julkinen, joten `docker login` -komentoa ei tarvita.
- **Käyttöliittymä latautuu, mutta taustajärjestelmä ei ole kunnossa:** ensimmäinen käynnistys rakentaa Agent Server -ympäristön kontin sisälle. Odota hetki ja päivitä sivu, tarkista sitten edistyminen komennolla `docker logs <container>`.
- **Agent Canvas ei saa yhteyttä Lemonadeen kontista:** aseta LLM:n **Base URL** -arvoksi `http://host.docker.internal:13305/api/v1` (ei `127.0.0.1`), ja varmista, että Lemonade on käynnissä Windows-isäntäkoneella.
<!-- @os:end -->

- **Lemonade on pois päältä:** käynnistä se uudelleen komennolla `lemonade run "${LEMONADE_MODEL}"` vaiheessa 1, suorita sitten terveystarkistus uudelleen.
- **`npm install -g` epäonnistuu käyttöoikeusvirheeseen:** määritä Linuxissa tai WSL:ssä käyttäjän omistama globaali npm-hakemisto, lisää se shellin käynnistystiedostoon ja asenna sitten Agent Canvas uudelleen:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Jos käytät `zsh`-kuorta, lisää sama `export PATH=...` -rivi tiedostoon `~/.zshrc` tiedoston `~/.bashrc` sijaan.
- **Agent Canvas hylkää LLM-asetukset `custom_tokenizer`-asetuksen jälkeen:** asenna `transformers` Agent Server -python-ympäristöön, käynnistä Agent Canvas tarvittaessa uudelleen ja yritä tallentaa LLM-asetukset uudelleen. OpenHands tarvitsee Transformersin lataamaan tokenisoijan chat-mallipohjan, kun `custom_tokenizer` on asetettu.
- **Agent Canvas ei saa yhteyttä Lemonadeen:** varmista komennolla `curl -fsS "${LEMONADE_BASE_URL}/health"` ja tarkista, että ensikäytön LLM-lomakkeeseen tai kohtaan **Settings > LLM** syötetty perus-URL vastaa käynnissä olevaa paikallista päätepistettä tai HTTPS-tunnelia.
- **LLM-asetukset eivät tallentuneet:** varmista, että napsautit **Next** arvojen syöttämisen jälkeen. Avaa **Settings > LLM** uudelleen varmistaaksesi, että arvot säilyivät.
- **GitHub MCP ei näe yksityisiä repositorioita:** varmista, että GitHub-tokenilla on lukuoikeus kohderepositorioon ja että MCP:n **Test**-painike kohdassa **Customize** ilmoittaa GitHub-työkaluista.
- **Slack pystyy lukemaan kanavia, mutta ei voi julkaista:** kutsu Slack-sovellus kohdekanavalle ja varmista, että botilla on `chat:write`-oikeus.
- **Automaatio listaa liikaa Slack-kanavia:** käytä Slack-kanavan ID:tä ja aseta `SLACK_CHANNEL_IDS` Slack MCP -palvelimelle kohdassa **Customize**.
- **Automaation ajo epäonnistuu tai ylittää kontekstin:** varmista, että Lemonade käynnistettiin asetuksella `ctx_size=65536`, varmista, että OpenHands LLM:ssä on `custom_tokenizer` asetettuna, ja käytä nimenomaista repositoriota, jossa GitHub-tulosjoukot on rajattu 3–5 kohteeseen. Jos Agent Canvas -versiosi tarjoaa kondensoijan asetukset, aseta kondensoijan enimmäistokenmäärä Lemonade-kontekstikehystä pienemmäksi.

## Seuraavat vaiheet

- Lisää viikoittainen, vain julkaisuihin keskittyvä yhteenveto.
- Lisää GitHub-tapahtumalla laukaistava automaatio nopeampia PR- tai push-hälytyksiä varten.
- Reititä sama yhteenveto Notioniin, Lineariin tai muuhun MCP-pohjaiseen työkaluun.

## Resurssit

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server -dokumentaatio](https://lemonade-server.ai/docs)
- [OpenHands-laajennusten repositorio](https://github.com/OpenHands/extensions)
- [Model Context Protocol -palvelimet](https://github.com/modelcontextprotocol/servers)
- [Slack MCP -paketti](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->