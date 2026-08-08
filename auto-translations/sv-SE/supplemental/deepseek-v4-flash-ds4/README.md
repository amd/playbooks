<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Översikt

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) är den effektivitetsfokuserade varianten av DeepSeek V4-familjen — en modell med 284 miljarder parametrar av typen Mixture of Experts med 13 miljarder aktiva parametrar. Enligt [DeepSeeks tekniska rapport](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) uppnår den 79 % på SWE-bench Verified och 91,6 % på LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) är en dedikerad inferensmotor byggd specifikt för denna modellarkitektur. Snarare än en allmän runtime riktar sig ds4 direkt mot DeepSeek V4-familjen med arkitekturspecifika kärnoptimeringar för AMD ROCm™-mjukvara. Det är för närvarande en av de bäst presterande implementationerna av DeepSeek V4 Flash på Strix Halo.

Denna handledning visar hur man använder `ds4-cockpit`, ett terminalgränssnitt, för att konfigurera ds4, ladda ner modellvikter och börja servera DeepSeek V4 Flash lokalt på AMD Ryzen™ AI Halo Developer Platform.

## Vad du kommer att lära dig

- Hur man installerar och startar terminalgränssnittet `ds4-cockpit`
- Hur man skapar ds4 ROCm toolbox-containern
- Nedladdning av den rekommenderade kvantiseringen för en enskild Halo-nod
- Starta ds4-inferensservern och exponera en OpenAI-kompatibel slutpunkt
- Ansluta ett webbgränssnitt eller en kodningsagent till den lokala servern

## Konfigurera minnesinställningarna

<!-- @require:memory-config -->

## Installera mjukvaruförutsättningar

> **Systemkrav för denna konfiguration (enskild nod, IQ2_XXS vid 126k kontext):**
> - Ett Strix Halo-system med **minst 128 GB delat minne (unified memory)**.
> - **BIOS dedikerat VRAM (UMA framebuffer) inställt på minimum**, så att den delade minnespoolen kan vara så stor som möjligt.
> - GPU:ns **delade minnespool inställd på minst 110 GB**: kör `amd-ttm --set 110` (se minneskonfigurationssteget ovan) och starta om. Lägre värden kan orsaka minnesbrist när modellen laddas med en kontext på 126k. Om ditt system har mindre minne tillgängligt, sänk istället **Kontext**-värdet i Server Mode.
>
> **Obs!** Prova att ställa in **GPU:ns delade minnespool** till **110 GB** som utgångspunkt. Om du stöter på minnesbristfel, öka den delade minnespoolen eller sänk kontextstorleken.

ds4-cockpit använder container-toolboxes för att köra ds4-motorn. Installera `podman`, `distrobox` och `pipx`:

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

## Tillgängliga kvantiseringar

Upphovsmannen till ds4 tillhandahåller flera kvantiserade versioner av DeepSeek V4 Flash i GGUF-format. Alla modeller nedan använder importance matrix (imatrix)-kalibrering, vilket bevarar högre precision för de delar av modellen som är viktigast för kodnings- och resonemangsuppgifter.

| Kvantisering | Storlek | Beskrivning |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Rekommenderas för en enskild 128 GB-nod |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Behåller lagren 37–42 i Q4-precision för bättre noggrannhet. Ryms i 128 GB men lämnar mindre utrymme för kontext |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Högre kvalitet. Kräver två Halo-noder via klustring med flera noder |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Valfritt tillägg för spekulativ avkodning för att förbättra genereringshastigheten |

Modellen **IQ2_XXS imatrix** är en bra utgångspunkt. Den ryms bekvämt på en enda nod och lämnar tillräckligt med minne för ett rimligt kontextfönster.

## Installera ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) är ett lättviktigt terminalgränssnitt som gör det enkelt att komma igång med ds4 på Strix Halo. Det hanterar skapande av toolbox-containrar, nedladdning av modellvikter och start av servrar. Installera det med `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Starta cockpiten:
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

## Skapa toolboxen

I fliken **Interactive Toolboxes** väljer du den senaste tillgängliga/stabila toolboxen (t.ex. `ds4-rocm-7.2.4`) och klickar på **Create/Update**. Detta hämtar containeravbildningen och skapar toolbox-miljön.


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

## Ladda ner modellen

Gå till fliken **Model Manager**. Välj **IQ2_XXS imatrix (~80.8 GB)** i rullgardinsmenyn och klicka på **Download**. Modellfilerna sparas som standard i `~/ds4` (du kan ändra lagringssökvägen).

> **Obs!** Modellen IQ2_XXS är cirka 80 GB, så nedladdningen kan ta ett tag beroende på din anslutning. Du kan fortsätta när den är klar.

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

## Starta servern

Gå till fliken **Server Mode**. Välj den nedladdade modellen och toolboxen, och konfigurera sedan kontextstorlek, värd (host) och port. När du är klar klickar du på **Start ds4-server**.

> **Tips:** En kontextstorlek på `126000` är ett rimligt startvärde som bör rymmas på en enda nod — du kan öka den om du har minne att avvara, eller sänka den om du stöter på minnesbristfel. Porten (`8000` i den här guiden) är godtycklig; välj vilken ledig port som helst.

> **KV Disk Cache (valfritt).** Att aktivera **KV Disk Cache** avlastar KV-cachen till disk (vid **Host Cache Dir**, standard `~/.cache/ds4-kv`) så att upprepade systemprompter återställs från SSD istället för att beräknas om. Det är en prestandaoptimering för arbetsflöden med kodningsagenter med långa, upprepade prompter och är **inte nödvändigt** för att köra servern.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Servern startar och lyssnar på port 8000, vilket exponerar en OpenAI-kompatibel API-slutpunkt på `http://localhost:8000/v1`.

**Snabbtest:**
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

## Ansluta ett webbgränssnitt

Du kan ansluta valfritt chattgränssnitt som stöder OpenAI API-formatet. Till exempel, för att använda HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Öppna `http://localhost:3000` i din webbläsare för att börja chatta.
## Ansluta en kodningsagent

ds4-servern exponerar både OpenAI- och Anthropic-kompatibla slutpunkter, så de flesta kodningsagenter kan ansluta till den direkt. För att till exempel lägga till den i kodningsagenten `pi`, lägg till följande block i `~/.pi/agent/models.json`:

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

> **Tips**: Om din kodningsagent eller webbgränssnitt körs på en annan maskin än Halo-plattformen behöver du vidarebefordra port 8000 via SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Nästa steg

- **Klustring med flera noder**: Om du har två Halo-enheter stöder ds4 att distribuera Q4-modellen (~153 GB) över båda maskinerna via pipeline-parallellism. Se [ds4-toolbox-dokumentationen](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) för installationsanvisningar.
- **Spekulativ avkodning (MTP)**: Ladda ner MTP-vikterna (~3,6 GB) och skicka `--mtp` till servern för snabbare genereringshastighet.
- **Diskavlastning av KV-cache**: För arbetsflöden med kodningsagenter, aktivera `--kv-disk-dir` så att upprepade systemprompter återställs från SSD istället för att beräknas om varje gång.

För mer information, se [ds4-arkivet](https://github.com/antirez/ds4) och [ds4-cockpit-verktygslådan](https://github.com/kyuz0/strix-halo-ds4-toolbox).