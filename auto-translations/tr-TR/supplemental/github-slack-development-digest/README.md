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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Genel Bakış

Geliştiriciler, küçük ve tekrar eden döngülerde çok zaman harcar: etiketlenmiş pull request'leri incelemek, GitHub yorumlarını yanıtlamak, yeni sorunları önceliklendirmek, Slack konularını günlük durum toplantısı notlarına veya olay takiplerine dönüştürmek ve sürüm ya da araştırma sinyallerini izlemek.
Her döngü tanıdıktır, ancak yine de bir muhakeme gerektirir: doğru bağlamı toplamak, nelerin önemli olduğuna karar vermek ve ekibin zaten çalıştığı yerde net bir güncelleme paylaşmak.

[OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview), bu döngüleri zamanlanmış veya olay tetiklemeli agent konuşmalarına dönüştürür: bir AI yazılım agent'ının bağlamı okuyabildiği, araçları çağırabildiği ve bir güncelleme oluşturabildiği çalıştırmalar.
OpenHands eklentiler kataloğundaki paylaşılan otomasyon şablonları, GitHub pull request incelemesi, depo izleme, Linear sorun önceliklendirmesi, olay sonrası değerlendirmeler, Slack günlük durum özetleri ve araştırma özetleri için bu deseni izler: bir otomasyon uyanır, bağlamı almak için GitHub veya Slack gibi yapılandırılmış entegrasyonları kullanır, bu bağlam üzerinde büyük bir dil modeliyle (LLM) muhakeme yapar ve bir sonucu geri yazar.

[Agent Canvas](https://github.com/OpenHands/agent-canvas), bu otomasyonları oluşturmak ve test etmek için yerel kontrol düzlemidir.
Bu playbook'ta, agent konuşmalarını yürüten arka plan süreci olan bir OpenHands Agent Server çalıştırır ve agent'ı GitHub ve Slack gibi harici hizmetlere bağlar.

İş akışını AMD sisteminizde tutmak için agent, Lemonade Server tarafından sunulan yerel bir modelle konuşur.
Lemonade, bu modeli OpenAI uyumlu bir API üzerinden sunar; bu sayede Agent Canvas onu uzak bir OpenAI tarzı uç nokta gibi yapılandırabilirken model, prompt ve iş akışı bağlamı yerel kalır.

Bu playbook'ta somut bir otomasyon oluşturacaksınız: zamanlanmış bir GitHub'dan Slack'e geliştirme özeti.
Bu otomasyon, son depo etkinliğini incelemek için GitHub'ı, özeti paylaşmak için Slack'i, otomasyonu yapılandırmak ve test etmek için Agent Canvas API çağrılarını ve LLM'yi yerel olarak çalıştırmak için Lemonade'i kullanır.

![GitHub MCP, OpenHands otomasyonu, Lemonade Server ve Slack MCP'yi gösteren mimari diyagramı](assets/00-architecture-overview.png)

## Neler Öğreneceksiniz

- Lemonade Server'ı nasıl başlatacağınızı ve yerel bir modelin sohbet isteklerini yanıtladığını nasıl doğrulayacağınızı
- Agent Canvas'ı nasıl başlatacağınızı ve Agent Server'ını yerel bir LLM'ye nasıl yönlendireceğinizi
- Agent Server API üzerinden GitHub ve Slack Model Context Protocol (MCP) sunucularını nasıl kuracağınızı
- Slack'e bir geliştirme özeti gönderen zamanlanmış bir OpenHands otomasyonunu nasıl oluşturup çalıştıracağınızı
- En yaygın yerel model ve otomasyon hatalarını nasıl gidereceğinizi

## Temel Kavramlar

| Kavram | Nedir | Bu playbook'taki yeri |
| --- | --- | --- |
| Lemonade Server | AMD donanımı için oluşturulmuş, OpenAI uyumlu bir API sunan yerel bir LLM sunum platformu. Verileriniz asla makinenizden ayrılmaz. | Agent'ı güçlendiren modeli çalıştırır. |
| OpenHands Agent Server | OpenHands agent konuşmalarını yürüten arka plan süreci. | Agent'ı, LLM profilini ve MCP sunucularını barındırır. |
| Agent Canvas | Agent Server'ı ve agent çalıştırmalarını incelemek için bir arayüz çalıştıran OpenHands için yerel kontrol düzlemi. | Arka planları başlatır ve çağırdığınız API'yi sağlar. |
| MCP sunucusu | Bir agent'a GitHub veya Slack gibi harici bir hizmet için araçlar sağlayan bir Model Context Protocol sunucusu. | Agent'ın GitHub'ı okumasını ve Slack'e yazmasını sağlar. |
| OpenHands otomasyonu | Bağlamı alan, üzerinde muhakeme yapan ve bir sonucu bir yere yazan zamanlanmış veya olay tetiklemeli bir agent konuşması. | Burada oluşturduğunuz GitHub'dan Slack'e özet. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Kodlama-agent iş akışları daha büyük bir model ve bağlam penceresinden faydalanır.
> En az 32 GB sistem belleği kullanın ve daha büyük GGUF modelleri için 64 GB veya daha fazlasını tercih edin.
<!-- @device:end -->

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme

<!-- @require:software-update -->
<!-- @device:end -->

## Ön Koşullar

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

İhtiyacınız olanlar:

- Standart [Lemonade kurulum kılavuzu](https://lemonade-server.ai/docs/guide/install/) izlenerek kurulmuş Lemonade Server.

<!-- @os:linux -->
- Yayımlanmış Agent Canvas CLI'sini kurmak ve `npx` ile MCP sunucularını çalıştırmak için kullanılan Node.js 22.12 veya üzeri sürüm ve `npm`.
- Agent Canvas'ın Agent Server ortamını oluşturmak için kullandığı Python paket yöneticisi `uv`. Henüz kurulu değilse [uv kurulum kılavuzu](https://docs.astral.sh/uv/getting-started/installation/)'ndan kurun.
- Şema tabanlı agent ayarları, `LLMSummarizingCondenserSettings.max_tokens` ve LLM `custom_tokenizer` desteğine sahip güncel, yayımlanmış bir `@openhands/agent-canvas` paketi.
- Agent Server ortamında mevcut olan Python `transformers` paketi. `custom_tokenizer` ayarlandığında sohbet şablonu (chat-template) token sayımı için gereklidir.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), kurulu ve çalışır durumda. Windows'ta Agent Canvas yığını, Node.js, `uv`, `transformers` ve `@openhands/agent-canvas` paketini içeren yayımlanmış Docker imajından çalışır; bu nedenle bunları ana makinede kurmanız gerekmez.
<!-- @os:end -->

- Özetlenmesini istediğiniz depoya okuma erişimine sahip bir GitHub token'ı.
- `chat:write` ve kanal okuma erişimine sahip bir Slack bot token'ı (`xoxb-...`).
- Bir Slack ekip kimliği (`T...`).
- Özetin paylaşılacağı bir Slack kanal kimliği (`C...`).

Otomasyonu test etmeden önce Slack uygulamasını hedef kanala davet edin.
## Bu Kılavuzda Kullanılan Değişkenler

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

Bu iki değişken, aşağıdaki doğrulama komutları tarafından kullanılır.
Model, tokenizer ve diğer LLM ayarları, sonraki adımlarda doğrudan Agent Canvas kullanıcı arayüzüne girildiğinden, bunların gerçek değerleri ihtiyaç duyduğunuz yerde satır içinde gösterilir.

Aşağıdaki değerler, sonraki adımlarda Agent Canvas kullanıcı arayüzüne girilir.
Buraya kopyalayabilmeniz için bunları burada belirleyin:

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

`GITHUB_REPO_FILTER` için açık bir `owner/repo` değeri kullanın.
Geniş organizasyon joker karakterleri, yerel modeller için çok fazla MCP bağlamı döndürebilir.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Lemonade Sunucusunu Başlatın

Modeli Lemonade CLI üzerinden başlatın:

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **Donanımınıza uygun bir model seçin.** `Qwen3.6-35B-A3B-GGUF` (~20 GB), bu iş akışı için güçlü bir modeldir ancak büyük bir bellek havuzu gerektirir.
> Cihazınızın belleği veya GPU VRAM'i sınırlıysa, Lemonade model kütüphanesinden daha küçük bir GGUF modeli seçin ve bu model kimliğini (ve buna karşılık gelen tokenizer'ı) bu kılavuz boyunca kullanın.

> **Not:** İlk `lemonade run` komutu, model henüz mevcut değilse onu indirir; bu işlem, modelin boyutuna ve bağlantınıza bağlı olarak biraz zaman alabilir.

Lemonade, OpenAI uyumlu bir API'yi şu adreste sunar:

```text
http://127.0.0.1:13305/api/v1
```

İsteğe bağlı: Agent Canvas veya otomasyon çalıştırıcısı aynı makinede değilse, Lemonade uç noktasını güvenli bir tünel üzerinden yayınlayın ve HTTPS URL'sini LLM temel URL'si olarak kullanın.
[ngrok](https://ngrok.com/), yerel bir bağlantı noktasını güvenli bir HTTPS URL'si üzerinden internete açar; ücretsiz bir ngrok hesabı gerektirir ve `YOUR_NGROK_DOMAIN.ngrok-free.dev` yerine kendi ayrılmış alan adınızı koyarsınız:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Yerel Modeli Doğrulayın

Lemonade'in seçilen modeli sunabildiğini doğrulayın:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Ardından küçük bir sohbet isteği gönderin:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

Ardından küçük bir sohbet isteği gönderin:

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

Bu, bir `choices` dizisi döndürüyorsa, Lemonade Agent Canvas için hazır demektir.

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
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 64
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

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

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. Agent Canvas'ı Başlatın

<!-- @os:linux -->
Yayınlanan Agent Canvas paketini kurun ve tüm yığını başlatın:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Genel npm kurulumu bir izin hatasıyla başarısız olursa, aşağıdaki npm izinleri sorun giderme bölümüne bakın.

Varsayılan olarak, Agent Canvas `http://localhost:8000` adresinde başlar.
Bu URL'yi tarayıcınızda açın.
Bağlantı noktasının özel bir önemi yoktur—8000 zaten kullanımdaysa, `--port` (veya `-p`) ile boş herhangi bir bağlantı noktasını geçebilirsiniz.
Varsayılan yerel arka uç, ana ekranda sağlıklı olarak görünmelidir.

> **Not:** İlk başlatma, Agent Server'ın `uv` tarafından yönetilen Python ortamını oluşturduğundan, arka ucun sağlıklı olarak raporlanmasından önce birkaç dakika sürebilir.

`agent-canvas` komutu, agent sunucusunu, otomasyon arka ucunu ve web ön ucunu birlikte başlatır.
OpenHands'i yerel olarak çalıştırmak için yalnızca bu tek komuta ihtiyacınız vardır.
Bu kılavuzun geri kalanı, tarayıcınızdaki Agent Canvas kullanıcı arayüzü üzerinden her şeyi yapılandırır.
<!-- @os:end -->

<!-- @os:windows -->
Windows'ta, yayınlanan Agent Canvas konteyner görüntüsünü Docker Desktop ile çalıştırın.
Görüntü, Agent Server, otomasyon arka ucu ve web ön ucunu bir arada içerdiğinden, ana bilgisayara Node.js, `uv` veya CLI kurmanız gerekmez.

Öncelikle, konteynerin bağlayacağı yapılandırma ve çalışma alanı klasörlerini oluşturun:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Yayınlanan görüntüyü çekin (yaklaşık 6 GB; herkese açıktır, bu nedenle oturum açmaya gerek yoktur):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Ardından yığını başlatın:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Tarayıcınızda `http://localhost:8000/canvas` adresini açın.
8000 bağlantı noktası zaten kullanımdaysa, farklı bir ana bilgisayar bağlantı noktası eşleyin, örneğin `-p 8080:8000`, ve bunun yerine `http://localhost:8080/canvas` adresini açın.

> **Not:** İlk başlatma, konteyner içinde Agent Server ortamını oluşturduğundan, arka ucun sağlıklı olarak raporlanmasından önce birkaç dakika sürebilir.

`.openhands` bağlantısı, LLM profilinizi, MCP sunucularınızı ve otomasyonlarınızı konteyner yeniden başlatmaları arasında kalıcı hale getirir.
Bu kılavuzun geri kalanı, tarayıcınızdaki `http://localhost:8000/canvas` adresindeki Agent Canvas kullanıcı arayüzü üzerinden her şeyi yapılandırır.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->
## 4. UI'da Yerel LLM'i Yapılandırın

İlk açılışta Agent Canvas bir onboarding akışı açar.
Bu akışta:

1. Aracı olarak **OpenHands** seçili kalsın ve **Next** düğmesine tıklayın.
2. **Set up your LLM** adımında, **Advanced** seçeneğini seçin.
3. **Authentication** ayarını **API key** olarak bırakın.
4. **Custom Model** alanını `openai/Qwen3.6-35B-A3B-GGUF` olarak ayarlayın.
5. **Base URL** alanını `http://127.0.0.1:13305/api/v1` olarak ayarlayın.
6. **API Key** için `lemonade-local` gibi boş olmayan herhangi bir yer tutucu değer girin. Lemonade gerçek bir anahtar gerektirmez, ancak OpenHands istemcisinin gönderecek bir değere ihtiyacı vardır.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server konteyner içinde çalıştığından, **Base URL** alanını `http://127.0.0.1:13305/api/v1` yerine `http://host.docker.internal:13305/api/v1` olarak ayarlayın.
> Konteyner içinden bakıldığında, `127.0.0.1` konteynerin kendisidir; `host.docker.internal` ise Windows ana bilgisayarında çalışan Lemonade'e ulaşır ve Docker Desktop bu ana bilgisayar adını otomatik olarak sağlar.
<!-- @os:end -->

Bağlantı alanları şöyle görünmelidir.
API key alanı UI tarafından maskelenmiştir.

![Lemonade modeli ve yerel taban URL'si ile Agent Canvas ilk kullanım LLM Advanced ayarları](assets/01-llm-advanced-settings.png)

Ardından **All** öğesini seçin ve ek yerel model alanlarını ayarlayın:

1. **Custom Tokenizer** alanına gidin ve `Qwen/Qwen3.6-35B-A3B` olarak ayarlayın.
2. **LiteLLM Extra Body** alanına gidin ve `{"enable_thinking": true}` olarak ayarlayın.
3. **Next** düğmesine tıklayın.

![Qwen özel tokenizer'ı ile Agent Canvas ilk kullanım LLM All sekmesi](assets/02-llm-all-tokenizer-settings.png)

![LiteLLM extra body yapılandırılmış Agent Canvas ilk kullanım LLM All sekmesi](assets/03-llm-all-extra-body-settings.png)

LLM ayarları şunları göstermelidir:

| Alan | Değer |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/` öneki, LiteLLM'e Lemonade uç noktasına karşı OpenAI uyumlu istek biçimlendirmesi kullanmasını söyler.
Özel tokenizer, GGUF modeli için orijinal Hugging Face tokenizer'ıdır; bu, OpenHands'in yerel model sunucusunun gördüğü aynı chat-template token'larını saymasını sağlar.
Mevcut ilk kullanım LLM formu condenser ayarlarını göstermez.
Agent Canvas derlemeniz daha sonra **Settings > LLM** altında condenser ayarlarını gösteriyorsa, `llm_summarizing` kullanın ve maksimum token sayısını Lemonade bağlam penceresinin altında, örneğin `56000` olarak ayarlayın.

## 5. GitHub ve Slack MCP Sunucularını Kurun

Agent Canvas UI'da, aracıya GitHub ve Slack için araçlar sağlayan MCP sunucularını eklemek üzere **Customize** (veya **Settings > MCP**) bölümünü açın.
Token değerleri yalnızca yerel Agent Server'ınıza gönderilir ve şifrelenmiş ayarlar olarak saklanır.

<!-- @os:windows -->
> **Windows (Docker):** Aşağıdaki `npx` MCP sunucu komutları, zaten Node.js içeren konteyner içinde çalışır, bu yüzden ana bilgisayara ekstra bir şey kurulmaz.
> `.openhands` bağlandığından, MCP sunucuları ve token'ları konteyner yeniden başlatmaları arasında kalıcı kalır.
<!-- @os:end -->

### GitHub MCP sunucusu

Şu ayarlarla yeni bir MCP sunucusu ekleyin:

| Alan | Değer |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = GitHub token'ınız |

Özetlemek istediğiniz depoya okuma erişimi olan bir GitHub token'ı kullanın.

### Slack MCP sunucusu

İkinci bir MCP sunucusunu şu ayarlarla ekleyin:

| Alan | Değer |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = özet kanalınızın ID'si |

`SLACK_CHANNEL_IDS` değerini özet kanalı ID'sine (`SLACK_DIGEST_CHANNEL` ile aynı değer) ayarlayın, böylece aracının her Slack kanalını taraması gerekmez.

Her iki sunucuyu ekledikten sonra, bağlantı kurduğunu ve araçları tanıttığını doğrulamak için her birinde **Test** düğmesini kullanın.
GitHub sunucusu GitHub araçlarını listelemeli, Slack sunucusu da Slack araçlarını listelemelidir.

![GitHub ve Slack sunucuları kurulmuş Agent Canvas MCP sayfası](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Özet Otomasyonunu Oluşturun

Agent Canvas UI'da, **Automations** sayfasını açın ve yeni bir otomasyon oluşturun:

1. **Create automation** seçin ve **Prompt preset** türünü seçin.
2. **Name** alanını `GitHub Development Digest to Slack` olarak ayarlayın.
3. **Prompt** alanını, depo ve kanal yer tutucularını kendi değerlerinizle değiştirerek aşağıdaki metin olarak ayarlayın:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. **Trigger** alanını `0 9 * * 1-5` (hafta içi saat 9:00) programıyla **Cron** olarak ayarlayın ve **Timezone** alanını kendi saat diliminize, örneğin `America/New_York` olarak ayarlayın.
5. **Timeout** alanını `900` saniye olarak ayarlayın.
6. Otomasyonu kaydedin.

Otomasyon ayrıntı sayfası, yeni otomasyonu cron tetikleyicisi ve oluşturulan prompt-preset giriş noktasıyla birlikte gösterir.

![Oluşturma sonrası Agent Canvas otomasyon ayrıntı sayfası](assets/05-automation-created.png)
## 7. Otomasyonu Test Edin

Agent Canvas UI'daki otomasyon ayrıntı sayfasından:

1. Otomasyonu hemen bir kez çalıştırmak için **Run now** (veya **Dispatch**) düğmesine tıklayın.
2. Aynı sayfadaki çalıştırma listesini izleyin. En son çalıştırma `COMPLETED` durumuna geçmelidir.
3. Hedef Slack kanalınızı açın. Oluşturulan özeti içermelidir.

Cron zamanlamasının tetiklenmesini beklemenize gerek yoktur—**Run now**, zamanlamaya güvenmeden önce istemi, MCP bağlantılarını ve Slack'e gönderimin çalıştığını doğrulayabilmeniz için isteğe bağlı bir çalıştırma tetikler.

![Agent Canvas otomasyon çalıştırması başarıyla tamamlandı](assets/06-automation-run-completed.png)

![Oluşturulan OpenHands özetini gösteren Slack kanalı](assets/07-slackbot-message.png)

## Sorun Giderme

<!-- @os:windows -->
- **Docker 8000 portu zaten kullanımda:** farklı bir host portu eşleyin, örneğin `docker run ... -p 8080:8000 ...`, ve `http://localhost:8080/canvas` adresini açın.
- **`docker pull` bir kimlik bilgisi hatasıyla başarısız olur** (örneğin, "A specified logon session does not exist"): pull işlemini etkileşimli bir Windows oturumundan çalıştırın veya imajı önceden çekin. İmaj herkese açıktır, bu nedenle `docker login` gerekmez.
- **Arayüz yükleniyor ancak arka uç sağlıksız:** ilk başlatma, konteyner içinde Agent Server ortamını oluşturur. Bir dakika bekleyip yenileyin, ardından ilerlemeyi görmek için `docker logs <container>` komutunu kontrol edin.
- **Agent Canvas, konteynerden Lemonade'e ulaşamıyor:** LLM **Base URL** değerini `http://host.docker.internal:13305/api/v1` olarak ayarlayın (`127.0.0.1` değil) ve Lemonade'in Windows ana bilgisayarında çalıştığını doğrulayın.
<!-- @os:end -->

- **Lemonade çalışmıyor:** 1. adımdaki `lemonade run "${LEMONADE_MODEL}"` komutuyla yeniden başlatın, ardından sağlık kontrolünü tekrar çalıştırın.
- **`npm install -g` bir izin hatasıyla başarısız olur:** Linux veya WSL üzerinde, kullanıcıya ait bir genel npm dizini yapılandırın, bunu kabuk başlangıç dosyanıza ekleyin, ardından Agent Canvas'ı tekrar kurun:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

`zsh` kullanıyorsanız, aynı `export PATH=...` satırını `~/.bashrc` yerine `~/.zshrc` dosyasına ekleyin.
- **Agent Canvas, `custom_tokenizer` ayarlandıktan sonra LLM ayarlarını reddediyor:** Agent Server Python ortamına `transformers` kurun, gerekirse Agent Canvas'ı yeniden başlatın ve LLM ayarlarını kaydetmeyi tekrar deneyin. `custom_tokenizer` ayarlandığında OpenHands, tokenizer sohbet şablonunu yüklemek için Transformers'a ihtiyaç duyar.
- **Agent Canvas Lemonade'e ulaşamıyor:** `curl -fsS "${LEMONADE_BASE_URL}/health"` komutunu doğrulayın ve ilk kullanımdaki LLM formuna veya **Settings > LLM** bölümüne girilen taban URL'nin çalışan yerel uç noktayla veya HTTPS tüneliyle eşleştiğini onaylayın.
- **LLM ayarları kaydedilmedi:** değerleri girdikten sonra **Next** düğmesine tıkladığınızdan emin olun. Değerlerin kalıcı olduğunu doğrulamak için **Settings > LLM** bölümünü yeniden açın.
- **GitHub MCP özel depoları göremiyor:** GitHub belirtecinin hedef depoya okuma erişimine sahip olduğunu ve **Customize** içindeki MCP **Test** düğmesinin GitHub araçlarını gösterdiğini doğrulayın.
- **Slack kanalları okuyabiliyor ancak gönderi yapamıyor:** Slack uygulamasını hedef kanala davet edin ve botun `chat:write` iznine sahip olduğunu doğrulayın.
- **Otomasyon çok fazla Slack kanalı listeliyor:** bir Slack kanal kimliği kullanın ve **Customize** içindeki Slack MCP sunucusunda `SLACK_CHANNEL_IDS` ayarını yapın.
- **Otomasyon çalıştırması başarısız oluyor veya bağlamı aşıyor:** Lemonade'in `ctx_size=65536` ile başlatıldığını, OpenHands LLM'de `custom_tokenizer` ayarının yapıldığını doğrulayın ve GitHub sonuç kümeleri 3 ila 5 öğeyle sınırlandırılmış açık bir depo kullanın. Agent Canvas derlemeniz condenser ayarlarını sunuyorsa, condenser maksimum belirteç sayısını Lemonade bağlam penceresinin altında ayarlayın.

## Sonraki Adımlar

- Haftalık, yalnızca sürüm içeren bir özet ekleyin.
- Daha hızlı PR veya push uyarıları için GitHub olay tetiklemeli bir otomasyon ekleyin.
- Aynı özeti Notion, Linear veya başka bir MCP destekli araca yönlendirin.

## Kaynaklar

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server belgeleri](https://lemonade-server.ai/docs)
- [OpenHands extensions deposu](https://github.com/OpenHands/extensions)
- [Model Context Protocol sunucuları](https://github.com/modelcontextprotocol/servers)
- [Slack MCP paketi](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->