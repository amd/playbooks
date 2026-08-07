<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

# OpenClaw mit Lemonade Server als Backend ausführen

## Überblick

[**OpenClaw**](https://openclaw.ai/) ist ein autonomer KI-Agent, der Code schreiben und ausführen, Dateien verwalten und komplexe mehrstufige Aufgaben in Ihrem Auftrag erledigen kann. Im Gegensatz zu einem Chat-Assistenten, der lediglich Fragen beantwortet, führt OpenClaw echte Aktionen auf Ihrem System aus. Das bedeutet, dass es ein schnelles, leistungsfähiges KI-Backend benötigt, das mit einer anspruchsvollen Agent-Schleife mithalten kann.

[**Lemonade Server**](https://lemonade-server.ai/) ist genau dieses Backend. Es handelt sich um einen quelloffenen lokalen Inferenzserver, der GenAI-Modelle direkt auf Ihrer Hardware ausführt und sie über die branchenübliche OpenAI-API bereitstellt.

Gemeinsam bilden sie einen vollständig lokalen KI-Agenten-Stack: Lemonade übernimmt die Modellinferenz, und OpenClaw stellt die Agent-Schleife bereit, die Modellausgaben in echte Aktionen umsetzt.

> **Bevor Sie fortfahren:** OpenClaw ist ein hochgradig autonomer KI-Agent. Wenn Sie einem KI-Agenten Zugriff auf Ihr System gewähren, kann dies zu unvorhersehbaren oder unbeabsichtigten Ergebnissen führen. Fahren Sie nur fort, wenn Sie sich der Risiken bewusst sind und damit einverstanden sind, dass autonome Software in Ihrem Auftrag handelt.

---

## Was Sie lernen werden

Am Ende dieses Playbooks können Sie:

- Mehr über **Lemonade Server** erfahren
- **OpenClaw installieren** und **es auf Lemonade Server** als sein KI-Backend ausrichten.
- **Das OpenClaw-Gateway starten** und bestätigen, dass Ihr Agent einsatzbereit ist.
- **Einen Kommunikationskanal verbinden** (Discord oder Telegram), sodass Sie von jedem Gerät aus mit Ihrem Agenten chatten können.

---

## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Auf Software-Updates prüfen

<!-- @require:software-update -->
<!-- @device:end -->

## Installieren der Software-Voraussetzungen

<!-- @os:linux -->
- Ein PC mit **Ubuntu 24.04+** oder einer kompatiblen Debian-basierten Linux-Distribution mit `apt-get`
- Mindestens **12 GB RAM** (64 GB+ für größere Modelle empfohlen)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (optional, zum Sandboxing von OpenClaw)
- **~10–30 GB freier Speicherplatz** für Modellgewichte
<!-- @os:end -->

<!-- @os:windows -->
- Ein PC mit **Windows 10/11**
- Mindestens **12 GB RAM** (64 GB+ für größere Modelle empfohlen)
- **~10–30 GB freier Speicherplatz** für Modellgewichte
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (optional, zum Sandboxing von OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Empfohlenes Modell abrufen und laden

Das für dieses Playbook empfohlene Modell ist **Qwen3.6-35B-A3B-GGUF** von Unsloth, ein leistungsstarkes MoE-Modell mit einem Kontextfenster von 263.000 Token, das sich hervorragend für Agenten-Workloads eignet. Dieses Modell verwendet die UD-Q4_K_XL-Quantisierung. Rufen Sie es jetzt ab:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Laden Sie es anschließend mit einem großen Kontextfenster und speichern Sie diese Einstellung für zukünftige Ausführungen:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Das Modell hat standardmäßig eine Kontextlänge von 262.144 Token. Wenn Speicherüberlauf-Fehler (OOM) auftreten, sollten Sie das Kontextfenster verkleinern. Da Qwen3.6 jedoch einen erweiterten Kontext für komplexe Aufgaben nutzt, empfehlen wir, eine Kontextlänge von mindestens 128K Token beizubehalten, um die Denkfähigkeiten zu erhalten.

> **Tipp: Denkmodus für schnellere Agenten-Antworten deaktivieren:** Qwen3.6-35B-A3B läuft standardmäßig im Denkmodus, was vor jeder Antwort zusätzliche Latenz verursacht. Bei Agenten-Schleifen summiert sich dieser Mehraufwand schnell. Das Repository [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) stellt eine fertige Konfiguration bereit, die den Denkmodus deaktiviert. Laden Sie dazu die Datei herunter und importieren Sie sie:
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

Wir führen OpenClaw innerhalb von WSL (empfohlen) aus und verbinden es mit Lemonade, das nativ unter Windows läuft. So erhalten Sie eine Linux-Shell-Umgebung für OpenClaw, während die GPU-Beschleunigung von Lemonade auf der Windows-Seite erhalten bleibt.

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

**Ihre WSL-Gateway-IP finden** (innerhalb von WSL ausführen):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Portproxy hinzufügen** (in PowerShell als Administrator ausführen, ersetzen Sie `<WSL-Gateway-IP>` durch Ihre WSL-Gateway-IP):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Hinweis: Wenn ein Fehler `netsh: command not found` auftritt, versuchen Sie stattdessen den expliziten Ausführungsnamen `netsh.exe` zu verwenden

**Firewall-Regel hinzufügen** (dieselbe erhöhte PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Von WSL aus überprüfen**:

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

#### Aufrechterhaltung der Bridge-Funktion nach einem Neustart

Die `netsh portproxy`-Regel übersteht Neustarts, aber die WSL-Gateway-IP kann sich nach `wsl --shutdown` oder einem Neustart ändern. Wenn das passiert, verweist der Proxy weiterhin auf die alte IP und Lemonade wird von WSL aus nicht mehr erreichbar. In diesem Fall verwenden Sie eine der folgenden Optionen.

**Option 1 (empfohlen) — Die Bridge automatisch reparieren.** Um dies nicht jedes Mal manuell erledigen zu müssen, verwenden Sie eine geplante Aufgabe, die die Bridge bei jedem Start und jeder Anmeldung überprüft und sie nur dann neu aufbaut, wenn sich die Gateway-IP geändert hat. Siehe den [Leitfaden zur automatischen Reparatur der Lemonade WSL-Bridge](assets/RepairLemonadeWslBridge.md).


**Option 2 — Die Bridge manuell reparieren.** Ermitteln Sie zunächst die aktuelle WSL-Gateway-IP, indem Sie Folgendes innerhalb von WSL ausführen:

```bash
ip route show default | awk '{print $3}' | head -1
```

Kopieren Sie diesen Wert; Sie werden ihn im Folgenden anstelle von `<new-WSL-Gateway-IP>` verwenden.

Listen Sie dann in einer **erhöhten PowerShell** (als Administrator ausführen) die vorhandenen Regeln auf, löschen Sie nur die veraltete Lemonade-Regel und fügen Sie eine neue mit der aktuellen IP hinzu:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

In der Ausgabe von `show all` ist die veraltete Lemonade-Regel der Eintrag, dessen Verbindungsadresse `127.0.0.1` auf Port `13305` ist; seine Listen-Adresse ist Ihre `<old-WSL-Gateway-IP>`. Das Löschen anhand dieser Adresse entfernt nur diese Regel und lässt alle anderen Port-Proxy-Regeln auf Ihrem Rechner unberührt.

Die Firewall-Regel, die Sie während der Einrichtung hinzugefügt haben, ist an Port `13305` (nicht an die IP) gebunden, sodass sie weiterhin funktioniert und nicht neu erstellt werden muss.

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

Das Flag `--no-onboard` überspringt den interaktiven Einrichtungsassistenten, Sie konfigurieren das Modell-Backend im nächsten Schritt manuell, was Ihnen präzise Kontrolle darüber gibt, welches Modell und welcher Server verwendet werden.

Öffnen Sie ein neues Terminal und bestätigen Sie die Installation:

```bash
openclaw --version
```

> **Tipp:** Wenn nach der Installation `command not found` angezeigt wird, fügen Sie das globale bin-Verzeichnis von npm zu Ihrem PATH hinzu:
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

Dieser Befehl schreibt die Konfiguration von OpenClaw nach `~/.openclaw/openclaw.json`.

> **OpenClaw-Kontextfenstergröße:** Die Komprimierung von OpenClaw wird ausgelöst, wenn `contextTokens > contextWindow − reserveTokens`. Der Standardwert `reserveTokensFloor` beträgt 20.000 Token, ein Mindestwert, der `reserveTokens` überschreibt, wenn dieser niedriger ist, sodass jeder Modellkontext unter ~37k eine unendliche Komprimierungsschleife auslöst. Setzen Sie einmal in Ihrer Konfiguration eine niedrige Reserve und deaktivieren Sie den Mindestwert, dann gilt dies für jedes Modell, ohne dass eine modellspezifische Anpassung erforderlich ist:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` ist ein *Mindestwert* (Untergrenze), nicht die Reserve selbst; nur den Mindestwert zu setzen hat keine Wirkung. `reserveTokensFloor: 0` deaktiviert die Untergrenze, sodass der niedrigere `reserveTokens`-Wert akzeptiert wird.
>
> **Wann Sie dies anwenden sollten:** Verwenden Sie diese Konfiguration, wenn das effektive Kontextfenster Ihres Modells unter ~37k liegt, entweder weil das Modell klein ist (z. B. 8k, 16k, 32k) oder weil Sie es absichtlich auf einen niedrigeren Wert begrenzt haben (z. B. Laden eines 128k-Modells, aber Setzen des Kontexts auf 16k in Lemonade). Ohne dies gerät OpenClaw beim Start in eine unendliche Komprimierungsschleife.
>
> **Modelle mit großem Kontext bei vollem Kontext:** Sie können dies vollständig überspringen. Die Standardwerte funktionieren einwandfrei, die Komprimierung setzt bereits deutlich vor dem Füllen des Fensters ein, und das Modell hat ausreichend Platz, um lange Antworten zu generieren. Wenn Sie es dennoch anwenden, beachten Sie, dass `reserveTokens: 4096` die Antwortlänge auf ~4k Token begrenzt, was lange Dateigenerierungen oder detaillierte Pläne abschneiden kann.
>
> **Wo Sie dies hinzufügen:** Platzieren Sie den `compaction`-Block innerhalb von `agents.defaults` in Ihrer `openclaw.json` (normalerweise unter `~/.openclaw/openclaw.json`):
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
> Der Rest Ihrer Konfiguration (Gateway, Kanäle, Modelle usw.) bleibt unverändert, es muss nur der Schlüssel `compaction` hinzugefügt werden.
### (Empfohlen) Docker-Sandboxing aktivieren

OpenClaw kann alle Datei- und Codeoperationen des Agenten über einen isolierten Docker-Container leiten, anstatt sie direkt auf Ihrem Host auszuführen. Dies begrenzt die Auswirkungen unbeabsichtigter Aktionen auf die Sandbox, sodass Ihr Host-Dateisystem und Netzwerk unangetastet bleiben.

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
> Wenn beim Ausführen von Docker-Befehlen „permission denied“ angezeigt wird:
> 
> **Schritt 1: Fügen Sie Ihren Benutzer der Docker-Gruppe hinzu**
> 
> ```bash
> sudo groupadd docker                    # Gruppe bei Bedarf erstellen
> sudo usermod -aG docker $USER           # Sich selbst zur Gruppe hinzufügen
> newgrp docker                           # Änderung aktivieren
> docker run hello-world                  # Testen
> ```
> 
> **Schritt 2: Falls der Fehler weiterhin besteht, wenden Sie die dauerhafte Lösung an**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Starten Sie anschließend Ihr System **neu**.
> 
> **Schnelle temporäre Lösung** (wird nach Neustart zurückgesetzt):
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

[Firecrawl](https://docs.firecrawl.dev/introduction) bietet einen selbst gehosteten Web-Crawling- und Inhaltsextraktionsdienst, der diese Herausforderungen umgehen und das volle Potenzial der OpenClaw-Automatisierung freisetzen kann.

In diesem Setup läuft OpenClaw als eine Reihe von Docker-Containern, die mit Podman verwaltet werden. Um die Lebenszyklusverwaltung und den automatischen Start zu vereinfachen, registrieren wir Firecrawl als benutzerbasierten `systemd`-Dienst, der den zugrunde liegenden Podman-Compose-Stack orchestriert. Dadurch kann OpenClaw das Gateway starten, stoppen und den Firecrawl-Dienst mit standardmäßigen `systemctl --user`-Befehlen überprüfen, anstatt direkt mit den Containern zu interagieren.

Um es einfach zu halten, haben wir den gesamten Prozess in vier Schritte unterteilt:

---

### 1. Systemdienst registrieren
Navigieren Sie zum Konfigurationsverzeichnis für systemd-Benutzerdienste:
```bash
cd ~/.config/systemd/user
```
Erstellen und öffnen Sie eine neue Datei namens `firecrawl.service`.
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

 `default.target.wants/` enthält symbolische Links zu Diensten, die für den automatischen Start konfiguriert sind.

### 2. Firecrawl konfigurieren

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) eignet sich ideal für alle, die volle Kontrolle über ihre Scraping- und Datenverarbeitungsumgebungen benötigen, was jedoch mit zusätzlichem Wartungs- und Konfigurationsaufwand verbunden ist.

Beginnen Sie, indem Sie das Repository klonen:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Erstellen Sie `.env` im Stammverzeichnis `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. OpenClaw mit Podman Compose bereitstellen

Stellen Sie vor dem Fortfahren sicher, dass Sie das neueste OpenClaw-Docker-Image gezogen haben:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Sobald dies erledigt ist, laden Sie die OpenClaw-Compose-Datei [openclaw-compose.yaml](assets/openclaw-compose.yaml) herunter und platzieren Sie sie im Stammverzeichnis `/firecrawl`:

> Diese Konvention ist erforderlich, damit `systemd` den Dienst korrekt finden und starten kann, wie in `WorkingDirectory=${HOME}/firecrawl` festgelegt.

> Sie können den Stack jederzeit erweitern, indem Sie bei Bedarf zusätzliche Firecrawl-Dienste hinzufügen. Die vollständige Liste der verfügbaren Dienste finden Sie in der offiziellen [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. OpenClaw-Dienst über Firecrawl starten

Bevor Sie die Kontrolle an `systemd` übergeben, überprüfen Sie, ob alles korrekt funktioniert, indem Sie den Stack manuell ausführen:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Wenn alles korrekt konfiguriert ist, sollten Sie sehen, wie der OpenClaw-Container hochfährt, und Ihre Kommandozeilenausgabe sollte in etwa so aussehen:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Nach der Überprüfung fahren Sie den Stack wieder herunter, bevor Sie fortfahren:
```bash
podman compose -f openclaw-compose.yaml down
```
Bevor Sie den Dienst starten, müssen Sie sicherstellen, dass die korrekten Eigentumsverhältnisse und Berechtigungen für das Verzeichnis `firecrawl` und dessen `.env`-Datei festgelegt sind.
Dies ist unerlässlich, damit der Dienst Ihre Anmeldedaten beim Start schreiben kann.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Da nun alles überprüft ist, starten Sie den Dienst über `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Die OpenClaw-Aktionen](https://docs.openclaw.ai/) sind innerhalb des interaktiven Containers zugänglich, und das Web-Dashboard ist auf demselben Host und Port unter http://127.0.0.1:18789 verfügbar.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Ihren `OPENCLAW_GATEWAY_TOKEN` erhalten

Sobald der Dienst läuft, werden Sie feststellen, dass in Ihrem Home-Verzeichnis ein neues Verzeichnis `.openclaw` erstellt wurde (~/.openclaw). Dieses Verzeichnis ist standardmäßig gesperrt, sodass Sie es entsperren müssen, um Ihr Gateway-Token abzurufen.

1. Gewähren Sie Zugriff auf das Verzeichnis:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Lesen Sie Ihr Gateway-Token:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Suchen Sie den Wert von `OPENCLAW_GATEWAY_TOKEN` in der Ausgabe.

3. Öffnen Sie das Gateway-Dashboard in Ihrem Browser unter http://127.0.0.1:18789. Fügen Sie Ihr Token ein, wenn Sie zur Authentifizierung aufgefordert werden.

Um den Dienst zu stoppen, führen Sie Folgendes aus:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Starten des OpenClaw-Gateways

Das Gateway ist der OpenClaw-Prozess, der die Agenten-Schleife verwaltet und das Dashboard bereitstellt:

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

Da das Gateway an Loopback gebunden ist, authentifiziert sich das Dashboard automatisch, wenn es vom selben Rechner geöffnet wird, es ist keine Token-Eingabe oder Geräte-Genehmigung für lokalen Zugriff erforderlich. Sie sollten das OpenClaw-Dashboard sehen, mit Ihrem Lemonade-Modell als aktivem Backend gelistet.

> Wenn Sie Sandboxing aktiviert haben, können Sie dies überprüfen, indem Sie den Agenten bitten, `run hostname` über das Dashboard auszuführen. Wenn Sie eine kurze Container-ID anstelle des Hostnamens Ihres Rechners sehen, funktioniert die Sandbox.

**Herzlichen Glückwunsch, Sie haben einen vollständig lokalen KI-Agenten-Stack von Grund auf aufgebaut.**

> **Benötigen Sie das Gateway-Token?** Führen Sie `openclaw dashboard --no-open` aus, um die Dashboard-URL mit eingebettetem Token auszugeben (es wird auch versucht, ihn in Ihre Zwischenablage zu kopieren). Alternativ finden Sie das Token unter `gateway.auth.token` in `~/.openclaw/openclaw.json`.

**Zugriff auf das Dashboard von einem anderen Gerät (via SSH-Tunnel)**

Wenn OpenClaw auf einem entfernten Rechner läuft, können Sie dessen Dashboard von Ihrem lokalen Rechner über einen SSH-Tunnel erreichen. Der Tunnel leitet den Gateway-Port (`18789`) weiter, sodass Ihr lokaler Browser mit dem entfernten Gateway über `127.0.0.1` kommunizieren kann.

1. Verbinden Sie sich von Ihrem **lokalen Rechner** einmal mit dem entfernten Rechner und akzeptieren Sie die Fingerprint-Abfrage, damit der Host zu Ihren bekannten Hosts hinzugefügt wird:

   ```bash
   ssh user@<host-ip>
   ```

2. Öffnen Sie weiterhin auf Ihrem **lokalen Rechner** den SSH-Tunnel:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Hinweis:** Nachdem Sie Ihr Passwort eingegeben haben, zeigt das Terminal keine Ausgabe an und scheint zu hängen. Das ist erwartet: Das Flag `-N` weist SSH an, keinen entfernten Befehl auszuführen, sodass es lediglich den Tunnel offen hält. Lassen Sie dieses Terminal laufen.

3. Öffnen Sie auf Ihrem **lokalen Rechner** einen Browser und gehen Sie zu `http://127.0.0.1:18789`.

4. Geben Sie auf dem **entfernten Rechner** das Gateway-Token aus und fügen Sie es in den Browser ein, um sich anzumelden:

   ```bash
   openclaw dashboard --no-open
   ```

   Dies gibt die Dashboard-URL mit eingebettetem Token aus; kopieren Sie das Token, um sich anzumelden. (Das Token wird auch unter `gateway.auth.token` in `~/.openclaw/openclaw.json` gespeichert.)

> **Genehmigen eines entfernten Geräts:** Wenn Sie das Dashboard von einem anderen Rechner oder Smartphone öffnen, zeigt der Browser möglicherweise eine Anfrage-ID an. Listen Sie auf dem **entfernten Rechner** die ausstehenden Anfragen auf:
> ```bash
> openclaw devices list
> ```
> Genehmigen Sie dann die passende Anfrage:
> ```bash
> openclaw devices approve <requestId>
> ```
> Dies ist nur für entfernte oder sekundäre Geräte erforderlich; der Loopback-Zugriff vom selben Rechner authentifiziert sich automatisch. Weitere Details finden Sie in der Dokumentation [Remote Access](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Optional: Verbinden eines Kommunikationskanals

Sobald das Gateway läuft, können Sie Ihren lokalen Agenten von jedem Gerät aus erreichen. Wählen Sie die Option, die zu Ihrem Setup passt. OpenClaw unterstützt [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) und weitere Kanäle, die vollständige Liste finden Sie unter [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Option A: Discord

Discord erfordert einen Server, auf dem **Sie Administratorzugriff haben**, um einen Bot hinzuzufügen. Wenn Sie Server gemeinsam nutzen, aber keinen eigenen besitzen, verwenden Sie stattdessen Option B (Telegram).

#### Discord-Konto und -Server erstellen

Wenn Sie noch kein Discord-Konto haben, registrieren Sie sich unter [discord.com](https://discord.com). Sie benötigen außerdem einen Server, auf dem Sie Administrator sind. Erstellen Sie einen, indem Sie auf das **+**-Symbol in der Discord-Seitenleiste klicken und **Create My Own** auswählen. Ein privater Server ist ausreichend.

#### Discord-Anwendung und Bot erstellen

1. Gehen Sie zum [Discord Developer Portal](https://discord.com/developers/applications) und klicken Sie auf **New Application**. Geben Sie ihm einen Namen (z. B. „openclaw-bot").
2. Klicken Sie in der Seitenleiste auf **Bot**. Legen Sie einen Benutzernamen für den Bot fest.
3. Scrollen Sie weiterhin auf der Bot-Seite zu **Privileged Gateway Intents** und aktivieren Sie:
   - **Message Content Intent** (erforderlich)
   - **Server Members Intent** (empfohlen)
4. Scrollen Sie wieder nach oben und klicken Sie auf **Reset Token**, um Ihr Bot-Token zu generieren. Kopieren Sie es.

#### Den Bot zu Ihrem Server hinzufügen

1. Klicken Sie in der Seitenleiste auf **OAuth2/ URL Generator**.
2. Aktivieren Sie unter **Scopes** die Optionen `bot` und `applications.commands`.
3. Aktivieren Sie unter **Bot Permissions**: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopieren Sie die generierte URL, fügen Sie sie in Ihren Browser ein, wählen Sie Ihren Server aus und bestätigen Sie. Der Bot sollte nun in der Mitgliederliste Ihres Servers erscheinen.

#### Ihre IDs sammeln

Aktivieren Sie den Entwicklermodus in Discord (**User Settings/ Advanced/ Developer Mode**) und dann:
- Rechtsklick auf Ihr Server-Symbol: **Copy Server ID**
- Rechtsklick auf Ihren eigenen Avatar: **Copy User ID**

#### DMs von Servermitgliedern erlauben

Rechtsklick auf Ihr Server-Symbol/ **Privacy Settings**/ schalten Sie **Direct Messages** ein. Dies erlaubt dem Bot, Ihnen eine DM zu senden, was für den Pairing-Schritt erforderlich ist.

#### OpenClaw für Discord konfigurieren

Speichern Sie Ihr Bot-Token als Umgebungsvariable und erstellen Sie dann eine einzelne Patch-Datei, die Discord aktiviert, auf das Token verweist und Ihren Server auf die Allowlist setzt. Ersetzen Sie `<server_id>` und `<user_id>` durch die oben gesammelten IDs.

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

> **Verlassen Sie sich nicht darauf, den Agenten zu bitten, dies zu konfigurieren.** Wenn Sandboxing aktiviert ist, kann der Agent nicht aus dem Inneren der Sandbox in `~/.openclaw/openclaw.json` schreiben, verwenden Sie stattdessen die oben genannten CLI-Befehle auf dem Host.

Starten Sie das Gateway neu, damit es die neue Kanalkonfiguration übernimmt:

```bash
openclaw gateway run --bind loopback --port 18789
```

Sie sollten innerhalb weniger Sekunden `logged in to discord as <bot-name>` in der Gateway-Ausgabe sehen.
#### Verknüpfe dein Discord-Konto

Schreibe dem Bot eine Direktnachricht in Discord. Er antwortet mit einem kurzen Pairing-Code.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Bestätige ihn auf dem Rechner, auf dem OpenClaw läuft:
```bash
openclaw pairing approve discord <CODE>
```

> Pairing-Codes verfallen nach einer Stunde.

Du kannst jetzt direkt aus Discord mit deinem Agenten chatten und Aufgaben an deine lokale Hardware auslagern.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Option B: Telegram

Telegram ist für die meisten Nutzer einfacher als Discord, es erfordert weder einen Server noch Admin-Zugriff.

#### Erstelle einen Telegram-Bot

1. Öffne Telegram und schreibe eine Nachricht an **@BotFather**.
2. Sende `/newbot` und folge den Anweisungen. Speichere den Bot-Token, den du erhältst.

#### Konfiguriere OpenClaw für Telegram

Speichere den Token als Umgebungsvariable:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Füge die Kanalkonfiguration in `~/.openclaw/openclaw.json` hinzu (oder passe sie über das Dashboard an):

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

Starte das Gateway neu und schicke deinem Bot dann eine beliebige Nachricht in Telegram. Bestätige das Pairing:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Pairing-Codes verfallen nach einer Stunde. Du kannst jetzt über Telegram-Direktnachrichten mit deinem Agenten chatten.

---

## Nächste Schritte

Jetzt, da dein Agent Befehle von deinem Handy empfangen und auf deinem lokalen Rechner ausführen kann, gibt es drei Richtungen, die sich zu erkunden lohnen:

1. **Aktienmarkt-Zusammenfassung**: Lasse OpenClaw in festen Intervallen Daten von Finanz-APIs abrufen, die Kursbewegungen des Tages mit deinem lokalen Modell zusammenfassen und dir jeden Morgen über den Kanal deiner Wahl eine Übersicht auf dein Handy schicken.

2. **Fine-Tuning-Monitor**: Starte einen Trainingsjob remote über Telegram oder Discord und lass den Agenten das Trainingslog verfolgen sowie regelmäßig Loss-Werte, GPU-Auslastung und Speicherplatznutzung an dein Handy melden. Wenn der Lauf stockt oder der VRAM-Verbrauch ansteigt, erfährst du es sofort, ohne am Rechner sein zu müssen.

3. **IOT mit einem lokalen VLM**: Richte eine Kamera auf deine Haustür, betreibe ein Vision-Modell auf Lemonade und lass OpenClaw Frames auf Anfrage oder bei einem Auslöser analysieren. Frage von deinem Handy aus „Sind heute Pakete angekommen?“ und erhalte eine klare Antwort von deiner eigenen Hardware.

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