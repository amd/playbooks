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

[OpenHands](https://github.com/All-Hands-AI/OpenHands), kod yazabilen, komut
çalıştırabilen, web'de gezinebilen ve gerçek bir çalışma alanında dosyaları
düzenleyebilen bir yapay zeka yazılım aracısıdır. Bir sohbet penceresinden
önerileri kopyalamak yerine, aracıyı bir proje klasörüne yönlendirir ve işi
yapmasına izin verirsiniz: bir özellik uygulamak, bir hatayı düzeltmek, test
yazmak veya bir kod tabanını açıklamak.

[Agent Canvas](https://github.com/OpenHands/agent-canvas), OpenHands'ı
çalıştırmak için önerilen tarayıcı arayüzüdür. Tek bir `agent-canvas` komutu,
aracı sunucusunu, otomasyon arka ucunu ve web ön ucunu birlikte başlatır,
böylece tarayıcınızdan aracıyla bir konuşma yürütebilirsiniz.

Her şeyi AMD sisteminizde tutmak için aracı, Lemonade Server tarafından
sunulan yerel bir modelle konuşur. Lemonade bu modeli OpenAI uyumlu bir API
üzerinden sunar, böylece Agent Canvas onu diğer OpenAI tarzı uç noktalar gibi
yapılandırabilirken model, kodunuz ve konuşma bağlamının tümü makinenizde
kalır.

Bu kılavuzda, yerel bir model başlatacak, Agent Canvas'ı çalıştıracak, onu bu
modele yönlendirecek ve gerçek bir proje klasörüne karşı ilk kodlama görevinizi
çalıştıracaksınız.

## Neler Öğreneceksiniz

- Lemonade Server'ı nasıl başlatacağınızı ve yerel bir modelin sohbet
  isteklerini yanıtladığını nasıl doğrulayacağınızı
- Agent Canvas'ı npm paketinden nasıl kuracağınızı ve başlatacağınızı
- Agent Canvas'ı, yerel bir Lemonade modelini LLM olarak kullanacak şekilde
  nasıl yapılandıracağınızı
- Bir OpenHands konuşması nasıl başlatılır ve aracının bir çalışma alanında
  dosyaları düzenlemesini ve komutları çalıştırmasını nasıl izlersiniz
- Aracının neyi değiştirdiğini nasıl inceleyeceğinizi ve takip mesajlarıyla
  onu nasıl yönlendireceğinizi

## Temel Kavramlar

| Kavram | Nedir | Bu kılavuzdaki yeri |
| --- | --- | --- |
| Lemonade Server | AMD donanımı için oluşturulmuş, OpenAI uyumlu bir API sunan yerel bir LLM sunum platformu. Verileriniz asla makinenizden çıkmaz. | Aracıyı çalıştıran modeli çalıştırır. |
| OpenHands | Bir çalışma alanı içinde dosyaları okuyup düzenleyen, kabuk komutları çalıştıran ve web'de gezinen bir yapay zeka yazılım aracısı. | Sohbetten yönettiğiniz aracı. |
| Agent Canvas | OpenHands konuşmalarını çalıştıran ve araç çağrılarını ile dosya değişikliklerini gösteren tarayıcı arayüzü ve arka uç. | Yığını başlatır ve konuşmanıza ev sahipliği yapar. |
| Çalışma Alanı | Aracının okumasına ve değiştirmesine izin verilen proje klasörü. | Aracının düzenlemelerinin ve komutlarının hedefi. |

<!-- @device:stx,krk -->
> [!NOTE]
> Kodlama aracısı iş akışları daha büyük bir model ve bağlam penceresinden
> faydalanır. En az 32 GB sistem belleği kullanın ve daha büyük GGUF modelleri
> için 64 GB veya daha fazlasını tercih edin.
<!-- @device:end -->

## Ön Koşullar

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Şunlara ihtiyacınız var:

- Aşağıdaki modeli sunabilecek şekilde kurulmuş Lemonade Server.
- Node.js 22.12 veya üstü ve `npm` (`agent-canvas` CLI'si tarafından
  kullanılır).
- Agent Canvas'ın aracı sunucu ortamını yönetmek için kullandığı Python paket
  yöneticisi `uv`. Sisteminizde henüz yoksa, Agent Canvas'ı başlatmadan önce
  [uv kurulum kılavuzundan](https://docs.astral.sh/uv/getting-started/installation/)
  kurun.
- Üzerinde çalışılacak bir proje klasörü. Bu, aracının üzerinde çalışmasını
  istediğiniz herhangi bir yerel git deposu veya kod dizini olabilir.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Lemonade Server'ı Başlatın

Modeli Lemonade CLI'sinden başlatın:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade, OpenAI uyumlu bir API'yi şu adreste sunar:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Yerel Modeli Doğrulayın

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

Bu bir `choices` dizisi döndürürse, Lemonade Agent Canvas için hazırdır.

## 3. Agent Canvas'ı Kurun ve Başlatın

Yayınlanan Agent Canvas paketini genel olarak kurun:

```bash
npm install -g @openhands/agent-canvas
```

Ardından tam yığını bir terminalden başlatın:

```bash
agent-canvas
```

Varsayılan olarak Agent Canvas `http://localhost:8000` üzerinde başlar. Bu
URL'yi tarayıcınızda açın. 8000 portu zaten kullanımdaysa, Agent Canvas'ı
başlatırken `--port` (veya `-p`) parametresini geçirin:

```bash
agent-canvas --port 3000
```

Aynı komut Windows'ta PowerShell'de de çalışır. Ardından bunun yerine
`http://localhost:3000` adresini açın. Varsayılan yerel arka uç, ana ekranda
sağlıklı olarak görünmelidir.

`agent-canvas` komutu, aracı sunucusunu, otomasyon arka ucunu ve web ön ucunu
birlikte başlatır. OpenHands'ı yerel olarak çalıştırmak için yalnızca bu tek
komuta ihtiyacınız vardır.

## 4. Yerel LLM'yi Yapılandırın

İlk başlatmada, Agent Canvas bir katılım akışı açar. Bu akışta:

1. Aracı olarak **OpenHands**'i seçili tutun ve **Next**'e tıklayın.
2. **Set up your LLM** ekranında **Advanced**'i seçin.
3. **Authentication**'ı **API key** olarak tutun.
4. **Custom Model**'i `openai/Qwen3.6-35B-A3B-GGUF` olarak ayarlayın.
5. **Base URL**'i `http://127.0.0.1:13305/api/v1` olarak ayarlayın.
6. **API Key** için `lemonade-local` gibi boş olmayan herhangi bir yer
   tutucu değer girin. Lemonade gerçek bir anahtar gerektirmez, ancak
   OpenHands istemcisinin göndermesi için bir değere ihtiyacı vardır.
7. **Next**'e tıklayın.

Tamamlanan Gelişmiş ayarlar şöyle görünmelidir. API anahtarı alanı arayüz
tarafından maskelenir.

![Agent Canvas, Lemonade modeli ve yerel taban URL'siyle ilk kullanım LLM Gelişmiş ayarları](assets/01-llm-advanced-settings.png)

Agent Canvas bu değerleri bir LLM profili olarak kaydeder. Sürümünüz bu profile
bir ad vermenizi isterse, `lemonade-local` gibi boşluksuz bir ad kullanın.
Daha sonra modelleri değiştirirseniz, **Settings > LLM** menüsünü açın ve aynı
Gelişmiş alanları güncelleyin. Sohbet giriş alanından `/model` komutuyla
kayıtlı profiller arasında geçiş yapabilirsiniz.

## 5. Bir Çalışma Alanı Açın

Aracı yalnızca seçtiğiniz bir çalışma alanı içindeki dosyaları okuyabilir ve
değiştirebilir. Bir göreve başlamadan önce, Agent Canvas'ı proje klasörünüze
yönlendirin:

1. Ana ekrandan **Open Workspace**'i seçin.
2. Projenizi içeren klasörü seçin (örneğin, aracının üzerinde çalışmasını
   istediğiniz bir git deposu).
3. O çalışma alanında yeni bir konuşma başlatın.

Aracının yaptığı her şey—dosyaları okumak, komutları çalıştırmak, kodu
düzenlemek—o çalışma alanıyla sınırlıdır.

![Katılımdan sonra Agent Canvas ana ekranı](assets/02-agent-canvas-home.png)
## 6. İlk Kodlama Görevinizi Çalıştırın

Çalışma alanı açık ve yerel LLM seçiliyken, sohbete somut bir görev yazın. İyi bir ilk görev küçük ve doğrulanabilir olmalıdır, örneğin:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Konuşma zaman çizelgesini izleyin. OpenHands şunları yapacaktır:

- Yerleşimi anlamak için çalışma alanını okur.
- İstenen fonksiyon ve test bloğuyla `hello.py` dosyasını oluşturur.
- İsteğe bağlı olarak çıktıyı doğrulamak için `python3 hello.py` komutunu çalıştırır.
- Yaptıklarını ve varsa komut çıktısını sohbette raporlar.

Çalışma alanında yeni dosyanın belirdiğini ve aracının son mesajının yaptığı değişikliği açıkladığını görmelisiniz. Bu, ödül anıdır: aracı proje klasörünüzde gerçek kod yazdı ve çalıştırdı.

## 7. Aracıyı Gözden Geçirin ve Yönlendirin

Aracı bir adımı bitirdikten sonra, bir sonraki adımı kabul etmeden önce çalışmasını gözden geçirin:

- **Dosya değişiklikleri**: neyin eklendiğini, değiştirildiğini veya silindiğini tam olarak görmek için çalışma alanı dosya tarayıcısını veya aracının fark (diff) görünümünü kullanın.
- **Komut çıktısı**: standart çıktıyı, standart hatayı ve çıkış kodunu görmek için aracının çalıştırdığı herhangi bir komutu genişletin.
- **Devam adımları**: sonuç istediğiniz gibi değilse, aynı konuşmada bir düzeltmeyle yanıt verin. Aracı önceki bağlamı korur ve aynı dosyalar üzerinde yinelemeye devam eder.

Örneğin, test beklenen selamlamayı yazdırmadıysa, şu şekilde yanıt verin:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Aracı dosyayı yeniden okuyacak, komutu çalıştıracak, sorunu teşhis edecek ve dosyayı tekrar düzenleyecektir—hepsi aynı konuşma içinde.

## Sorun Giderme

- **`agent-canvas` PATH üzerinde değil:** `npm install -g @openhands/agent-canvas` ile yeniden yükleyin ve npm global ikili dosya dizininin PATH üzerinde olduğunu doğrulayın. Windows'ta `npm config get prefix` komutunu çalıştırın; döndürülen dizin, genellikle `%APPDATA%\npm` veya `%USERPROFILE%\.npm-global`, yeni bir terminalden `agent-canvas` başlatılabilmeden önce kullanıcı PATH'inizde olmalıdır.
- **`npm install -g` bir izin hatasıyla başarısız oluyor:** kullanıcıya ait bir global npm dizini yapılandırın, ardından terminali yeniden açın ve Agent Canvas'ı tekrar yükleyin.

  <!-- @os:linux -->
  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
  <!-- @os:end -->

  <!-- @os:windows -->
  ```powershell
  New-Item -ItemType Directory -Force "$env:USERPROFILE\.npm-global"
  npm config set prefix "$env:USERPROFILE\.npm-global"
  $env:Path = "$env:USERPROFILE\.npm-global;$env:Path"
  npm install -g @openhands/agent-canvas
  ```

  Windows PATH değişikliğini kalıcı hale getirmek için, **Settings > System > About > Advanced system settings > Environment Variables** üzerinden kullanıcı PATH'inize `%USERPROFILE%\.npm-global` ekleyin ve yeni bir terminal açın.
  <!-- @os:end -->
- **Arayüz yükleniyor ama arka uç sağlıksız görünüyor:** aracı sunucusunun başlamayı tamamlaması için birkaç saniye bekleyin, ardından yenileyin. Sağlıksız kalmaya devam ederse, `agent-canvas`'ı yeniden başlatın ve hataları görmek için terminal çıktısını kontrol edin.
- **Lemonade sohbet istekleri bir bağlantı hatasıyla başarısız oluyor:** `curl -fsS "http://127.0.0.1:13305/api/v1/health"` komutunun başarılı olduğunu ve Lemonade'in modeli `lemonade status` ile hâlâ sunmaya devam ettiğini doğrulayın.
- **Aracı bir bağlam uzunluğu veya token sınırı mesajıyla hata veriyor:** Lemonade'i daha büyük bir `ctx_size` ile (örneğin `ctx_size=65536`) yeniden başlatın ve aracının aşırı büyük bir geçmiş taşımaması için yeni bir konuşma başlatın.
- **Aracı düşük kaliteli veya eksik düzenlemeler üretiyor:** Lemonade'de daha büyük bir modele geçin veya aracıya daha küçük, daha somut bir görev verin ve bir sonraki değişikliği istemeden önce bitirmesine izin verin.
- **`uv` eksik:** [uv kurulum kılavuzundan](https://docs.astral.sh/uv/getting-started/installation/) yükleyin.
  Agent Canvas, aracı sunucusu Python ortamını yönetmek için `uv` kullanır.

## Sonraki Adımlar

- Aynı çalışma alanında, bir birim test dosyası eklemek veya bilinen bir hatayı düzeltmek gibi daha büyük bir görevi deneyin ve değişikliği tutmadan önce aracının farkını (diff) gözden geçirin.
- Aracının çalışırken sorunları okuyabilmesi veya güncellemeler yayınlayabilmesi için **Customize** altında GitHub veya Slack gibi bir MCP sunucusu bağlayın.
- Birden fazla LLM profili kaydedin (hızlı küçük bir model ve daha güçlü büyük bir model) ve konuşma sırasında bunlar arasında `/model` ile geçiş yapın.
- Tekrar eden geliştirme döngülerini zamanlanmış veya olay tetiklemeli aracı çalıştırmalarına dönüştürmek için [OpenHands otomasyonlarına](https://docs.openhands.dev/openhands/usage/automations/overview) geçin.

## Kaynaklar

- [OpenHands belgeleri](https://docs.openhands.dev/)
- [Agent Canvas genel bakış](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas kurulumu](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM profilleri ve model yapılandırması](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server belgeleri](https://lemonade-server.ai/docs)