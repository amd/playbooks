<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ten poradnik zawiera specjalne znaczniki, których GitHub nie może wyrenderować. Odwiedź stronę [amd.com/playbooks](https://amd.com/playbooks), aby poprawnie wyświetlić tę treść.
<!-- @github-only:end -->

## Przegląd

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ten poradnik wymaga co najmniej **32 GB** pamięci systemowej.
<!-- @device:end -->

n8n to platforma do automatyzacji przepływów pracy, która pozwala łączyć aplikacje i usługi za pomocą wizualnego edytora opartego na węzłach.

Ten poradnik pokazuje, jak skonfigurować oparty na sztucznej inteligencji streszczacz wiadomości finansowych, który pobiera dane z sekcji biznesowej AP News, wyodrębnia kluczowe nagłówki i wykorzystuje lokalny model LLM działający na Twoim systemie do wygenerowania podsumowania ukierunkowanego na inwestorów.

## Czego się nauczysz

- Jak zainstalować i uruchomić n8n
- Importowanie i konfigurowanie gotowego przepływu pracy
- Łączenie z Lemonade za pomocą natywnej integracji n8n
- Zrozumienie węzłów przepływu pracy i przepływu danych

## Czym jest Lemonade?

[Lemonade](https://lemonade-server.ai) to platforma do lokalnego serwowania modeli LLM zbudowana z myślą o sprzęcie AMD. Zapewnia interfejs API kompatybilny z OpenAI, który działa w całości na Twojej maszynie — Twoje dane nigdy nie opuszczają Twojego urządzenia.

W tym poradniku używamy Lemonade do serwowania lokalnego modelu LLM, z którym łączy się n8n w celu wykonywania zadań opartych na sztucznej inteligencji. 

n8n zawiera **natywny węzeł Lemonade** (`Lemonade Chat Model`), który zapewnia integrację najwyższej klasy - bez potrzeby ręcznej konfiguracji. Dzięki temu połączenie lokalnego modelu LLM z przepływami automatyzacji jest proste.

## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymaganego oprogramowania
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
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

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## Instalowanie n8n
<!-- @os:windows -->
Zainstaluj n8n globalnie za pomocą npm.

> **Uwaga**: Mogą pojawić się pewne ostrzeżenia npm. Jest to oczekiwane zachowanie.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Wskazówka**: Użytkownicy systemu Windows mogą potrzebować zmodyfikować zasady wykonywania PowerShell (np.
> ustawiając ją na RemoteSigned lub Unrestricted) przed uruchomieniem niektórych poleceń PowerShell.
<!-- @os:end -->


<!-- @os:windows -->
> **Problem ze zmienną PATH**: Jeśli polecenie `n8n --version` zwraca informację, że nie znaleziono polecenia, upewnij się, że katalog globalnych plików binarnych npm znajduje się w zmiennej `PATH` użytkownika. Zwykle ścieżka instalacji znajduje się w `C:\Users\<username>\AppData\Roaming\npm`. 
> Dodaj tę ścieżkę do zmiennej PATH użytkownika (Edytuj zmienne środowiskowe systemu > Zmienne środowiskowe > Edytuj ścieżkę użytkownika) i uruchom ponownie terminal. 

<!-- @os:end -->

<!-- @os:linux -->
Teraz użyjemy usługi Podman, aby skonteneryzować naszą instalację n8n.

Pobierz następujący plik do wybranego katalogu: [compose.yml](assets/compose.yml)

W tym katalogu uruchom następujące polecenie:
```bash
podman compose up -d
```

Spowoduje to zainstalowanie n8n i zapisanie danych w trwałej pamięci.

Uruchom n8n, wpisując `localhost:5678` w pasku adresu przeglądarki.
<!-- @os:end -->

<!-- @os:windows -->
## Uruchamianie n8n

Uruchom n8n z terminala:

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

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

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
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n uruchamia lokalny serwer WWW. Naciśnij `'o'` lub otwórz przeglądarkę pod adresem `http://localhost:5678`, aby uzyskać dostęp do edytora.
<!-- @os:end -->


> **Wskazówka**: Podczas korzystania z n8n pozostaw okno terminala otwarte. Jego zamknięcie może zatrzymać serwer.

## Uruchamianie Lemonade

Lemonade to lokalny serwer, który uruchomi model i połączy się z n8n. 

<!-- @os:linux -->
Otwórz interfejs graficzny Lemonade, klikając ikonę Lemonade na pasku zadań. Możesz stąd przeglądać modele, backendy i wczytywać wstępnie zainstalowane modele.
<!-- @os:end -->

<!-- @os:windows -->
Otwórz interfejs graficzny Lemonade, klikając ikonę Lemonade. Kliknij prawym przyciskiem myszy ikonę w zasobniku systemowym, aby otworzyć aplikację. Następnie możesz dodawać modele, backendy i wczytywać wstępnie zainstalowane modele.
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

Przy pierwszym otwarciu n8n zostaniesz poproszony o utworzenie konta lub zalogowanie się:

1. Otwórz `http://localhost:5678` w przeglądarce
2. Utwórz nowe lokalne konto za pomocą swojego adresu e-mail lub zaloguj się, jeśli masz już konto
3. Po zalogowaniu zobaczysz panel n8n

> **Wskazówka**: Jeśli zostaniesz zablokowany i nie będziesz mieć dostępu do konta, spróbuj użyć polecenia `n8n user-management:reset`

### Krok 2: Zaimportuj przepływ pracy

Udostępniliśmy gotowy przepływ pracy, który możesz zaimportować bezpośrednio:

1. Pobierz następujący plik przepływu pracy: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kliknij **Start from Scratch**, aby otworzyć edytor przepływu pracy. Alternatywnie kliknij przycisk + w lewym górnym rogu, a następnie **Add workflow**.
3. Kliknij menu **...** (trzy kropki) w prawym górnym pasku i wybierz **Import from file**
4. Wybierz pobrany plik `financial-news-workflow.json`
5. Przepływ pracy pojawi się na płótnie
### Krok 3: Zrozumienie przepływu pracy

Zaimportowany przepływ pracy zawiera 9 połączonych węzłów:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Węzeł | Cel |
|------|---------|
| **When clicking 'Execute workflow'** | Ręczny wyzwalacz do uruchomienia przepływu pracy |
| **Fetch Financial News Webpage** | Żądanie HTTP GET do `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Węzeł oczekiwania zapewniający pełne załadowanie zawartości strony |
| **Extract News Headlines & Text** | Węzeł HTML wyodrębniający nagłówki, wybór redakcji, najważniejsze wiadomości i wiadomości regionalne za pomocą selektorów CSS |
| **Clean Extracted News Data** | Węzeł Set łączący wszystkie wyodrębnione dane w jedno pole tekstowe |
| **AI Financial News Summarizer** | Agent AI przetwarzający wiadomości za pomocą systemowego promptu analityka finansowego |
| **Lemonade Chat Model** | Łączy się z lokalnym serwerem Lemonade uruchamiającym LLM |
| **Structured Output Parser** | Formatuje wynik AI jako ustrukturyzowany JSON |
| **Convert to File** | Konwertuje podsumowanie na plik do pobrania |

### Krok 4: Konfiguracja poświadczeń Lemonade

Przed uruchomieniem przepływu pracy należy połączyć go z lokalnym serwerem Lemonade:

1. Kliknij dwukrotnie węzeł **Lemonade Chat Model** w n8n
2. W menu rozwijanym **Credential to connect with** wybierz **Create New Credential**
3. Wprowadź wartości z poniższej tabeli i kliknij zapisz.
4. Wybierz odpowiedni model, który został załadowany w Lemonade Server.

  | Pole | Wartość |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Uwaga**: Przed przetestowaniem uruchom `lemonade status` w terminalu, aby potwierdzić, że serwer Lemonade działa.
<!-- @device:halo_box -->
> Ten przepływ pracy wykorzystuje GPT-OSS-120B, który jest domyślnie zainstalowany w Lemonade. Możesz zmienić go na inne załadowane modele w ustawieniach węzła Lemonade Chat Model.
<!-- @device:end -->

### Krok 5: Testowanie przepływu pracy

1. Upewnij się, że Lemonade jest uruchomiony z załadowanym modelem
2. Kliknij **Execute workflow** na dole środkowej części obszaru roboczego
3. Obserwuj wykonywanie każdego węzła od lewej do prawej — po zakończeniu zmieniają kolor na zielony
4. Kliknij dwukrotnie węzeł **AI Financial News Summarizer**, aby zobaczyć wygenerowane podsumowanie w dolnym panelu.
5. Kliknij dwukrotnie węzeł **Convert to File**, aby pobrać odpowiedni plik tekstowy w dolnym panelu.

## Zrozumienie agenta AI

AI Financial News Summarizer wykorzystuje systemowy prompt zaprojektowany do analizy finansowej:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agent otrzymuje oczyszczone dane o wiadomościach i generuje ustrukturyzowane podsumowanie z nastrojami rynkowymi.

### Zapisywanie przepływu pracy

Kliknij nazwę przepływu pracy u góry i zmień jej nazwę, jeśli chcesz. Przepływy pracy zapisują się automatycznie podczas pracy.

## Kolejne kroki

- **Zaplanuj automatyzację**: Zastąp Manual Trigger węzłem **Schedule Trigger**, aby uruchamiać przepływ codziennie
- **Wysyłaj powiadomienia**: Dodaj węzeł **Discord**, **Slack** lub **Email**, aby otrzymywać podsumowania
- **Wypróbuj różne modele**: Zmień model w węźle Lemonade Chat Model, aby eksperymentować z różnymi modelami LLM
- **Dostosuj ekstrakcję**: Zmodyfikuj selektory CSS węzła HTML Extract, aby kierować się na inne sekcje wiadomości
- **Wypróbuj różne backendy**: n8n obsługuje również [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio i inne lokalne backendy LLM

### Odkryj szablony n8n

n8n oferuje setki gotowych szablonów przepływów pracy. Przeglądaj oficjalną bibliotekę szablonów pod adresem:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Wyszukaj „AI”, „LLM” lub „automation”, aby znaleźć przepływy pracy, które możesz zaimportować i dostosować.

Aby uzyskać więcej informacji, zapoznaj się z [dokumentacją n8n](https://docs.n8n.io/).