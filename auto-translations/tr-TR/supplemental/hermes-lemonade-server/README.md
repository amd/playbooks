<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

# Lemonade Server ile Hermes Agent'ı Yerel Olarak Çalıştırma

## Genel Bakış

[**Hermes Agent**](https://hermes-agent.nousresearch.com/), Nous Research tarafından geliştirilen kendini geliştiren bir yapay zeka ajanıdır. Yerleşik bir öğrenme döngüsüne sahiptir, deneyimlerden beceriler oluşturur, oturumlar arasında sizinle ilgili kalıcı bir hafıza oluşturur ve sizin adınıza zamanlanmış otomasyonlar çalıştırabilir. Basit bir sohbet asistanının aksine, Hermes gerçek eylemler gerçekleştirir: kabuk komutları çalıştırır, dosya yazar, web'de gezinir ve paralel iş akışlarını alt ajanlara devreder.

[**Lemonade Server**](https://lemonade-server.ai/), bunu destekleyen yerel çıkarım arka ucudur. GenAI modellerini doğrudan AMD donanımınızda çalıştıran ve bunları endüstri standardı OpenAI API'si üzerinden sunan açık kaynaklı bir sunucudur.

Birlikte, tamamen yerel bir yapay zeka ajan yığını oluştururlar: Lemonade, GPU'nuzda model çıkarımını yönetir, Hermes ise ajan döngüsünü, hafızayı, becerileri ve mesajlaşma ağ geçidini sağlar.

> **Devam etmeden önce:** Hermes Agent, oldukça özerk bir yapay zeka ajanıdır. Herhangi bir yapay zeka ajanına sisteminize erişim vermek, öngörülemeyen veya istenmeyen sonuçlara yol açabilir. Yalnızca riskleri anlıyorsanız ve özerk yazılımın sizin adınıza hareket etmesinden rahatsız olmuyorsanız devam edin.

---

## Bu Rehberde Neler Öğreneceksiniz

Bu rehberin sonunda şunları yapabileceksiniz:

- **Hermes Agent'ı yükleyip** yapay zeka arka ucu olarak **Lemonade Server**'a yönlendirmek.
- **(Önerilir) Docker/Podman sandbox'lamayı etkinleştirerek** ajanın eylemlerini ana bilgisayarınızdan izole etmek.
- **Hermes ağ geçidini başlatıp** ajanınızın hazır olduğunu doğrulamak.
- **Bir iletişim kanalı bağlayarak** (Discord veya Telegram) ajanınızla herhangi bir cihazdan sohbet etmek.

---

<!-- @device:halo_box,halo,stx,krk -->
## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarını Yükleme

<!-- @os:linux -->
- `apt-get` içeren **Ubuntu 24.04+** veya uyumlu bir Debian tabanlı Linux dağıtımı çalıştıran bir PC
- En az **12 GB RAM** (daha büyük modeller için 64 GB+ önerilir)
- Model ağırlıkları için **~10–30 GB boş disk alanı**
- [Podman](https://podman.io/docs/installation) (İsteğe bağlı, Hermes Agent'ı sandbox'lamak için)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- **Windows 10/11** çalıştıran bir PC
- En az **12 GB RAM** (daha büyük modeller için 64 GB+ önerilir)
- Model ağırlıkları için **~10–30 GB boş disk alanı**
- Podman (İsteğe bağlı, Hermes Agent'ı sandbox'lamak için). WSL içinde yükleyin:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman, Halo Box üzerinde önceden yüklüdür ve herhangi bir kurulum gerekmez
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:hermes,lemonade-models-qwen3-35b-a3b,lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Önerilen Modeli İndirin ve Yükleyin

Bu rehber için önerilen model, Unsloth'tan **Qwen3.6-35B-A3B-GGUF**'tur; ajan iş yüklerine oldukça uygun, 263k token'lık bağlam penceresine sahip güçlü bir MoE modelidir. Bu model UD-Q4_K_XL niceleme (quantization) kullanır. Şimdi indirin:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Ardından geniş bir bağlam penceresiyle yükleyin ve bu ayarı gelecekteki çalıştırmalar için kaydedin:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Model, varsayılan olarak 262.144 token'lık bir bağlam uzunluğuna sahiptir. Bellek yetersizliği (OOM) hatalarıyla karşılaşırsanız bağlam penceresini küçültmeyi düşünün.

> **İpucu: Daha hızlı ajan yanıtları için düşünmeyi devre dışı bırakın:** Qwen3.6-35B-A3B, varsayılan olarak düşünme (thinking) modunda çalışır; bu da her yanıttan önce gecikme ekler. Ajan döngüleri için bu ek yük hızla birikir. [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) deposu, düşünmeyi devre dışı bırakan hazır bir yapılandırma sunar. Kullanmak için dosyayı indirin ve içe aktarın:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"

python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
model_id = "${hermes_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${hermes_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

## WSL Kurulumu

Hermes Agent'ı WSL içinde çalıştırıyor ve Windows üzerinde yerel olarak çalışan Lemonade'e bağlıyoruz. Bu, Lemonade'in GPU hızlandırmasını Windows tarafında tutarken Hermes için bir Linux kabuk ortamı sağlar.

### WSL ve Ubuntu'yu Yükleme

PowerShell'i Yönetici olarak açın ve WSL çekirdeğini yükleyin:

```powershell
wsl --install --no-distribution
```

Ardından Ubuntu'yu yükleyin:

```powershell
wsl --install -d Ubuntu-24.04
```

### WSL'de systemd'yi Etkinleştirme

Bunu Ubuntu terminali içinde çalıştırın:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

WSL'i yeniden başlatın:

```powershell
wsl --shutdown
wsl
```

### Lemonade'i Windows'tan WSL'e Köprüleme

WSL2, sanal bir ağda çalışır. Windows üzerindeki Lemonade, `127.0.0.1`'e bağlanır; WSL buna doğrudan erişemez. Bir Windows bağlantı noktası vekili (port proxy), WSL ağ geçidi IP'sinden Windows localhost'una trafiği yönlendirir.

**WSL ağ geçidi IP'nizi bulun** (WSL içinde çalıştırın):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Bağlantı noktası vekilini ekleyin** (Yönetici olarak PowerShell'de çalıştırın, `<WSL-Gateway-IP>` yerine WSL ağ geçidi IP'nizi yazın):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Bir güvenlik duvarı kuralı ekleyin** (aynı yükseltilmiş PowerShell'de):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**WSL'den doğrulayın**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Önceki adımda Qwen3.6-35B-A3B-GGUF modelini zaten yüklediyseniz, yüklü modelinizi listeleyen JSON çıktısını görmelisiniz.

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

> `netsh portproxy` kuralı yeniden başlatmalarda kalıcıdır, ancak `wsl --shutdown` sonrasında WSL ağ geçidi IP'si değişebilir. Yeniden başlatmanın ardından Lemonade'e WSL'den erişilemezse, güncellenmiş ağ geçidi IP'sini alın ve vekili bu yeni IP ile güncelleyin.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->

---
<!-- @os:end -->

## Hermes Agent'ı Yükleme

<!-- @os:windows -->
> Aksi belirtilmedikçe bu bölümdeki komutları **WSL terminalinizde** çalıştırın.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

`--skip-setup` bayrağı, etkileşimli kurulum sihirbazını atlar; böylece model arka ucunu bir sonraki adımda manuel olarak yapılandırabilirsiniz.

Kabuğunuzu yeniden yükleyin:

```bash
source ~/.bashrc
```

Kurulumu doğrulayın:

```bash
hermes --version
```

Tüm bağımlılıkları kontrol etmek için bir kendi kendine tanılama çalıştırın:

```bash
hermes doctor
```

> **İpucu:** Kurulumdan sonra `command not found` görürseniz, Hermes'i PATH'inize ekleyin:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Bunu kalıcı hale getirmek için yukarıdaki satırı `~/.bashrc` veya `~/.zshrc` dosyanıza ekleyin.

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## Hermes'in Lemonade Kullanacak Şekilde Yapılandırılması

Hermes, model yapılandırmasını `~/.hermes/config.yaml` dosyasında saklar. Etkileşimli `hermes model` seçicisini kullanabilir veya yapılandırmayı doğrudan yazabilirsiniz.

### Seçenek 1: Etkileşimli seçici

<!-- @os:windows -->
> Aşağıdaki komutu **WSL terminalinizin** içinde çalıştırın.
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

Sorulduğunda:

1. **Custom endpoint (enter URL manually)** seçeneğini seçin
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** WSL ağ geçidi IP'sini kullanın: bunu almak için WSL içinde `ip route show default | awk '{print $3}' | head -1` komutunu çalıştırın, ardından `http://<WSL-Gateway-IP>:13305/api/v1` girin
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Otomatik algıla)
5. **Select model:** listeden `Qwen3.6-35B-A3B-GGUF` seçin
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (veya tercih ettiğiniz herhangi bir ad)

`hermes model`, hem etkin model seçimini hem de bağlam uzunluğunu uç nokta ile birlikte saklayan adlandırılmış bir `custom_providers` girişini kaydeder. `~/.hermes/config.yaml` dosyasındaki sonuç şu şekilde görünür:

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### Seçenek 2: Yapılandırmayı doğrudan yazma

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

WSL terminalinizin içinde, Windows ana bilgisayar IP'sini alın ve yapılandırmayı yazın:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## (Önerilir) Podman Kum Havuzu (Sandboxing) Özelliğinin Etkinleştirilmesi

Hermes Agent, tüm aracı kabuk ve dosya işlemlerini doğrudan ana bilgisayarınızda çalıştırmak yerine izole bir konteyner üzerinden yönlendirebilir. Bu, istenmeyen herhangi bir eylemin etki alanını kum havuzuyla sınırlandırır ve ana bilgisayarınızın dosya sistemini ile ağını etkilenmemiş bırakır.

Hafif bir kum havuzu imajı oluşturun:

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
WSL terminalinize girin:

```powershell
wsl -d Ubuntu-24.04
```

Ardından, hafif bir kum havuzu imajı oluşturun:

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Ardından Hermes'i konteyner çalışma zamanı olarak Podman kullanacak şekilde yapılandırın ve terminal arka ucunu ayarlayın:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` hâlâ `docker` olarak kalır.
> `HERMES_DOCKER_BINARY`, Hermes'e çalışma zamanı olarak Podman kullanmasını söyleyen değişkendir.

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Hermes artık kalıcı bir kum havuzu konteyneri başlatacak ve tüm `terminal` ile dosya aracı çağrılarını bu konteyner üzerinden yönlendirecektir. Konteyner, Hermes sürecinin yaşam döngüsünü paylaşır, tüm araç çağrıları arasında yeniden kullanılır ve Hermes sonlandığında yok edilir.

> **Kum havuzunun çalıştığını doğrulayın:** Hermes'i başlatın (`hermes`) ve ona `run hostname` çalıştırmasını isteyin - makinenizin ana bilgisayar adı yerine kısa bir konteyner kimliği görmelisiniz. Ayrıca ona `rm -rf <path-to-a-dummy-file/folder>` komutunu çalıştırmasını da isteyebilirsiniz: Hermes silme işlemini onaylayacaktır, ancak klasör ana bilgisayarınızda hâlâ duruyor olacaktır. Komut, sizin `$HOME` dizininizde değil, konteynerin izole `$HOME` dizininde çalıştırılmıştır.

> **Daha güçlü izolasyon mu gerekiyor?** Hermes ayrıca, tüm aracı sürecini bir konteyner içinde çalıştıran resmi bir Docker imajı (`nousresearch/hermes-agent`) da sunar - ağ geçidi, araçlar ve her şey dahil. Kurulum ayrıntıları için [Hermes Docker belgelerine](https://hermes-agent.nousresearch.com/docs/user-guide/docker) bakın.

---

<!-- @os:linux -->
## (Önerilir) Hermes'in Firecrawl Hizmetleriyle Entegrasyonu

Hermes, yerleşik web araçlarını kullanarak web sitelerine göz atabilir ve içerik çıkarabilir. Ancak, birçok modern web sitesi bot tespit sistemleri kullanır; bu sistemler basit HTTP isteklerini engeller ve gerçek içerik yerine zorlayıcı (challenge) sayfalar döndürür. Sonuç olarak, Hermes bu sitelerden bilgi çıkarmayı güvenilir bir şekilde başaramayabilir.

Bu sınırlamanın üstesinden gelmek için, [Firecrawl](https://docs.firecrawl.dev/introduction) bu zorlukları aşabilen ve Hermes otomasyonunun tam potansiyelini açığa çıkarabilen, kendi kendine barındırılan (self-hosted) bir web tarama ve içerik çıkarma hizmeti sunar.

Bu kurulumda, Firecrawl, Podman ile yönetilen bir dizi Docker konteyneri olarak çalışır. Yaşam döngüsü yönetimini ve otomatik başlatmayı basitleştirmek için, Firecrawl'ı, alttaki Podman Compose yığınını düzenleyen kullanıcı düzeyinde bir `systemd` hizmeti olarak kaydediyoruz. Bu, Hermes'in konteynerlerle doğrudan etkileşime girmek yerine standart `systemctl --user` komutlarını kullanarak Firecrawl hizmetini başlatmasına, durdurmasına ve doğrulamasına olanak tanır.

İşleri basit tutmak için, tüm süreci dört adıma ayırdık:

---

### 1. Sistem hizmetinin kaydedilmesi
systemd kullanıcı yapılandırma dizinine gidin:
```bash
cd ~/.config/systemd/user
```
`firecrawl.service` adlı yeni bir dosya oluşturun ve açın.
```bash
nano firecrawl.service
```
Aşağıdaki yapılandırmayı kopyalayıp yapıştırın:
```bash
[Unit]
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
Bu noktada, hizmet tanımlanmış ancak henüz `systemd` ile kaydedilmemiştir.
Dosya adının yukarıda oluşturduğunuzla tam olarak eşleştiğinden emin olun, ardından şunu çalıştırın:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Başarılı olursa, aşağıdaki çıktıyı görmelisiniz:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/`, otomatik olarak başlatılacak şekilde yapılandırılmış hizmetlere yönelik sembolik bağlantılar içerir.

### 2. Hizmetiniz İçin Firecrawl'ın Yapılandırılması

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md), kazıma (scraping) ve veri işleme ortamları üzerinde tam kontrole ihtiyaç duyanlar için idealdir, ancak bunun karşılığında ek bakım ve yapılandırma çabası gerektirir.

Depoyu klonlayarak başlayın:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Kök `/firecrawl` dizininde `.env` dosyasını oluşturun:
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> `BULL_AUTH_KEY` değerini, özellikle güvenilir olmayan ağlardan erişilebilen herhangi bir dağıtımda, güçlü bir gizli anahtar olarak ayarlayın.
### 3. Hermes'in Compose ile Dağıtılması

Devam etmeden önce en son Hermes Docker imajını çektiğinizden emin olun:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Bu işlem tamamlandıktan sonra Hermes Compose dosyasını [hermes-compose.yaml](assets/hermes-compose.yaml) indirin ve `/firecrawl` kök dizinine yerleştirin:

> Bu kural, `systemd`'nin hizmeti `WorkingDirectory=${HOME}/firecrawl` içinde belirtildiği gibi bulup başlatabilmesi için gereklidir.

> Yığını gerektiğinde ek Firecrawl hizmetleri ekleyerek her zaman genişletebilirsiniz. Kullanılabilir hizmetlerin tam listesine resmi [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) dosyasından ulaşabilirsiniz.

### 4. Firecrawl Üzerinden Hermes Hizmetini Başlatma 

Kontrolü `systemd`'ye devretmeden önce, yığını manuel olarak çalıştırarak her şeyin doğru çalıştığını doğrulayın:
```bash
podman compose -f hermes-compose.yaml up -d
```
Her şey doğru yapılandırılmışsa, Hermes konteynerinin ayağa kalktığını görmelisiniz ve komut satırı çıktınız şuna benzer olmalıdır:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Doğruladıktan sonra, devam etmeden önce yığını tekrar kapatın:
```bash
podman compose -f hermes-compose.yaml down
```
Artık her şey doğrulandığına göre, hizmeti `systemd` üzerinden başlatın:
```bash
systemctl --user start firecrawl.service
```
[Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) etkileşimli konteyner içinden erişilebilir durumdadır ve Web Panosu aynı ana bilgisayar ve bağlantı noktasında http://127.0.0.1:9119 adresinde kullanılabilir.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Hizmeti durdurmak için şunu çalıştırın:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native (Yerel)

Doğrudan etkileşimli bir CLI oturumu başlatın: 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**Tebrikler, tamamen yerel bir AI ajan yığını oluşturdunuz.**

### Web Panosu

Hermes, yapılandırmayı, API anahtarlarını, modelleri, oturumları, belleği ve zamanlanmış görevleri yönetmek için tarayıcı tabanlı bir arayüz içerir. Ağ geçidi veya CLI çalışırken ikinci bir terminal açın ve aşağıdaki komutla başlatın:

```bash
hermes dashboard
```

Bu komut yerel bir sunucu başlatır ve tarayıcınızda `http://127.0.0.1:9119` adresini açar. Tüm özellik referansı için [pano belgelerine](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) bakın.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## İsteğe Bağlı: Bir İletişim Kanalı Bağlama

Ağ geçidi çalıştıktan sonra yerel ajanınıza herhangi bir cihazdan ulaşabilirsiniz. Hermes [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) ve diğerlerini destekler

---

### Discord

Discord, bir bot eklemek için **yönetici erişiminiz olan** bir sunucu gerektirir. Sunucuları paylaşıyor ancak sahibi değilseniz, bunun yerine Telegram kullanın.

#### Bir Discord uygulaması ve botu oluşturma

1. [Discord Geliştirici Portalı](https://discord.com/developers/applications)'na gidin ve **New Application** öğesine tıklayın. Bir ad verin (örneğin "hermes-bot").
2. Yan menüde **Bot** öğesine tıklayın. Bot için bir kullanıcı adı belirleyin.
3. Hâlâ Bot sayfasındayken **Privileged Gateway Intents** bölümüne kaydırın ve şunları etkinleştirin:
   - **Message Content Intent** (gerekli)
   - **Server Members Intent** (önerilir)
4. Yukarı kaydırın ve bot tokeninizi oluşturmak için **Reset Token** öğesine tıklayın. Kopyalayın.

#### Botu sunucunuza ekleme

1. Yan menüde **OAuth2 / URL Generator** öğesine tıklayın.
2. **Scopes** altında `bot` ve `applications.commands` seçeneklerini etkinleştirin.
3. **Bot Permissions** altında şunları etkinleştirin: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Oluşturulan URL'yi kopyalayın, tarayıcınıza yapıştırın, sunucunuzu seçin ve onaylayın.

#### Kimliklerinizi toplama ve DM'lere izin verme

Discord'da Geliştirici Modunu etkinleştirin (**User Settings / Advanced / Developer Mode**), ardından:
- Sunucu simgenize sağ tıklayın: **Copy Server ID**
- Kendi avatarınıza sağ tıklayın: **Copy User ID**

Sunucu simgenize sağ tıklayın / **Privacy Settings** / **Direct Messages** seçeneğini açık hale getirin. Bu, eşleştirme adımı için gereklidir.

#### Hermes'i Discord için yapılandırma

Aşağıdakini `~/.hermes/.env` dosyasına ekleyin:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Ardından ağ geçidini başlatın:

```bash
hermes gateway
```

Bot birkaç saniye içinde Discord'da çevrimiçi olmalıdır. Ona bir mesaj gönderin, ister bir DM ister görebildiği bir kanal üzerinden.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Bir Telegram botu oluşturma

1. Telegram'ı açın ve **@BotFather**'a mesaj gönderin.
2. `/newbot` komutunu gönderin ve yönergeleri izleyin. Size verilen bot tokenini kaydedin.

#### Hermes'i Telegram için yapılandırma

Aşağıdakini `~/.hermes/.env` dosyasına ekleyin:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Telegram kullanıcı kimliğinizi bilmiyor musunuz?** Telegram'da [@userinfobot](https://t.me/userinfobot)'a mesaj gönderin, size sayısal kimliğinizle yanıt verecektir.

Ardından ağ geçidini başlatın:

```bash
hermes gateway
```

Test etmek için botunuza Telegram üzerinden herhangi bir mesaj gönderin. Artık ajanınızla Telegram DM üzerinden sohbet edebilirsiniz. Webhook modu ve gelişmiş seçenekler için [tam Telegram kurulum kılavuzuna](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) bakın.

---

## Sonraki Adımlar

Artık ajanınız telefonunuzdan komut alıp yerel makinenizde işlem yapabildiğine göre, keşfedilmeye değer üç yön şunlardır:

1. **Otomatik araştırma özeti**: Hermes'i her sabah ilgilendiğiniz konular için webde arama yapacak, bulguları yerel modelinizle özetleyecek ve bir özeti Telegram veya Discord aracılığıyla telefonunuza gönderecek şekilde zamanlayın, tüm bunlar bulut maliyeti olmadan kendi donanımınızda çalışır.

2. **Talep üzerine kod incelemesi**: Hermes'i bir GitHub deposuna yönlendirin, açık pull request'leri incelemesini isteyin ve sohbetinize bir yorum veya özet göndermesini sağlayın. Docker terminal arka ucuyla, tüm git işlemleri sandbox içinde çalışır ve ana makinenizi temiz tutar.

3. **Yerel dosya asistanı**: Hermes'e bir çalışma dizinine erişim verin ve telefonunuzdan talep üzerine dosyaları düzenlemesini, yeniden adlandırmasını, özetlemesini veya dönüştürmesini isteyin. Docker terminal arka ucu tüm yazma işlemlerini sandbox çalışma alanıyla sınırlandırdığından, kazara yıkıcı işlemler kontrol altında tutulur.