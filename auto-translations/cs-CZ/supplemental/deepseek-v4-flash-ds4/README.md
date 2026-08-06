<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Přehled

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) je varianta rodiny DeepSeek V4 zaměřená na efektivitu — model typu Mixture of Experts s 284 miliardami parametrů, z nichž 13 miliard je aktivních. Podle [technické zprávy společnosti DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) dosahuje 79 % na SWE-bench Verified a 91,6 % na LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) je specializovaný inferenční engine vytvořený přímo pro tuto architekturu modelu. Namísto univerzálního runtime cílí ds4 přímo na rodinu DeepSeek V4 pomocí optimalizací jader specifických pro danou architekturu pro software AMD ROCm™. V současnosti se jedná o jednu z nejvýkonnějších implementací modelu DeepSeek V4 Flash na platformě Strix Halo.

Tento tutoriál ukazuje, jak pomocí terminálového uživatelského rozhraní `ds4-cockpit` nastavit ds4, stáhnout váhy modelu a spustit lokální poskytování modelu DeepSeek V4 Flash na vývojářské platformě AMD Ryzen™ AI Halo.

## Co se naučíte

- Jak nainstalovat a spustit terminálové uživatelské rozhraní `ds4-cockpit`
- Jak vytvořit ROCm toolbox kontejner pro ds4
- Stažení doporučené kvantizace pro jeden uzel Halo
- Spuštění inferenčního serveru ds4 a zpřístupnění koncového bodu kompatibilního s OpenAI
- Připojení webového rozhraní nebo kódovacího agenta k lokálnímu serveru

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

## Instalace softwarových předpokladů

> **Systémové požadavky pro tuto konfiguraci (jednouzlová konfigurace IQ2_XXS s kontextem 126k):**
> - Systém Strix Halo s **alespoň 128 GB sdílené paměti**.
> - **Vyhrazená paměť VRAM v BIOSu (UMA frame buffer) nastavená na minimum**, aby sdílený paměťový fond mohl být co největší.
> - **Sdílený paměťový fond GPU nastavený na alespoň 110 GB**: spusťte `amd-ttm --set 110` (viz výše uvedený krok konfigurace paměti) a restartujte systém. Nižší hodnoty mohou při načítání modelu s kontextem 126k selhat kvůli nedostatku paměti. Pokud máte k dispozici méně paměti, snižte místo toho hodnotu **Context** v režimu Server Mode.
>
> **Poznámka:** Jako výchozí bod zkuste nastavit **sdílený paměťový fond GPU** na **110 GB**. Pokud narazíte na chyby způsobené nedostatkem paměti, zvyšte sdílený paměťový fond nebo snižte velikost kontextu.

ds4-cockpit využívá kontejnerové toolboxy ke spuštění enginu ds4. Nainstalujte `podman`, `distrobox` a `pipx`:

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

## Dostupné kvantizace

Autor ds4 poskytuje několik kvantizovaných verzí modelu DeepSeek V4 Flash ve formátu GGUF. Všechny níže uvedené modely využívají kalibraci pomocí matice důležitosti (imatrix), která zachovává vyšší přesnost v těch částech modelu, jež jsou nejdůležitější pro úlohy spojené s programováním a uvažováním.

| Kvantizace | Velikost | Popis |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Doporučeno pro jeden uzel se 128 GB |
| [Hybridní Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Zachovává vrstvy 37–42 v přesnosti Q4 pro lepší přesnost. Vejde se do 128 GB, ale ponechává méně prostoru pro kontext |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Vyšší kvalita. Vyžaduje dva uzly Halo pomocí vícemodulárního clusteringu |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Volitelný doplněk pro spekulativní dekódování za účelem zvýšení rychlosti generování |

Model **IQ2_XXS imatrix** je dobrým výchozím bodem. Pohodlně se vejde na jeden uzel a ponechává dostatek paměti pro rozumně velké kontextové okno.

## Instalace ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) je odlehčené terminálové uživatelské rozhraní, které usnadňuje rozjezd a provoz ds4 na platformě Strix Halo. Stará se o vytváření kontejnerů toolboxů, stahování vah modelu a spouštění serverů. Nainstalujte jej pomocí `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Spusťte cockpit:
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

## Vytvoření toolboxu

Na kartě **Interactive Toolboxes** vyberte nejnovější dostupný/stabilní toolbox (např. `ds4-rocm-7.2.4`) a klikněte na **Create/Update**. Tím se stáhne obraz kontejneru a vytvoří se prostředí toolboxu.


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

## Stažení modelu

Přejděte na kartu **Model Manager**. V rozbalovací nabídce vyberte **IQ2_XXS imatrix (~80,8 GB)** a klikněte na **Download**. Soubory modelu se ve výchozím nastavení uloží do `~/ds4` (cestu k úložišti lze změnit).

> **Poznámka:** Model IQ2_XXS má přibližně 80 GB, takže stahování může v závislosti na rychlosti připojení nějakou dobu trvat. Po dokončení můžete pokračovat.

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

## Spuštění serveru

Přejděte na kartu **Server Mode**. Vyberte stažený model a toolbox, poté nastavte velikost kontextu, hostitele a port. Až budete připraveni, klikněte na **Start ds4-server**.

> **Tip** Velikost kontextu `126000` je rozumná výchozí hodnota, která by se měla vejít na jeden uzel — pokud máte paměti nazbyt, můžete ji nastavit vyšší, nebo ji snižte, pokud narazíte na chyby způsobené nedostatkem paměti. Port (`8000` v tomto návodu) je libovolný — vyberte jakýkoli volný port.

> **KV Disk Cache (volitelné).** Zapnutím **KV Disk Cache** se KV cache odloží na disk (do **Host Cache Dir**, výchozí `~/.cache/ds4-kv`), takže opakované systémové promptové zprávy se obnoví z SSD disku místo opětovného přepočítávání. Jde o optimalizaci výkonu pro pracovní postupy kódovacích agentů s dlouhými, opakujícími se prompty a **není nutná** pro spuštění serveru.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Server se spustí a bude naslouchat na portu 8000, čímž zpřístupní koncový bod API kompatibilní s OpenAI na adrese `http://localhost:8000/v1`.

**Rychlý test:**
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

## Připojení webového rozhraní

Můžete připojit libovolné chatovací rozhraní, které podporuje formát OpenAI API. Například pro použití HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Otevřete `http://localhost:3000` ve svém prohlížeči a začněte chatovat.
## Připojení kódovacího agenta

Server ds4 poskytuje koncové body kompatibilní s OpenAI i Anthropic, takže se k němu dá připojit přímo z většiny kódovacích agentů. Pokud jej chcete například přidat do kódovacího agenta `pi`, přidejte následující blok do souboru `~/.pi/agent/models.json`:

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

> **Tip**: Pokud váš kódovací agent nebo webové uživatelské rozhraní běží na jiném počítači než platforma Halo, budete muset port 8000 přesměrovat pomocí SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Další kroky

- **Vícenodové clustery**: Pokud máte dvě zařízení Halo, ds4 podporuje distribuci modelu Q4 (~153 GB) mezi oba počítače pomocí pipeline paralelismu. Pokyny k nastavení najdete v [dokumentaci ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Spekulativní dekódování (MTP)**: Stáhněte si váhy MTP (~3,6 GB) a pro rychlejší generování předejte serveru parametr `--mtp`.
- **Odkládání KV cache na disk**: Pro pracovní postupy kódovacích agentů povolte `--kv-disk-dir`, aby se opakující se systémové výzvy obnovovaly z SSD místo toho, aby se pokaždé znovu počítaly.

Další informace najdete v [repozitáři ds4](https://github.com/antirez/ds4) a v nástroji [ds4-cockpit toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox).