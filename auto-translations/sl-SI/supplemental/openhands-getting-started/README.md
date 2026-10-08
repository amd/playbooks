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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Pregled

[OpenHands](https://github.com/All-Hands-AI/OpenHands) je agent za umetno inteligenco za programsko opremo, ki lahko piše kodo, zaganja ukaze, brska po spletu in ureja datoteke v resničnem delovnem prostoru. Namesto kopiranja predlogov iz okna za klepet usmerite agenta na mapo projekta in mu prepustite delo: implementacijo funkcije, odpravljanje napake, pisanje testov ali razlago kodne baze.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je priporočeni vmesnik brskalnika za zagon OpenHands. En sam ukaz `agent-canvas` hkrati zažene strežnik agenta, zaledje za avtomatizacijo in spletni odjemalec, tako da lahko vodite pogovor z agentom iz brskalnika.

Da vse ostane na vašem sistemu AMD, agent komunicira z lokalnim modelom, ki ga strežba Lemonade Server. Lemonade izpostavi ta model prek API-ja, združljivega z OpenAI, tako da ga Agent Canvas lahko konfigurira kot katero koli drugo končno točko v slogu OpenAI, medtem ko model, vaša koda in kontekst pogovora ostanejo na vaši napravi.

V tem priročniku boste zagnali lokalni model, zagnali Agent Canvas, ga usmerili na ta model in izvedli svojo prvo nalogo kodiranja na resnični mapi projekta.

## Kaj se boste naučili

- Kako zagnati Lemonade Server in potrditi, da lokalni model odgovarja na zahteve za klepet
- Kako namestiti in zagnati Agent Canvas iz paketa npm
- Kako konfigurirati Agent Canvas za uporabo lokalnega modela Lemonade kot LLM
- Kako začeti pogovor OpenHands in opazovati, kako agent ureja datoteke in zaganja ukaze v delovnem prostoru
- Kako pregledati, kaj je agent spremenil, in ga usmerjati z nadaljnjimi sporočili

## Osnovni pojmi

| Pojem | Kaj je | Kam sodi v tem priročniku |
| --- | --- | --- |
| Lemonade Server | Platforma za lokalno strežbo LLM, zgrajena za strojno opremo AMD, ki izpostavi API, združljiv z OpenAI. Vaši podatki nikoli ne zapustijo vaše naprave. | Poganja model, ki napaja agenta. |
| OpenHands | Agent za umetno inteligenco za programsko opremo, ki bere in ureja datoteke, zaganja ukaze lupine in brska po spletu znotraj delovnega prostora. | Agent, ki ga upravljate iz klepeta. |
| Agent Canvas | Vmesnik brskalnika in zaledje, ki poganja pogovore OpenHands ter prikazuje klice orodij in spremembe datotek. | Zažene sklad in gosti vaš pogovor. |
| Delovni prostor | Mapa projekta, ki jo agent sme brati in spreminjati. | Cilj urejanja in ukazov agenta. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Delovni tokovi kodirnega agenta imajo korist od večjega modela in večjega kontekstnega okna. Uporabite vsaj 32 GB sistemskega pomnilnika, za večje modele GGUF pa priporočamo 64 GB ali več.
<!-- @device:end -->

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Predpogoji


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Potrebujete:

- Nameščen Lemonade Server, ki lahko streže spodnji model.

<!-- @os:linux -->
- Node.js 22.12 ali novejši in `npm` (uporablja ju CLI `agent-canvas`).
- `uv`, upravitelja paketov Python, ki ga Agent Canvas uporablja za upravljanje okolja strežnika agenta. Če ga vaš sistem še nima, ga namestite iz [vodnika za namestitev uv](https://docs.astral.sh/uv/getting-started/installation/), preden zaženete Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop za Windows](https://docs.docker.com/desktop/setup/install/windows-install/), nameščen in zagnan. V sistemu Windows se sklad Agent Canvas izvaja iz objavljene slike Docker, ki vključuje Node.js, `uv` in paket `@openhands/agent-canvas`, zato jih na gostitelju ni treba nameščati.
<!-- @os:end -->

- Mapo projekta, v kateri boste delali. To je lahko katero koli lokalno skladišče git ali mapa s kodo, na kateri želite, da agent dela.

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

## 1. Zagon Lemonade Server

Zaženite model iz CLI Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Izberite model, ki ustreza vaši strojni opremi.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je zmogljiv model za kodiranje, vendar potrebuje velik pomnilniški prostor. Če ima vaša naprava omejen pomnilnik ali VRAM GPU, namesto tega izberite manjši model GGUF iz knjižnice modelov Lemonade in ta ID modela uporabljajte v celotnem priročniku.

> **Opomba:** Prvi `lemonade run` prenese model, če ta še ni prisoten, kar lahko traja nekaj časa, odvisno od velikosti modela in vaše povezave.

Lemonade izpostavi API, združljiv z OpenAI, na:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Preverjanje lokalnega modela

Potrdite, da Lemonade lahko streže izbrani model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Nato pošljite majhno zahtevo za klepet:

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

Če se vrne polje `choices`, je Lemonade pripravljen za Agent Canvas.

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
## 3. Namestitev in zagon Agent Canvas

<!-- @os:linux -->
Globalno namestite izdano paketno različico Agent Canvas:

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

Nato zaženite celoten sklad iz terminala:

```bash
agent-canvas
```

Agent Canvas se privzeto zažene na `http://localhost:8000`. Odprite ta URL v
brskalniku. Vrata niso nič posebnega – če so vrata 8000 že zasedena, ob zagonu Agent Canvas
podajte katera koli prosta vrata z `--port` (ali `-p`):

```bash
agent-canvas --port 3000
```

Nato namesto tega odprite `http://localhost:3000`. Privzeto bi moral lokalni zaledni del
na domačem zaslonu biti prikazan kot zdrav.

Ukaz `agent-canvas` hkrati zažene agentski strežnik, zaledje za avtomatizacijo in
spletni vmesnik. Za lokalni zagon OpenHands potrebujete samo ta en ukaz.

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
V sistemu Windows zaženite izdano sliko vsebnika Agent Canvas z orodjem Docker Desktop.
Slika vključuje Agent Server, zaledje za avtomatizacijo in spletni vmesnik, zato
na gostitelju ni treba namestiti Node.js, `uv` ali ukazne vrstice.

Najprej ustvarite mapi za konfiguracijo in delovni prostor, ki ju vsebnik priklopi:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Prenesite izdano sliko (je javna, zato prijava ni potrebna):

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

Odprite `http://localhost:8000/canvas` v brskalniku. Če so vrata 8000 že
zasedena, preslikajte drugačna gostiteljska vrata, na primer `-p 8080:8000`, in namesto tega odprite
`http://localhost:8080/canvas`.

> **Opomba:** Ob prvem zagonu se Agent Server inicializira znotraj vsebnika,
> zato lahko traja minuto ali dve, preden zaledje javi, da je zdravo.

Priklop `.openhands` ohranja vaš profil LLM in nastavitve med ponovnimi zagoni
vsebnika. Preostali del tega vodnika konfigurira vse prek uporabniškega vmesnika
Agent Canvas v brskalniku.

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

## 4. Konfiguracija lokalnega LLM

Ob prvem zagonu Agent Canvas odpre postopek uvajanja. V tem postopku:

1. Pustite izbrano **OpenHands** kot agenta in kliknite **Next**.
2. V razdelku **Set up your LLM** izberite **Advanced**.
3. Pustite **Authentication** nastavljeno na **API key**.
4. Nastavite **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavite **Base URL** na `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > V sistemu Windows se sklad izvaja v vsebniku, ki ne more doseči gostitelja na
   > naslovu `127.0.0.1`. Namesto tega uporabite `http://host.docker.internal:13305/api/v1`, da
   > lahko vsebnikovan agent doseže Lemonade, ki se izvaja na gostitelju Windows.
   <!-- @os:end -->
6. V polje **API Key** vnesite kateri koli neprazen nadomestni niz, na primer `lemonade-local`.
   Lemonade ne zahteva pravega ključa, vendar odjemalec OpenHands potrebuje vrednost
   za pošiljanje.
7. Kliknite **Next**.

Dokončane napredne nastavitve bi morale izgledati takole. Polje za API-ključ
je v uporabniškem vmesniku zakrito.

![Napredne nastavitve LLM ob prvi uporabi Agent Canvas z modelom Lemonade in lokalnim osnovnim URL-jem](assets/01-llm-advanced-settings.png)

Agent Canvas te vrednosti shrani kot profil LLM. Če vas vaša različica prosi za
poimenovanje tega profila, uporabite ime brez presledkov, na primer `lemonade-local`. Če
pozneje spremenite modele, odprite **Settings > LLM** in posodobite ista napredna polja. Med
shranjenimi profili lahko preklapljate v vnosnem polju klepeta z ukazom `/model`.

## 5. Odpiranje delovnega prostora

Agent lahko bere in spreminja datoteke samo znotraj delovnega prostora, ki ga izberete. Preden
začnete opravilo, usmerite Agent Canvas v mapo svojega projekta:

1. Na domačem zaslonu izberite **Open Workspace**.
2. Izberite mapo, ki vsebuje vaš projekt (na primer git repozitorij,
   na katerem naj agent dela).
3. Začnite nov pogovor v tem delovnem prostoru.

Vse, kar agent počne – branje datotek, zagon ukazov, urejanje kode – je
omejeno na ta delovni prostor.

![Domači zaslon Agent Canvas po uvajanju](assets/02-agent-canvas-home.png)

## 6. Izvedite svoje prvo programersko opravilo

Ko je delovni prostor odprt in izbran lokalni LLM, v klepet vnesite konkretno
opravilo. Dobro prvo opravilo je majhno in preverljivo, na primer:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Opazujte časovnico pogovora. OpenHands bo:

- prebral delovni prostor, da razume postavitev,
- ustvaril `hello.py` z zahtevano funkcijo in testnim blokom,
- po potrebi zagnal `python3 hello.py`, da preveri izhod,
- v klepetu poročal, kaj je naredil, in morebiten izhod ukaza.

V delovnem prostoru bi se morala prikazati nova datoteka, agentovo zaključno
sporočilo pa bi moralo opisati spremembo, ki jo je naredil. To je trenutek izplačila:
agent je zapisal in zagnal pravo kodo v vaši projektni mapi.

## 7. Pregled in usmerjanje agenta

Ko agent zaključi korak, pred sprejetjem naslednjega pregledajte njegovo delo:

- **Spremembe datotek**: za natančen vpogled v to, kaj je bilo dodano, spremenjeno ali
  izbrisano, uporabite brskalnik datotek delovnega prostora ali agentov prikaz razlik (diff).
- **Izhod ukazov**: razširite kateri koli ukaz, ki ga je agent izvedel, da si ogledate stdout, stderr
  in izhodno kodo.
- **Nadaljnji koraki**: če rezultat ni tak, kot ste želeli, v istem
  pogovoru odgovorite s popravkom. Agent ohrani prejšnji kontekst in
  nadaljuje delo na istih datotekah.

Če na primer test ni izpisal pričakovanega pozdrava, odgovorite:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent bo ponovno prebral datoteko, zagnal ukaz, diagnosticiral težavo in znova uredil
datoteko – vse v istem pogovoru.
## Odpravljanje težav

<!-- @os:linux -->
- **`agent-canvas` ni na PATH:** znova namestite z
  `npm install -g @openhands/agent-canvas` in pred zagonom `agent-canvas` v novem
  terminalu preverite, ali je mapa z globalnimi binarnimi datotekami npm na vašem PATH.
- **`npm install -g` ne uspe zaradi napake z dovoljenji:** konfigurirajte uporabniško
  globalno mapo npm, nato znova odprite terminal in ponovno namestite Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` manjka:** namestite ga po navodilih na
  [vodniku za namestitev uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas uporablja `uv` za upravljanje Python okolja strežnika agenta.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` ali `docker run` se ne more povezati:** prepričajte se, da je Docker Desktop
  zagnan (njegova ikona kita je v sistemski vrstici) in da se je mehanizem (engine)
  končal z zagonom. `docker version` bi moral izpisati tako razdelek za odjemalca (Client) kot za strežnik (Server).
- **Vsebnik se zažene, vendar zaledje nikoli ni zdravo:** prvi zagon inicializira strežnik agenta
  znotraj vsebnika; počakajte minuto ali dve, nato preverite `docker logs <container>` za napake.
- **Vsebnik ne more doseči Lemonade:** vsebnik doseže gostitelja prek
  `host.docker.internal`. Potrdite, da Lemonade streže na gostitelju Windows z
  `lemonade status`, in pri konfiguraciji LLM uporabite `http://host.docker.internal:13305/api/v1` kot osnovni URL.
<!-- @os:end -->

- **Uporabniški vmesnik se naloži, vendar zaledje kaže kot nezdravo:** počakajte minuto ali dve,
  da strežnik agenta konča zagon, nato osvežite stran. Če ostane nezdravo, znova zaženite
  sklad in preverite dnevnike za napake.
- **Zahteve za klepet Lemonade ne uspejo z napako povezave:** potrdite, da
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` uspe in da Lemonade še vedno
  streže model z `lemonade status`.
- **Agent javi napako glede dolžine konteksta ali omejitve žetonov:** začnite
  nov pogovor, da agent ne nosi predolge zgodovine. Če se to še naprej dogaja,
  znova zaženite Lemonade z večjim `ctx_size`, kot je privzetih
  65536 (na primer `ctx_size=131072`), če vam pomnilnik to dopušča.
- **Agent ustvarja slabe ali nepopolne popravke:** preklopite na večji
  model v Lemonade ali dajte agentu manjšo, bolj konkretno nalogo in počakajte, da jo
  dokonča, preden zahtevate naslednjo spremembo.

## Naslednji koraki

- Preizkusite večjo nalogo v istem delovnem prostoru, na primer dodajte datoteko z enotskim testom ali
  odpravite znano napako, ter pred ohranitvijo spremembe preglejte agentovo razliko (diff).
- Povežite strežnik MCP, kot je GitHub ali Slack, v razdelku **Customize**, da
  lahko agent med delom bere težave (issues) ali objavlja posodobitve.
- Shranite več profilov LLM (hiter majhen model in zmogljivejši velik model) in
  preklapljajte med njimi z `/model` sredi pogovora.
- Nadaljujte z [avtomatizacijami OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview), da
  ponavljajoče se razvojne cikle spremenite v časovno ali dogodkovno sprožene zagone agenta.

## Viri

- [Dokumentacija OpenHands](https://docs.openhands.dev/)
- [Pregled Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Namestitev Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profili LLM in konfiguracija modela](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentacija Lemonade Server](https://lemonade-server.ai/docs)

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