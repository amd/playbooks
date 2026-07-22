<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizceden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Hatalar içerebilir ve bazı adımlar, komutlar, indirmeler veya ürün kullanılabilirliği dilinize veya bölgenize göre farklılık gösterebilir. Yanlış görünen bir şey varsa, orijinal İngilizce playbook'u kaynak olarak kabul edin.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> Bu kılavuz, GitHub'ın işleyemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->

# RCCL ile İki Ryzen™ AI Halo'yu Kümeleme

## Genel Bakış

Ryzen™ AI Halo'nuz zaten büyük dil modellerini yerel olarak çalıştırabilecek kapasitededir. Kümeleme, birden fazla sistemin GPU belleğini bir yerel ağ üzerinden birleştirerek bunu bir adım öteye taşır ve size daha güçlü akıl yürütme, daha iyi kod üretimi ve daha derin çok dilli anlama sunan çok daha büyük modellere, tamamen kendi donanımınızda erişim sağlar.

Bu kılavuz, RCCL (ROCm Communication Collectives Library) kullanarak vLLM ile iki Ryzen AI Halo sistemini nasıl kümeleyeceğinizi ve ROCm hızlandırmasıyla her iki makinede 397 milyar parametreli bir model olan Qwen3.5-397B'yi nasıl çalıştıracağınızı öğretir.

## Öğrenecekleriniz

- Ryzen AI Halo sistemlerinde VRAM ayırmayı nasıl genişletirsiniz
- ROCm desteğiyle vLLM'i nasıl başlatırsınız
- İki Ryzen AI Halo sistemi arasında çok düğümlü tensör paralel çıkarım için RCCL'yi nasıl yapılandırırsınız
- İki ağa bağlı Ryzen AI Halo sisteminde 397 milyar parametreli bir modeli nasıl çalıştırırsınız

## Ön Koşullar

### Donanım

Bu kılavuz, her biri doğrudan anahtara (switch) kablolanmış yıldız topolojisinde bağlanmış iki Ryzen AI Halo birimi ve bir Ethernet anahtarı gerektirir.

| Bileşen | Miktar | Açıklama |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Kümeyi oluşturan işlem düğümleri |
| 10Gbps Ethernet anahtarı | 1 | Çok düğümlü Ryzen AI Halo iletişimine olanak sağlayan merkezi anahtar (en az 2 port) |
| Ethernet kablosu | 2 | Her bir Halo birimini anahtara bağlar (Cat 7 veya üzeri önerilir) |

> **Not**: İki Ryzen AI Halo birimini bağlamak için iki Ethernet anahtarı portu gereklidir. Modele Halo birimlerinden birinden değil de ayrı bir istemci makineden erişiyorsanız üçüncü bir port gereklidir.

### Yazılım
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fiziksel Donanım Kurulumu

> **Not**: Bu adımı hem Makine 1'de hem de Makine 2'de tamamlayın.

Her Ryzen AI Halo birimini Cat 7 (veya üzeri) bir kablo kullanarak Ethernet anahtarına bağlayın. Bu, düğümler arasında yüksek hızlı iletişim için kullanılan 10Gbps bağlantıyı kurar.

### 1. Ağ Arayüzlerini Belirleme

Her makinede, ağ arayüzünün adını bulun ve not edin (talimatların geri kalanında `IFNAME` olarak anılacaktır). Çalıştırın:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Bu, arayüz adını doğrudan yazdırır, örneğin:

```bash
enp191s0
```

### 2. Ağ Bağlantı Hızlarını Doğrulama

Arayüzünüzün hızını kontrol ederek bağlantının etkin olduğunu ve tam hızda çalıştığını doğrulayın:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Not**: `<IFNAME>` yerine [1. Ağ Arayüzlerini Belirleme](#1-determine-network-interfaces) bölümündeki çıktı arayüz adını yazın

`10000Mb/s` hızını görmelisiniz:

```bash
	Speed: 10000Mb/s
```

> **Not**: Hız `10000Mb/s`'den düşükse veya bağlantı kurulmuyorsa, kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps'ye ayarlandığını doğrulayın. Bazı anahtarlar otomatik müzakerenin devre dışı bırakılmasını ve bağlantı hızının manuel olarak ayarlanmasını gerektirir; anahtarınızın belgelerine başvurun.

## VRAM Ayırmayı Genişletme

> **Not**: Bu adımı hem Makine 1'de hem de Makine 2'de tamamlayın.

### Büyük Modelleri Çalıştırmak İçin Bellek Yapılandırması

Linux'ta ROCm, paylaşımlı bir sistem belleği havuzu kullanır ve bu havuz varsayılan olarak sistem belleğinin yarısı olarak yapılandırılır.

Bu miktar, aşağıdaki talimatlarla çekirdeğin Translation Table Manager (TTM) sayfa ayarı değiştirilerek artırılabilir. AMD, BIOS'ta minimum ayrılmış VRAM'i (0.5 GB) ayarlamanızı önerir.

* pipx yardımcı programını kurun ve pipx tarafından kurulan wheel'lerin yolunu sistem arama yoluna ekleyin.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* amd-debug-tools wheel'ini PyPI'dan kurun.
  ```bash
  pipx install amd-debug-tools
  ```

* Paylaşımlı bellek için mevcut ayarları sorgulamak üzere amd-ttm aracını çalıştırın.
  ```bash
  amd-ttm
  ```

* Paylaşımlı bellek ayarlarını **120 GB**'a yeniden yapılandırın:
  ```bash
  amd-ttm --set 120
  ```

* Değişikliklerin etkili olması için sistemi yeniden başlatın.

## vLLM Konteyner Başlatma

> **Not**: Bu adımı hem Makine 1'de hem de Makine 2'de tamamlayın.

Ryzen AI Halo'nuz, önceden oluşturulmuş bir konteyner görüntüsü içine paketlenmiş vLLM ile birlikte gelir ve bunu ücretsiz ve açık kaynaklı bir konteyner aracı olan Podman kullanarak çalıştırırsınız.

### 1. Model İndirme Dizinini Oluşturma

Bu kılavuzda Qwen3.5-397B modelini sunarken, vLLM model ağırlıklarını sisteminize otomatik olarak indirecektir. Bu ağırlıkların konteyner içinden erişilebilir olduğundan emin olmak için önce konteynerin bağlayabileceği bir models dizini oluşturun:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLM Konteynerini Başlatma

Aşağıdaki komut konteyneri başlatır ve sizi etkileşimli bir kabuğa yönlendirir. Az önce oluşturduğunuz models dizinini bağlar ve `IFNAME`'inizi `NCCL_SOCKET_IFNAME` ile `GLOO_SOCKET_IFNAME`'e ileterek RCCL'ye (vLLM'in küme genelinde GPU'ları koordine etmek için kullandığı kütüphane) hangi arayüzü kullanacağını bildirir.

Konteyneri şu şekilde başlatın:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Not**: `<IFNAME>` yerine [1. Ağ Arayüzlerini Belirleme](#1-determine-network-interfaces) bölümündeki çıktı arayüz adını yazın

## Modeli Kümede Çalıştırma

vLLM, kümeyi düzenlemek için Ray'i ve düğümler arasında GPU'dan GPU'ya iletişimi yönetmek için RCCL'yi kullanır. Bir makine **baş düğüm** (Makine 1) olarak görev yapar ve çıkarımı koordine eder. Diğeri ise bir **işçi düğüm** (Makine 2) olarak katılır ve GPU belleği ile işlem gücünü katkıda bulunur.

> **Not**: Ray, vLLM için isteğe bağlı bir bağımlılıktır ve yalnızca önceden yapılandırılmış Podman konteyneri içinden kullanılabilir.

Başlatma sırasında, vLLM modeli tensör paralelliği kullanarak her iki düğüm arasında parçalara ayırır. Yüklendikten sonra, çıkarım tek bir hızlandırıcı üzerinde çalışıyormuş gibi ilerler.

### Adım 1: Ray Baş Düğümünü Başlatma (Makine 1)

Makine 1'de, kümeyi başlatmak için Ray baş düğümünü başlatın:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` Bulma**: Makine 1'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.
### Adım 2: Kümeye Katılın (Makine 2)

Makine 2'de, kümeyi oluşturmak için ana düğüme bağlanın:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` Adresini Bulma**: Makine 2'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.

### Adım 3: Modeli Sunun (Makine 1)

Makine 1'de, vLLM sunucusunu başlatın. Bu işlem, modeli otomatik olarak indirecek ve her iki düğümde de sunmaya başlayacaktır:

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
| `--host` | Sunucunun bağlanacağı IP adresi (tüm arayüzler için `0.0.0.0`) |
| `--max-model-len` | Token cinsinden maksimum bağlam uzunluğu |
| `--gpu-memory-utilization` | Ayrılacak GPU belleği oranı (0.0–1.0) |
| `--dtype` | Model ağırlıkları için veri türü |
| `--tensor-parallel-size` | Modelin parçalanacağı GPU sayısı (kümedeki toplam GPU sayısına ayarlayın) |
| `--distributed-executor-backend` | Çoklu düğüm yürütmesi için arka uç (küme dağıtımları için `ray`) |
| `--enforce-eager` | Uyumluluk için CUDA graph derlemesini devre dışı bırakır |
| `--language-model-only` | Yardımcı model bileşenlerinin yüklenmesini atlar (örneğin, görüntü kodlayıcı) |
| `--reasoning-parser` | Model için yapılandırılmış akıl yürütme çıktısı ayrıştırmasını etkinleştirir |

Tam parametre kullanımı için [vLLM belgelerine](https://docs.vllm.ai/en/latest/configuration/engine_args/) bakın.

## Modele Erişim

vLLM, OpenAI uyumlu bir API sunar; bu sayede kümenize uyumlu herhangi bir istemci veya arayüz bağlayabilirsiniz. Popüler seçeneklerden biri, tarayıcı tabanlı bir sohbet arayüzü sağlayan [Open WebUI](https://github.com/open-webui/open-webui)'dir.

Open WebUI'yi vLLM uç noktanıza bağlamak için:

1. **Ayarlar** > **Yönetici Paneli** > **Bağlantılar** menüsünü açın
2. **OpenAI API Bağlantılarını Yönet** üzerindeki **+** işaretine tıklayın
3. **Bağlantı Türünü** **External** olarak ayarlayın
4. **URL**'yi `http://<MACHINE_1_IP>:7000/v1` olarak ayarlayın
5. **Auth** altında, açılır menüden **None** seçeneğini seçin
6. Uç noktadan tüm modelleri otomatik olarak keşfetmek için **Model IDs** alanını boş bırakın

> **`<MACHINE_1_IP>` Adresini Bulma**: Makine 1'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın. Open WebUI'ye Makine 1'in kendisinden erişiyorsanız, `http://localhost:7000/v1` adresini kullanabilirsiniz.

![vLLM uç noktası için Open WebUI bağlantı ayarları](assets/openwebui-connection.png)

Bağlandıktan sonra, Open WebUI'deki model açılır menüsünden modeli seçin ve sohbete başlayın. Model artık her iki Ryzen AI Halo düğümünüzde birden çalışıyor:

![Open WebUI'de Qwen3.5-397B ile sohbet etme](assets/openwebui-chat.png)

## Sonraki Adımlar

- **Diğer modelleri keşfedin**: Kümenizin toplam GPU belleğine sığan yeni modelleri [Hugging Face](https://huggingface.co/models?&sort=trending) üzerinde keşfedin
- **Dört düğüme ölçeklendirin**: Modelleri daha fazla GPU'ya bölmek için ek Ray çalışanları olarak iki Ryzen AI Halo sistemi daha ekleyin. Bunun için her düğüm için en az dört portu olan bir Ethernet anahtarı gerekir. Her ek çalışan üzerinde [Adım 2: Kümeye Katılın](#step-2-join-the-cluster-machine-2) adımlarını izleyin ve `--tensor-parallel-size` değerini buna göre artırın
- **Diğer paralellik stratejilerini deneyin**: vLLM, karma uzman modelleri için [uzman paralelliğini](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) ve daha yüksek verim için [veri paralelliğini](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) destekler. İş yükünüz için en iyi yapılandırmayı bulmak amacıyla `--enable-expert-parallel` ve `--data-parallel-size` ile denemeler yapın