<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Genel Bakış

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), DeepSeek V4 ailesinin verimlilik odaklı varyantıdır — 13 milyar aktif parametreye sahip 284 milyar parametrelik bir Mixture of Experts modelidir. [DeepSeek'in teknik raporuna](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) göre, SWE-bench Verified'da %79 ve LiveCodeBench'te %91,6 puan almaktadır.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4), özellikle bu model mimarisi için oluşturulmuş özel bir çıkarım motorudur. Genel amaçlı bir çalışma zamanı yerine ds4, AMD ROCm™ yazılımı için mimariye özgü çekirdek optimizasyonlarıyla doğrudan DeepSeek V4 ailesini hedefler. Şu anda Strix Halo üzerinde DeepSeek V4 Flash'ın en iyi performans gösteren uygulamalarından biridir.

Bu eğitim, ds4'ü kurmak, model ağırlıklarını indirmek ve AMD Ryzen™ AI Halo Developer Platform üzerinde DeepSeek V4 Flash'ı yerel olarak sunmaya başlamak için bir terminal kullanıcı arayüzü olan `ds4-cockpit`'in nasıl kullanılacağını gösterir.

## Neler Öğreneceksiniz

- `ds4-cockpit` terminal kullanıcı arayüzünün nasıl kurulup başlatılacağı
- ds4 ROCm toolbox konteynerinin nasıl oluşturulacağı
- Tek bir Halo düğümü için önerilen kuantizasyonun indirilmesi
- ds4 çıkarım sunucusunun başlatılması ve OpenAI uyumlu bir uç noktanın açığa çıkarılması
- Bir Web UI veya kodlama ajanının yerel sunucuya bağlanması

## Bellek Yapılandırmasının Ayarlanması

<!-- @require:memory-config -->

## Yazılım Ön Koşullarının Kurulması

> **Bu yapılandırma için sistem gereksinimleri (tek düğümde 126k bağlam ile IQ2_XXS):**
> - **En az 128 GB birleşik belleğe** sahip bir Strix Halo sistemi.
> - Paylaşılan bellek havuzunun mümkün olduğunca büyük olabilmesi için **BIOS'ta ayrılmış VRAM'in (UMA çerçeve arabelleği) minimuma ayarlanması**.
> - GPU **paylaşılan bellek havuzunun en az 110 GB'a ayarlanması**: `amd-ttm --set 110` komutunu çalıştırın (yukarıdaki bellek yapılandırma adımına bakın) ve yeniden başlatın. Daha düşük değerler, model 126k bağlamda yüklenirken bellek yetersizliği hatasına neden olabilir. Sisteminizde daha az bellek varsa, bunun yerine Server Mode'daki **Context** değerini düşürün.
>
> **Not:** Başlangıç noktası olarak **GPU paylaşılan bellek havuzunu** **110 GB**'a ayarlamayı deneyin. Bellek yetersizliği hatalarıyla karşılaşırsanız, paylaşılan bellek havuzunu artırın veya bağlam boyutunu düşürün.

ds4-cockpit, ds4 motorunu çalıştırmak için konteyner toolbox'ları kullanır. `podman`, `distrobox` ve `pipx` yazılımlarını kurun:

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

## Kullanılabilir Kuantizasyonlar

ds4 yazarı, DeepSeek V4 Flash'ın GGUF formatında birkaç kuantize edilmiş sürümünü sunmaktadır. Aşağıdaki modellerin tümü, kodlama ve akıl yürütme görevleri için en önemli model bölümlerinde daha yüksek hassasiyeti koruyan önem matrisi (imatrix) kalibrasyonu kullanır.

| Kuantizasyon | Boyut | Açıklama |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Tek bir 128 GB düğüm için önerilir |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Daha iyi doğruluk için 37–42 katmanlarını Q4 hassasiyetinde tutar. 128 GB'a sığar ancak bağlam için daha az yer bırakır |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Daha yüksek kalite. Çok düğümlü kümeleme yoluyla iki Halo düğümü gerektirir |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Üretim hızını artırmak için spekülatif çözümleme için isteğe bağlı bir eklenti |

**IQ2_XXS imatrix** modeli iyi bir başlangıç noktasıdır. Tek bir düğüme rahatlıkla sığar ve makul bir bağlam penceresi için yeterli bellek bırakır.

## ds4-cockpit'in Kurulması

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox), Strix Halo üzerinde ds4 ile çalışmaya başlamayı kolaylaştıran hafif bir terminal kullanıcı arayüzüdür. Toolbox konteynerlerinin oluşturulmasını, model ağırlıklarının indirilmesini ve sunucuların başlatılmasını yönetir. `pipx` ile kurun:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Cockpit'i başlatın:
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

## Toolbox'ın Oluşturulması

**Interactive Toolboxes** sekmesinde, kullanılabilir en son kararlı toolbox'ı seçin (ör. `ds4-rocm-7.2.4`) ve **Create/Update**'e tıklayın. Bu, konteyner imajını çeker ve toolbox ortamını oluşturur.


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

## Modelin İndirilmesi

**Model Manager** sekmesine gidin. Açılır menüden **IQ2_XXS imatrix (~80,8 GB)** öğesini seçin ve **Download**'a tıklayın. Model dosyaları varsayılan olarak `~/ds4` konumuna kaydedilecektir (depolama yolunu değiştirebilirsiniz).

> **Not:** IQ2_XXS modeli yaklaşık 80 GB'dır, bu nedenle indirme işlemi bağlantınıza bağlı olarak biraz zaman alabilir. İşlem tamamlandığında devam edebilirsiniz.

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

## Sunucunun Başlatılması

**Server Mode** sekmesine gidin. İndirilen modeli ve toolbox'ı seçin, ardından bağlam boyutunu, ana bilgisayarı ve bağlantı noktasını yapılandırın. Hazır olduğunuzda **Start ds4-server**'a tıklayın.

> **İpucu** `126000` bağlam boyutu, tek bir düğüme sığması gereken makul bir başlangıç değeridir — bellek payınız varsa daha yüksek ayarlayabilir veya bellek yetersizliği hatalarıyla karşılaşırsanız düşürebilirsiniz. Bağlantı noktası (bu kılavuzda `8000`) rastgele seçilmiştir; herhangi bir boş bağlantı noktasını seçebilirsiniz.

> **KV Disk Cache (isteğe bağlı).** **KV Disk Cache**'i etkinleştirmek, KV önbelleğini diske (**Host Cache Dir** üzerinde, varsayılan `~/.cache/ds4-kv`) aktarır, böylece tekrarlanan sistem istemleri yeniden hesaplanmak yerine SSD'den geri yüklenir. Bu, uzun ve tekrarlanan istemlere sahip kodlama ajanı iş akışları için bir performans optimizasyonudur ve sunucuyu çalıştırmak için **gerekli değildir**.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Sunucu başlayacak ve 8000 numaralı bağlantı noktasını dinleyecek, `http://localhost:8000/v1` adresinde OpenAI uyumlu bir API uç noktasını açığa çıkaracaktır.

**Hızlı test:**
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

## Bir Web UI'nin Bağlanması

OpenAI API biçimini destekleyen herhangi bir sohbet arayüzüne bağlanabilirsiniz. Örneğin, HuggingFace ChatUI'yi kullanmak için:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Sohbet etmeye başlamak için tarayıcınızda `http://localhost:3000` adresini açın.
## Kodlama Aracısını Bağlama

ds4 sunucusu hem OpenAI hem de Anthropic uyumlu uç noktaları sunar, bu nedenle çoğu kodlama aracısı doğrudan ona bağlanabilir. Örneğin, bunu `pi` kodlama aracısına eklemek için `~/.pi/agent/models.json` dosyasına aşağıdaki bloğu ekleyin:

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

> **İpucu**: Kodlama aracınız veya Web UI'niz Halo platformundan farklı bir makinede çalışıyorsa, 8000 portunu SSH üzerinden yönlendirmeniz gerekir:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Sonraki Adımlar

- **Çok düğümlü kümeleme**: İki Halo cihazınız varsa, ds4, boru hattı paralelliği (pipeline parallelism) aracılığıyla Q4 modelini (~153 GB) her iki makineye dağıtmayı destekler. Kurulum talimatları için [ds4-toolbox belgelerine](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) bakın.
- **Spekülatif kod çözme (MTP)**: MTP ağırlıklarını (~3.6 GB) indirin ve daha hızlı üretim hızı için sunucuya `--mtp` parametresini geçirin.
- **KV önbelleği disk aktarımı**: Kodlama aracısı iş akışları için, tekrar eden sistem istemlerinin her seferinde yeniden hesaplanmak yerine SSD'den geri yüklenmesi için `--kv-disk-dir` seçeneğini etkinleştirin.

Daha fazla bilgi için [ds4 deposuna](https://github.com/antirez/ds4) ve [ds4-cockpit araç setine](https://github.com/kyuz0/strix-halo-ds4-toolbox) bakın.