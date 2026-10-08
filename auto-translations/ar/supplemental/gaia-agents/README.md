<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## نظرة عامة

وكلاء GAIA هم مساعدون يعتمدون على الذكاء الاصطناعي يستخدمون نموذج لغة محلي (LLM) للاستدلال واستدعاء الأدوات التي تحددها — مثل روبوتات الدردشة القادرة على اتخاذ إجراءات فعلية. تعمل هذه الوكلاء **محليًا بنسبة 100%** دون الحاجة إلى واجهات برمجة تطبيقات سحابية، ودون خروج أي بيانات من جهازك، ودون الحاجة إلى مفاتيح API.

في هذا الدليل التطبيقي، ستقوم ببناء وكيل مستشار الأجهزة (Hardware Advisor Agent) الذي يكتشف ذاكرة الوصول العشوائي (RAM) وGPU وNPU في نظامك، ويستعلم عن كتالوج النماذج المحلي، ويوصي بالنماذج اللغوية (LLMs) التي يمكن لجهازك تشغيلها. إنه مقدمة عملية لحزمة تطوير برامج GAIA Agent تنتج شيئًا مفيدًا فورًا.

## ما ستتعلمه

- كيفية إنشاء وكيل GAIA بأدوات مخصصة
- استخدام حزمة تطوير البرامج LemonadeClient للاستعلام عن معلومات النظام وكتالوجات النماذج
- اكتشاف GPU/NPU الخاص بالمنصة (Windows PowerShell وLinux lspci)
- تحديد حجم النموذج بناءً على الذاكرة باستخدام قاعدة الـ 70%
- بناء واجهة سطر أوامر (CLI) تفاعلية للاستعلامات باللغة الطبيعية حول الأجهزة

<!-- @device:halo_box,halo,stx,krk -->
## إعداد تهيئة الذاكرة

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج
> **ملاحظة**: إذا لم يكن VS Code مثبتًا، يمكنك تثبيته من خلال Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرامج

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

## البدء

احصل أولًا على الوكيل الجاهز وشغّله لترى ما ستقوم ببنائه. بعد ذلك، سنستعرض الكود خطوة بخطوة.

### تشغيل المثال الجاهز

يتضمن هذا الدليل التطبيقي الوكيل الكامل [hardware_advisor_agent.py](assets/hardware_advisor_agent.py). قم بتنزيله إلى دليل من اختيارك وشغّله لترى الوكيل النهائي أثناء عمله:

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

**جرّب أن تسأل:** "What size LLM can I run?"

**الناتج المتوقع:**

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

**تهانينا** - لقد بنيت وكيلًا!

سيشرح بقية هذا الدليل التطبيقي كيفية عمل كل جزء من السكربت، حتى تتمكن من فهمه من الأساس.
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


## فهم البنية المعمارية

يجمع وكيل مستشار الأجهزة بين ثلاثة مكونات:

- **حزمة تطوير البرامج LemonadeClient** — واجهات برمجة تطبيقات لمعلومات النظام وكتالوج النماذج
- **الاكتشاف الخاص بالمنصة** — Windows PowerShell / Linux lspci لمعلومات GPU
- **حسابات الذاكرة** — قاعدة الـ 70% لتحديد حجم النموذج بأمان

تتدفق البيانات عبر هذه المكونات بالتسلسل التالي: استعلام المستخدم ← يختار الوكيل أداة ← تستدعي الأداة LemonadeClient + اكتشاف نظام التشغيل ← يقوم الوكيل بتجميع النتائج في توصية.

### حزمة تطوير البرامج LemonadeClient

توفر LemonadeClient واجهة برمجة تطبيقات موحدة لاكتشاف النظام، وتوافر NPU/GPU، واستعلامات كتالوج النماذج.

**الاستيراد والتهيئة:**

```python
from gaia.llm.lemonade_client import LemonadeClient

client = LemonadeClient(keep_alive=True)
```

**`get_system_info()`** — تُرجع نظام التشغيل، والمعالج (CPU)، وذاكرة الوصول العشوائي (RAM)، وتوافر الأجهزة:

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

**`list_models(show_all=True)`** — تُرجع كتالوج النماذج الكامل:

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

**`get_model_info(model_id)`** — تُرجع تقديرات الحجم لنموذج معين:

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

### الاكتشاف الخاص بالمنصة لـ GPU

يستخدم الوكيل أوامر أصلية خاصة بنظام التشغيل بدلًا من PyTorch لاكتشاف GPU. يعمل هذا الأسلوب دون الحاجة إلى تثبيت برامج تشغيل GPU، ويكتشف جميع وحدات GPU (وليس فقط تلك المتوافقة مع CUDA)، ويتجنب استيراد المكتبات الثقيلة.

<!-- @os:windows -->

في Windows، يستخدم الوكيل PowerShell للاستعلام عن WMI:

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

في Linux، يستخدم الوكيل lspci:

```python
result = subprocess.run(
    ["lspci"], capture_output=True, text=True, timeout=5
)
# Parse output for "VGA compatible controller" lines
# Note: Memory not available via lspci
```

<!-- @os:end -->

### قاعدة الذاكرة بنسبة 70%

> **القاعدة:** يجب أن يكون حجم النموذج أقل من 70% من ذاكرة الوصول العشوائي (RAM) المتاحة لترك 30% كهامش إضافي لعمليات الاستدلال (ذاكرة التخزين المؤقت KV، ومخازن معالجة الدُفعات، وارتفاعات ذاكرة وقت التشغيل المفاجئة).

```
System: 32 GB RAM
Max safe model size: 32 x 0.7 = 22.4 GB
30B model (~18.5 GB): Fits safely
70B model (~42 GB):   Too large
```

## كتابة كود الوكيل خطوة بخطوة (اختياري)

ستقوم بإنشاء **ملف واحد** باسم `hardware_advisor_agent.py` وتضيف الميزات تدريجيًا. تعتمد كل خطوة على الخطوة السابقة.

### الخطوة 1: الهيكل الأساسي للوكيل

ابدأ ببنية أساسية بسيطة للوكيل — فقط الفئة (class) وتوجيه نظام بسيط. لا يمتلك الوكيل أي أدوات بعد.

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

شغّله للتحقق:

```bash
python hardware_advisor_agent.py
```

الناتج المتوقع:

```
Agent created successfully!
```

---

### الخطوة 2: اكتشاف GPU والأجهزة

أضف الدالة المساعدة `_get_gpu_info()` والأداة `get_hardware_info()`. هذا يجعل الوكيل تفاعليًا — يمكنك الآن استعلامه عن مواصفات النظام.

**حدّث عبارات الاستيراد** في أعلى الملف:

```python
from typing import Any, Dict

from gaia import Agent, tool
from gaia.llm.lemonade_client import LemonadeClient
```

**أضف الدالة المساعدة `_get_gpu_info()`** بعد الدالة `_get_system_prompt()`:

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

**استبدل الدالة `_register_tools()`** بالأداة `get_hardware_info`:

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

**حدّث الكتلة `__main__`** لتمكين الاختبار التفاعلي:

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

شغّله وجرّب أن تسأل "Show me my system specs":

```bash
python hardware_advisor_agent.py
```

**مثال على الناتج:**

```
You: Show me my system specs

Agent: Your system has excellent specs for running LLMs locally!
- 32 GB RAM
- AMD Radeon RX 7900 XTX with 24 GB VRAM
- Ryzen AI NPU for accelerated inference
```

---

### الخطوة 3: كتالوج النماذج

أضف الأداة `list_available_models()` داخل `_register_tools()`، بعد الدالة `get_hardware_info`. يمكن للوكيل الآن إخبارك بالنماذج المتوفرة.

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

شغّله وجرّب أن تسأل "What models are available?":

```bash
python hardware_advisor_agent.py
```

**مثال على الناتج:**

```
You: What models are available?

Agent: I found 15 models in the catalog:
- Qwen3-Coder-30B (18.5 GB) [hot, coding] - Not downloaded
- Llama-3.1-8B (4.7 GB) [general] - Downloaded
- Qwen3-0.6B (0.4 GB) [hot, cpu, small] - Downloaded
```

---

### الخطوة 4: التوصيات الذكية

أضف الأداة `recommend_models()` داخل `_register_tools()`، بعد `list_available_models`. يمكن للوكيل الآن حساب النماذج التي تناسب ذاكرة نظامك باستخدام قاعدة الـ 70%.

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

شغّله وجرّب أن تسأل "What size LLM can I run?":

```bash
python hardware_advisor_agent.py
```

**مثال على الناتج:**

```
You: What size LLM can I run?

Agent: With 32 GB RAM and 24 GB GPU, you can safely run models up to 22.4 GB!

Top recommendations:
1. Qwen3-Coder-30B (18.5 GB) - Fits in RAM and GPU
2. Llama-3.1-8B (4.7 GB) - Fits in RAM and GPU
```

---

### الخطوة 5: واجهة سطر أوامر جاهزة للإنتاج

استبدل الكتلة البسيطة `__main__` بواجهة سطر أوامر تفاعلية مصقولة. يضيف هذا شعارًا (banner)، وأوامر للخروج، ومعالجة أفضل للأخطاء.

**استبدل الكتلة الكاملة `if __name__ == "__main__":`** بما يلي:

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
### التحقق النهائي

يجب أن تحتوي `hardware_advisor_agent.py` الخاصة بك الآن على جميع هذه المكونات:

- [x] الاستيرادات: `from typing import Any, Dict` و `from gaia import Agent, tool`
- [x] فئة `HardwareAdvisorAgent` مع `__init__` وموجه النظام
- [x] مساعد `_get_gpu_info()` (PowerShell على Windows + lspci على Linux)
- [x] أداة `get_hardware_info()` مع حقول GPU وNPU ونظام التشغيل
- [x] أداة `list_available_models()` مع التسميات وإثراء الحجم
- [x] أداة `recommend_models()` مع قاعدة 70%، و`fits_in_ram`، و`fits_in_gpu`
- [x] دالة `main()` مع واجهة سطر أوامر تفاعلية

**اختبر هذه الاستعلامات للتأكد من أن كل شيء يعمل:**

- "ما حجم LLM الذي يمكنني تشغيله؟"
- "أظهر لي مواصفات نظامي"
- "ما هي النماذج المتوفرة؟"
- "هل يمكنني تشغيل نموذج 30B؟"

> **نصيحة**: التنفيذ الكامل متوفر في [hardware_advisor_agent.py](assets/hardware_advisor_agent.py).

## الخطوات التالية

- **استكشاف واجهات برمجة التطبيقات الخاصة بـ LemonadeClient** — اكتشف المزيد من إمكانيات إدارة النظام والنماذج في [وثائق LemonadeClient SDK](https://amd-gaia.ai/sdk/lemonade-client)
- **إضافة التفاعل الصوتي** — ادمج Whisper ASR وKokoro TTS للسماح للمستخدمين بطرح أسئلة عن الأجهزة عن طريق التحدث. راجع [دليل Talk](https://amd-gaia.ai/guides/talk)
- **إضافة دعم MCP** — اعرض مستشار الأجهزة كخادم MCP حتى تتمكن الأدوات الأخرى من الاستعلام عنه. راجع [دليل MCP](https://amd-gaia.ai/sdk/infrastructure/mcp)
- **توسيع محرك التوصيات** — خذ في الاعتبار ذاكرة GPU VRAM لتفريغ الطبقات، أو أضف قياس الأداء لتقدير عدد الرموز في الثانية
- **بناء نظام متعدد الوكلاء** — ادمج مستشار الأجهزة مع وكيل برمجي أو وكيل محادثة باستخدام [Routing Agent](https://amd-gaia.ai/guides/routing)