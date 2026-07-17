<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Bu playbook, GitHub'ın işleyemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->

# RPC ile İki Ryzen™ AI Halo'yu Kümeleme

## Genel Bakış

Ryzen™ AI Halo'nuz büyük dil modellerini yerel olarak çalıştırma konusunda zaten yetkindir. Kümeleme, yerel bir ağ üzerinden birden fazla sistemin GPU belleğini birleştirerek bunu daha da ileri taşır; daha güçlü akıl yürütme, daha iyi kod üretimi ve daha derin çok dilli anlayışa sahip çok daha büyük modellere erişim sağlar; tüm bunlar tamamen kendi donanımınızda gerçekleşir.

Bu playbook, llama.cpp'nin RPC motoru kullanılarak iki Ryzen AI Halo sisteminin nasıl kümeleneceğini ve AMD ROCm™ hızlandırmasıyla her iki makinede 358B parametreli bir model olan GLM 4.7'nin nasıl çalıştırılacağını öğretir.

## Neler Öğreneceksiniz

- Ryzen AI Halo sistemlerinde VRAM tahsisini nasıl genişleteceğiniz
- ROCm ve RPC desteğiyle llama.cpp kurulumu
- Bir RPC çalışanı yapılandırma ve iki düğüm arasında dağıtık çıkarım başlatma
- Ağa bağlı iki Ryzen AI Halo sistemi arasında 358B parametreli bir modeli çalıştırma

## Bellek Yapılandırmasını Ayarlama

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

<!-- @os:windows -->
Windows'ta daha yüksek bellek gerektiren büyük modelleri çalıştırmak için AMD Variable Graphics Memory (iGPU VRAM) tahsisini kullanmamız gerekir.

Bu işlem, AMD Software: Adrenalin Edition kontrol paneli açılarak şu yola gidilerek yapılabilir: `Performance > Tuning > AMD Variable Graphics Memory`. Değeri **96 GB** olarak ayarlayın. Değişikliklerin geçerli olması için lütfen sistemi yeniden başlatın.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linux'ta ROCm, paylaşılan bir sistem bellek havuzu kullanır ve bu havuz varsayılan olarak sistem belleğinin yarısına yapılandırılmıştır.

Bu miktar, aşağıdaki talimatlar izlenerek çekirdeğin Translation Table Manager (TTM) sayfa ayarı değiştirilerek artırılabilir. AMD, BIOS'ta minimum ayrılmış VRAM ayarlanmasını önerir (0,5 GB).

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


<!-- @os:end -->
<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Edin

<!-- @require:software-update -->
<!-- @device:end -->
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
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Lütfen şunları yükleyin:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- **Desktop Development with C++** iş yüküyle [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fiziksel Donanım Kurulumu

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

Her Ryzen AI Halo birimini Cat 7 (veya üzeri) kablo kullanarak Ethernet anahtarına bağlayın. Bu, düğümler arasındaki yüksek hızlı iletişim için kullanılan 10Gbps bağlantısını oluşturur.
<!-- @os:linux -->
### 1. Ağ Arayüzlerini Belirleme

Her makinede ağ arayüzünün adını bulun ve not edin (aşağıda `IFNAME` olarak anılacaktır). Şunu çalıştırın:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Bu, arayüz adını doğrudan yazdırır, örneğin:

```bash
enp191s0
```

### 2. Ağ Bağlantı Hızlarını Doğrulama

Bağlantının etkin olduğunu ve tam hızda çalıştığını, arayüzünüzün hızını kontrol ederek doğrulayın:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Not**: `<IFNAME>` kısmını [1. Ağ Arayüzlerini Belirleme](#1-determine-network-interfaces) bölümündeki çıktı arayüz adıyla değiştirin.

`10000Mb/s` hızını görmelisiniz:

```bash
	Speed: 10000Mb/s
```

> **Not**: Hız `10000Mb/s`'den düşükse veya bağlantı kurulmazsa kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps olarak ayarlandığını doğrulayın. Bazı anahtarlar otomatik anlaşmanın devre dışı bırakılmasını ve bağlantı hızının manuel olarak ayarlanmasını gerektirir; anahtarınızın belgelerine başvurun.

<!-- @os:end -->

<!-- @os:windows -->
### Ağ Bağlantı Hızını Doğrulama

Her makinede ağ arayüzlerinizin bağlantı hızını kontrol edin:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet arayüzünüz `Up` durumunda ve `10 Gbps` hızında çalışıyor olmalıdır:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Not**: Hız `10 Gbps`'den düşükse veya bağlantı kurulmazsa kablo bağlantısını kontrol edin ve anahtar portunun 10Gbps olarak ayarlandığını doğrulayın. Bazı anahtarlar otomatik anlaşmanın devre dışı bırakılmasını ve bağlantı hızının manuel olarak ayarlanmasını gerektirir; anahtarınızın belgelerine başvurun.

<!-- @os:end -->

## llama.cpp Kurulumu

> **Not**: Bu adımı hem Makine 1 hem de Makine 2 üzerinde tamamlayın.

İki kurulum seçeneği mevcuttur:

- [Seçenek 1: Lemonade SDK (Önerilen)](#option-1-lemonade-sdk-recommended) - önceden derlenmiş ikili dosyalar, en hızlı kurulum
- [Seçenek 2: Manuel Kaynak Derleme](#option-2-manual-source-build) - derleme bayrakları üzerinde tam kontrol ile kaynaktan derleme

### Seçenek 1: Lemonade SDK (Önerilen)

Lemonade SDK, gfx1151 (Strix Halo / Ryzen AI Max+ 395) ve diğer yeni Radeon mimarileri gibi GPU'ları hedefleyen AMD ROCm 7 hızlandırmasıyla llama.cpp'nin gecelik derlemelerini sağlar.

<!-- @os:windows -->
#### Adım 1: Önceden Derlenmiş İkili Dosyaları İndirin

En son sürüm sayfasına gidin ve platformunuza ve GPU hedefinize uygun arşivi indirin:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-windows-rocm-gfx1151-x64.zip` adlı dosyayı indirin (`xxxx` derleme numarasıdır).

#### Adım 2: İkili Dosyaları Çıkarın

İndirilen arşivi sıkıştırmadan çıkarın:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Bu dizin artık Ryzen AI Halo sisteminiz için önceden derlenmiş, ROCm etkin `llama-cli.exe`, `llama-server.exe` ve `rpc-server.exe` derlemelerini içermektedir.

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

`llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` adlı dosyayı indirin (`xxxx` derleme numarasıdır).

#### Adım 2: İkili Dosyaları Çıkarın ve Hazırlayın

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Bu dizin artık Ryzen AI Halo sisteminiz için önceden derlenmiş, ROCm etkin `llama-cli`, `llama-server` ve `rpc-server` derlemelerini içermektedir.

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

### Seçenek 2: Manuel Kaynak Derleme

<!-- @os:windows -->
#### Adım 1: llama.cpp'yi Derleyin

**x64 Native Tools Command Prompt**'u (Visual Studio Build Tools ile yüklenir) açın ve depoyu klonlayın:

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

#### Adım 3: HIP'i Kullanıcı Yolunuza Ekleyin

Yukarıdaki derleme adımı `%HIP_PATH%\bin`'i yalnızca mevcut oturum için ayarlamıştır. HIP kitaplıklarını herhangi bir terminalde (yalnızca x64 Native Tools Command Prompt'ta değil) kullanılabilir kılmak için bunu kullanıcı `PATH`'inize kalıcı olarak ekleyin:

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
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Derleme Bayrağı | Amaç |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm yazılım yığınını etkinleştirir |
| `-DGGML_RPC=ON` | Dağıtık çıkarım için RPC'yi etkinleştirir |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | AMD GPU'larda gelişmiş Flash Attention için rocWMMA'yı etkinleştirir |
| `-DAMDGPU_TARGETS="gfx1151"` | Ryzen AI Halo GPU'sunu (Radeon 8060s) hedefler |

Daha fazla derleme seçeneği için [llama.cpp derleme belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) başvurun.

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

Bu playbook, [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) tarafından sağlanan `Q4_K_XL` nicemlendirmesinde 358B parametreli bir model olan [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)'yi kullanır. Bu nicemlendirmede model yaklaşık 205GB depolama alanı gerektirir ve iki Ryzen AI Halo düğümünün birleşik GPU belleğine sığar.

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

> **Not**: Model indirme işleminin Makine 1'de (denetleyici) tamamlanması gerekir. RPC çalışan düğümlerinin model dosyalarının yerel bir kopyasına ihtiyacı yoktur.

## Modeli Kümede Başlatma

llama.cpp RPC (Uzak Yordam Çağrısı) motoru, tek bir llama.cpp örneğinin model katmanlarını ağ üzerinden uzak çalışanlara aktarmasına olanak tanır. Bir makine **denetleyici** (Makine 1) olarak görev yapar; simgeleştirme, zamanlama ve düzenlemeyi üstlenir. Diğer makine, GPU belleğini ve hesaplama gücünü denetleyiciye sunan hafif bir **RPC sunucusu** (Makine 2) çalıştırır.

Yükleme sırasında llama.cpp, modeli her iki düğüme böler. Yüklendikten sonra çıkarım, tek bir hızlandırıcıda çalışıyormuş gibi ilerler. RPC, tensör aktarımlarını ve senkronizasyonu arka planda yönetir.

### Adım 1: RPC Sunucusunu Başlatın (Makine 2)

Makine 2'de, GPU kaynaklarını denetleyiciye sunmak için RPC sunucusunu başlatın:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Bayrak | Amaç |
|------|---------|
| `-p` | RPC sunucusunun yayın yapacağı port |
| `-c` | Büyük tensörler için yerel önbelleği etkinleştirir; model yükleme sırasında tekrarlanan ağ aktarımlarını önler |
| `--host` | RPC sunucusunun bağlanacağı IP adresi (tüm arayüzler için `0.0.0.0`) |

Daha fazla seçenek için [llama.cpp RPC belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md) başvurun.

### Adım 2: Modeli Başlatın (Makine 1)

Makine 2'de RPC sunucusu çalışırken, Makine 1'den `llama-cli` veya `llama-server` kullanarak çıkarımı başlatın.

#### llama-cli

`llama-cli`, modelle doğrudan etkileşim için terminal tabanlı bir arayüz sağlar. Kıyaslama, hata ayıklama ve düşük seviyeli deneyler için idealdir.

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

> **`<RPC_WORKER_IP>`'yi Bulma**: Makine 2'de yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.
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

> **`<RPC_WORKER_IP>`'yi Bulma**: Makine 2'de yerel IP adresini bulmak için Terminal'de (Powershell) `ipconfig | findstr /C:"IPv4"` komutunu çalıştırın.

<!-- @os:end -->

Çalışmaya başladığında `llama-cli`, model yükleme ilerlemesini görüntüler ve modelle doğrudan sohbet edebileceğiniz etkileşimli bir istem açar:

![İki düğüm arasında GLM 4.7 çalıştıran llama-cli](assets/llama-cli-example.png)

#### llama-server

`llama-server`, aynı çıkarım motorunu entegre bir web arayüzü ve OpenAI uyumlu bir HTTP API'si ile kalıcı bir sunucu süreci aracılığıyla sunar. Bu, uzun süreli dağıtımlar, çok kullanıcılı erişim ve harici araçlarla entegrasyon için tercih edilen arayüzdür.

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

> **`<RPC_WORKER_IP>`'yi Bulma**: Makine 2'de yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.
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

> **`<RPC_WORKER_IP>`'yi Bulma**: Makine 2'de yerel IP adresini bulmak için Terminal'de (Powershell) `ipconfig | findstr /C:"IPv4"` komutunu çalıştırın.
<!-- @os:end -->

Başlatıldıktan sonra, yerleşik web arayüzüne erişmek için tarayıcınızda `http://<HOST_IP>:8081` adresini açın. Bu, modelle etkileşim için tarayıcı tabanlı bir sohbet arayüzü sağlar:

![İki düğüm arasında GLM 4.7 çalıştıran llama-server web arayüzü](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>`'yi Bulma**: Makine 1'de yerel IP adresini bulmak için `hostname -I | awk '{print $1}'` komutunu çalıştırın.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>`'yi Bulma**: Makine 1'de yerel IP adresini bulmak için Terminal'de (Powershell) `ipconfig | findstr /C:"IPv4"` komutunu çalıştırın.
<!-- @os:end -->

#### Parametre Referansı

| Bayrak | Amaç |
|------|---------|
| `-m` | GGUF model dosyasının yolu (ilk parçayı kullanın, `00001-of-00005`) |
| `-c` | Token cinsinden bağlam boyutu. Daha büyük değerler daha fazla bellek kullanır |
| `-fa on` | AMD GPU'larda gelişmiş performans için rocWMMA Flash Attention'ı etkinleştirir |
| `-ngl 999` | Tüm model katmanlarını GPU'ya aktarır |
| `--no-mmap` | Bellek eşlemeyi devre dışı bırakır; model boyutu sistem RAM'ini aşıp VRAM'e sığdığında yükleme sürelerini azaltır |
| `--host` | `llama-server`'ın bağlanacağı IP (yalnızca `llama-server`) |
| `--port` | HTTP API'sinin sunulacağı port (yalnızca `llama-server`) |
| `--rpc` | Virgülle ayrılmış RPC çalışan uç noktaları listesi (`IP:port`) |

Tam parametre kullanımı için [llama-cli belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) ve [llama-server belgelerine](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) başvurun.

## Sonraki Adımlar

- **Üçüncü taraf uygulamaları bağlayın**: `llama-server`, OpenAI uyumlu bir API sunar. Herhangi bir OpenAI uyumlu uygulamayı (Open WebUI gibi) kümenize bağlamak için `http://<HOST_IP>:8081` adresini ve herhangi bir yer tutucu API anahtarını (örn. `none`) kullanın
- **Diğer modelleri keşfedin**: Kümenizin birleşik GPU belleğine sığan modelleri bulmak için [Hugging Face](https://huggingface.co/models?search=gguf) üzerindeki nicemlendirilen GGUF'lara göz atın
- **Dört düğüme ölçeklendirin**: 1 trilyon parametre ölçeğindeki modellere erişmek için ek RPC çalışanları olarak iki Ryzen AI Halo sistemi daha ekleyin. `--rpc`'ye virgülle ayrılmış liste olarak ek uç noktalar ekleyin (örn. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)