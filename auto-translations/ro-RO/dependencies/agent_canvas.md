<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalarea Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) este interfața browser UI/CLI pentru OpenHands, distribuită ca pachetul npm `@openhands/agent-canvas`. Necesită **Node.js 24 sau o versiune ulterioară**. Instalați-l global:

```bash
npm install -g @openhands/agent-canvas
```

Binarul `agent-canvas` ajunge în directorul bin global al npm (de exemplu `~/.npm-global/bin`); asigurați-vă că acel director este în `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->