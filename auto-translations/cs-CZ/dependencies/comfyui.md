<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Stáhněte si nejnovější instalační program ComfyUI pro Windows z [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Vyberte konfiguraci hardwaru: Zvolte `AMD ROCm`.
3. Vyberte, kam se má ComfyUI nainstalovat: Použijte výchozí cestu nebo preferovanou složku.
4. Nastavení desktopové aplikace: Doporučujeme zrušit zaškrtnutí možnosti „Automatic Updates“, abyste měli jistotu, že používáte doporučenou verzi této aplikace.
5. Stisknutím tlačítka „Next“ zahajte instalaci.

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

Po aktivaci virtuálního prostředí Python spusťte:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Poznámka**: Další informace naleznete na [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI).

<!-- @os:end -->