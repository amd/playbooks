<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Przegląd

Deweloperzy poświęcają wiele czasu na drobne, powtarzające się czynności: przeglądanie oznaczonych etykietami pull requestów, odpowiadanie na komentarze w GitHub, segregowanie nowych zgłoszeń, przekształcanie wątków Slack w notatki ze standupów lub podsumowania incydentów oraz śledzenie sygnałów dotyczących wydań czy badań.
Każda z tych czynności jest znajoma, ale nadal wymaga oceny sytuacji: zebrania odpowiedniego kontekstu, zdecydowania, co jest istotne, i opublikowania czytelnej aktualizacji tam, gdzie zespół już pracuje.

[Automatyzacje OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) zamieniają te czynności w zaplanowane lub wyzwalane zdarzeniami konwersacje agenta: uruchomienia, w których agent AI może odczytywać kontekst, wywoływać narzędzia i generować aktualizację.
Współdzielone szablony automatyzacji w katalogu rozszerzeń OpenHands stosują ten wzorzec w przypadku przeglądu pull requestów w GitHub, monitorowania repozytoriów, segregowania zgłoszeń w Linear, podsumowań incydentów, cyfrowych raportów ze standupów na Slacku oraz briefów badawczych: automatyzacja „budzi się”, wykorzystuje skonfigurowane integracje, takie jak GitHub czy Slack, aby pobrać kontekst, analizuje ten kontekst za pomocą dużego modelu językowego (LLM) i zapisuje wynik.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) to lokalna płaszczyzna sterowania do tworzenia i testowania tych automatyzacji.
W tym przewodniku uruchamia on OpenHands Agent Server, czyli proces zaplecza wykonujący konwersacje agenta, i łączy agenta z usługami zewnętrznymi, takimi jak GitHub i Slack.

Aby cały przepływ pracy pozostał w obrębie Twojego systemu AMD, agent komunikuje się z lokalnym modelem udostępnianym przez Lemonade Server.
Lemonade udostępnia ten model poprzez interfejs API zgodny z OpenAI, dzięki czemu Agent Canvas może skonfigurować go jak zdalny punkt końcowy w stylu OpenAI, podczas gdy model, polecenie oraz kontekst przepływu pracy pozostają lokalne.

W tym przewodniku zbudujesz jedną konkretną automatyzację: zaplanowany cyfrowy raport rozwojowy z GitHub na Slack.
Wykorzystuje on GitHub do sprawdzania ostatniej aktywności repozytorium, Slack do publikowania raportu, wywołania API Agent Canvas do konfigurowania i testowania automatyzacji oraz Lemonade do lokalnego uruchamiania modelu LLM.

![Diagram architektury przedstawiający GitHub MCP, automatyzację OpenHands, Lemonade Server oraz Slack MCP](assets/00-architecture-overview.png)

## Czego się nauczysz

- Jak uruchomić Lemonade Server i zweryfikować, czy lokalny model odpowiada na żądania czatu
- Jak uruchomić Agent Canvas i skierować jego Agent Server do lokalnego LLM
- Jak zainstalować serwery GitHub i Slack Model Context Protocol (MCP) za pomocą API Agent Server
- Jak utworzyć i uruchomić zaplanowaną automatyzację OpenHands, która publikuje raport rozwojowy na Slacku
- Jak rozwiązywać najczęstsze problemy związane z lokalnym modelem i automatyzacją

## Podstawowe pojęcia

| Pojęcie | Czym jest | Gdzie pasuje w tym przewodniku |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma do udostępniania modeli LLM zbudowana z myślą o sprzęcie AMD, udostępniająca interfejs API zgodny z OpenAI. Twoje dane nigdy nie opuszczają Twojego komputera. | Uruchamia model, który zasila agenta. |
| OpenHands Agent Server | Proces zaplecza wykonujący konwersacje agenta OpenHands. | Hostuje agenta, jego profil LLM oraz jego serwery MCP. |
| Agent Canvas | Lokalna płaszczyzna sterowania dla OpenHands, która uruchamia Agent Server oraz interfejs użytkownika do analizowania uruchomień agenta. | Uruchamia backendy i udostępnia API, które wywołujesz. |
| Serwer MCP | Serwer Model Context Protocol, który udostępnia agentowi narzędzia dla usługi zewnętrznej, takiej jak GitHub czy Slack. | Umożliwia agentowi odczyt z GitHub i zapis na Slacku. |
| Automatyzacja OpenHands | Zaplanowana lub wyzwalana zdarzeniami konwersacja agenta, która pobiera kontekst, analizuje go i zapisuje wynik w określonym miejscu. | Raport z GitHub na Slack, który tworzysz w tym przewodniku. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Przepływy pracy agentów kodujących korzystają na większym modelu i oknie kontekstu.
> Użyj co najmniej 32 GB pamięci systemowej, a w przypadku większych modeli GGUF preferuj 64 GB lub więcej.
<!-- @device:end -->

## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Wymagania wstępne

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

Potrzebujesz:

- Lemonade Server zainstalowanego zgodnie ze standardowym [przewodnikiem instalacji Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 lub nowszego oraz `npm`, używanych do instalacji opublikowanego CLI Agent Canvas i uruchamiania serwerów MCP za pomocą `npx`.
- `uv`, menedżera pakietów Pythona, którego Agent Canvas używa do zbudowania środowiska Agent Server. Jeśli nie jest jeszcze zainstalowany, zainstaluj go z [przewodnika instalacji uv](https://docs.astral.sh/uv/getting-started/installation/).
- Niedawno opublikowanego pakietu `@openhands/agent-canvas` ze sterowanymi schematem ustawieniami agenta, `LLMSummarizingCondenserSettings.max_tokens` oraz obsługą `custom_tokenizer` dla LLM.
- Pakietu Pythona `transformers` dostępnego w środowisku Agent Server. Jest on wymagany do liczenia tokenów szablonu czatu, gdy ustawiony jest `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop dla systemu Windows](https://docs.docker.com/desktop/setup/install/windows-install/), zainstalowanego i uruchomionego. W systemie Windows stos Agent Canvas działa na podstawie opublikowanego obrazu Docker, który zawiera Node.js, `uv`, `transformers` oraz pakiet `@openhands/agent-canvas`, dzięki czemu nie musisz instalować ich na hoście.
<!-- @os:end -->

- Tokenu GitHub z dostępem do odczytu repozytorium, które ma zostać podsumowane.
- Tokenu bota Slack (`xoxb-...`) z dostępem `chat:write` oraz odczytem kanału.
- Identyfikatora zespołu Slack (`T...`).
- Identyfikatora kanału Slack (`C...`), na którym ma zostać opublikowany raport.

Zanim przetestujesz automatyzację, zaproś aplikację Slack do docelowego kanału.
## Zmienne używane w tym playbooku

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

Te dwie zmienne są używane przez poniższe polecenia weryfikacyjne.
Model, tokenizer i inne ustawienia LLM są wprowadzane bezpośrednio w interfejsie Agent Canvas UI w kolejnych krokach, dlatego ich dosłowne wartości są pokazane bezpośrednio w tekście tam, gdzie są potrzebne.

Poniższe wartości są wprowadzane do interfejsu Agent Canvas UI w kolejnych krokach.
Ustaw je tutaj, aby móc je później skopiować:

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

Użyj jawnej wartości `owner/repo` dla `GITHUB_REPO_FILTER`.
Szerokie symbole wieloznaczne dla organizacji mogą zwrócić zbyt dużo kontekstu MCP dla modeli lokalnych.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Uruchom Lemonade Server

Uruchom model z poziomu Lemonade CLI:

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

> **Wybierz model dopasowany do swojego sprzętu.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) jest mocnym modelem dla tego przepływu pracy, ale wymaga dużej puli pamięci.
> Jeśli Twoje urządzenie ma ograniczoną pamięć lub VRAM GPU, wybierz mniejszy model GGUF z biblioteki modeli Lemonade i używaj tego identyfikatora modelu (oraz pasującego mu tokenizera) w całym tym playbooku.

> **Uwaga:** Pierwsze uruchomienie `lemonade run` pobiera model, jeśli nie jest jeszcze obecny, co może chwilę potrwać w zależności od rozmiaru modelu i Twojego połączenia.

Lemonade udostępnia kompatybilne z OpenAI API pod adresem:

```text
http://127.0.0.1:13305/api/v1
```

Opcjonalnie: jeśli Agent Canvas lub runner automatyzacji nie znajdują się na tej samej maszynie, udostępnij punkt końcowy Lemonade przez bezpieczny tunel i użyj adresu URL HTTPS jako podstawowego URL-a LLM.
[ngrok](https://ngrok.com/) udostępnia lokalny port w internecie przez bezpieczny adres URL HTTPS; wymaga darmowego konta ngrok, a `YOUR_NGROK_DOMAIN.ngrok-free.dev` należy zastąpić własną zarezerwowaną domeną:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Zweryfikuj model lokalny

Potwierdź, że Lemonade może obsłużyć wybrany model:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Następnie wyślij małe żądanie czatu:

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

Następnie wyślij małe żądanie czatu:

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

Jeśli to zwraca tablicę `choices`, Lemonade jest gotowy dla Agent Canvas.

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

## 3. Uruchom Agent Canvas

<!-- @os:linux -->
Zainstaluj opublikowany pakiet Agent Canvas i uruchom cały stos:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Jeśli globalna instalacja npm zakończy się błędem uprawnień, zapoznaj się z poniższym wpisem dotyczącym rozwiązywania problemów z uprawnieniami npm.

Domyślnie Agent Canvas uruchamia się pod adresem `http://localhost:8000`.
Otwórz ten adres URL w przeglądarce.
Port nie jest niczym szczególnym — jeśli 8000 jest już zajęty, podaj dowolny wolny port za pomocą `--port` (lub `-p`).
Domyślny lokalny backend powinien na ekranie głównym być oznaczony jako działający poprawnie (healthy).

> **Uwaga:** Pierwsze uruchomienie buduje zarządzane przez `uv` środowisko Python dla Agent Server, więc może minąć kilka minut, zanim backend zgłosi stan „healthy”.

Polecenie `agent-canvas` uruchamia razem serwer agenta, backend automatyzacji oraz frontend webowy.
Potrzebujesz tylko tego jednego polecenia, aby uruchomić OpenHands lokalnie.
Reszta tego playbooka konfiguruje wszystko za pośrednictwem interfejsu Agent Canvas UI w przeglądarce.
<!-- @os:end -->

<!-- @os:windows -->
W systemie Windows uruchom opublikowany obraz kontenera Agent Canvas za pomocą Docker Desktop.
Obraz zawiera Agent Server, backend automatyzacji oraz frontend webowy, więc nie musisz instalować Node.js, `uv` ani CLI na hoście.

Najpierw utwórz foldery konfiguracji i workspace, które kontener montuje:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Pobierz opublikowany obraz (około 6 GB; jest publiczny, więc logowanie nie jest wymagane):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Następnie uruchom stos:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Otwórz `http://localhost:8000/canvas` w przeglądarce.
Jeśli port 8000 jest już zajęty, zmapuj inny port hosta, na przykład `-p 8080:8000`, i zamiast tego otwórz `http://localhost:8080/canvas`.

> **Uwaga:** Pierwsze uruchomienie buduje środowisko Agent Server wewnątrz kontenera, więc może minąć kilka minut, zanim backend zgłosi stan „healthy”.

Montowanie `.openhands` zachowuje Twój profil LLM, serwery MCP i automatyzacje pomiędzy ponownymi uruchomieniami kontenera.
Reszta tego playbooka konfiguruje wszystko za pośrednictwem interfejsu Agent Canvas UI w przeglądarce pod adresem `http://localhost:8000/canvas`.
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
## 4. Konfigurowanie lokalnego LLM w interfejsie użytkownika

Po pierwszym uruchomieniu Agent Canvas otwiera proces wdrożeniowy.
W tym procesie:

1. Pozostaw **OpenHands** wybrany jako agent i kliknij **Next**.
2. W sekcji **Set up your LLM** wybierz **Advanced**.
3. Pozostaw **Authentication** ustawione na **API key**.
4. Ustaw **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Ustaw **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. W polu **API Key** wpisz dowolny niepusty symbol zastępczy, na przykład `lemonade-local`. Lemonade nie wymaga rzeczywistego klucza, ale klient OpenHands musi otrzymać jakąś wartość do wysłania.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server działa wewnątrz kontenera, więc dla **Base URL** ustaw `http://host.docker.internal:13305/api/v1` zamiast `http://127.0.0.1:13305/api/v1`.
> Z poziomu kontenera `127.0.0.1` oznacza sam kontener; `host.docker.internal` pozwala dotrzeć do Lemonade działającego na hoście Windows, a Docker Desktop udostępnia tę nazwę hosta automatycznie.
<!-- @os:end -->

Pola połączenia powinny wyglądać następująco.
Pole klucza API jest maskowane przez interfejs użytkownika.

![Ustawienia zaawansowane LLM przy pierwszym uruchomieniu Agent Canvas z modelem Lemonade i lokalnym adresem URL podstawowym](assets/01-llm-advanced-settings.png)

Następnie wybierz **All** i ustaw dodatkowe pola modelu lokalnego:

1. Przewiń do **Custom Tokenizer** i ustaw na `Qwen/Qwen3.6-35B-A3B`.
2. Przewiń do **LiteLLM Extra Body** i ustaw na `{"enable_thinking": true}`.
3. Kliknij **Next**.

![Karta All ustawień LLM przy pierwszym uruchomieniu Agent Canvas z niestandardowym tokenizerem Qwen](assets/02-llm-all-tokenizer-settings.png)

![Karta All ustawień LLM przy pierwszym uruchomieniu Agent Canvas ze skonfigurowanym dodatkowym ciałem LiteLLM](assets/03-llm-all-extra-body-settings.png)

Ustawienia LLM powinny przedstawiać się następująco:

| Pole | Wartość |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Prefiks `openai/` informuje LiteLLM, aby stosować formatowanie żądań zgodne z OpenAI w komunikacji z punktem końcowym Lemonade.
Niestandardowy tokenizer to oryginalny tokenizer Hugging Face dla modelu GGUF; umożliwia on OpenHands liczenie tych samych tokenów szablonu czatu, które widzi lokalny serwer modelu.
Obecny formularz LLM pierwszego uruchomienia nie pokazuje ustawień kondensera.
Jeśli Twoja kompilacja Agent Canvas udostępnia później ustawienia kondensera w sekcji **Settings > LLM**, użyj `llm_summarizing` i ustaw maksymalną liczbę tokenów poniżej okna kontekstu Lemonade, na przykład `56000`.

## 5. Instalowanie serwerów MCP GitHub i Slack

W interfejsie użytkownika Agent Canvas otwórz **Customize** (lub **Settings > MCP**), aby dodać serwery MCP, które dają agentowi narzędzia do obsługi GitHub i Slack.
Wartości tokenów są wysyłane wyłącznie do Twojego lokalnego Agent Server i są przechowywane jako zaszyfrowane ustawienia.

<!-- @os:windows -->
> **Windows (Docker):** poniższe polecenia serwera MCP `npx` są uruchamiane wewnątrz kontenera, który już zawiera Node.js, więc na hoście nie jest instalowane nic dodatkowego.
> Ponieważ katalog `.openhands` jest zamontowany, serwery MCP i ich tokeny zachowują się po ponownym uruchomieniu kontenera.
<!-- @os:end -->

### Serwer MCP GitHub

Dodaj nowy serwer MCP z następującymi ustawieniami:

| Pole | Wartość |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = Twój token GitHub |

Użyj tokenu GitHub z dostępem do odczytu repozytorium, które ma być podsumowywane.

### Serwer MCP Slack

Dodaj drugi serwer MCP z następującymi ustawieniami:

| Pole | Wartość |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = identyfikator Twojego kanału podsumowań |

Ustaw `SLACK_CHANNEL_IDS` na identyfikator kanału podsumowań (tę samą wartość co `SLACK_DIGEST_CHANNEL`), aby agent nie musiał przeglądać wszystkich kanałów Slack.

Po dodaniu obu serwerów użyj przycisku **Test** przy każdym z nich, aby potwierdzić, że łączy się i udostępnia narzędzia.
Serwer GitHub powinien wyświetlić listę narzędzi GitHub, a serwer Slack – listę narzędzi Slack.

![Strona MCP Agent Canvas z zainstalowanymi serwerami GitHub i Slack](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Tworzenie automatyzacji podsumowań

W interfejsie użytkownika Agent Canvas otwórz stronę **Automations** i utwórz nową automatyzację:

1. Wybierz **Create automation** i wybierz typ **Prompt preset**.
2. Ustaw **Name** na `GitHub Development Digest to Slack`.
3. Ustaw **Prompt** na następujący tekst, zastępując symbole zastępcze repozytorium i kanału własnymi wartościami:

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

4. Ustaw **Trigger** na **Cron** z harmonogramem `0 9 * * 1-5` (godz. 9:00 w dni robocze) i ustaw **Timezone** na swoją strefę czasową, na przykład `America/New_York`.
5. Ustaw **Timeout** na `900` sekund.
6. Zapisz automatyzację.

Strona szczegółów automatyzacji przedstawia nowo utworzoną automatyzację wraz z jej wyzwalaczem cron i wygenerowanym punktem wejścia prompt-preset.

![Szczegóły automatyzacji Agent Canvas po utworzeniu](assets/05-automation-created.png)
## 7. Przetestuj automatyzację

Na stronie szczegółów automatyzacji w interfejsie Agent Canvas UI:

1. Kliknij **Run now** (lub **Dispatch**), aby natychmiast uruchomić automatyzację jednorazowo.
2. Obserwuj listę uruchomień na tej samej stronie. Najnowsze uruchomienie powinno przejść w stan `COMPLETED`.
3. Otwórz docelowy kanał Slack. Powinien zawierać wygenerowany digest.

Nie musisz czekać na uruchomienie harmonogramu cron — **Run now** wyzwala uruchomienie na żądanie, dzięki czemu możesz potwierdzić, że prompt, połączenia MCP i publikowanie na Slacku działają poprawnie, zanim zaczniesz polegać na harmonogramie.

![Pomyślnie zakończone uruchomienie automatyzacji w Agent Canvas](assets/06-automation-run-completed.png)

![Kanał Slack pokazujący wygenerowany digest OpenHands](assets/07-slackbot-message.png)

## Rozwiązywanie problemów

<!-- @os:windows -->
- **Port 8000 Dockera jest już zajęty:** zmapuj inny port hosta, na przykład `docker run ... -p 8080:8000 ...`, i otwórz `http://localhost:8080/canvas`.
- **`docker pull` kończy się błędem poświadczeń** (na przykład „A specified logon session does not exist”): uruchom pobieranie z interaktywnej sesji Windows lub wcześniej pobierz obraz. Obraz jest publiczny, więc `docker login` nie jest wymagany.
- **Interfejs się ładuje, ale backend jest niesprawny:** pierwsze uruchomienie buduje środowisko Agent Server wewnątrz kontenera. Poczekaj chwilę i odśwież stronę, a następnie sprawdź `docker logs <container>` w poszukiwaniu postępu.
- **Agent Canvas nie może połączyć się z Lemonade z poziomu kontenera:** ustaw **Base URL** modelu LLM na `http://host.docker.internal:13305/api/v1` (nie `127.0.0.1`) i potwierdź, że Lemonade działa na hoście Windows.
<!-- @os:end -->

- **Lemonade nie działa:** uruchom ją ponownie poleceniem `lemonade run "${LEMONADE_MODEL}"` z kroku 1, a następnie ponownie wykonaj test kondycji (health check).
- **`npm install -g` kończy się błędem uprawnień:** w systemie Linux lub WSL skonfiguruj globalny katalog npm należący do użytkownika, dodaj go do pliku startowego powłoki, a następnie zainstaluj Agent Canvas ponownie:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Jeśli używasz `zsh`, dodaj tę samą linię `export PATH=...` do `~/.zshrc` zamiast do `~/.bashrc`.
- **Agent Canvas odrzuca ustawienia LLM po ustawieniu `custom_tokenizer`:** zainstaluj `transformers` w środowisku Python Agent Server, w razie potrzeby uruchom ponownie Agent Canvas i spróbuj ponownie zapisać ustawienia LLM. OpenHands wymaga biblioteki Transformers do wczytania szablonu czatu tokenizera, gdy ustawione jest `custom_tokenizer`.
- **Agent Canvas nie może połączyć się z Lemonade:** zweryfikuj `curl -fsS "${LEMONADE_BASE_URL}/health"` i potwierdź, że adres bazowy wprowadzony w formularzu LLM przy pierwszym użyciu lub w **Settings > LLM** zgadza się z działającym lokalnym punktem końcowym lub tunelem HTTPS.
- **Ustawienia LLM nie zostały zapisane:** upewnij się, że po wprowadzeniu wartości kliknięto **Next**. Ponownie otwórz **Settings > LLM**, aby potwierdzić, że wartości zostały zachowane.
- **GitHub MCP nie widzi prywatnych repozytoriów:** potwierdź, że token GitHub ma dostęp do odczytu docelowego repozytorium oraz że przycisk **Test** MCP w **Customize** zgłasza dostępne narzędzia GitHub.
- **Slack może odczytywać kanały, ale nie może publikować:** zaproś aplikację Slack do docelowego kanału i potwierdź, że bot ma uprawnienie `chat:write`.
- **Automatyzacja wyświetla zbyt wiele kanałów Slack:** użyj identyfikatora kanału Slack i ustaw `SLACK_CHANNEL_IDS` na serwerze Slack MCP w **Customize**.
- **Uruchomienie automatyzacji kończy się niepowodzeniem lub przekracza kontekst:** potwierdź, że Lemonade została uruchomiona z `ctx_size=65536`, potwierdź, że model LLM OpenHands ma ustawione `custom_tokenizer`, oraz użyj jawnie określonego repozytorium z wynikami GitHub ograniczonymi do 3–5 elementów. Jeśli Twoja wersja Agent Canvas udostępnia ustawienia kondensatora (condenser), ustaw maksymalną liczbę tokenów kondensatora poniżej okna kontekstowego Lemonade.

## Kolejne kroki

- Dodaj cotygodniowy digest dotyczący wyłącznie wydań (release-only).
- Dodaj automatyzację wyzwalaną zdarzeniami GitHub w celu szybszych powiadomień o PR lub push.
- Przekieruj ten sam digest do Notion, Linear lub innego narzędzia opartego na MCP.

## Zasoby

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Dokumentacja Lemonade Server](https://lemonade-server.ai/docs)
- [Repozytorium rozszerzeń OpenHands](https://github.com/OpenHands/extensions)
- [Serwery Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Pakiet Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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