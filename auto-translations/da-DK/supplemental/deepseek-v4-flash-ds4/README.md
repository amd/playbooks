<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversigt

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) er den effektivitetsfokuserede variant af DeepSeek V4-familien — en Mixture of Experts-model med 284 milliarder parametre og 13 milliarder aktive parametre. Ifølge [DeepSeeks tekniske rapport](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) opnår den 79 % på SWE-bench Verified og 91,6 % på LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) er en dedikeret inference-motor bygget specifikt til denne modelarkitektur. Frem for en generel runtime retter ds4 sig direkte mod DeepSeek V4-familien med arkitekturspecifikke kernel-optimeringer til AMD ROCm™-software. Det er i øjeblikket en af de bedst ydende implementeringer af DeepSeek V4 Flash på Strix Halo.

Denne tutorial viser, hvordan du bruger `ds4-cockpit`, en terminal-UI, til at opsætte ds4, downloade modelvægte og starte servering af DeepSeek V4 Flash lokalt på AMD Ryzen™ AI Halo Developer Platform.

## Hvad du vil lære

- Hvordan du installerer og starter terminal-UI'en `ds4-cockpit`
- Hvordan du opretter ds4 ROCm toolbox-containeren
- Download af den anbefalede kvantisering til en enkelt Halo-node
- Start af ds4 inference-serveren og eksponering af et OpenAI-kompatibelt endpoint
- Forbindelse af en Web UI eller coding-agent til den lokale server

## Indstilling af hukommelseskonfigurationen

<!-- @require:memory-config -->

## Installation af softwareforudsætninger

> **Systemkrav til denne konfiguration (single-node IQ2_XXS ved 126k kontekst):**
> - Et Strix Halo-system med **mindst 128 GB delt hukommelse (unified memory)**.
> - **BIOS-dedikeret VRAM (UMA frame buffer) sat til minimum**, så den delte hukommelsespulje kan være så stor som muligt.
> - GPU'ens **delte hukommelsespulje sat til mindst 110 GB**: kør `amd-ttm --set 110` (se trinnet med hukommelseskonfiguration ovenfor) og genstart. Lavere værdier kan give hukommelsesfejl (out-of-memory), når modellen indlæses med en 126k kontekst. Hvis dit system har mindre tilgængelig hukommelse, kan du i stedet sænke **Context**-værdien i Server Mode.
>
> **Bemærk:** Prøv at sætte **GPU'ens delte hukommelsespulje** til **110 GB** som udgangspunkt. Hvis du støder på out-of-memory-fejl, så øg den delte hukommelsespulje eller sænk kontekststørrelsen.

ds4-cockpit bruger container-toolboxes til at køre ds4-motoren. Installer `podman`, `distrobox` og `pipx`:

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

## Tilgængelige kvantiseringer

ds4-forfatteren tilbyder flere kvantiserede versioner af DeepSeek V4 Flash i GGUF-format. Alle modeller nedenfor bruger importance matrix (imatrix)-kalibrering, hvilket bevarer højere præcision for de dele af modellen, der betyder mest for kodnings- og ræsonneringsopgaver.

| Kvantisering | Størrelse | Beskrivelse |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Anbefales til en enkelt 128 GB node |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Beholder lag 37–42 med Q4-præcision for bedre nøjagtighed. Passer i 128 GB, men efterlader mindre plads til kontekst |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Højere kvalitet. Kræver to Halo-noder via multi-node clustering |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Valgfrit tilføjelsesmodul til spekulativ afkodning for at forbedre genereringshastigheden |

**IQ2_XXS imatrix**-modellen er et godt udgangspunkt. Den passer komfortabelt på en enkelt node og efterlader nok hukommelse til et rimeligt kontekstvindue.

## Installation af ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) er en let terminal-UI, der gør det nemt at komme i gang med ds4 på Strix Halo. Den håndterer oprettelse af toolbox-containere, download af modelvægte og start af servere. Installer den med `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Start cockpit'en:
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

## Oprettelse af toolboxen

Under fanen **Interactive Toolboxes** skal du vælge den seneste tilgængelige/stabile toolbox (f.eks. `ds4-rocm-7.2.4`) og klikke på **Create/Update**. Dette henter container-billedet og opretter toolbox-miljøet.


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

## Download af modellen

Gå til fanen **Model Manager**. Vælg **IQ2_XXS imatrix (~80,8 GB)** i dropdown-menuen, og klik på **Download**. Modelfilerne gemmes som standard i `~/ds4` (du kan ændre lagringsstien).

> **Bemærk:** IQ2_XXS-modellen fylder cirka 80 GB, så downloadet kan tage et stykke tid afhængigt af din forbindelse. Du kan fortsætte, når det er færdigt.

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

## Start af serveren

Gå til fanen **Server Mode**. Vælg den downloadede model og toolboxen, og konfigurér derefter kontekststørrelse, host og port. Når du er klar, skal du klikke på **Start ds4-server**.

> **Tip** En kontekststørrelse på `126000` er en fornuftig startværdi, som burde passe på en enkelt node — du kan sætte den højere, hvis du har hukommelse til overs, eller sænke den, hvis du støder på out-of-memory-fejl. Porten (`8000` i denne guide) er vilkårlig; vælg en hvilken som helst ledig port.

> **KV Disk Cache (valgfrit).** Hvis du slår **KV Disk Cache** til, aflastes KV-cachen til disk (i **Host Cache Dir**, som standard `~/.cache/ds4-kv`), så gentagne systemprompter genskabes fra SSD i stedet for at blive genberegnet. Det er en performance-optimering til coding-agent-arbejdsgange med lange, gentagne prompter, og er **ikke påkrævet** for at køre serveren.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Serveren starter og lytter på port 8000, hvilket eksponerer et OpenAI-kompatibelt API-endpoint på `http://localhost:8000/v1`.

**Hurtig test:**
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

## Forbindelse af en Web UI

Du kan forbinde enhver chatgrænseflade, der understøtter OpenAI API-formatet. For eksempel for at bruge HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Åbn `http://localhost:3000` i din browser for at begynde at chatte.
## Tilslutning af en kodeagent

ds4-serveren eksponerer både OpenAI- og Anthropic-kompatible endpoints, så de fleste kodeagenter kan oprette forbindelse til den direkte. For eksempel, for at tilføje den til `pi`-kodeagenten, tilføj følgende blok til `~/.pi/agent/models.json`:

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

> **Tip**: Hvis din kodeagent eller Web UI kører på en anden maskine end Halo-platformen, skal du videresende port 8000 via SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Næste trin

- **Multi-node clustering**: Hvis du har to Halo-enheder, understøtter ds4 distribution af Q4-modellen (~153 GB) på tværs af begge maskiner via pipeline-parallelisme. Se [ds4-toolbox-dokumentationen](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) for opsætningsinstruktioner.
- **Spekulativ afkodning (MTP)**: Download MTP-vægtene (~3,6 GB), og send `--mtp` til serveren for hurtigere genereringshastighed.
- **KV-cache disk-offloading**: For kodeagent-workflows, aktivér `--kv-disk-dir`, så gentagne systemprompter gendannes fra SSD i stedet for at blive genberegnet hver gang.

For mere information, se [ds4-repositoriet](https://github.com/antirez/ds4) og [ds4-cockpit-toolboxen](https://github.com/kyuz0/strix-halo-ds4-toolbox).