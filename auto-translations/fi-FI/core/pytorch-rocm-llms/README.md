<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus


Haluatko ajaa tehokkaita tekoälyn kielimalleja omalla laitteistollasi? Tämä opas näyttää, miten se tehdään.
Tässä oppaassa käytetään PyTorchia, jota AMD ROCm™ -ohjelmisto tehostaa, mallien ajamiseen, jotka voivat tiivistää dokumentteja, vastata kysymyksiin, generoida tekstiä ja paljon muuta – kaikki paikallisesti.

## Mitä opit

- LLM-mallien, kuten gpt-oss-20b ja qwen3.5-4B, ajaminen paikallisesti PyTorchin ja ROCm:n avulla
- Dokumenttien tiivistystyökalun luominen LLM-malleja käyttäen

## Muistiasetusten määrittäminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomio**: Jos VS Code ei ole asennettuna, voit asentaa sen Ryzen AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

### Virtuaaliympäristön luominen

<!-- @os:linux -->
<!-- @device:halo_box -->
Avaa Linuxissa pääte haluamaasi hakemistoon ja seuraa ohjeita luodaksesi venv-ympäristön, johon ROCm+Pytorch on jo asennettu.
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
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta muutos astuu voimaan):

```bash
sudo usermod -aG render,video $LOGNAME
```

Avaa Linuxissa pääte haluamaasi hakemistoon ja seuraa ohjeita luodaksesi venv-ympäristön.
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
Avaa Windowsissa pääte haluamaasi hakemistoon ja seuraa ohjeita luodaksesi venv-ympäristön, johon ROCm+Pytorch on jo asennettu.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Avaa Windowsissa pääte haluamaasi hakemistoon ja seuraa ohjeita luodaksesi venv-ympäristön.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Vihje**: Windows-käyttäjien on ehkä muutettava PowerShellin suoritusperiaatetta (Execution Policy) (esim.
> asettamalla se arvoon RemoteSigned tai Unrestricted) ennen kuin jotkin PowerShell-komennot voidaan suorittaa.

<!-- @os:end -->

### Perusriippuvuuksien asentaminen
<!-- @require:driver,pytorch -->

### Lisäriippuvuuksien asentaminen

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

## Nopea aloitus esimerkkiskripteillä

Tämä ohjekirja sisältää valmiita, käyttövalmiita skriptejä. Napsauta niitä esikatsellaksesi ja ladataksesi ne samaan hakemistoon, johon loit ympäristön.

| Skripti | Kuvaus | Käyttö |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Perus-LLM-tekstin generointi | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Dokumenttien tiivistäjä Harmony-tuella | `python summarizer.py --file document.txt` |

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

Molemmat skriptit tukevat:
- Mallin valintaa `--model`-lipun avulla
- Chat-mallipohjan muotoilua oikeaa mallikehotusta varten, mikä on erityisen hyödyllistä dokumenttien tiivistämisessä

## Ensimmäisen LLM:n lataaminen ja ajaminen

Mukana oleva [run_llm.py](assets/run_llm.py)-skripti näyttää, miten tekstiä generoidaan LLM-malleilla PyTorchin ja AMD ROCm:n avulla.

> **Huomio:** Kun lataat mallin, Hugging Face Transformers tarkistaa ensin paikallisen välimuistinsa (`~/.cache/huggingface/hub` Linuxissa, `C:\Users\<user>\.cache\huggingface\hub` Windowsissa). Jos mallia ei ole välimuistissa, se ladataan automaattisesti osoitteesta huggingface.co. Ensimmäinen ajokerta voi kestää muutaman minuutin mallin koosta ja verkkoyhteyden nopeudesta riippuen.

Alla oleva koodinpätkä näyttää, miten mallia käytetään ja miten kysyttäviä kysymyksiä voi mukauttaa.

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

Kokeile ladattua skriptiä:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Dokumenttien tiivistäjän rakentaminen

Nyt kun olet tuottanut paikallista LLM-tulostetta, voit rakentaa sen päälle käytännöllisen dokumenttien tiivistäjän. Tässä osiossa käytät [summarizer.py](assets/summarizer.py)-skriptiä syöttääksesi .txt-tiedoston ja tuottaaksesi automaattisesti tiiviin yhteenvedon – kaikki paikallisesti GPU:llasi ajettuna.

Skripti on suunniteltu toimimaan sellaisenaan. Avaa skripti editorissa tutkiaksesi koodia, mukauttaaksesi kehotteita ja säätääksesi parametreja, kuten pituutta ja lämpötilaa (temperature).

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Käyttöesimerkkejä

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

## Tutustu generointiparametreihin

| Parametri | Mitä se ohjaa | Tyypilliset arvot |
|-----------|------------------|----------------|
| `max_new_tokens` | LLM:n tulosteen enimmäispituus | Käytä 50–500 tokenia tiivistelmiin. (1 token vastaa noin 0,75 englanninkielistä sanaa) |
| `temperature` | Luovuus. Matalat arvot tekevät tuloksesta täsmällisemmän, korkeat arvot arvaamattomamman | - **0,1–0,3**: Täsmällinen, deterministinen (hyvä tiivistelmiin) <br> **0,5–0,7**: Tasapainoinen (yleiskäyttöön) <br> **0,8–1,0**: Luova, vaihteleva (ideointiin) |
| `top_p` | Nucleus Sampling – matalat arvot rajaavat mallin tuloksia suppeammaksi | **0,1–0,5**: Tiukka, ennustettava <br> **0,9–0,95**: (standardi, luonteva, keskustelunomainen) |


## Käytännön sovelluksia

- **Tutkimusartikkelien analysointi**: Poimi keskeiset tulokset monimutkaisista julkaisuista nopeaa tarkastelua varten
- **Uutisten koostaminen**: Tiivistä uutisartikkelit lyhyiksi päivittäisiksi koosteiksi tai nostoiksi
- **Kokousmuistiinpanot**: Tiivistä litteroinnit toimenpiteiksi ja tiiviiksi yhteenvedoiksi
- **Oikeudellisten dokumenttien tarkastelu**: Poimi olennaiset lausekkeet tai velvoitteet pitkistä oikeudellisista teksteistä nopeasti
- **Koodin dokumentointi**: Luo tiiviitä repositorio-yleiskatsauksia ja funktioiden selityksiä

## Seuraavat vaiheet

- **Hienosäätö (fine-tuning)**: Mukauta malleja omalle alallesi tai erikoissanastollesi paremman tarkkuuden saavuttamiseksi (katso Fine-tuning-ohjekirjat)
- **RAG-järjestelmät**: Yhdistä LLM-mallit dokumenttien hakuun kontekstitietoisia vastauksia ja hakuja varten
- **Mallien tutkiminen**: Kokeile uusia malleja, kuten Llama 3, Phi-3 tai Qwen, parempien tulosten saamiseksi
- **Tuotantokäyttöönotto**: Käytä työkaluja, kuten vLLM, skaalautuvaan LLM-palveluun organisaatioissa

Järjestelmäsi antaa sinulle mahdollisuuden ajaa kehittyneitä kielimalleja paikallisesti. Kokeile erilaisia malleja, kehotteita ja parametreja löytääksesi, mikä toimii parhaiten omissa sovelluksissasi.