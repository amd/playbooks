<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> Ta priročnik uporablja posebne oznake, ki jih GitHub ne more upodobiti. Za pravilen predogled te vsebine obiščite [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Pregled

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) je različica družine DeepSeek V4, osredotočena na učinkovitost — model Mixture of Experts z 284 milijardami parametrov, od katerih je 13 milijard aktivnih. Glede na [DeepSeekovo tehnično poročilo](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) doseže 79 % pri SWE-bench Verified in 91,6 % pri LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) je namenski sklepalni pogon (inference engine), zgrajen posebej za to arhitekturo modela. Namesto splošno namenskega izvajalnega okolja je ds4 usmerjen neposredno v družino DeepSeek V4, z optimizacijami jeder, specifičnimi za arhitekturo, za programsko opremo AMD ROCm™. Trenutno je ena najbolje delujočih implementacij DeepSeek V4 Flash na platformi Strix Halo.

Ta vadnica prikazuje, kako z uporabo `ds4-cockpit`, terminalskega uporabniškega vmesnika, nastaviti ds4, prenesti uteži modela in začeti lokalno strežbo DeepSeek V4 Flash na platformi AMD Ryzen™ AI Halo Developer Platform.

## Kaj se boste naučili

- Kako namestiti in zagnati terminalski uporabniški vmesnik `ds4-cockpit`
- Kako ustvariti orodjarno (toolbox) ds4 ROCm v vsebniku
- Prenos priporočene kvantizacije za eno vozlišče Halo
- Zagon sklepalnega strežnika ds4 in izpostavitev končne točke, združljive z OpenAI
- Povezovanje spletnega vmesnika ali kodirnega agenta z lokalnim strežnikom

<!-- @setup:memory_config -->

## Namestitev programskih predpogojev

> **Sistemske zahteve za to konfiguracijo (enovozliščna IQ2_XXS pri 126k kontekstu):**
> - Sistem Strix Halo z **vsaj 128 GB skupnega (unified) pomnilnika**.
> - **Namenski VRAM v BIOS-u (UMA frame buffer), nastavljen na minimum**, da je lahko skupni pomnilniški bazen čim večji.
> - **Skupni pomnilniški bazen GPE nastavljen na vsaj 110 GB**: zaženite `amd-ttm --set 110` (glejte zgornji korak konfiguracije pomnilnika) in ponovno zaženite sistem. Nižje vrednosti povzročijo napako zaradi pomanjkanja pomnilnika pri nalaganju modela s 126k kontekstom. Če ima vaš sistem na voljo manj pomnilnika, namesto tega zmanjšajte vrednost **Context** v načinu strežnika (Server Mode).

ds4-cockpit uporablja orodjarne (toolbox) v vsebnikih za zagon pogona ds4. Namestite `podman`, `distrobox` in `pipx`:

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

## Razpoložljive kvantizacije

Avtor ds4 zagotavlja več kvantiziranih različic DeepSeek V4 Flash v formatu GGUF. Vsi spodnji modeli uporabljajo kalibracijo z matriko pomembnosti (imatrix), ki ohranja višjo natančnost za tiste dele modela, ki so najpomembnejši za opravila kodiranja in sklepanja.

| Kvantizacija | Velikost | Opis |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Priporočeno za eno vozlišče s 128 GB |
| [Hibridni Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Ohranja plasti 37–42 pri natančnosti Q4 za boljšo natančnost. Se prilega v 128 GB, vendar pusti manj prostora za kontekst |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Višja kakovost. Zahteva dve vozlišči Halo prek gručenja z več vozlišči |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Neobvezen dodatek za spekulativno dekodiranje za izboljšanje hitrosti generiranja |

Model **IQ2_XXS imatrix** je dobro izhodišče. Udobno se prilega na eno vozlišče in pusti dovolj pomnilnika za razumno velikost kontekstnega okna.

## Nameščanje ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) je lahek terminalski uporabniški vmesnik, ki olajša zagon in delovanje ds4 na Strix Halo. Poskrbi za ustvarjanje vsebnikov orodjarn, prenos uteži modela in zagon strežnikov. Namestite ga z `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Zaženite kokpit:
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

## Ustvarjanje orodjarne (Toolbox)

V zavihku **Interactive Toolboxes** izberite najnovejšo razpoložljivo orodjarno (npr. `ds4-rocm-7.2.4`) in kliknite **Create/Update**. To pridobi vsebniško sliko in ustvari okolje orodjarne.

> **Nasvet**: Različica orodjarne se bo sčasoma spreminjala, ko bodo izšle novejše različice ROCm. Izberite najnovejšo, ki je na voljo na seznamu.

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

## Prenos modela

Pojdite na zavihek **Model Manager**. V spustnem meniju izberite **IQ2_XXS imatrix (~80.8 GB)** in kliknite **Download**. Datoteke modela bodo privzeto shranjene v `~/ds4` (pot shranjevanja lahko spremenite).

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

## Zagon strežnika

Pojdite na zavihek **Server Mode**. Izberite preneseni model in orodjarno, nato konfigurirajte velikost konteksta (npr. 126000), gostitelja in vrata (8000). Ko ste pripravljeni, kliknite **Start ds4-server**.

> **KV Disk Cache (neobvezno).** Vklop možnosti **KV Disk Cache** prenese predpomnilnik KV na disk (v **Host Cache Dir**, privzeto `~/.cache/ds4-kv`), tako da se ponavljajoči se sistemski pozivi obnovijo s SSD-ja namesto ponovnega izračunavanja. Gre za optimizacijo zmogljivosti za delovne tokove kodirnih agentov z dolgimi, ponavljajočimi se pozivi in **ni potrebna** za zagon strežnika.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Strežnik se bo zagnal in poslušal na vratih 8000, pri čemer bo izpostavil končno točko API-ja, združljivo z OpenAI, na naslovu `http://localhost:8000/v1`.

**Hitri preizkus:**
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

## Povezovanje spletnega vmesnika

Povežete lahko kateri koli klepetalni vmesnik, ki podpira format API-ja OpenAI. Za uporabo HuggingFace ChatUI, na primer:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Odprite `http://localhost:3000` v brskalniku, da začnete klepetati.

## Povezovanje kodirnega agenta

Strežnik ds4 izpostavlja tako končne točke, združljive z OpenAI, kot tudi z Anthropic, zato se lahko z njim neposredno poveže večina kodirnih agentov. Za dodajanje v kodirnega agenta `pi`, na primer, dodajte naslednji blok v `~/.pi/agent/models.json`:

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

> **Nasvet**: Če vaš kodirni agent ali spletni vmesnik deluje na drugem računalniku kot platforma Halo, boste morali posredovati vrata 8000 prek SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```
## Naslednji koraki

- **Večvozliščno gručenje**: Če imate dve napravi Halo, ds4 omogoča porazdelitev modela Q4 (~153 GB) med obema napravama prek cevovodne vzporednosti (pipeline parallelism). Za navodila za nastavitev glejte [dokumentacijo ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Špekulativno dekodiranje (MTP)**: Prenesite uteži MTP (~3,6 GB) in strežniku posredujte `--mtp` za hitrejšo hitrost generiranja.
- **Razbremenitev predpomnilnika KV na disk**: Za delovne tokove kodirnih agentov omogočite `--kv-disk-dir`, da se ponavljajoči se sistemski pozivi obnovijo iz SSD-ja namesto ponovnega izračunavanja vsakič znova.

Za več informacij glejte [repozitorij ds4](https://github.com/antirez/ds4) in [orodje ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).