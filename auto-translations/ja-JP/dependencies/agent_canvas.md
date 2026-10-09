<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Agent Canvasのインストール

[Agent Canvas](https://github.com/OpenHands/agent-canvas)はOpenHands用のブラウザUI/CLIであり、npmパッケージ`@openhands/agent-canvas`として配布されています。**Node.js 24以降**が必要です。グローバルにインストールするには次のようにします。

```bash
npm install -g @openhands/agent-canvas
```

`agent-canvas`バイナリはnpmのグローバルbin（例：`~/.npm-global/bin`）に配置されます。このディレクトリが`PATH`に含まれていることを確認してください。

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->