<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

ตัวแทน GAIA (GAIA agents) คือผู้ช่วย AI ที่ใช้ LLM ในเครื่องเพื่อการให้เหตุผลและเรียกใช้เครื่องมือที่คุณกำหนด — เหมือนแชตบอตที่สามารถลงมือทำสิ่งต่าง ๆ ได้ ตัวแทนเหล่านี้ทำงาน **ในเครื่อง 100%** โดยไม่ต้องใช้ cloud API ไม่มีข้อมูลหลุดออกจากเครื่องของคุณ และไม่ต้องใช้ API keys

ในคู่มือนี้ คุณจะสร้าง Hardware Advisor Agent ที่ตรวจจับ RAM, GPU และ NPU ของระบบ ทำการสอบถาม model catalog ในเครื่อง และแนะนำว่าเครื่องของคุณสามารถรัน LLM ตัวใดได้บ้าง นี่คือการแนะนำเชิงปฏิบัติสู่ GAIA Agent SDK ที่ให้ผลลัพธ์ที่นำไปใช้ได้จริงทันที

## สิ่งที่คุณจะได้เรียนรู้

- วิธีสร้างตัวแทน GAIA พร้อมเครื่องมือที่กำหนดเอง
- การใช้ LemonadeClient SDK เพื่อสอบถามข้อมูลระบบและ model catalog
- การตรวจจับ GPU/NPU เฉพาะแพลตฟอร์ม (Windows PowerShell และ Linux lspci)
- การกำหนดขนาดโมเดลตามหน่วยความจำโดยใช้กฎ 70%
- การสร้าง CLI แบบโต้ตอบสำหรับการสอบถามฮาร์ดแวร์ด้วยภาษาธรรมชาติ

<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ผ่าน Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

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

## เริ่มต้นใช้งาน

เริ่มจากรันตัวแทนที่เสร็จสมบูรณ์ก่อนเพื่อให้เห็นว่าคุณกำลังจะสร้างอะไร จากนั้นเราจะอธิบายโค้ดทีละขั้นตอน

### รันตัวอย่างที่สร้างไว้ล่วงหน้า

คู่มือนี้มีไฟล์ [hardware_advisor_agent.py](assets/hardware_advisor_agent.py) ฉบับสมบูรณ์ ดาวน์โหลดไปไว้ในไดเรกทอรีที่คุณต้องการ แล้วรันเพื่อดูตัวแทนที่เสร็จสมบูรณ์ทำงาน:

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

**ลองถาม:** "What size LLM can I run?"

**ผลลัพธ์ที่คาดหวัง:**

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

**ยินดีด้วย** - คุณได้สร้างตัวแทนสำเร็จแล้ว! 

ส่วนที่เหลือของคู่มือนี้จะอธิบายว่าแต่ละส่วนของสคริปต์ทำงานอย่างไร เพื่อให้คุณเข้าใจตั้งแต่พื้นฐาน
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


## ทำความเข้าใจสถาปัตยกรรม

Hardware Advisor Agent ผสานรวมสามองค์ประกอบ:

- **LemonadeClient SDK** — API สำหรับข้อมูลระบบและ model catalog
- **การตรวจจับเฉพาะแพลตฟอร์ม** — Windows PowerShell / Linux lspci สำหรับข้อมูล GPU
- **การคำนวณหน่วยความจำ** — กฎ 70% สำหรับการกำหนดขนาดโมเดลอย่างปลอดภัย

ข้อมูลไหลผ่านขั้นตอนเหล่านี้ตามลำดับ: คำถามจากผู้ใช้ → ตัวแทนเลือกเครื่องมือ → เครื่องมือเรียกใช้ LemonadeClient + การตรวจจับ OS → ตัวแทนสังเคราะห์ผลลัพธ์เป็นคำแนะนำ

### LemonadeClient SDK

LemonadeClient มี API แบบรวมศูนย์สำหรับการตรวจจับระบบ ความพร้อมใช้งานของ NPU/GPU และการสอบถาม model catalog

**นำเข้าและเริ่มต้นใช้งาน:**

```python
from gaia.llm.lemonade_client import LemonadeClient

client = LemonadeClient(keep_alive=True)
```

**`get_system_info()`** — ส่งคืน OS, CPU, RAM และความพร้อมใช้งานของอุปกรณ์:

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

**`list_models(show_all=True)`** — ส่งคืน model catalog แบบเต็ม:

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

**`get_model_info(model_id)`** — ส่งคืนค่าประมาณขนาดสำหรับโมเดลที่ระบุ:

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

### การตรวจจับ GPU เฉพาะแพลตฟอร์ม

ตัวแทนใช้คำสั่งดั้งเดิมของ OS แทนที่จะใช้ PyTorch ในการตรวจจับ GPU วิธีนี้ทำงานได้โดยไม่ต้องติดตั้ง GPU driver ตรวจจับ GPU ได้ทุกตัว (ไม่ใช่เฉพาะที่รองรับ CUDA) และหลีกเลี่ยงการนำเข้าไลบรารีขนาดใหญ่

<!-- @os:windows -->

บน Windows ตัวแทนใช้ PowerShell เพื่อสอบถาม WMI:

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

บน Linux ตัวแทนใช้ lspci:

```python
result = subprocess.run(
    ["lspci"], capture_output=True, text=True, timeout=5
)
# Parse output for "VGA compatible controller" lines
# Note: Memory not available via lspci
```

<!-- @os:end -->

### กฎหน่วยความจำ 70%

> **กฎ:** ขนาดโมเดลควรน้อยกว่า 70% ของ RAM ที่มีอยู่ เพื่อเหลือพื้นที่สำรอง 30% สำหรับการทำงานของกระบวนการอนุมาน (KV cache, บัฟเฟอร์การประมวลผลแบบแบตช์, การเพิ่มขึ้นของหน่วยความจำขณะรันไทม์)

```
System: 32 GB RAM
Max safe model size: 32 x 0.7 = 22.4 GB
30B model (~18.5 GB): Fits safely
70B model (~42 GB):   Too large
```

## การเขียนโค้ดตัวแทนทีละขั้นตอน (ทางเลือกเสริม)

คุณจะสร้าง **ไฟล์เดียว** ชื่อ `hardware_advisor_agent.py` และเพิ่มคุณสมบัติทีละขั้นตอน แต่ละขั้นตอนต่อยอดจากขั้นตอนก่อนหน้า

### ขั้นตอนที่ 1: โครงร่างตัวแทน

เริ่มต้นด้วยโครงสร้างตัวแทนขั้นต่ำ — เพียงแค่คลาสและ system prompt พื้นฐาน ตัวแทนยังไม่มีเครื่องมือใด ๆ ในขั้นนี้

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

รันเพื่อตรวจสอบ:

```bash
python hardware_advisor_agent.py
```

ผลลัพธ์ที่คาดหวัง:

```
Agent created successfully!
```

---

### ขั้นตอนที่ 2: การตรวจจับ GPU และฮาร์ดแวร์

เพิ่มเมธอดช่วยเหลือ `_get_gpu_info()` และเครื่องมือ `get_hardware_info()` วิธีนี้ทำให้ตัวแทนสามารถโต้ตอบได้ — ตอนนี้คุณสามารถสอบถามเกี่ยวกับสเปกระบบได้แล้ว

**อัปเดตส่วนการนำเข้า (imports)** ที่ด้านบนของไฟล์:

```python
from typing import Any, Dict

from gaia import Agent, tool
from gaia.llm.lemonade_client import LemonadeClient
```

**เพิ่มเมธอดช่วยเหลือ `_get_gpu_info()`** หลังเมธอด `_get_system_prompt()`:

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

**แทนที่เมธอด `_register_tools()`** ด้วยเครื่องมือ `get_hardware_info`:

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

**อัปเดตบล็อก `__main__`** เพื่อเปิดใช้งานการทดสอบแบบโต้ตอบ:

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

รันแล้วลองถามว่า "Show me my system specs":

```bash
python hardware_advisor_agent.py
```

**ตัวอย่างผลลัพธ์:**

```
You: Show me my system specs

Agent: Your system has excellent specs for running LLMs locally!
- 32 GB RAM
- AMD Radeon RX 7900 XTX with 24 GB VRAM
- Ryzen AI NPU for accelerated inference
```

---

### ขั้นตอนที่ 3: Model Catalog

เพิ่มเครื่องมือ `list_available_models()` ไว้ภายใน `_register_tools()` ต่อจากฟังก์ชัน `get_hardware_info` ตอนนี้ตัวแทนสามารถบอกได้ว่ามีโมเดลใดบ้างที่พร้อมใช้งาน

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

รันแล้วลองถามว่า "What models are available?":

```bash
python hardware_advisor_agent.py
```

**ตัวอย่างผลลัพธ์:**

```
You: What models are available?

Agent: I found 15 models in the catalog:
- Qwen3-Coder-30B (18.5 GB) [hot, coding] - Not downloaded
- Llama-3.1-8B (4.7 GB) [general] - Downloaded
- Qwen3-0.6B (0.4 GB) [hot, cpu, small] - Downloaded
```

---

### ขั้นตอนที่ 4: คำแนะนำอัจฉริยะ

เพิ่มเครื่องมือ `recommend_models()` ไว้ภายใน `_register_tools()` ต่อจาก `list_available_models` ตอนนี้ตัวแทนสามารถคำนวณได้ว่าโมเดลใดเหมาะกับหน่วยความจำของระบบคุณโดยใช้กฎ 70%

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

รันแล้วลองถามว่า "What size LLM can I run?":

```bash
python hardware_advisor_agent.py
```

**ตัวอย่างผลลัพธ์:**

```
You: What size LLM can I run?

Agent: With 32 GB RAM and 24 GB GPU, you can safely run models up to 22.4 GB!

Top recommendations:
1. Qwen3-Coder-30B (18.5 GB) - Fits in RAM and GPU
2. Llama-3.1-8B (4.7 GB) - Fits in RAM and GPU
```

---

### ขั้นตอนที่ 5: CLI สำหรับใช้งานจริง

แทนที่บล็อก `__main__` แบบง่าย ๆ ด้วย CLI แบบโต้ตอบที่สมบูรณ์ยิ่งขึ้น ซึ่งจะเพิ่มแบนเนอร์ คำสั่งออกจากโปรแกรม และการจัดการข้อผิดพลาดที่ดีขึ้น

**แทนที่บล็อก `if __name__ == "__main__":` ทั้งหมด** ด้วย:

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
### การตรวจสอบขั้นสุดท้าย

`hardware_advisor_agent.py` ของคุณควรมีองค์ประกอบทั้งหมดต่อไปนี้แล้ว:

- [x] การ import: `from typing import Any, Dict` และ `from gaia import Agent, tool`
- [x] คลาส `HardwareAdvisorAgent` พร้อม `__init__` และ system prompt
- [x] ฟังก์ชันช่วยเหลือ `_get_gpu_info()` (Windows PowerShell + Linux lspci)
- [x] tool `get_hardware_info()` พร้อมฟิลด์ GPU, NPU และ OS
- [x] tool `list_available_models()` พร้อม labels และการเพิ่มข้อมูลขนาด
- [x] tool `recommend_models()` พร้อมกฎ 70%, fits_in_ram, fits_in_gpu
- [x] ฟังก์ชัน `main()` พร้อม CLI แบบโต้ตอบ

**ทดสอบคำถามเหล่านี้เพื่อยืนยันว่าทุกอย่างทำงานได้:**

- "What size LLM can I run?"
- "Show me my system specs"
- "What models are available?"
- "Can I run a 30B model?"

> **เคล็ดลับ**: การใช้งานฉบับสมบูรณ์มีให้ที่ [hardware_advisor_agent.py](assets/hardware_advisor_agent.py)

## ขั้นตอนถัดไป

- **สำรวจ LemonadeClient APIs** — ค้นพบความสามารถในการจัดการระบบและโมเดลเพิ่มเติมได้ที่ [เอกสาร LemonadeClient SDK](https://amd-gaia.ai/sdk/lemonade-client)
- **เพิ่มการโต้ตอบด้วยเสียง** — รวม Whisper ASR และ Kokoro TTS เพื่อให้ผู้ใช้สามารถถามคำถามเกี่ยวกับฮาร์ดแวร์ด้วยการพูด ดู [คู่มือ Talk](https://amd-gaia.ai/guides/talk)
- **เพิ่มการสนับสนุน MCP** — เปิดใช้งาน hardware advisor เป็น MCP server เพื่อให้เครื่องมืออื่นสามารถสอบถามข้อมูลได้ ดู [คู่มือ MCP](https://amd-gaia.ai/sdk/infrastructure/mcp)
- **ขยายระบบแนะนำ** — นำ GPU VRAM มาพิจารณาสำหรับการ offload layers หรือเพิ่มการทำ benchmarking เพื่อประมาณค่า tokens-per-second
- **สร้างระบบมัลติเอเจนต์** — รวม hardware advisor เข้ากับ code agent หรือ chat agent โดยใช้ [Routing Agent](https://amd-gaia.ai/guides/routing)