<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 安裝 OpenClaw

使用官方安裝程式安裝 OpenClaw：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-prompt --no-onboard` 旗標會跳過互動式設定精靈，這在無人值守安裝時是必要的；模型後端需另外設定。

> **提示：** 若安裝後出現 `command not found`，請將 npm 的全域 bin 目錄加入 PATH：
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> 若要永久套用此設定，請將上述這行加入您的 `~/.bashrc` 或 `~/.zshrc` 檔案中。

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->