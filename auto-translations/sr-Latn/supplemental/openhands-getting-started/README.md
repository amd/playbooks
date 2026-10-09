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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) je AI softverski agent koji može da piše kod, pokreće komande, pretražuje veb i uređuje fajlove u pravom radnom prostoru. Umesto kopiranja predloga iz prozora za ćaskanje, usmeravate agenta na fasciklu projekta i prepuštate mu posao: implementaciju funkcije, popravku greške, pisanje testova ili objašnjenje koda.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je preporučeni veb interfejs za pokretanje OpenHands-a. Jedna komanda `agent-canvas` pokreće server agenta, pozadinski sistem za automatizaciju i veb frontend zajedno, tako da možete voditi razgovor sa agentom iz svog pregledača.

Da bi sve ostalo na vašem AMD sistemu, agent komunicira sa lokalnim modelom koji opslužuje Lemonade Server. Lemonade izlaže taj model putem API-ja kompatibilnog sa OpenAI, tako da Agent Canvas može da ga konfiguriše kao bilo koju drugu krajnju tačku u OpenAI stilu, dok model, vaš kod i kontekst razgovora ostaju na vašem računaru.

U ovom vodiču ćete pokrenuti lokalni model, pokrenuti Agent Canvas, usmeriti ga na taj model i izvršiti svoj prvi zadatak kodiranja nad pravom fasciklom projekta.

## Šta ćete naučiti

- Kako da pokrenete Lemonade Server i potvrdite da lokalni model odgovara na zahteve za ćaskanje
- Kako da instalirate i pokrenete Agent Canvas iz npm paketa
- Kako da konfigurišete Agent Canvas da koristi lokalni Lemonade model kao LLM
- Kako da pokrenete OpenHands razgovor i posmatrate kako agent uređuje fajlove i pokreće komande u radnom prostoru
- Kako da pregledate šta je agent promenio i usmerite ga dodatnim porukama

## Osnovni koncepti

| Koncept | Šta je to | Gde se uklapa u ovaj vodič |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma za opsluživanje LLM-ova izgrađena za AMD hardver koja izlaže API kompatibilan sa OpenAI. Vaši podaci nikada ne napuštaju vaš računar. | Pokreće model koji pokreće agenta. |
| OpenHands | AI softverski agent koji čita i uređuje fajlove, pokreće komande ljuske i pretražuje veb unutar radnog prostora. | Agent kojim upravljate iz ćaskanja. |
| Agent Canvas | Veb interfejs i pozadinski sistem koji pokreće OpenHands razgovore i prikazuje pozive alata i izmene fajlova. | Pokreće celokupan sistem i ugošćava vaš razgovor. |
| Radni prostor | Fascikla projekta koju agent sme da čita i menja. | Meta agentovih izmena i komandi. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Radni tokovi agenata za kodiranje imaju koristi od većeg modela i prozora konteksta. Koristite najmanje 32 GB sistemske memorije, a za veće GGUF modele preporučuje se 64 GB ili više.
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
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so the host needs only Docker and the model.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:docker,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

Potrebno vam je:

- Instaliran Lemonade Server koji može da opslužuje model naveden ispod.

<!-- @os:linux -->
- Node.js 22.12 ili noviji i `npm` (koristi ih `agent-canvas` CLI).
- `uv`, Python menadžer paketa koji Agent Canvas koristi za upravljanje okruženjem servera agenta. Ako vaš sistem još uvek nema instaliran, instalirajte ga prema [vodiču za instalaciju uv-a](https://docs.astral.sh/uv/getting-started/installation/) pre pokretanja Agent Canvas-a.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop za Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  instaliran i pokrenut. Na Windows-u, Agent Canvas sistem se pokreće iz objavljene Docker
  slike, koja uključuje Node.js, `uv` i paket
  `@openhands/agent-canvas`, tako da te komponente ne morate da instalirate na host sistemu.
<!-- @os:end -->

- Fascikla projekta u kojoj ćete raditi. To može biti bilo koji lokalni git repozitorijum ili
  direktorijum sa kodom na kojem želite da agent radi.

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

> **Izaberite model koji odgovara vašem hardveru.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je snažan model za kodiranje, ali zahteva veliki memorijski prostor. Ako vaš uređaj ima ograničenu memoriju ili GPU VRAM, umesto toga izaberite manji GGUF model iz Lemonade biblioteke modela i koristite taj ID modela kroz ceo ovaj vodič.

> **Napomena:** Prvo pokretanje `lemonade run` preuzima model ako već nije prisutan, što može potrajati u zavisnosti od veličine modela i brzine vaše veze.

Lemonade izlaže API kompatibilan sa OpenAI na adresi:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Provera lokalnog modela

Potvrdite da Lemonade može da opslužuje izabrani model:

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
## 3. Instalirajte i pokrenite Agent Canvas

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

Zatim pokrenite ceo paket iz terminala:

```bash
agent-canvas
```

Podrazumevano, Agent Canvas se pokreće na `http://localhost:8000`. Otvorite taj URL u
vašem pregledaču. Port nije poseban — ako je 8000 već zauzet, prosledite bilo koji
slobodan port pomoću `--port` (ili `-p`) kada pokrećete Agent Canvas:

```bash
agent-canvas --port 3000
```

Zatim otvorite `http://localhost:3000` umesto toga. Podrazumevani lokalni bekend treba da bude prikazan
kao ispravan na početnom ekranu.

Komanda `agent-canvas` pokreće server agenta, bekend za automatizaciju i
veb frontend zajedno. Potrebna vam je samo ova jedna komanda da pokrenete OpenHands
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
Na Windows-u, pokrenite objavljenu Agent Canvas kontejnersku sliku pomoću Docker Desktop-a.
Slika uključuje Agent Server, bekend za automatizaciju i veb frontend, tako da
ne morate da instalirate Node.js, `uv` ili CLI na hostu.

Prvo, kreirajte fascikle za konfiguraciju i radni prostor koje kontejner montira:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Preuzmite objavljenu sliku (javna je, tako da prijavljivanje nije potrebno):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Zatim pokrenite paket:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Otvorite `http://localhost:8000/canvas` u vašem pregledaču. Ako je port 8000 već
zauzet, mapirajte drugačiji host port, na primer `-p 8080:8000`, i otvorite
`http://localhost:8080/canvas` umesto toga.

> **Napomena:** Prvo pokretanje inicijalizuje Agent Server unutar kontejnera,
> tako da može proći minut ili dva pre nego što bekend prijavi da je ispravan.

Montiranje `.openhands` čuva vaš LLM profil i podešavanja između ponovnih pokretanja
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

## 4. Konfigurišite lokalni LLM

Pri prvom pokretanju, Agent Canvas otvara tok uvođenja (onboarding). U tom toku:

1. Ostavite **OpenHands** izabran kao agent i kliknite na **Next**.
2. Na **Set up your LLM**, izaberite **Advanced**.
3. Ostavite **Authentication** podešeno na **API key**.
4. Podesite **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Podesite **Base URL** na `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Na Windows-u se paket izvršava u kontejneru, koji ne može da pristupi hostu na
   > `127.0.0.1`. Umesto toga koristite `http://host.docker.internal:13305/api/v1` tako da
   > kontejnerizovani agent može da pristupi Lemonade-u koji se izvršava na Windows hostu.
   <!-- @os:end -->
6. Za **API Key**, unesite bilo koju nepraznu rezervisanu vrednost kao što je `lemonade-local`.
   Lemonade ne zahteva pravi ključ, ali OpenHands klijentu je potrebna vrednost
   da bi je poslao.
7. Kliknite na **Next**.

Dovršena Advanced podešavanja treba da izgledaju ovako. Polje za API ključ je
maskirano u korisničkom interfejsu.

![Agent Canvas Advanced podešavanja LLM-a pri prvoj upotrebi sa Lemonade modelom i lokalnim base URL-om](assets/01-llm-advanced-settings.png)

Agent Canvas čuva ove vrednosti kao LLM profil. Ako vaša verzija traži da
imenujete taj profil, koristite ime bez razmaka kao što je `lemonade-local`. Ako kasnije
promenite modele, otvorite **Settings > LLM** i ažurirajte ista Advanced polja. Možete
da prebacujete sačuvane profile iz polja za unos ćaskanja pomoću komande `/model`.

## 5. Otvorite radni prostor

Agent može samo da čita i menja fajlove unutar radnog prostora koji vi izaberete. Pre
pokretanja zadatka, usmerite Agent Canvas na vašu fasciklu projekta:

1. Sa početnog ekrana, izaberite **Open Workspace**.
2. Izaberite fasciklu koja sadrži vaš projekat (na primer, git repozitorijum
   na kome želite da agent radi).
3. Pokrenite novi razgovor u tom radnom prostoru.

Sve što agent radi—čitanje fajlova, pokretanje komandi, uređivanje koda—ograničeno je
na taj radni prostor.

![Agent Canvas početni ekran posle uvođenja](assets/02-agent-canvas-home.png)

## 6. Pokrenite svoj prvi zadatak kodiranja

Sa otvorenim radnim prostorom i izabranim lokalnim LLM-om, unesite konkretan zadatak u
ćaskanje. Dobar prvi zadatak je mali i proverljiv, na primer:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Posmatrajte vremensku liniju razgovora. OpenHands će:

- Pročitati radni prostor da bi razumeo strukturu.
- Kreirati `hello.py` sa traženom funkcijom i test blokom.
- Opciono pokrenuti `python3 hello.py` da bi proverio izlaz.
- Prijaviti šta je uradio i izlaz bilo koje komande u ćaskanju.

Trebalo bi da vidite da se novi fajl pojavljuje u radnom prostoru, i agentova konačna
poruka treba da opiše promenu koju je napravio. Ovo je trenutak isplate: agent je napisao
i pokrenuo pravi kod u vašoj fascikli projekta.

## 7. Pregledajte i usmeravajte agenta

Nakon što agent završi korak, pregledajte njegov rad pre nego što prihvatite sledeći:

- **Izmene fajlova**: koristite pregledač fajlova radnog prostora ili agentov prikaz razlika da
  biste videli tačno šta je dodato, promenjeno ili obrisano.
- **Izlaz komande**: proširite bilo koju komandu koju je agent pokrenuo da biste videli stdout, stderr,
  i izlazni kod.
- **Dodatni zahtevi**: ako rezultat nije onakav kakav ste želeli, odgovorite u istom
  razgovoru sa ispravkom. Agent zadržava prethodni kontekst i
  nastavlja da radi na istim fajlovima.

Na primer, ako test nije ispisao očekivani pozdrav, odgovorite:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent će ponovo pročitati fajl, pokrenuti komandu, dijagnostikovati problem i izmeniti
fajl ponovo—sve u istom razgovoru.
## Rešavanje problema

<!-- @os:linux -->
- **`agent-canvas` nije na PATH-u:** ponovo instalirajte pomoću
  `npm install -g @openhands/agent-canvas` i proverite da li se direktorijum
  globalnih binarnih fajlova npm-a nalazi na vašem PATH-u pre nego što
  `agent-canvas` bude moguće pokrenuti iz novog terminala.
- **`npm install -g` ne uspeva zbog greške sa dozvolama:** podesite globalni npm
  direktorijum čiji ste vlasnik vi, zatim ponovo otvorite terminal i ponovo
  instalirajte Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` nedostaje:** instalirajte ga prema
  [vodiču za instalaciju uv-a](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas koristi `uv` za upravljanje Python okruženjem servera agenta.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` ili `docker run` ne uspevaju da se povežu:** proverite da li
  je Docker Desktop pokrenut (njegova ikonica kita se nalazi u traci sa
  ikonicama sistema) i da li je pokretanje mehanizma završeno. `docker version`
  bi trebalo da ispiše i Client i Server sekciju.
- **Kontejner se pokreće, ali bekend nikada ne postane ispravan (healthy):**
  prvo pokretanje inicijalizuje Agent Server unutar kontejnera; sačekajte
  minut ili dva, a zatim proverite `docker logs <container>` radi grešaka.
- **Kontejner ne može da dosegne Lemonade:** kontejner dopire do hosta preko
  `host.docker.internal`. Potvrdite da Lemonade opslužuje zahteve na Windows
  hostu pomoću `lemonade status`, i koristite
  `http://host.docker.internal:13305/api/v1` kao Base URL prilikom
  konfigurisanja LLM-a.
<!-- @os:end -->

- **UI se učitava, ali bekend prikazuje da nije ispravan (unhealthy):**
  sačekajte minut ili dva da server agenta završi pokretanje, a zatim osvežite
  stranicu. Ako ostane neispravan, ponovo pokrenite stek i proverite logove
  radi grešaka.
- **Zahtevi za Lemonade ćaskanje ne uspevaju uz grešku povezivanja:** proverite
  da li `curl -fsS "http://127.0.0.1:13305/api/v1/health"` uspeva i da li
  Lemonade i dalje opslužuje model pomoću `lemonade status`.
- **Agent prijavljuje grešku u vezi sa dužinom konteksta ili ograničenjem
  broja tokena:** započnite novi razgovor kako agent ne bi nosio preveliku
  istoriju. Ako se ovo i dalje dešava, ponovo pokrenite Lemonade sa većim
  `ctx_size` od podrazumevanih 65536 (na primer `ctx_size=131072`), ukoliko
  memorija to dozvoljava.
- **Agent proizvodi izmene lošeg kvaliteta ili nepotpune izmene:** pređite na
  veći model u Lemonade-u, ili dajte agentu manji, konkretniji zadatak i
  sačekajte da ga završi pre nego što zatražite sledeću izmenu.

## Sledeći koraci

- Isprobajte veći zadatak u istom radnom prostoru, kao što je dodavanje
  fajla za jedinično testiranje ili ispravljanje poznate greške, i pregledajte
  razliku (diff) koju je agent napravio pre nego što zadržite izmenu.
- Povežite MCP server poput GitHub-a ili Slack-a u okviru **Customize** kako bi
  agent mogao da čita probleme ili objavljuje ažuriranja dok radi.
- Sačuvajte nekoliko LLM profila (brz mali model i jači veliki model) i
  prebacujte se između njih pomoću `/model` tokom razgovora.
- Pređite na [OpenHands automatizacije](https://docs.openhands.dev/openhands/usage/automations/overview) kako
  biste ponavljajuće razvojne cikluse pretvorili u zakazana ili na događaje
  okinuta pokretanja agenta.

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