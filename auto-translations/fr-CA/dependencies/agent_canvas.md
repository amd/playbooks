<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation d'Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) est l'interface navigateur/CLI pour OpenHands, distribuée sous forme de paquet npm `@openhands/agent-canvas`. Elle nécessite **Node.js 24 ou version ultérieure**. Installez-la globalement :

```bash
npm install -g @openhands/agent-canvas
```

Le binaire `agent-canvas` se retrouve dans le répertoire bin global de npm (p. ex. `~/.npm-global/bin`); assurez-vous que ce répertoire figure dans votre `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->