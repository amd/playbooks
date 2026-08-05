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

# RCCL ile İki Ryzen™ AI Halo'nun Kümelenmesi

## Genel Bakış

Ryzen™ AI Halo sisteminiz zaten büyük dil modellerini yerel olarak çalıştırabilme yeteneğine sahiptir. Kümeleme, birden fazla sistemin GPU belleğini yerel bir ağ üzerinden birleştirerek bunu bir adım öteye taşır ve size daha güçlü akıl yürütme, daha iyi kod üretimi ve daha derin çok dilli anlama yeteneğine sahip çok daha büyük modellere, tamamen kendi donanımınız üzerinde erişim sağlar.

Bu kılavuz, iki Ryzen AI Halo sistemini RCCL (ROCm Communication Collectives Library) kullanarak vLLM ile kümelemeyi ve 397 milyar parametreli bir model olan Qwen3.5-397B'yi ROCm hızlandırmasıyla her iki makinede birden çalıştırmayı öğretir.

## Öğrenecekleriniz

- Ryzen AI Halo sistemlerinde VRAM ayırmayı genişletme
- ROCm desteğiyle vLLM'i başlatma
- İki Ryzen AI Halo sistemi arasında çoklu düğüm tensör-paralel çıkarım için RCCL yapılandırma
- 397 milyar parametreli bir modeli ağa bağlı iki Ryzen AI Halo sisteminde çalıştırma

## Ön Koşullar

### Donanım

Bu kılavuz, her biri doğrudan anahtara (switch) kablolanmış, yıldız topolojisinde bağlanmış iki Ryzen AI Halo ünitesi ve bir Ethernet anahtarı gerektirir.

| Bileşen | Miktar | Açıklama |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Kümeyi oluşturan hesaplama düğümleri |
| 10Gbps Ethernet anahtarı | 1 | Çoklu düğüm Ryzen AI Halo iletişimine olanak tanıyan merkezi anahtar (en az 2 port) |
| Ethernet kablosu | 2 | Her bir Halo ünitesini anahtara bağlar (Cat 7 veya üzeri önerilir) |

> **Not**: İki Ryzen AI Halo ünitesini bağlamak için iki Ethernet anahtarı portu gereklidir. Modele Halo ünitelerinden birinin üzerinden değil de ayrı bir istemci makineden erişiyorsanız üçüncü bir port gereklidir.

### Yazılım
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fiziksel Donanım Kurulumu

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

Her bir Ryzen AI Halo ünitesini bir Cat 7 (veya üzeri) kablo kullanarak Ethernet anahtarına bağlayın. Bu, düğümler arasında yüksek hızlı iletişim için kullanılan 10Gbps bağlantısını kurar.

### 1. Ağ Arayüzlerini Belirleme

Her bir makinede, ağ arayüzünün adını bulun ve not edin (talimatların geri kalanında `IFNAME` olarak anılacaktır). Çalıştırın:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Bu, arayüz adını doğrudan yazdırır, örneğin:

```bash
enp191s0
```

### 2. Ağ Bağlantı Hızlarını Doğrulama

Arayüzünüzün hızını kontrol ederek bağlantının etkin ve tam hızda çalıştığını doğrulayın:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Not**: `<IFNAME>` yerine [1. Ağ Arayüzlerini Belirleme](#1-a%C4%9F-ara%C3%BCzlerini-belirleme) bölümündeki çıktı arayüz adını kullanın

`10000Mb/s` hızını görmelisiniz:

```bash
	Speed: 10000Mb/s
```

> **Not**: Hız `10000Mb/s`'den düşükse veya bağlantı kurulmuyorsa, kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps olarak ayarlandığını onaylayın. Bazı anahtarlar, otomatik müzakerenin devre dışı bırakılmasını ve bağlantı hızının manuel olarak ayarlanmasını gerektirir; anahtarınızın belgelerine başvurun.

## VRAM Tahsisini Genişletme

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

### Büyük Modelleri Çalıştırmak İçin Bellek Yapılandırması

Linux'ta ROCm, paylaşılan bir sistem belleği havuzu kullanır ve bu havuz varsayılan olarak sistem belleğinin yarısı olacak şekilde yapılandırılmıştır.

Bu miktar, aşağıdaki talimatlarla kernel'in Translation Table Manager (TTM) sayfa ayarını değiştirerek artırılabilir. AMD, BIOS'ta minimum ayrılmış VRAM'in (0.5 GB) ayarlanmasını önerir.

* pipx yardımcı programını kurun ve pipx tarafından kurulan wheel'lerin yolunu sistem arama yoluna ekleyin.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPI'dan amd-debug-tools wheel'ini kurun.
  ```bash
  pipx install amd-debug-tools
  ```

* Paylaşılan bellek için mevcut ayarları sorgulamak üzere amd-ttm aracını çalıştırın.
  ```bash
  amd-ttm
  ```

* Paylaşılan bellek ayarlarını **120 GB**'a yeniden yapılandırın:
  ```bash
  amd-ttm --set 120
  ```

* Değişikliklerin etkili olması için sistemi yeniden başlatın.

## vLLM Konteyner Başlatma

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

Ryzen AI Halo sisteminiz, önceden oluşturulmuş bir konteyner imajı içinde paketlenmiş vLLM ile birlikte gelir ve bunu ücretsiz ve açık kaynaklı bir konteyner aracı olan Podman kullanarak çalıştırırsınız.

### 1. Model İndirme Dizinini Oluşturma

Bu kılavuzda Qwen3.5-397B modelini sunduğunuzda, vLLM model ağırlıklarını sisteminize otomatik olarak indirir. Bu ağırlıkların konteyner içinden erişilebilir olduğundan emin olmak için önce konteynerin bağlayabileceği bir models dizini oluşturun:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLM Konteynerini Başlatma

Aşağıdaki komut konteyneri başlatır ve sizi etkileşimli bir kabuğa (shell) bırakır. Az önce oluşturduğunuz models dizinini bağlar ve `IFNAME`'inizi `NCCL_SOCKET_IFNAME` ile `GLOO_SOCKET_IFNAME`'e ileterek RCCL'ye (vLLM'in küme genelinde GPU'ları koordine etmek için kullandığı kütüphane) hangi arayüzü kullanacağını bildirir.

Konteyneri şununla başlatın:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Not**: `<IFNAME>` yerine [1. Ağ Arayüzlerini Belirleme](#1-a%C4%9F-ara%C3%BCzlerini-belirleme) bölümündeki çıktı arayüz adını kullanın

## Modeli Küme Üzerinde Çalıştırma

vLLM, kümeyi düzenlemek için Ray'i ve düğümler arasında GPU'dan GPU'ya iletişimi yönetmek için RCCL'yi kullanır. Bir makine, çıkarımı koordine ederek **baş düğüm (head node)** (Makine 1) görevi görür. Diğeri ise GPU belleğine ve hesaplama gücüne katkıda bulunarak bir **çalışan düğüm (worker node)** (Makine 2) olarak katılır.

> **Not**: Ray, vLLM için isteğe bağlı bir bağımlılıktır ve yalnızca önceden yapılandırılmış Podman konteyneri içinden kullanılabilir.

Başlangıçta, vLLM modeli tensör paralelliği kullanarak her iki düğüme böler. Yüklendikten sonra, çıkarım tek bir hızlandırıcı üzerinde çalışıyormuş gibi devam eder.

### Adım 1: Ray Baş Düğümünü Başlatma (Makine 1)

Makine 1'de, kümeyi başlatmak için Ray baş düğümünü başlatın:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>`'yi bulma**: Makine 1'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.
### Adım 2: Kümeye Katılın (Makine 2)

Makine 2'de, kümeyi oluşturmak için baş düğüme bağlanın:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` Bulma**: Makine 2'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.

### Adım 3: Modeli Sunun (Makine 1)

Makine 1'de vLLM sunucusunu başlatın. Bu, modeli otomatik olarak indirecek ve her iki düğümde birden sunmaya başlayacaktır:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Parametre Referansı

| Bayrak | Amaç |
|------|---------|
| `--port` | HTTP API'nin sunulacağı port |
| `--host` | Sunucunun bağlanacağı IP adresi (tüm arabirimler için `0.0.0.0`) |
| `--max-model-len` | Belirteç cinsinden maksimum bağlam uzunluğu |
| `--gpu-memory-utilization` | Ayrılacak GPU belleği oranı (0.0–1.0) |
| `--dtype` | Model ağırlıkları için veri türü |
| `--tensor-parallel-size` | Modelin parçalanacağı GPU sayısı (kümedeki toplam GPU sayısına ayarlayın) |
| `--distributed-executor-backend` | Çok düğümlü yürütme için arka uç (küme dağıtımları için `ray`) |
| `--enforce-eager` | Uyumluluk için CUDA graf derlemesini devre dışı bırakır |
| `--language-model-only` | Yardımcı model bileşenlerinin yüklenmesini atlar (ör. görsel kodlayıcı) |
| `--reasoning-parser` | Model için yapılandırılmış akıl yürütme çıktısı ayrıştırmayı etkinleştirir |

Tam parametre kullanımı için [vLLM belgelerine](https://docs.vllm.ai/en/latest/configuration/engine_args/) başvurun.

## Modele Erişme

vLLM, OpenAI ile uyumlu bir API sunar, böylece kümenize uyumlu herhangi bir istemci veya arayüz bağlayabilirsiniz. Popüler seçeneklerden biri, tarayıcı tabanlı bir sohbet arayüzü sağlayan [Open WebUI](https://github.com/open-webui/open-webui)'dir.

Open WebUI'yi vLLM uç noktanıza bağlamak için:

1. **Ayarlar** > **Yönetici Paneli** > **Bağlantılar**'ı açın
2. **OpenAI API Bağlantılarını Yönet** üzerindeki **+** simgesine tıklayın
3. **Bağlantı Türü**'nü **External** olarak ayarlayın
4. **URL**'yi `http://<MACHINE_1_IP>:7000/v1` olarak ayarlayın
5. **Auth** altında, açılır menüden **None**'u seçin
6. Uç noktadaki tüm modelleri otomatik olarak keşfetmek için **Model IDs** alanını boş bırakın

> **`<MACHINE_1_IP>` Bulma**: Makine 1'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın. Open WebUI'ye Makine 1'in kendisinden erişiyorsanız, `http://localhost:7000/v1` adresini kullanabilirsiniz.

![vLLM uç noktası için Open WebUI bağlantı ayarları](assets/openwebui-connection.png)

Bağlandıktan sonra, Open WebUI'deki model açılır menüsünden modeli seçin ve sohbete başlayın. Model artık her iki Ryzen AI Halo düğümünüzde birden çalışıyor:

![Open WebUI'de Qwen3.5-397B ile sohbet etme](assets/openwebui-chat.png)

## Sonraki Adımlar

- **Diğer modelleri keşfedin**: Kümenizin birleşik GPU belleğine sığan yeni modelleri [Hugging Face](https://huggingface.co/models?&sort=trending) üzerinde keşfedin
- **Dört düğüme ölçeklendirin**: Modelleri daha fazla GPU arasında parçalamak için ek Ray çalışanları olarak iki Ryzen AI Halo sistemi daha ekleyin. Bunun için her düğüm için bir tane olmak üzere en az dört portlu bir Ethernet anahtarı gerekir. Her ek çalışan üzerinde [Adım 2: Kümeye Katılın](#step-2-join-the-cluster-machine-2) adımını izleyin ve `--tensor-parallel-size` değerini buna göre artırın
- **Diğer paralellik stratejilerini deneyin**: vLLM, karma uzman modelleri için [uzman paralel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) ve daha yüksek verim için [veri paralel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) desteği sunar. İş yükünüz için en iyi yapılandırmayı bulmak amacıyla `--enable-expert-parallel` ve `--data-parallel-size` ile deneyler yapın