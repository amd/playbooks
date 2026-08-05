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

Denna spelbok visar hur man finjusterar en språkmodell lokalt med Unsloth på AMD-hårdvara.

Den använder ett kort exempel på Supervised Fine-Tuning (SFT) med LoRA-adaptrar på `unsloth/gemma-4-E4B-it`, med en delmängd av datasetet `mlabonne/FineTome-100k`. Målet är att ge dig ett enkelt, heltäckande arbetsflöde som täcker installation, träning, inferens och sparande av det finjusterade resultatet.

Exemplet är utformat för att vara praktiskt och lätt att anpassa, så du kan använda det som en utgångspunkt för dina egna dataset och modeller.

## Vad du kommer att lära dig

- Hur man ställer in Unsloth-miljön
- Hur man finjusterar en LLM med SFT och Unsloth
- Hur man sparar det finjusterade resultatet lokalt

<!-- @device:halo,stx,krk -->
> **Obs:** Finjusteringsteknikerna i denna spelbok kräver minst **64 GB systemminne**, varav minst **24 GB måste vara tillgängligt för GPU:n** (24 GB är en del av de 64 GB, inte utöver dem).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Obs:** Finjusteringsteknikerna i denna spelbok kräver minst **24 GB totalt GPU-minne** och **32 GB systemminne**.
> - I Windows kombinerar det totala GPU-minnet grafikkortets dedikerade VRAM med delat GPU-minne (lånat från systemminnet).
> - Därför kan kort med mindre än 24 GB dedikerat VRAM ändå köra denna spelbok genom att använda delat GPU-minne för att kompensera skillnaden.
<!-- @os:end -->

<!-- @os:linux -->
> **Obs:** Finjusteringsteknikerna i denna spelbok kräver ett grafikkort med minst **24 GB dedikerat GPU-minne** och **32 GB systemminne**.
> - I Linux körs träningen helt i grafikkortets dedikerade VRAM.
> - Den faller inte tillbaka på delat GPU-minne (systemminne) när VRAM:et tar slut.
> - Kort med mindre än 24 GB dedikerat VRAM kommer att få slut på minne under träning i Linux, även om systemet har gott om RAM.
<!-- @os:end -->
<!-- @device:end -->

## Varför Unsloth?

Unsloth gör det enklare att köra LLM-finjustering på lokal hårdvara genom att minska minnesanvändningen och snabba upp träningen jämfört med en standardkonfiguration.

I denna spelbok använder vi Unsloth tillsammans med **LoRA-baserad SFT**. Det innebär att basmodellen till största delen förblir fryst, medan en mycket mindre uppsättning adaptervikter tränas. Detta passar bra för lokal utveckling eftersom det är lättare än fullständig finjustering och snabbare att iterera på.

Unsloth stöder även andra träningsmetoder, inklusive QLoRA och arbetsflöden för förstärkningsinlärning. Denna spelbok fokuserar först på den enklaste vägen: ett litet exempel på LoRA-finjustering som användare kan köra, förstå och utöka.

## Ställa in minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera programvaruuppdateringar
> **Obs**: Om VS Code inte är installerat kan du installera det med Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installera nödvändig programvara

### Skapa en virtuell miljö

<!-- @os:linux -->
<!-- @device:halo_box -->
Öppna en terminal och skapa en venv med AMD ROCm™-programvara och PyTorch redan installerat:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Ge din användare åtkomst till GPU-enheter** (logga ut och in igen för att detta ska träda i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

Öppna en terminal och skapa en venv:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Obs:** Python 3.13 krävs för Windows.

<!-- @device:halo_box -->
Öppna en PowerShell-terminal och skapa en virtuell miljö:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Öppna en PowerShell-terminal och skapa en virtuell miljö:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Installera grundläggande beroenden
<!-- @require:pytorch,driver -->

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### Ytterligare beroenden

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Obs:** Under import kan Unsloth prova valfria `bitsandbytes`-accelerationsvägar. På vissa ROCm-versioner kan du se ett meddelande som `bitsandbytes library load error: Configured ROCm binary not found`. Denna spelbok använder standard LoRA-finjustering med `optim="adamw_torch"`, så vi förlitar oss inte på `bitsandbytes`-optimeraren eller 4-bitars QLoRA. Detta meddelande kan tryggt ignoreras.

<!-- @os:windows -->
> **Obs:** På Windows ROCm kommer Unsloth att skriva ut flera varningar vid start — se [Kända varningar](#known-warnings) nedan. Dessa är alla säkra att ignorera; träningen fungerar korrekt.
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## Ladda ner Unsloth-finjusteringsskriptet

Istället för att manuellt utföra varje steg tillhandahåller denna spelbok ett rent, heltäckande skript här: [test_unsloth.py](assets/test_unsloth.py).

Kör följande kod för att köra skriptet:

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

Resten av spelboken kommer att konceptuellt gå igenom varje huvudsteg i skriptet. 

## Hur det fungerar

Skriptet test_unsloth.py utför följande steg:
* **Ladda modell**: Laddar unsloth/gemma-4-E4B-it med FastModel.
* **Förbered data**: Standardiserar datasetet (t.ex. FineTome-100k) och tillämpar Gemma-4-chattmallen.
* **Tillämpa LoRA**: Lägger till adaptrar till språk-, attentions- och MLP-moduler för effektiv träning.
* **Träna**: Använder SFTTrainer med förlustmaskering enbart för svar.
* **Inferens**: Kör ett snabbt genereringstest för att verifiera prestanda.
* **Spara**: Exporterar LoRA-adaptrar lokalt.

## Nyckelkonfiguration

Du kan ändra följande konstanter för att anpassa din körning:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Exempel på Unsloths välkomstmeddelande och utdata vid inläsning av modellvikterna:

![alt text](assets/welcome.png)

## Förbered dataset

Vi använder en delmängd av:
```text
mlabonne/FineTome-100k
```
Datasetet är: 
* Konverterat till chattformat
* Bearbetat med Gemma-4-chattmallen
* Rensat för att ta bort dubbla BOS-token

## Träna modellen

Skriptet kör en kort träningsdemo, med följande parametrar:
- ~50 steg
- Liten batchstorlek
- Gradientackumulering

Under träningen kommer du att se loggar som:

![alt text](assets/training.png)


## Sparande och distribution
### Lokal sparning (LoRA)

Skriptet sparar automatiskt LoRA-adaptrar till OUTPUT_DIR.
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### Spara sammanfogad modell (för vLLM) 

<!-- @os:windows -->
> **Obs:** vLLM stöder inte Windows. För att distribuera din finjusterade modell på Windows, använd llama.cpp (se [Exportera GGUF](#export-gguf-for-llamacpp) nedan) eller överför den sammanfogade modellen till en Linux-dator som kör vLLM.
<!-- @os:end -->

<!-- @os:linux -->
För distribution med vLLM, sammanfoga adaptrarna till en fullständig modell:
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### Exportera GGUF (för llama.cpp)

Konvertera direkt till GGUF för lokal inferens:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Kända varningar

Dessa varningar skrivs ut av Unsloth vid uppstart på Windows ROCm och kan alla ignoreras utan risk:

| Varning | Orsak | Säker att ignorera? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes har ingen Windows ROCm-version | Ja — den här spelboken använder `adamw_torch`, inte bnb |
| `No ROCm platform found for torch.distributed` | ROCm på Windows saknar stöd för distribuerad träning | Ja — enkel-GPU-träning påverkas inte |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth flaggar icke-Linux-byggen | Ja — Windows ROCm fungerar för enkel-GPU SFT |
| `triton is not available` | Triton har ingen Windows-version | Ja — Unsloth faller tillbaka på PyTorch-kärnor |

Träningen kommer att fortsätta korrekt trots dessa varningar.
<!-- @os:end -->

## Nästa steg
- Prova [Unsloth Studio](https://unsloth.ai/docs/new/studio), ett intuitivt grafiskt gränssnitt för Unsloth
- Träna på dina egna specifika datamängder
- Prova finjustering med olika hyperparametrar
- Distribuera med vLLM eller llama.cpp
- Prova QLoRA för en installation med lägre minnesanvändning

## Resurser

Nedan följer några ytterligare resurser för att lära dig mer om Unsloth och finjustering:

* [Unsloth Docs](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth Fine-tuning Guide](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)