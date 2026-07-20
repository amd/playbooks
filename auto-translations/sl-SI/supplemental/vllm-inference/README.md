<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ta priročnik uporablja posebne oznake, ki jih GitHub ne more upodobiti. Za pravilen ogled te vsebine obiščite [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->


## Pregled

vLLM je visoko zmogljiv sklepalni pogon, zasnovan za velike jezikovne modele (LLM). Zagotavlja optimizirano strežbo z neprekinjenim paketnim obdelovanjem za visoko prepustnost in API, združljiv z OpenAI, za nemoteno integracijo aplikacij. Zaradi tega je vLLM odličen za produkcijske uvedbe, kjer sta hitrost in učinkovita raba virov ključnega pomena.

Ta priročnik vas nauči, kako strežti LLM-je z uporabo kontejneriziranega vLLM na vgrajenem GPE in kako komunicirati z modeli prek OpenAI Python API-ja.

## Kaj se boste naučili

- Kako nastaviti in zagnati strežnik vLLM s podporo AMD ROCm™
- Kako komunicirati z modeli prek končnih točk API-ja, združljivega z OpenAI
- Kako pošiljati pozive lokalnemu strežniku z `vllm-prompt`

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

> **Opomba**: Če VS Code ni nameščen, ga lahko namestite z AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev potrebne programske opreme

Ta priročnik uporablja vnaprej pripravljeno kontejnersko sliko, ki vključuje vLLM, podporo ROCm in pomožne skripte, potrebne za zagon strežnika. Ni vam treba ročno namestiti PyTorch, vLLM ali lokalnih skript priročnika.

Na strani gostitelja ni koraka za namestitev vLLM. Zaženite vLLM z:

```bash
vllm-launch
```

Zaganjalnik zažene kontejner, cilja na vgrajeni GPE in izpostavi lokalni strežnik vLLM, združljiv z OpenAI. Alternativno kliknite ikono vLLM v opravilni vrstici.

## Hitri začetek

### 1. Potrdite, da strežnik vLLM deluje

`vllm-launch` lahko traja nekaj minut, da vse inicializira. Ko se zažene, je strežnik na voljo na `http://localhost:8001`. Terminal za zagon naj ostane odprt, ker strežnik teče v ospredju, nato pa odprite ločen terminal za preostale korake. Spodnji primeri uporabljajo `Qwen/Qwen3-1.7B`; če je vaš zaganjalnik konfiguriran za drug model, v zahtevah nadomestite ta ID modela.

### 2. Pošljite poziv

Uporabite priloženi skript `vllm-prompt`, da pošljete zahtevo lokalnemu strežniku vLLM, združljivemu z OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Klepetajte z modelom z uporabo OpenAI Python API

Ker vLLM izpostavlja API, združljiv z OpenAI, lahko za interakcijo z njim uporabite Python paket `openai`.

Najprej ustvarite virtualno okolje Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Namestite paket OpenAI
```bash
pip install openai
```

Ustvarite odjemalca `OpenAI`, usmerjenega na lokalni strežnik vLLM namesto na strežnike OpenAI. Odjemalec zahteva `api_key`, vendar ga vLLM ne preverja, zato deluje poljuben niz:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Nato pošljite zahtevo za dokončanje klepeta. To uporablja enak format sporočil kot API OpenAI — seznam sporočil z vlogami, kot sta `"user"` in `"assistant"`. Nastavitev `stream=True` pomeni, da bo odgovor prispel postopoma namesto naenkrat:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

Na koncu ponovite čez pretočene dele in izpišite vsak del besedila takoj, ko prispe:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Priloženi skript [chat_with_model.py](assets/chat_with_model.py) vsebuje celoten primer in ga je mogoče prenesti.


## Odpravljanje težav

### Povezava zavrnjena

Prepričajte se, da strežnik deluje:
```bash
curl http://localhost:8001/health
```

## Povzetek

V tem priročniku ste se naučili, kako:

- Zagnati kontejnerizirani vLLM s podporo ROCm na vgrajenem GPE
- Zagnati strežnik vLLM s končnimi točkami API-ja, združljivimi z OpenAI, na vratih 8001
- Pošiljati pozive z `vllm-prompt`
- Izvajati klice API-ja na strežnik vLLM z uporabo pretočnih in nepretočnih zahtev
- Odpravljati pogoste težave pri zagonu strežnika, pomnilniku in povezavah odjemalcev

Zdaj imate kontejnerizirano uvedbo vLLM za strežbo velikih jezikovnih modelov z optimizirano zmogljivostjo na vgrajenem GPE.

## Naslednji koraki

- **Preizkusite različne modele** — Zamenjajte model v konfiguraciji `vllm-launch`, da preizkusite različne LLM-je in primerjate zmogljivost.
- **Zgradite aplikacijo** — Uporabite API, združljiv z OpenAI, za integracijo vLLM v aplikacijo Python, klepetalnega robota ali potek avtomatizacije.
- **Fino prilagodite in strežite** — Fino prilagodite model z uporabo LoRA ali QLoRA, nato pa ga uvedite z vLLM za optimizirano sklepanje.

## Dodatni viri

- **[Uradna dokumentacija vLLM](https://docs.vllm.ai/)** — Celovita navodila in referenčni podatki API-ja
- **[Repozitorij vLLM na GitHub](https://github.com/vllm-project/vllm)** — Izvorna koda, težave in razprave skupnosti