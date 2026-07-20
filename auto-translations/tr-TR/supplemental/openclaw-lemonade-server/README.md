<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# OpenClaw'ı Lemonade Server ile Arka Uç Olarak Çalıştırma

## Genel Bakış

[**OpenClaw**](https://openclaw.ai/), kod yazıp çalıştırabilen, dosyaları yönetebilen ve sizin adınıza karmaşık, çok adımlı görevleri yürütebilen özerk bir yapay zeka aracısıdır. Yalnızca soruları yanıtlayan bir sohbet asistanının aksine, OpenClaw sisteminizde gerçek eylemler gerçekleştirir; bu da talepkâr bir aracı döngüsüne ayak uydurabilecek hızlı ve yetkin bir yapay zeka arka ucuna ihtiyaç duyduğu anlamına gelir.

[**Lemonade Server**](https://lemonade-server.ai/) tam olarak bu arka ucu sağlar. GenAI modellerini doğrudan donanımınızda çalıştıran ve bunları endüstri standardı OpenAI API'si üzerinden sunan açık kaynaklı, yerel bir çıkarım (inference) sunucusudur.

Bir araya geldiklerinde, tamamen yerel bir yapay zeka aracısı yığını oluştururlar: Lemonade model çıkarımını üstlenirken, OpenClaw model çıktılarını gerçek eylemlere dönüştüren aracı döngüsünü sağlar.

> **Devam etmeden önce:** OpenClaw, oldukça özerk bir yapay zeka aracısıdır. Herhangi bir yapay zeka aracısına sisteminize erişim vermek, öngörülemeyen veya istenmeyen sonuçlara yol açabilir. Yalnızca riskleri anladıysanız ve özerk yazılımın sizin adınıza hareket etmesinden rahatsanız devam edin.

---

## Bu Rehberde Öğrenecekleriniz

Bu rehberin sonunda şunları yapabileceksiniz:

- **Lemonade Server** hakkında bilgi edinme
- **OpenClaw'ı kurma** ve yapay zeka arka ucu olarak **Lemonade Server'a yönlendirme**.
- **OpenClaw ağ geçidini (gateway) başlatma** ve aracınızın çalışmaya hazır olduğunu doğrulama.
- Aracınızla herhangi bir cihazdan sohbet edebilmek için **bir iletişim kanalı bağlama** (Discord veya Telegram).

---

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Edin

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarını Kurma

<!-- @os:linux -->
- `apt-get` içeren **Ubuntu 24.04+** çalıştıran bir PC veya uyumlu bir Debian tabanlı Linux dağıtımı
- En az **12 GB RAM** (daha büyük modeller için 64 GB+ önerilir)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (İsteğe bağlı, OpenClaw'ı sanal ortamda (sandbox) çalıştırmak için)

- Model ağırlıkları için **~10-30 GB boş disk alanı**
<!-- @os:end -->
<!-- @os:windows -->
- **Windows 10/11** çalıştıran bir PC
- En az **12 GB RAM** (daha büyük modeller için 64 GB+ önerilir)
- Model ağırlıkları için **~10-30 GB boş disk alanı**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (İsteğe bağlı, OpenClaw'ı sanal ortamda (sandbox) çalıştırmak için)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Önerilen Modeli İndirin ve Yükleyin

Bu rehber için önerilen model, Unsloth'tan **Qwen3.6-35B-A3B-GGUF**'dur; aracı iş yüklerine son derece uygun, 263k token bağlam penceresine sahip güçlü bir MoE modelidir. Bu model UD-Q4_K_XL nicemlemesini (quantization) kullanır. Şimdi indirin:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Ardından geniş bir bağlam penceresiyle yükleyin ve bu ayarı sonraki çalıştırmalar için kaydedin:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Modelin varsayılan bağlam uzunluğu 262.144 tokendir. Bellek yetersizliği (OOM) hatalarıyla karşılaşırsanız, bağlam penceresini küçültmeyi düşünebilirsiniz. Ancak Qwen3.6, karmaşık görevler için genişletilmiş bağlamdan yararlandığından, düşünme yeteneklerini korumak amacıyla en az 128K token'lık bir bağlam uzunluğu sürdürmenizi öneririz.

> **İpucu: Daha hızlı aracı yanıtları için düşünmeyi devre dışı bırakın:** Qwen3.6-35B-A3B varsayılan olarak düşünme modunda çalışır; bu da her yanıttan önce gecikme ekler. Aracı döngülerinde bu ek yük hızla birikir. [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) deposu, düşünmeyi devre dışı bırakan hazır bir yapılandırma sunar. Kullanmak için dosyayı indirin ve içe aktarın:
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
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
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
model_id = "${openclaw_model}"

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
  "model": "${openclaw_model}",
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

OpenClaw'ı WSL içinde çalıştırıyoruz (Önerilir) ve Windows üzerinde yerel olarak çalışan Lemonade'e bağlıyoruz. Bu, Lemonade'in GPU hızlandırmasını Windows tarafında korurken, OpenClaw için bir Linux kabuk (shell) ortamı sağlar.

### WSL ve Ubuntu'yu Kurun

PowerShell'i Yönetici olarak açın ve WSL çekirdeğini kurun:

```powershell
wsl --install --no-distribution
```

Ardından Ubuntu'yu kurun:

```powershell
wsl --install -d Ubuntu-24.04
```

### WSL'de systemd'i Etkinleştirin

Bunu Ubuntu terminalinin içinde çalıştırın:

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

### Lemonade'i Windows'tan WSL'ye Köprüleyin

WSL2 sanal bir ağda çalışır. Windows üzerindeki Lemonade `127.0.0.1` adresine bağlanır ve WSL bu adrese doğrudan erişemez. Bir Windows bağlantı noktası vekili (port proxy), trafiği WSL ağ geçidi IP'sinden Windows yerel ana bilgisayarına yönlendirir.

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

Önceki adımda Qwen3.6-35B-A3B-GGUF modelini zaten yüklediyseniz, aşağıdaki gibi bir JSON çıktısı görmelisiniz:

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

> `netsh portproxy` kuralı yeniden başlatmalardan sonra da geçerliliğini korur, ancak `wsl --shutdown` sonrasında WSL ağ geçidi IP'si değişebilir. Yeniden başlatmadan sonra Lemonade'e WSL'den erişilemiyorsa, güncellenmiş ağ geçidi IP'sini alıp vekili bu yeni IP ile güncelleyin.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## OpenClaw'ı Kurma ve Yapılandırma

### OpenClaw'ı Kurun
<!-- @os:windows -->
> Bu bölümdeki komutları **WSL terminaliniz** içinde çalıştırın.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` bayrağı, etkileşimli kurulum sihirbazını atlar; model arka ucunu bir sonraki adımda elle yapılandıracaksınız, bu da hangi model ve sunucunun kullanıldığı üzerinde hassas denetim sağlar.

Yeni bir terminal açın ve kurulumu doğrulayın:

```bash
openclaw --version
```

> **İpucu:** Kurulumdan sonra `command not found` görürseniz, npm'in genel bin dizinini PATH'inize ekleyin:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Bunu kalıcı hale getirmek için yukarıdaki satırı `~/.bashrc` veya `~/.zshrc` dosyanıza ekleyin.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->
### OpenClaw'ı Lemonade Kullanacak Şekilde Yapılandırma

OpenClaw'ın etkileşimsiz katılım (onboarding) sürecini çalıştırın.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

Bu komut, OpenClaw'ın yapılandırmasını `~/.openclaw/openclaw.json` dosyasına yazar.

> **OpenClaw bağlam penceresi boyutlandırması:** OpenClaw'ın sıkıştırma (compaction) işlemi, `contextTokens > contextWindow − reserveTokens` olduğunda tetiklenir. Varsayılan `reserveTokensFloor` değeri 20.000 token'dır; bu, daha düşük olduğunda `reserveTokens` değerini geçersiz kılan bir taban değeridir, dolayısıyla yaklaşık 37 bin token'ın altındaki herhangi bir model bağlamı sonsuz bir sıkıştırma döngüsünü tetikler. Yapılandırmanızda düşük bir rezerv ayarlayıp tabanı bir kez devre dışı bırakırsanız, bu ayar model başına ince ayar gerektirmeden her modele uygulanır:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor`, rezervin kendisi değil, bir *taban* (minimum koruma) değeridir; yalnızca tabanı ayarlamanın bir etkisi olmaz. `reserveTokensFloor: 0`, korumayı devre dışı bırakarak daha düşük `reserveTokens` değerinin kabul edilmesini sağlar.
>
> **Ne zaman uygulanmalı:** Modelinizin etkin bağlam penceresi yaklaşık 37 bin token'ın altındaysa bu yapılandırmayı kullanın; bu durum ister modelin küçük olmasından (örneğin 8k, 16k, 32k) ister kasıtlı olarak daha düşük bir değere sınırlandırılmış olmasından (örneğin 128k'lık bir modeli yükleyip Lemonade'de bağlamı 16k olarak ayarlamaktan) kaynaklansın geçerlidir. Bu ayar yapılmazsa, OpenClaw başlangıçta sonsuz bir sıkıştırma döngüsüne girer.
>
> **Tam bağlamda büyük bağlamlı modeller:** Bunu tamamen atlayabilirsiniz. Varsayılan ayarlar iyi çalışır, sıkıştırma pencere dolmadan önce devreye girer ve modelin uzun yanıtlar üretmesi için yeterli alan bulunur. Yine de uygularsanız, `reserveTokens: 4096` yanıt uzunluğunu yaklaşık 4k token ile sınırlar; bu da uzun dosya oluşturma veya ayrıntılı planların kesilmesine neden olabilir.
>
> **Bunu nereye eklemeli:** `compaction` bloğunu `openclaw.json` dosyanızdaki (genellikle `~/.openclaw/openclaw.json` konumunda) `agents.defaults` içine yerleştirin:
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> Yapılandırmanızın geri kalanı (gateway, kanallar, modeller vb.) değişmeden kalır, yalnızca `compaction` anahtarının eklenmesi gerekir.

### (Önerilir) Docker Sandbox'ı Etkinleştirme

OpenClaw, tüm aracı dosya ve kod işlemlerini doğrudan ana makinenizde çalıştırmak yerine izole bir Docker konteyneri üzerinden yönlendirebilir. Bu, herhangi bir istenmeyen eylemin etki alanını sandbox ile sınırlandırır ve ana makinenizin dosya sistemini ile ağını etkilenmeden bırakır.

Sandbox görüntüsünü bir kez oluşturun (Docker kurulu olmalıdır):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
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

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
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

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

`~/.openclaw/openclaw.json` dosyasındaki mevcut `agents.defaults` bloğunun içine `sandbox` anahtarını eklemek için bunu çalıştırın:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

Sandbox konteynerlerinin varsayılan olarak **ağ erişimi yoktur**. Bağlı bağlantı noktaları (bind mount) ve ağ geçersiz kılmaları için [sandboxing referansına](https://docs.openclaw.ai/gateway/sandboxing) bakın.

> #### Sorun Giderme: Docker İzni Reddedildi
> 
> Docker komutlarını çalıştırırken "permission denied" hatası alıyorsanız:
> 
> **Adım 1: Kullanıcınızı docker grubuna ekleyin**
> 
> ```bash
> sudo groupadd docker                    # Gerekliyse grubu oluşturun
> sudo usermod -aG docker $USER           # Kendinizi gruba ekleyin
> newgrp docker                           # Değişikliği etkinleştirin
> docker run hello-world                  # Test edin
> ```
> 
> **Adım 2: Hata devam ederse kalıcı düzeltmeyi uygulayın**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Ardından sisteminizi **yeniden başlatın**.
> 
> **Hızlı geçici çözüm** (yeniden başlatmadan sonra sıfırlanır):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

### OpenClaw Gateway'i Başlatma

Gateway, aracı döngüsünü yöneten ve paneli (dashboard) sunan OpenClaw sürecidir:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

Paneli açmak için, gateway hâlâ çalışırken bunu ikinci bir terminalde çalıştırın:

```bash
openclaw dashboard
```

Gateway loopback'e bağlandığından, panel aynı makineden açıldığında otomatik olarak kimlik doğrular; yerel erişim için token girişi veya cihaz onayı gerekmez. Etkin arka uç olarak listelenen Lemonade modelinizle birlikte OpenClaw panelini görmelisiniz.

> Sandbox'ı etkinleştirdiyseniz, panelden aracıya `run hostname` çalıştırmasını isteyerek bunu doğrulayabilirsiniz. Makinenizin ana bilgisayar adı yerine kısa bir konteyner kimliği görüyorsanız, sandbox çalışıyor demektir.

**Tebrikler, sıfırdan tamamen yerel bir AI aracı yığını oluşturdunuz.**

> **Gateway token'ı mı gerekiyor?** Panel URL'sini token gömülü olarak yazdırmak için `openclaw dashboard --no-open` komutunu çalıştırın (ayrıca panoya kopyalamayı da dener). Alternatif olarak, token `~/.openclaw/openclaw.json` dosyasında `gateway.auth.token` konumundadır.
>
> **Uzak bir cihazı onaylama:** Paneli ikinci bir makineden veya telefondan açtığınızda, tarayıcı bir istek kimliği (request ID) görüntüler. Gateway'i çalıştıran makineye dönüp şunu çalıştırın:
> ```bash
> openclaw devices approve <requestId>
> ```
> Bu yalnızca uzak veya ikincil cihazlar için gereklidir; aynı makineden loopback erişimi otomatik olarak kimlik doğrular.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## İsteğe Bağlı: Bir İletişim Kanalı Bağlama

Gateway çalışmaya başladığında yerel aracınıza herhangi bir cihazdan erişebilirsiniz. Kurulumunuza uygun seçeneği belirleyin. OpenClaw [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) ve diğer kanalları destekler; tam listeyi [docs.openclaw.ai](https://docs.openclaw.ai) adresinde görebilirsiniz.

---

### Seçenek A: Discord

Discord, bir bot eklemek için **yönetici erişiminize sahip olduğunuz** bir sunucu gerektirir. Sunucuları paylaşıyor ancak birine sahip değilseniz, bunun yerine Seçenek B'yi (Telegram) kullanın.
#### Bir Discord hesabı ve sunucusu oluşturun

Bir Discord hesabınız yoksa [discord.com](https://discord.com) adresinden kaydolun. Ayrıca yönetici olduğunuz bir sunucuya ihtiyacınız var; Discord kenar çubuğundaki **+** simgesine tıklayıp **Create My Own** seçeneğini seçerek bir tane oluşturun. Özel bir sunucu yeterlidir.

#### Bir Discord uygulaması ve botu oluşturun

1. [Discord Developer Portal](https://discord.com/developers/applications) adresine gidin ve **New Application** düğmesine tıklayın. Ona bir isim verin (örneğin "openclaw-bot").
2. Kenar çubuğunda **Bot**'a tıklayın. Bot için bir kullanıcı adı belirleyin.
3. Yine Bot sayfasında, **Privileged Gateway Intents** bölümüne kaydırın ve şunları etkinleştirin:
   - **Message Content Intent** (gerekli)
   - **Server Members Intent** (önerilir)
4. Yukarı geri kaydırın ve bot tokeninizi oluşturmak için **Reset Token**'a tıklayın. Kopyalayın.

#### Botu sunucunuza ekleyin

1. Kenar çubuğunda **OAuth2/ URL Generator**'a tıklayın.
2. **Scopes** altında `bot` ve `applications.commands` seçeneklerini etkinleştirin.
3. **Bot Permissions** altında şunları etkinleştirin: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Oluşturulan URL'yi kopyalayın, tarayıcınıza yapıştırın, sunucunuzu seçin ve onaylayın. Bot artık sunucunuzun üye listesinde görünmelidir.

#### Kimliklerinizi toplayın

Discord'da Geliştirici Modunu etkinleştirin (**User Settings/ Advanced/ Developer Mode**), ardından:
- Sunucu simgenize sağ tıklayın: **Copy Server ID**
- Kendi avatarınıza sağ tıklayın: **Copy User ID**

#### Sunucu üyelerinden gelen DM'lere izin verin

Sunucu simgenize sağ tıklayın/ **Privacy Settings**/ **Direct Messages**'ı açık konuma getirin. Bu, botun size DM göndermesine izin verir; bu, eşleştirme adımı için gereklidir.

#### OpenClaw'ı Discord için yapılandırın

Bot tokeninizi bir ortam değişkeni olarak saklayın, ardından Discord'u etkinleştiren, tokene referans veren ve sunucunuzu izin listesine ekleyen tek bir yama dosyası oluşturun. Yukarıda toplanan kimlikleri kullanarak `<server_id>` ve `<user_id>` yerine kendi değerlerinizi yazın.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **Aracıyı bunu yapılandırması için görevlendirmeye güvenmeyin.** Sandbox etkinleştirildiğinde, aracı sandbox içinden `~/.openclaw/openclaw.json` dosyasına yazamaz; bunun yerine yukarıdaki CLI komutlarını ana makinede kullanın.

Yeni kanal yapılandırmasını almasını sağlamak için gateway'i yeniden başlatın:

```bash
openclaw gateway run --bind loopback --port 18789
```

Birkaç saniye içinde gateway çıktısında `logged in to discord as <bot-name>` ifadesini görmelisiniz.

#### Discord hesabınızı eşleştirin

Discord'da bota DM gönderin. Kısa bir eşleştirme kodu ile yanıt verecektir.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

OpenClaw'ı çalıştıran makinede onaylayın:
```bash
openclaw pairing approve discord <CODE>
```

> Eşleştirme kodları bir saat sonra geçerliliğini yitirir.

Artık doğrudan Discord'dan aracınızla sohbet edebilir ve görevleri yerel donanımınıza aktarabilirsiniz.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Seçenek B: Telegram

Telegram, çoğu kullanıcı için Discord'dan daha basittir; sunucu veya yönetici erişimi gerektirmez.

#### Bir Telegram botu oluşturun

1. Telegram'ı açın ve **@BotFather**'a mesaj gönderin.
2. `/newbot` gönderin ve yönergeleri izleyin. Verdiği bot tokenini kaydedin.

#### OpenClaw'ı Telegram için yapılandırın

Tokeni bir ortam değişkeni olarak saklayın:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Kanal yapılandırmasını `~/.openclaw/openclaw.json` dosyasına ekleyin (veya kontrol panelinden yamalayın):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

Gateway'i yeniden başlatın, ardından Telegram'da botunuza herhangi bir mesaj gönderin. Eşleştirmeyi onaylayın:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Eşleştirme kodları bir saat sonra geçerliliğini yitirir. Artık Telegram DM üzerinden aracınızla sohbet edebilirsiniz.

---

## Sonraki Adımlar

Artık aracınız telefonunuzdan komutlar alıp yerel makinenizde işlem yapabildiğine göre, keşfedilmeye değer üç yön var:

1. **Borsa özetleyici**: OpenClaw'ı sabit bir aralıkta finansal API'lerden veri çekecek, günün hareketlerini yerel modelinizle özetleyecek ve her sabah seçtiğiniz kanal üzerinden telefonunuza bir özet gönderecek şekilde zamanlayın.

2. **İnce ayar izleyicisi**: Telegram veya Discord üzerinden uzaktan bir eğitim işi başlatın, ardından aracının eğitim günlüğünü izlemesini ve periyodik kayıp değerlerini, GPU kullanımını ve disk kullanımını telefonunuza raporlamasını sağlayın. Çalışma durursa veya VRAM ani yükselirse, makinenin başında olmanıza gerek kalmadan hemen haberdar olursunuz.

3. **Yerel bir VLM ile IOT**: Ön kapınıza bir kamera yönlendirin, Lemonade üzerinde bir görü modeli çalıştırın ve OpenClaw'ın kareleri talep üzerine veya bir tetikleyiciyle analiz etmesini sağlayın. Telefonunuzdan "bugün herhangi bir paket geldi mi?" diye sorun ve kendi donanımınızdan doğrudan bir yanıt alın.