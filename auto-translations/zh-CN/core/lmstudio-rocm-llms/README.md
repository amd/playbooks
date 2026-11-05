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

## 概述

LM Studio 是一个功能强大的基于 GUI 的 [llama.cpp](https://github.com/ggml-org/llama.cpp) 封装工具，同时还提供了一个 [符合 OpenAI 规范的端点](https://lmstudio.ai/docs/developer/openai-compat)，用于本地模型服务。LM Studio 提供了一个简单而强大的界面，可轻松下载和部署模型。对于 AMD 用户，LM Studio 同时提供 Vulkan 和 AMD ROCm™ 软件后端（称为运行时）。

<!-- @device:halo_box -->
> **注意：** 部分 AMD Ryzen AI Halo 系统已预装本手册所需的模型，而其他系统则没有。这两种情况都受支持。当您进入 **下载模型** 部分时，请检查该模型是否已在 LM Studio 中可用——如果已有，您可以跳过下载步骤；如果没有，请按照相应步骤进行下载。
<!-- @device:end -->


## 您将学到什么
- 如何配置和使用 LM Studio 以充分利用您的本地硬件
- 在完全离线的环境中测试和管理 LLM
- 通过 OpenAI 兼容 API 提供模型服务，以支持自定义工作流和应用程序


<!-- @device:halo_box,halo,grgh,stx,krk -->
## 设置内存配置

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @os:linux -->
> **注意**：您可以通过 AMD Ryzen™ AI 开发者中心安装 VS Code。对于 LM Studio，请按照以下安装说明进行操作。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：如果尚未安装 VS Code 或 LM Studio，您可以通过 AMD Ryzen™ AI 开发者中心进行安装。
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->
<!-- @prereq:lmstudio -->

## 下载模型

<!-- @var:id=lms_model device=halo,grgh,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,grgh,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,grgh,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @prereq:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @prereq:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## 与 LLM 对话
了解如何完全在本地开始与达到 ChatGPT 级别的 LLM 进行对话。  

1. 打开 LMStudio。
2. 按下 `Ctrl + L` 打开模型加载器，选择 `Manually choose model load parameters`，然后点击 `${model_name}`
3. 确保已勾选“显示高级设置”。
4. 根据需要更改 `Context Length`（上下文长度）。更高的上下文长度意味着更大的模型内存占用，但会使用更多系统内存。本手册建议设置为 4096。
5. 确保 `GPU Offload` 设置为最大值，并且 `Flash Attention` 已开启（Cache Quantizations 可以保持关闭状态）
6. 勾选 `Remember settings`，然后点击 `Load Model`。
7. 如果未处于聊天窗口中，请按下 `Ctrl + 1` 或点击屏幕左上角的 👾 按钮。
8. 发送一条消息，开始与模型进行交互！

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,grgh,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **提示**：上下文长度是指模型的记忆能力。Flash Attention 可提升处理速度，同时降低内存占用。GPU Offload 可将计算负载转移到显卡上，从而加快响应速度。

## 通过兼容 OpenAI 的端点提供 LLM 服务

LM Studio 还以 LM Studio Server 的形式提供符合 OpenAI 规范的端点。这一点已经在 [此处](../playbooks/vscode-qwen3-coder) 的使用 Cline 的智能体编码工作流中进行了演示。另一个常见用例是通过向推理端点发送标准 HTTP 请求，将 LM Studio Server 与任何 Web 应用程序（React、Node.js、Python）连接起来。

要设置 LM Studio Server，请按照以下说明操作：

1. 在左侧，点击 `Developer` 选项卡（命令行图标）或按 `Ctrl + 2`，然后点击 `Server Settings`。  
2. （可选）：如果您希望通过局域网提供模型服务，请勾选 `Serve on Local Network`。如果您希望在网站中使用或在 VS Code 中进行大量调用，请勾选 `Enable CORS`。
3. 在左上角，点击 `Status` 前面的切换按钮，确保服务器正在运行。
4. 现在，符合 OpenAI 规范的端点将运行起来。该地址通常为 http://127.0.0.1:1234  
5. 如果尚未加载模型，您可以点击 `Load Model`，并按照前文所述步骤进行加载。

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->


现在，该模型将可以通过 LM Studio Server 端点进行访问，并支持包括以下在内的 OpenAI 端点：

| 端点 | 方法 | 文档 |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### 示例:对您的 Endpoint 执行 Ping 操作
刚刚创建了 OpenAI Compatible endpoint 后,让我们了解一下如何将其集成到 Python 开发环境(例如 VSCode)中,并将您的系统用作本地 API Provider。

1. 创建一个 Python 虚拟环境:

<!-- @os:linux -->
<!-- @device:halo_box -->
    在 Linux 系统上,在您选择的目录中打开终端,并按照以下命令创建一个 venv。
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,grgh,stx,krk,rx7900xt,rx9070xt,r9700 -->
**授予您的用户访问 GPU 设备的权限**(需要注销后重新登录才能生效):

```bash
sudo usermod -aG render,video $LOGNAME
```

    在 Linux 系统上,在您选择的目录中打开终端,并按照以下命令创建一个 venv。
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
    在 Windows 系统上,在您选择的目录中打开终端,并按照以下命令创建一个 venv。
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **提示**:Windows 用户在运行某些 Powershell 命令之前,可能需要修改其 PowerShell 执行策略(例如
    > 将其设置为 RemoteSigned 或 Unrestricted)。

<!-- @device:end -->

<!-- @device:halo,grgh,stx,krk,rx7900xt,rx9070xt,r9700 -->
    在 Windows 系统上,在您选择的目录中打开终端,并按照以下命令创建一个 venv。
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **提示**:Windows 用户在运行某些 Powershell 命令之前,可能需要修改其 PowerShell 执行策略(例如
    > 将其设置为 RemoteSigned 或 Unrestricted)。

<!-- @device:end -->
<!-- @os:end -->

2. 安装 OpenAI 软件包
    ```bash
    pip install openai
    ```

3. 运行以下脚本以对我们刚刚创建的 endpoint 执行 ping 操作。
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local LM Studio server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
   "temperature": 0,
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
   "temperature": 0,
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end --> 
<!-- @os:end -->

#### (可选):在 Runtime 之间切换

1. 在键盘上按下 `Ctrl + Shift + R`。或者,点击左侧的 `Discover` 选项卡(放大镜图标),然后在弹出窗口中点击 `Runtime`。
2. 随后您将看到 `Runtime Selections`,可以使用下拉菜单来更改 runtime。


## 后续步骤

- **自定义应用集成**:使用本地 OpenAI 兼容 API 集成您自己的 Python 脚本或应用程序。
- **高级前端**:将 Open WebUI 等功能强大的界面连接到您的服务器,以实现聊天记录和角色管理。

如需更多文档,请访问:https://lmstudio.ai/docs/developer