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
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Bu kılavuz için en az **32 GB** sistem belleği gereklidir.
<!-- @device:end -->
n8n, uygulamalar ve hizmetler arasında bağlantı kurmanızı sağlayan, görsel düğüm tabanlı bir editöre sahip bir iş akışı otomasyon platformudur.

Bu kılavuz, AP News iş dünyası bölümünü tarayan, önemli başlıkları çıkaran ve sisteminizde yerel olarak çalışan bir LLM kullanarak yatırımcı odaklı bir özet oluşturan, yapay zeka destekli bir finans haberleri özetleyicisinin nasıl kurulacağını öğretir.

## Neler Öğreneceksiniz

- n8n'i nasıl kurup başlatacağınızı
- Önceden hazırlanmış bir iş akışını nasıl içe aktarıp yapılandıracağınızı
- Yerel n8n entegrasyonunu kullanarak Lemonade'e nasıl bağlanacağınızı
- İş akışı düğümlerini ve veri akışını nasıl anlayacağınızı

## Lemonade Nedir?

[Lemonade](https://lemonade-server.ai), AMD donanımı için geliştirilmiş yerel bir LLM sunum platformudur. Tamamen kendi bilgisayarınızda çalışan, OpenAI ile uyumlu bir API sağlar; verileriniz cihazınızdan hiçbir zaman dışarı çıkmaz.

Bu kılavuzda, n8n'in yapay zeka destekli görevler için bağlandığı yerel bir LLM'yi sunmak amacıyla Lemonade'i kullanıyoruz.

n8n, ek bir manuel yapılandırmaya gerek kalmadan birinci sınıf bir entegrasyon sağlayan **yerel bir Lemonade düğümü** (`Lemonade Chat Model`) içerir. Bu sayede yerel LLM'inizi otomasyon iş akışlarına bağlamak son derece kolaydır.

## Bellek Yapılandırmasını Ayarlama
<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Edin
<!-- @require:software-update -->
<!-- @device:end -->
## Yazılım Ön Koşullarının Kurulumu
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
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
  "max_tokens": 32
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

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
## n8n Kurulumu
<!-- @os:windows -->
npm kullanarak n8n'i global olarak yükleyin.

> **Not**: Bazı npm uyarıları görebilirsiniz. Bu beklenen bir durumdur.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **İpucu**: Windows kullanıcılarının, bazı Powershell komutlarını çalıştırabilmek için PowerShell Yürütme İlkesini (Execution Policy) değiştirmesi gerekebilir (örneğin, RemoteSigned veya Unrestricted olarak ayarlamak gibi).
<!-- @os:end -->


<!-- @os:windows -->
> **PATH Sorunu**: `n8n --version` komutu "command not found" hatası veriyorsa, npm global bin dizininizin kullanıcı `PATH`'inde olduğundan emin olun. Genellikle kurulum yolu `C:\Users\<username>\AppData\Roaming\npm` şeklindedir.
> Bunu kullanıcı yoluna ekleyin (Sistem ortam değişkenlerini düzenle > Environment Variables > Edit User Path) ve terminali yeniden başlatın.
<!-- @os:end -->

<!-- @os:linux -->
Şimdi n8n kurulumumuzu konteynerleştirmek için Podman hizmetini kullanacağız.

Aşağıdakini seçtiğiniz bir dizine indirin: [compose.yml](assets/compose.yml)

Bu dizinde şu komutu çalıştırın:
```bash
podman compose up -d
```

Bu işlem n8n'i kurmalı ve kalıcı depolamaya yazmalıdır.

Tarayıcınızın adres çubuğuna `localhost:5678` yazarak n8n'i başlatın.
<!-- @os:end -->

<!-- @os:windows -->
## n8n'i Başlatma

n8n'i terminalden başlatın:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n yerel bir web sunucusu başlatır. Düzenleyiciye erişmek için `'o'` tuşuna basın veya tarayıcınızda `http://localhost:5678` adresini açın.
<!-- @os:end -->
> **İpucu**: n8n kullanırken terminal penceresini açık tutun. Pencereyi kapatmak, sunucunun durmasına neden olabilir.

## Lemonade'i Başlatma

Lemonade, bir modeli çalıştıracak ve n8n'e bağlanacak yerel sunucudur.
<!-- @os:linux -->
Taskbar'daki Lemonade simgesine tıklayarak Lemonade GUI'yi açın. Buradan modellere, arka uçlara göz atabilir ve önceden yüklenmiş modelleri yükleyebilirsiniz.
<!-- @os:end -->

<!-- @os:windows -->
Lemonade Simgesi'ne tıklayarak Lemonade Grafik Arayüzü'nü açın. Uygulamayı açmak için tepsi simgesine sağ tıklayın. Ardından modeller, arka uçlar ekleyebilir ve önceden yüklenmiş modelleri yükleyebilirsiniz.
<!-- @os:end -->
>**İpucu**: Çalışmaya başladıktan sonra Lemonade arayüzüne http://localhost:13305 adresinden de erişebilirsiniz.

Alternatif olarak, bir terminal açıp yüklü modelleri görmek için `lemonade list` komutunu çalıştırabilirsiniz. Ardından şunu çalıştırın:
<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->
## İş Akışını Ayarlama

### Adım 1: n8n'e Kaydolun veya Oturum Açın

n8n'i ilk açtığınızda bir hesap oluşturmanız veya oturum açmanız istenecektir:

1. Tarayıcınızda `http://localhost:5678` adresini açın
2. E-postanızla yeni bir yerel hesap oluşturun veya zaten bir hesabınız varsa oturum açın
3. Oturum açtıktan sonra n8n kontrol panelini göreceksiniz

> **İpucu**: Hesabınızdan kilitli kalırsanız `n8n user-management:reset` komutunu deneyin

### Adım 2: İş Akışını İçe Aktarın

Doğrudan içe aktarabileceğiniz önceden hazırlanmış bir iş akışı sunuyoruz:

1. Şu iş akışı dosyasını indirin: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. İş akışı düzenleyicisini açmak için **Start from Scratch** seçeneğine tıklayın. Alternatif olarak, sol üstteki + düğmesine ve ardından **Add workflow**'a tıklayın.
3. Sağ üstteki **...** menüsüne (üç nokta) tıklayın ve **Import from file** seçeneğini seçin
4. İndirdiğiniz `financial-news-workflow.json` dosyasını seçin
5. İş akışı tuval üzerinde görünecektir
### Adım 3: İş Akışını Anlama

İçe aktarılan iş akışı birbirine bağlı 9 düğüm içerir:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Düğüm | Amaç |
|------|---------|
| **When clicking 'Execute workflow'** | İş akışını başlatmak için manuel tetikleyici |
| **Fetch Financial News Webpage** | `https://apnews.com/business` adresine HTTP GET isteği |
| **Delay to Ensure Page Load** | Sayfa içeriğinin tamamen yüklendiğinden emin olmak için bekleme düğümü |
| **Extract News Headlines & Text** | CSS seçicileri kullanarak manşetleri, editör seçkilerini, öne çıkan haberleri ve bölgesel haberleri çıkaran HTML düğümü |
| **Clean Extracted News Data** | Çıkarılan tüm verileri tek bir metin alanında birleştiren Set düğümü |
| **AI Financial News Summarizer** | Haberleri bir finansal analist sistem istemiyle işleyen AI Agent |
| **Lemonade Chat Model** | Yerel Lemonade sunucunuzda çalışan LLM'e bağlanır |
| **Structured Output Parser** | AI çıktısını yapılandırılmış JSON olarak biçimlendirir |
| **Convert to File** | Özeti indirilebilir bir dosyaya dönüştürür |

### Adım 4: Lemonade Kimlik Bilgilerini Yapılandırma

İş akışını çalıştırmadan önce, onu yerel Lemonade sunucunuza bağlamanız gerekir:

1. n8n'de **Lemonade Chat Model** düğümüne çift tıklayın
2. **Credential to connect with** açılır menüsünden **Create New Credential** seçeneğini seçin
3. Aşağıdaki tablodaki değerleri girin ve kaydet düğmesine tıklayın.
4. Lemonade Server'da yüklediğiniz ilgili modeli seçin.

  | Alan | Değer |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Not**: Test etmeden önce, Lemonade sunucusunun çalıştığını doğrulamak için bir terminalde `lemonade status` komutunu çalıştırın.
<!-- @device:halo_box -->
> Bu iş akışı GPT-OSS-120B kullanır ve bu model Lemonade'de önceden yüklenmiştir. Bunu Lemonade Chat Model düğümü ayarlarında yüklü olan başka modellerle değiştirebilirsiniz.
<!-- @device:end -->

### Adım 5: İş Akışını Test Etme

1. Lemonade'in bir model yüklü olarak çalıştığından emin olun
2. Tuvalin alt orta kısmındaki **Execute workflow** düğmesine tıklayın
3. Her düğümün soldan sağa doğru çalışmasını izleyin—tamamlandığında yeşile döner
4. Oluşturulan özeti alt bölmede görmek için **AI Financial News Summarizer** düğümüne çift tıklayın.
5. İlgili metin dosyasını alt bölmede indirmek için **Convert to File** düğümüne çift tıklayın.

## AI Agent'ı Anlama

AI Financial News Summarizer, finansal analiz için tasarlanmış bir sistem istemi kullanır:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agent, temizlenmiş haber verilerini alır ve piyasa duyarlılığını içeren yapılandırılmış bir özet üretir.

### İş Akışınızı Kaydetme

Üstteki iş akışı adına tıklayın ve isterseniz yeniden adlandırın. İş akışları çalışırken otomatik olarak kaydedilir.

## Sonraki Adımlar

- **Otomasyonu zamanlayın**: Günlük çalıştırmak için Manual Trigger'ı bir **Schedule Trigger** ile değiştirin
- **Bildirim gönderin**: Özetleri almak için bir **Discord**, **Slack** veya **Email** düğümü ekleyin
- **Farklı modeller deneyin**: Farklı LLM'lerle denemeler yapmak için Lemonade Chat Model düğümündeki modeli değiştirin
- **Çıkarımı özelleştirin**: Farklı haber bölümlerini hedeflemek için HTML Extract düğümünün CSS seçicilerini değiştirin
- **Farklı arka uçlar deneyin**: n8n ayrıca [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio ve diğer yerel LLM arka uçlarını da destekler

### n8n Şablonlarını Keşfedin

n8n'de yüzlerce önceden oluşturulmuş iş akışı şablonu bulunur. Resmi şablon kütüphanesine göz atın:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

İçe aktarıp özelleştirebileceğiniz iş akışlarını bulmak için "AI", "LLM" veya "automation" araması yapın.

Daha fazla bilgi için [n8n Documentation](https://docs.n8n.io/) sayfasına göz atın.

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