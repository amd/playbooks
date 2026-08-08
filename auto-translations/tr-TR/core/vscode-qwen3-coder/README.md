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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Bu kılavuz en az **32GB** sistem belleği gerektirir.
<!-- @device:end -->

## Genel Bakış

Kodlama ajanları, geliştiricilerin Büyük Dil Modelleri (LLM'ler) tarafından desteklenen yapay zeka ajanlarıyla iş birliği yaparak güçlendirilmesini sağlayan güçlü araçlardır. Terminal veya VS Code gibi geliştirme ortamlarına gömülebilirler ve bu da geliştiricinin iş akışına sorunsuz bir şekilde entegre olmalarını sağlar.

Bu eğitim, kodlama ajanını tamamen yerel makinenizde çalıştırmak için Cline, VS Code ve LM Studio'nun nasıl kullanılacağını göstermektedir.

## Neler Öğreneceksiniz

* Yazılım mühendisliği görevlerine yardımcı olmak için Cline kodlama ajanı ile VS Code'un nasıl çalıştırılacağı.
* Kodlama ajanlarının yerel çıkarımı için Cline'ın LM Studio ile iletişim kuracak şekilde nasıl yapılandırılacağı.
* Gerçek dünya yazılım mühendisliği görevlerini çözmek için yerel kodlama ajanlarının nasıl kullanılacağı.

## Bellek Yapılandırmasının Ayarlanması

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme
> **Not**: VS Code yüklü değilse, Ryzen AI Developer Center ile yükleyebilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarının Yüklenmesi

<!-- @require:lmstudio,vscode -->

## LM Studio'yu Başlatma ve Yapılandırma

Kodlama ajanına güç veren LLM'yi sunmak için LM Studio'yu kullanacağız.

- Arama çubuğuna `LM Studio` yazın ve uygulamayı başlatın. Aşağıdaki sayfa ile karşılaşacaksınız.

![LM Studio Başlangıç Ekranı](assets/initial-lm-studio.png)

Ardından, LLM'yi sistem üzerine yüklememiz gerekiyor. Büyük bir bağlam uzunluğuna sahip `Qwen3-Coder-30B-A3B` modelini kullanacağız. (Henüz yüklemediyseniz, kurmak için Model sekmesini kullanın).
- LM Studio penceresinin üst kısmındaki arama çubuğuna tıklayın veya `CTRL+L` tuşlarına basın. `Manually choose model load parameters` anahtarına tıklayın ve ardından Qwen3-Coder-30B-A3B modeline tıklayın.
- Bağlam uzunluğunu `4096`'dan `32768`'e değiştirin ve `GPU Offload` değerinin maksimumda olduğundan emin olun. Ardından `Load Model` düğmesine tıklayın.

![Model Seçimi](assets/model-list-zoomed.png)

Ajanın büyük kod tabanlarını işleyebilmesi ve yapılan değişiklikleri hatırlayabilmesi için büyük bir bağlam uzunluğu kullanıyoruz.

![Modeli Yapılandırma](assets/selecting-model-zoomed.png)

Ardından, LM Studio Sunucusunu etkinleştirmemiz gerekiyor.
- LM Studio'da sol taraftaki Developer sekmesine tıklayın veya `CTRL+2` tuşlarına basın.
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

![Sunucu Durumu](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
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
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## VS Code'u Başlatma ve Yapılandırma

VS Code'a Cline Uzantısını yükleyecek ve az önce oluşturduğumuz LM Studio sunucusuna bağlayacağız.
- Arama çubuğuna `VS Code` yazın ve uygulamayı başlatın.
- VS Code'un sol sütunundaki `Extensions` simgesine tıklayın ve `Cline` araması yapın. Ardından `Install` düğmesine tıklayın.

![Cline Uzantısını Yükleme](assets/installing-cline-vscode-extension.png)

- Sol tarafta bir Cline simgesi görünmelidir. Cline'ı açmak için bu simgeye tıklayın. `How will you use Cline?` sorusunu soran bir pencere açılacaktır. LM Studio üzerinden çalışan yerel bir LLM kullanacağımız için `Bring my own API Key` seçeneğini seçin ve `Continue` düğmesine basın.

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

Ardından, Cline'ı kurduğumuz LM Studio sunucusuyla iletişim kuracak şekilde yapılandırmamız gerekiyor.
- API Provider'ı `LM Studio` olarak ve modeli `Qwen3-Coder-30B-A3B-GGUF` olarak ayarlayın.

>**İpucu**: Daha yeni modeller mevcut olabilir. İsterseniz Qwen3.6 modellerini indirmeyi ve bunlara geçmeyi düşünebilirsiniz.


![Model Yapılandırması](assets/cline-model-configuration-zoomed.png)

## İlk projenizi oluşturma

Yerel ajanımızı bir web sitesi oluşturmak için kullanalım! VS Code'u, Cline'ın dosyaları oluşturacağı bir dizinde açın.
- Bunu yapmak için VS Code'un sol üst kısmındaki `File -> Open Folder` seçeneğine gidin ve `Documents` gibi bir klasör seçin.

![VS Code Boş Klasör](assets/open-cline-test.png)

Artık yerel kodlama ajanına komut vermeye hazırız.
- Sol sütundaki Cline uzantısına tıklayın ve ajanı başlatmak için bir istem girin. Örnek olarak şu istemi kullanalım:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Ajan daha sonra istem doğrultusunda dosyalar oluşturmaya başlayacaktır. Kullanıcı olarak, kodun VS Code içinde nasıl oluşturulduğunu aşağıda gösterildiği gibi izleyebilirsiniz. Cline bir dosya oluşturmak istediğinde her seferinde `Save` düğmesine tıklamanız gerekebilir.

![Cline Kod Üretimi](assets/cline-code-generation.png)

Yazılım oluşturulduktan sonra ajan işini tamamlar ve uygulamayı çalıştırabilirsiniz. Bu durumda ajan üç dosyaya yazmıştır: `index.html`, `script.js` ve `styles.css`. HTML dosyasına çift tıklayarak oluşturulan web sitesini yükleyip etkileşime geçebiliriz.

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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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

Web sitesini oluşturduktan sonra, web sitesini geliştirmek için Cline ile çalışmaya devam edebilirsiniz. İki olası geliştirme şunlardır:

- **Dokümantasyon**: Ajanın web sitesini belgeleyen bir `README.md` dosyası oluşturması için ajana `Add a README` şeklinde bir istem vermek yeterlidir.
- **Animasyon**: Web sitesine bir dizüstü bilgisayarda çalışan büyük bir dil modelini görsel olarak temsil eden bir animasyon oluşturmak için modeli `Add an animation that visually represents a large language model running on a laptop.` istemiyle yönlendirin.

Okuyucuyu bu kurulumu kullanarak başka uygulamalar oluşturmayı denemeye teşvik ediyoruz. Aşağıda denediğimiz bazı eğlenceli örnekler yer almaktadır:

- **Retro Arcade Oyunları**: Başka istemler deneyin. Ajanın aşağıdaki istemle `PyGame` paketini kullanarak Python'da retro tarzı oyunlar oluşturması da eğlenceli olabilir:

```code
Create a simple pong game using the PyGame python package.
```

- **Veri Analizi**: Kodlama ajanlarının özellikle yararlı olduğu bir alan da betik yazma ve veri analizidir. Bu, yerel modelin hisse senedi fiyatı görselleştirmesi için veri analizi yazılımı oluşturma yeteneğini sergilemek amacıyla kullanılan bir istemdir:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Kaynaklar

Kodlama Ajanları, Cline ve iş yüklerini şu şekilde çalıştırma hakkında daha fazla bilgi edinmek için aşağıda bazı ek kaynaklar bulunmaktadır:

* AMD LM Studio ortaklığı ve entegrasyonu hakkında daha fazla bilgi: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD Ryzen™ AI ve Radeon™ Grafik Kartlarında Cline'ı çalıştırmayı anlatan AMD Blog yazısı: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* AI PC'lerde yerel olarak kodlama ajanları çalıştırma hakkında Cline Blog yazısı: https://cline.bot/blog/local-models-amd