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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) er den effektivitetsfokuserte varianten av DeepSeek V4-familien — en Mixture of Experts-modell med 284 milliarder parametere og 13 milliarder aktive parametere. Ifølge [DeepSeeks tekniske rapport](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) oppnår den 79 % på SWE-bench Verified og 91,6 % på LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) er en dedikert inferensmotor bygget spesifikt for denne modellarkitekturen. I stedet for et generelt kjøremiljø retter ds4 seg direkte mot DeepSeek V4-familien med arkitekturspesifikke kjerneoptimaliseringer for AMD ROCm™-programvare. Det er for øyeblikket en av implementasjonene med best ytelse for DeepSeek V4 Flash på Strix Halo.

Denne veiledningen viser hvordan du bruker `ds4-cockpit`, et terminal-brukergrensesnitt, til å sette opp ds4, laste ned modellvekter og starte servering av DeepSeek V4 Flash lokalt på AMD Ryzen™ AI Halo Developer Platform.

## Hva du vil lære

- Hvordan installere og starte terminal-brukergrensesnittet `ds4-cockpit`
- Hvordan opprette ds4 ROCm-verktøykassecontaineren
- Nedlasting av den anbefalte kvantiseringen for en enkelt Halo-node
- Starte ds4-inferensserveren og eksponere et OpenAI-kompatibelt endepunkt
- Koble et web-brukergrensesnitt eller en kodeagent til den lokale serveren

## Konfigurere minneoppsettet

<!-- @require:memory-config -->

## Installere programvareforutsetninger

> **Systemkrav for denne konfigurasjonen (enkelt-node IQ2_XXS med 126k kontekst):**
> - Et Strix Halo-system med **minst 128 GB delt minne**.
> - **BIOS-dedikert VRAM (UMA-bildebuffer) satt til minimum**, slik at det delte minnebassenget kan være så stort som mulig.
> - GPU-ens **delte minnebasseng satt til minst 110 GB**: kjør `amd-ttm --set 110` (se minnekonfigurasjonssteget ovenfor) og start på nytt. Lavere verdier kan mislykkes med tomt-for-minne når modellen lastes med 126k kontekst. Hvis systemet ditt har mindre tilgjengelig minne, senk **Context**-verdien i servermodus i stedet.
>
> **Merk:** Prøv å sette **GPU-ens delte minnebasseng** til **110 GB** som et utgangspunkt. Hvis du støter på tomt-for-minne-feil, øk det delte minnebassenget eller senk kontekststørrelsen.

ds4-cockpit bruker container-verktøykasser for å kjøre ds4-motoren. Installer `podman`, `distrobox` og `pipx`:

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

Forfatteren av ds4 tilbyr flere kvantiserte versjoner av DeepSeek V4 Flash i GGUF-format. Alle modellene nedenfor bruker kalibrering med viktighetsmatrise (imatrix), som bevarer høyere presisjon for de delene av modellen som betyr mest for koding og resonneringsoppgaver.

| Kvantisering | Størrelse | Beskrivelse |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Anbefalt for en enkelt 128 GB-node |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Beholder lag 37–42 med Q4-presisjon for bedre nøyaktighet. Får plass i 128 GB, men gir mindre rom for kontekst |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Høyere kvalitet. Krever to Halo-noder via multi-node-klynging |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Valgfri tilleggsmodul for spekulativ dekoding for å forbedre genereringshastigheten |

**IQ2_XXS imatrix**-modellen er et godt utgangspunkt. Den passer komfortabelt på en enkelt node og etterlater nok minne til et rimelig kontekstvindu.

## Installere ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) er et lett terminal-brukergrensesnitt som gjør det enkelt å komme i gang med ds4 på Strix Halo. Det håndterer opprettelse av verktøykassecontainere, nedlasting av modellvekter og oppstart av servere. Installer det med `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Start cockpit:
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

## Opprette verktøykassen

I fanen **Interactive Toolboxes** velger du den nyeste tilgjengelige/stabile verktøykassen (f.eks. `ds4-rocm-7.2.4`) og klikker **Create/Update**. Dette henter containeravbildet og oppretter verktøykassemiljøet.


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

## Laste ned modellen

Gå til fanen **Model Manager**. Velg **IQ2_XXS imatrix (~80.8 GB)** fra nedtrekksmenyen og klikk **Download**. Modellfilene lagres til `~/ds4` som standard (du kan endre lagringsbanen).

> **Merk:** IQ2_XXS-modellen er omtrent 80 GB, så nedlastingen kan ta en stund avhengig av tilkoblingen din. Du kan fortsette når den er ferdig.

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

## Starte serveren

Gå til fanen **Server Mode**. Velg den nedlastede modellen og verktøykassen, og konfigurer deretter kontekststørrelse, vert og port. Når du er klar, klikk **Start ds4-server**.

> **Tips** En kontekststørrelse på `126000` er en fornuftig startverdi som bør passe på en enkelt node — du kan sette den høyere hvis du har minne til overs, eller lavere hvis du støter på tomt-for-minne-feil. Porten (`8000` i denne veiledningen) er vilkårlig; velg en hvilken som helst ledig port.

> **KV Disk Cache (valgfritt).** Å slå på **KV Disk Cache** avlaster KV-mellomlageret til disk (ved **Host Cache Dir**, standard `~/.cache/ds4-kv`) slik at gjentatte systeminstruksjoner gjenopprettes fra SSD i stedet for å bli beregnet på nytt. Dette er en ytelsesoptimalisering for kodeagent-arbeidsflyter med lange, gjentatte instruksjoner, og er **ikke nødvendig** for å kjøre serveren.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Serveren starter og lytter på port 8000, og eksponerer et OpenAI-kompatibelt API-endepunkt på `http://localhost:8000/v1`.

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

## Koble til et web-brukergrensesnitt

Du kan koble til et hvilket som helst chat-grensesnitt som støtter OpenAI API-formatet. For eksempel, for å bruke HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Åpne `http://localhost:3000` i nettleseren din for å begynne å chatte.
## Koble til en kodingsagent

ds4-serveren eksponerer både OpenAI- og Anthropic-kompatible endepunkter, så de fleste kodingsagenter kan koble seg direkte til den. For å legge den til i kodingsagenten `pi`, kan du for eksempel legge til følgende blokk i `~/.pi/agent/models.json`:

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

> **Tips**: Hvis kodingsagenten eller Web UI-en din kjører på en annen maskin enn Halo-plattformen, må du videresende port 8000 via SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Neste steg

- **Klynging med flere noder**: Hvis du har to Halo-enheter, støtter ds4 distribusjon av Q4-modellen (~153 GB) over begge maskinene via pipeline-parallellisme. Se [ds4-toolbox-dokumentasjonen](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) for oppsettinstruksjoner.
- **Spekulativ dekoding (MTP)**: Last ned MTP-vektene (~3,6 GB) og send `--mtp` til serveren for raskere genereringshastighet.
- **Diskavlasting av KV-buffer**: For arbeidsflyter med kodingsagenter kan du aktivere `--kv-disk-dir` slik at gjentatte systemforespørsler gjenopprettes fra SSD i stedet for å bli beregnet på nytt hver gang.

For mer informasjon, se [ds4-repositoriet](https://github.com/antirez/ds4) og [ds4-cockpit-verktøykassen](https://github.com/kyuz0/strix-halo-ds4-toolbox).