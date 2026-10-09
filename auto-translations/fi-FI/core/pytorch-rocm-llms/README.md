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

Haluatko ajaa tehokkaita tekoälykielimalleja omalla laitteistollasi? Tämä opas näyttää, miten se tehdään.
Tässä ohjeessa käytetään AMD ROCm™ -ohjelmiston voimannuttamaa PyTorch-kehystä, jolla ajetaan paikallisesti malleja, jotka osaavat tiivistää asiakirjoja, vastata kysymyksiin, tuottaa tekstiä ja paljon muuta.

## Mitä opit

- Ajamaan LLM-malleja, kuten gpt-oss-20b ja qwen3.5-4B, paikallisesti PyTorchilla ja ROCm:lla
- Luomaan asiakirjojen tiivistystyökalun LLM-mallien avulla

<!-- @device:halo_box,halo,stx,krk -->
## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomautus**: Jos VS Code ei ole asennettuna, voit asentaa sen Ryzen AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

### Virtuaaliympäristön luominen

<!-- @os:linux -->
<!-- @device:halo_box -->
Linuxissa avaa pääte haluamaasi hakemistoon ja seuraa komentoja luodaksesi venv-ympäristön, jossa ROCm+PyTorch on jo valmiiksi asennettuna.
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
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta muutos tulee voimaan):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linuxissa avaa pääte haluamaasi hakemistoon ja seuraa komentoja luodaksesi venv-ympäristön.
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
Windowsissa avaa pääte haluamaasi hakemistoon ja seuraa komentoja luodaksesi venv-ympäristön, jossa ROCm+PyTorch on jo valmiiksi asennettuna.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windowsissa avaa pääte haluamaasi hakemistoon ja seuraa komentoja luodaksesi venv-ympäristön.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Vinkki**: Windows-käyttäjien voi olla tarpeen muokata PowerShell-suoritusperiaatetta (esim.
> asettaa se arvoon RemoteSigned tai Unrestricted) ennen joidenkin PowerShell-komentojen ajamista.

<!-- @os:end -->

### Perusriippuvuuksien asentaminen
<!-- @require:driver,pytorch -->

### Lisäriippuvuuksien asentaminen

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

> **Huomautus:** Jos malli ei lataudu tai muisti loppuu kesken, kokeile asentaa `kernels`-paketti, jotta malli voidaan ladata optimoidulla kvantisoinnilla.
>
> ```bash
> # Käytä tätä versiota, joka on yhteensopiva Transformers-version kanssa
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

## Pikakäynnistys esimerkkiskripteillä

Tähän ohjeeseen sisältyy valmiiksi käyttövalmiita skriptejä. Napsauta niitä esikatsellaksesi ja ladataksesi ne samaan hakemistoon, jossa luomasi ympäristö sijaitsee.

| Skripti | Kuvaus | Käyttö |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Peruskäyttöinen LLM-tekstintuotanto | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Asiakirjojen tiivistäjä, jossa on Harmony-tuki | `python summarizer.py --file document.txt` |

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
- Mallin valintaa `--model`-lipulla
- Chat-mallipohjan muotoilua oikeaoppista mallin ohjeistusta varten, mikä on erityisen hyödyllistä asiakirjojen tiivistämisessä

## Ensimmäisen LLM:n lataaminen ja ajaminen

Mukana oleva [run_llm.py](assets/run_llm.py)-skripti näyttää, miten tekstiä tuotetaan LLM-malleilla PyTorchia ja AMD ROCm:ia käyttäen.

> **Huomautus:** Kun lataat mallin, Hugging Face Transformers tarkistaa ensin paikallisen välimuistinsa (`~/.cache/huggingface/hub` Linuxissa, `C:\Users\<user>\.cache\huggingface\hub` Windowsissa). Jos malli ei ole välimuistissa, se ladataan automaattisesti osoitteesta huggingface.co. Ensimmäinen ajokerta voi kestää muutaman minuutin mallin koosta ja verkkoyhteyden nopeudesta riippuen.

Alla oleva koodinpätkä näyttää, miten mallia käytetään ja miten esitettäviä kysymyksiä voi muokata.

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

Kokeile ladattua skriptiä:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Asiakirjojen tiivistäjän rakentaminen

Nyt kun olet tuottanut paikallisen LLM:n tulosteen, voit rakentaa sen päälle käytännöllisen asiakirjojen tiivistäjän. Tässä osiossa käytät [summarizer.py](assets/summarizer.py)-skriptiä syöttämään .txt-tiedoston ja tuottamaan automaattisesti tiiviin yhteenvedon – kaikki paikallisesti GPU:llasi ajettuna.

Skripti on suunniteltu toimimaan heti käyttöönotettuna. Avaa skripti editorissa tutkiaksesi koodia, mukauttaaksesi kehotteita ja säätääksesi parametreja, kuten pituutta ja lämpötilaa (temperature).

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

| Parametri | Mitä se säätelee | Tyypilliset arvot |
|-----------|------------------|----------------|
| `max_new_tokens` | LLM:n tulosteen enimmäispituus | Käytä 50–500 tokenia tiivistelmissä. (1 tokeni on noin 0,75 englanninkielistä sanaa) |
| `temperature` | Luovuus. Matalat arvot tekevät tuloksesta fokusoituneen, korkeat arvot tuovat enemmän arvaamattomuutta | - **0.1–0.3**: Fokusoitu, deterministinen (hyvä tiivistelmiin) <br> **0.5–0.7**: Tasapainoinen (yleiskäyttöön) <br> **0.8–1.0**: Luova, vaihteleva (ideointiin) |
| `top_p` | Nucleus Sampling – Matalat arvot rajaavat mallin suppeampiin tulosteisiin | **0.1-0.5**: Tiukka, ennustettava <br> **0.9-0.95**: (vakio, luonnollinen, keskustelunomainen) |


## Käytännön sovellukset

- **Tutkimusartikkelien analyysi**: Poimi keskeiset havainnot monimutkaisista julkaisuista nopeaa tarkastelua varten
- **Uutisten koostaminen**: Tiivistä uutisartikkelit lyhyiksi päivittäisiksi koosteiksi tai kohokohdiksi
- **Kokousmuistiinpanot**: Tiivistä litteroinnit toimenpidekohteiksi ja ytimekkäiksi yhteenvedoiksi
- **Oikeudellisten asiakirjojen tarkastus**: Poimi olennaiset lausekkeet tai velvoitteet pitkistä oikeudellisista teksteistä nopeasti
- **Koodin dokumentointi**: Luo tiiviitä repositorioyleiskatsauksia ja funktioiden selityksiä
## Seuraavat vaiheet

- **Hienosäätö**: Mukauta malleja omalle alallesi tai erikoissanastollesi parempaa tarkkuutta varten (katso Fine-tuning Playbooks)
- **RAG-järjestelmät**: Yhdistä kielimalleja dokumenttien hakuun kontekstitietoisia vastauksia ja hakuja varten
- **Mallien tutkiminen**: Kokeile uusia malleja, kuten Llama 3, Phi-3 tai Qwen, parempien tulosten saavuttamiseksi
- **Tuotantokäyttöönotto**: Käytä työkaluja, kuten vLLM, skaalautuvaan kielimallien tarjoamiseen organisaatioissa

Järjestelmäsi antaa sinulle mahdollisuuden ajaa kehittyneitä kielimalleja paikallisesti. Kokeile erilaisia malleja, kehotteita ja parametreja löytääksesi sovelluksiisi parhaiten sopivat ratkaisut.