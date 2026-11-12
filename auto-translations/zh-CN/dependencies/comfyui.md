<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. 从 [download.comfy.org](https://download.comfy.org/windows/nsis/x64) 下载最新的 Windows ComfyUI 安装程序。
2. 选择你的硬件配置：选择 `AMD ROCm`。
3. 选择 ComfyUI 的安装位置：使用默认路径或你偏好的文件夹。
4. 桌面应用设置：我们建议取消选中“自动更新”，以确保你使用的是推荐版本的此应用。
5. 按“下一步”开始安装。

<!-- @os:end -->

<!-- @os:linux -->
#### 克隆 ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### （可选）切换到特定版本
```bash
git checkout v0.19.2
```

#### 安装 ComfyUI 依赖项

激活 Python 虚拟环境后，运行：
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **注意**：更多信息请参阅 [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI)。

<!-- @os:end -->