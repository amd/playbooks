<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概要

GAIA エージェントは、ローカル LLM を使用して推論を行い、定義したツールを呼び出す AI アシスタントです。アクションを実行できるチャットボットのようなものです。クラウド API を一切使用せず、データがマシンから外部に出ることもなく、API キーも不要で、**完全にローカル**で動作します。

このプレイブックでは、システムの RAM、GPU、NPU を検出し、ローカルモデルカタログに問い合わせ、お使いのマシンで実行可能な LLM を推奨する Hardware Advisor Agent を構築します。これは GAIA Agent SDK への実践的な入門であり、すぐに役立つ成果物を生み出します。

## 学習内容

- カスタムツールを備えた GAIA エージェントの作成方法
- LemonadeClient SDK を使用したシステム情報とモデルカタログの問い合わせ
- プラットフォーム固有の GPU/NPU 検出(Windows PowerShell と Linux lspci)
- 70% ルールを用いたメモリベースのモデルサイジング
- 自然言語によるハードウェア問い合わせのためのインタラクティブ CLI の構築

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する
> **注**: VS Code がインストールされていない場合は、Ryzen AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件のインストール

<!-- @os:windows -->
<!-- @test:id=python-env-check-windows timeout=30 hidden=True -->
```powershell
python --version
where.exe python
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux -->
<!-- @test:id=python-env-check-linux timeout=30 hidden=True -->
```bash
set -euo pipefail
python3 --version
which python3
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade -->
<!-- @require:gaia -->
<!-- @prereq:lemonade-models-qwen3-coder-30b -->

## はじめに

まずは完成版のエージェントを実際に動かし、何を構築しているのかを確認しましょう。その後、コードを一つずつ順を追って説明していきます。

### 事前構築済みのサンプルを実行する

このプレイブックには、完成版の [hardware_advisor_agent.py](assets/hardware_advisor_agent.py) が含まれています。任意のディレクトリにダウンロードして実行し、完成したエージェントの動作を確認してください。

```bash
python hardware_advisor_agent.py
```

<!-- @test:id=gaia-verify-assets timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["hardware_advisor_agent.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)

print("PASS: hardware_advisor_agent.py exists")

with open("hardware_advisor_agent.py", "r", encoding="utf-8") as f:
    ast.parse(f.read())

print("PASS: hardware_advisor_agent.py has valid syntax")
```
<!-- @test:end --> 

**試しに質問してみてください:** 「どのサイズの LLM を実行できますか?」

**期待される出力:**

```
============================================================
Hardware Advisor Agent
============================================================

Hi! I can help you figure out what size LLM your system can run.

Agent ready!

You: What size LLM can I run?

Agent: Great news! With 32 GB RAM and a 24 GB GPU, you can run:
- 30B parameter models (like Qwen3-Coder-30B)
- Most 7B-14B models comfortably
- NPU acceleration available for smaller models
```

**おめでとうございます** - エージェントを構築できました!

プレイブックの残りの部分では、スクリプトの各部分がどのように機能するかを説明し、基礎から理解できるようにしていきます。
<!-- @os:windows -->
<!-- @test:id=gaia-lemonadeclient-smoke-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"
try {
  $health = $null
  for ($i=0; $i -lt 120; $i++) {
    $health = curl.exe -sS --fail-with-body --max-time 2 http://127.0.0.1:13305/api/v1/health
    if ($health) { break }
    Start-Sleep -Seconds 1
  }
  if (-not $health) { throw "Lemonade server not ready on http://127.0.0.1:13305/api/v1/health" }

  $script = @'
from gaia.llm.lemonade_client import LemonadeClient

client = LemonadeClient(host="localhost", port=13305, keep_alive=True)

info = client.get_system_info()
assert isinstance(info, dict)
assert "Physical Memory" in info or "devices" in info

models = client.list_models(show_all=True)
assert isinstance(models, dict)
assert "data" in models

model_info = client.get_model_info("Qwen3-Coder-30B-A3B-Instruct-GGUF")
assert isinstance(model_info, dict)
assert model_info.get("id") == "Qwen3-Coder-30B-A3B-Instruct-GGUF"

print("OK: LemonadeClient works")
'@
  Set-Content -Path gaia_lemonadeclient_smoke.py -Value $script
  python gaia_lemonadeclient_smoke.py
} finally {
  Remove-Item gaia_lemonadeclient_smoke.py -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:windows -->
<!-- @test:id=gaia-hardware-advisor-smoke-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

$health = $null
for ($i=0; $i -lt 120; $i++) {
    $health = curl.exe -sS --fail-with-body --max-time 2 http://127.0.0.1:13305/api/v1/health
    if ($health) { break }
    Start-Sleep -Seconds 1
}

if (-not $health) { throw "Lemonade server not ready on http://127.0.0.1:13305/api/v1/health" }
Write-Host "OK: Lemonade server ready on http://127.0.0.1:13305/api/v1/health"

$output = cmd /c "echo quit| python hardware_advisor_agent.py"

if (-not ($output -match "Hardware Advisor Agent" -or $output -match "Agent ready!" -or $output -match "Goodbye!")) { throw "Did not see expected output from hardware_advisor_agent.py" }
Write-Host "OK: hardware_advisor_agent.py started successfully"

```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux -->
<!-- @test:id=gaia-lemonadeclient-smoke-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

health=""
for i in $(seq 1 120); do
  health="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/health || true)"
  if [ -n "$health" ]; then
    break
  fi
  sleep 1
done

if [ -z "$health" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305/api/v1/health"
  exit 1
fi
echo "OK: Lemonade server is responding on http://127.0.0.1:13305/api/v1/health"

cat >/tmp/gaia_lemonadeclient_smoke.py <<'PY'
from gaia.llm.lemonade_client import LemonadeClient

client = LemonadeClient(host="localhost", port=13305, keep_alive=True)

info = client.get_system_info()
assert isinstance(info, dict)
assert "Physical Memory" in info or "devices" in info

models = client.list_models(show_all=True)
assert isinstance(models, dict)
assert "data" in models

model_info = client.get_model_info("Qwen3-Coder-30B-A3B-Instruct-GGUF")
assert isinstance(model_info, dict)
assert model_info.get("id") == "Qwen3-Coder-30B-A3B-Instruct-GGUF"

print("OK: LemonadeClient works")
PY

python3 /tmp/gaia_lemonadeclient_smoke.py
rm -f /tmp/gaia_lemonadeclient_smoke.py
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux -->
<!-- @test:id=gaia-hardware-advisor-smoke-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

for i in $(seq 1 120); do
  health="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/health || true)"
  if [ -n "$health" ]; then
    break
  fi
  sleep 1
done

if [ -z "$health" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305/api/v1/health"
  exit 1
fi
echo "OK: Lemonade server is responding on http://127.0.0.1:13305/api/v1/health"

printf 'quit' | python3 hardware_advisor_agent.py >/tmp/gaia_agent_output.txt

grep -q "Hardware Advisor Agent" /tmp/gaia_agent_output.txt
echo "OK: hardware_advisor_agent.py started successfully"
```
<!-- @test:end --> 
<!-- @os:end --> 


## アーキテクチャを理解する

Hardware Advisor Agent は、次の 3 つのコンポーネントを組み合わせています。

- **LemonadeClient SDK** — システム情報およびモデルカタログ API
- **プラットフォーム固有の検出** — GPU 情報取得のための Windows PowerShell / Linux lspci
- **メモリ計算** — 安全なモデルサイジングのための 70% ルール

データは次の順序で流れます。ユーザーの質問 → エージェントがツールを選択 → ツールが LemonadeClient と OS 検出を呼び出す → エージェントが結果を統合して推奨事項を生成する。

### LemonadeClient SDK

LemonadeClient は、システム検出、NPU/GPU の利用可否、モデルカタログの問い合わせのための統一 API を提供します。

**インポートと初期化:**

```python
from gaia.llm.lemonade_client import LemonadeClient

client = LemonadeClient(keep_alive=True)
```

**`get_system_info()`** — OS、CPU、RAM、デバイスの利用可否を返します。

```python
info = client.get_system_info()
```

<!-- @os:windows -->

```python
# Returns:
{
    "OS Version": "Windows 11 Pro",
    "Processor": "AMD Ryzen 9 7950X",
    "Physical Memory": "32.0 GB",
    "devices": {
        "cpu": {"name": "...", "available": True},
        "amd_igpu": {"name": "...", "memory": 8192, "available": True},
        "amd_npu": {"name": "Ryzen AI NPU", "available": True}
    }
}
```

<!-- @os:end -->

<!-- @os:linux -->

```python
# Returns:
{
    "OS Version": "Ubuntu 24.04 LTS",
    "Processor": "AMD Ryzen 9 7950X",
    "Physical Memory": "32.0 GB",
    "devices": {
        "cpu": {"name": "...", "available": True},
        "amd_igpu": {"name": "...", "memory": 8192, "available": True},
        "amd_npu": {"name": "Not detected", "available": False}
    }
}
```

<!-- @os:end -->

**`list_models(show_all=True)`** — 完全なモデルカタログを返します。

```python
response = client.list_models(show_all=True)

# Returns:
{
    "data": [
        {
            "id": "Qwen3-0.6B-GGUF",
            "name": "Qwen3 0.6B",
            "downloaded": True,
            "labels": ["hot", "cpu", "small"]
        }
    ]
}
```

**`get_model_info(model_id)`** — 特定のモデルのサイズ見積もりを返します。

```python
model_info = client.get_model_info("Qwen3-Coder-30B-A3B-Instruct-GGUF")

# Returns:
{
    "id": "Qwen3-Coder-30B-A3B-Instruct-GGUF",
    "name": "Qwen3 Coder 30B",
    "size_gb": 18.5,
    "downloaded": False
}
```

### プラットフォーム固有の GPU 検出

このエージェントは GPU 検出に PyTorch ではなく OS ネイティブのコマンドを使用します。これにより GPU ドライバーがインストールされていなくても動作し、(CUDA 対応のものだけでなく)すべての GPU を検出でき、重いライブラリのインポートを回避できます。

<!-- @os:windows -->

Windows では、エージェントは PowerShell を使用して WMI に問い合わせます。

```python
ps_command = (
    "Get-WmiObject Win32_VideoController | "
    "Select-Object Name,AdapterRAM | "
    "ConvertTo-Csv -NoTypeInformation"
)
result = subprocess.run(
    ["powershell", "-Command", ps_command],
    capture_output=True, text=True, timeout=5
)
# Parse CSV output for GPU name and VRAM
```

<!-- @os:end -->

<!-- @os:linux -->

Linux では、エージェントは lspci を使用します。

```python
result = subprocess.run(
    ["lspci"], capture_output=True, text=True, timeout=5
)
# Parse output for "VGA compatible controller" lines
# Note: Memory not available via lspci
```

<!-- @os:end -->

### 70% メモリルール

> **ルール:** モデルサイズは、推論処理(KV キャッシュ、バッチ処理バッファ、実行時のメモリスパイク)のために 30% のオーバーヘッドを残せるよう、利用可能な RAM の 70% 未満である必要があります。

```
System: 32 GB RAM
Max safe model size: 32 x 0.7 = 22.4 GB
30B model (~18.5 GB): Fits safely
70B model (~42 GB):   Too large
```

## エージェントを一歩ずつコーディングする(任意)

`hardware_advisor_agent.py` という**1 つのファイル**を作成し、段階的に機能を追加していきます。各ステップは前のステップの上に構築されます。

### ステップ 1: エージェントの骨格

まずは最小限のエージェント構造から始めます — クラスと基本的なシステムプロンプトのみです。エージェントにはまだツールがありません。

```python
from gaia import Agent
from gaia.llm.lemonade_client import LemonadeClient


class HardwareAdvisorAgent(Agent):
    """Agent that advises on LLM capabilities based on your hardware."""

    def __init__(self, **kwargs):
        self.client = LemonadeClient(keep_alive=True)
        super().__init__(**kwargs)

    def _get_system_prompt(self) -> str:
        return "You are a hardware advisor for running local LLMs on AMD systems."

    def _register_tools(self):
        # Tools will be added in the next steps
        pass


if __name__ == "__main__":
    agent = HardwareAdvisorAgent()
    print("Agent created successfully!")
```

実行して確認します。

```bash
python hardware_advisor_agent.py
```

期待される出力:

```
Agent created successfully!
```

---

### ステップ 2: GPU とハードウェアの検出

`_get_gpu_info()` ヘルパーメソッドと `get_hardware_info()` ツールを追加します。これによりエージェントがインタラクティブになり、システムの仕様について問い合わせできるようになります。

ファイル先頭の**インポートを更新します**。

```python
from typing import Any, Dict

from gaia import Agent, tool
from gaia.llm.lemonade_client import LemonadeClient
```

`_get_system_prompt()` メソッドの後に、**`_get_gpu_info()` ヘルパーを追加します**。

```python
def _get_gpu_info(self) -> Dict[str, Any]:
    """Detect GPU using OS-native commands."""
    import platform
    import subprocess

    system = platform.system()

    try:
        if system == "Windows":
            ps_command = (
                "Get-WmiObject Win32_VideoController | "
                "Select-Object Name,AdapterRAM | "
                "ConvertTo-Csv -NoTypeInformation"
            )
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = [
                    l.strip()
                    for l in result.stdout.strip().split("\n")
                    if l.strip()
                ]
                # Skip virtual/remote adapters that aren't real GPUs
                skip_keywords = [
                    "microsoft remote display",
                    "microsoft basic display",
                    "remote desktop",
                ]
                # Collect all valid GPUs and pick the one with the most VRAM
                candidates = []
                for line in lines[1:]:  # Skip header
                    line = line.replace('"', "")
                    parts = line.split(",")
                    if len(parts) >= 2:
                        try:
                            name = parts[0].strip()
                            adapter_ram = (
                                int(parts[1]) if parts[1].strip().isdigit() else 0
                            )
                            if name and len(name) > 0:
                                if any(k in name.lower() for k in skip_keywords):
                                    continue
                                candidates.append({
                                    "name": name,
                                    "memory_mb": (
                                        adapter_ram // (1024 * 1024)
                                        if adapter_ram > 0
                                        else 0
                                    ),
                                })
                        except (ValueError, IndexError):
                            continue
                if candidates:
                    return max(candidates, key=lambda g: g["memory_mb"])

        elif system == "Linux":
            result = subprocess.run(
                ["lspci"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                candidates = []
                for line in result.stdout.split("\n"):
                    if "VGA compatible controller" in line:
                        parts = line.split(":", 2)
                        if len(parts) >= 3:
                            candidates.append({
                                "name": parts[2].strip(),
                                "memory_mb": 0,
                            })
                if candidates:
                    # Prefer AMD GPUs if present, otherwise return first
                    amd_gpus = [g for g in candidates if "amd" in g["name"].lower() or "radeon" in g["name"].lower()]
                    return amd_gpus[0] if amd_gpus else candidates[0]

    except Exception as e:
        print(f"GPU detection error: {e}")

    return {"name": "Not detected", "memory_mb": 0}
```

**`_register_tools()` メソッドを置き換え**、`get_hardware_info` ツールを追加します。

```python
def _register_tools(self):
    client = self.client
    agent = self

    @tool(atomic=True)
    def get_hardware_info() -> Dict[str, Any]:
        """Get detailed system hardware information including RAM, GPU, and NPU."""
        try:
            info = client.get_system_info()

            # Parse RAM (format: "32.0 GB")
            ram_str = info.get("Physical Memory", "0 GB")
            ram_gb = float(ram_str.split()[0]) if ram_str else 0

            # Detect GPU
            gpu_info = agent._get_gpu_info()
            gpu_name = gpu_info.get("name", "Not detected")
            gpu_available = gpu_name != "Not detected"
            gpu_memory_mb = gpu_info.get("memory_mb", 0)
            gpu_memory_gb = (
                round(gpu_memory_mb / 1024, 2) if gpu_memory_mb > 0 else 0
            )

            # Get NPU information from Lemonade
            devices = info.get("devices", {})
            npu_info = devices.get("amd_npu", {})
            npu_available = npu_info.get("available", False)
            npu_name = (
                npu_info.get("name", "Not detected")
                if npu_available
                else "Not detected"
            )

            return {
                "success": True,
                "os": info.get("OS Version", "Unknown"),
                "processor": info.get("Processor", "Unknown"),
                "ram_gb": ram_gb,
                "amd_igpu": {
                    "name": gpu_name,
                    "memory_mb": gpu_memory_mb,
                    "memory_gb": gpu_memory_gb,
                    "available": gpu_available,
                },
                "amd_npu": {"name": npu_name, "available": npu_available},
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get hardware information from Lemonade Server",
            }
```

インタラクティブなテストを有効にするために、**`__main__` ブロックを更新します**。

```python
if __name__ == "__main__":
    agent = HardwareAdvisorAgent()
    print("Hardware Advisor Agent (Ctrl+C to exit)")
    print("Try: 'Show me my system specs'\n")

    while True:
        try:
            query = input("You: ").strip()       
            if query:
                agent.process_query(query)
                print()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
```

実行して「システムの仕様を教えて」と尋ねてみてください。

```bash
python hardware_advisor_agent.py
```

**出力例:**

```
You: Show me my system specs

Agent: Your system has excellent specs for running LLMs locally!
- 32 GB RAM
- AMD Radeon RX 7900 XTX with 24 GB VRAM
- Ryzen AI NPU for accelerated inference
```

---

### ステップ 3: モデルカタログ

`_register_tools()` 内、`get_hardware_info` 関数の後に `list_available_models()` ツールを追加します。これでエージェントは利用可能なモデルについて答えられるようになります。

```python
    @tool(atomic=True)
    def list_available_models() -> Dict[str, Any]:
        """List all models available in the catalog with their sizes and download status."""
        try:
            response = client.list_models(show_all=True)
            models_data = response.get("data", [])

            enriched_models = []
            for model in models_data:
                model_id = model.get("id", "")
                model_info = client.get_model_info(model_id)
                size_gb = model_info.get("size_gb", 0)

                enriched_models.append(
                    {
                        "id": model_id,
                        "name": model.get("name", model_id),
                        "size_gb": size_gb,
                        "downloaded": model.get("downloaded", False),
                        "labels": model.get("labels", []),
                    }
                )

            enriched_models.sort(key=lambda m: m["size_gb"], reverse=True)

            return {
                "success": True,
                "models": enriched_models,
                "count": len(enriched_models),
                "message": f"Found {len(enriched_models)} models in catalog",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to fetch models from Lemonade Server",
            }
```

実行して「利用可能なモデルは何ですか?」と尋ねてみてください。

```bash
python hardware_advisor_agent.py
```

**出力例:**

```
You: What models are available?

Agent: I found 15 models in the catalog:
- Qwen3-Coder-30B (18.5 GB) [hot, coding] - Not downloaded
- Llama-3.1-8B (4.7 GB) [general] - Downloaded
- Qwen3-0.6B (0.4 GB) [hot, cpu, small] - Downloaded
```

---

### ステップ 4: スマートな推奨

`_register_tools()` 内、`list_available_models` の後に `recommend_models()` ツールを追加します。これでエージェントは、70% ルールを使ってシステムのメモリに収まるモデルを計算できるようになります。

```python
    @tool(atomic=True)
    def recommend_models(ram_gb: float, gpu_memory_mb: int = 0) -> Dict[str, Any]:
        """Recommend models based on available system memory.

        Args:
            ram_gb: Available system RAM in GB
            gpu_memory_mb: Available GPU memory in MB (0 if no GPU)

        Returns:
            Dictionary with model recommendations that fit in available memory
        """
        try:
            models_result = list_available_models()
            if not models_result.get("success"):
                return models_result

            all_models = models_result.get("models", [])

            # 70% rule: leave 30% overhead for inference
            max_model_size_gb = ram_gb * 0.7

            fitting_models = [
                model
                for model in all_models
                if model["size_gb"] <= max_model_size_gb and model["size_gb"] > 0
            ]

            for model in fitting_models:
                model["estimated_runtime_gb"] = round(model["size_gb"] * 1.3, 2)
                model["fits_in_ram"] = model["estimated_runtime_gb"] <= ram_gb

                if gpu_memory_mb > 0:
                    gpu_memory_gb = gpu_memory_mb / 1024
                    model["fits_in_gpu"] = model["size_gb"] <= (gpu_memory_gb * 0.9)

            fitting_models.sort(key=lambda m: m["size_gb"], reverse=True)

            return {
                "success": True,
                "recommendations": fitting_models,
                "total_fitting_models": len(fitting_models),
                "constraints": {
                    "available_ram_gb": ram_gb,
                    "available_gpu_mb": gpu_memory_mb,
                    "max_model_size_gb": round(max_model_size_gb, 2),
                    "safety_margin_percent": 30,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate model recommendations",
            }
```

実行して「どのサイズの LLM を実行できますか?」と尋ねてみてください。

```bash
python hardware_advisor_agent.py
```

**出力例:**

```
You: What size LLM can I run?

Agent: With 32 GB RAM and 24 GB GPU, you can safely run models up to 22.4 GB!

Top recommendations:
1. Qwen3-Coder-30B (18.5 GB) - Fits in RAM and GPU
2. Llama-3.1-8B (4.7 GB) - Fits in RAM and GPU
```

---

### ステップ 5: 本番用 CLI

シンプルな `__main__` ブロックを、洗練されたインタラクティブ CLI に置き換えます。これにより、バナー、終了コマンド、より優れたエラー処理が追加されます。

`if __name__ == "__main__":` ブロック全体を**次の内容に置き換えます**。

```python
def main():
    """Run the Hardware Advisor Agent interactively."""
    print("=" * 60)
    print("Hardware Advisor Agent")
    print("=" * 60)
    print("\nHi! I can help you figure out what size LLM your system can run.")
    print("\nTry asking:")
    print("  - 'What size LLM can I run?'")
    print("  - 'Show me my system specs'")
    print("  - 'What models are available?'")
    print("  - 'Can I run a 30B model?'")
    print("\nType 'quit', 'exit', or 'q' to stop.\n")

    try:
        agent = HardwareAdvisorAgent()
        print("Hardware Advisor Agent (Ctrl+C to exit)")
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("\nMake sure Lemonade Server is running before using GAIA.")
        return

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break

            agent.process_query(user_input)
            print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
```

---
### 最終確認

`hardware_advisor_agent.py` には、以下のコンポーネントがすべて揃っているはずです。

- [x] インポート: `from typing import Any, Dict` と `from gaia import Agent, tool`
- [x] `__init__` とシステムプロンプトを持つ `HardwareAdvisorAgent` クラス
- [x] `_get_gpu_info()` ヘルパー（Windows PowerShell + Linux lspci）
- [x] GPU、NPU、OS フィールドを持つ `get_hardware_info()` ツール
- [x] ラベルとサイズのエンリッチメントを備えた `list_available_models()` ツール
- [x] 70% ルール、fits_in_ram、fits_in_gpu を備えた `recommend_models()` ツール
- [x] インタラクティブ CLI を備えた `main()` 関数

**次のクエリをテストして、すべてが機能することを確認してください：**

- "What size LLM can I run?"
- "Show me my system specs"
- "What models are available?"
- "Can I run a 30B model?"

> **ヒント**: 完全な実装は [hardware_advisor_agent.py](assets/hardware_advisor_agent.py) で入手できます。

## 次のステップ

- **LemonadeClient API を調べる** — [LemonadeClient SDK ドキュメント](https://amd-gaia.ai/sdk/lemonade-client)で、より多くのシステムおよびモデル管理機能を発見してください
- **音声対話を追加する** — Whisper ASR と Kokoro TTS を統合して、ユーザーが話しかけることでハードウェアに関する質問ができるようにします。[Talk ガイド](https://amd-gaia.ai/guides/talk)をご覧ください
- **MCP サポートを追加する** — ハードウェアアドバイザーを MCP サーバーとして公開し、他のツールから問い合わせできるようにします。[MCP ガイド](https://amd-gaia.ai/sdk/infrastructure/mcp)をご覧ください
- **推奨エンジンを拡張する** — レイヤーのオフロードのために GPU の VRAM を考慮に入れる、またはベンチマークを追加してトークン毎秒を推定します
- **マルチエージェントシステムを構築する** — [Routing Agent](https://amd-gaia.ai/guides/routing) を使用して、ハードウェアアドバイザーをコードエージェントやチャットエージェントと組み合わせます