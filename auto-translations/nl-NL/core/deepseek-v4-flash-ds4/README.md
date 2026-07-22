<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> Deze playbook gebruikt speciale tags die GitHub niet kan weergeven. Ga naar [amd.com/playbooks](https://amd.com/playbooks) om deze inhoud correct te bekijken.
<!-- @github-only:end -->

## Overzicht

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) is de op efficiëntie gerichte variant van de DeepSeek V4-familie — een Mixture of Experts-model met 284 miljard parameters en 13 miljard actieve parameters. Volgens [het technische rapport van DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) scoort het 79% op SWE-bench Verified en 91,6% op LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) is een speciale inference-engine die specifiek voor deze modelarchitectuur is gebouwd. In plaats van een algemene runtime richt ds4 zich rechtstreeks op de DeepSeek V4-familie, met architectuurspecifieke kernel-optimalisaties voor AMD ROCm™-software. Het is momenteel een van de best presterende implementaties van DeepSeek V4 Flash op Strix Halo.

Deze tutorial laat zien hoe je `ds4-cockpit`, een terminal-UI, gebruikt om ds4 in te stellen, modelgewichten te downloaden en DeepSeek V4 Flash lokaal te serveren op het AMD Ryzen™ AI Halo Developer Platform.

## Wat je gaat leren

- Hoe je de `ds4-cockpit`-terminal-UI installeert en start
- Hoe je de ds4 ROCm toolbox-container aanmaakt
- Het downloaden van de aanbevolen quantisatie voor één enkele Halo-node
- Het starten van de ds4 inference-server en het beschikbaar stellen van een OpenAI-compatibel endpoint
- Het verbinden van een Web UI of coding agent met de lokale server

<!-- @setup:memory_config -->

## Softwarevereisten installeren

> **Systeemvereisten voor deze configuratie (single-node IQ2_XXS met 126k context):**
> - Een Strix Halo-systeem met **minimaal 128 GB gedeeld geheugen (unified memory)**.
> - **BIOS dedicated VRAM (UMA frame buffer) ingesteld op het minimum**, zodat de gedeelde geheugenpool zo groot mogelijk kan zijn.
> - De GPU **shared-memory pool ingesteld op ten minste 110 GB**: voer `amd-ttm --set 110` uit (zie de bovenstaande stap voor geheugenconfiguratie) en start opnieuw op. Lagere waarden mislukken met een out-of-memory-fout wanneer het model wordt geladen met een context van 126k. Als je systeem minder geheugen beschikbaar heeft, verlaag dan in plaats daarvan de waarde **Context** in Server Mode.

ds4-cockpit gebruikt container-toolboxen om de ds4-engine uit te voeren. Installeer `podman`, `distrobox` en `pipx`:

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

## Beschikbare quantisaties

De auteur van ds4 biedt verschillende gequantiseerde versies van DeepSeek V4 Flash aan in GGUF-formaat. Alle onderstaande modellen gebruiken importance matrix (imatrix)-kalibratie, wat een hogere precisie behoudt voor de onderdelen van het model die het belangrijkst zijn voor coderings- en redeneertaken.

| Quantisatie | Grootte | Beschrijving |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Aanbevolen voor één enkele node met 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Houdt lagen 37–42 op Q4-precisie voor betere nauwkeurigheid. Past in 128 GB, maar laat minder ruimte over voor context |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Hogere kwaliteit. Vereist twee Halo-nodes via multi-node clustering |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Optionele add-on voor speculative decoding om de generatiesnelheid te verbeteren |

Het **IQ2_XXS imatrix**-model is een goed startpunt. Het past comfortabel op één node en laat voldoende geheugen over voor een redelijk contextvenster.

## ds4-cockpit installeren

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) is een lichte terminal-UI die het gemakkelijk maakt om aan de slag te gaan met ds4 op Strix Halo. Het regelt het aanmaken van toolbox-containers, het downloaden van modelgewichten en het starten van servers. Installeer het met `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Start de cockpit:
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

## De toolbox aanmaken

Selecteer in het tabblad **Interactive Toolboxes** de nieuwste beschikbare toolbox (bijv. `ds4-rocm-7.2.4`) en klik op **Create/Update**. Dit haalt de container-image op en maakt de toolbox-omgeving aan.

> **Tip**: De toolbox-versie zal in de loop van de tijd veranderen naarmate nieuwere ROCm-builds worden uitgebracht. Kies de nieuwste die beschikbaar is in de lijst.

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

## Het model downloaden

Ga naar het tabblad **Model Manager**. Selecteer **IQ2_XXS imatrix (~80,8 GB)** in de vervolgkeuzelijst en klik op **Download**. De modelbestanden worden standaard opgeslagen in `~/ds4` (je kunt het opslagpad wijzigen).

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

## De server starten

Ga naar het tabblad **Server Mode**. Selecteer het gedownloade model en de toolbox, en configureer vervolgens de contextgrootte (bijv. 126000), host en poort (8000). Klik wanneer je klaar bent op **Start ds4-server**.

> **KV Disk Cache (optioneel).** Door **KV Disk Cache** in te schakelen, wordt de KV-cache uitgeladen naar schijf (in **Host Cache Dir**, standaard `~/.cache/ds4-kv`), zodat herhaalde systeemprompts worden hersteld vanaf SSD in plaats van opnieuw te worden berekend. Dit is een prestatie-optimalisatie voor coding-agent-workflows met lange, herhaalde prompts, en is **niet vereist** om de server te draaien.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

De server start op en luistert op poort 8000, waarbij een OpenAI-compatibel API-endpoint beschikbaar wordt gesteld op `http://localhost:8000/v1`.

**Snelle test:**
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

## Een Web UI verbinden

Je kunt elke chatinterface verbinden die het OpenAI API-formaat ondersteunt. Om bijvoorbeeld HuggingFace ChatUI te gebruiken:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Open `http://localhost:3000` in je browser om te beginnen met chatten.

## Een coding agent verbinden

De ds4-server stelt zowel OpenAI- als Anthropic-compatibele endpoints beschikbaar, dus de meeste coding agents kunnen er rechtstreeks verbinding mee maken. Om het bijvoorbeeld toe te voegen aan de `pi`-coding agent, voeg je het volgende blok toe aan `~/.pi/agent/models.json`:

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

> **Tip**: Als je coding agent of Web UI op een andere machine draait dan het Halo-platform, moet je poort 8000 doorsturen via SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```
## Volgende stappen

- **Multi-node clustering**: Als u twee Halo-apparaten hebt, ondersteunt ds4 het verdelen van het Q4-model (~153 GB) over beide machines via pipeline parallellisme. Zie de [ds4-toolbox-documentatie](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) voor installatie-instructies.
- **Speculative decoding (MTP)**: Download de MTP-gewichten (~3,6 GB) en geef `--mtp` mee aan de server voor een snellere generatiesnelheid.
- **KV cache disk offloading**: Schakel voor workflows met coderingsagents `--kv-disk-dir` in, zodat herhaalde systeempromts vanaf de SSD worden hersteld in plaats van telkens opnieuw te worden berekend.

Zie voor meer informatie de [ds4-repository](https://github.com/antirez/ds4) en de [ds4-cockpit-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox).