<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

# Platform Yapılandırması

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmasını açıklamaktadır.

## Gerekli Uygulamalar / Çerçeveler

| Bileşen          | Beklenen Yapılandırma                | Notlar                                                                        |
| ---------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python           | `venv` desteğine sahip Python        | `kernel-env` oluşturmak ve etkinleştirmek için kullanılır                    |
| ROCm Python SDK  | ROCm 7.13 paket ailesi               | Playbook bağımlılık akışı üzerinden yüklenir                                  |
| PyTorch ROCm     | PyTorch 2.11.0 + ROCm 7.13           | `torch.cuda`, HIP çalışma zamanı, JIT derlemesi ve `CUDAExtension` için gereklidir |
| GPU Sürücüsü     | ROCm/HIP desteğine sahip AMD GPU sürücüsü | PyTorch'un AMD GPU'yu algılayabilmesi için önce bu gereklidir            |

> Not: AMD Ryzen™ AI Halo Geliştirici Platformu üzerinde çalışıyorsanız, AMD ROCm™ yazılımı ve PyTorch önceden yüklenmiş olarak gelir.

## Linux Ön Koşulları

Aşağıdaki sistem paketleri gereklidir:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `kernel-env` oluşturmak için `python3-venv` gereklidir.
* C++ uzantısı örnekleri için `build-essential`, `gcc` ve `g++` gereklidir.
* Linux GPU görünürlüğü/kullanım kontrolleri için `amd-smi` kullanılır.

C++ uzantısı örnekleri, PyTorch'un `CUDAExtension` yolunu kullanarak `.cu` dosyalarından yerel `.so` modülleri derler.

## Windows Ön Koşulları

Windows çalıştırıcıları şunları gerektirir:

* `python` üzerinden erişilebilen Python
* En güncel sürümü yükleyin: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* **Desktop development with C++** iş yüküyle birlikte [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) veya [daha yenisi](https://visualstudio.microsoft.com/vs/community/)

Visual Studio C++ ortamı şunları sağlamalıdır:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK dahil etme ve kitaplık yolları

C++ uzantısı örnekleri, PyTorch'un `CUDAExtension` yolunu kullanarak `.cu` dosyalarından yerel `.pyd` modülleri derler.