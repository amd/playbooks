<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Přehled

[OpenHands](https://github.com/All-Hands-AI/OpenHands) je AI softwarový agent,
který dokáže psát kód, spouštět příkazy, procházet web a upravovat soubory ve
skutečném pracovním prostoru. Místo kopírování návrhů z chatovacího okna
nasměrujete agenta na složku projektu a necháte ho pracovat: implementovat
funkci, opravit chybu, napsat testy nebo vysvětlit kódovou základnu.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je doporučené
prohlížečové uživatelské rozhraní pro spouštění OpenHands. Jediný příkaz
`agent-canvas` spustí server agenta, automatizační backend a webové rozhraní
společně, takže konverzaci s agentem můžete vést přímo z prohlížeče.

Aby vše zůstalo na vašem systému AMD, agent komunikuje s lokálním modelem
poskytovaným pomocí Lemonade Server. Lemonade zpřístupňuje tento model
prostřednictvím API kompatibilního s OpenAI, takže Agent Canvas jej může
nakonfigurovat jako jakýkoli jiný koncový bod ve stylu OpenAI, zatímco model,
váš kód i kontext konverzace zůstávají na vašem počítači.

V tomto playbooku spustíte lokální model, spustíte Agent Canvas, nasměrujete
jej na tento model a spustíte svůj první úkol s kódem na skutečné složce
projektu.

## Co se naučíte

- Jak spustit Lemonade Server a ověřit, že lokální model odpovídá na chatové požadavky
- Jak nainstalovat a spustit Agent Canvas z npm balíčku
- Jak nakonfigurovat Agent Canvas tak, aby jako LLM používal lokální model Lemonade
- Jak zahájit konverzaci v OpenHands a sledovat, jak agent upravuje soubory a spouští
  příkazy v pracovním prostoru
- Jak zkontrolovat, co agent změnil, a usměrnit jej pomocí navazujících zpráv

## Základní pojmy

| Pojem | Co to je | Kde se uplatní v tomto playbooku |
| --- | --- | --- |
| Lemonade Server | Lokální platforma pro poskytování LLM postavená pro hardware AMD, která zpřístupňuje API kompatibilní s OpenAI. Vaše data nikdy neopustí váš počítač. | Spouští model, který pohání agenta. |
| OpenHands | AI softwarový agent, který čte a upravuje soubory, spouští příkazy shellu a prochází web uvnitř pracovního prostoru. | Agent, kterého řídíte z chatu. |
| Agent Canvas | Prohlížečové uživatelské rozhraní a backend, který spouští konverzace OpenHands a zobrazuje volání nástrojů a změny souborů. | Spouští celý stack a hostí vaši konverzaci. |
| Workspace | Složka projektu, kterou má agent povoleno číst a upravovat. | Cíl úprav a příkazů agenta. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Pracovní postupy s kódovacím agentem těží z většího modelu a většího kontextového okna. Použijte
> alespoň 32 GB systémové paměti a pro větší GGUF modely upřednostněte 64 GB nebo více.
<!-- @device:end -->

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Požadavky


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

Budete potřebovat:

- Nainstalovaný Lemonade Server schopný poskytovat níže uvedený model.

<!-- @os:linux -->
- Node.js 22.12 nebo novější a `npm` (používá je CLI nástroj `agent-canvas`).
- `uv`, správce balíčků Pythonu, který Agent Canvas používá ke správě prostředí
  serveru agenta. Pokud jej váš systém ještě nemá, nainstalujte jej podle
  [návodu k instalaci uv](https://docs.astral.sh/uv/getting-started/installation/)
  před spuštěním Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop pro Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  nainstalovaný a spuštěný. Na Windows běží stack Agent Canvas z publikovaného
  Docker obrazu, který obsahuje Node.js, `uv` a balíček `@openhands/agent-canvas`,
  takže tyto komponenty na hostitelský systém instalovat nemusíte.
<!-- @os:end -->

- Složku projektu, se kterou má agent pracovat. Může to být jakýkoli místní git repozitář
  nebo adresář s kódem, na kterém chcete, aby agent pracoval.

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

## 1. Spusťte Lemonade Server

Spusťte model z CLI nástroje Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Vyberte model, který odpovídá vašemu hardwaru.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je silný model pro programování, ale vyžaduje velký paměťový fond. Pokud má vaše zařízení omezenou paměť nebo VRAM GPU, zvolte místo toho menší GGUF model z knihovny modelů Lemonade a toto ID modelu používejte v celém playbooku.

> **Poznámka:** První spuštění `lemonade run` stáhne model, pokud ještě není přítomen, což může chvíli trvat v závislosti na velikosti modelu a vašem připojení.

Lemonade zpřístupňuje API kompatibilní s OpenAI na adrese:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Ověřte lokální model

Ověřte, že Lemonade dokáže poskytovat vybraný model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Poté odešlete malý chatový požadavek:

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

Pokud se vrátí pole `choices`, je Lemonade připraven pro Agent Canvas.

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
## 3. Instalace a spuštění Agent Canvas

<!-- @os:linux -->
Nainstalujte publikovaný balíček Agent Canvas globálně:

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

Poté spusťte celý stack z terminálu:

```bash
agent-canvas
```

Ve výchozím nastavení se Agent Canvas spouští na adrese `http://localhost:8000`. Otevřete tuto adresu URL ve
svém prohlížeči. Port není nijak zvláštní — pokud je 8000 již používán, zadejte při spuštění Agent Canvas
libovolný volný port pomocí `--port` (nebo `-p`):

```bash
agent-canvas --port 3000
```

Poté místo toho otevřete `http://localhost:3000`. Výchozí místní backend by se měl na domovské obrazovce zobrazovat
jako funkční (healthy).

Příkaz `agent-canvas` spouští agent server, automatizační backend a
webové rozhraní dohromady. K lokálnímu spuštění OpenHands potřebujete pouze tento jeden
příkaz.

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
Na Windows spusťte publikovaný image kontejneru Agent Canvas pomocí Docker Desktop.
Tento image obsahuje Agent Server, automatizační backend a webové rozhraní, takže
nemusíte na hostitelský systém instalovat Node.js, `uv` ani CLI.

Nejprve vytvořte složky pro konfiguraci a pracovní prostor, které kontejner připojuje:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Stáhněte publikovaný image (je veřejný, takže přihlášení není vyžadováno):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Poté spusťte stack:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Otevřete `http://localhost:8000/canvas` ve svém prohlížeči. Pokud je port 8000 již
používán, namapujte jiný hostitelský port, například `-p 8080:8000`, a místo toho otevřete
`http://localhost:8080/canvas`.

> **Poznámka:** Při prvním spuštění se Agent Server uvnitř kontejneru inicializuje,
> takže může trvat minutu nebo dvě, než backend nahlásí funkční stav (healthy).

Připojení `.openhands` uchovává váš profil LLM a nastavení i po restartu
kontejneru. Zbytek tohoto průvodce konfiguruje vše prostřednictvím rozhraní
Agent Canvas ve vašem prohlížeči.

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

## 4. Konfigurace lokálního LLM

Při prvním spuštění otevře Agent Canvas úvodní (onboarding) průvodce. V tomto průvodci:

1. Ponechte vybraného agenta **OpenHands** a klikněte na **Next**.
2. Na obrazovce **Set up your LLM** vyberte **Advanced**.
3. Ponechte **Authentication** nastavené na **API key**.
4. Nastavte **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavte **Base URL** na `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Na Windows běží stack v kontejneru, který se nemůže připojit k hostiteli na adrese
   > `127.0.0.1`. Použijte místo toho `http://host.docker.internal:13305/api/v1`, aby se
   > kontejnerizovaný agent mohl připojit k Lemonade běžícímu na hostitelském systému Windows.
   <!-- @os:end -->
6. Do pole **API Key** zadejte libovolný neprázdný zástupný text, například `lemonade-local`.
   Lemonade nevyžaduje skutečný klíč, ale klient OpenHands potřebuje nějakou hodnotu
   odeslat.
7. Klikněte na **Next**.

Dokončené pokročilé nastavení by mělo vypadat takto. Pole API key je
v rozhraní maskováno.

![Pokročilá nastavení LLM v Agent Canvas při prvním použití s modelem Lemonade a místní základní adresou URL](assets/01-llm-advanced-settings.png)

Agent Canvas uloží tyto hodnoty jako profil LLM. Pokud vás vaše verze požádá o
pojmenování tohoto profilu, použijte název bez mezer, například `lemonade-local`. Pokud
později změníte modely, otevřete **Settings > LLM** a aktualizujte stejná pokročilá pole. Mezi
uloženými profily můžete přepínat z pole chatu pomocí příkazu `/model`.

## 5. Otevření pracovního prostoru

Agent může číst a upravovat soubory pouze uvnitř pracovního prostoru, který zvolíte. Než
začnete s úkolem, nasměrujte Agent Canvas na vaši složku projektu:

1. Na domovské obrazovce vyberte **Open Workspace**.
2. Vyberte složku, která obsahuje váš projekt (například git repozitář,
   na kterém má agent pracovat).
3. Spusťte novou konverzaci v tomto pracovním prostoru.

Vše, co agent dělá — čtení souborů, spouštění příkazů, úprava kódu — je
omezeno na tento pracovní prostor.

![Domovská obrazovka Agent Canvas po dokončení onboardingu](assets/02-agent-canvas-home.png)

## 6. Spuštění prvního programátorského úkolu

S otevřeným pracovním prostorem a vybraným lokálním LLM zadejte do chatu
konkrétní úkol. Dobrým prvním úkolem je něco malého a ověřitelného, například:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Sledujte časovou osu konverzace. OpenHands:

- Přečte pracovní prostor, aby pochopil jeho strukturu.
- Vytvoří soubor `hello.py` s požadovanou funkcí a testovacím blokem.
- Volitelně spustí `python3 hello.py`, aby ověřil výstup.
- Nahlásí v chatu, co udělal, a případný výstup příkazu.

Měli byste vidět, jak se v pracovním prostoru objeví nový soubor, a závěrečná
zpráva agenta by měla popisovat provedenou změnu. Toto je klíčový okamžik: agent
napsal a spustil skutečný kód ve vaší projektové složce.

## 7. Kontrola a usměrňování agenta

Po dokončení kroku agentem zkontrolujte jeho práci, než přijmete další krok:

- **Změny souborů**: pomocí prohlížeče souborů pracovního prostoru nebo zobrazení rozdílů (diff view) agenta
  zjistíte přesně, co bylo přidáno, změněno nebo odstraněno.
- **Výstup příkazu**: rozbalte libovolný příkaz, který agent spustil, abyste viděli stdout, stderr
  a návratový kód (exit code).
- **Následné kroky**: pokud výsledek není takový, jaký jste chtěli, odpovězte ve stejné
  konverzaci s opravou. Agent si uchovává předchozí kontext a
  dále pracuje na stejných souborech.

Pokud například test nevypsal očekávaný pozdrav, odpovězte:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent soubor znovu přečte, spustí příkaz, diagnostikuje problém a soubor
znovu upraví — vše ve stejné konverzaci.
## Odstraňování problémů

<!-- @os:linux -->
- **`agent-canvas` není v PATH:** přeinstalujte pomocí
  `npm install -g @openhands/agent-canvas` a před spuštěním `agent-canvas`
  z nového terminálu ověřte, že je adresář globálních binárních souborů npm
  zahrnut v proměnné PATH.
- **`npm install -g` selže s chybou oprávnění:** nastavte globální adresář npm
  vlastněný uživatelem, znovu otevřete terminál a Agent Canvas nainstalujte znovu.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` chybí:** nainstalujte jej podle
  [průvodce instalací uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas používá `uv` ke správě Python prostředí serveru agenta.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` nebo `docker run` se nemůže připojit:** ujistěte se, že je
  spuštěn Docker Desktop (jeho ikona velryby se nachází v systémovém panelu)
  a že engine dokončil spouštění. Příkaz `docker version` by měl vypsat jak
  sekci Client, tak sekci Server.
- **Kontejner se spustí, ale backend nikdy není v pořádku:** první spuštění
  inicializuje Agent Server uvnitř kontejneru; dejte mu minutu až dvě a poté
  zkontrolujte chyby pomocí `docker logs <container>`.
- **Kontejner se nemůže připojit k Lemonade:** kontejner se dostane k hostiteli
  přes `host.docker.internal`. Ověřte, že Lemonade běží na hostitelském systému
  Windows pomocí `lemonade status`, a při konfiguraci LLM použijte jako
  základní URL `http://host.docker.internal:13305/api/v1`.
<!-- @os:end -->

- **Uživatelské rozhraní se načte, ale backend se zobrazuje jako nefunkční:**
  počkejte minutu až dvě, než server agenta dokončí spouštění, a poté obnovte
  stránku. Pokud zůstává nefunkční, restartujte stack a zkontrolujte chyby
  v protokolech.
- **Požadavky na chat Lemonade selhávají s chybou připojení:** ověřte, že
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` proběhne úspěšně a že
  Lemonade stále poskytuje model podle `lemonade status`.
- **Agent hlásí chybu s délkou kontextu nebo limitem tokenů:** zahajte novou
  konverzaci, aby agent nenesl předimenzovanou historii. Pokud se to opakuje,
  restartujte Lemonade s vyšší hodnotou `ctx_size` než výchozích 65536
  (například `ctx_size=131072`), pokud to dovolí paměť.
- **Agent produkuje nekvalitní nebo neúplné úpravy:** přepněte na větší model
  v Lemonade, nebo zadejte agentovi menší, konkrétnější úkol a nechte jej
  dokončit, než požádáte o další změnu.

## Další kroky

- Vyzkoušejte větší úkol ve stejném pracovním prostoru, například přidání
  souboru s jednotkovými testy nebo opravu známé chyby, a před ponecháním
  změny si projděte diff agenta.
- Připojte MCP server, jako je GitHub nebo Slack, v sekci **Customize**,
  aby agent mohl číst issues nebo publikovat aktualizace během práce.
- Uložte si několik profilů LLM (rychlý malý model a výkonnější velký model)
  a přepínejte mezi nimi pomocí `/model` uprostřed konverzace.
- Pokračujte na [automatizace OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
  a proměňte opakující se vývojové smyčky v plánované nebo událostmi
  spouštěné běhy agenta.

## Zdroje

- [Dokumentace OpenHands](https://docs.openhands.dev/)
- [Přehled Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Nastavení Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profily LLM a konfigurace modelu](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentace Lemonade Server](https://lemonade-server.ai/docs)

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