<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Descarregue o instalador mais recente do ComfyUI para Windows em [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Escolha a sua configuração de hardware: Selecione `AMD ROCm`.
3. Escolha onde instalar o ComfyUI: Utilize o caminho predefinido ou a pasta da sua preferência.
4. Definições da aplicação de ambiente de trabalho: Recomendamos que desmarque "Automatic Updates" para garantir que está a utilizar a versão recomendada desta aplicação.
5. Prima "Next" para iniciar a instalação.

<!-- @os:end -->

<!-- @os:linux -->
#### Clonar o ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Opcional) Obter uma versão específica
```bash
git checkout v0.19.2
```

#### Instalar os requisitos do ComfyUI

Com o ambiente virtual Python ativado, execute:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Nota**: Consulte o [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) para mais informações.

<!-- @os:end -->