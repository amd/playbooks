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

# RCCL ile İki Ryzen™ AI Halo'yu Kümeleme

## Genel Bakış

Ryzen™ AI Halo'nuz zaten büyük dil modellerini yerel olarak çalıştırabilecek kapasitededir. Kümeleme, birden fazla sistemin GPU belleğini yerel bir ağ üzerinden birleştirerek bunu bir adım öteye taşır ve tamamen kendi donanımınızda daha güçlü akıl yürütme, daha iyi kod üretimi ve daha derin çok dilli anlama sunan çok daha büyük modellere erişmenizi sağlar.

Bu rehber, iki Ryzen AI Halo sistemini vLLM ile RCCL (ROCm Communication Collectives Library) kullanarak kümelemeyi ve 397B parametreli bir model olan Qwen3.5-397B'yi ROCm hızlandırmasıyla her iki makinede birden çalıştırmayı öğretir.

## Neler Öğreneceksiniz

- Ryzen AI Halo sistemlerinde VRAM tahsisini nasıl genişletebileceğinizi
- ROCm desteğiyle vLLM'i başlatmayı
- İki Ryzen AI Halo sistemi arasında çok düğümlü tensor-parallel çıkarım için RCCL yapılandırmasını
- İki ağa bağlı Ryzen AI Halo sistemi arasında 397B parametreli bir modeli çalıştırmayı

## Ön Koşullar

### Donanım

Bu rehber, yıldız topolojisinde bağlanmış, her biri doğrudan anahtara kablolanmış iki Ryzen AI Halo birimi ve bir Ethernet anahtarı gerektirir.

| Bileşen | Miktar | Açıklama |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Kümeyi oluşturan hesaplama düğümleri |
| 10Gbps Ethernet anahtarı | 1 | Çok düğümlü Ryzen AI Halo iletişimine izin veren merkezi anahtar (en az 2 port) |
| Ethernet kablosu | 2 | Her bir Halo birimini anahtara bağlar (Cat 7 veya üzeri önerilir) |

> **Not**: İki Ryzen AI Halo birimini bağlamak için iki Ethernet anahtarı portu gereklidir. Modele Halo birimlerinden biri yerine ayrı bir istemci makineden erişiyorsanız üçüncü bir port gereklidir.

### Yazılım
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fiziksel Donanım Kurulumu

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

Her bir Ryzen AI Halo birimini bir Cat 7 (veya üzeri) kablo kullanarak Ethernet anahtarına bağlayın. Bu, düğümler arasındaki yüksek hızlı iletişim için kullanılan 10Gbps bağlantıyı kurar.

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

> **Not**: `<IFNAME>` kısmını [1. Ağ Arayüzlerini Belirleme](#1-ağ-arayüzlerini-belirleme) bölümündeki çıktı arayüz adıyla değiştirin

`10000Mb/s` hızı görmelisiniz:

```bash
	Speed: 10000Mb/s
```

> **Not**: Hız `10000Mb/s`'den düşükse veya bağlantı kurulmuyorsa, kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps'ye ayarlandığını doğrulayın. Bazı anahtarlar otomatik müzakerenin devre dışı bırakılmasını ve bağlantı hızının manuel olarak ayarlanmasını gerektirir; anahtarınızın belgelerine başvurun.

## VRAM Tahsisini Genişletme

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

### Büyük Modelleri Çalıştırmak İçin Bellek Yapılandırması

Linux'ta ROCm paylaşımlı bir sistem bellek havuzu kullanır ve bu havuz varsayılan olarak sistem belleğinin yarısına ayarlanmıştır.

Bu miktar, aşağıdaki talimatlar izlenerek çekirdeğin Translation Table Manager (TTM) sayfa ayarı değiştirilerek artırılabilir. AMD, BIOS'ta minimum ayrılmış VRAM'in (0,5 GB) ayarlanmasını önerir.

* pipx aracını kurun ve pipx ile kurulmuş wheel'lerin yolunu sistem arama yoluna ekleyin.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPI'den amd-debug-tools wheel'ini kurun.
  ```bash
  pipx install amd-debug-tools
  ```

* Paylaşımlı bellek için mevcut ayarları sorgulamak üzere amd-ttm aracını çalıştırın.
  ```bash
  amd-ttm
  ```

* Paylaşımlı bellek ayarlarını **120 GB** olarak yeniden yapılandırın:
  ```bash
  amd-ttm --set 120
  ```

* Değişikliklerin etkili olması için sistemi yeniden başlatın.

## vLLM Konteyner Başlatma

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

Ryzen AI Halo'nuz, önceden derlenmiş bir konteyner imajı içinde paketlenmiş vLLM ile birlikte gelir ve bunu ücretsiz ve açık kaynaklı bir konteyner aracı olan Podman kullanarak çalıştırırsınız.

### 1. Model İndirme Dizinini Oluşturma

Bu rehberde Qwen3.5-397B modelini sunduğunuzda, vLLM model ağırlıklarını sisteminize otomatik olarak indirir. Bu ağırlıkların konteyner içinden erişilebilir olmasını sağlamak için önce konteynerin bağlayabileceği bir models dizini oluşturun:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLM Konteynerini Başlatma

Aşağıdaki komut konteyneri başlatır ve sizi etkileşimli bir kabuğa yönlendirir. Az önce oluşturduğunuz models dizinini bağlar ve `IFNAME` değerinizi `NCCL_SOCKET_IFNAME` ile `GLOO_SOCKET_IFNAME`'e geçirerek RCCL'ye (vLLM'in küme genelinde GPU'ları koordine etmek için kullandığı kütüphane) hangi arayüzü kullanacağını bildirir.

Konteyneri şu şekilde başlatın:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Not**: `<IFNAME>` kısmını [1. Ağ Arayüzlerini Belirleme](#1-ağ-arayüzlerini-belirleme) bölümündeki çıktı arayüz adıyla değiştirin

## Modeli Kümede Çalıştırma

vLLM, kümeyi düzenlemek için Ray'i ve düğümler arasında GPU-GPU iletişimini yönetmek için RCCL'yi kullanır. Bir makine, çıkarımı koordine eden **head node** (Makine 1) olarak görev yapar. Diğeri ise GPU belleği ve hesaplama gücü ile katkıda bulunan bir **worker node** (Makine 2) olarak kümeye katılır.

> **Not**: Ray, vLLM için isteğe bağlı bir bağımlılıktır ve yalnızca önceden yapılandırılmış Podman konteyneri içinden kullanılabilir.

Başlangıçta, vLLM modeli tensor paralelliği kullanarak her iki düğüm arasında parçalara ayırır. Yüklendikten sonra, çıkarım tek bir hızlandırıcı üzerinde çalışıyormuş gibi devam eder.

#### Ray OOM Hatalarını Önleme

Varsayılan olarak, Ray her düğümdeki ana bilgisayar belleğini izler ve bellek kullanımı %95'i aştığında en büyük süreci sonlandırır. Ryzen™ AI Halo'nuzda GPU ve ana bilgisayar tek bir bellek havuzunu paylaşır, bu nedenle bir modeli yüklemek `ray.exceptions.OutOfMemoryError` hatasını tetikleyebilir ve worker sürecini sonlandırabilir.

Bunu önlemek için, kümeyi başlatmadan ve kümeye katılmadan önce her makinede `RAY_memory_monitor_refresh_ms=0` değerini dışa aktaracağız.
### Adım 1: Ray Head Node'u Başlatın (Makine 1)

Makine 1 üzerinde, kümeyi başlatmak için Ray head node'unu başlatın:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` Adresini Bulma**: Makine 1 üzerinde, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.

### Adım 2: Kümeye Katılın (Makine 2)

Makine 2 üzerinde, kümeyi oluşturmak için head node'a bağlanın:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` Adresini Bulma**: Makine 2 üzerinde, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.

### Adım 3: Modeli Sunun (Makine 1)

Makine 1 üzerinde, vLLM sunucusunu başlatın. Bu işlem modeli otomatik olarak indirecek ve her iki node üzerinde sunmaya başlayacaktır:

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
| `--distributed-executor-backend` | Çok node'lu yürütme için arka uç (küme dağıtımları için `ray`) |
| `--enforce-eager` | Uyumluluk için CUDA graph derlemesini devre dışı bırakır |
| `--language-model-only` | Yardımcı model bileşenlerinin (örneğin, görüntü kodlayıcı) yüklenmesini atlar |
| `--reasoning-parser` | Model için yapılandırılmış akıl yürütme çıktısı ayrıştırmayı etkinleştirir |

Tam parametre kullanımı için [vLLM belgelerine](https://docs.vllm.ai/en/latest/configuration/engine_args/) bakın.

## Modele Erişim

vLLM, OpenAI uyumlu bir API sunar, bu nedenle uyumlu herhangi bir istemciyi veya arayüzü kümenize bağlayabilirsiniz. Popüler seçeneklerden biri, tarayıcı tabanlı bir sohbet arayüzü sağlayan [Open WebUI](https://github.com/open-webui/open-webui)'dir.

Open WebUI'yi vLLM uç noktanıza bağlamak için:

1. **Settings** > **Admin Panel** > **Connections** bölümünü açın
2. **Manage OpenAI API Connections** üzerindeki **+** işaretine tıklayın
3. **Connection Type** alanını **External** olarak ayarlayın
4. **URL** alanını `http://<MACHINE_1_IP>:7000/v1` olarak ayarlayın
5. **Auth** altında, açılır menüden **None** seçin
6. Uç noktadaki tüm modelleri otomatik olarak keşfetmek için **Model IDs** alanını boş bırakın

> **`<MACHINE_1_IP>` Adresini Bulma**: Makine 1 üzerinde, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın. Open WebUI'ye Makine 1'in kendisinden erişiyorsanız, `http://localhost:7000/v1` adresini kullanabilirsiniz.

![vLLM uç noktası için Open WebUI bağlantı ayarları](assets/openwebui-connection.png)

Bağlandıktan sonra, Open WebUI'deki model açılır menüsünden modeli seçin ve sohbete başlayın. Model artık her iki Ryzen AI Halo node'unuzda birden çalışıyor:

![Open WebUI'de Qwen3.5-397B ile sohbet etme](assets/openwebui-chat.png)

## Sonraki Adımlar

- **Diğer modelleri keşfedin**: Kümenizin birleşik GPU belleğine sığan yeni modelleri [Hugging Face](https://huggingface.co/models?&sort=trending) üzerinde keşfedin
- **Dört node'a ölçeklendirin**: Modelleri daha da fazla GPU arasında parçalamak için ek Ray worker'ları olarak iki Ryzen AI Halo sistemi daha ekleyin. Bu, her node için bir tane olmak üzere en az dört portlu bir Ethernet anahtarı gerektirir. Eklediğiniz her bir worker üzerinde [Adım 2: Kümeye Katılın](#step-2-join-the-cluster-machine-2) bölümünü izleyin ve `--tensor-parallel-size` değerini buna göre artırın
- **Diğer paralellik stratejilerini deneyin**: vLLM, mixture-of-experts modelleri için [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) ve daha yüksek verim için [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) desteği sunar. İş yükünüz için en iyi yapılandırmayı bulmak üzere `--enable-expert-parallel` ve `--data-parallel-size` parametrelerini deneyin