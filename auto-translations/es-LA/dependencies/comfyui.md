<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Descarga el instalador de ComfyUI para Windows más reciente desde [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Elige tu configuración de hardware: Selecciona `AMD ROCm`.
3. Elige dónde instalar ComfyUI: Usa la ruta predeterminada o la carpeta que prefieras.
4. Configuración de la aplicación de escritorio: Recomendamos deseleccionar "Automatic Updates" para asegurarte de estar usando la versión recomendada de esta aplicación.
5. Presiona "Next" para comenzar la instalación.

<!-- @os:end -->

<!-- @os:linux -->
#### Clonar ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Opcional) Cambiar a una versión específica
```bash
git checkout v0.19.2
```

#### Instalar los requisitos de ComfyUI

Con el entorno virtual de Python activado, ejecuta:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Nota**: Consulta [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) para obtener más información.

<!-- @os:end -->