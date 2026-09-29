<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->
## Pregled

Razvijalci porabijo veliko časa za majhne ponavljajoče se zanke: pregledovanje označenih pull requestov, odgovarjanje na komentarje na GitHub, obravnavanje novih napak (issues), pretvarjanje Slack niti v zapiske za dnevne sestanke ali spremljanje incidentov ter sledenje signalom o izdajah ali raziskavah.
Vsaka zanka je znana, vendar še vedno zahteva presojo: zbrati pravi kontekst, odločiti, kaj je pomembno, in objaviti jasno posodobitev tam, kjer ekipa že dela.

[OpenHands avtomatizacije](https://docs.openhands.dev/openhands/usage/automations/overview) spremenijo te zanke v načrtovane ali z dogodki sprožene pogovore agentov: izvajanja, v katerih lahko programski agent z umetno inteligenco prebere kontekst, kliče orodja in ustvari posodobitev.
Skupne predloge za avtomatizacijo v katalogu razširitev OpenHands sledijo temu vzorcu za pregled pull requestov na GitHub, spremljanje repozitorijev, obravnavanje napak v Linear, retrospektive incidentov, dnevne povzetke prek Slack in raziskovalne povzetke: avtomatizacija se aktivira, uporabi konfigurirane integracije, kot sta GitHub ali Slack, za pridobitev konteksta, razmišlja o tem kontekstu z velikim jezikovnim modelom (LLM) in nazaj zapiše rezultat.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je lokalna nadzorna ploskev za gradnjo in testiranje teh avtomatizacij.
V tem vodniku poganja OpenHands Agent Server, zaledni proces, ki izvaja pogovore agentov, in povezuje agenta z zunanjimi storitvami, kot sta GitHub in Slack.

Da bi delovni tok ostal na vašem sistemu AMD, se agent pogovarja z lokalnim modelom, ki ga strežе Lemonade Server.
Lemonade izpostavi ta model prek vmesnika API, združljivega z OpenAI, tako da ga Agent Canvas lahko konfigurira kot oddaljeno končno točko v slogu OpenAI, medtem ko model, poziv in kontekst delovnega toka ostanejo lokalni.

V tem vodniku boste zgradili eno konkretno avtomatizacijo: načrtovan razvojni povzetek od GitHub do Slack.
Ta uporablja GitHub za pregled nedavne dejavnosti repozitorija, Slack za objavo povzetka, klice API Agent Canvas za konfiguracijo in testiranje avtomatizacije ter Lemonade za lokalno izvajanje LLM.

![Diagram arhitekture, ki prikazuje GitHub MCP, OpenHands avtomatizacijo, Lemonade Server in Slack MCP](assets/00-architecture-overview.png)

## Kaj se boste naučili

- Kako zagnati Lemonade Server in preveriti, ali lokalni model odgovarja na klepetalne zahteve
- Kako zagnati Agent Canvas in usmeriti njegov Agent Server na lokalni LLM
- Kako namestiti strežnike GitHub in Slack Model Context Protocol (MCP) prek vmesnika API Agent Server
- Kako ustvariti in sprožiti načrtovano OpenHands avtomatizacijo, ki objavi razvojni povzetek na Slack
- Kako odpraviti najpogostejše napake pri lokalnem modelu in avtomatizaciji

## Osnovni koncepti

| Koncept | Kaj je | Kje se uklapa v ta vodnik |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma za strežbo LLM, zgrajena za strojno opremo AMD, ki izpostavi vmesnik API, združljiv z OpenAI. Vaši podatki nikoli ne zapustijo vaše naprave. | Poganja model, ki napaja agenta. |
| OpenHands Agent Server | Zaledni proces, ki izvaja pogovore agentov OpenHands. | Gosti agenta, njegov profil LLM in njegove strežnike MCP. |
| Agent Canvas | Lokalna nadzorna ploskev za OpenHands, ki poganja Agent Server in uporabniški vmesnik za pregledovanje izvajanj agenta. | Zažene zaledne procese in zagotavlja vmesnik API, ki ga kličete. |
| Strežnik MCP | Strežnik Model Context Protocol, ki agentu zagotavlja orodja za zunanjo storitev, kot sta GitHub ali Slack. | Agentu omogoča branje GitHub in pisanje v Slack. |
| Avtomatizacija OpenHands | Načrtovan ali z dogodki sprožen pogovor agenta, ki pridobi kontekst, razmišlja o njem in nekje zapiše rezultat. | Povzetek od GitHub do Slack, ki ga zgradite tukaj. |
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Delovni tokovi kodirnih agentov imajo koristi od večjega modela in večjega kontekstnega okna.
> Uporabite vsaj 32 GB sistemskega pomnilnika, za večje modele GGUF pa je priporočljivih 64 GB ali več.
<!-- @device:end -->
## Nastavitev konfiguracije pomnilnika
<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje razpoložljivosti posodobitev programske opreme
<!-- @require:software-update -->
<!-- @device:end -->
## Predpogoji
<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->
- Nameščen strežnik Lemonade Server, po standardnem [vodniku za namestitev Lemonade](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:linux -->
- Node.js 22.12 ali novejši ter `npm`, uporabljena za namestitev objavljenega Agent Canvas CLI in zagon MCP strežnikov z `npx`.
- `uv`, upravitelj paketov Python, ki ga Agent Canvas uporablja za izgradnjo okolja Agent Server. Če še ni nameščen, ga namestite s pomočjo [navodil za namestitev uv](https://docs.astral.sh/uv/getting-started/installation/).
- Nedaven objavljen paket `@openhands/agent-canvas` s shemsko vodenimi nastavitvami agenta, `LLMSummarizingCondenserSettings.max_tokens` in podporo za LLM `custom_tokenizer`.
- Paket Python `transformers`, ki mora biti na voljo v okolju Agent Server. Potreben je za štetje žetonov predloge pogovora, ko je nastavljen `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), nameščen in zagnan. V sistemu Windows sklad Agent Canvas teče iz objavljene slike Docker, ki vključuje Node.js, `uv`, `transformers` in paket `@openhands/agent-canvas`, zato tega ni treba nameščati na gostitelja.
<!-- @os:end -->
- Žeton GitHub z dostopom za branje do repozitorija, ki ga želite povzeti.
- Žeton bota Slack (`xoxb-...`) z dostopom `chat:write` in dostopom za branje kanalov.
- ID ekipe Slack (`T...`).
- ID kanala Slack (`C...`), kamor naj bo objavljen povzetek.

Pred testiranjem avtomatizacije povabite aplikacijo Slack v ciljni kanal.
## Uporabljene spremenljivke v tem priročniku

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

Ti dve spremenljivki se uporabljata v spodnjih ukazih za preverjanje.
Model, tokenizator in druge nastavitve LLM se v naslednjih korakih vnesejo neposredno v uporabniškem vmesniku Agent Canvas, zato so njihove dobesedne vrednosti prikazane v besedilu, kjer jih potrebujete.

Naslednje vrednosti se v naslednjih korakih vnesejo v uporabniški vmesnik Agent Canvas.
Nastavite jih tukaj, da jih boste lahko preprosto kopirali:

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

Za `GITHUB_REPO_FILTER` uporabite eksplicitno vrednost `owner/repo`.
Široki nadomestni znaki za organizacije lahko vrnejo preveč konteksta MCP za lokalne modele.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Zagon strežnika Lemonade

Zaženite model iz ukazne vrstice Lemonade:

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

> **Izberite model, ki ustreza vaši strojni opremi.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je zmogljiv model za ta potek dela, vendar potrebuje velik pomnilniški bazen.
> Če ima vaša naprava omejen pomnilnik ali GPU VRAM, izberite manjši model GGUF iz knjižnice modelov Lemonade in v celotnem priročniku uporabite ta ID modela (in njegov ustrezni tokenizator).

> **Opomba:** Prvi zagon `lemonade run` prenese model, če ta še ni prisoten, kar lahko traja nekaj časa, odvisno od velikosti modela in vaše povezave.

Lemonade izpostavi API, združljiv z OpenAI, na:

```text
http://127.0.0.1:13305/api/v1
```

Neobvezno: če Agent Canvas ali zaganjalnik avtomatizacije ni v istem računalniku, izpostavite končno točko Lemonade prek varnega tunela in kot osnovni URL naslov LLM uporabite URL naslov HTTPS.
[ngrok](https://ngrok.com/) izpostavi lokalna vrata internetu prek varnega URL naslova HTTPS; zahteva brezplačen račun ngrok, pri čemer `YOUR_NGROK_DOMAIN.ngrok-free.dev` zamenjate s svojo rezervirano domeno:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Preverjanje lokalnega modela

Potrdite, da lahko Lemonade streže izbrani model:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Nato pošljite majhno klepetalno zahtevo:

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

Nato pošljite majhno klepetalno zahtevo:

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

Če to vrne polje `choices`, je Lemonade pripravljen za Agent Canvas.

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

## 3. Zagon Agent Canvas

<!-- @os:linux -->
Namestite objavljeni paket Agent Canvas in zaženite celoten nabor storitev:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Če namestitev prek globalnega npm ne uspe zaradi napake z dovoljenji, glejte spodnji vnos za odpravljanje težav z dovoljenji npm.

Privzeto se Agent Canvas zažene na `http://localhost:8000`.
Odprite ta URL naslov v brskalniku.
Vrata niso posebna – če so vrata 8000 že v uporabi, podajte katera koli prosta vrata z `--port` (ali `-p`).
Privzeti lokalni zaledni del bi moral na začetnem zaslonu biti prikazan kot zdrav.

> **Opomba:** Prvi zagon zgradi Pythonovo okolje agentskega strežnika, upravljano z `uv`, zato lahko traja nekaj minut, preden zaledni del sporoči, da je zdrav.

Ukaz `agent-canvas` skupaj zažene agentski strežnik, zaledni del za avtomatizacijo in spletni čelni del.
Za lokalni zagon OpenHands potrebujete samo ta en ukaz.
Preostanek tega priročnika vse konfigurira prek uporabniškega vmesnika Agent Canvas v brskalniku.
<!-- @os:end -->

<!-- @os:windows -->
V sistemu Windows zaženite objavljeno slikovno datoteko vsebnika Agent Canvas z aplikacijo Docker Desktop.
Slika vključuje agentski strežnik, zaledni del za avtomatizacijo in spletni čelni del, zato vam v gostiteljski sistem ni treba namestiti Node.js, `uv` ali ukazne vrstice.

Najprej ustvarite mape za konfiguracijo in delovni prostor, ki jih vsebnik priklopi:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Prenesite objavljeno sliko (približno 6 GB; je javna, zato prijava ni potrebna):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Nato zaženite nabor storitev:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Odprite `http://localhost:8000/canvas` v brskalniku.
Če so vrata 8000 že v uporabi, preslikajte druga gostiteljska vrata, na primer `-p 8080:8000`, in namesto tega odprite `http://localhost:8080/canvas`.

> **Opomba:** Prvi zagon zgradi okolje agentskega strežnika znotraj vsebnika, zato lahko traja nekaj minut, preden zaledni del sporoči, da je zdrav.

Priklop `.openhands` ohranja vaš profil LLM, strežnike MCP in avtomatizacije tudi po ponovnih zagonih vsebnika.
Preostanek tega priročnika vse konfigurira prek uporabniškega vmesnika Agent Canvas v brskalniku na naslovu `http://localhost:8000/canvas`.
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
## 4. Konfiguracija lokalnega LLM-ja v uporabniškem vmesniku

Ob prvem zagonu se odpre postopek uvajanja (onboarding) v Agent Canvas.
V tem postopku:

1. Pustite **OpenHands** izbran kot agent in kliknite **Next**.
2. Na zaslonu **Set up your LLM** izberite **Advanced**.
3. Pustite **Authentication** nastavljeno na **API key**.
4. Nastavite **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavite **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Za **API Key** vnesite kateri koli neprazen nadomestni niz, na primer `lemonade-local`. Lemonade ne zahteva pravega ključa, vendar odjemalec OpenHands potrebuje neko vrednost za pošiljanje.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server teče znotraj vsebnika, zato nastavite **Base URL** na `http://host.docker.internal:13305/api/v1` namesto `http://127.0.0.1:13305/api/v1`.
> Znotraj vsebnika je `127.0.0.1` vsebnik sam; `host.docker.internal` doseže Lemonade, ki teče na gostiteljskem sistemu Windows, to gostiteljsko ime pa samodejno zagotovi Docker Desktop.
<!-- @os:end -->

Polja za povezavo bi morala izgledati takole.
Polje za API ključ je v uporabniškem vmesniku maskirano.

![Napredne nastavitve LLM ob prvi uporabi Agent Canvas z modelom Lemonade in lokalnim osnovnim URL-jem](assets/01-llm-advanced-settings.png)

Nato izberite **All** in nastavite dodatna polja za lokalni model:

1. Pomaknite se do **Custom Tokenizer** in ga nastavite na `Qwen/Qwen3.6-35B-A3B`.
2. Pomaknite se do **LiteLLM Extra Body** in ga nastavite na `{"enable_thinking": true}`.
3. Kliknite **Next**.

![Zavihek Agent Canvas All ob prvi uporabi LLM z Qwen custom tokenizerjem](assets/02-llm-all-tokenizer-settings.png)

![Zavihek Agent Canvas All ob prvi uporabi LLM s konfiguriranim LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Nastavitve LLM naj prikazujejo:

| Polje | Vrednost |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Predpona `openai/` pove LiteLLM, naj uporabi obliko zahtev, združljivo z OpenAI, proti končni točki Lemonade.
Custom tokenizer je izvirni tokenizer Hugging Face za model GGUF; omogoča OpenHands, da šteje enake žetone predloge za pogovor (chat-template), kot jih vidi lokalni strežnik modela.
Trenutni obrazec LLM ob prvi uporabi ne prikazuje nastavitev za condenser.
Če vaša različica Agent Canvas kasneje izpostavi nastavitve za condenser pod **Settings > LLM**, uporabite `llm_summarizing` in nastavite največje število žetonov pod velikostjo konteksta Lemonade, na primer `56000`.

## 5. Namestitev strežnikov MCP za GitHub in Slack

V uporabniškem vmesniku Agent Canvas odprite **Customize** (ali **Settings > MCP**), da dodate strežnike MCP, ki agentu zagotovijo orodja za GitHub in Slack.
Vrednosti žetonov se pošiljajo samo vašemu lokalnemu Agent Server-ju in se shranjujejo kot šifrirane nastavitve.

<!-- @os:windows -->
> **Windows (Docker):** spodnji ukazi strežnika MCP z `npx` tečejo znotraj vsebnika, ki že vključuje Node.js, zato se na gostitelju ne namesti nič dodatnega.
> Ker je `.openhands` priklopljen, strežniki MCP in njihovi žetoni ostanejo shranjeni tudi po ponovnem zagonu vsebnika.
<!-- @os:end -->

### Strežnik MCP za GitHub

Dodajte nov strežnik MCP z naslednjimi nastavitvami:

| Polje | Vrednost |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = vaš žeton GitHub |

Uporabite žeton GitHub z bralnim dostopom do repozitorija, ki ga želite povzeti.

### Strežnik MCP za Slack

Dodajte drugi strežnik MCP z naslednjimi nastavitvami:

| Polje | Vrednost |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID vašega kanala za povzetek |

Nastavite `SLACK_CHANNEL_IDS` na ID kanala za povzetek (enaka vrednost kot `SLACK_DIGEST_CHANNEL`), da agentu ni treba brskati po vseh Slack kanalih.

Ko dodate oba strežnika, uporabite gumb **Test** na vsakem, da preverite, ali se povežeta in oglašujeta orodja.
Strežnik GitHub bi moral navesti orodja GitHub, strežnik Slack pa orodja Slack.

![Stran MCP v Agent Canvas z nameščenima strežnikoma GitHub in Slack](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Ustvarjanje avtomatizacije za povzetek

V uporabniškem vmesniku Agent Canvas odprite stran **Automations** in ustvarite novo avtomatizacijo:

1. Izberite **Create automation** in izberite tip **Prompt preset**.
2. Nastavite **Name** na `GitHub Development Digest to Slack`.
3. Nastavite **Prompt** na naslednje besedilo, pri čemer nadomestite oznake mesta za repozitorij in kanal z vašimi vrednostmi:

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

4. Nastavite **Trigger** na **Cron** z urnikom `0 9 * * 1-5` (ob 9. uri med delovniki) in nastavite **Timezone** na svoj časovni pas, na primer `America/New_York`.
5. Nastavite **Timeout** na `900` sekund.
6. Shranite avtomatizacijo.

Stran s podrobnostmi avtomatizacije prikazuje novo avtomatizacijo z njenim cron sprožilcem in ustvarjeno vstopno točko prompt-preset.

![Podrobnosti avtomatizacije v Agent Canvas po ustvarjanju](assets/05-automation-created.png)
## 7. Testiranje avtomatizacije

Na strani s podrobnostmi avtomatizacije v uporabniškem vmesniku Agent Canvas:

1. Kliknite **Run now** (ali **Dispatch**), da avtomatizacijo takoj enkrat zaženete.
2. Spremljajte seznam zagonov na isti strani. Najnovejši zagon bi moral preiti v stanje `COMPLETED`.
3. Odprite ciljni Slack kanal. Vsebovati bi moral generirani povzetek.

Ni vam treba čakati na sprožitev po urniku cron — **Run now** sproži zagon na zahtevo, tako da lahko preverite, ali poziv, povezave MCP in objavljanje v Slack delujejo, preden se zanesete na urnik.

![Uspešno zaključen zagon avtomatizacije v Agent Canvas](assets/06-automation-run-completed.png)

![Slack kanal, ki prikazuje generirani povzetek OpenHands](assets/07-slackbot-message.png)

## Odpravljanje težav

<!-- @os:windows -->
- **Vrata Docker 8000 so že v uporabi:** preslikajte drugačna vrata gostitelja, na primer `docker run ... -p 8080:8000 ...`, in odprite `http://localhost:8080/canvas`.
- **`docker pull` ne uspe z napako pri poverilnicah** (na primer "A specified logon session does not exist"): zaženite ukaz pull iz interaktivne seje sistema Windows ali sliko vnaprej prenesite. Slika je javna, zato prijava z `docker login` ni potrebna.
- **Uporabniški vmesnik se naloži, vendar zaledje ni v redu:** ob prvem zagonu se znotraj vsebnika zgradi okolje Agent Server. Počakajte minuto in osvežite stran, nato preverite `docker logs <container>` za napredek.
- **Agent Canvas ne more doseči Lemonade iz vsebnika:** nastavite **Base URL** za LLM na `http://host.docker.internal:13305/api/v1` (ne `127.0.0.1`) in preverite, ali Lemonade teče na gostiteljskem sistemu Windows.
<!-- @os:end -->

- **Lemonade ne deluje:** znova ga zaženite z ukazom `lemonade run "${LEMONADE_MODEL}"` iz koraka 1, nato ponovno zaženite preverjanje stanja.
- **`npm install -g` ne uspe z napako pri dovoljenjih:** v sistemu Linux ali WSL konfigurirajte uporabniško lasten globalni imenik npm, ga dodajte v zagonsko datoteko lupine, nato znova namestite Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Če uporabljate `zsh`, dodajte enako vrstico `export PATH=...` v `~/.zshrc` namesto v `~/.bashrc`.
- **Agent Canvas zavrne nastavitve LLM po nastavitvi `custom_tokenizer`:** namestite `transformers` v okolje Python za Agent Server, po potrebi znova zaženite Agent Canvas in ponovno poskusite shraniti nastavitve LLM. OpenHands zahteva Transformers za nalaganje predloge klepeta tokenizatorja, kadar je nastavljen `custom_tokenizer`.
- **Agent Canvas ne more doseči Lemonade:** preverite `curl -fsS "${LEMONADE_BASE_URL}/health"` in potrdite, da se osnovni URL, vnesen v obrazcu LLM ob prvi uporabi ali v **Settings > LLM**, ujema z delujočo lokalno končno točko ali predorom HTTPS.
- **Nastavitve LLM niso bile shranjene:** prepričajte se, da ste po vnosu vrednosti kliknili **Next**. Znova odprite **Settings > LLM**, da preverite, ali so se vrednosti ohranile.
- **GitHub MCP ne vidi zasebnih repozitorijev:** preverite, ali ima žeton GitHub dostop za branje ciljnega repozitorija in ali gumb **Test** v MCP pod **Customize** oglašuje orodja GitHub.
- **Slack lahko bere kanale, vendar ne more objavljati:** povabite aplikacijo Slack v ciljni kanal in preverite, ali ima bot dovoljenje `chat:write`.
- **Avtomatizacija navaja preveč Slack kanalov:** uporabite ID Slack kanala in nastavite `SLACK_CHANNEL_IDS` na strežniku Slack MCP pod **Customize**.
- **Zagon avtomatizacije ne uspe ali preseže kontekst:** preverite, ali je bil Lemonade zagnan z `ctx_size=65536`, preverite, ali ima LLM OpenHands nastavljen `custom_tokenizer`, in uporabite izrecen repozitorij z rezultati GitHub, omejenimi na 3 do 5 elementov. Če vaša različica Agent Canvas ponuja nastavitve zgoščevalnika (condenser), nastavite največje število žetonov zgoščevalnika pod velikostjo kontekstnega okna Lemonade.

## Naslednji koraki

- Dodajte tedenski povzetek, ki vključuje samo izdaje.
- Dodajte avtomatizacijo, sproženo z dogodkom GitHub, za hitrejša opozorila o PR ali potiskih (push).
- Preusmerite isti povzetek v Notion, Linear ali drugo orodje, podprto z MCP.

## Viri

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Dokumentacija Lemonade Server](https://lemonade-server.ai/docs)
- [Repozitorij razširitev OpenHands](https://github.com/OpenHands/extensions)
- [Strežniki Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Paket Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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