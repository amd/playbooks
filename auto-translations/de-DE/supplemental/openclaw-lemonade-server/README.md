<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

# OpenClaw mit Lemonade Server als Backend ausführen

## Übersicht

[**OpenClaw**](https://openclaw.ai/) ist ein autonomer KI-Agent, der Code schreiben und ausführen, Dateien verwalten und komplexe, mehrstufige Aufgaben in Ihrem Auftrag erledigen kann. Im Gegensatz zu einem Chat-Assistenten, der nur Fragen beantwortet, führt OpenClaw echte Aktionen auf Ihrem System aus, was bedeutet, dass ein schnelles, leistungsfähiges KI-Backend erforderlich ist, das mit einer anspruchsvollen Agenten-Schleife Schritt halten kann.

[**Lemonade Server**](https://lemonade-server.ai/) ist dieses Backend. Es handelt sich um einen quelloffenen lokalen Inferenzserver, der GenAI-Modelle direkt auf Ihrer Hardware ausführt und sie über die branchenübliche OpenAI-API bereitstellt.

Gemeinsam bilden sie einen vollständig lokalen KI-Agenten-Stack: Lemonade übernimmt die Modellinferenz, und OpenClaw stellt die Agenten-Schleife bereit, die Modellausgaben in echte Aktionen umsetzt.

> **Bevor Sie fortfahren:** OpenClaw ist ein hochgradig autonomer KI-Agent. Einem KI-Agenten Zugriff auf Ihr System zu gewähren, kann zu unvorhersehbaren oder unbeabsichtigten Ergebnissen führen. Fahren Sie nur fort, wenn Sie die Risiken verstehen und damit einverstanden sind, dass autonome Software in Ihrem Auftrag handelt.

---

## Was Sie lernen werden

Am Ende dieses Playbooks können Sie Folgendes:

- Mehr über **Lemonade Server** erfahren
- **OpenClaw installieren** und **es auf Lemonade Server** als KI-Backend ausrichten.
- **Das OpenClaw-Gateway starten** und bestätigen, dass Ihr Agent einsatzbereit ist.
- **Einen Kommunikationskanal verbinden** (Discord oder Telegram), damit Sie von jedem Gerät aus mit Ihrem Agenten chatten können.

---

<!-- @device:halo_box,halo,stx,krk -->
## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen

<!-- @require:software-update -->
<!-- @device:end -->

## Installieren der Software-Voraussetzungen

<!-- @os:linux -->
- Ein PC mit **Ubuntu 24.04+** oder einer kompatiblen Debian-basierten Linux-Distribution mit `apt-get`
- Mindestens **12 GB RAM** (64 GB+ empfohlen für größere Modelle)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Optional, zum Sandboxing von OpenClaw)
- **~10–30 GB freier Speicherplatz** für Modellgewichte
<!-- @os:end -->

<!-- @os:windows -->
- Ein PC mit **Windows 10/11**
- Mindestens **12 GB RAM** (64 GB+ empfohlen für größere Modelle)
- **~10–30 GB freier Speicherplatz** für Modellgewichte
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Optional, zum Sandboxing von OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Herunterladen und Laden des empfohlenen Modells

Das für dieses Playbook empfohlene Modell ist **Qwen3.6-35B-A3B-GGUF** von Unsloth, ein leistungsstarkes MoE-Modell mit einem Kontextfenster von 263.000 Token, das sich gut für Agenten-Workloads eignet. Dieses Modell verwendet die UD-Q4_K_XL-Quantisierung. Laden Sie es jetzt herunter:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Laden Sie es dann mit einem großen Kontextfenster und speichern Sie diese Einstellung für zukünftige Ausführungen:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Das Modell hat standardmäßig eine Kontextlänge von 262.144 Token. Wenn Sie Out-of-Memory-Fehler (OOM) feststellen, sollten Sie das Kontextfenster verkleinern. Da Qwen3.6 jedoch erweiterten Kontext für komplexe Aufgaben nutzt, empfehlen wir, eine Kontextlänge von mindestens 128.000 Token beizubehalten, um die Denkfähigkeiten zu erhalten.

> **Tipp: Denkmodus deaktivieren für schnellere Agenten-Antworten:** Qwen3.6-35B-A3B läuft standardmäßig im Denkmodus, was vor jeder Antwort zusätzliche Latenz verursacht. Bei Agenten-Loops summiert sich dieser Mehraufwand schnell. Das [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json)-Repository bietet eine fertige Konfiguration, die den Denkmodus deaktiviert. Um sie zu verwenden, laden Sie die Datei herunter und importieren Sie sie:
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

Wir führen OpenClaw innerhalb von WSL aus (empfohlen) und verbinden es mit Lemonade, das nativ unter Windows läuft. Dies bietet Ihnen eine Linux-Shell-Umgebung für OpenClaw, während die GPU-Beschleunigung von Lemonade auf der Windows-Seite erhalten bleibt.

### WSL und Ubuntu installieren

Öffnen Sie PowerShell als Administrator und installieren Sie den WSL-Kernel:

```powershell
wsl --install --no-distribution
```

Installieren Sie anschließend Ubuntu:

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

Beenden Sie WSL und starten Sie es neu:

```powershell
exit
wsl --shutdown
wsl
```

### Lemonade von Windows in WSL überbrücken

WSL2 läuft in einem virtuellen Netzwerk. Lemonade unter Windows bindet an `127.0.0.1`, was WSL nicht direkt erreichen kann. Ein Windows-Portproxy leitet den Datenverkehr von der WSL-Gateway-IP an den Windows-Localhost weiter.

**Finden Sie Ihre WSL-Gateway-IP** (innerhalb von WSL ausführen):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Fügen Sie den Portproxy hinzu** (in PowerShell als Administrator ausführen, ersetzen Sie `<WSL-Gateway-IP>` durch Ihre WSL-Gateway-IP):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Hinweis: Wenn der Fehler `netsh: command not found` auftritt, versuchen Sie stattdessen den expliziten ausführbaren Namen zu verwenden - `netsh.exe`

**Fügen Sie eine Firewall-Regel hinzu** (dieselbe erhöhte PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Von WSL aus überprüfen**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Wenn Sie das Modell Qwen3.6-35B-A3B-GGUF bereits im vorherigen Schritt geladen haben, sollten Sie eine JSON-Ausgabe wie diese sehen:

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

#### Sorge dafür, dass die Bridge nach einem Neustart weiter funktioniert

Die `netsh portproxy`-Regel übersteht Neustarts, aber die WSL-Gateway-IP kann sich nach `wsl --shutdown` oder einem Neustart ändern. In diesem Fall zeigt der Proxy weiterhin auf die alte IP, und Lemonade ist aus WSL heraus nicht mehr erreichbar. Falls dies passiert, verwenden Sie eine der folgenden Optionen.

**Option 1 (empfohlen) — Die Bridge automatisch reparieren.** Damit Sie dies nicht jedes Mal manuell erledigen müssen, verwenden Sie eine geplante Aufgabe, die die Bridge bei jedem Start und jeder Anmeldung überprüft und nur dann neu aufbaut, wenn sich die Gateway-IP geändert hat. Siehe die [Anleitung zur automatischen Reparatur der Lemonade-WSL-Bridge](assets/RepairLemonadeWslBridge.md).


**Option 2 — Die Bridge manuell reparieren.** Ermitteln Sie zunächst die aktuelle WSL-Gateway-IP, indem Sie Folgendes innerhalb von WSL ausführen:

```bash
ip route show default | awk '{print $3}' | head -1
```

Kopieren Sie diesen Wert; Sie werden ihn weiter unten anstelle von `<new-WSL-Gateway-IP>` verwenden.

Listen Sie anschließend in einer **erhöhten PowerShell** (Als Administrator ausführen) die bestehenden Regeln auf, löschen Sie nur die veraltete Lemonade-Regel und fügen Sie eine neue mit der aktuellen IP hinzu:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

In der Ausgabe von `show all` ist die veraltete Lemonade-Regel der Eintrag, dessen Connect-Adresse `127.0.0.1` auf Port `13305` lautet; ihre Listen-Adresse ist Ihre `<old-WSL-Gateway-IP>`. Wenn Sie anhand dieser Adresse löschen, wird nur diese Regel entfernt, während alle anderen Portproxy-Regeln auf Ihrem Rechner unberührt bleiben.

Die Firewall-Regel, die Sie während der Einrichtung hinzugefügt haben, ist an Port `13305` gebunden (nicht an die IP), sodass sie weiterhin funktioniert und nicht neu erstellt werden muss.

> **Empfehlung:** Um Gateway-Probleme zu vermeiden, empfehlen wir dringend die folgende Shell-Konfiguration:
> - **Windows-Befehle** sollten in **PowerShell** ausgeführt werden
> - **WSL-Distro-Befehle** sollten in einer **Eingabeaufforderung** (als **Administrator** ausgeführt) ausgeführt werden

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

Das Flag `--no-onboard` überspringt den interaktiven Einrichtungsassistenten; Sie konfigurieren das Modell-Backend im nächsten Schritt manuell, was Ihnen präzise Kontrolle darüber gibt, welches Modell und welcher Server verwendet werden.

Öffnen Sie ein neues Terminal und bestätigen Sie die Installation:

```bash
openclaw --version
```

> **Tipp:** Wenn nach der Installation `command not found` angezeigt wird, fügen Sie das globale npm-Bin-Verzeichnis zu Ihrem PATH hinzu:
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

> **Größe des OpenClaw-Kontextfensters:** Die Kompaktierung von OpenClaw wird ausgelöst, wenn `contextTokens > contextWindow − reserveTokens`. Der Standardwert für `reserveTokensFloor` beträgt 20.000 Token, eine Untergrenze, die `reserveTokens` außer Kraft setzt, wenn dieser niedriger ist. Daher löst jeder Modellkontext unter ~37k eine unendliche Kompaktierungsschleife aus. Setzen Sie einmal in Ihrer Konfiguration eine niedrige Reserve und deaktivieren Sie die Untergrenze, dann gilt dies für jedes Modell, ohne dass eine modellspezifische Anpassung erforderlich ist:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` ist eine *Untergrenze* (Mindestschutz), nicht die Reserve selbst; nur die Untergrenze zu setzen hat keine Wirkung. `reserveTokensFloor: 0` deaktiviert den Schutz, sodass der niedrigere Wert von `reserveTokens` akzeptiert wird.
>
> **Wann Sie dies anwenden sollten:** Verwenden Sie diese Konfiguration, wenn das effektive Kontextfenster Ihres Modells unter ~37k liegt, entweder weil das Modell klein ist (z. B. 8k, 16k, 32k) oder weil Sie es absichtlich auf einen niedrigeren Wert begrenzt haben (z. B. ein 128k-Modell laden, aber den Kontext in Lemonade auf 16k setzen). Ohne dies gerät OpenClaw beim Start in eine unendliche Kompaktierungsschleife.
>
> **Große-Kontext-Modelle bei vollem Kontext:** Sie können dies vollständig überspringen. Die Standardwerte funktionieren einwandfrei, die Kompaktierung greift lange bevor das Fenster voll ist, und das Modell hat ausreichend Raum, um lange Antworten zu generieren. Falls Sie es dennoch anwenden, beachten Sie, dass `reserveTokens: 4096` die Antwortlänge auf ~4k Token begrenzt, was lange Dateigenerierungen oder detaillierte Pläne abschneiden kann.
>
> **Wo Sie dies hinzufügen:** Platzieren Sie den `compaction`-Block innerhalb von `agents.defaults` in Ihrer `openclaw.json` (üblicherweise unter `~/.openclaw/openclaw.json`):
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
> Der Rest Ihrer Konfiguration (Gateway, Kanäle, Modelle usw.) bleibt unverändert, nur der Schlüssel `compaction` muss hinzugefügt werden.
### (Empfohlen) Docker-Sandboxing aktivieren

OpenClaw kann alle Datei- und Codeoperationen des Agenten über einen isolierten Docker-Container leiten, anstatt sie direkt auf Ihrem Host auszuführen. Dies begrenzt den Wirkungsradius unbeabsichtigter Aktionen auf die Sandbox und lässt Ihr Host-Dateisystem und -Netzwerk unangetastet.

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

Führen Sie Folgendes aus, um den Schlüssel `sandbox` innerhalb des bestehenden Blocks `agents.defaults` in `~/.openclaw/openclaw.json` hinzuzufügen:

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

> #### Fehlerbehebung: Docker-Berechtigung verweigert
> 
> Wenn Sie beim Ausführen von Docker-Befehlen die Meldung „permission denied“ erhalten:
> 
> **Schritt 1: Fügen Sie Ihren Benutzer der Docker-Gruppe hinzu**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Schritt 2: Falls der Fehler weiterhin besteht, wenden Sie die dauerhafte Lösung an**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Führen Sie anschließend einen **Neustart** Ihres Systems durch.
> 
> **Schnelle temporäre Lösung** (wird nach einem Neustart zurückgesetzt):
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
## (Empfohlen) OpenClaw-Integration mit Firecrawl-Diensten

[Firecrawl](https://docs.firecrawl.dev/introduction) bietet einen selbst gehosteten Dienst zum Crawlen von Webinhalten und zur Inhaltsextraktion, der diese Herausforderungen umgehen und das volle Potenzial der OpenClaw-Automatisierung freisetzen kann.

In dieser Konfiguration läuft OpenClaw als eine Reihe von Docker-Containern, die mit Podman verwaltet werden. Um die Lebenszyklusverwaltung und den automatischen Start zu vereinfachen, registrieren wir Firecrawl als benutzerbasierten `systemd`-Dienst, der den zugrunde liegenden Podman-Compose-Stack orchestriert. Dadurch kann OpenClaw das Gateway starten, stoppen und den Firecrawl-Dienst mit den üblichen `systemctl --user`-Befehlen überprüfen, anstatt direkt mit den Containern zu interagieren.

Um es einfach zu halten, haben wir den gesamten Prozess in vier Schritte unterteilt:

---

### 1. Den Systemdienst registrieren
Navigieren Sie zum Konfigurationsverzeichnis des systemd-Benutzers:
```bash
cd ~/.config/systemd/user
```
Erstellen und öffnen Sie eine neue Datei mit dem Namen `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopieren Sie die folgende Konfiguration und fügen Sie sie ein:
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
An diesem Punkt wurde der Dienst definiert, aber noch nicht bei `systemd` registriert.
Stellen Sie sicher, dass der Dateiname genau mit dem oben erstellten übereinstimmt, und führen Sie dann Folgendes aus:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Bei Erfolg sollten Sie die folgende Ausgabe sehen:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` enthält symbolische Links zu Diensten, die so konfiguriert sind, dass sie automatisch starten.

### 2. Firecrawl konfigurieren

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) eignet sich ideal für alle, die volle Kontrolle über ihre Scraping- und Datenverarbeitungsumgebungen benötigen, dies geht jedoch mit zusätzlichem Wartungs- und Konfigurationsaufwand einher.

Beginnen Sie damit, das Repository zu klonen:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Erstellen Sie eine `.env`-Datei im Verzeichnis `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. OpenClaw mit Podman Compose bereitstellen

Stellen Sie zunächst sicher, dass Sie das neueste OpenClaw-Docker-Image gezogen haben:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Sobald dies erledigt ist, laden Sie die OpenClaw-Compose-Datei [openclaw-compose.yaml](assets/openclaw-compose.yaml) herunter und legen Sie sie im Stammverzeichnis `/firecrawl` ab:

> Diese Konvention ist erforderlich, damit `systemd` den Dienst gemäß der Angabe in `WorkingDirectory=${HOME}/firecrawl` korrekt finden und starten kann.

> Sie können den Stack jederzeit erweitern, indem Sie bei Bedarf weitere Firecrawl-Dienste hinzufügen. Die vollständige Liste der verfügbaren Dienste finden Sie in der offiziellen [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. OpenClaw-Dienst über Firecrawl starten 

Bevor Sie die Kontrolle an `systemd` übergeben, überprüfen Sie durch manuelles Ausführen des Stacks, dass alles ordnungsgemäß funktioniert:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Wenn alles korrekt konfiguriert ist, sollten Sie sehen, dass der OpenClaw-Container hochfährt, und Ihre Kommandozeilenausgabe sollte in etwa so aussehen:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Nach erfolgreicher Überprüfung fahren Sie den Stack wieder herunter, bevor Sie fortfahren:
```bash
podman compose -f openclaw-compose.yaml down
```
Bevor Sie den Dienst starten, müssen Sie sicherstellen, dass die korrekten Eigentümerrechte und Berechtigungen für das Verzeichnis `firecrawl` und dessen `.env`-Datei gesetzt sind.
Dies ist unerlässlich, damit der Dienst Ihre Anmeldedaten beim Start schreiben kann.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Nachdem nun alles überprüft wurde, starten Sie den Dienst über `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Die OpenClaw-Aktionen](https://docs.openclaw.ai/) sind aus dem interaktiven Container heraus zugänglich, und das Web-Dashboard ist auf demselben Host und Port unter http://127.0.0.1:18789 verfügbar.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Abrufen Ihres `OPENCLAW_GATEWAY_TOKEN`

Sobald der Dienst läuft, wird in Ihrem Home-Verzeichnis ein neues Verzeichnis `.openclaw` angelegt (~/.openclaw). Dieses Verzeichnis ist standardmäßig gesperrt, sodass Sie es entsperren müssen, um Ihr Gateway-Token abzurufen.

1. Gewähren Sie Zugriff auf das Verzeichnis:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Lesen Sie Ihr Gateway-Token aus:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Suchen Sie in der Ausgabe nach dem Wert `OPENCLAW_GATEWAY_TOKEN`.

3. Öffnen Sie das Gateway-Dashboard in Ihrem Browser unter http://127.0.0.1:18789. Fügen Sie Ihr Token ein, wenn Sie zur Authentifizierung aufgefordert werden.

Um den Dienst zu stoppen, führen Sie Folgendes aus:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Den OpenClaw-Gateway starten

Der Gateway ist der OpenClaw-Prozess, der die Agent-Loop verwaltet und das Dashboard bereitstellt:

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

Um das Dashboard zu öffnen, führen Sie Folgendes in einem zweiten Terminal aus, während der Gateway noch läuft:

```bash
openclaw dashboard
```

Da der Gateway an Loopback gebunden ist, authentifiziert sich das Dashboard automatisch, wenn es von derselben Maschine aus geöffnet wird. Für lokalen Zugriff ist keine Token-Eingabe oder Geräte-Genehmigung erforderlich. Sie sollten das OpenClaw-Dashboard mit Ihrem Lemonade-Modell als aktives Backend sehen.

> Wenn Sie Sandboxing aktiviert haben, können Sie dies überprüfen, indem Sie den Agenten im Dashboard bitten, `run hostname` auszuführen. Wenn Sie eine kurze Container-ID anstelle des Hostnamens Ihrer Maschine sehen, funktioniert die Sandbox.

**Herzlichen Glückwunsch, Sie haben einen vollständig lokalen KI-Agenten-Stack von Grund auf erstellt.**

> **Benötigen Sie das Gateway-Token?** Führen Sie `openclaw dashboard --no-open` aus, um die Dashboard-URL mit eingebettetem Token auszugeben (es wird außerdem versucht, dieses in die Zwischenablage zu kopieren). Alternativ finden Sie das Token unter `gateway.auth.token` in `~/.openclaw/openclaw.json`.

**Zugriff auf das Dashboard von einem anderen Gerät (über einen SSH-Tunnel)**

Wenn OpenClaw auf einer entfernten Maschine läuft, können Sie über einen SSH-Tunnel von Ihrer lokalen Maschine aus auf das Dashboard zugreifen. Der Tunnel leitet den Gateway-Port (`18789`) weiter, sodass Ihr lokaler Browser über `127.0.0.1` mit dem entfernten Gateway kommunizieren kann.

1. Verbinden Sie sich von Ihrer **lokalen Maschine** aus einmal mit der entfernten Maschine und bestätigen Sie die Fingerprint-Abfrage, damit der Host zu Ihren bekannten Hosts hinzugefügt wird:

   ```bash
   ssh user@<host-ip>
   ```

2. Öffnen Sie weiterhin auf Ihrer **lokalen Maschine** den SSH-Tunnel:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Hinweis:** Nachdem Sie Ihr Passwort eingegeben haben, zeigt das Terminal keine Ausgabe an und scheint zu hängen. Das ist erwartet: Das Flag `-N` weist SSH an, keinen Remote-Befehl auszuführen, sodass es lediglich den Tunnel offen hält. Lassen Sie dieses Terminal weiterlaufen.

3. Öffnen Sie auf Ihrer **lokalen Maschine** einen Browser und rufen Sie `http://127.0.0.1:18789` auf.

4. Geben Sie auf der **entfernten Maschine** das Gateway-Token aus und fügen Sie es zum Anmelden in den Browser ein:

   ```bash
   openclaw dashboard --no-open
   ```

   Dies gibt die Dashboard-URL mit eingebettetem Token aus; kopieren Sie das Token, um sich anzumelden. (Das Token wird außerdem unter `gateway.auth.token` in `~/.openclaw/openclaw.json` gespeichert.)

> **Genehmigen eines entfernten Geräts:** Wenn Sie das Dashboard von einer anderen Maschine oder einem Telefon aus öffnen, zeigt der Browser möglicherweise eine Anfrage-ID an. Listen Sie auf der **entfernten Maschine** die ausstehenden Anfragen auf:
> ```bash
> openclaw devices list
> ```
> Genehmigen Sie anschließend die passende Anfrage:
> ```bash
> openclaw devices approve <requestId>
> ```
> Dies ist nur für entfernte oder zusätzliche Geräte erforderlich; Loopback-Zugriff von derselben Maschine authentifiziert sich automatisch. Weitere Details finden Sie in der Dokumentation zu [Remote Access](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Optional: Einen Kommunikationskanal verbinden

Sobald der Gateway läuft, können Sie von jedem Gerät aus auf Ihren lokalen Agenten zugreifen. Wählen Sie die Option, die zu Ihrem Setup passt. OpenClaw unterstützt [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) und weitere Kanäle; die vollständige Liste finden Sie unter [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Option A: Discord

Discord erfordert einen Server, auf dem **Sie über Administratorrechte verfügen**, um einen Bot hinzuzufügen. Wenn Sie Server gemeinsam nutzen, aber keinen besitzen, verwenden Sie stattdessen Option B (Telegram).

#### Ein Discord-Konto und einen Server erstellen

Falls Sie noch kein Discord-Konto haben, registrieren Sie sich unter [discord.com](https://discord.com). Sie benötigen außerdem einen Server, auf dem Sie Administrator sind. Erstellen Sie einen, indem Sie auf das **+**-Symbol in der Discord-Seitenleiste klicken und **Create My Own** auswählen. Ein privater Server genügt.

#### Eine Discord-Anwendung und einen Bot erstellen

1. Gehen Sie zum [Discord Developer Portal](https://discord.com/developers/applications) und klicken Sie auf **New Application**. Vergeben Sie einen Namen (z. B. „openclaw-bot“).
2. Klicken Sie in der Seitenleiste auf **Bot**. Legen Sie einen Benutzernamen für den Bot fest.
3. Scrollen Sie weiterhin auf der Bot-Seite zu **Privileged Gateway Intents** und aktivieren Sie:
   - **Message Content Intent** (erforderlich)
   - **Server Members Intent** (empfohlen)
4. Scrollen Sie zurück nach oben und klicken Sie auf **Reset Token**, um Ihr Bot-Token zu erzeugen. Kopieren Sie es.

#### Den Bot zu Ihrem Server hinzufügen

1. Klicken Sie in der Seitenleiste auf **OAuth2/ URL Generator**.
2. Aktivieren Sie unter **Scopes** die Optionen `bot` und `applications.commands`.
3. Aktivieren Sie unter **Bot Permissions**: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopieren Sie die generierte URL, fügen Sie sie in Ihren Browser ein, wählen Sie Ihren Server aus und bestätigen Sie. Der Bot sollte nun in der Mitgliederliste Ihres Servers erscheinen.

#### Ihre IDs sammeln

Aktivieren Sie den Entwicklermodus in Discord (**User Settings/ Advanced/ Developer Mode**), und dann:
- Rechtsklick auf Ihr Server-Symbol: **Copy Server ID**
- Rechtsklick auf Ihren eigenen Avatar: **Copy User ID**

#### DMs von Server-Mitgliedern zulassen

Rechtsklick auf Ihr Server-Symbol/ **Privacy Settings**/ **Direct Messages** aktivieren. Dies ermöglicht es dem Bot, Ihnen eine DM zu senden, was für den Pairing-Schritt erforderlich ist.

#### OpenClaw für Discord konfigurieren

Speichern Sie Ihr Bot-Token als Umgebungsvariable und erstellen Sie anschließend eine einzelne Patch-Datei, die Discord aktiviert, auf das Token verweist und Ihren Server auf die Allowlist setzt. Ersetzen Sie `<server_id>` und `<user_id>` durch die oben gesammelten IDs.

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

> **Verlassen Sie sich nicht darauf, den Agenten zu bitten, dies zu konfigurieren.** Wenn Sandboxing aktiviert ist, kann der Agent aus der Sandbox heraus nicht in `~/.openclaw/openclaw.json` schreiben. Verwenden Sie stattdessen die oben genannten CLI-Befehle auf dem Host.

Starten Sie den Gateway neu, damit er die neue Kanalkonfiguration übernimmt:

```bash
openclaw gateway run --bind loopback --port 18789
```

Sie sollten innerhalb weniger Sekunden `logged in to discord as <bot-name>` in der Gateway-Ausgabe sehen.
#### Koppeln Sie Ihr Discord-Konto

Senden Sie dem Bot eine Direktnachricht in Discord. Er antwortet mit einem kurzen Pairing-Code.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Genehmigen Sie ihn auf dem Rechner, auf dem OpenClaw läuft:
```bash
openclaw pairing approve discord <CODE>
```

> Pairing-Codes laufen nach einer Stunde ab.

Sie können jetzt direkt aus Discord mit Ihrem Agenten chatten und Aufgaben an Ihre lokale Hardware auslagern.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Option B: Telegram

Telegram ist für die meisten Nutzer einfacher als Discord, es erfordert weder einen Server noch Admin-Zugriff.

#### Erstellen Sie einen Telegram-Bot

1. Öffnen Sie Telegram und schreiben Sie **@BotFather** eine Nachricht.
2. Senden Sie `/newbot` und folgen Sie den Anweisungen. Speichern Sie das dabei angezeigte Bot-Token.

#### Konfigurieren Sie OpenClaw für Telegram

Speichern Sie das Token als Umgebungsvariable:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Fügen Sie die Kanalkonfiguration in `~/.openclaw/openclaw.json` hinzu (oder passen Sie sie über das Dashboard an):

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

Starten Sie das Gateway neu und senden Sie Ihrem Bot dann eine beliebige Nachricht in Telegram. Genehmigen Sie das Pairing:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Pairing-Codes laufen nach einer Stunde ab. Sie können jetzt per Telegram-Direktnachricht mit Ihrem Agenten chatten.

---

## Nächste Schritte

Jetzt, da Ihr Agent Befehle von Ihrem Smartphone empfangen und auf Ihrem lokalen Rechner ausführen kann, sind hier drei Richtungen, die sich zu erkunden lohnen:

1. **Aktienmarkt-Zusammenfasser**: Planen Sie, dass OpenClaw in festgelegten Intervallen Daten von Finanz-APIs abruft, die Bewegungen des Tages mit Ihrem lokalen Modell zusammenfasst und jeden Morgen über den von Ihnen gewählten Kanal eine Übersicht an Ihr Smartphone sendet.

2. **Fine-Tuning-Monitor**: Starten Sie einen Trainingsjob per Fernzugriff über Telegram oder Discord, und lassen Sie den Agenten das Trainingsprotokoll verfolgen sowie regelmäßig Verlustwerte, GPU-Auslastung und Speicherplatznutzung an Ihr Smartphone melden. Falls der Lauf ins Stocken gerät oder der VRAM-Verbrauch ansteigt, erfahren Sie es sofort, ohne am Rechner sein zu müssen.

3. **IOT mit einem lokalen VLM**: Richten Sie eine Kamera auf Ihre Haustür, führen Sie ein Vision-Modell auf Lemonade aus und lassen Sie OpenClaw Einzelbilder auf Abruf oder bei einem Auslöser analysieren. Fragen Sie von Ihrem Smartphone aus „Sind heute Pakete angekommen?" und erhalten Sie eine direkte Antwort von Ihrer eigenen Hardware.

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