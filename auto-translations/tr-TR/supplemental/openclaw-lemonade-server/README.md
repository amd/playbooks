<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

# OpenClaw'ı Arka Uç Olarak Lemonade Server ile Çalıştırma

## Genel Bakış

[**OpenClaw**](https://openclaw.ai/), kod yazıp çalıştırabilen, dosyaları yönetebilen ve sizin adınıza karmaşık çok adımlı görevleri yerine getirebilen özerk bir yapay zeka ajanıdır. Yalnızca soruları yanıtlayan bir sohbet asistanının aksine, OpenClaw sisteminizde gerçek eylemler gerçekleştirir; bu da onun, zorlu bir ajan döngüsüne ayak uydurabilecek hızlı ve yetenekli bir yapay zeka arka ucuna ihtiyaç duyduğu anlamına gelir.

[**Lemonade Server**](https://lemonade-server.ai/) işte bu arka uçtur. GenAI modellerini doğrudan donanımınızda çalıştıran ve bunları sektör standardı OpenAI API'si aracılığıyla sunan açık kaynaklı bir yerel çıkarım sunucusudur.

Birlikte, tamamen yerel bir yapay zeka ajan yığını oluştururlar: Lemonade model çıkarımını yönetir, OpenClaw ise model çıktılarını gerçek eylemlere dönüştüren ajan döngüsünü sağlar.

> **Devam etmeden önce:** OpenClaw son derece özerk bir yapay zeka ajanıdır. Herhangi bir yapay zeka ajanına sisteminize erişim izni vermek, öngörülemeyen veya istenmeyen sonuçlara yol açabilir. Yalnızca riskleri anladıysanız ve özerk yazılımların sizin adınıza hareket etmesinden rahatsız olmuyorsanız devam edin.

---

## Bu Rehberde Neler Öğreneceksiniz

Bu rehberin sonunda şunları yapabilecek duruma geleceksiniz:

- **Lemonade Server** hakkında bilgi edinin
- **OpenClaw'ı yükleyin** ve yapay zeka arka ucu olarak **Lemonade Server'a yönlendirin**.
- **OpenClaw ağ geçidini başlatın** ve ajanınızın çalışmaya hazır olduğunu doğrulayın.
- Herhangi bir cihazdan ajanınızla sohbet edebilmeniz için **bir iletişim kanalı bağlayın** (Discord veya Telegram).

---

<!-- @device:halo_box,halo,stx,krk -->
## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Edin

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarının Kurulması

<!-- @os:linux -->
- `apt-get` içeren **Ubuntu 24.04+** veya uyumlu bir Debian tabanlı Linux dağıtımı çalıştıran bir PC
- En az **12 GB RAM** (daha büyük modeller için 64 GB+ önerilir)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (İsteğe bağlı, OpenClaw'ı sanal alanda çalıştırmak için)
- Model ağırlıkları için **~10–30 GB boş disk alanı**
<!-- @os:end -->

<!-- @os:windows -->
- **Windows 10/11** çalıştıran bir PC
- En az **12 GB RAM** (daha büyük modeller için 64 GB+ önerilir)
- Model ağırlıkları için **~10–30 GB boş disk alanı**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (İsteğe bağlı, OpenClaw'ı sanal alanda çalıştırmak için)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:nodejs,openclaw,lemonade-models-qwen3-35b-a3b,lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Önerilen Modeli İndirin ve Yükleyin

Bu rehber için önerilen model, Unsloth'un **Qwen3.6-35B-A3B-GGUF** modelidir; ajan iş yüklerine oldukça uygun, 263k token'lık bağlam penceresine sahip güçlü bir MoE modelidir. Bu model UD-Q4_K_XL niceleme (quantization) kullanır. Şimdi indirin:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Ardından büyük bir bağlam penceresiyle yükleyin ve bu ayarı gelecekteki çalıştırmalar için kaydedin:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Modelin varsayılan bağlam uzunluğu 262.144 token'dır. Bellek yetersizliği (OOM) hatalarıyla karşılaşırsanız, bağlam penceresini küçültmeyi düşünebilirsiniz. Ancak Qwen3.6, karmaşık görevler için genişletilmiş bağlamdan yararlandığından, düşünme kapasitesini korumak için en az 128K token'lık bir bağlam uzunluğu korumanızı öneririz.

> **İpucu: Daha hızlı ajan yanıtları için düşünmeyi devre dışı bırakın:** Qwen3.6-35B-A3B varsayılan olarak düşünme modunda çalışır; bu da her yanıttan önce gecikme ekler. Ajan döngüleri için bu ek yük hızla birikir. [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) deposu, düşünmeyi devre dışı bırakan hazır bir yapılandırma sunar. Bunu kullanmak için dosyayı indirin ve içe aktarın:
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

## WSL'yi Kurma

OpenClaw'ı WSL içinde çalıştırıyoruz (Önerilir) ve Windows üzerinde yerel olarak çalışan Lemonade'e bağlıyoruz. Bu, Lemonade'in GPU hızlandırmasını Windows tarafında tutarken OpenClaw için bir Linux kabuk ortamı sağlar.

### WSL ve Ubuntu'yu Yükleyin

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

WSL'den çıkın ve yeniden başlatın:

```powershell
exit
wsl --shutdown
wsl
```

### Lemonade'i Windows'tan WSL'ye Köprüleyin

WSL2 sanal bir ağda çalışır. Windows üzerindeki Lemonade, WSL'nin doğrudan erişemediği `127.0.0.1` adresine bağlanır. Bir Windows bağlantı noktası vekili (port proxy), trafiği WSL ağ geçidi IP'sinden Windows localhost'una yönlendirir.

**WSL ağ geçidi IP'nizi bulun** (WSL içinde çalıştırın):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Bağlantı noktası vekilini ekleyin** (PowerShell'de Yönetici olarak çalıştırın, `<WSL-Gateway-IP>` kısmını kendi WSL ağ geçidi IP'niz ile değiştirin):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Not: Eğer `netsh: command not found` hatasıyla karşılaşırsanız, lütfen bunun yerine açık yürütülebilir adını kullanmayı deneyin - `netsh.exe`

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

#### Yeniden Başlatma Sonrasında Köprünün Çalışmaya Devam Etmesini Sağlama

`netsh portproxy` kuralı yeniden başlatmalara dayanıklıdır, ancak `wsl --shutdown` komutundan veya bir yeniden başlatmadan sonra WSL ağ geçidi IP'si değişebilir. Bu durumda, proxy hâlâ eski IP'yi gösterir ve Lemonade, WSL'den erişilemez hale gelir. Bu gerçekleşirse, aşağıdaki seçeneklerden birini kullanın.

**Seçenek 1 (önerilen) — Köprüyü otomatik olarak onarın.** Bunu her seferinde elle yapmaktan kaçınmak için, her başlangıçta ve oturum açışta köprüyü kontrol eden ve yalnızca ağ geçidi IP'si değiştiğinde yeniden oluşturan zamanlanmış bir görev kullanın. Bkz. [Lemonade WSL köprüsü otomatik onarım kılavuzu](assets/RepairLemonadeWslBridge.md).


**Seçenek 2 — Köprüyü elle onarın.** Öncelikle, WSL içinde aşağıdakini çalıştırarak mevcut WSL ağ geçidi IP'sini alın:

```bash
ip route show default | awk '{print $3}' | head -1
```

Bu değeri kopyalayın; aşağıda `<new-WSL-Gateway-IP>` yerine kullanacaksınız.

Ardından, **yükseltilmiş bir PowerShell** içinde (Yönetici olarak çalıştır), mevcut kuralları listeleyin, yalnızca eskimiş Lemonade kuralını silin ve mevcut IP ile yeni bir kural ekleyin:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

`show all` çıktısında, eskimiş Lemonade kuralı, bağlantı adresi `13305` portunda `127.0.0.1` olan girdidir; onun dinleme adresi `<old-WSL-Gateway-IP>` adresinizdir. Bu adrese göre silme işlemi yalnızca bu kuralı kaldırır ve makinenizdeki diğer port-proxy kurallarını etkilemeden bırakır.

Kurulum sırasında eklediğiniz güvenlik duvarı kuralı `13305` portuna (IP'ye değil) bağlıdır, bu nedenle çalışmaya devam eder ve yeniden oluşturulması gerekmez.

> **Öneri:** Ağ geçidi sorunlarından kaçınmak için, aşağıdaki kabuk yapılandırmasını şiddetle öneriyoruz:
> - **Windows komutları** **PowerShell**'de çalıştırılmalıdır
> - **WSL dağıtım komutları** **Yönetici** olarak çalıştırılan bir **Komut İsteminde** çalıştırılmalıdır

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

## OpenClaw'ı Yükleyin ve Yapılandırın

### OpenClaw'ı Yükleyin
<!-- @os:windows -->
> Bu bölümdeki komutları **WSL terminalinizin** içinde çalıştırın.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` bayrağı, etkileşimli kurulum sihirbazını atlar; model arka ucunu bir sonraki adımda elle yapılandıracaksınız, bu da hangi model ve sunucunun kullanıldığı üzerinde hassas kontrol sağlar.

Yeni bir terminal açın ve kurulumu doğrulayın:

```bash
openclaw --version
```

> **İpucu:** Kurulumdan sonra `command not found` görüyorsanız, npm'in global bin dizinini PATH'inize ekleyin:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Bunu kalıcı hale getirmek için, yukarıdaki satırı `~/.bashrc` veya `~/.zshrc` dosyanıza ekleyin.

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


### OpenClaw'ı Lemonade'i Kullanacak Şekilde Yapılandırma

OpenClaw'ın etkileşimli olmayan ilk kurulumunu (onboarding) çalıştırın.
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

> **OpenClaw bağlam penceresi boyutlandırması:** OpenClaw'ın sıkıştırması (compaction), `contextTokens > contextWindow − reserveTokens` olduğunda tetiklenir. Varsayılan `reserveTokensFloor` değeri 20.000 token'dır; bu, daha düşük olduğunda `reserveTokens` değerini geçersiz kılan bir tabandır, bu nedenle yaklaşık 37k'nin altındaki herhangi bir model bağlamı sonsuz bir sıkıştırma döngüsünü tetikleyecektir. Yapılandırmanızda bir kez düşük bir rezerv ayarlayın ve tabanı devre dışı bırakın; bu, her model için geçerli olur, model başına ayarlama gerekmez:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor`, rezervin kendisi değil, bir *taban* (minimum koruma) değeridir; yalnızca tabanı ayarlamanın hiçbir etkisi yoktur. `reserveTokensFloor: 0`, korumayı devre dışı bırakır böylece daha düşük `reserveTokens` değeri kabul edilir.
>
> **Ne zaman uygulanmalı:** Modelinizin etkin bağlam penceresi yaklaşık 37k'nin altındaysa bu yapılandırmayı kullanın; bu, modelin küçük olmasından (ör. 8k, 16k, 32k) veya kasıtlı olarak daha düşük bir değere sınırlandırmış olmanızdan (ör. 128k'lik bir modeli yükleyip Lemonade'de bağlamı 16k olarak ayarlamanızdan) kaynaklanabilir. Bu olmadan, OpenClaw başlangıçta sonsuz bir sıkıştırma döngüsüne girer.
>
> **Tam bağlamda büyük bağlamlı modeller:** Bunu tamamen atlayabilirsiniz. Varsayılanlar iyi çalışır, sıkıştırma pencere dolmadan çok önce devreye girer ve modelin uzun yanıtlar üretmesi için yeterli alan vardır. Bunu uygularsanız, `reserveTokens: 4096` değerinin yanıt uzunluğunu ~4k token ile sınırladığını unutmayın; bu, uzun dosya üretimini veya ayrıntılı planları kesebilir.
>
> **Bunun nereye ekleneceği:** `compaction` bloğunu, `openclaw.json` dosyanızdaki (genellikle `~/.openclaw/openclaw.json` konumunda) `agents.defaults` içine yerleştirin:
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
> Yapılandırmanızın geri kalanı (gateway, channels, models vb.) değişmeden kalır, yalnızca `compaction` anahtarının eklenmesi gerekir.
### (Önerilen) Docker Sandboxing'i Etkinleştirin

OpenClaw, tüm ajan dosya ve kod işlemlerini doğrudan ana makinenizde çalıştırmak yerine izole bir Docker container'ı üzerinden yönlendirebilir. Bu, istenmeyen herhangi bir eylemin etki alanını sandbox ile sınırlar ve ana makinenizin dosya sistemini ve ağını etkilenmeden bırakır.

Sandbox imajını bir kez oluşturun (Docker kurulu olmalıdır):

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

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
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

`~/.openclaw/openclaw.json` içindeki mevcut `agents.defaults` bloğuna `sandbox` anahtarını eklemek için şunu çalıştırın:

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

Sandbox container'ları varsayılan olarak **ağ erişimine sahip değildir**. Bind mount'lar ve ağ geçersiz kılmaları için [sandboxing referansına](https://docs.openclaw.ai/gateway/sandboxing) bakın.

> #### Sorun Giderme: Docker İzni Reddedildi
> 
> Docker komutlarını çalıştırırken "permission denied" hatası alıyorsanız:
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
> **Adım 2: Hata devam ederse, kalıcı düzeltmeyi uygulayın**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Ardından sisteminizi **yeniden başlatın**.
> 
> **Hızlı geçici çözüm** (yeniden başlatma sonrasında sıfırlanır):
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
## (Önerilen) Firecrawl Servisleri ile OpenClaw Entegrasyonu

[Firecrawl](https://docs.firecrawl.dev/introduction), bu zorlukların üstesinden gelebilen ve OpenClaw otomasyonunun tüm potansiyelini ortaya çıkarabilen, kendi kendine barındırılan bir web tarama ve içerik çıkarma hizmeti sunar.

Bu kurulumda OpenClaw, Podman ile yönetilen bir dizi Docker container'ı olarak çalışır. Yaşam döngüsü yönetimini ve otomatik başlatmayı basitleştirmek için Firecrawl'ı, temel Podman Compose yığınını düzenleyen bir kullanıcı düzeyinde `systemd` servisi olarak kaydediyoruz. Bu, OpenClaw'ın container'larla doğrudan etkileşime girmek yerine standart `systemctl --user` komutlarını kullanarak gateway'i başlatmasına, durdurmasına ve Firecrawl servisini doğrulamasına olanak tanır.

İşleri basit tutmak için tüm süreci dört adıma ayırdık:

---

### 1. Sistem servisini kaydedin
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
Bu noktada servis tanımlanmış ancak henüz `systemd` ile kaydedilmemiştir.
Dosya adının yukarıda oluşturduğunuzla tam olarak eşleştiğinden emin olun, ardından şunu çalıştırın:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Başarılı olursa, aşağıdaki çıktıyı görmelisiniz:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/`, otomatik olarak başlamak üzere yapılandırılmış servislere sembolik bağlantılar içerir.

### 2. Firecrawl'ı yapılandırın

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md), kazıma ve veri işleme ortamları üzerinde tam kontrole ihtiyaç duyanlar için idealdir ancak ek bakım ve yapılandırma çabası gerektirir.

Depoyu klonlayarak başlayın:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
`/firecrawl` dizininde bir `.env` dosyası oluşturun: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. OpenClaw'ı Podman Compose ile Dağıtın

Devam etmeden önce, en son OpenClaw Docker imajını çektiğinizden emin olun:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Bu işlem tamamlandıktan sonra, OpenClaw Compose dosyasını [openclaw-compose.yaml](assets/openclaw-compose.yaml) indirin ve kök `/firecrawl` dizinine yerleştirin:

> Bu kural, `systemd`'nin `WorkingDirectory=${HOME}/firecrawl` içinde belirtildiği gibi servisi doğru şekilde bulup başlatabilmesi için gereklidir.

> Gerektiğinde ek Firecrawl servisleri ekleyerek yığını her zaman genişletebilirsiniz. Mevcut servislerin tam listesi resmi [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) dosyasında bulunabilir.

### 4. OpenClaw Servisini Firecrawl Üzerinden Başlatın

Kontrolü `systemd`'ye devretmeden önce, yığını manuel olarak çalıştırarak her şeyin doğru çalıştığını doğrulayın:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Her şey doğru yapılandırılmışsa, OpenClaw container'ının ayağa kalktığını görmelisiniz ve komut satırı çıktınız şuna benzer olmalıdır:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Doğruladıktan sonra, devam etmeden önce yığını tekrar kapatın:
```bash
podman compose -f openclaw-compose.yaml down
```
Servisi başlatmadan önce, `firecrawl` dizini ve `.env` dosyası üzerinde doğru sahiplik ve izinlerin ayarlandığından emin olmalısınız.
Bu, servisin başlangıçta kimlik bilgilerinizi yazabilmesi için gereklidir.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Artık her şey doğrulandığına göre, servisi `systemd` üzerinden başlatın:
```bash
systemctl --user start firecrawl.service
```
[OpenClaw Eylemleri](https://docs.openclaw.ai/), etkileşimli container içinden erişilebilir ve Web Panosu aynı ana makine ve bağlantı noktasında http://127.0.0.1:18789 adresinde kullanılabilir.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### `OPENCLAW_GATEWAY_TOKEN` Değerinizi Alma

Servis çalışır duruma geldiğinde, ana dizininizde (~/.openclaw) yeni bir `.openclaw` dizininin oluşturulduğunu fark edeceksiniz. Bu dizin varsayılan olarak kilitlidir, bu nedenle gateway token'ınızı almak için kilidini açmanız gerekir.

1. Dizine erişim izni verin:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Gateway token'ınızı okuyun:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Çıktıda `OPENCLAW_GATEWAY_TOKEN` değerini bulun.

3. Gateway panosunu tarayıcınızda http://127.0.0.1:18789 adresinde açın. Kimlik doğrulama istendiğinde token'ınızı yapıştırın.

Servisi durdurmak için şunu çalıştırın:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## OpenClaw Gateway'i Başlatma

Gateway, aracı döngüsünü yöneten ve dashboard'u sunan OpenClaw sürecidir:

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

Dashboard'u açmak için, gateway hâlâ çalışırken ikinci bir terminalde şunu çalıştırın:

```bash
openclaw dashboard
```

Gateway loopback'e bağlandığı için, dashboard aynı makineden açıldığında otomatik olarak kimlik doğrulaması yapar; yerel erişim için token girişi veya cihaz onayına gerek yoktur. Lemonade modelinizin etkin backend olarak listelendiği OpenClaw dashboard'unu görmelisiniz.

> Sandboxing'i etkinleştirdiyseniz, dashboard üzerinden aracıya `run hostname` komutunu çalıştırmasını isteyerek bunu doğrulayabilirsiniz. Makinenizin ana bilgisayar adı yerine kısa bir container ID görüyorsanız, sandbox çalışıyor demektir.

**Tebrikler, sıfırdan tamamen yerel bir AI aracı yığını oluşturdunuz.**

> **Gateway token'ına mı ihtiyacınız var?** Dashboard URL'sini token gömülü şekilde yazdırmak için `openclaw dashboard --no-open` komutunu çalıştırın (ayrıca panoya kopyalamaya çalışır). Alternatif olarak, token `~/.openclaw/openclaw.json` dosyasında `gateway.auth.token` konumundadır.

**Dashboard'a Başka Bir Cihazdan Erişim (SSH Tüneli Üzerinden)**

OpenClaw uzak bir makinede çalışıyorsa, dashboard'una yerel makinenizden bir SSH tüneli üzerinden ulaşabilirsiniz. Tünel, gateway portunu (`18789`) ileterek yerel tarayıcınızın uzak gateway ile `127.0.0.1` üzerinden iletişim kurmasını sağlar.

1. **Yerel makinenizden**, uzak makineye bir kez bağlanın ve parmak izi istemini kabul edin, böylece host bilinen hostlarınıza eklenir:

   ```bash
   ssh user@<host-ip>
   ```

2. Hâlâ **yerel makinenizde**, SSH tünelini açın:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Not:** Şifrenizi girdikten sonra terminal herhangi bir çıktı göstermez ve donmuş gibi görünür. Bu beklenen bir durumdur: `-N` bayrağı SSH'ye herhangi bir uzak komut çalıştırmamasını söyler, bu yüzden sadece tüneli açık tutar. Bu terminali çalışır durumda bırakın.

3. **Yerel makinenizde**, bir tarayıcı açın ve `http://127.0.0.1:18789` adresine gidin.

4. **Uzak makinede**, gateway token'ını yazdırın ve giriş yapmak için tarayıcıya yapıştırın:

   ```bash
   openclaw dashboard --no-open
   ```

   Bu, dashboard URL'sini token gömülü şekilde yazdırır; giriş yapmak için token'ı kopyalayın. (Token ayrıca `~/.openclaw/openclaw.json` dosyasında `gateway.auth.token` konumunda saklanır.)

> **Uzak bir cihazı onaylama:** Dashboard'u başka bir makineden veya telefondan açtığınızda, tarayıcı bir istek ID'si gösterebilir. **Uzak makinede**, bekleyen istekleri listeleyin:
> ```bash
> openclaw devices list
> ```
> Ardından eşleşen isteği onaylayın:
> ```bash
> openclaw devices approve <requestId>
> ```
> Bu yalnızca uzak veya ikincil cihazlar için gereklidir; aynı makineden loopback erişimi otomatik olarak kimlik doğrulaması yapar. Ayrıntılar için [Uzaktan Erişim](https://docs.openclaw.ai/gateway/remote) belgelerine bakın.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## İsteğe Bağlı: Bir İletişim Kanalı Bağlama

Gateway çalışmaya başladığında yerel aracınıza herhangi bir cihazdan ulaşabilirsiniz. Kurulumunuza uyan seçeneği seçin. OpenClaw [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) ve diğer kanalları destekler, tam listeye [docs.openclaw.ai](https://docs.openclaw.ai) adresinden bakabilirsiniz.

---

### Seçenek A: Discord

Discord, bir bot eklemek için **yönetici erişiminiz olan** bir sunucu gerektirir. Sunucuları paylaşıyor ama birine sahip değilseniz, bunun yerine Seçenek B'yi (Telegram) kullanın.

#### Bir Discord hesabı ve sunucusu oluşturma

Bir Discord hesabınız yoksa, [discord.com](https://discord.com) adresinden kaydolun. Ayrıca yönetici olduğunuz bir sunucuya ihtiyacınız var; Discord kenar çubuğundaki **+** simgesine tıklayıp **Create My Own** seçeneğini seçerek bir tane oluşturun. Özel bir sunucu yeterlidir.

#### Bir Discord uygulaması ve bot oluşturma

1. [Discord Developer Portal](https://discord.com/developers/applications) adresine gidin ve **New Application**'a tıklayın. Bir isim verin (örn. "openclaw-bot").
2. Kenar çubuğunda **Bot**'a tıklayın. Bot için bir kullanıcı adı belirleyin.
3. Hâlâ Bot sayfasındayken, **Privileged Gateway Intents** bölümüne kaydırın ve şunları etkinleştirin:
   - **Message Content Intent** (gerekli)
   - **Server Members Intent** (önerilir)
4. Tekrar yukarı kaydırın ve bot token'ınızı oluşturmak için **Reset Token**'a tıklayın. Kopyalayın.

#### Botu sunucunuza ekleme

1. Kenar çubuğunda **OAuth2/ URL Generator**'a tıklayın.
2. **Scopes** altında, `bot` ve `applications.commands` seçeneklerini etkinleştirin.
3. **Bot Permissions** altında şunları etkinleştirin: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Oluşturulan URL'yi kopyalayın, tarayıcınıza yapıştırın, sunucunuzu seçin ve onaylayın. Bot artık sunucunuzun üye listesinde görünmelidir.

#### Kimliklerinizi toplama

Discord'da Geliştirici Modunu etkinleştirin (**User Settings/ Advanced/ Developer Mode**), ardından:
- Sunucu simgenize sağ tıklayın: **Copy Server ID**
- Kendi avatarınıza sağ tıklayın: **Copy User ID**

#### Sunucu üyelerinden DM'lere izin verme

Sunucu simgenize sağ tıklayın/ **Privacy Settings**/ **Direct Messages** seçeneğini açın. Bu, botun size DM gönderebilmesini sağlar ve eşleştirme adımı için gereklidir.

#### OpenClaw'u Discord için yapılandırma

Bot token'ınızı bir ortam değişkeni olarak saklayın, ardından Discord'u etkinleştiren, token'a referans veren ve sunucunuzu izin listesine ekleyen tek bir yama dosyası oluşturun. Yukarıda toplanan kimlikleri kullanarak `<server_id>` ve `<user_id>` yerine kendi değerlerinizi yazın.

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

> **Bunu yapılandırması için aracıya sormaya güvenmeyin.** Sandboxing etkinleştirildiğinde, aracı sandbox içinden `~/.openclaw/openclaw.json` dosyasına yazamaz; bunun yerine yukarıdaki CLI komutlarını host üzerinde kullanın.

Yeni kanal yapılandırmasını alması için gateway'i yeniden başlatın:

```bash
openclaw gateway run --bind loopback --port 18789
```

Birkaç saniye içinde gateway çıktısında `logged in to discord as <bot-name>` ifadesini görmelisiniz.
#### Discord hesabınızı eşleştirin

Discord'da bota DM gönderin. Bot kısa bir eşleştirme kodu ile yanıt verecektir.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

OpenClaw çalıştıran makinede onaylayın:
```bash
openclaw pairing approve discord <CODE>
```

> Eşleştirme kodlarının süresi bir saat sonra dolar.

Artık doğrudan Discord'dan aracınızla sohbet edebilir ve görevleri yerel donanımınıza aktarabilirsiniz.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Seçenek B: Telegram

Telegram, çoğu kullanıcı için Discord'dan daha basittir, sunucu veya yönetici erişimi gerektirmez.

#### Bir Telegram botu oluşturun

1. Telegram'ı açın ve **@BotFather**'a mesaj gönderin.
2. `/newbot` gönderin ve yönlendirmeleri izleyin. Size verdiği bot token'ını kaydedin.

#### Telegram için OpenClaw'ı yapılandırın

Token'ı bir ortam değişkeni olarak saklayın:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Kanal yapılandırmasını `~/.openclaw/openclaw.json` dosyasına ekleyin (veya panel üzerinden yama yapın):

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

Ağ geçidini yeniden başlatın, ardından botunuza Telegram'da herhangi bir mesaj gönderin. Eşleştirmeyi onaylayın:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Eşleştirme kodlarının süresi bir saat sonra dolar. Artık Telegram DM üzerinden aracınızla sohbet edebilirsiniz.

---

## Sonraki Adımlar

Artık aracınız telefonunuzdan komutlar alabildiğine ve yerel makinenizde işlem yapabildiğine göre, keşfetmeye değer üç yön şunlardır:

1. **Borsa özetleyici**: OpenClaw'ı sabit bir aralıkla finansal API'lerden veri almak, günün hareketlerini yerel modelinizle özetlemek ve seçtiğiniz kanal üzerinden her sabah telefonunuza bir özet göndermek üzere zamanlayın.

2. **İnce ayar izleyici**: Telegram veya Discord üzerinden uzaktan bir eğitim işi başlatın, ardından aracının eğitim günlüğünü takip etmesini ve periyodik kayıp değerlerini, GPU kullanımını ve disk kullanımını telefonunuza geri bildirmesini sağlayın. Çalışma takılırsa veya VRAM ani yükseliş yaparsa, makinenin başında olmanıza gerek kalmadan hemen haberdar olursunuz.

3. **Yerel bir VLM ile IOT**: Kapınıza bir kamera yönlendirin, Lemonade üzerinde bir görsel model çalıştırın ve OpenClaw'ın kareleri talep üzerine veya bir tetikleyiciyle analiz etmesini sağlayın. Telefonunuzdan "bugün herhangi bir paket geldi mi?" diye sorun ve kendi donanımınızdan net bir yanıt alın.

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