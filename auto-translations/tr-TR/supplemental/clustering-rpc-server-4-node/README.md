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

# RPC ile Dört Ryzen™ AI Halo'yu Kümeleme

## Genel Bakış

Ryzen™ AI Halo'nuz zaten büyük dil modellerini yerel olarak çalıştırma yeteneğine sahiptir. Kümeleme, birden fazla sistemin GPU belleğini yerel bir ağ üzerinden birleştirerek bunu bir adım öteye taşır ve size tamamen kendi donanımınızda, daha güçlü akıl yürütme, daha iyi kod üretimi ve daha derin çok dilli anlama sunan çok daha büyük modellere erişim sağlar.

Bu kılavuz, llama.cpp'nin RPC motorunu kullanarak dört Ryzen AI Halo sistemini nasıl kümeleyeceğinizi ve büyük bir mixture-of-experts modeli olan Kimi K2.6'yı AMD ROCm™ hızlandırmasıyla dört makinenin tamamında nasıl çalıştıracağınızı öğretir.

## Neler Öğreneceksiniz

- Ryzen AI Halo sistemlerinde VRAM ayırmayı nasıl genişletirsiniz
- ROCm ve RPC desteğiyle llama.cpp'yi kurma
- RPC çalışanlarını yapılandırma ve dört düğüm genelinde dağıtık çıkarımı başlatma
- Dört ağa bağlı Ryzen AI Halo sistemi genelinde 1T parametreli bir modeli çalıştırma

## Bellek Yapılandırmasını Ayarlama

> **Not**: Bu adımı dört makinenin tamamında (Makine 1'den Makine 4'e kadar) tamamlayın.

<!-- @os:windows -->
Windows'ta, daha yüksek bellek gerektiren daha büyük modelleri çalıştırmak için AMD Değişken Grafik Belleği (iGPU VRAM) tahsisini kullanmamız gerekir.

Bu işlem, AMD Software: Adrenalin Edition kontrol panelini açıp şu yola giderek yapılabilir: `Performance > Tuning > AMD Variable Graphics Memory`. Değeri **96 GB** olarak ayarlayın. Değişikliklerin etkili olması için lütfen sistemi yeniden başlatın.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linux'ta ROCm, paylaşımlı bir sistem bellek havuzu kullanır ve bu havuz varsayılan olarak sistem belleğinin yarısına ayarlanır.

Bu miktar, aşağıdaki talimatlarla çekirdeğin Translation Table Manager (TTM) sayfa ayarı değiştirilerek artırılabilir. AMD, BIOS'ta minimum ayrılmış VRAM'in (0,5 GB) ayarlanmasını önerir.

* pipx yardımcı programını kurun ve pipx tarafından kurulan wheel'lerin yolunu sistem arama yoluna ekleyin.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPI'den amd-debug-tools wheel'ini kurun.
  ```bash
  pipx install amd-debug-tools
  ```

* Paylaşımlı bellek için geçerli ayarları sorgulamak üzere amd-ttm aracını çalıştırın.
  ```bash
  amd-ttm
  ```

* Paylaşımlı bellek ayarlarını **120 GB** olarak yeniden yapılandırın:
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

Bu kılavuz, yıldız topolojisinde bağlanmış, her biri doğrudan anahtara kablolanmış dört Ryzen AI Halo ünitesi ve bir Ethernet anahtarı gerektirir.

| Bileşen | Miktar | Açıklama |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Kümeyi oluşturan işlem düğümleri |
| 10Gbps Ethernet anahtarı | 1 | Çok düğümlü Ryzen AI Halo iletişimine izin veren merkezi anahtar (en az 4 port) |
| Ethernet kablosu | 4 | Her Halo ünitesini anahtara bağlar (Cat 7 veya üzeri önerilir) |

> **Not**: Dört Ryzen AI Halo ünitesini bağlamak için dört Ethernet anahtarı portu gereklidir. Modele Halo ünitelerinden birinden değil de ayrı bir istemci makineden erişiyorsanız beşinci bir port gereklidir.

### Yazılım
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Lütfen şunları kurun:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- **Desktop Development with C++** iş yükü ile [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe)
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fiziksel Donanım Kurulumu

> **Not**: Bu adımı dört makinenin tamamında (Makine 1'den Makine 4'e kadar) tamamlayın.

Her Ryzen AI Halo ünitesini bir Cat 7 (veya üzeri) kablo kullanarak Ethernet anahtarına bağlayın. Bu, düğümler arasındaki yüksek hızlı iletişim için kullanılan 10Gbps bağlantıyı kurar.
<!-- @os:linux -->
### 1. Ağ Arabirimlerini Belirleme

Her makinede, ağ arabiriminin adını bulun ve not edin (aşağıda `IFNAME` olarak anılacaktır). Şunu çalıştırın:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Bu, arabirim adını doğrudan yazdırır, örneğin:

```bash
enp191s0
```

### 2. Ağ Bağlantı Hızlarını Doğrulama

Arabiriminizin hızını kontrol ederek bağlantının etkin olduğunu ve tam hızda çalıştığını doğrulayın:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Not**: `<IFNAME>` yerine [1. Ağ Arabirimlerini Belirleme](#1-determine-network-interfaces) bölümündeki çıktı arabirim adını kullanın

`10000Mb/s` hızını görmelisiniz:

```bash
	Speed: 10000Mb/s
```

> **Not**: Hız `10000Mb/s`'den düşükse veya bağlantı kurulmuyorsa kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps olarak ayarlandığını doğrulayın. Bazı anahtarlar otomatik müzakerenin devre dışı bırakılmasını ve bağlantı hızının manuel olarak ayarlanmasını gerektirir; lütfen anahtarınızın belgelerine bakın.

<!-- @os:end -->

<!-- @os:windows -->
### Ağ Bağlantı Hızını Doğrulama

Her makinede, ağ arabirimlerinizin bağlantı hızını kontrol edin:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet arabiriminiz `Up` durumunda olmalı ve `10 Gbps` hızında çalışmalıdır:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Not**: Hız `10 Gbps`'den düşükse veya bağlantı kurulmuyorsa kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps olarak ayarlandığını doğrulayın. Bazı anahtarlar otomatik müzakerenin devre dışı bırakılmasını ve bağlantı hızının manuel olarak ayarlanmasını gerektirir; lütfen anahtarınızın belgelerine bakın.

<!-- @os:end -->

## llama.cpp Kurulumu

> **Not**: Bu adımı dört makinenin tamamında (Makine 1'den Makine 4'e kadar) tamamlayın.

İki kurulum seçeneği mevcuttur:

- [Seçenek 1: Lemonade SDK (Önerilen)](#option-1-lemonade-sdk-recommended) - önceden derlenmiş ikili dosyalar, en hızlı kurulum
- [Seçenek 2: Manuel Kaynak Derlemesi](#option-2-manual-source-build) - derleme bayrakları üzerinde tam kontrol ile kaynaktan derleme

### Seçenek 1: Lemonade SDK (Önerilen)

Lemonade SDK, gfx1151 (Strix Halo / Ryzen AI Max+ 395) ve diğer yeni Radeon mimarilerini hedefleyen AMD ROCm 7 hızlandırmalı llama.cpp'nin gecelik derlemelerini sağlar.

<!-- @os:windows -->
#### Adım 1: Önceden Derlenmiş İkili Dosyaları İndirin

En son sürüm sayfasına gidin ve platformunuza ve GPU hedefinize uygun arşivi indirin:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-windows-rocm-gfx1151-x64.zip` adlı dosyayı indirin (burada `xxxx` derleme numarasıdır).

#### Adım 2: İkili Dosyaları Ayıklayın

İndirilen arşivi ayıklayın:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Bu dizin artık Ryzen AI Halo sisteminiz için önceden derlenmiş, ROCm özellikli `llama-cli.exe`, `llama-server.exe` ve `ggml-rpc-server.exe` derlemelerini içermektedir.

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

#### Adım 2: İkili Dosyaları Ayıklayın ve Hazırlayın

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Bu dizin artık Ryzen AI Halo sisteminiz için önceden derlenmiş, ROCm özellikli `llama-cli`, `llama-server` ve `rpc-server` derlemelerini içermektedir.

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
Her düğümde llama.cpp hazırlandıktan sonra [Modeli İndirme](#downloading-the-model) bölümüne geçin.

### Seçenek 2: Manuel Kaynak Derlemesi

<!-- @os:windows -->
#### Adım 1: llama.cpp'yi Derleyin

**x64 Native Tools Command Prompt**'u açın (Visual Studio Build Tools ile birlikte kurulur) ve depoyu klonlayın:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

HIP'i PATH'inize ekleyin ve ROCm ile RPC desteğiyle derleyin:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Derleme Bayrağı | Amaç |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm/HIP yazılım yığınını etkinleştirir |
| `-DGGML_RPC=ON` | Dağıtık çıkarım için RPC'yi etkinleştirir |
| `-DGPU_TARGETS=gfx1151` | Ryzen AI Halo GPU'sunu (Radeon 8060s) hedefler |
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

#### Adım 3: HIP'i Kullanıcı PATH'inize Ekleyin

Yukarıdaki derleme adımı `%HIP_PATH%\bin` değerini yalnızca mevcut oturum için ayarladı. HIP kitaplıklarını herhangi bir terminalde (yalnızca x64 Native Tools Command Prompt'ta değil) kullanılabilir hale getirmek için, bunu kullanıcı `PATH`'inize kalıcı olarak ekleyin:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Her düğümde llama.cpp hazırlandıktan sonra [Modeli İndirme](#downloading-the-model) bölümüne geçin.
<!-- @os:end -->

<!-- @os:linux -->
#### Adım 1: llama.cpp'yi Derleyin

Depoyu klonlayın:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

ROCm ve RPC desteğiyle derleyin:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Derleme Bayrağı | Amaç |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm yazılım yığınını etkinleştirir |
| `-DGGML_RPC=ON` | Dağıtık çıkarım için RPC'yi etkinleştirir |
| `-DAMDGPU_TARGETS="gfx1151"` | Ryzen AI Halo GPU'sunu (Radeon 8060s) hedefler |

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

Her düğümde llama.cpp hazırlandıktan sonra [Modeli İndirme](#downloading-the-model) bölümüne geçin.
<!-- @os:end -->

## Modeli İndirme

Bu kılavuz, [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL)'dan `UD-Q2_K_XL` niceleme biçiminde [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) kullanmaktadır. Bu niceleme, dört Ryzen AI Halo düğümünün birleşik GPU belleğine sığmaktadır.

GGUF dosyalarını Hugging Face CLI kullanarak indirin:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **Not**: Model indirme işlemi Makine 1'de (denetleyici) tamamlanmalıdır. RPC işçi düğümleri (Makine 2, 3 ve 4) model dosyalarının yerel bir kopyasına ihtiyaç duymaz.

## Modeli Küme Üzerinde Başlatma

llama.cpp RPC (Remote Procedure Call) motoru, tek bir llama.cpp örneğinin model katmanlarını ağ üzerinden uzak işçilere aktarmasına olanak tanır. Bir makine **denetleyici** (Machine 1) olarak görev yapar; tokenizasyon, zamanlama ve orkestrasyonu üstlenir. Diğer üç makinenin her biri, GPU belleklerini ve işlem güçlerini denetleyiciye sunan hafif bir **RPC sunucusu** (Machine 2, 3 ve 4) çalıştırır.

Yükleme sırasında, llama.cpp modeli dört düğümün tamamına parçalar. Yüklendikten sonra, çıkarım tek bir hızlandırıcı üzerinde çalışıyormuş gibi ilerler. RPC, tensör aktarımlarını ve senkronizasyonu perde arkasında yönetir.

### Adım 1: RPC Sunucularını Başlatın (Machine 2, 3 ve 4)

Machine 2, 3 ve 4'ün her birinde, GPU kaynaklarını denetleyiciye sunmak için RPC sunucusunu başlatın:
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
| `-c` | Büyük tensörler için yerel bir önbellek etkinleştirir, model yükleme sırasında tekrarlanan ağ aktarımlarını önler |
| `--host` | RPC sunucusunun bağlanacağı IP adresi (tüm arayüzler için `0.0.0.0`) |

Daha fazla seçenek için [llama.cpp RPC belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md) bakın.

### Adım 2: Modeli Başlatın (Machine 1)

RPC sunucuları Machine 2, 3 ve 4'te çalışırken, Machine 1'den `llama-cli` veya `llama-server` kullanarak çıkarımı başlatın.
#### llama-cli

`llama-cli`, modelle doğrudan etkileşim kurmak için terminal tabanlı bir arayüz sağlar. Karşılaştırma testi (benchmarking), hata ayıklama ve düşük seviyeli deneyler için idealdir.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` bulma**: Makine 2, 3 ve 4'ün her birinde, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.
<!-- @os:end -->

<!-- @os:windows -->
> **Not**: Bu komutu Terminal'de (Powershell) çalıştırın.

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` bulma**: Makine 2, 3 ve 4'ün her birinde, yerel IP adresini bulmak için Terminal'de (Powershell) `ipconfig | findstr /C:"IPv4"` komutunu çalıştırın.

<!-- @os:end -->

Çalışmaya başladıktan sonra `llama-cli`, model yükleme ilerlemesini gösterir ve modelle doğrudan sohbet edebileceğiniz etkileşimli bir istem ekranına geçer:

![llama-cli, Kimi K2.6'yı dört düğümde çalıştırıyor](assets/llama-cli-example.png)

#### llama-server

`llama-server`, aynı çıkarım motorunu, tümleşik bir web arayüzüne ve OpenAI uyumlu bir HTTP API'sine sahip kalıcı bir sunucu süreci üzerinden sunar. Bu, daha uzun süreli dağıtımlar, çoklu kullanıcı erişimi ve harici araçlarla entegrasyon için tercih edilen arayüzdür.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` bulma**: Makine 2, 3 ve 4'ün her birinde, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.
<!-- @os:end -->

<!-- @os:windows -->
> **Not**: Bu komutu Terminal'de (Powershell) çalıştırın.

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` bulma**: Makine 2, 3 ve 4'ün her birinde, yerel IP adresini bulmak için Terminal'de (Powershell) `ipconfig | findstr /C:"IPv4"` komutunu çalıştırın.
<!-- @os:end -->

Başlatıldıktan sonra, tarayıcınızda dahili web arayüzüne erişmek için `http://<HOST_IP>:8081` adresini açın. Bu, modelle etkileşim kurmak için tarayıcı tabanlı bir sohbet arayüzü sunar:

![llama-server web arayüzü, Kimi K2.6'yı dört düğümde çalıştırıyor](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` bulma**: Makine 1'de, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` bulma**: Makine 1'de, yerel IP adresini bulmak için Terminal'de (Powershell) `ipconfig | findstr /C:"IPv4"` komutunu çalıştırın.
<!-- @os:end -->

#### Parametre Referansı

| Bayrak | Amaç |
|------|---------|
| `-m` | GGUF model dosyasının yolu (ilk parçayı kullanın, `00001-of-00008`) |
| `-c` | Token cinsinden bağlam boyutu. Daha büyük değerler daha fazla bellek kullanır |
| `-fa on` | AMD GPU'larda gelişmiş performans için rocWMMA Flash Attention'ı etkinleştirir |
| `-ngl 999` | Tüm model katmanlarını GPU'ya aktarır |
| `-lm none` | Model yükleme modunu `none` olarak ayarlar, model boyutu sistem RAM'ini aşıp VRAM'e sığdığında yükleme sürelerini azaltmak için bellek eşlemeyi (memory-mapping) devre dışı bırakır |
| `-b` | Token cinsinden mantıksal (logical) toplu iş boyutu. 4096 olarak ayarlamak, düğümler arasında verim ve bellek kullanımını dengeler |
| `-ub` | İstem işleme için fiziksel (mikro) toplu iş boyutu. `-b` ile eşleştirmek, gereksiz parçalama (chunking) yükünü önler |
| `--host` | `llama-server`in bağlanacağı IP (yalnızca `llama-server`) |
| `--port` | HTTP API'nin sunulacağı bağlantı noktası (yalnızca `llama-server`) |
| `--rpc` | Virgülle ayrılmış RPC çalışan uç noktaları listesi (`IP:port`) |

Tam parametre kullanımı için [llama-cli belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) ve [llama-server belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) bakın.

## Sonraki Adımlar

- **Üçüncü taraf uygulamaları bağlayın**: `llama-server`, OpenAI uyumlu bir API sunar. Kümenize bağlanmak için OpenAI uyumlu herhangi bir uygulamayı (Open WebUI gibi) yer tutucu bir API anahtarıyla (örneğin, `none`) `http://<HOST_IP>:8081` adresine yönlendirin
- **Diğer modelleri keşfedin**: Kümenizin toplam GPU belleğine sığan modelleri bulmak için [Hugging Face](https://huggingface.co/models?search=gguf) üzerinde nicelenmiş (quantized) GGUF'lara göz atın
- **Dört düğümün ötesine ölçeklendirin**: 1 trilyon parametre ölçeğinin ötesindeki modellere erişmek için ek RPC çalışanları olarak daha fazla Ryzen AI Halo sistemi ekleyin. `--rpc` parametresine ek uç noktaları virgülle ayrılmış bir liste olarak geçirin (örneğin, `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)