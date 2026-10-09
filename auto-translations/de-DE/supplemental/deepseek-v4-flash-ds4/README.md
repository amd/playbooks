<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Übersicht

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) ist die auf Effizienz ausgelegte Variante der DeepSeek-V4-Familie — ein Mixture-of-Experts-Modell mit 284 Milliarden Parametern und 13 Milliarden aktiven Parametern. Laut [DeepSeeks technischem Bericht](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) erzielt es 79 % auf SWE-bench Verified und 91,6 % auf LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) ist eine dedizierte Inference-Engine, die speziell für diese Modellarchitektur entwickelt wurde. Anstatt einer allgemeinen Laufzeitumgebung richtet sich ds4 direkt an die DeepSeek-V4-Familie mit architekturspezifischen Kernel-Optimierungen für AMD ROCm™ Software. Es ist derzeit eine der leistungsstärksten Implementierungen von DeepSeek V4 Flash auf Strix Halo.

Dieses Tutorial zeigt, wie Sie mit `ai-toolbox-cockpit`, einer Terminal-UI, ds4 einrichten, Modellgewichte herunterladen und DeepSeek V4 Flash lokal auf der AMD Ryzen™ AI Halo Developer Platform bereitstellen.

## Was Sie lernen werden

- Wie man die `ai-toolbox-cockpit`-Terminal-UI installiert und startet
- Wie man den ds4-ROCm-Toolbox-Container erstellt
- Herunterladen der empfohlenen Quantisierung für einen einzelnen Halo-Knoten
- Starten des ds4-Inferenzservers und Bereitstellen eines OpenAI-kompatiblen Endpunkts
- Verbinden einer Web-UI oder eines Coding-Agenten mit dem lokalen Server

## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->

## Installieren der Software-Voraussetzungen

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:podman,distrobox,ds4-cockpit,ds4-toolbox-image -->

> **Systemanforderungen für diese Konfiguration (Single-Node IQ2_XXS bei 126k Kontext):**
> - Ein Strix-Halo-System mit **mindestens 128 GB unified memory**.
> - **Der dedizierte VRAM im BIOS (UMA-Framebuffer) sollte auf das Minimum gesetzt werden**, damit der gemeinsam genutzte Speicherpool so groß wie möglich sein kann.
> - Der **gemeinsam genutzte Speicherpool der GPU muss auf mindestens 110 GB gesetzt sein**: Führen Sie `amd-ttm --set 110` aus (siehe den Schritt zur Speicherkonfiguration oben) und starten Sie neu. Niedrigere Werte können beim Laden des Modells mit einem 126k-Kontext zu Out-of-Memory-Fehlern führen. Falls Ihr System über weniger verfügbaren Speicher verfügt, verringern Sie stattdessen den **Context**-Wert im Server-Modus.
>
> **Hinweis:** Versuchen Sie zunächst, den **gemeinsam genutzten GPU-Speicherpool** auf **110 GB** zu setzen. Wenn Out-of-Memory-Fehler auftreten, erhöhen Sie den gemeinsam genutzten Speicherpool oder verringern Sie die Kontextgröße.

ai-toolbox-cockpit verwendet Container-Toolboxes, um die ds4-Engine auszuführen. Installieren Sie `podman`, `distrobox` und `pipx`:

```bash
sudo apt update
sudo apt install -y podman distrobox pipx
```

<!-- @test:id=ds4-prereqs-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
podman --version
distrobox version 2>/dev/null || distrobox --version
pipx --version
echo "OK: podman, distrobox, and pipx are installed"
```
<!-- @test:end -->

## Verfügbare Quantisierungen

Der Autor von ds4 stellt mehrere quantisierte Versionen von DeepSeek V4 Flash im GGUF-Format bereit. Alle unten aufgeführten Modelle verwenden eine Kalibrierung mittels Importance Matrix (imatrix), wodurch eine höhere Präzision für die Teile des Modells erhalten bleibt, die für Coding- und Reasoning-Aufgaben am wichtigsten sind.

| Quantisierung | Größe | Beschreibung |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Empfohlen für einen einzelnen 128-GB-Knoten |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Behält die Schichten 37–42 in Q4-Präzision für bessere Genauigkeit bei. Passt in 128 GB, lässt aber weniger Platz für Kontext |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Höhere Qualität. Erfordert zwei Halo-Knoten über Multi-Node-Clustering |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Optionale Erweiterung für Speculative Decoding zur Verbesserung der Generierungsgeschwindigkeit |

Das **IQ2_XXS imatrix**-Modell ist ein guter Ausgangspunkt. Es passt problemlos auf einen einzelnen Knoten und lässt genügend Speicher für ein angemessenes Kontextfenster.

## Installieren von ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) ist eine schlanke Terminal-UI, die die Installation verschiedener KI-Backends erleichtert. Wir verwenden sie, um die Erstellung unseres ds4-Containers, den Download der Modellgewichte und das Starten von Servern zu übernehmen. Installieren Sie sie mit `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Starten Sie das Cockpit:
```bash
ai-toolbox-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ai-toolbox-cockpit
echo "OK: ai-toolbox-cockpit is installed and on PATH"
```
<!-- @test:end -->

## Schritt 1: Erstellen der Toolbox

Wählen Sie im Tab **Interactive Toolboxes** die neueste verfügbare/stabile Toolbox für ds4 (z. B. `ds4-rocm-10.0`) und klicken Sie auf **Create/Update**. Dadurch wird das Container-Image abgerufen und die Toolbox-Umgebung erstellt.


<p align="center">
  <img src="assets/ai-toolbox-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ai-toolbox-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## Schritt 2: Herunterladen des Modells

Gehen Sie zum Tab **Models**. Wählen Sie zunächst das Backend (ds4) aus. Wählen Sie dann **IQ2_XXS imatrix (~80.8 GB)** aus dem Dropdown-Menü und klicken Sie auf **Download**. Die Modelldateien werden standardmäßig unter `~/ds4` gespeichert (Sie können den Speicherpfad ändern).

> **Hinweis:** Das IQ2_XXS-Modell ist etwa 80 GB groß, daher kann der Download je nach Ihrer Verbindung eine Weile dauern. Sie können fortfahren, sobald er abgeschlossen ist.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-models.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ai-toolbox-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ai-toolbox-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ai-toolbox-cockpit first."
  exit 1
fi

# Prefer to confirm the recommended IQ2_XXS imatrix quantization is present.
if find "$model_dir" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' | grep -q .; then
  echo "OK: IQ2_XXS imatrix model is downloaded"
else
  echo "OK: a GGUF model is present (recommended IQ2_XXS imatrix file not detected by name)"
fi
```
<!-- @test:end -->

## Schritt 3: Starten des Servers

Gehen Sie zum Tab **Server Mode**. Wählen Sie das heruntergeladene Modell und die Toolbox aus, konfigurieren Sie dann die Kontextgröße, den Host und den Port. Klicken Sie anschließend auf **Start ds4-server**.

> **Tipp** Eine Kontextgröße von `126000` ist ein vernünftiger Ausgangswert, der auf einen einzelnen Knoten passen sollte — Sie können sie höher setzen, wenn Sie über ausreichend Speicher verfügen, oder niedriger, falls Out-of-Memory-Fehler auftreten. Der Port (`8000` in diesem Leitfaden) ist beliebig; wählen Sie einen beliebigen freien Port.

> **KV Disk Cache (optional).** Das Aktivieren von **KV Disk Cache** lagert den KV-Cache auf die Festplatte aus (unter **Host Cache Dir**, standardmäßig `~/.cache/ds4-kv`), sodass wiederholte System-Prompts von der SSD wiederhergestellt werden, anstatt neu berechnet zu werden. Dies ist eine Leistungsoptimierung für Coding-Agent-Workflows mit langen, wiederholten Prompts und **nicht erforderlich**, um den Server auszuführen.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Der Server startet und lauscht auf Port 8000, wodurch ein OpenAI-kompatibler API-Endpunkt unter `http://localhost:8000/v1` bereitgestellt wird.

**Schnelltest:**
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

<!-- @test:id=ds4-server-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

# This runner is shared with other playbooks, and ds4 at a 126k context consumes almost the entire GPU memory pool.
# So rather than keeping ds4 resident, CI starts the server, verifies a chat completion, then stops it again.
# This frees the memory for the next job.
# ds4 has no separate "unload"; stopping the server process is what releases the ~80 GB model.

CONTAINER="ds4-ci-server"
MODEL_DIR="$HOME/ds4"

# Locate the downloaded model (prefer the recommended IQ2_XXS imatrix file).
model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' 2>/dev/null | head -1)"
if [ -z "$model_file" ]; then
  model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*.gguf' 2>/dev/null | head -1)"
fi
if [ -z "$model_file" ]; then
  echo "No .gguf model found under $MODEL_DIR. Download it in ai-toolbox-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# keep-id maps the calling user into the container. Root does not need it, and as root it cannot
# be combined with --ipc=host (crun fails to mount /dev/mqueue), so root keeps the host user namespace.
userns=keep-id
if [ "$(id -u)" -eq 0 ]; then
  userns=host
fi

# Remove any stale instance, then start ds4-server detached (same flags ai-toolbox-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns="$userns" \
  -p 127.0.0.1:8000:8000 \
  -v "$MODEL_DIR":/models:ro \
  "$image" \
  ds4-server -m "/models/$model_name" --ctx 126000 --host 0.0.0.0 --port 8000

# Wait for readiness; the ~80 GB model can take a few minutes to load.
up=false
for i in $(seq 1 240); do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8000/v1/models || true)"
  if [ -n "$code" ] && [ "$code" != "000" ]; then
    up=true
    break
  fi
  if ! podman inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null | grep -q true; then
    echo "ds4-server container exited during startup:"
    podman logs "$CONTAINER" 2>&1 | tail -40 || true
    exit 1
  fi
  sleep 2
done

if [ "$up" != "true" ]; then
  echo "ds4 server did not become ready on http://127.0.0.1:8000"
  podman logs "$CONTAINER" 2>&1 | tail -40 || true
  exit 1
fi
echo "OK: ds4 server is responding on :8000"

body='{
  "model": "deepseek-v4-flash",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32,
  "stream": false
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from ds4 /v1/chat/completions"
  exit 1
fi

export DS4_OUT="$out"
python3 - <<'PY'
import json, os, sys

data = json.loads(os.environ["DS4_OUT"])
choices = data.get("choices")
if not choices:
    print("Response has no 'choices':")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

message = choices[0].get("message", {}) or {}
content = message.get("content") or message.get("reasoning_content")
if not content:
    print("Response choice has empty content:")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

print("OK: ds4 chat/completions returned content")
PY

echo "OK: ds4 server test complete; server stopped and GPU memory released"
```
<!-- @test:end -->
## Verbinden einer Web-UI

Sie können jede Chat-Oberfläche verbinden, die das OpenAI-API-Format unterstützt. Um beispielsweise HuggingFace ChatUI zu verwenden:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Öffnen Sie `http://localhost:3000` in Ihrem Browser, um mit dem Chatten zu beginnen.

> **Hinweis:** `--network=host` platziert die Web-UI im Netzwerk des Hosts, sodass sie den ds4-Server direkt über `localhost` erreichen kann. Dadurch bleibt der ds4-Server an das Loopback-Interface gebunden (er muss nicht auf anderen Schnittstellen freigegeben werden).

> **Tipp:** Der Port der Web-UI (hier `3000`, über `PORT` festgelegt) ist beliebig wählbar — nutzen Sie einen beliebigen freien Port, falls `3000` bereits belegt ist, und öffnen Sie diesen Port stattdessen in Ihrem Browser. Stellen Sie sicher, dass der Port in `OPENAI_BASE_URL` mit dem Port übereinstimmt, auf dem Ihr ds4-Server läuft.

## Verbinden eines Coding-Agenten

Der ds4-Server stellt sowohl OpenAI- als auch Anthropic-kompatible Endpunkte bereit, sodass sich die meisten Coding-Agenten direkt damit verbinden können. Um ihn beispielsweise zum `pi`-Coding-Agenten hinzuzufügen, fügen Sie den folgenden Block zu `~/.pi/agent/models.json` hinzu:

```json
"ds4": {
  "name": "ds4.c local",
  "baseUrl": "http://localhost:8000/v1",
  "api": "openai-completions",
  "apiKey": "dsv4-local",
  "compat": {
    "supportsStore": false,
    "supportsDeveloperRole": false,
    "supportsReasoningEffort": true,
    "supportsUsageInStreaming": true,
    "maxTokensField": "max_tokens",
    "supportsStrictMode": false,
    "thinkingFormat": "deepseek",
    "requiresReasoningContentOnAssistantMessages": true
  },
  "models": [
    {
      "id": "deepseek-v4-flash",
      "name": "DeepSeek V4 Flash (ds4.c local)",
      "reasoning": true,
      "thinkingLevelMap": {
        "off": null,
        "minimal": "low",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "input": ["text"],
      "contextWindow": 131072,
      "maxTokens": 65536,
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
    }
  ]
}
```

> **Tipp**: Wenn Ihr Coding-Agent oder Ihre Web-UI auf einem anderen Rechner als der Halo-Plattform läuft, müssen Sie den Server-Port (hier `8000`) über SSH weiterleiten:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Nächste Schritte

- **Multi-Node-Clustering**: Wenn Sie zwei Halo-Geräte besitzen, unterstützt ds4 die Verteilung des Q4-Modells (~153 GB) auf beide Maschinen mittels Pipeline-Parallelität. Weitere Anweisungen zur Einrichtung finden Sie in der [ds4-toolbox-Dokumentation](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Spekulatives Decoding (MTP)**: Laden Sie die MTP-Gewichte (~3,6 GB) herunter und übergeben Sie `--mtp` an den Server, um die Generierungsgeschwindigkeit zu erhöhen.
- **Auslagern des KV-Cache auf die Festplatte**: Aktivieren Sie für Coding-Agent-Workflows `--kv-disk-dir`, damit wiederkehrende Systemprompts von der SSD wiederhergestellt werden, anstatt jedes Mal neu berechnet zu werden.

Weitere Informationen finden Sie im [ds4-Repository](https://github.com/antirez/ds4) und in der [ds4-cockpit-Toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox).