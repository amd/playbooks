<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

# Uruchamianie Hermes Agent lokalnie z Lemonade Server

## Przegląd

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) to samodoskonalący się agent AI stworzony przez Nous Research. Posiada wbudowaną pętlę uczenia się, tworzy umiejętności na podstawie doświadczenia, buduje trwałą pamięć o tym, kim jesteś, między sesjami i może uruchamiać zaplanowane automatyzacje w Twoim imieniu. W przeciwieństwie do prostego asystenta czatu, Hermes podejmuje realne działania: uruchamia polecenia powłoki, zapisuje pliki, przegląda internet i deleguje równoległe strumienie zadań do subagentów.

[**Lemonade Server**](https://lemonade-server.ai/) to lokalny backend wnioskowania, który go zasila. Jest to serwer typu open-source, który uruchamia modele GenAI bezpośrednio na Twoim sprzęcie AMD i udostępnia je za pomocą standardowego w branży API OpenAI.

Razem tworzą w pełni lokalny stos agenta AI: Lemonade obsługuje wnioskowanie modelu na Twoim GPU, a Hermes zapewnia pętlę agenta, pamięć, umiejętności i bramę do przesyłania wiadomości.

> **Zanim przejdziesz dalej:** Hermes Agent to wysoce autonomiczny agent AI. Nadanie jakiemukolwiek agentowi AI dostępu do Twojego systemu może skutkować nieprzewidywalnymi lub niezamierzonymi wynikami. Kontynuuj tylko wtedy, gdy rozumiesz związane z tym ryzyko i akceptujesz działanie autonomicznego oprogramowania w Twoim imieniu.

---

## Czego się nauczysz

Po zakończeniu tego przewodnika będziesz w stanie:

- **Zainstalować Hermes Agent** i skierować go na **Lemonade Server** jako swój backend AI.
- **(Zalecane) Włączyć sandboxing Docker/Podman**, aby odizolować działania agenta od hosta.
- **Uruchomić bramę Hermes** i potwierdzić, że Twój agent jest gotowy.
- **Podłączyć kanał komunikacji** (Discord lub Telegram), aby móc rozmawiać ze swoim agentem z dowolnego urządzenia.

---

## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacja wymaganego oprogramowania

<!-- @os:linux -->
- Komputer PC z systemem **Ubuntu 24.04+** lub kompatybilną dystrybucją Linuksa opartą na Debianie z `apt-get`
- Co najmniej **12 GB pamięci RAM** (zalecane 64 GB+ dla większych modeli)
- **~10–30 GB wolnego miejsca na dysku** na wagi modelu
- [Podman](https://podman.io/docs/installation) (opcjonalnie, do sandboxingu Hermes Agent)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- Komputer PC z systemem **Windows 10/11**
- Co najmniej **12 GB pamięci RAM** (zalecane 64 GB+ dla większych modeli)
- **~10–30 GB wolnego miejsca na dysku** na wagi modelu
- Podman (opcjonalnie, do sandboxingu Hermes Agent). Zainstaluj wewnątrz WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman jest wstępnie zainstalowany na Halo Box i nie wymaga konfiguracji
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Pobierz i wczytaj zalecany model

Zalecanym modelem dla tego przewodnika jest **Qwen3.6-35B-A3B-GGUF** od Unsloth, silny model MoE z oknem kontekstowym 263k tokenów, który dobrze nadaje się do obciążeń agentowych. Ten model wykorzystuje kwantyzację UD-Q4_K_XL. Pobierz go teraz:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Następnie wczytaj go z dużym oknem kontekstowym i zapisz to ustawienie na przyszłe uruchomienia:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Model ma domyślną długość kontekstu 262 144 tokenów. Jeśli napotkasz błędy braku pamięci (OOM), rozważ zmniejszenie okna kontekstowego.

> **Wskazówka: Wyłącz tryb myślenia, aby przyspieszyć odpowiedzi agenta:** Qwen3.6-35B-A3B domyślnie działa w trybie myślenia, co dodaje opóźnienie przed każdą odpowiedzią. W przypadku pętli agenta ten narzut szybko się kumuluje. Repozytorium [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) zawiera gotową konfigurację, która wyłącza tryb myślenia. Aby jej użyć, pobierz plik i zaimportuj go:
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
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
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
model_id = "${hermes_model}"

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
  "model": "${hermes_model}",
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

Uruchamiamy Hermes Agent wewnątrz WSL i łączymy go z Lemonade działającym natywnie na Windows. Daje to środowisko powłoki Linux dla Hermes, przy jednoczesnym zachowaniu akceleracji GPU Lemonade po stronie Windows.

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

Zrestartuj WSL:

```powershell
wsl --shutdown
wsl
```

### Mostkowanie Lemonade z Windows do WSL

WSL2 działa w wirtualnej sieci. Lemonade na Windows wiąże się z `127.0.0.1`, do którego WSL nie ma bezpośredniego dostępu. Proxy portów Windows przekierowuje ruch z adresu IP bramy WSL do localhost Windows.

**Znajdź adres IP bramy WSL** (uruchom wewnątrz WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodaj proxy portu** (uruchom w PowerShell jako administrator, zastępując `<WSL-Gateway-IP>` swoim adresem IP bramy WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Dodaj regułę zapory sieciowej** (ten sam podniesiony PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Zweryfikuj z poziomu WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Jeśli wczytałeś już model Qwen3.6-35B-A3B-GGUF w poprzednim kroku, powinieneś zobaczyć wynik JSON zawierający listę wczytanego modelu.

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

> Reguła `netsh portproxy` przetrwa ponowne uruchomienia, ale adres IP bramy WSL może zmienić się po `wsl --shutdown`. Jeśli po restarcie Lemonade stanie się nieosiągalny z WSL, pobierz zaktualizowany adres IP bramy i zaktualizuj proxy o ten nowy adres.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## Instalacja Hermes Agent

<!-- @os:windows -->
> Uruchamiaj polecenia w tej sekcji wewnątrz swojego terminala **WSL**, chyba że zaznaczono inaczej.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Flaga `--skip-setup` pomija interaktywnego kreatora konfiguracji, dzięki czemu możesz ręcznie skonfigurować backend modelu w następnym kroku.

Przeładuj swoją powłokę:

```bash
source ~/.bashrc
```

Potwierdź instalację:

```bash
hermes --version
```

Uruchom autodiagnostykę, aby sprawdzić wszystkie zależności:

```bash
hermes doctor
```

> **Wskazówka:** Jeśli po instalacji zobaczysz komunikat `command not found`, dodaj Hermes do swojej zmiennej PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Aby to ustawienie było trwałe, dodaj powyższą linię do swojego pliku `~/.bashrc` lub `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## Konfigurowanie Hermes do korzystania z Lemonade

Hermes przechowuje konfigurację modelu w `~/.hermes/config.yaml`. Możesz albo skorzystać z interaktywnego selektora `hermes model`, albo zapisać konfigurację bezpośrednio.

### Opcja 1: Interaktywny selektor

<!-- @os:windows -->
> Uruchom poniższe polecenie w **terminalu WSL**.
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

Gdy pojawi się monit:

1. Wybierz **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** użyj adresu IP bramy WSL: uruchom `ip route show default | awk '{print $3}' | head -1` w WSL, aby go uzyskać, a następnie wpisz `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** wybierz `Qwen3.6-35B-A3B-GGUF` z listy
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (lub dowolna preferowana nazwa)

`hermes model` zapisuje zarówno aktywny wybór modelu, jak i nazwany wpis `custom_providers`, który przechowuje długość kontekstu razem z punktem końcowym. Wynik w `~/.hermes/config.yaml` wygląda następująco:

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### Opcja 2: Bezpośredni zapis konfiguracji

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

W terminalu WSL pobierz adres IP hosta Windows i zapisz konfigurację:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## (Zalecane) Włączanie izolacji Podman (sandboxing)

Hermes Agent może kierować wszystkie operacje agenta na powłoce i plikach przez izolowany kontener zamiast wykonywać je bezpośrednio na hoście. Ogranicza to zasięg ewentualnego niezamierzonego działania do środowiska izolowanego (sandbox), pozostawiając system plików i sieć hosta nietknięte.

Zbuduj lekki obraz środowiska izolowanego:

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Wejdź do terminala WSL:

```powershell
wsl -d Ubuntu-24.04
```

Następnie zbuduj lekki obraz środowiska izolowanego:

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Następnie skonfiguruj Hermes tak, aby korzystał z Podman jako środowiska uruchomieniowego kontenerów, i ustaw backend terminala:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` nadal ma wartość `docker`.
> To `HERMES_DOCKER_BINARY` informuje Hermes, aby jako środowisko uruchomieniowe używać Podman zamiast Docker.

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Hermes uruchomi teraz trwały kontener sandbox i będzie kierować przez niego wszystkie wywołania narzędzia `terminal` oraz narzędzi plikowych. Kontener istnieje przez cały czas trwania procesu Hermes, jest ponownie wykorzystywany przy wszystkich wywołaniach narzędzi i jest usuwany po zamknięciu Hermes.

> **Sprawdzanie, czy sandbox działa:** Uruchom Hermes (`hermes`) i poproś go o wykonanie `run hostname` - powinieneś zobaczyć krótki identyfikator kontenera zamiast nazwy hosta swojej maszyny. Możesz też poprosić go o wykonanie `rm -rf <path-to-a-dummy-file/folder>`: Hermes potwierdzi usunięcie, ale folder nadal będzie znajdował się na hoście. Polecenie zostało wykonane wewnątrz izolowanego `$HOME` kontenera, a nie Twojego.

> **Potrzebujesz silniejszej izolacji?** Hermes udostępnia również oficjalny obraz Docker (`nousresearch/hermes-agent`), który uruchamia cały proces agenta wewnątrz kontenera - bramę, narzędzia i wszystko inne. Szczegóły konfiguracji znajdziesz w [dokumentacji Hermes Docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker).

---

<!-- @os:linux -->
## (Zalecane) Integracja Hermes z usługami Firecrawl

Hermes może przeglądać strony internetowe i wyodrębniać z nich treści za pomocą wbudowanych narzędzi webowych. Jednak wiele nowoczesnych witryn korzysta z systemów wykrywania botów, które blokują proste żądania HTTP i zwracają strony z wyzwaniem (challenge page) zamiast rzeczywistej treści. W efekcie Hermes może nie być w stanie niezawodnie wyodrębnić informacji z takich witryn.

Aby przezwyciężyć to ograniczenie, [Firecrawl](https://docs.firecrawl.dev/introduction) udostępnia samodzielnie hostowaną usługę do przeszukiwania sieci i wyodrębniania treści, która potrafi ominąć te zabezpieczenia i odblokować pełny potencjał automatyzacji Hermes.

W tej konfiguracji Firecrawl działa jako zestaw kontenerów Docker zarządzanych za pomocą Podman. Aby uprościć zarządzanie cyklem życia i automatyczne uruchamianie, rejestrujemy Firecrawl jako usługę `systemd` na poziomie użytkownika, która zarządza bazowym stosem Podman Compose. Dzięki temu Hermes może uruchamiać, zatrzymywać i weryfikować usługę Firecrawl za pomocą standardowych poleceń `systemctl --user`, zamiast bezpośrednio wchodzić w interakcję z kontenerami.

Dla uproszczenia cały proces podzieliliśmy na cztery kroki:

---

### 1. Rejestracja usługi systemowej
Przejdź do katalogu konfiguracyjnego systemd użytkownika:
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
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

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

### 2. Konfigurowanie Firecrawl dla Twojej usługi

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) jest idealnym rozwiązaniem dla osób potrzebujących pełnej kontroli nad środowiskiem przeszukiwania i przetwarzania danych, kosztem dodatkowego nakładu pracy związanego z utrzymaniem i konfiguracją.

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
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> Ustaw `BULL_AUTH_KEY` na silny sekret, zwłaszcza w przypadku wdrożeń dostępnych z niezaufanych sieci.
### 3. Wdrażanie Hermes za pomocą Compose

Zanim przejdziesz dalej, upewnij się, że pobrano najnowszy obraz Docker Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Po wykonaniu tej czynności pobierz plik Compose Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) i umieść go w głównym katalogu `/firecrawl`:

> Ta konwencja jest wymagana, aby `systemd` mógł zlokalizować i uruchomić usługę poprawnie, zgodnie z ustawieniem `WorkingDirectory=${HOME}/firecrawl`.

> Zawsze możesz rozszerzyć stos, dodając kolejne usługi Firecrawl w razie potrzeby. Pełną listę dostępnych usług można znaleźć w oficjalnym pliku [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Uruchamianie usługi Hermes za pośrednictwem Firecrawl 

Zanim przekażesz kontrolę do `systemd`, sprawdź, czy wszystko działa poprawnie, uruchamiając stos ręcznie:
```bash
podman compose -f hermes-compose.yaml up -d
```
Jeśli wszystko zostało skonfigurowane prawidłowo, powinieneś zobaczyć uruchomiony kontener Hermes, a wynik w wierszu poleceń powinien wyglądać podobnie do tego:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Po sprawdzeniu zatrzymaj stos, zanim przejdziesz dalej:
```bash
podman compose -f hermes-compose.yaml down
```
Teraz, gdy wszystko zostało zweryfikowane, uruchom usługę za pośrednictwem `systemd`:
```bash
systemctl --user start firecrawl.service
```
[API Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) jest dostępne z poziomu interaktywnego kontenera, a Panel Web jest dostępny na tym samym hoście i porcie pod adresem http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Aby zatrzymać usługę, uruchom:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Uruchom interaktywną sesję CLI bezpośrednio: 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**Gratulacje, zbudowałeś w pełni lokalny stos agenta AI.**

### Panel Web

Hermes zawiera interfejs użytkownika oparty na przeglądarce do zarządzania konfiguracją, kluczami API, modelami, sesjami, pamięcią i zadaniami cron. Otwórz drugi terminal, gdy bramka lub CLI jest uruchomiona, i uruchom go za pomocą:

```bash
hermes dashboard
```

Spowoduje to uruchomienie lokalnego serwera i otworzenie `http://127.0.0.1:9119` w przeglądarce. Pełny opis funkcji znajdziesz w [dokumentacji panelu](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard).
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Opcjonalnie: Połącz kanał komunikacji

Gdy bramka jest uruchomiona, możesz połączyć się ze swoim lokalnym agentem z dowolnego urządzenia. Hermes obsługuje [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) i inne

---

### Discord

Discord wymaga serwera, na którym **masz uprawnienia administratora**, aby dodać bota. Jeśli współdzielisz serwery, ale żadnego nie posiadasz, użyj zamiast tego Telegramu.

#### Utwórz aplikację i bota Discord

1. Przejdź do [Discord Developer Portal](https://discord.com/developers/applications) i kliknij **New Application**. Nadaj mu nazwę (np. „hermes-bot”).
2. W panelu bocznym kliknij **Bot**. Ustaw nazwę użytkownika bota.
3. Nadal na stronie Bot przewiń do **Privileged Gateway Intents** i włącz:
   - **Message Content Intent** (wymagane)
   - **Server Members Intent** (zalecane)
4. Przewiń w górę i kliknij **Reset Token**, aby wygenerować token bota. Skopiuj go.

#### Dodaj bota do swojego serwera

1. W panelu bocznym kliknij **OAuth2 / URL Generator**.
2. W sekcji **Scopes** włącz `bot` oraz `applications.commands`.
3. W sekcji **Bot Permissions** włącz: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Skopiuj wygenerowany adres URL, wklej go w przeglądarce, wybierz swój serwer i potwierdź.

#### Zbierz swoje identyfikatory i zezwól na wiadomości prywatne

Włącz tryb dewelopera w Discord (**User Settings / Advanced / Developer Mode**), a następnie:
- Kliknij prawym przyciskiem myszy ikonę serwera: **Copy Server ID**
- Kliknij prawym przyciskiem myszy swój awatar: **Copy User ID**

Kliknij prawym przyciskiem myszy ikonę serwera / **Privacy Settings** / włącz **Direct Messages**. Jest to wymagane do etapu parowania.

#### Skonfiguruj Hermes dla Discord

Dodaj poniższe do `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Następnie uruchom bramkę:

```bash
hermes gateway
```

Bot powinien pojawić się w Discord w ciągu kilku sekund. Wyślij mu wiadomość, prywatną (DM) lub na kanale, do którego ma dostęp.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Utwórz bota Telegram

1. Otwórz Telegram i napisz wiadomość do **@BotFather**.
2. Wyślij `/newbot` i postępuj zgodnie z instrukcjami. Zapisz podany token bota.

#### Skonfiguruj Hermes dla Telegram

Dodaj poniższe do `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Nie znasz swojego identyfikatora użytkownika Telegram?** Napisz wiadomość do [@userinfobot](https://t.me/userinfobot) w Telegramie, odpowie on podając Twój numeryczny identyfikator.

Następnie uruchom bramkę:

```bash
hermes gateway
```

Wyślij swojemu botowi dowolną wiadomość w Telegramie, aby przetestować. Możesz teraz rozmawiać ze swoim agentem za pomocą wiadomości prywatnych w Telegramie. Zobacz [pełny przewodnik konfiguracji Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram), aby poznać tryb webhook i zaawansowane opcje.

---

## Następne kroki

Teraz, gdy Twój agent może otrzymywać polecenia z telefonu i działać na Twoim lokalnym komputerze, oto trzy kierunki warte dalszego zbadania:

1. **Automatyczny przegląd badań**: Zaplanuj, aby Hermes każdego ranka przeszukiwał sieć w poszukiwaniu interesujących Cię tematów, podsumowywał wyniki za pomocą Twojego lokalnego modelu i wysyłał przegląd na Twój telefon za pośrednictwem Telegramu lub Discord, wszystko działające na Twoim własnym sprzęcie, bez kosztów chmury.

2. **Przegląd kodu na żądanie**: Wskaż Hermes repozytorium GitHub, poproś go o przegląd otwartych pull requestów i niech opublikuje komentarze lub podsumowanie z powrotem na Twoim czacie. Dzięki backendowi terminala Docker wszystkie operacje git są wykonywane wewnątrz sandboxa, dzięki czemu Twój host pozostaje czysty.

3. **Lokalny asystent plików**: Daj Hermes dostęp do katalogu roboczego i poproś go o organizowanie, zmienianie nazw, podsumowywanie lub przekształcanie plików na żądanie z telefonu. Ponieważ backend terminala Docker ogranicza wszystkie operacje zapisu do przestrzeni roboczej sandboxa, przypadkowe destrukcyjne operacje są ograniczone.