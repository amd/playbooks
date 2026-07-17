<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Bu oyun kitabı, GitHub'ın işleyemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->

## Genel Bakış

🍋 **Lemonade**, büyük dil modellerini (LLM'ler), görüntü oluşturucuları ve ses modellerini doğrudan kendi donanımınızda çalıştırmanıza olanak tanıyan açık kaynaklı bir yerel AI sunucusudur. Modelleri sektör standardı **OpenAI API** aracılığıyla sunar; böylece OpenAI ile çalışan her uygulama anında Lemonade ile de çalışabilir. Oyun kitabının sonunda, Lemonade'i kullanarak modelleri makinenizde yerel olarak çalıştırıyor olacaksınız.

## Neler Öğreneceksiniz

Bu oyun kitabının sonunda şunları yapabileceksiniz:

* **Lemonade Server'ı kurmak** ve çalıştığını doğrulamak.
* **Tek bir komutla bir LLM indirmek ve sohbet etmek**.
* **Web arayüzünü keşfetmek** ve görme, konuşmadan metne ve görüntü oluşturma gibi farklı modaliteleri denemek.
* **GPU arka uçları arasında geçiş yapmak**: Vulkan ve AMD ROCm™ yazılımı arasında.
* **OpenAI uyumlu API kullanarak yerel bir LLM ile desteklenen bir Python uygulaması oluşturmak**.
<!-- @device:halo_box,halo,stx,krk -->
* **AMD Neural Processing Unit (NPU) üzerinde modeller çalıştırmak**: AMD Ryzen™ AI donanımında Hybrid ve FLM yürütme modlarını kullanarak.
<!-- @device:end -->

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarını Yükleme

Başlamadan önce aşağıdakilere sahip olduğunuzdan emin olun:

- **Windows 11** veya desteklenen bir **Linux** dağıtımı (Ubuntu 24.04+, Fedora, Debian) çalıştıran bir PC
- 1–7. Adımlarda kullanılan çalışma zamanı modeli için (`Gemma-4-E2B-it-GGUF`, ~3 GB) **16 GB RAM** önerilir. 6. Adımdaki daha büyük kod oluşturma modelini (`Qwen3.5-35B-A3B-GGUF`, ~20 GB) kullanmak istiyorsanız **32 GB+** önerilir.
- İndirdiğiniz modellere bağlı olarak **~4–30 GB boş disk alanı**. Bu kılavuzdaki en büyük model yaklaşık 20 GB'tır.
- **Python 3.10–3.13** (Python uygulama bölümünde kullanılır)
- İnternet bağlantısı (kablolu veya kablosuz)
<!-- @device:halo_box,halo,stx,krk -->
- [İsteğe bağlı] NPU üzerinde model çalıştırmak istiyorsanız, [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) adresinden en son sürücüsü yüklenmiş bir AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 serisi veya Z2 Extreme).
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

## Temel Kavramlar — Yerel AI Sunucuları Nasıl Çalışır

Bir modeli çalıştırmadan önce, neden bu şekilde kurulduğunu anlamak faydalıdır. Lemonade bir **yerel model sunucusudur**; AI modellerini belleğe yükleyen ve bunları uygulamalara HTTP üzerinden sunan, tıpkı bir bulut AI hizmeti gibi çalışan bir süreçtir.

### Neden Bir Sunucu?

| Fayda | Sizin İçin Ne Anlama Gelir |
|---------|----------------------|
| **Basitleştirilmiş entegrasyon** | Uygulamalar, donanıma özgü C++ veya Python kitaplıklarıyla uğraşmak yerine tek bir HTTP API'siyle iletişim kurar. |
| **Paylaşılan modeller** | Tek bir yüklü model, birden fazla uygulamaya aynı anda hizmet verebilir; RAM'inizi tüketen yinelenen kopyalar olmaz. |
| **Buluttan yerele taşınabilirlik** | OpenAI'nin bulut API'si için yazılmış kod, yalnızca bir URL değiştirilerek Lemonade ile çalışır. |
| **Sorumlulukların ayrılması** | Model yönetimi, akış ve hata toleransı sunucu tarafından yönetilir; böylece geliştiriciler uygulamalarına odaklanabilir. |

### OpenAI API Standardı

Lemonade, ChatGPT, Azure OpenAI ve düzinelerce başka hizmet tarafından kullanılan arayüzün aynısı olan **OpenAI API**'yi uygular. Konuşma modeli basittir:

| Rol | Kim Konuşuyor |
|------|---------------|
| **system** | Modele verilen talimatlar (kişilik, kısıtlamalar, mevcut araçlar) |
| **user** | İnsandan (veya uygulamadan) modele gelen mesajlar |
| **assistant** | Model tarafından oluşturulan yanıtlar |

Bu, OpenAI'yi destekleyen herhangi bir kitaplık veya uygulamanın, Lemonade Server çalışırken `http://localhost:13305/api/v1` adresine yönlendirilerek Lemonade ile iletişim kurabilmesi anlamına gelir.

## Ana Etkinlik — İlk Yerel AI Sohbetiniz

Bir LLM indirelim ve yapay zekayı tamamen kendi makinenizde çalıştırarak onunla sohbet edelim.

### Adım 1: Bir Model İndirin ve Çalıştırın

Lemonade, seçilmiş bir model kitaplığıyla birlikte gelir. Görme desteği de dahil olmak üzere yetenekli ve kompakt bir model olan **Gemma-4-E2B-it** ile başlayalım. Bir terminal açın ve şunu çalıştırın:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Bu tek komut üç şey yapar:

1. Henüz indirilmemişse modeli (~3 GB) Hugging Face'den **indirir**. (Biraz zaman alabilir)
2. Lemonade Server sürecini 13305 numaralı bağlantı noktasında **başlatır**.
3. Modelle sohbet etmeye başlayabilmeniz için **Lemonade App'i açar**.


<!-- @os:windows -->
Windows'ta Lemonade App otomatik olarak başlar ve hemen sohbet etmeye başlayabilirsiniz. `minimal.msi` paketini yüklediyseniz uygulama dahil değildir. Sohbet etmeye başlamak için web tarayıcınızı açın ve `http://localhost:13305` adresine gidin.
<!-- @os:end -->

<!-- @os:linux -->
Linux'ta tarayıcınızı açın ve web uygulamasına erişmek için `http://localhost:13305` adresine gidin.
<!-- @os:end -->

Bir soru yazmayı deneyin:

```
What are three fun facts about lemons?
```

Model doğrudan sohbet penceresinde yanıt verecektir. **Tebrikler! Yerel olarak büyük bir dil modeli çalıştırıyorsunuz.**

![Günlükler görüntülenen Lemonade App](../../dependencies/assets/ChatwithLogs.png)

Lemonade App'teki Sunucu Günlükleri bölmesinde, her yanıttan sonra modelin performansına ilişkin telemetri verilerini bulabilirsiniz. Örneğin:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Adım 2: Web Arayüzünü ve Farklı Modaliteleri Keşfedin

Lemonade, aşağıdakileri yapabileceğiniz yerleşik bir web arayüzü içerir:

- Yüklenen modelle tanıdık bir sohbet penceresinde **etkileşim** kurma
- Model Yöneticisi sekmesinde **modellere göz atma**
- Tek tıklamayla **yeni modeller indirme**

Web arayüzündeki **Model Yöneticisi** sekmesini kullanarak farklı modaliteler arasında geçiş yapmayı deneyin; burada modellere Tarife veya Kategori bazında göz atabilirsiniz:

1. **Görüntü:** Zaten yüklü olan `Gemma-4-E2B-it-GGUF` modeli görüntüyü destekler. Sohbet kutusuna bir görüntü yapıştırın ve modelden onu tanımlamasını isteyin.
2. **Görüntü oluşturma:** Görüntü kategorisinde, Model Yöneticisi'nden `SDXL-Turbo` gibi bir görüntü modeli indirin, ardından Lemonade Görüntü Oluşturucu'yu kullanarak bir istem yazın ve yerel olarak görüntü oluşturun.
3. **Ses:** Ses kategorisinde, konuşmadan metne dönüştürme yapabilen `Whisper-Tiny` gibi bir ses modeli indirin. Yerel olarak transkript oluşturmak için bir ses kaydı sağlayın. Metinden konuşmaya için, `kokoro-v1` gibi Konuşma kategorisindeki modellerden birini deneyin.

![Lemonade ile Çoklu Modalite](../../dependencies/assets/multi_modality.png)

### Adım 3: Farklı Bir Arka Uçla Model Deneyin

Lemonade Uygulaması'nda bir modelin üzerine geldiğinizde bir dişli simgesi göreceksiniz. Buna tıklamak, istediğiniz arka ucu seçmek de dahil olmak üzere model için seçenekler belirlemenize olanak tanır.

Lemonade, varsayılan olarak GPU hızlandırması için Vulkan kullanır. Desteklenen bir AMD ayrık GPU'nuz varsa ROCm'a geçebilirsiniz.

![Lemonade Arka Uç Seçimi](../../dependencies/assets/lemonademodeloptions.png)

Yüklü arka uçlarınızı yönetmek için en soldaki sütundaki arka uç düğmesine tıklayın.

Alternatif olarak, aşağıdaki komutu kullanarak arka ucu belirtebilirsiniz:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Ayrıca `LEMONADE_LLAMACPP` ortam değişkenini `vulkan`, `rocm` veya `cpu` değerleriyle kullanarak varsayılan arka ucunuzu ayarlayabilirsiniz.

---

## Daha Derine İnin — Python ile Yapay Zeka Destekli Bir Uygulama Oluşturun

Yerel bir yapay zeka sunucusunun gerçek gücü, herhangi bir uygulamanın yalnızca birkaç satır kodla ona bağlanabilmesidir. Bunu kanıtlamak için küçük ama işlevsel bir **çalışma kartı oluşturucu** oluşturalım; bir konu verirsiniz, kartları oluşturur ve kendinizi interaktif olarak sınayabilirsiniz.

### Adım 4: Sunucuyu Başlatın

Lemonade sunucusunun çalıştığını doğrulayın. Genellikle kurulumdan sonra arka planda otomatik olarak başlar. Doğrulamak için şunu çalıştırın:

```
lemonade status
```

Şuna benzer bir mesaj görmelisiniz: `Server is running on port 13305`.

Sunucu çalışmıyorsa, Lemonade uygulamasını açarak başlatın. Varsayılan **13305** portunu kullanın (bunu tepsi simgesinden onaylayabilir veya seçebilirsiniz).

### Adım 5: OpenAI Python İstemcisini Yükleyin

Bir terminalde, bir sanal ortam oluşturun ve aşağıdaki komutları kullanarak OpenAI Python İstemcisini yükleyin:
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

### Adım 6: Kart Uygulamasını Oluşturun

Kod oluşturmak için farklı bir model indirelim: `Qwen3.5-35B-A3B-GGUF`. Bu, büyük (~20 GB) ve performanslı bir modeldir; 32 GB+ RAM'e sahip sistemler için en uygundur. Daha az RAM'iniz varsa, bunun yerine `Qwen3.5-9B-GGUF` (~6 GB) modelini deneyin.

Bunu arayüzden indirebilir veya aşağıdakini çalıştırabilirsiniz:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Basit bir Kart uygulaması için kod oluşturmak amacıyla aşağıdaki istemi Lemonade Sohbet Arayüzü'ne girin.

Python uygulamamızı oluşturmak için Qwen3.5-35B-A3B-GGUF'u (kod yazmada daha iyi olan büyük model) kullanacağız; uygulamanın kendisi ise çalışma zamanında Gemma-4-E2B-it-GGUF'u (zaten indirdiğiniz küçük model) çağıracak. Kod daha sonra Python'da çalıştırılmak üzere seçtiğiniz bir dosyaya kopyalanabilir.

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

> **İpucu**: Kaynakları ve hızı optimize etmek için kapsamlı istem oluşturma ve iki modelli sistem kullanarak standart mühendislik uygulamalarını takip ettik.

Kolaylığınız için [`flashcards.py`](assets/flashcards.py) dosyasında örnek çıktı sağladık. Dizininize indirmekten çekinmeyin. Her iki durumda da artık çalıştırılabilecek bir Python dosyanız olmalıdır.

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

**Görmeniz gereken şey:**

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

Yaklaşık 150 satır kodla, yerel bir LLM tarafından desteklenen tam işlevli bir çalışma aracı oluşturdunuz. Yönetilecek API anahtarı yok, kullanım maliyeti yok ve verileriniz hiçbir zaman makinenizden çıkmıyor.

> **Temel içgörü:** `client = OpenAI(base_url=...) ` satırının bu uygulamayı OpenAI'nin bulutuna değil Lemonade'e bağlayan *tek* şey olduğuna dikkat edin. Kodun geri kalanı, herhangi bir OpenAI uyumlu servise karşı yazacağınızla aynıdır. OpenAI Python kütüphanesini daha önce kullandıysanız, Lemonade ile uygulama oluşturmayı zaten biliyorsunuzdur.

### Bu Neyi Gösteriyor

Bu küçük uygulama, birçok gerçek dünya entegrasyon kalıbını kullanır:

| Kalıp | Nerede Görünür |
|---------|-----------------|
| **Sistem istemleri** | `"system"` mesajı, LLM'e yapılandırılmış JSON çıktısı vermesini söyler |
| **Yapılandırılmış çıktı** | Uygulama, kart oluşturmak için LLM'in yanıtını JSON olarak ayrıştırır |
| **Durumsuz istekler** | Her `generate_flashcards()` çağrısı bağımsızdır |
| **Hata işleme** | `try/except`, LLM'in çıktısının geçerli JSON olmadığı durumları zarif biçimde ele alır |

Bu kalıpların tümü; sohbet botları, kod asistanları, içerik oluşturucular ve otomasyon araçları gibi her türlü uygulamaya ölçeklenebilir.

#### Bonus Meydan Okuma

* Ek bir meydan okuma için, [burada](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) sağlanan örneğe başvurarak kartların kullanıcıya sesli okunması için uygulamayı güncellemeyi deneyin.

---

<!-- @device:halo_box,halo,stx,krk -->
## Modelleri NPU Üzerinde Çalıştırma (İsteğe Bağlı)

Ryzen AI 300/400/Max 300 serisi veya Z2 Extreme cihazınız varsa, cihazınızda yerleşik bir **Sinir İşleme Birimi (NPU)** bulunmaktadır; bu, özellikle yapay zeka iş yükleri için tasarlanmış özel bir çiptir. Modelleri NPU üzerinde çalıştırmak, GPU kullanmaktan daha enerji verimlidir; bu da onu arka plan yapay zeka görevleri, uzun süreli oturumlar ve pille çalışan kullanım için ideal kılar.

Lemonade, aynı OpenAI API'sinin arkasında şeffaf biçimde çalışan üç NPU yürütme modunu destekler:

| Mod | Nasıl Çalışır | Tarif | Örnek Modeller |
|------|-------------|--------|----------------|
| **Hibrit (NPU + iGPU)** | NPU istemi işler, iGPU token üretir | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Yalnızca NPU** | Tüm çıkarım NPU üzerinde çalışır | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | NPU üzerinde FastFlowLM motorunu kullanır, AMD XDNA2 için optimize edilmiştir | FLM (`flm`) | qwen3.5-4b-FLM |

### Gereksinimler

- **AMD Ryzen AI 300/400 serisi veya Z2 serisi** işlemci
- **FLM** modelleri için: FLM çalışma zamanı Lemonade uygulaması içinden yüklenebilir veya Lemonade, bir FLM modeli çalıştırılırken FLM çalışma zamanını otomatik olarak yükler. FastFlowLM hakkında daha fazla bilgi edinmek için [buraya](https://fastflowlm.com/docs/) bakın.


### Adım 8: Hibrit Model Çalıştırma

Hibrit modeller, iyi bir hız ve verimlilik dengesi için işi NPU ile iGPU arasında paylaştırır. Lemonade Uygulamasında `Ryzen AI LLM` listesinden bir model seçin; örneğin `Qwen3-4B-Hybrid`, ya da aşağıdaki komutu kullanarak çalıştırın:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade, NPU'nuzu otomatik olarak algılar ve **Ryzen AI LLM** arka ucunu yükler.

> **Arka planda neler oluyor?** Bir mesaj gönderdiğinizde, NPU tüm isteminizi paralel olarak işler (buna "ön doldurma" denir). Ardından iGPU, yanıtı bir seferde bir token üretmek için devreye girer (buna "kod çözme" denir). Bu hibrit yaklaşım, her çipin güçlü yönlerinden yararlanır.

### Adım 9: FLM Modeli Çalıştırma

FastFlowLM (FLM) modelleri, AMD'nin XDNA2 NPU mimarisi için özel olarak optimize edilmiştir ve boyutlarına göre çok hızlı olabilir. Örneğin, `FastFlowLM NPU` listesinden `qwen3.5-4b-FLM` seçin veya aşağıdaki komutu kullanın:

<!-- @os:windows -->
Windows'ta `FastFlowLM` etkinleştirmek için:

* `Backends Manager` menüsünü açın.
* `FastFlowLM NPU` arka uç kategorisini bulun.
* NPU Yükle'ye tıklayın.
* Kurulum tamamlandıktan sonra, FFLM açılır menüsünde yaklaşık 36 varsayılan model kullanılabilir olacaktır.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
`Lemonade` Uygulaması ilk kez başlatıldığında, `FastFlowNPU` arka ucu varsayılan olarak etkin değildir.
Yerel uygulama, kurulum sürecinde size rehberlik etmek için kurulum sayfasını açacaktır.

Linux'ta `FastFlowLM` etkinleştirmek için:

* `Lemonade` Uygulamasını açın.
* [Resmi FLM](https://lemonade-server.ai/flm_npu_linux.html) belgelerini ziyaret edin ve Linux dağıtımınızı seçerek FLM kurulum adımlarını izleyin.
* Kurulum sayfasında belirtildiği şekilde backport'ları etkinleştirin.
* [etiketler sayfasından](https://github.com/FastFlowLM/FastFlowLM/tags) en son `v0.9.x` sürümünü indirin.'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
AMD Halo Geliştirici Platformu için Debian 13'ü seçtiğinizden emin olun.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* İndirilen `.deb` paketini yükleyin.
* Önerilen: `Lemonade App`'i kapatın ve değişikliklerin algılanması için yeniden açın.
* Önerilen: `Backends Manager`'ı açın ve `FastFlowNPU` Arka Ucunu Yükle'ye tıklayın.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Başarılı bir kurulumun ardından, **Lemonade Desktop App** içindeki **Download Manager**'da `flm:npu` işleminin tamamlandığını görmelisiniz.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Ardından mevcut FFLM modellerinden herhangi birini seçebilir ve NPU arka ucunu kullanmaya başlayabilirsiniz.

Belirli bir model için, istenen modeli [modeller sayfasından](https://fastflowlm.com/docs/models/qwen/) indirin ve belgede sağlanan Shell komutuyla doğrulayın.
```
flm run qwen3.5-4b-FLM
```
veya 
```
lemonade run qwen3.5-4b-FLM
```
 aracılığıyla
FLM modelleri en popüler mimarilerin bazılarını içerir (Gemma 3, Qwen 3, Llama 3 ve DeepSeek R1) ve 1 GB'ın altından 13 GB'ın üzerine kadar çeşitli boyutlarda gelir.
Lemonade, NPU'nuzu otomatik olarak algılar ve **FastFlowLM NPU** arka ucunu yükler.

<!-- @os:windows -->
> **İpucu:** En iyi NPU performansı için turbo modunu etkinleştirin:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Model Değiştirme

Adım 6'daki flash kart uygulaması NPU modellerinde de çalışır; yalnızca model adını değiştirin:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Sonraki Adımlar

Kendi donanımınızda çalışan yerel bir yapay zeka sunucunuz var; işte bundan sonra nereye gideceğiniz:

1. **Favori uygulamalarınızı bağlayın**: Lemonade, [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) ve [daha pek çok uygulama](https://lemonade-server.ai/marketplace) ile kutudan çıkar çıkmaz çalışır.

2. **Daha fazla model keşfedin**: Kodlama, akıl yürütme, görü ve daha fazlası için optimize edilmiş modelleri bulmak amacıyla tam [model kitaplığını](https://lemonade-server.ai/docs/server/server_models/) inceleyin. Nelerin mevcut olduğunu görmek için Lemonade Uygulamasını veya `lemonade list` komutunu kullanın.

3. **ROCm GPU hızlandırmasının kilidini açın**: Desteklenen bir AMD GPU'nuz varsa ROCm arka ucuna geçin: `lemonade config set llamacpp.backend=rocm`. [Desteklenen AMD GPU'lar](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations) sayfasına bakın.

4. **Tam API spesifikasyonunu okuyun**: Lemonade, sohbet tamamlamaları, gömme, ses transkripsiyonu, görüntü oluşturma, metinden konuşmaya ve daha fazlasını destekler. Her uç nokta için [Sunucu Spesifikasyonuna](https://lemonade-server.ai/docs/server/server_spec/) bakın.

5. **Katkıda bulunun**: Lemonade açık kaynaklıdır. [Katkı kılavuzuna](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) göz atın ve [İyi İlk Sorunları](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) arayın.