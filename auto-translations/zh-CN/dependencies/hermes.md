<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 安装 Hermes

使用官方安装程序安装 Hermes 代理 CLI。`--skip-setup` 标志可实现无人值守安装：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes 会安装到 `~/.local/bin` 中；请确保该目录已添加到你的 `PATH` 中。

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->