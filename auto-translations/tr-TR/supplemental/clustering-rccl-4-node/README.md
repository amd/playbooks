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

# RCCL ile Dört Ryzen™ AI Halo'nun Kümelenmesi

## Genel Bakış

Ryzen™ AI Halo'nuz halihazırda büyük dil modellerini yerel olarak çalıştırabilme kapasitesine sahiptir. Kümeleme, birden fazla sistemin GPU belleğini yerel bir ağ üzerinden birleştirerek bunu bir adım öteye taşır ve size daha güçlü akıl yürütme, daha iyi kod üretimi ve daha derin çok dilli anlama yetenekleriyle çok daha büyük modellere, tamamen kendi donanımınız üzerinde erişim sağlar.

Bu kılavuz, RCCL (ROCm Communication Collectives Library) kullanarak vLLM ile dört Ryzen AI Halo sistemini nasıl kümeleyeceğinizi ve 397 milyar parametreli bir model olan Qwen3.5-397B'yi ROCm hızlandırmasıyla dört makinenin tamamında nasıl çalıştıracağınızı öğretir.

## Neler Öğreneceksiniz

- Ryzen AI Halo sistemlerinde VRAM tahsisini genişletme
- ROCm desteğiyle vLLM'i başlatma
- Dört Ryzen AI Halo sistemi arasında çok düğümlü tensör paralel çıkarım için RCCL yapılandırması
- Dört ağa bağlı Ryzen AI Halo sisteminde 397 milyar parametreli bir modeli çalıştırma

## Ön Koşullar

### Donanım

Bu kılavuz, yıldız topolojisinde bağlanmış dört Ryzen AI Halo birimi ve her birimin doğrudan anahtara kablolandığı bir Ethernet anahtarı gerektirir.

| Bileşen | Miktar | Açıklama |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Kümeyi oluşturan işlem düğümleri |
| 10Gbps Ethernet anahtarı | 1 | Çok düğümlü Ryzen AI Halo iletişimine izin veren merkezi anahtar (en az 4 port) |
| Ethernet kablosu | 4 | Her Halo birimini anahtara bağlar (Cat 7 veya üzeri önerilir) |

> **Not**: Dört Ryzen AI Halo birimini bağlamak için dört Ethernet anahtar portu gereklidir. Halo birimlerinden birinin yerine ayrı bir istemci makineden modele erişirseniz beşinci bir port gereklidir.

### Yazılım
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fiziksel Donanım Kurulumu

> **Not**: Bu adımı dört makinenin tamamında (Makine 1'den Makine 4'e kadar) tamamlayın.

Her Ryzen AI Halo birimini bir Cat 7 (veya üzeri) kablo kullanarak Ethernet anahtarına bağlayın. Bu, düğümler arasında yüksek hızlı iletişim için kullanılan 10Gbps bağlantıyı kurar.

### 1. Ağ Arabirimlerini Belirleme

Her makinede, ağ arabiriminin adını bulun ve not edin (talimatların geri kalanında `IFNAME` olarak anılacaktır). Çalıştırın:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Bu, arabirim adını doğrudan yazdırır, örneğin:

```bash
enp191s0
```

### 2. Ağ Bağlantı Hızlarını Doğrulama

Arabiriminizin hızını kontrol ederek bağlantının etkin olduğunu ve tam hızda çalıştığını onaylayın:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Not**: `<IFNAME>` yerine [1. Ağ Arabirimlerini Belirleme](#1-determine-network-interfaces) bölümündeki çıktı arabirim adını kullanın

`10000Mb/s` hızını görmelisiniz:

```bash
	Speed: 10000Mb/s
```

> **Not**: Hız `10000Mb/s` değerinden düşükse veya bağlantı kurulmuyorsa kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps olarak ayarlandığını doğrulayın. Bazı anahtarlar otomatik müzakerenin devre dışı bırakılmasını ve bağlantı hızının manuel olarak ayarlanmasını gerektirir; anahtarınızın belgelerine bakın.

## VRAM Tahsisini Genişletme

> **Not**: Bu adımı dört makinenin tamamında (Makine 1'den Makine 4'e kadar) tamamlayın.

### Büyük Modelleri Çalıştırmak İçin Bellek Yapılandırması

Linux'ta ROCm, paylaşılan bir sistem belleği havuzu kullanır ve bu havuz varsayılan olarak sistem belleğinin yarısına ayarlanır.

Bu miktar, aşağıdaki talimatlarla çekirdeğin Translation Table Manager (TTM) sayfa ayarını değiştirerek artırılabilir. AMD, BIOS'ta minimum ayrılmış VRAM'in (0,5 GB) ayarlanmasını önerir.

* pipx aracını kurun ve pipx tarafından kurulan wheel'lerin yolunu sistem arama yoluna ekleyin.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPI'den amd-debug-tools wheel'ini kurun.
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

* Değişikliklerin etkili olması için sistemi yeniden başlatın.

## vLLM Konteyner Başlatma

> **Not**: Bu adımı dört makinenin tamamında (Makine 1'den Makine 4'e kadar) tamamlayın.

Ryzen AI Halo'nuz, önceden oluşturulmuş bir konteyner görüntüsü içinde paketlenmiş vLLM ile birlikte gelir ve bunu ücretsiz ve açık kaynaklı bir konteyner aracı olan Podman kullanarak çalıştırırsınız.

### 1. Model İndirme Dizinini Oluşturma

Bu kılavuzda Qwen3.5-397B modelini sunduğunuzda, vLLM model ağırlıklarını sisteminize otomatik olarak indirir. Bu ağırlıkların konteyner içinden erişilebilir olmasını sağlamak için önce konteynerin bağlayabileceği bir models dizini oluşturun:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLM Konteynerini Başlatma

Aşağıdaki komut konteyneri başlatır ve sizi etkileşimli bir kabuğa düşürür. Az önce oluşturduğunuz models dizinini bağlar ve `IFNAME` değerinizi `NCCL_SOCKET_IFNAME` ile `GLOO_SOCKET_IFNAME`'e geçirerek RCCL'ye (vLLM'in küme genelindeki GPU'ları koordine etmek için kullandığı kütüphane) hangi arabirimi kullanacağını söyler.

Konteyneri şu şekilde başlatın:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Not**: `<IFNAME>` yerine [1. Ağ Arabirimlerini Belirleme](#1-determine-network-interfaces) bölümündeki çıktı arabirim adını kullanın

## Modeli Kümede Çalıştırma

vLLM, kümeyi düzenlemek için Ray'i ve düğümler arası GPU'dan GPU'ya iletişimi yönetmek için RCCL'yi kullanır. Bir makine baş düğüm (Makine 1) olarak hareket ederek çıkarımı koordine eder. Diğer üç makine, GPU belleklerini ve hesaplama güçlerini katkıda bulunarak çalışan düğüm (Makine 2, 3 ve 4) olarak katılır.

> **Not**: Ray, vLLM için isteğe bağlı bir bağımlılıktır ve yalnızca önceden yapılandırılmış Podman konteyneri içinden kullanılabilir.

Başlangıçta, vLLM modeli tensör paralelliği kullanarak dört düğümün tamamına böler. Yüklendikten sonra çıkarım, tek bir hızlandırıcıda çalışıyormuş gibi devam eder.

#### Ray OOM Hatalarını Önleme

Varsayılan olarak Ray, her düğümdeki ana bilgisayar belleğini izler ve bellek kullanımı %95'i aştığında en büyük işlemi sonlandırır. Ryzen™ AI Halo'nuzda GPU ve ana bilgisayar tek bir bellek havuzunu paylaşır, bu nedenle bir modelin yüklenmesi bir `ray.exceptions.OutOfMemoryError` hatasını tetikleyebilir ve çalışan işlemi sonlandırabilir.

Bunu önlemek için, kümeye başlamadan ve katılmadan önce her makinede `RAY_memory_monitor_refresh_ms=0` değerini dışa aktaracağız.
### Adım 1: Ray Head Node'u Başlatın (Makine 1)

Makine 1'de, kümeyi başlatmak için Ray head node'u başlatın:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` Bulma**: Makine 1'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.

### Adım 2: Kümeye Katılın (Makine 2, 3 ve 4)

Makine 2, 3 ve 4'ün her birinde, kümeyi oluşturmak için head node'a bağlanın:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **`<MACHINE_N_IP>` Bulma**: Her çalışan makinede, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.

### Adım 3: Modeli Sunun (Makine 1)

Makine 1'de, vLLM sunucusunu başlatın. Bu, modeli otomatik olarak indirecek ve dört node'un tamamında sunmaya başlayacaktır:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.8 \
  --dtype float16 \
  --tensor-parallel-size 4 \
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
| `--gpu-memory-utilization` | Tahsis edilecek GPU belleği oranı (0.0–1.0) |
| `--dtype` | Model ağırlıkları için veri türü |
| `--tensor-parallel-size` | Modelin parçalanacağı GPU sayısı (kümedeki toplam GPU sayısına ayarlayın) |
| `--distributed-executor-backend` | Çok node'lu yürütme için arka uç (küme dağıtımları için `ray`) |
| `--enforce-eager` | Uyumluluk için CUDA grafik derlemesini devre dışı bırakır |
| `--language-model-only` | Yardımcı model bileşenlerinin yüklenmesini atlar (örn. görsel kodlayıcı) |
| `--reasoning-parser` | Model için yapılandırılmış akıl yürütme çıktısı ayrıştırmayı etkinleştirir |

Tam parametre kullanımı için [vLLM belgelerine](https://docs.vllm.ai/en/latest/configuration/engine_args/) bakın.

## Modele Erişim

vLLM, OpenAI uyumlu bir API sunar, bu nedenle kümenize uyumlu herhangi bir istemci veya arayüz bağlayabilirsiniz. Popüler seçeneklerden biri, tarayıcı tabanlı bir sohbet arayüzü sağlayan [Open WebUI](https://github.com/open-webui/open-webui)'dir.

Open WebUI'yi vLLM uç noktanıza bağlamak için:

1. **Ayarlar** > **Yönetici Paneli** > **Bağlantılar**'ı açın
2. **OpenAI API Bağlantılarını Yönet** üzerindeki **+** işaretine tıklayın
3. **Bağlantı Türü**'nü **External** olarak ayarlayın
4. **URL**'yi `http://<MACHINE_1_IP>:7000/v1` olarak ayarlayın
5. **Auth** altında, açılır menüden **None** seçin
6. Uç noktadaki tüm modelleri otomatik olarak keşfetmek için **Model IDs** alanını boş bırakın

> **`<MACHINE_1_IP>` Bulma**: Makine 1'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın. Open WebUI'ye Makine 1'in kendisinden erişiyorsanız, `http://localhost:7000/v1` adresini kullanabilirsiniz.

![vLLM uç noktası için Open WebUI bağlantı ayarları](assets/openwebui-connection.png)

Bağlandıktan sonra, Open WebUI'deki model açılır menüsünden modeli seçin ve sohbete başlayın. Model artık dört Ryzen AI Halo node'unuzun tamamında çalışıyor:

![Open WebUI'de Qwen3.5-397B ile sohbet etme](assets/openwebui-chat.png)

## Sonraki Adımlar

- **Diğer modelleri keşfedin**: Kümenizin toplam GPU belleğine sığacak yeni modelleri [Hugging Face](https://huggingface.co/models?&sort=trending) üzerinde keşfedin
- **Dört node'un ötesine ölçeklendirin**: Modelleri daha da fazla sayıda GPU'ya bölmek için ek Ray çalışanları olarak başka Ryzen AI Halo sistemleri ekleyin. Her ek çalışan makinede [Adım 2: Kümeye Katılın](#step-2-join-the-cluster-machines-2-3-and-4) adımını izleyin ve `--tensor-parallel-size` değerini buna göre artırın
- **Diğer paralellik stratejilerini deneyin**: vLLM, karışık uzman (mixture-of-experts) modeller için [uzman paralelliği](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) ve daha yüksek verim için [veri paralelliği](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) destekler. İş yükünüz için en iyi yapılandırmayı bulmak üzere `--enable-expert-parallel` ve `--data-parallel-size` ile deneyler yapın