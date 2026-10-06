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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Pregled

[OpenHands](https://github.com/All-Hands-AI/OpenHands) je AI softverski agent
koji može da piše kod, pokreće komande, pretražuje veb i uređuje fajlove u
stvarnom radnom okruženju. Umesto da kopirate predloge iz prozora za ćaskanje,
usmeravate agenta na fasciklu projekta i prepuštate mu posao: implementaciju
funkcije, ispravku greške, pisanje testova ili objašnjavanje koda.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je preporučeni
veb interfejs za pokretanje OpenHands-a. Jedna komanda `agent-canvas` pokreće
server agenta, pozadinski sistem za automatizaciju i veb frontend zajedno, tako
da možete da vodite razgovor sa agentom iz svog pregledača.

Da bi sve ostalo na vašem AMD sistemu, agent komunicira sa lokalnim modelom
koji servira Lemonade Server. Lemonade izlaže taj model kroz API kompatibilan
sa OpenAI-jem, tako da Agent Canvas može da ga podesi kao bilo koju drugu
krajnju tačku u OpenAI stilu, dok model, vaš kod i kontekst razgovora ostaju na
vašem računaru.

U ovom vodiču, pokrenućete lokalni model, pokrenuti Agent Canvas, usmeriti ga
na taj model i izvršiti svoj prvi zadatak kodiranja nad stvarnom fasciklom
projekta.

## Šta ćete naučiti

- Kako da pokrenete Lemonade Server i potvrdite da lokalni model odgovara na
  zahteve za ćaskanje
- Kako da instalirate i pokrenete Agent Canvas iz npm paketa
- Kako da podesite Agent Canvas da koristi lokalni Lemonade model kao LLM
- Kako da započnete OpenHands razgovor i posmatrate agenta dok uređuje fajlove
  i pokreće komande u radnom okruženju
- Kako da pregledate šta je agent promenio i usmerite ga daljim porukama

## Osnovni koncepti

| Koncept | Šta je to | Gde se uklapa u ovaj vodič |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma za serviranje LLM-ova napravljena za AMD hardver koja izlaže API kompatibilan sa OpenAI-jem. Vaši podaci nikada ne napuštaju vaš računar. | Pokreće model koji pokreće agenta. |
| OpenHands | AI softverski agent koji čita i uređuje fajlove, pokreće komande ljuske i pretražuje veb unutar radnog okruženja. | Agent kojim upravljate iz ćaskanja. |
| Agent Canvas | Veb interfejs i pozadinski sistem koji pokreće OpenHands razgovore i prikazuje pozive alatki i izmene fajlova. | Pokreće čitav sistem i smešta vaš razgovor. |
| Radno okruženje | Fascikla projekta koju je agentu dozvoljeno da čita i menja. | Cilj izmena i komandi agenta. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Tokovi rada sa agentom za kodiranje imaju koristi od većeg modela i prozora
> konteksta. Koristite najmanje 32 GB sistemske memorije, a za veće GGUF
> modele je poželjno 64 GB ili više.
<!-- @device:end -->

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->

## Preduslovi


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Potrebno vam je:

- Instaliran Lemonade Server koji može da servira model naveden ispod.

<!-- @os:linux -->
- Node.js 22.12 ili noviji i `npm` (koristi ih `agent-canvas` CLI).
- `uv`, menadžer Python paketa koji Agent Canvas koristi za upravljanje
  okruženjem servera agenta. Ako ga vaš sistem već nema, instalirajte ga iz
  [uv vodiča za instalaciju](https://docs.astral.sh/uv/getting-started/installation/)
  pre pokretanja Agent Canvas-a.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop za Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  instaliran i pokrenut. Na Windows-u, Agent Canvas sistem se izvršava iz
  objavljene Docker slike, koja u sebi sadrži Node.js, `uv` i paket
  `@openhands/agent-canvas`, tako da ih ne morate instalirati na domaćinu.
<!-- @os:end -->

- Fascikla projekta u kojoj ćete raditi. Ovo može biti bilo koji lokalni git
  repozitorijum ili direktorijum sa kodom na kojem želite da agent radi.

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

## 1. Pokretanje Lemonade Server-a

Pokrenite model iz Lemonade CLI-ja:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Izaberite model koji odgovara vašem hardveru.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je snažan model za kodiranje, ali zahteva veliku memoriju. Ako vaš uređaj ima ograničenu memoriju ili GPU VRAM, umesto toga izaberite manji GGUF model iz biblioteke Lemonade modela i koristite taj ID modela u celom ovom vodiču.

> **Napomena:** Prvo pokretanje `lemonade run` preuzima model ako već nije prisutan, što može potrajati u zavisnosti od veličine modela i vaše konekcije.

Lemonade izlaže API kompatibilan sa OpenAI-jem na:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Provera lokalnog modela

Potvrdite da Lemonade može da servira izabrani model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Zatim pošaljite mali zahtev za ćaskanje:

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
## 3. Instaliranje i pokretanje Agent Canvas

<!-- @os:linux -->
Instalirajte objavljeni Agent Canvas paket globalno:

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

Zatim pokrenite ceo stek iz terminala:

```bash
agent-canvas
```

Podrazumevano, Agent Canvas se pokreće na `http://localhost:8000`. Otvorite tu adresu u
svom pregledaču. Port nije ničim poseban — ako je 8000 već zauzet, prosledite bilo koji
slobodan port pomoću `--port` (ili `-p`) kada pokrećete Agent Canvas:

```bash
agent-canvas --port 3000
```

Zatim umesto toga otvorite `http://localhost:3000`. Podrazumevani lokalni bekend bi trebalo da se prikaže
kao ispravan na početnom ekranu.

Komanda `agent-canvas` pokreće server agenta, bekend za automatizaciju i
veb frontend zajedno. Potrebna vam je samo ova jedna komanda da biste pokrenuli OpenHands
lokalno.

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
Na Windows-u, pokrenite objavljenu Agent Canvas kontejner sliku pomoću Docker Desktop-a.
Slika uključuje Agent Server, bekend za automatizaciju i veb frontend, tako da
ne morate da instalirate Node.js, `uv` ili CLI na hostu.

Prvo, napravite fascikle za konfiguraciju i radni prostor koje kontejner montira:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Preuzmite objavljenu sliku (javna je, tako da prijava nije potrebna):

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

Otvorite `http://localhost:8000/canvas` u svom pregledaču. Ako je port 8000 već
zauzet, mapirajte drugi port na hostu, na primer `-p 8080:8000`, i umesto toga otvorite
`http://localhost:8080/canvas`.

> **Napomena:** Prvo pokretanje inicijalizuje Agent Server unutar kontejnera,
> tako da može proći minut ili dva pre nego što bekend prijavi da je ispravan.

Montirana fascikla `.openhands` čuva vaš LLM profil i podešavanja između ponovnih pokretanja
kontejnera. Ostatak ovog vodiča konfiguriše sve kroz Agent
Canvas korisnički interfejs u vašem pregledaču.

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

## 4. Konfigurisanje lokalnog LLM-a

Pri prvom pokretanju, Agent Canvas otvara tok uvođenja (onboarding). U tom toku:

1. Zadržite **OpenHands** izabran kao agenta i kliknite na **Next**.
2. Na **Set up your LLM**, izaberite **Advanced**.
3. Zadržite **Authentication** podešeno na **API key**.
4. Podesite **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Podesite **Base URL** na `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Na Windows-u stek radi u kontejneru, koji ne može da pristupi hostu na
   > `127.0.0.1`. Umesto toga koristite `http://host.docker.internal:13305/api/v1` kako bi
   > agent u kontejneru mogao da pristupi Lemonade-u koji radi na Windows hostu.
   <!-- @os:end -->
6. Za **API Key**, unesite bilo koji neprazan zamenski tekst poput `lemonade-local`.
   Lemonade-u nije potreban pravi ključ, ali OpenHands klijentu je potrebna vrednost
   za slanje.
7. Kliknite na **Next**.

Dovršena Advanced podešavanja bi trebalo da izgledaju ovako. Polje za API ključ je
maskirano u korisničkom interfejsu.

![Agent Canvas Advanced podešavanja LLM-a pri prvom korišćenju sa Lemonade modelom i lokalnom osnovnom adresom](assets/01-llm-advanced-settings.png)

Agent Canvas čuva ove vrednosti kao LLM profil. Ako vas vaša verzija zamoli da
imenujete taj profil, koristite ime bez razmaka, na primer `lemonade-local`. Ako kasnije
promenite modele, otvorite **Settings > LLM** i ažurirajte ista Advanced polja. Možete
prebacivati između sačuvanih profila iz polja za unos razgovora pomoću komande `/model`.

## 5. Otvaranje radnog prostora

Agent može da čita i menja samo fajlove unutar radnog prostora koji izaberete. Pre
pokretanja zadatka, usmerite Agent Canvas na fasciklu vašeg projekta:

1. Sa početnog ekrana, izaberite **Open Workspace**.
2. Izaberite fasciklu koja sadrži vaš projekat (na primer, git repozitorijum
   na kome želite da agent radi).
3. Pokrenite novi razgovor u tom radnom prostoru.

Sve što agent radi — čita fajlove, pokreće komande, menja kod — ograničeno je
na taj radni prostor.

![Agent Canvas početni ekran nakon uvođenja](assets/02-agent-canvas-home.png)

## 6. Pokretanje vašeg prvog zadatka kodiranja

Kada je radni prostor otvoren i lokalni LLM izabran, unesite konkretan zadatak u
ćaskanje. Dobar prvi zadatak je mali i proverljiv, na primer:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Pratite vremensku liniju razgovora. OpenHands će:

- Pročitati radni prostor da bi razumeo strukturu.
- Napraviti `hello.py` sa traženom funkcijom i test blokom.
- Opciono pokrenuti `python3 hello.py` da bi proverio izlaz.
- Izvestiti o tome šta je uradio i o svakom izlazu komande u ćaskanju.

Trebalo bi da vidite novi fajl kako se pojavljuje u radnom prostoru, a konačna poruka agenta
bi trebalo da opiše promenu koju je napravio. Ovo je trenutak isplate: agent je napisao i pokrenuo
pravi kod u vašoj fascikli projekta.

## 7. Pregled i usmeravanje agenta

Nakon što agent završi korak, pregledajte njegov rad pre nego što prihvatite sledeći:

- **Promene fajlova**: koristite pregledač fajlova radnog prostora ili prikaz razlika (diff) agenta da
  vidite tačno šta je dodato, promenjeno ili obrisano.
- **Izlaz komande**: proširite svaku komandu koju je agent pokrenuo da vidite stdout, stderr
  i izlazni kod.
- **Nastavci**: ako rezultat nije onakav kakav ste želeli, odgovorite u istom
  razgovoru sa ispravkom. Agent zadržava prethodni kontekst i
  nastavlja da radi na istim fajlovima.

Na primer, ako test nije ispisao očekivani pozdrav, odgovorite:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent će ponovo pročitati fajl, pokrenuti komandu, dijagnostikovati problem i ponovo urediti
fajl — sve u istom razgovoru.
## Rešavanje problema

<!-- @os:linux -->
- **`agent-canvas` nije u PATH-u:** ponovo instalirajte pomoću
  `npm install -g @openhands/agent-canvas` i proverite da li se globalni npm binarni
  direktorijum nalazi u PATH-u pre nego što `agent-canvas` bude moguće pokrenuti iz novog
  terminala.
- **`npm install -g` ne uspeva zbog greške u vezi sa dozvolama:** podesite globalni npm direktorijum
  koji je u vlasništvu korisnika, zatim ponovo otvorite terminal i ponovo instalirajte Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` nedostaje:** instalirajte ga prema
  [vodiču za instalaciju uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas koristi `uv` za upravljanje Python okruženjem servera agenta.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` ili `docker run` ne uspevaju da se povežu:** proverite da li je Docker Desktop
  pokrenut (njegova ikonica kita nalazi se u sistemskoj traci) i da li je mašina
  završila pokretanje. `docker version` bi trebalo da ispiše i Client i Server
  deo.
- **Kontejner se pokreće, ali backend nikada ne postaje ispravan:** prvo pokretanje
  inicijalizuje Agent Server unutar kontejnera; sačekajte minut ili
  dva, zatim proverite `docker logs <container>` zbog grešaka.
- **Kontejner ne može da dostigne Lemonade:** kontejner dolazi do hosta preko
  `host.docker.internal`. Potvrdite da Lemonade radi na Windows hostu pomoću
  `lemonade status` i koristite `http://host.docker.internal:13305/api/v1` kao
  osnovni URL prilikom konfigurisanja LLM-a.
<!-- @os:end -->

- **Korisnički interfejs se učitava, ali backend prikazuje da nije ispravan:** sačekajte minut ili dva
  da server agenta završi pokretanje, zatim osvežite stranicu. Ako i dalje ostane neispravan, ponovo pokrenite
  stek i proverite logove zbog grešaka.
- **Lemonade zahtevi za ćaskanje ne uspevaju zbog greške u vezi sa vezom:** potvrdite da
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` uspeva i da
  Lemonade i dalje služi model pomoću `lemonade status`.
- **Agent prijavljuje grešku u vezi sa dužinom konteksta ili ograničenjem broja tokena:** započnite
  novi razgovor kako agent ne bi nosio preveliku istoriju. Ako se ovo
  i dalje dešava, ponovo pokrenite Lemonade sa većim `ctx_size` od podrazumevanog
  65536 (na primer `ctx_size=131072`), ako memorija to dozvoljava.
- **Agent proizvodi izmene lošeg kvaliteta ili nepotpune izmene:** pređite na veći
  model u Lemonade-u, ili dajte agentu manji, konkretniji zadatak i sačekajte da ga
  završi pre nego što zatražite sledeću izmenu.

## Sledeći koraci

- Isprobajte veći zadatak u istom radnom prostoru, kao što je dodavanje datoteke sa jediničnim testom ili
  ispravljanje poznate greške, i pregledajte izmene agenta pre nego što ih zadržite.
- Povežite MCP server poput GitHub-a ili Slack-a u odeljku **Customize** kako bi
  agent mogao da čita pitanja ili objavljuje ažuriranja dok radi.
- Sačuvajte nekoliko LLM profila (brzi mali model i snažniji veliki model) i
  prebacujte se između njih pomoću `/model` tokom razgovora.
- Pređite na [OpenHands automatizacije](https://docs.openhands.dev/openhands/usage/automations/overview) kako biste
  pretvorili ponavljajuće razvojne cikluse u zakazana ili događajima pokrenuta izvršavanja agenta.

## Resursi

- [OpenHands dokumentacija](https://docs.openhands.dev/)
- [Pregled Agent Canvas-a](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Podešavanje Agent Canvas-a](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM profili i konfiguracija modela](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentacija Lemonade Server-a](https://lemonade-server.ai/docs)

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