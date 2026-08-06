<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled


Želite poganjati zmogljive jezikovne modele umetne inteligence na svoji strojni opremi? Ta vodnik vam pokaže, kako.
Ta vadnica uporablja PyTorch, ki ga poganja programska oprema AMD ROCm™, za zagon modelov, ki lahko povzemajo dokumente, odgovarjajo na vprašanja, generirajo besedilo in še več – vse to poteka lokalno.

## Kaj se boste naučili

- Zaganjanje jezikovnih modelov, kot sta gpt-oss-20b in qwen3.5-4B, lokalno z uporabo PyTorch in ROCm
- Ustvarjanje orodja za povzemanje dokumentov z uporabo jezikovnih modelov

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme
> **Opomba**: Če VS Code ni nameščen, ga lahko namestite z Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev zahtevane programske opreme

### Ustvarjanje navideznega okolja

<!-- @os:linux -->
<!-- @device:halo_box -->
V sistemu Linux odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje navideznega okolja (venv), v katerem sta že nameščena ROCm in Pytorch.
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
**Dodelite svojemu uporabniku dostop do naprav GPU** (za uveljavitev spremembe se odjavite in znova prijavite):

```bash
sudo usermod -aG render,video $LOGNAME
```

V sistemu Linux odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje navideznega okolja (venv).
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
V sistemu Windows odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje navideznega okolja (venv), v katerem sta že nameščena ROCm in Pytorch.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
V sistemu Windows odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje navideznega okolja (venv).
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Nasvet**: Uporabniki sistema Windows bodo morda morali pred izvajanjem nekaterih ukazov Powershell spremeniti svojo izvedbeno politiko (Execution Policy) (npr.
> jo nastaviti na RemoteSigned ali Unrestricted).

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

## Hiter začetek s primeri skript

Ta priročnik vključuje pripravljene skripte za takojšnjo uporabo. Kliknite nanje za predogled in prenos v isto mapo kot okolje, ki ste ga ustvarili.

| Skripta | Opis | Uporaba |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Osnovno generiranje besedila z jezikovnim modelom | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Povzemalnik dokumentov s podporo za Harmony | `python summarizer.py --file document.txt` |

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
- Oblikovanje predloge klepeta za ustrezno pozivanje modela, kar je še posebej uporabno za povzemanje dokumentov

## Nalaganje in zagon vašega prvega jezikovnega modela

Priložena skripta [run_llm.py](assets/run_llm.py) prikazuje, kako generirati besedilo z jezikovnimi modeli z uporabo PyTorch in AMD ROCm.

> **Opomba:** Ko naložite model, Hugging Face Transformers najprej preveri lokalni predpomnilnik (`~/.cache/huggingface/hub` v sistemu Linux, `C:\Users\<user>\.cache\huggingface\hub` v sistemu Windows). Če model ni predpomnjen, se samodejno prenese s huggingface.co. Prvi zagon lahko traja nekaj minut, odvisno od velikosti modela in hitrosti omrežja.

Spodnji izsek prikazuje, kako uporabiti model in prilagoditi zastavljena vprašanja.

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


## Izdelava povzemalnika dokumentov

Zdaj, ko ste generirali izhod lokalnega jezikovnega modela, lahko na tem gradite naprej z izdelavo praktičnega povzemalnika dokumentov. V tem razdelku boste uporabili skripto [summarizer.py](assets/summarizer.py) za vnos datoteke .txt in samodejno generiranje jedrnatega povzetka, vse to bo potekalo lokalno na vašem GPU-ju.

Skripta je zasnovana tako, da deluje takoj po namestitvi. Odprite skripto v urejevalniku, da raziščete kodo, prilagodite pozive in nastavite parametre, kot sta dolžina in temperatura.

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
| `temperature` | Ustvarjalnost. Nizke vrednosti pomenijo osredotočenost, visoke pa večjo nepredvidljivost | - **0,1–0,3**: Osredotočeno, deterministično (dobro za povzetke) <br> **0,5–0,7**: Uravnoteženo (splošna uporaba) <br> **0,8–1,0**: Ustvarjalno, raznoliko (nastajanje idej) |
| `top_p` | Nucleus Sampling – nizke vrednosti omejijo model na ožje izhode | **0,1-0,5**: Strogo, predvidljivo <br> **0,9-0,95**: (standardno, naravno, pogovorno) |


## Uporaba v resničnem svetu

- **Analiza raziskovalnih člankov**: Izluščite ključne ugotovitve iz zapletenih publikacij za hiter pregled
- **Zbiranje novic**: Povzemite novičarske članke v kratke dnevne izvlečke ali poudarke
- **Zapiski sestankov**: Strnite transkripte v konkretne naloge in jedrnate povzetke
- **Pregled pravnih dokumentov**: Hitro izluščite ustrezne klavzule ali obveznosti iz dolgih pravnih besedil
- **Dokumentacija kode**: Generirajte jedrnate preglede repozitorijev in razlage funkcij

## Naslednji koraki

- **Fino uravnavanje**: Prilagodite modele svojemu specifičnemu področju ali žargonu za boljšo natančnost (glejte priročnike za fino uravnavanje)
- **Sistemi RAG**: Združite jezikovne modele s pridobivanjem dokumentov za kontekstualno ozaveščene odgovore in iskanje
- **Raziskovanje modelov**: Eksperimentirajte z novimi modeli, kot so Llama 3, Phi-3 ali Qwen, za boljše rezultate
- **Produkcijska uvedba**: Uporabite orodja, kot je vLLM, za skalabilno strežbo jezikovnih modelov v organizacijah

Vaš sistem vam omogoča moč za lokalno poganjanje sofisticiranih jezikovnih modelov. Eksperimentirajte z različnimi modeli, pozivi in parametri, da odkrijete, kaj najbolje deluje za vaše aplikacije.