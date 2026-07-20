# 平台配置

本文档描述了运行此工作手册所需的预期平台配置。

## 前提条件

带有 ROCm 支持的 PyTorch 已在 AMD Ryzen™ AI Halo Developer Platform 上预安装。对于所有其他设备，用户必须手动安装带有 ROCm 支持的 PyTorch。请参阅适用于您操作系统的相关部分：

### Windows

| 组件     | 版本         | 说明                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 或更新版本    | 已在 AMD Ryzen AI Halo Developer Platform 上预安装；在所有其他设备上必须手动安装 |

### Linux

| 组件     | 版本         | 说明                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 或更新版本    | 已在 AMD Ryzen AI Halo Developer Platform 上预安装；在所有其他设备上必须手动安装 |

## 所需模型

以下模型已针对您的平台进行了测试和优化：

| 模型 | 参数 | 大小 | 下载位置 |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | 已在 AMD Ryzen AI Halo Developer Platform 上预安装；在所有其他设备上必须手动安装 |

模型将自动下载到 Hugging Face 缓存目录：
- **Windows**：`C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**：`~/.cache/huggingface/hub/`

请确保至少有 **20GB 可用空间** 用于模型存储。

## 网络要求

初始设置需要互联网访问以从 Hugging Face 下载模型。下载完成后，工作手册可以离线运行。

- 首次下载模型可能需要 **5-10 分钟**，具体取决于模型大小和网络连接速度
- 模型会被缓存在本地，无需重复下载