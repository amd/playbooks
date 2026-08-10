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

## Überblick

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) ist die auf Effizienz ausgerichtete Variante der DeepSeek-V4-Familie — ein Mixture-of-Experts-Modell mit 284 Milliarden Parametern und 13 Milliarden aktiven Parametern. Laut [DeepSeeks technischem Bericht](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) erreicht es 79 % bei SWE-bench Verified und 91,6 % bei LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) ist eine dedizierte Inference-Engine, die speziell für diese Modellarchitektur entwickelt wurde. Statt einer universellen Laufzeitumgebung zielt ds4 direkt auf die DeepSeek-V4-Familie ab und bietet architekturspezifische Kernel-Optimierungen für AMD ROCm™-Software. Aktuell zählt es zu den leistungsstärksten Implementierungen von DeepSeek V4 Flash auf Strix Halo.

Dieses Tutorial zeigt, wie Sie mit `ds4-cockpit`, einer Terminal-UI, ds4 einrichten, Modellgewichte herunterladen und DeepSeek V4 Flash lokal auf der AMD Ryzen™ AI Halo Developer Platform bereitstellen.

## Was Sie lernen werden

- Wie Sie die Terminal-UI `ds4-cockpit` installieren und starten
- Wie Sie den ROCm-Toolbox-Container für ds4 erstellen
- Herunterladen der empfohlenen Quantisierung für einen einzelnen Halo-Knoten
- Starten des ds4-Inferenzservers und Bereitstellen eines OpenAI-kompatiblen Endpunkts
- Verbinden einer Web-UI oder eines Coding-Agenten mit dem lokalen Server

## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->

## Installieren der Softwarevoraussetzungen

> **Systemanforderungen für diese Konfiguration (Single-Node IQ2_XXS mit 126k Kontext):**
> - Ein Strix-Halo-System mit **mindestens 128 GB einheitlichem Speicher (unified memory)**.
> - **Der im BIOS reservierte VRAM (UMA-Framebuffer) sollte auf das Minimum eingestellt sein**, damit der gemeinsam genutzte Speicherpool so groß wie möglich ausfallen kann.
> - Der **gemeinsam genutzte GPU-Speicherpool sollte auf mindestens 110 GB eingestellt sein**: Führen Sie `amd-ttm --set 110` aus (siehe den obigen Schritt zur Speicherkonfiguration) und starten Sie neu. Niedrigere Werte können beim Laden des Modells mit einem 126k-Kontext zu Speicherfehlern (Out-of-Memory) führen. Wenn Ihrem System weniger Speicher zur Verfügung steht, verringern Sie stattdessen den **Context**-Wert im Server Mode.
>
> **Hinweis:** Versuchen Sie zunächst, den **gemeinsam genutzten GPU-Speicherpool** auf **110 GB** einzustellen. Falls Speicherfehler (Out-of-Memory) auftreten, erhöhen Sie den gemeinsam genutzten Speicherpool oder verringern Sie die Kontextgröße.

ds4-cockpit verwendet Container-Toolboxes, um die ds4-Engine auszuführen. Installieren Sie `podman`, `distrobox` und `pipx`:

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

Der ds4-Autor stellt mehrere quantisierte Versionen von DeepSeek V4 Flash im GGUF-Format bereit. Alle unten aufgeführten Modelle verwenden eine Importance-Matrix-Kalibrierung (imatrix), die für die Teile des Modells, die für Coding- und Reasoning-Aufgaben am wichtigsten sind, eine höhere Präzision beibehält.

| Quantisierung | Größe | Beschreibung |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Empfohlen für einen einzelnen 128-GB-Knoten |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Behält die Layer 37–42 in Q4-Präzision für bessere Genauigkeit bei. Passt in 128 GB, lässt aber weniger Platz für den Kontext |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Höhere Qualität. Erfordert zwei Halo-Knoten über Multi-Node-Clustering |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Optionale Erweiterung für spekulatives Decoding zur Verbesserung der Generierungsgeschwindigkeit |

Das **IQ2_XXS imatrix**-Modell ist ein guter Ausgangspunkt. Es passt problemlos auf einen einzelnen Knoten und lässt genügend Speicher für ein angemessenes Kontextfenster übrig.

## Installieren von ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) ist eine leichte Terminal-UI, die den Einstieg mit ds4 auf Strix Halo erleichtert. Sie übernimmt das Erstellen von Toolbox-Containern, das Herunterladen von Modellgewichten und das Starten von Servern. Installieren Sie sie mit `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Starten Sie das Cockpit:
```bash
ds4-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ds4-cockpit
echo "OK: ds4-cockpit is installed and on PATH"
```
<!-- @test:end -->

## Erstellen der Toolbox

Wählen Sie im Tab **Interactive Toolboxes** die neueste verfügbare/stabile Toolbox (z. B. `ds4-rocm-7.2.4`) aus und klicken Sie auf **Create/Update**. Dadurch wird das Container-Image abgerufen und die Toolbox-Umgebung erstellt.


<p align="center">
  <img src="assets/ds4-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ds4-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## Herunterladen des Modells

Gehen Sie zum Tab **Model Manager**. Wählen Sie **IQ2_XXS imatrix (~80.8 GB)** aus dem Dropdown-Menü und klicken Sie auf **Download**. Die Modelldateien werden standardmäßig unter `~/ds4` gespeichert (Sie können den Speicherpfad ändern).

> **Hinweis:** Das IQ2_XXS-Modell ist etwa 80 GB groß, daher kann der Download je nach Internetverbindung eine Weile dauern. Sie können fortfahren, sobald er abgeschlossen ist.

<p align="center">
  <img src="assets/ds4-cockpit-model-manager.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ds4-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ds4-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ds4-cockpit first."
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

## Starten des Servers

Gehen Sie zum Tab **Server Mode**. Wählen Sie das heruntergeladene Modell und die Toolbox aus, und konfigurieren Sie dann die Kontextgröße, den Host und den Port. Klicken Sie anschließend auf **Start ds4-server**.

> **Tipp** Eine Kontextgröße von `126000` ist ein vernünftiger Ausgangswert, der auf einem einzelnen Knoten passen sollte — Sie können sie höher einstellen, wenn Sie über zusätzlichen Speicher verfügen, oder niedriger, wenn Speicherfehler (Out-of-Memory) auftreten. Der Port (`8000` in diesem Leitfaden) ist beliebig; wählen Sie einen freien Port.

> **KV Disk Cache (optional).** Das Aktivieren von **KV Disk Cache** lagert den KV-Cache auf die Festplatte aus (unter **Host Cache Dir**, standardmäßig `~/.cache/ds4-kv`), sodass wiederholte Systemprompts von der SSD wiederhergestellt statt neu berechnet werden. Dies ist eine Leistungsoptimierung für Coding-Agent-Workflows mit langen, wiederholten Prompts und **nicht erforderlich**, um den Server auszuführen.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Der Server wird gestartet und lauscht auf Port 8000, wodurch ein OpenAI-kompatibler API-Endpunkt unter `http://localhost:8000/v1` bereitgestellt wird.

**Kurzer Test:**
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
  echo "No .gguf model found under $MODEL_DIR. Download it in ds4-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Remove any stale instance, then start ds4-server detached (same flags ds4-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns=keep-id \
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
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Öffnen Sie `http://localhost:3000` in Ihrem Browser, um mit dem Chatten zu beginnen.
## Verbinden eines Coding-Agenten

Der ds4-Server stellt sowohl OpenAI- als auch Anthropic-kompatible Endpunkte bereit, sodass die meisten Coding-Agenten sich direkt damit verbinden können. Um ihn beispielsweise zum `pi`-Coding-Agenten hinzuzufügen, fügen Sie den folgenden Block zu `~/.pi/agent/models.json` hinzu:

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

> **Tipp**: Wenn Ihr Coding-Agent oder Ihre Web-UI auf einem anderen Rechner als der Halo-Plattform läuft, müssen Sie Port 8000 über SSH weiterleiten:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Nächste Schritte

- **Multi-Node-Clustering**: Wenn Sie über zwei Halo-Geräte verfügen, unterstützt ds4 die Verteilung des Q4-Modells (~153 GB) auf beide Rechner mittels Pipeline-Parallelität. Weitere Informationen zur Einrichtung finden Sie in der [ds4-toolbox-Dokumentation](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Spekulatives Dekodieren (MTP)**: Laden Sie die MTP-Gewichte (~3,6 GB) herunter und übergeben Sie `--mtp` an den Server für eine höhere Generierungsgeschwindigkeit.
- **KV-Cache-Auslagerung auf Datenträger**: Aktivieren Sie für Coding-Agent-Workflows `--kv-disk-dir`, damit wiederkehrende System-Prompts von der SSD wiederhergestellt werden, anstatt jedes Mal neu berechnet zu werden.

Weitere Informationen finden Sie im [ds4-Repository](https://github.com/antirez/ds4) und in der [ds4-cockpit-Toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox).