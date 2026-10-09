<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversikt

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) er den effektivitetsfokuserte varianten av DeepSeek V4-familien — en Mixture of Experts-modell med 284 milliarder parametere og 13 milliarder aktive parametere. Ifølge [DeepSeeks tekniske rapport](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) scorer den 79 % på SWE-bench Verified og 91,6 % på LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) er en dedikert inferensmotor bygget spesielt for denne modellarkitekturen. I stedet for å være et generelt kjøretidsmiljø retter ds4 seg direkte mot DeepSeek V4-familien med arkitekturspesifikke kjerneoptimaliseringer for AMD ROCm™-programvare. Den er for øyeblikket en av de best presterende implementasjonene av DeepSeek V4 Flash på Strix Halo.

Denne veiledningen viser hvordan du bruker `ai-toolbox-cockpit`, et terminalbrukergrensesnitt, til å sette opp ds4, laste ned modellvekter og starte lokal tjenesteyting av DeepSeek V4 Flash på AMD Ryzen™ AI Halo Developer Platform.

## Hva du vil lære

- Hvordan installere og starte terminalbrukergrensesnittet `ai-toolbox-cockpit`
- Hvordan opprette ds4 ROCm-toolbox-containeren
- Nedlasting av den anbefalte kvantiseringen for en enkelt Halo-node
- Hvordan starte ds4-inferensserveren og eksponere et OpenAI-kompatibelt endepunkt
- Hvordan koble en Web UI eller kodeagent til den lokale serveren

## Konfigurere minneinnstillingene

<!-- @require:memory-config -->

## Installere nødvendig programvare

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:podman,distrobox,ds4-cockpit,ds4-toolbox-image -->

> **Systemkrav for denne konfigurasjonen (enkelt node, IQ2_XXS med 126k kontekst):**
> - Et Strix Halo-system med **minst 128 GB delt minne (unified memory)**.
> - **Dedikert BIOS-VRAM (UMA-rammebuffer) satt til minimum**, slik at det delte minnebassenget kan være så stort som mulig.
> - GPU-ens **delte minnebasseng satt til minst 110 GB**: kjør `amd-ttm --set 110` (se minnekonfigurasjonstrinnet ovenfor) og start på nytt. Lavere verdier kan føre til minnefeil når modellen lastes med en 126k-kontekst. Hvis systemet ditt har mindre tilgjengelig minne, bør du heller senke **Context**-verdien i Server Mode.
>
> **Merk:** Prøv å sette **GPU-ens delte minnebasseng** til **110 GB** som et utgangspunkt. Hvis du støter på minnefeil, kan du øke det delte minnebassenget eller senke kontekststørrelsen.

ai-toolbox-cockpit bruker container-toolboxer for å kjøre ds4-motoren. Installer `podman`, `distrobox` og `pipx`:

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

## Tilgjengelige kvantiseringer

Forfatteren av ds4 tilbyr flere kvantiserte versjoner av DeepSeek V4 Flash i GGUF-format. Alle modellene nedenfor bruker kalibrering med viktighetsmatrise (imatrix), som bevarer høyere presisjon for de delene av modellen som betyr mest for kodings- og resonneringsoppgaver.

| Kvantisering | Størrelse | Beskrivelse |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Anbefales for en enkelt node på 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Beholder lagene 37–42 i Q4-presisjon for bedre nøyaktighet. Passer innenfor 128 GB, men gir mindre plass til kontekst |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Høyere kvalitet. Krever to Halo-noder via klynging med flere noder |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Valgfri tilleggsfunksjon for spekulativ dekoding for å forbedre genereringshastigheten |

**IQ2_XXS imatrix**-modellen er et godt utgangspunkt. Den passer komfortabelt på en enkelt node og gir nok minne til et rimelig kontekstvindu.

## Installere ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) er et lett terminalbrukergrensesnitt som gjør det enkelt å installere ulike AI-backends. Vi bruker det til å håndtere opprettelsen av ds4-containeren vår, laste ned modellvekter og starte servere. Installer det med `pipx`:

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

## Trinn 1: Opprette Toolbox-en

I fanen **Interactive Toolboxes** velger du den nyeste tilgjengelige/stabile toolbox-en for ds4 (f.eks. `ds4-rocm-10.0`) og klikker **Create/Update**. Dette henter container-avbildet og oppretter toolbox-miljøet.


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

## Trinn 2: Laste ned modellen

Gå til fanen **Models**. Velg først backend (ds4). Velg deretter **IQ2_XXS imatrix (~80,8 GB)** fra nedtrekkslisten og klikk **Download**. Modellfilene lagres som standard i `~/ds4` (du kan endre lagringsbanen).

> **Merk:** IQ2_XXS-modellen er på rundt 80 GB, så nedlastingen kan ta en stund avhengig av tilkoblingen din. Du kan fortsette så snart den er ferdig.

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

## Trinn 3: Starte serveren

Gå til fanen **Server Mode**. Velg den nedlastede modellen og toolbox-en, og konfigurer deretter kontekststørrelse, vert og port. Når du er klar, klikker du **Start ds4-server**.

> **Tips** En kontekststørrelse på `126000` er en fornuftig startverdi som skal passe på en enkelt node — du kan sette den høyere hvis du har minne til overs, eller lavere hvis du støter på minnefeil. Porten (`8000` i denne veiledningen) er vilkårlig; velg en hvilken som helst ledig port.

> **KV Disk Cache (valgfritt).** Hvis du slår på **KV Disk Cache**, avlastes KV-bufferen til disk (i **Host Cache Dir**, standard `~/.cache/ds4-kv`), slik at gjentatte systemmeldinger gjenopprettes fra SSD i stedet for å bli beregnet på nytt. Dette er en ytelsesoptimalisering for arbeidsflyter med kodeagenter som har lange, gjentatte meldinger, og er **ikke nødvendig** for å kjøre serveren.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Serveren starter og lytter på port 8000, og eksponerer et OpenAI-kompatibelt API-endepunkt på `http://localhost:8000/v1`.

**Rask test:**
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
## Koble til en nettbasert brukergrensesnitt

Du kan koble til enhver chat-grensesnitt som støtter OpenAI API-formatet. For eksempel, for å bruke HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Åpne `http://localhost:3000` i nettleseren din for å starte chatten.

> **Merk:** `--network=host` plasserer nettgrensesnittet på vertens nettverk slik at det kan nå ds4-serveren på `localhost` direkte. Dette gjør at ds4-serveren forblir bundet til loopback (den trenger ikke å eksponeres på andre grensesnitt).

> **Tips:** Porten til nettgrensesnittet (`3000` her, satt via `PORT`) er vilkårlig — velg en hvilken som helst ledig port hvis `3000` allerede er i bruk, og åpne den porten i nettleseren din i stedet. Pass på at porten i `OPENAI_BASE_URL` samsvarer med porten ds4-serveren din kjører på.

## Koble til en kodeagent

ds4-serveren eksponerer både OpenAI- og Anthropic-kompatible endepunkter, så de fleste kodeagenter kan koble til den direkte. For eksempel, for å legge den til i `pi`-kodeagenten, legg til følgende blokk i `~/.pi/agent/models.json`:

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

> **Tips**: Hvis kodeagenten din eller nettgrensesnittet kjører på en annen maskin enn Halo-plattformen, må du videresende serverporten (`8000` her) via SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Neste steg

- **Flernode-klynging**: Hvis du har to Halo-enheter, støtter ds4 distribusjon av Q4-modellen (~153 GB) på tvers av begge maskinene via pipeline-parallellisme. Se [ds4-toolbox-dokumentasjonen](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) for oppsettsinstruksjoner.
- **Spekulativ dekoding (MTP)**: Last ned MTP-vektene (~3,6 GB) og send `--mtp` til serveren for raskere genereringshastighet.
- **Avlastning av KV-mellomlager til disk**: For arbeidsflyter med kodeagenter, aktiver `--kv-disk-dir` slik at gjentatte systemprompter gjenopprettes fra SSD i stedet for å bli beregnet på nytt hver gang.

For mer informasjon, se [ds4-repositoriet](https://github.com/antirez/ds4) og [ds4-cockpit-verktøykassen](https://github.com/kyuz0/strix-halo-ds4-toolbox).