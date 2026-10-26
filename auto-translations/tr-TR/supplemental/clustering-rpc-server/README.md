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

# RPC ile İki Ryzen™ AI Halo'nun Kümelenmesi

## Genel Bakış

Ryzen™ AI Halo'nuz zaten büyük dil modellerini yerel olarak çalıştırma yeteneğine sahiptir. Kümeleme, birden fazla sistemin GPU belleğini yerel ağ üzerinden birleştirerek bunu bir adım öteye taşır ve size daha güçlü akıl yürütme, daha iyi kod üretimi ve daha derin çok dilli anlama yeteneğine sahip, tamamen kendi donanımınızda çalışan daha büyük modellere erişim sağlar.

Bu kılavuz, llama.cpp'nin RPC motorunu kullanarak iki Ryzen AI Halo sistemini nasıl kümeleyeceğinizi ve AMD ROCm™ hızlandırması ile her iki makinede 358B parametreli bir model olan GLM 4.7'yi nasıl çalıştıracağınızı öğretir.

## Öğrenecekleriniz

- Ryzen AI Halo sistemlerinde VRAM tahsisini genişletme
- ROCm ve RPC desteğiyle llama.cpp kurulumu
- Bir RPC çalışanı yapılandırma ve iki düğüm üzerinde dağıtık çıkarımı başlatma
- İki ağa bağlı Ryzen AI Halo sisteminde 358B parametreli bir model çalıştırma

## Bellek Yapılandırmasının Ayarlanması

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

<!-- @device:halo_box -->
<!-- @os:windows -->
> **128 GB'a yakın veya üzerindeki modelleri çalıştırma:** Windows çalıştıran AMD Ryzen™ AI Max 400 Serisi (Gorgon Halo) sistemlerinde, 128 GB belleğe yaklaşan veya bunu aşan modellerin hatasız çalışması için ek yapılandırma gerekir. Modeli yüklemeden önce [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) belgesindeki adımları izleyin.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Windows üzerinde, daha yüksek bellek gerektiren daha büyük modelleri çalıştırmak için AMD Variable Graphics Memory (iGPU VRAM) tahsisini kullanmamız gerekir.

Bu işlem, AMD Software: Adrenalin Edition kontrol panelini açarak ve şu yola giderek yapılabilir: `Performance > Tuning > AMD Variable Graphics Memory`. Değeri **96 GB** olarak ayarlayın. Değişikliklerin etkili olması için lütfen sistemi yeniden başlatın.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linux üzerinde ROCm, paylaşımlı bir sistem bellek havuzu kullanır ve bu havuz varsayılan olarak sistem belleğinin yarısı olacak şekilde yapılandırılmıştır.

Bu miktar, çekirdeğin Translation Table Manager (TTM) sayfa ayarı aşağıdaki talimatlarla değiştirilerek artırılabilir. AMD, BIOS'ta minimum özel VRAM'in (0,5 GB) ayarlanmasını önerir.

* pipx aracını yükleyin ve pipx ile kurulan wheel'lerin yolunu sistem arama yoluna ekleyin.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* amd-debug-tools wheel'ini PyPI'dan yükleyin.
  ```bash
  pipx install amd-debug-tools
  ```

* Mevcut paylaşımlı bellek ayarlarını sorgulamak için amd-ttm aracını çalıştırın.
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

Bu kılavuz, yıldız topolojisinde bağlanmış, her bir birimin anahtarlamaya doğrudan kablolu olduğu iki Ryzen AI Halo birimi ve bir Ethernet anahtarı gerektirir.

| Bileşen | Miktar | Açıklama |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Kümeyi oluşturan işlem düğümleri |
| 10Gbps Ethernet anahtarı | 1 | Çoklu düğüm Ryzen AI Halo iletişimine olanak tanıyan merkezi anahtar (en az 2 port) |
| Ethernet kablosu | 2 | Her Halo birimini anahtara bağlar (Cat 7 veya üzeri önerilir) |

> **Not**: İki Ryzen AI Halo birimini bağlamak için iki Ethernet anahtar portu gereklidir. Modele Halo birimlerinden birinden değil de ayrı bir istemci makineden erişiyorsanız üçüncü bir port gereklidir.

### Yazılım
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Lütfen şunları yükleyin:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- **Desktop Development with C++** iş yüküyle birlikte [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe)
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fiziksel Donanım Kurulumu

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

Her bir Ryzen AI Halo birimini, Cat 7 (veya üzeri) kablo kullanarak Ethernet anahtarına bağlayın. Bu, düğümler arasındaki yüksek hızlı iletişim için kullanılan 10Gbps bağlantıyı kurar.
<!-- @os:linux -->
### 1. Ağ Arayüzlerini Belirleme

Her makinede, ağ arayüzünün adını bulun ve not edin (aşağıda `IFNAME` olarak anılacaktır). Şunu çalıştırın:

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

> **Not**: `<IFNAME>` ifadesini [1. Ağ Arayüzlerini Belirleme](#1-determine-network-interfaces) bölümündeki çıktı arayüz adıyla değiştirin

`10000Mb/s` hızını görmelisiniz:

```bash
	Speed: 10000Mb/s
```

> **Not**: Hız `10000Mb/s` değerinden düşükse veya bağlantı kurulamıyorsa, kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps olarak ayarlandığını doğrulayın. Bazı anahtarlar otomatik müzakerenin devre dışı bırakılmasını ve bağlantı hızının manuel olarak ayarlanmasını gerektirir; anahtarınızın belgelerine bakın.

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

> **Not**: Hız `10 Gbps` değerinden düşükse veya bağlantı kurulamıyorsa, kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps olarak ayarlandığını doğrulayın. Bazı anahtarlar otomatik müzakerenin devre dışı bırakılmasını ve bağlantı hızının manuel olarak ayarlanmasını gerektirir; anahtarınızın belgelerine bakın.

<!-- @os:end -->

## llama.cpp Kurulumu

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

İki kurulum seçeneği mevcuttur:

- [Seçenek 1: Lemonade SDK (Önerilen)](#option-1-lemonade-sdk-recommended) - önceden derlenmiş ikili dosyalar, en hızlı kurulum
- [Seçenek 2: Manuel Kaynak Derlemesi](#option-2-manual-source-build) - derleme bayrakları üzerinde tam kontrol ile kaynaktan derleme
### Seçenek 1: Lemonade SDK (Önerilen)

Lemonade SDK, gfx1151 (Strix Halo / Ryzen AI Max+ 395) gibi GPU'ları ve diğer yeni Radeon mimarilerini hedefleyen, AMD ROCm 7 hızlandırmalı llama.cpp'nin gecelik derlemelerini sağlar.

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

Bu dizin artık `llama-cli.exe`, `llama-server.exe` ve `rpc-server.exe`'nin, Ryzen AI Halo sisteminiz için önceden derlenmiş ROCm destekli yapılarını içermektedir.

#### Adım 3: GPU Algılamasını Doğrulayın

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

Bu dizin artık `llama-cli`, `llama-server` ve `rpc-server`'ın, Ryzen AI Halo sisteminiz için önceden derlenmiş ROCm destekli yapılarını içermektedir.

#### Adım 3: GPU Algılamasını Doğrulayın

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

#### Adım 2: GPU Algılamasını Doğrulayın

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

Yukarıdaki derleme adımı `%HIP_PATH%\bin` değerini yalnızca mevcut oturum için ayarladı. HIP kütüphanelerini herhangi bir terminalde (yalnızca x64 Native Tools Command Prompt'ta değil) kullanılabilir hale getirmek için bunu kalıcı olarak kullanıcı `PATH` değişkeninize ekleyin:

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
| `-DAMDGPU_TARGETS="gfx1151"` | Ryzen AI Halo GPU'yu (Radeon 8060s) hedefler |

Daha fazla derleme seçeneği için [llama.cpp derleme belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) bakın.

#### Adım 2: GPU Algılamasını Doğrulayın

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

Bu kılavuz, Unsloth'tan `Q4_K_XL` nicemlemesinde 358B parametreli bir model olan [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)'yi kullanır ([Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL)). Bu nicemlemede model yaklaşık 205GB depolama alanı gerektirir ve iki Ryzen AI Halo düğümünün birleşik GPU belleğine sığar.

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

> **Not**: Model indirme işlemi, Makine 1'de (denetleyici) tamamlanmalıdır. RPC işçi düğümlerinin model dosyalarının yerel bir kopyasına ihtiyacı yoktur.

## Modeli Küme Üzerinde Başlatma

llama.cpp RPC (Remote Procedure Call) motoru, tek bir llama.cpp örneğinin model katmanlarını ağ üzerinden uzak işçilere aktarmasına olanak tanır. Bir makine **denetleyici** (Makine 1) olarak görev yapar; belirteçleştirme, zamanlama ve düzenlemeyi yönetir. Diğer makine ise GPU belleğini ve hesaplamasını denetleyiciye sunan hafif bir **RPC sunucusu** (Makine 2) çalıştırır.

Yükleme sırasında llama.cpp, modeli her iki düğüm arasında parçalara ayırır. Yüklendikten sonra çıkarım, tek bir hızlandırıcı üzerinde çalışıyormuş gibi devam eder. RPC, tensör aktarımlarını ve senkronizasyonu arka planda yönetir.

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
| `-c` | Model yükleme sırasında tekrarlanan ağ aktarımlarını önlemek amacıyla büyük tensörler için yerel bir önbellek etkinleştirir |
| `--host` | RPC sunucusunun bağlanacağı IP adresi (tüm arayüzler için `0.0.0.0`) |

Daha fazla seçenek için [llama.cpp RPC belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md) bakın.

### Adım 2: Modeli Başlatın (Makine 1)

Makine 2'de RPC sunucusu çalışırken, Makine 1'den `llama-cli` veya `llama-server` kullanarak çıkarımı başlatın.
#### llama-cli

`llama-cli`, modelle doğrudan etkileşim kurmak için terminal tabanlı bir arayüz sağlar. Kıyaslama (benchmarking), hata ayıklama ve düşük seviyeli deneyler için idealdir.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` bulma**: Makine 2 üzerinde, yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.
<!-- @os:end -->

<!-- @os:windows -->
> **Not**: Bu komutu Terminal'de (Powershell) çalıştırın.

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` bulma**: Makine 2 üzerinde, yerel IP adresini bulmak için Terminal'de (Powershell) `ipconfig | findstr /C:"IPv4"` komutunu çalıştırın.

<!-- @os:end -->

Çalışmaya başladığında, `llama-cli` model yükleme ilerlemesini gösterir ve modelle doğrudan sohbet edebileceğiniz etkileşimli bir komut istemi açar:

![GLM 4.7'yi iki düğümde çalıştıran llama-cli](assets/llama-cli-example.png)

#### llama-server

`llama-server`, aynı çıkarım motorunu entegre bir web arayüzü ve OpenAI uyumlu bir HTTP API'ye sahip kalıcı bir sunucu süreci üzerinden sunar. Bu, daha uzun süre çalışan dağıtımlar, çok kullanıcılı erişim ve harici araçlarla entegrasyon için tercih edilen arayüzdür.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
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
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` bulma**: Makine 2 üzerinde, yerel IP adresini bulmak için Terminal'de (Powershell) `ipconfig | findstr /C:"IPv4"` komutunu çalıştırın.
<!-- @os:end -->

Başlatıldıktan sonra, yerleşik web arayüzüne erişmek için tarayıcınızda `http://<HOST_IP>:8081` adresini açın. Bu, modelle etkileşim kurmak için tarayıcı tabanlı bir sohbet arayüzü sağlar:

![GLM 4.7'yi iki düğümde çalıştıran llama-server web arayüzü](assets/llama-server-example.png)

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
| `-fa on` | AMD GPU'larda gelişmiş performans için rocWMMA Flash Attention'ı etkinleştirir |
| `-ngl 999` | Tüm model katmanlarını GPU'ya aktarır |
| `-lm none` | Model yükleme modunu `none` olarak ayarlayarak, model boyutu sistem RAM'ini aşıp VRAM'e sığdığında yükleme sürelerini azaltmak için bellek eşlemeyi (memory-mapping) devre dışı bırakır |
| `--host` | `llama-server`'ın bağlanacağı IP (yalnızca `llama-server`) |
| `--port` | HTTP API'nin sunulacağı port (yalnızca `llama-server`) |
| `--rpc` | Virgülle ayrılmış RPC çalışan uç noktaları listesi (`IP:port`) |

Tam parametre kullanımı için [llama-cli belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) ve [llama-server belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) bakın.

## Sonraki Adımlar

- **Üçüncü taraf uygulamaları bağlayın**: `llama-server`, OpenAI uyumlu bir API sunar. Kümenize bağlanmak için herhangi bir OpenAI uyumlu uygulamayı (Open WebUI gibi) yer tutucu bir API anahtarıyla (ör. `none`) `http://<HOST_IP>:8081` adresine yönlendirin
- **Diğer modelleri keşfedin**: Kümenizin toplam GPU belleğine sığan modelleri bulmak için [Hugging Face](https://huggingface.co/models?search=gguf) üzerindeki nicelenmiş GGUF'lere göz atın
- **Dört düğüme ölçekleyin**: 1 trilyon parametre ölçeğindeki modellere erişmek için ek RPC çalışanları olarak iki Ryzen AI Halo sistemi daha ekleyin. Ek uç noktaları `--rpc` parametresine virgülle ayrılmış bir liste olarak geçirin (ör. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)