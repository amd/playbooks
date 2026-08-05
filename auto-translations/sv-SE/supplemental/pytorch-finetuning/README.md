<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Översikt

Den här handledningen innehåller steg-för-steg-exempel för att finjustera en stor språkmodell (LLM) med PyTorch och ROCm. Den täcker flera tekniker, från vanlig finjustering till minneseffektiva PEFT-strategier (Parameter-Efficient Fine-Tuning), så att du enkelt kan anpassa modeller efter dina behov.

**Modell som används**: google/gemma-3-4b-it  *(se [Aktivera HF-autentisering](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) om den är spärrad)*  
**Hårdvara**: AMD Radeon™-GPU med ROCm-stöd  
**Ramverk**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Obs:** 
> - Fullständig finjustering kräver minst **64 GB systemminne (RAM)**, med minst **32 GB av det tillgängligt för GPU:n** (32 GB är en del av de 64 GB, inte utöver dem).
> - Du kan även prova andra modellarkitekturer, inklusive **GPT-OSS-20B**, genom att ersätta modellen i de medföljande träningsskripten.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Obs:** LoRA- och QLoRA-finjustering kräver minst **32 GB systemminne (RAM)**, med minst **16 GB av det tillgängligt för GPU:n** (16 GB är en del av de 32 GB, inte utöver dem).
<!-- @os:end -->

<!-- @os:windows -->
> **Obs:** LoRA-finjustering kräver minst **32 GB systemminne (RAM)**, med minst **16 GB av det tillgängligt för GPU:n** (16 GB är en del av de 32 GB, inte utöver dem).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Obs:** LoRA- och QLoRA-finjustering kräver ett grafikkort med minst **16 GB dedikerat GPU-minne** och **32 GB systemminne**.
> - På Linux körs träningen helt i grafikkortets dedikerade VRAM.
> - Det växlar inte över till delat GPU-minne (systemminne) när VRAM tar slut.
> - Kort med mindre än 16 GB dedikerat VRAM kommer att få slut på minne under träningen på Linux, även om systemet har gott om RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Obs:** LoRA-finjustering kräver minst **16 GB totalt GPU-minne** och **32 GB systemminne**.
> - På Windows kombinerar det totala GPU-minnet grafikkortets dedikerade VRAM med delat GPU-minne (lånat från systemminnet).
> - Därför kan kort med mindre än 16 GB dedikerat VRAM ändå köra den här spelboken genom att använda delat GPU-minne för att kompensera för skillnaden.
<!-- @os:end -->
<!-- @device:end -->

## Vad du kommer att lära dig

- Hur du finjusterar en LLM med LoRA, QLoRA och fullständig finjustering med PyTorch och ROCm
- Hur du sparar och driftsätter din finjusterade modell
- Hur du övervakar träning och felsöker vanliga problem

## Ställa in minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera om det finns programvaruuppdateringar
> **Obs**: Om VS Code inte är installerat kan du installera det med Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installera nödvändig programvara

#### Skapa en virtuell miljö

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
```bash
sudo apt update 
sudo apt install -y python3-venv 
python3 -m venv finetune-venv --system-site-packages 
source finetune-venv/bin/activate 
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Ge din användare åtkomst till GPU-enheter** (logga ut och in igen för att detta ska träda i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv finetune-venv
source finetune-venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Installera grundläggande beroenden
<!-- @require:pytorch -->

#### Ytterligare beroenden

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Endast kärnpaketen testas och stöds här. **bitsandbytes stöds inte väl på Windows**, så Windows-installationen utelämnar det; använd LoRA eller fullständig finjustering på Windows (QLoRA kräver bitsandbytes och är avsett för Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Aktivera HF-autentisering (spärrade eller anpassade / ej förinstallerade modeller)

I det här exemplet använder vi **google/gemma-3-4b-it**, som är en **spärrad** modell. Du måste acceptera modellens villkor på Hugging Face och sedan autentisera dig så att träningsskripten kan hämta den.

1. **Acceptera licensen:** Öppna [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), logga in (eller skapa ett konto) och acceptera licensen/villkoren på modellsidan (t.ex. ”Agree and access repository”).
2. **Installera och logga in:** Installera Hugging Face CLI och kör sedan standardinloggningen:

```bash
pip install huggingface_hub
hf auth login
```

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['train_qlora.py', 'train_lora.py', 'train_full_finetuning.py']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in scripts:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
from trl import SFTTrainer

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=verify-package-version timeout=60 hidden=True setup=activate-venv -->
```python
import importlib.metadata as md

pkgs = [
    "torch", "transformers", "trl", "peft", "accelerate",
    "datasets", "safetensors", "fsspec", "bitsandbytes",
    "huggingface_hub", "tokenizers",
]
for p in pkgs:
    try:
        print(f"{p}: {md.version(p)}")
    except md.PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
```
<!-- @test:end -->

<!-- @test:id=quick-train-lora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=quick-train-qlora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_qlora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=quick-train-full-finetuning timeout=1200 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_full_finetuning.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @device:end -->
---

## Förstå teknikerna

### Vad är LoRA?

**LoRA (Low-Rank Adaptation)** håller basmodellen fryst och tränar bara små ”adapter”-matriser som läggs till i vissa lager. 

- **Nyckelidén**: istället för att uppdatera en enorm viktmatris med miljontals parametrar lär vi oss en lågrangsuppdatering (två små matriser vars produkt har betydligt färre parametrar). Det ger en stor minskning av antalet tränbara parametrar och VRAM samtidigt som det mesta av kvaliteten från fullständig finjustering bevaras.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Vad är QLoRA?

**QLoRA** kombinerar **4-bitars kvantisering** med **LoRA**. Basmodellen laddas i 4-bitarsformat (stora minnesbesparingar), och endast LoRA-adaptrarna tränas med högre precision. Du får alltså parametereffektiviteten från LoRA plus betydligt lägre VRAM-användning, med en liten kvalitetsavvägning jämfört med fullprecisions-LoRA. Observera att 4-bitars kvantisering kan orsaka numerisk instabilitet (förlusttoppar eller NaN-värden), så användare kan ofta föredra **LoRA** om tillräckligt med VRAM finns tillgängligt.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Obs**: För MXFP4-basmodeller som `openai/gpt-oss-20b` rekommenderar vi att använda **LoRA** (`train_lora.py`) istället för QLoRA. QLoRA-skriptets `bitsandbytes`-baserade 4-bitars sökväg dekvantiserar vanligtvis MXFP4-vikter till BF16, vilket gör att körningen beter sig som vanlig LoRA. Native MXFP4 kräver `bitsandbytes` byggt från källkod plus en matchande Transformers/Triton/kernels-stack. Se [Transformers MXFP4-dokumentationen](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Välj din metod

| Metod | Minne | Hastighet | Kvalitet | Bäst för |
|--------|--------|-------|---------|----------|
| **QLoRA** (endast Linux) | 12-16GB | Snabbast | 90-95% | Låg minnesanvändning |
| **LoRA** | 24-32GB | Snabb | 95-98% | Balanserad metod |
| **Full** | 80GB+ | Långsammast | 100% | Maximal kvalitet |

### 3. Kör träning

**Dataset och vad modellen lär sig**  
Skripten omvandlar datasetet till chattexempel. Till exempel använder QLoRA-skriptet **Abirate/english_quotes**: varje exempel blir ett användare–assistent-par som:

- **Användare:** ”Ge mig ett citat om: &lt;tag&gt;”
- **Assistent:** ”&lt;citat&gt; – &lt;författare&gt;”

Finjusteringen lär modellen att svara på uppmaningar som ber om citat om ett ämne och att returnera dem i formatet `<quote text> - <author>`. LoRA- och full-finjusteringsskripten använder **databricks/databricks-dolly-15k** (generella instruktions-/svarspar), så den exakta uppgiften varierar beroende på skript; idén är densamma - anpassa modellen till ditt valda dataset och format.

Nedan finns en sammanfattning av de tillgängliga träningsmetoderna. Varje metod länkar till sitt skript och ger en kort beskrivning för att välja rätt tillvägagångssätt.

| Skript                           | Metod            | Beskrivning                                                                                                         | Typiskt VRAM | Rekommenderas för                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Tränar små adaptermatriser samtidigt som basmodellen fryses. 3–5x snabbare; ~95–98% av full kvalitet.                         | 24–32GB      | Avancerade användare; flera adaptrar; mer VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(endast Linux)*             | **QLoRA**       | 4-bitars kvantisering + LoRA-adaptrar. Lägst minnesanvändning, snabbast, liten kvalitetsavvägning. Kräver `bitsandbytes` (endast Linux).                            | 12–16GB      | De flesta användare; snabba experiment; begränsat VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full finjustering** | Uppdaterar alla modellparametrar. Maximal kvalitet; högst minnes- och beräkningsanvändning.                                    | 40GB+      | Maximal kvalitet; forskning; stort VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Obs:** Full finjustering (`train_full_finetuning.py`) kan kräva mer än 64GB systemminne och kanske inte är genomförbart på den här enheten. Överväg att använda LoRA eller QLoRA istället.
<!-- @os:end -->

<!-- @os:windows -->
> **Obs:** Full finjustering (`train_full_finetuning.py`) kan kräva mer än 64GB systemminne och kanske inte är genomförbart på den här enheten. Överväg att använda LoRA istället.
<!-- @os:end -->
<!-- @device:end -->

Välj helt enkelt din önskade `Training method`, ladda ner motsvarande skript och kör det med kommandot medan din virtuella miljö är aktiverad: 

```python
python3 train_<method_name>.py.
```

## Använda din finjusterade modell

### Efter full finjustering

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Efter LoRA/QLoRA-träning

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Slå samman LoRA-adapter med basmodellen

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Obs:**  
- Se till att modellkatalogens namn (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) matchar din faktiska utdatamapp från träningen.  
- Om du använde LoRA istället för QLoRA, byt bara ut sökvägen därefter.  
- Vissa Gemma-modeller kräver att du anger `trust_remote_code=True` i `from_pretrained`; lägg till det om du ser en relaterad varning.

För fler anpassade inställningar (utfyllnadstokens, enhet osv.), se skriptet du använde för träningen.

<!-- @test:id=verify-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-lora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LoRA output looks correct")
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-qlora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-qlora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: QLoRA output looks correct")
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=verify-full-finetuning-output timeout=300 hidden=True setup=activate-venv -->
```python
import glob
import os
import sys

out_dir = "output-gemma-3-4b-it-full"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Anpassningsguide

### Använd ditt eget dataset

Alla skript använder samma datasetformat. Ersätt inläsningsavsnittet:

```python
from datasets import load_dataset

# Option 1: Local JSON/JSONL file
dataset = load_dataset('json', data_files='your_data.json')

# Option 2: Hugging Face Hub dataset
dataset = load_dataset('username/dataset-name')

# Option 3: CSV file
dataset = load_dataset('csv', data_files='data.csv')

# Format for chat models
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

dataset = dataset.map(format_instruction)
```

**Datasetformat för lokal JSON/JSONL-fil:**

När du använder den här metoden, se till att dina JSON-filer är korrekt strukturerade för att undvika tolkningsfel. 

Följande riktlinjer måste följas:
* **Filformatering:** JSON-filer bör formateras inom en integrerad utvecklingsmiljö (IDE) för att säkerställa korrekt struktur och syntax.
* **Obligatoriska nycklar:** Den anpassade JSON-filen måste innehålla nycklarna `instruction` och `response`. Dessa nycklar är nödvändiga för att metoden ska fungera korrekt.
```json
[
  {
    "instruction": "Your first instruction here",
    "response": "Expected response here"
  },
  {
    "instruction": "Your second instruction here",
    "response": "Expected response here"
  }
]
```
**Datasetformat för Hugging Face Hub-dataset**

Vid användning av dataset från Hugging Face, se till att dina dataset är korrekt strukturerade för att möjliggöra smidig integration. 

Följande riktlinjer bör följas:
* **Instruktion-svar-par:** Fokusera på dataset som innehåller ett `instruction-response`-par. Denna struktur är nödvändig för den avsedda funktionaliteten.
* **Anpassad nyckelmodifiering:** Om ditt dataset inte följer strukturen `instruction-response` har du möjlighet att ändra funktionen `format_instruction()`. Detta gör att du kan anpassa till specifika nycklar efter behov.

Exempel på justering: I fall där datasetets utdata behöver justeras kan du ändra svarsavsnittet i funktionen format_instruction() för att passa dina behov.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Datasetformat för CSV-fil**

För att anpassa skriptet till att använda ett CSV-filformat måste du se till att CSV-filen innehåller kolumner med namnen `instruction` och `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Justera träningsparametrar

Redigera träningsskriptet och ändra variablerna så att de matchar dina mål: **inlärningshastighet** (`LR`), **epoker** (`EPOCHS`), **batchstorlek** (`BATCH_SIZE`), **gradientackumulering** (`GRAD_ACCUM_STEPS`) och för LoRA/QLoRA **rank** (`LORA_R`). För snabbare körningar, använd färre epoker och en högre inlärningshastighet (LR); för bättre kvalitet, använd fler epoker och en lägre LR. Minska batchstorleken eller sekvenslängden om du stöter på minnesfel (out-of-memory).
### Tips för minnesoptimering

Om du stöter på minnesbristfel (out-of-memory):

**1. Minska batchstorleken:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Minska sekvenslängden:**
```python
max_seq_length=256  # Instead of 512
```

**3. Använd mer aggressiv kvantisering:**
```
Full → LoRA → QLoRA
```

**4. Aktivera gradient checkpointing (endast vid fullständig finjustering):**
```python
model.gradient_checkpointing_enable()
```

---

## Övervakning och felsökning

### Övervaka GPU-minne

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Valfritt) Spåra experiment med Weights & Biases

För att logga körningar och mätvärden till [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

Ställ i träningsskriptet in `report_to="wandb"` och eventuellt `run_name="your-experiment-name"` i tränarkonfigurationen. Om du föredrar att inte använda Wandb, låt `report_to` behålla standardvärdet eller ställ in det till `"none"`.

### Vanliga problem

#### Slut på minne (OOM)

**Lösning:** Minska batchstorleken och/eller använd QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Förlusten minskar inte

**Lösning:** Justera inlärningshastigheten
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Långsam träning

**Lösning:** Öka batchstorleken om minnet tillåter det
```python
BATCH_SIZE = 8
```
## Nästa steg

När du har slutfört en lyckad finjustering kan du överväga följande nästa steg för att få ut mer av din modell:

1. **Utvärdera** noggrant på undanhållen testdata för att mäta generalisering och undvika överanpassning.
2. **Experimentera** genom att prova olika hyperparametervärden för bättre avvägningar mellan noggrannhet, hastighet och minnesanvändning.
3. **Spåra** alla dina experiment (och tillhörande mätvärden) med Weights & Biases för reproducerbar forskning.
4. **Prova** att träna på dina egna anpassade dataset för att anpassa modellen specifikt för ditt användningsfall.
5. **Driftsätt** din finjusterade modell för snabb inferens med hjälp av effektiva backends som vLLM på kompatibel hårdvara.
6. **Utforska** avancerade tekniker som prompt engineering, blandad precision och längre sekvenslängder.
7. **Träna** flera LoRA-adaptrar för olika uppgifter eller domäner och byt mellan dem vid behov.

---