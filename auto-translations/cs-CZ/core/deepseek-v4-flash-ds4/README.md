<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tento playbook používá speciální značky, které GitHub neumí vykreslit. Pro správné zobrazení tohoto obsahu navštivte prosím [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Přehled

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) je varianta rodiny DeepSeek V4 zaměřená na efektivitu – model typu Mixture of Experts se 284 miliardami parametrů, z nichž 13 miliard je aktivních. Podle [technické zprávy společnosti DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) dosahuje 79 % v testu SWE-bench Verified a 91,6 % v testu LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) je dedikovaný inferenční engine vytvořený speciálně pro tuto architekturu modelu. Namísto obecného běhového prostředí cílí ds4 přímo na rodinu DeepSeek V4 pomocí optimalizací jádra specifických pro danou architekturu pro software AMD ROCm™. V současnosti se jedná o jednu z nejvýkonnějších implementací DeepSeek V4 Flash na platformě Strix Halo.

Tento tutoriál ukazuje, jak pomocí `ds4-cockpit`, terminálového uživatelského rozhraní, nastavit ds4, stáhnout váhy modelu a spustit lokální servírování modelu DeepSeek V4 Flash na platformě AMD Ryzen™ AI Halo Developer Platform.

## Co se naučíte

- Jak nainstalovat a spustit terminálové uživatelské rozhraní `ds4-cockpit`
- Jak vytvořit kontejner ds4 ROCm toolbox
- Stažení doporučené kvantizace pro jeden uzel Halo
- Spuštění inferenčního serveru ds4 a vystavení koncového bodu kompatibilního s OpenAI
- Připojení Web UI nebo kódovacího agenta k lokálnímu serveru

<!-- @setup:memory_config -->

## Instalace softwarových předpokladů

> **Systémové požadavky pro tuto konfiguraci (jednouzlová IQ2_XXS s kontextem 126k):**
> - Systém Strix Halo s **alespoň 128 GB sdílené paměti**.
> - **Vyhrazená paměť VRAM v BIOSu (UMA frame buffer) nastavená na minimum**, aby mohl být sdílený paměťový fond co největší.
> - **Sdílený paměťový fond GPU nastavený na alespoň 110 GB**: spusťte `amd-ttm --set 110` (viz krok konfigurace paměti výše) a restartujte systém. Nižší hodnoty selžou kvůli nedostatku paměti při načítání modelu s kontextem 126k. Pokud má váš systém k dispozici méně paměti, snižte místo toho hodnotu **Context** v Server Mode.

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

Autor ds4 poskytuje několik kvantizovaných verzí modelu DeepSeek V4 Flash ve formátu GGUF. Všechny níže uvedené modely využívají kalibraci pomocí matice důležitosti (imatrix), která zachovává vyšší přesnost u těch částí modelu, na kterých nejvíce záleží pro úkoly kódování a uvažování.

| Kvantizace | Velikost | Popis |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Doporučeno pro jeden uzel s 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Zachovává vrstvy 37–42 v přesnosti Q4 pro lepší přesnost. Vejde se do 128 GB, ale zůstává méně místa pro kontext |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Vyšší kvalita. Vyžaduje dva uzly Halo prostřednictvím vícenuzlového clusteringu |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Volitelný doplněk pro spekulativní dekódování ke zlepšení rychlosti generování |

Model **IQ2_XXS imatrix** je dobrým výchozím bodem. Pohodlně se vejde na jeden uzel a ponechává dostatek paměti pro rozumně velké kontextové okno.

## Instalace ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) je odlehčené terminálové uživatelské rozhraní, které usnadňuje zprovoznění ds4 na platformě Strix Halo. Stará se o vytváření kontejnerů toolboxů, stahování vah modelu a spouštění serverů. Nainstalujte jej pomocí `pipx`:

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

Na kartě **Interactive Toolboxes** vyberte nejnovější dostupný toolbox (např. `ds4-rocm-7.2.4`) a klikněte na **Create/Update**. Tím se stáhne obraz kontejneru a vytvoří se prostředí toolboxu.

> **Tip**: Verze toolboxu se bude v průběhu času měnit s tím, jak budou vydávány novější sestavení ROCm. Vyberte tu nejnovější dostupnou v seznamu.

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

Přejděte na kartu **Model Manager**. V rozbalovací nabídce vyberte **IQ2_XXS imatrix (~80,8 GB)** a klikněte na **Download**. Soubory modelu se ve výchozím nastavení uloží do `~/ds4` (cestu úložiště lze změnit).

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

Přejděte na kartu **Server Mode**. Vyberte stažený model a toolbox, poté nakonfigurujte velikost kontextu (např. 126000), hostitele a port (8000). Až budete připraveni, klikněte na **Start ds4-server**.

> **KV Disk Cache (volitelné).** Zapnutí volby **KV Disk Cache** přesune KV cache na disk (do umístění **Host Cache Dir**, výchozí `~/.cache/ds4-kv`), takže se opakující se systémové výzvy obnovují z SSD místo opětovného přepočítávání. Jedná se o optimalizaci výkonu pro pracovní postupy kódovacích agentů s dlouhými, opakujícími se výzvami a **není nutná** ke spuštění serveru.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Server se spustí a bude naslouchat na portu 8000, čímž vystaví koncový bod API kompatibilní s OpenAI na adrese `http://localhost:8000/v1`.

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

## Připojení Web UI

Můžete připojit jakékoli chatovací rozhraní, které podporuje formát OpenAI API. Například pro použití HuggingFace ChatUI:

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

Server ds4 vystavuje jak koncové body kompatibilní s OpenAI, tak s Anthropic, takže se k němu může přímo připojit většina kódovacích agentů. Chcete-li jej například přidat do kódovacího agenta `pi`, přidejte následující blok do souboru `~/.pi/agent/models.json`:

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

> **Tip**: Pokud váš kódovací agent nebo Web UI běží na jiném počítači než platforma Halo, budete muset přesměrovat port 8000 pomocí SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```
## Další kroky

- **Vícenodové clusterování**: Pokud máte dvě zařízení Halo, ds4 podporuje distribuci modelu Q4 (~153 GB) mezi oba počítače pomocí pipeline paralelismu. Pokyny k nastavení najdete v dokumentaci [ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Spekulativní dekódování (MTP)**: Stáhněte váhy MTP (~3,6 GB) a předejte serveru parametr `--mtp` pro vyšší rychlost generování.
- **Odkládání KV cache na disk**: Pro pracovní postupy kódovacích agentů povolte `--kv-disk-dir`, aby se opakující se systémové prompty obnovovaly z SSD namísto opětovného přepočítávání pokaždé.

Další informace najdete v [repozitáři ds4](https://github.com/antirez/ds4) a v nástroji [ds4-cockpit toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox).