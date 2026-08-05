<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) je varijanta DeepSeek V4 porodice fokusirana na efikasnost — Mixture of Experts model sa 284 milijarde parametara, od kojih je 13 milijardi aktivnih parametara. Prema [DeepSeek-ovom tehničkom izveštaju](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), postiže 79% na SWE-bench Verified i 91,6% na LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) je namenski inference engine kreiran posebno za ovu arhitekturu modela. Umesto da bude opšte namene, ds4 direktno cilja na DeepSeek V4 porodicu modela kroz optimizacije kernela specifične za arhitekturu, namenjene AMD ROCm™ softveru. Trenutno je jedna od implementacija sa najboljim performansama za DeepSeek V4 Flash na Strix Halo platformi.

Ovaj tutorijal pokazuje kako da koristite `ds4-cockpit`, terminalski korisnički interfejs, za podešavanje ds4-a, preuzimanje težina modela i pokretanje lokalnog servisiranja DeepSeek V4 Flash modela na AMD Ryzen™ AI Halo Developer Platform.

## Šta ćete naučiti

- Kako da instalirate i pokrenete `ds4-cockpit` terminalski korisnički interfejs
- Kako da kreirate ds4 ROCm toolbox kontejner
- Preuzimanje preporučene kvantizacije za pojedinačni Halo čvor
- Pokretanje ds4 inference servera i izlaganje OpenAI-kompatibilnog endpointa
- Povezivanje Web UI-ja ili agenta za kodiranje na lokalni server

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

## Instaliranje neophodnih softverskih preduslova

> **Sistemski zahtevi za ovu konfiguraciju (single-node IQ2_XXS sa 126k kontekstom):**
> - Strix Halo sistem sa **najmanje 128 GB objedinjene memorije**.
> - **BIOS namenska VRAM memorija (UMA frame buffer) podešena na minimum**, kako bi bazen deljene memorije mogao biti što je moguće veći.
> - **Bazen deljene memorije** GPU-a **podešen na najmanje 110 GB**: pokrenite `amd-ttm --set 110` (pogledajte prethodni korak konfiguracije memorije) i restartujte sistem. Niže vrednosti mogu izazvati grešku nedostatka memorije prilikom učitavanja modela sa kontekstom od 126k. Ako vaš sistem ima manje dostupne memorije, umesto toga smanjite vrednost **Context** u Server Mode.
>
> **Napomena:** Probajte da podesite **bazen deljene GPU memorije** na **110 GB** kao polaznu vrednost. Ako naiđete na greške zbog nedostatka memorije, povećajte bazen deljene memorije ili smanjite veličinu konteksta.

ds4-cockpit koristi kontejnerske toolbox-ove za pokretanje ds4 engine-a. Instalirajte `podman`, `distrobox` i `pipx`:

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

## Dostupne kvantizacije

Autor ds4-a pruža nekoliko kvantizovanih verzija DeepSeek V4 Flash modela u GGUF formatu. Svi modeli dole navedeni koriste kalibraciju importance matrix (imatrix), koja zadržava veću preciznost za delove modela koji su najvažniji za zadatke kodiranja i rezonovanja.

| Kvantizacija | Veličina | Opis |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | Preporučeno za pojedinačni čvor od 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Zadržava slojeve 37–42 na Q4 preciznosti radi bolje tačnosti. Staje u 128 GB, ali ostavlja manje prostora za kontekst |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Viši kvalitet. Zahteva dva Halo čvora putem multi-node klasterovanja |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | Opcioni dodatak za spekulativno dekodiranje radi poboljšanja brzine generisanja |

Model **IQ2_XXS imatrix** predstavlja dobru polaznu tačku. Staje udobno na pojedinačni čvor i ostavlja dovoljno memorije za razuman prozor konteksta.

## Instaliranje ds4-cockpit-a

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) je lagani terminalski korisnički interfejs koji olakšava pokretanje ds4-a na Strix Halo platformi. On upravlja kreiranjem toolbox kontejnera, preuzimanjem težina modela i pokretanjem servera. Instalirajte ga pomoću `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Pokrenite cockpit:
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

## Kreiranje toolbox-a

U kartici **Interactive Toolboxes** izaberite poslednji dostupan/stabilan toolbox (npr. `ds4-rocm-7.2.4`) i kliknite na **Create/Update**. Ovo preuzima sliku kontejnera i kreira toolbox okruženje.


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

## Preuzimanje modela

Idite na karticu **Model Manager**. Izaberite **IQ2_XXS imatrix (~80.8 GB)** iz padajućeg menija i kliknite na **Download**. Fajlovi modela će podrazumevano biti sačuvani u `~/ds4` (putanju za skladištenje možete promeniti).

> **Napomena:** IQ2_XXS model ima oko 80 GB, tako da preuzimanje može potrajati u zavisnosti od vaše internet konekcije. Možete nastaviti nakon što se preuzimanje završi.

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

## Pokretanje servera

Idite na karticu **Server Mode**. Izaberite preuzeti model i toolbox, a zatim podesite veličinu konteksta, host i port. Kada ste spremni, kliknite na **Start ds4-server**.

> **Savet** Veličina konteksta `126000` je razumna polazna vrednost koja bi trebalo da stane na pojedinačni čvor — možete je povećati ako imate viška memorije, ili smanjiti ako naiđete na greške zbog nedostatka memorije. Port (`8000` u ovom vodiču) je proizvoljan; izaberite bilo koji slobodan port.

> **KV Disk Cache (opciono).** Uključivanjem opcije **KV Disk Cache** vrši se izmeštanje KV keša na disk (u **Host Cache Dir**, podrazumevano `~/.cache/ds4-kv`) tako da se ponovljeni sistemski upiti obnavljaju sa SSD-a umesto ponovnog izračunavanja. Ovo je optimizacija performansi za tokove rada agenata za kodiranje sa dugim, ponovljenim upitima, i **nije neophodna** za pokretanje servera.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Server će se pokrenuti i osluškivati na portu 8000, izlažući OpenAI-kompatibilan API endpoint na `http://localhost:8000/v1`.

**Brzi test:**
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

## Povezivanje Web UI-ja

Možete povezati bilo koji chat interfejs koji podržava OpenAI API format. Na primer, da biste koristili HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Otvorite `http://localhost:3000` u vašem pretraživaču da biste započeli razgovor.
## Povezivanje agenta za kodiranje

Server ds4 izlaže krajnje tačke kompatibilne i sa OpenAI i sa Anthropic, tako da se većina agenata za kodiranje može direktno povezati na njega. Na primer, da biste ga dodali u agenta za kodiranje `pi`, dodajte sledeći blok u `~/.pi/agent/models.json`:

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

> **Savet**: Ako se vaš agent za kodiranje ili Web UI izvršava na drugom uređaju u odnosu na Halo platformu, potrebno je da prosledite port 8000 preko SSH-a:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Sledeći koraci

- **Klasterovanje sa više čvorova**: Ako imate dva Halo uređaja, ds4 podržava distribuciju Q4 modela (~153 GB) preko oba uređaja pomoću paralelizma cevovoda (pipeline parallelism). Pogledajte [dokumentaciju za ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) za uputstva za podešavanje.
- **Spekulativno dekodiranje (MTP)**: Preuzmite MTP težine (~3.6 GB) i prosledite `--mtp` serveru radi bržeg generisanja.
- **Iskorišćavanje diska za KV keš**: Za tokove rada agenata za kodiranje, omogućite `--kv-disk-dir` kako bi se ponovljeni sistemski upiti vraćali sa SSD-a umesto da se svaki put iznova izračunavaju.

Za više informacija, pogledajte [ds4 repozitorijum](https://github.com/antirez/ds4) i [ds4-cockpit toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox).