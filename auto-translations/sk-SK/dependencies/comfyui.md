<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Stiahnite si najnovší inštalátor ComfyUI pre Windows z [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Vyberte konfiguráciu hardvéru: Zvoľte `AMD ROCm`.
3. Vyberte, kam nainštalovať ComfyUI: Použite predvolenú cestu alebo vami preferovaný priečinok.
4. Nastavenia desktopovej aplikácie: Odporúčame zrušiť výber „Automatic Updates", aby ste mali istotu, že používate odporúčanú verziu tejto aplikácie.
5. Stlačte „Next" a začnite inštaláciu.

<!-- @os:end -->

<!-- @os:linux -->
#### Klonovanie ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Voliteľné) Prepnutie na konkrétnu verziu
```bash
git checkout v0.19.2
```

#### Inštalácia požiadaviek ComfyUI

S aktivovaným virtuálnym prostredím Python spustite:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Poznámka**: Ďalšie informácie nájdete na [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI).

<!-- @os:end -->