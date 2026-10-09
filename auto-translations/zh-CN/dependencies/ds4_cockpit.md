<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 安装 ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) 是一个轻量级终端界面，用于处理创建 toolbox 容器、下载模型权重以及启动服务器等工作。使用 `pipx` 安装它：

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx` 会将入口程序安装到 `~/.local/bin` 中；请确保该目录已包含在你的 `PATH` 中。

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->