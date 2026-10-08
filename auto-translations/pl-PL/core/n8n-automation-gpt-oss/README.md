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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Przegląd

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ten poradnik wymaga co najmniej **32 GB** pamięci systemowej.
<!-- @device:end -->

n8n to platforma do automatyzacji przepływów pracy, która pozwala łączyć aplikacje i usługi za pomocą wizualnego edytora opartego na węzłach.

Ten poradnik pokazuje, jak skonfigurować oparty na AI narzędzie do podsumowywania wiadomości finansowych, które pobiera najnowsze nagłówki biznesowe z kanału RSS z wiadomościami i wykorzystuje lokalny model LLM działający na Twoim systemie do wygenerowania podsumowania skierowanego do inwestorów.

## Czego się nauczysz

- Jak zainstalować i uruchomić n8n
- Importowanie i konfigurowanie gotowego przepływu pracy
- Łączenie się z Lemonade za pomocą natywnej integracji n8n
- Zrozumienie węzłów przepływu pracy i przepływu danych

## Czym jest Lemonade?

[Lemonade](https://lemonade-server.ai) to platforma do lokalnego serwowania modeli LLM zbudowana z myślą o sprzęcie AMD. Udostępnia API kompatybilne z OpenAI, które działa całkowicie na Twoim urządzeniu — Twoje dane nigdy go nie opuszczają.

W tym poradniku używamy Lemonade do serwowania lokalnego modelu LLM, z którym łączy się n8n w celu realizacji zadań opartych na AI.

n8n zawiera **natywny węzeł Lemonade** (`Lemonade Chat Model`), który zapewnia pełnoprawną integrację - bez konieczności ręcznej konfiguracji. Dzięki temu podłączenie lokalnego modelu LLM do przepływów automatyzacji jest proste.

<!-- @device:halo_box,halo,stx,krk -->
## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymaganego oprogramowania
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:n8n,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- Linux runs n8n as a Podman container (see compose.yml below), so Node.js and a host n8n install are not required; podman is the only extra prerequisite. -->
<!-- @require:lemonade,podman -->
<!-- @prereq:podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @prereq:lemonade-models-gpt-oss-120b -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:lemonade-models-gpt-oss-20b -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


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
  "max_tokens": 32
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
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## Instalowanie n8n
<!-- @os:windows -->
Zainstaluj n8n globalnie za pomocą npm.

> **Uwaga**: Mogą pojawić się ostrzeżenia npm. Jest to oczekiwane zachowanie.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Wskazówka**: Użytkownicy systemu Windows mogą potrzebować zmodyfikować zasady wykonywania PowerShell (Execution Policy) (np.
> ustawiając je na RemoteSigned lub Unrestricted) przed uruchomieniem niektórych poleceń Powershell.
<!-- @os:end -->


<!-- @os:windows -->
> **Problem z PATH**: Jeśli `n8n --version` zwraca informację, że polecenie nie zostało znalezione, upewnij się, że katalog binarny npm (global bin) znajduje się w zmiennej `PATH` użytkownika. Zwykła ścieżka instalacji to `C:\Users\<username>\AppData\Roaming\npm`. 
> Dodaj ją do ścieżki użytkownika (Edytuj zmienne środowiskowe systemu > Zmienne środowiskowe > Edytuj ścieżkę użytkownika) i ponownie uruchom terminal. 

<!-- @os:end -->

<!-- @os:linux -->
Teraz użyjemy usługi Podman do konteneryzacji naszej instalacji n8n.

Pobierz poniższy plik do wybranego katalogu: [compose.yml](assets/compose.yml)

W tym katalogu uruchom następujące polecenie:
```bash
podman compose up -d
```

Powinno to zainstalować n8n i zapisać dane do pamięci trwałej.

Uruchom n8n, wpisując `localhost:5678` w pasku adresu przeglądarki.
<!-- @os:end -->

<!-- @os:windows -->
## Uruchamianie n8n

Uruchom n8n z poziomu terminala:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

podman rm -f n8n >/dev/null 2>&1 || true
podman compose -f compose.yml up -d

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  podman ps -a || true
  podman logs n8n 2>&1 | tail -30 || true
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n uruchamia lokalny serwer WWW. Naciśnij `'o'` lub otwórz w przeglądarce adres `http://localhost:5678`, aby uzyskać dostęp do edytora.
<!-- @os:end -->


> **Wskazówka**: Podczas korzystania z n8n pozostaw okno terminala otwarte. Jego zamknięcie może zatrzymać serwer.

## Uruchamianie Lemonade

Lemonade to lokalny serwer, który uruchomi model i połączy się z n8n. 

<!-- @os:linux -->
Otwórz interfejs graficzny Lemonade, klikając ikonę Lemonade na pasku zadań. Stąd możesz przeglądać modele, backendy oraz wczytywać wstępnie zainstalowane modele.
<!-- @os:end -->

<!-- @os:windows -->
Otwórz interfejs graficzny Lemonade, klikając ikonę Lemonade. Kliknij prawym przyciskiem myszy ikonę w zasobniku systemowym, aby otworzyć aplikację. Następnie możesz dodawać modele, backendy oraz wczytywać wstępnie zainstalowane modele.
<!-- @os:end -->

>**Wskazówka**: Po uruchomieniu interfejs graficzny Lemonade jest również dostępny pod adresem http://localhost:13305

Alternatywnie możesz otworzyć terminal i uruchomić `lemonade list`, aby zobaczyć, jakie modele są zainstalowane. Następnie uruchom:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## Konfigurowanie przepływu pracy

### Krok 1: Zarejestruj się lub zaloguj do n8n

Gdy po raz pierwszy otworzysz n8n, zostaniesz poproszony o utworzenie konta lub zalogowanie się:

1. Otwórz `http://localhost:5678` w przeglądarce
2. Utwórz nowe konto lokalne, podając swój adres e-mail, lub zaloguj się, jeśli masz już konto
3. Po zalogowaniu zobaczysz panel n8n

> **Wskazówka**: Jeśli nie możesz zalogować się do konta, spróbuj `n8n user-management:reset`

### Krok 2: Zaimportuj przepływ pracy

Udostępniliśmy gotowy przepływ pracy, który możesz zaimportować bezpośrednio:

1. Pobierz następujący plik przepływu pracy: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kliknij **Start from Scratch**, aby otworzyć edytor przepływu pracy. Alternatywnie kliknij przycisk + w lewym górnym rogu, a następnie **Add workflow**.
3. Kliknij menu **...** (trzy kropki) w prawym górnym pasku i wybierz **Import from file**
4. Wybierz pobrany plik `financial-news-workflow.json`
5. Przepływ pracy pojawi się na płótnie roboczym
### Krok 3: Zrozumienie przepływu pracy

Zaimportowany przepływ pracy zawiera 8 połączonych węzłów:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Węzeł | Przeznaczenie |
|------|---------|
| **When clicking 'Execute workflow'** | Ręczny wyzwalacz uruchamiający przepływ pracy |
| **Fetch Financial News Feed** | Węzeł RSS Read, który pobiera najnowsze nagłówki biznesowe z kanału RSS (domyślnie kanał NYT Business, bez konieczności posiadania klucza API) |
| **Aggregate Headlines** | Węzeł Aggregate, który zbiera tytuły nagłówków i podsumowania z każdego elementu kanału w jedną listę |
| **Clean Extracted News Data** | Węzeł Set, który łączy wszystkie nagłówki w jedno pole tekstowe |
| **AI Financial News Summarizer** | Agent AI, który przetwarza wiadomości, korzystając z systemowego polecenia analityka finansowego |
| **Lemonade Chat Model** | Łączy się z lokalnym serwerem Lemonade, na którym działa LLM |
| **Structured Output Parser** | Formatuje wynik AI jako uporządkowany JSON |
| **Convert to File** | Konwertuje podsumowanie do pliku możliwego do pobrania |

> **Wskazówka**: Aby użyć innego źródła wiadomości, kliknij dwukrotnie węzeł **Fetch Financial News Feed** i zastąp adres URL dowolnym preferowanym kanałem RSS dotyczącym biznesu lub rynków.

### Krok 4: Konfiguracja poświadczeń Lemonade

Przed uruchomieniem przepływu pracy musisz połączyć go z lokalnym serwerem Lemonade:

1. Kliknij dwukrotnie węzeł **Lemonade Chat Model** w n8n
2. W menu rozwijanym **Credential to connect with** wybierz **Create New Credential**
3. Wprowadź wartości z poniższej tabeli i kliknij zapisz.
4. Wybierz odpowiedni model, który został wczytany w Lemonade Server.

  | Pole | Wartość |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Uwaga**: Przed testowaniem uruchom polecenie `lemonade status` w terminalu, aby potwierdzić, że serwer Lemonade działa.
<!-- @device:halo_box -->
> Ten przepływ pracy wykorzystuje model GPT-OSS-120B, który jest fabrycznie zainstalowany w Lemonade. Możesz zmienić go na inne wczytane modele w ustawieniach węzła Lemonade Chat Model.
<!-- @device:end -->

### Krok 5: Testowanie przepływu pracy

1. Upewnij się, że Lemonade działa z wczytanym modelem
2. Kliknij **Execute workflow** na dole, na środku obszaru roboczego
3. Obserwuj, jak każdy węzeł wykonuje się od lewej do prawej — po zakończeniu zmieniają kolor na zielony
4. Kliknij dwukrotnie węzeł **AI Financial News Summarizer**, aby zobaczyć wygenerowane podsumowanie w dolnym panelu.
5. Kliknij dwukrotnie węzeł **Convert to File**, aby pobrać odpowiedni plik tekstowy w dolnym panelu.

## Zrozumienie agenta AI

AI Financial News Summarizer wykorzystuje systemowe polecenie zaprojektowane do analizy finansowej:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agent otrzymuje oczyszczone dane dotyczące wiadomości i generuje uporządkowane podsumowanie wraz z nastrojami rynkowymi.

### Zapisywanie przepływu pracy

Kliknij nazwę przepływu pracy u góry i zmień ją według uznania. Przepływy pracy zapisują się automatycznie w trakcie pracy.

## Kolejne kroki

- **Automatyzacja harmonogramu**: Zastąp Manual Trigger węzłem **Schedule Trigger**, aby uruchamiać przepływ codziennie
- **Wysyłanie powiadomień**: Dodaj węzeł **Discord**, **Slack** lub **Email**, aby otrzymywać podsumowania
- **Wypróbuj inne modele**: Zmień model w węźle Lemonade Chat Model, aby eksperymentować z różnymi modelami LLM
- **Zmień źródło wiadomości**: Skieruj węzeł **Fetch Financial News Feed** na inny kanał RSS, aby śledzić inne sekcje lub publikacje
- **Wypróbuj inne backendy**: n8n obsługuje również [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio i inne lokalne backendy LLM

### Przeglądanie szablonów n8n

n8n posiada setki gotowych szablonów przepływów pracy. Przeglądaj oficjalną bibliotekę szablonów pod adresem:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Wyszukaj „AI”, „LLM” lub „automation”, aby znaleźć przepływy pracy, które możesz zaimportować i dostosować.

Aby uzyskać więcej informacji, zapoznaj się z [dokumentacją n8n](https://docs.n8n.io/).

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