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

LM Studio 是一款基于 GUI 的强大封装工具,用于 [llama.cpp](https://github.com/ggml-org/llama.cpp),同时还提供了一个[兼容 OpenAI 的端点](https://lmstudio.ai/docs/developer/openai-compat),用于本地模型服务。LM Studio 提供了一个简单而强大的界面,便于轻松下载和部署模型。LM Studio 为 AMD 用户提供了 Vulkan 和 AMD ROCm™ 软件后端(称为运行时)。


## 您将学到什么
- 如何配置和使用 LM Studio 以充分利用您的本地硬件
- 在完全离线的环境中测试和管理大语言模型
- 通过兼容 OpenAI 的 API 提供模型服务,以支持自定义工作流和应用程序


<!-- @device:halo_box,halo,stx,krk -->
## 设置内存配置

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @os:linux -->
> **注意**:您可以通过 AMD Ryzen™ AI Developer Center 安装 VS Code。对于 LM Studio,请按照下面的安装说明进行操作。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**:如果尚未安装 VS Code 或 LM Studio,您可以从 AMD Ryzen™ AI Developer Center 进行安装。 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## 下载模型

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## 与大语言模型对话
了解如何完全在本地开始与达到 ChatGPT 水准的大语言模型进行对话。

1. 打开 LMStudio。
2. 按下 `Ctrl + L` 打开模型加载器,选择 `Manually choose model load parameters`,然后点击 `${model_name}`
3. 确保已勾选 "show advanced settings"。
4. 根据需要更改 `Context Length`。上下文长度越高,意味着模型占用的内存越多,系统内存使用量也越大。此实战指南推荐设置为 4096。
5. 确保 `GPU Offload` 设置为最大值,并且 `Flash Attention` 已开启(Cache Quantizations 可以保持关闭状态)
6. 勾选 `Remember settings` 并点击 `Load Model`。
7. 如果不在聊天窗口中,请按下 `Ctrl + 1` 或点击屏幕左上角的 👾 按钮。
8. 发送一条消息,开始与模型互动!

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
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y }
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
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **提示**:上下文长度是指模型的内存。Flash Attention 在降低内存使用量的同时提升处理速度。GPU Offload 会将计算负载转移到显卡上,以实现更快的响应速度。

## 通过兼容 OpenAI 的端点提供大语言模型服务

LM Studio 还以 LM Studio Server 的形式提供了一个兼容 OpenAI 的端点。这一点已经在使用 Cline 的智能体编码工作流中得到了演示,详见[此处](../playbooks/vscode-qwen3-coder)。另一个常见的使用场景是,通过向推理端点发送标准 HTTP 请求,将 LM Studio Server 连接到任何 Web 应用程序(React、Node.js、Python)。

要设置 LM Studio Server,请按照以下说明操作:

1. 在左侧,点击 `Developer` 选项卡(命令行图标)或按 `Ctrl + 2`,然后点击 `Server Settings`。
2. (可选):如果您想通过局域网提供模型服务,请勾选 `Serve on Local Network`。如果您想在网站中使用,或在 VS Code 中进行大量调用,请勾选 `Enable CORS`。
3. 在左上角,通过点击 `Status` 前面的切换按钮,确保服务器正在运行。
4. 此时,一个兼容 OpenAI 的端点将开始运行。该地址通常位于 http://127.0.0.1:1234
5. 如果尚未加载模型,您可以点击 `Load Model` 并按照前面提到的步骤加载模型。

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


现在,该模型可以通过 LM Studio Server 端点进行访问,并将支持包括以下在内的 OpenAI 端点:

| 端点 | 方法 | 文档 |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### 示例：Ping 你的端点
刚刚创建了 OpenAI 兼容端点后，让我们来看看如何将其集成到 Python 开发者环境（例如 VSCode）中，并将你的系统用作本地 API 提供者。

1. 创建 Python 虚拟环境：

<!-- @os:linux -->
<!-- @device:halo_box -->
    在 Linux 上，在你选择的目录中打开一个终端，并按照以下命令创建 venv。
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**授予你的用户访问 GPU 设备的权限**（需要注销并重新登录才能生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

    在 Linux 上，在你选择的目录中打开一个终端，并按照以下命令创建 venv。
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
    在 Windows 上，在你选择的目录中打开一个终端，并按照以下命令创建 venv。
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **提示**：Windows 用户在运行某些 Powershell 命令之前，可能需要修改其 PowerShell 执行策略（例如
    > 将其设置为 RemoteSigned 或 Unrestricted）。

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    在 Windows 上，在你选择的目录中打开一个终端，并按照以下命令创建 venv。
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **提示**：Windows 用户在运行某些 Powershell 命令之前，可能需要修改其 PowerShell 执行策略（例如
    > 将其设置为 RemoteSigned 或 Unrestricted）。

<!-- @device:end -->
<!-- @os:end -->

2. 安装 OpenAI 包
    ```bash
    pip install openai
    ```

3. 运行以下脚本来 ping 我们刚刚创建的端点。
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

#### （可选）：切换运行时

1. 在键盘上按 `Ctrl + Shift + R`。或者，点击左侧的 `Discover` 标签（放大镜图标），然后在弹出窗口中点击 `Runtime`。
2. 随后你应该会看到 `Runtime Selections`，可以使用下拉菜单来更改运行时。


## 后续步骤

- **自定义应用集成**：使用本地 OpenAI 兼容 API 将你自己的 Python 脚本或应用程序集成进来。
- **高级前端**：将 Open WebUI 等强大的界面连接到你的服务器，以实现聊天记录和角色管理。

更多文档请访问：https://lmstudio.ai/docs/developer