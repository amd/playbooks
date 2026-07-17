<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus


Haluatko ajaa tehokkaita tekoälykielimalleja omalla laitteistollasi? Tämä opas näyttää, miten se tehdään.
Tässä opetusohjelmassa käytetään AMD ROCm™ -ohjelmiston käyttämää PyTorch-kirjastoa mallien ajamiseen. Mallit voivat tiivistää asiakirjoja, vastata kysymyksiin, tuottaa tekstiä ja paljon muuta – kaikki paikallisesti.

## Mitä opit

- Aja LLM-malleja, kuten gpt-oss-20b ja qwen3.5-4B, paikallisesti PyTorchin ja ROCm:n avulla
- Luo asiakirjojen tiivistämistyökalu LLM-mallien avulla

## Muistikonfiguraation asettaminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomio**: Jos VS Code ei ole asennettuna, voit asentaa sen Ryzen AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmistoedellytysten asentaminen

### Luo virtuaaliympäristö

<!-- @os:linux -->
<!-- @device:halo_box -->
Avaa Linuxissa pääte haluamassasi hakemistossa ja seuraa komentoja luodaksesi venv-ympäristön, johon ROCm+Pytorch on jo asennettu.
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
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta muutos tulee voimaan):

```bash
sudo usermod -aG render,video $LOGNAME
```

Avaa Linuxissa pääte haluamassasi hakemistossa ja seuraa komentoja luodaksesi venv-ympäristön.
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
Avaa Windowsissa pääte haluamassasi hakemistossa ja seuraa komentoja luodaksesi venv-ympäristön, johon ROCm+Pytorch on jo asennettu.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Avaa Windowsissa pääte haluamassasi hakemistossa ja seuraa komentoja luodaksesi venv-ympäristön.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Vinkki**: Windows-käyttäjien saattaa olla tarpeen muuttaa PowerShell-suorituskäytäntöään (esim.
> asettaa se RemoteSigned- tai Unrestricted-tilaan) ennen joidenkin PowerShell-komentojen suorittamista.

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

## Pikaopas esimerkkiskripteillä

Tämä playbook sisältää valmiita skriptejä. Napsauta niitä esikatsellaksesi ja ladataksesi ne samaan hakemistoon kuin luomasi ympäristö.

| Skripti | Kuvaus | Käyttö |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | LLM-tekstin perusgenerointi | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Asiakirjojen tiivistäjä Harmony-tuella | `python summarizer.py --file document.txt` |

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
- Chat-mallipohjien muotoilua oikeaa mallin kehottamista varten, erityisen hyödyllistä asiakirjojen tiivistämisessä

## Ensimmäisen LLM-mallin lataaminen ja ajaminen

Mukana oleva [run_llm.py](assets/run_llm.py)-skripti näyttää, miten tekstiä generoidaan LLM-malleilla PyTorchin ja AMD ROCm:n avulla.

> **Huomio:** Kun lataat mallin, Hugging Face Transformers tarkistaa ensin paikallisen välimuistinsa (`~/.cache/huggingface/hub` Linuxissa, `C:\Users\<user>\.cache\huggingface\hub` Windowsissa). Jos mallia ei ole välimuistissa, se ladataan automaattisesti huggingface.co-palvelusta. Ensimmäinen käynnistys voi kestää muutaman minuutin mallin koon ja verkon nopeuden mukaan.

Alla oleva koodinpätkä näyttää, miten mallia käytetään ja miten esitettyjä kysymyksiä mukautetaan.

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


## Asiakirjojen tiivistäjän rakentaminen

Nyt kun olet generoinut paikallista LLM-tulostetta, voit rakentaa sen päälle käytännöllisen asiakirjojen tiivistäjän. Tässä osiossa käytät [summarizer.py](assets/summarizer.py)-skriptiä syöttääksesi .txt-tiedoston ja generoidaksesi siitä automaattisesti tiiviin yhteenvedon – kaikki paikallisesti GPU:llasi.

Skripti on suunniteltu toimimaan heti käyttövalmiina. Avaa skripti editorissa tutustuaksesi koodiin, mukauttaaksesi kehotteita ja säätääksesi parametreja, kuten pituutta ja lämpötilaa.

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
| `max_new_tokens` | LLM:n tulosteen enimmäispituus | Käytä 50–500 tokenia tiivistelmiä varten. (1 token on noin 0,75 englanninkielistä sanaa) |
| `temperature` | Luovuus. Matalat arvot tekevät tuloksesta tarkemman, korkeat arvot lisäävät arvaamattomuutta | - **0.1–0.3**: Tarkka, deterministinen (hyvä tiivistelmiä varten) <br> **0.5–0.7**: Tasapainoinen (yleiskäyttö) <br> **0.8–1.0**: Luova, vaihteleva (ideointi) |
| `top_p` | Nucleus Sampling – matalat arvot rajoittavat mallin tulosteen kapeammaksi | **0.1-0.5**: Tiukka, ennustettava <br> **0.9-0.95**: (standardi, luonnollinen, keskustelumainen) |


## Käytännön sovelluksia

- **Tutkimusjulkaisujen analyysi**: Poimi keskeisiä löydöksiä monimutkaisista julkaisuista nopeaa tarkastelua varten
- **Uutisten koostaminen**: Tiivistä uutisartikkelit lyhyiksi päivittäisiksi koosteiksi tai nostoksiksi
- **Kokousmuistiinpanot**: Tiivistä transkriptit toimenpiteiksi ja lyhyiksi yhteenvedoiksi
- **Juridisten asiakirjojen tarkastelu**: Poimi nopeasti olennaiset lausekkeet tai velvoitteet pitkistä juridisista teksteistä
- **Koodin dokumentointi**: Luo tiiviit repositorion yleiskatsaukset ja funktioiden selitykset

## Seuraavat askeleet

- **Hienosäätö**: Mukauta malleja omaan alaasi tai ammattisanastoosi paremman tarkkuuden saavuttamiseksi (katso hienosäätöä käsittelevät playbook-oppaat)
- **RAG-järjestelmät**: Yhdistä LLM-mallit asiakirjojen hakuun kontekstikohtaisia vastauksia ja hakua varten
- **Mallien tutkiminen**: Kokeile uusia malleja, kuten Llama 3, Phi-3 tai Qwen, parempien tulosten saavuttamiseksi
- **Tuotantokäyttöönotto**: Käytä työkaluja, kuten vLLM, skaalautuvaan LLM-palveluun organisaatioissa

Järjestelmäsi antaa sinulle mahdollisuuden ajaa kehittyneitä kielimalleja paikallisesti. Kokeile eri malleja, kehotteita ja parametreja löytääksesi, mikä toimii parhaiten omiin sovelluksiisi.