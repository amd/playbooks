<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Lemonade Kurulumu

<!-- @os:windows -->
En son yükleyiciyi [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) adresinden indirin ve `.msi` dosyasını çalıştırın.

Kurulumdan sonra:
- `lemonade` CLI, sistem PATH'inize otomatik olarak eklenir
- Lemonade sunucusunun arka planda otomatik olarak çalışması beklenir

Komut satırından sessiz kurulum da yapabilirsiniz:
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

Diğer dağıtımlar için veya kaynaktan kurulum yapmak için [tam kurulum seçeneklerine](https://lemonade-server.ai/docs/guide/install/) bakın.
<!-- @os:end -->


#### Lemonade Kurulumunu Doğrulama

Bir terminal açın ve şunu çalıştırın:
```bash
lemonade --version
```

Aşağıdakine benzer bir çıktı görmelisiniz:
```
lemonade version x.y.z
```

Bir sürüm numarası görüyorsanız, Lemonade doğru şekilde kurulmuş ve kullanıma hazır demektir.

Hızlı başvuru için, yaygın Lemonade CLI komutları şunlardır:

| Komut | Ne yapar |
| --- | --- |
| `lemonade --help` | Mevcut tüm komutları ve bayrakları gösterir. |
| `lemonade --version` | Kurulu Lemonade sürümünü yazdırır. |
| `lemonade status` | Lemonade sunucusunun çalışıp çalışmadığını ve erişilebilir olup olmadığını doğrular. Varsayılan OpenAI uyumlu API temel URL'si `http://localhost:13305/api/v1` şeklindedir. |
| `lemonade list` | Lemonade kurulumunuzda kullanılabilir modelleri listeler. |
| `lemonade pull <MODEL_NAME>` | Bir modeli başlatmadan indirir. |
| `lemonade run <MODEL_NAME>` | Gerekirse modeli indirir, ardından çıkarım/sohbet için başlatır. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Bir llama.cpp modelini ROCm arka ucuyla başlatır. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Bir llama.cpp modelini Vulkan arka ucuyla başlatır. |
| `lemonade config` | Mevcut Lemonade yapılandırma değerlerini görüntüler. |
| `lemonade config set llamacpp.backend=rocm` | Varsayılan llama.cpp arka ucunu ROCm olarak ayarlar. |

En güncel Lemonade sunucu seçenekleri veya sorun giderme için lütfen [resmi Lemonade belgelerine](https://lemonade-server.ai/docs/lemonade-cli/) başvurun.