<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 安裝 Hermes

使用官方安裝程式安裝 Hermes agent CLI。`--skip-setup` 旗標可讓安裝過程不需人工介入：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes 會安裝到 `~/.local/bin`；請確認該目錄已加入您的 `PATH`。

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->