<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) je različica družine DeepSeek V4, osredotočena na učinkovitost — model mešanice strokovnjakov (Mixture of Experts) s 284 milijardami parametrov, od katerih je 13 milijard aktivnih. Glede na [tehnično poročilo podjetja DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) doseže 79 % pri SWE-bench Verified in 91,6 % pri LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) je namenski sklepalni pogon (inference engine), zgrajen posebej za to arhitekturo modela. Namesto splošno namenskega izvajalnega okolja je ds4 usmerjen neposredno na družino DeepSeek V4, z optimizacijami jeder, specifičnimi za arhitekturo, za programsko opremo AMD ROCm™. Trenutno je ena najbolje delujočih implementacij DeepSeek V4 Flash na Strix Halo.

Ta vadnica prikazuje, kako z orodjem `ds4-cockpit`, terminalskim uporabniškim vmesnikom, namestiti ds4, prenesti uteži modela in lokalno zagnati strežbo DeepSeek V4 Flash na platformi AMD Ryzen™ AI Halo Developer Platform.

## Kaj se boste naučili

- Kako namestiti in zagnati terminalski uporabniški vmesnik `ds4-cockpit`
- Kako ustvariti vsebnik orodne zbirke (toolbox) ds4 ROCm
- Prenos priporočene kvantizacije za posamezno vozlišče Halo
- Zagon strežnika za sklepanje ds4 in izpostavitev API-jevske končne točke, združljive z OpenAI
- Povezovanje spletnega vmesnika ali agenta za kodiranje z lokalnim strežnikom

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

## Namestitev programskih predpogojev

> **Sistemske zahteve za to konfiguracijo (posamezno vozlišče, IQ2_XXS pri kontekstu 126k):**
> - Sistem Strix Halo z **vsaj 128 GB enotnega pomnilnika**.
> - **Namenski VRAM v BIOS-u (UMA medpomnilnik) naj bo nastavljen na najnižjo vrednost**, tako da je skupni pomnilniški bazen lahko čim večji.
> - **Skupni pomnilniški bazen GPE naj bo nastavljen na vsaj 110 GB**: zaženite `amd-ttm --set 110` (glejte zgornji korak konfiguracije pomnilnika) in znova zaženite sistem. Nižje vrednosti lahko povzročijo napako zaradi pomanjkanja pomnilnika ob nalaganju modela pri kontekstu 126k. Če ima vaš sistem na voljo manj pomnilnika, namesto tega znižajte vrednost **Context** v načinu Server Mode.
>
> **Opomba:** Kot izhodišče poskusite nastaviti **skupni pomnilniški bazen GPE** na **110 GB**. Če naletite na napake zaradi pomanjkanja pomnilnika, povečajte skupni pomnilniški bazen ali zmanjšajte velikost konteksta.

ds4-cockpit za zagon pogona ds4 uporablja vsebniške orodne zbirke (toolboxes). Namestite `podman`, `distrobox` in `pipx`:

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

Avtor ds4 zagotavlja več kvantiziranih različic DeepSeek V4 Flash v obliki GGUF. Vsi spodnji modeli uporabljajo kalibracijo matrike pomembnosti (imatrix), ki ohranja višjo natančnost za tiste dele modela, ki so najpomembnejši za naloge kodiranja in sklepanja.

| Kvantizacija | Velikost | Opis |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Priporočeno za posamezno vozlišče s 128 GB |
| [Hibridni Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Ohranja plasti 37–42 pri natančnosti Q4 za boljšo točnost. Ustreza v 128 GB, vendar pusti manj prostora za kontekst |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Višja kakovost. Zahteva dve vozlišči Halo prek gručenja z več vozlišči (multi-node clustering) |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Neobvezen dodatek za špekulativno dekodiranje za izboljšanje hitrosti generiranja |

Model **IQ2_XXS imatrix** je dobro izhodišče. Udobno se prilega na posamezno vozlišče in pusti dovolj pomnilnika za razumno velik kontekstni okvir.

## Nameščanje ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) je lahek terminalski uporabniški vmesnik, ki olajša zagon in delovanje ds4 na Strix Halo. Poskrbi za ustvarjanje vsebnikov orodnih zbirk, prenos uteži modela in zagon strežnikov. Namestite ga s `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Zaženite kabino (cockpit):
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

## Ustvarjanje orodne zbirke

V zavihku **Interactive Toolboxes** izberite najnovejšo razpoložljivo/stabilno orodno zbirko (npr. `ds4-rocm-7.2.4`) in kliknite **Create/Update**. To povleče sliko vsebnika in ustvari okolje orodne zbirke.


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

Odprite zavihek **Model Manager**. V spustnem meniju izberite **IQ2_XXS imatrix (~80,8 GB)** in kliknite **Download**. Datoteke modela bodo privzeto shranjene v `~/ds4` (pot za shranjevanje lahko spremenite).

> **Opomba:** Model IQ2_XXS je velik približno 80 GB, zato lahko prenos glede na vašo povezavo traja dlje časa. Ko se prenos konča, lahko nadaljujete.

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

Odprite zavihek **Server Mode**. Izberite prenesen model in orodno zbirko, nato konfigurirajte velikost konteksta, gostitelja in vrata. Ko ste pripravljeni, kliknite **Start ds4-server**.

> **Nasvet** Velikost konteksta `126000` je razumna začetna vrednost, ki bi morala ustrezati na posameznem vozlišču — nastavite jo lahko višje, če imate na voljo dodaten pomnilnik, ali nižje, če naletite na napake zaradi pomanjkanja pomnilnika. Vrata (`8000` v tem vodniku) so poljubna; izberite katera koli prosta vrata.

> **Predpomnilnik KV na disku (neobvezno).** Vklop **KV Disk Cache** prenese predpomnilnik KV na disk (v **Host Cache Dir**, privzeto `~/.cache/ds4-kv`), tako da se ponavljajoči se sistemski pozivi obnovijo z SSD-ja namesto da bi se znova izračunavali. Gre za optimizacijo zmogljivosti za delovne tokove agentov za kodiranje z dolgimi, ponavljajočimi se pozivi in **ni potrebna** za zagon strežnika.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Strežnik se bo zagnal in poslušal na vratih 8000, ter izpostavil API-jevsko končno točko, združljivo z OpenAI, na naslovu `http://localhost:8000/v1`.

**Hiter test:**
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

## Povezovanje spletnega uporabniškega vmesnika

Povežete lahko kateri koli klepetalni vmesnik, ki podpira obliko API-ja OpenAI. Za uporabo HuggingFace ChatUI na primer:

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

Strežnik ds4 izpostavlja tako z OpenAI kot z Anthropic združljive končne točke, zato se lahko večina kodirnih agentov poveže z njim neposredno. Če ga na primer želite dodati h kodirnemu agentu `pi`, dodajte naslednji blok v `~/.pi/agent/models.json`:

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

> **Namig**: Če vaš kodirni agent ali spletni vmesnik teče na drugi napravi kot platforma Halo, morate vrata 8000 posredovati (angl. forward) prek SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Naslednji koraki

- **Gručenje več vozlišč (multi-node clustering)**: Če imate dve napravi Halo, ds4 podpira porazdelitev modela Q4 (~153 GB) med obema napravama s cevovodno paralelizacijo (angl. pipeline parallelism). Navodila za nastavitev si oglejte v [dokumentaciji ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Špekulativno dekodiranje (MTP)**: Prenesite uteži MTP (~3,6 GB) in strežniku posredujte `--mtp` za hitrejšo generacijo.
- **Razbremenitev predpomnilnika KV na disk**: Za delovne tokove kodirnega agenta omogočite `--kv-disk-dir`, da se ponovljeni sistemski pozivi obnovijo s SSD-ja namesto ponovnega izračuna vsakič znova.

Za več informacij si oglejte [repozitorij ds4](https://github.com/antirez/ds4) in [orodje ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).