<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 使用 Lemonade Server 作为后端运行 OpenClaw

## 概述

[**OpenClaw**](https://openclaw.ai/) 是一个自主 AI 智能体，能够代表你编写和运行代码、管理文件，并完成复杂的多步骤任务。与只会回答问题的聊天助手不同，OpenClaw 会在你的系统上执行真实操作，这意味着它需要一个能够跟上高强度智能体循环的快速、强大的 AI 后端。

[**Lemonade Server**](https://lemonade-server.ai/) 就是这样的后端。它是一个开源的本地推理服务器，可直接在你的硬件上运行 GenAI 模型，并通过行业标准的 OpenAI API 对外提供服务。

两者结合，构成了一套完全本地化的 AI 智能体技术栈：Lemonade 负责模型推理，OpenClaw 提供将模型输出转化为实际操作的智能体循环。

> **在继续之前：** OpenClaw 是一个高度自主的 AI 智能体。让任何 AI 智能体访问你的系统都可能导致不可预测或非预期的结果。请仅在你理解相关风险并能够接受自主软件代表你行动的情况下继续操作。

---

## 你将学到什么

阅读完本操作指南后，你将能够：

- 了解 **Lemonade Server**
- **安装 OpenClaw**，并**将其指向 Lemonade Server**作为其 AI 后端。
- **启动 OpenClaw 网关**，并确认你的智能体已准备就绪。
- **连接一个通信渠道**（Discord 或 Telegram），以便你可以在任意设备上与你的智能体聊天。

---

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

<!-- @os:linux -->
- 一台运行 **Ubuntu 24.04+** 或兼容的基于 Debian 且带有 `apt-get` 的 Linux 发行版的 PC
- 至少 **12 GB 内存**（对于更大的模型建议 64 GB 以上）
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)（可选，用于对 OpenClaw 进行沙箱隔离）
- 用于模型权重的 **约 10–30 GB 可用磁盘空间**
<!-- @os:end -->

<!-- @os:windows -->
- 一台运行 **Windows 10/11** 的 PC
- 至少 **12 GB 内存**（对于更大的模型建议 64 GB 以上）
- 用于模型权重的 **约 10–30 GB 可用磁盘空间**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)（可选，用于对 OpenClaw 进行沙箱隔离）
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 拉取并加载推荐模型

本操作指南推荐的模型是来自 Unsloth 的 **Qwen3.6-35B-A3B-GGUF**，这是一个强大的 MoE 模型，拥有 263k 词元的上下文窗口，非常适合智能体工作负载。该模型使用 UD-Q4_K_XL 量化。现在拉取该模型：

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

然后以较大的上下文窗口加载它，并将该设置保存以供以后运行使用：

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

该模型的默认上下文长度为 262,144 词元。如果遇到内存不足（OOM）错误，可以考虑减小上下文窗口。但由于 Qwen3.6 会利用扩展上下文来处理复杂任务，我们建议保持至少 128K 词元的上下文长度，以保留其思考能力。

> **提示：禁用思考模式以获得更快的智能体响应：** Qwen3.6-35B-A3B 默认在思考模式下运行，这会在每次响应前增加延迟。对于智能体循环而言，这种开销会迅速累积。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 仓库提供了一个可禁用思考模式的现成配置。要使用它，请下载该文件并导入：
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"

python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
model_id = "${openclaw_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->

## 设置 WSL

我们在 WSL 中运行 OpenClaw（推荐做法），并将其连接到在 Windows 上原生运行的 Lemonade。这样你既可以为 OpenClaw 提供 Linux Shell 环境，又能在 Windows 端保留 Lemonade 的 GPU 加速能力。

### 安装 WSL 和 Ubuntu

以管理员身份打开 PowerShell，并安装 WSL 内核：

```powershell
wsl --install --no-distribution
```

然后安装 Ubuntu：

```powershell
wsl --install -d Ubuntu-24.04
```

### 在 WSL 中启用 systemd

在 Ubuntu 终端中运行以下命令：

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

退出 WSL 并重新启动它：

```powershell
exit
wsl --shutdown
wsl
```

### 将 Lemonade 从 Windows 桥接到 WSL

WSL2 运行在一个虚拟网络中。Windows 上的 Lemonade 绑定到 `127.0.0.1`，而 WSL 无法直接访问该地址。可以通过 Windows 端口代理，将流量从 WSL 网关 IP 转发到 Windows 本地主机。

**查找你的 WSL 网关 IP**（在 WSL 中运行）：

```bash
ip route show default | awk '{print $3}' | head -1
```

**添加端口代理**（以管理员身份在 PowerShell 中运行，将 `<WSL-Gateway-IP>` 替换为你的 WSL 网关 IP）：

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> 注意：如果遇到 `netsh: command not found` 错误，请尝试改用完整的可执行文件名称——`netsh.exe`

**添加防火墙规则**（在同一个提升权限的 PowerShell 中）：

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**从 WSL 中进行验证**：

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

如果你在上一步中已经加载了 Qwen3.6-35B-A3B-GGUF 模型，你应该会看到如下所示的 JSON 输出：

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

#### 重启后保持网桥正常工作

`netsh portproxy` 规则在重启后仍然有效，但 WSL 网关 IP 在执行 `wsl --shutdown` 或重启后可能会发生变化。此时，代理仍指向旧的 IP，导致 Lemonade 无法从 WSL 访问。如果发生这种情况，请使用以下选项之一。

**选项 1（推荐）— 自动修复网桥。** 为避免每次都手动执行此操作，请使用计划任务在每次启动和登录时检查网桥，并仅在网关 IP 发生变化时才重建它。请参阅 [Lemonade WSL 网桥自动修复指南](assets/RepairLemonadeWslBridge.md)。


**选项 2 — 手动修复网桥。** 首先，在 WSL 内运行以下命令获取当前的 WSL 网关 IP：

```bash
ip route show default | awk '{print $3}' | head -1
```

复制此值；您将在下面用它替换 `<new-WSL-Gateway-IP>`。

然后，在**提升权限的 PowerShell**（以管理员身份运行）中，列出现有规则，仅删除过期的 Lemonade 规则，并使用当前 IP 添加一条新规则：

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

在 `show all` 的输出中，过期的 Lemonade 规则是连接地址为 `127.0.0.1`、端口为 `13305` 的条目；其监听地址就是您的 `<old-WSL-Gateway-IP>`。按该地址删除只会移除这一条规则，不会影响您计算机上的其他端口代理规则。

您在设置过程中添加的防火墙规则绑定的是端口 `13305`（而非 IP），因此它会持续生效，无需重新创建。

> **建议：** 为避免网关问题，我们强烈建议采用以下 shell 配置：
> - **Windows 命令**应在 **PowerShell** 中执行
> - **WSL 发行版命令**应在**命令提示符**（以**管理员身份**运行）中执行

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## 安装和配置 OpenClaw

### 安装 OpenClaw
<!-- @os:windows -->
> 请在您的 **WSL 终端**中运行本节中的命令。
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` 标志会跳过交互式设置向导，您将在下一步手动配置模型后端，这能让您精确控制使用哪个模型和服务器。

打开一个新终端并确认安装：

```bash
openclaw --version
```

> **提示：** 如果安装后出现 `command not found`，请将 npm 的全局 bin 目录添加到您的 PATH 中：
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> 要使此设置永久生效，请将上面这行添加到您的 `~/.bashrc` 或 `~/.zshrc` 文件中。

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


### 配置 OpenClaw 以使用 Lemonade

运行 OpenClaw 的非交互式引导程序。
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

此命令会将 OpenClaw 的配置写入 `~/.openclaw/openclaw.json`。

> **OpenClaw 上下文窗口大小设置：** 当 `contextTokens > contextWindow − reserveTokens` 时，OpenClaw 的压缩机制就会触发。默认的 `reserveTokensFloor` 为 20,000 个 token，这是一个下限值，当它高于 `reserveTokens` 时会覆盖后者，因此任何低于约 37k 的模型上下文都会触发无限压缩循环。在您的配置中一次性设置一个较低的保留值并禁用该下限，它就会应用于所有模型，无需针对每个模型单独调整：
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` 是一个*下限*（最小保护值），并非保留值本身，仅设置下限不会产生任何效果。`reserveTokensFloor: 0` 会禁用该保护机制，从而使较低的 `reserveTokens` 值得以生效。
>
> **何时应用此设置：** 如果您模型的有效上下文窗口低于约 37k（无论是因为模型本身较小，例如 8k、16k、32k，还是因为您有意将其限制为较低的值，例如加载了一个 128k 的模型但在 Lemonade 中将上下文设置为 16k），请使用此配置。否则，OpenClaw 在启动时会陷入无限压缩循环。
>
> **满上下文的大上下文模型：** 您可以完全跳过此设置。默认值运作良好，压缩会在窗口填满之前就适时启动，模型也有充足的空间生成长回复。如果您确实应用了此设置，请注意 `reserveTokens: 4096` 会将回复长度限制在约 4k token，这可能会截断较长的文件生成或详细计划。
>
> **添加位置：** 将 `compaction` 代码块放置在您 `openclaw.json`（通常位于 `~/.openclaw/openclaw.json`）中的 `agents.defaults` 内部：
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> 您配置的其余部分（gateway、channels、models 等）保持不变，只需添加 `compaction` 键即可。
### （推荐）启用 Docker 沙盒

OpenClaw 可以将所有 Agent 文件和代码操作路由到一个隔离的 Docker 容器中，而不是直接在主机上运行。这样可以将任何意外操作的影响范围限制在沙盒内，使主机文件系统和网络不受影响。

构建一次沙盒镜像（必须已安装 Docker）：

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

运行以下命令，在 `~/.openclaw/openclaw.json` 中已有的 `agents.defaults` 块内添加 `sandbox` 键：

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

默认情况下，沙盒容器**没有网络访问权限**。有关绑定挂载和网络覆盖的信息，请参阅[沙盒参考文档](https://docs.openclaw.ai/gateway/sandboxing)。

> #### 故障排除：Docker 权限被拒绝
> 
> 如果在运行 Docker 命令时遇到 "permission denied"（权限被拒绝）：
> 
> **步骤 1：将您的用户添加到 docker 组**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **步骤 2：如果错误仍然存在，请应用永久修复方案**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> 然后**重启**您的系统。
> 
> **快速临时修复方案**（重启后会重置）：
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
## （推荐）通过 Firecrawl 服务集成 OpenClaw

[Firecrawl](https://docs.firecrawl.dev/introduction) 提供了一项自托管的网页爬取和内容提取服务，可以绕过这些挑战，充分释放 OpenClaw 自动化的全部潜力。

在此设置中，OpenClaw 作为一组由 Podman 管理的 Docker 容器运行。为了简化生命周期管理并实现自动启动，我们将 Firecrawl 注册为用户级 `systemd` 服务，用于编排底层的 Podman Compose 堆栈。这样一来，OpenClaw 就可以使用标准的 `systemctl --user` 命令来启动网关、停止服务以及验证 Firecrawl 服务，而无需直接与容器交互。

为简化流程，我们将整个过程分为四个步骤：

---

### 1. 注册系统服务
导航到 systemd 用户配置目录：
```bash
cd ~/.config/systemd/user
```
创建并打开一个名为 `firecrawl.service` 的新文件。
```bash
nano firecrawl.service
```
复制并粘贴以下配置：
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
此时，该服务已定义，但尚未在 `systemd` 中注册。
请确保文件名与您上面创建的文件名完全一致，然后运行：
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
如果成功，您应该会看到以下输出：

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` 包含指向配置为自动启动的服务的符号链接。

### 2. 配置 Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) 非常适合那些需要完全控制其抓取和数据处理环境的用户，但代价是需要投入更多的维护和配置工作。

首先克隆代码仓库：
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
在根目录 `/firecrawl` 下创建 `.env` 文件：
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. 使用 Podman Compose 部署 OpenClaw

在继续之前，请确保您已拉取最新的 OpenClaw Docker 镜像：
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
完成后，下载 OpenClaw Compose 文件 [openclaw-compose.yaml](assets/openclaw-compose.yaml)，并将其放置在根目录 `/firecrawl` 下：

> 按照 `WorkingDirectory=${HOME}/firecrawl` 中的指定，此约定对于 `systemd` 正确定位并启动该服务是必需的。

> 您始终可以根据需要添加更多 Firecrawl 服务来扩展该堆栈。可用服务的完整列表可在官方 [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) 中找到。

### 4. 通过 Firecrawl 启动 OpenClaw 服务

在将控制权交给 `systemd` 之前，请手动运行该堆栈以验证一切是否正常工作：
```bash
podman compose -f openclaw-compose.yaml up -d
```
如果一切配置正确，您应该会看到 OpenClaw 容器启动，并且命令行输出应该类似如下：
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

验证完成后，在继续之前先关闭该堆栈：
```bash
podman compose -f openclaw-compose.yaml down
```
在启动服务之前，您必须确保 `firecrawl` 目录及其 `.env` 文件已设置正确的所有权和权限。
这对于该服务在启动时写入您的凭据至关重要。
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
现在一切都已验证完毕，通过 `systemd` 启动该服务：
```bash
systemctl --user start firecrawl.service
```
[OpenClaw 操作](https://docs.openclaw.ai/) 可在交互式容器内访问，Web 仪表盘也可在同一主机和端口上通过 http://127.0.0.1:18789 访问。
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### 获取您的 `OPENCLAW_GATEWAY_TOKEN`

服务启动并运行后，您会发现主目录下（~/.openclaw）新创建了一个 `.openclaw` 目录。该目录默认是锁定的，因此您需要解锁它才能获取网关令牌。

1. 授予对该目录的访问权限：
```bash
sudo chmod 777 ~/.openclaw/
```
2. 读取您的网关令牌：
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
在输出中找到 `OPENCLAW_GATEWAY_TOKEN` 的值。

3. 在浏览器中打开网关仪表盘 http://127.0.0.1:18789。在提示进行身份验证时粘贴您的令牌。

要停止该服务，请运行：
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## 启动 OpenClaw 网关

网关是管理智能体循环并提供仪表盘服务的 OpenClaw 进程：

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

要打开仪表盘，请在网关仍在运行的情况下，于第二个终端中运行：

```bash
openclaw dashboard
```

由于网关绑定到本地回环地址，从同一台机器打开仪表盘时会自动完成身份验证，本地访问无需输入令牌或设备批准。此时你应该能看到 OpenClaw 仪表盘，并将你的 Lemonade 模型列为活动后端。

> 如果你已启用沙箱功能，可以通过在仪表盘中让智能体执行 `run hostname` 来验证。如果看到的是一个简短的容器 ID，而不是你机器的主机名，说明沙箱正在正常工作。

**恭喜，你已经从零搭建了一套完全本地化的 AI 智能体技术栈。**

> **需要网关令牌？** 运行 `openclaw dashboard --no-open` 可打印出内嵌令牌的仪表盘 URL（该命令还会尝试将其复制到剪贴板）。此外，该令牌也保存在 `~/.openclaw/openclaw.json` 的 `gateway.auth.token` 中。

**从其他设备访问仪表盘（通过 SSH 隧道）**

如果 OpenClaw 运行在远程机器上，你可以通过 SSH 隧道从本地机器访问其仪表盘。该隧道会转发网关端口（`18789`），使你的本地浏览器能够通过 `127.0.0.1` 与远程网关通信。

1. 在**本地机器**上，先连接一次远程机器并接受指纹提示，以便将主机添加到已知主机列表中：

   ```bash
   ssh user@<host-ip>
   ```

2. 仍在**本地机器**上，打开 SSH 隧道：

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **注意：** 输入密码后，终端不会显示任何输出，看起来像是卡住了。这是正常现象：`-N` 参数告诉 SSH 不要运行任何远程命令，它只是保持隧道开启。请让此终端保持运行状态。

3. 在**本地机器**上，打开浏览器并访问 `http://127.0.0.1:18789`。

4. 在**远程机器**上，打印网关令牌并将其粘贴到浏览器中登录：

   ```bash
   openclaw dashboard --no-open
   ```

   这将打印出内嵌令牌的仪表盘 URL；复制该令牌用于登录。（该令牌也保存在 `~/.openclaw/openclaw.json` 的 `gateway.auth.token` 中。）

> **批准远程设备：** 当你从另一台机器或手机打开仪表盘时，浏览器可能会显示一个请求 ID。在**远程机器**上，列出待批准的请求：
> ```bash
> openclaw devices list
> ```
> 然后批准匹配的请求：
> ```bash
> openclaw devices approve <requestId>
> ```
> 这仅在远程或次要设备访问时才需要；同一台机器的本地回环访问会自动完成身份验证。详情请参阅[远程访问](https://docs.openclaw.ai/gateway/remote)文档。

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## 可选：连接通信渠道

网关运行后，你可以从任何设备访问本地智能体。请根据你的设置选择合适的选项。OpenClaw 支持 [Discord](https://docs.openclaw.ai/channels/discord)、[Telegram](https://docs.openclaw.ai/channels/telegram) 及其他渠道，完整列表请参见 [docs.openclaw.ai](https://docs.openclaw.ai)。

---

### 选项 A：Discord

Discord 需要一个**你拥有管理员权限**的服务器才能添加机器人。如果你只是加入了服务器但并非所有者，请改用选项 B（Telegram）。

#### 创建 Discord 账号和服务器

如果你还没有 Discord 账号，请前往 [discord.com](https://discord.com) 注册。你还需要一个你拥有管理员权限的服务器，点击 Discord 侧边栏中的 **+** 图标并选择**创建自己的服务器**即可创建一个。私人服务器即可满足需求。

#### 创建 Discord 应用和机器人

1. 前往 [Discord 开发者门户](https://discord.com/developers/applications)，点击 **New Application**。为其命名（例如“openclaw-bot”）。
2. 在侧边栏中，点击 **Bot**。为机器人设置一个用户名。
3. 仍在 Bot 页面上，滚动到 **Privileged Gateway Intents**，并启用：
   - **Message Content Intent**（必需）
   - **Server Members Intent**（推荐）
4. 向上滚动并点击 **Reset Token** 以生成你的机器人令牌。复制该令牌。

#### 将机器人添加到你的服务器

1. 在侧边栏中，点击 **OAuth2/ URL Generator**。
2. 在 **Scopes** 下，启用 `bot` 和 `applications.commands`。
3. 在 **Bot Permissions** 下，启用：View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 复制生成的 URL，粘贴到浏览器中，选择你的服务器并确认。此时机器人应出现在你服务器的成员列表中。

#### 收集你的 ID

在 Discord 中启用开发者模式（**User Settings/ Advanced/ Developer Mode**），然后：
- 右键点击你的服务器图标：**Copy Server ID**
- 右键点击你自己的头像：**Copy User ID**

#### 允许来自服务器成员的私信

右键点击你的服务器图标/ **Privacy Settings**/ 打开 **Direct Messages** 开关。这样机器人才能向你发送私信，这是配对步骤所必需的。

#### 为 Discord 配置 OpenClaw

将你的机器人令牌存储为环境变量，然后创建一个补丁文件，用于启用 Discord、引用该令牌，并将你的服务器加入允许列表。请将 `<server_id>` 和 `<user_id>` 替换为上面收集到的 ID。

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **不要依赖让智能体来配置此项。** 启用沙箱后，智能体无法从沙箱内部写入 `~/.openclaw/openclaw.json`，请改用上面的 CLI 命令在宿主机上操作。

重启网关，使其读取新的渠道配置：

```bash
openclaw gateway run --bind loopback --port 18789
```

你应该会在几秒钟内看到网关输出中显示 `logged in to discord as <bot-name>`。
#### 关联你的 Discord 账号

在 Discord 中给机器人发送私信。它将回复一个简短的配对码。

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

在运行 OpenClaw 的机器上批准它：
```bash
openclaw pairing approve discord <CODE>
```

> 配对码在一小时后过期。

现在你可以直接从 Discord 与你的智能体聊天，并将任务分派给你的本地硬件。

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### 选项 B：Telegram

对大多数用户来说，Telegram 比 Discord 更简单，它不需要服务器，也不需要管理员权限。

#### 创建一个 Telegram 机器人

1. 打开 Telegram，向 **@BotFather** 发送消息。
2. 发送 `/newbot` 并按照提示操作。保存它提供给你的机器人令牌。

#### 为 Telegram 配置 OpenClaw

将令牌存储为环境变量：

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

将频道配置添加到 `~/.openclaw/openclaw.json`（或通过仪表盘打补丁）：

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

重启网关，然后在 Telegram 中向你的机器人发送任意消息。批准配对：

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

配对码在一小时后过期。现在你可以通过 Telegram 私信与你的智能体聊天。

---

## 后续步骤

既然你的智能体现在可以从你的手机接收命令并在你的本地机器上执行操作，以下是三个值得探索的方向：

1. **股市摘要器**：安排 OpenClaw 按固定间隔从金融 API 获取数据，用你的本地模型总结当天的行情走势，并通过你选择的渠道每天早上将摘要推送到你的手机。

2. **微调监控器**：通过 Telegram 或 Discord 远程启动一项训练任务，然后让智能体跟踪训练日志，并将定期的损失值、GPU 利用率和磁盘使用情况回报到你的手机。如果运行停滞或显存出现峰值，你可以立即知晓，而无需守在机器旁。

3. **搭配本地 VLM 的物联网**：将摄像头对准你的前门，在 Lemonade 上运行一个视觉模型，让 OpenClaw 按需或按触发条件分析画面。从你的手机上问一句"今天有包裹送到吗？"，就能从你自己的硬件上得到直接的答案。

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->