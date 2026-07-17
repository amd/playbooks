<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Uruchamianie OpenClaw z Lemonade Server jako backendem

## Przegląd

[**OpenClaw**](https://openclaw.ai/) to autonomiczny agent AI, który może pisać i uruchamiać kod, zarządzać plikami oraz realizować złożone zadania wieloetapowe w Twoim imieniu. W przeciwieństwie do asystenta czatu, który jedynie odpowiada na pytania, OpenClaw podejmuje rzeczywiste działania w Twoim systemie — co oznacza, że potrzebuje szybkiego i wydajnego backendu AI, który nadąży za wymagającą pętlą agenta.

[**Lemonade Server**](https://lemonade-server.ai/) jest właśnie takim backendem. To otwartoźródłowy lokalny serwer wnioskowania, który uruchamia modele GenAI bezpośrednio na Twoim sprzęcie i udostępnia je przez standardowy w branży interfejs API OpenAI.

Razem tworzą w pełni lokalny stos agenta AI: Lemonade obsługuje wnioskowanie modelu, a OpenClaw zapewnia pętlę agenta, która przekształca wyniki modelu w rzeczywiste działania.

> **Zanim przejdziesz dalej:** OpenClaw to wysoce autonomiczny agent AI. Przyznanie jakiemukolwiek agentowi AI dostępu do Twojego systemu może prowadzić do nieprzewidywalnych lub niezamierzonych skutków. Kontynuuj tylko wtedy, gdy rozumiesz związane z tym ryzyko i akceptujesz fakt, że autonomiczne oprogramowanie będzie działać w Twoim imieniu.

---

## Czego się nauczysz

Po ukończeniu tego poradnika będziesz potrafić:

- Dowiedzieć się więcej o **Lemonade Server**
- **Zainstalować OpenClaw** i **skierować go na Lemonade Server** jako backend AI.
- **Uruchomić bramę OpenClaw** i potwierdzić, że agent jest gotowy do pracy.
- **Podłączyć kanał komunikacyjny** (Discord lub Telegram), aby móc rozmawiać z agentem z dowolnego urządzenia.

---

## Konfigurowanie ustawień pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymagań wstępnych oprogramowania

<!-- @os:linux -->
- Komputer z systemem **Ubuntu 24.04+** lub zgodną dystrybucją Linux opartą na Debianie z `apt-get`
- Co najmniej **12 GB RAM** (zalecane 64 GB+ dla większych modeli)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (opcjonalnie, do izolacji OpenClaw w piaskownicy)

- **~10–30 GB wolnego miejsca na dysku** na wagi modelu
<!-- @os:end -->
<!-- @os:windows -->
- Komputer z systemem **Windows 10/11**
- Co najmniej **12 GB RAM** (zalecane 64 GB+ dla większych modeli)
- **~10–30 GB wolnego miejsca na dysku** na wagi modelu
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (opcjonalnie, do izolacji OpenClaw w piaskownicy)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Pobieranie i ładowanie zalecanego modelu

Zalecanym modelem do tego poradnika jest **Qwen3.6-35B-A3B-GGUF** od Unsloth — wydajny model MoE z oknem kontekstowym 263k tokenów, dobrze przystosowany do zadań agentowych. Model ten używa kwantyzacji UD-Q4_K_XL. Pobierz go teraz:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Następnie załaduj go z dużym oknem kontekstowym i zapisz to ustawienie na przyszłe uruchomienia:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model ma domyślną długość kontekstu wynoszącą 262 144 tokeny. Jeśli napotkasz błędy braku pamięci (OOM), rozważ zmniejszenie okna kontekstowego. Ponieważ jednak Qwen3.6 wykorzystuje rozszerzony kontekst do złożonych zadań, zalecamy utrzymanie długości kontekstu na poziomie co najmniej 128K tokenów, aby zachować możliwości myślenia.

> **Wskazówka: Wyłącz tryb myślenia dla szybszych odpowiedzi agenta:** Qwen3.6-35B-A3B domyślnie działa w trybie myślenia, co powoduje opóźnienie przed każdą odpowiedzią. W pętlach agentowych to opóźnienie szybko się kumuluje. Repozytorium [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) udostępnia gotową konfigurację wyłączającą tryb myślenia. Aby z niej skorzystać, pobierz plik i zaimportuj go:
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

Uruchamiamy OpenClaw wewnątrz WSL (zalecane) i łączymy go z Lemonade działającym natywnie w systemie Windows. Daje to środowisko powłoki Linux dla OpenClaw, przy jednoczesnym zachowaniu akceleracji GPU Lemonade po stronie Windows.

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

Uruchom ponownie WSL:

```powershell
wsl --shutdown
wsl
```

### Mostkowanie Lemonade z Windows do WSL

WSL2 działa w sieci wirtualnej. Lemonade w systemie Windows wiąże się z `127.0.0.1`, którego WSL nie może bezpośrednio osiągnąć. Proxy portów Windows przekazuje ruch z adresu IP bramy WSL do lokalnego hosta Windows.

**Znajdź adres IP bramy WSL** (uruchom wewnątrz WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodaj proxy portów** (uruchom w PowerShell jako administrator, zastępując `<WSL-Gateway-IP>` adresem IP bramy WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Dodaj regułę zapory** (ten sam podwyższony PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Zweryfikuj z poziomu WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Jeśli w poprzednim kroku załadowałeś już model Qwen3.6-35B-A3B-GGUF, powinieneś zobaczyć dane wyjściowe JSON podobne do poniższych:

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

> Reguła `netsh portproxy` przeżywa ponowne uruchomienia, ale adres IP bramy WSL może się zmienić po wykonaniu `wsl --shutdown`. Jeśli Lemonade stanie się nieosiągalne z WSL po ponownym uruchomieniu, pobierz zaktualizowany adres IP bramy i zaktualizuj proxy tym nowym adresem IP.

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

## Instalowanie i konfigurowanie OpenClaw

### Instalowanie OpenClaw
<!-- @os:windows -->
> Uruchom polecenia z tej sekcji wewnątrz **terminala WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Flaga `--no-onboard` pomija interaktywnego kreatora konfiguracji — backend modelu skonfigurujesz ręcznie w następnym kroku, co daje Ci precyzyjną kontrolę nad tym, który model i serwer są używane.

Otwórz nowy terminal i potwierdź instalację:

```bash
openclaw --version
```

> **Wskazówka:** Jeśli po instalacji widzisz komunikat `command not found`, dodaj globalny katalog bin npm do swojej zmiennej PATH:
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


### Konfigurowanie OpenClaw do używania Lemonade

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

To polecenie zapisuje konfigurację OpenClaw do pliku `~/.openclaw/openclaw.json`.

> **Rozmiar okna kontekstowego OpenClaw:** Kompakcja OpenClaw uruchamia się, gdy `contextTokens > contextWindow − reserveTokens`. Domyślna wartość `reserveTokensFloor` wynosi 20 000 tokenów — jest to dolna granica, która zastępuje `reserveTokens`, gdy jest niższa, więc każdy kontekst modelu poniżej ~37k spowoduje nieskończoną pętlę kompakcji. Ustaw niską rezerwę i wyłącz dolną granicę raz w konfiguracji, a będzie ona obowiązywać dla każdego modelu bez konieczności dostrajania per model:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` to *dolna granica* (minimalne zabezpieczenie), a nie sama rezerwa — ustawienie tylko dolnej granicy nie ma żadnego efektu. `reserveTokensFloor: 0` wyłącza zabezpieczenie, dzięki czemu niższa wartość `reserveTokens` jest akceptowana.
>
> **Kiedy to stosować:** Użyj tej konfiguracji, jeśli efektywne okno kontekstowe Twojego modelu jest poniżej ~37k — albo dlatego, że model jest mały (np. 8k, 16k, 32k), albo dlatego, że celowo ograniczyłeś je do niższej wartości (np. ładując model 128k, ale ustawiając kontekst na 16k w Lemonade). Bez tego OpenClaw wchodzi w nieskończoną pętlę kompakcji przy uruchomieniu.
>
> **Modele z dużym kontekstem przy pełnym kontekście:** Możesz to całkowicie pominąć. Domyślne ustawienia działają poprawnie — kompakcja uruchomi się na długo przed wypełnieniem okna, a model ma wystarczająco dużo miejsca na generowanie długich odpowiedzi. Jeśli jednak to zastosujesz, pamiętaj, że `reserveTokens: 4096` ogranicza długość odpowiedzi do ~4k tokenów, co może ucinać długie generowanie plików lub szczegółowe plany.
>
> **Gdzie to dodać:** Umieść blok `compaction` wewnątrz `agents.defaults` w pliku `openclaw.json` (zazwyczaj w `~/.openclaw/openclaw.json`):
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
> Reszta konfiguracji (brama, kanały, modele itp.) pozostaje bez zmian — należy dodać tylko klucz `compaction`.

### (Zalecane) Włączanie izolacji w piaskownicy Docker

OpenClaw może kierować wszystkie operacje agenta na plikach i kodzie przez izolowany kontener Docker, zamiast uruchamiać je bezpośrednio na hoście. Ogranicza to zasięg ewentualnych niezamierzonych działań do piaskownicy, pozostawiając system plików i sieć hosta nienaruszone.

Zbuduj obraz piaskownicy jednorazowo (Docker musi być zainstalowany):

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

Uruchom to, aby dodać klucz `sandbox` wewnątrz istniejącego bloku `agents.defaults` w pliku `~/.openclaw/openclaw.json`:

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

Kontenery piaskownicy domyślnie **nie mają dostępu do sieci**. Zapoznaj się z [dokumentacją piaskownicy](https://docs.openclaw.ai/gateway/sandboxing), aby uzyskać informacje o montowaniach bind i nadpisaniach sieci.

> #### Rozwiązywanie problemów: Odmowa dostępu do Docker
> 
> Jeśli podczas uruchamiania poleceń Docker pojawia się błąd „permission denied":
> 
> **Krok 1: Dodaj swojego użytkownika do grupy docker**
> 
> ```bash
> sudo groupadd docker                    # Utwórz grupę, jeśli potrzeba
> sudo usermod -aG docker $USER           # Dodaj siebie do grupy
> newgrp docker                           # Aktywuj zmianę
> docker run hello-world                  # Przetestuj
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

### Uruchamianie bramy OpenClaw

Brama to proces OpenClaw, który zarządza pętlą agenta i obsługuje panel sterowania:

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

Aby otworzyć panel sterowania, uruchom to w drugim terminalu, gdy brama jest nadal uruchomiona:

```bash
openclaw dashboard
```

Ponieważ brama wiąże się z pętlą zwrotną, panel sterowania automatycznie uwierzytelnia się po otwarciu z tego samego komputera — nie jest wymagane wprowadzanie tokenu ani zatwierdzanie urządzenia w przypadku dostępu lokalnego. Powinieneś zobaczyć panel sterowania OpenClaw z modelem Lemonade wymienionym jako aktywny backend.

> Jeśli włączyłeś izolację w piaskownicy, możesz ją zweryfikować, prosząc agenta o wykonanie polecenia `run hostname` z panelu sterowania. Jeśli zamiast nazwy hosta Twojego komputera zobaczysz krótki identyfikator kontenera, piaskownica działa poprawnie.

**Gratulacje — zbudowałeś w pełni lokalny stos agenta AI od podstaw.**

> **Potrzebujesz tokenu bramy?** Uruchom `openclaw dashboard --no-open`, aby wydrukować adres URL panelu sterowania z osadzonym tokenem (próbuje też skopiować go do schowka). Alternatywnie token znajduje się w `gateway.auth.token` w pliku `~/.openclaw/openclaw.json`.
>
> **Zatwierdzanie zdalnego urządzenia:** Gdy otworzysz panel sterowania z drugiego komputera lub telefonu, przeglądarka wyświetli identyfikator żądania. Na komputerze, na którym działa brama, uruchom:
> ```bash
> openclaw devices approve <requestId>
> ```
> Jest to wymagane tylko w przypadku zdalnych lub dodatkowych urządzeń — dostęp przez pętlę zwrotną z tego samego komputera uwierzytelnia się automatycznie.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcjonalnie: Podłączanie kanału komunikacyjnego

Gdy brama jest uruchomiona, możesz dotrzeć do swojego lokalnego agenta z dowolnego urządzenia. Wybierz opcję odpowiadającą Twojej konfiguracji. OpenClaw obsługuje [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) i inne kanały — pełną listę znajdziesz na stronie [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opcja A: Discord

Discord wymaga serwera, na którym **masz uprawnienia administratora**, aby dodać bota. Jeśli korzystasz ze wspólnych serwerów, ale nie jesteś ich właścicielem, użyj Opcji B (Telegram).

#### Tworzenie konta Discord i serwera

Jeśli nie masz konta Discord, zarejestruj się na stronie [discord.com](https://discord.com). Potrzebujesz również serwera, na którym jesteś administratorem — utwórz go, klikając ikonę **+** na pasku bocznym Discord i wybierając **Utwórz własny**. Prywatny serwer jest odpowiedni.

#### Tworzenie aplikacji Discord i bota

1. Przejdź do [Portalu deweloperów Discord](https://discord.com/developers/applications) i kliknij **New Application**. Nadaj mu nazwę (np. „openclaw-bot").
2. Na pasku bocznym kliknij **Bot**. Ustaw nazwę użytkownika dla bota.
3. Nadal na stronie Bot przewiń do sekcji **Privileged Gateway Intents** i włącz:
   - **Message Content Intent** (wymagane)
   - **Server Members Intent** (zalecane)
4. Przewiń z powrotem do góry i kliknij **Reset Token**, aby wygenerować token bota. Skopiuj go.

#### Dodawanie bota do serwera

1. Na pasku bocznym kliknij **OAuth2/ URL Generator**.
2. W sekcji **Scopes** włącz `bot` i `applications.commands`.
3. W sekcji **Bot Permissions** włącz: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Skopiuj wygenerowany adres URL, wklej go w przeglądarce, wybierz swój serwer i potwierdź. Bot powinien teraz pojawić się na liście członków Twojego serwera.

#### Zbieranie identyfikatorów

Włącz tryb dewelopera w Discord (**Ustawienia użytkownika/ Zaawansowane/ Tryb dewelopera**), a następnie:
- Kliknij prawym przyciskiem myszy ikonę serwera: **Kopiuj ID serwera**
- Kliknij prawym przyciskiem myszy swój awatar: **Kopiuj ID użytkownika**

#### Zezwalanie na wiadomości bezpośrednie od członków serwera

Kliknij prawym przyciskiem myszy ikonę serwera/ **Ustawienia prywatności**/ włącz **Wiadomości bezpośrednie**. Umożliwia to botowi wysyłanie Ci wiadomości bezpośrednich, co jest wymagane w kroku parowania.

#### Konfigurowanie OpenClaw dla Discord

Zapisz token bota jako zmienną środowiskową, a następnie utwórz pojedynczy plik poprawki, który włącza Discord, odwołuje się do tokenu i umieszcza Twój serwer na liście dozwolonych. Zastąp `<server_id>` i `<user_id>` identyfikatorami zebranymi powyżej.

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

> **Nie polegaj na prośbie do agenta o skonfigurowanie tego.** Gdy izolacja w piaskownicy jest włączona, agent nie może zapisywać do `~/.openclaw/openclaw.json` z wnętrza piaskownicy — zamiast tego użyj powyższych poleceń CLI na hoście.

Uruchom ponownie bramę, aby odebrała nową konfigurację kanału:

```bash
openclaw gateway run --bind loopback --port 18789
```

W ciągu kilku sekund w danych wyjściowych bramy powinieneś zobaczyć komunikat `logged in to discord as <bot-name>`.

#### Parowanie konta Discord

Wyślij wiadomość bezpośrednią do bota w Discord. Odpowie krótkim kodem parowania.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Zatwierdź go na komputerze z uruchomionym OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Kody parowania wygasają po jednej godzinie.

Możesz teraz rozmawiać z agentem bezpośrednio z Discord i zlecać zadania do wykonania na lokalnym sprzęcie.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opcja B: Telegram

Telegram jest prostszy niż Discord dla większości użytkowników — nie wymaga serwera ani uprawnień administratora.

#### Tworzenie bota Telegram

1. Otwórz Telegram i napisz do **@BotFather**.
2. Wyślij `/newbot` i postępuj zgodnie z instrukcjami. Zapisz token bota, który otrzymasz.

#### Konfigurowanie OpenClaw dla Telegram

Zapisz token jako zmienną środowiskową:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Dodaj konfigurację kanału do `~/.openclaw/openclaw.json` (lub zastosuj ją przez panel sterowania):

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

Uruchom ponownie bramę, a następnie wyślij botowi dowolną wiadomość w Telegram. Zatwierdź parowanie:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Kody parowania wygasają po jednej godzinie. Możesz teraz rozmawiać z agentem przez wiadomości bezpośrednie w Telegram.

---

## Kolejne kroki

Teraz, gdy Twój agent może odbierać polecenia z telefonu i działać na lokalnym komputerze, oto trzy kierunki warte eksploracji:

1. **Podsumowanie rynku akcji**: Zaplanuj, aby OpenClaw pobierał dane z finansowych API w stałych odstępach czasu, podsumowywał dzienne ruchy za pomocą lokalnego modelu i wysyłał codziennie rano skrót na Twój telefon przez wybrany kanał.

2. **Monitor dostrajania**: Zdalnie uruchom zadanie treningowe przez Telegram lub Discord, a następnie niech agent śledzi dziennik treningowy i raportuje na Twój telefon okresowe wartości straty, wykorzystanie GPU i użycie dysku. Jeśli przebieg się zatrzyma lub VRAM gwałtownie wzrośnie, dowiesz się o tym natychmiast, bez konieczności bycia przy komputerze.

3. **IoT z lokalnym VLM**: Skieruj kamerę na drzwi wejściowe, uruchom model wizyjny na Lemonade i niech OpenClaw analizuje klatki na żądanie lub po wyzwoleniu. Zapytaj „czy dzisiaj dotarły jakieś paczki?" ze swojego telefonu i uzyskaj bezpośrednią odpowiedź z własnego sprzętu.