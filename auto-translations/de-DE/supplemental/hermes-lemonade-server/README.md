<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

# Hermes Agent lokal mit Lemonade Server ausführen

## Übersicht

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) ist ein selbstverbessernder KI-Agent von Nous Research. Er verfügt über eine eingebaute Lernschleife, erstellt Fähigkeiten aus Erfahrung, baut über Sitzungen hinweg ein dauerhaftes Gedächtnis darüber auf, wer Sie sind, und kann geplante Automatisierungen in Ihrem Namen ausführen. Anders als ein einfacher Chat-Assistent führt Hermes tatsächliche Aktionen aus: Ausführen von Shell-Befehlen, Schreiben von Dateien, Durchsuchen des Webs und Delegieren paralleler Arbeitsabläufe an Subagenten.

[**Lemonade Server**](https://lemonade-server.ai/) ist das lokale Inferenz-Backend, das ihn antreibt. Es handelt sich um einen Open-Source-Server, der GenAI-Modelle direkt auf Ihrer AMD-Hardware ausführt und sie über die branchenübliche OpenAI-API bereitstellt.

Zusammen bilden sie einen vollständig lokalen KI-Agenten-Stack: Lemonade übernimmt die Modellinferenz auf Ihrer GPU, und Hermes stellt die Agentenschleife, das Gedächtnis, die Fähigkeiten und das Messaging-Gateway bereit.

> **Bevor Sie fortfahren:** Hermes Agent ist ein hochgradig autonomer KI-Agent. Wenn Sie einem KI-Agenten Zugriff auf Ihr System gewähren, kann dies zu unvorhersehbaren oder unbeabsichtigten Ergebnissen führen. Fahren Sie nur fort, wenn Sie die Risiken verstehen und damit einverstanden sind, dass autonome Software in Ihrem Namen handelt.

---

## Was Sie lernen werden

Am Ende dieses Playbooks werden Sie in der Lage sein:

- **Hermes Agent zu installieren** und ihn auf **Lemonade Server** als KI-Backend auszurichten.
- **(Empfohlen) Docker/Podman-Sandboxing zu aktivieren**, um die Aktionen des Agenten vom Host zu isolieren.
- **Das Hermes-Gateway zu starten** und zu bestätigen, dass Ihr Agent bereit ist.
- **Einen Kommunikationskanal (Discord oder Telegram) zu verbinden**, damit Sie von jedem Gerät aus mit Ihrem Agenten chatten können.

---

## Konfigurieren des Speichers (Memory)

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen

<!-- @require:software-update -->
<!-- @device:end -->

## Installieren der Software-Voraussetzungen

<!-- @os:linux -->
- Ein PC mit **Ubuntu 24.04+** oder einer kompatiblen Debian-basierten Linux-Distribution mit `apt-get`
- Mindestens **12 GB RAM** (64 GB+ für größere Modelle empfohlen)
- **~10–30 GB freier Festplattenspeicher** für Modellgewichte
- [Podman](https://podman.io/docs/installation) (Optional, für das Sandboxing von Hermes Agent)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- Ein PC mit **Windows 10/11**
- Mindestens **12 GB RAM** (64 GB+ für größere Modelle empfohlen)
- **~10–30 GB freier Festplattenspeicher** für Modellgewichte
- Podman (Optional, für das Sandboxing von Hermes Agent). Installation innerhalb von WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman ist auf der Halo Box vorinstalliert und erfordert keine Einrichtung
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Empfohlenes Modell herunterladen und laden

Das für dieses Playbook empfohlene Modell ist **Qwen3.6-35B-A3B-GGUF** von Unsloth, ein leistungsstarkes MoE-Modell mit einem Kontextfenster von 263.000 Token, das sich gut für Agenten-Workloads eignet. Dieses Modell verwendet die UD-Q4_K_XL-Quantisierung. Laden Sie es jetzt herunter:

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

Das Modell hat standardmäßig eine Kontextlänge von 262.144 Token. Wenn Sie Speicherfehler (Out-of-Memory, OOM) feststellen, sollten Sie das Kontextfenster verkleinern.

> **Tipp: Denkmodus deaktivieren für schnellere Agentenantworten:** Qwen3.6-35B-A3B läuft standardmäßig im Denkmodus, was vor jeder Antwort zusätzliche Latenz verursacht. Bei Agentenschleifen summiert sich dieser Overhead schnell. Das Repository [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) stellt eine fertige Konfiguration bereit, die den Denkmodus deaktiviert. Laden Sie dazu die Datei herunter und importieren Sie sie:
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

## WSL einrichten

Wir führen Hermes Agent innerhalb von WSL aus und verbinden ihn mit Lemonade, das nativ unter Windows läuft. Dies bietet Ihnen eine Linux-Shell-Umgebung für Hermes, während die GPU-Beschleunigung von Lemonade weiterhin auf der Windows-Seite bleibt.

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

Führen Sie Folgendes im Ubuntu-Terminal aus:

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

### Lemonade von Windows in WSL überbrücken

WSL2 läuft in einem virtuellen Netzwerk. Lemonade unter Windows bindet an `127.0.0.1`, was WSL nicht direkt erreichen kann. Ein Windows-Portproxy leitet den Datenverkehr von der WSL-Gateway-IP an das Windows-Localhost weiter.

**Ermitteln Sie Ihre WSL-Gateway-IP** (innerhalb von WSL ausführen):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Fügen Sie den Portproxy hinzu** (in PowerShell als Administrator ausführen, ersetzen Sie `<WSL-Gateway-IP>` durch Ihre WSL-Gateway-IP):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Fügen Sie eine Firewall-Regel hinzu** (im selben erhöhten PowerShell-Fenster):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Überprüfen Sie von WSL aus**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Wenn Sie das Modell Qwen3.6-35B-A3B-GGUF im vorherigen Schritt bereits geladen haben, sollten Sie eine JSON-Ausgabe mit Ihrem geladenen Modell sehen.

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

> Die `netsh portproxy`-Regel bleibt nach einem Neustart erhalten, aber die WSL-Gateway-IP kann sich nach `wsl --shutdown` ändern. Falls Lemonade nach einem Neustart von WSL aus nicht mehr erreichbar ist, ermitteln Sie die aktualisierte Gateway-IP und aktualisieren Sie den Proxy mit dieser neuen IP.

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

## Hermes Agent installieren

<!-- @os:windows -->
> Führen Sie die Befehle in diesem Abschnitt in Ihrem **WSL-Terminal** aus, sofern nicht anders angegeben.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Das Flag `--skip-setup` überspringt den interaktiven Einrichtungsassistenten, sodass Sie das Modell-Backend im nächsten Schritt manuell konfigurieren können.

Laden Sie Ihre Shell neu:

```bash
source ~/.bashrc
```

Bestätigen Sie die Installation:

```bash
hermes --version
```

Führen Sie eine Selbstdiagnose durch, um alle Abhängigkeiten zu überprüfen:

```bash
hermes doctor
```

> **Tipp:** Wenn nach der Installation `command not found` angezeigt wird, fügen Sie Hermes zu Ihrem PATH hinzu:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Um dies dauerhaft zu machen, fügen Sie die obige Zeile zu Ihrer `~/.bashrc` oder `~/.zshrc` hinzu.

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
## Konfiguration von Hermes zur Nutzung von Lemonade

Hermes speichert seine Modellkonfiguration in `~/.hermes/config.yaml`. Sie können entweder die interaktive `hermes model`-Auswahl verwenden oder die Konfiguration direkt schreiben.

### Option 1: Interaktive Auswahl

<!-- @os:windows -->
> Führen Sie den folgenden Befehl in Ihrem **WSL-Terminal** aus.
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

Wenn Sie dazu aufgefordert werden:

1. Wählen Sie **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** verwenden Sie die WSL-Gateway-IP: führen Sie `ip route show default | awk '{print $3}' | head -1` in WSL aus, um sie zu erhalten, und geben Sie dann `http://<WSL-Gateway-IP>:13305/api/v1` ein
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** wählen Sie `Qwen3.6-35B-A3B-GGUF` aus der Liste
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (oder ein beliebiger Name Ihrer Wahl)

`hermes model` speichert sowohl die aktive Modellauswahl als auch einen benannten `custom_providers`-Eintrag, der die Kontextlänge zusammen mit dem Endpunkt speichert. Das Ergebnis in `~/.hermes/config.yaml` sieht folgendermaßen aus:

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

### Option 2: Konfiguration direkt schreiben

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

Ermitteln Sie in Ihrem WSL-Terminal die IP-Adresse des Windows-Hosts und schreiben Sie die Konfiguration:

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

## (Empfohlen) Podman-Sandboxing aktivieren

Der Hermes Agent kann alle Shell- und Dateioperationen des Agenten über einen isolierten Container leiten, anstatt sie direkt auf Ihrem Host auszuführen. Dies begrenzt den Wirkungsbereich unbeabsichtigter Aktionen auf die Sandbox und lässt Ihr Host-Dateisystem sowie das Netzwerk unberührt.

Erstellen Sie ein schlankes Sandbox-Image:

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
Öffnen Sie Ihr WSL-Terminal:

```powershell
wsl -d Ubuntu-24.04
```

Erstellen Sie anschließend ein schlankes Sandbox-Image:

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

Konfigurieren Sie anschließend Hermes so, dass Podman als Container-Laufzeitumgebung verwendet wird, und legen Sie das Terminal-Backend fest:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> Das `terminal.backend` bleibt weiterhin `docker`.
> `HERMES_DOCKER_BINARY` teilt Hermes mit, dass anstelle der Laufzeitumgebung Podman verwendet werden soll.

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

Hermes startet nun einen dauerhaften Sandbox-Container und leitet alle `terminal`- und Dateitool-Aufrufe darüber. Der Container teilt den Lebenszyklus mit dem Hermes-Prozess, wird für alle Tool-Aufrufe wiederverwendet und beim Beenden von Hermes zerstört.

> **Überprüfen, ob die Sandbox funktioniert:** Starten Sie Hermes (`hermes`) und bitten Sie es, `run hostname` auszuführen – Sie sollten eine kurze Container-ID anstelle des Hostnamens Ihres Rechners sehen. Sie können es auch bitten, `rm -rf <path-to-a-dummy-file/folder>` auszuführen: Hermes bestätigt die Löschung, aber der Ordner bleibt auf Ihrem Host erhalten. Der Befehl wurde innerhalb des isolierten `$HOME` des Containers ausgeführt, nicht in Ihrem.

> **Benötigen Sie eine stärkere Isolation?** Hermes bietet außerdem ein offizielles Docker-Image (`nousresearch/hermes-agent`), das den gesamten Agentenprozess innerhalb eines Containers ausführt – Gateway, Tools und alles Weitere. Weitere Informationen zur Einrichtung finden Sie in der [Hermes-Docker-Dokumentation](https://hermes-agent.nousresearch.com/docs/user-guide/docker).

---

<!-- @os:linux -->
## (Empfohlen) Hermes-Integration mit Firecrawl-Services

Hermes kann mithilfe seiner integrierten Web-Tools Websites durchsuchen und Inhalte daraus extrahieren. Viele moderne Websites verwenden jedoch Bot-Erkennungssysteme, die einfache HTTP-Anfragen blockieren und stattdessen Challenge-Seiten anstelle des eigentlichen Inhalts zurückgeben. Dadurch kann Hermes möglicherweise nicht zuverlässig Informationen von diesen Websites extrahieren.

Um diese Einschränkung zu überwinden, bietet [Firecrawl](https://docs.firecrawl.dev/introduction) einen selbst gehosteten Web-Crawling- und Content-Extraction-Dienst, der diese Herausforderungen umgehen kann und das volle Potenzial der Hermes-Automatisierung freisetzt.

In diesem Setup läuft Firecrawl als eine Reihe von Docker-Containern, die mit Podman verwaltet werden. Um die Lebenszyklusverwaltung und den automatischen Start zu vereinfachen, registrieren wir Firecrawl als benutzerbasierten `systemd`-Dienst, der den zugrunde liegenden Podman-Compose-Stack orchestriert. Dadurch kann Hermes den Firecrawl-Dienst mit Standardbefehlen von `systemctl --user` starten, stoppen und überprüfen, anstatt direkt mit den Containern zu interagieren.

Um die Angelegenheit einfach zu halten, haben wir den gesamten Prozess in vier Schritte unterteilt:

---

### 1. Den Systemdienst registrieren
Navigieren Sie zum systemd-Benutzerkonfigurationsverzeichnis:
```bash
cd ~/.config/systemd/user
```
Erstellen und öffnen Sie eine neue Datei mit dem Namen `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopieren und fügen Sie die folgende Konfiguration ein:
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
An diesem Punkt wurde der Dienst definiert, aber noch nicht bei `systemd` registriert.
Stellen Sie sicher, dass der Dateiname genau dem oben erstellten entspricht, und führen Sie dann Folgendes aus:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Bei Erfolg sollten Sie folgende Ausgabe sehen:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` enthält symbolische Links zu Diensten, die so konfiguriert sind, dass sie automatisch starten.

### 2. Firecrawl für Ihren Dienst konfigurieren

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) eignet sich ideal für alle, die volle Kontrolle über ihre Scraping- und Datenverarbeitungsumgebungen benötigen, was jedoch mit zusätzlichem Wartungs- und Konfigurationsaufwand verbunden ist.

Beginnen Sie mit dem Klonen des Repositorys:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Erstellen Sie `.env` im Stammverzeichnis `/firecrawl`:
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
> Setzen Sie `BULL_AUTH_KEY` auf ein starkes Geheimnis, insbesondere bei jeder Bereitstellung, die von nicht vertrauenswürdigen Netzwerken aus erreichbar ist.
### 3. Bereitstellung von Hermes über Compose

Stellen Sie zunächst sicher, dass Sie das neueste Hermes-Docker-Image heruntergeladen haben:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Ist dies erledigt, laden Sie die Hermes-Compose-Datei [hermes-compose.yaml](assets/hermes-compose.yaml) herunter und legen Sie diese im Stammverzeichnis `/firecrawl` ab:

> Diese Konvention ist erforderlich, damit `systemd` den Dienst wie in `WorkingDirectory=${HOME}/firecrawl` angegeben korrekt finden und starten kann.

> Sie können den Stack jederzeit erweitern, indem Sie bei Bedarf weitere Firecrawl-Dienste hinzufügen. Die vollständige Liste der verfügbaren Dienste finden Sie in der offiziellen [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Starten des Hermes-Dienstes über Firecrawl 

Bevor Sie die Kontrolle an `systemd` übergeben, überprüfen Sie durch manuelles Ausführen des Stacks, dass alles korrekt funktioniert:
```bash
podman compose -f hermes-compose.yaml up -d
```
Wenn alles korrekt konfiguriert ist, sollte der Hermes-Container hochfahren, und Ihre Kommandozeilenausgabe sollte in etwa so aussehen:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Nach erfolgreicher Überprüfung fahren Sie den Stack wieder herunter, bevor Sie fortfahren:
```bash
podman compose -f hermes-compose.yaml down
```
Nachdem nun alles überprüft wurde, starten Sie den Dienst über `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Die Hermes-API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) ist innerhalb des interaktiven Containers erreichbar, und das Web-Dashboard steht auf demselben Host und Port unter http://127.0.0.1:9119 zur Verfügung.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Um den Dienst zu stoppen, führen Sie aus:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Starten Sie direkt eine interaktive CLI-Sitzung: 

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

**Herzlichen Glückwunsch, Sie haben einen vollständig lokalen KI-Agenten-Stack erstellt.**

### Web-Dashboard

Hermes enthält eine browserbasierte Benutzeroberfläche zur Verwaltung von Konfiguration, API-Schlüsseln, Modellen, Sitzungen, Speicher und Cron-Jobs. Öffnen Sie ein zweites Terminal, während das Gateway oder die CLI läuft, und starten Sie es mit:

```bash
hermes dashboard
```

Dies startet einen lokalen Server und öffnet `http://127.0.0.1:9119` in Ihrem Browser. Die vollständige Funktionsübersicht finden Sie in der [Dashboard-Dokumentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard).
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Optional: Verbinden eines Kommunikationskanals

Sobald das Gateway läuft, können Sie von jedem Gerät aus auf Ihren lokalen Agenten zugreifen. Hermes unterstützt [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) und weitere

---

### Discord

Für Discord ist ein Server erforderlich, auf dem **Sie über Administratorrechte verfügen**, um einen Bot hinzuzufügen. Wenn Sie sich Server teilen, aber keinen eigenen besitzen, verwenden Sie stattdessen Telegram.

#### Erstellen einer Discord-Anwendung und eines Bots

1. Rufen Sie das [Discord-Entwicklerportal](https://discord.com/developers/applications) auf und klicken Sie auf **New Application**. Geben Sie ihr einen Namen (z. B. „hermes-bot“).
2. Klicken Sie in der Seitenleiste auf **Bot**. Legen Sie einen Benutzernamen für den Bot fest.
3. Scrollen Sie weiterhin auf der Bot-Seite zu **Privileged Gateway Intents** und aktivieren Sie:
   - **Message Content Intent** (erforderlich)
   - **Server Members Intent** (empfohlen)
4. Scrollen Sie zurück nach oben und klicken Sie auf **Reset Token**, um Ihren Bot-Token zu erzeugen. Kopieren Sie ihn.

#### Hinzufügen des Bots zu Ihrem Server

1. Klicken Sie in der Seitenleiste auf **OAuth2 / URL Generator**.
2. Aktivieren Sie unter **Scopes** die Optionen `bot` und `applications.commands`.
3. Aktivieren Sie unter **Bot Permissions**: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopieren Sie die generierte URL, fügen Sie sie in Ihren Browser ein, wählen Sie Ihren Server aus und bestätigen Sie.

#### Sammeln Ihrer IDs und Zulassen von Direktnachrichten

Aktivieren Sie den Entwicklermodus in Discord (**User Settings / Advanced / Developer Mode**), und dann:
- Rechtsklick auf Ihr Server-Symbol: **Copy Server ID**
- Rechtsklick auf Ihren eigenen Avatar: **Copy User ID**

Rechtsklick auf Ihr Server-Symbol / **Privacy Settings** / Schalten Sie **Direct Messages** ein. Dies ist für den Kopplungsschritt erforderlich.

#### Konfigurieren von Hermes für Discord

Fügen Sie Folgendes zu `~/.hermes/.env` hinzu:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Starten Sie dann das Gateway:

```bash
hermes gateway
```

Der Bot sollte innerhalb weniger Sekunden in Discord online erscheinen. Senden Sie ihm eine Nachricht, entweder per Direktnachricht oder in einem Kanal, den er sehen kann.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Erstellen eines Telegram-Bots

1. Öffnen Sie Telegram und schreiben Sie **@BotFather** eine Nachricht.
2. Senden Sie `/newbot` und folgen Sie den Anweisungen. Speichern Sie den erhaltenen Bot-Token.

#### Konfigurieren von Hermes für Telegram

Fügen Sie Folgendes zu `~/.hermes/.env` hinzu:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Sie kennen Ihre Telegram-Benutzer-ID nicht?** Schreiben Sie [@userinfobot](https://t.me/userinfobot) in Telegram eine Nachricht, er antwortet mit Ihrer numerischen ID.

Starten Sie dann das Gateway:

```bash
hermes gateway
```

Senden Sie Ihrem Bot in Telegram eine beliebige Nachricht, um ihn zu testen. Sie können nun per Telegram-Direktnachricht mit Ihrem Agenten chatten. Die [vollständige Telegram-Einrichtungsanleitung](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) enthält Informationen zum Webhook-Modus und weiteren erweiterten Optionen.

---

## Nächste Schritte

Nachdem Ihr Agent nun Befehle von Ihrem Smartphone entgegennehmen und auf Ihrem lokalen Rechner ausführen kann, sind hier drei Richtungen, die sich zur weiteren Erkundung lohnen:

1. **Automatisierter Rechercheüberblick**: Planen Sie, dass Hermes jeden Morgen das Web nach Themen durchsucht, die Sie interessieren, die Ergebnisse mit Ihrem lokalen Modell zusammenfasst und eine Übersicht per Telegram oder Discord an Ihr Smartphone sendet, alles läuft dabei auf Ihrer eigenen Hardware ohne Cloud-Kosten.

2. **Codeüberprüfung auf Abruf**: Verweisen Sie Hermes auf ein GitHub-Repository, bitten Sie es, offene Pull-Requests zu überprüfen, und lassen Sie es Kommentare oder eine Zusammenfassung an Ihren Chat zurückmelden. Mit dem Docker-Terminal-Backend laufen alle Git-Operationen innerhalb der Sandbox ab, sodass Ihr Host sauber bleibt.

3. **Lokaler Dateiassistent**: Geben Sie Hermes Zugriff auf ein Arbeitsverzeichnis und lassen Sie es Dateien auf Anfrage von Ihrem Smartphone aus organisieren, umbenennen, zusammenfassen oder umwandeln. Da das Docker-Terminal-Backend alle Schreibvorgänge auf den Sandbox-Arbeitsbereich beschränkt, bleiben versehentliche destruktive Vorgänge eingegrenzt.