<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversigt

GAIA-agenter er AI-assistenter, der bruger en lokal LLM til at ræsonnere og kalde værktøjer, du selv definerer — som chatbots, der kan udføre handlinger. De kører **100 % lokalt** uden cloud-API'er, uden at data forlader din maskine, og uden behov for API-nøgler.

I denne playbook skal du bygge en Hardware Advisor Agent, der registrerer dit systems RAM, GPU og NPU, forespørger det lokale modelkatalog og anbefaler, hvilke LLM'er din maskine kan køre. Det er en praktisk introduktion til GAIA Agent SDK, der giver noget umiddelbart brugbart.

## Hvad du vil lære

- Hvordan man opretter en GAIA-agent med brugerdefinerede værktøjer
- Brug af LemonadeClient SDK til at forespørge systemoplysninger og modelkataloger
- Platformsspecifik GPU/NPU-registrering (Windows PowerShell og Linux lspci)
- Hukommelsesbaseret modeldimensionering med 70 %-reglen
- Bygning af en interaktiv CLI til naturlige sproghenvendelser om hardware

## Konfiguration af hukommelse

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollér for softwareopdateringer
> **Bemærk**: Hvis VS Code ikke er installeret, kan du installere det med Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger

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

<!-- @require:lemonade -->
<!-- @require:gaia -->

## Kom godt i gang

Få først den færdige agent til at køre, så du kan se, hvad du bygger. Derefter gennemgår vi koden trin for trin.

### Kør det færdigbyggede eksempel

Denne playbook indeholder det komplette [hardware_advisor_agent.py](assets/hardware_advisor_agent.py). Download det til en mappe efter eget valg, og kør det for at se den færdige agent i aktion:

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

**Prøv at spørge:** "What size LLM can I run?"

**Forventet output:**

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

**Tillykke** - du har bygget en agent! 

Resten af playbooken vil forklare, hvordan hver del af scriptet fungerer, så du kan forstå det fra bunden.
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


## Forstå arkitekturen

Hardware Advisor Agent kombinerer tre komponenter:

- **LemonadeClient SDK** — API'er til systeminformation og modelkatalog
- **Platformsspecifik registrering** — Windows PowerShell / Linux lspci til GPU-information
- **Hukommelsesberegninger** — 70 %-reglen for sikker modeldimensionering

Dataene flyder gennem disse i rækkefølge: brugerforespørgsel → agenten vælger et værktøj → værktøjet kalder LemonadeClient + OS-registrering → agenten sammenfatter resultaterne til en anbefaling.

### LemonadeClient SDK

LemonadeClient tilbyder en samlet API til systemregistrering, tilgængelighed af NPU/GPU og forespørgsler i modelkataloget.

**Importér og initialisér:**

```python
from gaia.llm.lemonade_client import LemonadeClient

client = LemonadeClient(keep_alive=True)
```

**`get_system_info()`** — Returnerer OS, CPU, RAM og enhedstilgængelighed:

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

**`list_models(show_all=True)`** — Returnerer det fulde modelkatalog:

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

**`get_model_info(model_id)`** — Returnerer størrelsesestimater for en bestemt model:

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

### Platformsspecifik GPU-registrering

Agenten bruger OS-native kommandoer i stedet for PyTorch til GPU-registrering. Dette fungerer uden installerede GPU-drivere, registrerer alle GPU'er (ikke kun CUDA-kompatible), og undgår tunge biblioteksimporter.

<!-- @os:windows -->

På Windows bruger agenten PowerShell til at forespørge WMI:

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

På Linux bruger agenten lspci:

```python
result = subprocess.run(
    ["lspci"], capture_output=True, text=True, timeout=5
)
# Parse output for "VGA compatible controller" lines
# Note: Memory not available via lspci
```

<!-- @os:end -->

### 70 %-hukommelsesreglen

> **Regel:** Modelstørrelsen bør være mindre end 70 % af den tilgængelige RAM for at efterlade 30 % overhead til inferensoperationer (KV-cache, batchbehandlingsbuffere, runtime-hukommelsesspidser).

```
System: 32 GB RAM
Max safe model size: 32 x 0.7 = 22.4 GB
30B model (~18.5 GB): Fits safely
70B model (~42 GB):   Too large
```

## Kodning af agenten trin for trin (valgfrit)

Du skal oprette **én fil** kaldet `hardware_advisor_agent.py` og gradvist tilføje funktioner. Hvert trin bygger videre på det forrige.

### Trin 1: Agentskelet

Start med en minimal agentstruktur — kun klassen og en grundlæggende systemprompt. Agenten har endnu ingen værktøjer.

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

Kør det for at verificere:

```bash
python hardware_advisor_agent.py
```

Forventet output:

```
Agent created successfully!
```

---

### Trin 2: GPU- og hardwareregistrering

Tilføj hjælpemetoden `_get_gpu_info()` og værktøjet `get_hardware_info()`. Dette gør agenten interaktiv — du kan nu spørge den om systemspecifikationer.

**Opdatér importene** øverst i filen:

```python
from typing import Any, Dict

from gaia import Agent, tool
from gaia.llm.lemonade_client import LemonadeClient
```

**Tilføj hjælpemetoden `_get_gpu_info()`** efter metoden `_get_system_prompt()`:

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

**Erstat metoden `_register_tools()`** med værktøjet `get_hardware_info`:

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

**Opdatér `__main__`-blokken** for at aktivere interaktiv test:

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

Kør og prøv at spørge "Show me my system specs":

```bash
python hardware_advisor_agent.py
```

**Eksempel på output:**

```
You: Show me my system specs

Agent: Your system has excellent specs for running LLMs locally!
- 32 GB RAM
- AMD Radeon RX 7900 XTX with 24 GB VRAM
- Ryzen AI NPU for accelerated inference
```

---

### Trin 3: Modelkatalog

Tilføj værktøjet `list_available_models()` inde i `_register_tools()`, efter funktionen `get_hardware_info`. Nu kan agenten fortælle dig, hvilke modeller der er tilgængelige.

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

Kør og prøv at spørge "What models are available?":

```bash
python hardware_advisor_agent.py
```

**Eksempel på output:**

```
You: What models are available?

Agent: I found 15 models in the catalog:
- Qwen3-Coder-30B (18.5 GB) [hot, coding] - Not downloaded
- Llama-3.1-8B (4.7 GB) [general] - Downloaded
- Qwen3-0.6B (0.4 GB) [hot, cpu, small] - Downloaded
```

---

### Trin 4: Intelligente anbefalinger

Tilføj værktøjet `recommend_models()` inde i `_register_tools()`, efter `list_available_models`. Agenten kan nu beregne, hvilke modeller der passer ind i systemets hukommelse ved hjælp af 70 %-reglen.

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

Kør og prøv at spørge "What size LLM can I run?":

```bash
python hardware_advisor_agent.py
```

**Eksempel på output:**

```
You: What size LLM can I run?

Agent: With 32 GB RAM and 24 GB GPU, you can safely run models up to 22.4 GB!

Top recommendations:
1. Qwen3-Coder-30B (18.5 GB) - Fits in RAM and GPU
2. Llama-3.1-8B (4.7 GB) - Fits in RAM and GPU
```

---

### Trin 5: Produktions-CLI

Erstat den simple `__main__`-blok med en poleret interaktiv CLI. Dette tilføjer et banner, afslutningskommandoer og bedre fejlhåndtering.

**Erstat hele blokken `if __name__ == "__main__":`** med:

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
### Endelig verificering

Din `hardware_advisor_agent.py` bør nu have alle disse komponenter:

- [x] Imports: `from typing import Any, Dict` og `from gaia import Agent, tool`
- [x] `HardwareAdvisorAgent`-klasse med `__init__` og system prompt
- [x] `_get_gpu_info()`-hjælper (Windows PowerShell + Linux lspci)
- [x] `get_hardware_info()`-værktøj med GPU-, NPU- og OS-felter
- [x] `list_available_models()`-værktøj med etiketter og størrelsesberigelse
- [x] `recommend_models()`-værktøj med 70%-reglen, fits_in_ram, fits_in_gpu
- [x] `main()`-funktion med interaktiv CLI

**Test disse forespørgsler for at bekræfte, at alt fungerer:**

- "What size LLM can I run?"
- "Show me my system specs"
- "What models are available?"
- "Can I run a 30B model?"

> **Tip**: Den fulde implementering er tilgængelig på [hardware_advisor_agent.py](assets/hardware_advisor_agent.py).

## Næste skridt

- **Udforsk LemonadeClient API'er** — Opdag flere muligheder for system- og modelstyring i [LemonadeClient SDK-dokumentationen](https://amd-gaia.ai/sdk/lemonade-client)
- **Tilføj taleinteraktion** — Integrer Whisper ASR og Kokoro TTS, så brugere kan stille spørgsmål om hardware ved at tale. Se [Talk-guiden](https://amd-gaia.ai/guides/talk)
- **Tilføj MCP-understøttelse** — Eksponer hardwarerådgiveren som en MCP-server, så andre værktøjer kan forespørge den. Se [MCP-guiden](https://amd-gaia.ai/sdk/infrastructure/mcp)
- **Udvid anbefalingsmotoren** — Tag højde for GPU VRAM til aflastning af lag, eller tilføj benchmarking for at estimere tokens-per-second
- **Byg et multi-agent-system** — Kombiner hardwarerådgiveren med en kodeagent eller chatagent ved hjælp af [Routing Agent](https://amd-gaia.ai/guides/routing)