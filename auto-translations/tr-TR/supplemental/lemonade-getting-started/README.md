<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# <!-- @github-only -->
> [!IMPORTANT]
> Bu kılavuz, GitHub'ın işleyemediği özel etiketler kullanmaktadır. Bu içeriği doğru bir şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->

## Genel Bakış

🍋 **Lemonade**, büyük dil modellerini (LLM'ler), görüntü üreticilerini ve ses modellerini doğrudan kendi donanımınızda çalıştırmanızı sağlayan açık kaynaklı bir yerel yapay zeka sunucusudur. Modelleri sektör standardı **OpenAI API** üzerinden sunar, böylece OpenAI ile çalışan herhangi bir uygulama anında Lemonade ile de çalışabilir. Bu kılavuzun sonunda, Lemonade'i kendi makinenizde yerel olarak modeller çalıştırmak için kullanıyor olacaksınız.

## Bu Kılavuzda Öğrenecekleriniz

Bu kılavuzun sonunda şunları yapabileceksiniz:

* **Lemonade Server'ı kurmak** ve çalıştığını doğrulamak.
* Tek bir komutla **bir LLM indirmek ve onunla sohbet etmek**.
* **Web arayüzünü keşfetmek** ve görü, konuşmadan metne dönüştürme ve görüntü üretimi gibi farklı modaliteleri denemek.
* **GPU arka uçlarını** Vulkan ve AMD ROCm™ yazılımı arasında değiştirmek.
* OpenAI uyumlu API'yi kullanarak yerel bir LLM tarafından desteklenen **bir Python uygulaması oluşturmak**.
<!-- @device:halo_box,halo,stx,krk -->
* AMD Ryzen™ AI donanımında Hybrid ve FLM çalıştırma modlarını kullanarak **AMD Sinirsel İşlem Birimi'nde (NPU) modeller çalıştırmak**.
<!-- @device:end -->

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarının Kurulumu

Başlamadan önce, aşağıdakilere sahip olduğunuzdan emin olun:

- **Windows 11** çalıştıran bir PC veya desteklenen bir **Linux** dağıtımı (Ubuntu 24.04+, Fedora, Debian)
- Adım 1–7'de kullanılan çalışma zamanı modeli (`Gemma-4-E2B-it-GGUF`, ~3 GB) için **16 GB RAM** önerilir. Adım 6'daki daha büyük kod oluşturma modelini (`Qwen3.5-35B-A3B-GGUF`, ~20 GB) kullanmak istiyorsanız **32 GB+** önerilir.
- İndirdiğiniz modellere bağlı olarak **~4–30 GB boş disk alanı**. Bu kılavuzdaki en büyük model yaklaşık 20 GB'dır.
- **Python 3.10–3.13** (Python uygulaması bölümünde kullanılır)
- Bir internet bağlantısı (kablolu veya kablosuz)
<!-- @device:halo_box,halo,stx,krk -->
- [İsteğe bağlı] NPU üzerinde bir model çalıştırmak istiyorsanız, [Ryzen AI Yazılımı Kurulum Talimatları](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) sayfasından en son sürücüsü kurulmuş bir AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 serisi veya Z2 Extreme)
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
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

## Temel Kavramlar — Yerel Yapay Zeka Sunucuları Nasıl Çalışır

Bir modeli çalıştırmadan önce, işlerin *neden* bu şekilde kurulduğunu anlamakta fayda var. Lemonade bir **yerel model sunucusudur**; yapay zeka modellerini belleğe yükleyen ve tıpkı bir bulut yapay zeka hizmetinde olduğu gibi bunları HTTP üzerinden uygulamalara sunan bir süreçtir.

### Neden Bir Sunucu?

| Fayda | Sizin İçin Anlamı |
|---------|----------------------|
| **Basitleştirilmiş entegrasyon** | Uygulamalar, donanıma özgü C++ veya Python kütüphaneleriyle uğraşmak yerine tek bir HTTP API ile iletişim kurar. |
| **Paylaşılan modeller** | Tek bir yüklenmiş model aynı anda birden fazla uygulamaya hizmet verebilir; RAM'inizi tüketen yinelenen kopyalar oluşmaz. |
| **Buluttan yerele taşınabilirlik** | OpenAI'nin bulut API'si için yazılan kod, tek bir URL değiştirilerek Lemonade ile çalışır. |
| **Sorumlulukların ayrılması** | Model yönetimi, akış (streaming) ve hata toleransı sunucu tarafından ele alınır; böylece geliştiriciler uygulamalarına odaklanabilir. |

### OpenAI API Standardı

Lemonade, ChatGPT, Azure OpenAI ve düzinelerce başka hizmet tarafından kullanılan aynı arayüz olan **OpenAI API**'yi uygular. Konuşma modeli basittir:

| Rol | Kim Konuşuyor |
|------|---------------|
| **system** | Modele verilen talimatlar (kişilik, kısıtlamalar, mevcut araçlar) |
| **user** | İnsandan (veya uygulamadan) modele gönderilen mesajlar |
| **assistant** | Model tarafından üretilen yanıtlar |

Bu, OpenAI'yi destekleyen herhangi bir kütüphanenin veya uygulamanın, Lemonade Server çalışırken onu `http://localhost:13305/api/v1` adresine yönlendirerek Lemonade ile iletişim kurabileceği anlamına gelir.

## Ana Etkinlik — İlk Yerel Yapay Zeka Sohbetiniz

Bir LLM indirelim ve yapay zekayı tamamen kendi makinenizde çalıştırarak onunla bir sohbet gerçekleştirelim.

### Adım 1: Bir Model İndirme ve Çalıştırma

Lemonade, seçilmiş bir model kitaplığıyla birlikte gelir. **Gemma-4-E2B-it** ile başlayalım; görü desteği de içeren yetenekli ve kompakt bir model. Bir terminal açın ve şunu çalıştırın:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Bu tek komut üç şeyi yapar:

1. Model henüz indirilmemişse, Hugging Face'ten (~3 GB) **indirir**. (Biraz zaman alabilir)
2. Lemonade Server sürecini 13305 numaralı portta **başlatır**.
3. Modelle sohbet etmeye başlayabilmeniz için **Lemonade App'i açar**.


<!-- @os:windows -->
Windows'ta, Lemonade App otomatik olarak başlatılır ve hemen sohbet etmeye başlayabilirsiniz. `minimal.msi` paketini kurduysanız, uygulama dahil değildir. Sohbet etmeye başlamak için web tarayıcınızı açın ve `http://localhost:13305` adresine gidin.
<!-- @os:end -->

<!-- @os:linux -->
Linux'ta, web uygulamasına erişmek için tarayıcınızı açın ve `http://localhost:13305` adresine gidin.
<!-- @os:end -->

Bir soru yazmayı deneyin:

```
What are three fun facts about lemons?
```

Model, sohbet penceresinde doğrudan yanıt verecektir. **Tebrikler! Yerel olarak bir büyük dil modeli çalıştırıyorsunuz.**

![Günlükleri gösteren Lemonade App](../../dependencies/assets/ChatwithLogs.png)

Lemonade App'teki Sunucu Günlükleri panelinde, her yanıttan sonra modelin performansına ilişkin telemetri verilerini bulabilirsiniz. Örneğin:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Adım 2: Web Arayüzünü ve Farklı Modaliteleri Keşfedin

Lemonade, aşağıdaki işlemleri yapabileceğiniz yerleşik bir web arayüzü içerir:

- Tanıdık bir sohbet penceresinde yüklü modelle **etkileşim kurma**
- Model Yöneticisi sekmesinde **modellere göz atma**
- Tek tıklamayla **yeni modeller indirme**

Web arayüzündeki **Model Yöneticisi** sekmesini kullanarak farklı modaliteler arasında geçiş yapmayı deneyin; burada modellere Tarife (Recipe) veya Kategoriye göre göz atabilirsiniz:

1. **Görü:** Zaten yüklü olan `Gemma-4-E2B-it-GGUF` modeli görüyü destekler. Sohbet kutusuna bir görsel yapıştırın ve modelden onu tanımlamasını isteyin.
2. **Görsel oluşturma:** Görsel kategorisinde, Model Yöneticisi'nden `SDXL-Turbo` gibi bir görsel modeli indirin, ardından yerel olarak bir görsel oluşturmak için Lemonade Görsel Oluşturucu'da bir istem (prompt) yazın.
3. **Ses:** Ses kategorisinde, konuşmadan metne dönüştürme yapabilen `Whisper-Tiny` gibi bir ses modeli indirin. Yerel olarak metne dönüştürmek için bir ses kaydı sağlayın. Metinden konuşmaya için, Konuşma kategorisindeki `kokoro-v1` gibi modellerden birini deneyin.

![Lemonade ile Çoklu Modalite](../../dependencies/assets/multi_modality.png)

### Adım 3: Farklı Bir Arka Uçla Model Deneyin

Lemonade Uygulamasında bir modelin üzerine geldiğinizde bir dişli simgesi görürsünüz. Buna tıklamak, istediğiniz arka ucu seçmek de dahil olmak üzere model için seçenekler belirlemenize olanak tanır.

Lemonade varsayılan olarak GPU hızlandırması için Vulkan kullanır. Desteklenen bir AMD ayrık GPU'nuz varsa ROCm'e geçebilirsiniz.

![Lemonade Arka Uç Seçimi](../../dependencies/assets/lemonademodeloptions.png)

Yüklü arka uçlarınızı yönetmek için en soldaki sütundaki arka uç düğmesine tıklayın.

Alternatif olarak, arka ucu aşağıdaki komutu kullanarak belirtebilirsiniz:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Varsayılan arka ucunuzu `LEMONADE_LLAMACPP` ortam değişkenini şu değerlerle kullanarak da ayarlayabilirsiniz: `vulkan`, `rocm` veya `cpu`.

---

## Daha Derine İnmek — Python ile Yapay Zeka Destekli Bir Uygulama Oluşturma

Yerel bir yapay zeka sunucusunun gerçek gücü, herhangi bir uygulamanın sadece birkaç satır kodla ona bağlanabilmesidir. Bunu kanıtlamak için, küçük ama işlevsel bir **çalışma kartı (flashcard) oluşturucu** yapalım; burada bir konu verirsiniz, kartlar oluşturulur ve etkileşimli olarak kendinizi test edebilirsiniz.

### Adım 4: Sunucuyu Başlatın

Lemonade sunucusunun çalıştığını doğrulayın. Kurulumdan sonra genellikle arka planda otomatik olarak başlar. Doğrulamak için şunu çalıştırın:

```
lemonade status
```

Şuna benzer bir mesaj görmelisiniz: `Server is running on port 13305`.

Sunucu çalışmıyorsa, Lemonade uygulamasını açarak başlatın. Varsayılan bağlantı noktası **13305**'i kullanın (bunu tepsi simgesinden onaylayabilir veya seçebilirsiniz).

### Adım 5: OpenAI Python İstemcisini Kurun

Bir terminalde, bir venv oluşturun ve aşağıdaki komutları kullanarak OpenAI Python İstemcisini kurun:
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

### Adım 6: Flashcard Uygulamasını Oluşturun

Kod oluşturmak için farklı bir model indirelim: `Qwen3.5-35B-A3B-GGUF`. Bu, 32 GB+ RAM'e sahip sistemler için en uygun olan büyük (~20 GB) ve performanslı bir modeldir. Daha az RAM'iniz varsa, bunun yerine `Qwen3.5-9B-GGUF` (~6 GB) modelini deneyin.

Bunu arayüzden indirebilir veya aşağıdakini çalıştırabilirsiniz:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Basit bir Flashcard uygulaması için kod oluşturmak amacıyla aşağıdaki istemi Lemonade Sohbet Arayüzüne verin.

Python uygulamamızı oluşturmak için Qwen3.5-35B-A3B-GGUF'yi (kod yazmada daha iyi olan daha büyük bir model) kullanacağız ve uygulamanın kendisi çalışma zamanında Gemma-4-E2B-it-GGUF'yi (zaten indirdiğiniz daha küçük model) çağıracak. Kod daha sonra Python'da çalıştırılmak üzere seçtiğiniz bir dosyaya kopyalanabilir.

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

> **İpucu**: Kapsamlı bir istem oluşturma ve kaynakları ile hızı optimize etmek için iki modelli bir sistem kullanarak standart mühendislik uygulamalarını takip ettik.

Kolaylığınız için, [`flashcards.py`](assets/flashcards.py) dosyasında örnek bir çıktı sağladık. Dilerseniz kendi dizinize indirebilirsiniz. Her iki durumda da, artık çalıştırılabilecek bir Python dosyanız olmalı.

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

**Görmeniz gereken şey şu:**

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

Yaklaşık 150 satır kodla, yerel bir LLM tarafından desteklenen tamamen işlevsel bir çalışma aracı oluşturmuş oldunuz. Yönetilecek bir API anahtarı yok, kullanım maliyeti yok ve makinenizden hiçbir veri dışarı çıkmıyor.

> **Önemli çıkarım:** `client = OpenAI(base_url=...) ` satırının bu uygulamayı OpenAI'nin bulutu yerine Lemonade'e bağlayan *tek* şey olduğuna dikkat edin. Kodun geri kalanı, OpenAI uyumlu herhangi bir hizmete karşı yazacağınız kodla aynıdır. OpenAI Python kütüphanesini daha önce kullandıysanız, Lemonade ile nasıl uygulama oluşturacağınızı zaten biliyorsunuz demektir.

### Bunun Gösterdiği Şey

Bu küçük uygulama, birkaç gerçek dünya entegrasyon deseni sergiler:

| Desen | Nerede Görülür |
|---------|-----------------|
| **Sistem istemleri** | `"system"` mesajı, LLM'e yapılandırılmış JSON çıktısı vermesini söyler |
| **Yapılandırılmış çıktı** | Uygulama, flashcard'ları oluşturmak için LLM'in yanıtını JSON olarak ayrıştırır |
| **Durumsuz istekler** | Her `generate_flashcards()` çağrısı bağımsızdır |
| **Hata işleme** | `try/except`, LLM'in çıktısının geçerli JSON olmadığı durumları zarif bir şekilde ele alır |

Bu aynı desenler, sohbet botları, kod asistanları, içerik oluşturucular, otomasyon araçları gibi herhangi bir uygulamaya ölçeklenir.

#### Bonus Meydan Okuma

* Ek bir meydan okuma için, [burada](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) sağlanan örneğe başvurarak flashcard'ların kullanıcıya sesli okunmasını sağlayacak şekilde uygulamayı güncellemeyi deneyin.

---

<!-- @device:halo_box,halo,stx,krk -->
## NPU'da Model Çalıştırma (İsteğe Bağlı)

Bir Ryzen AI 300/400/Max 300 serisi veya Z2 Extreme cihazınız varsa, cihazınızda özellikle yapay zeka iş yükleri için tasarlanmış özel bir çip olan yerleşik bir **Sinirsel İşlem Birimi (NPU)** bulunur. Modelleri NPU üzerinde çalıştırmak GPU kullanmaktan daha güç tasarruflu olduğundan, bu durum arka planda çalışan yapay zeka görevleri, uzun oturumlar ve pil ile çalışma için idealdir.

Lemonade, hepsi aynı OpenAI API'sinin arkasında şeffaf olan üç NPU çalıştırma modunu destekler:

| Mod | Nasıl Çalışır | Tarif | Örnek Modeller |
|------|-------------|--------|----------------|
| **Hibrit (NPU + iGPU)** | NPU istemi işler, iGPU token üretir | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Yalnızca NPU** | Çıkarımın tamamı NPU üzerinde çalışır | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | AMD XDNA2 için optimize edilmiş, NPU üzerinde FastFlowLM motorunu kullanır | FLM (`flm`) | qwen3.5-4b-FLM |

### Gereksinimler

- **AMD Ryzen AI 300/400 serisi veya Z2 serisi** işlemci
- **FLM** modelleri için: FLM çalışma zamanı, Lemonade uygulaması içinden kurulabilir veya Lemonade bir FLM modeli çalıştırırken FLM çalışma zamanını otomatik olarak kuracaktır. FastFlowLM hakkında daha fazla bilgi edinmek için [buraya](https://fastflowlm.com/docs/) bakın.


### Adım 8: Bir Hibrit Model Çalıştırın

Hibrit modeller, hız ve verimlilik arasında iyi bir denge sağlamak için işi NPU ve iGPU arasında paylaştırır. Lemonade Uygulamasında, `Ryzen AI LLM` listesinden bir model seçin, örneğin `Qwen3-4B-Hybrid`, veya aşağıdaki komutu kullanarak çalıştırın:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade, NPU'nuzu otomatik olarak algılar ve **Ryzen AI LLM** arka ucunu kurar.

> **Perde arkasında neler oluyor?** Bir mesaj gönderdiğinizde, NPU tüm isteminizi paralel olarak işler (buna "prefill" denir). Ardından iGPU, yanıtı bir seferde bir token üreterek oluşturmaya başlar (buna "decode" denir). Bu hibrit yaklaşım, her bir çipin güçlü yönlerinden yararlanır.

### Adım 9: Bir FLM Modeli Çalıştırın

FastFlowLM (FLM) modelleri özellikle AMD'nin XDNA2 NPU mimarisi için optimize edilmiştir ve boyutlarına göre oldukça hızlı olabilirler. Örneğin, `FastFlowLM NPU` listesinden `qwen3.5-4b-FLM` seçin veya aşağıdaki komutu kullanın:

<!-- @os:windows -->
Windows üzerinde `FastFlowLM`'i etkinleştirmek için:

* `Backends Manager` menüsünü açın.
* `FastFlowLM NPU` arka uç kategorisini bulun.
* Install NPU'ya tıklayın.
* Kurulum tamamlandığında, FFLM açılır menüsü altında ~36 varsayılan model kullanılabilir olacaktır.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
`Lemonade` Uygulaması ilk kez başlatıldığında, `FastFlowNPU` arka ucu varsayılan olarak etkin değildir.
Yerel uygulama, kurulum sürecinde size rehberlik etmek için kurulum sayfasını açacaktır.

Linux üzerinde `FastFlowLM`'i etkinleştirmek için:

* `Lemonade` Uygulamasını açın.
* [Resmi FLM](https://lemonade-server.ai/flm_npu_linux.html) belgelerini ziyaret edin ve Linux dağıtımınızı seçerek FLM için kurulum adımlarını izleyin.
* Kurulum sayfasında belirtildiği gibi backports'u etkinleştirin.
* [etiketler sayfasından](https://github.com/FastFlowLM/FastFlowLM/tags) en son `v0.9.x` sürümünü indirin.'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
AMD Halo Developer Platform için Debian 13'ü seçtiğinizden emin olun.
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
* Önerilen: `Lemonade App`'ten çıkın ve değişikliklerin algılanması için tekrar açın.
* Önerilen: `Backends Manager`'ı açın ve `FastFlowNPU` Backend'i kurmak için tıklayın.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Başarılı bir kurulumdan sonra, **Lemonade Desktop App** içindeki **Download Manager**'da `flm:npu`'nun tamamlandığını görmelisiniz.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Ardından mevcut FFLM modellerinden herhangi birini seçip NPU arka ucunu kullanmaya başlayabilirsiniz.

Belirli bir model için, istediğiniz modeli [modeller sayfasından](https://fastflowlm.com/docs/models/qwen/) indirin ve belgelerde sağlanan Shell komutunu kullanarak doğrulayın.
```
flm run qwen3.5-4b-FLM
```
veya 
```
lemonade run qwen3.5-4b-FLM
```
 aracılığıyla
FLM modelleri en popüler mimarilerden bazılarını içerir (Gemma 3, Qwen 3, Llama 3 ve DeepSeek R1) ve 1 GB'ın altından 13 GB'ın üzerine kadar değişir.
Lemonade, NPU'nuzu otomatik olarak algılar ve **FastFlowLM NPU** arka ucunu kurar.

<!-- @os:windows -->
> **İpucu:** En iyi NPU performansı için turbo modunu etkinleştirin:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Modelleri Değiştirme

Adım 6'daki flashcard uygulaması NPU modelleriyle de çalışır, sadece model adını değiştirin:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Sonraki Adımlar

Kendi donanımınızda çalışan yerel bir yapay zeka sunucunuz var, işte bundan sonra yapabilecekleriniz:

1. **Favori uygulamalarınızı bağlayın**: Lemonade, [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) ve [daha birçoğuyla](https://lemonade-server.ai/marketplace) kutudan çıktığı gibi çalışır.

2. **Daha fazla modele göz atın**: Kodlama, akıl yürütme, görüntü işleme ve daha fazlası için optimize edilmiş modelleri bulmak üzere tam [model kütüphanesini](https://lemonade-server.ai/docs/server/server_models/) keşfedin. Mevcut olanları görmek için Lemonade Uygulamasını veya `lemonade list` komutunu kullanın.

3. **ROCm GPU hızlandırmasının kilidini açın**: Desteklenen bir AMD GPU'nuz varsa, ROCm arka ucuna geçin: `lemonade config set llamacpp.backend=rocm`. [Desteklenen AMD GPU'lara](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations) bakın.

4. **Tam API spesifikasyonunu okuyun**: Lemonade; sohbet tamamlamalarını, gömme (embedding) işlemlerini, ses transkripsiyonunu, görüntü oluşturmayı, metinden sese dönüşümü ve daha fazlasını destekler. Her uç nokta için [Sunucu Spesifikasyonuna](https://lemonade-server.ai/docs/server/server_spec/) bakın.

5. **Katkıda bulunun**: Lemonade açık kaynaklıdır. [Katkı kılavuzuna](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) göz atın ve [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) etiketli konulara bakın.