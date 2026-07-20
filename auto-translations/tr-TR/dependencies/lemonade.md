<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Lemonade Kurulumu

<!-- @os:windows -->
En son yükleyiciyi [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) adresinden indirin ve `.msi` dosyasını çalıştırın.

Kurulumdan sonra:
- `lemonade` CLI, sisteminizin PATH değişkenine otomatik olarak eklenir
- Lemonade sunucusunun arka planda otomatik olarak çalışması beklenir

Ayrıca komut satırından sessiz kurulum da yapabilirsiniz:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

Diğer dağıtımlar için veya kaynak koddan kurulum yapmak için [tam kurulum seçeneklerine](https://lemonade-server.ai/docs/guide/install/) bakın.
<!-- @os:end -->


#### Lemonade Kurulumunun Doğrulanması

Bir terminal açın ve şunu çalıştırın:
```bash
lemonade --version
```

Şuna benzer bir çıktı görmelisiniz:
```
lemonade version x.y.z
```

Bir sürüm numarası görüyorsanız, Lemonade doğru şekilde kurulmuştur ve kullanıma hazırdır.

Hızlı başvuru için, sık kullanılan Lemonade CLI komutları aşağıda verilmiştir:

| Komut | Ne yapar |
| --- | --- |
| `lemonade --help` | Mevcut tüm komutları ve bayrakları gösterir. |
| `lemonade --version` | Yüklü Lemonade sürümünü yazdırır. |
| `lemonade status` | Lemonade sunucusunun çalışıp çalışmadığını ve erişilebilir olup olmadığını doğrular. Varsayılan OpenAI uyumlu API temel URL'si `http://localhost:13305/api/v1` şeklindedir. |
| `lemonade list` | Lemonade kurulumunuz için kullanılabilir modelleri listeler. |
| `lemonade pull <MODEL_NAME>` | Bir modeli başlatmadan indirir. |
| `lemonade run <MODEL_NAME>` | Gerekirse modeli indirir, ardından çıkarım/sohbet için başlatır. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | ROCm arka ucuyla bir llama.cpp modelini başlatır. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Vulkan arka ucuyla bir llama.cpp modelini başlatır. |
| `lemonade config` | Geçerli Lemonade yapılandırma değerlerini gösterir. |
| `lemonade config set llamacpp.backend=rocm` | Varsayılan llama.cpp arka ucunu ROCm olarak ayarlar. |

En güncel Lemonade sunucu seçenekleri veya sorun giderme için lütfen [resmi Lemonade belgelerine](https://lemonade-server.ai/docs/lemonade-cli/) başvurun.