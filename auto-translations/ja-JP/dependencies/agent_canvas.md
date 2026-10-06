<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Agent Canvas のインストール

[Agent Canvas](https://github.com/OpenHands/agent-canvas) は OpenHands 用のブラウザ UI/CLI で、npm パッケージ `@openhands/agent-canvas` として配布されています。**Node.js 24 以降**が必要です。グローバルにインストールします。

```bash
npm install -g @openhands/agent-canvas
```

`agent-canvas` バイナリは npm のグローバル bin(例: `~/.npm-global/bin`)に配置されます。そのディレクトリが `PATH` に含まれていることを確認してください。

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->