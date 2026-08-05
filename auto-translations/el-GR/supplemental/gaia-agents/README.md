<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Μηχανική μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει ελεγχθεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένες οδηγίες, εντολές, στοιχεία λήψης, διαθεσιμότητα προϊόντων ή άλλο περιεχόμενο ενδέχεται να διαφέρουν ανάλογα με τη γλώσσα ή την περιοχή. Σε περίπτωση οποιασδήποτε ασυμφωνίας ή απόκλισης, υπερισχύει η πρωτότυπη αγγλική έκδοση του playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Επισκόπηση

Οι πράκτορες GAIA είναι βοηθοί τεχνητής νοημοσύνης που χρησιμοποιούν ένα τοπικό LLM για να συλλογίζονται και να καλούν εργαλεία που ορίζετε — σαν chatbots που μπορούν να αναλάβουν δράση. Εκτελούνται **100% τοπικά** χωρίς cloud API, χωρίς δεδομένα να εξέρχονται από το μηχάνημά σας και χωρίς να απαιτούνται κλειδιά API.

Σε αυτό το playbook, θα δημιουργήσετε έναν πράκτορα Hardware Advisor Agent που ανιχνεύει τη RAM, τη GPU και το NPU του συστήματός σας, ερωτά τον τοπικό κατάλογο μοντέλων και προτείνει ποια LLM μπορεί να εκτελέσει το μηχάνημά σας. Αποτελεί μια πρακτική εισαγωγή στο GAIA Agent SDK που παράγει κάτι άμεσα χρήσιμο.

## Τι Θα Μάθετε

- Πώς να δημιουργήσετε έναν πράκτορα GAIA με προσαρμοσμένα εργαλεία
- Χρήση του LemonadeClient SDK για ερωτήματα σχετικά με πληροφορίες συστήματος και καταλόγους μοντέλων
- Ανίχνευση GPU/NPU ανάλογα με την πλατφόρμα (Windows PowerShell και Linux lspci)
- Καθορισμός μεγέθους μοντέλου με βάση τη μνήμη χρησιμοποιώντας τον κανόνα 70%
- Δημιουργία διαδραστικού CLI για ερωτήματα υλικού σε φυσική γλώσσα

## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Ελέγξτε για Ενημερώσεις Λογισμικού
> **Σημείωση**: Αν το VS Code δεν είναι εγκατεστημένο, μπορείτε να το εγκαταστήσετε με το Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενων Λογισμικού

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

## Ξεκινώντας

Εκτελέστε πρώτα τον ολοκληρωμένο πράκτορα ώστε να δείτε τι θα δημιουργήσετε. Στη συνέχεια, θα εξηγήσουμε τον κώδικα βήμα προς βήμα.

### Εκτέλεση του Έτοιμου Παραδείγματος

Αυτό το playbook περιλαμβάνει τον πλήρη κώδικα [hardware_advisor_agent.py](assets/hardware_advisor_agent.py). Κατεβάστε τον σε έναν κατάλογο της επιλογής σας και εκτελέστε τον για να δείτε τον ολοκληρωμένο πράκτορα σε δράση:

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

**Δοκιμάστε να ρωτήσετε:** "What size LLM can I run?"

**Αναμενόμενη έξοδος:**

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

**Συγχαρητήρια** - δημιουργήσατε έναν πράκτορα! 

Το υπόλοιπο του playbook θα εξηγήσει πώς λειτουργεί κάθε μέρος του script, ώστε να το κατανοήσετε από την αρχή.
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


## Κατανόηση της Αρχιτεκτονικής

Ο Hardware Advisor Agent συνδυάζει τρία στοιχεία:

- **LemonadeClient SDK** — API πληροφοριών συστήματος και καταλόγου μοντέλων
- **Ανίχνευση ανάλογα με την πλατφόρμα** — Windows PowerShell / Linux lspci για πληροφορίες GPU
- **Υπολογισμοί μνήμης** — Κανόνας 70% για ασφαλή καθορισμό μεγέθους μοντέλου

Τα δεδομένα ρέουν μέσα από αυτά τα βήματα με τη σειρά: ερώτημα χρήστη → ο πράκτορας επιλέγει ένα εργαλείο → το εργαλείο καλεί το LemonadeClient + ανίχνευση OS → ο πράκτορας συνθέτει τα αποτελέσματα σε μια σύσταση.

### LemonadeClient SDK

Το LemonadeClient παρέχει ένα ενοποιημένο API για ανίχνευση συστήματος, διαθεσιμότητα NPU/GPU και ερωτήματα καταλόγου μοντέλων.

**Εισαγωγή και αρχικοποίηση:**

```python
from gaia.llm.lemonade_client import LemonadeClient

client = LemonadeClient(keep_alive=True)
```

**`get_system_info()`** — Επιστρέφει το OS, τον CPU, τη RAM και τη διαθεσιμότητα συσκευών:

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

**`list_models(show_all=True)`** — Επιστρέφει τον πλήρη κατάλογο μοντέλων:

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

**`get_model_info(model_id)`** — Επιστρέφει εκτιμήσεις μεγέθους για ένα συγκεκριμένο μοντέλο:

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

### Ανίχνευση GPU Ανάλογα με την Πλατφόρμα

Ο πράκτορας χρησιμοποιεί εντολές εγγενείς στο λειτουργικό σύστημα αντί για PyTorch για την ανίχνευση GPU. Αυτό λειτουργεί χωρίς εγκατεστημένους οδηγούς GPU, ανιχνεύει όλες τις GPU (όχι μόνο αυτές που υποστηρίζουν CUDA) και αποφεύγει τις βαριές εισαγωγές βιβλιοθηκών.

<!-- @os:windows -->

Στα Windows, ο πράκτορας χρησιμοποιεί το PowerShell για να κάνει ερωτήματα στο WMI:

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

Στο Linux, ο πράκτορας χρησιμοποιεί το lspci:

```python
result = subprocess.run(
    ["lspci"], capture_output=True, text=True, timeout=5
)
# Parse output for "VGA compatible controller" lines
# Note: Memory not available via lspci
```

<!-- @os:end -->

### Ο Κανόνας Μνήμης 70%

> **Κανόνας:** Το μέγεθος του μοντέλου πρέπει να είναι μικρότερο από το 70% της διαθέσιμης RAM, ώστε να παραμένει 30% περιθώριο για λειτουργίες συμπερασμού (KV cache, buffers επεξεργασίας batch, αιχμές μνήμης κατά την εκτέλεση).

```
System: 32 GB RAM
Max safe model size: 32 x 0.7 = 22.4 GB
30B model (~18.5 GB): Fits safely
70B model (~42 GB):   Too large
```

## Κωδικοποίηση του Πράκτορα Βήμα προς Βήμα (Προαιρετικό)

Θα δημιουργήσετε **ένα αρχείο** με το όνομα `hardware_advisor_agent.py` και θα προσθέτετε σταδιακά λειτουργίες. Κάθε βήμα βασίζεται στο προηγούμενο.

### Βήμα 1: Σκελετός Πράκτορα

Ξεκινήστε με μια ελάχιστη δομή πράκτορα — μόνο την κλάση και ένα βασικό system prompt. Ο πράκτορας δεν έχει ακόμη εργαλεία.

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

Εκτελέστε τον για να επαληθεύσετε:

```bash
python hardware_advisor_agent.py
```

Αναμενόμενη έξοδος:

```
Agent created successfully!
```

---

### Βήμα 2: Ανίχνευση GPU και Υλικού

Προσθέστε τη βοηθητική μέθοδο `_get_gpu_info()` και το εργαλείο `get_hardware_info()`. Αυτό κάνει τον πράκτορα διαδραστικό — τώρα μπορείτε να τον ερωτήσετε σχετικά με τις προδιαγραφές του συστήματος.

**Ενημερώστε τις εισαγωγές** στην κορυφή του αρχείου:

```python
from typing import Any, Dict

from gaia import Agent, tool
from gaia.llm.lemonade_client import LemonadeClient
```

**Προσθέστε τη βοηθητική `_get_gpu_info()`** μετά τη μέθοδο `_get_system_prompt()`:

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

**Αντικαταστήστε τη μέθοδο `_register_tools()`** με το εργαλείο `get_hardware_info`:

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

**Ενημερώστε το μπλοκ `__main__`** για να ενεργοποιήσετε διαδραστικό έλεγχο:

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

Εκτελέστε και δοκιμάστε να ρωτήσετε "Show me my system specs":

```bash
python hardware_advisor_agent.py
```

**Παράδειγμα εξόδου:**

```
You: Show me my system specs

Agent: Your system has excellent specs for running LLMs locally!
- 32 GB RAM
- AMD Radeon RX 7900 XTX with 24 GB VRAM
- Ryzen AI NPU for accelerated inference
```

---

### Βήμα 3: Κατάλογος Μοντέλων

Προσθέστε το εργαλείο `list_available_models()` μέσα στο `_register_tools()`, μετά τη συνάρτηση `get_hardware_info`. Τώρα ο πράκτορας μπορεί να σας πει ποια μοντέλα είναι διαθέσιμα.

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

Εκτελέστε και δοκιμάστε να ρωτήσετε "What models are available?":

```bash
python hardware_advisor_agent.py
```

**Παράδειγμα εξόδου:**

```
You: What models are available?

Agent: I found 15 models in the catalog:
- Qwen3-Coder-30B (18.5 GB) [hot, coding] - Not downloaded
- Llama-3.1-8B (4.7 GB) [general] - Downloaded
- Qwen3-0.6B (0.4 GB) [hot, cpu, small] - Downloaded
```

---

### Βήμα 4: Έξυπνες Συστάσεις

Προσθέστε το εργαλείο `recommend_models()` μέσα στο `_register_tools()`, μετά το `list_available_models`. Ο πράκτορας μπορεί τώρα να υπολογίσει ποια μοντέλα χωρούν στη μνήμη του συστήματός σας χρησιμοποιώντας τον κανόνα 70%.

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

Εκτελέστε και δοκιμάστε να ρωτήσετε "What size LLM can I run?":

```bash
python hardware_advisor_agent.py
```

**Παράδειγμα εξόδου:**

```
You: What size LLM can I run?

Agent: With 32 GB RAM and 24 GB GPU, you can safely run models up to 22.4 GB!

Top recommendations:
1. Qwen3-Coder-30B (18.5 GB) - Fits in RAM and GPU
2. Llama-3.1-8B (4.7 GB) - Fits in RAM and GPU
```

---

### Βήμα 5: CLI Παραγωγής

Αντικαταστήστε το απλό μπλοκ `__main__` με ένα βελτιωμένο διαδραστικό CLI. Αυτό προσθέτει ένα banner, εντολές εξόδου και καλύτερη διαχείριση σφαλμάτων.

**Αντικαταστήστε ολόκληρο το μπλοκ `if __name__ == "__main__":`** με:

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
### Τελική Επαλήθευση

Το `hardware_advisor_agent.py` θα πρέπει τώρα να διαθέτει όλα αυτά τα στοιχεία:

- [x] Εισαγωγές: `from typing import Any, Dict` και `from gaia import Agent, tool`
- [x] Κλάση `HardwareAdvisorAgent` με `__init__` και system prompt
- [x] Βοηθητική συνάρτηση `_get_gpu_info()` (Windows PowerShell + Linux lspci)
- [x] Εργαλείο `get_hardware_info()` με πεδία GPU, NPU και OS
- [x] Εργαλείο `list_available_models()` με ετικέτες και εμπλουτισμό μεγέθους
- [x] Εργαλείο `recommend_models()` με τον κανόνα 70%, `fits_in_ram`, `fits_in_gpu`
- [x] Συνάρτηση `main()` με διαδραστικό CLI

**Δοκιμάστε αυτά τα ερωτήματα για να επιβεβαιώσετε ότι όλα λειτουργούν:**

- "What size LLM can I run?"
- "Show me my system specs"
- "What models are available?"
- "Can I run a 30B model?"

> **Συμβουλή**: Η πλήρης υλοποίηση είναι διαθέσιμη στο [hardware_advisor_agent.py](assets/hardware_advisor_agent.py).

## Επόμενα Βήματα

- **Εξερευνήστε τα APIs του LemonadeClient** — Ανακαλύψτε περισσότερες δυνατότητες διαχείρισης συστήματος και μοντέλων στην τεκμηρίωση [LemonadeClient SDK documentation](https://amd-gaia.ai/sdk/lemonade-client)
- **Προσθέστε φωνητική αλληλεπίδραση** — Ενσωματώστε τα Whisper ASR και Kokoro TTS ώστε οι χρήστες να μπορούν να κάνουν ερωτήσεις για το hardware μιλώντας. Δείτε τον [Talk guide](https://amd-gaia.ai/guides/talk)
- **Προσθέστε υποστήριξη MCP** — Εκθέστε τον hardware advisor ως διακομιστή MCP ώστε άλλα εργαλεία να μπορούν να τον ερωτούν. Δείτε τον [MCP guide](https://amd-gaia.ai/sdk/infrastructure/mcp)
- **Επεκτείνετε τη μηχανή συστάσεων** — Λάβετε υπόψη τη VRAM της GPU για offloading επιπέδων, ή προσθέστε benchmarking για την εκτίμηση tokens-per-second
- **Δημιουργήστε ένα σύστημα πολλαπλών agents** — Συνδυάστε τον hardware advisor με έναν code agent ή chat agent χρησιμοποιώντας τον [Routing Agent](https://amd-gaia.ai/guides/routing)