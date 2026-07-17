<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Descărcați cel mai recent installer ComfyUI pentru Windows de la [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Alegeți configurația hardware: Selectați `AMD ROCm`.
3. Alegeți unde să instalați ComfyUI: Utilizați calea implicită sau folderul preferat.
4. Setări aplicație Desktop: Recomandăm deselectarea opțiunii „Actualizări automate" pentru a vă asigura că utilizați versiunea recomandată a acestei aplicații.
5. Apăsați „Next" pentru a începe instalarea.

<!-- @os:end -->

<!-- @os:linux -->
#### Clonați ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Opțional) Comutați la o versiune specifică
```bash
git checkout v0.19.2
```

#### Instalați cerințele ComfyUI

Cu mediul virtual Python activat, rulați:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Notă**: Consultați [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) pentru mai multe informații.

<!-- @os:end -->