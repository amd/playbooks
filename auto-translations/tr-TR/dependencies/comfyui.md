<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. En son Windows ComfyUI yükleyicisini [download.comfy.org](https://download.comfy.org/windows/nsis/x64) adresinden indirin.
2. Donanım kurulumunuzu seçin: `AMD ROCm` seçeneğini belirleyin.
3. ComfyUI'nin kurulacağı yeri seçin: Varsayılan yolu veya tercih ettiğiniz klasörü kullanın.
4. Masaüstü Uygulama Ayarları: Bu uygulamanın önerilen sürümünü kullandığınızdan emin olmak için "Otomatik Güncellemeler" seçeneğinin işaretini kaldırmanızı öneririz.
5. Kurulumu başlatmak için "İleri"ye basın.

<!-- @os:end -->

<!-- @os:linux -->
#### ComfyUI'yi Klonlayın
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (İsteğe Bağlı) Belirli bir sürüme geçin
```bash
git checkout v0.19.2
```

#### ComfyUI gereksinimlerini yükleyin

Python sanal ortamı etkinleştirilmiş durumdayken şunu çalıştırın:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Not**: Daha fazla bilgi için [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) sayfasına bakın.

<!-- @os:end -->