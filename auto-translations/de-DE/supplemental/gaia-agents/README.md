<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Übersicht

GAIA-Agenten sind KI-Assistenten, die ein lokales LLM verwenden, um zu argumentieren und von Ihnen definierte Tools aufzurufen — wie Chatbots, die Aktionen ausführen können. Sie laufen **zu 100 % lokal**, ohne Cloud-APIs, ohne dass Daten Ihren Rechner verlassen und ohne API-Schlüssel.

In diesem Playbook erstellen Sie einen Hardware Advisor Agent, der den RAM, die GPU und die NPU Ihres Systems erkennt, den lokalen Modellkatalog abfragt und empfiehlt, welche LLMs Ihr Rechner ausführen kann. Es ist eine praktische Einführung in das GAIA Agent SDK, die ein sofort nützliches Ergebnis liefert.

## Was Sie lernen werden

- Wie man einen GAIA-Agenten mit benutzerdefinierten Tools erstellt
- Verwendung des LemonadeClient SDK zur Abfrage von Systeminformationen und Modellkatalogen
- Plattformspezifische GPU/NPU-Erkennung (Windows PowerShell und Linux lspci)
- Speicherbasierte Modellgrößenbestimmung nach der 70-%-Regel
- Erstellung einer interaktiven CLI für natürlichsprachliche Hardware-Abfragen

## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen
> **Hinweis**: Falls VS Code nicht installiert ist, können Sie es mit dem Ryzen AI Developer Center installieren.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation der Software-Voraussetzungen

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

## Erste Schritte

Bringen Sie zunächst den fertigen Agenten zum Laufen, damit Sie sehen können, was Sie erstellen. Anschließend gehen wir den Code Schritt für Schritt durch.

### Das vorgefertigte Beispiel ausführen

Dieses Playbook enthält den vollständigen [hardware_advisor_agent.py](assets/hardware_advisor_agent.py). Laden Sie es in ein Verzeichnis Ihrer Wahl herunter und führen Sie es aus, um den fertigen Agenten in Aktion zu sehen:

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

**Versuchen Sie zu fragen:** "What size LLM can I run?"

**Erwartete Ausgabe:**

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

**Herzlichen Glückwunsch** – Sie haben einen Agenten erstellt!

Im Rest des Playbooks wird erklärt, wie jeder Teil des Skripts funktioniert, damit Sie es von Grund auf verstehen können.
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


## Die Architektur verstehen

Der Hardware Advisor Agent kombiniert drei Komponenten:

- **LemonadeClient SDK** — APIs für Systeminformationen und Modellkatalog
- **Plattformspezifische Erkennung** — Windows PowerShell / Linux lspci für GPU-Informationen
- **Speicherberechnungen** — 70-%-Regel für sichere Modellgrößenbestimmung

Die Daten durchlaufen diese Komponenten in dieser Reihenfolge: Benutzeranfrage → Agent wählt ein Tool aus → Tool ruft LemonadeClient + Betriebssystemerkennung auf → Agent fasst die Ergebnisse zu einer Empfehlung zusammen.

### LemonadeClient SDK

Der LemonadeClient bietet eine einheitliche API für Systemerkennung, NPU/GPU-Verfügbarkeit und Modellkatalogabfragen.

**Importieren und initialisieren:**

```python
from gaia.llm.lemonade_client import LemonadeClient

client = LemonadeClient(keep_alive=True)
```

**`get_system_info()`** — Gibt Betriebssystem, CPU, RAM und Geräteverfügbarkeit zurück:

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

**`list_models(show_all=True)`** — Gibt den vollständigen Modellkatalog zurück:

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

**`get_model_info(model_id)`** — Gibt Größenschätzungen für ein bestimmtes Modell zurück:

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

### Plattformspezifische GPU-Erkennung

Der Agent verwendet betriebssystemeigene Befehle anstelle von PyTorch zur GPU-Erkennung. Dies funktioniert auch ohne installierte GPU-Treiber, erkennt alle GPUs (nicht nur CUDA-fähige) und vermeidet das Importieren umfangreicher Bibliotheken.

<!-- @os:windows -->

Unter Windows verwendet der Agent PowerShell zur Abfrage von WMI:

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

Unter Linux verwendet der Agent lspci:

```python
result = subprocess.run(
    ["lspci"], capture_output=True, text=True, timeout=5
)
# Parse output for "VGA compatible controller" lines
# Note: Memory not available via lspci
```

<!-- @os:end -->

### Die 70-%-Speicherregel

> **Regel:** Die Modellgröße sollte weniger als 70 % des verfügbaren RAM betragen, um 30 % Spielraum für Inferenzoperationen (KV-Cache, Batch-Verarbeitungspuffer, Laufzeit-Speicherspitzen) zu lassen.

```
System: 32 GB RAM
Max safe model size: 32 x 0.7 = 22.4 GB
30B model (~18.5 GB): Fits safely
70B model (~42 GB):   Too large
```

## Den Agenten Schritt für Schritt programmieren (optional)

Sie erstellen **eine Datei** namens `hardware_advisor_agent.py` und fügen schrittweise Funktionen hinzu. Jeder Schritt baut auf dem vorherigen auf.

### Schritt 1: Agenten-Grundgerüst

Beginnen Sie mit einer minimalen Agentenstruktur — nur die Klasse und ein einfacher System-Prompt. Der Agent hat noch keine Tools.

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

Führen Sie es aus, um es zu überprüfen:

```bash
python hardware_advisor_agent.py
```

Erwartete Ausgabe:

```
Agent created successfully!
```

---

### Schritt 2: GPU- und Hardware-Erkennung

Fügen Sie die Hilfsmethode `_get_gpu_info()` und das Tool `get_hardware_info()` hinzu. Dies macht den Agenten interaktiv — Sie können ihn nun zu Systemspezifikationen befragen.

**Aktualisieren Sie die Importe** am Anfang der Datei:

```python
from typing import Any, Dict

from gaia import Agent, tool
from gaia.llm.lemonade_client import LemonadeClient
```

**Fügen Sie die Hilfsmethode `_get_gpu_info()`** nach der Methode `_get_system_prompt()` hinzu:

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

**Ersetzen Sie die Methode `_register_tools()`** durch das Tool `get_hardware_info`:

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

**Aktualisieren Sie den Block `__main__`**, um interaktives Testen zu ermöglichen:

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

Führen Sie das Programm aus und fragen Sie "Show me my system specs":

```bash
python hardware_advisor_agent.py
```

**Beispielausgabe:**

```
You: Show me my system specs

Agent: Your system has excellent specs for running LLMs locally!
- 32 GB RAM
- AMD Radeon RX 7900 XTX with 24 GB VRAM
- Ryzen AI NPU for accelerated inference
```

---

### Schritt 3: Modellkatalog

Fügen Sie das Tool `list_available_models()` innerhalb von `_register_tools()` nach der Funktion `get_hardware_info` hinzu. Der Agent kann Ihnen nun mitteilen, welche Modelle verfügbar sind.

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

Führen Sie das Programm aus und fragen Sie "What models are available?":

```bash
python hardware_advisor_agent.py
```

**Beispielausgabe:**

```
You: What models are available?

Agent: I found 15 models in the catalog:
- Qwen3-Coder-30B (18.5 GB) [hot, coding] - Not downloaded
- Llama-3.1-8B (4.7 GB) [general] - Downloaded
- Qwen3-0.6B (0.4 GB) [hot, cpu, small] - Downloaded
```

---

### Schritt 4: Intelligente Empfehlungen

Fügen Sie das Tool `recommend_models()` innerhalb von `_register_tools()` nach `list_available_models` hinzu. Der Agent kann nun mithilfe der 70-%-Regel berechnen, welche Modelle in den Speicher Ihres Systems passen.

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

Führen Sie das Programm aus und fragen Sie "What size LLM can I run?":

```bash
python hardware_advisor_agent.py
```

**Beispielausgabe:**

```
You: What size LLM can I run?

Agent: With 32 GB RAM and 24 GB GPU, you can safely run models up to 22.4 GB!

Top recommendations:
1. Qwen3-Coder-30B (18.5 GB) - Fits in RAM and GPU
2. Llama-3.1-8B (4.7 GB) - Fits in RAM and GPU
```

---

### Schritt 5: Produktions-CLI

Ersetzen Sie den einfachen `__main__`-Block durch eine ausgereifte interaktive CLI. Dies fügt ein Banner, Beendigungsbefehle und eine verbesserte Fehlerbehandlung hinzu.

**Ersetzen Sie den gesamten Block `if __name__ == "__main__":`** durch:

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
### Abschließende Überprüfung

Ihre `hardware_advisor_agent.py` sollte jetzt alle diese Komponenten enthalten:

- [x] Imports: `from typing import Any, Dict` und `from gaia import Agent, tool`
- [x] `HardwareAdvisorAgent`-Klasse mit `__init__` und System-Prompt
- [x] `_get_gpu_info()`-Hilfsfunktion (Windows PowerShell + Linux lspci)
- [x] `get_hardware_info()`-Tool mit GPU-, NPU- und Betriebssystemfeldern
- [x] `list_available_models()`-Tool mit Labels und Größenanreicherung
- [x] `recommend_models()`-Tool mit 70%-Regel, fits_in_ram, fits_in_gpu
- [x] `main()`-Funktion mit interaktiver CLI

**Testen Sie diese Anfragen, um sicherzustellen, dass alles funktioniert:**

- „Welche Größe an LLM kann ich ausführen?“
- „Zeig mir meine Systemspezifikationen“
- „Welche Modelle sind verfügbar?“
- „Kann ich ein 30B-Modell ausführen?“

> **Tipp**: Die vollständige Implementierung finden Sie unter [hardware_advisor_agent.py](assets/hardware_advisor_agent.py).

## Nächste Schritte

- **Erkunden Sie die LemonadeClient-APIs** — Entdecken Sie weitere Funktionen zur System- und Modellverwaltung in der [LemonadeClient-SDK-Dokumentation](https://amd-gaia.ai/sdk/lemonade-client)
- **Sprachinteraktion hinzufügen** — Integrieren Sie Whisper ASR und Kokoro TTS, damit Nutzer Hardwarefragen per Sprache stellen können. Siehe den [Talk-Guide](https://amd-gaia.ai/guides/talk)
- **MCP-Unterstützung hinzufügen** — Stellen Sie den Hardware-Advisor als MCP-Server bereit, damit andere Tools ihn abfragen können. Siehe den [MCP-Guide](https://amd-gaia.ai/sdk/infrastructure/mcp)
- **Erweitern Sie die Empfehlungs-Engine** — Berücksichtigen Sie den GPU-VRAM für das Auslagern von Layern oder fügen Sie Benchmarking hinzu, um Tokens pro Sekunde zu schätzen
- **Erstellen Sie ein Multi-Agenten-System** — Kombinieren Sie den Hardware-Advisor mit einem Code-Agenten oder Chat-Agenten mithilfe des [Routing-Agenten](https://amd-gaia.ai/guides/routing)