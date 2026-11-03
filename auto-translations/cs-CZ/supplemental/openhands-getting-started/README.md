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
který umí psát kód, spouštět příkazy, procházet web a upravovat soubory v reálném
pracovním prostoru. Místo kopírování návrhů z chatovacího okna nasměrujete
agenta na složku projektu a necháte ho odvést práci: implementovat funkci, opravit
chybu, napsat testy nebo vysvětlit kódovou základnu.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je doporučené
uživatelské rozhraní prohlížeče pro spuštění OpenHands. Jediný příkaz `agent-canvas`
spustí server agenta, backend automatizace a webový frontend společně, takže můžete
vést konverzaci s agentem přímo z prohlížeče.

Aby vše zůstalo na vašem systému AMD, agent komunikuje s lokálním modelem obsluhovaným
Lemonade Server. Lemonade zpřístupňuje tento model prostřednictvím API kompatibilního
s OpenAI, takže Agent Canvas ho může nakonfigurovat jako jakýkoli jiný koncový bod ve
stylu OpenAI, zatímco model, váš kód i kontext konverzace zůstávají na vašem
počítači.

V této příručce spustíte lokální model, spustíte Agent Canvas, nasměrujete ho
na tento model a spustíte svůj první programátorský úkol na skutečné složce projektu.

## Co se naučíte

- Jak spustit Lemonade Server a ověřit, že lokální model odpovídá na chatové požadavky
- Jak nainstalovat a spustit Agent Canvas z npm balíčku
- Jak nakonfigurovat Agent Canvas tak, aby jako LLM používal lokální model Lemonade
- Jak zahájit konverzaci OpenHands a sledovat, jak agent upravuje soubory a spouští
  příkazy v pracovním prostoru
- Jak zkontrolovat, co agent změnil, a usměrnit ho pomocí navazujících zpráv

## Základní pojmy

| Pojem | Co to je | Kam zapadá do této příručky |
| --- | --- | --- |
| Lemonade Server | Lokální platforma pro obsluhu LLM postavená pro hardware AMD, která zpřístupňuje API kompatibilní s OpenAI. Vaše data nikdy neopustí váš počítač. | Spouští model, který pohání agenta. |
| OpenHands | AI softwarový agent, který čte a upravuje soubory, spouští shellové příkazy a prochází web uvnitř pracovního prostoru. | Agent, kterého řídíte z chatu. |
| Agent Canvas | Uživatelské rozhraní prohlížeče a backend, které spouští konverzace OpenHands a zobrazuje volání nástrojů a změny souborů. | Spouští celý stack a hostuje vaši konverzaci. |
| Workspace | Složka projektu, kterou má agent povoleno číst a upravovat. | Cíl úprav a příkazů agenta. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Workflow s programátorským agentem těží z většího modelu a většího kontextového okna. Použijte
> alespoň 32 GB systémové paměti, a pro větší GGUF modely raději 64 GB nebo více.
<!-- @device:end -->

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Požadavky


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Budete potřebovat:

- Nainstalovaný Lemonade Server schopný obsluhovat níže uvedený model.

<!-- @os:linux -->
- Node.js 22.12 nebo novější a `npm` (používané CLI nástrojem `agent-canvas`).
- `uv`, správce balíčků Python, který Agent Canvas používá ke správě prostředí
  serveru agenta. Pokud ho na svém systému ještě nemáte, nainstalujte ho podle
  [průvodce instalací uv](https://docs.astral.sh/uv/getting-started/installation/)
  před spuštěním Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop pro Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  nainstalovaný a spuštěný. Ve Windows běží stack Agent Canvas z publikovaného
  Docker image, který obsahuje Node.js, `uv` a balíček
  `@openhands/agent-canvas`, takže je není nutné instalovat na hostitelský systém.
<!-- @os:end -->

- Složka projektu, ve které se bude pracovat. Může to být libovolný lokální git repozitář
  nebo adresář s kódem, na kterém má agent pracovat.

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

Spusťte model z Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Zvolte model, který odpovídá vašemu hardwaru.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je silný model pro programování, ale potřebuje velký paměťový prostor. Pokud má vaše zařízení omezenou paměť nebo VRAM GPU, zvolte místo něj menší GGUF model z knihovny modelů Lemonade a v celé této příručce používejte ID tohoto modelu.

> **Poznámka:** První spuštění `lemonade run` model stáhne, pokud ještě není přítomen, což může chvíli trvat v závislosti na velikosti modelu a vašem připojení.

Lemonade zpřístupňuje API kompatibilní s OpenAI na adrese:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Ověřte lokální model

Ověřte, že Lemonade dokáže obsluhovat vybraný model:

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

Pokud tento požadavek vrátí pole `choices`, Lemonade je připraven pro Agent Canvas.

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

Poté z terminálu spusťte celý zásobník:

```bash
agent-canvas
```

Ve výchozím nastavení se Agent Canvas spouští na `http://localhost:8000`. Otevřete tuto adresu URL
ve svém prohlížeči. Na portu nezáleží — pokud je port 8000 již používán, při spuštění Agent Canvas
zadejte libovolný volný port pomocí `--port` (nebo `-p`):

```bash
agent-canvas --port 3000
```

Poté otevřete `http://localhost:3000` místo toho. Výchozí lokální backend by se měl na domovské obrazovce
zobrazovat jako zdravý.

Příkaz `agent-canvas` spouští agent server, automatizační backend a
webový frontend společně. Ke spuštění OpenHands lokálně potřebujete pouze
tento jediný příkaz.

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
Na Windows spusťte publikovaný obrazový kontejner Agent Canvas pomocí Docker Desktop.
Tento obraz obsahuje Agent Server, automatizační backend a webový frontend, takže
na hostitele není třeba instalovat Node.js, `uv` ani CLI.

Nejprve vytvořte složky pro konfiguraci a pracovní prostor, které kontejner připojí:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Stáhněte publikovaný obraz (je veřejný, takže není nutné přihlášení):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Poté spusťte zásobník:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Otevřete `http://localhost:8000/canvas` ve svém prohlížeči. Pokud je port 8000 již
používán, namapujte jiný port hostitele, například `-p 8080:8000`, a místo toho otevřete
`http://localhost:8080/canvas`.

> **Poznámka:** První spuštění inicializuje Agent Server uvnitř kontejneru,
> takže může trvat minutu nebo dvě, než backend nahlásí, že je zdravý.

Připojení `.openhands` zachovává váš profil LLM a nastavení napříč restarty
kontejneru. Zbytek této příručky konfiguruje vše prostřednictvím uživatelského rozhraní Agent
Canvas ve vašem prohlížeči.

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

Při prvním spuštění Agent Canvas otevře úvodní proces (onboarding). V tomto procesu:

1. Ponechte **OpenHands** vybrané jako agenta a klikněte na **Next**.
2. V části **Set up your LLM** vyberte **Advanced**.
3. Ponechte **Authentication** nastavené na **API key**.
4. Nastavte **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavte **Base URL** na `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Na Windows běží zásobník v kontejneru, který se nemůže dostat k hostiteli na
   > `127.0.0.1`. Místo toho použijte `http://host.docker.internal:13305/api/v1`, aby se
   > kontejnerizovaný agent mohl dostat k Lemonade běžícímu na hostiteli Windows.
   <!-- @os:end -->
6. Do pole **API Key** zadejte jakýkoli neprázdný zástupný text, například `lemonade-local`.
   Lemonade nevyžaduje skutečný klíč, ale klient OpenHands potřebuje nějakou hodnotu
   k odeslání.
7. Klikněte na **Next**.

Dokončené pokročilé nastavení (Advanced settings) by mělo vypadat takto. Pole API klíče je
v uživatelském rozhraní maskováno.

![Pokročilé nastavení LLM při prvním použití Agent Canvas s modelem Lemonade a lokální základní adresou URL](assets/01-llm-advanced-settings.png)

Agent Canvas uloží tyto hodnoty jako profil LLM. Pokud vás vaše verze požádá o pojmenování
tohoto profilu, použijte název bez mezer, například `lemonade-local`. Pokud později
změníte modely, otevřete **Settings > LLM** a aktualizujte stejná pokročilá pole. Mezi
uloženými profily můžete přepínat z chatovacího vstupu pomocí příkazu `/model`.

## 5. Otevření pracovního prostoru

Agent může číst a upravovat pouze soubory uvnitř pracovního prostoru, který zvolíte. Než
zahájíte úkol, namiřte Agent Canvas na složku svého projektu:

1. Na domovské obrazovce zvolte **Open Workspace**.
2. Vyberte složku, která obsahuje váš projekt (například git repozitář,
   na kterém má agent pracovat).
3. Zahajte novou konverzaci v tomto pracovním prostoru.

Vše, co agent dělá — čtení souborů, spouštění příkazů, úprava kódu — je
omezeno na tento pracovní prostor.

![Domovská obrazovka Agent Canvas po dokončení onboardingu](assets/02-agent-canvas-home.png)

## 6. Spuštění vašeho prvního programátorského úkolu

S otevřeným pracovním prostorem a vybraným lokálním LLM zadejte do
chatu konkrétní úkol. Dobrým prvním úkolem je něco malého a ověřitelného, například:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Sledujte časovou osu konverzace. OpenHands provede následující:

- Přečte pracovní prostor, aby pochopil jeho rozvržení.
- Vytvoří `hello.py` s požadovanou funkcí a testovacím blokem.
- Volitelně spustí `python3 hello.py`, aby ověřil výstup.
- V chatu nahlásí, co udělal, a případný výstup příkazů.

Měli byste vidět, jak se v pracovním prostoru objeví nový soubor, a závěrečná zpráva agenta
by měla popisovat provedenou změnu. Toto je klíčový okamžik: agent
napsal a spustil skutečný kód ve vaší projektové složce.

## 7. Kontrola a usměrňování agenta

Poté, co agent dokončí krok, zkontrolujte jeho práci, než přijmete další krok:

- **Změny souborů**: pomocí prohlížeče souborů pracovního prostoru nebo zobrazení rozdílů (diff view)
  agenta si prohlédněte přesně, co bylo přidáno, změněno nebo odstraněno.
- **Výstup příkazů**: rozbalte libovolný příkaz, který agent spustil, abyste viděli stdout, stderr
  a návratový kód (exit code).
- **Následné kroky**: pokud výsledek není takový, jaký jste chtěli, odpovězte ve stejné
  konverzaci opravou. Agent si uchovává předchozí kontext a
  iteruje na stejných souborech.

Pokud například test nevytiskl očekávaný pozdrav, odpovězte:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent soubor znovu přečte, spustí příkaz, diagnostikuje problém a soubor
znovu upraví — vše ve stejné konverzaci.
## Řešení problémů

<!-- @os:linux -->
- **`agent-canvas` není v PATH:** proveďte novou instalaci pomocí
  `npm install -g @openhands/agent-canvas` a před spuštěním `agent-canvas` z nového
  terminálu ověřte, že je globální binární adresář npm zahrnut v proměnné PATH.
- **`npm install -g` selže s chybou oprávnění:** nakonfigurujte globální adresář npm
  vlastněný uživatelem, poté znovu otevřete terminál a Agent Canvas nainstalujte znovu.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **Chybí `uv`:** nainstalujte jej podle
  [průvodce instalací uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas používá `uv` ke správě prostředí Python pro agent server.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` nebo `docker run` se nemůže připojit:** ujistěte se, že Docker Desktop
  běží (jeho ikona velryby je v systémové liště) a že engine dokončil spouštění.
  `docker version` by měl vypsat sekci Client i Server.
- **Kontejner se spustí, ale backend nikdy nedosáhne stavu healthy:** první
  spuštění inicializuje Agent Server uvnitř kontejneru; dejte mu minutu nebo
  dvě a poté zkontrolujte `docker logs <container>`, zda neobsahuje chyby.
- **Kontejner se nemůže připojit k Lemonade:** kontejner se k hostiteli připojuje přes
  `host.docker.internal`. Ověřte, že Lemonade poskytuje služby na hostitelském systému Windows pomocí
  `lemonade status`, a jako Base URL při konfiguraci LLM použijte
  `http://host.docker.internal:13305/api/v1`.
<!-- @os:end -->

- **UI se načte, ale backend zobrazuje stav unhealthy:** počkejte minutu nebo dvě, než
  agent server dokončí spouštění, a poté obnovte stránku. Pokud stav unhealthy přetrvává, restartujte
  celý stack a zkontrolujte logy, zda neobsahují chyby.
- **Požadavky na chat Lemonade selhávají s chybou připojení:** ověřte, že
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` proběhne úspěšně a že
  Lemonade stále poskytuje model podle `lemonade status`.
- **Agent hlásí chybu s délkou kontextu nebo limitem tokenů:** začněte
  novou konverzaci, aby agent nenesl s sebou příliš velkou historii. Pokud se to
  stále opakuje, restartujte Lemonade s větší hodnotou `ctx_size`, než je výchozích
  65536 (například `ctx_size=131072`), pokud to paměť dovolí.
- **Agent vytváří nekvalitní nebo neúplné úpravy:** přepněte na větší
  model v Lemonade, nebo zadejte agentovi menší, konkrétnější úkol a nechte jej
  dokončit, než požádáte o další změnu.

## Další kroky

- Vyzkoušejte větší úkol ve stejném pracovním prostoru, například přidání souboru s jednotkovými testy nebo
  opravu známé chyby, a před ponecháním změny zkontrolujte diff od agenta.
- Připojte MCP server, jako je GitHub nebo Slack, v sekci **Customize**, aby
  agent mohl číst issues nebo publikovat aktualizace během práce.
- Uložte si několik LLM profilů (rychlý malý model a výkonnější velký model) a
  přepínejte mezi nimi pomocí `/model` uprostřed konverzace.
- Pokračujte na [automatizace OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) a
  proměňte opakující se vývojářské smyčky v naplánované nebo událostmi spouštěné spouštění agenta.

## Zdroje

- [Dokumentace OpenHands](https://docs.openhands.dev/)
- [Přehled Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Nastavení Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM profily a konfigurace modelu](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
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