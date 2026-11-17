<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. 从 [download.comfy.org](https://download.comfy.org/windows/nsis/x64) 下载最新的 Windows ComfyUI 安装程序。
2. 选择你的硬件配置：选择 `AMD ROCm`。
3. 选择 ComfyUI 的安装位置：使用默认路径或你偏好的文件夹。
4. 桌面应用设置：建议取消勾选“自动更新（Automatic Updates）”，以确保你使用的是该应用的推荐版本。
5. 点击“Next”开始安装。

<!-- @os:end -->

<!-- @os:linux -->
#### 克隆 ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### （可选）切换到指定版本
```bash
git checkout v0.19.2
```

#### 安装 ComfyUI 所需依赖

在已激活 Python 虚拟环境的情况下，运行：
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **注意**：更多信息请参阅 [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI)。

<!-- @os:end -->