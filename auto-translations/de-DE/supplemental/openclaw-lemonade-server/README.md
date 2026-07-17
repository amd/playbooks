<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# OpenClaw mit Lemonade Server als Backend ausführen

## Übersicht

[**OpenClaw**](https://openclaw.ai/) ist ein autonomer KI-Agent, der Code schreiben und ausführen, Dateien verwalten und komplexe mehrstufige Aufgaben in Ihrem Auftrag erledigen kann. Im Gegensatz zu einem Chat-Assistenten, der lediglich Fragen beantwortet, führt OpenClaw echte Aktionen auf Ihrem System aus – das bedeutet, es benötigt ein schnelles, leistungsfähiges KI-Backend, das mit einer anspruchsvollen Agent-Schleife mithalten kann.

[**Lemonade Server**](https://lemonade-server.ai/) ist dieses Backend. Es handelt sich um einen quelloffenen lokalen Inferenzserver, der GenAI-Modelle direkt auf Ihrer Hardware ausführt und sie über die branchenübliche OpenAI API bereitstellt.

Zusammen bilden sie einen vollständig lokalen KI-Agent-Stack: Lemonade übernimmt die Modellinferenz, und OpenClaw stellt die Agent-Schleife bereit, die Modellausgaben in echte Aktionen umwandelt.

> **Bevor Sie fortfahren:** OpenClaw ist ein hochgradig autonomer KI-Agent. Einem KI-Agenten Zugriff auf Ihr System zu gewähren kann zu unvorhersehbaren oder unbeabsichtigten Ergebnissen führen. Fahren Sie nur fort, wenn Sie die Risiken verstehen und damit einverstanden sind, dass autonome Software in Ihrem Auftrag handelt.

---

## Was Sie lernen werden

Am Ende dieses Playbooks werden Sie in der Lage sein:

- Mehr über **Lemonade Server** zu erfahren
- **OpenClaw zu installieren** und **es auf Lemonade Server** als KI-Backend auszurichten.
- Das **OpenClaw-Gateway zu starten** und zu bestätigen, dass Ihr Agent einsatzbereit ist.
- **Einen Kommunikationskanal zu verbinden** (Discord oder Telegram), damit Sie von jedem Gerät aus mit Ihrem Agenten chatten können.

---

## Speicherkonfiguration festlegen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Auf Software-Updates prüfen

<!-- @require:software-update -->
<!-- @device:end -->

## Software-Voraussetzungen installieren

<!-- @os:linux -->
- Ein PC mit **Ubuntu 24.04+** oder einer kompatiblen Debian-basierten Linux-Distribution mit `apt-get`
- Mindestens **12 GB RAM** (64 GB+ empfohlen für größere Modelle)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Optional, zur Sandbox-Isolierung von OpenClaw)

- **~10–30 GB freier Festplattenspeicher** für Modellgewichte
<!-- @os:end -->
<!-- @os:windows -->
- Ein PC mit **Windows 10/11**
- Mindestens **12 GB RAM** (64 GB+ empfohlen für größere Modelle)
- **~10–30 GB freier Festplattenspeicher** für Modellgewichte
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Optional, zur Sandbox-Isolierung von OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Das empfohlene Modell herunterladen und laden

Das für dieses Playbook empfohlene Modell ist **Qwen3.6-35B-A3B-GGUF** von Unsloth, ein leistungsstarkes MoE-Modell mit einem 263k-Token-Kontextfenster, das gut für Agent-Workloads geeignet ist. Dieses Modell verwendet UD-Q4_K_XL-Quantisierung. Laden Sie es jetzt herunter:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Laden Sie es dann mit einem großen Kontextfenster und speichern Sie diese Einstellung für zukünftige Ausführungen:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Das Modell hat eine Standard-Kontextlänge von 262.144 Tokens. Wenn Sie auf Out-of-Memory-Fehler (OOM) stoßen, sollten Sie das Kontextfenster verkleinern. Da Qwen3.6 jedoch den erweiterten Kontext für komplexe Aufgaben nutzt, empfehlen wir, eine Kontextlänge von mindestens 128K Tokens beizubehalten, um die Denkfähigkeiten zu erhalten.

> **Tipp: Denken für schnellere Agent-Antworten deaktivieren:** Qwen3.6-35B-A3B läuft standardmäßig im Denkmodus, was vor jeder Antwort zusätzliche Latenz verursacht. Bei Agent-Schleifen summiert sich dieser Overhead schnell. Das Repository [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) stellt eine fertige Konfiguration bereit, die das Denken deaktiviert. Um sie zu verwenden, laden Sie die Datei herunter und importieren Sie sie:
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

## WSL einrichten

Wir führen OpenClaw innerhalb von WSL (empfohlen) aus und verbinden es mit Lemonade, das nativ unter Windows läuft. Dies bietet Ihnen eine Linux-Shell-Umgebung für OpenClaw, während die GPU-Beschleunigung von Lemonade auf der Windows-Seite erhalten bleibt.

### WSL und Ubuntu installieren

Öffnen Sie PowerShell als Administrator und installieren Sie den WSL-Kernel:

```powershell
wsl --install --no-distribution
```

Installieren Sie dann Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### systemd in WSL aktivieren

Führen Sie dies im Ubuntu-Terminal aus:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Starten Sie WSL neu:

```powershell
wsl --shutdown
wsl
```

### Lemonade von Windows in WSL einbinden

WSL2 läuft in einem virtuellen Netzwerk. Lemonade unter Windows bindet an `127.0.0.1`, das WSL nicht direkt erreichen kann. Ein Windows-Port-Proxy leitet den Datenverkehr von der WSL-Gateway-IP an Windows-Localhost weiter.

**Finden Sie Ihre WSL-Gateway-IP** (innerhalb von WSL ausführen):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Fügen Sie den Port-Proxy hinzu** (in PowerShell als Administrator ausführen, ersetzen Sie `<WSL-Gateway-IP>` durch Ihre WSL-Gateway-IP):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Fügen Sie eine Firewall-Regel hinzu** (dieselbe erhöhte PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Überprüfen Sie aus WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Wenn Sie das Modell Qwen3.6-35B-A3B-GGUF im vorherigen Schritt bereits geladen haben, sollten Sie eine JSON-Ausgabe wie diese sehen:

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

> Die `netsh portproxy`-Regel überlebt Neustarts, aber die WSL-Gateway-IP kann sich nach `wsl --shutdown` ändern. Wenn Lemonade nach einem Neustart von WSL aus nicht mehr erreichbar ist, ermitteln Sie die aktualisierte Gateway-IP und aktualisieren Sie den Proxy mit dieser neuen IP.

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

## OpenClaw installieren und konfigurieren

### OpenClaw installieren
<!-- @os:windows -->
> Führen Sie die Befehle in diesem Abschnitt in Ihrem **WSL-Terminal** aus.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Das Flag `--no-onboard` überspringt den interaktiven Einrichtungsassistenten – Sie konfigurieren das Modell-Backend im nächsten Schritt manuell, was Ihnen genaue Kontrolle darüber gibt, welches Modell und welcher Server verwendet werden.

Öffnen Sie ein neues Terminal und bestätigen Sie die Installation:

```bash
openclaw --version
```

> **Tipp:** Wenn nach der Installation `command not found` angezeigt wird, fügen Sie das globale Bin-Verzeichnis von npm zu Ihrem PATH hinzu:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Um dies dauerhaft zu machen, fügen Sie die obige Zeile zu Ihrer `~/.bashrc`- oder `~/.zshrc`-Datei hinzu.

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


### OpenClaw für die Verwendung von Lemonade konfigurieren

Führen Sie das nicht-interaktive Onboarding von OpenClaw aus.
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

Dieser Befehl schreibt die Konfiguration von OpenClaw in `~/.openclaw/openclaw.json`.

> **Größenanpassung des OpenClaw-Kontextfensters:** Die Komprimierung von OpenClaw wird ausgelöst, wenn `contextTokens > contextWindow − reserveTokens`. Der Standard-`reserveTokensFloor` beträgt 20.000 Tokens – ein Mindestwert, der `reserveTokens` überschreibt, wenn dieser niedriger ist. Daher löst jeder Modellkontext unter ~37k eine endlose Komprimierungsschleife aus. Legen Sie einmalig in Ihrer Konfiguration eine niedrige Reserve fest und deaktivieren Sie den Mindestwert – dies gilt dann für jedes Modell, ohne modellspezifische Anpassungen:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` ist ein *Mindestwert* (Mindestschutz), nicht die Reserve selbst – nur den Mindestwert festzulegen hat keine Wirkung. `reserveTokensFloor: 0` deaktiviert den Schutz, sodass der niedrigere `reserveTokens`-Wert akzeptiert wird.
>
> **Wann dies anzuwenden ist:** Verwenden Sie diese Konfiguration, wenn das effektive Kontextfenster Ihres Modells unter ~37k liegt – entweder weil das Modell klein ist (z. B. 8k, 16k, 32k) oder weil Sie es absichtlich auf einen niedrigeren Wert begrenzt haben (z. B. ein 128k-Modell laden, aber den Kontext in Lemonade auf 16k setzen). Ohne diese Einstellung gerät OpenClaw beim Start in eine endlose Komprimierungsschleife.
>
> **Große-Kontext-Modelle bei vollem Kontext:** Sie können dies vollständig überspringen. Die Standardwerte funktionieren einwandfrei – die Komprimierung setzt ein, bevor das Fenster voll ist, und das Modell hat ausreichend Platz für lange Antworten. Wenn Sie es dennoch anwenden, beachten Sie, dass `reserveTokens: 4096` die Antwortlänge auf ~4k Tokens begrenzt, was die Generierung langer Dateien oder detaillierter Pläne abschneiden kann.
>
> **Wo dies hinzuzufügen ist:** Platzieren Sie den `compaction`-Block innerhalb von `agents.defaults` in Ihrer `openclaw.json` (normalerweise unter `~/.openclaw/openclaw.json`):
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
> Der Rest Ihrer Konfiguration (Gateway, Kanäle, Modelle usw.) bleibt unverändert – nur der `compaction`-Schlüssel muss hinzugefügt werden.

### (Empfohlen) Docker-Sandbox aktivieren

OpenClaw kann alle Datei- und Code-Operationen des Agenten durch einen isolierten Docker-Container leiten, anstatt sie direkt auf Ihrem Host auszuführen. Dies begrenzt den Wirkungsbereich unbeabsichtigter Aktionen auf die Sandbox und lässt Ihr Host-Dateisystem und -Netzwerk unberührt.

Erstellen Sie das Sandbox-Image einmalig (Docker muss installiert sein):

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

Führen Sie dies aus, um den `sandbox`-Schlüssel innerhalb des vorhandenen `agents.defaults`-Blocks in `~/.openclaw/openclaw.json` hinzuzufügen:

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

Sandbox-Container haben standardmäßig **keinen Netzwerkzugriff**. Weitere Informationen zu Bind-Mounts und Netzwerk-Overrides finden Sie in der [Sandboxing-Referenz](https://docs.openclaw.ai/gateway/sandboxing).

> #### Fehlerbehebung: Docker-Zugriff verweigert
> 
> Wenn Sie beim Ausführen von Docker-Befehlen „permission denied" erhalten:
> 
> **Schritt 1: Fügen Sie Ihren Benutzer zur Docker-Gruppe hinzu**
> 
> ```bash
> sudo groupadd docker                    # Gruppe erstellen, falls nötig
> sudo usermod -aG docker $USER           # Sich selbst zur Gruppe hinzufügen
> newgrp docker                           # Änderung aktivieren
> docker run hello-world                  # Testen
> ```
> 
> **Schritt 2: Wenn der Fehler weiterhin besteht, wenden Sie die dauerhafte Lösung an**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Starten Sie dann Ihr System **neu**.
> 
> **Schnelle temporäre Lösung** (wird nach dem Neustart zurückgesetzt):
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

### Das OpenClaw-Gateway starten

Das Gateway ist der OpenClaw-Prozess, der die Agent-Schleife verwaltet und das Dashboard bereitstellt:

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

Um das Dashboard zu öffnen, führen Sie dies in einem zweiten Terminal aus, während das Gateway noch läuft:

```bash
openclaw dashboard
```

Da das Gateway an Loopback gebunden ist, authentifiziert sich das Dashboard automatisch, wenn es vom selben Rechner aus geöffnet wird – keine Token-Eingabe oder Gerätegenehmigung ist für den lokalen Zugriff erforderlich. Sie sollten das OpenClaw-Dashboard sehen, mit Ihrem Lemonade-Modell als aktivem Backend aufgelistet.

> Wenn Sie Sandboxing aktiviert haben, können Sie es überprüfen, indem Sie den Agenten über das Dashboard bitten, `run hostname` auszuführen. Wenn Sie eine kurze Container-ID anstelle des Hostnamens Ihres Rechners sehen, funktioniert die Sandbox.

**Herzlichen Glückwunsch, Sie haben einen vollständig lokalen KI-Agent-Stack von Grund auf aufgebaut.**

> **Gateway-Token benötigt?** Führen Sie `openclaw dashboard --no-open` aus, um die Dashboard-URL mit eingebettetem Token auszugeben (es wird auch versucht, diese in die Zwischenablage zu kopieren). Alternativ befindet sich das Token unter `gateway.auth.token` in `~/.openclaw/openclaw.json`.
>
> **Ein Remote-Gerät genehmigen:** Wenn Sie das Dashboard von einem zweiten Gerät oder Telefon aus öffnen, zeigt der Browser eine Anfrage-ID an. Führen Sie auf dem Rechner, auf dem das Gateway läuft, Folgendes aus:
> ```bash
> openclaw devices approve <requestId>
> ```
> Dies ist nur für Remote- oder Sekundärgeräte erforderlich – der Loopback-Zugriff vom selben Rechner authentifiziert sich automatisch.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Optional: Einen Kommunikationskanal verbinden

Sobald das Gateway läuft, können Sie Ihren lokalen Agenten von jedem Gerät aus erreichen. Wählen Sie die Option, die zu Ihrer Einrichtung passt. OpenClaw unterstützt [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) und andere Kanäle – die vollständige Liste finden Sie unter [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Option A: Discord

Discord erfordert einen Server, auf dem **Sie Administratorzugriff** haben, um einen Bot hinzuzufügen. Wenn Sie Server teilen, aber keinen besitzen, verwenden Sie stattdessen Option B (Telegram).

#### Ein Discord-Konto und einen Server erstellen

Wenn Sie kein Discord-Konto haben, registrieren Sie sich unter [discord.com](https://discord.com). Sie benötigen außerdem einen Server, auf dem Sie Administrator sind – erstellen Sie einen, indem Sie auf das **+**-Symbol in der Discord-Seitenleiste klicken und **Eigenen erstellen** auswählen. Ein privater Server ist ausreichend.

#### Eine Discord-Anwendung und einen Bot erstellen

1. Gehen Sie zum [Discord Developer Portal](https://discord.com/developers/applications) und klicken Sie auf **New Application**. Geben Sie ihm einen Namen (z. B. „openclaw-bot").
2. Klicken Sie in der Seitenleiste auf **Bot**. Legen Sie einen Benutzernamen für den Bot fest.
3. Scrollen Sie auf der Bot-Seite zu **Privileged Gateway Intents** und aktivieren Sie:
   - **Message Content Intent** (erforderlich)
   - **Server Members Intent** (empfohlen)
4. Scrollen Sie wieder nach oben und klicken Sie auf **Reset Token**, um Ihr Bot-Token zu generieren. Kopieren Sie es.

#### Den Bot zu Ihrem Server hinzufügen

1. Klicken Sie in der Seitenleiste auf **OAuth2/ URL Generator**.
2. Aktivieren Sie unter **Scopes** `bot` und `applications.commands`.
3. Aktivieren Sie unter **Bot Permissions**: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopieren Sie die generierte URL, fügen Sie sie in Ihren Browser ein, wählen Sie Ihren Server aus und bestätigen Sie. Der Bot sollte nun in der Mitgliederliste Ihres Servers erscheinen.

#### Ihre IDs sammeln

Aktivieren Sie den Entwicklermodus in Discord (**Benutzereinstellungen/ Erweitert/ Entwicklermodus**), dann:
- Rechtsklick auf Ihr Server-Symbol: **Server-ID kopieren**
- Rechtsklick auf Ihren eigenen Avatar: **Benutzer-ID kopieren**

#### DMs von Server-Mitgliedern erlauben

Rechtsklick auf Ihr Server-Symbol/ **Datenschutzeinstellungen**/ **Direktnachrichten** aktivieren. Dies erlaubt dem Bot, Ihnen Direktnachrichten zu senden, was für den Kopplungsschritt erforderlich ist.

#### OpenClaw für Discord konfigurieren

Speichern Sie Ihr Bot-Token als Umgebungsvariable und erstellen Sie dann eine einzelne Patch-Datei, die Discord aktiviert, auf das Token verweist und Ihren Server auf die Zulassungsliste setzt. Ersetzen Sie `<server_id>` und `<user_id>` durch die oben gesammelten IDs.

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

> **Verlassen Sie sich nicht darauf, den Agenten darum zu bitten, dies zu konfigurieren.** Wenn Sandboxing aktiviert ist, kann der Agent nicht von innerhalb der Sandbox in `~/.openclaw/openclaw.json` schreiben – verwenden Sie stattdessen die obigen CLI-Befehle auf dem Host.

Starten Sie das Gateway neu, damit es die neue Kanal-Konfiguration übernimmt:

```bash
openclaw gateway run --bind loopback --port 18789
```

Innerhalb weniger Sekunden sollten Sie `logged in to discord as <bot-name>` in der Gateway-Ausgabe sehen.

#### Ihr Discord-Konto koppeln

Senden Sie dem Bot eine Direktnachricht in Discord. Er antwortet mit einem kurzen Kopplungscode.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Genehmigen Sie ihn auf dem Rechner, auf dem OpenClaw läuft:
```bash
openclaw pairing approve discord <CODE>
```

> Kopplungscodes laufen nach einer Stunde ab.

Sie können jetzt direkt über Discord mit Ihrem Agenten chatten und Aufgaben an Ihre lokale Hardware auslagern.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Option B: Telegram

Telegram ist für die meisten Benutzer einfacher als Discord – es erfordert keinen Server und keinen Administratorzugriff.

#### Einen Telegram-Bot erstellen

1. Öffnen Sie Telegram und schreiben Sie **@BotFather**.
2. Senden Sie `/newbot` und folgen Sie den Anweisungen. Speichern Sie das Bot-Token, das Sie erhalten.

#### OpenClaw für Telegram konfigurieren

Speichern Sie das Token als Umgebungsvariable:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Fügen Sie die Kanal-Konfiguration zu `~/.openclaw/openclaw.json` hinzu (oder patchen Sie sie über das Dashboard):

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

Starten Sie das Gateway neu und senden Sie Ihrem Bot dann eine beliebige Nachricht in Telegram. Genehmigen Sie die Kopplung:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Kopplungscodes laufen nach einer Stunde ab. Sie können jetzt über Telegram-Direktnachrichten mit Ihrem Agenten chatten.

---

## Nächste Schritte

Jetzt, da Ihr Agent Befehle von Ihrem Telefon empfangen und auf Ihrem lokalen Rechner handeln kann, sind hier drei Richtungen, die es wert sind, erkundet zu werden:

1. **Börsenmarkt-Zusammenfasser**: Planen Sie OpenClaw so, dass es in einem festen Intervall Daten von Finanz-APIs abruft, die Bewegungen des Tages mit Ihrem lokalen Modell zusammenfasst und jeden Morgen eine Zusammenfassung über Ihren gewählten Kanal auf Ihr Telefon sendet.

2. **Fine-Tuning-Monitor**: Starten Sie einen Trainingsauftrag aus der Ferne über Telegram oder Discord, und lassen Sie den Agenten dann das Trainingsprotokoll verfolgen und regelmäßig Verlustwerte, GPU-Auslastung und Festplattennutzung an Ihr Telefon melden. Wenn der Lauf ins Stocken gerät oder der VRAM ansteigt, erfahren Sie es sofort, ohne am Rechner sein zu müssen.

3. **IoT mit einem lokalen VLM**: Richten Sie eine Kamera auf Ihre Haustür, führen Sie ein Vision-Modell auf Lemonade aus und lassen Sie OpenClaw Frames auf Anfrage oder bei einem Auslöser analysieren. Fragen Sie „Sind heute Pakete angekommen?" von Ihrem Telefon und erhalten Sie eine direkte Antwort von Ihrer eigenen Hardware.