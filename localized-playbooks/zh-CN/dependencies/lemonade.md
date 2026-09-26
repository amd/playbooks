<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### 安装 Lemonade

<!-- @os:windows -->
从 [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) 下载最新安装程序，并运行 `.msi` 文件。

安装后：
- `lemonade` CLI 会自动添加到系统 PATH
- Lemonade server 预期会自动在后台运行

你也可以通过命令行静默安装：
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu：**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR)：**
```bash
yay -S lemonade-server
```

对于其他发行版，或需要从源码安装，请参阅[完整安装选项](https://lemonade-server.ai/docs/guide/install/)。
<!-- @os:end -->


#### 验证 Lemonade 安装

打开终端并运行：
```bash
lemonade --version
```

你应该会看到类似输出：
```
lemonade version x.y.z
```

如果能看到版本号，说明 Lemonade 已正确安装并可开始使用。

下面是常用 Lemonade CLI 命令，便于快速参考：

| 命令 | 作用 |
| --- | --- |
| `lemonade --help` | 显示所有可用命令和参数。 |
| `lemonade --version` | 输出已安装的 Lemonade 版本。 |
| `lemonade status` | 确认 Lemonade server 是否正在运行且可访问。默认兼容 OpenAI 的 API base URL 为 `http://localhost:13305/api/v1`。 |
| `lemonade list` | 列出当前 Lemonade 设置中可用的模型。 |
| `lemonade pull <MODEL_NAME>` | 下载模型，但不启动模型。 |
| `lemonade run <MODEL_NAME>` | 如有需要先下载模型，然后启动模型进行推理/聊天。 |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | 使用 ROCm 后端启动 llama.cpp 模型。 |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | 使用 Vulkan 后端启动 llama.cpp 模型。 |
| `lemonade config` | 显示当前 Lemonade 配置值。 |
| `lemonade config set llamacpp.backend=rocm` | 将默认 llama.cpp 后端设置为 ROCm。 |

有关最新 Lemonade server 选项或故障排除，请参阅 [Lemonade 官方文档](https://lemonade-server.ai/docs/lemonade-cli/)。
