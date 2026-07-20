<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# 使用 Lemonade Server 作为后端运行 OpenClaw

## 概述

[**OpenClaw**](https://openclaw.ai/) 是一个自主 AI 智能体，能够代表你编写和运行代码、管理文件，并处理复杂的多步骤任务。与只能回答问题的聊天助手不同，OpenClaw 会在你的系统上执行真实的操作，这意味着它需要一个快速、强大的 AI 后端来跟上其高要求的智能体循环。

[**Lemonade Server**](https://lemonade-server.ai/) 正是这样的后端。它是一个开源的本地推理服务器，可以直接在你的硬件上运行 GenAI 模型，并通过业界标准的 OpenAI API 对外提供服务。

两者结合，构成了一套完全本地化的 AI 智能体技术栈：Lemonade 负责模型推理，而 OpenClaw 提供智能体循环，将模型输出转化为真实的操作。

> **在继续之前：** OpenClaw 是一个高度自主的 AI 智能体。让任何 AI 智能体访问你的系统都可能导致不可预测或非预期的结果。请仅在你理解相关风险并愿意让自主软件代表你行事的情况下继续操作。

---

## 你将学到什么

完成本操作指南后，你将能够：

- 了解 **Lemonade Server**
- **安装 OpenClaw**，并**将其指向 Lemonade Server**作为其 AI 后端。
- **启动 OpenClaw 网关**，并确认你的智能体已准备就绪。
- **连接通信渠道**（Discord 或 Telegram），以便你可以从任何设备与你的智能体聊天。

---

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

<!-- @os:linux -->
- 一台运行 **Ubuntu 24.04+** 或兼容的、基于 Debian 且具备 `apt-get` 的 Linux 发行版的电脑
- 至少 **12 GB 内存**（推荐 64 GB 以上以支持更大的模型）
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)（可选，用于对 OpenClaw 进行沙盒隔离）

- 用于模型权重的**约 10–30 GB 可用磁盘空间**
<!-- @os:end -->
<!-- @os:windows -->
- 一台运行 **Windows 10/11** 的电脑
- 至少 **12 GB 内存**（推荐 64 GB 以上以支持更大的模型）
- 用于模型权重的**约 10–30 GB 可用磁盘空间**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)（可选，用于对 OpenClaw 进行沙盒隔离）
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

本操作指南推荐的模型是 Unsloth 提供的 **Qwen3.6-35B-A3B-GGUF**，这是一款出色的 MoE 模型，具有 263k token 的上下文窗口，非常适合智能体工作负载。该模型使用 UD-Q4_K_XL 量化。现在拉取该模型：

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

然后以较大的上下文窗口加载它，并保存该设置以供以后运行使用：

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

该模型的默认上下文长度为 262,144 个 token。如果遇到内存不足（OOM）错误，可以考虑减小上下文窗口。不过，由于 Qwen3.6 依赖扩展上下文来处理复杂任务，我们建议至少保持 128K token 的上下文长度，以保留其思考能力。

> **提示：禁用思考模式以获得更快的智能体响应：** Qwen3.6-35B-A3B 默认以思考模式运行，这会在每次响应前增加延迟。对于智能体循环来说，这种开销会迅速累积。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 仓库提供了一个可直接使用的、禁用思考模式的配置文件。要使用它，请下载该文件并导入：
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

我们在 WSL 中运行 OpenClaw（推荐做法），并将其连接到在 Windows 上原生运行的 Lemonade。这样可以为 OpenClaw 提供一个 Linux Shell 环境，同时在 Windows 一侧保留 Lemonade 的 GPU 加速能力。

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

重启 WSL：

```powershell
wsl --shutdown
wsl
```

### 将 Lemonade 从 Windows 桥接到 WSL

WSL2 运行在一个虚拟网络中。Windows 上的 Lemonade 绑定到 `127.0.0.1`，而 WSL 无法直接访问该地址。可以通过 Windows 端口代理，将流量从 WSL 网关 IP 转发到 Windows 本地地址。

**查找你的 WSL 网关 IP**（在 WSL 中运行）：

```bash
ip route show default | awk '{print $3}' | head -1
```

**添加端口代理**（以管理员身份在 PowerShell 中运行，将 `<WSL-Gateway-IP>` 替换为你的 WSL 网关 IP）：

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**添加防火墙规则**（在同一个提升权限的 PowerShell 中运行）：

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**从 WSL 中验证**：

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

如果你在上一步中已经加载了 Qwen3.6-35B-A3B-GGUF 模型，应该会看到如下的 JSON 输出：

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

> `netsh portproxy` 规则在重启后依然有效，但 WSL 网关 IP 可能会在执行 `wsl --shutdown` 后发生变化。如果重启后 WSL 无法访问 Lemonade，请获取更新后的网关 IP，并使用该新 IP 更新代理设置。

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

## 安装并配置 OpenClaw

### 安装 OpenClaw
<!-- @os:windows -->
> 请在你的 **WSL 终端**中运行本节中的命令。
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` 标志会跳过交互式设置向导，你将在下一步中手动配置模型后端，这样可以精确控制所使用的模型和服务器。

打开一个新终端并确认安装情况：

```bash
openclaw --version
```

> **提示：** 如果安装后出现 `command not found`，请将 npm 的全局 bin 目录添加到你的 PATH 中：
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> 若要使此设置永久生效，请将上面这行内容添加到你的 `~/.bashrc` 或 `~/.zshrc` 文件中。

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

运行 OpenClaw 的非交互式引导。
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

> **OpenClaw 上下文窗口大小设置：** 当 `contextTokens > contextWindow − reserveTokens` 时，OpenClaw 的压缩机制会被触发。默认的 `reserveTokensFloor` 为 20,000 个 token，这是一个下限值,当其低于 `reserveTokens` 时会覆盖后者,因此任何低于约 37k 的模型上下文都会触发无限压缩循环。在配置中设置一个较低的保留值并禁用该下限,这样只需一次设置即可应用于每个模型,无需针对每个模型单独调整：
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` 是一个*下限*（最小保护值），而非保留值本身,仅设置该下限不会产生任何效果。`reserveTokensFloor: 0` 会禁用该保护机制,从而使较低的 `reserveTokens` 值生效。
>
> **何时应用此配置：** 如果你的模型的有效上下文窗口低于约 37k（无论是因为模型本身较小，例如 8k、16k、32k，还是因为你有意将其限制为更低的值，例如加载了一个 128k 模型但在 Lemonade 中将上下文设置为 16k），请使用此配置。否则，OpenClaw 在启动时会进入无限压缩循环。
>
> **大上下文模型使用完整上下文时：** 你可以完全跳过此配置。默认设置即可正常工作，压缩机制会在窗口填满之前及时启动，模型也有充足的空间生成较长的回复。如果你确实应用了此配置，请注意 `reserveTokens: 4096` 会将回复长度限制在约 4k token，这可能会截断较长的文件生成或详细计划。
>
> **在何处添加此配置：** 将 `compaction` 代码块放置在 `openclaw.json`（通常位于 `~/.openclaw/openclaw.json`）中的 `agents.defaults` 内部：
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
> 配置的其余部分（gateway、channels、models 等）保持不变，只需添加 `compaction` 键即可。

### （推荐）启用 Docker 沙盒

OpenClaw 可以将所有代理文件和代码操作路由到一个隔离的 Docker 容器中，而不是直接在主机上运行。这样可以将任何意外操作的影响范围限制在沙盒内，使你的主机文件系统和网络不受影响。

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

运行以下命令，在 `~/.openclaw/openclaw.json` 中现有的 `agents.defaults` 代码块内添加 `sandbox` 键：

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

沙盒容器默认**没有网络访问权限**。有关绑定挂载和网络覆盖设置，请参阅[沙盒参考文档](https://docs.openclaw.ai/gateway/sandboxing)。

> #### 故障排查：Docker 权限被拒绝
> 
> 如果在运行 Docker 命令时出现“权限被拒绝”的提示：
> 
> **步骤 1：将你的用户添加到 docker 组**
> 
> ```bash
> sudo groupadd docker                    # 如果需要,创建该组
> sudo usermod -aG docker $USER           # 将自己添加到该组
> newgrp docker                           # 使更改生效
> docker run hello-world                  # 测试
> ```
> 
> **步骤 2：如果问题仍然存在，请应用永久修复方案**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> 然后**重启**你的系统。
> 
> **快速临时修复方案**（重启后失效）：
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

### 启动 OpenClaw 网关

网关是 OpenClaw 用于管理代理循环并提供仪表盘服务的进程：

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

要打开仪表盘，请在网关仍在运行的情况下，在第二个终端中运行以下命令：

```bash
openclaw dashboard
```

由于网关绑定到回环地址，因此从同一台机器打开仪表盘时会自动完成身份验证，本地访问无需输入令牌或进行设备批准。你应该会看到 OpenClaw 仪表盘，其中列出了你的 Lemonade 模型作为活动后端。

> 如果你已启用沙盒功能，可以通过在仪表盘中让代理执行 `run hostname` 来验证其是否正常工作。如果显示的是一个简短的容器 ID，而不是你机器的主机名，则说明沙盒正在正常工作。

**恭喜，你已经从零开始构建了一个完全本地化的 AI 代理技术栈。**

> **需要网关令牌？** 运行 `openclaw dashboard --no-open` 即可打印出包含令牌的仪表盘 URL（该命令还会尝试将其复制到剪贴板）。或者，你也可以在 `~/.openclaw/openclaw.json` 中的 `gateway.auth.token` 处找到该令牌。
>
> **批准远程设备：** 当你从第二台机器或手机打开仪表盘时，浏览器会显示一个请求 ID。回到运行网关的机器上，运行：
> ```bash
> openclaw devices approve <requestId>
> ```
> 只有远程或次要设备才需要执行此操作，来自同一台机器的回环访问会自动完成身份验证。

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## 可选：连接通信渠道

网关运行后，你可以从任何设备访问本地代理。请选择适合你使用场景的选项。OpenClaw 支持 [Discord](https://docs.openclaw.ai/channels/discord)、[Telegram](https://docs.openclaw.ai/channels/telegram) 以及其他渠道，完整列表请参阅 [docs.openclaw.ai](https://docs.openclaw.ai)。

---

### 选项 A：Discord

Discord 需要一个**你拥有管理员权限**的服务器才能添加机器人。如果你与他人共用服务器但并非所有者，请改用选项 B（Telegram）。
#### 创建 Discord 账号和服务器

如果你还没有 Discord 账号，请在 [discord.com](https://discord.com) 注册。你还需要一个你拥有管理员权限的服务器，点击 Discord 侧边栏中的 **+** 图标并选择 **Create My Own** 即可创建一个。私有服务器即可满足需求。

#### 创建 Discord 应用和机器人

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)，点击 **New Application**。为其命名（例如“openclaw-bot”）。
2. 在侧边栏中点击 **Bot**。为机器人设置一个用户名。
3. 仍在 Bot 页面上，滚动到 **Privileged Gateway Intents**，并启用：
   - **Message Content Intent**（必需）
   - **Server Members Intent**（推荐）
4. 向上滚动，点击 **Reset Token** 生成你的机器人令牌。复制它。

#### 将机器人添加到你的服务器

1. 在侧边栏中点击 **OAuth2/ URL Generator**。
2. 在 **Scopes** 下，启用 `bot` 和 `applications.commands`。
3. 在 **Bot Permissions** 下，启用：View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 复制生成的 URL，粘贴到浏览器中，选择你的服务器并确认。此时机器人应该已出现在你服务器的成员列表中。

#### 收集你的 ID

在 Discord 中启用开发者模式（**User Settings/ Advanced/ Developer Mode**），然后：
- 右键点击你的服务器图标：**Copy Server ID**
- 右键点击你自己的头像：**Copy User ID**

#### 允许服务器成员向你发送私信

右键点击你的服务器图标/ **Privacy Settings**/ 打开 **Direct Messages** 开关。这样机器人才能向你发送私信，这是配对步骤所必需的。

#### 为 Discord 配置 OpenClaw

将你的机器人令牌存储为环境变量，然后创建一个补丁文件，用来启用 Discord、引用该令牌，并将你的服务器加入白名单。将 `<server_id>` 和 `<user_id>` 替换为上面收集到的 ID。

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

> **不要依赖让智能体（agent）来配置此项。** 启用沙箱后，智能体无法从沙箱内部写入 `~/.openclaw/openclaw.json`，请改为在主机上使用上述 CLI 命令。

重启网关，使其加载新的频道配置：

```bash
openclaw gateway run --bind loopback --port 18789
```

在几秒钟内，你应该会在网关输出中看到 `logged in to discord as <bot-name>`。

#### 配对你的 Discord 账号

在 Discord 中给机器人发送私信。它会回复一个简短的配对码。

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

在运行 OpenClaw 的机器上批准该配对：
```bash
openclaw pairing approve discord <CODE>
```

> 配对码将在一小时后过期。

现在你可以直接从 Discord 与你的智能体聊天，并将任务分配给你的本地硬件。

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### 选项 B：Telegram

对大多数用户来说，Telegram 比 Discord 更简单，它不需要服务器，也不需要管理员权限。

#### 创建一个 Telegram 机器人

1. 打开 Telegram 并给 **@BotFather** 发消息。
2. 发送 `/newbot` 并按提示操作。保存它给你的机器人令牌。

#### 为 Telegram 配置 OpenClaw

将令牌存储为环境变量：

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

将频道配置添加到 `~/.openclaw/openclaw.json`（或通过仪表盘对其打补丁）：

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

重启网关，然后在 Telegram 中给你的机器人发送任意消息。批准该配对：

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

配对码将在一小时后过期。现在你可以通过 Telegram 私信与你的智能体聊天。

---

## 后续步骤

既然你的智能体现在可以从你的手机接收命令并在你的本地机器上执行操作，以下有三个值得探索的方向：

1. **股市摘要生成器**：安排 OpenClaw 按固定时间间隔从金融 API 获取数据，用你的本地模型总结当天的行情变动，并通过你选择的频道每天早上将摘要推送到你的手机上。

2. **微调监控器**：通过 Telegram 或 Discord 远程启动一个训练任务，然后让智能体持续跟踪训练日志，并定期将损失值、GPU 利用率和磁盘使用情况报告回你的手机。如果训练卡住或显存（VRAM）出现峰值，你无需守在机器旁就能立即知晓。

3. **搭配本地视觉语言模型（VLM）的物联网应用**：将摄像头对准你的前门，在 Lemonade 上运行一个视觉模型，让 OpenClaw 按需或在触发条件下分析画面帧。从你的手机上问“今天有包裹送达吗？”，即可从你自己的硬件上得到直接的回答。