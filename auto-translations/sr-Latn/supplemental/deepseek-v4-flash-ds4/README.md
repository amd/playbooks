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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) je varijanta porodice DeepSeek V4 usmerena na efikasnost — model tipa Mixture of Experts sa 284 milijarde parametara, od kojih je 13 milijardi aktivnih parametara. Prema [tehničkom izveštaju kompanije DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), postiže rezultat od 79% na SWE-bench Verified i 91,6% na LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) je namenski mehanizam za inferenciju napravljen posebno za ovu arhitekturu modela. Umesto da bude opšta runtime okolina, ds4 cilja direktno porodicu DeepSeek V4, sa optimizacijama kernela specifičnim za arhitekturu, namenjenim AMD ROCm™ softveru. Trenutno je jedna od implementacija sa najboljim performansama za DeepSeek V4 Flash na Strix Halo platformi.

Ovaj vodič pokazuje kako da koristite `ai-toolbox-cockpit`, terminalski korisnički interfejs, da podesite ds4, preuzmete težine modela i pokrenete lokalno posluživanje DeepSeek V4 Flash na AMD Ryzen™ AI Halo Developer Platform.

## Šta ćete naučiti

- Kako da instalirate i pokrenete terminalski UI `ai-toolbox-cockpit`
- Kako da kreirate ds4 ROCm toolbox kontejner
- Preuzimanje preporučene kvantizacije za jedan Halo čvor
- Pokretanje ds4 servera za inferenciju i izlaganje OpenAI-kompatibilnog endpoint-a
- Povezivanje Web UI-ja ili agenta za kodiranje sa lokalnim serverom

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

## Instaliranje preduslovnog softvera

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:podman,distrobox,ds4-cockpit,ds4-toolbox-image -->

> **Sistemski zahtevi za ovu konfiguraciju (IQ2_XXS na jednom čvoru, kontekst 126k):**
> - Strix Halo sistem sa **najmanje 128 GB jedinstvene memorije**.
> - **VRAM namenjen BIOS-u (UMA frame buffer) podešen na minimum**, kako bi zajednički memorijski bazen mogao da bude što veći.
> - **Zajednički memorijski bazen GPU-a podešen na najmanje 110 GB**: pokrenite `amd-ttm --set 110` (pogledajte korak za podešavanje memorije iznad) i restartujte sistem. Niže vrednosti mogu izazvati grešku nedostatka memorije kada se model učitava sa kontekstom od 126k. Ako vaš sistem ima manje dostupne memorije, umesto toga smanjite vrednost **Context** u Server Mode.
>
> **Napomena:** Probajte da podesite **zajednički memorijski bazen GPU-a** na **110 GB** kao polaznu vrednost. Ako naiđete na greške nedostatka memorije, povećajte zajednički memorijski bazen ili smanjite veličinu konteksta.

ai-toolbox-cockpit koristi kontejnerske toolbox-ove za pokretanje ds4 mehanizma. Instalirajte `podman`, `distrobox` i `pipx`:

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

Autor ds4 pruža nekoliko kvantizovanih verzija DeepSeek V4 Flash u GGUF formatu. Svi modeli u nastavku koriste kalibraciju matrice važnosti (imatrix), koja čuva veću preciznost za delove modela koji su najvažniji za zadatke kodiranja i rezonovanja.

| Kvantizacija | Veličina | Opis |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Preporučeno za jedan čvor od 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Zadržava slojeve 37–42 na Q4 preciznosti radi bolje tačnosti. Staje u 128 GB, ali ostavlja manje prostora za kontekst |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Viši kvalitet. Zahteva dva Halo čvora putem klasterovanja sa više čvorova |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Opcioni dodatak za spekulativno dekodiranje radi poboljšanja brzine generisanja |

Model **IQ2_XXS imatrix** je dobra polazna tačka. Udobno staje na jedan čvor i ostavlja dovoljno memorije za razuman prozor konteksta.

## Instaliranje ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) je lagani terminalski UI koji olakšava instaliranje raznih AI backend-a. Koristićemo ga da rukujemo kreiranjem našeg ds4 kontejnera, preuzimanjem težina modela i pokretanjem servera. Instalirajte ga pomoću `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Pokrenite cockpit:
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

## Korak 1: Kreiranje toolbox-a

U kartici **Interactive Toolboxes**, izaberite najnoviji dostupni/stabilni toolbox za ds4 (npr. `ds4-rocm-10.0`) i kliknite na **Create/Update**. Ovo preuzima sliku kontejnera i kreira toolbox okruženje.


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

## Korak 2: Preuzimanje modela

Idite na karticu **Models**. Prvo izaberite backend (ds4). Zatim izaberite **IQ2_XXS imatrix (~80,8 GB)** iz padajućeg menija i kliknite na **Download**. Datoteke modela će po difoltu biti sačuvane u `~/ds4` (putanju za skladištenje možete promeniti).

> **Napomena:** Model IQ2_XXS je otprilike 80 GB, pa preuzimanje može potrajati u zavisnosti od vaše veze. Možete nastaviti kada se završi.

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

## Korak 3: Pokretanje servera

Idite na karticu **Server Mode**. Izaberite preuzeti model i toolbox, zatim podesite veličinu konteksta, host i port. Kada budete spremni, kliknite na **Start ds4-server**.

> **Savet:** Veličina konteksta od `126000` je razumna polazna vrednost koja bi trebalo da stane na jedan čvor — možete je postaviti više ako imate memorije na pretek, ili je smanjiti ako naiđete na greške nedostatka memorije. Port (`8000` u ovom vodiču) je proizvoljan; izaberite bilo koji slobodan port.

> **KV Disk Cache (opciono).** Uključivanje opcije **KV Disk Cache** prebacuje KV keš na disk (u **Host Cache Dir**, podrazumevano `~/.cache/ds4-kv`), tako da se ponovljeni sistemski promptovi obnavljaju sa SSD-a umesto da se ponovo izračunavaju. Ovo je optimizacija performansi za tokove rada agenata za kodiranje sa dugim, ponovljenim promptovima i **nije neophodna** za pokretanje servera.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Server će se pokrenuti i slušati na portu 8000, izlažući OpenAI-kompatibilan API endpoint na `http://localhost:8000/v1`.

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
## Povezivanje veb interfejsa

Možete povezati bilo koji chat interfejs koji podržava OpenAI API format. Na primer, za korišćenje HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Otvorite `http://localhost:3000` u pregledaču da biste započeli ćaskanje.

> **Napomena:** `--network=host` postavlja veb interfejs na mrežu hosta kako bi mogao da dosegne ds4 server na `localhost` direktno. Ovo zadržava ds4 server vezan za loopback (ne mora biti izložen na drugim interfejsima).

> **Savet:** Port veb interfejsa (`3000` ovde, postavljen preko `PORT`) je proizvoljan — izaberite bilo koji slobodan port ako je `3000` već zauzet, i otvorite taj port u pregledaču umesto njega. Vodite računa da se port u `OPENAI_BASE_URL` poklapa sa portom na kojem radi vaš ds4 server.

## Povezivanje agenta za programiranje

ds4 server izlaže i OpenAI i Anthropic-kompatibilne krajnje tačke, tako da se većina agenata za programiranje može povezati direktno na njega. Na primer, da biste ga dodali u agenta za programiranje `pi`, dodajte sledeći blok u `~/.pi/agent/models.json`:

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

> **Savet**: Ako vaš agent za programiranje ili veb interfejs rade na drugoj mašini u odnosu na Halo platformu, moraćete da prosledite port servera (`8000` ovde) preko SSH-a:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Sledeći koraci

- **Klasterovanje sa više čvorova**: Ako imate dva Halo uređaja, ds4 podržava distribuciju Q4 modela (~153 GB) na obe mašine putem pipeline paralelizma. Pogledajte [ds4-toolbox dokumentaciju](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) za uputstva za podešavanje.
- **Spekulativno dekodiranje (MTP)**: Preuzmite MTP težine (~3.6 GB) i prosledite `--mtp` serveru radi bržeg generisanja.
- **Rasterećivanje KV keša na disk**: Za radne tokove agenata za programiranje, omogućite `--kv-disk-dir` kako bi se ponovljeni sistemski upiti obnavljali sa SSD-a umesto da se svaki put iznova izračunavaju.

Za više informacija, pogledajte [ds4 repozitorijum](https://github.com/antirez/ds4) i [ds4-cockpit toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox).