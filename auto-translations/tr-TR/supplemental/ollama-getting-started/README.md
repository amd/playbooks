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

Ollama, büyük dil modellerini yerel olarak çalıştırmak için popüler ve hafif bir araçtır. Model indirme, nicemleme ve sunma işlemlerini basit bir komut satırı arayüzü ve masaüstü uygulaması arkasında yönetir; böylece dakikalar içinde bir LLM ile sohbet etmeye başlayabilirsiniz.

Bu kılavuz, Ollama'nın kurulumundan GPT-OSS 20B modelinin indirilmesine ve hem terminal hem de masaüstü uygulaması aracılığıyla onunla sohbet etmeye kadar sizi adım adım yönlendirir.

## Öğrenecekleriniz

- Sisteminizde Ollama'yı nasıl kuracağınızı ve başlatacağınızı
- GPT-OSS 20B modelini yerel olarak nasıl indirip çalıştıracağınızı
- CLI kullanarak modellerle nasıl sohbet edeceğinizi
- REST API üzerinden modelleri programatik olarak nasıl sorgulayacağınızı

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme
> **Not**: VS Code kurulu değilse, Ryzen AI Developer Center ile kurabilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarının Kurulumu

<!-- @require:driver -->

### Ollama Kurulumu

<!-- @os:windows -->

1. Yükleyiciyi [ollama.com/download](https://ollama.com/download) adresinden indirin.
2. `.exe` yükleyicisini çalıştırın ve yönergeleri izleyin.
3. Kurulum tamamlandıktan sonra Ollama arka planda bir hizmet olarak çalışır ve terminal, masaüstü uygulaması ile sistem tepsisinden erişilebilir.

Bir terminal açıp aşağıdakini çalıştırarak kurulumu doğrulayın:

```powershell
ollama --version
```

<!-- @test:id=ollama-version-windows timeout=60 hidden=True -->
```powershell
ollama --version
```
<!-- @test:end --> 

Konsola yazdırılan yüklü sürüm numarasını görmelisiniz.
<!-- @os:end -->

<!-- @os:linux -->

Resmi kurulum betiğini çalıştırın:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Kurulumu doğrulayın:

```bash
ollama --version
```

<!-- @test:id=ollama-version-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end --> 

Konsola yazdırılan yüklü sürüm numarasını görmelisiniz.
<!-- @os:end -->

## İlk Modelinizi İndirme

Ollama, konteyner imgelerine benzer bir kayıt defteri (registry) aracılığıyla modelleri yönetir. GPT-OSS 20B'yi indirmek için:

```bash
ollama pull gpt-oss:20b
```

Bu işlem, model ağırlıklarını yerel makinenize indirir (yaklaşık 12 GB). İndirme yalnızca bir kez gerçekleşir; sonraki çalıştırmalarda model diskten yüklenir.

Modelin kullanılabilir olduğunu şu şekilde doğrulayabilirsiniz:

```bash
ollama list
```

Çıktıda `gpt-oss:20b` modelini, boyutu ve son değiştirilme tarihiyle birlikte görmelisiniz.

<!-- @os:windows -->
<!-- @test:id=ollama-list-gpt-oss-20b-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
$list = (ollama list | Out-String)
if (-not $list) { throw "ollama list returned no output" }
if ($list -notmatch 'gpt-oss:20b') { throw "Model gpt-oss:20b is not present in ollama list. Please download it before running this test." }
Write-Host "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-list-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"

cleanup() {
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-list-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

list="$(ollama list)"
if [ -z "$list" ]; then
  echo "ollama list returned no output"
  exit 1
fi
echo "$list" | grep -q 'gpt-oss:20b' || {
  echo "Model gpt-oss:20b is not present in ollama list. Please download it before running this test."
  exit 1
}
echo "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

### Model Adlandırması

Ollama model adları `ad:etiket` biçimini izler. Etiket genellikle parametre sayısını veya nicemleme çeşidini belirtir. Modelleri yönetmek için bazı yararlı komutlar:

| Komut | Açıklama |
|---------|-------------|
| `ollama list` | İndirilen tüm modelleri gösterir |
| `ollama pull <model>` | Bir modeli çalıştırmadan indirir |
| `ollama rm <model>` | Disk alanı boşaltmak için bir modeli kaldırır |
| `ollama show <model>` | Model meta verilerini ve parametrelerini görüntüler |

## Terminalden Sohbet Etme

Komut satırından doğrudan etkileşimli bir sohbet oturumu başlatın:

```bash
ollama run gpt-oss:20b
```

Ollama, modeli belleğe yükler ve sizi bir istem ekranına yönlendirir. Bir şeyler sormayı deneyin:

```
>>> What is the capital of France and why is it historically significant?
```

Model, yanıtını terminalde doğrudan belirteç belirteç (token-by-token) akış olarak verir. Oturumdan çıkmak için `/bye` yazın veya `Ctrl+D` tuşlarına basın.

> **İpucu**: İlk çalıştırma, modeli belleğe yüklemek için birkaç saniye sürer. Model bellekte kaldığı için aynı oturum içindeki sonraki istemler çok daha hızlı yanıt verir.

<!-- @os:windows -->
## Masaüstü Uygulamasından Sohbet Etme

Ollama ayrıca modellerinizle etkileşim kurmak için temiz bir sohbet arayüzü sunan bir masaüstü uygulamasıyla birlikte gelir.

Başlat menüsünden **Ollama**'yı açın veya sistem tepsisindeki Ollama simgesine tıklayıp **Open Ollama**'yı seçin.

Uygulama açıldıktan sonra:

1. Kenar çubuğundan **New Chat**'e tıklayın.
2. Sohbet giriş alanının sağ alt köşesindeki model açılır menüsünden **gpt-oss:20b**'yi seçin.
3. Bir mesaj yazın ve sohbete başlamak için Enter'a basın.

<p align="center">
  <img src="assets/ollama_app.png" alt="Ollama desktop app chatting with gpt-oss:20b" width="600"/>
</p>

Masaüstü uygulaması, önceki sohbetlerinize kolayca dönebilmeniz için konuşma geçmişinizi kenar çubuğunda tutar.
<!-- @os:end -->

## REST API Kullanımı

Kurulumdan sonra Ollama arka planda bir hizmet olarak çalışır ve modelleri kendi uygulamalarınıza ve betiklerinize entegre etmek için `http://localhost:11434` adresinde bir REST API sunar.

<!-- @os:windows -->
<!-- @test:id=ollama-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$p = $null
$startedHere = $false
$tmpShow = $null
$tmpGenerate = $null
$tmpChat = $null
$venv = "$PWD\ollama-env-ci"
$pythonSmoke = "$PWD\ollama_python_smoke.py" 

function Wait-OllamaApi {
  param( [int]$MaxAttempts = 120 )
  $resp = $null
  for ($i = 0; $i -lt $MaxAttempts; $i++) {
    $resp = curl.exe -s --max-time 2 http://127.0.0.1:11434/api/tags
    if ($LASTEXITCODE -eq 0 -and $resp) { return $resp }
    Start-Sleep -Seconds 1
  }
  return $null
}

try {
  # If Ollama API is not already up, start it.
  $tagsJson = Wait-OllamaApi -MaxAttempts 5
  if (-not $tagsJson) {
    $p = Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow -PassThru
    $startedHere = $true
    $tagsJson = Wait-OllamaApi -MaxAttempts 120
  }
  if (-not $tagsJson) { throw "Ollama API not ready on http://127.0.0.1:11434" }
  Write-Host "OK: Ollama API is responding on http://127.0.0.1:11434"

  # /api/tags must include gpt-oss:20b
  $tags = $tagsJson | ConvertFrom-Json
  $model = $tags.models | Where-Object { $_.name -eq "gpt-oss:20b" } | Select-Object -First 1
  if (-not $model) { throw "Model gpt-oss:20b is not present in /api/tags. Please download it before running this test." }
  Write-Host "OK: gpt-oss:20b is present in /api/tags"

  # /api/show should return model metadata
  $showBody = @{ name = "gpt-oss:20b" } | ConvertTo-Json
  $tmpShow = Join-Path $env:TEMP "ollama-show-body.json"
  [System.IO.File]::WriteAllText($tmpShow, $showBody, [System.Text.UTF8Encoding]::new($false))
  $showOut = curl.exe -sS --fail-with-body --max-time 60 http://127.0.0.1:11434/api/show `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpShow"
  if (-not $showOut) { throw "Empty response from /api/show" }
  $showJson = $showOut | ConvertFrom-Json
  if (-not $showJson.details) { throw "/api/show did not return model details for gpt-oss:20b" }
  Write-Host "OK: /api/show returned model details"

  # CLI inference smoke
  $cliOut = & ollama run gpt-oss:20b "Reply with exactly OK"
  if (-not $cliOut) { throw "ollama run returned empty output" }
  $cliText = ($cliOut | Out-String).Trim()
  if ($cliText -notmatch '(^|\s)OK(\s|$)') { throw "ollama run did not return OK. Output was: $cliText" }
  Write-Host "OK: ollama run inference works"

  # /api/generate smoke
  $generateBody = @{
    model  = "gpt-oss:20b"
    prompt = "Reply with exactly OK"
    stream = $false
  } | ConvertTo-Json
  $tmpGenerate = Join-Path $env:TEMP "ollama-generate-body.json"
  [System.IO.File]::WriteAllText($tmpGenerate, $generateBody, [System.Text.UTF8Encoding]::new($false))
  $generateOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/generate `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpGenerate"
  if (-not $generateOut) { throw "Empty response from /api/generate" }
  $generateJson = $generateOut | ConvertFrom-Json
  if (-not $generateJson.response) { throw "/api/generate did not return a response field" }
  if ($generateJson.response.Trim() -ne "OK") { throw "/api/generate expected exactly OK but got: $($generateJson.response)" }
  Write-Host "OK: /api/generate works"

  # /api/chat smoke
  $chatBody = @{
    model = "gpt-oss:20b"
    messages = @(
      @{
        role = "user"
        content = "Reply with exactly OK"
      }
    )
    stream = $false
  } | ConvertTo-Json -Depth 5
  $tmpChat = Join-Path $env:TEMP "ollama-chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/chat `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from /api/chat" }
  $chatJson = $chatOut | ConvertFrom-Json
  $chatText = $chatJson.message.content
  if (-not $chatText) { throw "/api/chat did not return message.content" }
  if ($chatText.Trim() -ne "OK") { throw "/api/chat expected exactly OK but got: $chatText" }
  Write-Host "OK: /api/chat works"

  # Python requests smoke
  if (Test-Path $venv) { Remove-Item -Recurse -Force $venv }
  python -m venv $venv
  $py = Join-Path $venv "Scripts\python.exe"
  & $py -m pip install --upgrade pip
  & $py -m pip install requests
@'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
'@ | Set-Content -Path $pythonSmoke -Encoding UTF8
  & $py $pythonSmoke
}

finally {
  Remove-Item $tmpShow, $tmpGenerate, $tmpChat, $pythonSmoke -Force -ErrorAction SilentlyContinue
  Remove-Item $venv -Recurse -Force -ErrorAction SilentlyContinue
  if ($startedHere) {
    if ($p -and -not $p.HasExited) {
      Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
  }
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-smoke-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"
venv="./ollama-env-ci"
python_smoke="./ollama_python_smoke.py" 

cleanup() {
  rm -f "$python_smoke"
  rm -rf "$venv"
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

export TAGS_JSON="$tags_json"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["TAGS_JSON"])
models = data.get("models", [])
for item in models:
    if item.get("name") == "gpt-oss:20b":
        print("OK: gpt-oss:20b is present in /api/tags")
        sys.exit(0)
print("Model gpt-oss:20b is not present in /api/tags. Please download it before running this test.")
sys.exit(1)
PY

show_out="$(curl -s --max-time 60 http://127.0.0.1:11434/api/show \
  -H "Content-Type: application/json" \
  -d '{"name":"gpt-oss:20b"}' || true)"
if [ -z "$show_out" ]; then
  echo "Empty response from /api/show"
  exit 1
fi
export SHOW_OUT="$show_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["SHOW_OUT"])
if not data.get("details"):
    print("/api/show did not return model details for gpt-oss:20b")
    sys.exit(1)
print("OK: /api/show returned model details")
PY

cli_out="$(ollama run gpt-oss:20b "Reply with exactly OK" || true)"
if [ -z "$cli_out" ]; then
  echo "ollama run returned empty output"
  exit 1
fi
export CLI_OUT="$cli_out"
python3 - <<'PY'
import os
import sys
text = os.environ["CLI_OUT"].strip()
if "OK" not in text.split():
    print(f"ollama run did not return OK. Output was: {text}")
    sys.exit(1)
print("OK: ollama run inference works")
PY

generate_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","prompt":"Reply with exactly OK","stream":false}' || true)"
if [ -z "$generate_out" ]; then
  echo "Empty response from /api/generate"
  exit 1
fi
export GENERATE_OUT="$generate_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["GENERATE_OUT"])
text = data.get("response", "")
if not text:
    print("/api/generate did not return a response field")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/generate expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/generate works")
PY

chat_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","messages":[{"role":"user","content":"Reply with exactly OK"}],"stream":false}' || true)"
if [ -z "$chat_out" ]; then
  echo "Empty response from /api/chat"
  exit 1
fi
export CHAT_OUT="$chat_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["CHAT_OUT"])
msg = data.get("message", {})
text = msg.get("content", "")
if not text:
    print("/api/chat did not return message.content")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/chat expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/chat works")
PY

rm -rf "$venv"
python3 -m venv "$venv"
py="$venv/bin/python"
"$py" -m pip install --upgrade pip
"$py" -m pip install requests
cat > "$python_smoke" <<'PY'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
PY
"$py" "$python_smoke"
```
<!-- @test:end --> 
<!-- @os:end -->

### Terminalde Yanıt Oluşturma

<!-- @os:linux -->
```bash
curl http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

Yanıt, modelin çıktısını `response` alanında içeren bir JSON nesnesidir.


### Python Örneği
Artık Ollama API'sini programatik olarak çağırabildiğimize göre, hadi onu Python'dan çağıralım.

#### Terminalde Sanal Ortam Oluşturma

<!-- @os:linux -->
```bash
sudo apt install -y python3-venv
python3 -m venv ollama-env
source ollama-env/bin/activate
pip install requests
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
python -m venv ollama-env
ollama-env\Scripts\activate
pip install requests
```
<!-- @os:end -->
#### Python Dosyası Oluşturma
Aynı dizinde, VS Code veya başka bir düzenleyici kullanarak bir .py dosyası oluşturun ve aşağıdaki kodu içine kopyalayın. Ardından, etkinleştirdiğiniz ortamda `python your_file_name.py` komutuyla dosyayı çalıştırın

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Write a haiku about local AI inference.",
        "stream": False,
    },
)

print(response.json()["response"])
```

### Temel API Uç Noktaları

| Uç Nokta | Yöntem | Amaç |
|----------|--------|---------|
| `/api/generate` | POST | Tek turlu metin üretimi |
| `/api/chat` | POST | Mesaj geçmişiyle çok turlu konuşma |
| `/api/tags` | GET | Kullanılabilir modelleri listeler |
| `/api/show` | POST | Model ayrıntılarını gösterir |
| `/api/pull` | POST | Kayıt defterinden bir model indirir |

Tam API referansı için [Ollama API belgelerine](https://github.com/ollama/ollama/blob/main/docs/api.md) bakın.
## Sonraki Adımlar

- **Farklı modeller deneyin**: Küçük kodlama asistanlarından büyük akıl yürütme modellerine kadar yüzlerce mevcut modeli keşfetmek için [Ollama model kütüphanesine](https://ollama.com/library) göz atın.
- **Özel modeller oluşturun**: Özelleştirilmiş bir deneyim için özel sistem istemleri, sıcaklık ve diğer parametreleri ayarlamak üzere bir [Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) kullanın.
- **API ile geliştirme yapın**: Ollama'yı uygulamalarınıza entegre etmek için [Python](https://github.com/ollama/ollama-python) veya [JavaScript](https://github.com/ollama/ollama-js) istemci kütüphanelerini kullanın.
- **Ön uçlara bağlanın**: Arama, kişilikler ve belge yükleme özellikleriyle zengin bir sohbet arayüzü için Ollama'yı [Open WebUI](https://github.com/open-webui/open-webui) gibi araçlarla birleştirin.

Daha fazla bilgi için [Ollama belgelerine](https://github.com/ollama/ollama/blob/main/README.md) göz atın.