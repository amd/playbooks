<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 安装 Hermes

使用官方安装程序安装 Hermes agent CLI。`--skip-setup` 标志可使安装过程无需人工干预：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes 会安装到 `~/.local/bin` 中；请确保该目录已包含在你的 `PATH` 中。

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->