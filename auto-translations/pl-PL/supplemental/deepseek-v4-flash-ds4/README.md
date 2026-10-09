<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Omówienie

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) to zorientowany na wydajność wariant rodziny DeepSeek V4 — model Mixture of Experts liczący 284 miliardy parametrów, z 13 miliardami aktywnych parametrów. Według [raportu technicznego DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) osiąga on 79% w teście SWE-bench Verified oraz 91,6% w LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) to dedykowany silnik wnioskowania zbudowany specjalnie pod tę architekturę modelu. Zamiast ogólnego środowiska uruchomieniowego, ds4 jest ukierunkowany bezpośrednio na rodzinę DeepSeek V4, z optymalizacjami kerneli dedykowanymi dla danej architektury, przeznaczonymi dla oprogramowania AMD ROCm™. Obecnie jest to jedna z najwydajniejszych implementacji DeepSeek V4 Flash na Strix Halo.

Ten samouczek pokazuje, jak za pomocą `ai-toolbox-cockpit`, interfejsu terminalowego, skonfigurować ds4, pobrać wagi modelu i uruchomić lokalne serwowanie DeepSeek V4 Flash na platformie AMD Ryzen™ AI Halo Developer Platform.

## Czego się nauczysz

- Jak zainstalować i uruchomić interfejs terminalowy `ai-toolbox-cockpit`
- Jak utworzyć kontener toolbox ds4 ROCm
- Pobieranie zalecanej kwantyzacji dla pojedynczego węzła Halo
- Uruchamianie serwera wnioskowania ds4 i udostępnianie punktu końcowego kompatybilnego z OpenAI
- Łączenie interfejsu Web UI lub agenta kodującego z lokalnym serwerem

## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->

## Instalowanie wymaganego oprogramowania

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:podman,distrobox,ds4-cockpit,ds4-toolbox-image -->

> **Wymagania systemowe dla tej konfiguracji (pojedynczy węzeł, IQ2_XXS przy kontekście 126k):**
> - System Strix Halo z **co najmniej 128 GB pamięci ujednoliconej (unified memory)**.
> - **Dedykowana pamięć VRAM w BIOS (UMA frame buffer) ustawiona na minimum**, aby pula pamięci współdzielonej mogła być jak największa.
> - **Pula pamięci współdzielonej GPU ustawiona na co najmniej 110 GB**: uruchom `amd-ttm --set 110` (patrz krok konfiguracji pamięci powyżej) i zrestartuj system. Niższe wartości mogą skutkować błędem braku pamięci podczas ładowania modelu przy kontekście 126k. Jeśli Twój system ma mniej dostępnej pamięci, zamiast tego zmniejsz wartość **Context** w trybie serwera.
>
> **Uwaga:** Jako punkt wyjścia spróbuj ustawić **pulę pamięci współdzielonej GPU** na **110 GB**. Jeśli wystąpią błędy braku pamięci, zwiększ pulę pamięci współdzielonej lub zmniejsz rozmiar kontekstu.

ai-toolbox-cockpit wykorzystuje kontenerowe toolboxy do uruchamiania silnika ds4. Zainstaluj `podman`, `distrobox` i `pipx`:

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

## Dostępne kwantyzacje

Autor ds4 udostępnia kilka skwantyzowanych wersji DeepSeek V4 Flash w formacie GGUF. Wszystkie poniższe modele wykorzystują kalibrację macierzy ważności (importance matrix, imatrix), która zachowuje wyższą precyzję dla tych części modelu, które są najważniejsze w zadaniach związanych z kodowaniem i rozumowaniem.

| Kwantyzacja | Rozmiar | Opis |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Zalecana dla pojedynczego węzła 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Utrzymuje warstwy 37–42 w precyzji Q4 dla lepszej dokładności. Mieści się w 128 GB, ale zostawia mniej miejsca na kontekst |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Wyższa jakość. Wymaga dwóch węzłów Halo poprzez klastrowanie wielowęzłowe |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Opcjonalny dodatek do dekodowania spekulacyjnego, poprawiający szybkość generowania |

Model **IQ2_XXS imatrix** to dobry punkt wyjścia. Mieści się bez problemu na pojedynczym węźle i zostawia wystarczająco dużo pamięci na rozsądne okno kontekstowe.

## Instalowanie ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) to lekki interfejs terminalowy ułatwiający instalację różnych backendów AI. Użyjemy go do obsługi tworzenia naszego kontenera ds4, pobierania wag modelu oraz uruchamiania serwerów. Zainstaluj go za pomocą `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Uruchom cockpit:
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

## Krok 1: Tworzenie toolboxa

W zakładce **Interactive Toolboxes** wybierz najnowszy dostępny/stabilny toolbox dla ds4 (np. `ds4-rocm-10.0`) i kliknij **Create/Update**. Spowoduje to pobranie obrazu kontenera i utworzenie środowiska toolbox.


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

## Krok 2: Pobieranie modelu

Przejdź do zakładki **Models**. Najpierw wybierz backend (ds4). Następnie z listy rozwijanej wybierz **IQ2_XXS imatrix (~80.8 GB)** i kliknij **Download**. Pliki modelu zostaną domyślnie zapisane w `~/ds4` (możesz zmienić ścieżkę zapisu).

> **Uwaga:** Model IQ2_XXS waży w przybliżeniu 80 GB, więc pobieranie może zająć sporo czasu w zależności od łącza. Możesz kontynuować po jego zakończeniu.

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

## Krok 3: Uruchamianie serwera

Przejdź do zakładki **Server Mode**. Wybierz pobrany model oraz toolbox, a następnie skonfiguruj rozmiar kontekstu, host i port. Gdy wszystko będzie gotowe, kliknij **Start ds4-server**.

> **Wskazówka** Rozmiar kontekstu `126000` to rozsądna wartość początkowa, która powinna zmieścić się na pojedynczym węźle — możesz ustawić wyższą wartość, jeśli masz zapas pamięci, lub niższą, jeśli napotkasz błędy braku pamięci. Port (`8000` w tym przewodniku) jest dowolny; wybierz dowolny wolny port.

> **Pamięć podręczna KV na dysku (opcjonalnie).** Włączenie opcji **KV Disk Cache** przenosi pamięć podręczną KV na dysk (w lokalizacji **Host Cache Dir**, domyślnie `~/.cache/ds4-kv`), dzięki czemu powtarzające się prompty systemowe są odtwarzane z dysku SSD zamiast obliczane od nowa. To optymalizacja wydajności dla scenariuszy użycia agentów kodujących z długimi, powtarzającymi się promptami i **nie jest wymagana** do uruchomienia serwera.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Serwer uruchomi się i będzie nasłuchiwał na porcie 8000, udostępniając punkt końcowy API kompatybilny z OpenAI pod adresem `http://localhost:8000/v1`.

**Szybki test:**
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
## Podłączanie interfejsu WWW

Możesz podłączyć dowolny interfejs czatu obsługujący format OpenAI API. Na przykład, aby użyć HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Otwórz `http://localhost:3000` w przeglądarce, aby rozpocząć czat.

> **Uwaga:** `--network=host` umieszcza interfejs WWW w sieci hosta, dzięki czemu może on bezpośrednio połączyć się z serwerem ds4 pod adresem `localhost`. Dzięki temu serwer ds4 pozostaje powiązany z interfejsem loopback (nie musi być udostępniany na innych interfejsach).

> **Wskazówka:** Port interfejsu WWW (tutaj `3000`, ustawiany przez `PORT`) jest dowolny — jeśli port `3000` jest już zajęty, wybierz dowolny wolny port i otwórz go w przeglądarce. Upewnij się, że port podany w `OPENAI_BASE_URL` odpowiada portowi, na którym działa Twój serwer ds4.

## Podłączanie agenta kodującego

Serwer ds4 udostępnia zarówno punkty końcowe kompatybilne z OpenAI, jak i z Anthropic, dzięki czemu większość agentów kodujących może połączyć się z nim bezpośrednio. Na przykład, aby dodać go do agenta kodującego `pi`, dodaj poniższy blok do `~/.pi/agent/models.json`:

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

> **Wskazówka**: Jeśli Twój agent kodujący lub interfejs WWW działa na innej maszynie niż platforma Halo, musisz przekierować port serwera (tutaj `8000`) za pomocą SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Kolejne kroki

- **Klastrowanie wielowęzłowe**: Jeśli posiadasz dwa urządzenia Halo, ds4 obsługuje rozdzielanie modelu Q4 (~153 GB) pomiędzy obiema maszynami za pomocą równoległości potokowej. Instrukcje konfiguracji znajdziesz w [dokumentacji ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Dekodowanie spekulacyjne (MTP)**: Pobierz wagi MTP (~3,6 GB) i przekaż `--mtp` do serwera, aby zwiększyć szybkość generowania.
- **Odciążanie pamięci podręcznej KV na dysk**: W przypadku przepływów pracy agentów kodujących włącz `--kv-disk-dir`, aby powtarzające się polecenia systemowe były przywracane z dysku SSD zamiast za każdym razem przeliczane od nowa.

Aby uzyskać więcej informacji, zobacz [repozytorium ds4](https://github.com/antirez/ds4) oraz [zestaw narzędzi ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).