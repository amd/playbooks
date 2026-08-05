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

# RPC ile İki Ryzen™ AI Halo'yu Kümeleme

## Genel Bakış

Ryzen™ AI Halo sisteminiz, büyük dil modellerini yerel olarak çalıştırma konusunda zaten yeterli kapasiteye sahiptir. Kümeleme, yerel ağ üzerinden birden fazla sistemin GPU belleğini bir araya getirerek bunu bir adım öteye taşır ve size çok daha büyük modellere erişim sağlar; bunlar daha güçlü akıl yürütme, daha iyi kod üretimi ve daha derin çok dilli anlama sunar; hepsi tamamen kendi donanımınız üzerinde gerçekleşir.

Bu kılavuz, llama.cpp'nin RPC motorunu kullanarak iki Ryzen AI Halo sistemini nasıl kümeleyeceğinizi ve AMD ROCm™ hızlandırması ile her iki makinede 358 milyar parametreli bir model olan GLM 4.7'yi nasıl çalıştıracağınızı öğretir.

## Neler Öğreneceksiniz

- Ryzen AI Halo sistemlerinde VRAM ayırma miktarını nasıl artırabileceğinizi
- ROCm ve RPC desteğiyle llama.cpp'nin nasıl kurulacağını
- Bir RPC çalışanının (worker) nasıl yapılandırılacağını ve iki düğüm arasında dağıtık çıkarımın nasıl başlatılacağını
- İki ağa bağlı Ryzen AI Halo sistemi üzerinde 358 milyar parametreli bir modeli nasıl çalıştırabileceğinizi

## Bellek Yapılandırmasının Ayarlanması

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

<!-- @os:windows -->
Windows'ta, daha fazla bellek gerektiren büyük modelleri çalıştırmak için AMD Değişken Grafik Belleği (iGPU VRAM) ayırma özelliğini kullanmamız gerekir.

Bunu yapmak için AMD Software: Adrenalin Edition kontrol panelini açın ve şu yola gidin: `Performance > Tuning > AMD Variable Graphics Memory`. Değeri **96 GB** olarak ayarlayın. Değişikliklerin etkili olması için lütfen sistemi yeniden başlatın.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linux'ta ROCm, paylaşılan bir sistem belleği havuzu kullanır ve bu havuz varsayılan olarak sistem belleğinin yarısı olacak şekilde yapılandırılmıştır.

Bu miktar, çekirdeğin Translation Table Manager (TTM) sayfa ayarı değiştirilerek aşağıdaki talimatlarla artırılabilir. AMD, BIOS'ta ayrılmış minimum VRAM'in ayarlanmasını önerir (0,5 GB).

* pipx aracını kurun ve pipx tarafından kurulan wheel'lerin yolunu sistem arama yoluna ekleyin.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* amd-debug-tools wheel'ini PyPI'den kurun.
  ```bash
  pipx install amd-debug-tools
  ```

* amd-ttm aracını çalıştırarak paylaşılan bellek için mevcut ayarları sorgulayın.
  ```bash
  amd-ttm
  ```

* Paylaşılan bellek ayarlarını **120 GB** olarak yeniden yapılandırın:
  ```bash
  amd-ttm --set 120
  ```

* Değişikliklerin etkili olması için sistemi yeniden başlatın.


<!-- @os:end -->
<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Edin

<!-- @require:software-update -->
<!-- @device:end -->
## Ön Koşullar

### Donanım

Bu kılavuz, yıldız topolojisinde bağlanmış, her biri doğrudan anahtara kablolanmış iki Ryzen AI Halo birimi ve bir Ethernet anahtarı gerektirir.

| Bileşen | Miktar | Açıklama |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Kümeyi oluşturan işlem düğümleri |
| 10Gbps Ethernet anahtarı | 1 | Çok düğümlü Ryzen AI Halo iletişimine izin veren merkezi anahtar (en az 2 port) |
| Ethernet kablosu | 2 | Her Halo birimini anahtara bağlar (Cat 7 veya üzeri önerilir) |

> **Not**: İki Ryzen AI Halo birimini bağlamak için iki Ethernet anahtarı portu gereklidir. Modele Halo birimlerinden birinden değil de ayrı bir istemci makineden erişiyorsanız, üçüncü bir port gereklidir.

### Yazılım
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Lütfen şunları kurun:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- **Desktop Development with C++** iş yükü ile birlikte [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe)
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fiziksel Donanım Kurulumu

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

Her bir Ryzen AI Halo birimini bir Cat 7 (veya üzeri) kablo kullanarak Ethernet anahtarına bağlayın. Bu, düğümler arasındaki yüksek hızlı iletişim için kullanılan 10Gbps bağlantıyı kurar.
<!-- @os:linux -->
### 1. Ağ Arayüzlerini Belirleme

Her makinede, ağ arayüzünün adını bulun ve not edin (aşağıda `IFNAME` olarak adlandırılacaktır). Çalıştırın:

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

> **Not**: `<IFNAME>` yerine [1. Ağ Arayüzlerini Belirleme](#1-determine-network-interfaces) bölümündeki çıktı arayüz adını kullanın

`10000Mb/s` hızını görmeniz gerekir:

```bash
	Speed: 10000Mb/s
```

> **Not**: Hız `10000Mb/s`'den düşükse veya bağlantı kurulmazsa, kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps olarak ayarlandığını doğrulayın. Bazı anahtarlar otomatik müzakerenin devre dışı bırakılmasını ve bağlantı hızının manuel olarak ayarlanmasını gerektirir; anahtarınızın belgelerine başvurun.

<!-- @os:end -->

<!-- @os:windows -->
### Ağ Bağlantı Hızını Doğrulama

Her makinede, ağ arayüzlerinizin bağlantı hızını kontrol edin:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet arayüzünüz `Up` durumunda olmalı ve `10 Gbps` hızında çalışmalıdır:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Not**: Hız `10 Gbps`'den düşükse veya bağlantı kurulmazsa, kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps olarak ayarlandığını doğrulayın. Bazı anahtarlar otomatik müzakerenin devre dışı bırakılmasını ve bağlantı hızının manuel olarak ayarlanmasını gerektirir; anahtarınızın belgelerine başvurun.

<!-- @os:end -->

## llama.cpp Kurulumu

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

İki kurulum seçeneği mevcuttur:

- [Seçenek 1: Lemonade SDK (Önerilen)](#option-1-lemonade-sdk-recommended) - önceden derlenmiş ikili dosyalar, en hızlı kurulum
- [Seçenek 2: Manuel Kaynak Derlemesi](#option-2-manual-source-build) - derleme bayrakları üzerinde tam kontrol ile kaynaktan derleme

### Seçenek 1: Lemonade SDK (Önerilen)

Lemonade SDK, gfx1151 (Strix Halo / Ryzen AI Max+ 395) ve diğer güncel Radeon mimarilerini hedefleyen AMD ROCm 7 hızlandırmalı llama.cpp'nin gecelik derlemelerini sağlar.

<!-- @os:windows -->
#### Adım 1: Önceden Derlenmiş İkili Dosyaları İndirin

En son sürüm sayfasına gidin ve platformunuza ve GPU hedefinize uygun arşivi indirin:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-windows-rocm-gfx1151-x64.zip` adlı dosyayı indirin (burada `xxxx` derleme numarasıdır).

#### Adım 2: İkili Dosyaları Çıkarın

İndirilen arşivi açın:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Bu dizin artık Ryzen AI Halo sisteminiz için önceden derlenmiş, ROCm destekli `llama-cli.exe`, `llama-server.exe` ve `rpc-server.exe` derlemelerini içermektedir.

#### Adım 3: GPU Algılamayı Doğrulayın

```bash
.\llama-cli.exe --list-devices
```

Beklenen çıktı:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Adım 1: Önceden Derlenmiş İkili Dosyaları İndirin

En son sürüm sayfasına gidin ve platformunuza ve GPU hedefinize uygun arşivi indirin:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` adlı dosyayı indirin (burada `xxxx` derleme numarasıdır).

#### Adım 2: İkili Dosyaları Çıkarın ve Hazırlayın

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Bu dizin artık Ryzen AI Halo sisteminiz için önceden derlenmiş, ROCm destekli `llama-cli`, `llama-server` ve `rpc-server` derlemelerini içermektedir.

#### Adım 3: GPU Algılamayı Doğrulayın

```bash
./llama-cli --list-devices
```

Beklenen çıktı:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
llama.cpp her düğümde hazırlandıktan sonra [Modeli İndirme](#downloading-the-model) bölümüne geçin.

### Seçenek 2: Manuel Kaynak Derlemesi

<!-- @os:windows -->
#### Adım 1: llama.cpp Derlemesi

**x64 Native Tools Command Prompt**'u açın (Visual Studio Build Tools ile birlikte kurulur) ve depoyu klonlayın:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

HIP'i yolunuza ekleyin ve ROCm ile RPC desteğiyle derleyin:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Derleme Bayrağı | Amaç |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm/HIP yazılım yığınını etkinleştirir |
| `-DGGML_RPC=ON` | Dağıtık çıkarım için RPC'yi etkinleştirir |
| `-DGPU_TARGETS=gfx1151` | Ryzen AI Halo GPU'yu (Radeon 8060s) hedefler |
| `-G Ninja` | Ninja derleme sistemini kullanır |

#### Adım 2: GPU Algılamayı Doğrulayın

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Beklenen çıktı:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Adım 3: HIP'i Kullanıcı Yolunuza Ekleyin

Yukarıdaki derleme adımı `%HIP_PATH%\bin` değerini yalnızca geçerli oturum için ayarladı. HIP kitaplıklarını herhangi bir terminalde (yalnızca x64 Native Tools Command Prompt'ta değil) kullanılabilir hale getirmek için, bunu kalıcı olarak kullanıcı `PATH` değerinize ekleyin:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

llama.cpp her düğümde hazırlandıktan sonra [Modeli İndirme](#downloading-the-model) bölümüne geçin.
<!-- @os:end -->

<!-- @os:linux -->
#### Adım 1: llama.cpp Derlemesi

Depoyu klonlayın:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

ROCm ve RPC desteğiyle derleyin:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Derleme Bayrağı | Amaç |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm yazılım yığınını etkinleştirir |
| `-DGGML_RPC=ON` | Dağıtık çıkarım için RPC'yi etkinleştirir |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | AMD GPU'larda gelişmiş Flash Attention için rocWMMA'yı etkinleştirir |
| `-DAMDGPU_TARGETS="gfx1151"` | Ryzen AI Halo GPU'yu (Radeon 8060s) hedefler |

Daha fazla derleme seçeneği için [llama.cpp derleme belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) bakın.

#### Adım 2: GPU Algılamayı Doğrulayın

```bash
cd rocm/bin
./llama-cli --list-devices
```

Beklenen çıktı:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

llama.cpp her düğümde hazırlandıktan sonra [Modeli İndirme](#downloading-the-model) bölümüne geçin.
<!-- @os:end -->

## Modeli İndirme

Bu kılavuz, [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL)'dan `Q4_K_XL` niceleme formatındaki 358B parametreli bir model olan [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)'yi kullanır. Bu niceleme seviyesinde model yaklaşık 205GB depolama alanı gerektirir ve iki Ryzen AI Halo düğümünün birleşik GPU belleğine sığar.

GGUF dosyalarını Hugging Face CLI kullanarak indirin:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **Not**: Model indirme işlemi Makine 1'de (denetleyici) tamamlanmalıdır. RPC işçi düğümlerinin model dosyalarının yerel bir kopyasına ihtiyacı yoktur.

## Modeli Küme Üzerinde Başlatma

llama.cpp RPC (Uzak Yordam Çağrısı) motoru, tek bir llama.cpp örneğinin model katmanlarını ağ üzerinden uzak işçilere aktarmasına olanak tanır. Bir makine **denetleyici** (Makine 1) olarak görev yapar ve belirteçleştirme, zamanlama ve orkestrasyonu yürütür. Diğer makine ise GPU belleğini ve hesaplama gücünü denetleyiciye sunan hafif bir **RPC sunucusu** (Makine 2) çalıştırır.

Yükleme sırasında llama.cpp, modeli her iki düğüme dağıtır. Yükleme tamamlandığında, çıkarım tek bir hızlandırıcı üzerinde çalışıyormuş gibi ilerler. RPC, tensör aktarımlarını ve senkronizasyonu perde arkasında yönetir.

### Adım 1: RPC Sunucusunu Başlatın (Makine 2)

Makine 2'de, GPU kaynaklarını denetleyiciye sunmak için RPC sunucusunu başlatın:
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Bayrak | Amaç |
|------|---------|
| `-p` | RPC sunucusunun yayın yapacağı bağlantı noktası |
| `-c` | Model yükleme sırasında tekrarlanan ağ aktarımlarını önleyerek büyük tensörler için yerel bir önbelleği etkinleştirir |
| `--host` | RPC sunucusunun bağlanacağı IP adresi (tüm arayüzler için `0.0.0.0`) |

Daha fazla seçenek için [llama.cpp RPC belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md) bakın.

### Adım 2: Modeli Başlatın (Makine 1)

Makine 2'de RPC sunucusu çalışırken, `llama-cli` veya `llama-server` kullanarak Makine 1'den çıkarımı başlatın.

#### llama-cli

`llama-cli`, modelle doğrudan etkileşim kurmak için terminal tabanlı bir arayüz sağlar. Kıyaslama, hata ayıklama ve düşük seviyeli deneyler için idealdir.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` değerini bulma**: Makine 2'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.
<!-- @os:end -->

<!-- @os:windows -->
> **Not**: Bu komutu Terminal'de (Powershell) çalıştırın.

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` değerini bulma**: Makine 2'de, yerel IP adresini bulmak için Terminal'de (Powershell) `ipconfig | findstr /C:"IPv4"` komutunu çalıştırın.

<!-- @os:end -->

Çalışmaya başladığında, `llama-cli` model yükleme ilerlemesini gösterir ve modelle doğrudan sohbet edebileceğiniz etkileşimli bir istem ekranına girer:

![İki düğüm üzerinde GLM 4.7 çalıştıran llama-cli](assets/llama-cli-example.png)
#### llama-server

`llama-server`, kalıcı bir sunucu süreci üzerinden aynı çıkarım motorunu, entegre bir web arayüzü ve OpenAI uyumlu bir HTTP API ile sunar. Bu, daha uzun süreli dağıtımlar, çok kullanıcılı erişim ve harici araçlarla entegrasyon için tercih edilen arayüzdür.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` bulma**: Makine 2 üzerinde, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.
<!-- @os:end -->

<!-- @os:windows -->
> **Not**: Bu komutu Terminal'de (Powershell) çalıştırın.

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` bulma**: Makine 2 üzerinde, yerel IP adresini bulmak için Terminal'de (Powershell) `ipconfig | findstr /C:"IPv4"` komutunu çalıştırın.
<!-- @os:end -->

Başlatıldıktan sonra, yerleşik web arayüzüne erişmek için tarayıcınızda `http://<HOST_IP>:8081` adresini açın. Bu, modelle etkileşim kurmak için tarayıcı tabanlı bir sohbet arayüzü sağlar:

![İki düğüm üzerinde GLM 4.7 çalıştıran llama-server web arayüzü](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` bulma**: Makine 1 üzerinde, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` bulma**: Makine 1 üzerinde, yerel IP adresini bulmak için Terminal'de (Powershell) `ipconfig | findstr /C:"IPv4"` komutunu çalıştırın.
<!-- @os:end -->

#### Parametre Referansı

| Bayrak | Amaç |
|------|---------|
| `-m` | GGUF model dosyasının yolu (ilk parçayı kullanın, `00001-of-00005`) |
| `-c` | Token cinsinden bağlam boyutu. Daha büyük değerler daha fazla bellek kullanır |
| `-fa on` | AMD GPU'larda daha iyi performans için rocWMMA Flash Attention'ı etkinleştirir |
| `-ngl 999` | Tüm model katmanlarını GPU'ya aktarır |
| `--no-mmap` | Bellek eşlemeyi devre dışı bırakır, model boyutu sistem RAM'ini aştığında ancak VRAM'e sığdığında yükleme sürelerini azaltır |
| `--host` | `llama-server`'ın bağlanacağı IP (yalnızca `llama-server`) |
| `--port` | HTTP API'sinin sunulacağı port (yalnızca `llama-server`) |
| `--rpc` | Virgülle ayrılmış RPC çalışan uç nokta listesi (`IP:port`) |

Tam parametre kullanımı için [llama-cli belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) ve [llama-server belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) bakın.

## Sonraki Adımlar

- **Üçüncü taraf uygulamaları bağlayın**: `llama-server`, OpenAI uyumlu bir API sunar. Kümenize bağlanmak için OpenAI uyumlu herhangi bir uygulamayı (Open WebUI gibi) herhangi bir yer tutucu API anahtarıyla (ör. `none`) `http://<HOST_IP>:8081` adresine yönlendirin
- **Diğer modelleri keşfedin**: Kümenizin toplam GPU belleğine sığan modelleri bulmak için [Hugging Face](https://huggingface.co/models?search=gguf) üzerinde nicelendirilmiş GGUF'lara göz atın
- **Dört düğüme ölçeklendirin**: 1 trilyon parametre ölçeğindeki modellere erişmek için ek RPC çalışanları olarak iki Ryzen AI Halo sistemi daha ekleyin. Ek uç noktaları virgülle ayrılmış bir liste olarak `--rpc` parametresine geçirin (ör. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)