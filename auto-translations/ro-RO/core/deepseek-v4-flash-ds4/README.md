<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din engleză și nu a fost revizuită de o persoană. Poate conține erori, iar unii pași, comenzi, descărcări sau disponibilitatea produselor pot diferi în funcție de limba sau regiunea dumneavoastră. Dacă ceva pare incorect, considerați playbook-ul original în limba engleză drept sursă de referință.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> Acest playbook folosește etichete speciale pe care GitHub nu le poate reda. Vă rugăm să vizitați [amd.com/playbooks](https://amd.com/playbooks) pentru a previzualiza corect acest conținut.
<!-- @github-only:end -->

## Prezentare generală

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) este varianta orientată spre eficiență din familia DeepSeek V4 — un model Mixture of Experts cu 284 de miliarde de parametri, dintre care 13 miliarde de parametri activi. Conform [raportului tehnic al DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), acesta obține un scor de 79% pe SWE-bench Verified și 91,6% pe LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) este un motor de inferență dedicat, construit special pentru această arhitectură de model. În loc să fie un runtime de uz general, ds4 vizează direct familia DeepSeek V4, cu optimizări de kernel specifice arhitecturii pentru software-ul AMD ROCm™. În prezent, este una dintre cele mai performante implementări ale DeepSeek V4 Flash pe Strix Halo.

Acest tutorial arată cum să folosiți `ds4-cockpit`, o interfață de terminal, pentru a configura ds4, a descărca ponderile modelului și a începe să serviți DeepSeek V4 Flash local pe platforma AMD Ryzen™ AI Halo Developer Platform.

## Ce veți învăța

- Cum să instalați și să lansați interfața de terminal `ds4-cockpit`
- Cum să creați containerul toolbox ds4 ROCm
- Descărcarea cuantizării recomandate pentru un singur nod Halo
- Pornirea serverului de inferență ds4 și expunerea unui endpoint compatibil OpenAI
- Conectarea unei interfețe Web sau a unui agent de programare la serverul local

<!-- @setup:memory_config -->

## Instalarea cerințelor preliminare de software

> **Cerințe de sistem pentru această configurație (IQ2_XXS pe un singur nod, cu context de 126k):**
> - Un sistem Strix Halo cu **cel puțin 128 GB memorie unificată**.
> - **VRAM dedicat din BIOS (UMA frame buffer) setat la minimum**, astfel încât fondul de memorie partajată să poată fi cât mai mare posibil.
> - Fondul de memorie partajată al GPU-ului **setat la cel puțin 110 GB**: rulați `amd-ttm --set 110` (vezi pasul de configurare a memoriei de mai sus) și reporniți. Valori mai mici eșuează cu erori de memorie insuficientă atunci când modelul este încărcat cu un context de 126k. Dacă sistemul dumneavoastră are mai puțină memorie disponibilă, reduceți în schimb valoarea **Context** din Server Mode.

ds4-cockpit folosește containere toolbox pentru a rula motorul ds4. Instalați `podman`, `distrobox` și `pipx`:

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

## Cuantizări disponibile

Autorul ds4 oferă mai multe versiuni cuantizate ale DeepSeek V4 Flash în format GGUF. Toate modelele de mai jos folosesc calibrarea prin matrice de importanță (imatrix), care păstrează o precizie mai mare pentru părțile modelului care contează cel mai mult pentru sarcinile de programare și raționament.

| Cuantizare | Dimensiune | Descriere |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Recomandat pentru un singur nod de 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Păstrează straturile 37–42 la precizie Q4 pentru o acuratețe mai bună. Încape în 128 GB, dar lasă mai puțin spațiu pentru context |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Calitate superioară. Necesită două noduri Halo prin clusterizare multi-nod |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Add-on opțional pentru decodare speculativă, pentru a îmbunătăți viteza de generare |

Modelul **IQ2_XXS imatrix** este un bun punct de plecare. Încape confortabil pe un singur nod și lasă suficientă memorie pentru o fereastră de context rezonabilă.

## Instalarea ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) este o interfață de terminal ușoară, menită să faciliteze pornirea și utilizarea ds4 pe Strix Halo. Se ocupă de crearea containerelor toolbox, descărcarea ponderilor modelului și pornirea serverelor. Instalați-o cu `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Lansați interfața cockpit:
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

## Crearea toolbox-ului

În fila **Interactive Toolboxes**, selectați cel mai recent toolbox disponibil (de exemplu, `ds4-rocm-7.2.4`) și faceți clic pe **Create/Update**. Aceasta descarcă imaginea containerului și creează mediul toolbox.

> **Sfat**: Versiunea toolbox-ului se va schimba în timp, pe măsură ce apar build-uri ROCm mai noi. Alegeți cea mai recentă versiune disponibilă din listă.

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

## Descărcarea modelului

Accesați fila **Model Manager**. Selectați **IQ2_XXS imatrix (~80.8 GB)** din meniul derulant și faceți clic pe **Download**. Fișierele modelului vor fi salvate implicit în `~/ds4` (puteți schimba calea de stocare).

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

## Pornirea serverului

Accesați fila **Server Mode**. Selectați modelul descărcat și toolbox-ul, apoi configurați dimensiunea contextului (de exemplu, 126000), gazda (host) și portul (8000). Când sunteți gata, faceți clic pe **Start ds4-server**.

> **KV Disk Cache (opțional).** Activarea opțiunii **KV Disk Cache** descarcă memoria cache KV pe disc (la **Host Cache Dir**, implicit `~/.cache/ds4-kv`), astfel încât prompturile de sistem repetate să fie restaurate de pe SSD în loc să fie recalculate. Este o optimizare de performanță pentru fluxurile de lucru ale agenților de programare cu prompturi lungi și repetate și **nu este necesară** pentru rularea serverului.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Serverul va porni și va asculta pe portul 8000, expunând un endpoint API compatibil OpenAI la `http://localhost:8000/v1`.

**Test rapid:**
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

## Conectarea unei interfețe Web

Puteți conecta orice interfață de chat care acceptă formatul API OpenAI. De exemplu, pentru a folosi HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Deschideți `http://localhost:3000` în browser pentru a începe să discutați.

## Conectarea unui agent de programare

Serverul ds4 expune atât endpoint-uri compatibile OpenAI, cât și Anthropic, astfel încât majoritatea agenților de programare se pot conecta la el direct. De exemplu, pentru a-l adăuga la agentul de programare `pi`, adăugați următorul bloc în `~/.pi/agent/models.json`:

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

> **Sfat**: Dacă agentul de programare sau interfața Web rulează pe un alt computer decât platforma Halo, va trebui să redirecționați portul 8000 prin SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```
## Următorii pași

- **Clustering multi-nod**: Dacă aveți două dispozitive Halo, ds4 permite distribuirea modelului Q4 (~153 GB) pe ambele mașini prin pipeline parallelism. Consultați [documentația ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) pentru instrucțiuni de configurare.
- **Speculative decoding (MTP)**: Descărcați greutățile MTP (~3.6 GB) și transmiteți `--mtp` către server pentru o viteză de generare mai mare.
- **KV cache disk offloading**: Pentru fluxuri de lucru cu agenți de codare, activați `--kv-disk-dir` astfel încât prompturile de sistem repetate să fie restaurate de pe SSD în loc să fie recalculate de fiecare dată.

Pentru mai multe informații, consultați [repository-ul ds4](https://github.com/antirez/ds4) și [toolbox-ul ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).