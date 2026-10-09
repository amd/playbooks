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


Želite poganjati zmogljive jezikovne modele AI na lastni strojni opremi? Ta vodnik vam pokaže, kako.
V tem vodniku je uporabljen PyTorch, ki ga poganja programska oprema AMD ROCm™, za zagon modelov, ki lahko povzemajo dokumente, odgovarjajo na vprašanja, ustvarjajo besedilo in še več, vse to lokalno.

## Kaj se boste naučili

- Lokalno poganjanje velikih jezikovnih modelov, kot sta gpt-oss-20b in qwen3.5-4B, z uporabo PyTorch in ROCm
- Izdelava orodja za povzemanje dokumentov z uporabo velikih jezikovnih modelov

<!-- @device:halo_box,halo,stx,krk -->
## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Preverite posodobitve programske opreme
> **Opomba**: Če VS Code ni nameščen, ga lahko namestite z Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev zahtev za programsko opremo

### Ustvarjanje navideznega okolja

<!-- @os:linux -->
<!-- @device:halo_box -->
V sistemu Linux odprite terminal v imeniku po izbiri in sledite ukazom za ustvarjanje venv z že nameščenima ROCm+Pytorch.
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
**Uporabniku dodelite dostop do naprav GPU** (za uveljavitev se odjavite in ponovno prijavite):

```bash
sudo usermod -aG render,video $LOGNAME
```

V sistemu Linux odprite terminal v imeniku po izbiri in sledite ukazom za ustvarjanje venv.
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
V sistemu Windows odprite terminal v imeniku po izbiri in sledite ukazom za ustvarjanje venv z že nameščenima ROCm+Pytorch.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
V sistemu Windows odprite terminal v imeniku po izbiri in sledite ukazom za ustvarjanje venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Nasvet**: Uporabniki sistema Windows bodo morda morali spremeniti svojo izvedbeno politiko PowerShell (Execution Policy) (npr.
> nastaviti jo na RemoteSigned ali Unrestricted), preden zaženejo nekatere ukaze Powershell.

<!-- @os:end -->

### Namestitev osnovnih odvisnosti
<!-- @require:driver,pytorch -->

### Namestitev dodatnih odvisnosti

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

> **Opomba:** Če se model ne naloži ali zmanjka pomnilnika, poskusite namestiti paket `kernels`, da naložite model z optimizirano kvantizacijo.
>
> ```bash
> # Uporabite to različico, ki je združljiva z različico Transformers
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

## Hiter začetek z vzorčnimi skriptami

Ta vodnik vključuje pripravljene skripte za takojšnjo uporabo. Kliknite nanje za predogled in prenos v isti imenik kot okolje, ki ste ga ustvarili.

| Skripta | Opis | Uporaba |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Osnovno ustvarjanje besedila z velikimi jezikovnimi modeli | `python run_llm.py` |
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
- Izbiro modela z zastavico `--model`
- Oblikovanje predlog klepeta za pravilno pozivanje modela, kar je še posebej uporabno za povzemanje dokumentov

## Nalaganje in zagon prvega velikega jezikovnega modela

Priložena skripta [run_llm.py](assets/run_llm.py) prikazuje, kako ustvariti besedilo z velikimi jezikovnimi modeli z uporabo PyTorch in AMD ROCm.

> **Opomba:** Ko naložite model, Hugging Face Transformers najprej preveri svoj lokalni predpomnilnik (`~/.cache/huggingface/hub` v sistemu Linux, `C:\Users\<user>\.cache\huggingface\hub` v sistemu Windows). Če model ni predpomnjen, se samodejno prenese s huggingface.co. Prvi zagon lahko traja nekaj minut, odvisno od velikosti modela in hitrosti omrežja.

Spodnji odlomek prikazuje, kako uporabiti model in prilagoditi zastavljena vprašanja.

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

Preizkusite preneseno skripto:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Izdelava povzemalnika dokumentov

Zdaj, ko ste ustvarili lokalni izhod velikega jezikovnega modela, lahko na tem nadgradite tako, da izdelate praktičen povzemalnik dokumentov. V tem razdelku boste uporabili skripto [summarizer.py](assets/summarizer.py), da vnesete datoteko .txt in samodejno ustvarite jedrnat povzetek, vse to lokalno na vašem GPE.

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

## Spoznajte parametre ustvarjanja

| Parameter | Kaj nadzoruje | Tipične vrednosti |
|-----------|------------------|----------------|
| `max_new_tokens` | Največja dolžina izhoda velikega jezikovnega modela | Za povzetke uporabite 50–500 žetonov. (1 žeton je približno 0,75 angleške besede) |
| `temperature` | Ustvarjalnost. Nizke vrednosti jo naredijo osredotočeno, visoke pa prinesejo več nepredvidljivosti | - **0,1–0,3**: osredotočeno, determinirano (dobro za povzetke) <br> **0,5–0,7**: uravnoteženo (splošna uporaba) <br> **0,8–1,0**: ustvarjalno, raznoliko (viharjenje možganov) |
| `top_p` | Vzorčenje jedra (Nucleus Sampling) - nizke vrednosti omejijo model na ožje izhode | **0,1-0,5**: strogo, predvidljivo <br> **0,9-0,95**: (standardno, naravno, pogovorno) |


## Realne aplikacije

- **Analiza raziskovalnih člankov**: izluščite ključne ugotovitve iz zapletenih publikacij za hiter pregled
- **Združevanje novic**: povzemite novičarske članke v kratke dnevne povzetke ali poudarke
- **Zapiski s sestankov**: strnite prepise v konkretne naloge in jedrnate povzetke
- **Pregled pravnih dokumentov**: hitro izluščite ustrezne klavzule ali obveznosti iz dolgih pravnih besedil
- **Dokumentacija kode**: ustvarite jedrnate preglede repozitorijev in razlage funkcij
## Naslednji koraki

- **Fino prilagajanje**: Prilagodite modele svojemu specifičnemu področju ali terminologiji za boljšo natančnost (glejte Fine-tuning Playbooks)
- **Sistemi RAG**: Združite jezikovne modele (LLM) s pridobivanjem dokumentov za kontekstualno ozaveščene odgovore in iskanje
- **Raziskovanje modelov**: Eksperimentirajte z novimi modeli, kot so Llama 3, Phi-3 ali Qwen, za boljše rezultate
- **Produkcijska uvedba**: Uporabite orodja, kot je vLLM, za skalabilno strežbo jezikovnih modelov (LLM) v organizacijah

Vaš sistem vam omogoča zagon zahtevnih jezikovnih modelov lokalno. Eksperimentirajte z različnimi modeli, pozivi in parametri, da odkrijete, kaj najbolje deluje za vaše aplikacije.