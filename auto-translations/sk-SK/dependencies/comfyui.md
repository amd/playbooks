<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Stiahnite si najnovší inštalátor ComfyUI pre Windows z [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Vyberte svoju hardvérovú konfiguráciu: Zvoľte `AMD ROCm`.
3. Vyberte, kam chcete nainštalovať ComfyUI: Použite predvolenú cestu alebo vami preferovaný priečinok.
4. Nastavenia aplikácie Desktop App: Odporúčame zrušiť výber "Automatic Updates" (Automatické aktualizácie), aby ste zaistili používanie odporúčanej verzie tejto aplikácie.
5. Stlačením tlačidla "Next" spustite inštaláciu.

<!-- @os:end -->

<!-- @os:linux -->
#### Naklonujte ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Voliteľné) Prepnite sa na konkrétnu verziu
```bash
git checkout v0.19.2
```

#### Nainštalujte požiadavky ComfyUI

S aktivovaným virtuálnym prostredím Python spustite:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Poznámka**: Ďalšie informácie nájdete na [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI).

<!-- @os:end -->