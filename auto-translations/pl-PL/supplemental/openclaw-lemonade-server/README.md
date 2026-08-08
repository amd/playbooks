<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

# Uruchamianie OpenClaw z Lemonade Server jako backendem

## Przegląd

[**OpenClaw**](https://openclaw.ai/) to autonomiczny agent AI, który potrafi pisać i uruchamiać kod, zarządzać plikami oraz realizować złożone, wieloetapowe zadania w Twoim imieniu. W przeciwieństwie do asystenta czatu, który jedynie odpowiada na pytania, OpenClaw podejmuje rzeczywiste działania w Twoim systemie, co oznacza, że potrzebuje szybkiego, wydajnego backendu AI, który poradzi sobie z wymagającą pętlą agenta.

[**Lemonade Server**](https://lemonade-server.ai/) jest właśnie takim backendem. To otwartoźródłowy lokalny serwer wnioskowania, który uruchamia modele GenAI bezpośrednio na Twoim sprzęcie i udostępnia je za pośrednictwem standardowego w branży API OpenAI.

Razem tworzą w pełni lokalny stos agenta AI: Lemonade obsługuje wnioskowanie modelu, a OpenClaw zapewnia pętlę agenta, która zamienia wyniki modelu w rzeczywiste działania.

> **Zanim przejdziesz dalej:** OpenClaw jest wysoce autonomicznym agentem AI. Nadanie jakiemukolwiek agentowi AI dostępu do Twojego systemu może skutkować nieprzewidywalnymi lub niezamierzonymi rezultatami. Kontynuuj tylko wtedy, gdy rozumiesz związane z tym ryzyko i akceptujesz działanie autonomicznego oprogramowania w Twoim imieniu.

---

## Czego się nauczysz

Po zakończeniu tego przewodnika będziesz w stanie:

- Poznać **Lemonade Server**
- **Zainstalować OpenClaw** i **skierować go do Lemonade Server** jako swojego backendu AI.
- **Uruchomić bramę OpenClaw** i potwierdzić, że Twój agent jest gotowy do pracy.
- **Podłączyć kanał komunikacji** (Discord lub Telegram), aby móc rozmawiać ze swoim agentem z dowolnego urządzenia.

---

## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymaganego oprogramowania

<!-- @os:linux -->
- Komputer z systemem **Ubuntu 24.04+** lub zgodną dystrybucją Linuksa opartą na Debianie z `apt-get`
- Co najmniej **12 GB pamięci RAM** (zalecane 64 GB+ w przypadku większych modeli)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (opcjonalnie, do izolowania OpenClaw w piaskownicy)
- **~10–30 GB wolnego miejsca na dysku** na wagi modelu
<!-- @os:end -->

<!-- @os:windows -->
- Komputer z systemem **Windows 10/11**
- Co najmniej **12 GB pamięci RAM** (zalecane 64 GB+ w przypadku większych modeli)
- **~10–30 GB wolnego miejsca na dysku** na wagi modelu
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (opcjonalnie, do izolowania OpenClaw w piaskownicy)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Pobieranie i wczytywanie zalecanego modelu

Zalecanym modelem do tego przewodnika jest **Qwen3.6-35B-A3B-GGUF** od Unsloth, silny model MoE z oknem kontekstu wynoszącym 263 tys. tokenów, dobrze dopasowany do obciążeń związanych z agentami. Ten model wykorzystuje kwantyzację UD-Q4_K_XL. Pobierz go teraz:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Następnie wczytaj go z dużym oknem kontekstu i zapisz to ustawienie na potrzeby przyszłych uruchomień:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model ma domyślną długość kontekstu wynoszącą 262 144 tokeny. Jeśli napotkasz błędy braku pamięci (OOM), rozważ zmniejszenie okna kontekstu. Ponieważ jednak Qwen3.6 wykorzystuje rozszerzony kontekst do złożonych zadań, zalecamy utrzymanie długości kontekstu wynoszącej co najmniej 128 tys. tokenów, aby zachować zdolności rozumowania.

> **Wskazówka: Wyłącz tryb myślenia, aby uzyskać szybsze odpowiedzi agenta:** Qwen3.6-35B-A3B domyślnie działa w trybie myślenia, co dodaje opóźnienie przed każdą odpowiedzią. W przypadku pętli agenta ten narzut szybko się kumuluje. Repozytorium [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) udostępnia gotową konfigurację wyłączającą tryb myślenia. Aby jej użyć, pobierz plik i zaimportuj go:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

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
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
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
model_id = "${openclaw_model}"

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

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
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

## Konfigurowanie WSL

Uruchamiamy OpenClaw wewnątrz WSL (zalecane) i łączymy go z Lemonade działającym natywnie w systemie Windows. Dzięki temu masz środowisko powłoki Linux dla OpenClaw, jednocześnie zachowując akcelerację GPU Lemonade po stronie Windows.

### Instalowanie WSL i Ubuntu

Otwórz PowerShell jako administrator i zainstaluj jądro WSL:

```powershell
wsl --install --no-distribution
```

Następnie zainstaluj Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Włączanie systemd w WSL

Uruchom to wewnątrz terminala Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Zamknij WSL i uruchom je ponownie:

```powershell
exit
wsl --shutdown
wsl
```

### Mostkowanie Lemonade z Windows do WSL

WSL2 działa w sieci wirtualnej. Lemonade w systemie Windows wiąże się z `127.0.0.1`, do którego WSL nie ma bezpośredniego dostępu. Proxy portów Windows przekazuje ruch z adresu IP bramy WSL do localhost systemu Windows.

**Znajdź adres IP bramy WSL** (uruchom wewnątrz WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodaj proxy portu** (uruchom w PowerShell jako administrator, zastępując `<WSL-Gateway-IP>` adresem IP bramy WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Uwaga: Jeśli napotkasz błąd `netsh: command not found`, spróbuj zamiast tego użyć jawnej nazwy pliku wykonywalnego – `netsh.exe`

**Dodaj regułę zapory** (w tym samym podniesionym oknie PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Zweryfikuj z poziomu WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Jeśli w poprzednim kroku wczytano już model Qwen3.6-35B-A3B-GGUF, powinieneś zobaczyć wynik JSON podobny do poniższego:

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

#### Utrzymanie działania mostu po ponownym uruchomieniu

Reguła `netsh portproxy` przetrwa ponowne uruchomienie, ale adres IP bramy WSL może się zmienić po `wsl --shutdown` lub restarcie. Gdy to nastąpi, proxy nadal wskazuje na stary adres IP, a Lemonade staje się nieosiągalne z poziomu WSL. Jeśli tak się stanie, skorzystaj z jednej z poniższych opcji.

**Opcja 1 (zalecana) — Automatyczna naprawa mostu.** Aby uniknąć wykonywania tego ręcznie za każdym razem, użyj zaplanowanego zadania, które sprawdza most przy każdym uruchomieniu i logowaniu i odbudowuje go tylko wtedy, gdy adres IP bramy się zmienił. Zobacz [przewodnik automatycznej naprawy mostu WSL dla Lemonade](assets/RepairLemonadeWslBridge.md).


**Opcja 2 — Ręczna naprawa mostu.** Najpierw pobierz aktualny adres IP bramy WSL, uruchamiając to wewnątrz WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Skopiuj tę wartość; użyjesz jej w miejsce `<new-WSL-Gateway-IP>` poniżej.

Następnie w **podniesionym oknie PowerShell** (uruchomionym jako administrator) wyświetl listę istniejących reguł, usuń tylko nieaktualną regułę Lemonade i dodaj nową z aktualnym adresem IP:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

W wynikach polecenia `show all` nieaktualna reguła Lemonade to wpis, którego adres connect to `127.0.0.1` na porcie `13305`; jego adres listen to Twój `<old-WSL-Gateway-IP>`. Usunięcie na podstawie tego adresu usuwa tylko tę regułę, pozostawiając nienaruszone inne reguły port-proxy na Twoim komputerze.

Reguła zapory dodana podczas konfiguracji jest powiązana z portem `13305` (a nie z adresem IP), więc nadal działa i nie trzeba jej ponownie tworzyć.

> **Zalecenie:** Aby uniknąć problemów z bramą, zdecydowanie zalecamy następującą konfigurację powłoki:
> - **Polecenia Windows** powinny być wykonywane w **PowerShell**
> - **Polecenia dystrybucji WSL** powinny być wykonywane w **wierszu polecenia** (uruchomionym jako **Administrator**)

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## Instalacja i konfiguracja OpenClaw

### Instalacja OpenClaw
<!-- @os:windows -->
> Uruchom polecenia z tej sekcji w swoim **terminalu WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Flaga `--no-onboard` pomija interaktywnego kreatora konfiguracji, backend modelu skonfigurujesz ręcznie w następnym kroku, co daje precyzyjną kontrolę nad tym, jaki model i serwer są używane.

Otwórz nowy terminal i potwierdź instalację:

```bash
openclaw --version
```

> **Wskazówka:** Jeśli po instalacji pojawi się komunikat `command not found`, dodaj globalny katalog bin npm do PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Aby uczynić to trwałym, dodaj powyższą linię do pliku `~/.bashrc` lub `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


### Konfiguracja OpenClaw do korzystania z Lemonade

Uruchom nieinteraktywny onboarding OpenClaw.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

To polecenie zapisuje konfigurację OpenClaw w pliku `~/.openclaw/openclaw.json`.

> **Rozmiar okna kontekstu w OpenClaw:** Kompaktowanie w OpenClaw uruchamia się, gdy `contextTokens > contextWindow − reserveTokens`. Domyślna wartość `reserveTokensFloor` to 20 000 tokenów, czyli próg minimalny, który nadpisuje `reserveTokens`, gdy jest ono niższe, więc każdy kontekst modelu poniżej ~37k spowoduje nieskończoną pętlę kompaktowania. Ustaw niską rezerwę i wyłącz próg minimalny raz w swojej konfiguracji, a będzie miało to zastosowanie do każdego modelu, bez konieczności dostrajania per model:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` to *próg minimalny* (minimalne zabezpieczenie), a nie sama rezerwa, ustawienie samego progu nie ma efektu. `reserveTokensFloor: 0` wyłącza zabezpieczenie, dzięki czemu niższa wartość `reserveTokens` zostaje zaakceptowana.
>
> **Kiedy to zastosować:** Użyj tej konfiguracji, jeśli efektywne okno kontekstu Twojego modelu jest mniejsze niż ~37k, czy to dlatego, że model jest mały (np. 8k, 16k, 32k), czy dlatego, że celowo ograniczyłeś go do niższej wartości (np. ładując model 128k, ale ustawiając kontekst na 16k w Lemonade). Bez tego OpenClaw wejdzie w nieskończoną pętlę kompaktowania przy uruchomieniu.
>
> **Modele z dużym kontekstem przy pełnym kontekście:** Możesz całkowicie pominąć ten krok. Wartości domyślne działają dobrze, kompaktowanie uruchomi się na długo przed zapełnieniem okna, a model ma wystarczająco dużo miejsca na generowanie długich odpowiedzi. Jeśli mimo to zastosujesz tę konfigurację, pamiętaj, że `reserveTokens: 4096` ogranicza długość odpowiedzi do ~4k tokenów, co może obciąć generowanie długich plików lub szczegółowych planów.
>
> **Gdzie to dodać:** Umieść blok `compaction` wewnątrz `agents.defaults` w swoim pliku `openclaw.json` (zwykle w `~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> Reszta konfiguracji (gateway, channels, models itd.) pozostaje bez zmian, dodać należy jedynie klucz `compaction`.
### (Zalecane) Włącz sandboxing Dockera

OpenClaw może kierować wszystkie operacje agenta na plikach i kodzie przez izolowany kontener Docker, zamiast wykonywać je bezpośrednio na hoście. Ogranicza to zasięg oddziaływania każdej niezamierzonej akcji do środowiska izolowanego (sandbox), pozostawiając system plików i sieć hosta nietknięte.

Zbuduj obraz sandboxa raz (Docker musi być zainstalowany):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Uruchom to, aby dodać klucz `sandbox` wewnątrz istniejącego bloku `agents.defaults` w `~/.openclaw/openclaw.json`:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

Kontenery sandbox domyślnie **nie mają dostępu do sieci**. Zobacz [dokumentację sandboxingu](https://docs.openclaw.ai/gateway/sandboxing), aby dowiedzieć się o montowaniach woluminów i nadpisywaniu ustawień sieciowych.

> #### Rozwiązywanie problemów: Odmowa uprawnień Dockera
> 
> Jeśli otrzymasz komunikat „permission denied” podczas uruchamiania poleceń Dockera:
> 
> **Krok 1: Dodaj swojego użytkownika do grupy docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Krok 2: Jeśli błąd nadal występuje, zastosuj trwałą poprawkę**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Następnie **uruchom ponownie** system.
> 
> **Szybka tymczasowa poprawka** (resetuje się po ponownym uruchomieniu):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
## (Zalecane) Integracja OpenClaw z usługami Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) zapewnia samodzielnie hostowaną usługę indeksowania stron internetowych i ekstrakcji treści, która może obejść te wyzwania i odblokować pełny potencjał automatyzacji OpenClaw. 

W tej konfiguracji OpenClaw działa jako zestaw kontenerów Docker zarządzanych za pomocą Podman. Aby uprościć zarządzanie cyklem życia i automatyczne uruchamianie, rejestrujemy Firecrawl jako usługę `systemd` na poziomie użytkownika, która orkiestruje bazowy stos Podman Compose. Dzięki temu OpenClaw może uruchamiać bramę (gateway), zatrzymywać ją i weryfikować usługę Firecrawl za pomocą standardowych poleceń `systemctl --user`, zamiast bezpośrednio wchodzić w interakcję z kontenerami. 

Aby wszystko było proste, podzieliliśmy cały proces na cztery kroki:

---

### 1. Zarejestruj usługę systemową
Przejdź do katalogu konfiguracyjnego użytkownika systemd:
```bash
cd ~/.config/systemd/user
```
Utwórz i otwórz nowy plik o nazwie `firecrawl.service`.
```bash
nano firecrawl.service
```
Skopiuj i wklej następującą konfigurację:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
W tym momencie usługa została zdefiniowana, ale jeszcze nie zarejestrowana w `systemd`. 
Upewnij się, że nazwa pliku dokładnie odpowiada tej utworzonej powyżej, a następnie uruchom:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Jeśli operacja się powiedzie, powinieneś zobaczyć następujący wynik:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` zawiera dowiązania symboliczne do usług skonfigurowanych do automatycznego uruchamiania.

### 2. Skonfiguruj Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) jest idealnym rozwiązaniem dla osób, które potrzebują pełnej kontroli nad środowiskiem scrapowania i przetwarzania danych, ale wiąże się to z dodatkowym nakładem pracy na utrzymanie i konfigurację.

Zacznij od sklonowania repozytorium:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Utwórz plik `.env` w katalogu głównym `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Wdróż OpenClaw za pomocą Podman Compose

Zanim przejdziesz dalej, upewnij się, że pobrałeś najnowszy obraz Docker OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Po wykonaniu tego kroku pobierz plik Compose OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) i umieść go w katalogu głównym `/firecrawl`:

> Ta konwencja jest wymagana, aby `systemd` mógł poprawnie zlokalizować i uruchomić usługę zgodnie z ustawieniem `WorkingDirectory=${HOME}/firecrawl`.

> Zawsze możesz rozbudować stos, dodając kolejne usługi Firecrawl w razie potrzeby. Pełną listę dostępnych usług znajdziesz w oficjalnym pliku [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Uruchom usługę OpenClaw za pośrednictwem Firecrawl 

Zanim przekażesz kontrolę do `systemd`, sprawdź, czy wszystko działa poprawnie, uruchamiając stos ręcznie:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Jeśli wszystko jest skonfigurowane prawidłowo, powinieneś zobaczyć uruchamiający się kontener OpenClaw, a wynik w wierszu poleceń powinien wyglądać podobnie do tego:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Po weryfikacji zatrzymaj stos przed przejściem dalej:
```bash
podman compose -f openclaw-compose.yaml down
```
Przed uruchomieniem usługi musisz upewnić się, że ustawiono odpowiedniego właściciela i uprawnienia dla katalogu `firecrawl` oraz jego pliku `.env`. 
Jest to niezbędne, aby usługa mogła zapisać Twoje dane uwierzytelniające podczas uruchamiania.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Teraz, gdy wszystko zostało zweryfikowane, uruchom usługę za pomocą `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Akcje OpenClaw](https://docs.openclaw.ai/) są dostępne z poziomu interaktywnego kontenera, a Panel internetowy (Web Dashboard) jest dostępny na tym samym hoście i porcie pod adresem http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Uzyskiwanie tokenu `OPENCLAW_GATEWAY_TOKEN`

Po uruchomieniu usługi zauważysz nowy katalog `.openclaw` utworzony w Twoim katalogu domowym (~/.openclaw). Ten katalog jest domyślnie zablokowany, więc musisz go odblokować, aby pobrać token bramy (gateway).

1. Nadaj dostęp do katalogu:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Odczytaj swój token bramy:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Znajdź wartość `OPENCLAW_GATEWAY_TOKEN` w wyniku.

3. Otwórz panel bramy w przeglądarce pod adresem http://127.0.0.1:18789. Wklej token po wyświetleniu monitu o uwierzytelnienie.

Aby zatrzymać usługę, uruchom:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Uruchamianie bramki OpenClaw

Bramka to proces OpenClaw, który zarządza pętlą agenta i obsługuje panel:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

Aby otworzyć panel, uruchom to polecenie w drugim terminalu, podczas gdy bramka nadal działa:

```bash
openclaw dashboard
```

Ponieważ bramka wiąże się z interfejsem loopback, panel automatycznie uwierzytelnia się po otwarciu z tego samego komputera – wprowadzanie tokenu ani zatwierdzanie urządzenia nie jest wymagane w przypadku dostępu lokalnego. Powinieneś zobaczyć panel OpenClaw z modelem Lemonade wymienionym jako aktywny backend.

> Jeśli włączono sandboxing, możesz to zweryfikować, prosząc agenta o wykonanie `run hostname` z poziomu panelu. Jeśli zamiast nazwy hosta swojego komputera zobaczysz krótki identyfikator kontenera, sandbox działa poprawnie.

**Gratulacje, zbudowałeś w pełni lokalny stos agenta AI od podstaw.**

> **Potrzebujesz tokenu bramki?** Uruchom `openclaw dashboard --no-open`, aby wyświetlić adres URL panelu z osadzonym tokenem (podejmowana jest również próba skopiowania go do schowka). Alternatywnie token znajduje się pod kluczem `gateway.auth.token` w pliku `~/.openclaw/openclaw.json`.

**Dostęp do panelu z innego urządzenia (przez tunel SSH)**

Jeśli OpenClaw działa na zdalnym komputerze, możesz uzyskać dostęp do jego panelu z lokalnego komputera za pomocą tunelu SSH. Tunel przekazuje port bramki (`18789`), dzięki czemu lokalna przeglądarka może komunikować się ze zdalną bramką przez `127.0.0.1`.

1. Z poziomu **lokalnego komputera** połącz się raz ze zdalnym komputerem i zaakceptuj monit o odcisku palca, aby host został dodany do znanych hostów:

   ```bash
   ssh user@<host-ip>
   ```

2. Nadal na **lokalnym komputerze** otwórz tunel SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Uwaga:** Po wprowadzeniu hasła terminal nie wyświetla żadnych danych wyjściowych i wygląda, jakby się zawiesił. Jest to oczekiwane zachowanie: flaga `-N` mówi SSH, aby nie uruchamiać żadnego zdalnego polecenia, więc po prostu utrzymuje otwarty tunel. Pozostaw ten terminal uruchomiony.

3. Na **lokalnym komputerze** otwórz przeglądarkę i przejdź pod adres `http://127.0.0.1:18789`.

4. Na **zdalnym komputerze** wyświetl token bramki i wklej go do przeglądarki, aby się zalogować:

   ```bash
   openclaw dashboard --no-open
   ```

   To polecenie wyświetla adres URL panelu z osadzonym tokenem; skopiuj token, aby się zalogować. (Token jest również przechowywany pod kluczem `gateway.auth.token` w pliku `~/.openclaw/openclaw.json`).

> **Zatwierdzanie zdalnego urządzenia:** Gdy otworzysz panel z innego komputera lub telefonu, przeglądarka może wyświetlić identyfikator żądania. Na **zdalnym komputerze** wyświetl listę oczekujących żądań:
> ```bash
> openclaw devices list
> ```
> Następnie zatwierdź pasujące żądanie:
> ```bash
> openclaw devices approve <requestId>
> ```
> Jest to potrzebne tylko w przypadku urządzeń zdalnych lub drugorzędnych; dostęp loopback z tego samego komputera uwierzytelnia się automatycznie. Szczegóły znajdziesz w dokumentacji [Remote Access](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcjonalnie: Połącz kanał komunikacji

Gdy bramka działa, możesz połączyć się ze swoim lokalnym agentem z dowolnego urządzenia. Wybierz opcję odpowiednią dla Twojej konfiguracji. OpenClaw obsługuje [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) i inne kanały – pełną listę znajdziesz na stronie [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opcja A: Discord

Discord wymaga serwera, na którym **masz uprawnienia administratora**, aby dodać bota. Jeśli współdzielisz serwery, ale żadnego nie posiadasz, skorzystaj zamiast tego z Opcji B (Telegram).

#### Utwórz konto i serwer Discord

Jeśli nie masz konta Discord, zarejestruj się na stronie [discord.com](https://discord.com). Potrzebujesz również serwera, na którym jesteś administratorem – utwórz go, klikając ikonę **+** na pasku bocznym Discorda i wybierając **Create My Own**. Prywatny serwer w zupełności wystarczy.

#### Utwórz aplikację i bota Discord

1. Przejdź do [Discord Developer Portal](https://discord.com/developers/applications) i kliknij **New Application**. Nadaj mu nazwę (np. „openclaw-bot”).
2. Na pasku bocznym kliknij **Bot**. Ustaw nazwę użytkownika bota.
3. Nadal na stronie Bot przewiń do sekcji **Privileged Gateway Intents** i włącz:
   - **Message Content Intent** (wymagane)
   - **Server Members Intent** (zalecane)
4. Przewiń z powrotem w górę i kliknij **Reset Token**, aby wygenerować token bota. Skopiuj go.

#### Dodaj bota do swojego serwera

1. Na pasku bocznym kliknij **OAuth2/ URL Generator**.
2. W sekcji **Scopes** włącz `bot` oraz `applications.commands`.
3. W sekcji **Bot Permissions** włącz: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Skopiuj wygenerowany adres URL, wklej go w przeglądarce, wybierz swój serwer i potwierdź. Bot powinien teraz pojawić się na liście członków serwera.

#### Zbierz swoje identyfikatory

Włącz tryb dewelopera w Discordzie (**User Settings/ Advanced/ Developer Mode**), a następnie:
- Kliknij prawym przyciskiem myszy ikonę swojego serwera: **Copy Server ID**
- Kliknij prawym przyciskiem myszy swój własny awatar: **Copy User ID**

#### Zezwól na wiadomości prywatne od członków serwera

Kliknij prawym przyciskiem myszy ikonę serwera/ **Privacy Settings**/ włącz opcję **Direct Messages**. Umożliwia to botowi wysyłanie do Ciebie wiadomości prywatnych, co jest wymagane w kroku parowania.

#### Skonfiguruj OpenClaw dla Discorda

Zapisz token bota jako zmienną środowiskową, a następnie utwórz pojedynczy plik poprawek (patch), który włącza Discorda, odwołuje się do tokenu i dodaje Twój serwer do listy dozwolonych. Zastąp `<server_id>` i `<user_id>` identyfikatorami zebranymi powyżej.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **Nie polegaj na proszeniu agenta o skonfigurowanie tego.** Gdy sandboxing jest włączony, agent nie może zapisywać do pliku `~/.openclaw/openclaw.json` z wnętrza sandboksa – zamiast tego użyj powyższych poleceń CLI na hoście.

Uruchom ponownie bramkę, aby uwzględniła nową konfigurację kanału:

```bash
openclaw gateway run --bind loopback --port 18789
```

W ciągu kilku sekund w danych wyjściowych bramki powinieneś zobaczyć komunikat `logged in to discord as <bot-name>`.
#### Sparuj swoje konto Discord

Wyślij wiadomość do bota na Discordzie. Bot odpowie krótkim kodem parowania.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Zatwierdź go na maszynie, na której działa OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Kody parowania wygasają po godzinie.

Możesz teraz rozmawiać ze swoim agentem bezpośrednio z Discorda i przekazywać zadania do swojego lokalnego sprzętu.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opcja B: Telegram

Telegram jest dla większości użytkowników prostszy niż Discord, nie wymaga serwera ani uprawnień administratora.

#### Utwórz bota Telegram

1. Otwórz Telegram i wyślij wiadomość do **@BotFather**.
2. Wyślij `/newbot` i postępuj zgodnie z instrukcjami. Zapisz token bota, który otrzymasz.

#### Skonfiguruj OpenClaw dla Telegramu

Zapisz token jako zmienną środowiskową:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Dodaj konfigurację kanału do `~/.openclaw/openclaw.json` (lub zaktualizuj ją za pomocą panelu):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

Uruchom ponownie bramę, a następnie wyślij swojemu botowi dowolną wiadomość w Telegramie. Zatwierdź parowanie:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Kody parowania wygasają po godzinie. Możesz teraz rozmawiać ze swoim agentem przez wiadomości prywatne w Telegramie.

---

## Kolejne kroki

Skoro Twój agent może teraz otrzymywać polecenia z telefonu i działać na Twojej lokalnej maszynie, oto trzy kierunki warte zbadania:

1. **Podsumowanie rynku akcji**: Zaplanuj, aby OpenClaw pobierał dane z interfejsów API instytucji finansowych w stałych odstępach czasu, podsumowywał dzienne zmiany za pomocą Twojego lokalnego modelu i wysyłał codzienne zestawienie na Twój telefon każdego ranka wybranym kanałem.

2. **Monitor dostrajania modeli**: Uruchom zdalnie zadanie treningowe przez Telegram lub Discord, a następnie poleć agentowi śledzić log treningu i przekazywać na Twój telefon okresowe informacje o wartościach straty, wykorzystaniu GPU i zajętości dysku. Jeśli proces się zatrzyma lub wystąpi skok zużycia VRAM, dowiesz się o tym od razu, bez konieczności bycia przy komputerze.

3. **IOT z lokalnym modelem VLM**: Skieruj kamerę na drzwi wejściowe, uruchom model wizyjny na Lemonade i pozwól OpenClaw analizować klatki na żądanie lub po wystąpieniu zdarzenia wyzwalającego. Zapytaj „czy dzisiaj przyszły jakieś paczki?” z telefonu i otrzymaj konkretną odpowiedź z Twojego własnego sprzętu.

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