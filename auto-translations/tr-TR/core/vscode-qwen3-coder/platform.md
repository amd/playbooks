<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmalarını açıklar.

## Windows

### LM Studio Kurulumu

LM Studio önceden kurulu olmalıdır:

| Bileşen | Sürüm | Konum |
|-----------|---------|----------|
| **LM Studio (Modeller + Çeşitli)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Önbellek)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Model İndirme

Aşağıdaki modeller LM Studio modeller dizininde (`C:\Users\...\.lmstudio\models`) zaten mevcut olmalıdır:

| Model Türü | Kuantizasyon | Boyut | Konum |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18,2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio Kurulumu

Daha fazla ayrıntı için lmstudio.md dosyasına bakın (bağımlılıklar klasörünün içinde).

### Model İndirme

Windows ile aynıdır.