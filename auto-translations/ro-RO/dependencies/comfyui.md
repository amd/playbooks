<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Descărcați cel mai recent program de instalare ComfyUI pentru Windows de pe [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Alegeți configurația hardware: Selectați `AMD ROCm`.
3. Alegeți locul unde va fi instalat ComfyUI: Utilizați calea implicită sau folderul preferat.
4. Setările aplicației desktop: Vă recomandăm să deselectați „Automatic Updates” pentru a vă asigura că utilizați versiunea recomandată a acestei aplicații.
5. Apăsați „Next” pentru a începe instalarea.

<!-- @os:end -->

<!-- @os:linux -->
#### Clonați ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Opțional) Extrageți o versiune specifică
```bash
git checkout v0.19.2
```

#### Instalați cerințele ComfyUI

Cu mediul virtual Python activat, executați:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Notă**: Consultați [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) pentru mai multe informații.

<!-- @os:end -->