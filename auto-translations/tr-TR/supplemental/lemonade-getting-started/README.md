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

🍋 **Lemonade**, büyük dil modellerini (LLM'ler), görüntü üreticilerini ve ses modellerini doğrudan kendi donanımınızda çalıştırmanızı sağlayan açık kaynaklı, yerel bir yapay zeka sunucusudur. Modelleri endüstri standardı **OpenAI API** aracılığıyla sunar; böylece OpenAI ile çalışan herhangi bir uygulama anında Lemonade ile de çalışabilir. Bu playbook'un sonunda, modelleri makinenizde yerel olarak çalıştırmak için Lemonade'i kullanıyor olacaksınız.

## Neler Öğreneceksiniz

Bu playbook'un sonunda şunları yapabileceksiniz:

* **Lemonade Server'ı yükleme** ve çalıştığını doğrulama.
* Tek bir komutla **bir LLM'i indirme ve onunla sohbet etme**.
* **Web UI'yi keşfetme** ve görü, konuşmadan metne dönüştürme ve görüntü üretimi gibi farklı modaliteleri deneme.
* GPU arka uçları arasında Vulkan ile AMD ROCm™ yazılımı arasında **geçiş yapma**.
* OpenAI uyumlu API'yi kullanarak yerel bir LLM ile çalışan **bir Python uygulaması oluşturma**.
<!-- @device:halo_box,halo,stx,krk -->
* **AMD Ryzen™ AI donanımında Hybrid ve FLM çalıştırma modlarını kullanarak modelleri AMD Neural Processing Unit (NPU) üzerinde çalıştırın.**
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Bellek Yapılandırmasını Ayarlama
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Edin
<!-- @require:software-update -->
<!-- @device:end -->
## Yazılım Ön Koşullarının Kurulumu

Başlamadan önce aşağıdakilere sahip olduğunuzdan emin olun:

- **Windows 11** çalıştıran bir bilgisayar veya desteklenen bir **Linux** dağıtımı (Ubuntu 24.04+, Fedora, Debian)
- Adım 1–7'de kullanılan çalışma zamanı modeli (`Gemma-4-E2B-it-GGUF`, ~3 GB) için **16 GB RAM** önerilir. Adım 6'daki daha büyük kod üretim modelini (`Qwen3.5-35B-A3B-GGUF`, ~20 GB) kullanmak isterseniz **32 GB+** önerilir.
- İndirdiğiniz modellere bağlı olarak **~4–30 GB boş disk alanı**. Bu kılavuzdaki en büyük model yaklaşık 20 GB'tır.
- **Python 3.10–3.13** (Python uygulaması bölümünde kullanılır)
- Bir internet bağlantısı (kablolu veya kablosuz)
<!-- @device:halo_box,halo,stx,krk -->
- [İsteğe bağlı] Modeli NPU üzerinde çalıştırmak istiyorsanız, [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) adresinden yüklenen en güncel sürücüye sahip bir AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 serisi veya Z2 Extreme).
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade-models-gemma-4-e2b,lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
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
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->
---

## Temel Kavramlar — Yerel Yapay Zeka Sunucuları Nasıl Çalışır?

Bir modeli çalıştırmadan önce, bu düzenin *neden* bu şekilde kurulduğunu anlamakta fayda var. Lemonade bir **yerel model sunucusudur**; yapay zeka modellerini belleğe yükleyen ve bunları tıpkı bulut tabanlı bir yapay zeka hizmetinde olduğu gibi HTTP üzerinden uygulamalara sunan bir süreçtir.

### Neden Bir Sunucu?

| Fayda | Sizin İçin Anlamı |
|---------|----------------------|
| **Basitleştirilmiş entegrasyon** | Uygulamalar, donanıma özgü C++ veya Python kütüphaneleriyle uğraşmak yerine tek bir HTTP API ile iletişim kurar. |
| **Paylaşılan modeller** | Tek bir yüklü model aynı anda birden fazla uygulamaya hizmet verebilir; böylece RAM'inizi tüketen yinelenen kopyalar oluşmaz. |
| **Buluttan yerele taşınabilirlik** | OpenAI'nin bulut API'si için yazılmış kod, yalnızca bir URL değiştirilerek Lemonade ile çalışır. |
| **Sorumlulukların ayrılması** | Model yönetimi, akış (streaming) ve hata toleransı sunucu tarafından ele alınır; böylece geliştiriciler uygulamalarına odaklanabilir. |

### OpenAI API Standardı

Lemonade, ChatGPT, Azure OpenAI ve diğer birçok hizmet tarafından kullanılan aynı arayüz olan **OpenAI API**'yi uygular. Konuşma modeli basittir:

| Rol | Kim Konuşuyor |
|------|---------------|
| **system** | Modele verilen talimatlar (kişilik, kısıtlamalar, kullanılabilir araçlar) |
| **user** | İnsandan (veya uygulamadan) modele gönderilen mesajlar |
| **assistant** | Model tarafından üretilen yanıtlar |

Bu, OpenAI'yi destekleyen herhangi bir kütüphane veya uygulamanın, Lemonade Server çalışırken `http://localhost:13305/api/v1` adresine yönlendirilerek Lemonade ile iletişim kurabileceği anlamına gelir.

## Ana Etkinlik — İlk Yerel Yapay Zeka Sohbetiniz

Bir LLM indirip onunla bir sohbet gerçekleştirelim; yapay zekayı tamamen kendi makinenizde çalıştıracağız.

### Adım 1: Bir Modeli İndirin ve Çalıştırın

Lemonade, özenle hazırlanmış bir model kütüphanesiyle gelir. **Gemma-4-E2B-it** ile başlayalım; görsel destek de içeren, yetenekli ve kompakt bir model. Bir terminal açın ve şunu çalıştırın:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Bu tek komut üç şeyi yapar:

1. Model henüz indirilmemişse Hugging Face'ten (~3 GB) **indirir**. (Biraz zaman alabilir)
2. 13305 portunda Lemonade Server işlemini **başlatır**.
3. Modelle sohbet etmeye başlayabilmeniz için Lemonade App'i **açar**.
<!-- @os:windows -->
Windows'ta Lemonade App otomatik olarak başlatılır ve hemen sohbete başlayabilirsiniz. `minimal.msi` paketini kurduysanız, uygulama dahil değildir. Sohbete başlamak için web tarayıcınızı açın ve `http://localhost:13305` adresine gidin.
<!-- @os:end -->

<!-- @os:linux -->
Linux üzerinde, tarayıcınızı açın ve web uygulamasına erişmek için `http://localhost:13305` adresine gidin.
<!-- @os:end -->
Bir soru yazmayı deneyin:

```
What are three fun facts about lemons?
```

Model, sohbet penceresinde doğrudan yanıt verecektir. **Tebrikler! Artık büyük bir dil modelini yerel olarak çalıştırıyorsunuz.**

![Günlükler görüntülenmiş Lemonade Uygulaması](../../dependencies/assets/ChatwithLogs.png)

Lemonade Uygulamasındaki Sunucu Günlükleri (Server Logs) panelinde, her yanıttan sonra modelin performansına ilişkin telemetri verilerini bulabilirsiniz. Örneğin:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Adım 2: Web Arayüzünü ve Farklı Modaliteleri Keşfedin

Lemonade, şunları yapabileceğiniz yerleşik bir web arayüzü içerir:

- **Etkileşim kurun:** Yüklenen modelle tanıdık bir sohbet penceresinde etkileşime geçin
- **Modelleri inceleyin:** Model Manager sekmesinde modellere göz atın
- **Yeni modeller indirin:** Tek tıklamayla yeni modeller indirin

Web arayüzündeki **Model Manager** sekmesini kullanarak modelleri Recipe veya Category'ye göre inceleyebileceğiniz farklı modaliteler arasında geçiş yapmayı deneyin:

1. **Görüntü:** Zaten yüklü olan `Gemma-4-E2B-it-GGUF` modeli görüntü desteğine sahiptir. Sohbet kutusuna bir resim yapıştırın ve modelden resmi tanımlamasını isteyin.
2. **Görüntü oluşturma:** Image kategorisinde, Model Manager'dan `SDXL-Turbo` gibi bir görüntü modeli indirin ve ardından yerel olarak bir görüntü oluşturmak için bir istem yazmak üzere Lemonade Image Generator'ı kullanın.
3. **Ses:** Audio kategorisinde, konuşmadan metne dönüştürme yapabilen `Whisper-Tiny` gibi bir ses modeli indirin. Yerel olarak yazıya dökmek için bir ses kaydı sağlayın. Metinden konuşmaya dönüştürme için Speech kategorisindeki `kokoro-v1` gibi modellerden birini deneyin.

![Lemonade ile Çoklu Modalite](../../dependencies/assets/multi_modality.png)

### Adım 3: Bir Modeli Farklı Bir Arka Uçla Deneyin

Lemonade App'te bir modelin üzerine gelirseniz bir dişli simgesi görürsünüz. Buna tıklamak, istediğiniz arka ucu seçme de dahil olmak üzere model için seçenekler belirlemenize olanak tanır.

Lemonade, varsayılan olarak GPU hızlandırması için Vulkan kullanır. Desteklenen bir AMD ayrık GPU'nuz varsa ROCm'a geçebilirsiniz.

![Lemonade Arka Uç Seçimi](../../dependencies/assets/lemonademodeloptions.png)

Yüklü arka uçlarınızı yönetmek için en soldaki sütunda bulunan arka uç düğmesine tıklayın.

Alternatif olarak, aşağıdaki komutu kullanarak arka ucu belirtebilirsiniz:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Ayrıca `LEMONADE_LLAMACPP` ortam değişkenini şu değerlerle kullanarak varsayılan arka ucunuzu ayarlayabilirsiniz: `vulkan`, `rocm` veya `cpu`.

---

## Daha Derine İnmek — Python ile Yapay Zeka Destekli Bir Uygulama Oluşturun

Yerel bir yapay zeka sunucusunun gerçek gücü, herhangi bir uygulamanın sadece birkaç satır kodla ona bağlanabilmesidir. Bunu kanıtlamak için küçük ama işlevsel bir **çalışma kartı (flashcard) oluşturucu** inşa edelim; burada bir konu verirsiniz, kartları oluşturur ve kendinizi interaktif olarak sınava tabi tutabilirsiniz.

### Adım 4: Sunucuyu Başlatın

Lemonade sunucusunun çalıştığını doğrulayın. Genellikle kurulumdan sonra arka planda otomatik olarak başlar. Doğrulamak için şunu çalıştırın:

```
lemonade status
```

`Server is running on port 13305` gibi bir mesaj görmelisiniz.

Sunucu çalışmıyorsa, Lemonade uygulamasını açarak başlatın. Varsayılan bağlantı noktası olan **13305**'i kullanın (bunu tepsi simgesinden onaylayabilir veya seçebilirsiniz).

### Adım 5: OpenAI Python İstemcisini Kurun

Bir terminalde, aşağıdaki komutları kullanarak bir venv oluşturun ve OpenAI Python İstemcisini kurun:
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### Adım 6: Çalışma Kartı Uygulamasını Oluşturun

Kod oluşturmak için farklı bir model indirelim: `Qwen3.5-35B-A3B-GGUF`. Bu, 32 GB+ RAM'e sahip sistemler için en uygun olan büyük (~20 GB) ve performanslı bir modeldir. Daha az RAM'iniz varsa, bunun yerine `Qwen3.5-9B-GGUF` (~6 GB) modelini deneyin.

Bunu arayüzden indirebilir veya aşağıdakini çalıştırabilirsiniz:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Basit bir Flashcard uygulaması için kod oluşturmak üzere aşağıdaki istemi Lemonade Chat arayüzüne verin.

Python uygulamamızı oluşturmak için Qwen3.5-35B-A3B-GGUF'u (kod yazmada daha iyi olan daha büyük bir model) kullanacağız ve uygulamanın kendisi çalışma zamanında Gemma-4-E2B-it-GGUF'u (zaten indirdiğiniz daha küçük model) çağıracak. Kod daha sonra Python'da çalıştırılmak üzere seçtiğiniz bir dosyaya kopyalanabilir.

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **İpucu**: Kaynakları ve hızı optimize etmek için kapsamlı istem (prompt) oluşturma ve iki modelli bir sistem kullanma yoluyla standart mühendislik uygulamalarını takip ettik.

Kolaylık olması açısından [`flashcards.py`](assets/flashcards.py) dosyasında örnek bir çıktı sağladık. Dilerseniz dizininize indirebilirsiniz. Her iki durumda da artık çalıştırılabilecek bir Python dosyasına sahip olmalısınız.

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
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

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### Adım 7: Oluşturulan Kodu Çalıştırın

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**İşte görmeniz gereken şey:**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

Yaklaşık 150 satır kodla, yerel bir LLM tarafından desteklenen tamamen işlevsel bir çalışma aracı oluşturdunuz. Yönetilecek bir API anahtarı yok, kullanım maliyeti yok ve hiçbir veri makinenizden asla çıkmıyor.

> **Önemli nokta:** `client = OpenAI(base_url=...) ` satırının bu uygulamayı OpenAI'nin bulutuna değil Lemonade'e bağlayan *tek* şey olduğuna dikkat edin. Kodun geri kalanı, OpenAI uyumlu herhangi bir hizmete karşı yazacağınız kodla aynıdır. OpenAI Python kütüphanesini daha önce hiç kullandıysanız, Lemonade ile nasıl uygulama oluşturacağınızı zaten biliyorsunuz demektir.

### Bunun Gösterdikleri

Bu küçük uygulama, çeşitli gerçek dünya entegrasyon kalıplarını sergiler:

| Kalıp | Nerede Görülür |
|---------|-----------------|
| **Sistem istemleri** | `"system"` mesajı, LLM'e yapılandırılmış JSON çıktısı vermesini söyler |
| **Yapılandırılmış çıktı** | Uygulama, çalışma kartlarını oluşturmak için LLM'in yanıtını JSON olarak ayrıştırır |
| **Durumsuz istekler** | Her `generate_flashcards()` çağrısı bağımsızdır |
| **Hata işleme** | `try/except`, LLM'in çıktısının geçerli JSON olmadığı durumları zarifçe ele alır |

Bu aynı kalıplar, sohbet botları, kod asistanları, içerik oluşturucular, otomasyon araçları gibi her türlü uygulamaya ölçeklenir.

#### Bonus Meydan Okuma

* Ekstra bir meydan okuma için, [burada](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) sağlanan örneğe başvurarak çalışma kartlarının kullanıcıya sesli okunmasını sağlamak üzere uygulamayı güncellemeyi deneyin.

---

<!-- @device:halo_box,halo,stx,krk -->
## NPU'da Model Çalıştırma (İsteğe Bağlı)

Bir Ryzen AI 300/400/Max 300 serisi veya Z2 Extreme cihazınız varsa, cihazınızda özellikle yapay zeka iş yükleri için tasarlanmış özel bir çip olan yerleşik bir **Sinirsel İşlem Birimi (NPU)** bulunur. Modelleri NPU üzerinde çalıştırmak, GPU kullanmaktan daha güç verimlidir; bu da onu arka plan yapay zeka görevleri, daha uzun oturumlar ve pil ile çalışan kullanım için ideal hale getirir.

Lemonade, aynı OpenAI API'nin arkasında şeffaf şekilde çalışan üç NPU çalıştırma modunu destekler:

| Mod | Nasıl Çalışır | Tarif | Örnek Modeller |
|------|-------------|--------|----------------|
| **Hibrit (NPU + iGPU)** | NPU istemi işler, iGPU token üretir | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Yalnızca NPU** | Tüm çıkarım NPU üzerinde çalışır | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | NPU üzerinde, AMD XDNA2 için optimize edilmiş FastFlowLM motorunu kullanır | FLM (`flm`) | qwen3.5-4b-FLM |

### Gereksinimler

- **AMD Ryzen AI 300/400 serisi veya Z2 serisi** işlemci
- **FLM** modelleri için: FLM çalışma zamanı, Lemonade uygulaması içinden kurulabilir veya bir FLM modeli çalıştırıldığında Lemonade, FLM çalışma zamanını otomatik olarak kuracaktır. FastFlowLM hakkında daha fazla bilgi edinmek için [buraya](https://fastflowlm.com/docs/) bakın.


### Adım 8: Bir Hibrit Model Çalıştırın

Hibrit modeller, hız ve verimlilik arasında iyi bir denge için işi NPU ve iGPU arasında paylaştırır. Lemonade Uygulamasında, `Ryzen AI LLM` listesinden bir model seçin, örneğin `Qwen3-4B-Hybrid`, ya da aşağıdaki komutu kullanarak çalıştırın:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade, NPU'nuzu otomatik olarak algılar ve **Ryzen AI LLM** arka ucunu kurar.

> **Perde arkasında neler oluyor?** Bir mesaj gönderdiğinizde, NPU tüm isteminizi paralel olarak işler (buna "prefill" denir). Ardından, iGPU devreye girerek yanıtı tek seferde bir token üreterek oluşturur (buna "decode" denir). Bu hibrit yaklaşım, her çipin güçlü yönlerinden yararlanır.

### Adım 9: Bir FLM Modeli Çalıştırın

FastFlowLM (FLM) modelleri, özellikle AMD'nin XDNA2 NPU mimarisi için optimize edilmiştir ve boyutlarına göre oldukça hızlı olabilir. Örneğin, `FastFlowLM NPU` listesinden `qwen3.5-4b-FLM` seçin veya aşağıdaki komutu kullanın:

<!-- @os:windows -->
Windows'ta `FastFlowLM`'i etkinleştirmek için:

* `Backends Manager` menüsünü açın.
* `FastFlowLM NPU` arka uç kategorisini bulun.
* Install NPU üzerine tıklayın.
* Kurulum tamamlandığında, FFLM açılır menüsü altında ~36 varsayılan model kullanılabilir olacaktır.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
`Lemonade` Uygulaması ilk kez başlatıldığında, `FastFlowNPU` arka ucu varsayılan olarak etkin değildir.
Yerel uygulama, kurulum sürecinde size rehberlik etmek için kurulum sayfasını açacaktır.

Linux'ta `FastFlowLM`'i etkinleştirmek için:

* `Lemonade` Uygulamasını açın.
* [Resmi FLM](https://lemonade-server.ai/flm_npu_linux.html) belgelerini ziyaret edin ve Linux dağıtımınızı seçerek FLM için kurulum adımlarını izleyin.
* Kurulum sayfasında belirtildiği şekilde backports'ları etkinleştirin.
* [etiketler sayfasından](https://github.com/FastFlowLM/FastFlowLM/tags) en son `v0.9.x` sürümünü indirin.

<!-- @device:halo_box -->
>[!Note]
AMD Halo Developer Platform için, Debian 13'ü seçtiğinizden emin olun.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* İndirilen `.deb` paketini kurun.
* Önerilen: `Lemonade App`'ten çıkın ve değişikliklerin algılanması için yeniden açın.
* Önerilen: `Backends Manager`'ı açın ve `FastFlowNPU` Backend'i Install edin.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Başarılı bir kurulumdan sonra, **Lemonade Desktop App** içindeki **Download Manager**'da `flm:npu`'nun tamamlandığını görmelisiniz.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Ardından, mevcut FFLM modellerinden herhangi birini seçip NPU arka ucunu kullanmaya başlayabilirsiniz.

Belirli bir model için, istediğiniz modeli [modeller sayfasından](https://fastflowlm.com/docs/models/qwen/) indirin ve belgelerde verilen Shell komutuyla doğrulayın.
```
flm run qwen3.5-4b-FLM
```
veya 
```
lemonade run qwen3.5-4b-FLM
```
 üzerinden
FLM modelleri, en popüler mimarilerden bazılarını (Gemma 3, Qwen 3, Llama 3 ve DeepSeek R1) içerir ve 1 GB'ın altından 13 GB'ın üzerine kadar değişir.
Lemonade, NPU'nuzu otomatik olarak algılar ve **FastFlowLM NPU** arka ucunu kurar.

<!-- @os:windows -->
> **İpucu:** En iyi NPU performansı için turbo modunu etkinleştirin:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Modeller Arasında Geçiş Yapma

Adım 6'daki flashcard uygulaması NPU modellerinde de çalışır, sadece model adını değiştirin:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Sonraki Adımlar

Kendi donanımınızda çalışan yerel bir yapay zeka sunucunuz var, şimdi sırada yapılacaklar:

1. **Favori uygulamalarınızı bağlayın**: Lemonade, [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) ve [daha birçoğuyla](https://lemonade-server.ai/marketplace) kutudan çıktığı gibi çalışır.

2. **Daha fazla model keşfedin**: Kodlama, akıl yürütme, görsel ve daha fazlası için optimize edilmiş modelleri bulmak üzere tam [model kütüphanesini](https://lemonade-server.ai/docs/server/server_models/) inceleyin. Neler mevcut olduğunu görmek için Lemonade Uygulamasını veya `lemonade list` komutunu kullanın.

3. **ROCm GPU hızlandırmasının kilidini açın**: Desteklenen bir AMD GPU'nuz varsa, ROCm arka ucuna geçin: `lemonade config set llamacpp.backend=rocm`. [Desteklenen AMD GPU'lara](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations) bakın.

4. **Tam API spesifikasyonunu okuyun**: Lemonade, sohbet tamamlamaları, gömmeler (embeddings), ses transkripsiyonu, görüntü üretimi, metinden konuşmaya dönüşüm ve daha fazlasını destekler. Her uç nokta için [Sunucu Spesifikasyonuna](https://lemonade-server.ai/docs/server/server_spec/) bakın.

5. **Katkıda bulunun**: Lemonade açık kaynaklıdır. [Katkı rehberine](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) göz atın ve [İlk Katkı İçin Uygun Sorunları](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) inceleyin.

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