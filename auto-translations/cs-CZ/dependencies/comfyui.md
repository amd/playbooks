<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Stáhněte nejnovější instalátor ComfyUI pro Windows z [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Zvolte nastavení hardwaru: Vyberte `AMD ROCm`.
3. Zvolte, kam nainstalovat ComfyUI: Použijte výchozí cestu nebo vámi preferovanou složku.
4. Nastavení desktopové aplikace: Doporučujeme zrušit výběr možnosti „Automatic Updates", abyste zajistili používání doporučené verze této aplikace.
5. Stiskněte „Next" pro zahájení instalace.

<!-- @os:end -->

<!-- @os:linux -->
#### Klonování ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Volitelné) Přepnutí na konkrétní verzi
```bash
git checkout v0.19.2
```

#### Instalace požadavků ComfyUI

S aktivovaným virtuálním prostředím Python spusťte:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Poznámka**: Další informace naleznete na [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI).

<!-- @os:end -->