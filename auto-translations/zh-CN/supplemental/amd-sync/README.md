<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# 使用 AMD Sync 进行远程开发

## 概述

**AMD Sync** 可将您的笔记本电脑变成 AMD Ryzen™ AI Halo 的远程控制台。无需手动配置 SSH、密钥和 IDE——安装 AMD Sync 后，即可一键访问 Ryzen AI Halo 上的远程终端、VS Code、JupyterLab，以及实时 GPU/CPU/内存监控面板。

您的本地机器保持原有的使用习惯；所有命令、笔记本和模型均在 Ryzen AI Halo 上运行。

> **提示**：本页面将包含 AMDSync 的所有最新更新。

## 您将学到的内容

- 在 Ryzen AI Halo 上启用 SSH，并通过 AMD Sync 连接到它
- 一键在 Ryzen AI Halo 上启动 VS Code、终端、JupyterLab 和实时监控指标
- 使用 AMD Sync 的托管项目文件夹组织远程工作

---

## 核心概念

AMD Sync 分为两端：**客户端**（您的笔记本电脑，运行 AMD Sync 应用）和**服务器**（Ryzen AI Halo，运行 AMD Sync 通过隧道连接的 SSH 服务器）。您从 AMD Sync 启动的所有内容——VS Code、终端、笔记本——均在本地打开，但在 Ryzen AI Halo 上执行。

> **支持的客户端：** Windows 11 和 Linux。不支持 macOS。

---

## 第一步 — 在 Ryzen AI Halo 上启用 SSH


> **注意：** 在 Windows 上，Ryzen AI Halo 默认*关闭* SSH 服务器。在 Linux 上，默认*开启* SSH 服务器。

1. 在 Ryzen AI Halo 上，打开 **AMD Ryzen™ AI Developer Center**。
2. 进入 **Remote** 选项卡。
3. 将 **SSH Server** 切换为开启状态。
4. 记录 **Server Information** 下显示的 **IP Address**、**Port** 和 **Username**——您需要将它们填入 AMD Sync。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **注意：** 这是 Windows 版 AMD Developer Center。Linux 版界面可能有所不同，但具有类似的远程功能。

> **提示：** AMD Sync 需要的是该用户的 **操作系统登录密码**，而非 Developer Center 中的密码。

---

## 第二步 — 在客户端安装 AMD Sync

AMD Sync 支持 Windows 11 和 Linux。请下载适用于您操作系统的安装程序，然后按照以下步骤操作。安装完成后，在 **Get Started** 界面点击 **Accept & Install**——AMD Sync 完成后将自动启动。

### Windows

[下载 AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. 双击 `AMDSyncInstaller.exe`。
2. 点击 **Accept & Install**。

> 如果 Windows 防火墙弹出提示，请允许 AMD Sync 访问网络，以便其通过 SSH 连接到 Ryzen AI Halo。

### Linux

点击链接下载您偏好的格式：

| 格式 | 下载 | 安装命令 |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **注意：** Ubuntu 应用中心可能会将本地打开的 `.deb` 文件标记为*"潜在不安全"*。这是针对任何第三方本地安装程序的标准警告。如果双击 `.deb` 文件失败，请使用上方的终端命令进行安装。

---

## 第三步 — 连接到您的 Ryzen AI Halo

首次启动时，AMD Sync 会显示 **Add a Remote Device** 表单。请使用 Developer Center **Remote** 选项卡中的值填写。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| 字段 | 说明 |
|-------|-------|
| **Device Name** *（可选）* | 一个友好的标签，例如 `Ryzen AI Halo`。默认为 `Device 1`、`Device 2`…… |
| **Hostname or IP** | 来自 Remote 选项卡 |
| **SSH Port** | 来自 Remote 选项卡（仅限数字） |
| **Username** | 您在 Ryzen AI Halo 上的操作系统账户名 |
| **Password** | 您的操作系统登录密码——输入时以掩码显示 |

点击 **Add Device**。短暂的加载界面后，您将看到 **"Connection Successful"**，并进入主视图，该视图位于系统托盘中。点击窗口外部可将其关闭；AMD Sync 将继续在后台运行，一键即可访问。

> **如果连接失败，** AMD Sync 将返回表单并保留您已填写的值。常见原因包括：Ryzen AI Halo 上未启用 SSH、密码错误，或两台设备不在同一网络中。

---

## 第四步 — 启动您的第一个远程工具

主视图提供五个一键组件——无论客户端和 Ryzen AI Halo 运行何种操作系统，均可使用。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| 组件 | 功能说明 |
|-----------|--------------|
| **Directory** | 选择 Ryzen AI Halo 上供 VS Code、终端和 JupyterLab 打开的文件夹。默认为托管的 `Documents/AMD_Sync` 工作区。 |
| **VS Code** | 在本地打开 VS Code，并通过 SSH 隧道连接到所选文件夹。 |
| **Terminal** | 打开一个通过 SSH 连接到 Ryzen AI Halo 的本地终端，位于所选文件夹中。 |
| **JupyterLab** | 启动一个通过 SSH 连接到 Ryzen AI Halo 的笔记本项目，范围限定在所选文件夹内。 |
| **Live Metrics** | 实时查看 Ryzen AI Halo 上的 GPU、内存和 CPU 使用情况。 |

### 试用 VS Code

首次启动时，建议试用 **VS Code**。

1. 将 **Directory** 保留为默认的 `~/Documents/AMD_Sync`。
2. 点击 **VS Code**。
3. AMD Sync 将在 Ryzen AI Halo 上创建 `Documents/AMD_Sync/Project_1`，并在本地打开 VS Code，通过隧道连接到该目录。

现在，您正在使用本地的 VS Code 编辑存储在 Ryzen AI Halo 上的文件。创建 `helloworld.py`，添加 `print("hello world")`，打开集成终端（`` Ctrl + ` ``），然后运行：

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

状态栏显示 **SSH: Linux**——这证明您的代码正在 Ryzen AI Halo 上运行，而非您的笔记本电脑。

### 试用终端

点击 **Terminal**，无需离开键盘即可通过 SSH 进入同一文件夹。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

在 Windows 上，默认终端为 **PowerShell**——如需切换，可在设置菜单中选择 **Windows Command Prompt**。在 Linux 上，AMD Sync 使用您系统的默认终端。

---

## Directory 的工作原理

**Directory** 下拉菜单是 AMD Sync 中最重要的控件——它决定了您启动的每个工具在 Ryzen AI Halo 上的落地位置。

- **`~/Documents/AMD_Sync`（默认）** — 从此处启动 VS Code 或 JupyterLab 时，系统会自动创建新的项目文件夹（VS Code 对应 `Project_1`、`Project_2`……；JupyterLab 对应 `Notebook_Project_1`、`Notebook_Project_2`……）。
- **现有项目文件夹** — `AMD_Sync` 的任何直接子文件夹（包括您在 Ryzen AI Halo 上手动创建的文件夹）都会出现在下拉菜单中。您上次使用的文件夹将成为下次的默认选项。
- **自定义路径** — 输入任意绝对路径以打开 Ryzen AI Halo 上其他位置的文件夹。AMD Sync 仅会*打开*该路径——不会在 `AMD_Sync` 之外创建文件夹，且自定义路径不会在会话之间保存。

如果自定义路径无效，AMD Sync 会告知原因：语法无效、文件夹不存在，或路径指向的是文件而非文件夹。

---

## 实时指标与 JupyterLab

- **Live Metrics** — GPU、内存和 CPU 使用情况的实时监控面板。这是确认远程训练任务是否真正在硬件上运行的最快方式。
- **JupyterLab** — 通过 SSH 连接到 Ryzen AI Halo 的完整笔记本项目，内置集成终端，可在不离开界面的情况下混合使用笔记本单元格和 Shell 命令。

---

## 设置与多设备管理

**Settings** 菜单包含三个选项卡：

| 选项卡 | 内容说明 |
|-----|----------------|
| **Devices** | 列出您成功连接过的所有 Ryzen AI Halo。可重新连接、编辑凭据或添加新设备。 |
| **Information** | 提供文档和论坛支持的链接。 |
| **Customize** | 调整应用在桌面上的位置、切换终端类型（仅限 Windows），以及检查 AMD Sync 更新。 |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **终端类型（Windows）** — 在 **PowerShell**（默认）和 **Windows Command Prompt** 之间选择。
- **终端类型（Linux）** — 仅支持系统默认终端。
- **应用更新** — 此选项卡是在界面内检查和安装新版 AMD Sync 的正确入口；无需单独的更新程序。

> 设备仅在首次成功连接后才会出现在 **Devices** 列表中，因此失败的连接尝试不会造成列表混乱。

---

## 故障排除

- **连接立即失败** — 确认 Ryzen AI Halo 在 Developer Center 的 **Remote** 选项卡中已启用 SSH 服务器。
- **密码错误** — 请使用 Ryzen AI Halo 上的**操作系统登录密码**，而非 Developer Center 中的密码。
- **VS Code 按钮无响应** — 请从 [code.visualstudio.com](https://code.visualstudio.com) 在客户端机器上安装 VS Code。
- **AMD Sync 托盘图标缺失（Linux/GNOME）** — 请安装并启用 AppIndicator 扩展。
- **`.deb` 文件无法从文件管理器打开** — 请在终端中使用 `sudo apt install ./AMDSyncInstaller.deb`。

---