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

Razvijalci porabijo veliko časa za majhne ponavljajoče se zanke: pregledovanje označenih pull requestov, odgovarjanje na komentarje GitHub, triažo novih issuejev, spreminjanje niti Slack v zapiske za dnevni sestanek ali nadaljnje ukrepe po incidentu ter spremljanje signalov o izdajah ali raziskavah.
Vsaka zanka je znana, a vseeno zahteva presojo: zbrati pravi kontekst, odločiti, kaj je pomembno, in objaviti jasno posodobitev tam, kjer ekipa že dela.

[Avtomatizacije OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) te zanke spremenijo v načrtovane ali z dogodki sprožene pogovore agenta: zagone, pri katerih lahko AI programski agent prebere kontekst, pokliče orodja in ustvari posodobitev.
Skupne predloge avtomatizacij v katalogu razširitev OpenHands sledijo temu vzorcu za pregled pull requestov na GitHub, spremljanje repozitorijev, triažo issuejev Linear, retrospektive incidentov, dnevne povzetke Slack in raziskovalne povzetke: avtomatizacija se prebudi, uporabi konfigurirane integracije, kot sta GitHub ali Slack, za pridobitev konteksta, razmišlja o tem kontekstu z velikim jezikovnim modelom (LLM) in zapiše rezultat nazaj.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je lokalna nadzorna ravnina za gradnjo in testiranje teh avtomatizacij.
V tem priročniku zažene strežnik OpenHands Agent Server, zaledni proces, ki izvaja pogovore agenta, in poveže agenta z zunanjimi storitvami, kot sta GitHub in Slack.

Da bi potek dela ostal na vašem sistemu AMD, se agent pogovarja z lokalnim modelom, ki ga streže Lemonade Server.
Lemonade ta model izpostavi prek API-ja, združljivega z OpenAI, tako da ga lahko Agent Canvas konfigurira kot oddaljeno končno točko v slogu OpenAI, medtem ko model, poziv in kontekst poteka dela ostanejo lokalni.

V tem priročniku boste zgradili eno konkretno avtomatizacijo: načrtovan razvojni povzetek iz GitHub v Slack.
Uporablja GitHub za pregled nedavne dejavnosti repozitorija, Slack za objavo povzetka, klice API-ja Agent Canvas za konfiguracijo in testiranje avtomatizacije ter Lemonade za lokalno izvajanje LLM.

![Diagram arhitekture, ki prikazuje GitHub MCP, avtomatizacijo OpenHands, Lemonade Server in Slack MCP](assets/00-architecture-overview.png)

## Kaj se boste naučili

- Kako zagnati Lemonade Server in preveriti, ali lokalni model odgovarja na zahteve za klepet
- Kako zagnati Agent Canvas in usmeriti njegov Agent Server na lokalni LLM
- Kako namestiti strežnike GitHub in Slack Model Context Protocol (MCP) prek API-ja Agent Server
- Kako ustvariti in sprožiti načrtovano avtomatizacijo OpenHands, ki objavi razvojni povzetek v Slack
- Kako odpraviti najpogostejše napake lokalnega modela in avtomatizacije

## Osnovni koncepti

| Koncept | Kaj je | Kam sodi v ta priročnik |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma za strežbo LLM, zgrajena za strojno opremo AMD, ki izpostavi API, združljiv z OpenAI. Vaši podatki nikoli ne zapustijo vašega računalnika. | Poganja model, ki napaja agenta. |
| OpenHands Agent Server | Zaledni proces, ki izvaja pogovore agenta OpenHands. | Gosti agenta, njegov profil LLM in njegove strežnike MCP. |
| Agent Canvas | Lokalna nadzorna ravnina za OpenHands, ki poganja Agent Server in uporabniški vmesnik za pregledovanje zagonov agenta. | Zažene zaledne sisteme in zagotovi API, ki ga kličete. |
| Strežnik MCP | Strežnik Model Context Protocol, ki agentu zagotavlja orodja za zunanjo storitev, kot sta GitHub ali Slack. | Agentu omogoča branje iz GitHub in pisanje v Slack. |
| Avtomatizacija OpenHands | Načrtovan ali z dogodki sprožen pogovor agenta, ki pridobi kontekst, razmišlja o njem in nekje zapiše rezultat. | Povzetek iz GitHub v Slack, ki ga zgradite tukaj. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Poteki dela agenta za kodiranje imajo koristi od večjega modela in večjega konteksta.
> Uporabite vsaj 32 GB sistemskega pomnilnika, pri večjih modelih GGUF pa dajte prednost 64 GB ali več.
<!-- @device:end -->

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Predpogoji

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

Potrebujete:

- Nameščen Lemonade Server po standardnih navodilih v [vodniku za namestitev Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 ali novejši ter `npm`, za namestitev objavljenega vmesnika CLI Agent Canvas in zagon strežnikov MCP z `npx`.
- `uv`, upravitelja paketov Python, ki ga Agent Canvas uporablja za gradnjo okolja Agent Server. Če še ni nameščen, ga namestite iz [vodnika za namestitev uv](https://docs.astral.sh/uv/getting-started/installation/).
- Nedaven objavljen paket `@openhands/agent-canvas` s shemsko vodenimi nastavitvami agenta, podporo za `LLMSummarizingCondenserSettings.max_tokens` in podporo za `custom_tokenizer` pri LLM.
- Paket Python `transformers`, na voljo v okolju Agent Server. Potreben je za štetje žetonov predloge klepeta, kadar je nastavljen `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop za Windows](https://docs.docker.com/desktop/setup/install/windows-install/), nameščen in zagnan. V sistemu Windows se sklad Agent Canvas izvaja iz objavljene slike Docker, ki vključuje Node.js, `uv`, `transformers` in paket `@openhands/agent-canvas`, zato jih ni treba nameščati na gostitelju.
<!-- @os:end -->

- Žeton GitHub z bralnim dostopom do repozitorija, ki ga želite povzeti.
- Žeton bota Slack (`xoxb-...`) z `chat:write` in bralnim dostopom do kanala.
- ID ekipe Slack (`T...`).
- ID kanala Slack (`C...`), kamor naj se objavi povzetek.

Pred testiranjem avtomatizacije povabite aplikacijo Slack v ciljni kanal.
## Spremenljivke, uporabljene v tem priročniku

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

Ti dve spremenljivki se uporabljata v spodnjih preverjalnih ukazih.
Model, tokenizator in druge nastavitve LLM se v naslednjih korakih vnesejo neposredno v uporabniškem vmesniku Agent Canvas, zato so njihove dejanske vrednosti prikazane neposredno tam, kjer jih boste potrebovali.

Naslednje vrednosti se v naslednjih korakih vnesejo v uporabniški vmesnik Agent Canvas.
Nastavite jih tukaj, da jih lahko kasneje kopirate:

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
> Če ima vaša naprava omejen pomnilnik ali VRAM GPE, izberite manjši model GGUF iz knjižnice modelov Lemonade in uporabite ta ID modela (in njegov ustrezni tokenizator) skozi celoten priročnik.

> **Opomba:** Ob prvem zagonu `lemonade run` prenese model, če ta še ni prisoten, kar lahko traja nekaj časa, odvisno od velikosti modela in vaše povezave.

Lemonade izpostavi API, združljiv z OpenAI, na:

```text
http://127.0.0.1:13305/api/v1
```

Izbirno: če Agent Canvas ali izvajalnik avtomatizacije nista na isti napravi, objavite končno točko Lemonade prek varnega tunela in uporabite naslov URL HTTPS kot osnovni naslov URL LLM.
[ngrok](https://ngrok.com/) izpostavi lokalna vrata internetu prek varnega naslova URL HTTPS; zahteva brezplačen račun ngrok, pri čemer `YOUR_NGROK_DOMAIN.ngrok-free.dev` zamenjate s svojo rezervirano domeno:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Preverjanje lokalnega modela

Potrdite, da lahko Lemonade postreže izbrani model:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Nato pošljite majhno zahtevo za klepet:

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

Nato pošljite majhno zahtevo za klepet:

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
Namestite objavljeni paket Agent Canvas in zaženite celoten sklad:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Če globalna namestitev npm ne uspe zaradi napake z dovoljenji, si oglejte spodnjo postavko za odpravljanje težav z dovoljenji npm.

Privzeto se Agent Canvas zažene na `http://localhost:8000`.
Odprite ta naslov URL v brskalniku.
Vrata niso posebna — če so vrata 8000 že v uporabi, podajte katera koli prosta vrata z `--port` (ali `-p`).
Privzeti lokalni zaledni sistem naj bi se na domačem zaslonu prikazal kot zdrav.

> **Opomba:** Prvi zagon izgradi s `uv` upravljano okolje Python za strežnik agentov, zato lahko traja nekaj minut, preden zaledje javi, da je zdravo.

Ukaz `agent-canvas` skupaj zažene strežnik agentov, zaledje avtomatizacije in spletni vmesnik.
Za lokalni zagon OpenHands potrebujete samo ta en ukaz.
Preostanek tega priročnika vse konfigurira prek uporabniškega vmesnika Agent Canvas v vašem brskalniku.
<!-- @os:end -->

<!-- @os:windows -->
V sistemu Windows zaženite objavljeno slovno sliko vsebnika Agent Canvas z Docker Desktop.
Slika združuje strežnik agentov, zaledje avtomatizacije in spletni vmesnik, zato na gostitelju ni treba namestiti Node.js, `uv` ali ukazne vrstice.

Najprej ustvarite mape za konfiguracijo in delovni prostor, ki jih vsebnik priklopi:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Prenesite objavljeno sliko (približno 6 GB; je javna, zato prijava ni potrebna):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Nato zaženite sklad:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Odprite `http://localhost:8000/canvas` v brskalniku.
Če so vrata 8000 že v uporabi, preslikajte drugačna gostiteljska vrata, na primer `-p 8080:8000`, in namesto tega odprite `http://localhost:8080/canvas`.

> **Opomba:** Prvi zagon izgradi okolje strežnika agentov znotraj vsebnika, zato lahko traja nekaj minut, preden zaledje javi, da je zdravo.

Priklop `.openhands` ohrani vaš profil LLM, strežnike MCP in avtomatizacije med ponovnimi zagoni vsebnika.
Preostanek tega priročnika vse konfigurira prek uporabniškega vmesnika Agent Canvas v vašem brskalniku na `http://localhost:8000/canvas`.
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
## 4. Konfigurirajte lokalni LLM v uporabniškem vmesniku

Ob prvem zagonu Agent Canvas odpre postopek uvajanja.
V tem postopku:

1. Pustite **OpenHands** izbran kot agent in kliknite **Next**.
2. Na zaslonu **Set up your LLM** izberite **Advanced**.
3. Pustite **Authentication** nastavljeno na **API key**.
4. Nastavite **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavite **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Pri **API Key** vnesite poljuben neprazen nadomestni niz, na primer `lemonade-local`. Lemonade ne zahteva pravega ključa, vendar odjemalec OpenHands potrebuje vrednost za pošiljanje.

<!-- @os:windows -->
> **Windows (Docker):** strežnik Agent Server teče znotraj vsebnika, zato nastavite **Base URL** na `http://host.docker.internal:13305/api/v1` namesto `http://127.0.0.1:13305/api/v1`.
> Znotraj vsebnika je `127.0.0.1` vsebnik sam; `host.docker.internal` doseže Lemonade, ki teče na gostitelju Windows, Docker Desktop pa to gostiteljsko ime zagotovi samodejno.
<!-- @os:end -->

Polja za povezavo bi morala izgledati tako.
Polje API-ključa je v uporabniškem vmesniku zakrito.

![Napredne nastavitve LLM ob prvi uporabi Agent Canvas z modelom Lemonade in lokalnim osnovnim naslovom URL](assets/01-llm-advanced-settings.png)

Nato izberite **All** in nastavite dodatna polja za lokalni model:

1. Pomaknite se do **Custom Tokenizer** in ga nastavite na `Qwen/Qwen3.6-35B-A3B`.
2. Pomaknite se do **LiteLLM Extra Body** in nastavite na `{"enable_thinking": true}`.
3. Kliknite **Next**.

![Zavihek LLM All ob prvi uporabi Agent Canvas s prilagojenim tokenizatorjem Qwen](assets/02-llm-all-tokenizer-settings.png)

![Zavihek LLM All ob prvi uporabi Agent Canvas s konfiguriranim LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Nastavitve LLM naj prikazujejo:

| Polje | Vrednost |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Predpona `openai/` pove LiteLLM, naj proti končni točki Lemonade uporabi oblikovanje zahtev, združljivo z OpenAI.
Prilagojeni tokenizator je izvirni tokenizator Hugging Face za model GGUF; omogoča, da OpenHands šteje iste tokene predloge pogovora (chat-template), kot jih vidi lokalni strežnik modela.
Trenutni obrazec LLM ob prvi uporabi ne prikazuje nastavitev zgoščevalnika (condenser).
Če vaša izdaja Agent Canvas pozneje izpostavi nastavitve zgoščevalnika pod **Settings > LLM**, uporabite `llm_summarizing` in nastavite največje število tokenov pod oknom konteksta Lemonade, na primer `56000`.

## 5. Namestite strežnika MCP za GitHub in Slack

V uporabniškem vmesniku Agent Canvas odprite **Customize** (ali **Settings > MCP**), da dodate strežnike MCP, ki agentu zagotovijo orodja za GitHub in Slack.
Vrednosti žetonov se pošljejo samo vašemu lokalnemu strežniku Agent Server in se shranijo kot šifrirane nastavitve.

<!-- @os:windows -->
> **Windows (Docker):** spodnji ukazi strežnika MCP z `npx` tečejo znotraj vsebnika, ki že vključuje Node.js, zato se na gostitelju ne namesti nič dodatnega.
> Ker je `.openhands` priklopljen, strežniki MCP in njihovi žetoni ostanejo ohranjeni tudi po ponovnem zagonu vsebnika.
<!-- @os:end -->

### Strežnik MCP za GitHub

Dodajte nov strežnik MCP s temi nastavitvami:

| Polje | Vrednost |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = vaš žeton GitHub |

Uporabite žeton GitHub z bralnim dostopom do repozitorija, za katerega želite povzetek.

### Strežnik MCP za Slack

Dodajte drugi strežnik MCP s temi nastavitvami:

| Polje | Vrednost |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID vašega kanala za povzetek |

Nastavite `SLACK_CHANNEL_IDS` na ID kanala za povzetek (enaka vrednost kot `SLACK_DIGEST_CHANNEL`), da agentu ni treba brskati po vseh kanalih Slack.

Po dodajanju obeh strežnikov uporabite gumb **Test** na vsakem izmed njiju, da potrdite, da se poveže in oglašuje orodja.
Strežnik GitHub naj izpiše orodja GitHub, strežnik Slack pa orodja Slack.

![Stran MCP Agent Canvas z nameščenima strežnikoma GitHub in Slack](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Ustvarite avtomatizacijo za povzetek

V uporabniškem vmesniku Agent Canvas odprite stran **Automations** in ustvarite novo avtomatizacijo:

1. Izberite **Create automation** in nato tip **Prompt preset**.
2. Nastavite **Name** na `GitHub Development Digest to Slack`.
3. Nastavite **Prompt** na naslednje besedilo, pri čemer nadomestite ogrodje za repozitorij in kanal z vašimi vrednostmi:

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

4. Nastavite **Trigger** na **Cron** z urnikom `0 9 * * 1-5` (ob 9. uri ob delavnikih) in nastavite **Timezone** na vaš časovni pas, na primer `America/New_York`.
5. Nastavite **Timeout** na `900` sekund.
6. Shranite avtomatizacijo.

Stran s podrobnostmi avtomatizacije prikazuje novo avtomatizacijo z njenim cron sprožilcem in ustvarjeno vstopno točko prednastavljenega poziva (prompt preset).

![Podrobnosti avtomatizacije Agent Canvas po ustvarjanju](assets/05-automation-created.png)
## 7. Testiraj avtomatizacijo

Na strani s podrobnostmi avtomatizacije v uporabniškem vmesniku Agent Canvas:

1. Kliknite **Run now** (ali **Dispatch**), da avtomatizacijo takoj enkrat zaženete.
2. Opazujte seznam zagonov na isti strani. Najnovejši zagon bi moral preiti v stanje `COMPLETED`.
3. Odprite svoj ciljni Slack kanal. Vsebovati bi moral generiran povzetek.

Ni vam treba čakati, da se sproži urnik cron — **Run now** sproži zagon na zahtevo, tako da lahko preverite, ali poziv, povezave MCP in objavljanje v Slack delujejo, preden se zanesete na urnik.

![Uspešno zaključen zagon avtomatizacije Agent Canvas](assets/06-automation-run-completed.png)

![Slack kanal prikazuje generiran povzetek OpenHands](assets/07-slackbot-message.png)

## Odpravljanje težav

<!-- @os:windows -->
- **Vrata Docker 8000 so že v uporabi:** preslikajte drugačna vrata gostitelja, na primer `docker run ... -p 8080:8000 ...`, in odprite `http://localhost:8080/canvas`.
- **`docker pull` spodleti z napako poverilnic** (na primer "A specified logon session does not exist"): izvedite pull iz interaktivne seje v sistemu Windows ali vnaprej prenesite sliko (pull). Slika je javna, zato `docker login` ni potreben.
- **Uporabniški vmesnik se naloži, vendar je zaledje nezdravo:** prvi zagon zgradi okolje Agent Server znotraj vsebnika. Počakajte minuto in osvežite stran, nato preverite `docker logs <container>` za napredek.
- **Agent Canvas ne more doseči Lemonade iz vsebnika:** nastavite **Base URL** za LLM na `http://host.docker.internal:13305/api/v1` (ne `127.0.0.1`) in preverite, ali Lemonade teče na gostiteljskem sistemu Windows.
<!-- @os:end -->

- **Lemonade ne deluje:** znova ga zaženite z ukazom `lemonade run "${LEMONADE_MODEL}"` iz koraka 1, nato znova zaženite preverjanje stanja.
- **`npm install -g` spodleti z napako dovoljenj:** v sistemu Linux ali WSL konfigurirajte globalno mapo npm v lasti uporabnika, jo dodajte v zagonsko datoteko lupine, nato znova namestite Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Če uporabljate `zsh`, dodajte isto vrstico `export PATH=...` v `~/.zshrc` namesto v `~/.bashrc`.
- **Agent Canvas zavrne nastavitve LLM po nastavitvi `custom_tokenizer`:** namestite `transformers` v okolje Python za Agent Server, po potrebi znova zaženite Agent Canvas in ponovno poskusite shraniti nastavitve LLM. OpenHands potrebuje Transformers za nalaganje predloge pogovora tokenizerja, ko je nastavljen `custom_tokenizer`.
- **Agent Canvas ne more doseči Lemonade:** preverite `curl -fsS "${LEMONADE_BASE_URL}/health"` in potrdite, da se osnovni URL, vnesen v obrazec LLM ob prvi uporabi ali v **Settings > LLM**, ujema z delujočo lokalno končno točko ali predorom HTTPS.
- **Nastavitve LLM se niso shranile:** prepričajte se, da ste po vnosu vrednosti kliknili **Next**. Znova odprite **Settings > LLM**, da preverite, ali so se vrednosti ohranile.
- **GitHub MCP ne vidi zasebnih repozitorijev:** potrdite, da ima žeton GitHub dostop za branje do ciljnega repozitorija in da gumb **Test** za MCP v **Customize** prikazuje orodja GitHub.
- **Slack lahko bere kanale, vendar ne more objavljati:** povabite aplikacijo Slack v ciljni kanal in potrdite, da ima bot dovoljenje `chat:write`.
- **Avtomatizacija navede preveč kanalov Slack:** uporabite ID kanala Slack in nastavite `SLACK_CHANNEL_IDS` na strežniku Slack MCP v **Customize**.
- **Zagon avtomatizacije spodleti ali preseže kontekst:** potrdite, da je bil Lemonade zagnan s `ctx_size=65536`, potrdite, da ima LLM OpenHands nastavljen `custom_tokenizer`, in uporabite izrecen repozitorij z rezultati GitHub, omejenimi na 3 do 5 elementov. Če vaša različica Agent Canvas izpostavlja nastavitve kondenzorja (condenser), nastavite največje število žetonov kondenzorja pod kontekstnim oknom Lemonade.

## Naslednji koraki

- Dodajte tedenski povzetek samo za izdaje (release-only).
- Dodajte avtomatizacijo, sproženo z dogodki GitHub, za hitrejša opozorila o PR ali potiskih (push).
- Usmerite isti povzetek v Notion, Linear ali drugo orodje, podprto z MCP.

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