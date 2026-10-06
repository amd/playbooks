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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) er den effektivitetsfokuserte varianten av DeepSeek V4-familien — en Mixture of Experts-modell på 284 milliarder parametere med 13 milliarder aktive parametere. Ifølge [DeepSeeks tekniske rapport](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) oppnår den 79 % på SWE-bench Verified og 91,6 % på LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) er en dedikert inferensmotor bygget spesifikt for denne modellarkitekturen. I stedet for å være en generell kjøretidsmotor retter ds4 seg direkte mot DeepSeek V4-familien med arkitekturspesifikke kjerneoptimaliseringer for AMD ROCm™-programvare. Det er for øyeblikket en av de best presterende implementasjonene av DeepSeek V4 Flash på Strix Halo.

Denne veiledningen viser hvordan du bruker `ai-toolbox-cockpit`, et terminalgrensesnitt, for å sette opp ds4, laste ned modellvekter og starte lokal servering av DeepSeek V4 Flash på AMD Ryzen™ AI Halo Developer Platform.

## Hva du vil lære

- Hvordan installere og starte terminalgrensesnittet `ai-toolbox-cockpit`
- Hvordan opprette ds4 ROCm-toolbox-containeren
- Nedlasting av den anbefalte kvantiseringen for en enkelt Halo-node
- Starte ds4-inferensserveren og eksponere et OpenAI-kompatibelt endepunkt
- Koble en Web UI eller kodeagent til den lokale serveren

## Konfigurere minneinnstillinger

<!-- @require:memory-config -->

## Installere nødvendig programvare

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:distrobox,ds4-cockpit,ds4-toolbox-image -->

> **Systemkrav for denne konfigurasjonen (enkeltnode IQ2_XXS med 126k kontekst):**
> - Et Strix Halo-system med **minst 128 GB forent minne**.
> - **BIOS-dedikert VRAM (UMA-frame buffer) satt til minimum**, slik at det delte minnebassenget kan være så stort som mulig.
> - GPU-ens **delte minnebasseng satt til minst 110 GB**: kjør `amd-ttm --set 110` (se minnekonfigurasjonstrinnet ovenfor) og start på nytt. Lavere verdier kan feile med tomt for minne når modellen lastes med 126k kontekst. Hvis systemet ditt har mindre tilgjengelig minne, bør du heller redusere **Context**-verdien i Server Mode.
>
> **Merk:** Prøv å sette **GPU-ens delte minnebasseng** til **110 GB** som utgangspunkt. Hvis du støter på feil knyttet til tomt for minne, øk det delte minnebassenget eller reduser kontekststørrelsen.

ai-toolbox-cockpit bruker container-toolboxer for å kjøre ds4-motoren. Installer `podman`, `distrobox`, og `pipx`:

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

ds4-forfatteren tilbyr flere kvantiserte versjoner av DeepSeek V4 Flash i GGUF-format. Alle modellene nedenfor bruker importance matrix (imatrix)-kalibrering, som bevarer høyere presisjon for de delene av modellen som betyr mest for koding og resonneringsoppgaver.

| Kvantisering | Størrelse | Beskrivelse |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Anbefales for en enkelt 128 GB-node |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Beholder lag 37–42 i Q4-presisjon for bedre nøyaktighet. Passer innenfor 128 GB, men etterlater mindre plass til kontekst |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Høyere kvalitet. Krever to Halo-noder via klynging med flere noder |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Valgfritt tillegg for spekulativ dekoding for å forbedre genereringshastighet |

Modellen **IQ2_XXS imatrix** er et godt utgangspunkt. Den passer komfortabelt på en enkelt node og etterlater nok minne til et rimelig kontekstvindu.

## Installere ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) er et lett terminalgrensesnitt som gjør det enkelt å installere ulike AI-backender. Vi vil bruke det til å håndtere opprettelsen av vår ds4-container, nedlasting av modellvekter og oppstart av servere. Installer det med `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Start kokpittet:
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

## Trinn 1: Opprette toolboxen

I fanen **Interactive Toolboxes**, velg den nyeste tilgjengelige/stabile toolboxen for ds4 (f.eks. `ds4-rocm-10.0`) og klikk **Create/Update**. Dette henter container-avbildet og oppretter toolbox-miljøet.


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

Gå til fanen **Models**. Velg først backend (ds4). Velg deretter **IQ2_XXS imatrix (~80,8 GB)** fra nedtrekksmenyen og klikk **Download**. Modellfilene lagres som standard i `~/ds4` (du kan endre lagringsstien).

> **Merk:** IQ2_XXS-modellen er på rundt 80 GB, så nedlastingen kan ta en stund avhengig av tilkoblingen din. Du kan fortsette når den er ferdig.

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

Gå til fanen **Server Mode**. Velg den nedlastede modellen og toolboxen, og konfigurer deretter kontekststørrelse, host og port. Når du er klar, klikk **Start ds4-server**.

> **Tips** En kontekststørrelse på `126000` er en rimelig startverdi som bør passe på en enkelt node — du kan sette den høyere hvis du har minne til overs, eller lavere hvis du støter på feil knyttet til tomt for minne. Porten (`8000` i denne veiledningen) er vilkårlig; velg en hvilken som helst ledig port.

> **KV Disk Cache (valgfritt).** Hvis du slår på **KV Disk Cache**, avlastes KV-cachen til disk (ved **Host Cache Dir**, standard `~/.cache/ds4-kv`), slik at gjentatte systemmeldinger gjenopprettes fra SSD i stedet for å bli beregnet på nytt. Dette er en ytelsesoptimalisering for arbeidsflyter med kodeagenter som bruker lange, gjentatte meldinger, og er **ikke påkrevd** for å kjøre serveren.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Serveren vil starte og lytte på port 8000, og eksponere et OpenAI-kompatibelt API-endepunkt på `http://localhost:8000/v1`.

**Hurtigtest:**
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
## Koble til et nettgrensesnitt

Du kan koble til et hvilket som helst chat-grensesnitt som støtter OpenAI API-formatet. For å bruke HuggingFace ChatUI, for eksempel:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Åpne `http://localhost:3000` i nettleseren din for å starte chattingen.

> **Merk:** `--network=host` plasserer nettgrensesnittet på vertens nettverk slik at det kan nå ds4-serveren på `localhost` direkte. Dette gjør at ds4-serveren forblir bundet til loopback (den trenger ikke å eksponeres på andre grensesnitt).

> **Tips:** Porten til nettgrensesnittet (`3000` her, satt via `PORT`) er vilkårlig — velg en hvilken som helst ledig port hvis `3000` allerede er i bruk, og åpne den porten i nettleseren din i stedet. Pass på at porten i `OPENAI_BASE_URL` stemmer overens med porten ds4-serveren kjører på.

## Koble til en kodeagent

ds4-serveren eksponerer både OpenAI- og Anthropic-kompatible endepunkter, så de fleste kodeagenter kan koble til den direkte. For eksempel, for å legge den til i kodeagenten `pi`, legg til følgende blokk i `~/.pi/agent/models.json`:

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

> **Tips**: Hvis kodeagenten eller nettgrensesnittet ditt kjører på en annen maskin enn Halo-plattformen, må du videresende serverporten (`8000` her) via SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Neste steg

- **Klynging med flere noder**: Hvis du har to Halo-enheter, støtter ds4 distribusjon av Q4-modellen (~153 GB) på tvers av begge maskinene via pipeline-parallellisme. Se [ds4-toolbox-dokumentasjonen](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) for oppsettinstruksjoner.
- **Spekulativ dekoding (MTP)**: Last ned MTP-vektene (~3,6 GB) og send `--mtp` til serveren for raskere genereringshastighet.
- **Diskavlastning av KV-cache**: For arbeidsflyter med kodeagenter, aktiver `--kv-disk-dir` slik at gjentatte systemprompter gjenopprettes fra SSD i stedet for å bli regnet ut på nytt hver gang.

For mer informasjon, se [ds4-repositoriet](https://github.com/antirez/ds4) og [ds4-cockpit-toolboxen](https://github.com/kyuz0/strix-halo-ds4-toolbox).