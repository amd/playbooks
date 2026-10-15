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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Genel Bakış

[OpenHands](https://github.com/All-Hands-AI/OpenHands), kod yazabilen, komut çalıştırabilen, web'de gezinebilen ve gerçek bir çalışma alanında dosyaları düzenleyebilen bir yapay zeka yazılım aracısıdır (agent). Bir sohbet penceresinden önerileri kopyalamak yerine, aracıyı bir proje klasörüne yönlendirir ve işi onun yapmasına izin verirsiniz: bir özellik uygulamak, bir hatayı düzeltmek, testler yazmak veya bir kod tabanını açıklamak gibi.

[Agent Canvas](https://github.com/OpenHands/agent-canvas), OpenHands'i çalıştırmak için önerilen tarayıcı arayüzüdür. Tek bir `agent-canvas` komutu, aracı sunucusunu, otomasyon arka ucunu ve web ön yüzünü birlikte başlatır; böylece tarayıcınızdan aracıyla bir sohbet yürütebilirsiniz.

Her şeyi AMD sisteminizde tutmak için aracı, Lemonade Server tarafından sunulan yerel bir modelle konuşur. Lemonade, bu modeli OpenAI uyumlu bir API üzerinden sunar; böylece Agent Canvas onu diğer OpenAI tarzı uç noktalar gibi yapılandırabilirken model, kodunuz ve sohbet bağlamı makinenizde kalır.

Bu kılavuzda, yerel bir model başlatacak, Agent Canvas'ı başlatacak, onu bu modele yönlendirecek ve gerçek bir proje klasöründe ilk kodlama görevinizi çalıştıracaksınız.

## Neler Öğreneceksiniz

- Lemonade Server'ı nasıl başlatacağınızı ve yerel bir modelin sohbet isteklerine yanıt verdiğini nasıl doğrulayacağınızı
- Agent Canvas'ı npm paketinden nasıl kuracağınızı ve başlatacağınızı
- Agent Canvas'ı LLM olarak yerel bir Lemonade modelini kullanacak şekilde nasıl yapılandıracağınızı
- Bir OpenHands sohbeti nasıl başlatacağınızı ve aracının bir çalışma alanında dosyaları düzenlemesini ve komutları çalıştırmasını nasıl izleyeceğinizi
- Aracının neyi değiştirdiğini nasıl inceleyeceğinizi ve takip mesajlarıyla onu nasıl yönlendireceğinizi

## Temel Kavramlar

| Kavram | Nedir | Bu kılavuzdaki yeri |
| --- | --- | --- |
| Lemonade Server | AMD donanımı için oluşturulmuş, OpenAI uyumlu bir API sunan yerel bir LLM sunum platformu. Verileriniz asla makinenizden çıkmaz. | Aracıyı çalıştıran modeli barındırır. |
| OpenHands | Dosyaları okuyan ve düzenleyen, kabuk komutları çalıştıran ve bir çalışma alanı içinde web'de gezinen bir yapay zeka yazılım aracısı. | Sohbet üzerinden yönettiğiniz aracı. |
| Agent Canvas | OpenHands sohbetlerini çalıştıran ve araç çağrılarını ile dosya değişikliklerini gösteren tarayıcı arayüzü ve arka uç. | Yığını başlatır ve sohbetinize ev sahipliği yapar. |
| Çalışma Alanı | Aracının okumasına ve değiştirmesine izin verilen proje klasörü. | Aracının düzenlemelerinin ve komutlarının hedefi. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Kodlama aracısı iş akışları daha büyük bir model ve bağlam penceresinden faydalanır. En az 32 GB sistem belleği kullanın ve daha büyük GGUF modelleri için 64 GB veya daha fazlasını tercih edin.
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

Şunlara ihtiyacınız var:

- Aşağıdaki modeli sunmaya hazır, kurulmuş bir Lemonade Server.

<!-- @os:linux -->
- Node.js 22.12 veya üstü ve `npm` (`agent-canvas` CLI tarafından kullanılır).
- Agent Canvas'ın aracı sunucusu ortamını yönetmek için kullandığı Python paket yöneticisi `uv`. Sisteminizde zaten yoksa, Agent Canvas'ı başlatmadan önce [uv kurulum kılavuzundan](https://docs.astral.sh/uv/getting-started/installation/) kurun.
<!-- @os:end -->

<!-- @os:windows -->
- Kurulu ve çalışır durumda [Windows için Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/). Windows'ta, Agent Canvas yığını, Node.js, `uv` ve `@openhands/agent-canvas` paketini içeren yayınlanmış Docker imajından çalışır; bu nedenle bunları ana bilgisayara kurmanız gerekmez.
<!-- @os:end -->

- Üzerinde çalışılacak bir proje klasörü. Bu, aracının üzerinde çalışmasını istediğiniz herhangi bir yerel git deposu veya kod dizini olabilir.

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. Lemonade Server'ı Başlatma

Modeli Lemonade CLI'dan başlatın:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Donanımınıza uygun bir model seçin.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) güçlü bir kodlama modelidir ancak büyük bir bellek havuzu gerektirir. Cihazınızın belleği veya GPU VRAM'i sınırlıysa, bunun yerine Lemonade model kitaplığından daha küçük bir GGUF modeli seçin ve bu kılavuz boyunca o model kimliğini kullanın.

> **Not:** İlk `lemonade run` çalıştırması, model henüz mevcut değilse onu indirir; bu, model boyutuna ve bağlantınıza bağlı olarak biraz zaman alabilir.

Lemonade, OpenAI uyumlu bir API'yi şu adreste sunar:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Yerel Modeli Doğrulama

Lemonade'in seçilen modeli sunabildiğini doğrulayın:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Ardından küçük bir sohbet isteği gönderin:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Bu bir `choices` dizisi döndürüyorsa, Lemonade Agent Canvas için hazırdır.

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
model_id = "${lemonade_model}"

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
PY

body='{
  "model": "${lemonade_model}",
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
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
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
## 3. Agent Canvas'ı Kurun ve Başlatın

<!-- @os:linux -->
Yayınlanan Agent Canvas paketini global olarak kurun:

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

Ardından tüm yığını bir terminalden başlatın:

```bash
agent-canvas
```

Agent Canvas varsayılan olarak `http://localhost:8000` adresinde başlar. Bu
URL'yi tarayıcınızda açın. Port özel bir değer değildir — eğer 8000 zaten
kullanımdaysa, Agent Canvas'ı başlatırken `--port` (veya `-p`) ile herhangi
boş bir port belirtebilirsiniz:

```bash
agent-canvas --port 3000
```

Ardından bunun yerine `http://localhost:3000` adresini açın. Varsayılan yerel
backend, ana ekranda sağlıklı olarak görünmelidir.

`agent-canvas` komutu; agent sunucusunu, otomasyon backend'ini ve web
frontend'ini birlikte başlatır. OpenHands'i yerel olarak çalıştırmak için
yalnızca bu tek komuta ihtiyacınız vardır.

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
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
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Windows'ta, yayınlanan Agent Canvas container görüntüsünü Docker Desktop ile
çalıştırın. Bu görüntü, Agent Server, otomasyon backend'i ve web frontend'ini
bir arada barındırır; bu nedenle ana makineye Node.js, `uv` veya CLI'ı
kurmanız gerekmez.

Öncelikle, container'ın bağlayacağı yapılandırma ve çalışma alanı klasörlerini
oluşturun:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Yayınlanan görüntüyü indirin (herkese açıktır, giriş yapmanız gerekmez):

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

Tarayıcınızda `http://localhost:8000/canvas` adresini açın. 8000 numaralı port
zaten kullanımdaysa, farklı bir ana makine portu eşleyin, örneğin
`-p 8080:8000`, ve bunun yerine `http://localhost:8080/canvas` adresini açın.

> **Not:** İlk başlatma, container içinde Agent Server'ı başlattığından,
> backend'in sağlıklı olarak raporlanması bir veya iki dakika sürebilir.

`.openhands` bağlantısı, LLM profilinizi ve ayarlarınızı container yeniden
başlatmaları arasında kalıcı hale getirir. Bu kılavuzun geri kalanı, her şeyi
tarayıcınızdaki Agent Canvas kullanıcı arayüzü üzerinden yapılandırır.

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
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

## 4. Yerel LLM'i Yapılandırın

İlk başlatmada, Agent Canvas bir tanıtım akışı açar. Bu akışta:

1. **OpenHands**'in agent olarak seçili kalmasına izin verin ve **Next**'e
   tıklayın.
2. **Set up your LLM** ekranında **Advanced**'i seçin.
3. **Authentication**'ı **API key** olarak bırakın.
4. **Custom Model**'i `openai/Qwen3.6-35B-A3B-GGUF` olarak ayarlayın.
5. **Base URL**'i `http://127.0.0.1:13305/api/v1` olarak ayarlayın.
   <!-- @os:windows -->
   > Windows'ta yığın bir container içinde çalışır ve bu container ana makineye
   > `127.0.0.1` üzerinden erişemez. Bunun yerine
   > `http://host.docker.internal:13305/api/v1` kullanın, böylece
   > container'daki agent, Windows ana makinesinde çalışan Lemonade'e
   > ulaşabilir.
   <!-- @os:end -->
6. **API Key** için, `lemonade-local` gibi boş olmayan herhangi bir yer
   tutucu değer girin. Lemonade gerçek bir anahtar gerektirmez, ancak
   OpenHands istemcisinin göndermesi gereken bir değer vardır.
7. **Next**'e tıklayın.

Tamamlanmış Advanced ayarları şu şekilde görünmelidir. API anahtarı alanı
kullanıcı arayüzü tarafından maskelenmiştir.

![Lemonade modeli ve yerel base URL ile Agent Canvas ilk kullanım LLM Advanced ayarları](assets/01-llm-advanced-settings.png)

Agent Canvas bu değerleri bir LLM profili olarak kaydeder. Sürümünüz bu
profile bir isim vermenizi isterse, `lemonade-local` gibi boşluk içermeyen
bir isim kullanın. Daha sonra modelleri değiştirirseniz, **Settings > LLM**'i
açın ve aynı Advanced alanlarını güncelleyin. Kaydedilmiş profiller arasında
sohbet giriş alanından `/model` komutuyla geçiş yapabilirsiniz.

## 5. Bir Çalışma Alanı Açın

Agent yalnızca sizin seçtiğiniz bir çalışma alanı içindeki dosyaları
okuyabilir ve değiştirebilir. Bir göreve başlamadan önce, Agent Canvas'ı
proje klasörünüze yönlendirin:

1. Ana ekrandan **Open Workspace**'i seçin.
2. Projenizi içeren klasörü seçin (örneğin, agent'ın üzerinde çalışmasını
   istediğiniz bir git deposu).
3. O çalışma alanında yeni bir konuşma başlatın.

Agent'ın yaptığı her şey—dosyaları okuma, komutları çalıştırma, kodu
düzenleme—o çalışma alanıyla sınırlıdır.

![Tanıtımdan sonra Agent Canvas ana ekranı](assets/02-agent-canvas-home.png)

## 6. İlk Kodlama Görevinizi Çalıştırın

Çalışma alanı açıkken ve yerel LLM seçiliyken, sohbete somut bir görev yazın.
İyi bir ilk görev küçük ve doğrulanabilir olmalıdır, örneğin:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Konuşma zaman çizelgesini izleyin. OpenHands şunları yapacaktır:

- Düzeni anlamak için çalışma alanını okur.
- İstenen fonksiyonu ve test bloğunu içeren `hello.py` dosyasını oluşturur.
- İsteğe bağlı olarak çıktıyı doğrulamak için `python3 hello.py` komutunu
  çalıştırır.
- Yaptıklarını ve varsa komut çıktısını sohbette bildirir.

Yeni dosyanın çalışma alanında göründüğünü görmelisiniz ve agent'ın son
mesajı yaptığı değişikliği açıklamalıdır. Bu, en önemli andır: agent projenizin
klasöründe gerçek kod yazmış ve çalıştırmıştır.

## 7. Agent'ı Gözden Geçirin ve Yönlendirin

Agent bir adımı tamamladıktan sonra, bir sonraki adımı kabul etmeden önce
çalışmasını gözden geçirin:

- **Dosya değişiklikleri**: agent'ın tam olarak neyi eklediğini, değiştirdiğini
  veya sildiğini görmek için çalışma alanı dosya tarayıcısını veya agent'ın
  diff görünümünü kullanın.
- **Komut çıktısı**: agent'ın çalıştırdığı herhangi bir komutu genişleterek
  stdout, stderr ve çıkış kodunu görün.
- **Devam eden adımlar**: sonuç istediğiniz gibi değilse, aynı konuşmada bir
  düzeltmeyle yanıt verin. Agent önceki bağlamı korur ve aynı dosyalar
  üzerinde yinelemeye devam eder.

Örneğin, test beklenen selamlamayı yazdırmadıysa, şu şekilde yanıt verin:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent, dosyayı yeniden okuyacak, komutu çalıştıracak, sorunu teşhis edecek ve
dosyayı tekrar düzenleyecektir—hepsi aynı konuşma içinde.
## Sorun Giderme

<!-- @os:linux -->
- **`agent-canvas` PATH üzerinde değil:** `npm install -g @openhands/agent-canvas`
  komutuyla yeniden yükleyin ve `agent-canvas` yeni bir terminalden
  başlatılabilmeden önce npm genel ikili dosya dizininin PATH üzerinde
  olduğunu doğrulayın.
- **`npm install -g` izin hatasıyla başarısız oluyor:** kullanıcıya ait bir
  genel npm dizini yapılandırın, ardından terminali yeniden açıp Agent Canvas'ı
  tekrar yükleyin.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` eksik:** [uv kurulum kılavuzundan](https://docs.astral.sh/uv/getting-started/installation/)
  yükleyin. Agent Canvas, ajan sunucusunun Python ortamını yönetmek için
  `uv` kullanır.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` veya `docker run` bağlanamıyor:** Docker Desktop'ın çalıştığından
  (sistem tepsisindeki balina simgesi) ve motorun başlatma işlemini
  tamamladığından emin olun. `docker version` hem bir Client hem de bir Server
  bölümü yazdırmalıdır.
- **Konteyner başlıyor ancak arka uç asla sağlıklı hale gelmiyor:** ilk
  başlatma, konteyner içinde Agent Server'ı başlatır; bir iki dakika bekleyin,
  ardından hataları görmek için `docker logs <container>` komutunu kontrol
  edin.
- **Konteyner Lemonade'e erişemiyor:** konteyner, ana bilgisayara
  `host.docker.internal` üzerinden erişir. Lemonade'in Windows ana
  bilgisayarında `lemonade status` ile hizmet verdiğini doğrulayın ve LLM'i
  yapılandırırken Base URL olarak `http://host.docker.internal:13305/api/v1`
  kullanın.
<!-- @os:end -->

- **Arayüz yükleniyor ancak arka uç sağlıksız görünüyor:** ajan sunucusunun
  başlamayı tamamlaması için bir iki dakika bekleyin, ardından yenileyin.
  Sağlıksız kalmaya devam ederse yığını yeniden başlatın ve hataları görmek
  için günlükleri kontrol edin.
- **Lemonade sohbet istekleri bağlantı hatasıyla başarısız oluyor:**
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` komutunun başarılı
  olduğunu ve Lemonade'in modeli hâlâ `lemonade status` ile sunduğunu
  doğrulayın.
- **Ajan bir bağlam uzunluğu veya belirteç sınırı mesajıyla hata veriyor:**
  ajanın aşırı büyük bir geçmiş taşımaması için yeni bir konuşma başlatın.
  Bu durum tekrar ederse, bellek uygunsa Lemonade'i varsayılan 65536 değerinden
  daha büyük bir `ctx_size` ile yeniden başlatın (örneğin `ctx_size=131072`).
- **Ajan düşük kaliteli veya eksik düzenlemeler üretiyor:** Lemonade'de daha
  büyük bir modele geçin veya ajana daha küçük, daha somut bir görev verip
  bir sonraki değişikliği istemeden önce bitirmesine izin verin.

## Sonraki Adımlar

- Aynı çalışma alanında birim test dosyası eklemek veya bilinen bir hatayı
  düzeltmek gibi daha büyük bir görevi deneyin ve değişikliği tutmadan önce
  ajanın diff'ini inceleyin.
- Ajanın çalışırken sorunları okuyabilmesi veya güncellemeleri
  paylaşabilmesi için **Customize** altında GitHub veya Slack gibi bir MCP
  sunucusu bağlayın.
- Birkaç LLM profili kaydedin (hızlı küçük bir model ve daha güçlü büyük bir
  model) ve konuşma sırasında `/model` komutuyla aralarında geçiş yapın.
- Tekrarlayan geliştirme döngülerini zamanlanmış veya olay tetiklemeli ajan
  çalıştırmalarına dönüştürmek için
  [OpenHands otomasyonlarına](https://docs.openhands.dev/openhands/usage/automations/overview) geçin.

## Kaynaklar

- [OpenHands belgeleri](https://docs.openhands.dev/)
- [Agent Canvas genel bakış](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas kurulumu](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM profilleri ve model yapılandırması](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server belgeleri](https://lemonade-server.ai/docs)

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