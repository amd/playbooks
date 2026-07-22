<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizceden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Hatalar içerebilir ve bazı adımlar, komutlar, indirmeler veya ürün kullanılabilirliği dilinize veya bölgenize göre farklılık gösterebilir. Yanlış görünen bir şey varsa, orijinal İngilizce playbook'u kaynak olarak kabul edin.
<!-- auto-translated-disclaimer:end -->

# Run OpenClaw with Lemonade Server as the backend

## Overview

[**OpenClaw**](https://openclaw.ai/), sizin adınıza kod yazıp çalıştırabilen, dosyaları yönetebilen ve karmaşık, çok adımlı görevler üzerinde çalışabilen özerk bir yapay zeka ajanıdır. Sadece soruları yanıtlayan bir sohbet asistanının aksine, OpenClaw sisteminiz üzerinde gerçek eylemler gerçekleştirir; bu da talepkâr bir ajan döngüsüne ayak uydurabilecek hızlı ve yetenekli bir yapay zeka arka ucuna ihtiyaç duyduğu anlamına gelir.

[**Lemonade Server**](https://lemonade-server.ai/) işte bu arka uçtur. GenAI modellerini doğrudan donanımınızda çalıştıran ve bunları endüstri standardı OpenAI API'si üzerinden sunan açık kaynaklı, yerel bir çıkarım sunucusudur.

Birlikte, tamamen yerel bir yapay zeka ajan yığını oluştururlar: Lemonade model çıkarımını yönetir, OpenClaw ise model çıktılarını gerçek eylemlere dönüştüren ajan döngüsünü sağlar.

> **Devam etmeden önce:** OpenClaw son derece özerk bir yapay zeka ajanıdır. Herhangi bir yapay zeka ajanına sisteminize erişim vermek, öngörülemeyen veya istenmeyen sonuçlara yol açabilir. Yalnızca riskleri anladıysanız ve sizin adınıza hareket eden özerk yazılımlarla ilgili rahatsanız devam edin.

---

## Bu Rehberde Neler Öğreneceksiniz

Bu rehberin sonunda şunları yapabileceksiniz:

- **Lemonade Server** hakkında bilgi edinme
- **OpenClaw'ı kurma** ve yapay zeka arka ucu olarak **Lemonade Server'a yönlendirme**.
- **OpenClaw ağ geçidini başlatma** ve ajanınızın çalışmaya hazır olduğunu doğrulama.
- Herhangi bir cihazdan ajanınızla sohbet edebilmeniz için bir **iletişim kanalı bağlama** (Discord veya Telegram).

---

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Edin

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarının Kurulumu

<!-- @os:linux -->
- `apt-get` ile **Ubuntu 24.04+** veya uyumlu bir Debian tabanlı Linux dağıtımı çalıştıran bir bilgisayar
- En az **12 GB RAM** (daha büyük modeller için 64 GB+ önerilir)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (İsteğe bağlı, OpenClaw'ı korumalı alanda çalıştırmak için)

- Model ağırlıkları için **~10–30 GB boş disk alanı**
<!-- @os:end -->
<!-- @os:windows -->
- **Windows 10/11** çalıştıran bir bilgisayar
- En az **12 GB RAM** (daha büyük modeller için 64 GB+ önerilir)
- Model ağırlıkları için **~10–30 GB boş disk alanı**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (İsteğe bağlı, OpenClaw'ı korumalı alanda çalıştırmak için)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Önerilen Modeli Çekin ve Yükleyin

Bu rehber için önerilen model, ajan iş yükleri için son derece uygun, 263k belirteçlik bağlam penceresine sahip güçlü bir MoE modeli olan Unsloth'un **Qwen3.6-35B-A3B-GGUF** modelidir. Bu model UD-Q4_K_XL nicelemesini kullanır. Şimdi çekin:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Ardından büyük bir bağlam penceresiyle yükleyin ve bu ayarı sonraki çalıştırmalar için kaydedin:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Modelin varsayılan bağlam uzunluğu 262.144 belirteçtir. Bellek yetersizliği (OOM) hatalarıyla karşılaşırsanız bağlam penceresini küçültmeyi düşünebilirsiniz. Ancak Qwen3.6, karmaşık görevler için genişletilmiş bağlamdan yararlandığından, düşünme yeteneklerini korumak amacıyla bağlam uzunluğunu en az 128K belirteç olarak tutmanızı öneririz.

> **İpucu: Daha hızlı ajan yanıtları için düşünmeyi devre dışı bırakın:** Qwen3.6-35B-A3B varsayılan olarak düşünme modunda çalışır ve bu, her yanıttan önce gecikme ekler. Ajan döngülerinde bu ek yük hızla birikir. [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) deposu, düşünmeyi devre dışı bırakan hazır bir yapılandırma sunar. Bunu kullanmak için dosyayı indirin ve içe aktarın:
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

OpenClaw'ı WSL içinde çalıştırırız (Önerilen) ve bunu Windows üzerinde yerel olarak çalışan Lemonade'e bağlarız. Bu, Lemonade'in GPU hızlandırmasını Windows tarafında tutarken OpenClaw için bir Linux kabuk ortamı sağlar.

### WSL ve Ubuntu'yu Kurun

PowerShell'i Yönetici olarak açın ve WSL çekirdeğini kurun:

```powershell
wsl --install --no-distribution
```

Ardından Ubuntu'yu kurun:

```powershell
wsl --install -d Ubuntu-24.04
```

### WSL'de systemd'yi Etkinleştirin

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

WSL2 sanal bir ağda çalışır. Windows üzerindeki Lemonade `127.0.0.1` adresine bağlanır ve WSL bu adrese doğrudan erişemez. Bir Windows bağlantı noktası proxy'si, trafiği WSL ağ geçidi IP'sinden Windows localhost'a yönlendirir.

**WSL ağ geçidi IP'nizi bulun** (WSL içinde çalıştırın):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Bağlantı noktası proxy'sini ekleyin** (Yönetici olarak PowerShell'de çalıştırın, `<WSL-Gateway-IP>` yerine WSL ağ geçidi IP'nizi yazın):

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

Bir önceki adımda Qwen3.6-35B-A3B-GGUF modelini zaten yüklediyseniz, aşağıdaki gibi bir JSON çıktısı görmelisiniz:

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

> `netsh portproxy` kuralı yeniden başlatmalardan sonra kalıcı olarak korunur, ancak WSL ağ geçidi IP'si `wsl --shutdown` sonrasında değişebilir. Yeniden başlatmadan sonra Lemonade'e WSL'den erişilemez hale gelirse, güncellenmiş ağ geçidi IP'sini alın ve proxy'yi bu yeni IP ile güncelleyin.

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

## OpenClaw'ı Kurun ve Yapılandırın

### OpenClaw'ı Kurun
<!-- @os:windows -->
> Bu bölümdeki komutları **WSL terminalinizin** içinde çalıştırın.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` bayrağı, etkileşimli kurulum sihirbazını atlar; model arka ucunu bir sonraki adımda manuel olarak yapılandıracaksınız, bu da hangi model ve sunucunun kullanıldığı üzerinde hassas bir kontrol sağlar.

Yeni bir terminal açın ve kurulumu doğrulayın:

```bash
openclaw --version
```

> **İpucu:** Kurulumdan sonra `command not found` görürseniz, npm'in global bin dizinini PATH'inize ekleyin:
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

OpenClaw'ın etkileşimli olmayan (non-interactive) katılım işlemini çalıştırın.
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

> **OpenClaw bağlam penceresi boyutlandırması:** OpenClaw'ın sıkıştırma (compaction) işlemi, `contextTokens > contextWindow − reserveTokens` olduğunda tetiklenir. Varsayılan `reserveTokensFloor` değeri 20.000 token'dır; bu değer daha düşük olduğunda `reserveTokens` değerinin önüne geçen bir alt sınırdır (floor), bu nedenle ~37k'nin altındaki herhangi bir model bağlamı sonsuz bir sıkıştırma döngüsünü tetikler. Yapılandırmanızda düşük bir rezerv ayarlayıp bu alt sınırı bir kez devre dışı bırakırsanız, bu ayar her model için geçerli olur; model başına ayarlama yapmaya gerek kalmaz:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor`, rezervin kendisi değil bir *alt sınırdır* (minimum koruma); yalnızca bu alt sınırı ayarlamanın bir etkisi olmaz. `reserveTokensFloor: 0`, korumayı devre dışı bırakır ve böylece daha düşük olan `reserveTokens` değeri kabul edilir.
>
> **Ne zaman uygulanmalı:** Modelinizin etkin bağlam penceresi ~37k'nin altındaysa (model küçük olduğu için, örneğin 8k, 16k, 32k, veya bilinçli olarak daha düşük bir değere sınırladığınız için, örneğin Lemonade'de 128k'lık bir modeli yükleyip bağlamı 16k olarak ayarladığınız için) bu yapılandırmayı kullanın. Bu yapılmazsa, OpenClaw başlangıçta sonsuz bir sıkıştırma döngüsüne girer.
>
> **Tam bağlamda büyük bağlamlı modeller:** Bunu tamamen atlayabilirsiniz. Varsayılan ayarlar iyi çalışır; sıkıştırma, pencere dolmadan önce iyi bir noktada devreye girer ve modelin uzun yanıtlar üretmesi için yeterli alan olur. Yine de uygularsanız, `reserveTokens: 4096` ayarının yanıt uzunluğunu ~4k token ile sınırladığını unutmayın; bu da uzun dosya oluşturmayı veya ayrıntılı planları kesebilir.
>
> **Nereye eklenmeli:** `compaction` bloğunu, `openclaw.json` dosyanızdaki (genellikle `~/.openclaw/openclaw.json` konumunda) `agents.defaults` içine yerleştirin:
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
> Yapılandırmanızın geri kalanı (gateway, channels, models vb.) değişmeden kalır; yalnızca `compaction` anahtarının eklenmesi yeterlidir.

### (Önerilir) Docker Sandboxing'i Etkinleştirme

OpenClaw, tüm ajan dosya ve kod işlemlerini doğrudan ana makinenizde çalıştırmak yerine, izole bir Docker konteyneri üzerinden yönlendirebilir. Bu, herhangi bir istenmeyen işlemin etki alanını sandbox ile sınırlandırır ve ana makinenizin dosya sistemini ve ağını etkilenmeden bırakır.

Sandbox görüntüsünü (image) bir kez oluşturun (Docker'ın kurulu olması gerekir):

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

`~/.openclaw/openclaw.json` içindeki mevcut `agents.defaults` bloğuna `sandbox` anahtarını eklemek için bunu çalıştırın:

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

Sandbox konteynerlerinin varsayılan olarak **ağ erişimi yoktur**. Bağlama (bind) noktaları ve ağ geçersiz kılmaları için [sandboxing referansına](https://docs.openclaw.ai/gateway/sandboxing) bakın.

> #### Sorun Giderme: Docker İzin Reddedildi
> 
> Docker komutlarını çalıştırırken "permission denied" hatası alırsanız:
> 
> **Adım 1: Kullanıcınızı docker grubuna ekleyin**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
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
> **Hızlı geçici çözüm** (yeniden başlatma sonrası sıfırlanır):
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

<!-- @os:linux -->
## (Önerilir) Firecrawl Hizmetleriyle OpenClaw Entegrasyonu

[Firecrawl](https://docs.firecrawl.dev/introduction), bu zorlukların üstesinden gelebilen ve OpenClaw otomasyonunun tüm potansiyelini ortaya çıkarabilen, kendi kendine barındırılan (self-hosted) bir web tarama ve içerik çıkarma hizmeti sunar.

Bu kurulumda OpenClaw, Podman ile yönetilen bir dizi Docker konteyneri olarak çalışır. Yaşam döngüsü yönetimini ve otomatik başlatmayı basitleştirmek için, Firecrawl'ı, temeldeki Podman Compose yığınını (stack) düzenleyen bir kullanıcı düzeyinde `systemd` hizmeti olarak kaydediyoruz. Bu, OpenClaw'ın konteynerlerle doğrudan etkileşime girmek yerine standart `systemctl --user` komutlarını kullanarak Firecrawl hizmetinin gateway'ini başlatmasına, durdurmasına ve doğrulamasına olanak tanır.

İşleri basit tutmak için tüm süreci dört adıma ayırdık:

---

### 1. Sistem hizmetini kaydedin
Systemd kullanıcı yapılandırma dizinine gidin:
```bash
cd ~/.config/systemd/user
```
`firecrawl.service` adında yeni bir dosya oluşturup açın.
```bash
nano firecrawl.service
```
Aşağıdaki yapılandırmayı kopyalayıp yapıştırın:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
Bu noktada, hizmet tanımlanmış ancak henüz `systemd` ile kaydedilmemiştir.
Dosya adının yukarıda oluşturduğunuzla tam olarak eşleştiğinden emin olun, ardından şunu çalıştırın:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Başarılı olursa aşağıdaki çıktıyı görmelisiniz:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/`, otomatik olarak başlatılacak şekilde yapılandırılmış hizmetlere sembolik bağlantılar içerir.
### 2. Firecrawl'ı Yapılandırın

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md), kazıma ve veri işleme ortamları üzerinde tam kontrol isteyenler için idealdir, ancak buna karşılık ek bakım ve yapılandırma çabası gerektirir.

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
# FIRECRAWL_API_KEY="" # optional
```
### 3. OpenClaw'ı Podman Compose ile Dağıtın

Devam etmeden önce en son OpenClaw Docker imajını çektiğinizden emin olun:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Bu işlem tamamlandıktan sonra, OpenClaw Compose dosyasını [openclaw-compose.yaml](assets/openclaw-compose.yaml) indirin ve kök `/firecrawl` dizinine yerleştirin:

> `WorkingDirectory=${HOME}/firecrawl` içinde belirtildiği gibi `systemd`'nin hizmeti doğru şekilde bulup başlatabilmesi için bu kural gereklidir.

> Gerektiğinde ek Firecrawl hizmetleri ekleyerek yığını her zaman genişletebilirsiniz. Kullanılabilir hizmetlerin tam listesini resmi [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) dosyasında bulabilirsiniz.

### 4. Firecrawl Üzerinden OpenClaw Hizmetini Başlatın

Kontrolü `systemd`'ye devretmeden önce, yığını manuel olarak çalıştırarak her şeyin doğru çalıştığını doğrulayın:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Her şey doğru şekilde yapılandırılmışsa, OpenClaw konteynerinin ayağa kalktığını görmelisiniz ve komut satırı çıktınız buna benzer görünmelidir:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Doğruladıktan sonra, devam etmeden önce yığını tekrar kapatın:
```bash
podman compose -f openclaw-compose.yaml down
```
Hizmeti başlatmadan önce, `firecrawl` dizini ve `.env` dosyası üzerinde doğru sahiplik ve izinlerin ayarlandığından emin olmalısınız.
Bu, hizmetin başlangıçta kimlik bilgilerinizi yazabilmesi için gereklidir.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Her şey doğrulandığına göre, hizmeti `systemd` üzerinden başlatın:
```bash
systemctl --user start firecrawl.service
```
[OpenClaw Actions](https://docs.openclaw.ai/) etkileşimli konteyner içinden erişilebilir ve Web Dashboard aynı ana bilgisayarda ve portta http://127.0.0.1:18789 adresinde kullanılabilir.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### `OPENCLAW_GATEWAY_TOKEN` Değerini Elde Etme

Hizmet çalışmaya başladığında, ana dizininizde yeni bir `.openclaw` dizini oluşturulduğunu fark edeceksiniz (~/.openclaw). Bu dizin varsayılan olarak kilitlidir, bu nedenle gateway token'ınızı almak için kilidini açmanız gerekir.

1. Dizine erişim izni verin:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Gateway token'ınızı okuyun:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Çıktıda `OPENCLAW_GATEWAY_TOKEN` değerini bulun.

3. Gateway dashboard'ını tarayıcınızda http://127.0.0.1:18789 adresinden açın. Kimlik doğrulama istendiğinde token'ınızı yapıştırın.

Hizmeti durdurmak için şunu çalıştırın:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## OpenClaw Gateway'i Başlatın

Gateway, agent döngüsünü yöneten ve dashboard'ı sunan OpenClaw sürecidir:

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

Gateway hâlâ çalışırken, dashboard'ı açmak için ikinci bir terminalde şunu çalıştırın:

```bash
openclaw dashboard
```

Gateway, loopback'e bağlandığından, dashboard aynı makineden açıldığında otomatik olarak kimlik doğrulaması yapar; yerel erişim için token girişi veya cihaz onayı gerekmez. Lemonade modelinizin aktif backend olarak listelendiği OpenClaw dashboard'ını görmelisiniz.

> Sandboxing'i etkinleştirdiyseniz, dashboard'dan agent'a `run hostname` komutunu çalıştırmasını isteyerek bunu doğrulayabilirsiniz. Makinenizin ana bilgisayar adı yerine kısa bir konteyner kimliği görürseniz, sandbox çalışıyor demektir.

**Tebrikler, sıfırdan tamamen yerel bir AI agent yığını oluşturdunuz.**

> **Gateway token'ına mı ihtiyacınız var?** Dashboard URL'sini token gömülü olarak yazdırmak için `openclaw dashboard --no-open` komutunu çalıştırın (ayrıca panonuza kopyalamayı da dener). Alternatif olarak, token `~/.openclaw/openclaw.json` dosyasında `gateway.auth.token` konumundadır.
>
> **Uzak bir cihazı onaylama:** Dashboard'ı ikinci bir makineden veya telefondan açtığınızda, tarayıcı bir istek kimliği görüntüler. Gateway'i çalıştıran makineye geri dönüp şunu çalıştırın:
> ```bash
> openclaw devices approve <requestId>
> ```
> Bu yalnızca uzak veya ikincil cihazlar için gereklidir, aynı makineden loopback erişimi otomatik olarak kimlik doğrular.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## İsteğe Bağlı: Bir İletişim Kanalı Bağlama

Gateway çalışmaya başladıktan sonra herhangi bir cihazdan yerel agent'ınıza ulaşabilirsiniz. Kurulumunuza uygun seçeneği seçin. OpenClaw [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) ve diğer kanalları destekler, tam listeyi [docs.openclaw.ai](https://docs.openclaw.ai) adresinde bulabilirsiniz.

---

### Seçenek A: Discord

Discord, bir bot eklemek için **yönetici erişiminize sahip olduğunuz** bir sunucu gerektirir. Sunucuları paylaşıyor ancak birine sahip değilseniz, bunun yerine Seçenek B'yi (Telegram) kullanın.

#### Bir Discord hesabı ve sunucusu oluşturun

Discord hesabınız yoksa [discord.com](https://discord.com) adresinden kaydolun. Ayrıca yönetici olduğunuz bir sunucuya da ihtiyacınız var; Discord kenar çubuğundaki **+** simgesine tıklayıp **Create My Own**'ı seçerek bir tane oluşturun. Özel bir sunucu yeterlidir.

#### Bir Discord uygulaması ve botu oluşturun

1. [Discord Developer Portal](https://discord.com/developers/applications) adresine gidin ve **New Application**'a tıklayın. Bir isim verin (örn. "openclaw-bot").
2. Kenar çubuğunda **Bot**'a tıklayın. Bot için bir kullanıcı adı belirleyin.
3. Hâlâ Bot sayfasındayken, **Privileged Gateway Intents** bölümüne kaydırın ve şunları etkinleştirin:
   - **Message Content Intent** (gerekli)
   - **Server Members Intent** (önerilir)
4. Yukarı kaydırın ve bot token'ınızı oluşturmak için **Reset Token**'a tıklayın. Kopyalayın.

#### Botu sunucunuza ekleyin

1. Kenar çubuğunda **OAuth2/ URL Generator**'a tıklayın.
2. **Scopes** altında `bot` ve `applications.commands`'ı etkinleştirin.
3. **Bot Permissions** altında şunları etkinleştirin: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Oluşturulan URL'yi kopyalayın, tarayıcınıza yapıştırın, sunucunuzu seçin ve onaylayın. Bot artık sunucunuzun üye listesinde görünmelidir.
#### Kimliklerinizi toplayın

Discord'da Geliştirici Modunu etkinleştirin (**Kullanıcı Ayarları/ Gelişmiş/ Geliştirici Modu**), ardından:
- Sunucu simgenize sağ tıklayın: **Sunucu Kimliğini Kopyala**
- Kendi avatarınıza sağ tıklayın: **Kullanıcı Kimliğini Kopyala**

#### Sunucu üyelerinden gelen DM'lere izin verin

Sunucu simgenize sağ tıklayın/ **Gizlilik Ayarları**/ **Doğrudan Mesajlar**'ı açık konuma getirin. Bu, botun size DM göndermesine olanak tanır ve eşleştirme adımı için gereklidir.

#### OpenClaw'ı Discord için yapılandırın

Bot token'ınızı bir ortam değişkeni olarak saklayın, ardından Discord'u etkinleştiren, token'a başvuran ve sunucunuzu izin listesine ekleyen tek bir yama dosyası oluşturun. Yukarıda toplanan kimliklerle `<server_id>` ve `<user_id>` değerlerini değiştirin.

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

> **Bu yapılandırmayı yapmasını ajana sormaya güvenmeyin.** Sanal alan (sandboxing) etkinleştirildiğinde, ajan sanal alan içinden `~/.openclaw/openclaw.json` dosyasına yazamaz; bunun yerine ana makinede yukarıdaki CLI komutlarını kullanın.

Yeni kanal yapılandırmasını algılaması için ağ geçidini yeniden başlatın:

```bash
openclaw gateway run --bind loopback --port 18789
```

Birkaç saniye içinde ağ geçidi çıktısında `logged in to discord as <bot-name>` ifadesini görmelisiniz.

#### Discord hesabınızı eşleştirin

Discord'da bota DM gönderin. Bot kısa bir eşleştirme kodu ile yanıt verecektir.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

OpenClaw'ı çalıştıran makinede onaylayın:
```bash
openclaw pairing approve discord <CODE>
```

> Eşleştirme kodları bir saat sonra geçerliliğini yitirir.

Artık ajanınızla doğrudan Discord üzerinden sohbet edebilir ve görevleri yerel donanımınıza aktarabilirsiniz.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Seçenek B: Telegram

Telegram, çoğu kullanıcı için Discord'dan daha basittir; sunucu veya yönetici erişimi gerektirmez.

#### Bir Telegram botu oluşturun

1. Telegram'ı açın ve **@BotFather**'a mesaj gönderin.
2. `/newbot` gönderin ve yönergeleri izleyin. Size verilen bot token'ını kaydedin.

#### OpenClaw'ı Telegram için yapılandırın

Token'ı bir ortam değişkeni olarak saklayın:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Kanal yapılandırmasını `~/.openclaw/openclaw.json` dosyasına ekleyin (veya panel üzerinden yamalayın):

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

Ağ geçidini yeniden başlatın, ardından botunuza Telegram üzerinden herhangi bir mesaj gönderin. Eşleştirmeyi onaylayın:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Eşleştirme kodları bir saat sonra geçerliliğini yitirir. Artık ajanınızla Telegram DM üzerinden sohbet edebilirsiniz.

---

## Sonraki Adımlar

Ajanınız artık telefonunuzdan komutlar alabilir ve yerel makinenizde işlem yapabilir hale geldiğine göre, keşfetmeye değer üç yön:

1. **Borsa özetleyici**: OpenClaw'ı belirli bir aralıkta finansal API'lerden veri almak, günün hareketlerini yerel modelinizle özetlemek ve seçtiğiniz kanal üzerinden her sabah telefonunuza bir özet göndermek üzere zamanlayın.

2. **İnce ayar izleyicisi**: Telegram veya Discord üzerinden uzaktan bir eğitim işi başlatın, ardından ajanın eğitim günlüğünü izlemesini ve periyodik olarak kayıp (loss) değerlerini, GPU kullanımını ve disk kullanımını telefonunuza bildirmesini sağlayın. Çalıştırma takılırsa veya VRAM ani yükseliş yaparsa, makinenin başında olmanıza gerek kalmadan hemen haberdar olursunuz.

3. **Yerel bir VLM ile IOT**: Ön kapınıza bir kamera yerleştirin, Lemonade üzerinde bir görüntü işleme modeli çalıştırın ve OpenClaw'ın çerçeveleri talep üzerine veya bir tetikleyiciyle analiz etmesini sağlayın. Telefonunuzdan "bugün herhangi bir paket geldi mi?" diye sorun ve kendi donanımınızdan net bir yanıt alın.

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->