<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

# Hermes Agent'ı Lemonade Server ile Yerel Olarak Çalıştırma

## Genel Bakış

[**Hermes Agent**](https://hermes-agent.nousresearch.com/), Nous Research tarafından geliştirilen kendi kendini geliştiren bir yapay zeka aracıdır. Yerleşik bir öğrenme döngüsü vardır, deneyimlerden beceriler oluşturur, oturumlar arasında sizinle ilgili kalıcı bir bellek inşa eder ve sizin adınıza zamanlanmış otomasyonlar çalıştırabilir. Basit bir sohbet asistanının aksine, Hermes gerçek eylemler gerçekleştirir: kabuk komutları çalıştırır, dosyalar yazar, web'de gezinir ve paralel iş akışlarını alt aracılara devreder.

[**Lemonade Server**](https://lemonade-server.ai/), bunu güçlendiren yerel çıkarım arka ucudur. GenAI modellerini doğrudan AMD donanımınızda çalıştıran ve bunları sektör standardı OpenAI API'si üzerinden sunan açık kaynaklı bir sunucudur.

Birlikte, tamamen yerel bir yapay zeka aracı yığını oluştururlar: Lemonade, GPU'nuzda model çıkarımını işlerken Hermes, aracı döngüsünü, belleği, becerileri ve mesajlaşma ağ geçidini sağlar.

> **Devam etmeden önce:** Hermes Agent, oldukça özerk bir yapay zeka aracıdır. Herhangi bir yapay zeka aracına sisteminize erişim vermek, öngörülemeyen veya istenmeyen sonuçlara yol açabilir. Yalnızca riskleri anladıysanız ve özerk yazılımın sizin adınıza hareket etmesinden rahatsızlık duymuyorsanız devam edin.

---

## Bu Kılavuzda Neler Öğreneceksiniz

Bu kılavuzun sonunda şunları yapabileceksiniz:

- **Hermes Agent'ı kurmak** ve yapay zeka arka ucu olarak **Lemonade Server**'ı işaret etmek.
- **(Önerilir) Docker/Podman sanal alanını (sandboxing) etkinleştirmek** ve böylece aracının eylemlerini ana bilgisayarınızdan izole etmek.
- **Hermes ağ geçidini başlatmak** ve aracınızın hazır olduğunu doğrulamak.
- **Bir iletişim kanalı (Discord veya Telegram) bağlamak** ve böylece herhangi bir cihazdan aracınızla sohbet edebilmek.

---

<!-- @device:halo_box,halo,stx,krk -->
## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarını Kurma

<!-- @os:linux -->
- `apt-get` ile **Ubuntu 24.04+** veya uyumlu bir Debian tabanlı Linux dağıtımı çalıştıran bir PC
- En az **12 GB RAM** (daha büyük modeller için 64 GB+ önerilir)
- Model ağırlıkları için **~10–30 GB boş disk alanı**
- [Podman](https://podman.io/docs/installation) (İsteğe bağlı, Hermes Agent'ı sanal alana almak için)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- **Windows 10/11** çalıştıran bir PC
- En az **12 GB RAM** (daha büyük modeller için 64 GB+ önerilir)
- Model ağırlıkları için **~10–30 GB boş disk alanı**
- Podman (İsteğe bağlı, Hermes Agent'ı sanal alana almak için). WSL içinde kurun:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman, Halo Box üzerinde önceden kurulu gelir ve herhangi bir kurulum gerektirmez
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Önerilen Modeli İndirme (Pull) ve Yükleme

Bu kılavuz için önerilen model, Unsloth'un **Qwen3.6-35B-A3B-GGUF** modelidir; aracı iş yüklerine oldukça uygun, 263 bin token'lık bağlam penceresine sahip güçlü bir MoE modelidir. Bu model UD-Q4_K_XL nicelemesini kullanır. Şimdi indirin:

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

Modelin varsayılan bağlam uzunluğu 262.144 token'dır. Bellek yetersizliği (OOM) hatalarıyla karşılaşırsanız bağlam penceresini küçültmeyi düşünün.

> **İpucu: Daha hızlı aracı yanıtları için düşünmeyi devre dışı bırakın:** Qwen3.6-35B-A3B, varsayılan olarak düşünme modunda çalışır ve bu, her yanıttan önce gecikme ekler. Aracı döngüleri için bu ek yük hızla birikir. [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) deposu, düşünmeyi devre dışı bırakan hazır bir yapılandırma sunar. Kullanmak için dosyayı indirin ve içe aktarın:
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

### WSL ve Ubuntu'yu Kurma

PowerShell'i Yönetici olarak açın ve WSL çekirdeğini kurun:

```powershell
wsl --install --no-distribution
```

Ardından Ubuntu'yu kurun:

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

WSL'yi yeniden başlatın:

```powershell
wsl --shutdown
wsl
```

### Lemonade'i Windows'tan WSL'ye Köprüleme

WSL2, sanal bir ağ içinde çalışır. Windows üzerindeki Lemonade `127.0.0.1` adresine bağlanır ve WSL buna doğrudan erişemez. Bir Windows port proxy'si, trafiği WSL ağ geçidi IP'sinden Windows localhost'una yönlendirir.

**WSL ağ geçidi IP'nizi bulun** (WSL içinde çalıştırın):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Port proxy'sini ekleyin** (`<WSL-Gateway-IP>` yerine WSL ağ geçidi IP'nizi koyarak PowerShell'de Yönetici olarak çalıştırın):

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

> `netsh portproxy` kuralı yeniden başlatmalardan sonra kalıcı kalır ancak WSL ağ geçidi IP'si `wsl --shutdown` sonrasında değişebilir. Yeniden başlatmadan sonra Lemonade WSL'den erişilemez hale gelirse, güncellenmiş ağ geçidi IP'sini alın ve proxy'yi bu yeni IP ile güncelleyin.

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

## Hermes Agent'ı Kurma

<!-- @os:windows -->
> Aksi belirtilmedikçe bu bölümdeki komutları **WSL terminaliniz** içinde çalıştırın.
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
## Hermes'i Lemonade Kullanacak Şekilde Yapılandırma

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

İstendiğinde:

1. **Custom endpoint (enter URL manually)** seçeneğini seçin
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** WSL ağ geçidi IP'sini kullanın: bunu almak için WSL içinde `ip route show default | awk '{print $3}' | head -1` komutunu çalıştırın, ardından `http://<WSL-Gateway-IP>:13305/api/v1` şeklinde girin
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Otomatik algıla)
5. **Select model:** listeden `Qwen3.6-35B-A3B-GGUF` seçin
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (veya tercih ettiğiniz herhangi bir ad)

`hermes model`, hem etkin model seçimini hem de bağlam uzunluğunu uç noktayla birlikte saklayan adlandırılmış bir `custom_providers` girdisini kaydeder. Sonuç, `~/.hermes/config.yaml` içinde şu şekilde görünür:

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

## (Önerilen) Podman Sandbox'ını Etkinleştirme

Hermes Agent, tüm aracı kabuk ve dosya işlemlerini doğrudan ana bilgisayarınızda çalıştırmak yerine, izole edilmiş bir konteyner üzerinden yönlendirebilir. Bu, herhangi bir istenmeyen eylemin etki alanını sandbox ile sınırlar; böylece ana bilgisayarınızın dosya sistemi ve ağı etkilenmemiş olur.

Hafif bir sandbox imajı oluşturun:

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

Ardından, hafif bir sandbox imajı oluşturun:

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

Ardından, Hermes'i konteyner çalışma zamanı olarak Podman'ı kullanacak şekilde yapılandırın ve terminal arka ucunu ayarlayın:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` hâlâ `docker` olarak kalır.
> `HERMES_DOCKER_BINARY`, Hermes'e çalışma zamanı olarak Docker yerine Podman kullanmasını söyleyen ayardır.

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

Hermes artık kalıcı bir sandbox konteyneri başlatacak ve tüm `terminal` ve dosya aracı çağrılarını bu konteyner üzerinden yönlendirecektir. Konteyner, Hermes sürecinin yaşam döngüsünü paylaşır, tüm araç çağrılarında yeniden kullanılır ve Hermes kapatıldığında yok edilir.

> **Sandbox'ın çalıştığını doğrulayın:** Hermes'i başlatın (`hermes`) ve ondan `run hostname` çalıştırmasını isteyin - makinenizin ana bilgisayar adı yerine kısa bir konteyner kimliği görmelisiniz. Ayrıca ondan `rm -rf <path-to-a-dummy-file/folder>` çalıştırmasını da isteyebilirsiniz: Hermes silme işlemini onaylayacaktır, ancak klasör ana bilgisayarınızda hâlâ duruyor olacaktır. Komut, sizin değil, konteynerin izole edilmiş `$HOME` dizini içinde çalıştı.

> **Daha güçlü izolasyona mı ihtiyacınız var?** Hermes ayrıca, tüm aracı sürecini - ağ geçidi, araçlar ve her şey - bir konteyner içinde çalıştıran resmi bir Docker imajı (`nousresearch/hermes-agent`) sunar. Kurulum ayrıntıları için [Hermes Docker belgelerine](https://hermes-agent.nousresearch.com/docs/user-guide/docker) bakın.

---

<!-- @os:linux -->
## (Önerilen) Hermes'in Firecrawl Hizmetleriyle Entegrasyonu

Hermes, yerleşik web araçlarını kullanarak web sitelerine göz atabilir ve içerik çıkarabilir. Ancak, birçok modern web sitesi bot algılama sistemleri kullanır; bu sistemler basit HTTP isteklerini engeller ve gerçek içerik yerine doğrulama sayfaları döndürür. Bunun sonucunda, Hermes bu sitelerden güvenilir bir şekilde bilgi çıkaramayabilir.

Bu sınırlamanın üstesinden gelmek için, [Firecrawl](https://docs.firecrawl.dev/introduction), bu doğrulamaları aşabilen ve Hermes otomasyonunun tüm potansiyelini ortaya çıkarabilen, kendi kendine barındırılan bir web tarama ve içerik çıkarma hizmeti sunar.

Bu kurulumda, Firecrawl, Podman ile yönetilen bir dizi Docker konteyneri olarak çalışır. Yaşam döngüsü yönetimini ve otomatik başlatmayı basitleştirmek için, Firecrawl'ı, altta yatan Podman Compose yığınını düzenleyen kullanıcı düzeyinde bir `systemd` hizmeti olarak kaydediyoruz. Bu, Hermes'in Firecrawl hizmetini konteynerlerle doğrudan etkileşime girmek yerine standart `systemctl --user` komutlarını kullanarak başlatmasına, durdurmasına ve doğrulamasına olanak tanır.

İşleri basit tutmak için, tüm süreci dört adıma böldük:

---

### 1. Sistem hizmetini kaydedin
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

`default.target.wants/`, otomatik olarak başlatılacak şekilde yapılandırılmış hizmetlere işaret eden sembolik bağlantılar içerir.

### 2. Firecrawl'ı Hizmetiniz İçin Yapılandırma

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md), kazıma ve veri işleme ortamları üzerinde tam kontrole ihtiyaç duyanlar için idealdir; ancak bu, ek bakım ve yapılandırma çabası gerektirir.

Depoyu klonlayarak başlayın:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Kök `/firecrawl` dizininde `.env` dosyası oluşturun:
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
> Özellikle güvenilmeyen ağlardan erişilebilen herhangi bir dağıtımda, `BULL_AUTH_KEY` değerini güçlü bir gizli anahtar olarak ayarlayın.
### 3. Hermes'i Compose Üzerinden Dağıtma

Devam etmeden önce, Hermes Docker imajının en son sürümünü çektiğinizden emin olun:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Bu işlem tamamlandıktan sonra, Hermes Compose dosyasını [hermes-compose.yaml](assets/hermes-compose.yaml) indirin ve kök `/firecrawl` dizinine yerleştirin:

> Bu kural, `systemd`'nin `WorkingDirectory=${HOME}/firecrawl` içinde belirtildiği gibi hizmeti doğru bir şekilde bulup başlatabilmesi için gereklidir.

> İhtiyaç duydukça ek Firecrawl hizmetleri ekleyerek yığını her zaman genişletebilirsiniz. Kullanılabilir hizmetlerin tam listesini resmi [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) dosyasında bulabilirsiniz.

### 4. Hermes Hizmetini Firecrawl Üzerinden Başlatma

Kontrolü `systemd`'ye devretmeden önce, yığını manuel olarak çalıştırarak her şeyin doğru çalıştığını doğrulayın:
```bash
podman compose -f hermes-compose.yaml up -d
```
Her şey doğru yapılandırılmışsa, Hermes konteynerinin ayağa kalktığını görmelisiniz ve komut satırı çıktınız aşağıdakine benzer görünmelidir:
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
[Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints)'ye etkileşimli konteyner içerisinden erişilebilir ve Web Panosu aynı ana bilgisayarda ve portta http://127.0.0.1:9119 adresinde kullanılabilir.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Hizmeti durdurmak için şunu çalıştırın:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

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

Hermes, yapılandırmayı, API anahtarlarını, modelleri, oturumları, belleği ve cron işlerini yönetmek için tarayıcı tabanlı bir arayüz içerir. Ağ geçidi veya CLI çalışırken ikinci bir terminal açın ve şununla başlatın:

```bash
hermes dashboard
```

Bu, yerel bir sunucu başlatır ve tarayıcınızda `http://127.0.0.1:9119` adresini açar. Tam özellik referansı için [pano belgelerine](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) bakın.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## İsteğe Bağlı: Bir İletişim Kanalı Bağlama

Ağ geçidi çalıştığında, yerel ajanınıza herhangi bir cihazdan erişebilirsiniz. Hermes, [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) ve diğerlerini destekler

---

### Discord

Discord, bir bot eklemek için **yönetici erişiminize sahip olduğunuz** bir sunucu gerektirir. Sunucuları paylaşıyor ama sahibi değilseniz, bunun yerine Telegram kullanın.

#### Bir Discord uygulaması ve botu oluşturma

1. [Discord Geliştirici Portalı](https://discord.com/developers/applications)'na gidin ve **New Application** düğmesine tıklayın. Ona bir ad verin (örneğin "hermes-bot").
2. Kenar çubuğunda **Bot**'a tıklayın. Bot için bir kullanıcı adı belirleyin.
3. Yine Bot sayfasında, **Privileged Gateway Intents** bölümüne kaydırın ve şunları etkinleştirin:
   - **Message Content Intent** (gerekli)
   - **Server Members Intent** (önerilir)
4. Yukarı kaydırın ve bot tokeninizi oluşturmak için **Reset Token**'a tıklayın. Kopyalayın.

#### Botu sunucunuza ekleme

1. Kenar çubuğunda **OAuth2 / URL Generator**'a tıklayın.
2. **Scopes** altında, `bot` ve `applications.commands` seçeneklerini etkinleştirin.
3. **Bot Permissions** altında şunları etkinleştirin: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Oluşturulan URL'yi kopyalayın, tarayıcınıza yapıştırın, sunucunuzu seçin ve onaylayın.

#### Kimliklerinizi toplama ve DM'lere izin verme

Discord'da Geliştirici Modunu etkinleştirin (**User Settings / Advanced / Developer Mode**), ardından:
- Sunucu simgenize sağ tıklayın: **Copy Server ID**
- Kendi avatarınıza sağ tıklayın: **Copy User ID**

Sunucu simgenize sağ tıklayın / **Privacy Settings** / **Direct Messages**'ı açın. Bu, eşleştirme adımı için gereklidir.

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

Bot birkaç saniye içinde Discord'da çevrimiçi olmalıdır. Ona bir mesaj gönderin, ister DM ister görebildiği bir kanalda.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Bir Telegram botu oluşturma

1. Telegram'ı açın ve **@BotFather**'a mesaj gönderin.
2. `/newbot` gönderin ve talimatları izleyin. Size verdiği bot tokenini kaydedin.

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

Test etmek için botunuza Telegram'da herhangi bir mesaj gönderin. Artık ajanınızla Telegram DM üzerinden sohbet edebilirsiniz. Webhook modu ve gelişmiş seçenekler için [tam Telegram kurulum kılavuzuna](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) bakın.

---

## Sonraki Adımlar

Artık ajanınız telefonunuzdan komutlar alıp yerel makinenizde işlem yapabildiğine göre, keşfetmeye değer üç yön burada:

1. **Otomatik araştırma özeti**: Hermes'i, her sabah ilgilendiğiniz konular için web'de arama yapacak, bulguları yerel modelinizle özetleyecek ve bir özeti Telegram veya Discord üzerinden telefonunuza gönderecek şekilde zamanlayın, tümü kendi donanımınızda, hiçbir bulut maliyeti olmadan çalışır.

2. **Talep üzerine kod incelemesi**: Hermes'i bir GitHub deposuna yönlendirin, açık pull request'leri incelemesini isteyin ve yorumları veya bir özeti sohbetinize geri göndermesini sağlayın. Docker terminal arka ucuyla, tüm git işlemleri sandbox içinde çalışır ve ana bilgisayarınızı temiz tutar.

3. **Yerel dosya asistanı**: Hermes'e bir çalışma dizinine erişim verin ve telefonunuzdan talep üzerine dosyaları düzenlemesini, yeniden adlandırmasını, özetlemesini veya dönüştürmesini isteyin. Docker terminal arka ucu tüm yazma işlemlerini sandbox çalışma alanıyla sınırlandırdığı için, yanlışlıkla yapılan yıkıcı işlemler kontrol altında tutulur.