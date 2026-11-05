<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# 使用 AMD Sync 进行远程开发

## 概述

**AMD Sync** 可将您的笔记本电脑变为 AMD Ryzen™ AI Halo 的远程驾驶舱。无需手动设置 SSH、密钥和 IDE——只需安装 AMD Sync，即可一键访问远程终端、VS Code、JupyterLab 以及 Ryzen AI Halo 上的实时 GPU/CPU/内存仪表盘。

您的本地设备保持熟悉的操作方式；每条命令、每个笔记本和每个模型都在 Ryzen AI Halo 上运行。

> **提示**：本页面将包含 AMDSync 的所有新更新。

## 您将学到的内容

- 在 Ryzen AI Halo 上启用 SSH，并从 AMD Sync 连接到它
- 一键针对 Ryzen AI Halo 启动 VS Code、终端、JupyterLab 和实时指标
- 使用 AMD Sync 的托管项目文件夹组织远程工作

---

## 核心概念

AMD Sync 分为两端：**客户端**（运行 AMD Sync 应用的笔记本电脑）和**服务器端**（运行 SSH 服务器的 Ryzen AI Halo，AMD Sync 通过隧道连接到该服务器）。您从 AMD Sync 启动的所有内容——VS Code、终端、笔记本——都在本地打开，但在 Ryzen AI Halo 上执行。

> **支持的客户端：** Windows 11 和 Linux。不支持 macOS。

---

## 步骤 1 — 在 Ryzen AI Halo 上启用 SSH


> **注意：** 在 Windows 上，Ryzen AI Halo *默认关闭* SSH 服务器。在 Linux 上，它*默认开启* SSH 服务器。

1. 在 Ryzen AI Halo 上，打开 **AMD Ryzen™ AI Developer Center**。
2. 转到 **Remote** 选项卡。
3. 打开 **SSH Server** 开关。
4. 记下 **Server Information** 下显示的 **IP Address**（IP 地址）、**Port**（端口）和 **Username**（用户名）——您将把它们粘贴到 AMD Sync 中。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **注意：** 这是适用于 Windows 的 AMD Developer Center。Linux 版本的界面可能有所不同，但远程功能类似。

> **提示：** AMD Sync 要求输入该用户的**操作系统登录密码**，而不是 Developer Center 的密码。

---

## 步骤 2 — 在客户端安装 AMD Sync

AMD Sync 可在 Windows 11 和 Linux 上运行。下载适用于您操作系统的安装程序，然后按照以下步骤操作。安装完成后，在 **Get Started** 屏幕上点击 **Accept & Install**——安装完成后 AMD Sync 会自动启动。

### Windows

[下载 AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. 双击 `AMDSyncInstaller.exe`。
2. 点击 **Accept & Install**。

> 如果 Windows 防火墙弹出提示，请允许 AMD Sync 访问网络，以便其可以通过 SSH 访问 Ryzen AI Halo。

### Linux

点击链接下载您偏好的格式：

| 格式 | 下载 | 安装命令 |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **注意：** Ubuntu App Center 可能会将本地打开的 `.deb` 标记为*“可能不安全”*。这是针对任何第三方本地安装程序的标准警告。如果双击 `.deb` 失败，请使用上面的终端命令。

---

## 步骤 3 — 连接到您的 Ryzen AI Halo

首次启动时，AMD Sync 会显示 **Add a Remote Device** 表单。请使用 Developer Center 的 **Remote** 选项卡中的值填写该表单。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| 字段 | 说明 |
|-------|-------|
| **Device Name**（设备名称）*（可选）* | 一个友好的标签，如 `Ryzen AI Halo`。默认值为 `Device 1`、`Device 2`，……… |
| **Hostname or IP**（主机名或 IP） | 来自 Remote 选项卡 |
| **SSH Port**（SSH 端口） | 来自 Remote 选项卡（仅限数字） |
| **Username**（用户名） | 您在 Ryzen AI Halo 上的操作系统账户名 |
| **Password**（密码） | 您的操作系统登录密码——输入时将被遮盖 |

点击 **Add Device**。经过短暂的加载界面后，您将看到**“Connection Successful”**（连接成功），并进入主界面——该界面驻留在您的系统托盘中。点击窗口外部可将其关闭；AMD Sync 会继续在后台运行，随时可一键打开。

> **如果连接失败**，AMD Sync 会返回表单并保留您输入的值。常见原因包括：Ryzen AI Halo 上未启用 SSH、密码错误，或两台设备处于不同的网络中。

---

## 步骤 4 — 启动您的第一个远程工具

主界面提供五个一键式组件——无论客户端和 Ryzen AI Halo 运行的是哪种操作系统，这些组件均可使用。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| 组件 | 功能 |
|-----------|--------------|
| **Directory**（目录） | 选择 Ryzen AI Halo 上的文件夹，VS Code、Terminal 和 JupyterLab 将在该文件夹中打开。默认是一个托管的 `Documents/AMD_Sync` 工作区。 |
| **VS Code** | 在本地打开 VS Code，并通过 SSH 隧道连接到所选文件夹。 |
| **Terminal**（终端） | 打开一个通过 SSH 连接到 Ryzen AI Halo 的本地终端，位于所选文件夹中。 |
| **JupyterLab** | 启动一个通过 SSH 连接到 Ryzen AI Halo 的笔记本项目，范围限定在所选文件夹内。 |
| **Live Metrics**（实时指标） | 实时查看 Ryzen AI Halo 上的 GPU、内存和 CPU 利用率。 |

### 尝试使用 VS Code

对于首次启动，请尝试使用 **VS Code**。以下说明针对 Linux，但 Windows 上的体验类似。

1. 保留 **Directory** 为默认的 `~/Documents/AMD_Sync`。
2. 点击 **VS Code**。
3. AMD Sync 会在 Ryzen AI Halo 上创建 `Documents/AMD_Sync/Project_1`，并在本地打开 VS Code，通过隧道连接到该目录。

此时，您正在使用本地的 VS Code 设置编辑位于 Ryzen AI Halo 上的文件。创建 `helloworld.py`，添加 `print("hello world")`，打开集成终端（`` Ctrl + ` ``），然后运行：

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

状态栏显示 **SSH: Linux**——这证明您的代码正在 Ryzen AI Halo 上运行，而不是在您的笔记本电脑上。
### 试用终端

点击 **Terminal** 即可通过 SSH 进入相同的文件夹，无需离开键盘。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

在 Windows 上，默认终端是 **PowerShell**——如果你更喜欢，可以在设置菜单中切换为 **Windows Command Prompt**。在 Linux 上，AMD Sync 使用你的默认系统终端。

---

## 目录的工作方式

**Directory** 下拉菜单是 AMD Sync 中最重要的单个控件——它决定了你启动的每个工具会在 Ryzen AI Halo 上落在哪里。

- **`~/Documents/AMD_Sync`（默认）** —— 从这里启动 VS Code 或 JupyterLab 会自动创建一个新的项目文件夹（VS Code 为 `Project_1`、`Project_2`……；JupyterLab 为 `Notebook_Project_1`、`Notebook_Project_2`……）。
- **现有的项目文件夹** —— `AMD_Sync` 的任何直接子文件夹（包括你在 Ryzen AI Halo 上手动创建的文件夹）都会出现在下拉菜单中。你上次使用的文件夹会成为下次的默认选项。
- **自定义路径** —— 输入任意绝对路径即可打开 Ryzen AI Halo 上其他位置的文件夹。AMD Sync 只会*打开*它——不会在 `AMD_Sync` 之外创建文件夹，并且自定义路径不会在会话之间保存。

如果自定义路径不起作用，AMD Sync 会告诉你原因：语法无效、文件夹不存在，或该路径指向的是一个文件。

---

## 实时指标与 JupyterLab

- **Live Metrics** —— GPU、内存和 CPU 使用情况的实时仪表盘。是确认远程训练任务确实在使用硬件的最快方式。
- **JupyterLab** —— 一个完整的笔记本项目，通过 SSH 连接到 Ryzen AI Halo，并拥有自己的集成终端，可在不离开界面的情况下混合使用笔记本单元格和 shell 命令。

---

## 设置与多台设备

**Settings** 菜单有三个标签页：

| 标签页 | 内容 |
|-----|----------------|
| **Devices** | 列出你成功连接过的每一台 Ryzen AI Halo。可重新连接、编辑凭据，或添加新设备。 |
| **Information** | 指向文档和论坛支持的链接。 |
| **Customize** | 在桌面上重新定位应用、切换终端类型（仅限 Windows），以及检查 AMD Sync 更新。 |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **终端类型（Windows）** —— 在 **PowerShell**（默认）和 **Windows Command Prompt** 之间选择。
- **终端类型（Linux）** —— 仅提供默认系统终端。
- **应用更新** —— 这个标签页是在界面内检查并安装新版本 AMD Sync 的正确位置；无需单独的更新程序。

> 只有在首次连接成功后，设备才会出现在 **Devices** 下，因此失败的尝试不会使列表变得杂乱。

---

## 故障排除

- **连接立即失败** —— 确认 Developer Center 中 Ryzen AI Halo 的 **Remote** 标签页已启用 SSH 服务器。
- **密码错误提示** —— 使用 Ryzen AI Halo 上的 **操作系统登录密码**，而不是从 Developer Center 获取的密码。
- **VS Code 按钮没有反应** —— 从 [code.visualstudio.com](https://code.visualstudio.com) 在你的客户端机器上安装 VS Code。
- **AMD Sync 托盘图标缺失（Linux/GNOME）** —— 安装并启用 AppIndicator 扩展。
- **`.deb` 无法从文件管理器打开** —— 在终端中使用 `sudo apt install ./AMDSyncInstaller.deb`。
- **每次启动都重新出现设置界面（Linux）**：解锁你的登录密钥环，或使用 `--password-store=gnome-libsecret` 启动，然后重新完成一次设置。

---