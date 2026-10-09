<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 安装 OpenClaw

使用官方安装程序安装 OpenClaw：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-prompt --no-onboard` 标志会跳过交互式设置向导，这是无人值守安装所必需的；模型后端需单独配置。

> **提示：** 如果安装后出现 `command not found`，请将 npm 的全局 bin 目录添加到 PATH 中：
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> 要使其永久生效，请将上面这一行添加到你的 `~/.bashrc` 或 `~/.zshrc` 文件中。

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->