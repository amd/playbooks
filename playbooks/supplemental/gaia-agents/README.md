<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overview

# Getting Started Creating Agents with GAIA

GAIA agents are AI assistants that use a local LLM to reason and call tools you define — like chatbots that can take action. They run **100% locally** with no cloud APIs, no data leaving your machine, and no API keys required.

In this playbook, you'll build a Hardware Advisor Agent that detects your system's RAM, GPU, and NPU, queries the local model catalog, and recommends which LLMs your machine can run. It's a practical introduction to the GAIA Agent SDK that produces something immediately useful.

## What You'll Learn

- How to create a GAIA agent with custom tools
- Using the LemonadeClient SDK to query system info and model catalogs
- Platform-specific GPU/NPU detection (Windows PowerShell and Linux lspci)
- Memory-based model sizing using the 70% rule
- Building an interactive CLI for natural language hardware queries

## Installing Dependencies

<!-- @require:gaia,lemonade -->

## Getting Started

Get the finished agent running first so you can see what you're building, then we'll walk through the code step by step.

### 1. Run the Pre-Built Example

This playbook includes the complete [hardware_advisor_agent.py](assets/hardware_advisor_agent.py). Run it to see the finished agent in action:

```
uv run hardware_advisor_agent.py
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

**Try asking:** "What size LLM can I run?"

**Expected output:**

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

Now let's build this from scratch.

<!-- @os:windows -->
<!-- @test:id=gaia-lemonadeclient-smoke-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
$p = Start-Process -FilePath "lemonade-server" -ArgumentList "serve --no-tray --host 127.0.0.1 --port 8000" -NoNewWindow -PassThru
try {
  $health = $null
  for ($i=0; $i -lt 120; $i++) {
    $health = curl.exe -s --max-time 2 http://127.0.0.1:8000/api/v1/health
    if ($health) { break }
    Start-Sleep -Seconds 1
  }
  if (-not $health) { throw "Lemonade server not ready on http://127.0.0.1:8000/api/v1/health" }

  $script = @'
from gaia.llm.lemonade_client import LemonadeClient

client = LemonadeClient(keep_alive=True)

info = client.get_system_info()
assert isinstance(info, dict)
assert "Physical Memory" in info or "devices" in info

models = client.list_models(show_all=True)
assert isinstance(models, dict)
assert "data" in models

model_info = client.get_model_info("Qwen3-Coder-30B-A3B-Instruct-GGUF")
assert isinstance(model_info, dict)
assert model_info.get("id") == "Qwen3-Coder-30B-A3B-Instruct-GGUF"

print("OK")
'@
  Set-Content -Path gaia_lemonadeclient_smoke.py -Value $script
  .\.venv\Scripts\python.exe gaia_lemonadeclient_smoke.py
} finally {
  Remove-Item gaia_lemonadeclient_smoke.py -ErrorAction SilentlyContinue
  & lemonade-server stop
  Start-Sleep -Seconds 2
  if ($p -and -not $p.HasExited) {
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
  }
}
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:windows -->
<!-- @test:id=gaia-hardware-advisor-smoke-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
$uvBin = Join-Path $env:USERPROFILE ".local\bin"
if (Test-Path $uvBin) { $env:PATH = "$uvBin;$env:PATH" }

$p = Start-Process -FilePath "lemonade-server" -ArgumentList "serve --no-tray --host 127.0.0.1 --port 8000" -NoNewWindow -PassThru
try {
  for ($i=0; $i -lt 120; $i++) {
    $health = curl.exe -s --max-time 2 http://127.0.0.1:8000/api/v1/health
    if ($health) { break }
    Start-Sleep -Seconds 1
  }

  $inputText = "quit"
  $output = $inputText | uv run hardware_advisor_agent.py
  if (-not ($output -match "Hardware Advisor Agent")) {
    throw "Did not see expected startup banner from hardware_advisor_agent.py"
  }
  Write-Host "OK: hardware_advisor_agent.py started successfully"
} finally {
  & lemonade-server stop
  Start-Sleep -Seconds 2
  if ($p -and -not $p.HasExited) {
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
  }
}
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux -->
<!-- @test:id=gaia-lemonadeclient-smoke-linux timeout=300 hidden=True -->
```bash
set -euo pipefail
source .venv/bin/activate

cat >/tmp/gaia_lemonadeclient_smoke.py <<'PY'
from gaia.llm.lemonade_client import LemonadeClient

client = LemonadeClient(keep_alive=True)

info = client.get_system_info()
assert isinstance(info, dict)
assert "Physical Memory" in info or "devices" in info

models = client.list_models(show_all=True)
assert isinstance(models, dict)
assert "data" in models

model_info = client.get_model_info("Qwen3-Coder-30B-A3B-Instruct-GGUF")
assert isinstance(model_info, dict)
assert model_info.get("id") == "Qwen3-Coder-30B-A3B-Instruct-GGUF"

print("OK")
PY

python3 /tmp/gaia_lemonadeclient_smoke.py
rm -f /tmp/gaia_lemonadeclient_smoke.py
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux -->
<!-- @test:id=gaia-hardware-advisor-smoke-linux timeout=300 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

p=""
cleanup() {
  lemonade-server stop >/dev/null 2>&1 || true
  sleep 2
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

lemonade-server serve --host 127.0.0.1 --port 8000 >/tmp/gaia-agent.log 2>&1 &
p=$!

for i in $(seq 1 120); do
  health="$(curl -s --max-time 2 http://127.0.0.1:8000/api/v1/health || true)"
  if [ -n "$health" ]; then
    break
  fi
  sleep 1
done

printf 'quit' | uv run hardware_advisor_agent.py >/tmp/gaia_agent_output.txt

grep -q "Hardware Advisor Agent" /tmp/gaia_agent_output.txt
echo "OK: hardware_advisor_agent.py started successfully"
```
<!-- @test:end --> 
<!-- @os:end --> 


## Core Concepts

### Architecture

The Hardware Advisor Agent combines three components:

- **LemonadeClient SDK** — System info and model catalog APIs
- **Platform-specific detection** — Windows PowerShell / Linux lspci for GPU info
- **Memory calculations** — 70% rule for safe model sizing

The data flows through these in sequence: user query → agent selects a tool → tool calls LemonadeClient + OS detection → agent synthesizes the results into a recommendation.

### LemonadeClient SDK

The LemonadeClient provides a unified API for system detection, NPU/GPU availability, and model catalog queries.

**Import and initialize:**

```python
from gaia.llm.lemonade_client import LemonadeClient

client = LemonadeClient(keep_alive=True)
```

**`get_system_info()`** — Returns OS, CPU, RAM, and device availability:

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

**`list_models(show_all=True)`** — Returns the full model catalog:

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

**`get_model_info(model_id)`** — Returns size estimates for a specific model:

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

### Platform-Specific GPU Detection

The agent uses OS-native commands rather than PyTorch for GPU detection. This works without GPU drivers installed, detects all GPUs (not just CUDA-capable ones), and avoids heavy library imports.

<!-- @os:windows -->

On Windows, the agent uses PowerShell to query WMI:

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

On Linux, the agent uses lspci:

```python
result = subprocess.run(
    ["lspci"], capture_output=True, text=True, timeout=5
)
# Parse output for "VGA compatible controller" lines
# Note: Memory not available via lspci
```

<!-- @os:end -->

### The 70% Memory Rule

> **Rule:** Model size should be less than 70% of available RAM to leave 30% overhead for inference operations (KV cache, batch processing buffers, runtime memory spikes).

```
System: 32 GB RAM
Max safe model size: 32 x 0.7 = 22.4 GB
30B model (~18.5 GB): Fits safely
70B model (~42 GB):   Too large
```

## Building the Agent Step by Step

You'll create **one file** called `hardware_advisor.py` and progressively add features. Each step builds on the previous one.

### Step 1: Agent Skeleton

Start with a minimal agent structure — just the class and a basic system prompt. The agent has no tools yet.

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

Run it to verify:

```
uv run hardware_advisor.py
```

Expected output:

```
Agent created successfully!
```

---

### Step 2: GPU and Hardware Detection

Add the `_get_gpu_info()` helper method and the `get_hardware_info()` tool. This makes the agent interactive — you can now query it about system specs.

**Update the imports** at the top of the file:

```python
from typing import Any, Dict

from gaia import Agent, tool
from gaia.llm.lemonade_client import LemonadeClient
```

**Add the `_get_gpu_info()` helper** after the `_get_system_prompt()` method:

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

**Replace the `_register_tools()` method** with the `get_hardware_info` tool:

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

**Update the `__main__` block** to enable interactive testing:

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

Run and try asking "Show me my system specs":

```
uv run hardware_advisor.py
```

**Example output:**

```
You: Show me my system specs

Agent: Your system has excellent specs for running LLMs locally!
- 32 GB RAM
- AMD Radeon RX 7900 XTX with 24 GB VRAM
- Ryzen AI NPU for accelerated inference
```

---

### Step 3: Model Catalog

Add the `list_available_models()` tool inside `_register_tools()`, after the `get_hardware_info` function. Now the agent can tell you what models are available.

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

Run and try asking "What models are available?":

```
uv run hardware_advisor.py
```

**Example output:**

```
You: What models are available?

Agent: I found 15 models in the catalog:
- Qwen3-Coder-30B (18.5 GB) [hot, coding] - Not downloaded
- Llama-3.1-8B (4.7 GB) [general] - Downloaded
- Qwen3-0.6B (0.4 GB) [hot, cpu, small] - Downloaded
```

---

### Step 4: Smart Recommendations

Add the `recommend_models()` tool inside `_register_tools()`, after `list_available_models`. The agent can now calculate which models fit in your system's memory using the 70% rule.

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

Run and try asking "What size LLM can I run?":

```
uv run hardware_advisor.py
```

**Example output:**

```
You: What size LLM can I run?

Agent: With 32 GB RAM and 24 GB GPU, you can safely run models up to 22.4 GB!

Top recommendations:
1. Qwen3-Coder-30B (18.5 GB) - Fits in RAM and GPU
2. Llama-3.1-8B (4.7 GB) - Fits in RAM and GPU
```

---

### Step 5: Production CLI

Replace the simple `__main__` block with a polished interactive CLI. This adds a banner, quit commands, and better error handling.

**Replace the entire `if __name__ == "__main__":` block** with:

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
        print("Agent ready!\n")
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

### Final Verification

Your `hardware_advisor.py` should now have all of these components:

- [x] Imports: `from typing import Any, Dict` and `from gaia import Agent, tool`
- [x] `HardwareAdvisorAgent` class with `__init__` and system prompt
- [x] `_get_gpu_info()` helper (Windows PowerShell + Linux lspci)
- [x] `get_hardware_info()` tool with GPU, NPU, and OS fields
- [x] `list_available_models()` tool with labels and size enrichment
- [x] `recommend_models()` tool with 70% rule, fits_in_ram, fits_in_gpu
- [x] `main()` function with interactive CLI

**Test these queries to confirm everything works:**

- "What size LLM can I run?"
- "Show me my system specs"
- "What models are available?"
- "Can I run a 30B model?"

> **Tip**: The complete implementation is available at [hardware_advisor_agent.py](assets/hardware_advisor_agent.py).

## Next Steps

- **Explore LemonadeClient APIs** — Discover more system and model management capabilities in the [LemonadeClient SDK documentation](https://amd-gaia.ai/sdk/lemonade-client)
- **Add voice interaction** — Integrate Whisper ASR and Kokoro TTS to let users ask hardware questions by speaking. See the [Talk guide](https://amd-gaia.ai/guides/talk)
- **Add MCP support** — Expose the hardware advisor as an MCP server so other tools can query it. See the [MCP guide](https://amd-gaia.ai/sdk/infrastructure/mcp)
- **Extend the recommendation engine** — Factor in GPU VRAM for offloading layers, or add benchmarking to estimate tokens-per-second
- **Build a multi-agent system** — Combine the hardware advisor with a code agent or chat agent using the [Routing Agent](https://amd-gaia.ai/guides/routing)
