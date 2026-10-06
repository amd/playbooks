<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalação do Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) é a interface de utilizador/CLI de navegador para o OpenHands, distribuída como o pacote npm `@openhands/agent-canvas`. Requer **Node.js 24 ou posterior**. Instale-o globalmente:

```bash
npm install -g @openhands/agent-canvas
```

O binário `agent-canvas` fica na pasta bin global do npm (por exemplo, `~/.npm-global/bin`); certifique-se de que esse diretório está no seu `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->