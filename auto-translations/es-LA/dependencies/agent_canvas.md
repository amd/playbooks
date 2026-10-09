<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalación de Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) es la interfaz de navegador/CLI para OpenHands, distribuida como el paquete npm `@openhands/agent-canvas`. Requiere **Node.js 24 o posterior**. Instálalo de forma global:

```bash
npm install -g @openhands/agent-canvas
```

El binario `agent-canvas` se ubica en el bin global de npm (por ejemplo, `~/.npm-global/bin`); asegúrate de que ese directorio esté en tu `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->