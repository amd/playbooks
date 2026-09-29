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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) er den effektivitetsfokuserede variant af DeepSeek V4-familien — en Mixture of Experts-model med 284 milliarder parametre og 13 milliarder aktive parametre. Ifølge [DeepSeeks tekniske rapport](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) scorer den 79% på SWE-bench Verified og 91,6% på LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) er en dedikeret inference-motor bygget specifikt til denne modelarkitektur. I stedet for en generel runtime målretter ds4 direkte DeepSeek V4-familien med arkitekturspecifikke kerneoptimeringer til AMD ROCm™-software. Den er i øjeblikket en af de bedst præsterende implementeringer af DeepSeek V4 Flash på Strix Halo.

Denne vejledning viser, hvordan du bruger `ai-toolbox-cockpit`, en terminal-UI, til at opsætte ds4, downloade modelvægte og starte lokal servering af DeepSeek V4 Flash på AMD Ryzen™ AI Halo Developer Platform.

## Hvad du vil lære

- Hvordan man installerer og starter terminal-UI'en `ai-toolbox-cockpit`
- Hvordan man opretter ds4 ROCm-toolbox-containeren
- Download af den anbefalede kvantisering til en enkelt Halo-node
- Start af ds4-inferenceserveren og eksponering af et OpenAI-kompatibelt endpoint
- Tilslutning af en Web UI eller kodningsagent til den lokale server

## Konfiguration af hukommelsen

<!-- @require:memory-config -->

## Installation af softwareforudsætninger

> **Systemkrav til denne konfiguration (single-node IQ2_XXS med 126k kontekst):**
> - Et Strix Halo-system med **mindst 128 GB samlet hukommelse (unified memory)**.
> - **BIOS dedikeret VRAM (UMA frame buffer) sat til minimum**, så den delte hukommelsespulje kan være så stor som muligt.
> - GPU'ens **delte hukommelsespulje sat til mindst 110 GB**: kør `amd-ttm --set 110` (se trinnet om hukommelseskonfiguration ovenfor) og genstart. Lavere værdier kan resultere i hukommelsesmangel (out-of-memory), når modellen indlæses med en 126k-kontekst. Hvis dit system har mindre hukommelse til rådighed, skal du i stedet sænke værdien **Context** i Server Mode.
>
> **Bemærk:** Prøv at sætte **GPU'ens delte hukommelsespulje** til **110 GB** som udgangspunkt. Hvis du støder på fejl med manglende hukommelse (out-of-memory), skal du øge den delte hukommelsespulje eller sænke kontekststørrelsen.

ai-toolbox-cockpit bruger container-toolboxes til at køre ds4-motoren. Installer `podman`, `distrobox` og `pipx`:

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

Forfatteren bag ds4 leverer flere kvantiserede versioner af DeepSeek V4 Flash i GGUF-format. Alle modeller nedenfor bruger importance matrix (imatrix)-kalibrering, som bevarer højere præcision for de dele af modellen, der betyder mest for kodnings- og ræsonneringsopgaver.

| Kvantisering | Størrelse | Beskrivelse |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Anbefales til en enkelt 128 GB-node |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Beholder lagene 37–42 i Q4-præcision for bedre nøjagtighed. Passer i 128 GB, men efterlader mindre plads til kontekst |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Højere kvalitet. Kræver to Halo-noder via multi-node clustering |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Valgfrit tilføjelsesmodul til spekulativ afkodning for at forbedre genereringshastigheden |

Modellen **IQ2_XXS imatrix** er et godt udgangspunkt. Den passer nemt på en enkelt node og efterlader nok hukommelse til et rimeligt kontekstvindue.

## Installation af ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) er en let terminal-UI, der gør det nemt at installere forskellige AI-backends. Vi bruger den til at håndtere oprettelsen af vores ds4-container, download af modelvægte og start af servere. Installer den med `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Start cockpit:
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

## Trin 1: Oprettelse af toolboxen

Under fanen **Interactive Toolboxes** skal du vælge den nyeste tilgængelige/stabile toolbox til ds4 (f.eks. `ds4-rocm-10.0`) og klikke på **Create/Update**. Dette henter containerimaget og opretter toolbox-miljøet.


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

## Trin 2: Download af modellen

Gå til fanen **Models**. Vælg først backend'en (ds4). Vælg derefter **IQ2_XXS imatrix (~80,8 GB)** i dropdown-menuen, og klik på **Download**. Modelfilerne gemmes som standard i `~/ds4` (du kan ændre lagringsstien).

> **Bemærk:** IQ2_XXS-modellen er cirka 80 GB, så downloadet kan tage et stykke tid afhængigt af din forbindelse. Du kan fortsætte, når det er færdigt.

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

## Trin 3: Start af serveren

Gå til fanen **Server Mode**. Vælg den downloadede model og toolboxen, og konfigurer derefter kontekststørrelse, host og port. Når du er klar, skal du klikke på **Start ds4-server**.

> **Tip** En kontekststørrelse på `126000` er en fornuftig startværdi, som burde passe på en enkelt node — du kan sætte den højere, hvis du har hukommelse til overs, eller lavere, hvis du støder på fejl med manglende hukommelse (out-of-memory). Porten (`8000` i denne vejledning) er vilkårlig; vælg en hvilken som helst ledig port.

> **KV Disk Cache (valgfrit).** Aktivering af **KV Disk Cache** flytter KV-cachen over til disk (under **Host Cache Dir**, standard `~/.cache/ds4-kv`), så gentagne systemprompter gendannes fra SSD i stedet for at blive genberegnet. Det er en performanceoptimering til arbejdsgange med kodningsagenter, der bruger lange, gentagne prompter, og er **ikke påkrævet** for at køre serveren.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
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
## Tilslutning af en webgrænseflade

Du kan forbinde enhver chatgrænseflade, der understøtter OpenAI API-formatet. For eksempel for at bruge HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Åbn `http://localhost:3000` i din browser for at begynde at chatte.

> **Bemærk:** `--network=host` placerer webgrænsefladen på værtens netværk, så den direkte kan nå ds4-serveren på `localhost`. Dette holder ds4-serveren bundet til loopback (den behøver ikke at blive eksponeret på andre interfaces).

> **Tip:** Webgrænsefladens port (`3000` her, angivet via `PORT`) er vilkårlig — vælg en hvilken som helst ledig port, hvis `3000` allerede er i brug, og åbn den port i din browser i stedet. Sørg for, at porten i `OPENAI_BASE_URL` matcher den port, din ds4-server kører på.

## Tilslutning af en kodningsagent

ds4-serveren eksponerer både OpenAI- og Anthropic-kompatible endpoints, så de fleste kodningsagenter kan forbinde direkte til den. For eksempel, for at tilføje den til `pi`-kodningsagenten, tilføjes følgende blok til `~/.pi/agent/models.json`:

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

> **Tip**: Hvis din kodningsagent eller webgrænseflade kører på en anden maskine end Halo-platformen, skal du videresende serverporten (`8000` her) via SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Næste skridt

- **Multi-node clustering**: Hvis du har to Halo-enheder, understøtter ds4 distribution af Q4-modellen (~153 GB) på tværs af begge maskiner via pipeline-parallelisme. Se [ds4-toolbox-dokumentationen](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) for opsætningsinstruktioner.
- **Spekulativ afkodning (MTP)**: Download MTP-vægtene (~3,6 GB), og angiv `--mtp` til serveren for hurtigere genereringshastighed.
- **Diskaflastning af KV-cache**: For arbejdsgange med kodningsagenter kan du aktivere `--kv-disk-dir`, så gentagne systemprompter gendannes fra SSD i stedet for at blive genberegnet hver gang.

For mere information, se [ds4-repositoriet](https://github.com/antirez/ds4) og [ds4-cockpit-toolboxen](https://github.com/kyuz0/strix-halo-ds4-toolbox).