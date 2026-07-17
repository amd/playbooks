<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés


Szeretne hatékony AI nyelvi modelleket futtatni saját hardverén? Ez az útmutató megmutatja, hogyan teheti meg.
Ez az oktatóanyag az AMD ROCm™ szoftver által támogatott PyTorch segítségével futtat olyan modelleket, amelyek képesek dokumentumokat összefoglalni, kérdésekre válaszolni, szöveget generálni és még sok mást – mindezt helyben futtatva.

## Mit fog megtanulni

- LLM-ek, például a gpt-oss-20b és a qwen3.5-4B helyi futtatása PyTorch és ROCm segítségével
- Dokumentum-összefoglaló eszköz létrehozása LLM-ek használatával

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, a Ryzen AI Developer Center segítségével telepítheti.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése

### Virtuális környezet létrehozása

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux rendszeren nyisson meg egy terminált a kívánt könyvtárban, és kövesse az alábbi parancsokat egy ROCm+Pytorch előre telepített venv létrehozásához.
<!-- @test:id=create-venv timeout=120 -->
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
**Adjon hozzáférést a felhasználójának a GPU eszközökhöz** (a módosítás érvénybe lépéséhez jelentkezzen ki, majd be újra):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux rendszeren nyisson meg egy terminált a kívánt könyvtárban, és kövesse az alábbi parancsokat egy venv létrehozásához.
<!-- @test:id=create-venv timeout=120 -->
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
Windows rendszeren nyisson meg egy terminált a kívánt könyvtárban, és kövesse az alábbi parancsokat egy ROCm+Pytorch előre telepített venv létrehozásához.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windows rendszeren nyisson meg egy terminált a kívánt könyvtárban, és kövesse az alábbi parancsokat egy venv létrehozásához.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tipp**: Előfordulhat, hogy a Windows-felhasználóknak módosítaniuk kell a PowerShell végrehajtási házirendjét (pl.
> RemoteSigned vagy Unrestricted értékre kell állítani) egyes PowerShell-parancsok futtatása előtt.

<!-- @os:end -->

### Alapvető függőségek telepítése
<!-- @require:driver,pytorch -->

### További függőségek telepítése

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
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
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Gyors kezdés példaszkriptekkel

Ez a playbook azonnal használható szkripteket tartalmaz. Kattintson rájuk az előnézethez, és töltse le őket ugyanabba a könyvtárba, ahol a létrehozott környezet található.

| Szkript | Leírás | Használat |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Alapszintű LLM szöveggenerálás | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Dokumentum-összefoglaló Harmony-támogatással | `python summarizer.py --file document.txt` |

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

Mindkét szkript támogatja:
- Modellkiválasztást a `--model` jelzőn keresztül
- Chat sablon formázást a megfelelő modell-promptoláshoz, különösen hasznos dokumentum-összefoglaláshoz

## Az első LLM betöltése és futtatása

A mellékelt [run_llm.py](assets/run_llm.py) szkript bemutatja, hogyan lehet szöveget generálni LLM-ekkel PyTorch és AMD ROCm segítségével.

> **Megjegyzés:** Amikor betölt egy modellt, a Hugging Face Transformers először ellenőrzi a helyi gyorsítótárát (Linux rendszeren `~/.cache/huggingface/hub`, Windows rendszeren `C:\Users\<user>\.cache\huggingface\hub`). Ha a modell nincs gyorsítótárazva, automatikusan letöltődik a huggingface.co oldalról. Az első futtatás a modell méretétől és a hálózati sebességtől függően néhány percet vehet igénybe.

Az alábbi kódrészlet bemutatja, hogyan használható a modell, és hogyan szabhatók testre a feltett kérdések.

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
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
    device_map="auto"
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

Most, hogy helyi LLM-kimenetet generált, erre építve létrehozhat egy praktikus dokumentum-összefoglalót. Ebben a részben a [summarizer.py](assets/summarizer.py) szkriptet fogja használni egy .txt fájl betáplálásához és egy tömör összefoglaló automatikus generálásához – mindezt helyben, a GPU-n futtatva.

A szkript azonnal használható. Nyissa meg egy szerkesztőben a kód felfedezéséhez, a promptok testreszabásához, valamint az olyan paraméterek módosításához, mint a hossz és a hőmérséklet.

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

## Tudjon meg többet a generálási paraméterekről

| Paraméter | Mit szabályoz | Tipikus értékek |
|-----------|------------------|----------------|
| `max_new_tokens` | Az LLM kimenetének maximális hossza | Összefoglalókhoz 50–500 tokent használjon. (1 token körülbelül 0,75 angol szónak felel meg) |
| `temperature` | Kreativitás. Az alacsony értékek fókuszáltabbá teszik, míg a magas értékek nagyobb kiszámíthatatlanságot hoznak | - **0.1–0.3**: Fókuszált, determinisztikus (összefoglalókhoz jó) <br> **0.5–0.7**: Kiegyensúlyozott (általános használat) <br> **0.8–1.0**: Kreatív, változatos (ötleteléshez) |
| `top_p` | Nucleus Sampling – Az alacsony értékek szűkebb kimenetekre korlátozzák a modellt | **0.1-0.5**: Szigorú, kiszámítható <br> **0.9-0.95**: (standard, természetes, társalgási) |


## Valós alkalmazások

- **Kutatási cikkek elemzése**: Kulcsmegállapítások kinyerése összetett publikációkból gyors áttekintés céljából
- **Híraggregálás**: Hírcikkek összefoglalása rövid napi összefoglalókká vagy kiemeléssé
- **Értekezleti jegyzetek**: Átiratok tömörítése végrehajtható elemekké és tömör összefoglalókká
- **Jogi dokumentumok áttekintése**: Releváns záradékok vagy kötelezettségek gyors kinyerése hosszú jogi szövegekből
- **Kóddokumentáció**: Tömör tárház-áttekintők és függvénymagyarázatok generálása

## Következő lépések

- **Finomhangolás**: Modellek adaptálása az adott szakterülethez vagy szakzsargonhoz a jobb pontosság érdekében (lásd a finomhangolási playbook-okat)
- **RAG rendszerek**: LLM-ek kombinálása dokumentum-visszakereséssel kontextustudatos válaszokhoz és kereséshez
- **Modellkísérletezés**: Kísérletezzen új modellekkel, mint a Llama 3, Phi-3 vagy Qwen a jobb eredményekért
- **Éles üzembe helyezés**: Használjon olyan eszközöket, mint a vLLM a skálázható LLM-kiszolgáláshoz szervezetekben

A rendszere megadja az erőt, hogy kifinomult nyelvi modelleket futtasson helyben. Kísérletezzen különböző modellekkel, promptokkal és paraméterekkel, hogy felfedezze, mi működik a legjobban az alkalmazásai számára.