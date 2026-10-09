<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

vLLM je visokozmogljiv mehanizem za sklepanje (inference engine), zasnovan za velike jezikovne modele (LLM-je). Zagotavlja optimizirano strežbo z neprekinjenim paketnim obdelovanjem (continuous batching) za visoko prepustnost ter z OpenAI združljiv API za nemoteno integracijo aplikacij. Zaradi tega je vLLM odličen za produkcijske postavitve, kjer sta hitrost in učinkovita raba virov ključnega pomena.

Ta vodnik vas nauči, kako strežete LLM-je s pomočjo kontejneriziranega vLLM na integrirani GPE ter kako komunicirati z modeli prek OpenAI Python API-ja.

## Kaj se boste naučili

- Kako nastaviti in zagnati strežnik vLLM s podporo AMD ROCm™
- Kako komunicirati z modeli prek z OpenAI združljivih API-jevih končnih točk
- Kako pošiljati pozive lokalnemu strežniku z `vllm-prompt`

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverite, ali so na voljo posodobitve programske opreme

> **Opomba**: Če VS Code ni nameščen, ga lahko namestite prek AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev zahtevane programske opreme

vLLM se izvaja v vnaprej izdelanem kontejnerju z ROCm in njegovimi vnaprej usklajenimi odvisnostmi. Dodatna namestitev ni potrebna.

Ni koraka namestitve vLLM na gostiteljski strani. Zaženite vLLM z ukazom:

```bash
vllm-launch
```

Zagonski program (launcher) zažene kontejner, cilja na integrirano GPE in izpostavi lokalni z OpenAI združljiv strežnik vLLM. Druga možnost je, da kliknete ikono vLLM v opravilni vrstici.

## Hiter začetek

### 1. Potrdite, da se strežnik vLLM izvaja

`vllm-launch` lahko potrebuje nekaj minut, da vse inicializira. Ko se zažene, je strežnik na voljo na naslovu `http://localhost:8001`. Zagonski terminal naj ostane odprt, saj se strežnik izvaja v ospredju, nato odprite ločen terminal za preostale korake. Spodnji primeri uporabljajo `Qwen/Qwen3-1.7B`; če je vaš zagonski program konfiguriran za drug model, v zahtevah nadomestite z ustrezno identifikacijo modela.

### 2. Pošljite poziv

Uporabite priloženi skript `vllm-prompt`, da pošljete zahtevo lokalnemu z OpenAI združljivemu strežniku vLLM:

```bash
vllm-prompt "Tell me a story"
```

### 3. Pogovarjajte se z modelom z uporabo OpenAI Python API-ja

Ker vLLM izpostavlja z OpenAI združljiv API, lahko za komunikacijo z njim uporabite paket Python `openai`.

Najprej ustvarite virtualno okolje Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->

Namestite paket OpenAI
```bash
pip install openai
```

Ustvarite odjemalca `OpenAI`, ki je usmerjen na lokalni strežnik vLLM namesto na OpenAI-jeve strežnike. Odjemalec zahteva `api_key`, vendar ga vLLM ne preverja, zato deluje poljuben niz:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Nato pošljite zahtevo za dokončanje pogovora (chat completion). To uporablja enak format sporočil kot OpenAI API — seznam sporočil z vlogami, kot sta `"user"` in `"assistant"`. Nastavitev `stream=True` pomeni, da bo odgovor prispel postopoma, namesto naenkrat:

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

Na koncu iterirajte skozi prejete dele podatkov (streamed chunks) in izpišite vsak del besedila ob prejemu:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Priloženi skript [chat_with_model.py](assets/chat_with_model.py) vsebuje celoten primer in ga je mogoče prenesti.


## Izbira in konfiguracija modela

Privzeto `vllm-launch` streže `Qwen/Qwen3-1.7B` kot testni model na vratih `8001`. Model, vrata in parametre strežbe vLLM lahko spremenite brez ponovne gradnje ali urejanja kontejnerja.

### Modeli, ki jih je testiral AMD

Naslednji modeli so vnaprej konfigurirani in jih je potrdil AMD:

| Model | Opombe |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Privzeti model. Lahek in hiter za nalaganje. |
| `openai/gpt-oss-20b` | Večji model za kakovostnejše odgovore. |

### Zagon drugega modela

Podajte identifikacijo modela z `--model` (ali `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Spreminjanje vrat

Podajte vrata, večja od 1024, z `--port` (ali `-p`); privzeta vrednost je `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Če spremenite vrata, usmerite `base_url` odjemalca na ista vrata (na primer `http://localhost:8080/v1`).

### Podajanje dodatnih parametrov vLLM

Vsi dodatni argumenti se posredujejo neposredno vLLM, zato lahko prilagodite obnašanje strežbe, kot sta dolžina konteksta ali podatkovni tip. Obstajata dva načina za njihovo podajanje.

**V vrstici** (inline), za možnostmi zagonskega programa:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Trajno**, v konfiguracijski datoteki na `~/.local/share/vLLM/vllm-launch.conf`. Ta datoteka privzeto ne obstaja — ustvarite jo in dodajte svoje argumente kot polje Bash (Bash array):

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Uporabite `+=` za dodajanje k privzetim argumentom, namesto da jih nadomestite:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Če si želite kadar koli ogledati vse možnosti zagonskega programa, zaženite:

```bash
vllm-launch --help
```

### Kje so shranjeni modeli

`vllm-launch` išče modele na dveh mestih:

| Mesto | Pot |
|----------|------|
| Sistemski modeli | `/var/cache/models` |
| Uporabniški modeli | `~/.local/share/vLLM/models` |

Preneseni model lahko postavite v kateri koli od teh dveh imenikov in ga zaženete tako, da njegovo pot ali identifikacijo podate parametru `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Opomba**: Pričakuje se, da bo zagon lastnega prenesenega modela na ta način deloval, ko bo model postavljen v enega od zgornjih imenikov, vendar AMD tega poteka dela še ni uradno potrdil.

## Odpravljanje težav

### Povezava zavrnjena

Prepričajte se, da se strežnik izvaja:
```bash
curl http://localhost:8001/health
```

## Povzetek

V tem vodniku ste se naučili, kako:

- Zagnati kontejneriziran vLLM s podporo ROCm na integrirani GPE
- Zagnati strežnik vLLM z z OpenAI združljivimi končnimi točkami API-ja na vratih 8001
- Pošiljati pozive z `vllm-prompt`
- Izvajati klice API-ja strežniku vLLM z uporabo tako pretočnih (streaming) kot nepretočnih zahtev
- Odpraviti pogoste težave pri zagonu strežnika, pomnilniku in povezavah odjemalcev

Zdaj imate kontejenerizirano postavitev vLLM za strežbo velikih jezikovnih modelov z optimizirano zmogljivostjo na integrirani GPE.

## Naslednji koraki

- **Preizkusite različne modele** — Uporabite `vllm-launch --model <model>` za eksperimentiranje z različnimi LLM-ji in primerjavo zmogljivosti (glejte [Izbira in konfiguracija modela](#choosing-and-configuring-a-model)).
- **Zgradite aplikacijo** — Uporabite z OpenAI združljiv API za integracijo vLLM v aplikacijo Python, klepetalnega robota ali avtomatizacijski delovni tok.
- **Natančno prilagodite in strezite** — Natančno prilagodite model z uporabo LoRA ali QLoRA, nato pa ga uvedite z vLLM za optimizirano sklepanje.
## Dodatni viri

- **[Uradna dokumentacija vLLM](https://docs.vllm.ai/)** — Izčrpni vodniki in referenčni priročniki za API
- **[Repozitorij vLLM na GitHub](https://github.com/vllm-project/vllm)** — Izvorna koda, težave in razprave skupnosti