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


Szeretne nagy teljesítményű AI nyelvi modelleket futtatni a saját hardverén? Ez az útmutató megmutatja, hogyan.
Ez az oktatóanyag a PyTorch-ot használja, az AMD ROCm™ szoftver által meghajtva, hogy olyan modelleket futtasson, amelyek dokumentumokat foglalnak össze, kérdésekre válaszolnak, szöveget generálnak, és sok minden mást, mindezt helyben futtatva.

## Amit meg fog tanulni

- Olyan LLM-ek futtatása, mint a gpt-oss-20b és a qwen3.5-4B, helyben, PyTorch és ROCm segítségével
- Dokumentum-összefoglaló eszköz létrehozása LLM-ek felhasználásával

<!-- @device:halo_box,halo,stx,krk -->
## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheti a Ryzen AI Developer Centerrel.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése

### Virtuális környezet létrehozása

<!-- @os:linux -->
<!-- @device:halo_box -->
Linuxon nyisson meg egy terminált a kívánt könyvtárban, és kövesse a parancsokat egy olyan venv létrehozásához, amelyben a ROCm+Pytorch már telepítve van.
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
**Adjon hozzáférést a felhasználójának a GPU-eszközökhöz** (a hatásba lépéshez jelentkezzen ki, majd vissza):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linuxon nyisson meg egy terminált a kívánt könyvtárban, és kövesse a parancsokat egy venv létrehozásához.
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
Windowson nyisson meg egy terminált a kívánt könyvtárban, és kövesse a parancsokat egy olyan venv létrehozásához, amelyben a ROCm+Pytorch már telepítve van.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windowson nyisson meg egy terminált a kívánt könyvtárban, és kövesse a parancsokat egy venv létrehozásához.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tipp**: Windows felhasználóknak szükségük lehet a PowerShell végrehajtási házirendjének módosítására (pl.
> RemoteSigned vagy Unrestricted értékre állítva) mielőtt egyes PowerShell parancsokat futtatnak.

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

> **Megjegyzés:** Ha a modell nem tölthető be, vagy elfogy a memória, próbálja meg telepíteni a `kernels` csomagot, hogy optimalizált kvantálással töltse be a modellt.
>
> ```bash
> # Use this version which is compatible with the Transformers version
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

## Gyors kezdés a példaszkriptekkel

Ez a playbook azonnal használható szkripteket tartalmaz. Kattintson rájuk az előnézethez, és töltse le őket ugyanabba a könyvtárba, ahol a létrehozott környezet található.

| Szkript | Leírás | Használat |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Alapvető LLM szöveggenerálás | `python run_llm.py` |
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
- A modell kiválasztását a `--model` kapcsolóval
- A chat sablon formázását a megfelelő modell-promptoláshoz, ami különösen hasznos dokumentum-összefoglaláshoz

## Az első LLM betöltése és futtatása

A mellékelt [run_llm.py](assets/run_llm.py) szkript bemutatja, hogyan lehet szöveget generálni LLM-ekkel PyTorch és AMD ROCm segítségével.

> **Megjegyzés:** Amikor betölt egy modellt, a Hugging Face Transformers először ellenőrzi a helyi gyorsítótárat (`~/.cache/huggingface/hub` Linuxon, `C:\Users\<user>\.cache\huggingface\hub` Windowson). Ha a modell nincs gyorsítótárazva, automatikusan letöltődik a huggingface.co-ról. Az első futtatás néhány percig is eltarthat a modell méretétől és a hálózati sebességtől függően.

Az alábbi kódrészlet bemutatja, hogyan használható a modell, és hogyan testreszabhatók a feltett kérdések.

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

Miután helyben generált LLM-kimenetet, ezt tovább építheti egy gyakorlati dokumentum-összefoglaló létrehozásával. Ebben a szakaszban a [summarizer.py](assets/summarizer.py) szkriptet fogja használni, hogy betöltsön egy .txt fájlt, és automatikusan tömör összefoglalót generáljon, mindezt helyben, a GPU-ján futtatva.

A szkriptet úgy tervezték, hogy azonnal működjön. Nyissa meg a szkriptet egy szerkesztőben, hogy megismerje a kódot, testreszabja a promptokat, és finomhangolja az olyan paramétereket, mint a hossz és a hőmérséklet.

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

## Ismerje meg a generálási paramétereket

| Paraméter | Mit szabályoz | Tipikus értékek |
|-----------|------------------|----------------|
| `max_new_tokens` | Az LLM kimenetének maximális hossza | Használjon 50–500 tokent összefoglalókhoz. (1 token körülbelül 0,75 angol szónak felel meg) |
| `temperature` | Kreativitás. Az alacsony értékek koncentráltabbá teszik, míg a magasabb értékek nagyobb kiszámíthatatlansággal járnak | - **0.1–0.3**: Koncentrált, determinisztikus (jó összefoglalókhoz) <br> **0.5–0.7**: Kiegyensúlyozott (általános használat) <br> **0.8–1.0**: Kreatív, változatos (ötletelés) |
| `top_p` | Nucleus Sampling - Az alacsony értékek szűkebb kimenetre korlátozzák a modellt | **0.1-0.5**: Szigorú, kiszámítható <br> **0.9-0.95**: (standard, természetes, beszélgetős) |


## Valós alkalmazások

- **Kutatási cikk elemzés**: Kulcsfontosságú megállapítások kinyerése összetett publikációkból gyors áttekintéshez
- **Hírösszesítés**: Hírcikkek összefoglalása rövid napi kivonatokba vagy kiemelésekbe
- **Megbeszélési jegyzetek**: Átiratok tömörítése végrehajtandó feladatokká és tömör összefoglalókká
- **Jogi dokumentumok áttekintése**: Releváns záradékok vagy kötelezettségek gyors kinyerése hosszú jogi szövegekből
- **Kód dokumentáció**: Tömör repository-áttekintések és függvénymagyarázatok generálása
## Következő lépések

- **Finomhangolás**: Modellek adaptálása az adott szakterületre vagy szaknyelvre a nagyobb pontosság érdekében (lásd a Finomhangolási útmutatókat)
- **RAG rendszerek**: LLM-ek kombinálása dokumentumkereséssel a kontextusérzékeny válaszok és keresés érdekében
- **Modellek felfedezése**: Kísérletezés új modellekkel, például Llama 3, Phi-3 vagy Qwen, jobb eredmények elérése érdekében
- **Éles üzembe helyezés**: Olyan eszközök használata, mint a vLLM, a skálázható LLM-kiszolgáláshoz szervezeteknél

A rendszered lehetővé teszi számodra, hogy kifinomult nyelvi modelleket futtass helyben. Kísérletezz különböző modellekkel, promptokkal és paraméterekkel, hogy megtaláld, mi működik a legjobban az alkalmazásaidhoz.