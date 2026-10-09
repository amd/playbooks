<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Установка Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) — это браузерный UI/CLI для OpenHands, распространяемый в виде npm-пакета `@openhands/agent-canvas`. Для него требуется **Node.js 24 или новее**. Установите его глобально:

```bash
npm install -g @openhands/agent-canvas
```

Исполняемый файл `agent-canvas` появится в глобальной папке bin для npm (например, `~/.npm-global/bin`); убедитесь, что этот каталог добавлен в `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->