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


Szeretne hatékony AI nyelvi modelleket futtatni saját hardverén? Ez az útmutató megmutatja, hogyan.
Ez az oktatóanyag a PyTorch keretrendszert használja, amelyet az AMD ROCm™ szoftver hajt meg, hogy olyan modelleket futtasson, amelyek dokumentumokat képesek összefoglalni, kérdésekre válaszolni, szöveget generálni és még sok mást, mindezt helyben futtatva.

## Mit fog megtanulni

- Olyan LLM-ek futtatása, mint a gpt-oss-20b és a qwen3.5-4B, helyben, PyTorch és ROCm használatával
- Dokumentum-összefoglaló eszköz létrehozása LLM-ek segítségével

<!-- @device:halo_box,halo,stx,krk -->
## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheti a Ryzen AI Developer Center segítségével.

<!-- @require:software-update -->
<!-- @device:end -->

## A szükséges szoftverek telepítése

### Virtuális környezet létrehozása

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux rendszeren nyisson meg egy terminált a kívánt könyvtárban, és kövesse a parancsokat egy olyan venv létrehozásához, amelyben a ROCm+Pytorch már telepítve van.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Adjon hozzáférést felhasználójának a GPU-eszközökhöz** (ahhoz, hogy ez érvénybe lépjen, jelentkezzen ki, majd újra be):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux rendszeren nyisson meg egy terminált a kívánt könyvtárban, és kövesse a parancsokat egy venv létrehozásához.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
Windows rendszeren nyisson meg egy terminált a kívánt könyvtárban, és kövesse a parancsokat egy olyan venv létrehozásához, amelyben a ROCm+Pytorch már telepítve van.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windows rendszeren nyisson meg egy terminált a kívánt könyvtárban, és kövesse a parancsokat egy venv létrehozásához.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tipp**: Előfordulhat, hogy Windows felhasználóknak módosítaniuk kell a PowerShell végrehajtási szabályzatát (pl.
> RemoteSigned vagy Unrestricted értékre állítva) néhány PowerShell parancs futtatása előtt.

<!-- @os:end -->

### Alapvető függőségek telepítése
<!-- @require:driver,pytorch -->

### További függőségek telepítése

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->
<!-- @device:halo,halo_box -->
<!-- @prereq:hf-models-gpt-oss-20b -->
<!-- @device:end -->
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:hf-models-qwen3-5-4b -->
<!-- @device:end -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

> **Megjegyzés:** Ha a modell betöltése sikertelen, vagy elfogy a memória, próbálja meg telepíteni a `kernels` csomagot a modell optimalizált kvantálással történő betöltéséhez.
>
> ```bash
> # Használja ezt a verziót, amely kompatibilis a Transformers verzióval
> pip install "kernels==0.14.1" 
> ```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Gyors kezdés példaszkriptekkel

Ez a playbook azonnal használható szkripteket tartalmaz. Kattintson rájuk az előnézethez, és töltse le őket ugyanabba a könyvtárba, amelyben a korábban létrehozott környezet található.

| Szkript | Leírás | Használat |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Alapvető LLM szöveggenerálás | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Dokumentum-összefoglaló Harmony támogatással | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

Mindkét szkript támogatja a következőket:
- Modellkiválasztás a `--model` kapcsolóval
- Chat sablon formázás a megfelelő modell-promptoláshoz, ami különösen hasznos dokumentum-összefoglaláshoz

## Az első LLM betöltése és futtatása

A mellékelt [run_llm.py](assets/run_llm.py) szkript bemutatja, hogyan generálhat szöveget LLM-ekkel PyTorch és AMD ROCm használatával.

> **Megjegyzés:** Amikor betölt egy modellt, a Hugging Face Transformers először ellenőrzi a helyi gyorsítótárat (`~/.cache/huggingface/hub` Linuxon, `C:\Users\<user>\.cache\huggingface\hub` Windowson). Ha a modell nincs gyorsítótárazva, automatikusan letöltődik a huggingface.co oldalról. Az első futtatás a modell méretétől és a hálózati sebességtől függően néhány percig is eltarthat.

Az alábbi kódrészlet bemutatja, hogyan használható a modell, és hogyan testre szabhatók a feltett kérdések.

<!-- @test:id=verify-imports timeout=300 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    disable_mmap=True
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

Próbálja ki a letöltött szkriptet:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Dokumentum-összefoglaló készítése

Most, hogy már generált helyi LLM-kimenetet, erre építve létrehozhat egy gyakorlati dokumentum-összefoglalót. Ebben a részben a [summarizer.py](assets/summarizer.py) szkriptet fogja használni egy .txt fájl betöltéséhez, és automatikusan tömör összefoglalót generál, mindezt a GPU-n, helyben futtatva.

A szkriptet úgy tervezték, hogy azonnal, módosítás nélkül is működjön. Nyissa meg a szkriptet egy szerkesztőben, hogy felfedezze a kódot, testre szabja a promptokat, és finomhangolja az olyan paramétereket, mint a hossz és a hőmérséklet.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Használati példák

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## A generálási paraméterek megismerése

| Paraméter | Mit vezérel | Tipikus értékek |
|-----------|------------------|----------------|
| `max_new_tokens` | Az LLM kimenetének maximális hossza | Összefoglalókhoz használjon 50–500 tokent. (1 token körülbelül 0,75 angol szónak felel meg) |
| `temperature` | Kreativitás. Alacsony értékek fókuszáltabbá teszik, míg magas értékek kiszámíthatatlanabbá | - **0,1–0,3**: Fókuszált, determinisztikus (jó összefoglalókhoz) <br> **0,5–0,7**: Kiegyensúlyozott (általános használatra) <br> **0,8–1,0**: Kreatív, változatos (ötletelés) |
| `top_p` | Nucleus Sampling - Az alacsony értékek szűkebb kimenetekre korlátozzák a modellt | **0,1-0,5**: Szigorú, kiszámítható <br> **0,9-0,95**: (standard, természetes, beszélgetős) |


## Valós alkalmazások

- **Kutatási cikkek elemzése**: Kulcsfontosságú megállapítások kiemelése összetett publikációkból a gyors áttekintéshez
- **Hírösszesítés**: Hírcikkek összefoglalása rövid napi kivonatokba vagy kiemelésekbe
- **Értekezletjegyzetek**: Átiratok tömörítése cselekvési pontokká és tömör összefoglalókká
- **Jogi dokumentumok áttekintése**: Releváns záradékok vagy kötelezettségek gyors kinyerése hosszú jogi szövegekből
- **Kóddokumentáció**: Tömör tárhely-áttekintések és funkcióleírások generálása
## Következő lépések

- **Finomhangolás**: Igazítsd a modelleket a saját szakterületedhez vagy szaknyelvedhez a jobb pontosság érdekében (lásd a Finomhangolási útmutatókat)
- **RAG rendszerek**: Kombináld az LLM-eket dokumentumkereséssel a kontextustudatos válaszokért és kereséshez
- **Modellek felfedezése**: Kísérletezz új modellekkel, például Llama 3, Phi-3 vagy Qwen, a jobb eredmények érdekében
- **Éles üzembe helyezés**: Használj olyan eszközöket, mint a vLLM, a skálázható LLM-kiszolgáláshoz szervezeteknél

A rendszered lehetővé teszi, hogy kifinomult nyelvi modelleket futtass helyben. Kísérletezz különböző modellekkel, promptokkal és paraméterekkel, hogy megtaláld, mi működik a legjobban az alkalmazásaidhoz.