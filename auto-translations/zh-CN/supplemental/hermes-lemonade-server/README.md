<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 使用 Lemonade Server 在本地运行 Hermes Agent

## 概述

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) 是由 Nous Research 构建的一款可自我提升的 AI 智能体。它内置了学习循环，能够从经验中创建技能，在多个会话之间建立关于你的持久记忆，并可以代表你运行计划自动化任务。与简单的聊天助手不同，Hermes 会执行真实的操作：运行 shell 命令、写入文件、浏览网页，并将并行工作任务委派给子智能体。

[**Lemonade Server**](https://lemonade-server.ai/) 是为其提供支持的本地推理后端。它是一个开源服务器，可直接在你的 AMD 硬件上运行生成式 AI 模型，并通过行业标准的 OpenAI API 对外暴露这些模型。

两者结合在一起，构成了一个完全本地化的 AI 智能体技术栈：Lemonade 在你的 GPU 上处理模型推理，Hermes 则提供智能体循环、记忆、技能以及消息网关。

> **在继续之前：** Hermes Agent 是一个高度自主的 AI 智能体。让任何 AI 智能体访问你的系统都可能导致不可预测或非预期的结果。只有在你理解其中的风险，并且能够接受自主软件代表你执行操作的情况下，才应继续进行。

---

## 你将学到什么

完成本手册后，你将能够：

- **安装 Hermes Agent**，并将其指向 **Lemonade Server** 作为其 AI 后端。
- **（推荐）启用 Docker/Podman 沙箱**，将智能体的操作与主机隔离。
- **启动 Hermes 网关**，并确认你的智能体已准备就绪。
- **连接通信渠道**（Discord 或 Telegram），以便你可以在任何设备上与你的智能体聊天。

---

<!-- @device:halo_box,halo,stx,krk -->
## 设置内存配置

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

<!-- @os:linux -->
- 一台运行 **Ubuntu 24.04+** 或兼容的基于 Debian 的 Linux 发行版（支持 `apt-get`）的 PC
- 至少 **12 GB 的内存**（对于较大的模型，建议使用 64 GB 以上）
- **约 10–30 GB 的可用磁盘空间**，用于存储模型权重
- [Podman](https://podman.io/docs/installation)（可选，用于为 Hermes Agent 提供沙箱环境）
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- 一台运行 **Windows 10/11** 的 PC
- 至少 **12 GB 的内存**（对于较大的模型，建议使用 64 GB 以上）
- **约 10–30 GB 的可用磁盘空间**，用于存储模型权重
- Podman（可选，用于为 Hermes Agent 提供沙箱环境）。请在 WSL 内部安装：
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Halo Box 已预装 Podman，无需额外设置
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:hermes,lemonade-models-qwen3-35b-a3b,lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 拉取并加载推荐模型

本手册推荐使用的模型是 Unsloth 提供的 **Qwen3.6-35B-A3B-GGUF**，这是一个强大的 MoE 模型，拥有 263k token 的上下文窗口，非常适合智能体任务负载。该模型使用 UD-Q4_K_XL 量化。现在拉取该模型：

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

然后以较大的上下文窗口加载该模型，并将此设置保存以供以后运行使用：

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

该模型的默认上下文长度为 262,144 个 token。如果遇到内存不足（OOM）错误，可以考虑减小上下文窗口。

> **提示：禁用思考模式以获得更快的智能体响应：** Qwen3.6-35B-A3B 默认以思考模式运行，这会在每次响应前增加延迟。对于智能体循环来说，这种开销会迅速累积。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 仓库提供了一个现成的配置，可以禁用思考模式。要使用它，请下载该文件并导入：
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
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
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
model_id = "${hermes_model}"

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
  "model": "${hermes_model}",
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

我们在 WSL 内部运行 Hermes Agent，并将其连接到原生运行在 Windows 上的 Lemonade。这样可以为 Hermes 提供一个 Linux shell 环境，同时在 Windows 一侧保留 Lemonade 的 GPU 加速能力。

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

WSL2 运行在一个虚拟网络中。Windows 上的 Lemonade 绑定到 `127.0.0.1`，而 WSL 无法直接访问该地址。Windows 端口代理会将流量从 WSL 网关 IP 转发到 Windows 本地主机。

**查找你的 WSL 网关 IP**（在 WSL 内运行）：

```bash
ip route show default | awk '{print $3}' | head -1
```

**添加端口代理**（以管理员身份在 PowerShell 中运行，将 `<WSL-Gateway-IP>` 替换为你的 WSL 网关 IP）：

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**添加防火墙规则**（在同一个提升权限的 PowerShell 中）：

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**从 WSL 中验证**：

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

如果你在上一步中已经加载了 Qwen3.6-35B-A3B-GGUF 模型，你应该会看到列出已加载模型的 JSON 输出。

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

> `netsh portproxy` 规则在重启后仍然有效，但 WSL 网关 IP 在执行 `wsl --shutdown` 后可能会发生变化。如果重启后 WSL 无法访问 Lemonade，请获取更新后的网关 IP，并用这个新 IP 更新代理设置。

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## 安装 Hermes Agent

<!-- @os:windows -->
> 除非另有说明，否则请在你的 **WSL 终端** 中运行本节中的命令。
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

`--skip-setup` 标志会跳过交互式设置向导，以便你可以在下一步中手动配置模型后端。

重新加载你的 shell：

```bash
source ~/.bashrc
```

确认安装是否成功：

```bash
hermes --version
```

运行自检程序以检查所有依赖项：

```bash
hermes doctor
```

> **提示：** 如果安装后出现 `command not found`，请将 Hermes 添加到你的 PATH 中：
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> 要使此设置永久生效，请将上面这行内容添加到你的 `~/.bashrc` 或 `~/.zshrc` 文件中。

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## 配置 Hermes 以使用 Lemonade

Hermes 将其模型配置存储在 `~/.hermes/config.yaml` 中。您既可以使用交互式 `hermes model` 选择器，也可以直接编写配置。

### 方式一：交互式选择器

<!-- @os:windows -->
> 请在 **WSL 终端**中运行以下命令。
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

当出现提示时：

1. 选择 **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL（API 基础地址）：** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL（API 基础地址）：** 使用 WSL 网关 IP：在 WSL 内运行 `ip route show default | awk '{print $3}' | head -1` 获取该地址，然后输入 `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key（API 密钥）：** `lemonade`
4. **API compatibility mode（API 兼容模式）：** `1`（自动检测）
5. **Select model（选择模型）：** 从列表中选择 `Qwen3.6-35B-A3B-GGUF`
6. **Context length in tokens（上下文长度，以 token 计）：** `262144`
7. **Display name（显示名称）：** `local-lemonade`（或您喜欢的任何名称）

`hermes model` 会同时保存当前激活的模型选择，以及一个命名为 `custom_providers` 的条目，该条目会将上下文长度与端点一起存储。`~/.hermes/config.yaml` 中生成的结果如下所示：

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### 方式二：直接编写配置

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

在您的 WSL 终端中，获取 Windows 主机 IP 并写入配置：

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## （推荐）启用 Podman 沙箱

Hermes Agent 可以将所有代理的 shell 和文件操作通过一个隔离的容器进行转发，而不是直接在主机上运行。这将任何意外操作的影响范围限制在沙箱内，使主机文件系统和网络不受影响。

构建一个轻量级沙箱镜像：

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
进入您的 WSL 终端：

```powershell
wsl -d Ubuntu-24.04
```

然后，构建一个轻量级沙箱镜像：

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

然后配置 Hermes 使用 Podman 作为容器运行时，并设置终端后端：

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` 仍然是 `docker`。
> `HERMES_DOCKER_BINARY` 用于告知 Hermes 使用 Podman 作为运行时，而不是 Docker。

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Hermes 现在将启动一个持久化的沙箱容器，并将所有 `terminal` 和文件工具调用通过该容器转发。该容器与 Hermes 进程的生命周期共存，在所有工具调用之间被复用，并在 Hermes 退出时被销毁。

> **验证沙箱是否正常工作：** 启动 Hermes（`hermes`）并让它 `run hostname`——您应该会看到一个简短的容器 ID，而不是您机器的主机名。您也可以让它执行 `rm -rf <path-to-a-dummy-file/folder>`：Hermes 会确认删除操作，但该文件夹仍会保留在您的主机上。该命令是在容器隔离的 `$HOME` 中运行的，而不是您自己的 `$HOME`。

> **需要更强的隔离性？** Hermes 还提供了一个官方 Docker 镜像（`nousresearch/hermes-agent`），可将整个代理进程——网关、工具及其他全部内容——运行在容器内。有关设置详情，请参阅 [Hermes Docker 文档](https://hermes-agent.nousresearch.com/docs/user-guide/docker)。

---

<!-- @os:linux -->
## （推荐）Hermes 与 Firecrawl 服务集成

Hermes 可以使用其内置的网页工具浏览和提取网站内容。然而，许多现代网站使用机器人检测系统，会阻止简单的 HTTP 请求并返回质询页面，而非实际内容。因此，Hermes 可能无法可靠地从这些网站提取信息。

为克服此限制，[Firecrawl](https://docs.firecrawl.dev/introduction) 提供了一项可自行托管的网页抓取和内容提取服务，能够绕过这些质询，充分释放 Hermes 自动化的全部潜力。

在此设置中，Firecrawl 作为一组由 Podman 管理的 Docker 容器运行。为简化生命周期管理并实现自动启动，我们将 Firecrawl 注册为一个用户级的 `systemd` 服务，用于编排底层的 Podman Compose 技术栈。这样一来，Hermes 便可以使用标准的 `systemctl --user` 命令来启动、停止和验证 Firecrawl 服务，而无需直接与容器交互。

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
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
此时，该服务已被定义，但尚未在 `systemd` 中注册。
请确保文件名与您上面创建的文件名完全一致，然后运行：
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
如果成功，您应该会看到以下输出：

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` 包含指向已配置为自动启动的服务的符号链接。

### 2. 为您的服务配置 Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) 非常适合那些需要对其抓取和数据处理环境拥有完全控制权的用户，但其代价是需要额外的维护和配置工作。

首先克隆该仓库：
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
在根目录 `/firecrawl` 中创建 `.env`：
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> 将 `BULL_AUTH_KEY` 设置为一个强密钥，尤其是在任何可从不受信任网络访问的部署中。
### 3. 通过 Compose 部署 Hermes

在继续之前，请确保您已拉取最新的 Hermes Docker 镜像：
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
完成后，下载 Hermes Compose 文件 [hermes-compose.yaml](assets/hermes-compose.yaml) 并将其放置在根目录 `/firecrawl` 中：

> 这一约定是 `systemd` 能够按照 `WorkingDirectory=${HOME}/firecrawl` 中指定的方式正确定位并启动服务所必需的。

> 您可以随时通过添加其他 Firecrawl 服务来扩展此技术栈。完整的可用服务列表请参见官方 [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml)。

### 4. 通过 Firecrawl 启动 Hermes 服务

在将控制权交给 `systemd` 之前，请先手动运行该技术栈，验证一切是否正常工作：
```bash
podman compose -f hermes-compose.yaml up -d
```
如果一切配置正确，您应该会看到 Hermes 容器启动，命令行输出应类似于以下内容：
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

验证完成后，在继续之前先将技术栈停止：
```bash
podman compose -f hermes-compose.yaml down
```
现在一切都已验证完毕，通过 `systemd` 启动该服务：
```bash
systemctl --user start firecrawl.service
```
[Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) 可在交互式容器内访问，Web 控制面板可在同一主机和端口上通过 http://127.0.0.1:9119 访问。
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

要停止该服务，请运行：
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes 原生版

直接启动交互式 CLI 会话：

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**恭喜，您已经构建了一个完全本地化的 AI 代理技术栈。**

### Web 控制面板

Hermes 包含一个基于浏览器的 UI，用于管理配置、API 密钥、模型、会话、记忆和定时任务。在网关或 CLI 运行时打开第二个终端，并使用以下命令启动它：

```bash
hermes dashboard
```

这将启动一个本地服务器，并在浏览器中打开 `http://127.0.0.1:9119`。有关完整功能参考，请参阅 [控制面板文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)。
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## 可选：连接通信渠道

网关运行后，您可以从任何设备访问您的本地代理。Hermes 支持 [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord)、[Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) 等多种渠道

---

### Discord

Discord 需要一个您拥有**管理员权限**的服务器来添加机器人。如果您共用服务器但并非所有者，请改用 Telegram。

#### 创建 Discord 应用程序和机器人

1. 前往 [Discord 开发者门户](https://discord.com/developers/applications)，点击 **New Application**。为其命名（例如 "hermes-bot"）。
2. 在侧边栏中，点击 **Bot**。为机器人设置用户名。
3. 仍在 Bot 页面，向下滚动到 **Privileged Gateway Intents**，并启用：
   - **Message Content Intent**（必需）
   - **Server Members Intent**（推荐）
4. 向上滚动，点击 **Reset Token** 生成您的机器人令牌。将其复制下来。

#### 将机器人添加到您的服务器

1. 在侧边栏中，点击 **OAuth2 / URL Generator**。
2. 在 **Scopes** 下，启用 `bot` 和 `applications.commands`。
3. 在 **Bot Permissions** 下，启用：View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 复制生成的 URL，粘贴到浏览器中，选择您的服务器，然后确认。

#### 收集您的 ID 并允许私信

在 Discord 中启用开发者模式（**User Settings / Advanced / Developer Mode**），然后：
- 右键点击您的服务器图标：**Copy Server ID**
- 右键点击您自己的头像：**Copy User ID**

右键点击您的服务器图标 / **Privacy Settings** / 开启 **Direct Messages**。此步骤是配对所必需的。

#### 配置 Hermes 以使用 Discord

将以下内容添加到 `~/.hermes/.env`：

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

然后启动网关：

```bash
hermes gateway
```

机器人应在几秒钟内在 Discord 中上线。向其发送一条消息，可以是私信，也可以是它能看到的频道中的消息。

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### 创建 Telegram 机器人

1. 打开 Telegram，向 **@BotFather** 发送消息。
2. 发送 `/newbot` 并按照提示操作。保存它提供给您的机器人令牌。

#### 配置 Hermes 以使用 Telegram

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **不知道您的 Telegram 用户 ID？** 在 Telegram 中向 [@userinfobot](https://t.me/userinfobot) 发送消息，它会回复您的数字 ID。

然后启动网关：

```bash
hermes gateway
```

在 Telegram 中向您的机器人发送任意消息进行测试。您现在可以通过 Telegram 私信与您的代理聊天。有关 webhook 模式和高级选项，请参阅 [完整的 Telegram 设置指南](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)。

---

## 后续步骤

既然您的代理现在可以接收来自手机的命令并在您的本地机器上执行操作，以下是三个值得探索的方向：

1. **自动化研究摘要**：安排 Hermes 每天早上在网络上搜索您关心的主题，使用您的本地模型对研究结果进行总结，并通过 Telegram 或 Discord 将摘要推送到您的手机——所有这些都在您自己的硬件上运行，无需任何云端费用。

2. **按需代码审查**：让 Hermes 指向一个 GitHub 仓库，要求它审查开放的拉取请求，并让它将评论或摘要发回到您的聊天中。借助 Docker 终端后端，所有 git 操作都在沙盒内运行，保持主机环境整洁。

3. **本地文件助手**：授予 Hermes 对某个工作目录的访问权限，并要求它根据您从手机发出的需求，整理、重命名、总结或转换文件。由于 Docker 终端后端将所有写入操作限制在沙盒工作区内，意外的破坏性操作也能得到有效控制。