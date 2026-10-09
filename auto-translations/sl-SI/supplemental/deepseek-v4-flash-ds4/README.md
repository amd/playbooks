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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) je na učinkovitost usmerjena različica družine DeepSeek V4 — model Mixture of Experts z 284 milijardami parametrov in 13 milijardami aktivnih parametrov. Glede na [DeepSeekovo tehnično poročilo](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) doseže 79 % na SWE-bench Verified in 91,6 % na LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) je namenski sklepalni pogon, zgrajen posebej za to arhitekturo modela. Namesto splošnonamenskega izvajalnega okolja je ds4 usmerjen neposredno na družino DeepSeek V4, z optimizacijami jeder, specifičnimi za arhitekturo, za programsko opremo AMD ROCm™. Trenutno je ena izmed najbolje delujočih implementacij modela DeepSeek V4 Flash na platformi Strix Halo.

Ta vodnik prikazuje, kako z `ai-toolbox-cockpit`, terminalskim uporabniškim vmesnikom, nastaviti ds4, prenesti uteži modela ter zagnati lokalno strežbo modela DeepSeek V4 Flash na razvojni platformi AMD Ryzen™ AI Halo.

## Kaj se boste naučili

- Kako namestiti in zagnati terminalski uporabniški vmesnik `ai-toolbox-cockpit`
- Kako ustvariti vsebnik toolbox za ds4 ROCm
- Prenos priporočene kvantizacije za eno vozlišče Halo
- Zagon strežnika za sklepanje ds4 in izpostavitev končne točke, združljive z OpenAI
- Povezovanje spletnega uporabniškega vmesnika ali agenta za kodiranje z lokalnim strežnikom

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

## Namestitev programskih predpogojev

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:podman,distrobox,ds4-cockpit,ds4-toolbox-image -->

> **Sistemske zahteve za to konfiguracijo (eno vozlišče IQ2_XXS pri kontekstu 126k):**
> - Sistem Strix Halo z **vsaj 128 GB enotnega pomnilnika**.
> - **Namenski VRAM v BIOS-u (UMA frame buffer) nastavljen na minimum**, da je lahko skupni pomnilniški nabor čim večji.
> - **Skupni pomnilniški nabor GPE nastavljen na vsaj 110 GB**: zaženite `amd-ttm --set 110` (glejte zgornji korak konfiguracije pomnilnika) in ponovno zaženite sistem. Nižje vrednosti lahko povzročijo napako pomanjkanja pomnilnika pri nalaganju modela pri kontekstu 126k. Če ima vaš sistem na voljo manj pomnilnika, raje znižajte vrednost **Context** v načinu Server Mode.
>
> **Opomba:** Poskusite nastaviti **skupni pomnilniški nabor GPE** na **110 GB** kot izhodiščno vrednost. Če naletite na napake pomanjkanja pomnilnika, povečajte skupni pomnilniški nabor ali znižajte velikost konteksta.

ai-toolbox-cockpit za zagon pogona ds4 uporablja toolbox vsebnike. Namestite `podman`, `distrobox` in `pipx`:

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

Avtor ds4 ponuja več kvantiziranih različic modela DeepSeek V4 Flash v obliki GGUF. Vsi spodnji modeli uporabljajo kalibracijo z matriko pomembnosti (imatrix), ki ohranja višjo natančnost tistih delov modela, ki so najpomembnejši za naloge kodiranja in sklepanja.

| Kvantizacija | Velikost | Opis |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Priporočeno za eno vozlišče s 128 GB |
| [Hibridni Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Ohranja plasti 37–42 pri natančnosti Q4 za boljšo natančnost. Prilega se v 128 GB, vendar pusti manj prostora za kontekst |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Višja kakovost. Zahteva dve vozlišči Halo prek gručenja z več vozlišči |
| [Špekulativno dekodiranje MTP](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Dodatna možnost za špekulativno dekodiranje za izboljšanje hitrosti generiranja |

Model **IQ2_XXS imatrix** je dobra izhodiščna točka. Udobno se prilega enemu vozlišču in pusti dovolj pomnilnika za razumno veliko kontekstno okno.

## Nameščanje ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) je lahek terminalski uporabniški vmesnik, ki olajša namestitev različnih zalednih sistemov za UI. Uporabili ga bomo za ustvarjanje našega vsebnika ds4, prenos uteži modela in zagon strežnikov. Namestite ga z `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Zaženite cockpit:
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

## Korak 1: Ustvarjanje toolboxa

V zavihku **Interactive Toolboxes** izberite najnovejši razpoložljivi/stabilni toolbox za ds4 (npr. `ds4-rocm-10.0`) in kliknite **Create/Update**. S tem se prenese slika vsebnika in ustvari okolje toolboxa.


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

## Korak 2: Prenos modela

Pojdite na zavihek **Models**. Najprej izberite zaledni sistem (ds4). Nato v spustnem seznamu izberite **IQ2_XXS imatrix (~80,8 GB)** in kliknite **Download**. Datoteke modela bodo privzeto shranjene v `~/ds4` (pot shranjevanja lahko spremenite).

> **Opomba:** Model IQ2_XXS je velik približno 80 GB, zato lahko prenos glede na vašo povezavo traja dlje časa. Ko se zaključi, lahko nadaljujete.

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

## Korak 3: Zagon strežnika

Pojdite na zavihek **Server Mode**. Izberite preneseni model in toolbox, nato konfigurirajte velikost konteksta, gostitelja in vrata. Ko ste pripravljeni, kliknite **Start ds4-server**.

> **Nasvet** Velikost konteksta `126000` je razumna izhodiščna vrednost, ki bi se morala prilegati enemu vozlišču — nastavite jo lahko višje, če imate na voljo dodaten pomnilnik, ali nižje, če naletite na napake pomanjkanja pomnilnika. Vrata (`8000` v tem vodniku) so poljubna; izberite katerakoli prosta vrata.

> **Predpomnilnik KV na disku (neobvezno).** Vklop možnosti **KV Disk Cache** razbremeni predpomnilnik KV na disk (v **Host Cache Dir**, privzeto `~/.cache/ds4-kv`), tako da se ponavljajoči sistemski pozivi obnovijo s SSD-ja namesto ponovnega izračuna. To je optimizacija zmogljivosti za delovne tokove agentov za kodiranje z dolgimi, ponavljajočimi se pozivi in **ni obvezna** za zagon strežnika.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Strežnik se bo zagnal in poslušal na vratih 8000, pri čemer bo izpostavil končno točko API, združljivo z OpenAI, na naslovu `http://localhost:8000/v1`.

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
## Povezovanje spletnega vmesnika

Lahko povežete kateri koli klepetalni vmesnik, ki podpira obliko OpenAI API. Na primer, za uporabo HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Odprite `http://localhost:3000` v brskalniku, da začnete klepetati.

> **Opomba:** `--network=host` postavi spletni vmesnik v omrežje gostitelja, tako da lahko neposredno doseže strežnik ds4 na `localhost`. To ohranja strežnik ds4 vezan na povratno zanko (loopback) (ni ga treba izpostaviti na drugih vmesnikih).

> **Nasvet:** Vrata spletnega vmesnika (tukaj `3000`, nastavljena prek `PORT`) so poljubna — izberite katera koli prosta vrata, če so `3000` že zasedena, in v brskalniku odprite ta vrata namesto tega. Prepričajte se, da se vrata v `OPENAI_BASE_URL` ujemajo z vrati, na katerih teče vaš strežnik ds4.

## Povezovanje kodirnega agenta

Strežnik ds4 izpostavlja tako z OpenAI kot z Anthropic združljive končne točke, zato se lahko večina kodirnih agentov poveže z njim neposredno. Na primer, za dodajanje k kodirnemu agentu `pi` dodajte naslednji blok v `~/.pi/agent/models.json`:

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

> **Nasvet**: Če vaš kodirni agent ali spletni vmesnik teče na drugem računalniku kot platforma Halo, boste morali posredovati vrata strežnika (tukaj `8000`) prek SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Naslednji koraki

- **Večvozliščno povezovanje v gruče (multi-node clustering)**: Če imate dve napravi Halo, ds4 podpira porazdelitev modela Q4 (~153 GB) med obema napravama s pomočjo cevovodne vzporednosti (pipeline parallelism). Za navodila za nastavitev si oglejte [dokumentacijo ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Spekulativno dekodiranje (MTP)**: Prenesite uteži MTP (~3,6 GB) in strežniku podajte `--mtp` za hitrejšo hitrost generiranja.
- **Razbremenitev predpomnilnika KV na disk**: Za delovne tokove kodirnih agentov omogočite `--kv-disk-dir`, tako da se ponavljajoči se sistemski pozivi obnovijo s SSD-ja namesto da bi se vsakič znova izračunali.

Za več informacij si oglejte [repozitorij ds4](https://github.com/antirez/ds4) in [orodje ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).