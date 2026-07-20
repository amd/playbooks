<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Bu kılavuz, GitHub'ın işleyemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Bu kılavuz en az **32GB** sistem belleği gerektirmektedir.
<!-- @device:end -->

## Genel Bakış

Kodlama ajanları, geliştiricilerin Büyük Dil Modelleri (LLM) tarafından desteklenen yapay zeka ajanlarıyla işbirliği yapmasını sağlayan güçlü araçlardır. Terminal veya VS Code gibi geliştirme ortamlarına gömülebilirler ve bu sayede bir geliştiricinin iş akışına kusursuz bir şekilde entegre olabilirler.

Bu eğitim, tamamen yerel makinenizde bir kodlama ajanı çalıştırmak için Cline, VS Code ve LM Studio'nun nasıl kullanılacağını göstermektedir.

## Öğrenecekleriniz

* Yazılım mühendisliği görevlerine yardımcı olması için Cline kodlama ajanıyla VS Code'un nasıl çalıştırılacağı.
* Kodlama ajanlarının yerel çıkarımı için LM Studio ile iletişim kuracak şekilde Cline'ın nasıl yapılandırılacağı.
* Gerçek dünya yazılım mühendisliği görevlerini çözmek için yerel kodlama ajanlarının nasıl kullanılacağı.

## Bellek Yapılandırmasının Ayarlanması

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme
> **Not**: VS Code kurulu değilse, Ryzen AI Developer Center ile kurabilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarının Kurulumu

<!-- @require:lmstudio,vscode -->

## LM Studio'nun Başlatılması ve Yapılandırılması

Kodlama ajanını çalıştıran LLM'i sunmak için LM Studio'yu kullanacağız.

- Arama çubuğunda `LM Studio` araması yapın ve uygulamayı başlatın. Aşağıdaki sayfayla karşılaşacaksınız.

![LM Studio Initial Screen](assets/initial-lm-studio.png)

Ardından, LLM'i sisteme yüklememiz gerekiyor. Büyük bir bağlam uzunluğuna sahip `Qwen3-Coder-30B-A3B` modelini kullanacağız. (Henüz kurmadıysanız, kurmak için Model sekmesini kullanın).
- LM Studio penceresinin üst kısmındaki arama çubuğuna tıklayın veya `CTRL+L` tuşlarına basın. `Manually choose model load parameters` anahtarına tıklayın ve ardından Qwen3-Coder-30B-A3B modeline tıklayın.
- Bağlam uzunluğunu `4096`'dan `32768`'e değiştirin ve `GPU Offload` değerinin maksimumda olduğundan emin olun. Ardından `Load Model`'e tıklayın

![Selecting Model](assets/model-list-zoomed.png)

Büyük bir bağlam uzunluğu kullanıyoruz, böylece ajan büyük kod tabanlarını işleyebilir ve yapılan değişiklikleri hatırlayabilir.

![Configuring Model](assets/selecting-model-zoomed.png)

Ardından, LM Studio Sunucusunu etkinleştirmemiz gerekiyor.
- LM Studio'da soldaki Developer sekmesine tıklayın veya `CTRL+2` tuşlarına basın.
- Durum düğmesini kontrol edin ve `Running` olarak ayarlandığından emin olun.

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

![Server Status](assets/lm-studio-server-status.png)

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

## VS Code'un Başlatılması ve Yapılandırılması

VS Code'a Cline Uzantısını kuracağız ve az önce oluşturduğumuz LM Studio sunucusuna bağlayacağız.
- Arama çubuğunda `VS Code` araması yapın ve uygulamayı başlatın.
- VS Code'un sol sütunundaki `Extensions` simgesine tıklayın ve `Cline` araması yapın. Ardından `Install` düğmesine tıklayın.

![Installing Cline Extension](assets/installing-cline-vscode-extension.png)

- Solda bir Cline simgesi bulunmalıdır. Cline'ı açmak için buna tıklayın. `How will you use Cline?` sorusunu soran bir pencere açılacaktır. LM Studio üzerinden çalışan yerel bir LLM kullanacağımız için `Bring my own API Key` seçeneğini seçin ve `Continue`'a basın.

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

![Account Creation](assets/cline-how-will-you-use-cline-zoomed.png)

Ardından, Cline'ı kurduğumuz LM Studio sunucusuyla iletişim kuracak şekilde yapılandırmamız gerekiyor.
- API Provider'ı `LM Studio` ve modeli `Qwen3-Coder-30B-A3B-GGUF` olarak ayarlayın.

>**İpucu**: Daha yeni modeller mevcut olabilir. İsterseniz Qwen3.6 modellerini indirmeyi ve bunlara geçmeyi düşünün.


![Model Configuration](assets/cline-model-configuration-zoomed.png)

## İlk Projenizi Oluşturma

Bir web sitesi oluşturmak için yerel ajanımızı kullanalım! VS Code'u, Cline'ın dosyaları oluşturacağı bir dizinde açın.
- Bunu yapmak için, VS Code'un sol üst kısmındaki `File -> Open Folder` menüsüne gidin ve `Documents` gibi bir klasör seçin.

![VS Code Empty Folder](assets/open-cline-test.png)

Artık yerel kodlama ajanına komut vermeye hazırız.
- Sol sütundaki Cline uzantısına tıklayın ve ajanı başlatmak için bir istem (prompt) girin. Örnek olarak, aşağıdaki istemi kullanalım:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Ajan daha sonra istemine göre dosyalar oluşturmaya başlayacaktır. Bir kullanıcı olarak, kodun VS Code içinde nasıl oluşturulduğunu aşağıda gösterildiği gibi izleyebilirsiniz. Cline her dosya oluşturmak istediğinde `Save`'e tıklamanız gerekebilir.

![Cline Code Generation](assets/cline-code-generation.png)

Yazılımı oluşturduktan sonra, ajan görevini tamamlar ve uygulamayı çalıştırabilirsiniz. Bu durumda, ajan üç dosyaya yazdı: `index.html`, `script.js` ve `styles.css`. HTML dosyasına çift tıklayarak oluşturulan web sitesini yükleyebilir ve etkileşime geçebiliriz.

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

Web sitesini oluşturduktan sonra, web sitesini iyileştirmek için Cline ile çalışmaya devam edebilirsiniz. İki olası iyileştirme şunlardır:

- **Belgelendirme**: Aracıyı `Add a README` ile yönlendirmeniz, aracının web sitesini belgeleyen bir `README.md` dosyası oluşturması için yeterlidir.
- **Animasyon**: Modeli, bir dizüstü bilgisayarda çalışan büyük bir dil modelini görsel olarak temsil eden bir animasyon oluşturmak için `Add an animation that visually represents a large language model running on a laptop.` ile yönlendirin.

Okuyucuyu bu kurulumu kullanarak başka uygulamalar oluşturmayı denemeye teşvik ediyoruz. Aşağıda denediğimiz bazı eğlenceli örnekler yer almaktadır:

- **Retro Atari Oyunları**: Başka istemler deneyin. Aracının, aşağıdaki istemle `PyGame` paketini kullanarak Python'da retro tarzı oyunlar oluşturması da eğlenceli olabilir:

```code
Create a simple pong game using the PyGame python package.
```

- **Veri Analizi**: Kodlama aracılarının özellikle yararlı olduğu bir alan da betik yazma ve veri analizidir. Bu, yerel modelin hisse senedi fiyat görselleştirmesi için veri analizi yazılımı oluşturma becerisini sergilemek amacıyla kullanılan bir istemdir:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Kaynaklar

Kodlama Aracıları, Cline ve iş yüklerinin çalıştırılması hakkında daha fazla bilgi edinmek için aşağıda bazı ek kaynaklar bulunmaktadır 

* AMD LM Studio ortaklığı ve entegrasyonu hakkında daha fazla bilgi: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD Ryzen™ AI ve Radeon™ Grafik Kartlarında Cline'ı çalıştırmayı anlatan AMD Blogu: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* AI PC'lerde yerel olarak kodlama aracıları çalıştırma üzerine Cline Blogu: https://cline.bot/blog/local-models-amd