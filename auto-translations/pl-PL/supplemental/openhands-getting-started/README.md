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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Omówienie

[OpenHands](https://github.com/All-Hands-AI/OpenHands) to agent programistyczny AI, który potrafi pisać kod, uruchamiać polecenia, przeglądać internet i edytować pliki w rzeczywistym obszarze roboczym. Zamiast kopiować sugestie z okna czatu, wskazujesz agentowi folder projektu i pozwalasz mu wykonać pracę: zaimplementować funkcję, naprawić błąd, napisać testy lub wyjaśnić działanie kodu.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) to zalecany interfejs przeglądarkowy do uruchamiania OpenHands. Pojedyncze polecenie `agent-canvas` uruchamia jednocześnie serwer agenta, backend automatyzacji oraz frontend webowy, dzięki czemu możesz prowadzić rozmowę z agentem z poziomu przeglądarki.

Aby wszystko pozostało na Twoim systemie AMD, agent komunikuje się z lokalnym modelem udostępnianym przez Lemonade Server. Lemonade udostępnia ten model poprzez API kompatybilne z OpenAI, dzięki czemu Agent Canvas może go skonfigurować tak jak każdy inny punkt końcowy w stylu OpenAI, podczas gdy model, Twój kod i kontekst rozmowy pozostają na Twoim komputerze.

W tym przewodniku uruchomisz lokalny model, uruchomisz Agent Canvas, skierujesz go na ten model oraz wykonasz swoje pierwsze zadanie programistyczne na rzeczywistym folderze projektu.

## Czego się nauczysz

- Jak uruchomić Lemonade Server i potwierdzić, że lokalny model odpowiada na zapytania czatu
- Jak zainstalować i uruchomić Agent Canvas z pakietu npm
- Jak skonfigurować Agent Canvas do korzystania z lokalnego modelu Lemonade jako LLM
- Jak rozpocząć rozmowę w OpenHands i obserwować, jak agent edytuje pliki i uruchamia polecenia w obszarze roboczym
- Jak przejrzeć zmiany wprowadzone przez agenta i kierować nim za pomocą kolejnych wiadomości

## Podstawowe pojęcia

| Pojęcie | Czym jest | Gdzie pasuje w tym przewodniku |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma do serwowania LLM zbudowana dla sprzętu AMD, która udostępnia API kompatybilne z OpenAI. Twoje dane nigdy nie opuszczają Twojego komputera. | Uruchamia model, który zasila agenta. |
| OpenHands | Agent programistyczny AI, który odczytuje i edytuje pliki, uruchamia polecenia powłoki oraz przegląda internet wewnątrz obszaru roboczego. | Agent, którym sterujesz z poziomu czatu. |
| Agent Canvas | Interfejs przeglądarkowy i backend, który uruchamia rozmowy OpenHands i pokazuje wywołania narzędzi oraz zmiany w plikach. | Uruchamia cały stos i hostuje Twoją rozmowę. |
| Obszar roboczy | Folder projektu, który agent ma prawo odczytywać i modyfikować. | Cel edycji i poleceń agenta. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Przepływy pracy agenta programistycznego korzystają z większego modelu i okna kontekstu. Użyj co najmniej 32 GB pamięci systemowej, a w przypadku większych modeli GGUF preferuj 64 GB lub więcej.
<!-- @device:end -->

## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Wymagania wstępne


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

Potrzebujesz:

- Zainstalowanego Lemonade Server zdolnego do serwowania poniższego modelu.

<!-- @os:linux -->
- Node.js 22.12 lub nowszego oraz `npm` (używanych przez CLI `agent-canvas`).
- `uv`, menedżera pakietów Pythona, którego Agent Canvas używa do zarządzania środowiskiem serwera agenta. Jeśli Twój system jeszcze go nie posiada, zainstaluj go z [przewodnika instalacji uv](https://docs.astral.sh/uv/getting-started/installation/) przed uruchomieniem Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop dla Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  zainstalowany i uruchomiony. W systemie Windows stos Agent Canvas działa z opublikowanego obrazu Docker, który zawiera Node.js, `uv` oraz pakiet `@openhands/agent-canvas`, więc nie musisz instalować tych elementów na hoście.
<!-- @os:end -->

- Folder projektu, w którym będziesz pracować. Może to być dowolne lokalne repozytorium git lub katalog z kodem, nad którym ma pracować agent.

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

## 1. Uruchom Lemonade Server

Uruchom model z poziomu CLI Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Wybierz model dopasowany do swojego sprzętu.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) to mocny model programistyczny, ale wymaga dużej puli pamięci. Jeśli Twoje urządzenie ma ograniczoną pamięć lub VRAM GPU, wybierz zamiast tego mniejszy model GGUF z biblioteki modeli Lemonade i używaj identyfikatora tego modelu w całym przewodniku.

> **Uwaga:** Pierwsze uruchomienie `lemonade run` pobiera model, jeśli nie jest jeszcze dostępny, co może chwilę potrwać w zależności od rozmiaru modelu i Twojego połączenia.

Lemonade udostępnia API kompatybilne z OpenAI pod adresem:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Zweryfikuj lokalny model

Potwierdź, że Lemonade może serwować wybrany model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Następnie wyślij małe zapytanie czatu:

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

Jeśli zwrócona zostanie tablica `choices`, Lemonade jest gotowy dla Agent Canvas.

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
## 3. Instalacja i uruchomienie Agent Canvas

<!-- @os:linux -->
Zainstaluj globalnie opublikowany pakiet Agent Canvas:

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

Następnie uruchom pełny stos z terminala:

```bash
agent-canvas
```

Domyślnie Agent Canvas uruchamia się pod adresem `http://localhost:8000`. Otwórz
ten adres URL w przeglądarce. Port nie jest niczym szczególnym — jeśli port 8000
jest już zajęty, podaj dowolny wolny port za pomocą `--port` (lub `-p`) podczas
uruchamiania Agent Canvas:

```bash
agent-canvas --port 3000
```

Następnie otwórz `http://localhost:3000`. Domyślny lokalny backend powinien być
oznaczony jako sprawny (healthy) na ekranie głównym.

Polecenie `agent-canvas` uruchamia razem serwer agenta, backend automatyzacji
oraz frontend webowy. Potrzebujesz tylko tego jednego polecenia, aby uruchomić
OpenHands lokalnie.

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
W systemie Windows uruchom opublikowany obraz kontenera Agent Canvas za pomocą
Docker Desktop. Obraz zawiera serwer Agent Server, backend automatyzacji oraz
frontend webowy, dzięki czemu nie musisz instalować Node.js, `uv` ani CLI na
hoście.

Najpierw utwórz foldery konfiguracji i workspace, które kontener montuje:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Pobierz opublikowany obraz (jest publiczny, więc logowanie nie jest wymagane):

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

Otwórz `http://localhost:8000/canvas` w przeglądarce. Jeśli port 8000 jest już
zajęty, zmapuj inny port hosta, na przykład `-p 8080:8000`, i otwórz zamiast
tego `http://localhost:8080/canvas`.

> **Uwaga:** Pierwsze uruchomienie inicjalizuje Agent Server wewnątrz kontenera,
> więc zanim backend zgłosi stan „healthy”, może minąć minuta lub dwie.

Montowanie `.openhands` zachowuje Twój profil LLM oraz ustawienia pomiędzy
ponownymi uruchomieniami kontenera. Pozostała część tego przewodnika
konfiguruje wszystko za pomocą interfejsu Agent Canvas w przeglądarce.

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

## 4. Konfiguracja lokalnego LLM

Przy pierwszym uruchomieniu Agent Canvas otwiera proces wdrożenia (onboarding).
W tym procesie:

1. Pozostaw zaznaczoną opcję **OpenHands** jako agenta i kliknij **Next**.
2. W sekcji **Set up your LLM** wybierz **Advanced**.
3. Pozostaw **Authentication** ustawione na **API key**.
4. Ustaw **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Ustaw **Base URL** na `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > W systemie Windows stos działa w kontenerze, który nie może dotrzeć do
   > hosta pod adresem `127.0.0.1`. Użyj zamiast tego
   > `http://host.docker.internal:13305/api/v1`, aby skonteneryzowany agent
   > mógł połączyć się z Lemonade działającym na hoście Windows.
   <!-- @os:end -->
6. W polu **API Key** wpisz dowolny niepusty symbol zastępczy, na przykład
   `lemonade-local`. Lemonade nie wymaga prawdziwego klucza, ale klient
   OpenHands potrzebuje jakiejś wartości do wysłania.
7. Kliknij **Next**.

Ukończone ustawienia Advanced powinny wyglądać następująco. Pole klucza API
jest zamaskowane przez interfejs.

![Ustawienia Advanced LLM w Agent Canvas przy pierwszym użyciu z modelem Lemonade i lokalnym adresem URL bazowym](assets/01-llm-advanced-settings.png)

Agent Canvas zapisuje te wartości jako profil LLM. Jeśli Twoja wersja prosi o
nadanie nazwy temu profilowi, użyj nazwy bez spacji, na przykład
`lemonade-local`. Jeśli później zmienisz modele, otwórz **Settings > LLM** i
zaktualizuj te same pola Advanced. Możesz przełączać zapisane profile z pola
czatu za pomocą polecenia `/model`.

## 5. Otwieranie workspace

Agent może odczytywać i modyfikować pliki tylko w ramach wybranego przez
Ciebie workspace. Przed rozpoczęciem zadania wskaż Agent Canvas folder swojego
projektu:

1. Na ekranie głównym wybierz **Open Workspace**.
2. Wybierz folder zawierający Twój projekt (na przykład repozytorium git, nad
   którym ma pracować agent).
3. Rozpocznij nową konwersację w tym workspace.

Wszystko, co robi agent — odczytywanie plików, uruchamianie poleceń, edycja
kodu — jest ograniczone do tego workspace.

![Ekran główny Agent Canvas po zakończeniu wdrożenia](assets/02-agent-canvas-home.png)

## 6. Uruchomienie pierwszego zadania programistycznego

Mając otwarty workspace i wybrany lokalny LLM, wpisz w czacie konkretne
zadanie. Dobrym pierwszym zadaniem jest coś małego i możliwego do
zweryfikowania, na przykład:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Obserwuj oś czasu konwersacji. OpenHands będzie:

- Odczytywać workspace, aby zrozumieć jego strukturę.
- Tworzyć plik `hello.py` z żądaną funkcją i blokiem testowym.
- Opcjonalnie uruchamiać `python3 hello.py`, aby zweryfikować wynik.
- Zgłaszać w czacie, co zrobił, oraz wynik działania poleceń.

Powinieneś zobaczyć nowy plik pojawiający się w workspace, a ostateczna
wiadomość agenta powinna opisywać wprowadzoną zmianę. To właśnie ten moment
jest efektem końcowym: agent napisał i uruchomił prawdziwy kod w Twoim
folderze projektu.

## 7. Przeglądanie i kierowanie pracą agenta

Po zakończeniu danego kroku przez agenta przejrzyj jego pracę przed
zaakceptowaniem kolejnego kroku:

- **Zmiany w plikach**: skorzystaj z przeglądarki plików workspace lub
  widoku różnic (diff) agenta, aby zobaczyć dokładnie, co zostało dodane,
  zmienione lub usunięte.
- **Wynik poleceń**: rozwiń dowolne polecenie uruchomione przez agenta, aby
  zobaczyć stdout, stderr oraz kod wyjścia.
- **Działania następcze**: jeśli wynik nie jest zgodny z Twoimi oczekiwaniami,
  odpowiedz w tej samej konwersacji z poprawką. Agent zachowuje poprzedni
  kontekst i kontynuuje pracę nad tymi samymi plikami.

Na przykład, jeśli test nie wyświetlił oczekiwanego powitania, odpowiedz:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent ponownie odczyta plik, uruchomi polecenie, zdiagnozuje problem i
ponownie edytuje plik — wszystko w ramach tej samej konwersacji.
## Rozwiązywanie problemów

<!-- @os:linux -->
- **`agent-canvas` nie znajduje się w PATH:** zainstaluj ponownie za pomocą
  `npm install -g @openhands/agent-canvas` i upewnij się, że katalog globalnych
  plików binarnych npm znajduje się w PATH, zanim spróbujesz uruchomić
  `agent-canvas` z nowego terminala.
- **`npm install -g` kończy się błędem uprawnień:** skonfiguruj globalny
  katalog npm należący do użytkownika, a następnie ponownie otwórz terminal
  i zainstaluj Agent Canvas jeszcze raz.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **Brak `uv`:** zainstaluj je, korzystając z
  [przewodnika instalacji uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas używa `uv` do zarządzania środowiskiem Python serwera agenta.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` lub `docker run` nie może nawiązać połączenia:** upewnij się,
  że Docker Desktop jest uruchomiony (jego ikona wieloryba znajduje się na pasku
  zadań) i że silnik zakończył uruchamianie. Polecenie `docker version` powinno
  wyświetlić zarówno sekcję Client, jak i Server.
- **Kontener się uruchamia, ale backend nigdy nie staje się zdrowy:** pierwsze
  uruchomienie inicjalizuje Agent Server wewnątrz kontenera; odczekaj minutę
  lub dwie, a następnie sprawdź `docker logs <container>` pod kątem błędów.
- **Kontener nie może połączyć się z Lemonade:** kontener łączy się z hostem
  przez `host.docker.internal`. Upewnij się, że Lemonade działa na hoście
  Windows za pomocą `lemonade status`, i użyj `http://host.docker.internal:13305/api/v1`
  jako Base URL podczas konfigurowania LLM.
<!-- @os:end -->

- **Interfejs ładuje się, ale backend pokazuje stan niezdrowy:** odczekaj
  minutę lub dwie, aż serwer agenta zakończy uruchamianie, a następnie odśwież
  stronę. Jeśli stan niezdrowy się utrzymuje, zrestartuj stos i sprawdź logi
  pod kątem błędów.
- **Żądania czatu Lemonade kończą się błędem połączenia:** upewnij się, że
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` kończy się powodzeniem
  i że Lemonade nadal udostępnia model, co można sprawdzić za pomocą
  `lemonade status`.
- **Agent zgłasza błąd dotyczący długości kontekstu lub limitu tokenów:**
  rozpocznij nową rozmowę, aby agent nie przenosił zbyt dużej historii.
  Jeśli problem się powtarza, zrestartuj Lemonade z większą wartością
  `ctx_size` niż domyślna 65536 (na przykład `ctx_size=131072`), jeśli
  pozwala na to dostępna pamięć.
- **Agent tworzy edycje niskiej jakości lub niekompletne:** przełącz się na
  większy model w Lemonade, albo zleć agentowi mniejsze, bardziej konkretne
  zadanie i pozwól mu je ukończyć przed poproszeniem o kolejną zmianę.

## Kolejne kroki

- Spróbuj wykonać większe zadanie w tym samym obszarze roboczym, na przykład
  dodanie pliku testów jednostkowych lub naprawienie znanego błędu, i przejrzyj
  różnicę (diff) agenta przed zaakceptowaniem zmiany.
- Podłącz serwer MCP, taki jak GitHub lub Slack, w sekcji **Customize**, aby
  agent mógł odczytywać zgłoszenia (issues) lub publikować aktualizacje podczas
  pracy.
- Zapisz kilka profili LLM (szybki, mały model i silniejszy, duży model)
  i przełączaj się między nimi za pomocą `/model` w trakcie rozmowy.
- Przejdź do [automatyzacji OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview), aby
  zamienić powtarzające się cykle programistyczne w zaplanowane lub wyzwalane
  zdarzeniami uruchomienia agenta.

## Zasoby

- [Dokumentacja OpenHands](https://docs.openhands.dev/)
- [Przegląd Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Konfiguracja Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profile LLM i konfiguracja modeli](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentacja Lemonade Server](https://lemonade-server.ai/docs)

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