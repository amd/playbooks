<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Pobierz najnowszy instalator ComfyUI dla systemu Windows ze strony [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Wybierz konfigurację sprzętową: Wybierz `AMD ROCm`.
3. Wybierz miejsce instalacji ComfyUI: Użyj domyślnej ścieżki lub preferowanego folderu.
4. Ustawienia aplikacji desktopowej: Zalecamy odznaczenie opcji „Automatyczne aktualizacje", aby mieć pewność, że używasz zalecanej wersji tej aplikacji.
5. Naciśnij „Dalej", aby rozpocząć instalację.

<!-- @os:end -->

<!-- @os:linux -->
#### Sklonuj ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Opcjonalnie) Przełącz się na określoną wersję
```bash
git checkout v0.19.2
```

#### Zainstaluj wymagania ComfyUI

Po aktywowaniu wirtualnego środowiska Python uruchom:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Uwaga**: Więcej informacji znajdziesz na stronie [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI).

<!-- @os:end -->