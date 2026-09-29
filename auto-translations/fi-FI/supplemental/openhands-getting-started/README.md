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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Yleiskatsaus

[OpenHands](https://github.com/All-Hands-AI/OpenHands) on tekoälypohjainen ohjelmistoagentti, joka osaa kirjoittaa koodia, suorittaa komentoja, selata verkkoa ja muokata tiedostoja oikeassa työtilassa. Sen sijaan, että kopioisit ehdotuksia chat-ikkunasta, ohjaat agentin projektikansioon ja annat sen tehdä työn: toteuttaa ominaisuuden, korjata virheen, kirjoittaa testejä tai selittää koodikannan toimintaa.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) on suositeltu selainkäyttöliittymä OpenHandsin ajamiseen. Yksittäinen `agent-canvas`-komento käynnistää agenttipalvelimen, automaatiotaustajärjestelmän ja web-käyttöliittymän yhdessä, joten voit käydä keskustelua agentin kanssa selaimessasi.

Jotta kaikki pysyy AMD-järjestelmässäsi, agentti keskustelee Lemonade Serverin tarjoaman paikallisen mallin kanssa. Lemonade tarjoaa kyseisen mallin OpenAI-yhteensopivan API:n kautta, joten Agent Canvas voi määrittää sen kuten minkä tahansa muun OpenAI-tyylisen päätepisteen, samalla kun malli, koodisi ja keskustelun konteksti pysyvät koneellasi.

Tässä ohjekirjassa käynnistät paikallisen mallin, käynnistät Agent Canvasin, osoitat sen kyseiseen malliin ja suoritat ensimmäisen koodaustehtäväsi oikeaa projektikansiota vasten.

## Mitä opit

- Kuinka käynnistää Lemonade Server ja varmistaa, että paikallinen malli vastaa chat-pyyntöihin
- Kuinka asentaa ja käynnistää Agent Canvas npm-paketista
- Kuinka määrittää Agent Canvas käyttämään paikallista Lemonade-mallia LLM:nä
- Kuinka aloittaa OpenHands-keskustelu ja seurata, kuinka agentti muokkaa tiedostoja ja suorittaa komentoja työtilassa
- Kuinka tarkistaa, mitä agentti muutti, ja ohjata sitä jatkoviesteillä

## Keskeiset käsitteet

| Käsite | Mikä se on | Missä kohtaa se liittyy tähän ohjekirjaan |
| --- | --- | --- |
| Lemonade Server | Paikallinen LLM-palvelualusta, joka on rakennettu AMD-laitteistolle ja tarjoaa OpenAI-yhteensopivan API:n. Datasi ei koskaan poistu koneeltasi. | Ajaa mallia, joka toimii agentin voimanlähteenä. |
| OpenHands | Tekoälypohjainen ohjelmistoagentti, joka lukee ja muokkaa tiedostoja, suorittaa shell-komentoja ja selaa verkkoa työtilan sisällä. | Agentti, jota ohjaat chatista. |
| Agent Canvas | Selainkäyttöliittymä ja taustajärjestelmä, joka ajaa OpenHands-keskusteluja ja näyttää työkalukutsut sekä tiedostomuutokset. | Käynnistää pinon ja isännöi keskusteluasi. |
| Työtila | Projektikansio, jota agentin sallitaan lukea ja muokata. | Agentin muokkausten ja komentojen kohde. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Koodausagentin työnkulut hyötyvät suuremmasta mallista ja kontekstiikkunasta. Käytä vähintään 32 Gt järjestelmämuistia ja suosi 64 Gt tai enemmän suuremmille GGUF-malleille.
<!-- @device:end -->

## Muistiasetuksen tekeminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Vaatimukset


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Tarvitset:

- Lemonade Serverin, joka on asennettu ja pystyy tarjoamaan alla olevan mallin.

<!-- @os:linux -->
- Node.js 22.12 tai uudemman ja `npm`-työkalun (jota `agent-canvas`-CLI käyttää).
- `uv`:n, Python-pakettienhallintaohjelman, jota Agent Canvas käyttää agenttipalvelimen ympäristön hallintaan. Jos järjestelmässäsi ei vielä ole sitä, asenna se [uv:n asennusoppaasta](https://docs.astral.sh/uv/getting-started/installation/) ennen Agent Canvasin käynnistämistä.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) asennettuna ja käynnissä. Windowsissa Agent Canvas -pino ajetaan julkaistusta Docker-levykuvasta, joka sisältää Node.js:n, `uv`:n ja `@openhands/agent-canvas`-paketin, joten sinun ei tarvitse asentaa niitä isäntäkoneelle.
<!-- @os:end -->

- Projektikansion, jossa työskennellä. Tämä voi olla mikä tahansa paikallinen git-tietovarasto tai koodihakemisto, jonka parissa haluat agentin työskentelevän.

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. Käynnistä Lemonade Server

Käynnistä malli Lemonade-CLI:stä:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Valitse laitteistoosi sopiva malli.** `Qwen3.6-35B-A3B-GGUF` (~20 Gt) on vahva koodausmalli, mutta se tarvitsee suuren muistivarannon. Jos laitteessasi on rajallisesti muistia tai GPU-VRAM:ia, valitse sen sijaan pienempi GGUF-malli Lemonade-mallikirjastosta ja käytä kyseistä malli-ID:tä läpi tämän ohjekirjan.

> **Huomautus:** Ensimmäinen `lemonade run` lataa mallin, jos se ei ole vielä valmiiksi läsnä, mikä voi kestää jonkin aikaa mallin koosta ja yhteydestäsi riippuen.

Lemonade tarjoaa OpenAI-yhteensopivan API:n osoitteessa:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Vahvista paikallinen malli

Vahvista, että Lemonade pystyy tarjoamaan valitun mallin:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Lähetä sitten pieni chat-pyyntö:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Jos tämä palauttaa `choices`-taulukon, Lemonade on valmis Agent Canvasille.

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
model_id = "${lemonade_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
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

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->
## 3. Asenna ja käynnistä Agent Canvas

<!-- @os:linux -->
Asenna julkaistu Agent Canvas -paketti globaalisti:

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

Käynnistä sitten koko pino päätteestä:

```bash
agent-canvas
```

Oletuksena Agent Canvas käynnistyy osoitteessa `http://localhost:8000`. Avaa
tämä URL-osoite selaimessasi. Portti ei ole erityinen — jos 8000 on jo
käytössä, anna vapaa portti valitsimella `--port` (tai `-p`) kun käynnistät
Agent Canvasin:

```bash
agent-canvas --port 3000
```

Avaa sitten sen sijaan `http://localhost:3000`. Oletusarvoisen paikallisen
taustajärjestelmän tulisi näkyä toimivana kotinäytöllä.

`agent-canvas`-komento käynnistää agenttipalvelimen, automaatiobackendin ja
verkkokäyttöliittymän yhdessä. Tarvitset vain tämän yhden komennon OpenHandsin
käyttämiseen paikallisesti.

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
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
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Windowsissa suorita julkaistu Agent Canvas -säilökuva Docker Desktopilla.
Kuva sisältää Agent Serverin, automaatiobackendin ja verkkokäyttöliittymän,
joten sinun ei tarvitse asentaa isäntäkoneelle Node.js:ää, `uv`:ta tai CLI:tä.

Luo ensin kansiot asetuksille ja työtilalle, jotka säilö liittää:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Hae julkaistu kuva (se on julkinen, joten kirjautumista ei tarvita):

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

Avaa selaimessasi `http://localhost:8000/canvas`. Jos portti 8000 on jo
käytössä, kohdista eri isäntäportti, esimerkiksi `-p 8080:8000`, ja avaa
sen sijaan `http://localhost:8080/canvas`.

> **Huomio:** Ensimmäinen käynnistys alustaa Agent Serverin säilön sisällä,
> joten voi kestää minuutin tai pari ennen kuin taustajärjestelmä raportoi
> olevansa toimintakunnossa.

`.openhands`-liitos säilyttää LLM-profiilisi ja asetuksesi säilön
uudelleenkäynnistysten yli. Tämän oppaan loppuosa määrittää kaiken Agent
Canvasin käyttöliittymän kautta selaimessasi.

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
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

## 4. Määritä paikallinen LLM

Ensimmäisellä käynnistyskerralla Agent Canvas avaa käyttöönottoprosessin.
Tässä prosessissa:

1. Pidä **OpenHands** valittuna agenttina ja napsauta **Next**.
2. Kohdassa **Set up your LLM**, valitse **Advanced**.
3. Pidä **Authentication**-asetuksena **API key**.
4. Aseta **Custom Model**-kentäksi `openai/Qwen3.6-35B-A3B-GGUF`.
5. Aseta **Base URL**-kentäksi `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Windowsissa pino käy säilössä, joka ei pysty tavoittamaan isäntäkonetta
   > osoitteessa `127.0.0.1`. Käytä sen sijaan osoitetta
   > `http://host.docker.internal:13305/api/v1`, jotta säilöytetty agentti voi
   > tavoittaa Windows-isäntäkoneella toimivan Lemonaden.
   <!-- @os:end -->
6. Anna **API Key**-kenttään mikä tahansa tyhjä paikkamerkki, kuten
   `lemonade-local`. Lemonade ei vaadi oikeaa avainta, mutta OpenHands-asiakas
   tarvitsee lähetettäväksi jonkin arvon.
7. Napsauta **Next**.

Valmiiden Advanced-asetusten pitäisi näyttää tältä. Käyttöliittymä peittää
API-avainkentän.

![Agent Canvasin ensikäytön LLM Advanced -asetukset Lemonade-mallilla ja paikallisella base URL:lla](assets/01-llm-advanced-settings.png)

Agent Canvas tallentaa nämä arvot LLM-profiiliksi. Jos versiosi pyytää sinua
nimeämään kyseisen profiilin, käytä nimeä, jossa ei ole välilyöntejä, kuten
`lemonade-local`. Jos vaihdat mallia myöhemmin, avaa **Settings > LLM** ja
päivitä samat Advanced-kentät. Voit vaihtaa tallennettuja profiileja
keskustelun syöttökentästä `/model`-komennolla.

## 5. Avaa työtila

Agentti voi lukea ja muokata tiedostoja vain valitsemasi työtilan sisällä.
Ennen tehtävän aloittamista osoita Agent Canvas projektikansioosi:

1. Valitse kotinäytöltä **Open Workspace**.
2. Valitse kansio, joka sisältää projektisi (esimerkiksi git-repositorio, jonka
   parissa haluat agentin työskentelevän).
3. Aloita uusi keskustelu kyseisessä työtilassa.

Kaikki mitä agentti tekee — tiedostojen lukeminen, komentojen suorittaminen,
koodin muokkaaminen — rajautuu kyseiseen työtilaan.

![Agent Canvas -kotinäkymä käyttöönoton jälkeen](assets/02-agent-canvas-home.png)

## 6. Suorita ensimmäinen koodaustehtäväsi

Kun työtila on avoinna ja paikallinen LLM valittuna, kirjoita konkreettinen
tehtävä keskusteluun. Hyvä ensimmäinen tehtävä on pieni ja todennettavissa,
esimerkiksi:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Seuraa keskustelun aikajanaa. OpenHands tekee seuraavaa:

- Lukee työtilan ymmärtääkseen sen rakenteen.
- Luo tiedoston `hello.py` pyydetyllä funktiolla ja testilohkolla.
- Suorittaa tarvittaessa komennon `python3 hello.py` tulosteen tarkistamiseksi.
- Raportoi tekemänsä toimet ja mahdollisen komentotulosteen keskustelussa.

Sinun pitäisi nähdä uuden tiedoston ilmestyvän työtilaan, ja agentin
lopullisen viestin tulisi kuvata tekemänsä muutos. Tämä on ratkaiseva hetki:
agentti kirjoitti ja suoritti oikeaa koodia projektikansiossasi.

## 7. Tarkasta ja ohjaa agenttia

Kun agentti on suorittanut vaiheen, tarkasta sen työ ennen seuraavan
hyväksymistä:

- **Tiedostomuutokset**: käytä työtilan tiedostoselainta tai agentin
  diff-näkymää nähdäksesi tarkalleen, mitä lisättiin, muutettiin tai
  poistettiin.
- **Komentotuloste**: laajenna mikä tahansa agentin suorittama komento
  nähdäksesi stdoutin, stderrin ja poistumiskoodin.
- **Jatkotoimet**: jos tulos ei ole toivomasi, vastaa samassa keskustelussa
  korjauksella. Agentti säilyttää aiemman kontekstin ja jatkaa iterointia
  samoilla tiedostoilla.

Jos esimerkiksi testi ei tulostanut odotettua tervehdystä, vastaa:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agentti lukee tiedoston uudelleen, suorittaa komennon, selvittää ongelman ja
muokkaa tiedostoa uudelleen — kaikki saman keskustelun sisällä.
## Vianmääritys

<!-- @os:linux -->
- **`agent-canvas` ei ole PATH-muuttujassa:** asenna uudelleen komennolla
  `npm install -g @openhands/agent-canvas` ja varmista, että npm:n
  globaali binäärihakemisto on PATH-muuttujassa ennen kuin `agent-canvas`
  voidaan käynnistää uudesta päätteestä.
- **`npm install -g` epäonnistuu käyttöoikeusvirheeseen:** määritä
  käyttäjän omistama globaali npm-hakemisto, avaa sitten pääte uudelleen ja
  asenna Agent Canvas uudelleen.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` puuttuu:** asenna se
  [uv:n asennusoppaasta](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas käyttää `uv`-työkalua agenttipalvelimen Python-ympäristön hallintaan.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` tai `docker run` ei muodosta yhteyttä:** varmista, että
  Docker Desktop on käynnissä (sen valaskuvake näkyy ilmaisinalueella) ja että
  moottori on käynnistynyt loppuun. `docker version`-komennon pitäisi tulostaa
  sekä Client- että Server-osio.
- **Kontti käynnistyy, mutta taustajärjestelmä ei koskaan siirry
  toimintakuntoiseksi:** ensimmäinen käynnistys alustaa Agent Serverin kontin
  sisällä; anna sille minuutti tai kaksi aikaa ja tarkista sen jälkeen
  `docker logs <container>` virheiden varalta.
- **Kontti ei saa yhteyttä Lemonadeen:** kontti tavoittaa isäntäkoneen
  osoitteella `host.docker.internal`. Varmista, että Lemonade palvelee
  Windows-isäntäkoneella komennolla `lemonade status`, ja käytä
  LLM:ää määrittäessäsi perus-URL-osoitteena
  `http://host.docker.internal:13305/api/v1`.
<!-- @os:end -->

- **Käyttöliittymä latautuu, mutta taustajärjestelmä näyttää
  epäterveenä:** odota minuutti tai kaksi, että agenttipalvelin käynnistyy
  loppuun, ja päivitä sitten sivu. Jos tila pysyy epäterveenä, käynnistä
  pino uudelleen ja tarkista lokit virheiden varalta.
- **Lemonade-keskustelupyynnöt epäonnistuvat yhteysvirheeseen:** varmista,
  että `curl -fsS "http://127.0.0.1:13305/api/v1/health"` onnistuu ja että
  Lemonade edelleen palvelee mallia komennolla `lemonade status`.
- **Agentti antaa virheen kontekstin pituudesta tai token-rajasta:** aloita
  uusi keskustelu, jotta agentille ei kerry liian suurta historiaa. Jos
  ongelma jatkuu, käynnistä Lemonade uudelleen suuremmalla `ctx_size`-arvolla
  kuin oletus 65536 (esimerkiksi `ctx_size=131072`), muistin salliessa.
- **Agentti tuottaa heikkolaatuisia tai keskeneräisiä muokkauksia:** vaihda
  Lemonadessa suurempaan malliin tai anna agentille pienempi, konkreettisempi
  tehtävä ja anna sen valmistua ennen kuin pyydät seuraavaa muutosta.

## Seuraavat vaiheet

- Kokeile suurempaa tehtävää samassa työtilassa, kuten yksikkötestitiedoston
  lisäämistä tai tunnetun virheen korjaamista, ja tarkista agentin
  muutosehdotus ennen sen hyväksymistä.
- Yhdistä MCP-palvelin, kuten GitHub tai Slack, kohdassa **Customize**, jotta
  agentti voi lukea ongelmia tai julkaista päivityksiä työn aikana.
- Tallenna useita LLM-profiileja (nopea pieni malli ja tehokkaampi suuri
  malli) ja vaihda niiden välillä komennolla `/model` kesken keskustelun.
- Siirry käyttämään [OpenHands-automaatioita](https://docs.openhands.dev/openhands/usage/automations/overview)
  muuttaaksesi toistuvat kehityssilmukat ajastetuiksi tai
  tapahtumapohjaisiksi agenttiajoiksi.

## Resurssit

- [OpenHands-dokumentaatio](https://docs.openhands.dev/)
- [Agent Canvas -yleiskatsaus](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvasin käyttöönotto](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-profiilit ja mallin määritys](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server -dokumentaatio](https://lemonade-server.ai/docs)

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