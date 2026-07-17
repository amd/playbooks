<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmasını açıklar.

## Gerekli Uygulamalar / Çerçeveler

| Bileşen         | Beklenen Yapılandırma                | Notlar                                                                       |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | `venv` desteğiyle Python           | `kernel-env` oluşturmak ve etkinleştirmek için kullanılır                    |
| ROCm Python SDK | ROCm 7.13 paket ailesi               | Playbook bağımlılık akışı aracılığıyla yüklenir                              |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | `torch.cuda`, HIP çalışma zamanı, JIT derlemesi ve `CUDAExtension` için gereklidir |
| GPU Sürücüsü    | ROCm/HIP destekli AMD GPU sürücüsü   | PyTorch'un AMD GPU'yu algılayabilmesi için gereklidir                        |

> Not: AMD Ryzen™ AI Halo Developer Platform üzerinde çalışıyorsanız, AMD ROCm™ yazılımı ve PyTorch önceden yüklenmiş olarak gelir.

## Linux Ön Koşulları

Aşağıdaki sistem paketleri gereklidir:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv`, `kernel-env` oluşturmak için gereklidir.
* `build-essential`, `gcc` ve `g++`, C++ uzantısı adım adım anlatımları için gereklidir.
* `amd-smi`, Linux GPU görünürlüğü/kullanım denetimlerinde kullanılır.

C++ uzantısı örnekleri, PyTorch'un `CUDAExtension` yolu kullanılarak `.cu` dosyalarından yerel `.so` modülleri derler.

## Windows Ön Koşulları

Windows çalıştırıcıları şunları gerektirir:

* `python` aracılığıyla erişilebilen Python
* En son sürümü yükleyin: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* **C++ ile masaüstü geliştirme** iş yüküyle birlikte [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) veya [daha yenisi](https://visualstudio.microsoft.com/vs/community/)

Visual Studio C++ ortamı şunları sağlamalıdır:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK dahil etme ve kitaplık yolları

C++ uzantısı örnekleri, PyTorch'un `CUDAExtension` yolu kullanılarak `.cu` dosyalarından yerel `.pyd` modülleri derler.