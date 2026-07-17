<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled


Želite zaganjati zmogljive jezikovne modele umetne inteligence na lastni strojni opremi? Ta vodič vam pokaže, kako.
Ta vadnica uporablja PyTorch, ki ga poganja programska oprema AMD ROCm™, za zaganjanje modelov, ki znajo povzemati dokumente, odgovarjati na vprašanja, generirati besedilo in še več – vse lokalno.

## Kaj se boste naučili

- Lokalno zaganjanje jezikovnih modelov, kot sta gpt-oss-20b in qwen3.5-4B, z uporabo PyTorch in ROCm
- Ustvarjanje orodja za povzemanje dokumentov z jezikovnimi modeli

## Nastavitev konfigurace pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme
> **Opomba**: Če VS Code ni nameščen, ga lahko namestite prek Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev predpogojne programske opreme

### Ustvarjanje navideznega okolja

<!-- @os:linux -->
<!-- @device:halo_box -->
V Linuxu odprite terminal v izbranem imeniku in sledite ukazom za ustvarjanje navideznega okolja (venv) z že nameščenima ROCm in PyTorch.
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
**Svojemu uporabniku dodelite dostop do naprav GPU** (za uveljavitev se odjavite in znova prijavite):

```bash
sudo usermod -aG render,video $LOGNAME
```

V Linuxu odprite terminal v izbranem imeniku in sledite ukazom za ustvarjanje navideznega okolja (venv).
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
V sistemu Windows odprite terminal v izbranem imeniku in sledite ukazom za ustvarjanje navideznega okolja (venv) z že nameščenima ROCm in PyTorch.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
V sistemu Windows odprite terminal v izbranem imeniku in sledite ukazom za ustvarjanje navideznega okolja (venv).
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Nasvet**: Uporabniki sistema Windows bodo morda morali spremeniti pravilnik izvajanja PowerShell (npr.
> nastaviti ga na RemoteSigned ali Unrestricted), preden zaženejo nekatere ukaze PowerShell.

<!-- @os:end -->

### Namestitev osnovnih odvisnosti
<!-- @require:driver,pytorch -->

### Namestitev dodatnih odvisnosti

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

## Hiter začetek z vzorčnimi skriptami

Ta priročnik vključuje skripte, pripravljene za uporabo. Kliknite jih za predogled in jih prenesite v isti imenik, kjer ste ustvarili okolje.

| Skripta | Opis | Uporaba |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Osnovno generiranje besedila z jezikovnim modelom | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Orodje za povzemanje dokumentov s podporo za Harmony | `python summarizer.py --file document.txt` |

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

Obe skripti podpirata:
- Izbiro modela prek zastavice `--model`
- Oblikovanje predloge za klepet za pravilno pozivanje modela, kar je še posebej koristno pri povzemanju dokumentov

## Nalaganje in zagon prvega jezikovnega modela

Priložena skripta [run_llm.py](assets/run_llm.py) prikazuje, kako generirati besedilo z jezikovnimi modeli z uporabo PyTorch in AMD ROCm.

> **Opomba:** Ko naložite model, Hugging Face Transformers najprej preveri lokalni predpomnilnik (`~/.cache/huggingface/hub` v Linuxu, `C:\Users\<user>\.cache\huggingface\hub` v sistemu Windows). Če model ni v predpomnilniku, se samodejno prenese s huggingface.co. Prvi zagon lahko traja nekaj minut, odvisno od velikosti modela in hitrosti omrežja.

Spodnji odlomek prikazuje, kako uporabiti model in prilagoditi zastavljena vprašanja.

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

Preizkusite preneseno skripto:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Izgradnja orodja za povzemanje dokumentov

Zdaj, ko ste ustvarili lokalni izhod jezikovnega modela, lahko to nadgradite z izdelavo praktičnega orodja za povzemanje dokumentov. V tem razdelku boste uporabili skripto [summarizer.py](assets/summarizer.py), da vnesete datoteko .txt in samodejno ustvarite jedrnato povzetek – vse lokalno na vašem GPU.

Skripta je zasnovana tako, da deluje takoj po namestitvi. Odprite jo v urejevalniku, da raziščete kodo, prilagodite pozive in nastavite parametre, kot sta dolžina in temperatura.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Primeri uporabe

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

## Spoznajte parametre generiranja

| Parameter | Kaj nadzoruje | Tipične vrednosti |
|-----------|------------------|----------------|
| `max_new_tokens` | Največja dolžina izhoda jezikovnega modela | Za povzetke uporabite 50–500 žetonov. (1 žeton je približno 0,75 angleške besede) |
| `temperature` | Ustvarjalnost. Nizke vrednosti zagotavljajo osredotočenost, visoke vrednosti prinašajo večjo nepredvidljivost | - **0,1–0,3**: Osredotočeno, deterministično (primerno za povzetke) <br> **0,5–0,7**: Uravnoteženo (splošna uporaba) <br> **0,8–1,0**: Ustvarjalno, raznovrstno (možganska nevihta) |
| `top_p` | Vzorčenje jedra – nizke vrednosti omejijo model na ožje izhode | **0,1–0,5**: Strogo, predvidljivo <br> **0,9–0,95**: (standardno, naravno, pogovorno) |


## Aplikacije v resničnem svetu

- **Analiza znanstvenih člankov**: Izvlecite ključne ugotovitve iz kompleksnih publikacij za hitri pregled
- **Agregacija novic**: Povzemite novičarske članke v kratke dnevne preglede ali poudarke
- **Zapisniki sestankov**: Strnite prepise v izvedljive točke in jedrnate povzetke
- **Pregled pravnih dokumentov**: Hitro izvlecite ustrezne klavzule ali obveznosti iz dolgih pravnih besedil
- **Dokumentacija kode**: Ustvarite jedrnate preglede repozitorijev in razlage funkcij

## Naslednji koraki

- **Fino uglaševanje**: Prilagodite modele svojemu specifičnemu področju ali žargonu za boljšo natančnost (glejte priročnike za fino uglaševanje)
- **Sistemi RAG**: Kombinirajte jezikovne modele s pridobivanjem dokumentov za kontekstualno ozaveščene odgovore in iskanje
- **Raziskovanje modelov**: Eksperimentirajte z novimi modeli, kot so Llama 3, Phi-3 ali Qwen, za boljše rezultate
- **Produkcijska namestitev**: Uporabite orodja, kot je vLLM, za razširljivo strežbo jezikovnih modelov v organizacijah

Vaš sistem vam daje moč za lokalno zaganjanje sofisticiranih jezikovnih modelov. Eksperimentirajte z različnimi modeli, pozivi in parametri, da odkrijete, kaj najbolje deluje za vaše aplikacije.