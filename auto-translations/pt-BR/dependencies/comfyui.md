<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Baixe o instalador mais recente do ComfyUI para Windows em [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Escolha sua configuração de hardware: Selecione `AMD ROCm`.
3. Escolha onde instalar o ComfyUI: Use o caminho padrão ou sua pasta preferida.
4. Configurações do Aplicativo Desktop: Recomendamos desmarcar "Automatic Updates" para garantir que você esteja usando a versão recomendada deste aplicativo.
5. Pressione "Next" para iniciar a instalação.

<!-- @os:end -->

<!-- @os:linux -->
#### Clone ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Opcional) Faça checkout de uma versão específica
```bash
git checkout v0.19.2
```

#### Instale os requisitos do ComfyUI

Com o ambiente virtual Python ativado, execute:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Nota**: Consulte o [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) para mais informações.

<!-- @os:end -->