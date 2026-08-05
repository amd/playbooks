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

Geliştiriciler zamanlarının büyük bir kısmını küçük, tekrarlayan döngülerde
harcarlar: etiketlenmiş pull request'leri incelemek, GitHub yorumlarını
yanıtlamak, yeni sorunları önceliklendirmek, Slack konuşmalarını günlük
toplantı notlarına veya olay takip kayıtlarına dönüştürmek ve sürüm ya da
araştırma sinyallerini izlemek. Her döngü tanıdıktır ama yine de muhakeme
gerektirir: doğru bağlamı toplamak, neyin önemli olduğuna karar vermek ve
ekibin zaten çalıştığı yere net bir güncelleme yayınlamak.

[OpenHands otomasyonları](https://docs.openhands.dev/openhands/usage/automations/overview)
bu döngüleri zamanlanmış veya olay tetiklemeli aracı konuşmalarına dönüştürür:
bir yapay zeka yazılım aracısının bağlamı okuyabildiği, araçları
çağırabildiği ve bir güncelleme üretebildiği çalıştırmalar. OpenHands
eklenti kataloğundaki paylaşılan otomasyon şablonları; GitHub pull request
incelemesi, depo izleme, Linear sorun önceliklendirmesi, olay sonrası
değerlendirmeler, Slack günlük toplantı özetleri ve araştırma özetleri için
şu deseni izler: bir otomasyon uyanır, bağlamı almak için GitHub veya Slack
gibi yapılandırılmış entegrasyonları kullanır, bu bağlam üzerinde büyük bir
dil modeliyle (LLM) muhakeme yapar ve bir sonucu geri yazar.

[Agent Canvas](https://github.com/OpenHands/agent-canvas), bu otomasyonları
oluşturmak ve test etmek için kullanılan yerel kontrol düzlemidir. Bu
playbook'ta, aracı konuşmalarını yürüten arka plan işlemi olan bir OpenHands
Agent Server çalıştırır ve aracıyı GitHub ve Slack gibi harici hizmetlere
bağlar.

İş akışını AMD sisteminizde tutmak için aracı, Lemonade Server tarafından
sunulan yerel bir modelle konuşur. Lemonade bu modeli OpenAI uyumlu bir API
üzerinden sunar, böylece Agent Canvas onu uzak bir OpenAI tarzı uç nokta gibi
yapılandırabilirken model, istem ve iş akışı bağlamı yerel kalır.

Bu playbook'ta somut bir otomasyon oluşturacaksınız: zamanlanmış bir
GitHub'dan Slack'e geliştirme özeti. Bu otomasyon, son depo etkinliğini
incelemek için GitHub'ı, özeti yayınlamak için Slack'i, otomasyonu
yapılandırmak ve test etmek için Agent Canvas API çağrılarını ve LLM'yi
yerel olarak çalıştırmak için Lemonade'i kullanır.

![GitHub MCP, OpenHands otomasyonu, Lemonade Server ve Slack MCP'yi gösteren mimari diyagram](assets/00-architecture-overview.png)

## Neler Öğreneceksiniz

- Lemonade Server'ı nasıl başlatacağınızı ve yerel bir modelin sohbet
  isteklerini yanıtladığını nasıl doğrulayacağınızı
- Agent Canvas'ı nasıl başlatacağınızı ve Agent Server'ını yerel bir LLM'ye
  nasıl yönlendireceğinizi
- Agent Server API'si aracılığıyla GitHub ve Slack Model Context Protocol
  (MCP) sunucularını nasıl kuracağınızı
- Slack'e bir geliştirme özeti yayınlayan zamanlanmış bir OpenHands
  otomasyonunu nasıl oluşturup çalıştıracağınızı
- En yaygın yerel model ve otomasyon hatalarını nasıl gidereceğinizi

## Temel Kavramlar

| Kavram | Nedir | Bu playbook'ta nereye uyuyor |
| --- | --- | --- |
| Lemonade Server | AMD donanımı için oluşturulmuş, OpenAI uyumlu bir API sunan yerel bir LLM sunum platformu. Verileriniz asla makinenizden çıkmaz. | Aracıyı çalıştıran modeli barındırır. |
| OpenHands Agent Server | OpenHands aracı konuşmalarını yürüten arka plan işlemi. | Aracıyı, LLM profilini ve MCP sunucularını barındırır. |
| Agent Canvas | Agent Server'ı ve aracı çalıştırmalarını incelemek için bir kullanıcı arayüzünü çalıştıran OpenHands için yerel kontrol düzlemi. | Arka planları başlatır ve çağırdığınız API'yi sağlar. |
| MCP sunucusu | Bir aracıya GitHub veya Slack gibi harici bir hizmet için araçlar sağlayan bir Model Context Protocol sunucusu. | Aracının GitHub'ı okumasını ve Slack'e yazmasını sağlar. |
| OpenHands otomasyonu | Bağlamı alan, üzerinde muhakeme yapan ve bir sonucu bir yere yazan zamanlanmış veya olay tetiklemeli bir aracı konuşması. | Burada oluşturduğunuz GitHub'dan Slack'e özet. |

<!-- @device:stx,krk -->
> [!NOTE]
> Kodlama aracısı iş akışları, daha büyük bir model ve bağlam penceresinden
> fayda görür. En az 32 GB sistem belleği kullanın ve daha büyük GGUF
> modelleri için 64 GB veya daha fazlasını tercih edin.
<!-- @device:end -->

## Ön Koşullar

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Şunlara ihtiyacınız var:

- Standart
  [Lemonade kurulum kılavuzu](https://lemonade-server.ai/docs/guide/install/)
  izlenerek kurulmuş Lemonade Server.
- Yayınlanan Agent Canvas CLI'sini kurmak ve MCP sunucularını `npx` ile
  çalıştırmak için kullanılan Node.js 22.12 veya üzeri ve `npm`.
- Şema tabanlı aracı ayarları, `LLMSummarizingCondenserSettings.max_tokens`
  ve LLM `custom_tokenizer` desteği içeren güncel, yayınlanmış bir
  `@openhands/agent-canvas` paketi.
- Agent Server ortamında bulunan Python `transformers` paketi.
  `custom_tokenizer` ayarlandığında sohbet şablonu belirteç sayımı için
  gereklidir.
- Özetlenmesini istediğiniz depoya okuma erişimi olan bir GitHub belirteci.
- `chat:write` ve kanal okuma erişimine sahip bir Slack bot belirteci
  (`xoxb-...`).
- Bir Slack takım kimliği (`T...`).
- Özetin yayınlanması gereken bir Slack kanal kimliği (`C...`).

Otomasyonu test etmeden önce Slack uygulamasını hedef kanala davet edin.

## Bu Playbook'ta Kullanılan Değişkenler

<!-- @device:halo,halo_box,stx,krk -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
export OPENHANDS_LLM_MODEL="openai/${LEMONADE_MODEL}"
export QWEN_CUSTOM_TOKENIZER="Qwen/Qwen3.6-35B-A3B"
export CONDENSER_MAX_TOKENS="56000"
```

Aşağıdaki değerler, sonraki adımlarda Agent Canvas kullanıcı arayüzüne
girilir. Bunları buradan kopyalayabilmek için burada ayarlayın:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

`GITHUB_REPO_FILTER` için açık bir `owner/repo` değeri kullanın. Geniş
kuruluş joker karakterleri, yerel modeller için çok fazla MCP bağlamı
döndürebilir.

## 1. Lemonade Server'ı Başlatın

Modeli Lemonade CLI'den başlatın:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade, OpenAI uyumlu bir API'yi şu adreste sunar:

```text
http://127.0.0.1:13305/api/v1
```

İsteğe bağlı: Agent Canvas veya otomasyon çalıştırıcısı aynı makinede
değilse, Lemonade uç noktasını güvenli bir tünel üzerinden yayınlayın ve
LLM temel URL'si olarak HTTPS URL'sini kullanın:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Yerel Modeli Doğrulayın

Lemonade'in seçilen modeli sunabildiğini doğrulayın:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Ardından küçük bir sohbet isteği gönderin:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Bu bir `choices` dizisi döndürürse, Lemonade Agent Canvas için hazırdır.
## 3. Agent Canvas'ı Başlatma

Yayınlanan Agent Canvas paketini yükleyin ve tam yığını başlatın:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Genel npm install işlemi izin hatasıyla başarısız olursa, aşağıdaki npm
izinleri sorun giderme bölümüne bakın.

Varsayılan olarak Agent Canvas, `http://localhost:8000` adresinde başlar.
Bu URL'yi tarayıcınızda açın. Varsayılan yerel arka uç ana ekranda sağlıklı
olarak görünmelidir.

`agent-canvas` komutu, agent sunucusunu, otomasyon arka ucunu ve web ön
yüzünü birlikte başlatır. OpenHands'i yerel olarak çalıştırmak için yalnızca
bu tek komuta ihtiyacınız vardır. Bu kılavuzun geri kalanı, her şeyi
tarayıcınızdaki Agent Canvas kullanıcı arayüzü üzerinden yapılandırır.

## 4. Kullanıcı Arayüzünde Yerel LLM'i Yapılandırma

İlk başlatmada, Agent Canvas bir katılım akışı açar. Bu akışta:

1. Agent olarak **OpenHands**'in seçili kalmasına izin verin ve **Next**'e
   tıklayın.
2. **Set up your LLM** ekranında **Advanced**'i seçin.
3. **Authentication**'ı **API key** olarak bırakın.
4. **Custom Model**'i `OPENHANDS_LLM_MODEL` değerine, yani
   `openai/Qwen3.6-35B-A3B-GGUF` değerine ayarlayın.
5. **Base URL**'i `http://127.0.0.1:13305/api/v1` olarak ayarlayın.
6. **API Key** için `lemonade-local` gibi boş olmayan bir yer tutucu değer
   girin. Lemonade gerçek bir anahtar gerektirmez, ancak OpenHands
   istemcisinin gönderecek bir değere ihtiyacı vardır.

Bağlantı alanları şu şekilde görünmelidir. API anahtarı alanı kullanıcı
arayüzü tarafından maskelenir.

![Lemonade modeli ve yerel taban URL'siyle Agent Canvas ilk kullanım LLM Advanced ayarları](assets/01-llm-advanced-settings.png)

Ardından **All**'ı seçin ve ekstra yerel model alanlarını ayarlayın:

1. **Custom Tokenizer**'a kaydırın ve `Qwen/Qwen3.6-35B-A3B` olarak ayarlayın.
2. **LiteLLM Extra Body**'ye kaydırın ve `{"enable_thinking": true}` olarak
   ayarlayın.
3. **Next**'e tıklayın.

![Qwen özel tokenizer ile Agent Canvas ilk kullanım LLM All sekmesi](assets/02-llm-all-tokenizer-settings.png)

![LiteLLM extra body yapılandırılmış Agent Canvas ilk kullanım LLM All sekmesi](assets/03-llm-all-extra-body-settings.png)

LLM ayarları şunları göstermelidir:

| Alan | Değer |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/` ön eki, LiteLLM'e Lemonade uç noktasına karşı OpenAI uyumlu istek
biçimlendirmesi kullanmasını söyler. Özel tokenizer, GGUF model için orijinal
Hugging Face tokenizer'ıdır; bu, OpenHands'in yerel model sunucusunun
gördüğü aynı sohbet şablonu belirteçlerini saymasını sağlar. Mevcut ilk
kullanım LLM formu condenser ayarlarını göstermez. Agent Canvas
derlemeniz condenser ayarlarını daha sonra **Settings > LLM** altında
gösterirse, `llm_summarizing` kullanın ve maksimum belirteç sayısını
Lemonade bağlam penceresinin altında, örneğin `56000` olarak ayarlayın.

## 5. GitHub ve Slack MCP Sunucularını Yükleme

Agent Canvas kullanıcı arayüzünde, agent'a GitHub ve Slack için araçlar
sağlayan MCP sunucularını eklemek üzere **Customize**'ı (veya
**Settings > MCP**'yi) açın. Token değerleri yalnızca yerel Agent Server'ınıza
gönderilir ve şifrelenmiş ayarlar olarak kalıcı hale getirilir.

### GitHub MCP sunucusu

Aşağıdaki ayarlarla yeni bir MCP sunucusu ekleyin:

| Alan | Değer |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = GitHub token'ınız |

Özetlemek istediğiniz depoya okuma erişimi olan bir GitHub token'ı kullanın.

### Slack MCP sunucusu

Aşağıdaki ayarlarla ikinci bir MCP sunucusu ekleyin:

| Alan | Değer |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = özet kanal kimliğiniz |

Agent'ın her Slack kanalında gezinmesi gerekmemesi için `SLACK_CHANNEL_IDS`'i
özet kanal kimliğine (`SLACK_DIGEST_CHANNEL` ile aynı değere) ayarlayın.

Her iki sunucuyu ekledikten sonra, bağlandığını ve araçları duyurduğunu
doğrulamak için her birinde **Test** düğmesini kullanın. GitHub sunucusu
GitHub araçlarını listelemeli, Slack sunucusu ise Slack araçlarını
listelemelidir.

![GitHub ve Slack sunucuları yüklenmiş Agent Canvas MCP sayfası](assets/04-mcp-servers-installed.png)

## 6. Özet Otomasyonunu Oluşturma

Agent Canvas kullanıcı arayüzünde, **Automations** sayfasını açın ve yeni
bir otomasyon oluşturun:

1. **Create automation**'ı seçin ve **Prompt preset** türünü belirleyin.
2. **Name**'i `GitHub Development Digest to Slack` olarak ayarlayın.
3. **Prompt**'u, depo ve kanal yer tutucularını kendi değerlerinizle
   değiştirerek aşağıdaki metin olarak ayarlayın:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. **Trigger**'ı `0 9 * * 1-5` zamanlamasıyla (hafta içi günlerde saat 09:00)
   **Cron** olarak ayarlayın ve **Timezone**'u kendi saat diliminize, örneğin
   `America/New_York` olarak ayarlayın.
5. **Timeout**'u `900` saniye olarak ayarlayın.
6. Otomasyonu kaydedin.

Otomasyon ayrıntı sayfası, cron tetikleyicisi ve oluşturulan prompt-preset
giriş noktasıyla birlikte yeni otomasyonu gösterir.

![Oluşturma sonrası Agent Canvas otomasyon ayrıntı sayfası](assets/05-automation-created.png)
## 7. Otomasyonu Test Edin

Agent Canvas UI'daki otomasyon detay sayfasından:

1. Otomasyonu bir kez hemen çalıştırmak için **Run now** (veya **Dispatch**) düğesine tıklayın.
2. Aynı sayfadaki çalışma listesini izleyin. En son çalışma `COMPLETED` durumuna geçmelidir.
3. Hedef Slack kanalınızı açın. Oluşturulan özeti içermelidir.

Cron zamanlamasının tetiklenmesini beklemenize gerek yok—**Run now**, zamanlamaya güvenmeden önce istemi, MCP bağlantılarını ve Slack gönderiminin tümünün çalıştığını doğrulayabilmeniz için talep üzerine bir çalışma tetikler.

![Agent Canvas otomasyon çalıştırması başarıyla tamamlandı](assets/06-automation-run-completed.png)

![Oluşturulan OpenHands özetini gösteren Slack kanalı](assets/07-slackbot-message.png)

## Sorun Giderme

- **Lemonade çalışmıyor:** 1. adımdaki `lemonade run "${LEMONADE_MODEL}"` komutuyla yeniden başlatın, ardından sağlık kontrolünü tekrar çalıştırın.
- **`npm install -g` izin hatasıyla başarısız oluyor:** Linux veya WSL'de, kullanıcıya ait genel bir npm dizini yapılandırın, bunu kabuk başlangıç dosyanıza ekleyin, ardından Agent Canvas'ı tekrar kurun:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  `zsh` kullanıyorsanız aynı `export PATH=...` satırını `~/.bashrc` yerine `~/.zshrc` dosyasına ekleyin.
- **Agent Canvas, `custom_tokenizer` ayarlandıktan sonra LLM ayarlarını reddediyor:** Agent Server Python ortamına `transformers` kurun, gerekirse Agent Canvas'ı yeniden başlatın ve LLM ayarlarını kaydetmeyi tekrar deneyin. `custom_tokenizer` ayarlandığında OpenHands, tokenizer sohbet şablonunu yüklemek için Transformers'a ihtiyaç duyar.
- **Agent Canvas, Lemonade'e ulaşamıyor:** `curl -fsS "${LEMONADE_BASE_URL}/health"` komutunu doğrulayın ve ilk kullanım LLM formuna veya **Settings > LLM** kısmına girilen temel URL'nin çalışan yerel uç nokta veya HTTPS tüneli ile eşleştiğini onaylayın.
- **LLM ayarları kaydedilmedi:** değerleri girdikten sonra **Next** düğmesine tıkladığınızdan emin olun. Değerlerin kalıcı olduğunu doğrulamak için **Settings > LLM** kısmını yeniden açın.
- **GitHub MCP özel depoları göremiyor:** GitHub belirtecinin hedef depoya okuma erişimine sahip olduğunu ve **Customize** içindeki MCP **Test** düğmesinin GitHub araçlarını gösterdiğini onaylayın.
- **Slack kanalları okuyabiliyor ama gönderi yapamıyor:** Slack uygulamasını hedef kanala davet edin ve botun `chat:write` iznine sahip olduğunu onaylayın.
- **Otomasyon çok fazla Slack kanalı listeliyor:** bir Slack kanal kimliği kullanın ve **Customize** kısmında Slack MCP sunucusunda `SLACK_CHANNEL_IDS` değerini ayarlayın.
- **Otomasyon çalıştırması başarısız oluyor veya bağlamı aşıyor:** Lemonade'in `ctx_size=65536` ile başlatıldığını, OpenHands LLM'de `custom_tokenizer`'ın ayarlandığını onaylayın ve GitHub sonuç kümeleri 3 ila 5 öğeyle sınırlandırılmış açık bir depo kullanın. Agent Canvas yapılandırmanız condenser ayarlarını sunuyorsa, condenser maksimum token sayısını Lemonade bağlam penceresinin altına ayarlayın.

## Sonraki Adımlar

- Haftalık, yalnızca sürüm içeren bir özet ekleyin.
- Daha hızlı PR veya push uyarıları için GitHub olay tetiklemeli bir otomasyon ekleyin.
- Aynı özeti Notion, Linear veya başka bir MCP destekli araca yönlendirin.

## Kaynaklar

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server belgeleri](https://lemonade-server.ai/docs)
- [OpenHands uzantılar deposu](https://github.com/OpenHands/extensions)
- [Model Context Protocol sunucuları](https://github.com/modelcontextprotocol/servers)
- [Slack MCP paketi](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)