<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Agent Canvas Kurulumu

[Agent Canvas](https://github.com/OpenHands/agent-canvas), OpenHands için tarayıcı UI/CLI'sidir ve `@openhands/agent-canvas` npm paketi olarak dağıtılır. **Node.js 24 veya üzeri** gerektirir. Genel olarak yüklemek için:

```bash
npm install -g @openhands/agent-canvas
```

`agent-canvas` ikili dosyası npm'in genel bin dizinine (ör. `~/.npm-global/bin`) yerleşir; bu dizinin `PATH` üzerinde olduğundan emin olun.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->