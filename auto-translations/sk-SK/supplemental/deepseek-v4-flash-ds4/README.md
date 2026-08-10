<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) je variant rodiny DeepSeek V4 zameraný na efektivitu — model typu Mixture of Experts s 284 miliardami parametrov, z ktorých je 13 miliárd aktívnych. Podľa [technickej správy DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) dosahuje 79 % v teste SWE-bench Verified a 91,6 % v teste LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) je vyhradený inferenčný engine vytvorený špecificky pre túto architektúru modelu. Namiesto univerzálneho runtime prostredia je ds4 zameraný priamo na rodinu DeepSeek V4, s optimalizáciami jadier špecifickými pre danú architektúru pre softvér AMD ROCm™. V súčasnosti ide o jednu z najvýkonnejších implementácií modelu DeepSeek V4 Flash na platforme Strix Halo.

Tento návod ukazuje, ako pomocou terminálového používateľského rozhrania `ds4-cockpit` nastaviť ds4, stiahnuť váhy modelu a spustiť lokálne poskytovanie modelu DeepSeek V4 Flash na vývojárskej platforme AMD Ryzen™ AI Halo.

## Čo sa naučíte

- Ako nainštalovať a spustiť terminálové používateľské rozhranie `ds4-cockpit`
- Ako vytvoriť kontajner ds4 ROCm toolbox
- Stiahnutie odporúčanej kvantizácie pre jeden uzol Halo
- Spustenie inferenčného servera ds4 a sprístupnenie koncového bodu kompatibilného s OpenAI
- Pripojenie webového rozhrania alebo kódovacieho agenta k lokálnemu serveru

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

## Inštalácia softvérových predpokladov

> **Systémové požiadavky pre túto konfiguráciu (jednouzlová IQ2_XXS s kontextom 126 tis.):**
> - Systém Strix Halo s **aspoň 128 GB zdieľanej pamäte**.
> - **VRAM vyhradená v BIOSe (rámcový buffer UMA) nastavená na minimum**, aby mohol byť zdieľaný pamäťový fond čo najväčší.
> - **Zdieľaný pamäťový fond GPU nastavený na aspoň 110 GB**: spustite `amd-ttm --set 110` (pozri krok nastavenia konfigurácie pamäte vyššie) a reštartujte systém. Nižšie hodnoty môžu pri načítaní modelu s kontextom 126 tis. zlyhať pre nedostatok pamäte. Ak má váš systém k dispozícii menej pamäte, znížte namiesto toho hodnotu **Context** v režime Server.
>
> **Poznámka:** Skúste ako východiskovú hodnotu nastaviť **zdieľaný pamäťový fond GPU** na **110 GB**. Ak narazíte na chyby spôsobené nedostatkom pamäte, zvýšte zdieľaný pamäťový fond alebo znížte veľkosť kontextu.

ds4-cockpit používa kontajnerové toolboxy na spúšťanie enginu ds4. Nainštalujte `podman`, `distrobox` a `pipx`:

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

## Dostupné kvantizácie

Autor ds4 poskytuje niekoľko kvantizovaných verzií modelu DeepSeek V4 Flash vo formáte GGUF. Všetky modely uvedené nižšie využívajú kalibráciu pomocou matice dôležitosti (imatrix), ktorá zachováva vyššiu presnosť pre tie časti modelu, ktoré sú najdôležitejšie pre úlohy súvisiace s kódovaním a uvažovaním.

| Kvantizácia | Veľkosť | Popis |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Odporúčané pre jeden uzol so 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Zachováva vrstvy 37 – 42 v presnosti Q4 kvôli lepšej presnosti. Zmestí sa do 128 GB, ale ponecháva menej priestoru pre kontext |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Vyššia kvalita. Vyžaduje dva uzly Halo prostredníctvom viacuzlového klastrovania |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Voliteľný doplnok pre špekulatívne dekódovanie na zlepšenie rýchlosti generovania |

Model **IQ2_XXS imatrix** je dobrým východiskovým bodom. Pohodlne sa zmestí na jeden uzol a ponecháva dostatok pamäte pre primerané okno kontextu.

## Inštalácia ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) je ľahké terminálové používateľské rozhranie, ktoré uľahčuje sprevádzkovanie ds4 na platforme Strix Halo. Zabezpečuje vytváranie kontajnerov toolbox, sťahovanie váh modelu a spúšťanie serverov. Nainštalujte ho pomocou `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Spustite cockpit:
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

## Vytvorenie toolboxu

Na karte **Interactive Toolboxes** vyberte najnovší dostupný/stabilný toolbox (napr. `ds4-rocm-7.2.4`) a kliknite na **Create/Update**. Týmto sa stiahne obraz kontajnera a vytvorí sa prostredie toolboxu.


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

## Stiahnutie modelu

Prejdite na kartu **Model Manager**. Z rozbaľovacieho zoznamu vyberte **IQ2_XXS imatrix (~80,8 GB)** a kliknite na **Download**. Súbory modelu sa predvolene uložia do priečinka `~/ds4` (cestu na ukladanie môžete zmeniť).

> **Poznámka:** Model IQ2_XXS má približne 80 GB, takže sťahovanie môže v závislosti od pripojenia chvíľu trvať. Po jeho dokončení môžete pokračovať.

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

## Spustenie servera

Prejdite na kartu **Server Mode**. Vyberte stiahnutý model a toolbox, potom nakonfigurujte veľkosť kontextu, hostiteľa a port. Keď budete pripravení, kliknite na **Start ds4-server**.

> **Tip** Veľkosť kontextu `126000` je rozumná východisková hodnota, ktorá by mala fungovať na jednom uzle — ak máte k dispozícii viac pamäte, môžete ju nastaviť vyššie, alebo ju znížte, ak narazíte na chyby spôsobené nedostatkom pamäte. Port (`8000` v tomto návode) je ľubovoľný — vyberte akýkoľvek voľný port.

> **Vyrovnávacia pamäť KV na disku (voliteľné).** Zapnutím **KV Disk Cache** sa vyrovnávacia pamäť KV odsunie na disk (v priečinku **Host Cache Dir**, predvolene `~/.cache/ds4-kv`), takže opakované systémové výzvy sa obnovujú z SSD namiesto opätovného výpočtu. Ide o optimalizáciu výkonu pre pracovné postupy kódovacích agentov s dlhými, opakovanými výzvami a **nie je potrebná** na spustenie servera.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Server sa spustí a bude počúvať na porte 8000, pričom sprístupní koncový bod API kompatibilný s OpenAI na adrese `http://localhost:8000/v1`.

**Rýchly test:**
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

## Pripojenie webového rozhrania

Môžete pripojiť akékoľvek chatovacie rozhranie, ktoré podporuje formát OpenAI API. Napríklad na použitie HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Otvorte `http://localhost:3000` vo svojom prehliadači a začnite chatovať.
## Pripojenie kódovacieho agenta

Server ds4 poskytuje koncové body kompatibilné s OpenAI aj Anthropic, takže väčšina kódovacích agentov sa naň dokáže pripojiť priamo. Napríklad na jeho pridanie do kódovacieho agenta `pi` pridajte nasledujúci blok do `~/.pi/agent/models.json`:

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

> **Tip**: Ak váš kódovací agent alebo Web UI beží na inom stroji ako platforma Halo, budete musieť port 8000 presmerovať cez SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Ďalšie kroky

- **Klastrovanie viacerých uzlov**: Ak máte dve zariadenia Halo, ds4 podporuje distribúciu modelu Q4 (~153 GB) medzi oboma strojmi pomocou pipeline paralelizmu. Pokyny na nastavenie nájdete v [dokumentácii ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Špekulatívne dekódovanie (MTP)**: Stiahnite si váhy MTP (~3,6 GB) a odovzdajte serveru parameter `--mtp` na dosiahnutie rýchlejšej generácie.
- **Odkladanie KV cache na disk**: Pri pracovných postupoch s kódovacím agentom povoľte `--kv-disk-dir`, aby sa opakované systémové príkazy obnovovali z SSD namiesto ich opätovného výpočtu zakaždým.

Ďalšie informácie nájdete v [repozitári ds4](https://github.com/antirez/ds4) a v nástroji [ds4-cockpit toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox).