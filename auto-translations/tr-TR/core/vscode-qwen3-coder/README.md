<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Bu playbook, GitHub'ın render edemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Bu playbook, minimum **32GB** sistem belleği gerektirir.
<!-- @device:end -->

## Genel Bakış

Kodlama ajanları, geliştiricileri Büyük Dil Modelleri (LLM'ler) tarafından desteklenen yapay zeka ajanlarıyla iş birliği yoluyla güçlendiren araçlardır. Terminal veya VS Code gibi geliştirme ortamına gömülebilir ve bir geliştiricinin iş akışına sorunsuz entegrasyon sağlarlar.

Bu eğitim, Cline, VS Code ve LM Studio kullanarak bir kodlama ajanını tamamen yerel makinenizde nasıl çalıştıracağınızı göstermektedir.

## Neler Öğreneceksiniz

* Yazılım mühendisliği görevlerinde yardımcı olmak için Cline kodlama ajanıyla VS Code'u nasıl çalıştıracağınızı.
* Yerel çıkarım için Cline'ı LM Studio ile iletişim kuracak şekilde nasıl yapılandıracağınızı.
* Gerçek dünya yazılım mühendisliği görevlerini çözmek için yerel kodlama ajanlarını nasıl kullanacağınızı.

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme
> **Not**: VS Code yüklü değilse, Ryzen AI Developer Center ile yükleyebilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarını Yükleme

<!-- @require:lmstudio,vscode -->

## LM Studio'yu Başlatma ve Yapılandırma

Kodlama ajanını destekleyen LLM'yi sunmak için LM Studio kullanacağız.

- Arama çubuğunda `LM Studio` arayın ve uygulamayı başlatın. Aşağıdaki sayfa sizi karşılayacaktır.

![LM Studio İlk Ekran](assets/initial-lm-studio.png)

Ardından, LLM'yi sisteme yüklememiz gerekiyor. Büyük bir bağlam uzunluğuyla `Qwen3-Coder-30B-A3B` modelini kullanacağız. (Henüz yüklemediyseniz, Model sekmesini kullanarak yükleyin).
- LM Studio penceresinin üst kısmındaki arama çubuğuna tıklayın veya `CTRL+L` tuşlarına basın. `Manually choose model load parameters` anahtarına tıklayın ve ardından Qwen3-Coder-30B-A3B modeline tıklayın.
- Bağlam uzunluğunu `4096`'dan `32768`'e değiştirin ve `GPU Offload` değerinin maksimumda olduğundan emin olun. Ardından `Load Model`'e tıklayın.

![Model Seçimi](assets/model-list-zoomed.png)

Ajanın büyük kod tabanlarını işleyebilmesi ve yapılan değişiklikleri hatırlayabilmesi için büyük bir bağlam uzunluğu kullanıyoruz.

![Model Yapılandırması](assets/selecting-model-zoomed.png)

Ardından, LM Studio Sunucusunu etkinleştirmemiz gerekiyor.
- Sol taraftaki Developer sekmesine tıklayın veya LM Studio'da `CTRL+2` tuşlarına basın.
- Durum geçişini kontrol edin ve `Running` olarak ayarlandığından emin olun.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![Sunucu Durumu](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## VS Code'u Başlatma ve Yapılandırma

Cline Uzantısını VS Code'a yükleyeceğiz ve az önce oluşturduğumuz LM Studio sunucusuna bağlayacağız.
- Arama çubuğunda `VS Code` arayın ve uygulamayı başlatın.
- VS Code'un sol sütunundaki `Extensions` simgesine tıklayın ve `Cline` arayın. Ardından `Install` düğmesine tıklayın.

![Cline Uzantısını Yükleme](assets/installing-cline-vscode-extension.png)

- Sol tarafta bir Cline simgesi görünmelidir. Cline'ı açmak için buna tıklayın. `How will you use Cline?` soran bir pencere açılacaktır. LM Studio aracılığıyla çalışan yerel bir LLM kullanacağımız için `Bring my own API Key` seçeneğini seçin ve `Continue`'ya tıklayın.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Hesap Oluşturma](assets/cline-how-will-you-use-cline-zoomed.png)

Ardından, kurduğumuz LM Studio sunucusuyla iletişim kurmak için Cline'ı yapılandırmamız gerekiyor.
- API Sağlayıcısını `LM Studio` ve modeli `Qwen3-Coder-30B-A3B-GGUF` olarak ayarlayın.

>**İpucu**: Daha yeni modeller mevcut olabilir. İstenirse Qwen3.6 modellerini indirip geçiş yapmayı düşünün.


![Model Yapılandırması](assets/cline-model-configuration-zoomed.png)

## İlk Projenizi Oluşturma

Yerel ajanımızı kullanarak bir web sitesi oluşturalım! Cline'ın dosyaları oluşturacağı istediğiniz bir dizinde VSCode'u açın.
- Bunu yapmak için VS Code'un sol üst köşesindeki `File -> Open Folder` seçeneğine gidin ve `Documents` gibi bir klasör seçin.

![VS Code Boş Klasör](assets/open-cline-test.png)

Artık yerel kodlama ajanına komut vermeye hazırız.
- Sol sütundaki Cline uzantısına tıklayın ve ajanı başlatmak için bir komut girin. Örnek olarak aşağıdaki komutu kullanalım:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Ajan daha sonra komuta göre dosyalar oluşturmaya başlayacaktır. Kullanıcı olarak, aşağıda gösterildiği gibi VS Code'da oluşturulan kodu izleyebilirsiniz. Cline bir dosya oluşturmak istediğinde `Save`'e tıklamanız gerekebilir.

![Cline Kod Üretimi](assets/cline-code-generation.png)

Yazılımı oluşturduktan sonra ajan tamamlanır ve uygulamayı çalıştırabilirsiniz. Bu durumda ajan üç dosyaya yazdı: `index.html`, `script.js` ve `styles.css`. HTML dosyasına çift tıklayarak oluşturulan web sitesini yükleyebilir ve etkileşime girebilirsiniz.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

## Sonraki Adımlar

Web sitesini oluşturduktan sonra, web sitesini geliştirmek için Cline ile çalışmaya devam edebilirsiniz. İki olası iyileştirme şunlardır:

- **Dokümantasyon**: Ajana `Add a README` komutu vermek, ajanın web sitesini belgeleyen bir `README.md` dosyası oluşturması için yeterlidir.
- **Animasyon**: Modele `Add an animation that visually represents a large language model running on a laptop.` komutunu vererek web sitesine bir animasyon ekleyin.

Okuyucuyu bu kurulumu kullanarak başka uygulamalar oluşturmayı denemeye teşvik ediyoruz. Aşağıda denediğimiz bazı eğlenceli örnekler verilmiştir:

- **Retro Arcade Oyunları**: Başka komutlar deneyin. Ajanın aşağıdaki komutla `PyGame` paketini kullanarak Python'da retro tarzı oyunlar oluşturması da eğlenceli olabilir:

```code
Create a simple pong game using the PyGame python package.
```

- **Veri Analizi**: Kodlama ajanlarının özellikle yararlı olduğu alanlardan biri betik yazma ve veri analizidir. Bu, yerel modelin hisse senedi fiyatı görselleştirmesi için veri analizi yazılımı oluşturma yeteneğini sergilemek amacıyla hazırlanmış bir komuttur:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Kaynaklar

Kodlama Ajanları, Cline ve iş yüklerini çalıştırma hakkında daha fazla bilgi edinmek için aşağıdaki ek kaynaklar mevcuttur:

* AMD LM Studio ortaklığı ve entegrasyonu hakkında daha fazla bilgi: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD Ryzen™ AI ve Radeon™ Grafik Kartlarında Cline çalıştırmayı anlatan AMD Blog: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Yapay Zeka PC'lerde yerel olarak kodlama ajanları çalıştırmaya ilişkin Cline Blog: https://cline.bot/blog/local-models-amd