<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalación de uv

[uv](https://docs.astral.sh/uv/) es el administrador de paquetes/entornos de Python que Agent Canvas utiliza para construir su entorno de agent-server. Instálalo con el script oficial:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` se instala en `~/.local/bin`; asegúrate de que ese directorio esté en tu `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->