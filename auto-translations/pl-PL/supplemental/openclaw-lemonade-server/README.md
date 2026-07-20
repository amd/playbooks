<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Uruchamianie OpenClaw z Lemonade Server jako backendem

## Przegląd

[**OpenClaw**](https://openclaw.ai/) to autonomiczny agent AI, który potrafi pisać i uruchamiać kod, zarządzać plikami oraz realizować złożone, wieloetapowe zadania w Twoim imieniu. W przeciwieństwie do asystenta czatu, który jedynie odpowiada na pytania, OpenClaw wykonuje rzeczywiste działania w systemie, co oznacza, że potrzebuje szybkiego, wydajnego backendu AI, który nadąży za wymagającą pętlą agenta.

[**Lemonade Server**](https://lemonade-server.ai/) jest właśnie takim backendem. To open-source'owy lokalny serwer wnioskowania, który uruchamia modele GenAI bezpośrednio na Twoim sprzęcie i udostępnia je za pomocą standardowego w branży API OpenAI.

Razem tworzą w pełni lokalny stos agenta AI: Lemonade zajmuje się wnioskowaniem modelu, a OpenClaw zapewnia pętlę agenta, która zamienia wyniki modelu w rzeczywiste działania.

> **Zanim przejdziesz dalej:** OpenClaw jest wysoce autonomicznym agentem AI. Nadanie jakiemukolwiek agentowi AI dostępu do Twojego systemu może prowadzić do nieprzewidywalnych lub niezamierzonych skutków. Kontynuuj tylko wtedy, gdy rozumiesz związane z tym ryzyko i akceptujesz działanie autonomicznego oprogramowania w Twoim imieniu.

---

## Czego się nauczysz

Po zakończeniu tego przewodnika będziesz w stanie:

- Poznać **Lemonade Server**
- **Zainstalować OpenClaw** i **skonfigurować go tak, aby korzystał z Lemonade Server** jako backendu AI.
- **Uruchomić bramkę OpenClaw** i potwierdzić, że Twój agent jest gotowy do pracy.
- **Podłączyć kanał komunikacji** (Discord lub Telegram), aby móc rozmawiać z agentem z dowolnego urządzenia.

---

## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacja wymaganego oprogramowania

<!-- @os:linux -->
- PC z systemem **Ubuntu 24.04+** lub kompatybilną dystrybucją Linuksa opartą na Debianie z `apt-get`
- Co najmniej **12 GB pamięci RAM** (zalecane 64 GB+ dla większych modeli)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (opcjonalnie, do izolowania OpenClaw w sandboksie)

- **~10–30 GB wolnego miejsca na dysku** na wagi modeli
<!-- @os:end -->
<!-- @os:windows -->
- PC z systemem **Windows 10/11**
- Co najmniej **12 GB pamięci RAM** (zalecane 64 GB+ dla większych modeli)
- **~10–30 GB wolnego miejsca na dysku** na wagi modeli
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (opcjonalnie, do izolowania OpenClaw w sandboksie)
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

Zalecanym modelem dla tego przewodnika jest **Qwen3.6-35B-A3B-GGUF** od Unsloth — silny model typu MoE z 263-tysięcznym oknem kontekstu, który dobrze sprawdza się w obciążeniach związanych z pracą agentów. Ten model wykorzystuje kwantyzację UD-Q4_K_XL. Pobierz go teraz:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Następnie wczytaj go z dużym oknem kontekstu i zapisz to ustawienie na potrzeby kolejnych uruchomień:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model ma domyślną długość kontekstu wynoszącą 262 144 tokenów. Jeśli napotkasz błędy braku pamięci (OOM), rozważ zmniejszenie okna kontekstu. Ponieważ jednak Qwen3.6 wykorzystuje rozszerzony kontekst do realizacji złożonych zadań, zalecamy utrzymanie długości kontekstu na poziomie co najmniej 128K tokenów, aby zachować zdolności rozumowania.

> **Wskazówka: Wyłącz tryb myślenia dla szybszych odpowiedzi agenta:** Qwen3.6-35B-A3B domyślnie działa w trybie myślenia, co dodaje opóźnienie przed każdą odpowiedzią. W przypadku pętli agenta ten narzut szybko się kumuluje. Repozytorium [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) udostępnia gotową konfigurację wyłączającą tryb myślenia. Aby jej użyć, pobierz plik i zaimportuj go:
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

Uruchamiamy OpenClaw wewnątrz WSL (zalecane) i łączymy go z Lemonade działającym natywnie w systemie Windows. Dzięki temu masz środowisko powłoki Linux dla OpenClaw, zachowując jednocześnie akcelerację GPU Lemonade po stronie Windows.

### Instalacja WSL i Ubuntu

Otwórz PowerShell jako administrator i zainstaluj jądro WSL:

```powershell
wsl --install --no-distribution
```

Następnie zainstaluj Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Włączanie systemd w WSL

Uruchom to w terminalu Ubuntu:

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

WSL2 działa w wirtualnej sieci. Lemonade w systemie Windows nasłuchuje na `127.0.0.1`, czego WSL nie może osiągnąć bezpośrednio. Proxy portów systemu Windows przekazuje ruch z adresu IP bramy WSL do lokalnego hosta Windows.

**Znajdź adres IP bramy WSL** (uruchom wewnątrz WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodaj proxy portów** (uruchom w PowerShell jako administrator, zastępując `<WSL-Gateway-IP>` swoim adresem IP bramy WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Dodaj regułę zapory sieciowej** (w tym samym uprzywilejowanym oknie PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Zweryfikuj z poziomu WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Jeśli w poprzednim kroku wczytano już model Qwen3.6-35B-A3B-GGUF, powinieneś zobaczyć wynik JSON podobny do tego:

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

> Reguła `netsh portproxy` zachowuje ważność po restarcie, ale adres IP bramy WSL może się zmienić po wykonaniu `wsl --shutdown`. Jeśli po ponownym uruchomieniu Lemonade stanie się nieosiągalny z WSL, pobierz zaktualizowany adres IP bramy i zaktualizuj proxy o ten nowy adres.

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
> Polecenia w tej sekcji uruchamiaj wewnątrz terminala **WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Flaga `--no-onboard` pomija interaktywny kreator konfiguracji — backend modelu skonfigurujesz ręcznie w kolejnym kroku, co daje precyzyjną kontrolę nad tym, jaki model i serwer są używane.

Otwórz nowy terminal i potwierdź instalację:

```bash
openclaw --version
```

> **Wskazówka:** Jeśli po instalacji zobaczysz komunikat `command not found`, dodaj globalny katalog bin npm do swojej zmiennej PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Aby ustawienie to było trwałe, dodaj powyższą linię do pliku `~/.bashrc` lub `~/.zshrc`.

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
### Konfigurowanie OpenClaw do korzystania z Lemonade

Uruchom nieinteraktywny proces wdrażania OpenClaw.
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

> **Rozmiar okna kontekstu w OpenClaw:** Kompresja (compaction) w OpenClaw uruchamia się, gdy `contextTokens > contextWindow − reserveTokens`. Domyślna wartość `reserveTokensFloor` wynosi 20 000 tokenów — to dolny próg, który nadpisuje `reserveTokens`, gdy jest od niego niższy, więc każdy model z kontekstem poniżej ~37k spowoduje nieskończoną pętlę kompresji. Ustaw niski rezerwowany limit i wyłącz próg raz w swojej konfiguracji, a będzie on obowiązywał dla każdego modelu, bez konieczności ustawień per-model:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` to *próg* (minimalne zabezpieczenie), a nie sama rezerwa — ustawienie samego progu nie ma efektu. `reserveTokensFloor: 0` wyłącza to zabezpieczenie, dzięki czemu niższa wartość `reserveTokens` zostaje zaakceptowana.
>
> **Kiedy to zastosować:** Użyj tej konfiguracji, jeśli efektywne okno kontekstu Twojego modelu jest mniejsze niż ~37k — czy to dlatego, że model jest mały (np. 8k, 16k, 32k), czy dlatego, że celowo ograniczono je do niższej wartości (np. wczytując model 128k, ale ustawiając kontekst na 16k w Lemonade). Bez tego OpenClaw wpada w nieskończoną pętlę kompresji przy starcie.
>
> **Modele z dużym kontekstem przy pełnym oknie:** Możesz całkowicie pominąć tę konfigurację. Wartości domyślne działają dobrze — kompresja uruchomi się na długo przed zapełnieniem okna, a model będzie miał wystarczająco miejsca na generowanie długich odpowiedzi. Jeśli mimo to zastosujesz tę konfigurację, pamiętaj, że `reserveTokens: 4096` ogranicza długość odpowiedzi do ~4k tokenów, co może obcinać generowanie długich plików lub szczegółowych planów.
>
> **Gdzie to dodać:** Umieść blok `compaction` wewnątrz `agents.defaults` w swoim pliku `openclaw.json` (zwykle znajdującym się w `~/.openclaw/openclaw.json`):
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
> Reszta Twojej konfiguracji (gateway, kanały, modele itd.) pozostaje bez zmian — wystarczy dodać sam klucz `compaction`.

### (Zalecane) Włączenie sandboksingu Docker

OpenClaw może kierować wszystkie operacje agenta na plikach i kodzie przez izolowany kontener Docker, zamiast wykonywać je bezpośrednio na hoście. Ogranicza to zasięg ewentualnego niezamierzonego działania do sandboksa, pozostawiając system plików i sieć hosta nietknięte.

Zbuduj obraz sandboksa jednorazowo (Docker musi być zainstalowany):

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

Kontenery sandboksa domyślnie **nie mają dostępu do sieci**. Zobacz [dokumentację referencyjną sandboksingu](https://docs.openclaw.ai/gateway/sandboxing), aby dowiedzieć się więcej o montowaniu wiązań (bind mounts) i nadpisywaniu ustawień sieciowych.

> #### Rozwiązywanie problemów: brak uprawnień Docker
> 
> Jeśli podczas uruchamiania poleceń Docker pojawia się błąd „permission denied":
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
> **Krok 2: Jeśli błąd nadal występuje, zastosuj trwałe rozwiązanie**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Następnie **uruchom ponownie** system.
> 
> **Szybkie tymczasowe rozwiązanie** (resetuje się po restarcie):
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

### Uruchamianie bramy (Gateway) OpenClaw

Gateway to proces OpenClaw, który zarządza pętlą agenta i obsługuje panel (dashboard):

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

Aby otworzyć panel, uruchom poniższe polecenie w drugim terminalu, podczas gdy gateway nadal działa:

```bash
openclaw dashboard
```

Ponieważ gateway wiąże się z interfejsem loopback, panel automatycznie uwierzytelnia się po otwarciu z tej samej maszyny — nie jest wymagane wprowadzanie tokena ani zatwierdzanie urządzenia przy dostępie lokalnym. Powinieneś zobaczyć panel OpenClaw z Twoim modelem Lemonade wymienionym jako aktywny backend.

> Jeśli włączyłeś sandboksing, możesz to zweryfikować, prosząc agenta o wykonanie `run hostname` z poziomu panelu. Jeśli zamiast nazwy hosta Twojej maszyny zobaczysz krótki identyfikator kontenera, sandboks działa poprawnie.

**Gratulacje, zbudowałeś w pełni lokalny stos AI od podstaw.**

> **Potrzebujesz tokena bramy?** Uruchom `openclaw dashboard --no-open`, aby wyświetlić adres URL panelu z osadzonym tokenem (polecenie próbuje również skopiować go do schowka). Alternatywnie token znajduje się pod kluczem `gateway.auth.token` w pliku `~/.openclaw/openclaw.json`.
>
> **Zatwierdzanie zdalnego urządzenia:** Gdy otworzysz panel z drugiej maszyny lub telefonu, przeglądarka wyświetli identyfikator żądania. Na maszynie, na której działa gateway, uruchom:
> ```bash
> openclaw devices approve <requestId>
> ```
> Jest to potrzebne wyłącznie w przypadku urządzeń zdalnych lub dodatkowych — dostęp przez loopback z tej samej maszyny uwierzytelnia się automatycznie.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcjonalnie: Połączenie kanału komunikacji

Gdy gateway już działa, możesz łączyć się ze swoim lokalnym agentem z dowolnego urządzenia. Wybierz opcję odpowiadającą Twojej konfiguracji. OpenClaw obsługuje [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) i inne kanały — pełną listę znajdziesz na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opcja A: Discord

Discord wymaga serwera, na którym **masz uprawnienia administratora**, aby dodać bota. Jeśli współdzielisz serwery, ale żaden z nich nie należy do Ciebie, użyj zamiast tego Opcji B (Telegram).
#### Utwórz konto i serwer Discord

Jeśli nie masz konta Discord, zarejestruj się na [discord.com](https://discord.com). Potrzebujesz również serwera, na którym jesteś administratorem — utwórz go, klikając ikonę **+** na pasku bocznym Discord i wybierając **Create My Own**. Prywatny serwer w zupełności wystarczy.

#### Utwórz aplikację i bota Discord

1. Przejdź do [Discord Developer Portal](https://discord.com/developers/applications) i kliknij **New Application**. Nadaj mu nazwę (np. „openclaw-bot").
2. Na pasku bocznym kliknij **Bot**. Ustaw nazwę użytkownika bota.
3. Nadal na stronie Bot przewiń do **Privileged Gateway Intents** i włącz:
   - **Message Content Intent** (wymagane)
   - **Server Members Intent** (zalecane)
4. Przewiń z powrotem w górę i kliknij **Reset Token**, aby wygenerować token bota. Skopiuj go.

#### Dodaj bota do swojego serwera

1. Na pasku bocznym kliknij **OAuth2/ URL Generator**.
2. W sekcji **Scopes** włącz `bot` oraz `applications.commands`.
3. W sekcji **Bot Permissions** włącz: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Skopiuj wygenerowany adres URL, wklej go w przeglądarce, wybierz swój serwer i potwierdź. Bot powinien teraz pojawić się na liście członków twojego serwera.

#### Zbierz swoje identyfikatory

Włącz tryb dewelopera w Discord (**User Settings/ Advanced/ Developer Mode**), a następnie:
- Kliknij prawym przyciskiem myszy na ikonę swojego serwera: **Copy Server ID**
- Kliknij prawym przyciskiem myszy na swój awatar: **Copy User ID**

#### Zezwól na wiadomości prywatne od członków serwera

Kliknij prawym przyciskiem myszy na ikonę serwera/ **Privacy Settings**/ włącz **Direct Messages**. Umożliwia to botowi wysłanie ci wiadomości prywatnej, co jest wymagane na etapie parowania.

#### Skonfiguruj OpenClaw dla Discord

Zapisz token swojego bota jako zmienną środowiskową, a następnie utwórz pojedynczy plik patch, który włącza Discord, odwołuje się do tokenu i umieszcza twój serwer na białej liście. Zamień `<server_id>` i `<user_id>` na identyfikatory zebrane powyżej.

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

> **Nie polegaj na proszeniu agenta o skonfigurowanie tego.** Gdy sandboxing jest włączony, agent nie może zapisywać do `~/.openclaw/openclaw.json` z wewnątrz sandboksa — zamiast tego użyj powyższych poleceń CLI na hoście.

Uruchom ponownie bramę, aby uwzględniła nową konfigurację kanału:

```bash
openclaw gateway run --bind loopback --port 18789
```

W ciągu kilku sekund powinieneś zobaczyć `logged in to discord as <bot-name>` w danych wyjściowych bramy.

#### Sparuj swoje konto Discord

Wyślij wiadomość prywatną do bota w Discord. Odpowie krótkim kodem parowania.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Zatwierdź go na maszynie, na której działa OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Kody parowania wygasają po godzinie.

Możesz teraz rozmawiać ze swoim agentem bezpośrednio z Discord i przekazywać zadania do swojego lokalnego sprzętu.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opcja B: Telegram

Telegram jest prostszy niż Discord dla większości użytkowników — nie wymaga serwera ani uprawnień administratora.

#### Utwórz bota Telegram

1. Otwórz Telegram i wyślij wiadomość do **@BotFather**.
2. Wyślij `/newbot` i postępuj zgodnie z instrukcjami. Zapisz token bota, który otrzymasz.

#### Skonfiguruj OpenClaw dla Telegram

Zapisz token jako zmienną środowiskową:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Dodaj konfigurację kanału do `~/.openclaw/openclaw.json` (lub zastosuj patch przez panel):

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

Uruchom ponownie bramę, a następnie wyślij swojemu botowi dowolną wiadomość w Telegram. Zatwierdź parowanie:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Kody parowania wygasają po godzinie. Możesz teraz rozmawiać ze swoim agentem przez wiadomości prywatne w Telegram.

---

## Kolejne kroki

Teraz, gdy twój agent może odbierać polecenia z twojego telefonu i wykonywać działania na twojej lokalnej maszynie, oto trzy kierunki warte zbadania:

1. **Podsumowanie giełdy**: Zaplanuj, aby OpenClaw pobierał dane z API finansowych w stałych odstępach czasu, podsumowywał dzienne zmiany za pomocą twojego lokalnego modelu i wysyłał codzienne zestawienie na twój telefon każdego ranka poprzez wybrany kanał.

2. **Monitor fine-tuningu**: Uruchom zadanie treningowe zdalnie przez Telegram lub Discord, a następnie pozwól agentowi śledzić dziennik treningu i raportować okresowe wartości straty, wykorzystanie GPU oraz użycie dysku z powrotem na twój telefon. Jeśli trening się zatrzyma lub nastąpi skok zużycia VRAM, dowiesz się o tym natychmiast, bez konieczności bycia przy maszynie.

3. **IOT z lokalnym VLM**: Skieruj kamerę na drzwi wejściowe, uruchom model wizyjny na Lemonade i pozwól OpenClaw analizować klatki na żądanie lub po wystąpieniu wyzwalacza. Zapytaj „czy dzisiaj przyszły jakieś paczki?" ze swojego telefonu i otrzymaj konkretną odpowiedź od własnego sprzętu.