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

[**OpenClaw**](https://openclaw.ai/) to autonomiczny agent AI, który potrafi pisać i uruchamiać kod, zarządzać plikami oraz realizować złożone, wieloetapowe zadania w Twoim imieniu. W przeciwieństwie do asystenta czatu, który jedynie odpowiada na pytania, OpenClaw podejmuje rzeczywiste działania w Twoim systemie, co oznacza, że potrzebuje szybkiego i wydajnego backendu AI, zdolnego nadążyć za wymagającą pętlą agenta.

[**Lemonade Server**](https://lemonade-server.ai/) jest właśnie takim backendem. To otwartoźródłowy lokalny serwer wnioskowania, który uruchamia modele GenAI bezpośrednio na Twoim sprzęcie i udostępnia je poprzez standardowe w branży API OpenAI.

Razem tworzą w pełni lokalny stos agenta AI: Lemonade obsługuje wnioskowanie modelu, a OpenClaw zapewnia pętlę agenta, która zamienia wyniki modelu w rzeczywiste działania.

> **Zanim przejdziesz dalej:** OpenClaw jest wysoce autonomicznym agentem AI. Nadanie dowolnemu agentowi AI dostępu do Twojego systemu może prowadzić do nieprzewidywalnych lub niezamierzonych rezultatów. Kontynuuj tylko wtedy, gdy rozumiesz te ryzyka i akceptujesz działanie autonomicznego oprogramowania w Twoim imieniu.

---

## Czego się nauczysz

Po ukończeniu tego przewodnika będziesz w stanie:

- Poznać **Lemonade Server**
- **Zainstalować OpenClaw** i **skonfigurować go do korzystania z Lemonade Server** jako backendu AI.
- **Uruchomić bramkę (gateway) OpenClaw** i potwierdzić, że Twój agent jest gotowy do pracy.
- **Połączyć kanał komunikacji** (Discord lub Telegram), aby móc rozmawiać ze swoim agentem z dowolnego urządzenia.

---

<!-- @device:halo_box,halo,stx,krk -->
## Konfiguracja pamięci (Memory Configuration)

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacja wymaganego oprogramowania

<!-- @os:linux -->
- Komputer z systemem **Ubuntu 24.04+** lub kompatybilną dystrybucją Linuksa opartą na Debianie, z narzędziem `apt-get`
- Co najmniej **12 GB pamięci RAM** (zalecane 64 GB+ dla większych modeli)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (opcjonalnie, do piaskownicy OpenClaw)
- **~10–30 GB wolnego miejsca na dysku** na wagi modelu
<!-- @os:end -->

<!-- @os:windows -->
- Komputer z systemem **Windows 10/11**
- Co najmniej **12 GB pamięci RAM** (zalecane 64 GB+ dla większych modeli)
- **~10–30 GB wolnego miejsca na dysku** na wagi modelu
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (opcjonalnie, do piaskownicy OpenClaw)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:nodejs,openclaw,lemonade-models-qwen3-35b-a3b -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Pobierz i wczytaj zalecany model

Zalecanym modelem w tym przewodniku jest **Qwen3.6-35B-A3B-GGUF** od Unsloth — potężny model MoE z oknem kontekstu wynoszącym 263 tys. tokenów, dobrze dopasowany do obciążeń agentowych. Model ten wykorzystuje kwantyzację UD-Q4_K_XL. Pobierz go teraz:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Następnie wczytaj go z dużym oknem kontekstu i zapisz to ustawienie na przyszłość:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Domyślna długość kontekstu modelu wynosi 262 144 tokeny. Jeśli napotkasz błędy związane z brakiem pamięci (OOM), rozważ zmniejszenie okna kontekstu. Jednak ponieważ Qwen3.6 wykorzystuje rozszerzony kontekst do złożonych zadań, zalecamy utrzymanie długości kontekstu na poziomie co najmniej 128 tys. tokenów, aby zachować zdolności „myślenia”.

> **Wskazówka: wyłącz tryb myślenia dla szybszych odpowiedzi agenta:** Qwen3.6-35B-A3B domyślnie działa w trybie myślenia, co dodaje opóźnienie przed każdą odpowiedzią. W pętlach agentowych ten narzut szybko się kumuluje. Repozytorium [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) udostępnia gotową konfigurację wyłączającą tryb myślenia. Aby jej użyć, pobierz plik i zaimportuj go:
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

## Konfiguracja WSL

OpenClaw uruchamiamy wewnątrz WSL (zalecane) i łączymy go z Lemonade działającym natywnie w systemie Windows. Dzięki temu masz środowisko powłoki Linux dla OpenClaw, zachowując jednocześnie akcelerację GPU Lemonade po stronie Windows.

### Instalacja WSL i Ubuntu

Otwórz PowerShell jako administrator i zainstaluj jądro WSL:

```powershell
wsl --install --no-distribution
```

Następnie zainstaluj Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Włącz systemd w WSL

Uruchom to w terminalu Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Wyjdź z WSL i uruchom je ponownie:

```powershell
exit
wsl --shutdown
wsl
```

### Przekierowanie Lemonade z Windows do WSL

WSL2 działa w wirtualnej sieci. Lemonade w systemie Windows wiąże się z adresem `127.0.0.1`, do którego WSL nie ma bezpośredniego dostępu. Proxy portów w Windows przekazuje ruch z adresu IP bramy WSL do localhost w Windows.

**Znajdź adres IP bramy WSL** (uruchom wewnątrz WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodaj proxy portów** (uruchom w PowerShell jako administrator, zastępując `<WSL-Gateway-IP>` adresem IP bramy WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Uwaga: jeśli napotkasz błąd `netsh: command not found`, spróbuj użyć jawnej nazwy pliku wykonywalnego – `netsh.exe`

**Dodaj regułę zapory sieciowej** (ten sam podniesiony PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Zweryfikuj z poziomu WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Jeśli w poprzednim kroku wczytałeś już model Qwen3.6-35B-A3B-GGUF, powinieneś zobaczyć wynik JSON podobny do poniższego:

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

Reguła `netsh portproxy` przetrwa ponowne uruchomienia, ale adres IP bramy WSL może się zmienić po `wsl --shutdown` lub ponownym uruchomieniu. Gdy tak się stanie, proxy nadal wskazuje stary adres IP, a Lemonade staje się niedostępne z poziomu WSL. Jeśli tak się stanie, skorzystaj z jednej z poniższych opcji.

**Opcja 1 (zalecana) — Automatyczna naprawa mostu.** Aby uniknąć robienia tego ręcznie za każdym razem, użyj zaplanowanego zadania, które sprawdza most przy każdym uruchomieniu i zalogowaniu i odbudowuje go tylko wtedy, gdy adres IP bramy się zmienił. Zobacz [przewodnik automatycznej naprawy mostu Lemonade WSL](assets/RepairLemonadeWslBridge.md).


**Opcja 2 — Ręczna naprawa mostu.** Najpierw pobierz bieżący adres IP bramy WSL, uruchamiając to wewnątrz WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Skopiuj tę wartość; użyjesz jej w miejsce `<new-WSL-Gateway-IP>` poniżej.

Następnie w **podniesionym oknie PowerShell** (uruchom jako administrator) wypisz istniejące reguły, usuń tylko nieaktualną regułę Lemonade i dodaj nową z bieżącym adresem IP:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

W wynikach `show all` nieaktualna reguła Lemonade to wpis, którego adres połączenia to `127.0.0.1` na porcie `13305`; jego adres nasłuchu to Twój `<old-WSL-Gateway-IP>`. Usunięcie według tego adresu usuwa tylko tę regułę i pozostawia nietknięte wszystkie inne reguły port-proxy na Twoim komputerze.

Reguła zapory, którą dodałeś podczas konfiguracji, jest powiązana z portem `13305` (a nie z adresem IP), więc nadal działa i nie wymaga ponownego utworzenia.

> **Zalecenie:** Aby uniknąć problemów z bramą, zdecydowanie zalecamy następującą konfigurację powłoki:
> - **Polecenia Windows** powinny być wykonywane w **PowerShell**
> - **Polecenia dystrybucji WSL** powinny być wykonywane w **wierszu poleceń** (uruchomionym jako **Administrator**)

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

## Zainstaluj i skonfiguruj OpenClaw

### Zainstaluj OpenClaw
<!-- @os:windows -->
> Uruchom polecenia z tej sekcji w swoim **terminalu WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Flaga `--no-onboard` pomija interaktywnego kreatora konfiguracji, w następnym kroku skonfigurujesz backend modelu ręcznie, co daje precyzyjną kontrolę nad tym, który model i serwer są używane.

Otwórz nowy terminal i potwierdź instalację:

```bash
openclaw --version
```

> **Wskazówka:** Jeśli po instalacji widzisz `command not found`, dodaj globalny katalog bin npm do zmiennej PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Aby uczynić to trwałym, dodaj powyższą linię do swojego pliku `~/.bashrc` lub `~/.zshrc`.

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


### Skonfiguruj OpenClaw do korzystania z Lemonade

Uruchom nieinteraktywne wdrożenie OpenClaw.
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

To polecenie zapisuje konfigurację OpenClaw w `~/.openclaw/openclaw.json`.

> **Rozmiar okna kontekstu OpenClaw:** Kompaktowanie w OpenClaw uruchamia się, gdy `contextTokens > contextWindow − reserveTokens`. Domyślna wartość `reserveTokensFloor` to 20 000 tokenów — jest to próg minimalny, który nadpisuje `reserveTokens`, gdy jest niższy, więc dla każdego modelu z kontekstem poniżej ~37k wystąpi nieskończona pętla kompaktowania. Ustaw niski próg rezerwy i wyłącz dolny limit raz w swojej konfiguracji, a będzie on obowiązywał dla każdego modelu, bez konieczności dostrajania dla poszczególnych modeli:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` to *dolny limit* (minimalne zabezpieczenie), a nie sama rezerwa, ustawienie samego dolnego limitu nie ma efektu. `reserveTokensFloor: 0` wyłącza to zabezpieczenie, dzięki czemu niższa wartość `reserveTokens` zostaje zaakceptowana.
>
> **Kiedy to zastosować:** Użyj tej konfiguracji, jeśli efektywne okno kontekstu Twojego modelu jest poniżej ~37k, czy to dlatego, że model jest mały (np. 8k, 16k, 32k), czy dlatego, że celowo ograniczyłeś je do niższej wartości (np. ładując model 128k, ale ustawiając kontekst na 16k w Lemonade). Bez tego OpenClaw wpada w nieskończoną pętlę kompaktowania przy uruchomieniu.
>
> **Modele z dużym kontekstem przy pełnym kontekście:** Możesz całkowicie pominąć ten krok. Wartości domyślne działają dobrze, kompaktowanie uruchomi się na długo przed zapełnieniem okna, a model ma mnóstwo miejsca na generowanie długich odpowiedzi. Jeśli jednak to zastosujesz, miej na uwadze, że `reserveTokens: 4096` ogranicza długość odpowiedzi do ~4k tokenów, co może przerywać generowanie długich plików lub szczegółowych planów.
>
> **Gdzie to dodać:** Umieść blok `compaction` wewnątrz `agents.defaults` w swoim pliku `openclaw.json` (zazwyczaj w `~/.openclaw/openclaw.json`):
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
> Reszta konfiguracji (gateway, channels, models itd.) pozostaje bez zmian, trzeba dodać tylko klucz `compaction`.
### (Zalecane) Włącz sandboxing Docker

OpenClaw może kierować wszystkie operacje agenta na plikach i kodzie przez izolowany kontener Docker zamiast wykonywać je bezpośrednio na hoście. Ogranicza to zasięg działania każdej niezamierzonej operacji do sandboksa, pozostawiając system plików i sieć hosta nienaruszone.

Zbuduj obraz sandboksa raz (Docker musi być zainstalowany):

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

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
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

Kontenery sandboksa domyślnie **nie mają dostępu do sieci**. Zobacz [dokumentację referencyjną sandboksingu](https://docs.openclaw.ai/gateway/sandboxing), aby dowiedzieć się więcej o montowaniach wiązanych (bind mounts) i zastąpieniach ustawień sieciowych.

> #### Rozwiązywanie problemów: Odmowa uprawnień Docker
> 
> Jeśli podczas uruchamiania poleceń Docker pojawi się błąd „permission denied”:
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
> Następnie **zrestartuj** system.
> 
> **Szybka tymczasowa poprawka** (resetuje się po restarcie):
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

[Firecrawl](https://docs.firecrawl.dev/introduction) to samodzielnie hostowana usługa do crawlowania stron internetowych i ekstrakcji treści, która może pomóc ominąć te ograniczenia i w pełni wykorzystać potencjał automatyzacji OpenClaw. 

W tej konfiguracji OpenClaw działa jako zestaw kontenerów Docker zarządzanych przez Podman. Aby uprościć zarządzanie cyklem życia i automatyczne uruchamianie, rejestrujemy Firecrawl jako usługę `systemd` na poziomie użytkownika, która orkiestruje bazowy stos Podman Compose. Dzięki temu OpenClaw może uruchamiać gateway, zatrzymywać go i weryfikować usługę Firecrawl za pomocą standardowych poleceń `systemctl --user` zamiast bezpośredniej interakcji z kontenerami. 

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
Upewnij się, że nazwa pliku dokładnie odpowiada tej, którą utworzyłeś powyżej, a następnie uruchom:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Jeśli operacja się powiedzie, powinieneś zobaczyć następujący wynik:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` zawiera dowiązania symboliczne do usług skonfigurowanych do automatycznego uruchamiania.

### 2. Skonfiguruj Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) jest idealny dla tych, którzy potrzebują pełnej kontroli nad swoim środowiskiem scrapowania i przetwarzania danych, ale wiąże się to z dodatkowym nakładem pracy związanym z utrzymaniem i konfiguracją.

Zacznij od sklonowania repozytorium:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Utwórz plik `.env` w katalogu `/firecrawl`: 
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
Gdy to zostanie zrobione, pobierz plik Compose OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) i umieść go w katalogu głównym `/firecrawl`:

> Ta konwencja jest wymagana, aby `systemd` mógł poprawnie zlokalizować i uruchomić usługę, zgodnie z ustawieniem `WorkingDirectory=${HOME}/firecrawl`.

> Zawsze możesz rozszerzyć stos, dodając kolejne usługi Firecrawl w razie potrzeby. Pełną listę dostępnych usług znajdziesz w oficjalnym pliku [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Uruchom usługę OpenClaw za pośrednictwem Firecrawl 

Zanim przekażesz kontrolę `systemd`, sprawdź, czy wszystko działa poprawnie, uruchamiając stos ręcznie:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Jeśli wszystko jest poprawnie skonfigurowane, powinieneś zobaczyć uruchomiony kontener OpenClaw, a wynik polecenia w wierszu poleceń powinien wyglądać podobnie do tego:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Po zweryfikowaniu, przed kontynuowaniem zatrzymaj stos:
```bash
podman compose -f openclaw-compose.yaml down
```
Przed uruchomieniem usługi musisz upewnić się, że dla katalogu `firecrawl` oraz jego pliku `.env` ustawiono prawidłowego właściciela i uprawnienia. 
Jest to niezbędne, aby usługa mogła zapisać Twoje dane uwierzytelniające podczas uruchamiania.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Teraz, gdy wszystko zostało zweryfikowane, uruchom usługę za pomocą `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Akcje OpenClaw](https://docs.openclaw.ai/) są dostępne z poziomu interaktywnego kontenera, a Panel Web jest dostępny na tym samym hoście i porcie pod adresem http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Uzyskiwanie `OPENCLAW_GATEWAY_TOKEN`

Gdy usługa jest już uruchomiona, zauważysz nowy katalog `.openclaw` utworzony w Twoim katalogu domowym (~/.openclaw). Ten katalog jest domyślnie zablokowany, więc musisz go odblokować, aby odzyskać swój token gateway.

1. Przyznaj dostęp do katalogu:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Odczytaj swój token gateway:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Znajdź wartość `OPENCLAW_GATEWAY_TOKEN` w wyniku.

3. Otwórz panel gateway w przeglądarce pod adresem http://127.0.0.1:18789. Po wyświetleniu monitu wklej swój token, aby się uwierzytelnić.

Aby zatrzymać usługę, uruchom:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Uruchom bramkę OpenClaw (OpenClaw Gateway)

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

Aby otworzyć panel, uruchom to w drugim terminalu, gdy bramka nadal działa:

```bash
openclaw dashboard
```

Ponieważ bramka wiąże się z loopbackiem, panel uwierzytelnia się automatycznie po otwarciu z tej samej maszyny, nie jest wymagane wprowadzanie tokena ani zatwierdzanie urządzenia w przypadku dostępu lokalnego. Powinieneś zobaczyć panel OpenClaw z Twoim modelem Lemonade wymienionym jako aktywny backend.

> Jeśli włączyłeś sandboxing, możesz go zweryfikować, prosząc agenta o wykonanie `run hostname` z poziomu panelu. Jeśli zamiast nazwy hosta Twojej maszyny zobaczysz krótki identyfikator kontenera, sandbox działa poprawnie.

**Gratulacje, zbudowałeś w pełni lokalny stos agenta AI od podstaw.**

> **Potrzebujesz tokena bramki?** Uruchom `openclaw dashboard --no-open`, aby wyświetlić adres URL panelu z osadzonym tokenem (próbuje też skopiować go do schowka). Alternatywnie token znajduje się w `gateway.auth.token` w pliku `~/.openclaw/openclaw.json`.

**Dostęp do panelu z innego urządzenia (przez tunel SSH)**

Jeśli OpenClaw działa na zdalnej maszynie, możesz uzyskać dostęp do jego panelu z lokalnej maszyny przez tunel SSH. Tunel przekierowuje port bramki (`18789`), dzięki czemu lokalna przeglądarka może komunikować się ze zdalną bramką przez `127.0.0.1`.

1. Na swojej **lokalnej maszynie** połącz się ze zdalną maszyną raz i zaakceptuj monit o odcisk palca (fingerprint), aby host został dodany do znanych hostów:

   ```bash
   ssh user@<host-ip>
   ```

2. Nadal na swojej **lokalnej maszynie** otwórz tunel SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Uwaga:** Po wprowadzeniu hasła terminal nie wyświetla żadnych danych wyjściowych i wygląda, jakby się zawiesił. Jest to zachowanie zamierzone: flaga `-N` informuje SSH, aby nie uruchamiał żadnego zdalnego polecenia, więc po prostu utrzymuje tunel otwarty. Pozostaw ten terminal uruchomiony.

3. Na swojej **lokalnej maszynie** otwórz przeglądarkę i przejdź do `http://127.0.0.1:18789`.

4. Na **zdalnej maszynie** wyświetl token bramki i wklej go w przeglądarce, aby się zalogować:

   ```bash
   openclaw dashboard --no-open
   ```

   Wyświetli to adres URL panelu z osadzonym tokenem; skopiuj token, aby się zalogować. (Token jest również przechowywany w `gateway.auth.token` w pliku `~/.openclaw/openclaw.json`.)

> **Zatwierdzanie zdalnego urządzenia:** Gdy otworzysz panel z innej maszyny lub telefonu, przeglądarka może wyświetlić identyfikator żądania. Na **zdalnej maszynie** wyświetl listę oczekujących żądań:
> ```bash
> openclaw devices list
> ```
> Następnie zatwierdź pasujące żądanie:
> ```bash
> openclaw devices approve <requestId>
> ```
> Jest to wymagane tylko w przypadku urządzeń zdalnych lub dodatkowych; dostęp loopback z tej samej maszyny uwierzytelnia się automatycznie. Zobacz dokumentację [Remote Access](https://docs.openclaw.ai/gateway/remote), aby dowiedzieć się więcej.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcjonalnie: połącz kanał komunikacji

Gdy bramka działa, możesz dotrzeć do swojego lokalnego agenta z dowolnego urządzenia. Wybierz opcję, która pasuje do Twojej konfiguracji. OpenClaw obsługuje [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) oraz inne kanały, zobacz pełną listę na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opcja A: Discord

Discord wymaga serwera, na którym **masz dostęp administratora**, aby dodać bota. Jeśli uczestniczysz w serwerach, ale żadnego nie posiadasz, skorzystaj z Opcji B (Telegram).

#### Utwórz konto i serwer Discord

Jeśli nie masz konta Discord, zarejestruj się na [discord.com](https://discord.com). Potrzebujesz też serwera, na którym jesteś administratorem, utwórz go, klikając ikonę **+** na pasku bocznym Discord i wybierając **Create My Own**. Prywatny serwer jest wystarczający.

#### Utwórz aplikację i bota Discord

1. Przejdź do [Discord Developer Portal](https://discord.com/developers/applications) i kliknij **New Application**. Nadaj mu nazwę (np. „openclaw-bot”).
2. Na pasku bocznym kliknij **Bot**. Ustaw nazwę użytkownika dla bota.
3. Nadal na stronie Bot, przewiń do sekcji **Privileged Gateway Intents** i włącz:
   - **Message Content Intent** (wymagane)
   - **Server Members Intent** (zalecane)
4. Przewiń z powrotem do góry i kliknij **Reset Token**, aby wygenerować token bota. Skopiuj go.

#### Dodaj bota do swojego serwera

1. Na pasku bocznym kliknij **OAuth2/ URL Generator**.
2. W sekcji **Scopes** włącz `bot` oraz `applications.commands`.
3. W sekcji **Bot Permissions** włącz: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Skopiuj wygenerowany adres URL, wklej go w przeglądarce, wybierz swój serwer i potwierdź. Bot powinien teraz pojawić się na liście członków Twojego serwera.

#### Zbierz swoje identyfikatory

Włącz tryb deweloperski w Discordzie (**User Settings/ Advanced/ Developer Mode**), a następnie:
- Kliknij prawym przyciskiem myszy ikonę serwera: **Copy Server ID**
- Kliknij prawym przyciskiem myszy swój awatar: **Copy User ID**

#### Zezwól na wiadomości prywatne od członków serwera

Kliknij prawym przyciskiem myszy ikonę serwera/ **Privacy Settings**/ włącz **Direct Messages**. Umożliwia to botowi wysyłanie Ci wiadomości prywatnych, co jest wymagane w kroku parowania.

#### Skonfiguruj OpenClaw dla Discorda

Zapisz token swojego bota jako zmienną środowiskową, a następnie utwórz pojedynczy plik poprawek, który włącza Discord, odwołuje się do tokena i dodaje Twój serwer do listy dozwolonych. Zastąp `<server_id>` i `<user_id>` identyfikatorami zebranymi powyżej.

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

> **Nie polegaj na proszeniu agenta o skonfigurowanie tego.** Gdy sandboxing jest włączony, agent nie może zapisywać do `~/.openclaw/openclaw.json` z wnętrza sandboksa, użyj zamiast tego powyższych poleceń CLI na hoście.

Zrestartuj bramkę, aby uwzględniła nową konfigurację kanału:

```bash
openclaw gateway run --bind loopback --port 18789
```

W ciągu kilku sekund powinieneś zobaczyć `logged in to discord as <bot-name>` w danych wyjściowych bramki.
#### Połącz swoje konto Discord

Napisz do bota wiadomość prywatną na Discordzie. Odpowie krótkim kodem parowania.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Zatwierdź go na maszynie, na której działa OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Kody parowania wygasają po godzinie.

Teraz możesz rozmawiać ze swoim agentem bezpośrednio z Discorda i przekazywać zadania do swojego lokalnego sprzętu.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opcja B: Telegram

Telegram jest prostszy niż Discord dla większości użytkowników — nie wymaga serwera ani dostępu administracyjnego.

#### Utwórz bota Telegram

1. Otwórz Telegram i napisz wiadomość do **@BotFather**.
2. Wyślij `/newbot` i postępuj zgodnie z instrukcjami. Zapisz token bota, który otrzymasz.

#### Skonfiguruj OpenClaw dla Telegrama

Zapisz token jako zmienną środowiskową:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Dodaj konfigurację kanału do `~/.openclaw/openclaw.json` (lub wprowadź poprawkę przez panel):

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

Uruchom ponownie bramę, a następnie wyślij do swojego bota dowolną wiadomość na Telegramie. Zatwierdź parowanie:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Kody parowania wygasają po godzinie. Teraz możesz rozmawiać ze swoim agentem przez wiadomości prywatne na Telegramie.

---

## Kolejne kroki

Teraz, gdy twój agent może odbierać polecenia z telefonu i działać na twojej lokalnej maszynie, oto trzy kierunki warte zbadania:

1. **Podsumowanie rynku akcji**: Zaplanuj, aby OpenClaw pobierał dane z interfejsów API finansowych w stałych odstępach czasu, podsumowywał dzienne zmiany za pomocą twojego lokalnego modelu i wysyłał codzienny skrót na twój telefon każdego ranka za pośrednictwem wybranego kanału.

2. **Monitor dostrajania (fine-tuning)**: Uruchom zadanie trenowania zdalnie przez Telegram lub Discord, a następnie poproś agenta o śledzenie dziennika trenowania i cykliczne raportowanie wartości strat, wykorzystania GPU oraz zajętości dysku z powrotem na twój telefon. Jeśli proces się zatrzyma lub wystąpi skok zużycia VRAM, dowiesz się o tym natychmiast, bez konieczności siedzenia przy maszynie.

3. **IOT z lokalnym modelem VLM**: Skieruj kamerę na drzwi wejściowe, uruchom model wizyjny na Lemonade i poproś OpenClaw o analizę klatek na żądanie lub po wyzwoleniu triggera. Zapytaj „czy dzisiaj przyszły jakieś paczki?” ze swojego telefonu i uzyskaj bezpośrednią odpowiedź z własnego sprzętu.

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