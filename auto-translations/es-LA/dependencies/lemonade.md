<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Instalación de Lemonade

<!-- @os:windows -->
Descarga el instalador más reciente desde [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) y ejecuta el archivo `.msi`.

Después de la instalación:
- El CLI `lemonade` se agrega automáticamente al PATH del sistema
- Se espera que el servidor Lemonade se ejecute automáticamente en segundo plano

También puedes instalar de forma silenciosa desde la línea de comandos:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

Para otras distribuciones o para instalar desde el código fuente, consulta las [opciones de instalación completas](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Verificación de la instalación de Lemonade

Abre una terminal y ejecuta:
```bash
lemonade --version
```

Deberías ver una salida como:
```
lemonade version x.y.z
```

Si ves un número de versión, Lemonade está instalado correctamente y listo para usar.

Para referencia rápida, aquí están los comandos comunes del CLI de Lemonade:

| Comando | Qué hace |
| --- | --- |
| `lemonade --help` | Muestra todos los comandos y flags disponibles. |
| `lemonade --version` | Imprime la versión instalada de Lemonade. |
| `lemonade status` | Confirma si el servidor Lemonade está en ejecución y es accesible. La URL base predeterminada compatible con OpenAI es `http://localhost:13305/api/v1`. |
| `lemonade list` | Lista los modelos disponibles para tu configuración de Lemonade. |
| `lemonade pull <MODEL_NAME>` | Descarga un modelo sin iniciarlo. |
| `lemonade run <MODEL_NAME>` | Descarga el modelo si es necesario y luego lo inicia para inferencia/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Inicia un modelo llama.cpp con el backend ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Inicia un modelo llama.cpp con el backend Vulkan. |
| `lemonade config` | Muestra los valores de configuración actuales de Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Establece el backend predeterminado de llama.cpp en ROCm. |

Para conocer las últimas opciones del servidor Lemonade o para solución de problemas, consulta la [documentación oficial de Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).