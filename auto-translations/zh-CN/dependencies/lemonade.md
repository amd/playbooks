<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### 安装 Lemonade

<!-- @os:windows -->
从 [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) 下载最新的安装程序,并运行该 `.msi` 文件。

安装完成后:
- `lemonade` CLI 会自动添加到系统 PATH 中
- Lemonade 服务器将自动在后台运行

您也可以通过命令行进行静默安装:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
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

对于其他发行版,或希望从源代码安装,请参阅[完整安装选项](https://lemonade-server.ai/docs/guide/install/)。
<!-- @os:end -->


#### 验证 Lemonade 安装

打开终端并运行:
```bash
lemonade --version
```

您应该会看到如下输出:
```
lemonade version x.y.z
```

如果看到版本号,则说明 Lemonade 已正确安装并可以使用。

以下是常用 Lemonade CLI 命令,供快速参考:

| 命令 | 作用 |
| --- | --- |
| `lemonade --help` | 显示所有可用命令和参数。 |
| `lemonade --version` | 打印已安装的 Lemonade 版本。 |
| `lemonade status` | 确认 Lemonade 服务器是否正在运行且可访问。默认的 OpenAI 兼容 API 基础 URL 为 `http://localhost:13305/api/v1`。 |
| `lemonade list` | 列出您的 Lemonade 环境中可用的模型。 |
| `lemonade pull <MODEL_NAME>` | 下载模型但不启动它。 |
| `lemonade run <MODEL_NAME>` | 如有需要则下载模型,然后启动它以进行推理/聊天。 |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | 使用 ROCm 后端启动 llama.cpp 模型。 |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | 使用 Vulkan 后端启动 llama.cpp 模型。 |
| `lemonade config` | 显示当前的 Lemonade 配置值。 |
| `lemonade config set llamacpp.backend=rocm` | 将默认的 llama.cpp 后端设置为 ROCm。 |

有关最新的 Lemonade 服务器选项或故障排除,请参阅[官方 Lemonade 文档](https://lemonade-server.ai/docs/lemonade-cli/)。