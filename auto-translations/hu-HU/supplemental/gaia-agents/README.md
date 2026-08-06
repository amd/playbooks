<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés

A GAIA ügynökök olyan AI asszisztensek, amelyek egy helyi LLM-et használnak az érveléshez és az általad definiált eszközök meghívásához — olyan chatbotok, amelyek képesek cselekedni. **100%-ban helyben** futnak, felhő alapú API-k nélkül, anélkül, hogy bármilyen adat elhagyná a gépedet, és API-kulcsok sem szükségesek.

Ebben a playbookban egy Hardware Advisor Agentet fogsz építeni, amely érzékeli a rendszered RAM-ját, GPU-ját és NPU-ját, lekérdezi a helyi modellkatalógust, és javaslatot tesz arra, hogy mely LLM-eket tudja futtatni a géped. Ez egy gyakorlatias bevezetés a GAIA Agent SDK-ba, amely azonnal hasznos eredményt ad.

## Amit meg fogsz tanulni

- Hogyan hozz létre egy GAIA ügynököt egyedi eszközökkel
- A LemonadeClient SDK használata rendszerinformációk és modellkatalógusok lekérdezéséhez
- Platformspecifikus GPU/NPU-érzékelés (Windows PowerShell és Linux lspci)
- Memória alapú modellméretezés a 70%-os szabály segítségével
- Interaktív CLI építése természetes nyelvű hardverkérdésekhez

## A memória konfigurálása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Ellenőrizd a szoftverfrissítéseket
> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheted a Ryzen AI Developer Centerrel.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftverelőfeltételek telepítése

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

## Első lépések

Először futtasd le a kész ügynököt, hogy lásd, mit fogsz építeni. Ezután lépésről lépésre végigmegyünk a kódon.

### Az előre elkészített példa futtatása

Ez a playbook tartalmazza a teljes [hardware_advisor_agent.py](assets/hardware_advisor_agent.py) fájlt. Töltsd le egy tetszőleges könyvtárba, és futtasd, hogy megnézd a kész ügynököt működés közben:

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

**Próbáld ezt kérdezni:** "What size LLM can I run?"

**Várt kimenet:**

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

**Gratulálunk** – sikeresen felépítettél egy ügynököt!

A playbook hátralévő része azt fogja bemutatni, hogyan működik a szkript minden egyes része, hogy a legelejétől megértsd.
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


## Az architektúra megértése

A Hardware Advisor Agent három komponenst egyesít:

- **LemonadeClient SDK** — Rendszerinformációs és modellkatalógus API-k
- **Platformspecifikus érzékelés** — Windows PowerShell / Linux lspci a GPU-információkhoz
- **Memóriaszámítások** — 70%-os szabály a biztonságos modellméretezéshez

Az adatok az alábbi sorrendben áramlanak: felhasználói kérdés → az ügynök kiválaszt egy eszközt → az eszköz meghívja a LemonadeClientet + az operációs rendszer érzékelését → az ügynök az eredményeket egy javaslattá szintetizálja.

### LemonadeClient SDK

A LemonadeClient egységes API-t biztosít a rendszerérzékeléshez, az NPU/GPU elérhetőségéhez és a modellkatalógus-lekérdezésekhez.

**Importálás és inicializálás:**

```python
from gaia.llm.lemonade_client import LemonadeClient

client = LemonadeClient(keep_alive=True)
```

**`get_system_info()`** — Visszaadja az operációs rendszert, a CPU-t, a RAM-ot és az eszközök elérhetőségét:

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

**`list_models(show_all=True)`** — Visszaadja a teljes modellkatalógust:

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

**`get_model_info(model_id)`** — Visszaadja egy adott modell méretbecslését:

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

### Platformspecifikus GPU-érzékelés

Az ügynök az operációs rendszer natív parancsait használja a GPU-érzékeléshez, nem pedig a PyTorch-ot. Ez GPU-illesztőprogramok nélkül is működik, minden GPU-t érzékel (nem csak a CUDA-képeseket), és elkerüli a nehéz könyvtárimportokat.

<!-- @os:windows -->

Windows rendszeren az ügynök PowerShellt használ a WMI lekérdezéséhez:

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

Linux rendszeren az ügynök az lspci-t használja:

```python
result = subprocess.run(
    ["lspci"], capture_output=True, text=True, timeout=5
)
# Parse output for "VGA compatible controller" lines
# Note: Memory not available via lspci
```

<!-- @os:end -->

### A 70%-os memóriaszabály

> **Szabály:** A modell méretének kisebbnek kell lennie a rendelkezésre álló RAM 70%-ánál, hogy 30% ráhagyás maradjon az inferencia műveletekhez (KV-cache, kötegelt feldolgozási pufferek, futásidejű memóriacsúcsok).

```
System: 32 GB RAM
Max safe model size: 32 x 0.7 = 22.4 GB
30B model (~18.5 GB): Fits safely
70B model (~42 GB):   Too large
```

## Az ügynök kódolása lépésről lépésre (opcionális)

Létre fogsz hozni **egyetlen fájlt** `hardware_advisor_agent.py` néven, és fokozatosan hozzáadod a funkciókat. Minden lépés az előzőre épül.

### 1. lépés: Az ügynök váza

Kezdd egy minimális ügynökstruktúrával — csak az osztály és egy alapvető rendszerprompt. Az ügynöknek még nincsenek eszközei.

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

Futtasd, hogy ellenőrizd:

```bash
python hardware_advisor_agent.py
```

Várt kimenet:

```
Agent created successfully!
```

---

### 2. lépés: GPU- és hardverérzékelés

Add hozzá a `_get_gpu_info()` segédmetódust és a `get_hardware_info()` eszközt. Ez interaktívvá teszi az ügynököt — most már lekérdezheted tőle a rendszer specifikációit.

**Frissítsd az importokat** a fájl elején:

```python
from typing import Any, Dict

from gaia import Agent, tool
from gaia.llm.lemonade_client import LemonadeClient
```

**Add hozzá a `_get_gpu_info()` segédmetódust** a `_get_system_prompt()` metódus után:

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

**Cseréld le a `_register_tools()` metódust** a `get_hardware_info` eszközre:

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

**Frissítsd a `__main__` blokkot** az interaktív teszteléshez:

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

Futtasd, és próbáld megkérdezni: "Show me my system specs":

```bash
python hardware_advisor_agent.py
```

**Példa kimenet:**

```
You: Show me my system specs

Agent: Your system has excellent specs for running LLMs locally!
- 32 GB RAM
- AMD Radeon RX 7900 XTX with 24 GB VRAM
- Ryzen AI NPU for accelerated inference
```

---

### 3. lépés: Modellkatalógus

Add hozzá a `list_available_models()` eszközt a `_register_tools()`-on belül, a `get_hardware_info` funkció után. Az ügynök most már meg tudja mondani, milyen modellek érhetők el.

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

Futtasd, és próbáld megkérdezni: "What models are available?":

```bash
python hardware_advisor_agent.py
```

**Példa kimenet:**

```
You: What models are available?

Agent: I found 15 models in the catalog:
- Qwen3-Coder-30B (18.5 GB) [hot, coding] - Not downloaded
- Llama-3.1-8B (4.7 GB) [general] - Downloaded
- Qwen3-0.6B (0.4 GB) [hot, cpu, small] - Downloaded
```

---

### 4. lépés: Okos ajánlások

Add hozzá a `recommend_models()` eszközt a `_register_tools()`-on belül, a `list_available_models` után. Az ügynök mostantól ki tudja számítani, hogy mely modellek férnek el a rendszered memóriájában a 70%-os szabály alapján.

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

Futtasd, és próbáld megkérdezni: "What size LLM can I run?":

```bash
python hardware_advisor_agent.py
```

**Példa kimenet:**

```
You: What size LLM can I run?

Agent: With 32 GB RAM and 24 GB GPU, you can safely run models up to 22.4 GB!

Top recommendations:
1. Qwen3-Coder-30B (18.5 GB) - Fits in RAM and GPU
2. Llama-3.1-8B (4.7 GB) - Fits in RAM and GPU
```

---

### 5. lépés: Éles CLI

Cseréld le az egyszerű `__main__` blokkot egy csiszolt, interaktív CLI-re. Ez hozzáad egy fejlécet, kilépési parancsokat és jobb hibakezelést.

**Cseréld le a teljes `if __name__ == "__main__":` blokkot** erre:

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
### Végső ellenőrzés

A `hardware_advisor_agent.py` fájlodnak most már tartalmaznia kell az összes alábbi komponenst:

- [x] Importok: `from typing import Any, Dict` és `from gaia import Agent, tool`
- [x] `HardwareAdvisorAgent` osztály `__init__` metódussal és rendszerpromttal
- [x] `_get_gpu_info()` segédfüggvény (Windows PowerShell + Linux lspci)
- [x] `get_hardware_info()` eszköz GPU, NPU és OS mezőkkel
- [x] `list_available_models()` eszköz címkékkel és mérettel bővítve
- [x] `recommend_models()` eszköz a 70%-os szabállyal, fits_in_ram és fits_in_gpu mezőkkel
- [x] `main()` függvény interaktív CLI-vel

**Teszteld ezeket a lekérdezéseket, hogy minden működik-e:**

- "Milyen méretű LLM-et tudok futtatni?"
- "Mutasd meg a rendszerem specifikációit"
- "Milyen modellek érhetők el?"
- "Tudok futtatni egy 30B-s modellt?"

> **Tipp**: A teljes implementáció elérhető itt: [hardware_advisor_agent.py](assets/hardware_advisor_agent.py).

## Következő lépések

- **Fedezd fel a LemonadeClient API-kat** — Ismerd meg a további rendszer- és modellkezelési lehetőségeket a [LemonadeClient SDK dokumentációban](https://amd-gaia.ai/sdk/lemonade-client)
- **Adj hozzá hangalapú interakciót** — Integrálj Whisper ASR-t és Kokoro TTS-t, hogy a felhasználók beszéddel is feltehessék a hardverrel kapcsolatos kérdéseiket. Lásd a [Talk útmutatót](https://amd-gaia.ai/guides/talk)
- **Adj hozzá MCP-támogatást** — Tedd elérhetővé a hardver-tanácsadót MCP szerverként, hogy más eszközök is lekérdezhessék. Lásd az [MCP útmutatót](https://amd-gaia.ai/sdk/infrastructure/mcp)
- **Bővítsd az ajánlómotort** — Vedd figyelembe a GPU VRAM-ot a rétegek kiszervezéséhez, vagy adj hozzá benchmarkingot a másodpercenkénti tokenszám becsléséhez
- **Építs többügynökös rendszert** — Kombináld a hardver-tanácsadót egy kódügynökkel vagy csevegő ügynökkel a [Routing Agent](https://amd-gaia.ai/guides/routing) segítségével