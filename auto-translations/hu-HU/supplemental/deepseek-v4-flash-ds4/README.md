<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés

A [DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) a DeepSeek V4 család hatékonyságra optimalizált változata — egy 284 milliárd paraméteres Mixture of Experts modell, 13 milliárd aktív paraméterrel. A [DeepSeek technikai jelentése](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) szerint a modell 79%-ot ér el a SWE-bench Verified teszten és 91,6%-ot a LiveCodeBench teszten.

A [ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) egy kifejezetten ehhez a modellarchitektúrához épített, dedikált inferencia-motor. Ahelyett, hogy egy általános célú futtatókörnyezet lenne, a ds4 közvetlenül a DeepSeek V4 családot célozza meg, architektúra-specifikus kernel-optimalizációkkal az AMD ROCm™ szoftverhez. Jelenleg az egyik legjobban teljesítő implementáció a DeepSeek V4 Flash számára Strix Halo platformon.

Ez az oktatóanyag bemutatja, hogyan használható a `ds4-cockpit`, egy terminálalapú felhasználói felület, a ds4 beállításához, a modellsúlyok letöltéséhez, és a DeepSeek V4 Flash helyi kiszolgálásának elindításához az AMD Ryzen™ AI Halo Developer Platform-on.

## Amit meg fogsz tanulni

- Hogyan telepítsd és indítsd el a `ds4-cockpit` terminálalapú felhasználói felületet
- Hogyan hozd létre a ds4 ROCm eszköztár-konténert
- Az ajánlott kvantálás letöltése egyetlen Halo csomóponthoz
- A ds4 inferenciaszerver elindítása és egy OpenAI-kompatibilis végpont közzététele
- Egy webes felület vagy kódoló ügynök csatlakoztatása a helyi szerverhez

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

## A szoftverkövetelmények telepítése

> **Rendszerkövetelmények ehhez a konfigurációhoz (egycsomópontos IQ2_XXS, 126k kontextus mellett):**
> - Egy Strix Halo rendszer **legalább 128 GB egyesített memóriával**.
> - **A BIOS dedikált VRAM (UMA framebuffer) beállítása a minimumra**, hogy a megosztott memóriakészlet a lehető legnagyobb lehessen.
> - A GPU **megosztott memóriakészletének beállítása legalább 110 GB-ra**: futtassa az `amd-ttm --set 110` parancsot (lásd a fenti memóriakonfigurációs lépést), majd indítsa újra a rendszert. Alacsonyabb értékek esetén a modell betöltésekor 126k kontextus mellett memóriahiba léphet fel. Ha a rendszerében kevesebb memória áll rendelkezésre, inkább csökkentse a **Context** értéket a Server Mode-ban.
>
> **Megjegyzés:** Kezdetnek próbálja meg **110 GB**-ra állítani a **GPU megosztott memóriakészletét**. Ha memóriahiba lép fel, növelje a megosztott memóriakészletet, vagy csökkentse a kontextusméretet.

A ds4-cockpit konténeres eszköztárakat használ a ds4 motor futtatásához. Telepítse a `podman`, `distrobox` és `pipx` csomagokat:

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

## Elérhető kvantálások

A ds4 szerzője a DeepSeek V4 Flash több kvantált változatát is biztosítja GGUF formátumban. Az alábbi modellek mindegyike importance matrix (imatrix) kalibrációt használ, amely nagyobb pontosságot őriz meg a modell azon részein, amelyek a leginkább számítanak a kódolási és következtetési feladatok szempontjából.

| Kvantálás | Méret | Leírás |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Egyetlen 128 GB-os csomóponthoz ajánlott |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | A 37–42. rétegeket Q4 pontosságon tartja a jobb pontosság érdekében. Elfér 128 GB-ban, de kevesebb helyet hagy a kontextusnak |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Magasabb minőség. Két Halo csomópontot igényel több csomópontos fürtözésen keresztül |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Opcionális kiegészítő a spekulatív dekódoláshoz, a generálási sebesség javítása érdekében |

Az **IQ2_XXS imatrix** modell jó kiindulópont. Kényelmesen elfér egyetlen csomóponton, és elegendő memóriát hagy egy megfelelő méretű kontextusablakhoz.

## A ds4-cockpit telepítése

A [ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) egy könnyű terminálalapú felhasználói felület, amely megkönnyíti a ds4 elindítását Strix Halo rendszeren. Kezeli az eszköztár-konténerek létrehozását, a modellsúlyok letöltését és a szerverek indítását. Telepítse a `pipx` segítségével:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Indítsa el a cockpitot:
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

## Az eszköztár létrehozása

Az **Interactive Toolboxes** fülön válassza ki a legújabb elérhető/stabil eszköztárat (pl. `ds4-rocm-7.2.4`), majd kattintson a **Create/Update** gombra. Ez letölti a konténerképet, és létrehozza az eszköztár-környezetet.


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

## A modell letöltése

Nyissa meg a **Model Manager** fület. Válassza ki az **IQ2_XXS imatrix (~80.8 GB)** opciót a legördülő listából, majd kattintson a **Download** gombra. A modellfájlok alapértelmezés szerint a `~/ds4` mappába kerülnek mentésre (a tárolási útvonal megváltoztatható).

> **Megjegyzés:** Az IQ2_XXS modell nagyjából 80 GB méretű, ezért a letöltés az internetkapcsolattól függően eltarthat egy ideig. A folyamat befejezése után folytathatja.

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

## A szerver elindítása

Nyissa meg a **Server Mode** fület. Válassza ki a letöltött modellt és az eszköztárat, majd állítsa be a kontextusméretet, a hostot és a portot. Ha készen áll, kattintson a **Start ds4-server** gombra.

> **Tipp:** A `126000` kontextusméret egy elfogadható kiindulási érték, amely egyetlen csomóponton is elférhet — magasabbra állíthatja, ha van elegendő memóriája, vagy alacsonyabbra, ha memóriahibába ütközik. A port (ebben az útmutatóban `8000`) tetszőleges — válasszon egy szabad portot.

> **KV lemez-gyorsítótár (opcionális).** A **KV Disk Cache** bekapcsolásával a KV-gyorsítótár lemezre kerül kihelyezésre (a **Host Cache Dir** helyen, alapértelmezetten `~/.cache/ds4-kv`), így az ismétlődő rendszerprompt-okat SSD-ről állítja vissza a rendszer, ahelyett hogy újraszámolná őket. Ez egy teljesítmény-optimalizálás a hosszú, ismétlődő promptokkal dolgozó kódoló ügynök munkafolyamatokhoz, és **nem szükséges** a szerver futtatásához.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

A szerver elindul, és a 8000-es porton figyel, egy OpenAI-kompatibilis API-végpontot téve elérhetővé a `http://localhost:8000/v1` címen.

**Gyors teszt:**
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

## Webes felület csatlakoztatása

Bármilyen chatfelületet csatlakoztathat, amely támogatja az OpenAI API formátumot. Például a HuggingFace ChatUI használatához:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Nyissa meg a `http://localhost:3000` címet a böngészőjében a beszélgetés megkezdéséhez.
## Kódoló ügynök csatlakoztatása

A ds4 szerver mind az OpenAI, mind az Anthropic-kompatibilis végpontokat biztosítja, így a legtöbb kódoló ügynök közvetlenül csatlakozhat hozzá. Például, hogy hozzáadd a `pi` kódoló ügynökhöz, illeszd be a következő blokkot a `~/.pi/agent/models.json` fájlba:

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

> **Tipp**: Ha a kódoló ügynököd vagy a Web UI egy másik gépen fut, mint a Halo platform, akkor a 8000-es portot SSH-n keresztül továbbítanod kell:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Következő lépések

- **Több csomópontos fürtözés**: Ha két Halo eszközzel rendelkezel, a ds4 támogatja a Q4 modell (~153 GB) elosztását mindkét gép között pipeline párhuzamosítással. A beállítási útmutatóért lásd a [ds4-toolbox dokumentációját](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Spekulatív dekódolás (MTP)**: Töltsd le az MTP súlyokat (~3,6 GB), és add meg a `--mtp` kapcsolót a szervernek a gyorsabb generálási sebesség érdekében.
- **KV gyorsítótár lemezre helyezése**: Kódoló ügynök munkafolyamatokhoz engedélyezd a `--kv-disk-dir` beállítást, hogy az ismétlődő rendszerpromptok SSD-ről álljanak vissza, ahelyett hogy minden alkalommal újraszámolódnának.

További információért lásd a [ds4 tárolót](https://github.com/antirez/ds4) és a [ds4-cockpit toolboxot](https://github.com/kyuz0/strix-halo-ds4-toolbox).