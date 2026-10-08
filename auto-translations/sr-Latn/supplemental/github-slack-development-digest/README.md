<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Pregled

Programeri provode mnogo vremena na male ponavljajuće petlje: pregledanje označenih pull zahteva, odgovaranje na GitHub komentare, triažiranje novih problema (issues), pretvaranje Slack niti u beleške za standup ili praćenje incidenata, i praćenje signala izdanja ili istraživanja.
Svaka petlja je poznata, ali ipak zahteva rasuđivanje: prikupljanje pravog konteksta, odlučivanje šta je bitno i objavljivanje jasnog ažuriranja na mestu gde tim već radi.

[OpenHands automatizacije](https://docs.openhands.dev/openhands/usage/automations/overview) pretvaraju te petlje u zakazane ili događajima pokrenute razgovore agenta: pokretanja u kojima AI softverski agent može da čita kontekst, poziva alate i proizvede ažuriranje.
Deljeni šabloni automatizacije u katalogu ekstenzija OpenHands prate ovaj obrazac za pregled GitHub pull zahteva, praćenje repozitorijuma, triažiranje Linear problema, retrospektive incidenata, Slack standup preglede i istraživačke izveštaje: automatizacija se aktivira, koristi konfigurisane integracije kao što su GitHub ili Slack da dobavi kontekst, rezonuje nad tim kontekstom pomoću velikog jezičkog modela (LLM) i upisuje rezultat nazad.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je lokalna kontrolna ravan za izgradnju i testiranje tih automatizacija.
U ovom vodiču on pokreće OpenHands Agent Server, pozadinski proces koji izvršava razgovore agenta, i povezuje agenta sa spoljnim servisima kao što su GitHub i Slack.

Da bi tok rada ostao na vašem AMD sistemu, agent komunicira sa lokalnim modelom koji opslužuje Lemonade Server.
Lemonade izlaže taj model kroz API kompatibilan sa OpenAI, tako da Agent Canvas može da ga konfiguriše kao udaljenu krajnju tačku u OpenAI stilu, dok model, upit i kontekst toka rada ostaju lokalni.

U ovom vodiču izgradićete jednu konkretnu automatizaciju: zakazani razvojni pregled od GitHub-a ka Slack-u.
Ona koristi GitHub da ispita nedavnu aktivnost repozitorijuma, Slack da objavi pregled, Agent Canvas API pozive da konfiguriše i testira automatizaciju, i Lemonade da lokalno pokreće LLM.

![Dijagram arhitekture koji prikazuje GitHub MCP, OpenHands automatizaciju, Lemonade Server i Slack MCP](assets/00-architecture-overview.png)

## Šta ćete naučiti

- Kako da pokrenete Lemonade Server i proverite da li lokalni model odgovara na chat zahteve
- Kako da pokrenete Agent Canvas i usmerite njegov Agent Server ka lokalnom LLM-u
- Kako da instalirate GitHub i Slack Model Context Protocol (MCP) servere putem Agent Server API-ja
- Kako da kreirate i pokrenete zakazanu OpenHands automatizaciju koja objavljuje razvojni pregled na Slack
- Kako da rešite najčešće greške lokalnog modela i automatizacije

## Osnovni koncepti

| Koncept | Šta predstavlja | Gde se uklapa u ovom vodiču |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma za opsluživanje LLM-a napravljena za AMD hardver koja izlaže API kompatibilan sa OpenAI. Vaši podaci nikada ne napuštaju vaš računar. | Pokreće model koji pokreće agenta. |
| OpenHands Agent Server | Pozadinski proces koji izvršava razgovore OpenHands agenta. | Hostuje agenta, njegov LLM profil i njegove MCP servere. |
| Agent Canvas | Lokalna kontrolna ravan za OpenHands koja pokreće Agent Server i korisnički interfejs za pregled pokretanja agenta. | Pokreće pozadinske sisteme i obezbeđuje API koji pozivate. |
| MCP server | Model Context Protocol server koji agentu pruža alate za spoljni servis kao što je GitHub ili Slack. | Omogućava agentu da čita sa GitHub-a i piše na Slack. |
| OpenHands automatizacija | Zakazani ili događajima pokrenuti razgovor agenta koji dobavlja kontekst, rezonuje nad njim i negde upisuje rezultat. | Pregled od GitHub-a ka Slack-u koji ovde gradite. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Radni tokovi agenta za kodiranje imaju koristi od većeg modela i veće dužine konteksta.
> Koristite najmanje 32 GB sistemske memorije, a za veće GGUF modele poželjno je 64 GB ili više.
<!-- @device:end -->

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->

## Preduslovi

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Potrebno vam je:

- Lemonade Server instaliran prateći standardni [vodič za instalaciju Lemonade-a](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 ili noviji i `npm`, koji se koriste za instaliranje objavljenog Agent Canvas CLI-a i pokretanje MCP servera pomoću `npx`.
- `uv`, Python menadžer paketa koji Agent Canvas koristi za izgradnju okruženja Agent Server-a. Ako već nije instaliran, instalirajte ga iz [vodiča za instalaciju uv-a](https://docs.astral.sh/uv/getting-started/installation/).
- Nedavno objavljen paket `@openhands/agent-canvas` sa podešavanjima agenta zasnovanim na šemi, `LLMSummarizingCondenserSettings.max_tokens`, i podrškom za LLM `custom_tokenizer`.
- Python paket `transformers` dostupan u okruženju Agent Server-a. Potreban je za brojanje tokena šablona chata kada je podešen `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop za Windows](https://docs.docker.com/desktop/setup/install/windows-install/), instaliran i pokrenut. Na Windows-u, Agent Canvas stek se pokreće iz objavljene Docker slike, koja uključuje Node.js, `uv`, `transformers` i paket `@openhands/agent-canvas`, tako da te komponente ne morate instalirati na domaćinu.
<!-- @os:end -->

- GitHub token sa pristupom za čitanje repozitorijuma koji želite da sumirate.
- Slack bot token (`xoxb-...`) sa `chat:write` i pristupom za čitanje kanala.
- ID Slack tima (`T...`).
- ID Slack kanala (`C...`) gde treba objaviti pregled.

Pozovite Slack aplikaciju u ciljni kanal pre testiranja automatizacije.
## Promenljive korišćene u ovom priručniku

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

Ove dve promenljive koriste se u komandama za proveru u nastavku.
Model, tokenizer i druga podešavanja LLM-a unose se direktno u Agent Canvas korisnički interfejs u kasnijim koracima, tako da su njihove doslovne vrednosti prikazane inline tamo gde su vam potrebne.

Sledeće vrednosti se unose u Agent Canvas korisnički interfejs u kasnijim koracima.
Postavite ih ovde kako biste mogli da ih kopirate:

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

Koristite eksplicitnu vrednost `owner/repo` za `GITHUB_REPO_FILTER`.
Široki džoker znakovi za organizacije mogu vratiti previše MCP konteksta za lokalne modele.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Pokretanje Lemonade servera

Pokrenite model preko Lemonade CLI-ja:

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

> **Izaberite model koji odgovara vašem hardveru.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je snažan model za ovaj radni tok, ali zahteva veliki memorijski prostor.
> Ako vaš uređaj ima ograničenu memoriju ili GPU VRAM, odaberite manji GGUF model iz Lemonade biblioteke modela i koristite taj ID modela (i odgovarajući tokenizer) tokom celog priručnika.

> **Napomena:** Prvo pokretanje `lemonade run` preuzima model ako već nije prisutan, što može potrajati u zavisnosti od veličine modela i vaše veze.

Lemonade izlaže OpenAI-kompatibilni API na:

```text
http://127.0.0.1:13305/api/v1
```

Opciono: ako Agent Canvas ili automatizacioni pokretač nisu na istom računaru, objavite Lemonade krajnju tačku kroz bezbedan tunel i koristite HTTPS URL kao osnovni URL za LLM.
[ngrok](https://ngrok.com/) izlaže lokalni port na internet preko bezbednog HTTPS URL-a; zahteva besplatan ngrok nalog, a vi menjate `YOUR_NGROK_DOMAIN.ngrok-free.dev` svojim rezervisanim domenom:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Provera lokalnog modela

Potvrdite da Lemonade može da posluži izabrani model:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Zatim pošaljite mali chat zahtev:

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

Zatim pošaljite mali chat zahtev:

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

Ako ovo vrati niz `choices`, Lemonade je spreman za Agent Canvas.

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

## 3. Pokretanje Agent Canvas

<!-- @os:linux -->
Instalirajte objavljeni Agent Canvas paket i pokrenite ceo stek:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Ako globalna npm instalacija ne uspe zbog greške sa dozvolama, pogledajte stavku o rešavanju problema sa npm dozvolama ispod.

Podrazumevano, Agent Canvas se pokreće na `http://localhost:8000`.
Otvorite taj URL u svom pretraživaču.
Port nije poseban – ako je 8000 već zauzet, prosledite bilo koji slobodan port pomoću `--port` (ili `-p`).
Podrazumevani lokalni bekend bi trebalo da se prikaže kao ispravan na početnom ekranu.

> **Napomena:** Prvo pokretanje izgrađuje `uv`-upravljano Python okruženje Agent Server-a, tako da može potrajati nekoliko minuta pre nego što bekend prijavi da je ispravan.

Komanda `agent-canvas` pokreće agent server, automatizacioni bekend i veb frontend zajedno.
Potrebna vam je samo ova jedna komanda da biste pokrenuli OpenHands lokalno.
Ostatak ovog priručnika konfiguriše sve kroz Agent Canvas korisnički interfejs u vašem pretraživaču.
<!-- @os:end -->

<!-- @os:windows -->
Na Windows-u, pokrenite objavljenu sliku Agent Canvas kontejnera pomoću Docker Desktop-a.
Slika objedinjuje Agent Server, automatizacioni bekend i veb frontend, tako da ne morate da instalirate Node.js, `uv` ili CLI na host sistemu.

Prvo, kreirajte fascikle za konfiguraciju i radni prostor koje kontejner montira:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Preuzmite objavljenu sliku (oko 6 GB; javna je, tako da prijava nije potrebna):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Zatim pokrenite stek:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Otvorite `http://localhost:8000/canvas` u svom pretraživaču.
Ako je port 8000 već zauzet, mapirajte drugi host port, na primer `-p 8080:8000`, i umesto toga otvorite `http://localhost:8080/canvas`.

> **Napomena:** Prvo pokretanje izgrađuje okruženje Agent Server-a unutar kontejnera, tako da može potrajati nekoliko minuta pre nego što bekend prijavi da je ispravan.

Montiranje `.openhands` čuva vaš LLM profil, MCP servere i automatizacije prilikom ponovnog pokretanja kontejnera.
Ostatak ovog priručnika konfiguriše sve kroz Agent Canvas korisnički interfejs u vašem pretraživaču na `http://localhost:8000/canvas`.
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
## 4. Konfigurisanje lokalnog LLM-a u korisničkom interfejsu

Pri prvom pokretanju, Agent Canvas otvara tok za uvodno podešavanje (onboarding).
U tom toku:

1. Zadržite **OpenHands** kao izabranog agenta i kliknite na **Next**.
2. Na **Set up your LLM**, izaberite **Advanced**.
3. Zadržite **Authentication** podešeno na **API key**.
4. Podesite **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Podesite **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Za **API Key**, unesite bilo koji vrednosni placeholder koji nije prazan, na primer `lemonade-local`. Lemonade ne zahteva pravi ključ, ali OpenHands klijentu je potrebna vrednost koju će poslati.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server se izvršava unutar kontejnera, pa podesite **Base URL** na `http://host.docker.internal:13305/api/v1` umesto `http://127.0.0.1:13305/api/v1`.
> Iznutra kontejnera, `127.0.0.1` predstavlja sam kontejner; `host.docker.internal` dopire do Lemonade koji se izvršava na Windows host mašini, a Docker Desktop automatski obezbeđuje to ime hosta.
<!-- @os:end -->

Polja za konekciju bi trebalo da izgledaju ovako.
Polje za API ključ je maskirano u korisničkom interfejsu.

![Agent Canvas napredna LLM podešavanja pri prvoj upotrebi sa Lemonade modelom i lokalnim baznim URL-om](assets/01-llm-advanced-settings.png)

Zatim izaberite **All** i podesite dodatna polja za lokalni model:

1. Skrolujte do **Custom Tokenizer** i podesite ga na `Qwen/Qwen3.6-35B-A3B`.
2. Skrolujte do **LiteLLM Extra Body** i podesite ga na `{"enable_thinking": true}`.
3. Kliknite na **Next**.

![Agent Canvas kartica All pri prvoj upotrebi LLM-a sa Qwen custom tokenizerom](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas kartica All pri prvoj upotrebi LLM-a sa konfigurisanim LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

LLM podešavanja bi trebalo da prikazuju:

| Polje | Vrednost |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Prefiks `openai/` govori LiteLLM-u da koristi OpenAI-kompatibilno formatiranje zahteva prema Lemonade endpoint-u.
Custom tokenizer je originalni Hugging Face tokenizer za GGUF model; on omogućava OpenHands-u da broji iste tokene chat-šablona koje vidi lokalni model server.
Trenutni formular za prvu upotrebu LLM-a ne prikazuje podešavanja kondenzatora.
Ako vaša verzija Agent Canvas-a kasnije izloži podešavanja kondenzatora pod **Settings > LLM**, koristite `llm_summarizing` i podesite maksimalan broj tokena ispod Lemonade kontekstnog prozora, na primer `56000`.

## 5. Instaliranje GitHub i Slack MCP servera

U Agent Canvas korisničkom interfejsu, otvorite **Customize** (ili **Settings > MCP**) da dodate MCP servere koji agentu daju alate za GitHub i Slack.
Vrednosti tokena se šalju samo vašem lokalnom Agent Server-u i čuvaju se kao šifrovana podešavanja.

<!-- @os:windows -->
> **Windows (Docker):** komande MCP servera `npx` navedene ispod se izvršavaju unutar kontejnera, koji već uključuje Node.js, tako da se na host mašini ne instalira ništa dodatno.
> Pošto je `.openhands` montiran, MCP serveri i njihovi tokeni se čuvaju i nakon ponovnog pokretanja kontejnera.
<!-- @os:end -->

### GitHub MCP server

Dodajte novi MCP server sa ovim podešavanjima:

| Polje | Vrednost |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = vaš GitHub token |

Koristite GitHub token sa pravima čitanja za repozitorijum koji želite da sumirate.

### Slack MCP server

Dodajte drugi MCP server sa ovim podešavanjima:

| Polje | Vrednost |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID vašeg digest kanala |

Podesite `SLACK_CHANNEL_IDS` na ID digest kanala (istu vrednost kao `SLACK_DIGEST_CHANNEL`) tako da agent ne mora da pretražuje svaki Slack kanal.

Nakon dodavanja oba servera, koristite dugme **Test** na svakom od njih da potvrdite da se povezuje i oglašava alate.
GitHub server bi trebalo da prikaže listu GitHub alata, a Slack server listu Slack alata.

![Agent Canvas MCP stranica sa instaliranim GitHub i Slack serverima](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Kreiranje automatizacije za digest

U Agent Canvas korisničkom interfejsu, otvorite stranicu **Automations** i kreirajte novu automatizaciju:

1. Izaberite **Create automation** i izaberite tip **Prompt preset**.
2. Podesite **Name** na `GitHub Development Digest to Slack`.
3. Podesite **Prompt** na sledeći tekst, zamenjujući placeholdere za repozitorijum i kanal vašim vrednostima:

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

4. Podesite **Trigger** na **Cron** sa rasporedom `0 9 * * 1-5` (9 ujutru radnim danima) i podesite **Timezone** na vašu vremensku zonu, na primer `America/New_York`.
5. Podesite **Timeout** na `900` sekundi.
6. Sačuvajte automatizaciju.

Stranica sa detaljima automatizacije prikazuje novu automatizaciju sa njenim cron okidačem i generisanom ulaznom tačkom prompt-preseta.

![Agent Canvas stranica sa detaljima automatizacije nakon kreiranja](assets/05-automation-created.png)
## 7. Testiranje automatizacije

Sa stranice sa detaljima automatizacije u Agent Canvas UI-ju:

1. Kliknite **Run now** (ili **Dispatch**) da odmah pokrenete automatizaciju jednom.
2. Pratite listu pokretanja na istoj stranici. Najnovije pokretanje treba da pređe u status `COMPLETED`.
3. Otvorite vaš ciljni Slack kanal. Trebalo bi da sadrži generisani digest.

Ne morate da čekate da se aktivira cron raspored—**Run now** pokreće izvršavanje na zahtev, tako da možete da potvrdite da prompt, MCP konekcije i objavljivanje na Slack-u rade pre nego što se oslonite na raspored.

![Agent Canvas automatizacija je uspešno završena](assets/06-automation-run-completed.png)

![Slack kanal koji prikazuje generisani OpenHands digest](assets/07-slackbot-message.png)

## Rešavanje problema

<!-- @os:windows -->
- **Docker port 8000 je već u upotrebi:** mapirajte drugačiji host port, na primer `docker run ... -p 8080:8000 ...`, i otvorite `http://localhost:8080/canvas`.
- **`docker pull` ne uspeva sa greškom u vezi sa kredencijalima** (na primer, "A specified logon session does not exist"): pokrenite pull iz interaktivne Windows sesije, ili unapred preuzmite sliku. Slika je javna, pa `docker login` nije potreban.
- **UI se učitava, ali backend nije ispravan:** prvo pokretanje gradi okruženje Agent Server-a unutar kontejnera. Sačekajte minut i osvežite stranicu, zatim proverite `docker logs <container>` za napredak.
- **Agent Canvas ne može da dosegne Lemonade iz kontejnera:** podesite LLM **Base URL** na `http://host.docker.internal:13305/api/v1` (ne `127.0.0.1`), i potvrdite da Lemonade radi na Windows host-u.
<!-- @os:end -->

- **Lemonade je ugašen:** ponovo ga pokrenite komandom `lemonade run "${LEMONADE_MODEL}"` iz koraka 1, a zatim ponovo pokrenite proveru ispravnosti.
- **`npm install -g` ne uspeva sa greškom u vezi sa dozvolama:** na Linux-u ili WSL-u, konfigurišite globalni npm direktorijum u vlasništvu korisnika, dodajte ga u vašu startup datoteku ljuske, a zatim ponovo instalirajte Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Ako koristite `zsh`, dodajte istu liniju `export PATH=...` u `~/.zshrc` umesto u `~/.bashrc`.
- **Agent Canvas odbija LLM podešavanja nakon postavljanja `custom_tokenizer`:** instalirajte `transformers` u Python okruženju Agent Server-a, ponovo pokrenite Agent Canvas ako je potrebno, i pokušajte ponovo da sačuvate LLM podešavanja. OpenHands zahteva Transformers za učitavanje chat template-a tokenizera kada je postavljen `custom_tokenizer`.
- **Agent Canvas ne može da dosegne Lemonade:** proverite `curl -fsS "${LEMONADE_BASE_URL}/health"` i potvrdite da se base URL unet u LLM formu prilikom prve upotrebe ili u **Settings > LLM** poklapa sa pokrenutim lokalnim endpoint-om ili HTTPS tunelom.
- **LLM podešavanja nisu sačuvana:** proverite da ste kliknuli na **Next** nakon unosa vrednosti. Ponovo otvorite **Settings > LLM** da potvrdite da su vrednosti sačuvane.
- **GitHub MCP ne vidi privatne repozitorijume:** potvrdite da GitHub token ima pristup za čitanje ciljnog repozitorijuma i da dugme **Test** za MCP u **Customize** prikazuje GitHub alate.
- **Slack može da čita kanale, ali ne može da objavljuje:** pozovite Slack aplikaciju u ciljni kanal i potvrdite da bot ima `chat:write`.
- **Automatizacija prikazuje previše Slack kanala:** koristite ID Slack kanala i postavite `SLACK_CHANNEL_IDS` na Slack MCP serveru u **Customize**.
- **Izvršavanje automatizacije ne uspeva ili prevazilazi kontekst:** potvrdite da je Lemonade pokrenut sa `ctx_size=65536`, potvrdite da OpenHands LLM ima postavljen `custom_tokenizer`, i koristite eksplicitni repozitorijum sa GitHub rezultatima ograničenim na 3 do 5 stavki. Ako vaša verzija Agent Canvas-a izlaže podešavanja kondenzatora, postavite maksimalan broj tokena kondenzatora ispod Lemonade kontekstnog prozora.

## Sledeći koraci

- Dodajte nedeljni digest samo za izdanja (release).
- Dodajte automatizaciju pokrenutu GitHub događajima za brže obaveštenja o PR-ovima ili push-evima.
- Usmerite isti digest u Notion, Linear, ili drugi alat podržan putem MCP-a.

## Resursi

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Dokumentacija za Lemonade Server](https://lemonade-server.ai/docs)
- [Repozitorijum ekstenzija za OpenHands](https://github.com/OpenHands/extensions)
- [Model Context Protocol serveri](https://github.com/modelcontextprotocol/servers)
- [Slack MCP paket](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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