<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### 安装 Lemonade

<!-- @os:windows -->
从 [lemonade-server.ai](https://lemonade-server.ai/docs/guide/install/) 下载最新的安装程序并运行 `.msi` 文件。发布了两个安装程序,它们不可互换:

| 安装程序 | 内容 |
|-----------|----------|
| [`lemonade.msi`](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) | 服务器**及** Lemonade 桌面应用。除非有特殊原因,否则请使用此安装程序。 |
| [`lemonade-server-minimal.msi`](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade-server-minimal.msi) | 仅服务器,无桌面应用。 |

安装完成后:
- `lemonade` 命令行工具会自动添加到系统 PATH 中
- Lemonade 服务器会自动在后台运行
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

如需其他发行版或从源代码安装,请参阅[完整安装选项](https://lemonade-server.ai/docs/guide/install/)。
<!-- @os:end -->


#### 验证 Lemonade 安装

打开终端并运行:
```bash
lemonade --version
```

应该会看到类似以下的输出:
```
lemonade version x.y.z
```

如果看到版本号,说明 Lemonade 已正确安装并可以使用。

为便于快速参考,以下是常用的 Lemonade 命令行命令:

| 命令 | 作用 |
| --- | --- |
| `lemonade --help` | 显示所有可用的命令和参数。 |
| `lemonade --version` | 打印已安装的 Lemonade 版本。 |
| `lemonade status` | 确认 Lemonade 服务器是否正在运行且可访问。默认的 OpenAI 兼容 API 基础 URL 为 `http://localhost:13305/api/v1`。 |
| `lemonade list` | 列出你的 Lemonade 环境中可用的模型。 |
| `lemonade pull <MODEL_NAME>` | 下载模型但不启动它。 |
| `lemonade run <MODEL_NAME>` | 如有需要会下载模型,然后启动它以进行推理/对话。 |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | 使用 ROCm 后端启动 llama.cpp 模型。 |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | 使用 Vulkan 后端启动 llama.cpp 模型。 |
| `lemonade config` | 显示当前的 Lemonade 配置值。 |
| `lemonade config set llamacpp.backend=rocm` | 将默认的 llama.cpp 后端设置为 ROCm。 |

有关最新的 Lemonade 服务器选项或故障排除信息,请参阅[官方 Lemonade 文档](https://lemonade-server.ai/docs/lemonade-cli/)。