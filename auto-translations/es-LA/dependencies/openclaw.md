<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalación de OpenClaw

Instala OpenClaw con el instalador oficial:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Las opciones `--no-prompt --no-onboard` omiten el asistente de configuración interactivo, lo cual es necesario para instalaciones desatendidas; el backend del modelo se configura por separado.

> **Consejo:** Si ves `command not found` después de la instalación, agrega el directorio global bin de npm a tu PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Para que esto sea permanente, agrega la línea anterior a tu archivo `~/.bashrc` o `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->