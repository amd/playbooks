<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overzicht

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) is de op efficiëntie gerichte variant van de DeepSeek V4-familie — een Mixture of Experts-model met 284 miljard parameters, waarvan 13 miljard actieve parameters. Volgens [het technische rapport van DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) scoort het 79% op SWE-bench Verified en 91,6% op LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) is een speciaal inferentie-engine die specifiek is gebouwd voor deze modelarchitectuur. In plaats van een algemene runtime richt ds4 zich rechtstreeks op de DeepSeek V4-familie, met architectuurspecifieke kernel-optimalisaties voor AMD ROCm™-software. Het is momenteel een van de best presterende implementaties van DeepSeek V4 Flash op Strix Halo.

Deze tutorial laat zien hoe je `ai-toolbox-cockpit`, een terminal-UI, kunt gebruiken om ds4 in te stellen, modelgewichten te downloaden en DeepSeek V4 Flash lokaal te laten draaien op het AMD Ryzen™ AI Halo Developer Platform.

## Wat je leert

- Hoe je de `ai-toolbox-cockpit` terminal-UI installeert en start
- Hoe je de ds4 ROCm-toolboxcontainer maakt
- Het downloaden van de aanbevolen kwantisering voor een enkele Halo-node
- Het starten van de ds4-inferentieserver en het blootstellen van een OpenAI-compatibel eindpunt
- Het verbinden van een Web UI of codeeragent met de lokale server

## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

## Softwarevereisten installeren

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:podman,distrobox,ds4-cockpit,ds4-toolbox-image -->

> **Systeemvereisten voor deze configuratie (enkele node, IQ2_XXS bij 126k context):**
> - Een Strix Halo-systeem met **ten minste 128 GB unified memory**.
> - **BIOS dedicated VRAM (UMA frame buffer) ingesteld op het minimum**, zodat de gedeelde geheugenpool zo groot mogelijk kan zijn.
> - De **gedeelde geheugenpool van de GPU ingesteld op ten minste 110 GB**: voer `amd-ttm --set 110` uit (zie de bovenstaande stap voor geheugenconfiguratie) en herstart. Lagere waarden kunnen leiden tot out-of-memory-fouten wanneer het model wordt geladen met een context van 126k. Als je systeem minder geheugen beschikbaar heeft, verlaag dan in plaats daarvan de waarde van **Context** in Server Mode.
>
> **Opmerking:** Probeer de **gedeelde geheugenpool van de GPU** als uitgangspunt in te stellen op **110 GB**. Als je out-of-memory-fouten tegenkomt, verhoog dan de gedeelde geheugenpool of verlaag de contextgrootte.

ai-toolbox-cockpit gebruikt containertoolboxen om de ds4-engine uit te voeren. Installeer `podman`, `distrobox` en `pipx`:

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

## Beschikbare kwantiseringen

De auteur van ds4 biedt verschillende gekwantiseerde versies van DeepSeek V4 Flash in GGUF-formaat. Alle onderstaande modellen gebruiken importance matrix (imatrix) kalibratie, waardoor hogere precisie behouden blijft voor de delen van het model die het belangrijkst zijn voor codeer- en redeneertaken.

| Kwantisering | Grootte | Beschrijving |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Aanbevolen voor een enkele node van 128 GB |
| [Hybride Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Behoudt lagen 37–42 op Q4-precisie voor betere nauwkeurigheid. Past in 128 GB, maar laat minder ruimte voor context |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Hogere kwaliteit. Vereist twee Halo-nodes via multi-node clustering |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Optionele toevoeging voor speculative decoding om de generatiesnelheid te verbeteren |

Het **IQ2_XXS imatrix**-model is een goed startpunt. Het past gemakkelijk op één node en laat genoeg geheugen over voor een redelijk contextvenster.

## ai-toolbox-cockpit installeren

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) is een lichte terminal-UI die het eenvoudig maakt om verschillende AI-backends te installeren. We gebruiken het om het maken van onze ds4-container, het downloaden van modelgewichten en het starten van servers af te handelen. Installeer het met `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Start de cockpit:
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

## Stap 1: De toolbox maken

Selecteer in het tabblad **Interactive Toolboxes** de nieuwste beschikbare/stabiele toolbox voor ds4 (bijv. `ds4-rocm-10.0`) en klik op **Create/Update**. Hiermee wordt de containerimage opgehaald en de toolboxomgeving aangemaakt.


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

## Stap 2: Het model downloaden

Ga naar het tabblad **Models**. Selecteer eerst de backend (ds4). Selecteer vervolgens **IQ2_XXS imatrix (~80,8 GB)** in de vervolgkeuzelijst en klik op **Download**. De modelbestanden worden standaard opgeslagen in `~/ds4` (je kunt het opslagpad wijzigen).

> **Opmerking:** Het IQ2_XXS-model is ongeveer 80 GB groot, dus het downloaden kan even duren, afhankelijk van je verbinding. Je kunt verdergaan zodra het klaar is.

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

## Stap 3: De server starten

Ga naar het tabblad **Server Mode**. Selecteer het gedownloade model en de toolbox, en configureer vervolgens de contextgrootte, host en poort. Klik, wanneer je klaar bent, op **Start ds4-server**.

> **Tip** Een contextgrootte van `126000` is een redelijke startwaarde die op één node zou moeten passen — je kunt deze hoger instellen als je geheugen over hebt, of lager als je out-of-memory-fouten tegenkomt. De poort (`8000` in deze handleiding) is willekeurig; kies een vrije poort naar keuze.

> **KV Disk Cache (optioneel).** Door **KV Disk Cache** in te schakelen, wordt de KV-cache uitbesteed aan schijf (bij **Host Cache Dir**, standaard `~/.cache/ds4-kv`), zodat herhaalde systeemprompts vanaf SSD worden hersteld in plaats van opnieuw te worden berekend. Dit is een prestatieoptimalisatie voor workflows met codeeragents met lange, herhaalde prompts, en is **niet vereist** om de server te draaien.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

De server start en luistert op poort 8000, waarbij een OpenAI-compatibel API-eindpunt wordt blootgesteld op `http://localhost:8000/v1`.

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
## Een Web UI verbinden

U kunt elke chatinterface verbinden die het OpenAI API-formaat ondersteunt. Om bijvoorbeeld HuggingFace ChatUI te gebruiken:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Open `http://localhost:3000` in uw browser om te beginnen met chatten.

> **Opmerking:** `--network=host` plaatst de Web UI op het netwerk van de host, zodat deze de ds4-server op `localhost` rechtstreeks kan bereiken. Dit zorgt ervoor dat de ds4-server gebonden blijft aan loopback (deze hoeft niet op andere interfaces te worden blootgesteld).

> **Tip:** De poort van de Web UI (`3000` hier, ingesteld via `PORT`) is willekeurig — kies elke vrije poort als `3000` al in gebruik is, en open die poort in uw browser in plaats daarvan. Zorg ervoor dat de poort in `OPENAI_BASE_URL` overeenkomt met de poort waarop uw ds4-server draait.

## Een Coding Agent verbinden

De ds4-server biedt zowel OpenAI- als Anthropic-compatibele endpoints, zodat de meeste coding agents er rechtstreeks verbinding mee kunnen maken. Om het bijvoorbeeld toe te voegen aan de `pi` coding agent, voegt u het volgende blok toe aan `~/.pi/agent/models.json`:

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

> **Tip**: Als uw coding agent of Web UI op een andere machine draait dan het Halo-platform, moet u de serverpoort (`8000` hier) doorsturen via SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Volgende stappen

- **Multi-node clustering**: Als u twee Halo-apparaten heeft, ondersteunt ds4 het verdelen van het Q4-model (~153 GB) over beide machines via pipeline parallellisme. Zie de [ds4-toolbox documentatie](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) voor installatie-instructies.
- **Speculative decoding (MTP)**: Download de MTP-gewichten (~3,6 GB) en geef `--mtp` door aan de server voor snellere generatiesnelheid.
- **KV cache disk offloading**: Schakel voor coding agent-workflows `--kv-disk-dir` in, zodat herhaalde systeemprompts vanaf SSD worden hersteld in plaats van telkens opnieuw te worden berekend.

Zie voor meer informatie de [ds4 repository](https://github.com/antirez/ds4) en de [ds4-cockpit toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox).