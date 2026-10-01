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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) je na efektivitu zaměřená varianta rodiny DeepSeek V4 — model typu Mixture of Experts se 284 miliardami parametrů, z toho 13 miliard aktivních parametrů. Podle [technické zprávy DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) dosahuje 79 % na SWE-bench Verified a 91,6 % na LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) je vyhrazený inferenční engine postavený speciálně pro tuto architekturu modelu. Namísto univerzálního běhového prostředí je ds4 zaměřen přímo na rodinu DeepSeek V4 s optimalizacemi jader specifickými pro architekturu určenými pro AMD ROCm™ software. V současnosti se jedná o jednu z nejvýkonnějších implementací DeepSeek V4 Flash na platformě Strix Halo.

Tento tutoriál ukazuje, jak pomocí `ai-toolbox-cockpit`, terminálového uživatelského rozhraní, nastavit ds4, stáhnout váhy modelu a lokálně spustit obsluhu modelu DeepSeek V4 Flash na vývojářské platformě AMD Ryzen™ AI Halo.

## Co se naučíte

- Jak nainstalovat a spustit terminálové uživatelské rozhraní `ai-toolbox-cockpit`
- Jak vytvořit toolbox kontejner ds4 ROCm
- Stažení doporučené kvantizace pro jeden uzel Halo
- Spuštění inferenčního serveru ds4 a zpřístupnění koncového bodu kompatibilního s OpenAI
- Připojení webového uživatelského rozhraní nebo kódovacího agenta k lokálnímu serveru

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

## Instalace požadovaného softwaru

> **Systémové požadavky pro tuto konfiguraci (jeden uzel, IQ2_XXS při kontextu 126k):**
> - Systém Strix Halo s **minimálně 128 GB sjednocené paměti (unified memory)**.
> - **Vyhrazená VRAM v BIOSu (UMA frame buffer) nastavená na minimum**, aby sdílený paměťový fond mohl být co největší.
> - **Sdílený paměťový fond GPU nastavený na alespoň 110 GB**: spusťte `amd-ttm --set 110` (viz krok nastavení konfigurace paměti výše) a restartujte. Nižší hodnoty mohou způsobit chybu nedostatku paměti při načítání modelu s kontextem 126k. Pokud má váš systém méně dostupné paměti, snižte místo toho hodnotu **Context** v režimu Server Mode.
>
> **Poznámka:** Zkuste jako výchozí bod nastavit **sdílený paměťový fond GPU** na **110 GB**. Pokud narazíte na chyby nedostatku paměti, zvyšte sdílený paměťový fond nebo snižte velikost kontextu.

ai-toolbox-cockpit používá kontejnerové toolboxy ke spouštění enginu ds4. Nainstalujte `podman`, `distrobox` a `pipx`:

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

Autor ds4 poskytuje několik kvantizovaných verzí modelu DeepSeek V4 Flash ve formátu GGUF. Všechny níže uvedené modely používají kalibraci pomocí matice důležitosti (imatrix), která zachovává vyšší přesnost pro ty části modelu, na kterých nejvíce záleží při úlohách zaměřených na programování a uvažování.

| Kvantizace | Velikost | Popis |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Doporučeno pro jeden uzel s 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Zachovává vrstvy 37–42 v přesnosti Q4 pro vyšší přesnost. Vejde se do 128 GB, ale ponechává méně prostoru pro kontext |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Vyšší kvalita. Vyžaduje dva uzly Halo prostřednictvím vícenodového clusteringu |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Volitelný doplněk pro spekulativní dekódování ke zlepšení rychlosti generování |

Model **IQ2_XXS imatrix** je dobrým výchozím bodem. Pohodlně se vejde na jeden uzel a ponechává dostatek paměti pro rozumně velké kontextové okno.

## Instalace ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) je odlehčené terminálové uživatelské rozhraní, které usnadňuje instalaci různých AI backendů. Použijeme ho k vytvoření našeho kontejneru ds4, stažení váh modelu a spouštění serverů. Nainstalujte ho pomocí `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Spusťte cockpit:
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

## Krok 1: Vytvoření toolboxu

Na kartě **Interactive Toolboxes** vyberte nejnovější dostupný/stabilní toolbox pro ds4 (např. `ds4-rocm-10.0`) a klikněte na **Create/Update**. Tím se stáhne obraz kontejneru a vytvoří prostředí toolboxu.


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

## Krok 2: Stažení modelu

Přejděte na kartu **Models**. Nejprve vyberte backend (ds4). Poté z rozbalovací nabídky vyberte **IQ2_XXS imatrix (~80,8 GB)** a klikněte na **Download**. Soubory modelu se ve výchozím nastavení uloží do `~/ds4` (cestu uložení lze změnit).

> **Poznámka:** Model IQ2_XXS má přibližně 80 GB, takže stahování může v závislosti na vašem připojení nějakou dobu trvat. Po dokončení můžete pokračovat.

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

## Krok 3: Spuštění serveru

Přejděte na kartu **Server Mode**. Vyberte stažený model a toolbox, poté nastavte velikost kontextu, hostitele a port. Až budete připraveni, klikněte na **Start ds4-server**.

> **Tip** Velikost kontextu `126000` je rozumnou výchozí hodnotou, která by se měla vejít na jeden uzel — pokud máte paměť navíc, můžete ji zvýšit, nebo ji snížit, pokud narazíte na chyby nedostatku paměti. Port (`8000` v tomto průvodci) je libovolný — vyberte jakýkoli volný port.

> **Vyrovnávací paměť KV na disku (volitelné).** Zapnutí **KV Disk Cache** přesune KV cache na disk (do **Host Cache Dir**, výchozí `~/.cache/ds4-kv`), takže opakované systémové prompty se obnovují z SSD místo přepočítávání. Jedná se o optimalizaci výkonu pro pracovní postupy kódovacích agentů s dlouhými, opakujícími se prompty a **není** nutná ke spuštění serveru.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
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
## Připojení webového uživatelského rozhraní

Můžete připojit jakékoli chatovací rozhraní, které podporuje formát OpenAI API. Například pro použití HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Otevřete `http://localhost:3000` ve svém prohlížeči a začněte chatovat.

> **Poznámka:** `--network=host` umístí webové uživatelské rozhraní do sítě hostitele, takže může přímo dosáhnout na server ds4 na `localhost`. Server ds4 tak zůstává navázán pouze na loopback (nemusí být zpřístupněn na jiných rozhraních).

> **Tip:** Port webového uživatelského rozhraní (zde `3000`, nastavený pomocí `PORT`) je libovolný — pokud je `3000` již obsazen, zvolte jakýkoli volný port a otevřete tento port ve svém prohlížeči. Ujistěte se, že port v `OPENAI_BASE_URL` odpovídá portu, na kterém běží váš server ds4.

## Připojení kódovacího agenta

Server ds4 poskytuje jak koncové body kompatibilní s OpenAI, tak s Anthropic, takže se k němu může přímo připojit většina kódovacích agentů. Například pro přidání do kódovacího agenta `pi` přidejte následující blok do `~/.pi/agent/models.json`:

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

> **Tip**: Pokud váš kódovací agent nebo webové uživatelské rozhraní běží na jiném počítači než platforma Halo, budete muset přesměrovat port serveru (zde `8000`) přes SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Další kroky

- **Vícenodové clusterování**: Pokud máte dvě zařízení Halo, ds4 podporuje rozdělení modelu Q4 (~153 GB) mezi oba počítače pomocí pipeline paralelismu. Pokyny k nastavení najdete v [dokumentaci ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Spekulativní dekódování (MTP)**: Stáhněte si váhy MTP (~3,6 GB) a předejte serveru přepínač `--mtp` pro rychlejší generování.
- **Odkládání KV cache na disk**: Pro pracovní postupy kódovacích agentů povolte `--kv-disk-dir`, aby se opakující se systémové výzvy obnovovaly z SSD místo opětovného přepočítávání pokaždé znovu.

Další informace najdete v [repozitáři ds4](https://github.com/antirez/ds4) a v [sadě nástrojů ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).