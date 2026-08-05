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

**AMD Sync** 可将您的笔记本电脑变为 AMD Ryzen™ AI Halo 的远程控制台。无需手动配置 SSH、密钥和 IDE — 安装 AMD Sync，即可一键访问远程终端、VS Code、JupyterLab，以及 Ryzen AI Halo 上的实时 GPU/CPU/内存仪表盘。

您的本地设备保持熟悉的操作方式；而每条命令、每个 notebook 及每个模型都在 Ryzen AI Halo 上运行。

> **提示**：本页面将包含 AMDSync 的所有最新更新。

## 您将学到什么

- 在 Ryzen AI Halo 上启用 SSH，并从 AMD Sync 连接到它
- 一键针对 Ryzen AI Halo 启动 VS Code、终端、JupyterLab 和实时指标
- 使用 AMD Sync 的托管项目文件夹来组织远程工作

---

## 核心概念

AMD Sync 分为两端：**客户端**（您的笔记本电脑，运行 AMD Sync 应用）和**服务器**（Ryzen AI Halo，运行 SSH 服务器，AMD Sync 通过隧道连接到该服务器）。您从 AMD Sync 启动的一切内容 — VS Code、终端、notebook — 都在本地打开，但在 Ryzen AI Halo 上执行。

> **支持的客户端：** Windows 11 和 Linux。不支持 macOS。

---

## 步骤 1 — 在 Ryzen AI Halo 上启用 SSH


> **注意：** 在 Windows 上，Ryzen AI Halo 出厂时 SSH 服务器*默认关闭*。在 Linux 上，SSH 服务器*默认开启*。

1. 在 Ryzen AI Halo 上，打开 **AMD Ryzen™ AI Developer Center**。
2. 转到 **Remote** 选项卡。
3. 打开 **SSH Server** 开关。
4. 记下 **Server Information** 下显示的 **IP Address**、**Port** 和 **Username** — 稍后您需要将它们粘贴到 AMD Sync 中。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **注意：** 这是适用于 Windows 的 AMD Developer Center。Linux 版本的界面可能有所不同，但远程功能类似。

> **提示：** AMD Sync 要求输入该用户的**操作系统登录密码**，而不是 Developer Center 中的密码。

---

## 步骤 2 — 在客户端上安装 AMD Sync

AMD Sync 可在 Windows 11 和 Linux 上运行。请下载适用于您操作系统的安装程序，然后按照以下步骤操作。安装完成后，在**开始使用（Get Started）**界面上点击**接受并安装（Accept & Install）** — AMD Sync 会在安装完成后自动启动。

### Windows

[下载 AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. 双击 `AMDSyncInstaller.exe`。
2. 点击**接受并安装（Accept & Install）**。

> 如果 Windows 防火墙弹出提示，请允许 AMD Sync 访问网络，以便它能够通过 SSH 连接到 Ryzen AI Halo。

### Linux

点击链接以下载您偏好的格式：

| 格式 | 下载 | 安装命令 |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **注意：** Ubuntu App Center 可能会将本地打开的 `.deb` 文件标记为*“可能不安全”*。这是针对任何第三方本地安装程序的标准警告。如果双击 `.deb` 文件失败，请使用上述终端命令。

---

## 步骤 3 — 连接到您的 Ryzen AI Halo

首次启动时，AMD Sync 会显示**添加远程设备（Add a Remote Device）**表单。请使用 Developer Center 中 **Remote** 选项卡的值填写。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| 字段 | 说明 |
|-------|-------|
| **设备名称（Device Name）***（可选）* | 类似 `Ryzen AI Halo` 的友好标签。默认为 `Device 1`、`Device 2`……|
| **主机名或 IP（Hostname or IP）** | 来自 Remote 选项卡 |
| **SSH 端口（SSH Port）** | 来自 Remote 选项卡（仅限数字）|
| **用户名（Username）** | 您在 Ryzen AI Halo 上的操作系统账户名 |
| **密码（Password）** | 您的操作系统登录密码 — 输入时会被隐藏 |

点击**添加设备（Add Device）**。短暂加载后，您将看到**“连接成功（Connection Successful）”**，并进入主视图，该视图位于系统托盘中。点击窗口外部即可将其关闭；AMD Sync 会继续在后台运行，随时可一键调用。

> **如果连接失败，** AMD Sync 会返回表单，并保留您输入的值。常见原因包括 Ryzen AI Halo 上禁用了 SSH、密码错误，或两台设备处于不同网络。

---

## 步骤 4 — 启动您的第一个远程工具

主视图为您提供五个一键可用的组件 — 无论客户端和 Ryzen AI Halo 运行哪种操作系统，这些组件均可用。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| 组件 | 功能说明 |
|-----------|--------------|
| **目录（Directory）** | 选择 Ryzen AI Halo 上的文件夹，VS Code、终端和 JupyterLab 将在其中打开。默认使用托管的 `Documents/AMD_Sync` 工作区。 |
| **VS Code** | 在本地打开 VS Code，并通过 SSH 隧道连接到所选文件夹。 |
| **终端（Terminal）** | 打开一个通过 SSH 连接到 Ryzen AI Halo 的本地终端，位于所选文件夹中。 |
| **JupyterLab** | 启动一个通过 SSH 连接到 Ryzen AI Halo 的 notebook 项目，范围限定在所选文件夹内。 |
| **实时指标（Live Metrics）** | 实时查看 Ryzen AI Halo 上的 GPU、内存和 CPU 使用率。 |

### 试用 VS Code

首次启动时，请尝试使用 **VS Code**。

1. 将**目录（Directory）**保留为默认值 `~/Documents/AMD_Sync`。
2. 点击 **VS Code**。
3. AMD Sync 会在 Ryzen AI Halo 上创建 `Documents/AMD_Sync/Project_1`，并在本地打开通过隧道连接到该目录的 VS Code。

现在，您正在使用本地的 VS Code 设置编辑存放在 Ryzen AI Halo 上的文件。创建 `helloworld.py`，添加 `print("hello world")`，打开集成终端（`` Ctrl + ` ``），并运行它：

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

状态栏显示 **SSH: Linux** — 这证明您的代码正在 Ryzen AI Halo 上运行，而不是在您的笔记本电脑上。
### 试用终端

点击**终端 (Terminal)** 即可通过 SSH 进入同一文件夹，无需离开键盘。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

在 Windows 上，默认终端是 **PowerShell** —— 如果你更喜欢，可以从设置菜单切换到 **Windows 命令提示符**。在 Linux 上，AMD Sync 使用你的系统默认终端。

---

## 目录（Directory）的工作方式

**目录 (Directory)** 下拉菜单是 AMD Sync 中最重要的单一控件——它决定了你启动的每个工具会落在 Ryzen AI Halo 上的哪个位置。

- **`~/Documents/AMD_Sync`（默认）** —— 从这里启动 VS Code 或 JupyterLab 会自动创建一个全新的项目文件夹（VS Code 使用 `Project_1`、`Project_2`……；JupyterLab 使用 `Notebook_Project_1`、`Notebook_Project_2`……）。
- **已有的项目文件夹** —— `AMD_Sync` 的任何直接子文件夹（包括你在 Ryzen AI Halo 上手动创建的文件夹）都会出现在下拉菜单中。你上次使用的文件夹会成为下次的默认值。
- **自定义路径** —— 输入任意绝对路径即可打开 Ryzen AI Halo 上其他位置的文件夹。AMD Sync 只会*打开*它——不会在 `AMD_Sync` 之外创建文件夹，并且自定义路径不会在会话之间保存。

如果自定义路径无法使用，AMD Sync 会告诉你原因：语法无效、文件夹不存在，或路径指向的是一个文件。

---

## 实时指标与 JupyterLab

- **实时指标 (Live Metrics)** —— GPU、内存和 CPU 使用情况的实时仪表盘。这是确认远程训练任务确实在使用硬件的最快方式。
- **JupyterLab** —— 一个通过 SSH 连接到 Ryzen AI Halo 的完整笔记本项目，拥有自己集成的终端，可以在不离开界面的情况下混合使用笔记本单元格和 shell 命令。

---

## 设置与多设备

**设置 (Settings)** 菜单有三个选项卡：

| 选项卡 | 内容 |
|-----|----------------|
| **设备 (Devices)** | 列出你成功连接过的每一台 Ryzen AI Halo。可以重新连接、编辑凭据，或添加新设备。 |
| **信息 (Information)** | 提供文档和论坛支持的链接。 |
| **自定义 (Customize)** | 重新放置应用在桌面上的位置、切换终端类型（仅限 Windows），以及检查 AMD Sync 更新。 |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **终端类型（Windows）** —— 在 **PowerShell**（默认）和 **Windows 命令提示符**之间选择。
- **终端类型（Linux）** —— 仅提供默认系统终端。
- **应用更新** —— 该选项卡是在界面内检查并安装新版本 AMD Sync 的合适位置；无需单独的更新程序。

> 只有在成功建立首次连接后，设备才会出现在**设备 (Devices)** 下方，因此失败的尝试不会使列表变得杂乱。

---

## 故障排除

- **连接立即失败** —— 请确认已在 Developer Center 的 **远程 (Remote)** 选项卡中为 Ryzen AI Halo 启用了 SSH 服务器。
- **密码错误提示** —— 请使用 Ryzen AI Halo 上的**操作系统登录密码**，而不是从 Developer Center 获取的密码。
- **VS Code 按钮没有反应** —— 请从 [code.visualstudio.com](https://code.visualstudio.com) 在客户端机器上安装 VS Code。
- **AMD Sync 托盘图标缺失（Linux/GNOME）** —— 安装并启用 AppIndicator 扩展。
- **无法从文件管理器打开 `.deb` 文件** —— 请在终端中使用 `sudo apt install ./AMDSyncInstaller.deb`。

---