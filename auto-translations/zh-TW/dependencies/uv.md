<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 安裝 uv

[uv](https://docs.astral.sh/uv/) 是 Agent Canvas 用來建置其 agent-server 環境的 Python 套件/環境管理工具。請使用官方腳本安裝：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` 會安裝到 `~/.local/bin`，請確認該目錄已加入你的 `PATH`。

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->