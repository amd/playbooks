<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Panoramica

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) è la variante orientata all'efficienza della famiglia DeepSeek V4 — un modello Mixture of Experts da 284 miliardi di parametri con 13 miliardi di parametri attivi. Secondo il [report tecnico di DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), ottiene un punteggio del 79% su SWE-bench Verified e del 91.6% su LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) è un motore di inferenza dedicato, costruito appositamente per questa architettura di modello. Piuttosto che un runtime general-purpose, ds4 è mirato direttamente alla famiglia DeepSeek V4 con ottimizzazioni dei kernel specifiche per l'architettura per il software AMD ROCm™. Attualmente è una delle implementazioni con le migliori prestazioni di DeepSeek V4 Flash su Strix Halo.

Questo tutorial mostra come utilizzare `ai-toolbox-cockpit`, un'interfaccia utente a terminale, per configurare ds4, scaricare i pesi del modello e avviare l'erogazione di DeepSeek V4 Flash localmente sull'AMD Ryzen™ AI Halo Developer Platform.

## Cosa imparerai

- Come installare e avviare l'interfaccia utente a terminale `ai-toolbox-cockpit`
- Come creare il container toolbox ROCm di ds4
- Scaricare la quantizzazione consigliata per un singolo nodo Halo
- Avviare il server di inferenza ds4 ed esporre un endpoint compatibile con OpenAI
- Collegare una Web UI o un coding agent al server locale

## Impostazione della configurazione della memoria

<!-- @require:memory-config -->

## Installazione dei prerequisiti software

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:podman,distrobox,ds4-cockpit,ds4-toolbox-image -->

> **Requisiti di sistema per questa configurazione (IQ2_XXS su singolo nodo con contesto a 126k):**
> - Un sistema Strix Halo con **almeno 128 GB di memoria unificata**.
> - **La VRAM dedicata del BIOS (UMA frame buffer) impostata al minimo**, in modo che il pool di memoria condivisa possa essere il più grande possibile.
> - Il pool di memoria condivisa della GPU **impostato ad almeno 110 GB**: eseguire `amd-ttm --set 110` (vedere il passaggio di configurazione della memoria sopra) e riavviare. Valori più bassi possono causare errori di memoria esaurita quando il modello viene caricato con un contesto di 126k. Se il sistema in uso ha meno memoria disponibile, ridurre invece il valore di **Context** in Server Mode.
>
> **Nota:** Provare a impostare il **pool di memoria condivisa della GPU** a **110 GB** come punto di partenza. In caso di errori di memoria esaurita, aumentare il pool di memoria condivisa o ridurre la dimensione del contesto.

ai-toolbox-cockpit utilizza container toolbox per eseguire il motore ds4. Installare `podman`, `distrobox` e `pipx`:

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

## Quantizzazioni disponibili

L'autore di ds4 fornisce diverse versioni quantizzate di DeepSeek V4 Flash in formato GGUF. Tutti i modelli sottostanti utilizzano la calibrazione importance matrix (imatrix), che preserva una precisione maggiore per le parti del modello che contano di più per le attività di coding e ragionamento.

| Quantizzazione | Dimensione | Descrizione |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | Consigliato per un singolo nodo da 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Mantiene i layer 37–42 a precisione Q4 per una migliore accuratezza. Entra in 128 GB ma lascia meno spazio per il contesto |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Qualità superiore. Richiede due nodi Halo tramite clustering multi-nodo |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | Componente opzionale per la decodifica speculativa per migliorare la velocità di generazione |

Il modello **IQ2_XXS imatrix** è un buon punto di partenza. Si adatta comodamente a un singolo nodo e lascia abbastanza memoria per una finestra di contesto ragionevole.

## Installazione di ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) è un'interfaccia utente a terminale leggera che semplifica l'installazione di vari backend AI. La utilizzeremo per gestire la creazione del nostro container ds4, il download dei pesi del modello e l'avvio dei server. Installarla con `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Avviare il cockpit:
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

## Passaggio 1: Creazione del toolbox

Nella scheda **Interactive Toolboxes**, selezionare il toolbox stabile/disponibile più recente per ds4 (ad esempio `ds4-rocm-10.0`) e fare clic su **Create/Update**. Questo scarica l'immagine del container e crea l'ambiente toolbox.


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

## Passaggio 2: Download del modello

Andare alla scheda **Models**. Prima selezionare il backend (ds4). Poi selezionare **IQ2_XXS imatrix (~80.8 GB)** dal menu a tendina e fare clic su **Download**. I file del modello verranno salvati per impostazione predefinita in `~/ds4` (è possibile modificare il percorso di archiviazione).

> **Nota:** Il modello IQ2_XXS è di circa 80 GB, quindi il download può richiedere del tempo a seconda della connessione. Una volta terminato, è possibile proseguire.

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

## Passaggio 3: Avvio del server

Andare alla scheda **Server Mode**. Selezionare il modello scaricato e il toolbox, quindi configurare la dimensione del contesto, l'host e la porta. Una volta pronti, fare clic su **Start ds4-server**.

> **Suggerimento** Una dimensione del contesto di `126000` è un valore di partenza ragionevole che dovrebbe adattarsi a un singolo nodo — è possibile impostarla più alta se si dispone di memoria sufficiente, oppure più bassa in caso di errori di memoria esaurita. La porta (`8000` in questa guida) è arbitraria; sceglierne una qualsiasi libera.

> **KV Disk Cache (opzionale).** Attivare **KV Disk Cache** scarica la cache KV su disco (in **Host Cache Dir**, il valore predefinito è `~/.cache/ds4-kv`), così i prompt di sistema ripetuti vengono ripristinati dall'SSD invece di essere ricalcolati. Si tratta di un'ottimizzazione delle prestazioni per i flussi di lavoro con coding agent che utilizzano prompt lunghi e ripetuti, e **non è necessaria** per eseguire il server.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Il server si avvierà e rimarrà in ascolto sulla porta 8000, esponendo un endpoint API compatibile con OpenAI all'indirizzo `http://localhost:8000/v1`.

**Test rapido:**
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
## Connessione di un'interfaccia Web

Puoi collegare qualsiasi interfaccia di chat che supporti il formato OpenAI API. Ad esempio, per usare HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Apri `http://localhost:3000` nel tuo browser per iniziare a chattare.

> **Nota:** `--network=host` mette l'interfaccia Web sulla rete dell'host, così può raggiungere direttamente il server ds4 su `localhost`. Questo mantiene il server ds4 vincolato al loopback (non deve essere esposto su altre interfacce).

> **Suggerimento:** La porta dell'interfaccia Web (`3000` in questo caso, impostata tramite `PORT`) è arbitraria: scegli una qualsiasi porta libera se la `3000` è già in uso e apri quella porta nel tuo browser. Assicurati che la porta in `OPENAI_BASE_URL` corrisponda alla porta su cui è in esecuzione il tuo server ds4.

## Connessione di un agente di coding

Il server ds4 espone endpoint compatibili sia con OpenAI che con Anthropic, quindi la maggior parte degli agenti di coding può connettersi direttamente ad esso. Ad esempio, per aggiungerlo all'agente di coding `pi`, aggiungi il seguente blocco a `~/.pi/agent/models.json`:

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

> **Suggerimento**: Se il tuo agente di coding o la tua interfaccia Web è in esecuzione su una macchina diversa dalla piattaforma Halo, dovrai inoltrare la porta del server (`8000` in questo caso) tramite SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Prossimi passi

- **Clustering multi-nodo**: Se disponi di due dispositivi Halo, ds4 supporta la distribuzione del modello Q4 (~153 GB) su entrambe le macchine tramite pipeline parallelism. Consulta la [documentazione di ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) per le istruzioni di configurazione.
- **Decodifica speculativa (MTP)**: Scarica i pesi MTP (~3,6 GB) e passa `--mtp` al server per una velocità di generazione più elevata.
- **Offloading su disco della cache KV**: Per i flussi di lavoro degli agenti di coding, abilita `--kv-disk-dir` in modo che i prompt di sistema ripetuti vengano ripristinati dall'SSD invece di essere ricalcolati ogni volta.

Per maggiori informazioni, consulta il [repository ds4](https://github.com/antirez/ds4) e il [toolbox ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).