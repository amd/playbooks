<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 安装 uv

[uv](https://docs.astral.sh/uv/) 是 Agent Canvas 用来构建其 agent-server 环境的 Python 包/环境管理器。使用官方脚本安装它：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` 会安装到 `~/.local/bin`；请确保该目录位于你的 `PATH` 中。

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->