<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Bu playbook, GitHub'ın render edemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->

# RCCL ile İki Ryzen™ AI Halo'yu Kümeleme

## Genel Bakış

Ryzen™ AI Halo'nuz, büyük dil modellerini yerel olarak çalıştırma konusunda zaten yetkindir. Kümeleme, birden fazla sistemin GPU belleğini yerel bir ağ üzerinden birleştirerek bunu daha da ileri taşır; daha güçlü akıl yürütme, daha iyi kod üretimi ve daha derin çok dilli anlayışa sahip çok daha büyük modellere erişim sağlar; üstelik tüm bunlar tamamen kendi donanımınızda gerçekleşir.

Bu playbook, RCCL (ROCm Communication Collectives Library) kullanarak iki Ryzen AI Halo sistemini vLLM ile nasıl kümeleyeceğinizi ve ROCm hızlandırmasıyla her iki makineye yayılmış 397B parametreli bir model olan Qwen3.5-397B'yi nasıl çalıştıracağınızı öğretir.

## Neler Öğreneceksiniz

- Ryzen AI Halo sistemlerinde VRAM tahsisini nasıl genişleteceğiniz
- ROCm desteğiyle vLLM'i başlatma
- İki Ryzen AI Halo sistemi arasında çok düğümlü tensör paralel çıkarım için RCCL yapılandırması
- Ağa bağlı iki Ryzen AI Halo sistemi arasında 397B parametreli bir modeli çalıştırma

## Ön Koşullar

### Donanım

Bu playbook, iki Ryzen AI Halo birimi ve her birimin doğrudan anahtara bağlandığı yıldız topolojisinde bağlı bir Ethernet anahtarı gerektirir.

| Bileşen | Miktar | Açıklama |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Kümeyi oluşturan hesaplama düğümleri |
| 10Gbps Ethernet anahtarı | 1 | Çok düğümlü Ryzen AI Halo iletişimine olanak tanıyan merkezi anahtar (en az 2 port) |
| Ethernet kablosu | 2 | Her Halo birimini anahtara bağlar (Cat 7 veya üzeri önerilir) |

> **Not**: İki Ryzen AI Halo birimini bağlamak için iki Ethernet anahtarı portu gereklidir. Modele Halo birimlerinden biri yerine ayrı bir istemci makineden erişiyorsanız üçüncü bir port gereklidir.

### Yazılım
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fiziksel Donanım Kurulumu

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

Her Ryzen AI Halo birimini Cat 7 (veya üzeri) kablo kullanarak Ethernet anahtarına bağlayın. Bu, düğümler arasındaki yüksek hızlı iletişim için kullanılan 10Gbps bağlantısını kurar.

### 1. Ağ Arayüzlerini Belirleme

Her makinede, ağ arayüzünün adını bulun ve not edin (talimatların geri kalanında `IFNAME` olarak anılacaktır). Şunu çalıştırın:

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

> **Not**: `<IFNAME>` kısmını [1. Ağ Arayüzlerini Belirleme](#1-determine-network-interfaces) bölümündeki çıktı arayüz adıyla değiştirin.

`10000Mb/s` hızını görmelisiniz:

```bash
	Speed: 10000Mb/s
```

> **Not**: Hız `10000Mb/s`'den düşükse veya bağlantı kurulmazsa kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps olarak ayarlandığını doğrulayın. Bazı anahtarlar otomatik müzakereyi devre dışı bırakmayı ve bağlantı hızını manuel olarak ayarlamayı gerektirebilir; anahtarınızın belgelerine başvurun.

## VRAM Tahsisini Genişletme

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

### Büyük Modelleri Çalıştırmak için Bellek Yapılandırması

Linux'ta ROCm, paylaşılan bir sistem bellek havuzundan yararlanır ve bu havuz varsayılan olarak sistem belleğinin yarısına yapılandırılmıştır.

Bu miktar, aşağıdaki talimatlarla çekirdeğin Translation Table Manager (TTM) sayfa ayarı değiştirilerek artırılabilir. AMD, BIOS'ta minimum ayrılmış VRAM'i (0,5 GB) ayarlamayı önerir.

* pipx yardımcı programını yükleyin ve pipx tarafından yüklenen wheel'ler için yolu sistem arama yoluna ekleyin.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* amd-debug-tools wheel'ini PyPI'dan yükleyin.
  ```bash
  pipx install amd-debug-tools
  ```

* Paylaşılan bellek için mevcut ayarları sorgulamak üzere amd-ttm aracını çalıştırın.
  ```bash
  amd-ttm
  ```

* Paylaşılan bellek ayarlarını **120 GB** olarak yeniden yapılandırın:
  ```bash
  amd-ttm --set 120
  ```

* Değişikliklerin geçerli olması için sistemi yeniden başlatın.

## vLLM Konteyner Başlatma

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

Ryzen AI Halo'nuz, önceden oluşturulmuş bir konteyner görüntüsünün içinde paketlenmiş vLLM ile birlikte gelir; bunu ücretsiz ve açık kaynaklı bir konteyner aracı olan Podman kullanarak çalıştırırsınız.

### 1. Model İndirme Dizinini Oluşturma

Bu playbook'ta Qwen3.5-397B modelini sunduğunuzda, vLLM model ağırlıklarını otomatik olarak sisteminize indirecektir. Bu ağırlıklara konteynerin içinden erişilebilir olduğundan emin olmak için önce konteynerin bağlayabileceği bir modeller dizini oluşturun:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLM Konteynerini Başlatma

Aşağıdaki komut, konteyneri başlatır ve sizi etkileşimli bir kabuk oturumuna bırakır. Az önce oluşturduğunuz modeller dizinini bağlar ve `IFNAME`'inizi `NCCL_SOCKET_IFNAME` ve `GLOO_SOCKET_IFNAME`'e ileterek RCCL'ye (vLLM'in küme genelinde GPU'ları koordine etmek için kullandığı kütüphane) hangi arayüzü kullanacağını söyler.

Konteyneri şununla başlatın:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Not**: `<IFNAME>` kısmını [1. Ağ Arayüzlerini Belirleme](#1-determine-network-interfaces) bölümündeki çıktı arayüz adıyla değiştirin.

## Modeli Kümede Çalıştırma

vLLM, kümeyi düzenlemek için Ray'i ve düğümler arasında GPU-GPU iletişimini yönetmek için RCCL'yi kullanır. Bir makine **baş düğüm** (Makine 1) olarak çıkarımı koordine eder. Diğeri **işçi düğümü** (Makine 2) olarak katılır ve GPU belleği ile hesaplama gücü sağlar.

> **Not**: Ray, vLLM için isteğe bağlı bir bağımlılıktır ve yalnızca önceden yapılandırılmış Podman konteyneri içinden kullanılabilir.

Başlatma sırasında vLLM, tensör paralelliği kullanarak modeli her iki düğüme dağıtır. Yüklendikten sonra çıkarım, tek bir hızlandırıcıda çalışıyormuş gibi ilerler.

### Adım 1: Ray Baş Düğümünü Başlatma (Makine 1)

Makine 1'de, kümeyi başlatmak için Ray baş düğümünü başlatın:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>`'yi Bulma**: Makine 1'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.

### Adım 2: Kümeye Katılma (Makine 2)

Makine 2'de, kümeyi oluşturmak için baş düğüme bağlanın:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>`'yi Bulma**: Makine 2'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.

### Adım 3: Modeli Sunma (Makine 1)

Makine 1'de, vLLM sunucusunu başlatın. Bu, modeli otomatik olarak indirecek ve her iki düğümde sunmaya başlayacaktır:

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
| `--port` | HTTP API'sinin sunulacağı port |
| `--host` | Sunucunun bağlanacağı IP adresi (tüm arayüzler için `0.0.0.0`) |
| `--max-model-len` | Token cinsinden maksimum bağlam uzunluğu |
| `--gpu-memory-utilization` | Tahsis edilecek GPU belleği oranı (0,0–1,0) |
| `--dtype` | Model ağırlıkları için veri türü |
| `--tensor-parallel-size` | Modelin dağıtılacağı GPU sayısı (kümedeki toplam GPU sayısına ayarlayın) |
| `--distributed-executor-backend` | Çok düğümlü yürütme için arka uç (küme dağıtımları için `ray`) |
| `--enforce-eager` | Uyumluluk için CUDA grafik derlemesini devre dışı bırakır |
| `--language-model-only` | Yardımcı model bileşenlerinin yüklenmesini atlar (örn. görüntü kodlayıcı) |
| `--reasoning-parser` | Model için yapılandırılmış akıl yürütme çıktısı ayrıştırmayı etkinleştirir |

Tam parametre kullanımı için [vLLM belgelerine](https://docs.vllm.ai/en/latest/configuration/engine_args/) başvurun.

## Modele Erişim

vLLM, OpenAI uyumlu bir API sunar; bu nedenle herhangi bir uyumlu istemciyi veya arayüzü kümenize bağlayabilirsiniz. Popüler bir seçenek, tarayıcı tabanlı bir sohbet arayüzü sağlayan [Open WebUI](https://github.com/open-webui/open-webui)'dir.

Open WebUI'yi vLLM uç noktanıza bağlamak için:

1. **Ayarlar** > **Yönetici Paneli** > **Bağlantılar** bölümünü açın
2. **OpenAI API Bağlantılarını Yönet** üzerindeki **+** simgesine tıklayın
3. **Bağlantı Türü**'nü **Harici** olarak ayarlayın
4. **URL**'yi `http://<MACHINE_1_IP>:7000/v1` olarak ayarlayın
5. **Kimlik Doğrulama** altında açılır menüden **Yok**'u seçin
6. Uç noktadaki tüm modelleri otomatik olarak keşfetmek için **Model Kimlikleri**'ni boş bırakın

> **`<MACHINE_1_IP>`'yi Bulma**: Makine 1'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın. Open WebUI'ye Makine 1'in kendisinden erişiyorsanız `http://localhost:7000/v1` kullanabilirsiniz.

![vLLM uç noktası için Open WebUI bağlantı ayarları](assets/openwebui-connection.png)

Bağlandıktan sonra Open WebUI'deki model açılır menüsünden modeli seçin ve sohbet etmeye başlayın. Model artık her iki Ryzen AI Halo düğümünüzde çalışmaktadır:

![Open WebUI'de Qwen3.5-397B ile sohbet](assets/openwebui-chat.png)

## Sonraki Adımlar

- **Diğer modelleri keşfedin**: Kümenizin birleşik GPU belleğine sığan yeni modelleri [Hugging Face](https://huggingface.co/models?&sort=trending) üzerinde keşfedin
- **Dört düğüme ölçeklendirin**: Modelleri daha da fazla GPU'ya dağıtmak için ek Ray işçileri olarak iki Ryzen AI Halo sistemi daha ekleyin. Bu, her düğüm için bir tane olmak üzere en az dört portlu bir Ethernet anahtarı gerektirir. Her ek işçide [Adım 2: Kümeye Katılma](#step-2-join-the-cluster-machine-2) bölümünü izleyin ve `--tensor-parallel-size` değerini buna göre artırın
- **Diğer paralellik stratejilerini deneyin**: vLLM, karışık uzman modelleri için [uzman paralel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) ve daha yüksek verim için [veri paralel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) seçeneklerini destekler. İş yükünüz için en iyi yapılandırmayı bulmak üzere `--enable-expert-parallel` ve `--data-parallel-size` ile denemeler yapın